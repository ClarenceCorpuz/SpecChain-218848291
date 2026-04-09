"""runs the full pipeline end-to-end"""

# src/run_all.py
import subprocess, sys

scripts = [
    "src/00_validate_repo.py",
    "src/01_collect_or_import.py",
    "src/02_clean.py",
    "src/03_manual_coding_template.py",
    "src/04_personas_manual.py",
    "src/05_personas_auto.py",
    "src/06_spec_generate.py",
    "src/07_tests_generate.py",
    "src/08_metrics.py"
]

def main():
    for s in scripts:
        print(f"\n=== Running {s} ===")
        r = subprocess.run([sys.executable, s])
        if r.returncode != 0:
            print(f"Script failed: {s}")
            sys.exit(r.returncode)
    print("\nAll steps completed.")

if __name__ == "__main__":
    main()
