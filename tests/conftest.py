"""Configuração compartilhada dos testes.

Garante que ``src/`` esteja no ``sys.path`` para importar o pacote
``sharepath`` sem precisar instalá-lo.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
