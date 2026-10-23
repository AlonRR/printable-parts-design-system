# Sides

Skådis Air only. Four toggle buttons round a small drawing of the board, one at each side, to
choose which sides are closed (a solid edge) and which stay open (half slots, to join a
neighbour).

- **State:** each button is a `button` with `aria-pressed`. Pressed is `action-tint` with an
  `action` ring and a bold label, and its box is filled and ticked: a tick means pick several. The
  box is the radio's size and drawn pressed or not, so pressing never moves the layout. A chosen
  `Choice` looks the same but shows a radio, as it is pick-one (D26).
- **Markup:** a `.ws-sides` group (`role="group"`, `aria-label="Closed sides"`) of four
  `button.ws-sides__btn`, each placed by `ws-sides__top`, `ws-sides__left`, `ws-sides__right` or
  `ws-sides__bottom`, round a `.ws-sides__board`, the drawing, which is decorative and
  `aria-hidden`.
- **Width:** 300px, its board drawing `sides-w` wide, where there is room. In a narrower space the
  drawing gives way, so the group fits the least sidebar side by side, 320px (D98): there the
  drawing is 86px wide, and 52px inside a fieldset. The buttons keep their size.
- **Defaults:** a single panel is open all round; a wall is closed round its outer edge and open
  at its seams.
- **Labels:** label each button with the side's name alone ("Left"), not an icon alone and not its
  state ("Left: closed" makes four buttons wider than a phone). Caption the group "Sides (ticked
  = closed)".
