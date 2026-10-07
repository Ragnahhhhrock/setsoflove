import { json, fail, getUser, loadProfile, missingForSubmit } from "../../../lib/util.js";

export async function onRequestPost({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const { profile, photos } = await loadProfile(env, user.id);
  const missing = missingForSubmit(profile, photos.length);
  if (missing.length) {
    const list = missing.length > 1 ? `${missing.slice(0, -1).join(", ")} and ${missing[missing.length - 1]}` : missing[0];
    return fail(`Add ${list} before you send your profile for approval.`);
  }
  if (profile.status === "pending") return json({ ok: true });

  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare("UPDATE profiles SET status = 'pending', admin_note = '', submitted_at = ?, updated_at = ? WHERE user_id = ?")
    .bind(now, now, user.id)
    .run();
  return json({ ok: true });
}
