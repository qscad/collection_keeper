"""Test all things config."""
from collection_keeper import config


def test_config_loading() -> None:
    """Test config loader."""
    config.Config.set_config_path("./test_collection.yml")

    assert config.Config.get("download").get("num_workers") == 1
    assert config.Config.get("download").get("tags").get("tag_1")[0] == "rule34"
