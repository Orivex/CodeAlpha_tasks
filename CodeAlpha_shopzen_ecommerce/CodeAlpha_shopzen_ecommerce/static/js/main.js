// Toggle mobile nav
function toggleMenu() {
  const menu = document.getElementById('mobileMenu');
  menu.classList.toggle('open');
}

// Auto-dismiss messages after 4s
document.addEventListener('DOMContentLoaded', () => {
  const messages = document.querySelectorAll('.message');
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(100%)';
      msg.style.transition = 'all .3s ease';
      setTimeout(() => msg.remove(), 300);
    }, 4000);
  });

  // Format card number input
  const cardInput = document.querySelector('input[name="card_number"]');
  if (cardInput) {
    cardInput.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
      let matches = v.match(/\d{4,16}/g);
      let match = (matches && matches[0]) || '';
      let parts = [];
      for (let i = 0, len = match.length; i < len; i += 4) {
        parts.push(match.substring(i, i + 4));
      }
      e.target.value = parts.length ? parts.join(' ') : v;
    });
  }

  // Format expiry input
  const expiryInput = document.querySelector('input[name="expiry"]');
  if (expiryInput) {
    expiryInput.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length >= 2) v = v.slice(0, 2) + '/' + v.slice(2, 4);
      e.target.value = v;
    });
  }

  // Checkout form - add loading state on submit
  const checkoutForm = document.getElementById('checkoutForm');
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', (e) => {
      const btn = checkoutForm.querySelector('button[type="submit"]');
      btn.textContent = 'Processing…';
      btn.disabled = true;
    });
  }
});
