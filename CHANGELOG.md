# Changelog

What changed in each version, and how a tool that copies the files moves to it.

**Versions** follow [Semantic Versioning](https://semver.org), counted by what a tool must do,
not by the size of the change:

- A **patch** version (0.4.1) can be copied over the last one with no change to a tool's markup
  or CSS, and every page stays as it was or better.
- Anything a tool must follow is a **minor** version while the version is 0.x, however small.
  v0.5.0 is one: with the v0.4.0 markup, its stylesheet stretches the view choice over the 3D
  view.
- The version is in `tokens.json`, in the head of `tokens.css` and in `pyproject.toml`.
  `scripts/build-tokens.py` keeps them, this file and the tag in step, and refuses a tag whose
  entry here still says "unreleased".

**Each entry** says what the version is for, then:

- **Moving to it:** the steps a tool takes to follow, in order: the files to copy, then any
  change to its markup or script. Read it before copying a new version over an old one.
- **Changed, Fixed, Added:** what a tool sees, and why. An ID such as D39 points to the decision
  in [`docs/decisions.md`](docs/decisions.md).

**Tags.** Releases in this repository start at v0.6.0, and it holds the tags v0.1.0 and v0.2.0.
The tags v0.3.0 to v0.5.1 are not in this repository: they are kept on the owner's own forge,
and the entries below are their release notes.

## v0.8.1 (23 Oct 2026)

Skådis Air's request for two components (its A319), and the owner's answers D94 and D95 (23 Oct
2026). A patch, by the rule above: it adds what a tool may use, and a tool that uses none of it
copies the files and changes nothing.

### Moving to it

Copy `tokens.css` and `components/bundle.css` from the tag. To fold a field's help behind an "i",
follow the Help README; to show that a part is being rebuilt, the Workbench README's "While a part
is rebuilt". A tool whose script already marks its stage view `aria-busy` now sees its drawing dim
after 0.4s: add the ring's markup, and drop any rules of its own for the same thing.

### Added

- **Help: a field's help, folded behind an "i" beside its label (D94).** A quiet Button holding
  Codicons' info, named "About <label>" (`aria-label`), with `aria-expanded`, and `aria-controls`
  naming the field's `.ws-note`, which is `hidden` while folded and stays in the field's
  `aria-describedby`. It sits after its label in a `.ws-label-row`, or in a fieldset's
  `legend.ws-label-row`; it is a `control-h` square pulled into the label's line, so the row is
  as tall as the label. The script is the Disclosure toggle's lines, which a tool that has them
  already runs. It is the one button whose icon stands alone: `check-previews.py` fails an icon
  alone in any other, and measures the toggle's icon on its box's centre, within 0.75px in every
  engine.
- **The busy ring: a part being rebuilt says so (D95).** While the tool marks its stage view
  `aria-busy`, after `--busy-delay` (0.4s), so a quick rebuild never flickers, the part on show
  dims to `--opacity-disabled` and twelve dashes turn round a `control-h` ring on a
  `surface-raised` chip over it, in twelve steps a second (`--busy-turn`), never smoothly: in a
  page drawn in software, as a headless browser test draws, a smooth ring failed 28 of Skådis
  Air's 105 browser tests, and in steps none. With reduced motion it shows and does not turn; at
  rest nothing turns; a drag goes through it; it is `aria-hidden`, as the status line says it in
  words. `.ws-busy`, `.ws-busy__chip` and `.ws-busy__ring`, and the tokens `busy-delay`,
  `busy-fade` and `busy-turn`. `check-previews.py` marks each view busy and back, as a tool does.

### Changed

- **One motion and one gradient (D95).** DESIGN.md's "no gradients, no motion" allows the busy
  ring alone. `build-tokens.py` refuses any other animation or transition, an animation that does
  not turn in steps or that reduced motion does not stop, and a gradient, an angle, or a
  percentage other than 50% and 100%, anywhere but the ring.

### Fixed

- **A typed percentage fails the build.** The build's pattern for a typed length ended in a word
  boundary, which a `%` followed by a comma or a semicolon never has, so `width:37%` passed;
  `50%` and `100%` were the only ones typed, and stay allowed as geometry.

## v0.8.0 (21 Oct 2026)

The owner's answers A86 and D87 to D91, on an audit of `v0.7.0` against interface design and
engineering practice (21 Oct 2026). A minor version, by the rule above: a tool adds lines to its
script (D87) and writes each label's ellipsis as the one character (D89).

### Moving to it

Copy `tokens.css` and `components/bundle.css` from the tag. Then, in a tool whose header has
More…, add the lines the Header README gives to its script: they close the menu when an action in
it is picked (D87). A tool whose header has no More… (Skådis Air's) changes nothing.

In every label, write an ellipsis as the one character `…` (U+2026), never three full stops: the
button that opens a dialog, "Download the pieces…", and the plan bar's short label,
`Download<span class="ws-plan__long">&nbsp;the pieces</span>…` (D89).

### Changed

- **Picking an action in More… closes the menu (D87).** It stayed open over the 3D view, a third
  of it on a 375 × 667 phone, and Reset's change happened behind it. The Header README gives the
  lines for a tool's script, as the Workbench README does for View… (D42); the action's own
  handler runs first. `check-previews.py` runs them on every preview with More… and picks each
  action in turn; on the `v0.7.0` files each of the four picks left it open.
- **What a tool relies on is `tokens.css` (D91).** The README sent tools to `tokens.json` for the
  model colours, though no tool copies it. Now the README and DESIGN.md say a tool reads the
  values through `tokens.css`'s custom properties, the model colours as `--model-board` and the
  like, read from the page; `tokens.json` is the source, and its layout may change in any version.
  Neither tool reads `tokens.json` today, so neither changes.
- **One ellipsis, the character `…` (D89).** A button that opens a dialog ended in three full
  stops, "Download...", while More… and View… end in the one character, so a phone showed both
  forms side by side, and in the system's monospace font three full stops take three cells where
  `…` takes one. Now every label writes `…`: the Button and Workbench previews, and
  DESIGN.md, the Button and the Workbench READMEs, which say so. `check-previews.py` fails three
  full stops in a preview, or in what a doc tells a tool to write, outside its code blocks of
  script.

### Fixed

- **Icons sit on their labels' capitals (D88).** The font centres its icons 88.5 of its 1,950 units
  under its capitals, so every icon sat low: 1 to 1.75px in Chromium 156, 0.5 to 0.75px in WebKit
  27.2 and Firefox 157, measured on the drawn pixels. `tokens.css` now has `--icon-rise`
  (0.0454em), which `build-tokens.py` derives from the font file, and `.ws-ic` is raised by it.
  Now an icon is at most 0.75px from its label's capitals in Chromium on Windows and 1px in CI's
  Chromium on Linux, 0.5px in WebKit and Firefox on both, and 1px where the font-metric overrides
  are not read, as in released Safari: 244 icons an engine, on every screen the previews are drawn
  on. `check-previews.py` measures each icon against its label's capitals, within 1.25px. A tool's
  own CSS that moves `.ws-ic` should not.
- **The dark well is darker than the page (D90).** In dark, `surface-sunken` (`#1f2b35`) was the
  lightest surface, lighter than the panel it is drawn into (`surface-raised`, `#17212a`), so the
  board in Sides read as raised, the opposite of light, where it is the darkest. Now it is
  `#0c1217`: as in light, the well is darker than the page and the page than a panel, and its step
  down from the panel is light's, 1.15:1. Ink on it is 15.8:1 and `border-strong` 5.3:1.
  `check-contrast.py` holds the surfaces' order in every theme.
- **The plan sentence says it is an example first (A86).** The Workbench preview's sentence ended
  "Example wall: replace the sizes with yours.", the words the two-line clamp cuts first: on 14 of
  the 18 screens the preview is drawn on, 375 × 800, 768 × 264 and 960 × 800 among them, the clamp
  had already cut the sentence before them. Now it starts "Example wall.", a first sentence that shows whole on every screen, down to
  two lines of about 14 characters at 320px wide; DESIGN.md and the Workbench README say to lead
  with what must be read. A tool's own sentence is its own: put what must be read first.
  `check-previews.py` fails a screen where the first sentence's last word is cut.
- **The More… menu's items line up (A86).** Each button centred its label, and the menu stretches
  its buttons, so on a phone the four icons started from 217.8 to 251.3px across, 33.5px apart.
  Now each starts at the button's edge, the icons in one column. `check-previews.py` fails if the
  open menu's icons start more than 0.5px apart.

## v0.7.0 (21 Oct 2026)

The owner's answers D75 and D79: beside the sidebar the plan bar and the status bar keep one row,
as the plan bar does on a phone, and one height, derived from the tokens, replaces the three swept
breakpoints that decided when a short screen goes side by side. A minor version, by the rule
above: four tokens leave `tokens.css`, so a tool whose own CSS reads one must change, and beside
the sidebar a page now shows the primary button's short label and two lines of the plan's
sentence where it showed them whole, which is not "as it was or better" for every reader. No
markup changes, and no script.

### Moving to it

Copy `tokens.css` and `components/bundle.css` from the tag. A tool's markup and script do not
change: the status bar's two hints are already in one span, last in the bar, as the Workbench
preview and Skådis Air have them, and that span is what is cut short. A tool whose own CSS reads
`--plan-line-basis`, `--breakpoint-side-short`, `--breakpoint-side-size-w` or
`--breakpoint-side-size-h` drops it: they are gone.

### Changed

- **Beside the sidebar the plan bar keeps one row (D75, D79).** It wrapped in the stage's column:
  beside the full label the sentence took three lines or more (at 1280 × 360, 595px wide, three
  lines, the bar 81.5px), and narrower the button moved under it. Now, as on a phone, the sentence
  is at most two lines beside the primary button's short label ("Download...", D39); the rest of
  both is hidden from view only, so a screen reader hears them whole. The bar is one height on
  every screen side by side: 62.7px with a mouse, 69px on touch, the taller of `control-h` and
  the sentence's two lines. At 768px wide the sentence is 185px, two lines, 34 of its 139
  characters; three lines would show 57 and need the screen 18rem tall (D79).
- **Beside the sidebar the status bar keeps one row (D75).** Its parts stay whole but the last,
  the hints, which are cut short with an ellipsis where they do not fit: at 768px wide a mouse's
  hint shows 163 of its 502px. The whole hint stays in the page for a screen reader. The bar is
  41px on every screen side by side.
- **One derived height for side by side (D75).** A short screen went side by side from
  `breakpoint-side-short` (61rem), or from `breakpoint-side-size-w` by `breakpoint-side-size-h`
  (56.5rem by 25.5rem), values swept in each engine that moved with each engine's and system's
  text widths (D65); and from 61rem wide a screen went side by side at any height, 976 × 240 with
  the view at 21 %. Now a screen goes side by side from `breakpoint-wide`, or landscape from
  `breakpoint-side-min` (D41), and either way from H tall, the least height at which the header,
  the plan bar and the status bar leave the 3D view 40 % of the screen. `build-tokens.py` derives
  H from the bars' tokens, and a touch screen's taller `control-h` sets it:
  (48 + 2 × 12 + 44 + 1 + 32 + 2 × 4 + 1) / 0.6 = 263.3px, so 264px, 16.5rem. Phones held
  sideways from 800 × 360 now go side by side, their views at 56 % and more.
- **Tokens.** `plan-line-basis`, `breakpoint-side-short`, `breakpoint-side-size-w` and
  `breakpoint-side-size-h` are gone, with D52's and D54's breakpoints and the wrapping plan bar.
- **The checks.** `build-tokens.py` derives H and fails if the side-by-side query says another;
  its controls change a token H is made of (the header, a touch screen's `control-h`, the note's
  line) and must be refused, so a typed H cannot pass. `check-previews.py` holds the plan bar to
  one row and its sentence to two lines on every screen, draws 800 × 360, 844 × 390 and 900 × 400
  side by side, and the new edge: 768 × 264 on touch side by side, 768 × 263 and 767 × 264
  stacked. `scripts/sweep-side-by-side.py` now sweeps the rule over 140,021 screens a pointer,
  700 to 1,280px wide and 240 to 480px tall: every screen side by side exactly where the rule
  says, the bars one row of one height, the view at 40 %. In Chromium 156, WebKit 27.2 and
  Firefox 157 it passes with a mouse and on touch, the worst screen 768 × 264, 40.2 % on touch
  and 42.5 % with a mouse. On the `v0.6.0` stylesheet each check fails with its own message: the
  build on the query; the previews on 800 × 360, 844 × 390, 900 × 400 and 768 × 264, stacked,
  and on four side-by-side screens whose sentence took more than two lines; and the sweep on
  7,320 screens side by side where the rule stacks them (976 to 1,280 × 240 to 263), 39,744
  stacked where it puts them side by side, a plan bar 81.5 to 160.4px tall and a status bar of
  two rows, and 17,295 screens under 40 %, down to 21.1 % at 976 × 240.

## v0.6.0 (19 Oct 2026)

The owner's answers D47, D49, D41, D42, D52, D39, D51, D40, D55, D54, D57, D58, D59, D56, D61, D65,
D60, D68 and D69: a selected PieceMap cell says so with a mark, not by colour alone; the header
keeps the tool's name whole wherever the sidebar sits beside the stage, and on a phone puts the
version in More…; a narrow landscape screen stacks, and a short one unless it is large enough to
keep the 3D view at 40 % beside the sidebar; the open View… menu leaves the part in sight; on a
phone the primary button's short label leaves the plan's sentence room; the system states the
browsers it targets and checks its previews in Chromium, WebKit and Firefox, Playwright 1.64's
builds; the `hidden` attribute hides anything the system styles; the theme setter that runs before
the first paint is a file of the system, `theme-init.js`; a number field can have arrows, ↓ and ↑,
that move its value by its step and reach below zero from a phone's decimal keypad, the `Stepper`;
every field is exactly as tall as a button; a long list has a control of its own, the `Select`; and
the checks take their engine from `PREVIEW_ENGINE`, run on a pinned CI image, and draw the two
fallbacks in the target that no engine draws as it is. A minor version: D42 asks a tool's script
for a few lines, D39 and D51 change a tool's markup, D58 adds a file to copy and a line to the
head, and D56 and D69 add components a tool may take, D56's with its lines.

### Moving to it

Copy `tokens.css`, `components/bundle.css`, `theme-init.js` (new, D58) and `fonts/` from the tag,
`theme-init.js` beside `tokens.css`. Then, in the tool's script, close the View… menu when a view
is picked (D42), with the lines the Workbench README gives: a `change` listener on each
`.ws-stage__menu` that calls `hidePopover()` when the change comes from its `.ws-stage__views`
choice and the menu is open. Then three changes to the markup:

- **The theme setter (D58).** Load `theme-init.js` at the top of the head, before the
  stylesheets, replacing any script in the page that set `data-theme`:
  `<script src="theme-init.js" data-key="skadis-air-theme"></script>`, `data-key` naming the key
  the tool's own script stores the toggle's choice under ("light" or "dark"), so a choice already
  made still holds. Without `data-key` the key is `printable-parts-theme`. As a file it runs under a
  content security policy without `'unsafe-inline'`.

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

A tool that wants arrows on a number field, the `Stepper` (D56), adds them as below; nothing else
has to change for it:

- **The Stepper (D56).** For each such field, the label names the field by its `id` and is no
  longer wrapped round it, and the field and two Buttons go in a `div.ws-stepper`:
  `<label class="ws-label" for="clearance">Slot clearance (mm)</label><div class="ws-stepper"><input class="ws-input" id="clearance" inputmode="decimal" autocomplete="off" value="0" data-step="0.05" data-min="-0.5" data-max="1"><button class="ws-btn ws-stepper__btn" type="button" aria-label="Smaller slot clearance">↓</button><button class="ws-btn ws-stepper__btn" type="button" aria-label="Larger slot clearance">↑</button></div>`,
  then the note and the error as before. `data-step` is the setting's step, `data-min` and
  `data-max` its limits, and `data-on-step` marks a setting that keeps to its steps. The CSS comes
  with `bundle.css`; the tool's script takes the lines the Stepper README gives, which make the
  arrows and the arrow keys move the value and fire an `input` event, as typing does. A field that
  can go below zero can be `inputmode="decimal"` in a Stepper, as ↓ gets there. Skådis Air's own
  `.number-row` and `.number-step` rules give way to the bundle's. Its own stepping (`ab4b630`,
  `web/src/form.ts`) differs from the lines in four ways: at a limit the
  button says so (`aria-disabled="true"`) and a press fires no `input` event; ↑ on a value above
  the limit leaves it, where Skådis Air's moved it down to the limit (↓ still brings it back);
  and a value typed with more decimals than the step keeps them, 0.275 less 0.05 being 0.225,
  where Skådis Air's rounded to the step's, 0.23.

A tool with a long list to pick from, the `Select` (D69), adds it as below; nothing else has to
change for it:

- **The Select (D69).** The native `<select>`, given the class `ws-input` and wrapped in a
  `span.ws-select` inside its label:
  `<label class="ws-label">Printer<span class="ws-select"><select class="ws-input">…</select></span></label>`.
  The CSS comes with `bundle.css`, the chevron with the font; no script. Use it for a list longer
  than about seven short options, and `Choice` up to that. A tool that styled its own selects
  drops those rules.

### Changed

- **Every field is exactly `control-h` tall (D68).** A field's block padding was `field-pad-y`,
  6.4px, so with a mouse a field was 37.3px against a button's 36: its line (22.5px), the padding
  twice and its border. The padding is now derived from `control-h`, what it leaves of the line
  and the border, as a Disclosure summary's is, so every field is 36px with a mouse, 1.3px
  shorter than before, in Chromium 156, WebKit 27.2 and Firefox 157 alike; on a touch screen it is
  44px, as before. A Stepper's buttons, which stretched to the field, are 36px with it. The token
  `field-pad-y` is gone, and with it `--field-pad-y` from `tokens.css`: a tool whose own CSS reads
  it takes the field's padding from the bundle instead. `check-previews.py` now holds every field
  and a Stepper's buttons to exactly `control-h`, where it allowed them more; on the old stylesheet
  it fails every field and Stepper button with a mouse (16 in the Field, Stepper and Workbench
  previews, light, on a desktop). A tool copies the files; its markup does not change.

- **A Button with `aria-disabled="true"` looks disabled (D56).** It is faded and takes no hover, as
  a disabled one, for a button that must keep its focus while it cannot be used: a Stepper's at a
  limit. Disabled, the focused button lost its focus, to the page in Firefox (measured in
  Playwright's Firefox 157; Chromium and WebKit keep it). A button without the attribute is drawn
  as before.

- **The `hidden` attribute always hides (D57).** The browser's own `[hidden]{display:none}` is the
  weakest rule there is, so any class in the stylesheet that sets a display beat it: a Choice given
  `hidden` stayed on show, and Skådis Air wrapped its hidden Choice in a plain `div`. The
  stylesheet now restates it, `!important`, for anything with the attribute but
  `hidden="until-found"`, which keeps the browser's meaning. A tool can drop such wrappers;
  nothing else changes. `check-previews.py` gives every element of every preview the attribute in
  turn and fails if one is still drawn: on the old stylesheet 112 failures in the light theme on a
  phone and a desktop, among them every Choice and the wide View… menu, whose `display:contents`
  would beat even a rule without `!important`.

- **A short screen also goes side by side by its size (D54).** After D52 every short screen
  narrower than 61rem stacked, large phones held sideways among them, and stacked, a short screen
  pins nothing, so the part scrolled out of sight while a value was changed. A short screen now
  also puts the sidebar beside the stage from `breakpoint-side-size-w` wide and
  `breakpoint-side-size-h` tall (56.5rem by 25.5rem, 904 × 408, two new tokens), on its size
  alone, whatever the pointer. The values are swept, not guessed: `scripts/sweep-side-by-side.py`,
  new, draws every short screen a pixel apart, 768 to 1,280px wide and 360 to 480px tall, with a
  mouse and on touch, and fails if one side by side gives the view under 40 %. In Chromium 156,
  WebKit 27.2 and Firefox 157 alike on Windows, and in WebKit and Firefox on Linux, from 901px
  wide every short screen keeps 40 % from 403px tall; narrower, the plan bar takes one more row
  and would need 434px. The worst screen side by side is a 904 × 408 mouse window, at 40.7 %.
  Linux's Chromium sets the bars' text narrower: there every short screen keeps 40 % from
  896 × 378, and the worst gets 44.3 %. So 932 × 430 goes side by side again (47.2 %), with
  915 × 412 (44.9 %), 926 × 428 (46.9 %) and 956 × 440 (48.4 %), and 844 × 390 still stacks
  (45 %). `check-previews.py` now draws 904 × 408 and two windows that stack, 900 × 408 and
  904 × 400 (side by side, 36.1 and 39.5 % on Windows), and fails if a checked screen puts the sidebar
  anywhere but where its decision says; `build-tokens.py` fails if the side-by-side query lacks
  the new clause. A tool copies the files as before; its markup does not change.

- **The previews are checked in newer engines (D55).** The check and CI move from Playwright 1.56
  (Chromium 141, WebKit 26.0, Firefox 142) to 1.64: Chromium 156.0.8078.4, WebKit 27.2 and
  Firefox 157.0. Firefox 142 was older than every Firefox in the target but ESR 140 and had no
  `position-area`, so CI checked only the View… menu's fallback there; Firefox 157 anchors the
  menu, so the anchored menu is checked in all three engines, and the fallback ESR 140 shows is
  stated in README.md, "Browsers", but no job draws it any more. What the check leaves out moved
  with the engines: Playwright's Firefox now emulates a phone (`is_mobile`), so a phone there is
  no longer a touch window of the phone's size; Playwright 1.64 reads no engine's accessibility
  tree but Chromium's (through CDP), so in WebKit and Firefox the names are Playwright's reading
  of the page, and the run says so; WebKit 27.2 has `ascent-override`, which 26.0 lacked, so no
  job draws the labels as a Safari without it does. The label and mark scans read a control's
  place again after the screenshot, as Firefox 157 moves the page a pixel by itself a few frames
  after a scroll. Each engine checks 116 pages with 0 failing, and Chromium 156 measures every
  view, plan sentence and header name as Chromium 141 did. Nothing in the files a tool copies
  changes.

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
  pins nothing, so the view keeps `stage-phone-h` (45 %) and the page scrolls. So 844 × 390, a
  large phone held sideways, now stacks too; larger ones go side by side again by size (D54,
  above). `check-previews.py` now draws 800 × 360,
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

- **The controls' engine is `PREVIEW_ENGINE`, and CI runs on `ubuntu-24.04` (D61, D65).**
  `tests/test-check-previews.sh` took its engine from `BROWSER`, which many tools read as a web
  browser's command: in a shell with `BROWSER=true` it asked the check for an engine called "true",
  and every control failed. It now reads `PREVIEW_ENGINE`, Chromium when unset, as CI's preview
  jobs do, and runs one control again in a shell with `BROWSER=true`, which must be refused as
  usual. Every CI job ran on `ubuntu-latest`, which GitHub moves to a new image (Ubuntu 26, from
  19 Oct 2026); Linux Chromium's text widths already moved D54's measured edge once, so every job
  now runs on `ubuntu-24.04`, and a new image is a step of its own, with the sweep run on it.
  `tests/test-workflow.sh` refuses `BROWSER` and `ubuntu-latest` in the workflow, each with a
  control. Nothing in the files a tool copies changes.

- **One rule for each shared look (D44).** A cleanup of `bundle.css` that draws every preview as
  before: the hover tint, the selected look and a selected label's bold are one rule each,
  `.ws-plan__long` and `.ws-sr` share theirs, and two declarations that never applied go. What a
  tool can read of it: `control-h`'s touch value, `tap`, is set in `tokens.css` now, in
  `@media (pointer: coarse)`, not in `bundle.css`, so a page that loads `tokens.css` alone gets it
  too; `--control-pad-y`, new and derived, is what `control-h` leaves of a line, a Disclosure
  summary's block padding and, less its border, a field's; and a Choice, Sides toggle, tile,
  PieceMap cell, step button, Disclosure summary or Select with `aria-disabled="true"` takes no
  hover tint, as such a Button already did. Before and after, every preview's screenshots are the
  same pixel for pixel in Chromium 156, WebKit 27.2 and Firefox 157 and in the fallback pass (544
  pairs), and every computed style of every preview in Chromium, at rest, hovered and focused (2.9
  million values), differs only by the new property and that hover. `build-tokens.py` now refuses
  any custom property `bundle.css` sets, and a token that reads one `tokens.css` lacks. A tool
  copies the files; its markup does not change.

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

- **`Select`, a long list to pick one from (D69).** The native `<select>`, a Field's input drawn
  from tokens: exactly `control-h` tall (`tap` on touch), with a field's border, focus ring, error
  outline and fading, tinted on hover, and its `color-scheme` the page's, so the list the browser
  opens follows the theme. `appearance: none` takes away the browser's own arrow, which each
  engine draws its own way, WebKit's 42.5px tall with a mouse; the chevron is the Codicon
  `chevron-down` (U+EAB4) from the font, drawn by the wrapper's `::after` in a `control-h` square
  at the select's end, over the select: text, so it takes `ink` and, in forced colours, the user's
  text colour, where an image or a mask drawn with a background colour would not; it lets a press
  through, and its empty alternative text keeps it from a screen reader. DESIGN.md's rule:
  `Choice` for up to about seven short options, `Select` for longer lists. `check-previews.py`
  check 35 fails a select outside a `.ws-select`, a chevron outside the font or not in the select's
  text colour, and, measured on the pixels that change when it is hidden, one that draws nothing,
  lies over the text or takes the press, also in forced colours; the hover, height, ring, disabled
  and invalid checks take the select in.

- **`Stepper`, a number field with ↓ and ↑ (D56).** Modelled on Skådis Air's number field:
  the field, a Field's `inputmode="decimal"` input, and two Buttons after it in a row, reading ↓
  and ↑, from the font's arrows, and named `Smaller <label>` and `Larger <label>` (`aria-label`),
  so DESIGN.md's rule that an icon never stands alone holds: the arrow is text. The buttons are
  `control-h` tall, as the field is (D68), so they line up with it, and are at least `control-h`
  wide, so a touch target each way: at Skådis Air's
  `space-2` padding alone they were 27px wide. On a narrow sidebar the field gives way, so the row
  fits a 320px screen. A `type="number"` field in a Stepper loses the browser's spin buttons:
  `appearance:textfield` hides them in Firefox, the `::-webkit-` spin buttons' rule in Chromium and
  WebKit, neither alone in all three (measured). The README gives the lines for the tool's script:
  ↑, ↓, ArrowUp and ArrowDown move the value by `data-step`, onto its steps where it has
  `data-on-step`, read "," as a decimal point, stop at `data-min` and `data-max`, where the button
  says so (`aria-disabled`) and keeps its focus, and fire one `input` event per change and none at
  a limit; ↓ from 0 goes below zero where `data-min` is below it, the way to a negative value from
  a decimal keypad, which has no minus sign (Skådis Air's slot clearance goes to −0.5 mm). The
  Workbench preview's track width is a Stepper, so the row is checked in a sidebar on every
  screen. `check-previews.py` fails if a Stepper is not its field and two Buttons, ↓ then ↑, named
  for the field and outside its label, or if a button is narrower than `control-h` or does not
  line up with the field; and it runs the README's lines on the previews and presses every
  Stepper's arrows and keys, real key presses, in the field as it is and as a `type=number` one,
  failing on a wrong step, a step not onto the steps, a comma not read, a limit passed or not
  said, an `input` event missing or extra, a negative value out of reach, or spin buttons kept.
  On the stylesheet before and the README without its lines, the Stepper preview failed 123
  times in the light theme on a phone and a desktop; each failure is held to a control.
- **`theme-init.js`, the theme setter (D58).** The script that sets `data-theme` on `<html>`
  before the page is first drawn, so a dark screen never flashes light, was each tool's own,
  Skådis Air's in its page; it is now a file of the system, loaded first in the head (above). It
  sets the theme stored under its key, "light" or "dark", and with nothing stored, any other value,
  or storage missing or refused, the system setting's: `tokens.css` themes the page through
  `data-theme` alone, light without it, so with the attribute unset a dark system would get a light
  first paint. Its key and values are Skådis Air's (`data-key="skadis-air-theme"`). Licensed
  MPL-2.0, as code. `check-previews.py` runs it in a served page in each engine, in eight cases
  (stored dark and light, nothing stored on a dark and a light system, an unknown value, storage
  refused on a dark and a light system, a key of the tool's own), and fails if `data-theme` is not
  the case's when the script has run, before the stylesheet is read, or if the script throws; each
  case is held to a control.
- **Two patterns in the component READMEs, no new CSS.** Choice: a switch between groups, a
  Choice of the groups above one Choice per group, the others `hidden` (D57), with the lines a
  tool's script needs. Disclosure: a toggle that sits in a row of buttons, a Button with
  `aria-expanded` and `aria-controls` whose script flips both and the section's `hidden` (D59).
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
  accessible names are read from each engine's own tree (Chromium's only, since D55, above), and
  each focused control is scrolled into view as Tab brings it, as WebKit's `focus()` scrolls
  nothing. On the files of `b90b5c5`, WebKit 26.0 and Firefox 142 each check 116 pages with 0
  failing; the engines checked since are under D55, above.
- **`check-previews.py --fallbacks` (D60).** Since D55 every engine CI runs anchors the View… menu
  and reads the font-metric overrides, so two fallbacks in the target went unchecked: the menu
  where there is no `position-area` (Firefox ESR 140), and labels without the overrides (released
  Safari reads none of `ascent-override`, `descent-override` and `line-gap-override`, so all three
  go, not `ascent-override` alone). The option renders every preview from copies of `tokens.css`
  and `bundle.css` with the `@supports (position-area: …)` block and the three descriptors taken
  out, as such a browser reads them, and runs every check on them; a CI job of its own runs it in
  WebKit, Safari's engine, where alone the labels are measured. On these files it finds nothing to
  fix: in WebKit 27.2 the menu opens on the screen with its items on all 32 screens that show it,
  320px wide among them, and a pick closes it; all 920 labels are within 1px of centre, and the
  Sides ticks within 0.25px (Firefox 157 draws the same within 1px). Chromium 156 without the
  overrides sets 524 of the 920 labels 1.75 to 2px high, as it rounds the font's own ascent and
  descent to whole pixels: a drawing no browser in the target makes, as Chrome reads the
  overrides, so there the pass leaves labels out and says so. The run fails if there is nothing to
  take out, if a page still anchors the menu or loads a face with an override, or if no menu opened
  unanchored, and `tests/test-check-previews.sh` holds each to a control, with a menu that runs off
  the screen only where nothing anchors it, which the main run passes. Nothing in the files a tool
  copies changes.

## v0.5.1 (17 Oct 2026)

The fixes from the second review of v0.5.0 that need no decision (A38). A patch: copy the files
over v0.5.0; no change to a tool's markup or CSS.

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

From the review of 16 Oct 2026 and the owner's answers D25 to D33, A34 and A35.

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
