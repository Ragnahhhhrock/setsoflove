import { json, fail, getUser, sniffImageType } from "../../../lib/util.js";

const MAX_BYTES = 5 * 1024 * 1024;
const MAX_PHOTOS = 4;

// Body is the raw image file.
export async function onRequestPost({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);

  const count = await env.DB.prepare("SELECT COUNT(*) AS n FROM photos WHERE user_id = ?").bind(user.id).first();
  if (count.n >= MAX_PHOTOS) return fail(`You can add up to ${MAX_PHOTOS} photos. Remove one first.`);

  const bytes = new Uint8Array(await request.arrayBuffer());
  if (bytes.length === 0) return fail("That file was empty. Choose a photo and try again.");
  if (bytes.length > MAX_BYTES) return fail("That photo is over 5 MB. Choose a smaller one.");
  const type = sniffImageType(bytes);
  if (!type) return fail("Use a JPEG, PNG or WebP photo.");

  const id = crypto.randomUUID();
  await env.PHOTOS.put(`photos/${id}`, bytes, { httpMetadata: { contentType: type } });
  const now = Math.floor(Date.now() / 1000);
  await env.DB.batch([
    env.DB.prepare("INSERT INTO photos (id, user_id, content_type, position, created_at) VALUES (?, ?, ?, ?, ?)")
      .bind(id, user.id, type, count.n, now),
    env.DB.prepare("UPDATE profiles SET status = 'draft', updated_at = ? WHERE user_id = ?").bind(now, user.id),
  ]);
  return json({ ok: true, id }, 201);
}
