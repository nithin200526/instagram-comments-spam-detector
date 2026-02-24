/**
 * ShieldPost — Production-Ready Frontend
 * All interactions functional: like, save, share, delete, comment moderation.
 */

const API = '';

// ─── State ──────────────────────────────────────────
const state = { likedPosts: new Set(), savedPosts: new Set() };

// ─── Toast ──────────────────────────────────────────
function toast(msg, type = 'info') {
    const c = document.getElementById('toasts');
    if (!c) return;
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    c.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// ─── Utils ──────────────────────────────────────────
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function timeAgo(d) {
    const s = Math.floor((Date.now() - new Date(d)) / 1000);
    if (s < 60) return 'now';
    if (s < 3600) return Math.floor(s / 60) + 'm';
    if (s < 86400) return Math.floor(s / 3600) + 'h';
    if (s < 604800) return Math.floor(s / 86400) + 'd';
    return Math.floor(s / 2592000) + 'mo';
}

function initials(n) { return (n || 'A').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2); }

const grads = [
    'linear-gradient(135deg,#667eea,#764ba2)', 'linear-gradient(135deg,#f093fb,#f5576c)',
    'linear-gradient(135deg,#4facfe,#00f2fe)', 'linear-gradient(135deg,#43e97b,#38f9d7)',
    'linear-gradient(135deg,#fa709a,#fee140)', 'linear-gradient(135deg,#a18cd1,#fbc2eb)',
    'linear-gradient(135deg,#fccb90,#d57eeb)', 'linear-gradient(135deg,#e0c3fc,#8ec5fc)',
];

function grad(name) {
    let h = 0;
    for (let i = 0; i < (name || '').length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
    return grads[Math.abs(h) % grads.length];
}

// ─── Emojis ─────────────────────────────────────────
const emojis = ['😊', '😂', '❤️', '🔥', '👏', '💯', '😍', '🙌', '✨', '🎉', '👀', '💪', '🙏', '😎', '🤩'];
function insertEmoji() {
    const ta = document.getElementById('postCaption');
    if (!ta) return;
    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
    ta.value += emoji;
    ta.focus();
}

// ─── Image Preview ──────────────────────────────────
const fileInput = document.getElementById('postImage');
const fileLabel = document.getElementById('fileName');
const imgPreview = document.getElementById('imgPreview');

if (fileInput) {
    fileInput.addEventListener('change', () => {
        const f = fileInput.files[0];
        if (f) {
            fileLabel.textContent = f.name;
            const r = new FileReader();
            r.onload = e => { imgPreview.src = e.target.result; imgPreview.style.display = 'block'; };
            r.readAsDataURL(f);
        }
    });
}

// Create nav click scrolls to composer
const navCreate = document.getElementById('navCreate');
if (navCreate) {
    navCreate.addEventListener('click', e => {
        e.preventDefault();
        const c = document.getElementById('composer');
        if (c) { c.scrollIntoView({ behavior: 'smooth' }); document.getElementById('postCaption').focus(); }
    });
}

// ─── Lightbox ───────────────────────────────────────
function openLightbox(src) {
    const lb = document.getElementById('lightbox');
    document.getElementById('lightboxImg').src = src;
    lb.classList.add('open');
}
function closeLightbox() { document.getElementById('lightbox').classList.remove('open'); }
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });

// ─── Confirm Dialog ─────────────────────────────────
let confirmCallback = null;
function showConfirm(title, msg, cb) {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMsg').textContent = msg;
    confirmCallback = cb;
    document.getElementById('confirmOverlay').classList.add('open');
}
function closeConfirm() { document.getElementById('confirmOverlay').classList.remove('open'); confirmCallback = null; }
document.getElementById('confirmAction')?.addEventListener('click', () => {
    if (confirmCallback) confirmCallback();
    closeConfirm();
});

