#!/bin/sh
# site/의 그림 파일을 다시 만든다. 레포지토리 최상위에서 실행한다. macOS의 Chrome과 sips를 쓴다.
#   tools/site/render.sh
set -eu
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
shot() { "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --blink-settings=preferredColorScheme=1 \
  --virtual-time-budget=5000 --window-size="$2" --screenshot="$3" "file://$PWD/$1" 2>/dev/null; }
shot tools/site/og-image.html 1200,630 site/og-image.png
# 다크 모드인 컴퓨터에서도 라이트 색으로 그린다(preferredColorScheme=1). 헤드리스 창은 500px보다 좁아지지 않는다. 그래서 500px 창 가운데에 그린 뒤 가운데를 자른다.
for size in 32 180; do
  name=$([ "$size" = 32 ] && echo favicon-32 || echo apple-touch-icon)
  shot "tools/site/icon.html#$size" 500,500 "site/$name.png"
  sips -c "$size" "$size" "site/$name.png" >/dev/null
done
