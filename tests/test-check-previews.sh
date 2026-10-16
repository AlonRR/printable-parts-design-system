#!/usr/bin/env bash
# Hold scripts/check-previews.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-check-previews.sh
#
# Each control is a copy of the files the check reads (the script, tokens.json, tokens.css, the docs,
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
  cp "$HERE/tokens.json" "$HERE/tokens.css" "$HERE/README.md" "$HERE/DESIGN.md" "$1/"
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
gone() { # gone <label> <pattern> <filters> <path>: a copied file or folder deleted
  wanted "$1" || return 0
  local dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
  rm -r "${dir:?}/$4"
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

css "a button with no focus ring" 'states: button.ws-btn .*focused, has no action ring' "--only Button $D" '.ws-btn:focus-visible{outline:0}'
sub "a ring token of 0px" 'has no action ring 2px or wider' "--only Button $D" tokens.css '--ring: 2px;' '--ring: 0px;'
css "a header that clips its rings" 'focus ring of .* is cut off .* by header.ws-header' "--only Header $P" '.ws-header{overflow-x:auto}'
css "the actions scrolling inside the header" 'ws-header__actions scrolls sideways inside itself' "--only Header --theme light --device breakpoint" \
  '@media (min-width:56rem){.ws-header__actions,.ws-header__actions:not(:popover-open){flex:1 1 0;overflow:auto}}'
css "a pressed tile not tinted" 'states: button.ws-tile .* is selected but has no tint' "--only Gallery $D" \
  '.ws-tile[aria-pressed=true]{background:var(--surface-raised)}'
css "a pressed Sides toggle not bold" 'states: button.ws-sides__btn .* is selected but has no bold label' "--only Sides $D" \
  '.ws-sides__btn[aria-pressed="true"]{font-weight:var(--weight-regular)}'
css "the current step not ringed" 'states: button.ws-rail__btn .* is selected but has no ring' "--only Workbench $D" \
  '.ws-rail__btn[aria-current=step]{outline:0}'
css "an invalid field not marked" 'states: the invalid field' "--only Field $D" \
  '.ws-input[aria-invalid=true]{border-color:var(--border-strong);outline:0}'
css "a disabled field not faded" 'states: input.ws-input .* is disabled but not faded' "--only Field $D" '.ws-input:disabled{opacity:1}'
css "a disabled button that tints on hover" 'states: button.ws-btn .* is disabled but changes on hover' "--only Button $D" \
  '.ws-btn:hover{background:var(--action-tint)}'
css "a tile with no hover" 'states: button.ws-tile .* does not change on hover' "--only Gallery $D" \
  '.ws-tile:hover:not(:disabled){background:var(--surface-raised)}'
css "an error message in ink-muted" "states: the error 'Enter a number" "--only Field $D" '.ws-error{color:var(--ink-muted)}'
css "the header's actions hidden on a wide screen" 'header: on a wide screen .* are not on show' "--only Header $D" \
  '@media (min-width:56rem){.ws-header__actions,.ws-header__actions:not(:popover-open){display:none}}'
css "the More... menu off the screen" 'header: the More… menu, at .* runs off the screen' "--only Header $P" \
  '.ws-header__actions:popover-open{inset:var(--header-h) auto auto var(--measure)}'
sub "a popovertarget typo" 'aria: .* opens #ws-mroe, which is no popover' "--only Header $P" components/Header/preview.html \
  'popovertarget="ws-more"' 'popovertarget="ws-mroe"'
css "the phone view unpinned" 'pinned: scrolled down, the 3D view' "--only Workbench $P" '.ws-stage__view{position:relative}'
css "the plan bar unpinned" 'pinned: scrolled down, the plan bar' "--only Workbench $P" '.ws-plan{position:static}'
sub "a tap token of 30px" 'height: control-h is 30.00px on a touch screen' "--only Button $P" tokens.css '--tap: 2.75rem;' '--tap: 1.875rem;'
css "a tile shorter than control-h" 'height: ws-tile' "--only Gallery $P" '.ws-tile svg{display:none}'
css "a one-line Choice face too tall" "height: ws-choice__face 'None' is 48.00px" "--only Choice $P" \
  '.ws-choice__face{min-height:calc(var(--control-h) + var(--space-1))}'
sub "tiles without aria-pressed" 'aria: ws-tile .* has no aria-pressed' "--only Gallery $D" components/Gallery/preview.html \
  ' aria-pressed="false"' ''
css "a note in border-strong" "text: 'Set by the opening width.* needs 4.5:1" "--only Field $D" '.ws-note{color:var(--border-strong)}'
css "a faint colour mixed in the stylesheet" "text: '.*' is [0-9.]+:1, .*needs 4.5:1" "--only Field $D" \
  '.ws-note{color:color-mix(in srgb, var(--ink-muted) 40%, var(--surface))}'
css "a colour the check cannot read" "text: the colours of .* cannot be read" "--only Field $D" '.ws-note{color:oklch(50% 0.1 250)}'
css "hovered text losing its contrast" "text: hovered, 'Add another port' is" "--only Button $D" \
  '.ws-btn:hover:not(:disabled){background:var(--ink-muted)}'
sub "a dropped preview variant" 'coverage: bundle.css styles .ws-notice--error, which no preview shows' "--only Button $D" components/Notice/preview.html '<div class="ws-notice ws-notice--error"><strong>Error: depth is larger than the opening</strong>Fix the marked fields to see the plan.</div>' ''
gone "a deleted component" 'coverage: bundle.css styles .ws-map, which no preview shows' "--only Button $D" components/PieceMap
sub "a README naming a class the system lacks" 'coverage: components/Button/README.md names .ws-btn--ghost' "--only Button $D" components/Button/README.md '`.ws-btn--quiet` has neither' '`.ws-btn--ghost` has neither'
css "a class no doc names" 'coverage: bundle.css styles .ws-extra, which no doc names' "--only Button $D" '.ws-extra{display:block}'
css "a chosen radio that loses its dot in forced colours" 'forced: the chosen and the unchosen options .* have the same mark' "--only Choice --device forced" '@media (forced-colors:active){.ws-choice__input:checked + .ws-choice__face::before{background:Canvas}}'
css "a done step like one not reached in forced colours" 'forced: the done step and the step not reached' "--only Workbench --device forced" '@media (forced-colors:active){.ws-rail__btn:not([data-done=yes]):not([aria-current=step]){border-color:CanvasText}}'
sub "a Choice that is no radiogroup" 'aria: the Choice .* is not a named radiogroup' "--only Choice $D" components/Choice/preview.html \
  '<div class="ws-choice" role="radiogroup" aria-label="Seal">' '<div class="ws-choice" aria-label="Seal">'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ -z "$ONLY" ] && [ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
