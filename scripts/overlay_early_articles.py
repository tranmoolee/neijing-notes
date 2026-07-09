#!/usr/bin/env python3
"""
Overlay script for early neijing-notes articles (00-序 through 13-煎厥与薄厥)
Uses same flat-region detection as overlay_v7.py
"""
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path("/Users/tranmoo/neijing-notes")
SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"
GOLD_HEX = "#d4a04a"
WARM_HEX = "#f0e8d8"

def font_title(size):
    return ImageFont.truetype(SONGTI, size, encoding="unic", index=2)

def font_body(size):
    return ImageFont.truetype(SONGTI, size, encoding="unic", index=0)

def hex_rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def text_size(draw, font, text):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]

def find_best_text_region(gray_img, grid_rows=20, grid_cols=20, min_cells=2, margin=50):
    w, h = gray_img.size
    edges = gray_img.filter(ImageFilter.FIND_EDGES)
    inner_w = w - 2 * margin
    inner_h = h - 2 * margin
    inner_left = margin
    inner_top = margin
    cell_w = inner_w // grid_cols
    cell_h = inner_h // grid_rows

    grid = []
    brightnesses = []
    for row in range(grid_rows):
        grid_row = []
        for col in range(grid_cols):
            left = inner_left + col * cell_w
            upper = inner_top + row * cell_h
            right = min(left + cell_w, w - margin)
            lower = min(upper + cell_h, h - margin)
            crop_b = gray_img.crop((left, upper, right, lower))
            avg_b = sum(crop_b.getdata()) / len(list(crop_b.getdata()))
            crop_e = edges.crop((left, upper, right, lower))
            avg_e = sum(crop_e.getdata()) / len(list(crop_e.getdata()))
            is_good = avg_e < 25
            grid_row.append(1 if is_good else 0)
            brightnesses.append(avg_b)
        grid.append(grid_row)

    def largest_rect(grid):
        rows, cols = len(grid), len(grid[0])
        heights = [0] * cols
        best_area = 0
        best_rect = (0, 0, 1, 1)
        for r in range(rows):
            for c in range(cols):
                heights[c] = heights[c] + 1 if grid[r][c] else 0
            stack = []
            for c in range(cols + 1):
                hc = heights[c] if c < cols else 0
                while stack and heights[stack[-1]] > hc:
                    height = heights[stack[-1]]
                    stack.pop()
                    left_rect = stack[-1] + 1 if stack else 0
                    width = c - left_rect
                    area = width * height
                    if area > best_area:
                        best_area = area
                        best_rect = (left_rect, r - height + 1, width, height)
                stack.append(c)
        return best_rect, best_area

    (left, top, rw, rh), area = largest_rect(grid)
    if area < min_cells:
        inner_corners = [
            (margin, margin),
            (w - margin - cell_w * 2, margin),
            (margin, h - margin - cell_h * 2),
            (w - margin - cell_w * 2, h - margin - cell_h * 2),
        ]
        best_corner = min(inner_corners,
                          key=lambda p: sum(gray_img.crop((p[0], p[1], p[0] + cell_w, p[1] + cell_h)).getdata()) / (cell_w * cell_h))
        px, py = best_corner
        left, top = 0, 0
        rw, rh = 2, 2
    else:
        px = inner_left + left * cell_w
        py = inner_top + top * cell_h

    pw = rw * cell_w
    ph = rh * cell_h
    bright_samples = []
    for r in range(top, min(top + rh, grid_rows)):
        for c in range(left, min(left + rw, grid_cols)):
            idx = r * grid_cols + c
            if idx < len(brightnesses):
                bright_samples.append(brightnesses[idx])
    avg_region = sum(bright_samples) / len(bright_samples) if bright_samples else 128

    return {
        "x": px, "y": py, "w": pw, "h": ph,
        "cols": rw, "rows": rh, "area": area,
        "avg_bright": avg_region,
        "needs_dark_shadow": avg_region > 120,
    }

