const { chromium } = require('playwright');
const path = require('path');

const TASK_DIR = "/Users/tranmoo/neijing-notes/生气通天论-小结";
const HTML_FILE = path.join(TASK_DIR, "social-cards.html");
const OUTPUT_DIR = path.join(TASK_DIR, "xhs-publish-pack/images");
const CARDS = [
  "xhs-cover",
  "xhs-01", "xhs-02", "xhs-03", "xhs-04",
  "xhs-05", "xhs-06", "xhs-07", "xhs-08"
];
const FILE_NAMES = [
  "cover.jpg",
  "card-01.jpg", "card-02.jpg", "card-03.jpg", "card-04.jpg",
  "card-05.jpg", "card-06.jpg", "card-07.jpg", "card-08.jpg"
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  await page.goto(`file://${HTML_FILE}`, { waitUntil: "networkidle" });
  
  // Wait for all images to load
  await page.waitForTimeout(2000);
  
  for (let i = 0; i < CARDS.length; i++) {
    const selector = `#${CARDS[i]}`;
    const el = await page.$(selector);
    if (!el) {
      console.log(`❌ Element #${CARDS[i]} not found`);
      continue;
    }
    
    const outputPath = path.join(OUTPUT_DIR, FILE_NAMES[i]);
    await el.screenshot({ path: outputPath, type: "jpeg", quality: 92 });
    console.log(`✅ ${FILE_NAMES[i]} saved`);
  }
  
  await browser.close();
  console.log("\n🎉 全部 9 张 social card 渲染完成！");
})();
