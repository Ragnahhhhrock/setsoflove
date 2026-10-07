import { json, fail, readJson, getUser, destroySession, clearSessionCookie } from "../../lib/util.js";

// Deletes the member's account, profile and photos.
export async function onRequestDelete({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const body = await readJson(request);
  if (body?.confirm !== true) return fail("Confirm to delete your profile.");

  const photos = await env.DB.prepare("SELECT id FROM photos WHERE user_id = ?").bind(user.id).all();
  for (const p of photos.results) await env.PHOTOS.delete(`photos/${p.id}`);
  await destroySession(env, request);
  await env.DB.batch([
    env.DB.prepare("DELETE FROM photos WHERE user_id = ?").bind(user.id),
    env.DB.prepare("DELETE FROM profiles WHERE user_id = ?").bind(user.id),
    env.DB.prepare("DELETE FROM sessions WHERE user_id = ?").bind(user.id),
    env.DB.prepare("DELETE FROM users WHERE id = ?").bind(user.id),
  ]);
  return json({ ok: true }, 200, { "set-cookie": clearSessionCookie(request) });
}
