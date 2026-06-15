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
function placeholder() { return 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="320"><rect width="100%" height="100%" fill="#e4e6eb"/><text x="50%" y="50%" fill="#888" font-size="16" text-anchor="middle" dominant-baseline="middle">Нет фото</text></svg>'); }

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
  if (page === 'rooms') initRooms();
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
      const data = await api('/api/login', { method: 'POST', body: {
        username: form.username.value.trim(), password: form.password.value,
      }});
      setAuth(data.token, data.user);
      location.href = 'rooms.html';
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

function initRooms() {
  const grid = document.getElementById('grid');
  const f = document.getElementById('filters');
  async function load() {
    const params = new URLSearchParams();
    if (f.type.value) params.set('type', f.type.value);
    if (f.capacity.value) params.set('capacity', f.capacity.value);
    if (f.sort.value) params.set('sort', f.sort.value);
    const rooms = await api('/api/rooms?' + params.toString());
    grid.innerHTML = rooms.length ? '' : '<div class="empty">Номера не найдены</div>';
    const today = new Date().toISOString().slice(0, 10);
    rooms.forEach(r => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img class="poster" src="${r.image_path}" onerror="this.src=placeholder()" alt="">
        <div class="body">
          <div class="title">№ ${r.room_number}</div>
          <div class="meta">
            <span class="tag">${r.type_name}</span>
            <span class="tag">${r.capacity} чел.</span>
          </div>
          <div class="price">${fmtPrice(r.price_per_night)} / ночь</div>
          <form class="buy-form">
            <div class="row">
              <label style="flex:1">Заезд<input type="date" name="check_in_date" min="${today}" required></label>
              <label style="flex:1">Выезд<input type="date" name="check_out_date" min="${today}" required></label>
            </div>
            <button class="btn small" type="submit">Забронировать</button>
            <div class="msg"></div>
          </form>
        </div>`;
      const form = card.querySelector('form');
      const fmsg = card.querySelector('.msg');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!getToken()) { location.href = 'login.html'; return; }
        const ci = form.check_in_date.value, co = form.check_out_date.value;
        if (ci < today) { showMsg(fmsg, 'Дата заезда в прошлом', 'error'); return; }
        if (co <= ci) { showMsg(fmsg, 'Выезд должен быть позже заезда', 'error'); return; }
        try {
          const res = await api('/api/bookings', { method: 'POST', body: { room_id: r.id, check_in_date: ci, check_out_date: co } });
          showMsg(fmsg, `Забронировано! ${res.nights} ноч. — ${fmtPrice(res.total_price)}`, 'success');
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
  const avatarEl = document.getElementById('pAvatar');
  const list = document.getElementById('bookings');
  const avForm = document.getElementById('avatarForm');
  const avMsg = document.getElementById('avatarMsg');

  async function load() {
    const data = await api('/api/profile');
    nameEl.textContent = data.user.full_name;
    loginEl.textContent = '@' + data.user.username;
    avatarEl.src = data.user.avatar_path || placeholder();
    list.innerHTML = data.bookings.length ? '' : '<div class="empty">У вас пока нет бронирований</div>';
    data.bookings.forEach(b => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${b.image_path}" onerror="this.src=placeholder()" alt="">
        <div class="info">
          <div class="title">Номер № ${b.room_number} (${b.type_name})</div>
          <div class="meta">${b.check_in_date} → ${b.check_out_date} · <b>${fmtPrice(b.total_price)}</b></div>
          <span class="badge ${b.status}">${b.status === 'active' ? 'Активна' : 'Отменена'}</span>
        </div>
        ${b.status === 'active' ? `<button class="btn danger small">Отменить</button>` : ''}`;
      const btn = item.querySelector('button');
      if (btn) btn.addEventListener('click', async () => {
        try { await api(`/api/bookings/${b.id}/cancel`, { method: 'POST' }); load(); }
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
    try { await api('/api/profile/avatar', { method: 'POST', body: fd }); showMsg(avMsg, 'Аватар обновлён', 'success'); load(); }
    catch (err) { showMsg(avMsg, err.message, 'error'); }
  });
  load();
}
