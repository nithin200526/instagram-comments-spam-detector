/**
 * ShieldPost — Professional Social Media Frontend
 * Handles post creation, comments, spam moderation, and UI state.
 */

const API = '';

// ─── Toast Notifications ────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── Time Formatting ────────────────────────────────────────
function timeAgo(dateStr) {
    const seconds = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h';
    if (seconds < 604800) return Math.floor(seconds / 86400) + 'd';
    return Math.floor(seconds / 2592000) + 'mo';
}

function getInitials(name) {
    return (name || 'A').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Random avatar gradient
const gradients = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)',
    'linear-gradient(135deg, #a18cd1, #fbc2eb)',
    'linear-gradient(135deg, #fccb90, #d57eeb)',
    'linear-gradient(135deg, #e0c3fc, #8ec5fc)',
];

function randomGradient(name) {
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return gradients[Math.abs(hash) % gradients.length];
}

// ─── Image Preview ──────────────────────────────────────────
const fileInput = document.getElementById('postImage');
const fileNameEl = document.getElementById('fileName');
const previewImg = document.getElementById('imagePreview');

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) {
            fileNameEl.textContent = fileInput.files[0].name;
            const reader = new FileReader();
            reader.onload = e => {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
            };
            reader.readAsDataURL(fileInput.files[0]);
        }
    });
}

