#!/usr/bin/env python3
"""Pillow overlay text onto shengqi-tongtian-lun summary images"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE = "/Users/tranmoo/neijing-notes/\u751f\u6c14\u901a\u5929\u8bba-\u5c0f\u7ed3/images"
OUT = "/Users/tranmoo/neijing-notes/\u751f\u6c14\u901a\u5929\u8bba-\u5c0f\u7ed3/xhs-publish-pack/images"

FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"

def get_font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_LIGHT, size)

def add_overlay(draw, box, color=(0, 0, 0, 180)):
    draw.rectangle(box, fill=color)

def draw_centered(draw, text, y, font, color=(255, 255, 255)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (1024 - tw) // 2
    draw.text((x, y), text, fill=color, font=font)

def draw_lines(draw, lines, start_y, font, color=(230, 230, 230), x=80, gap=10):
    y = start_y
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        y += font.size + gap

def run():
    os.makedirs(OUT, exist_ok=True)
    gold = (212, 175, 55)

    # ---- COVER ----
    img = Image.open(f"{BASE}/cover.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))

    f1 = get_font(44, True)
    f2 = get_font(60, True)
    f3 = get_font(28, True)
    f4 = get_font(20, False)

    draw_centered(d, '\u8bfb\u5b8c\u300a\u751f\u6c14\u901a\u5929\u8bba\u300b', 880, f1)
    draw_centered(d, '\u5b83\u901a\u7bc7\u5728\u8bb2\u4e24\u4e2a\u5b57', 940, f1)
    draw_centered(d, '\u81ea\u4f24', 1060, f2, gold)
    draw_centered(d, '\u4f60\u4ee5\u4e3a\u5b83\u5728\u8bb2\u201c\u5929\u4eba\u5408\u4e00\u201d', 1200, f3)
    draw_centered(d, '\u5176\u5b9e\u901a\u7bc7\u5728\u8bb2\u2014\u2014\u81ea\u4f24', 1245, f3)
    draw_centered(d, '\u5b66\u6e23\u8bfb\u5185\u7ecf \u00b7 \u751f\u6c14\u901a\u5929\u8bba\u5c0f\u7ed3', 1350, f4, (200, 200, 200))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/cover.jpg", quality=95)
    print("\u2705 cover.jpg")

    # ---- CARD 1 ----
    img = Image.open(f"{BASE}/card-01.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u6211\u4ee5\u4e3a\u8bb2\u201c\u5929\u548c\u4eba\u201d', 870, get_font(38, True))
    draw_centered(d, '\u5176\u5b9e\u8bb2\u201c\u81ea\u4f24\u201d', 925, get_font(38, True))
    draw_lines(d, [
        '\u300c\u751f\u6c14\u901a\u5929\u300d\uff0c\u6211\u4e00\u76f4\u4ee5\u4e3a\u8bb2\u7684\u662f',
        '\u5929\u600e\u4e48\u5f71\u54cd\u4eba\u3002',
        '',
        '\u4f46\u539f\u6587\u53cd\u590d\u51fa\u73b0\u7684\u662f\u53e6\u5916\u4e24\u4e2a\u5b57\uff1a',
        '\u300c\u536b\u6c14\u6563\u89e3\uff0c\u6b64\u8c13\u81ea\u4f24\u3002\u300d',
        '',
        '\u5b83\u4ece\u5934\u5230\u5c3e\u5728\u8bb2\uff1a',
        '\u4f60\u662f\u600e\u4e48\u628a\u81ea\u5df1\u641e\u574f\u7684\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-01.jpg", quality=95)
    print("\u2705 card-01.jpg")

    # ---- CARD 2 ----
    img = Image.open(f"{BASE}/card-02.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u9633\u6c14\uff0c\u662f\u4f60\u8fd9\u53f0\u673a\u5668', 870, get_font(38, True))
    draw_centered(d, '\u7684\u7535\u6e90', 925, get_font(38, True))
    draw_lines(d, [
        '\u300c\u9633\u6c14\u8005\uff0c\u82e5\u5929\u4e0e\u65e5\u3002\u300d',
        '',
        '\u4e0d\u662f\u9526\u4e0a\u6dfb\u82b1\u7684\u6696\u6c14\uff0c',
        '\u662f\u5e95\u5c42\u7535\u6e90\u3002',
        '\u592a\u9633\u6ca1\u4e86\u4e0d\u662f\u67d0\u4e2a\u96f6\u4ef6\u574f\uff0c',
        '\u662f\u6574\u673a\u5173\u673a\u3002',
        '',
        '\u800c\u5b83\u7684\u6d3b\u513f\u662f\u201c\u536b\u5916\u201d\u2014\u2014',
        '\u50cf\u8fb9\u9632\u519b\u5b88\u5728\u4f53\u8868\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-02.jpg", quality=95)
    print("\u2705 card-02.jpg")

    # ---- CARD 3 ----
    img = Image.open(f"{BASE}/card-03.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u9634\u5e73\u9633\u79d8\u2014\u2014', 870, get_font(38, True))
    draw_centered(d, '\u4e0d\u662f\u4e94\u4e94\u5f00', 925, get_font(38, True))
    draw_lines(d, [
        '\u6211\u4e00\u76f4\u4ee5\u4e3a\u7406\u60f3\u662f\u9634\u9633\u4e94\u4e94\u5f00\u3002',
        '\u539f\u6587\u8bf4\uff1a\u300c\u9633\u5bc6\u4e43\u56fa\u3002\u300d',
        '',
        '\u5173\u952e\u4e0d\u5728\u5e73\u8861\uff0c',
        '\u5728\u9633\u6c14\u5bc6\u4e0d\u5bc6\u3002',
        '',
        '\u7535\u8981\u6709\uff0c\u8fd8\u5f97\u4e0d\u6f0f\u3002',
        '\u65fa\u800c\u4e0d\u5bc6\uff0c\u662f\u53e6\u4e00\u79cd\u5d29\u6e83\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-03.jpg", quality=95)
    print("\u2705 card-03.jpg")

    # ---- CARD 4 ----
    img = Image.open(f"{BASE}/card-04.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u98ce\u4e3a\u767e\u75c5\u4e4b\u59cb', 870, get_font(36, True))
    draw_centered(d, '\u53ef\u95e8\u662f\u4f60\u81ea\u5df1\u5f00\u7684', 925, get_font(36, True))
    draw_lines(d, [
        '\u300c\u98ce\u8005\uff0c\u767e\u75c5\u4e4b\u59cb\u4e5f\u3002\u300d',
        '\u98ce\u4e0d\u662f\u6700\u6bd2\u7684\uff0c\u662f\u201c\u5f00\u95e8\u7684\u201d\u3002',
        '',
        '\u4f46\u300c\u6e05\u9759\u5219\u8089\u805a\u95ed\u62d2\u300d\u2014\u2014',
        '\u4f60\u5b89\u9759\uff0c\u95e8\u5c31\u5173\u7740\uff0c',
        '\u518d\u5927\u7684\u98ce\u4e5f\u8fdb\u4e0d\u6765\u3002',
        '',
        '\u90a3\u6247\u95e8\uff0c\u4f60\u81ea\u5df1\u5f00\uff0c',
        '\u4e5f\u4f60\u81ea\u5df1\u5173\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-04.jpg", quality=95)
    print("\u2705 card-04.jpg")

    # ---- CARD 5 ----
    img = Image.open(f"{BASE}/card-05.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u714e\u5384\u4e0e\u8584\u5384', 870, get_font(38, True))
    draw_centered(d, '\u4e0b\u624b\u7684\u90fd\u662f\u4f60', 925, get_font(38, True))
    draw_lines(d, [
        '\u714e\u5384\u2014\u2014\u70e6\u52b3\u628a\u9634\u7cbe',
        '\u50cf\u5c0f\u706b\u6162\u6162\u714e\u5e72\u3002',
        '',
        '\u8584\u5384\u2014\u2014\u5927\u6012\u8ba9\u8840',
        '\u4e00\u4e0b\u51b2\u4e0a\u5934\u3002',
        '',
        '\u4e00\u4e2a\u6162\u706b\uff0c\u4e00\u4e2a\u731b\u706b\u3002',
        '\u4f46\u70b9\u706b\u7684\uff0c\u90fd\u662f\u4f60\u81ea\u5df1\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-05.jpg", quality=95)
    print("\u2705 card-05.jpg")

    # ---- CARD 6 ----
    img = Image.open(f"{BASE}/card-06.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u517b\u4f60\u7684\u548c\u4f24\u4f60\u7684', 870, get_font(36, True))
    draw_centered(d, '\u662f\u540c\u4e00\u4e2a\u4e1c\u897f', 925, get_font(36, True))
    draw_lines(d, [
        '\u300c\u9634\u4e4b\u6240\u751f\uff0c\u672c\u5728\u4e94\u5473\uff1b',
        '  \u9634\u4e4b\u4e94\u5bab\uff0c\u4f24\u5728\u4e94\u5473\u3002\u300d',
        '',
        '\u517b\u4f60\u7684\u662f\u9178\u82e6\u7518\u8f9b\u54b8\uff0c',
        '\u4f24\u4f60\u7684\u4e5f\u662f\u3002',
        '\u533a\u522b\u53ea\u5728\u91cf\u3002',
        '',
        '\u6574\u7bc7\u6700\u540e\u843d\u5728\u56db\u4e2a\u5b57\uff1a',
        '\u8c28\u548c\u4e94\u5473\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-06.jpg", quality=95)
    print("\u2705 card-06.jpg")

    # ---- CARD 7 ----
    img = Image.open(f"{BASE}/card-07.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u5b83\u7ed9\u7684\u4e0d\u662f\u836f\u65b9', 870, get_font(36, True))
    draw_centered(d, '\u662f\u201c\u522b\u62c6\u81ea\u5df1\u201d\u6e05\u5355', 925, get_font(36, True))
    draw_lines(d, [
        '\u300c\u867d\u6709\u8d3c\u90aa\uff0c\u5f17\u80fd\u5bb3\u4e5f\u3002\u300d',
        '\u90aa\u4e00\u76f4\u90fd\u5728\uff0c\u5bb3\u5f97\u4e86\u4f60\u7684',
        '\u53ea\u6709\u201c\u81ea\u4f24\u201d\u3002',
        '',
        '\u6574\u7bc7\u6ca1\u6709\u4e00\u5473\u836f\u2014\u2014',
        '\u6ca1\u6559\u4f60\u5403\u4ec0\u4e48\uff0c\u53ea\u6559\u4f60\u201c\u522b\u201d\uff1a',
        '\u522b\u4e0d\u6e05\u9759\u3001\u522b\u70e6\u52b3\u5927\u6012\u3001',
        '\u522b\u8fc7\u91cf\u3002',
    ], 1060, get_font(26, False))
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-07.jpg", quality=95)
    print("\u2705 card-07.jpg")

    # ---- CARD 8 ----
    img = Image.open(f"{BASE}/card-08.jpg").convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    add_overlay(d, [0, 780, 1024, 1536], (0, 0, 0, 210))
    draw_centered(d, '\u5b83\u8bb2\u7684\u662f\u51cf\u6cd5', 870, get_font(38, True))
    draw_centered(d, '\u4e0d\u662f\u52a0\u6cd5', 925, get_font(38, True))
    draw_lines(d, [
        '\u300a\u5185\u7ecf\u300b\u51e0\u4e4e\u4e0d\u544a\u8bc9\u4f60',
        '\u8865\u4ec0\u4e48\u3001\u7ec3\u4ec0\u4e48\u3002',
        '',
        '\u5b83\u4e00\u76f4\u8bf4\uff1a\u522b\u62c6\u4ec0\u4e48\u3001',
        '\u522b\u8017\u4ec0\u4e48\u3002',
        '',
        '\u201c\u957f\u6709\u5929\u547d\u201d\u2014\u2014\u4e0d\u591a\u7ed9\u4f60\u5bff\u547d\uff0c',
        '\u53ea\u8bf4\uff1a\u4f60\u672c\u6765\u80fd\u6d3b\u7684\uff0c',
        '\u522b\u81ea\u5df1\u6298\u635f\u6389\u3002',
    ], 1060, get_font(26, False))
    draw_centered(d, '\u6311\u4e00\u4ef6\u201c\u81ea\u4f24\u201d\u7684\u4e8b\uff0c\u505c\u4e03\u5929\u3002', 1400, get_font(30, True), gold)
    Image.alpha_composite(img, ov).convert("RGB").save(f"{OUT}/card-08.jpg", quality=95)
    print("\u2705 card-08.jpg")

    print("\n\U0001f389 \u5168\u90e89\u5f20\u56fe\u7247\u6587\u5b57\u53e0\u52a0\u5b8c\u6210\uff01")

if __name__ == "__main__":
    run()
