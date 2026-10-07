import { getUser, escapeHtml } from "../lib/util.js";

const page = (title, body, { robots = "noindex, nofollow", status = 200 } = {}) =>
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
</head>
<body>
${body}
</body>
</html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-cache" } }
  );

const header = `<header class="site-header"><a href="/" aria-label="SetsOfLove home"><img src="/brand/logo-lockup.svg" alt="SetsOfLove" height="40"></a></header>`;

const notFound = () =>
  page(
    "Profile not found – SetsOfLove",
    `${header}<main class="page narrow center">
      <h1>We can't find that profile</h1>
      <p>The link may be wrong, or the profile isn't live yet.</p>
      <p><a class="btn btn-secondary" href="/">Go to SetsOfLove</a></p>
    </main>`,
    { status: 404 }
  );

const section = (label, text) =>
  text ? `<section class="profile-section"><h2 class="h3">${escapeHtml(label)}</h2><p>${escapeHtml(text).replace(/\n/g, "<br>")}</p></section>` : "";

// Profile pages live at the root: setsoflove.com/sam-t
export async function onRequestGet(context) {
  const { env, params, request } = context;
  const stub = String(params.stub || "").toLowerCase();

  // Not a profile link (static pages like /signin, files like /app.css): let static assets answer.
  const reserved = ["admin", "login", "signin", "signup", "signout", "profile", "account", "api", "brand", "fonts"];
  if (reserved.includes(stub) || stub.includes(".") || !/^[a-z0-9-]{3,30}$/.test(stub)) return context.next();

  const profile = await env.DB.prepare("SELECT * FROM profiles WHERE stub = ?").bind(stub).first();
  if (!profile) return notFound();

  let preview = false;
  if (profile.status !== "approved") {
    const user = await getUser(env, request);
    if (!user || (user.id !== profile.user_id && !user.isAdmin)) return notFound();
    preview = true;
  }

  const photos = await env.DB.prepare("SELECT id FROM photos WHERE user_id = ? ORDER BY position, created_at")
    .bind(profile.user_id)
    .all();
  const name = escapeHtml(profile.first_name);
  const gallery = photos.results
    .map((p, i) => `<img class="profile-photo" src="/api/photos/${p.id}" alt="Photo of ${name}" ${i ? 'loading="lazy"' : ""}>`)
    .join("");

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
  <p class="small muted">We approve every profile before it goes live.</p>
  <p><a class="btn btn-secondary" href="/signup">Create your profile</a></p>
</main>`,
    { robots: "noindex, nofollow" }
  );
}
