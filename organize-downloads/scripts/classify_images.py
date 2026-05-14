#!/usr/bin/env python3
"""
Image source classifier for Downloads/图片/

Three-layer classification (rules loaded from classification_rules.json):
  Layer 1: Filename pattern matching
  Layer 2: EXIF metadata + file properties
  Layer 3: Visual features (edge density, brightness, contrast, flat areas)

Usage:
    conda run -n henri_env python classify_images.py [options]
"""

import re
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

from PIL import Image, ExifTags
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.heic', '.tiff', '.bmp', '.avif'}

RULES_FILE = SCRIPT_DIR / 'classification_rules.json'


def load_rules(path=None):
    p = Path(path) if path else RULES_FILE
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)

    compiled = []
    for group in data['filename_rules']:
        for rule in group['rules']:
            flags = 0
            for fl in rule.get('flags', []):
                flags |= getattr(re, fl, 0)
            compiled.append((
                re.compile(rule['pattern'], flags),
                rule['category'],
                rule.get('subcategory'),
                rule['confidence'],
                rule['evidence'],
            ))

    visual_compiled = []
    for vrule in data.get('visual_rules', []):
        visual_compiled.append({
            'name': vrule['name'],
            'conditions': vrule['conditions'],
            'category': vrule['category'],
            'subcategory': vrule.get('subcategory'),
            'confidence': vrule['confidence'],
            'evidence': vrule['evidence'],
        })

    url_rules_raw = data.get('metadata_url_rules', {})
    url_compiled = []
    for rule in url_rules_raw.get('rules', []):
        url_compiled.append({
            'domain_re': re.compile(rule['domain'], re.IGNORECASE),
            'category': rule['category'],
            'subcategory': rule.get('subcategory'),
            'confidence': rule['confidence'],
            'evidence': rule['evidence'],
        })

    return {
        'filename_rules': compiled,
        'exif_rules': data['exif_rules'],
        'url_rules': url_compiled,
        'url_skip_domains': [re.compile(s, re.IGNORECASE) for s in url_rules_raw.get('skip_domains', [])],
        'visual_rules': visual_compiled,
        'default_fallback': data['default_fallback'],
        'own_devices': data.get('own_devices', []),
    }


def read_exif(img):
    exif_raw = img.getexif()
    exif = {}
    for k, v in exif_raw.items():
        name = ExifTags.TAGS.get(k, str(k))
        exif[name] = v
    return exif


def classify_by_exif(exif, exif_rules, own_devices=None):
    if not exif:
        return None, None, 0, []

    own_devices = [d.lower() for d in (own_devices or [])]
    camera_tags = set(exif_rules['camera_tags'])
    found = [k for k in camera_tags if k in exif]
    if not found:
        return None, None, 0, []

    make = str(exif.get('Make', '')).lower()
    model = str(exif.get('Model', '')).lower()

    odm = exif_rules['own_device_match']
    for dev in own_devices:
        if dev.lower() in model or dev.lower() in make:
            return (
                odm['category'], odm.get('subcategory'), odm['confidence'],
                [f'EXIF matches own device: {dev}',
                 f'Make={exif.get("Make")}, Model={exif.get("Model")}'],
            )

    mtm = exif_rules['multi_tag_match']
    if len(found) >= mtm['min_tags']:
        return (
            mtm['category'], mtm.get('subcategory'), mtm['confidence'],
            [f'Camera EXIF present: {found}',
             f'Make={exif.get("Make", "?")}, Model={exif.get("Model", "?")}'],
        )

    stm = exif_rules['single_tag_match']
    return (stm['category'], stm.get('subcategory'), stm['confidence'],
            [f'Partial camera EXIF: {found}'])


def extract_urls_from_file(filepath):
    urls = []
    path = Path(filepath)

    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except Exception:
        return urls

    found = set(re.findall(rb'https?://[^\x00-\x1f\s"<>]{10,300}', raw))
    for u in found:
        try:
            decoded = u.decode('utf-8', errors='ignore').rstrip('.0+,;$&')
            urls.append(decoded)
        except Exception:
            pass

    try:
        img = Image.open(path)
        if hasattr(img, 'text') and img.text:
            for v in img.text.values():
                for m in re.findall(r'https?://[^\s"<>]{10,300}', str(v)):
                    urls.append(m.rstrip('.0+,;$&'))
    except Exception:
        pass

    return list(set(urls))


def classify_by_metadata_urls(filepath, url_rules, url_skip_domains):
    urls = extract_urls_from_file(filepath)
    if not urls:
        return None, None, 0, [], []

    meaningful = []
    for url in urls:
        if any(skip.search(url) for skip in url_skip_domains):
            continue
        meaningful.append(url)

    if not meaningful:
        return None, None, 0, [], urls

    for rule in url_rules:
        for url in meaningful:
            if rule['domain_re'].search(url):
                return (
                    rule['category'],
                    rule.get('subcategory'),
                    rule['confidence'],
                    [rule['evidence'], f'URL: {url[:120]}'],
                    urls,
                )

    return None, None, 0, [], urls


