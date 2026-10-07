/* Share buttons on profile pages. Each button is a plain link; no third-party code is loaded. */
(function () {
  var root = document.querySelector('[data-share-root]');
  if (!root) return;
  var url = root.getAttribute('data-url');
  var text = root.getAttribute('data-text');
  var status = root.querySelector('[data-share-status]');
  function say(msg) { if (status) status.textContent = msg; }

  var copy = root.querySelector('[data-share-copy]');
  if (copy) {
    copy.parentNode.hidden = false;
    copy.addEventListener('click', function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(
          function () { say('Link copied'); },
          function () { say('Copy failed. Select the link and copy it.'); }
        );
      } else {
        say('Copy failed. Select the link and copy it.');
      }
    });
  }

  var native = root.querySelector('[data-share-native]');
  if (native && navigator.share) {
    native.parentNode.hidden = false;
    native.addEventListener('click', function () {
      navigator.share({ title: text, text: text, url: url }).catch(function () {});
    });
  }
})();
