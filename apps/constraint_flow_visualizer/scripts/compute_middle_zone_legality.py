"""
Compute per-MIDDLE zone legality from AZC corpus.

This extracts per-MIDDLE per-zone occurrence counts directly from AZC tokens,
preserving actual zeros (unlike cluster means which erase them).

Per expert diagnosis: Cluster mean profiles are NOT legality masks.
Zeros are the signal. Cluster means hide them.

Zone data source: Transcript column 10 (`placement`) contains zone codes.
Filter: transcriber == 'H' (PRIMARY), language == 'NA' (AZC tokens only).
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add parent directories to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.morphology import decompose_token

# Zone consolidation (per existing pattern in MIDDLE_ZONE_SURVIVAL phase)
# R1-R4 -> R, S0-S3 -> S, C/C1/C2 -> C, P -> P
ZONE_MAP = {
    'C': 'C', 'C1': 'C', 'C2': 'C',
    'P': 'P',
    'R': 'R', 'R1': 'R', 'R2': 'R', 'R3': 'R', 'R4': 'R',
    'S': 'S', 'S0': 'S', 'S1': 'S', 'S2': 'S', 'S3': 'S'
}


def main():
    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"

    if not transcript_path.exists():
        print(f"ERROR: Transcript not found at {transcript_path}")
        return

    # Build per-MIDDLE zone counts
    middle_data = defaultdict(lambda: Counter())
    total_tokens = 0
    skipped_no_placement = 0
    skipped_no_middle = 0

    with open(transcript_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        print(f"Transcript columns: {len(header)}")

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            placement = parts[10].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            # MANDATORY: H-track only, AZC only (language == 'NA')
            if transcriber != 'H' or language != 'NA':
                continue

            total_tokens += 1

            # Map placement to base zone
            base_zone = ZONE_MAP.get(placement)
            if not base_zone:
                skipped_no_placement += 1
                continue

            # Decompose token to get MIDDLE
            morph = decompose_token(token)
            middle = morph.middle if morph.middle else ""
            if not middle:
                skipped_no_middle += 1
                continue

            # Count occurrence (zeros automatically preserved via Counter)
            middle_data[middle][base_zone] += 1

    print(f"\nProcessed {total_tokens} AZC tokens (H-track)")
    print(f"  Skipped (no placement): {skipped_no_placement}")
    print(f"  Skipped (no MIDDLE): {skipped_no_middle}")
    print(f"  Unique MIDDLEs found: {len(middle_data)}")

    # Build output with binary legality
    output = {}
    MIN_OCCURRENCES = 5  # Match existing threshold from MIDDLE_ZONE_SURVIVAL

    qualified = 0
    below_threshold = 0

    for middle, zone_counts in middle_data.items():
        total = sum(zone_counts.values())
        if total < MIN_OCCURRENCES:
            below_threshold += 1
            continue

        qualified += 1

        # Explicitly include zeros for all zones
        counts = {
            'C': zone_counts.get('C', 0),
            'P': zone_counts.get('P', 0),
            'R': zone_counts.get('R', 0),
            'S': zone_counts.get('S', 0)
        }

        # Binary legality: count > 0 = legal
        legal_zones = [z for z, c in counts.items() if c > 0]

        output[middle] = {
            'counts': counts,
            'total': total,
            'legal_zones': sorted(legal_zones)
        }

    print(f"\nQualified MIDDLEs (>={MIN_OCCURRENCES} occurrences): {qualified}")
    print(f"Below threshold: {below_threshold}")

    # Save
    output_path = PROJECT_ROOT / "results" / "middle_zone_legality.json"
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True))
    print(f"\nSaved to: {output_path}")

    # Zone pattern distribution (CRITICAL CHECK)
    patterns = defaultdict(list)
    for middle, data in output.items():
        pattern = tuple(sorted(data['legal_zones']))
        patterns[pattern].append(middle)

    print("\n" + "=" * 60)
    print("Zone legality patterns (zeros = illegal):")
    print("=" * 60)

    all_legal_count = 0
    partial_count = 0

    for pattern, middles in sorted(patterns.items(), key=lambda x: -len(x[1])):
        if pattern == ('C', 'P', 'R', 'S'):
            all_legal_count = len(middles)
            marker = " <-- ALL ZONES LEGAL"
        else:
            partial_count += len(middles)
            marker = ""

        print(f"  {pattern}: {len(middles)} MIDDLEs{marker}")
        if len(middles) <= 5:
            print(f"    Examples: {middles}")
        else:
            print(f"    Examples: {middles[:5]}...")

    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)
    print(f"  All-zone legal: {all_legal_count}")
    print(f"  Partial legality (has zeros): {partial_count}")

    if partial_count == 0:
        print("\n  WARNING: No MIDDLEs have zone restrictions!")
        print("  This suggests the data extraction is still wrong.")
    else:
        pct = 100 * partial_count / (all_legal_count + partial_count)
        print(f"\n  {pct:.1f}% of MIDDLEs have zone restrictions.")
        print("  This is the expected behavior - zeros create differentiation.")


if __name__ == "__main__":
    main()
