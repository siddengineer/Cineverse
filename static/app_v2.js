console.log("🔥 BUILD VERSION 2 LOADED");
/* ─── CONFIG ───────────────────────────────────────────────────────────────── */
// const API_BASE = 'http://127.0.0.1:8000/api';
const API_BASE = "/api";
/* ─── STATE ────────────────────────────────────────────────────────────────── */
let state = {
  user: null,
  accessToken: null,
  currentPage: 'home',
  searchTimer: null,
  searchPage: 1,
  selectedStars: 0,
  currentMovieId: null,
  chatHistory: [],
};

/* ─── INIT ─────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const access = localStorage.getItem('cv_access');
  const user = localStorage.getItem('cv_user');
  if (access && user) {
    state.accessToken = access;
    state.user = JSON.parse(user);
    updateAuthUI();
  }
  loadHomeData();
  loadGenres();
  showPage('home');
});

/* ─── API HELPERS ──────────────────────────────────────────────────────────── */
async function api(endpoint, method = 'GET', body = null, auth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && state.accessToken) {
    headers['Authorization'] = `Token ${state.accessToken}`;
  }
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  let res;
  try {
    res = await fetch(`${API_BASE}${endpoint}`, opts);
  } catch (networkErr) {
    throw new Error('Cannot reach server. Is the backend running on port 8000?');
  }

  // Only auto-logout on 401 for protected routes, NOT for login/register
  const isAuthEndpoint = endpoint.includes('/auth/login') || endpoint.includes('/auth/register');
  if (res.status === 401 && !isAuthEndpoint) {
    logout();
    throw new Error('Session expired. Please sign in again.');
  }

  if (res.status === 204) return {};

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    // Flatten DRF validation errors nicely
    const msg = err.detail || err.error || err.non_field_errors?.[0]
      || Object.entries(err).map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`).join(' | ')
      || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return res.json();
}

/* ─── AUTH ─────────────────────────────────────────────────────────────────── */
async function doLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  const btn = errEl.previousElementSibling?.tagName === 'BUTTON'
    ? errEl.previousElementSibling : null;
  errEl.textContent = '';
  if (!username || !password) { errEl.textContent = 'Please fill all fields.'; return; }
  try {
    const data = await api('/auth/login/', 'POST', { username, password });
    setSession(data);
    closeModal('loginModal');
    showToast('Welcome back, ' + data.user.username + '!', 'success');
    loadHomeData();
  } catch (e) {
    errEl.textContent = e.message.includes('{') ? 'Invalid username or password.' : e.message;
  }
}

async function doRegister() {
  const username = document.getElementById('regUsername').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  const errEl = document.getElementById('regError');
  errEl.textContent = '';
  if (!username || !email || !password) { errEl.textContent = 'Please fill all fields.'; return; }
  if (password.length < 6) { errEl.textContent = 'Password must be at least 6 characters.'; return; }
  try {
    const data = await api('/auth/register/', 'POST', { username, email, password, password2: password });
    setSession(data);
    closeModal('registerModal');
    showToast('Account created! Welcome, ' + data.user.username + '!', 'success');
    loadHomeData();
  } catch (e) {
    errEl.textContent = e.message.includes('{') ? 'Registration failed. Try a different username.' : e.message;
  }
}

function setSession(data) {
  state.user = data.user;
  state.accessToken = data.token;
  localStorage.setItem('cv_access', data.token);
  localStorage.setItem('cv_user', JSON.stringify(data.user));
  updateAuthUI();
}

function logout() {
  if (state.accessToken) {
    api('/auth/logout/', 'POST', null, true).catch(() => {});
  }
  state.user = null;
  state.accessToken = null;
  state.chatHistory = [];
  localStorage.removeItem('cv_access');
  localStorage.removeItem('cv_user');
  updateAuthUI();
  showPage('home');
  showToast('You have signed out.');
}

function updateAuthUI() {
  const authBtns = document.getElementById('authButtons');
  const userMenu = document.getElementById('userMenu');
  const recoSection = document.getElementById('recoSection');
  if (state.user) {
    authBtns.classList.add('hidden'); userMenu.classList.remove('hidden');
    const initials = state.user.username ? state.user.username[0].toUpperCase() : 'U';
    document.getElementById('userAvatar').textContent = initials;
    document.getElementById('dropdownName').textContent = state.user.username;
    document.getElementById('profileAvatarLarge').textContent = initials;
    document.getElementById('profileInfo').innerHTML = `
      <div><strong style="font-size:1.3rem;font-family:var(--ff-display)">${state.user.username}</strong></div>
      <div style="color:var(--text-sub);font-size:0.9rem;margin-top:0.25rem">${state.user.email || ''}</div>`;
    if (recoSection) recoSection.style.display = '';
    loadRecommendations();
  } else {
    authBtns.classList.remove('hidden'); userMenu.classList.add('hidden');
    if (recoSection) recoSection.style.display = 'none';
  }
}

function toggleUserDropdown() { document.getElementById('userDropdown').classList.toggle('hidden'); }
document.addEventListener('click', e => {
  if (!e.target.closest('.user-menu')) document.getElementById('userDropdown')?.classList.add('hidden');
});

/* ─── PAGES ────────────────────────────────────────────────────────────────── */
function showPage(page, data = null) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const pageEl = document.getElementById('page-' + page);
  if (pageEl) pageEl.classList.add('active');
  const navLink = document.querySelector(`.nav-link[onclick*="'${page}'"]`);
  if (navLink) navLink.classList.add('active');
  state.currentPage = page; window.scrollTo(0, 0);
  if (page === 'watchlist') loadWatchlist();
  if (page === 'lists') loadLists();
  if (page === 'profile') loadProfile();
  if (page === 'detail' && data) loadMovieDetail(data);
}

/* ─── HOME DATA ─────────────────────────────────────────────────────────────── */
async function loadHomeData() {
  loadSection('trendingWeek', '/movies/trending-week/');
  loadSection('topRated', '/movies/top-rated/');
  loadSection('indianMovies', '/movies/indian/');
}

async function loadSection(containerId, endpoint) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '<div class="loader-row"></div>';
  try {
    const data = await api(endpoint);
    const movies = Array.isArray(data) ? data : (data.results || []);
    container.innerHTML = '';
    movies.forEach(m => container.appendChild(buildMovieCard(m)));
  } catch (e) {
    container.innerHTML = `<div style="color:var(--text-dim);padding:1rem;font-size:0.875rem;">Failed to load. Is the backend running?</div>`;
  }
}

async function loadRecommendations() {
  if (!state.user) return;
  try {
    const data = await api('/movies/recommendations/', 'GET', null, true);
    const container = document.getElementById('recommendations');
    if (!container) return;
    container.innerHTML = '';
    const movies = Array.isArray(data) ? data : (data.results || []);
    movies.forEach(m => container.appendChild(buildMovieCard(m)));
  } catch {}
}

/* ─── GENRE PARSING — FIX for raw JSON display ───────────────────────────── */
function parseGenreNames(genreField) {
  if (!genreField) return [];
  // Already a plain string like "Action, Crime, Drama"
  if (typeof genreField === 'string') {
    // Check if it looks like JSON array: starts with [ or [{
    const trimmed = genreField.trim();
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed.replace(/'/g, '"'));
        if (Array.isArray(parsed)) {
          return parsed.map(g => (typeof g === 'object' ? g.name : g)).filter(Boolean);
        }
      } catch {}
      // fallback: strip brackets and extract quoted names
      const matches = trimmed.match(/"name":\s*"([^"]+)"/g) || [];
      if (matches.length) return matches.map(m => m.replace(/"name":\s*"/, '').replace('"', ''));
    }
    // Plain comma-separated
    return genreField.split(',').map(g => g.trim()).filter(Boolean);
  }
  // Array of objects [{id,name}]
  if (Array.isArray(genreField)) {
    return genreField.map(g => (typeof g === 'object' ? g.name : g)).filter(Boolean);
  }
  return [];
}

/* ─── MOVIE CARDS ───────────────────────────────────────────────────────────── */
function buildMovieCard(movie, removable = false) {
  const card = document.createElement('div');
  card.className = 'movie-card';
  card.onclick = () => showPage('detail', movie.id);
  let inner = '';
  if (movie.poster_url) {
    inner = `
      <img src="${movie.poster_url}" alt="${escHtml(movie.title)}" loading="lazy"
        onerror="this.parentElement.innerHTML='${fallbackInner(movie)}'">
      <div class="movie-card-overlay">
        <div class="movie-card-title">${escHtml(movie.title)}</div>
        <div class="movie-card-meta">${movie.release_year || ''} · ${formatLang(movie.language)}</div>
        ${movie.rating ? `<div class="movie-card-rating">★ ${parseFloat(movie.rating).toFixed(1)}</div>` : ''}
      </div>`;
  } else {
    inner = `<div class="movie-card-fallback">
      <div class="film-icon">🎞</div>
      <div class="fallback-title">${escHtml(movie.title)}</div>
      <div class="fallback-year">${movie.release_year || ''}</div>
    </div>`;
  }
  if (removable) {
    inner += `<div class="watchlist-card-actions"><button class="watchlist-remove-btn" onclick="event.stopPropagation();removeFromWatchlist(${movie.watchlist_id || movie.id}, this.closest('.movie-card'))" title="Remove">✕</button></div>`;
  }
  card.innerHTML = inner;
  return card;
}

function fallbackInner(movie) {
  return `<div class=\\\"movie-card-fallback\\\"><div class=\\\"film-icon\\\">🎞</div><div class=\\\"fallback-title\\\">${escHtml(movie.title)}</div></div>`;
}

