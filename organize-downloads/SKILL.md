---
name: organize-downloads
description: 整理 Downloads 或类似收件目录，区分论文、图书、报告、讲义和扫描版，先规范命名再移动到用户明确指定的本地目录，并维护书库清单与移动日志。适用于目录审计、批量归类、扫描文档 OCR、Downloads 根目录归位、独立书库对账、OneDrive 等指定来源查重、备份整合和目录迁移。必须按绝对路径确认 tmp 等目录含义，查重来源采用用户授权白名单；优先复用现有宽分类，任何新目录都需先列出并获得确认。
metadata:
  author: Henri
  created: 2026-05-14
  last_updated: 2026-07-26
---

> **Single source of truth**: This skill is maintained in the `henri_skills` repository. Edit the repository files, not the symlinked copies used by agent clients.

# Downloads 文件整理

把 Downloads 视为接收和处理入口，而不是整理完成内容的长期存放地。先在来源目录中识别、查重和规范命名，再把已完成分类的文档型内容移动到 Documents 或用户指定的本地暂存库。`书籍/` 中的内容先按文档类型分流，保留的图书再按主题归类。

用户明确指定的目录角色与路径优先于本技能默认值。特别是用户说“tmp”时，必须先解析并复述其绝对路径；已知用户指 `Downloads/tmp` 时，禁止改用 `/tmp`、`/private/tmp` 或其他系统临时目录作为整理库。系统临时目录只能保存可随时删除的计划、OCR 图像和中间产物，不能承载最终整理内容。

## 当前用户约定：文档项目与个人档案的归位

Henri uses two independent roots: document projects belong in `/Users/henripogatrain/Documents/文档项目/`, while personal archives belong in `/Users/henripogatrain/Documents/个人档案/`. These are sibling libraries under Documents; do not place personal archives in `Documents/文档项目/个人档案/`. This replaces the earlier completed-content destinations in `Downloads/项目/` and `Downloads/个人档案/`. Other users' explicit paths take precedence. Existing destinations for books, standalone original papers, and other content remain unchanged; software repositories are not document projects merely because their parent is named 项目.

| 内容与用途 | Target relative to `/Users/henripogatrain/Documents/` |
|---|---|
| 专题文献综述、领域调研及其文献库、证据素材和稿件，例如半导体制造视觉方法、轨道交通产业调研 | `文档项目/文献调研/{专题项目}/` |
| 围绕具体经典专著或论文的精读、译注、对照文本、研读笔记及配套资料 | `文档项目/经典研读/{作品或研读项目}/` |
| 身份、求职、财务、私人服务记录与聊天备份等个人档案 | `个人档案/{已有类别}/`；没有合适类别时先提出目录方案 |
| 学位论文、答辩、审查及正式配套材料 | 优先复用 `文档项目/01-论文与答辩/` 下现有的论文正稿、答辩与审查、论文附件等对应目录 |

文档项目直接归入“文献调研”“经典研读”等用途子目录，不另套一层 `项目/`。按项目的实际目的判断类别，不把所有译文或名人文章都当作“经典研读”；其他文档项目先检查并复用现有 `02-数据与文献/`、`03-其他材料/` 等合适分类，仍无合适类别时提出建议并等待确认。敏感个人档案与公开文献调研、经典研读资料分开存放。

Reuse existing categories in the independent personal-archive root; do not recreate `文档项目/个人档案/`. Preserve versions, internal links, and attachments when migrating personal archives. Keep original subdirectories or merge into existing categories according to the user-confirmed batch plan, without overwriting same-name files.

These conventions specify destinations, not permission to migrate existing directories, create missing categories, or rearrange Documents. List source paths, targets, and new directories and obtain confirmation for the relevant batch. A request to update the skill alone does not authorize moving files.

## 目录角色与存储边界（执行前必查）

不要仅凭目录同名、内容重叠或存在云端副本，推断两个目录是同一书库。先明确每个目录的角色：

