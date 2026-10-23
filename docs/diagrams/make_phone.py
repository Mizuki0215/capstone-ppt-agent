#!/usr/bin/env python3
"""Phone version of the status diagram: portrait, one block per row.

Landscape is fine on a desktop and unreadable on a phone. This figure stacks the
same blocks vertically, keeps the plain-language line in larger type, and puts
the block name on the left so it can be read without pinching.

Regenerate with:
    MPLCONFIGDIR=/tmp/mpl python3 docs/diagrams/make_phone.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp
import matplotlib.pyplot as plt

from content import CONTROL, GATES, PIPELINE, SCORES

OUT = Path(__file__).resolve().parent / "status_2026-10-23_phone.png"

INK = "#10233A"
INK2 = "#3C4E60"
GREY = "#8A99A8"
GREEN = "#2F7D5D"
AMBER = "#C08A2E"
TEAL = "#2E6F95"
RED = "#A83542"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = ["PingFang HK", "Helvetica Neue", "Arial"]

PAGE_W = 7.2
X0 = 0.34
CW = PAGE_W - 2 * X0
SPLIT = 2.24          # name column / plain-line column
ROW_H = 0.62
PITCH = 0.70

FILL = {"done": "#E6F2EC", "partial": "#FBF1DE", "planned": "#EEF1F4"}
EDGE = {"done": GREEN, "partial": AMBER, "planned": GREY}


class Cursor:
    """Top-down layout: each element is placed by how much height it needs."""

    def __init__(self, top):
        self.y = top

    def take(self, h):
        self.y -= h
        return self.y


def row(ax, y, h, name, tech, plain, status, ai=False, name_fs=9.6, plain_fs=8.4):
    ax.add_patch(mp.FancyBboxPatch(
        (X0, y), CW, h, boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.5 if status != "planned" else 1.1,
        edgecolor=EDGE[status], facecolor=FILL[status], zorder=2,
        linestyle="--" if status == "planned" else "solid",
    ))
    ax.text(X0 + 0.16, y + h * 0.67, name, ha="left", va="center", fontsize=name_fs,
            color=INK, weight="bold", zorder=3)
    if tech:
        ax.text(X0 + 0.16, y + h * 0.27, f"AI · {tech}" if ai else tech,
                ha="left", va="center", fontsize=6.6,
                color=TEAL if ai else INK2, style="italic", zorder=3)
    ax.plot([X0 + SPLIT, X0 + SPLIT], [y + 0.10, y + h - 0.10], color=EDGE[status],
            lw=0.7, alpha=0.45, zorder=3)
    ax.text(X0 + SPLIT + 0.16, y + h / 2, plain, ha="left", va="center",
            fontsize=plain_fs, color=INK, zorder=3, wrap=True)


fig, ax = plt.subplots(figsize=(PAGE_W, 17.95), dpi=150)
ax.set_xlim(0, PAGE_W)
ax.set_ylim(0.15, 18.10)  # keep the legend swatches inside the axes
ax.axis("off")
fig.patch.set_facecolor(WHITE)
cur = Cursor(18.10)

# ---------------------------------------------------------------- title ----
cur.take(0.24)
ax.text(X0, cur.y, "DSAI4901 · CAPSTONE", fontsize=9, color=GREY, weight="bold")
cur.take(0.48)
ax.text(X0, cur.y, "論文 → 簡報", fontsize=21, color=INK, weight="bold")
cur.take(0.44)
ax.text(X0, cur.y, "每一格做咩，同埋邊部分做好咗", fontsize=11.5, color=INK2)
cur.take(0.30)
ax.text(X0, cur.y, "2026-10-23", fontsize=9, color=GREY)
cur.take(0.30)

# ================================================================= A 生成 ==
ax.text(X0, cur.y, "A · 由論文變成文字", fontsize=10.5, color=GREY, weight="bold")
cur.take(0.30)
for name, tech, plain, status, ai in PIPELINE:
    row(ax, cur.take(ROW_H), ROW_H, name, tech, plain, status, ai)
    cur.y -= PITCH - ROW_H
cur.take(0.24)

# ================================================================= B 量度 ==
ax.text(X0, cur.y, "B · 用程式檢查，唔用感覺", fontsize=10.5, color=GREY, weight="bold")
cur.take(0.30)
for name, thr, plain, status in GATES:
    row(ax, cur.take(ROW_H), ROW_H, name, thr, plain, status, name_fs=9.2)
    cur.y -= PITCH - ROW_H
for name, tech, plain, status in SCORES:
    row(ax, cur.take(ROW_H), ROW_H, name, tech, plain, status, name_fs=9.6)
    cur.y -= PITCH - ROW_H
cur.take(0.24)

# ================================================================= C 修復 ==
ax.text(X0, cur.y, "C · 發現問題就修（論文的主貢獻）", fontsize=10.5, color=GREY,
        weight="bold")
cur.take(0.30)
for name, tech, plain in CONTROL:
    row(ax, cur.take(ROW_H), ROW_H, name, tech, plain, "planned", name_fs=9.2)
    cur.y -= PITCH - ROW_H

# ================================================================ legend ===
cur.take(0.40)
legend = [("已做好，有測試", "#E6F2EC", GREEN), ("做了一半", "#FBF1DE", AMBER),
          ("未開始", "#EEF1F4", GREY)]
lx = X0
for label, fill, edge in legend:
    ax.add_patch(mp.Rectangle((lx, cur.y - 0.06), 0.17, 0.17, facecolor=fill,
                              edgecolor=edge, lw=1.4, zorder=3))
    ax.text(lx + 0.24, cur.y + 0.03, label, fontsize=8.2, color=INK2, va="center")
    lx += 1.62
cur.take(0.40)
ax.text(X0, cur.y, "藍色「AI ·」＝用大型語言模型；冇標記＝固定規則。", fontsize=7.6, color=INK2)
cur.take(0.24)
ax.text(X0, cur.y, "今天的位置：P1c 選段做完 —— 規則表 + 38 個測試綠燈，但未接上 pipeline。",
        fontsize=7.6, color=RED)

fig.savefig(OUT, dpi=150, facecolor=WHITE, bbox_inches="tight", pad_inches=0.12)
print("wrote", OUT)
