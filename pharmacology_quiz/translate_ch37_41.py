#!/usr/bin/env python3
"""
Translate pharmacology quiz CSVs (Chapters 37-41) from Chinese to English.
Hybrid approach: Google Translate for natural text, dictionary for exact matches.

Strategy:
- Google Translate handles all Chinese text (questions, explanations, categories, options)
- Dictionary handles exact-match cases (question types, True/False values)
- Rate limiting with delays to avoid API throttling
"""

import csv
import os
import time
import sys
from deep_translator import GoogleTranslator

# ============================================================
# Exact-match dictionary (only for categories that need precise names)
# ============================================================

# Question type mapping (exact match)
TYPE_MAP = {
    "是非题": "True/False",
    "单选题": "Single Choice",
    "简答题(多选)": "Multiple Choice",
    "简答题（多选）": "Multiple Choice",
}

# ============================================================
# Google Translate wrapper
# ============================================================

def has_chinese(text):
    """Check if text contains Chinese characters."""
    if not text:
        return False
    for c in text:
        if '一' <= c <= '鿿':
            return True
    return False


def google_translate(text, retries=3):
    """
    Translate Chinese text to English using Google Translate.
    Returns original text if no Chinese characters or translation fails.
    """
    if not text or not text.strip():
        return text
    if not has_chinese(text):
        return text

    for attempt in range(retries):
        try:
            result = GoogleTranslator(source='zh-CN', target='en').translate(text)
            time.sleep(0.25)  # Rate limiting
            return result
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"  Retry {attempt+1}/{retries} after {wait}s: {str(e)[:80]}")
                time.sleep(wait)
            else:
                print(f"  FAILED translation after {retries} attempts: {str(e)[:80]}")
                print(f"  Text preview: {text[:100]}...")
                return text  # Return original on failure

    return text


def translate_option(val):
    """Translate option value - handle True/False specially."""
    val = val.strip()
    if val == '正确':
        return 'True'
    if val == '错误':
        return 'False'
    if not val:
        return val
    return google_translate(val)


# ============================================================
# Chapter processing
# ============================================================

def process_chapter(src_path, dst_path):
    """Read, translate, and write a single chapter CSV."""
    chapter_name = os.path.basename(src_path)
    print(f"Processing: {chapter_name} -> {os.path.basename(dst_path)}")
    print(f"  (Using Google Translate - this will take several minutes)")

    with open(src_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    total = len(rows)
    for i, row in enumerate(rows):
        if (i + 1) % 10 == 0 or i == 0:
            sys.stdout.write(f"\r  Translating row {i+1}/{total}...")
            sys.stdout.flush()

        # Question type (exact match)
        qt = row.get('type', '').strip()
        if qt in TYPE_MAP:
            row['type'] = TYPE_MAP[qt]

        # Question text (Google Translate)
        q = row.get('question', '').strip()
        if q:
            row['question'] = google_translate(q)

        # Options
        for col in ['option_a', 'option_b', 'option_c', 'option_d', 'option_e',
                    'option_f', 'option_g', 'option_h', 'option_i', 'option_j']:
            val = row.get(col, '').strip()
            if val:
                row[col] = translate_option(val)

        # Explanation (Google Translate)
        expl = row.get('explanation', '').strip()
        if expl:
            row['explanation'] = google_translate(expl)

        # Category (Google Translate)
        cat = row.get('category', '').strip()
        if cat:
            row['category'] = google_translate(cat)

    print(f"\r  Done: {total} rows translated and written")

    with open(dst_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    base = "/Users/weixu/Downloads/pnas"
    chapters = [
        ("pharma_cn_ch37.csv", "pharma_en_ch37.csv"),
        ("pharma_cn_ch38.csv", "pharma_en_ch38.csv"),
        ("pharma_cn_ch39.csv", "pharma_en_ch39.csv"),
        ("pharma_cn_ch40.csv", "pharma_en_ch40.csv"),
        ("pharma_cn_ch41.csv", "pharma_en_ch41.csv"),
    ]

    for src_name, dst_name in chapters:
        src_path = os.path.join(base, src_name)
        dst_path = os.path.join(base, dst_name)
        if not os.path.exists(src_path):
            print(f"WARNING: Source file not found: {src_path}")
            continue
        process_chapter(src_path, dst_path)

    print("\nAll chapters processed.")


if __name__ == "__main__":
    main()
