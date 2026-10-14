#!/usr/bin/env python3
"""Render every components/*/preview.html and check what a reader would see. Fails (exit 1) on a defect.

Run from the project folder:  python3 scripts/check-previews.py [--out DIR]
Needs: playwright and pillow (pip install -r requirements.txt), and Chromium for Playwright
(python3 -m playwright install chromium; a cloud session already has it).

Each preview is loaded with tokens.css then components/bundle.css, in every theme, on a phone
(375 px wide, touch) and a desktop (960 px), and screenshot into DIR (default build/previews).
Checks, per page:
1. fonts:    every glyph is drawn from the bundled font, as Chromium reports it; a fallback
             means a missing glyph or an element that sets its own family (e.g. <code>).
2. overflow: on the phone, the page does not scroll sideways and no box cuts off content it
             hides (overflow:hidden); on both devices, no box's content sticks out sideways
             beyond it. FIXED_SIZE previews are fixed-size art and skipped on the phone.
3. choice:   the chosen Choice is filled with action and its radio inverted; the others are
             surface-raised with a hollow radio.
4. centring: the capitals of each control's label sit within CENTRE_TOL of the box's centre,
             measured on the pixels of a capital H drawn in place of the label. Each control
             is scrolled into view first (a toolbar or sidebar may scroll), and fails if
             something else is drawn over it.
5. height:   buttons, Choice faces, Sides toggles and rail buttons are control-h tall.
6. names:    no accessible name carries an icon glyph (Private Use Area): icons are hidden.
"""
import argparse, io, json, pathlib, re, sys, tempfile
from PIL import Image
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parent.parent
tok = json.loads((root / "tokens.json").read_text())
themes = [t["id"] for t in tok["color"]["themes"]]
families = {f["family"] for f in tok["type"]["fonts"]}
DEVICES = [("phone", dict(viewport={"width": 375, "height": 800}, has_touch=True, is_mobile=True)),
           ("desktop", dict(viewport={"width": 960, "height": 800}))]
DPR = 2                 # screenshots at 2x, so the centring scan resolves half pixels
CENTRE_TOL = 1.5        # px; Chromium rounds the baseline to whole pixels (up to about 1.2 px measured)
FIXED_SIZE = {"Cover", "CoverSkadisAir"}  # 960 x 288 cover art; whether it should scale is open (STATUS.md, Q3)
CONTROLS = ".ws-btn, .ws-choice__face, .ws-sides__btn, .ws-rail__btn, .ws-piece"
SIZED = ".ws-btn, .ws-choice__face, .ws-sides__btn, .ws-rail__btn"
PUA = re.compile("[\ue000-\uf8ff]")

PAGE = """<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{tokens}"><link rel="stylesheet" href="{bundle}">
<style>html,body{{margin:0;background:var(--surface)}}</style></head><body>{fragment}</body></html>"""

# In the page: what the overflow, choice and height checks read.
LAYOUT_JS = """([sized]) => {
  const vw = document.documentElement.clientWidth, cut = [], spill = [];
  for (const el of document.body.querySelectorAll('*')) {
    const ox = getComputedStyle(el).overflowX, id = `${el.localName}.${String(el.className.baseVal ?? el.className).split(' ')[0]}`;
    if (el.scrollWidth <= el.clientWidth + 1 || !el.clientWidth || el.closest('svg')) continue;
    if (ox === 'hidden' || ox === 'clip') cut.push(`${id} shows ${el.clientWidth} of ${el.scrollWidth}px`);
    else if (ox === 'visible') spill.push(`${id} is ${el.clientWidth}px wide, its content ${el.scrollWidth}px`);
  }
  const probe = document.createElement('div');
  probe.style.height = 'var(--control-h)'; document.body.append(probe);
  const controlH = probe.getBoundingClientRect().height;
  const colour = (v) => { probe.style.color = v; return getComputedStyle(probe).color; };
  const s = getComputedStyle(document.documentElement);
  const t = { action: colour(s.getPropertyValue('--action')), onAction: colour(s.getPropertyValue('--on-action')),
              raised: colour(s.getPropertyValue('--surface-raised')) };
  probe.remove();
  const choice = [...document.querySelectorAll('.ws-choice__input')].map((inp) => {
    const face = inp.nextElementSibling, f = getComputedStyle(face), m = getComputedStyle(face, '::before');
    const ok = inp.checked
      ? f.backgroundColor === t.action && m.backgroundColor === t.onAction && m.borderTopColor === t.action && m.boxShadow.includes(t.onAction)
      : f.backgroundColor === t.raised && m.backgroundColor === 'rgba(0, 0, 0, 0)' && parseFloat(m.width) > 0;
    return { label: face.textContent, checked: inp.checked, ok };
  });
  const heights = [...document.querySelectorAll(sized)].filter((e) => e.getClientRects().length)
    .map((e) => ({ cls: String(e.className).split(' ')[0], label: e.textContent.trim(), h: e.getBoundingClientRect().height }));
  return { scroll: document.documentElement.scrollWidth - vw, cut, spill, choice, heights, controlH };
}"""

