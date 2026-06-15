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
function placeholder() { return 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="180"><rect width="100%" height="100%" fill="#e4e6eb"/><text x="50%" y="50%" fill="#888" font-size="16" text-anchor="middle" dominant-baseline="middle">Нет фото</text></svg>'); }

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
  if (page === 'cars') initCars();
  if (page === 'profile') initProfile();
});

function initRegister() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/register', { method: 'POST', body: {
        username: form.username.value.trim(), full_name: form.full_name.value.trim(),
        phone_number: form.phone_number.value.trim(), password: form.password.value,
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
      location.href = 'cars.html';
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

function carCard(a) {
  return `
    <img class="poster" style="height:180px" src="${a.image_path || placeholder()}" onerror="this.src=placeholder()" alt="">
    <div class="body">
      <div class="title">${a.brand} ${a.model}</div>
      <div class="meta"><span class="tag">${a.year} г.</span></div>
      <div class="price">${fmtPrice(a.price)}</div>
      <div class="meta">${a.description || ''}</div>
      <div class="meta">📞 ${a.seller_phone} · ${a.seller_name}</div>
    </div>`;
}

function initCars() {
  const grid = document.getElementById('grid');
  const f = document.getElementById('filters');
  async function load() {
    const params = new URLSearchParams();
    if (f.brand.value.trim()) params.set('brand', f.brand.value.trim());
    if (f.year_from.value) params.set('year_from', f.year_from.value);
    if (f.year_to.value) params.set('year_to', f.year_to.value);
    if (f.sort.value) params.set('sort', f.sort.value);
    const list = await api('/api/cars?' + params.toString());
    grid.innerHTML = list.length ? '' : '<div class="empty">Объявления не найдены</div>';
    list.forEach(a => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = carCard(a);
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
  const list = document.getElementById('ads');
  const addForm = document.getElementById('addForm');
  const addMsg = document.getElementById('addMsg');
  const avForm = document.getElementById('avatarForm');
  const avMsg = document.getElementById('avatarMsg');

  async function load() {
    const data = await api('/api/profile');
    nameEl.textContent = data.user.full_name;
    loginEl.textContent = '@' + data.user.username + ' · 📞 ' + data.user.phone_number;
    avatarEl.src = data.user.avatar_path || placeholder();
    list.innerHTML = data.ads.length ? '' : '<div class="empty">У вас пока нет объявлений</div>';
    data.ads.forEach(a => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${a.image_path || placeholder()}" onerror="this.src=placeholder()" alt="" style="width:120px;height:80px">
        <div class="info">
          <div class="title">${a.brand} ${a.model}, ${a.year}</div>
          <div class="meta"><b>${fmtPrice(a.price)}</b></div>
          <span class="badge ${a.status}">${a.status === 'active' ? 'В продаже' : 'Продано'}</span>
        </div>
        ${a.status === 'active' ? `<button class="btn danger small">Снять с продажи</button>` : ''}`;
      const btn = item.querySelector('button');
      if (btn) btn.addEventListener('click', async () => {
        try { await api(`/api/ads/${a.id}/sold`, { method: 'POST' }); load(); }
        catch (err) { alert(err.message); }
      });
      list.appendChild(item);
    });
  }

  addForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const price = parseInt(addForm.price.value, 10);
    if (price <= 0) { showMsg(addMsg, 'Цена должна быть больше 0', 'error'); return; }
    const fd = new FormData();
    fd.append('brand', addForm.brand.value.trim());
    fd.append('model', addForm.model.value.trim());
    fd.append('year', addForm.year.value);
    fd.append('price', addForm.price.value);
    fd.append('description', addForm.description.value.trim());
    if (addForm.image.files[0]) fd.append('image', addForm.image.files[0]);
    try {
      await api('/api/ads', { method: 'POST', body: fd });
      showMsg(addMsg, 'Объявление добавлено!', 'success');
      addForm.reset();
      load();
    } catch (err) { showMsg(addMsg, err.message, 'error'); }
  });

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
