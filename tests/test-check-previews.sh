#!/usr/bin/env bash
# Hold scripts/check-previews.py to its own claims: on the repository's files it passes, and each
# mistake it says it catches makes it fail, with that check's own message.
#
#   bash tests/test-check-previews.sh
#
# Each control is a copy of the files the check reads (the script, build-tokens.py, from which it reads
# H, tokens.json, tokens.css, the docs, theme-init.js, components/, fonts/) with one mistake put in, rendered only where the mistake shows
# (--only, --device, --theme), so the whole set runs in minutes. A control counts as refused only if the run
# fails AND its output names the expected check: a run that fails for another reason proves nothing.
# Needs Chromium for Playwright, as the check does. CI runs it in Chromium only: the font and hover
# checks read through CDP, which only Chromium has, so their controls can be refused only there.
# The engine is PREVIEW_ENGINE's, never BROWSER's, which many tools read as a web browser's command (D61).
#
#   PREVIEW_ENGINE=webkit ONLY='pinned' bash tests/test-check-previews.sh   # the controls in another
#                                                     # engine (--browser); never a result either
#
#   ONLY='header' bash tests/test-check-previews.sh   # while working: only the controls whose label
#                                                     # has this text, and no base run; never a result
#
#   PREVIEWS_CHECKED=1 bash tests/test-check-previews.sh   # right after the full check passed on these
#                                                     # files (the gate, CI's Chromium job): the base
#                                                     # run, a part of that one, is left out
set -uo pipefail
ONLY="${ONLY:-}"
ENGINE="${PREVIEW_ENGINE:-chromium}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
# shellcheck source=tests/controls.sh
. "$HERE/tests/controls.sh"
INPUTS=(scripts/check-previews.py scripts/build-tokens.py tokens.json tokens.css README.md DESIGN.md theme-init.js components fonts)
WHAT=check
run() { # run <dir> [filters...]: the check on the copy in <dir>
  local dir="$1"
  shift
  (cd "$dir" && uv run -q --project "$HERE" --locked python scripts/check-previews.py --browser "$ENGINE" --out "$dir/shots" "$@") > "$dir/out.txt" 2>&1
}

pass=0
fail=0
echo "the check on the repository's files (every preview and device, the light theme):"
copy "$tmp/base"
if [ -n "$ONLY" ]; then
  printf '    --    not run: ONLY is set, so this is no result\n'
elif [ -n "${PREVIEWS_CHECKED:-}" ]; then
  printf '    --    not run: PREVIEWS_CHECKED says the full check has just passed on these files\n'
elif run "$tmp/base" --theme light; then
  printf '    ok    passes (%s)\n' "$(grep -E '^[0-9]+ pages' "$tmp/base/out.txt" | cut -d';' -f1)"
  pass=$((pass + 1))
  # The run names the engine it rendered in: the one --browser asked for (D40)
  if grep -qE "^engine: $ENGINE [0-9]" "$tmp/base/out.txt"; then
    printf '    ok    renders in %s\n' "$(grep -E '^engine: ' "$tmp/base/out.txt" | cut -d' ' -f2-)"
    pass=$((pass + 1))
  else
    printf '    FAIL  does not say it rendered in %s\n' "$ENGINE"
    fail=$((fail + 1))
  fi
else
  printf '    FAIL  fails:\n'
  grep -E '^FAIL|Error' "$tmp/base/out.txt" | sed 's/^/          /' | head -20
  fail=$((fail + 1))
fi

wanted() { [ -z "$ONLY" ] || [[ "$1" == *"$ONLY"* ]]; }

# The engine is PREVIEW_ENGINE's alone, never BROWSER's (D61): many tools read BROWSER as the command
# for a web browser, and a shell that set BROWSER=true once failed every control here. So one control
# runs again in a shell like that, with no PREVIEW_ENGINE, and must be refused as it is in Chromium.
SHELL_LABEL="a shell with BROWSER=true and no PREVIEW_ENGINE still runs the controls in chromium"
if wanted "$SHELL_LABEL"; then
  echo "the engine variable:"
  nested="$(env -u PREVIEW_ENGINE BROWSER=true ONLY='a label pushed off centre' bash "$HERE/tests/test-check-previews.sh" 2>&1)"
  if grep -qF 'ok    control "a label pushed off centre": refused' <<< "$nested"; then
    printf '    ok    %s\n' "$SHELL_LABEL"
    pass=$((pass + 1))
  else
    printf '    FAIL  %s:\n' "$SHELL_LABEL"
    grep -E 'FAIL|rror' <<< "$nested" | sed 's/^ */          /' | head -5
    fail=$((fail + 1))
  fi
