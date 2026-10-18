# Fonts and icons

`fonts/FiraCodeNF.woff2` and `FiraCodeNF-Bold.woff2` are subsets of **FiraCode Nerd Font** (Regular and Bold): Basic Latin, Latin-1, punctuation, the arrows ← ↑ → ↓ (U+2190 to U+2193: "Next: Fittings →", and a `Stepper`'s ↓ and ↑), the minus sign (U+2212), the check mark (U+2713), Powerline (U+E0A0 to U+E0D7), Codicons (U+EA60 to U+EBFF) and Font Awesome (U+F000 to U+F2FF). `tokens.css` loads them with its `@font-face` rules, so keep `fonts/` beside `tokens.css`; nothing else declares a font.

Components and their upstream licences, checked against each project's licence file on 14 Oct 2026 (`STATUS.md`, step 5); the texts are in [`fonts/licenses/`](fonts/licenses/README.md):

- **Fira Code**: SIL Open Font License 1.1.
- **Nerd Fonts** (the patched family and its patcher): see the Nerd Fonts repository; the patched fonts keep the base font's licence.
- **Codicons** (Microsoft): icons under CC BY 4.0, which requires attribution.
- **Font Awesome Free** glyphs: icons CC BY 4.0, font files SIL OFL 1.1; attribution required.
- **Powerline** glyphs (Powerline and Powerline Extra Symbols, via Nerd Fonts): MIT.

The licence texts and the credits are in `fonts/licenses/`, inside `fonts/`, so they travel with the fonts. A subset is a modified font; it keeps the name FiraCode Nerd Font, which the OFL permits because neither Fira Code nor Nerd Fonts reserves a font name.

To rebuild a subset: `uv run pyftsubset` with the Unicode ranges above, `--flavor=woff2`, `--layout-features='*'` (ligatures must survive), then `uv run python scripts/fit-icon-advances.py`. The patched fonts give each icon one text cell and draw most of them wider; that script sets each icon's advance to the width it draws, so the gap to its label is `icon-gap` for every icon. Text glyphs keep their cell. `scripts/build-tokens.py` fails if a rebuilt subset skips the step.
