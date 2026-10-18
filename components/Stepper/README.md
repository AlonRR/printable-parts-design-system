A number field with two buttons after it, ↓ and ↑, that move its value by the setting's step and stop at its limits (D56). Use it for a number a user nudges more than types: a size in steps, a clearance tried a little at a time. It is how a value below zero is entered on a phone: the field is `inputmode="decimal"`, whose keypad has no minus sign, and ↓ goes below zero.

The field is a `Field`'s `input.ws-input` (`inputmode="decimal"`, `autocomplete="off"`, its note and error after the row), and the buttons are two `Button`s, `button.ws-btn.ws-stepper__btn`, in a `div.ws-stepper` after it: ↓ first, then ↑. Their text is the arrow, from the font's arrows (U+2193 and U+2191), and their names say what they do, `aria-label="Smaller <label>"` and `aria-label="Larger <label>"`, the label without its unit ("Smaller slot clearance"). An arrow with a name is the button's text, not an icon, so DESIGN.md's rule that an icon never stands alone holds. The label names the field by its `id` (`label.ws-label` with `for`) and is not wrapped round the row, as a Field's is: inside it, the buttons' names would join the field's. The setting goes on the field: `data-step`, the step a press moves by; `data-min` and `data-max`, the limits it stops at, either left out for none; and `data-on-step` for a setting that keeps to its steps, counted from `data-min` (a board's size in 40 mm steps), where a press goes to the next step, not a step further.

The buttons take the field's height, so they line up with it, and are at least `control-h` wide, so a touch target each way on a touch screen; the field gives way on a narrow sidebar. A `type="number"` field, if a tool keeps one, loses the browser's spin buttons in a Stepper, as the arrows replace them; ↓ is still the way below zero there on an iPhone's keypad.

```html
<label class="ws-label" for="clearance">Slot clearance (mm)</label>
<div class="ws-stepper"><input class="ws-input" id="clearance" inputmode="decimal" autocomplete="off" value="0" data-step="0.05" data-min="-0.5" data-max="1" aria-describedby="clearance-err"><button class="ws-btn ws-stepper__btn" type="button" aria-label="Smaller slot clearance">↓</button><button class="ws-btn ws-stepper__btn" type="button" aria-label="Larger slot clearance">↑</button></div>
<span class="ws-error" id="clearance-err" aria-live="polite"></span>
```

The tool's script makes the arrows work, with the lines below (`check-previews.py` runs them on the previews and fails if a press or a key does not do what this paragraph says). A press on ↑ or ↓, or ArrowUp or ArrowDown in the field, moves the value by its step, onto its steps where it has `data-on-step`, and stops at its limits; "," reads as a decimal point, as in any Field. The keys are the script's, as a text field does not step by itself, and stop the browser's own step in a `type="number"` field. A button at a limit says so, `aria-disabled="true"`: it is drawn faded, as a disabled Button, and a press on it does nothing, but it keeps its focus and its place in the tab order, where a disabled button would drop it (Firefox moves the focus to the page). Each press that changes the value fires an `input` event, as typing does, so the part is rebuilt at once; one at a limit fires none. A tool that sets a field from its script (Reset, Load project) fires an `input` event on it too, so the arrows say again where the value is.

```js
for (const row of document.querySelectorAll('.ws-stepper')) {
  const field = row.querySelector('.ws-input'), [down, up] = row.querySelectorAll('.ws-stepper__btn');
  const { step, min = '-Infinity', max = 'Infinity' } = field.dataset;
  const by = Number(step), low = Number(min), high = Number(max), base = Number.isFinite(low) ? low : 0;
  const decimals = (text) => (text.split('.')[1] ?? '').length;
  const read = () => { const text = field.value.trim().replace(',', '.'); return text === '' ? NaN : Number(text); };
  const say = () => {
    const value = read();
    down.setAttribute('aria-disabled', String(value <= low));
    up.setAttribute('aria-disabled', String(value >= high));
  };
  const move = (sign) => {
    const typed = read(), from = Number.isFinite(typed) ? typed : Number(field.defaultValue) || 0;
    if (sign > 0 ? from >= high : from <= low) return;   // at a limit: its button says so, and nothing moves
    const q = (from - base) / by;
    const next = 'onStep' in field.dataset
      ? base + (sign > 0 ? Math.floor(q + 1e-9) + 1 : Math.ceil(q - 1e-9) - 1) * by
      : from + sign * by;
    const places = Math.max(decimals(step), decimals(String(from)));
    field.value = String(Number(Math.min(high, Math.max(low, next)).toFixed(places)));
    field.dispatchEvent(new Event('input', { bubbles: true }));
  };
  down.addEventListener('click', () => move(-1));
  up.addEventListener('click', () => move(1));
  field.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
    e.preventDefault();
    move(e.key === 'ArrowUp' ? 1 : -1);
  });
  field.addEventListener('input', say);
  say();
}
```
