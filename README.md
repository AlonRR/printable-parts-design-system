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
| `scripts/` | `build-tokens.py`, `check-contrast.py` and `check-previews.py`. |

## Working on it

Python runs through [uv](https://docs.astral.sh/uv/); the dependencies are in `pyproject.toml`, pinned in `uv.lock`, and `uv run` installs them on first use.

```sh
uv run python scripts/build-tokens.py     # rebuilds tokens.css, checks bundle.css agrees
uv run python scripts/check-contrast.py   # every theme: text 4.5:1, borders and rings 3:1
uv run python scripts/check-previews.py   # renders every preview on a phone and a desktop, each theme
```

`check-previews.py` needs Chromium for Playwright once: `uv run python -m playwright install chromium`. It writes screenshots to `build/previews`.

Commits go through [pre-commit](https://pre-commit.com) hooks (`.pre-commit-config.yaml`): formatting and secret checks on the files, and two house hooks in `.githooks/` that check the commit's identity and its message (`type(scope): summary`, no attribution trailers). `uvx pre-commit@4.6.2 install` wires them into a clone.

CI runs all three, every hook, the hooks' own tests, a check of every pushed commit's identity and a secret scan of the whole history, and fails if `tokens.css` is out of date. Rules for changing the system are in `DESIGN.md` under "Rules for changing the system".

## Using it in a tool

Copy `tokens.css`, `components/bundle.css` and `fonts/` into the tool, keeping `fonts/` beside `tokens.css`, which loads the fonts from it, and `fonts/licenses/` inside it. Copy them byte for byte from a tag (the files as the tag's commit holds them, not a checkout, which may have converted line ends), record the tag, and keep formatting tools off them. Serve them unchanged from a static folder rather than through a bundler, which renames the fonts and leaves the licence texts out of the site. Load `tokens.css` then `bundle.css`, set `data-theme="light"` or `"dark"` on `<html>` before the page is first drawn, and put `class="ws-page"` on `<body>`. Each theme sets the page's `color-scheme`, so the browser's own scroll bars, spinners and lists follow it. Start from a copy until the tools get tedious to keep in step, then consider a submodule or a small package. Skådis Air's copy script, theme code, framing code and browser test are the reference for the next tool: `DESIGN.md`, "Reference implementations".

Skådis Air adds `model-board`, `model-board-outline`, `warning` and the `Sides` component; the window sealer uses `model-panel`, `model-joint`, `model-tape`, `model-tpu`. Both are defined in the one `tokens.json`.

## Licence

The code (tokens, stylesheets, component previews, scripts, tests) is [MPL-2.0](LICENSES/MPL-2.0.txt) and the documentation [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt), as in the tools that use this system; `REUSE.toml` assigns each file, and `reuse lint` checks it. The fonts and icons keep their own licences: OFL-1.1, CC-BY-4.0 and MIT, see [`FONTS.md`](FONTS.md) and [`fonts/licenses/`](fonts/licenses/README.md).

_Parts of this repository were drafted with the help of an LLM agent; reviewed and verified locally._
