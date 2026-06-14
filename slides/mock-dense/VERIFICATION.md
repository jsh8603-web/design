# 핸드오프 규칙 검증 리포트 (2026-06-14)

> 핸드오프 문서(§G 5건 + §A overlap)가 제안한 검출 규칙 변경을, **합성 슬라이드 + 실제 PowerPoint 렌더(COM)**로 직접 A/B 검증하고 추가 수정까지 반영한 기록. 다음 세션이 이 파일만으로 "왜 이렇게 바꿨나"를 재구성할 수 있도록 측정 데이터·그라운드트루스·정정 이력을 모두 박제.

## 1. 목적과 방법

- **검증 대상**: PF-25(폰트 px) · PF-28(텍스트량 출처제외) · PF-18(겹침) · VP-16(CJK 폭) · validate-slides(sibling-overlap) · G4(convert silent-failure) · G5(draft-marp stdin/Chrome).
- **합성 슬라이드**: `slide-1~6.html` (body 960×540px, LAYOUT_16x9). 그라운드트루스를 미리 알고 설계.
  - slide-1: 고밀도 텍스트 + 9px 출처(PF-25/28)
  - slide-2: 겹침 4종 — text-on-text 43%(결함) / 박스 10%(경계) / 배지-온-이미지(의도) / flex 레이어(의도)
  - slide-3: CJK 박스 여유도 스펙트럼(VP-16)
  - **slide-4~6: 적대적 케이스** — 새 규칙이 FN(놓침) 낼 함정
- **그라운드트루스**: `node scripts/screenshot-html.mjs`(HTML 렌더) + `powershell scripts/export-slides-png.ps1`(PowerPoint COM 렌더). 산출물 `png/`, `pptx-png/`(재생성 가능, 미커밋).
- **검출 비교**: 기존 HEAD 코드(백업 `/tmp/*-OLD.js`) vs 새 규칙. 회귀는 무관 규칙 카운트 불변으로 확인.

> node는 `/c/Program Files/nodejs`. 빽빽한 슬라이드는 PF-28 ERROR라 정상 변환이 막히므로 `convert-native --skip-preflight`로 PPTX를 강제 생성해 VP-16까지 측정.

## 2. 규칙별 판정 (그라운드트루스 = PowerPoint 렌더)

| 규칙 | 기존 | 새 규칙 | 렌더 진실 | 판정 |
|---|---|---|---|---|
| **PF-25** px 인식 | px 무시 → 9px 미검출(FN) | px×0.75→pt, 6건 검출 | 9·11·13px 모두 10pt 미만 = 위반 | ✅ 개선 |
| **PF-28** 출처 제외 | source/caption 합산(334) | 제외(294) | 출처는 부수텍스트 | ✅ 개선(등급 불변, 내용 정확) |
| **PF-18** 겹침 | worst 1건만(43%) | ERROR 1 + WARN 1 동시(43%+10%) | 한 슬라이드 다중 겹침 | ✅ 개선(노출↑) |
| **validate-slides** | 4종 일률 WARN, flex·배지 오탐 | critical/warn 분화 + 의도 레이아웃 skip | flex·배지=의도, 43%=결함, 10%=미세 | ✅ 개선 + FN 보완(아래 §3) |
| **VP-16** CJK 폭 | 0.55 균일 → 한글 FP(95/104%) | CJK1.0/Latin0.5/공백0.25 | slide-2 한글 실제 안 넘침 | ✅ 개선(FP 제거) |
| **G4** silent-failure | 부분/전량실패도 exit 0 + 빈/누락 덱 출하 | exit 1 + 빈 덱 미작성 | — | ✅ 개선, 부작용 0 |
| **G5** draft-marp | 비대화형 stdin 대기로 멈춤 | --no-stdin + CHROME_PATH 자동 | — | ✅ 91714B PPTX 생성 |

### 디테일
- **PF-25 경계 정확성**(slide-6): 10px(7.5pt)·12px(9pt)·13px(9.75pt) 검출 / **13.34px(10.005pt)·14px·16px 통과** — px→pt 0.75 환산 경계 오판 없음.
- **PF-18 ERROR-gate 주의**: `convert-native`는 preflight ERROR가 하나라도 있으면 `process.exit(0)`(:117)으로 WARN 출력 전에 종료한다. PF-18의 ERROR+WARN 동시 생성은 `preflightCheck()` 직접 호출의 `.errors`/`.warnings`에서 확인됨(convert 출력만으로는 WARN이 안 보임).

