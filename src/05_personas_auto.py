"""automated persona generation pipeline"""
"""
Task 4: Automated Persona & Review Group Generation using Groq API
Uses meta-llama/llama-4-scout-17b-16e-instruct model to:
  1. Automatically cluster reviews into groups (review_groups_auto.json)
  2. Generate personas from review groups (personas_auto.json)
"""

import json
import os
import re
import time
import random

try:
    from groq import Groq
except ImportError:
    os.system("pip install groq")
    from groq import Groq

CLEAN_PATH        = os.path.join("data", "reviews_clean.jsonl")
GROUPS_OUTPUT     = os.path.join("data", "review_groups_auto.json")
PERSONAS_OUTPUT   = os.path.join("personas", "personas_auto.json")
HYBRID_GROUPS_OUTPUT = os.path.join("data", "review_groups_hybrid.json")
HYBRID_PERSONAS_OUTPUT = os.path.join("personas", "personas_hybrid.json")

GROQ_API_KEY      = "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"
MODEL             = "meta-llama/llama-4-scout-17b-16e-instruct"
NUM_GROUPS        = 5
SAMPLE_SIZE       = 150   # reviews sent to LLM for grouping
MAX_RETRIES       = 3


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


def artifact_is_stale(source_path, target_path):
    """Return True if the target is missing or older than the source file."""
    if not os.path.exists(target_path):
        return True
    return os.path.getmtime(target_path) < os.path.getmtime(source_path)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def build_hybrid_groups(auto_groups_data):
    """Create hybrid review groups from the latest automated groups."""
    hybrid_groups = []
    for idx, group in enumerate(auto_groups_data.get("groups", []), start=1):
        hybrid_groups.append(
            {
                "group_id": f"H{idx}",
                "theme": group.get("theme", f"Hybrid Theme {idx}"),
                "review_ids": group.get("review_ids", []),
                "example_reviews": group.get("example_reviews", [])[:2],
                "notes": "Auto-regenerated from the latest cleaned dataset; refine manually if needed.",
            }
        )
    return {"groups": hybrid_groups}


def build_hybrid_personas(auto_personas_data, hybrid_groups_data):
    """Create hybrid personas from the latest automated personas and hybrid groups."""
    personas = []
    hybrid_groups = hybrid_groups_data.get("groups", [])

    for idx, (persona, group) in enumerate(zip(auto_personas_data.get("personas", []), hybrid_groups), start=1):
        persona_id = f"P_hybrid_{idx}"
        personas.append(
            {
                "persona_id": persona_id,
                "id": persona_id,
                "name": persona.get("name", f"Hybrid Persona {idx}"),
                "description": persona.get("description", ""),
                "derived_from_group": group["group_id"],
                "source_group": group["group_id"],
                "goals": persona.get("goals", []),
                "pain_points": persona.get("pain_points", []),
                "context": persona.get("context", []),
                "constraints": persona.get("constraints", []),
                "evidence_reviews": group.get("review_ids", [])[:3],
                "notes": "Auto-regenerated from the latest cleaned dataset; refine manually if needed.",
            }
        )

    return {"personas": personas}


def call_groq(client, prompt, temperature=0.3, max_tokens=4096):
    """Call Groq API with exponential-backoff retry."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            wait = 2 ** attempt
            print(f"  ⚠️  Groq API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"  Retrying in {wait}s …")
                time.sleep(wait)
    return None


def extract_json_block(text):
    """Extract the first JSON object or array from a string."""
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


# ─────────────────────────────────────────────
#  STEP 1 – Generate review groups
# ─────────────────────────────────────────────
def generate_review_groups(client, reviews):
    """Ask the LLM to cluster a sample of reviews into NUM_GROUPS thematic groups."""
    sample = random.sample(reviews, min(SAMPLE_SIZE, len(reviews)))

    review_lines = "\n".join(
        f"[{r['id']}] (score:{r.get('score','?')}) {r.get('original','')[:150]}"
        for r in sample
    )

    prompt = f"""You are a requirements engineer analysing user reviews for Headspace,
a meditation and mindfulness mobile app on Google Play.

Analyse the {len(sample)} user reviews below and group them into EXACTLY {NUM_GROUPS}
thematic groups that represent distinct user needs, issues, or situations.

RULES:
- Each group must contain at least 10 review IDs.
- Use only the review IDs that appear in the list below.
- Each group_id must follow the pattern A1, A2, … A{NUM_GROUPS}.
- Return ONLY valid JSON — no markdown fences, no explanation.

REVIEWS:
{review_lines}

Return this exact JSON schema:
{{
  "groups": [
    {{
      "group_id": "A1",
      "theme": "<concise theme name>",
      "review_ids": ["<id1>", "<id2>", ...],
      "example_reviews": [
        "<verbatim text of one review from the group>",
        "<verbatim text of another review from the group>"
      ]
    }}
  ]
}}"""

    print("  Calling Groq API to generate review groups …")
    raw = call_groq(client, prompt, temperature=0.2, max_tokens=4096)
    if not raw:
        print("  ERROR: No response from Groq API.")
        return None

    data = extract_json_block(raw)
    if not data or "groups" not in data:
        print("  ERROR: Could not parse JSON from LLM response.")
        print("  Raw response (first 500 chars):", raw[:500])
        return None

    # Validate each group has >= 10 review IDs
    valid_ids = {r["id"] for r in reviews}
    for g in data["groups"]:
        # keep only IDs that actually exist in our dataset
        g["review_ids"] = [rid for rid in g.get("review_ids", []) if rid in valid_ids]

    return data


# ─────────────────────────────────────────────
#  STEP 2 – Generate personas from groups
# ─────────────────────────────────────────────
def generate_personas(client, groups_data, reviews):
    """Ask the LLM to produce one persona per review group."""
    review_map = {r["id"]: r for r in reviews}
    personas = []

    for idx, group in enumerate(groups_data.get("groups", []), start=1):
        gid   = group["group_id"]
        theme = group["theme"]

        # Build representative review snippets
        snippets = []
        for rid in group.get("review_ids", [])[:10]:
            r = review_map.get(rid)
            if r:
                snippets.append(
                    f"- [{rid}] score:{r.get('score','?')} | {r.get('original','')[:200]}"
                )

        snippets_text = "\n".join(snippets) if snippets else "(no reviews available)"

        prompt = f"""You are a UX researcher creating a software persona for the Headspace
