// Reveal-on-scroll. Progressive enhancement only — content is fully visible without JS.
(function () {
  var els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        // small stagger for siblings
        var sibs = Array.prototype.slice.call(e.target.parentNode.children);
        var i = Math.max(0, sibs.indexOf(e.target));
        setTimeout(function () { e.target.classList.add('in'); }, Math.min(i * 70, 280));
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (el) { io.observe(el); });
})();
