# 시청 지속률 (원본: yt-retention)

지속률 곡선은 유튜브가 주는 유일하게 솔직한 피드백이다.

## 데이터 얻기

- **기본 (무료)**: YouTube Studio → 영상 → 분석 → 참여도 → 시청 지속률 차트 → 다운로드 아이콘. CSV를 받는다.
- **사용자가 파일을 못 받을 때만** vidIQ `vidiq_channel_analytics` (`report: "audience_retention"`, `filters: "video==영상ID"`, 5크레딧). 결과 행을 JSON 파일로 저장해 그대로 넣는다.

```bash
python3 scripts/retention.py retention.json --duration 600 --transcript transcript.srt
```

`--duration`(초)을 주면 %축을 초로 바꾸고, `--transcript` 를 주면 **이탈 순간에 한 말**을 보여 준다. 그래야 보고서가 '흥미로운 것'이 아니라 '고칠 수 있는 것'이 된다.

## 세 가지 다른 문제

- **HOOK LEAK**: 첫 30초에 잃은 비율. 25% 미만이 건강. 고칠 곳은 언제나 대본 첫 15초이고 편집이 아니다 → 대본·훅 모드.
- **CLIFFS**: 가파른 한 번의 하락. 예고 없는 주제 전환, 광고, 긴 준비 설명 같은 '순간'.
- **SLIDE**: 중간에서 꾸준히 새는 것. 속도 문제다. 다시 쓰지 말고 자른다 → 편집 모드.

## 넘겨줄 것

가장 큰 누수 하나와 그에 대한 변경 하나. 다섯 개 목록이 아니다. 나머지는 물어볼 때만.
도입 이탈이 건강하고 slide도 완만하면 "영상은 괜찮고 문제는 포장(제목·썸네일)"이라고 말하고 제목·썸네일 모드로 보낸다.
