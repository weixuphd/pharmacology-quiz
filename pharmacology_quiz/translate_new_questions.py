#!/usr/bin/env python3
"""Translate Terminology and Short Answer rows in EN CSVs from Chinese to English.

Uses sogou translator via the translators library.
After translation, runs postprocess_en.py to fix abbreviations and academic style.
"""
import csv
import os
import sys
import time
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["translators_default_region"] = "EN"
import translators as ts


def translate_text(text):
    """Translate Chinese text to English using Sogou."""
    if not text or not text.strip():
        return text
    try:
        result = ts.translate_text(text, translator='youdao', from_language='zh')
        return result
    except Exception as e:
        print(f"    WARNING: Translation failed: {e}")
        return text


def process_chapter(ch_num, dry_run=False):
    """Process one chapter's EN CSV."""
    en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch_num:02d}.csv")
    backup_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch_num:02d}.csv.bak")

    if not os.path.exists(en_path):
        print(f"  Ch{ch_num}: EN CSV not found, skipping")
        return 0

    shutil.copy2(en_path, backup_path)

    with open(en_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Find Chinese rows that need translation
    to_translate = []
    for i, r in enumerate(rows):
        t = r.get('type', '').strip()
        if t not in ('Terminology', 'Short Answer'):
            continue
        # Check if question is in Chinese
        q = r.get('question', '')
        has_chinese = any('一' <= c <= '鿿' for c in q)
        if has_chinese:
            to_translate.append(i)

    if not to_translate:
        print(f"  Ch{ch_num}: No Chinese rows to translate ({len(rows)} total)")
        return 0

    print(f"  Ch{ch_num}: Translating {len(to_translate)} rows out of {len(rows)}")

    if dry_run:
        for i in to_translate:
            r = rows[i]
            print(f"    [{r.get('type','')}] {r.get('question','')[:50]}")
        return len(to_translate)

    # Translate in batches
    batch_size = 5
    for batch_start in range(0, len(to_translate), batch_size):
        batch = to_translate[batch_start:batch_start + batch_size]

        for i in batch:
            r = rows[i]
            fields = ['question', 'correct', 'explanation']
            for field in fields:
                val = r.get(field, '')
                if val and any('一' <= c <= '鿿' for c in val):
                    translated = translate_text(val)
                    rows[i][field] = translated
            time.sleep(0.3)  # Rate limit

    # Write back
    with open(en_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return len(to_translate)


def postprocess_chapter(ch_num):
    """Run postprocess_en.py on a chapter's EN CSV."""
    en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch_num:02d}.csv")
    if os.path.exists(en_path):
        subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, 'postprocess_en.py'), en_path, en_path],
            capture_output=True
        )


if __name__ == '__main__':
    import subprocess

    dry_run = '--dry-run' in sys.argv

    total = 0
    for ch in range(1, 47):
        count = process_chapter(ch, dry_run=dry_run)
        total += count
        if not dry_run and count > 0:
            postprocess_chapter(ch)
        if not dry_run:
            time.sleep(0.5)

    print(f"\nTotal rows to translate: {total}")
    if dry_run:
        print("(dry run, no files modified)")
