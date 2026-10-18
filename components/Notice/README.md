# Notice

Inline message for a warning or error about the plan, never a toast.

Start with a bold one-line headline (`strong`) that says what is wrong, then one sentence on how to fix it. Use a variant: `ws-notice--warning` for something that does not block (a board larger than the bed), `ws-notice--error` for something that does; each turns the border and the headline to `warning` or `error`, and the words carry the meaning. Place it next to the thing it concerns. The notice can be kept in the page empty, as the `aria-live="polite"` region that announces it: an empty `.ws-notice` takes no room, and shows when the tool writes into it. For a word of warning inside other text, `.ws-warning` colours it `warning`; the words still carry the meaning.
