"""
Text preprocessing pipeline for spam detection.
Handles: URL removal, emoji removal, special char cleanup,
lowercasing, tokenization, stopword removal, and lemmatization.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (runs once)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# Initialize
_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))

# ─── Regex Patterns ──────────────────────────────────────────────────────────
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental
    "\U0001FA00-\U0001FA6F"  # chess
    "\U0001FA70-\U0001FAFF"  # extended-A
    "\U00002702-\U000027B0"
    "]+",
    flags=re.UNICODE,
)
SPECIAL_CHARS_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline for a single text string.
    
    Steps:
        1. Remove URLs
        2. Remove emojis
        3. Remove special characters
        4. Lowercase
        5. Tokenize
        6. Remove stopwords
        7. Lemmatize
        8. Rejoin
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned, preprocessed text string
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # 1. Remove URLs
    text = URL_PATTERN.sub("", text)
    
    # 2. Remove emojis
    text = EMOJI_PATTERN.sub("", text)
    
    # 3. Remove special characters (keep alphanumeric + spaces)
    text = SPECIAL_CHARS_PATTERN.sub(" ", text)
    
    # 4. Lowercase
    text = text.lower()
    
    # 5. Tokenize
    tokens = word_tokenize(text)
    
    # 6. Remove stopwords + 7. Lemmatize
    tokens = [
        _lemmatizer.lemmatize(token)
        for token in tokens
        if token not in _stop_words and len(token) > 1
    ]
    
    # 8. Rejoin
    return " ".join(tokens)


def preprocess_dataframe(df, text_column="CONTENT", output_column="cleaned_text"):
    """
    Apply preprocessing to an entire DataFrame.
    
    Args:
        df: pandas DataFrame containing the text data
        text_column: Name of the column with raw text
        output_column: Name for the new preprocessed column
        
    Returns:
        DataFrame with new preprocessed column added
    """
    df = df.copy()
    df[output_column] = df[text_column].apply(preprocess_text)
    return df


if __name__ == "__main__":
    # Quick test
    test_cases = [
        "Check out http://scam.com for FREE money!!! 🔥🔥🔥",
        "Great video, really enjoyed it! Keep it up 👍",
        "SUBSCRIBE TO MY CHANNEL!!!! http://bit.ly/sub4sub 💰💰",
        "I learned so much from this tutorial, thank you!",
    ]
    for text in test_cases:
        print(f"Original : {text}")
        print(f"Cleaned  : {preprocess_text(text)}")
        print()
