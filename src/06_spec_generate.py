"""generates structured specs from personas"""
#!/usr/bin/env python3
"""
06_spec_generate.py

TASK 3.3: GENERATE SPECIFICATIONS FROM PERSONAS
EECS 4312 - Software Requirements
Instructor: Maleknaz Nayebi

This script derives structured specifications from the personas created
in Task 3.2. Each persona's goals and pain points are transformed into
formal requirements with traceability links.

It handles all three pipelines:
  - Manual   : personas/personas_manual.json  → spec/spec_manual.md
  - Auto     : personas/personas_auto.json    → spec/spec_auto.md
  - Hybrid   : personas/personas_hybrid.json  → spec/spec_hybrid.md

Each requirement has:
  - ID, description, priority, type (Functional / Non-Functional)
  - Source persona for traceability
"""

import json
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PIPELINE_CONFIG = {
    "manual": {
        "personas_path": "personas/personas_manual.json",
        "spec_path":     "spec/spec_manual.md"
    },
    "auto": {
        "personas_path": "personas/personas_auto.json",
        "spec_path":     "spec/spec_auto.md"
    },
    "hybrid": {
        "personas_path": "personas/personas_hybrid.json",
        "spec_path":     "spec/spec_hybrid.md"
    }
}

# Keywords that indicate a non-functional requirement
NF_KEYWORDS = [
    "slow", "fast", "performance", "reliable", "reliability", "secure",
    "security", "expensive", "cost", "battery", "privacy", "accurate",
    "accuracy", "responsive", "stable", "stability", "crash", "freeze",
    "latency", "scalable", "availability", "usability", "accessible"
]

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def ensure_directories():
    """Ensure required output directories exist."""
    os.makedirs("spec", exist_ok=True)


def load_json(path: str):
    """Load a JSON file and return its contents."""
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# REQUIREMENT DERIVATION
# ─────────────────────────────────────────────────────────────────────────────

def classify_requirement_type(text: str) -> str:
    """
    Classify whether a requirement is Functional or Non-Functional
    based on keyword heuristics.

    Args:
        text (str): The goal or pain point text.

    Returns:
        str: 'Functional' or 'Non-Functional'
    """
    text_lower = text.lower()
    for kw in NF_KEYWORDS:
        if kw in text_lower:
            return "Non-Functional"
    return "Functional"


def derive_requirements_from_persona(persona: dict, req_counter: int) -> tuple:
    """
    Derive requirements from a single persona's goals and pain points.

    Args:
        persona (dict): A single persona record.
        req_counter (int): Starting counter for requirement IDs.

    Returns:
        tuple: (list[dict] of requirements, updated req_counter)
    """
    requirements = []
    pid = persona.get("persona_id", "P?")
    name = persona.get("name", "Unknown")

    # Derive requirements from goals
    for goal in persona.get("goals", []):
        req_id = f"REQ-{req_counter:03d}"
        req_type = classify_requirement_type(goal)
        requirements.append({
            "req_id": req_id,
            "type": req_type,
            "priority": "High",
            "description": f"The system shall support: {goal}",
            "source_persona": pid,
            "source_persona_name": name,
            "derived_from": "goal",
            "original_text": goal
        })
        req_counter += 1

    # Derive requirements from pain points
    for pain in persona.get("pain_points", []):
        req_id = f"REQ-{req_counter:03d}"
        req_type = classify_requirement_type(pain)
        requirements.append({
            "req_id": req_id,
            "type": req_type,
            "priority": "High",
            "description": f"The system shall address: {pain}",
            "source_persona": pid,
            "source_persona_name": name,
            "derived_from": "pain_point",
            "original_text": pain
        })
        req_counter += 1

    return requirements, req_counter


def generate_spec_from_personas(personas: dict) -> tuple:
    """
    Generate a full specification from all personas.

    Args:
        personas (dict): The personas data structure.

    Returns:
        tuple: (list[dict] of all requirements, dict of summary stats)
    """
    all_requirements = []
    req_counter = 1

    for persona in personas.get("personas", []):
        reqs, req_counter = derive_requirements_from_persona(persona, req_counter)
        all_requirements.extend(reqs)

    # Compute summary statistics
    functional_count     = sum(1 for r in all_requirements if r["type"] == "Functional")
    non_functional_count = sum(1 for r in all_requirements if r["type"] == "Non-Functional")
    from_goals           = sum(1 for r in all_requirements if r["derived_from"] == "goal")
    from_pain            = sum(1 for r in all_requirements if r["derived_from"] == "pain_point")

    summary = {
        "total_requirements": len(all_requirements),
        "functional": functional_count,
        "non_functional": non_functional_count,
        "derived_from_goals": from_goals,
        "derived_from_pain_points": from_pain,
        "personas_count": len(personas.get("personas", [])),
        "generated_at": datetime.now().isoformat()
    }

    return all_requirements, summary


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN RENDERING
# ─────────────────────────────────────────────────────────────────────────────

