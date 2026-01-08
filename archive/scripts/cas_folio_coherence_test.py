"""
CAS-FOLIO: Within-Folio Coherence Test for Currier A

Question: Do entries within a Currier A folio share more vocabulary
than entries on different folios within the same section?

Tests:
  T1: Within-folio vs between-folio Jaccard similarity
  T2: Folio vocabulary exclusivity (% of tokens unique to one folio)
  T3: Adjacent entry similarity (do consecutive lines share more?)
  T4: Folio-level marker concentration (does each folio favor certain markers?)

If within-folio similarity >> between-folio similarity, then folios
have internal thematic coherence beyond section-level organization.
"""

import sys
import os
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np
from scipy import stats
import random

# Load data
DATA_FILE = 'data/transcriptions/interlinear_full_words.txt'

def load_currier_a_entries():
    """Load Currier A entries grouped by folio."""

    entries_by_folio = defaultdict(list)
    folio_sections = {}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                # Only Currier A
                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None:
                        entries_by_folio[current_entry['folio']].append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }
                    folio_sections[folio] = section

                current_entry['tokens'].append(word)

        # Don't forget last entry
        if current_entry is not None:
            entries_by_folio[current_entry['folio']].append(current_entry)

    return entries_by_folio, folio_sections


def jaccard(set1, set2):
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def test_1_within_vs_between_folio(entries_by_folio, folio_sections):
    """T1: Compare within-folio vs between-folio vocabulary similarity."""

    print("\n" + "="*60)
    print("T1: WITHIN-FOLIO vs BETWEEN-FOLIO VOCABULARY SIMILARITY")
    print("="*60)

    # Get folio vocabularies
    folio_vocab = {}
    for folio, entries in entries_by_folio.items():
        vocab = set()
        for entry in entries:
            vocab.update(entry['tokens'])
        if len(vocab) >= 5:  # Minimum vocabulary threshold
            folio_vocab[folio] = vocab

    # Group folios by section
    section_folios = defaultdict(list)
    for folio in folio_vocab:
        section = folio_sections.get(folio, '')
        if section:
            section_folios[section].append(folio)

    print(f"\nFolios with sufficient vocabulary: {len(folio_vocab)}")
    print(f"Sections: {dict((s, len(f)) for s, f in section_folios.items())}")

    # Calculate within-folio similarity (entry pairs within same folio)
    within_sims = []
    for folio, entries in entries_by_folio.items():
        if len(entries) >= 2:
            entry_vocabs = [set(e['tokens']) for e in entries if len(e['tokens']) >= 2]
            for i, v1 in enumerate(entry_vocabs):
                for v2 in entry_vocabs[i+1:]:
                    sim = jaccard(v1, v2)
                    within_sims.append(sim)

    # Calculate between-folio similarity (entry pairs from different folios, same section)
    between_sims = []
    for section, folios in section_folios.items():
        if len(folios) >= 2:
            # Sample pairs to avoid combinatorial explosion
            folio_pairs = list(combinations(folios, 2))
            if len(folio_pairs) > 500:
                folio_pairs = random.sample(folio_pairs, 500)

            for f1, f2 in folio_pairs:
                # Pick random entries from each folio
                e1_list = entries_by_folio[f1]
                e2_list = entries_by_folio[f2]

                if e1_list and e2_list:
                    # Sample up to 3 pairs per folio pair
                    for _ in range(min(3, len(e1_list), len(e2_list))):
                        e1 = random.choice(e1_list)
                        e2 = random.choice(e2_list)
                        sim = jaccard(set(e1['tokens']), set(e2['tokens']))
                        between_sims.append(sim)

    print(f"\nWithin-folio entry pairs: {len(within_sims)}")
    print(f"Between-folio entry pairs: {len(between_sims)}")

    if within_sims and between_sims:
        within_mean = np.mean(within_sims)
        between_mean = np.mean(between_sims)

        print(f"\nWithin-folio mean Jaccard:  {within_mean:.4f} (std: {np.std(within_sims):.4f})")
        print(f"Between-folio mean Jaccard: {between_mean:.4f} (std: {np.std(between_sims):.4f})")
        print(f"Ratio (within/between):     {within_mean/between_mean:.2f}x" if between_mean > 0 else "N/A")

        # Mann-Whitney U test
        stat, p_value = stats.mannwhitneyu(within_sims, between_sims, alternative='greater')
        print(f"\nMann-Whitney U test (within > between):")
        print(f"  U-statistic: {stat:.1f}")
        print(f"  p-value: {p_value:.6f}")

        # Effect size (rank-biserial correlation)
        n1, n2 = len(within_sims), len(between_sims)
        r = 1 - (2*stat)/(n1*n2)
        print(f"  Effect size (r): {r:.3f}")

        if p_value < 0.001 and within_mean > between_mean * 1.2:
            verdict = "FOLIO_COHERENT"
            interpretation = "Entries within a folio share significantly more vocabulary than entries across folios."
        elif p_value < 0.05 and within_mean > between_mean:
            verdict = "WEAK_COHERENCE"
            interpretation = "Slight within-folio vocabulary enrichment detected."
        else:
            verdict = "NO_COHERENCE"
            interpretation = "No evidence that folios organize entries by vocabulary."

        print(f"\nVerdict: {verdict}")
        print(f"Interpretation: {interpretation}")

        return {
            'within_mean': within_mean,
            'between_mean': between_mean,
            'ratio': within_mean / between_mean if between_mean > 0 else float('inf'),
            'p_value': p_value,
            'effect_size': r,
            'verdict': verdict
        }

    return {'verdict': 'INSUFFICIENT_DATA'}


