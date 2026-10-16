A grid of buttons that mirrors the wall as seen from the room, to choose one piece.

The user supplies the column and row counts: the pieces are `button.ws-piece` in a `.ws-map` whose `grid-template-columns` is set to the column count; piece 1,1 is the bottom left. A toggle button uses `aria-pressed`; the chosen piece is `action-tint` with an `action` ring and border (D26), and a piece with its own setting is bold (`data-own="yes"`), so state never relies on colour. Show the chosen piece's controls directly beneath the grid.
