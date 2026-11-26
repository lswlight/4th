"""징동편 영상: 녹음 3개(j1·j2·j3)에서 잘된 부분만 이어 붙이고, 슬라이드(모션그래픽)·자막을 맞춘다.
- j1 86.4~94.6(문진 첫 녹음)은 j2 앞부분(다시 녹음)으로 대체
- j2 55.9~끝(마무리 첫 녹음, '번호를 받았기' 말실수)은 j3(다시 녹음)으로 대체
- 2·3장(전체 순서·준비물)은 녹음에 없어 넣지 않음. 표지는 2.5초 무음으로 시작."""
import json, subprocess, os, sys
P = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, P)
TTF = os.environ.get('SV_FONTS', os.path.expanduser('~/.cache/slide-video/fonts'))
run = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
if not os.path.exists(f'{P}/rec/sil.m4a'):
    run('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono', '-t', '3', '-c:a', 'aac', f'{P}/rec/sil.m4a')

FILES = ['sil', 'j0', 'j1', 'j2', 'j3']
# 슬라이드 번호 → (파일, 시작, 끝, 뒤 쉼) 목록
CLIPS = [(1, [('sil', 0, 2.5, 0)]),
         (3, [('j0', 0.3, 25.3, 0.7)]),
         (4, [('j1', 0.25, 7.15, 0.6)]),
         (5, [('j1', 9.9, 21.5, 0.6)]),
         (6, [('j1', 24.5, 33.35, 0.35), ('j1', 34.15, 47.5, 0.7)]),
         (7, [('j1', 51.15, 62.75, 0.7)]),
         (8, [('j1', 67.65, 78.25, 0.6)]),
         (9, [('j1', 80.15, 85.95, 0.35), ('j2', 0.2, 14.0, 0.8)]),
         (10, [('j2', 16.8, 28.7, 0.45)]),
         (11, [('j2', 29.3, 37.8, 0.7)]),
         (12, [('j2', 39.15, 55.2, 0.8)]),
         (13, [('j3', 0.1, 16.2, 0.6)])]
SEG = [c for _, cs in CLIPS for c in cs]
OFF = []; acc = 0
for f, a_, b_, g in SEG: OFF.append(acc); acc += (b_ - a_) + g
TOTAL = acc
def nt(t, f):
    for (ff, a_, b_, g), o in zip(SEG, OFF):
        if ff == f and a_ - 1e-6 <= t <= b_ + 1e-6: return o + t - a_
    return None
SL = [n for n, _ in CLIPS]
starts = []; k = 0
for n, cs in CLIPS: starts.append(OFF[k]); k += len(cs)
starts.append(TOTAL)
durs = [starts[i + 1] - starts[i] for i in range(len(SL))]
XF = 0.45

# ── 단어 시각 (모션그래픽 등장 시점)
STT = {f: json.load(open(f'{P}/rec/stt_{f}.json')) for f in ('j0', 'j1', 'j2', 'j3')}
def cue(n, f, word, after=0.0, d=0.0):
    for s in STT[f]:
        for w0, w1, w in s['words']:
            if w0 >= after and word in w:
                g = nt(w0, f); i_ = SL.index(n)
                if g is not None and starts[i_] - 0.5 <= g < starts[i_ + 1]: return max(0.1, g - starts[i_] + d)
    raise KeyError((n, f, word))
