import { api, el, setMessage, notice, busy, signOut } from "/common.js";

const form = document.getElementById("form");
const statusBox = document.getElementById("status");
const photosBox = document.getElementById("photos");
const photoMessage = document.getElementById("photo-message");
const formMessage = document.getElementById("form-message");
const fileInput = document.getElementById("photo-input");
const addPhoto = document.getElementById("add-photo");
const saveBtn = document.getElementById("save");
const sendBtn = document.getElementById("send");
const FIELDS = ["first_name", "age", "suburb", "occupation", "training", "about", "looking_for", "stub"];
let state = null;

document.getElementById("link-prefix").textContent = `${location.host}/`;
document.getElementById("signout").addEventListener("click", signOut);

async function load() {
  const res = await api("/api/me");
  if (res.status === 401) {
    location.href = "/signin";
    return;
  }
  if (!res.ok) {
    statusBox.replaceChildren(notice("error", res.error));
    return;
  }
  state = res.data;
  if (state.user.isAdmin) document.getElementById("admin-link").hidden = false;
  render();
}

function render() {
  const { profile, photos } = state;
  for (const f of FIELDS) {
    // Don't overwrite what the member is typing.
    if (document.activeElement !== form[f]) form[f].value = profile[f] ?? "";
  }

  statusBox.replaceChildren();
  const link = profile.stub ? `${location.origin}/${profile.stub}` : null;
  if (profile.status === "approved") {
    const box = notice("success", "Your profile is live. Anyone with your link can see it.");
    box.append(el("div", { class: "actions" }));
    statusBox.append(box);
    if (link) statusBox.append(linkRow(link));
    statusBox.append(notice("warning", "Saving changes takes your profile offline until we approve it again."));
  } else if (profile.status === "pending") {
    statusBox.append(notice("warning", "Sent for approval. We'll review it soon, so check back here for the result."));
    if (link) statusBox.append(linkRow(link, "Preview your profile"));
  } else if (profile.status === "rejected") {
    statusBox.append(notice("error", `We need a change before your profile can go live. ${profile.admin_note}`.trim()));
  } else if (profile.admin_note) {
    statusBox.append(notice("warning", `Your profile was taken offline. ${profile.admin_note}`));
  }

  photosBox.replaceChildren(
    ...photos.map((p, i) =>
      el(
        "div",
        { class: "photo-item" },
        el("img", { src: `/api/photos/${p.id}`, alt: `Photo ${i + 1} of your profile` }),
        el(
          "div",
          { class: "photo-actions" },
          i === 0
            ? el("span", { class: "caption tag" }, "Main photo")
            : el("button", { class: "btn-link", type: "button", onclick: () => makeMain(p.id) }, "Make main"),
          el("button", { class: "btn-link", type: "button", onclick: () => removePhoto(p.id) }, "Remove")
        )
      )
    )
  );
  if (!photos.length) photosBox.replaceChildren(el("p", { class: "muted" }, "No photos yet. Add your first one."));
  addPhoto.hidden = photos.length >= 4;
}

function linkRow(link, label = "Copy your link") {
  const row = el("div", { class: "card" }, el("p", { class: "small" }, link));
  const actions = el("div", { class: "actions" });
  actions.append(
    el("a", { class: "btn btn-secondary btn-small", href: new URL(link).pathname }, "View profile"),
    el("button", { class: "btn btn-secondary btn-small", type: "button", onclick: async (e) => {
      try {
        await navigator.clipboard.writeText(link);
        e.target.textContent = "Link copied";
      } catch {
        e.target.textContent = "Copy it from above";
      }
    } }, label === "Copy your link" ? label : "Copy link")
  );
  row.append(actions);
  return row;
}

function formBody() {
  const body = {};
  for (const f of FIELDS) body[f] = form[f].value;
  return body;
}

async function save() {
  setMessage(formMessage, "error", "");
  const res = await api("/api/profile", { method: "PUT", body: formBody() });
  if (!res.ok) setMessage(formMessage, "error", res.error);
  return res.ok;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  busy(saveBtn, true, "Saving");
  const ok = await save();
  busy(saveBtn, false, "Saving");
  if (ok) {
    await load();
    setMessage(formMessage, "success", "Profile saved");
  }
});

sendBtn.addEventListener("click", async () => {
  busy(sendBtn, true, "Sending");
  let ok = await save();
  if (ok) {
    const res = await api("/api/profile/submit", { method: "POST" });
    ok = res.ok;
    if (!ok) setMessage(formMessage, "error", res.error);
  }
  busy(sendBtn, false, "Sending");
  if (ok) {
    await load();
    scrollTo({ top: 0 });
  }
});

// ---- photos ----

addPhoto.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  fileInput.value = "";
  if (!file) return;
  setMessage(photoMessage, "error", "");
  busy(addPhoto, true, "Adding photo");
  try {
    const blob = await cropToPortrait(file);
    const res = await api("/api/photos", { method: "POST", raw: blob });
    if (!res.ok) setMessage(photoMessage, "error", res.error);
    else await load();
  } catch {
    setMessage(photoMessage, "error", "We couldn't read that photo. Try a JPEG or PNG.");
  }
  busy(addPhoto, false, "Adding photo");
});

// Crop to 4:5 portrait (keeping a little extra above centre for faces) and shrink to 1080 x 1350.
async function cropToPortrait(file) {
  const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
  const targetRatio = 4 / 5;
  let sw = bitmap.width;
  let sh = bitmap.height;
  let sx = 0;
  let sy = 0;
  if (sw / sh > targetRatio) {
    const w = Math.round(sh * targetRatio);
    sx = Math.round((sw - w) / 2);
    sw = w;
  } else {
    const h = Math.round(sw / targetRatio);
    sy = Math.round((sh - h) * 0.35);
    sh = h;
  }
  const scale = Math.min(1, 1080 / sw);
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(sw * scale);
  canvas.height = Math.round(sh * scale);
  canvas.getContext("2d").drawImage(bitmap, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject()), "image/jpeg", 0.88));
}

async function removePhoto(id) {
  const res = await api(`/api/photos/${id}`, { method: "DELETE" });
  if (!res.ok) setMessage(photoMessage, "error", res.error);
  else await load();
}

async function makeMain(id) {
  const res = await api(`/api/photos/${id}/main`, { method: "POST" });
  if (!res.ok) setMessage(photoMessage, "error", res.error);
  else await load();
}

document.getElementById("delete").addEventListener("click", async () => {
  if (!confirm("Delete your profile? This can't be undone.")) return;
  const res = await api("/api/account", { method: "DELETE", body: { confirm: true } });
  if (res.ok) location.href = "/";
  else setMessage(formMessage, "error", res.error);
});

load();
