// copy_bibtex.js
// Extracted from templates/bibtex.html
// Provides a function to copy the contents of an element to the clipboard
function copy_to_clipboard(elm_id) {
  var text = document.getElementById(elm_id).textContent;
  if (!navigator.clipboard) {
    // Fallback for older browsers
    var textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showCopyNotification();
    } catch (err) {
      alert('Failed to copy to clipboard');
    }
    document.body.removeChild(textArea);
    return;
  }

  navigator.clipboard.writeText(text).then(function() {
    showCopyNotification();
  }).catch(function(err) {
    alert('Failed to copy to clipboard');
  });
}

function showCopyNotification() {
  const notification = document.getElementById('copy-notification');
  if (!notification) return;
  notification.style.display = 'block';
  setTimeout(function() {
    notification.style.display = 'none';
  }, 2000);
}

// If desired, attach to buttons with data-copy-target attribute on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('[data-copy-target]').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      const target = btn.getAttribute('data-copy-target');
      if (target) copy_to_clipboard(target);
    });
  });
});
