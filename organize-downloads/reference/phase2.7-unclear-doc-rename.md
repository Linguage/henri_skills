# 2.7 阶段：命名不明确文档的内容提取与改名

经过前几个阶段后，仍会剩下一批**文件名无法判断内容**的文档（如 `notes.pdf`、`____.pptx`、`config.txt`、`url.html`、`2_timeleft-clock.html`、`高手接话1739842635.epub`）。本阶段通过**提取文档内容**给出建议新名，同时检测是否含个人信息。

> 已完成识别的文件应归入本地暂存根目录（通常为 `Documents/`）下的 `书籍/`、`论文/`、`文档/`、`个人档案/` 或 `学位论文/`；仍无法确认者留在 Downloads 的待处理区。

## 一、什么算"命名不明确"

需要进入本阶段的文件特征：

| 模式 | 示例 |
|------|------|
| 文件名 ≤ 4 字符或纯符号 | `____.pptx`、`notes.pdf`、`url.html` |
| 文件名只有时间戳/编号 | `高手接话1739842635.epub`、`Subscriptions-0614.opml`、`ADA157917.pdf`（DTIC 文档号） |
| 缩写不明 | `YMW-Clock-1.0.html`、`MMP_TsingHua.pdf.mht`、`config.txt`、`2016_DIGRAPHS.pdf` |
| **重命名脚本的模板占位符** | `Author_2024_Title.pdf`、`clairejohnson_2011_Microsoft Word - CSSC_Final9.14.11.pdf`（上载者名 + Word 默认名） |
| 命名与内容严重不符 | `AI赋能.docx` 实际是铁路扣件项目摘要；`yan@TJU-ME_2012_SSReader Print..pdf` 实际是《可靠性数学引论》 |
| 文件名过于宽泛 | `工作汇报.key`、`Build with Andrew.docx`（不知道是介绍/教程/笔记） |
| Adobe 软件默认导出名 | `0007855_2020_486954_1_En_Print.indd.pdf`（InDesign）、`XXXX.dvi`、`SSReader Print..pdf`（超星） |
| 外文非中文非英文 | `2012_X МЕЖДУНАРОДНЫХ.pdf`（俄）、`朗道传 (朗道,Landau,Ландау,墨盟).pdf`、`2006_КОЛМОГОРОВ.pdf` |
| **看似规范实则错乱**（详见下方「⚠️ 命名错误的典型模式」） | `Eva_2004_Bernt Øksendal.pdf`（作者错位）、`Mary_2012_Universitext.pdf`（丛书名误为书名）、`Evans_2013_An Introduction to.pdf`（在 "to" 截断） |

**跳过的文件**：
- 文件名已经是 `作者_年份_标题` 格式（但需排除 `Author_XXXX_Title` 模板）
- 文件名含明确中文标题
- 已分类到具体专题子目录的文件

### ⚠️ 模板占位符的特殊识别

`Author_XXXX_Title.pdf` 这种格式看起来符合 `作者_年份_标题` 规范，但实际是**重命名脚本的占位符**（脚本无法识别作者和标题时的兜底输出）。识别要点：

```python
import re
def is_template_placeholder(name):
    """检测是否为重命名脚本的模板占位符。"""
    base = name.rsplit(".", 1)[0]
    # 严格匹配 Author_YYYY_Title 模板
    if re.match(r"^Author_\d{4}_Title$", base):
        return True
    # Word/PowerPoint/Excel 默认名 + 上载者前缀
    if re.search(r"_Microsoft\s+(Word|PowerPoint|Excel)\s*-\s*", name, re.I):
        return True
    # SSReader / 超星 默认名
    if "SSReader" in name or "Reader Print" in name:
        return True
    # Adobe InDesign 默认名（XXXX_YYYY_XXXXXXX_X_En_Print.indd.pdf）
    if re.match(r"^\d+_\d{4}_\d+_\d+_En_Print\.indd$", base):
        return True
    return False
```

这类文件**必须用第二章的内容提取或第三章的 OCR 识别**才能获得正确的新名。

### ⚠️ 命名错误的典型模式（看似规范实则错乱）

除"模板占位符"外，还有几种命名错误特别需要警惕——它们**看起来符合 `作者_年份_标题` 规范**，但实际信息错误。扫描时**不能仅靠文件名判断**，必须交叉验证首页内容。

#### 模式 1：丛书名误为书名

