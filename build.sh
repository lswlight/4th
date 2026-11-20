#!/usr/bin/env bash
# claude.ai 업로드용 스킬 zip 생성 → dist/youtube-studio.zip
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p dist
rm -f dist/youtube-studio.zip
(cd skills && zip -rq ../dist/youtube-studio.zip youtube-studio -x '*.DS_Store' '*/__pycache__/*')
echo "built dist/youtube-studio.zip"
