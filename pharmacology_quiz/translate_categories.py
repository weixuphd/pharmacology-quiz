#!/usr/bin/env python3
"""Translate Chinese category labels in EN CSVs to English.

Uses existing EN category data from True/False and Single Choice rows
as a mapping source. Falls back to direct translation for unmatched categories.
"""
import csv
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_category_mapping():
    """Build CN->EN category mapping from existing EN CSVs."""
    en_cat_lookup = {}  # EN cat -> EN cat (identity, just need to know it exists)
    cn_to_en = {}  # CN cat -> EN cat
    cn_cats_by_ch = {}
    en_cats_by_ch = {}

    for ch in range(1, 47):
        en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch:02d}.csv")
        cn_path = os.path.join(SCRIPT_DIR, f"pharma_cn_ch{ch:02d}.csv")

        en_cats = set()
        cn_cats = set()

        if os.path.exists(en_path):
            with open(en_path, 'r', encoding='utf-8-sig') as f:
                for r in csv.DictReader(f):
                    t = r.get('type', '').strip()
                    if t in ('True/False', 'Single Choice'):
                        cat = r.get('category', '')
                        if cat and not any('一' <= c <= '鿿' for c in cat):
                            en_cats.add(cat)
                            en_cat_lookup[cat] = cat

        if os.path.exists(cn_path):
            with open(cn_path, 'r', encoding='utf-8-sig') as f:
                for r in csv.DictReader(f):
                    cat = r.get('category', '').strip()
                    if cat:
                        cn_cats.add(cat)

        cn_cats_by_ch[ch] = cn_cats
        en_cats_by_ch[ch] = en_cats

    # Map CN cats to EN cats within same chapter
    for ch in range(1, 47):
        for cn_cat in cn_cats_by_ch.get(ch, set()):
            if cn_cat not in cn_to_en:
                for en_cat in en_cats_by_ch.get(ch, set()):
                    cn_to_en[cn_cat] = en_cat
                    break

    # For remaining CN cats, try fuzzy matching by chapter overlap
    for ch in range(1, 47):
        for cn_cat in cn_cats_by_ch.get(ch, set()):
            if cn_cat not in cn_to_en:
                # Find another chapter that has this CN cat and an EN cat
                for ch2 in range(1, 47):
                    if ch2 != ch and cn_cat in cn_cats_by_ch.get(ch2, set()):
                        for en_cat in en_cats_by_ch.get(ch2, set()):
                            if en_cat not in cn_to_en.values():
                                cn_to_en[cn_cat] = en_cat
                                break
                        if cn_cat in cn_to_en:
                            break

    return cn_to_en


def translate_text(text):
    """Fallback translator using youdao via deep-translator."""
    if not text or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='zh-CN', target='en').translate(text)
    except:
        return text


def main():
    mapping = build_category_mapping()

    # Find untranslated categories
    untranslated = {}
    for ch in range(1, 47):
        en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch:02d}.csv")
        if not os.path.exists(en_path):
            continue
        with open(en_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        for r in rows:
            cat = r.get('category', '')
            if cat and any('一' <= c <= '鿿' for c in cat):
                if cat not in mapping:
                    untranslated[cat] = True

    print(f"Untranslated categories: {len(untranslated)}")

    # Translate remaining
    for cat in untranslated:
        translated = translate_text(cat)
        if translated and translated != cat:
            mapping[cat] = translated
            print(f"  Translated: '{cat}' -> '{translated}'")
        else:
            mapping[cat] = cat
            print(f"  Failed: '{cat}'")
        time.sleep(0.3)

    # Apply mapping to all EN CSVs
    total_fixed = 0
    for ch in range(1, 47):
        en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch:02d}.csv")
        if not os.path.exists(en_path):
            continue

        with open(en_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        changed = 0
        for r in rows:
            old_cat = r.get('category', '')
            if old_cat and any('一' <= c <= '鿿' for c in old_cat):
                new_cat = mapping.get(old_cat, old_cat)
                if new_cat != old_cat:
                    r['category'] = new_cat
                    changed += 1

        if changed > 0:
            with open(en_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            total_fixed += changed
            print(f"Ch{ch}: fixed {changed} categories")

    print(f"\nTotal categories fixed: {total_fixed}")


if __name__ == '__main__':
    main()
