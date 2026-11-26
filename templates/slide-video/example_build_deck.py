"""칭다오 마운자로 2편 · 징동 주문 · 비대면 진료 — 슬라이드 13장 (PDF 검토용)
화면에는 큰 글자만, 세부 설명은 narration.txt. 휴대폰 화면은 예시 그림.
문진은 '사실대로 답하기'만 안내한다(질환명 바꿔 고르기·임의 번호 넣기는 넣지 않음)."""
import os
_D = os.path.dirname(os.path.abspath(__file__))
exec(open(f'{_D}/_head.py', encoding='utf-8').read())
exec(open(f'{_D}/_helpers.py', encoding='utf-8').read())

# ── 심볼 추가 (여권 · 집 · 카드 · 돋보기 · 문서 · 말풍선 · 경고 · 약사)
_sym0 = sym
def sym(kind, cx, cy, size=120):
    if kind not in ('pass', 'home', 'pay', 'search', 'doc', 'chat', 'warn', 'tap', 'clock', 'box'):
        return _sym0(kind, cx, cy, size)
    S_ = 4; n = size * S_; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    top, bot = {'pass': ((110, 150, 255), (60, 90, 220)), 'home': ((255, 205, 90), (240, 150, 40)), 'pay': ((90, 225, 150), (30, 170, 100)),
                'search': ((255, 110, 100), (215, 40, 50)), 'doc': ((90, 200, 255), (40, 130, 230)), 'chat': ((90, 225, 200), (30, 170, 150)),
                'warn': ((255, 120, 110), (200, 35, 45)), 'tap': ((255, 120, 110), (200, 35, 45)), 'clock': ((255, 205, 90), (240, 150, 40)),
                'box': ((170, 140, 255), (120, 80, 230))}[kind]
    for yy in range(n):
        t_ = yy / n; g.line((0, yy, n, yy), fill=tuple(int(top[j] * (1 - t_) + bot[j] * t_) for j in range(3)) + (255,))
    m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, n - 1, n - 1), radius=n // 4, fill=255)
    im.putalpha(m); g = ImageDraw.Draw(im); Wt = (255, 255, 255, 255); u = n / 100; B = bot + (255,)
    if kind == 'pass':     # 여권
        g.rounded_rectangle((26 * u, 14 * u, 74 * u, 86 * u), radius=6 * u, fill=Wt)
        g.ellipse((37 * u, 30 * u, 63 * u, 56 * u), outline=B, width=int(4 * u)); g.line((50 * u, 30 * u, 50 * u, 56 * u), fill=B, width=int(3 * u))
        g.line((37 * u, 43 * u, 63 * u, 43 * u), fill=B, width=int(3 * u)); g.rounded_rectangle((36 * u, 66 * u, 64 * u, 72 * u), radius=3 * u, fill=B)
    elif kind == 'home':   # 호텔 건물
        g.rectangle((28 * u, 22 * u, 72 * u, 86 * u), fill=Wt)
        for r_ in range(4):
            for c_ in range(3): g.rectangle(((34 + c_ * 12) * u, (30 + r_ * 12) * u, (40 + c_ * 12) * u, (36 + r_ * 12) * u), fill=B)
        g.rectangle((44 * u, 76 * u, 56 * u, 86 * u), fill=B); g.rectangle((24 * u, 16 * u, 76 * u, 24 * u), fill=Wt)
    elif kind == 'pay':    # 카드
        g.rounded_rectangle((14 * u, 26 * u, 86 * u, 74 * u), radius=8 * u, fill=Wt); g.rectangle((14 * u, 36 * u, 86 * u, 46 * u), fill=B)
        g.rounded_rectangle((22 * u, 56 * u, 46 * u, 64 * u), radius=3 * u, fill=B)
    elif kind == 'search':
        g.ellipse((18 * u, 18 * u, 64 * u, 64 * u), outline=Wt, width=int(10 * u)); g.line((58 * u, 58 * u, 82 * u, 82 * u), fill=Wt, width=int(12 * u))
    elif kind == 'doc':    # 처방전
        g.rounded_rectangle((24 * u, 12 * u, 76 * u, 88 * u), radius=6 * u, fill=Wt)
        for j in range(4): g.rounded_rectangle((33 * u, (26 + j * 11) * u, (67 - (j == 3) * 14) * u, (31 + j * 11) * u), radius=2 * u, fill=B)
        g.ellipse((52 * u, 66 * u, 70 * u, 84 * u), outline=(230, 60, 60, 255), width=int(4 * u))
    elif kind == 'chat':
        g.rounded_rectangle((14 * u, 18 * u, 86 * u, 70 * u), radius=14 * u, fill=Wt); g.polygon([(28 * u, 66 * u), (24 * u, 86 * u), (44 * u, 68 * u)], fill=Wt)
        for j in range(3): g.ellipse(((32 + j * 15) * u, 40 * u, (40 + j * 15) * u, 48 * u), fill=B)
    elif kind == 'warn':
        g.polygon([(50 * u, 14 * u), (88 * u, 82 * u), (12 * u, 82 * u)], fill=Wt)
        g.rounded_rectangle((46 * u, 36 * u, 54 * u, 62 * u), radius=3 * u, fill=B); g.ellipse((45 * u, 67 * u, 55 * u, 77 * u), fill=B)
    elif kind == 'tap':    # 손가락 연타
        g.rounded_rectangle((40 * u, 20 * u, 56 * u, 66 * u), radius=8 * u, fill=Wt); g.rounded_rectangle((34 * u, 48 * u, 74 * u, 88 * u), radius=12 * u, fill=Wt)
        for a_ in (0, 1): g.arc(((26 - a_ * 10) * u, (8 - a_ * 6) * u, (70 + a_ * 10) * u, (40 + a_ * 6) * u), 200, 340, fill=Wt, width=int(4 * u))
    elif kind == 'clock':
        g.ellipse((16 * u, 16 * u, 84 * u, 84 * u), fill=Wt); g.line((50 * u, 50 * u, 50 * u, 28 * u), fill=B, width=int(7 * u))
        g.line((50 * u, 50 * u, 66 * u, 58 * u), fill=B, width=int(7 * u))
    elif kind == 'box':    # 약 상자
        g.polygon([(50 * u, 14 * u), (84 * u, 30 * u), (50 * u, 46 * u), (16 * u, 30 * u)], fill=(235, 230, 255, 255))
        g.polygon([(16 * u, 30 * u), (50 * u, 46 * u), (50 * u, 86 * u), (16 * u, 70 * u)], fill=Wt)
        g.polygon([(84 * u, 30 * u), (50 * u, 46 * u), (50 * u, 86 * u), (84 * u, 70 * u)], fill=(220, 214, 255, 255))
        g.rounded_rectangle((26 * u, 52 * u, 40 * u, 58 * u), radius=2 * u, fill=B)
    im = im.resize((size, size), Image.LANCZOS)
    sh = Image.new('L', (W, H), 0); sh.paste(im.split()[3], (int(cx - size / 2) + 4, int(cy - size / 2) + 8))
    pil.paste(Image.new('RGB', (W, H), (4, 6, 14)), (0, 0), sh.point(lambda v: int(v * .5)).filter(ImageFilter.GaussianBlur(8)))
    pil.paste(im, (int(cx - size / 2), int(cy - size / 2)), im)