/* ─── MOVIE DETAIL ──────────────────────────────────────────────────────────── */
async function loadMovieDetail(movieId) {
  state.currentMovieId = movieId;
  const container = document.getElementById('movieDetailContent');
  container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:60vh;color:var(--text-dim)">Loading…</div>`;
  try {
    const movie = await api(`/movies/${movieId}/`, 'GET', null, state.user ? true : false);
    renderMovieDetail(movie, container);
    loadSimilar(movieId);
  } catch (e) {
    container.innerHTML = `<div style="padding:3rem;color:var(--red)">${e.message}</div>`;
  }
}

function renderMovieDetail(movie, container) {
  // ✅ FIX: properly parse genres, not raw JSON
  const genres = parseGenreNames(movie.genre_names || movie.genres);
  const genreChips = genres.map(g => `<span class="genre-chip">${escHtml(g)}</span>`).join('');
  const userRating = movie.user_rating || 0;
  const inWatchlist = movie.in_watchlist || false;

  container.innerHTML = `
    <div class="detail-back" onclick="history.back()">← Back</div>
    <div class="detail-hero">
      <div class="detail-hero-bg" style="background-image:url('${movie.poster_url || ''}')"></div>
      <div class="detail-hero-gradient"></div>
      <div class="detail-hero-content">
        <div class="detail-poster">
          ${movie.poster_url
            ? `<img src="${movie.poster_url}" alt="${escHtml(movie.title)}" />`
            : `<div class="movie-card-fallback" style="height:100%"><div class="film-icon" style="font-size:3rem">🎞</div><div class="fallback-title">${escHtml(movie.title)}</div></div>`}
        </div>
        <div class="detail-info">
          <div class="detail-genre-chips">${genreChips || '<span class="genre-chip">Film</span>'}</div>
          <h1 class="detail-title">${escHtml(movie.title)}</h1>
          <div class="detail-meta">
            ${movie.release_year ? `<span>${movie.release_year}</span>` : ''}
            ${movie.runtime ? `<span>${movie.runtime} min</span>` : ''}
            ${movie.language ? `<span>${formatLang(movie.language)}</span>` : ''}
            ${movie.rating ? `<span class="rating-badge">★ ${parseFloat(movie.rating).toFixed(1)} <span style="font-weight:400;color:var(--text-dim)">(${movie.vote_count?.toLocaleString() || '?'} votes)</span></span>` : ''}
          </div>
          <p class="detail-overview">${escHtml(movie.overview || 'No description available.')}</p>
          <div class="detail-actions">
            <button class="btn-primary" id="watchlistBtn" onclick="toggleWatchlist(${movie.id})">${inWatchlist ? '✓ In Watchlist' : '+ Watchlist'}</button>
            ${movie.imdb_id ? `<a href="https://www.imdb.com/title/${movie.imdb_id}/" target="_blank" class="btn-outline">IMDb ↗</a>` : ''}
            <button class="btn-outline" onclick="askAIAbout(${movie.id}, '${escHtml(movie.title).replace(/'/g, "\\'")}')">Ask AI</button>
            <button class="btn-outline" onclick="checkOTT(${movie.id}, '${escHtml(movie.title).replace(/'/g, "\\'")}')">📺 Where to Watch</button>
          </div>
        </div>
      </div>
    </div>
    <div class="detail-body">
      ${state.user ? `
      <div class="detail-section">
        <h3>Rate This Film</h3>
        <div class="star-rating" id="starRating">
          ${[1,2,3,4,5,6,7,8,9,10].map(i => `<span class="star ${i <= userRating ? 'active' : ''}" data-val="${i}" onclick="selectStar(${i})" onmouseover="hoverStar(${i})" onmouseout="resetStarHover()">★</span>`).join('')}
          <span class="star-rating-label" id="starLabel">${userRating ? userRating + '/10' : 'Tap to rate'}</span>
        </div>
        <button class="btn-primary rate-submit" onclick="submitRating(${movie.id})">Save Rating</button>
      </div>` : `
      <div class="detail-section">
        <p style="color:var(--text-sub);font-size:0.9rem"><a onclick="openModal('loginModal')" style="color:var(--gold);cursor:pointer">Sign in</a> to rate this film and get personalised recommendations.</p>
      </div>`}
      <div id="ottResult"></div>
      <div class="detail-section">
        <h3>Similar Films</h3>
        <div class="movie-row" id="similarMovies"><div class="loader-row"></div></div>
      </div>
    </div>`;
  state.selectedStars = userRating;
}