- **收件与处理区**：如 `Downloads/`。只保存新下载、待识别、正在处理、待确认和短期待删除内容；整理完成的文档型内容不继续长期留在这里。
- **本地暂存库**：如 `Documents/书籍/`、`Documents/论文/`、`Documents/文档/`、`Documents/个人档案/`。用于保存已完成分类、等待后续使用或云端归档的内容；它是独立本地库，允许与云端不同。
- **云端归档库**：如 OneDrive、iCloud、NAS 或其他同步目录中的 `书籍/`。用于长期保存、跨设备同步和维护归档清单；它不是本地积累库的替代路径。
- **过渡目录**：如 `书籍1/`、`待分类/`、`tmp/`。必须记录并向用户复述绝对路径，不能根据目录名自行改用系统临时目录。只有用户明确说明生命周期后才能清空或移除。
- **待删除区**：只保存经过确认、等待最终删除的副本或临时产物；不能把正常来源库当作待删除区。

执行前必须向用户确认或从既有约定中查明：来源目录、本地暂存根目录、云端归档根目录（如有）、采用复制还是移动，以及来源文件是否保留。缺少明确约定时，采用以下安全默认值：

1. “整理 Downloads”解释为：在获得移动方案确认后，把已完成分类的内容**移动**到本地暂存库；Downloads 只保留未完成批次、待确认项和短期待删除项。
2. “同步、备份、整合、归档到云端”解释为：从本地暂存库**查重后复制**，本地暂存副本保留。
3. Local cleanup requires a user request such as “把已经备份、可以清理的文件移到待删除”. Apply it to the named directories and batch; an earlier authorization remains valid for that scope. Files do not need to be retained merely because they were called “originals”.
4. A statement that cloud backup is complete does not itself authorize local cleanup. Once the user also requests cleanup, move all files whose backup is supported by the evidence into the approved pending-deletion batch; retain unresolved files and explain the specific gap.
5. Do not automatically download offline cloud papers or books for deduplication, auditing, or restoration. Use existing verification records and current file metadata where sufficient; filename and size alone do not prove identical content. Ask for download authorization only when content access is necessary and not already authorized.
6. 本地库和云端库分别维护自己的 `inventory.json` 与 `书籍清单.md`。一次归档只更新目标库清单，不得用目标库清单覆盖来源库清单。
7. 若误把云端复制执行成移动，立即停止后续清理，依据执行日志区分仍在本地的文件与云端占位文件；未经授权不得批量下载恢复。
8. 查重来源采用白名单。用户指定“只检查 OneDrive”时，只检查该 OneDrive 路径，禁止顺带扫描 Zotero、Documents、其他书库或缓存目录。
9. 优先复用目标根目录中已有的宽分类。当前目录没有合适类别时，先列出拟新增目录及理由并等待确认；不得自行创建过细专题或多层目录。
10. 用户可为不同类型指定不同目标根目录，例如图书进入 `Downloads/书籍`，论文和其它文档进入 `Downloads/tmp`。按用户给出的逐类型路径执行，不强制统一到 Documents。
11. 整理日志默认放入用户指定暂存根目录下的隐藏 `.log/`；创建 `.log/` 也需要用户明确同意或已有约定。

## Backup completion, cleanup, and local-only indexes

For cloud backup, backup-status questions, or cleanup after backup, read [`reference/backup-and-cleanup.md`](reference/backup-and-cleanup.md). Apply these constraints throughout the workflow:

- Track every source file as copied and verified, already present with supporting evidence, or unresolved. Copying into a local OneDrive directory and completing cloud synchronization are separate facts; never report the entire backup complete while any source file remains unresolved.
- Report physical files currently present, files moved in this batch, and files remaining. Keep hash-deduplicated content counts, earlier batches, and database/catalog files separate from publication-file counts.
- Henri's Downloads literature indexes and book catalogs list only files physically present within their own folder or library. Remove entries for files moved out; do not redirect their links to OneDrive, another library, or the pending-deletion folder. Check resolved link targets against that index's folder boundary. Details: [`reference/phase3-inventory.md`](reference/phase3-inventory.md).
- Updating a generated index does not authorize deleting or rewriting full-text database records. Preserve the database body and keep archive history in the existing log location.
- Existing cleanup authorization covers its agreed batch. Prepare the concrete move list, reuse the pending-deletion location, verify moves, and finish without requesting the same confirmation again.