def test_2_folio_vocabulary_exclusivity(entries_by_folio, folio_sections):
    """T2: What percentage of vocabulary is exclusive to single folios?"""

    print("\n" + "="*60)
    print("T2: FOLIO VOCABULARY EXCLUSIVITY")
    print("="*60)

    # Track which folios each token appears in
    token_folios = defaultdict(set)
    folio_vocab_size = {}

    for folio, entries in entries_by_folio.items():
        vocab = set()
        for entry in entries:
            for token in entry['tokens']:
                token_folios[token].add(folio)
                vocab.add(token)
        folio_vocab_size[folio] = len(vocab)

    # Count exclusivity levels
    exclusivity = Counter()
    for token, folios in token_folios.items():
        exclusivity[len(folios)] += 1

    total_tokens = len(token_folios)
    single_folio = exclusivity[1]

    print(f"\nTotal unique tokens in Currier A: {total_tokens}")
    print(f"Tokens appearing in exactly 1 folio: {single_folio} ({100*single_folio/total_tokens:.1f}%)")
    print(f"Tokens appearing in 2 folios: {exclusivity[2]} ({100*exclusivity[2]/total_tokens:.1f}%)")
    print(f"Tokens appearing in 3+ folios: {sum(v for k, v in exclusivity.items() if k >= 3)} ({100*sum(v for k, v in exclusivity.items() if k >= 3)/total_tokens:.1f}%)")

    # Compare to section exclusivity
    token_sections = defaultdict(set)
    for folio, entries in entries_by_folio.items():
        section = folio_sections.get(folio, '')
        for entry in entries:
            for token in entry['tokens']:
                token_sections[token].add(section)

    single_section = sum(1 for t, s in token_sections.items() if len(s) == 1)
    print(f"\nTokens appearing in exactly 1 section: {single_section} ({100*single_section/total_tokens:.1f}%)")

    # Key ratio: folio exclusivity vs section exclusivity
    folio_exclusive_pct = 100 * single_folio / total_tokens
    section_exclusive_pct = 100 * single_section / total_tokens

    print(f"\nFolio-exclusive: {folio_exclusive_pct:.1f}%")
    print(f"Section-exclusive: {section_exclusive_pct:.1f}%")
    print(f"Gap (folio - section): {folio_exclusive_pct - section_exclusive_pct:.1f}pp")

    if folio_exclusive_pct > section_exclusive_pct + 20:
        verdict = "FOLIO_SPECIFIC"
        interpretation = "Most vocabulary is folio-specific beyond section boundaries."
    elif folio_exclusive_pct > section_exclusive_pct + 5:
        verdict = "MODERATE_FOLIO_SPECIFICITY"
        interpretation = "Some vocabulary is folio-specific."
    else:
        verdict = "SECTION_DRIVEN"
        interpretation = "Vocabulary exclusivity is primarily section-driven, not folio-driven."

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interpretation}")

    return {
        'folio_exclusive_pct': folio_exclusive_pct,
        'section_exclusive_pct': section_exclusive_pct,
        'gap': folio_exclusive_pct - section_exclusive_pct,
        'verdict': verdict
    }


