#!/usr/bin/env bash
# End-to-end generator: PDF -> .pptx (with speaker notes)
# Stage 1 needs PyMuPDF, stage 3 needs python-pptx; they live in different interpreters.
set -euo pipefail

PDF="${1:?usage: ./run.sh paper.pdf [--llm]}"
NAME="$(basename "$PDF" .pdf)"
shift || true

PY_PARSE="${PY_PARSE:-/opt/anaconda3/bin/python3}"          # has PyMuPDF
PY_RENDER="${PY_RENDER:-/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/python/bin/python3}"  # has python-pptx

mkdir -p build out

echo "[1/3] parse"
"$PY_PARSE" src/parse.py "$PDF" -o "build/$NAME.deck.json"

echo "[2/3] compose"
python3 src/compose.py "build/$NAME.deck.json" -o "build/$NAME.plan.json" "$@"

echo "[3/3] render"
"$PY_RENDER" src/render.py "build/$NAME.plan.json" -o "out/$NAME.pptx"

echo "done -> out/$NAME.pptx"
