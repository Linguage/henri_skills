---
name: organize-documents
description: 规范化整理 Documents/文档 库：统一文件命名、判定来源归属、粗粒度主题归类并记录日志。适用于对参考阅读、技术资料、课程与演示、个人整理目录做命名审计、去重、来源识别（个人整理 vs 网络快照 vs 网络原生）、子目录归类和批次移动；先出计划再执行，复用 organize-downloads 的 apply_move_plan.py。
metadata:
  author: Henri
  created: 2026-09-13
  last_updated: 2026-09-13
---

> **单一来源**：本 skill 的唯一实体在 `henri_skills` 仓库中，`~/.claude/skills/`、`~/.codex/skills/` 以及 `Documents/文档/.devin/skills/` 等均为软链接。编辑时请直接修改 `henri_skills` 中的文件。

# 文档库规范化整理

对 `/Users/henripogatrain/Documents/文档/` 这个**本地暂存库**做维护性整理：先规范命名，再判来源，最后按粗主题归类。它不是收件目录，不负责从 Downloads 分流（那是 `organize-downloads` 的职责）；也不改写任何文档内容。

## 目录角色（执行前复述）

| 路径（相对 `Documents/文档/`） | 角色 | 现有子目录 |
|---|---|---|
| `参考阅读/` | 非技术的报告、文章、合集、政策文件 | `AI报告/` `数学与科学史/` `工程与结构/` `计算机经典/` |
| `技术资料/` | 手册、指南、速查卡、专利、规范 | `AI工具/`（含 `Claude Code/` `OpenAI_Agent构建指南/`）`速查卡/` `结构与有限元/` `LaTeX/`（含 `字体/`） |
| `课程与演示/` | 讲义、课程笔记、习题、幻灯片 | `演示文稿/`（含 `MIT 6.S191/` `MIT 6.S978/`）`DeepSeek专题/` `基本分析讲义/` |
| `个人整理/` | 用户自建或 AI 辅助生成后导出的文档、自制 PPT/Keynote、邮件导出、译稿、脚本 | `CS50P/` `网页工具/`；**不再细分** |
| `.管理/.log/` | 每批操作的 JSON 日志 | — |
| `.管理/待删除/` | 确认重复后暂存，等待用户最终删除 | — |

`.管理/` 可能被用户手动清空；不存在时按需重建，不要把它的缺失当成异常。

## 命名规范

```
{作者或机构}_{年份}_{标题}.{ext}
```

- 作者：英文取姓（`Lamport`）、中文取全名（`段永平`）、多作者用连字符（`Arnold-Reitherman`）；机构用通行简称（`OpenAI`、`McKinsey Global Institute`、`清华大学沈阳团队`、`中国电子技术标准化研究院`）。
- 年份：按正文/版权页/讲座日期，不按下载日期；原文件名年份与正文冲突时以正文为准。查不到作者用 `{年份}_{标题}`；查不到年份用 `{机构}_{标题}`；两者都没有时保留原标题并在报告中单列。
- 标题：去掉书名号、`(1)` `(2)` `(Z-Library)` `(it-ebooks)` `【高清版】` `baoyu.io` 等下载残留和平台后缀；冒号改为连字符；保留必要的编号信息放在括号里（`(TRITA-BKN 141)`、`(PEER 2011-05)`）。
- 特殊类型前缀 / 后缀：
  - 同一文档的译本：`（中译）` / `（英文）` / `(宝玉中译)`
  - 邮件导出：`（Gmail邮件导出）` / `（Outlook邮件导出）`
  - AI 生成或对话导出：作者位写 `ChatGPT_` `Gemini DeepResearch_` `DeepSeek对话_` `AI对话_`，或标题尾加 `（AI综述）` `（AI问答）` `（视频脚本整理）`
  - 网页快照：作者位写来源站 `Wikipedia_` `Reddit_` `Quanta_`，年份取保存年
  - 专利：`专利CN112733390A_2021_标题`
  - 速查卡：`{工具}_Cheat Sheet.pdf` 或 `{作者}_{年份}_{工具} Reference Card.pdf`
  - 系列：`清华大学_2025_DeepSeek系列01-标题`，序号两位数
