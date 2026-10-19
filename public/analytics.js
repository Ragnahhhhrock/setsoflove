/* Google Analytics 4 for SetsOfLove. Loaded on every page as a plain script (the CSP blocks inline code).
 *
 * The Google tag and its hits go through our own domain (Google tag gateway, see functions/metrics/[[path]].js).
 * Clear GA_MEASUREMENT_ID to turn analytics off.
 *
 * Privacy rules (see content/privacy.html section 12):
 *  - No advertising features: Google signals and ad personalisation are off.
 *  - Nothing is sent when the browser says Do Not Track or Global Privacy Control.
 *  - Event details never include an email, name, stub, gender, who someone wants to meet or what they're after.
 *  - Public profile pages are reported under one shared path, so individual profile links aren't recorded.
 */
(function () {
  var GA_MEASUREMENT_ID = "G-FJKNFMW5NN";

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  var optedOut = navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.globalPrivacyControl === true;
  var enabled = /^G-[A-Z0-9]{6,}$/.test(GA_MEASUREMENT_ID) && !optedOut;

  // Safe to call from anywhere. Does nothing when analytics is off.
  window.solTrack = function (name, params) {
    if (!enabled) return;
    try { gtag("event", name, Object.assign({ transport_type: "beacon" }, params || {})); } catch (e) {}
  };
  if (!enabled) return;

  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "granted",
  });
  gtag("js", new Date());

  var config = {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    // Google tag gateway: send hits to our own domain, which forwards them to Google.
    transport_url: location.origin + "/metrics",
    first_party_collection: true,
  };
  var meta = document.querySelector('meta[name="sol-analytics-page"]');
  if (meta) {
    // A member's public profile. Report it as one page so the link isn't recorded.
    config.page_path = "/" + meta.content;
    config.page_location = location.origin + "/" + meta.content;
    config.page_title = "Member profile";
  }
  gtag("config", GA_MEASUREMENT_ID, config);

  var s = document.createElement("script");
  s.async = true;
  s.src = "/metrics/gtag.js?id=" + encodeURIComponent(GA_MEASUREMENT_ID);
  document.head.appendChild(s);

  // Any element with data-track="event_name" reports a click. Extra details come from data-track-* attributes,
  // for example data-track-location="hero" is sent as { location: "hero" }.
  document.addEventListener("click", function (e) {
    var node = e.target.closest ? e.target.closest("[data-track]") : null;
    if (!node) return;
    var params = {};
    for (var i = 0; i < node.attributes.length; i++) {
      var a = node.attributes[i];
      if (a.name.indexOf("data-track-") === 0) params[a.name.slice(11)] = a.value;
    }
    window.solTrack(node.getAttribute("data-track"), params);
  });
})();
