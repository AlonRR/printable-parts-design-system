Modal for one short choice with a confirm and a cancel.

Use the native `dialog` element, `dialog.ws-dialog`, labelled by its `h2` heading (`aria-labelledby`). Group related choices in fieldsets, shown as `Choice` buttons, keep a `.ws-note` for live status (`aria-live="polite"`), and end with a `menu` of Cancel then the primary action, right-aligned. Do not use a dialog for anything that can sit on the page.
