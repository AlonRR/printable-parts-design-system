#!/usr/bin/env python3
"""Sweep short screens: wherever the stylesheet puts the sidebar beside the stage, the 3D view keeps 40 %.

Run from the project folder:  uv run python scripts/sweep-side-by-side.py [--browser webkit]
    [--widths 768-1280] [--heights 360-480] [--pointers mouse,touch] [--json FILE]
Needs: playwright (pyproject.toml), and the engine for Playwright, as check-previews.py does.

check-previews.py draws a few chosen screens; this draws every screen in the ranges, a pixel
apart: by default every width from breakpoint-side-min to 1280px and every height from 360px (a
phone held sideways) to breakpoint-short, with a mouse and on a touch phone, the Workbench preview
with tokens.css and components/bundle.css as they are, in Chromium (the default), WebKit or Firefox
(--browser, Playwright's build of each). It fails (exit 1) if a screen the stylesheet puts side by
side gives the 3D view under 40 % of its height (D25), the share D52 and D54 hold every short
screen side by side to. The page is check-previews.py's own (its template, font loading, engines
and pixel ratio). Every screen, so it runs in minutes, not hours:

1. side:  which screens go side by side, from an iframe of each size in the page, holding the
          preview: its media queries are the stylesheet's, read by the engine; none is copied here.
2. bars:  side by side, the header, plan bar and status bar keep their height whatever the
          screen's height, and the view takes the rest. So the bars are measured once per width,
          in a window as tall as the tallest height, from a copy of the stylesheet with its
          side-by-side query made to match every screen; a side-by-side screen's view is its height
          less them, and a width's shortest side-by-side screen is its worst.
3. edge:  each width's shortest side-by-side screen is drawn in a window of its own size, from the
          stylesheet as it is: it must be side by side, as the iframe said, and its view its height
          less the bars, within 0.5px; one pixel shorter, the window must stack if the iframe says so.
4. view:  every side-by-side screen gives the view at least 40 % of its height, less the 0.5px of
          rounding check-previews.py allows.
5. setup: the page runs in the engine asked for, each iframe is the size asked for, and touch is
          on or off as the pointer says.
A run in which no screen goes side by side checked nothing, and fails.

It prints, per pointer, each run of widths with the same bars: the least height at which the view
would keep 40 % side by side, and the least height at which the stylesheet puts it side by side;
then, from each width, the least height at which every short screen that wide or wider keeps 40 %,
the boundary breakpoint-side-short (D52) and breakpoint-side-size-w and -h (D54) were chosen from;
and the worst screen side by side. tests/test-sweep-side-by-side.sh holds each check to a control.
"""
import argparse, importlib.util, json, math, pathlib, re, sys, tempfile
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_previews", root / "scripts/check-previews.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)   # its constants only; main() runs only as a script
SHARE = 0.4   # the view's least share of the screen's height (D25)
TOL = 0.5     # px: the rounding of a box's edge, as check-previews.py allows it
# The side-by-side block: the media query whose first rule gives the workbench its two columns.
SIDE_QUERY = re.compile(r"@media ([^{}]+)\{\s*\.ws-workbench\{grid-template-columns:")

