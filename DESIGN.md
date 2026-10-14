# Design guidance

The rules for every tool built on this system. Values live in `tokens.json`; this page says how to use them.

## One base, two projects

This system serves Alon's browser tools that generate printable parts. The **base** (everything outside the two project sections below) is shared: workbench layout, Choice buttons, Fira Code, Codicons, rounded corners, light and dark themes, save and load, live updates. Each **project** adds only its own cover, model colours, step names, wording and a few components. A new generator starts from the base and adds one more section.

- **Parametric window sealer** (AlonRR/parametric-window-sealer): panels and seals for the gap a window leaves. Model colours `model-panel`, `model-joint`, `model-tape`, `model-tpu`. Steps: Opening, Window, Fittings, Seal, Printer and style. Cover: `Cover`.
- **Skådis Air** (AlonRR/skadis_ultralight_generator): light, tileable SKÅDIS-compatible pegboards and connectors. Model colours `model-board`, `model-board-outline`. Steps: Board, Size and sides, Mounting, Printer. Components: `Sides`. Cover: `CoverSkadisAir`.

Use `surface` for the page and the stage, `surface-raised` for the header, sidebar, dialogs and groups, and `ink` for text. Put notes, units and errors in `ink-muted` and `error`. Never put `ink-muted` or `error` on a coloured fill.

## The tool is a workbench

- **The wall is the page.** The 3D stage is the biggest thing on screen and is always visible. Controls live in a sidebar beside it. The result is never below the inputs. (See `Workbench`.)
- **Header, stage, sidebar, status bar.** A slim `header-h` header carries the name, undo/redo/reset, Save project, Load project and the theme toggle. The stage fills the rest, with a status bar (`status-h`) under it showing sizes, units and the mouse hints "Left drag: orbit · Right drag: pan · Scroll: zoom". The sidebar is `panel-width` wide and collapses from an edge toggle.
- **A numbered step rail, one step at a time.** The rail holds 1 to 5 (Opening, Window, Fittings, Seal, Printer and style). The sidebar shows the current step's title and fieldsets, then Back and Next. The stage shows the whole wall at every step and highlights what the step changes.
- **Open on a working example.** The first visit shows an example wall and says so; presets replace every value in one tap. A short welcome dialog gives a four-step quick start and says everything runs in the browser, then never shows again.
- **Live, no Apply.** Every change updates the stage at once. An invalid value keeps the last good wall, marks the field and says what to fix.
- **Show only what applies.** Track depth appears only for an edge in a track; hose size only for a hose. Rarely changed settings go in an "Advanced" `Disclosure` at the end of the step.
- **Pick-one options are buttons with a radio mark.** Use `Choice`: every option is a button with a small radio circle at its left. The chosen one is filled, and its circle is inverted (white with a blue centre and an extra white ring), so it reads as both highlighted and selected. A tick means pick several (the `Sides` toggles); never use a tick for pick-one. For picture options use `Gallery`, not a dropdown.
- **Projects can be saved.** Save project and Load project write and read one file; undo and redo cover every change.
- **Measuring help is beside the field.** A "How do I measure?" link opens the guide with its drawing as a panel; the user returns to the same spot.
- **Phone:** the stage is pinned at the top at 45% of the screen height; the sidebar scrolls beneath it; the primary button stays reachable. Touch targets are `tap` (44px) or more; rotate and zoom use drag and pinch.

## Rules for changing the system

No value is typed twice. Colours, sizes, gaps, the ring width, the control height and the breakpoint live in `tokens.json`; components read them as variables. Two scripts keep it honest. Run them after any change:

- `python3 scripts/build-tokens.py` rebuilds `tokens.css` from `tokens.json`, works out each font's vertical-centring overrides from its cap height, and fails if `bundle.css` disagrees on the overrides or the breakpoint, or uses a hard-coded colour.
- `python3 scripts/check-contrast.py` checks every theme: text pairs need 4.5:1, borders, focus rings and outlines 3:1. Add a pair when you add a colour.
- `python3 scripts/check-previews.py` renders every `preview.html` in every theme on a phone (375px, touch) and a desktop, and fails if a glyph falls back to another font, the page scrolls sideways or a box cuts off or spills its content, a control is not `control-h` tall, a label is more than 1.5px off centre or covered, the chosen Choice is not filled with an inverted radio, or an icon reaches an accessible name. Write a preview for every new component.

Controls are `control-h` tall (36px), and `tap` (44px) on touch screens, set once. Focus, selected outlines and the chosen radio's ring all use `ring`; the radio's offsets are derived from it, so changing `ring` or `radio-size` cannot shift a label. Icons, ticks and radio marks sit `icon-gap` from their label.

## Content fundamentals

- Say "you" and use plain words: panel, piece, strip, edge, seal. No jargon.
- Units in every label: `Width (mm)`. Metric default, millimetres for sizes. Imperial optional as a setting next to language.
- Be honest about what is untested: the joint fit and track sizes are "starting values that a test print still has to confirm". Put it in a note, not a tooltip.
- Errors say what to fix: "Fix the marked fields to see the plan." Warnings name the choice that resolves them.
- Sentence case for headings and buttons. End a button that opens a dialog with an ellipsis ("Download the pieces...").
- Say where the work happens: "Everything runs in your browser; nothing is uploaded."

## Visual foundations

