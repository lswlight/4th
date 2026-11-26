"""모션그래픽: 장마다 배경·제목(slides_bg)을 먼저 보여 주고, 요소(카드·화면·박스)를 나레이션 시점에 맞춰
아래에서 떠오르며 나타나게 한다. 시각은 각 장 시작부터의 초. 1장(표지)은 제목 줄·사진이 순서대로 등장."""
import numpy as np, subprocess
from PIL import Image
FPS = 30
# (x0, y0, x1, y1), 등장 시각
SPEC = {
    2: [((0, 990, 1920, 1025), 0.0), ((100, 230, 660, 995), 1.2), ((660, 230, 1240, 995), 11.2), ((1240, 230, 1830, 995), 15.6)],
    3: [((100, 240, 660, 980), 0.8), ((680, 240, 1240, 980), 4.6), ((1260, 240, 1820, 980), 5.8)],
    4: [((80, 230, 660, 780), 3.7), ((660, 230, 1240, 780), 10.1), ((1240, 230, 1840, 780), 15.4), ((90, 790, 1830, 960), 25.5)],
    5: [((90, 230, 1010, 970), 0.3), ((1000, 280, 1840, 470), 5.0), ((1000, 480, 1840, 670), 6.6), ((1000, 680, 1840, 870), 8.8)],
    6: [((90, 230, 1010, 970), 0.2), ((1000, 250, 1840, 410), 0.8), ((1000, 420, 1840, 582), 1.8), ((1000, 592, 1840, 754), 2.8), ((1000, 764, 1840, 926), 4.0)],
    7: [((90, 230, 1010, 970), 0.2), ((1000, 280, 1840, 470), 0.9), ((1000, 480, 1840, 670), 2.3), ((1000, 680, 1840, 870), 3.8)],
    8: [((90, 230, 1830, 700), 0.4), ((90, 710, 1830, 970), 4.8)],
    9: [((90, 210, 870, 990), 0.6), ((930, 230, 1830, 410), 8.2), ((930, 420, 1830, 600), 11.2), ((930, 610, 1830, 790), 14.2), ((930, 810, 1830, 970), 17.8)],
    10: [((90, 230, 1110, 490), 3.5), ((90, 500, 1110, 760), 12.1), ((90, 770, 1110, 970), 15.0), ((1150, 230, 1830, 335), 17.7),
         ((1150, 335, 1830, 487), 18.2), ((1150, 487, 1830, 639), 19.0), ((1150, 639, 1830, 791), 21.3), ((1150, 791, 1830, 970), 22.4)],
    11: [((300, 180, 1620, 420), 18.8), ((400, 520, 720, 880), 19.3), ((800, 520, 1120, 880), 19.9), ((1200, 520, 1520, 880), 20.5)],
}
EMPH = {2: [((120, 240, 640, 905), 6.0, 11.2), ((700, 240, 1220, 905), 11.2, 15.6), ((1280, 240, 1800, 905), 15.6, 30)]}
def ease(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3

def render(n, dur, bg_path, fg_path, out, rise=40, fade=0.45):
    fg = np.asarray(Image.open(fg_path).convert('RGB')).astype(np.float32)
    bg = np.asarray(Image.open(bg_path).convert('RGB')).astype(np.float32) if bg_path else None
    if bg is None:   # 표지: 요소 바깥은 그대로, 요소 영역만 어둡게 시작
        bg = fg.copy()
        for (x0, y0, x1, y1), _ in SPEC[n]: bg[y0:y1, x0:x1] = fg[y0:y1, x0:x1] * 0.25 + np.array([8, 12, 24]) * 0.75
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    last = max(t for _, t in SPEC[n]) + fade
    for k in range(int(round(dur * FPS))):
        t = k / FPS
        if t > last + 0.1 and not EMPH.get(n): fr = fg
        else:
            fr = bg.copy()
            for (x0, y0, x1, y1), t0 in SPEC[n]:
                a = ease((t - t0) / fade)
                if a <= 0: continue
                dy = int(round((1 - a) * rise)); src = fg[y0:y1, x0:x1]
                ya, yb = y0 + dy, min(y1 + dy, 1080); h = yb - ya
                fr[ya:yb, x0:x1] = fr[ya:yb, x0:x1] * (1 - a) + src[:h] * a
        for (x0, y0, x1, y1), t0, t1 in EMPH.get(n, []):
            a = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.3))
            if a <= 0: continue
            sc = 1 + 0.07 * a; reg = Image.fromarray(fr[y0:y1, x0:x1].clip(0, 255).astype(np.uint8))
            w, h = int((x1 - x0) * sc), int((y1 - y0) * sc); reg = np.asarray(reg.resize((w, h), Image.LANCZOS)).astype(np.float32)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; X0, Y0 = cx - w // 2, cy - h // 2
            fr = fr.copy() if fr is fg else fr
            sh = 18; fr[Y0 + sh:Y0 + h + sh, X0 + 10:X0 + w + 10] *= 1 - 0.35 * a
            fr[Y0:Y0 + h, X0:X0 + w] = reg
        p.stdin.write(fr.clip(0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
