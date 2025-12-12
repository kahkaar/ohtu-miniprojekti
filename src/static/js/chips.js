// Shared chip-based multi-select behavior for tags and categories.
(function () {
  function setupChipInput(opts) {
    const { selectId, containerId, hiddenInputsId, inputName, removeClass } = opts;

    const select = document.getElementById(selectId);
    const container = document.getElementById(containerId);
    const hidden = document.getElementById(hiddenInputsId);

  if (!select || !container || !hidden) return;

    select.addEventListener("change", function () {
      const value = this.value;
      if (!value) return;

      const chip = document.createElement("div");
      chip.className = "chip";
      chip.dataset.value = value;
      chip.innerHTML = `${value} <span class="${removeClass}" data-value="${value}">✕</span>`;
      container.appendChild(chip);

      const input = document.createElement("input");
      input.type = "hidden";
      input.name = inputName;
      input.value = value;
      hidden.appendChild(input);

      const opt = this.querySelector(`option[value="${value}"]`);
      if (opt) opt.remove();
      this.value = "";
    });

    // Delegated click handler: be resilient to clicks on the span/text or the chip wrapper.
    document.addEventListener("click", function (e) {
      // Find nearest element that carries the removeClass
      let el = e.target;
      while (el && el !== document) {
        if (el.classList && el.classList.contains(removeClass)) break;
        el = el.parentNode;
      }
      if (!el || el === document) return;

      const value = el.dataset && el.dataset.value;
      if (!value) return;

      // Remove chip element if present
      const chip = container.querySelector(`.chip[data-value="${value}"]`);
      if (chip) chip.remove();

      // Remove the corresponding hidden input
      const input = hidden.querySelector(`input[value="${value}"]`);
      if (input) input.remove();

      // Restore the option to the select only if it's not already present
      if (!select.querySelector(`option[value="${value}"]`)) {
        const opt = document.createElement("option");
        opt.value = value;
        opt.textContent = value;
        select.appendChild(opt);
      }
    });
  }

  // expose to window for templates to call
  window.setupChipInput = setupChipInput;
})();
