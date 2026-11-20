#!/usr/bin/env python3
"""retention.py - 시청 지속률 곡선에서 시청자가 나간 지점을 찾는다.

    python3 retention.py retention.csv --duration 600
    python3 retention.py retention.csv --duration 600 --transcript transcript.srt   # 이탈 순간에 한 말
    python3 retention.py retention.json --duration 600                               # vidIQ 결과 저장본
    python3 retention.py retention.csv --json

입력 (둘 중 하나):
  - CSV: 두 숫자 열, 위치(% 또는 초)와 남은 시청자 %. YouTube Studio → 분석 → 참여도 →
    시청 지속률 차트 → 다운로드.
  - JSON: vidIQ `vidiq_channel_analytics` (report=audience_retention, filters=video==ID) 결과의 행.
    elapsedVideoTimeRatio(0~1)와 audienceWatchRatio(0~1 또는 그 이상)를 자동으로 % 로 바꾼다.

세 가지를 따로 본다. 원인도 해결책도 다르기 때문이다.
  HOOK LEAK  첫 30초에 잃은 비율. 25% 미만이 건강. 고칠 곳은 늘 대본 첫 15초다.
  CLIFFS     가파른 한 번의 하락. 예고 없는 주제 전환, 광고, 긴 준비 설명 같은 '순간'.
  SLIDE      중간 구간에서 꾸준히 새는 속도. 내용이 아니라 속도 문제 - 다시 쓰지 말고 자른다.

원본: Jake Schincariol, youtube-agent-skill (MIT). 한국어 출력과 vidIQ JSON 입력을 추가했다.
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.reader(fh):
            nums = []
            for c in r:
                c = c.strip().replace("%", "").replace(",", "")
                try: nums.append(float(c))
                except ValueError: pass
            if len(nums) >= 2: rows.append((nums[0], nums[1]))
    return rows

def load_json(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("rows") or d.get("data") or d.get("result") or []
    rows = []
    for r in d:
        if isinstance(r, dict):
            x = r.get("elapsedVideoTimeRatio", r.get("x"))
            y = r.get("audienceWatchRatio", r.get("y"))
        else:
            x, y = r[0], r[1]
        if x is None or y is None: continue
        rows.append((float(x), float(y)))
    if rows and max(x for x, _ in rows) <= 1.0:          # 0~1 비율 → %
        rows = [(x * 100, y * 100 if max(v for _, v in rows) <= 1.5 else y) for x, y in rows]
    return rows

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
    dur = float(a[a.index("--duration") + 1]) if "--duration" in a else None
    skip = {tr, str(dur) if dur else None, a[a.index("--duration") + 1] if "--duration" in a else None}
    files = [x for x in a if not x.startswith("--") and x not in skip]
    if not files or not os.path.exists(files[0]): print(__doc__); sys.exit(1)
    rows = load_json(files[0]) if files[0].endswith(".json") else load_csv(files[0])
    rows.sort()
    if len(rows) < 8: print("데이터 점을 8개 이상 못 읽었습니다"); sys.exit(1)
    xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
    pct_axis = max(xs) <= 100.5
    def at(x): return (x / 100.0 * dur) if (pct_axis and dur) else x
    start = ys[0] or 100.0
    cutoff = 30.0 if not pct_axis else (30.0 / dur * 100 if dur else 10.0)
    hook_end = min((y for x, y in rows if x <= cutoff), default=start)
    hook_leak = start - hook_end
    drops = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        drops.append((d / span, xs[i - 1], xs[i], d))
    mid = [r for r in drops if r[1] > cutoff]
    slide = sum(r[0] for r in mid) / len(mid) if mid else 0
    drops.sort(reverse=True)
    cliffs = [{"from": round(a1, 2), "to": round(b1, 2), "lost": round(d, 2),
               "at_seconds": round(at(a1), 1) if (not pct_axis or dur) else None}
              for _, a1, b1, d in drops[:5] if d > 0.8]
    said = {}
    if tr and os.path.exists(tr):
        from deadair import load as load_cues
        cues = load_cues(tr)
        for c in cliffs:
            if c["at_seconds"] is None: continue
            t = c["at_seconds"]
            near = [q[2] for q in cues if q[0] <= t + 4 and q[1] >= t - 4]
            said[str(c["from"])] = " ".join(near)[:140]
    out = {"points": len(rows), "start": start, "hook_leak": round(hook_leak, 2),
           "end": ys[-1], "cliffs": cliffs, "slide_per_unit": round(slide, 3), "said": said}
    if as_json: print(json.dumps(out, ensure_ascii=False, indent=1)); return
    print(f"\n  {files[0]}   점 {len(rows)}개   {ys[0]:.1f}% → {ys[-1]:.1f}%\n")
    verdict = "건강" if hook_leak < 25 else "새는 중" if hook_leak < 40 else "심각"
    print(f"  HOOK LEAK   도입부에서 {hook_leak:.1f}% 이탈   [{verdict}]")
    print( "              25% 미만이 건강. 다른 것보다 첫 문장부터 고친다.\n")
    print( "  CLIFFS      시청자가 실제로 나간 순간")
    for c in cliffs:
        where = f"{c['at_seconds']:.0f}초" if c["at_seconds"] is not None else f"{c['from']}%"
        print(f"    -{c['lost']:5.1f}%  {where:>8}" + (f'   "{said.get(str(c["from"]), "")}"' if said else ""))
    if not cliffs: print("    0.8% 넘는 급락 없음 - 순간이 아니라 꾸준한 누수(slide) 문제")
    if pct_axis and not dur: print("    (--duration 을 주면 초 단위로 바꿔 보여 준다)")
    print(f"\n  SLIDE       중간 구간 단위당 {slide:.3f}% 감소")
    print( "              완만하게 새는 건 속도 문제. 다시 쓰지 말고 중간을 자른다.\n")

if __name__ == "__main__":
    main()
