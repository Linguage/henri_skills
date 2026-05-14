# 2.5 阶段：PDF 论文重命名

将文件名不直观的 PDF 论文，按 `第一作者姓_发表年份_短标题.pdf` 格式重命名。

## 命名格式

```
{LastName}_{Year}_{Short Title}.pdf
```

- **LastName**：第一作者姓氏（中文论文用姓，英文论文取 last name），去掉变音符号
- **Year**：发表年份（优先取 PDF 内文本中的年份，其次取 arXiv ID 前两位推算世纪）
- **Short Title**：原标题适当截断（建议 60 字符以内），去掉冒号等文件系统不安全字符

示例：
- `2603.20639v1.pdf` → `Smith_2026_A Survey on Large Language Models.pdf`
- `1-s2.0-S0043164825004788-main.pdf` → `Lee_2025_Deep Reinforcement Learning for Robotics.pdf`

## 需要重命名的文件名模式

- arXiv ID：`????.XXXXXv?.pdf`（如 `2603.20639v1.pdf`）
- ScienceDirect：`1-s2.0-*.pdf`
- Springer DOI：`s*-**-***-*.pdf`（如 `s40534-025-00375-7.pdf`）
- 其他文件名不直观的 PDF（短随机字符串、编号等）

**跳过的文件：**
- 文件名已包含可读的中文或英文标题
- 已符合 `作者_年份_标题` 格式的文件

## 提取脚本

使用 `rename_pdfs.py` 批量处理：

```bash
# 扫描并展示重命名方案（不执行）
conda run -n henri_env python .claude/skills/organize-downloads/rename_pdfs.py --dir 书籍/(子目录)

# 确认后执行重命名
conda run -n henri_env python .claude/skills/organize-downloads/rename_pdfs.py --dir 书籍/(子目录) --rename

# 导出 JSON 结果
conda run -n henri_env python .claude/skills/organize-downloads/rename_pdfs.py --dir 书籍/ --json 书籍/rename_report.json

# 处理所有 PDF（包括已命名的）
conda run -n henri_env python .claude/skills/organize-downloads/rename_pdfs.py --dir 书籍/ --all
```

## 重命名工作流

1. **扫描目标文件**：用脚本扫描指定目录，筛选出需要重命名的 PDF
2. **展示重命名方案**：列出完整映射表，等待用户确认
3. **执行重命名**：用户确认后加 `--rename` 执行
4. **更新书籍清单**：重命名完成后必须同步更新 `书籍清单.md`（见第三阶段）

## 注意事项

- **不要覆盖已有文件**：目标文件名冲突时自动添加后缀 `_2`、`_3`
- **保留原文件扩展名**：`.pdf` 不可更改
- **中文论文**：姓氏取前 1-2 个汉字（如 `宋`、`欧阳`），标题保持中文
- **arXiv 论文**：年份可从 ID 推算（如 `2603` = 2026 年 3 月）
