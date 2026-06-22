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
├── start_app.py          # ⭐ lançador único: deps + Radmin + tutorial + inicia + navegador
├── Script.py             # ponto de entrada: pega o IP, copia e sobe o servidor
├── Utils.py              # funções de apoio (IP, servidor, cores)
├── radmin.py             # Radmin VPN: detecta, baixa/instala e orienta (cross-OS)
├── requirements.txt      # dependências Python
├── requirements-dev.txt  # dependências de teste (pytest)
├── tests/                # testes automatizados (pytest)
├── ShareIcon.ico         # ícone do projeto
├── IA.md                 # contexto operacional do projeto
└── YourIp.txt            # cache local do seu IP (ignorado pelo git)
```

---

## ✅ Pré-requisitos

- [Python 3](https://www.python.org/) instalado
- [Radmin VPN](https://www.radmin-vpn.com/) com a rede já criada/conectada nos 2 PCs
  — se faltar, o `start_app.py` oferece **baixar e instalar automaticamente** (Windows)
  ou mostra um tutorial por SO (Linux/macOS via Wine).

---

## 🚀 Como usar

### Opção 1 — Lançador único (recomendado) ⭐

Um comando instala as dependências, inicia o SharePath e abre o navegador local:

```bash
python start_app.py
```

O lançador também **verifica o Radmin VPN** (oferece instalar se faltar) e
imprime um **passo a passo de uso no terminal**, em qualquer SO.

Outras opções:

```bash
python start_app.py --dir "C:/Fotos"  # compartilha outra pasta (padrão: a pasta atual)
python start_app.py --port 8123       # fixa a porta (padrão 8000; troca sozinha se ocupada)
python start_app.py --no-install      # pula a instalação de dependências
python start_app.py --no-browser      # inicia sem abrir o navegador
python start_app.py --no-radmin       # pula a verificação do Radmin VPN
python start_app.py restart           # libera a porta e reinicia limpo
```

### Opção 2 — Manual

```bash
pip install -r requirements.txt
python -m sharepath                   # ou: python src/sharepath/main.py
python -m sharepath --dir "C:/Fotos"  # compartilha a pasta indicada
python -m sharepath --port 8123       # porta fixa
```

### Em seguida

1. Escolha o que compartilhar: coloque os arquivos na pasta atual, ou aponte
   outra pasta com `--dir PASTA` (ou a variável `SHAREPATH_DIR`).
2. Na primeira vez, o SharePath abre o Radmin e pede o seu IP (salvo em `YourIp.txt`).
3. O IP **e a porta escolhida** já vêm copiados — mande pro seu amigo, que abre
   `http://SEU_IP:PORTA` no navegador.
4. `Ctrl + C` encerra o servidor.

> 📁 **Pasta a compartilhar:** por padrão é a pasta atual. Use `--dir PASTA` ou
> a variável `SHAREPATH_DIR` para servir qualquer outra pasta, sem precisar mover
> arquivos.

> 🔌 **Porta automática:** o padrão é `8000`, mas se essa porta estiver ocupada
> (por outro app), o SharePath escolhe sozinho a próxima porta livre e avisa qual.
> Você também pode fixar com `--port` ou a variável `SHAREPATH_PORT`.

---

## 🔧 Arquivos

| Caminho                    | Função                                                       |
|----------------------------|--------------------------------------------------------------|
| **`start_app.py`**         | Lançador único: deps + Radmin + tutorial + inicia + navegador|
| **`src/sharepath/main.py`**| Ponto de entrada: pega o IP, copia e sobe o servidor         |
| **`src/sharepath/utils.py`**| Funções de apoio (ler/salvar IP, cores, servidor)           |
| **`src/sharepath/radmin.py`**| Radmin VPN: detecta, baixa/instala e orienta (cross-OS)    |
| **`assets/ShareIcon.ico`** | Ícone do projeto                                             |
| **`tests/`**               | Testes automatizados (pytest)                               |
| **`YourIp.txt`**           | Cache local do seu IP do Radmin (ignorado pelo git)         |

---

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Cobrem a validação de IP, o cache de IP, a resolução automática de porta e a
detecção/instalação do Radmin VPN.

---

## ⚠️ Observações

- O `YourIp.txt` fica na raiz do projeto, então ele roda de qualquer pasta/máquina.
- A porta padrão é `8000`, mas é **resolvida automaticamente**: se estiver ocupada,
  o SharePath usa a próxima porta livre. Fixe com `--port` ou `SHAREPATH_PORT`.
- Por padrão o servidor expõe a **pasta atual**; use `--dir` / `SHAREPATH_DIR` para
  escolher outra. Lembre que **tudo na pasta servida fica acessível** na rede Radmin.
- O Radmin VPN é oficialmente só para Windows; em Linux/macOS roda via Wine.

---

## 📝 Licença & Autores

Distribuído sob a licença **MIT** — veja [LICENSE](LICENSE).

Feito por **[Felipe (Felipe-Alcantara)](https://github.com/Felipe-Alcantara)** e **Deimox**.
