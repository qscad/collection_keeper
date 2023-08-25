"""Dedupe images."""
import os
from glob import glob
from sqlite3 import Binary
from typing import Generator

from imagehash import ImageHash, hex_to_hash, phash
from PIL import Image
from sqlitedict import SqliteDict, decode, encode

from collection_keeper.config import Config


def is_image(filename: str) -> bool:
    """Check if the file has image extension."""
    f = filename.lower()
    return f.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg")) or ".jpg" in f


def encode_hash(image_hash: ImageHash) -> Binary:
    """Convert image hash to hex string."""
    return encode(str(image_hash))


def decode_hash(stored_data: Binary) -> ImageHash:
    """Convert hex string to image hash."""
    return hex_to_hash(decode(stored_data))


def update_phashes(root_folder: str) -> None:
    """Update phashes for images in the collection.

    Args:
        root_folder (str): root folder of the collection
    """
    db_path = Config.get("postprocessing").get("dedupe_strategy").get("phashes_db")
    commit_freq = Config.get("postprocessing").get("dedupe_strategy").get("commit_freq")
    calculated_phashes = 0
    with get_dict(db_path) as db:
        for img in generate_image_paths(root_folder):
            if img not in db:
                img_phash = phash(Image.open(img))
                db[img] = img_phash
                calculated_phashes += 1
                if (calculated_phashes + 1) % commit_freq == 0:
                    db.commit()
        db.commit()


def get_dict(db_path: str) -> SqliteDict:
    """Get sqlite dictionary to store hashes."""
    return SqliteDict(db_path, encode=encode_hash, decode=decode_hash)


def generate_image_paths(root_folder: str) -> Generator[str, None, None]:
    """Generate all image paths recursively."""
    yield from filter(
        is_image,
        glob(os.path.join(root_folder, "**", "*.*"), recursive=True),
    )
