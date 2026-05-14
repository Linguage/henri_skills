#!/usr/bin/env python3
"""批量提取 PDF 论文元数据并以「作者_年份_标题」格式重命名。

改进版：多策略作者/标题提取、中文支持、扫描件检测、回退保护。

Usage:
    conda run -n henri_env python rename_pdfs.py [--dir PATH] [--rename] [--json PATH] [--all] [--target-unknown]
"""

import fitz
import re
import sys
import json
import os
import shutil
import argparse
from pathlib import Path

_COMMON_SURNAMES = frozenset("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏窦章苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卡齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊甄家封芮储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴郁胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾母沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公")


JUNK_LINES = {
    'issn', 'doi', 'isbn', 'arxiv', 'preprint', 'draft', 'conference',
    'proceedings', 'vol.', 'volume', 'number', 'pages', 'chapter',
    'contents', 'table of', 'index', 'bibliography', 'references',
    'microsoft word', 'microsoft powerpoint', 'ssreader print',
    'pagination_cover', '.dvi', '.pptx', '.docx',
}

FALSE_AUTHORS = {
    'edition', 'university', 'providence', 'cliffs', 'kalamazoo',
    'maryland', 'baltimore', 'society', 'press', 'publisher',
    'college', 'institute', 'department', 'faculty', 'school',
    'springer', 'wiley', 'cambridge', 'oxford', 'elsevier',
    'pagination', 'cover', 'print', 'online',
}

CN_FALSE_AUTHORS = {
    '以下是对', '在纷繁复', '度增强到', '众所皆知', '对于', '接着',
    '本文', '摘要', '关键词', '目录', '前言', '引言', '附录',
    '概述', '简介', '背景', '正文', '结论', '总结', '参考文献',
    '第一章', '第二章', '第三章', '第四章', '第五章',
}

JUNK_PREFIXES = [
    r'^\d+$',
    r'^page\s+\d+',
    r'^fig\.?\s*\d+',
    r'^table\s+\d+',
    r'^abstract\s*$',
    r'^keywords?\s*:',
    r'^\[\d+\]',
    r'^\*+',
    r'^received\s*:',
    r'^accepted\s*:',
    r'^published',
    r'^copyright',
    r'^\d+\s+\w+\s+\d{4}',  # date like "May 14, 2026"
    r'^vol\.?\s*\d+',
    r'^no\.?\s*\d+',
    r'^pp\.?\s*\d+',
    r'^https?://',
    r'^www\.',
]


def _is_junk_line(line):
    lower = line.lower().strip()
    if len(lower) < 3:
        return True
    for junk in JUNK_LINES:
        if junk in lower and len(lower) < len(junk) + 20:
            return True
    for pat in JUNK_PREFIXES:
        if re.match(pat, lower):
            return True
    return False


def extract_lastname(author_str):
    if not author_str or not author_str.strip():
        return None
    author_str = author_str.strip()
    first = re.split(r'[;，;,]', author_str)[0].strip()
    for skip in ['arXiv', 'Elsevier', 'Springer', 'VTeX', 'LaTeX', 'IEEE',
                 'Unknown', 'anonymous', 'CamScanner', 'ssreader', 'Pagination',
                 '0007855', '0009172']:
        if skip.lower() in first.lower():
            return None
    first = re.sub(r'[\d*†‡§¶]+', '', first).strip()
    first = re.sub(r'\s*\(.*?\)\s*$', '', first).strip()
    first = re.sub(r'\s*(Author|author|编辑|编著|编译|译)\s*$', '', first).strip()
    if re.match(r'^[\u4e00-\u9fff]', first):
        m = re.match(r'^([\u4e00-\u9fff]{1,4})', first)
        if m:
            return m.group(1)
        return first[:2]
    parts = first.split()
    parts = [p for p in parts if not re.match(r'^[A-Z]\.?$', p)]
    if len(parts) >= 2:
        return parts[-1].strip('.,')
    if parts:
        return parts[0].strip('.,')
    return None


