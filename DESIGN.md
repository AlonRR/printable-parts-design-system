# Design guidance

The rules for every tool built on this system. Values live in `tokens.json`; this page says how to
use them. An ID such as D26 points to the decision behind a rule, in
[`docs/decisions.md`](docs/decisions.md).

## One base, two projects

The system serves browser tools that generate printable parts. The **base**, everything outside
the two project sections below, is shared: the workbench layout, Choice buttons, Fira Code,
Codicons, rounded corners, light and dark themes, save and load, live updates. Each **project**
adds only its own cover, model colours, step names, wording and a few components. A new generator
starts from the base and adds one more project section.

- **Parametric window sealer** (AlonRR/parametric-window-sealer): panels and seals for the gap a
  window leaves. Model colours `model-panel`, `model-joint`, `model-tape` and `model-tpu`, with
  `model-outline` edges. Steps: Opening, Window, Fittings, Seal, Printer and style. Cover: `Cover`.
- **Skådis Air** (AlonRR/skadis-air): light, tileable SKÅDIS-compatible pegboards and connectors.
  Model colours `model-board` and `model-board-outline`. Steps: Board, Size and sides, Mounting,
  Printer. Components: `Sides`. Cover: `CoverSkadisAir`.

A **cover** is fixed-size artwork (960 × 288 px) for use outside the tool: the gallery card, the
repository's social preview, a README banner. It does not reflow, so it never appears in the tool
itself.

Colour roles:

- `surface` for the page and the stage; `surface-raised` for the header, sidebar, dialogs and
  groups; `surface-sunken` for a well drawn into a panel, such as the board in Sides; `ink` for
  text.
- The surfaces keep their depth in both themes: the well darker than the page, the page darker
  than a panel (D90). `check-contrast.py` holds the order.
- Notes, units and errors in `ink-muted` and `error`.
- Never put `ink-muted` or `error` on `action` or on a model colour. `ink-muted` on `action-tint`
  (a hovered step) is a pair `check-contrast.py` holds to 4.5:1.

## The tool is a workbench

### Layout

- **The wall is the page.** The 3D stage is the biggest thing on screen and always visible.
  Controls live in a sidebar beside it. The result is never below the inputs (`Workbench`).
- **The part always fits the stage (D15).**
  - It is framed to fill `stage-fit` of the stage whenever the part or its size changes.
  - When the stage changes size, the camera keeps the user's angle and pulls back only as far as
    the whole part needs to fit again.
  - Zooming out stops at `stage-min-fill`, and panning cannot move the part off the stage.
  - "Reset view" returns to the first view.
  - A browser test checks that the part's outline lies inside the stage on a phone and a desktop,
    and after a resize.
- **Header.** A slim `header-h` bar with the name, Undo, Redo and Reset, Save project, Load project
  and the theme toggle.
  - Below `breakpoint-header` (64rem), everything but Undo and Redo sits in one labelled "More…"
    menu (D28), the tool's version with it (D51). Its items line up, their icons in one column
    (A86), and picking one closes it, so what it does shows at once (D87).
  - `breakpoint-header` is wider than the layout's breakpoint, so the tool's name is whole
    wherever the sidebar sits beside the stage (D49).
- **Stage and status bar.** The stage fills the rest, with a status bar (`status-h`) under it
  showing sizes, units and one hint naming the gestures the tool supports: for a mouse "Left
  drag: orbit · Scroll: zoom · Arrow keys: turn", for a touch screen "Drag: turn · Pinch: zoom",
  never both. Beside the sidebar the bar is one row, and a hint too long for it is cut short
  with an ellipsis, whole for a screen reader (D75).
- **Over the view** sit "Reset view", "Zoom in" and "Zoom out" at the top right, and a Front ·
  Back · Top choice at the bottom left (D30). On a phone or a short screen, "Reset view" and
  "View…", a menu holding the rest, so the view stays clear for pinch and drag (D36).
- **Sidebar.** `panel-width` wide. Collapsing it from an edge toggle is planned, not yet a
  component.

### Behaviour

