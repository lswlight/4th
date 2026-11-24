"""3편 세로 예고(9:16): 위 고정 제목(도현체) + 가운데 가로 영상 + 아래 자막 → 인스타 릴스·유튜브 쇼츠 공용.
소리 규칙(audio.md): 구간 소리는 PCM, 구간 앞뒤 40ms 페이드, 압축은 마지막 한 번, adeclick + 리미터."""
import subprocess, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
P='/home/user/4th/media/part3'; T=f'{P}/teaser'; R=f'{P}/raw'
TTF='/tmp/claude-0/-home-user-4th/1b6b0142-36e0-5974-9570-7e66779ccf2f/scratchpad/ttf'
W,H=1080,1920; VY=640; VH=608; FPS=30; SPEED=1.1
YEL=(255,221,0); WHT=(255,255,255); BLK=(0,0,0)
DH=lambda s:ImageFont.truetype(f'{TTF}/DoHyeon.ttf',s); F=lambda w,s:ImageFont.truetype(f'{TTF}/NotoSansKR-{w}.ttf',s)
os.makedirs(f'{T}/seg',exist_ok=True)
D='20261123_'
SEGS=[
 dict(v=D+'115248',vin=0.0,a=D+'115248',ain=0.0,dur=1.9,blur=True,tag='11/23 · 대마도 히타카츠',
      subs=[[0.0,1.8,'물건을 수령했습니다.']]),
 dict(v=D+'115400',vin=0.0,a=D+'115400',ain=0.0,dur=11.65,raw=True,tag='마운자로 12펜 수령',
      subs=[[0.0,3.4,'총 12펜을 신청했습니다.'],[3.5,7.6,'하나, 둘, 셋, 넷, 다섯, 여섯.'],[7.7,11.6,'한 통에 두 개씩, 확인했습니다.']]),
 dict(v=D+'111547',vin=0.0,a=D+'111212',ain=0.0,dur=4.7,pad=True,tag='부산에서 배로 1시간 반',
      subs=[[0.0,1.3,'도착했습니다.'],[1.5,4.6,'여기는 일본 히타카츠항입니다.']]),
 dict(v=D+'114601',vin=8.0,a=D+'115828',ain=16.4,dur=14.25,tag='수령은 간단합니다',
      subs=[[0.0,3.3,'야마토 운수 직원분께 인사하고'],[3.4,7.9,'운송장 번호를 보여 주면 다른 말 없이 바로'],[8.1,14.2,'마운자로가 든 쿨택배를 건네줍니다.']]),
 dict(v=D+'172225',vin=15.5,a=D+'172225',ain=15.5,dur=6.35,tag='귀국 · 세관 자진 신고',
      subs=[[0.0,6.3,'앞으로 3개월간 마운자로 추가 반입은\\N불가능하다는 안내를 받고']]),
 dict(v=D+'172225',vin=23.45,a=D+'172225',ain=23.45,dur=1.75,tag='귀국 · 세관 자진 신고',
      subs=[[0.0,1.7,'세관에서 나왔습니다.']]),
 dict(card=True,a=D+'194849',ain=16.8,dur=7.8,
      subs=[[0.0,7.6,'당일치기보다는 여유 있게\\N1박 2일이 훨씬 효율적일 것 같습니다.']]),
]
def level(clip,ss,t):
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(t),'-i',f'{R}/{clip}.mp4','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    y=np.frombuffer(raw,np.int16).astype(float)/32768; w=y[:len(y)//320*320].reshape(-1,320); r=np.sqrt((w**2).mean(1))
    return 20*np.log10(r[r>np.percentile(r,60)].mean()+1e-9)
def tag_png(text):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # 위 고정 제목 (도현체, 노랑+흰, 두꺼운 테두리)
    for t,y,s,c in [('대마도 당일치기',150,128,YEL),('마운자로 직접 받아왔다',300,112,WHT)]:
        f=DH(s); tw=d.textlength(t,font=f); x=(W-tw)/2
        d.text((x+6,y+8),t,font=f,fill=(0,0,0,170),stroke_width=11,stroke_fill=(0,0,0,170)); d.text((x,y),t,font=f,fill=c,stroke_width=11,stroke_fill=BLK)
    if text:
        f=F(900,44); tw=d.textlength(text,font=f); x=(W-tw-48)/2
        d.rounded_rectangle((x,VY-96,x+tw+48,VY-24),18,fill=(225,30,60)); d.text((x+24,VY-92),text,font=f,fill=WHT)
    f=F(900,40); t='이라도시 | 재테크 일상'; tw=d.textlength(t,font=f)
    d.text(((W-tw)/2,H-150),t,font=f,fill=WHT,stroke_width=4,stroke_fill=BLK)
    return im
