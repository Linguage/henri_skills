# 第二阶段：书籍目录文档类型分流

`书籍/` 是第一阶段文件分类的兜底目录，里面会混杂论文、图书、报告、讲义、规章等不同类型的内容。本阶段的目标是**先把不同类型分流到合适的根目录**，留下来的才是真正的图书，再交给第三阶段做主题归类。

> 本文件中的 `书籍/`、`论文/` 和 `文档/` 都相对于本地暂存根目录（通常为 `Documents/`）。Downloads 中的同名旧目录属于待迁移批次或过渡目录，不再作为长期库。

## 一、目标分流去向

| 文档类型 | 去向 | 说明 |
|---------|------|------|
| **论文**（期刊/会议/arXiv 预印本） | `论文/{原主题子目录}/` | 子目录名沿用 书籍/ 原类目 |
| **学术专著 / 教材** | `书籍/{主题}/` | 有 ISBN、出版社与完整章节结构的正式图书，包括研究生教材 |
| **长综述 / arXiv 长论文** | `论文/专题综述/` | 超长综述、专题论文集、arXiv 长文（>80 页） |
| **技术报告 / System Card** | `文档/报告与白皮书/` 或 `文档/技术资料/` | 公司发布的技术报告、安全报告、模型卡 |
| **大众图书 / 工程实用书** | `书籍/{主题}/` | EPUB、自助、科普、传记、工程经典、用户指南 |
| **报告**（政策/行业/白皮书） | `文档/报告与白皮书/` | AI Index、政策报告 |
| **讲义 / 课件** | `文档/课程与演示/` | Lecture Notes、MIT 6S191、CS50P |
| **行业标准** | `论文/行业标准/` | 标准编号、发布机构与规范条款明确的正式资料 |
| **一般规章 / 公文** | `文档/个人与行政/` 或既有专题目录 | 通知、办法、规定等非行业标准文件 |
| **未分类 PDF** | `文档/杂项收容/` | 已确认不是图书或论文，但文件名乱码、性质仍不明确 |
| **杂志** | `书籍/杂志/` | 已有目录，保留 |

## 二、判断顺序（重要）

**不要简单地用页数判断论文。** 按以下顺序判断：

### 第 1 步：PDF 元信息（首选）

用 PyMuPDF 读取 PDF 元数据：

```python
import fitz
doc = fitz.open(path)
meta = doc.metadata  # title, author, subject, keywords
first_page_text = doc[0].get_text()  # 首页文本
```

**论文特征**（任一即可判定为论文）：
- 首页含 arXiv ID（如 `arXiv:2603.20639v1`）
- 首页含 "Abstract" / "Keywords" / "References"
- 元数据 `subject` 含会议/期刊名（NeurIPS / ICML / ACL / Nature / IEEE 等）
- 首页含 DOI（`10.XXXX/...`）
- 首页含作者机构列表（"University of ..."、"Department of ..."）
- 双栏排版特征（用 `page.get_text("dict")` 检查列数）

**图书特征**（任一即可判定为图书）：
- 元数据含 ISBN（`978-X-XXX-XXXXX-X`）
- 首页或封页含出版社名（Springer / Cambridge / Oxford / MIT Press / O'Reilly / Wiley / Pearson / 机械工业 / 电子工业 / 人民邮电 等）
- 首页含 "Edition" / "2nd ed." / "Third Edition" / "第 X 版"
- 首页含 "Copyright Page" / "All rights reserved" + 出版社
- 首页含 "Table of Contents" + 多章节
- EPUB 格式（绝大多数是图书）

**报告特征**：
- 标题或首页含 "Report" / "System Card" / "Technical Report" / "White Paper" / "Index Report"
- 首页含发布机构（"Anthropic" / "OpenAI" / "Google AI" / "Stanford HAI" 等）+ 报告样式

**讲义特征**：
- 文件名或首页含 "Lecture Notes" / "讲义" / "Course Notes"
- 课程编号（CS50P / 6S191 / 6.006 / MIT / Stanford）
- 多 slides 排版（横向页面、大标题居中、要点列表）

**规章/公文特征**：
- 中文标题含《》/ "通知" / "办法" / "规定" / "印发"
- 首页含发文单位 + 文号

### 第 2 步：文件名启发式（次选）

如果元信息不明确，看文件名：

| 文件名模式 | 判定 |
|-----------|------|
| `XXXX.XXXXXvN.pdf` | arXiv 预印本 → 论文 |
| `sXXXX-XXX-XXXXX-X.pdf` | Springer 期刊文章 → 论文 |
| `1-s2.0-*.pdf` | ScienceDirect 文章 → 论文 |
| `作者_年份_短标题.pdf` | 论文或专著，需进一步判断 |
| `XXX-XX-XXXX-X.pdf` 数字串 | ISBN → 图书 |
| `(Z-Library).epub` / `(z-library.sk).epub` | 图书 |
| 含 "GTM" / "Graduate Texts" / "Springer Undergraduate" / "IOP ebooks" | 正式出版的教材/专著 → 书籍 |
| 含 "Handbook" / "Manual" / "Guide" / "Cheatsheet" | 工程书 → 书籍 |
| 含 "Lecture Notes" / "讲义" | 讲义 |

### 第 3 步：页数兜底（仅在元信息和文件名都不明确时使用）

如果上述两步都无法判断，按页数兜底：

| 页数 | 归类 | 说明 |
|-----|------|------|
| **> 80 页** | 图书或研究报告 | 长篇学术论文极罕见；结合出版信息归到 `书籍/`、`论文/专题综述/` 或 `文档/报告与白皮书/`，存疑时让用户决定 |
| **≤ 80 页** | 论文候选 | 默认归到 论文/ |

