#!/bin/bash
# Download NLTK data needed for preprocessing
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('vader_lexicon')"
