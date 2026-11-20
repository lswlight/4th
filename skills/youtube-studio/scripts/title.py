#!/usr/bin/env python3
"""title.py - 올리기 전에 제목과 썸네일 문구를 한 쌍으로 점검한다. 한국어·영어 자동 판별.

    python3 title.py --title "제목" --thumb "썸네일 문구"
    python3 title.py titles.txt              # 한 줄에 제목 하나, 점수순
    python3 title.py titles.txt --thumb "문구" --json

단위는 제목이 아니라 '제목+썸네일'이다. 썸네일이 제목을 반복하면 클릭 화면 절반을 버린다.

길이: 유튜브는 글자 수가 아니라 화면 폭으로 자른다. 한글 한 글자는 영문 평균보다 넓어서
'환산 폭'(한글 1.7, 영문·숫자·공백 1)으로 잰다. 데스크톱 검색은 약 60폭(한글 약 35자),
모바일 홈 피드는 약 40폭(한글 약 23자)에서 잘린다. 하드 제한은 실제 글자 수 100자.

원본: Jake Schincariol, youtube-agent-skill (MIT). 한국어 규칙은 새로 추가한 것이다.
"""
import json, os, re, sys

DESKTOP, MOBILE, HARD = 60, 40, 100
HANGUL = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")

EN_VAGUE = {"amazing","incredible","insane","crazy","huge","massive","ultimate","best","powerful",
            "secret","revolutionary","mindblowing","epic","perfect","complete","everything"}
EN_STOP = {"the","a","an","of","for","to","in","on","and","or","is","are","with","your","you","my","i",
           "this","that","it","how","what","why"}
KO_VAGUE = re.compile(r"(대박|미친|역대급|엄청난|놀라운|레전드|최고의|완벽|무조건|꿀팁|끝판왕|필수|어마어마|충격적)")
KO_FRONT_FILLER = {"오늘","오늘은","이번","이번엔","요즘","그냥","진짜","정말","드디어","결국","아니","와","헐"}
KO_STOP = {"이","그","저","것","수","등","및","더","또","왜","어떻게","무엇","지금","이제","그리고","하는","있는","되는","하면","합니다"}
# 명사 끝에 붙는 조사·어미를 떼어 '같은 단어' 비교가 되게 한다 (비트코인이 = 비트코인)
JOSA = re.compile(r"(으로써|으로서|에서는|에게서|이라는|이라고|까지는|부터는|입니다|이에요|에서|에게|으로|이랑|하고|까지|부터|처럼|보다|이나|라는|라고|이다|였다|은|는|이|가|을|를|의|에|로|와|과|도|만|나|랑|요)$")
COUNT = re.compile(r"\d[\d,.]*\s?%?|(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s?(가지|개|명|번|배)")

def is_ko(t): return len(HANGUL.findall(t)) >= 2

def width(t): return round(sum(1.7 if HANGUL.match(c) else 1 for c in t), 1)

def cut_at(t, w):
    acc, out = 0.0, ""
    for c in t:
        acc += 1.7 if HANGUL.match(c) else 1
        if acc > w: break
        out += c
    return out.rsplit(" ", 1)[0] if " " in out else out

def en_words(t): return re.findall(r"[a-z0-9']+", t.lower())

def ko_terms(t):
    """비교용 핵심어: 2글자 이상 한글 어절(조사 제거) + 영문·숫자 토큰."""
    out = set()
    for w in re.findall(r"[가-힣]+|[A-Za-z0-9]+", t):
        if re.match(r"[A-Za-z0-9]", w):
            if w.lower() not in EN_STOP: out.add(w.lower())
            continue
        stem = JOSA.sub("", w) if len(w) > 2 else w
        if len(stem) >= 2 and stem not in KO_STOP: out.add(stem)
    return out

