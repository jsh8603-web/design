#!/usr/bin/env node
/**
 * skill-lint.mjs — Claude Code 인터페이스 무결성 린트.
 * 이 레포의 "API"는 SKILL.md/rules 다. 거기서 참조하는 파일 경로가 실제로 존재하는지,
 * 그리고 크로스-레포 참조(EXCEL_REPO)가 해소되는지 확인해 '조용한 에이전트 실패'를 막는다.
 *
 * Run: node tests/skill-lint.mjs        (exit 1 = 깨진 참조 있음)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCES = ['SKILL.md', 'README.md', 'dispatch.md'];
const RULE_DIR = path.join(ROOT, 'rules');

// 참조이되 파일 시스템 경로가 아닌(개념명·플레이스홀더) 토큰 — allow-list.
// 이동했거나 의도된 개념명은 여기에 흡수하고, 진짜 깨진 경로만 FAIL 시킨다.
// 아래 5종은 content-authoring.md 가 작업 중 *생성*하라고 안내하는 산출물명이지
// 레포에 상주해야 하는 파일이 아니다(00-brief/deck/deck-v1·v2 는 slides/<slug>/ 에 생성,
// verify.py 는 "의도적으로 코드를 안 박았음" 명시). → 흡수.
const ALLOW = new Set([
  '00-brief.md',   // slides/<slug>/00-brief.md 로 작업 시작 시 생성
  'deck.md',       // slides/<slug>/deck.md 아웃라인 산출물
  'deck-v1.md',    // 버저닝 산출물명
  'deck-v2.md',    // 버저닝 산출물명
  'verify.py',     // 받을 추출본 검증 스크립트(의도적 미수록)
  'content-gate.py', // excel 레포 소유 — design 은 호출 계약만(SKILL.md §5), ROOT 부재가 정상
  'slide-outline.md', // Step 1 에서 slides/<slug>/ 에 생성하는 아웃라인 산출물
  'slide-NN.html',    // Step 2 생성 슬라이드 파일명 플레이스홀더(NN)
]);

// 백틱 안의 경로 같은 토큰: `scripts/x.js`, `design-system/...`, `tests/...`
const PATHLIKE = /`([A-Za-z0-9_./-]+\.(?:js|mjs|cjs|py|md|json|css|html|yml|yaml|csv|xlsx))`/g;
const DIRLIKE = /`((?:scripts|design-system|pipelines|rules|src|bin|tests|skills)\/[A-Za-z0-9_./-]+\/?)`/g;

export function lintFile(absFile) {
  const broken = [];
  if (!fs.existsSync(absFile)) return [{ ref: path.basename(absFile), reason: 'source file missing' }];
  const txt = fs.readFileSync(absFile, 'utf8');
  const seen = new Set();
  for (const re of [PATHLIKE, DIRLIKE]) {
    for (const m of txt.matchAll(re)) {
      const ref = m[1].replace(/\/$/, '');
      if (seen.has(ref)) continue; seen.add(ref);
      if (/^https?:|^\+|node_modules|^\.\.?$/.test(ref)) continue;
      if (ALLOW.has(ref)) continue;
      if (!fs.existsSync(path.join(ROOT, ref))) broken.push({ ref, in: path.basename(absFile) });
    }
  }
  return broken;
}

export function lintAll() {
  const files = [...SOURCES.map(f => path.join(ROOT, f))];
  if (fs.existsSync(RULE_DIR)) for (const f of fs.readdirSync(RULE_DIR).filter(x => x.endsWith('.md'))) files.push(path.join(RULE_DIR, f));
  let broken = [];
  for (const f of files) if (fs.existsSync(f)) broken = broken.concat(lintFile(f));
  // cross-repo: EXCEL_REPO 해소되나
  const excel = process.env.EXCEL_REPO || path.join(ROOT, '..', 'excel');
  const excelOk = fs.existsSync(excel) && fs.existsSync(path.join(excel, 'main.py'));
  return { broken, excel, excelOk };
}

// pathToFileURL handles Windows backslash paths (a bare `file://${argv[1]}` won't match).
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { broken, excel, excelOk } = lintAll();
  for (const b of broken) console.log(`  ✗ 깨진 참조: ${b.ref}  (in ${b.in})`);
  console.log(excelOk ? `  ✓ EXCEL_REPO 해소: ${excel}` : `  ⚠ EXCEL_REPO 미해소: ${excel} (content-gate 라우팅엔 필요)`);
  console.log(`${broken.length ? 'FAIL' : 'PASS'}: ${broken.length} broken reference(s)`);
  process.exit(broken.length ? 1 : 0);
}
