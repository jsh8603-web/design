# Visual Regression — 결정론적 시각 회귀

파이프라인 산출물(HTML 슬라이드 / PDF / PPTX)이 **시각적으로** 깨졌는지 잡는다.
원래의 Gemini-Vision 검증 단을 **신규 npm 의존성 0, 네트워크·OAuth·Vision 0**으로 대체한다.

엔진은 `sharp`(기존 의존성), 래스터라이저는 시스템 도구(`pdftoppm`, LibreOffice `soffice` — 탐지·스킵).

## 구성

| 파일 | 역할 | 검증 |
|---|---|---|
| `diff.mjs` | 픽셀 diff 엔진 (정규화·톨러런스·히트맵) | `test-diff.mjs` 10/10 |
| `rasterize.mjs` | PDF→PNG(poppler), PPTX→PDF→PNG(LibreOffice) | `test-rasterize.mjs` 7/7 |
| `run-visual-regression.mjs` | 하니스 (html/pdf/pptx 모드) | `test-harness.mjs` 20/20 |

## 사용

```bash
# 골든 최초 생성(렌더 가능한 메인 환경에서 1회) — 모드별
npm run vr:save                 # html (design-system 레이아웃·차트 전체)
npm run vr:save -- --mode pdf  --artifacts <pdf디렉터리>
npm run vr:save -- --mode pptx --artifacts <pptx디렉터리>

# 비교 (회귀 시 exit 1, diff/ 에 히트맵 저장)
npm run vr                      # html
npm run vr:pdf  -- --artifacts <dir>
npm run vr:pptx -- --artifacts <dir>

# 렌더 없이 사전 PNG로 비교 (CI 분리/오프라인)
npm run vr -- --current <png디렉터리>

# 전체 자체 테스트
npm run vr:test
```

골든은 `golden/<mode>/<key>.png`. 멀티페이지(PDF/PPTX)는 `<key>__p2.png` 식. 회귀 히트맵은 `diff/`(gitignore).
임계값은 `--threshold 0.005`(기본 0.5%) 로 조정.

## 결정성 규칙 (반드시 같은 환경)

1. **골든 생성과 비교는 동일 컨테이너/chromium/LibreOffice 에서.** OS가 다르면 폰트 힌팅·AA 차로 오탐.
   측정상 동일 환경 결정성은 HTML/PDF 0.000, **LibreOffice 0.00000**.
2. HTML 렌더 시 `animation:none/transition:none` 자동 주입(하니스), `document.fonts.ready` 대기.
3. 폰트는 로컬 woff2(`design-system/fonts/`)만.
4. 차트 JS의 `Date.now()`/`Math.random()` 은 시드 고정 또는 데모 데이터 고정.
5. 뷰포트 1600×900, PDF/PPTX 래스터 150dpi 고정.

## 임계값 주의

전체프레임 비율 임계는 **희소한 슬라이드의 작은 텍스트-only 변경을 놓칠 수 있다**(실측: 제목 한 줄 변경 ≈ 0.48% < 0.5%).
숫자 정합이 critical 한 보고서라면 (a) 임계를 낮추거나, (b) 텍스트 정합은 기존 PF/VP(규칙·XML) 레이어로 잡고
시각 회귀는 레이아웃·차트 깨짐 탐지에 집중하는 분업이 안전하다.

## 도구 부재 환경 (사내 = 정상 상태)

poppler·LibreOffice 미설치가 사내의 정상 상태다(설치 불가). 이때 PDF/PPTX 레이어(B/C)는 **자동 SKIP**(fail 아님):
`vr:test` = 엔진 **10/10 PASS** + 래스터 **2 skip** + 하니스 **9 pass·2 skip** = **전부 0 failed**.
HTML 레이어(A)만으로 슬라이드·차트 시각 회귀를 잡는다(전 경로가 HTML로 수렴하므로 커버리지 핵심).
poppler/LibreOffice가 있는 CI 컨테이너에서는 B/C도 활성화되어 하니스 20/20·래스터 7/7이 된다.

## LibreOffice 한계

PPTX 모드는 LibreOffice 렌더를 기준으로 한다(≠ PowerPoint). **자기 골든 대비 회귀**만 잡으며,
PowerPoint 와의 절대 일치를 보장하지 않는다(크로스플랫폼 COM 불가가 전제).
