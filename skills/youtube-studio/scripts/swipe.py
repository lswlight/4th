#!/usr/bin/env python3
"""swipe.py - 영상을 '그 채널 평소 조회수(중앙값) 대비 몇 배'로 줄 세우고, 제목의 훅 공식을 붙인다.

vidIQ 크레딧이 없을 때 쓰는 무료 대안이다. vidIQ와 달리 '모르는 채널'은 찾지 못하고,
이미 아는 경쟁 채널들 안에서 평소보다 터진 영상을 고른다.

    python3 swipe.py --rss UCxxxxxxxxxxxxxxxxxxxxxx @handle https://www.youtube.com/@other --save collected.json
    python3 swipe.py collected.json --min 2.0
    python3 swipe.py collected.json --json

입력 JSON (직접 만들거나 붙여 넣은 목록도 같은 형식):
    [{"channel":"채널명","title":"…","views":412000,"url":"…","published":"2026-11-01"}, …]

--rss: 채널 RSS(키 필요 없음)에서 최근 영상 15개의 제목·조회수·날짜를 받는다. 쇼츠와 롱폼이 섞여 나온다.
       youtube.com 접속이 막힌 환경(claude.ai 코드 실행 기본 설정 등)에서는 NETWORK_BLOCKED 를 내고 끝난다.
       그때는 Settings → Capabilities 에서 www.youtube.com 을 허용하거나, 목록을 직접 붙여 받는다.

규칙
- 채널당 영상 4개 미만이면 중앙값이 의미 없으니 빼고 알려 준다.
- 올라온 지 72시간이 안 된 영상은 아직 조회수가 덜 쌓였으니 순위·중앙값에서 뺀다 (날짜가 있을 때).
- 공식은 hooks.json 패턴을 '제목'에 맞춘 판단이다. 영상이 왜 떴는지에 대한 주장이 아니다.

원본: Jake Schincariol, youtube-agent-skill (MIT). 한국어 공식 판별, RSS 수집, 72시간 제외를 추가했다.
"""
import datetime as dt, json, os, re, statistics, sys, urllib.error, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(HERE, "hooks.json"), encoding="utf-8"))["hooks"]
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}
UA = {"User-Agent": "Mozilla/5.0 (youtube-studio skill)"}

def classify(title):
    ko = bool(re.search(r"[가-힣]", title))
    best, hits = None, 0
    for f in FORMULAS:
        pats = f.get("match_ko", []) if ko else f["match"]
        n = sum(1 for p in pats if re.search(p, title, 0 if ko else re.I))
        if n > hits: best, hits = f, n
    if not best: return "미분류"
    return best["name_ko"] if ko else best["name"]

def _get(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 407): sys.exit(f"NETWORK_BLOCKED: {url} 접속이 막혔습니다 (HTTP {e.code}). 목록을 직접 받아 주세요.")
        if e.code == 404: return None
        raise
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"NETWORK_BLOCKED: {url} 에 연결하지 못했습니다 ({e}). 목록을 직접 받아 주세요.")

def channel_id(ref):
    ref = ref.strip()
    m = re.search(r"(UC[A-Za-z0-9_-]{22})", ref)
    if m: return m.group(1)
    handle = ref if ref.startswith("http") else "https://www.youtube.com/" + (ref if ref.startswith("@") else "@" + ref)
    html = _get(handle) or ""
    m = re.search(r'"(?:externalId|channelId)":"(UC[A-Za-z0-9_-]{22})"', html) or \
        re.search(r'/channel/(UC[A-Za-z0-9_-]{22})', html)
    if not m: sys.exit(f"채널 ID를 찾지 못했습니다: {ref}")
    return m.group(1)

def parse_feed(xml):
    root = ET.fromstring(xml)
    ch = root.findtext("a:title", default="?", namespaces=NS)
    out = []
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", default="", namespaces=NS)
        stats = e.find("media:group/media:community/media:statistics", NS)
        out.append({"channel": ch, "title": e.findtext("a:title", default="", namespaces=NS),
                    "views": int(stats.get("views", 0)) if stats is not None else 0,
                    "url": f"https://www.youtube.com/watch?v={vid}" if vid else "",
                    "published": (e.findtext("a:published", default="", namespaces=NS) or "")[:10]})
    return out

