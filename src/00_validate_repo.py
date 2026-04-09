"""checks required files/folders exist"""
"""
Task 0: Validate repository structure
Checks that all required folders and files are present.
"""

import os
import sys

REQUIRED_STRUCTURE = {
    "data": [
        "reviews_raw.jsonl",
        "reviews_clean.jsonl",
        "dataset_metadata.json",
        "review_groups_manual.json",
        "review_groups_hybrid.json",
    ],
    "personas": [
        "personas_manual.json",
        "personas_auto.json",
        "personas_hybrid.json",
    ],
    "spec": [
        "spec_manual.md",
        "spec_auto.md",
        "spec_hybrid.md",
    ],
    "metrics": [
        "metrics_manual.json",
        "metrics_auto.json",
        "metrics_hybrid.json",
    ],
    "tests": [
        "tests_manual.json",
        "tests_auto.json",
        "tests_hybrid.json",
    ],
    "reflection": [
        "reflection.md",
    ],
    "src": [
        "00_validate_repo.py",
        "01_collect_or_import.py",
        "02_clean.py",
        "03_manual_coding_template.py",
        "04_personas_manual.py",
        "05_personas_auto.py",
        "06_spec_generate.py",
        "07_tests_generate.py",
        "08_metrics.py",
        "run_all.py",
    ],
}

ROOT_FILES = ["README.md"]


def validate_repo(base_path="."):
    missing = []
    present = []

    # Check root files
    for f in ROOT_FILES:
        full_path = os.path.join(base_path, f)
        if os.path.exists(full_path):
            present.append(full_path)
        else:
            missing.append(full_path)

    # Check folder/file structure
    for folder, files in REQUIRED_STRUCTURE.items():
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(folder_path):
            missing.append(f"{folder}/ (directory missing)")
            for f in files:
                missing.append(os.path.join(folder, f))
        else:
            present.append(f"{folder}/")
            for f in files:
                full_path = os.path.join(folder_path, f)
                if os.path.exists(full_path):
                    present.append(full_path)
                else:
                    missing.append(full_path)

    print("=" * 60)
    print("REPOSITORY VALIDATION REPORT")
    print("=" * 60)
    print(f"\n Present ({len(present)}):")
    for p in present:
        print(f"   [OK]  {p}")

    print(f"\n Missing ({len(missing)}):")
    if missing:
        for m in missing:
            print(f"   [MISSING]  {m}")
    else:
        print("   None — all files present!")

    print("\n" + "=" * 60)
    if missing:
        print(f"RESULT: INCOMPLETE — {len(missing)} file(s)/folder(s) missing.")
        return False
    else:
        print("RESULT: COMPLETE — Repository structure is valid.")
        return True


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_repo(base)
    sys.exit(0 if success else 1)
