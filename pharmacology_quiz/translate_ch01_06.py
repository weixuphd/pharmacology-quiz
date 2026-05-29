#!/usr/bin/env python3
"""
Translate pharmacology quiz banks from Chinese to English (Chapters 1-6).

Uses Google Translate via deep-translator with concurrent request processing
for speed, plus pre-translation dictionaries for type/category fields, and
pharmacological post-correction for standard terminology.
"""
import csv
import os
import re
import time
import hashlib
import concurrent.futures
import threading
from deep_translator import GoogleTranslator

WORK_DIR = "/Users/weixu/Downloads/pnas"
FIELDNAMES = [
    "id", "type", "question", "option_a", "option_b", "option_c",
    "option_d", "option_e", "option_f", "option_g", "option_h",
    "option_i", "option_j", "correct", "explanation", "category"
]
TRANSLATABLE_FIELDS = [
    "type", "question", "explanation", "category",
    "option_a", "option_b", "option_c", "option_d", "option_e",
    "option_f", "option_g", "option_h", "option_i", "option_j",
]

# ── Simple dictionary for non-sentence text ──
SIMPLE_MAP = {
    "是非题": "True/False",
    "单选题": "Single Choice",
    "简答题(多选)": "Multiple Choice",
    "正确": "True",
    "错误": "False",
    # Category names
    "药理学的性质与任务": "Nature and Tasks of Pharmacology",
    "药理学发展简史": "Brief History of Pharmacology",
    "药理学分支": "Branches of Pharmacology",
    "药理学与新药研究": "Pharmacology and New Drug Research",
    "药物的基本作用": "Basic Drug Actions",
    "量效关系与构效关系": "Dose-Effect and Structure-Activity Relationships",
    "药物的作用机制": "Mechanisms of Drug Action",
    "药物与受体的相互作用": "Drug-Receptor Interactions",
    "药物跨膜转运": "Drug Transport Across Membranes",
    "药物的体内过程": "Drug Disposition (ADME)",
    "房室模型与消除动力学": "Compartment Models and Elimination Kinetics",
    "药物消除动力学": "Drug Elimination Kinetics",
    "药动学重要参数": "Key Pharmacokinetic Parameters",
    "药物剂量的设计和优化": "Dosage Regimen Design and Optimization",
    "药物因素": "Drug-Related Factors",
    "机体因素": "Host-Related Factors",
    "临床合理用药原则": "Principles of Rational Drug Use",
    "神经元和胶质细胞": "Neurons and Glial Cells",
    "突触与信息传递": "Synapses and Signal Transmission",
    "传出神经系统分类递质和受体": "Classification of Efferent Nervous System: Transmitters and Receptors",
    "中枢神经系统递质及其受体": "CNS Transmitters and Their Receptors",
    "神经系统药理学特点及药物分类": "Characteristics of Nervous System Pharmacology and Drug Classification",
    "M、N受体激动药": "M and N Receptor Agonists",
    "M受体激动药": "M Receptor Agonists",
    "N受体激动药": "N Receptor Agonists",
}

