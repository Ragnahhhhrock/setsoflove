import { getUser, escapeHtml, RESERVED_STUBS } from "../lib/util.js";

const page = (title, body, { robots = "noindex, nofollow", status = 200, head = "" } = {}) =>
  new Response(
    `<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="${robots}">
<title>${escapeHtml(title)}</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/app.css">
${head}</head>
<body>
${body}
</body>
</html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-cache" } }
  );

const header = `<header class="site-header"><a href="/" aria-label="SetsOfLove home"><img src="/brand/logo-lockup.svg" alt="SetsOfLove" height="32"></a></header>`;

const footer = (env) => `<footer class="site-footer">
  <ul>
    <li><a href="/terms/">Terms of use</a></li>
    <li><a href="/privacy/">Privacy policy</a></li>${env.CONTACT_EMAIL ? `\n    <li><a href="mailto:${escapeHtml(env.CONTACT_EMAIL)}">${escapeHtml(env.CONTACT_EMAIL)}</a></li>` : ""}
  </ul>
  <p class="small">SetsOfLove is for adults aged 18 and over. We approve every profile before it goes live.</p>
</footer>`;

const notFound = (env) =>
  page(
    "Profile not found – SetsOfLove",
    `${header}<main class="page narrow center">
      <h1>We can't find that profile</h1>
      <p>The link may be wrong, or the profile isn't live yet.</p>
      <p><a class="btn btn-secondary" href="/">Go to SetsOfLove</a></p>
    </main>${footer(env)}`,
    { status: 404 }
  );

const section = (label, text) =>
  text ? `<section class="profile-section"><h2 class="h3">${escapeHtml(label)}</h2><p>${escapeHtml(text).replace(/\n/g, "<br>")}</p></section>` : "";

// Profile pages live at the root: setsoflove.com/sam-t
export async function onRequestGet(context) {
  const { env, params, request } = context;
  const stub = String(params.stub || "").toLowerCase();

  // Not a profile link (static pages like /signin, files like /app.css): let static assets answer.
  if (RESERVED_STUBS.has(stub) || stub.includes(".") || !/^[a-z0-9-]{3,30}$/.test(stub)) return context.next();

  const profile = await env.DB.prepare("SELECT * FROM profiles WHERE stub = ?").bind(stub).first();
  if (!profile) return notFound(env);

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

  const origin = new URL(request.url).origin;
  const url = `${origin}/${stub}`;
  const shareText = `Meet ${profile.first_name} on SetsOfLove`;
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(shareText);
  const shareLinks = [
    ["Facebook", `https://www.facebook.com/sharer/sharer.php?u=${u}`, true],
    ["X", `https://twitter.com/intent/tweet?url=${u}&text=${t}`, true],
    ["WhatsApp", `https://wa.me/?text=${t}%20${u}`, true],
    ["Email", `mailto:?subject=${t}&body=${t}%0A%0A${u}`, false],
  ]
    .map(
      ([label, href, external]) =>
        `<li><a class="btn btn-secondary" href="${escapeHtml(href)}"${external ? ' target="_blank" rel="noopener noreferrer"' : ""} aria-label="Share ${label === "Email" ? "by email" : "on " + label}">${label}</a></li>`
    )
    .join("");
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
  const firstPhoto = photos.results[0];
  const head = preview
    ? ""
    : `<meta name="description" content="${escapeHtml(description)}">
<link rel="canonical" href="${escapeHtml(url)}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="SetsOfLove">
<meta property="og:title" content="${name}, ${escapeHtml(profile.age)} on SetsOfLove">
<meta property="og:description" content="${escapeHtml(description)}">
<meta property="og:url" content="${escapeHtml(url)}">
<meta name="twitter:card" content="${firstPhoto ? "summary_large_image" : "summary"}">
${firstPhoto ? `<meta property="og:image" content="${origin}/api/photos/${firstPhoto.id}">\n<meta property="og:image:alt" content="Photo of ${name}">\n<meta name="twitter:image" content="${origin}/api/photos/${firstPhoto.id}">\n` : ""}`;

  const banner = preview
    ? `<p class="notice notice-warning" role="status">Preview only. This profile isn't live, so only you and the admin can see it.</p>`
    : "";

  return page(
    `${profile.first_name}, ${profile.age} – SetsOfLove`,
    `${header}
<main class="page narrow">
  ${banner}
  <article class="card profile-card">
    <div class="gallery" tabindex="0" aria-label="Photos of ${name}">${gallery}</div>
    <div class="profile-body">
      <h1>${name}, ${escapeHtml(profile.age)}</h1>
      <p class="muted">${escapeHtml(profile.suburb)}</p>
      ${section(`What ${profile.first_name} does`, profile.occupation)}
      ${section(`How ${profile.first_name} trains`, profile.training)}
      ${section(`About ${profile.first_name}`, profile.about)}
      ${section("Looking for", profile.looking_for)}
    </div>
  </article>
  ${sharing}
  <p class="small muted">We approve every profile before it goes live. <a href="${env.CONTACT_EMAIL ? `mailto:${escapeHtml(env.CONTACT_EMAIL)}?subject=${encodeURIComponent("Report profile " + stub)}` : "/terms/#report"}">Report this profile</a></p>
  <p><a class="btn btn-secondary" href="/signup">Create your profile</a></p>
</main>
${footer(env)}`,
    { robots: "noindex, nofollow", head }
  );
}
