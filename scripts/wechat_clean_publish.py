#!/usr/bin/env python3
"""
WeChat draft publishing for neijing-notes.
Clean API: sends Chinese text as raw UTF-8 (no HTML entity hacks).
Saves separate wechat-images/ locally.
"""

import json, os, sys, re
from pathlib import Path
from datetime import datetime, timezone
import requests

# ── Config ──────────────────────────────────────────────────────────
def load_creds():
    env_path = Path.home() / ".hermes" / ".env"
    vals = {}
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                vals[k] = v
    return vals.get("WECHAT_APP_ID", ""), vals.get("WECHAT_APP_SECRET", "")

APP_ID, APP_SECRET = load_creds()
POST_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
OUT_DIR = POST_DIR / "wechat-images"

# ── Frontmatter helpers ─────────────────────────────────────────────
def parse_frontmatter(text):
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
    """WeChat title limit: 10 chars."""
    if len(title) <= max_chars:
        return title
    m = re.match(r'^(第[一二三四五六七八九十\d]+篇[：:])(.+)$', title)
    if m:
        prefix = m.group(1)
        suffix = m.group(2)
        remain = max_chars - len(prefix)
        if remain >= 2:
            return prefix + suffix[:remain]
    return title[:max_chars]

def extract_digest(body, max_bytes=55):
    """Extract first clean sentence as digest."""
    clean = re.sub(r'[#>*\[\]`|!]', '', body).strip()
    # Take up to max_bytes
    for i in range(max_bytes, 0, -1):
        chunk = clean[:i].encode('utf-8')
        if len(chunk) <= max_bytes:
            return chunk.decode('utf-8', errors='replace')
    return ""

# ── WeChat API ──────────────────────────────────────────────────────
def get_token():
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token",
                     params={"grant_type": "client_credential", "appid": APP_ID, "secret": APP_SECRET})
    r.raise_for_status()
    d = r.json()
    if "access_token" not in d:
        raise RuntimeError(f"WeChat auth failed: {d}")
    return d["access_token"]

def upload_cover(token, path):
    """Upload cover as permanent material (material/add_material)."""
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.weixin.qq.com/cgi-bin/material/add_material",
            params={"access_token": token, "type": "image"},
            files={"media": (path.name, f, "image/jpeg")}
        )
    r.raise_for_status()
    d = r.json()
    if "media_id" not in d:
        raise RuntimeError(f"Cover upload failed: {d}")
    return d["media_id"]

def upload_content_images(token):
    """Upload all content images via media/uploadimg. Returns {local_ref: cdn_url}."""
    img_dir = POST_DIR / "images"
    url_map = {}
    for name in sorted(img_dir.glob("*.jpg")):
        fname = name.name
        with open(name, "rb") as f:
            r = requests.post(
                "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
                params={"access_token": token},
                files={"media": (fname, f, "image/jpeg")}
            )
        r.raise_for_status()
        d = r.json()
        if "url" in d:
            url_map[f"images/{fname}"] = d["url"]
            print(f"  ✅ {fname} → CDN")
        else:
            print(f"  ⚠️  {fname}: no url: {d}")
    return url_map

