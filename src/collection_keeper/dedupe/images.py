"""Dedupe images."""
import os
from glob import glob
from sqlite3 import Binary
from typing import FrozenSet, Generator, List, Set

import numpy as np
from imagehash import ImageHash, hex_to_hash, phash
from PIL import Image
from sklearn.neighbors import NearestNeighbors
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


def get_dict(db_path: str) -> SqliteDict:
    """Get sqlite dictionary to store hashes."""
    return SqliteDict(db_path, encode=encode_hash, decode=decode_hash)


def generate_image_paths(root_folder: str) -> Generator[str, None, None]:
    """Generate all image paths recursively."""
    yield from filter(
        is_image,
        glob(os.path.join(root_folder, "**", "*.*"), recursive=True),
    )


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


def get_duplicates(distance: int = 0) -> List[List[str]]:
    """Get duplicates clusters.

    Args:
        distance (int, optional): maximum distance between objects in a duplicates cluster. Defaults to 0.

    Returns:
        List[List[str]]: list with clusters. Items can appear in more than one cluster.
    """
    db_path = Config.get("postprocessing").get("dedupe_strategy").get("phashes_db")
    keys = []
    matrix = []
    with get_dict(db_path) as db:
        for key in db:
            keys.append(key)
            matrix.append(db[key].hash.reshape(-1).astype(np.int8))
    matrix = np.stack(matrix)
    nneighbors = NearestNeighbors(radius=distance, metric="l1")
    nneighbors.fit(matrix)

    clusters: Set[FrozenSet[int]] = set()
    all_distances, all_neighbors = nneighbors.radius_neighbors(return_distance=True)
    for row_id, [distances, neighbors] in enumerate(
        zip(all_distances, all_neighbors),
    ):
        cluster_ids = frozenset(
            [
                *list(neighbors[distances <= distance]),
                row_id,
            ],
        )
        if len(cluster_ids) > 1:
            clusters.add(cluster_ids)

    return [[keys[i] for i in x] for x in clusters]
