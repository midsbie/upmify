#!/usr/bin/env python3
"""
Convert a .unitypackage to a UPM-style package.

Usage:
    python -m upmify.cmd \
        MyAsset.unitypackage \
        ./out \
        com.mycompany.myasset \
        "My Asset"
"""

from __future__ import annotations

import argparse
import importlib.resources as pkg_resources
import json
import logging
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

log = logging.getLogger(__name__)


def _safe_members(tar: tarfile.TarFile) -> Iterable[tarfile.TarInfo]:
    """Yield members while blocking any path-traversal attempt (CVE-2022-2590 family)."""
    for member in tar.getmembers():
        member_path = Path(member.name)
        if ".." in member_path.parts:
            log.warning("Skipping suspicious entry %s", member.name)
            continue
        yield member


def extract_unitypackage(src: Path, dest: Path) -> None:
    with tarfile.open(src) as tar:
        tar.extractall(dest, members=_safe_members(tar))


def rebuild_asset_structure(temp_dir: Path, runtime_dir: Path) -> None:
    for sub in temp_dir.iterdir():
        pathname = sub / "pathname"
        if not pathname.is_file():
            log.debug("Skipping junk folder: %s", sub)
            continue  # skip junk folders

        with pathname.open("rb") as f:
            raw = f.read()

        # Split at the first newline or NUL and decode just that part
        relative = raw.split(b"\n", 1)[0].split(b"\x00", 1)[0].decode("utf-8", "ignore")

        dest_path = runtime_dir / relative
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        asset_file = sub / "asset"
        meta_file = sub / "asset.meta"

        if asset_file.is_file():  # regular asset
            log.debug("Copying asset: %s -> %s", asset_file, dest_path)
            shutil.copy2(asset_file, dest_path)
        elif meta_file.is_file():  # folder asset
            log.debug("Creating folder: %s", dest_path)
            dest_path.mkdir(exist_ok=True)
        else:  # nothing useful
            log.debug("Skipping empty entry: %s", sub)
            continue

        # copy the .meta if we have one (works for both kinds above)
        if not meta_file.is_file():
            log.warning("No .meta for %s", asset_file)
            continue

        shutil.copy2(meta_file, dest_path.with_suffix(dest_path.suffix + ".meta"))


def write_package_json(
    pkg_dir: Path, name: str, display: str, version="1.0.0", unity="2021.3"
) -> None:
    pkg_def = {
        "name": name,
        "displayName": display,
        "version": version,
        "unity": unity,
        "description": f"Wrapped version of {display}",
        "author": {"name": "AutoWrapped", "email": "noreply@example.com"},
    }
    (pkg_dir / "package.json").write_text(json.dumps(pkg_def, indent=4))


def write_asmdef(runtime_dir: Path, name: str) -> None:
    asm = {
        "name": name,
        "references": [],
        "autoReferenced": True,
        "noEngineReferences": False,
    }
    (runtime_dir / f"{name}.asmdef").write_text(json.dumps(asm, indent=4))


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


def convert(
    unitypackage: Path,
    output_dir: Path,
    package_name: str,
    display_name: str,
    git_init: bool = False,
    use_lfs: bool = False,
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    pkg_dir = output_dir / package_name
    runtime_dir = pkg_dir / "Runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    log.info("Extracting %s...", unitypackage)
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        extract_unitypackage(unitypackage, tmp_path)

        log.info("Rebuilding asset tree...")
        rebuild_asset_structure(tmp_path, runtime_dir)

    log.info("Writing package.json and asmdef...")
    write_package_json(pkg_dir, package_name, display_name)
    write_asmdef(runtime_dir, display_name.replace(" ", ""))

    if git_init:
        init_git_repo(pkg_dir, display_name, use_lfs=use_lfs)

    log.info("Done. Package written to %s", pkg_dir)


def main():
    p = argparse.ArgumentParser(
        description="Wrap a .unitypackage as a Unity UPM package"
    )
    p.add_argument("unitypackage", type=Path, help="Path to the .unitypackage")
    p.add_argument("output_dir", type=Path, help="Destination directory")
    p.add_argument("package_name", help="UPM name, e.g. com.myco.asset")
    p.add_argument("display_name", help="Human-readable display name")
    p.add_argument(
        "--git-init",
        "-g",
        action="store_true",
        help="Initialise a git repository in the generated package and commit the result",
    )
    p.add_argument(
        "--lfs",
        action="store_true",
        help="After --git-init, copy .gitattributes and run 'git lfs install --local'",
    )

    verbosity = p.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--verbose", "-v", action="store_true", help="Enable detailed logging"
    )
    verbosity.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress most output"
    )

    args = p.parse_args()

    # Configure logging level
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    convert(
        args.unitypackage,
        args.output_dir,
        args.package_name,
        args.display_name,
        git_init=args.git_init,
        use_lfs=args.lfs,
    )


if __name__ == "__main__":
    main()