## 目录结构

详见 [`reference/directory-template.md`](reference/directory-template.md)。

精简结构：
```
Downloads/                  # 收件与处理区
├── _待处理/                # 尚未识别或待确认
├── 临时文件/               # 未完成下载和短期中间状态
└── 待删除/                 # 等待用户最终确认

Documents/                  # 默认本地暂存库；也可由用户指定其他根目录
├── 书籍/          # 仅保留真正的图书（EPUB、教材、专著、大众读物）
│   ├── (主题子目录，如 数学/ 物理与自然科学/ 工程科学/ 科学人文/ 思想与人文/ AI工程与实践/ 铁路与交通工程/)
│   ├── 大文件/      # 主要收纳扫描版，内部按同一主题框架细分
│   ├── 人物/        # 按人物归集著作、传记和通信
│   ├── 丛书/        # 按正式丛书或系列名归集各卷，优先级仅次于人物
│   ├── 杂志/      # 期刊报纸
│   └── 待确认重复/
├── 论文/          # 期刊/会议论文、预印本和长综述（按主题分子目录）→ 见 phase2
│   ├── (主题子目录，对应原 书籍/ 子目录名)
│   └── 专题综述/  # 长综述、专题论文集和超长预印本；不收完整出版的教材/专著
├── 文档/          # PPTX、XLSX、DOCX、TXT、HTML，以及非图书、非论文资料
│   ├── 报告与白皮书/
│   ├── 技术资料/
│   ├── 课程与演示/
│   └── 杂项收容/
├── 个人档案/      # 敏感个人信息文档
└── 学位论文/      # 正稿、章节、引用文献、汇报与铁路工程研究等
```

图片、视频、音频、安装包和数据集只有在 Documents 或用户指定位置已有明确长期目录时才移动过去；否则先提出目标建议，不要为了清空 Downloads 擅自新建宽泛资料库。

## 知识性文档的项目关联优先

用户自行撰写、检索整理、翻译、汇编或重新生成的知识性文档（如文献综述、专题调研、阅读研究稿），先判断其直接关联的项目，再按文档类型分流。能确认项目关系的内容优先归入对应项目，不把正文、文献库、章节素材、图表和 PDF 导出版分别拆到论文、文档或图片库。

在本次授权的收件根目录及点名项目目录内，核对同一项目的散落稿件、框架、术语库、参考文献主表、论证素材、附件与输出文件，集中到用户确认的项目路径；原版资料若明确作为该项目的直接来源，也可随项目归集。仅主题关键词相似不足以判定关联，无明确项目关系的独立原版资料仍按类型归类；不得借项目归集扩展查重或扫描白名单。

这里的“整合”默认指文件归集和关系梳理，不授权改写正文、拼接章节或替用户决定定稿。保留源稿与导出版的配对、不同版本及引用编号，必要时增加项目资料索引；移动时检查本地链接及附件关系。优先复用现有项目目录，新增目录和层级仍须事先列出并获得确认。

## 完整工作流程

```
阶段 0：确认每个目录的绝对路径、查重白名单、保留策略、复制/移动语义和云端占位状态
  → 根目录散落文件
  → 提取元信息和必要正文，识别类型与敏感内容
  → 自行整理的知识性文档先核对项目关联，归集直接相关的稿件、来源与附件
  → 在来源目录中先生成并执行重命名计划
  → 第一阶段：只复用已确认目录，按类型移动到各自目标根
  → 第二阶段：书籍目录文档类型分流（论文/图书/报告/讲义/规章分离）
     判断顺序：
       (1) PDF 元信息（metadata.title/author + 首页文本特征）
       (2) 文件名启发式（arXiv ID / ISBN / 出版社 / "Report" 等）
       (3) 元信息不明确时，页数兜底：>80 页 → 书籍或研究报告；≤80 页 → 论文候选
     分流去向：
       → 论文            → Documents/论文/{原主题子目录}/
       → 学术专著/教材   → Documents/书籍/{主题}/
       → 大众/工程书     → Documents/书籍/{主题}/
       → 报告/讲义/规章  → Documents/文档/{对应主题目录}/
  → 2.5 阶段：对仍未规范的 PDF 补充重命名；只在查重白名单允许时检查 arXiv 版本关系
  → 2.7 阶段：命名不明确文档的内容提取与改名（提取内容 + PII 检测）
  → 2.8 阶段：全文提取与元数据整合（可选，输出 _metadata_integrated.json）
  → 第三阶段：书籍按主题归类（仅针对保留在 书籍/ 的图书）
     归集优先级：人物 > 丛书 > 用户声明的专门主题 > 扫描属性 > 一般主题
  → 第四阶段：维护 inventory.json + 生成 书籍清单.md
  → 第五阶段：图片来源分类（classify_images.py 三层系统）
```

