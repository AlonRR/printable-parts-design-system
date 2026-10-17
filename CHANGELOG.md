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

## v0.6.0 (unreleased)

The owner's answers D47, D49, D41, D42, D52, D39, D51 and D40: a selected PieceMap cell says so
with a mark, not by colour alone; the header keeps the tool's name whole wherever the sidebar
sits beside the stage, and on a phone puts the version in More…; a narrow or short landscape
screen stacks; the open View… menu leaves the part in sight; on a phone the primary button's
short label leaves the plan's sentence room; and the system states the browsers it targets and
checks its previews in Chromium, WebKit and Firefox. A minor version: D42 asks a tool's script for
a few lines, and D39 and D51 change a tool's markup.

### Moving to it

Copy `tokens.css`, `components/bundle.css` and `fonts/` from the tag, as before. Then, in the
tool's script, close the View… menu when a view is picked (D42), with the lines the Workbench
README gives: a `change` listener on each `.ws-stage__menu` that calls `hidePopover()` when the
change comes from its `.ws-stage__views` choice and the menu is open. Then two changes to the
markup:

- **The primary button's label (D39).** In the plan bar, put the words the button drops on a
  phone in a `span.ws-plan__long`, starting it with `&nbsp;` and keeping the ellipsis outside it:
  `Download the pieces...` becomes `Download<span class="ws-plan__long">&nbsp;the pieces</span>...`,
  after the icon as before. Without the span the button keeps its whole label on a phone, and the
  sentence beside it gets 70px at 375px wide and 15px at 320.
- **The version inside More… (D51).** If the header shows the tool's version, add a second copy,
  the same text, as the last thing in `.ws-header__actions`, after the theme toggle:
  `<span class="ws-header__version">v1.2.0</span>`. Keep the one beside the name. Without the
  copy a phone shows no version at all. A header without More… changes nothing: its version stays
  in its row.

### Changed

- **On a phone the primary button shows a short label (D39).** Wherever the plan bar is one row
  (every screen where the sidebar is not beside the stage), its sentence shared the row with
  "Download the pieces...", which never wraps: 70px at 375px wide, about 8 characters a line,
  and 15px at 320. There the button now shows "Download...", the rest of its label hidden from
  view only, so a screen reader still hears all of it; the ellipsis stays on screen, as a button
  that opens a dialog ends with one. Side by side the whole label shows, drawn as before. The
  sentence gets 172px at 375px wide and 117px at 320 (Chromium). A new token, `plan-line-min`
  (7rem, 112px), is the sentence's least width on any screen; nothing in the stylesheet reads it,
  and `check-previews.py` fails a screen where the sentence is narrower (on the old markup,
  375 × 800, 375 × 667, 320 × 256 and 320 × 180) and a button whose label has a part hidden from
  screen readers (`display:none`, `visibility:hidden` or `aria-hidden`, an icon aside). Chromium
  puts a space between the label's parts in the button's name, "Download the pieces ...", which a
  screen reader says as before.

- **On a phone the version is in More… (D51).** Below `breakpoint-header` the version tag beside
  the tool's name cut the name short: in the Header preview, 10 of its 120px at 320px wide and 65
  at 375. There it now sits in the More… menu, after the actions, and from `breakpoint-header` up
  beside the name, as before. The copy not on show is `display:none`, so a screen reader hears one
  version: on a phone in the open menu, with the actions. A header without More… keeps its
  version in its row. `check-previews.py` fails if the row holds a version below
  `breakpoint-header` (on the old markup, on all 15 checked screens narrower than 64rem), or if
  more or fewer than one shows, in the open menu or on a wide screen.

- **A short screen stacks below 61rem (D52).** After D41, a short screen (`breakpoint-short` or
  less tall) from 48rem up to 964px wide still put the sidebar beside the stage, and there the 3D
  view got 28 to 39 % of the screen: the plan bar wrapped to two or three rows in the stage's
  column, and with a mouse the status bar's hint to two lines. 800 × 360, a phone held sideways,
  gave the view 111px (31 %). A short screen now goes side by side only from
  `breakpoint-side-short` (61rem, 976px, a new token), its value the narrowest from which every
  short screen side by side, 360 to 470px tall, keeps 40 % (measured); narrower, it stacks and
  pins nothing, so the view keeps `stage-phone-h` (45 %) and the page scrolls. So 844 × 390 and
  932 × 430, large phones held sideways, now stack too. `check-previews.py` now draws 800 × 360,
  a 900 × 400 window and 976 × 360, and `build-tokens.py` fails if the side-by-side query lets a
  short screen through.

