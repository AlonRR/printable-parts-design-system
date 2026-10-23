# Workbench

The page layout of the tool: a header, the 3D stage with its plan and status bars, and a sidebar,
with a step rail once the form outgrows a screen.

## The page

Put `class="ws-page"` on `<body>`: it drops the browser's margin and sets the page's background,
text colour and font, form controls included. Build the page as four parts in a `.ws-workbench`.

### 1. The header

`.ws-header` (see `Header`):

- The tool's name (`h1.ws-header__name`) at the left, then Undo and Redo.
- A `.ws-header__more` "More…" button and the `.ws-header__actions` popover it opens
  (`popovertarget`), holding Reset, Save project, Load project and the theme toggle, and last a
  copy of the version if the header shows one, as below `--breakpoint-header` the version goes
  there, not in the row (D51).
- From `--breakpoint-header` up the popover sits inline and More… is hidden; below it, the popover
  opens under the header (D28). That is wider than `--breakpoint-wide`, so the tool's name stays
  whole beside the sidebar (D49).

### 2. The stage

`.ws-stage`: the 3D view fills it, with a `.ws-plan` bar under it and a `.ws-status` bar under
that.

- **The plan bar** holds the plan's sentence in `.ws-plan__line` (`aria-live="polite"`, so a change
  is announced), then `.ws-plan__actions` with the primary button. On every screen the bar is one
  row, the sentence at most two lines beside the button, on a phone (D25) and beside the sidebar
  (D75, D79); the whole sentence stays in the page for a screen reader, and a long file name
  breaks rather than widening the page.
- **What must be read goes first (A86).** The clamp cuts the sentence's end, so lead with what the
  person must know, in a first sentence short enough to show whole on every screen: on the first
  visit, that the sizes are an example, "Example wall. Replace the sizes with yours. 4 pieces · …".
  At 320px wide (1280px at 400 % zoom) the sentence is two lines of about 14 characters.
  `check-previews.py` fails a screen where the first sentence's last word is cut.
- **The short label (D39).** As the bar is one row, the primary button shows a short label. Put
  the words it drops in a `span.ws-plan__long`:
  `Download<span class="ws-plan__long">&nbsp;the pieces</span>…`.
  - The stylesheet hides that span from view only, on every screen, not from screen readers, so
    the button still says "Download the pieces…" to them.
  - Keep the ellipsis outside the span, as a button that opens a dialog ends with one on every
    screen, and start the span with `&nbsp;`, a space no layout drops.
  - `check-previews.py` fails a screen where the sentence is narrower than `--plan-line-min`
    (7rem).
- **The view's own controls** go over it, in `.ws-stage__tools` at the top right: "Reset view",
  then the "View…" button and its menu holding "Zoom in", "Zoom out" and the Front · Back · Top
  choice (D30, D36; below).
- **The status bar** shows file or part information, units and the hints. The hints are two spans,
  `.ws-hint-fine` for a mouse and `.ws-hint-touch` for a touch screen, each naming the gestures the
  tool supports ("Left drag: orbit · Scroll: zoom · Arrow keys: turn", "Drag: turn · Pinch:
  zoom"); the stylesheet shows the one that fits the screen. Put both in one span, last in the
  bar, as the preview does: beside the sidebar the bar is one row, and that last span is cut short
  with an ellipsis where the hint does not fit, its whole text still in the page (D75).

### 3. The sidebar

`.ws-side`. When the form outgrows a screen, a `nav.ws-rail` runs across its top, with one
`button.ws-rail__btn` per step, each `<span class="ws-rail__num">2</span>Window`:
`aria-current="step"` on the active one, and on a done one `data-done="yes"` with
`<span class="ws-sr">, done</span>`. Then `.ws-controls` holds the step title, its fieldsets, and
Back and Next in a `.ws-nav`. A short form is `.ws-controls` alone (D31).

### 4. The edge toggle

Planned, not yet a component: a toggle on the sidebar's border that collapses it, so the stage
gets the full width.

## The 3D view

The tool's 3D view is a `canvas` placed directly in `.ws-stage__view`. The stylesheet makes it
fill the view and never size it, so a resize cannot feed back into itself, and turns off the
browser's own touch gestures on it (`touch-action:none`), so drag and pinch reach the view. An
`svg` drawing standing in for the canvas, as in the preview, is laid out the same way.

**Without a pointer (D30).** Every move has a press and a key, and the view has a name.

- Give the canvas `tabindex="0"`, `role="img"`, an `aria-label` naming the part ("The wall in 3D")
  and `aria-describedby` pointing at the plan line's `id`, so a screen reader hears the name and
  then the plan.
- Focused, it shows a ring inside the view. The tool's script turns the camera with the arrow keys
  (Left and Right round the part, Up and Down over it) and zooms with `+` and `-`, by the same
  steps as the buttons.
- "Zoom in" and "Zoom out" (`&#xeb81;`, `&#xeb82;`) step the zoom and stop where a pinch stops.
- The views are a `Choice` (`role="radiogroup"`, `aria-label="View"`): picking one turns the camera
  to face that side, framed as below. The side the camera faces is chosen, and a drag or a key
  that turns it away clears the choice, so this is the one Choice without a standing default.
  "Reset view" goes back to the first view.
- The controls wrap rather than overlap, and a drag between them still reaches the canvas.

**On a phone (D36).** Below the breakpoint, and on a short screen, the view shows only "Reset
view" and "View…", so it stays clear for the fingers that pinch and drag. View… opens the rest in
a menu below the view, over the plan bar, so the part stays in sight while zooming (D42), one
press away for anyone who cannot pinch.

- The markup is the same on every screen: after Reset view,
  `<button class="ws-btn ws-stage__more" type="button" popovertarget="ws-view-menu">View…</button>`,
  then `<div class="ws-stage__menu" id="ws-view-menu" popover>` holding Zoom in, Zoom out and the
  `.ws-choice.ws-stage__views` choice.
- On a wide screen the stylesheet hides View… and lays the menu's contents out in place: the zoom
  buttons beside Reset view, the choice at the bottom left.
- The browser opens the menu, and closes it on Escape or a press outside it. The tool's script
  closes it when a view is picked, so the new view shows at once (D42), with the lines below.
- Where a browser cannot anchor the menu to the view, it opens in the middle of the screen, over
  the part.

Closing View… when a view is picked, in the tool's script (`check-previews.py` runs these lines on
the preview, picks a view, and fails if the menu stays open):

