from __future__ import annotations

import importlib.resources as pkg_resources
import logging
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def _copy_template_file(package: str, resource_name: str, dest: Path) -> None:
    try:
        with pkg_resources.files(package).joinpath(resource_name).open("rb") as fsrc:
            with dest.open("wb") as fdst:
                shutil.copyfileobj(fsrc, fdst)
    except FileNotFoundError:
        log.warning("Template %s not found in package %s", resource_name, package)


def init_git_repo(pkg_dir: Path, display_name: str, *, use_lfs: bool = False) -> None:
    if (pkg_dir / ".git").is_dir():
        log.debug("Git repo already present, skipping git init")
        return

    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        log.warning("Git executable not found – skipping repository initialisation")
        return

    log.info("Initialising git repository…")
    subprocess.run(["git", "init"], cwd=pkg_dir, check=True)

    _copy_template_file("upmify.templates", ".gitignore", pkg_dir / ".gitignore")

    if use_lfs:
        _copy_template_file(
            "upmify.templates", ".gitattributes", pkg_dir / ".gitattributes"
        )
        try:
            subprocess.run(
                ["git", "lfs", "install", "--local"], cwd=pkg_dir, check=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            log.warning("Git-LFS is not available – continuing without it")

    subprocess.run(["git", "add", "-A"], cwd=pkg_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Add initial UPM package for {display_name}"],
        cwd=pkg_dir,
        check=True,
    )
