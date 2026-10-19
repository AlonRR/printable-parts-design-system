#!/usr/bin/env python3
"""Regenerate tokens.css from tokens.json and check the stylesheet agrees with it.

Run from the project folder:  uv run python scripts/build-tokens.py [--tag vX.Y.Z]
Needs: fonttools and brotli (pyproject.toml; uv run installs them).

It does ten things, so nothing is kept in step by hand:
1. Writes tokens.css (themes, spacing, radius, type, @font-face) from tokens.json. Each theme
   sets its color-scheme, so the browser's own controls, scroll bars and spinners follow it. A
   token's touch value is set in @media (pointer: coarse), so control-h becomes tap there.
2. Derives each font's ascent/descent overrides from its cap height, so capitals sit
   on the centre line of any line box (see DESIGN.md, Type), and writes them into the
   generated @font-face rules.
3. Checks that components/bundle.css uses the breakpoints as tokens.json has them (a media query
   cannot read a variable): breakpoint-wide; breakpoint-side-min with landscape-ratio for side by
   side, and the same ratio with breakpoint-short where nothing is pinned (D41);
   breakpoint-side-short with breakpoint-short, from which a short screen goes side by side (D52);
   breakpoint-side-size-w with breakpoint-side-size-h, from which a narrower short screen does
   (D54); and breakpoint-header, where the header's rules change and nowhere else (D49). And that
   it declares no font of its own: the fonts load once, as files, through the @font-face rules in
   tokens.css (D9).
4. Fails if bundle.css uses a hard-coded colour.
5. Fails if a document in fonts/, which the tools copy with the stylesheets, links to anything the
   copy does not carry: a relative link out of fonts/, or this repository (D24).
6. Fails if bundle.css types a value instead of reading a token: a colour in any notation (rgb(),
   color-mix(), a named or a system colour), a gradient, a length other than the few in LITERAL_OK,
   a font family, size, weight, line height or letter spacing, an opacity, a custom property
   tokens.css does not define, or any it sets (a touch screen's values are tokens' touch values),
   or a token in tokens.json that reads one tokens.css does not define; an
   at-rule other than @media and @supports, a media query other than the breakpoints,
   (pointer:coarse) and (forced-colors:active), or a system colour outside that last one; and if
   a type style asks for a weight no @font-face ships.
7. Fails if an icon in the bundled fonts draws past its advance, so the gap to its label would not
   be icon-gap (scripts/fit-icon-advances.py sets them).
8. One version (D32): tokens.json's version is written into the head of tokens.css, and the build
   fails if pyproject.toml says another, if CHANGELOG.md has no entry for it, if a class in
   bundle.css lacks the ws- prefix (the generated type classes are ws-type-*), or, given --tag
   (CI does, on a tag), if the tag names another version or its changelog entry is still marked
   unreleased.
9. Fails if a rule inside a media query is undone by a later rule outside any: the same selector
   setting the same property wins by coming later, so the media query's value never applies.
10. Fails if an open popover is laid out as a grid without align-content, which WebKit stretches
   to the screen's height (WebKit bug 270334).
tests/test-build-tokens.sh holds every one of these to a control that must fail.
"""
import argparse, json, re, sys, pathlib, tomllib
from fontTools.ttLib import TTFont

root = pathlib.Path(__file__).resolve().parent.parent
tok = json.loads((root / "tokens.json").read_text(encoding="utf-8"))

def overrides(path):
    f = TTFont(root / path)
    upm = f["head"].unitsPerEm
    cap = f["OS/2"].sCapHeight / upm
    hh = f["hhea"]
    total = (hh.ascent - hh.descent) / upm        # keep the font's own line height
    return (total + cap) / 2 * 100, (total - cap) / 2 * 100   # ascent - descent = cap height

args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
args.add_argument("--tag", help="the git tag being built, e.g. v0.4.0; it must name the version in tokens.json")
args.add_argument("--query", choices=("side-by-side", "side-size"),
                  help="print the media query bundle.css must have for side by side, or its size-only part (D54), "
                       "and exit, writing nothing: the tests read the queries from here, not typed again")
