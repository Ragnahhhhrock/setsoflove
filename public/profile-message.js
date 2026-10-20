import { api, setMessage, busy } from "/common.js";

// "Send message" on a profile page. The message goes out as an email. Nothing is shown or kept here afterwards.
const form = document.querySelector("[data-message-form]");

if (form) {
  const error = form.querySelector("[data-message-error]");
  const status = form.querySelector("[data-message-status]");
  const button = form.querySelector("button[type=submit]");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(error, "error", "");
    status.textContent = "";
    busy(button, true, "Sending");
    const res = await api("/api/profile-message", { method: "POST", body: { stub: form.dataset.stub, message: form.message.value } });
    if (res.status === 401) {
      location.href = "/signin";
      return;
    }
    busy(button, false, "Sending");
    if (!res.ok) {
      setMessage(error, "error", res.error);
      return;
    }
    form.message.value = "";
    status.textContent = "Sent. They'll get it by email.";
  });
}
