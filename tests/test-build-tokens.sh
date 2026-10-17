#!/usr/bin/env bash
# Hold scripts/build-tokens.py to its own claims: on the repository's files it passes and writes
# tokens.css byte for byte as committed, and each mistake it says it catches makes it fail.
#
#   bash tests/test-build-tokens.sh
#
# Each control is a copy of the files the build reads (tokens.json, fonts/, components/bundle.css,
# the script) with one mistake put back. A check that cannot fail is not a check.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

copy() { # copy <dir>: the build's inputs, as committed in the working tree
  mkdir -p "$1/scripts" "$1/components"
  cp "$HERE/scripts/build-tokens.py" "$1/scripts/"
  cp "$HERE/tokens.json" "$HERE/pyproject.toml" "$HERE/CHANGELOG.md" "$1/"
  cp "$HERE/components/bundle.css" "$1/components/"
  cp -r "$HERE/fonts" "$1/"
}
build() { (cd "$1" && uv run -q --project "$HERE" --locked python scripts/build-tokens.py) > "$1/out.txt" 2>&1; }

pass=0
fail=0
echo "the build on the repository's files:"
copy "$tmp/base"
if build "$tmp/base"; then
  printf '    ok    passes\n'
  pass=$((pass + 1))
else
  printf '    FAIL  fails:\n'
  sed 's/^/          /' "$tmp/base/out.txt" | head -20
  fail=$((fail + 1))
fi
if cmp -s "$tmp/base/tokens.css" "$HERE/tokens.css"; then
  printf '    ok    writes tokens.css byte for byte as committed\n'
  pass=$((pass + 1))
else
  printf '    FAIL  writes a different tokens.css\n'
  fail=$((fail + 1))
fi

# A release: with its changelog entry dated, the build passes as the tag that names its version.
ver="$(python3 -I -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["version"])' "$HERE/tokens.json")"
copy "$tmp/dated"
sed -i "s/^## v$ver .*/## v$ver (1 Jan 2026)/" "$tmp/dated/CHANGELOG.md"
if (cd "$tmp/dated" && uv run -q --project "$HERE" --locked python scripts/build-tokens.py --tag "v$ver") > "$tmp/dated/out.txt" 2>&1; then
  printf '    ok    passes as the tag v%s, its changelog entry dated\n' "$ver"
  pass=$((pass + 1))
else
  printf '    FAIL  fails as the tag v%s, its changelog entry dated:\n' "$ver"
  sed 's/^/          /' "$tmp/dated/out.txt" | head -20
  fail=$((fail + 1))
fi