- **The open View… menu leaves the part in sight (D42).** On a phone or a short screen the menu
  opened under its button, over the part: 28 % of the 3D view on a 375 × 800 phone, 33 % at
  375 × 667, 44 % at 844 × 390, and it stayed open after Front, Back or Top was picked. It now
  opens below the view, over the plan bar, its right edge under View…'s, covering none of the view
  on any checked screen; and the tool's script closes it when a view is picked (above). Where a
  browser cannot anchor the menu, it opens mid-screen, over the part, as before. On a screen
  zoomed to 320px wide the room below the view is short, so the menu scrolls inside (85px of 140
  at 320 × 256, 43px at 320 × 180). `check-previews.py` fails if the open menu covers any of the
  view, sits above it, leaves its column or runs off the screen, and runs the README's lines on
  the preview, failing if a pick leaves the menu open.

- **A narrow landscape screen stacks (D41).** Any screen wider than 4:3 put the sidebar beside the
  stage, however narrow: on a 740 × 360 phone the 3D view was 111px (31 % of the screen), at
  200 % zoom on 1280 × 720 104px, and at 400 % 16px, its controls drawn outside it. Side by side
  now also needs `breakpoint-side-min` (48rem, a new token): a narrower landscape screen stacks,
  as a phone held upright does, and pins nothing, as a short screen already does, so the view
  keeps `stage-phone-h` (45 %) and the page scrolls. Open, the More… and View… menus now end at
  the screen's bottom edge and scroll inside: at 320 × 180 both ran off it. `check-previews.py` now
  draws 667 × 375, 740 × 360, 640 × 360, 320 × 180 and a 720 × 520 window, and fails if anything
  is pinned on a stacked landscape screen; `build-tokens.py` fails if either query leaves the
  token out.

- **The header keeps its phone row up to 64rem (D49).** From 56rem, where the sidebar moves
  beside the stage, the header's whole row left the tool's name as little as 20px at 896px ("W…"
  beside the version, v0.5.1). The header now changes at a width of its own, `breakpoint-header`
  (64rem, a new token in `tokens.css`): below it Reset, Save project, Load project and the theme
  toggle stay behind More… and the name takes the legend size, as on a phone; from it the whole
  row shows. So on a window 56 to 64rem wide the sidebar sits beside the stage under the phone's
  header row, and the name and the version are whole. `check-previews.py` fails if the name is
  cut from 56rem up, and `build-tokens.py` if a header rule sits at the layout's breakpoint.

### Fixed

- **A selected PieceMap cell (every version so far).** Focused, a selected cell and an unselected
  one differed only by their border and tint (1.13:1): every other selected control has a bold
  label, but a cell's bold says it has its own fill. A selected cell now shows the chosen radio's
  dot before its label, as a chosen Choice option does: a piece is one of a pick-one, and a tick
  means pick several. The dot is drawn by the Choice rules, in forced colours too. A cell's width
  comes from the grid's columns, so the dot never moves the map: the PieceMap README now asks for
  `repeat(<columns>, 1fr)` columns, as with `auto` ones the dot would widen the chosen cell's
  column. No tool shows a PieceMap yet, so none has to change. `check-previews.py` fails if a
  selected cell has no mark, if a cell that is not selected has one, or if in forced colours the
  two look alike by their marks.

### Added

- **A browser target (D40).** README.md, "Browsers": the current and previous major version of
  Safari (iOS too), Chrome and Firefox, and Firefox ESR, with what the system relies on, the first
  version of each engine that has it, and what a browser in the target without it shows: Firefox
  before 147, ESR 140 among them, has no `position-area`, so there the open View… menu opens
  mid-screen, over the part, as before D42. Nothing in the files a tool copies changes.
