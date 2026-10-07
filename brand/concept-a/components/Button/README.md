The button for every action in the app, in three variants: primary, secondary and ghost.

**The consumer provides** a short sentence-case label (two to three words, such as "Send for approval") and the click handler. A button is always a real `<button>` or `<a>`.

- Primary: `action` fill with `on-action` text. One per screen, for the step that moves a profile forward.
- Secondary: transparent with a 1.5px `control-border` outline and `ink` text.
- Ghost: no border, `brand-text` text, for low-priority actions such as "Report this profile".
- Style: `label`, 44px minimum height, `radius-md`, `space-5` side padding.
- Focus: solid 2px `focus` ring with a 2px offset.

**Don't** put `brand` coral behind button text, stack two primary buttons, or use all-caps labels.