args = args.parse_args()
def space(name): return next(x["value"] for x in tok["spacing"]["tokens"] if x["name"] == name)
bp, short, ratio = space("breakpoint-wide"), space("breakpoint-short"), space("landscape-ratio")
hdr, side, side_short = space("breakpoint-header"), space("breakpoint-side-min"), space("breakpoint-side-short")
size_w, size_h = space("breakpoint-side-size-w"), space("breakpoint-side-size-h")
# Side by side: a short screen from breakpoint-side-short (D52), or from breakpoint-side-size-w wide and
# breakpoint-side-size-h tall, on size alone (D54); a taller one from breakpoint-wide, or landscape from
# breakpoint-side-min (D41)
SIZE = f"(min-width:{size_w}) and (min-height:{size_h})"
WIDE = (f"(min-width:{side_short}),{SIZE},(min-width:{bp}) and (min-height:{short}),"
        f"(min-aspect-ratio:{ratio}) and (min-width:{side}) and (min-height:{short})")
if args.query:
    print({"side-by-side": WIDE, "side-size": SIZE}[args.query])
    sys.exit(0)
version = tok["version"]
out = [f"/* Printable-parts design system v{version}. Generated by scripts/build-tokens.py from tokens.json. Do not edit. */"]
themes = [t["id"] for t in tok["color"]["themes"]]
scheme = {t["id"]: t["colorScheme"] for t in tok["color"]["themes"]}
def block(sel, lines): out.append(sel + " {\n" + "\n".join("  " + l for l in lines) + "\n}")
light, other = [f"color-scheme: {scheme[themes[0]]};"], {t: [f"color-scheme: {scheme[t]};"] for t in themes[1:]}
for c in tok["color"]["tokens"]:
    v = c["value"]
    if isinstance(v, dict):
        light.append(f"--{c['name']}: {v[themes[0]]}; /* {c['usage']} */")
        for t in themes[1:]:
            if t in v and v[t] != v[themes[0]]: other[t].append(f"--{c['name']}: {v[t]};")
    else:
        light.append(f"--{c['name']}: {v}; /* {c['usage']} */")
block(":root, [data-theme=\"%s\"]" % themes[0], light)
for t, lines in other.items(): block(f'[data-theme="{t}"]', lines)
root_vars = [f"--{x['name']}: {x['value']}; /* {x['usage']} */" for g in ("spacing", "radius") for x in tok[g]["tokens"]]
fam = tok["type"]["families"]["ui"]
root_vars.append(f"--font-ui: {fam};")
WEIGHT_NAME = {"400": "regular", "700": "bold"}
for w in sorted({str(f["weight"]) for f in tok["type"]["fonts"]}):
    root_vars.append(f"--weight-{WEIGHT_NAME[w]}: {w}; /* the {WEIGHT_NAME[w]} face in fonts/ */")
for g in tok["type"]["groups"]:
    for s in g["styles"]:
        root_vars.append(f"--text-{s['name']}: {s['fontWeight']} {s['fontSize']}/{s['lineHeight']} var(--font-ui); /* {s['usage']} */")
        if s.get("letterSpacing", "0") not in ("0", 0):
            root_vars.append(f"--text-{s['name']}-tracking: {s['letterSpacing']}; /* the shorthand cannot carry letter spacing */")
block(":root", root_vars)
# A token's touch value, after the :root block so it wins there: control-h becomes tap on a touch screen
touch = [f"--{x['name']}: {x['touch']};" for g in ("spacing", "radius") for x in tok[g]["tokens"] if "touch" in x]
if touch:
    out.append("@media (pointer: coarse) {\n  :root {\n" + "\n".join("    " + l for l in touch) + "\n  }\n}")
for g in tok["type"]["groups"]:
    for s in g["styles"]:
        out.append(f".ws-type-{s['name']} {{\n  font-family: var(--font-ui);\n  font-size: {s['fontSize']};\n  line-height: {s['lineHeight']};\n  font-weight: {s['fontWeight']};\n  letter-spacing: {s.get('letterSpacing','0')};\n" + (f"  text-transform: {s['textTransform']};\n" if s.get("textTransform") else "") + "}")
for f in tok["type"]["fonts"]:
    a, d = overrides(f["file"])
    out.append('@font-face {\n  font-family: "%s";\n  src: url("%s") format("woff2");\n  font-weight: %s;\n  font-style: %s;\n  ascent-override: %.2f%%;\n  descent-override: %.2f%%;\n  line-gap-override: 0%%;\n  font-display: swap;\n}' % (f["family"], f["file"], f["weight"], f["style"], a, d))
(root / "tokens.css").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")   # the same bytes on every OS

errors = []
bundle = (root / "components/bundle.css").read_text(encoding="utf-8")
if "@font-face" in bundle or "url(data:" in bundle:
    errors.append("bundle.css declares or embeds a font; the fonts load once, from fonts/ through tokens.css")
