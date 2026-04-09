"""cleans raw data & make clean dataset"""
"""
Task 2: Clean the raw reviews dataset
Reads data/reviews_raw.jsonl and produces data/reviews_clean.jsonl
Cleaning steps:
  - Remove duplicates
  - Remove empty / extremely short reviews
  - Remove punctuation, special characters, emojis
  - Convert numbers to text
  - Lowercase
  - Remove stop words
  - Lemmatize
"""

import json
import os
import re
import unicodedata

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
except ImportError:
    os.system("pip install nltk")
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

try:
    from num2words import num2words
except ImportError:
    os.system("pip install num2words")
    from num2words import num2words

# Download necessary NLTK resources
for resource in ["stopwords", "wordnet", "omw-1.4", "punkt"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

RAW_PATH = os.path.join("data", "reviews_raw.jsonl")
CLEAN_PATH = os.path.join("data", "reviews_clean.jsonl")
MIN_WORD_COUNT = 3  # minimum words after cleaning

lemmatizer = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words("english"))

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"
    "\u3030"
    "]+",
    flags=re.UNICODE,
)


def remove_emojis(text):
    return EMOJI_PATTERN.sub("", text)


def convert_numbers(text):
    """Replace integer tokens with their word equivalents."""
    def replace_match(m):
        try:
            return num2words(int(m.group()))
        except Exception:
            return m.group()
    return re.sub(r"\b\d+\b", replace_match, text)


def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Remove emojis
    text = remove_emojis(text)

    # Normalize unicode (remove accents etc.)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Convert numbers to words
    text = convert_numbers(text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove special characters and punctuation (keep only letters and spaces)
    text = re.sub(r"[^a-z\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize
    tokens = text.split()

    # Remove stop words and lemmatize
    tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in STOP_WORDS and len(token) > 1
    ]

    return " ".join(tokens)


def load_raw_reviews(path):
    reviews = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    reviews.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return reviews


def clean_reviews():
    print(f"Loading raw reviews from: {RAW_PATH}")

    if not os.path.exists(RAW_PATH):
        print(f"ERROR: {RAW_PATH} not found. Run 01_collect_or_import.py first.")
        return

    raw_reviews = load_raw_reviews(RAW_PATH)
    print(f"Loaded {len(raw_reviews)} raw reviews.")

    cleaned = []
    seen_texts = set()
    seen_ids = set()

    stats = {
        "total_raw": len(raw_reviews),
        "removed_empty": 0,
        "removed_short": 0,
        "removed_duplicate": 0,
        "kept": 0,
    }

    for review in raw_reviews:
        original_text = review.get("original", "").strip()

        # Skip empty
        if not original_text:
            stats["removed_empty"] += 1
            continue

        # Skip extremely short (< 10 chars)
        if len(original_text) < 10:
            stats["removed_short"] += 1
            continue

        # Clean
        clean = clean_text(original_text)

        # Skip if cleaning left too few words
        if len(clean.split()) < MIN_WORD_COUNT:
            stats["removed_short"] += 1
            continue

        # Skip duplicate clean text
        if clean in seen_texts:
            stats["removed_duplicate"] += 1
            continue

        # Skip duplicate review IDs
        review_id = review.get("reviewId", "")
        if review_id and review_id in seen_ids:
            stats["removed_duplicate"] += 1
            continue

        seen_texts.add(clean)
        if review_id:
            seen_ids.add(review_id)

        record = {
            "id": review.get("id", f"R{len(cleaned):05d}"),
            "reviewId": review.get("reviewId", ""),
            "userName": review.get("userName", ""),
            "score": review.get("score", 0),
            "at": review.get("at", ""),
            "original": original_text,
            "clean": clean,
            "thumbsUpCount": review.get("thumbsUpCount", 0),
            "appVersion": review.get("appVersion", ""),
            "replyContent": review.get("replyContent", None),
        }
        cleaned.append(record)
        stats["kept"] += 1

    # Save cleaned reviews
    os.makedirs("data", exist_ok=True)
    with open(CLEAN_PATH, "w", encoding="utf-8") as f:
        for record in cleaned:
            f.write(json.dumps(record) + "\n")

    print(f"\nCleaning complete:")
    print(f"  Raw reviews:         {stats['total_raw']}")
    print(f"  Removed (empty):     {stats['removed_empty']}")
    print(f"  Removed (short):     {stats['removed_short']}")
    print(f"  Removed (duplicate): {stats['removed_duplicate']}")
    print(f"  Kept (clean):        {stats['kept']}")
    print(f"\nCleaned dataset saved to: {CLEAN_PATH}")

    # Update metadata
    meta_path = os.path.join("data", "dataset_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        metadata["cleaned_dataset_size"] = stats["kept"]
        metadata["cleaning_stats"] = stats
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata updated: {meta_path}")

    return stats["kept"]


if __name__ == "__main__":
    clean_reviews()
