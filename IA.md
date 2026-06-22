# 🤖 IA.md — Contexto Operacional do Projeto

> Ponto único de recuperação de contexto técnico do SharePath.
> Fonte do padrão: Felixo System Design.

---

## 🎯 OBJETIVO DO PROJETO

SharePath compartilha arquivos **P2P entre 2 PCs** usando Python + Radmin VPN.
O Radmin cria uma rede privada (faixa `26.x.x.x`) e o SharePath sobe um servidor
HTTP nessa rede para o outro PC baixar os arquivos da pasta.

---

## 🏁 METAS & MILESTONES

⬜ pendente | 🔄 em progresso | ✅ concluída | ❌ cancelada

- ✅ [2026-06-22] Servidor de arquivos funcional via `http.server`.
- ✅ [2026-06-22] Adequação ao padrão de qualidade Felixo (refactor + start_app.py + docs).
- ✅ [2026-06-22] `start_app.py` autossustentável: cross-OS, detecta/instala o Radmin,
  imprime tutorial no terminal.
- ✅ [2026-06-22] Testes automatizados (pytest) e reorganização em `src/sharepath/`,
  `assets/`, `tests/`.

---

## 🛠️ STACK & DEPENDÊNCIAS

- **Python 3** (apenas).
- Dependências de runtime: `pyperclip` (clipboard), `colorama` (cores no terminal).
- Dependências de dev: `pytest` (em `requirements-dev.txt`).
- `start_app.py` e `radmin.py` usam só a biblioteca padrão.
- Servidor HTTP via `python -m http.server`.

---

## 📐 DECISÕES DE ARQUITETURA

- Código fica no pacote `src/sharepath/`: `main.py` (entrada), `utils.py` (IP,
  servidor, cores) e `radmin.py` (detecção/instalação/tutorial do Radmin, cross-OS).
- `start_app.py` (lançador único exigido pelo padrão) e docs ficam na **raiz**;
  ícone em `assets/`; testes em `tests/`.
- Responsabilidades separadas: entrada não conhece I/O do IP; lidar com o Radmin
  é responsabilidade exclusiva de `radmin.py`.
- Execução como pacote (`python -m sharepath`), com fallback de import para rodar
  o arquivo diretamente.
- Cache do IP ancorado em `Path.cwd()` (pasta compartilhada), não no caminho do módulo.

---

## 🎨 DECISÕES DE DESIGN & CONVENÇÕES

- Funções em `snake_case`; constantes em `MAIÚSCULAS` (`PORT`, `IP_CACHE_FILE`).
- Sem `import *` e sem `except:` nu — exceções específicas (`OSError`, etc.).
- Commits no formato Conventional Commits (`feat`/`fix`/`docs`/`refactor`/`chore`).

---

## 🧪 TESTES IMPORTANTES

✅ passou | ❌ falhou

- ✅ Suíte pytest (18 testes): validação de IP, cache de IP, detecção/instalação
  do Radmin e tutoriais por SO. Rode com `python -m pytest`.
- Verificação manual: `python start_app.py` instala deps, checa o Radmin, imprime
  o tutorial, sobe o servidor e abre o navegador.

---

## 🐛 BUGS & FIXES RELEVANTES

- **BUG:** caminho do cache de IP fixo em `C:/SharePath/YourIp.txt`.
  **CAUSA:** path hardcoded em `Utils.py`.
  **FIX:** cache passou a ficar ao lado do módulo (`Path(__file__).parent / "YourIp.txt"`),
  permitindo rodar de qualquer pasta/máquina.
- **BUG:** IP inválido era salvo sem validação.
  **CAUSA:** `getIp` não validava a entrada.
  **FIX:** `ask_ip`/`get_ip` agora validam com `is_valid_ip` antes de persistir.

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

- **Radmin VPN**: rede privada `26.x.x.x` entre os 2 PCs. Aberto via `os.startfile`
  procurando caminhos comuns de instalação (sem secrets envolvidos).

---

## 📝 NOTAS GERAIS

- A porta padrão é `8000` (constante `PORT` em `Utils.py` e `start_app.py`).
- `YourIp.txt` é cache local por máquina e fica fora do versionamento (`.gitignore`).

---

## 🧠 RESUMOS DE DECISÃO

- **CONTEXTO:** adequar repositório ao padrão Felixo System Design.
  **ALTERNATIVAS:** manter scripts como estavam vs. refatorar + adicionar artefatos do padrão.
  **DECISÃO:** refatorar `Utils.py`/`Script.py`, criar `start_app.py`, `LICENSE`, `IA.md`
  e atualizar README/`.gitignore`.
  **VALIDAÇÃO:** lint manual, validação de IP testada, fluxo de start verificado.
