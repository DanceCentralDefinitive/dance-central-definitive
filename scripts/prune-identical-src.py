#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Delete files from src that are identical to the matching file in orig, "
            "then prune empty parent directories back up to src."
        )
    )
    parser.add_argument(
        "--src",
        default="src",
        type=Path,
        help="Source tree to prune (default: src)",
    )
    parser.add_argument(
        "--orig",
        default="orig",
        type=Path,
        help="Reference tree to compare against (default: orig)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without changing anything.",
    )
    return parser.parse_args()


def prune_empty_parents(path: Path, stop_at: Path, dry_run: bool) -> int:
    removed = 0
    current = path.parent

    while current != stop_at and stop_at in current.parents:
        if current.exists() and current.is_dir() and not any(current.iterdir()):
            if dry_run:
                print(f"DRY-RUN remove empty dir: {current}")
            else:
                os.rmdir(current)
            removed += 1
            current = current.parent
            continue
        break

    return removed


def main() -> int:
    args = parse_args()
    src_root = args.src.resolve()
    orig_root = args.orig.resolve()

    if not src_root.is_dir():
        raise FileNotFoundError(f"Missing src directory: {src_root}")
    if not orig_root.is_dir():
        raise FileNotFoundError(f"Missing orig directory: {orig_root}")

    removed_files = 0
    removed_dirs = 0
    skipped = 0

    for src_file in sorted(src_root.rglob("*")):
        if not src_file.is_file():
            continue

        rel_path = src_file.relative_to(src_root)
        orig_file = orig_root / rel_path

        if not orig_file.is_file():
            skipped += 1
            continue

        if not filecmp.cmp(src_file, orig_file, shallow=False):
            skipped += 1
            continue

        if args.dry_run:
            print(f"DRY-RUN delete file: {src_file}")
        else:
            src_file.unlink()

        removed_files += 1
        removed_dirs += prune_empty_parents(src_file, src_root, args.dry_run)

    print(f"Removed files: {removed_files}")
    print(f"Removed empty dirs: {removed_dirs}")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())