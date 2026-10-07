import { json, fail, readJson, cleanText, sha256 } from "../../lib/util.js";

const MAX_PER_HOUR = 5;

export async function onRequestPost({ request, env }) {
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");

  // Hidden field that people never fill in. Pretend it worked so bots move on.
  if (body.website) return json({ ok: true }, 201);

  const name = cleanText(body.name, 80);
  const email = cleanText(body.email, 254).toLowerCase();
  const message = cleanText(body.message, 2000);
  if (!name) return fail("Enter your name.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return fail("Enter a valid email address.");
  if (message.length < 10) return fail("Write a short message so we know how to help.");

  const now = Math.floor(Date.now() / 1000);
  const ipHash = await sha256(request.headers.get("cf-connecting-ip") || "unknown");
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM contact_messages WHERE ip_hash = ? AND created_at > ?")
    .bind(ipHash, now - 3600)
    .first();
  if (recent && recent.n >= MAX_PER_HOUR) return fail("You've sent a few messages already. Try again in an hour.", 429);

  const saved = await env.DB.prepare(
    "INSERT INTO contact_messages (name, email, message, ip_hash, created_at) VALUES (?, ?, ?, ?, ?)"
  )
    .bind(name, email, message, ipHash, now)
    .run();

  // Email it to the contact address. Needs RESEND_API_KEY (see DEPLOY.md). The saved copy is the fallback.
  const to = env.CONTACT_EMAIL;
  if (to && env.RESEND_API_KEY) {
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
        body: JSON.stringify({
          from: `SetsOfLove <${env.CONTACT_FROM || "noreply@setsoflove.com"}>`,
          to: [to],
          reply_to: email,
          subject: `Contact form: ${name.replace(/[\r\n]+/g, " ")}`,
          text: `From: ${name} <${email}>\n\n${message}`,
        }),
      });
      if (res.ok) {
        await env.DB.prepare("UPDATE contact_messages SET emailed = 1 WHERE id = ?").bind(saved.meta.last_row_id).run();
      }
    } catch {}
  }

  return json({ ok: true }, 201);
}