# ── Post-correction regex patterns ──
POST_PATTERNS = [
    # Capitalize True/False
    (r'(?i)\btrue\b', 'True'),
    (r'(?i)\bfalse\b', 'False'),

    # Standard pharmacological abbreviations
    (r'\bacetylcholine\b', 'acetylcholine (ACh)'),
    (r"\bAlzheimer'?s disease\b", "Alzheimer's disease (AD)"),
    (r"\bParkinson'?s disease\b", "Parkinson's disease (PD)"),
    (r'\bnitric oxide\b', 'nitric oxide (NO)'),

    # Standard terminological fixes
    (r'rules of action', 'principles of action'),
    (r'dynamic of drug effect', 'pharmacodynamics'),
    (r'metabolic kinetics of drugs', 'pharmacokinetics'),
    (r'drug effect dynamics', 'pharmacodynamics'),
    (r'drug metabolic kinetics', 'pharmacokinetics'),
    (r'first-pass elimination of the first pass', 'first-pass elimination'),
    (r'blood[- ]brain barrier', 'blood-brain barrier'),
    (r'structure[- ]activity relationship', 'structure-activity relationship (SAR)'),
    (r'G protein[- ]coupled receptor', 'G protein-coupled receptor (GPCR)'),
    (r'apparent volume of distribution', 'apparent volume of distribution (Vd)'),
    (r'steady[- ]state blood concentration', 'steady-state plasma concentration (Css)'),
    (r'steady[- ]state plasma concentration', 'steady-state concentration (Css)'),

    # Receptor cleanup
    (r'\bM1 receptor\b', 'M1 receptor'),
    (r'\bM2 receptor\b', 'M2 receptor'),
    (r'\bM3 receptor\b', 'M3 receptor'),
    (r'\bM4 receptor\b', 'M4 receptor'),
    (r'\bM5 receptor\b', 'M5 receptor'),
    (r'\bNN receptor\b', 'NN receptor (neuronal-type)'),
    (r'\bNM receptor\b', 'NM receptor (muscle-type)'),
    (r'(?<!\w)alpha(?!\w)', 'alpha'),
    (r'(?<!\w)beta(?!\w)', 'beta'),

    # Eye terms
    (r'regulatory spasm', 'accommodation spasm (cyclospasm)'),
    (r'accommodation spasm', 'accommodation spasm (cyclospasm)'),
    (r'regulatory paralysis', 'cycloplegia'),
    (r'pupil sphincter muscle', 'pupillary sphincter muscle'),
    (r'schlemm', 'Schlemm'),
    (r'intraocular pressure', 'intraocular pressure'),

    # Drug target types
    (r'inverse agonist', 'inverse agonist'),
    (r'biased agonist', 'biased agonist'),
    (r'positive allosteric modulatory', 'positive allosteric modulator (PAM)'),
    (r'negative allosteric modulatory', 'negative allosteric modulator (NAM)'),
    (r'competitive antagonist', 'competitive antagonist'),
    (r'non[- ]?competitive antagonist', 'noncompetitive antagonist'),

    # Enzymes
    (r'cytochrome P450', 'cytochrome P450 (CYP)'),
    (r'CYP enzyme', 'CYP enzyme'),
    (r'monoamine oxidase', 'monoamine oxidase (MAO)'),
    (r'catechol[- ]O[- ]methyltransferase', 'COMT'),

    # Pharmacokinetics
    (r'first[- ]order kinetic', 'first-order kinetic'),
    (r'zero[- ]order kinetic', 'zero-order kinetic'),
    (r'Michaelis[- ]Menten', 'Michaelis-Menten'),

    # Drug class cleanup
    (r'M receptor agonist drug', 'M receptor agonist'),
    (r'N receptor agonist drug', 'N receptor agonist'),
    (r'M receptor blocker', 'M receptor antagonist'),
    (r'N receptor blocker', 'N receptor antagonist'),
    (r'anticholinesterase drug', 'anticholinesterase agent'),
    (r'beta blocker', 'beta-adrenoceptor antagonist'),
    (r'beta receptor blocker', 'beta-adrenoceptor antagonist (beta-blocker)'),
    (r'alpha receptor blocker', 'alpha-adrenoceptor antagonist'),
    (r'proton pump inhibitor', 'proton pump inhibitor'),

    # Drug name standardization
    (r'pilocarpine', 'pilocarpine'),
    (r'atropine', 'atropine'),
    (r'nicotine', 'nicotine'),
    (r'muscarine', 'muscarine'),
    (r'bethanechol', 'bethanechol'),
    (r'carbachol', 'carbachol'),
    (r'methacholine', 'methacholine'),
    (r'varenicline', 'varenicline'),
    (r'xanomeline', 'xanomeline'),
    (r'neostigmine', 'neostigmine'),
    (r'physostigmine', 'physostigmine'),
    (r'propranolol', 'propranolol'),
    (r'timolol', 'timolol'),
    (r'guanethidine', 'guanethidine'),
    (r'ephedrine', 'ephedrine'),
    (r'labetalol', 'labetalol'),
    (r'omeprazole', 'omeprazole'),
    (r'chloramphenicol', 'chloramphenicol'),
    (r'warfarin', 'warfarin'),
    (r'phenytoin', 'phenytoin'),
    (r'probenecid', 'probenecid'),
    (r'clonidine', 'clonidine'),
    (r'reserpine', 'reserpine'),
    (r'metaraminol', 'metaraminol'),
    (r'pirenzepine', 'pirenzepine'),
    (r'solifenacin', 'solifenacin'),
    (r'gallamine', 'gallamine'),
    (r'mecamylamine', 'mecamylamine'),
    (r'salbutamol', 'salbutamol'),
    (r'norepinephrine', 'norepinephrine (NA)'),
    (r'epinephrine', 'epinephrine'),
    (r'dopamine', 'dopamine'),
    (r'histamine', 'histamine'),
    (r'glutamate', 'glutamate'),
    (r'glycine', 'glycine'),
    (r'GABA', 'GABA'),
    (r'serotonin \(5-HT\)', 'serotonin (5-HT)'),
    (r'serotonin', 'serotonin (5-HT)'),

    # General cleanup
    (r'  +', ' '),
    (r'\s+([,.;:?!])', r'\1'),
    (r'\(\s+', '('),
    (r'\s+\)', ')'),
]


def is_chinese(text):
    """Check if text contains Chinese characters."""
    return any('一' <= c <= '鿿' for c in text)


def post_correct(text):
    """Apply pharmacological term corrections after machine translation."""
    if not text or not isinstance(text, str):
        return text
    result = text
    for pattern, replacement in POST_PATTERNS:
        try:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        except re.error:
            pass
    return result.strip()


