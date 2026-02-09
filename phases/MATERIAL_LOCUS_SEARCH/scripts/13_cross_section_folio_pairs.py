#!/usr/bin/env python3
"""
MATERIAL_LOCUS_SEARCH Phase - Test 13: Cross-Section Folio Pair Comparison

Question: When two folios from DIFFERENT sections share unusually high vocabulary
overlap, what distinguishes them? Is the overlap operational or material?

Method:
1. Load Currier B tokens, extract MIDDLEs per folio.
2. Compute all cross-section folio-pair MIDDLE Jaccard similarities.
3. Identify top 10 highest-overlap cross-section pairs.
4. For each pair, decode both folios (structural + interpretive).
5. Analyze shared vs unique MIDDLEs, folio frequency of shared MIDDLEs.
6. Classify overlap as OPERATIONAL, MATERIAL_SIGNAL, or AMBIGUOUS.

Pass: 3+ pairs have material signals.
Fail: Otherwise.
"""

import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology, BFolioDecoder

# ============================================================
# 1. LOAD DATA
# ============================================================
print("Loading transcript and extracting MIDDLEs for Currier B...")
tx = Transcript()
morph = Morphology()

# Collect per-folio data
folio_middles = defaultdict(set)        # folio -> set of MIDDLEs
folio_middle_counts = defaultdict(Counter)  # folio -> Counter of MIDDLEs
folio_sections = {}                     # folio -> section
folio_token_counts = Counter()          # folio -> total token count
middle_folio_presence = defaultdict(set)  # middle -> set of folios it appears in

# Also collect per-folio, per-line, per-paragraph-position data for later analysis
folio_line_middles = defaultdict(lambda: defaultdict(list))  # folio -> line -> [middles]
folio_par_initial_middles = defaultdict(list)   # folio -> [middles at par-initial]
folio_par_final_middles = defaultdict(list)     # folio -> [middles at par-final]
folio_line_initial_middles = defaultdict(list)  # folio -> [middles at line-initial]

for token in tx.currier_b():
    folio = token.folio
    section = token.section
    m = morph.extract(token.word)
    middle = m.middle

    if middle and middle != '_EMPTY_':
        folio_middles[folio].add(middle)
        folio_middle_counts[folio][middle] += 1
        folio_token_counts[folio] += 1
        middle_folio_presence[middle].add(folio)

        if folio not in folio_sections:
            folio_sections[folio] = section

        # Positional data
        folio_line_middles[folio][token.line].append(middle)
        if token.par_initial:
            folio_par_initial_middles[folio].append(middle)
        if token.par_final:
            folio_par_final_middles[folio].append(middle)
        if token.line_initial:
            folio_line_initial_middles[folio].append(middle)

folios = sorted(folio_middles.keys())
n_folios = len(folios)
total_b_folios = n_folios  # Used for frequency classification

# Build folio-count for each MIDDLE
middle_folio_count = {mid: len(fset) for mid, fset in middle_folio_presence.items()}

print(f"  Found {n_folios} Currier B folios")
print(f"  Sections: {dict(Counter(folio_sections[f] for f in folios))}")

# ============================================================
# 2. COMPUTE ALL CROSS-SECTION FOLIO-PAIR JACCARD SIMILARITIES
# ============================================================
print("\nComputing cross-section Jaccard similarities...")

pairs = []
for i in range(len(folios)):
    for j in range(i + 1, len(folios)):
        f1, f2 = folios[i], folios[j]
        s1, s2 = folio_sections.get(f1, '?'), folio_sections.get(f2, '?')

        # Only cross-section pairs
        if s1 == s2:
            continue

        set1 = folio_middles[f1]
        set2 = folio_middles[f2]
        intersection = set1 & set2
        union = set1 | set2

        if len(union) == 0:
            continue

        jaccard = len(intersection) / len(union)
        pairs.append({
            'folio1': f1,
            'folio2': f2,
            'section1': s1,
            'section2': s2,
            'jaccard': jaccard,
            'n_shared': len(intersection),
            'n_union': len(union),
            'n_f1_only': len(set1 - set2),
            'n_f2_only': len(set2 - set1),
        })

# Sort by Jaccard descending
pairs.sort(key=lambda x: x['jaccard'], reverse=True)
print(f"  Total cross-section pairs: {len(pairs)}")
print(f"  Top 10 Jaccard scores: {[round(p['jaccard'], 4) for p in pairs[:10]]}")

