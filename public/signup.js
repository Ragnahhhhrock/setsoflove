import { api, setMessage, busy, track } from "/common.js";

const form = document.getElementById("form");
const message = document.getElementById("message");
const submit = document.getElementById("submit");

// First time someone touches the form, so we can see how many start versus finish.
form.addEventListener("focusin", () => track("signup_start"), { once: true });

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(message, "error", "");
  busy(submit, true, "Creating account");
  const res = await api("/api/signup", {
    method: "POST",
    body: {
      email: form.email.value,
      password: form.password.value,
      confirm: document.getElementById("confirm").checked,
      accept_terms: document.getElementById("accept_terms").checked,
      consent_public: document.getElementById("consent_public").checked,
    },
  });
  if (res.ok) {
    track("sign_up", { method: "email" });
    location.href = "/profile";
    return;
  }
  busy(submit, false, "Creating account");
  track("signup_error", { reason: res.status === 409 ? "email_taken" : res.status === 0 ? "network" : res.status === 400 ? "validation" : "other" });
  setMessage(message, "error", res.error);
});
