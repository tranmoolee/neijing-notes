#!/usr/bin/env python3
# 从已增强的 article.md 生成 wechat.md（=正文+footer）与 ghost.md（=frontmatter+正文(去H1)+footer）
# ghost 正文与 wechat 一致（Ghost 跟随公众号）。用法：python3 .gen-platform.py [folder ...]
import sys, os, re

FOOTER = (
    "\n\n——\n"
    "本文系「学渣读内经」个人学习笔记，由作者撰写、AI 辅助整理与排版；\n"
    "仅为学习记录，不构成任何医疗或就医建议，身体不适请咨询专业医生。\n"
)

BASE_TAGS = "学渣读内经, 黄帝内经, 中医学习"

# folder -> (slug, extra_tags, excerpt)
DATA = {
 "18-阴阳者天地之道": ("neijing-18-yinyang-tiandao", "阴阳应象大论, 阴阳",
   "阴阳不是玄学，是万物运行的底层操作系统；这一篇教我把看不见的规律，落到看得见的现象上。"),
 "19-清阳浊阴": ("neijing-19-qingyang-zhuoyin", "阴阳应象大论, 升降",
   "清的往上、浊的往下，身体里有一套升降交通规则；走反了，就出问题。"),
 "20-天气通于肺": ("neijing-20-tianqi-tongfei", "阴阳应象大论, 五脏",
   "天地的六种气，对应通向身体的六个口；人不是封闭的，一直和天地在换气。"),
 "21-味归形气归精": ("neijing-21-wei-gui-xing", "阴阳应象大论, 气味",
   "吃进去的味、吸进来的气，在身体里有方向也有厚薄；阴阳还分剂量。"),
 "22-壮火少火": ("neijing-22-zhuanghuo-shaohuo", "阴阳应象大论, 壮火少火",
   "同样是火，小火养你，旺火烧你——咖啡和熬夜那种'猛火'，越提神越掏空你。"),
 "23-东方生风": ("neijing-23-dongfang-shengfeng", "阴阳应象大论, 五行",
   "五方五气五色五味五脏串成一张大对应表——它不是用来背的，是一本'翻译词典'。"),
 "24-善诊者察色按脉": ("neijing-24-shanzhen-chase", "阴阳应象大论, 中医诊断",
   "读了七篇理论，最后三个字把一切拉回地面：先别阴阳。"),
 "25-三阴三阳": ("neijing-25-sanyin-sanyang", "阴阳离合论, 三阴三阳, 开阖枢",
   "太阳少阳阳明这六个玄乎的名字，其实在讲一扇门怎么开关——最关键的是那个不起眼的合页。"),
 "26-脉之阴阳": ("neijing-26-mai-yinyang", "阴阳别论, 脉诊, 胃气",
   "摸脉不只看哪儿病了，还能读出'还剩多少时间'；脉里那股从容劲儿，叫胃气。"),
 "27-十二官": ("neijing-27-shier-guan", "灵兰秘典论, 脏腑",
   "身体是一个朝廷，而皇帝（心）的KPI不是勤政，是别糊涂——主明则下安。"),
 "28-藏象何如": ("neijing-28-zangxiang", "六节藏象论, 藏象",
   "内脏藏在身体里，却一直把状态挂在外面——脸色、头发、指甲，都是内脏的仪表盘。"),
 "29-五脏生成": ("neijing-29-wuzang-shengcheng", "五脏生成, 睡眠, 五行相克",
   "人卧血归于肝——睡觉原来是让血'回仓库'的工序；而五脏，是一张互相管着的网。"),
 "30-奇恒之腑": ("neijing-30-qiheng-fu", "五脏别论, 脏腑",
   "脏和腑的区别居然只有一条：存不存东西。脏是仓库，腑是管道。"),
 "31-经脉别论": ("neijing-31-jingmai-bielun", "经脉别论, 气血",
   "一口饭和一口水，进身体后走的是两条路；而生病，起于'过用'。"),
 "32-太阴阳明论": ("neijing-32-taiyin-yangming", "太阴阳明论, 脾胃, 后天之本",
   "那个不挂名、没有自己季节、却谁都离不开的脏——脾。手脚有没有劲，看它。"),
 "33-血气形志": ("neijing-33-xueqi-xingzhi", "血气形志, 情绪与健康",
   "古人早就把'身体累'和'心里累'分开算了；最戳现代人的一格叫——形乐志苦。"),
 "34-骨空论": ("neijing-34-gukong-lun", "骨空论, 经络, 任督二脉",
   "身体前后各有一条主干道——任脉和督脉，谁也不归某个脏管，统调全局。"),
 "P3-七篇回头看": ("neijing-p3-stage3-review", "第三阶段回顾, 阴阳应象大论",
   "号称《内经》理论密度最高、最硬的一篇，读完发现它其实最接地气——因为'应象'就是把玄的翻译成具体的。"),
 "P4-六篇回头看": ("neijing-p4-stage4-review", "第四阶段回顾, 脏腑理论",
   "我以为脏腑理论是在拆零件，其实它从头到尾在讲关系——身体是一张关系网，不是一张零件清单。"),
 "P5-四篇回头看": ("neijing-p5-stage5-review", "第五阶段回顾, 经络与气血",
   "一听'气血'我以为讲的是'你有多少'，其实第五阶段讲的全是'送不送得到'——健康看流通，不看库存。"),
 "35-脉要精微": ("neijing-35-maiyao-jingwei", "脉要精微论, 脉诊, 中医诊断",
   "古人看病最准的时刻，是你刚睡醒、还没吃没动的那会儿——那是身体没化妆的基线；连姿态都会出卖五脏。"),
 "36-平人气象": ("neijing-36-pingren-qixiang", "平人气象论, 平人, 胃气",
   "量你健不健康的尺子，原来是一个普通人的呼吸——健康的标志不是强、不是猛，是一个'平'字。"),
 "37-病机十九条": ("neijing-37-bingji-19", "至真要大论, 病机十九条, 中医诊断",
   "一份两千年前的'症状→根源'查找表，但最关键的是末尾那句——别对号入座，有者求之，无者求之。"),
 "38-热论": ("neijing-38-relun", "热论, 伤寒, 食复",
   "发烧原来有剧本——按天从表到里推进；最实用的一条是'食复'：刚退烧那顿千万别嘴馋。"),
 "39-举痛论": ("neijing-39-jutonglun", "举痛论, 不通则痛, 情绪与健康",
   "痛，多半不是哪里坏了，是哪里堵了；而堵的源头，常常是情绪——百病生于气。"),
 "P6-五篇回头看": ("neijing-p6-stage6-review", "第六阶段回顾, 诊法与病机, 主线收官",
   "主线四十篇收官。读完才发现，中医的'诊断'从头到尾在做一件事——从表象反查那个看不见的源头。"),
 "40-九针十二原": ("neijing-40-jiuzhen-shieryuan", "灵枢, 九针十二原, 针灸入门",
   "进阶阶段开《灵枢》。九针不是九根针，是一套工具箱——而'针经'开篇先教的不是怎么扎，是'粗守形，上守神'。"),
}

