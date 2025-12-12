// Collect selected citation ids and submit export form as hidden input
(function () {
  function exportBibTeX() {
    var form = document.forms['exportform'];
    if (!form) return;

    var selectedIds = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(function (checkbox) {
      selectedIds.push(checkbox.id);
    });
    if (selectedIds.length === 0) {
      alert('Please select at least one citation to export.');
      return;
    }

    while (form.lastChild && form.lastChild.name === 'citation_ids') {
      form.removeChild(form.lastChild);
    }
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'citation_ids';
    input.value = selectedIds;
    form.appendChild(input);
    form.submit();
  }

  // expose global function used by templates
  window.export_bibtex = exportBibTeX;
})();
