#!/usr/bin/env python3
"""
Generate 书籍清单.md from inventory.json (the single source of truth).

Usage:
    python3 update_inventory.py [--books-dir PATH]

Workflow:
1. Loads inventory.json — the master database of all book metadata
2. Scans the 书籍/ subdirectories on disk
3. Reconciles: detects new files (adds stubs to JSON) and missing files (reports them)
4. Generates 书籍/书籍清单.md from the reconciled data

To edit metadata (cn_title, author, notes, etc.), edit inventory.json directly,
then re-run this script. The MD is always generated from the JSON, never the reverse.
"""

import json, os, sys, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

CATEGORY_LABELS = {
    "铁路与交通工程": "1. 铁路与交通工程",
    "AI理论与基础模型": "2. AI 理论与基础模型",
    "AI Agent与智能体": "3. AI Agent 与智能体",
    "科技人文与数学": "4. 科技人文与数学",
    "AI工程与实践": "5. AI 工程与实践",
}

CATEGORY_ORDER = list(CATEGORY_LABELS.keys())

MAGAZINE_SECTION = """## 6. 杂志（17 种，32 期）

| # | 期刊名 | 期数 | 文件 |
|---|--------|------|------|
| 1 | Apple Magazine | 1 期 (Issue 756, 2026-04-24) | [PDF](杂志/Apple%20Magazine/AppleMagazine_-_Issue_756%2C_24_April_2026.pdf) |
| 2 | Barron's | 5 期 (2026-04-06 / 04-13 / 04-20 / 04-27 / 05-04) | [PDF](杂志/Barron%27s/Barron%27s_Magazine_-_April_06%2C_2026.pdf) · [PDF](杂志/Barron%27s/Barron%27s_Magazine_-_April_13%2C_2026.pdf) · [PDF](杂志/Barron%27s/Barron%27s_Magazine_-_April_20%2C_2026.pdf) · [PDF](杂志/Barron%27s/Barrons_-_April_27%2C_2026.pdf) · [PDF](杂志/Barron%27s/Barron%27s_Magazine_-_May_4%2C_2026.pdf) |
| 3 | The Atlantic | 3 期 (2026-03 / 2026-04 / 2026-05) | [EPUB](杂志/The%20Atlantic/Atlantic_2026.03.02.epub) · [EPUB](杂志/The%20Atlantic/Atlantic_2026.04.02.epub) · [EPUB](杂志/The%20Atlantic/Atlantic_2026.05.02.epub) |
| 4 | Discover | 1 期 (Spring 2026) | [PDF](杂志/Discover/Discover_-_Spring_2026.pdf) |
| 5 | MIT Technology Review | 1 期 (May/June 2026) | [PDF](杂志/MIT%20Technology%20Review/MIT_Technology_Review_-_MayJune_2026.pdf) |
| 6 | National Geographic | 1 期 (May 2026) | [PDF](杂志/National%20Geographic/National_Geographic_Magazine_-_May_2026_-_En.pdf) |
| 7 | New Scientist | 1 期 (2026-04-25) | [PDF](杂志/New%20Scientist/New_Scientist_USA_-_April_25%2C_2026.pdf) |
| 8 | The New Yorker | 5 期 (2026-04-06 / 04-13 / 04-20 / 04-27 / 05-04) | [EPUB](杂志/The%20New%20Yorker/new_yorker.2026.04.06.epub) · [EPUB](杂志/The%20New%20Yorker/new_yorker.2026.04.13.epub) · [EPUB](杂志/The%20New%20Yorker/new_yorker.2026.04.20.epub) · [EPUB](杂志/The%20New%20Yorker/new_yorker.2026.04.27.epub) · [EPUB](杂志/The%20New%20Yorker/new_yorker.2026.05.04.epub) |
| 9 | Newsweek | 1 期 (2026-05-01) | [PDF](杂志/Newsweek/Newsweek_US_-_May_1st_2026_%282026-04-24%29.pdf) |
| 10 | Science | 1 期 (Vol.392, 2026-04-23) | [PDF](杂志/Science/Science_-_Issue_6796_Volume_392%2C_April_23%2C_2026.pdf) |
| 11 | New York Times Book Review | 2 期 (2026-03-22 / 2026-04-05) | [PDF](杂志/New%20York%20Times%20Book%20Review/The_New_York_Times_Book_Review_-_March_22%2C_2026.pdf) · [PDF](杂志/New%20York%20Times%20Book%20Review/The_New_York_Times_Book_Review_-_April_05%2C_2026.pdf) |
| 12 | Wall Street Journal Magazine | 1 期 (April 2026) | [PDF](杂志/Wall%20Street%20Journal%20Magazine/The_Wall_Street_Journal_Magazine_-_April_2026.pdf) |
| 13 | The Economist | 6 期 (2026-03-21 / 04-04 / 04-11 / 04-18 / 04-25 / 05-02) | [EPUB](杂志/The%20Economist/TheEconomist.2026.03.21.epub) · [EPUB](杂志/The%20Economist/TheEconomist.2026.04.04.epub) · [EPUB](杂志/The%20Economist/TheEconomist.2026.04.11.epub) · [EPUB](杂志/The%20Economist/TheEconomist.2026.04.18.epub) · [EPUB](杂志/The%20Economist/TheEconomist.2026.04.25.epub) · [EPUB](杂志/The%20Economist/TheEconomist.2026.05.02.epub) |
| 14 | Wired | 3 期 (2026-03 / 2026-04 / 2026-05) | [EPUB](杂志/Wired/wired_2026.03.02.epub) · [EPUB](杂志/Wired/wired_2026.04.02.epub) · [EPUB](杂志/Wired/wired_2026.05.02.epub) |
| 15 | Time | 1 期 (2026-05-11) | [PDF](杂志/Time/Time_USA_-_May_11%2C_2026.pdf) |
| 16 | The Paris Review | 1 期 (Spring 2025) | [PDF](杂志/The%20Paris%20Review/The_Paris_Review_Spring_2025_freemagazines_top.pdf) |
| 17 | Linux Complete Manual | 1 期 (Spring 2026) | [PDF](杂志/Linux%20Complete%20Manual/Linux_Complete_Manual_-_Spring_2026.pdf) |
"""