FREE =f"(max-height:{short}),(min-aspect-ratio:{ratio})"   # nothing pinned: short, or landscape and stacked
FORCED = "(forced-colors:active)"   # the user's own colours: the only place for system colours
MEDIA_OK = (WIDE, FREE, f"(min-width:{bp})", f"(min-width:{hdr})", f"(max-height:{short})", "(pointer:coarse)", FORCED)
if f"@media {WIDE}" not in bundle:
    # Say which guard is gone: the side-by-side query is the one on the landscape ratio that pins (no max-height)
    found = next((m for m in re.findall(r"@media\s*([^{]+?)\s*\{", bundle) if "min-aspect-ratio" in m and "max-height" not in m), "")
    why = [w for w, gone in (("landscape only from breakpoint-side-min (D41)", f"(min-width:{side})" not in found),
                             ("a short screen only from breakpoint-side-short (D52)",
                              f"(min-width:{side_short})" not in found or f"(min-height:{short})" not in found),
                             ("a short screen narrower than that only from breakpoint-side-size-w wide and breakpoint-side-size-h tall (D54)",
                              SIZE not in found)) if gone]
    errors.append(f"bundle.css should put the sidebar beside the stage at @media {WIDE}" + ("".join(", " + w for w in why)))
if f"@media {FREE}" not in bundle:
    errors.append(f"bundle.css should pin nothing on a short screen or a stacked landscape one, at @media {FREE} (D41)")
if f"@media (min-width:{hdr})" not in bundle:
    errors.append(f"bundle.css should show the header's actions in its row at @media (min-width:{hdr}), breakpoint-header (D49)")
for m in re.findall(r"#[0-9a-fA-F]{3,8}\b", bundle):
    errors.append(f"bundle.css has a hard-coded colour {m}; use a token")