- **`check-previews.py --browser chromium|webkit|firefox`**, and CI runs it in each, a job each
  with its own screenshots, so a WebKit-only fault such as v0.5.0's full-screen View… menu fails
  a job. The run prints the engine and its version and fails if the page's user agent is another
  engine's; `tests/test-check-previews.sh` holds that to a control (a copy that always launches
  Chromium, asked for WebKit, must fail). Outside Chromium the font and hover checks are left out
  (they read through CDP), and in WebKit forced colours (emulated but not drawn); where an engine
  has no `position-area`, only the View… menu's fallback is checked; the run names each. The
  accessible names are now read from each engine's own tree, and each focused control is scrolled
  into view as Tab brings it, as WebKit's `focus()` scrolls nothing. On the files of `08f4f49`,
  WebKit 26.0 and Firefox 142 each check 116 pages with 0 failing.

## v0.5.1 (17 Oct 2026)

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
  text still in the page. Just above the breakpoint that leaves little of it: at 896px, 80px of
  "Window sealer" in the Workbench preview, and 20px beside a version tag. How much of the name
  must stay is decided for the next version (D49). The header is now 48px (`header-h`) with its
  border, not 49px, so it no longer runs 1px into the stage and the phone's More… menu opens under
  it, not over its rule.
- **Hover (v0.4.0 and v0.5.0).** A disabled Button or Choice took the hover tint, as if it could
  be used; it no longer changes. Tiles, PieceMap cells, step buttons and Disclosure summaries had
  no hover; they take the tint, as every other control does.
- **The selected tile and piece.** A selected Gallery tile and PieceMap cell kept a grey border
  inside their ring, so a focused one differed from a focused unselected one by its tint alone
  (1.13:1). Both take the `action` border, as Choice, Sides and the rail do, and a selected tile's
  label is bold. A PieceMap cell's bold already says it has its own fill, so its label stays as it
  is.
- **Forced colours (v0.4.0 and v0.5.0).** With Windows High Contrast or any forced colours, the
  chosen Choice's radio lost its dot (its `action` fill turned to the page colour) and looked
  unchosen, and a step not yet reached took the same border as a done one. The chosen radio is now
  a filled circle in the user's text colour and a later step has no border, in system colours used
  only there. `build-tokens.py` allows `@media (forced-colors:active)` and system colours only
  inside it; `check-previews.py` renders every preview in forced colours and fails if two states
  look the same.
- **The Dialog (v0.4.0 and v0.5.0).** On a phone it ran edge to edge, as its `max-width` left out
  its padding and border; it now keeps `space-4` from each edge. Opened as a modal, it stood on the
  browser's own backdrop, 1.25:1 against the dimmed page in light and 1.03:1 in dark. The page
  behind it is now dimmed by the new `scrim` token, and the dialog's edge is `border-strong`, so it
  stands out 3:1 in both themes: in light by its face, in dark by its edge (no dimming lifts a dark
  dialog off a dark page). `check-contrast.py` holds it; `check-previews.py` opens each dialog as a
  modal and checks its margins and backdrop.
- **Vertical rhythm (v0.4.0 and v0.5.0).** The first item under a legend sat 16, 20 or 24px below
  it, the fieldset's padding plus the item's own margin; it now sits `space-3` below it, whatever
  it is. A note sat 4 or 8px under its group, as the Gallery and PieceMap kept a bottom margin; it
  now sits `space-1` under any group. `check-previews.py` measures both.
- **The steps from v0.2.0.** v0.3.0's entry had no "Moving to it": a tool on v0.2.0 had nothing
  to say it must put `ws-page` on `<body>`, rename five classes and drop its local rules. It now
  has them, every local rule named. v0.4.0's entry now says which of those rules do harm if kept,
  that the warnings take `ws-notice--warning` before the local headline colour goes (in the other
  order they turn grey), and that a header with one or two buttons needs no More….
- **`check-previews.py` let some mistakes through.** A broken font query passed as "no fallback"
  (every error was caught); a misspelt selector checked nothing and passed; the count of primary
  buttons counted pages, so it could never be zero; focusing the form only downwards never put a
  field under the pinned stage, so a lost `scroll-padding` passed; and on Windows a message quoting
  an icon crashed the run. Each now fails.
