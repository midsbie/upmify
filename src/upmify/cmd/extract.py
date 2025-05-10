from __future__ import annotations

import importlib.resources as pkg_resources
import logging
import tarfile
from pathlib import Path
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
