"""
05_section_synthesis.py - Synthesize section architecture findings

What we've learned:
1. HT-EN inverse correlation (rho=-0.506)
2. PHARMA has 40% HT vs BIO 22% (1.8x)
3. f66r is anomalous (28 single-char labels)
4. When normalized, section differences persist
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def get_section(folio):
    num = int(''.join(c for c in folio if c.isdigit()))
    if 74 <= num <= 84:
        return 'BIO'
    elif 26 <= num <= 56:
        return 'HERBAL_B'
    elif 57 <= num <= 67:
        return 'PHARMA'
    elif num >= 103:
        return 'RECIPE_B'
    else:
        return 'OTHER'

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load previous results
    with open(results_dir / 'section_census.json') as f:
        census = json.load(f)

    with open(results_dir / 'ht_en_inverse.json') as f:
        inverse = json.load(f)

    with open(results_dir / 'pharma_deep_dive.json') as f:
        pharma = json.load(f)

    with open(results_dir / 'f66r_investigation.json') as f:
        f66r = json.load(f)

    print("=" * 60)
    print("SECTION ARCHITECTURE SYNTHESIS")
    print("=" * 60)

    # === 1. SECTION PROFILES ===
    print("\n--- 1. SECTION PROFILES ---\n")

    print(f"{'Section':<12} {'Folios':>8} {'HT Rate':>10} {'EN Rate':>10} {'Structure':>15}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        s = census['sections'][section]
        ht_rate = s['ht_rate']
        en_rate = s['roles'].get('EN', 0) / s['tokens'] if s['tokens'] > 0 else 0
        tok_per_par = s['tokens'] / s['paragraphs'] if s['paragraphs'] > 0 else 0
        struct = f"{tok_per_par:.0f} tok/par"
        print(f"{section:<12} {len(s['folios']):>8} {ht_rate:>10.1%} {en_rate:>10.1%} {struct:>15}")

    # === 2. HT-EN INVERSE ===
    print("\n--- 2. HT-EN INVERSE RELATIONSHIP ---\n")

    print(f"Folio-level correlation: rho = {inverse['folio_correlation']:.3f}")
    if inverse.get('paragraph_correlation'):
        print(f"Paragraph-level correlation: rho = {inverse['paragraph_correlation']:.3f}")

    print("\nRole composition by HT level:")
    print(f"{'HT Level':<15} {'n':>8} {'HT':>10} {'EN':>10} {'CC':>10}")
    for level in ['low', 'med', 'high']:
        profile = inverse['role_by_ht_level'][level]
        n = inverse['n_paragraphs_by_level'][level]
        print(f"{level:<15} {n:>8} {profile.get('HT',0):>10.1%} {profile.get('EN',0):>10.1%} {profile.get('CC',0):>10.1%}")

    # === 3. PHARMA ANOMALY ===
    print("\n--- 3. PHARMA STRUCTURAL ANOMALY ---\n")

    print(f"PHARMA mean paragraph size: {pharma['pharma_mean_size']:.1f} tokens")
    print(f"BIO mean paragraph size: {pharma['bio_mean_size']:.1f} tokens")
    print(f"PHARMA single-line rate: {pharma['pharma_single_line_rate']:.1%}")
    print(f"BIO single-line rate: {pharma['bio_single_line_rate']:.1%}")

    print(f"\nf66r structure:")
    print(f"  - {f66r['label_paragraphs']} label paragraphs")
    print(f"  - {f66r['normal_paragraphs']} normal paragraphs")
    print(f"  - {f66r['primitive_rate']:.1%} of single-chars are primitives")

    # === 4. INTERPRETATION ===
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    print("""
FINDING 1: SECTIONS ARE STRUCTURALLY DISTINCT
---------------------------------------------
- BIO: Low HT (22%), High EN (40%), Large paragraphs (46 tok)
- PHARMA: High HT (40%), Low EN (27%), Small paragraphs (13 tok)
- Sections are NOT just content variations - they have different PROGRAM STRUCTURES

FINDING 2: HT AND EN ARE STRUCTURAL SUBSTITUTES
-----------------------------------------------
- Folio-level correlation: rho = -0.506 (strong inverse)
- High-HT paragraphs have 22.5% EN vs 39.8% in low-HT
- HT fills the role that EN would occupy
- This is COMPENSATORY, not random

FINDING 3: PHARMA IS A SPECIAL DOCUMENT TYPE
--------------------------------------------
- Only 3 folios, highly unusual structure
- f66r has 28 single-character labels (likely diagram/index)
- When excluding labels, PHARMA still has elevated HT (38-42%)
- PHARMA may be a REFERENCE SECTION, not operational procedures

FINDING 4: SECTIONS REFLECT PROGRAM COMPLEXITY
----------------------------------------------
- BIO: Dense EN execution = complex energy modulation programs
- HERBAL_B: Moderate structure = standard procedures
- PHARMA: Sparse EN, high HT = identification-heavy, execution-light
- RECIPE_B: Moderate HT/EN = balanced programs

MODEL: SECTION = PROGRAM TYPE
=============================

| Section | Program Type | HT Role | EN Role |
|---------|--------------|---------|---------|
| BIO | Execution-heavy | Minimal ID | Complex modulation |
| HERBAL_B | Balanced | Moderate ID | Moderate modulation |
| PHARMA | Index/Reference | Heavy ID | Sparse execution |
| RECIPE_B | Balanced | Moderate ID | Standard modulation |

HT = Identification vocabulary (material/context markers)
EN = Energy modulation vocabulary (execution instructions)

The HT-EN tradeoff reflects a fundamental architectural choice:
- More identification needed = more HT, less EN
- More execution needed = more EN, less HT
""")

    # === 5. CONSTRAINTS TO LOG ===
    print("\n--- PROPOSED CONSTRAINTS ---\n")

    print("C873: Section Structural Profiles (Tier 2)")
    print("  - Sections have distinct HT/EN profiles (not just content variation)")
    print()
    print("C874: HT-EN Structural Inverse (Tier 2)")
    print("  - rho=-0.506 at folio level, compensatory relationship")
    print()
    print("C875: PHARMA Structural Anomaly (Tier 2)")
    print("  - f66r is index/label structure, not operational text")
    print()
    print("C876: Section Program Type Interpretation (Tier 3)")
    print("  - Sections reflect program complexity/type, not just content")

    # Save
    synthesis = {
        'ht_en_correlation': inverse['folio_correlation'],
        'section_profiles': {
            section: {
                'ht_rate': census['sections'][section]['ht_rate'],
                'en_rate': census['sections'][section]['roles'].get('EN', 0) / census['sections'][section]['tokens'],
                'folios': len(census['sections'][section]['folios']),
                'tokens': census['sections'][section]['tokens']
            }
            for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']
        },
        'pharma_anomaly': {
            'f66r_labels': f66r['label_paragraphs'],
            'f66r_normal': f66r['normal_paragraphs'],
            'mean_par_size': pharma['pharma_mean_size']
        },
        'interpretation': 'SECTION_PROGRAM_TYPE'
    }

    with open(results_dir / 'section_synthesis.json', 'w') as f:
        json.dump(synthesis, f, indent=2)

    print(f"\nSaved to section_synthesis.json")

if __name__ == '__main__':
    main()
