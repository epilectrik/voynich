"""
Phase 4: Folio Footprint Validity Audit

Check if B folio class footprints are overstated.
"""
import sys
from pathlib import Path
from collections import defaultdict
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.morphology import decompose_token


def compute_line_level_footprints(ds) -> dict:
    """
    Compute class footprints at LINE level, not folio level.

    This distinguishes:
    - REQUIRED_ALWAYS: class appears in EVERY line of the folio
    - REQUIRED_SOMETIMES: class appears in SOME lines
    - OPTIONAL: class appears rarely
    """
    transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"

    # Track class usage per folio-line
    folio_line_classes = defaultdict(lambda: defaultdict(set))
    folio_line_count = defaultdict(set)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            token = parts[0].strip('"').strip()
            folio = parts[2].strip('"').strip()
            line_num = parts[3].strip('"').strip()
            language = parts[6].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            if transcriber != 'H' or language != 'B':
                continue

            folio_line_count[folio].add(line_num)

            morph = decompose_token(token)
            middle = morph.middle or ""

            classes = ds.middle_to_classes.get(middle, set())
            folio_line_classes[folio][line_num].update(classes)

    # Compute per-class presence statistics
    footprint_analysis = {}

    for folio, line_classes in folio_line_classes.items():
        num_lines = len(folio_line_count[folio])
        class_presence = defaultdict(int)

        for line_num, classes in line_classes.items():
            for cls in classes:
                class_presence[cls] += 1

        # Classify each class
        always = set()    # In ALL lines (100%)
        sometimes = set() # In >50% of lines
        rarely = set()    # In <50% of lines

        for cls, count in class_presence.items():
            pct = count / num_lines if num_lines > 0 else 0
            if pct == 1.0:
                always.add(cls)
            elif pct >= 0.5:
                sometimes.add(cls)
            else:
                rarely.add(cls)

        footprint_analysis[folio] = {
            "num_lines": num_lines,
            "always": sorted(always),
            "sometimes": sorted(sometimes),
            "rarely": sorted(rarely),
            "current_footprint": sorted(ds.b_folio_class_footprints.get(folio, set()))
        }

    return footprint_analysis