def extract_authors_from_text(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    priority_patterns = [
        (r'author[s]?\s*[:：]\s*(.+)', 0),
        (r'by\s+([A-Z][a-z]+\s+[A-Z][a-zA-Z\-]+)', 0),
        (r'作者\s*[:：]\s*([\u4e00-\u9fff]{2,4})', 0),
        (r'编辑\s*[:：]?\s*([\u4e00-\u9fff]{2,4})', 0),
        (r'([\u4e00-\u9fff]{2,4})\s*著', 0),
        (r'([\u4e00-\u9fff]{2,4})\s*译', 0),
    ]

    secondary_patterns = [
        (r'^([A-Z][a-z]+\s+[A-Z][a-zA-Z\-]+)\s*[,;，·†‡*]', 1),
        (r'^([A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-zA-Z\-]+)\s*[,;，·†‡*]', 1),
        (r'^([A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z]\.?)\s*[,;，·†‡*]', 1),
        (r'^([\u4e00-\u9fff]{2,4})\s*[,;，·、1\d†‡*]', 1),
        (r'^([\u4e00-\u9fff]{2,4}(?:\s*[\u4e00-\u9fff]{2,4})+)\s*[,;，·]', 1),
        (r'^([A-Z][a-z]+)\s*[,;，·†‡*]', 1),
    ]

    def validate_name(name):
        if not name:
            return None
        if name.lower() in FALSE_AUTHORS:
            return None
        for cn_false in CN_FALSE_AUTHORS:
            if cn_false in name:
                return None
        if re.match(r'^[\u4e00-\u9fff]', name):
            if len(name) < 2 or len(name) > 4:
                return None
            if name[0] not in _COMMON_SURNAMES:
                return None
        return name

    for pat, grp in priority_patterns:
        for line in lines[:20]:
            m = re.search(pat, line)
            if m:
                candidate = m.group(grp).strip()
                name = extract_lastname(candidate)
                validated = validate_name(name)
                if validated:
                    return validated

    for i, line in enumerate(lines[:15]):
        if _is_junk_line(line):
            continue
        for pat, grp in secondary_patterns:
            m = re.search(pat, line)
            if m:
                candidate = m.group(grp).strip()
                name = extract_lastname(candidate)
                validated = validate_name(name)
                if validated:
                    return validated

    return None


def extract_title_from_text(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return None

    for line in lines[:10]:
        if _is_junk_line(line):
            continue
        if len(line) < 5:
            continue
        if re.match(r'^[A-Z\s\d]+$', line) and len(line) > 5:
            return line
        if re.match(r'^[\u4e00-\u9fff]', line) and len(line) > 4:
            return line
        if re.match(r'^[A-Z][a-zA-Z\s\-:,.]+', line) and len(line) > 8:
            return line

    for line in lines[:10]:
        if _is_junk_line(line):
            continue
        if len(line) >= 5:
            return line

    return None


def extract_year(text, creation_date=None, filename=None):
    # Infer from arXiv-style filename (e.g. 2603.20639v1.pdf → 2026)
    if filename:
        m = re.match(r'^(\d{2})(\d{2})\.\d{4,5}', os.path.basename(filename))
        if m and 1 <= int(m.group(2)) <= 12:
            return "20" + m.group(1)
    pub = re.search(r'Published\s+online:?\s+\d+\s+\w+\s+(20\d{2})', text)
    if pub:
        return pub.group(1)
    accepted = re.search(r'Accepted:?\s+\d+\s+\w+\s+(20\d{2})', text)
    if accepted:
        return accepted.group(1)
    cn_pub = re.search(r'(20\d{2})\s*年', text)
    if cn_pub:
        return cn_pub.group(1)
    years = re.findall(r'\b(20[0-2]\d)\b', text)
    if years:
        recent = [y for y in years if int(y) >= 2020]
        return max(recent, key=int) if recent else max(years, key=int)
    if creation_date:
        m = re.search(r'(20\d{2})', creation_date)
        if m:
            return m.group(1)
    return None


def sanitize_title(title, max_len=80):
    if not title:
        return None
    title = re.sub(r'[:/\\]', ' -', title)
    title = re.sub(r'[<>?*|"]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'\.pdf$', '', title, flags=re.I)
    if len(title) > max_len:
        if re.search(r'[\u4e00-\u9fff]', title):
            title = title[:max_len]
        else:
            title = title[:max_len].rsplit(' ', 1)[0]
    return title if title else None


def needs_rename(filename):
    if re.match(r'^Unknown_', filename):
        return True
    if re.match(r'^[A-Z][a-zA-Z\-\u4e00-\u9fff]+_(?!XXXX)\d{4}_', filename):
        return False
    if re.match(r'^[\u4e00-\u9fff]', filename):
        return False
    patterns = [
        r'^\d{4}\.\d{4,5}',
        r'^1-s2\.0-',
        r'^s\d+-\d+-\d+-\d+',
        r'^[a-f0-9]{8,}\.pdf$',
        r'^\d{5,}\.pdf$',
        r'^book_\d',
        r'^978-?\d',
        r'^ssrn',
        r'^[A-Z][a-zA-Z\-]+_XXXX_',  # Invalid year placeholder
    ]
    return any(re.match(p, filename, re.I) for p in patterns)


def process_pdf(filepath):
    with fitz.open(filepath) as doc:
        meta = doc.metadata
        text = ""
        for i in range(min(5, len(doc))):
            text += doc[i].get_text()

    has_text = len(text.strip()) > 50

    meta_author = meta.get('author', '') or ''
    meta_title = meta.get('title', '') or ''

    for skip in ['None', '.dvi', 'book.dvi', 'doi:', 'sbornik']:
        if meta_title.strip().lower() == skip.lower() or meta_title.strip() == skip:
            meta_title = ''
            break

    year = extract_year(text, meta.get('creationDate', ''), filename=filepath)
    year_str = year if year else "XXXX"

    lastname = None
    if meta_author:
        lastname = extract_lastname(meta_author)
    if not lastname and has_text:
        lastname = extract_authors_from_text(text)

    title = None
    if meta_title and len(meta_title) > 3 and not _is_junk_line(meta_title):
        title = meta_title
    if not title and has_text:
        title = extract_title_from_text(text)

    title = sanitize_title(title)

    if not has_text and not title:
        return {
            'file': os.path.basename(filepath),
            'author': meta_author,
            'first_author_lastname': lastname or '(no author)',
            'year': year_str,
            'title': '(scanned - no text)',
            'suggested_name': None,
            'has_text': False,
        }

    if not lastname:
        lastname = None
    if not title:
        title = 'Untitled'

    if lastname:
        new_name = f"{lastname}_{year_str}_{title}.pdf"
    else:
        new_name = f"{year_str}_{title}.pdf"
    return {
        'file': os.path.basename(filepath),
        'author': meta_author,
        'first_author_lastname': lastname,
        'year': year_str,
        'title': title,
        'suggested_name': new_name,
        'has_text': has_text,
    }


def main():
    parser = argparse.ArgumentParser(description='PDF paper renamer (improved)')
    parser.add_argument('--dir', default='.', help='Directory with PDFs')
    parser.add_argument('--rename', action='store_true', help='Execute renames')
    parser.add_argument('--dry-run', action='store_true', help='Show proposed renames without executing')
    parser.add_argument('--json', metavar='PATH', help='Output results as JSON')
    parser.add_argument('--all', action='store_true', help='Process all PDFs')
    parser.add_argument('--target-unknown', action='store_true',
                        help='Only process files starting with Unknown_')
    args = parser.parse_args()

    directory = args.dir
    pdfs = sorted([f for f in os.listdir(directory) if f.lower().endswith('.pdf')])

    if args.target_unknown:
        pdfs = [f for f in pdfs if f.startswith('Unknown_')]
    elif not args.all:
        pdfs = [f for f in pdfs if needs_rename(f)]

    results = []
    skipped = 0
    for pdf in pdfs:
        path = os.path.join(directory, pdf)
        try:
            info = process_pdf(path)
            if info['suggested_name'] is None:
                print(f"{info['file']}")
                print(f"  → SKIP (scanned/no text)")
                skipped += 1
                continue
            results.append(info)
            print(f"{info['file']}")
            print(f"  → {info['suggested_name']}")
            print(f"    author={info['first_author_lastname']}  year={info['year']}  has_text={info['has_text']}")
        except Exception as e:
            results.append({'file': pdf, 'error': str(e)})
            print(f"{pdf} → ERROR: {e}")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nJSON saved: {args.json}")

    if skipped:
        print(f"\nSkipped (scanned/no text): {skipped}")

    if args.dry_run and not args.rename:
        print("\n[Dry run] Use --rename to execute.")
    elif args.rename:
        renamed = 0
        errors = 0
        for info in results:
            if 'error' in info:
                continue
            if info['suggested_name'] is None:
                continue
            src = os.path.join(directory, info['file'])
            dst = os.path.join(directory, info['suggested_name'])
            if src == dst:
                continue
            if os.path.exists(dst):
                base, ext = os.path.splitext(dst)
                counter = 2
                while os.path.exists(f"{base}_{counter}{ext}"):
                    counter += 1
                dst = f"{base}_{counter}{ext}"
            try:
                shutil.move(src, dst)
                print(f"  renamed: {info['file']} → {os.path.basename(dst)}")
                renamed += 1
            except Exception as e:
                print(f"  ERROR: {e}")
                errors += 1
        print(f"\nRenamed: {renamed}, Errors: {errors}")


if __name__ == '__main__':
    main()
