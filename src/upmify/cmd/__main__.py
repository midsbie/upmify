#!/usr/bin/env python3
"""
Convert a .unitypackage to a UPM-style package.

Usage:
    python -m upmify.cmd \
        MyAsset.unitypackage \
        --output-dir ./out \
        --package-name com.mycompany.myasset \
        --display-name "My Asset" \
        --assembly-name MyCompany.MyAsset \
        [--package-version 1.0.0] \
        [--unity-version 2021.3] \
        [--git-init] \
        [--lfs] \
        [--force] \
        [--verbose | --quiet]

Arguments:
    unitypackage            Path to the .unitypackage file to convert

Options:
    -o, --output-dir        Destination directory for the generated UPM package
    -p, --package-name      UPM-style package name (e.g., com.mycompany.myasset)
    -d, --display-name      Human-readable name for the package
    -a, --assembly-name     C# assembly name for the .asmdef file
    --package-version       Version string for the UPM package (default: 1.0.0)
    --unity-version         Minimum required Unity version (default: 2021.3)
    -g, --git-init          Initialize a git repository in the package
    --lfs                   Enable Git LFS support if --git-init is used
    -f, --force             Overwrite output directory if it exists
    -v, --verbose           Enable detailed logging
    -q, --quiet             Suppress most output
"""

from __future__ import annotations

import argparse
import importlib.resources as pkg_resources
import logging
import re
from pathlib import Path

from .convert import convert

log = logging.getLogger(__name__)


def validate_assembly_name(name: str) -> str:
    identifier_re = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    parts = name.split(".")
    for part in parts:
        if not identifier_re.match(part):
            raise argparse.ArgumentTypeError(
                f"Invalid assembly name: '{name}'. "
                "Each part must be a valid C# identifier "
                f"(got invalid segment: '{part}')"
            )
    return name


def main():
    p = argparse.ArgumentParser(
        description="Wrap a .unitypackage as a Unity UPM package",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument("unitypackage", type=Path, help="Path to the .unitypackage")
    p.add_argument(
        "--output-dir", "-o", required=True, type=Path, help="Destination directory"
    )
    p.add_argument(
        "--package-name", "-p", required=True, help="UPM name, e.g. com.myco.asset"
    )
    p.add_argument(
        "--display-name", "-d", required=True, help="Human-readable display name"
    )
    p.add_argument(
        "--assembly-name",
        "-a",
        type=validate_assembly_name,
        required=True,
        help="Name for the generated .asmdef file (must be a valid C# assembly name)",
    )

    p.add_argument(
        "--git-init",
        "-g",
        action="store_true",
        help=(
            "Initialise a git repository in the generated package and commit the result"
        ),
    )
    p.add_argument(
        "--lfs",
        action="store_true",
        help="After --git-init, copy .gitattributes and run 'git lfs install --local'",
    )

    p.add_argument(
        "--package-version",
        default="1.0.0",
        help="Version of the package",
    )
    p.add_argument(
        "--unity-version",
        default="6000.0",
        help="Minimum required Unity version",
    )

    p.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Delete the output package directory if it already exists",
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
        args.assembly_name,
        git_init=args.git_init,
        use_lfs=args.lfs,
        force=args.force,
        package_version=args.package_version,
        unity_version=args.unity_version,
    )


if __name__ == "__main__":
    main()
