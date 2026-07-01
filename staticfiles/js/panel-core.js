// ═══════════════════════════════════════════════════════════
// KinderCRM — Director Panel Core JS
// Auth, API helpers, Toast, Modal, Common utilities
// ═══════════════════════════════════════════════════════════

const Panel = (() => {
  // ── Auth ──
  function getToken() { return localStorage.getItem('access_token'); }
  function getRefresh() { return localStorage.getItem('refresh_token'); }
  function getKGId() { return localStorage.getItem('kindergarten_id'); }

  function requireAuth() {
    if (!getToken()) { window.location.href = '/panel/login/'; return false; }
    return true;
  }

  function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('kindergarten_id');
    localStorage.removeItem('username');
    window.location.href = '/panel/login/';
  }

  // ── API Fetch ──
  async function apiFetch(url, options = {}) {
    const token = getToken();
    if (!token) { logout(); return null; }

    const headers = { 'Authorization': `Bearer ${token}`, ...options.headers };
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const res = await fetch(url, { ...options, headers });
      if (res.status === 401) {
        // Try refresh
        const refreshed = await tryRefresh();
        if (refreshed) {
          headers['Authorization'] = `Bearer ${getToken()}`;
          return fetch(url, { ...options, headers });
        }
        logout();
        return null;
      }
      return res;
    } catch (err) {
      toast('Tarmoq xatosi', 'error');
      return null;
    }
  }

  async function tryRefresh() {
    const refresh = getRefresh();
    if (!refresh) return false;
    try {
      const res = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        return true;
      }
    } catch(e) {}
    return false;
  }

  async function apiGet(url) {
    const res = await apiFetch(url);
    if (!res) return null;
    if (!res.ok) { const d = await res.json().catch(()=>({})); toast(d.detail || d.error || 'Xatolik', 'error'); return null; }
    const data = await res.json();
    return data.results !== undefined ? data.results : data;
  }

  async function apiPost(url, body) {
    const isFormData = body instanceof FormData;
    const res = await apiFetch(url, {
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body),
    });
    if (!res) return null;
    return res;
  }

  async function apiPatch(url, body) {
    const isFormData = body instanceof FormData;
    const res = await apiFetch(url, {
      method: 'PATCH',
      body: isFormData ? body : JSON.stringify(body),
    });
    if (!res) return null;
    return res;
  }

  async function apiDelete(url) {
    const res = await apiFetch(url, { method: 'DELETE' });
    if (!res) return null;
    return res;
  }

  // ── Toast ──
  function toast(msg, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const icons = { success: '✓', error: '✗', info: 'ℹ' };
    const t = document.createElement('div');
    t.className = `toast toast-${type} fade-in`;
    t.innerHTML = `<span>${icons[type] || 'ℹ'}</span> <span>${msg}</span>`;
    container.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(20px)'; setTimeout(() => t.remove(), 300); }, 4000);
  }

  // ── Modal ──
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('show');
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('show');
  }
  function closeAllModals() {
    document.querySelectorAll('.modal-overlay.show').forEach(m => m.classList.remove('show'));
  }

  // ── Confirm ──
  function confirm(msg) {
    return window.confirm(msg);
  }

  // ── Format date ──
  function formatDate(str) {
    if (!str) return '-';
    const d = new Date(str);
    return d.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  function formatTime(str) {
    if (!str) return '';
    const d = new Date(str);
    return d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });
  }

  // ── Sidebar Active ──
  function initSidebar() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item[data-path]').forEach(item => {
      const p = item.getAttribute('data-path');
      if (path === p || (p !== '/panel/' && path.startsWith(p))) {
        item.classList.add('active');
      }
    });

    // Hamburger
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    if (hamburger && sidebar) {
      hamburger.addEventListener('click', () => sidebar.classList.toggle('open'));
      document.addEventListener('click', e => {
        if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== hamburger) {
          sidebar.classList.remove('open');
        }
      });
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', e => { e.preventDefault(); logout(); });

    // Username display
    const usernameEl = document.getElementById('navUsername');
    if (usernameEl) usernameEl.textContent = localStorage.getItem('username') || 'Admin';
  }

  // ── Loading ──
  function showLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = '<div class="page-loader"><span class="spinner"></span></div>';
  }

  function showEmpty(containerId, icon, title, desc) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">${icon}</div><h3>${title}</h3><p>${desc}</p></div>`;
  }

  // ── Init (call on every panel page) ──
  function init() {
    if (!requireAuth()) return false;
    initSidebar();
    // Close modals on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', e => { if (e.target === overlay) overlay.classList.remove('show'); });
    });
    return true;
  }

  return {
    getToken, getRefresh, getKGId, requireAuth, logout,
    apiFetch, apiGet, apiPost, apiPatch, apiDelete,
    toast, openModal, closeModal, closeAllModals, confirm,
    formatDate, formatTime, initSidebar, showLoading, showEmpty, init,
  };
})();