def mock(d): put(d, 100, 994, '※ 이해를 돕는 예시 화면 · 실제 앱과 다를 수 있음', F(500, 20), MUTE)
def hl(d, b, col=YEL, w=5): d.rounded_rectangle((b[0] - 2, b[1] - 2, b[2] + 2, b[3] + 2), radius=12, outline=col, width=w)
def link(d, pts, b, col=YEL):
    """콜아웃(px,py) → 화면 상자 오른쪽 끝"""
    px, py = pts; lead(d, [(px, py), (b[2] + 8, (b[1] + b[3]) / 2)], col)
JR = (226, 35, 26)   # 징동 빨강

def product_screen(pil, x, y, w=520, h=780, tab='自提'):
    ph = Phone(pil, x, y, w, h); d = ph.d; sx, sw = ph.sx, ph.sw
    # 위치 + 검색창
    put(d, sx + 22, ph.y + 6, '◉ 青岛 市南区', F(700, 20), INK); ph.y += 44
    sb = (sx + 18, ph.y, sx + sw - 18, ph.y + 56)
    d.rounded_rectangle(sb, radius=28, fill=(255, 255, 255), outline=JR, width=3)
    put(d, sx + 44, ph.y + 28 - th(F(700, 24)) / 2, '替尔泊肽  40mg', F(700, 24), INK)
    d.rounded_rectangle((sx + sw - 104, ph.y + 6, sx + sw - 24, ph.y + 50), radius=22, fill=JR); ctext(d, sx + sw - 64, ph.y + 16, '搜索', F(700, 20), WHITE)
    ph.y += 74
    # 配送 / 自提 탭
    tb = {}
    for j, t in enumerate(['配送', '自提']):
        x0 = sx + 18 + j * (sw - 36) / 2; on = t == tab
        b = (x0, ph.y, x0 + (sw - 36) / 2, ph.y + 54); tb[t] = b
        d.rectangle(b, fill=(255, 255, 255)); ctext(d, (b[0] + b[2]) / 2, ph.y + 13, t, F(900 if on else 500, 26), JR if on else GRAY)
        if on: d.rectangle((b[0] + 50, b[3] - 6, b[2] - 50, b[3]), fill=JR)
    ph.y += 66
    # 필터
    fx = sx + 18; chips = {}
    for t in ['原研药', '综合', '销量', '价格']:
        on = t == '原研药'; f = F(700 if on else 500, 19); wd = tlen(t, f) + 30
        b = (fx, ph.y, fx + wd, ph.y + 40); chips[t] = b
        d.rounded_rectangle(b, radius=20, fill=(255, 236, 234) if on else (238, 240, 244)); put(d, fx + 15, ph.y + 20 - th(f) / 2, t, f, JR if on else INK); fx += wd + 10
    ph.y += 56
    # 상품 카드 2개
    cards = []
    for k_, (nm, badge, pr) in enumerate([('穆峰达 替尔泊肽注射液', '自营', '936.70'), ('穆峰达 2.4ml:40mg', '京东大药房', '958.00')]):
        b = (sx + 14, ph.y, sx + sw - 14, ph.y + 196); cards.append(b)
        d.rounded_rectangle(b, radius=16, fill=(255, 255, 255))
        bx = box_img(150); pil.paste(bx, (int(b[0] + 30), int(b[1] + 22)), bx)
        tx = b[0] + 150
        d.rounded_rectangle((tx, b[1] + 22, tx + tlen(badge, F(700, 17)) + 16, b[1] + 50), radius=6, fill=JR)
        put(d, tx + 8, b[1] + 36 - th(F(700, 17)) / 2, badge, F(700, 17), WHITE)
        put(d, tx, b[1] + 62, nm, F(700, 20), INK); put(d, tx, b[1] + 94, '2.4ml:40mg  ×1支', F(500, 18), GRAY)
        put(d, tx, b[1] + 132, '¥', F(700, 22), JR); put(d, tx + 18, b[1] + 124, pr, F(900, 32), JR)
        ph.y += 212
    return ph, sb, tb, chips, cards

