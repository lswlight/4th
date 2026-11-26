"""Unsplash 무료 사진 받기 + 한눈에 보는 미리보기 + 출처 목록.
사용: python3 fetch_photos.py 폴더 "검색어1" "검색어2" ... [--n 3]
- 키는 환경의 네트워크 비밀값(api.unsplash.com, 헤더 Authorization, 앞말 Client-ID)으로 자동으로 붙는다. 코드나 채팅에 키를 쓰지 않는다.
- 결과: 폴더/<검색어순번>_<i>.jpg, 폴더/sheet.jpg(미리보기), 폴더/credits.txt (설명란 '사진 출처'에 그대로 쓴다)"""
import sys, json, subprocess, urllib.parse, os
from PIL import Image, ImageDraw
args = [a for a in sys.argv[1:] if not a.startswith('--')]; n = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 3
out, qs = args[0], [a for a in args[1:] if not a.isdigit()]
os.makedirs(out, exist_ok=True); cred = []; files = []
for qi, q in enumerate(qs):
    r = subprocess.run(['curl', '-s', '-m', '20', f'https://api.unsplash.com/search/photos?per_page={n}&orientation=landscape&query=' + urllib.parse.quote(q)], capture_output=True, text=True).stdout
    for i, p in enumerate(json.loads(r).get('results', [])[:n]):
        f = f'{out}/q{qi:02d}_{i}.jpg'; subprocess.run(['curl', '-s', '-m', '30', '-o', f, p['urls']['regular']]); files.append(f)
        cred.append(f"q{qi:02d}_{i} ({q}): Photo by {p['user']['name']} on Unsplash — {p['links']['html']}")
open(f'{out}/credits.txt', 'w').write('\n'.join(cred) + '\n')
c = Image.new('RGB', (n * 320, max(1, len(qs)) * 200), 'white'); d = ImageDraw.Draw(c)
for f in files:
    qi, i = int(os.path.basename(f)[1:3]), int(os.path.basename(f)[4])
    im = Image.open(f); im.thumbnail((310, 175)); c.paste(im, (i * 320, qi * 200 + 20)); d.text((i * 320 + 4, qi * 200 + 4), os.path.basename(f), fill='red')
c.save(f'{out}/sheet.jpg', quality=80); print(len(files), 'photos →', out)
