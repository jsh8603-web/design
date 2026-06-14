# A/B 규칙 검증 방법론 (검출기 변경 → 운영 덱 효과 + FP/FN 회귀)

> 핸드오프 규칙/계수 변경을 **합성 슬라이드 + 적대적 케이스 + 운영 덱 + FP/FN 렌더 대조**로 검증하는 재현 절차.
> 근거 실측 전문: `slides/mock-dense/VERIFICATION.md` (§1-9.1). node = `/c/Program Files/nodejs`.

## 환경
- node: `export PATH="/c/Program Files/nodejs:$PATH"`
- /tmp(bash)=`C:\msys64\tmp` 이지만 **node 인자엔 Windows 경로**(`C:/msys64/tmp/...`) 줘야 함(bash `/tmp`를 node가 `D:\tmp`로 오인 — 단 CLI arg는 MSYS 자동변환됨).
- PPTX 렌더: PowerPoint COM 가용. `powershell scripts/export-slides-png.ps1 -PptxPath <win> -OutputDir <win> -Width 1600 -Height 900 -Slides "5,8"`
- 운영 덱: `D:/projects/slides-grab/slides/<deck>/slide-NN.html` (+ assets/). 빽빽 후보: 투자리포트(ai-infra/samsung/naver/kakao/posco/coupang), commodity, payroll-guide.

## 5단계 절차

### 1. 합성 슬라이드 (그라운드트루스를 알고 설계)
`slides/mock-dense/slide-1~6.html` (커밋됨, body 960×540px). 1~3=정상 케이스, 4~6=적대적(FN 함정).
렌더: `node scripts/screenshot-html.mjs --slides-dir slides/mock-dense --output slides/mock-dense/png`

### 2. 기존 vs 새 규칙 A/B (현재 작업본 vs git)
빽빽=PF-28 ERROR라 정상변환 막힘 → `convert-native --skip-preflight`로 PPTX 강제 생성.
검출 카운트 비교 (PF/VP/overlap):
```
# 새 규칙(현재) 측정 → git stash 또는 git checkout HEAD~N -- scripts/ 로 기존 측정 → diff
node --input-type=module -e "import {preflightCheck} from './scripts/preflight-html.js'; const r=await preflightCheck('<deck>',{full:true}); ..."  # PF errors+warnings
node scripts/convert-native.mjs --slides-dir <deck> --output <pptx> --skip-preflight   # 변환
node scripts/validate-pptx.js --input <pptx> | grep -oE 'VP-[0-9]+' | sort | uniq -c   # VP
node scripts/validate-slides.js --slides-dir <deck> | grep criticalIssues              # overlap
```
회귀 안전 = **의도 안 한 규칙 카운트 불변** 확인(PF 30종/VP 9종).

### 3. 운영 덱 합본 (실세계 빈도 축)
```
bash tests/ab-method/build-mix.sh C:/msys64/tmp/realmix D:/projects/slides-grab/slides \
  ai-infra-investment samsung-investment-report naver-investment-strategy kakao-investment-strategy \
  posco-investment-strategy coupang-investment-report commodity-analysis payroll-guide
```
그 다음 §2 명령을 합본 폴더에 적용. 156장 ~수분.

### 4. VP-16 계수 캘리브레이션 (변경이 VP-16이면)
`node tests/ab-method/measure-cjk.mjs "텍스트1" "텍스트2"` → 실측 폭 → 계수 역산.
현 채택: CJK 0.92 / Latin 0.5 / 공백 0.25 (`validate-pptx.js:1149`). 공백 0.4는 FP 재발로 철회.

### 5. ★FP/FN 양방향 렌더 대조 (정탐 회귀 — 빼먹지 말 것)
- **FP 확인**: 새 규칙이 제거한 케이스(OLD WARN→NEW PASS)를 PPTX 렌더 → 실제 안 넘치면 FP 제거 정당.
- **★FN 확인(정탐 놓침 회귀)**: 격하 케이스 **전수**의 `fills %` 분포 추출 → 경계(95~101%) 슬라이드를 PPTX COM 렌더 → 실제 wrap/overflow면 FN(과공격), 박스 안 들어가면 FP였음.
  ```
  # OLD/NEW VP-16 텍스트 diff로 격하 케이스 추출
  comm -23 <(grep -oE 'text "[^"]*"' OLD.txt|sort -u) <(grep -oE 'text "[^"]*"' NEW.txt|sort -u)
  # 격하 케이스 fills% 정렬 → 최저(가장 빠듯)부터 렌더 확인
  ```
  CJK 0.92 사례: 격하 19건 전부 fills 95~101%, 렌더 전수 대조 → 전부 FP, FN 0 (VERIFICATION §9.1).
  **will overflow(심각)뿐 아니라 may wrap→pass 격하분도 반드시 봐야 함**(이번에 처음 누락→사용자 지적으로 보강).

## 산출
- 코드 변경 + `slides/mock-dense/VERIFICATION.md`에 측정 데이터·정정 이력·FP/FN 결과 박제 후 커밋.
- "잔여 N건 = 전부 FP 아님" 분류(will overflow=TP / may wrap=빽빽 한글 실제 wrap 다수=TP / fits) 명시.
