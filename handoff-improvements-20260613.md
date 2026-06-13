---
title: design 레포 핵심 개선 9건 — 적용 핸드오프
tags: [handoff, improvements, vr, fonts, ci]
date: 2026-06-13
next-action: 사용자 "design 레포 핵심 개선 9건" HANDOFF 문서 재제공 받아 §A 4파일 + §B 적용 → vr:test 검증 → 커밋
---

# 핸드오프 — design 레포 개선 9건 적용

## 0. 출처 / 재개 전제
- 작업 = 사용자가 준 **"design 레포 핵심 개선 9건 — 적용 프롬프트"** HANDOFF 문서 적용 (2026-06-13 14:07 메시지).
- ★다음 세션은 그 HANDOFF 문서 전문이 필요 — 사용자에게 재제공 요청("개선 9건 문서 다시 줘"). 문서에 §A 새파일 전문 + §B 수정 위치 다 있음.
- 직전 완료 (push됨): PPTX 12종 `0c08568`, VR 시스템 `e02e5d1`, harness skip `90a3643`, 골든격리 `ad3ff36`.

## 1. 9건 목록 + 적용 상태
| # | 개선 | 파일 | 상태 |
|---|---|---|---|
| 8 | LICENSE(MIT) | `LICENSE` | ✅ 생성 완료 (미커밋) |
| 1 | GitHub Actions CI | `.github/workflows/visual-regression.yml` | ⬜ §A.4 전문 그대로 생성 |
| 7 | 케이스별 임계 | `tests/visual-regression/thresholds.json` | ⬜ §B.3 `{"default":0.005,"overrides":{...}}` |
| 3,4 | 폰트 임베드+가드 | `tests/visual-regression/embed-fonts.mjs` | ⬜ §A.1 전문 (jszip, 신규의존 0) |
| 6 | diff 리뷰 리포트 | `tests/visual-regression/gen-report.mjs` | ⬜ §A.2 전문 (zero-dep HTML 갤러리) |
| 3,4,5 | 폰트 ground-truth 테스트 | `tests/visual-regression/test-fonts.mjs` | ⬜ §A.3 전문 |
| 4 | 가드 연결 | `scripts/convert-native.mjs` | ⬜ §B.1 PPTX 생성 직후 guardFonts() 호출 + process.exit(1) |
| 1 | vr:test 합류 | `package.json` | ⬜ §B.1 vr:test 끝에 `&& node tests/visual-regression/test-fonts.mjs` |
| 9 | Vision 가이드 펜싱 | `.aiignore` 또는 SKILL 라우팅 | ⬜ §B.5 `_archive-company-blocked/` 추가 |
| 9 | 렌더러 이중화 패리티 | 테스트 1개 | ⬜ §B.6 convert-native vs convert.cjs → rasterize → diff (설계만) |

## 2. 환경 제약 (증명 시 주의)
- 이 Windows 환경: **fonttools/brotli 없음, soffice(LibreOffice) 없음, python3 명령 없음**(python.exe는 `/c/Users/jsh86/AppData/Local/Programs/Python/Python312/python.exe`), LiberationSans TTF 없음(`/usr/share/fonts/...`는 Linux 경로).
- test-fonts.mjs는 **Linux/CI(ubuntu) 전제** — Windows 로컬에선 LibreOffice/python3/TTF 단계 실패. CI(§A.4)에서 50/50.
- §C 증명 "vr:test 50/50"은 CI 기준. Windows 로컬은 diff 10 + harness 9(skip 2) + fonts 부분.
- node 실행: `export PATH="/c/Program Files/nodejs:$PATH"` 선행. python은 위 풀패스.

## 3. 핵심 설계 메모 (HANDOFF §D·E 요약)
- 신규 npm 의존성 0 (sharp/jszip/pdf-lib/pptxgenjs 기존만). woff2→ttf는 python fonttools 선택.
- 폰트 임베딩: raw TTF (LibreOffice/Mac PPT OK, Windows PPT는 EOT/.fntdata 필요 — 불안정). **가드(#4)가 안전망, 임베드(#3)는 best-effort**.
- 임계: Playwright threshold/maxDiffPixels 모델. diff.mjs는 현재 ratio 기반 — maxDiffPixels 절대픽셀은 추가 인자 필요.
- CI: TZ=Asia/Seoul 핀, 골든은 CI 동일 이미지(ubuntu)에서 재생성 커밋(드리프트 방지).

## 4. 재개 레시피
1. 사용자에게 "개선 9건 HANDOFF 문서 다시 줘" 요청.
2. §A.1~A.3(긴 3 .mjs)은 subagent 위임 권장(전문 그대로 Write) — 메인 컨텍스트 보호.
3. §A.4 yml, thresholds.json, §B.1 convert-native 가드 + package.json은 메인 직접.
4. `export PATH="/c/Program Files/nodejs:$PATH"; node tests/visual-regression/test-diff.mjs` 등으로 검증(Windows 부분).
5. 커밋 단위 분할(LICENSE+CI / 폰트 / 리포트). commit hook 1차 차단 시 그대로 재커밋.
