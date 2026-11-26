
# ── 호텔 협의편 (약국 수령 기준) · 화면에는 큰 글자만, 세부 설명은 narration.txt 로
def shot(pil, name, box, r=22):
    im = Image.open(f'{P}/src/{name}.png').convert('RGB')
    bw, bh = box[2] - box[0], box[3] - box[1]; k = min(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    x = box[0] + (bw - im.width) // 2; y = box[1] + (bh - im.height) // 2
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x + 10, y + 16, x + im.width + 10, y + im.height + 16), radius=r, fill=150)
    pil.paste(Image.new('RGB', (W, H), (3, 5, 12)), (0, 0), sh.filter(ImageFilter.GaussianBlur(20)))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r, fill=255)
    pil.paste(im, (x, y), m)
    return (lambda px, py: (x + px * k, y + py * k)), k
def mark(d, Pf, box, px, py, col=YEL):
    (x0, y0), (x1, y1) = Pf(box[0], box[1]), Pf(box[2], box[3])
    d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=10, outline=col, width=5)
    lead(d, [(px, py), (x1 + 6, (y0 + y1) / 2)], col)
def ring(d, c, r=30, col=YEL):
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=col, width=5)
def big_callouts(d, items, x=1060, y0=250, gap=150, wid=760):
    """번호 + 큰 제목만 (설명은 나레이션)"""
    out = []
    for i, it in enumerate(items):
        n, t = it[:2]; kind = it[2] if len(it) > 2 else None; y = y0 + i * gap; h = gap - 24
        card(d, (x, y, x + wid, y + h), kind); num(d, x + 52, y + h / 2, n, 26)
        f = F(900, 38); put(d, x + 100, y + h / 2 - th(f) / 2, t, f, WHITE)
        out.append((x, y + h / 2))
    return out

def wechat(pil, x, y, w=560, h=760):
    """위챗 대화 예시 (약국 픽업용)"""
    d = ImageDraw.Draw(pil)
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x + 10, y + 16, x + w + 10, y + h + 16), radius=28, fill=150)
    pil.paste(Image.new('RGB', (W, H), (3, 5, 12)), (0, 0), sh.filter(ImageFilter.GaussianBlur(20)))
    d.rounded_rectangle((x, y, x + w, y + h), radius=28, fill=(237, 237, 237))
    d.rounded_rectangle((x, y, x + w, y + 84), radius=28, fill=(247, 247, 247)); d.rectangle((x, y + 56, x + w, y + 84), fill=(247, 247, 247))
    ctext(d, x + w / 2, y + 28, '酒店前台', F(700, 28), INK)
    yy = y + 110
    def msg(lines, me, yy, big=False):
        f = F(700 if big else 500, 30 if big else 25); lw = max(tlen(l, f) for l in lines) + 40; lh = (44 if big else 36) * len(lines) + 26
        av = (x + w - 74, yy) if me else (x + 18, yy)
        d.rounded_rectangle((av[0], av[1], av[0] + 56, av[1] + 56), radius=10, fill=(90, 150, 230) if me else (60, 70, 90))
        ctext(d, av[0] + 28, av[1] + 14, '나' if me else '前', F(900, 22), (255, 255, 255))
        bx = x + w - 90 - lw if me else x + 88
        d.rounded_rectangle((bx, yy, bx + lw, yy + lh), radius=12, fill=(149, 236, 105) if me else (255, 255, 255))
        for j, l in enumerate(lines): put(d, bx + 20, yy + 14 + j * (44 if big else 36), l, f, INK)
        return yy + lh + 22, (bx, yy, bx + lw, yy + lh)
    yy, _ = msg(['您好，我11月25日入住。', '京东药店自提要填联系电话，', '可以用酒店的11位手机号吗？'], True, yy)
    yy, num_b = msg(['可以，用这个：', '138-1234-5678'], False, yy, big=True)
    yy, _ = msg(['谢谢！微信号是？'], True, yy)
    yy, id_b = msg(['qd-hotel'], False, yy, big=True)
    d.rounded_rectangle((x + 20, y + h - 70, x + w - 20, y + h - 20), radius=12, fill=(255, 255, 255))
    return num_b, id_b