async function checkOTT(movieId, title) {
  const container = document.getElementById('ottResult');
  if (!container) return;
  container.innerHTML = `<div class="detail-section"><h3>📺 Where to Watch</h3><div style="color:var(--text-dim);font-size:0.9rem">Checking platforms…</div></div>`;
  try {
    const data = await api(`/ai/ott/${movieId}/`);
    const platforms = data.platforms || [];
    container.innerHTML = `
      <div class="detail-section">
        <h3>📺 Where to Watch — <em>${escHtml(title)}</em></h3>
        ${platforms.length
          ? `<div class="ott-chips">${platforms.map(p => `<span class="ott-chip">${escHtml(p)}</span>`).join('')}</div>
             <p style="color:var(--text-dim);font-size:0.8rem;margin-top:0.5rem">Confidence: ${data.confidence || '?'} ${data.note ? '· ' + escHtml(data.note) : ''}</p>`
          : `<p style="color:var(--text-sub)">No platform info available. ${data.note ? escHtml(data.note) : ''}</p>`}
      </div>`;
  } catch (e) {
    container.innerHTML = `<div class="detail-section" style="color:var(--red)">${e.message}</div>`;
  }
}

async function loadSimilar(movieId) {
  const container = document.getElementById('similarMovies');
  if (!container) return;
  try {
    const data = await api(`/movies/${movieId}/similar/`);
    container.innerHTML = '';
    const movies = Array.isArray(data) ? data : (data.results || []);
    movies.forEach(m => container.appendChild(buildMovieCard(m)));
  } catch {}
}

