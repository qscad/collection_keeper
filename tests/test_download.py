"""Test collection_keeper.download."""
import os


def test_download_tags(tmpdir, mocker) -> None:
    """Test download_tags."""
    mocker.patch("collection_keeper.download.utils.download", return_value=["tag_1"])

    from collection_keeper import config
    from collection_keeper.download import download

    config.Config.set_config_path(os.path.abspath("./test_collection.yml"))

    with tmpdir.as_cwd() as _:
        paths = download.download_tags()
        assert len(paths) == 1
        assert "tag_1" in paths[0]
