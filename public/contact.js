import { api, setMessage, busy, track } from "/common.js";

const form = document.getElementById("form");
const message = document.getElementById("message");
const submit = document.getElementById("submit");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMessage(message, "error", "");
  busy(submit, true, "Sending");
  const res = await api("/api/contact", {
    method: "POST",
    body: { name: form.name.value, email: form.email.value, message: form.message.value, website: form.website.value },
  });
  busy(submit, false, "Sending");
  if (!res.ok) {
    setMessage(message, "error", res.error);
    return;
  }
  track("contact_submit");
  form.reset();
  setMessage(message, "success", "Message sent. We'll reply by email.");
});
