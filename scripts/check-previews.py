#!/usr/bin/env python3
"""Render every components/*/preview.html and check what a reader would see. Fails (exit 1) on a defect.

Run from the project folder:  uv run python scripts/check-previews.py [--out DIR]
Needs: playwright and pillow (pyproject.toml; uv run installs them), and Chromium for
Playwright (uv run python -m playwright install chromium; a cloud session already has it).

Each preview is loaded with tokens.css then components/bundle.css, in every theme, on a phone
(375 px wide, touch) and a desktop (960 px), each in a fresh page, and screenshot into DIR
(default build/previews) after it is checked. Chromium switches the touch emulation off for any
capture beyond the window (Playwright's full-page screenshot, and CDP's captureBeyondViewport),
which drew every phone screenshot as a mouse screen; so the window is grown to the page's
height and that is captured (vh units grow with it). The run fails if the emulation is not what
the device says, before the checks, after them, or when the screenshot is drawn.
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
5. height:   buttons, Sides toggles and rail buttons are control-h tall; inputs, selects,
             PieceMap cells, Disclosure summaries and Choice faces (a long label wraps on a
             narrow screen) are at least that tall. On the phone control-h is tap (44px).
6. names:    no accessible name carries an icon glyph (Private Use Area): icons are hidden.
7. stage:    everything drawn in a stage view lies inside it, on both devices: the part
             always fits the stage (DESIGN.md, D15). A large canvas put into each stage view,
             as a tool puts its 3D view, fills it exactly and leaves its size alone (a canvas
             that sizes its stage feeds every resize back into itself); an empty stage
             message takes no room, and a message with text sits on surface-raised, not on
             the model.
8. scheme:   the page's color-scheme is its theme, so the browser's own controls (scroll
             bars, number spinners, lists) follow it.
9. hints:    a status bar shows the touch hint on a touch screen and the mouse hint
             otherwise, never both.
10. notice:  the error and warning Notices take their border and headline colour from
             their token, and an empty Notice takes no room.
    Empty live regions (a Notice, the stage message) take no room but stay in the page and
    the accessibility tree (not display:none), so a screen reader announces them when they fill.
15. live:    errors (.ws-error), the plan line, and every empty Notice or stage message are
             aria-live regions; an invalid field (aria-invalid) is described by an element
             that says what is wrong (aria-describedby), so its error is read with it (Field).
11. plan:    side by side, a plan bar's sentence is never narrower than plan-line-basis (or
             than the bar, when the bar is narrower): below it the buttons move under it. On
             a phone, where the plan bar is pinned under the view, it is one row: the sentence,
             at most two lines, beside the primary button (D25).
16. view:    the 3D view gets at least 40 % of the screen's height (D25), and a control in the
             sidebar, once focused, is on screen and not covered by the pinned stage (WCAG
             2.4.11). LAYOUT_DEVICES add a short phone, a landscape phone and a small zoomed
             screen, for the previews with a workbench.
12. primary: at most one primary button in view (Button).
13. units:   a field whose label ends in a unit in brackets, "Width (mm)", asks for a numeric
             keyboard: inputmode decimal or numeric, or type number (Field).
14. markup:  read from the files, not rendered: every component folder has a preview.html and a
             README.md; a preview's inline styles set only the card's own size (STYLE_OK), never
             spacing, colour, font or display, so a preview shows the stylesheet, not an
             override of it; a <style> block only in the covers and the Icons catalogue.
Every check counts what it looked at, prints the counts, and fails the run if one is zero: a
selector that matches nothing passes everything.
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
LAYOUT_DEVICES = [("phone-667", dict(viewport={"width": 375, "height": 667}, has_touch=True, is_mobile=True)),
                  ("landscape", dict(viewport={"width": 844, "height": 390}, has_touch=True, is_mobile=True)),
                  ("zoomed", dict(viewport={"width": 320, "height": 256}))]   # 1280 x 1024 at 400 %
BP_PX = 16 * float(next(x["value"] for x in tok["spacing"]["tokens"] if x["name"] == "breakpoint-wide").rstrip("rem"))
DPR = 2                 # screenshots at 2x, so the centring scan resolves half pixels
CENTRE_TOL = 1.5        # px; Chromium rounds the baseline to whole pixels (up to about 1.2 px measured)
FIXED_SIZE = {"Cover", "CoverSkadisAir"}  # 960 x 288 art for use outside the tools, never in them (their READMEs)
CONTROLS = ".ws-btn, .ws-choice__face, .ws-sides__btn, .ws-rail__btn, .ws-piece"
SIZED = ".ws-btn, .ws-sides__btn, .ws-rail__btn"                       # exactly control-h
AT_LEAST = ".ws-input, .ws-piece, .ws-summary, .ws-choice__face"        # control-h or more: a long Choice label wraps on a narrow screen
PUA = re.compile("[\ue000-\uf8ff]")
STYLE_OK = {"max-width", "width", "height", "grid-template-columns"}   # the card's own size
STYLE_BLOCK_OK = FIXED_SIZE | {"Icons"}   # art, and the catalogue of glyphs

PAGE = """<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{tokens}"><link rel="stylesheet" href="{bundle}">
</head><body class="ws-page">{fragment}</body></html>"""

# In the page: load every declared font face, then let layout catch up, before anything is read.
# fonts.ready alone can resolve before a face is even requested, and a face that has just loaded
# (font-display: swap) is drawn only after the next layout; reading earlier sees the fallback.
# Returns the faces that failed to load.
SETTLE_JS = """() => Promise.all([...document.fonts].map((f) => f.load().then(() => null, () => `${f.family} ${f.weight} ${f.style}`)))
  .then((bad) => document.fonts.ready.then(() => new Promise((done) => {
    document.body.offsetHeight;
    requestAnimationFrame(() => requestAnimationFrame(() => done(bad.filter(Boolean))));
  })))"""

# In the page: what the overflow, choice and height checks read.
LAYOUT_JS = """([sized, atLeast]) => {
  const vw = document.documentElement.clientWidth, cut = [], spill = [];
  for (const el of document.body.querySelectorAll('*')) {
    const ox = getComputedStyle(el).overflowX, id = `${el.localName}.${String(el.className.baseVal ?? el.className).split(' ')[0]}`;
    if (el.scrollWidth <= el.clientWidth + 1 || !el.clientWidth || el.closest('svg')) continue;
    if ((ox === 'hidden' || ox === 'clip') && getComputedStyle(el).textOverflow !== 'ellipsis') cut.push(`${id} shows ${el.clientWidth} of ${el.scrollWidth}px`);   // an ellipsis is a cut on purpose
    else if (ox === 'visible') spill.push(`${id} is ${el.clientWidth}px wide, its content ${el.scrollWidth}px`);
  }
  const probe = document.createElement('div');
  probe.style.height = 'var(--control-h)'; document.body.append(probe);
  const controlH = probe.getBoundingClientRect().height;
  const colour = (v) => { probe.style.color = v; return getComputedStyle(probe).color; };
  const s = getComputedStyle(document.documentElement);
  const t = { action: colour(s.getPropertyValue('--action')), onAction: colour(s.getPropertyValue('--on-action')),
              raised: colour(s.getPropertyValue('--surface-raised')) };
  const choice = [...document.querySelectorAll('.ws-choice__input')].map((inp) => {
    const face = inp.nextElementSibling, f = getComputedStyle(face), m = getComputedStyle(face, '::before');
    const ok = inp.checked
      ? f.backgroundColor === t.action && m.backgroundColor === t.onAction && m.borderTopColor === t.action && m.boxShadow.includes(t.onAction)
      : f.backgroundColor === t.raised && m.backgroundColor === 'rgba(0, 0, 0, 0)' && parseFloat(m.width) > 0;
    return { label: face.textContent, checked: inp.checked, ok };
  });
  const size = (sel, exact) => [...document.querySelectorAll(sel)].filter((e) => e.getClientRects().length)
    .map((e) => ({ cls: String(e.className).split(' ')[0], label: (e.textContent.trim() || e.value || '').slice(0, 40), exact, h: e.getBoundingClientRect().height }));
  const heights = [...size(sized, true), ...size(atLeast, false)];
  const stage = [...document.querySelectorAll('.ws-stage__view')].flatMap((view) => {
    const v = view.getBoundingClientRect();
    return [...view.querySelectorAll('*')].map((e) => [e, e.getBoundingClientRect()])
      .filter(([, r]) => r.width && (r.left < v.left - 0.5 || r.top < v.top - 0.5 || r.right > v.right + 0.5 || r.bottom > v.bottom + 0.5))
      .map(([e, r]) => `${e.localName} at ${Math.round(r.left)},${Math.round(r.top)} to ${Math.round(r.right)},${Math.round(r.bottom)} in a stage view at ${Math.round(v.left)},${Math.round(v.top)} to ${Math.round(v.right)},${Math.round(v.bottom)}`);
  });
  for (const view of document.querySelectorAll('.ws-stage__view')) {
    const was = view.getBoundingClientRect(), c = document.createElement('canvas');
    c.width = 3000; c.height = 3000; view.append(c);
    const v = view.getBoundingClientRect(), r = c.getBoundingClientRect(), px = (b) => `${Math.round(b.width)} x ${Math.round(b.height)}`;
    if (Math.abs(v.width - was.width) > 0.5 || Math.abs(v.height - was.height) > 0.5) stage.push(`a canvas resizes its stage view from ${px(was)} to ${px(v)}`);
    if ([r.left - v.left, r.top - v.top, r.right - v.right, r.bottom - v.bottom].some((d) => Math.abs(d) > 0.5)) stage.push(`a canvas is ${px(r)} in a stage view of ${px(v)}, not filling it`);
    c.remove();
  }
  const gone = (e) => getComputedStyle(e).display === 'none' || getComputedStyle(e).visibility === 'hidden';
  for (const m of document.querySelectorAll('.ws-stage__message:empty')) {
    if (gone(m)) stage.push('an empty stage message is hidden from the accessibility tree; collapse it instead');
    else if (m.getBoundingClientRect().height > 0.5) stage.push('an empty stage message takes room');
    m.textContent = 'Building the part…';
    if (getComputedStyle(m).backgroundColor !== colour(s.getPropertyValue('--surface-raised'))) stage.push('the stage message has no surface-raised backing; on the model its text can vanish');
    m.textContent = '';
  }
  const scheme = getComputedStyle(document.documentElement).colorScheme;
  const shown = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const hints = [...document.querySelectorAll('.ws-status')].map((bar) => ({
    fine: [...bar.querySelectorAll('.ws-hint-fine')].some(shown),
    touch: [...bar.querySelectorAll('.ws-hint-touch')].some(shown),
  }));
  const notices = [];
  for (const [variant, token] of [['error', '--error'], ['warning', '--warning']]) {
    const want = colour(s.getPropertyValue(token));
    for (const n of document.querySelectorAll(`.ws-notice--${variant}`)) {
      const head = n.querySelector('strong');
      if (getComputedStyle(n).borderTopColor !== want) notices.push(`the ${variant} Notice's border is not ${token}`);
      if (head && getComputedStyle(head).color !== want) notices.push(`the ${variant} Notice's headline is not ${token}`);
    }
  }
  for (const n of document.querySelectorAll('.ws-notice:empty')) {
    if (gone(n)) notices.push('an empty Notice is hidden from the accessibility tree; collapse it instead');
    else if (n.getBoundingClientRect().height > 0.5) notices.push('an empty Notice takes room');
  }
  const live = (e) => !!e.closest('[aria-live], [role=status], [role=alert]');
  const liveness = [];
  for (const e of document.querySelectorAll('.ws-error, .ws-plan__line, .ws-notice:empty, .ws-stage__message:empty'))
    if (!live(e)) liveness.push(`${e.className.split(' ')[0]} is not an aria-live region`);
  for (const e of document.querySelectorAll('[aria-invalid="true"]')) {
    const said = (e.getAttribute('aria-describedby') || '').split(/\s+/).map((id) => document.getElementById(id)).filter((d) => d && d.textContent.trim());
    if (!said.length) liveness.push(`the invalid field '${e.closest('label')?.firstChild?.data?.trim() ?? e.name}' is described by nothing that says what is wrong`);
  }
  probe.style.width = 'var(--plan-line-basis)';
  const basis = probe.getBoundingClientRect().width, plan = [];
  for (const line of document.querySelectorAll('.ws-plan__line')) {
    const bar = line.parentElement, bs = getComputedStyle(bar), w = line.getBoundingClientRect().width;
    const room = bar.clientWidth - parseFloat(bs.paddingLeft) - parseFloat(bs.paddingRight);
    const stacked = getComputedStyle(bar.closest('.ws-stage') || bar).display === 'contents';
    if (stacked) {
      const mid = (e) => { const r = e.getBoundingClientRect(); return (r.top + r.bottom) / 2; };
      if ([...bar.children].some((c) => Math.abs(mid(c) - mid(line)) > 1)) plan.push('on a phone the plan bar is not one row');
      if (line.getBoundingClientRect().height > 2 * parseFloat(getComputedStyle(line).lineHeight) + 1) plan.push('on a phone the plan sentence takes more than two lines');
    } else if (line.getClientRects().length && w < Math.min(basis, room) - 0.5) plan.push(`the sentence is ${Math.round(w)}px wide, plan-line-basis is ${Math.round(basis)}px`);
  }
  for (const h of document.querySelectorAll('.ws-header'))
    if (h.scrollWidth > h.clientWidth + 1) stage.push(`the header scrolls sideways (${h.scrollWidth} in ${h.clientWidth}px); its actions belong in More… (D28)`);
  for (const v of document.querySelectorAll('.ws-stage__view')) {
    const h = v.getBoundingClientRect().height;
    if (h < 0.4 * innerHeight - 0.5) stage.push(`the 3D view is ${Math.round(h)}px tall, under 40 % of a ${innerHeight}px screen`);
  }
  probe.remove();
  const primaries = [...document.querySelectorAll('.ws-btn--primary')].filter(shown).length;
  const units = [...document.querySelectorAll('input.ws-input')].filter((i) => i.type !== 'radio').map((i) => {
    const l = i.closest('label'), text = l ? [...l.childNodes].filter((n) => n.nodeType === 3).map((n) => n.data).join('').trim() : '';
    return { label: text, unit: /\([^)]+\)$/.test(text), ok: i.type === 'number' || ['decimal', 'numeric'].includes(i.inputMode) };
  }).filter((u) => u.unit);
  const seen = { stages: document.querySelectorAll('.ws-stage__view').length, bars: hints.length,
                 live: document.querySelectorAll('.ws-error, .ws-plan__line, .ws-notice:empty, .ws-stage__message:empty').length,
                 invalid: document.querySelectorAll('[aria-invalid="true"]').length,
                 variants: document.querySelectorAll('.ws-notice--error, .ws-notice--warning').length,
                 lines: document.querySelectorAll('.ws-plan__line').length, units: units.length };
  return { scroll: document.documentElement.scrollWidth - vw, cut, spill, choice, heights, controlH, stage, scheme, hints, notices, plan,
           primaries, units, liveness, seen, coarse: matchMedia('(pointer: coarse)').matches };
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

