# SetsOfLove scope and content policy

## What it is

A simple profile app for single gym-goers of any gender: men, women and non-binary people looking for dates, a relationship, marriage, friendship or just fun. Members create a profile, the admin approves it, and each approved profile lives at its own link (`setsoflove.com/sam-t`). Anyone can create an account, no invitation needed.

## Who it's for

- Any gym-goer who is 18 or over and single, at any gym
- Each member says who they are (man, woman or non-binary), who they'd like to meet (any mix of men, women and non-binary people) and what they're after (any mix of dates, a relationship, marriage, friendship and just fun)
- Nobody is steered or filtered by the app. There's no matching, so members choose how to share their own link
- Signed-in members can search live profiles by first name, link, suburb, city or country. Results are alphabetical, with no ranking, and gender and who someone would like to meet are never search filters

## Point of difference

Most dating apps treat gym photos as a side note. SetsOfLove makes them the main event. Workout photos are encouraged and appreciated, and lift stats sit on the profile next to the photos.

The voice stays friendly and dry. Keep the humour in the product, not in the body. See `STYLE_GUIDE.md` for the words we avoid.

## Tagline and homepage copy

The philosophy: SetsOfLove is where gym selfies are encouraged and welcomed on a dating app. It's for people who take pride in how they look, work hard at it and live healthy, fit lifestyles.

**Tagline:** Mirror selfies welcome.

Backup lines: "You put in the work. Show it off." and "Dating for people who train."

**Homepage hero**

> **Mirror selfies welcome.**
>
> SetsOfLove is a profile app for single gym-goers. Show off the work you put in, share your link, and let people get to know you.
>
> [Create your profile]

**Who it's for:** Single people aged 18+ who train, at any gym. Men, women and non-binary members are all welcome, looking for dates, a relationship, marriage, friendship or just fun. You choose who you'd like to meet and what you're after.

**What it is**

- Your own profile page, like setsoflove.com/sam-t
- Up to 4 photos, and gym selfies are encouraged
- Optional lift stats (bench press, squat, deadlift, overhead press) shown in kg and lb
- A few words about you and who you'd like to meet

**How it works:** Create your profile. We approve it. Share your link.

**Good to know:** No chat inbox, no comments, no algorithm. You decide where to share your link. If you like, keep your social accounts, phone or email private and share it only with people you say yes to. We approve every profile before it goes live.

Copy rule: "healthy, fit lifestyle" describes who the app is for, not a requirement to join. Gym membership and fitness aren't checked.

## Profile contents

- 1 to 4 photos, with the main photo showing the member's face clearly
- First name, age (18+), gender, who they'd like to meet, what they're after, suburb, city, country, what they do, how they train
- Optional lifts: bench press, squat, deadlift and overhead press, in kg or lb (stored in kg, shown in both)
- About you, and a few words on who you'd like to meet
- A link stub such as `sam-t`

## Required to send for approval

First name, age, gender, who they'd like to meet, what they're after, suburb, city, country, about you, a few words on who they'd like to meet, a link stub and at least 1 photo. What they do, how they train and the lifts are optional.

## Quick picks

To make the profile form faster, most text fields show tappable suggestions: country, what they do, how they train, about you, who you'd like to meet, and link stub ideas built from the member's first name, age and suburb. Tapping adds the text, tapping again removes it, and members can edit it freely. Suggestions follow `STYLE_GUIDE.md`, and a profile built from them is still approved by the admin like any other.

## Contact requests

How members get in touch without messages. It's opt-in and off by default.

- A member can add any mix of private contact methods: Instagram, Facebook, TikTok, Snapchat, X, WhatsApp, phone and email, as a name or a profile link. All are optional. They never show on the profile and isn't part of approval, so editing it doesn't take the profile offline
- The member turns on "Let members with a live profile ask for my contact details". Only then does a "Request contact" button appear on their profile
- To ask, someone must be signed in with a live profile of their own, so the member can check who is asking. There is no note or message, just the request
- The member sees the asker's name, age, place and photo, and a link to their profile. They choose Share details, Decline or Block
- A no is never announced. Anyone declined, blocked or stopped sees only "Requested", and can't ask again
- A yes shows the detail on the asker's view of that profile and in their "Shared with you" list. The member can stop sharing at any time. Changing the detail clears everyone's access, so people ask again
- Each member can ask at most 10 people in 24 hours
- Members find requests at `/requests`. Requests aren't emailed
- Requests are deleted with the account
- A member can also switch on "Let members with a live profile send me a message by email". Someone with a live profile then sees a short message form on that profile. The message goes to the owner's account email through Resend, with no reply-to and a link to the sender's profile, so the address stays private and the owner replies from the sender's profile. The text is never stored, only a log of who sent to whom and when
- Limits: 3 messages per person per day to the same member, 10 a day in total, 1000 characters, 10 minimum. A member the owner blocked from a contact request is told it worked and nothing is sent. Needs `RESEND_API_KEY`

## Photo rules

- Gym and workout photos are welcome: training shots, gym kit, a post-session mirror pic
- No nudity, nothing sexual, nothing obscene
- The member must be the person in the main photo
- No photos of other people without their consent, so no recognisable bystanders in gym shots
- No screenshots, memes, or images with text or logos

## Moderation

- Every profile is approved by the admin before it goes live
- Any edit takes a live profile offline until it is approved again
- Rejections and takedowns carry a note telling the member what to change
- Every public profile has a "Report this profile" link that goes to the contact address
- Members must be 18 or over and accept the terms before creating a profile

## Consent norms

- There are no comments, likes or public messages on profiles, so nobody gets unsolicited remarks on their photos. Emailed messages are opt-in and only from members with a live profile
- Contact details are kept out of public text fields. They are shared only through contact requests, or through mutual friends and at the gym
- Everyone is treated with the same respect, whatever their gender or who they're looking to meet. The admin removes profiles and takes action on reports that break this
- Gender and who someone would like to meet are shown only as the member chose them, and are never used to rank or suggest anyone
- Contact requests are the only way members reach each other in the app. They are opt-in, need a live profile, carry no message, never announce a no, and include block from day one. Report stays on the profile page
- If reactions are ever added, they should be opt-in, with a block and report option from day one

## Decisions

- Single is still required to join, for every kind of connection including friendship
- Gender is man, woman or non-binary. There's no free-text option for now
- Existing profiles were all men looking for women, so they were filled in that way and can be changed any time
- Gym membership is not checked. The admin approves profiles but does not confirm membership
- Lifts are self-reported, with no proof needed
- A "photo of a lift" label is left for a later version
- Contact is by request only, with no in-app messages and no free-text note on a request, so there's nothing extra to moderate
- Blocked members can't be unblocked in the app for now. The admin can help through the contact address
