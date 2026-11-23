// usage: node render.js <outDir> <fromSec> <toSec> [fps] [step]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const [outDir = 'frames', from = '0', to = '11', fps = '30', step = '1'] = process.argv.slice(2);
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); res.end(d); });
}).listen(8765);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('page:', m.text()));
  page.on('pageerror', e => console.log('ERR:', e.message));
  await page.goto('http://localhost:8765/scene.html');
  await page.waitForFunction(() => window.READY && window.renderFrame, null, { timeout: 60000 });
  const F = +fps, a = Math.round(+from * F), b = Math.round(+to * F);
  const t0 = Date.now();
  for (let f = a; f < b; f += +step) {
    const url = await page.evaluate(t => window.renderFrame(t), f / F);
    fs.writeFileSync(path.join(outDir, `f_${String(f).padStart(5, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
    if (f % 30 === 0) console.log('frame', f, ((Date.now() - t0) / 1000).toFixed(1) + 's');
  }
  await browser.close(); server.close();
})();
