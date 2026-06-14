import { validatePptx } from 'file:///D:/projects/design/scripts/validate-pptx.js';
const r = await validatePptx('C:/msys64/tmp/realmix.pptx', {});
const all=[...r.errors,...r.warnings];
const targets=[3,4,6,10,16,19,20,26,32,33,35,40,41,43,49,59,72,81,83,109,122,123,125,137,141,151,154,61,73,74,75,76,77,79,82,89,113,117];
for(const sn of [...new Set(targets)].sort((a,b)=>a-b)){
  const f=all.filter(x=>x.slide===sn && (x.code==='VP-04'||x.code==='VP-16'));
  if(f.length) console.log(`s${sn}: `+f.map(x=>x.code+' '+(x.message.match(/"#?[0-9A-Fa-f]{6}" on "#?[0-9A-Fa-f]{6}"|ratio: [\d.]+|wraps|fills \d+%|will overflow/g)||[]).join(' ')+' "'+(x.message.match(/"([^"]+)"\s*$|— "([^"]+)"/)||[])[1]+'"').join(' | '));
}
