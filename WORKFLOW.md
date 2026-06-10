# neijing-notes 内容发布工作流（v3）

> 完整发布流程：生图 → 叠字 → 审核 → Ghost draft

---

## 完整执行顺序

### 0) 生成平台 markdown 稿（wechat.md / ghost.md）
在生图/发布之前，`wechat.md`（公众号）和 `ghost.md`（Ghost）的 markdown 正文由 `article.md` 自动派生：
```bash
python3 .gen-platform.py "<post-dir>"        # 省略参数则全量重生成
```
- ghost.md 正文与 wechat.md 一致（"Ghost 跟随公众号"），仅多 frontmatter（title/slug/tags/excerpt/feature_image）。
- 文末统一附 **AI 标识 + 健康免责 footer**（合规，规避"低创作度"判定）。
- 新增篇目须先在 `.gen-platform.py` 的 `DATA` 字典登记 slug/tags/excerpt；改了 `article.md` 后重跑此脚本同步。
- 本步只产出 markdown 稿件；下面的步骤 5/6 才是把它们 + 叠字图上传成 Ghost/微信草稿。

### 1) Pull 文章目录
```bash
# 根据用户提示定位到目标文章目录
cd /Users/tranmoo/neijing-notes
git pull origin main
# 确认目标目录存在（如 "生气通天论-小结"）
```

### 2) 生成空白背景图 → images/
- 读取 `publish.md` 中的生图提示词（Part 1 封面 + Part 2 各卡片）
- 使用 `image_generate` 工具（gpt-image-2）生成无字图片
- 风格要求：**明亮暖棕调，不要暗调**，上方留出负空间用于叠字
- 保存到 `<post-dir>/images/` (cover.jpg + card-01~08.jpg)

### 3) Social-card 叠字 → img-temp/
- 根据每张图片的实际构图，在空白处贴文字
- 调整布局：左上/居中/中段/偏移，不要统一排版
- 调整文字颜色（鎏金 `#d4a04a` / 米白 `#f0e8d8`）
- 标题 58-72px，正文 30-34px
- 不要文字底框，仅用 text-shadow 保证可读
- 输出到 `<post-dir>/img-temp/`

### 4) 审核流程
- 按顺序发送 9 张叠字图给用户审核
- 审核通过 → 复制到对应的小红书发布图片文件夹
- 审核不通过 → 删除 `img-temp/` → 调整布局/颜色/字号 → 重新叠字 → 再次发送审核

### 5) 生成 Ghost Draft
- 读取 `article.md` 正文
- 读取小红书发布图片（审核通过的图）
- 生成 Ghost draft（含 frontmatter + 图片引用）

### 6) 生成公众号草稿（图文混排版）
- 读取 `wechat.md` 中的文章正文（纯文字，无 HTML）
- 读取 `xhs-publish-pack/images/` 中的叠字图（审核通过的图）
- 上传叠字图到微信素材库（封面用永久素材，内容图用临时 CDN）
- 正文 = 文章文字段落 + 干净 `<img>` 配图穿插
- 排版特点：
  - **文字是可编辑的真实正文**（叠在图上）
  - **配图是有字的叠图版**（social-card 生成的）
  - 无复杂自定义样式，保持微信原生排版感

```bash
python3 <post-dir>/wechat_draft_clean.py
```

---

## 目录约定

```
<post-dir>/
├── images/              ← 无字原图（image-2 生成）
├── img-temp/            ← 叠字后待审核图片（social-card 渲染）
├── xhs-publish-pack/    ← 审核通过后的小红书发布图片
│   └── images/
├── article.md           ← 博客正文母稿
├── publish.md            ← 小红书文案 + 生图提示词
├── ghost.md              ← Ghost 博客发布稿
├── wechat.md             ← 公众号发布稿
├── wechat_draft_clean.py ← 公众号草稿发布脚本（图文混排版）
├── x.md                  ← X/Twitter 线程稿
└── publish-log.json     ← 各平台发布状态
```

## 一条命令一件事

### 预检
```bash
python3 scripts/neijing_workflow.py preflight --post-dir "<post-dir>"
```

### 生成小红书手机包
```bash
python3 scripts/neijing_workflow.py build-xhs-pack --post-dir "<post-dir>"
```

### 平台状态记账
```bash
python3 scripts/neijing_workflow.py update-log \
  --post-dir "<post-dir>" \
  --platform ghost --status draft_created \
  --extra-json '{"editor_url":"..."}'
```

## 推荐发布顺序
1. Ghost draft（先验证标题与图片）
2. 公众号草稿（先发，和 Ghost 互相校对）
3. X 线程
4. 小红书（手机包手发）

## Git 提交规范
```bash
git add <post-dir>/images <post-dir>/img-temp <post-dir>/xhs-publish-pack <post-dir>/ghost.md <post-dir>/wechat_draft_clean.py publish-log.json
git commit -m "<post-dir>: 生图+叠字+ghost draft+公众号草稿"
git push origin main
```
