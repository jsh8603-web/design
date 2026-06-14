// FN 검증(VP): convert-native 가 상류 차단하는 결함(오프슬라이드·그림겹침·테이블)을
// PPTX XML 에 직접 주입해, 결함 존재 시 VP 규칙이 발화하는지(=FN 0) 확인한다.
// 사용: node inject-vp-defects.mjs <base.pptx> <out.pptx>
//   이후: node scripts/validate-pptx.js --input <out.pptx>  → VP-01/05/06/12/15 발화 확인
//   VP-13 은 별도(미디어>5MB 주입). VP-08 은 slides/rule-audit/slide-vp08.html 로 검증.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const JSZip = require(path.resolve(process.cwd(), 'node_modules/jszip'));
const BASE = process.argv[2] || 'C:/msys64/tmp/realmix.pptx';
const OUT = process.argv[3] || 'C:/msys64/tmp/fn-inject.pptx';

const NS = '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">';
const TREE_OPEN = '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>';
const TREE_CLOSE = '</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping/></p:clrMapOvr></p:sld>';

const IN = 914400;
function sp(id, name, x, y, w, h, text, fill) {
  const fillXml = fill ? `<a:solidFill><a:srgbClr val="${fill}"/></a:solidFill>` : '';
  const txt = text != null
    ? `<p:txBody><a:bodyPr/><a:p><a:r><a:t>${text}</a:t></a:r></a:p></p:txBody>`
    : `<p:txBody><a:bodyPr/><a:p/></p:txBody>`;
  return `<p:sp><p:nvSpPr><p:cNvPr id="${id}" name="${name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="${Math.round(x*IN)}" y="${Math.round(y*IN)}"/><a:ext cx="${Math.round(w*IN)}" cy="${Math.round(h*IN)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>${fillXml}</p:spPr>${txt}</p:sp>`;
}
function pic(id, name, x, y, w, h) {
  return `<p:pic><p:nvPicPr><p:cNvPr id="${id}" name="${name}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rId99"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="${Math.round(x*IN)}" y="${Math.round(y*IN)}"/><a:ext cx="${Math.round(w*IN)}" cy="${Math.round(h*IN)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>`;
}
function tableCell(text, attrs='') {
  return `<a:tc${attrs}><a:txBody><a:bodyPr/><a:p><a:r><a:t>${text}</a:t></a:r></a:p></a:txBody><a:tcPr/></a:tc>`;
}
function tableFrame(rows) {
  const trs = rows.map(cells => `<a:tr h="370840">${cells}</a:tr>`).join('');
  return `<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="50" name="testTable"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="${Math.round(0.5*IN)}" y="${Math.round(1*IN)}"/><a:ext cx="${Math.round(6*IN)}" cy="${Math.round(2*IN)}"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl><a:tblPr/><a:tblGrid><a:gridCol w="${Math.round(2*IN)}"/><a:gridCol w="${Math.round(2*IN)}"/><a:gridCol w="${Math.round(2*IN)}"/></a:tblGrid>${trs}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>`;
}
function slide(body){ return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+NS+TREE_OPEN+body+TREE_CLOSE; }

// slide1: VP-01(우경계초과 7.5+4=11.5>10) + VP-15(pic가 text 뒤=위로 겹침)
const s1 = slide(
  sp(10,'OffSlide',7.5,2,4,1,'경계초과박스','1428A0') +
  sp(11,'BehindText',1,3.2,4,1,'그림에 가려질 텍스트',null) +
  pic(12,'CoverPic',1,3.2,4,1)
);
// slide2: VP-05(빈셀) + VP-06(열수불일치: 헤더3, 마지막행2)
const s2 = slide(
  sp(20,'Title2',0.5,0.3,6,0.5,'테이블 결함',null) +
  tableFrame([
    tableCell('지표')+tableCell('2024')+tableCell('2025'),
    tableCell('매출')+tableCell('100')+tableCell('120'),
    tableCell('영업이익')+tableCell('')+tableCell('30'),
    tableCell('순이익')+tableCell('25')
  ])
);
// slide3: VP-12(도형 1개)
const s3 = slide( sp(30,'Lonely',1,1,3,1,'외톨이 도형',null) );

const zip = await JSZip.loadAsync(fs.readFileSync(BASE));
zip.file('ppt/slides/slide1.xml', s1);
zip.file('ppt/slides/slide2.xml', s2);
zip.file('ppt/slides/slide3.xml', s3);
zip.file('ppt/media/bigimage.png', Buffer.alloc(6 * 1024 * 1024, 1)); // VP-13: 6MB 미디어
fs.writeFileSync(OUT, await zip.generateAsync({ type: 'nodebuffer' }));
console.log(`주입 완료 → ${OUT}: slide1(VP-01+15) slide2(VP-05+06) slide3(VP-12) media(VP-13)`);
