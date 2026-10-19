/* Profile photo gallery: keeps the "1 / N" counter and dots in step with scrolling. No third-party code. */
(function () {
  var root = document.querySelector('[data-gallery-root]');
  if (!root) return;
  var gallery = root.querySelector('.gallery');
  var photos = root.querySelectorAll('.profile-photo');
  var dots = root.querySelectorAll('.gallery-dot');
  var count = root.querySelector('[data-gallery-count]');
  if (!gallery || photos.length < 2) return;

  var current = 0;
  function update() {
    var max = gallery.scrollWidth - gallery.clientWidth;
    var index;
    if (max > 0 && gallery.scrollLeft >= max - 2) {
      index = photos.length - 1;
    } else {
      var step = photos[1].offsetLeft - photos[0].offsetLeft || gallery.clientWidth;
      index = Math.round(gallery.scrollLeft / step);
    }
    index = Math.max(0, Math.min(photos.length - 1, index));
    if (index === current) return;
    current = index;
    for (var i = 0; i < dots.length; i++) dots[i].classList.toggle('is-active', i === index);
    if (count) count.textContent = index + 1 + ' / ' + photos.length;
  }

  var ticking = false;
  gallery.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { ticking = false; update(); });
  }, { passive: true });
})();