# ── 배경 선화 일러스트 (크레딧 없이 직접 그림, 흐리게)
def _art_layer(n):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L); C = (190, 205, 240, 255); w = 4
    def skyline(x0, base, sc=1.0):
        hs = [180, 260, 140, 320, 220, 280, 160, 240]
        x = x0
        for i_, h_ in enumerate(hs):
            bw = int((70 + (i_ % 3) * 20) * sc); hh = int(h_ * sc)
            g.rectangle((x, base - hh, x + bw, base), outline=C, width=w)
            for yy in range(base - hh + 20, base - 20, 34):
                for xx in range(x + 14, x + bw - 14, 24): g.rectangle((xx, yy, xx + 8, yy + 12), outline=C, width=2)
            x += bw + int(14 * sc)
        return x
    def may4(cx, base, sc=1.0):   # 5·4광장 '오월의 바람' 조형물 느낌
        for k in range(6):
            r = int((110 - k * 14) * sc); y = base - int(k * 40 * sc)
            g.arc((cx - r, y - int(30 * sc), cx + r, y + int(30 * sc)), 200, 520, fill=C, width=w)
    def waves(x0, x1, y):
        for k in range(3):
            pts = [(x, y + k * 26 + 10 * __import__('math').sin(x / 40)) for x in range(x0, x1, 6)]
            g.line(pts, fill=C, width=3)
    def hotel(x, base, sc=1.0):
        bw, bh = int(220 * sc), int(380 * sc)
        g.rectangle((x, base - bh, x + bw, base), outline=C, width=w)
        g.rectangle((x + bw // 2 - 50, base - bh - 50, x + bw // 2 + 50, base - bh), outline=C, width=w)
        put(g, x + bw // 2 - 34, base - bh - 40, 'HOTEL', F(900, int(24 * sc)), C)
        for yy in range(base - bh + 30, base - 60, 44):
            for xx in range(x + 24, x + bw - 24, 46): g.rectangle((xx, yy, xx + 22, yy + 26), outline=C, width=2)
        g.rectangle((x + bw // 2 - 26, base - 60, x + bw // 2 + 26, base), outline=C, width=w)
    def clipboard(x, y, sc=1.0):
        g.rounded_rectangle((x, y, x + int(220 * sc), y + int(290 * sc)), radius=16, outline=C, width=w)
        g.rounded_rectangle((x + int(70 * sc), y - 20, x + int(150 * sc), y + 20), radius=8, outline=C, width=w)
        for k in range(4):
            yy = y + int((60 + k * 56) * sc)
            g.line([(x + 30, yy), (x + 44, yy + 14), (x + 66, yy - 10)], fill=C, width=w)
            g.line([(x + 86, yy + 4), (x + int(190 * sc), yy + 4)], fill=C, width=3)
    def calendar(x, y, sc=1.0):
        cw, ch = int(260 * sc), int(230 * sc)
        g.rounded_rectangle((x, y, x + cw, y + ch), radius=14, outline=C, width=w)
        g.line([(x, y + 50), (x + cw, y + 50)], fill=C, width=w)
        for k in (60, cw - 60): g.line([(x + k, y - 18), (x + k, y + 18)], fill=C, width=6)
        for r in range(4):
            for c in range(6):
                xx = x + 22 + c * (cw - 44) // 6; yy = y + 70 + r * 38
                g.rectangle((xx, yy, xx + 22, yy + 20), outline=C, width=2)
    def laptop(x, y, sc=1.0):
        g.rounded_rectangle((x, y, x + int(320 * sc), y + int(200 * sc)), radius=10, outline=C, width=w)
        g.polygon([(x - 30, y + int(200 * sc) + 10), (x + int(320 * sc) + 30, y + int(200 * sc) + 10), (x + int(320 * sc) + 10, y + int(200 * sc) + 36), (x - 10, y + int(200 * sc) + 36)], outline=C)
        for k in range(4): g.line([(x + 30, y + 40 + k * 36), (x + int(280 * sc) - k * 40, y + 40 + k * 36)], fill=C, width=3)
    def bubble(x, y, wd, txt=None, right=False):
        g.rounded_rectangle((x, y, x + wd, y + 80), radius=24, outline=C, width=w)
        tx = x + wd - 40 if right else x + 30
        g.line([(tx, y + 80), (tx + (14 if right else -14), y + 108), (tx + (-10 if right else 20), y + 80)], fill=C, width=w)
        if txt: put(g, x + 26, y + 22, txt, F(700, 34), C)
    def phone(x, y, sc=1.0):
        g.rounded_rectangle((x, y, x + int(190 * sc), y + int(360 * sc)), radius=30, outline=C, width=w)
        g.rounded_rectangle((x + int(70 * sc), y + 14, x + int(120 * sc), y + 26), radius=6, outline=C, width=2)
        g.ellipse((x + int(80 * sc), y + int(320 * sc), x + int(110 * sc), y + int(350 * sc)), outline=C, width=3)
    def plane(x, y):
        g.polygon([(x, y), (x + 120, y + 20), (x + 150, y + 10), (x + 160, y + 20), (x + 120, y + 34), (x + 60, y + 70), (x + 46, y + 66), (x + 76, y + 30), (x + 20, y + 24)], outline=C)
        for k in range(12): g.line([(x - 40 - k * 50, y + 40 + k * 18), (x - 70 - k * 50, y + 51 + k * 18)], fill=C, width=3)
    def heart(cx, cy, r):
        g.arc((cx - r, cy - r, cx, cy), 140, 360, fill=C, width=w); g.arc((cx, cy - r, cx + r, cy), 180, 400, fill=C, width=w)
        g.line([(cx - r + 6, cy - r // 3), (cx, cy + r), (cx + r - 6, cy - r // 3)], fill=C, width=w)
    def star(cx, cy, r):
        import math
        pts = [(cx + (r if k % 2 == 0 else r / 2.4) * math.cos(math.pi / 2 + k * math.pi / 5), cy - (r if k % 2 == 0 else r / 2.4) * math.sin(math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        g.polygon(pts, outline=C)
    if n == 1: skyline(1000, 1060, 0.9); may4(1700, 1000, 1.0); waves(0, 1920, 1000)
    elif n == 2: plane(1500, 90); skyline(1200, 230, 0.55)
    elif n == 3: hotel(1500, 235, 0.55); hotel(1180, 235, 0.45)
    elif n == 4: clipboard(1600, 1000 - 300, 0.9); clipboard(1600, 60, 0.55)
    elif n == 5: g.line([(120, 1000), (600, 990), (1100, 1010), (1800, 990)], fill=C, width=4); clipboard(1620, 40, 0.6)
    elif n == 6: calendar(1500, 60, 0.7)
    elif n == 7: hotel(1600, 235, 0.5); calendar(1300, 90, 0.5)
    elif n == 8: laptop(1450, 80, 0.75)
    elif n == 9: bubble(1150, 30, 260, '你好', False); bubble(1480, 120, 300, 'Hello', True)
    elif n == 10: phone(1640, 20, 0.6); bubble(1250, 60, 300, '微信', True)
    elif n == 11: phone(1640, 20, 0.6); put(g, 1250, 120, '138-****-****', F(900, 50), C)
    elif n == 12: heart(300, 300, 90); heart(1650, 820, 110); star(1550, 300, 70); star(380, 820, 60); star(1780, 520, 40); star(150, 560, 40)
    return L
_frame_base = frame
def frame(n, step, label, title):
    global BG
    _bg0 = BG
    pil = BG.copy()
    # 배경 사진을 은은하게 (제목 영역은 더 어둡게)
    _bp = f'{P}/src/bgq/k{n}.jpg'   # 장마다 배경 사진 (fetch_photos.py 로 받기). 없으면 남색 그라데이션
    art = Image.open(_bp).convert('RGB') if os.path.exists(_bp) else BG.copy()
    _s = max(W / art.width, H / art.height); art = art.resize((int(art.width * _s) + 1, int(art.height * _s) + 1), Image.LANCZOS)
    _l = (art.width - W) // 2; _t = (art.height - H) // 2; art = art.crop((_l, _t, _l + W, _t + H)).filter(ImageFilter.GaussianBlur(2))
    # 표지처럼: 실사 사진을 꽉 채우고, 위(제목)·왼쪽을 더 어둡게
    import numpy as _np
    a_ = _np.asarray(art).astype(float)
    yy = _np.linspace(0, 1, H)[:, None, None]; xx = _np.linspace(0, 1, W)[None, :, None]
    dark = _np.clip(0.62 - yy * 0.12 + (0.25 - xx * 0.25) * 0.4, 0.45, 0.78)   # 0=원본, 1=검정
    dark = _np.where(yy < 0.22, _np.maximum(dark, 0.72), dark)             # 제목 띠는 더 어둡게
    _g = a_.mean(2, keepdims=True); a_ = a_ * 0.8 + _g * 0.2                      # 채도 낮춰 톤 통일
    a_ = a_ * _np.array([0.86, 0.95, 1.08])                                          # 남청색 톤
    out = a_ * (1 - dark) + _np.array([8, 12, 24]) * dark
    BG = Image.fromarray(out.clip(0, 255).astype('uint8'))
    res = _frame_base(n, step, label, [])
    BG = _bg0
    pil_, d_ = res
    # 제목: 표지와 같은 굵은 외곽선 글씨(도현체)
    _f = ImageFont.truetype(f'{T}/DoHyeon-Regular.ttf', 70); x_ = 96
    for t_, c_ in title:
        t_ = t_.replace('·', '|').replace('…', '...')
        d_.text((x_, 112), t_, font=_f, fill=c_, stroke_width=7, stroke_fill=(8, 10, 18)); x_ += _f.getlength(t_)
    os.makedirs(f'{P}/slides_bg', exist_ok=True); pil_.save(f'{P}/slides_bg/{n:02d}.png')
    return pil_, d_

os.makedirs(f'{P}/slides', exist_ok=True)
for f_ in os.listdir(f'{P}/slides'): os.remove(f'{P}/slides/{f_}')
S = []

def sym(kind, cx, cy, size=120):
    """플랫 일러스트 심볼 (4배로 그려 줄여서 매끈하게)"""
    S_ = 4; n = size * S_; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    top, bot = {'num': ((255, 205, 90), (240, 150, 40)), 'id': ((70, 220, 130), (20, 170, 90)),
                'ok': ((90, 225, 200), (30, 170, 150)), 'cap': ((255, 130, 120), (225, 70, 70)), 'jd': ((255, 110, 100), (215, 40, 50)), 'pharm': ((90, 200, 255), (40, 130, 230)), 'check': ((90, 225, 150), (30, 170, 100)), 'cross': ((255, 120, 110), (215, 45, 50)), 'pin': ((255, 205, 90), (240, 150, 40)), 'stop': ((255, 120, 110), (200, 35, 45)), 'like': ((255, 90, 90), (210, 20, 40)), 'bell': ((255, 90, 90), (210, 20, 40)), 'play': ((255, 90, 90), (210, 20, 40))}[kind]
    for yy in range(n):
        t_ = yy / n; c_ = tuple(int(top[j] * (1 - t_) + bot[j] * t_) for j in range(3))
        g.line((0, yy, n, yy), fill=c_ + (255,))
    m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, n - 1, n - 1), radius=n // 4, fill=255)
    im.putalpha(m); g = ImageDraw.Draw(im); Wt = (255, 255, 255, 255); u = n / 100
    if kind == 'num':      # 휴대폰 + 번호 줄
        g.rounded_rectangle((30 * u, 14 * u, 70 * u, 86 * u), radius=9 * u, fill=Wt)
        g.rounded_rectangle((35 * u, 24 * u, 65 * u, 72 * u), radius=3 * u, fill=top + (255,))
        for r_ in range(3):
            for c2 in range(3):
                x_ = 39 * u + c2 * 9 * u; y_ = 30 * u + r_ * 12 * u
                g.ellipse((x_, y_, x_ + 5 * u, y_ + 5 * u), fill=Wt)
        g.ellipse((46 * u, 76 * u, 54 * u, 84 * u), fill=bot + (255,))
    elif kind == 'id':     # 겹친 말풍선 (위챗 느낌)
        g.ellipse((14 * u, 20 * u, 64 * u, 62 * u), fill=Wt); g.polygon([(22 * u, 54 * u), (18 * u, 70 * u), (34 * u, 60 * u)], fill=Wt)
        g.ellipse((26 * u, 33 * u, 32 * u, 39 * u), fill=bot + (255,)); g.ellipse((44 * u, 33 * u, 50 * u, 39 * u), fill=bot + (255,))
        g.ellipse((44 * u, 42 * u, 88 * u, 78 * u), fill=(235, 255, 242, 255), outline=bot + (255,), width=int(3 * u))
        g.polygon([(78 * u, 72 * u), (84 * u, 86 * u), (70 * u, 76 * u)], fill=(235, 255, 242, 255))
        g.ellipse((56 * u, 55 * u, 61 * u, 60 * u), fill=bot + (255,)); g.ellipse((71 * u, 55 * u, 76 * u, 60 * u), fill=bot + (255,))
    elif kind == 'ok':     # 방패 + 체크
        g.polygon([(50 * u, 12 * u), (82 * u, 24 * u), (78 * u, 58 * u), (50 * u, 88 * u), (22 * u, 58 * u), (18 * u, 24 * u)], fill=Wt)
        g.line([(34 * u, 50 * u), (46 * u, 62 * u), (68 * u, 38 * u)], fill=bot + (255,), width=int(9 * u), joint='curve')
    elif kind == 'cap':    # 캡처 모서리 + 셔터
        L = 18 * u; w_ = int(8 * u)
        for (x_, y_, dx, dy) in [(18, 18, 1, 1), (82, 18, -1, 1), (18, 82, 1, -1), (82, 82, -1, -1)]:
            g.line([(x_ * u, y_ * u + dy * L), (x_ * u, y_ * u), (x_ * u + dx * L, y_ * u)], fill=Wt, width=w_, joint='curve')
        g.ellipse((34 * u, 34 * u, 66 * u, 66 * u), fill=Wt); g.ellipse((42 * u, 42 * u, 58 * u, 58 * u), fill=bot + (255,))
    elif kind == 'jd':     # 휴대폰 + 장바구니
        g.rounded_rectangle((22 * u, 12 * u, 60 * u, 88 * u), radius=8 * u, fill=Wt)
        g.rounded_rectangle((27 * u, 22 * u, 55 * u, 74 * u), radius=3 * u, fill=top + (255,))
        g.ellipse((37 * u, 77 * u, 45 * u, 85 * u), fill=bot + (255,))
        g.ellipse((52 * u, 40 * u, 90 * u, 78 * u), fill=Wt)
        g.line([(60 * u, 50 * u), (64 * u, 50 * u), (68 * u, 64 * u), (80 * u, 64 * u), (83 * u, 54 * u), (66 * u, 54 * u)], fill=bot + (255,), width=int(4 * u), joint='curve')
        g.ellipse((67 * u, 67 * u, 72 * u, 72 * u), fill=bot + (255,)); g.ellipse((77 * u, 67 * u, 82 * u, 72 * u), fill=bot + (255,))
    elif kind == 'pharm':  # 약국 십자
        g.rounded_rectangle((38 * u, 16 * u, 62 * u, 84 * u), radius=6 * u, fill=Wt)
        g.rounded_rectangle((16 * u, 38 * u, 84 * u, 62 * u), radius=6 * u, fill=Wt)
    elif kind == 'check':
        g.line([(26 * u, 52 * u), (43 * u, 69 * u), (75 * u, 33 * u)], fill=Wt, width=int(12 * u), joint='curve')
    elif kind == 'cross':
        g.line([(30 * u, 30 * u), (70 * u, 70 * u)], fill=Wt, width=int(12 * u)); g.line([(70 * u, 30 * u), (30 * u, 70 * u)], fill=Wt, width=int(12 * u))
    elif kind == 'pin':
        g.ellipse((28 * u, 14 * u, 72 * u, 58 * u), fill=Wt); g.polygon([(31 * u, 46 * u), (69 * u, 46 * u), (50 * u, 86 * u)], fill=Wt)
        g.ellipse((41 * u, 27 * u, 59 * u, 45 * u), fill=bot + (255,))
    elif kind == 'stop':
        g.rounded_rectangle((22 * u, 42 * u, 78 * u, 58 * u), radius=6 * u, fill=Wt)
    elif kind == 'like':   # 엄지
        g.rounded_rectangle((18 * u, 44 * u, 32 * u, 82 * u), radius=4 * u, fill=Wt)
        g.rounded_rectangle((36 * u, 42 * u, 80 * u, 82 * u), radius=10 * u, fill=Wt)
        g.polygon([(38 * u, 46 * u), (50 * u, 16 * u), (60 * u, 20 * u), (56 * u, 46 * u)], fill=Wt)
        g.ellipse((48 * u, 12 * u, 62 * u, 26 * u), fill=Wt)
    elif kind == 'bell':   # 알림 종
        g.pieslice((26 * u, 18 * u, 74 * u, 70 * u), 180, 360, fill=Wt)
        g.rectangle((26 * u, 43 * u, 74 * u, 66 * u), fill=Wt)
        g.rounded_rectangle((18 * u, 64 * u, 82 * u, 72 * u), radius=4 * u, fill=Wt)
        g.ellipse((43 * u, 72 * u, 57 * u, 86 * u), fill=Wt); g.ellipse((45 * u, 10 * u, 55 * u, 20 * u), fill=Wt)
    elif kind == 'play':   # 재생
        g.polygon([(38 * u, 26 * u), (76 * u, 50 * u), (38 * u, 74 * u)], fill=Wt)
    im = im.resize((size, size), Image.LANCZOS)
    sh = Image.new('L', (W, H), 0); sh.paste(im.split()[3], (int(cx - size / 2) + 4, int(cy - size / 2) + 8))
    pil.paste(Image.new('RGB', (W, H), (4, 6, 14)), (0, 0), sh.point(lambda v: int(v * .5)).filter(ImageFilter.GaussianBlur(8)))
    pil.paste(im, (int(cx - size / 2), int(cy - size / 2)), im)

_EMAP = {'✅': 'check', '❌': 'cross', '📍': 'pin', '⛔': 'stop'}
def emoji(pil_, ch, cx, cy, size):
    sym(_EMAP[ch], cx, cy, int(size))

HL_COL, HL_FILL, HL_TXT = (232, 52, 44), (60, 16, 20), (255, 255, 255)
DH = lambda sz: ImageFont.truetype(f'{T}/DoHyeon-Regular.ttf', sz)
def otext(d_, x, y, t, f, fill, sw=10, sc=(10, 12, 20)):
    d_.text((x, y), t, font=f, fill=fill, stroke_width=sw, stroke_fill=sc)
    return x + f.getlength(t)
def tag(d_, x, y, t, f, fill, col=(255, 255, 255), padx=24, h=70):
    w_ = f.getlength(t); d_.rounded_rectangle((x, y, x + w_ + padx * 2, y + h), radius=10, fill=fill)
    bb = f.getbbox(t); d_.text((x + padx, y + (h - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=col)
def photo(pil, name, box, r=22, yb=0.5):
    im = Image.open(f'{P}/src/{name}').convert('RGB'); bw, bh = box[2] - box[0], box[3] - box[1]
    k = max(bw / im.width, bh / im.height); im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    l = (im.width - bw) // 2; t = int((im.height - bh) * yb); im = im.crop((l, t, l + bw, t + bh))
    m = Image.new('L', (bw, bh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=r, fill=255)
    pil.paste(im, (box[0], box[1]), m)
