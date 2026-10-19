import { json, fail, getUser } from "../../lib/util.js";

const MIN_QUERY = 2;
const MAX_QUERY = 40;
const MAX_RESULTS = 24;

// Members search approved profiles by name, link, suburb, city or country. Results are alphabetical.
// There is no ranking and no filtering by gender or who someone would like to meet.
export async function onRequestGet({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to search.", 401);

  const q = (new URL(request.url).searchParams.get("q") || "").replace(/\s+/g, " ").trim().slice(0, MAX_QUERY);
  if (q.length < MIN_QUERY) return fail(`Type at least ${MIN_QUERY} letters to search.`);

  const like = `%${q.toLowerCase().replace(/[\\%_]/g, "\\$&")}%`;
  const rows = await env.DB.prepare(
    `SELECT pr.stub, pr.first_name, pr.age, pr.suburb, pr.city, pr.country,
            (SELECT p.id FROM photos p WHERE p.user_id = pr.user_id ORDER BY p.position, p.created_at LIMIT 1) AS photo
     FROM profiles pr
     WHERE pr.status = 'approved' AND pr.stub IS NOT NULL
       AND (lower(pr.first_name) LIKE ?1 ESCAPE '\\' OR pr.stub LIKE ?1 ESCAPE '\\' OR lower(pr.suburb) LIKE ?1 ESCAPE '\\'
            OR lower(pr.city) LIKE ?1 ESCAPE '\\' OR lower(pr.country) LIKE ?1 ESCAPE '\\')
     ORDER BY lower(pr.first_name), pr.stub
     LIMIT ?2`
  )
    .bind(like, MAX_RESULTS + 1)
    .all();

  const results = rows.results.slice(0, MAX_RESULTS).map((r) => ({
    stub: r.stub,
    first_name: r.first_name,
    age: r.age,
    place: [...new Set([r.suburb, r.city, r.country].map((s) => String(s || "").trim()).filter(Boolean))].join(", "),
    photo: r.photo,
  }));
  return json({ results, more: rows.results.length > MAX_RESULTS });
}
