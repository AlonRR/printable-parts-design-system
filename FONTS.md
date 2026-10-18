# Fonts and icons

The system uses one typeface, **FiraCode Nerd Font**, with its icons built in. `fonts/` holds two
subsets of it, `FiraCodeNF.woff2` (Regular) and `FiraCodeNF-Bold.woff2` (Bold), and nothing else
declares a font: `tokens.css` loads them with its `@font-face` rules, so keep `fonts/` beside
`tokens.css`.

## What the subsets hold

- Basic Latin, Latin-1 and general punctuation.
- The arrows ← ↑ → ↓ (U+2190 to U+2193), for "Next: Fittings →" and a `Stepper`'s ↓ and ↑.
- The minus sign (U+2212) and the check mark (U+2713).
- Powerline symbols (U+E0A0 to U+E0D7), Codicons (U+EA60 to U+EBFF) and Font Awesome
  (U+F000 to U+F2FF).

## Licences

| Part | Licence |
| --- | --- |
| Fira Code | SIL Open Font License 1.1 |
| Nerd Fonts, the patched family | The patched fonts keep the base font's licence, OFL 1.1; the patcher's code is MIT |
| Codicons (Microsoft) | Icons CC BY 4.0, which asks for attribution |
| Font Awesome Free | Icons CC BY 4.0, font files SIL OFL 1.1; attribution required |
| Powerline and Powerline Extra Symbols, via Nerd Fonts | MIT |

The licence texts and the credits are in [`fonts/licenses/`](fonts/licenses/README.md), inside
`fonts/`, so they travel with the fonts. The subsets carry no licence fields of their own (name
IDs 13 and 14), and the OFL accepts the notice as a file beside the font.

A subset is a modified font. It keeps the name FiraCode Nerd Font, which the OFL permits here:
neither Fira Code nor Nerd Fonts reserves a font name ("Reserved Font Name" appears only in the
OFL's own definitions). Font Awesome's font files reserve the name "Font Awesome", which nothing
here uses.

### How the licences were checked

Each statement above was read from the upstream licence file on 14 Oct 2026, at the commit
linked:

- Fira Code: [tonsky/FiraCode `LICENSE`](https://github.com/tonsky/FiraCode/blob/ecd367b040ad92a28b64fa93135775f7e2417b37/LICENSE),
  copyright "The Fira Code Project Authors". The bundled fonts carry the same copyright and say
  `Version 6.002;Nerd Fonts 3.4.0`.
- Nerd Fonts: [`LICENSE`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/LICENSE);
  its patched FiraCode folder ships Fira Code's licence byte for byte
  ([`patched-fonts/FiraCode/LICENSE`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/patched-fonts/FiraCode/LICENSE))
  and lists both icon sets as CC BY 4.0
  ([`patched-fonts/FiraCode/README.md`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/patched-fonts/FiraCode/README.md)).
- Codicons: [`LICENSE`](https://github.com/microsoft/vscode-codicons/blob/6b53088f5c55bce7107fb579765364f59cd4ad5d/LICENSE)
  (CC BY 4.0) and, for its code,
  [`LICENSE-CODE`](https://github.com/microsoft/vscode-codicons/blob/6b53088f5c55bce7107fb579765364f59cd4ad5d/LICENSE-CODE) (MIT).
- Font Awesome Free: [`LICENSE.txt`, 6.x](https://github.com/FortAwesome/Font-Awesome/blob/840c215f894f429b26b8c1402a65da835dc5a450/LICENSE.txt).

## Rebuilding a subset

1. Subset with `uv run pyftsubset`, the Unicode ranges above, `--flavor=woff2` and
   `--layout-features='*'`, so the ligatures survive.
2. Run `uv run python scripts/fit-icon-advances.py`. The patched fonts give each icon one text
   cell and draw most of them wider; the script sets each icon's advance to the width it draws,
   so the gap to its label is `icon-gap` for every icon. Text glyphs keep their cell.
3. Run `uv run python scripts/build-tokens.py`: it fails if an icon still draws past its advance.
