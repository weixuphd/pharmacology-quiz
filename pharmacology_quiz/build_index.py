#!/usr/bin/env python3
"""Build comprehensive index.html for all 46 pharmacology chapters.

Reads question counts dynamically from CSV files.
"""
import csv
import json
import os

PARTS = [
    ("第一篇  总论", [1, 2, 3, 4]),
    ("第二篇  外周神经系统药理学", [5, 6, 7, 8, 9, 10, 11, 12]),
    ("第三篇  中枢神经系统药理学", [13, 14, 15, 16, 17, 18, 19, 20]),
    ("第四篇  心血管系统药理学", [21, 22, 23, 24, 25, 26, 27, 28, 29]),
    ("第五篇  内分泌系统药理学", [30, 31, 32, 33, 34, 35]),
    ("第七篇  化学治疗药物", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]),
]

CHAPTER_NAMES = {
    1: "绪论",
    2: "药物效应动力学",
    3: "药物代谢动力学",
    4: "影响药物效应的因素及合理用药原则",
    5: "神经系统药理概论",
    6: "胆碱受体激动药",
    7: "抗胆碱酯酶药和胆碱酯酶复活药",
    8: "胆碱受体阻断药",
    9: "肾上腺素受体激动药",
    10: "肾上腺素受体阻断药",
    11: "局部麻醉药",
    12: "全身麻醉药",
    13: "镇静催眠药和促觉醒药",
    14: "抗癫痫药与抗惊厥药",
    15: "治疗神经退行性变性疾病药物",
    16: "抗精神失常药",
    17: "阿片类镇痛药、药物依赖性与药物滥用",
    18: "解热镇痛抗炎药",
    19: "影响其他自身活性物质的药物",
    20: "免疫调节药",
    21: "利尿药与脱水药",
    22: "抗心律失常药",
    23: "抗心肌缺血药",
    24: "调血脂药和抗动脉粥样硬化药",
    25: "抗高血压药",
    26: "抗慢性心功能不全药",
    27: "作用于血液及造血器官的药物",
    28: "作用于呼吸系统的药物",
    29: "作用于消化系统的药物",
    30: "子宫平滑肌兴奋药和抑制药",
    31: "肾上腺皮质激素类药物",
    32: "抗糖尿病药",
    33: "甲状腺激素和抗甲状腺药",
    34: "性激素类药与避孕药",
    35: "抗骨质疏松药",
    36: "抗菌药物概论",
    37: "β-内酰胺类抗生素及其他作用于细胞壁的抗生素",
    38: "大环内酯类、林可霉素类及其他抗生素",
    39: "氨基糖苷类及多黏菌素类抗生素",
    40: "四环素类及氯霉素类抗生素",
    41: "人工合成抗菌药",
    42: "抗结核病药及抗麻风药",
    43: "抗真菌药",
    44: "抗病毒药",
    45: "抗寄生虫药",
    46: "抗恶性肿瘤药",
}

COLORS = [
    ("#ebf4ff", "#2b6cb0"),  # blue
    ("#f0fff4", "#276749"),  # green
    ("#fffbeb", "#975a16"),  # amber
    ("#faf5ff", "#6b46c1"),  # purple
    ("#fff5f5", "#c53030"),  # red
    ("#f0fff4", "#276749"),  # green
    ("#ebf8ff", "#2c5282"),  # blue
    ("#fffbeb", "#975a16"),  # amber
    ("#faf5ff", "#6b46c1"),  # purple
    ("#fff5f5", "#c53030"),  # red
    ("#ebf4ff", "#2b6cb0"),  # blue
]


def count_questions(csv_path):
    """Count questions by type from a CSV file."""
    counts = {}
    total = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            t = row.get('type', 'unknown').strip()
            counts[t] = counts.get(t, 0) + 1
    return total, counts


def build_q_types_string(counts):
    """Build a human-readable string like '10+35+10+10' for question types."""
    order = ['是非题', '单选题', '名词解释', '简答题', '简答题(多选)']
    parts = []
    for t in order:
        if t in counts and counts[t] > 0:
            parts.append(str(counts[t]))
    # Include any other types not in the predefined order
    for t, c in sorted(counts.items()):
        if t not in order and c > 0:
            parts.append(f"{t}:{c}")
    return '+'.join(parts) if parts else str(total)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