def test_3_adjacent_entry_similarity(entries_by_folio):
    """T3: Do adjacent entries (consecutive lines) share more vocabulary?"""

    print("\n" + "="*60)
    print("T3: ADJACENT ENTRY SIMILARITY")
    print("="*60)

    adjacent_sims = []
    nonadjacent_sims = []

    for folio, entries in entries_by_folio.items():
        if len(entries) < 3:
            continue

        # Sort by line number
        sorted_entries = sorted(entries, key=lambda e: int(e['line']) if e['line'].isdigit() else 0)

        for i in range(len(sorted_entries)):
            v1 = set(sorted_entries[i]['tokens'])
            if len(v1) < 2:
                continue

            for j in range(i+1, len(sorted_entries)):
                v2 = set(sorted_entries[j]['tokens'])
                if len(v2) < 2:
                    continue

                sim = jaccard(v1, v2)

                if j == i + 1:
                    adjacent_sims.append(sim)
                else:
                    nonadjacent_sims.append(sim)

    print(f"\nAdjacent entry pairs: {len(adjacent_sims)}")
    print(f"Non-adjacent entry pairs: {len(nonadjacent_sims)}")

    if adjacent_sims and nonadjacent_sims:
        adj_mean = np.mean(adjacent_sims)
        nonadj_mean = np.mean(nonadjacent_sims)

        print(f"\nAdjacent mean Jaccard:     {adj_mean:.4f}")
        print(f"Non-adjacent mean Jaccard: {nonadj_mean:.4f}")
        print(f"Ratio: {adj_mean/nonadj_mean:.2f}x" if nonadj_mean > 0 else "N/A")

        stat, p_value = stats.mannwhitneyu(adjacent_sims, nonadjacent_sims, alternative='greater')
        print(f"\nMann-Whitney U (adjacent > non-adjacent): p = {p_value:.6f}")

        if p_value < 0.01 and adj_mean > nonadj_mean * 1.2:
            verdict = "SEQUENTIAL_COHERENCE"
            interpretation = "Adjacent entries share more vocabulary - suggests sequential organization."
        elif p_value < 0.05:
            verdict = "WEAK_SEQUENTIAL"
            interpretation = "Slight sequential pattern detected."
        else:
            verdict = "NO_SEQUENCE"
            interpretation = "Entry order within folio appears arbitrary."

        print(f"\nVerdict: {verdict}")

        return {
            'adjacent_mean': adj_mean,
            'nonadjacent_mean': nonadj_mean,
            'p_value': p_value,
            'verdict': verdict
        }

    return {'verdict': 'INSUFFICIENT_DATA'}


def test_4_folio_marker_concentration(entries_by_folio, folio_sections):
    """T4: Does each folio favor specific markers?"""

    print("\n" + "="*60)
    print("T4: FOLIO-LEVEL MARKER CONCENTRATION")
    print("="*60)

    MARKERS = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    folio_markers = defaultdict(Counter)
    section_markers = defaultdict(Counter)

    for folio, entries in entries_by_folio.items():
        section = folio_sections.get(folio, '')
        for entry in entries:
            for token in entry['tokens']:
                for m in MARKERS:
                    if token.startswith(m):
                        folio_markers[folio][m] += 1
                        section_markers[section][m] += 1
                        break

    # Calculate concentration (max marker %) for each folio
    folio_concentrations = []
    section_concentrations = {}

    for folio, markers in folio_markers.items():
        total = sum(markers.values())
        if total >= 10:
            max_pct = max(markers.values()) / total
            folio_concentrations.append(max_pct)

    for section, markers in section_markers.items():
        total = sum(markers.values())
        if total >= 10:
            max_pct = max(markers.values()) / total
            section_concentrations[section] = max_pct

    print(f"\nFolios analyzed: {len(folio_concentrations)}")
    print(f"Mean folio marker concentration: {np.mean(folio_concentrations):.1%}")
    print(f"Std: {np.std(folio_concentrations):.1%}")

    print(f"\nSection marker concentrations:")
    for section, conc in sorted(section_concentrations.items()):
        print(f"  {section}: {conc:.1%}")

    # Compare: are folios more concentrated than their sections?
    folio_mean = np.mean(folio_concentrations)
    section_mean = np.mean(list(section_concentrations.values())) if section_concentrations else 0

    print(f"\nFolio mean concentration: {folio_mean:.1%}")
    print(f"Section mean concentration: {section_mean:.1%}")

    if folio_mean > section_mean + 0.1:
        verdict = "FOLIO_SPECIALIZED"
        interpretation = "Folios specialize in specific markers beyond section-level patterns."
    elif folio_mean > section_mean + 0.03:
        verdict = "WEAK_SPECIALIZATION"
        interpretation = "Slight folio-level marker specialization."
    else:
        verdict = "SECTION_DRIVEN"
        interpretation = "Marker distribution is section-driven; folios don't add specialization."

    print(f"\nVerdict: {verdict}")

    return {
        'folio_mean_concentration': folio_mean,
        'section_mean_concentration': section_mean,
        'verdict': verdict
    }


