/**
 * ELECTRO-ORDINATEUR — main.js
 * Public-facing JS: theme, language, mini-cart, WhatsApp group
 */

// ─────────────────────────────────────────────────────────
//  Dark Mode
// ─────────────────────────────────────────────────────────
(function initTheme() {
  const saved = localStorage.getItem('electro-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (!icon) return;
  icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('electro-theme', next);
      updateThemeIcon(next);
    });
  }

  // Apply saved theme icon
  const saved = localStorage.getItem('electro-theme') || 'light';
  updateThemeIcon(saved);

  // Initialize cart from localStorage
  loadCartFromStorage();
  renderMiniCart();

  // Attach add-to-cart buttons
  attachCartButtons();

  // Animate product cards on scroll
  initScrollAnimations();
});

// ─────────────────────────────────────────────────────────
//  Mini-Cart (WhatsApp Group Selection)
// ─────────────────────────────────────────────────────────
let cart = [];

function loadCartFromStorage() {
  try {
    cart = JSON.parse(sessionStorage.getItem('electro-cart') || '[]');
  } catch (e) {
    cart = [];
  }
}

function saveCartToStorage() {
  sessionStorage.setItem('electro-cart', JSON.stringify(cart));
}

function attachCartButtons() {
  document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const item = {
        id: btn.dataset.id,
        nom: btn.dataset.nom,
        ref: btn.dataset.ref,
        prix: btn.dataset.prix,
      };
      addToCart(item);
      // Visual feedback
      btn.innerHTML = '<i class="bi bi-check-circle"></i>';
      btn.style.background = '#25d366';
      btn.style.color = 'white';
      setTimeout(() => {
        btn.innerHTML = '<i class="bi bi-cart-plus"></i>';
        btn.style.background = '';
        btn.style.color = '';
      }, 1200);
    });
  });
}

function addToCart(item) {
  const existing = cart.find(i => i.id === item.id);
  if (!existing) {
    cart.push(item);
    saveCartToStorage();
    renderMiniCart();
    showCartToast(item.nom);
  }
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  saveCartToStorage();
  renderMiniCart();
  renderCartModal();
}

function clearCart() {
  cart = [];
  saveCartToStorage();
  renderMiniCart();
  renderCartModal();
}

function renderMiniCart() {
  const miniCart = document.getElementById('miniCart');
  const cartCount = document.getElementById('cartCount');
  if (!miniCart) return;

  cartCount.textContent = cart.length;

  if (cart.length > 0) {
    miniCart.classList.add('visible');
  } else {
    miniCart.classList.remove('visible');
  }
}

function openCartModal() {
  renderCartModal();
  const modal = new bootstrap.Modal(document.getElementById('cartModal'));
  modal.show();
}

function renderCartModal() {
  const container = document.getElementById('cartItems');
  const sendBtn = document.getElementById('cartSendBtn');
  if (!container) return;

  if (cart.length === 0) {
    const t = window.ELECTRO?.t || {};
    container.innerHTML = `<p class="text-center text-muted py-3">${t.cart_empty || 'Votre sélection est vide'}</p>`;
    if (sendBtn) sendBtn.style.display = 'none';
    return;
  }

  if (sendBtn) sendBtn.style.display = 'inline-flex';
  const devise = window.ELECTRO?.currency || 'DH';

  container.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-info">
        <div class="cart-item-name">${escapeHtml(item.nom)}</div>
        <div class="cart-item-price">${item.prix} ${devise}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);">Réf: ${escapeHtml(item.ref)}</div>
      </div>
      <i class="bi bi-x-circle cart-item-remove" onclick="removeFromCart('${item.id}')"></i>
    </div>
  `).join('');
}

function sendCartWA() {
  const lang = window.ELECTRO?.lang || 'fr';
  const number = window.ELECTRO?.waNumber || '';
  const devise = window.ELECTRO?.currency || 'DH';

  if (!number || cart.length === 0) return;

  let header, footer;
  if (lang === 'ar') {
    header = 'مرحباً، أنا مهتم بالمنتجات التالية:\n';
    footer = '\nشكراً لكم.';
  } else {
    header = 'Bonjour, je suis intéressé(e) par les articles suivants :\n';
    footer = '\nMerci beaucoup.';
  }

  const lines = cart.map(item =>
    `• ${item.nom} — Réf: ${item.ref} — ${item.prix} ${devise}`
  );
  const message = header + lines.join('\n') + footer;
  const encoded = encodeURIComponent(message);
  const url = `https://wa.me/${number}?text=${encoded}`;

  window.open(url, '_blank');

  // Track each item click
  cart.forEach(item => {
    if (window.ELECTRO?.trackUrl) {
      fetch(`${window.ELECTRO.trackUrl}/${item.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }).catch(() => {});
    }
  });
}

// ─────────────────────────────────────────────────────────
//  Toast Notification
// ─────────────────────────────────────────────────────────
function showCartToast(name) {
  const existing = document.getElementById('cartToast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'cartToast';
  const lang = window.ELECTRO?.lang || 'fr';
  const msg = lang === 'ar' ? `✓ تمت الإضافة: ${name.substring(0, 30)}` : `✓ Ajouté : ${name.substring(0, 30)}`;

  toast.style.cssText = `
    position:fixed;bottom:90px;${lang === 'ar' ? 'left' : 'right'}:16px;
    z-index:9999;background:#1a237e;color:white;
    padding:0.6rem 1.2rem;border-radius:8px;font-size:0.85rem;
    font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,0.2);
    animation:slideInRight 0.3s ease;max-width:280px;
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ─────────────────────────────────────────────────────────
//  Scroll Animations
// ─────────────────────────────────────────────────────────
function initScrollAnimations() {
  const cards = document.querySelectorAll('.product-card, .category-card, .kpi-card');
  if (!cards.length || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = 'fadeInUp 0.4s ease forwards';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  // Add CSS animation
  if (!document.getElementById('scrollAnimCSS')) {
    const style = document.createElement('style');
    style.id = 'scrollAnimCSS';
    style.textContent = `
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      .product-card, .category-card { opacity: 0; }
    `;
    document.head.appendChild(style);
  }

  cards.forEach((card, i) => {
    card.style.animationDelay = `${(i % 8) * 0.05}s`;
    observer.observe(card);
  });
}

// ─────────────────────────────────────────────────────────
//  Helpers
// ─────────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// Navbar scroll behavior
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar-electro');
  if (!navbar) return;
  if (window.scrollY > 10) {
    navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.25)';
  } else {
    navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.2)';
  }
}, { passive: true });
