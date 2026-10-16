# Changelog

What changed in each version, and how a tool that copies the files moves to it. Versions follow
[Semantic Versioning](https://semver.org), counted by what a tool must do, not by the size of the
change. A patch version (0.4.1) can be copied over the last one with no change to a tool's markup
or CSS, and every page stays as it was or better. Anything a tool must follow is a minor version
while the version is 0.x, however small, and its entry says how to follow. v0.5.0 is one: with the
v0.4.0 markup, its stylesheet stretches the view choice over the 3D view. The version is in
`tokens.json`, in the head of `tokens.css` and in `pyproject.toml`, and `scripts/build-tokens.py`
keeps them, this file and the tag in step; it refuses a tag whose entry here still says
"unreleased".

## v0.5.1 (unreleased)

The second review of v0.5.0 (`docs/review-2026-10-16-2.md`), its fixes that need no decision
(A38). A patch: copy the files over v0.5.0; no change to a tool's markup or CSS.

### Moving to it

Copy `tokens.css`, `components/bundle.css` and `fonts/` from the tag, as before. Nothing else.

### Fixed

- **The wide-screen header (v0.4.0 and v0.5.0).** The phone rules came after the wide-screen ones
  at the same specificity and undid them, so on a desktop the tool name was in the `legend` size,
  not `step`, the header buttons had the phone's padding and the spacer was hidden.
  `build-tokens.py` now fails if a rule inside a media query is undone by a later rule outside one.
- **The View… menu in Safari and every iOS browser (v0.5.0).** WebKit stretched the menu's grid,
  and the menu with it, to the height of the screen, over the button that opened it
  ([WebKit bug 270334](https://bugs.webkit.org/show_bug.cgi?id=270334)). The grid now keeps to its
  rows (`align-content:start`): under its button, as in Chromium. `build-tokens.py` fails on a
  grid popover without `align-content`.
- **The header's focus rings (v0.4.0 and v0.5.0).** On a phone the header clipped the top and
  bottom of a focused button's ring (`overflow-x:auto`); on a wide screen the actions row did too,
  as the browser gives a popover `overflow:auto`, and between 896 and about 1000px it scrolled its
  own buttons out of sight ("Dark theme" cut off) instead of shortening the tool name. Nothing in
  the header clips now, and the wide row keeps its width; the name is cut short instead, its full
  text still in the page. The header is now 48px (`header-h`) with its border, not 49px, so it no
  longer runs 1px into the stage and the phone's More… menu opens under it, not over its rule.
- **Hover (v0.4.0 and v0.5.0).** A disabled Button or Choice took the hover tint, as if it could
  be used; it no longer changes. Tiles, PieceMap cells, step buttons and Disclosure summaries had
  no hover; they take the tint, as every other control does.
- **The selected tile and piece.** A selected Gallery tile and PieceMap cell kept a grey border
  inside their ring, so a focused one differed from a focused unselected one by its tint alone
  (1.13:1). Both take the `action` border, as Choice, Sides and the rail do, and a selected tile's
  label is bold. A PieceMap cell's bold already says it has its own fill, so its label stays as it
  is.
- **`check-previews.py` let some mistakes through.** A broken font query passed as "no fallback"
  (every error was caught); a misspelt selector checked nothing and passed; the count of primary
  buttons counted pages, so it could never be zero; focusing the form only downwards never put a
  field under the pinned stage, so a lost `scroll-padding` passed; and on Windows a message quoting
  an icon crashed the run. Each now fails.
- **`tests/test-build-tokens.sh` proved less than it said.** Its CSS controls all used the class
  `.x`, which the prefix rule (v0.4.0) refuses, so each was refused whatever its own rule did. Each
  control now uses `.ws-x` and counts only if the build fails with its own rule's message.

### Added

- `tests/test-check-previews.sh`: every check in `check-previews.py` held to a control, a copy
  with one mistake that must fail with that check's own message, run in CI after the check.
  `check-previews.py` takes `--only`, `--device` and `--theme` to render a part of the run.
- `check-previews.py` renders the states: every focusable control's ring (2px or wider, action,
  clipped by nothing), hover (an enabled control changes, a disabled one does not), every
  selected control's tint, ring, border and bold, faded disabled controls, the invalid field and
  error text. It fails on a box that scrolls sideways inside itself, and renders the workbench and
  the header at the breakpoint's width (896px) as well.
- It also opens the header's More… menu as it opens View… (under the header, on the screen, every
  action on show, and on a wide screen every action in the row); scrolls a phone to check the view
  and the plan bar stay pinned; holds a touch screen's controls to 44px, not to the `tap` token;
  holds tiles to `control-h` and a one-line Choice face to it exactly; and checks the attributes
  that make each control what it is (`aria-pressed` on toggles, a named `radiogroup` for a Choice,
  a popover behind every `popovertarget`).
- `check-previews.py` measures the contrast of every run of text as drawn, hovered too, against what
  is behind it (1772 runs), not only the token pairs `check-contrast.py` lists.
- `build-tokens.py` also refuses a system colour, `color-mix()`, a gradient, a typed opacity, font
  size or line height, an at-rule but `@media` and `@supports` (no `@container`, no `@keyframes`),
  and any custom property the stylesheet sets but `control-h` on a touch screen.

## v0.5.0 (16 Oct 2026)

The owner's answer D36: on a phone, the 3D view's own controls wait in one menu.

### Moving to it

Copy `tokens.css`, `components/bundle.css` and `fonts/` from the tag, as before. Then, in the stage:

- **View… (D36).** In `.ws-stage__tools`, right after "Reset view", add
  `<button class="ws-btn ws-stage__more" type="button" popovertarget="…">View…</button>`, then
  `<div class="ws-stage__menu" id="…" popover>` holding "Zoom in", "Zoom out" and the
  `.ws-stage__views` choice, which moves from after the tools into this menu. No script: the
  browser opens and closes the menu, and the buttons and the choice work as before.

### Changed

- On a phone or a short screen the view shows only "Reset view" and "View…", which opens Zoom in,
  Zoom out and Front · Back · Top in a menu under it, so the view stays clear for the fingers that
  pinch and drag; anyone who cannot is one press away (D36, WCAG 2.5.1 and 2.5.7). A wide screen
  shows them all, as before. Where a browser cannot anchor the menu to its button, it opens in the
  middle of the screen.

### Added

- `check-previews.py` checks the menu: on show only on a phone or a short screen, holding the zoom
  buttons and the choice, opening under its button and on the screen. The workbench is checked on
  one more screen, a large phone on its side (932 × 430), which is wide and short.

## v0.4.0 (16 Oct 2026)

From the review of 16 Oct 2026 (`docs/review-2026-10-16.md`) and the owner's answers D25 to D33,
A34 and A35.

### Moving to it

Copy `tokens.css`, `components/bundle.css` and `fonts/` from the tag, as before; the fonts changed.
Then, in your markup and your own CSS:

- **The type classes `tokens.css` generates are now `ws-type-*`** (`.ws-type-note`, not `.note`;
  likewise `title`, `section`, `step`, `body`, `legend`, `label-caps`, `code`). A tool that styles
  its own `.note` is unaffected; one that relied on the generated class renames it, or uses
  `.ws-note`.
- **Header (D28).** The name is `h1.ws-header__name`. Everything after Redo goes in
  `<div class="ws-header__actions" id="…" popover>`, opened by
  `<button class="ws-btn ws-header__more" type="button" popovertarget="…">More…</button>`, which
  comes right after Redo. The theme toggle reads "Dark theme" and carries `aria-pressed`.
- **Stage (D25).** "Reset view" moves out of the plan bar into
  `<div class="ws-stage__tools">` inside `.ws-stage__view`; the plan bar's `.ws-plan__actions`
  holds the primary button. On a phone `.ws-stage` lays its parts out in the page
  (`display:contents`), so put nothing on `.ws-stage` itself that a phone needs.
- **The 3D view without a pointer (D30).** In `.ws-stage__tools`, after "Reset view", add "Zoom in"
  (`&#xeb81;`) and "Zoom out" (`&#xeb82;`) buttons; after the tools,
  `<div class="ws-choice ws-stage__views" role="radiogroup" aria-label="View">` with Front, Back and
  Top as Choice options. Give the canvas `tabindex="0"`, `role="img"`, an `aria-label` naming the
  part ("The wall in 3D") and `aria-describedby` with the plan line's `id`. In the script: on the
  focused canvas the arrow keys turn the camera and `+` and `-` zoom, by the buttons' steps; the
  zoom buttons stop where a pinch stops; a view option turns the camera to face that side, framed to
  `stage-fit`, and a turn away clears the choice. Add "Arrow keys: turn" to the mouse hint. The view
  now lays its children out in rows, so `.ws-stage__tools` is no longer absolutely positioned; drop
  any local positioning of it.
- **Step rail (D31).** Optional: leave it out for a short form. When used, it runs across the top
  of the sidebar, and each button reads `<span class="ws-rail__num">2</span>Window`; a done step adds
  `<span class="ws-sr">, done</span>`. The `rail-w` token is gone.
- **`choice` (D27).** The token and the `.ws-fieldset--choices` border are gone; the class does
  nothing now and can be dropped.
- **Selection (D26).** No markup change: a chosen Choice, a pressed Sides toggle and the active
  step are now `action-tint` with an `action` ring and a bold label, as tiles and pieces were, and
  only the primary button is filled. The Sides box is drawn pressed or not, the radio's size, and
  its tick moved to `::after`; a tool's own CSS on `.ws-sides__btn::before` follows it.
- **Live regions.** Give `.ws-plan__line` and every `.ws-error` `aria-live="polite"`, and link a
  field's error and note to it with `aria-describedby`. An empty Notice or stage message is now
  collapsed rather than `display:none`, so it stays announced; no markup change.
- **Numeric fields.** `inputmode="decimal"` only for a value that cannot go below zero;
  `type="number"` for one that can.
- **Skådis Air:** drop the local rules v0.3.0 already carried, and the local
  `.ws-notice strong { color: var(--warning) }`, which would turn an error Notice's headline amber.

### Added

- The phone stage (D25): the 3D view alone is pinned at `stage-phone-h` (45svh), the plan bar
  pinned under it as one row, the status bar scrolling away; nothing pinned under
  `breakpoint-short`; side by side at `landscape-ratio` or wider, so a landscape phone is not
  stacked; `scroll-padding` keeps a focused field below the pinned part.
- The 3D view without a pointer (D30): Zoom in and Zoom out beside Reset view, a Front · Back · Top
  choice (`.ws-stage__views`), and a focus ring inside the view. The view lays its controls out in
  rows over the drawing, so they wrap and never overlap, and a drag between them reaches the
  drawing; a short screen's view grows to fit them. An `svg` in the view is laid out as a canvas is.
  The Icons card lists `zoom_in` and `zoom_out`.
- The header's "More…" popover below the breakpoint (D28); `.ws-header__version`.
- `.ws-stage__tools`, `.ws-actions` (a row of buttons), `.ws-sr` (text for assistive tech only),
  `.ws-rail__num`; links in text take `action` and the focus ring; a dialog's `h2` takes the
  `section` style.
- Tokens: `line` (1px hairlines), `sides-w`, `sides-h`, `stage-phone-h`, `breakpoint-short`,
  `landscape-ratio`; `--weight-regular` and `--weight-bold` from the font files;
  `--text-label-caps-tracking`; `label-caps` carries its uppercase.
- Checks. `build-tokens.py` fails on any value `bundle.css` types (a colour in any notation, a
  length, a font family, weight or tracking, an undefined custom property, another media query), on
  a weight no font ships, on an icon drawn past its advance, on versions out of step, on a tag whose
  changelog entry still says unreleased, and on a class without its prefix. `check-contrast.py`
  fails on a part that vanishes on the stage and on a colour in no pair. `check-previews.py` checks
  the markup (inline styles, one primary button, numeric keyboards), live regions and invalid
  fields, the phone layout on three more screens (view height, focus never covered, the header never
  scrolling), data shown as typed, named steps, selected states tinted and ringed with only the
  primary button filled, the Sides box the radio's size with its tick centred on it, and a 3D view
  usable without a pointer; every check counts what it looked at and fails at zero.
  `tests/test-build-tokens.sh` and `tests/test-check-contrast.sh` hold the first two to controls.
- Commit hooks and CI from Skådis Air (D20): every pre-commit hook, the identity of every pushed
  commit, a full-history secret scan.

### Changed

- The fonts: every icon's advance is the width it draws, so the gap to its label is `icon-gap` for
  every icon (`scripts/fit-icon-advances.py`); text glyphs are unchanged.
- `model-tpu` is `#666666` on the dark stage, where the seal and its outline had vanished.
- The type styles ask only for the weights that ship (400 and 700), which is how they drew.
- Ligatures go off in the plan line, so file names show as typed (D29).
- The Notice's corners are `radius-sm`; Back and Next wrap on a narrow sidebar; the status bar
  wraps between its items; Choice faces may wrap a long label on a narrow screen.
- Metric is the default and imperial stays an option, for accessibility (D33).
- Selection is tint and ring (D26): the chosen Choice (its radio an `action` dot), a pressed Sides
  toggle and the active step drop the `action` fill, which is the primary button's alone. The
  Sides box is the radio's size and stays drawn when not pressed, so pressing never moves a label.

### Fixed

- The docs and the previews now agree with the stylesheet (the review's 36 mismatches): the chosen
  Choice shows a radio, not a tick; the rail; the tool name's style; token usage texts;
  the Workbench preview follows its own rules.
- Phone screenshots are drawn with touch emulation on, at the device's own height.

## v0.3.0 (15 Oct 2026)

What Skådis Air had added to the system in its own page (D18): `color-scheme` per theme;
`.ws-page`; the warning Notice and headline colours; the stage's canvas contract and
`.ws-stage__message`; the mouse and touch hints; `.ws-plan__line` and `.ws-plan__actions` with the
tokens `plan-line-basis` and `number-field-w`; smaller margins. `DESIGN.md` names Skådis Air's code
as the reference (D19).

## v0.2.0 (14 Oct 2026)

The part always fits the stage (D15): the tokens `stage-fit` and `stage-min-fill`.

## v0.1.0 (14 Oct 2026)

The first version: tokens, components and their previews, the fonts loaded once from `fonts/`
(D9), MPL-2.0 and CERN-OHL-S-2.0 in the REUSE layout (D8), and the checks.
