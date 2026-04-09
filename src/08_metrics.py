"""computes metrics: coverage/traceability/ambiguity/testability"""
"""
Task 6: Compute evaluation metrics for all three pipelines.
Reads project artifacts and computes:
  - dataset_size, persona_count, requirements_count, tests_count
  - traceability_links, review_coverage
  - traceability_ratio, testability_rate, ambiguity_ratio
Saves:
  metrics/metrics_manual.json
  metrics/metrics_auto.json
  metrics/metrics_hybrid.json
  metrics/metrics_summary.json
"""

import json
import os
import re


CLEAN_PATH = os.path.join("data", "reviews_clean.jsonl")
META_PATH = os.path.join("data", "dataset_metadata.json")

GROUPS = {
    "manual": os.path.join("data", "review_groups_manual.json"),
    "auto": os.path.join("data", "review_groups_auto.json"),
    "hybrid": os.path.join("data", "review_groups_hybrid.json"),
}
PERSONAS = {
    "manual": os.path.join("personas", "personas_manual.json"),
    "auto": os.path.join("personas", "personas_auto.json"),
    "hybrid": os.path.join("personas", "personas_hybrid.json"),
}
SPECS = {
    "manual": os.path.join("spec", "spec_manual.md"),
    "auto": os.path.join("spec", "spec_auto.md"),
    "hybrid": os.path.join("spec", "spec_hybrid.md"),
}
TESTS = {
    "manual": os.path.join("tests", "tests_manual.json"),
    "auto": os.path.join("tests", "tests_auto.json"),
    "hybrid": os.path.join("tests", "tests_hybrid.json"),
}
METRICS_OUT = {
    "manual": os.path.join("metrics", "metrics_manual.json"),
    "auto": os.path.join("metrics", "metrics_auto.json"),
    "hybrid": os.path.join("metrics", "metrics_hybrid.json"),
}
SUMMARY_OUT = os.path.join("metrics", "metrics_summary.json")

AMBIGUOUS_TERMS = [
    r"\bshould\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bmay\b",
    r"\busually\b",
    r"\bgenerally\b",
    r"\btypically\b",
    r"\badequate\b",
    r"\bappropriate\b",
    r"\breasonable\b",
    r"\bfast\b",
    r"\bquick\b",
    r"\bsoon\b",
    r"\bsufficient\b",
    r"\beasy\b",
    r"\bsimple\b",
    r"\buser[- ]friendly\b",
    r"\bgood\b",
    r"\bbetter\b",
    r"\boptimal\b",
]
AMBIGUITY_RE = re.compile("|".join(AMBIGUOUS_TERMS), re.IGNORECASE)
REQ_ROW_RE = re.compile(r"^\|\s*(REQ-\d+)\s*\|", re.MULTILINE)
TRACE_ROW_RE = re.compile(
    r"^\|\s*(REQ-\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
    re.MULTILINE,
)
TOTAL_REQ_RE = re.compile(r"\|\s*Total Requirements\s*\|\s*(\d+)\s*\|")
DESCRIPTION_RE = re.compile(
    r"^\|\s*REQ-\d+\s*\|\s*[^|]+\|\s*[^|]+\|\s*(.*?)\s*\|\s*[^|]+\|",
    re.MULTILINE,
)


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path):
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def parse_requirement_ids(spec_text):
    return REQ_ROW_RE.findall(spec_text)


def count_requirements(spec_text):
    total_match = TOTAL_REQ_RE.search(spec_text)
    if total_match:
        return int(total_match.group(1))
    return len(parse_requirement_ids(spec_text))


def count_personas(personas_data):
    return len(personas_data.get("personas", []))


def count_tests(tests_data):
    return len(tests_data.get("tests", []))


def compute_review_coverage(groups_data, total_reviews):
    if total_reviews == 0:
        return 0.0
    covered_ids = set()
    for group in groups_data.get("groups", []):
        covered_ids.update(group.get("review_ids", []))
    return round(len(covered_ids) / total_reviews, 4)


