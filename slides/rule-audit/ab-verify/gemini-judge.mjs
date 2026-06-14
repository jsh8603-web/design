// Gemini Pro vision 판정 헬퍼 — 슬라이드 이미지 + 우리 룰 기준 → 진짜 결함 목록(ground truth)
// 사용: node gemini-judge.mjs <image.png> <prompt.txt> <out.json> [pro|flash]
import fs from 'node:fs';
import https from 'node:https';
const [imgPath, promptPath, outPath, modelArg='pro'] = process.argv.slice(2);
const MODELS = { pro: 'gemini-2.5-pro', flash: 'gemini-3.1-flash-lite-preview' };
const model = MODELS[modelArg] || MODELS.pro;
const apiKey = process.env.GEMINI_RESEARCH_KEY || process.env.GEMINI_RESEARCH_FREE_KEY;
if (!apiKey) { console.error('no gemini key'); process.exit(1); }
const prompt = fs.readFileSync(promptPath, 'utf8');
const imgB64 = fs.readFileSync(imgPath).toString('base64');
const body = JSON.stringify({
  contents: [{ parts: [{ text: prompt }, { inlineData: { mimeType: 'image/png', data: imgB64 } }] }],
  generationConfig: { maxOutputTokens: 8192, temperature: 0.2 },
});
const urlObj = new URL(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`);
const req = https.request({ hostname: urlObj.hostname, path: urlObj.pathname + urlObj.search, method: 'POST', headers: { 'Content-Type': 'application/json' } }, (res) => {
  let data = ''; res.on('data', c => data += c);
  res.on('end', () => {
    try { const j = JSON.parse(data);
      if (j.error) { console.error('API err', j.error.code, j.error.message); process.exit(2); }
      const text = j.candidates?.[0]?.content?.parts?.map(p => p.text).join('\n') || '(no content)';
      fs.writeFileSync(outPath, text); console.log('OK', outPath, text.length+'chars');
    } catch (e) { console.error('parse err', e.message, data.slice(0,300)); process.exit(3); }
  });
});
req.on('error', e => { console.error('req err', e.message); process.exit(4); });
req.write(body); req.end();
