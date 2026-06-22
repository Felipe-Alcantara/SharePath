"""start_app.py — lançador único e autossustentável do SharePath.

Com um único comando, este script:
  1. instala as dependências (``pip install -r requirements.txt``);
  2. verifica o Radmin VPN — se faltar, oferece baixar/instalar (Windows) ou
     mostra um tutorial por SO;
  3. imprime um passo a passo de uso no terminal (qualquer SO);
  4. inicia o SharePath (pega o IP do Radmin e sobe o servidor de arquivos);
  5. abre o servidor no navegador local para você conferir que está no ar.

Uso:
    python start_app.py                # tudo: deps + radmin + tutorial + inicia + navegador
    python start_app.py --port 8123    # fixa a porta (padrão 8000; troca sozinha se ocupada)
    python start_app.py --no-install   # pula a instalação de dependências
    python start_app.py --no-browser   # inicia sem abrir o navegador (servidor/automação)
    python start_app.py --no-radmin    # pula a verificação do Radmin VPN
    python start_app.py restart        # encerra processo na porta e reinicia limpo

A porta é resolvida automaticamente: se a escolhida estiver ocupada, o SharePath
troca sozinho por uma porta livre — sem conflito com outros apps.

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
SRC = ROOT / "src"
REQUIREMENTS = ROOT / "requirements.txt"
HOST = "127.0.0.1"          # endereço local só para conferência do host
DEFAULT_PORT = 8000         # deve casar com PORT em src/sharepath/utils.py
# -----------------------------------------------------------------------------

# Torna o pacote sharepath importável a partir de src/.
sys.path.insert(0, str(SRC))
from sharepath import radmin       # noqa: E402  (precisa do sys.path acima)
from sharepath.utils import resolve_port  # noqa: E402


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


def check_radmin():
    """Verifica o Radmin VPN; oferece instalar (Windows) ou orienta o usuário."""
    _print(">", "Verificando o Radmin VPN...")
    if radmin.is_installed():
        _print("OK", "Radmin VPN encontrado.")
        return
    # ensure_radmin imprime suas próprias mensagens (download/instalação/tutorial).
    if radmin.ensure_radmin():
        _print("OK", "Radmin VPN pronto.")
    else:
        _print("!", "Siga o tutorial acima para instalar o Radmin antes de compartilhar.")


def print_tutorial(port):
    """Imprime um passo a passo de uso no terminal, adaptado ao SO atual."""
    os_name = radmin.current_os()
    linha = "=" * 64
    print(f"\n{linha}")
    print("  COMO USAR O SHAREPATH (passo a passo)")
    print(linha)
    print(
        "  1. Garanta que o Radmin VPN está aberto e conectado à mesma rede\n"
        "     nos 2 PCs (faixa de IP 26.x.x.x).\n"
        "  2. Coloque nesta pasta os arquivos que você quer compartilhar.\n"
        "  3. Quando pedido, informe seu IP do Radmin (ele será copiado para\n"
        "     a área de transferência automaticamente).\n"
        "  4. Mande o endereço http://SEU_IP:%d para o seu amigo. No navegador\n"
        "     dele, a pasta aparece para baixar os arquivos.\n"
        "  5. Pressione Ctrl + C aqui para encerrar o servidor." % port
    )
    if os_name in ("linux", "macos"):
        print(
            "\n  Observação (%s): o Radmin VPN roda via Wine. Se ainda não tem,\n"
            "  veja o tutorial de instalação exibido acima." % os_name
        )
    print(f"{linha}\n")


def open_browser_when_ready(port):
    """Abre o navegador assim que o servidor responder (em background)."""
    url = f"http://{HOST}:{port}"
    for _ in range(60):  # até ~30s
        if port_in_use(HOST, port):
            webbrowser.open(url)
            return
        time.sleep(0.5)


def start_app(open_browser, port):
    """Inicia o SharePath na ``port`` e bloqueia até o usuário encerrar."""
    if not (SRC / "sharepath" / "main.py").exists():
        _print("X", f"Pacote sharepath não encontrado em {SRC}")
        sys.exit(1)

    if open_browser:
        threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True).start()

    _print(">", f"Iniciando o SharePath na porta {port}...")
    # Roda o pacote (python -m sharepath) com src/ no PYTHONPATH. cwd fica na
    # pasta atual de quem chamou, para o servidor expor os arquivos certos.
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        subprocess.run([sys.executable, "-m", "sharepath", "--port", str(port)], env=env)
    except KeyboardInterrupt:
        _print("OK", "Encerrado.")


def _extract_port(args):
    """Lê ``--port N`` (ou ``--port=N``) de ``args``, se houver."""
    for i, a in enumerate(args):
        if a == "--port" and i + 1 < len(args):
            try:
                return int(args[i + 1])
            except ValueError:
                return None
        if a.startswith("--port="):
            try:
                return int(a.split("=", 1)[1])
            except ValueError:
                return None
    return None


def main():
    args = sys.argv[1:]
    do_install = "--no-install" not in args
    open_browser = "--no-browser" not in args
    check_vpn = "--no-radmin" not in args
    restart = "restart" in args
    cli_port = _extract_port(args)

    if restart:
        # Libera a porta-base (e a fixada, se houver) antes de reiniciar.
        kill_port(cli_port if cli_port is not None else DEFAULT_PORT)

    # Resolve a porta automaticamente: troca sozinha se a escolhida estiver ocupada.
    port = resolve_port(cli_port)

    if do_install:
        install_dependencies()

    if check_vpn:
        check_radmin()

    print_tutorial(port)
    start_app(open_browser, port)


if __name__ == "__main__":
    main()
