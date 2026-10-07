import { json, fail, readJson, getUser, cleanText, validStub, hasContactDetails, pickKeys, GENDERS, INTERESTS, SEEKING, LIMITS, LIFTS, LIFT_MIN_KG, LIFT_MAX_KG, liftToKg, kgToLb } from "../../lib/util.js";

// Saves the member's profile. Any edit takes a live profile offline until it is approved again.
export async function onRequestPut({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const body = await readJson(request);
  if (!body) return fail("Something was missing. Check the form and try again.");

  const fields = {};
  for (const key of Object.keys(LIMITS)) {
    fields[key] = cleanText(body[key], LIMITS[key]);
    if (key !== "first_name" && key !== "suburb" && hasContactDetails(fields[key])) {
      return fail("Leave out phone numbers, email addresses, links and social handles.");
    }
  }
  if (fields.first_name && !/^[\p{L}][\p{L} '’-]*$/u.test(fields.first_name)) {
    return fail("Use letters only in your first name.");
  }
  for (const place of ["city", "country"]) {
    if (fields[place] && !/^[\p{L}][\p{L} .'’-]*$/u.test(fields[place])) {
      return fail(`Use letters only in your ${place}.`);
    }
  }

  const gender = pickKeys(body.gender, GENDERS).split(",")[0] || "";
  const interestedIn = pickKeys(body.interested_in, INTERESTS);
  const seeking = pickKeys(body.seeking, SEEKING);

  let age = null;
  if (body.age !== "" && body.age != null) {
    age = Number(body.age);
    if (!Number.isInteger(age) || age < 18 || age > 99) return fail("Enter an age between 18 and 99.");
  }

  const unit = body.weight_unit === "lb" ? "lb" : "kg";
  const lifts = {};
  for (const lift of LIFTS) {
    const kg = liftToKg(body[lift.key], unit);
    if (kg === undefined) {
      const range = unit === "lb" ? `${kgToLb(LIFT_MIN_KG)} and ${kgToLb(LIFT_MAX_KG)} lb` : `${LIFT_MIN_KG} and ${LIFT_MAX_KG} kg`;
      return fail(`Enter a ${lift.label.toLowerCase()} between ${range}, or leave it blank.`);
    }
    lifts[lift.column] = kg;
  }

  let stub = null;
  const rawStub = String(body.stub || "").trim().toLowerCase();
  if (rawStub) {
    if (!validStub(rawStub)) {
      return fail("Your link can use lowercase letters, numbers and hyphens, 3 to 30 characters. Try something like sam-t.");
    }
    const taken = await env.DB.prepare("SELECT user_id FROM profiles WHERE stub = ? AND user_id != ?")
      .bind(rawStub, user.id)
      .first();
    if (taken) return fail("Someone already has that link. Try another.", 409);
    stub = rawStub;
  }

  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare(
    `UPDATE profiles SET stub = ?, first_name = ?, gender = ?, interested_in = ?, seeking = ?, age = ?, suburb = ?, city = ?, country = ?, occupation = ?, training = ?,
       about = ?, looking_for = ?, bench_kg = ?, squat_kg = ?, deadlift_kg = ?, ohp_kg = ?, weight_unit = ?,
       status = 'draft', updated_at = ? WHERE user_id = ?`
  )
    .bind(
      stub, fields.first_name, gender, interestedIn, seeking, age, fields.suburb, fields.city, fields.country, fields.occupation, fields.training, fields.about, fields.looking_for,
      lifts.bench_kg, lifts.squat_kg, lifts.deadlift_kg, lifts.ohp_kg, unit, now, user.id
    )
    .run();
  return json({ ok: true });
}
