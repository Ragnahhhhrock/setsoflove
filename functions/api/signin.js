import { json, fail, readJson, hashPassword, safeEqual, createSession } from "../../lib/util.js";

const WINDOW_SECONDS = 15 * 60;
const MAX_FAILURES = 5;
const BAD_LOGIN = "That email or password doesn't match. Check them and try again.";

export async function onRequestPost({ request, env }) {
  const body = await readJson(request);
  const email = String(body?.email || "").trim().toLowerCase();
  const password = String(body?.password || "");
  if (!email || !password) return fail(BAD_LOGIN, 401);

  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare("DELETE FROM login_attempts WHERE at < ?").bind(now - WINDOW_SECONDS).run();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM login_attempts WHERE email = ? AND at >= ?")
    .bind(email, now - WINDOW_SECONDS)
    .first();
  if (recent.n >= MAX_FAILURES) return fail("Too many tries. Wait 15 minutes and try again.", 429);

  const user = await env.DB.prepare("SELECT id, pass_hash, pass_salt FROM users WHERE email = ?").bind(email).first();
  // Hash even for unknown emails so response time doesn't reveal which emails exist.
  const { hash } = await hashPassword(password, user ? user.pass_salt : "00".repeat(16));
  if (!user || !safeEqual(hash, user.pass_hash)) {
    await env.DB.prepare("INSERT INTO login_attempts (email, at) VALUES (?, ?)").bind(email, now).run();
    return fail(BAD_LOGIN, 401);
  }

  await env.DB.prepare("DELETE FROM login_attempts WHERE email = ?").bind(email).run();
  const cookie = await createSession(env, request, user.id);
  return json({ ok: true }, 200, { "set-cookie": cookie });
}
