"""Tools to load the config."""
import os
from typing import Any

from omegaconf import DictConfig, DictKeyType, OmegaConf


class NoConfigError(Exception):
    """Config does not exist."""


class InvalidConfigError(Exception):
    """Error during loading the config."""


class Config:
    """Config handler."""

    _config_path = os.path.expandvars(
        "%APPDATA%\\pcollection\\config.yml" if os.name == "nt" else "${HOME}/.config/pcollection/config.yml",
    )
    _config: DictConfig | None = None

    @classmethod
    def _load_config(cls) -> None:
        if not os.path.exists(cls._config_path):
            raise NoConfigError(
                f"No config found in '{cls._config_path}'",
            )
        _config = OmegaConf.load(cls._config_path)

        if not isinstance(_config, DictConfig):
            raise InvalidConfigError(
                f"Invalid config found in '{cls._config_path}'",
            )

        cls._config = _config

    @classmethod
    def set_config_path(cls, path: str) -> None:
        """Set config path.

        Args:
            path (str): new config path

        Raises:
            NoConfigError: raised if there is no config with the new path
        """
        cls._config_path = path
        cls._load_config()

    @classmethod
    def get(cls, key: DictKeyType, default_value: Any = None) -> Any:
        """Get config values."""
        if cls._config is None:
            cls._load_config()
        return cls._config.get(key, default_value)  # type: ignore[union-attr]
