"""start_app.py — lançador único do SharePath.

Com um único comando, este script:
  1. instala as dependências (``pip install -r requirements.txt``);
  2. inicia o SharePath (que pega o IP do Radmin e sobe o servidor de arquivos);
  3. abre o servidor no navegador local para você conferir que está no ar.

Uso:
    python start_app.py                # instala (se preciso) + inicia + abre o navegador
    python start_app.py --no-install   # pula a instalação de dependências
    python start_app.py --no-browser   # inicia sem abrir o navegador (servidor/automação)
    python start_app.py restart        # encerra processo na porta e reinicia limpo

Usa apenas a biblioteca padrão. Cross-platform (Windows, Linux, macOS).
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
from pathlib import Path

# --- CONFIG ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
ENTRY_POINT = ROOT / "Script.py"
HOST = "127.0.0.1"          # endereço local só para conferência do host
PORT = 8000                 # deve casar com PORT em Utils.py
URL = f"http://{HOST}:{PORT}"
# -----------------------------------------------------------------------------


def _print(prefix, msg):
    print(f"[start_app] {prefix} {msg}")


def install_dependencies():
    """Instala as dependências do ``requirements.txt`` com o Python atual."""
    if not REQUIREMENTS.exists():
        _print("!", f"requirements.txt não encontrado em {REQUIREMENTS}; pulando.")
        return
    _print(">", "Instalando dependências...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)]
    )
    if result.returncode != 0:
        _print("X", "Falha ao instalar dependências. Verifique sua conexão e o pip.")
        sys.exit(1)
    _print("OK", "Dependências prontas.")


def port_in_use(host, port):
    """Retorna True se algo já está escutando em ``host:port``."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def kill_port(port):
    """Encerra o processo que ocupa ``port`` (best-effort, cross-platform)."""
    _print(">", f"Liberando a porta {port}...")
    try:
        if os.name == "nt":
            out = subprocess.check_output(
                ["netstat", "-ano", "-p", "tcp"], text=True, errors="ignore"
            )
            pids = {
                line.split()[-1]
                for line in out.splitlines()
                if f":{port}" in line and "LISTENING" in line
            }
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            out = subprocess.run(
                ["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True
            ).stdout
            for pid in out.split():
                subprocess.run(["kill", "-9", pid],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.SubprocessError, FileNotFoundError):
        _print("!", "Não foi possível liberar a porta automaticamente.")


def open_browser_when_ready():
    """Abre o navegador assim que o servidor responder (em background)."""
    for _ in range(60):  # até ~30s
        if port_in_use(HOST, PORT):
            webbrowser.open(URL)
            return
        time.sleep(0.5)


def start_app(open_browser):
    """Inicia o SharePath e bloqueia até o usuário encerrar com Ctrl + C."""
    if not ENTRY_POINT.exists():
        _print("X", f"Ponto de entrada não encontrado: {ENTRY_POINT}")
        sys.exit(1)

    if open_browser:
        threading.Thread(target=open_browser_when_ready, daemon=True).start()

    _print(">", "Iniciando o SharePath...")
    try:
        subprocess.run([sys.executable, str(ENTRY_POINT)], cwd=str(ROOT))
    except KeyboardInterrupt:
        _print("OK", "Encerrado.")


def main():
    args = sys.argv[1:]
    do_install = "--no-install" not in args
    open_browser = "--no-browser" not in args
    restart = "restart" in args

    if restart:
        kill_port(PORT)
    elif port_in_use(HOST, PORT):
        _print("!", f"A porta {PORT} já está em uso. Use 'python start_app.py restart'.")
        sys.exit(1)

    if do_install:
        install_dependencies()

    start_app(open_browser)


if __name__ == "__main__":
    main()
