# Printable-parts design system

The shared look and layout for Alon's browser tools that generate printable parts: **Parametric window sealer** and **Skådis Air**. One base (workbench layout, Choice buttons, Fira Code, Codicons, rounded corners, light and dark themes) and a small layer per project (cover, model colours, wording).

Read [`DESIGN.md`](DESIGN.md) for how to use it. Components are in `components/<Name>/` (a `README.md` of rules and a `preview.html` card).

## What is here

| Path | What |
| --- | --- |
| `tokens.json` | The source of every colour, size, gap and type style, light and dark. Edit this, nothing else, to change a value. |
| `tokens.css` | Generated from `tokens.json`, with the `@font-face` rules that load `fonts/`. Never edit by hand. |
| `components/bundle.css` | Component styles. Reads only tokens; the build fails on a hard-coded colour or a font declared here. |
| `fonts/` | FiraCode Nerd Font, regular and bold, subset (see [`FONTS.md`](FONTS.md)). |
| `fonts/licenses/` | The upstream licence texts and credits for the fonts and icons, inside `fonts/` so they travel with it. |
| `LICENSES/`, `REUSE.toml` | This repository's licences, in the [REUSE](https://reuse.software) layout. |
| `scripts/` | `build-tokens.py`, `check-contrast.py`, `check-previews.py`, and `fit-icon-advances.py` for a rebuilt font subset. |
| `tests/` | Each check's controls, and the tests of the hooks and the CI workflow. |
| `CHANGELOG.md` | What changed in each version, and how a tool moves to it. |

## Working on it

Python runs through [uv](https://docs.astral.sh/uv/); the dependencies are in `pyproject.toml`, pinned in `uv.lock`, and `uv run` installs them on first use.

```sh
uv run python scripts/build-tokens.py     # rebuilds tokens.css, checks bundle.css agrees
uv run python scripts/check-contrast.py   # every theme: text 4.5:1, borders and rings 3:1
uv run python scripts/check-previews.py   # renders every preview on a phone and a desktop, each theme
```

`check-previews.py` needs Chromium for Playwright once: `uv run python -m playwright install chromium`. It writes screenshots to `build/previews`. `--browser webkit` or `--browser firefox` renders in that engine instead, after `uv run python -m playwright install webkit firefox` (see "Browsers").

Commits go through [pre-commit](https://pre-commit.com) hooks (`.pre-commit-config.yaml`): formatting and secret checks on the files, and two house hooks in `.githooks/` that check the commit's identity and its message (`type(scope): summary`, no attribution trailers). `uvx pre-commit@4.6.2 install` wires them into a clone.

CI runs all three, the previews in Chromium, WebKit and Firefox, a job each; every hook, the hooks' own tests, a check of every pushed commit's identity and a secret scan of the whole history, and fails if `tokens.css` is out of date. Rules for changing the system are in `DESIGN.md` under "Rules for changing the system".

## Browsers

The target (D40): the current and the previous major version of Safari, on iOS too, of Chrome and of Firefox, and Firefox ESR. Every browser on iOS is WebKit, so Safari's floor is every iOS user's. CI renders every preview in Playwright's build of each engine, Chromium, WebKit and Firefox, a job each (`check-previews.py --browser`).

What the system relies on, with the first version that has it (MDN's data, from the second review):

| What | Chrome / Safari / Firefox | Used for | In the target without it |
| --- | --- | --- | --- |
| `popover` | 114 / 17 / 125 | the More… and View… menus | none |
| `position-area` anchoring | 129 / 26 / 147 | the open View… menu, below the 3D view (D42) | Firefox before 147, so ESR 140 while it is supported: the menu opens mid-screen, over the part, as before D42; it still opens on the screen with its items, and a pick closes it |
| `:has()` | 105 / 15.4 / 121 | the header's version tag (D51), the page's `scroll-padding` | none |
| `svh` | 108 / 15.4 / 101 | the workbench's height | none |
| alternative text in `content` (`content: "" / ""`) | Safari 17.4, Firefox 128 | the Sides box and tick, kept from screen readers | none |
| `ascent-override` in `@font-face` | not in WebKit 26.0 (measured) | the capitals of a label centred in their box | Safari: the labels sit a little higher; in WebKit 26.0 all 712 labels the check measures are within its 1.5px |

What the check leaves out in an engine, and says so in its output: the fonts each glyph is drawn in and the hover states are read through the Chrome DevTools Protocol, Chromium only; forced colours run in Chromium and Firefox, as Playwright's WebKit matches the media query but keeps the author's colours (measured); where an engine has no `position-area` (Playwright's Firefox, 142), the View… menu's anchoring is not checked, only its fallback; and Playwright's Firefox has no phone mode (`is_mobile`), so a phone there is a touch window of the phone's size. The accessible names are read from each engine's own tree. The check's controls (`tests/test-check-previews.sh`) run in Chromium; `BROWSER=webkit` runs them in another engine.

## Using it in a tool

Copy `tokens.css`, `components/bundle.css` and `fonts/` into the tool, keeping `fonts/` beside `tokens.css`, which loads the fonts from it, and `fonts/licenses/` inside it. Copy them byte for byte from a tag (the files as the tag's commit holds them, not a checkout, which may have converted line ends), record the tag, and keep formatting tools off them. Serve them unchanged from a static folder rather than through a bundler, which renames the fonts and leaves the licence texts out of the site. Read the version's entry in `CHANGELOG.md` before you move to it: while the version is 0.x a minor version may change markup, and the entry says how to follow. Load `tokens.css` then `bundle.css`, set `data-theme="light"` or `"dark"` on `<html>` before the page is first drawn, and put `class="ws-page"` on `<body>`. Each theme sets the page's `color-scheme`, so the browser's own scroll bars, spinners and lists follow it. Start from a copy until the tools get tedious to keep in step, then consider a submodule or a small package. Skådis Air's copy script, theme code, framing code and browser test are the reference for the next tool: `DESIGN.md`, "Reference implementations".

Skådis Air adds `model-board`, `model-board-outline`, `warning` and the `Sides` component; the window sealer uses `model-panel`, `model-joint`, `model-tape`, `model-tpu`. Both are defined in the one `tokens.json`.

## Licence

The code (tokens, stylesheets, component previews, scripts, tests) is [MPL-2.0](LICENSES/MPL-2.0.txt) and the documentation [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt), as in the tools that use this system; `REUSE.toml` assigns each file, and `reuse lint` checks it. The fonts and icons keep their own licences: OFL-1.1, CC-BY-4.0 and MIT, see [`FONTS.md`](FONTS.md) and [`fonts/licenses/`](fonts/licenses/README.md).

_Parts of this repository were drafted with the help of an LLM agent; reviewed and verified locally._
