"""Dedupe images."""
import os
from glob import glob
from typing import Generator

from imagehash import phash
from PIL import Image
from sqlitedict import SqliteDict

from collection_keeper.config import Config


def is_image(filename: str) -> bool:
    """Check if the file has image extension."""
    f = filename.lower()
    return f.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg")) or ".jpg" in f


def update_phashes(root_folder: str) -> None:
    """Update phashes for images in the collection.

    Args:
        root_folder (str): root folder of the collection
    """
    db_path = Config.get("postprocessing").get("dedupe_strategy").get("phashes_db")
    commit_freq = Config.get("postprocessing").get("dedupe_strategy").get("commit_freq")
    calculated_phashes = 0
    with SqliteDict(db_path) as db:
        for img in generate_image_paths(root_folder):
            if img not in db:
                img_phash = phash(Image.open(img))
                db[img] = img_phash
                calculated_phashes += 1
                if (calculated_phashes + 1) % commit_freq == 0:
                    db.commit()
        db.commit()


def generate_image_paths(root_folder: str) -> Generator[str, None, None]:
    """Generate all image paths recursively."""
    yield from filter(
        is_image,
        glob(os.path.join(root_folder, "**", "*.*"), recursive=True),
    )
