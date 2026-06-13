# slides-grab — Gemini 프로젝트 보충 규칙

## 공유 규칙

이 프로젝트의 규칙은 **CLAUDE.md에 정의**. 반드시 읽고 따를 것.
CLAUDE.md의 모든 규칙(3분류 판정, A~I 체크리스트, change-log C-NN, 파이프라인 절차)을 준수.

## 읽기 경로 (.claude/docs/ 읽기 불가 → 루트 대체)

| CLAUDE.md 경로 | Gemini 읽기 경로 | 비고 |
|---------------|-----------------|------|
| .claude/docs/presentation-flow.md | PRESENTATION_FLOW.md | 읽기 전용 복사본 |
| .claude/docs/design-modes.md | DESIGN_MODES.md | 읽기 전용 복사본 |
| .claude/docs/pf-step-0-1.md | PF_STEP_0_1.md | 읽기 전용 복사본 |
| .claude/docs/pf-step-1.5b.md | PF_STEP_1_5B.md | 읽기 전용 복사본 |
| .claude/docs/pf-step-2-2.5.md | PF_STEP_2_2_5.md | 읽기 전용 복사본 |
| .claude/docs/pf-step-3-4.md | PF_STEP_3_4.md | 읽기 전용 복사본 |
| .claude/docs/pf-step-5-6-7.md | PF_STEP_5_6_7.md | 읽기 전용 복사본 |
| .claude/docs/testing-rules.md | TESTING_RULES.md | 읽기 전용 복사본 |
| .claude/docs/production-reporting-rules.md | PRODUCTION_REPORTING_RULES.md | 읽기 전용 복사본 |
| .claude/docs/html-rule-examples.md | HTML_RULE_EXAMPLES.md | 읽기 전용 복사본 |
| .claude/docs/notebooklm-fetch.md | NOTEBOOKLM_FETCH.md | 읽기 전용 복사본 |
| .claude/docs/vqa-pipeline-maintenance.md | VQA_PIPELINE_MAINTENANCE.md | 읽기 전용 복사본 |
| .claude/docs/research-supplement-rules.md | RESEARCH_SUPPLEMENT_RULES.md | 읽기 전용 복사본 |
| .claude/docs/html-prevention-rules.md | html-prevention-rules.md | **단일 원본 (루트)** |
| .claude/docs/pptx-inspection-log.md | pptx-inspection-log.md | **단일 원본 (루트)** |
| .claude/docs/nanoBanana-guide.md | nanoBanana-guide.md | **단일 원본 (루트)** |

### Skills 경로 매핑

| CLAUDE.md 경로 | Gemini 경로 |
|---------------|------------|
| .claude/skills/plan-skill/ | skills/ppt-plan-skill/ |
| .claude/skills/design-skill/ | skills/ppt-design-skill/ |
| .claude/skills/pptx-skill/ | skills/ppt-pptx-skill/ |
| .claude/skills/presentation-skill/ | skills/ppt-presentation-skill/ |

## 3분류 판정 — B/C/D는 독립 단계 (CLAUDE.md §3분류 판정 참조)

정탐-수정 시 B만 하고 C/D를 건너뛰는 것은 **금지**. 반드시 3단계 모두 수행.

### HTML/PPTX 파이프라인

| 판정 | B. 대상 수정 | C. 원인 수정 (생성 규칙) | D. 재발 방지 (탐지 코드) |
|------|------------|----------------------|----------------------|
| **오탐** | 해당 없음 | scripts/preflight-html.js 또는 validate-pptx.js | C=D |
| **정탐-수정** | slides/{name}/*.html 수정 | **html-prevention-rules.md에 회피 규칙 추가** | scripts/preflight-html.js 보강 |
| **정탐-한계** | 해당 없음 | html-prevention-rules.md에 금지 규칙 | — |

### 이미지 파이프라인

| 판정 | B. 대상 수정 | C. 원인 수정 (생성 규칙) | D. 재발 방지 (탐지 코드) |
|------|------------|----------------------|----------------------|
| **오탐** | 해당 없음 | scripts/generate-images.mjs | C=D |
| **정탐-수정** | 이미지/프롬프트 재생성 | **nanoBanana-guide.md에 생성 규칙 추가** | scripts/generate-images.mjs 보강 |
| **정탐-한계** | 해당 없음 | nanoBanana-guide.md에 금지 규칙 | — |

### 체크리스트 기재 형식 (필수)

B/C/D 각 항목에 **수정한 파일명 + 변경 내용**을 기재. "완료"만 적는 것은 금지.
- ✅ `C. 원인 수정: html-prevention-rules.md에 "PF-07: <p>에 background/border 금지" 규칙 추가`
- ❌ `C. 원인 수정: 완료` ← 검증 불가, 금지

## 기록 장소 (CLAUDE.md §파이프라인 MD 생성 규칙과 동일)

| 파일 | 위치 | 시점 | 형식 |
|------|------|------|------|
| progress.md | slides/{name}/ | 매 Step 즉시 | 4섹션 필수 (현재상태/Step진행/활성규칙/이슈목록) |
| change-log.md | slides/{name}/ | 코드 수정 시 | C-NN 다행 양식 (파일+함수/변경/이유/검증) |
| promotion-log | .gemini-outbox/promotion-log-entry.md | 에러/패턴 | Write-Proxy 경유 |

## 전역 연동 예외 (CLAUDE.md §전역 시스템 연동 규칙과 동일)

- 파이프라인 에러(PF/VP/COM) → progress.md + change-log.md에 기록 (promotion-log 불필요)
- pending-promotion: 파이프라인 명령 에러 → SKIP
- 가드 순서: 전역 guard → checklist-guard → 작업

## 리서치 보완 규칙 (RESEARCH_SUPPLEMENT_RULES.md 참조)

- 아웃라인 Source: 필드 필수 — 빈 Source는 보완 리서치 트리거
- 사용자 내용 보완 요청 시 search-engine 스킬로 리서치 완료 후 수정 (AI 지식만으로 수정 금지)
- Step 0.5 소스 커버리지 체크박스를 progress.md에 포함
- 상세: RESEARCH_SUPPLEMENT_RULES.md

## Agent 필드

progress.md `## 현재 상태`에 `Agent: Gemini CLI` 기재

## .claude/ 디렉토리 보호

`.claude/` 하위 파일은 **삭제/수정 금지**. `.geminiignore`로 차단됨.
- "단일 원본 (루트)"는 루트 파일을 Gemini가 읽으라는 의미이며, `.claude/docs/` 복사본을 삭제하라는 의미가 아님
- `.claude/docs/` 파일은 Claude가 사용하는 원본이므로 Gemini가 건드리면 Claude 파이프라인이 깨짐

## Auto-Approve Mode

자동승인 시 모든 확인 건너뛰고 파이프라인 진행
