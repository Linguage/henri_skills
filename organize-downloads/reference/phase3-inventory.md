# 第四阶段：维护书籍清单

After adding, renaming, moving, reclassifying, or moving books to pending deletion, update that library's `inventory.json` and regenerate `书籍清单.md`.

> 本文件中的 `书籍/` 指本地暂存根目录（通常为 `Documents/`）下的图书库。云端归档库应维护自己的独立清单，不能用其中一方覆盖另一方。

## 范围说明

经过第二阶段分流后，`inventory.json` **只跟踪 `书籍/` 下的图书**：
- `论文/` 下的论文和专业书籍**不在** inventory 中（无统一清单）
- `文档/` 下的报告、讲义与一般资料**不在** inventory 中
- `书籍/杂志/`、`书籍/待确认重复/`、`书籍/重复/` 与 `书籍/已归档/` 不被 update_inventory.py 跟踪；人物和大文件等登记类别支持递归发现

Keep paper indexes separate from the book inventory. Apply the local-link rules below to existing `文献目录.md` files; do not create a new paper database merely to refresh their links.

## Local-only publication indexes

Henri's Downloads indexes describe files present in the indexed folder, not all works ever processed or archived. For a project `文献目录.md`, the boundary is that file's containing folder and its descendants; for `书籍清单.md`, it is the book-library root and its descendants.

- Build the active list from the actual remaining files after the authorized moves. Do not keep moved-out files in the active catalog or replace their links with OneDrive, sibling-project, other-library, or pending-deletion links.
- Use relative file links. Decode URL escapes and resolve the target, including symlinks, when validating: it must exist as a file and remain inside the applicable boundary. A link that opens successfully outside that boundary still fails this requirement.
- Back up the previous generated index in the existing log location. Keep archive destinations and previous locations in movement/history logs, not in the active local index.
- Keep existing full-text JSONL records, extraction reports, and schemas intact during an index-only cleanup. Do not delete records because the original PDF moved, or automatically rewrite database paths to OneDrive. Historical paths already embedded in raw records are not proof that their files are present locally; distinguish the database's record count from the folder's publication count.
- A local index may link to its own folder's database and extraction report. If the database includes moved-out publications, state that its records cover more material than the currently retained PDFs.

## 数据架构

```
书籍/
├── inventory.json       ← 主数据库（唯一数据源，手动编辑）
├── 书籍清单.md           ← 由 inventory.json 生成（只读，勿手动编辑）
├── (主题子目录，如 数学/ 物理与自然科学/ 工程科学/ 科学人文/ 思想与人文/)
├── 杂志/
└── 待确认重复/
```

**核心原则：`inventory.json` 是唯一数据源，`书籍清单.md` 由脚本自动生成，绝不反向同步。**

## inventory.json 格式

