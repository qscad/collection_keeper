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

import click

from collection_keeper.config import Config
from collection_keeper.dedupe import mark_duplicates, update_phashes
from collection_keeper.download import download_tags
from collection_keeper.logging import _setup_logging


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="collection-keeper")


@click.command(name="Collection Keeper")
@click.option("--config", "-c", help="Config file location.")
@click.option("--download", "--update", "-u", help="Update collection.", is_flag=True)
@click.option("--dedupe", "-d", help="Deduplicate collection.", is_flag=True)
def main(
    download: bool,  # noqa: FBT001
    dedupe: bool,  # noqa: FBT001
    config: str | None = None,
) -> int:
    """Run the main program. Default pipeline includes downloading and deduplication."""
    if config is not None:
        Config.set_config_path(config)
    _setup_logging()
    if not (download or dedupe):
        download = True
        dedupe = True
    if download:
        download_tags()
    if dedupe:
        update_phashes(Config.get("collection_root"))
        mark_duplicates()
    return 0
