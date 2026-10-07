import { json, fail, readJson, hashPassword, safeEqual, createSession } from "../../lib/util.js";
import { TERMS_VERSION } from "../../lib/legal.js";

export async function onRequestPost({ request, env }) {
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");

  if (!env.SIGNUP_CODE) return fail("Sign-ups are closed right now.", 403);
  if (!safeEqual(String(body.code || "").trim().toLowerCase(), env.SIGNUP_CODE.trim().toLowerCase())) {
    return fail("That invite code doesn't match. Check it with whoever invited you.", 403);
  }
  if (body.confirm !== true) return fail("Please confirm you're a gym member looking to meet a woman.");

  if (body.accept_terms !== true) return fail("Tick the box to accept the terms of use and privacy policy.");
  if (body.consent_public !== true) return fail("Tick the box to confirm you understand your profile is visible to anyone with your link.");

  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return fail("Enter a valid email address.");
  if (password.length < 10 || password.length > 200) return fail("Use a password of at least 10 characters.");

  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
  if (existing) return fail("There's already an account with that email. Try signing in.", 409);

  const { hash, salt } = await hashPassword(password);
  const now = Math.floor(Date.now() / 1000);
  const result = await env.DB.prepare(
    "INSERT INTO users (email, pass_hash, pass_salt, created_at, terms_version, terms_accepted_at) VALUES (?, ?, ?, ?, ?, ?)"
  )
    .bind(email, hash, salt, now, TERMS_VERSION, now)
    .run();
  const userId = result.meta.last_row_id;
  await env.DB.prepare("INSERT INTO profiles (user_id, updated_at) VALUES (?, ?)").bind(userId, now).run();

  const cookie = await createSession(env, request, userId);
  return json({ ok: true }, 201, { "set-cookie": cookie });
}
