# CLAUDE.md — Agent 操作规范

这是《学渣读内经》内容项目。

**第一步必读**：读 `SCHEMA.md` 了解完整文件结构规范，再开始任何操作。

## 项目简介

博客系列《学渣读内经》的内容仓库。每篇对应一个独立文件夹，包含博客正文、小红书发布素材和配图。

- GitHub：https://github.com/tranmoolee/neijing-notes（tranmoolee 账户，main 分支）
- 博客主站：https://www.ileemoo.com

## 每篇文件夹结构

```
NN-主题/
├── article.md   ← 博客正文
├── publish.md   ← 小红书图文 + 配图 Prompt + 标签
└── images/      ← 配图存放位置
```

## 新增一篇的标准流程

按 `SCHEMA.md` 第六节执行：

1. 新建 `NN-主题/` 文件夹（NN 为两位数编号）
2. 创建 `article.md` `publish.md` `images/` `audio/` `video/`
3. 在 `README.md` 系列目录新增一行，状态 `🔲 待写`
4. 写完后状态改为 `✅ 已完成`
5. git commit + push

**提交格式**：`feat: NN-主题 article + publish`

## 红线

- `article.md` 中 `## 今天这段` 下的原文引用块（`> `）不可修改
- 不要改动已完成篇目的正文内容，除非用户明确要求
- push 前确认 README.md 系列目录状态已更新