执行时应按阶段依次进行，每个阶段完成后向用户报告结果，再进入下一阶段。

### 各阶段详细规则

| 阶段 | 说明 | 详细规则 |
|------|------|---------|
| 第一阶段 | 根目录文件分类 + 敏感文档识别 | [`reference/phase1-root-classification.md`](reference/phase1-root-classification.md) |
| 第二阶段 | **文档类型分流**（元信息 + 页数兜底） | [`reference/phase2-book-categorization.md`](reference/phase2-book-categorization.md) |
| 2.5 阶段 | PDF 论文重命名 + arXiv 重复检测 | [`reference/phase2.5-pdf-renaming.md`](reference/phase2.5-pdf-renaming.md) |
| 2.7 阶段 | **命名不明确文档：内容提取 + 改名 + PII 检测** | [`reference/phase2.7-unclear-doc-rename.md`](reference/phase2.7-unclear-doc-rename.md) |
| 2.8 阶段 | **全文提取与元数据整合**（可选，输出 `_metadata_integrated.json`） | [`reference/phase2.8-fulltext-extraction.md`](reference/phase2.8-fulltext-extraction.md) |
| 第三阶段 | 书籍按主题归类到子目录（仅针对保留在 书籍/ 的图书） | [`reference/phase3-book-thematic.md`](reference/phase3-book-thematic.md) |
| 第四阶段 | 维护 inventory.json + 生成书籍清单.md | [`reference/phase3-inventory.md`](reference/phase3-inventory.md) |
| 第五阶段 | 图片三层来源分类系统 | [`reference/phase4-image-classification.md`](reference/phase4-image-classification.md) |

## 脚本清单

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `classify_images.py` | 图片来源分类 | `--scan-root` / `--move` / `--json` |
| `rename_pdfs.py` | PDF 论文批量重命名 | `--dir PATH` / `--rename` / `--json` / `--all` |
| `update_inventory.py` | 初始化或对账 inventory.json 并生成书籍清单.md | `--books-dir PATH` / `--init` / `--dry-run` |
| `apply_move_plan.py` | 安全预检并执行同根或跨根 JSON 移动清单；默认只检查，不删除、不覆盖 | `PLAN.json` / `--execute` / `--log PATH` |
| `classification_rules.json` | 图片分类外部规则配置 | 由 classify_images.py 读取 |

批量移动项目较多时，优先把已经获得用户确认的操作写成 JSON 清单，再使用
`apply_move_plan.py`。同一根目录内移动时，清单包含一个绝对 `root`；从 Downloads
归位到 Documents 等跨根移动时，分别使用绝对 `source_root` 与 `target_root`。
`moves`（或 `operations`）中的 `source`、`target` 分别相对于对应根目录。脚本拒绝
越出根目录、缺失源文件、重复目标和覆盖已有文件。默认只做预检，只有显式传入
`--execute` 才执行移动。

## 运行环境

脚本使用 Python 3，不依赖特定代理、客户端或虚拟环境：
```bash
python <skill-dir>/scripts/<script>.py
```

依赖安装到任意隔离的 Python 环境即可：

```bash
python -m pip install -r <skill-dir>/scripts/requirements.txt

# OCR 工具（用于识别扫描版 PDF，详见 phase2.7 第三章）
brew install tesseract tesseract-lang
```

