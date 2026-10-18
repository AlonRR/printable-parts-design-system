# Gallery

A grid of picture tiles to choose from, instead of a dropdown, when the options are visual.

Use it for panel fills (for example sealed, grid, dots, brick) and for saved presets. Each tile is a `button.ws-tile` with `aria-pressed`, a small drawing of the result and a one-word label, in a `.ws-gallery`, four to a row in the sidebar. Put the most common choice first and show the current one as every selected state is (D26): `action-tint`, an `action` ring and border, and a bold label, so it never relies on colour. If there are more than about 12, add a "More fills…" button that opens the full set in a dialog.
