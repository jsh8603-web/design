---
title: 변환기 버그 채굴 stress-loop 핸드오프 — 방식·무드리프트·8테마 의무
tags: [handoff, design-e2e, stress-loop, converter-bug-mining, btn-design]
date: 2026-06-19
next-action: "★8테마 균등 2사이클 완료(c5 8/8 + c6 8/8 = 16장 전부 변환 정상). ★엔진 결함 2종 근본 fix 완료(widthIncrease 단위 + X-collapse 전폭tableColumn, 둘 다 GT 회귀0). 다음 세션 = ①c7 8테마 3회차(신규 차트 차원: 스택영역/슬로프/레이더/불릿/네트워크/박스플롯 등 ×8테마)로 회귀+신규결함 사냥, 또는 ②slide-08 2단 X-collapse가 새 fix와 다른 원인인지 [XTC] step디버그 확인. 방식 §2. 무드리프트 §3. SSOT = GENERATOR-CONTRACT.md + slides/stress-loop-state.md(c5·c6 원장)."
---

# 변환기 버그 채굴 stress-loop 핸드오프 (2026-06-19, btn-design)

## §1 현재 상태 · 첫 행동
- **목표**(사용자): 생성기를 고쳐 "한번에 제대로 변환"(PF+VP 통과), **디자인 의도 절대 드리프트 0**, 버그 단시간 대량 채굴. 단 PF/VP가 정말 틀렸으면 고침.
- **달성**: first-try-clean **0/10 → 9/10** 입증. 무한 루프 **수렴**(2연속 클린: 사이클2·3). 40 stress 차원(c1~c4) 검증. 회귀0·드리프트0.
- **★8테마 갭 = 사이클5서 해소(2026-06-19)**: 8테마 균등 1장씩(c5 slide-01~08) 생성·변환·vision → **8/8 클린**. 테마특화 결함 7종(serif폴백 PF-19/opacity PF-42/다크footnote PF-71/fr분할 A12/navy대비 A10/conic-gradient PF-62/span-bg PF-55) + 엔진결함 1종(widthIncrease 단위) 수확·수정. 계약 A2·A12·A17·A18·A19 갱신.
- **★엔진 fix 채택(c5)**: `html2pptx.cjs` L510 widthIncrease 가 `isSingleLine`(L472 inch/pt 단위버그로 거의 항상 true) 의존 → multi-line CJK 가 widthIncrease 적용받아 2단 좁은컬럼서 인접침범. fix=widthIncrease만 올바른 단위로 multi-line 재판정. **GT 17덱 회귀 delta=0 검증(stash 비교)**. 상세 = stress-loop-state.md "c5 editorial 엔진결함 추적".
- **★다음 첫 행동**: §5 의 **2단+quote-wrap X-collapse deep-debug**(slide-08 단일컬럼 회피만, 근본 미해결) 또는 c6 8테마 2회차.

## §2 내가 쓴 방식 (정확히 — 이대로 재현)
1. **계약 SSOT 선행**: `GENERATOR-CONTRACT.md`(루트) — 학습16+idiomatic6 통합 A0~A16 하드규칙. ⛔design-system/ 안 두고 루트(§3 동결 준수). 새 결함 발견 시 여기에 A항 추가.
2. **병렬 생성**: 차원당 `general-purpose` 서브에이전트 1개, 한 번에 8~10 동시 스폰. 각 에이전트 = `GENERATOR-CONTRACT.md` §A0 envelope verbatim + §A 전 규칙 준수 + 1 stress 차원 극단 + 실제 한국 FP&A 더미 + 1280×720 fit. `slides/stress-cN/slide-NN.html` 작성, JSON 1줄 반환. ⛔에이전트는 preflight/convert/타파일/하위스폰 금지(생성만).
3. **중앙 직렬 검증**(메인이): preflight `--full` → `convert-native.mjs`(PF 포함) → `export-slides-png.ps1`(COM 렌더, **단일 인스턴스라 직렬**) → PNG **1600px 리사이즈**(4000px=many-image 한도 초과, System.Drawing) → Read(vision).
4. **triage 2축**(생성기>변환기>룰, §C): 룰오발→preflight수정(회귀0) / 진짜변환문제 → 시각동일 안전마크업 있으면 **계약수정(생성기회피)** / 없으면 **변환기수정**(GT회귀0). 디자인 깎기 최후.
5. **수정 = 살아있는 에이전트 SendMessage**(agentId, 컨텍스트 보존) 또는 메인 직접. 재변환·재렌더·재vision으로 검증.
6. **사이클 기록**: `slides/stress-loop-state.md`에 매 단계 append(압축 내성). 종료 = 2연속 신규 변환기버그 0.