def check(title, thumb=None):
    t = title.strip()
    ko = is_ko(t) or (thumb is not None and is_ko(thumb))
    n, w = len(t), width(t)
    issues, good = [], []
    if n > HARD: issues.append(("길이", f"{n}자 - 유튜브 제목 하드 제한은 {HARD}자"))
    elif w > DESKTOP: issues.append(("길이", f"환산 폭 {w} - 데스크톱 검색은 {DESKTOP} 근처에서 잘림 (한글 약 35자)"))
    else: good.append(f"환산 폭 {w}, 데스크톱 컷({DESKTOP}) 안쪽")
    if w > MOBILE:
        issues.append(("모바일", f'모바일 피드에는 대략 "{cut_at(t, MOBILE)}..." 까지 보임 - 주제가 살아남는지 확인'))
    caps = [x for x in re.findall(r"[A-Za-z]+", t) if len(x) > 2 and x.isupper()]
    known = {"ETF","FOMC","CPI","PPI","GDP","NVDA","AI","BTC","ETH","USD","KRW","IPO","PER","PBR","ROE","RSI","MACD"}
    shout = [x for x in caps if x not in known]
    if len(shout) > 2: issues.append(("대문자", f"전부 대문자 단어 {len(shout)}개 - 둘이 넘으면 스팸처럼 읽힘"))
    vague = sorted(set(KO_VAGUE.findall(t))) + sorted({x for x in en_words(t) if x in EN_VAGUE})
    if vague: issues.append(("막연함", f"{', '.join(vague)} - 숫자·이름·날짜로 바꾼다"))
    nums = [m.group(0).strip() for m in COUNT.finditer(t)]
    if nums: good.append(f"구체적인 숫자 있음 ({', '.join(nums[:3])})")
    else: issues.append(("숫자없음", "숫자·날짜·이름이 없음 - 가장 확실한 한 가지 개선"))
    if re.search(r"(\?|까요|나요|을까|ㄹ까)\s*$", t): good.append("제목이 열린 질문")
    if ko:
        front = [x for x in t.split()[:2] if x.strip(",.!?") not in KO_FRONT_FILLER]
        if not front: issues.append(("앞쪽", "앞 두 어절이 군말('오늘은', '드디어' 등) - 주제를 앞으로"))
    else:
        if not [x for x in en_words(t)[:3] if x not in EN_STOP]:
            issues.append(("앞쪽", "the first three words are all filler - move the subject forward"))
    if thumb:
        tw = ko_terms(t) if ko else set(en_words(t)) - EN_STOP
        hw = ko_terms(thumb) if ko else set(en_words(thumb)) - EN_STOP
        shared = tw & hw
        if shared:
            issues.append(("중복", f"썸네일이 제목 단어를 반복 ({', '.join(sorted(shared))}) - 썸네일은 제목이 안 한 말을 한다"))
        else:
            good.append("제목과 썸네일이 다른 단어로 같은 약속을 함")
        tn = len(thumb.split())
        if tn > 3 or (ko and len(re.sub(r"\s", "", thumb)) > 12):
            issues.append(("썸네일길이", f"썸네일 문구 {tn}어절/{len(re.sub(chr(32), '', thumb))}자 - 피드 크기에서는 3어절·12자 안쪽"))
    score = max(0, min(100, 100 - 14 * len(issues) + 4 * len(good)))
    return {"title": t, "thumb": thumb, "chars": n, "width": w, "score": score, "issues": issues, "good": good}

def show(r):
    print(f'\n  "{r["title"]}"' + (f'   + 썸네일 "{r["thumb"]}"' if r["thumb"] else ""))
    print(f"  {r['chars']}자 (환산 폭 {r['width']})   점수 {r['score']}/100")
    for k, m in r["issues"]: print(f"    x   {k:<6} {m}")
    for m in r["good"]:      print(f"    ok         {m}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    thumb = a[a.index("--thumb") + 1] if "--thumb" in a else None
    if "--title" in a:
        rows = [check(a[a.index("--title") + 1], thumb)]
    elif a and os.path.exists(a[0]):
        rows = [check(l, thumb) for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1)
    rows.sort(key=lambda r: -r["score"])
    if as_json: print(json.dumps(rows, ensure_ascii=False, indent=1)); return
    for r in rows: show(r)
    print()

if __name__ == "__main__":
    main()
