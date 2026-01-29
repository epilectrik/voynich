"""
04_ht_synthesis.py - Synthesize HT token findings

What we've learned:
1. HT = 30.5% of B tokens (7042 tokens, 2660 unique)
2. Line 1 has 47% HT vs 27% later (1.74x enrichment)
3. f-initial paragraphs have 38.6% HT (vs 30% for p)
4. 86% of Line-1 HT tokens are folio-singletons
5. 1229 tokens are BOTH folio-unique AND Line-1 exclusive
6. HT cooccurs with FL (flow), avoids CC and FQ
7. Line-1 HT uses AX_INIT scaffolding

SYNTHESIS: What is HT?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def line_to_num(l):
    """Convert line like '4a' to numeric 4."""
    nums = ''.join(c for c in str(l) if c.isdigit())
    return int(nums) if nums else 1

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load previous results
    with open(results_dir / 'ht_census.json') as f:
        census = json.load(f)

    with open(results_dir / 'ht_gallows_connection.json') as f:
        gallows = json.load(f)

    with open(results_dir / 'line1_ht_identity.json') as f:
        identity = json.load(f)

    with open(results_dir / 'ht_c475_compliance.json') as f:
        compliance = json.load(f)

    print("=" * 60)
    print("HT TOKEN SYNTHESIS")
    print("=" * 60)

    print("\n--- POPULATION STATISTICS ---\n")
    print(f"Total HT tokens: {census['ht_count']}")
    print(f"HT rate in B: {census['ht_rate']:.1%}")
    print(f"Unique HT vocabulary: {census['unique_ht']}")

    print("\n--- POSITIONAL DISTRIBUTION ---\n")
    print("Line 1 vs later:")
    print(f"  Line-1 HT rate: ~47% (from script 01)")
    print(f"  Later-line HT rate: ~27%")
    print(f"  Ratio: 1.74x enrichment in Line 1")

    print("\nGallows-initial paragraph HT rates:")
    for g in ['f', 't', 'p', 'k']:
        if g in gallows['gallows_ht_rates']:
            print(f"  {g}-initial: {gallows['gallows_ht_rates'][g]:.1%}")

    print("\n--- VOCABULARY CHARACTER ---\n")
    print(f"Line-1 HT vocabulary: {identity['total_line1_ht_vocab']} unique tokens")
    print(f"Folio-singleton rate: {identity['folio_singleton_rate']:.1%}")
    print(f"Folio-unique AND Line-1 only: {identity['folio_unique_line1_only']}")
    print(f"Gallows-initial rate: {identity['gallows_initial_rate']:.1%}")
    print(f"IS-opener rate: {identity['is_opener_rate']:.1%}")

    print("\n--- COOCCURRENCE PATTERN ---\n")
    total_lines = compliance['ht_only_lines'] + compliance['mixed_lines'] + compliance['no_ht_lines']
    print(f"HT-only lines: {compliance['ht_only_lines']} ({compliance['ht_only_lines']/total_lines:.1%})")
    print(f"Mixed lines: {compliance['mixed_lines']} ({compliance['mixed_lines']/total_lines:.1%})")
    print(f"No-HT lines: {compliance['no_ht_lines']} ({compliance['no_ht_lines']/total_lines:.1%})")

    print("\n--- SECTION VARIATION ---\n")
    print("HT rate by section:")
    for section, rate in census['section_rates'].items():
        print(f"  {section}: {rate:.1%}")

    print("\n" + "=" * 60)
    print("SYNTHESIS: WHAT IS HT?")
    print("=" * 60)

    print("""
FINDING 1: HT is LINE-POSITIONAL
--------------------------------
- Line 1 has 47% HT vs 27% elsewhere (1.74x enrichment)
- This is PARAGRAPH Line 1, not folio Line 1
- Effect is universal across gallows types (all show ~2x ratio)

FINDING 2: HT is FOLIO-SPECIFIC
-------------------------------
- 86% of Line-1 HT tokens appear in only ONE folio
- 1229 tokens are BOTH folio-unique AND Line-1 exclusive
- This is IDENTIFICATION vocabulary unique to each folio/material

FINDING 3: HT COOCCURS with GRAMMAR
-----------------------------------
- 89% of lines mix HT with classified tokens
- Only 2.6% of lines are HT-only
- HT tokens follow positional patterns (not isolated)

FINDING 4: HT AVOIDS CORE CONTROL
---------------------------------
- HT enriched on lines with FL (flow control)
- HT depleted on lines with CC (core control) and FQ
- Suggests: HT in "setup/identification" zones, not "execution" zones

FINDING 5: LINE-1 HT IS NOT THE GALLOWS
---------------------------------------
- Only 19.5% of Line-1 HT IS the paragraph opener
- Only 25.5% of Line-1 HT is gallows-initial
- The HT enrichment is the SECOND and THIRD tokens, not just first

FINDING 6: F-INITIAL PARAGRAPHS ARE HT-RICH
-------------------------------------------
- f-initial: 38.6% HT (vs 30% for p)
- f = folio opener, front-biased (position 0.30)
- f paragraphs mark folio identification/setup phase

INTERPRETATION
==============
HT tokens are MATERIAL IDENTIFICATION vocabulary:

1. They concentrate in Line 1 (header) of each paragraph
2. They are highly folio-specific (unique to each material/procedure)
3. They cooccur with initialization scaffolding (AX_INIT)
4. They avoid dense instruction zones (CC, FQ)

HT IS the "human" part of the text - the names, identifiers, and
material-specific markers that vary between folios/procedures,
while the instruction grammar (PP classes) is shared.

Line 1 = HEADER: "What material? What variant? What state?"
Later = BODY: "How to process? What controls? What checks?"

This explains:
- Why HT is folio-specific (different materials)
- Why HT concentrates in Line 1 (identification header)
- Why HT mixes with grammar (integrated, not separate)
- Why f-initial paragraphs are HT-rich (folio-level identification)
""")

    # Save synthesis
    synthesis = {
        'ht_rate': census['ht_rate'],
        'line1_ht_rate': 0.47,  # Approximate from script 01
        'later_ht_rate': 0.27,
        'line1_enrichment': 1.74,
        'folio_singleton_rate': identity['folio_singleton_rate'],
        'folio_unique_line1_only': identity['folio_unique_line1_only'],
        'mixed_line_rate': compliance['mixed_lines'] / total_lines,
        'interpretation': 'MATERIAL_IDENTIFICATION_VOCABULARY',
        'key_claims': [
            'HT is line-positional (concentrates in Line 1)',
            'HT is folio-specific (86% singletons)',
            'HT cooccurs with classified tokens (89% mixed lines)',
            'HT avoids core control zones',
            'Line-1 HT is identification/header vocabulary',
            'HT = the material-specific part of each procedure'
        ]
    }

    with open(results_dir / 'ht_synthesis.json', 'w') as f:
        json.dump(synthesis, f, indent=2)

    print(f"\nSaved to ht_synthesis.json")

if __name__ == '__main__':
    main()
