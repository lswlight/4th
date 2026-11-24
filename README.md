# 유튜브 작업실 스킬 (youtube-studio)

영상을 **만들기 전과 올리기 직전**에 필요한 글과 판단을 만들어 주는 Claude 스킬입니다.
대본·훅, 제목·썸네일, 컷 편집, 쇼츠 구간, 시청 지속률, 설명란·챕터, 댓글, 업로드 계획, 채널 진단, 떡상 영상 찾기까지 한 스킬에 모았습니다.

```
skills/youtube-studio/
├── SKILL.md                 # 모드 판단, 공통 규칙, 다른 스킬과 역할 나누기
├── scripts/
│   ├── hookscore.py         # 훅(첫 15초) 점수 - 한국어·영어 자동 판별
│   ├── hooks.json           # 훅 공식 21가지 (한국어 이름·예시·판별 패턴 포함)
│   ├── title.py             # 제목+썸네일 문구 점검 (한글 화면 폭 기준 잘림)
│   ├── deadair.py           # 자막 → 컷 편집 목록 (공백·군말·NG 재시작)
│   ├── retention.py         # 시청 지속률 이탈 지점 (Studio CSV 또는 vidIQ JSON)
│   ├── swipe.py             # 아는 채널들 중 평소보다 터진 영상 (RSS, 무료)
│   └── audioqc.py           # 음성 이음 잡음(찍·뻑·틱) 정리·점검, 자르는 점 검사 (ffmpeg 필요)
├── references/              # 모드별 작업 규칙 + 말투 프로필(voice.md)
└── LICENSE-upstream         # 원본 MIT 라이선스
dist/youtube-studio.zip      # claude.ai 업로드용 패키지
```

## 이렇게 말하면 됩니다

| 모드 | 예 |
|---|---|
| 대본·훅 | "비트코인 볼린저 밴드 상단 돌파로 쇼츠 대본 써줘" |
| 제목·썸네일 | "이 영상 제목 10개 뽑고 썸네일 문구까지" |
| 편집·쇼츠 | (자막 .srt 첨부) "NG랑 군말 잘라 줘", "쇼츠로 쓸 구간 찾아줘" |
| 지속률 | "지난 영상 왜 30초에서 다 나갔는지 봐줘" |
| 검색·설명란 | "설명란이랑 태그, 챕터 써줘" |
| 댓글 | (댓글 붙여넣기) "답글 써 주고 고정할 거 골라 줘" |
| 업로드 계획 | "다음 주 업로드 계획 짜줘, 시간은 6시간" |
| 채널 진단 | "내 채널 왜 안 크는지 진단해줘" |
| 바이럴 찾기 | "요즘 코인 쇼츠 중에 평소보다 터진 영상 찾아줘" |

## 다른 스킬·도구와 역할 나누기

| 일 | 맡는 곳 |
|---|---|
| 특정 영상 링크를 장면 단위로 분석 (Gemini가 화면을 직접 봄), 스토리보드, 영상 생성 프롬프트 | `youtube-analyzer` 스킬 |
| 쿠팡 파트너스 쇼츠 | `coupang-affiliate-shorts` 스킬 |
| 떡상 영상 찾기 (모르는 채널까지) | vidIQ 커넥터 — 크레딧은 여기에 우선 사용 |
| 기획, 대본, 점수 매기기, 판단 | 이 스킬 (Claude) |

## 원본과 달라진 점

원본: [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) (MIT, 영어 스킬 11개 + 도구 6개)

- **한국어화**: 원본 점수 규칙은 영어 단어만 찾아서 같은 뜻의 한국어 훅이 62점 → 34점으로 나왔습니다. 한국어 규칙(호명 "~이시라면/여러분", 손실 "놓치/손해", 궁금증 "왜/아무도", 음절 기준 길이)을 추가해 같은 훅이 59점이 됩니다. 한국어 규칙은 실제 데이터로 보정하지 않았으니 참고용입니다.
- **제목 길이**: 글자 수 대신 화면 폭(한글 1.7배)으로 잽니다. 데스크톱 약 35자, 모바일 약 23자.
- **11개 → 1개 스킬**: claude.ai에 한 번만 올리면 되도록 모드로 합쳤습니다.
- **겹치는 기능 정리 (vidIQ 무료 크레딧 월 약 150, 호출당 5)**
  - 떡상 영상 찾기: vidIQ 우선 (유튜브 전체 탐색). 크레딧이 없으면 `swipe.py` + 채널 RSS로 아는 채널만 무료 탐색.
  - 챕터: `chapters.py`(영어 전용)는 빼고 Claude가 자막을 직접 읽고 씀. vidIQ 챕터 생성도 쓰지 않음 (품질 차이 거의 없음).
  - 키워드·지속률·댓글·채널 분석: 사용자 자료(Studio CSV, 붙여 넣은 댓글) 먼저, 못 줄 때만 vidIQ.
  - 레퍼런스 영상 장면 분석: `youtube-analyzer` (Gemini 무료 한도).
- **투자 콘텐츠 규칙** 추가: 수익 보장·매수 권유 금지, 조건부 시나리오, 면책 문구.

## 도구 직접 돌리기

```bash
python3 skills/youtube-studio/scripts/hookscore.py --hook "월급 300 이하 직장인이시라면, 다음 주 FOMC 전에 이것 하나만 확인하세요."
python3 skills/youtube-studio/scripts/title.py --title "볼린저 밴드 상단 돌파 후 꼭 볼 3가지" --thumb "진짜 돌파?"
python3 skills/youtube-studio/scripts/deadair.py transcript.srt
python3 skills/youtube-studio/scripts/retention.py retention.csv --duration 600 --transcript transcript.srt
python3 skills/youtube-studio/scripts/swipe.py --rss @채널1 @채널2 --save c.json && python3 skills/youtube-studio/scripts/swipe.py c.json --min 2.0
python3 skills/youtube-studio/scripts/audioqc.py check 완성본.mp4
python3 skills/youtube-studio/scripts/audioqc.py cuts cuts.txt --export 조각/   # 현장 음성 자르는 점 검사
```

`swipe.py --rss` 는 www.youtube.com 접속이 필요합니다. claude.ai에서 `NETWORK_BLOCKED` 가 나오면 Settings → Capabilities 의 코드 실행 네트워크 설정에서 `www.youtube.com` 을 허용하거나, 영상 목록을 붙여 넣으면 됩니다.

## 설치 (모든 채팅에 적용하려면)

- **claude.ai (웹·앱·클라우드 세션 전체)**: `./build.sh` 로 만든 `dist/youtube-studio.zip` 을 Settings → Capabilities → Skills 에 업로드합니다. 한 번 올리면 모든 채팅방에서 쓰입니다.
- **Claude Code (이 저장소 안)**: 저장소를 열면 `.claude/skills/youtube-studio` 가 자동으로 잡힙니다.

말투 프로필 `skills/youtube-studio/references/voice.md` 를 먼저 채우면 대본·제목·댓글이 내 말투로 나옵니다.
