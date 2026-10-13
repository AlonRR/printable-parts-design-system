# Fonts and icons

`fonts/FiraCodeNF.woff2` and `FiraCodeNF-Bold.woff2` are subsets of **FiraCode Nerd Font** (Regular and Bold): Basic Latin, Latin-1, punctuation, arrows, Powerline (U+E0A0 to U+E0D7), Codicons (U+EA60 to U+EBFF) and Font Awesome (U+F000 to U+F2FF). They are embedded as base64 in `components/bundle.css`.

Components and their upstream licences, to be confirmed against each project's current licence files before this repo is shared:

- **Fira Code**: SIL Open Font License 1.1.
- **Nerd Fonts** (the patched family and its patcher): see the Nerd Fonts repository; the patched fonts keep the base font's licence.
- **Codicons** (Microsoft): icons under CC BY 4.0, which requires attribution.
- **Font Awesome Free** glyphs: icons CC BY 4.0, font files SIL OFL 1.1; attribution required.

Add the full licence texts under `licenses/` when the licence of this repo is decided. A subset is a modified font; the family keeps the Nerd Fonts name, which the OFL permits when the original reserved names are not reused, but check this too.

To rebuild a subset: `pyftsubset` with the Unicode ranges above, `--flavor=woff2`, `--layout-features='*'` (ligatures must survive).
