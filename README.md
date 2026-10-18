# Printable-parts design system

The shared look and layout for Alon's browser tools that generate printable parts: **Parametric window sealer** and **Skådis Air**. One base (workbench layout, Choice buttons, Fira Code, Codicons, rounded corners, light and dark themes) and a small layer per project (cover, model colours, wording).

Read [`DESIGN.md`](DESIGN.md) for how to use it. Components are in `components/<Name>/` (a `README.md` of rules and a `preview.html` card).

## What is here

| Path | What |
| --- | --- |
| `tokens.json` | The source of every colour, size, gap and type style, light and dark. Edit this, nothing else, to change a value. |
| `tokens.css` | Generated from `tokens.json`, with the `@font-face` rules that load `fonts/`. Never edit by hand. |
| `components/bundle.css` | Component styles. Reads only tokens; the build fails on a hard-coded colour or a font declared here. |
| `theme-init.js` | The theme setter a tool loads first in its head: it sets `data-theme` on `<html>` before the page is first drawn (D58). |
| `fonts/` | FiraCode Nerd Font, regular and bold, subset (see [`FONTS.md`](FONTS.md)). |
| `fonts/licenses/` | The upstream licence texts and credits for the fonts and icons, inside `fonts/` so they travel with it. |
| `LICENSES/`, `REUSE.toml` | This repository's licences, in the [REUSE](https://reuse.software) layout. |
| `scripts/` | `build-tokens.py`, `check-contrast.py`, `check-previews.py`, `sweep-side-by-side.py`, and `fit-icon-advances.py` for a rebuilt font subset. |
| `tests/` | Each check's controls, and the tests of the hooks and the CI workflow. |
| `CHANGELOG.md` | What changed in each version, and how a tool moves to it. |

## Working on it

