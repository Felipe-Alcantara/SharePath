"""Testes de utils: validação de IP e cache de IP."""

from sharepath import utils


class TestIsValidIp:
    def test_aceita_ipv4_valido(self):
        assert utils.is_valid_ip("26.123.45.67")
        assert utils.is_valid_ip("0.0.0.0")
        assert utils.is_valid_ip("255.255.255.255")

    def test_ignora_espacos_ao_redor(self):
        assert utils.is_valid_ip("  26.1.2.3  ")

    def test_rejeita_octeto_acima_de_255(self):
        assert not utils.is_valid_ip("26.1.2.300")
        assert not utils.is_valid_ip("256.0.0.1")

    def test_rejeita_formato_invalido(self):
        assert not utils.is_valid_ip("abc")
        assert not utils.is_valid_ip("")
        assert not utils.is_valid_ip("26.1.2")
        assert not utils.is_valid_ip("26.1.2.3.4")
        assert not utils.is_valid_ip("26.1.2.3:8000")


class TestGetIp:
    def test_usa_cache_valido_sem_perguntar(self, tmp_path, monkeypatch):
        cache = tmp_path / "YourIp.txt"
        cache.write_text("26.10.20.30", encoding="utf-8")
        monkeypatch.setattr(utils, "IP_CACHE_FILE", cache)
        # Se tentar perguntar, falha o teste.
        monkeypatch.setattr(utils, "ask_ip", lambda: pytest_fail())

        assert utils.get_ip() == f"26.10.20.30:{utils.PORT}"

    def test_pergunta_e_salva_quando_cache_ausente(self, tmp_path, monkeypatch):
        cache = tmp_path / "YourIp.txt"
        monkeypatch.setattr(utils, "IP_CACHE_FILE", cache)
        monkeypatch.setattr(utils, "ask_ip", lambda: "26.99.88.77")

        resultado = utils.get_ip()

        assert resultado == f"26.99.88.77:{utils.PORT}"
        assert cache.read_text(encoding="utf-8") == "26.99.88.77"

    def test_pergunta_quando_cache_invalido(self, tmp_path, monkeypatch):
        cache = tmp_path / "YourIp.txt"
        cache.write_text("lixo-invalido", encoding="utf-8")
        monkeypatch.setattr(utils, "IP_CACHE_FILE", cache)
        monkeypatch.setattr(utils, "ask_ip", lambda: "26.1.1.1")

        assert utils.get_ip() == f"26.1.1.1:{utils.PORT}"
        assert cache.read_text(encoding="utf-8") == "26.1.1.1"


def pytest_fail():
    raise AssertionError("ask_ip não deveria ter sido chamado com cache válido")
