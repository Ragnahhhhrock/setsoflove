import {
  json, fail, readJson, getUser, hasProfileColumn, describeContact, isSampleEmail, samplesAllowed,
  SAMPLE_EMAIL_PATTERN, CONTACT_REQUESTS_PER_DAY,
} from "../../../lib/util.js";

const placeOf = (r) => [...new Set([r.suburb, r.city, r.country].map((s) => String(s || "").trim()).filter(Boolean))].join(", ");

// Someone with a live profile asks to see a member's private contact details.
// A no is never announced: anyone already asked just sees "Requested", whatever the answer was.
export async function onRequestPost({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to ask for contact details.", 401);
  if (!(await hasProfileColumn(env, "contact_open"))) return fail("Contact details aren't switched on yet. Try again soon.", 503);
  const body = await readJson(request);
  const stub = String(body?.stub || "").trim().toLowerCase();

  const mine = await env.DB.prepare("SELECT status FROM profiles WHERE user_id = ?").bind(user.id).first();
  if (mine?.status !== "approved") return fail("Your own profile needs to be live before you can ask. Send it for approval first.", 403);

  const target = await env.DB.prepare(
    `SELECT pr.user_id, pr.status, pr.contact_open, pr.contact_value, u.email
     FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE pr.stub = ?`
  )
    .bind(stub)
    .first();
  const unavailable = !target || target.status !== "approved" || !target.contact_open || !target.contact_value ||
    (isSampleEmail(target.email) && !samplesAllowed(env));
  if (unavailable) return fail("That member isn't sharing contact details right now.", 404);
  if (target.user_id === user.id) return fail("That's your own profile.");

  const existing = await env.DB.prepare("SELECT status FROM contact_requests WHERE from_user_id = ? AND to_user_id = ?")
    .bind(user.id, target.user_id)
    .first();
  if (existing) return json({ ok: true, state: existing.status === "approved" ? "shared" : "requested" });

  const now = Math.floor(Date.now() / 1000);
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM contact_requests WHERE from_user_id = ? AND created_at > ?")
    .bind(user.id, now - 86400)
    .first();
  if (recent && recent.n >= CONTACT_REQUESTS_PER_DAY) return fail("You've asked a lot of people today. Try again tomorrow.", 429);

  await env.DB.prepare("INSERT OR IGNORE INTO contact_requests (from_user_id, to_user_id, status, created_at) VALUES (?, ?, 'pending', ?)")
    .bind(user.id, target.user_id, now)
    .run();
  return json({ ok: true, state: "requested" }, 201);
}

// Everything the signed-in member needs on the requests page.
// incoming: people waiting for an answer. sharing: people they've said yes to. shared: contact details others have shared with them.
export async function onRequestGet({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const empty = { incoming: [], sharing: [], shared: [] };
  if (!(await hasProfileColumn(env, "contact_open"))) return json(empty);

  const allowSamples = samplesAllowed(env) ? 1 : 0;
  const photo = "(SELECT p.id FROM photos p WHERE p.user_id = pr.user_id ORDER BY p.position, p.created_at LIMIT 1) AS photo";
  const columns = `cr.id, cr.status, cr.created_at, cr.decided_at, pr.stub, pr.first_name, pr.age, pr.suburb, pr.city, pr.country, ${photo}`;
  // Only people whose profile is live are listed, so every request can be checked against a profile page.
  const live = `pr.status = 'approved' AND pr.stub IS NOT NULL
       AND (?2 = 1 OR pr.user_id NOT IN (SELECT id FROM users WHERE email LIKE ?3))`;

  const person = (r) => ({ id: r.id, stub: r.stub, first_name: r.first_name, age: r.age, place: placeOf(r), photo: r.photo, at: r.decided_at || r.created_at });

  const incoming = await env.DB.prepare(
    `SELECT ${columns} FROM contact_requests cr JOIN profiles pr ON pr.user_id = cr.from_user_id
     WHERE cr.to_user_id = ?1 AND cr.status = 'pending' AND ${live}
     ORDER BY cr.created_at DESC LIMIT 100`
  )
    .bind(user.id, allowSamples, SAMPLE_EMAIL_PATTERN)
    .all();

  const sharing = await env.DB.prepare(
    `SELECT ${columns} FROM contact_requests cr JOIN profiles pr ON pr.user_id = cr.from_user_id
     WHERE cr.to_user_id = ?1 AND cr.status = 'approved' AND ${live}
     ORDER BY cr.decided_at DESC LIMIT 100`
  )
    .bind(user.id, allowSamples, SAMPLE_EMAIL_PATTERN)
    .all();

  const shared = await env.DB.prepare(
    `SELECT ${columns}, pr.contact_kind, pr.contact_value
     FROM contact_requests cr JOIN profiles pr ON pr.user_id = cr.to_user_id
     WHERE cr.from_user_id = ?1 AND cr.status = 'approved' AND pr.contact_open = 1 AND pr.contact_value != '' AND ${live}
     ORDER BY cr.decided_at DESC LIMIT 100`
  )
    .bind(user.id, allowSamples, SAMPLE_EMAIL_PATTERN)
    .all();

  return json({
    incoming: incoming.results.map(person),
    sharing: sharing.results.map(person),
    shared: shared.results.map((r) => ({ ...person(r), contact: describeContact(r.contact_kind, r.contact_value) })),
  });
}
