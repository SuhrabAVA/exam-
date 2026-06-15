// ===== Общие помощники =====
function getToken() { return localStorage.getItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch (e) { return null; } }
function setAuth(token, user) { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }
function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); location.href = 'ads.html'; }
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
function roomsLabel(n) { return n === 0 ? 'Студия' : n + '-комн.'; }

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
  if (page === 'ads') initAds();
  if (page === 'profile') initProfile();
});

function initRegister() {
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const data = await api('/api/register', { method: 'POST', body: {
        username: form.username.value.trim(), full_name: form.full_name.value.trim(),
        phone: form.phone.value.trim(), password: form.password.value,
      }});
      setAuth(data.token, data.user);        // авто-вход после регистрации
      location.href = 'ads.html';
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
      location.href = 'ads.html';
    } catch (err) { showMsg(msg, err.message, 'error'); }
  });
}

// ----- Лента объявлений -----
async function initAds() {
  const grid = document.getElementById('grid');
  const f = document.getElementById('filters');
  const createBtn = document.getElementById('createBtn');
  const modal = document.getElementById('modal');
  const createForm = document.getElementById('createForm');
  const createMsg = document.getElementById('createMsg');

  // Города в фильтр
  const cities = await api('/api/cities');
  cities.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; f.city.appendChild(o); });
  // Категории в фильтр и в форму создания
  const cats = await api('/api/categories');
  cats.forEach(c => {
    const o1 = document.createElement('option'); o1.value = c.id; o1.textContent = c.name; f.category.appendChild(o1);
    const o2 = document.createElement('option'); o2.value = c.id; o2.textContent = c.name; createForm.category_id.appendChild(o2);
  });

  async function load() {
    const p = new URLSearchParams();
    if (f.city.value) p.set('city', f.city.value);
    if (f.category.value) p.set('category', f.category.value);
    if (f.price_from.value) p.set('price_from', f.price_from.value);
    if (f.price_to.value) p.set('price_to', f.price_to.value);
    if (f.rooms.value) p.set('rooms', f.rooms.value);
    if (f.sort.value) p.set('sort', f.sort.value);
    if (f.q.value.trim()) p.set('q', f.q.value.trim());
    const list = await api('/api/ads?' + p.toString());
    grid.innerHTML = list.length ? '' : '<div class="empty">Объявления не найдены</div>';
    list.forEach(a => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img class="poster" style="height:180px" src="${a.image_path || placeholder()}" onerror="this.src=placeholder()" alt="">
        <div class="body">
          <div class="title">${a.title}</div>
          <div class="price">${fmtPrice(a.price)}</div>
          <div class="meta">
            <span class="tag">${a.category}</span>
            <span class="tag">${roomsLabel(a.rooms)}</span>
            <span class="tag">${a.area ? a.area + ' м²' : ''}</span>
          </div>
          <div class="meta">📍 ${a.city} · ${a.seller_name}</div>
          <button class="btn secondary small fav">☆ В избранное</button>
        </div>`;
      card.querySelector('.fav').addEventListener('click', async () => {
        if (!getToken()) { location.href = 'login.html'; return; }
        try { await api('/api/favorites', { method: 'POST', body: { ad_id: a.id } }); alert('Добавлено в избранное'); }
        catch (err) { alert(err.message); }
      });
      grid.appendChild(card);
    });
  }

  f.addEventListener('submit', (e) => { e.preventDefault(); load(); });
  f.addEventListener('change', load);

  createBtn.addEventListener('click', () => {
    if (!getToken()) { location.href = 'login.html'; return; }
    modal.style.display = 'flex';
  });
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
  document.getElementById('closeModal').addEventListener('click', () => modal.style.display = 'none');

  createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const price = parseInt(createForm.price.value, 10);
    const area = parseFloat(createForm.area.value);
    const rooms = parseInt(createForm.rooms.value || '0', 10);
    if (!createForm.title.value.trim()) { showMsg(createMsg, 'Введите заголовок', 'error'); return; }
    if (!createForm.city.value.trim()) { showMsg(createMsg, 'Введите город', 'error'); return; }
    if (price <= 0) { showMsg(createMsg, 'Цена должна быть > 0', 'error'); return; }
    if (rooms < 0) { showMsg(createMsg, 'Комнаты >= 0', 'error'); return; }
    if (!(area > 0)) { showMsg(createMsg, 'Площадь должна быть > 0', 'error'); return; }
    const fd = new FormData();
    ['category_id', 'title', 'description', 'price', 'rooms', 'area', 'city'].forEach(k => fd.append(k, createForm[k].value));
    if (createForm.image.files[0]) fd.append('image', createForm.image.files[0]);
    try {
      await api('/api/ads', { method: 'POST', body: fd });
      showMsg(createMsg, 'Объявление создано!', 'success');
      createForm.reset();
      modal.style.display = 'none';
      load();
    } catch (err) { showMsg(createMsg, err.message, 'error'); }
  });

  load();
}

// ----- Профиль -----
function initProfile() {
  if (!requireAuth()) return;
  const nameEl = document.getElementById('pName');
  const loginEl = document.getElementById('pLogin');
  const avatarEl = document.getElementById('pAvatar');
  const myList = document.getElementById('myAds');
  const favList = document.getElementById('favs');
  const avForm = document.getElementById('avatarForm');
  const avMsg = document.getElementById('avatarMsg');

  async function loadProfile() {
    const data = await api('/api/profile');
    nameEl.textContent = data.user.full_name;
    loginEl.textContent = '@' + data.user.username + ' · 📞 ' + data.user.phone;
    avatarEl.src = data.user.avatar_path || placeholder();
  }
  async function loadMyAds() {
    const list = await api('/api/users/me/ads');
    myList.innerHTML = list.length ? '' : '<div class="empty">У вас пока нет объявлений</div>';
    list.forEach(a => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${a.image_path || placeholder()}" onerror="this.src=placeholder()" alt="" style="width:120px;height:80px">
        <div class="info">
          <div class="title">${a.title}</div>
          <div class="meta"><b>${fmtPrice(a.price)}</b> · ${a.city} · ${a.created_at}</div>
          <span class="badge ${a.status}">${a.status === 'active' ? 'Активно' : 'Продано'}</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px">
          ${a.status === 'active' ? `<button class="btn small close">Продано</button>` : ''}
          <button class="btn danger small del">Удалить</button>
        </div>`;
      const closeBtn = item.querySelector('.close');
      if (closeBtn) closeBtn.addEventListener('click', async () => {
        try { await api(`/api/ads/${a.id}/close`, { method: 'PATCH' }); loadMyAds(); } catch (err) { alert(err.message); }
      });
      item.querySelector('.del').addEventListener('click', async () => {
        if (!confirm('Удалить объявление?')) return;
        try { await api(`/api/ads/${a.id}`, { method: 'DELETE' }); loadMyAds(); } catch (err) { alert(err.message); }
      });
      myList.appendChild(item);
    });
  }
  async function loadFavs() {
    const list = await api('/api/favorites');
    favList.innerHTML = list.length ? '' : '<div class="empty">Избранное пусто</div>';
    list.forEach(a => {
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <img src="${a.image_path || placeholder()}" onerror="this.src=placeholder()" alt="" style="width:120px;height:80px">
        <div class="info">
          <div class="title">${a.title}</div>
          <div class="meta"><b>${fmtPrice(a.price)}</b> · ${a.city}</div>
        </div>
        <button class="btn danger small">Удалить из избранного</button>`;
      item.querySelector('button').addEventListener('click', async () => {
        try { await api(`/api/favorites/${a.id}`, { method: 'DELETE' }); loadFavs(); } catch (err) { alert(err.message); }
      });
      favList.appendChild(item);
    });
  }
  avForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = avForm.avatar.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('avatar', file);
    try { await api('/api/profile/avatar', { method: 'POST', body: fd }); showMsg(avMsg, 'Аватар обновлён', 'success'); loadProfile(); }
    catch (err) { showMsg(avMsg, err.message, 'error'); }
  });
  loadProfile(); loadMyAds(); loadFavs();
}
