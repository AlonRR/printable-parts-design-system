#!/usr/bin/env bash
# Hold scripts/check-contrast.py to its claims: it passes on the repository's tokens, and each
# kind of mistake it says it catches makes it fail.
#
#   bash tests/test-check-contrast.sh
#
# Each control is a copy of tokens.json with one colour changed or added. A check that cannot fail
# is not a check.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

copy() { # copy <dir>: the script and the tokens it reads
  mkdir -p "$1/scripts"
  cp "$HERE/scripts/check-contrast.py" "$1/scripts/"
  cp "$HERE/tokens.json" "$1/"
}
run() { (cd "$1" && uv run -q --project "$HERE" --locked python scripts/check-contrast.py) > "$1/out.txt" 2>&1; }

pass=0
fail=0
echo "the check on the repository's tokens:"
copy "$tmp/base"
if run "$tmp/base"; then
  printf '    ok    passes\n'
  pass=$((pass + 1))
else
  printf '    FAIL  fails:\n'
  grep FAIL "$tmp/base/out.txt" | sed 's/^/          /' | head -10
  fail=$((fail + 1))
fi

controls=0
refused=0
control() { # control <label> <pattern> <python statement on the token list `t`>: refused with /pattern/
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  python3 -I - "$dir/tokens.json" "$3" << 'EOF'
import json, sys
p, change = sys.argv[1], sys.argv[2]
d = json.load(open(p, encoding="utf-8"))
t = {c["name"]: c for c in d["color"]["tokens"]}
exec(change, {"t": t, "d": d})
json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
EOF
  if run "$dir"; then
    printf '    FAIL  control "%s": the check passed it\n' "$1"
  elif grep -qE -- "$2" "$dir/out.txt"; then
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  else
    printf '    FAIL  control "%s": refused, but not with /%s/\n' "$1" "$2"
  fi
}
# Each control names the rule it tests by the message it expects: refused by another rule, it proves nothing.
echo "the controls, each a copy with one mistake that must be refused, by its own rule:"
control "faint body text" '^FAIL light text +ink-muted on' 't["ink-muted"]["value"]["light"] = "#a0a8b0"'
control "a faint control border" '^FAIL dark +non-text border-strong on' 't["border-strong"]["value"]["dark"] = "#2a3540"'
control "a part that vanishes on the dark stage" '^FAIL dark +part +model-tpu' 't["model-tpu"]["value"]["dark"] = "#2b2b2b"'
control "a colour in no pair" '^FAIL highlight: in no checked pair' 'd["color"]["tokens"].append({"name": "highlight", "value": "#ffcc00", "usage": "x"})'
control "a scrim between, losing both the dialog's face and edge" '^FAIL light +dialog' 't["scrim"]["value"]["light"] = "#16222c4d"'
# The surfaces' depth (D90): v0.7.0's dark well, lighter than the page and the panel; and a panel below the page
control "a dark well lighter than the page" '^FAIL dark +depth .*out of order' 't["surface-sunken"]["value"]["dark"] = "#1f2b35"'
control "a light panel darker than the page" '^FAIL light +depth .*out of order' 't["surface-raised"]["value"]["light"] = "#f0f2f3"'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