CR = lambda ys, h, x0=1000, x1=1820: [(x0, y, x1, y + h) for y in ys]
c4 = CR([260, 432, 604, 776], 148)
SPEC = {
    3: [((310 + i * 433 - 205, 245, 310 + i * 433 + 205, 805), t) for i, t in enumerate(
        [cue(3, 'j0', '여권'), cue(3, 'j0', '호텔'), cue(3, 'j0', '11자리'), cue(3, 'j0', '결제를')])]
       + [((95, 835, 1825, 965), cue(3, 'j0', '없으면'))],
    4: [((230, 220, 735, 995), 0.1), ((735, 220, 1000, 995), cue(4, 'j1', '가입')), (c4[0], cue(4, 'j1', '가입')),
        (c4[1], cue(4, 'j1', '한국')), (c4[2], cue(4, 'j1', '한국', d=1.0)), (c4[3], cue(4, 'j1', '위채'))],
    5: [((230, 220, 735, 995), 0.1), ((1000, 232, 1820, 382), cue(5, 'j1', '마이')), ((735, 220, 1000, 995), cue(5, 'j1', '새', after=12)),
        ((1000, 410, 1820, 526), cue(5, 'j1', '새', after=12)), ((1000, 550, 1820, 666), cue(5, 'j1', '새', after=12, d=0.7)),
        ((1000, 690, 1820, 806), cue(5, 'j1', '호텔을')), ((1000, 830, 1820, 946), cue(5, 'j1', '선택'))],
    6: [((160, 220, 665, 995), 0.1), ((665, 230, 1830, 480), cue(6, 'j1', '구매를')), ((740, 495, 1830, 970), cue(6, 'j1', '우측에'))],
    7: [((230, 220, 735, 995), 0.1), ((735, 220, 1000, 995), cue(7, 'j1', '픽업')), (c4[0], cue(7, 'j1', '픽업')),
        (c4[1], cue(7, 'j1', '호텔')), (c4[2], cue(7, 'j1', '픽업시간')), (c4[3], cue(7, 'j1', '수량을'))],
    8: [((230, 220, 735, 995), 0.1), ((735, 220, 1000, 995), cue(8, 'j1', '신분증을', after=69)),
        ((1000, 300, 1820, 476), cue(8, 'j1', '신분증을', after=69)), ((1000, 500, 1820, 676), cue(8, 'j1', '여권번호와')),
        ((1000, 700, 1820, 876), cue(8, 'j1', '영문'))],
    9: [((160, 220, 725, 995), 0.1)] + [((790, 240 + i * 182, 1830, 400 + i * 182), t) for i, t in enumerate(
        [cue(9, 'j2', '사실대로'), cue(9, 'j2', '사실', after=11), cue(9, 'j2', '사실', after=11, d=1.4), cue(9, 'j2', '사실', after=11, d=2.4)])],
    10: [((310 + i * 433 - 190, 250, 310 + i * 433 + 245, 645), t) for i, t in enumerate(
        [cue(10, 'j2', '처방이'), cue(10, 'j2', '약사'), cue(10, 'j2', '약사', d=1.6), cue(10, 'j2', '최종적으로')])]
        + [((100, 675, 1830, 805), cue(10, 'j2', '완료되고', d=0.3)), ((100, 815, 1830, 945), cue(10, 'j2', '완료되고', d=0.9))],
    11: [((380 + i * 580 - 262, 238, 380 + i * 580 + 262, 905), t) for i, t in enumerate(
        [cue(11, 'j2', '코드'), cue(11, 'j2', '번호'), cue(11, 'j2', '처방전')])] + [((100, 915, 1830, 1005), cue(11, 'j2', '반드시'))],
    12: [((100, 270 + i * 230, 1830, 465 + i * 230), t) for i, t in enumerate(
        [cue(12, 'j2', '결제'), cue(12, 'j2', '같은'), cue(12, 'j2', '임의로')])],
    13: [((355, 875, 1565, 985), 0.3), ((300, 180, 1620, 420), cue(13, 'j3', '도움이')),
         ((400, 520, 720, 880), cue(13, 'j3', '도움이', d=0.5)), ((800, 520, 1120, 880), cue(13, 'j3', '도움이', d=1.0)),
         ((1200, 520, 1520, 880), cue(13, 'j3', '도움이', d=1.5))],
}

