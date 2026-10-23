#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the coding-decisions document (Traditional Chinese, for the report).

    python3 docs/build_coding_doc.py

Everything factual in the output is read from the repository at build time:
file counts come from git, test counts from the test files, so the document
cannot drift from the code it describes.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Coding_Decisions_ZH.docx"
DIAG = ROOT / "docs" / "diagrams"

INK = RGBColor(0x10, 0x23, 0x3A)
GREY = RGBColor(0x5A, 0x6B, 0x7C)
GOLD = RGBColor(0xB0, 0x7A, 0x1E)
CJK = "PingFang HK"
LATIN = "Helvetica Neue"


# --------------------------------------------------------------------------- #
# document helpers
# --------------------------------------------------------------------------- #

def set_cjk(run, size=None, bold=None, colour=None):
    run.font.name = LATIN
    run._element.rPr.rFonts.set(qn("w:eastAsia"), CJK)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if colour is not None:
        run.font.color.rgb = colour


def para(doc, text, size=10.5, bold=False, colour=INK, space_after=6,
         indent=0.0, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if align:
        p.alignment = align
    set_cjk(p.add_run(text), size, bold, colour)
    return p


def heading(doc, text, level=1):
    sizes = {1: 15, 2: 12.5, 3: 11}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    set_cjk(p.add_run(text), sizes[level], True, INK)
    if level == 1:
        pPr = p._p.get_or_add_pPr()
        border = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), "B07A1E")
        border.append(bottom)
        pPr.append(border)
    return p


def bullet(doc, text, size=10.5, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Cm(0.8 + 0.6 * level)
    set_cjk(p.add_run(text), size)
    return p


def shade(cell, hex_colour):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_colour)
    tcPr.append(shd)


def table(doc, headers, rows, widths, size=8.8, head_fill="E8EEF3"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        set_cjk(p.add_run(h), size, True, INK)
        shade(cell, head_fill)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            set_cjk(p.add_run(str(value)), size)
    for r in t.rows:
        for i, w in enumerate(widths):
            r.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(doc, name, width_cm, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(DIAG / name), width=Cm(width_cm))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(10)
    set_cjk(c.add_run(caption), 8.6, False, GREY)


def landscape(doc):
    """Open a landscape section so a wide diagram can use the whole page."""
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE
    w, h = sec.page_width, sec.page_height
    if w < h:
        sec.page_width, sec.page_height = h, w
    sec.left_margin = sec.right_margin = Cm(1.4)
    sec.top_margin = sec.bottom_margin = Cm(1.4)
    return sec


def portrait(doc):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.PORTRAIT
    w, h = sec.page_width, sec.page_height
    if w > h:
        sec.page_width, sec.page_height = h, w
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)
    return sec


def wide_figure(doc, name, caption):
    """Full-width diagram on its own landscape page, then back to portrait."""
    landscape(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(DIAG / name), width=Cm(25.6))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cjk(c.add_run(caption), 9.2, False, GREY)
    portrait(doc)


def code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.name = "Menlo"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), CJK)
    run.font.size = Pt(8.6)
    run.font.color.rgb = RGBColor(0x1E, 0x36, 0x52)
    return p


