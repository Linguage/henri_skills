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
    "铁路与交通工程", "AI理论与基础模型", "AI Agent与智能体",
    "科技人文与数学", "AI工程与实践",
]

DEFAULT_CATEGORY_LABELS = {
    "铁路与交通工程": "铁路与交通工程",
    "AI理论与基础模型": "AI 理论与基础模型",
    "AI Agent与智能体": "AI Agent 与智能体",
    "科技人文与数学": "科技人文与数学",
    "AI工程与实践": "AI 工程与实践",
}

ACCEPTED_EXTS = {'.pdf', '.epub', '.mobi', '.azw3', '.docx'}

_EXT_LABEL = {'.epub': 'EPUB', '.mobi': 'MOBI', '.azw3': 'AZW3',
              '.docx': 'DOCX', '.pdf': 'PDF'}


def esc(s):
    """URL-encode path segments."""
    return quote(s, safe='/')


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
    """Return {category: [filename, ...]} for all supported files on disk."""
    disk = {}
    iter_order = cat_order if cat_order else sorted(os.listdir(books_dir))
    for cat in iter_order:
        if cat.startswith('.'):
            continue
        path = os.path.join(books_dir, cat)
        if not os.path.isdir(path):
            continue
        files = sorted([
            f for f in os.listdir(path)
            if not f.startswith('.') and any(f.lower().endswith(e) for e in ACCEPTED_EXTS)
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
    if "categories" not in inventory["_meta"] or not isinstance(inventory["_meta"]["categories"], list):
        inventory["_meta"]["categories"] = cat_order

    return inventory, new_files, missing_files


def build_markdown(inventory, cat_order, cat_labels):
    """Generate 书籍清单.md content from inventory data."""
    categories = inventory.get("categories", {})
    meta = inventory.get("_meta", {})
    today = meta.get("generated", datetime.date.today().isoformat())
    total = sum(len(v) for v in categories.values())

    lines = [
        "# 书籍与论文清单",
        "",
        f"> 自动生成于 {today}，共 {total} 篇文档，分 {len(categories)} 个目录。",
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
        lines.append(f"## {section_num}. {label}（{len(entries)} 篇）")
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
            link = f"[{ext}]({esc(cat)}/{esc(filename)})"
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
            links = " · ".join(f"[{f['ext']}]({quote(f['link'], safe='/')})" for f in files)
            lines.append(f"| {i} | {name} | {issues} | {links} |")
        lines.append("")

    lines.append("---")
    lines.append(f"*共 {total} 篇，{len([c for c in cat_order if c in categories])} 个目录。*")
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
        books_dir = os.path.join(os.getcwd(), "书籍")
        if not os.path.isdir(books_dir):
            fallback = os.path.join(SCRIPT_DIR.parent.parent.parent, "书籍")
            if os.path.isdir(fallback):
                books_dir = fallback

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

    cat_order = meta.get("categories", DEFAULT_CATEGORY_ORDER)
    cat_labels = meta.get("category_labels", DEFAULT_CATEGORY_LABELS)

    disk = scan_disk(books_dir, cat_order)
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
