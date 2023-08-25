"""Test all things dedup."""
import os
import tempfile
from itertools import combinations

import numpy as np
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
        assert config.Config._config is not None
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


def _get_hashes_diff(img1, img2) -> int:
    return np.sum(
        np.abs(
            phash(Image.open(img1)).hash.reshape(-1).astype(np.int8)
            - phash(Image.open(img2)).hash.reshape(-1).astype(np.int8),
        ),
    )


def test_get_duplicates() -> None:
    """Test get_duplicates."""
    config.Config.set_config_path(os.path.abspath("./test_collection.yml"))
    with tempfile.NamedTemporaryFile() as tmp_file:
        assert config.Config._config is not None
        config.Config._config["postprocessing"]["dedupe_strategy"][
            "phashes_db"
        ] = tmp_file.name
        images.update_phashes("./test_images/")
        d = images.get_duplicates()
        assert len(d) == 1
        assert d[0] == ["./test_images/a/cat879.jpg", "./test_images/c/cat879.jpg"]

        d = images.get_duplicates(25)
        assert len(d) == 3
        for cluster in d:
            for i, j in combinations(cluster, 2):
                assert _get_hashes_diff(i, j) == (
                    phash(Image.open(i)) - phash(Image.open(j))
                )
