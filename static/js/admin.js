/**
 * ELECTRO-ORDINATEUR — admin.js
 * Admin panel JS: sidebar, inline edits, upload previews, etc.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash alerts after 5 seconds
  document.querySelectorAll('.alert[data-bs-dismiss]').forEach(el => {
    setTimeout(() => {
      try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch(e) {}
    }, 5000);
  });

  // Initialize tooltips
  document.querySelectorAll('[title]').forEach(el => {
    if (el.title) {
      try { new bootstrap.Tooltip(el, { trigger: 'hover', placement: 'top' }); } catch(e) {}
    }
  });

  // Confirm delete on forms with data-confirm
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  // Color input sync (settings page)
  document.querySelectorAll('input[type="color"]').forEach(picker => {
    const textId = picker.id + 'Text';
    const textInput = document.getElementById(textId);
    if (textInput) {
      picker.addEventListener('input', () => textInput.value = picker.value);
      textInput.addEventListener('input', () => {
        if (/^#[0-9A-Fa-f]{6}$/.test(textInput.value)) {
          picker.value = textInput.value;
        }
      });
    }
  });

  // Upload zone drag & drop (product form)
  const zone = document.getElementById('uploadZone');
  if (zone) {
    zone.addEventListener('dragover', e => {
      e.preventDefault();
      zone.classList.add('dragover');
    });
    ['dragleave', 'dragend'].forEach(ev => {
      zone.addEventListener(ev, () => zone.classList.remove('dragover'));
    });
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('dragover');
      const input = document.getElementById('imageInput');
      if (input && e.dataTransfer.files.length) {
        // Create a new FileList-like object
        const dt = new DataTransfer();
        Array.from(e.dataTransfer.files).forEach(f => {
          if (f.type.startsWith('image/')) dt.items.add(f);
        });
        input.files = dt.files;
        if (typeof previewImages === 'function') previewImages(input);
      }
    });
  }

  // Image preview (product form)
  const imageInput = document.getElementById('imageInput');
  if (imageInput) {
    imageInput.addEventListener('change', () => previewImages(imageInput));
  }

  // Inline stock inputs - save on Enter
  document.querySelectorAll('.inline-stock-input').forEach(input => {
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (typeof updateStock === 'function') updateStock(input);
        input.blur();
      }
    });
  });

  // Sidebar active link highlight
  highlightActiveNav();
});

// ─────────────────────────────────────────────────────────
//  Image Preview (admin product form)
// ─────────────────────────────────────────────────────────
function previewImages(input) {
  const preview = document.getElementById('newPreviews');
  if (!preview) return;
  preview.innerHTML = '';

  Array.from(input.files).forEach((file, idx) => {
    if (!file.type.startsWith('image/')) return;
    const maxMb = 5;
    if (file.size > maxMb * 1024 * 1024) {
      showAdminAlert(`Image trop grande : ${file.name} (max ${maxMb} Mo)`, 'warning');
      return;
    }

    const reader = new FileReader();
    reader.onload = e => {
      const div = document.createElement('div');
      div.className = 'upload-preview';
      div.innerHTML = `
        <img src="${e.target.result}" alt="${escapeHtml(file.name)}">
        <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.5);color:white;font-size:0.6rem;padding:2px 4px;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">
          ${file.name}
        </div>
      `;
      preview.appendChild(div);
    };
    reader.readAsDataURL(file);
  });
}

// ─────────────────────────────────────────────────────────
//  Alerts
// ─────────────────────────────────────────────────────────
function showAdminAlert(message, type = 'info') {
  const container = document.querySelector('.admin-header .header-actions');
  if (!container) { alert(message); return; }

  const alert = document.createElement('div');
  alert.className = `alert alert-${type} py-1 px-3 mb-0 d-flex align-items-center gap-2`;
  alert.style.cssText = 'font-size:0.85rem;border-radius:8px;';
  alert.innerHTML = `${escapeHtml(message)} <button type="button" class="btn-close btn-close-sm ms-2" data-bs-dismiss="alert"></button>`;
  container.prepend(alert);

  setTimeout(() => {
    try { bootstrap.Alert.getOrCreateInstance(alert).close(); } catch(e) { alert.remove(); }
  }, 4000);
}

// ─────────────────────────────────────────────────────────
//  Sidebar Active Highlight
// ─────────────────────────────────────────────────────────
function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && path.startsWith(href) && href.length > 1) {
      link.classList.add('active');
    }
  });
}

// ─────────────────────────────────────────────────────────
//  Spec Builder Helper (product form)
// ─────────────────────────────────────────────────────────
function addSpec() {
  const container = document.getElementById('specsContainer');
  if (!container) return;

  const row = document.createElement('div');
  row.className = 'spec-row';
  row.innerHTML = `
    <input type="text" name="spec_key[]" class="form-control form-control-sm" placeholder="Propriété (ex: CPU)">
    <input type="text" name="spec_val[]" class="form-control form-control-sm" placeholder="Valeur (ex: Intel i5)">
    <button type="button" class="btn-remove-spec" onclick="this.parentElement.remove()" title="Supprimer">
      <i class="bi bi-x"></i>
    </button>
  `;
  container.appendChild(row);
  row.querySelector('input').focus();
}

// ─────────────────────────────────────────────────────────
//  Icon Picker (categories)
// ─────────────────────────────────────────────────────────
function updateIconPreview(val) {
  const el = document.getElementById('iconPreviewIcon');
  if (el) el.className = 'bi ' + (val || 'bi-box');
}

function setIcon(icon) {
  const input = document.getElementById('iconeInput');
  if (input) {
    input.value = icon;
    updateIconPreview(icon);
    input.focus();
  }
}

// ─────────────────────────────────────────────────────────
//  Helpers
// ─────────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

// Confirm unsaved changes
let formDirty = false;
document.addEventListener('change', e => {
  if (e.target.closest('form#productForm')) formDirty = true;
});
window.addEventListener('beforeunload', e => {
  if (formDirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
document.querySelector('form#productForm')?.addEventListener('submit', () => {
  formDirty = false;
});
