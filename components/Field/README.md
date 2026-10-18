# Field

A labelled input or select with its help note and its error line: the unit of every form on the
page.

- **Label:** wrap the label text, with the unit in brackets (`Opening width (mm)`), and its
  `input.ws-input` in one `label.ws-label`.
- **Numbers:** give the `input` `inputmode="decimal"` for a value that cannot go below zero. For
  one that can, use a `Stepper`, whose ↓ goes below zero, or without the arrows `type="number"`,
  as the decimal keypad on a phone has no minus sign (D56). Add `autocomplete="off"`, and read ","
  as a decimal point as well as ".".
- **Width:** a number field (`type="number"` or `inputmode="decimal"`) is at most
  `--number-field-w` wide: as wide as a number, not as the sidebar.
- **Help text** goes in a `.ws-note` directly under the field, never in a placeholder.
- **Errors:** put an error span (`.ws-error`) after the input. Mark a bad value with
  `aria-invalid="true"` and write the reason in the error span, so the message does not depend on
  colour. Keep the error span in the layout when empty, so the form does not jump.
- **Wiring:** link the error and any note to the input with `aria-describedby`, and give the error
  span `aria-live="polite"`, so a screen reader reads them with the field and hears a new error.
