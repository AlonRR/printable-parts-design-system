# Button

An action button, `button.ws-btn`. `.ws-btn--primary` fills with `action`; the default is
outlined; `.ws-btn--quiet` has neither border nor fill, for the header's Undo, Redo and Reset.

- **One primary button in view**, at most, for the step that finishes the task (Download the
  pieces). Label it with a verb, and end the label with an ellipsis when it opens a dialog.
- **On a phone, in the plan bar,** it shows a short label, "Download...": the rest of its label is
  in a `.ws-plan__long` span hidden from view only, so its name stays whole and the ellipsis stays
  on screen (D39; see `Workbench`).
- **A disabled button** explains why in a note next to it.
- **A button that must keep its focus while it cannot be used**, a `Stepper`'s at a limit, takes
  `aria-disabled="true"` instead of `disabled`. It is drawn as a disabled one and takes no hover,
  keeps its place in the tab order, and the tool's script ignores a press on it. Disabled, the
  focused button would lose its focus: Firefox drops it to the page (D56).
- **Type:** buttons are `type="button"` unless they submit a form.
- **Rows:** put a row of buttons in `.ws-actions`; the plan bar (`.ws-plan__actions`) and a
  dialog's `menu` have their own.
