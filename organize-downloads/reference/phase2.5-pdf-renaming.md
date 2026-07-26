# 2.5 阶段：PDF 论文重命名 + arXiv 重复检测

将文件名不直观的 PDF 论文，按 `第一作者姓_发表年份_短标题.pdf` 格式重命名。同时检测 arXiv 预印本是否与已有图书重复。

> 本阶段处理的 `论文/` 与用于对照的 `书籍/` 默认位于本地暂存根目录（通常为 `Documents/`），不是 Downloads 中的长期目录。

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
python <skill-dir>/scripts/rename_pdfs.py --dir 论文/(子目录)

# 确认后执行重命名
python <skill-dir>/scripts/rename_pdfs.py --dir 论文/(子目录) --rename

# 导出 JSON 结果
python <skill-dir>/scripts/rename_pdfs.py --dir 论文/ --json 论文/rename_report.json

# 处理所有 PDF（包括已命名的）
python <skill-dir>/scripts/rename_pdfs.py --dir 论文/ --all
```

## arXiv 版本关系检测（仅在查重白名单允许时）

arXiv 预印本可能与正式出版内容相同，但检查范围必须服从本次任务的查重白名单。用户只允许检查 OneDrive 时，只在指定 OneDrive 路径中检查；禁止顺带扫描 Zotero、Documents 或其他书库。

查重白名单包含对应书库时，按以下步骤检查：

1. **用 `rename_pdfs.py --dry-run` 提取 arXiv 的标题和作者**
2. **在 `书籍/` 下搜索是否有同名/同作者的图书**
3. **若发现重复**：
   - 标注 `(arXiv预印本)` 后缀，避免与正式版混淆
   - 提示用户决定是否移到 `书籍/待确认重复/` 或 `论文/{对应主题}/`

### 重复检测示例

```
原文件: 2102.05242v2.pdf
提取结果: Recht_2021_Patterns, Predictions, and Actions

检查: 书籍/AI工程与实践/ 下是否存在 Recht_*_Patterns*
发现: Recht_2024_Patterns, Predictions, and Actions.pdf（2024 正式版）

处理:
  重命名为: Recht_2021_Patterns, Predictions, and Actions (arXiv预印本).pdf
  保留位置: 论文/AI工程与实践/（让用户决定后续）
  报告: 与 书籍/AI工程与实践/Recht_2024_... 同书，arXiv 是 2021 预印本
```

### 重复判定的容错

- **作者姓名相同 + 标题相似度 > 0.8** → 视为重复候选
- **年份不同**（如 arXiv 2021 vs 正式版 2024）→ 标注但不删除
- **标题完全相同 + 同年份** → 高度怀疑完全重复，强烈建议移到 `待确认重复/`

## 重命名工作流

1. **扫描来源文件**：在文件尚未移动时筛选需要重命名的 PDF。
2. **dry-run 展示方案**：列出完整映射表；仅包含查重白名单允许的版本关系结果。
3. **执行重命名**：用户确认后在来源目录中先完成重命名并保存独立日志。
4. **重新读取目录状态**：后续分类和移动计划必须引用重命名后的文件名，不能沿用旧名。
5. **处理版本关系**：同题不同大小或版本默认进入待确认；不得直接当作完全重复删除。
6. **避免劣化已命名文件**：对于 `DeepSeek_2026_DeepSeek-V4.pdf` 这类已命名的文件，重命名可能反而变差（如改成 `2026_DeepSeek-V4 -.pdf`），用 `--target-unknown` 只处理未知文件，或手动跳过。

## 注意事项

- **不要覆盖已有文件**：目标文件名冲突时自动添加后缀 `_2`、`_3`
- **保留原文件扩展名**：`.pdf` 不可更改
- **中文论文**：姓氏取前 1-2 个汉字（如 `宋`、`欧阳`），标题保持中文
- **arXiv 论文**：年份可从 ID 推算（如 `2603` = 2026 年 3 月）
- **手动优先**：rename_pdfs.py 的启发式不完美。对于 3 个以内 arXiv 文件，建议手动 `mv` 重命名，避免批量重命名误伤已命名的文件
- **跳过乱码**：rename_pdfs.py 无法处理文件名编码错乱（如 `<=AB@B>@_...`）的文件，这类用 PyMuPDF 读首页文本手动判断后重命名