MEASURE_JS = """async () => {
  await ck.frames();
  const st = document.querySelector('.ws-workbench .ws-stage'), v = st.querySelector('.ws-stage__view');
  return { side: getComputedStyle(st).display !== 'contents', view: v.getBoundingClientRect().height,
           w: innerWidth, h: innerHeight, coarse: matchMedia('(pointer: coarse)').matches };
}"""
# In the page: an iframe of each size, holding the page; which sizes put the sidebar beside the stage.
SIDE_JS = """async ([doc, ws, hs]) => {
  const f = document.createElement('iframe');
  f.style.cssText = 'position:absolute;left:0;top:0;border:0';
  f.srcdoc = doc; document.body.append(f);
  await new Promise((ok) => f.addEventListener('load', ok, { once: true }));
  const win = f.contentWindow, st = f.contentDocument.querySelector('.ws-workbench .ws-stage'), side = [], wrong = [];
  for (const w of ws) {
    let row = '';
    for (const h of hs) {
      f.style.width = `${w}px`; f.style.height = `${h}px`; f.offsetWidth;
      if (win.innerWidth !== w || win.innerHeight !== h) wrong.push(`${w} x ${h} is ${win.innerWidth} x ${win.innerHeight}`);
      row += win.getComputedStyle(st).display !== 'contents' ? '1' : '0';
    }
    side.push(row);
  }
  f.remove();
  return { side, wrong };
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

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--browser", choices=cp.ENGINES, default="chromium", help="the engine, Playwright's build of it (default chromium)")
    ap.add_argument("--widths", default=f"{cp.rem_px('breakpoint-side-min')}-1280", help="first-last, in px, every one (default %(default)s)")
    ap.add_argument("--heights", default=f"360-{cp.rem_px('breakpoint-short')}", help="first-last, in px, every one (default %(default)s)")
    ap.add_argument("--pointers", default="mouse,touch", help="mouse, touch or both (default %(default)s)")
    ap.add_argument("--json", help="write each width's bars and least heights to this file")
    args = ap.parse_args()
    widths, heights, pointers = span(args.widths), span(args.heights), args.pointers.split(",")
    bad = 0
    def fail(msg):
        nonlocal bad; bad += 1; print(f"FAIL {msg}")
    bundle = (root / "components/bundle.css").read_text(encoding="utf-8")
    query = SIDE_QUERY.search(bundle)
    if not query:
        print("FAIL setup: bundle.css has no side-by-side query (the @media whose first rule gives .ws-workbench its columns)\n1 failing")
        return 1
    forced = bundle[:query.start(1)] + "all" + bundle[query.end(1):]
    fragment = (root / "components/Workbench/preview.html").read_text(encoding="utf-8")
    count = dict(screens=0, side=0, edges=0)
    worst, table = None, {}
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "forced.css").write_text(forced, encoding="utf-8")
        styled_html = cp.PAGE.format(theme="light", fragment=fragment, tokens=(root / "tokens.css").as_uri(), bundle=(root / "components/bundle.css").as_uri())
        forced_html = cp.PAGE.format(theme="light", fragment=fragment, tokens=(root / "tokens.css").as_uri(), bundle=(tmp / "forced.css").as_uri())
        (tmp / "styled.html").write_text(styled_html, encoding="utf-8")
        (tmp / "forced.html").write_text(forced_html, encoding="utf-8")
        frame_html = styled_html   # what the iframes hold: the stylesheet as it is
        browser = getattr(pw, args.browser).launch()
        version = f"{args.browser} {browser.version}"
        print(f"engine: {version}")
        for pointer in pointers:
            touch = pointer == "touch"
            ctx = browser.new_context(viewport={"width": widths[0], "height": heights[-1]}, device_scale_factor=cp.DPR, has_touch=touch, is_mobile=touch)
            ctx.add_init_script(cp.PRELUDE)   # the helpers check-previews.py's pages have (SETTLE_JS's wait)
            styled, flat = ctx.new_page(), ctx.new_page()
            for page, html in ((styled, "styled.html"), (flat, "forced.html")):
                page.goto((tmp / html).as_uri())
                for f in page.evaluate(cp.SETTLE_JS): fail(f"setup: {f} did not load")
            ua = styled.evaluate("navigator.userAgent")
            if not re.search(cp.ENGINES[args.browser], ua): fail(f"setup: asked for {args.browser}, but the page runs in {ua}")
            got = styled.evaluate(SIDE_JS, [frame_html, widths, heights])
            for w in got["wrong"][:3]: fail(f"setup: an iframe asked for {w}")
            side = {w: [h for h, s in zip(heights, row) if s == "1"] for w, row in zip(widths, got["side"])}
            count["screens"] += len(widths) * len(heights)
            count["side"] += sum(map(len, side.values()))
            bars, least, edge = {}, {}, {}
            for w in widths:
                flat.set_viewport_size({"width": w, "height": heights[-1]})
                r = flat.evaluate(MEASURE_JS)
                if r["coarse"] != touch: fail(f"setup: touch emulation is {'on' if r['coarse'] else 'off'}, expected {'on' if touch else 'off'}")
                if not r["side"]: fail(f"bars: with the side-by-side query made to match every screen, {w} x {heights[-1]} ({pointer}) still stacks")
                bars[w] = heights[-1] - r["view"]
                if not side[w]:
                    continue
                low = least[w] = side[w][0]   # the shortest side by side, the width's worst
                styled.set_viewport_size({"width": w, "height": low})
                r = styled.evaluate(MEASURE_JS); count["edges"] += 1
                if not r["side"]: fail(f"side: the iframe puts {w} x {low} ({pointer}) side by side, and a window that size stacks")
                elif abs(r["view"] - (low - bars[w])) > TOL:
                    fail(f"bars: side by side at {w} x {low} ({pointer}) the view is {r['view']:.2f}px, the height less the bars measured {heights[-1]}px tall {low - bars[w]:.2f}px: the bars change with the screen's height")
                edge[w] = r["view"]
                if low > heights[0] and low - 1 not in side[w]:
                    styled.set_viewport_size({"width": w, "height": low - 1})
                    if styled.evaluate(MEASURE_JS)["side"]: fail(f"side: the iframe stacks {w} x {low - 1} ({pointer}), and a window that size goes side by side")
            # Every side-by-side screen: the view is its height less the bars, and keeps SHARE of it.
            under = {}
            for w in widths:
                for h in side[w]:
                    view = h - bars[w]
                    if worst is None or view / h < worst[0]: worst = (view / h, w, h, pointer, view)
                    if view < SHARE * h - TOL: under.setdefault(round(bars[w], 2), []).append((w, h, view))
            for b, screens in under.items():
                ws, hs = [s[0] for s in screens], [s[1] for s in screens]
                p, w, h, v = min((v / h, w, h, v) for w, h, v in screens)
                fail(f"view: {min(ws)}-{max(ws)} x {min(hs)}-{max(hs)} ({pointer}) go side by side, the view down to {100 * p:.1f} % ({v:.2f}px at {w} x {h}), under 40 % (D25)")
            print(f"\n{pointer}: widths, the bars side by side, the least height that keeps the view at 40 %, the least height side by side here")
            for w0, w1, (b, lo) in runs(widths, lambda w: (round(bars[w], 2), least.get(w))):
                at = f"side by side from {lo}px, the view {100 * edge[w0] / lo:.1f} % there" if lo else f"stacks up to {heights[-1]}px"
                print(f"  {w0:>4}-{w1:<4}  bars {b:7.2f}px  40 % from {need(b)}px  {at}")
            table[pointer] = {w: dict(bars=round(bars[w], 2), keeps40=need(bars[w]), side_from=least.get(w)) for w in widths}
            ctx.close()
        browser.close()
    # From each width: the least height at which every short screen that wide or wider keeps 40 %.
    reach = {}
    for w in reversed(widths):
        reach[w] = max([need(table[p][w]["bars"]) for p in table] + [reach.get(w + 1, 0)])
    print(f"\nfrom each width, the least height at which every screen that wide or wider keeps 40 % ({', '.join(table)}):")
    for w0, w1, h in runs(widths, reach.get):
        print(f"  from {w0:>4}px (to {w1}): {h}px")
    if worst:
        print(f"\nworst side by side: {worst[1]} x {worst[2]} ({worst[3]}), the view {worst[4]:.2f}px, {100 * worst[0]:.1f} %")
    if not count["side"]: fail("run: no screen in the sweep goes side by side, so it checked nothing")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(dict(engine=version, heights=[heights[0], heights[-1]], pointers=table)), encoding="utf-8")
    print(f"\n{count['screens']} screens ({len(widths)} widths x {len(heights)} heights x {len(pointers)} pointers) in {version}; "
          f"{count['side']} side by side, {count['edges']} edges drawn in a window")
    print("%d failing" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
