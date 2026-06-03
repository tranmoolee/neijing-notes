#!/usr/bin/env python3
"""
Publish wechat draft for 生气通天论-小结 with clean body text + clean images.
No HTML styling, no pure-image format — real article text with interspersed clean images.
"""
import json, os, re, sys
from pathlib import Path
import requests

BASE = Path("/Users/tranmoo/neijing-notes/生气通天论-小结")
IMAGES = BASE / "xhs-publish-pack" / "images"
WECHAT_IMAGES = BASE / "wechat-images"

# ── Credentials ──
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
    print("❌ WECHAT_APP_ID or WECHAT_APP_SECRET not found in ~/.hermes/.env")
    sys.exit(1)

def get_token():
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token",
                     params={"grant_type": "client_credential", "appid": APP_ID, "secret": APP_SECRET})
    r.raise_for_status()
    d = r.json()
    if "access_token" not in d:
        raise RuntimeError(f"WeChat auth failed: {d}")
    return d["access_token"]

def upload_permanent(token, path, media_type="image"):
    """Upload permanent material (for cover)."""
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.weixin.qq.com/cgi-bin/material/add_material",
            params={"access_token": token, "type": media_type},
            files={"media": (path.name, f, "image/jpeg")}
        )
    r.raise_for_status()
    d = r.json()
    if "media_id" not in d:
        raise RuntimeError(f"Permanent upload failed: {d}")
    return d["media_id"]

def upload_temporary(token, path):
    """Upload temporary image (returns CDN url)."""
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
            params={"access_token": token},
            files={"media": (path.name, f, "image/jpeg")}
        )
    r.raise_for_status()
    d = r.json()
    if "url" not in d:
        raise RuntimeError(f"Temporary upload failed: {d}")
    return d["url"]

def create_draft(token, html, title, digest, cover_media_id):
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

def main():
    # 1. Read wechat.md for the article text
    wc_md = BASE / "wechat.md"
    if not wc_md.exists():
        print("❌ wechat.md not found")
        sys.exit(1)
    
    md_text = wc_md.read_text("utf-8")
    
    # Extract title (first # line)
    title_match = re.search(r'^# (.+)$', md_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = "生气通天论小结"
    
    # WeChat title max ~10 chars, keep it short
    if len(title) > 10:
        title = "生气通天论小结"
    
    # Extract digest: first non-empty, non-header line after the title
    digest = ""
    for line in md_text.split("\n"):
        clean = line.strip()
        if clean and not clean.startswith("#") and not clean.startswith(">") and clean != "---":
            digest = clean[:50]
            break
    
    print(f"📖 Title: {title}")
    print(f"📖 Digest: {digest}")
    
    # 2. Copy clean images to wechat-images/
    WECHAT_IMAGES.mkdir(parents=True, exist_ok=True)
    image_files = sorted(IMAGES.glob("*.jpg"))
    for img in image_files:
        out_path = WECHAT_IMAGES / img.name
        out_path.write_bytes(img.read_bytes())
    print(f"📁 Copied {len(image_files)} images to {WECHAT_IMAGES}")
    
    # 3. Get token
    print("🔑 Getting access token...")
    token = get_token()
    
    # 4. Upload cover as permanent material
    print("⬆️  Uploading cover...")
    cover_path = WECHAT_IMAGES / "cover.jpg"
    if not cover_path.exists():
        print("❌ cover.jpg not found")
        sys.exit(1)
    cover_media_id = upload_permanent(token, cover_path)
    print(f"   Cover media_id: {cover_media_id}")
    
    # 5. Upload all cards as temporary (get CDN urls for body)
    print("⬆️  Uploading card images...")
    cdn_urls = {}
    # Upload cover to temporary too (in case needed in body)
    cover_url = upload_temporary(token, cover_path)
    cdn_urls["cover.jpg"] = cover_url
    print(f"   ✅ cover.jpg → CDN")
    
    card_names = [f"card-{i:02d}.jpg" for i in range(1, 9)]
    for name in card_names:
        path = WECHAT_IMAGES / name
        if not path.exists():
            print(f"  ⚠️  {name} not found, skipping")
            continue
        url = upload_temporary(token, path)
        cdn_urls[name] = url
        print(f"   ✅ {name} → CDN")
    
    # 6. Build body content from wechat.md
    # Clean, minimal formatting — like what WeChat editor natively produces
    print("📝 Building article body...")
    
    lines = md_text.split("\n")
    html_parts = []
    
    for line in lines:
        # Skip the title line (already in title field)
        if line.startswith("# ") and line.strip() == f"# {title}":
            continue
        
        # Image references: ![alt](images/xxx.jpg) — replace with img tag
        img_match = re.match(r'!\[.*?\]\((images/[^)]+)\)', line)
        if img_match:
            local_ref = img_match.group(1)
            fname = os.path.basename(local_ref)
            cdn_url = cdn_urls.get(fname)
            if cdn_url:
                html_parts.append(
                    f'<p style="text-align: center;">'
                    f'<img src="{cdn_url}" data-src="{cdn_url}" '
                    f'style="width: 100%; max-width: 400px;" alt=""/>'
                    f'</p>'
                )
            continue
        
        # Horizontal rule
        if line.strip() == "---":
            html_parts.append('<hr style="border-top: 1px solid #e0e0e0; margin: 24px 0;"/>')
            continue
        
        # Blockquote
        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            if text:
                # Bold within blockquote
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                html_parts.append(
                    f'<section style="padding: 10px 16px; margin: 12px 0; '
                    f'background: #f7f7f7; border-radius: 4px; color: #666;">'
                    f'<p style="margin: 0;">{text}</p></section>'
                )
            continue
        
        # Heading
        if line.startswith("## "):
            text = line[3:].strip()
            html_parts.append(
                f'<p style="font-weight: bold; font-size: 17px; '
                f'margin: 28px 0 12px;">{text}</p>'
            )
            continue
        
        # Bold inline
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        
        # Regular paragraph
        if line.strip():
            html_parts.append(f'<p style="margin: 8px 0; line-height: 1.8;">{line.strip()}</p>')
        else:
            html_parts.append('<p style="margin: 8px 0;">&nbsp;</p>')
    
    body_html = "\n".join(html_parts)
    
    # 7. Create draft
    print("📝 Creating WeChat draft...")
    draft_media_id = create_draft(token, body_html, title, digest, cover_media_id)
    print(f"✅ Draft created! media_id: {draft_media_id}")
    
    # 8. Save log
    result = {
        "wechat_draft": {
            "status": "created",
            "draft_media_id": draft_media_id,
            "title": title,
            "digest": digest,
            "images_uploaded": len(cdn_urls),
            "method": "clean_text_with_images",
        }
    }
    log_path = BASE / "publish-log.json"
    existing = {}
    if log_path.exists():
        existing = json.loads(log_path.read_text("utf-8"))
    existing.update(result)
    log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"📋 Log saved to {log_path}")
    
    print("\n✅ Done! Login to mp.weixin.qq.com → 草稿箱 to preview.")

if __name__ == "__main__":
    main()
