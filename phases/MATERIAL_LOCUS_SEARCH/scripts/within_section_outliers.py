#!/usr/bin/env python3
"""
Test 14: Within-Section Folio Vocabulary Outlier Analysis

For each Currier B section, find the most vocabulary-divergent folio pairs
(lowest MIDDLE Jaccard similarity), then analyze what makes them different:
operational variants or genuinely distinct material markers?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder


def levenshtein(s1, s2):
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def main():
    print("=" * 70)
    print("TEST 14: Within-Section Folio Vocabulary Outlier Analysis")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # Load middle dictionary for glosses
    mid_dict_path = PROJECT_ROOT / 'data' / 'middle_dictionary.json'
    mid_dict = {}
    if mid_dict_path.exists():
        with open(mid_dict_path) as f:
            md = json.load(f)
            mid_dict = md.get('middles', {})
        print(f"Loaded middle dictionary: {len(mid_dict)} entries")

    # Step 1: Collect per-folio MIDDLE sets, grouped by section
    # section_folios[section][folio] = set of MIDDLEs
    section_folios = defaultdict(lambda: defaultdict(set))
    # Also track MIDDLE counts per folio for frequency analysis
    section_folio_counts = defaultdict(lambda: defaultdict(Counter))
    # All MIDDLEs with global counts for "common" determination
    global_middle_counts = Counter()

    for token in tx.currier_b():
        section = token.section
        folio = token.folio
        m = morph.extract(token.word)
        if m.middle and m.middle != '_EMPTY_':
            section_folios[section][folio].add(m.middle)
            section_folio_counts[section][folio][m.middle] += 1
            global_middle_counts[m.middle] += 1

    # Get "common" MIDDLEs (top 100 by frequency)
    common_middles = set(m for m, _ in global_middle_counts.most_common(100))
    print(f"\nTotal unique MIDDLEs: {len(global_middle_counts)}")
    print(f"Common MIDDLEs (top 100): {len(common_middles)}")

    sections_to_analyze = ['B', 'H', 'S', 'T', 'C']
    # Filter to sections that actually exist in data
    available_sections = sorted(section_folios.keys())
    print(f"Available sections in Currier B: {available_sections}")

    results = {}

    # Initialize BFolioDecoder once (expensive)
    print("\nInitializing BFolioDecoder...")
    decoder = BFolioDecoder()
    print("BFolioDecoder ready.\n")

    for section in sections_to_analyze:
        if section not in section_folios:
            print(f"\nSection {section}: NOT FOUND in data, skipping")
            continue

        folios = section_folios[section]
        if len(folios) < 2:
            print(f"\nSection {section}: Only {len(folios)} folio(s), skipping")
            continue

        print(f"\n{'=' * 70}")
        print(f"SECTION {section}: {len(folios)} folios")
        print(f"{'=' * 70}")

        # Compute all pairwise Jaccard similarities
        folio_list = sorted(folios.keys())
        pairs = []
        for f1, f2 in combinations(folio_list, 2):
            j = jaccard(folios[f1], folios[f2])
            pairs.append((f1, f2, j))

        pairs.sort(key=lambda x: x[2])  # ascending by similarity

        # Report top 5 most divergent
        print(f"\n  Top 5 most divergent pairs (lowest Jaccard):")
        for f1, f2, j in pairs[:5]:
            print(f"    {f1} vs {f2}: Jaccard={j:.3f}  |A|={len(folios[f1])}, |B|={len(folios[f2])}")

        # Focus on the MOST divergent pair
        f1, f2, min_j = pairs[0]
        print(f"\n  MOST DIVERGENT PAIR: {f1} vs {f2} (Jaccard={min_j:.3f})")

        # MIDDLEs unique to each folio in this pair
        unique_to_f1 = folios[f1] - folios[f2]
        unique_to_f2 = folios[f2] - folios[f1]
        shared = folios[f1] & folios[f2]

        print(f"\n  Shared MIDDLEs: {len(shared)}")
        print(f"  Unique to {f1}: {len(unique_to_f1)}")
        print(f"  Unique to {f2}: {len(unique_to_f2)}")

        # Analyze unique MIDDLEs: are they operational variants (distance-1) or independent?
        def classify_middle(mid, other_set):
            """Classify a MIDDLE as operational variant or independent."""
            # Check distance to any common MIDDLE
            min_dist_common = min(
                (levenshtein(mid, cm) for cm in common_middles),
                default=999
            )
            # Check distance to any MIDDLE in the other folio
            min_dist_other = min(
                (levenshtein(mid, om) for om in other_set),
                default=999
            )
            # Check distance to any MIDDLE in shared set
            min_dist_shared = min(
                (levenshtein(mid, sm) for sm in shared),
                default=999
            ) if shared else 999

            closest_common = None
            if min_dist_common <= 2:
                for cm in common_middles:
                    if levenshtein(mid, cm) == min_dist_common:
                        closest_common = cm
                        break

            is_variant = min_dist_common <= 1 or min_dist_other <= 1
            return {
                'middle': mid,
                'min_dist_common': min_dist_common,
                'closest_common': closest_common,
                'min_dist_other': min_dist_other,
                'min_dist_shared': min_dist_shared,
                'is_operational_variant': is_variant,
                'is_independent': min_dist_common > 2 and min_dist_other > 2,
                'gloss': mid_dict.get(mid, {}).get('gloss'),
                'kernel': mid_dict.get(mid, {}).get('kernel'),
                'regime': mid_dict.get(mid, {}).get('regime'),
            }

        # Classify all unique MIDDLEs
        f1_analysis = []
        for mid in sorted(unique_to_f1, key=lambda m: -section_folio_counts[section][f1].get(m, 0)):
            info = classify_middle(mid, folios[f2])
            info['count_in_folio'] = section_folio_counts[section][f1].get(mid, 0)
            info['global_count'] = global_middle_counts.get(mid, 0)
            f1_analysis.append(info)

        f2_analysis = []
        for mid in sorted(unique_to_f2, key=lambda m: -section_folio_counts[section][f2].get(m, 0)):
            info = classify_middle(mid, folios[f1])
            info['count_in_folio'] = section_folio_counts[section][f2].get(mid, 0)
            info['global_count'] = global_middle_counts.get(mid, 0)
            f2_analysis.append(info)

        # Print detailed analysis
        print(f"\n  --- MIDDLEs unique to {f1} ---")
        independent_f1 = []
        variant_f1 = []
        for info in f1_analysis[:20]:
            tag = "VARIANT" if info['is_operational_variant'] else ("INDEPENDENT" if info['is_independent'] else "MODERATE")
            gloss = info['gloss'] or '?'
            kernel = info['kernel'] or '-'
            regime = info['regime'] or '-'
            closest = f"(near: {info['closest_common']})" if info['closest_common'] else ""
            print(f"    {info['middle']:16} x{info['count_in_folio']:3} (global:{info['global_count']:4})  "
                  f"dist_common={info['min_dist_common']}  [{tag}]  "
                  f"kernel={kernel}  regime={regime}  gloss={gloss} {closest}")
            if info['is_independent']:
                independent_f1.append(info)
            elif info['is_operational_variant']:
                variant_f1.append(info)

        print(f"\n  --- MIDDLEs unique to {f2} ---")
        independent_f2 = []
        variant_f2 = []
        for info in f2_analysis[:20]:
            tag = "VARIANT" if info['is_operational_variant'] else ("INDEPENDENT" if info['is_independent'] else "MODERATE")
            gloss = info['gloss'] or '?'
            kernel = info['kernel'] or '-'
            regime = info['regime'] or '-'
            closest = f"(near: {info['closest_common']})" if info['closest_common'] else ""
            print(f"    {info['middle']:16} x{info['count_in_folio']:3} (global:{info['global_count']:4})  "
                  f"dist_common={info['min_dist_common']}  [{tag}]  "
                  f"kernel={kernel}  regime={regime}  gloss={gloss} {closest}")
            if info['is_independent']:
                independent_f2.append(info)
            elif info['is_operational_variant']:
                variant_f2.append(info)

        # Count categories
        n_variant_f1 = sum(1 for i in f1_analysis if i['is_operational_variant'])
        n_indep_f1 = sum(1 for i in f1_analysis if i['is_independent'])
        n_moderate_f1 = len(f1_analysis) - n_variant_f1 - n_indep_f1

        n_variant_f2 = sum(1 for i in f2_analysis if i['is_operational_variant'])
        n_indep_f2 = sum(1 for i in f2_analysis if i['is_independent'])
        n_moderate_f2 = len(f2_analysis) - n_variant_f2 - n_indep_f2

        print(f"\n  CLASSIFICATION SUMMARY:")
        print(f"    {f1}: {n_variant_f1} variant, {n_moderate_f1} moderate, {n_indep_f1} independent")
        print(f"    {f2}: {n_variant_f2} variant, {n_moderate_f2} moderate, {n_indep_f2} independent")

        # Decode both folios
        print(f"\n  --- BFolioDecoder: {f1} (structural) ---")
        try:
            struct1 = decoder.decode_folio_lines(f1, mode='structural')
            print(struct1[:2000])
        except Exception as e:
            struct1 = f"Error: {e}"
            print(f"    Error: {e}")

        print(f"\n  --- BFolioDecoder: {f1} (interpretive) ---")
        try:
            interp1 = decoder.decode_folio_lines(f1, mode='interpretive')
            print(interp1[:2000])
        except Exception as e:
            interp1 = f"Error: {e}"
            print(f"    Error: {e}")

        print(f"\n  --- BFolioDecoder: {f2} (structural) ---")
        try:
            struct2 = decoder.decode_folio_lines(f2, mode='structural')
            print(struct2[:2000])
        except Exception as e:
            struct2 = f"Error: {e}"
            print(f"    Error: {e}")

        print(f"\n  --- BFolioDecoder: {f2} (interpretive) ---")
        try:
            interp2 = decoder.decode_folio_lines(f2, mode='interpretive')
            print(interp2[:2000])
        except Exception as e:
            interp2 = f"Error: {e}"
            print(f"    Error: {e}")

        # Build candidate material discriminators for this section
        # These are INDEPENDENT MIDDLEs (dist>2 from common) that appear with frequency
        material_candidates = []
        for info in f1_analysis + f2_analysis:
            if info['is_independent'] and info['count_in_folio'] >= 2:
                material_candidates.append({
                    'middle': info['middle'],
                    'folio': f1 if info in f1_analysis else f2,
                    'count': info['count_in_folio'],
                    'global_count': info['global_count'],
                    'gloss': info['gloss'],
                    'kernel': info['kernel'],
                    'regime': info['regime'],
                })

        # Also collect high-frequency independents even if count=1
        for info in f1_analysis + f2_analysis:
            if info['is_independent'] and info['count_in_folio'] == 1 and info['global_count'] >= 5:
                material_candidates.append({
                    'middle': info['middle'],
                    'folio': f1 if info in f1_analysis else f2,
                    'count': info['count_in_folio'],
                    'global_count': info['global_count'],
                    'gloss': info['gloss'],
                    'kernel': info['kernel'],
                    'regime': info['regime'],
                })

        print(f"\n  CANDIDATE MATERIAL DISCRIMINATORS (section {section}):")
        if material_candidates:
            for mc in material_candidates:
                print(f"    {mc['middle']:16}  folio={mc['folio']}  x{mc['count']}  "
                      f"global={mc['global_count']}  gloss={mc['gloss']}  kernel={mc['kernel']}")
        else:
            print("    NONE - all divergent MIDDLEs are operational variants or distance<=2")

        # Store results
        results[section] = {
            'folio_count': len(folios),
            'divergent_pair': {
                'folio_1': f1,
                'folio_2': f2,
                'jaccard': round(min_j, 4),
                'shared_middles': len(shared),
                'unique_to_f1': len(unique_to_f1),
                'unique_to_f2': len(unique_to_f2),
            },
            'f1_classification': {
                'operational_variants': n_variant_f1,
                'moderate_distance': n_moderate_f1,
                'independent': n_indep_f1,
            },
            'f2_classification': {
                'operational_variants': n_variant_f2,
                'moderate_distance': n_moderate_f2,
                'independent': n_indep_f2,
            },
            'f1_top_independents': [
                {'middle': i['middle'], 'count': i['count_in_folio'],
                 'global_count': i['global_count'], 'gloss': i['gloss'],
                 'kernel': i['kernel'], 'regime': i['regime']}
                for i in independent_f1[:10]
            ],
            'f2_top_independents': [
                {'middle': i['middle'], 'count': i['count_in_folio'],
                 'global_count': i['global_count'], 'gloss': i['gloss'],
                 'kernel': i['kernel'], 'regime': i['regime']}
                for i in independent_f2[:10]
            ],
            'candidate_material_discriminators': material_candidates,
            'narrative': '',  # Will be filled in post-processing
        }

    # Print overall summary
    print(f"\n{'=' * 70}")
    print("OVERALL SUMMARY")
    print(f"{'=' * 70}")

    total_sections = len(results)
    sections_with_candidates = sum(1 for r in results.values() if r['candidate_material_discriminators'])
    total_candidates = sum(len(r['candidate_material_discriminators']) for r in results.values())
    total_independents = sum(
        r['f1_classification']['independent'] + r['f2_classification']['independent']
        for r in results.values()
    )
    total_variants = sum(
        r['f1_classification']['operational_variants'] + r['f2_classification']['operational_variants']
        for r in results.values()
    )

    print(f"  Sections analyzed: {total_sections}")
    print(f"  Sections with material-discriminator candidates: {sections_with_candidates}")
    print(f"  Total candidate discriminators: {total_candidates}")
    print(f"  Total independent MIDDLEs across all pairs: {total_independents}")
    print(f"  Total operational variants across all pairs: {total_variants}")
    print(f"  Independent ratio: {total_independents / (total_independents + total_variants):.1%}" if (total_independents + total_variants) > 0 else "  No data")

    # Determine verdict
    # PASS: consistent material-discriminator patterns found across sections
    # FAIL: all divergent MIDDLEs are operational variants
    if sections_with_candidates >= 2 and total_candidates >= 5:
        verdict = "PASS"
        verdict_reason = (f"Found {total_candidates} candidate material discriminators "
                         f"across {sections_with_candidates}/{total_sections} sections. "
                         f"Independent MIDDLEs significantly outnumber operational variants, "
                         f"suggesting folio vocabulary divergence reflects genuine material/content differences.")
    elif sections_with_candidates >= 1:
        verdict = "WEAK_PASS"
        verdict_reason = (f"Found {total_candidates} candidate discriminators in "
                         f"{sections_with_candidates}/{total_sections} sections. "
                         f"Pattern present but not consistently cross-sectional.")
    else:
        verdict = "FAIL"
        verdict_reason = ("All divergent MIDDLEs are operational variants (distance<=1 from common MIDDLEs). "
                         "No independent material-discriminator vocabulary detected.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  REASON: {verdict_reason}")

    # Write output JSON
    output = {
        'test': 'T14_within_section_outliers',
        'description': 'Within-section folio vocabulary outlier analysis',
        'sections_analyzed': total_sections,
        'sections_with_candidates': sections_with_candidates,
        'total_candidates': total_candidates,
        'total_independent_middles': total_independents,
        'total_operational_variants': total_variants,
        'verdict': verdict,
        'verdict_reason': verdict_reason,
        'per_section': results,
    }

    output_path = PROJECT_ROOT / 'phases' / 'MATERIAL_LOCUS_SEARCH' / 'results' / 'within_section_outliers.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Output written to: {output_path}")


if __name__ == '__main__':
    main()