def card_png():
    bg=Image.open(f'{P}/thumb/c_harbor.jpg').convert('RGB')
    bg=bg.resize((int(bg.width*H/bg.height),H),Image.LANCZOS); bg=bg.crop(((bg.width-W)//2,0,(bg.width-W)//2+W,H))
    bg=ImageEnhance.Brightness(bg).enhance(0.55).filter(ImageFilter.GaussianBlur(3)).convert('RGBA')
    d=ImageDraw.Draw(bg)
    def c(t,y,f,col,st=10):
        tw=d.textlength(t,font=f); x=(W-tw)/2
        d.text((x+6,y+8),t,font=f,fill=(0,0,0,170),stroke_width=st,stroke_fill=(0,0,0,170)); d.text((x,y),t,font=f,fill=col,stroke_width=st,stroke_fill=BLK)
    c('당일치기 총비용',520,DH(110),YEL); c('54만원',660,DH(230),WHT,13)
    c('배편 6.9만 + 처방·배송 4만엔',930,F(900,48),(225,235,245),5)
    f=F(900,54); t='전체 과정은 유튜브 3편에서'; tw=d.textlength(t,font=f); x=(W-tw-60)/2
    d.rounded_rectangle((x,1060,x+tw+60,1160),24,fill=YEL); d.text((x+30,1072),t,font=f,fill=(15,15,15))
    f=F(900,40); t='이라도시 | 재테크 일상'; tw=d.textlength(t,font=f); d.text(((W-tw)/2,H-150),t,font=f,fill=WHT,stroke_width=4,stroke_fill=BLK)
    return bg
outs=[]
for i,s in enumerate(SEGS):
    out=f'{T}/seg/{i}.mov'; g=-25.5-level(s['a'],s['ain'],s['dur']); g=max(-8,min(8,g))
    ov=f'{T}/seg/ov{i}.png'
    if s.get('card'):
        card_png().convert('RGB').save(ov)
        vin=['-loop','1','-framerate',str(FPS),'-t',str(s['dur']),'-i',ov]
        vf="[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v]"
        ovin=[]
    else:
        tag_png(s['tag']).save(ov)
        vin=(['-noautorotate'] if s.get('raw') else [])+['-ss',str(s['vin']),'-t',str(s['dur']),'-i',f"{R}/{s['v']}.mp4"]
        b=''
        if s.get('blur'): b=",split[o][c];[c]crop=iw*0.36:ih*0.85:iw*0.43:ih*0.15,boxblur=40:5[cb];[o][cb]overlay=W*0.43:H*0.15"
        pv="tpad=stop_mode=clone:stop_duration=1," if s.get('pad') else ""
        vf=(f"[0:v]{pv}fps=30,setsar=1,scale=1920:1080{b}[src];[src]split[a1][a2];"
            f"[a1]scale=-2:1920,crop=1080:1920,boxblur=30:4,eq=brightness=-0.22[bg];[a2]scale=1080:-2[fg];"
            f"[bg][fg]overlay=0:{VY}[m];[m][2:v]overlay=0:0,format=yuv420p[v]")
        ovin=['-loop','1','-i',ov]
    ain=['-ss',str(s['ain']),'-t',str(s['dur']),'-i',f"{R}/{s['a']}.mp4"]
    af=f"[1:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=90,volume={g:.1f}dB,afade=t=in:d=0.04,afade=t=out:st={s['dur']-0.04}:d=0.04[a]"
    subprocess.run(['ffmpeg','-v','error','-y',*vin,*ain,*ovin,'-filter_complex',vf+';'+af,'-map','[v]','-map','[a]','-t',str(s['dur']),
                    '-c:v','libx264','-preset','veryfast','-crf','18','-c:a','pcm_s16le',out],check=True)
    outs.append(out)
open(f'{T}/segs.txt','w').write(''.join(f"file '{o}'\n" for o in outs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{T}/segs.txt','-c','copy',f'{T}/joined.mov'],check=True)
# 자막 (영상 아래, 흰 상자 + 진한 글씨)
def ts(x): return f'{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}'
ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','','[V4+ Styles]',
 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
 'Style: Sub,Noto Sans KR,58,&H00271811,&H00271811,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,18,0,8,70,70,1330,1','','[Events]',
 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
t=0
for s in SEGS:
    for a,b,x in s['subs']:
        if s.get('card'): continue
        ass.append(f'Dialogue: 0,{ts(t+a)},{ts(t+b-0.02)},Sub,,0,0,0,,{x}')
    if s.get('card'):
        for a,b,x in s['subs']: ass.append(f'Dialogue: 0,{ts(t+a)},{ts(t+b)},Sub,,0,0,0,{"" }, {x}'.replace(',0,0,0, ,',',0,0,0,,').replace('Sub,,0,0,0,','Sub,,0,0,1500,'))
    t+=s['dur']
open(f'{T}/teaser.ass','w',encoding='utf-8').write('\n'.join(ass)+'\n')
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{T}/joined.mov','-filter_complex',
  f"[0:v]subtitles={T}/teaser.ass:fontsdir={TTF},setpts=PTS/{SPEED},fps=30[v]",'-map','[v]','-map','0:a',
  '-af',f'atempo={SPEED},adeclick,alimiter=limit=0.9:level=disabled','-c:v','libx264','-preset','medium','-crf','20',
  '-c:a','aac','-b:a','160k','-movflags','+faststart',f'{P}/upload/3편_세로예고.mp4'],check=True)
print('total',round(t/SPEED,1),'s')
