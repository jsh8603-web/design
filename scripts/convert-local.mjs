import PptxGenJS from 'pptxgenjs';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const html2pptx = require('./html2pptx-local.cjs');

const DEFAULT_SLIDES_DIR = 'slides';
const DEFAULT_OUTPUT = 'output-native.pptx';

function parseArgs(args) {
  const options = {
    slidesDir: DEFAULT_SLIDES_DIR,
    output: DEFAULT_OUTPUT
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--slides-dir' && args[i + 1]) { options.slidesDir = args[++i]; }
    if (args[i] === '--output' && args[i + 1]) { options.output = args[++i]; }
  }
  return options;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const slidesDir = path.resolve(options.slidesDir);
  const outputPath = path.resolve(options.output);

  const files = fs.readdirSync(slidesDir)
    .filter(f => /^slide-\d+[^]*\.html$/.test(f))
    .sort();

  if (files.length === 0) {
    console.error('No slide-*.html files found in', slidesDir);
    process.exit(1);
  }

  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_16x9';

  console.log(`Converting ${files.length} slides from ${slidesDir}...`);

  for (const file of files) {
    const filePath = path.join(slidesDir, file);
    process.stdout.write(`  Processing ${file}... `);
    try {
      await html2pptx(filePath, pptx);
      console.log('OK');
    } catch (err) {
      console.log('FAILED:', err.message);
    }
  }

  await pptx.writeFile({ fileName: outputPath });
  console.log(`\nSuccessfully saved PPTX to: ${outputPath}`);
}

main().catch(err => {
  console.error('\nConversion failed:', err);
  process.exit(1);
});
