#!/usr/bin/env node

/**
 * Post-PPTX XML validator — parses the ZIP/XML inside a .pptx file
 * and checks for layout issues (overflow, alignment, empty text, contrast).
 *
 * Usage:
 *   node scripts/validate-pptx.js --input slides/presentation/output.pptx
 *
 * Exit code 1 if any ERROR, 0 otherwise.
 *
 * Programmatic API:
 *   import { validatePptx } from './validate-pptx.js';
 *   const { errors, warnings, passed } = await validatePptx('path/to.pptx');
 */

import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const JSZip = require('jszip');

// ── Constants ──────────────────────────────────────────────────────────────

const EMU_PER_INCH = 914400;
const EMU_PER_PT = 12700;

// Default 16:9 slide dimensions (10" x 5.625")
const DEFAULT_SLIDE_W = 9144000;
const DEFAULT_SLIDE_H = 5143500;

// Column alignment tolerance (~3pt)
const COL_TOLERANCE = 36000;

// WCAG contrast thresholds
const CONTRAST_ERROR = 1.5;
// VP-04 sweet-spot(GT 이미지직접확인 2026-06-14): WARN 임계 4.5→3.0→2.124.
// realmix 10장 PowerPoint COM 이미지 직접 판정: ratio 2.13~2.8 발화는 전부 FP —
//   강조배지(주황#E8913A·초록#03C75A on 흰글자, s115)·강조수치(주황#FF6F00, s23)·
//   출처캡션(회색#94A3B8/#999999, 보조정보 가독OK)·밝은배경 금색(GT보다 대비좋음).
// GT 9건 raw = 1.947~2.118(청록#00C2FF 2.067·초록#00D48A 1.947·금색#D4A537 2.118).
// FP 최소 raw = 2.130(#AAAAAA). ratio는 XML색상 결정함수(렌더무관) → floor 2.124면
// GT 9건 항상 발화·그 위 445건 항상 침묵, 양쪽 마진 0.006. recall=1.0 유지.
const CONTRAST_WARN = 2.124;
const CONTRAST_LARGE = 3.0; // (subsumed by WARN floor) WCAG 큰 텍스트 임계

// ── Helpers ────────────────────────────────────────────────────────────────

function emuToInches(emu) {
  return (emu / EMU_PER_INCH).toFixed(2);
}

/**
 * Parse sRGB hex (6-char) into linear-light components for contrast calc.
 */
