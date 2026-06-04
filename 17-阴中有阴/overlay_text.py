#!/usr/bin/env python3
"""Overlay text onto 17-阴中有阴 images using Pillow."""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

BASE = "/Users/tranmoo/neijing-notes/17-阴中有阴"
IMG_DIR = os.path.join(BASE, "images")
OUT_DIR = os.path.join(BASE, "img-temp")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_TITLE = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_BODY = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_SUB = "/System/Library/Fonts/Hiragino Sans GB.ttc"

W, H = 1024, 1536

def make_font(path, size):
    return ImageFont.truetype(path, size)

def draw_text(draw, text, font, color, y, max_w=800, align="center", line_spacing=1.3):
    """Draw text with word wrap."""
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.fill(para, width=30) if font.size > 35 else textwrap.fill(para, width=40)
        lines.extend(wrapped.split("\n"))
    
    line_h = int(font.size * line_spacing)
    total_h = len(lines) * line_h
    start_y = y - total_h // 2 if align == "center" else y
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, start_y + i * line_h), line, font=font, fill=color)
    
    return start_y + len(lines) * line_h

# ========== Define overlays for each card ==========
overlays = {
    "cover": {
        "lines": [
            ("阴阳不是二分法", make_font(FONT_TITLE, 64), (212, 160, 96)),  # gold
            ("是俄罗斯套娃", make_font(FONT_TITLE, 52), (240, 224, 200)),    # warm white
            ("学渣读经 · 第十七篇", make_font(FONT_SUB, 28), (180, 180, 180)),  # grey
        ],
        "y_positions": [600, 680, 750],
    },
    "card-01": {
        "lines": [
            ("阴中有阴", make_font(FONT_TITLE, 56), (212, 160, 96)),
            ("阳中有阳", make_font(FONT_TITLE, 56), (240, 224, 200)),
        ],
        "body": "以前我以为阴阳是二分法\n白天阳，晚上阴，一刀两半\n\n这段话说：\n分完之后，每一半还能继续分",
        "y_positions": [550, 630],
        "body_y": 850,
    },
    "card-02": {
        "title": "一天四段，四种阴阳",
        "body": "清晨→中午：阳中之阳 ☀\n中午→傍晚：阳中之阴 🌤\n前半夜：阴中之阴 🌙\n后半夜→天亮：阴中之阳 🌅",
        "y_title": 550,
        "y_body": 700,
    },
    "card-03": {
        "title": "身体也是套娃",
        "body": "第一层：外为阳，内为阴\n第二层：背为阳，腹为阴\n第三层：脏为阴，腑为阳\n第四层：每个脏各有阴阳\n\n层层嵌套，像分形一样\n在每个尺度上重复",
        "y_title": 550,
        "y_body": 700,
    },
    "card-04": {
        "title": "心——阴中之阳",
        "body": "心是脏，脏属阴——所以心属阴\n但心主火、对应夏天\n功能上最\"阳\"\n\n心是\"阴中之阳\"\n\n同一个东西\n有时说阴有时说阳——不矛盾\n取决于你在哪一层比较",
        "y_title": 520,
        "y_body": 660,
    },
    "card-05": {
        "title": "\"故人亦应之\"",
        "body": "天有阳中阳、阳中阴\n阴中阴、阴中阳\n\n人也有\n\n不是\"有点像\"\n是同一套结构\n在不同尺度上的重复",
        "y_title": 550,
        "y_body": 700,
    },
    "card-06": {
        "title": "暂时的理解",
        "body": "阴阳是可以无限嵌套的结构\n白天里有阳有阴\n夜里也有阴有阳\n\n人体也是：外内、背腹、脏腑\n——层层套娃\n\n知道这个结构是为了定位\n你的病在阴阳的第几层？",
        "y_title": 520,
        "y_body": 660,
    },
    "card-07": {
        "title": "留的坑",
        "body": "① \"肾阴\"\"肾阳\"\n是不是第四层嵌套？\n\n② 春病在阴、秋病在阳\n为什么？\n\n③ 阴阳的\"层数\"\n临床一般分到第几层？",
        "y_title": 520,
        "y_body": 660,
    },
    "card-08": {
        "title": "下期预告",
        "body": "第二阶段读完了\n\n下一阶段：《阴阳应象大论》\n理论密度最高的一章\n\n做好了被虐的准备",
        "y_title": 520,
        "y_body": 700,
    },
}

def render_card(img_path, out_path, cfg):
    img = Image.open(img_path).convert("RGB").resize((W, H), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    
    from PIL import ImageFilter
    
    def make_glow_layer(text, font, pos, blur_radius=6):
        """Create a soft glow/shadow layer using Gaussian blur."""
        x, y = pos
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = int(blur_radius * 3)
        glow = Image.new("RGBA", (W + pad*2, H + pad*2), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.text((pad + x, pad + y), text, font=font, fill=(0, 0, 0, 180))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return glow, pad
    
    def shadow_text(text, font, fill, pos):
        """Draw text with a Gaussian-blurred glow for feathering."""
        x, y = pos
        glow, pad = make_glow_layer(text, font, pos, blur_radius=2)
        img.paste(glow, (-pad, -pad), glow)
        draw.text((x, y), text, font=font, fill=fill)
    
    def draw_centered(text, font, fill, y):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        shadow_text(text, font, fill, ((W - tw) // 2, y))
    
    if "title" in cfg and "lines" not in cfg:
        ft = make_font(FONT_TITLE, 48)
        draw_centered(cfg["title"], ft, (212, 160, 96), cfg["y_title"])
        
        fb = make_font(FONT_BODY, 28)
        for i, line in enumerate(cfg["body"].split("\n")):
            draw_centered(line, fb, (230, 220, 210), cfg["y_body"] + i * 38)
    elif "lines" in cfg:
        for (text, font, color), y in zip(cfg["lines"], cfg["y_positions"]):
            draw_centered(text, font, color, y)
        
        if "body" in cfg:
            fb = make_font(FONT_BODY, 28)
            for i, line in enumerate(cfg["body"].split("\n")):
                draw_centered(line, fb, (230, 220, 210), cfg.get("body_y", 800) + i * 38)
    
    img.save(out_path, "JPEG", quality=92)
    print(f"  ✅ {os.path.basename(out_path)}")

# Cover
print("📝 Overlaying text on images...")
render_card(
    os.path.join(IMG_DIR, "cover.jpg"),
    os.path.join(OUT_DIR, "cover.jpg"),
    overlays["cover"]
)

# Cards 1-8
for i in range(1, 9):
    key = f"card-{i:02d}"
    render_card(
        os.path.join(IMG_DIR, f"{key}.jpg"),
        os.path.join(OUT_DIR, f"{key}.jpg"),
        overlays[key]
    )

print(f"\n✅ All 9 images saved to {OUT_DIR}")