# ═══ 1. 표지
pil = Image.open(f'{P}/src/bg2/b24.jpg').convert('RGB')
_s = max(W / pil.width, H / pil.height); pil = pil.resize((int(pil.width * _s) + 1, int(pil.height * _s) + 1), Image.LANCZOS)
_l = (pil.width - W) // 2; _t = (pil.height - H) // 2; pil = pil.crop((_l, _t, _l + W, _t + H))
_a = np.asarray(pil).astype(float); _gx = np.linspace(0, 1, W)[None, :, None]
_dark = np.clip(0.72 - _gx * 0.55, 0.15, 0.72)
pil = Image.fromarray((_a * (1 - _dark) + np.array([8, 12, 24]) * _dark).clip(0, 255).astype('uint8')); d = ImageDraw.Draw(pil)
tag(d, 90, 80, '마라자로 | 칭다오 마운자로 2편', DH(46), (24, 150, 90))
_f = DH(46); _bb = _f.getbbox('마'); _x = 90 + 24 + _f.getlength('마라자로 | 칭다오 마운자로 ')
d.text((_x, 80 + (70 - (_bb[3] - _bb[1])) / 2 - _bb[1]), '2편', font=_f, fill=(255, 226, 60), stroke_width=2, stroke_fill=(10, 60, 30))
tag(d, 90, 168, '징동 주문 | 비대면 진료', DH(50), (215, 40, 40))
otext(d, 82, 270, '칭다오 마운자로', DH(140), (255, 214, 40), sw=12)
_x = otext(d, 82, 440, '징동 앱', DH(150), (255, 80, 70), sw=13); otext(d, _x, 440, '으로', DH(150), (255, 255, 255), sw=13)
otext(d, 82, 610, '처방까지 받기', DH(140), (120, 200, 255), sw=12)
d.text((96, 830), '준비물 3개  |  여권  |  호텔 주소  |  11자리 번호', font=DH(46), fill=(235, 240, 250), stroke_width=4, stroke_fill=(10, 12, 20))
_c = Image.new('RGB', (W, H), (20, 24, 34)); product_screen(_c, 0, 0, 520, 780)
_c = _c.crop((0, 0, 520, 690)).convert('RGBA')
_m = Image.new('L', _c.size, 0); ImageDraw.Draw(_m).rounded_rectangle((0, 0, 519, 760), radius=62, fill=255); _c.putalpha(_m)
_c = _c.rotate(-6, expand=True, resample=Image.BICUBIC)
_sh = Image.new('L', (W, H), 0); _sh.paste(_c.split()[3], (1330 + 20, 200 + 28))
pil.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 0), _sh.point(lambda v: int(v * .6)).filter(ImageFilter.GaussianBlur(22)))
pil.paste(_c, (1330, 200), _c)
_ph = Image.open(f'{P}/src/cover_cn_boxes.jpg').convert('RGB'); _ph.thumbnail((400, 400))
_f2 = Image.new('RGB', (_ph.width + 24, _ph.height + 24), (255, 255, 255)); _f2.paste(_ph, (12, 12))
_f2 = _f2.convert('RGBA').rotate(7, expand=True, resample=Image.BICUBIC); shadow_paste(pil, _f2, 1050, 590, glow=False)
S.append(pil)

