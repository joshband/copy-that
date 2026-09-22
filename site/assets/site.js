/* Hiring showcase interactions */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function revealAll(selector) {
    document.querySelectorAll(selector).forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  if (reduce || !('IntersectionObserver' in window)) {
    revealAll('[data-reveal]');
    var grid = document.querySelector('.applied-grid');
    if (grid) grid.classList.add('in-view');
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      if (entry.target.classList.contains('applied-grid')) {
        entry.target.classList.add('in-view');
      }
      io.unobserve(entry.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('[data-reveal], .applied-grid').forEach(function (el) {
    io.observe(el);
  });
})();
