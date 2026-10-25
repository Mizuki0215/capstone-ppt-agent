#!/usr/bin/env python3
"""Build the Chinese progress deck for the supervisor meeting.

    <python with python-pptx> deck/build_progress_deck.py

Content is the project as it stands on 2026-10-24: the literature argument, the
parts of the system, and the measured results. Every number on the result slides
comes from build/detect_v1.json and a fresh detector run, not from memory.
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deck" / "progress_deck_zh.pptx"
IMG = ROOT / "deck" / "progress_img"

INK = RGBColor(0x10, 0x23, 0x3A)
INK2 = RGBColor(0x1E, 0x36, 0x52)
GREY = RGBColor(0x5A, 0x6B, 0x7C)
LGREY = RGBColor(0x8A, 0x99, 0xA8)
GOLD = RGBColor(0xC0, 0x8A, 0x2E)
PANEL = RGBColor(0xF4, 0xF6, 0xF8)
PANEL2 = RGBColor(0xEC, 0xF1, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2F, 0x7D, 0x5D)
AMBER = RGBColor(0xB0, 0x7A, 0x1E)
RED = RGBColor(0xA8, 0x35, 0x42)
TEAL = RGBColor(0x2E, 0x6F, 0x95)

FONT = "PingFang HK"
W, H = 13.333, 7.5


# --------------------------------------------------------------------------- #
def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def tb(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    return tf


def write(tf, text, size, colour=INK, bold=False, first=False, space=0, line=1.15,
          align=PP_ALIGN.LEFT, italic=False, font=FONT):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space)
    p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = colour
    return p


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.9, shape=MSO_SHAPE.RECTANGLE,
         radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    s.shadow.inherit = False
    style = s._element.find(qn("p:style"))   # theme effects put a shadow back
    if style is not None:
        s._element.remove(style)
    s.text_frame.word_wrap = True
    return s


def page(prs, kicker, title, number=None):
    s = blank(prs)
    rect(s, 0, 0, 0.26, H, fill=INK)
    rect(s, 0.26, 0, 0.05, H, fill=GOLD)
    tf = tb(s, 0.95, 0.42, 11.6, 0.30)
    write(tf, kicker.upper(), 9.5, GOLD, True, first=True)
    tf = tb(s, 0.95, 0.70, 11.9, 0.75)
    write(tf, title, 25, INK, True, first=True, line=1.05)
    rect(s, 0.95, 1.52, 11.9, 0.014, fill=RGBColor(0xDD, 0xE2, 0xE8))
    if number:
        tf = tb(s, 12.2, 6.95, 0.7, 0.3)
        write(tf, f"{number:02d}", 9, LGREY, first=True, align=PP_ALIGN.RIGHT)
    return s


def bullets(slide, x, y, w, items, size=15, gap=8, colour=INK, bullet_col=GOLD):
    tf = tb(slide, x, y, w, 4.2)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else gap)
        p.line_spacing = 1.22
        r = p.add_run()
        r.text = "-  "
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = bullet_col
        if isinstance(item, tuple):
            head, rest = item
            r = p.add_run(); r.text = head
            r.font.name = FONT; r.font.size = Pt(size); r.font.bold = True
            r.font.color.rgb = colour
            r = p.add_run(); r.text = rest
            r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = colour
        else:
            r = p.add_run(); r.text = item
            r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = colour
    return tf


def table(slide, headers, rows, x, y, w, widths, size=10, head=10, row_h=0.32,
          head_h=0.34):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y),
                                   Inches(w), Inches(row_h * (len(rows) + 1)))
    t = shape.table
    for i, cw in enumerate(widths):
        t.columns[i].width = Inches(cw)
    t.rows[0].height = Inches(head_h)
    for r in range(1, len(rows) + 1):
        t.rows[r].height = Inches(row_h)
    for i, h in enumerate(headers):
        cell = t.cell(0, i)
        cell.fill.solid(); cell.fill.fore_color.rgb = PANEL2
        cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        tf = cell.text_frame; tf.word_wrap = True
        write(tf, h, head, INK, True, first=True)
    for r, row in enumerate(rows, start=1):
        for i, val in enumerate(row):
            cell = t.cell(r, i)
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
            cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            tf = cell.text_frame; tf.word_wrap = True
            colour = INK if i == 0 else INK2
            write(tf, str(val), size, colour, i == 0, first=True, line=1.1)
    return t


def pill(slide, x, y, w, text, colour, size=9):
    s = rect(slide, x, y, w, 0.30, fill=WHITE, line=colour, lw=1.2,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = s.text_frame
    tf.margin_top = 0; tf.margin_bottom = 0
    write(tf, text, size, colour, True, first=True, align=PP_ALIGN.CENTER)
    return s


# --------------------------------------------------------------------------- #
def slide_title(prs):
    s = blank(prs)
    rect(s, 0, 0, 0.34, H, fill=INK)
    rect(s, 0.34, 0, 0.07, H, fill=GOLD)
    tf = tb(s, 1.1, 1.35, 10.8, 0.4)
    write(tf, "DSAI4901  ·  CAPSTONE 進度簡報", 11, GOLD, True, first=True)
    tf = tb(s, 1.1, 1.95, 10.9, 2.4)
    write(tf, "由生成，\n到可驗證", 46, INK, True, first=True, line=1.02)
    tf = tb(s, 1.1, 4.15, 10.4, 1.0)
    write(tf, "以可量度的版面可用性，作為論文轉簡報的控制訊號", 14.5, GREY, first=True, line=1.3)
    rect(s, 1.1, 5.35, 3.4, 0.02, fill=GOLD)
    tf = tb(s, 1.1, 5.55, 10.4, 1.0)
    write(tf, "CHAN Yee Tung", 12.5, INK, True, first=True)
    write(tf, "指導老師：Dr. Jibin Wu   ·   2026 年 10 月 29 日", 11, GREY, space=4)
    return s


def slide_lit(prs):
    s = page(prs, "文獻現況", "兩大家族，缺一件工具", 2)
    rows = [
        ["PPTAgent、SlideGen、\nSlideLab、ArcDeck", "強生成器；敘事規劃",
         "這份 deck 到底能不能用；\n局部、機械性的失敗"],
        ["ReDeck、PPTPilot、\nSLIDEFORGE", "會讀渲染回饋的\n修復迴圈",
         "哪一類缺陷對修復有反應，\n反應幾大"],
        ["SlideAudit、DECKBench、\nPresentBench", "缺陷分類法；對照參考 deck\n評分",
         "生成之後才到；需要目標 deck\n或標註"],
    ]
    table(s, ["工作", "提供什麼", "仍留下什麼"], rows, 0.95, 1.82,
          11.9, [3.5, 3.6, 4.8], size=10.5, head=10.5, row_h=0.58, head_h=0.36)
    tf = tb(s, 0.95, 4.30, 11.6, 1.9)
    write(tf, "合起來看，這個領域很會做 deck，也很會在事後打分，但中間那一段沒有接上。", 15, INK, first=True,
          line=1.35)
    write(tf, "工具來得太遲，指揮不到生成；真的用得著的時候，又不可分解。", 12.5, GREY, space=8, line=1.3)
    rect(s, 0.95, 5.55, 11.9, 1.05, fill=PANEL2)
    rect(s, 0.95, 5.55, 0.07, 1.05, fill=GOLD)
    tf = tb(s, 1.28, 5.72, 11.3, 0.8)
    write(tf, "缺口：冇一件工具跑在迴圈裡面，冇一件把分數拆得開。一個 deck 層面的數字，講不出應該修哪一類缺陷。", 12.5, INK,
          first=True, line=1.3)
    return s


def slide_why(prs):
    s = page(prs, "為什麼做這個方向", "文獻沒有做的三件事", 3)
    cols = [
        ("歸因缺失", "ReDeck 與 PPTPilot 都會修，但 deck 升十分，講不出是哪一類缺陷對修復有反應。",
         AMBER),
        ("量度是事後的", "SlideAudit 與 DECKBench 評的是成品。生成之後才到的分數，指揮不到生成。", TEAL),
        ("工具需要參考或標註", "要一個目標 deck，或者人手標註圖像。兩者在生成時都對任意 .pptx 算不到。", RED),
    ]
    x = 0.95
    for title, body, colour in cols:
        rect(s, x, 1.88, 3.72, 2.15, fill=PANEL)
        rect(s, x, 1.90, 3.72, 0.06, fill=colour)
        tf = tb(s, x + 0.28, 2.08, 3.2, 0.6)
        write(tf, title, 13.5, INK, True, first=True, line=1.15)
        tf = tb(s, x + 0.28, 2.68, 3.2, 1.3)
        write(tf, body, 10.5, INK2, first=True, line=1.3)
        x += 3.96
    tf = tb(s, 0.95, 4.45, 11.6, 0.5)
    write(tf, "所以貢獻不是又一個生成器，也不是一套新分類法。", 15, INK,
          True, first=True)
    bullets(s, 0.95, 5.10, 11.6, [
        ("而是一層量度", "：無需參考、在物件模型上計算、便宜到可以跑在迴圈裡面。"),
        ("以及研究這個量度值多少", " —— 按違規類別計，對照成本。"),
    ], size=12.5, gap=6)
    return s


def slide_gap(prs):
    s = page(prs, "問題", "一個缺口，兩條研究問題", 4)
    rect(s, 0.95, 1.85, 11.9, 1.55, fill=PANEL2)
    rect(s, 0.95, 1.85, 0.07, 1.55, fill=GOLD)
    tf = tb(s, 1.28, 2.02, 11.3, 1.3)
    write(tf, "「簡報品質現在可以事後量度。這些工具答不到的是：量度本身能不能驅動生成。」",
          13.5, INK, first=True, line=1.35, italic=True)
    qs = [("RQ1", "一組機械性的 gate，能不能取代參考 deck 或人手標註，而仍然按人會給的次序排列 deck？"),
          ("RQ2", "把這個訊號放進迴圈裡，實際加了多少？按違規類別計，成本又是幾多？")]
    y = 3.72
    for tag, q in qs:
        pill(s, 0.95, y + 0.04, 0.85, tag, GOLD, size=10)
        tf = tb(s, 1.98, y, 10.8, 0.9)
        write(tf, q, 13, INK2, first=True, line=1.35)
        y += 1.05
    tf = tb(s, 0.95, 5.95, 11.6, 0.9)
    write(tf, "兩條問題由同一件東西回答：一份 deck、一個分數、一份修復記錄。",
          11.5, GREY, first=True, italic=True)
    return s


def slide_workflow(prs):
    s = page(prs, "系統", "七個零件，其中四個用到模型", 5)
    parts = [
        ("parse", "PDF → 章節、圖、圖說", "det"),
        ("claims", "斷言，附上\nevidence id", "AI"),
        ("requirement", "幾分鐘、聽眾是誰\n→ 一張表", "AI"),
        ("select", "逐條 claim\n決定要或不要", "rule"),
        ("outline", "重排成一條\n論證", "AI"),
        ("bullets+notes", "壓縮，再寫成\n講稿", "AI"),
        ("render", "原生、可再編輯\n的 .pptx", "det"),
    ]
    x, y, w, h, gap = 0.95, 1.92, 1.43, 1.12, 0.155
    for i, (name, sub, tag) in enumerate(parts):
        fill = PANEL if tag == "AI" else PANEL2
        rect(s, x, y, w, h, fill=fill, line=RGBColor(0xD3, 0xDB, 0xE3))
        tf = tb(s, x + 0.08, y + 0.12, w - 0.16, 0.3)
        write(tf, name, 10.5, INK, True, first=True, align=PP_ALIGN.CENTER)
        tf = tb(s, x + 0.08, y + 0.44, w - 0.16, 0.55)
        write(tf, sub, 7.8, INK2, first=True, align=PP_ALIGN.CENTER, line=1.15)
        if tag == "AI":
            tf = tb(s, x + w - 0.40, y + 0.10, 0.32, 0.2)
            write(tf, "AI", 6.5, TEAL, True, first=True, align=PP_ALIGN.RIGHT)
        if i < len(parts) - 1:
            arrow = rect(s, x + w + 0.025, y + h / 2 - 0.075, gap - 0.05, 0.15,
                         fill=LGREY, shape=MSO_SHAPE.RIGHT_ARROW)
        x += w + gap

    # measurement row
    gates = ["G1 出界", "G2 重疊", "G3 字級", "G4 對比",
             "G5 文字溢出", "G6 密度"]
    gx, gy, gw, gh, gg = 0.95, 3.92, 1.40, 0.70, 0.12
    for i, g in enumerate(gates):
        rect(s, gx, gy, gw, gh, fill=WHITE, line=RGBColor(0xC3, 0xCE, 0xD8))
        tf = tb(s, gx + 0.05, gy + 0.24, gw - 0.1, 0.3)
        write(tf, g, 9, INK, True, first=True, align=PP_ALIGN.CENTER)
        gx += gw + gg
    rect(s, 10.12, gy, 1.00, gh, fill=PANEL2, line=GOLD)
    tf = tb(s, 10.17, gy + 0.23, 0.90, 0.3)
    write(tf, "SRR", 11, INK, True, first=True, align=PP_ALIGN.CENTER)
    rect(s, 11.28, gy, 1.05, gh, fill=PANEL2, line=GOLD)
    tf = tb(s, 11.33, gy + 0.23, 0.95, 0.3)
    write(tf, "ready?", 9.5, INK, True, first=True, align=PP_ALIGN.CENTER)

    tf = tb(s, 0.95, 1.62, 11.6, 0.3)
    write(tf, "A  生成 —— 文字層，寫定即凍結", 9.5, GREY, True, first=True)
    tf = tb(s, 0.95, 3.52, 11.6, 0.3)
    write(tf, "B  量度 —— 六個 gate，直接在 .pptx 物件模型上，不渲染", 9.5, GREY,
          True, first=True)
    # the contribution, drawn as the third band
    cx, cy, cw, ch = 0.95, 4.95, 3.55, 0.78
    for label, sub, colour in [("1  量度", "先找最嚴重那一項", GREY),
                               ("2  修復", "最便宜、可還原的動作", GREY),
                               ("3  再量", "每秒、每元的改善", GREY)]:
        rect(s, cx, cy, cw, ch, fill=WHITE, line=colour, lw=1.0)
        tf = tb(s, cx + 0.15, cy + 0.14, cw - 0.3, 0.55)
        write(tf, label, 10.5, INK, True, first=True)
        write(tf, sub, 8, INK2, space=2)
        cx += cw + 0.35
    tf = tb(s, 0.95, 5.88, 11.9, 0.95)
    write(tf, "只有文字層可以改字。修復可以移、可以縮、可以換色，但永遠不可以加內容或改數字。這樣「迴圈令 deck 變好」才不會同「迴圈改寫了 deck」混在一起。", 11, INK2, first=True, line=1.35)
    return s


def slide_parse(prs):
    s = page(prs, "零件一 · 讀論文", "圖說是裁出來的，不是抽出來的", 6)
    bullets(s, 0.95, 1.85, 6.3, [
        ("章節標題", "靠字級與粗體判斷，不靠固定清單。"),
        ("圖", "在這個領域多數是向量圖：抽內嵌圖片只會抽到 32×32 的 icon。所以按圖說的位置裁出區域，再以 200 dpi 光柵化。"),
        ("裁切的界線停在最近的段落", "，不是停在任何文字方塊 —— 圖裡面本身有標籤，停在標籤就會把圖切一半。"),
    ], size=12, gap=10)
    img = IMG.parent / "figures" / "PPTAgent_2501.03936" / "p02_01_figure.png"
    if not img.exists():
        img = ROOT / "build" / "figures" / "PPTAgent_2501.03936" / "p02_01_figure.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(7.55), Inches(1.95), width=Inches(4.85))
        tf = tb(s, 7.55, 4.35, 4.85, 0.5)
        write(tf, "PPTAgent 的 Figure 2，直接由 PDF 裁出來", 8.5, GREY, first=True,
              italic=True)
    tf = tb(s, 0.95, 5.62, 11.9, 1.1)
    write(tf, "這篇論文 32 個圖說之中，12 個裁出可用的圖。失敗的是「圖說在表格上方」與「跨兩欄的圖」。兩者都可以修；而產生這 12 張的規則，就是評估時會用的同一條。", 10.5, GREY, first=True, line=1.35)
    return s


def slide_select(prs):
    s = page(prs, "零件二 · 決定講什麼", "選段是一張表，不是一個判斷", 7)
    rows = [
        ["5 分鐘、一般聽眾", "results、conclusion", "method (core only)", "analysis, limitations"],
        ["12 分鐘、專家", "results、conclusion、method、\nmotivation、background、analysis",
         "related work、setup", "—"],
    ]
    table(s, ["要求", "一定保留", "有空間才保留", "丟掉"], rows, 0.95, 1.85,
          11.9, [2.4, 4.3, 2.9, 2.3], size=10, head=10, row_h=0.55)
    tf = tb(s, 0.95, 3.55, 11.9, 0.4)
    write(tf, "每一條被保留或被丟掉的 claim，都帶著決定它的規則編號：", 11.5,
          INK, True, first=True)
    rows2 = [
        ["c3", "results", "3", "保留", "hard:results", "results 永遠保留"],
        ["c7", "setup", "2", "丟掉", "table:12:setup", "12 分鐘的 talk 不講"],
        ["c9", "analysis", "1", "丟掉", "importance:cut2", "重要度 1 低於門檻 2"],
    ]
    table(s, ["claim", "章節", "重要度", "決定", "規則編號", "原因"], rows2, 0.95, 4.05,
          11.9, [1.0, 1.5, 0.8, 1.3, 2.5, 4.8], size=9.5, head=9.5, row_h=0.32)
    tf = tb(s, 0.95, 5.95, 11.9, 0.9)
    write(tf, "模型只出現在兩個邊界：把自由文字的要求轉成那張表，以及抽取 claim。中間的取捨是查表，所以第二個人可以重跑一次。", 10.5, GREY, first=True, line=1.35)
    return s


def slide_measure(prs):
    s = page(prs, "零件三 · 量度", "六個 gate 做了四個，兩個是下一步", 8)
    rows = [
        ["G1 出界", "所有形狀在版面內", "0 pt", "已做"],
        ["G2 重疊", "文字交集 ÷ 較小框", "> 5 %", "已做"],
        ["G3 字級", "內文與標題，按角色", "角色下限", "已做·全局"],
        ["G6 密度", "字數與 bullet，按角色", "角色上限", "已做·全局"],
        ["G4 對比", "WCAG 2.2 AA，字對背景", "4.5 : 1", "下一步"],
        ["G5 文字溢出", "渲染高度 ÷ 框高", "≤ 0.95", "下一步"],
    ]
    t = table(s, ["gate", "規則", "門檻", "狀態"], rows, 0.95, 1.85, 7.6,
              [1.9, 3.3, 1.2, 1.2], size=10, head=10, row_h=0.42)
    for r in range(1, len(rows) + 1):
        cell = t.cell(r, 3)
        cell.text_frame.clear()          # table() already wrote it; colour it once
        state = rows[r - 1][3]
        write(cell.text_frame, state, 10, GREEN if state.startswith("已做") and "全局" not in state else
              (AMBER if "全局" in state else RED), True, first=True)

    rect(s, 8.85, 1.85, 3.95, 1.55, fill=PANEL)
    tf = tb(s, 9.1, 2.02, 3.5, 1.2)
    write(tf, "SRR", 16, INK, True, first=True)
    write(tf, "可判斷的檢查之中，通過的比例。權重全部相等，沒有 fit 出來的數；判斷不到的檢查不計入平均，但會令 deck-ready 不成立。", 10, INK2, space=6,
          line=1.3)
    rect(s, 8.85, 3.60, 3.95, 1.55, fill=PANEL)
    tf = tb(s, 9.1, 3.77, 3.5, 1.2)
    write(tf, "為什麼不用權重", 13, INK, True, first=True)
    write(tf, "任何權重都是一個沒有證據的數 —— 同報告反對「24 點字」的理由一樣。", 10, INK2, space=6, line=1.3)
    tf = tb(s, 0.95, 5.35, 11.9, 1.2)
    write(tf, "G4 與 G5 是兩個真正需要解析度的：顏色要穿過主題與 z-order 解析，文字高度要用字體度量估算。兩者都排在迴圈之前，因為一個不能信的指標，不能當訊號。", 10.5, GREY, first=True, line=1.35)
    return s


def slide_space(prs):
    s = page(prs, "範圍", "可以量的有 65 項，值得做的有 6 項", 9)
    rows = [["A  版面幾何", "14"], ["B  字體與排版", "15"],
            ["C  顏色與對比", "7"], ["D  內容與語意", "12"],
            ["E  結構", "8"], ["F  渲染", "5"], ["G  觀眾", "4"],
            ["合計", "65"]]
    t = table(s, ["候選", "數量"], rows, 0.95, 1.85, 3.9, [2.9, 1.0],
              size=9.5, head=9, row_h=0.34)
    for r in range(1, len(rows) + 1):
        if rows[r - 1][0] == "合計":
            c0, c1 = t.cell(r, 0), t.cell(r, 1)
            c0.text_frame.clear()
            c1.text_frame.clear()
            write(c0.text_frame, "合計", 9.5, INK, True, first=True)
            write(c1.text_frame, "65", 9.5, GOLD, True, first=True)

    tf = tb(s, 5.25, 1.85, 3.1, 0.35)
    write(tf, "五個條件", 11, INK, True, first=True)
    tests = ["可判定：不需要參考答案",
             "確定性：同一份檔案同一個分數",
             "違規就是變壞，不是不同",
             "便宜到可以跑在迴圈裡",
             "可解釋：指得出形狀、數值、門檻"]
    tf = tb(s, 5.25, 2.25, 3.15, 2.4)
    for i, item in enumerate(tests):
        write(tf, "-  " + item, 9, INK2, first=(i == 0), space=0 if i == 0 else 7,
              line=1.2)

    tf = tb(s, 8.65, 1.85, 3.75, 0.35)
    write(tf, "最後留下的", 11, INK, True, first=True)
    rows2 = [["G1 出界", "A1"], ["G2 重疊", "A2"], ["G3 字級", "B1"],
             ["G4 對比", "C1"], ["G5 文字溢出", "B7"], ["G6 密度", "B5+B6"]]
    table(s, ["gate", "來源"], rows2, 8.65, 2.25, 3.75, [2.85, 0.9],
          size=9.5, head=9, row_h=0.33)

    rect(s, 0.95, 5.55, 11.9, 1.15, fill=PANEL2)
    rect(s, 0.95, 5.55, 0.07, 1.15, fill=RED)
    tf = tb(s, 1.28, 5.70, 11.3, 0.9)
    write(tf, "而它看不見什麼：一句 bullet 可以語法正確、長度正常、字級正確 —— 而完全冇意義。"
              "這就是機械式量度的邊界，屬於人評。", 11, INK, first=True, line=1.3)
    return s


def slide_results(prs):
    s = page(prs, "目前結果", "每一張生成出來的 slide 都至少違反一個 gate", 10)
    img = IMG / "slide02.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.95), Inches(1.80), width=Inches(6.85))
        tf = tb(s, 0.95, 5.75, 6.85, 0.5)
        write(tf, "生成的 deck 第 2 頁：圖已放入，圖說在下面", 8.5, GREY,
              first=True, italic=True)
    rows = [
        ["頁數", "9", "9"],
        ["合格頁", "0", "0"],
        ["SRR（頁面級）", "0.00", "0.00"],
        ["違規數", "33", "32"],
        ["G3 違規頁", "9 / 9", "9 / 9"],
        ["G6 違規頁", "8 / 9", "8 / 9"],
    ]
    table(s, ["", "PPTAgent", "DOC2PPT"], rows, 8.15, 1.82, 4.55,
          [2.05, 1.25, 1.25], size=10, head=9.5, row_h=0.33)
    tf = tb(s, 8.15, 4.62, 4.6, 1.6)
    write(tf, "這是預期結果，不是缺陷：baseline 生成器完全不理會這些 gate。重點是這個數字可以重跑，而違規是逐項命名的。", 10, INK2, first=True, line=1.35)
    return s


def slide_console(prs):
    s = page(prs, "實際執行", "整條 pipeline 跑得完，而且會老實地報錯", 11)
    img = IMG / "console_run.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.95), Inches(1.80), width=Inches(8.30))
        tf = tb(s, 0.95, 7.06, 8.3, 0.3)
        write(tf, "真實終端輸出；中間幾行省略。", 8, GREY, first=True, italic=True)
    notes = [
        ("parse", "8 個章節、24 個圖說、裁出 11 張圖"),
        ("compose", "8 張 slide，每張 90 秒"),
        ("render", "9 頁 deck，原生可編輯"),
        ("detect", "32 個違規，SRR 0.00"),
        ("pytest", "76 個測試全綠"),
    ]
    y = 1.90
    for head, body in notes:
        tf = tb(s, 9.65, y, 3.2, 0.78)
        write(tf, head, 10, GOLD, True, first=True)
        write(tf, body, 9, INK2, space=1, line=1.25)
        y += 0.92
    return s


def slide_status(prs):
    s = page(prs, "狀態", "做好了什麼，下一步是什麼", 12)
    groups = [
        ("已做好並有測試", GREEN, ["parse：章節、圖、圖說",
                                     "裁圖：樣本上 32 個圖說成功 12 個",
                                     "render：原生 .pptx 連講稿",
                                     "G1、G2、G3、G6 + SRR",
                                     "選段規則表，55 個測試函數"]),
        ("部分完成", AMBER, ["G3 / G6 仍然用一個全局門檻",
                                    "圖說截斷要改成詞語邊界",
                                    "claim 仍然由 heuristic 抽取"]),
        ("未開始", GREY, ["G4 對比、G5 文字溢出",
                               "修復動作與迴圈",
                               "110 張測試集與標註",
                               "人手 deck、baseline、2×2 實驗"]),
    ]
    x = 0.95
    for title, colour, items in groups:
        rect(s, x, 1.85, 3.85, 3.20, fill=PANEL)
        rect(s, x, 1.85, 3.85, 0.055, fill=colour)
        tf = tb(s, x + 0.25, 2.05, 3.4, 0.35)
        write(tf, title, 12.5, INK, True, first=True)
        tf = tb(s, x + 0.25, 2.55, 3.45, 3.1)
        for i, item in enumerate(items):
            write(tf, "-  " + item, 9.5, INK2, first=(i == 0), space=0 if i == 0 else 7,
                  line=1.25)
        x += 4.03
    tf = tb(s, 0.95, 5.40, 11.9, 0.6)
    write(tf, "76 個測試全綠。上面那份 deck 就是這條 pipeline 由頭到尾跑出來的。",
          10.5, GREY, first=True, italic=True)
    return s


def slide_plan(prs):
    s = page(prs, "計劃", "實驗設計，與時間表", 13)
    # 2x2
    tf = tb(s, 0.95, 1.80, 5.6, 0.35)
    write(tf, "設計：2 × 2 因子", 12.5, INK, True, first=True)
    headers = ["", "不檢查", "開檢查"]
    rows = [["基礎模型", "A1", "A2"], ["fine-tuned", "A1'", "A2'"]]
    table(s, headers, rows, 0.95, 2.20, 5.4, [1.9, 1.75, 1.75], size=11, head=9.5, row_h=0.45)
    tf = tb(s, 0.95, 3.45, 5.5, 1.6)
    write(tf, "A2 − A1 隔離出檢查帶來的增益。fine-tune 那一行測試這個增益在更強生成器下是否仍然存在。", 10.5, INK2, first=True, line=1.35)
    write(tf, "fine-tune 那一臂是條件性的：只有主結果出來、而且剩下四週 buffer 才會跑。", 10, GREY, space=6, line=1.3, italic=True)

    rows2 = [
        ["W1-2", "範圍與文獻", "提案 11/5"],
        ["W3-7", "rulebook、六個 gate、校準", "效度檢查"],
        ["W8-11", "修復動作、110 張測試集", "中期報告 1/7"],
        ["W12-18", "迴圈、消融、20 人研究", "偏好相關性"],
        ["W19-23", "報告、demo、簡報", "最終 4/8"],
    ]
    table(s, ["週次", "工作", "里程碑"], rows2, 6.85, 2.20, 6.0,
          [1.15, 3.0, 1.85], size=9.5, head=9.5, row_h=0.40)
    tf = tb(s, 6.85, 5.05, 6.0, 1.3)
    write(tf, "兩個效度檢查在主要研究之前跑：deck 要排成 人手 > PPTAgent > naive；SRR 要跟隨人類偏好。相關係數會預先註冊，無論結果如何都報。", 10, GREY, first=True, line=1.35)
    return s


def slide_asks(prs):
    s = page(prs, "需要你的意見", "三個決定，一個問題", 14)
    items = [
        ("1", "人手 deck", "哪裡可以拿到作者真正上台用的 deck？它是效度檢查的上界，而我手上完全沒有。"),
        ("2", "範圍", "單欄英文論文、10–12 張、8 篇 held-out —— 這樣窄到做得完，還是窄到不能推廣？"),
        ("3", "Gate 集", "六個機械性 gate，密度與字級用掃描而不是擬合。這樣站得住腳，還是應該減一個？"),
    ]
    y = 1.85
    for num, head, body in items:
        pill(s, 0.95, y + 0.05, 0.55, num, GOLD, size=12)
        tf = tb(s, 1.75, y, 10.9, 0.95)
        write(tf, head, 12.5, INK, True, first=True)
        write(tf, body, 10.5, INK2, space=3, line=1.3)
        y += 1.35
    rect(s, 0.95, 5.95, 11.9, 0.85, fill=PANEL2)
    tf = tb(s, 1.2, 6.08, 11.3, 0.6)
    write(tf, "另外想聽你的看法：一個確定性的 detector，在這裡會被視為優點，還是被視為 AI 成分不足？",
          11, INK, first=True, line=1.3)
    return s


# --------------------------------------------------------------------------- #
def main():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    slide_title(prs)
    slide_lit(prs)
    slide_why(prs)
    slide_gap(prs)
    slide_workflow(prs)
    slide_parse(prs)
    slide_select(prs)
    slide_measure(prs)
    slide_space(prs)
    slide_results(prs)
    slide_console(prs)
    slide_status(prs)
    slide_plan(prs)
    slide_asks(prs)
    prs.save(OUT)
    print(f"wrote {OUT}  slides={len(prs.slides.__iter__.__self__._sldIdLst)}")


if __name__ == "__main__":
    main()
