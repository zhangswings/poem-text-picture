#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""登鹳雀楼 · 高密度字群版（v4.1）

对标"字群堆实"的参考做法：
1. 形状用几何包含判断（inside(x,y)），边缘干净，不是概率撒点
2. 填实率 ≈ 95%：字距 ≈ 字宽 0.85，行距 ≈ 字高 0.82，只留 1px 抖动 + ±5° 微旋
3. 同一物体内字号统一，明暗只靠透明度
4. 远山淡、中山中、近山浓；太阳暖橙、河海靛蓝、楼层赭石
5. 大字（主路径）比体字大 3–4 倍，沿物体边缘或留白走
"""
import math
import random

random.seed(5)
W, H = 1000, 1400

INK = "#14161a"
SUN1 = "#b8471f"
SUN2 = "#d98a4a"
RIVER1 = "#2a6489"
RIVER2 = "#6f9cbd"
M1 = "#1b1f22"   # 近山
M2 = "#49535a"   # 中山
M3 = "#b6c0c4"   # 远山
TOWER1 = "#6f4626"
TOWER2 = "#a97b4e"

out = []

# ---- 主字（主阅读路径）：先登记，填字时挖空，最后再写上去 ----
BIGS = [
    (78, 372, 46, "白", 0), (128, 372, 46, "日", 0),
    (184, 424, 48, "依", 14), (230, 474, 48, "山", 24), (276, 524, 48, "尽", 32),
    (72, 744, 50, "黄", 0), (128, 758, 50, "河", 0), (186, 772, 48, "入", -8),
    (712, 780, 62, "海", 0), (800, 826, 54, "流", -14),
    (112, 1004, 56, "欲", 0), (186, 1014, 56, "穷", 0),
    (260, 1004, 56, "千", 0), (334, 1014, 56, "里", 0), (408, 1004, 56, "目", 0),
]
RES = []
for (bx, by, bs, bt, br) in BIGS:
    w = bs * len(bt) * 1.02
    RES.append((bx - 10, by - bs * 1.04, bx + w + 10, by + bs * 0.26))


def T(x, y, s, txt, fill=INK, op=1.0, rot=0.0):
    tr = ' transform="rotate(%.1f %.1f %.1f)"' % (rot, x, y) if rot else ""
    out.append('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" opacity="%.2f"%s>%s</text>'
               % (x, y, s, fill, op, tr, txt))


def fill(inside, x0, x1, y0, y1, size, txt, color, afn,
         jx=1.0, jy=0.9, sx=None, sy=None, rot=5.0, mix=None):
    """几何包含填字；mix 可传 (另一字, 概率) 混排，打散网格感"""
    stepx = sx or size * 0.85
    stepy = sy or size * 0.82
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            if inside(x, y) and not any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in RES):
                a = afn(x, y)
                if a > 0.05:
                    t = txt
                    if mix and random.random() < mix[1]:
                        t = mix[0]
                    T(x + random.uniform(-jx, jx), y + random.uniform(-jy, jy),
                      size, t, color, a, random.uniform(-rot, rot))
            x += stepx
        y += stepy


# ================= 一、白日：日/白混排成圆 =================
CX, CY, R = 198, 176, 112


def sun_in(x, y):
    return (x - CX) ** 2 + (y - CY) ** 2 <= R ** 2


fill(sun_in, CX - R, CX + R, CY - R, CY + R, 17, "日", SUN1,
     lambda x, y: 0.96 - 0.34 * (math.hypot(x - CX, y - CY) / R) ** 1.4,
     jx=1.2, jy=1.0, sx=16.6, sy=15.8, rot=5, mix=("白", 0.30))

# 日晕：外圈一层更淡的「白日」
fill(lambda x, y: ((x - CX) ** 2 + (y - CY) ** 2 <= (R + 26) ** 2
                   and (x - CX) ** 2 + (y - CY) ** 2 > R ** 2),
     CX - R - 26, CX + R + 26, CY - R - 26, CY + R + 26, 13, "白日", SUN2,
     lambda x, y: 0.34 - 0.14 * ((math.hypot(x - CX, y - CY) - R) / 26),
     jx=2.0, jy=1.8, sx=20, sy=20, rot=12)


# ================= 二、山：三层，远淡近浓 =================
def ridge(x, peaks, base):
    h = base
    for (px, py, w) in peaks:
        h = min(h, py + (base - py) * (1 - math.exp(-((x - px) ** 2) / (2 * w * w))))
    return h


far = [(330, 230, 94), (560, 202, 100), (800, 234, 92)]
mid = [(200, 300, 92), (430, 268, 100), (690, 302, 94)]
near = [(300, 372, 98), (580, 340, 106), (840, 380, 96)]

fill(lambda x, y: y >= ridge(x, far, 520), 20, 985, 190, 520, 12, "山", M3,
     lambda x, y: 0.46 - 0.22 * ((y - 190) / 330), sx=12.4, sy=12.0, rot=7)
fill(lambda x, y: y >= ridge(x, mid, 580), 14, 990, 250, 580, 13, "山", M2,
     lambda x, y: 0.74 - 0.26 * ((y - 250) / 330), sx=12.2, sy=11.8, rot=6)
def foot(x):
    return 640 + 22 * math.sin((x - 40) / 170.0)


fill(lambda x, y: ridge(x, near, 650) <= y <= foot(x), 8, 995, 320, 665, 15, "山", M1,
     lambda x, y: (1.0 - 0.62 * ((y - 330) / 320) ** 1.25) * (0.72 + 0.28 * (1 - (y - ridge(x, near, 650)) / 30)),
     sx=13.6, sy=13.0, rot=5)

# 山脚雾：更小更淡的一层，向外化开
fill(lambda x, y: foot(x) <= y <= foot(x) + 34, 8, 995, 640, 700, 10, "山", M3,
     lambda x, y: 0.22 - 0.14 * ((y - 640) / 60), sx=26, sy=22, rot=12)

# 山脚雾化：山与河之间的一道淡字
fill(lambda x, y: 640 < y < 700, 20, 990, 660, 700, 11, "山", M3,
     lambda x, y: 0.20 - 0.14 * ((y - 660) / 40), sx=26, sy=20, rot=10)


# ================= 三、黄河入海：河道会弯、入海处放开 =================
def rc(x):
    return 758 + 46 * math.sin((x - 10) / 210.0) + 13 * math.sin((x - 10) / 74.0)


def rh(x):
    return 11 + max(0.0, x - 60) * 0.078


def river_in(x, y):
    if x > 704:
        return False
    h = rh(x) * (1 + 0.12 * math.sin(x / 33.0) + 0.06 * math.sin(x / 11.0))
    return abs(y - rc(x)) <= h


fill(river_in, 24, 700, 690, 1010, 14, "黄河", RIVER1,
     lambda x, y: 0.90 - 0.40 * abs(y - rc(x)) / max(rh(x), 1),
     sx=12.4, sy=12.0, rot=4)

# 海：与河口相接的一块水域，边缘带波
SCX, SCY, SRX, SRY = 846, 792, 148, 118


def sea_in(x, y):
    dx, dy = (x - SCX) / SRX, (y - SCY) / SRY
    th = math.atan2(dy, dx)
    return math.hypot(dx, dy) <= 1 + 0.07 * math.sin(6 * th) + 0.04 * math.sin(11 * th)


fill(sea_in, SCX - SRX - 16, SCX + SRX + 16, SCY - SRY - 16, SCY + SRY + 16,
     15, "海", RIVER1,
     lambda x, y: 0.96 - 0.30 * math.hypot((x - SCX) / SRX, (y - SCY) / SRY) ** 1.3,
     sx=13.0, sy=12.6, rot=4)

# 浪：河口到海之间的淡蓝小字，接住两块水域
fill(lambda x, y: True, 656, 706, 700, 900, 12, "海", RIVER2,
     lambda x, y: 0.26, sx=16, sy=15, rot=8)


# ================= 四、楼：真阶梯，逐级递升 =================
SX0, N, SW, SH = 424, 9, 56, 44
TOP0 = 1330


def stair_in(x, y):
    if x < SX0 or x > SX0 + N * SW:
        return False
    k = int((x - SX0) // SW)
    top = TOP0 - k * SH
    return top <= y <= top + 30


fill(stair_in, SX0, SX0 + N * SW + 10, 880, 1400, 13, "层楼", TOWER1,
     lambda x, y: 0.95 - 0.22 * ((y - 880) / 520), sx=10.8, sy=9.8, rot=2)


# 楼顶：阶梯最上一级长出一小段塔身
def tower_in(x, y):
    if not (866 <= y <= 986):
        return False
    half = 20 + (986 - y) * 0.115
    return abs(x - 906) <= half


fill(tower_in, 856, 962, 860, 990, 12, "层楼", TOWER2,
     lambda x, y: 0.72 - 0.26 * ((986 - y) / 120), sx=10.8, sy=10.2, rot=3)

# ================= 五、大字：主阅读路径 =================
for (bx, by, bs, bt, br) in BIGS:
    T(bx, by, bs, bt, INK, 1.0, rot=br)

for i, (ch, size) in enumerate([("更", 42), ("上", 42), ("一", 42), ("层", 46), ("楼", 58)]):
    k = i * 2
    x = SX0 + k * SW + 9
    y = TOP0 - k * SH + 26
    T(x, y, size, ch, INK, 1.0, rot=-10)

out.append("</svg>")
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
       'font-family="\'Kaiti SC\',\'STKaiti\',\'KaiTi\',serif" fill="%s">'
       '<rect width="%d" height="%d" fill="#fdfcf9"/>%s'
       % (W, H, W, H, INK, W, H, "\n".join(out)))

with open("v4-1-dengguanquelou.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote v4-1-dengguanquelou.svg", len(out), "text nodes")
