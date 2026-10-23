# Help

A field's help, folded behind an "i" button beside its label (D94). A form with a note under every
field reads as a wall of text, so each note can wait until it is asked for. The "i" is the one
button whose icon stands alone (DESIGN.md, Iconography): it repeats beside every field, where a
word would repeat a dozen times, and its name says what it opens.

## Markup

- **The row:** a `div.ws-label-row` holds the field's `label.ws-label`, which names the field by
  its `id` (`for`) as a Stepper's label does, and after it the toggle. The label is not wrapped
  round the field, as a Field's is: inside it, the toggle's name would join the field's.
- **A group:** the row is the fieldset's `legend.ws-label-row`, its words in a `span` with an `id`,
  and the fieldset is named by those words alone (`aria-labelledby`), not by the toggle's name too.
- **The toggle:** a quiet Button, `button.ws-btn.ws-btn--quiet.ws-help-toggle`, `type="button"`,
  holding one icon, Codicons' info (`&#xea74;`), `aria-hidden`. Its name says what it opens:
  `aria-label="About <label>"`, the label without its unit ("About thickness").
- **The help:** the field's `p.ws-note`, where a Field puts it, under the field (a group's, after
  the group), `hidden` while it is folded. The toggle's `aria-controls` names it, and its
  `aria-expanded` says whether it shows.
- **Still read:** the help stays in the field's `aria-describedby` (the fieldset's, for a group)
  while it is hidden. A description may name hidden text, so a screen reader reads the help with
  the field, folded or not.
- **Only help folds.** A warning, an error, a count, or anything a field needs to be filled in
  right is always shown.
- **Folded to start, and nothing remembered:** every help is folded when a form opens.

The toggle is a `control-h` square, so a touch target each way on a touch screen, pulled into its
label's line by `control-pad-y` above and below, so the row is no taller than the label. Its icon
sits on the box's centre, raised by `--icon-rise` as an icon beside a label is (D88).

```html
<div class="ws-label-row"><label class="ws-label" for="thick">Thickness (mm)</label><button class="ws-btn ws-btn--quiet ws-help-toggle" type="button" aria-label="About thickness" aria-expanded="false" aria-controls="thick-help"><span class="ws-ic" aria-hidden="true">&#xea74;</span></button></div>
<input class="ws-input" id="thick" inputmode="decimal" autocomplete="off" value="12" aria-describedby="thick-help thick-err">
<p class="ws-note" id="thick-help" hidden>How thick the board is.</p>
<span class="ws-error" id="thick-err" aria-live="polite"></span>
```

## The tool's script

A press shows the help, and another hides it. These are the Disclosure toggle's lines (D59): they
serve every button with `aria-controls` and `aria-expanded`, a help toggle too, so a tool that has
them adds nothing, and one that has neither adds them once. `check-previews.py` runs them on the
previews and fails if a press does not show or hide a help as this section says.

```js
for (const toggle of document.querySelectorAll('button[aria-controls][aria-expanded]'))
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    document.getElementById(toggle.getAttribute('aria-controls')).hidden = !open;
  });
```
