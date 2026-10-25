#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""江雪 · 字群成体版（v3）

手法要点（学自参考图）：
1. 剪影由字群外缘决定——山、船都是几十上百个字堆出来的"体"
2. 密度即体积：靠峰顶密、山脚疏；船心密、船舷疏
3. 空气透视：远山用小字淡色，山脚用更小更淡的雾字向外消融
4. 全诗沿一条主斜线推进，主字只留给每句的关键词
5. 一色一义：全图只有"寒江"染蓝

输出：v3-2-jiangxue.svg
"""
import math
import random

random.seed(11)
W, H = 900, 1200
INK = "#1a1a1a"
FAR = "#98a3ab"
WATER = "#7d93a6"
DEEP = "#3f5a70"
SNOW = "#bcc7d1"

out = []


def T(x, y, s, txt, fill=INK, op=1.0, rot=0.0):
    tr = ' transform="rotate(%.0f %.0f %.0f)"' % (rot, x, y) if rot else ""
    out.append('<text x="%.0f" y="%.0f" font-size="%d" fill="%s" opacity="%.2f"%s>%s</text>'
               % (x, y, s, fill, op, tr, txt))


# ---------- 山：字群堆出剪影（峰顶窄、山脚宽） ----------
def mountain(cx, peak, base, halfw, unit="千山", alpha=1.0, s_top=26):
    y = peak
    while y < base:
        t = (y - peak) / (base - peak)
        hw = halfw * (t ** 1.25)          # 山顶窄、山脚宽，坡面内凹
        s_row = int(round(s_top - 9 * t))
        x = cx - hw
        while x <= cx + hw:
            d = abs(x - cx) / max(hw, 1)   # 0=中轴 1=边缘
            if random.random() < 0.95 - 0.25 * t:
                s = max(10, int(round(s_row - 3 * d + random.uniform(-2, 2))))
                op = (0.97 - 0.55 * d) * (1 - 0.40 * t) * alpha
                T(x + random.uniform(-3, 3), y + random.uniform(-3, 3), s, unit,
                  "#242424", max(op, 0.10))
            x += random.uniform(s_row * 1.45, s_row * 1.75)
        y += random.uniform(s_top * 0.62, s_top * 0.78)
    # 山脚雾化：向外扩散的小淡字，让山"化"进雪里
    for _ in range(34):
        T(cx + random.uniform(-halfw * 1.15, halfw * 1.15),
          base + random.uniform(-8, 44),
          random.randint(10, 14), unit, FAR, random.uniform(0.10, 0.26))


# ---------- 径：斜向点线，越远越稀越小 ----------
def path_dots(p0, p1, p2, unit="万径", n=12, s0=22, s1=12):
    for i in range(n):
        t = i / (n - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        T(x, y, int(round(s0 + (s1 - s0) * t)), unit, "#333", 0.85 - 0.45 * t, rot=-14)


# ---------- 船：船体由「蓑笠翁」字群填满，不外溢轮廓 ----------
def hull(x0, x1, deck, keel, unit="蓑笠翁"):
    y = deck + 6
    while y <= keel - 2:
        x = x0 + random.uniform(0, 10)
        while x <= x1:
            xr = (x - x0) / (x1 - x0)
            yd = deck - 15 * math.sin(math.pi * xr)          # 甲板微拱
            yk = deck + (keel - deck) * math.sin(math.pi * xr) ** 0.6
            s = random.randint(12, 14)
            if yd + 3 <= y <= yk and x + 3 * s * 0.95 < x1:
                T(x, y, s, unit, INK, random.uniform(0.32, 0.6))
            x += random.uniform(36, 42)
        y += 14


# ================= 画面 =================
out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
           'font-family="\'Kaiti SC\',\'STKaiti\',\'KaiTi\',serif" fill="%s">' % (W, H, W, H, INK))
out.append('<rect width="%d" height="%d" fill="#fcfdfe"/>' % (W, H))

# 底晕（极淡，只做雪的空气）


# 远山：最小最淡，压在后排
mountain(806, 168, 348, 72, alpha=0.42, s_top=16)
mountain(700, 196, 372, 86, alpha=0.5, s_top=18)

# 近山：三峰，峰间留白
mountain(400, 108, 384, 134, alpha=1.0, s_top=28)
mountain(176, 168, 404, 120, alpha=1.0, s_top=26)
mountain(838, 318, 438, 66, alpha=0.4, s_top=16)

# 千山：主字压在峰顶
T(112, 196, 82, "千")
T(172, 196, 82, "山")
T(392, 156, 48, "千山", "#242424", 0.85)

# 鸟飞绝：一路向右下坠，越飞越远越淡
for x, y, s, op in [(636, 410, 15, 0.34), (612, 386, 13, 0.27), (660, 386, 12, 0.22)]:
    T(x, y, s, "鸟", "#3a3a3a", op)
T(678, 452, 52, "鸟", INK, 1.0, rot=-12)
T(724, 510, 52, "飞", INK, 1.0, rot=-20)
T(770, 568, 52, "绝", INK, 0.9, rot=-20)
for x, y, s, op in [(800, 500, 14, 0.3), (818, 474, 12, 0.24), (700, 600, 13, 0.24)]:
    T(x, y, s, "鸟", "#3a3a3a", op)

# 万径：一条斜径，越走越淡
T(74, 486, 52, "万")
T(134, 520, 52, "径")
path_dots((196, 540), (320, 604), (452, 668), n=12)

# 人踪灭：径的尽头，没有脚印
T(464, 706, 48, "人", INK, 0.95, rot=26)
T(508, 766, 48, "踪", INK, 0.82, rot=26)
T(552, 826, 48, "灭", INK, 0.66, rot=26)

# 孤舟蓑笠翁：船体全靠字群堆出来
hull(286, 520, 796, 884)
# 船上的人：蓑笠翁叠成一小团，越靠上越小
rows = [(716, 1), (733, 2), (750, 3), (767, 2), (784, 1)]
for y, cnt in rows:
    total = cnt * 48
    cx0 = 404 - total // 2
    for k in range(cnt):
        T(cx0 + k * 48, y, random.randint(13, 16), "蓑笠翁", INK, random.uniform(0.55, 0.95))
# 船舷：小字「孤舟」沿甲板与船底勾边，把船形"描"出来
for k in range(13):
    xr = 0.04 + k * 0.076
    if xr > 1:
        break
    x = 286 + (520 - 286) * xr
    T(x, 796 + 88 * math.sin(math.pi * xr) ** 0.6 - 3, 13, "孤舟", INK, 0.85)
# 船身主字
T(300, 866, 44, "孤", INK, 1.0, rot=-14)
T(348, 850, 46, "舟", INK, 1.0)
T(402, 866, 38, "舟", INK, 1.0, rot=12)

# 独钓：主字 + 垂进江心的细线
T(626, 656, 54, "独", INK, 1.0, rot=-8)
T(668, 716, 54, "钓", INK, 1.0, rot=-18)
for s, (x, y) in zip([17, 15, 13, 12, 11],
                     [(706, 770), (728, 800), (748, 828), (766, 854), (782, 878)]):
    T(x, y, s, "独钓", DEEP, 0.5)

# 寒江：颗粒状水面带（分行分列，不许压成一团）
for i in range(56):
    x = 26 + (i % 14) * 62 + random.uniform(-18, 18)
    y = 930 + (i // 14 - 1.5) * 30 + random.uniform(-13, 13)
    if x > 870:
        continue
    T(x, y, random.randint(12, 19), "寒江", WATER, random.uniform(0.16, 0.5))
T(300, 966, 50, "寒江", DEEP, 0.95)
T(614, 982, 44, "寒江", DEEP, 0.85)

# 雪：大小错落，落满全图
for x, y, s in [(74, 1046, 38), (188, 1112, 32), (312, 1152, 42), (466, 1062, 28),
                (560, 1132, 36), (684, 1094, 32), (796, 1142, 40), (124, 988, 24),
                (492, 1000, 22), (752, 1016, 26), (410, 1110, 22)]:
    T(x, y, s, "雪", SNOW, 0.9)
for _ in range(22):
    T(random.uniform(40, 860), random.uniform(430, 1160), random.randint(11, 17), "雪", SNOW,
      random.uniform(0.2, 0.5))

out.append("</svg>")

with open("v3-2-jiangxue.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote v3-2-jiangxue.svg", len(out), "elements")
