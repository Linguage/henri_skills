#!/usr/bin/env python3
"""
Generate 书籍清单.md from inventory.json (the single source of truth).

Usage:
    python3 update_inventory.py [--books-dir PATH] [--dry-run]
"""

import json, os, sys, datetime, tempfile, argparse
from pathlib import Path
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_CATEGORY_ORDER = [
    "数学与物理", "思想与人文", "铁路与交通工程",
    "AI工程与实践", "计算机科学与软件工程", "金融与商业",
]

DEFAULT_CATEGORY_LABELS = {
    "数学与物理": "数学与物理",
    "思想与人文": "思想与人文",
    "铁路与交通工程": "铁路与交通工程",
    "AI工程与实践": "AI 工程与实践",
    "计算机科学与软件工程": "计算机科学与软件工程",
    "金融与商业": "金融与商业",
}

ACCEPTED_EXTS = {'.pdf', '.epub', '.mobi', '.azw3', '.docx', '.djvu'}

_EXT_LABEL = {'.epub': 'EPUB', '.mobi': 'MOBI', '.azw3': 'AZW3',
              '.docx': 'DOCX', '.pdf': 'PDF', '.djvu': 'DJVU'}


def esc(s):
    """URL-encode path segments."""
    return quote(s, safe='/')


def md_link(label, rel_path):
    """生成 Markdown 链接，保留中文可读（仅在特殊字符时用 <...> 包裹）。

    - 不做 URL 编码，让链接保持中文可读
    - 含空格/括号等特殊字符时，用 <...> 包裹避免 Markdown 解析问题
    """
    if any(c in rel_path for c in (' ', '(', ')', '<', '>', '[', ']', '`', '\\')):
        return f"[{label}](<{rel_path}>)"
    return f"[{label}]({rel_path})"


def atomic_write(path, content):
    """Write file atomically via tmp + replace."""
    d = os.path.dirname(path) or '.'
    suffix = '.tmp'
    with tempfile.NamedTemporaryFile(mode='w', dir=d, delete=False,
                                     encoding='utf-8', suffix=suffix) as tf:
        tf.write(content)
        tmp = tf.name
    os.replace(tmp, path)


def scan_disk(books_dir, cat_order=None):
    """递归发现图书类别，并返回 {相对目录: [文件名, ...]}。

    `杂志/`、重复与归档审核目录是独立管理维度，不纳入图书 inventory。
    每个含受支持文件的目录都是一个类别，因此可处理 `人物/姓名`、
    `大文件/主题` 等多级目录。
    """
    excluded_roots = {"杂志", "待确认重复", "重复", "已归档"}
    discovered = []
    for dirpath, dirnames, filenames in os.walk(books_dir):
        rel = os.path.relpath(dirpath, books_dir)
        if rel == ".":
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in excluded_roots
            ]
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if any(
            not f.startswith(".") and Path(f).suffix.lower() in ACCEPTED_EXTS
            for f in filenames
        ):
            discovered.append(rel)

    iter_order = list(cat_order or [])
    for cat in sorted(discovered):
        if cat not in iter_order:
            iter_order.append(cat)

    disk = {}
    for cat in iter_order:
        if cat.startswith('.'):
            continue
        path = os.path.join(books_dir, cat)
        if not os.path.isdir(path):
            continue
        files = sorted([
            f for f in os.listdir(path)
            if not f.startswith('.') and Path(f).suffix.lower() in ACCEPTED_EXTS
        ])
        disk[cat] = files
    return disk


def reconcile(inventory, disk, books_dir, cat_order):
    """Reconcile inventory.json with files on disk."""
    new_files = []
    missing_files = []
    today = datetime.date.today().isoformat()

    categories = inventory.setdefault("categories", {})

    for cat in cat_order:
        if cat not in categories:
            categories[cat] = []

        json_files = {e["filename"] for e in categories[cat]}
        disk_files = set(disk.get(cat, []))

        for f in sorted(disk_files - json_files):
            full_path = os.path.join(books_dir, cat, f)
            mtime = os.path.getmtime(full_path)
            dl_date = datetime.date.fromtimestamp(mtime).isoformat()
            entry = {
                "filename": f, "cn_title": "", "author": "",
                "added_date": dl_date, "notes": ""
            }
            categories[cat].append(entry)
            new_files.append((cat, f))

        for f in sorted(json_files - disk_files):
            missing_files.append((cat, f))

        categories[cat].sort(key=lambda e: e["filename"])

    total = sum(len(v) for v in categories.values())
    if "_meta" not in inventory:
        inventory["_meta"] = {}
    inventory["_meta"]["generated"] = today
    inventory["_meta"]["total_docs"] = total
    inventory["_meta"]["categories"] = cat_order
    inventory["_meta"]["total_categories"] = len(categories)

    return inventory, new_files, missing_files


