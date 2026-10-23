#!/usr/bin/env python3
"""Annotated poster: each block is a node, and a leader line points at its label.

This is the version to hand to someone with no background. The node carries only
the name; the plain-language explanation sits in its own box underneath, joined
to the node by a leader line, so the reader can always tell which note belongs to
which block.

Regenerate with:
    MPLCONFIGDIR=/tmp/mpl python3 docs/diagrams/make_annotated.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp
import matplotlib.pyplot as plt

from content import CONTROL, GATES, PIPELINE, SCORES

OUT = Path(__file__).resolve().parent / "status_2026-10-23_annotated.png"

INK = "#10233A"
INK2 = "#3C4E60"
GREY = "#8A99A8"
GREEN = "#2F7D5D"
AMBER = "#C08A2E"
TEAL = "#2E6F95"
RED = "#A83542"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = ["PingFang HK", "Helvetica Neue", "Arial"]

FILL = {"done": "#E6F2EC", "partial": "#FBF1DE", "planned": "#EEF1F4"}
EDGE = {"done": GREEN, "partial": AMBER, "planned": GREY}


def wrap(s, n):
    return "\n".join(s[i:i + n] for i in range(0, len(s), n))


def node(ax, x, y, w, h, text, status, ai=False, fs=9.4):
    ax.add_patch(mp.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.6 if status != "planned" else 1.1,
        edgecolor=EDGE[status], facecolor=FILL[status], zorder=3,
        linestyle="--" if status == "planned" else "solid",
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=INK, weight="bold", zorder=4)
    if ai:
        ax.text(x + w - 0.13, y + h - 0.10, "AI", ha="center", va="center",
                fontsize=5.8, color=TEAL, weight="bold", zorder=5,
                bbox=dict(boxstyle="circle,pad=0.16", facecolor=WHITE,
                          edgecolor=TEAL, linewidth=0.7))


def label(ax, x, y, w, h, text, status, wrap_n, fs=7.4):
    """The explanation box, plus the leader that points at the node above it."""
    ax.add_patch(mp.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.05",
        linewidth=0.8, edgecolor="#D3DBE3", facecolor=WHITE, zorder=2,
    ))
    ax.text(x + w / 2, y + h / 2, wrap(text, wrap_n), ha="center", va="center",
            fontsize=fs, color=INK, zorder=4, linespacing=1.55)
    cx = x + w / 2
    ax.annotate("", xy=(cx, y + h + 0.34), xytext=(cx, y + h + 0.02), zorder=4,
                arrowprops=dict(arrowstyle="-|>", color=EDGE[status], lw=1.1,
                                shrinkA=0, shrinkB=0,
                                mutation_scale=8))


def run_row(ax, y_node, y_label, w, h_node, h_label, items, wrap_n, name_fs=9.4,
            gap=0.20, fs=7.4):
    total = len(items) * w + (len(items) - 1) * gap
    x = (16 - total) / 2
    for it in items:
        name, status, plain, ai = it
        node(ax, x, y_node, w, h_node, name, status, ai, fs=name_fs)
        label(ax, x, y_label, w, h_label, plain, status, wrap_n, fs)
        x += w + gap


def arrows(ax, y_node, w, h_node, n, gap):
    total = n * w + (n - 1) * gap
    x = (16 - total) / 2
    for _ in range(n - 1):
        ax.annotate("", xy=(x + w + gap - 0.04, y_node + h_node / 2),
                    xytext=(x + w + 0.02, y_node + h_node / 2), zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))


fig, ax = plt.subplots(figsize=(16, 9.6), dpi=150)
ax.set_xlim(0, 16)
ax.set_ylim(2.30, 11.80)
ax.axis("off")
fig.patch.set_facecolor(WHITE)

# ---------------------------------------------------------------- title ----
ax.text(0.55, 11.42, "論文 → 簡報：每一格做咩", fontsize=21, color=INK, weight="bold")
ax.text(0.55, 11.02, "方塊＝系統的一步；下面的框＝用日常講法講一次，引線指住它屬於邊一格。"
                     "顏色＝進度（2026-10-23）", fontsize=10.2, color=INK2)

# ================================================================= A 生成 ==
ax.text(0.55, 10.42, "A · 由論文變成文字", fontsize=10.5, color=GREY, weight="bold")
run_row(ax, 9.62, 8.42, 1.92, 0.62, 1.04,
        [(n, s, p, ai) for n, t, p, s, ai in PIPELINE], wrap_n=14, fs=7.2)
arrows(ax, 9.62, 1.92, 0.62, 7, 0.20)

# ================================================================= B 量度 ==
ax.text(0.55, 8.06, "B · 用程式檢查，唔用感覺", fontsize=10.5, color=GREY, weight="bold")
run_row(ax, 7.26, 6.06, 1.78, 0.62, 1.04,
        [(n, s, p, False) for n, t, p, s in GATES + SCORES], wrap_n=13, gap=0.16, fs=7.4)
arrows(ax, 7.26, 1.78, 0.62, 6, 0.16)

# ================================================================= C 修復 ==
ax.text(0.55, 5.70, "C · 發現問題就修（論文的主貢獻）", fontsize=10.5, color=GREY,
        weight="bold")
run_row(ax, 4.90, 3.70, 2.92, 0.62, 1.04,
        [(n, "planned", p, False) for n, t, p in CONTROL], wrap_n=22, gap=0.30, fs=7.4)
arrows(ax, 4.90, 2.92, 0.62, 5, 0.30)

# ============================================================== footnote ====
ax.text(0.55, 3.06,
        "「AI」小圓點＝這一格用大型語言模型；冇圓點＝固定規則，答案每次一樣。",
        fontsize=8.2, color=INK2)
ax.text(0.55, 2.76,
        "「修完再量」只回到分數，唔會回到文字 —— 所以檢查的功勞同改寫的功勞分得開。",
        fontsize=8.2, color=INK2)

# ================================================================ legend ===
lx = 10.55
for text, st in (("已做好並有測試", "done"), ("做了一半", "partial"), ("未開始", "planned")):
    ax.add_patch(mp.FancyBboxPatch((lx, 10.48), 0.24, 0.18,
                                   boxstyle="round,pad=0.01,rounding_size=0.04",
                                   linewidth=1.4, edgecolor=EDGE[st], facecolor=FILL[st],
                                   zorder=3))
    ax.text(lx + 0.31, 10.57, text, fontsize=8.0, color=INK2, va="center")
    lx += 1.66

ax.text(15.45, 2.76, "Mizuki0215/capstone-ppt-agent · docs/diagrams/make_annotated.py",
        ha="right", fontsize=7.2, color=GREY)

fig.savefig(OUT, dpi=150, facecolor=WHITE, bbox_inches="tight", pad_inches=0.18)
print("wrote", OUT)
