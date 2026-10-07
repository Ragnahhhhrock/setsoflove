-- SetsOfLove opens to all gym-goers. Each profile now says who the member is, who they'd like to meet and what they're after.
-- gender: man | woman | non-binary
-- interested_in: comma-separated, any of men, women, non-binary
-- seeking: comma-separated, any of dates, relationship, marriage, friendship, fun
ALTER TABLE profiles ADD COLUMN gender TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN interested_in TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN seeking TEXT NOT NULL DEFAULT '';

-- Every profile created so far is a man looking to meet women, so fill those in. Members can change them at any time.
UPDATE profiles SET gender = 'man', interested_in = 'women';