def build_markdown(inventory, cat_order, cat_labels):
    """Generate 书籍清单.md content from inventory data."""
    categories = inventory.get("categories", {})
    meta = inventory.get("_meta", {})
    today = meta.get("generated", datetime.date.today().isoformat())
    total = sum(len(v) for v in categories.values())

    lines = [
        "# 书籍清单",
        "",
        f"> 自动生成于 {today}，共 {total} 本图书，分 {len(categories)} 个目录。",
        "",
        "---",
        "",
    ]

    section_num = 0
    for cat in cat_order:
        entries = categories.get(cat, [])
        if not entries:
            continue
        label = cat_labels.get(cat, cat)
        section_num += 1
        lines.append(f"## {section_num}. {label}（{len(entries)} 本）")
        lines.append("")
        lines.append("| # | 标题 | 作者 | 文件 |")
        lines.append("|---|------|------|------|")

        for i, entry in enumerate(entries, 1):
            cn_title = entry.get("cn_title", "") or "—"
            if len(cn_title) > 60:
                cn_title = cn_title[:57] + "..."
            author = entry.get("author", "") or "—"
            filename = entry["filename"]
            ext = _EXT_LABEL.get(Path(filename).suffix.lower(), 'FILE')
            link = md_link(ext, f"{cat}/{filename}")
            cn_title = cn_title.replace("|", "/").replace("\n", " ").replace("\r", " ")
            author = author.replace("|", "/").replace("\n", " ").replace("\r", " ")
            lines.append(f"| {i} | {cn_title} | {author} | {link} |")
        lines.append("")

    # Magazine section from inventory.json magazines field
    magazines = meta.get("magazines", {})
    if magazines:
        section_num += 1
        lines.append(f"## {section_num}. 杂志（{magazines.get('count', '?')} 种）")
        lines.append("")
        lines.append("| # | 期刊名 | 期数 | 文件 |")
        lines.append("|---|--------|------|------|")
        for i, entry in enumerate(magazines.get("entries", []), 1):
            name = entry.get("name", "")
            issues = entry.get("issues", "")
            files = entry.get("files", [])
            links = " · ".join(md_link(f['ext'], f['link']) for f in files)
            lines.append(f"| {i} | {name} | {issues} | {links} |")
        lines.append("")

    lines.append("---")
    lines.append(f"*共 {total} 本图书，{len([c for c in cat_order if c in categories])} 个目录。*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Update 书籍清单.md from inventory.json')
    parser.add_argument('--books-dir', help='Path to 书籍/ directory')
    parser.add_argument('--dry-run', action='store_true', help='Print without writing files')
    args = parser.parse_args()

    if args.books_dir:
        books_dir = args.books_dir
    else:
        cwd = Path.cwd()
        candidates = []
        if cwd.name == "书籍":
            candidates.append(cwd)
        candidates.extend([
            Path.home() / "Documents" / "书籍",
            cwd / "书籍",  # 兼容旧用法与用户指定的工作根目录
        ])
        books_dir = str(next((p for p in candidates if p.is_dir()), candidates[0]))

    if not os.path.isdir(books_dir):
        print(f"ERROR: books directory not found: {books_dir}")
        sys.exit(1)

    inventory_file = os.path.join(books_dir, "inventory.json")
    if not os.path.exists(inventory_file):
        print(f"ERROR: {inventory_file} not found. Run the initializer first.")
        sys.exit(1)

    with open(inventory_file, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    meta = inventory.setdefault("_meta", {})

    cat_order = list(meta.get("categories", DEFAULT_CATEGORY_ORDER))
    for cat in inventory.get("categories", {}):
        if cat not in cat_order:
            cat_order.append(cat)
    cat_labels = meta.get("category_labels", DEFAULT_CATEGORY_LABELS)

    disk = scan_disk(books_dir, cat_order)
    for cat in disk:
        if cat not in cat_order:
            cat_order.append(cat)
    inventory, new_files, missing_files = reconcile(inventory, disk, books_dir, cat_order)

    md_content = build_markdown(inventory, cat_order, cat_labels)
    md_path = os.path.join(books_dir, "书籍清单.md")

    if args.dry_run:
        print(f"[DRY-RUN] Would write {md_path}")
        print(md_content[:500] + "...")
        return

    atomic_write(inventory_file, json.dumps(inventory, ensure_ascii=False, indent=2))
    atomic_write(md_path, md_content)

    total = inventory["_meta"]["total_docs"]
    print(f"Generated {md_path}")
    print(f"Categories: {len(inventory['categories'])}, Total: {total} docs")

    if new_files:
        print(f"\n--- NEW FILES (stubs added to inventory.json, please fill metadata) ---")
        for cat, f in new_files:
            print(f"  [{cat}] {f}")

    if missing_files:
        print(f"\n--- MISSING ON DISK (in JSON but file not found) ---")
        for cat, f in missing_files:
            print(f"  [{cat}] {f}")

    missing_meta = []
    for cat, entries in inventory["categories"].items():
        for e in entries:
            if not e.get("cn_title") or not e.get("author"):
                missing_meta.append((cat, e["filename"]))
    if missing_meta:
        print(f"\n--- INCOMPLETE METADATA ({len(missing_meta)} entries need cn_title/author) ---")
        for cat, f in missing_meta:
            print(f"  [{cat}] {f}")

    if not new_files and not missing_files and not missing_meta:
        print("All files synced, all metadata complete.")


if __name__ == "__main__":
    main()