def compute_visual_features(image_path):
    try:
        img = Image.open(image_path)
        rgb = img.convert('RGB')
        arr = np.array(rgb, dtype=np.float64)
        h, w = arr.shape[:2]

        gray = np.dot(arr[..., :3], [0.299, 0.587, 0.114])
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        if HAS_CV2:
            gray_u8 = np.clip(gray, 0, 255).astype(np.uint8)
            edges = cv2.Canny(gray_u8, 80, 160)
            edge_density = float(np.mean(edges) / 255.0)
            sobel_x = cv2.Sobel(gray_u8, cv2.CV_64F, 1, 0)
            sobel_y = cv2.Sobel(gray_u8, cv2.CV_64F, 0, 1)
            grad = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
        else:
            gx = np.diff(gray, axis=1, prepend=gray[:, :1])
            gy = np.diff(gray, axis=0, prepend=gray[:1, :])
            grad = np.sqrt(gx ** 2 + gy ** 2)
            edge_density = float(np.mean(grad > 30))

        flat_area_ratio = float(np.mean(grad < 5))

        step = max(1, int((h * w) ** 0.5 / 200))
        sample = arr[::step, ::step]
        unique_colors = len(np.unique(sample.reshape(-1, 3).astype(int), axis=0))

        return {
            'width': w,
            'height': h,
            'aspect_ratio': round(w / h, 4),
            'brightness': round(brightness, 1),
            'contrast': round(contrast, 1),
            'edge_density': round(edge_density, 4),
            'flat_area_ratio': round(flat_area_ratio, 4),
            'unique_colors': unique_colors,
        }
    except Exception as e:
        return {'error': str(e)}


def _check_condition(cond, features):
    field = cond['field']
    op = cond['op']
    val = features.get(field, 0)

    if op == '>':
        return val > cond['value']
    if op == '<':
        return val < cond['value']
    if op == '>=':
        return val >= cond['value']
    if op == '<=':
        if 'max_field' in cond:
            other = features.get(cond['max_field'], 0)
            return max(val, other) <= cond['value']
        return val <= cond['value']
    if op == 'between':
        return cond['min'] <= val <= cond['max']
    return False


def classify_by_features(features, visual_rules):
    if 'error' in features:
        return None, None, 0, ['Feature extraction failed']

    for vrule in visual_rules:
        if all(_check_condition(c, features) for c in vrule['conditions']):
            try:
                evi = vrule['evidence'].format(**features)
            except (KeyError, ValueError):
                evi = vrule['evidence']
            return (vrule['category'], vrule.get('subcategory'),
                    vrule['confidence'], [evi])

    return None, None, 0, []


def classify_image(filepath, rules, own_devices=None):
    path = Path(filepath)
    filename = path.name

    result = {
        'filepath': str(path),
        'filename': filename,
        'category': None,
        'subcategory': None,
        'confidence': 0,
        'evidence': [],
        'layer': None,
    }

    for regex, cat, subcat, conf, evi in rules['filename_rules']:
        if regex.search(filename):
            result['category'] = cat
            result['subcategory'] = subcat
            result['confidence'] = conf
            result['evidence'] = [evi]
            result['layer'] = 'filename'
            break

    if result['confidence'] >= 0.70:
        _fill_file_meta(result, path)
        return result

    try:
        img = Image.open(filepath)
        exif = read_exif(img)
        result['format'] = img.format
        result['mode'] = img.mode
        result['size'] = list(img.size)
        result['file_size'] = path.stat().st_size

        cat, subcat, conf, evi = classify_by_exif(
            exif, rules['exif_rules'], own_devices)
        if conf > result['confidence']:
            result['category'] = cat
            result['subcategory'] = subcat
            result['confidence'] = conf
            result['evidence'] = evi
            result['layer'] = 'exif'
    except Exception:
        pass

    if result['confidence'] >= 0.60:
        return result

    # Layer 2.5: Metadata URL extraction
    cat, subcat, conf, evi, all_urls = classify_by_metadata_urls(
        filepath, rules['url_rules'], rules['url_skip_domains'])
    result['metadata_urls'] = all_urls
    if conf > result['confidence']:
        result['category'] = cat
        result['subcategory'] = subcat
        result['confidence'] = conf
        result['evidence'] = evi
        result['layer'] = 'metadata_url'

    if result['confidence'] >= 0.60:
        return result

    # Layer 3: Visual features
    features = compute_visual_features(filepath)
    result['features'] = features

    cat, subcat, conf, evi = classify_by_features(features, rules['visual_rules'])
    if conf > result['confidence']:
        result['category'] = cat
        result['subcategory'] = subcat
        result['confidence'] = conf
        result['evidence'] = evi
        result['layer'] = 'visual'

    if result['category'] is None:
        fb = rules['default_fallback']
        result['category'] = fb['category']
        result['confidence'] = fb['confidence']
        result['evidence'] = [fb['evidence']]
        result['layer'] = 'fallback'

    return result