- **Light or dark, as the system says, until the user chooses.**
  - The page follows the system setting until the header's "Dark theme" toggle is used: a
    `button` with `aria-pressed`, pressed while the page is dark.
  - The choice is then remembered in this browser and wins over the system setting. Where the
    browser keeps nothing (a private window), it lasts while the page is open.
  - The theme is set on `<html>` before the page is first drawn, so a dark screen never flashes
    light, by `theme-init.js`, which the tool loads first in its head (D58): the stored choice, or
    else the system setting, as `tokens.css` themes the page through `data-theme` alone.
  - Everything that follows the theme, the 3D view included, watches `data-theme`, never the
    system setting itself.
- **One form first; numbered steps when it outgrows a screen (D31).**
  - A short tool is one form in the sidebar.
  - A longer one gets a step rail across the top of the sidebar, one step at a time. Each step
    button shows its number and name ("2 Window"); the current one carries
    `aria-current="step"`, and a done one says "done" to assistive tech.
  - The sidebar shows the current step's title and fieldsets, then Back and Next.
  - The stage shows the whole part at every step and highlights what the step changes. Each
    tool's steps are in its project section.
- **Open on a working example.** The first visit shows an example and says so, first in the plan
  sentence ("Example wall."), as its two-line clamp cuts the end (A86); presets replace every
  value in one tap. A short welcome dialog gives a four-step quick start and says everything
  runs in the browser, then never shows again.
- **Live, no Apply.**
  - Every change updates the stage at once.
  - An invalid value keeps the last good part, marks the field and says what to fix.
  - A build that can take longer than about 100 ms runs off the page's main thread, so typing
    never stalls; the last good part stays on the stage, with the stage message "Updating…",
    until the new one is ready.
- **Show only what applies.** Track depth appears only for an edge in a track, hose size only for
  a hose. Rarely changed settings go in an "Advanced" `Disclosure` at the end of the step. Hide
  what does not apply with the `hidden` attribute, which hides anything the system styles (D57).
- **Pick-one options are buttons with a radio mark.**
  - Use `Choice` for up to about seven short options: every option is a button with a small
    radio circle at its left, all in sight. A longer list, such as printer models, is a `Select`,
    the native `<select>` with a chevron from the font (D69).
  - The chosen one is `action-tint` with an `action` ring and a bold label, and its circle holds
    an `action` dot, so it reads as selected without relying on colour (D26).
  - A selected `PieceMap` cell, one of a pick-one, shows the same dot (D47).
  - A tick means pick several (the `Sides` toggles); never use a tick for pick-one.
  - For picture options use `Gallery`, not a drop-down.
- **Projects can be saved.** Save project and Load project write and read one file; undo and redo
  cover every change.
- **Measuring help is beside the field.** A "How do I measure?" link opens the guide with its
  drawing as a panel; the user returns to the same spot.

### Phones and small screens

- **The phone stage.**
  - The 3D view alone is pinned at the top, `stage-phone-h` (45 % of the screen).
  - Under it the plan bar, pinned too, is one row: the sentence, at most two lines, beside the
    primary button, which stays in reach.
  - The button shows a short label ("Download…"), the rest of it hidden from view only, so its
    name stays whole and the sentence keeps `plan-line-min` (D39).
  - "Reset view" sits on the view. The status bar and the sidebar scroll beneath, and a focused
    field always lands below the pinned part.
- **A short or zoomed screen** (under `breakpoint-short`) pins nothing.
- **Beside the sidebar the bars keep one row** (D75): the plan bar as on a phone, the sentence at
  most two lines (D79) beside the short label, and the status bar, its hint cut short with an
  ellipsis and whole for a screen reader. So the header, the plan bar and the status bar are one
  height each on every screen side by side: 48, 62.7 and 41px with a mouse, 48, 69 and 41px on
  touch, the plan bar's row the taller of `control-h` and the sentence's two lines.
