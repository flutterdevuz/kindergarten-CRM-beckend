// ═══════════════════════════════════════════════════════════
// KinderCRM — Superadmin JS
// CSRF, API Fetch, Toast, Modals
// ═══════════════════════════════════════════════════════════

function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

async function apiFetch(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
    ...options.headers
  };
  try {
    const res = await fetch(url, { ...options, headers });
    return res;
  } catch (e) {
    showToast('Tarmoq xatosi', 'error');
    return null;
  }
}

function showToast(msg, type = 'success') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.borderLeftColor = type === 'error' ? 'var(--error)' : 'var(--primary)';
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 3000);
}

function openModal(id) {
  document.getElementById(id).classList.add('show');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('show');
}
document.querySelectorAll('.modal-overlay').forEach(el => {
  el.addEventListener('click', e => { if(e.target===el) el.classList.remove('show'); });
});

async function updateAppStatus(id, status) {
  if (!confirm(`Haqiqatan ham arizani "${status}" holatiga o'tkazmoqchimisiz?`)) return;
  const res = await apiFetch(`/superadmin/api/applications/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
  if (res && res.ok) {
    showToast("Holat o'zgartirildi");
    window.location.reload();
  } else {
    showToast("Xatolik yuz berdi", "error");
  }
}

// Global scope to store app id for create form
let currentCreateAppId = null;

function openCreateModal(appId, appName) {
  currentCreateAppId = appId;
  document.getElementById('c_kg_name').textContent = appName;
  document.getElementById('c_username').value = '';
  document.getElementById('c_password').value = '';
  openModal('createKgModal');
}

async function createKindergarten() {
  const username = document.getElementById('c_username').value;
  const password = document.getElementById('c_password').value;
  const btn = document.getElementById('createKgBtn');

  if (!username || password.length < 8) {
    return showToast("Parol kamida 8ta belgi bo'lishi kerak", "error");
  }

  btn.disabled = true;
  btn.textContent = 'Kuting...';

  const res = await apiFetch(`/superadmin/api/applications/${currentCreateAppId}/create-kindergarten/`, {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });

  if (res && res.ok) {
    showToast("Bog'cha va admin muvaffaqiyatli yaratildi!");
    setTimeout(() => window.location.reload(), 1500);
  } else {
    const data = await res.json();
    showToast(data.error || "Xatolik", "error");
    btn.disabled = false;
    btn.textContent = 'Yaratish';
  }
}

async function toggleKg(id) {
  if (!confirm("Bog'cha holatini o'zgartirmoqchimisiz?")) return;
  const res = await apiFetch(`/superadmin/api/kindergartens/${id}/toggle/`, { method: 'POST' });
  if (res && res.ok) {
    showToast("Holat o'zgardi");
    window.location.reload();
  } else {
    showToast("Xatolik yuz berdi", "error");
  }
}