## §3 사용자 박제 (대화 고유 — 절대 준수)
1. **⛔절대 드리프트 0**: `design-system/` 토큰·테마·레이아웃·규칙 수정 = 드리프트. **허용 = scripts/·html2pptx·preflight/validate·slides/산출물·루트계약문서**뿐. design-system 수정 필요 시 **사용자 승인 필수**(이번 `.t-*` vendored = 승인받음).
2. **★8개 디자인 세트(테마) 고르게 사용**(사용자 2026-06-19 지시): modern/classic/dark-mono/company/executive-editorial/dark-pitch/academic/editorial 8테마 균등. **내가 modern만 써서 못 지킨 부분 = 다음 세션 의무 정정.** 단일 테마 편중 금지.
3. **생성기 우선 수정**: 시각동일 안전 마크업으로 회피 가능하면 생성기(계약). 정당한 시맨틱 태그(blockquote 등)가 깨지면 변환기 엔진 수정. 룰 미세조정은 GT 17덱 회귀0 게이트.
4. **stress 슬라이드 = 일회용 테스트 픽스처**(slides/stress-cN/). 기존 디자인 자산 아님 → 자유 재작성 OK(드리프트 아님). round* 자산은 불가침.
5. **멈추지 말고 토큰 태워라**(사용자): 수렴 후에도 보너스 사냥 계속. 서브에이전트 대량 투입.

## §4 파일 inventory (절대경로)
- **계약 SSOT**: `D:/projects/design/GENERATOR-CONTRACT.md` (A0~A16, §C triage, §D 드리프트게이트, §E stress차원)
- **사이클 원장**: `D:/projects/design/slides/stress-loop-state.md` (c1~c4 전 발견·수정 기록)
- **코드 변경 3개**(이것만 손댐):
  - `scripts/preflight-html.js`: `stripComments`(주석-FP 클래스 수정, L1508 근처) + `PF-76`(대각화살표 char-scan, runStaticChecks 등록)
  - `skills/pptx-skill/scripts/html2pptx.cjs`: (1) blockquote/textTag double-emit 가드(L~1615). (2) **c5: widthIncrease multi-line 단위 fix(L~510)** — isSingleLine inch/pt 단위버그 우회, multi-line=minWidthIncrease(2단 CJK 인접침범 차단). (3) **★c6: X-collapse fix(L653)** — tableColumns 필터에 `c.w > 7.0` 제외(전폭 shape가 가짜 tableColumn 되어 텍스트 전부 col.x snap하는 결함 차단). **둘 다 GT 17덱 회귀 delta=0**(baseline 5 ERROR 불변). convert-native가 require하는 파일(L18).
  - `design-system/colors_and_type.css`: `.t-body-compact`(--pt-body-compact:16pt)·`.t-chart-label`(--pt-chart-label:10pt mono) 추가(사용자 승인). 기존 8 .t-* 무변경.
- **stress 산출**: `slides/stress-c1~c4/slide-*.html` + `png/*.png`+`*_sm.png`. probe: `slides/probe/slide-01.html`(트리거 격리 실험).
- **변환 도구**: NODE=`/c/Program Files/nodejs/node.exe`. `scripts/convert-native.mjs`(PF포함) / `scripts/export-slides-png.ps1`(COM) / `tests/regress-generated.sh`(GT 회귀).
- **기존 핸드오프**(round 워크플로): `slides/handoff-design-e2e-20260616.md`(8테마 sed-propagate 방식 §5).