/* ─── STAR RATING ──────────────────────────────────────────────────────────── */
function selectStar(val) { state.selectedStars = val; updateStars(val); }
function hoverStar(val) { updateStars(val, true); }
function resetStarHover() { updateStars(state.selectedStars); }
function updateStars(val, hovering = false) {
  document.querySelectorAll('#starRating .star').forEach(s => {
    s.classList.toggle('active', parseInt(s.dataset.val) <= val);
  });
  const label = document.getElementById('starLabel');
  if (label) label.textContent = val ? (hovering ? val + '/10' : state.selectedStars + '/10') : 'Tap to rate';
}

async function submitRating(movieId) {
  if (!state.user) { openModal('loginModal'); return; }
  if (!state.selectedStars) { showToast('Please select a star rating.', 'error'); return; }
  try {
    await api('/ratings/rate/', 'POST', { movie_id: movieId, rating: state.selectedStars }, true);
    showToast('Rating saved!', 'success');
  } catch (e) { showToast(e.message, 'error'); }
}

/* ─── WATCHLIST ─────────────────────────────────────────────────────────────── */
async function toggleWatchlist(movieId) {
  if (!state.user) { openModal('loginModal'); return; }
  const btn = document.getElementById('watchlistBtn');
  try {
    const wl = await api('/watchlist/', 'GET', null, true);
    const items = Array.isArray(wl) ? wl : (wl.results || []);
    const existing = items.find(i => i.movie?.id === movieId || i.movie_id === movieId);
    if (existing) {
      await api(`/watchlist/${existing.id}/remove/`, 'DELETE', null, true);
      if (btn) btn.textContent = '+ Watchlist';
      showToast('Removed from watchlist.');
    } else {
      await api('/watchlist/add/', 'POST', { movie_id: movieId }, true);
      if (btn) btn.textContent = '✓ In Watchlist';
      showToast('Added to watchlist!', 'success');
    }
  } catch (e) { showToast(e.message, 'error'); }
}

