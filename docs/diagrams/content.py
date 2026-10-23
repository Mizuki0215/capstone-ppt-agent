"""Single source of truth for the status diagrams.

Both the landscape figure (make_status.py) and the phone figure (make_phone.py)
read from here, so a change of wording or status cannot drift between them.

Status vocabulary:
    done     built and tested      green
    partial  something works, the job is not closed   amber
    planned  not started           grey, dashed

"AI" marks the four blocks where a language model is used. Everything else is
a fixed rule.
"""

# name, technical label, plain-language line, status, uses a model
PIPELINE = [
    ("parse.py", "sections · figures · sentences", "把論文拆開：邊段講背景、邊段講方法", "done", False),
    ("claims", "per section, evidence id", "每段抽一句重點，並記住它出自哪一行", "planned", True),
    ("requirement", "free text → 5-field table", "聽明你的要求：講幾分鐘、聽眾是誰", "partial", True),
    ("select", "rule table, 1/0 per claim", "用規則決定邊啲重點要講、邊啲唔講", "partial", False),
    ("outline", "global, re-orders evidence", "把要講的重點排成一條故事線", "planned", True),
    ("bullets + notes", "compressed, timed", "壓成一句 bullet，再寫成講稿連時間", "partial", True),
    ("render.py", "python-pptx, native shapes", "真正畫出 .pptx，之後仲改得", "done", False),
]

# name, threshold, plain-language line, status
GATES = [
    ("G1 containment", "0 pt", "有東西跑出畫面外嗎", "done"),
    ("G2 overlap", ">5%", "兩段字疊在一起嗎", "done"),
    ("G3 font size", "角色下限", "字夠大嗎，後排看得清嗎", "done"),
    ("G4 contrast", "4.5:1", "字和底色夠分明嗎", "partial"),
    ("G5 text fit", "≤0.95", "字有沒有擠爆個框", "partial"),
    ("G6 density", "角色上限", "一頁塞太多字了嗎", "done"),
]

SCORES = [
    ("SRR", "六項合成一個分數", "0–1，愈高愈好", "partial"),
    ("deck-ready", "全頁都合格才算", "夠不夠格直接上台", "partial"),
]

# name, technical label, plain-language line
CONTROL = [
    ("1 · measure", "worst violation first", "先量一次，找出最嚴重那一項"),
    ("2 · repair", "cheapest reversible action", "用最便宜、可以還原的方法修"),
    ("3 · re-measure", "ΔSRR per second / per $", "再量一次：改善幾多、花幾多"),
    ("guardrail", "no new text, no numbers", "唔准加內容、唔准改數字"),
    ("the claim under test", "A2 − A1", "開著檢查 vs 關掉檢查，差別就係檢查的價值"),
]