def _fill_file_meta(result, path):
    try:
        img = Image.open(path)
        result['format'] = img.format
        result['mode'] = img.mode
        result['size'] = list(img.size)
        result['file_size'] = path.stat().st_size
    except Exception:
        pass


def scan_images(images_dir, scan_root_only=False):
    images = []
    p = Path(images_dir)

    for f in sorted(p.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            images.append(str(f))

    if not scan_root_only:
        other_dir = p / '其他图片'
        if other_dir.is_dir():
            for f in sorted(other_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
                    images.append(str(f))

    return images


def get_target_dir(images_dir, category, subcategory):
    if subcategory:
        return Path(images_dir) / category / subcategory
    return Path(images_dir) / category


def print_report(results):
    cat_width = max(len('Category'), max(len(r['category']) for r in results))
    sub_width = max(len('Sub'), max(len(r.get('subcategory') or '-') for r in results))

    header = f'{"Category":<{cat_width}}  {"Sub":<{sub_width}}  {"Conf":>5}  {"Layer":<8}  Filename'
    print(header)
    print('-' * len(header))

    for r in results:
        sub = r.get('subcategory') or '-'
        conf = f'{r["confidence"]:.0%}'
        layer = r.get('layer', '?')
        print(f'{r["category"]:<{cat_width}}  {sub:<{sub_width}}  {conf:>5}  {layer:<8}  {r["filename"]}')


def print_summary(results):
    counts = {}
    for r in results:
        cat = r['category']
        sub = r.get('subcategory')
        key = f'{cat}/{sub}' if sub else cat
        counts[key] = counts.get(key, 0) + 1

    print(f'\n--- Summary ({len(results)} images) ---')
    for key, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f'  {key}: {count}')


def move_files(results, images_dir):
    moved = 0
    errors = 0

    for r in results:
        src = Path(r['filepath'])
        target = get_target_dir(images_dir, r['category'], r.get('subcategory'))

        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)

        dst = target / src.name
        if src.resolve() == dst.resolve():
            continue

        if dst.exists():
            stem, suffix = src.stem, src.suffix
            counter = 1
            while dst.exists():
                dst = target / f'{stem}_{counter}{suffix}'
                counter += 1

        try:
            src.rename(dst)
            print(f'  {src.name} → {dst.relative_to(images_dir)}')
            moved += 1
        except Exception as e:
            print(f'  ERROR {src.name}: {e}')
            errors += 1

    print(f'\nMoved: {moved}, Errors: {errors}')
    return moved, errors


def main():
    parser = argparse.ArgumentParser(description='Image source classifier')
    parser.add_argument('--images-dir', help='Path to 图片/ directory')
    parser.add_argument('--rules', help='Path to classification_rules.json')
    parser.add_argument('--scan-root', action='store_true',
                        help='Only scan root-level images')
    parser.add_argument('--move', action='store_true',
                        help='Move files to classified directories')
    parser.add_argument('--json', metavar='PATH',
                        help='Output JSON results to file')
    parser.add_argument('--own-devices', nargs='*',
                        help='Device names for EXIF matching (overrides rules file)')
    args = parser.parse_args()

    rules = load_rules(args.rules)

    own_devices = args.own_devices if args.own_devices is not None else rules['own_devices']

    if args.images_dir:
        images_dir = args.images_dir
    else:
        images_dir = os.path.join(os.getcwd(), '图片')
        if not os.path.isdir(images_dir):
            fallback = str(Path(SCRIPT_DIR).parent.parent.parent / '图片')
            if os.path.isdir(fallback):
                images_dir = fallback

    if not os.path.isdir(images_dir):
        print(f'ERROR: Directory not found: {images_dir}')
        sys.exit(1)

    print(f'Scanning: {images_dir}')
    print(f'Rules: {args.rules or "default"}')

    images = scan_images(images_dir, scan_root_only=args.scan_root)
    print(f'Found {len(images)} images to classify\n')

    if not images:
        print('No unclassified images found.')
        return

    results = []
    for img_path in images:
        result = classify_image(img_path, rules, own_devices=own_devices)
        results.append(result)

    print_report(results)
    print_summary(results)

    if args.json:
        output = {
            'generated': datetime.now().isoformat(),
            'images_dir': images_dir,
            'total': len(results),
            'results': results,
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f'\nJSON saved: {args.json}')

    if args.move:
        print(f'\n--- Moving files ---')
        move_files(results, images_dir)


if __name__ == '__main__':
    main()
