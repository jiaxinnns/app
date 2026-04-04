from functools import wraps
from typing import Any, Callable, Dict, Tuple

import click

from app.configs.gitmastery_config import (
    GITMASTERY_CONFIG_NAME,
    GITMASTERY_FOLDER_NAME,
    GitMasteryConfig,
    migrate_to_gitmastery_folder,
)
from app.configs.utils import find_root
from app.hooks.utils import generate_cds_string
from app.utils.click import CliContextKey, error, warn


def in_gitmastery_root(
    must: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @click.pass_context
        @wraps(func)
        def wrapper(
            ctx: click.Context, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]
        ) -> Any:
            root = find_root(GITMASTERY_CONFIG_NAME, folder=GITMASTERY_FOLDER_NAME)
            if root is None:
                old_root = find_root(".gitmastery.json")
                if old_root is None:
                    error(
                        f"You are not in a Git-Mastery root folder. Navigate to an appropriate folder or use "
                        f"{click.style('gitmastery setup', bold=True, italic=True)}"
                    )
                try:
                    migrate_to_gitmastery_folder(old_root[0])
                    warn("Migrated your Git-Mastery metadata to .gitmastery/ folder.")
                    root = find_root(
                        GITMASTERY_CONFIG_NAME, folder=GITMASTERY_FOLDER_NAME
                    )
                except Exception:
                    error(
                        "Failed to automatically migrate your Git-Mastery metadata to the .gitmastery/ folder. "
                        "Please manually move your .gitmastery.json, .gitmastery.log, and progress/ folder into "
                        "a .gitmastery/ folder in your exercises root directory."
                    )
                if root is None:
                    error(
                        "Failed to automatically migrate your Git-Mastery metadata to the .gitmastery/ folder. "
                        "Please manually move your .gitmastery.json, .gitmastery.log, and progress/ folder into "
                        "a .gitmastery/ folder in your exercises root directory."
                    )

            path, cds = root
            config = GitMasteryConfig.read(path, cds)

            if must and cds != 0:
                error(
                    f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} "
                    "to move to the root of the Git-Mastery root folder."
                )

            ctx.obj[CliContextKey.GITMASTERY_ROOT_CONFIG] = config
            return func(*args, **kwargs)

        return wrapper

    return decorator
