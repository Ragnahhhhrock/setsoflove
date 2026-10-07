import { json, fail, getUser } from "../../../../lib/util.js";

export async function onRequestPost({ request, env, params }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const rows = await env.DB.prepare("SELECT id FROM photos WHERE user_id = ? ORDER BY position, created_at").bind(user.id).all();
  const ids = rows.results.map((r) => r.id);
  if (!ids.includes(params.id)) return fail("We couldn't find that photo.", 404);

  const ordered = [params.id, ...ids.filter((id) => id !== params.id)];
  const now = Math.floor(Date.now() / 1000);
  await env.DB.batch([
    ...ordered.map((id, i) => env.DB.prepare("UPDATE photos SET position = ? WHERE id = ?").bind(i, id)),
    env.DB.prepare("UPDATE profiles SET status = 'draft', updated_at = ? WHERE user_id = ?").bind(now, user.id),
  ]);
  return json({ ok: true });
}
