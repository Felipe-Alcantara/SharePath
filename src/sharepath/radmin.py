"""Detecção, download e instalação do Radmin VPN — cross-platform.

O Radmin VPN é um software **oficialmente só para Windows**. Este módulo:

- no **Windows**, procura a instalação, baixa o instalador oficial e instala
  silenciosamente quando o usuário autoriza;
- no **Linux/macOS**, detecta uma instalação via Wine (se houver) e, caso não
  exista, orienta o usuário com um tutorial claro (Wine + instalador oficial),
  já que não há build nativo.

Usa apenas a biblioteca padrão para não acoplar a instalação a dependências.
"""

import os
import sys
import shutil
import platform
import tempfile
import subprocess
import urllib.request
from pathlib import Path

# URL oficial de download do instalador do Radmin VPN (Windows).
RADMIN_DOWNLOAD_URL = "https://download.radmin-vpn.com/download/files/Radmin_VPN_1.4.4642.1.exe"
RADMIN_SITE = "https://www.radmin-vpn.com/"

# Caminhos comuns do executável no Windows.
_WINDOWS_PATHS = (
    r"C:/Program Files (x86)/Radmin VPN/RvRvpnGui.exe",
    r"C:/Program Files/Radmin VPN/RvRvpnGui.exe",
)


def current_os():
    """Retorna 'windows', 'linux', 'macos' ou 'unknown'."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    if system == "darwin":
        return "macos"
    return "unknown"


def _wine_radmin_paths():
    """Caminhos prováveis do Radmin sob prefixos Wine (Linux/macOS)."""
    home = Path.home()
    prefixes = [home / ".wine"]
    # Prefixo customizado, se o usuário usar um.
    env_prefix = os.environ.get("WINEPREFIX")
    if env_prefix:
        prefixes.append(Path(env_prefix))
    paths = []
    for prefix in prefixes:
        drive_c = prefix / "drive_c"
        paths.append(drive_c / "Program Files (x86)" / "Radmin VPN" / "RvRvpnGui.exe")
        paths.append(drive_c / "Program Files" / "Radmin VPN" / "RvRvpnGui.exe")
    return paths


def find_radmin():
    """Retorna o caminho do executável do Radmin, ou ``None`` se não achar."""
    if current_os() == "windows":
        for path in _WINDOWS_PATHS:
            if os.path.exists(path):
                return path
        return None

    # Linux/macOS: procura sob Wine.
    for path in _wine_radmin_paths():
        if path.exists():
            return str(path)
    return None


def is_installed():
    """True se uma instalação do Radmin foi encontrada."""
    return find_radmin() is not None


def open_radmin():
    """Abre o Radmin VPN. Retorna True se conseguiu iniciar."""
    path = find_radmin()
    if not path:
        return False

    try:
        if current_os() == "windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif shutil.which("wine"):
            subprocess.Popen(["wine", path],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            return False
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def _download(url, dest):
    """Baixa ``url`` para ``dest`` mostrando progresso simples."""
    def _progress(block_num, block_size, total_size):
        if total_size > 0:
            pct = min(100, block_num * block_size * 100 // total_size)
            print(f"\r  Baixando... {pct}%", end="", flush=True)

    urllib.request.urlretrieve(url, dest, _progress)
    print()  # quebra de linha após o progresso


def download_and_install_windows():
    """Baixa e instala o Radmin no Windows. Retorna True em caso de sucesso."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="sharepath-radmin-"))
    installer = tmp_dir / "RadminVPN_setup.exe"
    try:
        print(f"  Origem: {RADMIN_DOWNLOAD_URL}")
        _download(RADMIN_DOWNLOAD_URL, installer)
        print("  Executando o instalador (modo silencioso)...")
        # /S = instalação silenciosa (instalador NSIS, padrão do Radmin).
        result = subprocess.run([str(installer), "/S"])
        if result.returncode != 0:
            print("  O instalador retornou um código de erro. Tente instalar manualmente.")
            return False
        return is_installed()
    except (OSError, urllib.error.URLError) as exc:
        print(f"  Falha ao baixar/instalar: {exc}")
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def tutorial(os_name=None):
    """Retorna um tutorial de instalação do Radmin para o SO informado."""
    os_name = os_name or current_os()

    if os_name == "windows":
        return (
            "Como instalar o Radmin VPN no Windows:\n"
            f"  1. Baixe o instalador: {RADMIN_SITE}\n"
            "  2. Execute e siga o assistente (Avançar > Avançar > Concluir).\n"
            "  3. Abra o Radmin, crie ou entre numa rede e conecte os 2 PCs.\n"
            "  (Ou deixe o SharePath baixar e instalar automaticamente quando perguntar.)"
        )

    if os_name in ("linux", "macos"):
        wine_hint = (
            "    Linux:  sudo apt install wine   (ou o gerenciador da sua distro)\n"
            "    macOS:  brew install --cask wine-stable"
        )
        return (
            f"O Radmin VPN não tem versão nativa para {os_name}. Use o Wine:\n"
            "  1. Instale o Wine:\n"
            f"{wine_hint}\n"
            f"  2. Baixe o instalador do Radmin: {RADMIN_SITE}\n"
            "  3. Instale com:  wine Radmin_VPN_setup.exe\n"
            "  4. Crie/entre numa rede e conecte os 2 PCs.\n"
            "  Alternativa: rode o SharePath direto na máquina Windows do par."
        )

    return (
        "Não reconheci seu sistema operacional. Baixe o Radmin VPN em:\n"
        f"  {RADMIN_SITE}\n"
        "e instale conforme as instruções do site."
    )


def ensure_radmin(prompt_install=True, ask=input):
    """Garante o Radmin disponível, instalando-o quando possível e autorizado.

    Retorna True se o Radmin está (ou ficou) instalado. ``ask`` é injetável
    para facilitar testes (substitui ``input``).
    """
    if is_installed():
        return True

    os_name = current_os()
    print("Radmin VPN não encontrado neste computador.\n")

    # Auto-instalação só é viável no Windows (instalador oficial nativo).
    if os_name == "windows" and prompt_install:
        resposta = ask("Deseja baixar e instalar o Radmin VPN agora? [s/N] ").strip().lower()
        if resposta in ("s", "sim", "y", "yes"):
            print("\nBaixando e instalando o Radmin VPN...")
            if download_and_install_windows():
                print("Radmin VPN instalado com sucesso!\n")
                return True
            print("Não foi possível instalar automaticamente.\n")

    print(tutorial(os_name))
    print()
    return is_installed()
