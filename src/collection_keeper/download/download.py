"""Main file in the download module."""

from typing import List

from joblib import Parallel, delayed
from omegaconf import OmegaConf
from tqdm.auto import tqdm

from collection_keeper.config import Config
from collection_keeper.download.utils import download, generate_download_tasks


def download_tags() -> List[str]:
    """Download all the tags, according to Config.

    Returns:
        List[str]: List of all files in the collection
    """
    download_config = Config.get(
        "download",
        OmegaConf.create(),
    )
    proxies = download_config.get(
        "proxies",
        [],
    )
    tags_config = download_config.get(
        "tags",
        {},
    )
    num_workers = download_config.get(
        "num_workers",
        1,
    )

    download_tasks = list(
        generate_download_tasks(
            tags_config=tags_config,
            proxies=proxies,
        ),
    )
    result = []
    with Parallel(n_jobs=num_workers, return_as="generator") as parallel:
        for files_list in parallel(delayed(download)(url, proxy) for url, proxy in tqdm(download_tasks)):
            result.extend(files_list)
    return result
