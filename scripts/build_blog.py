#!/usr/bin/env python3
"""Build the blog into public/blog/, public/sitemap.xml and the homepage "From the blog" list.

Posts live in content/blog/posts/<slug>.md. Their order, topic and publish time live in
content/blog/plan.json. Only posts whose publish_at has passed are built, so a post stays
private until its time. A GitHub Action runs this every 15 minutes and commits any change
(see .github/workflows/publish-blog.yml). Standard library only.

    python3 scripts/build_blog.py                      # publish everything that is due
    python3 scripts/build_blog.py --all --out /tmp/x   # preview every post in a copy of public/
    python3 scripts/build_blog.py --now 2026-11-01T12:00:00+08:00
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "content" / "blog" / "plan.json"
POSTS = ROOT / "content" / "blog" / "posts"
SOCIAL_ALT = "SetsOfLove. Find someone who gets the early alarm."
NOTE_PILLARS = {"lifts-and-gym-life", "dating-safely", "perth-and-australia"}

m = re.search(r'^CONTACT_EMAIL\s*=\s*"([^"]*)"', (ROOT / "wrangler.toml").read_text(), re.M)
EMAIL = m.group(1).strip() if m else ""


# ---------- markdown (small, strict subset) ----------

def inline(text: str) -> str:
    t = escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda mm: f'<a href="{mm.group(2)}">{mm.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", t)
    return t


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def table(lines: list[str]) -> str:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    head, body = rows[0], [r for r in rows[2:]] if len(rows) > 1 and set("".join(rows[1]).replace(" ", "")) <= set("-:") else rows[1:]
    th = "".join(f'<th scope="col">{inline(c)}</th>' for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def markdown(body: str) -> str:
    out, used = [], set()
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = [ln.rstrip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        first = lines[0]
        if first.startswith("### ") or first.startswith("## "):
            level = 3 if first.startswith("### ") else 2
            text = first[level + 1:].strip()
            hid = base = slugify(text) or "section"
            n = 2
            while hid in used:
                hid, n = f"{base}-{n}", n + 1
            used.add(hid)
            out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
            lines = lines[1:]
            if not lines:
                continue
            first = lines[0]
        if first.startswith("|"):
            out.append(table(lines))
        elif re.match(r"^- ", first) or re.match(r"^\d+\. ", first):
            tag = "ul" if first.startswith("- ") else "ol"
            items: list[str] = []
            for ln in lines:
                if re.match(r"^(- |\d+\. )", ln):
                    items.append(re.sub(r"^(- |\d+\. )", "", ln))
                else:
                    items[-1] += " " + ln.strip()
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
        else:
            out.append(f"<p>{inline(' '.join(ln.strip() for ln in lines))}</p>")
    return "\n".join(out)


def parse_post(slug: str) -> dict:
    path = POSTS / f"{slug}.md"
    if not path.exists():
        raise SystemExit(f"ERROR: {path.relative_to(ROOT)} is missing but the plan says it is due")
    raw = path.read_text()
    mm = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not mm:
        raise SystemExit(f"ERROR: {path.relative_to(ROOT)} has no front matter")
    meta = {}
    for ln in mm.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            v = v.strip()
            if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[k.strip()] = v
    body = mm.group(2).strip()
    words = len(re.findall(r"\b[\w'’-]+\b", re.sub(r"\]\([^)]*\)", "]", body)))
    return {"meta": meta, "body": body, "words": words}


# ---------- page pieces ----------

def fmt_date(dt: datetime) -> str:
    return f"{dt.day} {dt.strftime('%b %Y')}"


def head(title: str, description: str, canonical: str, *, robots: str = "index, follow, max-image-preview:large",
         og_type: str = "website", extra: str = "", jsonld: list | None = None) -> str:
    ld = "".join(
        '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace("<", "\\u003c") + "</script>\n"
        for d in (jsonld or [])
    )
    t, d = escape(title), escape(description)
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="{robots}">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="theme-color" content="#FFF6EC">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="SetsOfLove">
<meta property="og:locale" content="en_AU">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="https://setsoflove.com/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SOCIAL_ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="https://setsoflove.com/twitter-card.png">
<meta name="twitter:image:alt" content="{SOCIAL_ALT}">
{extra}<link rel="alternate" type="application/rss+xml" title="SetsOfLove blog" href="/blog/rss.xml">
<link rel="manifest" href="/site.webmanifest">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/app.css">
{ld}</head>
<body>
"""