Springer/AMS 等出版社的丛书名被脚本提取为"标题"，导致多个不同书共用相同标题。

| 错误命名 | 实际应为 |
|---|---|
| `Mary_2012_Universitext.pdf` | `Koralov-Sinai_2012_Theory of Probability and Random Processes (2nd ed).pdf` |
| `Adem_2016_Graduate Texts in Mathematics.pdf` | `Petersen_2016_Riemannian Geometry (3rd ed, GTM 171).pdf` |
| `Krupka_2016_Atlantis Studies in Variational Geometry.pdf` | `Sardanashvily_2016_Noether Theorems - Applications in Mechanics and Field Theory.pdf` |

**检测启发式**：
```python
SERIES_NAMES = {
    "universitext", "graduate texts in mathematics", "gtm",
    "springer undergraduate texts", "undergraduate texts in mathematics",
    "atlantis studies", "studies in advanced mathematics",
    "encyclopedia of mathematics", "lecture notes in mathematics",
    "graduate studies in mathematics", "textbooks in mathematics",
    "springer series in", "cambridge studies in advanced mathematics",
    "mathematical association of america",
}
def is_likely_series_name(title):
    """检测标题是否疑似丛书名。"""
    return title.lower().strip() in SERIES_NAMES or any(
        s in title.lower() for s in SERIES_NAMES
    )
```

#### 模式 2：翻译者/编辑者误为作者

经典著作的"译本"中，译者或编者被脚本识别为"作者"，但实际作者另有其人。

| 错误命名 | 实际应为 |
|---|---|
| `Baker_2004_Collected Papers.pdf` | `Riemann_2004_Collected Papers (Baker等英译).pdf`（Baker 是译者） |
| `Krupka_2016_Atlantis Studies...pdf` | `Sardanashvily_2016_...`（Krupka 是丛书编辑） |
| `Sergey_2019_...pdf` | `Byrne_1847_欧几里得元素前六书 (Sergey 2019 重制).pdf`（Sergey 是重制者） |

**检测启发式**：
- 首页含 `Translated by` / `译文` / `译` / `Editor` / `Series Editor`
- 作者是常见名（Baker/Mary/John/Smith 等），但书是经典著作
- 首页出现的实际作者位置在标题下方（不是顶部）

#### 模式 3：作者和标题位置颠倒

`作者_年份_标题` 格式被脚本填充时，作者和标题字段被颠倒。

| 错误命名 | 实际应为 |
|---|---|
| `Eva_2004_Bernt Øksendal.pdf` | `Øksendal_2003_Stochastic Differential Equations (5th ed).pdf`（Eva 是误识别的前缀；Øksendal 才是作者，标题被完全丢失） |

**检测启发式**：
- 标题位置出现明显的人名（如 `Bernt Øksendal`、`John Smith`）
- 作者位置是简短单词（如 `Eva`、`Mary`、`Author`）
- 文件总长度异常短（标题只有 2 个词）

#### 模式 4：标题在介词/连词处被截断

PDF metadata.title 或脚本提取的标题在某些字符处被截断，留下半句话。

| 错误命名 | 实际应为 |
|---|---|
| `Evans_2013_An Introduction to.pdf` | `Evans_2013_An Introduction to Stochastic Differential Equations.pdf` |
| `Sergey_2019_THE FIRST SIX BOOKS OF.pdf` | `Byrne_1847_欧几里得元素前六书.pdf`（在 "OF" 处截断） |
| `Henrich_2019_...along the Mathematical.pdf` | `...along the Mathematical Journey.pdf`（在 "Mathematical" 处截断） |
| `Lee_2021_Logic - A Complete Introduction - Teach Yourself (Complete.pdf` | `...Teach Yourself).pdf`（在括号内截断） |

**检测启发式**：
```python
import re
TRAILING_PARTICLES = re.compile(
    r"[_\s]((to|of|the|and|or|in|for|on|with|a|an|from|by|as|at)\.pdf)$",
    re.I
)
UNCLOSED_PAREN = re.compile(r"\([^)]*\.pdf$")  # 括号未闭合
def is_likely_truncated(name):
    return bool(TRAILING_PARTICLES.search(name) or UNCLOSED_PAREN.search(name))
```

#### 模式 5：封面/版式描述误为书名

PDF 首页是版权页或封面说明，脚本提取的"标题"实际是封面图说明或版权描述。

