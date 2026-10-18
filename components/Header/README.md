# Header

The slim top bar of the tool: the name, project actions and the theme. Everything here acts on
the whole project; step controls never go here.

## Layout

Height `header-h` (48px).

- **Left:** the tool's name (`h1.ws-header__name`, in the `step` style) and, small beside it, the
  version (`.ws-header__version`), then a `span.ws-header__spacer`, which pushes the buttons to the
  right on a wide screen.
- **Right, in this order:** Undo, Redo and Reset (quiet buttons); Save project and Load project
  (they act on the whole project); language, if any; and the "Dark theme" toggle (`aria-pressed`,
  pressed while the page is dark).
- **Icons:** each button has a Nerd Font icon before its word (undo eae2, redo ebb0, reset eb37,
  save eb4b, load eaf7, theme eac6). The icon is `aria-hidden`, and the word is always there.

## More… below `breakpoint-header`

Everything after Redo goes in `div.ws-header__actions` with `popover`, opened by a
`button.ws-header__more` "More…" (`popovertarget`): inline from `breakpoint-header` (64rem) up, a
menu under the header below it (D28). The browser gives the menu its expanded state, Escape and
light dismiss; no script is needed.

- `breakpoint-header` is wider than the layout's breakpoint (56rem), as the whole row left the
  name as little as 20px there. So on a window 56 to 64rem wide the sidebar sits beside the stage
  while the header keeps its phone row (D49).
- Below `breakpoint-header` the name takes the legend size. When the row is tight, on a narrow
  phone, the name is cut short (its full text stays in the page): the buttons never shrink, scroll
  or wrap, and nothing in the header clips a focus ring.
- From the layout's breakpoint up the name is whole, and `check-previews.py` fails if it is cut
  (D49).
- A tool whose header holds no more than fits a phone's row (Skådis Air's holds the theme toggle
  alone) leaves out More… and the popover, and its buttons and its one version stay in the row on
  every screen.

## The version tag

The version goes in twice: beside the name, and again last in `.ws-header__actions`, after the
theme toggle, `<span class="ws-header__version">v1.2.0</span>`.

- Below `breakpoint-header` the stylesheet hides the one in the row, where it cut a phone's name
  to 10 of its 120px, and the More… menu shows the other (D51). From `breakpoint-header` up the
  row's shows and the menu's is hidden.
- The hidden copy is `display:none`, so a screen reader hears one version: beside the name on a
  wide screen, and in the open menu on a phone, with the rest of the actions.
- `check-previews.py` fails if the row holds a version below `breakpoint-header`, or if more or
  fewer than one shows.