class FastTranslator:
    """Translates Chinese text to English using concurrent Google Translate calls."""

    def __init__(self, max_workers=8):
        self.cache = {}
        self.lock = threading.Lock()
        self.max_workers = max_workers
        self.total = 0
        self.done = 0
        self.errors = 0
        self.start_time = None

    def _translate_one(self, text):
        """Translate a single text string, with retry."""
        if not text or not is_chinese(text):
            return text

        try:
            translator = GoogleTranslator(source='zh-CN', target='en')
            result = translator.translate(text)
            return result
        except Exception as e:
            try:
                time.sleep(1)
                translator = GoogleTranslator(source='zh-CN', target='en')
                return translator.translate(text)
            except Exception as e2:
                return f"[TRANSLATION_FAILED: {text[:50]}...]"

    def translate_batch(self, texts):
        """Translate a list of unique texts concurrently."""
        self.total = len(texts)
        self.done = 0
        self.start_time = time.time()

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {
                executor.submit(self._translate_one, text): text
                for text in texts
            }
            for future in concurrent.futures.as_completed(future_to_text):
                text = future_to_text[future]
                try:
                    result = future.result()
                    result = post_correct(result)
                    with self.lock:
                        results[text] = result
                        self.done += 1
                        if self.done % 50 == 0:
                            elapsed = time.time() - self.start_time
                            rate = self.done / elapsed
                            eta = (self.total - self.done) / rate if rate > 0 else 0
                            print(f"  Progress: {self.done}/{self.total} texts "
                                  f"({rate:.1f} texts/s, ETA {eta:.0f}s)")
                except Exception as e:
                    with self.lock:
                        self.errors += 1
                        results[text] = text

        return results


def collect_unique_texts(chapters):
    """Collect all unique Chinese text segments from all chapters."""
    all_texts = set()
    for ch_num, _ in chapters:
        cn_file = os.path.join(WORK_DIR, f"pharma_cn_ch{ch_num:02d}.csv")
        with open(cn_file, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                for field in TRANSLATABLE_FIELDS:
                    text = row.get(field, "")
                    if text and text.strip() and is_chinese(text):
                        # Don't add items that are in SIMPLE_MAP
                        if text.strip() not in SIMPLE_MAP:
                            all_texts.add(text.strip())
    return all_texts


def process_chapter(ch_num, topic, translations):
    """Read CSV, apply translations, write output."""
    cn_file = os.path.join(WORK_DIR, f"pharma_cn_ch{ch_num:02d}.csv")
    en_file = os.path.join(WORK_DIR, f"pharma_en_ch{ch_num:02d}.csv")

    print(f"\nProcessing Chapter {ch_num}: {topic}")
    rows = []
    with open(cn_file, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    print(f"  Rows: {len(rows)}")

    translated_rows = []
    for row in rows:
        tr = dict(row)
        for field in TRANSLATABLE_FIELDS:
            text = row.get(field, "")
            if not text or not text.strip():
                continue

            text = text.strip()

            # Use simple map first
            if text in SIMPLE_MAP:
                tr[field] = SIMPLE_MAP[text]
                continue

            # If not Chinese, keep as-is
            if not is_chinese(text):
                tr[field] = text
                continue

            # Use Google Translate result
            if text in translations:
                tr[field] = translations[text]
            else:
                tr[field] = text  # Fallback: keep original

        translated_rows.append(tr)

    with open(en_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(translated_rows)

    print(f"  Done -> {en_file}")


CHAPTERS = [
    (1, "Introduction to Pharmacology"),
    (2, "Pharmacodynamics"),
    (3, "Pharmacokinetics"),
    (4, "Factors Affecting Drug Effects and Principles of Rational Drug Use"),
    (5, "Introduction to Nervous System Pharmacology"),
    (6, "Cholinergic Receptor Agonists"),
]


def main():
    print("=" * 60)
    print("PHARMACOLOGY QUIZ BANK TRANSLATION (Ch 1-6)")
    print("Chinese -> English (Google Translate concurrent + post-correction)")
    print("=" * 60)

    # Phase 1: Collect all unique Chinese texts
    print("\nPhase 1: Collecting unique Chinese texts...")
    unique_texts = collect_unique_texts(CHAPTERS)
    print(f"  Found {len(unique_texts)} unique Chinese text segments needing translation")
    simple_count = len(SIMPLE_MAP)
    print(f"  {simple_count} texts handled by simple dictionary (types, categories, True/False)")

    # Phase 2: Translate all unique texts concurrently
    print(f"\nPhase 2: Translating {len(unique_texts)} unique texts (concurrent, 8 workers)...")
    t_start = time.time()
    translator = FastTranslator(max_workers=8)
    translations = translator.translate_batch(list(unique_texts))
    elapsed = time.time() - t_start
    print(f"  Completed {len(translations)} translations in {elapsed:.0f}s "
          f"({len(translations)/elapsed:.1f} texts/s)")
    print(f"  Errors: {translator.errors}")

    # Phase 3: Apply translations to each chapter CSV
    print("\nPhase 3: Writing translated CSV files...")
    for ch_num, topic in CHAPTERS:
        process_chapter(ch_num, topic, translations)

    print(f"\n{'='*60}")
    print("TRANSLATION COMPLETE")
    print(f"Total time: {time.time() - t_start:.0f}s")
    print("=" * 60)
    for ch_num, _ in CHAPTERS:
        print(f"  {os.path.join(WORK_DIR, f'pharma_en_ch{ch_num:02d}.csv')}")


if __name__ == "__main__":
    main()
