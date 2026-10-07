import { json, fail, getUser } from "../../../lib/util.js";

// Public only while the owner's profile is approved. Owners and admins can always see them.
export async function onRequestGet({ request, env, params }) {
  const photo = await env.DB.prepare(
    `SELECT p.id, p.user_id, p.content_type, pr.status FROM photos p
     JOIN profiles pr ON pr.user_id = p.user_id WHERE p.id = ?`
  )
    .bind(params.id)
    .first();
  if (!photo) return new Response("Not found", { status: 404 });

  let cache = "public, max-age=600";
  if (photo.status !== "approved") {
    const user = await getUser(env, request);
    if (!user || (user.id !== photo.user_id && !user.isAdmin)) return new Response("Not found", { status: 404 });
    cache = "private, no-store";
  }

  const object = await env.PHOTOS.get(`photos/${photo.id}`);
  if (!object) return new Response("Not found", { status: 404 });
  return new Response(object.body, {
    headers: { "content-type": photo.content_type, "cache-control": cache, "x-robots-tag": "noindex" },
  });
}

export async function onRequestDelete({ request, env, params }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const photo = await env.DB.prepare("SELECT id FROM photos WHERE id = ? AND user_id = ?").bind(params.id, user.id).first();
  if (!photo) return fail("We couldn't find that photo.", 404);

  await env.PHOTOS.delete(`photos/${photo.id}`);
  const now = Math.floor(Date.now() / 1000);
  await env.DB.batch([
    env.DB.prepare("DELETE FROM photos WHERE id = ?").bind(photo.id),
    env.DB.prepare("UPDATE profiles SET status = 'draft', updated_at = ? WHERE user_id = ?").bind(now, user.id),
  ]);
  // Close the gap in the ordering.
  const rest = await env.DB.prepare("SELECT id FROM photos WHERE user_id = ? ORDER BY position, created_at").bind(user.id).all();
  await env.DB.batch(rest.results.map((p, i) => env.DB.prepare("UPDATE photos SET position = ? WHERE id = ?").bind(i, p.id)));
  return json({ ok: true });
}
