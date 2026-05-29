#!/usr/bin/env python3
"""
Translate pharmacology quiz CSVs (Chapters 37-41) from Chinese to English.
Uses deep_translator (Google Translate) batch mode for efficiency.
"""

import csv
import os
import time
from deep_translator import GoogleTranslator

QUESTION_TYPES = {
    "是非题": "True/False",
    "单选题": "Single Choice",
    "简答题(多选)": "Multiple Choice",
    "简答题（多选）": "Multiple Choice",
}


def collect_texts(rows):
    """Collect all translatable texts from rows into a flat list with metadata."""
    texts = []
    positions = []

    for row_idx, row in enumerate(rows):
        # Question type
        qtype = row['type'].strip()
        if qtype not in QUESTION_TYPES:
            texts.append(qtype)
            positions.append(('type', row_idx))

        # Question text
        q = row['question'].strip()
        if q:
            # Remove 【...】 prefix
            q_clean = q
            if q_clean.startswith('【'):
                end = q_clean.find('】')
                if end > 0:
                    q_clean = q_clean[end+1:].strip()
            if q_clean:
                texts.append(q_clean)
                positions.append(('question', row_idx))

        # Options
        for col in ['option_a', 'option_b', 'option_c', 'option_d', 'option_e',
                    'option_f', 'option_g', 'option_h', 'option_i', 'option_j']:
            val = row.get(col, '').strip()
            if val:
                if val == '正确':
                    row[col] = 'True'
                elif val == '错误':
                    row[col] = 'False'
                else:
                    texts.append(val)
                    positions.append((col, row_idx))

        # Explanation
        expl = row.get('explanation', '').strip()
        if expl:
            texts.append(expl)
            positions.append(('explanation', row_idx))

        # Category
        cat = row.get('category', '').strip()
        if cat:
            texts.append(cat)
            positions.append(('category', row_idx))

    return texts, positions


def apply_translations(rows, texts, positions, translations):
    """Apply translated texts back to the correct rows and fields."""
    assert len(texts) == len(positions) == len(translations), \
        f"Mismatch: texts={len(texts)}, positions={len(positions)}, translations={len(translations)}"

    for (field, row_idx), translation in zip(positions, translations):
        if field == 'type':
            rows[row_idx]['type'] = translation
        elif field == 'question':
            rows[row_idx]['question'] = translation
        elif field.startswith('option_'):
            rows[row_idx][field] = translation
        elif field == 'explanation':
            rows[row_idx]['explanation'] = translation
        elif field == 'category':
            rows[row_idx]['category'] = translation

    return rows


def process_chapter(src_path, dst_path):
    """Read, translate, and write a single chapter CSV."""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(src_path)} -> {os.path.basename(dst_path)}")

    # Read source
    with open(src_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"  Read {len(rows)} rows")

    # Translate question types first (fixed mapping, no Google needed)
    for row in rows:
        qtype = row['type'].strip()
        if qtype in QUESTION_TYPES:
            row['type'] = QUESTION_TYPES[qtype]

    # Collect all texts needing Google Translate
    texts, positions = collect_texts(rows)
    print(f"  Collected {len(texts)} texts to translate")

    if not texts:
        print("  No texts to translate, writing directly")
        with open(dst_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return

    # Translate in batches (Google Translate may have size limits)
    translator = GoogleTranslator(source='zh-CN', target='en')
    BATCH_SIZE = 100
    all_translations = []

    for batch_start in range(0, len(texts), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(texts))
        batch = texts[batch_start:batch_end]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"  Translating batch {batch_num}/{total_batches} ({len(batch)} texts)...")
        t0 = time.time()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                translations = translator.translate_batch(batch)
                all_translations.extend(translations)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    Retry {attempt+1} after error: {e}")
                    time.sleep(3)
                else:
                    print(f"    Failed after {max_retries} attempts: {e}")
                    # Use original text as fallback
                    all_translations.extend(batch)

        t1 = time.time()
        print(f"    Done in {t1-t0:.1f}s")

        # Rate limiting between batches
        if batch_end < len(texts):
            time.sleep(1)

    # Apply translations back to rows
    print(f"  Applying {len(all_translations)} translations...")
    rows = apply_translations(rows, texts, positions, all_translations)

    # Write output
    with open(dst_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Done: {len(rows)} rows written to {os.path.basename(dst_path)}")


def main():
    base = "/Users/weixu/Downloads/pnas"
    chapters = [
        (37, "pharma_cn_ch37.csv", "pharma_en_ch37.csv"),
        (38, "pharma_cn_ch38.csv", "pharma_en_ch38.csv"),
        (39, "pharma_cn_ch39.csv", "pharma_en_ch39.csv"),
        (40, "pharma_cn_ch40.csv", "pharma_en_ch40.csv"),
        (41, "pharma_cn_ch41.csv", "pharma_en_ch41.csv"),
    ]

    total_start = time.time()
    for ch_num, src_name, dst_name in chapters:
        src_path = os.path.join(base, src_name)
        dst_path = os.path.join(base, dst_name)
        if not os.path.exists(src_path):
            print(f"WARNING: Source file not found: {src_path}")
            continue
        process_chapter(src_path, dst_path)

    total_elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"All chapters processed. Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")


if __name__ == "__main__":
    main()
