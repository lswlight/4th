#!/usr/bin/env python3
"""hookscore.py - 촬영 전에 유튜브 훅(첫 15초) 점수를 매긴다. 한국어·영어 자동 판별.

    python3 hookscore.py hooks.txt              # 한 줄에 훅 하나, 점수순 정렬
    python3 hookscore.py --hook "훅 한 줄"       # 하나만
    python3 hookscore.py --json hooks.txt       # 기계용 출력

다섯 항목(구체성, 시청자 호명, 걸린 것, 궁금증, 길이)을 0~100으로 매기고,
종합 점수 = 평균 60% + 가장 약한 항목 40%. 하나만 죽어도 그 지점에서 새기 때문에 평균만 보지 않는다.

원본: Jake Schincariol, youtube-agent-skill (MIT). 영어 규칙은 원본 그대로이며 실제 훅 74개로 보정됐다.
한국어 규칙은 같은 구조로 새로 만든 것이고 실제 데이터로 보정하지 않았다.
낮은 점수는 다시 볼 이유일 뿐이고, 높은 점수가 조회수를 약속하지 않는다.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(HERE, "hooks.json"), encoding="utf-8"))["hooks"]
HANGUL = re.compile(r"[가-힣]")

def is_ko(t):
    letters = re.findall(r"[A-Za-z가-힣]", t)
    return bool(letters) and len(HANGUL.findall(t)) / len(letters) >= 0.3

# ---------------------------------------------------------------- 영어 (원본 규칙)
EN_FILLER = {"basically","actually","literally","just","really","very","so","kind","sort","like",
             "guys","hey","welcome","today","video","subscribe","channel"}
EN_VAGUE = {"amazing","incredible","insane","crazy","huge","massive","game","changer","secret",
            "powerful","ultimate","best","revolutionary","mind","blowing","unbelievable"}
EN_CONCRETE = re.compile(r"\b(\d[\d,.]*\s?(%|k|m|x|s|m|h)?|\$\d|\d+\s?(second|minute|hour|day|week|month|year)s?)\b", re.I)
EN_YOU = re.compile(r"\b(you|your|you're|youre|yourself)\b", re.I)
EN_STAKE = re.compile(r"\b(lose|lost|wasting|waste|quit|fail|broke|cost|risk|before|stop|never|die|dying|dead)\b", re.I)
EN_CURIOUS = re.compile(r"\b(why|how|what|which|until|before|but|nobody|almost|except|reason|actually)\b", re.I)
EN_CLOSED = re.compile(r"\b(because|so that|which means)\b", re.I)

def en_words(t): return re.findall(r"[a-z0-9'%$.]+", t.lower())

def en_props(t):
    w = en_words(t)
    spec = 0
    if w:
        spec = 34 + len(EN_CONCRETE.findall(t)) * 22 - sum(x in EN_VAGUE for x in w) * 16 - sum(x in EN_FILLER for x in w) * 5
        spec += min(18, 6 * sum(1 for x in t.split()[1:] if x[:1].isupper()))
    addr = 26 + len(EN_YOU.findall(t)) * 20 + (30 if EN_YOU.search(" ".join(t.split()[:6])) else 0)
    stake = 22 + len(EN_STAKE.findall(t)) * 26 + (14 if EN_CONCRETE.search(t) else 0)
    cur = 24 + len(EN_CURIOUS.findall(t)) * 17 + (18 if t.strip().endswith("?") else 0) - (18 if EN_CLOSED.search(t) else 0)
    n = len(w)
    brev = 0 if n == 0 else 100 if 9 <= n <= 24 else max(30, 100 - (9 - n) * 11) if n < 9 else max(10, 100 - (n - 24) * 7)
    return spec, addr, stake, cur, brev

# ---------------------------------------------------------------- 한국어
# 숫자 + 단위, 또는 "세 가지" 같은 개수 표현
KO_CONCRETE = re.compile(r"\d[\d,.]*\s?(%|퍼센트|원|만|억|조|배|개|명|초|분|시간|일|주|개월|달|년|달러|포인트|bp)?"
                         r"|\$\d|(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s?(가지|개|명|번|배)")
KO_VAGUE = re.compile(r"(대박|미친|역대급|엄청난|엄청|놀라운|충격|레전드|최고의|완벽한|완벽|무조건|꿀팁|끝판왕|필수|인생|어마어마)")
KO_FILLER = re.compile(r"(안녕하세요|구독|좋아요|알림\s?설정|오늘은|오늘\s?영상|이번\s?영상|영상에서|채널|그냥|약간|일단|진짜|정말|사실상)")
# 시청자를 부르는 말: 2인칭, 대상 지정, 시청자에게 하는 존댓말 의문·권유
KO_YOU = re.compile(r"(여러분|당신|님들|분들|이시라면|이라면|하신다면|하시는\s?분|계시죠|계신가요|계시나요|하시죠|시죠|세요|셨나요|으셨|하셨|본인|내\s?돈|내\s?계좌)")
KO_STAKE = re.compile(r"(손해|손실|잃|날리|날린|날려|놓치|놓친|망하|망한|실패|후회|위험|비용|그만두|포기|버리|낭비|물리|물린|폭락|떨어|큰일|함정|조심|주의|경고|전에|절대|하지\s?마|안\s?하면|늦기|끝납니다)")
KO_CURIOUS = re.compile(r"(왜|어떻게|무엇|뭘|뭐가|어떤|어느|이유|원인|아무도|모르는|몰랐던|사실은|그런데|하지만|근데|딱\s?하나|단\s?하나|숨은|숨겨진|진짜\s?이유|까지|과연)")
KO_QUESTION_END = re.compile(r"(\?|까요|나요|ㄹ까|을까|는지|던가)\s*$")
KO_CLOSED = re.compile(r"(때문입니다|때문이에요|때문에|그래서|즉,|즉\s|결론은|정답은)")
LATIN_NAME = re.compile(r"\b([A-Z][A-Za-z0-9&]+|[A-Z]{2,}[0-9]*)\b")  # NVDA, ETF, S&P500, Tesla

def ko_props(t):
    s = t.strip()
    eojeol = s.split()
    syl = len(HANGUL.findall(s)) + len(re.findall(r"[A-Za-z0-9]+", s))
    spec = 34 + len(KO_CONCRETE.findall(s)) * 22 - len(KO_VAGUE.findall(s)) * 16 - len(KO_FILLER.findall(s)) * 5
    spec += min(18, 6 * len(LATIN_NAME.findall(s)))
    head = " ".join(eojeol[:4])
    addr = 26 + len(KO_YOU.findall(s)) * 20 + (30 if KO_YOU.search(head) else 0)
    stake = 22 + len(KO_STAKE.findall(s)) * 26 + (14 if KO_CONCRETE.search(s) else 0)
    cur = 24 + len(KO_CURIOUS.findall(s)) * 17 + (18 if KO_QUESTION_END.search(s) else 0) - (18 if KO_CLOSED.search(s) else 0)
    # 말로 하는 훅은 10초 안에 끝나야 한다. 한국어 유튜브 발화 약 5~6음절/초 → 20~60음절 구간이 만점
    if syl == 0: brev = 0
    elif 20 <= syl <= 60: brev = 100
    elif syl < 20: brev = max(30, 100 - (20 - syl) * 5)
    else: brev = max(10, 100 - (syl - 60) * 3)
    return spec, addr, stake, cur, brev

NAMES = ["SPECIFICITY", "ADDRESS", "STAKES", "CURIOSITY", "BREVITY"]
LABEL = {"SPECIFICITY": "구체성", "ADDRESS": "시청자호명", "STAKES": "걸린것", "CURIOSITY": "궁금증", "BREVITY": "길이"}
FIX_KO = {
 "SPECIFICITY": "형용사 하나를 숫자·이름·날짜로 바꾼다 (대박·역대급·꿀팁은 감점)",
 "ADDRESS": "앞 네 어절 안에서 시청자를 부른다 ('~하시는 분', '여러분', '~이시라면')",
 "STAKES": "지금 방식대로 계속하면 무엇을 잃는지 말한다",
 "CURIOSITY": "스스로 답해 버리는 절반('~때문입니다', '그래서')을 잘라 낸다",
 "BREVITY": "20~60음절. 소리 내어 읽고 숨이 찰 때 끊는다",
}
FIX_EN = {
 "SPECIFICITY": "swap one adjective for a number, a name or a date",
 "ADDRESS": "say 'you' in the first six words",
 "STAKES": "name what it costs them to keep doing it the current way",
 "CURIOSITY": "cut the half of the sentence that answers itself",
 "BREVITY": "9 to 24 words. Read it out loud and stop where you run out of breath",
}

def classify(t, ko):
    best, hits = None, 0
    for f in FORMULAS:
        pats = f.get("match_ko", []) if ko else f["match"]
        n = sum(1 for p in pats if re.search(p, t, 0 if ko else re.I))
        if n > hits: best, hits = f, n
    if not best: return ("미분류" if ko else "Unclassified"), 0
    return (f'{best["name_ko"]} ({best["name"]})' if ko else best["name"]), hits

def clamp(v): return max(0, min(100, int(round(v))))

def score(t):
    ko = is_ko(t)
    vals = [clamp(v) for v in (ko_props(t) if ko else en_props(t))]
    parts = dict(zip(NAMES, vals))
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    name, hits = classify(t, ko)
    return parts, verdict, name, hits, ko

def band(v): return "STRONG(강함)" if v >= 72 else "WORKABLE(쓸 만함)" if v >= 55 else "WEAK(약함)"

def report(r):
    t, parts, ko = r["hook"], r["properties"], r["lang"] == "ko"
    print(f"\n  {t}")
    print(f"  {'-' * min(72, max(20, len(t)))}")
    for k, v in parts.items():
        print(f"    {LABEL[k]:<8} {v:3d}  {'#' * (v // 5)}")
    print(f"    {'종합':<8} {r['verdict']:3d}  {band(r['verdict'])}")
    tail = f"  (패턴 {r['matched']}개 일치)" if r["matched"] else "  (맞는 공식 없음 - 훅이 아니라 요약일 때가 많다)"
    print(f"    공식      {r['formula']}{tail}")
    low = min(parts, key=parts.get)
    print(f"    약점      {LABEL[low]} - {(FIX_KO if ko else FIX_EN)[low]}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        lines = [l for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1 if not a else 0)
    out = []
    for t in lines:
        parts, verdict, name, hits, ko = score(t)
        out.append({"hook": t.strip(), "lang": "ko" if ko else "en", "properties": parts, "verdict": verdict,
                    "band": band(verdict), "formula": name, "matched": hits})
    out.sort(key=lambda r: -r["verdict"])
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "matched"} for r in out], ensure_ascii=False, indent=1)); return
    for r in out: report(r)
    if len(out) > 1:
        print(f"\n  1위: {out[0]['hook']}  ({out[0]['verdict']}, {out[0]['band']})\n")

if __name__ == "__main__":
    main()
