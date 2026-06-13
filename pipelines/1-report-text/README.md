# Pipeline 1 — Report Text (본문 텍스트)

**출력**: `deck.md` (또는 보고서 `.md`). 본문 + 화자 노트 + 근거 태그.
**용처**: 초안·메모·이메일 보고, 엑셀/DB 데이터 보고서, 그리고 파이프라인 2·3 의 입력.

## 언제 이걸 쓰나
- 디자인/슬라이드가 아직 필요 없고 **내용**을 먼저 확정할 때.
- 엑셀·DB 추출처럼 데이터가 주가 되는 보고서(`rules/content-authoring.md §17.1`).
- PDF·PPTX 로 갈 거라도 **항상 여기서 시작**한다.

## 흐름
1. **Brief** — `slides/<slug>/00-brief.md` 생성, 방향·근거맵·검증 원장. (`content-authoring.md §10`)
2. **고스트덱 아웃라인** — 액션 타이틀만으로 논리 확인. (`§2`, `§11.2`)
3. **슬라이드별 본문 작성** — `deck.md` 에 한 장씩. 액션 타이틀 / ≤40 단어 / exhibit 1개 / 모든 수치에 `[src: …]`. (`§11.3~§11.5`)
4. **리서치** — 사내 DB + WebFetch + Confluence 3종으로만. (`rules/research-sourcing.md`)
5. **§13 검증 게이트** — internal(NLI) / external(RARR) / derived(코드 재계산). 출구 = `unsupported` 0건. (`§13`)
6. **리더 테스트** — 서브에이전트로 고스트덱 재구성·자가완결 슬라이드 점검. (`§14`)

## 산출 스키마 (deck.md 슬라이드 단위)
```
## Slide N: [액션 타이틀]
**Key message**: [한 문장]
**Body**: [3–5 bullets, ≤40 단어]
**Visual hint**: [차트 종류·축·강조·비강조]
**Sources**: [모든 수치 src 태그; internal 은 as-of date]
**Speaker notes**: [3–6문장: 맥락/전환/Q&A]
```

## 데이터 보고서 체크 (엑셀/DB)
- derived 숫자(분산·증감률·마진·비중·합계)는 **코드로 재계산** + cross-foot. (`§13.4`)
- as-of date 필수. 표보다 그래프. `<table>` 금지(→ CSS grid는 디자인 단계).

## 다음 단계
- 회람 문서면 → `../2-pdf/`
- 발표자료면 → `../3-pptx/`