| 错误命名 | 实际应为 |
|---|---|
| `Crombecque_2025_The cover design is associated with.pdf` | `AMS-Notices_2024_Vol 71 No 6.pdf`（这是 Notices of the AMS 杂志一期，Crombecque 是封面文章作者） |

**检测启发式**：
- 标题以 "The cover design" / "Copyright" / "Cover image" 等开头
- 标题是一句完整描述句，不是名词短语
- 文件实际是期刊/杂志时，应改为 `[刊名]_[年份]_Vol X No Y.pdf`

#### 模式 6：上载者/译者信息误为作者

用户从网盘/超星下载时，文件名常带上载者信息，被脚本当作作者。

| 错误命名 | 实际应为 |
|---|---|
| `DongZS_2006_SSReader Print..pdf` | `Horn_1985_Matrix Analysis (中文版).pdf`（DongZS 是译者，SSReader 是超星阅读器） |
| `yan@TJU-ME_2012_SSReader Print..pdf` | `曹晋华-程侃_可靠性数学引论 (高教社).pdf` |
| `clairejohnson_2011_Microsoft Word - CSSC_Final9.14.11.pdf` | `Moehle_2011_Case Studies of Seismic Performance of Tall Buildings.pdf` |

**检测启发式**：
- 作者位置含 `@` 符号（如 `yan@TJU-ME`）
- 作者位置是用户名风格（DongZS / clairejohnson / hzr_2018 等）
- 含 `SSReader Print` / `CamScanner` / `Microsoft Word - ` 等软件水印

### 处理建议（统一）

任何命中上述 6 类模式的文件都不要信任原文件名。先判断是否为扫描版：扫描版优先 OCR；普通电子版先读文本层，失败后再 OCR。识别后按以下顺序校验：

1. **丛书名 vs 书名**：从首页找 `Title:` 字样或大字号的书名，而非丛书名
2. **作者 vs 译者/编者**：从首页的 `by XXX` / `XXX 著` / `原著 XXX` 找真实作者
3. **作者位置 vs 标题位置**：作者应是 1-3 词的人名，标题应是名词短语
4. **截断检查**：标题不应以 `to/of/the/and` 等结尾，括号不应未闭合
5. **杂志 vs 书**：含 ISSN、Vol/No 字段的应是期刊，不是书

## 二、内容提取方法（按扩展名）

```python
import os, re, zipfile
from xml.etree import ElementTree as ET

def read_text(path, max_chars=500):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".md", ".txt", ".ps1", ".opml", ".vcf", ".html"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars * 3)[:max_chars]
    if ext == ".pdf":
        import fitz
        doc = fitz.open(path)
        # 已判定为扫描版时优先 OCR；普通电子版先读文本层。
        sample_count = min(5, doc.page_count)
        scan_votes = 0
        for pno in range(sample_count):
            page = doc[pno]
            if len(page.get_text().strip()) < 40 and page.get_images(full=True):
                scan_votes += 1
        scan_candidate = sample_count > 0 and scan_votes * 2 >= sample_count
        if scan_candidate:
            doc.close()
            return ocr_first_identifiable_page(path, max_chars=max_chars)
        t = ""
        for pno in range(min(5, doc.page_count)):
            page_text = doc[pno].get_text()
            if page_text.strip() and not _looks_like_garbled(page_text):
                t = page_text[:max_chars]
                break
        if not t:
            # 文本层为空或乱码 → 调用 OCR
            t = ocr_first_identifiable_page(path, max_chars=max_chars)
        doc.close()
        return t
    if ext == ".epub":
        with zipfile.ZipFile(path) as z:
            with z.open("META-INF/container.xml") as f:
                tree = ET.parse(f)
                ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
                opf = tree.find(".//c:rootfile", ns).get("full-path")
            with z.open(opf) as f:
                tree = ET.parse(f)
                ns = {"dc": "http://purl.org/dc/elements/1.1/"}
                title = tree.find(".//dc:title", ns)
                creator = tree.find(".//dc:creator", ns)
                return f"TITLE: {title.text if title is not None else '?'}\nAUTHOR: {creator.text if creator is not None else '?'}"
    if ext == ".docx":
        with zipfile.ZipFile(path) as z:
            with z.open("word/document.xml") as f:
                txt = f.read().decode("utf-8", errors="ignore")
                texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", txt)
                return " ".join(texts)[:max_chars]
    if ext == ".pptx":
        with zipfile.ZipFile(path) as z:
            slides = sorted([n for n in z.namelist()
                            if n.startswith("ppt/slides/slide") and n.endswith(".xml")])[:3]
            out = []
            for s in slides:
                with z.open(s) as f:
                    txt = f.read().decode("utf-8", errors="ignore")
                    texts = re.findall(r"<a:t[^>]*>([^<]*)</a:t>", txt)
                    out.append(" | ".join(texts))
            return "\n".join(out)[:max_chars]
    if ext == ".xlsx":
        with zipfile.ZipFile(path) as z:
            if "xl/sharedStrings.xml" in z.namelist():
                with z.open("xl/sharedStrings.xml") as f:
                    txt = f.read().decode("utf-8", errors="ignore")
                    texts = re.findall(r"<t[^>]*>([^<]*)</t>", txt)
                    return " | ".join(texts[:30])[:max_chars]
    if ext == ".mht":
        with open(path, "rb") as f:
            raw = f.read(8000)
        try:
            t = raw.decode("utf-8", errors="ignore")
        except Exception:
            t = raw.decode("gbk", errors="ignore")
        m = re.search(r"<title[^>]*>([^<]+)</title>", t, re.I)
        if m:
            return f"TITLE: {m.group(1)}\n\n{t[:300]}"
        return t[:max_chars]
    if ext == ".key":
        return "[Apple Keynote，无法直接读取，需手动打开]"
    return "[未识别扩展名]"


def _looks_like_garbled(text, sample_size=200):
    """检测文本是否为乱码（CID 编码或字体映射失败的产物）。
    
    特征：含大量孤立的单字符（空格分隔）、字符分布异常。
    """
    sample = text[:sample_size]
    if not sample.strip():
        return True
    # 若大部分字符是不可打印的孤立字符（"\\x / \\y" 模式），视为乱码
    import re
    tokens = sample.split()
    if len(tokens) > 10 and sum(1 for t in tokens if len(t) <= 2) / len(tokens) > 0.7:
        return True
    return False
```