fi

# The side-by-side query and its least height H as the build has them, from the tokens (D75)
QUERY="$(query side-by-side)" || {
  echo "FAIL build-tokens.py --query side-by-side gives nothing"
  exit 1
}
H="$(query side-h)" || {
  echo "FAIL build-tokens.py --query side-h gives nothing"
  exit 1
}
HPX="$(python3 -I -c 'import sys; print(round(16 * float(sys.argv[1].removesuffix("rem"))))' "$H")" # H in px

P="--theme light --device phone"
D="--theme light --device desktop"
echo "the controls, each a copy with one mistake that must be refused:"
# --browser that never reaches the launch: the run renders in Chromium, whatever it asked for (D40)
sub "--browser ignored, Chromium launched" 'setup: asked for webkit, but the page runs in .*Chrome/' "--browser webkit --only Button $D" \
  scripts/check-previews.py 'getattr(pw, engine).launch()' 'pw.chromium.launch()'
css "code in the browser's monospace" 'fonts: <code>' "--only Dialog $D" 'code{font-family:monospace}'
sub "a broken font query" 'getPlatformFontsForNodes' "--only Button $D" scripts/check-previews.py \
  '"CSS.getPlatformFontsForNode"' '"CSS.getPlatformFontsForNodes"'
# The engine reports the fonts of the layout as it stands, and a box not laid out yet reports none, which
# reads as no fallback: so the walk lays the page out first, and a walk that finds no layout fails. The
# body hidden at that step stands in, every run, for the race that let the control above pass once in CI
sub "a font walk that finds no layout" 'setup: the font walk read no font for <code>, which draws text' "--only Dialog $D" \
  scripts/check-previews.py 'document.body.offsetHeight;   // laid out' 'document.body.hidden = true; document.body.offsetHeight;   // laid out'
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
  "--only Workbench --theme light --device landscape-800" '.ws-stage__menu:popover-open{translate:var(--panel-width) 0}'
sub "View... left open when a view is picked" "close: picking '[A-Za-z]+' leaves the View… menu open" "--only Workbench $P" \
  components/Workbench/README.md 'menu.hidePopover();' 'void menu;'
sub "no lines for closing View..." 'Workbench: close: its README gives no lines' "--only Workbench $P" \
  components/Workbench/README.md '```js' '```text'
# More… closes when an action in it is picked, with the Header README's lines (D87), and its items line up (A86)
sub "More... left open when an action is picked" "close: picking '[A-Za-z ]+' leaves the More… menu open" "--only Header $P" \
  components/Header/README.md 'menu.hidePopover();' 'void menu;'
sub "no lines for closing More..." 'Header: close: its README gives no lines' "--only Header $P" \
  components/Header/README.md '```js' '```text'
css "the More... menu's items centred" "header: the open More… menu's icons start from [0-9.]+ to [0-9.]+px across" "--only Header $P" \
  '.ws-header__actions:popover-open > .ws-btn{justify-content:center}'
sub "the dark theme in a light color-scheme" 'scheme:' "--only Button --theme dark --device desktop" tokens.css \
  'color-scheme: dark;' 'color-scheme: light;'
css "both hints on show" 'hints:' "--only Workbench $D" '.ws-hint-touch{display:inline}'
css "a warning headline in ink" "notice: the warning Notice's headline" "--only Notice $D" \
  '.ws-notice--warning strong{color:var(--ink)}'
css "an empty Notice taking room" 'notice: an empty Notice takes room' "--only Notice $D" \
  '.ws-notice:empty{padding:var(--space-3)}'
sub "a plan line nobody hears" 'live: ws-plan__line' "--only Workbench $D" components/Workbench/preview.html \
  'id="ws-plan-line" aria-live="polite"' 'id="ws-plan-line"'
css "a squeezed plan sentence" 'plan: the plan sentence is [0-9]+px wide on a 960px screen, under plan-line-min' \
  "--only Workbench $D" '.ws-plan__line{max-width:var(--space-6)}'
# Beside the sidebar the plan bar is one row too, its sentence at most two lines (D75, D79)
css "a plan bar of two rows beside the sidebar" 'plan: the plan bar is not one row, beside the sidebar on a 960 x 800 screen' \
  "--only Workbench $D" '.ws-plan{flex-wrap:wrap}.ws-plan__line{flex-basis:100%}'
