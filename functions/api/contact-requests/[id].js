import { json, fail, readJson, getUser, hasProfileColumn } from "../../../lib/util.js";

// The member who was asked answers a request.
// approve | decline | block work on a waiting request. revoke stops sharing with someone already approved.
// The person who asked is never told about a decline, a block or a revoke.
export async function onRequestPost({ request, env, params }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  if (!(await hasProfileColumn(env, "contact_open"))) return fail("Contact details aren't switched on yet. Try again soon.", 503);
  const body = await readJson(request);
  const action = body?.action;
  if (!["approve", "decline", "block", "revoke"].includes(action)) return fail("Unknown action.");
  if (!/^\d+$/.test(String(params.id))) return fail("We couldn't find that request.", 404);

  const row = await env.DB.prepare("SELECT id, status FROM contact_requests WHERE id = ? AND to_user_id = ?").bind(Number(params.id), user.id).first();
  if (!row) return fail("We couldn't find that request.", 404);

  const wanted = action === "revoke" ? "approved" : "pending";
  if (row.status !== wanted) return fail("That request has already been answered.", 409);

  if (action === "approve") {
    const mine = await env.DB.prepare("SELECT contact_open, contact_value FROM profiles WHERE user_id = ?").bind(user.id).first();
    if (!mine?.contact_open || !mine.contact_value) return fail("Turn on your contact details before you share them.", 409);
  }

  const status = { approve: "approved", decline: "declined", block: "blocked", revoke: "declined" }[action];
  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare("UPDATE contact_requests SET status = ?, decided_at = ? WHERE id = ? AND to_user_id = ?")
    .bind(status, now, row.id, user.id)
    .run();
  return json({ ok: true });
}
