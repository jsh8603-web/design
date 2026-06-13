# Research Sourcing — 사내 환경 지식 수집 규칙

보고서의 모든 비자명한 주장은 **출처가 있어야** 한다. 이 문서는 사내 Claude Code 환경에서
**무엇으로 자료를 모으는지**와 **어떻게 출처를 다는지**를 규정한다.
검증(주장이 출처에 부합하는지)은 `rules/content-authoring.md §13`(verification gate)이 담당한다.

## 1. 허용 소스 3종 (이것만 사용)

NotebookLM·Gemini 리서치·OAuth 기반 도구는 **전부 불가**. 다음 3종만 쓴다.

| # | 소스 | 무엇 | 출처 클래스(§13) | 비고 |
|---|---|---|---|---|
| 1 | **사내 DB** | 쿼리 결과 / 테이블·뷰 / 셀 참조 / 대시보드 추출본 | internal | 기준일(as-of) 필수. bitemporal |
| 2 | **WebFetch / WebSearch (직접)** | 공개 URL·권위 출처 (국세청·한국회계기준원·IFRS·시장데이터) | external | 1차 출처 우선, 집계/블로그 회피 |
| 3 | **Confluence** (사내 위키·용어집) | 사내 정의·표준·용어집·이전 보고서 | internal/external 경계 | 사내 용어 통일·내부 정책 근거 |

- **사내 DB 접근**: 연결이 닿으면 읽고 brief 의 *Decisions log* 에 기록. 안 닿으면(프록시/SSL) 사용자에게 추출본(쿼리결과 JSON/CSV/셀참조)을 요청한다. 추정치로 메우지 않는다.
- **WebFetch/WebSearch**: 사내망에서 외부 접근 가능 여부를 먼저 확인. 막히면 사용자에게 자료를 받는다. 더 많은 검색 ≠ 더 신뢰 — 권위 출처 소수가 약한 출처 다수를 이긴다.
- **Confluence**: 사내 용어·정의·정책은 Confluence 를 1차로 본다. 같은 개념을 보고서마다 다르게 부르지 않도록 용어집을 기준으로 통일한다.

## 2. Source 필드 의무 (아웃라인·본문)

- 아웃라인의 모든 슬라이드/섹션에 `Source:` 필드를 둔다. 빈 `Source:` 가 있으면 미완성이다.
- 본문의 모든 수치는 인라인 태그를 단다(`content-authoring.md §5`).
  - internal: `[src: <query_id|table.view|file p.X|cell Sheet!B12> @ <as_of_date>]`
  - external: `[src: <authority>, <doc/standard>, <section>, <retrieved_date>]`
  - Confluence: `[src: confluence:<space>/<page> @ <retrieved_date>]`
  - 미상: `[Source needed]` — 완료 전 반드시 해소.

## 3. 리서치 보강 트리거 (다음 중 하나면 추가 조사)

1. **커버리지 공백**: 섹션 주장에 출처가 비었거나 1개뿐.
2. **구체성 테스트 실패**: 한 섹션에서 사실 3개 이상을 출처와 함께 댈 수 없다.
3. **사용자 보강 요청**: "내용 더 채워줘" → AI 기억만으로 쓰지 말고 위 3종 소스로 보강.

보강 시 우선순위: **사내 DB → Confluence → WebFetch/WebSearch → (최후) AI 일반지식**.
AI 일반지식만으로 채운 문장은 `[Source needed]` 로 표시하고 검증 대상에 올린다.

### 면제
사용자가 "리서치 없이" 명시 / 텍스트만 편집 / 이미지·레이아웃 변경 / 이미 섹션당 출처 3개 이상.

## 4. 환각 방지 연계

- 수집한 external 주장은 `content-authoring.md §13.3`(RARR: 검증질문 → 권위 출처 retrieve → 합의 게이트 → 모순 시에만 수정·재인용)을 통과해야 ship.
- 인용한 출처가 **실제로 그 내용을 말하는지** 확인한다(존재만 확인하지 말 것).
- 권위 출처가 못 푸는 external 사실은 `needs-human` 으로 사용자에게 라우팅.
