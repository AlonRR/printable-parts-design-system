# Printable-parts design system

The shared look and layout for Alon's browser tools that generate printable parts: **Parametric window sealer** and **Skådis Air**. One base (workbench layout, Choice buttons, Fira Code, Codicons, rounded corners, light and dark themes) and a small layer per project (cover, model colours, wording).

Read [`DESIGN.md`](DESIGN.md) for how to use it. Components are in `components/<Name>/` (a `README.md` of rules and a `preview.html` card).

## What is here

| Path | What |
| --- | --- |
| `tokens.json` | The source of every colour, size, gap and type style, light and dark. Edit this, nothing else, to change a value. |
| `tokens.css` | Generated from `tokens.json`. Never edit by hand. |
| `components/bundle.css` | Component styles. Reads only tokens; the build fails on a hard-coded colour. Fonts are embedded here as base64 so previews and tools work with one file. |
| `fonts/` | FiraCode Nerd Font, regular and bold, subset (see [`FONTS.md`](FONTS.md)). |
| `scripts/` | `build-tokens.py`, `check-contrast.py` and `check-previews.py`. |

## Working on it

```sh
pip install -r requirements.txt
python3 scripts/build-tokens.py     # rebuilds tokens.css, checks bundle.css agrees
python3 scripts/check-contrast.py   # every theme: text 4.5:1, borders and rings 3:1
python3 scripts/check-previews.py   # renders every preview on a phone and a desktop, each theme
```

`check-previews.py` needs Chromium for Playwright once: `python3 -m playwright install chromium`. It writes screenshots to `build/previews`.

CI runs all three and fails if `tokens.css` is out of date. Rules for changing the system are in `DESIGN.md` under "Rules for changing the system".

## Using it in a tool

Copy `tokens.css`, `components/bundle.css` and `fonts/` into the tool (or link them), load `tokens.css` then `bundle.css`, and set `data-theme="light"` or `"dark"` on `<html>`. Start from a copy until the tools get tedious to keep in step, then consider a submodule or a small package.

Skådis Air adds `model-board`, `model-board-outline`, `warning` and the `Sides` component; the window sealer uses `model-panel`, `model-joint`, `model-tape`, `model-tpu`. Both are defined in the one `tokens.json`.

## Licence

To be chosen by the owner before the repo is shared; until then, all rights reserved. Fonts and icons carry their own licences, see [`FONTS.md`](FONTS.md).

_Parts of this repository were drafted with the help of an LLM agent; reviewed and verified locally._