## 三、扫描版 PDF 的 OCR 与视觉识别

扫描版候选应优先用 OCR 提取实际内容。普通电子版只有在文本层为空、乱码或 CID 编码异常时才回退到 OCR。OCR 无法获得足够信息时，再使用可用的视觉理解能力；若执行环境不具备视觉能力，则增加 OCR 页数、分辨率与语言组合。

### 1. macOS 上的 OCR 工具

#### Tesseract（推荐）

```bash
# 安装（Homebrew）
brew install tesseract tesseract-lang

# 支持的语言（163 种）
tesseract --list-langs
# 常用：chi_sim（简中）、chi_tra（繁中）、eng（英文）、jpn（日文）、fra（法语）
```

#### macOS Vision API（备选，识别精度更高）

通过 `shortcuts` 调用系统自带的 Vision 框架：

```bash
shortcuts run "Extract Text from Image" -i image.png
```

### 2. OCR 调用脚本

```python
import os, subprocess
import fitz

# 优先从 PATH 查找；macOS Homebrew 路径仅作为后备。
import shutil, tempfile
TESSERACT_BIN = shutil.which("tesseract") or "/opt/homebrew/bin/tesseract"
# 使用执行环境可写的临时目录；遇到 macOS TCC 限制时改用用户目录。
OCR_TMP = os.environ.get("OCR_TMP") or os.path.join(tempfile.gettempdir(), "ocr-books")


def ocr_pdf_page(pdf_path, pno, dpi=150, lang="chi_sim+eng"):
    """提取 PDF 指定页的图像并用 tesseract OCR。
    
    注意：必须用绝对路径调用 tesseract 二进制，避免 conda env 干扰。
    """
    os.makedirs(OCR_TMP, exist_ok=True)
    doc = fitz.open(pdf_path)
    page = doc[pno]
    pix = page.get_pixmap(dpi=dpi)
    img_path = os.path.join(OCR_TMP, f"ocr_p{pno}.png")
    pix.save(img_path)
    doc.close()
    
    result = subprocess.run(
        [TESSERACT_BIN, img_path, "stdout", "-l", lang],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout


def ocr_first_identifiable_page(pdf_path, max_chars=500):
    """OCR 多个页面，返回首个含有效文本的页面内容。
    
    扫描页码策略：[0, 1, 2, 4, 6] —— 首页常是封面（信息少），
    跳页扫到内页（书名页、目录页通常在前 5 页内）。
    """
    doc = fitz.open(pdf_path)
    pages = doc.page_count
    doc.close()
    
    for pno in [0, 1, 2, 4, 6]:
        if pno >= pages:
            break
        try:
            text = ocr_pdf_page(pdf_path, pno)
            # 过滤太短的（可能是空白页或 OCR 失败）
            if text and len(text.strip()) > 30:
                return text[:max_chars]
        except Exception as e:
            continue
    return "[OCR 无法识别有效内容]"
```

