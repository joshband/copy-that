/* Reveal the illustrative "token system unlocks" cards on scroll. */
(function () {
  var grid = document.querySelector('.applied-grid');
  if (!grid) return;
  if (!('IntersectionObserver' in window)) { grid.classList.add('in-view'); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        grid.classList.add('in-view');
        io.disconnect();
      }
    });
  }, { threshold: 0.2 });
  io.observe(grid);
})();