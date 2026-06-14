import { validatePptx } from 'file:///D:/projects/design/scripts/validate-pptx.js';
import fs from 'fs';
const r = await validatePptx('C:/msys64/tmp/realmix.pptx', {});
const all=[...r.errors,...r.warnings];
const vp16=all.filter(x=>x.code==='VP-16');
const b={will:0,wraps:0,fills:0};
for(const x of vp16){if(x.message.includes('will overflow'))b.will++;else if(x.message.includes('wraps to'))b.wraps++;else if(x.message.includes('fills'))b.fills++;}
console.log('VP-16:', vp16.length, JSON.stringify(b), '(이전 will4/wraps127/fills41)');
// GT 4건 VP-16 보존
const gt=[{sn:71,t:'10년 평균 0.55배'},{sn:71,t:'현재'},{sn:99,t:'중동 지정학'},{sn:99,t:'분석팀'}];
let ok=0;
for(const g of gt){const hit=vp16.find(x=>x.slide===g.sn&&x.message.includes(g.t));console.log(hit?'  OK':'  ✗LOST',`s${g.sn} "${g.t}"`,hit?hit.message.match(/(wraps to|fills|will)[^[]*/)[0].slice(0,40):'');if(hit)ok++;}
console.log(`GT VP-16 보존: ${ok}/4`);
// 전체 GT 13
const gtj=JSON.parse(fs.readFileSync('slides/rule-audit/ab-verify/groundtruth.json'));
let g13=0;for(const f of gtj.realFlags){const sn=+f.id.split('.')[0];if(all.find(x=>x.code===f.code&&x.slide===sn))g13++;}
console.log(`전체 GT: ${g13}/13`);
console.log('총 WARN:', r.warnings.length, 'errors:', r.errors.length);
