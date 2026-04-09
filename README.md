# EECS 4312 – SpecChain 

Student: Clarence Corpuz (218848291)  
Repository: https://github.com/ClarenceCorpuz/SpecChain-218848291.git  
Application: Headspace - Meditation & Sleep (com.getsomeheadspace.android)

## Purpose
This README documents: how to run the pipeline to compute metrics, where outputs are saved, and a concise summary of results for Manual, Auto, and Hybrid pipelines.

---

## App and Dataset Details

- App name: Headspace - Meditation & Sleep
- Store: Google Play Store
- Store URL: https://play.google.com/store/apps/details?id=com.getsomeheadspace.android&hl=en_CA
- App ID: com.getsomeheadspace.android
- Collection date: 2026-04-07T00:43:38
- Data collection method: google-play-scraper (Python library)
- Language/Country: en / ca
- Sort order: NEWEST

Original dataset:
- Total reviews collected: 5000
- File: data/reviews_raw.jsonl

Final cleaned dataset:
- Cleaned dataset size: 4515
- File: data/reviews_clean.jsonl

Cleaning decisions (from data/dataset_metadata.json):
- removed_duplicates: true
- removed_empty_reviews: true
- removed_short_reviews: true (min_review_length_chars: 10)
- lowercased: true
- removed_punctuation: true
- removed_special_characters: true
- removed_emojis: true
- converted_numbers_to_text: true
- removed_stopwords: true
- lemmatized: true

Cleaning stats:
- total_raw: 5000
- removed_empty: 0
- removed_short: 470
- removed_duplicate: 15
- kept: 4515

---

## Repository Structure

- data/
  - reviews_raw.jsonl
  - reviews_clean.jsonl
  - dataset_metadata.json
  - review_groups_manual.json
  - review_groups_hybrid.json
- personas/
  - personas_manual.json
  - personas_auto.json
  - personas_hybrid.json
- spec/
  - spec_manual.md
  - spec_auto.md
  - spec_hybrid.md
- tests/
  - tests_manual.json
  - tests_auto.json
  - tests_hybrid.json
- metrics/
  - metrics_manual.json
  - metrics_auto.json
  - metrics_hybrid.json
- src/
  - 00_validate_repo.py
  - 01_collect_or_import.py
  - 02_clean.py
  - 03_manual_coding_template.py
  - 04_personas_manual.py
  - 05_personas_auto.py
  - 06_spec_generate.py
  - 07_tests_generate.py
  - 08_metrics.py
  - run_all.py
- reflection/
  - reflection.md

---

## How to Run (Commands)

Environment setup and full pipeline:


How to Run:
1. Make sure the correct directory is used
2. py -3.10 -m venv .venv
3. .venv\Scripts\activate
4. python -m pip install --upgrade pip
5. pip install google-play-scraper nltk num2words groq
6. python src/run_all.py

