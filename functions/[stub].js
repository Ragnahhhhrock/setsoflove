import { getUser, escapeHtml, RESERVED_STUBS, isSampleEmail, samplesAllowed, LIFTS, formatLift, GENDERS, ZODIAC, INTERESTS, SEEKING, labelsFor, describeContact } from "../lib/util.js";

const page = (title, body, { robots = "noindex, nofollow", status = 200, head = "", analyticsPage = "member-profile" } = {}) =>
  new Response(
    `<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="${robots}">
<title>${escapeHtml(title)}</title>
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/app.css">
<meta name="sol-analytics-page" content="${analyticsPage}">
<script src="/analytics.js" defer></script>
${head}</head>
<body>
${body}
</body>
</html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-cache" } }
  );

const header = `<header class="site-header"><a href="/" aria-label="SetsOfLove home"><img src="/brand/logo-lockup.png" alt="SetsOfLove" height="32"></a></header>`;

const footer = (env) => `<footer class="site-footer">
  <ul>
    <li><a href="/blog/">Blog</a></li>
    <li><a href="/terms/">Terms of use</a></li>
    <li><a href="/privacy/">Privacy policy</a></li>
    <li><a href="/contact">Contact</a></li>${env.CONTACT_EMAIL ? `\n    <li><a href="mailto:${escapeHtml(env.CONTACT_EMAIL)}">${escapeHtml(env.CONTACT_EMAIL)}</a></li>` : ""}
  </ul>
  <p class="small">SetsOfLove is for adults aged 18 and over. We approve every profile before it goes live.</p>
  <p class="small">Another <a href="https://malgordon.com/">Mal Gordon</a> creation</p>
</footer>`;

const notFound = (env) =>
  page(
    "Profile not found – SetsOfLove",
    `${header}<main class="page narrow center">
      <h1>We can't find that profile</h1>
      <p>The link may be wrong, or the profile isn't live yet.</p>
      <p><a class="btn btn-secondary" href="/">Go to SetsOfLove</a></p>
    </main>${footer(env)}`,
    { status: 404, analyticsPage: "profile-not-found" }
  );

// "Subiaco, Perth, Australia". Blank parts are skipped and repeats (a suburb named for its city) are dropped.
const place = (profile) => {
  const seen = new Set();
  return [profile.suburb, profile.city, profile.country]
    .map((part) => String(part || "").trim())
    .filter((part) => part && !seen.has(part.toLowerCase()) && seen.add(part.toLowerCase()))
    .join(", ");
};

// "Man. Interested in women. After dates and a relationship."
const list = (items) => (items.length > 1 ? `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}` : items[0] || "");
const whoLine = (profile) => {
  const who = labelsFor(profile.gender, GENDERS)[0];
  const into = labelsFor(profile.interested_in, INTERESTS).map((l) => l.toLowerCase());
  const after = labelsFor(profile.seeking, SEEKING).map((l) => l.toLowerCase());
  const sign = labelsFor(profile.zodiac, ZODIAC)[0];
  return [who, sign ? `${sign} sun sign` : "", into.length ? `interested in ${list(into)}` : "", after.length ? `after ${list(after)}` : ""]
    .filter(Boolean)
    .join(". ");
};

const section = (label, text) =>
  text ? `<section class="profile-section"><h2 class="h3">${escapeHtml(label)}</h2><p>${escapeHtml(text).replace(/\n/g, "<br>")}</p></section>` : "";

const liftsSection = (profile) => {
  const rows = LIFTS.filter((l) => profile[l.column] != null)
    .map((l) => `<div><dt>${escapeHtml(l.label)}</dt><dd>${escapeHtml(formatLift(profile[l.column], profile.weight_unit))}</dd></div>`)
    .join("");
  return rows
    ? `<section class="profile-section"><h2 class="h3">${escapeHtml(profile.first_name)}'s lifts</h2><dl class="lift-stats">${rows}</dl></section>`
    : "";
};