# ═══ 2. 전체 순서
pil, d = frame(2, None, '전체 순서', [('칭다오 마운자로 ', WHITE), ('받는 순서', YEL)])
road = [('photo_hotel_desk.jpg', '호텔에서 / 중국 휴대폰 번호 받기', '1편'), ('photo_jd_store.jpg', '징동 주문 / 비대면 진료', '오늘 영상'), ('photo_pharmacy.jpg', '칭다오 도착 / 약국 수령', None)]
for i, (ph_, t, tg) in enumerate(road):
    cx = 380 + i * 580; hi = i == 1
    card(d, (cx - 260, 240, cx + 260, 900), 'yel' if hi else None)
    photo(pil, ph_, (cx - 230, 270, cx + 230, 600)); d = ImageDraw.Draw(pil)
    if hi: d.rounded_rectangle((cx - 232, 268, cx + 232, 602), radius=22, outline=YEL, width=4)
    num(d, cx - 190, 310, str(i + 1), 34)
    for j, part in enumerate(t.split(' / ')): ctext(d, cx, 680 + j * 66, part, F(900, 44), YEL if hi else WHITE)
    if tg: pill(d, cx - tlen(tg, F(900, 28)) / 2 - 22, 930, tg, F(900, 28), RED if hi else (70, 82, 120), WHITE, padx=22, h=52)
    if i < 2: arrow(d, cx + 266, cx + 314, 435, w=7)
put(d, 1000, 1000, '사진: Wikimedia Commons · N509FZ / Windmemories / Shwangtianyuan · CC BY-SA 4.0', F(500, 18), (111, 123, 153))
S.append(pil)

# ═══ 3. 준비물
pil, d = frame(3, None, '시작 전에', [('준비물 ', WHITE), ('3가지', YEL), (' + 결제 수단', WHITE)])
prep = [('pass', '여권', '복용자 등록', None), ('home', '호텔 중국어 주소', '배송지 · 근처 약국', None),
        ('num', '중국 휴대폰 번호', '1편에서 받은 번호', 'yel'), ('pay', '위챗페이 · 알리페이', '해외 카드 등록', 'mint')]
for i, (k_, t, s_, kd) in enumerate(prep):
    cx = 310 + i * 433; x0 = cx - 200
    card(d, (x0, 250, x0 + 400, 800), kd)
    photo(pil, 'us/' + {'pass': 'pass_kr', 'home': 'home_0', 'num': 'num_1', 'pay': 'pay_0'}[k_] + '.jpg', (x0 + 18, 268, x0 + 382, 500), r=18); d = ImageDraw.Draw(pil)
    if i == 3: pill(d, x0 + 20, 270, '+ 결제', F(900, 24), MINT, (10, 40, 30), padx=16, h=42)
    for j, part in enumerate(t.split(' · ') if i == 3 else [t]):
        ctext(d, cx, 540 + j * 60, part + (' ·' if (i == 3 and j == 0) else ''), F(900, 42), YEL if kd == 'yel' else WHITE)
    ctext(d, cx, 700 if i == 3 else 620, s_, F(700, 30), SUB)
card(d, (100, 840, 1820, 960), 'red'); sym('warn', 180, 900, 76); d = ImageDraw.Draw(pil)
put(d, 250, 900 - th(F(900, 42)) / 2, '번호가 없으면 → 1편(호텔 협의) 먼저', F(900, 42), (255, 170, 160))
S.append(pil)

# ═══ 4. STEP 1 가입 · 로그인
pil, d = frame(4, 'STEP 1', '앱 설치 · 로그인', [('한국 번호', YEL), ('로 가입하기', WHITE)])
ph = Phone(pil, 230, 220, 500, 770, '登录'); dd = ph.d
ph.gap(30); ctext(dd, ph.sx + ph.sw / 2, ph.y, 'JD 京东', F(900, 44), JR); ph.y += 90
b_cty = ph.row('国家/地区', '海外 › 韩国  +82', vcol=(40, 90, 200))
b_tel = ph.row('手机号', '10 - 1234 - ****')
b_code = ph.row('验证码', '______', vcol=GRAY)
dd.rounded_rectangle((ph.sx + ph.sw - 170, b_code[1] + 16, ph.sx + ph.sw - 20, b_code[3] - 16), radius=20, outline=JR, width=2)
ctext(dd, ph.sx + ph.sw - 95, b_code[1] + 26, '获取验证码', F(700, 18), JR)
b_btn = ph.button('登录', y=ph.y + 40, col=JR)
put(dd, ph.sx + 30, b_btn[3] + 50, '其他方式登录', F(500, 18), GRAY)
b_wx = (ph.sx + 40, b_btn[3] + 90, ph.sx + ph.sw - 40, b_btn[3] + 154)
dd.rounded_rectangle(b_wx, radius=32, fill=(7, 193, 96)); ctext(dd, (b_wx[0] + b_wx[2]) / 2, b_wx[1] + 20, '微信登录', F(700, 24), WHITE)
d = ImageDraw.Draw(pil)
pts = big_callouts(d, [('1', '마이(我的) → 로그인'), ('2', '국가: 해외 → 한국 +82'), ('3', '인증 문자 입력'), ('4', '위챗 로그인도 OK', 'mint')], x=1000, y0=260, gap=172, wid=820)
hl(d, b_cty); link(d, pts[1], b_cty); hl(d, b_code); link(d, pts[2], b_code); hl(d, b_wx, MINT); link(d, pts[3], b_wx, MINT)
mock(d); S.append(pil)

