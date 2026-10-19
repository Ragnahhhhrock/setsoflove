// Shared helpers for SetsOfLove Pages Functions. Not a route (lives outside /functions).

export const SESSION_COOKIE = "sol_session";
const SESSION_SECONDS = 60 * 60 * 24 * 30;
const PBKDF2_ITERATIONS = 100000; // Cloudflare Workers caps PBKDF2 at 100000

export const RESERVED_STUBS = new Set([
  "admin", "login", "signin", "signup", "signout", "logout", "api", "p", "profile",
  "account", "settings", "help", "about", "terms", "privacy", "static", "assets",
  "public", "fonts", "brand", "me", "new", "edit", "support", "contact", "setsoflove", "search", "metrics", "blog", "requests",
]);

// Sample profiles are made-up characters (seed/sample-profiles.json) loaded only into local or staging databases.
// Their accounts use an @sample.invalid email, which can't receive mail. The live site never shows them unless ALLOW_SAMPLES is 1.
export const SAMPLE_EMAIL_PATTERN = "%@sample.invalid";
export const isSampleEmail = (email) => /@sample\.invalid$/i.test(String(email || ""));
export const samplesAllowed = (env) => env.ALLOW_SAMPLES === "1";

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

export const LIMITS = { first_name: 30, suburb: 40, city: 40, country: 40, occupation: 60, training: 200, about: 600, looking_for: 400 };

// ---------- who you are and who you'd like to meet ----------

// Stored as plain keys. `label` is what members see, `phrase` is how it reads in a sentence.
export const GENDERS = [
  { key: "man", label: "Man" },
  { key: "woman", label: "Woman" },
  { key: "non-binary", label: "Non-binary" },
];
export const ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
  .map((label) => ({ key: label.toLowerCase(), label }));
export const INTERESTS = [
  { key: "men", label: "Men" },
  { key: "women", label: "Women" },
  { key: "non-binary", label: "Non-binary people" },
];
export const SEEKING = [
  { key: "dates", label: "Dates" },
  { key: "relationship", label: "A relationship" },
  { key: "marriage", label: "Marriage" },
  { key: "friendship", label: "Friendship" },
  { key: "fun", label: "Just fun" },
];

// Turns whatever the form sent into a comma-separated string of known keys, in the order of `options`.
export function pickKeys(value, options) {
  const list = Array.isArray(value) ? value : typeof value === "string" ? value.split(",") : [];
  const wanted = new Set(list.map((v) => String(v).trim().toLowerCase()));
  return options.filter((o) => wanted.has(o.key)).map((o) => o.key).join(",");
}

export const labelsFor = (csv, options) =>
  String(csv || "").split(",").filter(Boolean).map((k) => options.find((o) => o.key === k)?.label).filter(Boolean);

// ---------- contact details (shared only when the owner says yes) ----------

// The ways a member can choose to be reached. They add any mix, or none. `example` is the placeholder shown in the form.
export const CONTACT_KINDS = [
  { key: "instagram", label: "Instagram", example: "sam_t" },
  { key: "facebook", label: "Facebook", example: "sam.t" },
  { key: "tiktok", label: "TikTok", example: "sam_t" },
  { key: "snapchat", label: "Snapchat", example: "sam_t" },
  { key: "x", label: "X", example: "sam_t" },
  { key: "whatsapp", label: "WhatsApp", example: "+61 400 000 000" },
  { key: "phone", label: "Phone", example: "0400 000 000" },
  { key: "email", label: "Email", example: "sam@example.com" },
];

// A member can ask this many people in 24 hours. It stops anyone working through the whole site.
export const CONTACT_REQUESTS_PER_DAY = 10;

