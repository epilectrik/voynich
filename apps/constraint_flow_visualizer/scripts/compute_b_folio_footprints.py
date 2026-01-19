"""
Compute instruction class footprints for each B folio.

This is a one-time extraction that creates:
  results/b_folio_class_footprints.json

For each B folio, determines which instruction classes it uses
by parsing tokens → decomposing MIDDLEs → mapping to classes.

Per C121, C440, C482: Grammar is universal, B is uniformly sourced,
and this is empirical corpus extraction (not REGIME derivation).
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directories to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.morphology import decompose_token


def main():
    # Load MIDDLE → class mapping
    middle_class_path = PROJECT_ROOT / "phases" / "AZC_REACHABILITY_SUPPRESSION" / "middle_class_index.json"
    if not middle_class_path.exists():
        print(f"ERROR: {middle_class_path} not found")
        return

    middle_class_index = json.loads(middle_class_path.read_text())
    middle_to_classes = middle_class_index['middle_to_classes']

    print(f"Loaded MIDDLE->class mapping: {len(middle_to_classes)} MIDDLEs")

    # Parse transcript for B folios
    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"
    if not transcript_path.exists():
        print(f"ERROR: {transcript_path} not found")
        return

    b_folio_classes = defaultdict(set)
    token_count = 0
    unknown_middles = set()

    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            # Filter: PRIMARY transcriber, Currier B only
            if transcriber != 'H' or language != 'B':
                continue

            if not token:
                continue

            token_count += 1

            # Decompose token to get MIDDLE
            morph = decompose_token(token)
            middle = morph.middle if morph.middle else ""

            # Map MIDDLE → classes
            classes = middle_to_classes.get(middle)
            if classes:
                b_folio_classes[folio].update(classes)
            else:
                # Track unknown MIDDLEs for diagnostics
                if middle:
                    unknown_middles.add(middle)

    # Convert to sorted lists for JSON
    output = {folio: sorted(classes) for folio, classes in sorted(b_folio_classes.items())}

    # Save result
    output_path = PROJECT_ROOT / "results" / "b_folio_class_footprints.json"
    output_path.write_text(json.dumps(output, indent=2))

    print(f"\n=== B Folio Class Footprints ===")
    print(f"Processed {token_count} B tokens")
    print(f"Found {len(output)} B folios")
    print(f"Unknown MIDDLEs (not in class index): {len(unknown_middles)}")

    if unknown_middles:
        print(f"  Examples: {list(unknown_middles)[:10]}")

    # Show distribution
    class_counts = defaultdict(int)
    for classes in output.values():
        for c in classes:
            class_counts[c] += 1

    print(f"\nClass coverage across B folios:")
    print(f"  Classes appearing in all folios: {sum(1 for c, n in class_counts.items() if n == len(output))}")
    print(f"  Classes appearing in >50% folios: {sum(1 for c, n in class_counts.items() if n > len(output)//2)}")

    # Show a few example folios
    print(f"\nExample footprints:")
    for folio in list(output.keys())[:3]:
        print(f"  {folio}: {len(output[folio])} classes - {output[folio][:10]}...")

    print(f"\nOutput saved to: {output_path}")


if __name__ == "__main__":
    main()
