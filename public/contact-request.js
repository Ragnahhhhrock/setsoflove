import { api, setMessage, busy } from "/common.js";

// "Request contact" on a profile page. The request is sent once. After that the card only says "Requested".
const root = document.querySelector("[data-contact-root]");
const button = root?.querySelector("[data-contact-request]");

if (button) {
  const message = root.querySelector("[data-contact-message]");
  const status = root.querySelector("[data-contact-status]");
  button.dataset.label = button.textContent;

  button.addEventListener("click", async () => {
    setMessage(message, "error", "");
    busy(button, true, "Requesting");
    const res = await api("/api/contact-requests", { method: "POST", body: { stub: button.dataset.stub } });
    if (res.status === 401) {
      location.href = "/signin";
      return;
    }
    if (!res.ok) {
      busy(button, false, "Requesting");
      setMessage(message, "error", res.error);
      return;
    }
    if (res.data.state === "shared") {
      // Already shared with this member. Reload to show the details.
      location.reload();
      return;
    }
    button.hidden = true;
    status.textContent = `Requested. If ${button.dataset.name} says yes, their contact details will show here.`;
  });
}
