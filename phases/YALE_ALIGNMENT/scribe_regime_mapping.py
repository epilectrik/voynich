"""
Scribe-Regime Mapping Test
Phase: YALE_ALIGNMENT

Tests whether Lisa Fagin Davis's 5 paleographic scribes correlate with our 4 operational regimes.

Scribe assignments extracted from Yale transcript (approximate based on section descriptions):
- Scribe 1: Herbal A (botanical), Language A
- Scribe 2: Balneological, collaborates throughout, Language B
- Scribe 3: Starred paragraphs (final section)
- Scribe 4: Astronomical/astrological diagrams
- Scribe 5: Outer bifolia only (limited corpus)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_regime_assignments():
    """Load folio-to-regime assignments from our results."""
    results_dir = Path(__file__).parent.parent.parent / "results"

    # Load from b_design_space_cartography.json - has all 83 B folios
    cart_path = results_dir / "b_design_space_cartography.json"
    folio_regime = {}

    if cart_path.exists():
        with open(cart_path) as f:
            cart_data = json.load(f)

        # Extract from folio_positions
        for folio, data in cart_data.get("folio_positions", {}).items():
            if "regime" in data:
                folio_regime[folio] = data["regime"]

    # Count distribution
    voynich_raw = Counter(folio_regime.values())

    return folio_regime, dict(voynich_raw)

def assign_scribes_by_section(available_folios):
    """
    Assign scribes to folios based on Yale transcript section descriptions.

    This is an APPROXIMATION based on:
    - Davis's description of which scribes write which sections
    - The known section boundaries in the manuscript

    Scribe assignments from Yale lecture:
    - Scribe 1: Herbal A (botanical), Language A, Quires 1-8 dominant
    - Scribe 2: Balneological (entire), collaborates elsewhere, Language B
    - Scribe 3: Starred paragraphs (final section, f103-f116)
    - Scribe 4: Astronomical/astrological diagrams (Quire 9)
    - Scribe 5: Outer bifolia only (limited, skipping for this analysis)
    """
    scribe_assignments = {}

    for folio in available_folios:
        # Extract folio number
        # Format: f103r, f103v, f86v3, f86v4, etc.
        folio_clean = folio.lower()

        # Parse folio number
        import re
        match = re.match(r'f(\d+)', folio_clean)
        if not match:
            continue
        num = int(match.group(1))

        # Assign based on section
        # Botanical/Herbal A (f1-f66) - Scribe 1/2 mixed, assign Scribe 1 as dominant
        if num <= 66:
            scribe_assignments[folio] = 1

        # Astronomical (f67-f73) - Scribe 4
        elif 67 <= num <= 73:
            scribe_assignments[folio] = 4

        # Balneological (f75-f84) - Scribe 2
        elif 75 <= num <= 84:
            scribe_assignments[folio] = 2

        # Rosettes/Foldouts (f85-f86) - Scribe 2 dominant
        elif 85 <= num <= 86:
            scribe_assignments[folio] = 2

        # Pharmaceutical (f87-f102) - Scribe 1
        elif 87 <= num <= 102:
            scribe_assignments[folio] = 1

        # Starred paragraphs (f103-f116) - Scribe 3
        elif 103 <= num <= 116:
            scribe_assignments[folio] = 3

    return scribe_assignments

def test_scribe_regime_correlation():
    """Test correlation between scribes and regimes."""
    folio_regime, raw_counts = load_regime_assignments()
    scribe_assignments = assign_scribes_by_section(folio_regime.keys())

    # Find overlapping folios
    overlap = set(folio_regime.keys()) & set(scribe_assignments.keys())

    # Build contingency table
    scribe_regime_matrix = defaultdict(lambda: defaultdict(int))

    for folio in overlap:
        scribe = scribe_assignments[folio]
        regime = folio_regime[folio]
        scribe_regime_matrix[scribe][regime] += 1

    # Calculate statistics
    results = {
        "test": "SCRIBE_REGIME_MAPPING",
        "date": "2026-01-14",
        "source": "Yale Beinecke lecture (Lisa Fagin Davis)",
        "n_regime_folios": len(folio_regime),
        "n_scribe_assigned": len(scribe_assignments),
        "n_overlap": len(overlap),
        "contingency_table": {},
        "scribe_dominant_regime": {},
        "regime_dominant_scribe": {},
        "interpretation": ""
    }

    # Convert contingency table
    for scribe, regimes in sorted(scribe_regime_matrix.items()):
        results["contingency_table"][f"Scribe_{scribe}"] = dict(regimes)

        # Find dominant regime for each scribe
        if regimes:
            dominant_regime = max(regimes.items(), key=lambda x: x[1])
            total = sum(regimes.values())
            results["scribe_dominant_regime"][f"Scribe_{scribe}"] = {
                "regime": dominant_regime[0],
                "count": dominant_regime[1],
                "total": total,
                "percentage": round(100 * dominant_regime[1] / total, 1)
            }

    # Find dominant scribe for each regime
    regime_scribe = defaultdict(lambda: defaultdict(int))
    for folio in overlap:
        scribe = scribe_assignments[folio]
        regime = folio_regime[folio]
        regime_scribe[regime][scribe] += 1

    for regime, scribes in sorted(regime_scribe.items()):
        if scribes:
            dominant_scribe = max(scribes.items(), key=lambda x: x[1])
            total = sum(scribes.values())
            results["regime_dominant_scribe"][regime] = {
                "scribe": dominant_scribe[0],
                "count": dominant_scribe[1],
                "total": total,
                "percentage": round(100 * dominant_scribe[1] / total, 1)
            }

    # Interpretation
    mappings = []
    for scribe, data in results["scribe_dominant_regime"].items():
        mappings.append(f"{scribe} -> {data['regime']} ({data['percentage']}%)")

    results["interpretation"] = "; ".join(mappings)

    return results

def main():
    print("=" * 60)
    print("SCRIBE-REGIME MAPPING TEST")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    results = test_scribe_regime_correlation()

    print(f"\nOverlap: {results['n_overlap']} folios")
    print("\nContingency Table:")
    print("-" * 40)

    for scribe, regimes in sorted(results["contingency_table"].items()):
        print(f"  {scribe}:")
        for regime, count in sorted(regimes.items()):
            print(f"    {regime}: {count}")

    print("\nDominant Regime per Scribe:")
    print("-" * 40)
    for scribe, data in sorted(results["scribe_dominant_regime"].items()):
        print(f"  {scribe}: {data['regime']} ({data['count']}/{data['total']} = {data['percentage']}%)")

    print("\nDominant Scribe per Regime:")
    print("-" * 40)
    for regime, data in sorted(results["regime_dominant_scribe"].items()):
        print(f"  {regime}: Scribe {data['scribe']} ({data['count']}/{data['total']} = {data['percentage']}%)")

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "scribe_regime_mapping.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == "__main__":
    main()
