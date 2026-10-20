import { api, el, setMessage, signOut } from "/common.js";

const list = document.getElementById("list");
const queue = document.getElementById("queue");
const statsBox = document.getElementById("stats");
const message = document.getElementById("message");
document.getElementById("signout").addEventListener("click", signOut);

const LABELS = { pending: "Waiting for approval", approved: "Approved", rejected: "Needs changes" };

function ago(seconds) {
  const mins = Math.max(0, Math.round((Date.now() / 1000 - seconds) / 60));
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 48) return `${hours} hr ago`;
  return `${Math.round(hours / 24)} days ago`;
}

function stat(value, label, alert) {
  return el("div", { class: `stat${alert ? " stat-alert" : ""}` }, el("span", { class: "stat-value" }, value), el("span", { class: "stat-label" }, label));
}

async function loadStats() {
  const res = await api("/api/admin/stats");
  if (!res.ok) {
    statsBox.replaceChildren(el("p", { class: "muted" }, "Stats aren't available right now."));
    return;
  }
  const s = res.data;
  statsBox.replaceChildren(
    stat(s.profiles.pending, "Awaiting approval", s.profiles.pending > 0),
    stat(s.oldestPendingAt ? ago(s.oldestPendingAt) : "None", "Oldest waiting"),
    stat(s.profiles.approved, "Approved profiles"),
    stat(s.profiles.rejected, "Needing changes"),
    stat(s.members, "Members"),
    stat(s.newMembersWeek, "New in 7 days"),
    stat(s.newMembersDay, "New in 24 hours"),
    stat(s.profiles.draft, "Profiles in draft"),
    stat(s.livePhotos, "Photos on live profiles"),
    stat(s.contactRequestsPending, "Contact requests waiting"),
    stat(s.contactRequestsShared, "Contact details shared"),
    stat(s.emailsWeek + s.contactMessagesWeek, "Messages in 7 days")
  );
}

function renderQueue(profiles) {
  const waiting = profiles.filter((p) => p.status === "pending").sort((a, b) => (a.submitted_at || 0) - (b.submitted_at || 0));
  if (!waiting.length) {
    queue.replaceChildren(el("p", { class: "muted" }, "Nothing waiting. New profiles will show up here."));
    return;
  }
  queue.replaceChildren(
    el(
      "ul",
      { class: "queue-list" },
      waiting.map((p) =>
        el(
          "li",
          {},
          el("a", { href: `#profile-${p.user_id}` }, `${p.first_name || "No name"}${p.age ? `, ${p.age}` : ""}`),
          el("span", { class: "muted" }, [p.suburb, p.city].filter(Boolean).join(", ") || "No place yet"),
          el("span", { class: "muted" }, p.submitted_at ? `Sent ${ago(p.submitted_at)}` : "")
        )
      )
    )
  );
}

async function load() {
  loadStats();
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
    queue.replaceChildren(el("p", { class: "muted" }, "Nothing waiting. New profiles will show up here."));
    list.replaceChildren(el("p", { class: "muted" }, "No profiles yet. They'll show up here once members send them for approval."));
    return;
  }
  renderQueue(profiles);
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
  add("Gender", p.gender);
  add("Star sign", p.zodiac);
  add("Interested in", p.interested_in && p.interested_in.split(",").join(", "));
  add("After", p.seeking && p.seeking.split(",").join(", "));
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
  add("Would like to meet", p.looking_for);

  return el(
    "article",
    { class: "card", id: `profile-${p.user_id}` },
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
