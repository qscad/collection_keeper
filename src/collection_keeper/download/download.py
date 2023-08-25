"""Main file in the download module."""

from typing import List, Tuple

from joblib import Parallel, delayed
from omegaconf import OmegaConf
from tqdm.auto import tqdm

from collection_keeper.config import Config
from collection_keeper.download.utils import download, generate_download_tasks
from collection_keeper.utils import safe_call


def download_tags() -> Tuple[List[str], List[str]]:
    """Download all the tags, according to Config.

    Returns:
        Tuple[List[str], List[str]]: List of all files in the collection and raised errors
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
    result_errors = []
    with Parallel(n_jobs=num_workers, return_as="generator") as parallel:
        for files_list, errors in parallel(
            delayed(safe_call(download))(url, proxy) for url, proxy in tqdm(download_tasks)
        ):
            result.extend(files_list)
            result_errors.extend(errors)
    return result, result_errors