HEADER = """<header class="site-header">
  <a href="/" aria-label="SetsOfLove home"><img src="/brand/logo-lockup.png" alt="SetsOfLove" height="32"></a>
  <nav><a href="/blog/">Blog</a><a href="/signin">Sign in</a></nav>
</header>
"""


def footer() -> str:
    contact = f'\n    <li><a href="mailto:{escape(EMAIL)}">{escape(EMAIL)}</a></li>' if EMAIL else ""
    return f"""<footer class="site-footer">
  <ul>
    <li><a href="/blog/">Blog</a></li>
    <li><a href="/terms/">Terms of use</a></li>
    <li><a href="/privacy/">Privacy policy</a></li>
    <li><a href="/contact">Contact</a></li>{contact}
  </ul>
  <p class="small">SetsOfLove is for adults aged 18 and over. We approve every profile before it goes live.</p>
  <p class="small">Another <a href="https://malgordon.com/">Mal Gordon</a> creation</p>
</footer>
</body>
</html>
"""


def breadcrumb_ld(site: str, crumbs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url} for i, (name, url) in enumerate(crumbs, 1)
        ],
    }


def post_item(p: dict, show_desc: bool = True) -> str:
    desc = f'\n      <p class="small muted">{escape(p["description"])}</p>' if show_desc else ""
    return f'    <li>\n      <a class="post-link" href="/blog/{p["slug"]}/">{escape(p["title"])}</a>{desc}\n    </li>'


