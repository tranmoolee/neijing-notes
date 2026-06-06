const { chromium } = require('playwright');
const path = require('path');

const dir = path.resolve(__dirname);
const htmlPath = 'file://' + path.join(dir, 'index.html');
const output = path.join(dir);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 2400, height: 1600 } });
  await page.goto(htmlPath, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  const wechat = await page.$('#wechat-header');
  if (wechat) {
    await wechat.screenshot({ path: path.join(output, 'wechat-header-21x9.png') });
    console.log('✅ wechat-header-21x9.png');
  }
  const ghost = await page.$('#ghost-feature');
  if (ghost) {
    await ghost.screenshot({ path: path.join(output, 'ghost-feature-21x9.png') });
    console.log('✅ ghost-feature-21x9.png');
  }
  await browser.close();
  console.log('Done');
})();
