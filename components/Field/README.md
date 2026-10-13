A labelled input or select with its help note and its error line, the unit of every form on the page.

Provide the label text with the unit in brackets (`Opening width (mm)`), an `input` with `inputmode="decimal"` and `autocomplete="off"`, and an error `span` after it. Put help text in a `.ws-note` directly under the field, never in a placeholder. Mark a bad value with `aria-invalid="true"` and write the reason in the error span (`.ws-error`), so the message does not depend on colour. Keep the error span in the layout when empty so the form does not jump.