## 3. 적대적 케이스 — "다 승자"가 아님을 확인

새 규칙이 **FN(놓침)** 내는 함정을 만들어 검증한 결과, trade-off가 실재함:

- **validate-slides FN (실재)**: slide-5 — flex 자식 두 텍스트가 **완전히 겹쳐 판독불가**(A), "긴급 정정 공지"가 본문 글자를 **가림**(B). 무조건 skip이 이 진짜 결함을 묵인.
  → **추가 수정**: flex/containment 겹침이라도 **양쪽이 텍스트면 WARNING으로 노출**(critical은 아님 → 빌드는 통과시키되 검토 신호). 한쪽이 비텍스트(이미지+배지 오버레이)면 skip 유지. 결과: slide-5 warn 2건으로 노출, slide-2 배지 skip·flex레이어 warn.

- **VP-16 "라틴 FN"은 오판이었음 (정정)**: 처음엔 `Total addressable market...now` 등 영문장 wrap을 FN으로 봤으나, 실측 결과 — (a) VP-16은 `cjkRatio < 0.2`면 검사 자체를 skip(CJK 폭 전용 규칙). 순영문은 **설계상 대상 밖**. (b) 새 계수가 순라틴 실측과 거의 일치.

## 4. VP-16 계수 측정 데이터 (Playwright measureText, 100px 폰트)

| 문장 | 실측(em) | 새(0.5/0.25) | 기존(0.55) | cjk/lat/sp |
|---|---|---|---|---|
| Total addressable market...(순라틴) | 22.22 | 22.50 | 26.40 | 0/42/6 |
| we expect a strong rebound...(순라틴) | 23.41 | 23.25 | 28.05 | 0/42/9 |
| 분기 매출 전년比 12.4%...(한글) | 13.66 | 14.75 | 16.50 | 11/5/5 |
| 영업이익률 추가 개선 여력 확보(한글) | 12.24 | 14.00 | 15.20 | 13/0/4 |
| 데이터센터 전력 효율...(한글) | 19.91 | 22.75 | 24.85 | 21/0/7 |

- **라틴**: 새 계수(0.5/0.25)가 실측과 거의 일치, 기존(0.55)은 과대.
- **한글**: 양쪽 다 과대추정. 근본 원인은 **CJK 1.0이 실측 ~0.9보다 큼**(공백 아님).
- **공백 0.4 보정 시도 → 철회**: 측정에서 공백 ~0.40이 나와 0.25→0.4로 올렸더니 slide-2 "분기 매출" 97% **FP가 재발**(실제 안 넘침). FP 주범은 공백이 아니라 CJK 1.0이므로, 공백 상향은 개악. **0.25 원복**. CJK 1.0은 보수적으로 유지(과대추정이 FN보다 안전, PPTX 임베드 Pretendard 실폭 불확실).

## 5. 추가 수정 3건 (이 커밋)

1. **validate-slides** `scripts/validate-slides.js`: flex/containment 텍스트-텍스트 겹침을 skip 대신 WARNING 노출(§3). 비텍스트 오버레이는 skip 유지.
2. **PF-18** `scripts/preflight-html.js`: worst 1건 → worstError(≥20%) + worstWarn(5–20%) 분리, 둘 다 보고.
3. **VP-16** `scripts/validate-pptx.js`: 공백 0.25 유지(0.4 철회), CJK 1.0 유지. 주석에 measureText 근거 박제.

## 6. 회귀 (mock-dense 6장, 무관 규칙 불변)

| | OLD | NEW |
|---|---|---|
| PF-25 | 0 | 6 (의도) |
| PF-28 | 1 | 1 (단어수 334→294) |
| PF-35/36 | 1/4 | 1/4 **(불변)** |
| VP-02/03/04/09/10/11/14 | 3/18/18/9/3/4/3 | **(전부 동일)** |
| VP-16 | 16 | 14 (한글 FP 2건 제거) |
| validate-slides overlap | crit0/warn6 | crit1/warn(slide별) |

→ 의도하지 않은 규칙(PF-35/36, VP 7종)의 카운트가 전부 불변 = 다른 규칙 오염 없음.
→ G4: 부분실패·전량실패 모두 exit 1, 전량실패 시 빈 덱 미작성 확인.
→ G5: 비대화형 91714바이트 PPTX 생성(멈춤 해소).

