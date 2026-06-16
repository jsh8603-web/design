---
title: R1 디자인스킬 8테마 재현 e2e — 진행 핸드오프
tags: [handoff, design-system, e2e, round1, btn-design]
date: 2026-06-16
next-action: "★R1~R8 완료(8테마 ERROR0+COM의도보존+정탐회귀0). ★다음 우선순위 = 사용자 1번 선택(2026-06-16): **이전 라운드(R1~R7) 색강조 복원** — R4 리스크매트릭스 위험배지·셀틴트 등 변환기 색칩약점 회피로 깎인 색강조를 학습8(색배경 div 직속텍스트)로 복원. 그 후 R9~R10. ★종료조건 = 2연속 클린 라운드(신규결함0)면 stop. 현재 클린카운터=0. ★상세 잔여작업·테스트·재현레시피 = 본 핸드오프 §10. ★진행 SSOT = slides/progress.md 상단 헤더 + ckpt-202606161700(R8). ★누적 학습 9개 + 변환기수정(커밋 f61de27). 자율주행(소진 or 2연속클린, ctx750 자동압축, long-mode on2)."
---

# R1 핸드오프 — slides-grab 복잡슬라이드 5장 → 디자인스킬 8테마 재현

> 프로젝트 = `D:/projects/design`. plan = `plan-design-e2e.md` §0.6(25장 SSOT). progress = `slides/progress.md`. 변환기 = `skills/pptx-skill/scripts/html2pptx.cjs`. 룰 = `scripts/validate-pptx.js`(VP) + `scripts/preflight-html.js`(PF).

