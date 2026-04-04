import os
import shutil
from pathlib import Path

from app.configs.gitmastery_config import (
    GITMASTERY_CONFIG_NAME,
    GITMASTERY_LOG_NAME,
    METADATA_FOLDER_NAME,
)


def migrate_gitmastery_metadata(root: Path) -> None:
    """
    Migrates a legacy Git-Mastery metadata layout to the new .gitmastery/ folder structure.

    Moves and renames the following files under root/:
      .gitmastery.json        → .gitmastery/config.json
      .gitmastery.log         → .gitmastery/gitmastery.log  (created empty if absent)
      progress/               → .gitmastery/progress/

    The original files and directories are removed after a successful copy.
    """
    from app.commands.progress.constants import PROGRESS_LOCAL_FOLDER_NAME
    from app.utils.cli import rmtree

    gitmastery_dir = root / METADATA_FOLDER_NAME
    gitmastery_dir.mkdir(exist_ok=True)

    # Old config file must exist for migration to proceed
    if not (root / ".gitmastery.json").exists():
        raise FileNotFoundError("Legacy config file not found.")

    # shutil.copy2 overwrites destination if it already exists.
    shutil.copy2(root / ".gitmastery.json", gitmastery_dir / GITMASTERY_CONFIG_NAME)

    # Log file is created lazily and may not exist; create an empty one if it doesn't exist
    legacy_log = root / ".gitmastery.log"
    new_log = gitmastery_dir / GITMASTERY_LOG_NAME
    if legacy_log.exists():
        shutil.copy2(legacy_log, new_log)
    else:
        new_log.touch()

    # If new progress directory already exists, assume migration has failed in a partial state previously.
    # If migration had succeeded previously, this function would not be called.
    # Delete the new progress directory if it exists as shutil.copytree fails if destination exists.
    if (gitmastery_dir / PROGRESS_LOCAL_FOLDER_NAME).is_dir():
        rmtree(gitmastery_dir / PROGRESS_LOCAL_FOLDER_NAME)

    # Old progress directory must exist for migration to proceed
    if not (root / PROGRESS_LOCAL_FOLDER_NAME).is_dir():
        raise FileNotFoundError("Legacy progress directory not found.")

    shutil.copytree(
        root / PROGRESS_LOCAL_FOLDER_NAME,
        gitmastery_dir / PROGRESS_LOCAL_FOLDER_NAME,
    )

    # Remove legacy files last so that any failure before this point leaves
    # .gitmastery.json in place, allowing migration to be retried on the next run.
    rmtree(root / PROGRESS_LOCAL_FOLDER_NAME)
    if legacy_log.exists():
        os.remove(legacy_log)
    os.remove(root / ".gitmastery.json")
