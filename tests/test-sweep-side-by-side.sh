#!/usr/bin/env bash
# Hold scripts/sweep-side-by-side.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-sweep-side-by-side.sh
#
# Each control is a copy of the files the sweep reads (the sweep, check-previews.py, whose page and
# constants it takes, build-tokens.py, from which they read H, tokens.json, tokens.css, components/,
# fonts/) with one mistake put in, swept only over the screens where it shows, so the set runs in a
# minute or two. A control counts as refused only if the run fails AND its output names the expected
# check: a run that fails for another reason proves nothing. Needs Chromium for Playwright. It always
# sweeps in Chromium; the whole sweep runs in each engine on its own (--browser, as CI does). It reads
# no BROWSER variable, which many shells set to a web browser's command (D61).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
# shellcheck source=tests/controls.sh
. "$HERE/tests/controls.sh"
INPUTS=(scripts/sweep-side-by-side.py scripts/check-previews.py scripts/build-tokens.py tokens.json tokens.css components fonts)
WHAT=sweep
run() { # run <dir> [arguments...]: the sweep on the copy in <dir>
  local dir="$1"
  shift
  (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/sweep-side-by-side.py "$@") > "$dir/out.txt" 2>&1
}

pass=0
fail=0
# The rule's edges, both pointers: breakpoint-side-min (768px) and H (16.5rem, 264px) a few pixels either
# way, up to breakpoint-short, so the bars are measured on short and less short screens alike
EDGES="--widths 760-790 --heights 250-480"
echo "the sweep on the repository's files ($EDGES, a mouse and touch):"
copy "$tmp/base"
# shellcheck disable=SC2086  # the arguments are words
if run "$tmp/base" $EDGES; then
  printf '    ok    passes (%s)\n' "$(grep -E '^[0-9]+ screens' "$tmp/base/out.txt" | cut -d';' -f1)"
  pass=$((pass + 1))
  if grep -qE '^engine: chromium [0-9]' "$tmp/base/out.txt"; then
    printf '    ok    renders in %s\n' "$(grep -E '^engine: ' "$tmp/base/out.txt" | cut -d' ' -f2-)"
    pass=$((pass + 1))
  else
    printf '    FAIL  does not say it rendered in chromium\n'
    fail=$((fail + 1))
  fi
else
  printf '    FAIL  fails:\n'
  grep -E '^FAIL|Error' "$tmp/base/out.txt" | sed 's/^/          /' | head -20
  fail=$((fail + 1))
fi

B=components/bundle.css
S=scripts/sweep-side-by-side.py
# The side-by-side query and its least height H as the build has them, from the tokens (D75)
QUERY="$(query side-by-side)" || {
  echo "FAIL build-tokens.py --query side-by-side gives nothing"
  exit 1
}
H="$(query side-h)" || {
  echo "FAIL build-tokens.py --query side-h gives nothing"
  exit 1
}
EDGE="--widths 766-770 --heights 260-268 --pointers mouse"
echo "the controls, each a copy with one mistake that must be refused:"
# The bars: one row each, and one height on every screen (D75)
css "a plan bar of two rows" 'bars: side by side, the plan bar is not one row on [0-9]+ screens \(mouse\)' "$EDGE" \
  '.ws-plan{flex-wrap:wrap}.ws-plan__line{flex-basis:100%}'
css "a status bar of two rows" 'bars: side by side, the status bar is not one row on [0-9]+ screens \(mouse\)' "$EDGE" \
  '.ws-status{flex-direction:column;align-items:flex-start}'
css "a plan bar that grows with the screen's height" "bars: side by side, the plan bar is [0-9.]+px tall at [0-9]+ x [0-9]+ and [0-9.]+px at [0-9]+ x [0-9]+ \(mouse\), not one height" \
  "--widths 900-904 --heights 300-480 --pointers mouse" '.ws-plan{padding-bottom:10svh}'
# H: another than the build derives, typed in the stylesheet, and one that lets a screen under 40 % (D75)
sub "a typed H, 20rem" 'rule: [0-9]+ screens \(mouse\) stack where the rule puts them side by side, 768-[0-9]+ x 2[0-9]+-' \
  "--widths 766-770 --heights 260-330 --pointers mouse" $B "(min-height:$H)" '(min-height:20rem)'
sub "an H that lets a screen under 40 %, 15rem" 'view: [0-9]+ screens \(touch\), 768-[0-9]+ x 240-[0-9]+, go side by side, the view down to [0-9.]+ %' \
  "--widths 766-770 --heights 240-250 --pointers touch" $B "(min-height:$H)" '(min-height:15rem)'
# The edge screens in a window of their own size
sub "a window drawn taller than asked" 'side: at 768 x [0-9]+ \(mouse\) a window.s view is [0-9.]+px, the iframe.s [0-9.]+px' "$EDGE" \
  $S 'styled.set_viewport_size({"width": w, "height": h})' 'styled.set_viewport_size({"width": w, "height": h + 8})'
sub "nothing side by side" 'run: no screen in the sweep goes side by side, so it checked nothing' "$EDGE" \
  $B "$QUERY{" '(min-width:200rem){'
sub "--browser ignored, Chromium launched" 'setup: asked for webkit, but the page runs in .*Chrome/' "--browser webkit $EDGE" \
  $S 'getattr(pw, args.browser).launch()' 'pw.chromium.launch()'
sub "a touch phone without touch" 'setup: touch emulation is off, expected on' "--widths 768-770 --heights 262-266 --pointers touch" \
  $S 'has_touch=touch, is_mobile=touch' 'has_touch=False, is_mobile=False'
sub "an iframe a pixel taller than asked" 'setup: an iframe asked for [0-9]+ x [0-9]+ is [0-9]+ x [0-9]+' "$EDGE" \
  $S 'f.style.height = `${h}px`' 'f.style.height = `${h + 1}px`'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
