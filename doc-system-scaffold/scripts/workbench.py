"""Generate a project-workbench index and publish progress events."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4

ID = re.compile(r"[A-Za-z0-9_-]{1,80}")
SECTIONS = {"specs", "jobs", "legacy", "reports", "work-notes", "theory"}


def identifier(value):
    if not ID.fullmatch(value):
        raise argparse.ArgumentTypeError("标识限用字母、数字、下划线或连字符，最多 80 个字符。")
    return value


def text(value, limit):
    if not value.strip() or len(value) > limit:
        raise ValueError(f"文字应包含 1 到 {limit} 个字符。")
    return value


def relative(value):
    return "\\" not in value and "\x00" not in value and all(
        part not in {"", ".", ".."} for part in value.split("/")
    )


def publish(path, value):
    """Publish a complete new file, leaving any existing record in place."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".pending-", dir=path.parent,
                                     delete=False) as stream:
        stage = Path(stream.name)
        try:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            os.link(stage, path)
        finally:
            stage.unlink()


def directory(path):
    if path.is_symlink():
        raise ValueError(f"工作台的记录目录不能为符号链接：{path}")
    path.mkdir(mode=0o700, exist_ok=True)


def read_index(path):
    if path.is_symlink():
        raise ValueError("workbench.json 不能为符号链接。")
    index = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(index, dict) or index.get("schemaVersion") != 1:
        raise ValueError("管理目录索引版本无效。")
    return index


def initialize(args, root):
    root.mkdir(parents=True, exist_ok=True)
    index = {"schemaVersion": 1, "title": text(args.title, 200), "projects": []}
    ids = set()
    if len(args.project) > 300:
        raise ValueError("最多可登记 300 个项目。")
    for project_id, title, path in args.project:
        identifier(project_id)
        if project_id in ids or (path != "." and not relative(path)):
            raise ValueError("项目标识重复或给出的项目路径无效。")
        ids.add(project_id)
        index["projects"].append({"id": project_id, "title": text(title, 200), "path": path})
    target = root / "workbench.json"
    try:
        publish(target, index)
    except FileExistsError:
        if read_index(target) != index:
            raise ValueError(f"已存在的索引内容不同。请先核对：{target}") from None
    print(target)


def record(args, root):
    index = read_index(root / "workbench.json")
    if args.project and args.project not in {project["id"] for project in index.get("projects", [])}:
        raise ValueError("事件所引用的项目尚未登记。")
    if args.status in {"verified", "completed"} and not args.evidence:
        raise ValueError("验证或完成状态需要附上实际证据。")
    event = {
        "id": args.event_id or uuid4().hex, "task": args.task, "status": args.status,
        "title": text(args.title, 200), "agent": text(args.agent, 120),
        "summary": text(args.summary, 4000),
    }
    if args.project:
        event["project"] = args.project
    if args.next:
        event["next"] = text(args.next, 4000)
    if args.document:
        parts = args.document.split("/")
        permitted = args.document.lower() == "readme.md" or parts[0] in SECTIONS
        if (not relative(args.document) or not args.document.lower().endswith(".md") or
                not permitted or any(part.startswith(".") for part in parts)):
            raise ValueError("请使用管理目录内的 Markdown 文档相对路径。")
        event["document"] = args.document
    if args.evidence:
        if len(args.evidence) > 20:
            raise ValueError("单条进展最多附上 20 条证据。")
        event["evidence"] = [text(item, 1000) for item in args.evidence]
    staging = root / ".workbench"
    directory(staging)
    directory(staging / "events")
    target = staging / "events" / (event["id"] + ".json")
    event["at"] = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    try:
        publish(target, event)
    except FileExistsError:
        if target.is_symlink():
            raise ValueError("事件不能通过符号链接读取。") from None
        existing = json.loads(target.read_text(encoding="utf-8"))
        event["at"] = existing.get("at")
        if existing != event:
            raise ValueError(f"事件标识已使用，且内容不同：{args.event_id}") from None
    print(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("directory", type=Path)
    init.add_argument("--title", required=True)
    init.add_argument("--project", nargs=3, action="append", default=[], metavar=("ID", "TITLE", "PATH"))
    add = commands.add_parser("record")
    add.add_argument("directory", type=Path)
    add.add_argument("--task", type=identifier, required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--agent", required=True)
    add.add_argument("--status", required=True,
                     choices=("running", "blocked", "review", "verified", "completed", "interrupted"))
    add.add_argument("--summary", required=True)
    add.add_argument("--event-id", type=identifier)
    add.add_argument("--project", type=identifier)
    add.add_argument("--next")
    add.add_argument("--document")
    add.add_argument("--evidence", action="append")
    args = parser.parse_args()
    try:
        (initialize if args.command == "init" else record)(args, args.directory.expanduser().resolve())
    except (argparse.ArgumentTypeError, OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
