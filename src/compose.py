#!/usr/bin/env python3
"""Stage 2 - build a slide plan (outline, bullets, speaker notes) from parsed JSON.

Pure standard library. Default mode is deterministic and needs no API key; pass
--llm to have a model rewrite the bullets and notes instead.
"""
import argparse
import json
import os
import re
import urllib.request

MAX_SLIDES = 12
BULLETS_PER_SLIDE = (4, 6)
MAX_WORDS = 14
TOTAL_SECONDS = 12 * 60

CITE = re.compile(r"\([A-Z][^()]{0,80}?(?:19|20)\d{2}[a-z]?\)")
NUMLIKE = re.compile(r"\d")
STOPISH = {"the", "of", "and", "to", "in", "a", "is", "we", "that", "for"}


KEEP_HYPHEN = {
    "well", "state", "end", "real", "self", "cross", "long", "short", "open", "closed",
    "high", "low", "rule", "task", "text", "image", "data", "model", "human", "non",
    "pre", "post", "co", "multi", "few", "zero", "one", "two", "three", "vision",
}


def _rejoin(m):
    a, b = m.group(1), m.group(2)
    if len(a) <= 2 or a.lower() in KEEP_HYPHEN:
        return f"{a}-{b}"          # sequence-to- sequence -> sequence-to-sequence
    return a + b                  # doc- uments -> documents


def dehyphenate(text):
    text = re.sub(r"([A-Za-z]+)-\s+([a-z]+)", _rejoin, text)
    return re.sub(r"\s+", " ", text)


def sentences(text):
    text = dehyphenate(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        p = CITE.sub("", p)
        p = re.sub(r"\s+", " ", p).strip(" .;,")
        if not (40 <= len(p) <= 320):
            continue
        if not p[:1].isupper():                      # fragments such as "2011), exiting work..."
            continue
        if re.match(r"^(19|20)\d{2}\b", p):
            continue
        if p.lower().count("et al") >= 2:            # citation soup
            continue
        out.append(p)
    return out


def score(s):
    words = s.split()
    if not words:
        return -99
    sc = 0.0
    if NUMLIKE.search(s):
        sc += 2.0          # numbers carry claims
    if 8 <= len(words) <= 22:
        sc += 1.5          # fits a bullet
    sc -= 0.06 * abs(len(words) - 14)
    if words[0].lower() in STOPISH:
        sc -= 0.8
    if s.lower().startswith(("however", "therefore", "in this", "we ")):
        sc += 0.6
    return sc


def clip_words(s, n=MAX_WORDS):
    w = s.split()
    if len(w) <= n:
        return " ".join(w)
    return " ".join(w[:n]).rstrip(",;:") + " ..."


def key_terms(title):
    return [w.lower() for w in re.findall(r"[A-Za-z]{5,}", title)]


def pick_bullets(sec, k_max=6):
    body = sec["text"]
    cands = sentences(body)
    if not cands:
        return []
    terms = key_terms(sec["title"])
    ranked = sorted(cands, key=lambda s: score(s) + 0.4 * sum(t in s.lower() for t in terms),
                    reverse=True)
    chosen, seen = [], set()
    for s in ranked:
        key = " ".join(s.lower().split()[:6])
        if key in seen:
            continue
        seen.add(key)
        chosen.append(clip_words(s))
        if len(chosen) >= k_max:
            break
    return chosen


def build_notes(slide, idx, total, seconds):
    b = slide["bullets"]
    lead = b[0] if b else slide["title"]
    tail = b[1] if len(b) > 1 else ""
    note = (
        f"This slide covers {slide['title'].lower()}. "
        f"Open with: {lead}. "
    )
    if tail:
        note += f"Then move to: {tail}. "
    note += f"Target roughly {max(20, round(seconds))} seconds here."
    return note


def plan_from_json(data):
    secs = [s for s in data["sections"] if len(s["text"]) >= 160]
    secs = [s for s in secs if not re.match(r"^(acknowledg|appendix)", s["title"], re.I)]
    if len(secs) > MAX_SLIDES - 1:
        # keep the first N-1 and always try to keep a closing section
        tail = [s for s in secs if re.match(r"^conclusion", s["title"], re.I)]
        head = [s for s in secs if s not in tail][: MAX_SLIDES - 2]
        secs = head + tail[:1]
    slides = []
    for i, s in enumerate(secs):
        b = pick_bullets(s, k_max=BULLETS_PER_SLIDE[1])
        if len(b) < 2:
            continue
        if len(b) < BULLETS_PER_SLIDE[0]:
            b = b + [clip_words(x) for x in sentences(s["text"])][: BULLETS_PER_SLIDE[0] - len(b)]
        slides.append({
            "title": s["title"][:70],
            "bullets": b[:BULLETS_PER_SLIDE[1]],
            "source_page": s["page"],
        })
    # figures: attach the first unused caption to a mid-deck slide
    figs = data.get("figures", [])
    if figs and len(slides) >= 3:
        slides[2]["figure"] = figs[0]["caption"][:160]
    seconds = TOTAL_SECONDS / max(1, len(slides))
    for sl in slides:
        sl["seconds"] = round(seconds)
        sl["notes"] = build_notes(sl, 0, len(slides), seconds)
    return {"title": data.get("title", "Untitled"), "slides": slides}


def llm_rewrite(plan, model="gpt-4o-mini"):
    """Optional: rewrite bullets and notes. Falls back silently on any error."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("  (no OPENAI_API_KEY - keeping heuristic output)")
        return plan
    for sl in plan["slides"]:
        prompt = (
            "Rewrite this slide for a 12-minute conference talk. Return JSON only: "
            '{"title": str, "bullets": [str], "notes": str}. '
            "Rules: 4-6 bullets, each <= 14 words, no citations, no new facts; "
            "notes = 2-3 sentences a speaker can read aloud, including a time cue.\n"
            f"Slide title: {sl['title']}\nBullets so far: {sl['bullets']}\n"
            f"Target seconds: {sl['seconds']}"
        )
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions", data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(json.loads(r.read())["choices"][0]["message"]["content"])
            if out.get("bullets"):
                sl["bullets"] = [clip_words(b, 16) for b in out["bullets"]][:6]
                sl["notes"] = out.get("notes", sl["notes"])
        except Exception as e:  # noqa: BLE001
            print("  llm skipped:", e)
            break
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck_json")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--llm", action="store_true")
    args = ap.parse_args()
    data = json.load(open(args.deck_json))
    plan = plan_from_json(data)
    if args.llm:
        plan = llm_rewrite(plan)
    json.dump(plan, open(args.out, "w"), indent=1)
    print(f"slides={len(plan['slides'])} -> {args.out}")
    for s in plan["slides"]:
        print(f"  {s['title'][:52]:52s} bullets={len(s['bullets'])} {s['seconds']}s")


if __name__ == "__main__":
    main()
