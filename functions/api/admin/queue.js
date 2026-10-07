import { json, fail, getUser } from "../../../lib/util.js";

export async function onRequestGet({ request, env }) {
  const user = await getUser(env, request);
  if (!user?.isAdmin) return fail("Not found.", 404);

  const rows = await env.DB.prepare(
    `SELECT pr.user_id, pr.stub, pr.first_name, pr.age, pr.suburb, pr.occupation, pr.training, pr.about,
            pr.looking_for, pr.status, pr.admin_note, pr.submitted_at, u.email
     FROM profiles pr JOIN users u ON u.id = pr.user_id
     WHERE pr.status IN ('pending','approved','rejected')
     ORDER BY CASE pr.status WHEN 'pending' THEN 0 WHEN 'rejected' THEN 1 ELSE 2 END, pr.submitted_at DESC`
  ).all();
  const photos = await env.DB.prepare("SELECT id, user_id FROM photos ORDER BY position, created_at").all();
  const byUser = {};
  for (const p of photos.results) (byUser[p.user_id] ||= []).push(p.id);
  return json({ profiles: rows.results.map((r) => ({ ...r, photos: byUser[r.user_id] || [] })) });
}
