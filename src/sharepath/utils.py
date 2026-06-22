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


def open_server(port=PORT):
    """Sobe ``python -m http.server`` na pasta atual.

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
    """Retorna ``IP:PORTA`` do Radmin, usando o cache local quando válido.

    Se o cache não existir ou estiver inválido, pergunta ao usuário e o
    persiste. O valor salvo é sempre um IP validado.
    """
    ip = ""
    try:
        ip = IP_CACHE_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        pass

    if not is_valid_ip(ip):
        ip = ask_ip()
        IP_CACHE_FILE.write_text(ip, encoding="utf-8")

    return f"{ip}:{PORT}"