# Card text for early articles (from publish.md Part 2)
ALL_TEXT = {
    "00-序": {
        "cover.jpg": [("我爸扎了一辈子针", True), ("我现在才开始读《内经》", True), ("学渣读经·序章", False)],
        "card-01.jpg": [("我爸的\"家传\"，我没接", True), ("父亲做针灸几十年", False), ("家里中医是日常背景音", False), ("\"会一点，但不专门学\"", False)],
        "card-02.jpg": [("移民之后，事情变了", True), ("睡不好、吃不下、月经不调、长期疲劳", False), ("西医检查常常一切正常", False), ("但人就是不舒服", False)],
        "card-03.jpg": [("一个朋友的崩漏", True), ("血红蛋白掉到参考值的一半", False), ("几次扎下来，出血停了", False)],
        "card-04.jpg": [("这是我决定写这个系列的原因", True), ("3月9日 Hb:6.20", False), ("4月24日 Hb:7.80", False), ("红细胞、红细胞压积都在往上走", False)],
        "card-05.jpg": [("单一案例下不了结论", True), ("但我手上能接触到的这套东西", False), ("比我以为的更值得认真学", True)],
        "card-06.jpg": [("学习总要从一个头开始", True), ("《内经》不教扎针也不教开方", False), ("它讲的是怎么看人、看天、看病", False)],
        "card-07.jpg": [("关于这个系列", True), ("1. 我是学渣，不是老师", False), ("2. 不开方、不诊断、不远程看病", False), ("3. 进度很慢，十年读不完都正常", False)],
        "card-08.jpg": [("下一篇，从这一句开始", True), ("上古之人，其知道者", False), ("法于阴阳，和于术数……", False), ("\"法于阴阳\"四个字像鳗鱼，怎么都抓不住", False)],
    },
    "01-法于阴阳": {
        "cover.jpg": [("《内经》开头这一句", True), ("我读了三遍还没懂", True), ("学渣读经·第一篇", False)],
        "card-01.jpg": [("我的第一反应：这不就是鸡汤？", True), ("早睡早起、规律饮食、别瞎折腾", False), ("跟我妈在家庭群里转的养生文章一模一样", False)],
        "card-02.jpg": [("\"字都认识\"但\"合起来读不懂\"", True), ("法于阴阳，和于术数，食饮有节，起居有常", False), ("每个字都认识，合起来到底在说什么？", False)],
        "card-03.jpg": [("查了三家的注", True), ("王冰、马莳、张介宾", False), ("每个人解释都不一样", False)],
        "card-04.jpg": [("日落了你得睡觉", True), ("顺着太阳走就是法于阴阳", False), ("这么简单？还是我理解得太简单了？", False)],
        "card-05.jpg": [("留个坑", True), ("道是什么？——以后再说", False), ("术数 = ???", False)],
        "card-06.jpg": [("法于阴阳就是照着做", True), ("不是理解透彻了再动手", False), ("边做边懂，别卡在第一步", False)],
        "card-07.jpg": [("这一句困住我三遍", True), ("但困住是对的", False), ("没有大困惑就不会有真思考", False)],
        "card-08.jpg": [("下一篇：古人骂街", True), ("两千年没过期", False)],
    },
    "02-古人骂街": {
        "cover.jpg": [("古人骂街", True), ("两千年没过期", True), ("学渣读经·第二篇", False)],
        "card-01.jpg": [("这段话我一遍就读懂了", True), ("字都认识，逻辑都通", False), ("然后我意识到：这种轻松感本身是个陷阱", False)],
        "card-02.jpg": [("\"以酒为浆\"——我不喝酒，我过了？", True), ("如果把\"酒\"换成需要节制却成了日常必需的东西", False), ("我每天早上没有咖啡会头疼", False)],
        "card-03.jpg": [("\"以妄为常\"——我心虚了", True), ("西班牙夏天晚上十点天才黑", False), ("我已经把\"妄\"过成\"常\"了", False)],
        "card-04.jpg": [("精和真——有限的底牌", True), ("中医里的\"精\"和\"真\"，耗一分少一分", False), ("熬夜靠咖啡撑，这就是慢慢漏", False)],
        "card-05.jpg": [("现代人最稀缺的能力", True), ("不知持满——不知道自己快满了，不知道停", False), ("几乎没有工具帮我们识别：该停了", False)],
        "card-06.jpg": [("古人说的最让我停住的一句", True), ("务快其心，逆于生乐", False), ("你以为在追快乐，其实在往反方向跑", False)],
        "card-07.jpg": [("两种快乐，质地不同", True), ("刷短视频停不下来 vs 专注做完一件事", False), ("是两种质地完全不同的东西", False)],
        "card-08.jpg": [("下一篇：人生倒计时表", True), ("女七男八——你现在在哪一格？", False)],
    },
    "03-女七男八": {
        "cover.jpg": [("古人排好了时间表", True), ("我对进去之后沉默了", True), ("学渣读经·第三篇", False)],
        "card-01.jpg": [("一张人体倒计时表", True), ("女子七岁肾气盛……七七形坏而无子", False), ("男子八岁肾气实……八八齿发去", False)],
        "card-02.jpg": [("我对进去，发现自己在五七", True), ("阳明脉衰，面始焦，发始堕", False), ("三十五岁，女性身体开始走下坡", False)],
        "card-03.jpg": [("我很平静地接受了", True), ("不是因为豁达", False), ("而是这些年已经隐约感觉到了", False)],
        "card-04.jpg": [("男人的表更残酷", True), ("五八肾气衰，发堕齿槁", False), ("四十岁就开始掉头发了", False)],
        "card-05.jpg": [("这表准吗？", True), ("不是每格都精确到年", False), ("但节奏是对的——身体有时间感", False)],
        "card-06.jpg": [("知道倒计时在哪，比不知道好", True), ("不是制造焦虑", False), ("知道还有多少时间，才知道怎么花", False)],
        "card-07.jpg": [("养生不是往回走", True), ("不可能回到三七四八的顶峰", False), ("顺应当下的阶段，把剩下的用好", False)],
        "card-08.jpg": [("下一篇：《内经》里的四种人", True), ("我连最低档都没达到", False)],
    },
    "04-四种人": {
        "cover.jpg": [("《内经》里的四种人", True), ("我连最低档都没达到", True), ("学渣读经·第四篇", False)],
        "card-01.jpg": [("四个档位——真人、至人、圣人、贤人", True), ("像武侠小说的内功章节", False)],
        "card-02.jpg": [("真人——满级账号", True), ("提挈天地，把握阴阳", False), ("寿敝天地，无有终时", False)],
        "card-03.jpg": [("至人——接近通关", True), ("淳德全道，和于阴阳", False), ("游行天地之间，视听八达之外", False)],
        "card-04.jpg": [("圣人——还有点人间烟火", True), ("处天地之和，从八风之理", False), ("适嗜欲于世俗之间，无恚嗔之心", False)],
        "card-05.jpg": [("贤人——最低一档，我也够不着", True), ("法则天地，象似日月", False), ("亦益寿而有极时", False)],
        "card-06.jpg": [("我连贤人的门槛都没摸着", True), ("法则天地——我连节气都不太清楚", False), ("象似日月——我每天几点睡？", False)],
        "card-07.jpg": [("让我最难受的，不是没达到", True), ("而是\"最低档\"不是用来考的", False), ("是告诉你：人真的可以往这个方向走", False)],
        "card-08.jpg": [("下一篇：渴了才挖井，来得及吗？", True), ("治未病——圣人不治已病治未病", False)],
    },
    "09-圣人治未病": {
        "cover.jpg": [("渴了才挖井", True), ("来得及吗？", True), ("学渣读经·第九篇", False)],
        "card-01.jpg": [("四季讲完了", True), ("春发、夏长、秋收、冬藏", False), ("古人做了一个总结", False)],
        "card-02.jpg": [("春夏养阳，秋冬养阴", True), ("顺着四季养自己", False), ("逆之则灾害生，从之则苛疾不起", False)],
        "card-03.jpg": [("圣人不治已病治未病", True), ("病已成而后药之，不亦晚乎", False)],
        "card-04.jpg": [("治未病到底是什么意思？", True), ("不是预防医学那么简单", False), ("是在小问题变成病之前就把它调回去", False)],
        "card-05.jpg": [("我有一段时间持续低烧", True), ("查不出原因，最后自己好了", False), ("回头看——那就是身体在喊停", False)],
        "card-06.jpg": [("治未病三件事", True), ("1. 听懂身体的信号", False), ("2. 别把小不舒服拖成病", False), ("3. 日常作息本身就是药", False)],
        "card-07.jpg": [("早睡是治未病最便宜的药", True), ("没有什么养生方法比这个更基础", False), ("也最难做到", False)],
        "card-08.jpg": [("下一篇：风邪与百病", True), ("为什么偏偏是风排在百病之首？", False)],
    },
    "12-风邪百病": {
        "cover.jpg": [("为什么偏偏是\"风\"", True), ("排在百病之首？", True), ("学渣读经·第十二篇", False)],
        "card-01.jpg": [("风为百病之始", True), ("中医最著名的论断之一", False), ("为什么是风，不是寒不是热？", False)],
        "card-02.jpg": [("风是载体", True), ("寒、热、湿、燥都可能跟着风进来", False), ("风是第一道门缝", False)],
        "card-03.jpg": [("春伤于风，邪气留连", True), ("乃为洞泄；夏伤于暑，秋必痎疟", False), ("一个季节的债，下个季节还", False)],
        "card-04.jpg": [("风的特点是善行数变", True), ("来得快，位置不定", False), ("今天头痛明天关节痛后天皮肤痒", False)],
        "card-05.jpg": [("防风就是守住门", True), ("清静则肉腠闭拒", False), ("身体状态好，风进不来", False)],
        "card-06.jpg": [("现代人最容易被风击中的时候", True), ("熬夜后、大汗后、洗完澡没擦干", False), ("腠理开了，风就进去了", False)],
        "card-07.jpg": [("一条链：风入→传变→难治", True), ("故病久则传化，上下不并，良医弗为", False)],
        "card-08.jpg": [("下一篇：阳气崩溃的几种死法", True), ("煎厥与薄厥——古人写得像病历", False)],
    },
    "13-煎厥与薄厥": {
        "cover.jpg": [("阳气崩溃的几种死法", True), ("古人写得像病历", True), ("学渣读经·第十三篇", False)],
        "card-01.jpg": [("阳气像太阳", True), ("前两篇讲阳气应该怎样", False), ("这一篇开始讲搞砸了会怎样", False)],
        "card-02.jpg": [("煎厥——慢慢煮干", True), ("烦劳则张，精绝，辟积于夏", False), ("目盲不可以视，耳闭不可以听", False)],
        "card-03.jpg": [("薄厥——瞬间爆掉", True), ("大怒则形气绝，血菀于上", False), ("有伤于筋，纵，其若不容", False)],
        "card-04.jpg": [("两种死法的共同点", True), ("都是阳气出了问题", False), ("一个是慢性耗尽，一个是急性爆发", False)],
        "card-05.jpg": [("汗出偏沮，使人偏枯", True), ("一边出汗一边不出汗", False), ("身体已经开始失衡了", False)],
        "card-06.jpg": [("高梁之变，足生大丁", True), ("吃太好也会出事", False), ("营养过剩同样伤阳气", False)],
        "card-07.jpg": [("劳汗当风，寒薄为皶", True), ("运动出汗后被风吹", False), ("毛孔开了，寒进去了", False)],
        "card-08.jpg": [("阳气不是越多越好", True), ("是能收能放、该在的时候在", False), ("下一篇继续", False)],
    },
}

