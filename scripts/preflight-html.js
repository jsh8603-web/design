/**
 * HTML Pre-flight Validator — checks slide HTML files for known anti-patterns
 * BEFORE PPTX conversion.
 *
 * Usage:
 *   node scripts/preflight-html.js --slides-dir slides/presentation-name
 *   node scripts/preflight-html.js --slides-dir slides/presentation-name --full
 *   node scripts/preflight-html.js --slides-dir slides/presentation-name --full --summary
 *
 * Phase 1 (default): Static regex/string checks — fast, no browser.
 * Phase 2 (--full):  Playwright checks for overflow and CJK font-size.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'node:url';

const PF_DIR = path.dirname(fileURLToPath(import.meta.url));

// ── ANSI helpers ──────────────────────────────────────────────────────────────

const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';
const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

function fmtError(file, id, msg) {
  return `${RED}${BOLD}\u274c ERROR${RESET} ${RED}[${file}] ${id}: ${msg}${RESET}`;
}
function fmtWarn(file, id, msg) {
  return `${YELLOW}\u26a0\ufe0f  WARN ${RESET} ${YELLOW}[${file}] ${id}: ${msg}${RESET}`;
}

// ── Luminance helper ──────────────────────────────────────────────────────────

function hexToRgb(hex) {
  hex = hex.replace(/^#/, '');
  if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  if (hex.length !== 6) return null;
  const n = parseInt(hex, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function relativeLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

// isBrightColor removed — was only used by PF-01 (now removed)

// ── CJK detection ─────────────────────────────────────────────────────────────

const CJK_RE = /[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/;
const FLAG_EMOJI_RE = /[\u{1F1E6}-\u{1F1FF}]{2}/gu;

// ── Static checks (Phase 1) ──────────────────────────────────────────────────

// PF-01: REMOVED — subsumed by PF-39 (linear-gradient) + PF-62 (radial/conic-gradient)
// Gradient loss in PPTX makes text invisibility moot; PF-39/62 already catch the root cause.

function checkPF02(html, file) {
  const issues = [];
  // Find flex:1 or flex: 1 in inline styles, then check if box-sizing: border-box is absent
  const flexOneRe = /style="([^"]*)"/gi;
  let m;
  while ((m = flexOneRe.exec(html)) !== null) {
    const style = m[1];
    if (/flex\s*:\s*1(?:\s|;|$)/.test(style) && !/box-sizing\s*:\s*border-box/i.test(style)) {
      issues.push(fmtWarn(file, 'PF-02',
        'flex:1 div without box-sizing:border-box \u2014 may cause overflow'));
      return issues; // one per file
    }
  }
  return issues;
}

function checkPF04(html, file) {
  const issues = [];
  // <img with height:100% but no max-height
  const imgRe = /<img\s[^>]*style="([^"]*)"/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const style = m[1];
    if (/height\s*:\s*100%/i.test(style) && !/max-height/i.test(style)) {
      issues.push(fmtWarn(file, 'PF-04',
        'img with height:100% without max-height \u2014 may overflow 0.5" bottom margin'));
      break;
    }
  }
  return issues;
}

function checkPF05(html, file) {
  const issues = [];
  // Non-body DIV with background: url() or background-image: url()
  // Skip <body ...> lines. Look for <div with url() in background.
  const divBgRe = /<div\s[^>]*style="[^"]*background(?:-image)?\s*:\s*[^"]*url\s*\(/gi;
  if (divBgRe.test(html)) {
    issues.push(fmtError(file, 'PF-05',
      'non-body div with background url() \u2014 may fail in html2pptx conversion'));
  }
  return issues;
}

function checkPF06(html, file) {
  const issues = [];
  // Flex container with <img> child but missing overflow:hidden
  // Heuristic: find display:flex divs, check if they contain <img, and lack overflow:hidden
  const flexDivRe = /<div\s[^>]*style="([^"]*display\s*:\s*flex[^"]*)"/gi;
  let m;
  while ((m = flexDivRe.exec(html)) !== null) {
    const style = m[1];
    const afterDiv = html.substring(m.index, m.index + 1500);
    // Check if there's an <img within the next ~1500 chars (same container)
    if (/<img\s/i.test(afterDiv) && !/overflow\s*:\s*hidden/i.test(style)) {
      issues.push(fmtWarn(file, 'PF-06',
        'flex container with img child missing overflow:hidden \u2014 image may overflow'));
      return issues; // one per file
    }
  }
  return issues;
}

function checkPF07(html, file) {
  const issues = [];
  // <p>, <h1>-<h6>, <li> with background or border in inline style
  const tagRe = /<(p|h[1-6]|li)\s[^>]*style="([^"]*)"/gi;
  let m;
  while ((m = tagRe.exec(html)) !== null) {
    const tag = m[1].toLowerCase();
    const style = m[2];
    if (/(?:^|;\s*)(?:background|border)\s*:/i.test(style)) {
      issues.push(fmtError(file, 'PF-07',
        `<${tag}> with background/border style \u2014 wrap in <div> for html2pptx`));
    }
  }
  return issues;
}

function checkPF12(html, file) {
  const issues = [];
  for (const m of html.matchAll(FLAG_EMOJI_RE)) {
    issues.push(fmtError(file, 'PF-12',
      `Flag emoji "${m[0]}" found — PowerPoint renders as text codes. Use <img> PNG instead [IL-26]`));
  }
  return issues;
}

// parse an inline-style length (anchored so border-width / line-height / max-width don't false-match)
function pf13Len(style, prop) {
  const re = new RegExp('(?:^|[;\\s])' + prop + '\\s*:\\s*([0-9.]+)\\s*(px|pt|em|rem|%|in|cm|mm|vw|vh)?', 'i');
  const mm = style.match(re);
  if (!mm) return null;
  return { val: parseFloat(mm[1]), unit: (mm[2] || 'px').toLowerCase() };
}

function checkPF13(html, file) {
  const issues = [];
  // IL-25: border-radius: 50% + border combo (donut/circle chart trick).
  // Verified by COM render (2026-06-15): a SQUARE element with border-radius:50% renders as a
  // perfect circle in PPTX (roundRect adj clamps at 50% → square+50% = clean circle), so the
  // designer's intent is fully preserved → NOT a defect. Only NON-SQUARE border-radius:50%
  // renders as a pill/stadium (≠ intended ellipse) → real defect. Square cases (e.g. timeline
  // dot markers) were the sole PF-13 GT and were a baked-in false positive.
  const styleRe = /style="([^"]*)"/gi;
  let m;
  while ((m = styleRe.exec(html)) !== null) {
    const style = m[1];
    if (/border-radius\s*:\s*50%/i.test(style) && /(?:^|;\s*)border\s*:/i.test(style)) {
      const w = pf13Len(style, 'width');
      const h = pf13Len(style, 'height');
      if (w && h && w.unit === h.unit && h.val > 0) {
        const ratio = w.val / h.val;
        if (ratio >= 0.95 && ratio <= 1.05) continue; // square → clean circle, intent preserved
      }
      // non-square OR dimensions unverifiable → keep ERROR (conservative, recall-preserving)
      issues.push(fmtError(file, 'PF-13',
        'non-square border-radius:50% + border — renders as pill/stadium in PPTX, not an ellipse; use PNG image [IL-25]'));
      return issues; // one per file
    }
  }
  return issues;
}

function checkPF14(html, file) {
  const issues = [];
  // IL-24: <div> with background child div followed by direct sibling <span>
  // Problematic: <div><div style="background:..."></div><span>text</span></div>
  // Safe: <div><div style="background:..."></div><p><span>text</span></p></div>
  // Detect: </div> followed by whitespace then <span> (not inside <p>)
  const patternRe = /<div\s[^>]*style="[^"]*background[^"]*"[^>]*>\s*<\/div>\s*<span[\s>]/gi;
  if (patternRe.test(html)) {
    issues.push(fmtWarn(file, 'PF-14',
      'Background div followed by sibling <span> — span text will be lost in PPTX, use <p> instead [IL-24]'));
  }
  return issues;
}

function checkPF15(html, file) {
  // PF-15 비활성(2026-06-15 COM 직접판정, s3004 등 3xxx 10장 전수 FP). 정적 휴리스틱("3+컬럼 grid +
  // CJK + >7.5pt = overflow 우려")이 컬럼 실폭·텍스트량을 못 봐 안 넘치는 카드도 발화. 실측 CJK
  // overflow 는 PF-23(--full Playwright scrollWidth 초과)이 정확히 커버 → 정적 예측 폐기.
  void html; void file;
  return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // IL-27: 3+ column CSS grid with CJK text > 7.5pt
  const gridRe = /style="([^"]*grid-template-columns\s*:[^"]*)"/gi;
  let m;
  while ((m = gridRe.exec(html)) !== null) {
    const style = m[1];
    // Count columns: split grid-template-columns value by whitespace tokens
    const colMatch = style.match(/grid-template-columns\s*:\s*([^;"]+)/i);
    if (!colMatch) continue;
    const colValue = colMatch[1].trim();
    // Handle repeat() shorthand: repeat(4, 1fr) → 4 columns
    const repeatMatch = colValue.match(/repeat\(\s*(\d+)/);
    let colCount;
    if (repeatMatch) {
      colCount = parseInt(repeatMatch[1], 10);
    } else {
      const colTokens = colValue.split(/\s+/).filter(t => t && !t.startsWith('/'));
      colCount = colTokens.length;
    }
    if (colCount < 3) continue;

    // Check surrounding context (~2000 chars) for CJK text with font-size > 7.5pt
    const afterIdx = m.index;
    const region = html.substring(afterIdx, afterIdx + 3000);
    if (!CJK_RE.test(region)) continue;

    // Look for font-size declarations in this region
    const fontSizeRe = /font-size\s*:\s*([\d.]+)\s*(pt|px)/gi;
    let fs;
    while ((fs = fontSizeRe.exec(region)) !== null) {
      let size = parseFloat(fs[1]);
      if (fs[2].toLowerCase() === 'px') size = size * 0.75; // px→pt
      if (size > 7.5 && CJK_RE.test(region.substring(fs.index, fs.index + 500))) {
        issues.push(fmtWarn(file, 'PF-15',
          `${colCount}-column grid with CJK text at ${size}pt (>7.5pt) — may overflow in PPTX [IL-27]`));
        return issues; // one per file
      }
    }
  }
  return issues;
}

function checkPF16(html, file) {
  const issues = [];
  // IL-07: background image on body without text-shadow on text elements
  // Check both inline style on <body> and <style> block for body { background: url(...) }
  const bodyBgInline = /<body[^>]*style="[^"]*background[^"]*url\s*\(/i.test(html);
  const bodyBgStyle = /body\s*\{[^}]*background[^}]*url\s*\(/i.test(html);
  if (!bodyBgInline && !bodyBgStyle) return issues;

  // Body has background image — check if text elements have text-shadow
  // Look for text-bearing elements (h1-h6, p, span, div with text) without text-shadow
  const textElRe = /<(h[1-6]|p)\s[^>]*style="([^"]*)"/gi;
  let m;
  let hasTextWithoutShadow = false;
  while ((m = textElRe.exec(html)) !== null) {
    const style = m[2];
    if (!/text-shadow/i.test(style)) {
      hasTextWithoutShadow = true;
      break;
    }
  }
  if (hasTextWithoutShadow) {
    issues.push(fmtWarn(file, 'PF-16',
      'Background image slide has text elements without text-shadow — readability issue in PPTX [IL-07]'));
  }
  return issues;
}

function checkPF17(html, file) {
  const issues = [];
  // Unsupported CSS transforms (scale, skew, perspective — only rotate is supported)
  const transformRe = /transform\s*:\s*([^;"]+)/gi;
  let m;
  while ((m = transformRe.exec(html)) !== null) {
    const val = m[1];
    // Check for unsupported transform functions (translate is OK — used for centering)
    if (/(?:scale\w*|skew\w*|perspective|matrix\w*)\s*\(/i.test(val)) {
      const fnMatch = val.match(/(scale\w*|skew\w*|perspective|matrix\w*)\s*\(/i);
      issues.push(fmtWarn(file, 'PF-17',
        `Unsupported CSS transform "${fnMatch[1]}()" — only rotate is supported in PPTX conversion`));
      return issues; // one per file
    }
  }
  return issues;
}

// Allowed fonts that are available in PowerPoint or embedded
const ALLOWED_FONTS_STATIC = [
  'pretendard', 'segoe ui', 'arial', 'helvetica', 'sans-serif', 'serif',
  'times new roman', 'courier new', 'monospace', 'calibri', 'cambria',
  'noto sans kr', 'noto sans', 'malgun gothic', 'gulim', 'dotum',
  'biz udpgothic', 'meiryo', 'yu gothic', 'ms pgothic',
  'inherit', 'initial', 'unset',
  // CSS system font keywords — gracefully fall back in all environments
  '-apple-system', 'blinkmacsystemfont', 'system-ui', 'ui-sans-serif',
  'ui-serif', 'ui-monospace', 'ui-rounded',
];

// PF-19 동적 확장: vendored woff2 = 임베드 가능 = PowerPoint Arial fallback 없음 → allow-list 자동 확장.
// "JetBrainsMono-Bold.woff2" → family "JetBrainsMono" → {"jetbrainsmono", "jetbrains mono"} 둘 다 등록.
function scanVendoredFonts() {
  const families = new Set();
  try {
    const fontsDir = path.resolve(PF_DIR, '..', 'design-system', 'fonts', 'files');
    for (const f of fs.readdirSync(fontsDir)) {
      if (!f.toLowerCase().endsWith('.woff2')) continue;
      const family = f.replace(/\.woff2$/i, '').split('-')[0];
      families.add(family.toLowerCase());
      const spaced = family.replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase();
      if (spaced !== family.toLowerCase()) families.add(spaced);
    }
  } catch (_) { /* fonts dir 없으면 static allow-list 만 사용 */ }
  return families;
}
const VENDORED_FONTS = scanVendoredFonts();