```json
{
  "_meta": {
    "generated": "YYYY-MM-DD",
    "total_docs": 0,
    "description": "书籍目录主数据库。MD清单由此文件生成。",
    "categories": ["数学", "物理与自然科学", "工程科学", "科学人文", "思想与人文"]
  },
  "categories": {
    "(主题类别A)": [
      {
        "filename": "Author_2024_Paper Title.pdf",
        "cn_title": "论文中文译名",
        "author": "Author et al. (2024)",
        "added_date": "YYYY-MM-DD",
        "notes": ""
      }
    ]
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `filename` | string | 磁盘上的文件名（主键） |
| `cn_title` | string | 中文译名（显示在MD表格中） |
| `author` | string | 作者信息，格式 `姓 et al. (年份)` 或 `—` |
| `added_date` | string | ISO 日期，文件下载/添加日期 |
| `notes` | string | 备注（可选，不显示在MD中） |
| `_meta.categories` | list | 类目顺序，控制 书籍清单.md 章节顺序 |

## 维护工作流

1. **初始化新书库**：若尚无 `inventory.json`，运行 `python <skill-dir>/scripts/update_inventory.py --books-dir <书籍绝对路径> --init`。该参数只创建清单文件，不创建或细分主题目录，也不覆盖现有 inventory。
2. **添加新图书**：移动 PDF/EPUB 到已经确认的对应子目录。
3. **编辑元数据**：在 `inventory.json` 中填充 `cn_title` 和 `author`。
4. **生成MD**：运行 `python <skill-dir>/scripts/update_inventory.py --books-dir <书籍绝对路径>`。
5. **验证**：检查输出报告的 missing/incomplete 条目。

`update_inventory.py` 脚本会自动：
- 检测磁盘上有但 JSON 中没有的新文件 → 添加 stub 条目（`cn_title` 和 `author` 留空）
- 递归发现 `人物/姓名`、`大文件/主题` 等多级类别，同时排除杂志和待确认重复
- 检测 JSON 中有但磁盘上没有的文件 → **报告 missing，但不删除 JSON 条目**
- 列出字段不完整的条目
- 重新生成 `书籍清单.md`

## 清理 missing 条目（重要）

`update_inventory.py` **不会自动删除** missing 条目。当大量文件被分流到 `论文/` 或 `文档/` 后，inventory.json 会保留所有旧条目，导致 书籍清单.md 显示已不存在的文件（链接失效）。

For an authorized move or cleanup, back up the inventory and remove the exact entries identified by the completed move list, using category plus filename rather than filename alone. Preserve all metadata for retained entries. Remove emptied categories from both `categories` and `_meta.categories`, and update totals before regenerating the Markdown.

Investigate other missing entries separately. Do not silently discard metadata because a path is temporarily unavailable or a library could not be read. The active index must not publish broken file links; keep unresolved metadata in the backup or audit record rather than presenting it as a locally present file.

Run `update_inventory.py` after this reconciliation. Running it alone does not remove moved-out entries, and regeneration is not complete until the resulting local links have been checked.

## 子目录改名 / 拆分时的同步

当主题子目录改名（如 `科技人文与数学` → `数学`、`物理与自然科学`、`科学人文`）或拆分（一个旧目录拆为多个新目录）时，inventory.json 要按以下规则同步：

1. **按文件实际位置归类目**，不要直接清空原类目：
   ```python
   for entry in inv["categories"]["科技人文与数学"]:
       fn = entry["filename"]
       if os.path.exists(f"{BOOKS}/思想与人文/{fn}"):
           new_cat_entries["思想与人文"].append(entry)
       elif os.path.exists(f"{BOOKS}/数学/{fn}"):
           new_cat_entries["数学"].append(entry)
   ```
2. **保留 `cn_title`、`author`、`added_date`** 等元数据，不要清空
3. **更新 `_meta.categories`**：在原位置替换为新类目（保持顺序）
4. **删除空类目**：从 `categories` 字典和 `_meta.categories` 列表中同时删除

## 书籍清单.md 格式规范

```markdown
# 书籍清单

> 自动生成于 YYYY-MM-DD，共 N 本图书，分 M 个主题类别。

---

## 1. 主题类别名（N 本）

| # | 中文译名 | 原标题 / 作者 | 文件 |
|---|---------|-------------|------|
| 1 | 中文标题 | Author et al. (Year) · *English Title* | [PDF](子目录/文件名.pdf) |
| 2 | 中文标题 | — | [PDF](子目录/文件名.pdf) |
```

> **注意**：第二阶段分流后，标题改为"书籍清单"（不再是"书籍与论文清单"，论文已移出）。

## 清单编写规则

- **中文译名**：所有英文图书必须提供中文译名
- **作者格式**：`第一作者姓 et al. (年份)`，单一作者则不加 et al.，中文/非图书文档标 `—`
- **File links**: use valid relative Markdown links to files inside the indexed root. URL-encode special characters, or use the existing generator's angle-bracket destinations where valid; validate decoded, resolved targets in either case.
- **排序**：同一类别内按文件名字母序排列
- **更新时机**：每次整理操作完成后立即更新，不可跳过

## 清单更新检查项

更新清单时需确认：
- [ ] Catalog totals match actual tracked files, including recursively discovered categories; report excluded magazines and duplicate-review directories separately when counting the entire library.
- [ ] 每个类别的篇数标注正确
- [ ] Every active file link resolves to an existing file inside the indexed root; no OneDrive, sibling-library, pending-deletion, or missing-file targets remain.
- [ ] 新增图书已补充中文译名（INCOMPLETE METADATA 列表为空）
- [ ] 日期更新为当天
- [ ] 子目录改名/拆分后，`_meta.categories` 顺序正确
