"""Ponto de entrada do SharePath.

Pega o IP do Radmin VPN, copia para a área de transferência e sobe o servidor
de arquivos na pasta atual para o outro PC baixar.
"""

import pyperclip
from colorama import Fore, Back

from Utils import PORT, clear, custom_print, get_ip, open_server


def main():
    ip = get_ip()
    pyperclip.copy(ip)

    clear()
    custom_print(
        "IP COPIADO PARA A ÁREA DE TRANSFERÊNCIA (Ctrl + V)",
        Fore.BLACK,
        Back.BLUE,
    )
    print(f"Compartilhe: http://{ip}")
    print('Aperte "Ctrl + C" para ENCERRAR a conexão')

    try:
        open_server(PORT)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
