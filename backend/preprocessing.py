"""
NLP-powered text preprocessing and feature extraction for spam detection.

Two-layer approach:
  1. Text cleaning (for TF-IDF lexical features)
  2. NLP feature extraction (semantic understanding):
     - VADER Sentiment Analysis (emotional tone)
     - Linguistic features (writing style, grammar patterns)
     - Behavioral signals (urgency, self-promotion, manipulation)
"""

import re
import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data (runs once, silent)
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4", "vader_lexicon"]:
    nltk.download(resource, quiet=True)

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))
_vader = SentimentIntensityAnalyzer()

# ─── Compiled Regex Patterns ─────────────────────────────────────────────────
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)
_SPECIAL_RE = re.compile(r"[^a-zA-Z0-9\s]")
_WHITESPACE_RE = re.compile(r"\s+")
_MONEY_RE = re.compile(r"\$\d+|\d+\s*(?:dollars|usd|euros|btc|bitcoin)", re.IGNORECASE)
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#\w+")
_REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}")
_ALL_CAPS_WORD_RE = re.compile(r"\b[A-Z]{2,}\b")

# Spam-indicative phrase patterns (understood semantically)
_URGENCY_PHRASES = re.compile(
    r"\b(hurry|act now|limited time|don.t miss|last chance|expires|urgent|asap|right now|immediately)\b",
    re.IGNORECASE,
)
_PROMO_PHRASES = re.compile(
    r"\b(check out|visit|click|subscribe|sub4sub|follow me|check my|my channel|my page|my profile|my bio|link in bio)\b",
    re.IGNORECASE,
)
_INCENTIVE_PHRASES = re.compile(
    r"\b(free|win|winner|giveaway|gift card|prize|reward|bonus|discount|offer|deal|earn|income|profit|rich)\b",
    re.IGNORECASE,
)
_COMMAND_PHRASES = re.compile(
    r"\b(click here|tap here|go to|check this|see this|look at this|open this|watch this)\b",
    re.IGNORECASE,
)


# ─── Text Cleaning (for TF-IDF) ──────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """
    Clean text for TF-IDF vectorization.
    Steps: remove URLs -> remove emojis -> remove punctuation
    -> lowercase -> tokenize -> remove stopwords -> lemmatize
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    text = _URL_RE.sub("", text)
    text = _EMOJI_RE.sub("", text)
    text = _SPECIAL_RE.sub(" ", text)
    text = text.lower()

    tokens = word_tokenize(text)
    tokens = [
        _lemmatizer.lemmatize(t)
        for t in tokens
        if t not in _stop_words and len(t) > 1
    ]

    return " ".join(tokens)


# ─── NLP Feature Extraction (semantic understanding) ─────────────────────────

def extract_nlp_features(text: str) -> dict:
    """
    Extract NLP features that capture the *meaning* and *intent* of a comment.

    Feature groups:
      1. Sentiment (VADER) — emotional tone / manipulation detection
      2. Style — writing patterns (caps, punctuation, length)
      3. Behavioral — self-promotion, urgency, incentives, commands
      4. Linguistic — vocabulary richness, readability, coherence
    """
    if not isinstance(text, str) or not text.strip():
        return _empty_features()

    raw = text
    raw_lower = raw.lower()
    chars = list(raw)
    words = word_tokenize(raw)
    words_lower = [w.lower() for w in words]
    sentences = sent_tokenize(raw)

    n_chars = max(len(raw), 1)
    n_words = max(len(words), 1)
    n_sentences = max(len(sentences), 1)

    # ── 1. Sentiment (VADER) ──────────────────────
    sentiment = _vader.polarity_scores(raw)

    # ── 2. Style Features ─────────────────────────
    n_uppercase = sum(1 for c in chars if c.isupper())
    n_exclamation = raw.count("!")
    n_question = raw.count("?")
    n_dots = raw.count(".")
    n_urls = len(_URL_RE.findall(raw))
    n_emojis = len(_EMOJI_RE.findall(raw))
    n_mentions = len(_MENTION_RE.findall(raw))
    n_hashtags = len(_HASHTAG_RE.findall(raw))
    n_money_refs = len(_MONEY_RE.findall(raw))
    n_repeated = len(_REPEATED_CHAR_RE.findall(raw))
    n_caps_words = len(_ALL_CAPS_WORD_RE.findall(raw))

    # ── 3. Behavioral / Intent Features ───────────
    n_urgency = len(_URGENCY_PHRASES.findall(raw))
    n_promo = len(_PROMO_PHRASES.findall(raw))
    n_incentive = len(_INCENTIVE_PHRASES.findall(raw))
    n_commands = len(_COMMAND_PHRASES.findall(raw))

    # ── 4. Linguistic Features ────────────────────
    unique_words = set(words_lower)
    vocab_richness = len(unique_words) / n_words  # type-token ratio
    avg_word_length = sum(len(w) for w in words) / n_words
    avg_sentence_length = n_words / n_sentences

    # Stopword ratio — spammers tend to use fewer stopwords
    n_stopwords = sum(1 for w in words_lower if w in _stop_words)
    stopword_ratio = n_stopwords / n_words

    # Punctuation density
    n_punct = sum(1 for c in chars if not c.isalnum() and not c.isspace())
    punct_density = n_punct / n_chars

    return {
        # Sentiment (4 features)
        "sentiment_pos": sentiment["pos"],
        "sentiment_neg": sentiment["neg"],
        "sentiment_neu": sentiment["neu"],
        "sentiment_compound": sentiment["compound"],

        # Style (12 features)
        "caps_ratio": n_uppercase / n_chars,
        "exclamation_count": min(n_exclamation, 10),
        "question_count": min(n_question, 5),
        "url_count": min(n_urls, 5),
        "emoji_count": min(n_emojis, 10),
        "mention_count": min(n_mentions, 5),
        "hashtag_count": min(n_hashtags, 10),
        "money_ref_count": min(n_money_refs, 5),
        "repeated_char_count": min(n_repeated, 5),
        "caps_word_count": min(n_caps_words, 10),
        "char_count": min(n_chars / 500, 1.0),  # normalized
        "word_count": min(n_words / 100, 1.0),  # normalized

        # Behavioral / Intent (4 features)
        "urgency_score": min(n_urgency, 5),
        "promo_score": min(n_promo, 5),
        "incentive_score": min(n_incentive, 5),
        "command_score": min(n_commands, 5),

        # Linguistic (5 features)
        "vocab_richness": vocab_richness,
        "avg_word_length": min(avg_word_length / 15, 1.0),
        "avg_sentence_length": min(avg_sentence_length / 50, 1.0),
        "stopword_ratio": stopword_ratio,
        "punct_density": punct_density,
    }


def _empty_features() -> dict:
    """Return zeroed feature dict for empty text."""
    keys = [
        "sentiment_pos", "sentiment_neg", "sentiment_neu", "sentiment_compound",
        "caps_ratio", "exclamation_count", "question_count", "url_count",
        "emoji_count", "mention_count", "hashtag_count", "money_ref_count",
        "repeated_char_count", "caps_word_count", "char_count", "word_count",
        "urgency_score", "promo_score", "incentive_score", "command_score",
        "vocab_richness", "avg_word_length", "avg_sentence_length",
        "stopword_ratio", "punct_density",
    ]
    return {k: 0.0 for k in keys}


# ─── Feature Names (for model training) ──────────────────────────────────────
NLP_FEATURE_NAMES = list(_empty_features().keys())