def main():
    print("=" * 70)
    print("PHASE 4: FOLIO FOOTPRINT VALIDITY AUDIT")
    print("=" * 70)

    ds = get_data_store()

    # Compute line-level footprints
    print("\nComputing line-level class footprints...")
    footprints = compute_line_level_footprints(ds)

    print(f"Analyzed {len(footprints)} B folios")

    # Focus on blocking classes (from Phase 1/previous investigation)
    blocking_classes = {36, 44, 46, 48}

    print("\n" + "-" * 70)
    print(f"ANALYSIS OF BLOCKING CLASSES: {sorted(blocking_classes)}")
    print("-" * 70)

    # For each blocking class, check its presence pattern
    for class_id in sorted(blocking_classes):
        always_count = 0
        sometimes_count = 0
        rarely_count = 0
        absent_count = 0

        for folio, analysis in footprints.items():
            if class_id in analysis["always"]:
                always_count += 1
            elif class_id in analysis["sometimes"]:
                sometimes_count += 1
            elif class_id in analysis["rarely"]:
                rarely_count += 1
            else:
                absent_count += 1

        total = len(footprints)
        print(f"\nClass {class_id}:")
        print(f"  Always (100%): {always_count}/{total} folios ({100*always_count/total:.1f}%)")
        print(f"  Sometimes (50-99%): {sometimes_count}/{total} folios ({100*sometimes_count/total:.1f}%)")
        print(f"  Rarely (<50%): {rarely_count}/{total} folios ({100*rarely_count/total:.1f}%)")
        print(f"  Absent: {absent_count}/{total} folios ({100*absent_count/total:.1f}%)")

    # Compare current footprints vs ALWAYS-only footprints
    print("\n" + "-" * 70)
    print("FOOTPRINT STRICTNESS COMPARISON")
    print("-" * 70)

    # Check if blocking classes are in ALWAYS vs SOMETIMES
    always_blocking_folios = 0
    sometimes_blocking_folios = 0
    rarely_blocking_folios = 0

    for folio, analysis in footprints.items():
        blocking_in_always = blocking_classes & set(analysis["always"])
        blocking_in_sometimes = blocking_classes & set(analysis["sometimes"])
        blocking_in_rarely = blocking_classes & set(analysis["rarely"])

        if blocking_in_always:
            always_blocking_folios += 1
        if blocking_in_sometimes:
            sometimes_blocking_folios += 1
        if blocking_in_rarely:
            rarely_blocking_folios += 1

    total_folios = len(footprints)
    print(f"\nFolios where blocking classes appear as ALWAYS: {always_blocking_folios}/{total_folios}")
    print(f"Folios where blocking classes appear as SOMETIMES: {sometimes_blocking_folios}/{total_folios}")
    print(f"Folios where blocking classes appear as RARELY: {rarely_blocking_folios}/{total_folios}")

    # Compute revised footprint sizes
    print("\n" + "-" * 70)
    print("FOOTPRINT SIZE COMPARISON")
    print("-" * 70)

    current_sizes = []
    always_sizes = []

    for folio, analysis in footprints.items():
        current_sizes.append(len(analysis["current_footprint"]))
        always_sizes.append(len(analysis["always"]))

    avg_current = sum(current_sizes) / len(current_sizes) if current_sizes else 0
    avg_always = sum(always_sizes) / len(always_sizes) if always_sizes else 0

    print(f"\nAverage classes per folio (current footprint): {avg_current:.1f}")
    print(f"Average classes per folio (ALWAYS-only): {avg_always:.1f}")
    print(f"Reduction factor: {avg_current/avg_always:.2f}x" if avg_always > 0 else "N/A")

    # Detailed folio-by-folio analysis
    print("\n" + "-" * 70)
    print("SAMPLE FOLIO ANALYSIS (first 10)")
    print("-" * 70)

    for folio, analysis in list(footprints.items())[:10]:
        current = set(analysis["current_footprint"])
        always = set(analysis["always"])
        sometimes = set(analysis["sometimes"])

        in_current_not_always = current - always
        blocking_in_current = blocking_classes & current
        blocking_in_always = blocking_classes & always

        print(f"\n{folio} ({analysis['num_lines']} lines):")
        print(f"  Current footprint: {len(current)} classes")
        print(f"  ALWAYS classes: {len(always)}")
        print(f"  In current but not ALWAYS: {len(in_current_not_always)}")
        if blocking_in_current:
            print(f"  Blocking classes in current: {sorted(blocking_in_current)}")
        if blocking_in_always:
            print(f"  Blocking classes in ALWAYS: {sorted(blocking_in_always)}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if sometimes_blocking_folios > always_blocking_folios:
        print("\nBlocking classes are mostly SOMETIMES, not ALWAYS")
        print("-> Footprints are overstated")
        print("-> Use ALWAYS-only footprints for reachability")
        print("\nRECOMMENDATION: Revise B folio footprints to only include")
        print("classes that appear in 100% of folio lines.")
    else:
        print("\nBlocking classes are truly required (appear in ALWAYS category)")
        print("-> These classes are connectivity infrastructure")
        print("-> They should be immune to AZC pruning")
        print("\nRECOMMENDATION: Add blocking classes to infrastructure tier")
        print("(immune to AZC vocabulary pruning).")

    # Save results
    output_path = PROJECT_ROOT / "results" / "phase4_footprint_audit.json"
    output_path.write_text(json.dumps({
        "blocking_classes": sorted(blocking_classes),
        "total_folios": total_folios,
        "always_blocking_folios": always_blocking_folios,
        "sometimes_blocking_folios": sometimes_blocking_folios,
        "rarely_blocking_folios": rarely_blocking_folios,
        "avg_current_footprint_size": avg_current,
        "avg_always_footprint_size": avg_always,
        "folio_analysis": {
            k: {
                "num_lines": v["num_lines"],
                "current_size": len(v["current_footprint"]),
                "always_size": len(v["always"]),
                "sometimes_size": len(v["sometimes"]),
                "rarely_size": len(v["rarely"]),
                "blocking_in_always": sorted(blocking_classes & set(v["always"])),
                "blocking_in_sometimes": sorted(blocking_classes & set(v["sometimes"]))
            }
            for k, v in footprints.items()
        }
    }, indent=2, default=str))
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
