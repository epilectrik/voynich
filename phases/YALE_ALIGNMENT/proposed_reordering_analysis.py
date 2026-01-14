"""
Detailed Analysis of Proposed Folio Reordering
Phase: YALE_ALIGNMENT

Creates a comprehensive view of the proposed original order.
"""

import json
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_folio_features():
    """Load structural features for all B folios."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    cart_path = results_dir / "b_design_space_cartography.json"

    with open(cart_path) as f:
        cart_data = json.load(f)

    folios = {}
    for folio, data in cart_data.get("folio_positions", {}).items():
        folios[folio] = {
            "hazard_density": data.get("hazard_density", 0),
            "escape_density": data.get("escape_density", 0),
            "cei_total": data.get("cei_total", 0),
            "link_density": data.get("link_density", 0),
            "execution_tension": data.get("execution_tension", 0),
            "regime": data.get("regime", "UNKNOWN")
        }

    return folios


def get_section(folio):
    """Determine manuscript section from folio number."""
    match = re.match(r'f(\d+)', folio.lower())
    if not match:
        return "UNKNOWN"
    num = int(match.group(1))

    if num <= 66:
        return "HERBAL"
    elif 67 <= num <= 73:
        return "ASTRO"  # Not in B corpus
    elif 75 <= num <= 84:
        return "BALNEO"
    elif 85 <= num <= 86:
        return "ROSETTE"
    elif 87 <= num <= 102:
        return "PHARMA"
    elif 103 <= num <= 116:
        return "STARRED"
    else:
        return "UNKNOWN"


def get_scribe(folio):
    """Assign probable scribe based on section (from Davis)."""
    match = re.match(r'f(\d+)', folio.lower())
    if not match:
        return "?"
    num = int(match.group(1))

    if num <= 66:
        return "1"  # Herbal - mostly Scribe 1
    elif 67 <= num <= 73:
        return "4"  # Astronomical - Scribe 4
    elif 75 <= num <= 84:
        return "2"  # Balneological - Scribe 2
    elif 85 <= num <= 86:
        return "2"  # Rosettes - Scribe 2
    elif 87 <= num <= 102:
        return "1"  # Pharmaceutical - Scribe 1
    elif 103 <= num <= 116:
        return "3"  # Starred - Scribe 3
    return "?"


def main():
    print("=" * 80)
    print("PROPOSED FOLIO REORDERING - DETAILED ANALYSIS")
    print("=" * 80)

    # Load data
    features = load_folio_features()

    # Load reordering results
    results_dir = Path(__file__).parent.parent.parent / "results"
    with open(results_dir / "folio_reordering.json") as f:
        reorder_data = json.load(f)

    proposed_order = reorder_data["optimal_order"]["sequence"]

    print(f"\nAnalyzing {len(proposed_order)} folios in proposed order\n")

    # Create detailed table
    print("-" * 80)
    print(f"{'Pos':>3} | {'Folio':<8} | {'Regime':<9} | {'Section':<8} | {'Scribe':<6} | "
          f"{'Hazard':>7} | {'CEI':>6} | {'Tension':>8}")
    print("-" * 80)

    # Track progression
    prev_regime = None
    regime_changes = 0
    section_blocks = []
    current_section = None

    for i, folio in enumerate(proposed_order):
        data = features[folio]
        regime = data['regime']
        section = get_section(folio)
        scribe = get_scribe(folio)

        # Track regime changes
        if prev_regime and regime != prev_regime:
            regime_changes += 1
        prev_regime = regime

        # Track section blocks
        if section != current_section:
            if current_section:
                section_blocks.append(current_section)
            current_section = section

        print(f"{i+1:>3} | {folio:<8} | {regime:<9} | {section:<8} | {scribe:^6} | "
              f"{data['hazard_density']:>7.3f} | {data['cei_total']:>6.3f} | {data['execution_tension']:>8.3f}")

    section_blocks.append(current_section)

    # Summary statistics
    print("\n" + "=" * 80)
    print("PROGRESSION ANALYSIS")
    print("=" * 80)

    print(f"\nRegime changes in sequence: {regime_changes}")
    print(f"Section block sequence: {' -> '.join(section_blocks[:20])}...")

    # Regime progression summary
    print("\n" + "-" * 40)
    print("REGIME PROGRESSION")
    print("-" * 40)

    regime_first = {}
    regime_last = {}
    for i, folio in enumerate(proposed_order):
        regime = features[folio]['regime']
        if regime not in regime_first:
            regime_first[regime] = i
        regime_last[regime] = i

    for regime in sorted(regime_first.keys()):
        print(f"{regime}: positions {regime_first[regime]+1} - {regime_last[regime]+1}")

    # Identify contiguous blocks
    print("\n" + "-" * 40)
    print("CONTIGUOUS REGIME BLOCKS (3+ folios)")
    print("-" * 40)

    current_regime = None
    block_start = 0
    blocks = []

    for i, folio in enumerate(proposed_order):
        regime = features[folio]['regime']
        if regime != current_regime:
            if current_regime and i - block_start >= 3:
                blocks.append((current_regime, block_start, i-1))
            current_regime = regime
            block_start = i

    # Don't forget last block
    if current_regime and len(proposed_order) - block_start >= 3:
        blocks.append((current_regime, block_start, len(proposed_order)-1))

    for regime, start, end in blocks:
        folios_in_block = proposed_order[start:end+1]
        print(f"\n{regime}: positions {start+1}-{end+1} ({end-start+1} folios)")
        print(f"  Folios: {', '.join(folios_in_block)}")

    # Section mixing analysis
    print("\n" + "-" * 40)
    print("SECTION DISTRIBUTION IN PROPOSED ORDER")
    print("-" * 40)

    section_positions = {}
    for i, folio in enumerate(proposed_order):
        section = get_section(folio)
        if section not in section_positions:
            section_positions[section] = []
        section_positions[section].append(i+1)

    for section in ['HERBAL', 'BALNEO', 'ROSETTE', 'PHARMA', 'STARRED']:
        if section in section_positions:
            positions = section_positions[section]
            print(f"\n{section}:")
            print(f"  Count: {len(positions)}")
            print(f"  Range: {min(positions)} - {max(positions)}")
            print(f"  Mean position: {sum(positions)/len(positions):.1f}")

    # Create curriculum interpretation
    print("\n" + "=" * 80)
    print("CURRICULUM INTERPRETATION")
    print("=" * 80)

    # Divide into thirds
    n = len(proposed_order)
    early = proposed_order[:n//3]
    middle = proposed_order[n//3:2*n//3]
    late = proposed_order[2*n//3:]

    print("\nEARLY PHASE (positions 1-27):")
    early_regimes = [features[f]['regime'] for f in early]
    early_sections = [get_section(f) for f in early]
    print(f"  Dominant regime: {max(set(early_regimes), key=early_regimes.count)}")
    print(f"  Sections: {set(early_sections)}")
    print(f"  Avg hazard: {sum(features[f]['hazard_density'] for f in early)/len(early):.3f}")

    print("\nMIDDLE PHASE (positions 28-55):")
    middle_regimes = [features[f]['regime'] for f in middle]
    middle_sections = [get_section(f) for f in middle]
    print(f"  Dominant regime: {max(set(middle_regimes), key=middle_regimes.count)}")
    print(f"  Sections: {set(middle_sections)}")
    print(f"  Avg hazard: {sum(features[f]['hazard_density'] for f in middle)/len(middle):.3f}")

    print("\nLATE PHASE (positions 56-83):")
    late_regimes = [features[f]['regime'] for f in late]
    late_sections = [get_section(f) for f in late]
    print(f"  Dominant regime: {max(set(late_regimes), key=late_regimes.count)}")
    print(f"  Sections: {set(late_sections)}")
    print(f"  Avg hazard: {sum(features[f]['hazard_density'] for f in late)/len(late):.3f}")

    # Output the full proposed order to a text file
    output_path = Path(__file__).parent.parent.parent / "results" / "proposed_folio_order.txt"
    with open(output_path, 'w') as f:
        f.write("PROPOSED ORIGINAL FOLIO ORDER\n")
        f.write("Based on structural gradient optimization\n")
        f.write("=" * 60 + "\n\n")
        f.write("Optimized for:\n")
        f.write(f"  - Risk gradient (hazard_density): rho = {reorder_data['optimal_order']['risk_rho']}\n")
        f.write(f"  - Tension gradient: rho = {reorder_data['optimal_order']['tension_rho']}\n")
        f.write(f"  - CEI gradient: rho = {reorder_data['optimal_order']['cei_rho']}\n")
        f.write(f"  - Combined improvement: {reorder_data['improvement']}\n\n")
        f.write("=" * 60 + "\n")
        f.write(f"{'Pos':>3} | {'Folio':<8} | {'Regime':<9} | {'Section':<8} | {'Hazard':>7} | {'CEI':>6}\n")
        f.write("-" * 60 + "\n")

        for i, folio in enumerate(proposed_order):
            data = features[folio]
            section = get_section(folio)
            f.write(f"{i+1:>3} | {folio:<8} | {data['regime']:<9} | {section:<8} | "
                    f"{data['hazard_density']:>7.3f} | {data['cei_total']:>6.3f}\n")

    print(f"\n\nFull proposed order saved to: {output_path}")


if __name__ == "__main__":
    main()
