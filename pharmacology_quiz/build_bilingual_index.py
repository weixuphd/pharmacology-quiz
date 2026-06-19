#!/usr/bin/env python3
"""Build bilingual index.html with language toggle for all 46 chapters.
Counts questions dynamically from CN CSV files."""
import csv, os

PARTS = [
    ("第一篇  总论", [1, 2, 3, 4]),
    ("Part 1: General Principles", [1, 2, 3, 4]),
    ("第二篇  作用于神经系统的药物", [5, 6, 7, 8, 9, 10, 11, 12]),
    ("Part 2: Drugs Acting on the Nervous System", [5, 6, 7, 8, 9, 10, 11, 12]),
    ("第三篇  影响自身活性物质和免疫功能的药物", [13, 14, 15, 16, 17, 18, 19, 20]),
    ("Part 3: Drugs Affecting Autacoids and Immunity", [13, 14, 15, 16, 17, 18, 19, 20]),
    ("第四篇  作用于肾脏和心血管系统的药物", [21, 22, 23, 24, 25, 26, 27, 28, 29]),
    ("Part 4: Drugs Acting on Kidney and Cardiovascular System", [21, 22, 23, 24, 25, 26, 27, 28, 29]),
    ("第五篇  作用于血液和内脏系统的药物", [30, 31, 32, 33, 34, 35]),
    ("Part 5: Drugs Acting on Blood and Viscera", [30, 31, 32, 33, 34, 35]),
    ("第六篇  作用于内分泌系统和影响代谢的药物", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]),
    ("Part 6: Drugs Acting on Endocrine System and Metabolism", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]),
]

CHAPTER_NAMES_CN = {
    1: "绪论", 2: "药物效应动力学", 3: "药物代谢动力学",
    4: "影响药物效应的因素及合理用药原则", 5: "神经系统药理概论",
    6: "胆碱受体激动药", 7: "抗胆碱酯酶药和胆碱酯酶复活药",
    8: "胆碱受体阻断药", 9: "肾上腺素受体激动药",
    10: "肾上腺素受体阻断药", 11: "局部麻醉药", 12: "全身麻醉药",
    13: "镇静催眠药和促觉醒药", 14: "抗癫痫药与抗惊厥药",
    15: "治疗神经退行性变性疾病药物", 16: "抗精神失常药",
    17: "阿片类镇痛药、药物依赖性与药物滥用", 18: "解热镇痛抗炎药",
    19: "影响其他自身活性物质的药物", 20: "免疫调节药",
    21: "利尿药与脱水药", 22: "抗心律失常药", 23: "抗心肌缺血药",
    24: "调血脂药和抗动脉粥样硬化药", 25: "抗高血压药",
    26: "抗慢性心功能不全药", 27: "作用于血液及造血器官的药物",
    28: "作用于呼吸系统的药物", 29: "作用于消化系统的药物",
    30: "子宫平滑肌兴奋药和抑制药", 31: "肾上腺皮质激素类药物",
    32: "抗糖尿病药", 33: "甲状腺激素和抗甲状腺药",
    34: "性激素类药与避孕药", 35: "抗骨质疏松药",
    36: "抗菌药物概论",
    37: "β-内酰胺类抗生素及其他作用于细胞壁的抗生素",
    38: "大环内酯类、林可霉素类及其他抗生素",
    39: "氨基糖苷类及多黏菌素类抗生素",
    40: "四环素类及氯霉素类抗生素",
    41: "人工合成抗菌药", 42: "抗结核病药及抗麻风药",
    43: "抗真菌药", 44: "抗病毒药", 45: "抗寄生虫药", 46: "抗恶性肿瘤药",
}

