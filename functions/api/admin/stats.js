import { json, fail, getUser, SAMPLE_EMAIL_PATTERN } from "../../../lib/util.js";

const DAY = 60 * 60 * 24;

// Admin-only totals for the top of the approvals page. Counts only, and made-up sample accounts are left out.
export async function onRequestGet({ request, env }) {
  const user = await getUser(env, request);
  if (!user?.isAdmin) return fail("Not found.", 404);

  const now = Math.floor(Date.now() / 1000);
  const week = now - 7 * DAY;
  const day = now - DAY;
  const real = `u.is_admin = 0 AND u.email NOT LIKE '${SAMPLE_EMAIL_PATTERN}'`;
  const one = async (sql, ...binds) => (await env.DB.prepare(sql).bind(...binds).first())?.n || 0;
  // Tables from later migrations may not exist yet on a database that hasn't been migrated. Those counts show as 0.
  const safe = async (fn) => {
    try {
      return await fn();
    } catch {
      return 0;
    }
  };

  try {
    const [members, newWeek, newDay, byStatus, oldest, photos, requestsPending, requestsApproved, emailsWeek, messagesWeek] = await Promise.all([
      one(`SELECT COUNT(*) AS n FROM users u WHERE ${real}`),
      one(`SELECT COUNT(*) AS n FROM users u WHERE ${real} AND u.created_at > ?`, week),
      one(`SELECT COUNT(*) AS n FROM users u WHERE ${real} AND u.created_at > ?`, day),
      env.DB.prepare(
        `SELECT pr.status AS status, COUNT(*) AS n FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE ${real} GROUP BY pr.status`
      ).all(),
      env.DB.prepare(
        `SELECT MIN(pr.submitted_at) AS at FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE ${real} AND pr.status = 'pending'`
      ).first(),
      one(
        `SELECT COUNT(*) AS n FROM photos WHERE user_id IN
           (SELECT pr.user_id FROM profiles pr JOIN users u ON u.id = pr.user_id WHERE ${real} AND pr.status = 'approved')`
      ),
      safe(() => one("SELECT COUNT(*) AS n FROM contact_requests WHERE status = 'pending'")),
      safe(() => one("SELECT COUNT(*) AS n FROM contact_requests WHERE status = 'approved'")),
      safe(() => one("SELECT COUNT(*) AS n FROM profile_emails WHERE created_at > ?", week)),
      safe(() => one("SELECT COUNT(*) AS n FROM contact_messages WHERE created_at > ?", week)),
    ]);

    const status = { draft: 0, pending: 0, approved: 0, rejected: 0 };
    for (const r of byStatus.results) status[r.status] = r.n;

    return json({
      members,
      newMembersWeek: newWeek,
      newMembersDay: newDay,
      profiles: status,
      oldestPendingAt: oldest?.at || null,
      livePhotos: photos,
      contactRequestsPending: requestsPending,
      contactRequestsShared: requestsApproved,
      emailsWeek,
      contactMessagesWeek: messagesWeek,
    });
  } catch (err) {
    console.error("admin stats failed", err);
    return fail("Stats aren't available right now.", 500);
  }
}