## §5 미해결 · 실패한 시도 (삽질 방지)
- **✅8테마 균등 = c5서 완료**(8/8 클린, §1 참조). 더 이상 갭 아님.
- **★★2단 X-collapse 엔진버그 (c5 미해결, 다음 deep-debug) — repro A~G 7개 격리, trigger 4중조합으로 좁힘**: editorial 좌우2단서 우측 col 텍스트가 좌측 X(457200 EMU)로 collapse→겹침. **probe-c5/ 격리(전부 우측 x=4529138 정상 확인)**: A(단일)·B(2단순수,widthIncrease fix후)·C(좌shape+우순수)·D(우깊은중첩)·E(D+span)·F(E+divider)·G(좌quote-wrap+prose AND 우깊은중첩) **전부 정상**. 단일·2·3 조합 다 무죄. repro-H(slide-08 2단 정확 재현)도 정상 → repro A~H 8개 전부 정상(2~3요소). ★**c6 slide-02가 X-collapse 강력 재현**: 워터폴 라벨을 절대배치→flex-row(.axisrow **6칸** 균등)로 회피해도 **6칸이 중앙으로 X-collapse**(7회 회피 실패). ★★결정적 단서 = **repro-B(flex 2칸)=정상 vs slide-02(flex 6칸)=collapse** → **flex-row 칸 수(≥N)가 트리거 변수** = c5 repro가 2~3요소라 못 잡은 이유 설명. 
  - ★**step 디버그로 근본 원인 확정 + 엔진 fix 완료(2026-06-19)**: [XDBG] rect.left 정확(58~838px 균등) + [XDBG2] push시 toX 정상(0.28~6.48") 인데 PPTX x 전부 414338(0.45" 첫칸) collapse → [XTC] 범인 = **column-norm phase2(L677)가 전폭(9.09") gridline shape를 가짜 tableColumn으로 오판** → axisrow 텍스트 전부 col.x=0.45로 snap(L698). **fix = tableColumns 필터(L653)에 `c.w > 7.0` 제외**(전폭=격자선/배경, 셀 아님). **slide-02 완전해소✅ + GT 17덱 회귀 delta=0✅**. slide-08 2단은 전폭 shape 없어 다른 원인 가능성(단일컬럼 회피 유지, 재현 시 [XTC] 로그 적용). slide-08은 단일컬럼(repro-A)으로 회피 정리(픽스처 OK). blockquote/figcaption textTag 변환 자체는 repro-A서 정상=stress 목적 달성.
- **c4 잔여 vision 미완**: c4 slide-04밀집표·05다국어·06폰트웨이트·07장문·09kitchen-sink 5장 vision 안 봄(변환은 10/10 성공). png `slides/stress-c4/png/slide_NN_sm.png`(재변환 후 매핑 = png_NN=slide-NN, 02/03도 이제 변환됨). **slide_06(c4 dim8 deep5-nested) 헤더영역 겹침 의심**(1600px 불명확)=풀해상도 Read 재확인 필요.
- **삽질 회피**: (a) COM 렌더 PNG는 4000px=many-image 한도 → **1600px 리사이즈 필수**(System.Drawing 1-liner, stress-loop-state에 코드). (b) 에이전트 생성 시 §A0 envelope 누락=body 붕괴 FAILED → 프롬프트에 "verbatim" 강조. (c) flex 컨테이너 직속텍스트노드=garble → A9(`<div><p>`). (d) 선두 bullet글리프(`●○◆`)=변환거부(html2pptx.cjs:1620)→A15. (e) GT 회귀는 베이스라인 측정(git stash로 원본 비교) 후 delta 판정.
- **변환기 정상 확인된 구조**(재의심 말 것): 비교매트릭스·도넛·히트맵·간트·버블(절대배치)·조직도·워터폴·게이지·깔때기·빅넘버·회전텍스트(-45°)·중첩그리드·stacked-bar·진행바·sparkline·다국어인라인·blockquote(수정후) — 전부 modern서 변환 정상. **단 8테마서 재검증 필요**.

## §6 자문 종합
- 외부 AI 자문 미사용(자체 probe 실험으로 트리거 격리 = 경험적 검증으로 충분). 강제 트리거 해당 없음(설계 확정·dispute 없었음).
- 핵심 통찰 = **A0 envelope 갭**(§9 스켈레톤이 body사이징+om-fit-scaler 누락 → modern 외 모든 생성 실패의 지배 원인). 이게 "한번에 제대로 변환"의 최대 레버리지였음.
