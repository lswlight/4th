#!/usr/bin/env python3
"""음성 이음 잡음('찍', '뻑', '틱') 방지·점검 도구. 파이썬 표준 라이브러리 + ffmpeg 만 쓴다.

  clean  : AI 내레이션 한 문장 정리 — 앞뒤의 짧은 '틱' 덩어리를 지우고, 말끝 여운은 끝까지 살린다.
  join   : 여러 음성을 압축 없이(WAV) 이어 붙인다. 이음매마다 짧은 페이드(또는 크로스페이드)를 넣는다.
  check  : 완성 음성·영상에서 튀는 소리와 갑자기 끊기는 곳을 찾아 시각을 알려 준다.

예)
  python3 audioqc.py clean raw.wav out.wav --tempo 1.0 --pad 0.3
  python3 audioqc.py join a.wav b.wav c.wav -o narration.wav --gap 0.3
  python3 audioqc.py join a.wav b.wav -o mix.wav --xfade 0.05
  python3 audioqc.py check final.mp4 --speed 1.0
"""
import argparse, array, math, subprocess, sys

SR = 48000


def decode(path, sr=SR):
    """ffmpeg 로 모노 16bit PCM 을 읽어 -1~1 실수 배열로."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    a = array.array('h'); a.frombytes(raw)
    return [v / 32768.0 for v in a]


def encode(samples, path, sr=SR, tempo=1.0):
    a = array.array('h', (max(-32767, min(32767, int(v * 32767))) for v in samples))
    af = ['-af', f'atempo={tempo}'] if abs(tempo - 1.0) > 1e-6 else []
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', '-'] + af +
                   ['-ac', '2', '-c:a', 'pcm_s16le', path], input=a.tobytes(), check=True)


def rms_db(samples, sr, win=0.01):
    n = int(sr * win); out = []
    for i in range(0, len(samples) - n + 1, n):
        s = 0.0
        for v in samples[i:i + n]: s += v * v
        out.append(10 * math.log10(s / n + 1e-18))
    return out


def groups(db, thr=-50.0, merge=25):
    """thr 를 넘는 창들을 merge 창(10ms 단위) 이내 간격이면 한 덩어리로."""
    g, i, n = [], 0, len(db)
    while i < n:
        if db[i] > thr:
            j = i
            while j < n and (db[j] > thr or any(x > thr for x in db[j:j + merge])): j += 1
            g.append([i, j]); i = j
        else:
            i += 1
    return g


def clean(samples, sr=SR, target_db=-18.0):
    db = rms_db(samples, sr); g = groups(db)
    if not g: return samples
    # 앞뒤 '틱': 80ms 이하로 짧고, 말소리와 200ms 이상 떨어진 덩어리
    while len(g) > 1 and g[0][1] - g[0][0] <= 8 and g[1][0] - g[0][1] >= 20: g.pop(0)
    while len(g) > 1 and g[-1][1] - g[-1][0] <= 8 and g[-1][0] - g[-2][1] >= 20: g.pop()
    w = int(sr * 0.01); s = max(0, g[0][0] - 3); e = g[-1][1]; k = 0
    while e < len(db) and db[e] > -60 and k < 30: e += 1; k += 1   # 말끝 여운 보존 (최대 0.3초)
    e = min(len(db), e + 2)
    out = samples[s * w:e * w]
    fi, fo = int(sr * 0.015), int(sr * 0.08)
    for i in range(min(fi, len(out))): out[i] *= i / fi
    for i in range(min(fo, len(out))): out[-1 - i] *= i / fo
    act = [v for v in out if abs(v) > 0.02] or out
    r = math.sqrt(sum(v * v for v in act) / len(act)) + 1e-12
    gain = 10 ** (target_db / 20) / r
    return [max(-0.97, min(0.97, v * gain)) for v in out]


def check(path, speed=1.0, sr=16000):
    x = decode(path, sr); db = rms_db(x, sr)
    peak = max((abs(v) for v in x), default=0.0)
    spikes, cuts = [], []
    for i in range(3, len(db) - 3):
        # 앞뒤 30ms 보다 20dB 이상 크게 혼자 튀는 10~30ms 덩어리
        if db[i] > -25 and db[i] - max(db[i - 3], db[i + 3]) > 20: spikes.append(i * 0.01)
        # 말소리 크기에서 바로 디지털 무음으로 뚝 끊김
        if db[i] > -35 and db[i + 1] < -90: cuts.append(i * 0.01)
    fmt = lambda t: f'{int(t // 60)}:{t % 60:05.2f}'
    print(f'최대 음량 {20 * math.log10(peak + 1e-12):.1f} dBFS (−1 dB 넘으면 깨짐 위험)')
    print(f'튀는 소리 {len(spikes)}곳: ' + ', '.join(fmt(t) for t in spikes[:20]))
    print(f'갑자기 끊김 {len(cuts)}곳: ' + ', '.join(fmt(t) for t in cuts[:20]))
    print('※ 말하는 중간의 ㅊ·ㅋ·ㅌ 자음도 튀는 소리로 잡힐 수 있다. 잡힌 시각은 귀로 확인한다.')
    return 1 if (cuts or peak > 0.89) else 0


def join(paths, out, gap=0.0, xfade=0.0, edge=0.03):
    if xfade > 0:
        ins = sum((['-i', p] for p in paths), [])
        chain, last = [], '[0:a]'
        for k in range(1, len(paths)):
            lab = f'[x{k}]'; chain.append(f'{last}[{k}:a]acrossfade=d={xfade}:c1=tri:c2=tri{lab}'); last = lab
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(chain), '-map', last,
                        '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_s16le', out], check=True)
        return
    allv = []
    for n, p in enumerate(paths):
        s = decode(p); e = int(SR * edge)
        for i in range(min(e, len(s))): s[i] *= i / e; s[-1 - i] *= i / e
        allv += s
        if gap > 0 and n < len(paths) - 1: allv += [0.0] * int(SR * gap)
    encode(allv, out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    c = sp.add_parser('clean'); c.add_argument('src'); c.add_argument('dst')
    c.add_argument('--tempo', type=float, default=1.0); c.add_argument('--pad', type=float, default=0.3)
    c.add_argument('--target-db', type=float, default=-18.0)
    j = sp.add_parser('join'); j.add_argument('src', nargs='+'); j.add_argument('-o', required=True)
    j.add_argument('--gap', type=float, default=0.0); j.add_argument('--xfade', type=float, default=0.0)
    k = sp.add_parser('check'); k.add_argument('src'); k.add_argument('--speed', type=float, default=1.0)
    a = ap.parse_args()
    if a.cmd == 'clean':
        s = clean(decode(a.src), target_db=a.target_db) + [0.0] * int(SR * a.pad)
        encode(s, a.dst, tempo=a.tempo); print(f'{a.dst}: {len(s) / SR / a.tempo:.2f}초')
    elif a.cmd == 'join':
        join(a.src, a.o, gap=a.gap, xfade=a.xfade); print(a.o)
    else:
        sys.exit(check(a.src, a.speed))


if __name__ == '__main__':
    main()
