#!/usr/bin/env python3
"""Status diagram for the capstone: what the system does, and what is built.

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
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = ["PingFang HK", "Helvetica Neue", "Arial"]


def box(ax, x, y, w, h, title, sub="", status="done", fs=11, subfs=8.2):
    fill = {"done": "#E6F2EC", "partial": "#FBF1DE", "planned": "#EEF1F4"}[status]
    edge = {"done": GREEN, "partial": AMBER, "planned": GREY}[status]
    ax.add_patch(mp.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.6 if status != "planned" else 1.2,
        edgecolor=edge, facecolor=fill, zorder=2,
        linestyle="--" if status == "planned" else "solid",
    ))
    if sub:
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center",
                fontsize=fs, color=INK, weight="semibold", zorder=3)
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                fontsize=subfs, color=INK2, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=fs, color=INK, weight="semibold", zorder=3)


def badge(ax, x, y, text, colour=GREY):
    ax.text(x, y, text, ha="center", va="center", fontsize=6.6, color=colour,
            weight="bold", zorder=5,
            bbox=dict(boxstyle="round,pad=0.22", facecolor=WHITE, edgecolor=colour,
                      linewidth=0.8))


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


fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
ax.set_xlim(0, 16)
ax.set_ylim(0.55, 8.95)
ax.axis("off")
fig.patch.set_facecolor(WHITE)

# ---------------------------------------------------------------- title ----
ax.text(0.55, 8.55, "DSAI4901 · From generating to verifying", fontsize=19,
        color=INK, weight="bold")
ax.text(0.55, 8.10, "論文 → deck 的系統長什麼樣，以及邊一部分已經做好（2026-10-23）",
        fontsize=10.5, color=INK2)
ax.text(15.45, 8.48, "WBS 98 jobs · 216 h", fontsize=9.5, color=GREY, ha="right")

# ================================================================= A 生成 ==
ax.text(0.55, 7.05, "A  GENERATION — text layer", fontsize=10, color=GREY, weight="bold")

y1, h1, w1 = 5.78, 0.92, 1.92
xs = [0.55, 2.67, 4.79, 6.91, 9.03, 11.15, 13.27]
box(ax, xs[0], y1, w1, h1, "parse.py", "sections · figures · sentences", "done")
box(ax, xs[1], y1, w1, h1, "claims", "per section, evidence id", "planned")
box(ax, xs[2], y1, w1, h1, "requirement", "free text → 5-field table", "partial")
box(ax, xs[3], y1, w1, h1, "select", "rule table, 1/0 per claim", "partial")
box(ax, xs[4], y1, w1, h1, "outline", "global, re-orders evidence", "planned")
box(ax, xs[5], y1, w1, h1, "bullets + notes", "compressed, timed", "partial")
box(ax, xs[6], y1, w1, h1, "render.py", "python-pptx, native shapes", "done")
for a, b in zip(xs, xs[1:]):
    arrow(ax, a + w1, y1 + h1 / 2, b, y1 + h1 / 2)

badge(ax, xs[0] + w1 - 0.22, y1 + h1 - 0.14, "det")
badge(ax, xs[6] + w1 - 0.22, y1 + h1 - 0.14, "det")
for i in (1, 2, 4, 5):
    ax.text(xs[i] + w1 / 2, y1 + h1 + 0.17, "LLM", ha="center", va="bottom",
            fontsize=7.6, color=AMBER, weight="bold")

now = plt.Rectangle((4.72, y1 - 0.12), 4.15, h1 + 0.24, fill=False,
                    edgecolor=RED, lw=1.8, linestyle=(0, (4, 3)), zorder=4)
ax.add_patch(now)
ax.text(6.79, y1 + h1 + 0.58, "現在在這裡 · P1c 選段", ha="center", fontsize=9,
        color=RED, weight="bold")

ax.text(0.55, 5.35,
        "LLM 只在四格出現，其餘是規則。文字生成一次即凍結 —— 之後所有改動只准發生在 layout 層，"
        "否則 ablation 分不出是 inspection 的功勞，還是改寫的功勞。",
        fontsize=8.6, color=INK2)

# .pptx 由 render 交去量度層：走 bus，避免一條長斜線橫跨整個圖
elbow(ax, [(14.23, y1), (14.23, 4.85), (0.26, 4.85), (0.26, 3.72), (0.55, 3.72)])
ax.text(11.0, 4.92, ".pptx — native object model", fontsize=7.8, color=INK2, ha="center")

# ================================================================= B 量度 ==
ax.text(0.55, 4.50, "B  MEASUREMENT — six gates on the object model", fontsize=10,
        color=GREY, weight="bold")
ax.text(0.55, 4.28, "fixed order  G1 → G5 → G2 → G4 → G3 → G6", fontsize=7.8, color=GREY)

yg, hg = 3.25, 0.94
gates = [("G1 containment", "0 pt", "done"), ("G2 overlap", ">5%", "done"),
         ("G3 font size", "role min", "done"), ("G4 contrast", "4.5:1", "partial"),
         ("G5 text fit", "≤0.95", "partial"), ("G6 density", "role max", "done")]
gw, gap = 1.40, 0.22
for i, (name, thr, st) in enumerate(gates):
    box(ax, 0.55 + i * (gw + gap), yg, gw, hg, name, thr, st, fs=8.9, subfs=8.0)

box(ax, 10.45, yg, 2.15, hg, "SRR", "0–1, per deck", "partial", fs=11)
box(ax, 12.82, yg, 2.35, hg, "deck-ready", "no gate fires anywhere", "partial", fs=11)
arrow(ax, 9.90, yg + hg / 2, 10.45, yg + hg / 2, colour=INK2)
arrow(ax, 12.60, yg + hg / 2, 12.82, yg + hg / 2, colour=INK2)

# ================================================================= C 修復 ==
ax.text(0.55, 2.85, "C  REPAIR & CONTROL — the contribution", fontsize=10,
        color=GREY, weight="bold")
yc, hc = 1.55, 0.92
box(ax, 0.55, yc, 2.55, hc, "1 · measure", "worst violation first", "planned", fs=10)
box(ax, 3.45, yc, 2.55, hc, "2 · repair", "cheapest reversible action", "planned", fs=10)
box(ax, 6.35, yc, 2.55, hc, "3 · re-measure", "ΔSRR per second / per $", "planned", fs=10)
box(ax, 9.25, yc, 2.15, hc, "guardrail", "no new text, no numbers", "planned", fs=9.6)
box(ax, 11.75, yc, 3.42, hc, "the claim under test",
    "A2 − A1 = what inspection is worth", "planned", fs=9.6)
for x in (3.10, 6.00, 8.90, 11.40):
    arrow(ax, x, yc + hc / 2, x + 0.35, yc + hc / 2, colour=GREY, style="--")

arrow(ax, 7.62, yg, 7.62, yc + hc, colour=GREY, style="--")
ax.text(7.78, 2.62, "loops back to the metric, never to the text", fontsize=7.8, color=GREY)

# ================================================================ legend ===
handles = [
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#E6F2EC",
           markeredgecolor=GREEN, markersize=13, label="已做好並有測試"),
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#FBF1DE",
           markeredgecolor=AMBER, markersize=13, label="部分（有嘢跑得，但 job 未收）"),
    Line2D([0], [0], marker="s", color="none", markerfacecolor="#EEF1F4",
           markeredgecolor=GREY, markersize=13, label="計劃中，未開始"),
]
leg = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.025, 0.02),
                frameon=False, fontsize=9, ncol=3, handletextpad=0.6,
                columnspacing=2.0)
for t in leg.get_texts():
    t.set_color(INK2)

ax.text(15.45, 0.72,
        "Mizuki0215/capstone-ppt-agent · docs/diagrams/make_status.py",
        ha="right", fontsize=7.5, color=GREY)

fig.savefig(OUT, dpi=150, facecolor=WHITE, bbox_inches="tight", pad_inches=0.2)
print("wrote", OUT)
