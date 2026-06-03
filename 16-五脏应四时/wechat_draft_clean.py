#!/usr/bin/env python3
"""
Publish wechat draft for 16-五脏应四时 with clean body text + overlaid images.
"""
import json, os, re, sys
from pathlib import Path
import requests

BASE = Path("/Users/tranmoo/neijing-notes/16-五脏应四时")
IMAGES = BASE / "xhs-publish-pack" / "images"
WECHAT_IMAGES = BASE / "wechat-images"

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

def upload_permanent(token, path):
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

def upload_temporary(token, path):
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
            params={"access_token": token},
            files={"media": (path.name, f, "image/jpeg")}
        )
    r.raise_for_status()
    d = r.json()
    if "url" not in d:
        raise RuntimeError(f"Temp upload failed: {d}")
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
    wc_md = BASE / "wechat.md"
    if not wc_md.exists():
        print("❌ wechat.md not found"); sys.exit(1)
    
    md_text = wc_md.read_text("utf-8")
    title_match = re.search(r'^# (.+)$', md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "五脏应四时"
    if len(title) > 10:
        title = "五脏应四时"
    
    digest = ""
    for line in md_text.split("\n"):
        clean = line.strip()
        if clean and not clean.startswith("#") and not clean.startswith(">") and clean != "---":
            digest = clean[:50]; break
    
    print(f"📖 Title: {title}")
    print(f"📖 Digest: {digest}")
    
    WECHAT_IMAGES.mkdir(parents=True, exist_ok=True)
    image_files = sorted(IMAGES.glob("*.jpg"))
    for img in image_files:
        (WECHAT_IMAGES / img.name).write_bytes(img.read_bytes())
    print(f"📁 Copied {len(image_files)} images")
    
    print("🔑 Getting token...")
    token = get_token()
    
    print("⬆️  Uploading cover...")
    cover_path = WECHAT_IMAGES / "cover.jpg"
    cover_media_id = upload_permanent(token, cover_path)
    print(f"   Cover media_id: {cover_media_id}")
    
    print("⬆️  Uploading card images...")
    cdn_urls = {}
    cover_url = upload_temporary(token, cover_path)
    cdn_urls["cover.jpg"] = cover_url
    
    for name in sorted(f"card-{i:02d}.jpg" for i in range(1, 9)):
        path = WECHAT_IMAGES / name
        if path.exists():
            url = upload_temporary(token, path)
            cdn_urls[name] = url
            print(f"   ✅ {name}")
    
    print("📝 Building article body...")
    lines = md_text.split("\n")
    html_parts = []
    
    for line in lines:
        if line.startswith("# ") and line.strip() == f"# {title}":
            continue
        img_match = re.match(r'!\[.*?\]\((images/[^)]+)\)', line)
        if img_match:
            fname = os.path.basename(img_match.group(1))
            cdn_url = cdn_urls.get(fname)
            if cdn_url:
                html_parts.append(
                    f'<p style="text-align:center;">'
                    f'<img src="{cdn_url}" data-src="{cdn_url}" '
                    f'style="width:100%;max-width:400px;" alt=""/>'
                    f'</p>'
                )
            continue
        if line.strip() == "---":
            html_parts.append('<hr style="border-top:1px solid #e0e0e0;margin:24px 0;"/>')
            continue
        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            if text:
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                html_parts.append(
                    f'<section style="padding:10px 16px;margin:12px 0;'
                    f'background:#f7f7f7;border-radius:4px;color:#666;">'
                    f'<p style="margin:0;">{text}</p></section>'
                )
            continue
        if line.startswith("## "):
            html_parts.append(f'<p style="font-weight:bold;font-size:17px;margin:28px 0 12px;">{line[3:].strip()}</p>')
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        if line.strip():
            html_parts.append(f'<p style="margin:8px 0;line-height:1.8;">{line.strip()}</p>')
        else:
            html_parts.append('<p style="margin:8px 0;">&nbsp;</p>')
    
    body_html = "\n".join(html_parts)
    
    print("📝 Creating WeChat draft...")
    draft_media_id = create_draft(token, body_html, title, digest, cover_media_id)
    print(f"✅ Draft created! media_id: {draft_media_id}")
    
    result = {"wechat_draft": {"status":"created","draft_media_id":draft_media_id,"title":title,"digest":digest,"images_uploaded":len(cdn_urls)}}
    log_path = BASE / "publish-log.json"
    existing = {}
    if log_path.exists():
        existing = json.loads(log_path.read_text("utf-8"))
    existing.update(result)
    log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", "utf-8")
    
    print("\n✅ Done! Login to mp.weixin.qq.com → 草稿箱 to preview.")

if __name__ == "__main__":
    main()
