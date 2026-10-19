#!/usr/bin/env bash
# Hold scripts/sweep-side-by-side.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-sweep-side-by-side.sh
#
# Each control is a copy of the files the sweep reads (the two scripts, tokens.json, tokens.css,
# components/, fonts/) with one mistake put in, swept only over the screens where it shows, so the
# set runs in a minute or two. A control counts as refused only if the run fails AND its output
# names the expected check: a run that fails for another reason proves nothing. Needs Chromium for
# Playwright. It always sweeps in Chromium; the whole sweep runs in each engine on its own
# (--browser, as CI does). It reads no BROWSER variable, which many shells set to a web browser's
# command (D61).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
# shellcheck source=tests/controls.sh
. "$HERE/tests/controls.sh"
INPUTS=(scripts/sweep-side-by-side.py scripts/check-previews.py tokens.json tokens.css components fonts)
WHAT=sweep
run() { # run <dir> [arguments...]: the sweep on the copy in <dir>
  local dir="$1"
  shift
  (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/sweep-side-by-side.py "$@") > "$dir/out.txt" 2>&1
}

pass=0
fail=0
# The rule's edges, both pointers: the plan bar's extra row (877 to 900px), breakpoint-side-size-w
# and -h (904 x 408) and breakpoint-side-short (976px), every short height
EDGES="--widths 870-990 --heights 360-480"
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
# The side-by-side query and its size-only part as the build has them, from the tokens (D54)
QUERY="$(query side-by-side)" || {
  echo "FAIL build-tokens.py --query side-by-side gives nothing"
  exit 1
}
SIZE="$(query side-size)" || {
  echo "FAIL build-tokens.py --query side-size gives nothing"
  exit 1
}
EDGE="--widths 896-912 --heights 396-412 --pointers mouse"
echo "the controls, each a copy with one mistake that must be refused:"
# The two view controls go well past the rule's edges: there the views differ by platform (Linux's
# Chromium sets text narrower than Windows' engines and Linux's WebKit and Firefox, CI)
sub "a short screen side by side from 18rem tall" 'view: 904-[0-9]+ x 288-[0-9]+ \(mouse\) go side by side, the view down to [0-9.]+ %' \
  "--widths 904-912 --heights 288-300 --pointers mouse" $B "$SIZE" '(min-width:56.5rem) and (min-height:18rem)'
sub "a short screen side by side from 40rem wide" 'view: 640-[0-9]+ x 408-[0-9]+ \(mouse\) go side by side, the view down to [0-9.]+ %' \
  "--widths 640-648 --heights 408-412 --pointers mouse" $B "$SIZE" '(min-width:40rem) and (min-height:25.5rem)'
css "a plan bar that grows with the screen's height" "bars: side by side at [0-9]+ x [0-9]+ \(mouse\) the view is .* the bars change with the screen's height" \
  "--widths 904-908 --heights 360-480 --pointers mouse" '.ws-plan{padding-bottom:10svh}'
sub "the iframes holding another stylesheet" 'side: the iframe puts [0-9]+ x 396 \(mouse\) side by side, and a window that size stacks' "$EDGE" \
  $S 'frame_html = styled_html' 'frame_html = forced_html'
sub "nothing side by side" 'run: no screen in the sweep goes side by side, so it checked nothing' "$EDGE" \
  $B "$QUERY{" '(min-width:200rem){'
sub "--browser ignored, Chromium launched" 'setup: asked for webkit, but the page runs in .*Chrome/' "--browser webkit $EDGE" \
  $S 'getattr(pw, args.browser).launch()' 'pw.chromium.launch()'
sub "a touch phone without touch" 'setup: touch emulation is off, expected on' "--widths 904-906 --heights 406-410 --pointers touch" \
  $S 'has_touch=touch, is_mobile=touch' 'has_touch=False, is_mobile=False'
sub "an iframe a pixel taller than asked" 'setup: an iframe asked for [0-9]+ x [0-9]+ is [0-9]+ x [0-9]+' "$EDGE" \
  $S 'f.style.height = `${h}px`' 'f.style.height = `${h + 1}px`'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
