// Quick picks for the profile form. Tap to add, tap again to remove. Members can still type anything.
// Suggestions follow STYLE_GUIDE.md: plain, positive, Australian English, no contact details.
import { el } from "/common.js";

// replace: one answer, tapping swaps it in.
// list: short phrases joined with commas.
// sentences: full sentences added to the end of a longer answer.
export const SUGGESTIONS = {
  country: { mode: "replace", items: ["Australia", "New Zealand", "United Kingdom", "Ireland", "United States"] },
  occupation: {
    mode: "replace",
    items: ["Tradie", "FIFO worker", "Office job", "Healthcare", "Teacher", "Engineer", "Hospitality", "Emergency services", "Self-employed", "Student"],
  },
  training: {
    mode: "list",
    items: [
      "Early morning weights",
      "After-work sessions",
      "Powerlifting",
      "Bodybuilding",
      "Functional fitness",
      "Weights and cardio",
      "A weekend run",
      "A Sunday swim",
    ],
  },
  about: {
    mode: "sentences",
    items: [
      "I train most mornings and like a routine.",
      "I'm easygoing and I like a good laugh.",
      "Work keeps me busy, but I always make time for the gym.",
      "I like cooking at home and trying new cafes.",
      "Weekends are for family, mates and the outdoors.",
      "I'm into hiking, the beach and the odd road trip.",
    ],
  },
  looking_for: {
    mode: "sentences",
    items: [
      "Someone kind who enjoys being active.",
      "Someone with a good sense of humour.",
      "Someone who's happy with early starts.",
      "Someone to share weekends, good food and coffee.",
      "Something genuine and relaxed.",
      "Something long term, with someone I can be myself around.",
    ],
  },
};

const norm = (s) => String(s).trim().toLowerCase();
const parts = (value) => value.split(",").map((p) => p.trim()).filter(Boolean);

const isOn = (mode, value, item) => {
  if (mode === "replace") return norm(value) === norm(item);
  if (mode === "list") return parts(value).some((p) => norm(p) === norm(item));
  return value.includes(item);
};

const added = (mode, value, item) => {
  if (mode === "replace") return item;
  if (mode === "list") return [...parts(value), item].join(", ");
  return value.trim() ? `${value.trim()} ${item}` : item;
};

const removed = (mode, value, item) => {
  if (mode === "replace") return "";
  if (mode === "list") return parts(value).filter((p) => norm(p) !== norm(item)).join(", ");
  return value.replace(item, "").replace(/[ \t]{2,}/g, " ").replace(/^[ \t]+|[ \t]+$/gm, "").trim();
};

// Builds one row of chips under a field. Returns a function that refreshes their state.
export function mountChips(container, input, { mode, items }, label) {
  const max = Number(input.maxLength) > 0 ? Number(input.maxLength) : Infinity;
  container.setAttribute("role", "group");
  container.setAttribute("aria-label", `Quick picks for ${label}`);
  const buttons = items.map((item) => {
    const btn = el("button", { class: "chip", type: "button", "aria-pressed": "false" }, item);
    btn.addEventListener("click", () => {
      const next = isOn(mode, input.value, item) ? removed(mode, input.value, item) : added(mode, input.value, item);
      if (next.length > max) return;
      input.value = next;
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    return { btn, item };
  });
  container.replaceChildren(...buttons.map((b) => b.btn));

  const refresh = () => {
    for (const { btn, item } of buttons) {
      const on = isOn(mode, input.value, item);
      btn.setAttribute("aria-pressed", String(on));
      // A chip that would push the answer past its limit is switched off until there's room.
      btn.disabled = !on && added(mode, input.value, item).length > max;
    }
  };
  input.addEventListener("input", refresh);
  refresh();
  return refresh;
}

// ---- link suggestions ----

const slug = (text) =>
  String(text || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

// Same shape the server accepts: 3 to 30 characters, lowercase letters, numbers and single hyphens.
const validStub = (s) => /^[a-z0-9](?:[a-z0-9-]{1,28})[a-z0-9]$/.test(s) && !s.includes("--");

export function stubIdeas({ first_name, age, suburb }) {
  const first = slug(first_name);
  if (!first) return [];
  const ideas = [age ? `${first}-${age}` : "", suburb ? `${first}-${slug(suburb)}` : "", `${first}-gym`];
  return [...new Set(ideas)].filter(validStub);
}

// Chips under the link field, rebuilt from the first name, age and suburb as they're typed.
export function mountStubChips(container, form) {
  container.setAttribute("role", "group");
  container.setAttribute("aria-label", "Quick picks for your link");
  const render = () => {
    const ideas = stubIdeas({ first_name: form.first_name.value, age: form.age.value, suburb: form.suburb.value });
    container.hidden = !ideas.length;
    container.replaceChildren(
      ...ideas.map((idea) => {
        const btn = el("button", { class: "chip", type: "button", "aria-pressed": String(form.stub.value === idea) }, idea);
        btn.addEventListener("click", () => {
          form.stub.value = form.stub.value === idea ? "" : idea;
          form.stub.dispatchEvent(new Event("input", { bubbles: true }));
        });
        return btn;
      })
    );
  };
  for (const name of ["first_name", "age", "suburb", "stub"]) form[name].addEventListener("input", render);
  render();
  return render;
}
