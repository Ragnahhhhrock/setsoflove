// Homepage social proof: fetch the public totals and count them up once on load.
// The strip stays hidden if the totals can't be fetched or are still too small to be worth showing (see functions/api/stats.js).
import { api } from "/common.js";

const DURATION_MS = 1200;
const section = document.getElementById("proof");
const format = new Intl.NumberFormat("en-AU");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const easeOut = (t) => 1 - Math.pow(1 - t, 3);

async function init() {
  if (!section) return;
  const res = await api("/api/stats");
  if (!res.ok || !res.data.show) return;

  const counters = [];
  for (const item of section.querySelectorAll("[data-stat]")) {
    const value = Number(res.data[item.dataset.stat]) || 0;
    if (value <= 0) {
      item.hidden = true;
      continue;
    }
    // Screen readers get the final figure straight away. The moving number is hidden from them.
    item.querySelector(".visually-hidden").textContent = format.format(value);
    counters.push({ node: item.querySelector(".stat-num"), value });
  }
  if (!counters.length) return;

  for (const { node, value } of counters) node.textContent = reduceMotion ? format.format(value) : "0";
  section.hidden = false;
  if (reduceMotion) return;

  const start = performance.now();
  const tick = (now) => {
    const t = Math.min(1, (now - start) / DURATION_MS);
    for (const { node, value } of counters) node.textContent = format.format(Math.round(value * easeOut(t)));
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

init();