# ═══ 5. STEP 1 배송지 · 위치
pil, d = frame(5, 'STEP 1', '배송지(收货地址) 등록', [('가입 후 ', WHITE), ('마이 → 설정', YEL), ('에서 ', WHITE), ('새 주소 추가', YEL)])
ph = Phone(pil, 230, 220, 500, 770, '新建收货地址'); dd = ph.d; ph.gap(18)
b_nm = ph.row('收货人', 'HONG GILDONG')
b_tel = ph.row('手机号', '+86  138-1234-5678', vcol=(40, 90, 200))
b_area = ph.row('所在地区', '山东省 青岛市 市南区')
b_map = ph.row('详细地址', '地图选址 ›  ○○酒店', vcol=(40, 90, 200))
ph.gap(18)
mp = (ph.sx + 20, ph.y, ph.sx + ph.sw - 20, ph.y + 200); dd.rounded_rectangle(mp, radius=14, fill=(226, 236, 228))
for j in range(5): dd.line((mp[0], mp[1] + 30 + j * 38, mp[2], mp[1] + 10 + j * 42), fill=(255, 255, 255), width=8)
dd.line((mp[0] + 150, mp[1], mp[0] + 200, mp[3]), fill=(255, 255, 255), width=10)
cxm, cym = (mp[0] + mp[2]) / 2, (mp[1] + mp[3]) / 2
dd.ellipse((cxm - 16, cym - 40, cxm + 16, cym - 8), fill=JR); dd.polygon([(cxm - 13, cym - 18), (cxm + 13, cym - 18), (cxm, cym + 6)], fill=JR)
for (px_, py_) in [(-120, 40), (110, -50), (140, 60)]:
    dd.rounded_rectangle((cxm + px_ - 16, cym + py_ - 16, cxm + px_ + 16, cym + py_ + 16), radius=6, fill=(40, 130, 230)); ctext(dd, cxm + px_, cym + py_ - 11, '+', F(900, 20), WHITE)
ph.y = mp[3] + 30; ph.button('保存', y=ph.y, col=JR)
d = ImageDraw.Draw(pil)
pts = big_callouts(d, [('1', '이름: 여권 영문 그대로'), ('2', '번호: 중국 휴대폰 번호', 'yel'), ('3', '지도에서 호텔 선택'), ('4', '근처 약국이 자동 표시', 'mint')], x=1000, y0=410, gap=140, wid=820)
card(d, (1000, 232, 1820, 382), 'blue')
put(d, 1036, 250, '주소 추가 방법', F(700, 26), SUB)
put(d, 1036, 300, '마이(我的) → 설정 → 주소 관리 → 새 주소', F(900, 32), WHITE)
put(d, 1036, 346, '我的 → 设置 → 地址管理 → 新建收货地址', F(500, 22), SUB)
for p_, b_, c_ in zip(pts, [b_nm, b_tel, b_map, mp], [YEL, YEL, YEL, MINT]): hl(d, b_, c_); link(d, p_, b_, c_)
mock(d); S.append(pil)

# ═══ 6. STEP 2 검색
pil, d = frame(6, 'STEP 2', '약 검색', [('중국 이름', YEL), ('으로 검색', WHITE)])
ph, sb, tb, chips, cards = product_screen(pil, 160, 220, 500, 770); d = ImageDraw.Draw(pil)
hl(d, sb); hl(d, chips['原研药']); hl(d, (cards[0][0] + 130, cards[0][1] + 16, cards[0][0] + 240, cards[0][1] + 56), MINT)
card(d, (740, 240, 1820, 470))
put(d, 790, 268, '검색어 (복사해 두기)', F(700, 30), SUB)
put(d, 790, 330, '替尔泊肽', F(900, 64), YEL); put(d, 1180, 342, '티르제파타이드', F(700, 34), WHITE)
put(d, 790, 410 - 6, '穆峰达', F(900, 44), WHITE); put(d, 1000, 412, '무펑다 (중국 상품명)', F(700, 30), SUB)
lead(d, [(790, 360), (sb[2] + 8, (sb[1] + sb[3]) / 2)])
# 용량 표
card(d, (740, 500, 1820, 960), 'blue')
put(d, 790, 525, '상자 표기  →  주 1회 용량', F(900, 36), WHITE); put(d, 1530, 532, '후기 가격', F(700, 28), SUB)
rows_ = [('10mg', '2.5mg', '¥324~358'), ('20mg', '5mg', '¥549~585'), ('30mg', '7.5mg', '¥751'), ('40mg', '10mg', '¥924~999')]
for j, (a_, b_, c_) in enumerate(rows_):
    y = 585 + j * 82
    d.rounded_rectangle((780, y, 1780, y + 72), radius=14, fill=(32, 56, 100) if j % 2 == 0 else (26, 46, 86))
    put(d, 820, y + 36 - th(F(900, 38)) / 2, a_, F(900, 38), WHITE); arrow(d, 990, 1080, y + 36, col=(150, 175, 230), w=5)
    put(d, 1110, y + 36 - th(F(900, 38)) / 2, b_, F(900, 38), YEL); put(d, 1500, y + 36 - th(F(700, 32)) / 2, c_, F(700, 32), SUB)