async function loadWatchlist() {
  if (!state.user) {
    document.getElementById('watchlistContent').innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">🔐</div>
        <p><a onclick="openModal('loginModal')" style="color:var(--gold);cursor:pointer">Sign in</a> to see your watchlist</p>
      </div>`; return;
  }
  const container = document.getElementById('watchlistContent');
  container.innerHTML = '<div class="loader-row" style="grid-column:1/-1;height:200px"></div>';
  try {
    const data = await api('/watchlist/', 'GET', null, true);
    const items = Array.isArray(data) ? data : (data.results || []);
    container.innerHTML = '';
    if (items.length === 0) {
      container.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🎬</div><p>Your watchlist is empty. Start adding films!</p></div>`;
      return;
    }
    items.forEach(item => {
      const movie = { ...item.movie, watchlist_id: item.id };
      container.appendChild(buildMovieCard(movie, true));
    });
  } catch (e) { container.innerHTML = `<div style="color:var(--red);padding:1rem">${e.message}</div>`; }
}

async function removeFromWatchlist(itemId, cardEl) {
  try {
    await api(`/watchlist/${itemId}/remove/`, 'DELETE', null, true);
    cardEl.style.transition = 'all 0.3s';
    cardEl.style.opacity = '0'; cardEl.style.transform = 'scale(0.8)';
    setTimeout(() => cardEl.remove(), 300);
    showToast('Removed from watchlist.');
  } catch (e) { showToast(e.message, 'error'); }
}

/* ─── SEARCH ────────────────────────────────────────────────────────────────── */
function debounceSearch() {
  clearTimeout(state.searchTimer);
  state.searchTimer = setTimeout(() => runSearch(1), 350);
}

function doHeroSearch() {
  const q = document.getElementById('heroSearch').value.trim();
  if (!q) return;
  showPage('search');
  document.getElementById('searchInput').value = q;
  runSearch(1);
}

