#!/usr/bin/env node
// VP-16 폭 계수 캘리브레이션용 — 실제 렌더 텍스트 폭을 측정해 CJK/Latin/공백 계수 역산.
// 반드시 레포 루트에서 실행(playwright 해결): cd design && node tests/ab-method/measure-cjk.mjs
// 폰트는 @font-face 미주입 시 Malgun Gothic fallback. PPTX는 Pretendard 임베드라
// 최종 채택 전 export-slides-png.ps1로 PPTX 렌더 교차 확인 필수(§README 5단계).
import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await b.newPage();
await p.setContent('<div id="t" style="font-family:Pretendard,\'Malgun Gothic\',sans-serif;font-size:100px;white-space:nowrap;position:absolute;left:0;top:0"></div>');
const samples = process.argv.slice(2).length ? process.argv.slice(2) : [
  'Total addressable market reached 320 billion now',
  '데이터센터 전력 효율 전년 대비 삼십이 퍼센트 개선',
  '분기 매출 전년比 12.4% 성장 달성',
];
for (const s of samples) {
  const w = await p.evaluate(t => { const e = document.getElementById('t'); e.textContent = t; return e.getBoundingClientRect().width; }, s);
  const cjk = (s.match(/[　-鿿가-힯＀-￯]/g) || []).length;
  const sp = (s.match(/\s/g) || []).length;
  const latin = s.length - cjk - sp;
  console.log(`실측em=${(w/100).toFixed(2)} | cjk=${cjk} latin=${latin} sp=${sp} | "${s.slice(0,24)}"`);
}
await b.close();
// 역산: 실측em = cjk*C + latin*L + sp*S 연립. 현 채택값 C=0.92 L=0.5 S=0.25 (VERIFICATION §9).