def esc(s):
    """URL-encode spaces in a path segment."""
    return s.replace(" ", "%20")


def scan_disk(books_dir):
    """Return {category: [filename, ...]} for PDF/EPUB files on disk."""
    disk = {}
    for cat in CATEGORY_ORDER:
        path = os.path.join(books_dir, cat)
        if not os.path.isdir(path):
            disk[cat] = []
            continue
        files = sorted([
            f for f in os.listdir(path)
            if not f.startswith('.') and (f.lower().endswith('.pdf') or f.lower().endswith('.epub'))
        ])
        disk[cat] = files
    return disk


def reconcile(inventory, disk, books_dir):
    """Reconcile inventory.json with files on disk.

    - New files on disk not in JSON → add stub entry with today's date
    - Files in JSON but not on disk → report as missing (keep in JSON)
    Returns (updated_inventory, new_files, missing_files).
    """
    new_files = []
    missing_files = []
    today = datetime.date.today().isoformat()

    categories = inventory.setdefault("categories", {})

    for cat in CATEGORY_ORDER:
        if cat not in categories:
            categories[cat] = []

        json_files = {e["filename"] for e in categories[cat]}
        disk_files = set(disk.get(cat, []))

        # Files on disk but not in JSON → add stub
        for f in sorted(disk_files - json_files):
            full_path = os.path.join(books_dir, cat, f)
            mtime = os.path.getmtime(full_path)
            dl_date = datetime.date.fromtimestamp(mtime).isoformat()
            entry = {
                "filename": f,
                "cn_title": "",
                "author": "",
                "added_date": dl_date,
                "notes": ""
            }
            categories[cat].append(entry)
            new_files.append((cat, f))

        # Files in JSON but not on disk
        for f in sorted(json_files - disk_files):
            missing_files.append((cat, f))

        # Re-sort entries by filename
        categories[cat].sort(key=lambda e: e["filename"])

    # Update meta
    total = sum(len(v) for v in categories.values())
    if "_meta" not in inventory:
        inventory["_meta"] = {}
    inventory["_meta"]["generated"] = today
    inventory["_meta"]["total_docs"] = total

    return inventory, new_files, missing_files


def build_markdown(inventory):
    """Generate 书籍清单.md content from inventory data."""
    categories = inventory.get("categories", {})
    today = inventory.get("_meta", {}).get("generated", datetime.date.today().isoformat())
    total = sum(len(v) for v in categories.values())

    lines = [
        "# 书籍与论文清单\n",
        f"> 自动生成于 {today}，共 {total} 篇文档，分 {len(categories)} 个主题类别（另含 17 种杂志共 32 期）。\n",
        "---\n",
    ]

    for cat in CATEGORY_ORDER:
        entries = categories.get(cat, [])
        label = CATEGORY_LABELS.get(cat, cat)
        lines.append(f"## {label}（{len(entries)} 篇）\n")
        lines.append("| # | 中文译名 | 原标题 / 作者 | 文件 |")
        lines.append("|---|---------|-------------|------|")

        for i, entry in enumerate(entries, 1):
            cn_title = entry.get("cn_title", "") or "—"
            author = entry.get("author", "") or "—"
            filename = entry["filename"]
            ext = "EPUB" if filename.lower().endswith('.epub') else "PDF"
            link = f"[{ext}]({esc(cat)}/{esc(filename)})"
            lines.append(f"| {i} | {cn_title} | {author} | {link} |")

        lines.append("")

    lines.append("---\n")
    lines.append(MAGAZINE_SECTION)
    return "\n".join(lines)


def main():
    if "--books-dir" in sys.argv:
        idx = sys.argv.index("--books-dir")
        books_dir = sys.argv[idx + 1]
    else:
        books_dir = os.path.join(os.getcwd(), "书籍")
        if not os.path.isdir(books_dir):
            fallback = os.path.join(SCRIPT_DIR.parent.parent.parent, "书籍")
            if os.path.isdir(fallback):
                books_dir = fallback

    if not os.path.isdir(books_dir):
        print(f"ERROR: books directory not found: {books_dir}")
        sys.exit(1)

    # inventory.json lives alongside 书籍清单.md in the 书籍/ directory
    inventory_file = os.path.join(books_dir, "inventory.json")

    # Load inventory
    if not os.path.exists(inventory_file):
        print(f"ERROR: {inventory_file} not found. Run the initializer first.")
        sys.exit(1)

    with open(inventory_file, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    # Scan disk and reconcile
    disk = scan_disk(books_dir)
    inventory, new_files, missing_files = reconcile(inventory, disk, books_dir)

    # Write updated inventory (with any new stubs added)
    with open(inventory_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    # Generate markdown
    md_content = build_markdown(inventory)
    md_path = os.path.join(books_dir, "书籍清单.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Report
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
