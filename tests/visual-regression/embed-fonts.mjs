/**
 * PPTX font tooling — embed TrueType fonts into a .pptx (OOXML), and a
 * preflight guard that fails when a slide uses a typeface that won't travel.
 *
 * Why: pptxgenjs does NOT embed fonts. If the recipient lacks Pretendard the
 * deck silently falls back and the layout breaks. Two defenses:
 *   - embedFonts()   : write the fonts into the package (LibreOffice/Mac-PPT solid;
 *                      Windows PowerPoint wants EOT/.fntdata — see CAVEAT).
 *   - guardFonts()   : static check — every <a:latin> typeface used must be on
 *                      the allow-list (fonts we actually ship). Zero risk, CI-safe.
 *
 * Zero new npm deps (uses jszip, already a dependency).
 *
 * CAVEAT (from OOXML/PowerPoint reality): PowerPoint stores embedded fonts as
 * EOT-format *.fntdata (subsetted/compressed). Embedding raw TTF renders in
 * LibreOffice and recent Mac PowerPoint but may not on every Windows build.
 * The guard is the reliable safety net; embedding is best-effort portability.
 */
import fs from 'node:fs';
import path from 'node:path';
import JSZip from 'jszip';

const REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships';
const FONT_REL = `${REL_NS}/font`;

/** Shipped typefaces — the allow-list for guardFonts(). */
export const SHIPPED_TYPEFACES = ['Pretendard', 'Newsreader', 'JetBrains Mono'];
/** Generic/system families that are safe to leave unembedded. */
const SAFE_GENERIC = new Set([
  '', 'Calibri', 'Arial',
  // theme font-scheme placeholders (resolve via the deck theme — always safe)
  '+mn-lt', '+mj-lt', '+mn-ea', '+mj-ea', '+mn-cs', '+mj-cs',
]);

async function loadPptx(file) { return JSZip.loadAsync(fs.readFileSync(file)); }

/** Collect every typeface referenced in slide/master/layout XML. */
export async function usedTypefaces(file) {
  const zip = await loadPptx(file);
  const found = new Set();
  const targets = Object.keys(zip.files).filter(n => /ppt\/(slides|slideLayouts|slideMasters)\/.*\.xml$/.test(n));
  for (const n of targets) {
    const xml = await zip.file(n).async('string');
    for (const m of xml.matchAll(/typeface="([^"]*)"/g)) found.add(m[1]);
  }
  return [...found];
}

/**
 * Guard: throw if a deck uses a typeface that is neither shipped nor generic.
 * @returns {{ok:boolean, used:string[], offenders:string[]}}
 */
export async function guardFonts(file, { allow = SHIPPED_TYPEFACES } = {}) {
  const allowSet = new Set(allow);
  const used = await usedTypefaces(file);
  const offenders = used.filter(t => !allowSet.has(t) && !SAFE_GENERIC.has(t));
  return { ok: offenders.length === 0, used, offenders };
}

/**
 * Embed TTF fonts into a pptx.
 * @param {string} inFile   source .pptx
 * @param {string} outFile  destination .pptx
 * @param {Array<{typeface:string, regular?:string, bold?:string, italic?:string, boldItalic?:string}>} fonts
 *        each style value is a path to a .ttf/.otf file
 */
export async function embedFonts(inFile, outFile, fonts) {
  const zip = await loadPptx(inFile);

  // 1) [Content_Types].xml — default for fntdata
  let ct = await zip.file('[Content_Types].xml').async('string');
  if (!/Extension="fntdata"/.test(ct)) {
    ct = ct.replace('</Types>', '<Default Extension="fntdata" ContentType="application/x-fontdata"/></Types>');
    zip.file('[Content_Types].xml', ct);
  }

  // 2) write font binaries + collect rels
  const relsPath = 'ppt/_rels/presentation.xml.rels';
  let rels = await zip.file(relsPath).async('string');
  const existingIds = [...rels.matchAll(/Id="(rId\d+)"/g)].map(m => parseInt(m[1].slice(3)));
  let nextId = (existingIds.length ? Math.max(...existingIds) : 0) + 1;
  let fontIdx = 1;
  const relAdds = [];
  const embeddedEntries = [];
  const styleTag = { regular: 'p:regular', bold: 'p:bold', italic: 'p:italic', boldItalic: 'p:boldItalic' };

  for (const f of fonts) {
    const styleRels = [];
    for (const style of ['regular', 'bold', 'italic', 'boldItalic']) {
      if (!f[style]) continue;
      const data = fs.readFileSync(f[style]);
      const target = `fonts/font${fontIdx}.fntdata`;
      zip.file(`ppt/${target}`, data);
      const rId = `rId${nextId++}`;
      relAdds.push(`<Relationship Id="${rId}" Type="${FONT_REL}" Target="${target}"/>`);
      styleRels.push(`<${styleTag[style]} r:id="${rId}"/>`);
      fontIdx++;
    }
    embeddedEntries.push(`<p:embeddedFont><p:font typeface="${f.typeface}"/>${styleRels.join('')}</p:embeddedFont>`);
  }
  rels = rels.replace('</Relationships>', relAdds.join('') + '</Relationships>');
  zip.file(relsPath, rels);

  // 3) presentation.xml — embedTrueTypeFonts + embeddedFontLst (schema order: after notesSz)
  let pres = await zip.file('ppt/presentation.xml').async('string');
  if (!/embedTrueTypeFonts=/.test(pres)) {
    pres = pres.replace(/<p:presentation([^>]*)>/, '<p:presentation$1 embedTrueTypeFonts="1">')
               .replace('<p:presentation embedTrueTypeFonts="1"', '<p:presentation embedTrueTypeFonts="1"'); // no-op guard
  }
  const lst = `<p:embeddedFontLst>${embeddedEntries.join('')}</p:embeddedFontLst>`;
  if (/<\/p:notesSz>/.test(pres)) pres = pres.replace('</p:notesSz>', '</p:notesSz>' + lst);
  else pres = pres.replace('</p:presentation>', lst + '</p:presentation>');
  zip.file('ppt/presentation.xml', pres);

  const buf = await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  fs.writeFileSync(outFile, buf);
  return { outFile, fontsEmbedded: fontIdx - 1 };
}