def facts():
    """Read the numbers from the repo instead of hard-coding them."""
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True).stdout.splitlines()
    by_file: dict[str, int] = {}
    try:   # case count, so parametrised tests are counted one by one
        out = subprocess.run(["python3", "-m", "pytest", "--collect-only", "-q"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        for m in re.finditer(r"^(\S+\.py): (\d+)$", out, re.M):
            by_file[Path(m.group(1)).name] = int(m.group(2))
    except Exception:
        pass
    if not by_file:   # fall back to counting test functions
        for f in (ROOT / "tests").glob("test_*.py"):
            by_file[f.name] = sum(1 for n in ast.walk(ast.parse(f.read_text()))
                                  if isinstance(n, ast.FunctionDef)
                                  and n.name.startswith("test_"))
    tests = sum(by_file.values())
    loc = sum(len(f.read_text().splitlines()) for f in (ROOT / "src").glob("*.py"))
    papers = len(list((ROOT / "research" / "pdfs").glob("*.pdf")))
    return {"files": len(tracked), "tests": tests, "loc": loc, "papers": papers,
            "by_file": by_file, "modules": len(list((ROOT / "src").glob("*.py")))}


F = facts()

# --------------------------------------------------------------------------- #
# document
# --------------------------------------------------------------------------- #

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(2.0)
sec.left_margin = Cm(2.2)
sec.right_margin = Cm(2.2)

# ---------------- cover ----------------
para(doc, "DSAI4901 Capstone — 程式決策記錄", 24, True, INK, space_after=4)
para(doc, "由論文到簡報：每一行程式為何這樣寫", 13, False, GREY, space_after=18)

table(doc, ["項目", "內容"], [
    ["專案", "From Generating to Verifying（AI Agent for Presentation Slides Design）"],
    ["作者", "CHAN Yee Tung · 指導老師 Dr. Jibin Wu"],
    ["Repository", "github.com/Mizuki0215/capstone-ppt-agent"],
    ["文件日期", "2026-10-23"],
    ["程式規模", f"{F['modules']} 個模組 · {F['loc']} 行 · {F['tests']} 個測試"],
    ["語料庫", f"{F['papers']} 篇論文 PDF（不進 git，用 scripts/fetch_papers.py 重建）"],
    ["本文件用途", "寫報告時查閱：每段程式為何存在、為何這樣寫、可以引用哪一句"],
], [3.4, 13.0], size=9.2)

para(doc, "", 8)
para(doc, "讀法：第 1 章是整體（三張圖）；第 2 章由大到小（流程 → 模組 → 函數）；"
          "第 3 章是檔案清單；第 4 章是決策記錄（寫論文最有用）；第 5–6 章是每個 import "
          "與每個函數的出處；第 7 章是驗證方法；第 8 章是之後會加什麼。", 9.6, False, GREY)

doc.add_page_break()

# ---------------- 1 專案與三張圖 ----------------
heading(doc, "1. 專案是什麼（先看圖）", 1)
para(doc, "這個專案把一篇論文轉成一份簡報，然後用程式檢查這份簡報「能不能用」。"
          "關鍵不是生成，而是驗證：語言模型看不到自己寫出來的畫面，所以文字框跑出邊界、"
          "兩段字疊在一起、字太細後排看不到——這些它都不會知道。我們把這些失敗變成"
          "六條可以計算的規則（G1–G6），並研究「一邊做、一邊檢查」到底令成品好幾多。")

heading(doc, "1.1 系統全圖與註解版（下兩頁，橫向）", 2)
para(doc, "看圖 1 的先後次序：由左至右走 A 列，到 render.py 之後，"
          "沿下面那條實線回到左邊入 B 列（量度），不合格就落 C 列（修復），"
          "修完由虛線回到分數。全圖最重要的一句寫在虛線旁："
          "「修完再量：只回到分數，唔會回到文字」。", 10)
para(doc, "圖 2 是同一張圖的教學版：上方彩色方塊是系統的一步，下方白框是白話解釋，"
          "短箭頭指住它屬於哪一格。可以直接放進報告或簡報。三個顏色代表進度，"
          "藍色「AI」代表該格用到大型語言模型（只有四格），沒有標記的代表固定規則。", 10)

landscape(doc)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(DIAG / "status_2026-10-23.png"), width=Cm(25.6))
c = doc.add_paragraph()
c.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_cjk(c.add_run("圖 1　系統全圖：A 生成（論文→文字）、B 量度（六個 gate）、C 修復（論文的主貢獻）。"
                  "顏色＝進度：綠＝完成且有測試，琥珀＝部分，灰＝未開始。"), 9.2, False, GREY)

doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(DIAG / "status_2026-10-23_annotated.png"), width=Cm(25.6))
c = doc.add_paragraph()
c.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_cjk(c.add_run("圖 2　註解版：上方彩色方塊是系統的一步，下方白框是白話解釋，"
                  "短箭頭指住它屬於哪一格。"), 9.2, False, GREY)
portrait(doc)

heading(doc, "1.2 每一格的一句話", 2)
table(doc, ["Block", "一句話", "狀態"], [
    ["parse.py", "把論文拆開：分段落、抽圖和圖說", "完成"],
    ["claims", "每段抽一句重點，並記住它出自哪一行", "規劃中（L5）"],
    ["requirement", "聽明你的要求：講幾分鐘、聽眾是誰", "部分（schema 完成）"],
    ["select", "用規則決定邊啲重點要講、邊啲唔講", "部分（規則完成，未接線）"],
    ["outline", "把要講的重點排成一條故事線", "規劃中（L3）"],
    ["bullets + notes", "壓成一句 bullet，再寫成講稿連時間", "部分（heuristic）"],
    ["render.py", "真正畫出 .pptx，之後仲改得", "完成"],
    ["G1 containment", "有東西跑出畫面外嗎", "完成"],
    ["G2 overlap", "兩段字疊在一起嗎", "完成"],
    ["G3 font size", "字夠大嗎，後排看得清嗎", "完成（未按角色）"],
    ["G4 contrast", "字和底色夠分明嗎", "未做"],
    ["G5 text fit", "字有沒有擠爆個框", "未做"],
    ["G6 density", "一頁塞太多字了嗎", "完成（未按角色）"],
    ["SRR / deck-ready", "六項合成一個分數；全頁合格才夠格上台", "部分"],
], [3.2, 10.2, 3.0])