async function runSearch(page = 1) {
  const q = document.getElementById('searchInput').value.trim();
  const genre = document.getElementById('filterGenre').value;
  const year = document.getElementById('filterYear').value;
  const lang = document.getElementById('filterLang').value;
  const container = document.getElementById('searchResults');
  if (!q && !genre && !year && !lang) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">🎬</div><p>Start typing to search…</p></div>`;
    document.getElementById('searchPagination').innerHTML = ''; return;
  }
  container.innerHTML = '<div class="loader-row" style="grid-column:1/-1;height:200px;"></div>';
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (genre) params.set('genre', genre);
  if (year) params.set('year', year);
  if (lang) params.set('language', lang);
  params.set('page', page);
  try {
    const data = await api(`/movies/search/?${params}`);
    container.innerHTML = '';
    const results = Array.isArray(data) ? data : (data.results || []);
    if (results.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">😶</div><p>No films found. Try different terms.</p></div>`;
    } else { results.forEach(m => container.appendChild(buildMovieCard(m))); }
    renderPagination(data, page);
  } catch (e) {
    container.innerHTML = `<div style="color:var(--red);padding:1rem;grid-column:1/-1">${e.message}</div>`;
  }
}

function renderPagination(data, currentPage) {
  const el = document.getElementById('searchPagination');
  if (!el) return;
  if (!data.count || (!data.next && !data.previous && data.count <= 20)) { el.innerHTML = ''; return; }
  const total = Math.ceil(data.count / 20);
  let html = '';
  for (let i = Math.max(1, currentPage - 2); i <= Math.min(total, currentPage + 2); i++) {
    html += `<button class="${i === currentPage ? 'active' : ''}" onclick="runSearch(${i})">${i}</button>`;
  }
  el.innerHTML = html;
}

async function loadGenres() {
  try {
    const genres = await api('/movies/genres/');
    const sel = document.getElementById('filterGenre');
    genres.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g.name; opt.textContent = g.name;
      sel.appendChild(opt);
    });
  } catch {}
}

/* ─── LISTS ─────────────────────────────────────────────────────────────────── */
async function loadLists() {
  if (!state.user) {
    document.getElementById('listsContent').innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">🔐</div>
        <p><a onclick="openModal('loginModal')" style="color:var(--gold);cursor:pointer">Sign in</a> to manage your lists</p>
      </div>`; return;
  }
  const container = document.getElementById('listsContent');
  container.innerHTML = '<div class="loader-row" style="height:120px"></div>';
  try {
    const data = await api('/lists/mine/', 'GET', null, true);
    const items = Array.isArray(data) ? data : (data.results || []);
    container.innerHTML = '';
    if (items.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><p>No lists yet. Create one or let AI curate one for you!</p></div>`;
      return;
    }
    items.forEach(list => container.appendChild(buildListCard(list)));
  } catch (e) {
    container.innerHTML = `<div style="color:var(--red);padding:1rem">${e.message}</div>`;
  }
}

function buildListCard(list) {
  const card = document.createElement('div');
  card.className = 'list-card';
  card.dataset.id = list.id;
  card.innerHTML = `
    <div class="list-card-header">
      <div class="list-card-title">${escHtml(list.title)}</div>
      <div class="list-card-actions-row">
        <button class="list-action-btn ask-ai-btn" onclick="event.stopPropagation();askAIAboutList(${list.id},'${escHtml(list.title).replace(/'/g,"\\'")}')">
          ✨ Ask AI
        </button>
        <button class="list-action-btn delete-list-btn" onclick="event.stopPropagation();deleteList(${list.id}, this.closest('.list-card'))" title="Delete list">
          🗑
        </button>
      </div>
    </div>
    <div class="list-card-desc">${escHtml(list.description || 'No description')}</div>
    <div class="list-card-meta">
      <span>🎬 ${list.movie_count || 0} films</span>
      <span>${list.is_public ? '🌐 Public' : '🔒 Private'}</span>
      ${list.is_ai_generated ? '<span class="ai-badge">✨ AI</span>' : ''}
      <span>❤️ ${list.like_count || 0}</span>
    </div>`;
  return card;
}

