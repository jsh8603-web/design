# progress — 디자인시스템 8테마 e2e (btn-design)

## ★SSOT 헤더 (오해 방지 — 테스트 자산·방법·진행)
- **테스트 자산** = `slides/round{N}-{theme}/slide-01~05.html` (N=1~10 라운드, theme=editorial·modern·executive(executive-editorial)·academic·classic·dark-mono·company·dark-pitch). 라운드당 40장, 총 400장. ⛔slides-grab 소재는 레퍼런스+read-only GT일 뿐 변환대상 아님 — **변환·검증 대상 = round{N}-{theme} 산출물**.
- **테스트 방법** = [plan §0.6 "테스트 절차 5단"](../plan-design-e2e.md): ①소재 5장 Read(복잡도 재확인, 단순=목차/intro면 교체) ②design-system 8테마 재현 생성(modern 범용토큰 베이스 → sed 6테마 + editorial serif, 누적 학습 선적용) ③PF포함 변환(`convert-native.mjs`) ④VP + COM(`export-slides-png.ps1` → PNG Read 의도보존) ⑤K규칙·정탐회귀0. **변환 ERROR 집계 = C(CONTRAST)/inv(invisible-text)/xml(XML validation)/FAILED(720초과 omit) 4형식 모두 grep**.
- **종료 조건** = 2연속 라운드 신규결함0(클린). 라운드에서 결함 발견·수정 시 그 라운드는 클린 아님.
- **소재 SSOT** = plan §0.6 표(R1~R10 50장). **완료자산 등록** = `slides/RENDERED-ASSETS-INDEX.md`.
- **현재(2026-06-16)**: R1~R7 완료(8테마 ERROR0+COM의도보존+정탐회귀0). **클린카운터=0**(R3만 첫시도클린, R4~R7 각 결함발견·수정). R8 대기. **누적 학습 7개**=handoff §9 / 아래 R7 ckpt. 자율주행(소진 or 2연속클린까지, ctx750 자동압축, long-mode on2).
- **정탐회귀** = 룰(`validate-pptx.js`)/변환기(`html2pptx.cjs`) 무수정 시 자동 0(7라운드 내내 git diff=0). 회귀 측정 시 ★preflight 포함 변환 필수(`--skip-preflight`는 자동보정 빠져 오탐).

---

## Working Notes — ckpt-202606161103 (btn-design, R1 거의완료)
- **dark-mono fix 완료**: 텍스트 `color:var(--primary)`→`color:var(--heading, var(--primary))` 일괄치환(modern 베이스 13곳) → ERROR 88→**0**. COM 검증=다크bg 밝은텍스트 선명. 룰 무수정(정탐 정확, 디자인수정).
- **R1 8테마 전부 ERROR 0 + COM 의도보존 확인**: editorial/modern/dark-mono/executive(navy)/academic(blue)/classic(cyan)/dark-pitch(다크cyan)/company(orange). 전 테마 XML/PF 통과.
- **정탐회귀 0 확정 ✅**: 룰/변환기 git diff=0(구조적 보장). GT 17덱 전부 정상파이프라인(preflight 포함) ERROR=0. ★주의: `--skip-preflight`로 변환하면 preflight 자동보정(동일색 텍스트→가독색)이 빠져 VP-04 ERROR 오탐(manufacturing-kpi 5·sailing-ships 4·lg-hynix 2·noah 2 = 측정아티팩트, 회귀 아님). **회귀 측정 시 반드시 preflight 포함 변환**.
- **regress-generated.sh 한계**: GT 아니라 이전 드리프트 산출물(e2e2/e2e3/e2e4-*) 스캔 → 그 산출물 자체결함 ERROR5(VP-04 cyan-on-cyan·VP-07 빈셀, 진짜정탐, 이번세션 무관). e2e2/3/4=드리프트 라운드(폐기대상). **게이트 baseline 재정의 필요**(round1-* 포함, 드리프트 제외 + preflight 포함) = 사용자 확인사항.
- **R1 완료**: 8테마 ERROR0 + COM의도보존 + 정탐회귀0 + FP0. 클린카운터 = 0 유지(R1에서 dark-mono 신규결함 발견·수정 = 클린라운드 아님). R2가 클린이면 1, R3 클린이면 2→종료.
- **STATUS**: resolved (2026-06-16 R1 완료)

