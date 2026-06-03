const { chromium } = require('playwright');
const path = require('path');

const BASE = '/Users/tranmoo/neijing-notes/16-五脏应四时';
const IMG_DIR = path.join(BASE, 'images');
const OUT_DIR = path.join(BASE, 'img-temp');
const HTML = path.join(BASE, 'social-cards.html');

const CARDS = [
  'cover.jpg', 'card-01.jpg', 'card-02.jpg', 'card-03.jpg',
  'card-04.jpg', 'card-05.jpg', 'card-06.jpg', 'card-07.jpg', 'card-08.jpg'
];

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1024, height: 1536 }, deviceScaleFactor: 2 });

  const html = fs.readFileSync(HTML, 'utf-8');
  await page.goto('file://' + HTML, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const cards = await page.$$('.card');
  for (let i = 0; i < cards.length; i++) {
    const name = CARDS[i];
    await cards[i].screenshot({ path: path.join(OUT_DIR, name) });
    console.log(`✅ ${name}`);
  }

  await browser.close();
  console.log('\n🎉 All cards rendered!');
})();
