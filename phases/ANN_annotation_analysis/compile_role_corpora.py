#!/usr/bin/env python3
"""
Compile role-conditioned text corpora for vocabulary analysis.

Workstream 3: Role-conditioned token analysis with pre-registered invalidation.
"""

import json
import csv
from collections import defaultdict
from datetime import datetime
from annotation_config import load_folio_metadata

# Hub heading to role mapping
HUB_HEADING_ROLES = {
    "tol": "opener",
    "paiin": "opener",
    "par": "opener",
    "pchor": "opener",
    "pol": "closer",
    "tor": "closer",  # f96r - excluded but mapping kept
    "sho": "support",
    "kor": "support"
}


def load_transcription():
    """Load transcription data."""
    rows = []
    with open("data/transcriptions/interlinear_full_words.txt", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def get_hub_folios():
    """Get hub folios from metadata."""
    metadata = load_folio_metadata()
    hub_folios = {}

    for folio_id, meta in metadata.items():
        if meta.hub_status == "hub":
            hub_folios[folio_id] = {
                "heading": meta.heading,
                "prefix": meta.opening_prefix,
                "role": meta.category_role
            }

    return hub_folios


def extract_role_corpora(transcription, hub_folios):
    """
    Extract text corpora for each functional role.

    Includes:
    - Full text from Currier A entries with hub headings
    - Context windows around hub references in B (future extension)
    """
    role_corpora = defaultdict(list)
    role_token_counts = defaultdict(int)
    role_folio_counts = defaultdict(int)
    folio_texts = defaultdict(list)

    # Group transcription by folio
    for row in transcription:
        folio = row.get("folio", "")
        word = row.get("word", "")
        if folio and word:
            folio_texts[folio].append(word)

    # Extract hub folio texts
    for folio_id, hub_info in hub_folios.items():
        role = hub_info["role"]
        if not role:
            continue

        if folio_id in folio_texts:
            words = folio_texts[folio_id]
            role_corpora[role].extend(words)
            role_token_counts[role] += len(words)
            role_folio_counts[role] += 1

    # Also collect baseline (non-hub) text
    baseline_words = []
    hub_folio_ids = set(hub_folios.keys())

    for folio_id, words in folio_texts.items():
        if folio_id not in hub_folio_ids:
            baseline_words.extend(words)

    return {
        "role_corpora": dict(role_corpora),
        "role_token_counts": dict(role_token_counts),
        "role_folio_counts": dict(role_folio_counts),
        "baseline_words": baseline_words,
        "baseline_token_count": len(baseline_words)
    }


def compute_token_frequencies(corpora_data):
    """Compute token frequencies by role and baseline."""
    role_freqs = {}

    for role, words in corpora_data["role_corpora"].items():
        freq = defaultdict(int)
        for word in words:
            freq[word] += 1
        role_freqs[role] = dict(freq)

    baseline_freq = defaultdict(int)
    for word in corpora_data["baseline_words"]:
        baseline_freq[word] += 1

    return {
        "role_frequencies": role_freqs,
        "baseline_frequency": dict(baseline_freq)
    }


def compute_enrichment(freqs, corpora_data):
    """
    Compute enrichment scores for each token in each role.

    enrichment = (role_freq / role_total) / (baseline_freq / baseline_total)
    """
    enrichment = defaultdict(lambda: defaultdict(dict))

    baseline_total = corpora_data["baseline_token_count"]
    baseline_freq = freqs["baseline_frequency"]

    for role, role_freq in freqs["role_frequencies"].items():
        role_total = corpora_data["role_token_counts"][role]

        for token, count in role_freq.items():
            role_rate = count / role_total if role_total > 0 else 0
            baseline_count = baseline_freq.get(token, 0)
            baseline_rate = baseline_count / baseline_total if baseline_total > 0 else 0

            if baseline_rate > 0:
                enrich = role_rate / baseline_rate
            else:
                enrich = float("inf") if role_rate > 0 else 0

            enrichment[role][token] = {
                "role_count": count,
                "role_rate": round(role_rate, 6),
                "baseline_count": baseline_count,
                "baseline_rate": round(baseline_rate, 6),
                "enrichment": round(enrich, 3) if enrich != float("inf") else "INF"
            }

    return dict(enrichment)


def identify_role_enriched_tokens(enrichment, corpora_data, threshold=2.0, min_count=3):
    """
    Identify tokens enriched in each role.

    Criteria:
    - enrichment > threshold (default 2.0)
    - raw count >= min_count (default 3)
    - appears in >= 2 entries of that role (need folio-level tracking)
    """
    enriched = {}

    for role, tokens in enrichment.items():
        role_enriched = []

        for token, stats in tokens.items():
            if stats["enrichment"] == "INF":
                enrich = 100  # Cap infinity
            else:
                enrich = stats["enrichment"]

            if enrich >= threshold and stats["role_count"] >= min_count:
                role_enriched.append({
                    "token": token,
                    "enrichment": stats["enrichment"],
                    "role_count": stats["role_count"],
                    "baseline_count": stats["baseline_count"]
                })

        # Sort by enrichment
        role_enriched.sort(key=lambda x: 100 if x["enrichment"] == "INF" else x["enrichment"], reverse=True)
        enriched[role] = role_enriched[:20]  # Top 20

    return enriched


def identify_role_exclusive_tokens(freqs):
    """Find tokens that appear ONLY in one role's corpus."""
    exclusive = defaultdict(list)

    # Get all tokens across all roles
    all_role_tokens = {}
    for role, freq in freqs["role_frequencies"].items():
        all_role_tokens[role] = set(freq.keys())

    # Find exclusive tokens
    for role, tokens in all_role_tokens.items():
        other_tokens = set()
        for other_role, other_set in all_role_tokens.items():
            if other_role != role:
                other_tokens.update(other_set)

        # Also check baseline
        baseline_tokens = set(freqs["baseline_frequency"].keys())
        other_tokens.update(baseline_tokens)

        exclusive_set = tokens - other_tokens
        exclusive[role] = list(exclusive_set)

    return dict(exclusive)


def check_invalidation_rules(corpora_data):
    """Check pre-registered invalidation rules for vocabulary analysis."""
    rules = {
        "min_folios_per_role": 3,
        "min_tokens_per_role": 500
    }

    violations = []

    for role in ["opener", "closer", "support"]:
        folio_count = corpora_data["role_folio_counts"].get(role, 0)
        token_count = corpora_data["role_token_counts"].get(role, 0)

        if folio_count < rules["min_folios_per_role"]:
            violations.append({
                "rule": "min_folios_per_role",
                "role": role,
                "actual": folio_count,
                "required": rules["min_folios_per_role"],
                "status": "VIOLATED"
            })

        if token_count < rules["min_tokens_per_role"]:
            violations.append({
                "rule": "min_tokens_per_role",
                "role": role,
                "actual": token_count,
                "required": rules["min_tokens_per_role"],
                "status": "VIOLATED"
            })

    return {
        "rules": rules,
        "violations": violations,
        "valid": len(violations) == 0,
        "note": "Replication (Workstream 1) must also pass for confirmatory status"
    }


def main():
    """Compile role-conditioned text corpora."""
    print("=" * 60)
    print("ROLE-CONDITIONED CORPUS COMPILATION")
    print("=" * 60)

    # Load data
    transcription = load_transcription()
    hub_folios = get_hub_folios()

    print(f"\nTranscription records: {len(transcription)}")
    print(f"\nHub folios:")
    for folio_id, info in hub_folios.items():
        print(f"  {folio_id}: {info['heading']} ({info['role']})")

    # Extract corpora
    corpora_data = extract_role_corpora(transcription, hub_folios)

    print("\nRole corpus summary:")
    for role in ["opener", "closer", "support"]:
        count = corpora_data["role_token_counts"].get(role, 0)
        folios = corpora_data["role_folio_counts"].get(role, 0)
        print(f"  {role.upper()}: {count} tokens from {folios} folios")

    print(f"  BASELINE: {corpora_data['baseline_token_count']} tokens")

    # Compute frequencies and enrichment
    freqs = compute_token_frequencies(corpora_data)
    enrichment = compute_enrichment(freqs, corpora_data)

    # Identify enriched and exclusive tokens
    enriched = identify_role_enriched_tokens(enrichment, corpora_data)
    exclusive = identify_role_exclusive_tokens(freqs)

    print("\nEnriched tokens (top 5 per role):")
    for role, tokens in enriched.items():
        print(f"  {role.upper()}:")
        for t in tokens[:5]:
            print(f"    {t['token']}: enrichment={t['enrichment']}, count={t['role_count']}")

    print("\nRole-exclusive tokens:")
    for role, tokens in exclusive.items():
        print(f"  {role.upper()}: {len(tokens)} exclusive tokens")

    # Check invalidation
    validation = check_invalidation_rules(corpora_data)

    print("\nValidation status:")
    if validation["valid"]:
        print("  ALL RULES PASSED")
    else:
        print("  VIOLATIONS DETECTED:")
        for v in validation["violations"]:
            print(f"    {v['role']}: {v['rule']} - {v['actual']} < {v['required']}")

    # Output
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "transcription_records": len(transcription),
            "hub_folios_analyzed": len(hub_folios)
        },
        "corpora_summary": {
            "role_token_counts": corpora_data["role_token_counts"],
            "role_folio_counts": corpora_data["role_folio_counts"],
            "baseline_token_count": corpora_data["baseline_token_count"]
        },
        "role_enriched_tokens": enriched,
        "role_exclusive_tokens": exclusive,
        "validation": validation,
        "enrichment_detail": {
            role: list(tokens.items())[:50]  # Sample for each role
            for role, tokens in enrichment.items()
        }
    }

    output_path = "role_conditioned_vocabulary.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Output saved to: {output_path}")
    print(f"{'=' * 60}")

    return output


if __name__ == "__main__":
    main()
