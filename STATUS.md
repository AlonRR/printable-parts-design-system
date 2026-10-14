# Status

Progress against the brief in [`docs/original-brief.md`](docs/original-brief.md).

| Step | State |
|---|---|
| 1. Verify the folder | Done. `build-tokens.py` regenerates `tokens.css` unchanged; `check-contrast.py` reports 0 failing. |
| 2. Visual check of `components/*/preview.html` (light and dark, 375 px wide) | Done; the defects below are fixed, and `scripts/check-previews.py` now fails CI on each of them. Covers and touch targets wait on Q3 and Q4. |
| 3. Repository | `AlonRR/printable-parts-design-system` exists. `main` and branch `claude/inspiring-babbage-98suc5` hold the same rebuilt history. |
| 4. CI (`.github/workflows/check.yml`, runs on every push) | Green on the first pushes (job `tokens`: build, `tokens.css` unchanged, 52 contrast pairs, 0 failing). The new job `previews` runs from the next push. |
| 5. Report, incl. the `FONTS.md` "to be confirmed" items | Not started. |

## Step 2: what the previews showed

`check-previews.py` renders the 15 previews in both themes on a phone (375 px, touch) and a
desktop (960 px). Before the fixes it reported 110 failures; after them, 0. Proved able to fail:
on the files as delivered, on labels pinned off centre, and on a button with a box drawn over it.

Fixed, at the source:

- **`<code>` was not in FiraCode.** The browser sets `code` in its own monospace (Liberation Mono
  here, Consolas or Menlo elsewhere): the Dialog's `-print-8` and the Icons names. `bundle.css`
  now sets `code`, `kbd`, `samp` and `pre` in `--font-ui`.
- **The header cut off its buttons on a phone.** `overflow:hidden` hid Redo, Save, Load and the
  theme toggle at 375 px. The header now scrolls sideways instead (`overflow-x:auto`), one row.
- **Choice buttons were 38 px tall, not `control-h` (36 px; 46 px, not 44, on touch).** A `span`
  with `min-height` adds its border; the face is now `box-sizing:border-box`.
- **The Sides tick reached screen readers** (" Top"). The generated tick now carries empty
  alternative text (`content:"\eab2" / ""`), the CSS form of `aria-hidden`.
- **The plan bar crushed the stage on a phone.** Its sentence was squeezed into a narrow column
  beside the Download button, the stage drawing overflowed upwards over the header. The plan
  bar now wraps below the breakpoint and stays one row above it.
- **The Workbench preview typed its own layout** (`22rem` sidebar instead of `panel-width`,
  fixed rows): "Next: Fittings" stuck out of the sidebar on the desktop, and on a phone the
  preview kept the desktop columns. The preview now uses the component's own layout, and its
  stand-in drawing fills the stage the way the tool's canvas does.

Checked and correct: icons and the radio mark render from the bundled font in every preview;
the chosen Choice is filled with an inverted radio, 40 options in 4 runs.

Not changed:

- **Label centring.** Capitals sit 0.2 to 1.2 px above the centre of their box. The font
  overrides are right (the H glyph's height equals the font's cap height in both weights);
  Chromium rounds the ascent and descent to whole pixels and floors the top half-leading, which
  with a 22.5 px line box leaves the caps 0.55 px high, plus up to half a pixel from where the
  box falls on the pixel grid. A whole-pixel body line height would bring it to about 0.3 px;
  not worth changing every line of text for. The check allows 1.5 px.
- **The status bar** wraps each hint onto two lines at 960 px and on a phone; two lines just fit
  its 32 px. A longer hint would spill out of it.

## History

- An earlier session committed this content as `Claude <noreply@anthropic.com>`, with
  attribution trailers and unscoped subjects. On the owner's instruction the history was deleted
  and rebuilt with the cloud-session starter from `AlonRR/engineering-practices` in place.

## Open questions

- **Q1.** The house rules say Python dependencies go through `uv` and `pyproject.toml`, but the
  folder ships `requirements.txt`, and CI and the README install it with pip. Convert to
  `pyproject.toml` + `uv`, or keep `requirements.txt` for this repo?
- **Q2.** Closed: the owner chose to reset `main` to the rebuilt history.
- **Q3.** `Cover` and `CoverSkadisAir` are fixed 960 x 288 px, so on a phone they run 585 px off
  the side. If they are only gallery or social-card art, that is fine; if a tool shows them, they
  should scale. Which is it? Until answered, `check-previews.py` skips them on the phone.
- **Q4.** `DESIGN.md` says touch targets are `tap` (44 px) or more on a phone, but `control-h`
  covers only buttons, Choice faces, toggles and rail buttons. On a touch screen, inputs and
  selects are 36 to 37 px tall, PieceMap cells 32.5 px and the Disclosure summary 22.5 px.
  Should they grow to `tap` too?