def render_spec_markdown(requirements: list, summary: dict, pipeline_name: str) -> str:
    """
    Render the specification as a Markdown document.

    Args:
        requirements (list[dict]): All derived requirements.
        summary (dict): Summary statistics.
        pipeline_name (str): Name of the pipeline (manual/auto/hybrid).

    Returns:
        str: The full Markdown content.
    """
    lines = []
    lines.append(f"# Software Requirements Specification — {pipeline_name.upper()} Pipeline")
    lines.append("")
    lines.append(f"**Generated**: {summary.get('generated_at', 'N/A')}")
    lines.append(f"**Pipeline**: {pipeline_name}")
    lines.append(f"**Total Requirements**: {summary['total_requirements']}")
    lines.append(f"**Functional**: {summary['functional']}  |  "
                 f"**Non-Functional**: {summary['non_functional']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Requirements | {summary['total_requirements']} |")
    lines.append(f"| Functional | {summary['functional']} |")
    lines.append(f"| Non-Functional | {summary['non_functional']} |")
    lines.append(f"| From Goals | {summary['derived_from_goals']} |")
    lines.append(f"| From Pain Points | {summary['derived_from_pain_points']} |")
    lines.append(f"| Source Personas | {summary['personas_count']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group requirements by source persona
    from collections import OrderedDict
    by_persona = OrderedDict()
    for req in requirements:
        key = f"{req['source_persona']} — {req['source_persona_name']}"
        by_persona.setdefault(key, []).append(req)

    for persona_label, reqs in by_persona.items():
        lines.append(f"## Requirements from {persona_label}")
        lines.append("")
        lines.append("| Req ID | Type | Priority | Description | Derived From |")
        lines.append("|--------|------|----------|-------------|--------------|")
        for r in reqs:
            desc = r['description'].replace("|", "\\|")
            lines.append(f"| {r['req_id']} | {r['type']} | {r['priority']} | {desc} | {r['derived_from']} |")
        lines.append("")

    # Traceability matrix
    lines.append("---")
    lines.append("")
    lines.append("## Traceability Matrix")
    lines.append("")
    lines.append("| Req ID | Source Persona | Derived From | Original Text |")
    lines.append("|--------|---------------|--------------|---------------|")
    for r in requirements:
        orig = r.get('original_text', '').replace("|", "\\|")[:80]
        lines.append(f"| {r['req_id']} | {r['source_persona']} | {r['derived_from']} | {orig} |")
    lines.append("")

    return "\n".join(lines)


def save_spec(content: str, path: str):
    """Save the Markdown spec to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] Specification saved to '{path}'.")


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(pipeline_name: str):
    """
    Run the spec generation for a specific pipeline.

    Args:
        pipeline_name (str): One of 'manual', 'auto', 'hybrid'.
    """
    config = PIPELINE_CONFIG.get(pipeline_name)
    if not config:
        print(f"[ERROR] Unknown pipeline: {pipeline_name}")
        return

    print(f"\n{'=' * 70}")
    print(f"  GENERATING SPECIFICATION — {pipeline_name.upper()} PIPELINE")
    print(f"{'=' * 70}")

    personas = load_json(config["personas_path"])
    if not personas:
        print(f"[SKIP] No personas found for {pipeline_name} pipeline.")
        return

    persona_count = len(personas.get("personas", []))
    print(f"[INFO] Loaded {persona_count} personas from '{config['personas_path']}'.")

    # Generate
    requirements, summary = generate_spec_from_personas(personas)

    # Render
    markdown = render_spec_markdown(requirements, summary, pipeline_name)

    # Save
    save_spec(markdown, config["spec_path"])

    # Print summary
    print(f"[INFO] {summary['total_requirements']} requirements generated.")
    print(f"       Functional: {summary['functional']}  |  "
          f"Non-Functional: {summary['non_functional']}")
    print(f"       Output → {config['spec_path']}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  TASK 3.3 — GENERATE SPECIFICATIONS FROM PERSONAS")
    print("=" * 70)

    ensure_directories()

    # Determine which pipelines to run
    # Default: run all available pipelines
    pipelines_to_run = []
    for name, config in PIPELINE_CONFIG.items():
        if os.path.exists(config["personas_path"]):
            pipelines_to_run.append(name)
        else:
            print(f"[SKIP] {name} pipeline — personas file not found: {config['personas_path']}")

    if not pipelines_to_run:
        print("[ERROR] No persona files found. Run persona generation scripts first.")
        sys.exit(1)

    for pipeline_name in pipelines_to_run:
        run_pipeline(pipeline_name)

    print(f"\n[DONE] 06_spec_generate.py complete.\n")


if __name__ == "__main__":
    main()
