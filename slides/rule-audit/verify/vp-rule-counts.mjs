import { validatePptx } from 'file:///D:/projects/design/scripts/validate-pptx.js';
const r = await validatePptx('C:/msys64/tmp/realmix.pptx', {});
const E={},W={};
for(const x of r.errors)E[x.code]=(E[x.code]||0)+1;
for(const x of r.warnings)W[x.code]=(W[x.code]||0)+1;
const codes=[...new Set([...Object.keys(E),...Object.keys(W)])].sort();
console.log('=== VP 전 룰 발화 (errors 21 + warnings 132) ===');
for(const c of codes)console.log(`${c}: E${E[c]||0} W${W[c]||0}`);
// 점검여부 표시
const seen={'VP-04':'GT+잔존 다수','VP-16':'GT+wraps/fills 다수','VP-02':'s8','VP-03':'s9','VP-10':'s124','VP-11':'s24','VP-09':'s110 1장'};
console.log('\n=== 미점검 룰 ===');
for(const c of codes)if(!seen[c])console.log(`  ${c}: E${E[c]||0} W${W[c]||0} ← 이미지 미확인`);
// VP-14 ERROR 내용
console.log('\n=== VP-14 발화 내용 ===');
for(const x of [...r.errors,...r.warnings].filter(x=>x.code==='VP-14'))console.log('  ',x.level,`s${x.slide}`,x.message.slice(0,75));
console.log('=== VP-07 ===');
for(const x of [...r.errors,...r.warnings].filter(x=>x.code==='VP-07'))console.log('  ',x.level,`s${x.slide}`,x.message.slice(0,75));
