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
control() { # control <label> <file relative to the copy> <text appended to it>
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  printf '%s\n' "$3" >> "$dir/$2"
  if build "$dir"; then
    printf '    FAIL  control "%s": the build passed it\n' "$1"
  else
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  fi
}
weight() { # weight <label> <style> <weight>: a type style asking for a weight no font ships
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  python3 -I - "$dir/tokens.json" "$2" "$3" << 'EOF'
import json, sys
p, name, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = json.load(open(p, encoding="utf-8"))
for g in t["type"]["groups"]:
    for s in g["styles"]:
        if s["name"] == name: s["fontWeight"] = w
json.dump(t, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
EOF
  if build "$dir"; then
    printf '    FAIL  control "%s": the build passed it\n' "$1"
  else
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  fi
}
narrow_icon() { # narrow_icon <label>: one icon in the copy's regular font given back its one-cell advance
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  uv run -q --project "$HERE" --locked python -I - "$dir/fonts/FiraCodeNF.woff2" << 'PYEOF'
import sys
from fontTools.ttLib import TTFont
f = TTFont(sys.argv[1]); name = f.getBestCmap()[0xEB4B]
f["hmtx"][name] = (1200, f["hmtx"][name][1]); f.flavor = "woff2"; f.save(sys.argv[1])
PYEOF
  if build "$dir"; then
    printf '    FAIL  control "%s": the build passed it\n' "$1"
  else
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  fi
}
edited() { # edited <label> <file> <sed expression> [build arguments]: a copy with one line changed
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  sed -i -e "$3" "$dir/$2"
  if (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/build-tokens.py "${@:4}") > "$dir/out.txt" 2>&1; then
    printf '    FAIL  control "%s": the build passed it\n' "$1"
  else
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  fi
}
echo "the controls, each a copy with one mistake that must be refused:"
control "a hex colour" components/bundle.css '.x{color:#ff0000}'
control "an rgb() colour" components/bundle.css '.x{color:rgb(255,0,0)}'
control "an hsl() colour" components/bundle.css '.x{background:hsl(0 0% 50%)}'
control "a named colour" components/bundle.css '.x{border-color:red}'
control "a second breakpoint" components/bundle.css '@media (min-width:50rem){.x{display:none}}'
control "another font family" components/bundle.css '.x{font-family:Arial}'
control "a literal font shorthand" components/bundle.css '.x{font:700 1rem/1.4 var(--font-ui)}'
control "a typed weight" components/bundle.css '.x{font-weight:600}'
control "typed tracking" components/bundle.css '.x{letter-spacing:.1em}'
control "a typed length" components/bundle.css '.x{padding:13px}'
control "a typed length in calc()" components/bundle.css '.x{width:calc(100% - 2rem)}'
control "a misspelt token" components/bundle.css '.x{color:var(--acton)}'
control "a value defined in the stylesheet" components/bundle.css '.x{--gap:var(--space-2)}'
control "a font in the stylesheet" components/bundle.css '@font-face{font-family:"X";src:url(x.woff2)}'
control "a font embedded as data" components/bundle.css '.x{background:url(data:font/woff2;base64,AAAA)}'
control "a relative link out of fonts/" fonts/licenses/README.md '[FONTS.md](../../FONTS.md)'
control "a link to this repository" fonts/licenses/README.md '[x](https://github.com/AlonRR/printable-parts-design-system/blob/main/FONTS.md)'
weight "a weight no font ships" body 500
narrow_icon "an icon drawn past its advance"
control "a class without the ws- prefix" components/bundle.css '.note{color:var(--ink)}'
control "a wide-screen rule undone by a later one" components/bundle.css '@media (min-width:56rem){.ws-x{padding:0}} .ws-x{padding-left:var(--space-1)}'
control "a grid popover WebKit stretches" components/bundle.css '.ws-x:popover-open{display:grid;gap:var(--space-2)}'
edited "pyproject.toml on another version" pyproject.toml 's/^version = ".*"/version = "9.9.9"/'
edited "no changelog entry for the version" CHANGELOG.md "s/^## v$ver .*/## Unreleased/" # dated or not
edited "a tag that names another version" CHANGELOG.md 's/^$//' --tag v9.9.9
edited "a tag on an entry still unreleased" CHANGELOG.md "s/^## v$ver .*/## v$ver (unreleased)/" --tag "v$ver"

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