### 3. macOS 权限注意事项

- **TCC 限制**：macOS 隐私保护可能阻止 tesseract 访问 `/tmp/`、`/var/folders/...`
- **症状**：报错 `Image file \xXX cannot be read!` 或 `Leptonica Error in findFileFormat`
- **解决**：
  1. 把图片复制到用户目录下（如 `~/ocr_test/`）—— **最简单**
  2. 在「系统设置 → 隐私与安全性 → 完全磁盘访问权限」中添加 `/opt/homebrew/bin/tesseract`
  3. **必须用绝对路径**调用 tesseract 二进制，避免 `conda run` 干扰 PATH

### 4. OCR 失败后的处理

- 图形、表格、手写内容或复杂版面：先尝试 OCR；信息不足且环境具备视觉能力时，检查封面、书名页、目录页和正文样页。
- 不具备视觉能力：把 DPI 提高到 250-300，扩大页码样本并切换正确语言包；仍失败则标注“需人工查看”。
- 加密且无法读取的 PDF：不要绕过保护，标注“需人工查看”。
- 视觉识别结果不能单独作为改名依据，需与多页 OCR、PDF 元数据或现有书目信息交叉验证。

### 5. OCR 改名示例

```
原文件: 2009_Untitled.pdf (100p, 文本层全是乱码)
OCR 第1页: "线性代数五讲 / 中国 合肥 230026"
OCR 第2页: "内容简介：本书从现代数学, 尤其是模的观点..."
改名: 中科大_线性代数五讲.pdf
去向: 书籍/大文件/数学与物理/（扫描版数学教材）

原文件: Unknown_XXXX_Untitled.pdf (15p, 无文本层)
OCR 第1页: "医疗AI的认知双刃剑: 全球视角下的风险、监管与专家智识的存续"
改名: 2025_医疗AI的认知双刃剑.pdf
去向: _待分类_从书籍整理/文章/

原文件: LIU_2025_v0.3@220725.pdf (59p, 首页仅 "v0.3@220725")
OCR 第3页: "Contents / 1 Welcome / 6 Programme / Day Zero: Sunday 17th August, 2025"
OCR 第17页: "Welcome to the IAVSD2025!"
改名: IAVSD_2025_Symposium Programme (v0.3).pdf
去向: _待分类_从书籍整理/报告/
```

### 6. 识别质量验证

OCR 结果可能含错别字。改名前用以下规则校验：
- **关键词匹配**：标题中是否含明显的主题词（论文、报告、讲义、年份等）
- **作者词典**：识别的作者名是否在常见姓氏表（中英文）中
- **多页交叉验证**：如果首页 OCR 模糊，OCR 第 2-3 页找书名页/版权页
- **存疑标注**：识别置信度低时，文件名加 `(?)` 后缀，等用户复核

### 7. 外语文档的语言识别

部分文档是中文/英文之外的语言（俄语、日语、韩语、阿拉伯语等）。OCR 时**必须按文档实际语言选择 tesseract 语言包**，否则识别率极低或完全失败。

#### 7.1 通过文件名字符范围初判语言

```python
import re

def detect_language_by_filename(name):
    """根据文件名中的字符范围推测文档语言。"""
    if re.search(r"[\u0400-\u04FF]", name):  # 西里尔字母
        return "rus"
    if re.search(r"[\u3040-\u309F\u30A0-\u30FF]", name):  # 日文假名
        return "jpn"
    if re.search(r"[\uAC00-\uD7AF]", name):  # 韩文
        return "kor"
    if re.search(r"[\u0600-\u06FF]", name):  # 阿拉伯文
        return "ara"
    if re.search(r"[\u0590-\u05FF]", name):  # 希伯来文
        return "heb"
    if re.search(r"[\u0E00-\u0E7F]", name):  # 泰文
        return "tha"
    return None  # 通过文件名无法判断，需先提取文本
```

#### 7.2 文件名是 ASCII 但内容是外文

