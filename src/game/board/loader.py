"""loader"""
import importlib


class BoardEventPluginInterface:
    """A plugin has a single function called initialize."""

    @staticmethod
    def initialize() -> None:
        """Initialize the plugin"""


def import_module(name: str) -> BoardEventPluginInterface:
    return importlib.import_module(name)  # type: ignore


def load_plugins(plugins: list[str]) -> None:
    """Load the plugins defined in the plugins list."""
    for plugin_name in plugins:
        plugin = import_module(plugin_name)
        plugin.initialize()
