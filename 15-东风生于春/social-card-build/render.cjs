#!/usr/bin/env node
/* Swiss social-card renderer for 15-东风生于春 (IKB accent).
 * Uses system Chrome headless --screenshot (no Playwright dependency).
 * Each poster is written as a standalone 1080x1440 page linking style.css,
 * then captured at 1x (native Rednote resolution).
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const DIR = __dirname;
const OUT = path.join(DIR, "output");
fs.mkdirSync(OUT, { recursive: true });

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// ---- shared bits ----------------------------------------------------------
const ARROW = `<i data-lucide="arrow-right" width="44" height="44"></i>`;

function chainRow(items) {
  // items: [..., organ]  — organ is the accent endpoint
  const last = items.length - 1;
  const parts = items
    .map((t, i) => {
      const cls = i === last ? "chain-organ" : "chain-node";
      return `<span class="${cls}">${t}</span>`;
    })
    .join(`<span class="chain-eq">=</span>`);
  return `<div class="chain-row">${parts}</div>`;
}

// ---- posters ---------------------------------------------------------------
const posters = [];

// 01 · Cover — S01 Accent Cover
posters.push({
  id: "xhs-01-cover",
  html: `
<section class="poster xhs">
  <div class="content stack gap-9">
    <div class="chrome-min">
      <span>金匮真言论 · No.15</span>
      <span>学渣读内经</span>
    </div>
    <div class="stack gap-7">
      <p class="t-cat">封面 · 金匮真言论</p>
      <h1 class="h-statement">古人给五脏<br>做了一套<br>GPS 坐标</h1>
    </div>
    <div class="grow"></div>
    <hr class="hr-accent">
    <p class="lead">方位、季节、脏腑、身体部位——<br>古人把它们对应成一张多维地图。</p>
    <div class="row gap-6">
      <p class="t-meta">第十五篇</p>
      <p class="t-meta">/ 学渣读经</p>
    </div>
  </div>
</section>`,
});

// 02 · 五脏坐标表 — custom Swiss data table
const tableRows = [
  ["东", "春", "肝", "颈项"],
  ["南", "夏", "心", "胸胁"],
  ["西", "秋", "肺", "肩背"],
  ["北", "冬", "肾", "腰股"],
  ["中", "长夏", "脾", "脊"],
];
posters.push({
  id: "xhs-02-table",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">坐标表 · The Map</p>
    <h2 class="h-xl">一张五脏<br>坐标表</h2>
    <div class="ntable">
      <div class="ntable-head">
        <span>方位</span><span>季节</span><span>脏</span><span>俞 · 易病处</span>
      </div>
      <div class="ntable-rows">
      ${tableRows
        .map(
          (r) => `<div class="ntable-row">
        <span class="td-dir">${r[0]}</span>
        <span class="td-season">${r[1]}</span>
        <span class="td-organ">${r[2]}</span>
        <span class="td-yu">${r[3]}</span>
      </div>`
        )
        .join("\n")}
      </div>
    </div>
    <p class="body" style="color:var(--grey-3)">不是器官列表,是一张多维地图。</p>
  </div>
</section>`,
});

// 03 · 同类归组 — equivalence chains
posters.push({
  id: "xhs-03-group",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">归组 · 同类相聚</p>
    <h2 class="h-xl">不是解剖学<br>是同类归组</h2>
    <div class="spread chains" style="margin-top:8px">
      ${chainRow(["东", "升起", "春", "生发", "肝"])}
      ${chainRow(["南", "最热", "夏", "旺盛", "心"])}
      ${chainRow(["西", "落下", "秋", "收敛", "肺"])}
      ${chainRow(["北", "最冷", "冬", "收藏", "肾"])}
    </div>
    <p class="body" style="color:var(--grey-3)">性质相似的东西归到同一组——<br>不是位置关系,是功能特征的分类。</p>
  </div>
</section>`,
});

// 04 · 俞 · 疼痛定位 — S05 Trap rows
const yuRows = [
  ["脖子僵", "肝"],
  ["胸闷", "心"],
  ["肩背痛", "肺"],
  ["腰酸", "肾"],
];
posters.push({
  id: "xhs-04-locate",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">俞 · 疼痛定位</p>
    <h2 class="h-xl">哪里不舒服<br>提示哪个脏</h2>
    <div class="locate spread">
      ${yuRows
        .map(
          (r) => `<div class="locate-row">
        <span class="lc-sym">${r[0]}</span>
        ${ARROW}
        <span class="lc-organ">${r[1]}</span>
      </div>`
        )
        .join("\n")}
    </div>
    <p class="body" style="color:var(--grey-3)">每个脏有一个容易出问题的反应区域。</p>
  </div>
</section>`,
});

// 05 · 脾在中央 — card-ink statement
posters.push({
  id: "xhs-05-spleen",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">中央为土 · 枢纽</p>
    <div class="card-ink stack gap-6 grow" style="justify-content:center">
      <p class="t-meta">其他四脏都有方位</p>
      <h2 class="h-xl" style="color:var(--paper)">脾在中央</h2>
      <p class="lead">像东南西北四城之间的交通枢纽,<br>所有物资都经过它转运。</p>
      <p class="lead">不偏不倚,却最不可或缺——<br>这就是"脾为后天之本"。</p>
    </div>
  </div>
</section>`,
});

// 06 · 暂时的理解 — S11 stacked ledger (4 rows)
const recap = [
  ["01", "功能分组", "按性质相似归类,不按解剖位置"],
  ["02", "多维对应", "每脏配方位 · 季节 · 风 · 部位"],
  ["03", "实用价值", "哪季哪脏易病,症状帮你定位"],
  ["04", "脾为枢纽", "居中调度,服务四方"],
];
posters.push({
  id: "xhs-06-recap",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">暂时的理解 · Recap</p>
    <h2 class="h-xl">这一段<br>我读到了什么</h2>
    <div class="stacked-ledger">
      ${recap
        .map(
          (r) => `<div class="ledger-row">
        <p class="ledger-num">${r[0]}</p>
        <div class="ledger-lbl">${r[1]}<span class="sub">${r[2]}</span></div>
      </div>`
        )
        .join("\n")}
    </div>
  </div>
</section>`,
});

// 07 · 留的坑 — numbered open questions (4 rows)
const pits = [
  ["01", '"俞"是穴位,还是泛指区域?'],
  ["02", "这套方位,在南半球还适用吗?"],
  ["03", '脾对应"长夏",还是"四季末各十八天"?'],
  ["04", "这张表和四季养生是什么关系?"],
];
posters.push({
  id: "xhs-07-pits",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">留的坑 · Open Questions</p>
    <h2 class="h-xl">还没想明白<br>的几件事</h2>
    <div class="pits spread">
      ${pits
        .map(
          (r) => `<div class="pit-row">
        <span class="pit-nb">${r[0]}</span>
        <span class="pit-q">${r[1]}</span>
      </div>`
        )
        .join("\n")}
    </div>
  </div>
</section>`,
});

// 08 · 下期预告 — matrix of attributes + closing
const attrs = [
  ["颜色", true],
  ["味道", false],
  ["声音", false],
  ["数字", false],
  ["开窍", false],
  ["情绪", false],
];
posters.push({
  id: "xhs-08-next",
  html: `
<section class="poster xhs">
  <div class="content stack gap-7">
    <p class="t-cat">下期预告 · Next</p>
    <h2 class="h-xl">每个脏<br>都有一张身份证</h2>
    <div class="matrix-fill">
      ${attrs
        .map(
          (a, i) =>
            `<div class="matrix-cell${a[1] ? " is-accent" : ""}"><p class="cell-nb">0${
              i + 1
            }</p><p class="cell-title">${a[0]}</p></div>`
        )
        .join("\n")}
    </div>
    <hr class="hr-hairline">
    <p class="lead">信息量最大的一段,像在读数据库。</p>
    <div class="row gap-6"><p class="t-meta">下篇见</p><p class="t-meta">/ 东方青色,入通于肝</p></div>
  </div>
</section>`,
});

// ---- task-scoped CSS (one named block, semantic resets only) ---------------
const taskCss = `
  /* ---- 15-东风 task-scoped Swiss helpers ---- */
  /* fill the vertical canvas: row groups grow + space out evenly */
  .spread { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
  .ntable { display:flex; flex-direction:column; flex:1; margin-top:8px; }
  .ntable-rows { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
  .ntable-head, .ntable-row {
    display:grid; grid-template-columns: 1.1fr 1.3fr 1fr 2.2fr;
    align-items:center; gap:var(--sp-6);
  }
  .ntable-head {
    padding-bottom:16px; border-bottom:2px solid var(--ink);
  }
  .ntable-head span {
    font-family:var(--mono); font-size:22px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--grey-3);
  }
  .ntable-row { padding:22px 0; border-bottom:1px solid var(--grey-2); }
  .ntable-row .td-dir   { font-family:var(--sans-zh); font-weight:500; font-size:48px; color:var(--ink); }
  .ntable-row .td-season{ font-family:var(--sans-zh); font-weight:400; font-size:38px; color:var(--ink); }
  .ntable-row .td-organ { font-family:var(--sans-zh); font-weight:600; font-size:48px; color:var(--accent); }
  .ntable-row .td-yu    { font-family:var(--sans-zh); font-weight:400; font-size:38px; color:var(--grey-3); }

  .chains .chain-row { padding:26px 0; border-bottom:1px solid var(--grey-2); }
  .chains .chain-row:last-child { border-bottom:0; }
  .chain-row { display:flex; align-items:center; flex-wrap:wrap; gap:18px; }
  .chain-node  { font-family:var(--sans-zh); font-weight:500; font-size:40px; color:var(--ink); }
  .chain-eq    { font-family:var(--mono); font-weight:400; font-size:34px; color:var(--grey-3); }
  .chain-organ { font-family:var(--sans-zh); font-weight:600; font-size:48px; color:var(--accent); }

  .locate { display:flex; flex-direction:column; }
  .locate-row {
    display:grid; grid-template-columns: 1fr 60px 1fr; align-items:center; gap:var(--sp-7);
    padding:34px 0; border-bottom:1px solid var(--grey-2);
  }
  .locate-row:last-child { border-bottom:0; }
  .locate-row .lc-sym   { font-family:var(--sans-zh); font-weight:500; font-size:54px; color:var(--ink); }
  .locate-row .lc-organ { font-family:var(--sans-zh); font-weight:600; font-size:60px; color:var(--accent); text-align:right; }
  .locate-row i { color:var(--grey-3); }

  .pits { display:flex; flex-direction:column; }
  .pit-row {
    display:grid; grid-template-columns: 96px 1fr; align-items:baseline; gap:var(--sp-7);
    padding:30px 0; border-bottom:1px solid var(--grey-2);
  }
  .pit-row:last-child { border-bottom:0; }
  .pit-row .pit-nb { font-family:var(--sans); font-weight:200; font-size:64px; line-height:1; color:var(--accent); }
  .pit-row .pit-q  { font-family:var(--sans-zh); font-weight:500; font-size:36px; line-height:1.35; color:var(--ink); }
`;

// ---- render loop -----------------------------------------------------------
const targets = [];
for (const p of posters) {
  const file = path.join(DIR, `_page-${p.id}.html`);
  const page = `<!doctype html><html lang="zh-CN" data-accent="ikb"><head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&family=Noto+Sans+SC:wght@200;300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<link rel="stylesheet" href="style.css">
<style>${taskCss}</style>
</head>
<body style="margin:0;padding:0;background:#fff">
${p.html}
<script>if(window.lucide&&lucide.createIcons)lucide.createIcons();</script>
</body></html>`;
  fs.writeFileSync(file, page);
  targets.push({ file, out: path.join(OUT, `${p.id}.png`) });
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
      "--default-background-color=ffffffff",
      "--virtual-time-budget=12000",
      `--screenshot=${t.out}`,
      `file://${t.file}`,
    ],
    { stdio: "inherit", timeout: 60000 }
  );
}

console.log("done");