total_questions = 0
cards_html = ""
color_idx = 0

for part_title, chapter_nums in PARTS:
    cards_html += f'\n<div class="section-title">{part_title}</div>\n'
    for ch_num in chapter_nums:
        csv_path = os.path.join(SCRIPT_DIR, f"pharma_cn_ch{ch_num:02d}.csv")
        en_path = os.path.join(SCRIPT_DIR, f"pharma_en_ch{ch_num:02d}.csv")

        if os.path.exists(csv_path):
            total, counts = count_questions(csv_path)
        elif os.path.exists(en_path):
            total, counts = count_questions(en_path)
        else:
            total = 0
            counts = {}

        color = COLORS[color_idx % len(COLORS)]
        q_types_str = build_q_types_string(counts)
        ch_name = CHAPTER_NAMES.get(ch_num, f"第{ch_num}章")
        cards_html += f'''<div class="card c{color_idx % 8 + 1}"><a href="ch{ch_num:02d}_cn.html">
<div class="card-num">{ch_num}</div>
<div class="card-info"><div class="card-title">{ch_name}</div><div class="card-meta"><span>{total}题</span><span>{q_types_str}</span></div></div>
<div class="arr">&#8250;</div>
</a></div>
'''
        color_idx += 1
        total_questions += total

FULL_HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="药理学题库">
<meta itemprop="name" content="药理学题库">
<meta itemprop="description" content="药理学全教材题库训练 · 共46章 {total_questions}题">
<meta name="twitter:card" content="summary">
<title>药理学题库</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f0f4f8;color:#1a202c;min-height:100vh}}
.header{{background:linear-gradient(135deg,#2c5282,#38a169);color:#fff;padding:28px 16px 24px;text-align:center}}
.header h1{{font-size:1.5rem;font-weight:700;margin-bottom:5px}}
.header p{{font-size:.85rem;opacity:.85;margin-top:4px}}
.container{{max-width:680px;margin:0 auto;padding:12px}}
.section-title{{font-size:.82rem;font-weight:600;color:#4a5568;padding:14px 8px 6px;text-transform:uppercase;letter-spacing:.5px}}
.card{{background:#fff;border-radius:10px;margin-bottom:4px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden}}
.card a{{display:flex;align-items:center;padding:12px 16px;text-decoration:none;color:#1a202c;transition:background .15s}}
.card a:active{{background:#edf2f7}}
.card-num{{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem;margin-right:12px;flex-shrink:0}}
.card-info{{flex:1;min-width:0}}
.card-title{{font-size:.88rem;font-weight:600;margin-bottom:2px}}
.card-meta{{font-size:.7rem;color:#718096}}
.card-meta span{{margin-right:8px}}
.arr{{color:#a0aec0;font-size:1rem;margin-left:6px}}
.footer{{text-align:center;padding:20px;color:#a0aec0;font-size:.72rem}}
.c1 .card-num{{background:#ebf4ff;color:#2b6cb0}}
.c2 .card-num{{background:#f0fff4;color:#276749}}
.c3 .card-num{{background:#fffbeb;color:#975a16}}
.c4 .card-num{{background:#faf5ff;color:#6b46c1}}
.c5 .card-num{{background:#fff5f5;color:#c53030}}
.c6 .card-num{{background:#f0fff4;color:#276749}}
.c7 .card-num{{background:#ebf8ff;color:#2c5282}}
.c8 .card-num{{background:#fffbeb;color:#975a16}}
</style>
</head>
<body>
<div class="header">
<h1>药理学 · 题库训练</h1>
<p>全教材共46章 · 总计{total_questions}题 · 各章含是非题/单选题/名词解释/简答题</p>
</div>
<div class="container">
{cards_html}
</div>
<div class="footer">药理学题库 &copy; 2026 · 仅供教学使用 · 有效期至2026-12-31</div>
</body>
</html>'''

output_path = os.path.join(SCRIPT_DIR, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(FULL_HTML)
print(f"index.html written: {total_questions} questions across {color_idx} chapters")
