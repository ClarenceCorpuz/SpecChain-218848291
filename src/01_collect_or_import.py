"""imports or reads your raw dataset; if you scraped, include scraper here"""
"""
Task 2: Collect reviews from Google Play Store
App: Headspace - Meditation & Sleep
App ID: com.getsomeheadspace.android
Collects up to 5000 reviews and saves to data/reviews_raw.jsonl
"""

import json
import os
import time
from datetime import datetime

try:
    from google_play_scraper import reviews, Sort
except ImportError:
    print("Installing google-play-scraper...")
    os.system("pip install google-play-scraper")
    from google_play_scraper import reviews, Sort

APP_ID = "com.getsomeheadspace.android"
OUTPUT_PATH = os.path.join("data", "reviews_raw.jsonl")
METADATA_PATH = os.path.join("data", "dataset_metadata.json")
TARGET_COUNT = 5000
BATCH_SIZE = 200

os.makedirs("data", exist_ok=True)


def collect_reviews():
    print(f"Collecting reviews for app: {APP_ID}")
    print(f"Target count: {TARGET_COUNT}")

    all_reviews = []
    continuation_token = None
    attempt = 0

    while len(all_reviews) < TARGET_COUNT:
        try:
            batch, continuation_token = reviews(
                APP_ID,
                lang="en",
                country="ca",
                sort=Sort.NEWEST,
                count=BATCH_SIZE,
                continuation_token=continuation_token,
            )
            if not batch:
                print("No more reviews available.")
                break

            all_reviews.extend(batch)
            print(f"  Collected {len(all_reviews)} reviews so far...")

            if continuation_token is None:
                print("Reached end of available reviews.")
                break

            time.sleep(0.5)  # polite delay
            attempt += 1

        except Exception as e:
            print(f"Error during collection: {e}")
            if attempt > 3:
                break
            time.sleep(2)
            attempt += 1

    print(f"\nTotal reviews collected: {len(all_reviews)}")

    # Save to JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for i, review in enumerate(all_reviews):
            record = {
                "id": f"R{i:05d}",
                "reviewId": review.get("reviewId", ""),
                "userName": review.get("userName", ""),
                "score": review.get("score", 0),
                "at": review.get("at", datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
                if hasattr(review.get("at", ""), "strftime")
                else str(review.get("at", "")),
                "original": review.get("content", ""),
                "thumbsUpCount": review.get("thumbsUpCount", 0),
                "appVersion": review.get("appVersion", ""),
                "replyContent": review.get("replyContent", None),
            }
            f.write(json.dumps(record) + "\n")

    print(f"Raw reviews saved to: {OUTPUT_PATH}")

    # Save metadata
    metadata = {
        "app_name": "Headspace - Meditation & Sleep",
        "app_id": APP_ID,
        "store": "Google Play Store",
        "store_url": "https://play.google.com/store/apps/details?id=com.getsomeheadspace.android&hl=en_CA",
        "collection_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "collection_method": "google-play-scraper Python library",
        "language": "en",
        "country": "ca",
        "sort_order": "NEWEST",
        "total_reviews_collected": len(all_reviews),
        "target_reviews": TARGET_COUNT,
        "notes": (
            "Collected using google-play-scraper. "
            "Reviews are in English from the Canadian store. "
            "If fewer than target were collected, it means fewer reviews are available."
        ),
        "cleaning_decisions": {
            "removed_duplicates": True,
            "removed_empty_reviews": True,
            "removed_short_reviews": True,
            "min_review_length_chars": 10,
            "lowercased": True,
            "removed_punctuation": True,
            "removed_special_characters": True,
            "removed_emojis": True,
            "converted_numbers_to_text": True,
            "removed_stopwords": True,
            "lemmatized": True,
        },
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved to: {METADATA_PATH}")
    return len(all_reviews)


if __name__ == "__main__":
    count = collect_reviews()
    print(f"\nDone. Collected {count} reviews.")