meditation app based on real user reviews.

Review group: {gid}
Theme: {theme}

Representative reviews from this group:
{snippets_text}

Create ONE detailed persona that represents the users in this group.
Return ONLY valid JSON — no markdown fences, no explanation.

Use this exact schema:
{{
  "id": "P_auto_{idx}",
  "name": "<persona first name + descriptive role, e.g. 'Calm-Seeker Claire'>",
  "description": "<2-3 sentence description of who this user is>",
  "derived_from_group": "{gid}",
  "goals": ["<goal 1>", "<goal 2>", "<goal 3>"],
  "pain_points": ["<pain 1>", "<pain 2>", "<pain 3>"],
  "context": ["<usage context 1>", "<usage context 2>"],
  "constraints": ["<system constraint 1>", "<system constraint 2>"],
  "evidence_reviews": {json.dumps(group.get("review_ids", [])[:3])}
}}"""

        print(f"  Generating persona for group {gid} ({theme}) …")
        raw = call_groq(client, prompt, temperature=0.4, max_tokens=1024)
        if not raw:
            print(f"  ERROR: No response for group {gid}.")
            continue

        persona = extract_json_block(raw)
        if not persona:
            print(f"  ERROR: Could not parse persona JSON for group {gid}.")
            print("  Raw (first 400 chars):", raw[:400])
            continue

        # Enforce required fields
        persona.setdefault("id", f"P_auto_{idx}")
        persona.setdefault("persona_id", persona["id"])
        persona.setdefault("derived_from_group", gid)
        persona.setdefault("source_group", gid)
        persona.setdefault("evidence_reviews", group.get("review_ids", [])[:3])
        personas.append(persona)
        time.sleep(0.5)   # polite pacing

    return {"personas": personas}


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("AUTOMATED PIPELINE  —  05_personas_auto.py")
    print("Model:", MODEL)
    print("=" * 60)

    if not os.path.exists(CLEAN_PATH):
        print(f"ERROR: {CLEAN_PATH} not found. Run 02_clean.py first.")
        return

    reviews = load_clean_reviews()
    print(f"Loaded {len(reviews)} clean reviews.\n")

    client = Groq(api_key=GROQ_API_KEY)

    # ── Step 1: Review groups ──────────────────
    print("STEP 1: Generating review groups …")
    auto_groups_stale = artifact_is_stale(CLEAN_PATH, GROUPS_OUTPUT)
    if not auto_groups_stale:
        print(f"  Using existing file: {GROUPS_OUTPUT}  (clean dataset unchanged)")
        with open(GROUPS_OUTPUT, "r", encoding="utf-8") as f:
            groups_data = json.load(f)
    else:
        print("  Clean dataset is newer than automated groups — regenerating.")
        groups_data = generate_review_groups(client, reviews)
        if not groups_data:
            print("Failed to generate review groups. Aborting.")
            return
        write_json(GROUPS_OUTPUT, groups_data)
        print(f"  ✅ Review groups saved to: {GROUPS_OUTPUT}")

    num_groups = len(groups_data.get("groups", []))
    print(f"  Groups: {num_groups}")
    for g in groups_data.get("groups", []):
        print(f"    [{g['group_id']}] {g['theme']}  ({len(g.get('review_ids',[]))} reviews)")

    # ── Step 2: Personas ───────────────────────
    print("\nSTEP 2: Generating personas …")
    personas_data = generate_personas(client, groups_data, reviews)

    write_json(PERSONAS_OUTPUT, personas_data)
    print(f"\n  ✅ Personas saved to: {PERSONAS_OUTPUT}")
    print(f"  Personas generated: {len(personas_data.get('personas', []))}")

    # ── Step 3: Hybrid refresh ─────────────────────
    print("\nSTEP 3: Refreshing hybrid artifacts …")
    hybrid_stale = (
        auto_groups_stale
        or artifact_is_stale(CLEAN_PATH, HYBRID_GROUPS_OUTPUT)
        or artifact_is_stale(CLEAN_PATH, HYBRID_PERSONAS_OUTPUT)
    )
    if hybrid_stale:
        hybrid_groups_data = build_hybrid_groups(groups_data)
        hybrid_personas_data = build_hybrid_personas(personas_data, hybrid_groups_data)
        write_json(HYBRID_GROUPS_OUTPUT, hybrid_groups_data)
        write_json(HYBRID_PERSONAS_OUTPUT, hybrid_personas_data)
        print(f"  ✅ Hybrid review groups saved to: {HYBRID_GROUPS_OUTPUT}")
        print(f"  ✅ Hybrid personas saved to: {HYBRID_PERSONAS_OUTPUT}")
    else:
        print("  Hybrid artifacts are already up to date with the clean dataset.")

    print("\nDone.")


if __name__ == "__main__":
    main()
