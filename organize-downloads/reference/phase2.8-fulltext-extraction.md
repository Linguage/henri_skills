# 2.8 阶段：全文提取与元数据整合（可选）

经过前几个阶段后，论文已按主题归位、文件名已规范。本阶段把每个 PDF 的**完整全文**与**结构化元信息**（来自 Zotero 或手工 papers_metadata.json）整合为一个 JSON 数据库，便于后续检索、综述生成、RAG 等场景。

> 本阶段的 `论文/` 指本地暂存根目录（通常为 `Documents/`）中的论文库。全文提取产物应放在任务临时目录或明确的检索项目目录中，验证后清理无须长期保留的中间文件。

> **可选阶段**：仅当需要程序化处理全文时才执行（如构建检索系统、生成文献综述、批量翻译摘要等）。如果只是为了人眼浏览，跳过本阶段即可。

## 一、何时做全文提取

| 场景 | 是否需要 |
|------|---------|
| 人工浏览论文 | ❌ 跳过 |
| 生成文献综述初稿 | ✅ 需要 |
| 构建 RAG 检索系统 | ✅ 需要 |
| 跨论文主题聚类 | ✅ 需要 |
| 批量翻译摘要 / 提取关键词 | ✅ 需要 |
| 与 Zotero 同步校验 | ✅ 需要 |
| 仅仅是文件归档 | ❌ 跳过 |

**判断原则**：如果你需要"问问题给一组论文"，就需要全文提取。

## 二、PDF 全文提取方法

### 1. PyMuPDF 按页提取（推荐）

```python
import fitz

def extract_fulltext(pdf_path):
    """提取 PDF 完整全文，按页存储。
    
    返回:
        pages_text: list[str]，每页一个元素（page 0 = pages_text[0]）
        full_text: str，所有页拼接（页间空行分隔）
        n_pages: int，总页数
    """
    doc = fitz.open(pdf_path)
    n_pages = doc.page_count
    pages_text = [doc[p].get_text() for p in range(n_pages)]
    doc.close()
    full_text = "\n\n".join(pages_text)
    return pages_text, full_text, n_pages
```

### 2. 性能与体积参考

实测数据（2026 年）：

| 目录 | 论文数 | 总页数 | 总字符 | JSON 大小 |
|------|-------:|-------:|-------:|----------:|
| `论文/铁路与交通工程/` | 23 | 360 | 1,087,986 | 2.3 MB |
| `论文/AI与铁路动力学/` | 96 | 2,074 | 6,337,116 | 13.8 MB |

**经验值**：每页平均 500-600 字符（双栏学术论文），10 MB JSON 大约对应 70-80 篇论文。

### 3. 何时提取会失败

- **扫描版 PDF**（无文本层）：返回空字符串。这时需要先做 OCR（见 phase2.7 第三章）才能获得文本
- **加密 PDF**：会报错。先用 `qpdf --decrypt input.pdf output.pdf` 解密
- **图片为主、文字为辅的 PPTX 转 PDF**：文本层稀疏，提取出来不完整

### 4. 与首页提取（phase2.7）的区别

| 维度 | phase2.7（首页提取） | phase2.8（全文提取） |
|------|---------------------|---------------------|
| 用途 | 改名/识别 | 检索/综述/RAG |
| 提取范围 | 前 3 页前 3000 字符 | **所有页** |
| 输出 | 内嵌在改名建议里 | 独立的 JSON 文件 |
| 必需性 | 必需（用于识别） | 可选 |

## 三、整合 JSON 输出格式

每个论文子目录输出一个 `_metadata_integrated.json`，结构如下：

