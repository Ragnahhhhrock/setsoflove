// Shared client helpers. No inline scripts anywhere: the CSP only allows files from this site.

const ICONS = {
  error: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.01"/></svg>',
  success: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/></svg>',
  info: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5v.01"/></svg>',
};

export async function api(path, { method = "GET", body, raw } = {}) {
  const init = { method, credentials: "same-origin", headers: {} };
  if (raw) {
    init.body = raw;
  } else if (body !== undefined) {
    init.headers["content-type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(path, init);
  } catch {
    return { ok: false, status: 0, error: "We couldn't reach SetsOfLove. Check your connection and try again." };
  }
  let data = null;
  try {
    data = await res.json();
  } catch {}
  if (!res.ok) return { ok: false, status: res.status, error: data?.error || "Something went wrong. Try again in a moment." };
  return { ok: true, status: res.status, data };
}

export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === false || v == null) continue;
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return node;
}

// Message with icon + text. kind: error | success
export function setMessage(container, kind, text) {
  container.replaceChildren();
  if (!text) {
    container.hidden = true;
    return;
  }
  container.className = `msg msg-${kind}`;
  container.hidden = false;
  const icon = document.createElement("span");
  icon.innerHTML = ICONS[kind];
  container.append(icon, el("span", {}, text));
}

export function notice(kind, text) {
  const cls = { error: "notice-error", success: "notice-success", warning: "notice-warning", info: "" }[kind];
  const node = el("div", { class: `notice ${cls}`, role: kind === "error" ? "alert" : "status" });
  const icon = document.createElement("span");
  icon.innerHTML = ICONS[kind === "warning" ? "info" : kind];
  node.append(icon, el("p", {}, text));
  return node;
}

export function busy(button, isBusy, label) {
  button.disabled = isBusy;
  if (label) button.textContent = isBusy ? label : button.dataset.label;
}

export async function signOut() {
  await api("/api/signout", { method: "POST" });
  location.href = "/";
}
