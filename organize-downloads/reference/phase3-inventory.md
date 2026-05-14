# 第三阶段：维护书籍清单

每次完成书籍目录的整理操作（新增文件、重命名、归类调整）后，**必须同步更新** `书籍/书籍清单.md`。

## 数据架构

```
书籍/
├── inventory.json       ← 主数据库（唯一数据源，手动编辑）
├── 书籍清单.md           ← 由 inventory.json 生成（只读，勿手动编辑）
├── (主题类别A)/
├── (主题类别B)/
├── (主题类别C)/
└── 杂志/
```

**核心原则：`inventory.json` 是唯一数据源，`书籍清单.md` 由脚本自动生成，绝不反向同步。**

## inventory.json 格式

```json
{
  "_meta": {
    "generated": "YYYY-MM-DD",
    "total_docs": 0,
    "description": "书籍目录主数据库。MD清单由此文件生成。"
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

## 维护工作流

1. **添加新论文**：移动 PDF 到对应子目录
2. **编辑元数据**：在 `inventory.json` 中填充 `cn_title` 和 `author`
3. **生成MD**：运行 `conda run -n henri_env python .claude/skills/organize-downloads/update_inventory.py`
4. **验证**：检查输出报告的 missing/incomplete 条目

脚本会自动：
- 检测磁盘上有但 JSON 中没有的新文件 → 添加 stub 条目（`cn_title` 和 `author` 留空）
- 检测 JSON 中有但磁盘上没有的文件 → 报告 missing（保留 JSON 条目不删除）
- 列出字段不完整的条目
- 重新生成 `书籍清单.md`

## 书籍清单.md 格式规范

```markdown
# 书籍与论文清单

> 自动生成于 YYYY-MM-DD，共 N 篇文档，分 M 个主题类别。

---

## 1. 主题类别名（N 篇）

| # | 中文译名 | 原标题 / 作者 | 文件 |
|---|---------|-------------|------|
| 1 | 中文标题 | Author et al. (Year) · *English Title* | [PDF](子目录/文件名.pdf) |
| 2 | 中文标题 | — | [PDF](子目录/文件名.pdf) |
```

## 清单编写规则

- **中文译名**：所有英文论文必须提供中文译名
- **作者格式**：`第一作者姓 et al. (年份)`，单一作者则不加 et al.，中文/非论文文档标 `—`
- **文件链接**：使用相对路径，文件名做 URL 编码（空格→`%20`，加号→`%2B` 等）
- **排序**：同一类别内按文件名字母序排列
- **更新时机**：每次整理操作完成后立即更新，不可跳过

## 清单更新检查项

更新清单时需确认：
- [ ] 文档总数与实际文件数一致
- [ ] 每个类别的篇数标注正确
- [ ] 所有文件链接可点击且指向正确文件
- [ ] 新增文档已补充中文译名
- [ ] 日期更新为当天
