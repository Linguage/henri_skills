#!/usr/bin/env python3
"""批量提取 PDF 论文元数据并以「作者_年份_标题」格式重命名。

Usage:
    conda run -n henri_env python rename_pdfs.py [--dir PATH] [--rename] [--json PATH]
"""

import fitz
import re
import sys
import json
import os
import argparse
from pathlib import Path


def extract_lastname(author_str):
    if not author_str or not author_str.strip():
        return "Unknown"
    author_str = author_str.strip()
    first = re.split(r'[;]', author_str)[0].strip()
    for skip in ['arXiv', 'Elsevier', 'Springer', 'VTeX', 'LaTeX', 'IEEE']:
        if skip.lower() in first.lower():
            return "Unknown"
    parts = first.split()
    if len(parts) >= 2:
        return parts[-1].strip('.,')
    if re.match(r'[\u4e00-\u9fff]', first):
        return first[:2] if len(first) > 2 else first
    return first.strip('.,')


def extract_year(text, creation_date=None):
    pub = re.search(r'Published\s+online:?\s+\d+\s+\w+\s+(20\d{2})', text)
    if pub:
        return pub.group(1)
    accepted = re.search(r'Accepted:?\s+\d+\s+\w+\s+(20\d{2})', text)
    if accepted:
        return accepted.group(1)
    years = re.findall(r'\b(20[0-2]\d)\b', text)
    if years:
        recent = [y for y in years if int(y) >= 2020]
        return max(recent) if recent else max(years)
    if creation_date:
        m = re.search(r'(20\d{2})', creation_date)
        if m:
            return m.group(1)
    return "XXXX"


def sanitize_title(title, max_len=60):
    if not title:
        return "Untitled"
    title = re.sub(r'[:/\\]', ' -', title)
    title = re.sub(r'\s+', ' ', title).strip()
    if len(title) > max_len:
        title = title[:max_len].rsplit(' ', 1)[0]
    return title


def needs_rename(filename):
    if re.match(r'^[A-Z][a-zA-Z\-]+_\d{4}_', filename):
        return False
    if re.match(r'^[\u4e00-\u9fff]', filename):
        return False
    patterns = [
        r'^\d{4}\.\d{4,5}',        # arXiv
        r'^1-s2\.0-',               # ScienceDirect
        r'^s\d+-\d+-\d+-\d+',       # Springer DOI
        r'^[a-f0-9]{8,}\.pdf$',     # hash
        r'^\d{5,}\.pdf$',           # numeric ID
    ]
    return any(re.match(p, filename) for p in patterns)


def process_pdf(filepath):
    doc = fitz.open(filepath)
    meta = doc.metadata
    text = ""
    for i in range(min(3, len(doc))):
        text += doc[i].get_text()

    author = meta.get('author', '')
    title = meta.get('title', '')

    if not title or title == 'None':
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        title = lines[0] if lines else ''

    year = extract_year(text, meta.get('creationDate', ''))
    lastname = extract_lastname(author)

    if lastname == "Unknown":
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[1:5]:
            author_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z\.]+)?)\s*[,·]', line)
            if author_match:
                lastname = extract_lastname(author_match.group(1))
                break

    new_name = f"{lastname}_{year}_{sanitize_title(title)}.pdf"
    return {
        'file': os.path.basename(filepath),
        'author': author,
        'first_author_lastname': lastname,
        'year': year,
        'title': title,
        'suggested_name': new_name,
    }


def main():
    parser = argparse.ArgumentParser(description='PDF paper renamer')
    parser.add_argument('--dir', default='.', help='Directory with PDFs')
    parser.add_argument('--rename', action='store_true', help='Execute renames')
    parser.add_argument('--json', metavar='PATH', help='Output results as JSON')
    parser.add_argument('--all', action='store_true', help='Process all PDFs, not just unreadable names')
    args = parser.parse_args()

    directory = args.dir
    pdfs = sorted([f for f in os.listdir(directory) if f.lower().endswith('.pdf')])

    if not args.all:
        pdfs = [f for f in pdfs if needs_rename(f)]

    results = []
    for pdf in pdfs:
        path = os.path.join(directory, pdf)
        try:
            info = process_pdf(path)
            results.append(info)
            print(f"{info['file']}")
            print(f"  → {info['suggested_name']}")
            print(f"    author={info['author'][:60]}  year={info['year']}")
        except Exception as e:
            results.append({'file': pdf, 'error': str(e)})
            print(f"{pdf} → ERROR: {e}")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nJSON saved: {args.json}")

    if args.rename:
        renamed = 0
        errors = 0
        for info in results:
            if 'error' in info:
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
                os.rename(src, dst)
                print(f"  renamed: {info['file']} → {os.path.basename(dst)}")
                renamed += 1
            except Exception as e:
                print(f"  ERROR: {e}")
                errors += 1
        print(f"\nRenamed: {renamed}, Errors: {errors}")


if __name__ == '__main__':
    main()
