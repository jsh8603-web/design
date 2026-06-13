# slides-grab 가드/테스트 — 사내 적용 노트

원본 slides-grab 의 운영 가드·테스트를 누락 없이 이식했으나, **그대로는 사내에서 작동하지 않는다**.
사내 hook 시스템에 붙일 때 아래를 조정한다. (조정 전까지는 **참고 자산**)

## 대상 파일
- `scripts/checklist-guard.mjs` — Edit/Write 전 progress.md 체크리스트 강제 (원본 CLAUDE.md 워크플로우)
- `scripts/session-restore-guard.mjs` — 세션 복원 전 가드
- `scripts/post-compact-restore.mjs` — 압축 후 복원
- `tests/test-guard.mjs` — 위 가드들의 테스트

## 사내 적용 시 조정 필요
1. **경로 의존**: `.claude/docs/`, `.claude/skills/` 등 원본 경로를 참조한다. 사내 구조(`rules/`, `design-system/`, `skills/`)로 매핑해야 한다.
2. **회사의존 참조 제거 대상** (해당 파일이 사내에 없어 매칭만 안 될 뿐, 정리 권장):
   - `checklist-guard.mjs`: `nanoBanana-guide.md`, `generate-images`, `test-vision-accuracy.mjs`, `vision-ground-truth.json` 참조 (이미지 생성/Gemini Vision)
   - `tests/test-guard.mjs`: C13/C14 (vision 파일 가드 테스트) — 사내 미해당
   - `tests/detection-regression/full-baseline.json`: VC(Vision) 케이스 1건 — 회귀 baseline 데이터, 무해
3. **활성화 방법**: 사내 Claude Code 의 hook 설정(settings.json PreToolUse)에 연결해야 작동한다. 미연결 시 단순 스크립트로만 존재.

## 결론
가드 로직 자체는 유효(progress.md 규율 강제)하나, **사내 hook 통합은 별도 작업**이다.
변환 파이프라인(`scripts/convert-native.mjs` 등)은 가드와 독립적으로 동작하므로 가드 미활성이어도 변환에 지장 없다.
