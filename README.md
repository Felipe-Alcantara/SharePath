# SharePath

Compartilhamento de arquivos **P2P entre 2 PCs** usando **Python + [Radmin VPN](https://www.radmin-vpn.com/)**.

A ideia é simples: o Radmin VPN cria uma rede privada (faixa de IP `26.x.x.x`) entre as duas
máquinas, e o SharePath sobe um servidor HTTP nessa rede para o outro PC baixar os arquivos da pasta.

> Projeto feito por mim e pelo meu amigo **Deimox**.

## Como funciona

1. `Script.py` lê (ou pergunta) o seu IP do Radmin VPN e o copia para a área de transferência.
2. Sobe um servidor de arquivos com `python -m http.server 8000` na pasta atual.
3. O outro PC, conectado à mesma rede Radmin, acessa `http://SEU_IP_RADMIN:8000` no navegador
   e baixa os arquivos.

## Pré-requisitos

- [Python 3](https://www.python.org/) instalado
- [Radmin VPN](https://www.radmin-vpn.com/) instalado e com a rede já criada/conectada nos 2 PCs
- Dependências Python:

```bash
pip install -r requirements.txt
```

## Uso

1. Coloque os arquivos que quer compartilhar dentro da pasta do projeto.
2. Rode:

```bash
python Script.py
```

3. Na primeira vez, ele abre o Radmin e pede o seu IP (o IP fica salvo em `YourIp.txt`).
4. O IP já vem copiado — mande pro seu amigo, que abre `http://SEU_IP:8000` no navegador.
5. `Ctrl + C` encerra o servidor.

## Arquivos

| Arquivo         | Função                                                        |
|-----------------|---------------------------------------------------------------|
| `Script.py`     | Ponto de entrada: pega o IP, copia e sobe o servidor          |
| `Utils.py`      | Funções de apoio (abrir Radmin, ler/salvar IP, util de cores) |
| `ShareIcon.ico` | Ícone do projeto                                              |
| `YourIp.txt`    | Cache local do seu IP do Radmin (ignorado pelo git)           |

## Observações

- O caminho do `YourIp.txt` está fixo como `C:/SharePath/YourIp.txt` no `Utils.py`.
  Para rodar de outra pasta, ajuste esse caminho.
- A porta padrão é `8000` (`port` em `Utils.py`).