Python runs through [uv](https://docs.astral.sh/uv/); the dependencies are in `pyproject.toml`, pinned in `uv.lock`, and `uv run` installs them on first use.

```sh
uv run python scripts/build-tokens.py     # rebuilds tokens.css, checks bundle.css agrees
uv run python scripts/check-contrast.py   # every theme: text 4.5:1, borders and rings 3:1
uv run python scripts/check-previews.py   # renders every preview on a phone and a desktop, each theme
uv run python scripts/sweep-side-by-side.py   # every short screen side by side keeps 40 % for the 3D view
```

`check-previews.py` needs Chromium for Playwright once: `uv run python -m playwright install chromium`. It writes screenshots to `build/previews`. `--browser webkit` or `--browser firefox` renders in that engine instead, after `uv run python -m playwright install webkit firefox` (see "Browsers"). `sweep-side-by-side.py` takes the same `--browser`, and draws the Workbench preview on every short screen a pixel apart, with a mouse and on touch, in about two minutes (D54).

Commits go through [pre-commit](https://pre-commit.com) hooks (`.pre-commit-config.yaml`): formatting and secret checks on the files, and two house hooks in `.githooks/` that check the commit's identity and its message (`type(scope): summary`, no attribution trailers). `uvx pre-commit@4.6.2 install` wires them into a clone.

CI runs all three, the previews in Chromium, WebKit and Firefox, a job each; every hook, the hooks' own tests, a check of every pushed commit's identity and a secret scan of the whole history, and fails if `tokens.css` is out of date. Rules for changing the system are in `DESIGN.md` under "Rules for changing the system".

## Browsers

The target (D40): the current and the previous major version of Safari, on iOS too, of Chrome and of Firefox, and Firefox ESR. Every browser on iOS is WebKit, so Safari's floor is every iOS user's. CI renders every preview in Playwright's build of each engine, Chromium, WebKit and Firefox, a job each (`check-previews.py --browser`): since D55, Playwright 1.64's Chromium 156, WebKit 27.2 and Firefox 157, pinned in `pyproject.toml`.

What the system relies on, with the first version that has it (MDN's data, from the second review):

| What | Chrome / Safari / Firefox | Used for | In the target without it |
| --- | --- | --- | --- |
| `popover` | 114 / 17 / 125 | the More… and View… menus | none |
| `position-area` anchoring | 129 / 26 / 147 | the open View… menu, below the 3D view (D42) | Firefox before 147, so ESR 140 while it is supported: the menu opens mid-screen, over the part, as before D42; it still opens on the screen with its items, and a pick closes it |
| `:has()` | 105 / 15.4 / 121 | the header's version tag (D51), the page's `scroll-padding` | none |
| `svh` | 108 / 15.4 / 101 | the workbench's height | none |
| alternative text in `content` (`content: "" / ""`) | Safari 17.4, Firefox 128 | the Sides box and tick, kept from screen readers | none |
| `ascent-override` in `@font-face` | 87 / Technology Preview only (MDN, 18 Oct 2026) / 89; Playwright's WebKit 27.2 has it, its 26.0 did not (measured) | the capitals of a label centred in their box | Safari: the labels sit a little higher; in WebKit 26.0 all 712 labels the check measures were within its 1.5px |

What the check leaves out in an engine, and says so in its output: the fonts each glyph is drawn in and the hover states are read through the Chrome DevTools Protocol, Chromium only; forced colours run in Chromium and Firefox, as Playwright's WebKit matches the media query but keeps the author's colours (measured in 26.0 and 27.2); and the accessible names are Chromium's own tree, but in WebKit and Firefox Playwright's reading of the page, as Playwright 1.64 reads no other engine's tree. Every engine CI runs since D55 has `position-area` and `ascent-override`, so two fallbacks in the target are stated in the table above but drawn by no job: the View… menu without anchoring (Firefox ESR 140; last checked in Playwright's Firefox 142, D40) and labels without `ascent-override` (Safari; last measured in WebKit 26.0). In an engine without `position-area` the check still checks only the menu's fallback, and says so. The check's controls (`tests/test-check-previews.sh`) run in Chromium; `BROWSER=webkit` runs them in another engine. `BROWSER` must name an engine: a shell that sets it to a web browser's command, as some do (an agent's shell had `BROWSER=true`), fails every control; set `BROWSER=chromium` there.

## Using it in a tool

Copy `tokens.css`, `components/bundle.css`, `theme-init.js` and `fonts/` into the tool, keeping `fonts/` beside `tokens.css`, which loads the fonts from it, and `fonts/licenses/` inside it. Copy them byte for byte from a tag (the files as the tag's commit holds them, not a checkout, which may have converted line ends), record the tag, and keep formatting tools off them. Serve them unchanged from a static folder rather than through a bundler, which renames the fonts and leaves the licence texts out of the site. Read the version's entry in `CHANGELOG.md` before you move to it: while the version is 0.x a minor version may change markup, and the entry says how to follow. At the top of the head, before the stylesheets, load the theme setter, `<script src="theme-init.js" data-key="skadis-air-theme"></script>`, then `tokens.css` and `bundle.css`, and put `class="ws-page"` on `<body>`. `theme-init.js` sets `data-theme="light"` or `"dark"` on `<html>` before the page is first drawn (D58): the theme stored under the key `data-key` names (`printable-parts-theme` without one), or else, with nothing stored, another value or storage refused, the system setting's, as `tokens.css` themes the page through `data-theme` alone and is light without it. It is a file, not a script in the page, so a content security policy without `'unsafe-inline'` runs it. The tool's own script keeps `data-theme` in step while the page is open and stores the toggle's choice, `"light"` or `"dark"`, under the same key (DESIGN.md, "Light or dark"). Each theme sets the page's `color-scheme`, so the browser's own scroll bars, spinners and lists follow it. The `hidden` attribute hides anything the system styles, whatever display its class sets (D57). Two components need a few lines in the tool's script, given in their READMEs and run by `check-previews.py` on the previews: closing the View… menu when a view is picked (`Workbench`, D42) and a `Stepper`'s arrows and arrow keys (D56). Start from a copy until the tools get tedious to keep in step, then consider a submodule or a small package. Skådis Air's copy script, theme code, framing code and browser test are the reference for the next tool: `DESIGN.md`, "Reference implementations".

Skådis Air adds `model-board`, `model-board-outline`, `warning` and the `Sides` component; the window sealer uses `model-panel`, `model-joint`, `model-tape`, `model-tpu`. Both are defined in the one `tokens.json`.

## Licence

The code (tokens, stylesheets, component previews, scripts, tests) is [MPL-2.0](LICENSES/MPL-2.0.txt) and the documentation [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt), as in the tools that use this system; `REUSE.toml` assigns each file, and `reuse lint` checks it. The fonts and icons keep their own licences: OFL-1.1, CC-BY-4.0 and MIT, see [`FONTS.md`](FONTS.md) and [`fonts/licenses/`](fonts/licenses/README.md).

_Parts of this repository were drafted with the help of an LLM agent; reviewed and verified locally._
