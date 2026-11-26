#!/usr/bin/env bash
# 글꼴 받기: Noto Sans KR 500/700/900 + 배민 도현체 (둘 다 무료 공개 글꼴, Google Fonts)
# 사용: bash get_fonts.sh   → ~/.cache/slide-video/fonts (SV_FONTS 로 바꿀 수 있음)
set -e
DIR="${SV_FONTS:-$HOME/.cache/slide-video/fonts}"; mkdir -p "$DIR"
CSS=$(curl -s -A "Wget/1.21" "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&family=Do+Hyeon")
get() { url=$(echo "$CSS" | grep -A6 "font-family: '$1'" | grep -A4 "font-weight: $2" | grep -o 'https://[^)]*\.ttf' | head -1); curl -s -o "$DIR/$3" "$url"; echo "$3 ← $url"; }
get 'Noto Sans KR' 500 NotoSansKR-500.ttf
get 'Noto Sans KR' 700 NotoSansKR-700.ttf
get 'Noto Sans KR' 900 NotoSansKR-900.ttf
get 'Do Hyeon' 400 DoHyeon-Regular.ttf
ls -la "$DIR"