```js
for (const menu of document.querySelectorAll('.ws-stage__menu'))
  menu.addEventListener('change', (e) => {
    if (e.target.closest('.ws-stage__views') && menu.matches(':popover-open')) menu.hidePopover();
  });
```

**The stage message.** A `p.ws-stage__message` (`aria-live="polite"`) in the view says what is
happening while the part loads, or when it cannot be drawn, on a `surface-raised` backing so it
reads over the model. Empty, it takes no room but stays in the page, so it is announced when it
fills.

**While a part is rebuilt (D95).** The part on show is the old one until the new one is drawn, so
the view says so: after a moment it dims, and a ring turns over it. This is the system's one
motion.

- **Markup:** after the stage message, in the view,
  `<div class="ws-busy" aria-hidden="true"><span class="ws-busy__chip"><span class="ws-busy__ring"></span></span></div>`.
  It is for the eye alone: the status line says what is happening in words, as it does now.
- **The tool's script** sets `aria-busy="true"` on the `.ws-stage__view` when it starts making a
  part, the first one included, and removes it when the part is drawn, or when the form or the
  build says it cannot be made. The view, not the stage round it: a screen reader may hold back
  what changes inside a busy element, and the status line is in the stage.
- **What the stylesheet does with it:** after `--busy-delay` (0.4s), so a quick rebuild never
  flickers, it fades in over `--busy-fade` (0.15s): the drawing dims to `--opacity-disabled`, the
  stage message is hidden under the ring, and twelve dashes, from `border` to `action` at the
  head, turn round a `control-h` ring on a `surface-raised` chip, centred over the view. Removed,
  everything goes at once.
- **How it turns:** in twelve steps a second (`--busy-turn`), only once it shows. A ring turning
  smoothly asks for a frame every 60th of a second, and in a page drawn in software, as a headless
  browser test draws, that slowed eight pages at once several times over and failed 28 of
  Skådis Air's 105 browser tests; in steps, all passed (its C316). With reduced motion it shows and
  does not turn; at rest nothing turns.
- **A drag goes through it** (`pointer-events: none`) and turns the view.

**Framing.** The part in the stage always fits it (`DESIGN.md`): framed to `--stage-fit` when the
part or its size changes, pulled back only as far as needed when the stage resizes (keeping the
user's angle), zoom stopping at `--stage-min-fill`, no panning off the stage, and "Reset view"
back to the first view.

## Layout by screen

The stage is always mounted and always visible. Never put the result under the inputs.

- **A phone.** The stage lays its parts out in the page (`display:contents`): the view,
  `--stage-phone-h` tall, and the plan bar are pinned, the status bar scrolls away with the form,
  and the page's `scroll-padding` keeps a focused field below the pinned part. Under
  `--breakpoint-short` nothing is pinned.
- **Side by side** (D25, D75): on a screen `--breakpoint-wide` or wider, or at least
  `--landscape-ratio` wide and `--breakpoint-side-min` (48rem) or wider, and either way at least
  H tall, the stage takes the full height beside the sidebar (`panel-width`, at most half the
  screen). There the header, the plan bar and the status bar keep one row each, so they are one
  height on every screen, and the 3D view takes the rest.
- **A narrow landscape screen** stacks, as a phone held upright does, and pins nothing, so the
  view keeps `--stage-phone-h` and the page scrolls (D41).
- **H** is the least height at which those bars leave the 3D view 40 % of the screen, 16.5rem
  (264px), set by a touch screen's taller `--control-h`. `build-tokens.py` derives it from the
  bars' tokens (DESIGN.md, Phones and small screens) and fails if the stylesheet says another.
  A shorter screen stacks and pins nothing. So a phone held sideways, 800 × 360 and larger, goes
  side by side, its view 56 % and more.
- **The margin.** The worst screen side by side, 768 × 264 on touch, gives the view 40.2 %.
  `scripts/sweep-side-by-side.py` draws every short screen, a pixel apart, in Chromium, WebKit
  and Firefox, and fails if one goes side by side other than as the rule says, if a bar beside
  the sidebar is not one row of one height, or if one side by side gives the view under 40 %.

## First visit

Show a short welcome dialog: a quick start in four numbered steps and a line that everything runs
in the browser. Keep it dismissible, and show it once.
