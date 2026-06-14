# FN 검증 — 미발화 38규칙 결함주입 재현 자산

운영덱(realmix 156장)에서 미발화인 규칙들이 **진짜 결함이 있을 때 발화하는지(=FN 0)** 확인하는 재현 자산.
미발화 = 깨끗한 운영덱에 해당 결함이 없어서일 뿐, 규칙이 망가진 게 아님을 입증한다.

## 배경
- **PF 규칙**: `preflight-html.js` 가 HTML 원본을 정규식 검사 → 결함 HTML 을 preflight 에 직접 먹이면 발화. (convert-native 불요)
- **VP 규칙**: `validate-pptx.js` 가 PPTX XML 검사. 일부 결함(오프슬라이드·그림겹침·테이블)은 **convert-native 가 상류 차단/정규화**(오버플로 conversion FAIL / 그림 항상 텍스트 뒤 / HTML table→도형) → HTML 픽스처로 트리거 불가 = 외부PPTX용 defense-in-depth. → PPTX XML 에 결함을 **직접 주입**해 검증.

## 재현
```bash
export PATH="/c/Program Files/nodejs:$PATH"

# PF 미발화 31규칙 (slide-1/2.html = 결함 다발)
node scripts/preflight-html.js --slides-dir slides/rule-audit/fn-verify --full
#   → PF-02·04·05·06·07·12·13·14·16·17·34·38·39·43·44·46·48·49·50·51·52·53·54·55·56·57·58·59·61·62·63 발화

# VP 미발화 7규칙 (base pptx 에 결함 주입)
node slides/rule-audit/fn-verify/inject-vp-defects.mjs <base.pptx> /tmp/fn.pptx
node scripts/validate-pptx.js --input /tmp/fn.pptx
#   → VP-01(오프슬라이드) 05/06(테이블 빈셀·열수) 12(도형<2) 13(미디어>5MB) 15(그림 텍스트위) 발화
# VP-08(그리드 빈카드)은 ../slide-vp08.html 로 별도 검증
```

## 결과 (2026-06-14)
| 그룹 | 규칙수 | 결과 |
|---|---|---|
| 미발화 PF | 31 | **31/31 발화** (결함 주입 시) |
| 미발화 VP | 7 (01·05·06·08·12·13·15) | **7/7 발화** |
| **합계** | **38** | **FN 0 — 전 규칙 정상 작동 확인** |

## 결함→규칙 매핑 (주요)
- VP-01 오프슬라이드 / VP-05 빈 테이블셀 / VP-06 테이블 열수 불일치 / VP-08 그리드 빈카드 / VP-12 도형<2 / VP-13 미디어>5MB / VP-15 그림이 텍스트 위
- PF-02 flex:1 no box-sizing / PF-04 img height:100% / PF-05 div bg url / PF-07 p에 background / PF-12 국기이모지 / PF-13 border-radius:50%+border / PF-34 block span 혼합 / PF-38 underline / PF-43 object-fit:fill / PF-44 outline / PF-46 text-indent / PF-49 mix-blend-mode / PF-50 border-image / PF-51 sticky / PF-52 @font-face / PF-53 rtl / PF-54 white-space:pre / PF-55 span bg+color / PF-59 flex:1+overflow:hidden+큰 자식높이 / PF-62 conic-gradient / PF-63 table 등
