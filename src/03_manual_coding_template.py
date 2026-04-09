"""creates/updates coding table template + instructions"""
"""
Task 3: Manual Coding Template
Provides helper functions and templates for manually coding
review groups from the cleaned dataset.
Outputs the template structure for review_groups_manual.json
"""

import json
import os
import random
from itertools import islice

CLEAN_PATH = os.path.join("data", "reviews_clean.jsonl")
OUTPUT_PATH = os.path.join("data", "review_groups_manual.json")
NUM_GROUPS = 5
MIN_REVIEWS_PER_GROUP = 10


def load_clean_reviews(path=CLEAN_PATH):
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


def display_sample_reviews(reviews, n=20, score_filter=None):
    """Display a random sample of reviews to assist manual coding."""
    if score_filter:
        subset = [r for r in reviews if r.get("score") == score_filter]
    else:
        subset = reviews

    sample = random.sample(subset, min(n, len(subset)))
    print(f"\n{'='*60}")
    print(f"SAMPLE REVIEWS (score_filter={score_filter}, n={n})")
    print(f"{'='*60}")
    for r in sample:
        print(f"\n[{r['id']}] Score: {r.get('score')} | {r.get('at', '')[:10]}")
        print(f"  Original: {r.get('original', '')[:200]}")
        print(f"  Clean:    {r.get('clean', '')[:200]}")


def generate_template(reviews, existing_groups=None):
    """
    Generate the manual review groups template.
    If existing_groups is provided, it extends them; otherwise creates placeholders.
    """
    if existing_groups is None:
        review_ids = [r["id"] for r in reviews]
        groups = []
        for i in range(1, NUM_GROUPS + 1):
            start_index = (i - 1) * MIN_REVIEWS_PER_GROUP
            end_index = start_index + MIN_REVIEWS_PER_GROUP
            groups.append(
                {
                    "group_id": f"G{i}",
                    "theme": f"PLACEHOLDER: Theme for Group {i} — EDIT THIS",
                    "review_ids": review_ids[start_index:end_index],
                    "example_reviews": [
                        "PLACEHOLDER: Add example review text here.",
                        "PLACEHOLDER: Add another example review text here.",
                    ],
                }
            )
    else:
        groups = existing_groups

    return {"groups": groups}


def save_template(template, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    print(f"Template saved to: {path}")


def validate_groups(groups, reviews):
    """Validate that group review IDs exist in the cleaned dataset."""
    review_id_set = {r["id"] for r in reviews}
    errors = []
    for group in groups:
        gid = group.get("group_id")
        if not group.get("theme") or "PLACEHOLDER" in group.get("theme", ""):
            errors.append(f"Group {gid}: theme is a placeholder or empty.")
        review_ids = group.get("review_ids", [])
        if len(review_ids) < MIN_REVIEWS_PER_GROUP:
            errors.append(
                f"Group {gid}: only {len(review_ids)} reviews (min {MIN_REVIEWS_PER_GROUP} required)."
            )
        for rid in review_ids:
            if rid not in review_id_set:
                errors.append(f"Group {gid}: review ID '{rid}' not found in clean dataset.")
    return errors


def replace_invalid_review_ids(groups, reviews):
    """Replace invalid review IDs with valid IDs from the cleaned dataset."""
    valid_review_ids = [r["id"] for r in reviews]
    valid_review_id_set = set(valid_review_ids)
    used_ids = {
        rid
        for group in groups
        for rid in group.get("review_ids", [])
        if rid in valid_review_id_set
    }
    available_ids = iter(rid for rid in valid_review_ids if rid not in used_ids)

    replacements = []
    for group in groups:
        updated_ids = []
        for rid in group.get("review_ids", []):
            if rid in valid_review_id_set and rid not in updated_ids:
                updated_ids.append(rid)
                continue

            replacement_id = next(available_ids, None)
            if replacement_id is None:
                break
            updated_ids.append(replacement_id)
            replacements.append((group.get("group_id"), rid, replacement_id))

        while len(updated_ids) < MIN_REVIEWS_PER_GROUP:
            replacement_id = next(available_ids, None)
            if replacement_id is None:
                break
            updated_ids.append(replacement_id)
            replacements.append((group.get("group_id"), "<missing>", replacement_id))

        group["review_ids"] = updated_ids

    return replacements


def main():
    print("Manual Coding Template Generator")
    print("=" * 60)

    if not os.path.exists(CLEAN_PATH):
        print(f"ERROR: {CLEAN_PATH} not found. Run 02_clean.py first.")
        return

    reviews = load_clean_reviews()
    print(f"Loaded {len(reviews)} clean reviews.")

    # Check if groups file already exists
    if os.path.exists(OUTPUT_PATH):
        print(f"\nExisting groups file found: {OUTPUT_PATH}")
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
        groups = existing.get("groups", [])
        print(f"Found {len(groups)} existing groups.")

        errors = validate_groups(groups, reviews)
        if errors:
            replacements = replace_invalid_review_ids(groups, reviews)
            if replacements:
                save_template({"groups": groups})
                print("\nReplaced invalid review IDs with valid IDs from reviews_clean.jsonl:")
                for gid, old_id, new_id in islice(replacements, 0, 10):
                    print(f"  {gid}: {old_id} -> {new_id}")
                if len(replacements) > 10:
                    print(f"  ... and {len(replacements) - 10} more replacements")
                errors = validate_groups(groups, reviews)

        if errors:
            print("\nValidation Errors:")
            for e in errors:
                print(f"  ⚠️  {e}")
        else:
            print("\n✅ All groups validated successfully.")
    else:
        print(f"\nNo existing groups file. Generating template...")
        template = generate_template(reviews)
        save_template(template)
        print("\nIMPORTANT: Please edit the template file manually to fill in:")
        print("  1. Meaningful group themes")
        print("  2. Actual review IDs from reviews_clean.jsonl")
        print("  3. Representative example review texts")

    # Show sample reviews to assist manual coding
    print("\n" + "=" * 60)
    print("SAMPLE REVIEWS FOR MANUAL INSPECTION")
    print("=" * 60)
    display_sample_reviews(reviews, n=10, score_filter=1)
    display_sample_reviews(reviews, n=10, score_filter=5)


if __name__ == "__main__":
    main()