# In the page: swap each control's label for capital H's, one for one and keeping the spaces, so
# in a monospace face nothing moves (a shorter label would change the layout being checked).
PROBE_JS = """([sel]) => [...document.querySelectorAll(sel)].flatMap((el) => {
  const texts = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) if (n.data.trim() && !n.parentElement.closest('.ws-ic')) texts.push(n);
  if (!texts.length || !el.getClientRects().length) return [];
  const label = el.textContent.trim();
  texts.forEach((n) => { n.data = n.data.replace(/\\S/g, 'H'); });
  el.dataset.probe = label;
  return [{ cls: String(el.className).split(' ')[0], label }];
})"""

# In the page: scroll one probed control into view and return where to look for its H's
# (viewport px), or what is drawn over it.
SPOT_JS = """([i]) => {
  const el = document.querySelectorAll('[data-probe]')[i], cs = getComputedStyle(el);
  el.scrollIntoView({ block: 'center', inline: 'center' });
  const r = el.getBoundingClientRect(), texts = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) if (n.data.trim() && !n.parentElement.closest('.ws-ic')) texts.push(n);
  const runs = texts.map((n) => { const g = document.createRange(); g.selectNodeContents(n); const b = g.getBoundingClientRect(); return [b.left, b.right]; });
  const mid = [(runs[0][0] + runs[0][1]) / 2, (r.top + r.bottom) / 2], hit = document.elementFromPoint(...mid);
  // A Choice face sits under its own (transparent) radio input, in the same label: that is not covered.
  const own = el.closest('label'), over = hit && !el.contains(hit) && !(own && own.contains(hit))
    ? hit.localName + (String(hit.className.baseVal ?? hit.className).split(' ')[0].replace(/^(?=.)/, '.')) : null;
  let bg = cs.backgroundColor;
  for (let p = el; bg === 'rgba(0, 0, 0, 0)' && p.parentElement; p = p.parentElement) bg = getComputedStyle(p.parentElement).backgroundColor;
  return { runs, over, bg: bg.match(/[\\d.]+/g).slice(0, 3).map(Number),
           top: r.top + parseFloat(cs.borderTopWidth), bottom: r.bottom - parseFloat(cs.borderBottomWidth) };
}"""

def font_fallbacks(cdp):
    """Every element and pseudo-element drawn (in part) in a family that is not the bundled one."""
    found, stack = [], [cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})["root"]]
    while stack:
        n = stack.pop()
        if n["nodeType"] == 1:
            try:
                fonts = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": n["nodeId"]})["fonts"]
            except Exception:
                fonts = []  # not rendered
            found += [f"<{n['localName'] or n.get('pseudoType')}> in {f['familyName']}" for f in fonts if f["familyName"] not in families]
            stack += n.get("pseudoElements", [])
        stack += n.get("children", [])
    return sorted(set(found))

def icon_names(cdp):
    return sorted({f"{n['role']['value']} \"{n['name']['value']}\"".encode("unicode_escape").decode()
                   for n in cdp.send("Accessibility.getFullAXTree")["nodes"]
                   if not n.get("ignored") and PUA.search(n.get("name", {}).get("value", "") or "")})

