"""
BCI Test 2: Kernel Interaction Profile

Check if infrastructure classes cluster temporally around kernel operations.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.morphology import decompose_token

INFRASTRUCTURE_CLASSES = {44, 46, 42, 36}
KERNEL_MIDDLES = {'k', 'h', 'e'}  # Kernel operators by MIDDLE position (BCSC)

def main():
    print("=" * 70)
    print("BCI TEST 2: KERNEL INTERACTION PROFILE")
    print("=" * 70)

    ds = get_data_store()

    # Parse transcript to get token sequences per folio
    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"

    # Build per-folio token sequences with class assignments
    folio_sequences = defaultdict(list)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            line_num = parts[3].strip('"').strip()
            position = parts[4].strip('"').strip() if len(parts) > 4 else "0"
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            if transcriber != 'H' or language != 'B':
                continue

            morph = decompose_token(token)
            middle = morph.middle or ""
            classes = ds.middle_to_classes.get(middle, set())

            folio_sequences[folio].append({
                "token": token,
                "middle": middle,
                "classes": classes,
                "line": line_num,
                "pos": position
            })

    print(f"\nParsed {len(folio_sequences)} B folios")

    # For each infrastructure class occurrence, find distance to nearest kernel
    infra_distances = defaultdict(list)

    for folio, tokens in folio_sequences.items():
        # Find kernel positions (tokens with k, h, or e as MIDDLE)
        kernel_positions = []
        for i, t in enumerate(tokens):
            if t["middle"] in KERNEL_MIDDLES:
                kernel_positions.append(i)

        if not kernel_positions:
            continue

        # For each infrastructure occurrence, measure distance to nearest kernel
        for i, t in enumerate(tokens):
            for infra_class in INFRASTRUCTURE_CLASSES:
                if infra_class in t["classes"]:
                    min_dist = min(abs(i - kp) for kp in kernel_positions)
                    infra_distances[infra_class].append(min_dist)

    # Report
    print("\n" + "-" * 70)
    print("DISTANCE TO NEAREST KERNEL OPERATION")
    print("-" * 70)

    for infra_class in sorted(INFRASTRUCTURE_CLASSES):
        distances = infra_distances[infra_class]
        if distances:
            avg_dist = statistics.mean(distances)
            median_dist = statistics.median(distances)
            std_dist = statistics.stdev(distances) if len(distances) > 1 else 0

            print(f"\nClass {infra_class} ({len(distances)} occurrences):")
            print(f"  Mean distance: {avg_dist:.2f} tokens")
            print(f"  Median distance: {median_dist:.1f} tokens")
            print(f"  Std dev: {std_dist:.2f}")

            # Distribution buckets
            near = sum(1 for d in distances if d <= 2)
            mid = sum(1 for d in distances if 3 <= d <= 5)
            far = sum(1 for d in distances if d > 5)

            print(f"  Near (0-2): {near} ({100*near/len(distances):.1f}%)")
            print(f"  Mid (3-5): {mid} ({100*mid/len(distances):.1f}%)")
            print(f"  Far (>5): {far} ({100*far/len(distances):.1f}%)")

    # Interpretation
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)

    all_distances = []
    for dists in infra_distances.values():
        all_distances.extend(dists)

    if all_distances:
        overall_mean = statistics.mean(all_distances)
        near_pct = sum(1 for d in all_distances if d <= 2) / len(all_distances)

        if near_pct > 0.5:
            print(f"\nInfrastructure classes are CLUSTERED near kernel ({near_pct:.1%} within 2 tokens)")
            print("-> They appear to be MEDIATORS for kernel operations")
        else:
            print(f"\nInfrastructure classes are DISTRIBUTED ({near_pct:.1%} within 2 tokens)")
            print("-> They appear to be NEUTRAL CARRIERS, not kernel-specific")

    # Save results
    output = {
        "infrastructure_classes": sorted(INFRASTRUCTURE_CLASSES),
        "kernel_middles": sorted(KERNEL_MIDDLES),
        "distance_stats": {
            str(k): {
                "count": len(v),
                "mean": statistics.mean(v) if v else 0,
                "median": statistics.median(v) if v else 0
            }
            for k, v in infra_distances.items()
        }
    }

    output_path = PROJECT_ROOT / "results" / "bci_kernel_interaction.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
