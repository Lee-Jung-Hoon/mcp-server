import logging
import unittest
from dataclasses import dataclass

from mcp_server_starter.config.settings import AppSettings
from mcp_server_starter.core.context import AppContext
from mcp_server_starter.core.registry import register_feature_modules


@dataclass(frozen=True)
class FakeModule:
    name: str

    def register(self, server: list[str], context: AppContext) -> None:
        server.append(self.name)


class RegisterFeatureModulesTest(unittest.TestCase):
    def test_registers_in_order(self) -> None:
        server: list[str] = []
        context = AppContext(AppSettings(), logging.getLogger("test"))

        register_feature_modules(server, context, (FakeModule("one"), FakeModule("two")))

        self.assertEqual(server, ["one", "two"])

    def test_rejects_duplicate_names(self) -> None:
        server: list[str] = []
        context = AppContext(AppSettings(), logging.getLogger("test"))

        with self.assertRaisesRegex(ValueError, "Duplicate MCP feature module name"):
            register_feature_modules(server, context, (FakeModule("same"), FakeModule("same")))


if __name__ == "__main__":
    unittest.main()
