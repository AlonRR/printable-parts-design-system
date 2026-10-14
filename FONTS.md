# Fonts and icons

`fonts/FiraCodeNF.woff2` and `FiraCodeNF-Bold.woff2` are subsets of **FiraCode Nerd Font** (Regular and Bold): Basic Latin, Latin-1, punctuation, arrows, Powerline (U+E0A0 to U+E0D7), Codicons (U+EA60 to U+EBFF) and Font Awesome (U+F000 to U+F2FF). They are embedded as base64 in `components/bundle.css`.

Components and their upstream licences, checked against each project's licence file on 14 Oct 2026 (`STATUS.md`, step 5); the texts are in [`licenses/`](licenses/README.md):

- **Fira Code**: SIL Open Font License 1.1.
- **Nerd Fonts** (the patched family and its patcher): see the Nerd Fonts repository; the patched fonts keep the base font's licence.
- **Codicons** (Microsoft): icons under CC BY 4.0, which requires attribution.
- **Font Awesome Free** glyphs: icons CC BY 4.0, font files SIL OFL 1.1; attribution required.
- **Powerline** glyphs (Powerline and Powerline Extra Symbols, via Nerd Fonts): MIT.

The licence texts and the credits travel in `licenses/`: copy that folder wherever `fonts/` or `bundle.css` goes. A subset is a modified font; it keeps the name FiraCode Nerd Font, which the OFL permits because neither Fira Code nor Nerd Fonts reserves a font name.

To rebuild a subset: `uv run pyftsubset` with the Unicode ranges above, `--flavor=woff2`, `--layout-features='*'` (ligatures must survive).
