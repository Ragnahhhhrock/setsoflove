// Shared helpers for SetsOfLove Pages Functions. Not a route (lives outside /functions).

export const SESSION_COOKIE = "sol_session";
const SESSION_SECONDS = 60 * 60 * 24 * 30;
const PBKDF2_ITERATIONS = 100000; // Cloudflare Workers caps PBKDF2 at 100000

export const RESERVED_STUBS = new Set([
  "admin", "login", "signin", "signup", "signout", "logout", "api", "p", "profile",
  "account", "settings", "help", "about", "terms", "privacy", "static", "assets",
  "public", "fonts", "brand", "me", "new", "edit", "support", "contact", "setsoflove",
]);

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers },
  });
}

export const fail = (message, status = 400) => json({ error: message }, status);

export async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

const enc = new TextEncoder();
const toHex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
const fromHex = (hex) => new Uint8Array(hex.match(/../g).map((h) => parseInt(h, 16)));

export async function sha256(text) {
  return toHex(await crypto.subtle.digest("SHA-256", enc.encode(text)));
}

export async function hashPassword(password, saltHex) {
  const salt = saltHex ? fromHex(saltHex) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt, iterations: PBKDF2_ITERATIONS },
    key,
    256
  );
  return { hash: toHex(bits), salt: toHex(salt) };
}

export function safeEqual(a, b) {
  const x = enc.encode(String(a));
  const y = enc.encode(String(b));
  let diff = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++) diff |= (x[i] || 0) ^ (y[i] || 0);
  return diff === 0;
}

function cookieFlags(request, maxAge) {
  const secure = new URL(request.url).protocol === "https:" ? "; Secure" : "";
  return `Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure}`;
}

export async function createSession(env, request, userId) {
  const token = toHex(crypto.getRandomValues(new Uint8Array(32)));
  const expires = Math.floor(Date.now() / 1000) + SESSION_SECONDS;
  await env.DB.prepare("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)")
    .bind(await sha256(token), userId, expires)
    .run();
  return `${SESSION_COOKIE}=${token}; ${cookieFlags(request, SESSION_SECONDS)}`;
}

export function clearSessionCookie(request) {
  return `${SESSION_COOKIE}=; ${cookieFlags(request, 0)}`;
}

function getCookie(request, name) {
  const header = request.headers.get("cookie") || "";
  for (const part of header.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

export async function getUser(env, request) {
  const token = getCookie(request, SESSION_COOKIE);
  if (!token || !/^[0-9a-f]{64}$/.test(token)) return null;
  const now = Math.floor(Date.now() / 1000);
  const row = await env.DB.prepare(
    `SELECT u.id, u.email, u.is_admin FROM sessions s JOIN users u ON u.id = s.user_id
     WHERE s.token_hash = ? AND s.expires_at > ?`
  )
    .bind(await sha256(token), now)
    .first();
  return row ? { id: row.id, email: row.email, isAdmin: !!row.is_admin } : null;
}

export async function destroySession(env, request) {
  const token = getCookie(request, SESSION_COOKIE);
  if (token) await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(await sha256(token)).run();
}

// ---------- validation ----------

export const LIMITS = { first_name: 30, suburb: 40, occupation: 60, training: 200, about: 600, looking_for: 400 };

const CONTACT_PATTERNS = [/@/, /https?:|www\./i, /\.(com|net|org|au|io|me)\b/i, /\d[\d\s().-]{6,}\d/];

export function hasContactDetails(text) {
  return CONTACT_PATTERNS.some((re) => re.test(text));
}

export function cleanText(value, max) {
  if (typeof value !== "string") return "";
  return value.replace(/\r\n/g, "\n").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}

export function validStub(stub) {
  return (
    typeof stub === "string" &&
    /^[a-z0-9](?:[a-z0-9-]{1,28})[a-z0-9]$/.test(stub) &&
    !stub.includes("--") &&
    !RESERVED_STUBS.has(stub)
  );
}

export function sniffImageType(bytes) {
  if (bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return "image/jpeg";
  if (bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) return "image/png";
  if (
    bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46 &&
    bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50
  ) return "image/webp";
  return null;
}

export function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export async function loadProfile(env, userId) {
  const profile = await env.DB.prepare("SELECT * FROM profiles WHERE user_id = ?").bind(userId).first();
  const photos = await env.DB.prepare("SELECT id, position FROM photos WHERE user_id = ? ORDER BY position, created_at")
    .bind(userId)
    .all();
  return { profile, photos: photos.results };
}

export function missingForSubmit(profile, photoCount) {
  const missing = [];
  if (!profile.first_name) missing.push("first name");
  if (!profile.age) missing.push("age");
  if (!profile.suburb) missing.push("suburb");
  if (!profile.about) missing.push("about you");
  if (!profile.looking_for) missing.push("what you're looking for");
  if (!profile.stub) missing.push("your link");
  if (photoCount < 1) missing.push("a photo");
  return missing;
}