put(d, 790, 920, '한 상자 = 4회분(4주)  ·  가격은 판매처·시기마다 다름', F(500, 22), SUB)
mock(d); S.append(pil)

# ═══ 7. STEP 2 自提(약국 픽업)
pil, d = frame(7, 'STEP 2', '받는 방법 고르기', [('픽업 탭', RED), ('으로 약국 수령', WHITE)])
ph = Phone(pil, 230, 220, 500, 770, '确认订单'); dd = ph.d; sx, sw = ph.sx, ph.sw
tb7 = {}
for j, t in enumerate(['配送', '自提']):
    x0 = sx + 18 + j * (sw - 36) / 2; on = t == '自提'; b = (x0, ph.y + 12, x0 + (sw - 36) / 2, ph.y + 66); tb7[t] = b
    dd.rounded_rectangle(b, radius=10, fill=(255, 236, 234) if on else (255, 255, 255)); ctext(dd, (b[0] + b[2]) / 2, b[1] + 13, t, F(900 if on else 500, 26), JR if on else GRAY)
ph.y += 84
b_ph = (sx + 14, ph.y, sx + sw - 14, ph.y + 120); dd.rounded_rectangle(b_ph, radius=14, fill=(255, 255, 255))
put(dd, sx + 34, ph.y + 18, '自提门店', F(500, 19), GRAY); put(dd, sx + 34, ph.y + 50, '○○大药房 (酒店附近)', F(700, 24), INK)
put(dd, sx + 34, ph.y + 86, '距您 600m · 步行 10分钟', F(500, 19), GRAY); ph.y += 136
b_tm = (sx + 14, ph.y, sx + sw - 14, ph.y + 86); dd.rounded_rectangle(b_tm, radius=14, fill=(255, 255, 255))
put(dd, sx + 34, ph.y + 30, '预约自提', F(700, 22), INK); put(dd, sx + 200, ph.y + 30, '明天 11:30  ›', F(700, 22), (40, 90, 200)); ph.y += 102
b_qty = (sx + 14, ph.y, sx + sw - 14, ph.y + 150); dd.rounded_rectangle(b_qty, radius=14, fill=(255, 255, 255))
bx = box_img(110); pil.paste(bx, (int(sx + 40), int(ph.y + 20)), bx)
put(dd, sx + 140, ph.y + 30, '穆峰达 2.4ml:40mg', F(700, 21), INK); put(dd, sx + 140, ph.y + 90, '¥936.70', F(900, 26), JR)
dd.rounded_rectangle((sx + sw - 150, ph.y + 86, sx + sw - 34, ph.y + 124), radius=8, outline=LINE, width=2); ctext(dd, sx + sw - 92, ph.y + 92, '－  1  ＋', F(700, 20), INK)
ph.y += 166
dd.rectangle((sx, ph.sy + ph.sh - 110, sx + sw, ph.sy + ph.sh), fill=(255, 255, 255))
put(dd, sx + 24, ph.sy + ph.sh - 76, '合计 ¥933.85', F(900, 26), JR)
dd.rounded_rectangle((sx + sw - 210, ph.sy + ph.sh - 92, sx + sw - 20, ph.sy + ph.sh - 30), radius=31, fill=JR); ctext(dd, sx + sw - 115, ph.sy + ph.sh - 78, '提交订单', F(700, 22), WHITE)
d = ImageDraw.Draw(pil)
pts = big_callouts(d, [('1', "'自提' 탭 선택"), ('2', '호텔 근처 약국'), ('3', '픽업 시간 예약'), ('4', '수량 1~2개 · 한 용량만', 'yel')], x=1000, y0=260, gap=172, wid=820)
for p_, b_ in zip(pts, [tb7['自提'], b_ph, b_tm, b_qty]): hl(d, b_); link(d, p_, b_)
mock(d); S.append(pil)

# ═══ 8. STEP 3 복용자 등록
pil, d = frame(8, 'STEP 3', '복용자(用药人) 등록', [('신분증 → ', WHITE), ('여권', YEL), ('으로 바꾸기', WHITE)])
ph = Phone(pil, 230, 220, 500, 770, '添加用药人'); dd = ph.d; ph.gap(20)
b_t = ph.row('证件类型', '外籍护照  ›', vcol=(40, 90, 200))
put(dd, ph.sx + 300, b_t[1] + 26, '身份证', F(500, 18), (190, 190, 200)); dd.line((ph.sx + 298, b_t[1] + 38, ph.sx + 358, b_t[1] + 38), fill=(200, 60, 60), width=3)
b_no = ph.row('证件号码', 'M1234****')
b_nm = ph.row('姓名', 'HONG GILDONG')
ph.row('性别', '男 / 女'); ph.row('出生日期', '19xx-xx-xx'); ph.row('与本人关系', '本人')
ph.button('保存', y=ph.y + 60, col=JR)
d = ImageDraw.Draw(pil)
pts = big_callouts(d, [('1', '신분증 변경: 身份证 → 外籍护照', 'yel'), ('2', '여권 번호 입력'), ('3', '이름: 여권 영문 그대로')], x=1000, y0=300, gap=200, wid=820)
for p_, b_ in zip(pts, [b_t, b_no, b_nm]): hl(d, b_); link(d, p_, b_)
mock(d); S.append(pil)