fonts = (root / "fonts").resolve()
for doc in sorted(fonts.rglob("*.md")):
    for link in re.findall(r"\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
        name = doc.relative_to(root).as_posix()
        if re.search(r"github\.com/AlonRR/printable-parts-design-system", link, re.I):
            errors.append(f"{name} links this repository ({link}); the copy in a public tool cannot follow it")
        elif not re.match(r"[a-z][a-z0-9+.-]*:|#", link, re.I) and not (doc.parent / link.split("#")[0]).resolve().is_relative_to(fonts):
            errors.append(f"{name} links {link}, outside fonts/; the tools copy fonts/ alone")
# 6. Nothing typed that a token holds.
NAMED = set("""aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet
brown burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid darkred
darksalmon darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet deeppink deepskyblue
dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro ghostwhite gold goldenrod gray
green greenyellow grey honeydew hotpink indianred indigo ivory khaki lavender lavenderblush lawngreen
lemonchiffon lightblue lightcoral lightcyan lightgoldenrodyellow lightgray lightgreen lightgrey lightpink
lightsalmon lightseagreen lightskyblue lightslategray lightslategrey lightsteelblue lightyellow lime limegreen
linen magenta maroon mediumaquamarine mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue
mediumspringgreen mediumturquoise mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite navy
oldlace olive olivedrab orange orangered orchid palegoldenrod palegreen paleturquoise palevioletred papayawhip
peachpuff peru pink plum powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown
seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen steelblue tan teal
thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen""".split())
SYSTEM = {c.lower() for c in """Canvas CanvasText LinkText VisitedText ActiveText ButtonFace ButtonText ButtonBorder Field
FieldText Highlight HighlightText SelectedItem SelectedItemText Mark MarkText GrayText AccentColor AccentColorText""".split()}
COLOUR_FN = r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color|color-mix|light-dark)\("
LITERAL_OK = {"0", "50%", "100%", "100vw", "100vh", "100svh", "1fr", "1lh"}   # geometry, not design values
UNIT = r"(?<![\w.-])-?(?:\d+\.?\d*|\.\d+)(?:px|rem|em|vh|vw|svh|dvh|lvh|vmin|vmax|%|ch|ex|lh|fr|deg|turn|s|ms|pt|cm|mm|in)\b"
css = re.sub(r"/\*.*?\*/", "", bundle, flags=re.S)
defined = set(re.findall(r"^\s*(--[a-z0-9-]+):", (root / "tokens.css").read_text(encoding="utf-8"), re.M))
def style_rules(text):
    """Every rule that declares, in order: (the at-rules it sits in, its selectors, [(property, value)]).
    A style rule, or an at-rule that declares itself, as @font-face does, with no selectors and its own
    head last among the at-rules. The declarations are pairs, in order: a rule may declare a property
    twice (content, with and without alternative text), and each is checked."""
    found, at, i = [], [], 0
    while (j := min((k for k in (text.find("{", i), text.find("}", i)) if k >= 0), default=-1)) >= 0:
        if text[j] == "}":
            at = at[:-1]; i = j + 1; continue
        if (head := text[i:j].strip()).startswith("@"):
            end, inner = text.find("}", j), text.find("{", j + 1)
            if end < 0 or 0 <= inner < end:
                at = at + [head]; i = j + 1; continue   # a block of rules: @media, @supports
            where, sels = at + [head], set()
        else:
            end = text.index("}", j)
            where, sels = at, {s.strip() for s in re.split(r",(?![^()]*\))", head)}
        found.append((where, sels, [tuple(x.strip() for x in d.split(":", 1)) for d in text[j + 1:end].split(";") if ":" in d]))
        i = end + 1
    return found
rules = style_rules(css)   # bundle.css parsed once, for every check below that reads its rules
styled = [r for r in rules if r[1]]   # the style rules: those with selectors
for rule in sorted(set(re.findall(r"@([a-z-]+)", css)) - {"media", "supports", "font-face"}):
    errors.append(f"bundle.css has @{rule}; the stylesheet's only at-rules are @media, on the queries below, and @supports")
for m in re.findall(r"@media\s*([^{]+?)\s*\{", css):
    if m not in MEDIA_OK:
        errors.append(f"bundle.css has @media {m}; the queries are {', '.join(MEDIA_OK)}")
# The header changes at its own width, breakpoint-header, not the layout's, so the name stays whole (D49).
for at, sels, props in styled:
    for q in (f"@media (min-width:{bp})", f"@media {WIDE}"):
        for s in sorted(s for s in sels if s.startswith(".ws-header") and q in at):
            errors.append(f"bundle.css styles {s} at {q}; the header changes at breakpoint-header, @media (min-width:{hdr}) (D49)")
# Values live in tokens.json: the stylesheet sets no custom property, a touch screen's included (a token's
# touch value, which tokens.css sets); and a token reads only tokens tokens.css defines.
for g in ("spacing", "radius"):
    for x in tok[g]["tokens"]:
        for key in ("value", "touch"):
            for name in re.findall(r"var\((--[a-z0-9-]+)", str(x.get(key, ""))):
                if name not in defined:
                    errors.append(f"tokens.json's {x['name']} reads {name} in its {key}, which tokens.css does not define")
for at, sels, props in styled:
    for p, v in props:
        if p.startswith("--"):
            errors.append(f"bundle.css sets {p}; values live in tokens.json, a touch screen's too, as a token's touch value")
        if SYSTEM & set(re.findall(r"[a-z]+", re.sub(r"var\([^)]*\)", "", v).lower())) and f"@media {FORCED}" not in at:
            errors.append(f"bundle.css types a colour in '{p}:{v}'; a system colour goes only in @media {FORCED}, where it keeps a state visible")
for at, sels, props in rules:   # every declaration, @font-face's too
    for prop, val in props:
        bare = re.sub(r"var\([^)]*\)", "", re.sub(r'"[^"]*"', "", val))   # without tokens and strings
        where = f"'{prop}:{val}'"
        for name in re.findall(r"var\((--[a-z0-9-]+)", val):
            if name not in defined:
                errors.append(f"bundle.css reads {name} in {where}, which tokens.css does not define")
        if re.search(COLOUR_FN, bare) or NAMED & set(re.findall(r"[a-z]+", bare.lower())):
            errors.append(f"bundle.css types a colour in {where}; use a token")
        if re.search(r"\b(?:repeating-)?(?:linear|radial|conic)-gradient\(", bare):
            errors.append(f"bundle.css draws a gradient in {where}; DESIGN: no gradients")
        if prop == "opacity" and not re.fullmatch(r"var\(--opacity-[a-z-]+\)|0|1", val):
            errors.append(f"bundle.css sets {where}; a faded control reads var(--opacity-disabled)")
        if prop == "font-size" and not re.fullmatch(r"var\(--[a-z0-9-]+\)|inherit", val):
            errors.append(f"bundle.css sets {where}; sizes come from the type styles, var(--text-...)")
        if prop == "line-height" and not re.fullmatch(r"var\(--[a-z0-9-]+\)|inherit|normal|1", val):
            errors.append(f"bundle.css sets {where}; line heights come from the type styles (1 only for a glyph's own box)")
        if prop == "font-family" and val not in ("var(--font-ui)", "inherit"):
            errors.append(f"bundle.css sets {where}; one family, var(--font-ui)")
        if prop == "font" and not re.fullmatch(r"var\(--text-[a-z-]+\)|inherit", val):
            errors.append(f"bundle.css sets {where}; use a type style, var(--text-...)")
        if prop == "font-weight" and not re.fullmatch(r"var\(--weight-[a-z]+\)|inherit|normal", val):
            errors.append(f"bundle.css sets {where}; use var(--weight-regular) or var(--weight-bold)")
        if prop == "letter-spacing" and not re.fullmatch(r"var\(--[a-z0-9-]+\)|normal|0", val):
            errors.append(f"bundle.css sets {where}; the tracking comes from the type style's token")
        for lit in re.findall(UNIT, bare):
            if lit.lstrip("-") not in LITERAL_OK:
                errors.append(f"bundle.css types the length {lit} in {where}; use a token")
# 7. Every icon as wide as it draws.
for f in tok["type"]["fonts"]:
    font = TTFont(root / f["file"]); glyf, hmtx = font["glyf"], font["hmtx"]
    past = 0
    for cp, name in font.getBestCmap().items():
        if 0xE000 <= cp < 0xF900 and glyf[name].numberOfContours:
            glyf[name].recalcBounds(glyf)
            past += glyf[name].xMax > hmtx[name][0]
    if past:
        errors.append(f"{f['file']}: {past} icons draw past their advance, so the gap to a label varies; run scripts/fit-icon-advances.py")
shipped = {str(f["weight"]) for f in tok["type"]["fonts"]}
for g in tok["type"]["groups"]:
    for s in g["styles"]:
        if str(s["fontWeight"]) not in shipped:
            errors.append(f"type style {s['name']} asks for weight {s['fontWeight']}; only {', '.join(sorted(shipped))} ship, so it would draw as another")
# 8. One version, and every class the system ships carries its prefix.
if not re.fullmatch(r"\d+\.\d+\.\d+", str(version)):
    errors.append(f"tokens.json's version is '{version}'; it must be X.Y.Z (Semantic Versioning)")
project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
if project != version:
    errors.append(f"pyproject.toml says version {project}, tokens.json {version}; they are one version")
changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
if not re.search(rf"^## v{re.escape(str(version))}\b", changelog, re.M):
    errors.append(f"CHANGELOG.md has no '## v{version}' entry; say what changed, and how to move to it")
if args.tag and args.tag != f"v{version}":
    errors.append(f"the tag {args.tag} names another version than tokens.json's {version}")
entry = re.search(rf"^## v{re.escape(str(version))}\b.*$", changelog, re.M)
if args.tag and entry and "unreleased" in entry.group(0).lower():
    errors.append(f"the tag {args.tag} is on a CHANGELOG.md entry still marked unreleased; date it, '## v{version} (16 Oct 2026)'")
for selector in re.findall(r"([^{}]+)\{", css):
    if selector.strip().startswith("@"):
        continue
    for cls in re.findall(r"\.(-?[A-Za-z_][\w-]*)", selector):
        if not cls.startswith("ws-"):
            errors.append(f"bundle.css styles the class .{cls}; every class the system ships starts ws-, so a tool's own names never collide")
# 9. A rule in a media query is not undone by a later one outside any: the same selector, setting the
# same property, wins by coming later, so the media query's value never applies.
overlap = lambda a, b: a == b or a.startswith(b + "-") or b.startswith(a + "-")   # margin and margin-left
conditional = []
for at, sels, props in styled:
    names = {p for p, _ in props}
    media = [a for a in at if a.startswith("@media")]
    if media:
        conditional.append((media[-1], sels, names)); continue
    for query, csels, cnames in conditional:
        for sel in sorted(sels & csels):
            if hit := sorted({p for p in names for q in cnames if overlap(p, q)}):
                errors.append(f"bundle.css sets {', '.join(hit)} on {sel} in {query}, and again later outside it, which undoes it; put the rule outside first")
# 10. An open popover laid out as a grid sets align-content: WebKit stretches its rows, and with them
# the popover, to the screen's height (https://bugs.webkit.org/show_bug.cgi?id=270334).
for at, sels, props in styled:
    last = dict(props)   # the value that wins, the last declared
    if last.get("display") == "grid" and "align-content" not in last and any(":popover-open" in s for s in sels):
        errors.append(f"bundle.css lays out {', '.join(sorted(sels))} as a grid without align-content; WebKit stretches it to the screen's height")
print("wrote tokens.css")
for e in errors: print("FAIL", e)
sys.exit(1 if errors else 0)