controls=0
refused=0
judge() { # judge <label> <pattern> [build arguments]: the build on copy c$controls must fail, saying /pattern/
  local dir="$tmp/c$controls" label="$1" pattern="$2"
  shift 2
  controls=$((controls + 1))
  if (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/build-tokens.py "$@") > "$dir/out.txt" 2>&1; then
    printf '    FAIL  control "%s": the build passed it\n' "$label"
  elif grep -qE -- "$pattern" "$dir/out.txt"; then
    printf '    ok    control "%s": refused\n' "$label"
    refused=$((refused + 1))
  else
    printf '    FAIL  control "%s": refused, but not with /%s/:\n' "$label" "$pattern"
    grep FAIL "$dir/out.txt" | sed 's/^/          /' | head -5
  fi
}
control() { # control <label> <pattern> <file relative to the copy> <text appended to it>
  copy "$tmp/c$controls"
  printf '%s\n' "$4" >> "$tmp/c$controls/$3"
  judge "$1" "$2"
}
weight() { # weight <label> <pattern> <style> <weight>: a type style asking for a weight no font ships
  copy "$tmp/c$controls"
  python3 -I - "$tmp/c$controls/tokens.json" "$3" "$4" << 'PYEOF'
import json, sys
p, name, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = json.load(open(p, encoding="utf-8"))
for g in t["type"]["groups"]:
    for s in g["styles"]:
        if s["name"] == name: s["fontWeight"] = w
json.dump(t, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PYEOF
  judge "$1" "$2"
}
narrow_icon() { # narrow_icon <label> <pattern>: one icon in the copy's regular font given back its one-cell advance
  copy "$tmp/c$controls"
  uv run -q --project "$HERE" --locked python -I - "$tmp/c$controls/fonts/FiraCodeNF.woff2" << 'PYEOF'
import sys
from fontTools.ttLib import TTFont
f = TTFont(sys.argv[1]); name = f.getBestCmap()[0xEB4B]
f["hmtx"][name] = (1200, f["hmtx"][name][1]); f.flavor = "woff2"; f.save(sys.argv[1])
PYEOF
  judge "$1" "$2"
}
edited() { # edited <label> <pattern> <file> <sed expression> [build arguments]: a copy with one line changed
  copy "$tmp/c$controls"
  sed -i -e "$4" "$tmp/c$controls/$3"
  judge "$1" "$2" "${@:5}"
}
# Each control names the rule it tests by the message it expects: a control refused by another rule
# proves nothing (until v0.5.1 every CSS control here used the class .x, which the prefix rule refused).
B=components/bundle.css
echo "the controls, each a copy with one mistake that must be refused, by its own rule:"
control "a hex colour" 'hard-coded colour #ff0000' $B '.ws-x{color:#ff0000}'
control "an rgb() colour" "types a colour in 'color:rgb" $B '.ws-x{color:rgb(255,0,0)}'
control "an hsl() colour" "types a colour in 'background:hsl" $B '.ws-x{background:hsl(0 0% 50%)}'
control "a named colour" "types a colour in 'border-color:red'" $B '.ws-x{border-color:red}'
control "a colour mixed in the stylesheet" "types a colour in 'color:color-mix" $B '.ws-x{color:color-mix(in srgb, var(--ink) 50%, var(--surface))}'
control "a system colour" "types a colour in 'color:CanvasText'" $B '.ws-x{color:CanvasText}'
control "a system colour in another query" "a system colour goes only in @media \(forced-colors:active\)" $B '@media (pointer:coarse){.ws-x{color:Canvas}}'
control "a gradient" "draws a gradient" $B '.ws-x{background:linear-gradient(var(--ink),var(--surface))}'
control "a second breakpoint" 'has @media \(min-width:50rem\)' $B '@media (min-width:50rem){.ws-x{display:none}}'
control "a header rule at the layout's breakpoint" 'styles .ws-header__more at @media \(min-width:56rem\); the header changes at breakpoint-header' $B '@media (min-width:56rem){.ws-header__more{display:none}}'
edited "no header breakpoint" "should show the header's actions in its row" $B 's/@media (min-width:64rem)/@media (min-width:56rem)/'
edited "side by side on any landscape screen" "should put the sidebar beside the stage at @media .* landscape only from breakpoint-side-min" $B 's/,(min-aspect-ratio:4\/3) and (min-width:48rem) and/,(min-aspect-ratio:4\/3) and/'
edited "side by side on any short screen" "should put the sidebar beside the stage at @media .* a short screen only from breakpoint-side-short" $B 's/ and (min-height:30rem)//g'
edited "a stacked landscape screen pinned" "should pin nothing on a short screen or a stacked landscape one" $B 's/@media (max-height:30rem),(min-aspect-ratio:4\/3){/@media (max-height:30rem){/'
control "a container query" 'has @container' $B '@container (min-width:30rem){.ws-x{display:none}}'
control "an animation" 'has @keyframes' $B '@keyframes ws-x{from{opacity:0}to{opacity:1}}'
control "another font family" "sets 'font-family:Arial'" $B '.ws-x{font-family:Arial}'
control "a literal font shorthand" "sets 'font:700 1rem" $B '.ws-x{font:700 1rem/1.4 var(--font-ui)}'
control "a typed weight" "sets 'font-weight:600'" $B '.ws-x{font-weight:600}'
control "a font-size keyword" "sets 'font-size:smaller'" $B '.ws-x{font-size:smaller}'
control "a unitless line height" "sets 'line-height:2'" $B '.ws-x{line-height:2}'
control "typed tracking" "sets 'letter-spacing:.1em'" $B '.ws-x{letter-spacing:.1em}'
control "a typed opacity" "sets 'opacity:.5'" $B '.ws-x{opacity:.5}'
control "a typed length" 'types the length 13px' $B '.ws-x{padding:13px}'
control "a typed length in calc()" 'types the length 2rem' $B '.ws-x{width:calc(100% - 2rem)}'
control "a misspelt token" 'reads --acton' $B '.ws-x{color:var(--acton)}'
control "a value defined in the stylesheet" 'sets --gap' $B '.ws-x{--gap:var(--space-2)}'
control "a token re-set in the stylesheet" 'sets --ink' $B '.ws-x{--ink:var(--ink-muted)}'
control "control-h re-set for a mouse" 'sets --control-h' $B '.ws-x{--control-h:var(--tap)}'
control "a font in the stylesheet" 'declares or embeds a font' $B '@font-face{font-family:"X";src:url(x.woff2)}'
control "a font embedded as data" 'declares or embeds a font' $B '.ws-x{background:url(data:font/woff2;base64,AAAA)}'
control "a relative link out of fonts/" 'outside fonts/' fonts/licenses/README.md '[FONTS.md](../../FONTS.md)'
control "a link to this repository" 'links this repository' fonts/licenses/README.md '[x](https://github.com/AlonRR/printable-parts-design-system/blob/main/FONTS.md)'
weight "a weight no font ships" 'asks for weight 500' body 500
narrow_icon "an icon drawn past its advance" 'draw past their advance'
control "a class without the ws- prefix" 'styles the class .note' $B '.note{color:var(--ink)}'
control "a wide-screen rule undone by a later one" 'and again later outside it' $B '@media (min-width:56rem){.ws-x{padding:0}} .ws-x{padding-left:var(--space-1)}'
control "a grid popover WebKit stretches" 'without align-content' $B '.ws-x:popover-open{display:grid;gap:var(--space-2)}'
edited "pyproject.toml on another version" 'pyproject.toml says version 9.9.9' pyproject.toml 's/^version = ".*"/version = "9.9.9"/'
edited "no changelog entry for the version" "has no '## v" CHANGELOG.md "s/^## v$ver .*/## Unreleased/" # dated or not
edited "a tag that names another version" 'names another version' CHANGELOG.md 's/^$//' --tag v9.9.9
edited "a tag on an entry still unreleased" 'still marked unreleased' CHANGELOG.md "s/^## v$ver .*/## v$ver (unreleased)/" --tag "v$ver"

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
