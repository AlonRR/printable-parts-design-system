# Icons

The icon set: Codicons (thin line, lightest) and Font Awesome (solid, medium), both inside the FiraCode Nerd Font.

Use one set for the whole interface so icons match in weight: Codicons (`cod-`) for the light, thin-line look. Font Awesome (`fa-`) only where Codicons has no equivalent, and then it will look heavier. An icon goes before a text label as `<span class="ws-ic" aria-hidden="true">&#xea60;</span>`, never alone; the stylesheet raises it onto the label's capitals by `--icon-rise`, which the build derives from the font (D88). Font Awesome Light (the thin Pro style) is not part of Nerd Fonts; Codicons is the lightest available here. The card shows the curated glyphs with their names and code points; the font holds the full Codicons block (U+EA60 to U+EBFF) and Font Awesome block (U+F000 to U+F2FF).
