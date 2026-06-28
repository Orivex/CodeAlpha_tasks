// ── CSRF Helper ────────────────────────────────
function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// ── Like Buttons ────────────────────────────────
document.addEventListener('click', async function(e) {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;
  e.preventDefault();

  const postId = btn.dataset.postId;
  const icon = btn.querySelector('.like-icon');
  const count = btn.querySelector('.like-count');

  try {
    const res = await fetch(`/post/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await res.json();

    btn.dataset.liked = data.liked;
    btn.classList.toggle('liked', data.liked);
    icon.textContent = data.liked ? '❤️' : '🤍';
    count.textContent = data.count;

    // Animate
    btn.style.transform = 'scale(1.3)';
    setTimeout(() => btn.style.transform = '', 200);
  } catch (err) {
    console.error('Like failed', err);
  }
});

// ── Follow Buttons ──────────────────────────────
document.addEventListener('click', async function(e) {
  const btn = e.target.closest('.follow-btn');
  if (!btn) return;
  e.preventDefault();

  const username = btn.dataset.username;
  const isFollowing = btn.dataset.following === 'true';

  try {
    const res = await fetch(`/follow/${username}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await res.json();

    btn.dataset.following = data.following;

    if (data.following) {
      btn.textContent = 'Following';
      btn.classList.remove('btn-outline');
      btn.classList.add('btn-primary');
    } else {
      btn.textContent = 'Follow';
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-outline');
    }

    // Update follower count on profile page if it exists
    const followerCountEl = document.getElementById('followerCount');
    if (followerCountEl && data.followers_count !== undefined) {
      followerCountEl.textContent = data.followers_count;
    }
  } catch (err) {
    console.error('Follow failed', err);
  }
});

// ── Quick Comment Forms ─────────────────────────
document.addEventListener('submit', async function(e) {
  const form = e.target.closest('.comment-quick-form');
  if (!form) return;
  e.preventDefault();

  const input = form.querySelector('input[name="content"]');
  const content = input.value.trim();
  if (!content) return;

  const postId = form.dataset.postId;

  try {
    const res = await fetch(`/post/${postId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `content=${encodeURIComponent(content)}`
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      // Update comment count on this post card
      const postCard = document.getElementById(`post-${postId}`);
      if (postCard) {
        const commentBtn = postCard.querySelector('.btn-reaction[href]');
        if (commentBtn) {
          const span = commentBtn.querySelector('span');
          if (span) span.textContent = parseInt(span.textContent || 0) + 1;
        }
      }
      showToast('Comment posted!');
    }
  } catch (err) {
    console.error('Comment failed', err);
  }
});

// ── Image Preview ───────────────────────────────
const imageInput = document.getElementById('id_image');
if (imageInput) {
  imageInput.addEventListener('change', function() {
    const container = document.getElementById('image-preview-container');
    container.innerHTML = '';
    const file = this.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        const img = document.createElement('img');
        img.src = e.target.result;
        container.appendChild(img);
      };
      reader.readAsDataURL(file);
    }
  });
}

// ── Toast Notification ──────────────────────────
function showToast(msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px;
    background: #333; color: #fff; padding: 10px 18px;
    border-radius: 8px; font-size: 14px; z-index: 9999;
    opacity: 0; transition: opacity .3s;
  `;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.style.opacity = '1');
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ── Auto-dismiss messages ───────────────────────
setTimeout(() => {
  document.querySelectorAll('.message').forEach(el => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 3000);
