#!/usr/bin/env python3
"""Status diagram for the capstone: what the system does, and what is built.

Every block carries the plain-language answer to "what does it do", so the
figure can be read by someone who has never seen a slide-generation pipeline.

Regenerate with:
    MPLCONFIGDIR=/tmp/mpl python3 docs/diagrams/make_status.py

Colour carries meaning, not decoration:
    green   built and tested
    amber   partially built (something works, a job is still open)
    grey    planned, not started
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent / "status_2026-10-23.png"

INK = "#10233A"
INK2 = "#3C4E60"
GREY = "#8A99A8"
GREEN = "#2F7D5D"
AMBER = "#C08A2E"
RED = "#A83542"
TEAL = "#2E6F95"   # the model marker; not amber, which already means "partial"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = ["PingFang HK", "Helvetica Neue", "Arial"]


def wrap_cjk(text, n):
    """Chinese has no spaces, so wrap by character count."""
    return "\n".join(text[i:i + n] for i in range(0, len(text), n))


def card(ax, x, y, w, h, name, tech, plain, status="done", badge=None,
         name_fs=9.6, plain_fs=7.4, wrap=14):
    fill = {"done": "#E6F2EC", "partial": "#FBF1DE", "planned": "#EEF1F4"}[status]
    edge = {"done": GREEN, "partial": AMBER, "planned": GREY}[status]
    ax.add_patch(mp.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.7 if status != "planned" else 1.25,
        edgecolor=edge, facecolor=fill, zorder=2,
        linestyle="--" if status == "planned" else "solid",
    ))
    cx = x + w / 2
    ax.text(cx, y + h - 0.24, name, ha="center", va="center", fontsize=name_fs,
            color=INK, weight="bold", zorder=3)
    if badge == "LLM":
        tech = f"AI · {tech}"
        tech_colour = TEAL
    else:
        tech_colour = INK2
    ax.text(cx, y + h - 0.47, tech, ha="center", va="center", fontsize=6.2,
            color=tech_colour, style="italic", zorder=3)
    ax.plot([x + 0.16, x + w - 0.16], [y + h - 0.60] * 2, color=edge, lw=0.7, alpha=0.55,
            zorder=3)
    ax.text(cx, y + h * 0.22, wrap_cjk(plain, wrap), ha="center", va="center",
            fontsize=plain_fs, color=INK, zorder=3, linespacing=1.45)


def arrow(ax, x1, y1, x2, y2, colour=GREY, style="-", lw=1.4):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=colour, lw=lw,
                                linestyle=style, shrinkA=0, shrinkB=0))


def elbow(ax, pts, colour=INK2, lw=1.3):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:-1]):
        ax.plot([x1, x2], [y1, y2], color=colour, lw=lw, zorder=1,
                solid_capstyle="round")
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    arrow(ax, x1, y1, x2, y2, colour=colour, lw=lw)


fig, ax = plt.subplots(figsize=(16, 10.2), dpi=150)
ax.set_xlim(0, 16)
ax.set_ylim(1.15, 10.45)
ax.axis("off")
fig.patch.set_facecolor(WHITE)

# ---------------------------------------------------------------- title ----
ax.text(0.55, 10.02, "DSAI4901 · From generating to verifying", fontsize=19,
        color=INK, weight="bold")
ax.text(0.55, 9.62, "論文 → deck 的系統長什麼樣：每一格做咩（用日常講法講一次），"
                    "以及邊一部分已經做好（2026-10-23）", fontsize=10.5, color=INK2)
ax.text(15.45, 10.06, "WBS 98 jobs · 216 h", fontsize=9.5, color=GREY, ha="right")

# ================================================================= A 生成 ==
ax.text(0.55, 9.06, "A  GENERATION — 由論文變成文字", fontsize=10, color=GREY,
        weight="bold")

y1, h1, w1 = 7.62, 1.32, 1.92
xs = [0.55, 2.67, 4.79, 6.91, 9.03, 11.15, 13.27]
cards = [
    ("parse.py", "sections · figures · sentences", "把論文拆開：邊段講背景、邊段講方法", "done", "det"),
    ("claims", "per section, evidence id", "每段抽一句重點，並記住它出自哪一行", "planned", "LLM"),
    ("requirement", "free text → 5-field table", "聽明你的要求：講幾分鐘、聽眾是誰", "partial", "LLM"),
    ("select", "rule table, 1/0 per claim", "用規則決定邊啲重點要講、邊啲唔講", "partial", None),
    ("outline", "global, re-orders evidence", "把要講的重點排成一條故事線", "planned", "LLM"),
    ("bullets + notes", "compressed, timed", "壓成一句 bullet，再寫成講稿連時間", "partial", "LLM"),
    ("render.py", "python-pptx, native shapes", "真正畫出 .pptx，之後仲改得", "done", "det"),
]
for (name, tech, plain, st, badge), x in zip(cards, xs):
    card(ax, x, y1, w1, h1, name, tech, plain, st, badge)
for a, b in zip(xs, xs[1:]):
    arrow(ax, a + w1, y1 + h1 / 2, b, y1 + h1 / 2)

now = plt.Rectangle((4.72, y1 - 0.12), 4.15, h1 + 0.24, fill=False,
                    edgecolor=RED, lw=1.8, linestyle=(0, (4, 3)), zorder=4)
ax.add_patch(now)
ax.text(6.79, y1 + h1 + 0.20, "現在在這裡 · P1c 選段", ha="center", fontsize=9,
        color=RED, weight="bold")

ax.text(0.55, 7.16,
        "重點：只有四個標住「AI」的格用到模型，其餘全部是寫死的規則。文字生成一次就固定 —— 之後所有改動只准改排版，"
        "唔准改字，否則分不到「檢查」值幾多。", fontsize=8.8, color=INK2)

# .pptx 由 render 交去量度層：走 bus，避免一條長斜線橫跨整個圖
elbow(ax, [(14.23, y1), (14.23, 6.60), (0.26, 6.60), (0.26, 5.28), (0.55, 5.28)])
ax.text(11.0, 6.67, ".pptx — 已經畫好的檔案", fontsize=7.8, color=INK2, ha="center")

# ================================================================= B 量度 ==
ax.text(0.55, 6.24, "B  MEASUREMENT — 用程式檢查，唔用感覺", fontsize=10,
        color=GREY, weight="bold")
ax.text(0.55, 6.02, "檢查次序固定  G1 → G5 → G2 → G4 → G3 → G6", fontsize=7.8, color=GREY)

yg, hg = 4.56, 1.32
gates = [
    ("G1 containment", "0 pt", "有東西跑出畫面外嗎", "done"),
    ("G2 overlap", ">5%", "兩段字疊在一起嗎", "done"),
    ("G3 font size", "角色下限", "字夠大嗎，後排看得清嗎", "done"),
    ("G4 contrast", "4.5:1", "字和底色夠分明嗎", "partial"),
    ("G5 text fit", "≤0.95", "字有沒有擠爆個框", "partial"),
    ("G6 density", "角色上限", "一頁塞太多字了嗎", "done"),
]
gw, gap = 1.40, 0.22
for i, (name, thr, plain, st) in enumerate(gates):
    card(ax, 0.55 + i * (gw + gap), yg, gw, hg, name, thr, plain, st,
         name_fs=8.6, plain_fs=7.4, wrap=12)

card(ax, 10.45, yg, 2.15, hg, "SRR", "六項合成一個分數", "0–1，愈高愈好", "partial",
     name_fs=10.5, plain_fs=7.6, wrap=11)
card(ax, 12.82, yg, 2.35, hg, "deck-ready", "全頁都合格才算", "夠不夠格直接上台", "partial",
     name_fs=10, plain_fs=7.6, wrap=11)
arrow(ax, 9.90, yg + hg / 2, 10.45, yg + hg / 2, colour=INK2)
arrow(ax, 12.60, yg + hg / 2, 12.82, yg + hg / 2, colour=INK2)

# ================================================================= C 修復 ==
ax.text(0.55, 4.16, "C  REPAIR & CONTROL — 呢部分就係論文的主貢獻", fontsize=10,
        color=GREY, weight="bold")
yc, hc = 2.62, 1.32
card(ax, 0.55, yc, 2.55, hc, "1 · measure", "worst violation first",
     "先量一次，找出最嚴重那一項", "planned", name_fs=10, wrap=15)
card(ax, 3.45, yc, 2.55, hc, "2 · repair", "cheapest reversible action",
     "用最便宜、可以還原的方法修", "planned", name_fs=10, wrap=16)
card(ax, 6.35, yc, 2.55, hc, "3 · re-measure", "ΔSRR per second / per $",
     "再量一次：改善幾多、花幾多", "planned", name_fs=10, wrap=16)
card(ax, 9.25, yc, 2.15, hc, "guardrail", "no new text, no numbers",
     "唔准加內容、唔准改數字", "planned", name_fs=9.6, wrap=12)
card(ax, 11.75, yc, 3.42, hc, "the claim under test", "A2 − A1",
     "開著檢查 vs 關掉檢查，差別就係檢查的價值", "planned", name_fs=9.6, wrap=18)
for x in (3.10, 6.00, 8.90, 11.40):
    arrow(ax, x, yc + hc / 2, x + 0.35, yc + hc / 2, colour=GREY, style="--")

arrow(ax, 7.62, yg, 7.62, yc + hc, colour=GREY, style="--")
ax.text(8.02, 4.30, "修完再量：只回到分數，唔會回到文字", fontsize=7.8, color=GREY)

# ================================================================ legend ===
handles = [
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#E6F2EC",
           markeredgecolor=GREEN, markersize=13, label="已做好並有測試"),
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#FBF1DE",
           markeredgecolor=AMBER, markersize=13, label="部分（有嘢跑得，但未收貨）"),
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#EEF1F4",
           markeredgecolor=GREY, markersize=13, label="計劃中，未開始"),
]
leg = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.025, 0.04),
                frameon=False, fontsize=9, ncol=3, handletextpad=0.6,
                columnspacing=2.0)
for t in leg.get_texts():
    t.set_color(INK2)

ax.text(0.55, 1.36,
        "讀法：粗體＝block 名；藍色「AI ·」＝用大型語言模型，冇標記＝固定規則；"
        "下面那句＝中學生都明嘅講法。綠＝做完有測試，琥珀＝做了一半，灰虛線＝未開始。",
        fontsize=7.8, color=GREY)

ax.text(15.45, 1.36, "Mizuki0215/capstone-ppt-agent",
        ha="right", fontsize=7.4, color=GREY)

fig.savefig(OUT, dpi=150, facecolor=WHITE, bbox_inches="tight", pad_inches=0.2)
print("wrote", OUT)
