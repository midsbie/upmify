from __future__ import annotations

import importlib.resources as pkg_resources
import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def rebuild_asset_structure(temp_dir: Path, runtime_dir: Path) -> None:
    for sub in temp_dir.iterdir():
        pathname = sub / "pathname"
        if not pathname.is_file():
            log.debug("Skipping junk item: %s", sub)
            continue

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
