// Google tag gateway: serves the Google tag and forwards measurement hits through setsoflove.com/metrics,
// so the browser only talks to this site. Only the two Google endpoints below are reachable, so it can't be used as an open proxy.
//   /metrics/gtag.js?id=G-...   ->  https://www.googletagmanager.com/gtag/js?id=G-...
//   /metrics/g/collect          ->  https://www.google-analytics.com/g/collect
// public/analytics.js points the tag here. Don't also switch on Cloudflare's own Google tag gateway for this site.

const ID_PATTERN = /^G-[A-Z0-9]{6,}$/;

export async function onRequest({ request }) {
  const url = new URL(request.url);
  const rest = url.pathname.replace(/^\/metrics\/?/, "");

  let upstream;
  let isScript = false;
  if (rest === "gtag.js" && request.method === "GET") {
    if (!ID_PATTERN.test(url.searchParams.get("id") || "")) return new Response("Not found", { status: 404 });
    upstream = `https://www.googletagmanager.com/gtag/js${url.search}`;
    isScript = true;
  } else if ((rest === "g/collect" || rest === "g/s/collect") && ["GET", "POST"].includes(request.method)) {
    upstream = `https://www.google-analytics.com/${rest}${url.search}`;
  } else {
    return new Response("Not found", { status: 404 });
  }

  // Pass on what Google needs to count the visit properly (device, language, approximate location).
  const headers = new Headers();
  for (const name of ["user-agent", "accept-language", "content-type", "referer"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  const ip = request.headers.get("cf-connecting-ip");
  if (ip) headers.set("x-forwarded-for", ip);

  let res;
  try {
    res = await fetch(upstream, { method: request.method, headers, body: request.method === "POST" ? request.body : undefined });
  } catch {
    return new Response("Bad gateway", { status: 502, headers: { "cache-control": "no-store" } });
  }

  const out = new Headers();
  const type = res.headers.get("content-type");
  if (type) out.set("content-type", type);
  out.set("cache-control", isScript ? "public, max-age=3600" : "no-store");
  return new Response(res.body, { status: res.status, headers: out });
}