```json
{
  "_meta": {
    "description": "论文全文数据库（含元信息 + PDF 完整全文）",
    "total_papers": 23,
    "total_pages": 360,
    "total_chars": 1087986,
    "fields": {
      "file": "文件名",
      "path": "完整路径",
      "n_pages": "PDF 页数",
      "n_chars": "全文总字符数",
      "pages_text": "按页存储的文本数组",
      "full_text": "完整拼接的全文",
      "metadata": "结构化元信息（来源：Zotero 或 papers_metadata.json）"
    }
  },
  "papers": [
    {
      "file": "Gou_2023_Vibration Energy Transmission.pdf",
      "path": "/Users/.../论文/铁路与交通工程/Gou_2023_....pdf",
      "n_pages": 16,
      "n_chars": 45000,
      "pages_text": ["第1页文本", "第2页文本", "..."],
      "full_text": "第1页文本\n\n第2页文本\n\n...",
      "extracted_doi": "10.1016/j.engstruct.2023.117019",
      "match_method": "doi",
      "metadata": {
        "title": "Vibration energy transmission in high-speed train-track-bridge coupled systems",
        "cn_title": "高速列车-轨道-桥梁耦合系统的振动能量传输",
        "first_author": "Gou",
        "authors": "Hongye Gou, Hao Gao, Xinlin Ban, Xin Meng, Yi Bao",
        "year": "2023",
        "journal": "Engineering Structures",
        "doi": "10.1016/j.engstruct.2023.117019",
        "category": "子主题分类（可选）",
        "abstract": "完整摘要",
        "keywords": ["关键词1", "关键词2"],
        "pages": 16,
        "zotero_key": "VGUB9VLP（如果有）"
      }
    }
  ]
}
```

### 字段说明

| 字段 | 来源 | 必需 |
|------|------|------|
| `file`, `path` | 文件系统 | ✅ |
| `n_pages`, `n_chars` | PyMuPDF | ✅ |
| `pages_text`, `full_text` | PyMuPDF 全文提取 | ✅ |
| `extracted_doi` | 从 PDF 首页正则提取 | 可选 |
| `match_method` | 元数据匹配方式 | 可选 |
| `metadata.title/first_author/year/journal/doi` | Zotero 或 papers_metadata.json | 推荐 |
| `metadata.cn_title` | 手工或翻译 | 可选 |
| `metadata.abstract` | Zotero（自动同步） | 推荐 |
| `metadata.category` | 手工分类 | 可选 |

## 四、元数据来源

### 1. Zotero 数据库（首选）

如果用户有 Zotero 库，从 `zotero.sqlite` 提取：

```python
import sqlite3, shutil

# Zotero 运行时数据库被锁，需要先复制
shutil.copy("/path/to/zotero.sqlite", "/tmp/zotero_copy.sqlite")

conn = sqlite3.connect("/tmp/zotero_copy.sqlite")
# 字段映射：title=110, date=14, publicationTitle=12, abstractNote=17, DOI=1
# 详见 Zotero 数据库 schema
```

**匹配策略**（按优先级）：
1. **DOI 完全匹配**（最准确，从 PDF 首页提取 DOI，跟 Zotero 的 DOI 字段对比）
2. **标题归一化匹配**（去除空格/标点/括号后比较）
3. **作者+年份+期刊**（最后兜底）

### 2. 已有 papers_metadata.json（次选）

如果某个目录已有手工整理的 `papers_metadata.json`（含中文译名、子主题分类），直接按 `filename` 字段匹配：

```python
with open("papers_metadata.json") as f:
    meta_db = json.load(f)
meta_idx = {p["filename"]: p for p in meta_db["papers"]}
# 按 filename 直接查表
```

### 3. 手工录入（兜底）

如果 Zotero 和现有 JSON 都没有，可以从 PDF 首页手工录入：
- 标题：通常在第一页最显眼位置
- 作者：标题下方一行
- 年份：版权信息或Received/Accepted日期
- 期刊：页眉/页脚

## 五、匹配工作流

```python
# 三轮匹配
for paper in papers:
    # 第 1 轮：DOI 完全匹配
    if paper["extracted_doi"] and paper["extracted_doi"] in zotero_doi_index:
        paper["match_method"] = "doi"
        paper["metadata"] = zotero_doi_index[paper["extracted_doi"]]
        continue
    
    # 第 2 轮：标题模糊匹配
    norm_title = normalize(paper["file_parsed"]["title"])
    if norm_title in zotero_title_index:
        paper["match_method"] = "title_fuzzy"
        paper["metadata"] = zotero_title_index[norm_title]
        continue
    
    # 第 3 轮：手动匹配清单（针对 OCR 失败、DOI 缺失等特殊情况）
    for prefix, zotero_id in MANUAL_MATCH_LIST:
        if paper["file"].startswith(prefix):
            paper["match_method"] = "manual"
            paper["metadata"] = zotero_by_id[zotero_id]
            break
```

