// Shared logic for managing extra field rows (clone template, bind select/input, remove)
(function () {
  function _updateDisabledOptions(container) {
    var selects = container.querySelectorAll('.extra-select');
    var chosen = {};
    selects.forEach(function (s) {
      if (s.value) chosen[s.value] = true;
    });

    selects.forEach(function (s) {
      var options = s.options;
      for (var i = 0; i < options.length; i++) {
        var opt = options[i];
        if (opt.value === '') { opt.disabled = false; continue; }
        if (s.value === opt.value) { opt.disabled = false; continue; }
        opt.disabled = !!chosen[opt.value];
      }
    });
  }

  function _bindRow(row, container) {
    var select = row.querySelector('.extra-select');
    var input = row.querySelector('.extra-input');
    var remove = row.querySelector('.remove-extra');

    function onChange() {
      var field = select.value || '';
      input.name = field || 'additional_field_value';
      _updateDisabledOptions(container);
    }

    select.addEventListener('change', onChange);
    remove.addEventListener('click', function (e) {
      e.preventDefault();
      row.remove();
      _updateDisabledOptions(container);
    });
  }

  function initExtraFields(opts) {
    opts = opts || {};
    var container = document.getElementById(opts.containerId || 'extra_fields_container');
    var tpl = document.getElementById(opts.tplId || 'extra_row_template');
    var addBtn = document.getElementById(opts.addBtnId || 'add_extra');
    var existing = opts.existing || {};
    var defaults = opts.defaultFields || [];

    if (!container || !tpl || !addBtn) return;

    addBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var clone = tpl.content.firstElementChild.cloneNode(true);
      container.appendChild(clone);
      _bindRow(clone, container);
      _updateDisabledOptions(container);
    });

    // initialize existing extras (used on edit page)
    (function initExisting() {
      try {
        var ex = existing || {};
        var defs = defaults || [];
        for (var k in ex) {
          if (!Object.prototype.hasOwnProperty.call(ex, k)) continue;
          if (defs.indexOf(k) !== -1) continue;
          if (document.querySelector('input[name="' + k + '"]')) continue;

          addBtn.click();
          var last = container.lastElementChild;
          var sel = last.querySelector('.extra-select');
          var inp = last.querySelector('.extra-input');
          sel.value = k;
          sel.dispatchEvent(new Event('change'));
          inp.value = ex[k];
          inp.name = k;
        }
      } catch (err) {
        // defensive: don't break the page if initialization fails
        console.error('initExtraFields error', err);
      }
    })();

    if (opts.autoAddIfEmpty && !container.children.length) {
      addBtn.click();
    }
  }

  window.initExtraFields = initExtraFields;
})();
