# 바이럴 찾기 (원본: yt-viral)

조회수 순위는 채널 크기 순위다. 아이디어를 보려면 **그 채널 평소 조회수 대비 몇 배 나왔는지**로 봐야 한다.
구독자 200만 채널의 40만 조회는 평범한 화요일이고, 평소 3만인 채널의 40만은 연구할 대상이다.

## 찾기: vidIQ 먼저 (크레딧을 여기에 쓴다)

이 모드는 vidIQ 크레딧을 쓸 가치가 가장 큰 곳이다. vidIQ는 **모르는 채널까지** 유튜브 전체에서 찾고, 무료 대안은 아는 채널만 본다.

1. `vidiq_balance` (무료)로 잔액을 본다. 5 미만이면 아래 "크레딧이 없을 때"로 간다.
2. `vidiq_outliers` **한 번**에 끝낸다 (5크레딧):
   - `keyword`: 주제 (한국어 그대로), `language: "ko"`
   - `contentType`: `"short"` 또는 `"long"`
   - `limit: 20~30` — 한 번에 넉넉히 받고 다시 부르지 않는다
   - 특정 경쟁 채널이면 `channelIds`, 특정 영상과 비슷한 것이면 `seedVideoId`
   - `publishedWithin` 은 사용자가 기간을 말할 때만
   - 복붙 채널을 거르려면 `minEngagementRate: 0.02`
   결과의 breakout score가 배수다.

## 크레딧이 없을 때: swipe.py (무료, 아는 채널만)

사용자에게 경쟁 채널 3~10개(@핸들, 채널 URL, UC로 시작하는 ID)를 받는다.

```bash
python3 scripts/swipe.py --rss @채널1 @채널2 UCxxxx --save collected.json   # 채널당 최근 15개
python3 scripts/swipe.py collected.json --min 2.0
```

- `NETWORK_BLOCKED` 가 나오면 (claude.ai 코드 실행은 기본으로 youtube.com 이 막혀 있다) 두 가지 중 하나를 안내한다:
  Settings → Capabilities 에서 `www.youtube.com` 을 허용하거나, 채널 페이지의 영상 목록(제목·조회수)을 복사해 붙여 달라고 한다.
  붙여 준 목록은 `[{"channel","title","views","published"}]` JSON으로 바꿔 같은 스크립트에 넣는다.
- 채널당 영상 **4개 미만**은 중앙값이 의미 없어 빠진다. 올라온 지 **72시간 미만** 영상도 빠진다.
- RSS는 쇼츠와 롱폼이 섞여 나온다. 형식이 다르면 사용자에게 어느 쪽인지 묻고 나머지는 뺀다.

## 읽기

1. 상위 다섯 개를 배수와 함께.
2. 각 제목이 `scripts/hooks.json` 21가지 공식 중 어디에 해당하는지 (swipe.py 는 자동으로, vidIQ 결과는 `hookscore.py --json` 에 제목을 넣어 `formula` 확인). **이건 보이는 제목 단어에 대한 판단이지, 영상이 왜 떴는지에 대한 주장이 아니다** — 그렇게 말하고 전한다.
3. 다섯 개가 공유하는 **구조적 공통점 하나**.
4. 더 어려운 줄: 이 중 사용자가 **이번 주에, 자기 말투로, 가진 것으로** 실제 만들 수 있는 게 무엇인지.

## 더 깊이 보려면

상위 영상의 장면·편집·대본까지 뜯어봐야 하면 그 링크를 **youtube-analyzer** 로 넘긴다 (Gemini가 영상을 직접 본다, 무료 한도). 여기서 같은 분석을 하지 않는다.

**읽기만 하고 긁어 오지 않는다.** 공개 목록만. 사용자 계정으로 로그인하거나 자격 증명을 쓰지 않는다.
