"""
Task 3.2: Construct personas manually from review groups
Reads data/review_groups_manual.json and produces personas/personas_manual.json
This script provides a template and validates the manually created personas.
"""

import json
import os

GROUPS_PATH = os.path.join("data", "review_groups_manual.json")
PERSONAS_PATH = os.path.join("personas", "personas_manual.json")


def load_review_groups():
    with open(GROUPS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_persona_template(group):

    gid = group["group_id"]
    return {
        "persona_id": f"P{gid[1:]}",
        "name": f"PLACEHOLDER: Persona name for group {gid}",
        "description": f"PLACEHOLDER: A user who {group.get('theme', '').lower()}",
        "source_group": gid,
        "goals": [
            "PLACEHOLDER: Primary goal derived from reviews",
            "PLACEHOLDER: Secondary goal derived from reviews",
        ],
        "pain_points": [
            "PLACEHOLDER: Main pain point from reviews",
            "PLACEHOLDER: Secondary pain point from reviews",
        ],
        "context": "PLACEHOLDER: When and how this user uses the app.",
        "demographics": {
            "age_range": "PLACEHOLDER",
            "occupation": "PLACEHOLDER",
            "tech_comfort": "PLACEHOLDER",
            "device": "PLACEHOLDER",
        },
        "review_count": len(group.get("review_ids", [])),
        "sample_reviews": group.get("example_reviews", [])[:3],
    }


def validate_personas(personas):
    errors = []
    for p in personas:
        pid = p.get("persona_id") or p.get("id") or "?"
        for field in ["name", "goals", "pain_points", "context"]:
            val = p.get(field)
            if not val:
                errors.append(f"Persona {pid}: missing field '{field}'")
            elif isinstance(val, str) and "PLACEHOLDER" in val:
                errors.append(f"Persona {pid}: field '{field}' still has placeholder text")
            elif isinstance(val, list):
                for item in val:
                    if "PLACEHOLDER" in str(item):
                        errors.append(f"Persona {pid}: field '{field}' contains placeholder text")

        description = p.get("description")
        if description is not None and "PLACEHOLDER" in str(description):
            errors.append(f"Persona {pid}: field 'description' still has placeholder text")

        demographics = p.get("demographics")
        if demographics is not None:
            if not isinstance(demographics, dict) or not demographics:
                errors.append(f"Persona {pid}: invalid or empty 'demographics'")
            else:
                for key, value in demographics.items():
                    if not value:
                        errors.append(f"Persona {pid}: demographics field '{key}' is empty")
                    elif "PLACEHOLDER" in str(value):
                        errors.append(f"Persona {pid}: demographics field '{key}' still has placeholder text")

        source_group = p.get("source_group") or p.get("derived_from_group")
        if not source_group:
            errors.append(f"Persona {pid}: missing source group")

        evidence = p.get("sample_reviews") or p.get("evidence_reviews")
        if evidence is None:
            errors.append(f"Persona {pid}: missing review evidence field")
    return errors


def create_manual_personas_template():

    groups_data = load_review_groups()
    groups = groups_data.get("groups", [])

    personas = [generate_persona_template(g) for g in groups]
    output = {"personas": personas}

    os.makedirs("personas", exist_ok=True)
    with open(PERSONAS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Persona template saved to: {PERSONAS_PATH}")
    print("Please edit the file to fill in meaningful persona details.")


def enrich_personas_from_groups(personas, groups_data):
    """Backfill persona evidence fields from the matching review groups."""
    groups_by_id = {
        group.get("group_id"): group
        for group in groups_data.get("groups", [])
    }
    changed = False

    for persona in personas:
        source_group = persona.get("source_group") or persona.get("derived_from_group")
        group = groups_by_id.get(source_group)
        if not group:
            continue

        if not persona.get("sample_reviews") and group.get("example_reviews"):
            persona["sample_reviews"] = group.get("example_reviews", [])[:3]
            changed = True

        if not persona.get("review_count"):
            persona["review_count"] = len(group.get("review_ids", []))
            changed = True

    return changed


def main():
    print("Manual Personas Generator / Validator")
    print("=" * 60)

    if not os.path.exists(GROUPS_PATH):
        print(f"ERROR: {GROUPS_PATH} not found. Run 03_manual_coding_template.py first.")
        return

    if not os.path.exists(PERSONAS_PATH):
        print("No personas file found. Generating template from review groups...")
        create_manual_personas_template()
        return

    # Validate existing personas
    with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    personas = data.get("personas", [])
    groups_data = load_review_groups()

    if enrich_personas_from_groups(personas, groups_data):
        with open(PERSONAS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Backfilled missing persona evidence from review groups.")

    print(f"Loaded {len(personas)} personas from {PERSONAS_PATH}")

    errors = validate_personas(personas)
    if errors:
        print(f"\n⚠️  Validation issues found ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
    else:
        print("\n✅ All personas validated successfully.")

    print("\nPersonas Summary:")
    print("-" * 60)
    for p in personas:
        persona_id = p.get("persona_id") or p.get("id", "?")
        source_group = p.get("source_group") or p.get("derived_from_group")
        evidence_reviews = p.get("sample_reviews") or p.get("evidence_reviews", [])

        print(f"  [{persona_id}] {p['name']}")
        print(f"       Group: {source_group}")
        print(f"       Goals: {len(p.get('goals', []))}")
        print(f"       Pain Points: {len(p.get('pain_points', []))}")
        print(f"       Evidence Reviews: {len(evidence_reviews)}")


if __name__ == "__main__":
    main()