`requirements.txt` 包含脚本的额外依赖（opencv-python-headless、Pillow、numpy、PyMuPDF）。

`tesseract` 用于识别扫描版 PDF / 纯图像 PDF。先从 `PATH` 查找可执行文件；macOS Homebrew 的常见后备位置是 `/opt/homebrew/bin/tesseract`。临时图像应放在执行环境允许读写的目录中。

**外语文档**：识别非中文/非英文文档时，必须按文档实际语言选择 tesseract 语言包（西里尔→`rus`、假名→`jpn`、韩文→`kor`、阿拉伯文→`ara` 等），可用 `+` 组合（如 `rus+eng`）。详见 phase2.7 第 3.7 节。

## 临时产物管理

- 把任务中临时生成的脚本、移动清单、OCR 图片、文本抽取结果、测试样本和中间报告放入操作系统临时目录或任务专用临时目录，不要散落在待整理根目录。
- 创建临时目录时记录其确切路径；任务完成并验证最终结果后，立即清理本任务创建的临时文件和空目录。
- 清理前确认目标确为本任务生成，且不属于用户原始文件、最终交付物、正式 inventory、需要长期保留的审计日志或回滚记录。
- 临时脚本若经验证具有跨任务复用价值，按通用参数化方式并入本技能的 `scripts/` 并补充测试与调用说明；并入后清理工作副本。一次性、硬编码具体路径或日期的脚本在任务完成后清理。
- 任务失败或中断时，只保留继续诊断或安全回滚必需的产物，并在交接中列明路径与保留原因；恢复工作或确认无用后立即清理。
- 使用 `try/finally`、临时目录上下文管理器或等价机制，使正常完成与异常退出都能执行清理。不得为了清理临时产物而删除来源不明的文件。

## 重要规则

- **先声明目录角色**：执行前明确来源库、目标库、过渡目录和待删除区；同名目录不代表同一书库
- **绝对路径复述**：把用户使用的 `tmp`、`书籍` 等相对称呼解析为绝对路径并在移动前复述；禁止把用户目录替换成系统 `/tmp` 或 `/private/tmp`
- **查重白名单**：只检查用户点名或已明确约定的库；不得为了“更完整”自行加入 Zotero、Documents 或其他来源
- **先重命名后移动**：分别生成重命名计划与移动计划；移动计划必须引用重命名后的文件名，并分别保留日志
- **目录命名保守**：优先复用已有宽分类；任何新目录及新增层级都必须先列出并获得用户确认
- **Downloads 只作入口**：已完成分类的文档型内容默认移动到 Documents 或用户指定的本地暂存库，不在 Downloads 中另建长期镜像
- **整合默认复制**：同步、备份、整合和归档默认只复制新增文件，保留来源库；移动必须获得明确、逐目录授权
- **Cleanup authorization**: cloud presence alone is not authorization. After the user requests cleanup, move every eligible file in the authorized scope to pending deletion, including files previously described as originals; leave unresolved files in place.
- **保护云端占位文件**：查重和盘点不得自动下载已释放空间的图书；管理文档与图书正文分开处理
- **Authorization**: list the concrete operations before execution and obtain any missing authorization. Reuse existing approval for the same directories and batch; do not request it again merely because the work continues in another turn.
- **不直接删除**：禁止使用 `rm` 命令，所有需要删除的文件先移动到 `待删除/` 文件夹
- **保留现有文件夹**：不要移动已存在的分类文件夹（书籍、文档、图片等）
- **检查目标文件夹**：移动前检查目标文件夹是否存在；不存在时不得直接创建，必须先获得用户对目录名称和层级的确认
- **避免冲突**：如果目标位置已有同名文件，询问用户如何处理
- **清单分库维护**：哪个书库发生变动就更新哪个书库的 `inventory.json` 和 `书籍清单.md`，不得跨库覆盖
- **归类可讨论**：对无法自动归类的文档，主动向用户提出讨论，不擅自决定
- **临时产物必清理**：最终验证完成后，清理本任务生成且不再需要的临时脚本、清单、OCR/渲染文件和中间产物
