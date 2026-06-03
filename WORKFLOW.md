# neijing-notes 内容发布工作流（v3）

> 完整发布流程：生图 → 叠字 → 审核 → Ghost draft

---

## 完整执行顺序

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

---

## 目录约定

```
<post-dir>/
├── images/              ← 无字原图（image-2 生成）
├── img-temp/            ← 叠字后待审核图片（social-card 渲染）
├── xhs-publish-pack/    ← 审核通过后的小红书发布图片
│   └── images/
├── article.md           ← 博客正文母稿
├── publish.md           ← 小红书文案 + 生图提示词
├── ghost.md             ← Ghost 博客发布稿
├── wechat.md            ← 公众号发布稿
├── x.md                 ← X/Twitter 线程稿
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
2. WeChat draft（确认图片顺序一致）
3. X 线程
4. 小红书（手机包手发）

## Git 提交规范
```bash
git add <post-dir>/images <post-dir>/img-temp <post-dir>/xhs-publish-pack <post-dir>/ghost.md publish-log.json
git commit -m "<post-dir>: 生图+叠字+ghost draft"
git push origin main
```