// PF-19 var(--font-*) resolve: colors_and_type.css :root 의 첫 폰트로 환원 후 검사.
// "--font-mono: \"JetBrains Mono\", ..." → map["--font-mono"] = "jetbrains mono".
function resolveCssVarFonts() {
  const map = new Map();
  try {
    const cssPath = path.resolve(PF_DIR, '..', 'design-system', 'colors_and_type.css');
    const css = fs.readFileSync(cssPath, 'utf8');
    const re = /--font-([\w-]+)\s*:\s*([^;]+);/g;
    let m;
    while ((m = re.exec(css)) !== null) {
      const first = m[2].split(',')[0].trim().replace(/^["']|["']$/g, '').toLowerCase();
      map.set(`--font-${m[1]}`, first);
    }
  } catch (_) { /* css 없으면 var() 는 그대로 경고 */ }
  return map;
}
const CSS_VAR_FONTS = resolveCssVarFonts();

// allow-list = static + vendored 단순스캔 + CSS 변수의 실제 폰트값.
// ★vendored 카멜분해는 단어경계 오차 가능("JetBrainsMono"→"jet brains mono") → CSS 가 선언한
//   실제 패밀리명("jetbrains mono")을 SSOT 로 함께 포함해 var() resolve 결과와 일치 보장.
const ALLOWED_FONTS = new Set([...ALLOWED_FONTS_STATIC, ...VENDORED_FONTS, ...CSS_VAR_FONTS.values()]);

function checkPF19(html, file) {
  const issues = [];
  // Font availability: check font-family declarations against allowed list.
  // 정지 문자에 개행·중괄호 추가 — <style> 블록 내 다중 선언 오매칭 방지.
  const fontRe = /font-family\s*:\s*([^;"\n}]+)/gi;
  let m;
  while ((m = fontRe.exec(html)) !== null) {
    // var(--font-*) 선언은 fallback 인자·따옴표(var(--x, "Y") 형) 포함 가능 → fontRe 가 따옴표에서
    // 잘려 "var(--font-serif" 로 오발(stress-c6 slide-07/08). m[1] 전체서 var 토큰 인라인 추출·환원 우선.
    const varInline = m[1].match(/var\(\s*(--font-[\w-]+)/i);
    if (varInline) {
      const resolved = CSS_VAR_FONTS.get(varInline[1]);
      if (resolved && ALLOWED_FONTS.has(resolved)) continue; // CSS 토큰 환원=allow → 이 선언 통과
    }
    const fonts = m[1].split(',').map(f => f.trim().replace(/['"]/g, '').toLowerCase());
    for (let font of fonts) {
      if (!font) continue;
      // var(--font-xxx) → colors_and_type.css 정의된 실제 패밀리로 환원 후 검사.
      const varMatch = font.match(/^var\((--font-[\w-]+)\)$/i);
      if (varMatch) {
        const resolved = CSS_VAR_FONTS.get(varMatch[1]);
        if (resolved) {
          font = resolved;
        } else {
          issues.push(fmtWarn(file, 'PF-19',
            `CSS variable "${varMatch[1]}" not found in colors_and_type.css — cannot verify font availability`));
          return issues;
        }
      }
      if (ALLOWED_FONTS.has(font)) continue;
      issues.push(fmtWarn(file, 'PF-19',
        `Font "${font}" may not be available in PowerPoint — will fallback to Arial`));
      return issues; // one per file
    }
  }
  return issues;
}

// CSS properties that html2pptx cannot convert
const UNSUPPORTED_CSS_RE = /(?:backdrop-filter|clip-path|mask-image|filter\s*:\s*(?!none)(?:blur|brightness|contrast|drop-shadow|grayscale|hue-rotate|invert|saturate|sepia)|writing-mode\s*:\s*vertical|animation\s*:|@keyframes)\s*/i;

function checkPF22(html, file) {
  const issues = [];
  const styleRe = /style="([^"]*)"/gi;
  let m;
  while ((m = styleRe.exec(html)) !== null) {
    const style = m[1];
    const unsupported = style.match(UNSUPPORTED_CSS_RE);
    if (unsupported) {
      const prop = unsupported[0].trim().replace(/\s*:\s*$/, '');
      issues.push(fmtWarn(file, 'PF-22',
        `Unsupported CSS property "${prop}" — will be ignored in PPTX conversion`));
      return issues; // one per file
    }
    // box-shadow: inset — html2pptx ignores inset shadows
    if (/box-shadow\s*:[^;]*\binset\b/i.test(style)) {
      issues.push(fmtWarn(file, 'PF-22',
        `box-shadow: inset — inset shadows ignored in PPTX, only outer shadows supported`));
      return issues;
    }
  }
  // Also check <style> blocks
  const styleBlockRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  while ((m = styleBlockRe.exec(html)) !== null) {
    const block = m[1];
    const unsupported = block.match(UNSUPPORTED_CSS_RE);
    if (unsupported) {
      const prop = unsupported[0].trim().replace(/\s*:\s*$/, '');
      issues.push(fmtWarn(file, 'PF-22',
        `Unsupported CSS property "${prop}" in <style> block — will be ignored in PPTX conversion`));
      return issues;
    }
    if (/box-shadow\s*:[^;]*\binset\b/i.test(block)) {
      issues.push(fmtWarn(file, 'PF-22',
        `box-shadow: inset in <style> — inset shadows ignored in PPTX`));
      return issues;
    }
  }
  return issues;
}

function checkPF25(html, file) {
  // PF-25 는 --full computed 로 이전(runPlaywrightChecks 내 smallFontIssues).
  // 정적 정규식(inline font-size 스캔)은 ① CSS 클래스 폰트크기를 못 보고 ② 작은 글씨의 요소역할
  // (출처/범례/차트축/티커 = 의도된 보조정보)을 못 봐 전수 FP였다(2026-06-15 subagent COM 전수판정,
  // 발화 61→정적게이트 35 잔존 전부 클래스없는 inline 9pt 차트라벨/카드, 본문<10pt TP 0). computed
  // 실측 font-size + ancestor 역할판정(차트/표/svg/aux 클래스 제외)으로 본문영역 <10pt 만 ERROR.
  void html; void file;
  return [];
}

function checkPF27(html, file) {
  // PF-27 비활성(2026-06-15 COM 직접판정, s2008 점유율막대·카드 전수 1줄 완전표시 FP, s8030 "1pt
  // width"=flex/auto 측정오류). 정적 "좁은 컨테이너+CJK+nowrap없음=wrap 우려" 예측이 컨테이너 실제
  // 텍스트 fit 을 못 봐 안 wrap 하는 배지도 발화 — PF-15 와 동일 정적 한계. 실측 wrap 은 PF-65(셀)·
  // PF-23(CJK overflow, --full scrollWidth)이 정확히 커버 → 정적 예측 폐기.
  void html; void file;
  return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // CJK badge/label nowrap check: elements with explicit small width + CJK text without nowrap
  // Pattern: style="...width: Xpt..." containing CJK text without white-space: nowrap
  const styleBlockRe = /style="([^"]*)"/gi;
  let m;
  const violations = [];
  while ((m = styleBlockRe.exec(html)) !== null) {
    const style = m[1];
    // Check if element has explicit small width (< 150pt)
    const widthMatch = style.match(/(?:^|;\s*)width\s*:\s*([\d.]+)\s*pt/i);
    if (!widthMatch) continue;
    const width = parseFloat(widthMatch[1]);
    if (width >= 150) continue;
    // Check if it has nowrap already
    if (/white-space\s*:\s*nowrap/i.test(style)) continue;
    // Check surrounding context for CJK text (look only 100 characters ahead to reduce FPs)
    const pos = m.index;
    const nearby = html.substring(pos, Math.min(pos + 100, html.length));
    if (CJK_RE.test(nearby)) {
      violations.push(width);
    }
  }
  if (violations.length > 0) {
    const unique = [...new Set(violations)].sort((a, b) => a - b);
    issues.push(fmtWarn(file, 'PF-27',
      `CJK text in narrow container (${unique.join('pt, ')}pt width) without white-space:nowrap — may wrap in PPTX [IL-34]`));
  }
  return issues;
}

function checkPF28(html, file) {
  // PF-28 은 --full computed 로 이전(runPlaywrightChecks 내 overflowText). 정적 word-equiv 밀도
  // 카운트(5x5/6x6)는 표 셀·숫자 토큰 과대계수 + "밀도=결함" 단정 → 잘 정리된 IR 덱에서 전수 FP
  // (2026-06-15 subagent COM 전수판정, 84→정적게이트 61 잔존 전부 본문카드 FP). 실측 scrollHeight
  // 세로 넘침(고정높이 박스를 텍스트가 넘쳐 잘림)만 ERROR. body=PF-03, hidden clip=PF-66, 셀=PF-65.
  return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // Word count per slide: > 80 words WARN, > 120 ERROR (5x5/6x6 Rule, BCG principle)
  // Strip HTML tags, then count words
  // Extract body content only (ignore head/title/meta)
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  const bodyContent = bodyMatch ? bodyMatch[1] : html;
  const textOnly = bodyContent.replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<(figcaption|small)\b[\s\S]*?<\/\1>/gi, '')
    .replace(/<(\w+)[^>]*class="[^"]*\b(source|caption|footnote|footer)\b[^"]*"[\s\S]*?<\/\1>/gi, '')
    // \uD45C \uC140\u00B7\uCC28\uD2B8 \uB370\uC774\uD130 \uC81C\uC678(\uC774\uBBF8\uC9C0\uC9C1\uC811\uD310\uC815 2026-06-15, subagent: \uBC1C\uD65484 \uC804\uBD80 FP \u2014 \uD45C/\uCE74\uB4DC/\uBD88\uB9BF\uB85C
    // \uC815\uB9AC\uB3FC \uB118\uCE680\uC778\uB370 word-equiv\uAC00 \uD45C \uC140\u00B7\uC22B\uC790\uB97C \uACFC\uB300\uACC4\uC218). 6x6 Rule \uC740 \uBCF8\uBB38 \uD14D\uC2A4\uD2B8 \uBC00\uB3C4\uC6A9\uC774\uC9C0
    // \uD45C\u00B7\uB370\uC774\uD130 \uC2DC\uAC01\uD654 \uB300\uC0C1 \uC544\uB2D8 \u2192 <table>/<svg>(\uCC28\uD2B8) \uC81C\uAC70 \uD6C4 \uBCF8\uBB38\uB9CC \uCE74\uC6B4\uD2B8.
    .replace(/<table\b[\s\S]*?<\/table>/gi, ' ')
    .replace(/<svg\b[\s\S]*?<\/svg>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  // Count: CJK characters count as 1 word each, Latin words split by space
  const cjkChars = (textOnly.match(/[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/g) || []).length;
  // For word count: split non-CJK text by spaces, filter empties.
  // \uC21C\uC218 \uC22B\uC790/\uD37C\uC13C\uD2B8/\uD1B5\uD654/\uB2E8\uC704 \uD1A0\uD070(36.8%, 2,000, $1.5B \uB4F1)\uC740 \uB370\uC774\uD130\uAC12\uC774\uC9C0 '\uB2E8\uC5B4' \uC544\uB2D8 \u2192 \uC81C\uC678.
  const nonCjk = textOnly.replace(/[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/g, ' ');
  const latinWords = nonCjk.split(/\s+/).filter(w => w.length > 0 && !/^[\d.,%+\-/$~()]+[bmtkBMTK%]?$/.test(w)).length;
  // CJK: roughly 2 characters = 1 "word equivalent" for density
  const wordEquiv = latinWords + Math.ceil(cjkChars / 2);
  if (wordEquiv > 120) {
    issues.push(fmtError(file, 'PF-28',
      `Slide has ~${wordEquiv} word equivalents (max 120) — split content across slides [6x6 Rule]`));
  } else if (wordEquiv > 80) {
    issues.push(fmtWarn(file, 'PF-28',
      `Slide has ~${wordEquiv} word equivalents (recommend ≤80) — consider reducing text [5x5 Rule]`));
  }
  return issues;
}

function checkPF29(html, file) {
  const issues = [];
  // Image alt text check: <img> without alt or with alt="" (WCAG, Grackle, MS)
  const imgRe = /<img\b([^>]*)>/gi;
  let m;
  let missing = 0;
  while ((m = imgRe.exec(html)) !== null) {
    const attrs = m[1];
    // Skip tiny decorative images (icons)
    if (/width\s*[:=]\s*["']?\d{1,2}(px|pt)/i.test(attrs)) continue;
    // Check for alt attribute
    const altMatch = attrs.match(/\balt\s*=\s*"([^"]*)"/i);
    if (!altMatch || altMatch[1].trim() === '') {
      missing++;
    }
  }
  if (missing > 0) {
    issues.push(fmtWarn(file, 'PF-29',
      `${missing} image(s) missing alt text — add descriptive alt for accessibility [WCAG]`));
  }
  return issues;
}

function checkPF30(html, file) {
  const issues = [];
  // Font hierarchy inversion: title (h1/h2) font-size ≤ body (p/div/li) font-size
  let titleSize = 0;
  let bodyMaxSize = 0;

  // Find h1/h2 font sizes
  const titleRe = /<h[12][^>]*style="[^"]*font-size\s*:\s*([\d.]+)\s*(pt|px)/gi;
  let m;
  while ((m = titleRe.exec(html)) !== null) {
    let size = parseFloat(m[1]);
    if (m[2].toLowerCase() === 'px') size = size * 0.75;
    if (size > titleSize) titleSize = size;
  }

  // Find body text font sizes (p, li). 강조 숫자/지표값(metric-value 카드 대형숫자)은 본문 아닌 데이터
  // 강조라 제외(2026-06-15 COM 직접판정, s3004/3011/3016 카드 숫자 232,000 등이 제목보다 커서 계층역전
  // 오판 FP). 여는 태그 직후 텍스트가 숫자·통화·%·단위 위주 또는 짧으면(≤6자) 강조값으로 보고 skip.
  const bodyRe = /<(?:p|li)\b[^>]*style="[^"]*font-size\s*:\s*([\d.]+)\s*(pt|px)[^"]*"[^>]*>([^<]*)/gi;
  while ((m = bodyRe.exec(html)) !== null) {
    let size = parseFloat(m[1]);
    if (m[2].toLowerCase() === 'px') size = size * 0.75;
    const inner = (m[3] || '').replace(/&[a-z]+;/gi, '').trim();
    if (/^[\d.,%+\-/$~()원조억만달러x\s]*$/i.test(inner) || inner.length <= 6) continue;
    if (size > bodyMaxSize) bodyMaxSize = size;
  }

  if (titleSize > 0 && bodyMaxSize > 0 && titleSize <= bodyMaxSize) {
    issues.push(fmtWarn(file, 'PF-30',
      `Font hierarchy inversion: title ${titleSize.toFixed(1)}pt ≤ body ${bodyMaxSize.toFixed(1)}pt — title should be larger [2502.15412]`));
  }
  return issues;
}

// PF-31: Inline <span> inside heading/paragraph causes extra line breaks in PPTX [IL-45]
function checkPF34(html, file) {
  const issues = [];
  // Match <h1>...<span ...>...</span>...</h1> where text exists both before and inside span
  // This pattern causes PPTX converter to split span into separate paragraph
  const textElRe = /<(h[1-6]|p)\b[^>]*>([\s\S]*?)<\/\1>/gi;
  let m;
  while ((m = textElRe.exec(html)) !== null) {
    const tag = m[1];
    const content = m[2];
    // Check if content has text + <span> + text (mixed inline content)
    // Skip if span wraps entire content (no split issue)
    const spanRe = /<span\b[^>]*(?:style|class)[^>]*>/gi;
    const spans = content.match(spanRe);
    if (!spans) continue;
    // Check if there's text content outside spans
    const textOutsideSpans = content
      .replace(/<span\b[\s\S]*?<\/span>/gi, '')
      .replace(/<br\s*\/?>/gi, '')
      .replace(/<[^>]+>/g, '')
      .replace(/\s+/g, '')
      .trim();
    if (textOutsideSpans.length > 0 && spans.length > 0) {
      // 검증(실제 PPTX): html2pptx는 인라인 <span>을 런(run)으로 변환 → 단락 분리/줄 추가 없음.
      // 따라서 줄바꿈을 실제로 유발하는 block 계열(display:block/flex/grid) span만 발화한다.
      const blockSpans = content.match(
        /<span\b[^>]*style="[^"]*display\s*:\s*(?:block|flex|grid)[^"]*"[^>]*>/gi
      ) || [];
      if (blockSpans.length === 0) continue; // 인라인 전용 → PPTX에서 런으로 안전, FP 제외
      // Count expected line increase
      const brCount = (content.match(/<br\s*\/?>/gi) || []).length;
      const htmlLines = brCount + 1;
      const pptxLines = htmlLines + blockSpans.length; // block span 경계마다 줄 추가
      issues.push(fmtError(file, 'PF-34',
        `<${tag}> has block-level <span> with mixed text — PPTX will add ${blockSpans.length} extra line(s) (${htmlLines}→${pptxLines} lines). Use separate <p> elements instead [IL-45]`));
    }
  }
  return issues;
}

// PF-32: <li> + ::before/::after pseudo-element — PPTX ignores pseudo-elements [IL-44]
function checkPF35(html, file) {
  // PF-35 비활성(2026-06-15 subagent COM 전수판정 FP): ::before/::after bullet 은 PPTX 변환이 표준
  // bullet(·)로 정상 치환하고 위치오류 0(s4010 SWOT 확인). "position error" 전제 거짓.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  const hasLi = /<li\b/i.test(html);
  const hasPseudo = /::(?:before|after)\s*\{/i.test(html);
  if (hasLi && hasPseudo) {
    issues.push(fmtError(file, 'PF-35',
      `<li> with ::before/::after pseudo-element — PPTX ignores pseudo-elements, causing position errors. Use <p> + inline bullet character instead [IL-44]`));
  }
  return issues;
}

// PF-33: background: rgba() on any element — creates opaque shape covering text in PPTX [IL-43]
function checkPF36(html, file) {
  // PF-36 비활성(2026-06-15 subagent COM 전수판정 FP, 19발 최대 노이즈원): 변환 파이프라인이 rgba 알파
  // 배경을 정상 렌더(다크카드·틴트·오버레이 전부 텍스트 가림 0, s6001 표지 PPTX 확인). "ANY alpha→
  // opaque" 전제 거짓. 불투명화로 실제 대비역전(가림) 생기면 실측 PF-71(--full 대비)이 정확히 잡음.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // Extract CSS from <style> blocks
  const styleRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  let styleMatch;
  while ((styleMatch = styleRe.exec(html)) !== null) {
    const css = styleMatch[1];
    // Find background: rgba(...) or background-color: rgba(...)
    const bgRgbaRe = /background(?:-color)?\s*:\s*rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)/gi;
    let bgMatch;
    while ((bgMatch = bgRgbaRe.exec(css)) !== null) {
      const alpha = parseFloat(bgMatch[4]);
      if (alpha > 0 && alpha < 1.0) {
        issues.push(fmtError(file, 'PF-36',
          `background: rgba(${bgMatch[1]},${bgMatch[2]},${bgMatch[3]},${bgMatch[4]}) — PPTX converts ANY alpha to opaque shape. Use solid hex: blend with parent color [IL-43]`));
      }
    }
  }
  // Also check inline styles
  const inlineRe = /style="[^"]*background(?:-color)?\s*:\s*rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)/gi;
  let inlineMatch;
  while ((inlineMatch = inlineRe.exec(html)) !== null) {
    const alpha = parseFloat(inlineMatch[4]);
    if (alpha > 0 && alpha < 1.0) {
      issues.push(fmtError(file, 'PF-36',
        `Inline background: rgba(${inlineMatch[1]},${inlineMatch[2]},${inlineMatch[3]},${inlineMatch[4]}) — PPTX converts ANY alpha to opaque shape. Use solid hex [IL-43]`));
    }
  }
  return issues;
}

/**
 * PF-37: CSS border-triangle detection (IL-28)
 * border-top/bottom/left/right + transparent → white block in PPTX
 */
function checkPF37(html, file) {
  const issues = [];
  const allCss = [];
  // Collect CSS from <style> blocks
  const styleRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  let m;
  while ((m = styleRe.exec(html)) !== null) allCss.push(m[1]);
  // Collect inline styles
  const inlineRe = /style="([^"]*)"/gi;
  while ((m = inlineRe.exec(html)) !== null) allCss.push(m[1]);

  for (const css of allCss) {
    // Check for border-side with transparent
    const borderTransRe = /border-(top|bottom|left|right)\s*:\s*[^;]*transparent/gi;
    let bm;
    while ((bm = borderTransRe.exec(css)) !== null) {
      issues.push(fmtError(file, 'PF-37',
        `border-${bm[1]}: ...transparent — CSS triangle trick renders as white block in PPTX. Use rect shapes or SVG instead [IL-28]`));
      break; // one per CSS block is enough
    }
  }
  return issues;
}

/**
 * PF-38: text-decoration: underline detection (IL-38)
 * Underline position is distorted in PPTX
 */
function checkPF38(html, file) {
  const issues = [];
  const re = /text-decoration(?:-line)?\s*:\s*[^;]*underline/gi;
  if (re.test(html)) {
    issues.push(fmtError(file, 'PF-38',
      `text-decoration: underline — position distorted in PPTX. Use color or font-weight:700 for emphasis instead [IL-38]`));
  }
  return issues;
}

/**
 * PF-39: Non-body div with background-image: linear-gradient (IL-39)
 * Converts to solid rectangle covering content in PPTX
 */
function checkPF39(html, file) {
  const issues = [];
  // Check inline styles on non-body elements
  const inlineGradRe = /<(?!body\b)(\w+)[^>]*style="[^"]*background-image\s*:\s*linear-gradient\([^"]*"/gi;
  let m;
  while ((m = inlineGradRe.exec(html)) !== null) {
    issues.push(fmtError(file, 'PF-39',
      `<${m[1]}> background-image: linear-gradient() — slides use solid hex only (design-system rule); gradient belongs in the editor app. Use solid background or rasterized PNG [IL-39]`));
  }
  // Check <style> blocks for non-body selectors with background-image: linear-gradient
  const styleRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  while ((m = styleRe.exec(html)) !== null) {
    const css = m[1].replace(/\/\*[\s\S]*?\*\//g, ''); // CSS 주석 제거 — 주석이 selector 로 오인되는 것 방지
    // Match CSS rules: selector { ... background-image: linear-gradient ... }
    const ruleRe = /([^{}]+)\{([^}]*background-image\s*:\s*linear-gradient[^}]*)\}/gi;
    let rm;
    while ((rm = ruleRe.exec(css)) !== null) {
      const selector = rm[1].trim();
      // Skip body/html selectors
      if (/^(body|html)\s*$/i.test(selector)) continue;
      issues.push(fmtError(file, 'PF-39',
        `CSS "${selector}" background-image: linear-gradient() — slides use solid hex only (design-system rule); gradient belongs in the editor app. Use solid background or rasterized PNG [IL-39]`));
    }
  }
  return issues;
}

/**
 * PF-40: AI-generated infographic image detection (IL-31)
 * Images in assets/ with chart/graph/data keywords likely contain fake data
 */
/**
 * PF-41: letter-spacing detection
 * html2pptx ignores letter-spacing — text width differs in PPTX
 */
function checkPF41(html, file) {
  // PF-41 비활성(2026-06-15 subagent COM 전수판정 FP): letter-spacing 무시는 글자 폭만 좁아질 뿐
  // 가독성·레이아웃 무영향(s2018 "BUY" 배지 등 확인). 룰 본문도 "accept width difference" 자인.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  const re = /letter-spacing\s*:\s*(-?[\d.]+)\s*(pt|px)/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    let val = Math.abs(parseFloat(m[1]));
    if (m[2].toLowerCase() === 'px') val = val * 0.75; // px→pt
    if (val > 1) {
      issues.push(fmtWarn(file, 'PF-41',
        `letter-spacing: ${m[1]}${m[2]} — ignored in PPTX (>±1pt threshold). Remove or accept width difference [IL-46]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-42: opacity on non-body elements
 * html2pptx ignores standalone opacity CSS — element renders fully opaque in PPTX
 */
function checkPF42(html, file) {
  const issues = [];
  // Check inline styles for opacity (not inside rgba)
  const styleRe = /style="([^"]*)"/gi;
  let m;
  while ((m = styleRe.exec(html)) !== null) {
    const style = m[1];
    // Match standalone opacity property (not inside rgba/hsla)
    const opacityMatch = style.match(/(?:^|;\s*)opacity\s*:\s*([\d.]+)/i);
    if (!opacityMatch) continue;
    const val = parseFloat(opacityMatch[1]);
    if (val < 1.0) {
      // Check it's not on body
      const tagBefore = html.substring(Math.max(0, m.index - 30), m.index);
      if (/<body\b/i.test(tagBefore)) continue;
      issues.push(fmtWarn(file, 'PF-42',
        `opacity: ${val} — ignored in PPTX, element will be fully opaque. Use rgba() background or remove [IL-47]`));
      return issues;
    }
  }
  // Also check <style> blocks
  const styleBlockRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  while ((m = styleBlockRe.exec(html)) !== null) {
    const css = m[1];
    const opacityMatch = css.match(/(?:^|;\s*|{\s*)opacity\s*:\s*([\d.]+)/i);
    if (opacityMatch) {
      const val = parseFloat(opacityMatch[1]);
      if (val < 1.0) {
        issues.push(fmtWarn(file, 'PF-42',
          `opacity: ${val} in <style> — ignored in PPTX, element will be fully opaque [IL-47]`));
        return issues;
      }
    }
  }
  return issues;
}

/**
 * PF-43: object-fit on img — cover is required, fill/scale-down/none are errors
 * html2pptx uses sizing:'cover' — fill stretches, scale-down/none may distort
 */
function checkPF43(html, file) {
  const issues = [];
  // Detect fill/scale-down (distortion risk)
  const reBad = /object-fit\s*:\s*(fill|scale-down)/gi;
  let m;
  while ((m = reBad.exec(html)) !== null) {
    issues.push(fmtError(file, 'PF-43',
      `object-fit: ${m[1]} — will distort image aspect ratio. Use object-fit: cover instead`));
  }
  // Detect images without object-fit (stretch risk)
  const imgRe = /<img[^>]+style="([^"]*)"[^>]*>/gi;
  let im;
  while ((im = imgRe.exec(html)) !== null) {
    const style = im[1];
    if (!/object-fit/i.test(style) && /width\s*:/i.test(style) && /height\s*:/i.test(style)) {
      issues.push(fmtError(file, 'PF-43',
        `Image with explicit width+height but no object-fit — add object-fit: cover to prevent distortion`));
    }
  }
  return issues;
}

/**
 * PF-44: outline property (not none/0)
 * html2pptx ignores outline completely — use border instead
 */
function checkPF44(html, file) {
  const issues = [];
  const re = /(?:^|;\s*)outline\s*:\s*([^;"]+)/gi;
  const allCss = [];
  // Collect inline styles
  let m;
  const inlineRe = /style="([^"]*)"/gi;
  while ((m = inlineRe.exec(html)) !== null) allCss.push(m[1]);
  // Collect <style> blocks
  const styleBlockRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  while ((m = styleBlockRe.exec(html)) !== null) allCss.push(m[1]);

  for (const css of allCss) {
    const outlineRe = /(?:^|;\s*)outline\s*:\s*([^;"]+)/gi;
    let om;
    while ((om = outlineRe.exec(css)) !== null) {
      const val = om[1].trim().toLowerCase();
      if (val === 'none' || val === '0' || val === '0px' || val === '0pt') continue;
      issues.push(fmtWarn(file, 'PF-44',
        `outline: ${val} — ignored in PPTX. Use border instead [IL-49]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-45: Negative margins (≤ -5pt)
 * PPTX shape positioning may differ with large negative margins
 */
function checkPF45(html, file) {
  // PF-45 비활성(2026-06-15 subagent COM 전수판정 FP): negative margin 위치가 PPTX서 정상(s5013 타임라인
  // dot 선 위 정위치, 카드 정렬 동일). positioning 차이 0. 실제 요소 겹침은 실측 PF-18 이 잡음.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  const re = /margin(?:-(?:top|bottom|left|right))?\s*:\s*(-[\d.]+)\s*(pt|px)/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    let val = parseFloat(m[1]);
    if (m[2].toLowerCase() === 'px') val = val * 0.75; // px→pt
    if (val <= -5) {
      issues.push(fmtWarn(file, 'PF-45',
        `Negative margin ${m[1]}${m[2]} — PPTX shape positioning may differ. Consider absolute positioning [IL-50]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-46: text-indent
 * html2pptx does not extract text-indent — first-line indent ignored in PPTX
 */
function checkPF46(html, file) {
  const issues = [];
  const re = /text-indent\s*:\s*(-?[\d.]+)\s*(?:pt|px|em)/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const val = parseFloat(m[1]);
    if (val !== 0) {
      issues.push(fmtWarn(file, 'PF-46',
        `${m[0].match(/text-indent\s*:\s*[^;]+/)[0]} — ignored in PPTX. Use padding-left instead [IL-51]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-47: word-break: break-all / overflow-wrap: break-word
 * PPTX ignores these — line break positions differ
 */
function checkPF47(html, file) {
  // PF-47 비활성(2026-06-15 subagent COM 전수판정 FP): word-break:break-all 은 텍스트가 실제 overflow
  // 할 때만 발동하는데 s8030 등 단어중간 끊김·넘침 0. 실측 overflow 는 PF-03/23/66 이 잡음.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  if (/word-break\s*:\s*break-all/i.test(html)) {
    issues.push(fmtWarn(file, 'PF-47',
      `word-break: break-all — ignored in PPTX, line breaks will differ. Verify text fits [IL-52]`));
  }
  return issues;
}

/**
 * PF-48: column-count / columns (multi-column layout)
 * html2pptx does not support CSS columns — renders as single column
 */
function checkPF48(html, file) {
  const issues = [];
  // Avoid matching grid-template-columns by requiring word boundary before 'column-count'/'columns'
  const re = /(?<![a-z-])(?:column-count|columns)\s*:\s*(\d+)/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const count = parseInt(m[1], 10);
    if (count >= 2) {
      issues.push(fmtError(file, 'PF-48',
        `column-count: ${count} — CSS columns not supported in PPTX, will render as single column. Use CSS grid or flex instead [IL-53]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-49: mix-blend-mode (non-normal)
 * PPTX ignores blend modes — visual effect lost
 */
function checkPF49(html, file) {
  const issues = [];
  const re = /mix-blend-mode\s*:\s*(\w[\w-]*)/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    if (m[1].toLowerCase() !== 'normal') {
      issues.push(fmtWarn(file, 'PF-49',
        `mix-blend-mode: ${m[1]} — ignored in PPTX, visual effect will be lost [IL-54]`));
      return issues;
    }
  }
  return issues;
}

/**
 * PF-50: border-image / border-image-source
 * PPTX does not support image/gradient borders
 */
function checkPF50(html, file) {
  const issues = [];
  if (/border-image(?:-source)?\s*:\s*(?!none)/i.test(html)) {
    issues.push(fmtWarn(file, 'PF-50',
      `border-image — not supported in PPTX, border will be missing. Use solid border instead [IL-55]`));
  }
  return issues;
}

/**
 * PF-51: position: sticky
 * PPTX treats sticky as absolute — positioning differs
 */
function checkPF51(html, file) {
  const issues = [];
  if (/position\s*:\s*sticky/i.test(html)) {
    issues.push(fmtWarn(file, 'PF-51',
      `position: sticky — treated as absolute in PPTX, positioning will differ [IL-56]`));
  }
  return issues;
}

/**
 * PF-52: @font-face custom font
 * PPTX falls back to system fonts — layout may change
 */
function checkPF52(html, file) {
  const issues = [];
  if (/@font-face\s*\{/i.test(html)) {
    issues.push(fmtWarn(file, 'PF-52',
      `@font-face custom font — PPTX uses system fonts, layout may change [IL-57]`));
  }
  return issues;
}

/**
 * PF-53: direction: rtl
 * PPTX may not respect text direction
 */
function checkPF53(html, file) {
  const issues = [];
  if (/direction\s*:\s*rtl/i.test(html)) {
    issues.push(fmtWarn(file, 'PF-53',
      `direction: rtl — PPTX may not respect RTL text direction [IL-58]`));
  }
  return issues;
}

/**
 * PF-54: white-space: pre / pre-line
 * PPTX whitespace handling differs
 */
function checkPF54(html, file) {
  const issues = [];
  if (/white-space\s*:\s*pre(?:-line)?(?:\s|;|"|$)/i.test(html)) {
    // Skip white-space: pre-wrap (commonly used and less problematic)
    const match = html.match(/white-space\s*:\s*(pre(?:-line)?)(?:\s|;|"|$)/i);
    if (match) {
      issues.push(fmtWarn(file, 'PF-54',
        `white-space: ${match[1]} — PPTX whitespace/line-break handling may differ [IL-59]`));
    }
  }
  return issues;
}

/**
 * PF-55: Inline <span> with background inside text elements
 * html2pptx strips span backgrounds → text becomes invisible on parent bg
 */
function checkPF55(html, file) {
  const issues = [];
  // Match <span with background/background-color in style attribute
  const spanBgRe = /<span\b[^>]*style="[^"]*background(?:-color)?\s*:\s*(?!none|transparent)[^"]*"[^>]*>/gi;
  let m;
  while ((m = spanBgRe.exec(html)) !== null) {
    const tag = m[0];
    // Check if this span also has a contrasting text color (the dangerous pattern)
    const colorMatch = tag.match(/(?<!-)color\s*:\s*(#[0-9A-Fa-f]{3,8}|rgba?\([^)]+\)|[a-z]+)/i);
    const bgMatch = tag.match(/background(?:-color)?\s*:\s*(#[0-9A-Fa-f]{3,8}|rgba?\([^)]+\)|[a-z]+)/i);
    if (bgMatch) {
      const msg = colorMatch
        ? `<span> with background:${bgMatch[1]} + color:${colorMatch[1]} — PPTX strips span background, text color remains on parent bg → may become invisible. Use parent div background or text-only styling [IL-60]`
        : `<span> with background:${bgMatch[1]} — PPTX strips span background. Move background to parent <div> [IL-60]`;
      issues.push(fmtError(file, 'PF-55', msg));
    }
  }
  return issues;
}

function checkPF40(html, file) {
  const issues = [];
  const BANNED_KEYWORDS = /chart|graph|table|data|infographic|calendar|spreadsheet|timeline|diagram|funnel|waterfall|donut|pie|heatmap/i;

  const imgRe = /<img\b([^>]*)>/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const attrs = m[1];
    const srcMatch = attrs.match(/src\s*=\s*["']([^"']+)/i);
    if (!srcMatch) continue;
    const src = srcMatch[1];
    // Only check assets/ images (AI-generated), skip external URLs and SVGs
    if (!/assets\//i.test(src)) continue;
    if (/\.svg$/i.test(src)) continue;

    const filename = src.split('/').pop().toLowerCase();
    const altMatch = attrs.match(/alt\s*=\s*["']([^"']*)/i);
    const alt = altMatch ? altMatch[1] : '';

    const filenameHit = filename.match(BANNED_KEYWORDS);
    const altHit = alt.match(BANNED_KEYWORDS);

    if (filenameHit || altHit) {
      const keyword = (filenameHit || altHit)[0];
      issues.push(fmtWarn(file, 'PF-40',
        `AI image "${src}" may contain fake ${keyword} data — use HTML/CSS or PPTX native chart instead [IL-31]`));
    }
  }
  return issues;
}

/**
 * PF-58: Image src points to non-existent file in assets/
 * Catches filename mismatches between HTML and actual asset files
 */
function checkPF58(html, file, slidesDir) {
  const issues = [];
  const imgRe = /<img\b([^>]*)>/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const attrs = m[1];
    const srcMatch = attrs.match(/src\s*=\s*["']([^"']+)/i);
    if (!srcMatch) continue;
    const src = srcMatch[1];
    // Only check local assets/ paths, skip URLs
    if (/^https?:\/\//i.test(src)) continue;
    if (!slidesDir) continue;
    const filePath = path.join(slidesDir, src);
    if (!fs.existsSync(filePath)) {
      issues.push(fmtError(file, 'PF-58',
        `Image file not found: "${src}" — check filename matches actual asset [IL-64]`));
    }
  }
  return issues;
}

/**
 * PF-59: flex:1 + overflow:hidden container with tall fixed-height children
 * Content at the top may be clipped when align-items:flex-end pushes content down
 */
function checkPF59(html, file) {
  const issues = [];
  // Find flex:1 containers with overflow:hidden and flex-direction:column (or default)
  // Then check if they contain children with large fixed heights
  const containerRe = /style\s*=\s*"([^"]*flex:\s*1[^"]*overflow:\s*hidden[^"]*)"/gi;
  let m;
  while ((m = containerRe.exec(html)) !== null) {
    const style = m[1];
    // Only check column-direction flex containers (bar charts, vertical layouts)
    // Skip row-direction (default) as height clipping is less common
    if (!/flex-direction:\s*column/i.test(style) && !/align-items:\s*flex-end/i.test(style)) continue;
    // Look at the content after this container opening for fixed heights
    const after = html.substring(m.index, Math.min(m.index + 2000, html.length));
    const heightMatches = [...after.matchAll(/height:\s*(\d+(?:\.\d+)?)pt/gi)];
    if (heightMatches.length === 0) continue;
    const maxHeight = Math.max(...heightMatches.map(h => parseFloat(h[1])));
    if (maxHeight > 90) {
      issues.push(fmtWarn(file, 'PF-59',
        `flex:1 + overflow:hidden container has child with height ${maxHeight}pt — content may be clipped at top [IL-65]`));
    }
  }
  return issues;
}

/**
 * PF-60: Badge/decoration div text color invisible against parent background [IL-66]
 * Small divs (border-radius:50% or width/height ≤40pt) with text — PPTX may not
 * transfer the badge's background to the text shape, so text color must contrast
 * against the PARENT container's background, not just the badge's own background.
 */
function checkPF60(html, file) {
  // PF-60 비활성(2026-06-15 subagent COM 전수판정 사실상 FP): 배지 fill 은 PPTX서 정상 렌더+텍스트 선명
  // (s3003/3009 초록배지 흰텍스트 확인). "fill 미렌더→invisible" 거짓 + 부모배경 오귀속(배지는 흰슬라이드
  // 위). 브랜드컬러 저대비는 accent 약한정탐이고 실측 PF-71(--full 대비)이 배지 텍스트까지 커버.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // Find badge divs with border-radius:50% AND a background color AND containing text
  // The badge must have its own background (colored circle) to be relevant
  const badgeRe = /<div\b[^>]*style\s*=\s*"([^"]*border-radius:\s*50%[^"]*)"\s*>\s*<(?:p|h[1-6])\b[^>]*style\s*=\s*"([^"]*color:\s*(#[0-9A-Fa-f]{3,8})[^"]*)"/gi;
  let m;
  while ((m = badgeRe.exec(html)) !== null) {
    const divStyle = m[1];
    const textColor = m[3].toUpperCase();
    // Badge must have its own background color
    const badgeBgMatch = divStyle.match(/background(?:-color)?:\s*(#[0-9A-Fa-f]{3,8})/i);
    if (!badgeBgMatch) continue;
    const pos = m.index;
    // Find the nearest ancestor div with a background color (the parent card/container)
    const before = html.substring(Math.max(0, pos - 1500), pos);
    const parentBgs = [...before.matchAll(/background(?:-color)?:\s*(#[0-9A-Fa-f]{3,8})/gi)];
    if (parentBgs.length === 0) continue;
    const parentBg = parentBgs[parentBgs.length - 1][1].toUpperCase();
    // Calculate contrast of text against PARENT background (not badge background)
    const ratio = contrastRatio(textColor, parentBg);
    if (ratio < 3.0) {
      issues.push(fmtWarn(file, 'PF-60',
        `Badge text "${textColor}" on parent background "${parentBg}" — contrast ${ratio.toFixed(1)}:1 < 3:1. PPTX may not render badge fill → text invisible [IL-66]`));
    }
  }
  return issues;
}

// Helper for PF-60: WCAG contrast ratio calculation
function contrastRatio(hex1, hex2) {
  function hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    return [parseInt(hex.slice(0,2),16), parseInt(hex.slice(2,4),16), parseInt(hex.slice(4,6),16)];
  }
  function luminance(rgb) {
    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
  const l1 = luminance(hexToRgb(hex1));
  const l2 = luminance(hexToRgb(hex2));
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

/**
 * PF-62: conic-gradient / radial-gradient — PPTX cannot render these CSS functions
 * conic-gradient: completely lost (donut charts disappear) → ERROR
 * radial-gradient: may render as solid color → WARN
 */
function checkPF62(html, file) {
  const issues = [];
  // Check inline styles
  const inlineConicRe = /<(\w+)[^>]*style="[^"]*conic-gradient\s*\([^"]*"/gi;
  let m;
  while ((m = inlineConicRe.exec(html)) !== null) {
    issues.push(fmtError(file, 'PF-62',
      `<${m[1]}> uses conic-gradient() — completely lost in PPTX. Replace with horizontal bar chart (div+width%) or table [IL-70]`));
  }
  const inlineRadialRe = /<(?!body\b)(\w+)[^>]*style="[^"]*radial-gradient\s*\([^"]*"/gi;
  while ((m = inlineRadialRe.exec(html)) !== null) {
    issues.push(fmtWarn(file, 'PF-62',
      `<${m[1]}> uses radial-gradient() — may render as solid color in PPTX. Consider solid background or PNG [IL-70]`));
  }
  // Check <style> blocks
  const styleRe = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  while ((m = styleRe.exec(html)) !== null) {
    const css = m[1];
    if (/conic-gradient/i.test(css)) {
      const selectorRe = /([^{}]+)\{[^}]*conic-gradient\s*\([^}]*\}/gi;
      let rm;
      while ((rm = selectorRe.exec(css)) !== null) {
        issues.push(fmtError(file, 'PF-62',
          `CSS "${rm[1].trim()}" uses conic-gradient() — completely lost in PPTX. Replace with bar chart [IL-70]`));
      }
    }
    if (/radial-gradient/i.test(css)) {
      const selectorRe = /([^{}]+)\{[^}]*radial-gradient\s*\([^}]*\}/gi;
      let rm;
      while ((rm = selectorRe.exec(css)) !== null) {
        const sel = rm[1].trim();
        if (/^(body|html)\s*$/i.test(sel)) continue;
        issues.push(fmtWarn(file, 'PF-62',
          `CSS "${sel}" uses radial-gradient() — may render as solid color in PPTX [IL-70]`));
      }
    }
  }
  return issues;
}

/**
 * PF-63: HTML <table> usage — PPTX conversion loses table structure
 * html2pptx cannot convert HTML tables; they render as plain text or disappear entirely.
 * Detected from 3-round PF/VC gap test: slide-02 VC ERROR (CC=1,TF=1,LM=1).
 */
function checkPF63(html, file) {
  const issues = [];
  // Match <table> tags (case-insensitive), but exclude <table> inside comments
  const commentless = html.replace(/<!--[\s\S]*?-->/g, '');
  const tableRe = /<table\b/gi;
  let m;
  while ((m = tableRe.exec(commentless)) !== null) {
    issues.push(fmtError(file, 'PF-63',
      `<table> element detected — PPTX conversion cannot render HTML tables. Use div-based grid layout instead`));
  }
  return issues;
}

/**
 * PF-64: flex-wrap pill/badge layout — many small items with flex-wrap
 * When multiple small divs are arranged with flex-wrap, PPTX conversion fails
 * because html2pptx positions each item independently and they overlap.
 * Detected from 3-round PF/VC gap test: slide-16 VC ERROR (CC=1,TF=1).
 *
 * Detection: container with display:flex + flex-wrap:wrap containing 4+ child elements
 * with small explicit widths or inline-block-like sizing.
 */
function checkPF64(html, file) {
  // PF-64 비활성(2026-06-15 subagent COM 전수판정 FP): flex-wrap pill 컨테이너가 PPTX서 한 줄 정상정렬
  // (s3003 5 pill 겹침·오정렬 0). "may overlap" 미발생. 실제 요소 겹침은 실측 PF-18 이 잡음.
  void html; void file; return [];
  // eslint-disable-next-line no-unreachable
  const issues = [];
  // Step 1: Find div openings with style attributes
  const divOpenRe = /<div\b[^>]*style\s*=\s*"([^"]*)"[^>]*>/gi;
  let m;
  while ((m = divOpenRe.exec(html)) !== null) {
    const style = m[1];
    if (!/display:\s*flex/i.test(style)) continue;
    if (!/flex-wrap:\s*wrap/i.test(style)) continue;

    // Step 2: Find matching </div> using depth counting
    let depth = 1;
    let pos = m.index + m[0].length;
    let endPos = -1;
    while (pos < html.length && depth > 0) {
      const nextOpen = html.indexOf('<div', pos);
      const nextClose = html.indexOf('</div>', pos);
      if (nextClose === -1) break;
      if (nextOpen !== -1 && nextOpen < nextClose) {
        depth++;
        pos = nextOpen + 4;
      } else {
        depth--;
        if (depth === 0) { endPos = nextClose; break; }
        pos = nextClose + 6;
      }
    }
    if (endPos === -1) continue;
    const inner = html.slice(m.index + m[0].length, endPos);

    // Step 3: Count child divs/spans with pill-like styling
    const childRe = /<(?:div|span)\b[^>]*style\s*=\s*"([^"]*)"/gi;
    let childCount = 0;
    let pillCount = 0;
    let cm;
    while ((cm = childRe.exec(inner)) !== null) {
      childCount++;
      const cStyle = cm[1];
      if (/border-radius/i.test(cStyle) || /padding:\s*\d+px\s+\d+px/i.test(cStyle)) {
        pillCount++;
      }
    }
    if (childCount >= 4 && pillCount >= 2) {
      issues.push(fmtWarn(file, 'PF-64',
        `flex-wrap container with ${childCount} pill/badge children — PPTX conversion may overlap or misalign items. Use fixed grid layout instead`));
    }
  }
  return issues;
}

/**
 * PF-56: Image container with flex centering but missing explicit height
 * flex align-items:center without height causes container to collapse → centering has no effect
 */
function checkPF56(html, file) {
  const issues = [];
  // Find <img> tags with assets/ src (project images)
  const imgRe = /<img\b[^>]*src\s*=\s*["'](?:assets\/[^"']+)["'][^>]*>/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const imgPos = m.index;
    // Look for the closest parent div/element with flex + align-items:center
    // Search backwards from img position for style containing align-items
    const before = html.substring(Math.max(0, imgPos - 800), imgPos);
    // Find the innermost opening div/element before this img
    const parentDivs = [...before.matchAll(/<(?:div|section)\b([^>]*)>/gi)];
    if (parentDivs.length === 0) continue;
    const closestParent = parentDivs[parentDivs.length - 1];
    const parentAttrs = closestParent[1];
    // Check inline style
    const styleMatch = parentAttrs.match(/style\s*=\s*["']([^"']+)/i);
    if (!styleMatch) continue;
    const style = styleMatch[1];
    // Must have flex centering
    const hasFlex = /display\s*:\s*flex/i.test(style);
    const hasAlignCenter = /align-items\s*:\s*center/i.test(style);
    if (!hasFlex || !hasAlignCenter) continue;
    // Check if height is set (height:100%, height:NNpt, etc.)
    const hasHeight = /(?:^|;)\s*height\s*:/i.test(style);
    if (!hasHeight) {
      // Also check if it might be in a CSS class (check <style> block)
      // Extract class if any
      const classMatch = parentAttrs.match(/class\s*=\s*["']([^"']+)/i);
      let heightInClass = false;
      if (classMatch) {
        const className = classMatch[1].trim().split(/\s+/)[0];
        const classRe = new RegExp(`\\.${className}\\s*\\{([^}]+)\\}`, 'i');
        const classBody = html.match(classRe);
        if (classBody && /height\s*:/i.test(classBody[1])) {
          heightInClass = true;
        }
      }
      if (!heightInClass) {
        const src = (m[0].match(/src=["']([^"']+)/i) || [])[1] || 'unknown';
        issues.push(fmtWarn(file, 'PF-56',
          `Image container has flex centering but no explicit height — vertical centering will not work (img: ${src})`));
      }
    }
  }
  return issues;
}

/**
 * PF-57: Image too small relative to its container
 * Detects images with max-width/width < 30% of slide width (720pt) in split layouts
 */
function checkPF57(html, file) {
  const issues = [];
  const imgRe = /<img\b([^>]*)>/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const attrs = m[1];
    const srcMatch = attrs.match(/src\s*=\s*["']([^"']+)/i);
    if (!srcMatch) continue;
    const src = srcMatch[1];
    if (!/assets\//i.test(src)) continue; // only project images

    // Extract image dimensions from inline style or attributes
    const styleMatch = attrs.match(/style\s*=\s*["']([^"']+)/i);
    const style = styleMatch ? styleMatch[1] : '';

    // Get width/max-width in pt
    let imgWidth = null;
    const widthStyle = style.match(/(?:max-)?width\s*:\s*([\d.]+)\s*pt/i);
    const widthAttr = attrs.match(/width\s*=\s*["']?([\d.]+)/i);
    if (widthStyle) imgWidth = parseFloat(widthStyle[1]);
    else if (widthAttr) imgWidth = parseFloat(widthAttr[1]);

    let imgHeight = null;
    const heightStyle = style.match(/(?:max-)?height\s*:\s*([\d.]+)\s*pt/i);
    if (heightStyle) imgHeight = parseFloat(heightStyle[1]);

    // If image has explicit small dimensions
    if (imgWidth !== null && imgWidth < 100) {
      issues.push(fmtWarn(file, 'PF-57',
        `Image "${src}" width=${imgWidth}pt is very small (<100pt) — content may be hard to see`));
    } else if (imgHeight !== null && imgHeight < 80 && imgWidth === null) {
      issues.push(fmtWarn(file, 'PF-57',
        `Image "${src}" height=${imgHeight}pt is very small (<80pt) — content may be hard to see`));
    }
  }
  return issues;
}

/**
 * PF-70: Image Integration Quality — validates that images in slides follow
 * media-guide.md rules: proper size, no opacity tricks, object-fit:cover,
 * border-radius, meaningful alt text.
 * Catches: watermark-style images, invisible/tiny decorative images, missing alt.
 */
function checkPF70(html, file) {
  const issues = [];
  // Skip cover/background slides (full-bleed images are valid)
  if (/class\s*=\s*["'](cover-bg|bg-img)["']/i.test(html)) return issues;

  const imgRe = /<img\b([^>]*)>/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const attrs = m[1];
    const srcMatch = attrs.match(/src\s*=\s*["']([^"']+)/i);
    if (!srcMatch) continue;
    const src = srcMatch[1];
    if (!/assets\//i.test(src)) continue;

    const styleMatch = attrs.match(/style\s*=\s*["']([^"']+)/i);
    const style = styleMatch ? styleMatch[1] : '';

    const imgIdx = m.index;
    const before = html.substring(Math.max(0, imgIdx - 300), imgIdx);
    // 디자인 시스템 이미지 클래스 판정(이미지 직접판정 2026-06-15, subagent 발화25 전부 FP·TP0):
    // PF-70 정적 inline 검사는 CSS 클래스로 object-fit/크기/border-radius 를 스타일하는 디자인 시스템을
    // "inline 누락"으로 오판한다(realmix 25장 렌더 왜곡·잘림 0). 이미지 컨테이너 클래스(bg/hero/cover/
    // image/img/visual/photo/media 류)가 있으면 디자인 시스템이 스타일 처리 → inline 형식 검사 면제.
    const imgCls = (attrs.match(/class\s*=\s*["']([^"']+)/i) || [])[1] || '';
    const ctxCls = (imgCls + ' ' + [...before.matchAll(/class\s*=\s*["']([^"']+)["']/gi)].map(x => x[1]).join(' ')).toLowerCase();
    const isBgImg = /\b(bg|background|hero|cover|full-?bleed)[-_a-z]*/.test(ctxCls);
    const isDesignImg = isBgImg || /\b(image|img|visual|photo|picture|thumb|media|icon)[-_a-z]*/.test(ctxCls);

    // Check parent container for opacity — 단 배경 이미지는 흐림(opacity 저하)이 디자인 의도 → 면제
    const opacityMatch = before.match(/opacity\s*:\s*([\d.]+)/i);
    if (!isBgImg && opacityMatch) {
      const opacity = parseFloat(opacityMatch[1]);
      if (opacity < 0.5) {
        issues.push(fmtError(file, 'PF-70',
          `Image "${src}" has opacity ${opacity} (<0.5) — watermark-style images are not valid design. Use opacity >= 0.5 or remove.`));
      }
    }
    // 디자인 시스템 이미지 = CSS 클래스로 스타일 → inline 형식 검사(object-fit/border-radius/alt/pt) 면제
    if (isDesignImg) continue;

    // Check for object-fit: cover (contain leaves gaps, fill distorts)
    if (!/object-fit\s*:\s*cover/i.test(style)) {
      issues.push(fmtError(file, 'PF-70',
        `Image "${src}" missing object-fit:cover — required to prevent distortion (contain/fill forbidden)`));
    }

    // Check for border-radius
    if (!/border-radius/i.test(style)) {
      issues.push(fmtWarn(file, 'PF-70',
        `Image "${src}" missing border-radius — media-guide requires border-radius:8pt`));
    }

    // Check for meaningful alt text
    const altMatch = attrs.match(/alt\s*=\s*["']([^"']*)/i);
    if (!altMatch || altMatch[1].trim() === '') {
      issues.push(fmtWarn(file, 'PF-70',
        `Image "${src}" has empty alt text — add descriptive alt for accessibility`));
    }

    // Check explicit pt dimensions exist (flex-only sizing forbidden per media-guide)
    const widthMatch = style.match(/(?:max-)?width\s*:\s*([\d.]+)\s*pt/i);
    const heightMatch = style.match(/(?:max-)?height\s*:\s*([\d.]+)\s*pt/i);

    if (!widthMatch || !heightMatch) {
      issues.push(fmtError(file, 'PF-70',
        `Image "${src}" missing explicit pt dimensions — must specify width:Npt and height:Npt in inline style (flex-only sizing forbidden)`));
    } else {
      const w = parseFloat(widthMatch[1]);
      const h = parseFloat(heightMatch[1]);

      // Minimum dimensions: width >= 260pt, height >= 180pt (slide area 1/4 principle)
      if (w < 260) {
        issues.push(fmtError(file, 'PF-70',
          `Image "${src}" width=${w}pt is too small (<260pt) — media-guide minimum for 1/4 slide coverage`));
      }
      if (h < 180) {
        issues.push(fmtError(file, 'PF-70',
          `Image "${src}" height=${h}pt is too small (<180pt) — media-guide minimum for 1/4 slide coverage`));
      }
    }
  }
  return issues;
}

// PF-76: diagonal arrow glyphs (↖↗↘↙ etc.) — PPTX font fallback breaks them [A8/학습⑪]
function checkPF76(html, file) {
  const issues = [];
  // 가시 텍스트만 스캔 (style/script/태그 제거 → CSS·속성값 매칭 FP 차단)
  const text = html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<[^>]+>/g, ' ');
  const diag = text.match(/[↖↗↘↙⬈⬉⬊⬋⤡⤢]/g);
  if (diag && diag.length) {
    const uniq = [...new Set(diag)].join(' ');
    issues.push(fmtError(file, 'PF-76',
      `Diagonal arrow glyph(s) "${uniq}" in text — PPTX font fallback breaks these. Use orthogonal → ↑ ← ↓ or a CSS border+rotate shape [학습⑪]`));
  }
  return issues;
}

// 정적 검사 전 비렌더 영역(주석) 제거 — HTML 주석·<style> 내 CSS 주석은 렌더되지 않으므로
// 태그/속성 존재 스캔(PF-63 <table>, PF-22 clip-path 등)에서 주석 내 문자열 매칭 = false positive.
// (anchor: stress-c1 사이클1 — slide-01 PF-63 / slide-02·09 PF-22 주석-FP)
function stripComments(rawHtml) {
  let h = rawHtml.replace(/<!--[\s\S]*?-->/g, '');           // HTML 주석
  h = h.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, (block) => // <style> 내 CSS 주석만
    block.replace(/\/\*[\s\S]*?\*\//g, ''));
  return h;
}

function runStaticChecks(rawHtml, file) {
  const html = stripComments(rawHtml);
  return [
    // PF-01 removed (subsumed by PF-39 + PF-62)
    ...checkPF02(html, file),
    ...checkPF04(html, file),
    ...checkPF05(html, file),
    ...checkPF06(html, file),
    ...checkPF07(html, file),
    ...checkPF12(html, file),
    ...checkPF13(html, file),
    ...checkPF14(html, file),
    ...checkPF15(html, file),
    ...checkPF16(html, file),
    ...checkPF17(html, file),
    ...checkPF19(html, file),
    ...checkPF22(html, file),
    ...checkPF25(html, file),
    ...checkPF27(html, file),
    ...checkPF28(html, file),
    ...checkPF29(html, file),
    ...checkPF30(html, file),
    ...checkPF34(html, file),
    ...checkPF35(html, file),
    ...checkPF36(html, file),
    ...checkPF37(html, file),
    ...checkPF38(html, file),
    ...checkPF39(html, file),
    ...checkPF40(html, file),
    ...checkPF41(html, file),
    ...checkPF42(html, file),
    ...checkPF43(html, file),
    ...checkPF44(html, file),
    ...checkPF45(html, file),
    ...checkPF46(html, file),
    ...checkPF47(html, file),
    ...checkPF48(html, file),
    ...checkPF49(html, file),
    ...checkPF50(html, file),
    ...checkPF51(html, file),
    ...checkPF52(html, file),
    ...checkPF53(html, file),
    ...checkPF54(html, file),
    ...checkPF55(html, file),
    ...checkPF56(html, file),
    ...checkPF57(html, file),
    ...checkPF59(html, file),
    ...checkPF60(html, file),
    ...checkPF62(html, file),
    ...checkPF63(html, file),
    ...checkPF64(html, file),
    ...checkPF70(html, file),
    ...checkPF76(html, file),
  ];
}

// ── Playwright checks (Phase 2) ─────────────────────────────────────────────

async function runPlaywrightChecks(slidesDir, files) {
  const { chromium } = await import('playwright');
  const browser = await chromium.launch({ headless: true });
  const results = [];
  // A-02: Reuse a single page instead of newPage()/close() per file
  const page = await browser.newPage({ viewport: { width: 960, height: 540 } });

  try {
    for (const file of files) {
      const filePath = path.resolve(slidesDir, file);
      const fileUrl = `file:///${filePath.replace(/\\/g, '/')}`;

      try {
        await page.goto(fileUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });

        // PF-03: overflow check
        // tolerance 8px(=6pt, 2026-06-15 COM 직접판정): realmix 6xxx 덱 12장이 일관 4px(=3pt) 초과인데
        // 표지/본문 시각 잘림 0 = 디자인시스템 미세 여백/border 오차(FP). 의미있는 잘림(s2015 28px=박스
        // 하단 잘림)만 ERROR 유지하도록 8px 여유. 진짜 콘텐츠 잘림(정탐)은 보존.
        const overflow = await page.evaluate(() => {
          const body = document.body;
          return body.scrollHeight > body.clientHeight + 8;
        });
        if (overflow) {
          results.push(fmtError(file, 'PF-03',
            'content height exceeds 405pt (body overflow) \u2014 will be clipped in PPTX'));
        }

        // PF-08: REMOVED — subsumed by PF-23 (CJK text density with precise width calculation)
        // PF-23 fires on all slides PF-08 fires on, with more precise overflow prediction.
        // PF-18: Element overlap detection (text-on-text or image-on-text)
        const overlapIssue = await page.evaluate(() => {
          const textEls = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,li,div,img'));
          const entries = textEls
            .filter(el => {
              const t = (el.textContent || '').trim();
              if (!t) return false;
              const r = el.getBoundingClientRect();
              return r.width > 0 && r.height > 0;
            })
            .map(el => {
              const r = el.getBoundingClientRect();
              const ownText = Array.from(el.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('');
              return { el, tag: el.tagName, left: r.left, top: r.top, right: r.right, bottom: r.bottom, area: r.width * r.height, ownText };
            })
            // Filter to elements with their own text content (not just inherited) or images.
            // PF-18 FP 제거(2026-06-15 COM 직접판정): ownText 없는 순수 컨테이너 DIV(차트 막대 트랙+fill
            // 레이어, 배경 박스)는 의도된 시각 레이어인데 bbox 94% 겹침으로 오판(s5006 가로막대차트 전수
            // FP). "text unreadable" 룰 취지상 글자 보유 요소 + 이미지만 겹침 대상 → ownText DIV/IMG 만.
            .filter(r => r.ownText.length > 0 || r.tag === 'IMG');

          // Check pairwise overlaps (limit to first 50 elements for performance)
          const check = entries.slice(0, 50);
          let worstError = { ratio: 0 };
          let worstWarn = { ratio: 0 };
          for (let i = 0; i < check.length; i++) {
            for (let j = i + 1; j < check.length; j++) {
              const a = check[i], b = check[j];
              // Skip DOM containment (parent-child in DOM tree)
              if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
              // Skip elements in different branches of the same flex/grid container
              let skipFlexGrid = false;
              let ancestor = a.el;
              while (ancestor.parentElement) {
                const container = ancestor.parentElement;
                const pd = getComputedStyle(container).display;
                if (/flex|grid|inline-flex|inline-grid/.test(pd)) {
                  // ancestor is a flex/grid item; if b is in the same container but different subtree, skip
                  if (!ancestor.contains(b.el) && container.contains(b.el)) { skipFlexGrid = true; break; }
                }
                ancestor = container;
              }
              if (skipFlexGrid) continue;
              // Skip bounding-box containment (one visually contains the other)
              const aContainsB = a.left <= b.left && a.right >= b.right && a.top <= b.top && a.bottom >= b.bottom;
              const bContainsA = b.left <= a.left && b.right >= a.right && b.top <= a.top && b.bottom >= a.bottom;
              if (aContainsB || bContainsA) continue;

              const overlapW = Math.min(a.right, b.right) - Math.max(a.left, b.left);
              const overlapH = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
              if (overlapW > 0 && overlapH > 0) {
                const overlapArea = overlapW * overlapH;
                const smallerArea = Math.min(a.area, b.area);
                const ratio = smallerArea > 0 ? overlapArea / smallerArea : 0;
                // Unified sibling-overlap thresholds (shared with validate-slides.js):
                //   ratio < 0.05 → skip · 0.05–0.20 → WARN · ≥0.20 → ERROR.
                // Track worst ERROR and worst WARN separately so a slide with both
                // (e.g. 43% + 10%) surfaces one of each instead of hiding the smaller.
                if (ratio >= 0.20) {
                  if (ratio > worstError.ratio) worstError = { ratio, tag1: a.tag, tag2: b.tag };
                } else if (ratio >= 0.05) {
                  if (ratio > worstWarn.ratio) worstWarn = { ratio, tag1: a.tag, tag2: b.tag };
                }
              }
            }
          }
          return {
            error: worstError.ratio >= 0.20 ? { ...worstError, pct: Math.round(worstError.ratio * 100) } : null,
            warn: worstWarn.ratio >= 0.05 ? { ...worstWarn, pct: Math.round(worstWarn.ratio * 100) } : null
          };
        });
        if (overlapIssue.error) {
          results.push(fmtError(file, 'PF-18',
            `Elements overlap: ${overlapIssue.error.tag1} and ${overlapIssue.error.tag2} (${overlapIssue.error.pct}% overlap) — text unreadable, fix layout or split slide`));
        }
        if (overlapIssue.warn) {
          results.push(fmtWarn(file, 'PF-18',
            `Elements overlap: ${overlapIssue.warn.tag1} and ${overlapIssue.warn.tag2} (${overlapIssue.warn.pct}% overlap) — may cause readability issues`));
        }

        // PF-20: Bottom margin intrusion (content in 0.5" safe zone: 369pt-405pt)
        // getBoundingClientRect returns px; convert to pt: pt = px * 0.75 (72/96)
        const marginIssue = await page.evaluate(() => {
          const allEls = document.querySelectorAll('body > *');
          let maxBottomPx = 0;
          for (const el of allEls) {
            const r = el.getBoundingClientRect();
            if (r.height <= 0) continue;
            // PF-20 개선(이미지직접확인 2026-06-15, subagent 발화 전수 FP·TP0): 하단 0.5" safe margin
            // (369-405pt) 침범 요소가 realmix 전부 출처캡션·footer형 정보박스(참여기관/실적/CTA/네비)·
            // 차트 축(baseline+axis)이었고 실제 본문 잘림은 0(>405 넘침은 PF-03이 ERROR로 커버).
            // → footer/nav/cta/차트축 + 가로넓고 얕은 밴드형(footer 컨테이너)을 의도 디자인으로 면제.
            const cls = (el.className || '').toString().toLowerCase();
            const slideW = document.body.clientWidth || 960;
            const isFooter = /source|footer|caption|footnote|credit|nav|cta|info|meta|legend|chip|tag|badge|btn|button|action|disclaimer|axis|chart|graph|plot/.test(cls)
              || r.height < 20
              || (r.width > slideW * 0.6 && r.height < 50);  // 가로 넓고 얕은 밴드형 footer/축 영역
            if (isFooter) continue;
            if (r.bottom > maxBottomPx) maxBottomPx = r.bottom;
          }
          const maxBottomPt = maxBottomPx * 0.75; // px → pt
          // 369pt = 405pt - 36pt (0.5" margin)
          return { maxBottom: Math.round(maxBottomPt * 100) / 100, inMargin: maxBottomPt > 369, overSlide: maxBottomPt > 405 };
        });
        // PF-20 비활성(이미지직접확인 2026-06-15, subagent 발화 전수 FP·TP0): 369-405pt safe margin
        // '침범'은 잘림이 아니라 권장 여백 미달일 뿐 — realmix 디자인은 하단 출처캡션·footer박스·차트축을
        // 405pt 근처에 두는 일관 컨벤션이고 실제 본문 잘림(>405 슬라이드 밖)은 0건. 실제 넘침은 PF-03이
        // ERROR로 커버하므로 safe-margin WARN 은 과민(FP 생성기) → 비활성. (overSlide=PF-03 위임 유지)
        void marginIssue;

        // PF-21: Image resolution and aspect ratio check
        const imgIssues = await page.evaluate(() => {
          const issues = [];
          const imgs = document.querySelectorAll('img');
          for (const img of imgs) {
            if (!img.naturalWidth || !img.naturalHeight) continue;
            const r = img.getBoundingClientRect();
            if (r.width < 10 || r.height < 10) continue; // skip tiny/icon images

            // Upscale check: display size > natural size × 2
            const scaleX = r.width / img.naturalWidth;
            const scaleY = r.height / img.naturalHeight;
            if (scaleX > 2.0 || scaleY > 2.0) {
              issues.push({ type: 'lowres', scale: Math.max(scaleX, scaleY).toFixed(1), src: img.src.split('/').pop() });
            }

            // Aspect ratio distortion: >5% difference between scale axes.
            // PF-21 FP 제거(2026-06-15 subagent COM 전수판정 TP 0/FP 13): object-fit cover/contain/
            // scale-down 은 브라우저가 비율을 강제 보존(crop/letterbox)하므로 박스 AR≠원본 AR 이어도
            // 렌더 픽셀 왜곡 0. distorted 검사는 fill/none/미지정일 때만 의미. (cover crop 을 왜곡으로 오판)
            const objFit = getComputedStyle(img).objectFit;
            const arPreserved = objFit === 'cover' || objFit === 'contain' || objFit === 'scale-down';
            // fill 이어도 작은 썸네일/아이콘(<64px)은 stretch 왜곡이 시각적으로 인지 불가(s7006 32px 썸네일).
            const tinyThumb = r.width < 64 || r.height < 64;
            if (!arPreserved && !tinyThumb && Math.abs(scaleX - scaleY) / Math.max(scaleX, scaleY) > 0.05) {
              issues.push({ type: 'distorted', src: img.src.split('/').pop(), scaleX: scaleX.toFixed(2), scaleY: scaleY.toFixed(2) });
            }

            // DPI estimation: display pt * 96/72 → effective pixels needed, compare with natural
            // For projection: 96 DPI minimum, so display width in inches × 96 = min pixels
            // Slide is 720pt = 10 inches, so 1pt ≈ 1/72 inch
            const displayWidthInches = r.width / 72;
            const effectiveDPI = img.naturalWidth / displayWidthInches;
            if (effectiveDPI < 72 && r.width > 50) {
              issues.push({ type: 'lowdpi', src: img.src.split('/').pop(), dpi: Math.round(effectiveDPI) });
            }
          }
          return issues;
        });
        for (const img of imgIssues) {
          if (img.type === 'lowres') {
            results.push(fmtWarn(file, 'PF-21',
              `Image "${img.src}" upscaled ${img.scale}x — will look blurry when projected`));
          } else if (img.type === 'distorted') {
            results.push(fmtWarn(file, 'PF-21',
              `Image "${img.src}" aspect ratio distorted (scaleX=${img.scaleX}, scaleY=${img.scaleY})`));
          } else if (img.type === 'lowdpi') {
            results.push(fmtWarn(file, 'PF-21',
              `Image "${img.src}" effective DPI ${img.dpi} (min 72) — will look pixelated when projected`));
          }
        }

        // PF-26: Content section density — count visible top-level content blocks
        const densityCheck = await page.evaluate(() => {
          const body = document.body;
          if (!body) return { count: 0 };
          const children = Array.from(body.children);
          let visibleBlocks = 0;
          for (const child of children) {
            const r = child.getBoundingClientRect();
            // Count only visible blocks with meaningful size (> 30px height, > 50px width)
            if (r.height > 30 && r.width > 50) {
              visibleBlocks++;
            }
          }
          return { count: visibleBlocks };
        });
        // PF-26 비활성(2026-06-15 subagent COM 전수판정 FP): 블록 수만으로는 sparse 한 섹션 divider
        // (s8029 PART9 — 5블록이나 시각상 여백 충분·깔끔)도 "과밀"로 오판. 진짜 과밀=잘림은 실측
        // PF-03(body overflow 405pt)이 잡음. 블록 수 휴리스틱은 밀도와 무관 → 비활성.
        void densityCheck;

        // PF-23: CJK text density — predict overflow with 20% width correction
        const densityIssue = await page.evaluate(() => {
          const CJK = /[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/;
          const allEls = document.querySelectorAll('div, p, span, h1, h2, h3, h4, h5, h6, li');
          for (const el of allEls) {
            const text = (el.textContent || '').trim();
            if (!text || text.length < 3) continue;
            if (!CJK.test(text)) continue;

            const r = el.getBoundingClientRect();
            if (r.width < 20) continue;

            // Calculate CJK character ratio
            const cjkChars = (text.match(/[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/g) || []).length;
            const cjkRatio = cjkChars / text.length;
            if (cjkRatio < 0.3) continue;

            // PF-23 FP 제거: scrollWidth는 이미 줄바꿈/shrink-to-fit 결과를 반영한다.
            // 잘 맞는(감싸지는) 텍스트는 scrollWidth ≈ clientWidth이라 20% 보정이 무조건 5%를 넘겨
            // 항상 오발화한다. 실제 가로 오버플로(content가 box를 넘침)일 때만 판정한다.
            // 추가 FP 제거(2026-06-15 subagent COM 전수판정 TP 0/FP 4): sub-pixel(s8012·8017 1줄 완전
            // 표시) 과 장식 워터마크 글자(s8018 "6"·s8021 "7")가 20% 보정으로 과대추정 → +4px sub-pixel
            // tolerance + 보정 임계 10% 완화. 거대 단일글자(폰트>box높이 40%)는 의도된 배경 글리프 skip.
            const fs2 = parseFloat(getComputedStyle(el).fontSize) || 14;
            if (text.length <= 2 && fs2 > r.height * 0.4) continue; // 장식 워터마크
            const realOverflow = el.scrollWidth > r.width + 4;
            // Compare scrollWidth with clientWidth, applying 20% CJK correction
            const correctedWidth = el.scrollWidth * (1 + cjkRatio * 0.2);
            if (realOverflow && correctedWidth > r.width * 1.10) { // 10% tolerance
              return {
                found: true,
                text: text.substring(0, 30),
                containerWidth: Math.round(r.width),
                correctedWidth: Math.round(correctedWidth),
                cjkRatio: Math.round(cjkRatio * 100)
              };
            }
          }
          return { found: false };
        });
        if (densityIssue.found) {
          results.push(fmtWarn(file, 'PF-23',
            `CJK text "${densityIssue.text}..." (${densityIssue.cjkRatio}% CJK) will likely overflow in PPTX ` +
            `(corrected width ${densityIssue.correctedWidth}px > container ${densityIssue.containerWidth}px)`));
        }

        // PF-61: Image background contrast — check text readability on background images
        // Samples pixel brightness under text elements that sit on top of images
        const imgContrastIssues = await page.evaluate(() => {
          const issues = [];
          // Find text elements positioned over background images
          const textEls = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span');
          for (const el of textEls) {
            const text = (el.textContent || '').trim();
            if (!text || text.length < 2) continue;
            const cs = getComputedStyle(el);
            const textColor = cs.color;
            // Parse text color rgb
            const rgbMatch = textColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
            if (!rgbMatch) continue;
            const [tr, tg, tb] = [+rgbMatch[1], +rgbMatch[2], +rgbMatch[3]];

            // Check if any ancestor has a background-image or if there's an <img> behind this element
            let hasImageBg = false;
            let ancestor = el.parentElement;
            while (ancestor) {
              const acs = getComputedStyle(ancestor);
              if (acs.backgroundImage && acs.backgroundImage !== 'none') {
                hasImageBg = true;
                break;
              }
              ancestor = ancestor.parentElement;
            }
            // Also check for <img> siblings/cousins that might be positioned behind (absolute/relative)
            // Walk up ALL ancestors — the <img> may be a sibling of any ancestor, not just the closest positioned one
            if (!hasImageBg) {
              const elRect = el.getBoundingClientRect();
              let walk = el.parentElement;
              while (walk && walk !== document.body) {
                const imgs = walk.querySelectorAll(':scope > img');
                for (const img of imgs) {
                  const imgCs = getComputedStyle(img);
                  if (imgCs.position === 'absolute' || imgCs.position === 'fixed') {
                    const imgRect = img.getBoundingClientRect();
                    if (imgRect.left <= elRect.left && imgRect.right >= elRect.right &&
                        imgRect.top <= elRect.top && imgRect.bottom >= elRect.bottom) {
                      hasImageBg = true;
                      break;
                    }
                  }
                }
                if (hasImageBg) break;
                walk = walk.parentElement;
              }
            }
            if (!hasImageBg) continue;

            // Check if there's a solid overlay between image and text
            // Walk up from text element, check for solid background divs
            let hasOverlay = false;
            let cur = el.parentElement;
            while (cur && cur !== document.body) {
              const curCs = getComputedStyle(cur);
              const bg = curCs.backgroundColor;
              if (bg && bg !== 'transparent' && bg !== 'rgba(0, 0, 0, 0)') {
                // Parse alpha
                const rgbaM = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
                if (rgbaM) {
                  const alpha = rgbaM[4] !== undefined ? parseFloat(rgbaM[4]) : 1;
                  if (alpha >= 0.4) {
                    hasOverlay = true;
                    break;
                  }
                }
              }
              // Check opacity property on the element (used for overlays)
              const opacity = parseFloat(curCs.opacity);
              if (opacity < 1 && curCs.backgroundColor && curCs.backgroundColor !== 'transparent' && curCs.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                hasOverlay = true;
                break;
              }
              cur = cur.parentElement;
            }

            // Check text-shadow as fallback readability aid
            const hasShadow = cs.textShadow && cs.textShadow !== 'none';

            if (!hasOverlay && !hasShadow) {
              issues.push({
                text: text.substring(0, 40),
                color: `rgb(${tr},${tg},${tb})`,
                tag: el.tagName
              });
            }
          }
          return issues;
        });
        for (const issue of imgContrastIssues) {
          results.push(fmtWarn(file, 'PF-61',
            `Text "${issue.text}..." (${issue.color}) on background image without overlay or text-shadow — may be unreadable [IL-69]`));
        }

        // PF-71: 일반 텍스트 WCAG 대비 (VP-04 동등 floor 2.124) — PF-clean → VP-04-clean 보장.
        // 생성규칙: HTML이 저대비 색조합을 쓰면 변환 후 PPTX(VP-04)에서 잡힘. HTML 단계에서 막아
        // 생성 시 예방. PF-60(배지)·PF-24(흰on흰)·PF-61(이미지배경)이 못 잡는 일반 텍스트 커버.
        const lowContrastIssues = await page.evaluate(() => {
          function lum(r, g, b) { const a = [r, g, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]; }
          function cr(f, b) { const L = Math.max(lum(...f), lum(...b)), D = Math.min(lum(...f), lum(...b)); return (L + 0.05) / (D + 0.05); }
          const issues = [];
          const els = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,div,td,th,li,strong,b,em');
          for (const el of els) {
            // 직접 텍스트 노드만 (자식 요소 텍스트 중복 제외)
            const direct = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join('');
            if (!direct) continue;
            // 1자 텍스트: 장식 glyph(기호·화살표)만 제외하고 번호/문자 배지("1"~"6" 등)는 대비 검사한다.
            // VP-04 checkContrast 와 동일 패턴 — PF-clean⊇VP-clean 보장(2026-06-15 교차검증 구멍 발견:
            // s3014 번호배지 흰글씨 on 주황 1.75 대비를 VP-04 는 잡는데 PF-71 이 length<2 로 놓쳤음).
            if (direct.length === 1 && /^[+\-·•×÷/→←↑↓*=~|<>]$/.test(direct)) continue;
            const cs = getComputedStyle(el);
            const m = cs.color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/); if (!m) continue;
            const fg = [+m[1], +m[2], +m[3]];
            // 배경: ancestor chain 첫 solid bg. 이미지배경 만나면 PF-61 담당이라 skip.
            let bg = null, cur = el;
            while (cur && cur !== document.body) {
              const bcs = getComputedStyle(cur);
              if (bcs.backgroundImage && bcs.backgroundImage !== 'none') { bg = 'image'; break; }
              const bm = bcs.backgroundColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
              if (bm && (bm[4] === undefined || +bm[4] >= 0.5)) { bg = [+bm[1], +bm[2], +bm[3]]; break; }
              cur = cur.parentElement;
            }
            if (bg === 'image') continue;
            if (!bg) {
              // ancestor에서 solid bg 못 찾으면 body/html 실제 배경 사용(어두운 풀블리드 배경 s99 #1A1511
              // 같은 경우 흰글자=정상대비인데 흰 fallback이면 흰on흰 오판). body→html 순.
              for (const root of [document.body, document.documentElement]) {
                const rbg = getComputedStyle(root).backgroundColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
                if (rbg && (rbg[4] === undefined || +rbg[4] >= 0.5)) { bg = [+rbg[1], +rbg[2], +rbg[3]]; break; }
              }
              if (!bg) bg = [255, 255, 255];
            }
            const ratio = cr(fg, bg);
            if (ratio < 2.124) {
              issues.push({ text: direct.substring(0, 30), fg: `rgb(${fg.join(',')})`, bg: `rgb(${bg.join(',')})`, ratio: ratio.toFixed(2) });
            }
          }
          return issues;
        });
        for (const issue of lowContrastIssues) {
          results.push(fmtWarn(file, 'PF-71',
            `Text "${issue.text}..." (${issue.fg} on ${issue.bg}) — WCAG contrast ${issue.ratio}:1 < 2.124 (VP-04 동등). 변환 후 저대비=가독성 결함, 색 조정 필요 [IL-66]`));
        }

        // PF-25 (computed): 본문 영역 텍스트의 실측 font-size < 10pt. 정적 정규식(inline 스캔)은
        // CSS 클래스 폰트크기를 못 보고 작은 글씨의 요소역할(출처/범례/차트축/티커=의도된 보조정보)을
        // 못 봐 전수 FP였다(2026-06-15 subagent COM 전수판정, 본문<10pt TP 0). computed font-size +
        // ancestor 역할판정(svg/table/figure/aux 클래스 제외)으로 본문영역 <10pt 만 ERROR.
        const smallFontIssues = await page.evaluate(() => {
          const AUX_RE = /source|footer|caption|footnote|credit|legend|badge|label|chip|tag|pill|ticker|axis|tick|annotation|chart|graph|plot|donut|pie|treemap|disclaimer|note|meta|sub-?label|data-?label|datalabel|unit|delta|micro|fine-?print|small|kicker|eyebrow|watermark/i;
          const seen = new Set();
          const els = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,div,td,th,li,strong,b,em,a');
          for (const el of els) {
            // 직접 텍스트 노드만 (자식 텍스트 중복 제외)
            const direct = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join('');
            if (!direct || direct.length < 2) continue;
            const r = el.getBoundingClientRect();
            if (r.width <= 0 || r.height <= 0) continue;
            const cs = getComputedStyle(el);
            if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue;
            const px = parseFloat(cs.fontSize); if (!px) continue;
            const pt = px * 0.75; // px(96dpi) → pt
            // floor 정밀화(2026-06-15 6장 COM 직접판정): 8-9pt 본문 설명문·차트라벨·지표값·표숫자·도형
            // 라벨이 전수 화면상 가독(FP). 짧은 라벨/배지/값/축은 작아도 읽히고, 긴 본문도 7.5pt+ 는 읽힌다
            // → ① <7pt 극소 + ② 긴 본문문장(≥20자) 둘 다일 때만 진짜 가독성 결함(정탐)으로 잔류.
            // plan SSOT "TP=WCAG미달·잘림" 기준상 폰트 floor 자체는 약한정탐이라 보수화. CSS 10pt 환산오차도 동시 해소.
            if (pt >= 6.99) continue; // 6.99: CSS 7pt→9.333px→6.9997pt 환산오차 통과, 6pt대 이하만 잔류
            const tlen = direct.replace(/\s/g, '').length;
            if (tlen < 20) continue; // 짧은 라벨/배지/지표값/축/헤더 = 작아도 가독 OK
            // 출처/자료/주석 캡션은 클래스 없어도 보조정보(의도된 작은 글씨) → 텍스트 패턴으로 제외
            if (/^\s*(출처|자료|참고|주|source|note|ref|data|fig)\s*[:：.]/i.test(direct)) continue;
            // 차트/표/캡션 내부 = 데이터 라벨·셀·캡션(보조정보)
            if (el.closest('svg, table, figure, figcaption')) continue;
            // 자신+조상 className 에 보조정보 토큰 → 의도된 작은 글씨
            let aux = false, cur = el;
            while (cur && cur !== document.body) {
              if (AUX_RE.test((cur.className || '').toString())) { aux = true; break; }
              cur = cur.parentElement;
            }
            if (aux) continue;
            const key = Math.round(pt * 10) / 10;
            seen.add(key);
          }
          return [...seen].sort((a, b) => a - b);
        });
        if (smallFontIssues.length > 0) {
          results.push(fmtError(file, 'PF-25',
            `Body text below 10pt floor (computed): ${smallFontIssues.join('pt, ')}pt — increase to 10pt+ [IL-31]`));
        }

        // PF-28 (computed): 텍스트 컨테이너 실측 세로 넘침(scrollHeight 초과)만. 정적 word-equiv 밀도
        // 카운트는 표/숫자 과대계수 + "밀도=결함" 단정으로 전수 FP였다(COM 전수판정, 밀도 높아도 깨짐0).
        // 실제 잘림(고정높이 박스를 텍스트가 세로로 넘침)만 ERROR. body 전체=PF-03, 표/그리드 셀=PF-65.
        const overflowText = await page.evaluate(() => {
          let worst = null;
          const els = document.querySelectorAll('p,div,li,section,article,h1,h2,h3,h4,h5,h6');
          for (const el of els) {
            if (el === document.body) continue;
            const txt = (el.textContent || '').trim();
            if (txt.length < 10) continue;
            // 직접 텍스트 보유 요소만 (래퍼는 자식이 넘쳐도 자신 scrollHeight 동일 → 직접텍스트로 한정)
            const direct = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join('');
            if (direct.length < 10) continue;
            const cs = getComputedStyle(el);
            // 스크롤/자동확장 컨테이너는 잘리지 않음
            const oy = cs.overflowY, ox = cs.overflow;
            if (oy === 'auto' || oy === 'scroll' || ox === 'auto' || ox === 'scroll') continue;
            // 셀(PF-65 영역)·표 내부 제외
            if (el.tagName === 'TD' || el.tagName === 'TH' || el.closest('table')) continue;
            const over = el.scrollHeight - el.clientHeight;
            if (over > 4) { // 4px tolerance (rounding)
              if (!worst || over > worst.over) worst = { text: txt.substring(0, 30), over: Math.round(over) };
            }
          }
          return worst;
        });
        if (overflowText) {
          results.push(fmtError(file, 'PF-28',
            `Text overflows its container by ${overflowText.over}px: "${overflowText.text}..." — reduce text or enlarge box [6x6 Rule]`));
        }

        // PF-65: Table/grid cell text overflow — detect text wrapping in cells that should be single-line
        const cellOverflowIssues = await page.evaluate(() => {
          const issues = [];
          // Check CSS Grid cells and <td>/<th>
          const cells = document.querySelectorAll('td, th, [class*="st-cell"], [class*="cell"]');
          // Also check grid container direct children (common CSS table pattern)
          const gridContainers = document.querySelectorAll('[style*="grid-template-columns"]');
          const allCells = new Set(cells);
          for (const gc of gridContainers) {
            for (const child of gc.children) allCells.add(child);
          }
          // Also find grid via computed style
          const allDivs = document.querySelectorAll('div');
          for (const d of allDivs) {
            if (getComputedStyle(d).display === 'grid') {
              for (const child of d.children) allCells.add(child);
            }
          }
          for (const cell of allCells) {
            const text = (cell.textContent || '').trim();
            if (!text || text.length < 2) continue;
            const cs = getComputedStyle(cell);
            if (cs.whiteSpace === 'pre-wrap' || cs.whiteSpace === 'pre-line') continue;
            // PF-65 FP 제거(2026-06-15 subagent COM 전수판정 TP 0/FP 23): 세로축 회전 라벨(transform
            // rotate / writing-mode vertical)은 표 셀이 아닌 차트 축 라벨 → 제외(s2016 "충격도→").
            if (/rotate|matrix/.test(cs.transform) || /vertical/.test(cs.writingMode)) continue;
            const r = cell.getBoundingClientRect();
            if (r.width <= 0 || r.height <= 0) continue;
            // Horizontal overflow (scrollWidth exceeds visible width) — +4 sub-pixel tolerance
            // (s8012·8017 1줄 완전표시인데 sub-pixel 로 오발화)
            if (cell.scrollWidth > cell.clientWidth + 4) {
              issues.push({ text: text.substring(0, 30), tag: cell.tagName, type: 'scrollWidth' });
              continue;
            }
            // Line-count heuristic: short text forced into 2+ lines by narrow column
            const fontSize = parseFloat(cs.fontSize) || 14;
            const lineHeight = parseFloat(cs.lineHeight) || fontSize * 1.4;
            // PF-65 FP 제거: 셀 박스 높이는 같은 행의 다른 셀이 줄바꿈하면 함께 늘어난다(table-row stretch).
            // → 셀 박스가 아니라 '텍스트 자체'의 렌더 높이를 Range로 측정해 실제 줄 수를 구한다.
            let actualLines;
            try {
              const range = document.createRange();
              range.selectNodeContents(cell);
              const rects = Array.from(range.getClientRects());
              if (rects.length > 0) {
                const top = Math.min(...rects.map((rc) => rc.top));
                const bot = Math.max(...rects.map((rc) => rc.bottom));
                actualLines = Math.round((bot - top) / lineHeight);
              }
            } catch (e) { /* fall through to box measure */ }
            if (actualLines == null) {
              const padTop = parseFloat(cs.paddingTop) || 0;
              const padBot = parseFloat(cs.paddingBottom) || 0;
              let contentHeight = r.height - padTop - padBot;
              const cellDisplay = cs.display;
              if (cellDisplay === 'flex' || cellDisplay === 'inline-flex' || cellDisplay === 'grid') {
                const textChild = cell.querySelector('span, p, a') || cell.firstElementChild;
                if (textChild) contentHeight = textChild.getBoundingClientRect().height;
              }
              actualLines = Math.round(contentHeight / lineHeight);
            }
            // PF-65 추가개선: 셀에 블록 자식이 여럿(배지+라벨 등 의도적 세로배치)이면 wrap 이 아니다.
            // Range 는 배지 도형+라벨을 합산해 2줄로 오판하므로(slide-4007 복합셀 새 FP) 블록자식 ≤1 일 때만 발화.
            const blockKids = Array.from(cell.children).filter((c) => {
              const d = getComputedStyle(c).display;
              return d === 'block' || d === 'flex' || d === 'grid' || d === 'inline-flex';
            });
            // PF-65 FP 제거: 2줄 wrap 이어도 행 높이가 흡수해 실제 잘림(clip) 없으면 의도된 디자인이지
            // 결함 아님(s1009·8005·8015 의도된 2줄 보조값 스택). 셀 자체가 세로로 잘릴 때만(scrollHeight
            // 초과) ERROR. blockKids≤1 + 짧은 텍스트 조건 유지.
            const cellClipped = cell.scrollHeight > cell.clientHeight + 4;
            if (actualLines >= 2 && text.length <= 12 && blockKids.length <= 1 && cellClipped) {
              issues.push({ text: text.substring(0, 30), tag: cell.tagName, type: 'multiline' });
            }
          }
          return issues;
        });
        for (const issue of cellOverflowIssues) {
          results.push(fmtWarn(file, 'PF-65',
            `Table/grid cell text wraps unexpectedly: "${issue.text}" (${issue.tag}, ${issue.type}) — widen column or shorten text`));
        }

        // PF-66: overflow:hidden content clipping — detect content cut off by hidden overflow
        const clipIssues = await page.evaluate(() => {
          const issues = [];
          const allEls = document.querySelectorAll('div, section, article, li, aside, main');
          for (const el of allEls) {
            const cs = getComputedStyle(el);
            if (cs.overflow !== 'hidden' && cs.overflowY !== 'hidden') continue;
            // PF-66 FP 제거: 의도적 말줄임(ellipsis / line-clamp)은 설계된 truncation이지 사고가 아님.
            const clampVal = cs.getPropertyValue('-webkit-line-clamp');
            if (cs.textOverflow === 'ellipsis' || (clampVal && clampVal !== 'none')) continue;
            const r = el.getBoundingClientRect();
            if (r.width <= 0 || r.height <= 0) continue;
            // Vertical clipping: content taller than visible area
            if (el.scrollHeight > el.clientHeight + 2) {
              const allText = (el.textContent || '').trim();
              if (!allText) continue;
              // PF-66 FP 제거(2026-06-15 subagent COM 전수판정 TP 2/FP 12): scrollHeight 단독은 디센더
              // /box 패딩 미세오차(3~12px)와 장식 워터마크 글자를 진짜 잘림으로 오판. 진짜 정보손실은
              // "실제 본문 텍스트 자식이 컨테이너 하단을 디센더 이상 넘어 잘릴 때"만 (s8004 ④값·s8017
              // 콜아웃=TP). 잘린 본문 자식 없으면 skip.
              let clippedText = '', clippedLen = 0, clippedVis = 1;
              const children = el.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,span,div');
              for (const child of children) {
                const childTxt = (child.textContent || '').trim();
                if (!childTxt) continue;
                const cr = child.getBoundingClientRect();
                // 자식이 컨테이너 하단을 디센더 이상(>4px) 넘어 잘림
                if (cr.bottom <= r.bottom + 4) continue;
                // 장식 워터마크 skip: 짧은 글자(≤2자)가 컨테이너 높이의 40%+ 큰 폰트 = 의도된 배경 글리프
                const cfs = parseFloat(getComputedStyle(child).fontSize) || 14;
                if (childTxt.length <= 2 && cfs > r.height * 0.4) continue;
                // 자식이 컨테이너 안에서 보이는 비율(낮을수록 실제로 많이 잘림). 디센더/행높이 미세오차는
                // 자식이 거의 다 보이고(>0.65) 끝만 살짝 넘는다(s8034 셀·s8032). 진짜 잘림은 자식이 하단에
                // 걸쳐 절반↓ 만 보인다(s8004 ④행·s8017 콜아웃).
                const visRatio = (r.bottom - Math.max(cr.top, r.top)) / Math.max(1, cr.bottom - cr.top);
                // 가장 긴(본문) 잘린 자식 선택 — ④ 번호 span 같은 짧은 자식이 본문을 가리지 않게
                if (childTxt.length > clippedLen) { clippedLen = childTxt.length; clippedText = childTxt.substring(0, 30); clippedVis = visRatio; }
              }
              // 잘린 본문이 충분히 길고(>4자) 실제로 많이 잘릴 때(보이는 비율 ≤0.65)만 TP. 짧은 셀 라벨·
              // 행높이 디센더 오차(s8034·s8032)는 skip. s8004 ④값·s8017 콜아웃은 본문 길고 절반↓ 잘려 보존.
              if (!clippedText || clippedLen <= 4 || clippedVis > 0.65) continue;
              issues.push({
                clipped: Math.round(el.scrollHeight - el.clientHeight),
                text: clippedText,
                tag: el.tagName,
                cls: (el.className || '').toString().substring(0, 20)
              });
            }
          }
          return issues;
        });
        for (const issue of clipIssues) {
          results.push(fmtError(file, 'PF-66',
            `overflow:hidden clips content by ${issue.clipped}px: "${issue.text}" (${issue.tag}.${issue.cls}) — reduce content or remove overflow:hidden`));
        }

      } catch (e) {
        results.push(fmtWarn(file, 'PF-XX', `Playwright check failed: ${e.message}`));
      }
    }
  } finally {
    await page.close();
    await browser.close();
  }
  return results;
}

// ── Cross-slide consistency helpers ─────────────────────────────────────────

function stddev(arr) {
  if (arr.length < 2) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  const variance = arr.reduce((sum, v) => sum + (v - mean) ** 2, 0) / arr.length;
  return Math.sqrt(variance);
}

/** Extract metrics from HTML for cross-slide consistency checks. */
function extractSlideMetrics(html) {
  const metrics = { h1FontSize: null, h1Text: null, bodyPadding: null, usedColors: [], bodyBgBrightness: null, textColors: [] };

  // h1 font-size (inline style) and text content
  const h1Match = html.match(/<h1[^>]*style="[^"]*font-size\s*:\s*([\d.]+)\s*pt/i);
  if (h1Match) metrics.h1FontSize = parseFloat(h1Match[1]);
  const h1TextMatch = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  if (h1TextMatch) metrics.h1Text = h1TextMatch[1].replace(/<[^>]+>/g, '').trim();

  // body padding (inline style)
  const bodyMatch = html.match(/<body[^>]*style="[^"]*padding\s*:\s*([^;"]+)/i);
  if (bodyMatch) metrics.bodyPadding = bodyMatch[1].trim();

  // Collect hex colors used in inline styles only (skip href, id, class attributes)
  const styleBlocks = html.matchAll(/style="([^"]*)"/gi);
  for (const sb of styleBlocks) {
    const styleStr = sb[1];
    const colorMatches = styleStr.matchAll(/#([0-9a-fA-F]{6})(?=[;\s"',)]|$)/g);
    for (const m of colorMatches) {
      metrics.usedColors.push(m[1].toUpperCase());
    }
  }

  // Body background brightness for PF-24 — check both inline and <style> block
  const bodyBgMatch = html.match(/<body[^>]*style="[^"]*background\s*:\s*#([0-9a-fA-F]{6})/i)
    || html.match(/body\s*\{[^}]*background\s*:\s*#([0-9a-fA-F]{6})/i);
  if (bodyBgMatch) {
    const rgb = hexToRgb(bodyBgMatch[1]);
    if (rgb) metrics.bodyBgBrightness = relativeLuminance(...rgb);
  }

  // All container background colors for PF-24 (div/section/header with background)
  // Used to avoid false positives: white text on dark div is fine even if body bg is white
  metrics.containerBgColors = [];
  const styleBlockMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
  const bgRe = /background\s*:\s*#([0-9a-fA-F]{6})/gi;
  for (const sb of html.matchAll(/style="([^"]*)"/gi)) {
    let bm;
    while ((bm = bgRe.exec(sb[1])) !== null) {
      metrics.containerBgColors.push(bm[1].toUpperCase());
    }
  }
  if (styleBlockMatch) {
    let bm;
    const bgReBlock = /background\s*:\s*#([0-9a-fA-F]{6})/gi;
    while ((bm = bgReBlock.exec(styleBlockMatch[1])) !== null) {
      metrics.containerBgColors.push(bm[1].toUpperCase());
    }
  }

  // Text colors for PF-24 — check both inline styles and <style> blocks
  const textColorRe = /(?:^|;\s*)color\s*:\s*#([0-9a-fA-F]{6})/gi;
  // Inline styles
  for (const sb of html.matchAll(/style="([^"]*)"/gi)) {
    const styleStr = sb[1];
    let tcm;
    while ((tcm = textColorRe.exec(styleStr)) !== null) {
      const preceding = styleStr.substring(Math.max(0, tcm.index - 15), tcm.index);
      if (!/background-?\s*$/i.test(preceding)) {
        metrics.textColors.push(tcm[1].toUpperCase());
      }
    }
  }
  // Style block color declarations (for slides with CSS in <style>)
  if (styleBlockMatch) {
    const styleBlock = styleBlockMatch[1];
    const blockColorRe = /(?:^|;\s*)color\s*:\s*#([0-9a-fA-F]{6})/gi;
    let bcm;
    while ((bcm = blockColorRe.exec(styleBlock)) !== null) {
      const preceding = styleBlock.substring(Math.max(0, bcm.index - 15), bcm.index);
      if (!/background-?\s*$/i.test(preceding)) {
        metrics.textColors.push(bcm[1].toUpperCase());
      }
    }
  }

  return metrics;
}

function checkConsistency(allMetrics) {
  const warnings = [];

  // PF-09: Title (h1) font-size consistency
  const titleSizes = allMetrics.map(m => m.h1FontSize).filter(Boolean);
  if (titleSizes.length >= 2) {
    const sd = stddev(titleSizes);
    if (sd > 2) {
      warnings.push(fmtWarn('cross-slide', 'PF-09',
        `Title font-size inconsistency (stddev=${sd.toFixed(1)}pt across ${titleSizes.length} slides)`));
    }
  }

  // PF-10: Body padding consistency
  const paddings = allMetrics.map(m => m.bodyPadding).filter(Boolean);
  const uniquePaddings = new Set(paddings);
  if (uniquePaddings.size > 2) {
    warnings.push(fmtWarn('cross-slide', 'PF-10',
      `Body padding varies across ${uniquePaddings.size} patterns`));
  }

  // PF-11: Color palette consistency (unique color count)
  const allColors = new Set(allMetrics.flatMap(m => m.usedColors));
  if (allColors.size > 8) {
    warnings.push(fmtWarn('cross-slide', 'PF-11',
      `${allColors.size} unique colors used across deck (recommend ≤8)`));
  }

  // PF-31: Title uniqueness (Grackle, MS Accessibility)
  const titles = allMetrics.map((m, i) => ({ text: m.h1Text, slide: i + 1 })).filter(t => t.text);
  const titleMap = new Map();
  for (const t of titles) {
    const norm = t.text.toLowerCase().trim();
    if (!norm) continue;
    if (!titleMap.has(norm)) titleMap.set(norm, []);
    titleMap.get(norm).push(t.slide);
  }
  for (const [title, slides] of titleMap) {
    if (slides.length > 1) {
      warnings.push(fmtWarn('cross-slide', 'PF-31',
        `Duplicate slide title "${title.substring(0, 40)}..." on slides ${slides.join(', ')} — each slide should have a unique title [WCAG]`));
    }
  }

  // PF-24 비활성(2026-06-15 COM 직접판정, s8040 FAQ 흰글씨=주황 배지 위 정상, 흰on흰 0 = FP). cross-slide
  // 정적 검사는 텍스트↔배경 매핑이 없어 "흰글씨 존재 + 흰배경 존재"를 흰on흰으로 오판한다. 실측 PF-71
  // (--full ancestor 매핑 대비)이 정확히 대체 — PF-71 미발화인데 PF-24만 발화 = 정적 매핑부재 오판.
  for (let i = 0; false && i < allMetrics.length; i++) {
    const m = allMetrics[i];
    if (m.bodyBgBrightness === null || m.textColors.length === 0) continue;
    const isDarkBg = m.bodyBgBrightness < 0.2;
    const isLightBg = m.bodyBgBrightness > 0.8;

    // Collect all background luminances on this slide (body + container divs)
    const allBgLums = [m.bodyBgBrightness];
    for (const bgHex of (m.containerBgColors || [])) {
      const bgRgb = hexToRgb(bgHex);
      if (bgRgb) allBgLums.push(relativeLuminance(...bgRgb));
    }

    for (const tc of m.textColors) {
      const rgb = hexToRgb(tc);
      if (!rgb) continue;
      const textLum = relativeLuminance(...rgb);

      // Check: does this text color have good contrast with ANY background on the slide?
      // WCAG contrast ratio = (L1 + 0.05) / (L2 + 0.05) where L1 > L2
      const hasGoodContrast = allBgLums.some(bgLum => {
        const l1 = Math.max(textLum, bgLum);
        const l2 = Math.min(textLum, bgLum);
        return (l1 + 0.05) / (l2 + 0.05) >= 3.0; // minimum 3:1 for large text
      });

      if (hasGoodContrast) continue; // text is readable on at least one background

      // No background provides sufficient contrast — warn
      if (isDarkBg && textLum < 0.2) {
        warnings.push(fmtWarn(`slide-${String(i + 1).padStart(2, '0')}`, 'PF-24',
          `Dark text #${tc} on dark background (luminance ${m.bodyBgBrightness.toFixed(2)}) — low contrast`));
        break;
      }
      if (isLightBg && textLum > 0.8) {
        warnings.push(fmtWarn(`slide-${String(i + 1).padStart(2, '0')}`, 'PF-24',
          `Light text #${tc} on light background (luminance ${m.bodyBgBrightness.toFixed(2)}) — low contrast`));
        break;
      }
    }
  }

  return warnings;
}

// ── Main export ──────────────────────────────────────────────────────────────

/**
 * Run pre-flight checks on slide HTML files.
 * @param {string} slidesDir - Path to directory containing slide-*.html files
 * @param {{ full?: boolean }} options
 * @returns {Promise<{ errors: string[], warnings: string[], passed: boolean }>}
 */
// Parse an ANSI-formatted issue line into a structured object
function parseIssueLine(line) {
  const plain = line.replace(/\x1b\[[0-9;]*m/g, '');
  const level = plain.includes('ERROR') ? 'ERROR' : 'WARN';
  const fileMatch = plain.match(/\[([^\]]+)\]/);
  const ruleMatch = plain.match(/\] (PF-\d+):/);
  const msgMatch = plain.match(/PF-\d+: (.+)/);
  return {
    file: fileMatch ? fileMatch[1] : 'unknown',
    rule: ruleMatch ? ruleMatch[1] : 'UNKNOWN',
    level,
    message: msgMatch ? msgMatch[1] : plain,
  };
}

export async function preflightCheck(slidesDir, options = {}) {
  const absDir = path.resolve(slidesDir);
  const files = fs.readdirSync(absDir)
    .filter(f => /^slide-\d+[^]*\.html$/.test(f))
    .sort();

  if (files.length === 0) {
    return { errors: ['No slide-*.html files found in ' + absDir], warnings: [], passed: false };
  }

  const errors = [];
  const warnings = [];
  const allMetrics = [];

  // Phase 1: static checks + metric collection
  for (const file of files) {
    const html = fs.readFileSync(path.join(absDir, file), 'utf-8');
    const issues = [
      ...runStaticChecks(html, file),
      ...checkPF58(html, file, absDir),
    ];
    for (const line of issues) {
      if (line.includes('ERROR')) errors.push(line);
      else warnings.push(line);
    }
    allMetrics.push(extractSlideMetrics(html));
  }

  // Phase 2: Playwright checks (only with --full)
  if (options.full) {
    const pwIssues = await runPlaywrightChecks(absDir, files);
    for (const line of pwIssues) {
      if (line.includes('ERROR')) errors.push(line);
      else warnings.push(line);
    }
  }

  // Phase 3: Cross-slide consistency
  if (allMetrics.length >= 2) {
    const consistencyIssues = checkConsistency(allMetrics);
    for (const line of consistencyIssues) {
      warnings.push(line);
    }
  }

  // --json mode: also return structured array
  if (options.json) {
    const structured = [
      ...errors.map(parseIssueLine),
      ...warnings.map(parseIssueLine),
    ];
    return { errors, warnings, passed: errors.length === 0, structured };
  }

  return { errors, warnings, passed: errors.length === 0 };
}

export default preflightCheck;

// ── CLI entry ────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  let slidesDir = null;
  let full = false;
  let summary = false;
  let json = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--slides-dir' && args[i + 1]) slidesDir = args[++i];
    if (args[i] === '--full') full = true;
    if (args[i] === '--summary') summary = true;
    if (args[i] === '--json') json = true;
  }

  if (!slidesDir) {
    console.error('Usage: node scripts/preflight-html.js --slides-dir <dir> [--full] [--summary] [--json]');
    process.exit(1);
  }

  if (!json) {
    console.log(`${BOLD}Pre-flight HTML check: ${path.resolve(slidesDir)}${RESET}`);
    if (full) console.log('  (Playwright checks enabled with --full)\n');
    else console.log('  (Static checks only \u2014 use --full for Playwright overflow/CJK checks)\n');
  }

  const result = await preflightCheck(slidesDir, { full, json });

  // --json: output structured JSON and exit
  if (json) {
    console.log(JSON.stringify(result.structured || [], null, 2));
    process.exit(result.passed ? 0 : 1);
  }

  if (summary) {
    // --summary: ERROR detailed, WARN aggregated by rule ID
    for (const line of result.errors) {
      console.log(line);
    }
    if (result.warnings.length > 0) {
      // Group warnings by rule ID (e.g. "PF-08")
      const stripAnsi = s => s.replace(/\x1b\[[0-9;]*m/g, '');
      const warnGroups = new Map();
      for (const line of result.warnings) {
        const plain = stripAnsi(line);
        const idMatch = plain.match(/\] (PF-\d+):/);
        const fileMatch = plain.match(/\[([^\]]+)\]/);
        const id = idMatch ? idMatch[1] : 'OTHER';
        const file = fileMatch ? fileMatch[1] : 'unknown';
        if (!warnGroups.has(id)) warnGroups.set(id, { files: [], msg: '' });
        const group = warnGroups.get(id);
        group.files.push(file);
        if (!group.msg) {
          const msgMatch = plain.match(/PF-\d+: (.+)/);
          group.msg = msgMatch ? msgMatch[1] : '';
        }
      }
      console.log('');
      for (const [id, group] of warnGroups) {
        const fileList = group.files.length <= 3
          ? group.files.join(', ')
          : `${group.files[0]}~${group.files[group.files.length - 1]}`;
        console.log(`${YELLOW}${id}: ${group.files.length} slides (${fileList}) — ${group.msg}${RESET}`);
      }
    }
  } else {
    for (const line of [...result.errors, ...result.warnings]) {
      console.log(line);
    }
  }

  const total = result.errors.length + result.warnings.length;
  if (total === 0) {
    console.log(`\n${GREEN}${BOLD}\u2705 All checks passed.${RESET}`);
  } else {
    console.log(`\n${BOLD}Results: ${RED}${result.errors.length} error(s)${RESET}, ` +
      `${YELLOW}${result.warnings.length} warning(s)${RESET}`);
  }

  process.exit(result.passed ? 0 : 1);
}

// Run CLI when executed directly
const isMain = process.argv[1] &&
  path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'));
if (isMain) {
  main().catch(err => { console.error(err); process.exit(1); });
}
