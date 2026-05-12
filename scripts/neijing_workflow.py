#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil
from pathlib import Path
from datetime import datetime, UTC


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def extract_codeblock(md: str, heading: str) -> str:
    m = re.search(rf"{re.escape(heading)}\n\n```\n(.*?)\n```", md, re.S)
    return m.group(1).strip() if m else ""


def preflight(post_dir: Path) -> dict:
    required = ["article.md", "publish.md", "images"]
    missing = [x for x in required if not (post_dir / x).exists()]

    ghost = post_dir / "ghost.md"
    ghost_issues = []
    if ghost.exists():
        text = read(ghost)
        fm = text.startswith("---")
        if not fm:
            ghost_issues.append("ghost.md 缺少 frontmatter")
        # duplicate top-level title check
        if re.search(r"^#\s+", text, re.M):
            ghost_issues.append("ghost.md 含正文 H1，可能与 frontmatter title 重复")
        # local image refs check
        refs = re.findall(r"\]\((images/[^)]+)\)", text)
        for r in refs:
            if not (post_dir / r).exists():
                ghost_issues.append(f"图片缺失: {r}")
    else:
        ghost_issues.append("ghost.md 不存在")

    return {
        "ok": not missing and not ghost_issues,
        "missing": missing,
        "ghost_issues": ghost_issues,
    }


def build_xhs_pack(post_dir: Path, cards: int = 8) -> dict:
    pub = read(post_dir / "publish.md")
    body = extract_codeblock(pub, "### 📝 小红书发布正文")
    tags = extract_codeblock(pub, "### 🏷️ 推荐标签（8 个）") or extract_codeblock(pub, "### 🏷️ 推荐标签")

    pack = post_dir / "xhs-publish-pack"
    pack_img = pack / "images"
    pack_img.mkdir(parents=True, exist_ok=True)

    (pack / "xhs-body.txt").write_text((body + "\n\n" + tags).strip() + "\n", encoding="utf-8")

    lines = [
        "上传时图片顺序（按文件名排列）：",
        "1. cover.jpg - 封面",
    ]
    for i in range(1, cards + 1):
        lines.append(f"{i+1}. card-{i:02d}.jpg")
    lines += [
        "",
        "操作步骤：",
        "1. 打开小红书 App → +",
        "2. 选「上传图文」",
        "3. 按以上顺序选图（全选后系统按文件名排序）",
        "4. 贴入 xhs-body.txt 的正文",
        "5. 发布",
    ]
    (pack / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    copied = []
    for name in ["cover.jpg", *[f"card-{i:02d}.jpg" for i in range(1, cards + 1)]]:
        src = post_dir / "images" / name
        if src.exists():
            shutil.copy2(src, pack_img / name)
            copied.append(name)

    log = {
        "post": post_dir.name,
        "xhs_publish_pack": {
            "images": len(copied),
            "body_file": "xhs-body.txt",
            "instructions": "README.txt",
            "created_at": datetime.now(UTC).isoformat(),
        },
    }
    (pack / "publish-log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"pack": str(pack), "copied": copied}


def update_publish_log(post_dir: Path, platform: str, status: str, extra: dict) -> Path:
    p = post_dir / "publish-log.json"
    data = {}
    if p.exists():
        try:
            data = json.loads(read(p))
        except Exception:
            data = {}
    rec = {"status": status, "updated_at": datetime.now(UTC).isoformat()}
    rec.update(extra)
    data[platform] = rec
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def main():
    ap = argparse.ArgumentParser(description="neijing-notes 发布流程工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("preflight")
    p1.add_argument("--post-dir", required=True)

    p2 = sub.add_parser("build-xhs-pack")
    p2.add_argument("--post-dir", required=True)
    p2.add_argument("--cards", type=int, default=8)

    p3 = sub.add_parser("update-log")
    p3.add_argument("--post-dir", required=True)
    p3.add_argument("--platform", required=True)
    p3.add_argument("--status", required=True)
    p3.add_argument("--extra-json", default="{}")

    args = ap.parse_args()
    post_dir = Path(args.post_dir).expanduser().resolve()

    if args.cmd == "preflight":
        print(json.dumps(preflight(post_dir), ensure_ascii=False, indent=2))
    elif args.cmd == "build-xhs-pack":
        print(json.dumps(build_xhs_pack(post_dir, args.cards), ensure_ascii=False, indent=2))
    else:
        extra = json.loads(args.extra_json)
        p = update_publish_log(post_dir, args.platform, args.status, extra)
        print(str(p))


if __name__ == "__main__":
    main()
