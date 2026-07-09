#!/usr/bin/env python3
"""
Generate 21:9 Ghost feature + WeChat feature images for all 8 early articles.
Uses Playwright to render editorial-magazine-style cards at 2100×900 px.
"""
import os, json, subprocess, tempfile
from pathlib import Path

BASE = Path("/Users/tranmoo/neijing-notes")

ARTICLES = {
    "00-序": {
        "dir": "00-序",
        "ghost_title": "我爸扎了一辈子针<br>我现在才开始读《内经》",
        "ghost_sub": "序章 · 开篇",
        "wechat_title": "序：一个不太想学医的孩子",
        "wechat_sub": "学渣读内经 · 序章 · 第一篇",
    },
    "01-法于阴阳": {
        "dir": "01-法于阴阳",
        "ghost_title": "开头这一句<br>我读了三遍还是没懂",
        "ghost_sub": "第一篇 · 法于阴阳",
        "wechat_title": "\"法于阴阳\"四个字像鳗鱼",
        "wechat_sub": "学渣读内经 · 第一篇",
    },
    "02-古人骂街": {
        "dir": "02-古人骂街",
        "ghost_title": "古人骂街<br>两千年没过期",
        "ghost_sub": "第二篇 · 生气通天论",
        "wechat_title": "\"今时之人\"说的就是你",
        "wechat_sub": "学渣读内经 · 第二篇",
    },
    "03-女七男八": {
        "dir": "03-女七男八",
        "ghost_title": "古人排好了时间表<br>我对进去之后沉默了",
        "ghost_sub": "第三篇 · 女七男八",
        "wechat_title": "你现在在哪一格？",
        "wechat_sub": "学渣读内经 · 第三篇",
    },
    "04-四种人": {
        "dir": "04-四种人",
        "ghost_title": "《内经》里的四种人<br>我连最低档都没达到",
        "ghost_sub": "第四篇 · 四种人",
        "wechat_title": "最低档不是用来考的",
        "wechat_sub": "学渣读内经 · 第四篇",
    },
    "09-圣人治未病": {
        "dir": "09-圣人治未病",
        "ghost_title": "渴了才挖井<br>来得及吗？",
        "ghost_sub": "第九篇 · 四气调神大论",
        "wechat_title": "圣人不治已病治未病",
        "wechat_sub": "学渣读内经 · 第九篇",
    },
    "12-风邪百病": {
        "dir": "12-风邪百病",
        "ghost_title": "为什么偏偏是\"风\"<br>排在百病之首？",
        "ghost_sub": "第十二篇 · 生气通天论",
        "wechat_title": "风为百病之始",
        "wechat_sub": "学渣读内经 · 第十二篇",
    },
    "13-煎厥与薄厥": {
        "dir": "13-煎厥与薄厥",
        "ghost_title": "阳气崩溃的几种死法<br>古人写得像病历",
        "ghost_sub": "第十三篇 · 生气通天论",
        "wechat_title": "要么慢慢煮干，要么瞬间爆掉",
        "wechat_sub": "学渣读内经 · 第十三篇",
    },
}

# HTML Template — Editorial Magazine style for 21:9 feature cards
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  width: 2100px;
  height: 900px;
  overflow: hidden;
  font-family: 'Noto Serif SC', 'Songti SC', serif;
  background: #1a1512;
}

.card {
  width: 2100px;
  height: 900px;
  position: relative;
  display: flex;
  align-items: center;
}

/* Background image with dark gradient overlay */
.bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 2100px;
  height: 900px;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(10,8,6,0.85) 0%, rgba(10,8,6,0.60) 40%, rgba(10,8,6,0.30) 70%, transparent 100%);
}

/* Paper texture overlay */
.texture {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(255,255,255,0.015) 2px,
    rgba(255,255,255,0.015) 3px
  );
  opacity: 0.6;
}