// Social accounts can be entered as a name or as a link to the profile. Only these sites are accepted.
const SOCIAL = {
  instagram: { hosts: ["instagram.com", "www.instagram.com", "instagr.am"], name: /^[A-Za-z0-9._]{1,30}$/ },
  facebook: { hosts: ["facebook.com", "www.facebook.com", "m.facebook.com", "fb.com", "www.fb.com", "fb.me"], name: /^[A-Za-z0-9.]{5,50}$/ },
  tiktok: { hosts: ["tiktok.com", "www.tiktok.com"], name: /^[A-Za-z0-9._]{2,24}$/ },
  snapchat: { hosts: ["snapchat.com", "www.snapchat.com"], name: /^[A-Za-z0-9._-]{3,15}$/ },
  x: { hosts: ["x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"], name: /^[A-Za-z0-9_]{1,15}$/ },
};

// Returns the account name (or "id:123" for a Facebook profile with no name), or null when it isn't a valid account for that site.
function socialName(kind, text) {
  const rule = SOCIAL[kind];
  let candidate = text.trim();
  const lower = candidate.toLowerCase();
  const isLink = /^https?:\/\//i.test(candidate) || /^www\./i.test(candidate) || rule.hosts.some((h) => lower === h || lower.startsWith(`${h}/`));
  if (isLink) {
    let url;
    try {
      url = new URL(/^https?:\/\//i.test(candidate) ? candidate : `https://${candidate}`);
    } catch {
      return null;
    }
    if (!rule.hosts.includes(url.hostname.toLowerCase())) return null;
    const parts = url.pathname.split("/").filter(Boolean);
    if (kind === "facebook" && parts[0] === "profile.php") {
      const id = url.searchParams.get("id") || "";
      return /^\d{5,20}$/.test(id) ? `id:${id}` : null;
    }
    if (kind === "snapchat" && parts[0] === "add") parts.shift();
    candidate = parts[0] || "";
  }
  candidate = candidate.replace(/^@/, "");
  if (kind === "facebook" && /^id:\d{5,20}$/.test(candidate)) return candidate;
  return rule.name.test(candidate) ? candidate : null;
}

// Returns { value } with the entry tidied up, or { error } with what to fix.
export function cleanContact(kind, raw) {
  const text = cleanText(typeof raw === "string" ? raw : "", 254).replace(/\s+/g, " ");
  const option = CONTACT_KINDS.find((k) => k.key === kind);
  if (!option) return { error: "Choose how people should reach you." };
  if (!text) return { error: `Add your ${option.label} details, or leave it blank.` };

  if (SOCIAL[kind]) {
    const name = socialName(kind, text);
    if (!name) return { error: `Enter your ${option.label} name or the link to your ${option.label} profile, like ${option.example}.` };
    return { value: name };
  }
  if (kind === "phone" || kind === "whatsapp") {
    const digits = text.replace(/\D/g, "");
    if (!/^\+?[\d\s().-]{8,20}$/.test(text) || digits.length < 8 || digits.length > 15) {
      return { error: `Enter a ${kind === "phone" ? "phone" : option.label} number with 8 to 15 digits, like ${option.example}.` };
    }
    return { value: text };
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(text)) return { error: "Enter a valid email address." };
  return { value: text.toLowerCase() };
}

// The stored list, as an array of { kind, value } in the order of CONTACT_KINDS. Anything invalid is dropped.
export function parseContactMethods(json) {
  let list;
  try {
    list = JSON.parse(json || "[]");
  } catch {
    return [];
  }
  if (!Array.isArray(list)) return [];
  const byKind = new Map();
  for (const item of list) {
    if (!item || typeof item.kind !== "string" || typeof item.value !== "string") continue;
    const cleaned = cleanContact(item.kind, item.value);
    if (cleaned.value && !byKind.has(item.kind)) byKind.set(item.kind, cleaned.value);
  }
  return CONTACT_KINDS.filter((k) => byKind.has(k.key)).map((k) => ({ kind: k.key, value: byKind.get(k.key) }));
}

// What a member who has been approved sees: a label, the text to show and a safe link (or null).
// Every part comes from a value that passed cleanContact, so the link can't point anywhere unexpected.
export function describeContact(kind, value) {
  const option = CONTACT_KINDS.find((k) => k.key === kind);
  if (!option || !value) return null;
  const out = { kind: option.key, label: option.label, value, href: null };
  const digits = value.replace(/\D/g, "");
  switch (kind) {
    case "instagram":
      out.value = `@${value}`;
      out.href = `https://www.instagram.com/${value}/`;
      break;
    case "tiktok":
      out.value = `@${value}`;
      out.href = `https://www.tiktok.com/@${value}`;
      break;
    case "snapchat":
      out.value = `@${value}`;
      out.href = `https://www.snapchat.com/add/${value}`;
      break;
    case "x":
      out.value = `@${value}`;
      out.href = `https://x.com/${value}`;
      break;
    case "facebook":
      out.value = value.startsWith("id:") ? "Facebook profile" : `facebook.com/${value}`;
      out.href = value.startsWith("id:") ? `https://www.facebook.com/profile.php?id=${value.slice(3)}` : `https://www.facebook.com/${value}`;
      break;
    case "whatsapp":
      out.href = value.startsWith("+") ? `https://wa.me/${digits}` : null;
      break;
    case "phone":
      out.href = `tel:${value.startsWith("+") ? "+" : ""}${digits}`;
      break;
    case "email":
      out.href = `mailto:${value}`;
      break;
  }
  return out;
}

export const describeContacts = (methods) => methods.map((m) => describeContact(m.kind, m.value)).filter(Boolean);

// ---------- lifts ----------

// Lifts are stored in kg (one decimal). `key` is the form field, `column` the database column.
export const LIFTS = [
  { key: "bench", column: "bench_kg", label: "Bench press" },
  { key: "squat", column: "squat_kg", label: "Squat" },
  { key: "deadlift", column: "deadlift_kg", label: "Deadlift" },
  { key: "ohp", column: "ohp_kg", label: "Overhead press" },
];
const KG_PER_LB = 0.45359237;
export const LIFT_MIN_KG = 10;
export const LIFT_MAX_KG = 700;

// Returns kg rounded to 0.1, null when blank, or undefined when the value isn't usable.
export function liftToKg(value, unit) {
  if (value === "" || value == null) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return undefined;
  const kg = Math.round((unit === "lb" ? n * KG_PER_LB : n) * 10) / 10;
  return kg >= LIFT_MIN_KG && kg <= LIFT_MAX_KG ? kg : undefined;
}

export const kgToLb = (kg) => Math.round(kg / KG_PER_LB);
const trim = (n) => String(Math.round(n * 10) / 10);

// "100 kg (220 lb)", with the member's chosen unit first.
export function formatLift(kg, unit) {
  const k = `${trim(kg)} kg`;
  const l = `${kgToLb(kg)} lb`;
  return unit === "lb" ? `${l} (${k})` : `${k} (${l})`;
}

const CONTACT_PATTERNS =[/@/, /https?:|www\./i, /\.(com|net|org|au|io|me)\b/i, /\d[\d\s().-]{6,}\d/];

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
  if (!profile.gender) missing.push("who you are");
  if (!profile.interested_in) missing.push("who you'd like to meet");
  if (!profile.seeking) missing.push("what you're after");
  if (!profile.suburb) missing.push("suburb");
  if (!profile.city) missing.push("city");
  if (!profile.country) missing.push("country");
  if (!profile.about) missing.push("about you");
  if (!profile.looking_for) missing.push("a few words on who you'd like to meet");
  if (!profile.stub) missing.push("your link");
  if (photoCount < 1) missing.push("a photo");
  return missing;
}

// Columns that later migrations add. If the live database hasn't had a migration applied yet,
// the API skips that column instead of failing, so saving still works.
let profileColumns = null;
export async function hasProfileColumn(env, name) {
  // Only a found column is trusted from cache, so a migration applied later is picked up straight away.
  if (!profileColumns?.has(name)) {
    const { results } = await env.DB.prepare("PRAGMA table_info(profiles)").all();
    profileColumns = new Set(results.map((r) => r.name));
  }
  return profileColumns.has(name);
}