if __name__ == '__main__':
    SUBS_ONLY = os.environ.get('SUBS_ONLY') == '1'   # 자막만 바꿀 때: 음성·슬라이드 클립 재사용
    # ── 1) 음성
    fc = ''
    for i, (f, a_, b_, g) in enumerate(SEG):
        fi = FILES.index(f)
        fc += f"[{fi}:a]atrim={a_}:{b_},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.03,afade=t=out:st={b_ - a_ - 0.06:.3f}:d=0.06,apad=pad_dur={g}[a{i}];"
    fc += ''.join(f'[a{i}]' for i in range(len(SEG))) + f'concat=n={len(SEG)}:v=0:a=1[c];'
    fc += "[c]highpass=f=80,afftdn=nf=-25,acompressor=threshold=-22dB:ratio=2.5:attack=10:release=200,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.89:level=disabled[out]"
    args = []
    for f in FILES: args += ['-i', f'{P}/rec/{f}.m4a']
    if not SUBS_ONLY: run(*args, '-filter_complex', fc, '-map', '[out]', '-c:a', 'aac', '-b:a', '192k', f'{P}/rec/voice_edit.m4a')

    # ── 2) 슬라이드 클립
    import mg; mg.SPEC = SPEC; mg.EMPH = {}
    os.makedirs(f'{P}/vid', exist_ok=True)
    NS = len(SL)
    for i, n in enumerate(SL if not SUBS_ONLY else []):
        d = durs[i] + (XF if i < NS - 1 else 0); fr = int(d * 30) + 1
        if n in SPEC:
            mg.render(n, d, f'{P}/slides_bg/{n:02d}.png', f'{P}/slides/{n:02d}.png', f'{P}/vid/{i:02d}.mp4'); continue
        z = "min(1+0.035*on/{},1.035)".format(fr)
        run('-loop', '1', '-i', f'{P}/slides/{n:02d}.png', '-vf',
            f"scale=3840:2160,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1920x1080:fps=30,format=yuv420p",
            '-t', f'{d:.3f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', f'{P}/vid/{i:02d}.mp4')
    inp = []; [inp.extend(['-i', f'{P}/vid/{i:02d}.mp4']) for i in range(NS)]
    fc = ''; prev = '0:v'; acc = durs[0] + XF
    for i in range(1, NS):
        off = acc - XF
        fc += f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}];"
        prev = f'x{i}'; acc = off + durs[i] + (XF if i < NS - 1 else 0)
    if not SUBS_ONLY: run(*inp, '-filter_complex', fc.rstrip(';'), '-map', f'[{prev}]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', f'{P}/vid/joined.mp4')

    # ── 3) 자막 (받아쓰기 시각 + 바로잡은 글자)
    FIX = {('j0', 0.46): '준비물은 3가지입니다.', ('j0', 2.38): '여권,', ('j0', 4.14): '중국 내 호텔 주소,',
           ('j0', 7.1): '호텔에서 받은 중국 11자리 번호,', ('j0', 10.3): '그리고 결제 수단입니다.',
           ('j0', 12.78): '이때 호텔에서 제공받은 11자리 중국 휴대폰 번호가 없으면', ('j0', 18.68): '진행하지 말고',
           ('j0', 20.04): '다시 이 번호부터 확보한 뒤에 진행하셔야 합니다.',
           ('j1', 0.37): '징동 가입 방법입니다.',
           ('j1', 2.65): '한국 번호로 가입을 해도 되고, 위챗으로 로그인을 해도 됩니다.',
           ('j1', 10.06): '가입 후에는 징동에서 마이 → 설정에서 새 주소를 추가해야 합니다.',
           ('j1', 16.4): '이때 새 주소에는 호텔을 선택하시면 됩니다.',
           ('j1', 24.65): '그리고 징동에서 마운자로를 구매합니다.',
           ('j1', 28.19): '우측에 보시는 것과 같이 마운자로 용량별 금액이 있습니다.',
           ('j1', 34.29): '중국은 한국·일본과 다르게 펜을 나눠서 (처방 용량대로) 사용할 수 있다고 하니',
           ('j1', 41.81): '이 부분을 고려해서 필요한 용량을 한 가지 용량으로 구매하시면 됩니다.',
           ('j1', 51.29): '픽업 탭으로 넘어가서 약국에서 수령하는 것으로 하시면 됩니다.',
           ('j1', 56.35): '호텔 근처 약국으로 설정하시고, 대략적인 픽업 시간 그리고 수량을 기입합니다.',
           ('j1', 67.79): '다음으로는 신분증을 변경해야 합니다.',
           ('j1', 69.85): '신분증을 여권으로 변경하고, 여권 번호와 여권 영문 이름을 그대로 작성합니다.',
           ('j1', 80.3): '그다음에는 비대면 진료입니다.',
           ('j1', 82.56): '비대면 진료는 채팅을 통해서 하게 됩니다.',
           ('j2', 0.34): '여권 정보를 입력하면 문진 화면으로 넘어가게 됩니다.',
           ('j2', 4.84): '의사가 배정되면 문진을 진행하게 되고',
           ('j2', 8.56): '문진 시에는 최대한 사실대로 이야기를 하고',
           ('j2', 11.06): "사실일 때는 '是(스)'라고 적으시면 됩니다.",
           ('j2', 16.92): '문진 후에 처방이 나오고, 처방이 나오면 결제를 하시면 됩니다.',
           ('j2', 21.76): '결제하기 전에 약사 심사가 있는데, 이 부분은 기다리시면 될 듯합니다.',
           ('j2', 26.38): '최종적으로 주문이 완료되고',
           ('j2', 29.46): '주문이 완료되면 픽업 코드, 주문 번호 그리고 처방전 원본을',
           ('j2', 34.52): '반드시 가지고 계셔야 합니다.',
           ('j2', 39.31): '이때 주의할 점은, 계정이 막히면 안 되기 때문에',
           ('j2', 42.63): '결제 버튼을 여러 번 누르지 않고',
           ('j2', 45.4): '같은 검색을 반복하지 않으며',
           ('j2', 48.68): '임의로 번호를 넣으면 안 됩니다.',
           ('j2', 50.65): '반드시 호텔에서 받은 휴대폰 번호를 입력하시길 바랍니다.',
           ('j3', 0.27): '저 같은 경우에는 일본에서 이미 마운자로를 받았기 때문에',
           ('j3', 4.29): '추가적으로 중국에서 마운자로를 받을 수가 없어서',
           ('j3', 8.05): '제가 조사한 내용을 공유드립니다.',
           ('j3', 11.11): '도움이 되셨다면 구독과 좋아요 부탁드리겠습니다.',
           ('j3', 15.11): '감사합니다.'}
    ev = []
    for f in ('j0', 'j1', 'j2', 'j3'):
        for s_ in STT[f]:
            a_, b_ = nt(s_['start'], f), nt(min(s_['end'], s_['words'][-1][1]), f)
            if a_ is None: continue
            if b_ is None: b_ = a_ + (s_['end'] - s_['start'])
            ev.append([a_, b_, FIX[(f, round(s_['start'], 2))]])
    ev.sort()
    for i in range(len(ev) - 1): ev[i][1] = min(ev[i + 1][0] - 0.05, ev[i][1] + 0.5)
    ev[-1][1] = min(TOTAL, ev[-1][1] + 1.0)
    def ts(x): return f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
    ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080', 'WrapStyle: 0', '', '[V4+ Styles]',
           'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
           'Style: Sub,Noto Sans KR,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H9A000000,1,0,0,0,100,100,0,0,3,14,0,2,140,140,26,1',
           'Style: Note,Noto Sans KR,26,&H00D0D8E8,&H00D0D8E8,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,3,10,0,8,140,140,30,1', '',
           '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    ass += [f'Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{t}' for a, b, t in ev]
    ass.append(f"Dialogue: 0,{ts(starts[-2])},{ts(TOTAL)},Note,,0,0,0,,※ 여러 후기를 조사해 정리한 정보이며 의학적 조언이 아닙니다 · 처방과 용량은 반드시 의사와 상의하세요")
    open(f'{P}/vid/subs.ass', 'w', encoding='utf-8').write('\n'.join(ass) + '\n')

    # ── 4) 합치기
    run('-i', f'{P}/vid/joined.mp4', '-i', f'{P}/rec/voice_edit.m4a', '-filter_complex',
        f"[0:v]subtitles={P}/vid/subs.ass:fontsdir={TTF},fade=t=in:d=0.6,fade=t=out:st={TOTAL - 0.8:.2f}:d=0.8[v]",
        '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', f'{P}/qingdao_jd_order.mp4')
    json.dump({'slides': SL, 'starts': starts, 'total': TOTAL}, open(f'{P}/vid/timeline.json', 'w'))
    print('done', round(TOTAL, 1), 's', len(ev), 'subs', [round(s, 1) for s in starts])
