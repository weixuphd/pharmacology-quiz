#!/usr/bin/env python3
"""Re-translate a Chinese pharmacology CSV to academic English using Google Translate.

Usage: python3 retranslate_chapter.py pharma_cn_ch43.csv pharma_en_ch43.csv
"""

import csv, sys, time, os

SEP = "\n---SEP---\n"

def translate_batch(texts, source="zh-CN", target="en", max_retries=5):
    """Translate a list of texts in one API call, preserving order."""
    from deep_translator import GoogleTranslator

    if not texts or all(not t or not t.strip() for t in texts):
        return texts

    combined = SEP.join(texts)

    for attempt in range(max_retries):
        try:
            t = GoogleTranslator(source=source, target=target)
            result = t.translate(combined)
            parts = result.split(SEP)
            # If split count doesn't match, try other strategies
            if len(parts) == len(texts):
                return [p.strip() for p in parts]
            else:
                # Fall back to individual translation if batch fails
                return [translate_one(t, tx, source, target, max_retries) for tx in texts]
        except Exception as e:
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 3
                print(f"  Retry in {wait}s... ({e})")
                time.sleep(wait)
            else:
                raise

    return texts


def translate_one(translator, text, source, target, max_retries):
    if not text or not text.strip():
        return text
    for attempt in range(max_retries):
        try:
            return translator.translate(text).strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 3)
            else:
                raise
    return text


def translate_csv(in_path, out_path):
    rows = []
    with open(in_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"Translating {total} questions from {in_path}")

    fieldnames = list(rows[0].keys())
    translated_rows = []

    for i, row in enumerate(rows):
        # Collect texts to translate: question, all non-empty options, explanation, category
        text_fields = ["question"]
        for key in sorted(row.keys()):
            if key.startswith("option_") and row.get(key, "").strip():
                text_fields.append(key)
        text_fields.append("explanation")
        text_fields.append("category")

        texts = []
        for key in text_fields:
            texts.append(row.get(key, ""))

        # Translate in one batch call
        try:
            translated = translate_batch(texts)
        except Exception as e:
            print(f"  ERROR row {i+1}: {e}")
            translated = texts  # keep original on failure

        new_row = {}
        for key in row:
            val = row[key]
            if key in text_fields:
                idx = text_fields.index(key)
                new_row[key] = translated[idx] if idx < len(translated) else val
            else:
                new_row[key] = val  # id, type, correct unchanged

        translated_rows.append(new_row)

        if (i + 1) % 5 == 0:
            print(f"  {i+1}/{total} done")
        time.sleep(0.6)  # rate limit

    # fix True/False -> True/False (keep as-is)
    # fix type column
    type_map = {
        "是非题": "True/False",
        "单选题": "Single Choice",
        "简答题(多选)": "Multiple Choice",
        "简答题（多选）": "Multiple Choice",
    }
    for r in translated_rows:
        t = r.get("type", "")
        if t in type_map:
            r["type"] = type_map[t]

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(translated_rows)

    print(f"Saved: {out_path}")
    return total


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 retranslate_chapter.py <chinese_csv> <english_csv>")
        sys.exit(1)
    translate_csv(sys.argv[1], sys.argv[2])
