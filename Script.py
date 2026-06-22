from Utils import *
import pyperclip as pc

ip = getIp()
pc.copy(ip)

clear()
customPrint('IP COPIADO PARA A ÁREA DE TRANSFERÊNCIA (Ctrl + V)', Fore.BLACK, Back.BLUE + '\n')
print('Aperte "Ctrl + C" para ENCERRAR a conexão')
openPort(port)