# In the page: focus each control in the sidebar, as a keyboard user would, and say which end up off
# the screen or under something else (the pinned stage); then put the page back.
FOCUS_JS = """() => {
  const out = []; let n = 0;
  for (const el of document.querySelectorAll('.ws-side :is(button, input, select, textarea, a[href], summary)')) {
    if (!el.getClientRects().length) continue;
    n++; el.focus();
    const r = el.getClientRects()[0], x = (r.left + r.right) / 2, y = (r.top + r.bottom) / 2;   // a wrapped link: its first line
    const own = el.closest('label'), name = (own || el).textContent.trim().slice(0, 30) || el.value || el.localName;
    if (y < 0 || y > innerHeight) { out.push(`'${name}' is off the screen when focused`); continue; }
    const hit = document.elementFromPoint(x, y);
    if (hit && !el.contains(hit) && !(own && own.contains(hit))) out.push(`'${name}' is under ${hit.localName}.${String(hit.className).split(' ')[0]} when focused`);
  }
  document.activeElement && document.activeElement.blur(); scrollTo(0, 0);
  return { out, n };
}"""

# In the page: scroll one probed control into view and return where to look for its H's
# (viewport px), or why it cannot be looked at: drawn over, or still outside the window.
SPOT_JS = """([i]) => {
  const el = document.querySelectorAll('[data-probe]')[i], cs = getComputedStyle(el);
  el.scrollIntoView({ block: 'center', inline: 'center' });
  const r = el.getBoundingClientRect(), texts = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) if (n.data.trim() && !n.parentElement.closest('.ws-ic')) texts.push(n);
  const runs = texts.map((n) => { const g = document.createRange(); g.selectNodeContents(n); const b = g.getBoundingClientRect(); return [b.left, b.right]; });
  const mid = [(runs[0][0] + runs[0][1]) / 2, (r.top + r.bottom) / 2], hit = document.elementFromPoint(...mid);
  // A Choice face sits under its own (transparent) radio input, in the same label: that is not covered.
  const own = el.closest('label'), de = document.documentElement;
  const over = r.left < -0.5 || r.top < -0.5 || r.right > de.clientWidth + 0.5 || r.bottom > de.clientHeight + 0.5
    ? 'lies outside the window, even scrolled to'
    : hit && !el.contains(hit) && !(own && own.contains(hit))
    ? 'is covered by ' + hit.localName + (String(hit.className.baseVal ?? hit.className).split(' ')[0].replace(/^(?=.)/, '.')) : null;
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
    (px, + is low), None when no ink is visible, or why it could not be measured."""
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