CHAPTER_NAMES_EN = {
    1: "Introduction", 2: "Pharmacodynamics", 3: "Pharmacokinetics",
    4: "Factors Affecting Drug Effects and Rational Use",
    5: "Nervous System Pharmacology Overview", 6: "Cholinergic Receptor Agonists",
    7: "Anticholinesterases and Cholinesterase Reactivators",
    8: "Cholinergic Receptor Blockers", 9: "Adrenoceptor Agonists",
    10: "Adrenoceptor Blockers", 11: "Local Anesthetics", 12: "General Anesthetics",
    13: "Sedative-Hypnotics and Wakefulness-Promoting Drugs",
    14: "Antiepileptic and Anticonvulsant Drugs",
    15: "Drugs for Neurodegenerative Diseases", 16: "Drugs for Mental Disorders",
    17: "Opioid Analgesics, Drug Dependence and Abuse",
    18: "Antipyretic Analgesics and Anti-Inflammatory Drugs",
    19: "Drugs Affecting Other Autacoids", 20: "Immunomodulators",
    21: "Diuretics and Dehydrating Agents", 22: "Antiarrhythmic Drugs",
    23: "Antianginal Drugs", 24: "Lipid-Lowering and Antiatherosclerotic Drugs",
    25: "Antihypertensive Drugs", 26: "Drugs for Chronic Heart Failure",
    27: "Drugs Affecting Blood and Hematopoietic Organs",
    28: "Drugs Acting on the Respiratory System",
    29: "Drugs Acting on the Digestive System",
    30: "Uterine Smooth Muscle Stimulants and Relaxants",
    31: "Adrenocortical Hormone Drugs", 32: "Antidiabetic Drugs",
    33: "Thyroid Hormones and Antithyroid Drugs",
    34: "Sex Hormones and Contraceptives", 35: "Anti-Osteoporosis Drugs",
    36: "General Principles of Antibacterial Drugs",
    37: "Beta-Lactam and Other Cell Wall-Active Antibiotics",
    38: "Macrolides, Lincomycins, and Other Antibiotics",
    39: "Aminoglycosides and Polymyxins",
    40: "Tetracyclines and Chloramphenicol",
    41: "Synthetic Antibacterial Drugs",
    42: "Antituberculosis and Antileprosy Drugs",
    43: "Antifungal Drugs", 44: "Antiviral Drugs",
    45: "Antiparasitic Drugs", 46: "Antineoplastic Drugs",
}

COLORS = [
    ("#ebf4ff", "#2b6cb0"), ("#f0fff4", "#276749"), ("#fffbeb", "#975a16"),
    ("#faf5ff", "#6b46c1"), ("#fff5f5", "#c53030"), ("#f0fff4", "#276749"),
    ("#ebf8ff", "#2c5282"), ("#fffbeb", "#975a16"),
]


def count_questions(csv_path):
    total = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for _ in reader:
            total += 1
    return total


def build_section_cards(part_title, chapters, names_dict, suffix, ci_start):
    html = f'\n<div class="section-title">{part_title}</div>\n'
    ci = ci_start
    for ch_num in chapters:
        csv_path = os.path.join(SCRIPT_DIR, f"pharma_cn_ch{ch_num:02d}.csv")
        q_count = count_questions(csv_path) if os.path.exists(csv_path) else 0
        ch_title = names_dict.get(ch_num, f"Chapter {ch_num}")
        c = COLORS[ci % 8]
        html += f'''<div class="card"><a href="ch{ch_num:02d}_{suffix}.html">
<div class="card-num" style="background:{c[0]};color:{c[1]}">{ch_num}</div>
<div class="card-info"><div class="card-title">{ch_title}</div><div class="card-meta">{q_count} questions</div></div>
<div class="arr">&#8250;</div>
</a></div>\n'''
        ci += 1
    return html, ci


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build cards for each part (CN and EN alternate)
cn_cards = ""
en_cards = ""
ci = 0
for i in range(0, len(PARTS), 2):
    cn_part_title = PARTS[i][0]
    cn_chapters = PARTS[i][1]
    en_part_title = PARTS[i + 1][0]
    en_chapters = PARTS[i + 1][1]

    cn_section, ci = build_section_cards(cn_part_title, cn_chapters, CHAPTER_NAMES_CN, "cn", ci)
    cn_cards += cn_section

    en_section, ci = build_section_cards(en_part_title, en_chapters, CHAPTER_NAMES_EN, "en", ci)
    en_cards += en_section

