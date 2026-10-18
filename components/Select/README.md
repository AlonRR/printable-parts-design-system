# Select

A pick-one list the browser opens: the native `<select>`, drawn from tokens (D69). Use it for a
long list, such as printer models; for up to about seven short options use `Choice`, which keeps
every option in sight.

## Markup

- **The select** is a Field's input, `select.ws-input`, alone in a `span.ws-select`, which draws
  its chevron. Wrap the label text and the span in one `label.ws-label`, as a Field does.
- **The options** are plain `<option>`s, grouped under `<optgroup label="…">`s where the list has
  groups. Keep each to a few words, as a select is as wide as the sidebar.
- **A default:** have one chosen, as a Choice does.
- **Help text, errors and a disabled select** are a Field's: a `.ws-note` under it, an error span
  (`.ws-error`, `aria-live="polite"`) after the label with `aria-invalid="true"` on the select,
  both linked with `aria-describedby`; `disabled` fades it, its chevron too.

```html
<label class="ws-label">Printer<span class="ws-select"><select class="ws-input" aria-describedby="printer-note"><option>Prusa MK4S</option><option selected>Bambu Lab P1S</option><option>Custom size</option></select></span></label>
<p class="ws-note" id="printer-note">Sets the bed size; Custom size takes yours.</p>
```

## How it is drawn

The select is exactly `control-h` tall, `tap` on a touch screen, with a field's border, focus ring,
error outline and fading, as it is a `.ws-input`; a hover tints it, as a press opens it. Its
`color-scheme` is the page's, so the list the browser opens follows the theme.

The chevron is the Codicon `chevron-down` (U+EAB4) from the system's font, drawn by
`.ws-select::after` in a `control-h` square at the select's end, over the select, which keeps the
square free of its text. It is text in `ink`, so it follows the theme, and in forced colours it
takes the user's text colour. It lets a press through to the select (`pointer-events: none`), and
its alternative text is empty (`content: "\eab4" / ""`), so a screen reader skips it, as
`aria-hidden` would on an element; the label beside it says what the list is.

Why this way: `appearance: none` takes away the browser's own arrow, which each engine draws in its
own way, WebKit's at 42.5px tall with a mouse (measured in WebKit 27.2); an image as the arrow
could not follow the theme, and one drawn as a mask with a background colour would vanish in
forced colours, where backgrounds give way to the user's own; and a `<select>` cannot draw a
pseudo-element of its own, so the span draws it. `check-previews.py` fails if a select is not in a
`.ws-select`, if its chevron is not in the font, is drawn under something, is not in the select's
text colour, lies over its text or takes the press, and if the browser's own arrow comes back.
