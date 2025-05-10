from __future__ import annotations

import importlib.resources as pkg_resources
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def write_package_json(
    pkg_dir: Path,
    name: str,
    display: str,
    dependencies: dict[str, str] = None,
    version="1.0.0",
    unity="2021.3",
) -> None:
    pkg_def = {
        "name": name,
        "displayName": display,
        "version": version,
        "unity": unity,
        "description": f"Wrapped version of {display}",
        "author": {"name": "AutoWrapped", "email": "noreply@example.com"},
    }

    if dependencies:
        pkg_def["dependencies"] = dependencies

    (pkg_dir / "package.json").write_text(json.dumps(pkg_def, indent=4))


def write_asmdef(runtime_dir: Path, name: str) -> None:
    asm = {
        "name": name,
        "references": [],
        "autoReferenced": True,
        "noEngineReferences": False,
    }
    (runtime_dir / f"{name}.asmdef").write_text(json.dumps(asm, indent=4))