// ─── Create Post ────────────────────────────────────────────
async function createPost() {
    const btn = document.getElementById('postBtn');
    const imageFile = fileInput?.files[0];

    if (!imageFile) {
        showToast('Please select an image', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('caption', document.getElementById('postCaption').value);
    formData.append('author', document.getElementById('postAuthor').value || 'Anonymous');

    try {
        const res = await fetch(`${API}/api/posts`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error('Failed');
        showToast('Post shared!', 'success');

        // Reset composer
        document.getElementById('postCaption').value = '';
        document.getElementById('postCaption').style.height = 'auto';
        fileInput.value = '';
        fileNameEl.textContent = '';
        previewImg.style.display = 'none';

        loadPosts();
    } catch (err) {
        showToast('Failed to create post', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Post';
    }
}

// ─── Load Posts ─────────────────────────────────────────────
async function loadPosts() {
    try {
        const res = await fetch(`${API}/api/posts`);
        const data = await res.json();
        const container = document.getElementById('postsContainer');
        const emptyState = document.getElementById('emptyState');

        // Clear existing posts
        container.querySelectorAll('.post-card').forEach(p => p.remove());

        if (data.posts.length === 0) {
            emptyState.style.display = 'block';
            return;
        }
        emptyState.style.display = 'none';

        data.posts.forEach(post => {
            container.appendChild(renderPostCard(post));
        });
    } catch (err) {
        console.error('Failed to load posts:', err);
    }
}

// ─── Render Post Card ───────────────────────────────────────
function renderPostCard(post) {
    const el = document.createElement('div');
    el.className = 'post-card';
    el.id = `post-${post.id}`;

    const grad = randomGradient(post.author);
    const commentCount = post.comment_count || 0;
    const hiddenCount = post.hidden_count || 0;

    el.innerHTML = `
        <div class="post-header">
            <div class="post-avatar" style="background:${grad}">${getInitials(post.author)}</div>
            <div class="post-user-info">
                <div class="post-username">
                    ${escapeHtml(post.author)}
                    <span class="verified-badge">✓</span>
                </div>
                <div class="post-time">${timeAgo(post.created_at)}</div>
            </div>
            <button class="post-menu-btn" title="More">⋯</button>
        </div>

        <div class="post-image-container">
            <img src="${post.image_url}" class="post-image" alt="Post" loading="lazy">
        </div>

        <div class="post-actions">
            <button class="post-action-btn" onclick="this.classList.toggle('liked')" title="Like">♡</button>
            <button class="post-action-btn" onclick="document.getElementById('comment-input-${post.id}').focus()" title="Comment">💬</button>
            <button class="post-action-btn" title="Share">↗</button>
            <div class="post-action-spacer"></div>
            <button class="post-action-btn" title="Save">🔖</button>
        </div>

        ${post.caption ? `
            <div class="post-caption">
                <span class="caption-author">${escapeHtml(post.author)}</span>
                <span class="caption-text">${escapeHtml(post.caption)}</span>
            </div>
        ` : ''}

        <div class="comments-section">
            <span class="view-comments-link" id="comment-count-${post.id}">
                ${commentCount > 0 ? `View all ${commentCount} comments` : ''}
            </span>

            <div class="comments-list" id="comments-${post.id}"></div>

            <div class="comment-input-area">
                <input type="text" id="comment-input-${post.id}" placeholder="Add a comment..."
                       autocomplete="off"
                       onkeydown="if(event.key==='Enter' && this.value.trim()) addComment(${post.id})">
                <button class="comment-post-btn" onclick="addComment(${post.id})">Post</button>
            </div>

            <button class="hidden-toggle" id="hidden-toggle-${post.id}"
                    style="${hiddenCount > 0 ? '' : 'display:none'}"
                    onclick="toggleHidden(${post.id})">
                ⚠️ <span id="hidden-count-${post.id}">${hiddenCount}</span> spam comment${hiddenCount !== 1 ? 's' : ''} hidden by AI
            </button>
            <div class="hidden-panel" id="hidden-panel-${post.id}"></div>
        </div>
    `;

    loadComments(post.id);
    return el;
}

// ─── Load Comments ──────────────────────────────────────────
async function loadComments(postId) {
    try {
        const res = await fetch(`${API}/api/posts/${postId}/comments`);
        const data = await res.json();
        const container = document.getElementById(`comments-${postId}`);
        if (!container) return;

        container.innerHTML = '';
        data.comments.forEach(c => container.appendChild(renderComment(c)));

        const countEl = document.getElementById(`comment-count-${postId}`);
        if (countEl) {
            countEl.textContent = data.comments.length > 0
                ? `View all ${data.comments.length} comments` : '';
        }
    } catch (err) { }
}

// ─── Add Comment ────────────────────────────────────────────
async function addComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const text = input.value.trim();
    if (!text) return;

    input.disabled = true;

    try {
        const res = await fetch(`${API}/api/posts/${postId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author: 'User', text }),
        });
        if (!res.ok) throw new Error('Failed');
        const data = await res.json();
        input.value = '';

        const mod = data.moderation;
        if (mod.action === 'hidden') {
            showToast(`🚫 Spam detected (${Math.round(mod.spam_probability * 100)}%) — hidden`, 'warning');
            const toggle = document.getElementById(`hidden-toggle-${postId}`);
            if (toggle) toggle.style.display = '';
            const countEl = document.getElementById(`hidden-count-${postId}`);
            if (countEl) countEl.textContent = parseInt(countEl.textContent || '0') + 1;
            loadHiddenComments(postId);
        } else {
            showToast(`✅ Comment posted (${Math.round((1 - mod.spam_probability) * 100)}% safe)`, 'success');
            loadComments(postId);
        }

        updateSpamBadge();
    } catch (err) {
        showToast('Error posting comment', 'error');
    } finally {
        input.disabled = false;
        input.focus();
    }
}

// ─── Render Comment ─────────────────────────────────────────
function renderComment(c) {
    const el = document.createElement('div');
    el.className = 'comment-item';
    const grad = randomGradient(c.author);
    const isSpammy = c.spam_probability > 0.3;
    const barClass = isSpammy ? 'spam' : 'safe';
    const barWidth = Math.round(c.spam_probability * 100);

    el.innerHTML = `
        <div class="comment-avatar" style="background:${grad}">${getInitials(c.author)}</div>
        <div class="comment-body">
            <span class="comment-author">${escapeHtml(c.author)}</span>
            <span class="comment-text">${escapeHtml(c.text)}</span>
            <div class="comment-footer">
                <span class="comment-time">${timeAgo(c.created_at)}</span>
                <span class="comment-spam-indicator">
                    <span class="confidence-pill">
                        <span class="confidence-pill-fill ${barClass}" style="width:${barWidth}%"></span>
                    </span>
                    ${barWidth}% risk
                </span>
                <button class="btn-ghost comment-action-hide" onclick="hideComment(${c.id}, ${c.post_id})">Hide</button>
            </div>
        </div>
    `;
    return el;
}

// ─── Hidden Comments ────────────────────────────────────────
function toggleHidden(postId) {
    const panel = document.getElementById(`hidden-panel-${postId}`);
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) loadHiddenComments(postId);
}

async function loadHiddenComments(postId) {
    try {
        const res = await fetch(`${API}/api/posts/${postId}/hidden`);
        const data = await res.json();
        const container = document.getElementById(`hidden-panel-${postId}`);
        if (!container) return;

        container.innerHTML = '';
        if (data.comments.length === 0) {
            container.innerHTML = '<div style="padding:12px 16px;font-size:0.82rem;color:var(--text-muted)">No hidden comments</div>';
            return;
        }

        data.comments.forEach(c => {
            const item = document.createElement('div');
            item.className = 'hidden-item';
            item.innerHTML = `
                <div class="hidden-text">${escapeHtml(c.text)}</div>
                <div class="hidden-meta">
                    <span class="badge badge-spam">${Math.round(c.spam_probability * 100)}%</span>
                    <button class="btn btn-success btn-xs" onclick="approveComment(${c.id}, ${postId})">Approve</button>
                </div>
            `;
            container.appendChild(item);
        });
    } catch (err) { }
}

// ─── Override Actions ───────────────────────────────────────
async function approveComment(commentId, postId) {
    try {
        await fetch(`${API}/api/comments/${commentId}/approve`, { method: 'POST' });
        showToast('Comment approved', 'success');
        loadComments(postId);
        loadHiddenComments(postId);
        const el = document.getElementById(`hidden-count-${postId}`);
        if (el) {
            const val = Math.max(0, parseInt(el.textContent || '1') - 1);
            el.textContent = val;
            if (val === 0) {
                const toggle = document.getElementById(`hidden-toggle-${postId}`);
                if (toggle) toggle.style.display = 'none';
            }
        }
        updateSpamBadge();
    } catch (err) {
        showToast('Failed to approve', 'error');
    }
}

async function hideComment(commentId, postId) {
    try {
        await fetch(`${API}/api/comments/${commentId}/hide`, { method: 'POST' });
        showToast('Comment hidden', 'warning');
        loadComments(postId);
        const toggle = document.getElementById(`hidden-toggle-${postId}`);
        if (toggle) toggle.style.display = '';
        const el = document.getElementById(`hidden-count-${postId}`);
        if (el) el.textContent = parseInt(el.textContent || '0') + 1;
        loadHiddenComments(postId);
        updateSpamBadge();
    } catch (err) {
        showToast('Failed to hide', 'error');
    }
}

// ─── Spam Badge Count ───────────────────────────────────────
async function updateSpamBadge() {
    try {
        const res = await fetch(`${API}/api/analytics`);
        const data = await res.json();
        const badge = document.getElementById('spamBadge');
        if (badge && data.hidden > 0) {
            badge.textContent = data.hidden;
            badge.style.display = '';
        } else if (badge) {
            badge.style.display = 'none';
        }
    } catch (e) { }
}

// ─── Init ───────────────────────────────────────────────────
loadPosts();
updateSpamBadge();