# ═══ 9. STEP 3 비대면 문진
pil, d = frame(9, 'STEP 3', '비대면 진료 (문진)', [('문진은 ', WHITE), ('사실대로', MINT)])
ph = Phone(pil, 160, 220, 560, 770, '问诊 · 医生'); dd = ph.d; sx, sw = ph.sx, ph.sw
dd.rectangle((sx, ph.y, sx + sw, ph.sy + ph.sh - 30), fill=(237, 237, 237))
def cb(lines, me, y, col=None, big=False):
    f = F(700 if big else 500, 34 if big else 24); lw = max(tlen(l, f) for l in lines) + 36; lh = (46 if big else 36) * len(lines) + 24
    av = (sx + sw - 64, y) if me else (sx + 14, y)
    dd.rounded_rectangle((av[0], av[1], av[0] + 48, av[1] + 48), radius=10, fill=(90, 150, 230) if me else (60, 140, 120))
    ctext(dd, av[0] + 24, av[1] + 12, '나' if me else '医', F(900, 20), WHITE)
    bx_ = sx + sw - 76 - lw if me else sx + 74
    b = (bx_, y, bx_ + lw, y + lh); dd.rounded_rectangle(b, radius=12, fill=col or ((149, 236, 105) if me else (255, 255, 255)))
    for j, l in enumerate(lines): put(dd, bx_ + 18, y + 12 + j * (46 if big else 36), l, f, INK)
    return y + lh + 22, b
y_ = ph.y + 24
y_, b1 = cb(['您好，我是接诊医生。', '确认您已线下确诊，', '用过此药，无过敏、禁忌，', '以上符合请回复：是'], False, y_)
y_, b2 = cb(['是'], True, y_, big=True)
y_, b3 = cb(['处方已开具 ✓', '等待药师审核'], False, y_, col=(220, 245, 235))
d = ImageDraw.Draw(pil); hl(d, b1); hl(d, b2, MINT)
items = [('chat', '질환 · 복용 이력은 사실대로', 'mint'), ('check', "'是'는 사실일 때만", 'mint'), ('warn', '처음 복용 · 체중 목적 → 거절될 수 있음', 'red'), ('pharm', '거절되면 → 병원 진료', None)]
for i, (k_, t, kd) in enumerate(items):
    y = 240 + i * 182
    card(d, (790, y, 1820, y + 160), kd); photo(pil, 'us/' + {'chat': 'chat_1', 'check': 'check_1', 'warn': 'pharm_0', 'pharm': 'pharm_1'}[k_] + '.jpg', (804, y + 12, 1010, y + 148), r=14); d = ImageDraw.Draw(pil)
    f = F(900, 38 if len(t) < 18 else 32); put(d, 1036, y + 80 - th(f) / 2, t, f, (255, 170, 160) if kd == 'red' else WHITE)
mock(d); S.append(pil)

# ═══ 10. STEP 4 처방 → 결제
pil, d = frame(10, 'STEP 4', '처방전 발급 → 결제', [('처방 나오면 ', WHITE), ('바로 결제', YEL)])
flow = [('doc', '처방전 발급', '处方'), ('ok', '약사 심사', '药师审核'), ('pay', '결제하기', '去支付'), ('check', '주문 완료', '已下单')]
for i, (k_, t, zh) in enumerate(flow):
    cx = 310 + i * 433; x0 = cx - 190
    card(d, (x0, 250, x0 + 380, 640), 'yel' if i == 2 else None)
    photo(pil, 'us/' + {'doc': 'doc_0', 'ok': 'ok_2', 'pay': 'paydone_1', 'check': 'done_1'}[k_] + '.jpg', (x0 + 16, 266, x0 + 364, 462), r=16); d = ImageDraw.Draw(pil)
    ctext(d, cx, 500, t, F(900, 42), YEL if i == 2 else WHITE); ctext(d, cx, 570, zh, F(700, 30), SUB)
    if i < 3: arrow(d, x0 + 386, x0 + 428, 445, w=7)
for i, (k_, t, kd) in enumerate([('clock', '표시된 시간 안에 결제', 'red'), ('pay', '위챗페이 · 200위안 넘으면 수수료 3%', None)]):
    y = 680 + i * 140
    card(d, (100, y, 1820, y + 120), kd); sym(k_, 180, y + 60, 84); d = ImageDraw.Draw(pil)
    put(d, 260, y + 60 - th(F(900, 40)) / 2, t, F(900, 40), (255, 170, 160) if kd == 'red' else WHITE)