css "a plan sentence of three lines beside the sidebar" 'plan: the plan sentence takes more than two lines, beside the sidebar on a 960 x 800 screen' \
  "--only Workbench $D" '.ws-plan__line{-webkit-line-clamp:3}'
# What must be read goes first, as the clamp cuts the end: the first sentence shows whole (A86)
sub "the example last in the plan sentence" "plan: the plan sentence's first sentence, '4 pieces .*', is cut short, stacked on a 375 x 800 screen" \
  "--only Workbench $P" components/Workbench/preview.html \
  'Example wall. Replace the sizes with yours. 4 pieces · 1 hose port · foam tape: window_sealer_1280x420mm_hose_port_left_foam_tape_10mm.zip.' \
  '4 pieces · 1 hose port · foam tape: window_sealer_1280x420mm_hose_port_left_foam_tape_10mm.zip. Example wall. Replace the sizes with yours.'
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
# An ellipsis is the one character, in a preview's label and in what a doc tells a tool to write (D89)
sub "an ellipsis of three full stops in a label" "Button: markup: 'Download the pieces\.\.\.' ends in three full stops" "--only Button $D" \
  components/Button/preview.html 'Download the pieces…' 'Download the pieces...'
sub "a doc that writes an ellipsis as three full stops" "markup: components/Button/README.md writes 'Download\.\.\.' with three full stops" "--only Button $D" \
  components/Button/README.md '"Download…":' '"Download...":'
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
# With the bars one row, a narrow landscape phone side by side keeps 40 %; it stacks by its decision (D41)
sub "side by side on a narrow landscape screen" 'layout: the sidebar is beside the stage on a 740 x 360 screen, where it goes under the stage' \
  "--only Workbench --theme light --device landscape-740" components/bundle.css "${QUERY##*,}{" '(min-aspect-ratio:4/3){'
# The least screen side by side, breakpoint-side-min by H (D75), and its edges a pixel either way, by the
# layout check; then a phone held sideways, as the breakpoints before D75 left it
sub "the least screen side by side stacked, H a pixel taller" 'layout: the sidebar is under the stage on a 768 x [0-9]+ screen, where it goes beside the stage' \
  "--only Workbench --theme light --device side-least" components/bundle.css "(min-height:$H)" "(min-height:$((HPX + 1))px)"
sub "side by side a pixel under H" 'layout: the sidebar is beside the stage on a 768 x [0-9]+ screen, where it goes under the stage' \
  "--only Workbench --theme light --device side-least-low" components/bundle.css "(min-height:$H)" "(min-height:$((HPX - 1))px)"
sub "side by side a pixel under breakpoint-side-min" 'layout: the sidebar is beside the stage on a 767 x [0-9]+ screen, where it goes under the stage' \
  "--only Workbench --theme light --device side-least-narrow" components/bundle.css '(min-width:48rem)' '(min-width:47.9375rem)'
sub "800 x 360 stacked, as before D75" 'layout: the sidebar is under the stage on a 800 x 360 screen, where it goes beside the stage' \
  "--only Workbench --theme light --device landscape-800" components/bundle.css "$QUERY{" \
  '(min-width:61rem),(min-width:56.5rem) and (min-height:25.5rem),(min-width:56rem) and (min-height:30rem),(min-aspect-ratio:4/3) and (min-width:48rem) and (min-height:30rem){'
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
  '.ws-stepper__btn{position:relative;top:var(--space-1)}'
# Every field, and a Stepper's buttons, are exactly control-h tall (D68): taller, each fails on its own;
# shorter cannot happen, as min-height holds them at control-h
css "a field taller than control-h" "height: ws-input '640' is [0-9.]+px, control-h is 36.00px; a control of one line is exactly control-h tall \(D68\)" \
  "--only Field $D" '.ws-input{padding-block:var(--space-2)}'
css "Stepper buttons taller than control-h" "height: ws-btn '↓' is [0-9.]+px, control-h is 44.00px; a control of one line is exactly control-h tall \(D68\)" \
  "--only Stepper $P" '.ws-stepper__btn{min-height:calc(var(--control-h) + var(--space-1))}'
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
# The Select (D69): what it is made of and its chevron as the stylesheet gives it (check 35), then where the
# chevron is drawn, measured on the pixels that change when it is hidden, here and in forced colours
E=components/Select/preview.html
sub "a select outside a .ws-select" "select: 'Seal material' is not a select.ws-input alone in a span.ws-select" "--only Select $D" "$E" \
  'Seal material<span class="ws-select">' 'Seal material<span>'
