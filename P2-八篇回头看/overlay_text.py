#!/usr/bin/env python3
"""Overlay text onto P2-八篇回头看 images using Pillow (2px stroke, no shadow)."""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

BASE = "/Users/tranmoo/neijing-notes/P2-八篇回头看"
IMG_DIR = os.path.join(BASE, "images")
XHS_DIR = os.path.join(BASE, "xhs-publish-pack", "images")
os.makedirs(XHS_DIR, exist_ok=True)

FONT_TITLE = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_BODY = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_SUB = "/System/Library/Fonts/Hiragino Sans GB.ttc"

W, H = 1024, 1536
STROKE = 2
STROKE_COLOR = (0, 0, 0, 200)

def make_font(path, size):
    return ImageFont.truetype(path, size)

def draw_text_centered(draw, text, font, color, center_y, line_spacing=1.3):
    """Draw text centered at center_y with 2px stroke."""
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.fill(para, width=28) if font.size > 40 else textwrap.fill(para, width=36)
        lines.extend(wrapped.split("\n"))
    line_h = int(font.size * line_spacing)
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, start_y + i * line_h), line, font=font, fill=color,
                  stroke_width=STROKE, stroke_fill=STROKE_COLOR)
    return start_y + len(lines) * line_h

def draw_text_left(draw, text, font, color, x, y, line_spacing=1.3):
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.fill(para, width=28 if font.size > 40 else 36)
        lines.extend(wrapped.split("\n"))
    line_h = int(font.size * line_spacing)
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, font=font, fill=color,
                  stroke_width=STROKE, stroke_fill=STROKE_COLOR)
    return y + len(lines) * line_h

def create_overlay(img_name, overlay_items):
    src = os.path.join(IMG_DIR, img_name)
    dst = os.path.join(XHS_DIR, img_name)
    img = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for item in overlay_items:
        text, font, color, y = item[0], item[1], item[2], item[3]
        align = item[4] if len(item) > 4 else "center"
        if align == "left":
            draw_text_left(draw, text, font, color, 80, y)
        else:
            draw_text_centered(draw, text, font, color, y)
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(dst, "JPEG", quality=95)
    print(f"✅ {img_name}")

# Colors
GOLD = (212, 160, 96)
WARM_WHITE = (240, 224, 200)
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)
SOFT_GOLD = (180, 160, 120)

F64 = make_font(FONT_TITLE, 64)
F52 = make_font(FONT_TITLE, 52)
F48 = make_font(FONT_TITLE, 48)
F40 = make_font(FONT_TITLE, 40)
F36 = make_font(FONT_BODY, 36)
F32 = make_font(FONT_BODY, 32)
F28 = make_font(FONT_SUB, 28)
F24 = make_font(FONT_SUB, 24)

# cover — 八本书 + 茶碗
create_overlay("cover.jpg", [
    ('那张「五行大表」', F52, GOLD, 560),
    ('根本不是用来背的', F48, WARM_WHITE, 640),
    ('', F36, (0,0,0,0), 720),
    ('学渣读内经', F32, WHITE, 810),
    ('第二阶段回头看 · 10-17', F28, LIGHT_GREY, 860),
])

# card-01 — 两本不相干的书
create_overlay("card-01.jpg", [
    ('两本不相干的书', F52, GOLD, 540),
    ('', F36, (0,0,0,0), 620),
    ('生气通天论：讲道理', F36, WARM_WHITE, 720, "left"),
    ('  "别糟践自己"', F32, LIGHT_GREY, 775, "left"),
    ('', F28, (0,0,0,0), 840),
    ('金匮真言论：列表格', F36, WARM_WHITE, 900, "left"),
    ('  "东方青色入通于肝…"', F32, LIGHT_GREY, 955, "left"),
    ('一个温情，一个枯燥', F28, SOFT_GOLD, 1060),
    ('我一度以为编错了顺序', F28, SOFT_GOLD, 1100),
])

# card-02 — 上半场一句话：自伤
create_overlay("card-02.jpg", [
    ('上半场一句话', F36, LIGHT_GREY, 480),
    ('病，不是天降的', F52, GOLD, 560),
    ('是自伤', F52, WARM_WHITE, 640),
    ('', F28, (0,0,0,0), 720),
    ('「虽有贼邪，弗能害也」', F32, WHITE, 810),
    ('害得了你的，是', F32, LIGHT_GREY, 870),
    ('「卫气散解，此谓自伤」', F36, GOLD, 950),
    ('整篇没有一味药', F28, SOFT_GOLD, 1060),
    ('全是"别"', F28, SOFT_GOLD, 1105),
])