- **Where the sidebar goes.** It sits beside the stage on these screens, and stacks under it on
  every other:

  | Screen | Side by side from |
  | --- | --- |
  | At least H tall | `breakpoint-wide` (56rem) |
  | Landscape (`landscape-ratio` or wider), at least H tall | `breakpoint-side-min` (48rem) (D25, D41) |

  H is the least height at which those bars leave the 3D view 40 % of the screen (D75):
  (`header-h` + 2 × `space-3` + the taller of `control-h` and two lines of the note style +
  `status-h` + 2 × `space-1` + 2 × `line`) / 0.6, taken for a mouse and for a touch screen,
  whose taller `control-h` sets it, and rounded up to a whole pixel: 16.5rem (264px).
  `scripts/build-tokens.py` derives it from the tokens, never typed, and fails if the
  stylesheet's media query says another. A landscape or short screen that stacks pins nothing,
  so the view keeps 45 % and the page scrolls. So a phone held sideways, 800 × 360 and larger,
  goes side by side, its view 56 % and more, and the least screen side by side, 768 × 264, keeps
  40.2 % on touch.
- **Menus.** Open, the More… and View… menus end at the screen's bottom edge and scroll inside.
- **Touch.** Touch targets are `tap` (44px) or more; rotate and zoom use drag and pinch.

## Controls

- **Height.** Buttons, Choice buttons, toggles, rail buttons, inputs and selects are exactly
  `control-h` tall (36px), and `tap` (44px) on touch screens, its touch value, set once in
  `tokens.css`. A field's block padding is what `control-h` leaves of its line (`control-pad-y`,
  derived) less its border, never a padding of its own (D68). PieceMap
  cells and Disclosure summaries are at least that tall.
- **A help toggle** is a `control-h` square, pulled into its label's line by `control-pad-y`
  above and below, so a row with one is as tall as the label (D94).
- **A `Stepper`'s buttons** are `control-h` tall, as its field is, so they line up with it, and
  at least `control-h` wide, so a touch target each way (D56, D68).
- **Keeping focus while unusable.** A button that must keep its focus while it cannot be used, a
  Stepper's at a limit, says so with `aria-disabled="true"` and is drawn as a disabled one.
  Disabled, the focused button would lose its focus: Firefox drops it to the page.
- **Rings.** Focus, selected outlines and the chosen radio's ring all use `ring`. The radio's
  offsets are derived from it, so choosing an option never moves its label.
- **Gaps.** Icons sit `icon-gap` from their label; a radio and a Sides box, drawn with a `ring`
  border, sit `icon-gap` plus `ring` from theirs.

## Content fundamentals

- Say "you" and use plain words: panel, piece, strip, edge, seal. No jargon.
- Units in every label: `Width (mm)`. Metric by default, millimetres for sizes. Imperial stays
  available as a setting next to language, for people who read inches more easily (D33).
- Be honest about what is untested: the joint fit and track sizes are "starting values that a
  test print still has to confirm". Put it in a note, not a tooltip.
- Errors say what to fix: "Fix the marked fields to see the plan." Warnings name the choice that
  resolves them.
- Sentence case for headings and buttons. End a button that opens a dialog, or a menu, with an
  ellipsis, the one character "…", never three full stops ("Download the pieces…", "More…"), its
  short label in the plan bar too ("Download…", D39, D75, D89).
- Say where the work happens: "Everything runs in your browser; nothing is uploaded."

## Visual foundations

