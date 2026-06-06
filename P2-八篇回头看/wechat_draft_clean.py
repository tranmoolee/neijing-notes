#!/usr/bin/env python3
"""
P2-八篇回头看 → WeChat draft.
- source: ghost.md (with ![]() image references)
- images dir: xhs-publish-pack/images/ (overlaid text images)
- cover: xhs-publish-pack/images/header-wechat.jpg
- upload: permanent material library (material/add_material) + CDN URLs for body
"""
import json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone
import requests

BASE = Path("/Users/tranmoo/neijing-notes/P2-八篇回头看")
GHOST_MD = BASE / "ghost.md"
IMG_DIR = BASE / "xhs-publish-pack" / "images"
OUT_DIR = BASE / "wechat-images"  # working copy

def load_creds():
    env_path = Path.home() / ".hermes" / ".env"
    vals = {}
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    return vals.get("WECHAT_APP_ID", ""), vals.get("WECHAT_APP_SECRET", "")

APP_ID, APP_SECRET = load_creds()
if not APP_ID or not APP_SECRET:
    print("❌ WECHAT_APP_ID / WECHAT_APP_SECRET not found")
    sys.exit(1)

def get_token():
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": APP_ID, "secret": APP_SECRET})
    r.raise_for_status()
    d = r.json()
    if "access_token" not in d:
        raise RuntimeError(f"Auth failed: {d}")
    return d["access_token"]

def upload_permanent(token, path, mime="image/jpeg"):
    """Upload image as permanent material (素材库). Returns media_id."""
    with open(path, "rb") as f:
        r = requests.post("https://api.weixin.qq.com/cgi-bin/material/add_material",
            params={"access_token": token, "type": "image"},
            files={"media": (path.name, f, mime)})
    r.raise_for_status()
    d = r.json()
    if "media_id" not in d:
        raise RuntimeError(f"Permanent upload failed for {path.name}: {d}")
    return d["media_id"]

def upload_temporary_cdn(token, path, mime="image/jpeg"):
    """Upload image as temporary image, returns CDN URL for body content."""
    with open(path, "rb") as f:
        r = requests.post("https://api.weixin.qq.com/cgi-bin/media/uploadimg",
            params={"access_token": token},
            files={"media": (path.name, f, mime)})
    r.raise_for_status()
    d = r.json()
    if "url" not in d:
        raise RuntimeError(f"Temporary upload failed for {path.name}: {d}")
    return d["url"]

def upload_all_images(token):
    """
    Upload all images to:
    1. Permanent material library (素材库) → for permanent storage
    2. Temporary CDN → for body content reference
    Returns {local_ref: cdn_url}
    """
    if not IMG_DIR.exists():
        print(f"❌ IMG_DIR not found: {IMG_DIR}")
        return {}

    url_map = {}
    files = sorted(list(IMG_DIR.glob("*.jpg")) + list(IMG_DIR.glob("*.png")))
    print(f"📁 Found {len(files)} images in {IMG_DIR.parent.name}/images/")

    for f in files:
        fname = f.name
        mime_prefix = "image/png" if fname.endswith(".png") else "image/jpeg"
        local_ref = f"images/{fname}"

        # Step 1: Upload to permanent material library
        try:
            media_id = upload_permanent(token, f, mime_prefix)
            print(f"  ⬆️  {fname} → 素材库 (media_id: {media_id[:30]}...)")
        except Exception as e:
            print(f"  ⚠️  {fname} permanent upload failed: {e}")

        # Step 2: Upload for CDN URL (body reference)
        try:
            cdn_url = upload_temporary_cdn(token, f, mime_prefix)
            url_map[local_ref] = cdn_url
            print(f"  ✅ {fname} → CDN")
        except Exception as e:
            print(f"  ⚠️  {fname} CDN upload failed: {e}")

    return url_map

