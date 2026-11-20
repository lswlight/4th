#!/usr/bin/env python3
"""deadair.py - 타임코드 자막으로 편집 목록(EDL)을 만든다. 한국어·영어 군말 모두 인식.

    python3 deadair.py transcript.srt              # .srt, .vtt, whisper .json
    python3 deadair.py transcript.srt --floor 0.35 --json

찾는 것 세 가지:
  DEAD    말 사이 공백이 기준(기본 0.45초)보다 긴 곳. 양쪽 숨은 남기도록 가운데만 자른다.
  FILLER  군말만 있는 자막 ("음", "어", "그러니까", "um", "so yeah")
  REPEAT  같은 문장을 다시 시작한 곳 (NG 후 재촬영). 앞 테이크를 자를 대상으로 표시한다.

파일은 건드리지 않는다. 자를 목록, 줄어드는 시간, 최종 길이만 출력하고 편집은 편집 프로그램에서 한다.
원본: Jake Schincariol, youtube-agent-skill (MIT). 한국어 군말·재시작 판정은 새로 추가했다.
"""
import json, os, re, sys

FILLER_EN = (r"um+|uh+|er+|ah+|so|okay|ok|right|yeah|like|anyway|basically|actually|you know|i mean|"
             r"let me see|hold on")
FILLER_KO = (r"음+|으음+|어+|아+|에+|그+|저+|뭐+|막|이제|자|네|예|좀|약간|그러니까|그니까|그래서|근데|그런데|"
             r"아무튼|어쨌든|있잖아요|있잖아|그거|이거|저기|뭐랄까|뭐냐면|그러면|그럼|일단")
FILLER_ONLY = re.compile(r"^[\s,.…~!?-]*((" + FILLER_EN + "|" + FILLER_KO + r")[\s,.…~!?-]*)+$", re.I)

def parse_ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2]) if len(p) == 3 else int(p[0]) * 60 + float(p[1])

def load(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".json"):
        d = json.loads(raw)
        segs = d.get("segments", []) if isinstance(d, dict) else d
        return [(float(s["start"]), float(s["end"]), (s.get("text") or "").strip()) for s in segs]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [parse_ts(m.group(1)), parse_ts(m.group(2)), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(re.sub(r"<[^>]+>", "", line.strip()))
    return [(a, b, " ".join(t)) for a, b, t in cues if t]

def norm(t): return re.sub(r"[^a-z0-9가-힣 ]", "", t.lower()).split()

def is_restart(prev, cur):
    """같은 문장 다시 시작: 앞 4어절(영어 5단어)이 같거나, 공백 뺀 앞 8글자가 같다."""
    a, b = norm(prev), norm(cur)
    k = 4 if re.search(r"[가-힣]", prev + cur) else 5
    if len(a) >= 3 and len(b) >= 3 and a[:k] == b[:k]: return True
    ca, cb = "".join(a), "".join(b)
    return len(ca) >= 8 and len(cb) >= 8 and ca[:8] == cb[:8]

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    floor = float(a[a.index("--floor") + 1]) if "--floor" in a else 0.45
    a = [x for x in a if not x.startswith("--") and not re.match(r"^[\d.]+$", x)]
    if not a or not os.path.exists(a[0]): print(__doc__); sys.exit(1)
    cues = load(a[0])
    if not cues: print("자막을 못 읽었습니다 - srt, vtt, whisper json 인가요?"); sys.exit(1)
    dur = cues[-1][1]
    cuts = []
    for i, (s, e, t) in enumerate(cues):
        if FILLER_ONLY.match(t):
            cuts.append({"kind": "FILLER", "start": s, "end": e, "why": t.strip()[:48]})
        if i:
            gap = s - cues[i - 1][1]
            if gap > floor:
                keep = floor / 2
                cuts.append({"kind": "DEAD", "start": round(cues[i - 1][1] + keep, 3),
                             "end": round(s - keep, 3), "why": f"{gap:.2f}초 공백"})
        # 재시작은 '직전 자막'이 아니라 '직전에 실제로 말한 자막'과 비교한다. 대부분 NG 사이에 "음"이 끼어 있다.
        if t.strip() and not FILLER_ONLY.match(t):
            j = i - 1
            while j >= 0 and (FILLER_ONLY.match(cues[j][2]) or not cues[j][2].strip()): j -= 1
            if j >= 0 and is_restart(cues[j][2], t):
                cuts.append({"kind": "REPEAT", "start": cues[j][0], "end": cues[j][1],
                             "why": f'다시 시작: "{" ".join(norm(cues[j][2])[:4])}"'})
    cuts = [c for c in cuts if c["end"] > c["start"]]
    cuts.sort(key=lambda c: c["start"])
    removed = sum(c["end"] - c["start"] for c in cuts)
    if as_json:
        print(json.dumps({"source": a[0], "duration": dur, "cuts": cuts,
                          "removed": round(removed, 3), "out": round(dur - removed, 3)}, ensure_ascii=False, indent=1)); return
    print(f"\n  {a[0]}   원본 {dur:.2f}초, 자막 {len(cues)}개, 공백 기준 {floor}초\n")
    for c in cuts:
        print(f"    {c['kind']:<7} {c['start']:8.2f} -> {c['end']:8.2f}   {c['end']-c['start']:5.2f}초   {c['why']}")
    print(f"\n  자를 곳 {len(cuts)}개, {removed:.2f}초 제거 → {dur - removed:.2f}초 "
          f"({removed / dur * 100:.1f}% 짧아짐)")
    print("  주의: 말 기준 계산이다. 말없이 보여 주는 화면(차트 시연 등)이 길면 실제 결과와 다르다.\n")

if __name__ == "__main__":
    main()
