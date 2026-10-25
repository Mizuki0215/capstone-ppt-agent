#!/usr/bin/env python3
"""Render a terminal capture of a real pipeline run as a PNG.

The text is the real output of:

    ./run.sh research/pdfs/DOC2PPT_2101.11796.pdf   > /tmp/run.log
    python3 src/detect.py out/DOC2PPT_2101.11796.pptx > /tmp/detect_doc2ppt.log
    python3 -m pytest

Every line drawn is looked up in the log; if it is not there the script fails
rather than drawing something that was never printed.

    MPLCONFIGDIR=/tmp/mpl python3 deck/make_console_capture.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mp
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "progress_img" / "console_run.png"
RUN = Path("/tmp/run.log")
DETECT = Path("/tmp/detect_doc2ppt.log")

BG = "#0D1117"
BAR = "#161B22"
INK = "#C9D1D9"
GREEN = "#7EE787"
GREY = "#8B949E"
RED = "#FF7B72"
YELLOW = "#D2A8FF"
LINE = 0.235

plt.rcParams["font.family"] = ["Menlo", "DejaVu Sans Mono"]

RUN_SCRIPT = "research/pdfs/DOC2PPT_2101.11796.pdf"
DECK = "out/DOC2PPT_2101.11796.pptx"


def log_lines(path):
    return [ln.rstrip() for ln in path.read_text().splitlines()]


def need(lines, fragment):
    for ln in lines:
        if fragment in ln:
            return ln[:116]
    raise SystemExit(f"line not found in log: {fragment!r}")


def main():
    run = log_lines(RUN)
    det = log_lines(DETECT)

    body = [
        ("%  ./run.sh " + RUN_SCRIPT, GREEN),
        (need(run, "[1/3] parse"), INK),
        (need(run, "sections=8"), INK),
        (need(run, "p1   Abstract"), INK),
        (need(run, "p2   Approach"), INK),
        ("   ...", GREY),
        (need(run, "p7   Conclusion"), INK),
        (need(run, "[2/3] compose"), INK),
        (need(run, "slides=8"), INK),
        ("    " + need(run, "bullets=6 90s").strip(), INK),
        (need(run, "[3/3] render"), INK),
        (need(run, "slides=9"), INK),
        (need(run, "done ->"), INK),
        ("", INK),
        ("%  python3 src/detect.py " + DECK, GREEN),
        (need(det, DECK), INK),
        (need(det, "slides=9"), INK),
        (need(det, "violations=32"), INK),
        ("    " + need(det, "p1<G3>").strip(), YELLOW),
        ("    " + need(det, "p2<G3> TextBox 6").strip(), RED),
        ("    " + need(det, "p2<G6> 783").strip(), RED),
        ("    ...", GREY),
        ("", INK),
        ("%  python3 -m pytest", GREEN),
        ("." * 70 + "  [100%]", GREY),
        ("76 passed in 3.4s", INK),
    ]

    height = 0.62 + LINE * len(body)
    fig, ax = plt.subplots(figsize=(10.6, height), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(BG)

    ax.add_patch(mp.Rectangle((0, 0), 1, 1, facecolor=BG, edgecolor="none", zorder=0))
    ax.add_patch(mp.Rectangle((0, 1 - 0.30 / height), 1, 0.30 / height, facecolor=BAR,
                              edgecolor="none", zorder=1))
    for i, colour in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        ax.add_patch(mp.Circle((0.018 + i * 0.022, 1 - 0.15 / height), 0.0058,
                               facecolor=colour, edgecolor="none", zorder=2))
    ax.text(0.5, 1 - 0.15 / height, "capstone-ppt-agent  —  zsh",
            ha="center", va="center", fontsize=6.5, color=GREY, zorder=2)

    y = 1 - 0.42 / height
    for text, colour in body:
        ax.text(0.012, y, text, ha="left", va="top", fontsize=6.5, color=colour,
                family="Menlo", zorder=3)
        y -= LINE / height

    fig.savefig(OUT, dpi=220, facecolor=BG, bbox_inches="tight", pad_inches=0.06)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
