import unittest

from mcp_server_starter.config.settings import load_settings


class LoadSettingsTest(unittest.TestCase):
    def test_uses_defaults(self) -> None:
        settings = load_settings({})

        self.assertEqual(settings.server_name, "mcp-server-starter")
        self.assertEqual(settings.server_version, "0.1.0")
        self.assertEqual(settings.log_level, "INFO")

    def test_normalizes_log_level(self) -> None:
        settings = load_settings({"LOG_LEVEL": "debug"})

        self.assertEqual(settings.log_level, "DEBUG")

    def test_falls_back_for_invalid_log_level(self) -> None:
        settings = load_settings({"LOG_LEVEL": "verbose"})

        self.assertEqual(settings.log_level, "INFO")

    def test_loads_pii_settings(self) -> None:
        settings = load_settings({"PII_MODEL_NAME": "custom/model", "PII_THRESHOLD": "0.7"})

        self.assertEqual(settings.pii_model_name, "custom/model")
        self.assertEqual(settings.pii_threshold, 0.7)


if __name__ == "__main__":
    unittest.main()
