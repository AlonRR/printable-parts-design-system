#!/usr/bin/env bash
# Hold scripts/fit-icon-advances.py to its claims: on the repository's fonts, which it has already
# fitted, it changes nothing; and an icon whose advance is put back to one text cell gets an advance
# as wide as it draws again, the text glyphs untouched.
#
#   bash tests/test-fit-icon-advances.sh
#
# Added with the test gates (D101, 17 Nov 2026): the script had no test, so no line of it was
# covered. The script writes the fonts beside it, so every run is on a copy. A check that cannot
# fail is not a check.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

copy() { # copy <dir>: the script and the fonts it fits
  mkdir -p "$1/scripts" "$1/fonts"
  cp "$HERE/scripts/fit-icon-advances.py" "$1/scripts/"
  cp "$HERE"/fonts/*.woff2 "$1/fonts/"
}
run() { (cd "$1" && uv run -q --project "$HERE" --locked python scripts/fit-icon-advances.py) > "$1/out.txt" 2>&1; }
font() { # font <woff2> <python>: the font open as `font`, with its first icon's glyph name in `icon`, runs <python>
  uv run -q --project "$HERE" --locked python -I - "$1" "$2" << 'EOF'
import sys
from fontTools.ttLib import TTFont
path, code = sys.argv[1], sys.argv[2]
font = TTFont(path)
glyf = font["glyf"]
icon = next(n for cp, n in sorted(font.getBestCmap().items())
            if 0xE000 <= cp < 0xF900 and glyf[n].numberOfContours and (glyf[n].recalcBounds(glyf) or glyf[n].xMax > 1200))
text = font.getBestCmap()[ord("A")]
exec(code)
EOF
}

pass=0
fail=0
result() { # result <ok> <label>
  if [ "$1" -eq 0 ]; then
    printf '    ok    %s\n' "$2"
    pass=$((pass + 1))
  else
    printf '    FAIL  %s\n' "$2"
    sed 's/^/          /' "$dir/out.txt" | head -10
    fail=$((fail + 1))
  fi
}

echo "the script on the repository's fonts, already fitted:"
dir="$tmp/base"
copy "$dir"
run "$dir"
result $? "runs"
grep -cE '^fonts[/\]FiraCodeNF(-Bold)?\.woff2: 0 icon advances set to their drawn width$' "$dir/out.txt" | grep -qx 2
result $? "sets no advance in either font"
cmp -s "$dir/fonts/FiraCodeNF.woff2" "$HERE/fonts/FiraCodeNF.woff2" && cmp -s "$dir/fonts/FiraCodeNF-Bold.woff2" "$HERE/fonts/FiraCodeNF-Bold.woff2"
result $? "leaves both fonts byte for byte as they were"

echo "an icon put back to one text cell of advance:"
dir="$tmp/cell"
copy "$dir"
font "$dir/fonts/FiraCodeNF.woff2" '
font["hmtx"][icon] = (1200, font["hmtx"][icon][1]); font.flavor = "woff2"; font.save(path)'
run "$dir"
result $? "runs"
grep -qE '^fonts[/\]FiraCodeNF\.woff2: 1 icon advances set to their drawn width$' "$dir/out.txt"
result $? "sets that one advance"
font "$dir/fonts/FiraCodeNF.woff2" '
g = glyf[icon]; g.recalcBounds(glyf)
assert font["hmtx"][icon][0] == g.xMax, (icon, font["hmtx"][icon], g.xMax)
assert font["hmtx"][text][0] == 1200, font["hmtx"][text]' > "$dir/out.txt" 2>&1
result $? "to the width the icon draws, the text glyphs still one cell"

printf '\n%s checks passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ]
