"""Downloading utils."""
import subprocess as sp  # nosec
from itertools import cycle
from typing import Dict, Generator, List, Optional, Tuple

RESOURCES = {
    "e621": "https://e621.net/posts?tags={}",
    "rule34": "https://rule34.xxx/index.php?page=post&s=list&tags={}",
    "danbooru": "https://danbooru.donmai.us/posts?tags={}",
    "paheal": "https://rule34.paheal.net/post/list/{}",
    "joyreactor": "https://joyreactor.cc/tag/{}",
    "coomer": "https://coomer.party/onlyfans/user/{}",
    "kemono": "https://kemono.party/onlyfans/user/{}",
}


class DownloadError(Exception):
    """Error during downloading."""


class UnknownResourceError(Exception):
    """Error raised if the resource handle is unknown."""


def download(url: str, proxy: Optional[str] = None) -> List[str]:
    """Download media using gallery_dl.

    Args:
        url (str): url to pass into gallery_dl script
        proxy (Optional[str], optional): proxy connection string. Defaults to None.

    Raises:
        DownloadError: error during downloading.

    Returns:
        List[str]: list of all downloaded files (including existing before)
    """
    cmd = ("gallery-dl", "--proxy", proxy, url) if proxy is not None else ("gallery-dl", url)
    process = sp.Popen(
        cmd,  # nosec  # noqa: S603
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    if len(stderr) == 0:
        return stdout.split("\n")[:-1]
    raise DownloadError(stderr)


def generate_urls(
    tags_config: Dict[str, List[str]],
) -> Generator[str, None, None]:
    """Generate download URLs from the config.

    Args:
        tags_config (Dict[str, List[str]]): tags sub-config

    Raises:
        UnknownResourceError: raised if the resource handle is unknown

    Yields:
        Generator[str, None, None]: URLs
    """
    for tag in tags_config:
        for resource_handle in tags_config[tag]:
            resource_base_url = RESOURCES.get(resource_handle)
            if resource_base_url is None:
                raise UnknownResourceError(
                    f"Unknown resource handle: {resource_handle}. The options are: {', '.join(RESOURCES.keys())}",
                )
            yield resource_base_url.format(tag)


def generate_download_tasks(
    tags_config: Dict[str, List[str]],
    proxies: List[str | None],
) -> Generator[Tuple[str, str], None, None]:
    """Generate tuples to pass to download().

    Args:
        tags_config (Dict[str, List[str]]): tags sub-config
        proxies (List[str]): list of proxies

    Yields:
        Generator[Tuple[str, str], None, None]: list of Tuples
    """
    if len(proxies) == 0:
        proxies = [None]
    yield from zip(generate_urls(tags_config), cycle(proxies))
