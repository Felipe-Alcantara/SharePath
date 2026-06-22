"""Funções de apoio do SharePath.

Responsabilidades isoladas aqui:
- abrir o Radmin VPN;
- ler / perguntar / salvar o IP do Radmin (cache local em ``YourIp.txt``);
- subir o servidor de arquivos HTTP;
- utilitários de impressão colorida no terminal.

Nenhuma regra de negócio do ponto de entrada (``Script.py``) vive aqui.
"""

import os
import re
import sys
import socket
import subprocess
from pathlib import Path

from colorama import Fore, Back

try:
    # Execução como pacote: python -m sharepath
    from . import radmin
except ImportError:
    # Execução direta do arquivo: python src/sharepath/main.py
    import radmin

# Porta padrão do servidor de arquivos.
PORT = 8000

# Variável de ambiente para fixar a porta sem passar argumento.
PORT_ENV_VAR = "SHAREPATH_PORT"

# Cache local do IP fica na pasta de execução (a pasta compartilhada), não num
# caminho fixo do disco. Assim o projeto roda de qualquer pasta/máquina e o
# cache acompanha quem está rodando o servidor.
IP_CACHE_FILE = Path.cwd() / "YourIp.txt"

# IPv4 simples (ex.: 26.123.45.67). O Radmin usa a faixa 26.x.x.x.
_IPV4_RE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")


def clear():
    """Limpa a tela do terminal (Windows: ``cls``; demais: ``clear``)."""
    os.system("cls" if os.name == "nt" else "clear")


def custom_print(txt, fore=Fore.RESET, back=Back.RESET):
    """Imprime ``txt`` com cores e reseta o estilo ao final."""
    print(fore + back + txt + Back.RESET + Fore.RESET)


def is_valid_ip(ip):
    """Valida um IPv4 (cada octeto entre 0 e 255)."""
    match = _IPV4_RE.match(ip.strip())
    if not match:
        return False
    return all(0 <= int(octeto) <= 255 for octeto in match.groups())


def is_port_free(port, host="0.0.0.0"):
    """True se ``port`` está livre para escutar em ``host``.

    Não usa ``SO_REUSEADDR`` de propósito: no Windows ele permitiria fazer
    bind numa porta já em uso, dando falso positivo. Sem ele, o bind falha
    quando a porta está realmente ocupada.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(preferred=PORT, attempts=50):
    """Acha uma porta livre, começando pela ``preferred``.

    Tenta a preferida primeiro; se estiver ocupada, sobe a partir dela. Em
    último caso, pede uma porta efêmera ao SO. Assim o SharePath sai sozinho
    de uma porta disputada, sem o usuário configurar nada.
    """
    if is_port_free(preferred):
        return preferred
    for port in range(preferred + 1, preferred + 1 + attempts):
        if is_port_free(port):
            return port
    # Fallback: deixa o SO escolher qualquer porta livre.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("0.0.0.0", 0))
        return sock.getsockname()[1]


def resolve_port(cli_port=None):
    """Resolve a porta a usar e garante que esteja livre.

    Prioridade: argumento explícito > variável ``SHAREPATH_PORT`` > padrão
    ``PORT``. Em seguida, se a porta escolhida estiver ocupada, troca
    automaticamente por uma livre.
    """
    chosen = PORT
    env_port = os.environ.get(PORT_ENV_VAR)
    if cli_port is not None:
        chosen = cli_port
    elif env_port:
        try:
            chosen = int(env_port)
        except ValueError:
            custom_print(
                f"{PORT_ENV_VAR}={env_port!r} não é um número; usando {PORT}.",
                Fore.BLACK,
                Back.YELLOW,
            )

    free = find_free_port(chosen)
    if free != chosen:
        custom_print(
            f"Porta {chosen} ocupada — usando a porta livre {free}.",
            Fore.BLACK,
            Back.YELLOW,
        )
    return free


def open_server(port=PORT):
    """Sobe ``python -m http.server`` na pasta atual, na ``port`` indicada.

    Usa ``sys.executable`` para garantir o mesmo Python que está rodando este
    script, em vez de confiar num ``python`` qualquer do PATH.
    """
    subprocess.run([sys.executable, "-m", "http.server", str(port)])


def open_radmin():
    """Abre o Radmin VPN; avisa de forma clara se não conseguir."""
    if radmin.open_radmin():
        return
    custom_print(
        "Não foi possível abrir o Radmin automaticamente. Abra-o manualmente.",
        Fore.BLACK,
        Back.RED,
    )
    print()


def ask_ip():
    """Abre o Radmin e pergunta o IP ao usuário, validando a entrada."""
    open_radmin()
    while True:
        ip = input("Coloque seu IP (Radmin): ").strip()
        # Aceita "IP" ou "IP:porta" — descarta a porta, se vier.
        if ":" in ip:
            ip = ip.split(":")[0]
        if is_valid_ip(ip):
            return ip
        custom_print("IP inválido. Use o formato 26.x.x.x", Fore.BLACK, Back.RED)


def get_ip():
    """Retorna o IP do Radmin (sem porta), usando o cache local quando válido.

    Se o cache não existir ou estiver inválido, pergunta ao usuário e o
    persiste. O valor salvo é sempre um IP validado. A porta é resolvida à
    parte (ver :func:`resolve_port`), pois pode mudar a cada execução.
    """
    ip = ""
    try:
        ip = IP_CACHE_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        pass

    if not is_valid_ip(ip):
        ip = ask_ip()
        IP_CACHE_FILE.write_text(ip, encoding="utf-8")

    return ip