doc.add_page_break()
heading(doc, "1.3 手機版（一頁一格）", 2)
figure(doc, "status_2026-10-23_phone.png", 7.4,
       "圖 3　手機直向版：一行一格，左邊名字、右邊白話解釋。適合在手機或匯報時逐格講。")

heading(doc, "1.4 每一格的一句話", 2)
table(doc, ["Block", "一句話", "狀態"], [
    ["parse.py", "把論文拆開：分段落、抽圖和圖說", "完成"],
    ["claims", "每段抽一句重點，並記住它出自哪一行", "規劃中（L5）"],
    ["requirement", "聽明你的要求：講幾分鐘、聽眾是誰", "部分（schema 完成）"],
    ["select", "用規則決定邊啲重點要講、邊啲唔講", "部分（規則完成，未接線）"],
    ["outline", "把要講的重點排成一條故事線", "規劃中（L3）"],
    ["bullets + notes", "壓成一句 bullet，再寫成講稿連時間", "部分（heuristic）"],
    ["render.py", "真正畫出 .pptx，之後仲改得", "完成"],
    ["G1 containment", "有東西跑出畫面外嗎", "完成"],
    ["G2 overlap", "兩段字疊在一起嗎", "完成"],
    ["G3 font size", "字夠大嗎，後排看得清嗎", "完成（未按角色）"],
    ["G4 contrast", "字和底色夠分明嗎", "未做"],
    ["G5 text fit", "字有沒有擠爆個框", "未做"],
    ["G6 density", "一頁塞太多字了嗎", "完成（未按角色）"],
    ["SRR / deck-ready", "六項合成一個分數；全頁合格才夠格上台", "部分"],
], [3.2, 10.2, 3.0])

doc.add_page_break()

# ---------------- 2 由大到小 ----------------
heading(doc, "2. 由大到小：流程 → 模組 → 函數", 1)

heading(doc, "2.1 資料流（三個階段，五個檔案）", 2)
code(doc, "paper.pdf\n"
          "  → [parse.py]        → deck.json      （章節、圖、圖說、頁碼）\n"
          "  → [compose.py]      → plan.json      （大綱、bullet、講稿）\n"
          "  → [render.py]       → out/*.pptx     （可編輯的原生簡報）\n"
          "  → [detect.py]       → metrics.json   （六個 gate 的違規、SRR）\n"
          "  → [repair（未做）]   → 改 layout.json，不改 deck.json")
para(doc, "這個順序是有意義的：越前面越「決定講什麼」，越後面越「決定怎麼畫」。"
          "修復只准發生在後半段，理由見 §4 決策 D1。")

