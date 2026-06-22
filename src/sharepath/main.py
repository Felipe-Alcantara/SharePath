"""Ponto de entrada do SharePath.

Pega o IP do Radmin VPN, copia para a área de transferência e sobe o servidor
de arquivos para o outro PC baixar.

Por padrão compartilha a pasta atual; use ``--dir`` (ou ``SHAREPATH_DIR``) para
escolher outra pasta. A porta é resolvida automaticamente: usa a padrão (8000),
ou ``--port`` / ``SHAREPATH_PORT``, e troca sozinha por uma porta livre se a
escolhida estiver ocupada.
"""

import argparse

import pyperclip
from colorama import Fore, Back

try:
    # Execução como pacote: python -m sharepath
    from .utils import (
        clear, custom_print, get_ip, open_server, resolve_directory, resolve_port,
    )
except ImportError:
    # Execução direta do arquivo: python src/sharepath/main.py
    from utils import (
        clear, custom_print, get_ip, open_server, resolve_directory, resolve_port,
    )


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="sharepath", description=__doc__)
    parser.add_argument(
        "--port", type=int, default=None,
        help="Porta do servidor (padrão 8000; troca sozinha se ocupada).",
    )
    parser.add_argument(
        "--dir", "--folder", dest="directory", default=None, metavar="PASTA",
        help="Pasta a compartilhar (padrão: a pasta atual).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    port = resolve_port(args.port)
    directory = resolve_directory(args.directory)

    ip = get_ip()
    endereco = f"{ip}:{port}"
    pyperclip.copy(endereco)

    clear()
    custom_print(
        "IP COPIADO PARA A ÁREA DE TRANSFERÊNCIA (Ctrl + V)",
        Fore.BLACK,
        Back.BLUE,
    )
    print(f"Compartilhe: http://{endereco}")
    print(f"Pasta compartilhada: {directory}")
    print('Aperte "Ctrl + C" para ENCERRAR a conexão')

    try:
        open_server(port, directory)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