S.append(pil)

# ═══ 11. STEP 5 주문 확인 · 캡처
pil, d = frame(11, 'STEP 5', '주문 확인 · 캡처', [('캡처', RED), (' 3가지 남겨 두기', WHITE)])
def mini(x, y, w, h, title, lines, hl_i):
    d.rounded_rectangle((x, y, x + w, y + h), radius=20, fill=(246, 247, 250))
    d.rectangle((x, y + 50, x + w, y + 100), fill=(255, 255, 255)); ctext(d, x + w / 2, y + 62, title, F(700, 24), INK)
    yy = y + 124; out = None
    for j, (l, big) in enumerate(lines):
        f = F(900, 34) if big else F(500, 22)
        if big == 'bar':
            for k in range(36): d.rectangle((x + 60 + k * 11, yy, x + 60 + k * 11 + (3 if k % 3 else 6), yy + 80), fill=INK)
            out = (x + 40, yy - 12, x + w - 40, yy + 92); yy += 110; continue
        put(d, x + 30, yy, l, f, INK if big else GRAY)
        if j == hl_i: out = (x + 18, yy - 10, x + w - 18, yy + th(f) + 12)
        yy += th(f) + 30
    return out
cols = [('自提码 (픽업 코드)', '我的 › 待收货', [('待收货 · 待备货 → 已备货', False), ('', 'bar'), ('自提码  8 2 3 1 5 6', True)], 2),
        ('주문번호 · 끝 4자리', '全部订单信息', [('订单编号', False), ('3216 5489 0021', True), ('号码保护中', False), ('132****6261', True)], 3),
        ('처방전 원본', '处方详情', [('医生 · 互联网医院', False), ('处方单 原件', True), ('诊断 · 用药', False), ('[ 도장 찍힌 처방전 ]', True)], 1)]
for i, (t, tt, lines, hi_) in enumerate(cols):
    cx = 380 + i * 580; x0 = cx - 260
    card(d, (x0, 240, x0 + 520, 900), 'yel' if i == 2 else None)
    num(d, x0 + 46, 282, str(i + 1), 28); put(d, x0 + 90, 282 - th(F(900, 34)) / 2, t, F(900, 34), YEL if i == 2 else WHITE)
    b = mini(x0 + 30, 340, 460, 530, tt, lines, hi_)
    if b: hl(d, b)
card(d, (100, 920, 1820, 1000), 'red')
put(d, 140, 960 - th(F(900, 34)) / 2, '약국에서:  自提码  +  여권  보여 주기', F(900, 34), (255, 170, 160))
S.append(pil)

# ═══ 12. 주의
pil, d = frame(12, None, '주의', [('계정이 ', WHITE), ('막히지 않게', RED)])
warn = [('tap', '결제 버튼 여러 번 누르지 않기'), ('search', '새로고침 · 같은 검색 반복 X'), ('num', '임의 번호 넣지 않기 → 호텔 번호')]
for i, (k_, t) in enumerate(warn):
    y = 270 + i * 230
    card(d, (100, y, 1820, y + 190), 'red' if i < 2 else 'yel'); photo(pil, 'us/' + {'tap': 'tap_1', 'search': 'search_0', 'num': 'numok_0'}[k_] + '.jpg', (116, y + 14, 386, y + 176), r=16); d = ImageDraw.Draw(pil)
    sym('cross' if i < 2 else 'check', 1720, y + 95, 90); d = ImageDraw.Draw(pil)
    put(d, 420, y + 95 - th(F(900, 50)) / 2, t, F(900, 50), WHITE)
S.append(pil)

# ═══ 13. 구독 · 좋아요
pil, d = frame(13, None, None, [])
ctext(d, 960, 200, '도움이 되셨다면', F(700, 44), SUB)
runs(d, 960 - tlen('구독과 좋아요 부탁드려요', F(900, 84)) / 2, 290, [('구독', RED), ('과 ', WHITE), ('좋아요', RED), (' 부탁드려요', WHITE)], F(900, 84))
for j_, (k_, t_) in enumerate([('like', '좋아요'), ('play', '구독'), ('bell', '알림 설정')]):
    cx = 560 + j_ * 400; sym(k_, cx, 640, 220); d = ImageDraw.Draw(pil); ctext(d, cx, 790, t_, F(900, 44), WHITE)
card(d, (360, 880, 1560, 980))
ctext(d, 960, 900, '직접 경험이 아닌, 여러 후기를 조사해 정리한 내용입니다', F(900, 34), YEL)
ctext(d, 960, 948, '의학적 조언이 아니며 처방·용량은 반드시 의사와 상의하세요', F(500, 22), SUB)
S.append(pil)

for i, s in enumerate(S, 1): s.save(f'{P}/slides/{i:02d}.png')
S[0].save(f'{P}/qingdao_jd_order.pdf', save_all=True, append_images=[s.convert('RGB') for s in S[1:]], resolution=150)
print('ok', len(S))