## Working Notes — ckpt-202606161145 (btn-design, R2 진행)
- **R2 소재 5장**: payroll-guide/04(VS양패널), payroll-v2/07(4열10행표), kakao/07(5열컬러도트매트릭스), payroll-guide/12(투패널 KPI+세분류표), lg-hynix/09(투패널 타임라인).
- **R2 생성 완료**: 8테마 전부 convert ERROR 0 (CONTRAST/invisible/XML 모두 0). modern 범용토큰 베이스 → sed 6테마 → editorial serif 파생. 디렉토리 `slides/round2-{theme}/`.
- **R2에서 배운 토큰 함정**: ★`var(--accent-secondary, var(--accent))`로 "어두운 surface 위 강조" 하려 했으나 **academic은 accent-secondary(#1F4E79)==surface-inverse(#1F4E79) 동일색** → 1.00:1 invisible ERROR 4개. 해법=어두운 surface 위 강조는 색 대신 `var(--surface-inverse-fg)`(흰색 전테마안전)+크기/굵기. (R1 dark-mono와 다른 신규 함정. heading fallback과 별개.)
- **상태색**: kakao 매트릭스 green/amber/red = 데이터 의미색이라 solid hex 고정(#16A34A/#F59E0B/#DC2626), 테마토큰 아님.
- **R2 완료**: 8테마 convert ERROR0 + COM 의도보존 확인(modern/company/classic/academic/executive/editorial/dark-mono/dark-pitch). 정탐회귀0(룰/변환기 git diff=0). 결함 2건 발견·수정 = academic accent-secondary 동색(→surface-inverse-fg), slide-01 태그 wrap(→.tag p nowrap+텍스트단축 "공제 후 정산").
- **클린카운터 = 0 유지**: R1(dark-mono결함)·R2(결함2건) 모두 신규결함 발생 라운드 = 클린 아님. R3 무결함이면 1, R4 무결함이면 2→종료. ★매 라운드 새 레이아웃이라 토큰함정/wrap 미세결함 반복 경향 — 누적 학습(heading fallback·surface-inverse-fg 강조·tag nowrap)으로 R3+ 결함 감소 기대.
- **미세 개선여지(결함 아님)**: 투패널 slide-04 우측 하단 여백(1280×720 세로공간, 콘텐츠 위쪽정렬). ERROR 아님·가독성 정상. R3+ 레이아웃 개선 메모.
- **STATUS**: resolved (2026-06-16 R2 완료)

## Working Notes — ckpt-202606161230 (btn-design, R3 거의완료)
- **R3 소재 5장**: payroll-guide/06(프로세스흐름+KPI5카드)·payroll-guide/08(navy패널+3KPI+3detail박스)·discounted/18(토네이도차트+시나리오)·payroll-guide/10(navy패널+워터폴+결과)·coupang/08(metric6그리드+우선순위).
- **★R3 = 첫 클린 라운드**: 8테마 convert ERROR0 **첫 시도**(R1·R2와 달리 결함0). 학습된 토큰함정 3개(heading fallback·surface-inverse-fg 강조·tag nowrap) 처음부터 선적용 효과. 디렉토리 `slides/round3-{theme}/`.
- **COM 의도보존 확인**: 토네이도(flex 좌우발산 base중앙선 ✅)·워터폴(누적바차트 navy→orange 결과박스 ✅)·프로세스흐름(분기 YES green/NO orange ✅)·dark-mono navy패널(다크 흰텍스트/배지 선명 ✅). **slide_05 metric그리드 시각확인 1건 남음**(이미지 누적제한으로 다음 turn).
- **정탐회귀0**: 룰/변환기 git diff=0.
- **클린카운터: 0 → 1** (R3 첫클린). R4 무결함이면 2 → **종료**. R4가 마지막 관문.
- **R3 확정**: slide_05 metric그리드 COM 확인 완료(modern 현금highlight·editorial serif 의도보존 ✅). 8테마 전수 ERROR0 + COM 의도보존. **R3 = 첫 클린 라운드, 클린카운터=1**.
- **STATUS**: resolved (2026-06-16 R3 완료, 클린카운터 1)

## Working Notes — ckpt-202606161345 (btn-design, R4 완료)
- **R4 소재 5장**: payroll-v2/15(8열계산표)·payroll-v2/13(5열비교표)·triassic/05(수평타임라인 교대배치)·samsung/16(2×2 리스크매트릭스)·tax-jv/04(JV비교표 값평가).
- **R4 결과**: 8테마 convert ERROR0. COM 의도보존 — 계산표·타임라인(교대배치)·JV비교표(값평가 의미색)·매트릭스 전부 ✅. dark-mono 매트릭스 다크 확인.
- **★R4 신규 변환기 함정 (중요 학습)**: 리스크매트릭스 처음엔 `cell > ri > tag/rn/rd` 중첩 flex로 만들었는데, **변환기(html2pptx) table-column snap 후처리가 flex-column "단일 복합자식" 셀의 내부 p들을 같은 Y에 겹쳐 배치**(저충격 셀 ri 1개만 겹침, 고충격 ri 2개는 정상). align-items/grid/nowrap/flex 9회 우회 부분실패 → **표 셀 패턴(셀=단일 p 멀티라인 `<br>`, 위험도=span 색)으로 재설계해 해결**(표 셀은 단일 텍스트박스라 변환기 100% 안전, slide-01/05 입증). 위험도 배지→색텍스트 전환(의도보존 유지).
- **클린카운터: 1 → 0 리셋**: R4에서 매트릭스 겹침 신규결함 발생 = 클린 아님. R3(클린1) 다음 R4 결함 → 연속 깨짐. R5·R6 2연속 클린 필요.
- **누적 학습 4개**(R5+ 선적용): ①heading fallback ②어두운surface 강조=surface-inverse-fg ③태그 nowrap(div+p) ④**복합내용 셀은 표 패턴(단일 p 멀티라인), 중첩 flex 칩 회피**.
- **STATUS**: resolved (2026-06-16 R4 완료)

## Working Notes — ckpt-202606161440 (btn-design, R5 완료 + R6~R10 소재 등록)
- **R5 완료**: 소재=payroll-guide/20·31·35·space-resource/02·ai-infra/09. 8테마 ERROR0(수정후). KPI+시나리오표·step+환급표·차트복합·타임라인+표·월별캘린더. dark 캘린더 COM 확인.
- **★R5 신규결함(수정완료)**: ①시나리오/강조 행 bg에 **연한 톤 고정hex**(#EAF7EF/#FDF0E8/#FDF3EA) → 다크테마 밝은텍스트와 1.1:1 충돌(dark-mono/pitch 16 ERROR) → 연한bg 제거(theme-bg/gray-4 테마토큰), 강조는 텍스트색. ②academic slide-05 note accent-secondary==surface-inverse #1F4E79 충돌 → surface-inverse-fg. **누적 학습 5번째: 연한 톤 bg 고정hex 금지(다크충돌), 행/셀 강조 bg는 테마토큰**.
- **클린카운터=0 유지**: R5 결함 발생 = 클린아님. R4·R5 연속 결함. 2연속 클린 미달성. R6+ 필요.
- **★R6~R10 소재 25장 등록(plan §0.6)**: R1~R5 25장 소진 → Explore subagent 선정 → chupi-character 5장(SVG 일러스트 부적합) + payroll-guide/21·noahs-ark/04(단순) 교체 → 미사용 데이터덱 복잡슬라이드로. 전수 grid/flex 밀도+실재 검증 완료. 중복0.
- **워크플로우(R6~R10 동일)**: 매 라운드 = plan §0.6 소재 5장 Read → modern 범용토큰 베이스 생성(누적 5함정 선적용) → sed 6테마+editorial serif → preflight 포함 변환 → VP → COM 의도보존.
- **STATUS**: resolved (2026-06-16 R5완료+R6~R10소재등록)

## Working Notes — ckpt-202606161510 (btn-design, R6 완료, 자율주행)
- **자율주행 모드**: 사용자 지시 "R6~R10 소진 또는 2연속클린까지, ctx 750k 자동압축하며 계속". long-mode on2(750k) 활성. autopilot flag=secretary경로없어 skip.
- **R6 완료**: 소재=apartment/06(권역표)·posco/07(재무표,posco/03목차 교체)·space-economy/03-newspace(투패널 비용표+stat)·apartment/10(정책카드,manuf/02 intro 교체)·global-space/08(outlook카드). 8테마 ERROR0 + COM 의도보존(slide-01/03/05 확인). 정탐회귀0.
- **★R6 신규결함(수정완료) + 학습6**: 배지/태그를 `<span class="badge">텍스트</span>`(span 직접)로 만들면 **변환기가 span 배경 미렌더**(idiomatic "배경은 div만") + 텍스트 wrap("성장"→"성/장"). → **배지/태그 = `<div class="badge"><p>텍스트</p></div>` + `.badge p {white-space:nowrap}`**. slide-01 배지 6개 + slide-05 tag 6개 수정.
- **누적 학습 6개**(R7+ 선적용): ①heading fallback ②어두운surface강조=surface-inverse-fg ③긴텍스트 nowrap(div+p) ④복합셀=표패턴(단일p멀티라인) ⑤연한톤bg고정hex금지(다크충돌)→테마토큰 ⑥배지/태그=div>p+nowrap(span배경금지).
- **클린카운터=0**: R5·R6 연속 결함. R7+ 2연속클린 필요(누적6학습으로 확률↑).
- **★소재선정 주의**: subagent grep(grid/flex밀도)이 목차/intro/표지를 못 거름 → 각 라운드 진입 시 소재 Read로 "복잡 데이터슬라이드"인지 재확인, 단순이면 plan §0.6 미사용 복잡슬라이드로 교체.
- **STATUS**: resolved (2026-06-16 R6완료)

## Working Notes — ckpt-202606161545 (btn-design, R7 완료, 자율주행)
- **R7 완료**: 소재=payroll-v2/28(요율표+계수카드)·posco/12(리튬현황표,R7-2 중복해소 교체)·naver/15(재무전망표+카드)·payroll-v2/31(KPI+step+표)·payroll-guide/17(일용vs상용 12행비교표). 8테마 ERROR0+FAILED0 + COM의도보존(slide-03/05 확인). 정탐회귀0.
- **★R7 신규결함(수정완료) + 학습7**: slide-05(12행 비교표)가 **HTML 720pt를 7.5pt 초과** → 변환기가 `FAILED ... overflows body` + **슬라이드 silent omit**(pptx에 slide5.xml 누락). ★CONTRAST/invisible/XML ERROR 0이라 내 집계가 못잡음 → COM에서 빈(0byte) png로 발견. **수정**: head margin/padding + td padding 축소로 720 내. **집계 필수**: `grep -cE "FAILED|failed to convert"` 추가(C/inv/xml 3형식 + FAILED = 4형식).
- **누적 학습 7개**(R8+ 선적용): ①heading fallback ②어두운surface강조=surface-inverse-fg ③긴텍스트 nowrap(div+p) ④복합셀=표패턴(단일p멀티라인) ⑤연한톤bg고정hex금지→테마토큰 ⑥배지/태그=div>p+nowrap(span배경금지) ⑦**행많은 표는 720 초과주의(head/td padding 축소), 변환집계에 FAILED 포함**.
- **클린카운터=0**: R6·R7 연속 결함. R8+ 2연속클린 필요.
- **다음**: R8 진입(manuf-kpi/03·payroll-v2/14·payroll-guide/19·34·13) 소재 Read(복잡도 재확인) → 생성.
- **STATUS**: in-progress (R8 대기)

> [ckpt-202606161700:btn-design] ★R8 완료 + 변환기 수정(정사각 아이콘 column 오인) + 사용자 2지적 수용
- **R8 소재**: manuf-kpi/03·payroll-v2/14·payroll-guide/19·34·13 (PQCD 4카드·6열표·BEFORE/AFTER+영향표·9행캘린더·요율표+calc). 8테마 ERROR0+FAIL0+COM의도보존.
- **★사용자 2지적(2026-06-16)**: (a) "PF/VP에 맞게 깎는게 아니라 디자인 원안 의도 구현도 목표" (b) "이전 세션 수정도 원안 크게 헤치는지 전수검토". → 둘 다 수용.
- **전수검토 결과**: R1~R7 레이아웃·정보구조·데이터는 보존(표/카드/타임라인/매트릭스 구조 유지). 단 **색 시각강조 일부 약화**(R4 리스크매트릭스 위험도 셀틴트·배지 색칩 → 텍스트색/토큰으로 강등, R5 등). 원인=변환기가 색배경+흰글씨 칩을 invisible로 떨궈 회피한 것.
- **★학습8 (색배경 칩 invisible)**: 색배경 div 안에 자식 `<p>`(textTags)를 넣으면 변환기가 배경과 텍스트를 분리 → p텍스트가 전체폭으로 떨어져 배경과 어긋남 → invisible(`#FFF on #FFF`). **해결: 색배경 칩/아이콘은 자식 `<p>` 없이 div 직속 텍스트**(`<div class="ic-p">P</div>` = shape+embedded text, 분리 안 됨). R6 .th 통과는 표헤더 confirmed-column이라 snap 작동했던 것.
- **★학습9 (카드 불릿 텍스트 겹침/누락)**: `.item` flex(dot span + p) 구조는 변환기 column-snap에서 여러 p가 한 위치로 묶여 겹침/누락. 단일 `<p>`+inline `<b>`불릿 또는 `<br>` 멀티라인으로 통합.
- **★변환기 수정 (html2pptx.cjs line631-632)**: confirmed table column 판정에서 **정사각형 작은 shape(w<1.2" + near-square ratio<0.35) 제외**. 2×2 색아이콘이 table-column으로 오인되어 그 Y범위 내 카드 본문 텍스트가 snap돼 겹치던 버그 해결(학습4 동류). 주석에도 "badges are not table columns" 의도 존재. **사용자 1번 선택(변환기 수정으로 원안 색강조 복원)에 따른 전역 수정**.
- **★정탐회귀 0 검증**: GT 17덱(slides-grab) 재변환+VP → 전부 VP-ERROR=0 (baseline 동일). samsung FAIL=1슬라이드(slide-15 18pt overflow)는 GT 원본 고유, 변환기 수정 전후 동일(git stash 대조 확인) = 회귀 아님.
- **결과**: PQCD 2×2 색아이콘 카드(P파랑/Q초록/C주황/D보라 흰글씨) 원안 그대로 보존 + ERROR0. modern/dark-mono COM 확인(다크테마 색아이콘 대비 우수).
- **클린카운터=0** (R8에서 신규결함 발견·수정 = 클린라운드 아님).
- **미완 (다음)**: 이전 라운드(R4 매트릭스 배지/셀틴트 등) 색강조 복원 = 변환기 수정+학습8로 이제 가능 → 사용자 의도(의도보존) 차원에서 복원 권장. R9 진입 전 또는 병행 결정 필요.
- **STATUS**: R8 완료 (2026-06-16). 변환기 수정 미커밋(영속화 필요).

> [Working Notes — ckpt-202606160230:btn-design] R4 색강조 복원 (사용자 1번) — 압축 직전
- **마지막 결정**: R4 slide-04 리스크매트릭스 위험배지 색칩 복원 완료(커밋 fff40e8). 원안 samsung/16 위험도 색강조(critical 주황#FF6F00·moderate 파랑#1428A0·low 연파랑#B0C4DE)를 텍스트색 span 강등→학습8 색배경 div 직속텍스트로 복원. 배지 width:62px+center로 변환기 폭과소측정(3글자 클립) fix. 대응전략 3색 보더 복원. 셀 틴트 rgba는 변환기 알파 미합성으로 대비 오측정→제거(학습5 확장, 배지로 위험도 강조 유지). 8테마 ERROR0, modern COM 의도보존 확인.
- **다음 의도**: (1) R4 dark-mono/dark-pitch slide-04 COM 시각확인(배지 색칩 다크bg 대비) — modern만 확인함 (2) R5/R6 색강조 점검(grep 색배경칩 감소분, 원안 대비 복원) (3) R9 진행(payroll-v2/02·coupang/09·payroll-guide/30·11·32). 종료조건=2연속 클린, 클린카운터=0.
- **동기화 필요**: 핸드오프 §10.3(A) = R4 배지복원 완료 마킹. 학습8 확장(배지 폭 width명시)·학습5 확장(rgba도 알파미합성 함정).

## Working Notes — ckpt-202606160910 (btn-design, 색강조복원 종결 + R9 진입직전, 자율주행)
- **마지막 결정**: ★(A)색강조 복원 작업 **종결**. (1)R4 slide-04 dark-mono/dark-pitch COM 시각확인 완료 = 위험배지 색칩(중위험 파랑#1428A0/고위험 주황#FF6F00/저위험 연파랑#B0C4DE 검은글씨) 다크bg 대비 우수, 글씨 안잘림, 대응전략 3색보더 보임. modern 포함 3테마 의도보존. (2)R5 색강조 점검 = 약화없음(slide-01 연말정산: step주황컬러바·다크헤더표·데이터의미색 환급청록/추징빨강·주황강조박스 보존 / slide-03 우주채굴: 주황차트·세그먼트바 보존). R6은 학습6(배지div>p)으로 이미 색배지 살림. → 결론: R4 유일 명확약화였고 복원완료, R5/R6 충분보존.
- **사용자 질의응답(2026-06-16)**: "pptx가 원안png와 일치하나 보는거냐" → 정정설명: 2비교축 = ①생성HTML↔변환PNG(변환충실도, 주목적, 결함잡기) ②원안↔생성HTML(데이터·색강조 의도보존). 원안 픽셀일치 목표 아님(design-system은 다른 테마비주얼). 클린카운터=0(R3만 클린 후 R4~R8 매라운드 신규결함).
- **R9 소재 복잡도 판정 완료**: coupang/09(순환다이어그램6노드+3색보더카드)·payroll-guide/30(2컬럼step프로세스+공식박스+하단다크)·payroll-guide/11(5열11행 누적비용표 다크헤더+subtotal+주황누적, ★11행 720주의)·payroll-guide/32(5단계체크리스트+다크타임라인) = **복잡 데이터슬라이드 4장 채택**. ★payroll-v2/02 = 목차(2x5 TOC) → **교체 필요**(R6 posco/03 목차교체 전례).
- **다음 의도**: (1)payroll-v2/02 교체재 1장 확정 — 미사용 grid후보 중 slide-20(5열표 120/70/90/60/100pt)·17(4열)·24(4열)·22/23(3열 넓은) 유력, 1장 Read로 복잡도 확정 (2)R9 modern 베이스 5장 생성(★누적9학습 선적용: ①heading fallback ②어두운surface강조=surface-inverse-fg ③긴텍스트nowrap div+p ④복합셀=표패턴단일p ⑤연한톤bg고정hex금지→테마토큰 ⑥배지/태그=div>p+nowrap ⑦행많은표720주의 ⑧색배경칩=div직속텍스트 ⑨카드불릿=단일p) (3)sed 6테마+editorial serif (4)PF포함변환 (5)VP+COM 의도보존+정탐회귀0. 종료조건=2연속클린, **클린카운터=0**.
- **동기화 필요**: RENDERED-ASSETS-INDEX R9행 = payroll-v2/02 교체 반영. 핸드오프 §10.3(A) R4완료+R5/R6점검완료 마킹(반영함).

## Working Notes — ckpt-202606161900 (btn-design, R9 완료, 자율주행)
- **마지막 결정**: ★R9 완료(커밋 d19c6cc). 소재 5장 = coupang/09 플라이휠 · payroll-guide/30 step프로세스 · 11 누적표 · 32 체크리스트 · **payroll-v2/20 시뮬표**(payroll-v2/02 목차→20 교체 확정, slide-20=hero KPI+계산박스+5열4행 시뮬표 다크헤더/주황하이라이트). 9학습 선적용. 8테마 PF/XML ERROR 0. 6계열 COM 의도보존 확인(modern 라이트/dark-mono·dark-pitch 다크/editorial serif/executive warm-navy). 색강조 = var(--accent) 테마적응(modern주황/dark cyan/exec navy), 다크헤더·3색보더 surface-inverse, 색칩 div직속(학습8). CONTRAST 전건 WARN(ERROR0).
- **R9 신규결함 2건(K규칙 디자인수정, 둘다 해결)**: (1)slide-05 VP-14 = 좌우분리 head(제목+hero KPI) flex justify-between → 변환기 좌표화 58% 겹침 → htext width:720px+hero width:260px 둘다 flex-shrink:0 명시로 해소. (2)slide-01 대각선 화살표 ↘↗(U+2198/2197) → PowerPoint 폰트 폴백 È/É 깨짐 → 직교 →↑ 교체. **→ R9는 신규결함 발생 라운드 = 클린 아님. 클린카운터=0 유지(리셋)**. 학습10/11 = promotion-log K-202606161900 박제.
- **다음 의도**: R10 진행(payroll-v2/30·payroll-guide/09·41·samsung/06·discounted/11 — plan §0.6). ★학습10/11 선적용(좌우분할 head=명시width / 다이어그램=직교화살표만). modern 베이스 생성→sed 6테마+editorial serif→PF변환→VP+COM 의도보존+정탐회귀0. 소재 복잡도 Read 재확인(목차/단순이면 미사용 복잡슬라이드 교체). 종료조건=2연속클린, **클린카운터=0**.
- **동기화 필요**: RENDERED-ASSETS-INDEX R9행 완료 마킹(payroll-v2/20 교체 반영). 핸드오프 §10 R9완료+학습10/11 마킹.
