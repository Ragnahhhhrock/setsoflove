import { api, setMessage, busy, track } from "/common.js";

const form = document.getElementById("form");
const message = document.getElementById("message");
const submit = document.getElementById("submit");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(message, "error", "");
  busy(submit, true, "Signing in");
  const res = await api("/api/signin", { method: "POST", body: { email: form.email.value, password: form.password.value } });
  if (res.ok) {
    track("login", { method: "email" });
    const me = await api("/api/me");
    location.href = me.ok && me.data.user.isAdmin ? "/admin" : "/profile";
    return;
  }
  busy(submit, false, "Signing in");
  track("login_error", { reason: res.status === 429 ? "locked" : res.status === 0 ? "network" : "invalid" });
  setMessage(message, "error", res.error);
});
