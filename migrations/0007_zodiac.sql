-- Optional zodiac sun sign (aries, taurus, ... pisces). Blank means not shared.
ALTER TABLE profiles ADD COLUMN zodiac TEXT NOT NULL DEFAULT '';