def create_draft(token, html, title, digest, cover_media_id):
    """Create WeChat draft with raw UTF-8 JSON (no HTML entities)."""
    article = {
        "title": title,
        "author": "Leem",
        "digest": digest,
        "content": html,
        "content_source_url": "",
        "thumb_media_id": cover_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    payload = {"articles": [article]}
    
    # KEY FIX: send raw UTF-8 JSON, not escaped \uXXXX
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    r = requests.post(
        "https://api.weixin.qq.com/cgi-bin/draft/add",
        params={"access_token": token},
        data=body,
        headers=headers,
    )
    r.raise_for_status()
    d = r.json()
    if "media_id" not in d:
        raise RuntimeError(f"Draft creation failed: {d}")
    return d["media_id"]

def ghost_md_to_wechat_html(md_body, image_url_map):
    """Convert ghost.md body to WeChat-compatible HTML with CDN image refs."""
    lines = md_body.split("\n")
    html_parts = []
    in_blockquote = False
    
    for line in lines:
        # Image references: ![alt](images/xxx.jpg)
        img_match = re.match(r'!\[.*?\]\((images/[^)]+)\)', line)
        if img_match:
            local_path = img_match.group(1)
            cdn_url = image_url_map.get(local_path, "")
            if cdn_url:
                html_parts.append(f'<img src="{cdn_url}" style="width:100%;margin:16px 0;"/>')
            continue
        
        # Horizontal rule
        if line.strip() == "---":
            html_parts.append("<hr style=\"border:none;border-top:1px solid #ddd;margin:24px 0;\"/>")
            continue
        
        # Blockquote
        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            if text:
                if not in_blockquote:
                    html_parts.append("<blockquote style=\"border-left:4px solid #c84b5a;padding:8px 16px;margin:16px 0;color:#666;\">")
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
        
        # Headings
        if line.startswith("## "):
            html_parts.append(f"<h2 style=\"font-size:18px;margin:24px 0 12px;\">{line[3:]}</h2>")
            continue
        if line.startswith("### "):
            html_parts.append(f"<h3 style=\"font-size:16px;margin:20px 0 10px;\">{line[4:]}</h3>")
            continue
        
        # Bold text
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        
        # Regular paragraph
        if line.strip():
            html_parts.append(f"<p style=\"margin:8px 0;line-height:1.8;\">{line.strip()}</p>")
        else:
            html_parts.append("<p style=\"margin:8px 0;\">&nbsp;</p>")
    
    # Close any open blockquote
    if in_blockquote:
        html_parts.append("</blockquote>")
    
    return "\n".join(html_parts)

# ── Main ────────────────────────────────────────────────────────────
def main():
    # Read ghost.md
    ghost_path = POST_DIR / "ghost.md"
    if not ghost_path.exists():
        print(f"❌ ghost.md not found in {POST_DIR}")
        sys.exit(1)
    
    md_text = ghost_path.read_text("utf-8")
    md_body, fm = parse_frontmatter(md_text)
    title = shorten_title(fm.get("title", POST_DIR.name))
    digest = extract_digest(md_body)
    
    print(f"📖 Title: {title} ({len(title)} chars)")
    print(f"📖 Digest: {digest} ({len(digest.encode('utf-8'))} bytes)")
    
    # 1. Copy images to wechat-images/
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img_dir = POST_DIR / "images"
    copied = 0
    if img_dir.exists():
        for f in img_dir.glob("*.jpg"):
            out_path = OUT_DIR / f.name
            out_path.write_bytes(f.read_bytes())
            copied += 1
    print(f"📁 Copied {copied} images to {OUT_DIR}")
    
    # 2. Get token
    print("🔑 Getting access token...")
    token = get_token()
    
    # 3. Upload cover
    print("⬆️  Uploading cover...")
    cover_path = OUT_DIR / "cover.jpg"
    if not cover_path.exists():
        print(f"❌ cover.jpg not found")
        sys.exit(1)
    cover_media_id = upload_cover(token, cover_path)
    print(f"   Cover media_id: {cover_media_id}")
    
    # 4. Upload content images
    print("⬆️  Uploading content images...")
    url_map = upload_content_images(token)
    print(f"   {len(url_map)} images uploaded")
    
    # 5. Convert ghost.md to WeChat HTML
    print("📝 Converting to WeChat HTML...")
    wechat_html = ghost_md_to_wechat_html(md_body, url_map)
    
    # 6. Create draft
    print("📝 Creating draft...")
    draft_media_id = create_draft(token, wechat_html, title, digest, cover_media_id)
    print(f"✅ Draft created! media_id: {draft_media_id}")
    
    # 7. Save publish-log
    result = {
        "wechat": {
            "status": "draft_created",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "draft_media_id": draft_media_id,
            "title": title,
            "digest": digest,
            "method": "clean_utf8_json",
            "content_images": len([k for k in url_map if k != "images/cover.jpg"]),
        }
    }
    log_path = POST_DIR / "publish-log.json"
    existing = {}
    if log_path.exists():
        existing = json.loads(log_path.read_text("utf-8"))
    existing.update(result)
    log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"📋 Log saved to {log_path}")
    
    print("\n⚠️  Draft ready for review. Login to WeChat MP to preview and publish.")

if __name__ == "__main__":
    main()
