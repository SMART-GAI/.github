"""生成《雀脑 SMART-Sparrow v1 设计》配图（SVG）。用法：python3 images/design/generate_figures.py

与 images/blog/generate_figures.py 同一套视觉风格：浅色底 #fcfcfb、墨色文字、蓝色为主色，
分类色按固定顺序（蓝、橙、青绿、黄、品红、绿、紫、红）取用。只依赖标准库。
"""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif"
MONO = "'SFMono-Regular','Menlo','Consolas','DejaVu Sans Mono',monospace"
BG = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
PANEL = "#f4f3ef"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
GREEN = "#008300"
VIOLET = "#4a3aa7"
RED = "#e34948"
CAT = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
# 单色蓝顺序色阶（100→700，13 级），用于热力表
BLUE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
             "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
# 路由动作配色（与观测台一致）：FAST 绿、FAST+VERIFY 黄、SLOW 橙、ASK 紫
ROUTE = {"FAST": GREEN, "FAST+VERIFY": YELLOW, "SLOW": ORANGE, "ASK": VIOLET}
LAYER_NAMES = ["感觉前端", "落地与语言", "认知骨架", "专家工具箱", "效应器", "学习、社会与观测"]
LAYER_MODS = ["M0–M2", "M3–M4", "M5–M8", "M9–M10", "M11–M13", "M14–M18"]


# ---------------------------------------------------------------- helpers
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tint(c, t):
    """把颜色 c 与白色混合，t 为颜色占比（0..1）。"""
    c = c.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    m = lambda v: round(255 - (255 - v) * t)
    return f"#{m(r):02x}{m(g):02x}{m(b):02x}"


def is_wide(ch):
    o = ord(ch)
    return (0x2E80 <= o <= 0xA4CF or 0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF or
            0xFE30 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFF60 or 0x2460 <= o <= 0x24FF or
            0x2190 <= o <= 0x21FF or 0x2580 <= o <= 0x25FF or 0x2600 <= o <= 0x26FF or
            ch in "—…")


def tw(s, size):
    """估算文字宽度（按 WenQuanYi/PingFang 的大致字宽，略偏保守）。"""
    w = 0.0
    for ch in s:
        if is_wide(ch):
            w += 1.0
        elif ch == " ":
            w += 0.32
        elif ch in "il.,:;|!'()[]·“”‘’":
            w += 0.32
        elif ch in "≥≤✕✓⇄×":
            w += 0.85
        elif ch.isupper() or ch in "mwMW@%&":
            w += 0.72
        else:
            w += 0.58
    return w * size


CLOSERS = "，。、；：）》」』”’！？,.;:)]"


def tokens(s):
    out, buf = [], ""
    for ch in s:
        if is_wide(ch) or ch in "“”":
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        elif ch == " ":
            out.append(buf + " ")
            buf = ""
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def wrap(s, maxw, size):
    lines, cur = [], ""
    for tk in tokens(s):
        if cur and tw(cur + tk, size) > maxw and tk not in CLOSERS:
            lines.append(cur.rstrip())
            cur = tk.lstrip()
        else:
            cur += tk
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def wrap_items(items, maxw, size, sep=" · "):
    lines, cur = [], ""
    for it in items:
        cand = it if not cur else cur + sep + it
        if tw(cand, size) <= maxw:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            if tw(it, size) <= maxw:
                cur = it
            else:
                parts = wrap(it, maxw, size)
                lines.extend(parts[:-1])
                cur = parts[-1]
    if cur:
        lines.append(cur)
    return lines


def fmt(v):
    return f"{v:g}"


