import { json, fail, getUser, loadProfile } from "../../lib/util.js";

export async function onRequestGet({ request, env }) {
  const user = await getUser(env, request);
  if (!user) return fail("Sign in to continue.", 401);
  const { profile, photos } = await loadProfile(env, user.id);
  return json({ user: { email: user.email, isAdmin: user.isAdmin }, profile, photos });
}
