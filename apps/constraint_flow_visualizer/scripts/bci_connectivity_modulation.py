"""
BCI Test 3: Connectivity vs Modulation

Check if infrastructure classes enable paths or modulate path density.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.morphology import decompose_token

INFRASTRUCTURE_CLASSES = {44, 46, 42, 36}

def compute_transition_density(folio_tokens, ds):
    """Compute class transition graph density for a folio."""
    if len(folio_tokens) < 2:
        return {"transitions": 0, "unique_pairs": 0, "density": 0}

    # Build class sequence
    class_sequence = []
    for t in folio_tokens:
        classes = ds.middle_to_classes.get(t.get("middle", ""), set())
        class_sequence.append(classes)

    # Count transitions
    transitions = defaultdict(int)
    for i in range(len(class_sequence) - 1):
        for c1 in class_sequence[i]:
            for c2 in class_sequence[i + 1]:
                transitions[(c1, c2)] += 1

    total_transitions = sum(transitions.values())
    unique_pairs = len(transitions)

    # Density = unique pairs / possible pairs (49*49)
    density = unique_pairs / (49 * 49) if unique_pairs > 0 else 0

    return {
        "transitions": total_transitions,
        "unique_pairs": unique_pairs,
        "density": density
    }

def main():
    print("=" * 70)
    print("BCI TEST 3: CONNECTIVITY vs MODULATION")
    print("=" * 70)

    ds = get_data_store()

    # Parse transcript
    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"

    folio_tokens = defaultdict(list)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            if transcriber != 'H' or language != 'B':
                continue

            morph = decompose_token(token)
            folio_tokens[folio].append({"token": token, "middle": morph.middle or ""})

    # Classify folios by infrastructure presence
    with_infra = []
    without_infra = []

    for folio, footprint in ds.b_folio_class_footprints.items():
        has_infra = bool(footprint & INFRASTRUCTURE_CLASSES)
        density_info = compute_transition_density(folio_tokens.get(folio, []), ds)

        if has_infra:
            with_infra.append((folio, density_info))
        else:
            without_infra.append((folio, density_info))

    print(f"\nFolios WITH infrastructure: {len(with_infra)}")
    print(f"Folios WITHOUT infrastructure: {len(without_infra)}")

    # Compare densities
    print("\n" + "-" * 70)
    print("TRANSITION DENSITY COMPARISON")
    print("-" * 70)

    avg_with = 0
    avg_trans_with = 0
    avg_without = 0
    avg_trans_without = 0

    if with_infra:
        avg_with = sum(d["density"] for _, d in with_infra) / len(with_infra)
        avg_trans_with = sum(d["transitions"] for _, d in with_infra) / len(with_infra)
        print(f"\nWITH infrastructure ({len(with_infra)} folios):")
        print(f"  Avg transition density: {avg_with:.4f}")
        print(f"  Avg transitions: {avg_trans_with:.1f}")

    if without_infra:
        avg_without = sum(d["density"] for _, d in without_infra) / len(without_infra)
        avg_trans_without = sum(d["transitions"] for _, d in without_infra) / len(without_infra)
        print(f"\nWITHOUT infrastructure ({len(without_infra)} folios):")
        print(f"  Avg transition density: {avg_without:.4f}")
        print(f"  Avg transitions: {avg_trans_without:.1f}")

        print(f"\n  Folios without infrastructure: {[f for f, _ in without_infra]}")

    # Interpretation
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)

    if with_infra and without_infra:
        ratio = avg_with / avg_without if avg_without > 0 else float('inf')
        if 0.8 < ratio < 1.2:
            print(f"\nSimilar density (ratio {ratio:.2f})")
            print("-> Infrastructure classes ENABLE paths (binary presence/absence)")
        else:
            print(f"\nDifferent density (ratio {ratio:.2f})")
            print("-> Infrastructure classes MODULATE path structure")
    else:
        print("\nInsufficient data for comparison (need folios both with and without)")

    # Save results
    output_path = PROJECT_ROOT / "results" / "bci_connectivity_modulation.json"
    output_path.write_text(json.dumps({
        "with_infra_count": len(with_infra),
        "without_infra_count": len(without_infra),
        "without_infra_folios": [f for f, _ in without_infra],
        "avg_density_with": avg_with,
        "avg_density_without": avg_without
    }, indent=2))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