sub "a select with no label" "select: 'a select' has no label" "--only Select $D" "$E" \
  '<label class="ws-label">Seal material<span class="ws-select">' '<span class="ws-select">'
css "a select with the browser's own arrow" "select: 'Printer' keeps the browser's own arrow beside its chevron \(appearance auto" "--only Select $D" \
  '.ws-select > .ws-input{appearance:auto}'
css "a chevron the font lacks" "select: the chevron of 'Printer' is U\+E000, which the system's font does not hold" "--only Select $D" \
  '.ws-select::after{content:"\e000" / ""}'
css "a chevron in another family" "select: the chevron of 'Printer' is set in monospace, not in the system's font" "--only Select $D" \
  '.ws-select::after{font-family:monospace}'
css "a chevron with alternative text" "select: the chevron of 'Printer' is .*, not one glyph with empty alternative text" "--only Select $D" \
  '.ws-select::after{content:"\eab4" / "open"}'
css "a chevron read aloud" 'names: icon glyph' "--only Select $D" '.ws-select::after{content:"\eab4"}'
css "a chevron not in the text colour" "select: the chevron of 'Printer' is rgb\([0-9, ]+\), not the select's text colour" "--only Select $D" \
  '.ws-select::after{color:var(--ink-muted)}'
css "a chevron under its select" "select: the chevron of 'Printer' draws nothing on the screen \([0-9]+ pixels change when it is hidden\)" "--only Select $D" \
  '.ws-select > .ws-input{position:relative}'
css "a chevron over the select's text" "select: the chevron of 'Printer', drawn from .* lies over the select's text" "--only Select $D" \
  '.ws-select > .ws-input{padding-inline-end:var(--field-pad-x)}'
css "a chevron that takes the press" "select: the chevron of 'Printer' takes the press: at its centre a press lands on span.ws-select" "--only Select $D" \
  '.ws-select::after{pointer-events:auto}'
css "a chevron lost in forced colours" "select: in forced colours, the chevron of 'Printer' draws nothing on the screen" "--only Select --device forced" \
  '@media (forced-colors:active){.ws-select::after{content:none}}'
css "a select that does not tint on hover" "states: select.ws-input 'Bambu Lab P1S' does not change on hover" "--only Select $D" \
  '.ws-select > .ws-input:hover:not(:disabled){background:var(--surface-raised)}'
css "a disabled select that tints on hover" "states: select.ws-input '256 × 256 mm' is disabled but changes on hover" "--only Select $D" \
  '.ws-select > .ws-input:hover{background:var(--action-tint)}'
css "a select taller than control-h" "height: ws-input 'Bambu Lab P1S' is [0-9.]+px, control-h is 36.00px; a control of one line is exactly control-h tall" "--only Select $D" \
  '.ws-select > .ws-input{padding-block:var(--space-2)}'
# The fallback pass (D60): a View… menu that runs off the screen only where nothing anchors it (the main
# run passes this copy, as the @supports block sets the margin again), then the pass's own setup, each
# way it could draw what the main run draws instead of the fallback
F="--fallbacks --only Workbench $P"
sub "the unanchored View... menu off the screen" 'stage: the View… menu, unanchored as without position-area \(Firefox ESR 140\), at .* runs off the' \
  "$F" components/bundle.css '.ws-stage__menu:popover-open{display:grid;' '.ws-stage__menu:popover-open{margin:0 0 0 100vw;display:grid;'
sub "the fallback pass keeping the @supports block" 'setup: fallbacks: the open View… menu is anchored \(position-area' "$F" \
  scripts/check-previews.py 'bundle, blocks = without_blocks(bundle, FALLBACK_BLOCK)' 'blocks = 1'
sub "the fallback pass keeping the font-metric overrides" 'setup: fallbacks: .*FiraCode Nerd Font.* is loaded with ascent, descent and line-gap overrides' \
  "--fallbacks --only Button $D" scripts/check-previews.py 'tokens, overrides = FALLBACK_OVERRIDES.subn("", tokens)' 'overrides = 6'
sub "no @supports (position-area) block to take out" 'setup: fallbacks: bundle.css has no @supports \(position-area: …\) block to take out' \
  "--fallbacks --only Button $D" components/bundle.css '@supports (position-area:block-end){' '@supports (anchor-name:--ws-stage-view){'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ -z "$ONLY" ] && [ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