**注意**：页数是兜底手段，不能作为主判断。例如：
- 教材讲义可能 1000+ 页，但元信息会明确显示是讲义
- arXiv 长综述可能 60-90 页，但元信息会显示 arXiv ID
- 公司技术报告通常 50-300 页，但标题会明确含 "Report"

## 三、>80 页 PDF 的细分

对于超过 80 页的内容，进一步判断性质：

### 移到 `论文/专题综述/`（非图书的长篇学术内容）

- **长综述**：标题含 "Survey" / "Review" / "Foundations of"
- **专题论文集**：以论文集合而非连续章节构成，且没有独立图书出版信息
- **arXiv 长论文**：>50 页的 arXiv 预印本（保留在 `论文/专题综述/` 并重命名）

### 移到 `书籍/{主题}/`（大众/工程类）

- **EPUB 图书**：传记、自助、科普、商业、文学
- **大众科普**：标题含 "Popular Science" / "How to" / 友好入门
- **工程实用书**：Designing Data-Intensive Applications、SICP、Mastering Linux Shell Scripting
- **实用指南**：Fine-Tuning 指南、Prompting Guide、Cheatsheet、Handbook
- **学术专著与教材**：Springer、Cambridge、IOP、GTM 等正式出版物，包括研究生层次图书

### 边界情况处理

- **经典教材**（如 Strang 线性代数、Needham 可视化微分几何）：本科普及度高 → `书籍/`
- **研究生教材**（例如 Evans、Petersen、Springer GTM）：只要是完整出版的教材或专著 → `书籍/{主题}/`
- **公司技术报告 vs 政策报告**：两者均属于报告而非图书 → `文档/报告与白皮书/`；若是期刊/会议正式发表版本则归论文
- **哲学编著**：Cambridge Companion 系列 → `书籍/思想与人文/`（人文向，非研究向）

边界情况难以判断时，列出清单与用户讨论，不要擅自决定。

## 四、操作工作流

1. **扫描 书籍/ 下所有文件**：递归列出，排除 `.DS_Store`
2. **逐文件提取特征**：
   - 扩展名（EPUB/DJVU 直接归图书）
   - PDF 元数据 + 首页文本
   - 文件名启发式
   - 页数（兜底）
3. **生成分类报告**：列出每个文件的建议去向，对边界情况标注 `[需讨论]`
4. **报告给用户确认**：展示分流方案，让用户调整
5. **执行移动**：
   - 优先复用 `论文/`、`论文/专题综述/`、`论文/行业标准/`、`文档/报告与白皮书/`、`文档/课程与演示/`、`文档/杂项收容/` 等现有目录
   - 保持原子目录结构（论文/ 下子目录沿用 书籍/ 原类目名）
6. **更新 inventory.json**：移除已不存在的条目，添加新加入的图书 stub
7. **重跑 update_inventory.py** 生成新的 书籍清单.md

## 五、自动化脚本

阶段二的判断逻辑较复杂，建议用 Python 脚本实现：

```python
# 伪代码
def classify_pdf(path):
    meta, first_page = read_metadata_and_first_page(path)
    pages = get_page_count(path)

    # 第 1 步：元信息
    if has_arxiv_id(first_page): return "论文"
    if has_isbn(meta): return "图书"
    if has_publisher(first_page): return "图书"
    if is_report(first_page): return "报告"
    if is_lecture_notes(first_page, path): return "讲义"

    # 第 2 步：文件名
    if arxiv_id_in_filename(path): return "论文"
    if isbn_in_filename(path): return "图书"

    # 第 3 步：页数兜底
    if pages > 80: return "图书或报告（待人工确认）"
    return "论文"
```

实际执行时可以把分类结果输出为 JSON，让用户在 Markdown 表格里确认后再批量移动。

## 六、特殊情况

### 1. arXiv 预印本副本

某些 arXiv 文件实际是已收录为图书的预印本（如 Recht 的 *Patterns, Predictions, and Actions* 有 arXiv 版和正式版）。重命名 arXiv 时若发现与已有图书重复，标注 `(arXiv预印本)` 后缀，让用户决定是否归入 `书籍/待确认重复/`。详见 phase2.5。

### 2. 乱码文件名

文件名编码错乱（如 `<=AB@B>@_2011_Classical Mechanics.pdf`）无法根据文件名判断，**必须**用 PDF 元信息和首页文本判断。

### 3. 根目录散落文件

`书籍/` 根目录散落的文件（非任何子目录）也要参与分流。这部分文件在 inventory.json 中通常不被跟踪，但同样需要按类型分流。

### 4. inventory.json 元数据保留

对于留在 `书籍/` 的图书，inventory.json 中的 `cn_title`、`author`、`added_date` 等元数据要尽量保留。子目录改名时（如 `科技人文与数学` → `思想与人文` + `数学与物理`），脚本要按文件实际位置归类目，不要直接清空。

## 七、跳过分流的文件

以下文件**保留在 书籍/**，不参与分流：
- `书籍/inventory.json`、`书籍/书籍清单.md`、`书籍/translations.json`（元数据文件）
- `书籍/杂志/` 整个目录（已有专门的杂志分类）
- `书籍/待确认重复/` 整个目录（重复副本，单独处理）

分流后，`书籍/` 下应只剩真正的图书（EPUB、教材、专著、大众读物）+ 元数据 + 杂志 + 待确认重复。