# ============================================================
# 3. ANALYZE TOP 10 PAIRS IN DETAIL
# ============================================================
print("\n" + "=" * 80)
print("TOP 10 CROSS-SECTION FOLIO PAIRS (by MIDDLE Jaccard similarity)")
print("=" * 80)

# Initialize decoder (expensive - do once)
print("\nInitializing BFolioDecoder...")
decoder = BFolioDecoder()
print("  Decoder ready.\n")

top_10_analyses = []

for rank, pair in enumerate(pairs[:10], 1):
    f1, f2 = pair['folio1'], pair['folio2']
    s1, s2 = pair['section1'], pair['section2']
    jaccard = pair['jaccard']

    print(f"\n{'#' * 80}")
    print(f"# PAIR {rank}: {f1} (section {s1}) vs {f2} (section {s2})")
    print(f"# Jaccard = {jaccard:.4f} | Shared = {pair['n_shared']} | Union = {pair['n_union']}")
    print(f"{'#' * 80}")

    # Shared MIDDLEs
    shared = folio_middles[f1] & folio_middles[f2]
    f1_only = folio_middles[f1] - folio_middles[f2]
    f2_only = folio_middles[f2] - folio_middles[f1]

    # Classify shared MIDDLEs by frequency
    shared_common = []   # In 40+ folios
    shared_moderate = []  # In 15-39 folios
    shared_rare = []     # In <15 folios

    for mid in sorted(shared, key=lambda m: middle_folio_count.get(m, 0)):
        fc = middle_folio_count.get(mid, 0)
        entry = {
            'middle': mid,
            'folio_count': fc,
            'count_in_f1': folio_middle_counts[f1].get(mid, 0),
            'count_in_f2': folio_middle_counts[f2].get(mid, 0),
        }
        if fc >= 40:
            shared_common.append(entry)
        elif fc >= 15:
            shared_moderate.append(entry)
        else:
            shared_rare.append(entry)

    # Print shared MIDDLE analysis
    print(f"\n  SHARED MIDDLEs ({len(shared)} total):")
    print(f"    Common (40+ folios): {len(shared_common)} - {[e['middle'] for e in shared_common]}")
    print(f"    Moderate (15-39 folios): {len(shared_moderate)} - {[e['middle'] for e in shared_moderate]}")
    print(f"    RARE (<15 folios): {len(shared_rare)} - {[e['middle'] for e in shared_rare]}")

    for e in shared_rare:
        print(f"      '{e['middle']}': in {e['folio_count']} folios, "
              f"{e['count_in_f1']}x in {f1}, {e['count_in_f2']}x in {f2}")

    # Print unique MIDDLEs (abbreviated)
    f1_rare_unique = [m for m in f1_only if middle_folio_count.get(m, 0) < 15]
    f2_rare_unique = [m for m in f2_only if middle_folio_count.get(m, 0) < 15]
    print(f"\n  UNIQUE to {f1}: {len(f1_only)} total, {len(f1_rare_unique)} rare")
    if f1_rare_unique:
        print(f"    Rare unique: {f1_rare_unique[:10]}")
    print(f"  UNIQUE to {f2}: {len(f2_only)} total, {len(f2_rare_unique)} rare")
    if f2_rare_unique:
        print(f"    Rare unique: {f2_rare_unique[:10]}")

    # Check positional similarity of shared MIDDLEs
    # Do they appear in similar line positions?
    f1_line_init_set = set(folio_line_initial_middles.get(f1, []))
    f2_line_init_set = set(folio_line_initial_middles.get(f2, []))
    shared_at_line_init = shared & f1_line_init_set & f2_line_init_set

    f1_par_init_set = set(folio_par_initial_middles.get(f1, []))
    f2_par_init_set = set(folio_par_initial_middles.get(f2, []))
    shared_at_par_init = shared & f1_par_init_set & f2_par_init_set

    print(f"\n  POSITIONAL OVERLAP:")
    print(f"    Shared at line-initial in both: {len(shared_at_line_init)} - {sorted(shared_at_line_init)[:8]}")
    print(f"    Shared at par-initial in both:  {len(shared_at_par_init)} - {sorted(shared_at_par_init)[:8]}")

    # Decode both folios
    print(f"\n  --- DECODED: {f1} (section {s1}) STRUCTURAL ---")
    struct1 = decoder.decode_folio_lines(f1, mode='structural')
    print(struct1)

    print(f"\n  --- DECODED: {f1} (section {s1}) INTERPRETIVE ---")
    interp1 = decoder.decode_folio_lines(f1, mode='interpretive')
    print(interp1)

    print(f"\n  --- DECODED: {f2} (section {s2}) STRUCTURAL ---")
    struct2 = decoder.decode_folio_lines(f2, mode='structural')
    print(struct2)

    print(f"\n  --- DECODED: {f2} (section {s2}) INTERPRETIVE ---")
    interp2 = decoder.decode_folio_lines(f2, mode='interpretive')
    print(interp2)

    # Store analysis for JSON output
    top_10_analyses.append({
        'rank': rank,
        'folio1': f1,
        'folio2': f2,
        'section1': s1,
        'section2': s2,
        'jaccard': round(jaccard, 4),
        'n_shared': len(shared),
        'n_union': len(folio_middles[f1] | folio_middles[f2]),
        'n_f1_unique': len(f1_only),
        'n_f2_unique': len(f2_only),
        'shared_common': shared_common,
        'shared_moderate': shared_moderate,
        'shared_rare': shared_rare,
        'n_common': len(shared_common),
        'n_moderate': len(shared_moderate),
        'n_rare': len(shared_rare),
        'f1_rare_unique': f1_rare_unique[:15],
        'f2_rare_unique': f2_rare_unique[:15],
        'shared_at_line_initial_both': sorted(shared_at_line_init),
        'shared_at_par_initial_both': sorted(shared_at_par_init),
        'structural_decode_f1': struct1[:500],  # Truncate for JSON
        'structural_decode_f2': struct2[:500],
        'interpretive_decode_f1': interp1[:500],
        'interpretive_decode_f2': interp2[:500],
        # Placeholders - will be filled after reading output
        'narrative': '',
        'verdict': '',
    })