def fetch_rss(refs):
    rows = []
    for r in refs:
        cid = channel_id(r)
        xml = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
        if not xml: print(f"  RSS 없음: {r}", file=sys.stderr); continue
        rows += parse_feed(xml)
    return rows

def too_new(v, now):
    p = v.get("published")
    if not p: return False
    try: d = dt.date.fromisoformat(p[:10])
    except ValueError: return False
    return (now - d).days < 3

def rank(rows, lo):
    now = dt.date.today()
    fresh = [v for v in rows if too_new(v, now)]
    rows = [v for v in rows if not too_new(v, now)]
    by = {}
    for r in rows: by.setdefault(r.get("channel", "?"), []).append(r)
    out, thin = [], []
    for ch, vids in by.items():
        if len(vids) < 4: thin.append((ch, len(vids))); continue
        med = statistics.median(float(v.get("views", 0) or 0) for v in vids)
        for v in vids:
            m = (float(v.get("views", 0) or 0) / med) if med else 0
            out.append({"channel": ch, "title": v.get("title", ""), "views": int(v.get("views", 0) or 0),
                        "median": int(med), "multiple": round(m, 2),
                        "formula": classify(v.get("title", "")), "url": v.get("url", "")})
    out = sorted((r for r in out if r["multiple"] >= lo), key=lambda r: -r["multiple"])
    return out, thin, len(fresh), len(rows), len(by)

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    lo = float(a[a.index("--min") + 1]) if "--min" in a else 1.5
    save = a[a.index("--save") + 1] if "--save" in a else None
    if "--rss" in a:
        refs = [x for x in a[a.index("--rss") + 1:] if not x.startswith("--")]
        refs = [x for x in refs if x != save and not re.match(r"^[\d.]+$", x)]
        rows = fetch_rss(refs)
        if save:
            json.dump(rows, open(save, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"  {len(rows)}개 저장 → {save}", file=sys.stderr)
    else:
        files = [x for x in a if not x.startswith("--") and x != save and not re.match(r"^[\d.]+$", x)]
        if not files or not os.path.exists(files[0]): print(__doc__); sys.exit(1)
        rows = json.load(open(files[0], encoding="utf-8"))
        if isinstance(rows, dict): rows = rows.get("videos", [])
    out, thin, fresh, n, nch = rank(rows, lo)
    if as_json:
        print(json.dumps({"outliers": out, "skipped_thin_channels": thin, "skipped_fresh": fresh},
                         ensure_ascii=False, indent=1)); return
    print(f"\n  영상 {n}개 / 채널 {nch}개, 평소의 {lo}배 이상만\n")
    for r in out[:25]:
        print(f"    {r['multiple']:5.2f}배  {r['views']:>10,}  (평소 {r['median']:>9,})  {r['channel'][:16]:<16} {r['title'][:46]}")
        print(f"            공식: {r['formula']}")
    if not out: print("    기준을 넘은 영상 없음 - 채널당 영상을 더 모으거나 --min 을 낮춘다")
    if fresh: print(f"\n  올라온 지 72시간 안 된 영상 {fresh}개는 뺐다 (조회수가 아직 덜 쌓임)")
    if thin:
        print(f"\n  영상 4개 미만이라 뺀 채널 {len(thin)}개 (한두 개로 낸 중앙값은 중앙값이 아니다): "
              + ", ".join(f"{c}({k})" for c, k in thin[:6]))
    counts = {}
    for r in out: counts[r["formula"]] = counts.get(r["formula"], 0) + 1
    if counts:
        print("\n  터진 영상들의 제목 공식")
        for f, k in sorted(counts.items(), key=lambda x: -x[1]): print(f"    {k:2d}개  {f}")
    print()

if __name__ == "__main__":
    main()