部分文件被预命名为 `Unknown_XXXX_*.pdf` 或纯数字（如 `2012_X МЕЖДУНАРОДНЫХ.pdf` 是俄文，但被命名时可能丢失了原始字符）。这时先**提取文本层**（前几页）→ 用 Unicode 字符范围检测语言：

```python
def detect_language_by_text(text):
    """根据文本字符范围推测语言。"""
    if not text or len(text) < 10:
        return None
    counts = {
        "rus": len(re.findall(r"[\u0400-\u04FF]", text)),
        "jpn_kana": len(re.findall(r"[\u3040-\u30FF]", text)),
        "kor": len(re.findall(r"[\uAC00-\uD7AF]", text)),
        "ara": len(re.findall(r"[\u0600-\u06FF]", text)),
        "heb": len(re.findall(r"[\u0590-\u05FF]", text)),
        "tha": len(re.findall(r"[\u0E00-\u0E7F]", text)),
        "cjk": len(re.findall(r"[\u4E00-\u9FFF]", text)),  # 中日韩统一表意
        "latin": len(re.findall(r"[A-Za-z]", text)),
    }
    # 排除中文（cjk 需结合其他字符判断是中文/日文汉字）
    sorted_langs = sorted(counts.items(), key=lambda x: -x[1])
    if sorted_langs[0][1] >= 10:
        return sorted_langs[0][0]
    return None
```

#### 7.3 多语言策略

如果是**双语对照**或**译文+原文**（如 Bessarab 朗道传：俄文原版+英文版权页），用 `+` 组合多个语言包：

```bash
# 俄文为主，兼带英文版权信息
tesseract image.png stdout -l rus+eng

# 中日混排
tesseract image.png stdout -l chi_sim+jpn

# 中英混排（最常见）
tesseract image.png stdout -l chi_sim+eng
```

**注意**：同时启用太多语言包会降低准确率并增加耗时。建议最多 2-3 个，按主要语言优先排序。

#### 7.4 命名建议（外文文档）

外文文档的命名建议**保留原文 + 加中文译注**，便于检索：

| 文档语言 | 命名格式 | 示例 |
|---------|---------|------|
| 俄文 | `作者_年份_中文译名 (俄文原版).pdf` | `Bessarab_2009_朗道传-Лев Ландау (俄文原版).pdf` |
| 日文 | `作者_年份_中文译名 (日文原版).pdf` | `小平邦彦_1981_我只会算术 (日文原版).pdf` |
| 论文集（外文） | `年份_中文译名 (原文种).pdf` | `2012_X国际柯尔莫哥洛夫研讨会论文集 (俄文).pdf` |

中文译名让用户在文件管理器中**一眼看出文档主题**，括号内保留原文方便溯源。

#### 7.5 真实案例

```
原文件: 2012_X МЕЖДУНАРОДНЫХ.pdf (文件名含西里尔字母)
语言: rus
OCR p0: "МИНИСТЕРСТВО ОБРАЗОВАНИЯ ... ТРУДЫ X МЕЖДУНАРОДНЫХ КОЛМОГОРОВСКИХ ЧТЕНИЙ"
识别为: 第 10 届国际柯尔莫哥洛夫研讨会论文集（雅罗斯拉夫尔 + 莫斯科大学，2012）
改名: 2012_X国际柯尔莫哥洛夫研讨会论文集 (俄文).pdf

原文件: 朗道传 (朗道,Landau,Ландау,墨盟) (Z-Library).pdf (文件名混合中俄)
语言: rus
OCR p0: "Лев / Роман-биография / Майя Бессараб"  
OCR p2 (英文): "Originally published in Russian under the title Bessarab Майя. Лев Ландау..."
识别为: Bessarab 2009《Лев Ландау. Роман-биография》（朗道传记，俄文原版）
改名: Bessarab_2009_朗道传-Лев Ландау (俄文原版).pdf
```


## 四、个人信息检测

提取文本后，用正则扫描敏感模式：

```python
import re
PII_PATTERNS = re.compile(
    r"(身份证|护照|银行卡|账号|密码|手机号"
    r"|1[3-9]\d{9}"           # 中国手机号
    r"|token|api[_-]?key|secret|passport"
    r"|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)",  # email
    re.I
)

if PII_PATTERNS.search(text):
    flag = "⚠️ 含敏感信息，建议移到 个人档案/"
```

