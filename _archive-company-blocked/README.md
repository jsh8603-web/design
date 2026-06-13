# _archive-company-blocked

사내 Claude Code 환경에서 **사용 불가**한 자산을 모아둔 곳. 기능 파이프라인에서 제외됨.
보존 목적(추후 환경 변화 대비)으로만 둔다. **여기 파일은 import/실행하지 말 것.**

## 사내 제약 사유
- OAuth 키 사용 불가 → Gemini API(이미지 생성·Vision) 전부 불가
- NotebookLM 불가
- 지식 소스 = 사내 DB + WebFetch/WebSearch + Confluence 용어집 으로 한정

## 분리된 자산
| 파일 | 원위치 | 제외 사유 |
|---|---|---|
| `nano_banana_guide.md` | design-system/ | Gemini(nanoBanana) 이미지 생성 프롬프트 가이드. 이미지 생성 AI 의존 |

## 참고
- `image_slot_contract.md` 는 **제외하지 않음** — design-system/ 에 남겨 "수동/사내DB 이미지 배치용 마크업 규칙"으로 사용.
- 변환 엔진 쪽 사내불가 의존(generate-images.mjs, fetch-notebooklm.js, nlm-auto-research.js 등)은
  Phase 2 에서 원본 slides-grab 으로부터 **애초에 가져오지 않는** 방식으로 처리.
</content>