def parse_frontmatter(text):
    """Extract YAML frontmatter and body from ghost.md."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return parts[-1].strip() if len(parts) > 1 else text, {}
    body = parts[2].strip()
    fm = {}
    for line in parts[1].split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("-") and not line.startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return body, fm

def shorten_title(title, max_chars=10):
    return title[:max_chars]

def extract_digest(body, max_bytes=55):
    clean = re.sub(r'[#>*\[\]`|!]', '', body).strip()
    for i in range(max_bytes, 0, -1):
        chunk = clean[:i].encode('utf-8')
        if len(chunk) <= max_bytes:
            return chunk.decode('utf-8', errors='replace')
    return ""

def ghost_md_to_wechat_html(md_body, image_url_map):
    """Convert ghost.md body to WeChat HTML with CDN image refs."""
    lines = md_body.split("\n")
    html_parts = []
    in_blockquote = False

    for line in lines:
        img_match = re.match(r'!\[.*?\]\((images/[^)]+)\)', line)
        if img_match:
            local_path = img_match.group(1)
            # The local_path is like "images/card-01.jpg" 
            # Our url_map has keys like "images/card-01.jpg"
            cdn_url = image_url_map.get(local_path, "")
            if cdn_url:
                html_parts.append(f'<img src="{cdn_url}" style="width:100%;margin:16px 0;"/>')
            continue

        if line.strip() == "---":
            if in_blockquote:
                html_parts.append("</blockquote>")
                in_blockquote = False
            html_parts.append('<hr style="border:none;border-top:1px solid #ddd;margin:24px 0;"/>')
            continue

        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            if text:
                if not in_blockquote:
                    html_parts.append('<blockquote style="border-left:4px solid #c84b5a;padding:8px 16px;margin:16px 0;color:#666;">')
                    in_blockquote = True
                html_parts.append(f"<p>{text}</p>")
            continue
        elif in_blockquote and line.strip() == "":
            html_parts.append("</blockquote>")
            in_blockquote = False
            continue
        elif in_blockquote:
            html_parts.append("</blockquote>")
            in_blockquote = False

        if line.startswith("## "):
            html_parts.append(f'<h2 style="font-size:18px;margin:24px 0 12px;">{line[3:]}</h2>')
            continue
        if line.startswith("### "):
            html_parts.append(f'<h3 style="font-size:16px;margin:20px 0 10px;">{line[4:]}</h3>')
            continue

        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)

        if line.strip():
            html_parts.append(f'<p style="margin:8px 0;line-height:1.8;">{line.strip()}</p>')
        else:
            html_parts.append('<p style="margin:8px 0;">&nbsp;</p>')

    if in_blockquote:
        html_parts.append("</blockquote>")

    return "\n".join(html_parts)

def main():
    # 1. Read ghost.md
    if not GHOST_MD.exists():
        print(f"❌ ghost.md not found"); sys.exit(1)
    md_text = GHOST_MD.read_text("utf-8")
    md_body, fm = parse_frontmatter(md_text)
    raw_title = fm.get("title", "P2-八篇回头看")
    title = shorten_title(raw_title)
    digest = extract_digest(md_body)

    print(f"📖 Full title: {raw_title}")
    print(f"📖 Title ({len(title)} chars): {title}")
    print(f"📖 Digest: {digest}")

    # 2. Copy images to working dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    if IMG_DIR.exists():
        for f in list(IMG_DIR.glob("*.jpg")) + list(IMG_DIR.glob("*.png")):
            out_path = OUT_DIR / f.name
            out_path.write_bytes(f.read_bytes())
            copied += 1
    print(f"📁 Copied {copied} images (from xhs-publish-pack/images/) to {OUT_DIR}")

    # 3. Get token
    print("🔑 Getting access token...")
    token = get_token()

    # 4. Upload cover to permanent material
    # Use header-wechat.jpg from xhs-publish-pack (social-card landscape for WeChat)
    cover_candidates = [
        OUT_DIR / "header-wechat.jpg",
        OUT_DIR / "wechat-header-21x9.png",
        OUT_DIR / "cover.jpg",
    ]
    cover_path = None
    for c in cover_candidates:
        if c.exists():
            cover_path = c
            break
    if not cover_path:
        print("❌ No cover image found")
        sys.exit(1)

    mime = "image/png" if str(cover_path).endswith(".png") else "image/jpeg"
    print(f"⬆️  Uploading cover to 素材库: {cover_path.name}")
    cover_mid = upload_permanent(token, cover_path, mime)
    print(f"   Cover media_id: {cover_mid}")

    # 5. Upload ALL images to 素材库 + CDN
    print("⬆️  Uploading images to 素材库 + CDN...")
    url_map = upload_all_images(token)
    print(f"   {len(url_map)} images available for body")

    # 6. Convert ghost.md to WeChat HTML
    print("📝 Converting ghost.md → WeChat HTML...")
    wechat_html = ghost_md_to_wechat_html(md_body, url_map)

    img_count = wechat_html.count('<img src=')
    print(f"📄 HTML body: {len(wechat_html)} chars, {img_count} images inserted")

    # 7. Create draft
    print("📝 Creating WeChat draft...")
    article = {
        "title": title,
        "author": "Leem",
        "digest": digest,
        "content": wechat_html,
        "content_source_url": "",
        "thumb_media_id": cover_mid,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    payload = {"articles": [article]}
    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    r = requests.post("https://api.weixin.qq.com/cgi-bin/draft/add",
        params={"access_token": token},
        data=body_bytes,
        headers={"Content-Type": "application/json; charset=utf-8"})
    r.raise_for_status()
    d = r.json()
    if "media_id" not in d:
        raise RuntimeError(f"Draft creation failed: {d}")
    draft_media_id = d["media_id"]
    print(f"✅ Draft created! media_id: {draft_media_id}")

    # 8. Save publish-log
    result = {"wechat": {
        "status": "draft_created",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "draft_media_id": draft_media_id,
        "title": raw_title,
        "digest": digest,
        "method": "ghost_md_with_xhs_overlay_images",
        "cover_source": "xhs-publish-pack/images/header-wechat.jpg",
        "image_source": "xhs-publish-pack/images/ (overlaid text)",
        "upload_method": "permanent_material + CDN",
        "body_images": img_count,
    }}
    log_path = BASE / "publish-log.json"
    existing = {}
    if log_path.exists():
        existing = json.loads(log_path.read_text("utf-8"))
    existing["wechat"] = result["wechat"]
    log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"📋 Log saved to {log_path}")
    print("\n⚠️  Draft ready. Login to mp.weixin.qq.com → 草稿箱 to preview and publish.")

if __name__ == "__main__":
    main()
