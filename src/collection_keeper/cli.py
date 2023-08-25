"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m collection_keeper` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `collection_keeper.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `collection_keeper.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import logging

from collection_keeper.config import Config

logger = logging.getLogger("main")
logger.setLevel(logging.getLevelName(Config.get("log_level")))

fh = logging.FileHandler(Config.get("log_file"))
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s [%(name)s|%(levelname)s] %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="collection-keeper")


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `collection-keeper` or `python -m collection_keeper`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    return 0