- **Quiet, light and soft-cornered.** Light surfaces, a hairline `divider` between regions and
  `border` round groups, one accent. Corners: `radius-sm` (8px) on buttons, inputs, tiles and
  notices; `radius-md` (14px) on groups and dialogs. No drop shadows, no gradients, no motion (the
  chosen radio's inner ring is an inset shadow, drawn inside it), but one thing: the busy ring
  over a part being rebuilt (Workbench, D95) turns, and its dashes are a gradient from `border`
  to `action`. It waits `busy-delay`, so a quick rebuild never flickers; turns in twelve steps a
  second, never smoothly; stops with reduced motion; and nothing turns at rest. The build refuses
  any other motion or gradient.
- **One filled colour.**
  - `action` fills only the primary button, so the one filled thing on a screen is the next step,
    and draws the focus ring (solid 2px, 2px offset).
  - Every selected state is `action-tint` with an `action` ring and border: the chosen Choice, a
    pressed Sides toggle, the active step and a selected tile, in bold; and a selected piece,
    whose bold already says it has its own fill, with the radio's dot instead (D26, D47).
  - The marks inside them, the radio's dot and the Sides box, are the only other `action` fills.
  - `error` outlines a field, and the message explains it. Colour is never the only signal.
- **Control borders are `border-strong`** (3.5:1 or more); `border` and `divider` only separate.
- **The `model-*` colours are materials in the stage**, not UI: never use them for text, borders
  or a control's own fill. A drawing of the part, such as a `Gallery` tile, may use them.
  `model-tape` orange means seal.
- **Section labels** in the sidebar use `.ws-caps`, the `label-caps` style (uppercase, tracked,
  `ink-muted`). The status bar takes the same size in normal case, so its hints read as sentences.
- **Guide drawings** are inline SVG in `currentColor` with arrow markers.

## Type

- **One family for everything:** FiraCode Nerd Font (`ui`), a monospace face with icons built in.
  Fewer typefaces keep the interface calm, and a fixed-width face lines numbers up in columns and
  keeps 0/O and 1/l/I distinct. Do not mix in another family; hierarchy comes from size and
  weight.
- **Styles:** `title`, `section`, `step`, `body`, `legend`, `note`, `label-caps`, `code`. A page of
  text goes in `.ws-text` (body type, at most `measure` wide). Text is 15px (`body`) and notes
  13px; keep notes to short sentences, as a monospace line holds fewer characters.
- **Vertical centring is fixed at the font, not per component.** The `@font-face` rules in
  `tokens.css`, written by `build-tokens.py`, set `ascent-override` 96.85% and `descent-override`
  26.23% for Regular (97.08% and 26.00% for Bold; line gap 0), computed from each font file's cap
  height, so capital letters sit on the centre line of any line box. Any new font needs its own
  pair: ascent minus descent equals the cap height, and ascent plus descent keeps the line
  height. Do not nudge text with padding. Chromium rounds the ascent and descent to whole pixels,
  so capitals can sit up to about 1.2px off centre; the check allows 1.5px. Released Safari reads
  none of the overrides, so there the font's own metrics place the capitals: within 1px in WebKit
  27.2, which `check-previews.py --fallbacks` measures (D60).
- **Icons sit on the capitals, fixed at the font too (D88).** The font centres its icons 600 of
  its 1,950 units up, and its capitals at 688.5, so an icon sat 88.5 units (0.68px at 15px) under
  its label's capitals, and Chromium, rounding, drew it up to 1.75px under. `build-tokens.py` derives
  `--icon-rise` (0.0454em) from the font file, the Codicons' median centre against half the cap
  height, and `.ws-ic` is raised by it (`top`, which Chromium draws a whole pixel, not
  `translate`, which it draws half). `check-previews.py` measures each icon against its label's
  capitals on the pixels, within 1.25px: 0 to 0.75px in Chromium 156, WebKit 27.2 and Firefox
  157, 1px in CI's Chromium on Linux, and 1px at most where the overrides are not read.
- **Ligatures** are on in text, so `=>` and `->` join, and off in inputs, numbers, file names, the
  status bar and the plan line (`ws-input`, `code`, `ws-num`, `.ws-status` and `.ws-plan__line`
  turn them off, and a check holds it, D29), so a value never changes shape. Use real arrows (→)
  in labels: "Next: Fittings →". Numbers use the slashed zero.

## Accessibility

- **Native elements:** `fieldset`, `legend`, `details`, `dialog`, `select`. Pick-one options are
  radios underneath, shown as `Choice` buttons; the picture and map pickers (`Gallery`,
  `PieceMap`) are buttons with `aria-pressed`, one pressed at a time. Every control has a visible
  label.
- **State never relies on colour alone:** errors have text, the active step has
  `aria-current="step"` and a ringed, bold button, selected tiles use `aria-pressed`. In forced
  colours (Windows High Contrast and the like) the browser keeps only the user's system colours,
  so the stylesheet uses them, there alone, to give each state its own look: the chosen radio a
  filled circle, a step not reached without the border of a done one.
- **Live regions:** announce changing results (the plan line, errors, download status) with
  `aria-live="polite"`. Keep an empty live region in the page, collapsed, never `display:none`,
  so it is announced when it fills. Link a field's error and note to it with
  `aria-describedby`.
- **The stage works without a pointer** (D30, WCAG 2.1.1 and 2.5.7).
  - Every move is a press: Reset view, Zoom in, Zoom out and Front · Back · Top.
  - On a phone or a short screen all but Reset view are in the View… menu, which opens below the
    view, over the plan bar, so the part stays in sight; the tool's script closes it when a view
    is picked (D42).
  - The focused view, ringed inside its edge, turns with the arrow keys and zooms with + and −.
  - It is an image named for the part ("The wall in 3D") and described by the plan line, its
    text equivalent, which says pieces, ports and seal.
- **Numeric fields:** `inputmode="decimal"` for a value that cannot go below zero. One that can is
  a `Stepper`, whose ↓ goes below zero, or without the arrows `type="number"`, as the decimal
  keypad on a phone has no minus sign (D56). "," is read as a decimal point as well as ".".

## Iconography and logo

- Icons are Nerd Font glyphs. Prefer the thin-line Codicons (`cod-`), the lightest weight here, and
  use one set throughout (see `Icons`); Font Awesome (`fa-`) is solid and heavier.
- Real Regular and Bold weights are bundled, so bold text is a true bold:
  `<span class="ws-ic" aria-hidden="true">&#xeb4b;</span>Save`.
- Every icon sits before a text label and is `aria-hidden`; an icon is never the only thing that
  says what a button does, but in one place: a help toggle, the "i" beside a field's label that
  shows and hides its help (`Help`, D94). It repeats beside every field, where a word would
  repeat a dozen times; "i" is the most common sign for "about this"; and its `aria-label`
  ("About thickness") says what it opens. `check-previews.py` fails an icon alone anywhere else.
- An arrow from the font's arrows (← ↑ → ↓) is text, not an icon: a `Stepper`'s buttons read ↓
  and ↑ alone, and their `aria-label` ("Smaller width") says what they do, so the rule holds
  (D56).
- Common code points: save eb4b, load eaf7, download eac2, undo eae2, redo ebb0, reset eb37, theme
  eac6, tick eab2, a Select's chevron eab4, a help toggle's info ea74.
- There is no logo. The tool's name is set in the `step` style, and in `legend` below the
  breakpoint.

## Project: Skådis Air

- **Voice.** Short and plain, like the page: "Download STL", "Reset view", "= 6 tiles". Say what
  is untested: every number marked "to confirm" is a starting value until the fit coupon has been
  printed. Sizes in mm, in 40 mm steps, with the tile count beside the field.
- **Steps.** Board (solid, lightened or skeleton; list only the types that are built), Size and
  sides, Mounting (screw holes in the corner tiles, countersunk by default; optional 20 mm
  standoffs on the back), Printer (bed 200 × 200 mm by default, custom size beside it).
- **Stage.** The board is shown as it hangs: upright, front toward you, slots vertical, in
  `model-board` with `model-board-outline` edges. Drag turns it, wheel or pinch zooms, "Reset
  view" returns. One "Download STL" button sits under the preview.
- **Sides.** Open or closed is chosen side by side with `Sides`: four toggles round a small drawing
  of the board. A single panel is open all round by default; a wall is closed round its outer
  edge.
- **Advanced.** Slot clearance, chamfer and corner radius are folded under an "Advanced"
  `Disclosure`.
- **Warnings.** A board larger than the bed, or a thickness outside 4 to 5.5 mm, shows a `Notice`
  in `warning`. It warns and never refuses.
- **Brand.** Say "SKÅDIS-compatible". The page carries the line that it is not made, endorsed or
  supported by IKEA; no IKEA logo, colours or wordmark.

## Project: Parametric window sealer

- **Voice.** Panel, piece, strip, edge, seal.
- **Steps.** Opening, Window, Fittings, Seal, Printer and style. `model-tape` orange means seal.
- **Stage.** The wall seen from the room, with `PieceMap` to pick one piece.

## Reference implementations

What a tool needs beyond the stylesheets is code, and the code stays in the tools: this repository
holds no TypeScript (D19). Skådis Air built each piece first; the window sealer copies them and
renames what names Skådis Air. The links are pinned to `AlonRR/skadis-air` at `b55c32d`, its
`main` on 15 Oct 2026.

- **The theme.** `theme-init.js`, in this repository (D58), sets `data-theme` before the page is
  drawn ("Light or dark", above); a tool copies it and loads it first in its head (README, "Using
  it in a tool"). [`web/src/theme.ts`](https://github.com/AlonRR/skadis-air/blob/b55c32d/web/src/theme.ts)
  keeps it in step and works the toggle, storing the choice under the key the script tag names
  (`skadis-air-theme`), and survives storage that is missing or refused.
- **The part always fits the stage.**
  [`web/src/framing.ts`](https://github.com/AlonRR/skadis-air/blob/b55c32d/web/src/framing.ts)
  works out how far the camera stands so the part spans `stage-fit` of the stage, and where
  zooming out stops (`stage-min-fill`), from the eight corners of the part's bounding box as the
  camera sees them;
  [`web/test/framing.test.ts`](https://github.com/AlonRR/skadis-air/blob/b55c32d/web/test/framing.test.ts)
  holds both to three.js's own projection. Skådis Air switched panning off, which the rule allows.
- **The workbench's browser test.**
  [`web/e2e/workbench.spec.ts`](https://github.com/AlonRR/skadis-air/blob/b55c32d/web/e2e/workbench.spec.ts),
  8 tests (12 runs, as the four framing tests run on a phone and on a desktop): the part framed
  to `stage-fit` and inside the stage, pulled back inside after a resize, zoom out stopping at
  `stage-min-fill`, "Reset view" framing it again, the stage beside the sidebar on a wide screen
  and on top at 45 % of the height on a phone, and the theme following the system until chosen,
  then remembered.
- **Copying the system in.**
  [`scripts/design-system/copy-design-system.sh`](https://github.com/AlonRR/skadis-air/blob/b55c32d/scripts/design-system/copy-design-system.sh)
  copies `tokens.css`, `components/bundle.css` and `fonts/` from a tag's commit, byte for byte,
  and checks each file against it; the page serves them unchanged from `web/public/design-system/`
  (README, "Using it in a tool").

## Rules for changing the system

- **No value is typed twice.** Colours, sizes, gaps, the ring width, the control height and the
  breakpoints live in `tokens.json`; components read them as variables.
- **Run the checks after any change.** Four scripts keep the system honest, each held to its own
  controls in `tests/`; what each one fails on is under "The checks", below.
- **Write a preview for every new component**, and name its classes in its README.
- **Every change a tool can see goes in `CHANGELOG.md`** under the next version, with how a tool
  moves to it. What a tool can see: the files it copies, `tokens.css`'s custom properties among
  them, the classes and markup the components give, and the lines of script their READMEs give.
  `tokens.json` is the source, which no tool reads; a change to its layout alone is none (D91). The version lives in `tokens.json` and `pyproject.toml` and heads `tokens.css`;
  the build keeps them, the changelog and the tag in step (D32). While the version is 0.x, a
  change that breaks a tool's markup or CSS raises the minor version.

## The checks

### `scripts/build-tokens.py`

Rebuilds `tokens.css` from `tokens.json`, a token's touch value in `@media (pointer: coarse)`,
and works out each font's vertical-centring overrides from its cap height, and the icons' rise
onto the capitals (D88). It fails if:

- `bundle.css` types a value a token holds: a colour in any notation (`color-mix()` too, and a
  system colour outside the forced-colours query), a gradient, a length (beyond a few geometric
  ones such as `100%`, and the busy ring's angles and percentages, D95), a font family, size,
  weight, line height or tracking, or an opacity;
- anything moves but the busy ring (D95): an animation or a transition outside a view marked
  `aria-busy`, an animation that does not turn in steps, or one that
  `(prefers-reduced-motion:reduce)` does not stop; a gradient anywhere but the ring;
- `bundle.css` uses a custom property `tokens.css` does not define, or sets one (a touch
  screen's `control-h` is the token's touch value, which `tokens.css` sets), or a token in
  `tokens.json` reads one `tokens.css` does not define;
- `bundle.css` uses an at-rule other than `@media`, `@supports` and the busy ring's
  `@keyframes ws-busy-turn`, a breakpoint `tokens.json` lacks, or a header rule at the layout's
  breakpoint instead of `breakpoint-header`;
- `bundle.css` declares a font of its own (the fonts load once, through `tokens.css`, D9);
- a wide-screen rule is undone by a later rule outside the media query;
- a grid popover has no `align-content`, which WebKit stretches;
- a type style asks for a weight no font file ships, or an icon draws past its advance;
- a document in `fonts/` links out of `fonts/` or to this repository (D24);
- the versions, the changelog entry and the tag are out of step, or a class lacks the `ws-`
  prefix (D32).

`tests/test-build-tokens.sh` proves each of these fails.

### `scripts/check-contrast.py`

Checks every theme: text pairs need 4.5:1; borders, focus rings and outlines 3:1; each part in the
stage shows against it (3:1) by its fill or its outline; and an open dialog shows against the
page dimmed behind it (3:1) by its face or its edge. It fails on a colour in no pair, so add the
pairs when you add a colour. `tests/test-check-contrast.sh` holds it to controls.

### `scripts/check-previews.py`

Renders every `preview.html` in every theme on a phone (375px, touch) and a desktop, in Chromium,
WebKit or Firefox (`--browser`; CI runs all three, D40), and the workbench and header on
sixteen more screens: small landscape phones, short windows, zoomed 16:9 screens and the least
screen side by side with its edges among them (D41, D75). It fails if:

- **Layout:** a screen puts the sidebar beside the stage or under it other than as its decision
  says (D75); the page scrolls sideways, or a box cuts off, spills or scrolls its content
  sideways; the tool's name is cut on a screen as wide as the layout's breakpoint or wider; the
  phone's view and plan bar are not pinned, or anything is pinned on a short or stacked landscape
  screen; an open dialog runs to the screen's edge or has no scrim behind it.
- **Rhythm and size:** the first item under a legend is not `space-3` below it, or a note not
  `space-1` under its group; a button, an input or a one-line control is not exactly `control-h`
  tall (D68), or a PieceMap cell, a summary or a tile is shorter; a touch control is under 44px.
- **Focus and states:** a focused control has no `action` ring 2px wide, or something clips it; a
  disabled control changes on hover, or an enabled one does not; a selected control is not tinted
  and ringed with an `action` border and a bold label (a PieceMap cell has the radio's dot
  instead, as its bold says it has its own fill, and no other cell has a mark); the chosen Choice
  is not tinted and ringed with a dotted radio; anything but the primary button is filled with
  `action`; two states look the same in forced colours.
- **Text and type:** a glyph falls back to another font; a label or a Sides tick is more than
  1.5px off centre or covered, or an icon more than 1.25px off its label's capitals (D88); a Sides box is not the radio's size; a run of text, as drawn or
  hovered, is under 4.5:1 against what is behind it.
- **Names and markup:** an icon reaches an accessible name; a part of a button's label is hidden
  from screen readers; a toggle has no `aria-pressed`, or a Choice is no named `radiogroup`.
- **Theme and status:** a page's `color-scheme` is not its theme; a status bar shows the wrong hint
  for the screen; a Notice's colours are not its variant's; an empty Notice or stage message takes
  room.
- **The stage:** a canvas does not fill its stage view, or resizes it; the 3D view cannot be used
  without a pointer (no focusable, named drawing described by the plan line, no ring inside the
  view, no Reset view, Zoom in, Zoom out or view choice, or controls over each other or
  swallowing a drag); on a phone there is no View… menu, or the open menu covers any of the view,
  sits above it, leaves its column or runs off the screen (D42); the More… menu does not open
  under the header, on the screen, or its items' icons are not in one column (A86).
- **The plan bar and header:** on any screen the plan bar is not one row, or its sentence takes
  more than two lines (D25, D75, D79), or is narrower than `plan-line-min` (D39); below `breakpoint-header` a version tag sits in the
  header's row, or the header shows more or fewer than one (D51).
- **`hidden`:** an element given the `hidden` attribute is still drawn (D57).
- **The Stepper:** a `Stepper` is not its field and two Buttons after it, reading ↓ and ↑, named
  `Smaller <label>` and `Larger <label>` and outside the field's label; or a button of it is
  narrower than `control-h` or does not line up with the field (D56).
- **The Select:** a `select` is not a `select.ws-input` alone in a `.ws-select`, with a label, or
  keeps the browser's own arrow; its chevron is not one glyph with empty alternative text, in the
  system's font and held by it, in the select's text colour; or, measured on the pixels, it draws
  nothing (something covers it), lies over the select's text or takes a press, here or in forced
  colours (D69).
- **The help toggle:** a button shows an icon alone and is not a help toggle; or a help toggle is
  not a quiet Button holding Codicons' info alone, named `About <label>`, after its label in a
  `.ws-label-row` and outside it, with `aria-expanded` and `aria-controls` naming a help that is
  hidden exactly while it is folded and stays the field's description; or it is not a `control-h`
  square, makes its row taller than the label, or its icon, on the pixels, is more than
  `CENTRE_TOL` off its box's centre (D94).
- **The busy ring:** with its view marked `aria-busy` and back, as a tool marks it, with and
  without reduced motion, the ring shows or turns at rest, shows or dims the drawing before
  `busy-delay`, does not show, is not a `control-h` ring on a `surface-raised` chip centred over
  the view, takes a press meant for the drawing, leaves the stage message showing, turns other than
  in twelve steps, before it shows, or with reduced motion, or stays once the view is not busy
  (D95).
- **Coverage:** a class the stylesheet styles is shown by no preview or named in no doc, or a doc
  names a class the system lacks.

It also runs the lines the component READMEs give a tool's script, and `theme-init.js`, as a tool
would:

- **View… (D42):** the Workbench README's lines must close the open menu when a view is picked.
- **More… (D87):** the Header README's lines must close the open menu when any action in it is
  picked, each in turn.
- **Stepper (D56):** with the Stepper README's lines, ↑, ↓, ArrowUp and ArrowDown (real key
  presses, in the field as it is and as a `type=number` one) must move the value by its step,
  onto its steps where it keeps to them, and stop at its limits, where the button says so
  (`aria-disabled`); and ↓ must reach below zero from 0.
- **Help (D94):** with the Help README's lines, two presses on each help toggle must show its help,
  under its field, and hide it again, `aria-expanded` saying which.
- **The theme (D58):** in a page that loads it as a tool does, `theme-init.js` must set
  `data-theme` to the stored theme, or with nothing stored, an unknown value or storage refused,
  to the system setting's, when the script has run and before the stylesheet is read, and must
  never throw.

`tests/test-check-previews.sh` holds each check to a control.

### `scripts/sweep-side-by-side.py`

Draws the Workbench preview on every short screen a pixel apart (700 to 1,280px wide, 240px to
`breakpoint-short` tall, with a mouse and on touch, `--browser` as above: 140,021 screens a
pointer), and fails if a screen goes side by side other than as the rule says (H from the build,
D75), if a bar beside the sidebar is not one row of one height, or if a screen side by side gives
the 3D view under 40 % of its height (D25). `tests/test-sweep-side-by-side.sh` holds it to
controls.

## Where this comes from

- **Window sealer:** the model colours (`model-panel`, `model-joint`, `model-tape`, `model-tpu`),
  `error` (#b00020), the units, the form wording and the part vocabulary come from
  AlonRR/parametric-window-sealer (`main` at `1b47d3a`), whose page is a single plain column with
  the result at the bottom. Its `choice` colour (#b06d00) was dropped, as every Choice has a
  default (D27).
- **Skådis Air** (AlonRR/skadis-air, then named skadis_ultralight_generator) adds `model-board`,
  `model-board-outline` and `warning`, and its own decisions supply the sides, size and mounting
  behaviour.
- **The direction** (a stage-first workbench, a header toolbar, a 380px sidebar with a numbered
  rail, a status bar, a texture-style gallery, save and load, rounded corners of 8px and 14px, one
  Nerd Font, a restrained blue accent) follows the CNC Kitchen apps (BumpMesh, filaSim), as seen
  on cnckitchen.com/tools. It uses their approach, not their logo or brand marks.
- This system replaces both pages' layouts and styling. Its colours are chosen for this project
  and checked for contrast; its sizes are its own; the dark theme is an addition. The components
  are hand-written, with no component library and no code bundle.
