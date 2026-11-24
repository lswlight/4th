"""3편 조립: edl.json → 구간별 1080p 정규화(세로 영상은 흐린 배경 채움, 가림 처리) → 이어 붙이기 → 자막·배지 입히기."""
import json, subprocess, os, sys
P='/home/user/4th/media/part3'; TTF='/tmp/claude-0/-home-user-4th/1b6b0142-36e0-5974-9570-7e66779ccf2f/scratchpad/ttf'
E=json.load(open(f'{P}/edl.json')); os.makedirs(f'{P}/seg',exist_ok=True)
FPS=30
def probe_portrait(f):
    o=subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','stream_side_data=rotation','-of','csv=p=0',f]).decode()
    return '-90' in o or '90' in o
def vchain(s):
    """영상 필터: 회전 보정 → 가림 → 1920x1080 맞추기"""
    pre=[]
    if s.get('rot'): pre.append(s['rot'])
    for b in s.get('blur',[]):   # [x,y,w,h,t0,t1] (회전 후 원본 좌표, 비율 0~1)
        pass
    base=','.join(pre) if pre else 'null'
    return base
def build_seg(i,s):
    import hashlib
    extra=''
    for fk in ('img','vid','afile'):
        if s.get(fk) and os.path.exists(f"{P}/{s[fk]}"): extra+=str(os.path.getmtime(f"{P}/{s[fk]}"))
    key=hashlib.md5((json.dumps({k:v for k,v in s.items() if k!='force'},sort_keys=True,ensure_ascii=False)+extra).encode()).hexdigest()[:10]
    out=f'{P}/seg/h_{key}.mov'
    if os.path.exists(out) and not s.get('force'): return out
    dur=s['out']-s['in']
    if s.get('vid'):   # 모션그래픽 장면 (anim/*.mp4)
        vin=['-t',f'{dur}','-i',f"{P}/{s['vid']}"]
    elif s.get('img'):
        vin=['-loop','1','-framerate',str(FPS),'-t',f'{dur}','-i',f"{P}/{s['img']}"]
    else:
        vin=(['-noautorotate'] if s.get('raw') else [])+['-ss',str(s['in']),'-t',f"{dur*s.get('speed',1)}",'-i',f"{P}/raw/{s['clip']}.mp4"]
    ain_clip=None if s.get('afile') else s.get('aclip',s.get('clip'))
    if ain_clip: ain=(['-stream_loop','-1'] if s.get('aloop') else [])+['-ss',str(s.get('ain',s['in'])),'-t',f'{dur}','-i',f"{P}/raw/{ain_clip}.mp4"]
    elif s.get('afile'): ain=['-i',f"{P}/{s['afile']}"]
    else: ain=['-f','lavfi','-t',f'{dur}','-i','anullsrc=r=48000:cl=stereo']
    fc=[]
    if s.get('vid'):
        fc.append(f"[0:v]fps={FPS},setsar=1,format=yuv420p[v0]")
    elif s.get('img'):
        fc.append(f"[0:v]scale=3840:2160,zoompan=z='1+0.05*on/{int(dur*FPS)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS}[v0]")
    else:
        v='[0:v]'+(s['rot']+',' if s.get('rot') else '')
        # 가림: 지정 영역을 강하게 흐림 (rect 비율, 시간 구간)
        fc.append(f"{v}{'setpts=PTS/%s,'%s['speed'] if s.get('speed') else ''}fps={FPS},setsar=1[r]")
        cur='[r]'
        for k,(x,y,w,h,t0,t1) in enumerate(s.get('blur',[])):
            fc.append(f"{cur}split[a{k}][b{k}];[b{k}]crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},boxblur=40:5[c{k}];[a{k}][c{k}]overlay=W*{x}:H*{y}:enable='between(t,{t0},{t1})'[m{k}]")
            cur=f'[m{k}]'
        if s.get('fill'):   # 세로 화면을 가로로 꽉 채우기 (가운데 자르기)
            fc.append(f"{cur}scale=1920:-2,crop=1920:1080:0:(ih-1080)*0.45[v0]")
        elif s.get('portrait'):
            fc.append(f"{cur}split[p1][p2];[p1]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:4,eq=brightness=-0.12[bg];[p2]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0[v0]")
        else:
            fc.append(f"{cur}scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v0]")
    fade=0.05
    vf_in=0.6 if 'in' in s.get('vfade',[]) else 0; vf_out=0.6 if 'out' in s.get('vfade',[]) else 0
    g=s.get('gain',0)
    af=f"aresample=48000,aformat=channel_layouts=stereo,{'apad,' if s.get('afile') else ''}highpass=f=90,volume={g}dB,afade=t=in:d={max(fade,vf_in,s.get('afin',0))},afade=t=out:st={max(0,dur-max(fade,vf_out))}:d={max(fade,vf_out)}"
    if s.get('mute'): af=f"aresample=48000,aformat=channel_layouts=stereo,volume=-60dB"
    if vf_in or vf_out:
        fc[-1]=fc[-1].replace('[v0]','[v00]')
        fc.append(f"[v00]{'fade=t=in:d=%s,'%vf_in if vf_in else ''}{'fade=t=out:st=%s:d=%s,'%(dur-vf_out,vf_out) if vf_out else ''}null[v0]")
    fc.append(f"[1:a]{af}[a0]")
    subprocess.run(['ffmpeg','-v','error','-y',*vin,*ain,'-filter_complex',';'.join(fc),'-map','[v0]','-map','[a0]','-t',f'{dur}',
                    '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000',out],check=True)
    return out
