#!/bin/bash
# 여러 운영 덱을 하나로 합본 (파일명 충돌 회피 + assets 머지).
# preflight 패턴이 slide-{숫자}.html 만 받으므로 덱별 숫자 offset 부여.
# 사용: bash build-mix.sh <출력폴더> <덱루트> <덱1> <덱2> ...
# 예  : bash tests/ab-method/build-mix.sh C:/msys64/tmp/realmix D:/projects/slides-grab/slides \
#         ai-infra-investment samsung-investment-report naver-investment-strategy
set -e
MIX="$1"; ROOT="$2"; shift 2
rm -rf "$MIX"; mkdir -p "$MIX/assets"
off=1000
for d in "$@"; do
  for f in "$ROOT/$d"/slide-*.html; do
    [ -e "$f" ] || continue
    num=$(basename "$f" .html | grep -oE '[0-9]+' | sed 's/^0*//')
    cp "$f" "$MIX/slide-$((off + num)).html"
  done
  cp -rn "$ROOT/$d/assets/." "$MIX/assets/" 2>/dev/null || true
  off=$((off + 1000))
done
echo "합본: $(ls "$MIX"/slide-*.html | wc -l) 장, assets $(ls "$MIX/assets" 2>/dev/null | wc -l) 개"
echo "주의: assets 동명 충돌 시 첫 것만(cp -n) — 일부 이미지 깨질 수 있음(텍스트 룰 PF-28/VP-16/sibling-overlap엔 무영향, overflow-outside-frame은 신뢰도 낮아짐)"
