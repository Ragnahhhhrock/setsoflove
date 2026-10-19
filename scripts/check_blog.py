#!/usr/bin/env python3
"""Check every blog post against STYLE_GUIDE.md and content/blog/BRIEF.md.

Exit code 0 only if everything passes. Also called from check_conformance.py.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "content" / "blog" / "plan.json"
POSTS = ROOT / "content" / "blog" / "posts"

BANNED = re.compile(r"\b(hot|babe|hunk|swipe[sd]?|swiping|match(?:es|ed|ing|maker)?|bro|bros|thirst\w*|guys|ladies)\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-↪]")
ALLOWED_EXTERNAL = {
    "https://www.scamwatch.gov.au/", "https://www.cyber.gov.au/", "https://www.esafety.gov.au/",
    "https://www.1800respect.org.au/", "https://www.beyondblue.org.au/", "https://www.healthdirect.gov.au/",
    "https://www.parkrun.com.au/",
}
# Words that signal invented evidence. Posts must not lean on unnamed authorities or fake data.
INVENTED = re.compile(r"\b(studies show|research shows|research suggests|a recent study|according to (?:a|one) (?:study|survey)|experts (?:say|agree)|survey(?:s)? (?:found|show)|\d{1,3}% of (?:people|men|women|members|users))\b", re.I)
BRANDS = re.compile(r"\b(tinder|bumble|grindr|raya|coffee meets bagel|anytime fitness|f45|snap fitness|crossfit|strava|myfitnesspal|instagram|tiktok)\b", re.I)

failures: list[str] = []
passes = 0


def check(ok: bool, msg: str):
    global passes
    if ok:
        passes += 1
    else:
        failures.append(msg)


def parse(path: Path):
    raw = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        return None, raw
    meta = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            v = v.strip()
            if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[k.strip()] = v
    return meta, m.group(2).strip()


def words(body: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", re.sub(r"\]\([^)]*\)", "]", body)))


def run() -> int:
    plan = json.loads(PLAN.read_text())
    slugs = [p["slug"] for p in plan["posts"]]
    pillars = set(plan["pillars"])

    check(len(slugs) == len(set(slugs)), "plan.json: duplicate slugs")
    check(all(p["pillar"] in pillars for p in plan["posts"]), "plan.json: unknown pillar")

    # schedule: one post a day, in order, times vary
    days = [p["publish_at"][:10] for p in plan["posts"]]
    check(len(days) == len(set(days)), "plan.json: two posts share a day")
    check(days == sorted(days), "plan.json: posts are not in date order")
    stamps = [datetime.fromisoformat(p["publish_at"]) for p in plan["posts"]]
    check(all(stamps[i + 1] - stamps[i] > __import__("datetime").timedelta(hours=1) for i in range(len(stamps) - 1)), "plan.json: posts are too close together")

    # files
    on_disk = sorted(p.stem for p in POSTS.glob("*.md"))
    check(set(on_disk) == set(slugs), f"posts folder and plan.json differ: {sorted(set(on_disk) ^ set(slugs))}")

    for p in plan["posts"]:
        slug = p["slug"]
        path = POSTS / f"{slug}.md"
        rel = path.relative_to(ROOT)
        if not path.exists():
            continue
        check(bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug)) and len(slug) <= 80, f"{rel}: slug must be lowercase and hyphenated")
        meta, body = parse(path)
        check(meta is not None, f"{rel}: missing front matter")
        if meta is None:
            continue
        title, desc = meta.get("title", ""), meta.get("description", "")
        check(title == p["title"], f"{rel}: title must equal plan.json ('{p['title']}')")
        check(110 <= len(desc) <= 160, f"{rel}: description must be 110 to 160 characters, is {len(desc)}")
        check(not re.search(r"[!]", desc + title), f"{rel}: no exclamation marks in title or description")

        n = words(body)
        check(700 <= n <= 1300, f"{rel}: {n} words (want 700 to 1,300)")
        check(not body.lstrip().startswith("#"), f"{rel}: starts with a heading; open with the answer")
        check(not re.search(r"^# ", body, re.M), f"{rel}: has an H1 (the title is the H1)")
        h2 = re.findall(r"^## (.+)$", body, re.M)
        check(4 <= len(h2) <= 8, f"{rel}: {len(h2)} sections (want 4 to 8)")
        for h in re.findall(r"^#{2,3} (.+)$", body, re.M):
            letters = re.sub(r"[^A-Za-z ]", "", h)
            words_ = letters.split()
            check(not (len(words_) > 3 and all(w[:1].isupper() for w in words_)), f"{rel}: heading not in sentence case: {h}")

        text = re.sub(r"\]\([^)]*\)", "]", body) + " " + title + " " + desc
        m = BANNED.search(text)
        if m and m.group(0).lower() == "hot" and p["pillar"] == "perth-and-australia":
            m = None  # weather, not people
        check(not m, f"{rel}: banned word '{m and m.group(0)}'")
        check("!" not in text, f"{rel}: contains an exclamation mark")
        check(not EMOJI.search(text), f"{rel}: contains an emoji")
        m = INVENTED.search(text)
        check(not m, f"{rel}: sounds like invented evidence: '{m and m.group(0)}'")
        m = BRANDS.search(text)
        check(not m, f"{rel}: names a brand or competitor: '{m and m.group(0)}'")
        check("<" not in body, f"{rel}: contains HTML")
        check("```" not in body, f"{rel}: contains a code block")
        for mm in re.finditer(r"(?i)sets ?of ?love", body):
            tail = body[mm.end():mm.end() + 4].lower()
            ok = mm.group(0) == "SetsOfLove" or (mm.group(0) == "setsoflove" and tail.startswith((".com", "-")))
            check(ok, f"{rel}: write the product as SetsOfLove, found '{mm.group(0)}'")
        check(not re.search(r"\b(log in|log out|users?)\b", body, re.I), f"{rel}: use 'sign in' and 'member', not 'log in' or 'user'")

        links = re.findall(r"\[([^\]]+)\]\(([^)\s]+)\)", body)
        internal = [u for _, u in links if u.startswith("/")]
        for _, u in links:
            if u.startswith("/blog/"):
                target = u.strip("/").split("/")[1] if u.count("/") >= 2 else ""
                check(u == f"/blog/{target}/" and target in slugs, f"{rel}: bad internal link {u}")
                check(target != slug, f"{rel}: links to itself")
            elif u in ("/signup", "/signin", "/contact", "/terms/", "/privacy/"):
                pass
            elif u.startswith("http"):
                check(u in ALLOWED_EXTERNAL, f"{rel}: external link not on the allowed list: {u}")
            else:
                check(False, f"{rel}: unexpected link {u}")
        check(2 <= len([u for u in internal if u.startswith('/blog/')]) <= 6, f"{rel}: want 2 to 6 internal links to other posts")
        check(all(t.lower() not in ("here", "click here", "link", "this") for t, _ in links), f"{rel}: vague link text")

        # keyword in the opening paragraph, and the opening paragraph is short enough to quote
        first = re.split(r"\n\s*\n", body, maxsplit=1)[0]
        check(len(first.split()) <= 70, f"{rel}: opening paragraph is {len(first.split())} words (keep under 70)")

    # built output (only what is published) must match the source
    for page in sorted((ROOT / "public" / "blog").glob("*/index.html")):
        slug = page.parent.name
        if slug == "topic":
            continue
        check(slug in slugs, f"{page.relative_to(ROOT)}: no matching post in plan.json")
        html = page.read_text()
        check('rel="canonical" href="https://setsoflove.com/blog/' + slug + '/"' in html, f"{page.relative_to(ROOT)}: canonical link wrong")
        check('href="/terms/"' in html and 'href="/privacy/"' in html, f"{page.relative_to(ROOT)}: footer must link to terms and privacy")
        check("style=" not in html, f"{page.relative_to(ROOT)}: no inline styles")
        check("<h1>" in html and html.count("<h1>") == 1, f"{page.relative_to(ROOT)}: needs exactly one h1")

    return 0


def main():
    run()
    print(f"blog: {passes} checks passed, {len(failures)} failed")
    for f in failures:
        print("FAIL:", f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
