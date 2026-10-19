# SetsOfLove blog

A blog to grow search discoverability for SetsOfLove. 91 articles, one a day from 20 Oct 2026 to 18 Jan 2027, published automatically at a random time each day (Perth time).

## How it works

- Posts: `content/blog/posts/<slug>.md`. Order, topic and publish time: `content/blog/plan.json`. Calendar: `content/blog/SCHEDULE.md`.
- `python3 scripts/build_blog.py` builds only posts whose `publish_at` has passed into `public/blog/`, `public/sitemap.xml`, the RSS feed and the homepage "From the blog" list.
- `.github/workflows/publish-blog.yml` runs that build every 15 minutes and commits any change. The push redeploys Cloudflare Pages. A post therefore goes live within about 15 minutes of its scheduled time (GitHub can delay scheduled runs a little more).
- `python3 scripts/check_blog.py` (also run by `check_conformance.py`) checks every post against the style guide.
- To move a post, edit `publish_at` in `plan.json`. To add posts, append to `plan.json`, write the file, then run `python3 scripts/schedule_blog.py` (it re-spreads all unpublished and published posts, so only run it before launch, or edit times by hand afterwards).
- Writing rules, tone and product facts for new posts: `content/blog/BRIEF.md`.

## What the research said

- Google doesn't penalise AI-assisted writing. It penalises many pages made mainly to rank, with nothing new for the reader ([spam policies](https://developers.google.com/search/docs/essentials/spam-policies)). Every post therefore has a specific angle, concrete steps and no invented data.
- Google asks for clear authorship and honesty about how content is made ([helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)). Posts are bylined "The SetsOfLove team". Don't add fake author names or credentials. **Decision for Mal:** these articles were drafted with AI. Google's guidance suggests saying so where readers might wonder. Review the posts, add real experience where you have it, and consider a short "how we write" note.
- Article structured data has no required properties; headline, dates, image and author are recommended ([docs](https://developers.google.com/search/docs/data-types/article)). Every post carries `BlogPosting` and `BreadcrumbList` data.
- Sitemaps: Google ignores `priority` and `changefreq` and trusts `lastmod` only when accurate ([docs](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)). `lastmod` is the publish date, or the `updated:` field in a post's front matter when you materially edit it.
- Topic clusters: each pillar has a hub page (`/blog/topic/<pillar>/`) linking to its posts, and each post links back to the hub plus related posts.
- Safety advice follows Victoria Police and Australian government guidance on romance scams: slow pace, never send money, meet in public, tell a friend, report to Scamwatch or ReportCyber.
- The search results for "gym dating" and "gym etiquette" are crowded with generic listicles. We compete on being specific, respectful, consent-first and Australian, and on product-grounded pages the big sites can't write (profile links, approval, photo rules, no messages).
- No keyword volume data was available, so topics are chosen from search intent and gaps, not volumes. Check Search Console after 4 to 6 weeks and double down on what gets impressions.

## Personas (planning composites, not real members)

| Id | Who | What they want | Content they need |
|---|---|---|---|
| jess | Late 20s to mid 30s, trains early or around shifts | Someone who respects a routine, open to a relationship | Dating around training, shift work, early mornings |
| dave | Mid 30s, lifts, newly single, wary of apps | A calm way to meet people, straight talk | Approaching respectfully, profile basics, lifts on a profile |
| priya | Mid 20s, loves classes, new to the city | Friends and dates | Making friends at the gym, classes, places to meet |
| alex | Late 20s, non-binary | Consent, inclusive spaces, to be themselves | Etiquette, photo consent, privacy, honest profiles |
| marcus | Early 40s, a second chapter, trains seriously | A long-term relationship or marriage | Dating over 40, intent, balance, training as a couple |
| mia | Early 20s, newer to training, building confidence | Fun, friendship, low pressure | Gym confidence, photo tips, budget-friendly dates |
| kai | The friend who shares links and makes introductions | For it to go well | Introductions, sharing links safely, reporting |

## Content pillars

| Pillar | Posts | Purpose |
|---|---|---|
| Meeting people at the gym | 16 | Top-of-funnel search: etiquette, approaching, friends |
| Profiles and photos | 16 | Product-led: mirror selfies, bios, lifts, how SetsOfLove works |
| Dating around training | 17 | Date ideas and scheduling for active people |
| Dating safely | 14 | Trust: scams, privacy, consent, reporting |
| Lifts and gym life | 14 | Training audience: the four lifts, tracking, routine |
| Connection and intent | 8 | Dates, relationship, marriage, friendship, rejection |
| Perth and Australia | 6 | Local and seasonal: outdoors dates, summer training |

Seasonal posts are pinned: summer water dates (mid Nov), heat and training (late Nov), the holiday routine (mid Dec), January gym crowds (early Jan) and Valentine's Day (mid Jan, ahead of 14 Feb).

## After launch

1. Add `https://setsoflove.com` to Google Search Console and Bing Webmaster Tools, then submit `https://setsoflove.com/sitemap.xml`.
2. Confirm the homepage is no longer `noindex` (it was; it is now indexable so the blog can send people to it). Profile pages stay `noindex`.
3. After 4 to 6 weeks, review impressions and clicks by post. Refresh or expand what ranks on page 2, and retire anything that gets nothing.
4. Plan the next 90 days from what worked. Don't repeat topics.
