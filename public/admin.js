import { api, el, setMessage, signOut } from "/common.js";

const list = document.getElementById("list");
const message = document.getElementById("message");
document.getElementById("signout").addEventListener("click", signOut);

const LABELS = { pending: "Waiting for approval", approved: "Approved", rejected: "Needs changes" };

async function load() {
  const res = await api("/api/admin/queue");
  if (res.status === 401) {
    location.href = "/signin";
    return;
  }
  if (!res.ok) {
    list.replaceChildren(el("p", {}, "This page is for the admin only."));
    return;
  }
  const profiles = res.data.profiles;
  if (!profiles.length) {
    list.replaceChildren(el("p", { class: "muted" }, "No profiles yet. They'll show up here once members send them for approval."));
    return;
  }
  list.replaceChildren(...profiles.map(card));
}

function card(p) {
  const note = el("textarea", { id: `note-${p.user_id}`, maxlength: "300", "aria-label": `Note for ${p.first_name}` });
  const act = async (action) => {
    setMessage(message, "error", "");
    const res = await api(`/api/admin/profiles/${p.user_id}`, { method: "POST", body: { action, note: note.value } });
    if (!res.ok) {
      setMessage(message, "error", res.error);
      scrollTo({ top: 0 });
    } else await load();
  };

  const facts = el("dl", { class: "facts" });
  const add = (k, v) => v && facts.append(el("dt", {}, k), el("dd", {}, v));
  add("Email", p.email);
  add("Link", p.stub ? `/${p.stub}` : "");
  add("Suburb", p.suburb);
  add("City", p.city);
  add("Country", p.country);
  add("What they do", p.occupation);
  add("How they train", p.training);
  const lifts = [["Bench", p.bench_kg], ["Squat", p.squat_kg], ["Deadlift", p.deadlift_kg], ["Overhead press", p.ohp_kg]]
    .filter(([, kg]) => kg != null)
    .map(([name, kg]) => `${name} ${kg} kg (${Math.round(kg / 0.45359237)} lb)`)
    .join(", ");
  add("Lifts", lifts);
  add("About", p.about);
  add("Looking for", p.looking_for);

  return el(
    "article",
    { class: "card" },
    el("h2", {}, `${p.first_name || "No name"}${p.age ? `, ${p.age}` : ""} `, el("span", { class: `pill pill-${p.status}` }, LABELS[p.status])),
    el("div", { class: "admin-photos" }, p.photos.map((id) => el("img", { src: `/api/photos/${id}`, alt: `Photo of ${p.first_name}` }))),
    facts,
    p.stub ? el("p", {}, el("a", { href: `/${p.stub}` }, "Open profile page")) : "",
    el("div", { class: "field" }, el("label", { for: `note-${p.user_id}` }, "Note to member"), note, el("p", { class: "help" }, "Needed when you ask for changes or take a profile offline")),
    el(
      "div",
      { class: "actions" },
      p.status !== "approved" ? el("button", { class: "btn btn-small", type: "button", onclick: () => act("approve") }, "Approve") : "",
      p.status === "pending" ? el("button", { class: "btn btn-secondary btn-small", type: "button", onclick: () => act("reject") }, "Ask for changes") : "",
      p.status === "approved" ? el("button", { class: "btn btn-danger btn-small", type: "button", onclick: () => act("unpublish") }, "Take offline") : ""
    )
  );
}

load();
