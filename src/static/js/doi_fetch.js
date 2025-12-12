// doi_fetch.js
// Shared DOI fetch UI logic. Looks for elements with ids:
// - doi_input, doi_fetch, doi_status
// and when fetching, posts to /doi_lookup returning JSON { fields: {...} }
(function () {
  function initDoiFetch() {
    var btn = document.getElementById('doi_fetch');
    var input = document.getElementById('doi_input');
    var status = document.getElementById('doi_status');

    if (!btn || !input || !status) return;

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var v = input.value && input.value.trim();
      if (!v) {
        status.textContent = 'Please provide a DOI or DOI link.';
        status.style.color = '#ff6b6b';
        return;
      }
      status.textContent = 'Fetching...';
      status.style.color = '#60a5fa';
      fetch('/doi_lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doi: v })
      }).then(function (res) {
        if (!res.ok) throw res;
        return res.json();
      }).then(function (data) {
        status.textContent = 'DOI data loaded successfully!';
        status.style.color = '#48bb78';
        var fields = data.fields || {};
        Object.keys(fields).forEach(function (k) {
          var el = document.querySelector('[name="' + k + '"]');
          if (el) {
            el.value = fields[k];
          } else {
            var addBtn = document.getElementById('add_extra');
            if (addBtn) {
              addBtn.click();
              var container = document.getElementById('extra_fields_container');
              var last = container.lastElementChild;
              var sel = last.querySelector('.extra-select');
              var inp = last.querySelector('.extra-input');
              sel.value = k;
              sel.dispatchEvent(new Event('change'));
              inp.value = fields[k];
              inp.name = k;
            }
          }
        });
      }).catch(function (err) {
        if (err && err.json) {
          err.json().then(function (j) {
            status.textContent = j.error || 'Failed to fetch DOI metadata.';
            status.style.color = '#ff6b6b';
          });
        } else {
          status.textContent = 'Failed to fetch DOI metadata.';
          status.style.color = '#ff6b6b';
        }
      });
    });
  }

  // expose initializer
  window.initDoiFetch = initDoiFetch;
})();
