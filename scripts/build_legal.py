#!/usr/bin/env python3
"""Build public/terms/index.html and public/privacy/index.html from content/*.html.

Run after editing content/terms.html or content/privacy.html, then commit the output.
The contact email comes from CONTACT_EMAIL in wrangler.toml (also used in the footer of profile pages).
"""
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
m = re.search(r'^CONTACT_EMAIL\s*=\s*"([^"]*)"', (ROOT / "wrangler.toml").read_text(), re.M)
EMAIL = m.group(1).strip() if m else ""

PAGES = {
    "terms": ("Terms of use", "The terms for using SetsOfLove: who can join, profile rules, sharing, safety and your responsibilities."),
    "privacy": ("Privacy policy", "How SetsOfLove collects, uses, shares and protects your personal information."),
}


def footer() -> str:
    contact = f'<li><a href="mailto:{escape(EMAIL)}">{escape(EMAIL)}</a></li>' if EMAIL else ""
    return f"""<footer class="site-footer">
  <ul>
    <li><a href="/terms/">Terms of use</a></li>
    <li><a href="/privacy/">Privacy policy</a></li>
    <li><a href="/contact">Contact</a></li>
    {contact}
  </ul>
  <p class="small">SetsOfLove is for adults aged 18 and over. We approve every profile before it goes live.</p>
</footer>"""


def toc(fragment: str) -> str:
    items = re.findall(r'<h2 id="([^"]+)">\d+\.\s*(.*?)</h2>', fragment)
    lis = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items)
    return f'<nav class="toc" aria-label="On this page"><p class="label">On this page</p><ol>{lis}</ol></nav>'


for slug, (title, desc) in PAGES.items():
    fragment = (ROOT / "content" / f"{slug}.html").read_text()
    head, sep, rest = fragment.partition("<h2 id=")
    body = f"{head}{toc(fragment)}{sep}{rest}"
    html = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – SetsOfLove</title>
<meta name="description" content="{escape(desc)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/app.css">
</head>
<body>
<header class="site-header"><a href="/" aria-label="SetsOfLove home"><img src="/brand/logo-lockup.svg" alt="SetsOfLove" height="40"></a></header>
<main class="page narrow legal">
{body}
</main>
{footer()}
</body>
</html>
"""
    out = ROOT / "public" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}")

if not EMAIL:
    print("WARNING: CONTACT_EMAIL in wrangler.toml is empty. Add it before launch.")
