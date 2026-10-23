#!/usr/bin/env python3
"""Sweep short screens: side by side exactly where the rule says, the bars one row each, the view at 40 %.

Run from the project folder:  uv run python scripts/sweep-side-by-side.py [--browser webkit]
    [--widths 600-1280] [--heights 240-480] [--pointers mouse,touch] [--json FILE]
Needs: playwright (pyproject.toml), and the engine for Playwright, as check-previews.py does.

The rule (D75): the sidebar sits beside the stage on a screen at least breakpoint-wide wide, or at
least breakpoint-side-min wide and landscape-ratio wider than tall (D41), and either way at least H
tall, the least height at which the header, the plan bar and the status bar, one row each, leave
the 3D view 40 % of the screen (D25). scripts/build-tokens.py derives H from the bars' tokens and
holds bundle.css's media query to it; this sweep holds the engine to it. H comes from the build
(build-tokens.py --query side-h, through check-previews.py) and the breakpoints from tokens.json:
none is typed here.

check-previews.py draws a few chosen screens; this draws every screen in the ranges, a pixel
apart: by default every width from 600px (under breakpoint-side-min, where every screen stacks) to
1280px and every height from 240px (under H) to breakpoint-short, with a mouse and on a touch
phone: the Workbench preview with tokens.css and components/bundle.css as they are, in Chromium
(the default), WebKit or Firefox (--browser, Playwright's build of each), in an iframe of each
size, so the media queries are the stylesheet's, read by the engine. The page is
check-previews.py's own (its template, font loading, engines and pixel ratio). It fails (exit 1):

1. rule:  a screen goes side by side where the rule stacks it, or stacks where the rule puts it
          side by side.
2. bars:  side by side, the plan bar or the status bar is not one row (its parts are not on one
          line), a bar is not one height on every screen, or the 3D view is not the screen's
          height less the bars, within 0.5px.
3. side:  each width's shortest side-by-side screen, drawn in a window of its own size, is not
          side by side, or its view is not the iframe's within 0.5px; or one pixel shorter, where
          the iframe stacks, the window goes side by side.
4. view:  a side-by-side screen gives the 3D view under 40 % of its height, less the 0.5px of
          rounding check-previews.py allows.
5. setup: the page runs in another engine than asked, the fonts did not load in the iframe, an
          iframe is not the size asked for, or touch is not on or off as the pointer says.
A run in which no screen goes side by side checked nothing, and fails.

It prints, per pointer, the bars' heights side by side and the least height at which they leave
the view 40 %, each run of widths with the least height side by side there, and the worst screen
side by side. tests/test-sweep-side-by-side.sh holds each check to a control.
"""
import argparse, importlib.util, json, math, pathlib, re, sys, tempfile
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_previews", root / "scripts/check-previews.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)   # its constants only, H among them (from the build); main() runs only as a script
SHARE = 0.4   # the view's least share of the screen's height (D25)
TOL = 0.5     # px: the rounding of a box's edge, as check-previews.py allows it
BARS = ("header", "plan bar", "status bar")

# A window's own layout, for the edge screens drawn at their size
MEASURE_JS = """async () => {
  await ck.frames();
  const st = document.querySelector('.ws-workbench .ws-stage'), v = st.querySelector('.ws-stage__view');
  return { side: getComputedStyle(st).display !== 'contents', view: v.getBoundingClientRect().height,
           w: innerWidth, h: innerHeight, coarse: matchMedia('(pointer: coarse)').matches };
}"""
# In the page: one iframe holding the preview, its fonts loaded; then resized to each screen in turn
FRAME_JS = """async (doc) => {
  const f = document.createElement('iframe');
  f.style.cssText = 'position:absolute;left:0;top:0;border:0';
  f.srcdoc = doc; document.body.append(f);
  await new Promise((ok) => f.addEventListener('load', ok, { once: true }));
  const d = f.contentDocument;
  const bad = (await Promise.all([...d.fonts].map((x) => x.load().then(() => null, () => `${x.family} ${x.weight}`)))).filter(Boolean);
  await d.fonts.ready;
  window.__frame = f;
  return { bad, faces: d.fonts.size };
}"""
# One width, every height: [side] stacked, or [side, header, plan bar, status bar, view, plan one row,
# status one row] side by side; and the sizes the iframe was not
WIDTH_JS = """([w, hs]) => {
  const f = window.__frame, win = f.contentWindow, d = f.contentDocument, q = (s) => d.querySelector(s);
  const st = q('.ws-workbench .ws-stage'), header = q('.ws-header'), plan = q('.ws-plan'), status = q('.ws-status');
  const view = q('.ws-stage__view'), line = q('.ws-plan__line');
  const tall = (e) => Math.round(e.getBoundingClientRect().height * 1000) / 1000;
  const mid = (e) => { const r = e.getBoundingClientRect(); return (r.top + r.bottom) / 2; };
  const row = (bar, ref) => [...bar.children].every((c) => Math.abs(mid(c) - mid(ref)) <= 1) ? 1 : 0;
  const rows = [], wrong = [];
  f.style.width = `${w}px`;
  for (const h of hs) {
    f.style.height = `${h}px`;
    if (win.innerWidth !== w || win.innerHeight !== h) wrong.push(`${w} x ${h} is ${win.innerWidth} x ${win.innerHeight}`);
    if (win.getComputedStyle(st).display === 'contents') { rows.push([0]); continue; }
    rows.push([1, tall(header), tall(plan), tall(status), tall(view), row(plan, line), row(status, status.firstElementChild)]);
  }
  return { rows, wrong };
}"""

