# Adopting the design system in Skådis Air: a plan

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

- **D8. A licence for this repository.** Skådis Air needs one on every file it copies in, and its
  choice C32 copies code between the owner's repositories because both are MPL-2.0. Recommended:
  the tools' own split, MPL-2.0 for the tokens, the CSS, the scripts and the previews,
  CERN-OHL-S-2.0 for the documentation, in the REUSE layout; `fonts/` and `licenses/` keep their
  own. Choosing it is the owner's.
- **D9. Ship the fonts once.** `bundle.css` is 453 KB, nearly all of it the two fonts in base64,
  while `tokens.css` also points at the same fonts in `fonts/` (332 KB). A build would carry both,
  and a CSS file holding fonts would need four licences at once under REUSE. Recommended: take the
  base64 copies out of `bundle.css` (leaving 10.5 KB of CSS) and let `tokens.css` load the
  font files; `build-tokens.py` then checks the overrides in `tokens.css` alone. The previews and
  their check already load `tokens.css` first, so nothing else changes.
- **A version to point at.** Tag this repository (`v0.1.0`) once D8 and D9 are in, so Skådis Air
  records which version it copied. Tags are pushed from the owner's machine.

## The change in Skådis Air, in four parts

Each part is a row in its backlog and a branch of its own, ends with every check green, and leaves
a working page. Ease uses its backlog's scale.

1. **`design-system-base` (S): the look, not the layout.** Copy `tokens.css`, `bundle.css`,
   `fonts/` and the licence texts into `web/design-system/`, with a README naming the commit they
   came from (as C32 does). In REUSE, the fonts get `OFL-1.1 AND CC-BY-4.0 AND MIT` with their
   holders, and `LICENSES/` gains those three texts (`reuse download`). The page loads the two
   stylesheets, drops its own fonts and colours, and sets `data-theme` from the system setting.
   The preview reads `--surface`, `--model-board` and `--model-board-outline` instead of its
   typed colours, and again when the theme changes. The layout and the tests stay as they are.
2. **`design-system-controls` (M): the controls.** `form.ts` writes this system's markup: number
   fields as `Field` (the unit in the label, the tile count as a note); every choice as `Choice`
   buttons, radio inputs underneath with the same `name` and `value`, so `readValues` is
   untouched; the sides as `Sides` (`data-side` and `aria-pressed` kept); "Advanced" as
   `Disclosure`; the bed and thickness warnings as a `Notice` in `warning`. The board type follows
   D10, the printer becomes `Choice` (safe default, custom). The 8 tests that pick from a list
   change to checking a radio button, and the 3 that look at the list's headings and options to
   the buttons; the rest find what they found before.
3. **`workbench` (M): the layout.** The page becomes `Workbench`. The header holds the name and
   the theme toggle (D11). The stage holds the preview, which resizes to fill it, then a status
   bar with the board's size and "Drag: turn · Wheel or pinch: zoom", and "Reset view". The plan
   bar holds the board's status line and "Download STL" as the primary button. The sidebar holds
   the form. On a phone the stage stays on top at 45 % of the height, as `DESIGN.md` says. The
   intro and the two statements (the files are the user's; not made by IKEA) stay on the page, in
   the sidebar, until D12 is decided.
4. **`steps` (M), when wanted: the numbered steps.** `DESIGN.md` gives Skådis Air four steps:
   Board, Size and sides, Mounting, Printer. Each setting then has to say which step it belongs
   to, a new field in the library's setting definitions with a contract test over every entry
   (Skådis Air's `extension-registry` practice). Undo and redo, saving a project and the welcome
   dialog are features of their own, rows of their own, not part of the restyle.

**Checks, in every part.** The page's browser tests gain what this repository's
`check-previews.py` checks, on the real page: no sideways scrolling at 375 px, every control at
least 44 px tall on a touch screen, every glyph drawn in FiraCode, and the chosen `Choice` filled.

## Decisions for the owner

Skådis Air asks about anything a user would see (its D6), so these come before the parts they
change.

- **D8.** This repository's licence (above). Recommended: MPL-2.0 for code, CERN-OHL-S-2.0 for docs.
- **D9.** Ship the fonts once, as files (above). Recommended: yes.
- **D10.** How the board type is chosen: (a) `Choice` buttons under "Boards" and "Connectors"
  headings, keeping D91 (recommended); (b) a `Gallery` of pictures, which needs a drawing for
  every board and connector type.
- **D11.** A dark theme: (a) follow the system setting, with a toggle in the header
  (recommended); (b) light only for now.
- **D12.** Where the intro text goes: (a) stays in the sidebar for now (recommended); (b) into
  the welcome dialog `DESIGN.md` describes, which is a feature of its own.
- **D13.** The numbered steps: (a) one sidebar form first, steps when the form grows
  (recommended; the form is short today); (b) steps as part of the layout change.

## Who carries it out

Skådis Air pushes to the owner's Gitea first and keeps GitHub in step from there (its D7 and A77).
A cloud session reaches neither for writing: this session can read the repository but not push to
it. So the parts run in a session on the owner's machine, following Skådis Air's `CLAUDE.md`
(a backlog row, a branch `feat/<key>`, decisions in its `docs/status.md`, a failing test first).
The window sealer can follow the same four parts afterwards.
