#!/usr/bin/env python3
"""
RECIPE -> A REGISTER BACK-PROPAGATION

Question: Can we trace a specific Brunschwig recipe to a specific Currier A register
          that would "configure" the system for that product?

Theory: A registers are configuration strings (input material -> output product)
        Each A folio should correspond to a specific material+product combination

Method:
1. Look at the MIDDLE content of each A folio classified as a product type
2. See if different A folios within the same type have distinguishable MIDDLE sets
3. Check if these could correspond to different Brunschwig recipes
"""

import csv
import json
from collections import defaultdict, Counter

# ============================================================
# LOAD DATA
# ============================================================

def load_a_folio_middles():
    """Get the MIDDLE tokens in each A folio."""
    folio_middles = defaultdict(Counter)

    # Decomposition helper
    KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

    def get_middle(token):
        for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
            if token.startswith(p):
                return token[len(p):]
        return token

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio][middle] += 1

    return folio_middles

def load_classifications():
    """Load product type classifications."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("RECIPE -> A REGISTER BACK-PROPAGATION")
    print("=" * 70)
    print()
    print("Testing if Brunschwig recipes can trace to specific A registers.")
    print()

    # Load data
    folio_middles = load_a_folio_middles()
    classifications = load_classifications()

    print(f"Loaded {len(folio_middles)} A folios with MIDDLE data")
    print(f"Loaded {len(classifications)} folio classifications")
    print()

    # Group folios by product type
    type_folios = defaultdict(list)
    for folio, ptype in classifications.items():
        if folio in folio_middles:
            type_folios[ptype].append(folio)

    # Focus on WATER_GENTLE (small, testable)
    print("=" * 70)
    print("WATER_GENTLE FOLIOS - Can we distinguish recipes?")
    print("=" * 70)
    print()

    gentle_folios = type_folios.get('WATER_GENTLE', [])
    print(f"WATER_GENTLE has {len(gentle_folios)} A folios: {gentle_folios}")
    print()

    # Brunschwig gentle flower waters
    gentle_recipes = {
        'Rose water': 'Most common, delicate petals',
        'Lavender water': 'Aromatic flowers',
        'Violet water': 'Very delicate, premium',
        'Orange flower': 'Neroli-adjacent',
        'Elder flower': 'Medicinal',
        'Chamomile water': 'Medicinal flowers',
    }

    print(f"Brunschwig has ~{len(gentle_recipes)} gentle flower waters:")
    for recipe, desc in gentle_recipes.items():
        print(f"  - {recipe}: {desc}")
    print()

    # Compare MIDDLE inventories of WATER_GENTLE folios
    print("-" * 70)
    print("MIDDLE INVENTORIES:")
    print("-" * 70)
    print()

    folio_middle_sets = {}
    all_middles = set()

    for folio in sorted(gentle_folios):
        middles = set(folio_middles[folio].keys())
        folio_middle_sets[folio] = middles
        all_middles.update(middles)

        top_middles = folio_middles[folio].most_common(10)
        print(f"{folio}: {len(middles)} unique MIDDLEs")
        print(f"  Top 10: {[m[0] for m in top_middles]}")
        print()

    # Find UNIQUE middles per folio
    print("-" * 70)
    print("UNIQUE MIDDLES (appear in only one WATER_GENTLE folio):")
    print("-" * 70)
    print()

    middle_folios = defaultdict(set)
    for folio, middles in folio_middle_sets.items():
        for m in middles:
            middle_folios[m].add(folio)

    unique_by_folio = defaultdict(list)
    for m, folios in middle_folios.items():
        if len(folios) == 1:
            folio = list(folios)[0]
            unique_by_folio[folio].append(m)

    for folio in sorted(gentle_folios):
        unique = unique_by_folio.get(folio, [])
        print(f"{folio}: {len(unique)} unique MIDDLEs")
        if unique:
            print(f"  Examples: {unique[:10]}")
        print()

    # Overlap analysis
    print("-" * 70)
    print("FOLIO OVERLAP (Jaccard similarity):")
    print("-" * 70)
    print()

    for i, f1 in enumerate(sorted(gentle_folios)):
        for f2 in sorted(gentle_folios)[i+1:]:
            s1 = folio_middle_sets[f1]
            s2 = folio_middle_sets[f2]
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            jaccard = intersection / union if union > 0 else 0
            print(f"  {f1} vs {f2}: {jaccard:.2f} ({intersection}/{union})")
    print()

    # Can we distinguish?
    print("=" * 70)
    print("ASSESSMENT: Can recipes map to specific registers?")
    print("=" * 70)
    print()

    # Count distinguishing features
    distinguishable = sum(1 for f in gentle_folios if len(unique_by_folio.get(f, [])) >= 5)

    if distinguishable >= len(gentle_folios) * 0.5:
        print("YES - Most WATER_GENTLE folios have unique MIDDLE signatures")
        print()
        print("Potential recipe -> register mapping:")
        for folio in sorted(gentle_folios):
            n_unique = len(unique_by_folio.get(folio, []))
            print(f"  {folio}: {n_unique} unique MIDDLEs -> could be a specific gentle water")
    else:
        print("PARTIAL - Some differentiation but high overlap")
        print()
        print("Folios share many MIDDLEs, suggesting:")
        print("  - Common procedural vocabulary for product TYPE")
        print("  - Individual recipes may differ in PREFIX, not MIDDLE")

    print()

    # OIL_RESIN analysis
    print("=" * 70)
    print("OIL_RESIN FOLIOS - More aggressive products")
    print("=" * 70)
    print()

    oil_folios = type_folios.get('OIL_RESIN', [])
    print(f"OIL_RESIN has {len(oil_folios)} A folios")
    print()

    oil_unique = {}
    for folio in oil_folios:
        if folio in folio_middles:
            middles = set(folio_middles[folio].keys())
            unique = [m for m in middles if len(middle_folios.get(m, set())) == 1]
            oil_unique[folio] = len(unique)

    print("Unique MIDDLE counts:")
    for folio, count in sorted(oil_unique.items(), key=lambda x: -x[1])[:10]:
        print(f"  {folio}: {count} unique MIDDLEs")

    print()

    # Final verdict
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    total_with_unique = sum(1 for f in gentle_folios if len(unique_by_folio.get(f, [])) > 0)

    print(f"WATER_GENTLE: {total_with_unique}/{len(gentle_folios)} folios have unique MIDDLEs")
    print()

    if total_with_unique == len(gentle_folios):
        print("FINDING: Each A register has a DISTINGUISHABLE signature")
        print()
        print("This supports the theory that A registers are CONFIGURATION STRINGS")
        print("for specific input->output products, not just product TYPES.")
        print()
        print("A Brunschwig recipe CAN back-propagate to a SPECIFIC A register.")
    else:
        print("FINDING: A registers share vocabulary within product type")
        print()
        print("The back-propagation reaches TYPE level, not individual recipe level.")

if __name__ == '__main__':
    main()