- 不改名的情况：已合规的文件；带 `_files/` 配套目录的 `.html`；`.DS_Store`。
- 无扩展名文件先用 `file` 判类型再补扩展名（如 mht 文本 → `.mht`）。

## 来源归属判定

用 `mdls -raw -name kMDItemCreator/kMDItemEncodingApplications` 加 `pdftotext -l 2` 首页文本，把文件分成三档；这一步的结论决定它归 `个人整理/` 还是留在资料目录：

| 档 | 判据 | 去向 |
|---|---|---|
| 个人整理 | Typora / Obsidian / Markor / LibreOffice / Keynote / PptxGenJS 生成；正文以提问开头或带 `[1][2]` 式引用（Perplexity 类）；注明 "来自 Gemini 的 Deep Research" "由视频脚本生成"；docx 作者字段是用户；Gmail/Outlook 打印；自写脚本和网页工具 | `个人整理/` |
| 网络快照 | Chrome/Chromium/Safari 打印为 PDF、`.mht`、保存的 `.html`，内容是他人的网页 | 留在资料目录，作者位写来源站 |
| 网络原生 | InDesign / LaTeX / Word / Acrobat Distiller / 出版商 PDF 库生成的发布文档、EPUB、专利、手册 | 留在资料目录 |

纯图片 PDF、元数据为空的文件无法判定时列出来问用户，不猜。

## 主题归类原则

- 粗分：一个子目录至少约 6 个文件才值得建；不足的留在根目录，等积累后再建。
- 优先复用上表已有子目录；新建目录及其名称必须先列出并获得确认。
- 同一作品的中英文版、上下册、PDF+Markdown 放在同一目录，不因语言拆开。
- 目录（如 `CS50P/`、`MIT 6.S978/`）整体移动用 `mv`，脚本只处理文件。
- 疑似重复：比对页数、首页文本、渲染页；确认为同一内容后保留更完整的一份，另一份移到 `.管理/待删除/`，不用 `rm`。不同语言、不同版本、上下篇不算重复。

## 工作流程

```
0. 复述目录角色，确认本次范围（哪些目录）
1. 审计：ls + mdls + pdftotext 首页，列出不合规命名、疑似重复、来源可疑项
2. 写重命名计划 JSON → 预检 → 向用户列出全部映射与不确定的年份 → 确认后执行
3. 写来源归属表 → 用户确认 → 个人整理项移动
4. 写主题移动计划 JSON（引用重命名后的文件名）→ 确认新目录 → 执行
5. 去重：确认后移入 .管理/待删除/
6. 每批写日志 .管理/.log/YYYY-MM-DD_{rename|topic_move|personal|dedup|*_dirs}.json；清理 /tmp 下的计划文件
```

计划文件格式与执行脚本复用 `organize-downloads`：

```bash
SKILL_DL=~/.agents/skills/organize-downloads
python3 $SKILL_DL/scripts/apply_move_plan.py PLAN.json            # 预检
python3 $SKILL_DL/scripts/apply_move_plan.py PLAN.json --execute --log "<root>/.管理/.log/YYYY-MM-DD_xxx.json"
```

```json
{"root": "/Users/henripogatrain/Documents/文档",
 "moves": [{"source": "参考阅读/旧名.pdf", "target": "参考阅读/AI报告/新名.pdf"}]}
```

脚本拒绝覆盖、重复目标和越出根目录；`source` 必须是文件。执行后用 Python 校验所有 `target` 存在、所有 `source` 消失。

## 已知坑

- 文件名里可能混入兼容字符（`⾥` U+2F72 vs `里`），预检报 missing source 时先 `ls | grep` 取真实字节再写计划。
- `.key` 在 macOS 上可能是包目录也可能是单文件，先 `ls -ld` 再决定用 `mv` 还是脚本。
- `mdls` 的 Authors 字段多为生成软件名，不是真实作者；真实作者看首页文本。
- 重命名与移动分两个计划、两份日志；移动计划必须引用重命名后的名字。
- 未经确认不新建目录、不删除文件、不移动 `.管理/` 以外的现有目录。
