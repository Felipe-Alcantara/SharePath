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

        assert utils.get_ip() == "26.10.20.30"

    def test_pergunta_e_salva_quando_cache_ausente(self, tmp_path, monkeypatch):
        cache = tmp_path / "YourIp.txt"
        monkeypatch.setattr(utils, "IP_CACHE_FILE", cache)
        monkeypatch.setattr(utils, "ask_ip", lambda: "26.99.88.77")

        resultado = utils.get_ip()

        assert resultado == "26.99.88.77"
        assert cache.read_text(encoding="utf-8") == "26.99.88.77"

    def test_pergunta_quando_cache_invalido(self, tmp_path, monkeypatch):
        cache = tmp_path / "YourIp.txt"
        cache.write_text("lixo-invalido", encoding="utf-8")
        monkeypatch.setattr(utils, "IP_CACHE_FILE", cache)
        monkeypatch.setattr(utils, "ask_ip", lambda: "26.1.1.1")

        assert utils.get_ip() == "26.1.1.1"
        assert cache.read_text(encoding="utf-8") == "26.1.1.1"


class TestPortResolution:
    def test_porta_livre_e_detectada(self):
        # Pede ao SO uma porta efêmera livre e confirma que é vista como livre.
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            livre = s.getsockname()[1]
        # fora do "with" o socket fechou; a porta deve estar livre de novo
        assert utils.is_port_free(livre)

    def test_porta_ocupada_e_detectada(self):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            s.listen()
            ocupada = s.getsockname()[1]
            assert not utils.is_port_free(ocupada)

    def test_find_free_port_retorna_preferida_quando_livre(self, monkeypatch):
        monkeypatch.setattr(utils, "is_port_free", lambda p, host="0.0.0.0": p == 9123)
        assert utils.find_free_port(9123) == 9123

    def test_find_free_port_sobe_quando_ocupada(self, monkeypatch):
        # 9000 e 9001 ocupadas; 9002 livre.
        livres = {9002}
        monkeypatch.setattr(utils, "is_port_free", lambda p, host="0.0.0.0": p in livres)
        assert utils.find_free_port(9000) == 9002

    def test_resolve_port_prioriza_argumento(self, monkeypatch):
        monkeypatch.setattr(utils, "find_free_port", lambda p: p)
        monkeypatch.delenv(utils.PORT_ENV_VAR, raising=False)
        assert utils.resolve_port(8123) == 8123

    def test_resolve_port_usa_env(self, monkeypatch):
        monkeypatch.setattr(utils, "find_free_port", lambda p: p)
        monkeypatch.setenv(utils.PORT_ENV_VAR, "8765")
        assert utils.resolve_port() == 8765

    def test_resolve_port_troca_quando_ocupada(self, monkeypatch):
        # padrão pedido = 8000, mas find_free_port devolve outra (auto-troca)
        monkeypatch.setattr(utils, "find_free_port", lambda p: 8050)
        monkeypatch.delenv(utils.PORT_ENV_VAR, raising=False)
        assert utils.resolve_port() == 8050

    def test_resolve_port_env_invalida_cai_no_padrao(self, monkeypatch):
        monkeypatch.setattr(utils, "find_free_port", lambda p: p)
        monkeypatch.setenv(utils.PORT_ENV_VAR, "abc")
        assert utils.resolve_port() == utils.PORT


def pytest_fail():
    raise AssertionError("ask_ip não deveria ter sido chamado com cache válido")