def count_traceability_links(spec_text, tests_data):
    requirement_ids = set(parse_requirement_ids(spec_text))
    if not requirement_ids:
        return 0

    links = set()

    for requirement_id, source_persona, derived_from, _original_text in TRACE_ROW_RE.findall(spec_text):
        links.add((requirement_id, "persona", source_persona.strip()))
        links.add((requirement_id, "source", derived_from.strip()))

    for test in tests_data.get("tests", []):
        requirement_id = test.get("requirement_id")
        if requirement_id in requirement_ids:
            links.add((requirement_id, "test", test.get("test_id", "")))

    return len(links)


def compute_traceability_ratio(requirements_count, traceability_links):
    if requirements_count == 0:
        return 0.0
    max_links = requirements_count * 3
    return round(min(traceability_links / max_links, 1.0), 4)


def compute_testability_rate(spec_text, tests_data):
    requirement_ids = set(parse_requirement_ids(spec_text))
    if not requirement_ids:
        return 0.0
    tested_ids = {
        test.get("requirement_id")
        for test in tests_data.get("tests", [])
        if test.get("requirement_id") in requirement_ids
    }
    return round(len(tested_ids) / len(requirement_ids), 4)


def compute_ambiguity_ratio(spec_text):
    descriptions = [match.strip() for match in DESCRIPTION_RE.findall(spec_text)]
    if not descriptions:
        return 0.0
    ambiguous_count = sum(1 for description in descriptions if AMBIGUITY_RE.search(description))
    return round(ambiguous_count / len(descriptions), 4)


def compute_metrics_for(pipeline, app_id, total_reviews, raw_count, clean_count):
    print(f"\n  Computing metrics for: {pipeline}")

    groups_data = load_json(GROUPS[pipeline])
    personas_data = load_json(PERSONAS[pipeline])
    spec_text = load_text(SPECS[pipeline])
    tests_data = load_json(TESTS[pipeline])

    requirements_count = count_requirements(spec_text)
    traceability_links = count_traceability_links(spec_text, tests_data)

    metrics = {
        "app_id": app_id,
        "raw_count": raw_count,
        "clean_count": clean_count,
        "dataset_size": total_reviews,
        "persona_count": count_personas(personas_data),
        "requirements_count": requirements_count,
        "tests_count": count_tests(tests_data),
        "traceability_links": traceability_links,
        "review_coverage": compute_review_coverage(groups_data, total_reviews),
        "traceability_ratio": compute_traceability_ratio(requirements_count, traceability_links),
        "testability_rate": compute_testability_rate(spec_text, tests_data),
        "ambiguity_ratio": compute_ambiguity_ratio(spec_text),
    }

    write_json(METRICS_OUT[pipeline], metrics)
    return metrics


def main():
    print("=" * 60)
    print("METRICS COMPUTATION  -  08_metrics.py")
    print("=" * 60)

    metadata = load_json(META_PATH)
    clean_reviews = load_jsonl(CLEAN_PATH)

    app_id = metadata.get("app_id")
    raw_count = metadata.get("total_reviews_collected") or metadata.get("cleaning_stats", {}).get("total_raw", 0)
    clean_count = metadata.get("cleaned_dataset_size") or metadata.get("cleaning_stats", {}).get("kept", len(clean_reviews))
    total_reviews = len(clean_reviews)

    summary = {}
    for pipeline in ("manual", "auto", "hybrid"):
        summary[pipeline] = compute_metrics_for(
            pipeline,
            app_id,
            total_reviews,
            raw_count,
            clean_count,
        )

    write_json(SUMMARY_OUT, summary)

    print("\nSaved:")
    for pipeline in ("manual", "auto", "hybrid"):
        print(f"  - {METRICS_OUT[pipeline]}")
    print(f"  - {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
