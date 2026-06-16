#!/usr/bin/env bash
# 헤드리스 Chrome 으로 슬라이드 HTML 을 1280x720 PNG 로 일괄 렌더 (디자인 원본 = 의도 기준).
# COM PPTX 렌더와 나란히 비교해 변환 결함(글자 유실·클리핑)을 시각화하는 용도.
# usage: render-html-batch.sh [rounds] [themes]
set -u
cd /d/projects/design

CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
OUTDIR="slides/_render-check"
OUTWIN="D:/projects/design/slides/_render-check"
mkdir -p "$OUTDIR"

ROUNDS="${1:-13 14}"
THEMES="${2:-modern classic company academic dark-mono dark-pitch executive-editorial editorial}"

n=0; ok=0; miss=0
for r in $ROUNDS; do
  for t in $THEMES; do
    d="slides/round${r}-${t}"
    [ -d "$d" ] || { echo "SKIP [디렉토리없음] $d"; continue; }
    for f in "$d"/slide-0*.html; do
      [ -f "$f" ] || continue
      base=$(basename "$f" .html)          # slide-0X
      num="${base##*-}"                    # 0X
      out="${OUTWIN}/r${r}-${t}-s${num}.png"
      url="file:///D:/projects/design/${d}/${base}.html"
      n=$((n+1))
      "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
        --force-device-scale-factor=1 --window-size=1280,720 \
        --virtual-time-budget=3000 --screenshot="$out" "$url" >/dev/null 2>&1
      if [ -f "$OUTDIR/r${r}-${t}-s${num}.png" ]; then ok=$((ok+1)); else miss=$((miss+1)); echo "FAIL $out"; fi
    done
  done
done
echo "=== 렌더 완료: 시도 $n, 성공 $ok, 실패 $miss ==="
ls "$OUTDIR" | wc -l