def main():
    base = BASE
    total = 0
    articles = ["00-序", "01-法于阴阳", "02-古人骂街", "03-女七男八", "04-四种人", "09-圣人治未病", "12-风邪百病", "13-煎厥与薄厥"]

    for article_name in articles:
        cards_text = ALL_TEXT.get(article_name)
        if not cards_text:
            print(f"SKIP {article_name}: no text defined")
            continue

        img_dir = base / article_name / "images"
        out_dir = base / article_name / "img-temp"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=== {article_name} ===")

        for card_name, lines in cards_text.items():
            src = img_dir / card_name
            if not src.exists():
                print(f"  SKIP: {card_name}")
                continue

            gray = Image.open(str(src)).convert("L")
            img = Image.open(str(src)).convert("RGBA")
            draw = ImageDraw.Draw(img)
            w, h = img.size

            region = find_best_text_region(gray)
            needs_shadow = region["needs_dark_shadow"]
            px, py = region["x"], region["y"]
            pw, ph = region["w"], region["h"]
            avg_bright = region["avg_bright"]

            print(f"  {card_name}: region=({px},{py},{pw}x{ph}) bright={avg_bright:.0f} shadow={'Y' if needs_shadow else 'N'}", end="")

            title_size = 72
            body_size = 44

            total_h = 0
            for text, is_title in lines:
                size = title_size if is_title else body_size
                fn = font_title(size) if is_title else font_body(size)
                tw, th = text_size(draw, fn, text)
                total_h += th + 12

            if total_h > ph:
                scale = min(0.8, ph / total_h)
                title_size = max(36, int(title_size * scale))
                body_size = max(22, int(body_size * scale))
                print(f" shrink->t{title_size}/b{body_size}", end="")

            print()

            # Calculate total text block dimensions
            line_info = []
            max_line_w = 0
            total_text_h = 0
            for text, is_title in lines:
                size = title_size if is_title else body_size
                fn = font_title(size) if is_title else font_body(size)
                tw, th = text_size(draw, fn, text)
                line_info.append((text, fn, tw, th, size, is_title))
                max_line_w = max(max_line_w, tw)
                total_text_h += th + 14

            # Center the whole text block within region
            pad_x = max(60, pw // 12)
            pad_y = max(40, (ph - total_text_h) // 2)

            # Horizontal center: ensure x + max_line_w doesn't exceed right edge
            x_center = px + max(pad_x, (pw - max_line_w) // 2)
            y = py + pad_y

            # Clamp: text must not overflow image
            max_img_x = w - 20
            max_img_y = h - 20

            for text, fn, tw, th, size, is_title in line_info:
                gold = hex_rgba(GOLD_HEX)
                warm = hex_rgba(WARM_HEX)
                color = gold if is_title else warm

                # Position: try to center, but don't overflow
                x = min(x_center, max_img_x - tw)

                # If line would overflow image bottom, skip remaining text
                if y + th > max_img_y:
                    print(f" CLIP: '{text}' at y={y}+{th}>{max_img_y}", end="")
                    break

                if needs_shadow:
                    for ox, oy in [(2, 2), (0, 2), (2, 0), (1, 1)]:
                        sx = min(x + ox, max_img_x - tw)
                        sy = min(y + oy, max_img_y - th)
                        draw.text((sx, sy), text, font=fn, fill=(0, 0, 0, 220))
                else:
                    sx = min(x + 2, max_img_x - tw)
                    sy = min(y + 2, max_img_y - th)
                    draw.text((sx, sy), text, font=fn, fill=(0, 0, 0, 150))

                draw.text((x, y), text, font=fn, fill=color)
                y += th + 14

            out_path = out_dir / card_name
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (60, 50, 40))
                bg.paste(img, mask=img.split()[3])
                img = bg
            img.save(str(out_path), quality=92)
            total += 1

        # Also list generated files
        print(f"  Generated: {len(list(out_dir.glob('*.jpg')))} images")

    print(f"\nDone: {total} images total")

if __name__ == "__main__":
    main()
