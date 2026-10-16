#!/usr/bin/env python3
"""Give every icon in the bundled fonts an advance as wide as it draws.

Run from the project folder:  uv run python scripts/fit-icon-advances.py
Needs: fonttools and brotli (pyproject.toml; uv run installs them).

The Nerd Font patcher gives each icon one text cell of advance (1200 of 1950 units) and draws most
of them wider, up to 1780 units, so the gap between an icon and its label came out anywhere from
about 2 to 7 px at 15 px: icon-gap measured from the cell, not from the ink. This sets each icon's
advance (Private Use Area: Powerline, Codicons, Font Awesome) to its ink's right edge, so icon-gap is
the gap you see, for every icon. Text glyphs keep their cell, so text stays monospaced; no glyph is
redrawn. It changes nothing on a second run. scripts/build-tokens.py fails if an icon draws past its
advance, so a rebuilt subset that skips this step does not pass.
"""
import pathlib
from fontTools.ttLib import TTFont

root = pathlib.Path(__file__).resolve().parent.parent
PUA = range(0xE000, 0xF900)

for path in sorted((root / "fonts").glob("*.woff2")):
    font = TTFont(path)
    glyf, hmtx = font["glyf"], font["hmtx"]
    changed = 0
    for cp, name in font.getBestCmap().items():
        if cp not in PUA:
            continue
        g = glyf[name]
        if not g.numberOfContours:
            continue
        g.recalcBounds(glyf)
        adv, lsb = hmtx[name]
        if adv != g.xMax and g.xMax > 0:
            hmtx[name] = (g.xMax, lsb)
            changed += 1
    if changed:
        font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.metrics.values())
        font.flavor = "woff2"
        font.save(path)
    print(f"{path.relative_to(root)}: {changed} icon advances set to their drawn width")
