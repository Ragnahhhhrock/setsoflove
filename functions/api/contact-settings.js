import { json, fail, readJson, getUser, hasProfileColumn, cleanContact, CONTACT_KINDS } from "../../lib/util.js";

// Saves the member's private contact detail and whether others may ask for it.
// This is never public text, so it doesn't take a live profile offline.
export async function onRequestPut({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  if (!(await hasProfileColumn(env, "contact_open"))) return fail("Contact details aren't switched on yet. Try again soon.", 503);
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");

  const open = body.open === true;
  const kind = CONTACT_KINDS.find((k) => k.key === body.kind)?.key || "";
  const typed = typeof body.value === "string" ? body.value.trim() : "";

  let value = "";
  if (kind || typed) {
    const cleaned = cleanContact(kind, body.value);
    if (cleaned.error) return fail(cleaned.error);
    value = cleaned.value;
  }
  if (open && !value) return fail("Add your contact details before you let people ask for them.");

  const before = await env.DB.prepare("SELECT contact_kind, contact_value FROM profiles WHERE user_id = ?").bind(user.id).first();
  const changed = !before || before.contact_kind !== kind || before.contact_value !== value;

  const statements = [
    env.DB.prepare("UPDATE profiles SET contact_open = ?, contact_kind = ?, contact_value = ? WHERE user_id = ?").bind(open ? 1 : 0, kind, value, user.id),
  ];
  // Changing the details clears everyone's access, so people ask again for the new ones.
  if (changed) statements.push(env.DB.prepare("DELETE FROM contact_requests WHERE to_user_id = ? AND status = 'approved'").bind(user.id));
  await env.DB.batch(statements);
  return json({ ok: true });
}
