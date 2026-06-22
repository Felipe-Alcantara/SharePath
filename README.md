<div align="center">

# 🔗 SharePath

**Compartilhamento de arquivos P2P entre 2 PCs com Python + Radmin VPN**

![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![Radmin VPN](https://img.shields.io/badge/Radmin-VPN-26a269)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6?logo=windows&logoColor=white)

</div>

---

## 📋 Índice

- [🎯 Sobre](#-sobre)
- [⚙️ Como funciona](#️-como-funciona)
- [📁 Estrutura do projeto](#-estrutura-do-projeto)
- [✅ Pré-requisitos](#-pré-requisitos)
- [🚀 Como usar](#-como-usar) — ⭐ **comece por aqui**
- [🔧 Arquivos](#-arquivos)
- [⚠️ Observações](#️-observações)
- [📝 Licença & Autores](#-licença--autores)

---

## 🎯 Sobre

A ideia é simples: o [Radmin VPN](https://www.radmin-vpn.com/) cria uma rede privada
(faixa de IP `26.x.x.x`) entre as duas máquinas, e o SharePath sobe um servidor HTTP
nessa rede para o outro PC baixar os arquivos da pasta.

> Projeto feito por **Felipe (Felipe-Alcantara)** e seu amigo **Deimox**.

---

## ⚙️ Como funciona

1. `Script.py` lê (ou pergunta) o seu IP do Radmin VPN e o copia para a área de transferência.
2. Sobe um servidor de arquivos com `python -m http.server 8000` na pasta atual.
3. O outro PC, conectado à mesma rede Radmin, acessa `http://SEU_IP_RADMIN:8000` no
   navegador e baixa os arquivos.

---

## 📁 Estrutura do projeto

```text
SharePath/
├── start_app.py        # ⭐ lançador único: instala + inicia + abre o navegador
├── Script.py           # ponto de entrada: pega o IP, copia e sobe o servidor
├── Utils.py            # funções de apoio (Radmin, IP, servidor, cores)
├── requirements.txt    # dependências Python
├── ShareIcon.ico       # ícone do projeto
├── IA.md               # contexto operacional do projeto
└── YourIp.txt          # cache local do seu IP (ignorado pelo git)
```

---

## ✅ Pré-requisitos

- [Python 3](https://www.python.org/) instalado
- [Radmin VPN](https://www.radmin-vpn.com/) instalado e com a rede já criada/conectada nos 2 PCs

---

## 🚀 Como usar

### Opção 1 — Lançador único (recomendado) ⭐

Um comando instala as dependências, inicia o SharePath e abre o navegador local:

```bash
python start_app.py
```

Outras opções:

```bash
python start_app.py --no-install   # pula a instalação de dependências
python start_app.py --no-browser   # inicia sem abrir o navegador
python start_app.py restart        # libera a porta e reinicia limpo
```

### Opção 2 — Manual

```bash
pip install -r requirements.txt
python Script.py
```

### Em seguida

1. Coloque os arquivos que quer compartilhar dentro da pasta do projeto.
2. Na primeira vez, o SharePath abre o Radmin e pede o seu IP (salvo em `YourIp.txt`).
3. O IP já vem copiado — mande pro seu amigo, que abre `http://SEU_IP:8000` no navegador.
4. `Ctrl + C` encerra o servidor.

---

## 🔧 Arquivos

| Arquivo            | Função                                                          |
|--------------------|-----------------------------------------------------------------|
| **`start_app.py`** | Lançador único: instala deps, inicia o app e abre o navegador   |
| **`Script.py`**    | Ponto de entrada: pega o IP, copia e sobe o servidor            |
| **`Utils.py`**     | Funções de apoio (abrir Radmin, ler/salvar IP, cores, servidor) |
| **`ShareIcon.ico`**| Ícone do projeto                                                |
| **`YourIp.txt`**   | Cache local do seu IP do Radmin (ignorado pelo git)             |

---

## ⚠️ Observações

- O `YourIp.txt` fica ao lado dos scripts, então o projeto roda de qualquer pasta/máquina.
- A porta padrão é `8000` (constante `PORT` em `Utils.py` e `start_app.py`).
- O servidor expõe os arquivos da pasta atual na rede Radmin — coloque só o que quer compartilhar.

---

## 📝 Licença & Autores

Distribuído sob a licença **MIT** — veja [LICENSE](LICENSE).

Feito por **[Felipe (Felipe-Alcantara)](https://github.com/Felipe-Alcantara)** e **Deimox**.
