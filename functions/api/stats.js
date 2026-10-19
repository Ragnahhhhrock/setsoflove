import { json, fail, SAMPLE_EMAIL_PATTERN } from "../../lib/util.js";

// Made-up sample accounts never count towards the public totals.
const REAL = `user_id NOT IN (SELECT id FROM users WHERE email LIKE '${SAMPLE_EMAIL_PATTERN}')`;

// Public, anonymous totals for the homepage social-proof strip. Counts only: nothing about any one member.
// The homepage hides the strip until sign-ups reach STATS_MIN_SIGNUPS (wrangler.toml), so a brand-new site never shows tiny numbers.
export async function onRequestGet({ env }) {
  try {
    const [users, live, photos, lifts] = await Promise.all([
      env.DB.prepare(`SELECT COUNT(*) AS n FROM users WHERE is_admin = 0 AND email NOT LIKE '${SAMPLE_EMAIL_PATTERN}'`).first(),
      env.DB.prepare(`SELECT COUNT(*) AS n FROM profiles WHERE status = 'approved' AND ${REAL}`).first(),
      env.DB.prepare(
        `SELECT COUNT(*) AS n FROM photos WHERE user_id IN (SELECT user_id FROM profiles WHERE status = 'approved' AND ${REAL})`
      ).first(),
      env.DB.prepare(
        `SELECT COALESCE(SUM(COALESCE(bench_kg, 0) + COALESCE(squat_kg, 0) + COALESCE(deadlift_kg, 0) + COALESCE(ohp_kg, 0)), 0) AS kg
         FROM profiles WHERE status = 'approved' AND ${REAL}`
      ).first(),
    ]);

    const signups = users?.n || 0;
    const min = Number.parseInt(env.STATS_MIN_SIGNUPS, 10);
    const threshold = Number.isFinite(min) && min >= 0 ? min : 10;

    return json(
      {
        show: signups >= threshold,
        signups,
        profiles: live?.n || 0,
        photos: photos?.n || 0,
        kg: Math.round(lifts?.kg || 0),
      },
      200,
      { "cache-control": "public, max-age=300, s-maxage=300" }
    );
  } catch (err) {
    console.error("stats failed", err);
    return fail("Stats aren't available right now.", 500);
  }
}
