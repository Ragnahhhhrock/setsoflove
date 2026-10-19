import { api, el, setMessage, signOut } from "/common.js";

const message = document.getElementById("message");
document.getElementById("signout").addEventListener("click", signOut);

function head(r) {
  const photo = r.photo
    ? el("img", { src: `/api/photos/${r.photo}`, alt: `Photo of ${r.first_name}`, loading: "lazy", width: "64", height: "80" })
    : el("span", { class: "result-photo-empty", "aria-hidden": "true" });
  return el(
    "div",
    { class: "request-head" },
    photo,
    el("span", { class: "result-text" }, el("strong", {}, `${r.first_name}, ${r.age}`), el("span", { class: "small muted" }, r.place))
  );
}

async function decide(id, action) {
  setMessage(message, "error", "");
  const res = await api(`/api/contact-requests/${id}`, { method: "POST", body: { action } });
  if (!res.ok) setMessage(message, "error", res.error);
  await load();
}

const profileLink = (r) => el("a", { class: "btn btn-secondary btn-small", href: `/${r.stub}` }, "View profile");

function button(label, kind, onclick) {
  return el("button", { class: `btn btn-small ${kind}`, type: "button", onclick }, label);
}

function incomingRow(r) {
  return el(
    "li",
    {},
    el(
      "div",
      { class: "request" },
      head(r),
      el(
        "div",
        { class: "actions" },
        profileLink(r),
        button("Share details", "", () => decide(r.id, "approve")),
        button("Decline", "btn-secondary", () => decide(r.id, "decline")),
        button("Block", "btn-danger", () => {
          if (confirm(`Block ${r.first_name}? They won't be told, and they can't ask again.`)) decide(r.id, "block");
        })
      )
    )
  );
}

function sharingRow(r) {
  return el(
    "li",
    {},
    el(
      "div",
      { class: "request" },
      head(r),
      el(
        "div",
        { class: "actions" },
        profileLink(r),
        button("Stop sharing", "btn-danger", () => {
          if (confirm(`Stop sharing with ${r.first_name}? They won't be told. They keep anything they've already seen.`)) decide(r.id, "revoke");
        })
      )
    )
  );
}

function sharedRow(r) {
  return el(
    "li",
    {},
    el(
      "div",
      { class: "request" },
      head(r),
      el("p", { class: "small muted space-top" }, `${r.first_name} shared their ${r.contact.label}`),
      el("p", { class: "contact-value" }, r.contact.value),
      el("div", { class: "actions" }, profileLink(r))
    )
  );
}

function fill(listId, emptyId, rows, build) {
  const list = document.getElementById(listId);
  list.replaceChildren(...rows.map(build));
  document.getElementById(emptyId).hidden = rows.length > 0;
}

async function load() {
  const res = await api("/api/contact-requests");
  if (res.status === 401) {
    location.href = "/signin";
    return;
  }
  if (!res.ok) {
    setMessage(message, "error", res.error);
    return;
  }
  fill("incoming", "incoming-empty", res.data.incoming, incomingRow);
  fill("sharing", "sharing-empty", res.data.sharing, sharingRow);
  fill("shared", "shared-empty", res.data.shared, sharedRow);
}

load();