def centring(page, i):
    """Scroll probed control i into view; offset of its capitals' ink centre from its box centre
    (px, + is low), None when no ink is visible, or the element drawn over it."""
    s = page.evaluate(SPOT_JS, [i])
    if s["over"]:
        return None, s["over"]
    x0, x1 = min(l for l, r in s["runs"]), max(r for l, r in s["runs"])
    clip = dict(x=x0, y=s["top"], width=x1 - x0, height=s["bottom"] - s["top"])
    im = Image.open(io.BytesIO(page.screenshot(clip=clip))).convert("RGB"); px = im.load()
    # Past a border snapped to the device grid: skip the edge rows and columns of the clip.
    cols = [x for l, r in s["runs"] for x in range(max(0, int((l - x0) * DPR) + 1), min(im.width, int((r - x0) * DPR)))]
    rows = [y for y in range(2, im.height - 1) if any(sum(abs(a - b) for a, b in zip(px[x, y], s["bg"])) > 120 for x in cols)]
    return (None if not rows else (rows[0] + rows[-1] + 1) / 2 / DPR - im.height / 2 / DPR), None

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(root / "build" / "previews"))
    out = pathlib.Path(ap.parse_args().out); out.mkdir(parents=True, exist_ok=True)
    previews = sorted(p for p in (root / "components").glob("*/preview.html"))
    if not previews:
        print("FAIL no components/*/preview.html found"); return 1
    bad, pages, counts = 0, 0, dict(controls=0, choices=0, sized=0)
    def fail(where, msg):
        nonlocal bad; bad += 1; print(f"FAIL {where}: {msg}")
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        browser = pw.chromium.launch()
        for device, opts in DEVICES:
            for theme in themes:
                ctx = browser.new_context(device_scale_factor=DPR, **opts)
                page = ctx.new_page(); cdp = ctx.new_cdp_session(page)
                for d in ("DOM", "CSS", "Accessibility"): cdp.send(f"{d}.enable")
                for p in previews:
                    name, where = p.parent.name, f"{p.parent.name} {theme} {device}"
                    html = pathlib.Path(tmp) / f"{name}-{theme}-{device}.html"
                    html.write_text(PAGE.format(theme=theme, fragment=p.read_text(),
                        tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri()))
                    page.goto(html.as_uri()); page.evaluate("document.fonts.ready")
                    page.screenshot(path=str(out / f"{name}-{theme}-{device}.png"), full_page=True)
                    pages += 1
                    for f in font_fallbacks(cdp): fail(where, f"fonts: {f}")
                    for n in icon_names(cdp): fail(where, f"names: icon glyph in {n}")
                    lay = page.evaluate(LAYOUT_JS, [SIZED])
                    if device == "phone" and name not in FIXED_SIZE:
                        if lay["scroll"] > 0: fail(where, f"overflow: page scrolls sideways by {lay['scroll']}px")
                        for c in lay["cut"]: fail(where, f"overflow: {c}")
                    if device != "phone" or name not in FIXED_SIZE:
                        for c in lay["spill"]: fail(where, f"overflow: {c}")
                    for c in lay["choice"]:
                        counts["choices"] += 1
                        if not c["ok"]: fail(where, f"choice: '{c['label']}' ({'chosen' if c['checked'] else 'not chosen'}) is drawn wrong")
                    for h in lay["heights"]:
                        counts["sized"] += 1
                        if abs(h["h"] - lay["controlH"]) > 0.5: fail(where, f"height: {h['cls']} '{h['label']}' is {h['h']:.2f}px, control-h is {lay['controlH']:.2f}px")
                    for i, it in enumerate(page.evaluate(PROBE_JS, [CONTROLS])):
                        counts["controls"] += 1
                        off, over = centring(page, i)
                        if over: fail(where, f"centring: {it['cls']} '{it['label']}' is covered by {over}")
                        elif off is None: fail(where, f"centring: no label ink found in {it['cls']} '{it['label']}'")
                        elif abs(off) > CENTRE_TOL: fail(where, f"centring: {it['cls']} '{it['label']}' is {off:+.2f}px off centre")
                ctx.close()
        browser.close()
    print(f"\n{pages} pages ({len(previews)} previews x {len(DEVICES)} devices x {len(themes)} themes); "
          f"{counts['controls']} labels measured for centring, {counts['choices']} choice options, {counts['sized']} control heights checked")
    print(f"screenshots in {out}")
    print("%d failing" % bad)
    return 1 if bad or not counts["controls"] else 0

if __name__ == "__main__":
    sys.exit(main())