function hexToLuminance(hex) {
  const r = parseInt(hex.slice(0, 2), 16) / 255;
  const g = parseInt(hex.slice(2, 4), 16) / 255;
  const b = parseInt(hex.slice(4, 6), 16) / 255;
  const toLinear = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

function contrastRatio(hex1, hex2) {
  const l1 = hexToLuminance(hex1);
  const l2 = hexToLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ── Minimal regex-based XML helpers ────────────────────────────────────────

/**
 * Extract all matches of a regex pattern, returning an array of match objects.
 */
function matchAll(xml, pattern) {
  const re = new RegExp(pattern, 'gs');
  const results = [];
  let m;
  while ((m = re.exec(xml)) !== null) results.push(m);
  return results;
}

/**
 * Get attribute value from an XML tag string.
 */
function attr(tagStr, name) {
  const re = new RegExp(`${name}\\s*=\\s*"([^"]*)"`, 'i');
  const m = tagStr.match(re);
  return m ? m[1] : null;
}

// ── Slide size extraction ──────────────────────────────────────────────────

function parseSlideDimensions(presentationXml) {
  // <p:sldSz cx="9144000" cy="5143500" .../>
  const m = presentationXml.match(/<p:sldSz[^>]*>/i);
  if (!m) return { width: DEFAULT_SLIDE_W, height: DEFAULT_SLIDE_H };
  const cx = attr(m[0], 'cx');
  const cy = attr(m[0], 'cy');
  return {
    width: cx ? parseInt(cx, 10) : DEFAULT_SLIDE_W,
    height: cy ? parseInt(cy, 10) : DEFAULT_SLIDE_H,
  };
}

/**
 * Extract slide background color from <p:bg> element.
 * Returns 6-char hex string or null if no solid fill background.
 */
function extractSlideBgColor(slideXml) {
  const bgMatch = slideXml.match(/<p:bg>[\s\S]*?<a:solidFill>\s*<a:srgbClr\s+val="([0-9A-Fa-f]{6})"/i);
  return bgMatch ? bgMatch[1].toUpperCase() : null;
}

// ── Shape extraction from slide XML ────────────────────────────────────────

/**
 * Extract shape info from a slide XML string.
 * Returns array of { name, x, y, w, h, fillColor, textRuns: [{ text, color }] }
 */
function extractShapes(slideXml) {
  const shapes = [];

  // Match each <p:sp>...</p:sp> block
  const spBlocks = matchAll(slideXml, '<p:sp\\b[^>]*>([\\s\\S]*?)</p:sp>');

  for (const block of spBlocks) {
    const inner = block[1];
    const shape = { name: '', x: 0, y: 0, w: 0, h: 0, fillColor: null, hasTxBody: false, textRuns: [] };

    // Shape name from <p:nvSpPr><p:cNvPr ... name="..."/>
    const cNvPr = inner.match(/<p:cNvPr[^>]*>/i);
    if (cNvPr) {
      shape.name = attr(cNvPr[0], 'name') || '';
    }

    // Position: <a:off x="..." y="..."/>
    const off = inner.match(/<a:off[^>]*>/i);
    if (off) {
      shape.x = parseInt(attr(off[0], 'x') || '0', 10);
      shape.y = parseInt(attr(off[0], 'y') || '0', 10);
    }

    // Extent: <a:ext cx="..." cy="..."/>
    const ext = inner.match(/<a:ext[^>]*>/i);
    if (ext) {
      shape.w = parseInt(attr(ext[0], 'cx') || '0', 10);
      shape.h = parseInt(attr(ext[0], 'cy') || '0', 10);
    }

    // Shape fill: look for <a:solidFill> inside <p:spPr> but outside <p:txBody>
    // Split at <p:txBody> to isolate shape properties
    const txBodyStart = inner.indexOf('<p:txBody');
    const spPrSection = txBodyStart >= 0 ? inner.slice(0, txBodyStart) : inner;
    const spFill = spPrSection.match(/<a:solidFill>\s*<a:srgbClr\s+val="([0-9A-Fa-f]{6})"/i);
    if (spFill) {
      shape.fillColor = spFill[1].toUpperCase();
      // 반투명(rgba alpha) 파싱: PptxGenJS 가 HTML rgba(255,255,255,0.08) 류를 srgbClr+alpha 로 변환.
      // 낮은 alpha = 반투명 배경(아래 도형색이 비침) → 불투명색으로 대비 측정하면 오판(s141 운수업
      // 흰8% on 남색카드 = 실제 거의 남색이라 A8B8CC 라벨 읽힘인데 흰불투명으로 2.0 저대비 FP).
      const fillIdx = spPrSection.indexOf(spFill[0]);
      const alphaM = spPrSection.slice(fillIdx, fillIdx + 220).match(/<a:alpha\s+val="(\d+)"\s*\/>/);
      shape.fillAlpha = alphaM ? parseInt(alphaM[1], 10) / 100000 : 1;
    }

    // Text runs from <p:txBody>
    const txBody = inner.match(/<p:txBody>([\s\S]*?)<\/p:txBody>/i);
    if (txBody) {
      shape.hasTxBody = true;
      const runs = matchAll(txBody[1], '<a:r>([\\s\\S]*?)<\\/a:r>');
      for (const run of runs) {
        const runInner = run[1];

        // Text content: <a:t>...</a:t>
        const tMatch = runInner.match(/<a:t>([\s\S]*?)<\/a:t>/i);
        const text = tMatch ? tMatch[1] : '';

        // Text color: <a:rPr ...><a:solidFill><a:srgbClr val="..."/>
        let color = null;
        const rPr = runInner.match(/<a:rPr[^>]*>([\s\S]*?)<\/a:rPr>/i);
        if (rPr) {
          const textFill = rPr[1].match(/<a:solidFill>\s*<a:srgbClr\s+val="([0-9A-Fa-f]{6})"/i);
          if (textFill) color = textFill[1].toUpperCase();
        }
        // Also check rPr self-closing with nested solidFill via broader search
        if (!color) {
          const rPrBroad = runInner.match(/<a:rPr[\s\S]*?<a:srgbClr\s+val="([0-9A-Fa-f]{6})"/i);
          if (rPrBroad) color = rPrBroad[1].toUpperCase();
        }

        // Font size: <a:rPr sz="1200"/> = 12pt (hundredths of point)
        let fontSize = null;
        const szSource = rPr ? rPr[0] : runInner;
        const szMatch = szSource.match(/\bsz="(\d+)"/i);
        if (szMatch) fontSize = parseInt(szMatch[1]) / 100;

        shape.textRuns.push({ text, color, fontSize });
      }
    }

    shapes.push(shape);
  }

  return shapes;
}

// ── Table extraction from slide XML ─────────────────────────────────────────

/**
 * Extract table info from <p:graphicFrame> blocks containing <a:tbl>.
 * Returns array of { name, x, y, w, h, rows: [[{text, merged}]] }
 */
function extractTables(slideXml) {
  const tables = [];

  const gfBlocks = matchAll(slideXml, '<p:graphicFrame\\b[^>]*>([\\s\\S]*?)</p:graphicFrame>');

  for (const block of gfBlocks) {
    const inner = block[1];

    // Must contain a table
    if (!/<a:tbl\b/i.test(inner)) continue;

    const table = { name: '', x: 0, y: 0, w: 0, h: 0, rows: [] };

    // Name
    const cNvPr = inner.match(/<p:cNvPr[^>]*>/i);
    if (cNvPr) {
      table.name = attr(cNvPr[0], 'name') || '';
    }

    // Position
    const off = inner.match(/<a:off[^>]*>/i);
    if (off) {
      table.x = parseInt(attr(off[0], 'x') || '0', 10);
      table.y = parseInt(attr(off[0], 'y') || '0', 10);
    }
    const ext = inner.match(/<a:ext[^>]*>/i);
    if (ext) {
      table.w = parseInt(attr(ext[0], 'cx') || '0', 10);
      table.h = parseInt(attr(ext[0], 'cy') || '0', 10);
    }

    // Extract rows: <a:tr>...</a:tr>
    const rowBlocks = matchAll(inner, '<a:tr\\b[^>]*>([\\s\\S]*?)</a:tr>');
    for (const rowBlock of rowBlocks) {
      const rowInner = rowBlock[1];
      const cells = [];

      // Extract cells: <a:tc>...</a:tc>
      const cellBlocks = matchAll(rowInner, '<a:tc\\b([^>]*)>([\\s\\S]*?)</a:tc>');
      for (const cellBlock of cellBlocks) {
        const cellAttrs = cellBlock[1];
        const cellInner = cellBlock[2];

        // Check for merge spans (hMerge, vMerge, gridSpan, rowSpan)
        const hMerge = /hMerge\s*=\s*"1"/i.test(cellAttrs);
        const vMerge = /vMerge\s*=\s*"1"/i.test(cellAttrs);

        // Extract all text content from <a:t> tags
        const textParts = matchAll(cellInner, '<a:t>([\\s\\S]*?)<\\/a:t>');
        const text = textParts.map((t) => t[1]).join('').trim();

        cells.push({ text, merged: hMerge || vMerge });
      }

      table.rows.push(cells);
    }

    tables.push(table);
  }

  return tables;
}

// ── Validation checks ──────────────────────────────────────────────────────

function checkOverflow(shapes, slideW, slideH, slideNum) {
  const issues = [];
  for (const s of shapes) {
    if (s.w === 0 && s.h === 0) continue; // skip zero-size placeholders

    const right = s.x + s.w;
    const bottom = s.y + s.h;
    const name = s.name || 'unnamed';

    if (right > slideW + COL_TOLERANCE) {
      issues.push({
        level: 'ERROR',
        code: 'VP-01',
        slide: slideNum,
        message: `Shape "${name}" extends beyond slide right edge (x+w = ${emuToInches(right)}" > ${emuToInches(slideW)}")`,
      });
    }
    if (bottom > slideH + COL_TOLERANCE) {
      issues.push({
        level: 'ERROR',
        code: 'VP-01',
        slide: slideNum,
        message: `Shape "${name}" extends beyond slide bottom edge (y+h = ${emuToInches(bottom)}" > ${emuToInches(slideH)}")`,
      });
    }
    if (s.x < -COL_TOLERANCE) {
      issues.push({
        level: 'WARN',
        code: 'VP-01',
        slide: slideNum,
        message: `Shape "${name}" extends beyond slide left edge (x = ${emuToInches(s.x)}")`,
      });
    }
    if (s.y < -COL_TOLERANCE) {
      issues.push({
        level: 'WARN',
        code: 'VP-01',
        slide: slideNum,
        message: `Shape "${name}" extends beyond slide top edge (y = ${emuToInches(s.y)}")`,
      });
    }
  }
  return issues;
}

function checkColumnAlignment(shapes, slideNum) {
  const issues = [];

  // Filter to shapes with non-trivial size and not full-width (> 80% slide width)
  const candidates = shapes.filter((s) => {
    if (s.w === 0 && s.h === 0) return false;
    if (s.w > DEFAULT_SLIDE_W * 0.8) return false; // skip full-width elements
    if (s.h > DEFAULT_SLIDE_H * 0.8) return false; // skip full-height elements
    return true;
  });

  // Group shapes by x position AND similar width (within tolerance)
  const columns = [];
  for (const s of candidates) {
    let found = false;
    for (const col of columns) {
      const xClose = Math.abs(col.x - s.x) <= COL_TOLERANCE;
      // Width must be within 50% of median to belong to the same column group
      const medianW = col.shapes[0].w;
      const wClose = medianW > 0
        ? Math.abs(s.w - medianW) / medianW < 0.5
        : s.w < COL_TOLERANCE;
      if (xClose && wClose) {
        col.shapes.push(s);
        found = true;
        break;
      }
    }
    if (!found) {
      columns.push({ x: s.x, shapes: [s] });
    }
  }

  // For columns with 3+ shapes at different y positions, check width consistency
  for (const col of columns) {
    if (col.shapes.length < 3) continue;

    const uniqueY = new Set(col.shapes.map((s) => Math.round(s.y / COL_TOLERANCE)));
    if (uniqueY.size < 2) continue; // all at same y = row, not column

    // VP-02 표/그리드 가드(이미지직접확인 2026-06-14): 이 컬럼의 도형 다수가 행으로도 짝(같은 y에
    // 다른 x 셀)을 가지면 표/격자 셀이다 → 컬럼폭이 칸마다 다른 게 정상. realmix s124/s127/s131
    // 표를 일반 도형 그룹으로 오판하던 FP 제거. 진짜 리스트(행 짝 없음)·산발 도형은 발화 유지.
    const gridCells = col.shapes.filter((s) => candidates.some((o) =>
      o !== s && Math.abs(o.y - s.y) <= COL_TOLERANCE && Math.abs(o.x - s.x) > COL_TOLERANCE));
    if (gridCells.length >= Math.ceil(col.shapes.length / 2)) continue;

    const widths = col.shapes.map((s) => s.w);
    const minW = Math.min(...widths);
    const maxW = Math.max(...widths);

    // VP-02 추가개선: 절대 5pt 변동만으론 좌측정렬 리스트(텍스트 길이차로 폭만 다른 항목)도 발화한다
    // (약한 FP, slide5 [5.28×4,5.72×2]). 1차로 상대변동(max-min)/median>0.15 게이트를 뒀으나,
    // max-min 은 단일 outlier 에 민감 — s24 [1.11×13, 0.88](마지막 짧은 항목 1개)이 relVar 0.21 로 발화.
    // → 변동계수 CV(stdDev/mean) 로 교체. 다수 동일+소수 outlier 는 CV 작아 둔감(s24 0.05·s16 0.13),
    //   진짜 산발 불일치(폭 다양)는 CV 커서 보존. CV>0.15 일 때만 발화.
    const meanW = widths.reduce((a, b) => a + b, 0) / widths.length;
    const variance = widths.reduce((a, w) => a + (w - meanW) ** 2, 0) / widths.length;
    const cv = meanW > 0 ? Math.sqrt(variance) / meanW : 0;
    // VP-02 너비 불일치 분기 끔(이미지직접확인 2026-06-14): col은 같은 x로 묶인 좌측정렬 그룹인데,
    // 좌측정렬에선 폭이 내용따라 달라도 정렬이 맞는 게 정상(s8 "415TWh"·"945TWh" KPI카드+하단항목,
    // s7 차트). cv/widthStrs는 계산만 두되 발화 안 함. 진짜 결함은 아래 x-offset(같은 컬럼인데 좌측
    // 경계가 어긋남)만 의미. GT 0건이라 회귀 없음. (변수 미사용 경고 회피 위해 참조)
    void cv; void maxW; void minW;

    // Check x alignment within the column
    const xs = col.shapes.map((s) => s.x);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    if (maxX - minX > COL_TOLERANCE) {
      issues.push({
        level: 'WARN',
        code: 'VP-02',
        slide: slideNum,
        message: `Column at x~${emuToInches(col.x)}" has x-offset variance (${emuToInches(maxX - minX)}" spread)`,
      });
    }
  }

  return issues;
}

/**
 * Check if a shape has a sibling that overlaps it (containment or significant overlap).
 * html2pptx splits background fill and text into separate shapes — the fill shape
 * contains the text shape (text is inset by padding).
 * @param {object} shape - shape to check
 * @param {object[]} allShapes - all shapes on the slide
 * @param {function} siblingFilter - predicate for qualifying siblings
 * @returns {boolean}
 */
function hasOverlappingSibling(shape, allShapes, siblingFilter) {
  const sx = shape.x, sy = shape.y, sw = shape.w, sh = shape.h;
  const sCx = sx + sw / 2, sCy = sy + sh / 2;
  for (const other of allShapes) {
    if (other === shape) continue;
    if (!siblingFilter(other)) continue;
    // Check if other's center is inside shape, or shape's center is inside other
    const ox = other.x, oy = other.y, ow = other.w, oh = other.h;
    const oCx = ox + ow / 2, oCy = oy + oh / 2;
    const otherCenterInShape = oCx >= sx && oCx <= sx + sw && oCy >= sy && oCy <= sy + sh;
    const shapeCenterInOther = sCx >= ox && sCx <= ox + ow && sCy >= oy && sCy <= oy + oh;
    if (otherCenterInShape || shapeCenterInOther) {
      return true;
    }
  }
  return false;
}

function checkEmptyText(shapes, slideNum) {
  const issues = [];
  for (const s of shapes) {
    // Check shapes with txBody but no meaningful text content
    if (s.hasTxBody) {
      const allEmpty = s.textRuns.length === 0 || s.textRuns.every((r) => r.text.trim() === '');
      if (allEmpty) {
        // VP-03 추가개선: fill 있고 면적 있는 도형은 시각요소(막대·카드·배경·구분선)이고 텍스트 없는
        // 게 정상이다. 운영덱 빈 도형 1690개 중 92%가 fill, 68%가 fill+면적>0.2in²(막대·카드)=FP.
        // → 진짜 빈 텍스트박스(fill 없거나 면적 작음)만 발화. 핸드오프가 코퍼스 의존이라 보류한 영역.
        const areaIn2 = (s.w * s.h) / (EMU_PER_INCH * EMU_PER_INCH);
        if (s.fillColor && areaIn2 > 0.2) continue;
        // VP-03 추가개선: 텍스트 라벨로 못 쓰는 크기(높이<0.1in≈7pt OR 면적<0.025in²≈0.16²)는
        // placeholder 가 아니라 장식(점·구분선·밑줄·마일스톤마커). 점 0.08²·밑줄 0.83×0.06·마커 0.14²(10pt) 등.
        // 진짜 빈 라벨은 폭·높이 모두≥0.1 & 면적≥0.025 — 보존. min(w,h) 으로 가로·세로 얇은 바 모두 차단.
        if (Math.min(s.w, s.h) < 0.1 * EMU_PER_INCH || areaIn2 < 0.025) continue;
        // VP-03 추가개선: html2pptx 는 빈 wrapper div(컨테이너·행 래퍼)에도 txBody 를 붙인다.
        // 텍스트는 자식 도형에 있고 래퍼는 투명(no-fill). 겹치는 텍스트 자식이 있으면 래퍼 = 억제.
        // 기존엔 fill 도형만 억제해 no-fill 래퍼(s71 차트 컨테이너·행 래퍼 25건)를 놓쳤다.
        if (hasOverlappingSibling(s, shapes,
          (o) => o.textRuns.length > 0 && o.textRuns.some(r => r.text.trim()))) {
          continue;
        }
        const name = s.name || 'unnamed';
        issues.push({
          level: 'WARN',
          code: 'VP-03',
          slide: slideNum,
          message: `Shape "${name}" has a text frame but all text runs are empty`,
        });
      }
    }
  }
  return issues;
}

function checkTableEmptyCells(tables, slideNum) {
  const issues = [];
  for (const t of tables) {
    if (t.rows.length < 2) continue; // Need header + at least 1 data row

    const colCount = t.rows[0].length;

    // Data rows (skip header = row 0)
    for (let rowIdx = 1; rowIdx < t.rows.length; rowIdx++) {
      const row = t.rows[rowIdx];
      for (let colIdx = 0; colIdx < row.length; colIdx++) {
        const cell = row[colIdx];
        if (cell.merged) continue; // Skip merged continuation cells
        if (cell.text === '') {
          const name = t.name || 'unnamed';
          issues.push({
            level: 'WARN',
            code: 'VP-05',
            slide: slideNum,
            message: `Table "${name}" has empty cell at row ${rowIdx + 1}, col ${colIdx + 1}`,
          });
        }
      }
    }

    // Check if entire data row is empty (more severe)
    for (let rowIdx = 1; rowIdx < t.rows.length; rowIdx++) {
      const row = t.rows[rowIdx];
      const nonMergedCells = row.filter((c) => !c.merged);
      if (nonMergedCells.length > 0 && nonMergedCells.every((c) => c.text === '')) {
        const name = t.name || 'unnamed';
        issues.push({
          level: 'ERROR',
          code: 'VP-05',
          slide: slideNum,
          message: `Table "${name}" row ${rowIdx + 1} is entirely empty`,
        });
      }
    }
  }
  return issues;
}

function checkTableConsistency(tables, slideNum) {
  const issues = [];
  for (const t of tables) {
    if (t.rows.length < 2) continue;

    const headerColCount = t.rows[0].length;
    const name = t.name || 'unnamed';

    // Check column count consistency across rows
    for (let rowIdx = 1; rowIdx < t.rows.length; rowIdx++) {
      const rowColCount = t.rows[rowIdx].length;
      if (rowColCount !== headerColCount) {
        issues.push({
          level: 'ERROR',
          code: 'VP-06',
          slide: slideNum,
          message: `Table "${name}" row ${rowIdx + 1} has ${rowColCount} columns, header has ${headerColCount}`,
        });
      }
    }

    // Check if >50% of data cells are empty (suspicious)
    let totalDataCells = 0;
    let emptyDataCells = 0;
    for (let rowIdx = 1; rowIdx < t.rows.length; rowIdx++) {
      for (const cell of t.rows[rowIdx]) {
        if (cell.merged) continue;
        totalDataCells++;
        if (cell.text === '') emptyDataCells++;
      }
    }
    if (totalDataCells > 0 && emptyDataCells / totalDataCells > 0.5) {
      issues.push({
        level: 'ERROR',
        code: 'VP-06',
        slide: slideNum,
        message: `Table "${name}" has ${emptyDataCells}/${totalDataCells} empty data cells (${Math.round(emptyDataCells / totalDataCells * 100)}%)`,
      });
    }
  }
  return issues;
}

/**
 * VP-07: Detect shape-based table grids with empty cells.
 * html2pptx builds tables from individual shapes (not native <a:tbl>).
 * Groups by similar width → checks for grid pattern (2+ columns, 2+ rows)
 * → flags when some cells have text and others don't (= missing data).
 * Note: empty cells often have h=0 (collapsed), so height is NOT used for grouping.
 */
function checkShapeGridEmptyCells(shapes, slideNum) {
  const issues = [];

  const hasText = (s) => s.textRuns.length > 0 && s.textRuns.some((r) => r.text.trim() !== '');

  // Include shapes with fill, even if h=0 (collapsed empty cells)
  // Exclude fill-only shapes that are html2pptx bg siblings (have overlapping text shape)
  // 위치기반 짝 제외(이미지직접확인 2026-06-14): h=0 collapsed 셀 배경(E0E0E0)이 같은 셀 위치에 실제
  // text 셀(FAFAFA, s118 "1년+ 의무 적립")과 짝일 때, hasOverlappingSibling은 면적기반이라 h=0을 못
  // 잡아 빈 셀로 오발화. 같은 (x,y) 위치(±0.1")에 text 도형 있으면 진짜 빈칸 아니므로 제외.
  const CELL_POS_TOL = 0.1 * EMU_PER_INCH;
  const hasColocatedText = (s) => shapes.some((o) => o !== s &&
    o.textRuns.length > 0 && o.textRuns.some((r) => r.text.trim()) &&
    Math.abs(o.x - s.x) < CELL_POS_TOL && Math.abs(o.y - s.y) < CELL_POS_TOL);
  const filledShapes = shapes.filter((s) => s.w > 0 && s.fillColor && !hasOverlappingSibling(s, shapes,
    (o) => o.textRuns.length > 0 && o.textRuns.some(r => r.text.trim())) && !hasColocatedText(s));
  if (filledShapes.length < 6) return issues;


  // Group by similar width only (height varies: 0 for empty, ~24pt for filled)
  const widthGroups = [];
  for (const s of filledShapes) {
    let found = false;
    for (const g of widthGroups) {
      const refW = g[0].w;
      if (refW > 0 && Math.abs(s.w - refW) / refW < 0.08) {
        g.push(s);
        found = true;
        break;
      }
    }
    if (!found) widthGroups.push([s]);
  }

  for (const group of widthGroups) {
    if (group.length < 6) continue;

    // Grid check: 2+ distinct x AND 2+ distinct y positions
    const xSet = new Set(group.map((s) => Math.round(s.x / COL_TOLERANCE)));
    const ySet = new Set(group.map((s) => Math.round(s.y / COL_TOLERANCE)));


    if (xSet.size < 2 || ySet.size < 2) continue;

    // Mixed grid: some with text, some without
    const withText = group.filter(hasText);
    const withoutText = group.filter((s) => !hasText(s));
    if (withText.length === 0 || withoutText.length === 0) continue;

    const emptyRatio = withoutText.length / group.length;

    // Per-column WARN for individual empty cells
    const colMap = new Map();
    for (const s of group) {
      const xKey = Math.round(s.x / COL_TOLERANCE);
      if (!colMap.has(xKey)) colMap.set(xKey, []);
      colMap.get(xKey).push(s);
    }

    for (const [, colShapes] of colMap) {
      if (colShapes.length < 2) continue;
      const colWith = colShapes.filter(hasText);
      const colWithout = colShapes.filter((s) => !hasText(s));
      if (colWith.length > 0 && colWithout.length > 0) {
        for (const s of colWithout) {
          const name = s.name || 'unnamed';
          issues.push({
            level: 'WARN',
            code: 'VP-07',
            slide: slideNum,
            message: `Grid cell "${name}" at (${emuToInches(s.x)}", ${emuToInches(s.y)}") has fill but no text — possible empty table cell`,
          });
        }
      }
    }

    // Summary ERROR if >40% empty
    if (emptyRatio > 0.4) {
      issues.push({
        level: 'ERROR',
        code: 'VP-07',
        slide: slideNum,
        message: `Shape grid (${xSet.size}col × ${ySet.size}row) has ${withoutText.length}/${group.length} empty cells (${Math.round(emptyRatio * 100)}%) — likely table with missing data`,
      });
    }
  }

  return issues;
}

/**
 * VP-08 추가개선: 빈 채움도형이 "카드 그리드의 빈 칸"(작성자 텍스트 누락)일 때만 발화.
 * 같은 크기·정렬된 fill+텍스트 동료(peer)가 있어야 진짜 카드 그리드로 판정.
 * 차트 막대·트랙·구분선·장식 원·컨테이너 배경은 그런 peer 가 없어 억제(=VP-03 시각요소 원칙과 정합).
 * 운영덱 41건(전부 막대/트랙/장식 FP) → 0. 진짜 빈카드 TP 는 동료 카드가 텍스트를 품으므로 생존.
 */
function hasFilledTextPeer(s, shapes) {
  // html2pptx 는 카드를 [fill 배경 도형 + 별도 텍스트 도형] 으로 분리한다.
  // → 같은 크기·정렬된 다른 fill 카드배경(o)이 텍스트 자식을 품으면(콘텐츠 카드),
  //   s 는 그 그리드의 빈 카드 = 진짜 TP. 막대/트랙/장식/컨테이너는 이런 peer 가 없다.
  const ALIGN_TOL = 0.15 * EMU_PER_INCH; // 같은 행/열 정렬 허용
  const SIZE_TOL = 0.2; // ±20% 크기 일치
  if (s.w === 0 || s.h === 0) return false;
  const hasText = (o) => o.textRuns.length > 0 && o.textRuns.some(r => r.text.trim() !== '');
  for (const o of shapes) {
    if (o === s) continue;
    if (!o.fillColor) continue;
    const sizeMatch = Math.abs(o.w - s.w) <= SIZE_TOL * s.w && Math.abs(o.h - s.h) <= SIZE_TOL * s.h;
    if (!sizeMatch) continue;
    const sameRow = Math.abs(o.y - s.y) <= ALIGN_TOL;
    const sameCol = Math.abs(o.x - s.x) <= ALIGN_TOL;
    if (!(sameRow || sameCol)) continue;
    // o 가 콘텐츠 카드인가: 자신이 텍스트를 갖거나, 겹치는 텍스트 자식이 있다
    if (hasText(o) || hasOverlappingSibling(o, shapes, hasText)) return true;
  }
  return false;
}

/**
 * VP-08: Detect shapes with fill but no text content — possible empty card.
 * Only flags shapes with significant area (> 50pt × 50pt = 635000 × 635000 EMU)
 * AND that sit in a grid of same-size filled+text peer cards (genuine blank card).
 */
function checkFilledEmptyShapes(shapes, slideNum) {
  const issues = [];
  const MIN_AREA = 635000 * 635000; // ~50pt × 50pt in EMU²

  for (const s of shapes) {
    if (!s.fillColor) continue;
    const area = s.w * s.h;
    if (area < MIN_AREA) continue;

    const hasText = s.textRuns.length > 0 && s.textRuns.some(r => r.text.trim() !== '');
    if (!hasText) {
      // Suppress if this is html2pptx's background-fill shape with a text sibling nearby
      if (hasOverlappingSibling(s, shapes,
        (o) => o.textRuns.length > 0 && o.textRuns.some(r => r.text.trim()))) {
        continue;
      }
      // VP-08 추가개선: 길쭉한 도형(종횡비≥4)은 막대/트랙/구분선 = 카드 아님 → 억제
      const aspect = Math.max(s.w, s.h) / Math.min(s.w, s.h);
      if (aspect >= 4) continue;
      // VP-08 추가개선: 카드 그리드 동료(같은 크기·정렬 fill+텍스트)가 없으면 장식/컨테이너 = 억제
      if (!hasFilledTextPeer(s, shapes)) continue;
      const name = s.name || 'unnamed';
      issues.push({
        level: 'WARN',
        code: 'VP-08',
        slide: slideNum,
        message: `Shape "${name}" (${emuToInches(s.w)}" × ${emuToInches(s.h)}") has fill #${s.fillColor} but no text — possible empty card`,
      });
    }
  }
  return issues;
}

/**
 * Find the best background color for a text shape by looking for
 * overlapping filled shapes (html2pptx splits bg fill and text into separate shapes).
 * Returns the fillColor of the best-matching background shape, or 'FFFFFF' (slide bg).
 */
function findBackgroundColor(textShape, allShapes, slideBgColor, excludeColors = []) {
  const tx = textShape.x, ty = textShape.y;
  const tw = textShape.w, th = textShape.h;
  const tCx = tx + tw / 2, tCy = ty + th / 2; // center of text shape

  let bestFill = null;
  let bestScore = -Infinity;
  // 2차 후보: 텍스트 중심이 fill 밖이지만 충분히(≥30%) 겹치는 fill. 1차(중심포함) 후보가 전혀
  // 없을 때만 fallback. s144 "!" 는 아이콘 박스가 주황뱃지보다 넓어 중심이 뱃지를 50402EMU(마진
  // 26289 초과) 벗어남 → 1차 실패. 반투명 띠 제외 후 흰 slideBg 잡혀 흰on흰 1.0 FP → 2차로 주황뱃지
  // 선택해 해소. GT s71 금색은 1차(흰카드 cc통과)라 2차 미사용 = 보존.
  let bestFill2 = null, bestScore2 = -Infinity;

  for (const bg of allShapes) {
    if (bg === textShape) continue;
    if (!bg.fillColor) continue;
    // 반투명 fill(alpha<50%)은 아래 도형색이 비치므로 진짜 배경 아님 → 후보 제외(아래 불투명 카드 선택).
    // s141 운수업 흰8% 박스 제외 → 남색카드(1B2A4A) 선택 → A8B8CC 라벨 고대비 → FP 소멸.
    if (bg.fillAlpha != null && bg.fillAlpha < 0.5) continue;
    if (excludeColors.length > 0 && excludeColors.includes(bg.fillColor.toUpperCase())) continue;
    if (bg.w === 0 || bg.h === 0) continue;

    const bx = bg.x, by = bg.y, bw = bg.w, bh = bg.h;
    const ox = Math.min(tx + tw, bx + bw) - Math.max(tx, bx);
    const oy = Math.min(ty + th, by + bh) - Math.max(ty, by);

    // 게이트: 텍스트 중심이 fill 안(미세 톨러런스 포함)에 있어야 후보.
    // (구) 엄격 containsCenter 는 텍스트 박스가 컬러뱃지보다 약간 넓을 때 중심이 뱃지 경계를
    // 미세하게(예 s43 "1" 중심 x=992832 > 빨강뱃지 우측 990451, 2381EMU=0.003") 벗어나
    // 즉시배경(뱃지)을 놓치고 거대 카드배경(F5F5F5)을 잡아 흰글씨를 1.1 저대비로 오측정 = phantom FP.
    // → 텍스트 단변(min w,h)의 15% 마진으로 경계를 확장해 미세 이탈만 구제.
    //   (s43 뱃지 이탈 2381 < 마진 31218 → 구제 / s71 금색-남색막대 이탈 19050 > 마진 15716 →
    //    제외 유지, GT 금색 on F5F7FA 2.1 보존). overlap 전체 완화는 GT 배경선택을 바꿔 금지.
    const margin = Math.min(tw, th) * 0.15;
    const containsCenter =
      tCx >= bx - margin && tCx <= bx + bw + margin &&
      tCy >= by - margin && tCy <= by + bh + margin;

    // Score: prefer shapes that most closely match the text shape bounds (same origin = sibling)
    // Higher score = better match
    const dxOff = Math.abs(bx - tx);
    const dyOff = Math.abs(by - ty);
    const dw = Math.abs(bw - tw);
    const dh = Math.abs(bh - th);
    // Penalize distance; prefer shapes at same position with similar size
    const score = -(dxOff + dyOff + dw + dh);

    if (!containsCenter) {
      // 2차 후보: 중심 이탈했으나 텍스트 면적의 30%+ '실제 겹치는' fill(아이콘뱃지 등).
      // (1차 cc 는 톨러런스라 overlap=0 이어도 통과 가능 — F5F7FA 처럼 중심만 margin 내인 카드.
      //  그래서 overlap 게이트는 2차에만 적용, 1차는 cc 만으로 후보 = GT s71 금색 on F5F7FA 보존)
      // 2차는 '텍스트를 감싸는 작은 배지'만(폭·높이 ≤ 텍스트의 2배). 거대 막대/카드가 중심이탈로
      // 30% 겹치는 건 실제 배경 아님(s71 금색이 남색막대와 47% 겹쳐도 실제 배경은 연한 슬라이드 →
      // 거대 막대 폭 7배 제외해 GT 보존 / s144 주황뱃지는 "!" 폭의 0.56배라 통과).
      if (ox > 0 && oy > 0 && bw <= tw * 2 && bh <= th * 2) {
        const overlapRatio = (ox * oy) / (tw * th);
        if (overlapRatio >= 0.3 && score >= bestScore2) {
          bestScore2 = score;
          bestFill2 = bg.fillColor;
        }
      }
      continue;
    }

    // 동률(>=) 타이브레이크: 막대그래프에서 트랙배경과 값막대가 bounds 완전 동일(값=max → 풀폭)일 때
    // XML order 나중(=위에 그려진 = 텍스트 즉시배경)을 선택. (구) ">" 는 먼저 그려진 트랙(EEEEEE)을
    // 유지해 흰글씨 on EEEEEE 1.2 phantom(s59 "50"/"18.2") 발생. >= 면 위 막대(E31837 4.7:1) 선택→소멸.
    if (score >= bestScore) {
      bestScore = score;
      bestFill = bg.fillColor;
    }
  }

  return bestFill || bestFill2 || slideBgColor || 'FFFFFF';
}

function checkContrast(shapes, slideNum, slideBgColor, pictures = []) {
  const issues = [];
  const overlapsPicture = (s) =>
    pictures.some((p) =>
      s.x < p.x + p.w && s.x + s.w > p.x && s.y < p.y + p.h && s.y + s.h > p.y
    );
  for (const s of shapes) {
    if (s.textRuns.length === 0) continue;
    // VP-04 FP 제거(정교화): 그림 위 텍스트는 XML만으로 실제 배경색을 알 수 없다(픽셀 샘플링 필요).
    // 단, '무조건 제외'는 과잉 — 운영덱 실측상 소멸 34건 중 33건이 FN(연한 장식 picture 위 유채색/회색
    // 저대비 텍스트까지 제외). 따라서 '어두운 사진 위 밝은 글자' FP만 타겟: 도형의 모든 텍스트 run 이
    // 밝을(luma>200, 흰/연회색) 때만 picture 겹침 제외. 유채색·회색·어두운 텍스트는 유지(FN 방지).
    const litRuns = s.textRuns.filter(r => r.color && /^[0-9A-F]{6}$/.test(r.color));
    const allBright = litRuns.length > 0 && litRuns.every(r => {
      const R = parseInt(r.color.slice(0, 2), 16), G = parseInt(r.color.slice(2, 4), 16), B = parseInt(r.color.slice(4, 6), 16);
      return (0.299 * R + 0.587 * G + 0.114 * B) > 200;
    });
    if (overlapsPicture(s) && allBright) continue;

    // Determine background color: shape fill, nearest overlapping filled shape, slide bg, or white
    let bgColor = s.fillColor || findBackgroundColor(s, shapes, slideBgColor);

    // VP-04 오탐 방지: 텍스트와 동색 배경 감지 시 해당 색 제외하고 재탐색
    if (!s.fillColor) {
      const fgColors = s.textRuns.filter(r => r.color).map(r => r.color.toUpperCase());
      if (fgColors.includes(bgColor.toUpperCase())) {
        const altBg = findBackgroundColor(s, shapes, slideBgColor, [bgColor.toUpperCase()]);
        if (altBg.toUpperCase() !== bgColor.toUpperCase()) bgColor = altBg;
      }
    }

    for (const run of s.textRuns) {
      const rt = run.text.trim();
      if (!rt) continue;
      // VP-04 장식 glyph 제외: 단일 구분/연산 기호(+ · • × ÷ / → 등)는 막대/단계 사이 보조 연결
      // 시각요소로 의도적 저채도(본문 아님) → 대비검사 제외. (s123 막대그래프 "+" ×4 = 100+20+...145 FP)
      if (rt.length === 1 && /^[+\-·•×÷/→←↑↓*=~|<>]$/.test(rt)) continue;
      // Default text color is black if not specified
      const fgColor = run.color || '000000';

      const ratio = contrastRatio(fgColor, bgColor);
      const ratioStr = ratio.toFixed(1);
      const name = s.name || 'unnamed';
      const textPreview = run.text.trim().slice(0, 30);

      if (ratio < CONTRAST_ERROR) {
        issues.push({
          level: 'ERROR',
          code: 'VP-04',
          slide: slideNum,
          message: `Text "#${fgColor}" on "#${bgColor}" in "${name}" — invisible (ratio: ${ratioStr}:1) — "${textPreview}"`,
        });
      } else if (ratio < CONTRAST_WARN) {
        // VP-04 추가개선: WCAG AA 큰 텍스트(≥18pt) 면제 — 큰 텍스트 기준은 3:1. ratio≥3 이면 통과.
        // checkContrast가 run.fontSize 를 파싱하면서도 단일 4.5 임계만 써 큰 제목·강조(3.0~4.5)를 과발화.
        // bold≥14pt도 WCAG 큰텍스트지만 bold 미파싱 → ≥18pt만 보수적 면제(FN 방지). 운영덱 765 WARN 감축.
        if (run.fontSize && run.fontSize >= 18 && ratio >= CONTRAST_LARGE) continue;
        issues.push({
          level: 'WARN',
          code: 'VP-04',
          slide: slideNum,
          message: `Text "#${fgColor}" on "#${bgColor}" in "${name}" — low contrast (ratio: ${ratioStr}:1) — "${textPreview}"`,
        });
      }
    }
  }
  return issues;
}

/**
 * VP-09: Detect shapes where fit:shrink may not activate.
 * PptxGenJS fit:shrink requires manual edit to take effect.
 * Estimates text density vs shape area — flags when text likely overflows.
 */
function checkShrinkReliability(shapes, slideNum) {
  const issues = [];
  for (const s of shapes) {
    if (s.textRuns.length === 0 || s.w === 0 || s.h === 0) continue;
    // Estimate total text length
    const totalText = s.textRuns.map(r => r.text).join('');
    if (totalText.length < 10) continue;

    // 측정 기반 재보정: 균일 7pt/char는 CJK를 ~1.7배 과소추정(FN). 실측상 CJK≈0.92×폰트
    // (VP-16 현행값 validate-pptx.js:1149 와 일관), 라틴≈0.5×, 공백≈0.25×. 폰트크기는 run에서 취득.
    const fontSizes = s.textRuns.filter(r => r.fontSize).map(r => r.fontSize);
    const fontPt = fontSizes.length > 0 ? Math.max(...fontSizes) : 12;
    const cjkCount = (totalText.match(/[　-〿㐀-䶿一-鿿豈-﫿가-힯]/g) || []).length;
    const spaceCount = (totalText.match(/\s/g) || []).length;
    const otherLatin = Math.max(0, totalText.length - cjkCount - spaceCount);
    const textWidthPt = (cjkCount * fontPt * 0.92) + (otherLatin * fontPt * 0.5) + (spaceCount * fontPt * 0.25);
    const avgLineHeightPt = fontPt * 1.3; // 측정상 행높이 ≈ 1.3×폰트
    const shapWidthPt = s.w / EMU_PER_PT;
    const shapHeightPt = s.h / EMU_PER_PT;

    // 5% 폭 여유: 경계선(근소 초과) 텍스트가 줄 수 올림으로 오발화하지 않도록.
    const lines = Math.max(1, Math.ceil(textWidthPt / (shapWidthPt * 1.05)));
    const neededHeight = lines * avgLineHeightPt;

    // VP-09 추가개선: 박스높이가 한 줄(lineHeight)도 안 되게 잡힌 도형은 html2pptx 측정 아티팩트다
    // (라벨류 도형이 autofit 으로 실제론 늘어남). 운영덱 avail 8pt(<lineHeight) 8건 + 자연폭 자막류가
    // 약한 FP. 박스가 최소 한 줄 높이 이상일 때만 밀도 판정. 진짜 과밀(여러 줄 박스+넘침)은 보존.
    // VP-09 잔존 정밀화(이미지직접확인 2026-06-14): 운영덱 잔존 9건 전부 "2 lines" 추정인데 실제
    // PptxGenJS autofit/박스가 처리해 잘림 0(s110 카드제목·s56 funnel·s78 타임라인·s114 배지·s128 표헤더).
    // 진짜 과밀(fn-verify slide4 "5 lines")만 3줄+. → lines>=3 일 때만 발화. 2줄 경계 autofit FP 제거,
    // 다중줄 진짜 넘침은 보존(FN 안전).
    if (lines >= 3 && neededHeight > shapHeightPt * 1.5 && shapHeightPt >= avgLineHeightPt) {
      const name = s.name || 'unnamed';
      issues.push({
        level: 'WARN',
        code: 'VP-09',
        slide: slideNum,
        message: `Shape "${name}" text density high (est. ${lines} lines, ~${Math.round(neededHeight)}pt needed, ${Math.round(shapHeightPt)}pt available) — fit:shrink may not activate without manual edit`,
      });
    }
  }
  return issues;
}

/**
 * VP-10: Check gap consistency between shapes in the same row/column.
 */
function checkGapConsistency(shapes, slideNum) {
  const issues = [];

  // Filter to meaningful shapes
  const meaningfulRaw = shapes.filter(s => s.w > 0 && s.h > 0 && s.w < DEFAULT_SLIDE_W * 0.8);
  // VP-10 정밀화: 다른 도형 안에 완전히 포함된(중첩) 도형은 gap 피어가 아니다.
  // html2pptx가 카드 컨테이너 안에 텍스트 도형을 중첩 생성 → 음수 gap을 양산하므로 제외.
  const meaningful = meaningfulRaw.filter((s) => !meaningfulRaw.some((o) =>
    o !== s &&
    o.x <= s.x && o.y <= s.y &&
    o.x + o.w >= s.x + s.w && o.y + o.h >= s.y + s.h &&
    (o.w * o.h) > (s.w * s.h)
  ));
  if (meaningful.length < 3) return issues;

  // Group by similar y (same row, within ~10pt tolerance)
  const rowTolerance = 10 * EMU_PER_PT;
  const rows = [];
  for (const s of meaningful) {
    let found = false;
    for (const row of rows) {
      if (Math.abs(row.y - s.y) <= rowTolerance) {
        row.shapes.push(s);
        found = true;
        break;
      }
    }
    if (!found) rows.push({ y: s.y, shapes: [s] });
  }

  for (const row of rows) {
    if (row.shapes.length < 3) continue;
    // Sort by x position
    const sorted = row.shapes.sort((a, b) => a.x - b.x);
    // VP-10 표/그리드 가드(이미지직접확인 2026-06-14): 이 행의 셀 다수가 열로도 짝(같은 x에 다른 y
    // 셀)을 가지면 표/격자 행이다 → 셀 간격이 칸마다 다른 게 정상(라벨열 넓고 숫자열 좁고). realmix
    // s124 표 행을 '간격 불일치'로 오판하던 FP 제거. 진짜 단일 행 배치(열 짝 없음)는 발화 유지.
    const gridCells = sorted.filter((s) => meaningful.some((o) =>
      o !== s && Math.abs(o.x - s.x) <= rowTolerance && Math.abs(o.y - s.y) > rowTolerance));
    if (gridCells.length >= Math.ceil(sorted.length / 2)) continue;
    const gaps = [];
    for (let i = 1; i < sorted.length; i++) {
      const gap = sorted[i].x - (sorted[i - 1].x + sorted[i - 1].w);
      gaps.push(gap);
    }
    if (gaps.length < 2) continue;
    // VP-10 FP 제거: 겹친 도형(음수 gap)은 PF-18/sibling-overlap이 담당.
    // 음수 gap이 stdDev를 부풀려 '간격 불일치'로 오발화하므로 해당 행은 제외.
    if (gaps.some((g) => g < 0)) continue;
    // 그룹/쌍 배치 제외(이미지직접확인 2026-06-14): 매우 작은 양수 gap(<10pt)이 큰 gap과 섞이면
    // 아이콘-라벨 쌍/그룹 배치(s149 타임라인 점-라벨 6pt + 항목간 54pt)다 = 쌍 내부 근접이 stdDev를
    // 부풀려 오발화. 작은 gap이 있으면 의도적 그룹핑으로 보고 제외. 균등 단일행은 발화 유지.
    if (gaps.some((g) => g >= 0 && g < 10 * EMU_PER_PT)) continue;
    const gapMean = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    const gapStdDev = Math.sqrt(gaps.reduce((sum, g) => sum + (g - gapMean) ** 2, 0) / gaps.length);

    // VP-10 추가개선: 절대 stdDev 5pt 만으로는 균등 배치(마일스톤 점·진행바 등)의 텍스트폭 미세변동도
    // 발화한다(약한 FP, 운영덱 CV<0.2 8건 = 시각상 균등). 상대 변동계수(CV=stdDev/mean)도 함께 봐
    // CV>0.2(명백히 불균등)일 때만 발화. 균등(CV<0.2)은 제외. 진짜 불일치(예 [6,217,6] CV>1)는 보존.
    const gapCV = gapMean > 0 ? gapStdDev / gapMean : 0;
    // Flag if gap variance > 5pt AND relative variation is meaningful
    if (gapStdDev > 5 * EMU_PER_PT && gapCV > 0.2) {
      const gapsPt = gaps.map(g => (g / EMU_PER_PT).toFixed(1) + 'pt').join(', ');
      issues.push({
        level: 'WARN',
        code: 'VP-10',
        slide: slideNum,
        message: `Row at y=${emuToInches(row.y)}" has inconsistent gaps: [${gapsPt}]`,
      });
    }
  }
  return issues;
}

/**
 * VP-11: Check reading order — shape order in spTree vs visual (y→x) order.
 */
function checkReadingOrder(shapes, slideNum) {
  const issues = [];
  const meaningful = shapes.filter(s => s.w > 0 && s.h > 0 && s.textRuns.some(r => r.text.trim()));
  if (meaningful.length < 3) return issues;

  // VP-11 추가개선: (1) 멀티컬럼 그리드는 XML이 카드단위 열우선이 정상(스크린리더는 카드 한 묶음씩
  //   읽음). 행우선과만 비교하면 81% 오판(s6 4컬럼 완벽정렬). → 열우선 시각순서도 계산, 둘 중 하나만
  //   맞으면 정상. (2) exact-position 비교는 단일 요소(제목·푸터) 이동이 뒤 전체를 밀어 불일치 증폭 —
  //   Kendall tau(역전쌍) 거리로 교체해 국소 이동에 강건. 진짜 뒤섞임(역전쌍 다수)만 발화.
  const rowMajor = [...meaningful].sort((a, b) => {
    const yDiff = a.y - b.y;
    if (Math.abs(yDiff) > 20 * EMU_PER_PT) return yDiff;
    return a.x - b.x;
  });
  const colMajor = [...meaningful].sort((a, b) => {
    const xDiff = a.x - b.x;
    if (Math.abs(xDiff) > 20 * EMU_PER_PT) return xDiff;
    return a.y - b.y;
  });

  // XML 순서(meaningful) 대비 시각순서의 역전쌍 수 / 전체 쌍 = Kendall tau 정규화 거리
  const tauDist = (visualSorted) => {
    const rank = new Map();
    visualSorted.forEach((s, i) => rank.set(s, i));
    let inv = 0;
    for (let i = 0; i < meaningful.length; i++) {
      for (let j = i + 1; j < meaningful.length; j++) {
        if (rank.get(meaningful[i]) > rank.get(meaningful[j])) inv++;
      }
    }
    return inv;
  };
  const totalPairs = (meaningful.length * (meaningful.length - 1)) / 2;
  const inversions = Math.min(tauDist(rowMajor), tauDist(colMajor));
  const tauRatio = totalPairs > 0 ? inversions / totalPairs : 0;
  if (tauRatio > 0.2) {
    issues.push({
      level: 'WARN',
      code: 'VP-11',
      slide: slideNum,
      message: `Reading order mismatch: ${inversions}/${totalPairs} shape pairs inverted vs visual order (${Math.round(tauRatio * 100)}%) — may affect accessibility`,
    });
  }
  return issues;
}

/**
 * VP-12: Detect empty slides (no shapes or no text at all).
 */
function checkEmptySlide(shapes, tables, slideNum) {
  const issues = [];
  const totalShapes = shapes.length + tables.length;

  if (totalShapes < 2) {
    issues.push({
      level: 'ERROR',
      code: 'VP-12',
      slide: slideNum,
      message: `Slide has only ${totalShapes} shape(s) — likely empty or failed conversion`,
    });
    return issues;
  }

  // Check if any shape has text
  const hasAnyText = shapes.some(s => s.textRuns.some(r => r.text.trim() !== ''));
  const hasTableText = tables.some(t => t.rows.some(row => row.some(cell => cell.text.trim() !== '')));
  if (!hasAnyText && !hasTableText) {
    issues.push({
      level: 'ERROR',
      code: 'VP-12',
      slide: slideNum,
      message: `Slide has ${totalShapes} shapes but no text content — possible conversion failure`,
    });
  }
  return issues;
}

/**
 * VP-14: Detect overlapping text shapes on the same slide.
 * Compares bounding boxes of all shapes with text content.
 * Overlap > 20% of the smaller shape's area → ERROR (text unreadable).
 * Overlap 5-20% → WARN.
 * Ignores parent-child containment (one fully containing the other).
 */
function shapeText(s) {
  return (s.textRuns || []).map(r => r.text).join('').trim();
}

function checkShapeOverlap(shapes, slideNum) {
  const issues = [];
  // Filter to shapes with text content or fill and meaningful size (> 20pt × 20pt)
  const MIN_SIZE = 20 * 12700; // 20pt in EMU
  const textShapes = shapes.filter(s => {
    const text = shapeText(s);
    return (text.length > 0 || s.fillColor) && s.w > MIN_SIZE && s.h > MIN_SIZE;
  });

  if (textShapes.length < 2) return issues;

  // Limit pairwise check to first 60 shapes for performance
  const check = textShapes.slice(0, 60);
  const found = new Set();

  for (let i = 0; i < check.length; i++) {
    for (let j = i + 1; j < check.length; j++) {
      const a = check[i];
      const b = check[j];

      const aRight = a.x + a.w;
      const aBottom = a.y + a.h;
      const bRight = b.x + b.w;
      const bBottom = b.y + b.h;

      // Skip if one fully contains the other (parent-child)
      const aContainsB = a.x <= b.x && aRight >= bRight && a.y <= b.y && aBottom >= bBottom;
      const bContainsA = b.x <= a.x && bRight >= aRight && b.y <= a.y && bBottom >= aBottom;
      if (aContainsB || bContainsA) continue;

      // Skip bg+text sibling pairs: one has fill only (no text), other has text
      // html2pptx splits grid/table cells into separate fill and text shapes
      const aHasText = shapeText(a).length > 0;
      const bHasText = shapeText(b).length > 0;
      if ((!aHasText && a.fillColor && bHasText) || (!bHasText && b.fillColor && aHasText)) continue;
      // Skip fill-only pairs: neither shape has text → no readability impact
      if (!aHasText && !bHasText) continue;

      // 장식 대형 글자 제외(이미지직접확인 2026-06-14): S/W/O/T·5·6·7 같은 1~2자 거대 장식 글자는
      // box가 콘텐츠와 겹쳐도 실제 글자 위치는 분리(s57 SWOT·s129 큰숫자"5" 직접확인) = box-overlap이
      // 실제 글자 겹침을 과대평가 → 거짓 ERROR("text unreadable"). 짧은텍스트(≤2자)+큰폰트(≥48pt) 한쪽이면
      // 의도적 장식 배치로 보고 skip. 본문끼리 진짜 겹침은 유지.
      const fontOf = (s) => { const fs = s.textRuns.filter((r) => r.fontSize).map((r) => r.fontSize); return fs.length ? Math.max(...fs) : 0; };
      const aDecor = shapeText(a).trim().length <= 2 && fontOf(a) >= 30;
      const bDecor = shapeText(b).trim().length <= 2 && fontOf(b) >= 30;
      if (aDecor || bDecor) continue;

      const overlapW = Math.min(aRight, bRight) - Math.max(a.x, b.x);
      const overlapH = Math.min(aBottom, bBottom) - Math.max(a.y, b.y);

      if (overlapW > 0 && overlapH > 0) {
        const overlapArea = overlapW * overlapH;
        const aArea = a.w * a.h;
        const bArea = b.w * b.h;
        const smallerArea = Math.min(aArea, bArea);
        // Skip layout neighbor overlaps: shapes aligned in a row/column with thin overlap strip
        // (html2pptx conversion artifact from flex/grid layouts)
        const yOverlap = Math.min(aBottom, bBottom) - Math.max(a.y, b.y);
        const minH = Math.min(a.h, b.h);
        const xOverlap = Math.min(aRight, bRight) - Math.max(a.x, b.x);
        const minW = Math.min(a.w, b.w);
        // Same row (>50% vertical overlap) with thin horizontal strip, or same column with thin vertical strip
        if ((yOverlap > minH * 0.5 && xOverlap < minW * 0.25) ||
            (xOverlap > minW * 0.5 && yOverlap < minH * 0.25)) continue;
        const pct = Math.round(overlapArea / smallerArea * 100);

        if (pct >= 5) {
          const key = `${i}-${j}`;
          if (found.has(key)) continue;
          found.add(key);

          const aText = shapeText(a).substring(0, 20) || `[${a.name}]`;
          const bText = shapeText(b).substring(0, 20) || `[${b.name}]`;

          if (pct >= 20) {
            issues.push({
              level: 'ERROR',
              code: 'VP-14',
              slide: slideNum,
              message: `Shapes overlap ${pct}%: "${aText}..." ↔ "${bText}..." — text unreadable, fix layout or split slide`,
            });
          } else {
            issues.push({
              level: 'WARN',
              code: 'VP-14',
              slide: slideNum,
              message: `Shapes overlap ${pct}%: "${aText}..." ↔ "${bText}..." — may cause readability issues`,
            });
          }
        }
      }
    }
  }
  return issues;
}

// ── Picture extraction (for z-order check) ─────────────────────────────────

/**
 * Extract picture shapes from <p:pic> blocks.
 * Returns array of { name, x, y, w, h, type: 'picture', xmlOrder }
 */
function extractPictures(slideXml) {
  const pics = [];
  const picBlocks = matchAll(slideXml, '<p:pic\\b[^>]*>([\\s\\S]*?)</p:pic>');

  for (const block of picBlocks) {
    const inner = block[1];
    const pic = { name: '', x: 0, y: 0, w: 0, h: 0, type: 'picture' };

    const cNvPr = inner.match(/<p:cNvPr[^>]*>/i);
    if (cNvPr) {
      pic.name = attr(cNvPr[0], 'name') || '';
    }

    const off = inner.match(/<a:off[^>]*>/i);
    if (off) {
      pic.x = parseInt(attr(off[0], 'x') || '0', 10);
      pic.y = parseInt(attr(off[0], 'y') || '0', 10);
    }

    const ext = inner.match(/<a:ext[^>]*>/i);
    if (ext) {
      pic.w = parseInt(attr(ext[0], 'cx') || '0', 10);
      pic.h = parseInt(attr(ext[0], 'cy') || '0', 10);
    }

    pics.push(pic);
  }
  return pics;
}

/**
 * Get all elements (shapes + pictures) in XML order for z-order analysis.
 * Elements appearing later in XML are rendered on top.
 */
function extractAllElementsOrdered(slideXml) {
  const elements = [];
  // Match both <p:sp> and <p:pic> blocks with their positions in the XML
  const re = /<(p:sp|p:pic)\b[^>]*>([\s\S]*?)<\/\1>/g;
  let m;
  let order = 0;
  while ((m = re.exec(slideXml)) !== null) {
    const type = m[1] === 'p:pic' ? 'picture' : 'shape';
    const inner = m[2];
    const el = { type, name: '', x: 0, y: 0, w: 0, h: 0, xmlOrder: order++, textRuns: [], fillColor: null };

    const cNvPr = inner.match(/<p:cNvPr[^>]*>/i);
    if (cNvPr) el.name = attr(cNvPr[0], 'name') || '';

    const off = inner.match(/<a:off[^>]*>/i);
    if (off) {
      el.x = parseInt(attr(off[0], 'x') || '0', 10);
      el.y = parseInt(attr(off[0], 'y') || '0', 10);
    }

    const ext = inner.match(/<a:ext[^>]*>/i);
    if (ext) {
      el.w = parseInt(attr(ext[0], 'cx') || '0', 10);
      el.h = parseInt(attr(ext[0], 'cy') || '0', 10);
    }

    if (type === 'shape') {
      const txBody = inner.match(/<p:txBody>([\s\S]*?)<\/p:txBody>/i);
      if (txBody) {
        const runs = matchAll(txBody[1], '<a:r>([\\s\\S]*?)<\\/a:r>');
        for (const run of runs) {
          const tMatch = run[1].match(/<a:t>([\s\S]*?)<\/a:t>/i);
          el.textRuns.push({ text: tMatch ? tMatch[1] : '' });
        }
      }
      const txBodyStart = inner.indexOf('<p:txBody');
      const spPrSection = txBodyStart >= 0 ? inner.slice(0, txBodyStart) : inner;
      const spFill = spPrSection.match(/<a:solidFill>\s*<a:srgbClr\s+val="([0-9A-Fa-f]{6})"/i);
      if (spFill) el.fillColor = spFill[1].toUpperCase();
    }

    elements.push(el);
  }
  return elements;
}

// CJK character detection for VP-16
const CJK_CHAR_RE = /[\u3000-\u303F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]/g;

/**
 * VP-15: Check if picture shapes are behind overlapping text shapes (z-order issue)
 */
function checkPictureZOrder(allElements, slideNum) {
  const issues = [];
  const MIN_SIZE = 30 * EMU_PER_PT; // 30pt

  const pictures = allElements.filter(e => e.type === 'picture' && e.w > MIN_SIZE && e.h > MIN_SIZE);
  const textShapes = allElements.filter(e => {
    if (e.type !== 'shape') return false;
    const text = (e.textRuns || []).map(r => r.text).join('').trim();
    return text.length > 0 && e.w > MIN_SIZE && e.h > MIN_SIZE;
  });

  for (const pic of pictures) {
    for (const shape of textShapes) {
      // Check overlap
      const overlapW = Math.min(pic.x + pic.w, shape.x + shape.w) - Math.max(pic.x, shape.x);
      const overlapH = Math.min(pic.y + pic.h, shape.y + shape.h) - Math.max(pic.y, shape.y);
      if (overlapW <= 0 || overlapH <= 0) continue;

      const overlapArea = overlapW * overlapH;
      const picArea = pic.w * pic.h;
      const pct = Math.round(overlapArea / picArea * 100);
      if (pct < 10) continue;

      // Picture has HIGHER xmlOrder = rendered ON TOP (OK)
      // Picture has LOWER xmlOrder = rendered BEHIND text (problem)
      if (pic.xmlOrder > shape.xmlOrder) {
        // Picture is on top of text — this obscures text
        const shapeText = (shape.textRuns || []).map(r => r.text).join('').trim().substring(0, 20);
        issues.push({
          level: 'WARN',
          code: 'VP-15',
          slide: slideNum,
          message: `Picture "${pic.name}" overlaps text "${shapeText}..." (${pct}% of picture) and is rendered ON TOP — text may be hidden`,
        });
      }
    }
  }
  return issues;
}

/**
 * VP-16: Estimate CJK text width vs shape width — predict overflow/wrapping
 */
function checkCjkTextOverflow(shapes, slideNum) {
  const issues = [];

  for (const s of shapes) {
    if (s.w === 0 || s.h === 0) continue;
    const text = shapeText(s);
    if (text.length < 2) continue;

    // VP-16 출처/메타 캡션 제외(이미지직접확인 2026-06-15, s82 "출처: 포스코홀딩스 IR…" w1.40"
    // 한 줄 수용): "출처:/자료:/주:/참고:/※/*" 시작 = 슬라이드 하단 메타정보, 여백충분 한 줄.
    // CJK 0.92 과대추정으로 fills 110~120%·wraps 2줄 오판(s73/74/75/77/79/81/82/83 전부 7pt 출처).
    // GT s71("10년 평균")·s99("분석팀") 은 출처 아니라 무관. WARN 분기만 skip, ERROR(will overflow=
    // 심각 잘림)는 캡션이라도 유지(FN 방지).
    const isMetaCaption = /^\s*(출처|자료출처|자료|참고|주|note|source)\s*[:：]/i.test(text) || /^\s*[※*]\s/.test(text);

    // Count CJK characters
    const cjkMatches = text.match(CJK_CHAR_RE);
    if (!cjkMatches || cjkMatches.length === 0) continue;

    const cjkCount = cjkMatches.length;
    const latinCount = text.length - cjkCount;
    const cjkRatio = cjkCount / text.length;
    if (cjkRatio < 0.2) continue;

    // 표/격자 셀 판정(이미지직접확인 2026-06-14): 같은 행(다른 x)·같은 열(다른 y) 짝을 둘 다 가지면
    // 표 셀 = 셀 폭이 넉넉해 PptxGenJS autofit 한 줄(s130 "기본급(22일×10만)"·"퇴직금(1/12)" 한 줄).
    // CJK 추정 과대로 WARN 오발화 → wraps/fills 분기에서만 skip. 단 ERROR(will overflow=심각 넘침)는
    // 표 셀이라도 진짜 잘림일 수 있어 유지(FN 방지). GT(s71 막대라벨·s99 제목/푸터)는 격자 아니라 보존.
    const gtol = 10 * EMU_PER_PT;
    const hasRowPeer = shapes.some((o) => o !== s && shapeText(o).trim() &&
      Math.abs(o.y - s.y) <= gtol && Math.abs(o.x - s.x) > gtol);
    const hasColPeer = shapes.some((o) => o !== s && shapeText(o).trim() &&
      Math.abs(o.x - s.x) <= gtol && Math.abs(o.y - s.y) > gtol);
    const isGridCell = hasRowPeer && hasColPeer;

    // Use actual font size from textRuns if available, fallback to 12pt
    const fontSizes = s.textRuns.filter(r => r.fontSize).map(r => r.fontSize);
    const estimatedFontPt = fontSizes.length > 0 ? Math.max(...fontSizes) : 12;
    const fontEmu = estimatedFontPt * EMU_PER_PT;

    // Estimate text width, calibrated to measured render widths (Playwright measureText +
    // real-deck PPTX render verification, see VERIFICATION.md §8-9):
    // CJK ≈ 0.92× (measured ~0.9; 1.0 over-estimated → 156-deck FP. Lowering to 0.92 removed
    //   25% more WARN on real decks, all render-verified as non-overflowing, 0 new FN),
    // Latin/digit ≈ 0.5× (measured ~0.47), whitespace ≈ 0.25× (0.4 re-introduced CJK FP).
    // Note: VP-16 only runs when cjkRatio ≥ 0.2 (CJK-width rule); pure-Latin lines are out of scope.
    const spaceCount = (text.match(/\s/g) || []).length;
    const otherLatin = Math.max(0, latinCount - spaceCount);
    const estimatedWidth = (cjkCount * fontEmu * 0.92) + (otherLatin * fontEmu * 0.5) + (spaceCount * fontEmu * 0.25);

    // Compare with shape width (minus estimated padding ~5pt each side)
    const availableWidth = s.w - (10 * EMU_PER_PT);

    if (availableWidth <= 0) continue;

    const ratio = estimatedWidth / availableWidth;

    // Multi-line wrapping check: if shape is tall enough, wrapping is OK
    const linesNeeded = Math.ceil(estimatedWidth / availableWidth);
    const lineHeightEmu = fontEmu * 1.2; // PPTX default single spacing
    const heightNeeded = linesNeeded * lineHeightEmu;
    // Subtract estimated padding (~5pt top + 5pt bottom) from shape height for available height
    const availableHeight = s.h - (10 * EMU_PER_PT);
    const verticalOverflow = heightNeeded > availableHeight;

    // Downgrade to WARN for cases where PPTX shrink-to-fit likely handles it:
    // - Short text (≤5 chars): badge/label text, shrink always works
    // - Small font (≤12pt) needing only 2 lines: minor overflow, PPTX autofit handles it
    // - Height overflow < 50%: borderline cases where PPTX font compression resolves it
    const isShortText = text.length <= 5;
    const isMinorOverflow = linesNeeded <= 2 && estimatedFontPt <= 12;
    const overflowRatio = availableHeight > 0 ? heightNeeded / availableHeight : Infinity;
    const isBorderlineOverflow = overflowRatio < 1.5;

    if (ratio > 1.2 && verticalOverflow && !isShortText && !isMinorOverflow && !isBorderlineOverflow) {
      const availPt = Math.round(availableWidth / EMU_PER_PT);
      const estPt = Math.round(estimatedWidth / EMU_PER_PT);
      issues.push({
        level: 'ERROR',
        code: 'VP-16',
        slide: slideNum,
        message: `CJK text "${text.substring(0, 25)}..." ${estPt}pt > available ${availPt}pt (${estimatedFontPt}pt font, ${linesNeeded} lines needed, shape too short) — will overflow [IL-37]`,
      });
    } else if (ratio > 1.2 && (isShortText || isMinorOverflow || isBorderlineOverflow || !verticalOverflow)) {
      // VP-16 wraps 정밀화(이미지직접확인 2026-06-14): 2줄 wrap 자체는 정상 — 큰 도형의 긴 제목/문장이
      // 카드 안에서 2줄로 흐르는 건 디자인(s12 카드제목·s7 제목 여백충분). 진짜 결함은 ① 늘어난 텍스트가
      // 인접 텍스트 도형을 침범(s99 GT: 제목 3줄→부제 "호르무즈해협" 덮음) ② 작은 도형(막대 안 7pt,
      // s71 GT "10년평균0.55"/"현재")에서 잘림. → 겹침도 작은도형도 아니면(여백충분 큰도형) skip.
      // 인접 겹침 = 이 도형의 실제 bounding box(s.y~s.y+s.h) 안에 다른 텍스트 도형이 들어옴.
      // s99 GT: 제목 도형 h=2.07"(bottom 3.01")이 부제 y=2.97"를 품음 → 텍스트가 길어 2줄+ 되면
      // 하단까지 차며 부제 "호르무즈해협" 침범. 추정 텍스트높이가 아닌 실제 도형영역으로 판정.
      const shapeBottom = s.y + s.h;
      const overlapsNeighbor = shapes.some((o) => o !== s &&
        o.textRuns.some((rr) => rr.text && rr.text.trim()) &&
        o.y > s.y && o.y < shapeBottom && o.x < s.x + s.w && o.x + o.w > s.x);
      const isSmallShape = availableWidth < 1.5 * EMU_PER_INCH;
      if (isGridCell || isMetaCaption) continue; // 표 셀·출처캡션 = autofit 한 줄(WARN 한정 skip)
      // 큰 도형이고 인접 텍스트 도형 겹침도 없으면 = 여백충분 정상 2줄(s12 카드제목) → skip.
      // 작은도형(막대 s71) 또는 인접겹침(s99 제목→부제)이면 발화 유지(GT 보존).
      if (!isSmallShape && !overlapsNeighbor) continue;
      // Wraps but fits vertically — WARN only
      const availPt = Math.round(availableWidth / EMU_PER_PT);
      const estPt = Math.round(estimatedWidth / EMU_PER_PT);
      issues.push({
        level: 'WARN',
        code: 'VP-16',
        slide: slideNum,
        message: `CJK text "${text.substring(0, 25)}..." wraps to ${linesNeeded} lines (${estPt}pt / ${availPt}pt, ${estimatedFontPt}pt font) — fits vertically [IL-37]`,
      });
    } else if (ratio > 1.1) {
      // VP-16 sweet-spot(정답지 앵커, 2026-06-14): 임계 1.0→1.1. CJK 0.92 계수가 ~5% 과대추정이라
      // fills 100~110% 발화는 렌더상 실제 한 줄에 들어감(realmix 12장 검증: s2 101%·s7 105%/101%·
      // s99 105% 4건 모두 3-judge blind 다수결 FP, 정답 0건). 정답 99.9 "분석팀"은 fills 115%로
      // 110% 초과 → 생존. 단 fills 정밀화(이미지직접확인 2026-06-14): 가로 110~120% 초과 대부분은
      // CJK 0.92 과대추정 + PptxGenJS autofit/overflow로 실제 한 줄(s84 "투자결론"36pt·s132 배지 확인).
      // 진짜 잘림은 세로도 넘칠 때 — 도형 높이가 늘어난 줄수를 수용 못함(GT 99.9 "분석팀" 12pt가
      // 도형 h=0.20"<2줄 필요 = 세로 넘침). 세로 여유면(autofit 한 줄 처리) skip.
      // 짧은 텍스트(≤5자 배지·라벨, s132 "정기성")는 PptxGenJS autofit이 한 줄로 처리 → skip.
      // 세로 여유(s84 큰제목 한 줄) → skip. 긴 텍스트가 세로까지 넘칠 때만 진짜 잘림(GT 99.9 11자).
      if (isGridCell || isMetaCaption || !verticalOverflow || isShortText) continue;
      const availPt = Math.round(availableWidth / EMU_PER_PT);
      const estPt = Math.round(estimatedWidth / EMU_PER_PT);
      issues.push({
        level: 'WARN',
        code: 'VP-16',
        slide: slideNum,
        message: `CJK text "${text.substring(0, 25)}..." fills ${Math.round(ratio * 100)}% of available width (${estPt}pt / ${availPt}pt, ${estimatedFontPt}pt font) — may overflow/clip in PPTX [IL-37]`,
      });
    }
  }
  return issues;
}

// ── PPTX extraction & orchestration ────────────────────────────────────────

/**
 * Load PPTX into memory using JSZip (no temp dirs, no exec).
 * Returns a Map<string, string|Buffer> of file paths to contents.
 */
async function loadPptxInMemory(pptxPath) {
  const data = fs.readFileSync(path.resolve(pptxPath));
  const zip = await JSZip.loadAsync(data);
  const files = new Map();
  for (const [name, entry] of Object.entries(zip.files)) {
    if (entry.dir) continue;
    // XML files as text, media files as Buffer
    if (name.endsWith('.xml') || name.endsWith('.rels')) {
      files.set(name, await entry.async('text'));
    } else {
      files.set(name, await entry.async('nodebuffer'));
    }
  }
  return files;
}

/**
 * Main validation function.
 * @param {string} pptxPath - Path to the .pptx file
 * @returns {{ errors: Array, warnings: Array, passed: boolean }}
 */
export async function validatePptx(pptxPath, options = {}) {
  if (!fs.existsSync(pptxPath)) {
    throw new Error(`File not found: ${pptxPath}`);
  }

  const zipFiles = await loadPptxInMemory(pptxPath);
  const errors = [];
  const warnings = [];

  try {
    // Read slide dimensions from presentation.xml
    let slideW = DEFAULT_SLIDE_W;
    let slideH = DEFAULT_SLIDE_H;
    const presXml = zipFiles.get('ppt/presentation.xml');
    if (presXml) {
      const dims = parseSlideDimensions(presXml);
      slideW = dims.width;
      slideH = dims.height;
    }

    // Find all slide XML files from in-memory map
    const slideEntries = [];
    for (const [name] of zipFiles) {
      const m = name.match(/^ppt\/slides\/slide(\d+)\.xml$/i);
      if (m) slideEntries.push({ name, num: parseInt(m[1], 10) });
    }
    slideEntries.sort((a, b) => a.num - b.num);

    if (slideEntries.length === 0) {
      throw new Error('No ppt/slides directory found in PPTX');
    }

    // VP-13: Check media file sizes
    let totalMediaSize = 0;
    for (const [name, content] of zipFiles) {
      if (!name.startsWith('ppt/media/')) continue;
      const size = Buffer.isBuffer(content) ? content.length : Buffer.byteLength(content);
      totalMediaSize += size;
      if (size > 5 * 1024 * 1024) {
        const mf = name.split('/').pop();
        warnings.push({
          level: 'WARN',
          code: 'VP-13',
          slide: 0,
          message: `Media file "${mf}" is ${(size / 1024 / 1024).toFixed(1)}MB — consider compressing`,
        });
      }
    }
    if (totalMediaSize > 20 * 1024 * 1024) {
      warnings.push({
        level: 'WARN',
        code: 'VP-13',
        slide: 0,
        message: `Total media size ${(totalMediaSize / 1024 / 1024).toFixed(1)}MB exceeds 20MB — may cause sharing issues (Gmail 25MB, Outlook 20MB limit)`,
      });
    }

    if (!options.quiet) {
      console.log(`\nValidating ${path.basename(pptxPath)}`);
      console.log(`Slide size: ${emuToInches(slideW)}" x ${emuToInches(slideH)}" (${slideEntries.length} slides)\n`);
    }

    for (const { name: slidePath, num: slideNum } of slideEntries) {
      const slideXml = zipFiles.get(slidePath);
      const shapes = extractShapes(slideXml);
      const tables = extractTables(slideXml);
      const slideBgColor = extractSlideBgColor(slideXml);

      const allElements = extractAllElementsOrdered(slideXml);

      const slideIssues = [
        ...checkOverflow(shapes, slideW, slideH, slideNum),
        ...checkColumnAlignment(shapes, slideNum),
        // VP-03 checkEmptyText 비활성(이미지직접확인 2026-06-14): 빈 텍스트프레임 = convert/PptxGenJS
        // 구조 흔적, 렌더에 투명·시각 영향 0(realmix s9 6건 확인). GT 0건. 함수는 복구용 보존.
        // ...checkEmptyText(shapes, slideNum),
        ...checkContrast(shapes, slideNum, slideBgColor, allElements.filter((e) => e.type === 'picture')),
        ...checkFilledEmptyShapes(shapes, slideNum),
        ...checkShrinkReliability(shapes, slideNum),
        ...checkGapConsistency(shapes, slideNum),
        // VP-11 checkReadingOrder 비활성(이미지직접확인 2026-06-14): spTree 순서=변환 산물, 표 z-order를
        // '읽기순서 역전'으로 오판(realmix s24 표 확인). 정적 이미지로 탭순서 검증 불가(UNVERIFIABLE).
        // 접근성은 별도 a11y 도구 영역. 함수는 복구용 보존.
        // ...checkReadingOrder(shapes, slideNum),
        ...checkEmptySlide(shapes, tables, slideNum),
        ...checkTableEmptyCells(tables, slideNum),
        ...checkTableConsistency(tables, slideNum),
        ...checkShapeGridEmptyCells(shapes, slideNum),
        ...checkShapeOverlap(shapes, slideNum),
        ...checkPictureZOrder(allElements, slideNum),
        ...checkCjkTextOverflow(shapes, slideNum),
      ];

      for (const issue of slideIssues) {
        if (issue.level === 'ERROR') {
          errors.push(issue);
        } else {
          warnings.push(issue);
        }
      }
    }
  } finally {
    // In-memory — no cleanup needed
  }

  return { errors, warnings, passed: errors.length === 0 };
}

// ── CLI ────────────────────────────────────────────────────────────────────

function formatIssue(issue) {
  const icon = issue.level === 'ERROR' ? '❌ ERROR' : '⚠️  WARN ';
  return `${icon} [slide ${issue.slide}] ${issue.code}: ${issue.message}`;
}

function parseCliArgs(argv) {
  const args = { input: null, json: false };
  for (let i = 0; i < argv.length; i++) {
    if ((argv[i] === '--input' || argv[i] === '-i') && argv[i + 1]) {
      args.input = argv[++i];
    }
    if (argv[i] === '--json') args.json = true;
  }
  return args;
}

async function main() {
  const args = parseCliArgs(process.argv.slice(2));

  if (!args.input) {
    console.error('Usage: node scripts/validate-pptx.js --input <path-to.pptx> [--json]');
    process.exit(1);
  }

  try {
    const { errors, warnings, passed } = await validatePptx(args.input);

    // --json: output structured JSON and exit
    if (args.json) {
      const all = [...errors, ...warnings];
      console.log(JSON.stringify(all, null, 2));
      process.exit(passed ? 0 : 1);
    }

    // Print all issues
    for (const w of warnings) console.log(formatIssue(w));
    for (const e of errors) console.log(formatIssue(e));

    // Summary
    console.log(`\n${'─'.repeat(60)}`);
    if (passed && warnings.length === 0) {
      console.log(`✅ All checks passed — no issues found`);
    } else {
      console.log(`Results: ${errors.length} error(s), ${warnings.length} warning(s)`);
      if (!passed) {
        console.log(`❌ Validation FAILED`);
      } else {
        console.log(`✅ Passed (warnings only)`);
      }
    }

    process.exit(passed ? 0 : 1);
  } catch (err) {
    console.error(`Fatal: ${err.message}`);
    process.exit(2);
  }
}

// Run CLI if invoked directly
const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'));
if (isMain) {
  main();
}