- **Quiet, light and soft-cornered.** Light surfaces, hairline `border` between regions, one accent. Corners are rounded: `radius-sm` (8px) on buttons, inputs, tiles and notices; `radius-md` (14px) on groups, dialogs and the stage frame. No shadows, no gradients, no motion.
- **One filled colour.** `action` is the only fill: the primary button, the active step on the rail and the focus ring (solid 2px, 2px offset). Selected tiles and pieces use an `action` outline on `action-tint`. `error` outlines a field and the message explains it. `choice` outlines a group that needs a pick. Colour is never the only signal.
- **Control borders are `border-strong`** (3.5:1 or more); `border` only separates regions.
- **The `model-*` colours are materials in the stage**, not UI: never use them for text or controls. `model-tape` orange means seal.
- Section labels in the sidebar and status text use `label-caps` (mono, uppercase, `ink-muted`).
- Guide drawings are inline SVG in `currentColor` with arrow markers.

## Type

One family for everything: FiraCode Nerd Font (`ui`), a monospace face with icons built in. Fewer typefaces keep the interface calm, and a fixed-width face lines numbers up in columns and keeps 0/O and 1/l/I distinct. Do not mix in another family. Hierarchy comes from size and weight, never a second face. Styles: `title`, `section`, `step`, `body`, `legend`, `note`, `label-caps`, `code`. Text is 15px (`body`) and notes 13px; keep notes to short sentences, since a monospace line holds fewer characters.

Vertical centring is fixed at the font, not per component: the `@font-face` rules in `bundle.css` set `ascent-override` 96.85% and `descent-override` 26.23% (line gap 0), computed from the font's cap height so capital letters sit on the centre line of any line box. Any new font needs its own pair (ascent minus descent equals cap height; ascent plus descent keeps the line height). Do not nudge text with padding.

Ligatures: on in text (so `=>` and `->` join), off in inputs, numbers and file names (`ws-input`, `code`, `ws-num` turn them off), so a value never changes shape. Use real arrows (→) in labels, e.g. "Next: Fittings →". Numbers use the slashed zero.

## Accessibility

- Native elements: `fieldset`, `legend`, `details`, `dialog`, `select`. Pick-one options are radios underneath, shown as `Choice` buttons. Every control has a visible label.
- State never relies on colour alone: errors have text, the active step has `aria-current="step"` and a filled button, selected tiles use `aria-pressed`.
- Announce changing results (the plan line, errors, download status) with `aria-live="polite"`.
- The stage has a text equivalent: the plan line says pieces, ports and seal.
- `inputmode="decimal"` on numeric fields.

## Iconography and logo

Icons are Nerd Font glyphs. Prefer the thin-line Codicons (`cod-`), which are the lightest weight here, and use one set throughout (see `Icons`); Font Awesome (`fa-`) is solid and heavier. Real Regular and Bold weights are bundled, so bold text is a true bold: `<span class="ws-ic" aria-hidden="true">&#xeb4b;</span>Save`. Every icon sits before a text label and is `aria-hidden`; an icon is never the only thing that says what a button does. Common ones: save eb4b, load eaf7, download eac2, undo eae2, redo ebb0, reset eb37, theme eac6, tick f00c. There is no logo; the tool name is set in `title` style.

## Project: Skådis Air

- **Voice.** Short and plain, like the page: "Download STL", "Reset view", "= 6 tiles". Say what is untested: every number marked "to confirm" is a starting value until the fit coupon has been printed. Sizes in mm, in 40 mm steps, with the tile count beside the field.
- **Steps.** Board (solid, lightened or skeleton; list only the types that are built), Size and sides, Mounting (screw holes in the corner tiles, countersunk by default; optional 20 mm standoffs on the back), Printer (bed 200 × 200 mm by default, custom size beside it).
- **Stage.** The board is shown as it hangs: upright, front toward you, slots vertical, in `model-board` with `model-board-outline` edges. Drag turns it, wheel or pinch zooms, "Reset view" returns. One "Download STL" button sits under the preview.
- **Sides.** Open or closed is chosen side by side with `Sides`: four toggles round a small drawing of the board. A single panel is open all round by default; a wall is closed round its outer edge.
- **Advanced.** Slot clearance, chamfer and corner radius are folded under an "Advanced" `Disclosure`.
- **Warnings.** A board larger than the bed, or a thickness outside 4 to 5.5 mm, shows a `Notice` in `warning`. It warns and never refuses.
- **Brand.** Say "SKÅDIS-compatible". The page carries the line that it is not made, endorsed or supported by IKEA; no IKEA logo, colours or wordmark.

## Project: Parametric window sealer

- **Voice.** Panel, piece, strip, edge, seal.
- **Steps.** Opening, Window, Fittings, Seal, Printer and style. `model-tape` orange means seal.
- **Stage.** The wall seen from the room, with `PieceMap` to pick one piece.

## Where this comes from

Window sealer: the model colours (`model-panel`, `model-joint`, `model-tape`, `model-tpu`), `error` (#b00020) and `choice` (#b06d00), the units, the form wording and the part vocabulary come from the repo AlonRR/parametric-window-sealer (main@1b47d3a), whose page is a single plain column with the result at the bottom. Skådis Air (AlonRR/skadis_ultralight_generator, main) adds `model-board`, `model-board-outline` and `warning`, and its decisions D37 to D75 supply the sides, size and mounting behaviour. This system replaces both pages' layouts and styling. The direction (stage-first workbench, header toolbar, 380px sidebar with a numbered rail, status bar, texture-style gallery, save/load project, rounded corners (8px and 14px), one Nerd Font (FiraCode), a restrained blue accent) follows the CNC Kitchen apps (BumpMesh, filaSim) as seen on cnckitchen.com/tools; it uses their approach, not their logo or brand marks. Colours here are chosen for this project and checked for contrast; sizes are this system's own. The dark theme is an addition. Components are hand-written; the repo has no component library, so there is no code bundle.
