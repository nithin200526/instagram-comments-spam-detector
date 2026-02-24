"""
FastAPI route definitions for the social media platform.
Handles posts, comments, moderation, and analytics.
"""

import os
import uuid
import shutil
from collections import Counter
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from backend import database as db
from backend.model import predict_spam, get_threshold, set_threshold
from backend.preprocessing import preprocess_text

router = APIRouter(prefix="/api")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Pydantic Models ─────────────────────────────────────────────────────────

class CommentRequest(BaseModel):
    author: str = "Anonymous"
    text: str

class ThresholdRequest(BaseModel):
    threshold: float


# ─── Posts ────────────────────────────────────────────────────────────────────

@router.get("/posts")
def list_posts():
    posts = db.get_posts()
    for post in posts:
        post["comment_count"] = len(db.get_visible_comments(post["id"]))
        post["hidden_count"] = len(db.get_hidden_comments(post["id"]))
    return {"posts": posts}


@router.post("/posts")
async def create_post(
    image: UploadFile = File(...),
    caption: str = Form(""),
    author: str = Form("Anonymous"),
):
    # Save uploaded image
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        content = await image.read()
        f.write(content)

    image_url = f"/static/uploads/{filename}"
    post = db.create_post(image_url=image_url, caption=caption, author=author)
    return {"post": post}


# ─── Comments ─────────────────────────────────────────────────────────────────

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"comments": db.get_visible_comments(post_id)}


@router.post("/posts/{post_id}/comments")
def add_comment(post_id: int, body: CommentRequest):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Comment text is required")

    # AI moderation
    result = predict_spam(body.text)

    comment = db.create_comment(
        post_id=post_id,
        author=body.author or "Anonymous",
        text=body.text,
        is_spam=result["is_spam"],
        confidence=result["confidence"],
        spam_probability=result["spam_probability"],
        is_hidden=result["should_hide"],
    )

    return {
        "comment": comment,
        "moderation": {
            "label": result["label"],
            "confidence": result["confidence"],
            "spam_probability": result["spam_probability"],
            "action": "hidden" if result["should_hide"] else "approved",
        },
    }


@router.get("/posts/{post_id}/hidden")
def get_hidden(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"comments": db.get_hidden_comments(post_id)}


# ─── Moderation Overrides ────────────────────────────────────────────────────

@router.post("/comments/{comment_id}/approve")
def approve(comment_id: int):
    comment = db.approve_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"comment": comment}


@router.post("/comments/{comment_id}/hide")
def hide(comment_id: int):
    comment = db.hide_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"comment": comment}


# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/analytics")
def analytics():
    data = db.get_analytics()

    # Extract top spam keywords
    keywords = []
    for text in data["spam_texts"]:
        cleaned = preprocess_text(text)
        keywords.extend(cleaned.split())

    keyword_counts = Counter(keywords).most_common(15)

    return {
        "total": data["total"],
        "spam": data["spam"],
        "legit": data["legit"],
        "hidden": data["hidden"],
        "spam_percentage": data["spam_percentage"],
        "confidences": data["confidences"],
        "top_keywords": [{"word": w, "count": c} for w, c in keyword_counts],
    }


# ─── Settings ─────────────────────────────────────────────────────────────────

@router.get("/settings")
def get_settings():
    return {"threshold": get_threshold()}


@router.put("/settings/threshold")
def update_threshold(body: ThresholdRequest):
    set_threshold(body.threshold)
    return {"threshold": get_threshold()}
