"""Test all things dedup."""
import os
import tempfile

from imagehash import phash
from PIL import Image

from collection_keeper import config
from collection_keeper.dedupe import images


def test_is_image() -> None:
    """Test is_image."""
    assert images.is_image("a.png")
    assert images.is_image("a.jpg")
    assert images.is_image("a.jpeg")
    assert images.is_image("a.gif")


def test_hash_serialization() -> None:
    """Test encode_hash and decode_hash."""
    hsh = phash(Image.open("./test_images/a/cat879.jpg"))
    assert images.decode_hash(images.encode_hash(hsh)) == hsh


def test_update_phashes() -> None:
    """Test update_phashes."""
    config.Config.set_config_path(os.path.abspath("./test_collection.yml"))
    with tempfile.NamedTemporaryFile() as tmp_file:
        config.Config._config["postprocessing"]["dedupe_strategy"][
            "phashes_db"
        ] = tmp_file.name
        images.update_phashes("./test_images/")
        db_path = (
            config.Config.get("postprocessing").get("dedupe_strategy").get("phashes_db")
        )
        with images.get_dict(db_path) as db:
            assert len(db) == 6
            assert db["./test_images/a/cat879.jpg"] == db["./test_images/c/cat879.jpg"]
            assert db["./test_images/a/cat879.jpg"] != db["./test_images/c/cat4270.jpg"]
