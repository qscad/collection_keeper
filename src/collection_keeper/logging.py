"""Logging tools."""
import logging

from collection_keeper.config import Config


def _setup_logging() -> None:
    logger = logging.getLogger("main")
    logger.setLevel(logging.getLevelName(Config.get("log_level")))

    fh = logging.FileHandler(Config.get("log_file"))
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s [%(name)s|%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