# ============================================================
# 4. SUMMARY STATISTICS
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

# Distribution of Jaccard scores
all_jaccards = [p['jaccard'] for p in pairs]
print(f"\nAll cross-section pairs: {len(pairs)}")
print(f"  Mean Jaccard: {sum(all_jaccards) / len(all_jaccards):.4f}")
print(f"  Max Jaccard:  {max(all_jaccards):.4f}")
print(f"  Min Jaccard:  {min(all_jaccards):.4f}")

# Section pair distribution in top 10
section_pair_counts = Counter()
for a in top_10_analyses:
    sp = tuple(sorted([a['section1'], a['section2']]))
    section_pair_counts[sp] += 1
print(f"\nSection pair distribution in top 10: {dict(section_pair_counts)}")

# Rare MIDDLE prevalence
for a in top_10_analyses:
    pct_rare = a['n_rare'] / a['n_shared'] * 100 if a['n_shared'] > 0 else 0
    print(f"  Pair {a['rank']} ({a['folio1']}-{a['folio2']}): "
          f"{a['n_rare']}/{a['n_shared']} rare MIDDLEs ({pct_rare:.1f}%)")

# ============================================================
# 5. WRITE PRELIMINARY OUTPUT (narratives/verdicts to be filled externally)
# ============================================================
output_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/cross_section_folio_pairs.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

preliminary_output = {
    "test": "cross_section_folio_pairs",
    "phase": "MATERIAL_LOCUS_SEARCH",
    "question": "When two folios from DIFFERENT sections share unusually high vocabulary overlap, is the overlap operational or material?",
    "method": {
        "metric": "MIDDLE Jaccard similarity",
        "scope": "Currier B, H track, no labels, no uncertain",
        "n_folios": n_folios,
        "n_cross_section_pairs": len(pairs),
        "frequency_thresholds": {
            "common": "40+ folios",
            "moderate": "15-39 folios",
            "rare": "<15 folios (potential material markers)"
        }
    },
    "jaccard_distribution": {
        "mean": round(sum(all_jaccards) / len(all_jaccards), 4),
        "max": round(max(all_jaccards), 4),
        "min": round(min(all_jaccards), 4),
        "top10_scores": [round(p['jaccard'], 4) for p in pairs[:10]],
    },
    "top_10_pairs": top_10_analyses,
    "section_pair_distribution_top10": {f"{k[0]}-{k[1]}": v for k, v in section_pair_counts.items()},
    "verdict": "PENDING",
    "verdict_detail": "Narratives and per-pair verdicts to be filled after analysis",
}

with open(output_path, 'w') as f:
    json.dump(preliminary_output, f, indent=2, default=str)

print(f"\nPreliminary output written to {output_path}")
print("Done.")
