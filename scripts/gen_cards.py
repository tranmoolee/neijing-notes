#!/usr/bin/env python3
"""
[DEPRECATED] Pillow-based card generation for neijing-notes.

This script generated card-01 (坐标表) and card-03 (疼痛定位指南) using Pillow
with Chinese fonts. As of 2026-05-29, ALL cards including card-01 and card-03
are generated via gpt-image-2 (OpenAI Codex) for higher visual quality.

USE GPT-IMAGE-2 INSTEAD:
  Use the image_generate tool with these prompts:

  --- card-01 坐标表 prompt ---
  A traditional Chinese medical coordinate table card in vertical 3:4 format.
  Clean warm beige paper background with subtle texture and dark ink borders.
  At the top, the title "一张五脏坐标表" in elegant Chinese calligraphy style
  with decorative red seal stamp "学渣读经". Below, a beautifully designed table
  with 5 columns and 6 rows. Column headers: 方位, 风, 季节, 对应脏, 俞（反应区）.
  Row data: 东/东风/春/肝/颈项, 南/南风/夏/心/胸胁, 西/西风/秋/肺/肩背,
  北/北风/冬/肾/腰股, 中/—/长夏/脾/脊. The organ characters (肝心脾肺肾)
  highlighted in cinnabar red. The direction characters (东南西北中) in dark brown.
  Table has alternating row shading. At the bottom, a small text:
  "不是器官列表，是多维地图". Scholarly Chinese medicine chart aesthetic,
  clean infographic style, all text in Chinese.
  aspect_ratio: portrait

  --- card-03 疼痛指南 prompt ---
  Vertical Chinese medical infographic card. Warm beige paper background with
  subtle texture. Title in Chinese calligraphy style at top: "疼痛定位指南"
  with red seal "学渣读经". In the center, a simple stylized human body outline
  drawing (front view, simple lines) with five bright red dot markers. Thin red
  dashed lines connect each dot to a callout label showing the body part name
  and its corresponding organ in Chinese: 颈项（肝）, 胸胁（心）, 肩背（肺）,
  腰股（肾）, 脊（脾）. At bottom, highlighted text:
  "哪里不舒服 → 提示哪个脏有状况". Clean educational Chinese medicine chart,
  ink drawing style, scholarly atmosphere.
  aspect_ratio: portrait

This script is kept for backward compatibility / emergency fallback only.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

OUTPUT = "/Users/tranmoo/projects/neijing-notes/15-东风生于春/images"
W, H = 1080, 1440  # 3:4 portrait

# Font paths
FONT_SONG = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_FANG = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/1821952872c81043711aab6910052b65da8edf2c.asset/AssetData/STFANGSO.ttf"
FONT_KAI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/b86e58f38fd21e9782e70a104676f1655e72ebab.asset/AssetData/Yuanti.ttc"
FONT_HEI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/f7f6b250e97c182e68ac53a2b359ec44548878b9.asset/AssetData/Lantinghei.ttc"

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# Warm traditional palette
PAPER = hex_to_rgb('#F5F0E8')
INK = hex_to_rgb('#3D2B1F')
CINNABAR = hex_to_rgb('#CC3333')
SEAL = hex_to_rgb('#C73E3A')
ACCENT = hex_to_rgb('#8B4513')

def make_paper_bg():
    """Create a warm paper-textured background."""
    bg = Image.new('RGB', (W, H), PAPER)
    draw = ImageDraw.Draw(bg)
    # Subtle grain
    for _ in range(2000):
        x, y = __import__('random').randint(0, W-1), __import__('random').randint(0, H-1)
        shade = __import__('random').randint(-8, 8)
        c = tuple(max(0, min(255, v + shade)) for v in PAPER)
        bg.putpixel((x, y), c)
    # Dark border
    for i in range(8):
        draw.rectangle([i, i, W-1-i, H-1-i], outline=(70, 55, 40) if i < 4 else None, width=1)
    return bg, draw

def draw_title(draw, text, y, font_size=52, color=INK):
    font = ImageFont.truetype(FONT_HEI, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=color)

def draw_seal(draw, x, y, size=40):
    font = ImageFont.truetype(FONT_FANG, size)
    text = "学渣读经"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px, py = x - tw//2, y
    draw.rectangle([px-10, py-5, px+tw+10, py+th+10], outline=CINNABAR, width=2)
    draw.text((px, py), text, font=font, fill=CINNABAR)

def make_card_01():
    """Card 1: 五脏坐标表"""
    bg, draw = make_paper_bg()
    
    # Title
    draw_title(draw, "— 五脏坐标表 —", 60, 56, ACCENT)
    
    # Decorative line
    for i in range(5):
        x1, x2 = 200 + i * 15, 880 - i * 15
        draw.line([(x1, 120), (x2, 120)], fill=CINNABAR, width=1)
    
    # Table data
    rows = [
        ("东", "东风", "春", "肝", "颈项"),
        ("南", "南风", "夏", "心", "胸胁"),
        ("西", "西风", "秋", "肺", "肩背"),
        ("北", "北风", "冬", "肾", "腰股"),
        ("中", "—", "长夏", "脾", "脊"),
    ]
    headers = ["方位", "风", "季节", "对应脏", "俞（反应区）"]
    
    # Table layout
    left_margin = 60
    top = 170
    col_widths = [100, 120, 120, 130, 240]
    row_h = 85
    total_w = sum(col_widths)
    table_left = (W - total_w) // 2
    
    font_h = ImageFont.truetype(FONT_HEI, 32)
    font_b = ImageFont.truetype(FONT_KAI, 30)
    
    # Header row
    hx = table_left
    for i, h in enumerate(headers):
        draw.rectangle([hx, top, hx + col_widths[i], top + row_h], 
                       fill=(230, 215, 190), outline=INK, width=2)
        bbox = draw.textbbox((0, 0), h, font=font_h)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((hx + (col_widths[i] - tw) // 2, top + (row_h - th) // 2 - 5), 
                  h, font=font_h, fill=CINNABAR)
        hx += col_widths[i]
    
    # Data rows
    for ri, (dirr, wind, season, organ, point) in enumerate(rows):
        ry = top + row_h + ri * row_h
        rx = table_left
        bg_color = (245, 238, 228) if ri % 2 == 0 else (250, 245, 238)
        
        vals = [dirr, wind, season, organ, point]
        for ci, val in enumerate(vals):
            f = font_b if ci != 3 else ImageFont.truetype(FONT_HEI, 32)
            fc = CINNABAR if ci == 3 else INK
            draw.rectangle([rx, ry, rx + col_widths[ci], ry + row_h], 
                          fill=bg_color, outline=INK, width=1)
            # Bold for direction and organ
            if ci == 0 or ci == 3:
                f = ImageFont.truetype(FONT_HEI, 34)
                fc = CINNABAR if ci == 3 else ACCENT
            bbox = draw.textbbox((0, 0), val, font=f)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((rx + (col_widths[ci] - tw) // 2, ry + (row_h - th) // 2 - 5),
                     val, font=f, fill=fc)
            rx += col_widths[ci]
    
    # Seal
    draw_seal(draw, W - 120, H - 100, 36)
    
    # Bottom text
    font_s = ImageFont.truetype(FONT_KAI, 24)
    bottom = "每个脏配方位·季节·风·反应部位 → 多维地图"
    bbox = draw.textbbox((0, 0), bottom, font=font_s)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 160), bottom, font=font_s, fill=(100, 80, 60))
    
    bg.save(f"{OUTPUT}/card-01.jpg", quality=92)
    print(f"✅ card-01.jpg saved ({os.path.getsize(f'{OUTPUT}/card-01.jpg')//1024}KB)")

def make_card_03():
    """Card 3: 疼痛定位指南 - 人体痛点图"""
    bg, draw = make_paper_bg()
    
    draw_title(draw, "— 疼痛定位指南 —", 60, 56, ACCENT)
    for i in range(5):
        x1, x2 = 200 + i * 15, 880 - i * 15
        draw.line([(x1, 120), (x2, 120)], fill=CINNABAR, width=1)
    
    # Draw a stylized human body outline
    cx = W // 2
    head_center = (cx, 220)
    head_r = 55
    
    # Head
    draw.ellipse([head_center[0] - head_r, head_center[1] - head_r,
                  head_center[0] + head_r, head_center[1] + head_r], 
                 outline=INK, width=3, fill=(238, 230, 218))
    
    # Neck
    neck_top = head_center[1] + head_r
    neck_bottom = neck_top + 50
    neck_w = 40
    draw.polygon([(cx - neck_w, neck_top), (cx + neck_w, neck_top),
                  (cx + neck_w - 15, neck_bottom), (cx - neck_w + 15, neck_bottom)],
                 outline=INK, width=3, fill=(238, 230, 218))
    
    # Shoulders
    shoulder_y = neck_bottom
    draw.line([(cx - 180, shoulder_y + 30), (cx + 180, shoulder_y + 30)], fill=INK, width=3)
    
    # Torso
    body_left, body_right = cx - 120, cx + 120
    body_top = neck_bottom - 5
    body_bottom = body_top + 350
    draw.polygon([
        (body_left, body_top), (body_right, body_top),
        (body_right - 30, body_bottom), (body_left + 30, body_bottom)
    ], outline=INK, width=3, fill=(238, 230, 218))
    
    # Waist line
    waist_y = body_top + 200
    draw.line([(body_left + 10, waist_y), (body_right - 10, waist_y)], fill=(180, 160, 140), width=2)
    
    # Legs
    leg_top = body_bottom
    leg_w = 50
    draw.line([(cx - leg_w, leg_top), (cx - leg_w - 30, H - 160)], fill=INK, width=3)
    draw.line([(cx + leg_w, leg_top), (cx + leg_w + 30, H - 160)], fill=INK, width=3)
    
    # Arms
    arm_top_y = shoulder_y + 20
    draw.line([(body_left - 10, arm_top_y), (body_left - 80, arm_top_y + 180)], fill=INK, width=3)
    draw.line([(body_right + 10, arm_top_y), (body_right + 80, arm_top_y + 180)], fill=INK, width=3)
    
    # Pain points with labels
    points = [
        ("颈项", cx, neck_top + 15, "肝"),       # Neck
        ("胸胁", cx + body_right//2 - 60, body_top + 70, "心"),  # Chest/side
        ("肩背", body_right - 40, shoulder_y + 10, "肺"),  # Shoulder back
        ("腰股", cx + 50, waist_y + 40, "肾"),    # Lower back
        ("脊", cx, body_top + 120, "脾"),         # Spine
    ]
    
    font_p = ImageFont.truetype(FONT_FANG, 28)
    font_o = ImageFont.truetype(FONT_HEI, 32)
    
    for label, px, py, organ in points:
        # Marker dot
        dot_r = 10
        draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], 
                    fill=CINNABAR, outline=(180, 40, 40), width=2)
        
        # Glow
        for g in range(4):
            draw.ellipse([px - dot_r - g*2, py - dot_r - g*2, 
                         px + dot_r + g*2, py + dot_r + g*2], 
                        outline=(200, 80, 80, 80) if hasattr(Image, 'RGBA') else None, 
                        width=1)
        
        # Label position (offset to avoid overlap)
        if label == "颈项":
            lx, ly = px - 140, py - 30
        elif label == "胸胁":
            lx, ly = px + 30, py - 15
        elif label == "肩背":
            lx, ly = px - 160, py + 5
        elif label == "腰股":
            lx, ly = px + 30, py - 10
        else:  # 脊
            lx, ly = px - 140, py + 5
        
        # Background for label
        bbox = draw.textbbox((0, 0), f"{label}（{organ}）", font=font_p)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rectangle([lx-8, ly-5, lx+tw+8, ly+th+8], fill=(255, 245, 235), outline=CINNABAR, width=1)
        
        draw.text((lx, ly), f"{label}（{organ}）", font=font_p, fill=INK)
        
        # Connection line from dot to label
        draw.line([(px, py), (lx, ly+th//2)], fill=CINNABAR, width=2)
    
    # Bottom explanation
    font_s = ImageFont.truetype(FONT_KAI, 24)
    text = "哪里不舒服 → 提示哪个脏有状况"
    bbox = draw.textbbox((0, 0), text, font=font_s)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 200), text, font=font_s, fill=(100, 80, 60))
    
    draw_seal(draw, W - 120, H - 100, 36)
    
    bg.save(f"{OUTPUT}/card-03.jpg", quality=92)
    print(f"✅ card-03.jpg saved ({os.path.getsize(f'{OUTPUT}/card-03.jpg')//1024}KB)")

if __name__ == "__main__":
    print("⚠️  DEPRECATED: All cards should now use gpt-image-2, not Pillow.")
    print("    See the docstring at the top of this file for the correct prompts.")
    print("    Running in fallback mode...")
    make_card_01()
    make_card_03()