def record(page, path, grow):
    """Screenshot the page with the emulation intact. A phone keeps its own height, so the record
    shows what the phone shows (D25). Otherwise grow the window until the page fits: a page in vh
    units grows with the window, so stop when a round no longer brings it closer (a page of 100vh
    and a border never fits, and then loses that border's pixels)."""
    if not grow:
        page.screenshot(path=path); return
    w, gap = page.viewport_size["width"], None
    for _ in range(10):
        h, have = page.evaluate("document.documentElement.scrollHeight"), page.viewport_size["height"]
        if h <= have or (gap is not None and h - have >= gap): break
        gap = h - have
        page.set_viewport_size({"width": w, "height": h})
    page.screenshot(path=path)

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(root / "build" / "previews"))
    out = pathlib.Path(ap.parse_args().out); out.mkdir(parents=True, exist_ok=True)
    previews = sorted(p for p in (root / "components").glob("*/preview.html"))
    if not previews:
        print("FAIL no components/*/preview.html found"); return 1
    bad, pages = 0, 0
    counts = dict(controls=0, choices=0, sized=0, primary=0, units=0, stages=0, bars=0, variants=0, lines=0, live=0, invalid=0, focus=0, markup=0)
    def fail(where, msg):
        nonlocal bad; bad += 1; print(f"FAIL {where}: {msg}")
    for d in sorted(p for p in (root / "components").iterdir() if p.is_dir()):
        for need in ("preview.html", "README.md"):
            if not (d / need).is_file(): fail(d.name, f"markup: no {need}")
    for p in previews:
        name, src = p.parent.name, p.read_text(encoding="utf-8")
        counts["markup"] += 1
        if name not in FIXED_SIZE:
            for style in re.findall(r'\sstyle="([^"]*)"', src):
                extra = sorted({d.split(":")[0].strip() for d in style.split(";") if d.strip()} - STYLE_OK)
                if extra: fail(name, f"markup: an inline style sets {', '.join(extra)}; use the stylesheet ({style})")
        if name not in STYLE_BLOCK_OK and "<style" in src: fail(name, "markup: a <style> block; use the stylesheet")
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        browser = pw.chromium.launch()
        for device, opts in DEVICES + LAYOUT_DEVICES:
            for theme in themes:
                ctx = browser.new_context(device_scale_factor=DPR, **opts)
                touch = opts.get("has_touch", False)
                narrow = opts["viewport"]["width"] < BP_PX
                for p in previews:
                    if (device, opts) in LAYOUT_DEVICES and "ws-workbench" not in p.read_text(encoding="utf-8"):
                        continue
                    name, where = p.parent.name, f"{p.parent.name} {theme} {device}"
                    html = pathlib.Path(tmp) / f"{name}-{theme}-{device}.html"
                    html.write_text(PAGE.format(theme=theme, fragment=p.read_text(),
                        tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri()))
                    page = ctx.new_page(); cdp = ctx.new_cdp_session(page)
                    for d in ("DOM", "CSS", "Accessibility"): cdp.send(f"{d}.enable")
                    page.goto(html.as_uri())
                    for f in page.evaluate(SETTLE_JS): fail(where, f"fonts: {f} did not load")
                    pages += 1
                    for f in font_fallbacks(cdp): fail(where, f"fonts: {f}")
                    for n in icon_names(cdp): fail(where, f"names: icon glyph in {n}")
                    lay = page.evaluate(LAYOUT_JS, [SIZED, AT_LEAST])
                    if lay["coarse"] != touch: fail(where, f"setup: touch emulation is {'on' if lay['coarse'] else 'off'}, expected {'on' if touch else 'off'}")
                    if narrow and name not in FIXED_SIZE:
                        if lay["scroll"] > 0: fail(where, f"overflow: page scrolls sideways by {lay['scroll']}px")
                        for c in lay["cut"]: fail(where, f"overflow: {c}")
                    if not narrow or name not in FIXED_SIZE:
                        for c in lay["spill"]: fail(where, f"overflow: {c}")
                    for c in lay["stage"]: fail(where, f"stage: {c}")
                    if lay["scheme"] != theme: fail(where, f"scheme: color-scheme is '{lay['scheme']}', the theme is {theme}")
                    for h in lay["hints"]:
                        if not (h["touch"] if touch else h["fine"]) or (h["fine"] if touch else h["touch"]):
                            fail(where, f"hints: the status bar shows the mouse hint {'yes' if h['fine'] else 'no'}, the touch hint {'yes' if h['touch'] else 'no'}")
                    for n in lay["notices"]: fail(where, f"notice: {n}")
                    for n in lay["plan"]: fail(where, f"plan: {n}")
                    counts["primary"] += 1
                    if lay["primaries"] > 1: fail(where, f"primary: {lay['primaries']} primary buttons in view; at most one (Button)")
                    for u in lay["units"]:
                        if not u["ok"]: fail(where, f"units: '{u['label']}' gets a text keyboard; give it inputmode=\"decimal\" (Field)")
                    for n in lay["liveness"]: fail(where, f"live: {n}")
                    for k, v in lay["seen"].items(): counts[k] += v
                    foc = page.evaluate(FOCUS_JS); counts["focus"] += foc["n"]
                    for n in foc["out"]: fail(where, f"view: {n}")
                    for c in lay["choice"]:
                        counts["choices"] += 1
                        if not c["ok"]: fail(where, f"choice: '{c['label']}' ({'chosen' if c['checked'] else 'not chosen'}) is drawn wrong")
                    for h in lay["heights"]:
                        counts["sized"] += 1
                        if (abs(h["h"] - lay["controlH"]) if h["exact"] else lay["controlH"] - h["h"]) > 0.5:
                            fail(where, f"height: {h['cls']} '{h['label']}' is {h['h']:.2f}px, control-h is {lay['controlH']:.2f}px")
                    for i, it in enumerate(page.evaluate(PROBE_JS, [CONTROLS])):
                        counts["controls"] += 1
                        off, over = centring(page, i)
                        if over: fail(where, f"centring: {it['cls']} '{it['label']}' {over}")
                        elif off is None: fail(where, f"centring: no label ink found in {it['cls']} '{it['label']}'")
                        elif abs(off) > CENTRE_TOL: fail(where, f"centring: {it['cls']} '{it['label']}' is {off:+.2f}px off centre")
                    if page.evaluate("matchMedia('(pointer: coarse)').matches") != touch: fail(where, "setup: touch emulation changed during the checks")
                    page.reload(); page.evaluate(SETTLE_JS)   # the real labels back, for the record
                    page.evaluate("scrollTo(0, 0)")            # a reload keeps the scroll the checks left
                    record(page, str(out / f"{name}-{theme}-{device}.png"), grow=not narrow)
                    if page.evaluate("matchMedia('(pointer: coarse)').matches") != touch: fail(where, "setup: the screenshot was drawn with touch emulation changed")
                    page.close()
                ctx.close()
        browser.close()
    print(f"\n{pages} pages ({len(previews)} previews x {len(DEVICES)} devices x {len(themes)} themes, and the workbench on {len(LAYOUT_DEVICES)} more); "
          f"{counts['controls']} labels measured for centring, {counts['choices']} choice options, {counts['sized']} control heights checked")
    print("looked at: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    for k, v in counts.items():
        if not v: fail("run", f"{k}: nothing to check; a selector or a preview has gone missing")
    print(f"screenshots in {out}")
    print("%d failing" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
