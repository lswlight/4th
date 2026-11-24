"""3편 모션그래픽: 증시 리뷰 쇼츠와 같은 방식(장면별 HTML + setT(t)로 프레임 렌더)을 16:9로.
사진 전체 배경 + 그라데이션, 노란 라벨, 흰 큰 키워드, 카운트업 숫자, 줄 슬라이드, 칩, 진행 막대.
사용: python3 render_anim.py [장면이름 ...]  → anim/<장면>.mp4 (30fps, 1920x1080)
"""
import json, os, sys, subprocess, shutil
A = os.path.dirname(os.path.abspath(__file__))
TTF = '/tmp/claude-0/-home-user-4th/1b6b0142-36e0-5974-9570-7e66779ccf2f/scratchpad/ttf'
FPS = 30
CH = '이라도시 | 재테크 일상'

SCENES = {
 'title': dict(dur=8.1, bg='bg_sea.jpg', label='당일치기 브이로그', kw=['대마도에서', '마운자로 직접 받기'],
               chips=['당일치기 · 2026.11.23']),
 'recap': dict(dur=10.5, bg='bg_port.jpg', label='지난 2편', kw=['반송 직전,', '보관기한 연장'],
               rows=[['보관기한', '22일 → 24일'], ['도착 기준', '3일 → 5일']], chips=['오늘, 직접 받으러 갑니다']),
 'route': dict(dur=15.0, bg='bg_port.jpg', label='하루 정리', kw=['하루 만에 다녀왔습니다'], step=1.6, g2=True,
               rows=[['05:53', '대구 출발'], ['07:54', '부산역 도착'], ['09:40', '승선 마감'], ['11:12', '히타카츠 도착'],
                     ['11:52', '야마토 운수 수령'], ['17:22', '부산 입국 · 세관'], ['19:48', '집 도착']], hl=[4, 5], tl=True),
 'receive': dict(dur=18.6, bg='bg_parcel.jpg', label='수령 방법', kw=['3단계면 끝'], step=0.9,
                 rows=[['1', '운송장 번호 보여주기'], ['2', '여권 번호 확인'], ['3', '영문으로 서명']], num=True,
                 chips=['냉장 택배(쿨택배)로 바로 수령']),
 'transit': dict(dur=5.0, bg='bg_sea.jpg', label='이동 중', kw=['부산항 → 히타카츠'], step=0.5,
                 rows=[['배로', '약 1시간 30분'], ['도착 예정', '11:12 히타카츠항']]),
 'customs': dict(dur=10.6, bg='bg_terminal.jpg', label='귀국 세관', kw=['자진 신고 후', '3개월 추가 반입 불가'],
                 rows=[['신고', '마운자로 반입 자진 신고'], ['한도', '자가 사용 3개월분 · 최대 12펜']],
                 ),
 'cost': dict(dur=13.8, bg='bg_harbor.jpg', label='당일치기 총비용', g2=True, big=542000, bigpre='약 ', bigsuf='원', step=0.9,
              rows=[['배편 왕복', '69,500원'], ['기차 왕복', '27,300원'], ['보험 · eSIM · 커피', '12,090원'],
                    ['현지 식사 · 쇼핑 · 출국세', '10,340엔'], ['처방 · 배송 (12펜)', '40,310엔']],
              note='108,890원 + 50,650엔 · 원화 환산 약 54만 2천 원'),
 'end': dict(dur=4.5, bg='bg_harbor.jpg', label='3편 끝', kw=['12펜,', '무사히 반입 완료'],
             chips=['개인 경험 기록 · 의학적 조언 아님', '구독 · 좋아요 부탁드립니다']),
}

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:K;font-weight:500;src:url(file://__TTF__/NotoSansKR-500.ttf)}
@font-face{font-family:K;font-weight:700;src:url(file://__TTF__/NotoSansKR-700.ttf)}
@font-face{font-family:K;font-weight:900;src:url(file://__TTF__/NotoSansKR-900.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1920px;height:1080px;overflow:hidden;position:relative;font-family:"Inter",K,sans-serif;word-break:keep-all;background:#05080f;color:#fff}
#bg{position:absolute;inset:0;background-size:cover;background-position:center;transform-origin:center}
#gr{position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,10,20,.9) 0%,rgba(5,10,20,.82) 42%,rgba(5,10,20,.35) 75%,rgba(5,10,20,.15) 100%),linear-gradient(0deg,rgba(5,10,20,.55),rgba(5,10,20,0) 40%)}
#bar{position:absolute;left:0;top:0;height:8px;background:#14A06A;width:0}
#pill{position:absolute;top:56px;left:96px;font-size:36px;font-weight:900;background:rgba(20,160,106,.95);padding:10px 30px;border-radius:999px}
#ch{position:absolute;right:72px;bottom:52px;font-size:40px;font-weight:900;text-shadow:0 3px 10px rgba(0,0,0,.6);white-space:nowrap}
#body{position:absolute;left:120px;top:170px;right:120px}
#label{display:inline-block;background:#ffd84d;color:#0b1220;font-size:44px;font-weight:900;padding:8px 26px;border-radius:12px}
.kw{font-size:108px;font-weight:900;line-height:1.12;letter-spacing:-3px;text-shadow:0 6px 24px rgba(0,0,0,.55)}
#kw{margin-top:22px}
#big{font-size:170px;font-weight:900;color:#ffd84d;letter-spacing:-4px;margin-top:18px;line-height:1;text-shadow:0 6px 24px rgba(0,0,0,.5);font-variant-numeric:tabular-nums}
#rows{margin-top:36px;width:1500px}
.row{display:flex;align-items:center;gap:36px;padding:16px 0;border-bottom:2px solid rgba(255,255,255,.22)}
.row .k{font-size:50px;font-weight:700;color:#d6deea;min-width:380px}
.row .v{font-size:66px;font-weight:900}
.row.hl .k,.row.hl .v{color:#ffd84d}
.row .n{width:96px;height:96px;border-radius:50%;background:#ffd84d;color:#0b1220;font-size:60px;font-weight:900;display:flex;align-items:center;justify-content:center;flex:none}
#rows.g2{display:grid;grid-template-columns:1fr 1fr;column-gap:70px;width:1680px}#rows.g2 .row .k{font-size:42px;min-width:0;flex:1}#rows.g2 .row .v{font-size:56px}
.tl .row{padding:10px 0}.tl .row .k{font-size:46px;min-width:200px;color:#9fb0c6}.tl .row .v{font-size:58px}
#chips{margin-top:40px;display:flex;gap:22px;flex-wrap:wrap}
.chip{font-size:46px;font-weight:900;border:4px solid #fff;padding:12px 32px;border-radius:999px;background:rgba(5,10,20,.55)}
.chip.y{border-color:#ffd84d;color:#ffd84d}
#note{margin-top:26px;font-size:40px;font-weight:700;color:#d6deea}
</style></head><body>
<div id="bg"></div><div id="gr"></div><div id="bar"></div>
<div id="pill">3편 · 대마도 마운자로</div>
<div id="body"><div id="label"></div><div id="kw"></div><div id="big"></div><div id="rows"></div><div id="chips"></div><div id="note"></div></div>
<div id="ch">__CH__</div>
<script>
const S=__S__;
const $=id=>document.getElementById(id);
const eo=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
const back=x=>{x=Math.min(Math.max(x,0),1);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
$('bg').style.backgroundImage=`url(${S.bgurl})`;
$('label').textContent=S.label||'';
if(!S.label)$('label').style.display='none';
$('kw').innerHTML=(S.kw||[]).map(l=>`<div class="kw">${l}</div>`).join('');
$('rows').innerHTML=(S.rows||[]).map((r,i)=>`<div class="row${(S.hl||[]).includes(i)?' hl':''}">${S.num?`<div class="n">${r[0]}</div>`:`<div class="k">${r[0]}</div>`}<div class="v">${r[1]}</div></div>`).join('');
if(S.tl)$('rows').classList.add('tl');if(S.g2)$('rows').classList.add('g2');
$('chips').innerHTML=(S.chips||[]).map((c,i)=>`<div class="chip${i==(S.chips.length-1)&&S.chips.length>1?' y':''}">${c}</div>`).join('');
$('note').textContent=S.note||'';
if(S.big===undefined)$('big').style.display='none';
window.setT=function(t){
  const u=t/S.dur;
  $('bg').style.transform=`scale(${1+0.06*u}) translateY(${-14*u}px)`;
  $('bar').style.width=(100*Math.min(u,1))+'%';
  const lb=eo((t-0.05)/0.3); $('label').style.opacity=lb; $('label').style.transform=`translateX(${-60*(1-lb)}px)`;
  document.querySelectorAll('.kw').forEach((e,i)=>{const p=(t-0.2-0.18*i)/0.45; e.style.opacity=eo(p*1.6); e.style.transform=`translateY(${60*(1-back(p))}px)`});
  if(S.big!==undefined){const p=eo((t-0.6)/1.0); $('big').textContent=(S.bigpre||'')+Math.round(S.big*p).toLocaleString('en-US')+(S.bigsuf||''); $('big').style.opacity=Math.min(1,(t-0.5)*5)}
  const st=S.step||0.35, r0=S.big!==undefined?1.4:0.9;
  document.querySelectorAll('.row').forEach((e,i)=>{const p=eo((t-r0-st*i)/0.4); e.style.opacity=p; e.style.transform=`translateX(${80*(1-p)}px)`});
  const nr=(S.rows||[]).length, c0=r0+st*nr+0.2;
  document.querySelectorAll('.chip').forEach((e,i)=>{const p=(t-c0-0.4*i)/0.5; const s=0.7+0.3*back(p); e.style.opacity=eo(p*2); e.style.transform=`scale(${s})`});
  const pn=eo((t-c0)/0.5); $('note').style.opacity=pn;
};
setT(0);
</script></body></html>"""

def render(name):
    s = dict(SCENES[name]); s['bgurl'] = 'file://' + A + '/' + s['bg']
    html = HTML.replace('__TTF__', TTF).replace('__CH__', CH).replace('__S__', json.dumps(s, ensure_ascii=False))
    hp = f'{A}/{name}.html'; open(hp, 'w', encoding='utf-8').write(html)
    fd = f'{A}/f_{name}'; shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
    n = round(s['dur'] * FPS)
    subprocess.run(['node', f'{A}/frames.js', hp, fd, str(n)], check=True, cwd=A)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{fd}/%05d.jpg', '-c:v', 'libx264', '-preset', 'veryfast',
                    '-crf', '18', '-pix_fmt', 'yuv420p', f'{A}/{name}.mp4'], check=True)
    shutil.copy(f'{fd}/{n - 1:05d}.jpg', f'{A}/last_{name}.jpg')
    shutil.rmtree(fd)
    print(name, n, 'frames')

if __name__ == '__main__':
    for nm in (sys.argv[1:] or list(SCENES)): render(nm)