def span(s):
    lo, _, hi = s.partition("-")
    return list(range(int(lo), int(hi or lo) + 1))

def runs(keys, value):
    """Consecutive keys with the same value: [(first, last, value)]."""
    out = []
    for k in keys:
        v = value(k)
        if out and out[-1][2] == v and out[-1][1] == k - 1:
            out[-1] = (out[-1][0], k, v)
        else:
            out.append((k, k, v))
    return out

def need(bars):
    """The least whole height at which the view, the height less the bars, keeps SHARE of it."""
    return math.ceil((bars - TOL) / (1 - SHARE) - 1e-9)

def where(screens):
    """Screens [(w, h, ...)] as their extent: W-W x H-H."""
    ws, hs = [s[0] for s in screens], [s[1] for s in screens]
    return f"{min(ws)}-{max(ws)} x {min(hs)}-{max(hs)}"

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--browser", choices=cp.ENGINES, default="chromium", help="the engine, Playwright's build of it (default chromium)")
    ap.add_argument("--widths", default="600-1280", help="first-last, in px, every one (default %(default)s)")
    ap.add_argument("--heights", default=f"240-{cp.rem_px('breakpoint-short')}", help="first-last, in px, every one (default %(default)s)")
    ap.add_argument("--pointers", default="mouse,touch", help="mouse, touch or both (default %(default)s)")
    ap.add_argument("--json", help="write each pointer's bars and each width's least height side by side to this file")
    args = ap.parse_args()
    widths, heights, pointers = span(args.widths), span(args.heights), args.pointers.split(",")
    bad = 0
    def fail(msg):
        nonlocal bad; bad += 1; print(f"FAIL {msg}")
    # The rule, from the tokens and the build (D41, D75)
    wide, least_w, least_h = cp.rem_px("breakpoint-wide"), cp.SIDE_W, cp.SIDE_H_PX
    ra, rb = (int(x) for x in cp.SPACE["landscape-ratio"].split("/"))
    def rule(w, h):
        return h >= least_h and (w >= wide or (w >= least_w and w * rb >= h * ra))
    print(f"rule: side by side from {wide}px wide, or from {least_w}px at {ra}/{rb} or wider, and either way from H, "
          f"{cp.SIDE_H} ({least_h}px) tall, as build-tokens.py derives it")
    fragment = (root / "components/Workbench/preview.html").read_text(encoding="utf-8")
    count = dict(screens=0, side=0, edges=0)
    worst, table = None, {}
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        styled_html = cp.PAGE.format(theme="light", fragment=fragment, tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri())
        (tmp / "styled.html").write_text(styled_html, encoding="utf-8")
        # The iframe's page: a file, so the preview in it loads the stylesheets and fonts from files too
        (tmp / "host.html").write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                                       '</head><body style="margin:0"></body></html>', encoding="utf-8")
        frame_html = styled_html   # what the iframe holds: the stylesheet as it is
        browser = getattr(pw, args.browser).launch()
        version = f"{args.browser} {browser.version}"
        print(f"engine: {version}")
        for pointer in pointers:
            touch = pointer == "touch"
            ctx = browser.new_context(viewport={"width": widths[0], "height": heights[-1]}, device_scale_factor=cp.DPR, has_touch=touch, is_mobile=touch)
            ctx.add_init_script(cp.PRELUDE)   # the helpers check-previews.py's pages have (SETTLE_JS's wait)
            styled, grid = ctx.new_page(), ctx.new_page()
            styled.goto((tmp / "styled.html").as_uri())
            for f in styled.evaluate(cp.SETTLE_JS): fail(f"setup: {f} did not load")
            ua = styled.evaluate("navigator.userAgent")
            if not re.search(cp.ENGINES[args.browser], ua): fail(f"setup: asked for {args.browser}, but the page runs in {ua}")
            r = styled.evaluate(MEASURE_JS)
            if r["coarse"] != touch: fail(f"setup: touch emulation is {'on' if r['coarse'] else 'off'}, expected {'on' if touch else 'off'}")
            grid.set_viewport_size({"width": max(widths) + 20, "height": max(heights) + 20})
            grid.goto((tmp / "host.html").as_uri())
            got = grid.evaluate(FRAME_JS, frame_html)
            if got["bad"] or not got["faces"]: fail(f"setup: the fonts did not load in the iframe ({', '.join(got['bad']) or 'no faces'})")
            # Every screen: side by side or stacked, and side by side its bars and view
            side, stacked, wrong = {}, set(), []
            for w in widths:
                out = grid.evaluate(WIDTH_JS, [w, heights])
                wrong += out["wrong"]
                for h, row in zip(heights, out["rows"]):
                    if row[0]: side[(w, h)] = row[1:]
                    else: stacked.add((w, h))
            for x in wrong[:3]: fail(f"setup: an iframe asked for {x}")
            count["screens"] += len(widths) * len(heights)
            count["side"] += len(side)
            # 1. rule
            extra = sorted(s for s in side if not rule(*s))
            missing = sorted(s for s in stacked if rule(*s))
            if extra: fail(f"rule: {len(extra)} screens ({pointer}) go side by side where the rule stacks them, {where(extra)}, e.g. {extra[0][0]} x {extra[0][1]}")
            if missing: fail(f"rule: {len(missing)} screens ({pointer}) stack where the rule puts them side by side, {where(missing)}, e.g. {missing[0][0]} x {missing[0][1]}")
            # 2. bars: one row each, one height, and the view the rest
            for i, name in ((4, "plan bar"), (5, "status bar")):
                two = sorted(s for s, v in side.items() if not v[i])
                if two: fail(f"bars: side by side, the {name} is not one row on {len(two)} screens ({pointer}), {where(two)}, e.g. {two[0][0]} x {two[0][1]}")
            heights_of = {}
            for i, name in enumerate(BARS):
                if not side: break
                lo, hi = min(side.items(), key=lambda kv: kv[1][i]), max(side.items(), key=lambda kv: kv[1][i])
                heights_of[name] = lo[1][i]
                if hi[1][i] - lo[1][i] > TOL:
                    fail(f"bars: side by side, the {name} is {lo[1][i]:.2f}px tall at {lo[0][0]} x {lo[0][1]} and {hi[1][i]:.2f}px at {hi[0][0]} x {hi[0][1]} ({pointer}), "
                         f"not one height: it changes with the screen")
            off = sorted(s for s, v in side.items() if abs(s[1] - sum(v[:3]) - v[3]) > TOL)
            if off:
                (w, h), v = off[0], side[off[0]]
                fail(f"bars: side by side at {w} x {h} ({pointer}) the view is {v[3]:.2f}px, the height less the bars {h - sum(v[:3]):.2f}px "
                     f"({len(off)} screens like it, {where(off)})")
            # 3. side: each width's shortest side-by-side screen in a window of its own size
            low = {}
            for w in widths:
                hs = [h for h in heights if (w, h) in side]
                if not hs: continue
                h = low[w] = hs[0]
                styled.set_viewport_size({"width": w, "height": h})
                r = styled.evaluate(MEASURE_JS); count["edges"] += 1
                if not r["side"]: fail(f"side: the iframe puts {w} x {h} ({pointer}) side by side, and a window that size stacks")
                elif abs(r["view"] - side[(w, h)][3]) > TOL:
                    fail(f"side: at {w} x {h} ({pointer}) a window's view is {r['view']:.2f}px, the iframe's {side[(w, h)][3]:.2f}px")
                if (w, h - 1) in stacked:
                    styled.set_viewport_size({"width": w, "height": h - 1})
                    if styled.evaluate(MEASURE_JS)["side"]: fail(f"side: the iframe stacks {w} x {h - 1} ({pointer}), and a window that size goes side by side")
            # 4. view: every side-by-side screen keeps SHARE of its height
            under = []
            for (w, h), v in side.items():
                if worst is None or v[3] / h < worst[0]: worst = (v[3] / h, w, h, pointer, v[3])
                if v[3] < SHARE * h - TOL: under.append((w, h, v[3]))
            if under:
                p, w, h, v = min((v / h, w, h, v) for w, h, v in under)
                fail(f"view: {len(under)} screens ({pointer}), {where(under)}, go side by side, the view down to {100 * p:.1f} % ({v:.2f}px at {w} x {h}), under 40 % (D25)")
            total = sum(heights_of.values())
            print(f"\n{pointer}: side by side, " + (", ".join(f"{n} {v:.2f}px" for n, v in heights_of.items())
                  + f"; they leave the view 40 % from {need(total)}px" if heights_of else "nothing"))
            for w0, w1, h in runs(widths, low.get):
                at = f"side by side from {h}px, the view {100 * side[(w0, h)][3] / h:.1f} % there" if h else f"stack up to {heights[-1]}px"
                print(f"  {w0:>4}-{w1:<4}  {at}")
            table[pointer] = dict(bars=heights_of, least={w: low.get(w) for w in widths})
            ctx.close()
        browser.close()
    if worst:
        print(f"\nworst side by side: {worst[1]} x {worst[2]} ({worst[3]}), the view {worst[4]:.2f}px, {100 * worst[0]:.2f} %")
    if not count["side"]: fail("run: no screen in the sweep goes side by side, so it checked nothing")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(dict(engine=version, H=cp.SIDE_H, heights=[heights[0], heights[-1]], pointers=table)), encoding="utf-8")
    print(f"\n{count['screens']} screens ({len(widths)} widths x {len(heights)} heights x {len(pointers)} pointers) in {version}; "
          f"{count['side']} side by side, {count['edges']} edges drawn in a window")
    print("%d failing" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
