A badge showing where a profile is in moderation: Pending approval, Live or Needs changes, with the admin's note when there is one.

**The consumer provides** the status and, for Needs changes, the admin's note telling the member what to change.

- Pending approval: `gold` fill, `on-gold` text, clock icon. Shown for new profiles and after any edit.
- Live: `status-live` text and 1.5px border on `surface`, check icon.
- Needs changes: `status-rejected` text and border on `surface`, alert icon, with the note beneath in `body-s` `ink`.
- Every badge is a word plus an icon in `label` style, never colour alone. `radius-sm`, 32px high.

**Don't** show a Live badge on a profile with an unapproved edit; an edit takes a live profile offline until it is approved again.