// The "Contact" card. The details themselves only appear for a member the owner has said yes to.
// Returns "" when the owner isn't sharing, or if the contact requests migration hasn't been applied yet.
async function contactCard(env, request, profile) {
  try {
    if (!profile.contact_open || !profile.contact_value) return "";
    const name = escapeHtml(profile.first_name);
    const card = (inner, attrs = "") => `<section class="card" aria-labelledby="contact-h" data-contact-root${attrs}>
    <h2 id="contact-h" class="h3">Contact</h2>
    ${inner}
  </section>`;

    const user = await getUser(env, request);
    if (!user) {
      return card(`<p class="small muted">${name} decides who gets their contact details. Sign in with a live profile to ask.</p>
    <a class="btn btn-secondary" href="/signin">Sign in</a>`);
    }
    if (user.id === profile.user_id) {
      return card(`<p class="small muted">Members with a live profile can ask for your contact details. You decide each request.</p>
    <a class="btn btn-secondary" href="/requests">See requests</a>`);
    }

    const mine = await env.DB.prepare("SELECT status FROM profiles WHERE user_id = ?").bind(user.id).first();
    if (mine?.status !== "approved") {
      return card(`<p class="small muted">Your own profile needs to be live before you can ask ${name} for contact details.</p>
    <a class="btn btn-secondary" href="/profile">Go to your profile</a>`);
    }

    const asked = await env.DB.prepare("SELECT status FROM contact_requests WHERE from_user_id = ? AND to_user_id = ?")
      .bind(user.id, profile.user_id)
      .first();
    if (asked?.status === "approved") {
      const shared = describeContact(profile.contact_kind, profile.contact_value);
      if (shared) {
        return card(`<p class="small muted">${name} shared their ${escapeHtml(shared.label)} with you.</p>
    <p class="contact-value">${escapeHtml(shared.value)}</p>`);
      }
    }
    if (asked) {
      return card(`<p class="small muted" role="status">Requested. If ${name} says yes, their contact details will show here.</p>`);
    }
    return card(
      `<p class="small muted">${name} decides whether to share. You'll only hear back if the answer is yes.</p>
    <button type="button" class="btn btn-secondary" data-contact-request data-stub="${escapeHtml(profile.stub)}" data-name="${name}">Request contact</button>
    <div class="msg" role="alert" hidden data-contact-message></div>
    <p class="small muted" role="status" data-contact-status></p>
    <script type="module" src="/contact-request.js"></script>`
    );
  } catch {
    return "";
  }
}