### 同篇不同版本的处理

同一篇论文的不同版本（如 arXiv 预印本 + 正式版 + Final manuscript）会匹配到同一个 Zotero 条目。建议：
- **都保留**：每个版本一个 JSON 条目，metadata 字段指向同一个 Zotero 记录
- **文件名加后缀区分**：`Liu_2020_..._ steel-concrete bridge (JSV 正式版).pdf` vs `(早期版).pdf`

## 六、与其他阶段的关系

| 阶段 | 关系 |
|------|------|
| phase2.5（PDF 重命名） | 前置：必须先有规范的文件名才能匹配元数据 |
| phase2.7（命名不明确） | 前置：必须先识别内容才能匹配 |
| phase3（书籍主题归类） | 平行：本阶段针对论文目录，phase3 针对书籍目录 |
| phase4（inventory 维护） | 无关：inventory 只跟踪书籍，本阶段独立 |

## 七、自动化脚本

完整的整合脚本流程：

```bash
# 1. 复制 Zotero 数据库（避免锁定）
cp ~/Zotero/zotero.sqlite /tmp/zotero_copy.sqlite

# 2. 提取 Zotero 条目到 JSON
conda run -n henri_env python .claude/skills/organize-downloads/scripts/extract_zotero.py \
    --db /tmp/zotero_copy.sqlite \
    --output /tmp/zotero_entries.json

# 3. 对论文目录做全文提取 + 元数据匹配
conda run -n henri_env python .claude/skills/organize-downloads/scripts/integrate_metadata.py \
    --dir 论文/{子目录} \
    --zotero /tmp/zotero_entries.json \
    --output 论文/{子目录}/_metadata_integrated.json

# 4. 模糊匹配（第一轮未匹配的）
conda run -n henri_env python .claude/skills/organize-downloads/scripts/match_fuzzy.py \
    --json 论文/{子目录}/_metadata_integrated.json

# 5. 手动匹配（如有需要，编辑 MANUAL_MATCH 清单）
# 6. 重跑 integrate_metadata 输出最终 JSON
```

## 八、典型场景

### 场景 1：整理一个新论文目录

```
原状态: 论文/新主题/ 下有 30 篇论文，文件名已规范化
↓
步骤 1: 复制 Zotero 数据库
步骤 2: 提取 Zotero 条目
步骤 3: 全文提取 + 元数据匹配
步骤 4: 输出 _metadata_integrated.json
↓
新状态: 论文/新主题/_metadata_integrated.json 含 30 篇全文 + 元信息
```

### 场景 2：补充全文到已有 inventory

如果之前的 `_metadata_integrated.json` 只有首页文本（如 v1.0），重跑 integrate_metadata.py 升级到全文版（v2.0）：

```python
# 保留原有的 zotero 匹配信息，仅替换/添加 full_text 字段
for paper in existing_data:
    pages_text, full_text, n_pages = extract_fulltext(paper["path"])
    paper["pages_text"] = pages_text
    paper["full_text"] = full_text
    paper["n_pages"] = n_pages
    paper["n_chars"] = len(full_text)
    if "first_pages_text" in paper:  # 删除旧字段
        del paper["first_pages_text"]
```

### 场景 3：跨目录统一检索

把多个论文子目录的 JSON 合并为一个总索引：

```python
import json, glob

master = {"_meta": {}, "papers": []}
for path in glob.glob("论文/*/_metadata_integrated.json"):
    data = json.load(open(path))
    sub_dir = path.split("/")[-2]
    for p in data["papers"]:
        p["sub_dir"] = sub_dir  # 加上来源标记
    master["papers"].extend(data["papers"])

master["_meta"]["total_papers"] = len(master["papers"])
json.dump(master, open("论文/_master_index.json", "w"), ensure_ascii=False, indent=2)
```
