#!/usr/bin/env python3
"""Check colour contrast for every theme in tokens.json. Fails (exit 1) below the limits.

Run from the project folder:  python3 scripts/check-contrast.py
Text pairs need 4.5:1; borders, focus rings and outlines need 3:1 (WCAG 2.2 AA).
Edit PAIRS when a new colour is added; the `model-*` materials are drawn in the stage
and are checked only where text or outlines sit on them.
"""
import json, sys, pathlib
tok = json.loads((pathlib.Path(__file__).resolve().parent.parent / "tokens.json").read_text())
themes = [t["id"] for t in tok["color"]["themes"]]
col = {c["name"]: c["value"] for c in tok["color"]["tokens"]}
def val(n, th): v = col[n]; return v[th] if isinstance(v, dict) else v
def lum(h):
    h = h.lstrip("#"); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True); return (x + .05) / (y + .05)
BG = ["surface", "surface-raised"]
TEXT = [(fg, bg) for fg in ("ink", "ink-muted", "error", "warning", "action") for bg in BG]
TEXT += [("ink", "action-tint"), ("ink", "surface-sunken"), ("ink-muted", "action-tint"), ("on-action", "action")]
NONTEXT = [(fg, bg) for fg in ("border-strong", "action", "choice", "error") for bg in BG]
NONTEXT += [("model-board-outline", "model-board"), ("model-outline", "model-panel"), ("border-strong", "surface-sunken"), ("action", "action-tint")]
bad = 0
for th in themes:
    for label, pairs, need in (("text", TEXT, 4.5), ("non-text", NONTEXT, 3.0)):
        for fg, bg in pairs:
            r = ratio(val(fg, th), val(bg, th))
            ok = r >= need
            if not ok: bad += 1
            print(f"{'ok  ' if ok else 'FAIL'} {th:5} {label:8} {fg} on {bg}: {r:.2f} (need {need})")
print("\n%d failing" % bad)
sys.exit(1 if bad else 0)
