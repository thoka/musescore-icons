#!/usr/bin/env bash
# Screenshot einer URL mit dem headless Chrome aus dem Playwright-Cache.
#
# Aufruf:  tools/shot.sh <url> <zieldatei.png> [weitere chrome-flags ...]
# Beispiel: tools/shot.sh http://localhost:8000/ /tmp/start.png --window-size=1280,2000
#
# Die Screenshots gehoeren nicht ins Repo, sondern in den Scratchpad.
set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Aufruf: $0 <url> <zieldatei.png> [chrome-flags ...]" >&2
    exit 2
fi

url=$1
out=$2
shift 2

cache=${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}

# Bevorzugt die headless-shell, ersatzweise der volle Chromium mit --headless=new.
binary=""
extra=()
for candidate in "$cache"/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell; do
    if [ -x "$candidate" ]; then
        binary=$candidate
        break
    fi
done
if [ -z "$binary" ]; then
    for candidate in "$cache"/chromium-*/chrome-linux64/chrome; do
        if [ -x "$candidate" ]; then
            binary=$candidate
            extra+=(--headless=new)
            break
        fi
    done
fi
if [ -z "$binary" ]; then
    echo "Kein Chrome im Playwright-Cache gefunden ($cache)." >&2
    exit 1
fi

mkdir -p "$(dirname "$out")"

# --virtual-time-budget laesst die Seite ihre Fonts und ihr Layout fertig machen,
# bevor der Screenshot faellt.
"$binary" \
    "${extra[@]}" \
    --screenshot="$out" \
    --window-size=1280,900 \
    --hide-scrollbars \
    --force-device-scale-factor=2 \
    --virtual-time-budget=3000 \
    --disable-gpu \
    "$@" \
    "$url" >/dev/null 2>&1

if [ ! -s "$out" ]; then
    echo "Screenshot fehlgeschlagen: $out ist leer oder fehlt." >&2
    exit 1
fi

echo "$out"
