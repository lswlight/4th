# CLAUDE.md

유튜브 채널 운영 스킬(`youtube-studio`)의 원본 저장소. 사용법은 README.md 참고.

## 구조

- `skills/youtube-studio/`: 스킬 원본. `.claude/skills/youtube-studio` 는 이 폴더를 가리키는 심볼릭 링크이므로 원본만 수정한다.
- `dist/youtube-studio.zip`: claude.ai 업로드용 패키지. 직접 수정하지 말고 `./build.sh` 로 다시 만든다.

## 작업 규칙

- 스킬 파일을 바꾸면 `./build.sh` 를 실행해 `dist/youtube-studio.zip` 도 함께 커밋한다.
- `scripts/*.py` 는 파이썬 표준 라이브러리만 쓴다. 외부 패키지를 추가하지 않는다.
- 스크립트 원본은 Jake Schincariol의 youtube-agent-skill (MIT). `LICENSE-upstream` 을 지우지 않는다.
- 다른 계정 스킬과 일을 나눈다: 특정 영상 링크의 장면 분석은 `youtube-analyzer`, 쿠팡 쇼츠는 `coupang-affiliate-shorts`. 같은 기능을 이 스킬에 다시 넣지 않는다.
- 유튜브 자동 업로드는 넣지 않는다. 결과물은 복사·붙여넣기용이다.
- 투자 콘텐츠는 매수·매도 권유 없이 조건부로 쓰고 면책 문구를 넣는다.
- 공개 저장소다. 이메일·계정 ID·API 키 같은 개인 정보를 넣지 않는다.
- 문서와 스킬 결과물은 한국어로 작성하고, 사용자에게 하는 말도 한국어로 한다.
