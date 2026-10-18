# PieceMap

A grid of buttons that mirrors the wall as seen from the room, to choose one piece.

The user supplies the column and row counts: the pieces are `button.ws-piece` in a `.ws-map` whose `grid-template-columns` is set to the column count, `repeat(<columns>, 1fr)`, so each cell's width comes from the grid, not its label; piece 1,1 is the bottom left. A toggle button uses `aria-pressed`, one piece pressed at a time; the chosen piece is `action-tint` with an `action` ring and border (D26) and the chosen radio's dot before its label, as a pick-one (D47), and a piece with its own setting is bold (`data-own="yes"`), so state never relies on colour. Show the chosen piece's controls directly beneath the grid.
