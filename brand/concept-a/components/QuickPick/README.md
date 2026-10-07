A tappable suggestion chip that fills a profile form field: tap to add the text, tap again to remove it.

**The consumer provides** the suggestion text and whether it is currently added. Used for country, what they do, how they train, about you, what you're looking for, and link stub ideas built from the member's first name, age and suburb (for example `sam-t`, `sam-29`, `sam-subiaco`).

- Unselected: 1.5px `control-border`, `ink` text, `radius-pill`, 44px high.
- Selected: `action` fill, `on-action` text and a check icon, so selection is never colour alone.
- Set the chip in `label`. Keep suggestions short and in the voice of the style guide.
- The member can always edit the added text freely; a profile built from chips still goes to the admin for approval like any other.

**Don't** pre-select chips, add contact details to a suggestion, or write suggestions that put words in a member's mouth about their body or other people.