## 1. 현재 상태 (R1, 소재 5장 = payroll-guide/14·payroll-v2/11·discounted/13·samsung/14·naver/17)
| 테마 | 생성 | convert | ERROR | WARN | COM 의도보존 | 비고 |
|---|---|---|---|---|---|---|
| editorial | ✅ 5장 | ✅ | **0** | 60 | ✅ 5장 직접확인 | 메인 직접생성(Track B serif). 완벽 |
| modern | ✅ 5장 | ✅ | **0** | 120 | ✅ slide-01·05 확인 | 범용토큰 베이스. orange 2.96:1 WARN=advisory(COM 가독양호) |
| company | ✅ 5장 | ✅ | **0** | 120 | ⏳ 미검증 | modern 토큰동일(fallback). data-theme만 치환 |
| classic | ✅ 5장 | ✅ | **0** | 120 | ⏳ 미검증 | accent=cyan. sed 치환 |
| academic | ✅ 5장 | ✅ | **0** | 52 | ⏳ 미검증 | accent=navy blue(#2E75B6, 4.0:1 양호). sed 치환 |
| executive | ✅ 5장 | ✅ | **0** | 2 | ⏳ 미검증 | data-theme=executive-editorial. slide-01 calc만 accent-secondary(orange) 조정 |
| **dark-mono** | ✅ 5장 | ✅ | **88 ❌** | 14 | ❌ XML fail | ★진짜결함(아래 §5). 미수정 |
| dark-pitch | ✅ 5장 | ✅ | **0** | 14 | ⏳ 미검증 | accent=cyan, 다크bg. sed 치환. ERROR0이라 정상예상 |

- **클린카운터 = 0** (2연속 클린 라운드면 종료). R1 dark-mono fix + 나머지 COM 검증 후 라운드 판정.

## 2. ★첫 행동 (재개 시 순서)
1. **dark-mono ERROR 88 fix** (§5 코드레벨 — 디자인수정, 룰 정탐 정확).
2. dark-mono 재변환 → ERROR 0 확인 + COM 검증.
3. company/classic/academic/executive/dark-pitch **COM 렌더 + 의도보존 직접확인**(`scripts/export-slides-png.ps1`, PNG Read).
4. R1 완료 판정 → **회귀게이트**: `git show HEAD:scripts/validate-pptx.js` 기준 GT 17덱 ERROR delta=0 (룰 수정 안 했으면 자동 0) + `tests/regress-generated.sh`.
5. R2 진입 (plan §0.6 R2 5장).

## 3. 사용자 박제 (절대기준 — plan §0.5/§0.6 SSOT)
- 매 라운드 = slides-grab 복잡 5장 **소재 선택** → **디자인스킬 8테마 재현생성**(40장) → convert(PF)→VP→COM 원안보존. ⛔타입발명 금지·⛔slides-grab HTML 직접변환 금지(소재+read-only GT 두 역할).
- K규칙: 룰과탐=게이트수정(⛔등급강등 회피금지)/변환기결함=변환기수정/디자인결함=세트별수정. **정탐회귀0(recall=1.0)·FP0**. COM 직접렌더 판정(추정금지).
- advisory WARN(theme accent 토큰 대비)=워크어라운드 말고 note만(complex-spec 기준). 2연속 신규결함0=종료.

## 4. ★생성 방법 (재현 레시피 — 효율 핵심)
- **산출 형식**: `slides/round{N}-{theme}/slide-01~05.html`. 1280×720px, `<html data-theme>`, `<link ../../design-system/colors_and_type.css>`, om-fit-scaler script, `<body data-layout>`. (참조: `slides/e2e-editorial/slide-01.html` 또는 완성된 `slides/round1-editorial/`)
- **범용 의미토큰만 사용**(8테마 자동 resolve): `--surface-inverse`/`--surface-inverse-fg`(표헤더·계산박스), `--theme-bg`/`--gray-4`(셀·alt행), `--gray-1~3`(본문·약화), `--accent`(강조), `--heading`(제목·라벨 ← ★dark-mono 안전). ⛔theme-bg-card/theme-bg-alt는 4테마만 정의 → 미사용(gray-4로 대체).
- **테마 생성 절차**: modern 5장을 베이스로 `sed 's/data-theme="modern"/data-theme="{theme}"/'` 치환. executive theme값=`executive-editorial`. editorial은 Track B(serif chrome)라 메인 직접생성(범용 sed 아님).
- **테마별 예외**: executive(accent=어두운 navy)는 어두운 surface 위 텍스트만 `accent-secondary`(orange) 사용 — slide-01 calc 합계 1곳. 나머지 navy accent는 white bg 위라 OK.
- 변환: `"/c/Program Files/nodejs/node.exe" scripts/convert-native.mjs --slides-dir slides/round1-{theme} --output slides/round1-{theme}/out.pptx`
- COM: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\projects\design\slides\round1-{theme}\out.pptx" -OutputDir "D:\projects\design\slides\round1-{theme}\png"` → PNG Read(vision) 원안비교.

## 5. ★dark-mono ERROR 88 — root cause + fix (미해결, 첫 작업)
- **증상**: convert 시 VP CONTRAST ERROR 88 + XML validation 43 ERROR. 예: `<h1> "..." #0F1419 on #0F1419 (1.00:1)`, `<p> "산재" #0F1419 on #1F2937 (1.26:1)`.
- **root cause**: 범용 구조가 텍스트 color에 `var(--primary)` 사용. dark-mono 토큰은 `--primary:#0F1419` == `--theme-bg:#0F1419` (동일) → 제목·이름·강조 텍스트가 배경과 1.00:1 → **안 보임**. dark-mono는 별도 `--heading:#E5E7EB` 정의("primary==bg, titles must use --heading, never --primary directly" — colors_and_type.css:318-320 주석). 내 마크업이 이 규약 위반.
- **판정**: VP-04 = 1.00:1 정확 측정 = **정탐(과탐 아님)**. 룰 수정 ❌. **디자인 결함**(마크업) → 세트별 수정.
- **fix(코드레벨)**: 텍스트 `color:var(--primary)` → `color:var(--heading, var(--primary))`. dark-mono는 #E5E7EB resolve, 타 테마는 --heading 미정의→fallback=primary(무영향). 영향 위치 = h1/.td.name p/.td.item p/.td.cum p/.c-lb p/.ctitle/.chip p/.chart-title/.blbl/.td.lb p (전부 텍스트색 primary).
- **적용 절차**(권장): `slides/round1-modern/*.html`에서 `color:var(--primary)` → `color:var(--heading, var(--primary))` 일괄치환(sed) → 6테마(company/classic/academic/executive/dark-mono/dark-pitch) sed 재생성(executive calc 재조정) + editorial도 동일 패턴 반영 → 전 테마 재변환. ⛔ bg/border용 surface-inverse·accent는 건드리지 말 것(텍스트 color만).
- **검증**: dark-mono 재변환 ERROR=0 + COM에서 밝은 텍스트 on 다크 확인.

## 6. WARN 분류 (advisory 수용 — ERROR 아님)
- 전 테마 CONTRAST WARN = accent 토큰 고유 대비(editorial terracotta 4.07:1, modern/company orange 2.96:1, classic cyan ~2.6:1). design-system이 정의한 accent를 강조에 사용 → WCAG 수치 미달이나 **COM 실렌더 가독성 양호(17~18px bold)**. complex-spec 기준 = theme accent WARN은 note만. 단 accent를 데이터 다수강조에 쓰면 WARN 폭증(modern 120) — 디자인 가이드("accent=single highlight per slide")와 절충점이나 원안 충실(원안도 강조컬럼 다수) 우선. ERROR 아니므로 수용.
- CLAMP 경고(head/source element 폭 9.44" 초과 자동보정) = 무해(COM 시각 정상).

## 7. 미사용/자문
- 외부 자문 미사용. 전 판정 COM 직접렌더 근거.
- harness2 teammate 미사용(이번 R1). 직전 2세션 teammate 병렬이 타입발명 드리프트로 낭비 → 메인 직접생성으로 전환(드리프트0·토큰통제). 범용 sed 방식으로 테마당 생성비용 최소화.

## 8. R2 완료 + 누적 학습 (2026-06-16, 핵심 — R3 진입 전 필독)
- **R1·R2 상태**: 둘 다 8테마 convert ERROR0 + COM 의도보존 + 정탐회귀0(룰/변환기 git diff=0). 디렉토리 `slides/round{1,2}-{theme}/`. R2 소재=payroll-guide/04(VS양패널)·payroll-v2/07(4열10행표)·kakao/07(5열컬러도트매트릭스)·payroll-guide/12(투패널KPI)·lg-hynix/09(투패널타임라인).
- **클린카운터=0**: R1(dark-mono결함)·R2(결함2건) 모두 신규결함 라운드. 2연속 무결함=종료. R3·R4 무결함 필요.
- **★학습된 토큰 함정 3개 (R3+ 생성 시 처음부터 적용 = 결함 예방)**:
  1. **dark-mono primary==bg**: 텍스트색은 `var(--heading, var(--primary))` (절대 raw `var(--primary)` 금지). dark-mono는 #E5E7EB resolve.
  2. **어두운 surface(surface-inverse) 위 강조**: 색강조 금지(`accent`/`accent-secondary` 둘 다 함정 — executive navy accent==ink, academic accent-secondary #1F4E79==surface-inverse #1F4E79 동색). → `var(--surface-inverse-fg)` 흰색 + 크기/굵기로 강조. accent **bg**(badge·태그·VS원) 위 흰글씨는 OK.
  3. **태그/배지 텍스트 wrap**: `.tag` div + 내부 `p` **둘 다** `white-space:nowrap` + 텍스트 짧게(긴 라벨은 단축). div에만 nowrap 주면 자식 p에서 wrap됨.
  4. **복합내용 셀 = 표 패턴 강제 (R4 학습)**: 셀 안에 배지+제목+설명 등 여러 요소를 넣을 때 `cell > flex-column div > 여러 p` 중첩은 변환기 table-column snap 후처리가 단일복합자식 셀의 p들을 같은 Y에 겹쳐 배치(특히 자식 1개 셀). → **셀 = 단일 p 멀티라인(`<br>`) + 부분강조 `<span>` 색** 패턴으로(표 셀처럼 = 단일 텍스트박스 = 변환기 100% 안전). 매트릭스/카드 류에 적용.
  - 상태색(green/amber/red 등 데이터 의미색)=solid hex 고정(#16A34A/#F59E0B/#DC2626), 테마토큰 아님.
  - ★변환기 결함 진단 단서: 같은 슬라이드 내 일부 셀 정상·일부 겹침 = 셀 구조 차이(자식 개수)면 변환기 후처리 edge case. 전역 변환기 수정(회귀위험) 대신 표 셀 패턴 우회 우선.
- **생성 레시피(검증됨)**: modern 범용토큰 베이스 5장 직접작성 → `sed 's/data-theme="modern"/data-theme="{theme}"/'` 6테마(company/classic/academic/dark-mono/dark-pitch/executive=executive-editorial) → editorial은 modern sed + serif 주입(`* {...}` 다음 줄에 `h1,h2,h3,.sn,.tt,.kicker,.vsc p { font-family:'Newsreader','Times New Roman',serif; }`). **3개 함정 처음부터 반영하면 sed 후 전테마 ERROR0**.
- **변환/COM**: `"$NODE" scripts/convert-native.mjs --slides-dir slides/round{N}-{theme} --output .../out.pptx` (★preflight 포함 — `--skip-preflight` 금지: 자동보정 빠져 ERROR 오탐). COM=`export-slides-png.ps1` → png/slide_NN.png Read.
- **ERROR 집계 정확히**: grep `CONTRAST ERROR|❌ ERROR` + `invisible-text ERROR` + `XML validation found N ERROR` 3형식 모두 카운트(`❌ ERROR`만 보면 invisible-text 놓침).
- **회귀게이트 주의**: `tests/regress-generated.sh`는 구 드리프트 산출물(e2e2/3/4-*) 스캔=무관. GT 17덱 회귀는 preflight 포함 변환으로 측정(baseline `tests/detection-regression/full-baseline.json` 17덱 전부 ERROR0 기준).
- **미세 개선여지(결함 아님)**: 투패널 slide-04 우측 하단 여백(세로공간). R3+ 레이아웃 개선 메모.

## 9. R5·R6 추가 학습 (2026-06-16, 자율주행) — 누적 토큰/변환기 함정 6개
- **R1~R6 완료**(각 8테마 ERROR0+COM+정탐회귀0). 클린카운터=0(R3만 첫클린, R4~R6 각 결함발생). 2연속클린 미달. R7~R10 + 누적학습으로 진행중. 자율주행(소진 or 2연속클린까지, ctx750 자동압축). long-mode on2.
- **★누적 학습 6개 (R7+ 생성 시 처음부터 적용 = 결함 예방)**:
  1. **dark-mono primary==bg**: 텍스트색 `var(--heading, var(--primary))` (raw primary 금지).
  2. **어두운 surface 위 강조**: `var(--surface-inverse-fg)` (accent/accent-secondary 둘다 함정 — executive navy==ink, academic accent-secondary #1F4E79==surface-inverse). 크기/굵기로 강조.
  3. **긴 텍스트 wrap**: `.x p { white-space:nowrap }` (div+p 둘다), 텍스트 짧게.
  4. **복합내용 셀**: 표 패턴(셀=단일 p 멀티라인 `<br>` + span 색). 중첩 flex 칩(cell>div>여러p) = 변환기 table-column snap이 단일복합자식 셀 p 겹침.
  5. **연한 톤 bg 고정hex 금지**: #EAF7EF 류 light가정 연한색 → 다크테마 밝은텍스트와 1.1:1 충돌. 행/셀 강조 bg는 테마토큰(gray-4), 강조는 텍스트 의미색.
  6. **배지/태그 = `<div class="badge"><p>텍스트</p></div>` + nowrap**: `<span class="badge">텍스트</span>` span직접은 변환기가 배경 미렌더(idiomatic "배경은 div만") + wrap. 데이터 의미색(green/amber/red)은 solid hex bg + 흰글씨 p.
- **★소재 선정 함정**: subagent grep(grid/flex밀도)이 목차/intro/표지를 "복잡"으로 오판 → 각 라운드 진입 시 소재 Read로 "복잡 데이터슬라이드(표/차트/매트릭스)"인지 재확인, 단순(목차/Why/개요/이미지+불릿)이면 plan §0.6 미사용 복잡슬라이드로 교체. R6 posco/03(목차)·manuf-kpi/02(intro) 교체함. ★R6-2=posco/07 교체로 R7-2와 중복발생→R7-2=posco/12로 해소(plan 반영).
- **R7~R10 소재**(plan §0.6): R7 payroll-v2/28·posco/12·naver/15·payroll-v2/31·payroll-guide/17 / R8 manuf/03·payroll-v2/14·payroll-guide/19·34·13 / R9 payroll-v2/02·coupang/09·payroll-guide/30·11·32 / R10 payroll-v2/30·payroll-guide/09·41·samsung/06·discounted/11. 각 진입 시 복잡도 Read 재확인.

### §9 추가 (R7, 2026-06-16) — 학습 7번째
  7. **행 많은 표 = 720pt 초과 주의**: HTML이 720pt(슬라이드 높이)를 초과하면 변환기가 `FAILED ... overflows body` + **슬라이드 silent omit**(pptx에 그 slideN.xml 누락). ★CONTRAST/invisible/XML ERROR 0이라 일반 집계가 못잡음 → COM에서 0byte(빈) PNG로만 발견. **변환 ERROR 집계 = `grep -cE "CONTRAST ERROR|❌ ERROR"` + invisible-text + XML + `grep -cE "FAILED|failed to convert"` 4형식 필수**. 행 많은 표는 head margin/padding + td padding 축소로 720 내 맞춤(R7 slide-05 12행표 7.5pt 초과→축소).
- **R3·R7 = 누적학습 선적용으로 첫시도 클린에 근접**(R7은 slide-05 720초과 1건만). R8+ 7학습 처음부터 적용.

---

## §10. R8 완료 + 변환기 수정 + 잔여 작업·테스트 (2026-06-16, 압축내성 완결)

### 10.1 R8 완료 지점
- **R8 소재**: manuf-kpi/03(PQCD 4카드)·payroll-v2/14(6열표)·payroll-guide/19(BEFORE/AFTER+영향표)·34(9행캘린더)·13(요율표+calc). 8테마 ERROR0+FAIL0+COM의도보존+정탐회귀0. 커밋 **f61de27**.
- **COM 확인 완료**: modern slide-01/02/05, dark-mono slide-01(다크 색아이콘 대비 우수). 나머지 6테마 = sed 동일구조 + 전체 ERROR0.

### 10.2 ★이번 세션 핵심 — 변환기 수정 + 학습8/9 (재발 방지 박제)
- **학습8 (색배경 칩 invisible)**: 색배경 div 안에 자식 `<p>`(textTags)를 넣으면 변환기가 배경shape와 텍스트를 **분리** → p텍스트 origW가 전체폭(body content)으로 측정 → snap 실패(`origW > col.w×1.5`) → 배경과 어긋나 invisible(`#FFF on #FFF`). **해결: 색배경 칩/아이콘은 자식 `<p>` 없이 div 직속 텍스트** = `<div class="ic-p">P</div>` (leaf-div+bg = shape with embedded text, 분리 안 일어남). ⛔자식 `<p>`/`<span>` 금지.
- **학습9 (카드 불릿 겹침/누락)**: `.item` flex(dot span + p)는 변환기 column-snap이 여러 p를 한 위치로 묶어 겹침/누락. **단일 `<p>`+inline `<b>`불릿** 또는 `<br>` 멀티라인으로 통합.
- **★변환기 수정 (html2pptx.cjs line631-632, 커밋 f61de27)**: `tableColumns` 필터에 정사각 작은 shape 제외 추가 — `c.w < 1.2"(인치) && Math.abs(c.w-avgH) < max(c.w,avgH)*0.35` 면 confirmed column에서 제외. 2×2 색아이콘이 같은 X·2Y라 table-column 오인 → 그 Y범위 카드 본문 텍스트가 snap돼 겹치던 버그(학습4 동류) 해결.
- **정탐회귀 0 검증 (필수·완료)**: GT 17덱(slides-grab) 재변환+VP → 전부 VP-ERROR=0(baseline 동일). samsung FAIL=1슬라이드(slide-15 18pt overflow)는 GT 원본 고유 — git stash 대조로 수정 전후 동일 확인 = 회귀 아님.

### 10.3 ★잔여 작업 (우선순위 순)
**(A) 이전 라운드 색강조 복원 [사용자 1번 선택, 최우선]**
- **왜**: 사용자 2지적(2026-06-16) — "PF/VP 맞게 깎지말고 디자인 의도 구현도 목표" + "이전 세션 수정 원안 크게 헤치는지 전수검토". 전수검토 결과 = 레이아웃·정보는 보존됐으나 **색 시각강조가 변환기 색칩약점 회피로 텍스트색/토큰으로 약화**됨.
- **대상 (전수검토로 식별)**: ★R4 slide-04 리스크매트릭스 = 원안(samsung/16)의 위험도 셀틴트(high=주황#FFF3E0/med=파랑#F0F4FF/low=회색)·위험배지(critical 주황#FF6F00 칩·moderate 파랑#1428A0 칩 흰글씨) → 현재 `var(--theme-bg)` 단색 + 색텍스트(.crit{color:accent})로 강등. R5/R6 등도 grep지표상 색배경칩 감소(R5=0개, R7=0개 — 원안 색배경 6~7개 대비).
- **방법**: 학습8 패턴(색배경 div 직속텍스트)으로 위험배지·셀틴트 색칩 복원. 변환기 수정으로 이제 정사각/소형 색칩도 변환 안전. 단 색칩 흰글씨는 ⛔자식`<p>` 금지(div 직속텍스트). 각 복원 후 변환 ERROR0 + COM 의도보존 재확인.
- **범위**: R4 우선(가장 명확한 약화), 이후 R5/R6 색강조 점검. R1~R3/R7은 표 위주라 색강조 약화 적음(grep R2=3·R3=6·R6=5 일부 유지).
- **⚠️ 주의**: 복원은 "원안 색강조 되살리기"지 새 디자인 발명 아님. 원안 slides-grab HTML의 색배경/배지를 레퍼런스로.

**(B) R9 진행** (소재 = plan §0.6): payroll-v2/02·coupang/09·payroll-guide/30·11·32. 테스트절차 5단(plan §0.6). 처음부터 학습8/9 적용.
**(C) R10 진행**: payroll-v2/30·payroll-guide/09·41·samsung/06·discounted/11.

### 10.4 ★잔여 테스트 (종료 조건)
- **테스트 = 매 라운드 5단 절차**(plan §0.6): ①소재 Read ②design-system 8테마 재현생성(modern 베이스→sed 6테마+editorial serif) ③PF포함 변환(convert-native.mjs) ④VP+COM 의도보존 ⑤K규칙·정탐회귀0.
- **★종료 조건 = 2연속 클린 라운드**(신규 결함0 = 변환기버그·디자인결함 발견 없음). **현재 클린카운터=0**(R8에서 학습8/9+변환기수정 신규결함 발견·수정 = 클린 아님).
- **2r 성공 시 stop**. 그 전까지 R9·R10(+소재 소진 시 추가 선정 or 사용자 지시) 계속. 색강조 복원(A)은 라운드 클린 판정과 별개(이미 완료된 R1~R7 보강).
- **클린 판정 주의**: 변환기/룰 수정 0 + 디자인결함 0 인 라운드만 클린. 색칩/불릿 패턴은 이제 학습8/9로 처음부터 적용 → 신규결함 안 나면 클린.

### 10.5 재현 레시피 (환경·도구)
- **NODE**: `/c/Program Files/nodejs/node.exe`
- **변환(PF포함)**: `"$NODE" scripts/convert-native.mjs --slides-dir slides/round{N}-{theme} --output slides/round{N}-{theme}/out.pptx` (⛔`--skip-preflight` 금지=오탐)
- **COM 렌더**: `powershell.exe -ExecutionPolicy Bypass -File scripts/export-slides-png.ps1 -PptxPath "D:\...\out.pptx" -OutputDir "D:\...\png"` → PNG = `slide_NN.png` (4000×2250, Read 전 1400px resize 필수: System.Drawing)
- **ERROR 4형식 집계**: `XML validation found N ERROR` + `CONTRAST/❌/invisible-text ERROR` + `FAILED|failed to convert|omitted` + 0byte PNG.
- **정탐회귀 검증**: GT 17덱(slides-grab/slides/{ai-infra-investment,coupang-investment-report,...17덱}) 재변환+VP → VP-ERROR=0 확인. baseline = `tests/detection-regression/full-baseline.json`. ⛔변환기/룰 수정 시 필수.
- **테마 생성**: modern 베이스 작성 → `sed 's/data-theme="modern"/data-theme="{theme}"/'` 6테마(company/classic/academic/executive=executive-editorial/dark-mono/dark-pitch) + editorial(sed + serif 라인 `.serif-head,h1,h2,h3,h4,h5,.ctitle,.kicker{font-family:'Newsreader',serif}` 삽입).

### 10.6 미해결·실패 삽질 방지
- **⛔ invisible 디버깅 9회 삽질 교훈**: 색칩 invisible은 추정 falsify(복합클래스/flex/text-align/px 등) 9회 실패. **변환 XML 직독**(unzip slide1.xml → spPr noFill + ext cx 측정)으로 빨리 근본(텍스트 전체폭 + snap W_RATIO) 짚었어야. 다음에 변환 이상 = XML 직독 우선.
- **⛔ 표로 깎기 금지**: invisible 회피하려 PQCD를 표로 단순화한 건 사용자 의도(2×2 카드) 위반. 변환기 결함은 변환기 수정/근본진단으로, 디자인 깎기 X.