async function deleteList(listId, cardEl) {
  if (!confirm('Delete this list? This cannot be undone.')) return;
  try {
    await api(`/lists/${listId}/`, 'DELETE', null, true);
    cardEl.style.transition = 'all 0.3s';
    cardEl.style.opacity = '0'; cardEl.style.transform = 'scale(0.9)';
    setTimeout(() => cardEl.remove(), 300);
    showToast('List deleted.', 'success');
  } catch (e) { showToast(e.message, 'error'); }
}

function askAIAboutList(listId, title) {
  showPage('ai');
  const prompt = `Give me movie recommendations to add to my list called "${title}". What films would fit perfectly?`;
  document.getElementById('chatInput').value = prompt;
  sendChat();
}

async function createList() {
  if (!state.user) { openModal('loginModal'); return; }
  const name = document.getElementById('listName').value.trim();
  const description = document.getElementById('listDesc').value.trim();
  const is_public = document.getElementById('listPublic').checked;
  const errEl = document.getElementById('listError');
  errEl.textContent = '';
  if (!name) { errEl.textContent = 'Please enter a list name.'; return; }
  try {
    await api('/lists/', 'POST', { title: name, description, is_public }, true);
    closeModal('createListModal');
    document.getElementById('listName').value = '';
    document.getElementById('listDesc').value = '';
    document.getElementById('listPublic').checked = false;
    showToast('List created!', 'success');
    loadLists();
  } catch (e) { errEl.textContent = e.message; }
}

/* ─── AI LIST GENERATOR MODAL ─────────────────────────────────────────────── */
async function openAIListModal() {
  if (!state.user) { openModal('loginModal'); return; }
  openModal('aiListModal');
}

async function generateAIList() {
  const prompt = document.getElementById('aiListPrompt').value.trim();
  const saveList = document.getElementById('aiListSave').checked;
  const errEl = document.getElementById('aiListError');
  const resultEl = document.getElementById('aiListResult');
  errEl.textContent = '';
  resultEl.innerHTML = '';
  if (!prompt) { errEl.textContent = 'Please enter a prompt.'; return; }

  resultEl.innerHTML = `<div style="color:var(--text-dim);font-size:0.9rem;padding:1rem 0">✨ AI is curating your list…</div>`;
  try {
    const data = await api('/ai/list/', 'POST', {
      prompt,
      save: saveList,
      title: prompt.substring(0, 80)
    }, true);

    const movies = data.movies || [];
    if (movies.length === 0) {
      resultEl.innerHTML = `<div style="color:var(--text-sub)">No movies found. Try a different prompt.</div>`;
      return;
    }

    resultEl.innerHTML = `
      <div style="font-size:0.85rem;color:var(--text-dim);margin-bottom:0.75rem">
        Found ${movies.length} films${saveList ? ' · Saved to My Lists' : ''}
      </div>
      <div class="ai-list-movies">
        ${movies.map(m => `
          <div class="ai-list-movie-item" onclick="closeModal('aiListModal');showPage('detail',${m.id})">
            ${m.poster_url ? `<img src="${m.poster_url}" alt="" />` : `<div class="ai-list-no-poster">🎞</div>`}
            <div class="ai-list-movie-info">
              <div class="ai-list-movie-title">${escHtml(m.title)}</div>
              <div class="ai-list-movie-meta">${m.release_year || ''} ${m.rating ? '· ★ ' + parseFloat(m.rating).toFixed(1) : ''}</div>
            </div>
          </div>`).join('')}
      </div>`;

    if (saveList) { loadLists(); }
    showToast(saveList ? 'AI list saved!' : 'AI list generated!', 'success');
  } catch (e) {
    resultEl.innerHTML = '';
    errEl.textContent = e.message;
  }
}

