#!/usr/bin/env python3
"""Preflight and execute same-root or cross-root moves without overwriting files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import tempfile
from pathlib import Path


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        temporary = handle.name
    os.replace(temporary, path)


def resolve_under(root: Path, value: str) -> Path:
    root = root.expanduser().resolve()
    path = Path(value)
    resolved = (path if path.is_absolute() else root / path).resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Path escapes root: {value}")
    return resolved


def load_plan(path: Path) -> tuple[Path, Path, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "root" in data:
        source_root = target_root = Path(data["root"]).expanduser().resolve()
    else:
        source_root = Path(data["source_root"]).expanduser().resolve()
        target_root = Path(data["target_root"]).expanduser().resolve()
    operations = data.get("moves", data.get("operations", []))
    if not isinstance(operations, list):
        raise ValueError("moves/operations must be a list")
    return source_root, target_root, operations


def preflight(source_root: Path, target_root: Path, operations: list[dict]) -> list[dict]:
    checked = []
    seen_targets = set()
    for number, item in enumerate(operations, 1):
        source = resolve_under(source_root, item["source"])
        target = resolve_under(target_root, item["target"])
        if source == target:
            raise ValueError(f"Operation {number}: source equals target")
        if target in seen_targets:
            raise ValueError(f"Operation {number}: repeated target: {target}")
        seen_targets.add(target)
        if not source.is_file():
            raise FileNotFoundError(f"Operation {number}: missing source: {source}")
        if target.exists():
            raise FileExistsError(f"Operation {number}: target exists: {target}")
        checked.append({"number": number, "source": str(source), "target": str(target)})
    return checked


def execute(
    checked: list[dict], log_path: Path | None, source_root: Path, target_root: Path
) -> dict:
    progress = {
        "started_at": dt.datetime.now().astimezone().isoformat(),
        "status": "in_progress",
        "source_root": str(source_root),
        "target_root": str(target_root),
        "moves": [],
    }
    if log_path:
        atomic_json(log_path, progress)
    for item in checked:
        source, target = Path(item["source"]), Path(item["target"])
        if not source.is_file() or target.exists():
            raise RuntimeError(f"State changed before operation {item['number']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        progress["moves"].append(item)
        if log_path:
            atomic_json(log_path, progress)
    progress["status"] = "complete"
    progress["finished_at"] = dt.datetime.now().astimezone().isoformat()
    if log_path:
        atomic_json(log_path, progress)
    return progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "plan", type=Path,
        help="JSON plan with root, or source_root + target_root, and moves/operations",
    )
    parser.add_argument("--execute", action="store_true", help="perform moves after preflight")
    parser.add_argument("--log", type=Path, help="write an atomic JSON progress log")
    args = parser.parse_args()

    source_root, target_root, operations = load_plan(args.plan)
    checked = preflight(source_root, target_root, operations)
    print(
        f"Preflight passed: {len(checked)} moves; "
        f"source_root={source_root}; target_root={target_root}"
    )
    if args.execute:
        progress = execute(checked, args.log, source_root, target_root)
        print(f"Completed: {len(progress['moves'])} moves")
    else:
        print("Dry run only; add --execute to move files")


if __name__ == "__main__":
    main()