# ---------- build ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="ISO timestamp to treat as the current time")
    ap.add_argument("--all", action="store_true", help="build every post, ignoring publish_at")
    ap.add_argument("--out", default=str(ROOT / "public"), help="output folder (a copy of public/)")
    args = ap.parse_args()

    out = Path(args.out)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone(timedelta(hours=8)))

    plan = json.loads(PLAN.read_text())
    site = plan["site"].rstrip("/")
    pillars = plan["pillars"]

    published = []
    for p in plan["posts"]:
        when = datetime.fromisoformat(p["publish_at"])
        if args.all or when <= now:
            data = parse_post(p["slug"])
            published.append({**p, **data, "when": when,
                              "title": data["meta"].get("title", p["title"]),
                              "description": data["meta"].get("description", ""),
                              "updated": data["meta"].get("updated", "")})
    published.sort(key=lambda x: x["when"], reverse=True)  # newest first
    by_slug = {p["slug"]: p for p in published}
    order = {p["slug"]: i for i, p in enumerate(plan["posts"])}

    blog = out / "blog"
    if blog.exists():
        shutil.rmtree(blog)
    blog.mkdir(parents=True, exist_ok=True)

    live_pillars = [k for k in pillars if any(p["pillar"] == k for p in published)]

    # --- posts
    for p in published:
        pill = pillars[p["pillar"]]
        url = f"{site}/blog/{p['slug']}/"
        hub = f"{site}/blog/topic/{p['pillar']}/"
        mins = max(1, round(p["words"] / 220))
        iso = p["when"].isoformat()
        modified = p["updated"] or iso
        siblings = [q for q in published if q["pillar"] == p["pillar"] and q["slug"] != p["slug"]]
        siblings.sort(key=lambda q: abs(order[q["slug"]] - order[p["slug"]]))
        others = [q for q in published if q["pillar"] != p["pillar"]]
        others.sort(key=lambda q: abs(order[q["slug"]] - order[p["slug"]]))
        related = siblings[:2] + others[:1]
        for q in (siblings[2:] + others[1:]):
            if len(related) >= 3:
                break
            related.append(q)
        article_ld = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": p["title"],
            "description": p["description"],
            "datePublished": iso,
            "dateModified": modified,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "author": {"@type": "Organization", "name": "SetsOfLove", "url": site + "/"},
            "publisher": {"@type": "Organization", "name": "SetsOfLove", "url": site + "/",
                          "logo": {"@type": "ImageObject", "url": site + "/icon-512.png"}},
            "image": [site + "/og-image.png"],
            "articleSection": pill["title"],
            "inLanguage": "en-AU",
            "wordCount": p["words"],
        }
        crumbs = breadcrumb_ld(site, [("SetsOfLove", site + "/"), ("Blog", site + "/blog/"), (pill["title"], hub), (p["title"], url)])
        extra = (f'<meta property="article:published_time" content="{iso}">\n'
                 f'<meta property="article:modified_time" content="{modified}">\n'
                 f'<meta property="article:section" content="{escape(pill["title"])}">\n')
        note = ('\n  <p class="small muted post-note">This article is general information, not medical, legal or safety advice.</p>'
                if p["pillar"] in NOTE_PILLARS else "")
        rel = "\n".join(post_item(q, False) for q in related)
        html = head(f"{p['title']} – SetsOfLove", p["description"], url, og_type="article", extra=extra, jsonld=[article_ld, crumbs])
        html += HEADER + f"""<main class="page narrow post">
  <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/blog/">Blog</a><span aria-hidden="true">/</span><a href="/blog/topic/{p['pillar']}/">{escape(pill['title'])}</a></nav>
  <article>
    <h1>{escape(p['title'])}</h1>
    <p class="small post-meta"><time datetime="{iso}">{fmt_date(p['when'])}</time> · {mins} min read · By the SetsOfLove team</p>
    <div class="post-body">
{markdown(p['body'])}
    </div>
  </article>{note}
  <section class="card post-cta" aria-labelledby="cta-heading">
    <h2 id="cta-heading" class="h3">Show off the work you put in</h2>
    <p>SetsOfLove is a free profile app for single gym-goers of every gender. Add your gym photos, say who you'd like to meet and share your link. We approve every profile before it goes live.</p>
    <p><a class="btn" href="/signup">Create your profile</a></p>
  </section>
  <section class="stack" aria-labelledby="related-heading">
    <h2 id="related-heading" class="h3">Keep reading</h2>
    <ul class="post-list">
{rel}
    </ul>
    <p><a href="/blog/topic/{p['pillar']}/">More on {escape(pill['title'].lower())}</a></p>
  </section>
</main>
""" + footer()
        d = blog / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html)

    # --- topic hubs
    for key in live_pillars:
        pill = pillars[key]
        mine = [p for p in published if p["pillar"] == key]
        url = f"{site}/blog/topic/{key}/"
        crumbs = breadcrumb_ld(site, [("SetsOfLove", site + "/"), ("Blog", site + "/blog/"), (pill["title"], url)])
        html = head(f"{pill['title']} – SetsOfLove blog", pill["description"], url, jsonld=[crumbs])
        html += HEADER + f"""<main class="page narrow post">
  <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/blog/">Blog</a></nav>
  <h1>{escape(pill['title'])}</h1>
  <p>{escape(pill['intro'])}</p>
  <section class="stack" aria-labelledby="articles-heading">
    <h2 id="articles-heading" class="h3">{len(mine)} {'article' if len(mine) == 1 else 'articles'}</h2>
    <ul class="post-list">
{chr(10).join(post_item(p) for p in mine)}
    </ul>
  </section>
  <p><a href="/blog/">Back to all topics</a></p>
</main>
""" + footer()
        d = blog / "topic" / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html)

    # --- blog index
    url = f"{site}/blog/"
    desc = "Practical, friendly guides for single gym-goers: meeting people respectfully, building a profile, dating around training and staying safe."
    crumbs = breadcrumb_ld(site, [("SetsOfLove", site + "/"), ("Blog", url)])
    robots = "index, follow, max-image-preview:large" if published else "noindex, follow"
    topics = "\n".join(
        f'    <li><a href="/blog/topic/{k}/"><span class="topic-name">{escape(pillars[k]["title"])}</span>'
        f'<span class="topic-desc">{escape(pillars[k]["description"])}</span></a></li>'
        for k in live_pillars
    )
    latest = published[:12]
    if published:
        body = f"""  <section class="stack" aria-labelledby="topics-heading">
    <h2 id="topics-heading">Browse by topic</h2>
    <ul class="topic-list">
{topics}
    </ul>
  </section>
  <section class="stack" aria-labelledby="latest-heading">
    <h2 id="latest-heading">Latest articles</h2>
    <ul class="post-list">
{chr(10).join(post_item(p) for p in latest)}
    </ul>
  </section>
  <p class="small muted">General information only, not medical, legal or safety advice. <a href="/blog/rss.xml">Follow with RSS</a></p>"""
    else:
        first = min((datetime.fromisoformat(p["publish_at"]) for p in plan["posts"]), default=None)
        when = f" on {fmt_date(first)}" if first else " soon"
        body = f'  <p>The first articles arrive{when}.</p>\n  <p><a class="btn btn-secondary" href="/">Go to SetsOfLove</a></p>'
    html = head("Blog – SetsOfLove", desc, url, robots=robots, jsonld=[crumbs])
    html += HEADER + f"""<main class="page narrow post">
  <h1>The SetsOfLove blog</h1>
  <p>{escape(desc)}</p>
{body}
</main>
""" + footer()
    (blog / "index.html").write_text(html)

    # --- RSS
    def rfc(dt: datetime) -> str:
        return format_datetime(dt)

    items = "".join(
        f"""    <item>
      <title>{escape(p['title'])}</title>
      <link>{site}/blog/{p['slug']}/</link>
      <guid isPermaLink="true">{site}/blog/{p['slug']}/</guid>
      <pubDate>{rfc(p['when'])}</pubDate>
      <category>{escape(pillars[p['pillar']]['title'])}</category>
      <description>{escape(p['description'])}</description>
    </item>
""" for p in published[:30])
    last = rfc(published[0]["when"]) if published else rfc(now)
    (blog / "rss.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>SetsOfLove blog</title>
    <link>{site}/blog/</link>
    <description>{escape(desc)}</description>
    <language>en-AU</language>
    <lastBuildDate>{last}</lastBuildDate>
    <atom:link href="{site}/blog/rss.xml" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
""")

    # --- sitemap (lastmod only where it is accurate)
    def day(p): return (p["updated"] or p["when"].isoformat())[:10]
    urls = [(f"{site}/", None)]
    if published:
        urls.append((f"{site}/blog/", day(published[0])))
    for k in live_pillars:
        mine = [p for p in published if p["pillar"] == k]
        urls.append((f"{site}/blog/topic/{k}/", max(day(p) for p in mine)))
    urls += [(f"{site}/blog/{p['slug']}/", day(p)) for p in reversed(published)]
    urls += [(f"{site}/terms/", None), (f"{site}/privacy/", None)]
    xml = "".join(
        f"  <url><loc>{u}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>\n" for u, lm in urls
    )
    (out / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{xml}</urlset>\n'
    )

    # --- homepage "From the blog"
    home = out / "index.html"
    if home.exists():
        text = home.read_text()
        marker = re.compile(r"<!-- blog:latest:start -->.*?<!-- blog:latest:end -->", re.S)
        if marker.search(text):
            if published:
                lis = "\n".join(post_item(p, False) for p in published[:3])
                block = f"""<!-- blog:latest:start -->
  <section class="section stack" aria-labelledby="blog-heading">
    <h2 id="blog-heading">From the blog</h2>
    <ul class="post-list">
{lis}
    </ul>
    <p><a href="/blog/">All articles</a></p>
  </section>
  <!-- blog:latest:end -->"""
            else:
                block = "<!-- blog:latest:start -->\n  <!-- blog:latest:end -->"
            new = marker.sub(lambda _: block, text)
            if new != text:
                home.write_text(new)

    print(f"built {len(published)} of {len(plan['posts'])} posts into {blog}")


if __name__ == "__main__":
    sys.exit(main())
