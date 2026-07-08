#!/usr/bin/env node
/* 15-东风生于春 · 深色国风五色 · 具象图版 (仿14)
 * 9 图卡: 6 张 SVG 线描具象图 + 3 张排版卡.
 * 图: 天人方位轮 / 五行相生环 / 四季-五脏时间轴 / 人体俞位图 / 脾枢纽图.
 * 全 HTML+SVG 渲染, 文字 100% 精准. System Chrome headless, 1x 1080x1440.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const DIR = __dirname;
const OUT = path.join(DIR, "output-final");
fs.mkdirSync(OUT, { recursive: true });
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// 五色
const C = {
  qing: "#52b4a0",
  chi: "#e26a52",
  huang: "#e6b24e",
  bai: "#efe7d5",
  hei: "#cfc4ad",
};
const GLOW = {
  qing: "82,180,160",
  chi: "226,106,82",
  huang: "230,178,78",
  bai: "239,231,213",
  hei: "207,196,173",
};

// ---- 深色国风背景 ----------------------------------------------------------
function bg(seed, opt = {}) {
  const gx = opt.glowX ?? 30,
    gy = opt.glowY ?? 22,
    g = opt.glow ?? 0.5,
    mist = opt.mist ?? 0.15,
    moon = opt.moon
      ? `<circle cx="880" cy="250" r="92" fill="none" stroke="rgba(224,196,140,.32)" stroke-width="3"/><circle cx="905" cy="235" r="92" fill="#0e0d0c"/>`
      : "";
  return `<svg class="bg" width="1080" height="1440" viewBox="0 0 1080 1440" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="mist${seed}" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.006 0.011" numOctaves="4" seed="${seed}" stitchTiles="stitch"/><feColorMatrix type="matrix" values="0 0 0 0 0.80  0 0 0 0 0.70  0 0 0 0 0.52  0 0 0 0.85 0"/></filter>
    <radialGradient id="glow${seed}" cx="${gx}%" cy="${gy}%" r="62%"><stop offset="0%" stop-color="rgba(224,182,110,${g})"/><stop offset="45%" stop-color="rgba(150,110,60,${g * 0.28})"/><stop offset="100%" stop-color="rgba(14,13,12,0)"/></radialGradient>
    <linearGradient id="vig${seed}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="rgba(0,0,0,0)"/><stop offset="72%" stop-color="rgba(0,0,0,0)"/><stop offset="100%" stop-color="rgba(0,0,0,.5)"/></linearGradient>
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

// 五色 node disc (organ char inside ring)
function disc(cx, cy, k, organ, r = 70, fs = 60) {
  const col = C[k];
  const fill = k === "hei" ? "rgba(207,196,173,.06)" : `rgba(${GLOW[k]},.12)`;
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" stroke="${col}" stroke-width="3.5"/>
    <text x="${cx}" y="${cy + fs * 0.34}" text-anchor="middle" font-family="var(--serif-zh)" font-weight="700" font-size="${fs}" fill="${col}">${organ}</text>`;
}

// ---- 图1 · 天人方位轮 ------------------------------------------------------
function wheel() {
  return `<svg width="800" height="800" viewBox="0 0 820 820" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#d4a04a"><circle cx="410" cy="410" r="372" stroke-opacity=".18" stroke-width="1.5"/><circle cx="410" cy="410" r="352" stroke-opacity=".40" stroke-width="2"/></g>
    <g stroke="#d4a04a" stroke-opacity=".30" stroke-width="2"><line x1="410" y1="410" x2="410" y2="158"/><line x1="410" y1="410" x2="410" y2="662"/><line x1="410" y1="410" x2="158" y2="410"/><line x1="410" y1="410" x2="662" y2="410"/></g>
    <g font-family="var(--serif-zh)" fill="#ece2cf"><text x="410" y="66" text-anchor="middle" font-size="34">南</text><text x="410" y="98" text-anchor="middle" font-size="22" fill="#9a8c75">夏</text></g>
    ${disc(410, 150, "chi", "心")}
    <g font-family="var(--serif-zh)" fill="#ece2cf"><text x="410" y="784" text-anchor="middle" font-size="34">北</text><text x="410" y="752" text-anchor="middle" font-size="22" fill="#9a8c75">冬</text></g>
    ${disc(410, 670, "hei", "肾")}
    <g font-family="var(--serif-zh)" fill="#ece2cf"><text x="58" y="404" text-anchor="middle" font-size="34">东</text><text x="58" y="436" text-anchor="middle" font-size="22" fill="#9a8c75">春</text></g>
    ${disc(150, 410, "qing", "肝")}
    <g font-family="var(--serif-zh)" fill="#ece2cf"><text x="762" y="404" text-anchor="middle" font-size="34">西</text><text x="762" y="436" text-anchor="middle" font-size="22" fill="#9a8c75">秋</text></g>
    ${disc(670, 410, "bai", "肺")}
    ${disc(410, 410, "huang", "脾", 82, 68)}
    <text x="410" y="528" text-anchor="middle" font-family="var(--mono)" font-size="22" fill="#9a8c75" letter-spacing="2">中 · 长夏</text>
  </svg>`;
}

// ---- 图2 · 五行相生环 ------------------------------------------------------
function shengCycle() {
  const cx = 410,
    cy = 412,
    R = 268;
  // 相生顺序: 肝木→心火→脾土→肺金→肾水→(肝)
  const seq = [
    { k: "qing", o: "肝", s: "春·木" },
    { k: "chi", o: "心", s: "夏·火" },
    { k: "huang", o: "脾", s: "长夏·土" },
    { k: "bai", o: "肺", s: "秋·金" },
    { k: "hei", o: "肾", s: "冬·水" },
  ];
  const pts = seq.map((n, i) => {
    const a = (-90 + i * 72) * (Math.PI / 180);
    return { ...n, x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
  });
  const nr = 64;
  // arrows i->i+1 (clockwise, slightly outside the chord)
  let arrows = "";
  for (let i = 0; i < 5; i++) {
    const a = pts[i],
      b = pts[(i + 1) % 5];
    const dx = b.x - a.x,
      dy = b.y - a.y,
      len = Math.hypot(dx, dy);
    const ux = dx / len,
      uy = dy / len;
    const sx = a.x + ux * (nr + 10),
      sy = a.y + uy * (nr + 10);
    const ex = b.x - ux * (nr + 18),
      ey = b.y - uy * (nr + 18);
    // bow outward: control point pushed away from center
    const mx = (sx + ex) / 2,
      my = (sy + ey) / 2;
    const obx = mx - cx,
      oby = my - cy,
      ol = Math.hypot(obx, oby);
    const ctlx = mx + (obx / ol) * 46,
      ctly = my + (oby / ol) * 46;
    arrows += `<path d="M${sx.toFixed(1)},${sy.toFixed(1)} Q${ctlx.toFixed(1)},${ctly.toFixed(1)} ${ex.toFixed(1)},${ey.toFixed(1)}" fill="none" stroke="#d4a04a" stroke-opacity=".8" stroke-width="3" marker-end="url(#ah)"/>`;
  }
  const nodes = pts
    .map(
      (p) =>
        disc(p.x, p.y, p.k, p.o, nr, 54) +
        `<text x="${p.x}" y="${p.y + nr + 30}" text-anchor="middle" font-family="var(--mono)" font-size="20" fill="#9a8c75" letter-spacing="1">${p.s}</text>`
    )
    .join("");
  return `<svg width="800" height="800" viewBox="0 0 820 820" xmlns="http://www.w3.org/2000/svg">
    <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d4a04a"/></marker></defs>
    <circle cx="410" cy="412" r="330" fill="none" stroke="#d4a04a" stroke-opacity=".12" stroke-width="1.5"/>
    ${arrows}
    ${nodes}
    <text x="410" y="400" text-anchor="middle" font-family="var(--serif-zh)" font-weight="500" font-size="40" fill="#d4a04a">相生</text>
    <text x="410" y="446" text-anchor="middle" font-family="var(--mono)" font-size="20" fill="#9a8c75" letter-spacing="3">环环相养</text>
  </svg>`;
}

// ---- 图3 · 四季-五脏时间轴 -------------------------------------------------
function timeline() {
  const stops = [
    { k: "qing", se: "春", o: "肝", yu: "颈项" },
    { k: "chi", se: "夏", o: "心", yu: "胸胁" },
    { k: "huang", se: "长夏", o: "脾", yu: "脊" },
    { k: "bai", se: "秋", o: "肺", yu: "肩背" },
    { k: "hei", se: "冬", o: "肾", yu: "腰股" },
  ];
  const x = 150,
    y0 = 80,
    gap = 168;
  const line = `<line x1="${x}" y1="${y0}" x2="${x}" y2="${y0 + gap * 4}" stroke="#d4a04a" stroke-opacity=".5" stroke-width="2.5"/>`;
  const rows = stops
    .map((s, i) => {
      const y = y0 + gap * i;
      const dot =
        s.k === "hei"
          ? `<circle cx="${x}" cy="${y}" r="17" fill="#0e0d0c" stroke="${C.hei}" stroke-width="3.5"/>`
          : `<circle cx="${x}" cy="${y}" r="17" fill="${C[s.k]}" style="filter:drop-shadow(0 0 12px rgba(${GLOW[s.k]},.6))"/>`;
      return `${dot}
      <text x="${x + 56}" y="${y - 6}" font-family="var(--serif-zh)" font-weight="500" font-size="50" fill="#ece2cf">${s.se}</text>
      <text x="${x + 56}" y="${y + 44}" font-family="var(--mono)" font-size="22" fill="#9a8c75" letter-spacing="2">病在 ${s.yu}</text>
      <text x="${x + 360}" y="${y + 18}" font-family="var(--serif-zh)" font-weight="700" font-size="64" fill="${C[s.k]}">${s.o}</text>`;
    })
    .join("");
  return `<svg width="600" height="820" viewBox="0 0 600 820" xmlns="http://www.w3.org/2000/svg">${line}${rows}</svg>`;
}

// ---- 图4 · 人体俞位图 ------------------------------------------------------
function bodyYu() {
  return `<svg width="560" height="800" viewBox="0 0 620 880" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#bfb39a" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" opacity=".9">
      <circle cx="310" cy="92" r="56"/>
      <path d="M310,148 C270,150 250,168 246,205 L232,330 C228,372 236,470 252,520 L262,560 L358,560 L368,520 C384,470 392,372 388,330 L374,205 C370,168 350,150 310,148 Z"/>
      <path d="M252,212 C214,236 196,300 190,372"/>
      <path d="M368,212 C406,236 424,300 430,372"/>
      <path d="M278,560 L268,800"/><path d="M342,560 L352,800"/>
      <path d="M262,800 L300,800"/><path d="M320,800 L360,800"/>
    </g>
    <!-- 颈项·肝 -->
    <line x1="310" y1="156" x2="510" y2="120" stroke="${C.qing}" stroke-width="2" stroke-opacity=".7"/>
    <circle cx="310" cy="156" r="13" fill="${C.qing}"/>
    <text x="524" y="112" font-family="var(--serif-zh)" font-size="30" fill="#ece2cf">颈项</text>
    <text x="524" y="152" font-family="var(--serif-zh)" font-weight="700" font-size="42" fill="${C.qing}">肝</text>
    <!-- 胸胁·心 -->
    <line x1="356" y1="270" x2="512" y2="270" stroke="${C.chi}" stroke-width="2" stroke-opacity=".7"/>
    <circle cx="356" cy="270" r="13" fill="${C.chi}"/>
    <text x="526" y="262" font-family="var(--serif-zh)" font-size="30" fill="#ece2cf">胸胁</text>
    <text x="526" y="302" font-family="var(--serif-zh)" font-weight="700" font-size="42" fill="${C.chi}">心</text>
    <!-- 肩背·肺 -->
    <line x1="244" y1="250" x2="108" y2="250" stroke="${C.bai}" stroke-width="2" stroke-opacity=".7"/>
    <circle cx="244" cy="250" r="13" fill="${C.bai}"/>
    <text x="100" y="242" font-family="var(--serif-zh)" font-size="30" fill="#ece2cf" text-anchor="end">肩背</text>
    <text x="100" y="282" font-family="var(--serif-zh)" font-weight="700" font-size="42" fill="${C.bai}" text-anchor="end">肺</text>
    <!-- 脊·脾 -->
    <line x1="310" y1="380" x2="108" y2="430" stroke="${C.huang}" stroke-width="2" stroke-opacity=".7"/>
    <circle cx="310" cy="380" r="13" fill="${C.huang}"/>
    <text x="100" y="422" font-family="var(--serif-zh)" font-size="30" fill="#ece2cf" text-anchor="end">脊</text>
    <text x="100" y="462" font-family="var(--serif-zh)" font-weight="700" font-size="42" fill="${C.huang}" text-anchor="end">脾</text>
    <!-- 腰股·肾 -->
    <line x1="310" y1="500" x2="512" y2="540" stroke="${C.hei}" stroke-width="2" stroke-opacity=".7"/>
    <circle cx="310" cy="500" r="13" fill="none" stroke="${C.hei}" stroke-width="3"/>
    <text x="526" y="532" font-family="var(--serif-zh)" font-size="30" fill="#ece2cf">腰股</text>
    <text x="526" y="572" font-family="var(--serif-zh)" font-weight="700" font-size="42" fill="${C.hei}">肾</text>
  </svg>`;
}

// ---- 图5 · 脾枢纽图 --------------------------------------------------------
function hub() {
  const cx = 380,
    cy = 320;
  const corners = [
    { k: "qing", o: "肝", x: 130, y: 120 },
    { k: "chi", o: "心", x: 630, y: 120 },
    { k: "bai", o: "肺", x: 130, y: 520 },
    { k: "hei", o: "肾", x: 630, y: 520 },
  ];
  let arr = "";
  corners.forEach((c) => {
    const dx = c.x - cx,
      dy = c.y - cy,
      l = Math.hypot(dx, dy),
      ux = dx / l,
      uy = dy / l;
    const sx = cx + ux * 92,
      sy = cy + uy * 92,
      ex = c.x - ux * 64,
      ey = c.y - uy * 64;
    arr += `<line x1="${sx.toFixed(1)}" y1="${sy.toFixed(1)}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="#d4a04a" stroke-opacity=".7" stroke-width="3" marker-end="url(#ah2)"/>`;
  });
  const cn = corners.map((c) => disc(c.x, c.y, c.k, c.o, 58, 50)).join("");
  return `<svg width="720" height="640" viewBox="0 0 760 640" xmlns="http://www.w3.org/2000/svg">
    <defs><marker id="ah2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d4a04a"/></marker></defs>
    ${arr}
    ${cn}
    ${disc(cx, cy, "huang", "脾", 84, 70)}
  </svg>`;
}

// ---- diagram card builder --------------------------------------------------
function diagCard(id, seed, opt, kicker, title, svg, lead) {
  return {
    id,
    bg: bg(seed, opt),
    content: `<div class="content">
    <p class="kicker">${kicker}</p>
    <h2 class="h-xl diag-title">${title}</h2>
    <div class="diagram-wrap">${svg}</div>
    <p class="lead">${lead}</p>
  </div>`,
  };
}

const posters = [];

// 01 · 封面
posters.push({
  id: "01-cover",
  bg: bg(7, { glowX: 28, glowY: 20, glow: 0.6, mist: 0.2, moon: true }),
  content: `<div class="content stack gap-3">
    <div class="issue-row"><span>金匮真言论</span><span class="dot"></span><span>No.15</span><span class="dot"></span><span>学渣读经</span></div>
    <div class="stack gap-2"><p class="kicker">封面 · 第十五篇</p><h1 class="h-display cover-title">古人给五脏<br>做了一套<br>GPS 坐标</h1></div>
    <span class="seal">內<br>經</span>
    <div class="grow"></div>
    <div class="wuxing-strip">${["肝", "心", "脾", "肺", "肾"]
      .map(
        (k0) => {
          const m = { 肝: ["东", "qing"], 心: ["南", "chi"], 脾: ["中", "huang"], 肺: ["西", "bai"], 肾: ["北", "hei"] }[k0];
          return `<div class="wx-col"><span class="wu-dot wu-${m[1]}"></span><span class="wx-el">${m[0]}</span><span class="wx-organ glow-${m[1]}" style="color:${C[m[1]]}">${k0}</span></div>`;
        }
      )
      .join("")}</div>
    <p class="lead">方位、季节、脏腑、身体部位——<br>古人把它们对应成一张多维地图。</p>
  </div>
  <div class="issue-strip"><span>五脏坐标</span><span>—</span><span>素问 · 金匮真言论</span></div>`,
});

// 02 · 天人方位轮
posters.push(
  diagCard("02-wheel", 13, { glowX: 50, glowY: 40, glow: 0.5, mist: 0.15 }, "天人相应 · 五方五行", "五脏的<br>方位坐标", wheel(),
    `肝在"东方"——不是肝在身体东边,<br>是肝像东方、像春天,都主生发。`)
);

// 03 · 五行相生环
posters.push(
  diagCard("03-sheng", 21, { glowX: 50, glowY: 42, glow: 0.5, mist: 0.16 }, "同类归组 · 五行相生", "性质相似<br>环环相生", shengCycle(),
    `把性质相似的东西归到一组——<br>春生夏长、相邻相养,连成一个循环。`)
);

// 04 · 四季-五脏时间轴
posters.push(
  diagCard("04-timeline", 28, { glowX: 24, glowY: 24, glow: 0.4, mist: 0.13 }, "时间轴 · 应时而病", "哪个季节<br>哪个脏当令", timeline(),
    `一年走过五季,五脏轮流"值班"——<br>知道当令的脏,就知道该护哪里。`)
);

// 05 · 人体俞位图
posters.push(
  diagCard("05-body", 34, { glowX: 50, glowY: 30, glow: 0.46, mist: 0.14 }, "俞 · 疼痛定位", "哪里不舒服<br>提示哪个脏", bodyYu(),
    `哪里不舒服,可能提示哪个脏有状况——<br>一套"症状→脏腑"的定位指南。`)
);

// 06 · 脾枢纽图
posters.push(
  diagCard("06-hub", 45, { glowX: 50, glowY: 36, glow: 0.55, mist: 0.16 }, "中央为土 · 枢纽", "脾在中央<br>服务四方", hub(),
    `其他四脏各有方位,脾居正中——<br>像交通枢纽,把水谷运往四方。`)
);

// 07 · 暂时的理解 (ledger)
const recap = [
  ["功能分组", "按性质相似归类,不按解剖位置"],
  ["多维对应", "每脏配方位 · 季节 · 风 · 部位"],
  ["应时而病", "哪季哪脏当令,症状帮你定位"],
  ["脾为枢纽", "居中调度,服务四方"],
];
posters.push({
  id: "07-recap",
  bg: bg(56, { glowX: 26, glowY: 22, glow: 0.36, mist: 0.13 }),
  content: `<div class="content stack gap-2">
    <p class="kicker">暂时的理解 · 复盘</p>
    <h2 class="h-xl">这一段<br>我读到了什么</h2>
    <div class="ledger spread">${recap
      .map(
        ([t, n], i) =>
          `<div class="ledger-row"><span class="ledger-nb">0${i + 1}</span><div><div class="ledger-title">${t}</div><div class="ledger-note">${n}</div></div></div>`
      )
      .join("")}</div>
  </div>`,
});

// 08 · 留的坑 (ledger)
const pits = [
  '"俞"是穴位,还是泛指区域?',
  "这套方位,在南半球还适用吗?",
  '脾对应"长夏",还是"四季末各十八天"?',
  "这张表和四季养生是什么关系?",
];
posters.push({
  id: "08-pits",
  bg: bg(67, { glowX: 76, glowY: 24, glow: 0.34, mist: 0.12 }),
  content: `<div class="content stack gap-2">
    <p class="kicker">留的坑 · 待解</p>
    <h2 class="h-xl">还没想明白<br>的几件事</h2>
    <div class="ledger spread">${pits
      .map((q, i) => `<div class="ledger-row"><span class="ledger-nb">0${i + 1}</span><div class="ledger-title pit-q">${q}</div></div>`)
      .join("")}</div>
  </div>`,
});

// 09 · 下期预告
posters.push({
  id: "09-next",
  bg: bg(78, { glowX: 50, glowY: 30, glow: 0.55, mist: 0.18 }),
  content: `<div class="content stack gap-2">
    <p class="kicker">下期预告 · 下篇见</p>
    <h2 class="h-display" style="font-size:96px">每个脏<br>都有一张<br>身份证</h2>
    <div class="grow"></div>
    <div class="next-attrs">${["颜色", "味道", "声音", "数字", "开窍"].map((a) => `<span class="attr-chip">${a}</span>`).join("")}</div>
    <hr class="rule">
    <p class="lead">信息量最大的一段,像在读数据库。</p>
    <p class="meta glow-qing" style="color:${C.qing}">东方青色,入通于肝 ——</p>
  </div>`,
});

// ---- task CSS --------------------------------------------------------------
const taskCss = `
  :root, [data-theme="midnight-ink"] { --accent:#d4a04a; --accent-rgb:212,160,74; }
  :root { --c-qing:#52b4a0; --c-chi:#e26a52; --c-huang:#e6b24e; --c-bai:#efe7d5; --c-hei:#cfc4ad; }
  .bg { position:absolute; inset:0; z-index:0; width:100%; height:100%; pointer-events:none; }
  .content { position:relative; z-index:2; width:100%; height:100%; padding:96px 88px; display:flex; flex-direction:column; }
  .grow { flex:1; }
  .spread { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
  .cover-title { font-size:104px; line-height:1.08; }
  .diag-title { font-size:62px !important; line-height:1.12; margin:0 0 8px !important; }
  .diagram-wrap { flex:1; display:flex; align-items:center; justify-content:center; min-height:0; }
  .diagram-wrap svg { max-width:100%; max-height:100%; }

  .seal { position:absolute; right:88px; top:300px; z-index:3; width:98px; height:98px; display:flex; align-items:center; justify-content:center; font-family:var(--serif-zh); font-weight:700; font-size:34px; line-height:1.02; color:#f4ece0; background:#a8392c; letter-spacing:.04em; text-align:center; box-shadow:0 0 0 1px rgba(244,236,224,.18), 0 6px 18px rgba(0,0,0,.5); }

  .wu-dot { display:inline-block; width:30px; height:30px; border-radius:50%; flex:0 0 auto; }
  .wu-qing { background:var(--c-qing); box-shadow:0 0 18px rgba(82,180,160,.55); }
  .wu-chi  { background:var(--c-chi);  box-shadow:0 0 18px rgba(226,106,82,.55); }
  .wu-huang{ background:var(--c-huang);box-shadow:0 0 20px rgba(230,178,78,.6); }
  .wu-bai  { background:var(--c-bai);  box-shadow:0 0 18px rgba(239,231,213,.5); }
  .wu-hei  { background:transparent;   box-shadow:0 0 0 2px var(--c-hei) inset; }
  .glow-qing{text-shadow:0 0 22px rgba(82,180,160,.45);} .glow-chi{text-shadow:0 0 22px rgba(226,106,82,.45);}
  .glow-huang{text-shadow:0 0 24px rgba(230,178,78,.5);} .glow-bai{text-shadow:0 0 20px rgba(239,231,213,.4);}

  .wuxing-strip { display:grid; grid-template-columns:repeat(5,1fr); margin:8px 0; border-top:1px solid rgba(236,226,207,.18); border-bottom:1px solid rgba(236,226,207,.18); padding:30px 0; }
  .wx-col { display:flex; flex-direction:column; align-items:center; gap:14px; }
  .wx-el { font-family:var(--serif-zh); font-size:30px; color:var(--muted); }
  .wx-organ { font-family:var(--serif-zh); font-weight:700; font-size:52px; }

  .ledger-row { border-bottom:1px solid rgba(236,226,207,.14) !important; }
  .ledger-note { color:rgba(236,226,207,.72) !important; }
  .pit-q { font-size:34px !important; line-height:1.4; font-weight:500; }
  .next-attrs { display:flex; flex-wrap:wrap; gap:18px; margin:6px 0 4px; }
  .attr-chip { font-family:var(--serif-zh); font-weight:500; font-size:34px; color:var(--ink); padding:12px 28px; border:1px solid rgba(236,226,207,.28); background:rgba(236,226,207,.05); }
  .issue-strip { border-top-color:rgba(236,226,207,.2) !important; }
  .kicker { font-family:var(--mono); font-size:21px; letter-spacing:.22em; text-transform:uppercase; color:rgba(236,226,207,.55); margin:0 0 16px; }
`;

// ---- render ----------------------------------------------------------------
const FONTS = `https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700;900&family=Noto+Sans+SC:wght@300;400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap`;
const targets = [];
for (const p of posters) {
  const file = path.join(DIR, `_fn-${p.id}.html`);
  const page = `<!doctype html><html lang="zh-CN" data-theme="midnight-ink"><head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}"><link rel="stylesheet" href="style-editorial.css">
<style>${taskCss}</style></head>
<body style="margin:0;padding:0;background:#0e0d0c">
<section class="poster xhs" style="position:relative">${p.bg}${p.content}</section>
</body></html>`;
  fs.writeFileSync(file, page);
  targets.push({ file, out: path.join(OUT, `xhs-${p.id}.png`) });
}
for (const t of targets) {
  console.log("rendering", path.basename(t.out));
  execFileSync(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1080,1440", "--default-background-color=ff0e0d0c", "--virtual-time-budget=12000", `--screenshot=${t.out}`, `file://${t.file}`], { stdio: "inherit", timeout: 60000 });
}
console.log("done");
