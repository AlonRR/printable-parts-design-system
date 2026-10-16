#!/usr/bin/env bash
# Hold scripts/check-previews.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-check-previews.sh
#
# Each control is a copy of the files the check reads (the script, tokens.json, tokens.css,
# components/, fonts/) with one mistake put in, rendered only where the mistake shows (--only,
# --device, --theme), so the whole set runs in minutes. A control counts as refused only if the run
# fails AND its output names the expected check: a run that fails for another reason proves nothing.
# Needs Chromium for Playwright, as the check does.
#
#   ONLY='header' bash tests/test-check-previews.sh   # while working: only the controls whose label
#                                                     # has this text, and no base run; never a result
set -uo pipefail
ONLY="${ONLY:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

copy() { # copy <dir>: the check's inputs, as they are in the working tree
  mkdir -p "$1/scripts"
  cp "$HERE/scripts/check-previews.py" "$1/scripts/"
  cp "$HERE/tokens.json" "$HERE/tokens.css" "$1/"
  cp -r "$HERE/components" "$HERE/fonts" "$1/"
}
check() { # check <dir> [filters...]
  local dir="$1"
  shift
  (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/check-previews.py --out "$dir/shots" "$@") > "$dir/out.txt" 2>&1
}

pass=0
fail=0
echo "the check on the repository's files (every preview and device, the light theme):"
copy "$tmp/base"
if [ -n "$ONLY" ]; then
  printf '    --    not run: ONLY is set, so this is no result\n'
elif check "$tmp/base" --theme light; then
  printf '    ok    passes (%s)\n' "$(grep -E '^[0-9]+ pages' "$tmp/base/out.txt" | cut -d';' -f1)"
  pass=$((pass + 1))
else
  printf '    FAIL  fails:\n'
  grep -E '^FAIL|Error' "$tmp/base/out.txt" | sed 's/^/          /' | head -20
  fail=$((fail + 1))
fi

controls=0
refused=0
judge() { # judge <dir> <label> <pattern> [filters...]: run the check on the mutated copy
  local dir="$1" label="$2" pattern="$3"
  shift 3
  if check "$dir" "$@"; then
    printf '    FAIL  control "%s": the check passed it\n' "$label"
  elif grep -qE -- "$pattern" "$dir/out.txt"; then
    printf '    ok    control "%s": refused\n' "$label"
    refused=$((refused + 1))
  else
    printf '    FAIL  control "%s": failed, but not with /%s/:\n' "$label" "$pattern"
    grep -E '^FAIL|Error' "$dir/out.txt" | sed 's/^/          /' | head -5
  fi
}
wanted() { [ -z "$ONLY" ] || [[ "$1" == *"$ONLY"* ]]; }
css() { # css <label> <pattern> <filters> <css>: a rule added at the end of bundle.css
  wanted "$1" || return 0
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  printf '%s\n' "$4" >> "$dir/components/bundle.css"
  # shellcheck disable=SC2086  # the filters are words
  judge "$dir" "$1" "$2" $3
}
sub() { # sub <label> <pattern> <filters> <file> <old> <new>: one text replaced in a copied file
  wanted "$1" || return 0
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  if ! python3 -I - "$dir/$4" "$5" "$6" << 'EOF'; then
import sys
path, old, new = sys.argv[1:]
text = open(path, encoding="utf-8", newline="").read()
if old not in text:
    sys.exit(1)
open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new))
EOF
    printf '    FAIL  control "%s": its text is not in %s; the control no longer tests anything\n' "$1" "$4"
    return
  fi
  # shellcheck disable=SC2086
  judge "$dir" "$1" "$2" $3
}
gone() { # gone <label> <pattern> <filters> <file>: a copied file deleted
  wanted "$1" || return 0
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  rm "$dir/$4"
  # shellcheck disable=SC2086
  judge "$dir" "$1" "$2" $3
}

P="--theme light --device phone"
D="--theme light --device desktop"
echo "the controls, each a copy with one mistake that must be refused:"
css "code in the browser's monospace" 'fonts: <code>' "--only Dialog $D" 'code{font-family:monospace}'
sub "a broken font query" 'getPlatformFontsForNodes' "--only Button $D" scripts/check-previews.py \
  '"CSS.getPlatformFontsForNode"' '"CSS.getPlatformFontsForNodes"'
css "a group wider than the phone" 'overflow:' "--only Fieldset $P" '.ws-fieldset{min-width:var(--measure)}'
css "the chosen Choice without its ring" "choice: 'None' \(chosen\)" "--only Choice $D" \
  '.ws-choice__input:checked + .ws-choice__face{outline:0}'
