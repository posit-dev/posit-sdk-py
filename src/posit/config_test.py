from unittest.mock import Mock, patch

from .config import Config, ConfigBuilder, EnvironmentConfigProvider


class TestEnvironmentConfigProvider:
    @patch.dict("os.environ", {"CONNECT_API_KEY": "foobar"})
    def test_get_api_key(self):
        provider = EnvironmentConfigProvider()
        api_key = provider.get_value("api_key")
        assert api_key == "foobar"

    @patch.dict("os.environ", {"CONNECT_SERVER": "http://foo.bar"})
    def test_get_endpoint(self):
        provider = EnvironmentConfigProvider()
        endpoint = provider.get_value("endpoint")
        assert endpoint == "http://foo.bar"

    def test_get_value_miss(self):
        provider = EnvironmentConfigProvider()
        value = provider.get_value("foobar")
        assert value == None


class TestConfigBuilder:
    def test_build(self):
        builder = ConfigBuilder()
        assert builder._config == Config()

    def test_build_with_provider(self):
        provider = Mock()
        provider.get_value = Mock()
        builder = ConfigBuilder([provider])
        builder.build()
        for key in Config.__annotations__:
            provider.get_value.assert_any_call(key)

    def test_set_api_key(self):
        builder = ConfigBuilder()
        builder.set_api_key("foobar")
        assert builder._config.api_key == "foobar"

    def test_set_endpoint(self):
        builder = ConfigBuilder()
        builder.set_endpoint("http://foo.bar")
        assert builder._config.endpoint == "http://foo.bar"