# Calculate total
cn_total = 0
for ch in range(1, 47):
    csv_path = os.path.join(SCRIPT_DIR, f"pharma_cn_ch{ch:02d}.csv")
    if os.path.exists(csv_path):
        cn_total += count_questions(csv_path)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<title>Pharmacology Quiz Bank / 药理学题库</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#f0f4f8;color:#1a202c;min-height:100vh}}
.header{{background:linear-gradient(135deg,#2c5282,#38a169);color:#fff;padding:20px 16px 18px;text-align:center}}
.header h1{{font-size:1.4rem;font-weight:700;margin-bottom:4px}}
.header p{{font-size:.82rem;opacity:.85}}
.lang-bar{{display:flex;justify-content:center;gap:0;padding:14px 12px 10px;background:#fff;border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:100}}
.lang-btn{{padding:8px 28px;border:2px solid #e2e8f0;font-size:.85rem;font-weight:600;cursor:pointer;font-family:inherit;background:#fff;color:#718096;transition:all .15s}}
.lang-btn:first-child{{border-radius:8px 0 0 8px}}
.lang-btn:last-child{{border-radius:0 8px 8px 0}}
.lang-btn.active{{background:#2c5282;color:#fff;border-color:#2c5282}}
.container{{max-width:680px;margin:0 auto;padding:10px 12px}}
.section-title{{font-size:.8rem;font-weight:600;color:#4a5568;padding:12px 6px 4px;letter-spacing:.5px}}
.card{{background:#fff;border-radius:10px;margin-bottom:4px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden}}
.card a{{display:flex;align-items:center;padding:11px 14px;text-decoration:none;color:#1a202c}}
.card a:active{{background:#edf2f7}}
.card-num{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.78rem;margin-right:12px;flex-shrink:0}}
.card-info{{flex:1;min-width:0}}
.card-title{{font-size:.86rem;font-weight:600;margin-bottom:2px}}
.card-meta{{font-size:.7rem;color:#718096}}
.arr{{color:#a0aec0;font-size:1rem;margin-left:6px}}
.footer{{text-align:center;padding:20px;color:#a0aec0;font-size:.7rem}}
.cn-list,.en-list{{display:none}}
.cn-list.show,.en-list.show{{display:block}}
</style>
</head>
<body>
<div class="header">
<h1>Pharmacology Quiz Bank</h1>
<p>46 Chapters · {cn_total} Questions · True/False &amp; Single Choice &amp; Terminology &amp; Short Answer</p>
</div>
<div class="lang-bar">
<button class="lang-btn cn active" onclick="switchLang('cn')">中文</button>
<button class="lang-btn en" onclick="switchLang('en')">English</button>
</div>
<div class="container">
<div class="cn-list show" id="cnList">
{cn_cards}
</div>
<div class="en-list" id="enList">
{en_cards}
</div>
</div>
<div class="footer">Pharmacology Quiz Bank &copy; 2026 · For Educational Use Only · Expires 2026-12-31</div>
<script>
function switchLang(lang){{
  document.getElementById('cnList').classList.toggle('show', lang==='cn');
  document.getElementById('enList').classList.toggle('show', lang==='en');
  document.querySelectorAll('.lang-btn').forEach(function(b){{
    b.classList.toggle('active', b.classList.contains(lang));
  }});
  try{{localStorage.setItem('_quiz_lang', lang)}}catch(e){{}}
}}
(function(){{
  var saved=null;
  try{{saved=localStorage.getItem('_quiz_lang')}}catch(e){{}}
  if(saved==='en')switchLang('en');
}})();
</script>
</body>
</html>'''

out = os.path.join(os.path.dirname(__file__), "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Bilingual index.html written: {out}")
print(f"Total questions: {cn_total}")
