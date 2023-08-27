"""Test collection_keeper.download."""
import os


def test_download_tags(tmpdir, mocker) -> None:
    """Test download_tags."""
    mocker.patch(
        "collection_keeper.download.utils._run_gdl",
        return_value=["tag_1\n", ""],
    )

    from collection_keeper import config
    from collection_keeper.download import download

    config.Config.set_config_path(os.path.abspath("./test_collection.yml"))

    with tmpdir.as_cwd() as _:
        paths, errors = download.download_tags()
        assert len(paths) == 1
        assert len(errors) == 1
        assert len(errors[0]) == 0
        assert "tag_1" in paths[0]
