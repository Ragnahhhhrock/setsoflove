import { api, el, setMessage, busy, signOut } from "/common.js";

const form = document.getElementById("form");
const input = document.getElementById("q");
const submit = document.getElementById("submit");
const message = document.getElementById("message");
const status = document.getElementById("status");
const results = document.getElementById("results");
document.getElementById("signout").addEventListener("click", signOut);

function row(r) {
  const photo = r.photo
    ? el("img", { src: `/api/photos/${r.photo}`, alt: `Photo of ${r.first_name}`, loading: "lazy", width: "64", height: "80" })
    : el("span", { class: "result-photo-empty", "aria-hidden": "true" });
  return el(
    "li",
    {},
    el(
      "a",
      { class: "result", href: `/${r.stub}` },
      photo,
      el("span", { class: "result-text" }, el("strong", {}, `${r.first_name}, ${r.age}`), el("span", { class: "small muted" }, r.place))
    )
  );
}

async function run(q) {
  setMessage(message, "error", "");
  status.textContent = "";
  results.replaceChildren();
  if (q.trim().length < 2) {
    setMessage(message, "error", "Type at least 2 letters to search.");
    return;
  }
  busy(submit, true, "Searching");
  const res = await api(`/api/search?q=${encodeURIComponent(q)}`);
  busy(submit, false, "Searching");
  if (res.status === 401) {
    location.href = "/signin";
    return;
  }
  if (!res.ok) {
    setMessage(message, "error", res.error);
    return;
  }
  const { results: found, more } = res.data;
  if (!found.length) {
    status.textContent = "No live profiles found. Try a different name, suburb or city.";
    return;
  }
  status.textContent = more
    ? `Showing the first ${found.length} profiles. Add more letters to narrow it down.`
    : `${found.length} ${found.length === 1 ? "profile" : "profiles"} found.`;
  results.replaceChildren(...found.map(row));
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  history.replaceState(null, "", input.value.trim() ? `?q=${encodeURIComponent(input.value.trim())}` : location.pathname);
  run(input.value);
});

const start = new URLSearchParams(location.search).get("q");
(async () => {
  // Searching needs an account, so send signed-out visitors to sign in first.
  const me = await api("/api/me");
  if (me.status === 401) {
    location.href = "/signin";
    return;
  }
  if (start) {
    input.value = start;
    run(start);
  }
})();
