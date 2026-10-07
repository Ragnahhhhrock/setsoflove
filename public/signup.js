import { api, setMessage, busy } from "/common.js";

const form = document.getElementById("form");
const message = document.getElementById("message");
const submit = document.getElementById("submit");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(message, "error", "");
  busy(submit, true, "Creating account");
  const res = await api("/api/signup", {
    method: "POST",
    body: {
      email: form.email.value,
      password: form.password.value,
      code: form.code.value,
      confirm: document.getElementById("confirm").checked,
      accept_terms: document.getElementById("accept_terms").checked,
      consent_public: document.getElementById("consent_public").checked,
    },
  });
  if (res.ok) {
    location.href = "/profile";
    return;
  }
  busy(submit, false, "Creating account");
  setMessage(message, "error", res.error);
});
