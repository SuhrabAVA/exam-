// ===== Общие помощники =====
function getToken() { return localStorage.getItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch (e) { return null; } }
function setAuth(token, user) { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }
function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); location.href = 'login.html'; }
function requireAuth() { if (!getToken()) { location.href = 'login.html'; return false; } return true; }

async function api(path, opts = {}) {
  opts.headers = opts.headers || {};
  const t = getToken();
  if (t) opts.headers['Authorization'] = 'Bearer ' + t;
  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(path, opts);
  let data = null;
  try { data = await res.json(); } catch (e) {}
  if (!res.ok) throw new Error((data && data.error) || ('Ошибка ' + res.status));
  return data;
}

function showMsg(el, text, type) { if (!el) return; el.className = 'msg ' + type; el.textContent = text; }
function fmtPrice(n) { return Number(n).toLocaleString('ru-RU') + ' ₸'; }
function placeholder() { return 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="100%" height="100%" fill="#e4e6eb"/><text x="50%" y="50%" fill="#888" font-size="12" text-anchor="middle" dominant-baseline="middle">logo</text></svg>'); }

function renderNav() {
  const user = getUser();
  const authLink = document.getElementById('authLink');
  const userName = document.getElementById('userName');
  if (authLink) {
    if (user) { authLink.textContent = 'Выйти'; authLink.href = '#'; authLink.onclick = (e) => { e.preventDefault(); logout(); }; }
    else { authLink.textContent = 'Войти'; authLink.href = 'login.html'; }
  }
  if (userName) userName.textContent = user ? user.full_name : '';
}

document.addEventListener('DOMContentLoaded', () => {
  renderNav();
  const page = document.body.dataset.page;
  if (page === 'register') initRegister();
  if (page === 'login') initLogin();
  if (page === 'vacancies') initVacancies();
  if (page === 'profile') initProfile();
});

function initRegister() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/register', { method: 'POST', body: {
        username: form.username.value.trim(), full_name: form.full_name.value.trim(), password: form.password.value,
      }});
      showMsg(msg, 'Регистрация успешна! Перенаправляем на вход…', 'success');
      setTimeout(() => location.href = 'login.html', 800);
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

function initLogin() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const data = await api('/api/login', { method: 'POST', body: { username: form.username.value.trim(), password: form.password.value } });
      setAuth(data.token, data.user);
      location.href = 'vacancies.html';
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

function initVacancies() {
  const grid = document.getElementById('grid');
  const f = document.getElementById('filters');
  async function load() {
    const params = new URLSearchParams();
    if (f.category.value) params.set('category', f.category.value);
    if (f.experience.value !== '') params.set('experience', f.experience.value);
    if (f.q.value.trim()) params.set('q', f.q.value.trim());
    if (f.sort.value) params.set('sort', f.sort.value);
    const vacancies = await api('/api/vacancies?' + params.toString());
    grid.innerHTML = vacancies.length ? '' : '<div class="empty">Вакансии не найдены</div>';
    vacancies.forEach(v => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="body">
          <div style="display:flex;gap:12px;align-items:center">
            <img src="${v.company_logo_path}" onerror="this.src=placeholder()" alt="" style="width:56px;height:56px;border-radius:8px;object-fit:cover">
            <div class="title">${v.title}</div>
          </div>
          <div class="meta">
            <span class="tag">${v.category_name}</span>
            <span class="tag">${v.experience_label}</span>
          </div>
          <div class="price">${fmtPrice(v.salary)}</div>
          <div class="meta">${v.description}</div>
          <form class="buy-form">
            <textarea name="cover_letter" placeholder="Сопроводительное письмо…" required></textarea>
            <button class="btn small" type="submit">Откликнуться</button>
            <div class="msg"></div>
          </form>
        </div>`;
      const form = card.querySelector('form');
      const fmsg = card.querySelector('.msg');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!getToken()) { location.href = 'login.html'; return; }
        const letter = form.cover_letter.value.trim();
        if (!letter) { showMsg(fmsg, 'Введите письмо', 'error'); return; }
        try {
          await api('/api/applications', { method: 'POST', body: { vacancy_id: v.id, cover_letter: letter } });
          showMsg(fmsg, 'Отклик отправлен!', 'success');
          form.reset();
        } catch (err) { showMsg(fmsg, err.message, 'error'); }
      });
      grid.appendChild(card);
    });
  }
  f.addEventListener('submit', (e) => { e.preventDefault(); load(); });
  f.addEventListener('change', load);
  load();
}

function initProfile() {
  if (!requireAuth()) return;
  const nameEl = document.getElementById('pName');
  const loginEl = document.getElementById('pLogin');
  const list = document.getElementById('applications');
  async function load() {
    const data = await api('/api/profile');
    nameEl.textContent = data.user.full_name;
    loginEl.textContent = '@' + data.user.username;
    list.innerHTML = data.applications.length ? '' : '<div class="empty">У вас пока нет откликов</div>';
    data.applications.forEach(a => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${a.company_logo_path}" onerror="this.src=placeholder()" alt="" style="width:56px;height:56px">
        <div class="info">
          <div class="title">${a.vacancy_title}</div>
          <div class="meta">${a.category_name} · ${fmtPrice(a.salary)} · отклик от ${a.apply_date}</div>
          <div class="meta">«${a.cover_letter}»</div>
          <span class="badge ${a.status}">${a.status === 'active' ? 'Активен' : 'Отозван'}</span>
        </div>
        ${a.status === 'active' ? `<button class="btn danger small">Отозвать</button>` : ''}`;
      const btn = item.querySelector('button');
      if (btn) btn.addEventListener('click', async () => {
        try { await api(`/api/applications/${a.id}/withdraw`, { method: 'POST' }); load(); }
        catch (err) { alert(err.message); }
      });
      list.appendChild(item);
    });
  }
  load();
}