class Fig:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.els = []
        self.mk = {}

    def add(self, s):
        self.els.append(s)

    def _mid(self, color):
        k = "ah" + color.lstrip("#")
        self.mk[k] = color
        return k

    def text(self, x, y, s, size=13, anchor="start", bold=False, color=None, cls=None, mono=False, extra=""):
        a = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}"'
        if anchor != "start":
            a += f' text-anchor="{anchor}"'
        if bold:
            a += ' font-weight="700"'
        if cls:
            a += f' class="{cls}"'
        st = []
        if color:
            st.append(f"fill:{color}")
        if mono:
            st.append(f"font-family:{MONO}")
        if st:
            a += f' style="{";".join(st)}"'
        self.add(f"<text {a}{extra}>{esc(s)}</text>")

    def lines(self, x, y, lines, size=12, lh=None, **kw):
        lh = lh or round(size * 1.42, 1)
        for i, s in enumerate(lines):
            self.text(x, y + i * lh, s, size, **kw)
        return y + len(lines) * lh

    def rect(self, x, y, w, h, rx=8, fill="#fff", stroke=None, sw=1.5, dash=None, extra=""):
        a = f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
        if rx:
            a += f' rx="{rx}"'
        a += f' fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.add(f"<rect {a}{extra}/>")

    def circle(self, cx, cy, r, fill="#fff", stroke=None, sw=1.5, extra=""):
        a = f'cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        self.add(f"<circle {a}{extra}/>")

    def path(self, d, color=INK2, sw=1.6, dash=None, arrow=False, fill="none", extra="", cap="round"):
        a = f'd="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="{cap}" stroke-linejoin="round"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if arrow:
            a += f' marker-end="url(#{self._mid(color)})"'
        self.add(f"<path {a}{extra}/>")

    def arrow(self, x1, y1, x2, y2, color=INK2, sw=1.6, dash=None):
        self.path(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}", color, sw, dash, arrow=True)

    def badge(self, cx, cy, label, color=BLUE, r=11, size=13):
        self.circle(cx, cy, r, fill=color)
        self.text(cx, cy + size * 0.36, label, size, anchor="middle", bold=True, color="#fff")

    def chip(self, x, y, s, size=12, color=INK2, fill="#fff", stroke=None, bold=False, pad=8, h=None, dash=None, tcolor=None):
        w = tw(s, size) + 2 * pad
        h = h or size + 12
        self.rect(x, y, w, h, rx=h / 2, fill=fill, stroke=stroke or color, sw=1.2, dash=dash)
        self.text(x + w / 2, y + h / 2 + size * 0.36, s, size, anchor="middle", bold=bold, color=tcolor)
        return w

    def render(self):
        defs = "".join(
            f'<marker id="{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" '
            f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0.6 L10,5 L0,9.4 z" fill="{c}"/></marker>'
            for k, c in self.mk.items())
        body = "\n".join(self.els)
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-label="{self.title}">
<title>{self.title}</title>
<defs>{defs}</defs>
<style>text{{font-family:{FONT};fill:{INK}}} .s{{fill:{INK2}}} .m{{fill:{MUTED}}}</style>
<rect width="{self.w}" height="{self.h}" rx="12" fill="{BG}"/>
{body}
</svg>
'''


def save(name, fig):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(fig.render())


# ---------------------------------------------------------------- small icons
def icon_camera(f, cx, cy, c=INK2):
    f.rect(cx - 15, cy - 9, 30, 20, rx=4, fill="#fff", stroke=c, sw=1.6)
    f.rect(cx - 6, cy - 13, 12, 5, rx=1.5, fill=c)
    f.circle(cx, cy + 1, 6, fill="#fff", stroke=c, sw=1.6)
    f.circle(cx, cy + 1, 2.2, fill=c)


def icon_mic(f, cx, cy, c=INK2):
    f.rect(cx - 5, cy - 13, 10, 17, rx=5, fill="#fff", stroke=c, sw=1.6)
    f.path(f"M{cx-9},{cy-2} Q{cx-9},{cy+9} {cx},{cy+9} Q{cx+9},{cy+9} {cx+9},{cy-2}", c, 1.6)
    f.path(f"M{cx},{cy+9} V{cy+14} M{cx-5},{cy+14} H{cx+5}", c, 1.6)


def icon_screen(f, cx, cy, c=INK2):
    f.rect(cx - 16, cy - 12, 32, 21, rx=2.5, fill="#fff", stroke=c, sw=1.6)
    f.path(f"M{cx},{cy+9} V{cy+13} M{cx-7},{cy+13} H{cx+7}", c, 1.6)


def icon_speaker(f, cx, cy, c=INK2):
    f.path(f"M{cx-13},{cy-5} H{cx-7} L{cx},{cy-11} V{cy+11} L{cx-7},{cy+5} H{cx-13} Z", c, 1.6, fill="#fff")
    f.path(f"M{cx+5},{cy-5} Q{cx+9},{cy} {cx+5},{cy+5} M{cx+9},{cy-9} Q{cx+16},{cy} {cx+9},{cy+9}", c, 1.6)


def icon_tablet(f, cx, cy, c=INK2):
    f.rect(cx - 16, cy - 11, 30, 22, rx=3, fill="#fff", stroke=c, sw=1.6)
    f.path(f"M{cx-10},{cy+4} q4,-9 8,-2 t8,-3", c, 1.4)
    f.path(f"M{cx+7},{cy+13} L{cx+17},{cy-3}", c, 2.2)


def icon_sun(f, cx, cy, c=YELLOW):
    for k in range(8):
        a = k * math.pi / 4
        f.path(f"M{cx+9*math.cos(a):.1f},{cy+9*math.sin(a):.1f} L{cx+13*math.cos(a):.1f},{cy+13*math.sin(a):.1f}", c, 2)
    f.circle(cx, cy, 6, fill=c)


def icon_moon(f, cx, cy, c=VIOLET):
    f.path(f"M{cx+3},{cy-11} A11,11 0 1,0 {cx+10},{cy+6} A8.5,8.5 0 1,1 {cx+3},{cy-11} Z", c, 1, fill=c)


def icon_person(f, cx, cy, c=INK2, s=1.0):
    f.circle(cx, cy - 22 * s, 13 * s, fill="#fff", stroke=c, sw=1.8)
    f.path(f"M{cx-24*s:.1f},{cy+30*s:.1f} Q{cx-24*s:.1f},{cy-4*s:.1f} {cx:.1f},{cy-4*s:.1f} "
           f"Q{cx+24*s:.1f},{cy-4*s:.1f} {cx+24*s:.1f},{cy+30*s:.1f}", c, 1.8, fill="#fff")


# ================================================================ 1. routes × criteria heat table
def fig_routes():
    W, H = 1200, 560
    f = Fig(W, H, "五条候选路线在 8 项标准上的评审得分")
    f.text(40, 44, "五条候选路线的评审得分", 22, bold=True)
    f.text(40, 70, "8 项标准各 1–10 分，颜色越深分越高；最右一列为总分（满分 80）。路线 C 总分最高，被选作综合架构的主干。",
           14, cls="s")
    crit = [("低算力",), ("熟悉任务", "够快"), ("越熟越懂",), ("人类同款", "I/O"), ("现有技术", "可行性"),
            ("可观测性",), ("有机组合",), ("通用性",)]
    rows = [
        ("C", "快慢双通道·算法超市", "DualLane AlgoMart", [9, 8.5, 6.5, 6, 8.5, 9, 9.5, 5.5], 62.5),
        ("A", "神经-符号全局工作空间", "NeSy-GW（雀脑工作空间）", [5, 7.5, 8, 6, 7, 10, 9.5, 7.5], 60.5),
        ("E", "记忆中心·互补学习系统", "Sparrow-CLS（海马—新皮层—小脑）", [6, 7.5, 9, 6.5, 7, 9.5, 8, 7], 60.5),
        ("D", "发育闭环", "DevLoop（像婴儿一样长大）", [8, 7.5, 9, 8.5, 4, 9, 8, 6], 60),
        ("B", "预测之雀", "PredSparrow（小型 JEPA + 主动推理）", [7.5, 7.5, 7.5, 6.5, 5, 8, 7, 7], 56),
    ]
    lx, cx0, cw, gp = 40, 384, 72, 8
    pitch = cw + gp
    hy = 144
    for j, c in enumerate(crit):
        x = cx0 + j * pitch + cw / 2
        for k, s in enumerate(reversed(c)):
            f.text(x, hy - k * 17, s, 13, anchor="middle", cls="s")
    tx = cx0 + 8 * pitch + 20
    f.text(tx, hy, "总分", 13, cls="s")
    colmax = [max(r[3][j] for r in rows) for j in range(8)]
    ry0, rh = 158, 62
    for i, (code, name, sub, vals, tot) in enumerate(rows):
        assert abs(sum(vals) - tot) < 1e-9, (code, sum(vals), tot)
        y = ry0 + i * rh
        if i:
            f.path(f"M{lx},{y:.1f} H{cx0-12}", GRID, 1)
        f.text(lx, y + 30, f"路线 {code}", 16, bold=True)
        f.text(lx + 66, y + 30, name, 15)
        if i == 0:
            bx = lx + 66 + tw(name, 15) + 10
            f.rect(bx, y + 14, 44, 22, rx=11, fill=BLUE)
            f.text(bx + 22, y + 29.5, "主干", 12, anchor="middle", bold=True, color="#fff")
        f.text(lx + 66, y + 49, sub, 12, cls="m")
        for j, v in enumerate(vals):
            x = cx0 + j * pitch
            k = int(round((v - 4) * 2))
            best = v == colmax[j]
            f.rect(x, y + 6, cw, rh - 12, rx=6, fill=BLUE_RAMP[k])
            if best:
                f.rect(x - 3.5, y + 2.5, cw + 7, rh - 5, rx=8, fill="none", stroke=INK, sw=2)
            f.text(x + cw / 2, y + rh / 2 + 5.5, fmt(v), 16, anchor="middle", bold=best,
                   color="#fff" if k >= 7 else INK)
        bw = tot / 80 * 110
        f.rect(tx, y + 20, bw, 22, rx=4, fill=BLUE if i == 0 else "#86b6ef")
        f.text(tx + bw + 8, y + 36, fmt(tot), 15, bold=True)
    f.path(f"M{tx},{ry0+6} V{ry0+5*rh-6}", MUTED, 1.2)
    # legend
    ly = ry0 + 5 * rh + 34
    f.text(40, ly + 12.5, "单项评分", 13, cls="s")
    for k, c in enumerate(BLUE_RAMP):
        x = 110 + k * 26
        f.rect(x, ly, 24, 16, rx=3, fill=c)
        if k % 2 == 0:
            f.text(x + 12, ly + 34, fmt(4 + k / 2), 12, anchor="middle", cls="m")
    x = 110 + 13 * 26 + 36
    f.rect(x, ly, 24, 16, rx=3, fill=BLUE_RAMP[8])
    f.rect(x - 3, ly - 3, 30, 22, rx=5, fill="none", stroke=INK, sw=2)
    f.text(x + 36, ly + 12.5, "该项最高分（含并列）", 13, cls="s")
    x2 = x + 36 + tw("该项最高分（含并列）", 13) + 36
    f.rect(x2, ly + 1, 30, 14, rx=3, fill=BLUE)
    f.text(x2 + 40, ly + 12.5, "总分条：深色为选定的主干路线", 13, cls="s")
    return f


# ================================================================ 2. architecture (6 layers, 19 modules)
LAYERS = [
    ("第一层", ["感觉前端"], "神经网络 · 输入端", [
        ("M0", "事件闸门", ["帧差 / MOG2", "谱残差显著性", "Silero VAD", "中文 KWS", "30s 视听环形缓冲", "按需唤醒 M1 / M2"]),
        ("M1", "视觉级联", ["MobileNetV3 要旨", "DINOv2 中央凹", "EdgeSAM 分割", "ByteTrack + IMM",
                          "MediaPipe 手 / 姿态 / 脸", "PP-OCRv5 + HCCR"]),
        ("M2", "听觉前端", ["AEC3 + 自听支路", "流式 Zipformer", "语义早端点", "segmental DTW", "WORLD F0 声调",
                          "ECAPA 说话人"]),
    ]),
    ("第二层", ["落地与语言"], "原型与符号", [
        ("M3", "概念中枢 · 落地束", ["hub + spoke：认 / 写 / 画 / 说同一表示", "NCM + Deep SLDA", "共同注意贝叶斯绑定",
                                "kNN 开集", "ACI / Mondrian 共形"]),
        ("M4", "语言理解", ["Lark / WFST 句式语法", "CRF 槽位", "LightGBM 意图", "WeTextProcessing 数词",
                          "Qwen2.5-0.5B 按需懒加载（GBNF 约束）"]),
    ]),
    ("第三层", ["认知骨架"], "经典算法 · 调度", [
        ("M5", "全局工作空间", ["10Hz 认知周期", "4–7 组块联盟", "LightGBM 排序", "STN 输出同步"]),
        ("M6", "元认知路由器", ["置信度契约", "CART 深度 ≤6", "FAST/VERIFY/SLOW/ASK", "经验性能模型"]),
        ("M7", "技能缓存", ["Soar / CLIPS chunking", "L0–L3 晋级", "Beta 后验", "Minton 剪枝"]),
        ("M8", "海马情景记忆", ["事件分割", "HNSW + IVF-PQ", "Hopfield 重排", "冷热分层"]),
    ]),
    ("第四层", ["专家工具箱"], "精确推理 · 模拟", [
        ("M9", "符号推理与规划", ["精确算术 / SymPy", "clingo / Scallop", "HTN / A* / MCTS", "CP-SAT 版面",
                              "Stitch 库学习"]),
        ("M10", "世界模型与心理模拟", ["MOG2 + Hough 测量", "卡尔曼 + IMM", "NumPy 解析积分 / pymunk", "精度加权残差",
                                "惊奇信号", "QPT 叙述"]),
    ]),
    ("第五层", ["效应器"], "神经网络 · 输出端", [
        ("M11", "笔运动系统", ["sigma-lognormal", "ProMP", "身体图式单应", "摊销逆模型", "ILC 读回修正"]),
        ("M12", "屏幕渲染", ["Skia 逐笔动画", "线稿网络 + RDP", "部件程序", "ARAP 形变", "精灵合成"]),
        ("M13", "语音输出", ["模板 NLG", "数字读法规则", "Matcha-TTS + Vocos", "波形缓存"]),
    ]),
    ("第六层", ["学习 · 社会", "与观测"], "闭环 · 睡眠 · 观测", [
        ("M14", "自我监控", ["真实感官读回", "社会反馈检测", "错误归因", "划掉重写"]),
        ("M15", "好奇与练习", ["学习进度老虎机", "屏幕物理沙盒"]),
        ("M16", "睡眠巩固", ["优先重放", "编译蒸馏", "Stitch", "金丝雀回滚", "CI 损伤测试"]),
        ("M17", "上帝视角观测台", ["事件溯源", "因果父 ID", "快照回放", "11 个视图"]),
        ("M18", "先天固件清单", ["先天符号桥", "句式种子", "物理先验", "消融实验"]),
    ]),
]


def fig_architecture():
    W, H = 1340, 1116
    f = Fig(W, H, "SMART-Sparrow v1 综合架构：6 层 19 个模块")
    f.text(40, 42, "SMART-Sparrow（雀脑）v1：6 层 19 个模块", 22, bold=True)
    f.text(40, 68, "神经网络只守两端（感觉前端、效应器）；中间的记忆、判断、推理、调度交给非参数结构和经典算法，全程向观测台发布事件。",
           14, cls="s")
    XB0, XB1 = 200, 1060
    LBL = 118
    MX0, MX1 = XB0 + LBL, XB1 - 10
    BH, GAP = 108, 38
    tops = [190 + i * (BH + GAP) for i in range(6)]
    mid = [t + BH / 2 for t in tops]
    boxes = {}
    for li, (num, names, note, mods) in enumerate(LAYERS):
        y = tops[li]
        col = CAT[li]
        f.rect(XB0, y, XB1 - XB0, BH, rx=10, fill=tint(col, 0.09), stroke=tint(col, 0.45), sw=1.2)
        f.rect(XB0, y, 6, BH, rx=3, fill=col)
        ty = y + 28 if len(names) == 1 else y + 24
        f.text(XB0 + 16, ty, num, 12, cls="m")
        for k, nm in enumerate(names):
            f.text(XB0 + 16, ty + 21 + k * 19, nm, 15, bold=True)
        f.text(XB0 + 16, ty + 21 + len(names) * 19 + 2, note, 11, cls="s")
        n = len(mods)
        mw = (MX1 - MX0 - (n - 1) * 8) / n
        for k, (code, name, algs) in enumerate(mods):
            x = MX0 + k * (mw + 8)
            by = y + 8
            f.rect(x, by, mw, BH - 16, rx=7, fill="#fff", stroke=tint(col, 0.6), sw=1.3)
            f.text(x + 9, by + 20, code, 13, bold=True, color=INK)
            f.text(x + 9 + tw(code, 13) + 6, by + 20, name, 13, bold=True)
            ls = wrap_items(algs, mw - 18, 11.5)
            assert len(ls) <= 4, (code, ls)
            f.lines(x + 9, by + 38, ls, 11.5, lh=15.5, cls="s")
            boxes[code] = (x, by, mw, BH - 16)
    # ---- inputs (top) and raw bus
    for cx, lab, sub, ic in [(560, "摄像头 ×1", "≥1080p（建议 4K）· 30fps", icon_camera),
                             (860, "麦克风 ×2", "16kHz · AEC3 保留自听", icon_mic)]:
        f.rect(cx - 110, 88, 220, 52, rx=10, fill="#fff", stroke=INK2, sw=1.5)
        ic(f, cx - 82, 114)
        f.text(cx - 58, 110, lab, 14, bold=True)
        f.text(cx - 58, 129, sub, 11.5, cls="s")
        f.arrow(cx, 140, cx, 166)
    f.path(f"M{MX0+40},168 H{MX1-40}", INK2, 1.6)
    f.text(MX0 - 2, 162, "原始像素与波形（唯一输入）", 12, cls="s", anchor="end")
    for code in ("M0", "M1", "M2"):
        x, by, mw, bh = boxes[code]
        f.arrow(x + mw / 2, 168, x + mw / 2, by - 1)

    # ---- gap arrows between layers
    def gap(i, x, label, up=False, lx=None):
        y1, y2 = tops[i] + BH, tops[i + 1]
        if up:
            f.arrow(x, y2, x, y1 + 1)
        else:
            f.arrow(x, y1, x, y2 - 1)
        f.text((lx or x) + 10, (y1 + y2) / 2 + 4.5, label, 12, cls="s")
    cx = lambda code: boxes[code][0] + boxes[code][2] / 2
    gap(0, cx("M3"), "感知记录：嵌入 · 候选符号 · 结构 · 置信度契约 → M3 / M5 / M8")
    gap(1, cx("M3"), "概念 ID · 任务框架 → 黑板竞争与广播")
    gap(2, cx("M5"), "anytime 结果回黑板", up=True)
    gap(2, cx("M6"), "SLOW：按期望效用调用专家")
    gap(3, cx("M3"), "笔迹 / 草图 / 语音计划 → STN 同步")
    gap(4, cx("M14"), "动作与读回 → M14 奖励、错误归因")
    gap(4, cx("M16"), "睡眠巩固写回 M3 / M7 / M8 与小网络", up=True)
    # ---- FAST bypass (layer 3 -> layer 5)
    fx = 1095
    y5 = tops[4]
    drop = (boxes["M12"][0] + boxes["M12"][2] + boxes["M13"][0]) / 2
    f.path(f"M{XB1},{mid[2]:.1f} H{fx} V{y5-16} H{drop:.1f} V{y5-1}", GREEN, 2.4, arrow=True)
    f.rect(fx + 10, mid[3] - 24, 138, 48, rx=8, fill="#fff", stroke=GREEN, sw=1.4)
    f.text(fx + 22, mid[3] - 4, "FAST 直达", 13, bold=True)
    f.text(fx + 22, mid[3] + 14, "L2 / L3 技能 · <10ms", 11.5, cls="s")
    # ---- outputs (right, at effector level)
    outs = [("带屏手写板（M11）", icon_tablet), ("屏幕画布（M12）", icon_screen), ("扬声器（M13）", icon_speaker)]
    ox, ow, oh = 1140, 168, 32
    for k, (lab, ic) in enumerate(outs):
        oy = tops[4] + 2 + k * (oh + 6)
        f.rect(ox, oy, ow, oh, rx=8, fill="#fff", stroke=INK2, sw=1.5)
        ic(f, ox + 22, oy + oh / 2 + 1)
        f.text(ox + 44, oy + oh / 2 + 4.5, lab, 12.5)
        f.arrow(XB1, oy + oh / 2, ox - 1, oy + oh / 2)
    f.text(ox, tops[5] + 22, "✕ 没有文本输出通道", 12, cls="s")
    f.text(ox, tops[5] + 40, "屏上的字也由笔画程序画出", 11.5, cls="m")
    # ---- re-perception loop (outputs -> sensors)
    ly = tops[4] + BH / 2
    f.path(f"M{ox+ow},{ly:.1f} H1322 V114 H971", ORANGE, 2.6, dash="7 5", arrow=True)
    f.rect(1140, mid[1] - 44, 168, 88, rx=8, fill="#fff", stroke=ORANGE, sw=1.4)
    f.lines(1152, mid[1] - 20, ["再感知闭环", ], 13, bold=True)
    f.lines(1152, mid[1] + 0, ["自己写的、画的、说的", "只能经摄像头和麦克风", "重新读回"], 11.5, lh=15, cls="s")
    # ---- observatory tap (left)
    sx0, sx1 = 30, 178
    f.rect(sx0, tops[0], sx1 - sx0, tops[5] + BH - tops[0], rx=10, fill=PANEL, stroke=MUTED, sw=1.3, dash="4 4")
    f.text(sx0 + 12, tops[0] + 26, "观测旁路", 15, bold=True)
    f.lines(sx0 + 12, tops[0] + 48, ["事件总线 tap", "单向玻璃 · 只读"], 12, cls="s")
    f.text(sx0 + 12, tops[1] + 30, "每一步都发布带", 12, cls="s")
    f.text(sx0 + 12, tops[1] + 47, "因果父 ID 的事件：", 12, cls="s")
    kinds = ["percept", "hypothesis", "decision", "action", "outcome", "learn", "consolidate"]
    f.lines(sx0 + 16, tops[1] + 72, kinds, 12, lh=19, mono=True)
    f.lines(sx0 + 12, tops[3] + 60, ["Parquet + DuckDB", "快照 + 消息日志回放", "实验者只碰快照副本"], 11.5, lh=17, cls="s")
    for i in range(6):
        f.arrow(XB0, mid[i], sx1 + 1, mid[i], MUTED, 1.4, dash="2 3")
    x17, by17, w17, h17 = boxes["M17"]
    yb = tops[5] + BH + 16
    f.path(f"M{(sx0+sx1)/2},{tops[5]+BH} V{yb} H{x17+w17/2:.1f} V{by17+h17+1:.1f}", MUTED, 1.6, dash="2 3", arrow=True)
    f.text(x17 + w17 / 2 + 10, yb + 17, "汇入 M17 上帝视角观测台", 12, cls="s")
    # ---- legend
    lgy = H - 18
    x = 40
    f.path(f"M{x},{lgy-4} h36", INK2, 1.6, arrow=True)
    f.text(x + 46, lgy, "主数据流", 12, cls="s")
    x += 130
    f.path(f"M{x},{lgy-4} h36", GREEN, 2.4, arrow=True)
    f.text(x + 46, lgy, "FAST 快通道", 12, cls="s")
    x += 150
    f.path(f"M{x},{lgy-4} h36", ORANGE, 2.6, dash="7 5", arrow=True)
    f.text(x + 46, lgy, "再感知闭环", 12, cls="s")
    x += 140
    f.path(f"M{x},{lgy-4} h36", MUTED, 1.4, dash="2 3", arrow=True)
    f.text(x + 46, lgy, "观测旁路（只读）", 12, cls="s")
    return f


# ================================================================ 3. human-like body and closed loop
def fig_io_body():
    W, H = 1180, 720
    f = Fig(W, H, "人类同款身体：原始视听输入、三路输出与再感知闭环")
    f.text(40, 42, "人类同款身体：只有原始视听进来，只有笔、屏、声出去", 22, bold=True)
    f.text(40, 68, "摄像头看得见白板、老师，也看得见自己的手写板和屏幕；麦克风听得见老师，也听得见自己的声音。", 14, cls="s")
    VIS, AUD, MOT = BLUE, AQUA, VIOLET
    TOPL = 110  # loop line y
    # column A: world
    f.text(40, 146, "外部世界", 13, bold=True, color=INK2)
    f.rect(40, 156, 210, 110, rx=4, fill="#fff", stroke=INK2, sw=1.6)
    f.text(52, 176, "白板", 12, cls="m")
    f.text(145, 228, "12+7=", 34, anchor="middle", color=INK2, extra=' font-style="italic"')
    icon_person(f, 76, 404, INK2, 1.1)
    f.rect(120, 366, 130, 38, rx=10, fill="#fff", stroke=INK2, sw=1.3)
    f.path("M132,394 l-22,14 l30,-8", INK2, 1.3, fill="#fff")
    f.rect(128, 391, 16, 11, rx=0, fill="#fff")
    f.text(185, 390, "“写一个大字”", 13, anchor="middle")
    f.text(40, 466, "老师（照料者）", 13, bold=True)
    f.text(40, 485, "指向 · 表情 · 点头 · 说话", 11.5, cls="s")
    # column B: sensors
    f.text(310, 146, "感官", 13, bold=True, color=INK2)
    f.rect(310, 160, 160, 84, rx=10, fill="#fff", stroke=VIS, sw=1.8)
    icon_camera(f, 340, 202, VIS)
    f.text(366, 196, "摄像头", 15, bold=True)
    f.text(366, 216, "≥1080p · 30fps", 11.5, cls="s")
    f.text(366, 233, "中央凹原生裁剪", 11.5, cls="s")
    f.rect(310, 340, 160, 84, rx=10, fill="#fff", stroke=AUD, sw=1.8)
    icon_mic(f, 332, 382, AUD)
    icon_mic(f, 352, 382, AUD)
    f.text(372, 376, "麦克风 ×2", 15, bold=True)
    f.text(372, 396, "16kHz", 11.5, cls="s")
    f.text(372, 413, "AEC3 回声消除", 11.5, cls="s")
    # column C: brain
    f.rect(540, 150, 190, 284, rx=14, fill=tint(BLUE, 0.06), stroke=BLUE, sw=1.8)
    f.text(635, 180, "雀脑", 18, bold=True, anchor="middle")
    f.text(635, 199, "SMART-Sparrow v1", 12, anchor="middle", cls="m")
    for i in range(6):
        y = 214 + i * 34
        f.rect(556, y, 158, 28, rx=6, fill=tint(CAT[i], 0.16))
        f.text(566, y + 18.5, LAYER_NAMES[i] if i < 5 else "学习与社会", 12)
        f.text(704, y + 18.5, LAYER_MODS[i] if i < 5 else "M14–M16", 11, anchor="end", cls="s")
    # column D: effectors
    f.text(790, 146, "效应器", 13, bold=True, color=INK2)
    effs = [("笔 · M11", "200Hz (x, y, 压力)", 160), ("屏幕 · M12", "1024×768 · 30fps", 270), ("发声 · M13", "24kHz 波形", 380)]
    for lab, sub, y in effs:
        f.rect(790, y, 124, 58, rx=10, fill="#fff", stroke=MOT, sw=1.8)
        f.text(802, y + 25, lab, 14, bold=True)
        f.text(802, y + 44, sub, 11, cls="s")
    # column E: own devices
    f.text(970, 146, "自己的设备（都在视野里）", 13, bold=True, color=INK2)
    devs = [("带屏手写板", "写字 · 画画", icon_tablet, 160), ("显示屏", "逐笔动画 · 预测画面", icon_screen, 270),
            ("扬声器", "说话", icon_speaker, 380)]
    for lab, sub, ic, y in devs:
        f.rect(970, y, 170, 58, rx=10, fill="#fff", stroke=INK2, sw=1.6)
        ic(f, 996, y + 29)
        f.text(1024, y + 25, lab, 14, bold=True)
        f.text(1024, y + 44, sub, 11.5, cls="s")
    # sensing arrows
    f.arrow(250, 205, 309, 205, VIS, 2)
    f.arrow(96, 362, 316, 245, VIS, 2)
    f.arrow(250, 385, 309, 385, AUD, 2)
    f.arrow(470, 202, 539, 202, VIS, 2)
    f.text(505, 194, "像素", 11.5, anchor="middle", cls="s")
    f.arrow(470, 382, 539, 382, AUD, 2)
    f.text(505, 374, "波形", 11.5, anchor="middle", cls="s")
    for _, _, y in effs:
        f.arrow(730, y + 29, 789, y + 29, MOT, 2)
        f.arrow(914, y + 29, 969, y + 29, MOT, 2)
    # re-perception loops
    f.path(f"M1140,299 H1160 V{TOPL} H390 V159", ORANGE, 3, dash="8 5", arrow=True)
    f.path("M1140,189 H1160", ORANGE, 3, dash="8 5")
    f.rect(560, TOPL - 13, 356, 26, rx=13, fill="#fff", stroke=ORANGE, sw=1.4)
    f.text(738, TOPL + 4.5, "再感知闭环：摄像头看见自己写的字、画的画", 12.5, anchor="middle", bold=True)
    BOT = 470
    f.path(f"M1055,438 V{BOT} H390 V425", ORANGE, 3, dash="8 5", arrow=True)
    f.rect(556, BOT - 13, 364, 26, rx=13, fill="#fff", stroke=ORANGE, sw=1.4)
    f.text(738, BOT + 4.5, "再感知闭环：麦克风经 AEC 自听支路听见自己", 12.5, anchor="middle", bold=True)
    # bottom: experimenter channel & hard rules
    by = 520
    f.rect(40, by, 560, 170, rx=12, fill=PANEL, stroke=MUTED, sw=1.4, dash="6 5")
    f.text(58, by + 28, "实验者通道（观测台，与学习隔离）", 15, bold=True)
    f.rect(58, by + 46, 250, 52, rx=8, fill="#fff", stroke=MUTED, sw=1.2, dash="4 4")
    f.text(70, by + 67, "暂停 · 编辑 · 干预 · 人工标注", 12.5)
    f.text(70, by + 86, "反事实实验", 11.5, cls="s")
    f.arrow(308, by + 72, 360, by + 72, MUTED, 1.6, dash="4 3")
    f.rect(362, by + 46, 220, 52, rx=8, fill="#fff", stroke=MUTED, sw=1.2)
    f.text(374, by + 67, "只作用于快照副本", 12.5, bold=True)
    f.text(374, by + 86, "事件标 origin=experimenter", 11.5, cls="s")
    # blocked stub toward the brain
    f.path(f"M470,{by} V{by-26}", RED, 2, dash="4 3")
    f.text(470, by - 30, "✕", 18, anchor="middle", bold=True, color=RED)
    f.text(486, by - 14, "不写入学习", 12.5, bold=True)
    f.lines(58, by + 124, ["默认不写入任何学习存储；平台对雀脑严格只读（单向玻璃）。",
                           "教学反馈只能由人经摄像头和麦克风给出。"], 12.5, lh=20, cls="s")
    f.rect(630, by, 510, 170, rx=12, fill="#fff", stroke=GRID, sw=1.4)
    f.text(648, by + 28, "硬约束", 15, bold=True)
    rules = [("✓", GREEN, "运行时输入只有原始像素和波形"),
             ("✓", GREEN, "所有输出都要经真实感官重新感知，自检才算数"),
             ("✕", RED, "没有文本输出通道：屏上的字也要一笔一笔画出来"),
             ("✕", RED, "不读取手写板的数字回读（避免暗含本体感觉输入）"),
             ("✕", RED, "字形不直接读入：只能“看示范”或走明示的先天包")]
    for k, (sym, c, s) in enumerate(rules):
        y = by + 56 + k * 24
        f.text(650, y, sym, 14, bold=True, color=c)
        f.text(672, y, s, 12.5)
    return f


# ================================================================ 4. fast/slow ladder + router
def fig_ladder():
    W, H = 1200, 700
    f = Fig(W, H, "快慢双通道：四级晋级阶梯与路由器的四种动作")
    f.text(40, 42, "快慢双通道：四级晋级阶梯 + 路由器的四种动作", 22, bold=True)
    f.text(40, 68, "用回忆逐步替代计算：每次晋级都有可测的证据门槛；一旦失败就降级，旧版本保留。", 14, cls="s")
    # ---- left: ladder
    f.text(40, 108, "晋级阶梯（M7 技能缓存）", 15, bold=True)
    lv = [("L3", "运动自动化", "直接展开动作程序（sigma-lognormal / 缓存波形）", "<1 ms", 11),
          ("L2", "查表习惯", "任务键或感知签名 → 输出程序", "微秒级", 8),
          ("L1", "编译规则", "Soar / CLIPS 产生式匹配（10⁴ 条规则量级）", "0.1–1 ms", 6),
          ("L0", "深思", "工作空间 + 专家工具箱 + 可选 LM，anytime 可打断", "0.1–5 s", 3)]
    bx, bw, bh, g = 110, 300, 86, 54
    ys = [128 + i * (bh + g) for i in range(4)]
    for (code, name, desc, lat, ramp), y in zip(lv, ys):
        f.rect(bx, y, bw, bh, rx=10, fill="#fff", stroke=GRID, sw=1.6)
        f.rect(bx, y, 58, bh, rx=10, fill=BLUE_RAMP[ramp])
        f.rect(bx + 48, y, 10, bh, rx=0, fill=BLUE_RAMP[ramp])
        f.text(bx + 29, y + bh / 2 + 7, code, 20, anchor="middle", bold=True, color="#fff" if ramp >= 7 else INK)
        f.text(bx + 72, y + 28, name, 16, bold=True)
        lw = tw(lat, 12) + 16
        f.rect(bx + bw - lw - 10, y + 12, lw, 22, rx=11, fill=PANEL)
        f.text(bx + bw - 10 - lw / 2, y + 27.5, lat, 12, anchor="middle", bold=True)
        f.lines(bx + 72, y + 52, wrap(desc, bw - 84, 12), 12, lh=17, cls="s")
    promos = [("≥3 次一致成功", "chunking 编译为规则"), ("≥20 次且影子一致率 ≥98%", "升为查表"),
              ("ProMP 方差收敛", "且读回错误率 <2%（运动技能）")]
    for k, (a, b) in enumerate(promos):
        lo, hi = ys[3 - k], ys[2 - k]
        x = bx + bw - 60
        f.arrow(x, lo - 2, x, hi + bh + 3, BLUE, 2.2)
        f.text(bx + bw + 14, hi + bh + g / 2 - 3, a, 12.5, bold=True)
        f.text(bx + bw + 14, hi + bh + g / 2 + 15, b, 12, cls="s")
    # demotion
    dx = 72
    f.path(f"M{dx},{ys[0]+20} V{ys[3]+bh-20}", RED, 1.8, dash="5 4", arrow=True)
    f.text(dx - 10, (ys[0] + ys[3] + bh) / 2, "失败即降级 · 旧版本保留", 12.5, anchor="middle", cls="s",
           extra=f' transform="rotate(-90 {dx-10} {(ys[0]+ys[3]+bh)/2})"')
    f.text(40, ys[3] + bh + 40, "慢路成功解立即进入 L2 候选试用期：Beta(2,1)，前 N 次强制 FAST+VERIFY。", 12.5, cls="s")
    # ---- right: router
    rx0, rx1 = 640, 1170
    f.text(rx0, 108, "路由器（M6 元认知路由器）", 15, bold=True)
    f.rect(rx0, 122, rx1 - rx0, 76, rx=10, fill=PANEL)
    f.text(rx0 + 14, 145, "输入：置信度契约", 13, bold=True)
    f.lines(rx0 + 14, 166, ["校准概率 · 共形集大小 · 新颖度（kNN 百分位）· top1–top2 间隔 · 预计代价",
                            "+ Count-Min 计数（见过吗）· 技能 Beta 后验 95% 下界 · IMM / 集成方差"], 12, lh=18, cls="s")
    f.arrow((rx0 + rx1) / 2, 198, (rx0 + rx1) / 2, 216)
    f.rect(rx0, 218, rx1 - rx0, 38, rx=10, fill="#fff", stroke=INK2, sw=1.6)
    f.text((rx0 + rx1) / 2, 242, "CART 决策树（深度 ≤6，冷启动由约 30 条先天规则写成）", 13, anchor="middle", bold=True)
    cards = [
        ("FAST", "→ L2 / L3", "决策 <10ms",
         "条件：技能 ≥L2 · Beta 下界 ≥ τ_risk · 共形集 = 1 · 新颖 < P90",
         ["动作：直接执行技能条目（查表或展开运动程序）。"]),
        ("FAST+VERIFY", "→ 快路 + 影子", "试用期",
         "条件：技能在试用期，或下界落在 [τ_low, τ_risk)",
         ["动作：快路先出结果，慢路在影子中核对；", "不一致以慢路为准，快路记一次失败并降级；", "落笔前 150–250ms 可撤回，已落笔则划掉重写。"]),
        ("SLOW", "→ L0 深思", "0.1–5 s",
         "条件：新颖度高（认知不确定），或其余所有情况",
         ["动作：按 U = P·V − λ·cost 排序调用专家，anytime 运行；", "计算价值 VOC 决定想多深；新颖时同时启动学习。"]),
        ("ASK", "→ 再看 / 提问", "最便宜",
         "条件：新颖度低但共形集 > 1（偶然不确定）",
         ["动作：先放大中央凹再看一眼、再听一遍；", "仍不确定就开口问：“是十二加七吗？”"]),
    ]
    cy = 276
    tx = rx0 + 150
    trunk_x = rx0 - 16
    mids = []
    for name, tag, sub, cond, act in cards:
        lines_c = wrap(cond, rx1 - tx - 8, 12.5)
        lines_a = [l for seg in act for l in wrap(seg, rx1 - tx - 8, 12)]
        ch = max(84, 18 + len(lines_c) * 18 + len(lines_a) * 17 + 12)
        col = ROUTE[name]
        f.rect(rx0, cy, rx1 - rx0, ch, rx=10, fill="#fff", stroke=GRID, sw=1.4)
        f.rect(rx0, cy, 140, ch, rx=10, fill=tint(col, 0.16))
        f.rect(rx0 + 130, cy, 10, ch, rx=0, fill=tint(col, 0.16))
        f.rect(rx0, cy, 6, ch, rx=3, fill=col)
        f.text(rx0 + 18, cy + 28, name, 15 if len(name) < 6 else 13.5, bold=True)
        f.text(rx0 + 18, cy + 48, tag, 12, cls="s")
        f.text(rx0 + 18, cy + 66, sub, 11.5, cls="m")
        yy = f.lines(tx, cy + 26, lines_c, 12.5, lh=18)
        f.lines(tx, yy + 2, lines_a, 12, lh=17, cls="s")
        mids.append(cy + ch / 2)
        cy += ch + 12
    f.path(f"M{rx0},{237} H{trunk_x} V{mids[-1]:.1f}", INK2, 1.6)
    for m in mids:
        f.arrow(trunk_x, m, rx0 - 1, m)
    assert cy <= H - 10, cy
    return f


# ================================================================ 5. learning loop
def fig_learning():
    W, H = 1200, 720
    f = Fig(W, H, "学习循环：清醒时在线快学，睡眠时巩固")
    f.text(40, 42, "学习循环：清醒时在线快学，睡眠时巩固", 22, bold=True)
    f.text(40, 68, "清醒期全部追加式、不用梯度、可回滚；参数更新只在睡眠期进行，并受金丝雀门控。", 14, cls="s")
    # ---- awake panel
    ax0, ax1, ay0, ay1 = 30, 410, 92, 690
    f.rect(ax0, ay0, ax1 - ax0, ay1 - ay0, rx=14, fill=tint(YELLOW, 0.08), stroke=tint(YELLOW, 0.5), sw=1.4)
    icon_sun(f, ax0 + 32, ay0 + 26)
    f.text(ax0 + 52, ay0 + 32, "清醒 · 在线快学", 17, bold=True)
    f.text(ax0 + 20, ay0 + 54, "毫秒到秒级 · 写完立即可用", 12.5, cls="s")
    items = [("情景一次写入", "M8 写入即可检索（HNSW 热层），满足一次学习"),
             ("新概念原型", "一个样例就建原型，互动中追加视角；只有单一视角时 ASK"),
             ("词-物绑定", "拼音 + 声学模板为主键，更新共同注意贝叶斯计数"),
             ("运动示范", "一次示范拟合 sigma-lognormal，多次示范增量更新 ProMP"),
             ("技能 Beta 后验", "慢路成功解进 L2 候选：Beta(2,1)，前 N 次 FAST+VERIFY"),
             ("路由与物理", "River 在线森林、Thompson 统计、物体参数后验")]
    y = ay0 + 76
    for k, (t, d) in enumerate(items):
        f.badge(ax0 + 32, y + 12, str(k + 1), YELLOW, 11, 12)
        f.text(ax0 + 52, y + 17, t, 14, bold=True)
        ls = wrap(d, ax1 - ax0 - 76, 12)
        f.lines(ax0 + 52, y + 37, ls, 12, lh=17, cls="s")
        y += 30 + len(ls) * 17 + 10
    f.rect(ax0 + 16, ay1 - 104, ax1 - ax0 - 32, 88, rx=10, fill="#fff", stroke=tint(YELLOW, 0.6), sw=1.3, dash="5 4")
    f.text(ax0 + 30, ay1 - 78, "微睡眠", 14, bold=True)
    f.text(ax0 + 84, ay1 - 78, "空闲 >30s 时，持续几秒", 12, cls="s")
    f.lines(ax0 + 30, ay1 - 54, ["高优先级重放 · 单条 chunk 编译", "路由树增量更新"], 12, lh=18, cls="s")
    # ---- sleep panel
    sx0, sx1, sy0, sy1 = 500, 1170, 92, 690
    f.rect(sx0, sy0, sx1 - sx0, sy1 - sy0, rx=14, fill=tint(VIOLET, 0.06), stroke=tint(VIOLET, 0.4), sw=1.4)
    icon_moon(f, sx0 + 32, sy0 + 26)
    f.text(sx0 + 52, sy0 + 32, "夜间睡眠 · 巩固", 17, bold=True)
    f.text(sx0 + 20, sy0 + 54, "充电或无人时 · RTX 4090 约 0.5–2 GPU·小时 · Jetson 只做轻量阶段（2–4 小时）", 12.5, cls="s")
    stages = [("优先重放", ["优先级 = 惊奇", "× |奖励| × 社会", "× (1−CI) × 遗忘风险", "新 : 旧 = 1 : 3 交错"]),
              ("原型整理", ["HDBSCAN 合并/拆分", "剔除离群样例", "重校准开集阈值", "与 ACI 共形"]),
              ("编译与蒸馏", ["chunk 编译 + Minton", "LM 解析 → 语法规则", "慢路 → LightGBM", "或 1–5M 小策略网"]),
              ("抽象（Stitch）", ["抽出部首、部件、", "常用笔画组合", "CPU 限时 20–30 分钟"]),
              ("小网络更新", ["投影头 · HCCR", "摊销逆模型 · KWS", "树模型重训 + 校准", "编码器默认冻结"]),
              ("金丝雀门控", ["每项都留测试样例", "（含外部数据）", "任一旧项降 >2%", "→ 回滚该版本"]),
              ("CI 损伤测试", ["CI = 关 HPC 准确率", "÷ 开 HPC 准确率", "≥0.9 且两夜稳定", "→ 已巩固"]),
              ("报告", ["巩固差异报告：", "新增 / 合并 / 拆分", "规则增删 · 回滚记录", "→ 睡眠剧场"])]
    circ = "①②③④⑤⑥⑦⑧"
    ix0, ix1 = sx0 + 18, sx1 - 18
    gw = 16
    bw = (ix1 - ix0 - 3 * gw) / 4
    bh = 132
    top_y, bot_y = sy0 + 78, sy0 + 330
    pos = {}
    for k, (t, d) in enumerate(stages):
        if k < 4:
            x, y = ix0 + k * (bw + gw), top_y
        else:
            x, y = ix0 + (7 - k) * (bw + gw), bot_y
        pos[k] = (x, y)
        f.rect(x, y, bw, bh, rx=10, fill="#fff", stroke=tint(VIOLET, 0.55), sw=1.4)
        f.text(x + 10, y + 25, f"{circ[k]} {t}", 14, bold=True)
        assert all(tw(l, 12) <= bw - 20 for l in d), (t, d)
        f.lines(x + 10, y + 50, d, 12, lh=18, cls="s")
    for k in range(3):
        x, y = pos[k]
        f.arrow(x + bw, y + bh / 2, x + bw + gw - 1, y + bh / 2, VIOLET, 1.8)
    for k in range(4, 7):
        x, y = pos[k]
        f.arrow(x, y + bh / 2, x - gw + 1, y + bh / 2, VIOLET, 1.8)
    x3, y3 = pos[3]
    f.arrow(x3 + bw / 2, y3 + bh, x3 + bw / 2, bot_y - 1, VIOLET, 1.8)
    # center note between rows
    cy0 = top_y + bh
    f.text(ix0 + 4, cy0 + 44, "防遗忘", 13, bold=True)
    f.lines(ix0 + 62, cy0 + 44, ["主干冻结 · 非参数知识只增不改 · 每个概念独立原型与分类头",
                                 "交错重放 · 规则之间只做加法竞争 · 金丝雀门控 + 版本快照"], 12, lh=19, cls="s")
    # rollback chip under ⑥
    x6, y6 = pos[5]
    f.path(f"M{x6+bw/2:.1f},{y6+bh} V{y6+bh+30}", RED, 1.8, dash="4 3", arrow=True)
    f.rect(x6 + 4, y6 + bh + 32, bw - 8, 30, rx=15, fill="#fff", stroke=RED, sw=1.3)
    f.text(x6 + bw / 2, y6 + bh + 52, "回滚到上一版本快照", 12, anchor="middle")
    x7, y7 = pos[6]
    f.path(f"M{x7+bw/2:.1f},{y7+bh} V{y7+bh+30}", GREEN, 1.8, arrow=True)
    f.rect(x7 + 4, y7 + bh + 32, bw - 8, 30, rx=15, fill="#fff", stroke=GREEN, sw=1.3)
    f.text(x7 + bw / 2, y7 + bh + 52, "标为已巩固，可要点化", 12, anchor="middle")
    # ---- links between panels
    x0_, y0_ = pos[0]
    f.arrow(ax1, y0_ + bh / 2, x0_ - 1, y0_ + bh / 2, INK2, 2)
    f.text((ax1 + x0_) / 2, y0_ + bh / 2 - 22, "入睡", 12.5, anchor="middle", bold=True)
    f.text((ax1 + x0_) / 2, y0_ + bh / 2 - 7, "情景 + 日志", 11.5, anchor="middle", cls="s")
    x8, y8 = pos[7]
    f.arrow(x8, y8 + bh / 2, ax1 + 1, y8 + bh / 2, INK2, 2)
    f.text((ax1 + x8) / 2, y8 + bh / 2 - 22, "醒来", 12.5, anchor="middle", bold=True)
    f.text((ax1 + x8) / 2, y8 + bh / 2 - 7, "新版本上线", 11.5, anchor="middle", cls="s")
    f.text(sx0 + 20, sy1 - 20, "“越熟越懂”可测：更快 · 更准 · 更深 · 更省 · 更有自知之明（UD、CI、BWT、ECE、J/task）", 12.5, cls="s")
    return f


# ================================================================ 6. observatory main screen wireframe
def fig_platform():
    W, H = 1200, 924
    f = Fig(W, H, "上帝视角观测台主界面线框")
    f.text(24, 42, "上帝视角观测台：主界面（Live / Replay）线框", 22, bold=True)
    f.text(24, 68, "参考分辨率 1920×1080；所有面板共用一根时间游标，并按 span_id / concept_id / skill_id 联动高亮。", 14, cls="s")
    X0, Y0, FW = 24, 90, 1152
    X1 = X0 + FW
    HB, MH, TH, TB = 62, 372, 262, 40
    MY0 = Y0 + HB
    MY1 = MY0 + MH
    TY1 = MY1 + TH
    FB = TY1 + TB
    f.rect(X0, Y0, FW, FB - Y0, rx=10, fill="#fff", stroke=INK2, sw=1.6)
    # header
    f.rect(X0, Y0, FW, HB, rx=10, fill=PANEL)
    f.rect(X0, Y0 + HB - 10, FW, 10, rx=0, fill=PANEL)
    segs = ["sparrow-A ▾", "模式 [Live | Replay | Compare | Lab]", "刻度 [墙钟 | 周期# | 经历 t_exp]",
            "t_exp 212.4h", "周期 5,540,021"]
    x = X0 + 14
    for s in segs:
        f.text(x, Y0 + 24, s, 12.5)
        x += tw(s, 12.5) + 14
        f.path(f"M{x-7},{Y0+11} V{Y0+29}", GRID, 1.2)
    f.chip(x + 2, Y0 + 9, "AWAKE", 11.5, color=GREEN, bold=True)
    f.text(X0 + 14, Y0 + 49, "KPI：快通道 71% · ECE 0.04 · LM 调用 3.1% · J/task 0.8 · 回滚(7d) 1", 12.5, cls="s")
    f.text(X0 + 560, Y0 + 49, "观测开销 3.8% ● L0+L1", 12.5, cls="s")
    f.rect(X1 - 250, Y0 + 34, 236, 22, rx=11, fill="#fff", stroke=GRID, sw=1.2)
    f.text(X1 - 238, Y0 + 49.5, "⌕ 搜索 概念 / 技能 / episode", 12, cls="m")
    f.path(f"M{X0},{MY0} H{X1}", INK2, 1.2)
    c1 = X0 + FW * 0.28
    c2 = X0 + FW * 0.72
    f.path(f"M{c1:.1f},{MY0} V{MY1} M{c2:.1f},{MY0} V{MY1}", INK2, 1.2)

    def head(x, y, n, s):
        f.badge(x + 11, y - 5, n, BLUE, 11, 12.5)
        if s:
            f.text(x + 28, y, s, 14, bold=True)
    # ---- ① perception lens
    px0, px1 = X0 + 12, c1 - 12
    head(px0, MY0 + 24, "1", "感知透镜 V7（28%）")
    vy = MY0 + 38
    f.rect(px0, vy, px1 - px0, 128, rx=6, fill=PANEL, stroke=GRID, sw=1)
    f.text(px0 + 8, vy + 18, "周边画面", 11.5, cls="m")
    f.path(f"M{px0},{vy+100} H{px1}", GRID, 2)
    f.circle(px0 + 118, vy + 80, 15, fill=tint(ORANGE, 0.35), stroke=ORANGE, sw=1.4)
    f.rect(px0 + 76, vy + 42, 86, 60, rx=3, fill="none", stroke=BLUE, sw=1.6, dash="4 3")
    f.text(px0 + 76, vy + 36, "中央凹 448px · 物体#1734", 11.5, color=INK)
    f.path(f"M{px1-14},{vy+104} L{px0+140},{vy+86}", VIOLET, 1.6, arrow=True)
    f.text(px1 - 10, vy + 122, "指向射线", 11, cls="s", anchor="end")
    f.text(px0, vy + 146, "图层：显著 | 中央凹 | 掩码 | 轨迹 | kNN | OCR | 指向", 11, cls="s")
    ay = vy + 156
    f.rect(px0, ay, px1 - px0, 142, rx=6, fill="#fff", stroke=GRID, sw=1)
    f.text(px0 + 8, ay + 16, "log-mel 频谱 + VAD", 11.5, cls="m")
    ncol, nrow = 36, 8
    cwid = (px1 - px0 - 16) / ncol
    for i in range(ncol):
        for j in range(nrow):
            v = 0.5 + 0.5 * math.sin(i * 0.55 + j * 0.9) * math.cos(i * 0.21 - j * 0.4)
            if 9 <= i <= 27:
                v = min(1, v + 0.25)
            k = max(0, min(12, int(v * 9)))
            f.rect(px0 + 8 + i * cwid, ay + 24 + j * 5.5, cwid - 0.6, 5, rx=0, fill=BLUE_RAMP[k])
    f.rect(px0 + 8 + 9 * cwid, ay + 70, 19 * cwid, 5, rx=2, fill=AQUA)
    f.text(px0 + 8, ay + 94, "ASR：写一个[大]字", 12.5)
    sx = px0 + 8 + tw("ASR：写一个[大]字", 12.5) + 10
    f.text(sx, ay + 94, "姑", 12.5, cls="m")
    f.path(f"M{sx-1},{ay+89.5} h14", MUTED, 1.2)
    f.text(px0 + 8, ay + 114, "F0：da4 ↘ · 端点 ▮ · 撤回窗", 12, cls="s")
    f.text(px0 + 8, ay + 133, "n-best · DTW · 说话人 · 方向", 11.5, cls="m")
    # ---- ② theatre
    tx0, tx1 = c1 + 14, c2 - 14
    head(tx0, MY0 + 24, "2", "意识剧场 V1（44%）")
    cxm = (tx0 + tx1) / 2
    for (dx, dy, s) in [(-1, 0, "竞争：桌子"), (1, 0, "竞争：人手"), (-1, 1, "竞争：姑姑？"), (1, 1, "竞争：预测")]:
        w = tw(s, 12) + 20
        x = tx0 + 4 if dx < 0 else tx1 - w - 4
        y = MY0 + 50 + dy * 78
        f.rect(x, y, w, 26, rx=13, fill="#fff", stroke=MUTED, sw=1.2, dash="4 3")
        f.text(x + w / 2, y + 17.5, s, 12, anchor="middle", cls="s")
    f.rect(cxm - 96, MY0 + 40, 192, 104, rx=10, fill=tint(YELLOW, 0.16), stroke=YELLOW, sw=1.8)
    f.text(cxm, MY0 + 62, "★ 聚光灯联盟", 13.5, anchor="middle", bold=True)
    f.lines(cxm - 70, MY0 + 84, ["词 gu1gu1", "+ 物体 #1734", "+ 指向手势"], 12.5, lh=18)
    ly0 = MY0 + 172
    f.lines(tx0, ly0, ["容量 5/7 · 广播 → M3 M7 M8 M11",
                       "目标栈：ANSWER ▸ WRITE(19) ∥ SAY(十九)",
                       "STN：起笔 t0 ／ 开口 t0",
                       "内心独白（模板渲染）：“白板上是 12+7=，该作答”"], 12.5, lh=21)
    by0 = ly0 + 84
    f.text(tx0, by0 + 10, "意识流 bump chart（最近 10s）", 11.5, cls="m")
    bx0, bx1 = tx0, tx1
    ranks = [[1, 1, 2, 3, 3, 2, 1], [2, 3, 1, 1, 2, 3, 3], [3, 2, 3, 2, 1, 1, 2]]
    for r, col in zip(ranks, [BLUE, ORANGE, AQUA]):
        pts = [(bx0 + 8 + i * (bx1 - bx0 - 16) / 6, by0 + 20 + (v - 1) * 16) for i, v in enumerate(r)]
        f.path("M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts), col, 2)
        for a, b in pts:
            f.circle(a, b, 3, fill=col, extra=f' stroke="#fff" stroke-width="1.5"')
    # ---- ③ decision & output
    dx0, dx1 = c2 + 12, X1 - 12
    head(dx0, MY0 + 24, "3", "决策与输出（28%）")
    ry = MY0 + 38
    f.rect(dx0, ry, dx1 - dx0, 168, rx=8, fill="#fff", stroke=GRID, sw=1.3)
    f.text(dx0 + 10, ry + 20, "路由卡 V2", 12, cls="m")
    f.chip(dx0 + 10, ry + 28, "FAST", 12.5, color=GREEN, fill=tint(GREEN, 0.14), bold=True)
    f.text(dx0 + 78, ry + 46, "p_cal .98 · set=1", 12.5)
    f.lines(dx0 + 10, ry + 72, ["新颖 P12 · Beta 下界 .97", "不确定性：认知 低 / 偶然 低",
                                "CART：有技能≥L2 → 下界≥τ →", "  集合=1 → 新颖<P90 → FAST"], 12, lh=18, cls="s")
    f.chip(dx0 + 10, ry + 138, "为什么不是 SLOW？", 11.5, color=BLUE)
    oy = ry + 180
    f.text(dx0, oy + 4, "输出三窗", 12, cls="m")
    half = (dx1 - dx0 - 10) / 2
    f.rect(dx0, oy + 12, half, 70, rx=6, fill=PANEL, stroke=GRID, sw=1)
    f.text(dx0 + 8, oy + 28, "屏幕 1024×768", 11.5, cls="s")
    f.path(f"M{dx0+30},{oy+66} q20,-26 40,-6 t40,-4", INK2, 1.6)
    f.rect(dx0 + half + 10, oy + 12, half, 70, rx=6, fill=PANEL, stroke=GRID, sw=1)
    f.text(dx0 + half + 18, oy + 28, "手写板：计划/执行/读回", 11, cls="s")
    hx = dx0 + half + 28
    f.path(f"M{hx},{oy+48} h38 M{hx+19},{oy+38} v34 M{hx+19},{oy+52} l-16,18 M{hx+19},{oy+52} l16,18", BLUE, 1.4, dash="3 2")
    f.path(f"M{hx+2},{oy+50} h38 M{hx+21},{oy+40} v34 M{hx+21},{oy+54} l-16,18 M{hx+21},{oy+54} l16,18", INK, 1.8)
    f.rect(dx0, oy + 92, dx1 - dx0, 36, rx=6, fill=PANEL, stroke=GRID, sw=1)
    f.text(dx0 + 8, oy + 115, "扬声器 ▶", 11.5, cls="s")
    wx0 = dx0 + 70
    pts = []
    for i in range(80):
        a = math.sin(i * 0.9) * (6 + 5 * math.sin(i * 0.13))
        pts.append(f"{wx0 + i * (dx1 - dx0 - 84) / 80:.1f},{oy + 110 + a:.1f}")
    f.path("M" + " L".join(pts), AQUA, 1.2)
    # ---- ④ master timeline
    f.path(f"M{X0},{MY1} H{X1}", INK2, 1.2)
    head(X0 + 12, MY1 + 24, "4", "总控时间轴 V0（高 30%，可拉满）")
    cx = X0 + 330
    for s in ["|◀", "▶‖", "▶|", "1x ▾"]:
        w = f.chip(cx, MY1 + 9, s, 11.5, color=GRID)
        cx += w + 6
    cx += 12
    f.text(cx, MY1 + 24, "跳到下一个：", 12, cls="s")
    cx += tw("跳到下一个：", 12) + 4
    for s in ["惊奇", "SLOW", "ASK", "错误", "晋级", "纠正", "书签"]:
        w = f.chip(cx, MY1 + 9, s, 11.5, color=GRID)
        cx += w + 5
    tracks = ["视频缩略", "音频 / ASR", "闸门占空", "工作空间", "▸感觉前端 M0–M2", "▸落地语言 M3–M4", "▸认知骨架 M5–M8",
              "▸专家 M9–M10", "▸效应器 M11–M13", "▸学习社会 M14–M16", "输出 屏 / 声 / 笔", "事件标记"]
    LX1 = X0 + 150
    rowh = 17.5
    ty0 = MY1 + 50
    t0x, t1x = LX1 + 10, X1 - 14
    f.path(f"M{LX1},{ty0-4} V{ty0+len(tracks)*rowh}", GRID, 1)
    T = lambda u: t0x + u * (t1x - t0x)
    for i, name in enumerate(tracks):
        y = ty0 + i * rowh
        f.text(LX1 - 8, y + 13, name, 11.5, anchor="end", cls="s")
        if i % 2 == 0:
            f.rect(LX1 + 1, y, t1x - LX1 + 8, rowh, rx=0, fill="#f8f7f4")
    # track contents (S1 “写一个大字”)
    y = ty0
    for k in range(34):
        f.rect(T(k / 34) + 1, y + 3, (t1x - t0x) / 34 - 3, rowh - 6, rx=1.5, fill=tint(INK2, 0.18))
    y += rowh
    pts = []
    for i in range(160):
        u = i / 159
        amp = 5.5 if 0.14 < u < 0.36 else 1.2
        pts.append(f"{T(u):.1f},{y + 9 + amp * math.sin(i * 1.7):.1f}")
    f.path("M" + " L".join(pts), AQUA, 1.1)
    f.rect(T(0.17), y + 1, tw("写 一 个 大 字", 11) + 10, 16, rx=3, fill="#fff", stroke=AQUA, sw=1)
    f.text(T(0.17) + 5, y + 13, "写 一 个 大 字", 11)
    f.rect(T(0.365), y + 1, 3, 16, rx=0, fill=INK)
    f.rect(T(0.37), y + 3, T(0.42) - T(0.37), 12, rx=2, fill="none", stroke=MUTED, sw=1, dash="2 2")
    y += rowh
    duty = [1, 1, 2, 7, 7, 7, 7, 7, 7, 7, 7, 5, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 2, 2, 1, 1]
    for k, v in enumerate(duty):
        hh = v * 2
        f.rect(T(k / len(duty)) + 1, y + rowh - 2 - hh, (t1x - t0x) / len(duty) - 3, hh, rx=1, fill=BLUE)
    y += rowh
    f.rect(T(0.415), y + 2, tw("WRITE_CHAR 大", 11) + 10, 14, rx=3, fill=tint(YELLOW, 0.2), stroke=YELLOW, sw=1)
    f.text(T(0.415) + 5, y + 13, "WRITE_CHAR 大", 11)
    y += rowh
    lanes = [[(0.02, 0.06, GREEN), (0.14, 0.37, GREEN)], [(0.33, 0.375, GREEN)], [(0.375, 0.385, GREEN)], [],
             [(0.39, 0.66, GREEN)], [(0.68, 0.74, MUTED), (0.80, 0.84, MUTED)]]
    for lane in lanes:
        for a, b, col in lane:
            f.rect(T(a), y + 4, max(3, T(b) - T(a)), rowh - 8, rx=2, fill=col)
        y += rowh
    f.path(f"M{T(0.39):.1f},{y+9} H{T(0.66):.1f}", INK, 3)
    f.text(T(0.67), y + 13, "笔", 11, cls="s")
    f.path(f"M{T(0.45):.1f},{y+9} H{T(0.52):.1f}", AQUA, 3)
    y += rowh
    for u, s in [(0.05, "◆"), (0.37, "↑"), (0.70, "▲")]:
        f.text(T(u), y + 13, s, 11, anchor="middle", cls="s")
    f.text(T(0.72), y + 13, "◆首次  ▲惊奇  ×错误  ↑晋级  ?ASK", 11, cls="m")
    # cursor
    cux = T(0.40)
    f.path(f"M{cux:.1f},{ty0-6} V{ty0+len(tracks)*rowh}", RED, 1.6)
    f.path(f"M{cux-6:.1f},{ty0-12} h12 l-6,7 z", RED, 1, fill=RED)
    # ⑤ tabs
    f.path(f"M{X0},{TY1} H{X1}", INK2, 1.2)
    head(X0 + 12, TY1 + 26, "5", "")
    tabs = ["路由瀑布", "技能成长", "概念", "记忆", "睡眠", "遗忘", "世界模型", "推理", "模块", "经典", "显微镜", "来源",
            "系统(Grafana)"]
    x = X0 + 44
    for i, s in enumerate(tabs):
        w = tw(s, 12) + 20
        f.rect(x, TY1 + 8, w, 24, rx=6, fill=tint(BLUE, 0.14) if i == 0 else PANEL,
               stroke=BLUE if i == 0 else GRID, sw=1.1)
        f.text(x + w / 2, TY1 + 24.5, s, 12, anchor="middle", bold=(i == 0))
        x += w + 6
    # notes
    ny = FB + 28
    f.text(X0, ny, "浮层：在任一输出、卡片或 span 上右键「为什么」→ Why-Trace（V3），从输出一路回溯到原始像素或音频区间。", 12.5, cls="s")
    f.text(X0, ny + 22, "右侧抽屉：「此刻它知道什么」「当时 vs 现在」。红色竖线 = 共用游标，①②③ 同步显示游标时刻的状态。", 12.5, cls="s")
    lgx = X0
    f.text(lgx, ny + 46, "时间轴 span 按路由着色：", 12.5, cls="s")
    lgx += tw("时间轴 span 按路由着色：", 12.5) + 6
    for nm, col in [("FAST", GREEN), ("FAST+VERIFY", YELLOW), ("SLOW", ORANGE), ("ASK", VIOLET), ("后台学习 / 睡眠", MUTED)]:
        f.rect(lgx, ny + 35, 12, 12, rx=2, fill=col)
        f.text(lgx + 17, ny + 46, nm, 12.5, cls="s")
        lgx += 17 + tw(nm, 12.5) + 18
    return f


# ================================================================ 7. telemetry pipeline
def fig_telemetry():
    W, H = 1260, 680
    f = Fig(W, H, "遥测管线：从模块事件到观测视图")
    f.text(24, 42, "遥测管线：从模块事件到观测视图（单向玻璃）", 22, bold=True)
    f.text(24, 68, "平台对雀脑严格只读；回放由消息全序日志 + 快照驱动；实验者只能碰快照副本。", 14, cls="s")
    Y0, Y1 = 96, 486
    MIDY = 290
    stages = [(24, 184), (224, 452), (492, 600), (640, 872), (912, 1084), (1124, 1236)]

    def box(i, n, title, fill="#fff", stroke=INK2, dash=None):
        x0, x1 = stages[i]
        f.rect(x0, Y0, x1 - x0, Y1 - Y0, rx=12, fill=fill, stroke=stroke, sw=1.5, dash=dash)
        f.badge(x0 + 20, Y0 + 24, n, BLUE, 11, 12.5)
        f.text(x0 + 38, Y0 + 29, title, 14, bold=True)
        return x0 + 14, x1 - 14
    # ① modules
    a, b = box(0, "1", "雀脑模块")
    for i in range(6):
        y = Y0 + 48 + i * 36
        f.rect(a, y, b - a, 28, rx=6, fill=tint(CAT[i], 0.18))
        f.text(a + 8, y + 18.5, LAYER_NAMES[i] if i < 5 else "学习 · 社会", 12)
        f.text(b - 6, y + 18.5, LAYER_MODS[i] if i < 5 else "M14–M16", 11, anchor="end", cls="s")
    f.text(a, Y0 + 290, "smart-obs SDK", 12.5, bold=True)
    f.lines(a, Y0 + 310, ["emit()", "span()", "conf_contract()"], 11.5, lh=17, mono=True, cls="s")
    f.text(a, Y1 - 14, "写一次约 1–2µs", 11.5, cls="m")
    # ② envelope
    a, b = box(1, "2", "事件信封（统一 schema）")
    fields = [("seq · span_id", "全序号 · 片段 ID"),
              ("parent_ids", "因果父 ID → Why-Trace 回溯"),
              ("class", None),
              ("conf", "置信度契约：7 个统一字段"),
              ("module_ver · kb_ver", "版本号，回放时重建状态"),
              ("origin", "来源四色：先天 · 示范 · 自我 · 实验者"),
              ("clocks", "t_mono · cycle_id · t_exp · 帧号")]
    y = Y0 + 58
    for k, d in fields:
        f.text(a, y, k, 12, mono=True, bold=True)
        if d:
            ls = wrap_items(d.split(" · "), b - a, 11.5)
            f.lines(a, y + 17, ls, 11.5, lh=16, cls="s")
            y += 17 + len(ls) * 16 + 7
        else:
            f.text(a + tw("class", 12) + 18, y, "7 类", 11.5, cls="s")
            kinds = ["percept", "hypothesis", "decision", "action", "outcome", "learn", "consolidate"]
            cx, cy = a, y + 8
            for s in kinds:
                w = tw(s, 11) * 1.05 + 12
                if cx + w > b:
                    cx, cy = a, cy + 22
                f.rect(cx, cy, w, 18, rx=9, fill=tint(BLUE, 0.12))
                f.text(cx + w / 2, cy + 13, s, 11, anchor="middle", mono=True)
                cx += w + 5
            y = cy + 18 + 22
    # ③ tap (one-way glass)
    x0, x1 = stages[2]
    f.rect(x0, Y0, x1 - x0, Y1 - Y0, rx=12, fill=tint(AQUA, 0.10), stroke=AQUA, sw=1.5)
    yy = Y0 + 150
    while yy + 26 <= Y1 - 110:
        f.path(f"M{x0+10},{yy+26} L{x1-10},{yy}", "#ffffff", 5, cap="butt")
        yy += 40
    f.badge(x0 + 20, Y0 + 24, "3", BLUE, 11, 12.5)
    f.text(x0 + 38, Y0 + 29, "总线 tap", 14, bold=True)
    f.rect(x0 + 8, Y0 + 44, x1 - x0 - 16, 88, rx=8, fill="#fff")
    f.lines(x0 + 16, Y0 + 64, ["ZeroMQ", "PUB → SUB", "订阅 M5 黑板", "seq 已分配"], 11.5, lh=17)
    f.rect(x0 + 8, Y0 + 300, x1 - x0 - 16, 72, rx=8, fill="#fff")
    f.text((x0 + x1) / 2, Y0 + 322, "单向玻璃", 13.5, anchor="middle", bold=True)
    f.lines((x0 + x1) / 2, Y0 + 342, ["只出不进", "旁路近零成本"], 11.5, lh=17, anchor="middle", cls="s")
    # ④ recorder
    a, b = box(3, "4", "Recorder 旁路进程")
    recs = [("事件", "events.jsonl", "→ Parquet，每分钟滚动一个文件"),
            ("帧", "MCAP：周边视频", "+ 中央凹裁剪（模型实际输入）"),
            ("音频", "FLAC / Opus", "AEC 后 + 原始双声道 + 扬声器参考"),
            ("快照", "每次睡眠后", "小网络权重 · 规则库 · 技能表 · 概念库"),
            ("飞行记录", "30s 视听环形缓冲", "L2 触发时落盘前后片段")]
    y = Y0 + 50
    for k, main, sub in recs:
        f.rect(a, y, 52, 20, rx=10, fill=tint(ORANGE, 0.16))
        f.text(a + 26, y + 14.5, k, 11, anchor="middle")
        f.text(a + 60, y + 15, main, 12, bold=True, mono=main.startswith("events"))
        ls = wrap(sub, b - a, 11.5)
        f.lines(a, y + 38, ls, 11.5, lh=16, cls="s")
        y += 38 + len(ls) * 16 + 6
    f.text(a, Y1 - 14, "nice 19 · 与雀脑进程隔离", 11.5, cls="m")
    # ⑤ store / query
    a, b = box(4, "5", "存储与查询")
    sto = [("DuckDB", "SQL 查事件（Parquet 湖）"), ("LanceDB", "向量 · as-of 查询"), ("blob 库", "blake3 内容寻址"),
           ("state-at-t", "快照 + 重放 learn 事件，seek <500ms"), ("回放", "R1 日志 · R2 重执行 · R3 分叉")]
    y = Y0 + 58
    for k, d in sto:
        f.text(a, y, k, 12.5, bold=True, mono=k.isascii())
        ls = wrap_items(d.split(" · "), b - a, 11.5)
        f.lines(a, y + 18, ls, 11.5, lh=16, cls="s")
        y += 18 + len(ls) * 16 + 12
    # ⑥ views
    a, b = box(5, "6", "视图")
    views = ["婴儿监视器", "意识剧场", "路由瀑布", "Why-Trace", "概念卡片", "技能成长", "睡眠剧场", "反事实实验室", "算力账本"]
    for k, s in enumerate(views):
        y = Y0 + 46 + k * 34
        f.rect(a, y, b - a, 26, rx=6, fill=PANEL)
        f.text(a + 8, y + 17.5, s, 12)
    # arrows between stages
    for i in range(5):
        f.arrow(stages[i][1] + 2, MIDY, stages[i + 1][0] - 2, MIDY, INK2, 2.2)
    # no way back through the glass
    gx0, gx1 = stages[1][1], stages[2][0]
    f.path(f"M{gx1-2},{MIDY+36} H{gx0+4}", RED, 1.6, dash="3 3", arrow=True)
    f.text((gx0 + gx1) / 2, MIDY + 32, "✕", 15, anchor="middle", bold=True, color=RED)
    # ---- experimenter channel
    ey = 540
    vx = (stages[5][0] + stages[5][1]) / 2
    f.path(f"M{vx:.1f},{Y1} V{ey+30} H{1062}", MUTED, 1.8, dash="6 4", arrow=True)
    f.text(1086, ey + 58, "实验者通道", 13, bold=True)
    f.text(1086, ey + 77, "暂停 · 编辑 · 干预 · 标注", 11.5, cls="s")
    f.rect(800, ey, 260, 60, rx=10, fill=PANEL, stroke=MUTED, sw=1.4, dash="5 4")
    f.text(814, ey + 24, "快照副本（沙箱）", 13.5, bold=True)
    f.text(814, ey + 44, "R3 分叉推演，结果只写 LAB 子 episode", 11.5, cls="s")
    f.path(f"M800,{ey+30} H356", RED, 1.8, dash="6 4", arrow=True)
    f.circle(578, ey + 30, 12, fill=BG)
    f.text(578, ey + 36.5, "✕", 18, anchor="middle", bold=True, color=RED)
    f.text(578, ey + 60, "不写入任何学习存储（origin=experimenter · phase=LAB）", 12, anchor="middle", cls="s")
    f.rect(24, ey, 330, 60, rx=10, fill="#fff", stroke=INK2, sw=1.4)
    f.text(38, ey + 24, "雀脑的记忆 / 技能 / 概念库", 13.5, bold=True)
    f.text(38, ey + 44, "教学反馈只能由人经摄像头和麦克风给出", 11.5, cls="s")
    f.text(24, H - 20, "设备端只跑采集与 Recorder；分析、回放和 UI 在工作站。事件 Protobuf → Arrow IPC → Parquet；原始音视频与三路输出写 MCAP。",
           12, cls="m")
    return f


# ================================================================ 8. roadmap
def fig_roadmap():
    W = 1280
    stages = [
        (0, 6, "第 1–6 周", "身体与观测底座",
         "虚拟书桌模拟器 · 事件 schema（因果父 ID） · ZeroMQ + Parquet/DuckDB + Rerun · 参数与许可证台账接 CI · 先天清单 v0",
         "门槛", "婴儿监视器能回放 · 任一输出能回溯到输入"),
        (6, 14, "第 6–14 周", "S4 端到端：感知 + 输出 + 闭环",
         "VAD · KWS · Zipformer · DINOv2 · EdgeSAM · PP-OCRv5 · Matcha + Vocos · 书写完成检测 · 读回与自听",
         "门槛", "白板题正确率 ≥95% · 作答 p50 ≤0.7s · 因果追踪可用"),
        (14, 22, "第 14–22 周", "S1 与熟练化",
         "示范学习（HMM → iDeLog → ProMP） · 身体图式 · Soar/CLIPS chunking · L0–L3 晋级 · CART 路由",
         "门槛", "500 字×20 次后 L2 覆盖 ≥90% · 快路精确率 ≥98% · 决策 p50 <10ms"),
        (22, 32, "第 22–32 周", "S2 少样本概念",
         "物体提议 · 指向消歧 · 新词发现 · 共同注意贝叶斯 · 落地束 · 线稿绘画 · 社会反馈",
         "门槛", "两次命名后绑定 ≥85% · 画作 5 选 1 辨认 ≥70%"),
        (32, 38, "第 32–38 周", "S3 世界模型",
         "MOG2/Hough 测量 · IMM · 解析积分 · 修正版 pymunk · 惊奇 · 屏幕物理沙盒 · QPT 叙述",
         "门槛", "+1s 位置误差中位数 ≤1 个球径 · 90% 预测带覆盖 85–95%"),
        (38, 46, "第 38–46 周", "睡眠 v1 与慢通道",
         "分层存储 · 交错重放 · 编译蒸馏 · Stitch · 金丝雀回滚 · CI 损伤测试 · Qwen 解析 · ACI 共形",
         "门槛", "30 天生活流 BWT ≥ −2% · 熟悉领域 LM 调用 <5%"),
        (46, 52, "第 46–52 周", "真机与边缘设备",
         "Orin NX TensorRT INT8 · 纯 CPU 模式 · 真人教学 sim-to-real（按天 / 周计） · 3–4 人团队总计约 12 个月",
         "交付", "SMART 基准（30 天生活流 + S1–S4） · 开源代码 · 观测台 · 数据生成器"),
        (52, None, "持续", "研究线",
         "发音合成与咿呀学语 · 表征条件图像生成 · JEPA 式世界模型残差 · 任务图式归纳",
         "门槛", "SMART 基准上显著胜过现有组件 · 不破 1B 与延迟预算"),
    ]
    AX0, AX1, ZEND = 60, 1060, 1250
    X = lambda wk: AX0 + wk * (AX1 - AX0) / 52
    CW = 248
    pad = 12

    def layout(s):
        body = wrap_items(s[4].split(" · "), CW - 2 * pad, 11.5)
        gate = wrap_items(s[6].split(" · "), CW - 2 * pad - 40, 11.5)
        return body, gate
    lay = [layout(s) for s in stages]
    heights = [16 + 20 + 26 + len(b) * 16 + 12 + len(g) * 16 + 10 for b, g in lay]
    hup = max(heights[i] for i in range(0, 8, 2))
    hdn = max(heights[i] for i in range(1, 8, 2))
    TOP = 96
    AXY = TOP + hup + 36
    DTOP = AXY + 40
    H = int(DTOP + hdn + 50)
    f = Fig(W, H, "分阶段路线图：阶段 0 到阶段 7")
    f.text(40, 42, "分阶段路线图：约 12 个月（3–4 人团队）", 22, bold=True)
    f.text(40, 68, "每个阶段都有准入门槛；阶段 7 是持续的研究线，并入主干前必须在 SMART 基准上胜出。", 14, cls="s")
    # axis
    for i, s in enumerate(stages):
        a, b = s[0], s[1]
        col = CAT[i]
        if b is None:
            f.rect(X(a) + 1, AXY - 7, ZEND - X(a) - 12, 14, rx=3, fill=tint(col, 0.35))
            f.path(f"M{X(a)+1},{AXY} H{ZEND}", col, 2, dash="6 4", arrow=True)
        else:
            f.rect(X(a) + 1, AXY - 7, X(b) - X(a) - 2, 14, rx=3, fill=col)
    for wk in [0, 6, 14, 22, 32, 38, 46, 52]:
        f.path(f"M{X(wk):.1f},{AXY+9} V{AXY+15}", MUTED, 1.2)
        f.text(X(wk), AXY + 29, f"{wk}", 11.5, anchor="middle", cls="m")
    f.text(AX0 - 10, AXY + 29, "周", 11.5, anchor="end", cls="m")
    # cards
    placed = []
    for i, (s, (body, gate)) in enumerate(zip(stages, lay)):
        a, b = s[0], s[1]
        mid = (X(a) + X(b)) / 2 if b is not None else X(a) + 70
        x = min(max(mid - CW / 2, 24), W - 24 - CW)
        up = i % 2 == 0
        h = hup if up else hdn
        y = TOP if up else DTOP
        for (px, py) in placed:
            assert py != y or abs(px - x) >= CW + 6, (i, x, px)
        placed.append((x, y))
        col = CAT[i]
        if up:
            f.path(f"M{mid:.1f},{y+h} V{AXY-8}", col, 1.6)
        else:
            f.path(f"M{mid:.1f},{AXY+8} V{y}", col, 1.6)
        f.rect(x, y, CW, h, rx=10, fill="#fff", stroke=tint(col, 0.6), sw=1.4)
        f.rect(x, y, CW, 6, rx=3, fill=col)
        f.text(x + pad, y + 28, f"阶段 {i}", 12.5, bold=True)
        f.text(x + CW - pad, y + 28, s[2], 12, anchor="end", cls="s")
        f.text(x + pad, y + 51, s[3], 14.5, bold=True)
        yy = f.lines(x + pad, y + 72, body, 11.5, lh=16, cls="s")
        gy = yy + 8
        f.rect(x + pad, gy - 1, 34, 18, rx=9, fill=tint(col, 0.2))
        f.text(x + pad + 17, gy + 12, s[5], 11, anchor="middle", bold=True)
        f.lines(x + pad + 40, gy + 12, gate, 11.5, lh=16)
    f.text(X(52) + 4, AXY - 14, "≈ 12 个月", 12, bold=True)
    return f


FIGS = [
    ("01-routes-scores.svg", fig_routes),
    ("02-architecture.svg", fig_architecture),
    ("02-io-body.svg", fig_io_body),
    ("02-fast-slow-ladder.svg", fig_ladder),
    ("02-learning-loop.svg", fig_learning),
    ("03-platform-layout.svg", fig_platform),
    ("03-telemetry-pipeline.svg", fig_telemetry),
    ("04-roadmap.svg", fig_roadmap),
]

if __name__ == "__main__":
    for name, fn in FIGS:
        save(name, fn())
    print("ok")
