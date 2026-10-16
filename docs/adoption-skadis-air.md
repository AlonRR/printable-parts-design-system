# Adopting the design system in Skådis Air: a plan

**Since this plan (16 Oct 2026):** parts 1 to 3 are done in Skådis Air. It copies the design system
from a tag into `web/public/design-system/`, served unchanged (its C116), not `web/design-system/`
as written below; "Reset view" sits in the plan bar beside the download (its C126), not in the
status bar; and the current version is `v0.5.0`. `v0.3.0` carries what Skådis Air had added
locally (D18 here); `v0.4.0` and `v0.5.0` change its markup, and `CHANGELOG.md`, under "Moving to
it" for each, says how to follow; take both together, as `v0.5.0` with the `v0.4.0` markup draws
the view choice over the 3D view. The plan below is kept as it was decided.

A proposal for the owner (Q7, 14 Oct 2026). Nothing in Skådis Air has been changed: the plan was
made by reading its repository at commit `f463830` (`main`, 14 Oct 2026). Its own `CLAUDE.md` says
the repository is now `AlonRR/skadis-air` (A80; relayed, not checked from here). Decision IDs in
the form D8 belong to this repository; IDs such as D46 are Skådis Air's own, in its
`docs/status.md`.

## What the page is today

Read from the code, not run:

- **One column**, at most 44rem wide: `web/index.html` (5 KB, its own `<style>` with
  `system-ui` and its own greys and reds) and six TypeScript files under `web/src`.
- **The form is built from the board types** (`form.ts`, the extension registry): a number box per
  number setting, with the tile count beside size (D45); a `<select>` per choice; the four side
  toggles round a drawing of the board (D46), reading "Top: closed"; the fine settings under
  "Advanced" (D48).
- **The board type is one `<select>`**, boards and connectors under two headings (D91).
- **The printer** is a `<select>` (safe default or custom, D61); a board larger than the bed is
  warned about (D62).
- **The 3D preview** (three.js) has its colours typed in: board `0xc9cdd1`, edges `0x4a525a`,
  background `0xf4f4f4`. The first two are already this system's `model-board` and
  `model-board-outline`.
- **30 browser tests in 7 files.** They find things by `data-testid`, by `name` and by role; 8 of
  them pick from a `<select>` (11 calls), and 3 look at `<optgroup>` or `<option>`.
- **Licensing is REUSE**: `web/**` is MPL-2.0, the docs CERN-OHL-S-2.0, and `reuse lint` must
  pass; `LICENSES/` holds only those two texts.

## Before Skådis Air can take the files

These are in this repository.

- **D8, done.** This repository is MPL-2.0 for code (the tokens, the stylesheets, the previews,
  the scripts) and CERN-OHL-S-2.0 for documentation, in the REUSE layout, as the tools are;
  `reuse lint` passes and CI runs it. The fonts keep their own licences, with the upstream texts
  in `fonts/licenses/`.
- **D9, done** (`0eac517`). The fonts ship once, as files: `bundle.css` holds no font (453 KB
  down to 10 KB), and `tokens.css` loads `fonts/` through its `@font-face` rules, so `fonts/`
  stays beside `tokens.css`. `build-tokens.py` fails if a font comes back into `bundle.css`.
- **A version to point at, done.** Copy from `v0.2.0` (`7b43d0c`), which adds the two framing
  tokens of D15 to `v0.1.0` (`aa3188e`); Skådis Air records the version it copies. The owner
  pushes the tags (a cloud session cannot).

## The change in Skådis Air, in four parts

Each part is a row in its backlog and a branch of its own, ends with every check green, and leaves
a working page. Ease uses its backlog's scale.

1. **`design-system-base` (S): the look, not the layout.** Copy `tokens.css`, `bundle.css` and
   `fonts/` (with `fonts/licenses/` inside it) into `web/design-system/`, keeping `fonts/` beside
   `tokens.css`, with a README naming the tag they came from (as C32 does). In REUSE, the fonts
   get `OFL-1.1 AND CC-BY-4.0 AND MIT` with their holders, as this repository's `REUSE.toml`
   does, and `LICENSES/` gains those three texts (`reuse download`). The page loads the two
   stylesheets, drops its own fonts and colours, and sets `data-theme` from the system setting.
   The preview reads `--surface`, `--model-board` and `--model-board-outline` instead of its
   typed colours, and again when the theme changes. The layout and the tests stay as they are.
