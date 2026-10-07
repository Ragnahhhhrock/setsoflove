import { json, fail, readJson, getUser, cleanText } from "../../../../lib/util.js";

// action: approve | reject | unpublish
export async function onRequestPost({ request, env, params }) {
  const user = await getUser(env, request);
  if (!user?.isAdmin) return fail("Not found.", 404);
  const body = await readJson(request);
  const action = body?.action;
  const note = cleanText(body?.note, 300);

  const profile = await env.DB.prepare("SELECT user_id, status FROM profiles WHERE user_id = ?").bind(params.id).first();
  if (!profile) return fail("We couldn't find that profile.", 404);

  const now = Math.floor(Date.now() / 1000);
  if (action === "approve") {
    await env.DB.prepare("UPDATE profiles SET status = 'approved', admin_note = '', updated_at = ? WHERE user_id = ?").bind(now, profile.user_id).run();
  } else if (action === "reject" || action === "unpublish") {
    if (!note) return fail("Add a short note so the member knows what to change.");
    const status = action === "reject" ? "rejected" : "draft";
    await env.DB.prepare("UPDATE profiles SET status = ?, admin_note = ?, updated_at = ? WHERE user_id = ?").bind(status, note, now, profile.user_id).run();
  } else {
    return fail("Unknown action.");
  }
  return json({ ok: true });
}
