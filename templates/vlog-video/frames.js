// usage: node frames.js <html> <outdir> <nframes>
const { chromium } = require('playwright');
(async () => {
  const [html, out, n] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + html + '?n=' + Date.now()); await pg.waitForTimeout(400);
  for (let i = 0; i < +n; i++) {
    await pg.evaluate(t => setT(t), i / 30);
    await pg.screenshot({ path: `${out}/${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 90 });
  }
  await b.close();
})();
