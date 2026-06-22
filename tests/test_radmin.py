"""Testes do módulo radmin: detecção, tutorial e fluxo de garantia."""

from sharepath import radmin


class TestCurrentOs:
    def test_reconhece_sistemas(self, monkeypatch):
        monkeypatch.setattr(radmin.platform, "system", lambda: "Windows")
        assert radmin.current_os() == "windows"
        monkeypatch.setattr(radmin.platform, "system", lambda: "Linux")
        assert radmin.current_os() == "linux"
        monkeypatch.setattr(radmin.platform, "system", lambda: "Darwin")
        assert radmin.current_os() == "macos"
        monkeypatch.setattr(radmin.platform, "system", lambda: "Plan9")
        assert radmin.current_os() == "unknown"


class TestTutorial:
    def test_windows_aponta_site_oficial(self):
        texto = radmin.tutorial("windows")
        assert radmin.RADMIN_SITE in texto
        assert "Windows" in texto

    def test_linux_menciona_wine(self):
        texto = radmin.tutorial("linux")
        assert "Wine" in texto or "wine" in texto

    def test_macos_menciona_wine(self):
        texto = radmin.tutorial("macos")
        assert "wine" in texto.lower()

    def test_desconhecido_tem_fallback(self):
        texto = radmin.tutorial("unknown")
        assert radmin.RADMIN_SITE in texto


class TestFindRadmin:
    def test_retorna_caminho_quando_existe(self, monkeypatch):
        monkeypatch.setattr(radmin, "current_os", lambda: "windows")
        monkeypatch.setattr(radmin.os.path, "exists", lambda p: True)
        assert radmin.find_radmin() == radmin._WINDOWS_PATHS[0]

    def test_retorna_none_quando_ausente(self, monkeypatch):
        monkeypatch.setattr(radmin, "current_os", lambda: "windows")
        monkeypatch.setattr(radmin.os.path, "exists", lambda p: False)
        assert radmin.find_radmin() is None
        assert radmin.is_installed() is False


class TestEnsureRadmin:
    def test_retorna_true_quando_ja_instalado(self, monkeypatch):
        monkeypatch.setattr(radmin, "is_installed", lambda: True)
        assert radmin.ensure_radmin() is True

    def test_instala_no_windows_quando_autorizado(self, monkeypatch):
        chamadas = {"instalou": False}

        # Não instalado no início; instalado após "instalar".
        estados = iter([False, True, True])
        monkeypatch.setattr(radmin, "is_installed", lambda: next(estados))
        monkeypatch.setattr(radmin, "current_os", lambda: "windows")

        def fake_install():
            chamadas["instalou"] = True
            return True

        monkeypatch.setattr(radmin, "download_and_install_windows", fake_install)

        ok = radmin.ensure_radmin(ask=lambda _: "s")
        assert ok is True
        assert chamadas["instalou"] is True

    def test_mostra_tutorial_quando_recusa(self, monkeypatch, capsys):
        monkeypatch.setattr(radmin, "is_installed", lambda: False)
        monkeypatch.setattr(radmin, "current_os", lambda: "windows")

        ok = radmin.ensure_radmin(ask=lambda _: "n")
        assert ok is False
        saida = capsys.readouterr().out
        assert radmin.RADMIN_SITE in saida

    def test_linux_nao_tenta_instalar_e_orienta(self, monkeypatch, capsys):
        monkeypatch.setattr(radmin, "is_installed", lambda: False)
        monkeypatch.setattr(radmin, "current_os", lambda: "linux")

        ok = radmin.ensure_radmin(ask=lambda _: "s")
        assert ok is False
        assert "wine" in capsys.readouterr().out.lower()
