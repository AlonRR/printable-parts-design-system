#!/usr/bin/env python3
"""Render every components/*/preview.html and check what a reader would see. Fails (exit 1) on a defect.

Run from the project folder:  uv run python scripts/check-previews.py [--out DIR] [--only Button,...]
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
             beyond it or scrolls sideways inside it (a popover is overflow:auto by default).
             FIXED_SIZE previews are fixed-size art and skipped on the phone.
3. choice:   the chosen Choice is action-tint with an action ring and its radio shows an action
             dot; the others are surface-raised with a hollow radio (D26). Selected states are
             tint and ring: only a primary button is filled with action. A Sides button draws
             its box pressed or not, the same size, so pressing never moves the layout, and the
             box is the radio's size.
   marks:    the tick in a pressed Sides box sits within CENTRE_TOL of the box's centre, both
             ways, measured on its pixels, as a label does: drawn in its own cell, or with its
             own gap, it misses the box.
4. centring: the capitals of each control's label sit within CENTRE_TOL of the box's centre,
             measured on the pixels of a capital H drawn in place of the label. Each control
             is scrolled into view first (a toolbar or sidebar may scroll), and fails if
             something else is drawn over it.
5. height:   buttons, Sides toggles, rail buttons and one-line Choice faces are control-h tall;
             inputs, selects, PieceMap cells, Disclosure summaries, tiles and a Choice face that
             wraps a long label on a narrow screen are at least that tall. On a touch screen
             control-h is at least TAP_MIN (44px, WCAG 2.5.5), whatever the tap token says.
6. names:    no accessible name carries an icon glyph (Private Use Area): icons are hidden.
7. stage:    everything drawn in a stage view lies inside it, on both devices: the part
             always fits the stage (DESIGN.md, D15). A large canvas put into each stage view,
             as a tool puts its 3D view, fills it exactly and leaves its size alone (a canvas
             that sizes its stage feeds every resize back into itself); an empty stage
             message takes no room, and a message with text sits on surface-raised, not on
             the model. The view works without a pointer (D30): its drawing takes focus, with a
             ring inside the view, and is an image named and described by the plan line;
             Reset view, Zoom in, Zoom out and a view choice sit in it, none over another, and
             a drag between them still reaches the drawing. On a phone or a short screen only
             Reset view and View… show, and View… opens the rest in a menu under it (D36).
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
17. data:    the plan line, inputs, the status bar and code show text as typed: ligatures off
             (calt 0), so "1280x420mm" never becomes "1280×420mm" (D29).
18. rail:    a step button says its step's name beside its number ("2 Window"), so the name
             is seen and announced (D31).
16. view:    the 3D view gets at least 40 % of the screen's height (D25), and a control in the
             sidebar, once focused, going down the form and back up, is on screen and not
             covered by the pinned stage (WCAG 2.4.11). LAYOUT_DEVICES add a short phone, two
             landscape phones, a small zoomed screen and the narrowest wide screen (the
             breakpoint), for the previews with a workbench or a header.
12. primary: at most one primary button in view (Button).
13. units:   a field whose label ends in a unit in brackets, "Width (mm)", asks for a numeric
             keyboard: inputmode decimal or numeric, or type number (Field).
14. markup:  read from the files, not rendered: every component folder has a preview.html and a
             README.md; a preview's inline styles set only the card's own size (STYLE_OK), never
             spacing, colour, font or display, so a preview shows the stylesheet, not an
             override of it; a <style> block only in the covers and the Icons catalogue.
19. selectors: read from this file: every class it looks for is one a preview uses, so a
             misspelt selector, which would check nothing, fails.
20. states:  focused, every control shows an action ring at least RING_MIN (2px, WCAG 2.4.13)
             wide that no box clips; hovered (CDP forces :hover), an enabled one changes and a
             disabled one does not; selected (pressed, chosen or current), it is tinted and
             ringed, with an action border and a bold label (D26; not a PieceMap cell, whose
             bold says it has its own fill), and nothing else is tinted; disabled, it is faded;
             an invalid field is outlined in error, and an error message is in error.
21. header:  on a wide screen the header's actions are all on show in its row and More… is not;
             below the breakpoint More… opens them in a menu under the header, on the screen (D28).
22. pinned:  scrolled down on a phone, the 3D view is pinned to the top and the plan bar under it
             (D25).
23. aria:    every tile, PieceMap cell and Sides toggle has aria-pressed; every Choice is a named
             radiogroup of radios; Sides is a named group; the step rail is named and has a
             current step; every popovertarget names a popover; the theme toggle has aria-pressed.
24. text:    every run of text, as drawn and with each control hovered, has 4.5:1 against the
             background behind it, its own and its ancestors' composed (3:1 when large): what is
             drawn, not the token pairs check-contrast.py lists. Text in a faded (disabled)
             control, text for assistive tech only, SVG text and icons are left out.
25. coverage: read from the files: every class bundle.css styles is shown by a preview and named
             in a doc (README.md, DESIGN.md, a component README), and every class a doc names is
             one the system has; so a deleted component, a dropped variant or a README left
             naming a removed class fails, which no total would show.
26. forced:  in forced colours (once per preview, on a desktop), a chosen Choice and an unchosen
             one, a pressed toggle and one not pressed, and the current, a done and a later step
             each look different, by what is drawn; a Choice's radio and a Sides box and tick differ
             on their own (--device forced runs this alone).
27. dialog:  each dialog, opened as a modal as a tool opens it, keeps space-4 from the screen's
             edges and has the scrim behind it, not the browser's own backdrop.
28. rhythm:  the first item under a fieldset's legend sits space-3 below it, and a note space-1
             under the group it explains, as tokens.json's usage says.
Every check counts what it looked at, prints the counts, and fails the run if one is zero: a
selector that matches nothing passes everything. --only, --device and --theme render a part of
the run, for tests/test-check-previews.sh, which holds every check to a control; a part may count
zero, so the zero rule applies to the whole run only.
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
                  ("landscape-wide", dict(viewport={"width": 932, "height": 430}, has_touch=True, is_mobile=True)),   # wide and short
                  ("zoomed", dict(viewport={"width": 320, "height": 256}))]   # 1280 x 1024 at 400 %
SPACE = {x["name"]: x["value"] for x in tok["spacing"]["tokens"]}
LAYOUT_DEVICES.append(("breakpoint", dict(viewport={"width": round(16 * float(SPACE["breakpoint-wide"].rstrip("rem"))), "height": 800})))   # the narrowest wide screen
BP_PX = 16 * float(SPACE["breakpoint-wide"].rstrip("rem"))
WIDE, SHORT = f"(min-width:{SPACE['breakpoint-wide']})", f"(max-height:{SPACE['breakpoint-short']})"   # as bundle.css has them
DPR = 2                 # screenshots at 2x, so the centring scan resolves half pixels
CENTRE_TOL = 1.5        # px; Chromium rounds the baseline to whole pixels (up to about 1.2 px measured)
RING_MIN = 2            # px: the thinnest focus ring, the 2 CSS px WCAG 2.4.13 asks for (not the ring token, which a mistake can shrink)
TAP_MIN = 44            # px: the least control-h on a touch screen, WCAG 2.5.5's 44 x 44 (not the tap token, likewise)
FIXED_SIZE = {"Cover", "CoverSkadisAir"}  # 960 x 288 art for use outside the tools, never in them (their READMEs)
CONTROLS = ".ws-btn, .ws-choice__face, .ws-sides__btn, .ws-rail__btn, .ws-piece"
SIZED = ".ws-btn, .ws-sides__btn, .ws-rail__btn"                       # exactly control-h
MARKS = '.ws-sides__btn[aria-pressed="true"]'   # a glyph drawn in a box: the Sides tick
AT_LEAST = ".ws-input, .ws-piece, .ws-summary, .ws-choice__face, .ws-tile"   # control-h or more; a Choice face of one line is exact
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
LAYOUT_JS = """([sized, atLeast, wideQuery, shortQuery]) => {
  const vw = document.documentElement.clientWidth, cut = [], spill = [];
  for (const el of document.body.querySelectorAll('*')) {
    const ox = getComputedStyle(el).overflowX, id = `${el.localName}.${String(el.className.baseVal ?? el.className).split(' ')[0]}`;
    if (el.scrollWidth <= el.clientWidth + 1 || !el.clientWidth || el.closest('svg')) continue;
    if ((ox === 'hidden' || ox === 'clip') && getComputedStyle(el).textOverflow !== 'ellipsis' && !el.classList.contains('ws-sr')) cut.push(`${id} shows ${el.clientWidth} of ${el.scrollWidth}px`);   // an ellipsis, and text for assistive tech only, are cut on purpose
    else if (ox === 'visible') spill.push(`${id} is ${el.clientWidth}px wide, its content ${el.scrollWidth}px`);
    else if (ox === 'auto' || ox === 'scroll') spill.push(`${id} scrolls sideways inside itself, showing ${el.clientWidth} of ${el.scrollWidth}px`);   // a popover is overflow:auto by default
  }
  const probe = document.createElement('div');
  probe.style.height = 'var(--control-h)'; document.body.append(probe);
  const controlH = probe.getBoundingClientRect().height;
  const colour = (v) => { probe.style.color = v; return getComputedStyle(probe).color; };
  const s = getComputedStyle(document.documentElement);
  const t = { action: colour(s.getPropertyValue('--action')), onAction: colour(s.getPropertyValue('--on-action')),
              raised: colour(s.getPropertyValue('--surface-raised')), tint: colour(s.getPropertyValue('--action-tint')) };
  const choice = [...document.querySelectorAll('.ws-choice__input')].map((inp) => {
    const face = inp.nextElementSibling, f = getComputedStyle(face), m = getComputedStyle(face, '::before');
    const ok = inp.checked
      ? f.backgroundColor === t.tint && f.outlineColor === t.action && f.outlineStyle === 'solid' && m.backgroundColor === t.action && m.borderTopColor === t.action
      : f.backgroundColor === t.raised && m.backgroundColor === 'rgba(0, 0, 0, 0)' && parseFloat(m.width) > 0;
    return { label: face.textContent, checked: inp.checked, ok };
  });
  for (const e of document.body.querySelectorAll('*'))
    if (getComputedStyle(e).backgroundColor === t.action && !e.classList.contains('ws-btn--primary'))
      choice.push({ label: `${e.localName}.${String(e.className).split(' ')[0]} '${e.textContent.trim().slice(0, 20)}' is filled with action; selection is tint and ring, the fill is the primary button's (D26)`, checked: true, ok: false, raw: true });
  const boxes = [...document.querySelectorAll('.ws-sides__btn')].map((b) => parseFloat(getComputedStyle(b, '::before').width) || 0);
  if (boxes.length && (Math.min(...boxes) === 0 || Math.max(...boxes) !== Math.min(...boxes)))
    choice.push({ label: `the Sides boxes are ${[...new Set(boxes)].join(', ')}px wide; pressed or not they are one size, so pressing never moves the layout`, checked: true, ok: false, raw: true });
  for (const b of document.querySelectorAll('.ws-sides__btn')) {   // the radio's size, at the control's own font
    const r = document.createElement('i'); r.style.cssText = 'position:absolute;width:var(--radio-size)'; b.append(r);
    const want = r.getBoundingClientRect().width, w = parseFloat(getComputedStyle(b, '::before').width) || 0; r.remove();
    if (Math.abs(w - want) > 0.01) choice.push({ label: `the Sides box in '${b.textContent.trim()}' is ${w.toFixed(2)}px, the radio ${want.toFixed(2)}px; they are one size`, checked: true, ok: false, raw: true });
  }
  // A Choice face may wrap a long label on a narrow screen, so it is control-h or more; on one line it is exact.
  const lines = (e) => { const g = document.createRange(); g.selectNodeContents(e); return new Set([...g.getClientRects()].filter((q) => q.width).map((q) => Math.round(q.top))).size; };
  const size = (sel, exact) => [...document.querySelectorAll(sel)].filter((e) => e.getClientRects().length)
    .map((e) => ({ cls: String(e.className).split(' ')[0], label: (e.textContent.trim() || e.value || '').slice(0, 40),
                   exact: exact || (e.matches('.ws-choice__face') && lines(e) === 1), h: e.getBoundingClientRect().height }));
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
  // Without a pointer (D30): keys on the focused drawing, a press for each move, a name and a description.
  for (const view of document.querySelectorAll('.ws-stage__view')) {
    const art = view.querySelector(':scope > canvas, :scope > svg');
    if (!art) stage.push('a stage view has no drawing (its canvas, or an SVG standing in for one)');
    else {
      const said = (art.getAttribute('aria-describedby') || '').split(/\\s+/).map((id) => document.getElementById(id)).filter((d) => d && d.textContent.trim());
      if (!art.hasAttribute('tabindex') || art.tabIndex < 0) stage.push('the drawing cannot take focus, so no arrow key can turn it; give it tabindex="0"');
      if (art.getAttribute('role') !== 'img' || !(art.getAttribute('aria-label') || '').trim()) stage.push('the drawing is not an image with a name; give it role="img" and an aria-label');
      if (!said.some((d) => d.classList.contains('ws-plan__line'))) stage.push('the drawing is not described by the plan line; point its aria-describedby at it');
      art.focus({ preventScroll: true });
      const f = getComputedStyle(art);
      if (document.activeElement !== art) stage.push('the drawing did not take focus');
      else if (f.outlineStyle !== 'solid' || f.outlineColor !== t.action || parseFloat(f.outlineOffset) + parseFloat(f.outlineWidth) > 0.01)
        stage.push(`the focused drawing has no action ring inside the view (outline ${f.outlineStyle} ${f.outlineWidth}, offset ${f.outlineOffset}); the view clips a ring drawn outside`);
      art.blur();
    }
    const names = [...view.querySelectorAll('button')].map((b) => b.textContent.replace(/[\\ue000-\\uf8ff]/g, '').trim());   // less the icon
    for (const want of ['Reset view', 'Zoom in', 'Zoom out']) if (!names.includes(want)) stage.push(`no '${want}' button in the view: each move is one press, with no drag or pinch`);
    if (!view.querySelector('.ws-stage__views[role=radiogroup] input[type=radio]')) stage.push('no Front, Back and Top choice (.ws-stage__views) in the view');
    // The rows of controls lie over the drawing: between the controls, a drag must still reach it.
    for (const box of art ? view.querySelectorAll('.ws-stage__tools, .ws-stage__views') : []) {
      const r = box.getBoundingClientRect(), kids = [...box.querySelectorAll('.ws-btn, .ws-choice__face')].map((e) => e.getBoundingClientRect());
      sample: for (let y = r.top + 1; y < r.bottom; y += 4) for (let x = r.left + 1; x < r.right; x += 4) {
        if (kids.some((k) => x > k.left - 2 && x < k.right + 2 && y > k.top - 2 && y < k.bottom + 2)) continue;
        const e = document.elementFromPoint(x, y);
        if (e && e !== art && !art.contains(e)) { stage.push(`a drag at ${Math.round(x)},${Math.round(y)}, between the controls of ${box.className.split(' ').pop()}, lands on ${e.localName}.${String(e.className).split(' ')[0]}, not on the drawing`); break sample; }
      }
    }
    // On a phone or a short screen the view keeps Reset view and View…, a menu holding the rest; on a
    // wide screen all of them are on show and View… is not (D36).
    const wide = matchMedia(wideQuery).matches && !matchMedia(shortQuery).matches;
    const shown = (e) => !!e && e.getClientRects().length > 0;
    const zoom = [...view.querySelectorAll('button')].filter((b) => /Zoom (in|out)/.test(b.textContent));
    const picks = view.querySelector('.ws-stage__views');
    const more = [...view.querySelectorAll('button[popovertarget]')].find((b) => b.textContent.trim() === 'View…');
    if (wide) {
      if (zoom.some((b) => !shown(b)) || !shown(picks)) stage.push('on a wide screen Zoom in, Zoom out and the view choice are not all on show');
      if (shown(more)) stage.push('on a wide screen View… is on show; it is for a phone or a short screen');
    } else if (zoom.some(shown) || shown(picks)) stage.push('on a phone or a short screen Zoom in, Zoom out or the view choice crowd the view; they go in the View… menu');
    else if (!shown(more)) stage.push('on a phone or a short screen no View… button opens Zoom in, Zoom out and the view choice');
    else {
      const menu = document.getElementById(more.getAttribute('popovertarget'));
      if (!menu || zoom.length < 2 || !zoom.every((b) => menu.contains(b)) || !menu.contains(picks)) stage.push('the View… menu does not hold Zoom in, Zoom out and the view choice');
      else {
        more.click();
        const m = menu.getBoundingClientRect(), r = more.getBoundingClientRect(), de = document.documentElement, at = (b) => `${Math.round(b.left)},${Math.round(b.top)} to ${Math.round(b.right)},${Math.round(b.bottom)}`;
        if (!menu.matches(':popover-open')) stage.push('View… does not open its menu');
        else if (m.top < r.bottom - 0.5 || Math.abs(m.right - r.right) > 0.5) stage.push(`the View… menu, at ${at(m)}, is not under its button at ${at(r)}, right edges aligned`);
        else if (m.left < -0.5 || m.right > de.clientWidth + 0.5 || m.bottom > de.clientHeight + 0.5) stage.push(`the View… menu, at ${at(m)}, runs off the screen`);
        else if (zoom.some((b) => !shown(b)) || !shown(picks)) stage.push('the open View… menu does not show Zoom in, Zoom out and the view choice');
        menu.hidePopover();
      }
    }
    const hit = [...view.querySelectorAll('.ws-btn, .ws-choice__face')].filter((e) => e.getClientRects().length).map((e) => [e.textContent.trim(), e.getBoundingClientRect()]);
    for (let i = 0; i < hit.length; i++) for (let j = i + 1; j < hit.length; j++) {
      const [a, r] = hit[i], [b, q] = hit[j];
      if (r.left < q.right - 0.5 && q.left < r.right - 0.5 && r.top < q.bottom - 0.5 && q.top < r.bottom - 0.5) stage.push(`'${a}' and '${b}' lie over each other in the view`);
    }
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
    const said = (e.getAttribute('aria-describedby') || '').split(/\\s+/).map((id) => document.getElementById(id)).filter((d) => d && d.textContent.trim());
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
    return { label: text, unit: /\\([^)]+\\)$/.test(text), ok: i.type === 'number' || ['decimal', 'numeric'].includes(i.inputMode) };
  }).filter((u) => u.unit);
  const data = [...document.querySelectorAll('.ws-plan__line, .ws-input, .ws-status, .ws-num, code')].filter((e) => e.getClientRects().length)
    .filter((e) => !/"calt" 0/.test(getComputedStyle(e).fontFeatureSettings)).map((e) => `${e.localName}.${String(e.className).split(' ')[0]} draws ligatures; data must show as typed (D29)`);
  const rail = [...document.querySelectorAll('.ws-rail__btn')].filter((b) => !b.textContent.replace(/[\\d\\s]/g, '').trim())
    .map((b) => `step button '${b.textContent.trim()}' has a number and no name (D31)`);
  const seen = { stages: document.querySelectorAll('.ws-stage__view').length, bars: hints.length,
                 live: document.querySelectorAll('.ws-error, .ws-plan__line, .ws-notice:empty, .ws-stage__message:empty').length,
                 invalid: document.querySelectorAll('[aria-invalid="true"]').length,
                 data: document.querySelectorAll('.ws-plan__line, .ws-input, .ws-status, .ws-num, code').length,
                 steps: document.querySelectorAll('.ws-rail__btn').length,
                 variants: document.querySelectorAll('.ws-notice--error, .ws-notice--warning').length,
                 lines: document.querySelectorAll('.ws-plan__line').length, units: units.length };
  return { scroll: document.documentElement.scrollWidth - vw, cut, spill, choice, heights, controlH, stage, scheme, hints, notices, plan,
           primaries, units, liveness, data, rail, seen, coarse: matchMedia('(pointer: coarse)').matches };
}"""

# In the page: the header's More… menu, opened as View… is (D28); the phone stage pinned when the page
# scrolls (D25); the attributes that make each control what it says (a toggle's aria-pressed, a
# Choice's named radiogroup, a popover each opener points at); and each dialog opened as a modal, as a
# tool opens it (the preview shows it open in place): space-4 from the screen's edges, over the scrim.
MENUS_JS = """([wideQuery, shortQuery]) => {
  const out = { header: [], pinned: [], aria: [], dialog: [], rhythm: [] }, seen = { headers: 0, pins: 0, aria: 0, dialogs: 0, rhythm: 0 };
  const shown = (e) => !!e && e.getClientRects().length > 0, de = document.documentElement;
  const at = (b) => `${Math.round(b.left)},${Math.round(b.top)} to ${Math.round(b.right)},${Math.round(b.bottom)}`;
  for (const h of document.querySelectorAll('.ws-header')) {
    seen.headers++;
    const more = h.querySelector('.ws-header__more'), menu = h.querySelector('.ws-header__actions'), hb = h.getBoundingClientRect();
    if (!menu && !more) continue;   // a header whose few buttons fit a phone's row keeps them there (CHANGELOG, v0.4.0)
    const items = menu ? [...menu.querySelectorAll('button')] : [];
    if (!items.length) out.header.push('More… opens no .ws-header__actions holding the actions');
    else if (matchMedia(wideQuery).matches) {
      if (shown(more)) out.header.push('on a wide screen More… is on show; it is for a phone');
      const off = items.filter((b) => { const r = b.getBoundingClientRect(); return !shown(b) || r.left < hb.left - 0.5 || r.right > hb.right + 0.5 || r.top < hb.top - 0.5 || r.bottom > hb.bottom + 0.5; });
      if (off.length) out.header.push(`on a wide screen ${off.map((b) => `'${b.textContent.trim()}'`).join(', ')} are not on show in the header row`);
    } else if (!shown(more)) out.header.push("below the breakpoint no More… button opens the header's actions");
    else if (items.some(shown)) out.header.push("below the breakpoint the header's actions crowd the row; they go in More…");
    else {
      more.click();
      const m = menu.getBoundingClientRect();
      if (!menu.matches(':popover-open')) out.header.push(`More… does not open the header's actions (it points at #${more.getAttribute('popovertarget')})`);
      else if (m.top < hb.bottom - 0.5) out.header.push(`the More… menu, at ${at(m)}, is not under the header at ${at(hb)}`);
      else if (m.left < -0.5 || m.right > de.clientWidth + 0.5 || m.bottom > de.clientHeight + 0.5) out.header.push(`the More… menu, at ${at(m)}, runs off the screen`);
      else if (!items.every(shown)) out.header.push('the open More… menu does not show every action');
      menu.hidePopover();
    }
  }
  // Scrolled down on a phone, the 3D view is pinned to the top and the plan bar under it; side by side,
  // or on a short screen, nothing is pinned. A page too short to scroll has nothing to show.
  for (const v of document.querySelectorAll('.ws-stage__view')) {
    const stage = v.closest('.ws-stage'), plan = stage && stage.querySelector('.ws-plan');
    if (!stage || getComputedStyle(stage).display !== 'contents' || matchMedia(shortQuery).matches) continue;
    scrollTo(0, de.scrollHeight);
    if (scrollY > 0) {
      seen.pins++;
      const r = v.getBoundingClientRect(), p = plan && plan.getBoundingClientRect();
      if (Math.abs(r.top) > 0.5) out.pinned.push(`scrolled down, the 3D view is at ${Math.round(r.top)}px, not pinned to the top (D25)`);
      if (p && Math.abs(p.top - r.bottom) > 0.5) out.pinned.push(`scrolled down, the plan bar is at ${Math.round(p.top)}px, not pinned under the view at ${Math.round(r.bottom)}px (D25)`);
    }
    scrollTo(0, 0);
  }
  const label = (e) => `'${e.textContent.trim().slice(0, 24)}'`;
  for (const e of document.querySelectorAll('.ws-tile, .ws-piece, .ws-sides__btn')) {
    seen.aria++;
    if (!['true', 'false'].includes(e.getAttribute('aria-pressed'))) out.aria.push(`${e.className.split(' ')[0]} ${label(e)} has no aria-pressed: a toggle says whether it is on`);
  }
  for (const g of document.querySelectorAll('.ws-choice')) {
    seen.aria++;
    if (g.getAttribute('role') !== 'radiogroup' || !(g.getAttribute('aria-label') || g.getAttribute('aria-labelledby'))) out.aria.push(`the Choice ${label(g)} is not a named radiogroup`);
    if ([...g.querySelectorAll('.ws-choice__input')].some((i) => i.type !== 'radio')) out.aria.push(`the Choice ${label(g)} has an option that is not a radio`);
  }
  for (const g of document.querySelectorAll('.ws-sides')) {
    seen.aria++;
    if (g.getAttribute('role') !== 'group' || !g.getAttribute('aria-label')) out.aria.push('the Sides toggles are not a named group');
  }
  for (const r of document.querySelectorAll('.ws-rail')) {
    seen.aria++;
    if (!r.getAttribute('aria-label') || !r.querySelector('[aria-current=step]')) out.aria.push('the step rail has no name, or no step with aria-current="step"');
  }
  for (const b of document.querySelectorAll('[popovertarget]')) {
    seen.aria++;
    const t = document.getElementById(b.getAttribute('popovertarget'));
    if (!t || !t.hasAttribute('popover')) out.aria.push(`${label(b)} opens #${b.getAttribute('popovertarget')}, which is no popover`);
  }
  for (const b of document.querySelectorAll('.ws-header button'))
    if (/theme/i.test(b.textContent) && !['true', 'false'].includes(b.getAttribute('aria-pressed'))) out.aria.push(`the theme toggle ${label(b)} has no aria-pressed`);
  const probe = document.createElement('div'); probe.style.position = 'absolute'; document.body.append(probe);   // a block: an inline box has no width
  const px = (v) => { probe.style.width = v; return probe.getBoundingClientRect().width; }, gap = px('var(--space-4)');
  const above = { item: px('var(--space-3)'), note: px('var(--space-1)') };
  if (!(gap > 0) || !(above.item > 0) || !(above.note > 0)) out.dialog.push('a space token measures 0px; the checks that use it would measure nothing');
  const colour = (v) => { probe.style.color = v; return getComputedStyle(probe).color; }, scrim = colour('var(--scrim)');
  probe.remove();
  // Rhythm, as tokens.json says: the first item under a legend sits space-3 below it (the fieldset's
  // padding, not that plus the item's own margin), and a note space-1 under the group it explains.
  const space = (a, b) => b.getBoundingClientRect().top - a.getBoundingClientRect().bottom;
  for (const f of document.querySelectorAll('fieldset.ws-fieldset')) {
    const lg = f.querySelector(':scope > legend'), first = lg && lg.nextElementSibling;
    if (!first || !first.getClientRects().length) continue;
    seen.rhythm++;
    if (Math.abs(space(lg, first) - above.item) > 0.5) out.rhythm.push(`${first.localName}.${String(first.className).split(' ')[0]} sits ${space(lg, first).toFixed(1)}px under the legend '${lg.textContent.trim()}', not space-3 (${above.item}px)`);
  }
  for (const n of document.querySelectorAll('.ws-note')) {
    const g = n.previousElementSibling;
    if (!g || !n.getClientRects().length || !g.matches('.ws-choice, .ws-gallery, .ws-map, .ws-sides, .ws-label, .ws-actions, .ws-summary')) continue;
    seen.rhythm++;
    if (Math.abs(space(g, n) - above.note) > 0.5) out.rhythm.push(`the note '${n.textContent.trim().slice(0, 24)}' sits ${space(g, n).toFixed(1)}px under its ${g.className.split(' ')[0]}, not space-1 (${above.note}px)`);
  }
  for (const d of document.querySelectorAll('dialog.ws-dialog')) {
    seen.dialogs++;
    const was = d.open; d.close(); d.showModal();
    const r = d.getBoundingClientRect(), vw = de.clientWidth, back = getComputedStyle(d, '::backdrop').backgroundColor;
    if (r.left < gap - 0.5 || r.right > vw - gap + 0.5) out.dialog.push(`the open dialog, at ${at(r)}, runs to the screen's edge; it keeps space-4 (${gap}px) from each side`);
    if (back !== scrim) out.dialog.push(`the backdrop behind the open dialog is ${back}, not the scrim (${scrim})`);
    d.close(); if (was) d.show();
  }
  return { out, seen };
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

# In the page: focus each control in the sidebar, as a keyboard user would, down the page with Tab and
# back up with Shift+Tab, and say which end up off the screen or under something else (the pinned
# stage); then put the page back. Going down, the browser scrolls a field up from the bottom, where
# nothing is pinned; only going back up does it land under the stage, unless scroll-padding keeps it out.
FOCUS_JS = """() => {
  const out = new Set(), all = [...document.querySelectorAll('.ws-side :is(button, input, select, textarea, a[href], summary)')]
    .filter((el) => el.getClientRects().length);
  for (const el of [...all, ...all.slice().reverse()]) {
    el.focus();
    const r = el.getClientRects()[0], x = (r.left + r.right) / 2, y = (r.top + r.bottom) / 2;   // a wrapped link: its first line
    const own = el.closest('label'), name = (own || el).textContent.trim().slice(0, 30) || el.value || el.localName;
    if (y < 0 || y > innerHeight) { out.add(`'${name}' is off the screen when focused`); continue; }
    const hit = document.elementFromPoint(x, y);
    if (hit && !el.contains(hit) && !(own && own.contains(hit))) out.add(`'${name}' is under ${hit.localName}.${String(hit.className).split(' ')[0]} when focused`);
  }
  document.activeElement && document.activeElement.blur(); scrollTo(0, 0);
  return { out: [...out], n: all.length };
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

# In the page: scroll one mark's control into view; where to look (inside the control's border),
# the colours of the mark's box (::before) and of its glyph (::after, or the box's own text), and
# the box's border, which the scan skips.
MARK_JS = """([sel, i]) => {
  const el = document.querySelectorAll(sel)[i], cs = getComputedStyle(el), m = getComputedStyle(el, '::before'), a = getComputedStyle(el, '::after');
  el.scrollIntoView({ block: 'center', inline: 'center' });
  const r = el.getBoundingClientRect(), rgb = (c) => c.match(/[\\d.]+/g).slice(0, 3).map(Number), b = (k) => parseFloat(cs[k]) + 1;
  return { label: el.textContent.trim(), box: rgb(m.backgroundColor), ink: rgb((a.content === 'none' ? m : a).color), edge: parseFloat(m.borderTopWidth),
           clip: { x: r.left + b('borderLeftWidth'), y: r.top + b('borderTopWidth'),
                   width: r.width - b('borderLeftWidth') - b('borderRightWidth'), height: r.height - b('borderTopWidth') - b('borderBottomWidth') } };
}"""

# In the page: the states every control shows (D26; WCAG 1.4.1, 2.4.7, 2.4.13). Focused, an action ring at
# least ringMin wide that no box clips; selected (pressed, chosen or current), tinted, ringed, with an
# action border and a bold label (not a PieceMap cell: its bold already says "own fill"); not selected,
# not tinted; disabled, faded; an invalid field outlined in error, and an error message in error.
STATES_JS = """([ringMin]) => {
  const out = [], seen = { rings: 0, selected: 0, disabled: 0 };
  const probe = document.createElement('i'); document.body.append(probe);
  const colour = (v) => { probe.style.color = v; return getComputedStyle(probe).color; };
  const s = getComputedStyle(document.documentElement), tok = (n) => colour(s.getPropertyValue(n));
  const action = tok('--action'), tint = tok('--action-tint'), error = tok('--error');
  probe.remove();
  const face = (el) => el.matches('.ws-choice__input') ? el.nextElementSibling : el;   // a Choice shows its state on its face
  const name = (el) => `${el.localName}.${String(el.className.baseVal ?? el.className).split(' ')[0]} '${(face(el).textContent.trim() || el.value || el.getAttribute('aria-label') || '').slice(0, 24)}'`;
  const shown = (el) => el.getClientRects().length > 0;
  for (const el of document.querySelectorAll('button, input, select, textarea, summary, a[href], [tabindex]:not([tabindex="-1"])')) {
    if (!shown(el) || el.disabled) continue;
    seen.rings++; el.focus({ preventScroll: true }); face(el).scrollIntoView({ block: 'center', inline: 'center' });   // not merely scrolled out of a sidebar
    const t = face(el), f = getComputedStyle(t), w = parseFloat(f.outlineWidth), d = parseFloat(f.outlineOffset) + w;
    if (document.activeElement !== el) out.push(`${name(el)} does not take focus`);
    else if (f.outlineStyle !== 'solid' || f.outlineColor !== action || w < ringMin - 0.01)
      out.push(`${name(el)}, focused, has no action ring ${ringMin}px or wider (outline ${f.outlineStyle} ${f.outlineColor} ${f.outlineWidth})`);
    else {
      const r = t.getBoundingClientRect(), ring = { l: r.left - d, t: r.top - d, r: r.right + d, b: r.bottom + d };
      for (let a = t.parentElement; a && a !== document.body; a = a.parentElement) {
        const c = getComputedStyle(a);
        if ((c.overflowX === 'visible' && c.overflowY === 'visible') || c.display === 'contents') continue;   // no box, nothing clipped
        const q = a.getBoundingClientRect(), l = q.left + a.clientLeft, tp = q.top + a.clientTop;
        const cut = [c.overflowX !== 'visible' && (ring.l < l - 0.5 || ring.r > l + a.clientWidth + 0.5) && 'a side',
                     c.overflowY !== 'visible' && (ring.t < tp - 0.5 || ring.b > tp + a.clientHeight + 0.5) && 'the top or bottom'].filter(Boolean);
        if (cut.length) { out.push(`the focus ring of ${name(el)} is cut off at ${cut.join(' and ')} by ${a.localName}.${String(a.className).split(' ')[0]} (overflow ${c.overflowX} ${c.overflowY})`); break; }
      }
    }
    el.blur();
  }
  const selected = (el) => el.matches('[aria-pressed=true], [aria-current=step]') || (el.matches('.ws-choice__input') && el.checked);
  for (const el of document.querySelectorAll('[aria-pressed], [aria-current], .ws-rail__btn, .ws-choice__input')) {
    if (!shown(el)) continue;
    const f = getComputedStyle(face(el));
    if (selected(el)) {
      seen.selected++;
      const miss = [f.backgroundColor !== tint && 'tint', (f.outlineStyle !== 'solid' || f.outlineColor !== action) && 'ring', f.borderTopColor !== action && 'action border',
                    !el.matches('.ws-piece') && parseInt(f.fontWeight) < 700 && 'bold label'].filter(Boolean);
      if (miss.length) out.push(`${name(el)} is selected but has no ${miss.join(', no ')}: selection is tint, ring, action border and bold (D26)`);
    } else if (f.backgroundColor === tint) out.push(`${name(el)} is tinted but not selected`);
  }
  for (const el of document.querySelectorAll('button:disabled, input:disabled, select:disabled, textarea:disabled')) {
    if (!shown(el)) continue;
    seen.disabled++;
    let o = 1; for (let a = face(el); a; a = a.parentElement) o *= parseFloat(getComputedStyle(a).opacity);
    if (o > 0.99) out.push(`${name(el)} is disabled but not faded`);
  }
  for (const el of document.querySelectorAll('[aria-invalid=true]')) {
    const f = getComputedStyle(el);
    if (f.borderTopColor !== error || f.outlineStyle !== 'solid' || f.outlineColor !== error) out.push(`the invalid field ${name(el)} is not outlined in error`);
  }
  for (const el of document.querySelectorAll('.ws-error'))
    if (el.textContent.trim() && getComputedStyle(el).color !== error) out.push(`the error '${el.textContent.trim().slice(0, 24)}' is not in error`);
  return { out, seen };
}"""

# In the page: mark each control a pointer can hover, unless selected, for hover_changes. No preview
# shows a disabled Choice (DESIGN: show only what applies), so one unchosen option is disabled for it.
HOVER_MARK_JS = """() => {
  const spare = [...document.querySelectorAll('.ws-choice__input:not(:checked):not(:disabled)')].filter((e) => e.getClientRects().length).pop();
  if (spare) { spare.disabled = true; spare.dataset.spare = ''; }
  const all = [...document.querySelectorAll('.ws-btn, .ws-choice__input, .ws-sides__btn, .ws-tile, .ws-piece, .ws-rail__btn, .ws-summary')]
    .filter((e) => e.getClientRects().length && !e.matches('[aria-pressed=true], [aria-current=step], :checked'));
  all.forEach((e, i) => { e.dataset.hv = i; });
  return all.length;
}"""
LOOK_JS = """([i]) => {
  const el = document.querySelector(`[data-hv="${i}"]`), t = el.matches('.ws-choice__input') ? el.nextElementSibling : el;
  const f = getComputedStyle(t), m = getComputedStyle(t, '::before');
  return { name: `${el.localName}.${String(el.className).split(' ')[0]} '${t.textContent.trim().slice(0, 24)}'`, disabled: el.disabled,
           look: [f.backgroundColor, f.borderTopColor, f.color, f.filter, f.outlineStyle, f.outlineColor, m.borderTopColor].join(' ') };
}"""
UNMARK_JS = """() => {
  for (const e of document.querySelectorAll('[data-spare]')) { e.disabled = false; delete e.dataset.spare; }
  for (const e of document.querySelectorAll('[data-hv]')) delete e.dataset.hv;
}"""

# In the page: the contrast of every run of text against what is behind it, as drawn (WCAG 1.4.3):
# 4.5:1, or 3:1 for large text (24px, or 18.66px bold). The background is the element's own and its
# ancestors', composed, so text drawn over a picture is measured against its box, not the picture.
# Left out: text in a faded control (disabled, so inactive, which 1.4.3 exempts), text for assistive
# tech only, the drawings' own SVG text, and icons, which are decoration beside a label. Given a
# selector, only the text inside that element (a Choice input: its face).
TEXT_JS = """([root]) => {
  const rgba = (c) => { let m = c.match(/^rgba?\\(([\\d.]+), ([\\d.]+), ([\\d.]+)(?:, ([\\d.]+))?\\)$/);
    if (m) return [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]];
    m = c.match(/^color\\(srgb ([\\d.]+) ([\\d.]+) ([\\d.]+)(?: \\/ ([\\d.]+))?\\)$/);
    return m ? [255 * m[1], 255 * m[2], 255 * m[3], m[4] === undefined ? 1 : +m[4]] : null; };
  const over = (f, b) => [0, 1, 2].map((i) => f[i] * f[3] + b[i] * (1 - f[3])).concat(1);
  const lum = (c) => { const [r, g, b] = c.slice(0, 3).map((v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  let top = root ? document.querySelector(root) : document.body;
  if (top && top.matches('.ws-choice__input')) top = top.nextElementSibling;
  const out = new Set(); let n = 0;
  const walk = document.createTreeWalker(top || document.body, NodeFilter.SHOW_TEXT);
  for (let t = walk.nextNode(); t; t = walk.nextNode()) {
    const el = t.parentElement, said = t.data.trim().slice(0, 24);
    if (!t.data.replace(/[\\ue000-\\uf8ff\\s]/g, '') || !el.getClientRects().length || el.closest('svg, .ws-sr')) continue;
    let faded = false, unread = null; const layers = [];
    for (let a = el; a; a = a.parentElement) {
      const s = getComputedStyle(a), bg = rgba(s.backgroundColor);
      if (parseFloat(s.opacity) < 1) faded = true;
      if (!bg) { unread = s.backgroundColor; break; }
      if (bg[3] > 0) { layers.push(bg); if (bg[3] >= 1) break; }
    }
    if (faded) continue;
    const s = getComputedStyle(el), fg0 = rgba(s.color);
    if (unread || !fg0) { out.add(`the colours of '${said}' cannot be read (${unread || s.color}); use the tokens' own colours`); continue; }
    const bg = layers.reverse().reduce((b, l) => over(l, b), [255, 255, 255, 1]), fg = over(fg0, bg), r = ratio(fg, bg);
    const size = parseFloat(s.fontSize), need = size >= 24 || (size >= 18.66 && parseInt(s.fontWeight) >= 700) ? 3 : 4.5;
    n++;
    if (r < need - 0.005) out.add(`'${said}' is ${r.toFixed(2)}:1, ${hex(fg)} on ${hex(bg)}; text needs ${need}:1`);
  }
  return { out: [...out], n };
}"""

# In the page, in forced colours: each state still looks like itself. Within each group, a chosen
# Choice and an unchosen one, a pressed toggle and one not pressed, and the current, a done and a later
# step are compared by what is drawn: each box's colour as composed over what is behind it, its border
# and outline where they show against it, its weight, and its mark (a radio, a Sides box and tick).
# A Choice's or a Sides toggle's mark must differ on its own: it is what says "chosen" or "on".
FORCED_JS = """() => {
  const rgba = (c) => { const m = c.match(/[\\d.]+/g).map(Number); return [m[0], m[1], m[2], m.length > 3 ? m[3] : 1]; };
  const over = (f, b) => [0, 1, 2].map((i) => Math.round(f[i] * f[3] + b[i] * (1 - f[3]))).concat(1);
  const behind = (e) => { const l = []; for (let a = e; a; a = a.parentElement) { const c = rgba(getComputedStyle(a).backgroundColor); if (c[3] > 0) { l.push(c); if (c[3] >= 1) break; } }
    return l.reverse().reduce((b, c) => over(c, b), [255, 255, 255, 1]); };
  const face = (el) => el.matches('.ws-choice__input') ? el.nextElementSibling : el;
  const edge = (s, side, bg) => { const st = s[side + 'Style'], w = parseFloat(s[side + 'Width']), c = over(rgba(s[side + 'Color']), bg);
    return st === 'none' || st === 'hidden' || !w || c.join() === bg.join() ? 'none' : `${st} ${c}`; };
  const mark = (t, bg) => { const b = getComputedStyle(t, '::before'), a = getComputedStyle(t, '::after');
    const fill = b.content === 'none' ? null : over(rgba(b.backgroundColor), bg);
    return JSON.stringify([fill && fill.join(), fill && edge(b, 'borderTop', fill), a.content === 'none' ? null : [a.content, a.color]]); };
  const look = (el) => { const t = face(el), s = getComputedStyle(t), bg = behind(t);
    return JSON.stringify([bg.join(), edge(s, 'borderTop', bg), edge(s, 'outline', bg), parseInt(s.fontWeight) >= 700, mark(t, bg)]); };
  const name = (el) => `'${face(el).textContent.trim().slice(0, 20)}'`;
  const out = []; let n = 0;
  const differ = (a, b, what, marks) => {
    n++;
    if (look(a) === look(b)) out.push(`${what} ${name(a)} and ${name(b)} look the same`);
    else if (marks && mark(face(a), behind(face(a))) === mark(face(b), behind(face(b)))) out.push(`${what} ${name(a)} and ${name(b)} have the same mark`);
  };
  for (const g of document.querySelectorAll('.ws-choice')) {
    const all = [...g.querySelectorAll('.ws-choice__input')].filter((i) => i.getClientRects().length), on = all.find((i) => i.checked);
    for (const i of all) if (on && i !== on) differ(on, i, 'the chosen and the unchosen options', true);
  }
  for (const cls of ['.ws-sides__btn', '.ws-tile', '.ws-piece']) {
    const all = [...document.querySelectorAll(cls)], on = all.find((e) => e.getAttribute('aria-pressed') === 'true'), off = all.find((e) => e.getAttribute('aria-pressed') === 'false');
    if (on && off) differ(on, off, 'the pressed and the unpressed', cls === '.ws-sides__btn');
  }
  for (const r of document.querySelectorAll('.ws-rail')) {
    const b = [...r.querySelectorAll('.ws-rail__btn')], kinds = [b.find((e) => e.getAttribute('aria-current') === 'step'), b.find((e) => e.dataset.done === 'yes'), b.find((e) => !e.dataset.done && !e.hasAttribute('aria-current'))];
    const [cur, done, later] = kinds;
    if (cur && done) differ(cur, done, 'the current step and the done step', false);
    if (done && later) differ(done, later, 'the done step and the step not reached,', false);
    if (cur && later) differ(cur, later, 'the current step and the step not reached,', false);
  }
  return { out, n };
}"""

def hover_changes(page, cdp):
    """Hover each control (CDP forces :hover): an enabled one shows it, a disabled one does not, and
    its text keeps its contrast. Returns what is wrong, how many were hovered, and the text runs read."""
    out, n, runs = [], page.evaluate(HOVER_MARK_JS), 0
    doc = cdp.send("DOM.getDocument", {"depth": 0})["root"]["nodeId"]
    for i in range(n):
        node = cdp.send("DOM.querySelector", {"nodeId": doc, "selector": f'[data-hv="{i}"]'})["nodeId"]
        before = page.evaluate(LOOK_JS, [i])
        cdp.send("CSS.forcePseudoState", {"nodeId": node, "forcedPseudoClasses": ["hover"]})
        after = page.evaluate(LOOK_JS, [i])
        text = page.evaluate(TEXT_JS, [f'[data-hv="{i}"]'])
        cdp.send("CSS.forcePseudoState", {"nodeId": node, "forcedPseudoClasses": []})
        if before["disabled"] and after["look"] != before["look"]:
            out.append(f"{before['name']} is disabled but changes on hover, as if it could be used")
        elif not before["disabled"] and after["look"] == before["look"]:
            out.append(f"{before['name']} does not change on hover")
        runs += text["n"]
        out += [f"text: hovered, {m}" for m in text["out"]]
    page.evaluate(UNMARK_JS)
    return out, n, runs

def font_fallbacks(cdp):
    """Every element and pseudo-element drawn (in part) in a family that is not the bundled one, and
    how many were drawn in any font. No error is caught: Chromium answers for every node, drawn or
    not, so an error is a broken query, which must not pass as "no fallback"."""
    found, drawn, stack = [], 0, [cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})["root"]]
    while stack:
        n = stack.pop()
        if n["nodeType"] == 1:
            fonts = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": n["nodeId"]})["fonts"]
            drawn += bool(fonts)
            found += [f"<{n['localName'] or n.get('pseudoType')}> in {f['familyName']}" for f in fonts if f["familyName"] not in families]
            stack += n.get("pseudoElements", [])
        stack += n.get("children", [])
    return sorted(set(found)), drawn

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

def mark_offset(page, i):
    """Scroll mark i into view; its label, and the offset of its glyph's ink centre from its box's
    centre (px, + is right and low), or None when no box or no glyph is drawn."""
    s = page.evaluate(MARK_JS, [MARKS, i])
    im = Image.open(io.BytesIO(page.screenshot(clip=s["clip"]))).convert("RGB"); px = im.load()
    d = lambda p, c: sum(abs(a - b) for a, b in zip(p, c))
    # The box is the largest patch of its colour: the control's own rounded border, the same colour,
    # reaches into the corners of the clip.
    left, box = {(x, y) for y in range(im.height) for x in range(im.width) if d(px[x, y], s["box"]) < 30}, []
    while left:
        todo, patch = [left.pop()], []
        while todo:
            x, y = todo.pop(); patch.append((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in left: left.remove(q); todo.append(q)
        box = max(box, patch, key=len)
    if not box:
        return s["label"], None
    xs, ys, e = [x for x, _ in box], [y for _, y in box], round(s["edge"] * DPR)   # inside the border, the box is filled
    ink = [(x, y) for y in range(min(ys) + e, max(ys) + 1 - e) for x in range(min(xs) + e, max(xs) + 1 - e)
           if d(px[x, y], s["ink"]) < d(px[x, y], s["box"])]
    if not ink:
        return s["label"], None
    mid = lambda v: (min(v) + max(v) + 1) / 2 / DPR
    return s["label"], (mid([x for x, _ in ink]) - mid(xs), mid([y for _, y in ink]) - mid(ys))

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
    sys.stdout.reconfigure(encoding="utf-8")   # a message may quote a label with an icon or "…" in it
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(root / "build" / "previews"))
    names = lambda s: set(s.split(","))
    ap.add_argument("--only", type=names, help="render only these previews (folder names, comma-separated); for the controls in tests/")
    ap.add_argument("--device", type=names, help="render only on these devices: " + ", ".join(d for d, _ in DEVICES + LAYOUT_DEVICES) + ", forced (forced colours)")
    ap.add_argument("--theme", type=names, help="render only in these themes: " + ", ".join(themes))
    args = ap.parse_args()
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
    every = sorted(p for p in (root / "components").glob("*/preview.html"))
    if not every:
        print("FAIL no components/*/preview.html found"); return 1
    previews = [p for p in every if not args.only or p.parent.name in args.only]
    filtered = bool(args.only or args.device or args.theme)
    bad, pages = 0, 0
    counts = dict(coverage=0, forced=0, fonts=0, text=0, rings=0, hovers=0, selected=0, disabled=0, headers=0, pins=0, aria=0, dialogs=0, rhythm=0, controls=0, choices=0, sized=0, primary=0, units=0, stages=0, bars=0, variants=0, lines=0, live=0, invalid=0, data=0, steps=0, focus=0, markup=0, marks=0)
    def fail(where, msg):
        nonlocal bad; bad += 1; print(f"FAIL {where}: {msg}")
    for d in sorted(p for p in (root / "components").iterdir() if p.is_dir()):
        for need in ("preview.html", "README.md"):
            if not (d / need).is_file(): fail(d.name, f"markup: no {need}")
    # Read, not rendered, so it holds on any run: every class this script looks for is one a preview
    # uses. A misspelt selector matches nothing, and a check that looks at nothing passes everything.
    used = {c for p in every for a in re.findall(r'class="([^"]*)"', p.read_text(encoding="utf-8")) for c in a.split()}
    script = pathlib.Path(__file__).read_text(encoding="utf-8")
    for cls in sorted(set(re.findall(r"\.(ws-[\w-]*[\w])\b", script)) - used):
        fail("run", f"the check looks for .{cls}, which no preview uses; a misspelt selector checks nothing")
    # Coverage, read from the files: every class the stylesheet styles is shown by a preview and named
    # in a doc, and every class a doc names is one the system has. So a deleted component, a dropped
    # variant or a README left naming a removed class fails, which no total would show.
    styled = set(re.findall(r"\.(ws-[\w-]*[\w])\b", re.sub(r"/\*.*?\*/", "", (root / "components/bundle.css").read_text(encoding="utf-8"), flags=re.S)))
    generated = set(re.findall(r"\.(ws-type-[\w-]+)", (root / "tokens.css").read_text(encoding="utf-8")))
    docs = [root / "README.md", root / "DESIGN.md", *sorted((root / "components").glob("*/README.md"))]
    named = {}
    for d in docs:
        text = d.read_text(encoding="utf-8")   # a class: after a dot, alone in backticks, or in class="…"; not an id
        for cls in set(re.findall(r"\.(ws-[a-z0-9_-]*[a-z0-9])", text)) | set(re.findall(r"`(ws-[a-z0-9_-]*[a-z0-9])`", text)) \
                | {c for a in re.findall(r'class="([^"]*)"', text) for c in a.split() if c.startswith("ws-")}:
            named.setdefault(cls, d.relative_to(root).as_posix())
    for cls in sorted(styled - used - {"ws-page"}):   # the check's own page puts ws-page on <body>
        fail("run", f"coverage: bundle.css styles .{cls}, which no preview shows; show it, or remove it")
    for cls in sorted(styled - set(named)):
        fail("run", f"coverage: bundle.css styles .{cls}, which no doc names; say where it goes")
    for cls, doc in sorted(named.items()):
        if cls not in styled | generated:
            fail("run", f"coverage: {doc} names .{cls}, which the system does not have")
    counts["coverage"] = len(styled)
    for p in every:
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
                if (args.device and device not in args.device) or (args.theme and theme not in args.theme):
                    continue
                ctx = browser.new_context(device_scale_factor=DPR, **opts)
                touch = opts.get("has_touch", False)
                narrow = opts["viewport"]["width"] < BP_PX
                for p in previews:
                    if (device, opts) in LAYOUT_DEVICES and not re.search(r"ws-(workbench|header)\b", p.read_text(encoding="utf-8")):
                        continue
                    name, where = p.parent.name, f"{p.parent.name} {theme} {device}"
                    html = pathlib.Path(tmp) / f"{name}-{theme}-{device}.html"
                    html.write_text(PAGE.format(theme=theme, fragment=p.read_text(encoding="utf-8"),
                        tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri()), encoding="utf-8")
                    page = ctx.new_page(); cdp = ctx.new_cdp_session(page)
                    for d in ("DOM", "CSS", "Accessibility"): cdp.send(f"{d}.enable")
                    page.goto(html.as_uri())
                    for f in page.evaluate(SETTLE_JS): fail(where, f"fonts: {f} did not load")
                    pages += 1
                    fallbacks, drawn = font_fallbacks(cdp); counts["fonts"] += drawn
                    for f in fallbacks: fail(where, f"fonts: {f}")
                    for n in icon_names(cdp): fail(where, f"names: icon glyph in {n}")
                    lay = page.evaluate(LAYOUT_JS, [SIZED, AT_LEAST, WIDE, SHORT])
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
                    counts["primary"] += lay["primaries"]
                    if lay["primaries"] > 1: fail(where, f"primary: {lay['primaries']} primary buttons in view; at most one (Button)")
                    for u in lay["units"]:
                        if not u["ok"]: fail(where, f"units: '{u['label']}' gets a text keyboard; give it inputmode=\"decimal\" (Field)")
                    for n in lay["liveness"]: fail(where, f"live: {n}")
                    for n in lay["data"]: fail(where, f"data: {n}")
                    for n in lay["rail"]: fail(where, f"rail: {n}")
                    for k, v in lay["seen"].items(): counts[k] += v
                    if touch and lay["controlH"] < TAP_MIN - 0.01: fail(where, f"height: control-h is {lay['controlH']:.2f}px on a touch screen; at least {TAP_MIN}px (WCAG 2.5.5)")
                    ui = page.evaluate(MENUS_JS, [WIDE, SHORT])
                    for k, v in ui["seen"].items(): counts[k] += v
                    for kind, msgs in ui["out"].items():
                        for n in msgs: fail(where, f"{kind}: {n}")
                    foc = page.evaluate(FOCUS_JS); counts["focus"] += foc["n"]
                    for n in foc["out"]: fail(where, f"view: {n}")
                    st = page.evaluate(STATES_JS, [RING_MIN])
                    for k, v in st["seen"].items(): counts[k] += v
                    for n in st["out"]: fail(where, f"states: {n}")
                    hov, hovered, runs = hover_changes(page, cdp); counts["hovers"] += hovered; counts["text"] += runs
                    for n in hov: fail(where, n if n.startswith("text: ") else f"states: {n}")
                    txt = page.evaluate(TEXT_JS, [None]); counts["text"] += txt["n"]
                    for n in txt["out"]: fail(where, f"text: {n}")
                    for c in lay["choice"]:
                        counts["choices"] += not c.get("raw")
                        if not c["ok"]: fail(where, f"choice: {c['label']}" if c.get("raw") else f"choice: '{c['label']}' ({'chosen' if c['checked'] else 'not chosen'}) is drawn wrong")
                    for h in lay["heights"]:
                        counts["sized"] += 1
                        if (abs(h["h"] - lay["controlH"]) if h["exact"] else lay["controlH"] - h["h"]) > 0.5:
                            fail(where, f"height: {h['cls']} '{h['label']}' is {h['h']:.2f}px, control-h is {lay['controlH']:.2f}px")
                    for i in range(page.evaluate("(sel) => document.querySelectorAll(sel).length", MARKS)):
                        counts["marks"] += 1
                        label, off = mark_offset(page, i)
                        if off is None: fail(where, f"marks: no box with a glyph in it found in '{label}'")
                        elif max(map(abs, off)) > CENTRE_TOL: fail(where, f"marks: the tick in '{label}' is {off[0]:+.2f}px across and {off[1]:+.2f}px down from its box's centre")
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
        # Forced colours (Windows High Contrast and the like): the browser keeps only system colours, so
        # every state must still look like itself in them. Once per preview, in the light theme on a
        # desktop, as the user's palette replaces both themes alike.
        if not args.device or "forced" in args.device:
            ctx = browser.new_context(device_scale_factor=DPR, forced_colors="active", **dict(DEVICES)["desktop"])
            for p in previews:
                name, where = p.parent.name, f"{p.parent.name} forced-colors desktop"
                html = pathlib.Path(tmp) / f"{name}-forced.html"
                html.write_text(PAGE.format(theme=themes[0], fragment=p.read_text(encoding="utf-8"),
                    tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri()), encoding="utf-8")
                page = ctx.new_page(); page.goto(html.as_uri()); page.evaluate(SETTLE_JS)
                if not page.evaluate("matchMedia('(forced-colors: active)').matches"): fail(where, "setup: forced colours are not on")
                fc = page.evaluate(FORCED_JS); counts["forced"] += fc["n"]
                for n in fc["out"]: fail(where, f"forced: {n}")
                page.close()
            ctx.close()
        browser.close()
    shape = "a part of the run" if filtered else f"{len(previews)} previews x {len(DEVICES)} devices x {len(themes)} themes, and the workbench and header on {len(LAYOUT_DEVICES)} more"
    print(f"\n{pages} pages ({shape}); "
          f"{counts['controls']} labels measured for centring, {counts['choices']} choice options, {counts['sized']} control heights checked")
    print("looked at: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    if filtered:
        print("a part of the run (--only, --device, --theme): a count of zero is not a failure")
    else:
        for k, v in counts.items():
            if not v: fail("run", f"{k}: nothing to check; a selector or a preview has gone missing")
    print(f"screenshots in {out}")
    print("%d failing" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
