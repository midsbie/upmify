from __future__ import annotations

import argparse
import importlib.resources as pkg_resources
import json
import logging
import re
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from .extract import extract_unitypackage
from .structure import rebuild_asset_structure
from .package import write_package_json, write_asmdef
from .git import init_git_repo

log = logging.getLogger(__name__)


def convert(
    unitypackage: Path,
    output_dir: Path,
    package_name: str,
    display_name: str,
    assembly_name: str,
    git_init: bool = False,
    use_lfs: bool = False,
    force: bool = False,
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    pkg_dir = output_dir / package_name

    if pkg_dir.exists():
        if not force:
            log.error(
                "Package directory already exists: %s (use --force to overwrite)",
                pkg_dir,
            )
            raise SystemExit(1)
        log.info("Overwriting existing package directory: %s", pkg_dir)
        shutil.rmtree(pkg_dir)

    runtime_dir = pkg_dir / "Runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    log.info("Extracting %s...", unitypackage)
    dependencies = {}
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        extract_unitypackage(unitypackage, tmp_path)

        log.info("Rebuilding asset tree...")
        dependencies = rebuild_asset_structure(tmp_path, runtime_dir)

    log.info("Writing package.json and asmdef...")
    write_package_json(pkg_dir, package_name, display_name, dependencies=dependencies)
    write_asmdef(runtime_dir, assembly_name)

    if git_init:
        init_git_repo(pkg_dir, display_name, use_lfs=use_lfs)

    log.info("Done. Package written to %s", pkg_dir)
