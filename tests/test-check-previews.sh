#!/usr/bin/env bash
# Hold scripts/check-previews.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-check-previews.sh
#
# Each control is a copy of the files the check reads (the script, tokens.json, tokens.css, the docs,
# theme-init.js, components/, fonts/) with one mistake put in, rendered only where the mistake shows
# (--only, --device, --theme), so the whole set runs in minutes. A control counts as refused only if the run
# fails AND its output names the expected check: a run that fails for another reason proves nothing.
# Needs Chromium for Playwright, as the check does. CI runs it in Chromium only: the font and hover
# checks read through CDP, which only Chromium has, so their controls can be refused only there.
#
#   BROWSER=webkit ONLY='pinned' bash tests/test-check-previews.sh   # the controls in another engine
#                                                     # (--browser); never a result either
#
#   ONLY='header' bash tests/test-check-previews.sh   # while working: only the controls whose label
#                                                     # has this text, and no base run; never a result
set -uo pipefail
ONLY="${ONLY:-}"
BROWSER="${BROWSER:-chromium}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

copy() { # copy <dir>: the check's inputs, as they are in the working tree
  mkdir -p "$1/scripts"
  cp "$HERE/scripts/check-previews.py" "$1/scripts/"
  cp "$HERE/tokens.json" "$HERE/tokens.css" "$HERE/README.md" "$HERE/DESIGN.md" "$HERE/theme-init.js" "$1/"
  cp -r "$HERE/components" "$HERE/fonts" "$1/"
}
check() { # check <dir> [filters...]
  local dir="$1"
  shift
  (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/check-previews.py --browser "$BROWSER" --out "$dir/shots" "$@") > "$dir/out.txt" 2>&1
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
  # The run names the engine it rendered in: the one --browser asked for (D40)
  if grep -qE "^engine: $BROWSER [0-9]" "$tmp/base/out.txt"; then
    printf '    ok    renders in %s\n' "$(grep -E '^engine: ' "$tmp/base/out.txt" | cut -d' ' -f2-)"
    pass=$((pass + 1))
  else
    printf '    FAIL  does not say it rendered in %s\n' "$BROWSER"
    fail=$((fail + 1))
  fi
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
# --browser that never reaches the launch: the run renders in Chromium, whatever it asked for (D40)
sub "--browser ignored, Chromium launched" 'setup: asked for webkit, but the page runs in .*Chrome/' "--browser webkit --only Button $D" \
  scripts/check-previews.py 'getattr(pw, engine).launch()' 'pw.chromium.launch()'
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
css "the View... menu over the view, under its button" 'stage: the open View… menu, at .* covers [0-9]+ % of the view' \
  "--only Workbench $P" '.ws-stage__more{anchor-name:--under-view-btn}.ws-stage__menu:popover-open{position-anchor:--under-view-btn}'
css "the View... menu above the view" 'stage: the open View… menu, at .* is not below the view' "--only Workbench $P" \
  '@supports (position-area:block-end){.ws-stage__menu:popover-open{position-area:block-start span-inline-start}}'
css "the View... menu out of the view's column" "stage: the open View… menu, at .* leaves the view's column" \
  "--only Workbench --theme light --device side-short" '.ws-stage__menu:popover-open{translate:var(--panel-width) 0}'
sub "View... left open when a view is picked" "close: picking '[A-Za-z]+' leaves the View… menu open" "--only Workbench $P" \
  components/Workbench/README.md 'menu.hidePopover();' 'void menu;'
sub "no lines for closing View..." 'Workbench: close: its README gives no lines' "--only Workbench $P" \
  components/Workbench/README.md '```js' '```text'
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
css "the full label beside a phone's plan sentence" 'plan: the plan sentence is [0-9]+px wide on a 375px screen, under plan-line-min' \
  "--only Workbench $P" '.ws-plan__long{position:static;width:auto;height:auto;overflow:visible;clip-path:none}'
css "the short label's rest hidden from screen readers" "names: part of the label of 'Download.*', 'the pieces', is display:none" \
  "--only Workbench $P" '.ws-plan__long{display:none}'
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
css "the actions scrolling inside the header" 'ws-header__actions scrolls sideways inside itself' "--only Header --theme light --device header" \
  '@media (min-width:64rem){.ws-header__actions,.ws-header__actions:not(:popover-open){flex:1 1 0;overflow:auto}}'
css "a pressed tile not tinted" 'states: button.ws-tile .* is selected but has no tint' "--only Gallery $D" \
  '.ws-tile[aria-pressed=true]{background:var(--surface-raised)}'
css "a pressed Sides toggle not bold" 'states: button.ws-sides__btn .* is selected but has no bold label' "--only Sides $D" \
  '.ws-sides__btn[aria-pressed="true"]{font-weight:var(--weight-regular)}'
css "the current step not ringed" 'states: button.ws-rail__btn .* is selected but has no ring' "--only Workbench $D" \
  '.ws-rail__btn[aria-current=step]{outline:0}'
css "a selected piece without its mark" 'states: button.ws-piece .* is selected but has no mark' "--only PieceMap $D" \
  '.ws-piece[aria-pressed=true]::before{content:none}'
css "a mark on a piece not selected" 'states: button.ws-piece .* has a mark but is not selected' "--only PieceMap $D" \
  '.ws-piece[aria-pressed=false]::before{content:"x"}'
css "an invalid field not marked" 'states: the invalid field' "--only Field $D" \
  '.ws-input[aria-invalid=true]{border-color:var(--border-strong);outline:0}'
css "a disabled field not faded" 'states: input.ws-input .* is disabled but not faded' "--only Field $D" '.ws-input:disabled{opacity:1}'
css "a disabled button that tints on hover" 'states: button.ws-btn .* is disabled but changes on hover' "--only Button $D" \
  '.ws-btn:hover{background:var(--action-tint)}'
css "a tile with no hover" 'states: button.ws-tile .* does not change on hover' "--only Gallery $D" \
  '.ws-tile:hover:not(:disabled){background:var(--surface-raised)}'
css "an error message in ink-muted" "states: the error 'Enter a number" "--only Field $D" '.ws-error{color:var(--ink-muted)}'
css "the header's actions hidden on a wide screen" 'header: on a wide screen .* are not on show' "--only Header --theme light --device header" \
  '@media (min-width:64rem){.ws-header__actions,.ws-header__actions:not(:popover-open){display:none}}'
css "the header's actions in its row below breakpoint-header" "header: below breakpoint-header the header's actions crowd the row" "--only Header --theme light --device breakpoint" \
  '@media (min-width:56rem){.ws-header__actions:not(:popover-open){display:flex}}'
css "the tool's name cut on a wide screen" "header: the tool's name shows [0-9]+ of its [0-9]+px; from breakpoint-wide up it is whole" "--only Header --theme light --device breakpoint" \
  '.ws-header__name{max-width:var(--space-6)}'
css "the version in a phone's header row" "header: below breakpoint-header the version tag 'v[0-9.]+' is in the header's row" "--only Header $P" \
  '.ws-header:has(.ws-header__more) > .ws-header__version{display:inline}'
sub "no version in the More... menu" 'header: the open More… menu leaves 0 version tags on show' "--only Header $P" components/Header/preview.html \
  '<span class="ws-header__version">v0.3.0</span></div></header>' '</div></header>'
css "two versions on a wide screen" 'header: on a wide screen 2 version tags are on show' "--only Header --theme light --device header" \
  '@media (min-width:64rem){.ws-header__actions > .ws-header__version{display:inline}}'
css "the More... menu off the screen" 'header: the More… menu, at .* runs off the screen' "--only Header $P" \
  '.ws-header__actions:popover-open{inset:var(--header-h) auto auto var(--measure)}'
sub "a popovertarget typo" 'aria: .* opens #ws-mroe, which is no popover' "--only Header $P" components/Header/preview.html \
  'popovertarget="ws-more"' 'popovertarget="ws-mroe"'
css "the phone view unpinned" 'pinned: scrolled down, the 3D view' "--only Workbench $P" '.ws-stage__view{position:relative}'
css "the plan bar unpinned" 'pinned: scrolled down, the plan bar' "--only Workbench $P" '.ws-plan{position:static}'
css "a stacked landscape screen pinning the view" 'pinned: scrolled down on a short or landscape screen, the 3D view is at .*: it is pinned' \
  "--only Workbench --theme light --device landscape-tall" '@media (min-aspect-ratio:4/3){.ws-stage__view{position:sticky}}'
sub "side by side on a narrow landscape screen" 'stage: the 3D view is [0-9]+px tall, under 40 % of a 360px screen' \
  "--only Workbench --theme light --device landscape-740" components/bundle.css '(min-aspect-ratio:4/3) and (min-width:48rem) and (min-height:30rem){' '(min-aspect-ratio:4/3){'
sub "side by side on a short screen under breakpoint-side-short" 'stage: the 3D view is [0-9]+px tall, under 40 % of a 360px screen' \
  "--only Workbench --theme light --device landscape-800" components/bundle.css \
  '(min-width:61rem),(min-width:56.5rem) and (min-height:25.5rem),(min-width:56rem) and (min-height:30rem),(min-aspect-ratio:4/3) and (min-width:48rem) and (min-height:30rem){' \
  '(min-width:56rem),(min-aspect-ratio:4/3) and (min-width:48rem){'
# The size-only way side by side for a short screen (D54), breakpoint-side-size-w by -h: its edges, and
# the phones held sideways it decides, one each way
SIZE='(min-width:56.5rem) and (min-height:25.5rem)'
sub "932 x 430 stacked, as before D54" 'layout: the sidebar is under the stage on a 932 x 430 screen, where it goes beside the stage' \
  "--only Workbench --theme light --device landscape-wide" components/bundle.css ",$SIZE" ''
sub "844 x 390 side by side, its view still 41 %" 'layout: the sidebar is beside the stage on a 844 x 390 screen, where it goes under the stage' \
  "--only Workbench --theme light --device landscape" components/bundle.css "$SIZE" '(min-width:52rem) and (min-height:24rem)'
# The two edge windows stack by the layout check: their views side by side are under 40 % in Windows'
# engines and Linux's WebKit and Firefox, but not in Linux's Chromium, whose text sets narrower (CI)
sub "side by side 4px under breakpoint-side-size-w" 'layout: the sidebar is beside the stage on a 900 x 408 screen, where it goes under the stage' \
  "--only Workbench --theme light --device side-size-narrow" components/bundle.css "$SIZE" '(min-width:56rem) and (min-height:25.5rem)'
sub "side by side half a rem under breakpoint-side-size-h" 'layout: the sidebar is beside the stage on a 904 x 400 screen, where it goes under the stage' \
  "--only Workbench --theme light --device side-size-low" components/bundle.css "$SIZE" '(min-width:56.5rem) and (min-height:25rem)'
sub "a screen with no place for the sidebar" 'layout: the screen side-size-low has no place for the sidebar' "--only Button $D" \
  scripts/check-previews.py ', "side-size-low": False}' '}'
css "the More... menu taller than a 320 x 180 screen" 'header: the More… menu, at .* runs off the screen' \
  "--only Header --theme light --device zoomed-16x9" '.ws-header__actions:popover-open{max-height:none}'
css "the View... menu taller than a 320 x 180 screen" 'stage: the View… menu, at .* runs off the screen' \
  "--only Workbench --theme light --device zoomed-16x9" '.ws-stage__menu:popover-open{max-height:none}'
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
css "a selected piece that loses its mark in forced colours" 'forced: the pressed and the unpressed .* have the same mark' "--only PieceMap --device forced" '@media (forced-colors:active){.ws-piece[aria-pressed=true]::before{content:none}}'
css "a dialog to the screen's edge" "dialog: the open dialog, at .* runs to the screen's edge" "--only Dialog $P" '.ws-dialog{box-sizing:content-box}'
css "the browser's own backdrop" 'dialog: the backdrop behind the open dialog' "--only Dialog $D" '.ws-dialog::backdrop{background:transparent}'
css "a group keeping a bottom margin" 'rhythm: the note .* under its ws-gallery' "--only Gallery $D" '.ws-gallery{margin-bottom:var(--space-2)}'
css "a first item adding its margin under the legend" 'rhythm: .* under the legend' "--only Fieldset $D" '.ws-fieldset > legend + *{margin-top:var(--space-1)}'
sub "a Choice that is no radiogroup" 'aria: the Choice .* is not a named radiogroup' "--only Choice $D" components/Choice/preview.html \
  '<div class="ws-choice" role="radiogroup" aria-label="Seal">' '<div class="ws-choice" aria-label="Seal">'
# The hidden attribute always hides (D57): the rule left out, a Choice stays on show; and
# without !important, a rule as specific and later in the file wins, the wide View… menu's display:contents
HIDDEN='[hidden]:not([hidden=until-found i]){display:none !important}'
sub "a hidden Choice still drawn" 'hidden: div\.ws-choice is still drawn with the hidden attribute \(display flex\)' "--only Choice $D" \
  components/bundle.css "$HIDDEN" ''
sub "the hidden rule without !important" 'hidden: div\.ws-stage__menu is still drawn with the hidden attribute \(display contents\)' "--only Workbench $D" \
  components/bundle.css "$HIDDEN" '[hidden]:not([hidden=until-found i]){display:none}'
# theme-init.js (D58), each case of the check failing with its own message; the check runs alone
T="--device theme"
SET="  document.documentElement.dataset.theme = chosen === 'light' || chosen === 'dark' ? chosen : system;"
sub "a stored dark ignored" 'theme: stored dark: data-theme is "light" when theme-init.js has run' "$T" \
  theme-init.js "chosen === 'light' || chosen === 'dark' ?" "chosen === 'light' ?"
sub "a stored light ignored" 'theme: stored light: data-theme is "dark" when theme-init.js has run' "$T" \
  theme-init.js "chosen === 'light' || chosen === 'dark' ?" "chosen === 'dark' ?"
sub "the system's setting ignored" 'theme: nothing stored, a dark system: data-theme is "light" when' "$T" \
  theme-init.js "matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'" "'light'"
sub "data-theme left unset with nothing stored" 'theme: nothing stored, a dark system: data-theme is unset when theme-init.js has run, before' "$T" \
  theme-init.js "$SET" "  if (chosen === 'light' || chosen === 'dark') document.documentElement.dataset.theme = chosen;"
sub "a value it does not know kept" 'theme: a value it does not know stored: data-theme is "blue"' "$T" \
  theme-init.js "chosen === 'light' || chosen === 'dark' ? chosen : system" 'chosen || system'
sub "storage refused, and the setter throws" 'theme: storage refused, a dark system: theme-init.js threw' "$T" \
  theme-init.js '  } catch {' '  } catch (e) { throw e; } finally {'
sub "the theme set after the first paint" 'theme: stored dark: data-theme is unset when theme-init.js has run and "dark" only later, after the first paint' "$T" \
  theme-init.js "$SET" "  addEventListener('DOMContentLoaded', () => { $SET });"
sub "data-key ignored" 'theme: stored dark under the tool.s own key: data-theme is "light"' "$T" \
  theme-init.js "(document.currentScript && document.currentScript.dataset.key) || 'printable-parts-theme'" "'printable-parts-theme'"
gone "no theme-init.js" 'theme-init.js: theme: no theme-init.js' "$T" theme-init.js
# The Stepper (D56): what it is made of and where its buttons sit (check 33), then the README's lines for a
# tool's script, each way they can go wrong (check 34), the lines run on the preview as a tool runs them
R=components/Stepper/README.md
S=components/Stepper/preview.html
sub "a Stepper's lines missing" 'Stepper: step: its README gives no lines' "--only Stepper $D" "$R" '```js' '```text'
sub "a Stepper's lines that throw" "step: the Stepper README's lines fail" "--only Stepper $D" "$R" 'const by = Number(step)' 'const by = Number(stepp)'
sub "a press that moves two steps" "step: '↑' in '.*' moves .* not to .*, a step of" "--only Stepper $D" "$R" ': from + sign * by;' ': from + 2 * sign * by;'
sub "ArrowUp and ArrowDown that do nothing" "step: ArrowUp in 'Width \(mm\)' moves 600 to 600, not to 640" "--only Stepper $D" "$R" \
  "if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;" 'return;'
sub "a number field's own step as well" "step: ArrowUp in '.*' as a type=number field moves" "--only Stepper $D" "$R" 'e.preventDefault();' ''
sub "no stop at a limit" "step: '↑' in '.*' goes past its limit" "--only Stepper $D" "$R" \
  'String(Number(Math.min(high, Math.max(low, next)).toFixed(places)))' 'String(Number(next.toFixed(places)))'
sub "a button at its limit that does not say so" "step: at its max, .*, '↑' in '.*' does not say so" "--only Stepper $D" "$R" \
  "up.setAttribute('aria-disabled', String(value >= high));" "up.setAttribute('aria-disabled', 'false');"
sub "a button that says it is at a limit away from it" "step: '↓' in 'Width \(mm\)' says it is at a limit \(aria-disabled\) at" "--only Stepper $D" "$R" \
  "down.setAttribute('aria-disabled', String(value <= low));" "down.setAttribute('aria-disabled', 'true');"
sub "no way below zero" "step: '↓' in 'Slot clearance \(mm\)' from 0 gives 0; a value below zero" "--only Stepper $D" "$R" \
  'Math.max(low, next)' 'Math.max(low, 0, next)'
sub "a setting's steps ignored" "step: '↑' in 'Width \(mm\)' moves 620 to 660, not onto its steps" "--only Stepper $D" "$R" \
  "'onStep' in field.dataset" "'onstep' in field.dataset"
sub "a decimal comma not read" "step: '↑' in '.*' moves '0,25', a decimal comma" "--only Stepper $D" "$R" \
  "field.value.trim().replace(',', '.')" 'field.value.trim()'
sub "a press with no input event" 'step: .* fires 0 input events; one per change' "--only Stepper $D" "$R" \
  "field.dispatchEvent(new Event('input', { bubbles: true }));" ''
sub "an input event at a limit" 'step: .* fires 1 input events; none at a limit' "--only Stepper $D" "$R" \
  'if (sign > 0 ? from >= high : from <= low) return;' "if (sign > 0 ? from >= high : from <= low) return void field.dispatchEvent(new Event('input', { bubbles: true }));"
css "a number field's spin buttons kept" "step: a type=number field in '.*' keeps the browser's spin buttons" "--only Stepper $D" \
  '.ws-stepper > .ws-input[type=number]{appearance:auto}'
css "Stepper buttons under the touch size" "stepper: '↓' in '.*' is [0-9.]+px wide, under control-h" "--only Stepper $P" '.ws-stepper__btn{min-width:0}'
css "Stepper buttons not lined up with the field" "stepper: '↑' in '.*', at .* does not line up beside its field" "--only Stepper $D" \
  '.ws-stepper{align-items:center}'
css "a Stepper wider than a narrow sidebar" 'overflow: div.ws-stepper is [0-9]+px wide, its content [0-9]+px' \
  "--only Workbench --theme light --device zoomed" '.ws-stepper > .ws-input{flex:none}'
css "a Stepper keeping a bottom margin" 'rhythm: the note .* under its ws-stepper' "--only Stepper $D" '.ws-stepper{margin-bottom:var(--space-2)}'
css "a button at a limit that tints on hover" "states: button.ws-btn '↓' is disabled but changes on hover" "--only Stepper $D" \
  '.ws-btn[aria-disabled=true]:hover{background:var(--action-tint)}'
css "a button at a limit not faded" "states: button.ws-btn '↓' is disabled but not faded" "--only Stepper $D" '.ws-btn[aria-disabled=true]{opacity:1}'
sub "a Stepper's buttons inside its label" 'stepper: the buttons of .* are inside its label' "--only Stepper $D" "$S" \
  'for="st-radius">Corner radius (mm)</label>' 'for="st-radius">Corner radius (mm)'
sub "a Stepper with no step" "stepper: the field of 'Corner radius \(mm\)' has no data-step" "--only Stepper $D" "$S" ' data-step="0.5"' ''
sub "a Stepper button named for nothing" "stepper: '↑' in 'Corner radius \(mm\)' is named 'Up'" "--only Stepper $D" "$S" \
  'aria-label="Larger corner radius"' 'aria-label="Up"'
sub "a Stepper button that is no arrow" "stepper: the larger button of 'Width \(mm\)' reads '\+.*', not ↑" "--only Stepper $D" "$S" \
  'aria-label="Larger width">' 'aria-label="Larger width">+'
sub "a Stepper field with a text keyboard" "stepper: the field of 'Corner radius \(mm\)' is not inputmode" "--only Stepper $D" "$S" \
  'id="st-radius" inputmode="decimal"' 'id="st-radius"'
sub "a Stepper field's unit read from its label" "units: 'Corner radius \(mm\)' gets a text keyboard" "--only Stepper $D" "$S" \
  'id="st-radius" inputmode="decimal"' 'id="st-radius"'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ -z "$ONLY" ] && [ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
