import { json, fail, readJson, getUser, hasProfileColumn, cleanContact, parseContactMethods, CONTACT_KINDS } from "../../lib/util.js";

// Saves how the member would like to be reached (any mix of social accounts, phone and email, or none)
// and whether others may ask for it. This is never public text, so it doesn't take a live profile offline.
// Body: { open: true | false, email_form: true | false (optional), methods: { instagram: "sam_t", email: "sam@example.com", ... } }. Blank means not shared.
export async function onRequestPut({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  if (!(await hasProfileColumn(env, "contact_methods"))) return fail("Contact details aren't switched on yet. Try again soon.", 503);
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");

  const open = body.open === true;
  const given = body.methods && typeof body.methods === "object" && !Array.isArray(body.methods) ? body.methods : {};

  const methods = [];
  for (const kind of CONTACT_KINDS) {
    const typed = typeof given[kind.key] === "string" ? given[kind.key].trim() : "";
    if (!typed) continue;
    const cleaned = cleanContact(kind.key, typed);
    if (cleaned.error) return fail(cleaned.error);
    methods.push({ kind: kind.key, value: cleaned.value });
  }
  if (open && !methods.length) return fail("Add at least one way to reach you before you let people ask.");

  const stored = JSON.stringify(methods);
  const before = await env.DB.prepare("SELECT contact_methods FROM profiles WHERE user_id = ?").bind(user.id).first();
  const changed = JSON.stringify(parseContactMethods(before?.contact_methods)) !== stored;

  const statements = [
    env.DB.prepare("UPDATE profiles SET contact_open = ?, contact_methods = ? WHERE user_id = ?").bind(open ? 1 : 0, stored, user.id),
  ];
  // Optional: let members send a message by email. Only touched when the form sends it.
  if (typeof body.email_form === "boolean") {
    if (!(await hasProfileColumn(env, "email_open"))) return fail("Messages aren't switched on yet. Try again soon.", 503);
    statements.push(env.DB.prepare("UPDATE profiles SET email_open = ? WHERE user_id = ?").bind(body.email_form ? 1 : 0, user.id));
  }
  // Changing the details clears everyone's access, so people ask again for the new ones.
  if (changed) statements.push(env.DB.prepare("DELETE FROM contact_requests WHERE to_user_id = ? AND status = 'approved'").bind(user.id));
  await env.DB.batch(statements);
  return json({ ok: true });
}