def main():
    print("="*60)
    print("CAS-FOLIO: WITHIN-FOLIO COHERENCE TEST")
    print("="*60)
    print("\nQuestion: Do Currier A folios organize entries thematically,")
    print("or are they just physical containers?")

    # Load data
    print("\nLoading Currier A entries...")
    entries_by_folio, folio_sections = load_currier_a_entries()

    total_entries = sum(len(e) for e in entries_by_folio.values())
    print(f"Loaded {total_entries} entries across {len(entries_by_folio)} folios")

    # Run tests
    results = {}
    results['t1'] = test_1_within_vs_between_folio(entries_by_folio, folio_sections)
    results['t2'] = test_2_folio_vocabulary_exclusivity(entries_by_folio, folio_sections)
    results['t3'] = test_3_adjacent_entry_similarity(entries_by_folio)
    results['t4'] = test_4_folio_marker_concentration(entries_by_folio, folio_sections)

    # Synthesis
    print("\n" + "="*60)
    print("SYNTHESIS")
    print("="*60)

    verdicts = [r.get('verdict', 'UNKNOWN') for r in results.values()]

    coherent_signals = sum(1 for v in verdicts if 'COHERENT' in v or 'SPECIFIC' in v or 'SPECIALIZED' in v or 'SEQUENTIAL' in v)

    print(f"\nTest verdicts:")
    print(f"  T1 (vocabulary sharing): {results['t1'].get('verdict', 'N/A')}")
    print(f"  T2 (vocabulary exclusivity): {results['t2'].get('verdict', 'N/A')}")
    print(f"  T3 (adjacent similarity): {results['t3'].get('verdict', 'N/A')}")
    print(f"  T4 (marker concentration): {results['t4'].get('verdict', 'N/A')}")

    print(f"\nCoherence signals: {coherent_signals}/4")

    if coherent_signals >= 3:
        final_verdict = "FOLIO_ORGANIZED"
        interpretation = """
Currier A folios show internal thematic coherence.
Entries within a folio share vocabulary beyond section-level patterns.
This suggests folios are organized by topic, not just physical containers.

PROPOSED CONSTRAINT:
"Currier A folios exhibit within-folio vocabulary coherence beyond
section-level organization; folios group related entries."
"""
    elif coherent_signals >= 2:
        final_verdict = "PARTIAL_ORGANIZATION"
        interpretation = """
Some evidence of within-folio organization, but not conclusive.
Folios may partially group related entries.

PROPOSED CONSTRAINT:
"Currier A folios show weak within-folio coherence; organization
is primarily section-driven with modest folio-level clustering."
"""
    else:
        final_verdict = "NO_FOLIO_ORGANIZATION"
        interpretation = """
No evidence that Currier A folios organize entries thematically.
Folios appear to be physical containers only.
Organization hierarchy confirmed as: SECTION > MARKER > BLOCK
Folio boundaries do not add organizational structure.

PROPOSED CONSTRAINT:
"Currier A folios are physical containers without thematic coherence;
within-folio vocabulary similarity equals between-folio similarity."
"""

    print(f"\nFINAL VERDICT: {final_verdict}")
    print(interpretation)

    return results, final_verdict


if __name__ == '__main__':
    results, verdict = main()