def gen(folder):
    art = os.path.join(folder, "article.md")
    with open(art, encoding="utf-8") as f:
        body = f.read().rstrip("\n")
    # title = first H1
    m = re.search(r"^#\s+(.+)$", body, re.M)
    title = m.group(1).strip()
    slug, extra, excerpt = DATA[folder]
    tags = BASE_TAGS + ", " + extra
    # wechat = full article + footer
    wechat = body + FOOTER
    # ghost body = article without the first H1 line
    lines = body.split("\n")
    out = []
    dropped = False
    for ln in lines:
        if not dropped and re.match(r"^#\s+", ln):
            dropped = True
            continue
        out.append(ln)
    ghost_body = "\n".join(out).lstrip("\n")
    fm = (
        "---\n"
        f"title: {title}\n"
        f"slug: {slug}\n"
        "status: draft\n"
        f"tags: {tags}\n"
        f"excerpt: {excerpt}\n"
        "feature_image: images/cover.jpg\n"
        "---\n\n"
    )
    ghost = fm + ghost_body + FOOTER
    with open(os.path.join(folder, "wechat.md"), "w", encoding="utf-8") as f:
        f.write(wechat)
    with open(os.path.join(folder, "ghost.md"), "w", encoding="utf-8") as f:
        f.write(ghost)
    print(f"  ✓ {folder}  (title: {title[:24]}…)  wechat+ghost")

if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(DATA.keys())
    for t in targets:
        gen(t)