css "a selected tile filled with action" 'choice: .*filled with action' "--only Gallery $D" \
  '.ws-tile[aria-pressed=true]{background:var(--action)}'
css "the Sides tick off its box" 'marks: the tick' "--only Sides $D" \
  '.ws-sides__btn[aria-pressed="true"]::after{margin-left:var(--space-3)}'
css "a label pushed off centre" 'centring: ws-btn' "--only Button $D" '.ws-btn{padding-top:var(--space-2)}'
css "a step button under control-h" 'height: ws-rail__btn' "--only Workbench $P" '.ws-rail__btn{height:var(--space-6)}'
sub "an icon read aloud" 'names: icon glyph' "--only Header $D" components/Header/preview.html \
  '<span class="ws-ic" aria-hidden="true">&#xeae2;</span>' '<span class="ws-ic">&#xeae2;</span>'
css "a canvas laid out in the page" 'stage: a canvas' "--only Workbench $D" \
  '.ws-stage__view > :is(canvas,svg){position:static}'
css "the view's ring drawn outside it" 'no action ring inside' "--only Workbench $D" \
  '.ws-stage__view > :is(canvas,svg):focus-visible{outline-offset:var(--ring)}'
css "the View... menu not under its button" 'stage: the View… menu' "--only Workbench $P" \
  '@supports (position-area:block-end){.ws-stage__menu:popover-open{position-area:center}}'
sub "the dark theme in a light color-scheme" 'scheme:' "--only Button --theme dark --device desktop" tokens.css \
  'color-scheme: dark;' 'color-scheme: light;'
css "both hints on show" 'hints:' "--only Workbench $D" '.ws-hint-touch{display:inline}'
css "a warning headline in ink" "notice: the warning Notice's headline" "--only Notice $D" \
  '.ws-notice--warning strong{color:var(--ink)}'
css "an empty Notice taking room" 'notice: an empty Notice takes room' "--only Notice $D" \
  '.ws-notice:empty{padding:var(--space-3)}'
sub "a plan line nobody hears" 'live: ws-plan__line' "--only Workbench $D" components/Workbench/preview.html \
  'id="ws-plan-line" aria-live="polite"' 'id="ws-plan-line"'
css "a squeezed plan sentence" 'plan: the sentence' "--only Workbench $D" '.ws-plan__line{max-width:var(--space-6)}'
css "ligatures in a field" 'data: input.ws-input' "--only Field $D" '.ws-input{font-feature-settings:normal}'
sub "a step with no name" 'rail: step button' "--only Workbench $D" components/Workbench/preview.html \
  '<span class="ws-rail__num">2</span>Window' '<span class="ws-rail__num">2</span>'
css "a 3D view under 40 % of a phone" 'under 40 %' "--only Workbench $P" \
  '.ws-workbench{grid-template-rows:var(--header-h) var(--space-6) auto auto 1fr}'
css "a focused field under the pinned stage" "view: '.*' is (under|off)" "--only Workbench $P" \
  ':root:has(.ws-workbench){scroll-padding-top:0}'
sub "two primary buttons" 'primary: 2 primary' "--only Button $D" components/Button/preview.html \
  '<button class="ws-btn" type="button">Add another port' '<button class="ws-btn ws-btn--primary" type="button">Add another port'
sub "a size field with a text keyboard" "units: 'Opening width \(mm\)'" "--only Field $D" components/Field/preview.html \
  'Opening width (mm)<input class="ws-input" inputmode="decimal"' 'Opening width (mm)<input class="ws-input"'
sub "a preview that styles itself" 'markup: an inline style sets margin' "--only Choice $D" components/Choice/preview.html \
  '<div class="ws-choice" role="radiogroup" aria-label="Seal">' '<div class="ws-choice" style="margin:0" role="radiogroup" aria-label="Seal">'
gone "a component without its README" 'Notice: markup: no README.md' "--only Notice $D" components/Notice/README.md
sub "a misspelt selector in the check" 'looks for .ws-sides__bt,' "--only Sides $D" scripts/check-previews.py \
  '.ws-sides__btn, .ws-rail__btn, .ws-piece"' '.ws-sides__bt, .ws-rail__btn, .ws-piece"'
sub "a header that has to scroll" 'the header scrolls sideways' "--only Header $P" components/Header/preview.html \
  '<button class="ws-btn ws-header__more"' '<button class="ws-btn" type="button">Save project</button><button class="ws-btn" type="button">Load project</button><button class="ws-btn ws-header__more"'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ -z "$ONLY" ] && [ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