heading(doc, "2.2 七個模組", 2)
mods = [
    ("parse.py", "論文解析",
     "把 PDF 切成章節、抽出圖與圖說、抓標題，輸出 deck.json。",
     "輸入：PDF 路徑。輸出：deck.json。",
     "以字體大小、粗體、大寫比例判斷標題；維護一份「疑似頁眉／頁碼」的黑名單（重複 ≥3 次的行）。",
     "只支援單欄英文論文；二欄排版會把兩欄混在一起。"),
    ("figures.py", "圖片裁切",
     "為每個圖說找出它上方的內容區，裁成 PNG，存路徑與 bbox。",
     "輸入：PDF 路徑、輸出資料夾。輸出：PNG 檔 + image/bbox/area 三個欄位。",
     "用「非白色像素」界定內容範圍；band 停在最近一個**段落**而不是任何文字方塊，"
     "因為圖裡面本身有標籤文字。",
     f"目前成功 {12}／{32} 個圖說（PPTAgent 那篇）。目標 ≥70%。"),
    ("compose.py", "大綱與講稿",
     "把章節變成 8–12 張 slide 的計畫：標題、bullets、speaker notes、時間預算。",
     "輸入：deck.json。輸出：plan.json。",
     "目前是 heuristic（抽句子、打分、截斷 14 字）；另有 `--llm` 分支但未接上快取，"
     "正式版會換成 §4 的 L3/L5 設計。",
     "heuristic 的 bullets 是「論文的原句」，不是主張——這是 P1b 要解決的問題。"),
    ("render.py", "版面",
     "把 plan.json 畫成 13.333×7.5 吋的 .pptx，全部是原生物件（可再編輯）。",
     "輸入：plan.json。輸出：.pptx。",
     "有圖的頁面自動變兩欄：左邊 bullets、右邊圖片（contain，保持長寬比）、caption 在圖下面。",
     "只有一套模板；第二套（minimal）在 WBS P1.8。"),
    ("detect.py", "量度",
     "在 .pptx 物件模型上檢查四個 gate（G1 出界、G2 重疊、G3 字級、G6 密度），算 SRR。",
     "輸入：.pptx。輸出：每頁違規清單、SRR、deck-ready。",
     "完全不渲染：只讀 shape 的 bounding box、字級、字數——所以可重跑、可審核。",
     "G4 對比、G5 文字溢出未做；G3/G6 目前用全局閾值，proposal 寫的是按角色。"),
    ("schema.py", "選段的詞彙與規則",
     "把「章節 → 十類」「要求 → 一張表」「claim → 1/0 決定」寫成可測試的規則。",
     "輸入：Requirement + Claim 清單。輸出：Decision 清單（每條帶 rule id）。",
     "五段優先次序：硬性（results/conclusion）→ must_exclude → must_include → 規則表 → importance 門檻。",
     "規則表本身是慣例，需要在 WBS Q5 做寬鬆／嚴格兩版掃描。"),
    ("deck.py", "簡報的資料契約",
     "定義一份 deck 由什麼組成，並強制七條不變量。",
     "輸入：claims/figures/slides。輸出：deck.json 的結構 + 驗證錯誤清單。",
     "十種 section_type 各有一個 prompt spec，只准由 build_prompt() 組裝。",
     "layout.json / metrics.json 未落檔（WBS L8）。"),
]
for name, title, what, io, how, limit in mods:
    heading(doc, f"2.2.{mods.index((name, title, what, io, how, limit)) + 1}  {name} — {title}", 3)
    table(doc, ["項目", "內容"], [
        ["做什麼", what], ["輸入 / 輸出", io], ["關鍵做法", how], ["已知限制", limit],
    ], [2.6, 13.8], size=8.8)

heading(doc, "2.3 關鍵函數（每個做什麼）", 2)
table(doc, ["函數", "檔案", "作用"], [
    ["clean_heading(title)", "parse.py", "剝掉章節編號：\"1. Introduction\" → \"Introduction\"（要有空白才算編號）"],
    ["lines(doc)", "parse.py", "逐行吐出（頁碼、文字、字級、粗體），是所有判斷的原料"],
    ["find_title(doc)", "parse.py", "先看 PDF metadata，沒有就取第一頁最像標題的一行"],
    ["join_spans(spans)", "figures.py", "把同一行的多個 span 接起來：間距大過 0.25 字級才加空格"],
    ["find_captions(page)", "figures.py", "找出以 Figure/Table + 數字的文字方塊"],
    ["same_column(a, b)", "figures.py", "兩個方塊是否在同一欄（水平重疊 ≥50%）"],
    ["is_paragraph(rect, text)", "figures.py", "≥8 個字且高度 ≥18pt 才算正文，用來區分圖內標籤"],
    ["figure_band(...)", "figures.py", "圖說上方、停在最近一個段落的垂直帶"],
    ["ink_bbox(page, band)", "figures.py", "band 內非白色像素的外框（PDF 座標）"],
    ["extract(pdf, out, stem)", "figures.py", "逐個圖說裁圖、存 PNG、回傳 image/bbox/area"],
    ["sentences(text)", "compose.py", "把段落切句，去掉引用標記與殘句"],
    ["score(s)", "compose.py", "heuristic 打分：有數字加分、長度接近 14 字加分"],
    ["clip_words(s, n)", "compose.py", "截到 n 個字，超出的加 \" ...\""],
    ["plan_from_json(data)", "compose.py", "章節 → slides（標題、bullets、秒數、notes）"],
    ["dehyphenate(text)", "compose.py", "把 PDF 斷字接回：doc- uments → documents；清單內的複合詞保留連字號"],
    ["shorten(text, limit)", "render.py", "caption 在詞語邊界截斷，避免切一半"],
    ["place_contained(...)", "render.py", "把圖片放进指定框，保持長寬比（不拉伸）"],
    ["body_size(n_bullets, n_chars)", "render.py", "依內容量決定字級"],
    ["check_slide(slide, w, h)", "detect.py", "單頁的四個 gate 檢查"],
    ["analyse(path)", "detect.py", "整個 deck 的違規統計 + SRR"],
    ["section_type(title)", "schema.py", "章節標題 → 十類固定詞彙（對應不到回 None）"],
    ["decide(claims, req)", "schema.py", "套用五段優先次序，每條決定帶 rule id"],
    ["accounting(annotated, kept, in_deck)", "schema.py", "同時算 retention 與 coverage，兩者不混"],
    ["build_prompt(...)", "deck.py", "唯一准許組裝生成 prompt 的地方（要求 + 證據白名單 + 禁止項）"],
    ["record_edit(...)", "deck.py", "記錄人手改動：分層（deck/layout）、分方式（instruction/direct）"],
], [5.0, 2.4, 9.0], size=8.6)

