# Printable-parts design system

The shared look, layout and components of two browser tools that generate 3D-printable parts:
[Parametric window sealer](https://github.com/AlonRR/parametric-window-sealer), panels and seals
for the gap a window leaves, and [Skådis Air](https://github.com/AlonRR/skadis-air), light,
tileable SKÅDIS-compatible pegboards. It is written for those two tools and for the next one in
the family.

A tool copies a few static files: design tokens, one stylesheet, a small theme setter and the
fonts. They give it one base, the same in every tool (a workbench layout with the 3D view first,
`Choice` buttons, one typeface with icons built in, rounded corners, light and dark themes), and a
small layer of its own: a cover, model colours and wording. Every value comes from one source,
and scripts check contrast, layout and behaviour in Chromium, WebKit and Firefox.

## What is here

| Path | What |
| --- | --- |
| `tokens.json` | The source of every colour, size, gap and type style, light and dark. Change a value here and nowhere else. |
| `tokens.css` | Generated from `tokens.json`, with the `@font-face` rules that load `fonts/`. Never edited by hand. |
| `components/bundle.css` | The component styles. They read tokens only; the build fails on a typed colour or size, or a font declared here. |
| `components/<Name>/` | One folder per component: a `README.md` with its rules and markup, and a `preview.html` card. |
| `theme-init.js` | The theme setter a tool loads first in its head, so the page is drawn in the right theme from the first paint. |
| `fonts/` | FiraCode Nerd Font, Regular and Bold, subset; `fonts/licenses/` holds the upstream licences and credits. |
| `scripts/` | The build and the checks. |
| `tests/` | Each check's controls, and the tests of the hooks and the CI workflow. |
| `LICENSES/`, `REUSE.toml` | This repository's licences, in the [REUSE](https://reuse.software) layout. |

## Using it in a tool

1. **Copy the files from a release tag**, byte for byte as the tag's commit holds them (not from
   a checkout, which may have converted line ends): `tokens.css`, `components/bundle.css`,
   `theme-init.js` and `fonts/`. Keep `fonts/` beside `tokens.css`, which loads the fonts from
   it, and record the tag.
2. **Serve them unchanged** from a static folder, not through a bundler, which renames the fonts
   and leaves the licence texts out of the site. Keep formatting tools off them.
3. **Load them at the top of the head**, the theme setter first:

   ```html
   <script src="theme-init.js" data-key="skadis-air-theme"></script>
   <link rel="stylesheet" href="tokens.css">
   <link rel="stylesheet" href="bundle.css">
   ```

   `theme-init.js` sets `data-theme="light"` or `"dark"` on `<html>` before the page is first
   drawn: the theme stored under the key `data-key` names (`printable-parts-theme` without one),
   or else the system setting. `tokens.css` themes the page through `data-theme` alone, and each
   theme sets the page's `color-scheme`, so the browser's own scroll bars and lists follow it. As
   a file, it runs under a content security policy without `'unsafe-inline'`.
4. **Put `class="ws-page"` on `<body>`** and build the page from the components, starting with
   [`Workbench`](components/Workbench/README.md). The `hidden` attribute hides anything the
   system styles.
5. **Add the few lines of script the system needs.** Keep `data-theme` in step while the page is
   open and store the theme toggle's choice, `"light"` or `"dark"`, under the same key
   ([`DESIGN.md`](DESIGN.md), "Light or dark"). Three components give lines for the tool's script,
   which the checks run on their previews: closing the View… menu when a view is picked
   (`Workbench`), closing the More… menu when an action is picked (`Header`) and a `Stepper`'s
   arrows.
6. **Before moving to a new version, read its entry in [`CHANGELOG.md`](CHANGELOG.md).** While the
   version is 0.x, a minor version may change markup, and its entry says how to follow.

Start from a copy, and consider a submodule or a small package once keeping the tools in step
gets tedious. Skådis Air's copy script, theme code, framing code and browser test are the
reference for the next tool ([`DESIGN.md`](DESIGN.md), "Reference implementations"). The model
colours of both tools are in the one `tokens.json`: `model-board` and `model-board-outline` for
Skådis Air, `model-panel`, `model-joint`, `model-tape` and `model-tpu` for the window sealer.

## Components

Each links to its README; its `preview.html` shows it in both themes.

| Component | What it is |
| --- | --- |
| [Button](components/Button/README.md) | An action button: primary, outlined or quiet. |
| [Choice](components/Choice/README.md) | Pick-one options shown as buttons with a radio mark. |
| [Cover](components/Cover/README.md) | The window sealer's cover art, 960 × 288 px, for use outside the tool. |
| [CoverSkadisAir](components/CoverSkadisAir/README.md) | Skådis Air's cover art, likewise. |
| [Dialog](components/Dialog/README.md) | A modal for one short choice, over a scrim. |
| [Disclosure](components/Disclosure/README.md) | A collapsible section for rarely changed settings. |
| [Field](components/Field/README.md) | A labelled input with its note and its error line. |
| [Fieldset](components/Fieldset/README.md) | The fields of one decision, under a legend. |
| [Gallery](components/Gallery/README.md) | Picture tiles, for options that are visual. |
| [Header](components/Header/README.md) | The slim top bar: the tool's name, project actions and the theme. |
| [Icons](components/Icons/README.md) | The icon set, Codicons and Font Awesome, inside the font. |
| [Notice](components/Notice/README.md) | An inline warning or error about the plan. |
| [PieceMap](components/PieceMap/README.md) | A grid that mirrors the wall, to pick one piece. |
| [Select](components/Select/README.md) | A long list to pick one from: the native select, with a chevron from the font. |
| [Sides](components/Sides/README.md) | Skådis Air's four toggles for which sides of a board are closed. |
| [Stepper](components/Stepper/README.md) | A number field with ↓ and ↑ buttons that move it by its step. |
| [Workbench](components/Workbench/README.md) | The page: header, 3D stage, plan and status bars, and sidebar. |

## Documentation

- [`DESIGN.md`](DESIGN.md): the rules for every tool built on the system, and for changing it.
- [`FONTS.md`](FONTS.md): the fonts and icons, their licences, and how to rebuild a subset.
- [`CHANGELOG.md`](CHANGELOG.md): what changed in each version, and how a tool moves to it.
- [`docs/decisions.md`](docs/decisions.md): every decision with its date and reason; an ID such as
  D25 in any document resolves there.
- [`STATUS.md`](STATUS.md): the version in progress, what is left before its release, and how
  releases are made.
- [`CLAUDE.md`](CLAUDE.md): how this repository is worked on, with its house rules and the full
  local gate.

## Browsers

The target (D40) is the current and the previous major version of Safari (on iOS too), Chrome
and Firefox, and Firefox ESR. Every browser on iOS is WebKit, so Safari's floor is every iOS
user's. CI renders every preview in Playwright 1.64's build of each engine, a job each: Chromium
156, WebKit 27.2 and Firefox 157 (D55), pinned in `pyproject.toml`; one more job draws the two
fallbacks below (D60).

What the system relies on, with the first version of each browser that has it (MDN's data):

| What | Chrome / Safari / Firefox | Used for | In the target without it |
| --- | --- | --- | --- |
| `popover` | 114 / 17 / 125 | the More… and View… menus | none |
| `position-area` anchoring | 129 / 26 / 147 | the open View… menu, below the 3D view (D42) | Firefox ESR 140: the menu opens mid-screen, over the part; it still opens on the screen with its items, and a pick closes it |
| `:has()` | 105 / 15.4 / 121 | the header's version tag (D51), the page's `scroll-padding`, a disabled Select's chevron (D69) | none |
| `svh` | 108 / 15.4 / 101 | the workbench's height | none |
| `appearance: none` on a `select` | 84 / 15.4 / 80 | a Select without the browser's own arrow (D69) | none |
| `lh` | 109 / 16.4 / 120 | a field's and a Disclosure summary's block padding, derived from `control-h` (D68) | none |
| alternative text in `content` (`content: "" / ""`) | Safari 17.4, Firefox 128 | the Sides box and tick and a Select's chevron, kept from screen readers | none |
| `ascent-override`, `descent-override` and `line-gap-override` in `@font-face` | 87 / Technology Preview only (18 Oct 2026) / 89 | the capitals of a label centred in their box | Safari: the font's own metrics place the capitals; in WebKit 27.2 without the three, all 920 labels the check measures are within 1px of centre (D60) |

What the preview check covers in each engine, as its output says:

- **Fonts and hover states** are read through the Chrome DevTools Protocol, so in Chromium only.
- **Forced colours** run in Chromium and Firefox; Playwright's WebKit matches the media query but
  keeps the author's colours.
- **Accessible names** come from Chromium's own accessibility tree; in WebKit and Firefox they are
  Playwright's reading of the page, as Playwright 1.64 reads no other engine's tree.
- **Two fallbacks** in the target are drawn by none of the three engines as they are: the View…
  menu without anchoring (Firefox ESR 140) and labels without the font-metric overrides (Safari).
  `check-previews.py --fallbacks` draws both (D60), from copies of the stylesheets with the
  `@supports (position-area: …)` block and the three overrides taken out, as such a browser reads
  them, and runs every check on them; CI runs it in WebKit, a job of its own. Labels are measured
  there only: without the overrides Chromium sets the font's own ascent and descent to whole pixels
  and draws labels up to 2px high, which no browser in the target does, as Chrome reads them.

## Development

Python runs through [uv](https://docs.astral.sh/uv/): the dependencies are in `pyproject.toml`,
pinned in `uv.lock`, and `uv run` installs them on first use. The preview checks need
Playwright's engines once: `uv run python -m playwright install chromium webkit firefox`.

```sh
uv run python scripts/build-tokens.py          # rebuild tokens.css; check bundle.css reads only tokens
uv run python scripts/check-contrast.py        # every theme: text 4.5:1, borders and rings 3:1
uv run python scripts/check-previews.py        # render every preview; --browser webkit or firefox
uv run python scripts/check-previews.py --fallbacks --browser webkit   # as a browser without position-area or the overrides
uv run python scripts/sweep-side-by-side.py    # every short screen: side by side as the rule says, the 3D view at 40 %
```

- Each check is held to its own controls in `tests/`: a copy of the files with one mistake put
  in, which the check must refuse with that check's own message.
- `check-previews.py` writes its screenshots to `build/previews`, and with `--fallbacks` to
  `build/previews-fallbacks`. A change meant to draw nothing new is proved so by
  `uv run python scripts/compare-shots.py BEFORE AFTER`, two such folders compared pixel for
  pixel, every channel (D44).
- `tests/test-check-previews.sh` takes its engine from `PREVIEW_ENGINE`, Chromium when it is unset,
  as CI's preview jobs do: `PREVIEW_ENGINE=webkit bash tests/test-check-previews.sh`. It never reads
  `BROWSER`, which many tools take as a web browser's command (D61).
- Commits go through [pre-commit](https://pre-commit.com) hooks: formatting and secret checks, and
  two house hooks in `.githooks/` that check the commit's identity and its message
  (`type(scope): summary`). `uvx pre-commit@4.6.2 install` wires them into a clone.
- The full local gate, run before every commit, is in [`CLAUDE.md`](CLAUDE.md); CI runs the same
  checks on every push. The rules for changing the system are in [`DESIGN.md`](DESIGN.md), "Rules
  for changing the system".

## Versions

Versions follow [Semantic Versioning](https://semver.org), counted by what a tool must do to
follow, as [`CHANGELOG.md`](CHANGELOG.md) explains. The version is in `tokens.json`, in the head
of `tokens.css` and in `pyproject.toml`, and the build keeps them in step with the changelog and
the tag. Releases in this repository start at `v0.6.0`; the notes of every earlier version are in
`CHANGELOG.md`.

## Licence

The code (tokens, stylesheets, the theme setter, component previews, scripts and tests) is
[MPL-2.0](LICENSES/MPL-2.0.txt) and the documentation [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt),
as in the tools that use the system; `REUSE.toml` assigns each file, and `reuse lint` checks it.
The fonts and icons keep their own licences, OFL-1.1, CC-BY-4.0 and MIT: see
[`FONTS.md`](FONTS.md) and [`fonts/licenses/`](fonts/licenses/README.md).

_Parts of this repository were drafted with the help of an LLM agent; reviewed and verified locally._
