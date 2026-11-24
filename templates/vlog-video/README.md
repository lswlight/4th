# 브이로그 영상 제작 틀 (대마도 마운자로 3편에서 만든 것)

새 영상을 같은 스타일로 만들 때 이 폴더를 작업 폴더(`media/<편>/`)로 복사해서 고쳐 쓴다.
`media/` 는 저장소에 올라가지 않는다 (원본 영상·사진·개인정보 보호).

| 파일 | 하는 일 |
|---|---|
| `render_anim.py` + `frames.js` | 모션그래픽 장면(16:9). 증시 리뷰 쇼츠와 같은 방식: 장면별 HTML + `setT(t)` 를 Node Playwright로 프레임 렌더. 사진 전체 배경 + 그라데이션, 초록 시리즈 알약, 노란 라벨, 흰 큰 키워드, 카운트업 숫자, 줄 슬라이드, 칩, 진행 막대, 오른쪽 아래 채널명. `SCENES` 만 고치면 된다. |
| `build.py` | `edl.json` 구간 목록대로 클립·사진·모션그래픽·내레이션을 이어 붙여 본편을 만든다. 구간 캐시, PCM 이어 붙이기, 흰 상자 자막(ASS), 개인정보 흐림(`blur`), 전체 배속, adeclick+리미터. |
| `edl.sample.json` | 구간 목록 예시 (키 설명은 아래) |
| `make_teaser.py` | 9:16 세로 예고(릴스·쇼츠): 위 도현체 제목 고정 + 가운데 가로 영상 + 아래 자막 + 끝 카드. |

## 준비

- 글꼴: Noto Sans KR(500/700/900), 도현체(Do Hyeon) TTF를 한 폴더에 받고 각 파일의 `TTF=` 경로를 고친다.
  받는 법은 `skills/youtube-studio/references/package.md` 참고.
- 파이썬: numpy, Pillow / Node: playwright (클라우드 세션에는 이미 있음) / ffmpeg.
- 각 파일 맨 위의 경로(`P=`, `R=` 등)를 새 작업 폴더로 고친다.

## edl.json 구간 키

- 소리·그림 원본: `clip`+`in`/`out`(원본 영상), `vid`(모션그래픽 mp4), `img`(사진), `afile`(내레이션 wav), `aclip`/`ain`(다른 클립 소리), `aloop`
- 화면: `raw`(회전 정보 무시), `fill`(세로 영상을 16:9로 잘라 채움), `portrait`, `rot`, `blur` `[x,y,w,h,t0,t1]`(비율), `speed`
- 소리: `gain`(dB), `mute`, `vfade` `['in','out']`, `afin`
- 겹침: `subs` `[[시작,끝,문장]]`(구간 기준), `tag`(노란 라벨), `nobadge`, `force`(캐시 무시)

## 반드시 지킬 것

- 소리 규칙 여섯 가지: `skills/youtube-studio/references/audio.md`
  특히 **현장 음성은 문장 단위로 자르고, 조각마다 받아쓰기로 첫·마지막 단어를 확인**한다 (`audioqc.py cuts`).
- 휴대폰 영상·사진은 회전 정보가 틀린 경우가 많다. 프레임을 뽑아 눈으로 보고 `raw`/`fill` 을 정한다.
- 송장 이름·번호, 처방전, 병원 이름 등 개인정보는 화면과 설명란에서 가린다.
- 투자·돈 관련 내용은 단정·권유 없이, 면책 문구를 넣는다.