segs=[build_seg(i,s) for i,s in enumerate(E['segs'])]
open(f'{P}/segs.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{P}/segs.txt','-c','copy',f'{P}/joined.mov'],check=True)
# 자막 (구간 시작 시각 + 구간 안 상대시각)
def ts(x): return f'{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}'
ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','','[V4+ Styles]',
 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
 'Style: Sub,Noto Sans KR,52,&H00271811,&H00271811,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,16,0,2,300,300,56,1',
 'Style: Tag,Noto Sans KR,40,&H0020120B,&H0020120B,&H004DD8FF,&H004DD8FF,1,0,0,0,100,100,0,0,3,12,0,7,104,0,150,1',
 'Style: Big,Black Han Sans,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H66000000,0,0,0,0,100,100,0,0,1,8,0,5,80,80,0,1','',
 '[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
t=0; hide=[]
for s in E['segs']:
    d=s['out']-s['in']
    for a,b,txt in s.get('subs',[]):
        a0=max(0,a-s.get('ain',s['in'])); b0=min(d,b-s.get('ain',s['in']))
        if b0>a0: ass.append(f'Dialogue: 0,{ts(t+a0)},{ts(t+b0-0.02)},Sub,,0,0,0,,{txt}')
    if s.get('tag'): ass.append(f"Dialogue: 1,{ts(t)},{ts(t+min(d,4))},Tag,,0,0,0,,{s['tag']}")
    if s.get('big'): ass.append(f"Dialogue: 2,{ts(t)},{ts(t+d)},Big,,0,0,0,,{s['big']}")
    if s.get('vid') or s.get('nobadge'): hide.append((t,t+d))
    t+=d
open(f'{P}/part3.ass','w',encoding='utf-8').write('\n'.join(ass)+'\n')
en='+'.join(f'between(t,{a:.2f},{b:.2f})' for a,b in hide) or '0'
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{P}/joined.mov','-i',f'{P}/anim/overlay.png','-filter_complex',
  f"[0:v][1:v]overlay=0:0:enable='not({en})'[v1];[v1]subtitles={P}/part3.ass:fontsdir={TTF},setpts=PTS/1.05,fps=30[v]",'-map','[v]','-map','0:a','-af','atempo=1.05,adeclick,alimiter=limit=0.9:level=disabled',
  '-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',f'{P}/part3_draft.mp4'],check=True)
print('total',round(t,1))
