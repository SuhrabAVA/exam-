// ===== Общие помощники (Fetch API, токен в localStorage) =====
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

function showMsg(el, text, type) {
  if (!el) return;
  el.className = 'msg ' + type;
  el.textContent = text;
}
function fmtPrice(n) { return Number(n).toLocaleString('ru-RU') + ' ₸'; }
function placeholder() { return 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="320"><rect width="100%" height="100%" fill="#e4e6eb"/><text x="50%" y="50%" fill="#888" font-size="16" text-anchor="middle" dominant-baseline="middle">Нет фото</text></svg>'); }

// Навигация: показать имя пользователя / кнопку входа-выхода
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

const GENRES = { '1': 'Боевик', '2': 'Комедия', '3': 'Драма' };

// ===== Диспетчер страниц =====
document.addEventListener('DOMContentLoaded', () => {
  renderNav();
  const page = document.body.dataset.page;
  if (page === 'register') initRegister();
  if (page === 'login') initLogin();
  if (page === 'movies') initMovies();
  if (page === 'profile') initProfile();
});

// ----- Регистрация -----
function initRegister() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/register', { method: 'POST', body: {
        username: form.username.value.trim(),
        full_name: form.full_name.value.trim(),
        password: form.password.value,
      }});
      showMsg(msg, 'Регистрация успешна! Перенаправляем на вход…', 'success');
      setTimeout(() => location.href = 'login.html', 800);
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

// ----- Вход -----
function initLogin() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const data = await api('/api/login', { method: 'POST', body: {
        username: form.username.value.trim(),
        password: form.password.value,
      }});
      setAuth(data.token, data.user);
      location.href = 'movies.html';
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

// ----- Афиша -----
function initMovies() {
  const grid = document.getElementById('grid');
  const f = document.getElementById('filters');
  async function load() {
    const params = new URLSearchParams();
    if (f.genre.value) params.set('genre', f.genre.value);
    if (f.age_rating.value) params.set('age_rating', f.age_rating.value);
    if (f.q.value.trim()) params.set('q', f.q.value.trim());
    if (f.sort.value) params.set('sort', f.sort.value);
    const movies = await api('/api/movies?' + params.toString());
    grid.innerHTML = movies.length ? '' : '<div class="empty">Фильмы не найдены</div>';
    const today = new Date().toISOString().slice(0, 10);
    movies.forEach(m => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img class="poster" src="${m.poster_path}" onerror="this.src=placeholder()" alt="">
        <div class="body">
          <div class="title">${m.title}</div>
          <div class="meta">
            <span class="tag">${m.genre_name}</span>
            <span class="tag">${m.age_rating}+</span>
          </div>
          <div class="price">${fmtPrice(m.ticket_price)}</div>
          <form class="buy-form">
            <div class="row">
              <input type="date" name="show_date" min="${today}" required>
              <input type="number" name="quantity" min="1" value="1" required style="max-width:80px">
            </div>
            <button class="btn small" type="submit">Купить билет</button>
            <div class="msg"></div>
          </form>
        </div>`;
      const form = card.querySelector('form');
      const fmsg = card.querySelector('.msg');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!getToken()) { location.href = 'login.html'; return; }
        const qty = parseInt(form.quantity.value, 10);
        if (qty < 1) { showMsg(fmsg, 'Минимум 1 билет', 'error'); return; }
        if (form.show_date.value < today) { showMsg(fmsg, 'Дата в прошлом', 'error'); return; }
        try {
          await api('/api/tickets', { method: 'POST', body: {
            movie_id: m.id, show_date: form.show_date.value, quantity: qty,
          }});
          showMsg(fmsg, 'Билет куплен!', 'success');
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

// ----- Профиль -----
function initProfile() {
  if (!requireAuth()) return;
  const nameEl = document.getElementById('pName');
  const loginEl = document.getElementById('pLogin');
  const avatarEl = document.getElementById('pAvatar');
  const list = document.getElementById('tickets');
  const avForm = document.getElementById('avatarForm');
  const avMsg = document.getElementById('avatarMsg');

  async function load() {
    const data = await api('/api/profile');
    nameEl.textContent = data.user.full_name;
    loginEl.textContent = '@' + data.user.username;
    avatarEl.src = data.user.avatar_path || placeholder();
    list.innerHTML = data.tickets.length ? '' : '<div class="empty">У вас пока нет билетов</div>';
    data.tickets.forEach(t => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${t.poster_path}" onerror="this.src=placeholder()" alt="">
        <div class="info">
          <div class="title">${t.movie_title}</div>
          <div class="meta">Сеанс: ${t.show_date} · ${t.quantity} шт. · <b>${fmtPrice(t.total_price)}</b></div>
          <span class="badge ${t.status}">${t.status === 'active' ? 'Активен' : 'Возвращён'}</span>
        </div>
        ${t.status === 'active' ? `<button class="btn danger small" data-id="${t.id}">Вернуть</button>` : ''}`;
      const btn = item.querySelector('button');
      if (btn) btn.addEventListener('click', async () => {
        try { await api(`/api/tickets/${t.id}/refund`, { method: 'POST' }); load(); }
        catch (err) { alert(err.message); }
      });
      list.appendChild(item);
    });
  }
  avForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = avForm.avatar.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('avatar', file);
    try {
      await api('/api/profile/avatar', { method: 'POST', body: fd });
      showMsg(avMsg, 'Аватар обновлён', 'success');
      load();
    } catch (err) { showMsg(avMsg, err.message, 'error'); }
  });
  load();
}