## 7. 결론 · 잔여 한계

- 7개 규칙 모두 채택(개선 또는 trade-off 보완 완료). 단 **"무조건 우월"은 아님**:
  - validate-slides는 flex/containment 진짜 결함을 critical로 막지 못하고 WARNING으로만 노출(의도 레이아웃과 자동 구분 불가 → 사람 검토 필요).
  - VP-16 CJK 1.0은 실측보다 과대(보수적 선택). 한글 위주 실전엔 충분하나 calibration 여지 있음.
  - PF-18 다중 겹침은 ERROR 1 + WARN 1까지만(같은 등급 다수는 여전히 worst 1).
- **실세계 빈도 축 미검증**: `slides/`에 과거 baseline 덱이 없어, 합성 6장으로만 검증. 실덱 확보 시 `tests/run-full-regression.mjs`로 baseline 재생성 권장.
- 측정은 합성 슬라이드 기반(내가 그라운드트루스를 알고 설계) — 우호적 편향 가능성이 있어 적대적 케이스(slide-4~6)를 병행했음.

## 8. 운영 덱 검증 (slides-grab 156장, §7 실세계 빈도 축 메움)

빽빽한 투자/업무 덱 8개(ai-infra·samsung·naver·kakao·posco·coupang·commodity·payroll-guide)를 합본해 기존 vs 새 규칙 A/B.

| 항목 | OLD | NEW(커밋) | diff | 판정 |
|---|---|---|---|---|
| **VP-16** | 786 | 671 | **-115 (-15%)** | ✅ 최대 실효 (한글 폭 FP 제거, 30장에서 23건 렌더 확인과 동일 패턴) |
| **validate-slides warn** | 116 | 36 | **-80** | ✅ 의도 레이아웃(카드 그리드) 오탐 제거 + 텍스트겹침 노출 유지 |
| PF-28 | 89 | 84 | -5 | 미미 |
| **PF-25** | 61 | 61 | **0** | 운영 덱은 작은 폰트를 pt로 쓰고 px 9px급이 없음 → px 변경 효과 0 (무해한 안전망) |
| **PF-18** | 1 | 1 | **0** | 겹침 1건뿐 → ERROR+WARN 분리 발동 안 함 |
| 나머지 PF 30종·VP 9종 | = | = | 0 | 회귀 안전 |

- **핵심**: VP-16·validate-slides가 운영 덱 노이즈를 크게 줄임. PF-25/PF-18은 잘 만든 덱엔 트리거 0 (결함 생겼을 때를 위한 안전망).
- **합본 한계**: validate-slides critical(103/105)은 합본 이미지 일부 깨짐(assets 머지 누락)으로 overflow 오염 → 신뢰도 낮음. 정상 단일 덱(real-ai/sam/po/cm.pptx)으로 개별 검증함.

## 9. VP-16 CJK 계수 0.92 재보정 (운영 덱이 이끈 추가 개선)

운영 덱 671건 중 WARN 508건의 fills% 분포가 96~116% 경계에 몰려(CJK 1.0 과대추정). measureText 실측 CJK ~0.9를 반영해 1.0 → 0.92 재보정:

- **정상덱(ai+samsung) VP-16: 77 → 58 (-19, -25%)**, 합본 671 → 568.
- **빠진 케이스 렌더 검증 (FN 0)**: 1.0 WARN→0.92 PASS된 케이스("2024 글로벌 DC 전력 소비", "4대 하이퍼스케일러 투자 비교", "기회:전력 인프라...")가 PPTX 렌더(Pretendard 임베드)에서 전부 1줄로 박스 안에 들어감.
- **will overflow 7 → 4도 FP 격하 검증**: 빠진 3건(posco "구조개편 73건 완료로 1.8조원..." / commodity "변동성 시대를 위한 전략적 통찰")을 정상 덱 렌더로 확인 → posco는 카드 안 3줄 정상 표시, commodity는 2줄 wrap(화면 밖 넘침 아님). 1.0의 "shape too short" 판정이 과한 오판이었음.
- **CJK 1.0 → 0.92 채택**. whitespace 0.25·Latin 0.5는 유지(0.4는 §4에서 FP 재발로 철회). measureText(Malgun fallback) + PPTX(Pretendard) 양쪽 렌더로 교차 검증.
