// Toggle visibility of the advanced filters box and update button text
(function () {
  function initToggleFilters() {
    var btn = document.getElementById("toggleFilters");
    var box = document.getElementById("advancedFilters");
    if (!btn || !box) return;

    btn.addEventListener("click", function () {
      if (box.style.display === "none") {
        box.style.display = "block";
        this.textContent = "▲ Hide filters";
      } else {
        box.style.display = "none";
        this.textContent = "▼ More filters";
      }
    });
  }

  // expose init and auto-run when DOM is ready
  window.initToggleFilters = initToggleFilters;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToggleFilters);
  } else {
    initToggleFilters();
  }
})();
