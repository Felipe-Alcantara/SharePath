from colorama import Fore, Back
import os

ipTxt = 'C:/SharePath/YourIp.txt'
port = 8000

def clear():
    os.system('cls')

def customPrint(txt, fore = Fore.RESET, back = Back.RESET):
    print(fore + back + txt + Back.RESET + Fore.RESET)

def openPort(port):
    os.system(f'python -m http.server {port} > nul')

def openRadmin():
    try: 
        os.startfile('C:/Program Files (x86)/Radmin VPN/RvRvpnGui')
    except:
        customPrint('Não foi possível encontrar o Radmin em seu dispositivo, abra-o manualmente', Fore.BLACK, Back.RED)
        print()

def askIp():
    openRadmin()
    ip = str(input('Coloque seu IP (Radmin): '))
    if ':' in ip: ip = ip.split(':')[0]
    return ip

def getIp():
    ip = ''

    try:
        with open(ipTxt, 'r', encoding = 'utf-8') as f:
            ip = f.read()
    except:
        pass

    if not ip or ip == '':
        ip = askIp()

    with open(ipTxt, 'w', encoding = 'utf-8') as f:
        f.write(ip)

    with open(ipTxt, 'r', encoding = 'utf-8') as f:
        return f.read() + ':' + str(port)