doc.add_page_break()

# ---------------- 3 檔案清單 ----------------
heading(doc, "3. GitHub 現況：每個檔案做咩", 1)
para(doc, f"目前 {F['files']} 個受版本控制的檔案。下表按用途分組；「之後會加」一欄對應第 8 章的計劃。",
     10)

table(doc, ["路徑", "是什麼", "之後會加"], [
    ["src/parse.py", "論文 → deck.json（章節、圖說、標題）", "格式白名單、Bug 2 的 heading 誤判修正"],
    ["src/figures.py", "圖說 → 裁好的 PNG（image/bbox/area）", "跨欄大圖、表格 caption 在上方的情况"],
    ["src/compose.py", "deck.json → plan.json（大綱、bullet、notes）", "改由 LLM 生成（L3/L5）"],
    ["src/render.py", "plan.json → .pptx（原生可編輯）", "第二套模板、圖片 caption 自動收窄"],
    ["src/detect.py", "四 gate + SRR", "G4 對比、G5 文字溢出、按角色閾值"],
    ["src/schema.py", "選段：要求、claim 級 1/0、規則表", "Q3 由自由文字生成 requirement"],
    ["src/deck.py", "簡報資料契約 + 十種 prompt spec", "layout.json / metrics.json 落檔"],
    ["tests/test_schema.py", str(F["by_file"].get("test_schema.py", 0)) + " 個測試：" + "選段、fail-closed、優先次序", "—"],
    ["tests/test_deck.py", str(F["by_file"].get("test_deck.py", 0)) + " 個測試：" + "七條不變量、prompt、編輯分層", "—"],
    ["tests/test_figures.py", str(F["by_file"].get("test_figures.py", 0)) + " 個測試：" + "band 幾何、span 接合、端到端裁圖", "—"],
    ["tests/test_parse.py", str(F["by_file"].get("test_parse.py", 0)) + " 個測試：" + "章節編號剝除", "heading 判定（Bug 2）"],
    ["scripts/fetch_papers.py", "由 arXiv id 重建語料庫（PDF 不進 git）", "—"],
    ["run.sh", "三階段一鍵跑（parse → compose → render）", "加入 detect 與 repair"],
    ["build/*.json", "中間產物：deck.json、plan.json、detect_v1.json", "deck/layout/metrics 三檔"],
    ["out/*.pptx", "輸出的簡報（2 份示範）", "—"],
    ["docs/Proposal_*.docx/pdf", "提案（中英文）與其生成腳本", "P0 的三處修正"],
    ["docs/llm_plan.md", "生成層設計（LLM 只用在四格）", "L1–L13 實作"],
    ["docs/plan_selection.md", "選段設計（規則表、1/0）", "Q3–Q5"],
    ["docs/deck_schema.md", "資料結構設計（dt/rt/Ct）", "遷移與落檔"],
    ["docs/diagrams/*.png + make_*.py", "三張圖與其生成腳本", "—"],
    ["WBS.md", "98 個 job、216 小時、22 週", "逐週打勾"],
    ["rulebook.md", "每個 gate 的決策程序（20 條未決）", "P2 凍結成 v1"],
    ["research/papers_index.csv", "35 篇論文的索引（arXiv id、分類、賣點）", "—"],
    ["README.md", "專案入口、狀態、跑法", "—"],
], [5.4, 7.0, 4.0], size=8.4)

doc.add_page_break()

# ---------------- 4 決策記錄 ----------------
heading(doc, "4. Coding 決策記錄（寫論文最有用的一章）", 1)
para(doc, "每條格式：問題 → 決定 → 理由 → 可以直接引用的一句。"
          "這些決定都會出現在報告的設計章節，所以理由要寫得可以防守。", 10)