// Profile pages live at the root: setsoflove.com/sam-t
export async function onRequestGet(context) {
  const { env, params, request } = context;
  const stub = String(params.stub || "").toLowerCase();

  // Not a profile link (static pages like /signin, files like /app.css): let static assets answer.
  if (RESERVED_STUBS.has(stub) || stub.includes(".") || !/^[a-z0-9-]{3,30}$/.test(stub)) return context.next();

  const profile = await env.DB.prepare("SELECT pr.*, u.email AS owner_email FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE pr.stub = ?").bind(stub).first();
  if (!profile) return notFound(env);

  // Sample profiles are made-up characters for local and staging use. They never show on the live site.
  const sample = isSampleEmail(profile.owner_email);
  if (sample && !samplesAllowed(env)) return notFound(env);

  let preview = false;
  if (profile.status !== "approved") {
    const user = await getUser(env, request);
    if (!user || (user.id !== profile.user_id && !user.isAdmin)) return notFound(env);
    preview = true;
  }

  const photos = await env.DB.prepare("SELECT id FROM photos WHERE user_id = ? ORDER BY position, created_at")
    .bind(profile.user_id)
    .all();
  const name = escapeHtml(profile.first_name);
  const gallery = photos.results
    .map((p, i) => `<img class="profile-photo" src="/api/photos/${p.id}" alt="Photo of ${name}" ${i ? 'loading="lazy"' : ""}>`)
    .join("");
  const photoCount = photos.results.length;
  const multi = photoCount > 1;
  const galleryHint = multi
    ? `<p class="gallery-count" aria-hidden="true" data-gallery-count>1 / ${photoCount}</p>
      <div class="gallery-dots" aria-hidden="true">${photos.results.map((_, i) => `<span class="gallery-dot${i ? "" : " is-active"}"></span>`).join("")}</div>
      <script src="/gallery.js" defer></script>`
    : "";

  const origin = new URL(request.url).origin;
  const url = `${origin}/${stub}`;
  const shareText = `Meet ${profile.first_name} on SetsOfLove`;
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(shareText);
  const shareLinks = [
    ["Facebook", `https://www.facebook.com/sharer/sharer.php?u=${u}`, true, "facebook"],
    ["X", `https://twitter.com/intent/tweet?url=${u}&text=${t}`, true, "x"],
    ["WhatsApp", `https://wa.me/?text=${t}%20${u}`, true, "whatsapp"],
    ["Email", `mailto:?subject=${t}&body=${t}%0A%0A${u}`, false, "email"],
  ]
    .map(
      ([label, href, external, method]) =>
        `<li><a class="btn btn-secondary" href="${escapeHtml(href)}"${external ? ' target="_blank" rel="noopener noreferrer"' : ""} aria-label="Share ${label === "Email" ? "by email" : "on " + label}" data-track="share" data-track-method="${method}" data-track-content_type="profile">${label}</a></li>`
    )
    .join("");
  const contact = preview ? "" : await contactCard(env, request, profile);
  const sharing = preview
    ? ""
    : `<section class="card" aria-labelledby="share-h" data-share-root data-url="${escapeHtml(url)}" data-text="${escapeHtml(shareText)}">
    <h2 id="share-h" class="h3 share-title">Share this profile</h2>
    <p class="small muted">Anyone with this link can see ${name}'s profile.</p>
    <ul class="share-list">
      <li hidden><button type="button" class="btn btn-secondary" data-share-native>Share</button></li>
      <li hidden><button type="button" class="btn btn-secondary" data-share-copy>Copy link</button></li>
      ${shareLinks}
    </ul>
    <p class="share-status" role="status" aria-live="polite" data-share-status></p>
  </section>
  <script src="/share.js" defer></script>`;
  const about = String(profile.about || "").replace(/\s+/g, " ").trim();
  const description = about.length > 150 ? about.slice(0, 147).trimEnd() + "..." : about;
  const head = preview
    ? ""
    : `<meta name="description" content="${escapeHtml(description)}">
<link rel="canonical" href="${escapeHtml(url)}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="SetsOfLove">
<meta property="og:title" content="${name}, ${escapeHtml(profile.age)} on SetsOfLove">
<meta property="og:description" content="${escapeHtml(description)}">
<meta property="og:url" content="${escapeHtml(url)}">
<meta property="og:locale" content="en_AU">
<meta property="og:image" content="https://setsoflove.com/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="SetsOfLove. Find someone who gets the early alarm.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${name}, ${escapeHtml(profile.age)} on SetsOfLove">
<meta name="twitter:description" content="${escapeHtml(description)}">
<meta name="twitter:image" content="https://setsoflove.com/twitter-card.png">
<meta name="twitter:image:alt" content="SetsOfLove. Find someone who gets the early alarm.">`;

  const banner =
    (sample ? `<p class="notice notice-warning" role="status">Sample profile. This is a made-up character, not a real member.</p>` : "") +
    (preview ? `<p class="notice notice-warning" role="status">Preview only. This profile isn't live, so only you and the admin can see it.</p>` : "");

  return page(
    `${profile.first_name}, ${profile.age} – SetsOfLove`,
    `${header}
<main class="page narrow">
  ${banner}
  <article class="card profile-card">
    <div class="gallery-wrap${multi ? " gallery-multi" : ""}" data-gallery-root>
      <div class="gallery" tabindex="0" aria-label="Photos of ${name}${multi ? `, ${photoCount} photos, swipe to see more` : ""}">${gallery}</div>
      ${galleryHint}
    </div>
    <div class="profile-body">
      <h1>${name}, ${escapeHtml(profile.age)}</h1>
      <p class="muted">${escapeHtml(place(profile))}</p>
      <p class="small">${escapeHtml(whoLine(profile))}</p>
      ${section(`What ${profile.first_name} does`, profile.occupation)}
      ${section(`How ${profile.first_name} trains`, profile.training)}
      ${liftsSection(profile)}
      ${section(`About ${profile.first_name}`, profile.about)}
      ${section(`Who ${profile.first_name} would like to meet`, profile.looking_for)}
    </div>
  </article>
  ${contact}
  ${sharing}
  <p class="small muted">We approve every profile before it goes live. <a href="${env.CONTACT_EMAIL ? `mailto:${escapeHtml(env.CONTACT_EMAIL)}?subject=${encodeURIComponent("Report profile " + stub)}` : "/terms/#report"}" data-track="report_profile_click">Report this profile</a></p>
  <p><a class="btn btn-secondary" href="/signup" data-track="cta_click" data-track-location="profile_page" data-track-label="create_account">Create your profile</a></p>
</main>
${footer(env)}`,
    { robots: "noindex, nofollow", head }
  );
}
