A labelled text field for the profile form, including the link stub field that shows the `setsoflove.com/` prefix.

**The consumer provides** the label, the field's value, whether it is required, and any helper or error text. Always render a real `<label>` tied to an `<input>` or `<textarea>`.

- Label in `label` style above the field. Mark required fields with the word "Required" in `ink-muted`, not an asterisk alone.
- Input: `surface-raised`, 1.5px `control-border`, `radius-md`, 44px minimum height, `body` text.
- Helper text in `body-s` `ink-muted`. Error text in `body-s` `status-rejected` with an alert icon, and the border switches to `status-rejected`.
- Focus: solid 2px `focus` ring with a 2px offset.
- Link stub field: fixed `setsoflove.com/` prefix in `ink-muted`, then the editable stub.
- No field accepts contact details; the helper text says so where it matters.

**Don't** use placeholder text as the label or rely on red alone to show an error.