**注意**：Springer/Safari 等网站的 `sharing_token` URL 参数不是个人敏感信息，需要人工甄别。

## 五、改名规则

### 1. 内容识别后改名格式

| 内容类型 | 命名格式 | 示例 |
|---------|---------|------|
| PDF 论文/报告 | `作者_年份_中文标题.pdf` | `Prism_2026_Fibonacci数列深入研究报告.pdf` |
| EPUB 图书 | `作者_中文书名.epub`（中文书保留原名） | `乔向阳_高手接话.epub` |
| 课堂笔记 | `作者 (机构)-课程名笔记.pdf` | `Huy Nguyen (CMU)-ML课堂笔记.pdf` |
| PPT 主题 | `主题名.pptx` | `日本咖啡艺术介绍.pptx` |
| 配置文件 | `工具名-配置-变体名.ext` | `Ghostty配置-Coffee Theme.txt` |
| 网页存档（MHT） | `来源-标题.mht` | `Reddit-r_China_irl-中国历史时空示意图.mht` |
| 订阅列表（OPML） | `工具名-订阅类型-日期.opml` | `NetNewswire-RSS订阅-0614.opml` |

### 2. 改名工作流

1. **扫描目标文件**：用启发式筛出"命名不明确"的文件
2. **提取内容**：按扩展名读取首页/前几页文本
3. **扫描版优先 OCR**：普通电子版文本提取失败时再 OCR；OCR 不足时按第三章使用视觉或扩大 OCR 范围
4. **正则检测 PII**：标注敏感文件
5. **生成建议清单**：列出每个文件的提取内容 + 建议新名 + 建议去向
6. **用户确认**：展示清单，等用户调整（特别是改名涉及主观判断）
7. **执行改名 + 移动**：用户确认后批量执行
8. **更新 inventory.json**（如果文件移入或移出 `书籍/`）

## 六、典型场景

### 场景 1：泛名文件（notes.pdf）

```
原文件: notes.pdf
提取: "Introduction to Machine Learning Class Notes\nHuy Nguyen\nPhD Student, HCI Institute, CMU"
改名: Huy Nguyen (CMU)-ML课堂笔记.pdf
去向: 书籍/AI工程与实践/  或  文档/AI与工具笔记/
```

### 场景 2：纯符号文件名（____.pptx）

```
原文件: ____.pptx
提取: "日本の珈琲芸術: 序章 | 一杯の珈琲を超えた儀式..."
改名: 日本咖啡艺术介绍.pptx
去向: 文档/生活与杂项/（保留原位置）
```

### 场景 3：命名与内容严重不符（AI赋能.docx）

```
原文件: AI赋能.docx
提取: "非稳态热力交变荷载下铁路扣件系统约束性能劣化演进机制及匹配控制方法 项目摘要..."
→ 标注：文件名误导，实际是铁路研究项目摘要
改名: 铁路扣件系统约束性能劣化-项目摘要.docx
去向: 学位论文/铁路工程研究/  而非 文档/AI与工具笔记/
```

### 场景 4：含个人订阅信息（Subscriptions-0614.opml）

```
原文件: Subscriptions-0614.opml
提取: "<?xml ... <title>Subscriptions-0614.opml</title> ... <outline text='个人博客'>"
改名: NetNewswire-RSS订阅-0614.opml
去向: 个人档案/订阅与书签/  （含个人订阅偏好）
```

### 场景 5：仅含分享 token 的非敏感文件

```
原文件: An Interview with Maryna Viazovska.mht
提取: 含 Springer sharing_token=NXzStxki2Q...
PII 检测: ⚠️ 命中 token 关键词
人工甄别: 是文章访问令牌，非个人敏感 → 标注"非敏感"并保留
```

## 七、与其他阶段的关系

- **前置**：本阶段在 phase2（类型分流）和 phase2.5（PDF 重命名）之后执行，此时已有明确命名的文件已被处理
- **并行**：可与 phase3（书籍主题归类）并行，因为本阶段处理的多是 `文档/` 下的杂项
- **后续**：发现的个人信息文件移到 `个人档案/`（参考 directory-template.md 的个人档案子目录结构）

## 八、自动化输出

批量处理时复用本文件第二、三章的提取函数，输出 JSON 或 Markdown 报告；每项至少包含原路径、内容摘要、建议新名、建议去向、识别方式、置信度和 PII 标记。报告经用户确认后再执行改名或移动。