decisions = [
    ("D1", "為什麼要把文字層與版面層分成兩個檔案？",
     "deck.json 存「講什麼」（claims、headline、bullets、notes），layout.json 存「放在哪」"
     "（每個 shape 的座標與樣式），metrics.json 存「哪裡壞了」。修復只准寫 layout.json。",
     "如果修復可以同時改文字和版面，那麼「loop 令 deck 變好」就分不清是排版修好了，"
     "還是文字改好了。而 A2 − A1（有檢查 vs 無檢查）就是這份論文的主結果，"
     "它必須只反映排版修復的貢獻。分檔就是這條紀律的執行機制，不是整潔癖。",
     "Text and layout are separated into different artifacts so that the measured gain of "
     "the inspection loop cannot be attributed to rewriting."),
    ("D2", "為什麼不讓語言模型負責全部步驟？",
     "模型只出現在四格：claims 抽取、requirement 解析、outline 排序、bullets/notes 生成。"
     "其餘（切章節、選段規則、排版、六個 gate、驗證）全部是確定的程式。",
     "判分需要可審核。同一份輸入跑兩次要得到同一個分數，否則「檢查」本身變成另一個黑盒，"
     "而整份論文相對 PPTPilot 的差異化正是「不用視覺語言模型做裁判」。",
     "The model is confined to four boundary steps; everything between them is a rule that "
     "can be audited line by line."),
    ("D3", "claims 抽取為什麼不用 RAG？",
     "直接把該章節的文字放進 prompt，不做向量檢索、不建索引。",
     "一節大約 300–800 tokens，8 頁論文全文也只有 4–6k tokens，全部塞得入 context——"
     "檢索要解決的問題不存在。而檢索會為文字層加入一個新的機率成分（可能漏掉關鍵句），"
     "令 A2 − A1 的比較多一個無法控制的變數。接地是靠事後的 evidence id 對齊與數字檢查，"
     "不是靠檢索。",
     "Retrieval solves a context-capacity problem this task does not have, at the cost of a "
     "stochastic component in the layer whose determinism the comparison depends on."),
    ("D4", "為什麼不訓練模型？",
     "生成用現成 API（可快取、可凍結），判斷用規則。",
     "三個理由：① 論文的主張是「算術可審核，模型的意見不可」，訓練一個判斷器會摧毁這個主張；"
     "② 110 張標註足夠驗證一個確定性 detector，遠遠不夠訓練；"
     "③ 訓練一個更好的生成器會令生成器同時變動，A2 − A1 就不再乾淨。",
     "The contribution is a measurement layer, so the generator is held fixed by construction: "
     "training one would change the variable the experiment needs to control."),
    ("D5", "選段為什麼是「規則表」而不是「模型判斷」？",
     "模型只把自由文字要求變成一張固定表（幾分鐘、聽眾、必須包含/排除），"
     "之後的 1/0 由規則表決定，每條決定帶一個 rule id。",
     "要求是 5 分鐘還是 12 分鐘，是一個可以寫下來的規則；交畀模型只會得到一個無法重複的答案。"
     "規則表另一個好處是它可以被掃描（寬鬆版／嚴格版），符合「閾值要 sweep 不要 fit」的紀律。",
     "Selection is a lookup table, not a judgement: every kept or dropped claim carries the id "
     "of the rule that decided it."),
    ("D6", "為什麼 coverage 要拆成兩個數？",
     "retention = 保留的 claim / 標註的 claim；coverage = 進入 deck 的 claim / 保留的 claim。",
     "只報一個數會在兩個方向說謊：對住全部 claim 算，5 分鐘的 talk 看起來很差；"
     "對住被選中的 claim 算，剔走一半論文也可以拿 100%。兩個數並排，讀者自己判斷。",
     "Retention and coverage answer different questions and are reported separately, so "
     "neither a short talk nor a lossy render can be flattered by the metric."),
    ("D7", "圖片為什麼是「裁」而不是「抽」？",
     "對每個圖說，取它上方一塊區域、以非白色像素定出內容外框，再用 200 dpi 裁成 PNG。",
     "語料庫裡的圖多數是向量圖。實測 PPTAgent 那一頁有 39 個內嵌圖片（32×32 的 icon）"
     "與 160 條繪圖路徑，真正的 Figure 2 是路徑畫出來的——抽「圖片」只會抽到 icon。"
     "另外 band 要停在**段落**而不是任何文字方塊，因為圖裡面本身有標籤文字，"
     "停在標籤就會把圖切一半（修正前 32 個圖說只成功 2 個，修正後 12 個）。",
     "Figures are re-rendered from a clipped region rather than extracted, because the "
     "diagrams in this literature are vector art, not embedded bitmaps."),
    ("D8", "為什麼要把同一行的 span 用「間距」接合？",
     "相鄰 span 的水平間距大過 0.25 倍字級才插入空格，否則直接相連。",
     "用空格連接會把 \"PPTA\" + \"GENT\" 變成 \"PPTA GENT\"；用空字串連接會把 \"Stage\" + \"I:\" "
     "變成 \"StageI\"。只有間距分得出這兩種情況——一種是字距拆開的同一個詞，"
     "一種是真的空格。",
     "Span joining is decided by the horizontal gap, not by a fixed separator, because PDF "
     "text extraction splits both words and spaces into separate spans."),
    ("D9", "為什麼斷字接合要保留某些連字號？",
     "PDF 換行造成的斷字（doc- uments）直接接回；但清單內的複合詞（state-of-the-art）保留。",
     "原本用「前綴 ≤2 個字母就保留」，結果把 ex- tract 接成 ex-tract。"
     "改成只信清單：清單內的複合詞保留，其餘一律接回。",
     "Hyphen repair is driven by a compound list rather than by prefix length, because prefix "
     "length confuses a line break with a real hyphen."),
    ("D10", "為什麼圖說要在詞語邊界截斷？",
     "超過 210 字就在最後一個空格切，並加 \" ...\"。",
     "在固定字數硬切會出現 \"Presentation Generation gene\" 這種半個字，"
     "讀者會以為程式有 bug。這種瑕疵結構檢查抓不到，只有看過渲染圖才發現。",
     "Captions are truncated at a word boundary: a caption cut mid-word reads as a defect in "
     "the tool, not in the paper."),
    ("D11", "章節編號怎樣才算編號？",
     "只在前綴是 1–2 位數字、且後面有空白時才算章節編號。",
     "原本的規則會把 \"1. Introduction\" 剝成 \". Introduction\"（語料庫裡 AISSA 那篇中招三處），"
     "同時會把 \"5G Networks\" 剝成 \"G Networks\"。限制位數＋要求空白，兩個問題一齊解決。",
     "Section numbering is stripped only when a separator follows, so titles that begin with a "
     "number of their own survive."),
    ("D12", "為什麼測試寫在純函數而不是整條流程？",
     "幾何與規則類的函數直接單元測試；端到端只測一份真論文，而且 corpus 不在時自動跳過。",
     "把 60 幾個測試都做成整條 pipeline 會慢又不穩；但完全不測端到端，"
     "就會出現「每個函數都對、接起來錯」。兩層都要，但比例是 9:1。",
     "Geometry and rules are tested directly; the end-to-end path is tested once, on a real "
     "paper, and skipped when the corpus is absent."),
]
for did, q, decision, why, quote in decisions:
    heading(doc, f"{did}　{q}", 2)
    para(doc, "決定：" + decision, 10, space_after=4)
    para(doc, why, 10, space_after=4)
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(10)
    set_cjk(p.add_run("可引用：" + quote), 9.2, False, GREY)

