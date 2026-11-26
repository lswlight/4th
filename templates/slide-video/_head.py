"""슬라이드 영상 틀 · 공통 헬퍼 (글꼴·색·카드·휴대폰 예시 화면·콜아웃). 칭다오 마운자로 1·2편에서 만든 것.
휴대폰 화면은 이해를 돕는 예시 그림(실제 앱과 다를 수 있음). 문진은 사실대로 답하기만 안내."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
P = os.path.dirname(os.path.abspath(__file__))
T = os.environ.get('SV_FONTS', os.path.expanduser('~/.cache/slide-video/fonts'))   # get_fonts.sh 로 받은 글꼴 폴더
ZH = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
W, H, N = 1920, 1080, 13
_fc = {}
def F(w, s):
    k = (w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(f'{T}/NotoSansKR-{w}.ttf', s)
    return _fc[k]

# ── 색
BG0, BG1 = (12, 17, 32), (24, 32, 60)
WHITE, SUB, MUTE = (244, 247, 253), (168, 180, 206), (110, 122, 152)
RED, RED_D = (232, 52, 44), (120, 30, 32)
YEL, MINT, BLUE, PURP = (255, 206, 84), (80, 220, 170), (110, 170, 255), (170, 130, 255)
CARD, CARD_BD = (27, 36, 64), (50, 62, 96)
INK, GRAY, LINE = (26, 30, 40), (130, 136, 150), (232, 234, 240)

# ── 한글 글꼴에 없는 간체자는 중국어 글꼴로
_kf = ImageFont.truetype(f'{T}/NotoSansKR-500.ttf', 40); _nd = bytes(_kf.getmask('\U000F0000')); _has = {}
def has_kr(ch):
    if ch not in _has: _has[ch] = ord(ch) < 0x2E80 or bytes(_kf.getmask(ch)) != _nd
    return _has[ch]
def segs(text, font):
    zf = ImageFont.truetype(ZH, font.size); out = []
    mixed = any(not has_kr(c) for c in text)
    for ch in text:
        cjk = 0x3000 <= ord(ch) <= 0x9FFF or 0xFF00 <= ord(ch) <= 0xFFEF
        f = zf if (not has_kr(ch) or (mixed and cjk)) else font
        if out and out[-1][1] is f: out[-1][0] += ch
        else: out.append([ch, f])
    return out
def bold(font): return '700' in font.path or '900' in font.path
def tlen(text, font): return sum(f.getlength(t) + (len(t) if (f is not font and bold(font)) else 0) for t, f in segs(text, font))
def put(d, x, top, text, font, fill):
    gb = font.getbbox('가'); base = top - gb[1]
    for t, f in segs(text, font):
        dy = 0 if f is font else (gb[1] + gb[3]) / 2 - sum(f.getbbox('中')[1::2]) / 2
        sw = 1 if (f is not font and bold(font)) else 0
        d.text((x, base + dy), t, font=f, fill=fill, stroke_width=sw, stroke_fill=fill); x += f.getlength(t) + sw * len(t)
    return x
def runs(d, x, top, parts, font):
    for t, c in parts: x = put(d, x, top, t, font, c)
    return x
def ctext(d, cx, top, t, f, c): put(d, cx - tlen(t, f) / 2, top, t, f, c)
def th(f): b = f.getbbox('가'); return b[3] - b[1]

def emoji(pil, ch, cx, cy, size):
    im = Image.new('RGBA', (180, 180), (0, 0, 0, 0)); ImageDraw.Draw(im).text((20, 20), ch, font=EMO, embedded_color=True)
    im = im.crop(im.getbbox()); k = size / max(im.size)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    pil.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)
def icon(pil, d, ch, cx, cy, r, ring=(64, 78, 116), fill=(34, 45, 80)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=ring, width=3); emoji(pil, ch, cx, cy, int(r * 1.1))
def pill(d, x, y, t, f, fill, color, padx=20, h=48, outline=None):
    w = tlen(t, f); d.rounded_rectangle((x, y, x + w + padx * 2, y + h), radius=h // 2, fill=fill, outline=outline, width=2 if outline else 0)
    put(d, x + padx, y + (h - th(f)) / 2, t, f, color); return x + w + padx * 2
def card(d, box, kind=None, r=26):
    fill, bd = {None: (CARD, CARD_BD), 'red': ((58, 24, 30), (200, 70, 64)), 'mint': ((16, 52, 50), (60, 190, 150)),
                'yel': ((54, 46, 28), (200, 165, 80)), 'blue': ((22, 42, 80), (90, 140, 230))}[kind]
    d.rounded_rectangle(box, radius=r, fill=fill, outline=bd, width=2)
def num(d, cx, cy, t, r=24, fill=YEL, color=(30, 24, 10)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill); f = F(900, int(r * 1.15)); ctext(d, cx, cy - th(f) / 2 - 1, t, f, color)
def arrow(d, x0, x1, y, col=(120, 135, 170), w=6):
    d.line((x0, y, x1 - 16, y), fill=col, width=w); d.polygon([(x1, y), (x1 - 24, y - 16), (x1 - 24, y + 16)], fill=col)
def darrow(d, x, y0, y1, col=(120, 135, 170), w=6):
    d.line((x, y0, x, y1 - 16), fill=col, width=w); d.polygon([(x, y1), (x - 16, y1 - 24), (x + 16, y1 - 24)], fill=col)
def lead(d, pts, col=YEL, w=3):
    d.line(pts, fill=col, width=w, joint='curve'); x, y = pts[-1]; d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col)

# ── 배경
def make_bg():
    gx, gy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H)); t = (gx * .55 + gy * .45)[..., None]
    img = np.array(BG0) * (1 - t) + np.array(BG1) * t
    def glow(cx, cy, r, col, a):
        dd = np.sqrt(((gx - cx) * W) ** 2 + ((gy - cy) * H) ** 2) / r
        return np.clip(1 - dd, 0, 1)[..., None] ** 2 * a * (np.array(col) - img)
    img = img + glow(.95, .02, 900, (90, 30, 50), .55) + glow(.0, 1.0, 900, (30, 60, 120), .45)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))
BG = make_bg()
# 제품 상자 누끼(투명 PNG)를 src/box_cut.png 로 두면 휴대폰 예시 화면에 쓰인다. 없으면 회색 상자로 대신.
if os.path.exists(f'{P}/src/box_cut.png'): BOX = Image.open(f'{P}/src/box_cut.png').convert('RGBA')
else:
    BOX = Image.new('RGBA', (290, 670), (0, 0, 0, 0)); ImageDraw.Draw(BOX).rounded_rectangle((10, 10, 280, 660), radius=16, fill=(225, 228, 236, 255), outline=(150, 160, 180, 255), width=4)
def box_img(h): return BOX.resize((int(BOX.width * h / BOX.height), h), Image.LANCZOS)
def shadow_paste(pil, img, x, y, glow=True):
    if glow:
        g = Image.new('L', (W, H), 0); cx = x + img.width // 2
        ImageDraw.Draw(g).ellipse((cx - img.width, y + 20, cx + img.width, y + img.height - 20), fill=60)
        pil.paste(Image.new('RGB', (W, H), (90, 120, 190)), (0, 0), g.filter(ImageFilter.GaussianBlur(80)))
    sh = Image.new('L', (W, H), 0); sh.paste(img.split()[3], (x + 16, y + 20))
    pil.paste(Image.new('RGB', (W, H), (4, 6, 14)), (0, 0), sh.point(lambda v: int(v * .6)).filter(ImageFilter.GaussianBlur(20)))
    pil.paste(img, (x, y), img)

FOOT = os.environ.get('SV_FOOT', '시리즈 이름 · 편 이름')   # 오른쪽 위 작은 글씨 (build_deck.py 에서 바꿔도 됨)
def frame(n, step, label, title):
    pil = BG.copy(); d = ImageDraw.Draw(pil)
    # 위: 단계 배지 + 이름
    x = 100
    if step: x = pill(d, 100, 52, step, F(900, 24), RED, WHITE, padx=18, h=44) + 14
    if label: put(d, x, 63, label, F(700, 24), SUB)
    put(d, 1820 - tlen(FOOT, F(500, 20)), 64, FOOT, F(500, 20), MUTE)
    runs(d, 100, 124, title, F(900, 58))
    # 아래: 진행 점 + 쪽 번호
    for i in range(N):
        cx = 100 + i * 26; on = i < n
        d.rounded_rectangle((cx, 1034, cx + (40 if i == n - 1 else 16), 1044), radius=5, fill=RED if i == n - 1 else ((150, 160, 190) if on else (52, 62, 92)))
    put(d, 1820 - tlen(f'{n} / {N}', F(700, 22)), 1026, f'{n} / {N}', F(700, 22), SUB)
    return pil, d
def note(d, t, y=990, x=100):
    put(d, x, y, t, F(500, 20), MUTE)

# ── 휴대폰 화면 예시
class Phone:
    def __init__(s, pil, x, y, w=430, h=820, title=None, back=True):
        s.pil, s.d = pil, ImageDraw.Draw(pil)
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x + 10, y + 18, x + w + 10, y + h + 18), radius=64, fill=150)
        pil.paste(Image.new('RGB', (W, H), (3, 5, 12)), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
        s.d.rounded_rectangle((x, y, x + w, y + h), radius=62, fill=(18, 20, 26), outline=(90, 96, 112), width=3)
        s.sx, s.sy, s.sw, s.sh = x + 14, y + 14, w - 28, h - 28
        s.d.rounded_rectangle((s.sx, s.sy, s.sx + s.sw, s.sy + s.sh), radius=50, fill=(246, 247, 250))
        s.d.rounded_rectangle((x + w / 2 - 60, y + 24, x + w / 2 + 60, y + 52), radius=14, fill=(18, 20, 26))
        put(s.d, s.sx + 34, s.sy + 18, '9:41', F(700, 20), INK)
        s.y = s.sy + 60
        if title:
            s.d.rectangle((s.sx, s.y, s.sx + s.sw, s.y + 66), fill=(255, 255, 255))
            if back: put(s.d, s.sx + 20, s.y + 20, '‹', F(700, 30), INK)
            ctext(s.d, s.sx + s.sw / 2, s.y + 20, title, F(700, 25), INK)
            s.d.line((s.sx, s.y + 66, s.sx + s.sw, s.y + 66), fill=LINE, width=2); s.y += 66
    def X(s, a): return s.sx + a
    def row(s, label, value, h=74, vcol=INK, hl=None):
        d = s.d; y = s.y
        d.rectangle((s.sx, y, s.sx + s.sw, y + h), fill=(255, 255, 255)); d.line((s.sx + 20, y + h, s.sx + s.sw - 20, y + h), fill=LINE, width=2)
        put(d, s.sx + 22, y + (h - th(F(500, 21))) / 2, label, F(500, 21), GRAY)
        put(d, s.sx + 132, y + (h - th(F(700, 22))) / 2, value, F(700, 22), vcol)
        if hl: d.rounded_rectangle((s.sx + 6, y + 4, s.sx + s.sw - 6, y + h - 4), radius=12, outline=hl, width=4)
        s.y += h; return (s.sx, y, s.sx + s.sw, y + h)
    def gap(s, g=14): s.y += g
    def button(s, t, y=None, col=RED):
        y = y or s.sy + s.sh - 100; d = s.d
        d.rounded_rectangle((s.sx + 22, y, s.sx + s.sw - 22, y + 64), radius=32, fill=col)
        ctext(d, s.sx + s.sw / 2, y + 20, t, F(700, 24), (255, 255, 255)); return (s.sx + 22, y, s.sx + s.sw - 22, y + 64)

def callouts(d, items, x=700, y0=250, gap=150, wid=1120):
    """오른쪽 번호 설명: (번호, 제목, 설명, 강조색)"""
    out = []
    for i, it in enumerate(items):
        n, t, s_ = it[:3]; kind = it[3] if len(it) > 3 else None; y = y0 + i * gap
        card(d, (x, y, x + wid, y + gap - 22), kind)
        num(d, x + 52, y + (gap - 22) / 2, n, 26)
        put(d, x + 100, y + 26, t, F(900, 34), WHITE)
        if s_: put(d, x + 100, y + 80, s_, F(500, 25), SUB)
        out.append((x, y + (gap - 22) / 2))
    return out

