#!/usr/bin/env python3
"""Build bilingual index.html with language toggle for all 46 chapters."""
import os

CN_PARTS = [
    ("第一篇  总论", [
        (1, "绪论", 50), (2, "药物效应动力学", 75), (3, "药物代谢动力学", 100), (4, "影响药物效应的因素及合理用药原则", 50),
    ]),
    ("第二篇  外周神经系统药理学", [
        (5, "神经系统药理概论", 100), (6, "胆碱受体激动药", 30), (7, "抗胆碱酯酶药和胆碱酯酶复活药", 50),
        (8, "胆碱受体阻断药", 50), (9, "肾上腺素受体激动药", 50), (10, "肾上腺素受体阻断药", 50),
        (11, "局部麻醉药", 30), (12, "全身麻醉药", 30),
    ]),
    ("第三篇  中枢神经系统药理学", [
        (13, "镇静催眠药和促觉醒药", 50), (14, "抗癫痫药与抗惊厥药", 50), (15, "治疗神经退行性变性疾病药物", 50),
        (16, "抗精神失常药", 50), (17, "阿片类镇痛药、药物依赖性与药物滥用", 75), (18, "解热镇痛抗炎药", 75),
        (19, "影响其他自身活性物质的药物", 75), (20, "免疫调节药", 50),
    ]),
    ("第四篇  心血管系统药理学", [
        (21, "利尿药与脱水药", 30), (22, "抗心律失常药", 75), (23, "抗心肌缺血药", 50),
        (24, "调血脂药和抗动脉粥样硬化药", 50), (25, "抗高血压药", 75), (26, "抗慢性心功能不全药", 75),
        (27, "作用于血液及造血器官的药物", 75), (28, "作用于呼吸系统的药物", 50), (29, "作用于消化系统的药物", 75),
    ]),
    ("第五篇  内分泌系统药理学", [
        (30, "子宫平滑肌兴奋药和抑制药", 30), (31, "肾上腺皮质激素类药物", 50), (32, "抗糖尿病药", 50),
        (33, "甲状腺激素和抗甲状腺药", 30), (34, "性激素类药与避孕药", 50), (35, "抗骨质疏松药", 30),
    ]),
    ("第七篇  化学治疗药物", [
        (36, "抗菌药物概论", 100), (37, "β-内酰胺类抗生素及其他作用于细胞壁的抗生素", 100),
        (38, "大环内酯类、林可霉素类及其他抗生素", 50), (39, "氨基糖苷类及多黏菌素类抗生素", 75),
        (40, "四环素类及氯霉素类抗生素", 50), (41, "人工合成抗菌药", 100),
        (42, "抗结核病药及抗麻风药", 50), (43, "抗真菌药", 50), (44, "抗病毒药", 100),
        (45, "抗寄生虫药", 50), (46, "抗恶性肿瘤药", 100),
    ]),
]

EN_PARTS = [
    ("Part 1: General Principles", [
        (1, "Introduction to Pharmacology", 50), (2, "Pharmacodynamics", 75),
        (3, "Pharmacokinetics", 100), (4, "Factors Affecting Drug Effects and Rational Use", 50),
    ]),
    ("Part 2: Peripheral Nervous System Pharmacology", [
        (5, "Nervous System Pharmacology Overview", 100), (6, "Cholinergic Receptor Agonists", 30),
        (7, "Anticholinesterases and Cholinesterase Reactivators", 50), (8, "Cholinergic Receptor Blockers", 50),
        (9, "Adrenoceptor Agonists", 50), (10, "Adrenoceptor Blockers", 50),
        (11, "Local Anesthetics", 30), (12, "General Anesthetics", 30),
    ]),
    ("Part 3: Central Nervous System Pharmacology", [
        (13, "Sedative-Hypnotics and Wakefulness-Promoting Drugs", 50),
        (14, "Antiepileptic and Anticonvulsant Drugs", 50),
        (15, "Drugs for Neurodegenerative Diseases", 50),
        (16, "Drugs for Mental Disorders", 50), (17, "Opioid Analgesics, Drug Dependence and Abuse", 75),
        (18, "NSAIDs and Antirheumatic Drugs", 75), (19, "Drugs Affecting Autacoids", 75),
        (20, "Immunomodulators", 50),
    ]),
    ("Part 4: Cardiovascular System Pharmacology", [
        (21, "Diuretics and Dehydrating Agents", 30), (22, "Antiarrhythmic Drugs", 75),
        (23, "Antianginal Drugs", 50), (24, "Lipid-Lowering and Antiatherosclerotic Drugs", 50),
        (25, "Antihypertensive Drugs", 75), (26, "Drugs for Chronic Heart Failure", 75),
        (27, "Drugs Affecting Blood and Hematopoietic Organs", 75),
        (28, "Drugs Acting on the Respiratory System", 50),
        (29, "Drugs Acting on the Digestive System", 75),
    ]),
    ("Part 5: Endocrine System Pharmacology", [
        (30, "Uterine Smooth Muscle Stimulants and Relaxants", 30),
        (31, "Adrenocortical Hormone Drugs", 50), (32, "Antidiabetic Drugs", 50),
        (33, "Thyroid Hormones and Antithyroid Drugs", 30),
        (34, "Sex Hormones and Contraceptives", 50), (35, "Anti-Osteoporosis Drugs", 30),
    ]),
    ("Part 7: Chemotherapeutic Drugs", [
        (36, "General Principles of Antibacterial Drugs", 100),
        (37, "Beta-Lactam Antibiotics and Other Cell Wall-Active Antibiotics", 100),
        (38, "Macrolides, Lincomycins, and Other Antibiotics", 50),
        (39, "Aminoglycosides and Polymyxins", 75),
        (40, "Tetracyclines and Chloramphenicol", 50),
        (41, "Synthetic Antibacterial Drugs", 100),
        (42, "Antituberculosis and Antileprosy Drugs", 50),
        (43, "Antifungal Drugs", 50), (44, "Antiviral Drugs", 100),
        (45, "Antiparasitic Drugs", 50), (46, "Antineoplastic Drugs", 100),
    ]),
]

COLORS = [
    ("#ebf4ff","#2b6cb0"), ("#f0fff4","#276749"), ("#fffbeb","#975a16"),
    ("#faf5ff","#6b46c1"), ("#fff5f5","#c53030"), ("#f0fff4","#276749"),
    ("#ebf8ff","#2c5282"), ("#fffbeb","#975a16"),
]

def build_cards(parts, suffix, color_start=0):
    html = ""
    ci = color_start
    for part_title, chapters in parts:
        html += f'\n<div class="section-title">{part_title}</div>\n'
        for ch_num, ch_title, q_count in chapters:
            c = COLORS[ci % 8]
            html += f'''<div class="card"><a href="ch{ch_num:02d}_{suffix}.html">
<div class="card-num" style="background:{c[0]};color:{c[1]}">{ch_num}</div>
<div class="card-info"><div class="card-title">{ch_title}</div><div class="card-meta">{q_count} questions</div></div>
<div class="arr">&#8250;</div>
</a></div>\n'''
            ci += 1
    return html

cn_cards = build_cards(CN_PARTS, "cn")
en_cards = build_cards(EN_PARTS, "en")

cn_total = sum(q for _, chs in CN_PARTS for _, _, q in chs)

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
.lang-btn.cn{{}} .lang-btn.en{{}}
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
<p>46 Chapters · {cn_total} Questions · True/False &amp; Single Choice &amp; Multiple Choice</p>
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
print(f"Chinese links: chXX_cn.html, English links: chXX_en.html")