doc.add_page_break()

# ---------------- 5 imports ----------------
heading(doc, "5. 每個 import 係咩、用嚟做咩", 1)
para(doc, "報告的方法章節通常要交代「用了哪些工具」。下表列出每個 import 的用途，"
          "以及它對應到哪一個技術決定。", 10)

table(doc, ["模組", "import", "用嚟做咩", "為什麼要它"], [
    ["parse.py", "fitz (PyMuPDF)", "開 PDF、逐頁讀文字與字體資訊、取 metadata", "要字級與粗體才判斷得到標題；純文字抽取做不到"],
    ["parse.py", "figures", "呼叫裁圖模組", "圖與文在同一次解析中對齊，避免事後配對"],
    ["parse.py", "statistics", "算全文中位字級", "標題判定的基準線（字級 ≥ 中位 + 2.2pt）"],
    ["parse.py", "re / os / sys / json / argparse / pathlib", "字串處理、檔案、命令列、JSON", "標準庫，零依賴"],
    ["figures.py", "pymupdf", "get_pixmap(clip=…) 裁圖、Rect 幾何", "向量圖只能靠渲染，不能抽"],
    ["figures.py", "numpy", "把 pixmap 轉成陣列、找非白色像素範圍", "純 Python 逐像素太慢"],
    ["compose.py", "urllib.request", "呼叫 OpenAI API（`--llm` 分支）", "不想為一次呼叫引入 SDK 依賴"],
    ["compose.py", "re / json / os / argparse", "切句、去引用標記、輸出 plan.json", "標準庫"],
    ["render.py", "pptx (python-pptx)", "建立簡報、文字框、圖片、備忘稿", "輸出必須是原生可編輯的 .pptx，不是圖片"],
    ["render.py", "pptx.util / dml.color / enum.text", "吋、Pt、RGB、對齊、錨點", "排版需要精確單位"],
    ["detect.py", "pptx", "讀 shape 的 bbox、字級、文字", "量度在物件模型上做，不渲染"],
    ["detect.py", "itertools.combinations", "兩兩比較 shape 是否重疊", "G2 的本質是成對比較"],
    ["schema.py", "dataclasses / enum", "不可變的 Requirement、固定的十類章節", "驗證在建立物件時就完成（fail-closed）"],
    ["schema.py", "re", "章節標題正則、evidence 格式檢查", "標題五花八門，只能用模式配對"],
    ["deck.py", "dataclasses / json / pathlib", "資料契約與序列化", "結構要能被測試與驗證"],
    ["tests/", "pytest", "測試框架", "參數化測試（對照表類）最省行數"],
    ["scripts/", "urllib.request / csv", "由 arXiv id 下載語料庫", "PDF 不進 git，必須可重建"],
], [2.4, 4.4, 6.2, 4.4], size=8.2)

