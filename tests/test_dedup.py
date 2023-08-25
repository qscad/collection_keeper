"""Test all things dedup."""
import os

from sqlitedict import SqliteDict

from collection_keeper import config
from collection_keeper.dedupe import images


def test_is_image() -> None:
    """Test is_image."""
    assert images.is_image("a.png")
    assert images.is_image("a.jpg")
    assert images.is_image("a.jpeg")
    assert images.is_image("a.gif")


def test_update_phashes() -> None:
    """Test update_phashes."""
    config.Config.set_config_path(os.path.abspath("./test_collection.yml"))
    images.update_phashes("./test_images/")
    db_path = (
        config.Config.get("postprocessing").get("dedupe_strategy").get("phashes_db")
    )
    with SqliteDict(db_path) as db:
        assert len(db) == 6
        assert db["./test_images/a/cat879.jpg"] == db["./test_images/c/cat879.jpg"]
        assert db["./test_images/a/cat879.jpg"] != db["./test_images/c/cat4270.jpg"]
    os.remove(db_path)