# card-03 — 下半场：给五脏画地图
create_overlay("card-03.jpg", [
    ('下半场', F36, LIGHT_GREY, 480),
    ('古人在给五脏画地图', F52, GOLD, 560),
    ('', F36, (0,0,0,0), 650),
    ('给五脏建坐标系', F40, WARM_WHITE, 750),
    ('', F28, (0,0,0,0), 820),
    ('方位 × 季节 × 脏 × 部位', F32, WHITE, 900),
    ('再加颜色、味道、声音、数字…', F32, WHITE, 960),
    ('一张越画越细的地图', F28, SOFT_GOLD, 1060),
])

# card-04 — 第一反应：完蛋要背
create_overlay("card-04.jpg", [
    ('我第一反应', F36, LIGHT_GREY, 480),
    ('完蛋，要背', F52, GOLD, 560),
    ('', F28, (0,0,0,0), 650),
    ('肝青心赤脾黄肺白肾黑', F32, WHITE, 750),
    ('肝酸心苦脾甘肺辛肾咸', F32, WHITE, 800),
    ('肝八心七脾五肺九肾六…', F32, WHITE, 850),
    ('', F28, (0,0,0,0), 920),
    ('又是一张要死记硬背的表？', F32, WARM_WHITE, 1000),
    ('记住"肝的数是八"', F28, LIGHT_GREY, 1070),
    ('对我有啥用？', F28, LIGHT_GREY, 1115),
])

# card-05 — 转折：它是一台定位仪
create_overlay("card-05.jpg", [
    ('转折', F36, LIGHT_GREY, 470),
    ('它是一台定位仪', F52, GOLD, 550),
    ('', F28, (0,0,0,0), 640),
    ('「病在肝，俞在颈项」', F36, WARM_WHITE, 730),
    ('', F28, (0,0,0,0), 800),
    ('颜色不对 → 定位到脏', F32, WHITE, 890, "left"),
    ('总想吃某个味 → 定位到脏', F32, WHITE, 945, "left"),
    ('老在某季节犯病 → 定位到脏', F32, WHITE, 1000, "left"),
    ('表越细，不是负担，是精度', F28, SOFT_GOLD, 1100),
])

# card-06 — 坐标 × 自伤 = 报警地图
create_overlay("card-06.jpg", [
    ('坐标 × 自伤', F52, GOLD, 520),
    ('= 一张报警地图', F48, WARM_WHITE, 600),
    ('', F28, (0,0,0,0), 690),
    ('上半场：病是自伤（为什么报警）', F32, WHITE, 790, "left"),
    ('下半场：坐标定位（在哪报警）', F32, WHITE, 850, "left"),
    ('', F28, (0,0,0,0), 930),
    ('只看上半场：知道坏了，不知坏在哪', F28, LIGHT_GREY, 1020),
    ('只看下半场：有表，不知指向什么', F28, LIGHT_GREY, 1070),
    ('缝起来，就是一张报警地图', F32, GOLD, 1160),
])

# card-07 — 阴中有阴：给地图调焦
create_overlay("card-07.jpg", [
    ('阴中有阴', F52, GOLD, 520),
    ('给地图调焦', F48, WARM_WHITE, 600),
    ('', F28, (0,0,0,0), 690),
    ('白天还能分上午（阳中之阳）', F32, WHITE, 790, "left"),
    ('和下午（阳中之阴）', F32, WHITE, 845, "left"),
    ('分了还能再分', F32, WHITE, 900, "left"),
    ('', F28, (0,0,0,0), 980),
    ('它在告诉你：这张地图', F32, LIGHT_GREY, 1070),
    ('分辨率可以无限放大', F32, GOLD, 1130),
    ('刻度越密，定位越准', F28, SOFT_GOLD, 1200),
])

# card-08 — 下期预告
create_overlay("card-08.jpg", [
    ('第二阶段教我一句话', F36, LIGHT_GREY, 470),
    ('先认账，再定位', F52, GOLD, 560),
    ('', F28, (0,0,0,0), 660),
    ('不舒服别急着往外甩锅', F32, WHITE, 760),
    ('先问是不是自伤', F32, WARM_WHITE, 820),
    ('再读身体给的信号', F32, WARM_WHITE, 880),
    ('', F28, (0,0,0,0), 970),
    ('下一阶段：阴阳应象大论', F36, GOLD, 1070),
    ('最硬的一篇', F32, LIGHT_GREY, 1145),
    ('我做好了被虐的准备', F28, SOFT_GOLD, 1220),
])

print("\n✅ All overlaid images saved to xhs-publish-pack/images/")
