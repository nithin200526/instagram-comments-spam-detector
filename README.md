# 🛡️ ShieldPost — AI Social Media Platform

An AI-powered mini social media platform with **real-time spam comment moderation**, built with FastAPI + vanilla HTML/CSS/JS + scikit-learn.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📸 **Post Creation** | Upload images with captions |
| 💬 **Real-time Moderation** | Every comment auto-analyzed by ML before display |
| 🚫 **Auto-Hide Spam** | Comments above threshold are hidden automatically |
| ✅ **Manual Override** | Approve hidden comments or hide visible ones |
| 📊 **Dashboard** | Pie chart, keyword bar chart, confidence histogram |
| ⚙️ **Adjustable Threshold** | Slide to control sensitivity |

## 🚀 Quick Start

```bash
cd instagram-spam-detector

# Install dependencies
pip install -r requirements.txt

# Run the server (trains model on first launch)
python main.py
```

Open **http://localhost:8000** in your browser.

## 📂 Architecture

```
instagram-spam-detector/
├── main.py                  # FastAPI entrypoint
├── requirements.txt
├── backend/
│   ├── database.py          # SQLite (posts + comments)
│   ├── preprocessing.py     # Text cleaning pipeline
│   ├── model.py             # TF-IDF + Logistic Regression
│   └── routes.py            # API endpoints
├── static/
│   ├── index.html           # Social feed page
│   ├── dashboard.html       # Analytics dashboard
│   ├── styles.css            # Dark theme
│   ├── app.js               # Frontend logic
│   └── uploads/             # User-uploaded images
├── models/                  # Saved ML artifacts
└── data/                    # SQLite database
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts` | List all posts |
| `POST` | `/api/posts` | Create post (multipart) |
| `GET` | `/api/posts/{id}/comments` | Visible comments |
| `POST` | `/api/posts/{id}/comments` | Add comment (auto-moderated) |
| `GET` | `/api/posts/{id}/hidden` | Hidden spam comments |
| `POST` | `/api/comments/{id}/approve` | Approve hidden comment |
| `POST` | `/api/comments/{id}/hide` | Hide visible comment |
| `GET` | `/api/analytics` | Dashboard data |
| `GET` | `/api/settings` | Current threshold |
| `PUT` | `/api/settings/threshold` | Update threshold |

## 🧠 ML Model

- **Vectorizer:** TF-IDF with (1,2)-grams, 5000 features
- **Classifier:** Logistic Regression
- **Preprocessing:** URL removal, emoji removal, lowercasing, stopword removal, lemmatization
- **Threshold:** Adjustable (default 80%)

## 🛠️ Tech Stack

Python · FastAPI · Uvicorn · scikit-learn · NLTK · SQLite · Chart.js · Vanilla HTML/CSS/JS
