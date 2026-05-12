# neijing-notes 优化工作流（v2）

目标：减少返工、避免“标题重复/图片丢失/平台状态不一致”。

## 一条命令一件事

## 1) 预检（发任何平台前）
```bash
python3 scripts/neijing_workflow.py preflight --post-dir "08-冬三月闭藏"
```
检查：
- 必要文件是否齐全（article/publish/images）
- ghost.md 是否 frontmatter 正常
- ghost.md 是否出现正文 H1（会导致标题重复风险）
- ghost.md 引用图片是否真实存在

## 2) 生成小红书手机包
```bash
python3 scripts/neijing_workflow.py build-xhs-pack --post-dir "08-冬三月闭藏" --cards 8
```
输出：
- `xhs-publish-pack/images/cover.jpg + card-01..08.jpg`
- `xhs-body.txt`
- `README.txt`
- `publish-log.json`

## 3) 平台状态统一记账
```bash
python3 scripts/neijing_workflow.py update-log \
  --post-dir "08-冬三月闭藏" \
  --platform wechat \
  --status draft_created \
  --extra-json '{"draft_media_id":"xxx"}'
```
同理可记录 `ghost` / `x` / `xiaohongshu`。

---

## 推荐发布顺序（稳定版）
1. Ghost draft（先验证标题与图片）
2. WeChat draft（确认图片顺序一致）
3. X 线程
4. 小红书（自动草稿或手机包手发）

---

## 本仓库约定
- `article.md`：长文母稿（公众号/Ghost/X）
- `publish.md`：小红书文案与生图提示词
- `images/`：最终配图
- `xhs-publish-pack/`：手机手发包

---

## 提交建议
```bash
git add <post-dir>/images <post-dir>/xhs-publish-pack <post-dir>/publish-log.json scripts/neijing_workflow.py WORKFLOW.md
git commit -m "chore: optimize publishing workflow"
git push origin main
```
