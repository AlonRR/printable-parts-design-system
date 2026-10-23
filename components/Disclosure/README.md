# Disclosure

A collapsible section that keeps rarely changed settings out of the way.

- **Markup:** a native `details.ws-details` with a short `summary.ws-summary`, at least
  `control-h` tall.
- **Title** them like "Advanced: the joint between pieces".
- **Lead with a `.ws-note`** saying the values are starting values and what a test print will
  tell.
- **Never hide a required field** inside one.

## A toggle in a row of buttons

A toggle that must sit in a row of buttons (D59), such as Skådis Air's "Show all files" beside
"Download all", cannot be a `details`: its summary heads its own box.

- Make it a plain Button in the row (`button.ws-btn` in `.ws-actions`), with `aria-expanded`
  saying whether the section shows and `aria-controls` naming it.
- Give the section the `hidden` attribute while it is closed. The tool's script flips both when
  the button is pressed.
- The label stays the same, open or closed, as `aria-expanded` says which.
- It needs no CSS of its own: the button is a Button, and `hidden` hides anything the system
  styles (D57).
- A help toggle, the "i" beside a field's label, is one too (`Help`, D94): the lines below serve
  it as well, so a tool adds them once.

```html
<div class="ws-actions">
  <button class="ws-btn" type="button">Download all</button>
  <button class="ws-btn" type="button" aria-expanded="false" aria-controls="files">Show all files</button>
</div>
<div id="files" hidden>
  <!-- the list of files -->
</div>
```

```js
for (const toggle of document.querySelectorAll('button[aria-controls][aria-expanded]'))
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    document.getElementById(toggle.getAttribute('aria-controls')).hidden = !open;
  });
```