/* Left decorative vertical line */
.deco-line {
  position: absolute;
  left: 80px;
  top: 120px;
  width: 2px;
  height: 660px;
  background: linear-gradient(180deg, rgba(232,213,183,0.8) 0%, rgba(232,213,183,0.2) 60%, transparent 100%);
}

/* Content area */
.content {
  position: relative;
  z-index: 2;
  padding: 120px 100px 120px 140px;
  width: 85%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Title decoration line */
.title-deco {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #e8d5b7, transparent);
  margin-bottom: 24px;
}

/* Title */
.__TITLE_CLASS__ {
  font-weight: 900;
  letter-spacing: 0.08em;
  color: #f5f0e6;
  line-height: 1.2;
  margin-bottom: 28px;
  max-width: 1700px;
}

/* Subtitle */
.subtitle {
  font-size: 32px;
  font-weight: 400;
  letter-spacing: 0.15em;
  color: rgba(232,213,183,0.9);
  margin-bottom: 0;
}

/* Bottom right corner decoration */
.corner-br {
  position: absolute;
  right: 80px;
  bottom: 80px;
  width: 80px;
  height: 80px;
  border-right: 2px solid rgba(232,213,183,0.4);
  border-bottom: 2px solid rgba(232,213,183,0.4);
}

/* Upper right vertical text */
.vertical-label {
  position: absolute;
  right: 70px;
  top: 160px;
  writing-mode: vertical-rl;
  font-size: 18px;
  letter-spacing: 0.3em;
  color: rgba(232,213,183,0.35);
  font-family: 'Noto Serif SC', serif;
}
</style>
</head>
<body>
<div class="card">
  <img class="bg" src="__BG_PATH__" alt="">
  <div class="overlay"></div>
  <div class="texture"></div>
  <div class="deco-line"></div>
  <div class="corner-br"></div>
  <div class="vertical-label">黄帝内经</div>
  <div class="content">
    <div class="title-deco"></div>
    <div class="__TITLE_CLASS__">__TITLE__</div>
    <div class="subtitle">__SUBTITLE__</div>
  </div>
</div>
</body>
</html>
"""

def check_title_length(title):
    """Check if title (without br tags) exceeds 20 chars"""
    plain = title.replace("<br>", "").replace("\n", "")
    return "title-long" if len(plain) > 20 else "title"

def generate_all():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 2100, "height": 900},
            device_scale_factor=1
        )

        for slug, info in ARTICLES.items():
            article_dir = BASE / info["dir"]
            img_dir = article_dir / "images"
            soc_dir = article_dir / "social-card"
            out_dir = soc_dir / "output"
            out_dir.mkdir(parents=True, exist_ok=True)

            # Find background image (use existing horizontal cover.jpg)
            bg_src = img_dir / "cover.jpg"
            if not bg_src.exists():
                print(f"  SKIP {slug}: no cover.jpg")
                continue

            bg_abs = str(bg_src.resolve())

            variants = [
                ("ghost-feature.jpg", info["ghost_title"], info["ghost_sub"]),
                ("wechat-feature.jpg", info["wechat_title"], info["wechat_sub"]),
            ]

            for fname, title, subtitle in variants:
                title_class = check_title_length(title)
                html = (HTML_TEMPLATE
                    .replace("__TITLE__", title)
                    .replace("__TITLE_CLASS__", title_class)
                    .replace("__SUBTITLE__", subtitle)
                    .replace("__BG_PATH__", bg_abs))

                tmp_html = tempfile.mktemp(suffix=".html")
                with open(tmp_html, "w", encoding="utf-8") as f:
                    f.write(html)

                out_path = str(out_dir / fname)
                page.goto(f"file://{tmp_html}", wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(3000)  # fonts + images
                page.screenshot(path=out_path, full_page=False, clip={"x": 0, "y": 0, "width": 2100, "height": 900})
                os.remove(tmp_html)

                size_kb = os.path.getsize(out_path) / 1024
                print(f"  {slug}/{fname}: {size_kb:.0f}KB")

        browser.close()

    print("\nDone! All feature images generated.")

if __name__ == "__main__":
    generate_all()
