#!/usr/bin/env bash
# Hold scripts/compare-shots.py to its own claims: two folders of the same images pass, and each
# difference it says it finds makes it fail, with its own message.
#
#   bash tests/test-compare-shots.sh
#
# The images are made here, small, with Pillow: one opaque RGB, as check-previews.py writes them,
# and one RGBA, in a subfolder. The first control is the one a comparison through Pillow's getbbox()
# on RGBA misses: one opaque pixel changed in colour, which leaves the difference image transparent
# everywhere. A check that cannot fail is not a check.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

make() { # make <dir> [change]: the two images in <dir>/shots, with the change (Python) made to them
  uv run -q --project "$HERE" --locked python -I - "$1/shots" "${2:-}" << 'EOF'
import os, sys
from PIL import Image
d, change = sys.argv[1], sys.argv[2]
rgb = Image.new("RGB", (40, 30), (240, 244, 248)); rgb.putpixel((5, 5), (20, 30, 40))
rgba = Image.new("RGBA", (20, 20), (10, 20, 30, 128))
v = {"rgb": rgb, "rgba": rgba, "drop": [], "extra": [], "folder": True}
exec(change, v)
if v["folder"]:
    os.makedirs(f"{d}/sub")
    for name, im in [("a.png", v["rgb"]), ("sub/b.png", v["rgba"])] + [(e, v["rgb"]) for e in v["extra"]]:
        if name not in v["drop"]:
            im.save(f"{d}/{name}")
EOF
}
compare() { # compare <dir>: the images before against <dir>/shots
  mkdir -p "$1"
  uv run -q --project "$HERE" --locked python "$HERE/scripts/compare-shots.py" "$tmp/before/shots" "$1/shots" > "$1/out.txt" 2>&1
}

pass=0
fail=0
make "$tmp/before"
echo "the comparison of two folders of the same images:"
make "$tmp/same"
if compare "$tmp/same" && grep -qE '^2 before, 2 after; 2 pairs compared, 0 differ, 0 only before, 0 only after$' "$tmp/same/out.txt"; then
  printf '    ok    passes (%s)\n' "$(head -1 "$tmp/same/out.txt")"
  pass=$((pass + 1))
else
  printf '    FAIL  fails:\n'
  sed 's/^/          /' "$tmp/same/out.txt" | head -10
  fail=$((fail + 1))
fi

controls=0
refused=0
control() { # control <label> <pattern> <change>: the folder made with the change must fail, saying /pattern/
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  make "$dir" "$3"
  if compare "$dir"; then
    printf '    FAIL  control "%s": the comparison passed it\n' "$1"
  elif grep -qE -- "$2" "$dir/out.txt"; then
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  else
    printf '    FAIL  control "%s": failed, but not with /%s/:\n' "$1" "$2"
    grep FAIL "$dir/out.txt" | sed 's/^/          /' | head -5
  fi
}
echo "the controls, each a difference that must be refused:"
control "one opaque pixel a shade off" '^FAIL a\.png: pixels differ from 7,9 to 8,10$' 'rgb.putpixel((7, 9), (240, 244, 249))'
control "one pixel a shade more transparent" '^FAIL sub/b\.png: pixels differ from 3,4 to 4,5$' 'rgba.putpixel((3, 4), (10, 20, 30, 127))'
control "an image a pixel wider" '^FAIL a\.png: 40 x 30 RGB before, 41 x 30 RGB after$' 'rgb = rgb.crop((0, 0, 41, 30))'
control "an image given alpha" '^FAIL a\.png: 40 x 30 RGB before, 40 x 30 RGBA after$' 'rgb = rgb.convert("RGBA")'
control "a screenshot missing after" '^FAIL sub/b\.png: only before$' 'drop.append("sub/b.png")'
control "a screenshot only after" '^FAIL extra\.png: only after$' 'extra.append("extra.png")'
control "no screenshot in common" '^FAIL nothing to compare: no file is in both folders$' 'drop += ["a.png", "sub/b.png"]'
control "a folder that is not there" 'shots is not a folder$' 'folder = False'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
