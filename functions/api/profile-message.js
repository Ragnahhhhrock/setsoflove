import { json, fail, readJson, getUser, hasProfileColumn, cleanText, isSampleEmail, samplesAllowed } from "../../lib/util.js";

const PER_PAIR_PER_DAY = 3;
const PER_SENDER_PER_DAY = 10;

// A signed-in member with a live profile sends a short message to another member's account email.
// The sender never sees the address. The email carries no reply-to, only a link back to the sender's profile.
// Nothing about the message is stored except that it was sent.
export async function onRequestPost({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to send a message.", 401);
  if (!(await hasProfileColumn(env, "email_open"))) return fail("Messages aren't switched on yet. Try again soon.", 503);
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");
  const stub = String(body.stub || "").trim().toLowerCase();
  const message = cleanText(body.message, 1000);
  if (message.length < 10) return fail("Write a short message, at least a sentence.");

  const mine = await env.DB.prepare("SELECT status, first_name, stub FROM profiles WHERE user_id = ?").bind(user.id).first();
  if (mine?.status !== "approved") return fail("Your own profile needs to be live before you can send a message.", 403);

  const target = await env.DB.prepare(
    `SELECT pr.user_id, pr.status, pr.first_name, pr.email_open, u.email
     FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE pr.stub = ?`
  )
    .bind(stub)
    .first();
  if (!target || target.status !== "approved" || !target.email_open || (isSampleEmail(target.email) && !samplesAllowed(env))) {
    return fail("That member isn't taking messages right now.", 404);
  }
  if (target.user_id === user.id) return fail("That's your own profile.");

  if (!env.RESEND_API_KEY) return fail("Messages can't be sent right now. Try again later.", 503);

  // A member who blocked you from a contact request gets nothing, and you aren't told.
  try {
    const blocked = await env.DB.prepare("SELECT 1 AS x FROM contact_requests WHERE from_user_id = ? AND to_user_id = ? AND status = 'blocked'")
      .bind(user.id, target.user_id)
      .first();
    if (blocked) return json({ ok: true });
  } catch {}

  const now = Math.floor(Date.now() / 1000);
  const pair = await env.DB.prepare("SELECT COUNT(*) AS n FROM profile_emails WHERE from_user_id = ? AND to_user_id = ? AND created_at > ?")
    .bind(user.id, target.user_id, now - 86400)
    .first();
  if (pair && pair.n >= PER_PAIR_PER_DAY) return fail(`You've already written to ${target.first_name} a few times today. Try again tomorrow.`, 429);
  const sender = await env.DB.prepare("SELECT COUNT(*) AS n FROM profile_emails WHERE from_user_id = ? AND created_at > ?")
    .bind(user.id, now - 86400)
    .first();
  if (sender && sender.n >= PER_SENDER_PER_DAY) return fail("You've sent a lot of messages today. Try again tomorrow.", 429);

  // Reserve the slot first so two quick sends can't both slip under the limit.
  const saved = await env.DB.prepare("INSERT INTO profile_emails (from_user_id, to_user_id, created_at) VALUES (?, ?, ?)")
    .bind(user.id, target.user_id, now)
    .run();

  const origin = new URL(request.url).origin;
  const link = `${origin}/${mine.stub}`;
  let sent = false;
  try {
    const res = await fetch(env.RESEND_API_URL || "https://api.resend.com/emails", {
      method: "POST",
      headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
      body: JSON.stringify({
        from: `SetsOfLove <${env.CONTACT_FROM || "noreply@setsoflove.com"}>`,
        to: [target.email],
        subject: `A message from ${mine.first_name.replace(/[\r\n]+/g, " ")} on SetsOfLove`,
        text:
          `${mine.first_name} sent you a message through your SetsOfLove profile.\n\n` +
          `${message}\n\n` +
          `----\n` +
          `Their profile: ${link}\n` +
          `To reply, open their profile and send a message back. You'll need your own profile to be live.\n\n` +
          `Your email address wasn't shared with ${mine.first_name}. Please don't reply to this email. ` +
          `To stop getting messages, turn them off under "Contact details" on your profile. To report this message, use "Report this profile" on their page.`,
      }),
    });
    sent = res.ok;
  } catch {}

  if (!sent) {
    await env.DB.prepare("DELETE FROM profile_emails WHERE id = ?").bind(saved.meta.last_row_id).run();
    return fail("That message couldn't be sent. Try again in a few minutes.", 502);
  }
  return json({ ok: true }, 201);
}