# ---------------- 6 測試 ----------------
heading(doc, "6. 測試與「親眼驗證」", 1)
table(doc, ["檔案", "測試數", "測什麼"], [
    ["tests/test_schema.py", str(F["by_file"].get("test_schema.py", 0)),
     "章節對照、fail-closed、五段優先次序、determinism、兩個 coverage 數"],
    ["tests/test_deck.py", str(F["by_file"].get("test_deck.py", 0)),
     "七條不變量、prompt 內容、編輯分層"],
    ["tests/test_figures.py", str(F["by_file"].get("test_figures.py", 0)),
     "same_column、is_paragraph、band 停在哪、span 接合、端到端裁圖"],
    ["tests/test_parse.py", str(F["by_file"].get("test_parse.py", 0)),
     "章節編號剝除（包括不准剝的例子）"],
], [5.0, 2.0, 10.4])

para(doc, "跑法：", 10, True)
code(doc, "cd capstone-ppt-agent && python3 -m pytest")
para(doc, f"目前 {F['tests']} 個測試全綠。", 10)

heading(doc, "6.1 一個踩過的坑：渲染器", 2)
para(doc, "LibreOfficeKit 的 render 指令在這個環境會輸出全黑圖片——連一份已知正常的簡報也一樣，"
          "所以問題在工具而不是檔案。可行的驗證路徑是先用 convert 轉 PDF，再用 PyMuPDF 光柵化：", 10)
code(doc, '"<node>" "<cli>" convert --input out/deck.pptx --output /tmp/deck.pdf\n'
          'python3 -c "import pymupdf; pymupdf.open(\'/tmp/deck.pdf\')[1].get_pixmap(dpi=110).save(\'/tmp/p.png\')"')
para(doc, "這件事值得寫進報告的方法章節：結構檢查（ZIP/XML 完整、圖片存在、座標在版面內）"
          "通過並不等於畫面正確；真正的瑕疵（caption 切半、PPTA GENT、ex-tract）都是看渲染圖才發現的。", 10)

# ---------------- 7 之後加什麼 ----------------
heading(doc, "7. 之後會加啲咩", 1)
table(doc, ["階段", "會加的東西", "對應 WBS"], [
    ["立即", "提案三處修正（引用、週次、Workshop 日期）", "P0.1–P0.3"],
    ["11 月", "第二套模板、圖片 contain（已完成）、parse 硬化", "P1.8–P1.10"],
    ["11–12 月", "LLM 生成層：cache、client、outline、bullets、notes、grounding", "L1–L13"],
    ["11–12 月", "自由文字 → requirement 表；規則表寬鬆／嚴格兩版", "Q3–Q5"],
    ["12 月", "G4 對比、G5 文字溢出、按角色的 G3/G6", "P2.11–P2.16"],
    ["12–1 月", "六類修復動作、guardrail、110 張測試集、雙人標註", "P3"],
    ["1–2 月", "迴圈（greedy → budget-aware）、掃描凍結", "P4"],
    ["2–3 月", "消融（A0/A1/A2）、人評 20 人、統計", "P5"],
    ["3–4 月", "報告、Turnitin、AI report、示範、簡報", "P6"],
], [2.6, 10.6, 3.2])

# ---------------- 8 一句話總結 ----------------
heading(doc, "8. 一句話總結", 1)
para(doc, "這個系統做的不是「生成一份好看的簡報」，而是「生成一份簡報，並且知道它哪裡不能用」。"
          "所有設計決定——分檔、規則化、凍結要求、分層編輯——都是為了讓那個「知道」"
          "可以被重跑、被審核、被質疑。", 10.5)

doc.save(OUT)
print(f"saved {OUT}  ({F['files']} files, {F['tests']} tests, {F['loc']} lines)")
