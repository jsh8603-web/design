#!/bin/bash
# 생성 e2e 덱 전수 회귀: 현 파이프라인으로 재변환+VP → ERROR=0 유지 확인
cd /d/projects/design
NODE="/c/Program Files/nodejs/node.exe"
TOT_E=0; N=0; FAIL=""
for d in slides/e2e-* slides/e2e2-* slides/e2e3-* slides/e2e4-*; do
  [ -d "$d" ] || continue
  ls "$d"/slide-*.html >/dev/null 2>&1 || continue
  N=$((N+1))
  "$NODE" scripts/convert-native.mjs --slides-dir "$d" --output "/tmp/rg_$(basename $d).pptx" --skip-preflight --skip-validation >/dev/null 2>&1
  E=$("$NODE" scripts/validate-pptx.js --input "/tmp/rg_$(basename $d).pptx" 2>&1 | grep -cE "❌ ERROR")
  TOT_E=$((TOT_E+E))
  [ "$E" -gt 0 ] && { FAIL="$FAIL $(basename $d):$E"; echo "  ⚠️ $(basename $d): ERROR=$E"; }
  rm -f "/tmp/rg_$(basename $d).pptx"
done
echo "=== 생성덱 회귀: $N 덱, 총 ERROR=$TOT_E ==="
[ "$TOT_E" -eq 0 ] && echo "✅ 전 생성덱 ERROR=0 (회귀 없음)" || echo "❌ 회귀: $FAIL"