/* ─── PROFILE ───────────────────────────────────────────────────────────────── */
async function loadProfile() {
  if (!state.user) { showPage('home'); openModal('loginModal'); return; }
  try {
    const data = await api('/ratings/', 'GET', null, true);
    const ratings = Array.isArray(data) ? data : (data.results || []);
    const container = document.getElementById('myRatings');
    container.innerHTML = '';
    if (ratings.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">⭐</div><p>You haven't rated any films yet.</p></div>`;
      return;
    }
    ratings.forEach(r => {
      const card = buildMovieCard(r.movie);
      const ratingBadge = document.createElement('div');
      ratingBadge.style.cssText = 'position:absolute;top:0.5rem;left:0.5rem;background:var(--gold);color:#1a1000;font-weight:700;font-size:0.78rem;padding:0.2rem 0.5rem;border-radius:6px;z-index:3;';
      ratingBadge.textContent = '★ ' + r.rating;
      card.style.position = 'relative';
      card.appendChild(ratingBadge);
      container.appendChild(card);
    });
  } catch (e) { document.getElementById('myRatings').innerHTML = `<div style="color:var(--red)">${e.message}</div>`; }
}

/* ─── AI CHAT ───────────────────────────────────────────────────────────────── */
async function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  appendChatMsg(msg, 'user');
  const typingEl = appendTyping();
  try {
    const data = await api('/ai/chat/', 'POST', {
      message: msg,
      history: state.chatHistory.slice(-16)
    }, state.user ? true : false);
    typingEl.remove();
    const reply = data.reply || data.message || JSON.stringify(data);
    appendChatMsg(reply, 'assistant');
    state.chatHistory.push({ role: 'user', content: msg });
    state.chatHistory.push({ role: 'assistant', content: reply });
    if (state.chatHistory.length > 40) state.chatHistory = state.chatHistory.slice(-40);
  } catch (e) {
    typingEl.remove();
    appendChatMsg('Sorry, I ran into an issue: ' + e.message, 'assistant');
  }
}

function sendQuickPrompt(prompt) {
  document.getElementById('chatInput').value = prompt;
  sendChat();
}

function askAIAbout(movieId, title) {
  showPage('ai');
  document.getElementById('chatInput').value = `Tell me about "${title}" and why I might love it`;
  sendChat();
}

function appendChatMsg(text, role) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.innerHTML = `<div class="chat-bubble">${escHtml(text).replace(/\n/g, '<br>')}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function appendTyping() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-msg assistant chat-typing';
  div.innerHTML = `<div class="chat-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

/* ─── MODALS ────────────────────────────────────────────────────────────────── */
function openModal(id) { document.getElementById(id).classList.remove('hidden'); document.body.style.overflow = 'hidden'; }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); document.body.style.overflow = ''; }
function closeModalOnBg(event, id) { if (event.target === event.currentTarget) closeModal(id); }
function switchModal(fromId, toId) { closeModal(fromId); openModal(toId); }

/* ─── TOAST ─────────────────────────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, type = '') {
  const el = document.getElementById('toast');
  el.textContent = msg; el.className = 'toast show ' + type;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.classList.remove('show'); }, 3000);
}

/* ─── UTILS ─────────────────────────────────────────────────────────────────── */
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

const LANG_NAMES = {
  en: 'English', hi: 'Hindi', ta: 'Tamil', te: 'Telugu',
  ml: 'Malayalam', kn: 'Kannada', bn: 'Bengali', mr: 'Marathi',
  pa: 'Punjabi', ur: 'Urdu', ko: 'Korean', fr: 'French',
  es: 'Spanish', ja: 'Japanese', zh: 'Chinese', de: 'German',
  it: 'Italian', pt: 'Portuguese', ru: 'Russian', ar: 'Arabic',
  hindi: 'Hindi', tamil: 'Tamil', telugu: 'Telugu',
  malayalam: 'Malayalam', kannada: 'Kannada', bengali: 'Bengali',
  marathi: 'Marathi', punjabi: 'Punjabi', urdu: 'Urdu',
  english: 'English', bhojpuri: 'Bhojpuri', assamese: 'Assamese',
  oriya: 'Odia', nepali: 'Nepali', gujarati: 'Gujarati',
};
function formatLang(code) {
  if (!code) return '';
  return LANG_NAMES[code.toLowerCase()] || code.charAt(0).toUpperCase() + code.slice(1);
}