function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast');
  const inner = document.getElementById('toast-inner');
  inner.textContent = message;
  inner.className = type;
  container.classList.remove('hidden');
  container.classList.add('flex');
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => {
    container.classList.add('hidden');
    container.classList.remove('flex');
  }, duration);
}

async function loadModelStatus() {
  try {
    const res = await fetch('/api/training/status');
    if (!res.ok) return;
    const data = await res.json();
    const el = document.getElementById('model-status');
    if (!el) return;
    if (data.model_exists) {
      el.innerHTML = `<span class="text-green-400 font-medium">Model ready</span><br><span class="text-slate-500">${data.encoding_count} encodings</span>`;
    } else {
      el.innerHTML = `<span class="text-yellow-400 font-medium">Model not trained</span><br><a href="/" onclick="return false;" class="text-slate-500 text-xs">Train from dashboard</a>`;
    }
  } catch (_) {}
}

async function checkActiveSession() {
  try {
    const res = await fetch('/api/attendance/sessions/active');
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById('live-badge');
    if (!badge) return;
    if (data.active) {
      badge.classList.remove('hidden');
      badge.classList.add('flex');
    } else {
      badge.classList.add('hidden');
      badge.classList.remove('flex');
    }
  } catch (_) {}
}

document.addEventListener('DOMContentLoaded', () => {
  loadModelStatus();
  checkActiveSession();
});
