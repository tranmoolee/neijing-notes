#!/usr/bin/env node
/* Editorial × Midnight-Ink 五色五行 (DARK 国风) renderer — 仿14号暗调鎏金.
 * 深黑宣纸底 + SVG水墨雾(feTurbulence) + 远山 + 金晕; 宋体大字; 五色发亮.
 * 文字全部 HTML 渲染, 100% 精准. System Chrome headless, 1x 1080x1440.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const DIR = __dirname;
const OUT = path.join(DIR, "output-dark");
fs.mkdirSync(OUT, { recursive: true });
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// 程序化深色水墨国风背景：水墨雾 + 远山 + 金晕 + 月（可选）
function bg(seed, opt = {}) {
  const glowX = opt.glowX ?? 30,
    glowY = opt.glowY ?? 22,
    glow = opt.glow ?? 0.5,
    mist = opt.mist ?? 0.16,
    moon = opt.moon ? `<circle cx="880" cy="250" r="92" fill="none" stroke="rgba(224,196,140,.32)" stroke-width="3"/><circle cx="905" cy="235" r="92" fill="#0e0d0c"/>` : "";
  return `<svg class="bg" width="1080" height="1440" viewBox="0 0 1080 1440" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="mist${seed}" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.006 0.011" numOctaves="4" seed="${seed}" stitchTiles="stitch" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.80  0 0 0 0 0.70  0 0 0 0 0.52  0 0 0 0.85 0"/>
    </filter>
    <radialGradient id="glow${seed}" cx="${glowX}%" cy="${glowY}%" r="62%">
      <stop offset="0%" stop-color="rgba(224,182,110,${glow})"/>
      <stop offset="45%" stop-color="rgba(150,110,60,${glow * 0.28})"/>
      <stop offset="100%" stop-color="rgba(14,13,12,0)"/>
    </radialGradient>
    <linearGradient id="vig${seed}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba(0,0,0,0)"/>
      <stop offset="72%" stop-color="rgba(0,0,0,0)"/>
      <stop offset="100%" stop-color="rgba(0,0,0,.55)"/>
    </linearGradient>
  </defs>
  <rect width="1080" height="1440" fill="#0e0d0c"/>
  <rect width="1080" height="1440" fill="url(#glow${seed})"/>
  <g opacity="${mist}" style="mix-blend-mode:screen"><rect width="1080" height="1440" filter="url(#mist${seed})"/></g>
  ${moon}
  <path d="M0,1180 C220,1095 360,1170 560,1120 C760,1070 920,1150 1080,1110 L1080,1440 L0,1440 Z" fill="#16130f"/>
  <path d="M0,1290 C260,1230 420,1300 660,1255 C840,1222 980,1285 1080,1262 L1080,1440 L0,1440 Z" fill="#1d1812"/>
  <rect width="1080" height="1440" fill="url(#vig${seed})"/>
</svg>`;
}

// 五正色 → 五脏
const WU = {
  肝: { c: "qing", color: "var(--c-qing)", el: "东", season: "春", yu: "颈项" },
  心: { c: "chi", color: "var(--c-chi)", el: "南", season: "夏", yu: "胸胁" },
  脾: { c: "huang", color: "var(--c-huang)", el: "中", season: "长夏", yu: "脊" },
  肺: { c: "bai", color: "var(--c-bai)", el: "西", season: "秋", yu: "肩背" },
  肾: { c: "hei", color: "var(--c-hei)", el: "北", season: "冬", yu: "腰股" },
};
const swatch = (k) => `<span class="wu-dot wu-${WU[k].c}"></span>`;
const organ = (k) => `<span class="organ glow-${WU[k].c}" style="color:${WU[k].color}">${k}</span>`;

const posters = [];

// 01 · Cover
posters.push({
  id: "01-cover",
  bg: bg(7, { glowX: 28, glowY: 20, glow: 0.6, mist: 0.2, moon: true }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-3">
    <div class="issue-row"><span>金匮真言论</span><span class="dot"></span><span>No.15</span><span class="dot"></span><span>学渣读经</span></div>
    <div class="stack gap-2">
      <p class="kicker">封面 · 第十五篇</p>
      <h1 class="h-display cover-title">古人给五脏<br>做了一套<br>GPS 坐标</h1>
    </div>
    <span class="seal">內<br>經</span>
    <div class="grow"></div>
    <div class="wuxing-strip">
      ${["肝", "心", "脾", "肺", "肾"]
        .map(
          (k) => `<div class="wx-col">
        ${swatch(k)}
        <span class="wx-el">${WU[k].el}</span>
        <span class="wx-organ glow-${WU[k].c}" style="color:${WU[k].color}">${k}</span>
      </div>`
        )
        .join("")}
    </div>
    <p class="lead">方位、季节、脏腑、身体部位——<br>古人把它们对应成一张多维地图。</p>
  </div>
  <div class="issue-strip"><span>五脏坐标</span><span>—</span><span>素问 · 金匮真言论</span></div>
</section>`,
});

// 02 · 五色坐标表
posters.push({
  id: "02-table",
  bg: bg(13, { glowX: 78, glowY: 16, glow: 0.4, mist: 0.13 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">坐标表 · 五色入五脏</p>
    <h2 class="h-xl">一张五脏<br>坐标表</h2>
    <div class="wu-ledger spread">
      <div class="wu-head"><span>方位</span><span>季节</span><span>脏 · 色</span><span>俞 · 易病</span></div>
      ${["肝", "心", "肺", "肾", "脾"]
        .map(
          (k) => `<div class="wu-row">
        <span class="wu-el">${WU[k].el}</span>
        <span class="wu-season">${WU[k].season}</span>
        <span class="wu-organ">${swatch(k)}${organ(k)}</span>
        <span class="wu-yu">${WU[k].yu}</span>
      </div>`
        )
        .join("")}
    </div>
    <p class="body" style="color:var(--muted)">不是器官列表,是一张多维地图。</p>
  </div>
</section>`,
});

// 03 · 同类归组
const chain = (items, k) => {
  const nodes = items.map((t) => `<span class="cn">${t}</span>`).join(`<span class="ce">=</span>`);
  return `<div class="chain-row">${nodes}<span class="ce">=</span><span class="cn co glow-${WU[k].c}" style="color:${WU[k].color}">${k}</span></div>`;
};
posters.push({
  id: "03-group",
  bg: bg(21, { glowX: 24, glowY: 30, glow: 0.38, mist: 0.13 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">归组 · 同类相聚</p>
    <h2 class="h-xl">不是解剖学<br>是同类归组</h2>
    <div class="chains spread">
      ${chain(["东", "升起", "春", "生发"], "肝")}
      ${chain(["南", "最热", "夏", "旺盛"], "心")}
      ${chain(["西", "落下", "秋", "收敛"], "肺")}
      ${chain(["北", "最冷", "冬", "收藏"], "肾")}
    </div>
    <p class="body" style="color:var(--muted)">性质相似的东西归到同一组——<br>不是位置关系,是功能特征的分类。</p>
  </div>
</section>`,
});

// 04 · 俞 · 疼痛定位
const locate = [["脖子僵", "肝"], ["胸闷", "心"], ["肩背痛", "肺"], ["腰酸", "肾"]];
posters.push({
  id: "04-locate",
  bg: bg(34, { glowX: 80, glowY: 28, glow: 0.36, mist: 0.13 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">俞 · 疼痛定位</p>
    <h2 class="h-xl">哪里不舒服<br>提示哪个脏</h2>
    <div class="locate spread">
      ${locate
        .map(
          ([s, k]) => `<div class="lc-row">
        <span class="lc-sym">${s}</span>
        <span class="lc-arrow">→</span>
        <span class="lc-organ">${swatch(k)}<span class="glow-${WU[k].c}" style="color:${WU[k].color}">${k}</span></span>
      </div>`
        )
        .join("")}
    </div>
    <p class="body" style="color:var(--muted)">每个脏有一个容易出问题的反应区域。</p>
  </div>
</section>`,
});

// 05 · 脾在中央
posters.push({
  id: "05-spleen",
  bg: bg(45, { glowX: 50, glowY: 38, glow: 0.62, mist: 0.18 }),
  html: `
<section class="poster xhs">
  <div class="content stack" style="justify-content:center; gap:36px">
    <p class="kicker">中央为土 · 枢纽</p>
    <div class="row" style="align-items:center; gap:30px">
      <span class="wu-dot wu-huang big"></span>
      <h2 class="h-display glow-huang" style="margin:0; color:var(--c-huang)">脾在中央</h2>
    </div>
    <hr class="rule-accent" style="background:var(--c-huang); width:120px; height:3px">
    <p class="lead" style="font-size:34px">像东南西北四城之间的交通枢纽,<br>所有物资都经过它转运。</p>
    <p class="lead" style="font-size:34px">不偏不倚,却最不可或缺——<br>这就是"脾为后天之本"。</p>
  </div>
</section>`,
});

// 06 · 暂时的理解
const recap = [
  ["功能分组", "按性质相似归类,不按解剖位置"],
  ["多维对应", "每脏配方位 · 季节 · 风 · 部位"],
  ["实用价值", "哪季哪脏易病,症状帮你定位"],
  ["脾为枢纽", "居中调度,不偏一方,服务四方"],
];
posters.push({
  id: "06-recap",
  bg: bg(56, { glowX: 26, glowY: 22, glow: 0.36, mist: 0.13 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">暂时的理解 · 复盘</p>
    <h2 class="h-xl">这一段<br>我读到了什么</h2>
    <div class="ledger spread">
      ${recap
        .map(
          ([t, n], i) => `<div class="ledger-row">
        <span class="ledger-nb">0${i + 1}</span>
        <div><div class="ledger-title">${t}</div><div class="ledger-note">${n}</div></div>
      </div>`
        )
        .join("")}
    </div>
  </div>
</section>`,
});

// 07 · 留的坑
const pits = [
  '"俞"是穴位,还是泛指区域?',
  "这套方位,在南半球还适用吗?",
  '脾对应"长夏",还是"四季末各十八天"?',
  "这张表和四季养生是什么关系?",
];
posters.push({
  id: "07-pits",
  bg: bg(67, { glowX: 76, glowY: 24, glow: 0.34, mist: 0.12 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">留的坑 · 待解</p>
    <h2 class="h-xl">还没想明白<br>的几件事</h2>
    <div class="ledger spread">
      ${pits
        .map(
          (q, i) => `<div class="ledger-row">
        <span class="ledger-nb">0${i + 1}</span>
        <div class="ledger-title pit-q">${q}</div>
      </div>`
        )
        .join("")}
    </div>
  </div>
</section>`,
});

// 08 · 下期预告
posters.push({
  id: "08-next",
  bg: bg(78, { glowX: 50, glowY: 30, glow: 0.55, mist: 0.18 }),
  html: `
<section class="poster xhs">
  <div class="content stack gap-2">
    <p class="kicker">下期预告 · 下篇见</p>
    <h2 class="h-display" style="font-size:96px">每个脏<br>都有一张<br>身份证</h2>
    <div class="grow"></div>
    <div class="next-attrs">
      ${["颜色", "味道", "声音", "数字", "开窍"].map((a) => `<span class="attr-chip">${a}</span>`).join("")}
    </div>
    <hr class="rule">
    <p class="lead">信息量最大的一段,像在读数据库。</p>
    <p class="meta glow-qing" style="color:var(--c-qing)">东方青色,入通于肝 ——</p>
  </div>
</section>`,
});

// ---- task CSS --------------------------------------------------------------
const taskCss = `
  :root, [data-theme="midnight-ink"] { --accent:#d4a04a; --accent-rgb:212,160,74; }
  /* 五正色 · 深底增亮 */
  :root {
    --c-qing:#52b4a0;   /* 青 · 肝 */
    --c-chi:#e26a52;    /* 赤 · 心 */
    --c-huang:#e6b24e;  /* 黄 · 脾 */
    --c-bai:#efe7d5;    /* 白(素) · 肺 */
    --c-hei:#cfc4ad;    /* 黑→描边圈用 cream 边 */
  }
  .bg { position:absolute; inset:0; z-index:0; width:100%; height:100%; pointer-events:none; }
  .content { z-index:2; }
  .grow { flex:1; }
  .spread { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
  .cover-title { font-size:104px; line-height:1.08; }

  /* 朱砂印 */
  .seal { position:absolute; right:88px; top:300px; z-index:3;
    width:98px; height:98px; display:flex; align-items:center; justify-content:center;
    font-family:var(--serif-zh); font-weight:700; font-size:34px; line-height:1.02;
    color:#f4ece0; background:#a8392c; letter-spacing:.04em; text-align:center;
    box-shadow:0 0 0 1px rgba(244,236,224,.18), 0 6px 18px rgba(0,0,0,.5); }

  /* 五色点 + 发亮 */
  .wu-dot { display:inline-block; width:30px; height:30px; border-radius:50%; flex:0 0 auto; vertical-align:middle; }
  .wu-dot.big { width:60px; height:60px; }
  .wu-qing { background:var(--c-qing); box-shadow:0 0 18px rgba(82,180,160,.55); }
  .wu-chi  { background:var(--c-chi);  box-shadow:0 0 18px rgba(226,106,82,.55); }
  .wu-huang{ background:var(--c-huang);box-shadow:0 0 20px rgba(230,178,78,.6); }
  .wu-bai  { background:var(--c-bai);  box-shadow:0 0 18px rgba(239,231,213,.5); }
  .wu-hei  { background:transparent;   box-shadow:0 0 0 2px var(--c-hei) inset; }
  .glow-qing  { text-shadow:0 0 22px rgba(82,180,160,.45); }
  .glow-chi   { text-shadow:0 0 22px rgba(226,106,82,.45); }
  .glow-huang { text-shadow:0 0 24px rgba(230,178,78,.5); }
  .glow-bai   { text-shadow:0 0 20px rgba(239,231,213,.4); }
  .glow-hei   { text-shadow:none; }

  /* cover 五行 strip */
  .wuxing-strip { display:grid; grid-template-columns:repeat(5,1fr); gap:0; margin:8px 0;
    border-top:1px solid rgba(236,226,207,.18); border-bottom:1px solid rgba(236,226,207,.18); padding:30px 0; }
  .wx-col { display:flex; flex-direction:column; align-items:center; gap:14px; }
  .wx-el { font-family:var(--serif-zh); font-size:30px; color:var(--muted); }
  .wx-organ { font-family:var(--serif-zh); font-weight:700; font-size:52px; }

  /* 五色坐标表 */
  .wu-ledger { display:flex; flex-direction:column; margin-top:6px; }
  .wu-head, .wu-row { display:grid; grid-template-columns:1.1fr 1.4fr 1.6fr 1.4fr; align-items:center; gap:20px; }
  .wu-head { padding-bottom:14px; border-bottom:2px solid rgba(236,226,207,.5); }
  .wu-head span { font-family:var(--mono); font-size:21px; letter-spacing:.14em; color:var(--muted); }
  .wu-row { border-bottom:1px solid rgba(236,226,207,.14); }
  .wu-el     { font-family:var(--serif-zh); font-weight:500; font-size:54px; color:var(--ink); }
  .wu-season { font-family:var(--serif-zh); font-weight:400; font-size:40px; color:rgba(236,226,207,.78); }
  .wu-organ  { display:flex; align-items:center; gap:16px; }
  .wu-organ .organ { font-family:var(--serif-zh); font-weight:700; font-size:56px; }
  .wu-yu     { font-family:var(--serif-zh); font-weight:400; font-size:38px; color:var(--muted); }

  /* 同类归组 */
  .chains .chain-row { display:flex; align-items:center; flex-wrap:wrap; gap:16px;
    padding:24px 0; border-bottom:1px solid rgba(236,226,207,.14); }
  .chains .chain-row:last-child { border-bottom:0; }
  .chain-row .cn { font-family:var(--serif-zh); font-weight:500; font-size:42px; color:var(--ink); }
  .chain-row .cn.co { font-weight:700; font-size:52px; }
  .chain-row .ce { font-family:var(--mono); font-size:32px; color:var(--muted); }

  /* 疼痛定位 */
  .locate .lc-row { display:grid; grid-template-columns:1fr 70px 1fr; align-items:center; gap:32px;
    padding:30px 0; border-bottom:1px solid rgba(236,226,207,.14); }
  .locate .lc-row:last-child { border-bottom:0; }
  .lc-sym { font-family:var(--serif-zh); font-weight:500; font-size:56px; color:var(--ink); }
  .lc-arrow { font-family:var(--serif-zh); font-size:48px; color:var(--muted); text-align:center; }
  .lc-organ { display:flex; align-items:center; justify-content:flex-end; gap:18px;
    font-family:var(--serif-zh); font-weight:700; font-size:64px; }

  /* ledger note 在深底上提亮 */
  .ledger-row { border-bottom:1px solid rgba(236,226,207,.14) !important; }
  .ledger-note { color:rgba(236,226,207,.72) !important; }
  .pit-q { font-size:34px !important; line-height:1.4; font-weight:500; }

  /* 下期预告 chips */
  .next-attrs { display:flex; flex-wrap:wrap; gap:18px; margin:6px 0 4px; }
  .attr-chip { font-family:var(--serif-zh); font-weight:500; font-size:34px; color:var(--ink);
    padding:12px 28px; border:1px solid rgba(236,226,207,.28); background:rgba(236,226,207,.05); }

  .issue-strip { border-top-color:rgba(236,226,207,.2) !important; }
`;

// ---- render ----------------------------------------------------------------
const FONTS = `https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700;900&family=Noto+Sans+SC:wght@300;400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap`;
const targets = [];
for (const p of posters) {
  const file = path.join(DIR, `_dk-${p.id}.html`);
  const page = `<!doctype html><html lang="zh-CN" data-theme="midnight-ink"><head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}">
<link rel="stylesheet" href="style-editorial.css">
<style>${taskCss}</style>
</head>
<body style="margin:0;padding:0;background:#0e0d0c">
<section class="poster xhs" style="position:relative">
  ${p.bg}
  ${p.html.replace(/^\s*<section class="poster xhs">/, "").replace(/<\/section>\s*$/, "")}
</section>
</body></html>`;
  fs.writeFileSync(file, page);
  targets.push({ file, out: path.join(OUT, `xhs-${p.id}.png`) });
}

for (const t of targets) {
  console.log("rendering", path.basename(t.out));
  execFileSync(
    CHROME,
    [
      "--headless=new",
      "--disable-gpu",
      "--hide-scrollbars",
      "--force-device-scale-factor=1",
      "--window-size=1080,1440",
      "--default-background-color=ff0e0d0c",
      "--virtual-time-budget=12000",
      `--screenshot=${t.out}`,
      `file://${t.file}`,
    ],
    { stdio: "inherit", timeout: 60000 }
  );
}
console.log("done");
