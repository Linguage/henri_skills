---
name: organize-downloads
description: 整理 Downloads 根目录文件，按类型分类到对应文件夹。对书籍目录进一步按主题归类，并维护书籍清单.md。操作前必须获取用户授权，不直接删除文件。
---

# Downloads 文件整理

整理 Downloads 根目录的散落文件，按类型分类到对应文件夹，并对书籍目录做主题归类。

## 目录结构

详见 [`reference/directory-template.md`](reference/directory-template.md)。

精简结构：
```
Downloads/
├── 书籍/          # PDF、EPUB（按主题分子目录）→ 见 phase2
├── 文档/          # PPTX、XLSX、DOCX、TXT、HTML
├── 图片/          # 三层来源分类系统 → 见 phase4
├── 视频/          # MP4、MOV
├── 安装包/        # DMG、PKG、ZIP
├── 数据文件/      # CSV、JSON
├── 个人档案/      # 敏感个人信息文档
├── 音频/          # M4A、MP3
├── 临时文件/      # CRDOWNLOAD
└── 待删除/        # 等待用户确认后删除
```

## 完整工作流程

```
根目录散落文件
  → 第一阶段：按类型分类（书籍/文档/图片/安装包/...）
  → 第二阶段：书籍目录按主题归类（子目录）
  → 2.5 阶段：PDF 论文重命名（rename_pdfs.py）
  → 第三阶段：更新 书籍清单.md
  → 第四阶段：图片来源分类（classify_images.py 三层系统）
```

执行时应按阶段依次进行，每个阶段完成后向用户报告结果，再进入下一阶段。

### 各阶段详细规则

| 阶段 | 说明 | 详细规则 |
|------|------|---------|
| 第一阶段 | 根目录文件分类 + 敏感文档识别 | [`reference/phase1-root-classification.md`](reference/phase1-root-classification.md) |
| 第二阶段 | 书籍按主题归类到子目录 | [`reference/phase2-book-categorization.md`](reference/phase2-book-categorization.md) |
| 2.5 阶段 | PDF 论文重命名（arXiv/ScienceDirect/Springer） | [`reference/phase2.5-pdf-renaming.md`](reference/phase2.5-pdf-renaming.md) |
| 第三阶段 | 维护 inventory.json + 生成书籍清单.md | [`reference/phase3-inventory.md`](reference/phase3-inventory.md) |
| 第四阶段 | 图片三层来源分类系统 | [`reference/phase4-image-classification.md`](reference/phase4-image-classification.md) |

## 脚本清单

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `classify_images.py` | 图片来源分类 | `--scan-root` / `--move` / `--json` |
| `rename_pdfs.py` | PDF 论文批量重命名 | `--dir PATH` / `--rename` / `--json` / `--all` |
| `update_inventory.py` | 从 inventory.json 生成书籍清单.md | 无参数 |
| `classification_rules.json` | 图片分类外部规则配置 | 由 classify_images.py 读取 |

## 运行环境

所有 Python 脚本均使用 `henri_env` conda 环境运行：
```bash
conda run -n henri_env python <script>
```

### 新设备配置

```bash
conda create -n henri_env python=3.13
conda activate henri_env
pip install -r .claude/skills/organize-downloads/scripts/requirements.txt
```

`requirements.txt` 包含本 skill 所有脚本的额外依赖（opencv-python-headless、Pillow、numpy、PyMuPDF）。

## 重要规则

- **获取授权**：在执行任何文件移动前，必须列出所有操作并等待用户确认
- **不直接删除**：禁止使用 `rm` 命令，所有需要删除的文件先移动到 `待删除/` 文件夹
- **保留现有文件夹**：不要移动已存在的分类文件夹（书籍、文档、图片等）
- **检查目标文件夹**：移动前检查目标文件夹是否存在，不存在则创建
- **避免冲突**：如果目标位置已有同名文件，询问用户如何处理
- **清单必更新**：书籍目录有任何变动后，必须同步更新 `书籍清单.md`
- **归类可讨论**：对无法自动归类的文档，主动向用户提出讨论，不擅自决定