// ─── Create Post ────────────────────────────────────
async function createPost() {
    const btn = document.getElementById('postBtn');
    if (!fileInput?.files[0]) { toast('Please select an image', 'warn'); return; }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';

    const fd = new FormData();
    fd.append('image', fileInput.files[0]);
    fd.append('caption', document.getElementById('postCaption').value);
    fd.append('author', document.getElementById('postAuthor').value || 'Anonymous');

    try {
        const r = await fetch(`${API}/api/posts`, { method: 'POST', body: fd });
        if (!r.ok) throw 0;
        toast('Post shared!', 'ok');
        document.getElementById('postCaption').value = '';
        document.getElementById('postCaption').style.height = 'auto';
        fileInput.value = '';
        fileLabel.textContent = '';
        imgPreview.style.display = 'none';
        loadPosts();
    } catch { toast('Failed to create post', 'err'); }
    finally { btn.disabled = false; btn.textContent = 'Post'; }
}

// ─── Load Posts ─────────────────────────────────────
async function loadPosts() {
    try {
        const r = await fetch(`${API}/api/posts`);
        const d = await r.json();
        const c = document.getElementById('postsContainer');
        const empty = document.getElementById('emptyState');

        c.querySelectorAll('.post').forEach(p => p.remove());

        if (!d.posts.length) { empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        d.posts.forEach(p => c.appendChild(renderPost(p)));
    } catch (e) { console.error('Load posts error:', e); }
}

// ─── Render Post ────────────────────────────────────
function renderPost(p) {
    const el = document.createElement('div');
    el.className = 'post';
    el.id = `post-${p.id}`;

    const g = grad(p.author);
    const liked = state.likedPosts.has(p.id);
    const saved = state.savedPosts.has(p.id);
    const likes = p.likes || 0;

    el.innerHTML = `
        <div class="post-head">
            <div class="post-av" style="background:${g}">${initials(p.author)}</div>
            <div class="post-info">
                <div class="post-author">${esc(p.author)} <span class="v-badge">✓</span></div>
                <div class="post-ts">${timeAgo(p.created_at)}</div>
            </div>
            <div class="post-menu">
                <button class="post-menu-btn" onclick="toggleMenu(${p.id})">⋯</button>
                <div class="post-dropdown" id="menu-${p.id}">
                    <button class="post-dropdown-item" onclick="copyLink(${p.id})">📋 Copy Link</button>
                    <button class="post-dropdown-item" onclick="sharePost(${p.id})">↗️ Share</button>
                    <button class="post-dropdown-item danger" onclick="confirmDeletePost(${p.id})">🗑️ Delete Post</button>
                </div>
            </div>
        </div>

        <div class="post-img">
            <img src="${p.image_url}" alt="Post" loading="lazy" onclick="openLightbox('${p.image_url}')">
        </div>

        <div class="post-bar">
            <button class="act-btn ${liked ? 'liked' : ''}" id="like-btn-${p.id}"
                    onclick="toggleLike(${p.id})" title="Like">${liked ? '❤️' : '🤍'}</button>
            <button class="act-btn" onclick="focusComment(${p.id})" title="Comment">💬</button>
            <button class="act-btn" onclick="sharePost(${p.id})" title="Share">↗️</button>
            <div class="spacer"></div>
            <button class="act-btn ${saved ? 'saved' : ''}" id="save-btn-${p.id}"
                    onclick="toggleSave(${p.id})" title="Save">${saved ? '🔖' : '🏷️'}</button>
        </div>

        <div class="post-likes" id="likes-${p.id}">${likes > 0 ? `${likes.toLocaleString()} like${likes !== 1 ? 's' : ''}` : ''}</div>

        ${p.caption ? `<div class="post-caption-area"><span class="cap-author">${esc(p.author)}</span><span class="cap-text">${esc(p.caption)}</span></div>` : ''}

        <div class="comments-area">
            <span class="view-all-link" id="count-${p.id}">${(p.comment_count || 0) > 0 ? `View all ${p.comment_count} comments` : ''}</span>
            <div class="c-list" id="clist-${p.id}"></div>

            <div class="c-input-bar">
                <button class="emoji-btn" onclick="insertCommentEmoji(${p.id})">😊</button>
                <input type="text" id="cinput-${p.id}" placeholder="Add a comment..." autocomplete="off"
                       onkeydown="if(event.key==='Enter'&&this.value.trim())addComment(${p.id})">
                <button class="c-submit-btn" onclick="addComment(${p.id})">Post</button>
            </div>

            <button class="spam-toggle" id="spam-toggle-${p.id}" style="${(p.hidden_count || 0) > 0 ? '' : 'display:none'}"
                    onclick="toggleSpam(${p.id})">
                ⚠️ <span id="spam-count-${p.id}">${p.hidden_count || 0}</span> spam comment${(p.hidden_count || 0) !== 1 ? 's' : ''} hidden
            </button>
            <div class="spam-panel" id="spam-panel-${p.id}"></div>
        </div>
    `;

    loadComments(p.id);
    return el;
}

// ─── Post Menu ──────────────────────────────────────
function toggleMenu(id) {
    // Close all others
    document.querySelectorAll('.post-dropdown.open').forEach(d => {
        if (d.id !== `menu-${id}`) d.classList.remove('open');
    });
    document.getElementById(`menu-${id}`).classList.toggle('open');
}

// Close menus on outside click
document.addEventListener('click', e => {
    if (!e.target.closest('.post-menu')) {
        document.querySelectorAll('.post-dropdown.open').forEach(d => d.classList.remove('open'));
    }
});

// ─── Like ───────────────────────────────────────────
async function toggleLike(id) {
    const liked = state.likedPosts.has(id);
    const endpoint = liked ? 'unlike' : 'like';
    try {
        const r = await fetch(`${API}/api/posts/${id}/${endpoint}`, { method: 'POST' });
        const d = await r.json();
        if (liked) state.likedPosts.delete(id); else state.likedPosts.add(id);

        const btn = document.getElementById(`like-btn-${id}`);
        btn.className = `act-btn ${!liked ? 'liked' : ''}`;
        btn.textContent = !liked ? '❤️' : '🤍';

        const lk = document.getElementById(`likes-${id}`);
        lk.textContent = d.likes > 0 ? `${d.likes.toLocaleString()} like${d.likes !== 1 ? 's' : ''}` : '';
    } catch { toast('Error', 'err'); }
}

// ─── Save ───────────────────────────────────────────
async function toggleSave(id) {
    try {
        const r = await fetch(`${API}/api/posts/${id}/save`, { method: 'POST' });
        const d = await r.json();
        const btn = document.getElementById(`save-btn-${id}`);
        if (d.saved) {
            state.savedPosts.add(id);
            btn.className = 'act-btn saved';
            btn.textContent = '🔖';
            toast('Post saved', 'ok');
        } else {
            state.savedPosts.delete(id);
            btn.className = 'act-btn';
            btn.textContent = '🏷️';
            toast('Post unsaved', 'info');
        }
    } catch { toast('Error', 'err'); }
}

// ─── Share / Copy Link ──────────────────────────────
function sharePost(postId) {
    const url = `${window.location.origin}/#post-${postId}`;
    navigator.clipboard.writeText(url).then(() => {
        toast('Link copied to clipboard!', 'ok');
    }).catch(() => {
        toast(`Share link: ${url}`, 'info');
    });
    // Close menu if open
    document.querySelectorAll('.post-dropdown.open').forEach(d => d.classList.remove('open'));
}

function copyLink(postId) { sharePost(postId); }

// ─── Delete Post ────────────────────────────────────
function confirmDeletePost(id) {
    document.querySelectorAll('.post-dropdown.open').forEach(d => d.classList.remove('open'));
    showConfirm('Delete Post?', 'This will permanently delete this post and all its comments.', async () => {
        try {
            const r = await fetch(`${API}/api/posts/${id}`, { method: 'DELETE' });
            if (!r.ok) throw 0;
            const el = document.getElementById(`post-${id}`);
            if (el) { el.style.transition = 'all 0.3s'; el.style.opacity = '0'; el.style.transform = 'scale(0.95)'; setTimeout(() => el.remove(), 300); }
            toast('Post deleted', 'ok');
            updateSpamBadge();
        } catch { toast('Failed to delete', 'err'); }
    });
}

// ─── Focus Comment Input ────────────────────────────
function focusComment(id) { document.getElementById(`cinput-${id}`)?.focus(); }

// ─── Emoji in Comment ───────────────────────────────
function insertCommentEmoji(id) {
    const inp = document.getElementById(`cinput-${id}`);
    if (inp) { inp.value += emojis[Math.floor(Math.random() * emojis.length)]; inp.focus(); }
}

// ─── Load Comments ──────────────────────────────────
async function loadComments(id) {
    try {
        const r = await fetch(`${API}/api/posts/${id}/comments`);
        const d = await r.json();
        const c = document.getElementById(`clist-${id}`);
        if (!c) return;
        c.innerHTML = '';
        d.comments.forEach(cm => c.appendChild(renderComment(cm)));

        const cnt = document.getElementById(`count-${id}`);
        if (cnt) cnt.textContent = d.comments.length > 0 ? `View all ${d.comments.length} comments` : '';
    } catch { }
}

// ─── Add Comment ────────────────────────────────────
async function addComment(id) {
    const inp = document.getElementById(`cinput-${id}`);
    const txt = inp.value.trim();
    if (!txt) return;
    inp.disabled = true;

    try {
        const r = await fetch(`${API}/api/posts/${id}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author: document.getElementById('postAuthor')?.value || 'User', text: txt }),
        });
        if (!r.ok) throw 0;
        const d = await r.json();
        inp.value = '';

        const mod = d.moderation;
        if (mod.action === 'hidden') {
            toast(`🚫 Spam (${Math.round(mod.spam_probability * 100)}%) — hidden by AI`, 'warn');
            const toggle = document.getElementById(`spam-toggle-${id}`);
            if (toggle) toggle.style.display = '';
            const cnt = document.getElementById(`spam-count-${id}`);
            if (cnt) cnt.textContent = parseInt(cnt.textContent || '0') + 1;
            loadSpam(id);
        } else {
            const safe = Math.round((1 - mod.spam_probability) * 100);
            toast(`✅ Posted (${safe}% safe)`, 'ok');
            loadComments(id);
        }
        updateSpamBadge();
    } catch { toast('Error posting comment', 'err'); }
    finally { inp.disabled = false; inp.focus(); }
}

// ─── Render Comment ─────────────────────────────────
function renderComment(c) {
    const el = document.createElement('div');
    el.className = 'c-item';
    el.id = `comment-${c.id}`;
    const g = grad(c.author);
    const prob = Math.round((c.spam_probability || 0) * 100);
    const riskClass = prob > 60 ? 'bad' : prob > 30 ? 'warn' : 'ok';
    const likes = c.likes || 0;

    el.innerHTML = `
        <div class="c-av" style="background:${g}">${initials(c.author)}</div>
        <div class="c-body">
            <span class="c-author">${esc(c.author)}</span>
            <span class="c-text">${esc(c.text)}</span>
            <div class="c-meta">
                <span class="c-time">${timeAgo(c.created_at)}</span>
                <span class="risk-bar">
                    <span class="risk-track"><span class="risk-fill ${riskClass}" style="width:${prob}%"></span></span>
                    ${prob}%
                </span>
                ${likes > 0 ? `<span class="c-time">${likes} ♥</span>` : ''}
                <span class="c-actions">
                    <button class="c-like-btn" onclick="likeComment(${c.id})" title="Like">♡</button>
                    <button class="c-del-btn" onclick="confirmDeleteComment(${c.id}, ${c.post_id})" title="Delete">✕</button>
                    <button class="c-del-btn" onclick="hideComment(${c.id}, ${c.post_id})" title="Hide">Hide</button>
                </span>
            </div>
        </div>
    `;
    return el;
}

// ─── Like Comment ───────────────────────────────────
async function likeComment(id) {
    try {
        await fetch(`${API}/api/comments/${id}/like`, { method: 'POST' });
    } catch { }
}

// ─── Delete Comment ─────────────────────────────────
function confirmDeleteComment(cId, pId) {
    showConfirm('Delete Comment?', 'This comment will be permanently removed.', async () => {
        try {
            await fetch(`${API}/api/comments/${cId}`, { method: 'DELETE' });
            const el = document.getElementById(`comment-${cId}`);
            if (el) { el.style.opacity = '0'; setTimeout(() => { el.remove(); }, 200); }
            toast('Comment deleted', 'ok');
        } catch { toast('Failed to delete', 'err'); }
    });
}

// ─── Hide Comment ───────────────────────────────────
async function hideComment(cId, pId) {
    try {
        await fetch(`${API}/api/comments/${cId}/hide`, { method: 'POST' });
        toast('Comment hidden', 'warn');
        loadComments(pId);
        const t = document.getElementById(`spam-toggle-${pId}`);
        if (t) t.style.display = '';
        const c = document.getElementById(`spam-count-${pId}`);
        if (c) c.textContent = parseInt(c.textContent || '0') + 1;
        loadSpam(pId);
        updateSpamBadge();
    } catch { toast('Failed', 'err'); }
}

// ─── Spam Panel ─────────────────────────────────────
function toggleSpam(id) {
    const p = document.getElementById(`spam-panel-${id}`);
    p.classList.toggle('open');
    if (p.classList.contains('open')) loadSpam(id);
}

async function loadSpam(id) {
    try {
        const r = await fetch(`${API}/api/posts/${id}/hidden`);
        const d = await r.json();
        const c = document.getElementById(`spam-panel-${id}`);
        if (!c) return;
        c.innerHTML = '';
        if (!d.comments.length) {
            c.innerHTML = '<div style="padding:12px 16px;font-size:0.82rem;color:var(--text-muted)">No hidden comments</div>';
            return;
        }
        d.comments.forEach(cm => {
            const item = document.createElement('div');
            item.className = 'spam-item';
            item.innerHTML = `
                <span class="spam-text">${esc(cm.text)}</span>
                <span class="pill pill-spam">${Math.round(cm.spam_probability * 100)}%</span>
                <button class="btn btn-success btn-xs" onclick="approveComment(${cm.id}, ${id})">Approve</button>
                <button class="btn btn-danger btn-xs" onclick="deleteSpamComment(${cm.id}, ${id})">Delete</button>
            `;
            c.appendChild(item);
        });
    } catch { }
}

async function approveComment(cId, pId) {
    try {
        await fetch(`${API}/api/comments/${cId}/approve`, { method: 'POST' });
        toast('Comment approved', 'ok');
        loadComments(pId);
        loadSpam(pId);
        const c = document.getElementById(`spam-count-${pId}`);
        if (c) {
            const v = Math.max(0, parseInt(c.textContent || '1') - 1);
            c.textContent = v;
            if (v === 0) document.getElementById(`spam-toggle-${pId}`).style.display = 'none';
        }
        updateSpamBadge();
    } catch { toast('Failed', 'err'); }
}

async function deleteSpamComment(cId, pId) {
    try {
        await fetch(`${API}/api/comments/${cId}`, { method: 'DELETE' });
        toast('Spam deleted', 'ok');
        loadSpam(pId);
        const c = document.getElementById(`spam-count-${pId}`);
        if (c) {
            const v = Math.max(0, parseInt(c.textContent || '1') - 1);
            c.textContent = v;
            if (v === 0) document.getElementById(`spam-toggle-${pId}`).style.display = 'none';
        }
        updateSpamBadge();
    } catch { toast('Failed', 'err'); }
}

// ─── Spam Badge ─────────────────────────────────────
async function updateSpamBadge() {
    try {
        const r = await fetch(`${API}/api/analytics`);
        const d = await r.json();
        const b = document.getElementById('spamBadge');
        if (b && d.hidden > 0) { b.textContent = d.hidden; b.style.display = ''; }
        else if (b) { b.style.display = 'none'; }
    } catch { }
}

// ─── Init ───────────────────────────────────────────
loadPosts();
updateSpamBadge();
