"""
SQLite database layer for the social media platform.
Tables: posts, comments, likes
"""

import sqlite3
import os
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Use /tmp on Vercel (serverless), local data/ dir otherwise
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/platform.db"
else:
    DB_PATH = os.path.join(_PROJECT_ROOT, "data", "platform.db")


def get_connection():
    """Get a database connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT NOT NULL,
            caption TEXT DEFAULT '',
            author TEXT DEFAULT 'Anonymous',
            likes INTEGER DEFAULT 0,
            saved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author TEXT DEFAULT 'Anonymous',
            text TEXT NOT NULL,
            is_spam INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.0,
            spam_probability REAL DEFAULT 0.0,
            is_hidden INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """)

    # Migrate existing tables: add new columns if missing
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN saved INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("  Database initialized")


# ─── Posts ────────────────────────────────────────────────────────────────────

def create_post(image_url: str, caption: str = "", author: str = "Anonymous") -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (image_url, caption, author) VALUES (?, ?, ?)",
        (image_url, caption, author),
    )
    conn.commit()
    post_id = cursor.lastrowid
    row = cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row)


def get_posts() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_post(post_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_post(post_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT image_url FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not row:
        conn.close()
        return False
    conn.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    # Try to delete image file
    if row[0]:
        img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), row[0].lstrip("/"))
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass
    return True


def like_post(post_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def unlike_post(post_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE posts SET likes = MAX(0, likes - 1) WHERE id = ?", (post_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_post(post_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE posts SET saved = 1 - saved WHERE id = ?", (post_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Comments ─────────────────────────────────────────────────────────────────

def create_comment(post_id: int, author: str, text: str,
                   is_spam: bool, confidence: float,
                   spam_probability: float, is_hidden: bool) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO comments
           (post_id, author, text, is_spam, confidence, spam_probability, is_hidden)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (post_id, author, text, int(is_spam), confidence, spam_probability, int(is_hidden)),
    )
    conn.commit()
    comment_id = cursor.lastrowid
    row = cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
    conn.close()
    return dict(row)


def get_visible_comments(post_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comments WHERE post_id = ? AND is_hidden = 0 ORDER BY created_at DESC",
        (post_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_hidden_comments(post_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comments WHERE post_id = ? AND is_hidden = 1 ORDER BY created_at DESC",
        (post_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_comment(comment_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE comments SET is_hidden = 0 WHERE id = ?", (comment_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def hide_comment(comment_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE comments SET is_hidden = 1 WHERE id = ?", (comment_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_comment(comment_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT id FROM comments WHERE id = ?", (comment_id,)).fetchone()
    if not row:
        conn.close()
        return False
    conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return True


def like_comment(comment_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?", (comment_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Analytics ────────────────────────────────────────────────────────────────

def get_analytics() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
    spam = conn.execute("SELECT COUNT(*) FROM comments WHERE is_spam = 1").fetchone()[0]
    legit = total - spam
    hidden = conn.execute("SELECT COUNT(*) FROM comments WHERE is_hidden = 1").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM comments WHERE is_hidden = 0 AND is_spam = 1").fetchone()[0]
    total_posts = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    total_likes = conn.execute("SELECT COALESCE(SUM(likes), 0) FROM posts").fetchone()[0]

    confidences = conn.execute("SELECT spam_probability FROM comments").fetchall()
    confidence_list = [r[0] for r in confidences]

    spam_texts = conn.execute("SELECT text FROM comments WHERE is_spam = 1").fetchall()
    spam_text_list = [r[0] for r in spam_texts]

    # Recent moderation activity
    recent = conn.execute(
        "SELECT author, text, is_spam, spam_probability, is_hidden, created_at FROM comments ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    recent_list = [dict(r) for r in recent]

    conn.close()

    return {
        "total": total,
        "spam": spam,
        "legit": legit,
        "hidden": hidden,
        "approved_spam": approved,
        "total_posts": total_posts,
        "total_likes": total_likes,
        "spam_percentage": round((spam / total * 100) if total > 0 else 0, 1),
        "confidences": confidence_list,
        "spam_texts": spam_text_list,
        "recent_activity": recent_list,
    }
