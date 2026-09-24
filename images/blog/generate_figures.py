"""生成《通用人工智能科普系列》博文配图（SVG）。用法：python3 images/blog/generate_figures.py"""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif"
BG = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
VIOLET = "#4a3aa7"
YELLOW = "#eda100"
RED = "#e34948"


def svg(w, h, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">
<title>{title}</title>
<style>text{{font-family:{FONT};fill:{INK}}} .s{{fill:{INK2}}} .m{{fill:{MUTED}}}</style>
<rect width="{w}" height="{h}" rx="12" fill="{BG}"/>
{body}
</svg>
'''


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


def catmull(points):
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


# ---------------------------------------------------------------- 1. narrow vs general
def narrow_vs_general():
    b = []
    b.append(f'<text x="210" y="46" font-size="22" font-weight="700" text-anchor="middle">专用人工智能（今天的大多数 AI）</text>')
    b.append(f'<text x="210" y="72" font-size="14" class="s" text-anchor="middle">一个模型只会一件事，换个任务就要重新造</text>')
    items = [("♟", "下棋 AI", "只会下棋"), ("🔤", "翻译 AI", "只会翻译"), ("👁", "识图 AI", "只会认图"), ("🎙", "语音 AI", "只会听写")]
    for i, (ic, name, sub) in enumerate(items):
        x = 40 + (i % 2) * 180
        y = 100 + (i // 2) * 130
        b.append(f'<rect x="{x}" y="{y}" width="160" height="110" rx="10" fill="#fff" stroke="{GRID}" stroke-width="2"/>')
        b.append(f'<text x="{x+80}" y="{y+44}" font-size="30" text-anchor="middle">{ic}</text>')
        b.append(f'<text x="{x+80}" y="{y+76}" font-size="16" font-weight="700" text-anchor="middle">{name}</text>')
        b.append(f'<text x="{x+80}" y="{y+97}" font-size="13" class="s" text-anchor="middle">{sub}</text>')
    b.append(f'<line x1="420" y1="40" x2="420" y2="380" stroke="{GRID}" stroke-width="2" stroke-dasharray="6 6"/>')
    cx, cy = 630, 230
    b.append(f'<text x="{cx}" y="46" font-size="22" font-weight="700" text-anchor="middle">通用人工智能（AGI）</text>')
    b.append(f'<text x="{cx}" y="72" font-size="14" class="s" text-anchor="middle">一个“大脑”，能学会、迁移、组合各种本领</text>')
    tasks = ["下棋", "翻译", "看图", "听说", "写代码", "做数学", "画画", "做实验", "操作机器人", "规划任务"]
    r = 125
    for i, t in enumerate(tasks):
        a = -math.pi / 2 + i * 2 * math.pi / len(tasks)
        tx, ty = cx + r * math.cos(a), cy + 12 + r * math.sin(a)
        b.append(f'<line x1="{cx}" y1="{cy+12}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{BLUE}" stroke-opacity=".35" stroke-width="2"/>')
        w = 16 * len(t) + 20
        b.append(f'<rect x="{tx-w/2:.1f}" y="{ty-15:.1f}" width="{w}" height="30" rx="15" fill="#fff" stroke="{BLUE}" stroke-width="1.5"/>')
        b.append(f'<text x="{tx:.1f}" y="{ty+5:.1f}" font-size="14" text-anchor="middle">{t}</text>')
    b.append(f'<circle cx="{cx}" cy="{cy+12}" r="46" fill="{BLUE}"/>')
    b.append(f'<text x="{cx}" y="{cy+6}" font-size="26" text-anchor="middle" style="fill:#fff">🧠</text>')
    b.append(f'<text x="{cx}" y="{cy+32}" font-size="13" text-anchor="middle" style="fill:#fff" font-weight="700">通用大脑</text>')
    return svg(840, 400, "\n".join(b), "专用人工智能与通用人工智能对比")


# ---------------------------------------------------------------- 2. timeline with summers and winters
def timeline():
    W, H = 1100, 560
    x0, x1 = 70, 1060
    base = 470

    def X(y):
        return x0 + (y - 1950) * (x1 - x0) / (2026 - 1950)

    b = []
    b.append(f'<text x="{W/2}" y="40" font-size="24" font-weight="700" text-anchor="middle">人工智能 70 年：三次高潮与两次寒冬</text>')
    b.append(f'<text x="{W/2}" y="66" font-size="14" class="s" text-anchor="middle">曲线表示社会关注度与投入的大致起伏（示意，非精确数据）</text>')
    for a, z, lab in [(1974, 1980, "第一次寒冬"), (1987, 1993, "第二次寒冬")]:
        b.append(f'<rect x="{X(a):.1f}" y="90" width="{X(z)-X(a):.1f}" height="{base-90}" fill="#dfe8f3"/>')
        b.append(f'<text x="{(X(a)+X(z))/2:.1f}" y="112" font-size="14" text-anchor="middle" class="s">❄ {lab}</text>')
    for y in range(1950, 2030, 10):
        if y > 2026:
            break
        b.append(f'<line x1="{X(y):.1f}" y1="{base}" x2="{X(y):.1f}" y2="{base+6}" stroke="{MUTED}"/>')
        b.append(f'<text x="{X(y):.1f}" y="{base+24}" font-size="13" class="m" text-anchor="middle">{y}</text>')
    b.append(f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{MUTED}" stroke-width="1.5"/>')
    pts = [(1950, 400), (1956, 330), (1966, 250), (1972, 330), (1977, 420), (1982, 330), (1985, 270),
           (1988, 380), (1992, 420), (1997, 370), (2006, 350), (2012, 290), (2016, 230), (2020, 180),
           (2022, 130), (2024, 105), (2026, 95)]
    P = [(X(a), c) for a, c in pts]
    d = catmull(P)
    b.append(f'<path d="{d} L{X(2026):.1f},{base} L{X(1950):.1f},{base} Z" fill="{BLUE}" fill-opacity=".10"/>')
    b.append(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linecap="round"/>')
    b.append(f'<text x="{X(1962):.1f}" y="222" font-size="15" font-weight="700" text-anchor="middle" style="fill:{BLUE}">第一次高潮：符号推理</text>')
    b.append(f'<text x="{X(1984):.1f}" y="244" font-size="15" font-weight="700" text-anchor="middle" style="fill:{BLUE}">第二次：专家系统</text>')
    b.append(f'<text x="{X(2008):.1f}" y="150" font-size="15" font-weight="700" text-anchor="middle" style="fill:{BLUE}">第三次：深度学习 → 大模型</text>')

    events = [(1950, "图灵测试", 400, -1), (1956, "达特茅斯会议", 330, 1), (1958, "感知机", 300, -1),
              (1966, "ELIZA", 250, 1), (1986, "反向传播", 300, 1), (1997, "深蓝胜卡斯帕罗夫", 370, -1),
              (2012, "AlexNet", 290, 1), (2016, "AlphaGo", 230, 1), (2017, "Transformer", 215, -1),
              (2020, "GPT-3", 180, 1), (2022, "ChatGPT", 130, -1), (2024, "推理模型", 105, 1)]
    events = [(y, n, c, s) for y, n, c, s in events]
    samples = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        for k in range(101):
            t = k / 100
            mt = 1 - t
            samples.append((mt**3*p1[0]+3*mt*mt*t*c1[0]+3*mt*t*t*c2[0]+t**3*p2[0],
                            mt**3*p1[1]+3*mt*mt*t*c1[1]+3*mt*t*t*c2[1]+t**3*p2[1]))
    def onCurve(x):
        return min(samples, key=lambda s: abs(s[0] - x))[1]
    for yr, name, _cy, side in events:
        x = X(yr)
        cy = onCurve(x)
        # nudge dot to curve roughly
        b.append(f'<circle cx="{x:.1f}" cy="{cy}" r="5" fill="#fff" stroke="{ORANGE}" stroke-width="2.5"/>')
        ly = cy + (34 if side > 0 else -14)
        if side > 0:
            b.append(f'<line x1="{x:.1f}" y1="{cy+6}" x2="{x:.1f}" y2="{ly-14}" stroke="{MUTED}" stroke-width="1"/>')
        anchor = "middle"
        if yr in (2017, 2022):
            anchor = "end"; x -= 10; ly = cy + 5
        if yr == 2024:
            ly = cy + 48
            b.append(f'<line x1="{x:.1f}" y1="{cy+6:.1f}" x2="{x:.1f}" y2="{ly-14:.1f}" stroke="{MUTED}" stroke-width="1"/>')
        b.append(f'<text x="{x:.1f}" y="{ly}" font-size="13" text-anchor="{anchor}">{name}</text>')
    b.append(f'<text x="{x0}" y="{H-20}" font-size="12" class="m">橙色圆点：里程碑事件</text>')
    return svg(W, H, "\n".join(b), "人工智能发展时间线：三次高潮与两次寒冬")


# ---------------------------------------------------------------- 3. parameter growth (log scale bars)
def params():
    W, H = 900, 480
    data = [("GPT-1", "2018", 1.17e8, "1.17 亿"), ("GPT-2", "2019", 1.5e9, "15 亿"),
            ("GPT-3", "2020", 1.75e11, "1750 亿"), ("PaLM", "2022", 5.4e11, "5400 亿"),
            ("Llama 3.1", "2024", 4.05e11, "4050 亿"), ("DeepSeek-V3", "2024", 6.71e11, "6710 亿*")]
    top, bot = 100, 390
    lo, hi = 8, 12
    def Y(v):
        return bot - (math.log10(v) - lo) / (hi - lo) * (bot - top)
    b = []
    b.append(f'<text x="60" y="44" font-size="22" font-weight="700">公开的大语言模型参数量（对数刻度）</text>')
    b.append(f'<text x="60" y="70" font-size="14" class="s">六年间，模型规模增长了数千倍；纵轴每一格代表 10 倍</text>')
    labels = {8: "1 亿", 9: "10 亿", 10: "100 亿", 11: "1000 亿", 12: "1 万亿"}
    for e in range(lo, hi + 1):
        y = Y(10 ** e)
        b.append(f'<line x1="100" y1="{y:.1f}" x2="860" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        b.append(f'<text x="90" y="{y+4:.1f}" font-size="12" class="m" text-anchor="end">{labels[e]}</text>')
    bw = 70
    step = 760 / len(data)
    for i, (n, yr, v, lab) in enumerate(data):
        cx = 100 + step * (i + .5)
        y = Y(v)
        h = bot - y
        b.append(f'<path d="M{cx-bw/2:.1f},{bot} V{y+4:.1f} Q{cx-bw/2:.1f},{y:.1f} {cx-bw/2+4:.1f},{y:.1f} H{cx+bw/2-4:.1f} Q{cx+bw/2:.1f},{y:.1f} {cx+bw/2:.1f},{y+4:.1f} V{bot} Z" fill="{BLUE}"/>')
        b.append(f'<text x="{cx:.1f}" y="{y-10:.1f}" font-size="14" font-weight="700" text-anchor="middle">{lab}</text>')
        b.append(f'<text x="{cx:.1f}" y="{bot+22}" font-size="14" text-anchor="middle">{n}</text>')
        b.append(f'<text x="{cx:.1f}" y="{bot+40}" font-size="12" class="m" text-anchor="middle">{yr}</text>')
    b.append(f'<line x1="100" y1="{bot}" x2="860" y2="{bot}" stroke="{MUTED}" stroke-width="1.5"/>')
    b.append(f'<text x="60" y="{H-18}" font-size="12" class="m">* DeepSeek-V3 为“混合专家”结构，每次只激活约 370 亿参数。2023 年后多家头部闭源模型不再公布参数量，故未列出。</text>')
    return svg(W, H, "\n".join(b), "大语言模型参数量增长")


# ---------------------------------------------------------------- 4. next token prediction
def next_token():
    W, H = 900, 360
    b = []
    b.append(f'<text x="{W/2}" y="42" font-size="22" font-weight="700" text-anchor="middle">大语言模型在做什么？——“猜下一个字”</text>')
    # input
    toks = ["今", "天", "天", "气", "真"]
    for i, t in enumerate(toks):
        x = 40 + i * 52
        b.append(f'<rect x="{x}" y="150" width="44" height="44" rx="8" fill="#fff" stroke="{INK2}" stroke-width="1.5"/>')
        b.append(f'<text x="{x+22}" y="179" font-size="20" text-anchor="middle">{t}</text>')
    b.append(f'<text x="165" y="226" font-size="13" class="s" text-anchor="middle">输入：已经写出的文字</text>')
    b.append(f'<path d="M310,172 H360" stroke="{MUTED}" stroke-width="2" marker-end="url(#ar)"/>')
    b.append(f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')
    b.append(f'<rect x="370" y="110" width="170" height="124" rx="14" fill="{BLUE}"/>')
    b.append(f'<text x="455" y="160" font-size="18" font-weight="700" text-anchor="middle" style="fill:#fff">神经网络</text>')
    b.append(f'<text x="455" y="186" font-size="13" text-anchor="middle" style="fill:#fff">（千亿个可调旋钮）</text>')
    b.append(f'<text x="455" y="208" font-size="13" text-anchor="middle" style="fill:#fff">Transformer</text>')
    b.append(f'<path d="M548,172 H598" stroke="{MUTED}" stroke-width="2" marker-end="url(#ar)"/>')
    probs = [("好", .62), ("不", .15), ("热", .09), ("冷", .06), ("…", .08)]
    for i, (t, p) in enumerate(probs):
        y = 100 + i * 36
        b.append(f'<text x="625" y="{y+19}" font-size="18" text-anchor="middle">{t}</text>')
        w = p * 330
        b.append(f'<rect x="645" y="{y+4}" width="{w:.1f}" height="20" rx="4" fill="{BLUE if i==0 else "#a9c6ea"}"/>')
        b.append(f'<text x="{645+w+8:.1f}" y="{y+19}" font-size="13" class="s">{int(p*100)}%</text>')
    b.append(f'<text x="740" y="296" font-size="13" class="s" text-anchor="middle">输出：下一个字的概率（示意）</text>')
    b.append(f'<text x="{W/2}" y="334" font-size="14" text-anchor="middle">选出“好”，接到句尾，再猜下一个字……一个字一个字地“接龙”，就写出了整段回答。</text>')
    return svg(W, H, "\n".join(b), "大语言模型预测下一个字的示意图")


# ---------------------------------------------------------------- 5. levels of AGI
def levels():
    W, H = 920, 450
    lv = [("L0", "无 AI", ["计算器、编译器"]),
          ("L1", "初现", ["与普通人相当或略好", "", "例：2023 年的", "ChatGPT、Llama 2"]),
          ("L2", "胜任", ["超过 50% 的", "熟练成年人"]),
          ("L3", "专家", ["超过 90% 的", "熟练成年人"]),
          ("L4", "大师", ["超过 99% 的", "熟练成年人"]),
          ("L5", "超人", ["超过所有人类", "", "专用领域已有：", "AlphaFold、AlphaZero"])]
    b = []
    b.append(f'<text x="40" y="44" font-size="22" font-weight="700">AGI 的“段位”：Google DeepMind 提出的 6 个等级</text>')
    b.append(f'<text x="40" y="70" font-size="14" class="s">来源：Morris 等《Levels of AGI》（2023），按“超过多少比例的熟练成年人”分级；示例为论文发表时的判断。</text>')
    shades = ["#e9f1fb", "#d3e3f6", "#a9c6ea", "#7eaae0", "#5590d8", BLUE]
    for i, (code, name, lines) in enumerate(lv):
        x = 40 + i * 142
        h = 90 + i * 52
        y = 420 - h
        b.append(f'<rect x="{x}" y="{y}" width="134" height="{h}" rx="8" fill="{shades[i]}"/>')
        tc = "#fff" if i >= 3 else INK
        b.append(f'<text x="{x+67}" y="{y+28}" font-size="18" font-weight="700" text-anchor="middle" style="fill:{tc}">{code} {name}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{x+67}" y="{y+52+j*18}" font-size="12" text-anchor="middle" style="fill:{tc}">{ln}</text>')
    return svg(W, H, "\n".join(b), "AGI 分级示意图")


# ---------------------------------------------------------------- 6. jagged frontier
def jagged():
    W, H = 900, 560
    cx, cy = 330, 310
    skills = [("写作", 1.25), ("编程", 1.3), ("数学竞赛", 1.3), ("知识问答", 1.4), ("翻译", 1.25),
              ("长期规划", .65), ("持续学习", .45), ("物理操作", .35), ("常识推理", .85), ("看图理解", 1.0),
              ("可靠不出错", .6), ("自知之明", .6)]
    R = 120
    n = len(skills)
    b = []
    b.append(f'<text x="40" y="44" font-size="22" font-weight="700">“参差不齐”的能力边界</text>')
    b.append(f'<text x="40" y="70" font-size="14" class="s">今天的 AI：有些方面远超常人，有些方面还不如小孩（示意图）</text>')
    for k in (0.5, 1.0, 1.5):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{R*k}" fill="none" stroke="{GRID}"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    pts = []
    for i, (name, v) in enumerate(skills):
        a = -math.pi / 2 + i * 2 * math.pi / n
        pts.append((cx + R * v * math.cos(a), cy + R * v * math.sin(a)))
        lx, ly = cx + (R * 1.5 + 22) * math.cos(a), cy + (R * 1.5 + 22) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + R*1.5*math.cos(a):.1f}" y2="{cy + R*1.5*math.sin(a):.1f}" stroke="{GRID}"/>')
        b.append(f'<text x="{lx:.1f}" y="{ly+5:.1f}" font-size="14" text-anchor="{anchor}">{name}</text>')
    b.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f' Z" fill="{BLUE}" fill-opacity=".18" stroke="{BLUE}" stroke-width="2.5" stroke-linejoin="round"/>')
    # legend
    lx = 620
    b.append(f'<line x1="{lx}" y1="200" x2="{lx+40}" y2="200" stroke="{ORANGE}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    b.append(f'<text x="{lx+50}" y="205" font-size="14">普通成年人水平</text>')
    b.append(f'<rect x="{lx}" y="228" width="40" height="18" fill="{BLUE}" fill-opacity=".18" stroke="{BLUE}" stroke-width="2"/>')
    b.append(f'<text x="{lx+50}" y="242" font-size="14">当前大模型（大致）</text>')
    b.append(f'<text x="{lx}" y="300" font-size="13" class="s">伸出圆圈 = 超过常人</text>')
    b.append(f'<text x="{lx}" y="322" font-size="13" class="s">缩在圆内 = 仍有差距</text>')
    b.append(f'<text x="{lx}" y="360" font-size="13" class="s">AGI 需要把凹进去的</text>')
    b.append(f'<text x="{lx}" y="382" font-size="13" class="s">部分都补齐</text>')
    return svg(W, H, "\n".join(b), "当前 AI 能力参差不齐的示意雷达图")


# ---------------------------------------------------------------- 7. future paths
def paths():
    W, H = 960, 500
    b = []
    b.append(f'<defs><marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')
    b.append(f'<text x="40" y="44" font-size="22" font-weight="700">通往 AGI 的几条路（它们并不互斥）</text>')
    routes = [("📈", "规模扩展", "更多数据、算力、参数", BLUE),
              ("🤔", "推理与思考", "先想再答，多步推演", VIOLET),
              ("🛠", "智能体", "会用工具、能长时间干活", AQUA),
              ("🌍", "世界模型与具身", "理解物理世界，控制机器人", ORANGE),
              ("🐦", "小而精的模型", "高效、低能耗、可普及", YELLOW),
              ("🧩", "持续学习与记忆", "边用边学，不忘旧知", RED)]
    for i, (ic, name, sub, col) in enumerate(routes):
        y = 80 + i * 58
        b.append(f'<rect x="40" y="{y}" width="340" height="48" rx="10" fill="#fff" stroke="{col}" stroke-width="2"/>')
        b.append(f'<rect x="40" y="{y}" width="8" height="48" rx="4" fill="{col}"/>')
        b.append(f'<text x="70" y="{y+31}" font-size="20">{ic}</text>')
        b.append(f'<text x="104" y="{y+22}" font-size="16" font-weight="700">{name}</text>')
        b.append(f'<text x="104" y="{y+40}" font-size="12" class="s">{sub}</text>')
        b.append(f'<path d="M384,{y+24} C520,{y+24} 520,250 640,250" fill="none" stroke="{col}" stroke-width="2" stroke-opacity=".7"/>')
    b.append(f'<circle cx="720" cy="250" r="80" fill="{BLUE}"/>')
    b.append(f'<text x="720" y="245" font-size="30" font-weight="700" text-anchor="middle" style="fill:#fff">AGI</text>')
    b.append(f'<text x="720" y="272" font-size="13" text-anchor="middle" style="fill:#fff">通用人工智能</text>')
    b.append(f'<rect x="40" y="440" width="880" height="40" rx="10" fill="#eef3e9" stroke="{"#008300"}" stroke-width="1.5"/>')
    b.append(f'<text x="480" y="466" font-size="15" text-anchor="middle">🛡 地基：安全与对齐 —— 可解释、可控制、符合人类价值观</text>')
    return svg(W, H, "\n".join(b), "通往通用人工智能的几条技术路线")


save("01-narrow-vs-general.svg", narrow_vs_general())
save("02-ai-timeline.svg", timeline())
save("03-parameter-growth.svg", params())
save("03-next-token.svg", next_token())
save("03-agi-levels.svg", levels())
save("03-jagged-frontier.svg", jagged())
save("04-future-paths.svg", paths())
print("ok")