- **`tests/test-build-tokens.sh` proved less than it said.** Its CSS controls all used the class
  `.x`, which the prefix rule (v0.4.0) refuses, so each was refused whatever its own rule did. Each
  control now uses `.ws-x` and counts only if the build fails with its own rule's message.

### Added

- The `scrim` token: the page behind an open modal dialog.
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
  is behind it, not only the token pairs `check-contrast.py` lists.
- `build-tokens.py` also refuses a system colour, `color-mix()`, a gradient, a typed opacity, font
  size or line height, an at-rule but `@media` and `@supports` (no `@container`, no `@keyframes`),
  and any custom property the stylesheet sets but `control-h` on a touch screen.
- `check-previews.py` checks coverage: every class the stylesheet styles is shown by a preview
  and named in a doc, and every class a doc names exists. Twenty-two classes were named in no
  doc; each component README now names its classes, and the Field and Notice previews show
  `.ws-num` and `.ws-warning`.

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
  comes right after Redo. The theme toggle reads "Dark theme" and carries `aria-pressed`. A tool
  whose header holds no more than fits a phone's row (Skådis Air's holds the theme toggle alone)
  leaves out More… and the popover, and its buttons stay in the row on every screen.
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
- **Coming from v0.2.0:** take v0.3.0's steps first (below): its renames, and the local rules it
  names. Three of them do harm from this version on if they stay: `.ws-stage__view { position:
  relative }` unpins the phone's 3D view, `.ws-notice:empty { display: none }` takes an empty
  Notice out of the page, so it is never announced, and `.ws-header__name { margin: 0 }` pulls
  More… beside the name.
- **The warning headline.** Give each warning Notice `ws-notice--warning` first, then drop a local
  `.ws-notice strong { color: var(--warning) }`, which would turn an error Notice's headline amber.
  In that order: dropped while the warnings are plain `.ws-notice`, it turns their headlines grey.

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

### Moving to it

Added in v0.5.1: this entry had no steps. They come from the page Skådis Air built on v0.2.0
(`AlonRR/skadis-air` `b55c32d`, `web/index.html`), which shows what a tool on v0.2.0 had to add
itself. Copy `tokens.css`, `components/bundle.css` and `fonts/` from the tag, then:

- Put `class="ws-page"` on `<body>`.
- Rename the classes the system now has: `preview-message` to `ws-stage__message`, `plan-line` to
  `ws-plan__line`, `plan-actions` to `ws-plan__actions`, `hint-fine` to `ws-hint-fine` and
  `hint-touch` to `ws-hint-touch`.
- Give a warning Notice `ws-notice--warning`, and an error one `ws-notice--error`: the variant now
  colours the border and the headline.
- Delete every local rule the system now holds. In Skådis Air's page they were: `:root {
  color-scheme }` and `:root[data-theme='dark'] { color-scheme }`; `html, body { margin }`; `body {
  background; color; font }`; `input, button { font: inherit }`; `.ws-header__name { margin }`;
  `.ws-controls > :first-child { margin-top }`; `.ws-notice:empty { display: none }`; `.ws-notice
  strong { color }`, once the warnings carry their variant; `.ws-input[type='number'] { max-width }`;
  `.ws-sides { margin-top }`; `.ws-choice + .ws-caps { margin-top }`; `.ws-stage__view { position;
  overflow }`; `.ws-stage__view canvas { … }`; `.preview-message` and `.preview-message:empty`;
  `.plan-line`; `.plan-actions`; and `.hint-fine`, `.hint-touch` and their `@media (pointer:
  coarse)`.
- Keep only the page's own rules: in Skådis Air, `.tagline`, `.note` and the `[data-state]` colours.

Skipped, the hints both show and run together, the plan sentence runs to six lines and the
primary button is cut off.

## v0.2.0 (14 Oct 2026)

The part always fits the stage (D15): the tokens `stage-fit` and `stage-min-fill`.

## v0.1.0 (14 Oct 2026)

The first version: tokens, components and their previews, the fonts loaded once from `fonts/`
(D9), MPL-2.0 and CERN-OHL-S-2.0 in the REUSE layout (D8), and the checks.