2. **`design-system-controls` (M): the controls.** `form.ts` writes this system's markup: number
   fields as `Field` (the unit in the label, the tile count as a note); every choice as `Choice`
   buttons, radio inputs underneath with the same `name` and `value`, so `readValues` is
   untouched; the sides as `Sides` (`data-side` and `aria-pressed` kept); "Advanced" as
   `Disclosure`; the bed and thickness warnings as a `Notice` in `warning`. The board type becomes
   `Choice` buttons under "Boards" and "Connectors" (D10), the printer becomes `Choice` (safe
   default, custom). The 8 tests that pick from a list change to checking a radio button, and the
   3 that look at the list's headings and options to the buttons; the rest find what they found
   before.
3. **`workbench` (M): the layout.** The page becomes `Workbench`. The header holds the name and
   the theme toggle (D11). The stage holds the preview, which resizes to fill it, then a status
   bar with the board's size and "Drag: turn · Wheel or pinch: zoom", and "Reset view". The plan
   bar holds the board's status line and "Download STL" as the primary button. The sidebar holds
   the form. On a phone the stage stays on top at 45 % of the height, as `DESIGN.md` says. The
   intro and the two statements (the files are the user's; not made by IKEA) stay on the page, in
   the sidebar (D12).
   **The part always fits the stage (D15).** Today the preview keeps a fixed 0.6 aspect, frames
   the board only when its type or size changes or on "Reset view", and lets zoom and pan go
   anywhere (`web/src/preview.ts`, read at `41c79c5`). Filling the stage, it must instead: frame
   to `--stage-fit` when the part or its size changes; on a resize, keep the user's angle and
   pull back only as far as the whole part needs; stop zooming out at `--stage-min-fill`; keep
   the part's centre on the stage when panning (or switch panning off); and frame again on
   "Reset view". Both ratios are read from `tokens.css`, not typed in. A browser test projects
   the corners of the part's bounding box into the canvas and checks they lie inside it, on a
   phone and a desktop, after a resize, and after zooming out as far as it goes; with a positive
   control that fails when the framing is skipped.
4. **`steps` (M), later, when the form grows (D13): the numbered steps.** `DESIGN.md` gives
   Skådis Air four steps: Board, Size and sides, Mounting, Printer. Each setting then has to say
   which step it belongs to, a new field in the library's setting definitions with a contract test
   over every entry (Skådis Air's `extension-registry` practice). Undo and redo, saving a project
   and the welcome dialog are features of their own, rows of their own, not part of the restyle.

**Checks, in every part.** The page's browser tests gain what this repository's
`check-previews.py` checks, on the real page: no sideways scrolling at 375 px, every control at
least 44 px tall on a touch screen, every glyph drawn in FiraCode, and the chosen `Choice` tinted and ringed (D26).

## Decisions

Skådis Air asks about anything a user would see (its D6). The owner answered these on
14 Oct 2026, each as recommended; D10 to D13 go into Skådis Air's `docs/status.md`, under its own
IDs, when the work starts there.

- **D8.** This repository's licence: MPL-2.0 for code, CERN-OHL-S-2.0 for docs. Done.
- **D9.** The fonts ship once, as files. Done.
- **D10.** The board type is chosen with `Choice` buttons under "Boards" and "Connectors",
  keeping D91; a `Gallery` waits for drawings of every type.
- **D11.** A dark theme that follows the system setting, with a toggle in the header.
- **D12.** The intro text stays in the sidebar for now; a welcome dialog is a feature of its own.
- **D13.** One sidebar form first; the numbered steps come when the form grows.
- **D15.** The part always fits the stage, as above and in `DESIGN.md`; the two ratios are the
  tokens `stage-fit` and `stage-min-fill`.

## Who carries it out

Skådis Air pushes to the owner's Gitea first and keeps GitHub in step from there (its D7 and A77).
A cloud session reaches neither for writing: this session can read the repository but not push to
it. So the parts run in a session on the owner's machine, following Skådis Air's `CLAUDE.md`
(a backlog row, a branch `feat/<key>`, decisions in its `docs/status.md`, a failing test first).
The window sealer can follow the same four parts afterwards.
