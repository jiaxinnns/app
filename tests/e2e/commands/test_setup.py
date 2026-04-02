import json
from pathlib import Path


def test_setup(setup_gitmastery_root: Path) -> None:
    """setup creates the expected directory structure, config, and empty progress file."""
    gitmastery_dir = setup_gitmastery_root / ".gitmastery"
    assert gitmastery_dir.is_dir()

    progress_dir = gitmastery_dir / "progress"
    assert progress_dir.is_dir()

    progress_file = progress_dir / "progress.json"
    assert progress_file.is_file()
    assert json.loads(progress_file.read_text()) == []

    config_file = gitmastery_dir / "config.json"
    assert config_file.is_file()
    config = json.loads(config_file.read_text())
    assert config["progress_local"] is True
    assert config["progress_remote"] is False

    assert (gitmastery_dir / "gitmastery.log").is_file()
