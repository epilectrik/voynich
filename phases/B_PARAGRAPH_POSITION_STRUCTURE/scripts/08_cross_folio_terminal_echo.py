"""
08_cross_folio_terminal_echo.py - Test cross-folio TERMINAL FL vocabulary echo

Hypothesis: B folios chain together in a processing pipeline.
- Folio X's late lines describe output (TERMINAL FL)
- Folio Y's early lines describe that same material as input (TERMINAL FL)

If true: TERMINAL FL vocabulary in LATE lines of one folio should
overlap with TERMINAL FL vocabulary in EARLY lines of other folios.

Tests:
1. Do late-folio TERMINAL tokens appear in early-folio positions elsewhere?
2. Is this pattern stronger within sections than across sections?
3. Is observed overlap greater than chance?
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
import random

# TERMINAL FL suffixes
TERMINAL_SUFFIXES = {'y', 'aly', 'am', 'dy', 'ly'}

def get_terminal_fl_tokens(tokens, morph):
    """Extract tokens with TERMINAL FL suffixes."""
    terminal_tokens = []
    for t in tokens:
        m = morph.extract(t.word)
        if m and m.suffix in TERMINAL_SUFFIXES:
            terminal_tokens.append({
                'word': t.word,
                'middle': m.middle,
                'suffix': m.suffix
            })
    return terminal_tokens

def main():
    tx = Transcript()
    morph = Morphology()

    # Group B tokens by folio
    folio_tokens = defaultdict(list)
    folio_sections = {}

    for t in tx.currier_b():
        folio_tokens[t.folio].append(t)
        folio_sections[t.folio] = t.section

    print("=" * 80)
    print("CROSS-FOLIO TERMINAL FL VOCABULARY ECHO TEST")
    print("=" * 80)
    print(f"\nTotal B folios: {len(folio_tokens)}")

    # For each folio, extract TERMINAL FL from early vs late thirds
    folio_terminal = {}  # folio -> {'early': set of words, 'late': set of words}

    for folio, tokens in folio_tokens.items():
        # Group by line
        lines = defaultdict(list)
        for t in tokens:
            lines[t.line].append(t)

        sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
        n_lines = len(sorted_lines)

        if n_lines < 3:
            continue

        third = n_lines // 3
        early_lines = sorted_lines[:third]
        late_lines = sorted_lines[2*third:]

        # Get tokens from early/late
        early_tokens = [t for ln in early_lines for t in lines[ln]]
        late_tokens = [t for ln in late_lines for t in lines[ln]]

        # Extract TERMINAL FL
        early_terminal = get_terminal_fl_tokens(early_tokens, morph)
        late_terminal = get_terminal_fl_tokens(late_tokens, morph)

        folio_terminal[folio] = {
            'early_words': set(t['word'] for t in early_terminal),
            'early_middles': set(t['middle'] for t in early_terminal if t['middle']),
            'late_words': set(t['word'] for t in late_terminal),
            'late_middles': set(t['middle'] for t in late_terminal if t['middle']),
            'section': folio_sections.get(folio, 'UNK')
        }

    print(f"Folios with sufficient lines: {len(folio_terminal)}")

    # Test 1: Do late-folio TERMINAL tokens appear in early-folio positions elsewhere?
    print("\n" + "=" * 80)
    print("TEST 1: LATE-TO-EARLY TERMINAL FL ECHO")
    print("=" * 80)

    # For each folio's late TERMINAL vocabulary, count how many other folios
    # have that vocabulary in their early lines
    echo_counts = []  # (folio, late_word, n_folios_with_early_match)

    all_late_words = set()
    all_early_words = set()

    for folio, data in folio_terminal.items():
        all_late_words |= data['late_words']
        all_early_words |= data['early_words']

    # Words that appear in BOTH late (somewhere) and early (somewhere)
    echo_words = all_late_words & all_early_words
    late_only_words = all_late_words - all_early_words
    early_only_words = all_early_words - all_late_words

    print(f"\nTERMINAL FL word counts:")
    print(f"  Unique words in LATE positions: {len(all_late_words)}")
    print(f"  Unique words in EARLY positions: {len(all_early_words)}")
    print(f"  Words appearing in BOTH: {len(echo_words)} ({len(echo_words)/len(all_late_words)*100:.1f}% of late)")
    print(f"  LATE-only words: {len(late_only_words)}")
    print(f"  EARLY-only words: {len(early_only_words)}")

    # Test 2: Pairwise folio echo analysis
    print("\n" + "=" * 80)
    print("TEST 2: PAIRWISE FOLIO ECHO MATRIX")
    print("=" * 80)

    folios = sorted(folio_terminal.keys())
    n_folios = len(folios)

    # Compute late-to-early Jaccard for all folio pairs
    same_section_echoes = []
    diff_section_echoes = []

    for i, f1 in enumerate(folios):
        for j, f2 in enumerate(folios):
            if i == j:
                continue

            # f1's late vocabulary vs f2's early vocabulary
            late_vocab = folio_terminal[f1]['late_words']
            early_vocab = folio_terminal[f2]['early_words']

            if not late_vocab or not early_vocab:
                continue

            overlap = len(late_vocab & early_vocab)
            union = len(late_vocab | early_vocab)
            jaccard = overlap / union if union > 0 else 0

            same_section = folio_terminal[f1]['section'] == folio_terminal[f2]['section']

            if same_section:
                same_section_echoes.append(jaccard)
            else:
                diff_section_echoes.append(jaccard)

    print(f"\nLate(folio X) -> Early(folio Y) Jaccard overlap:")
    print(f"  Same section pairs: mean={np.mean(same_section_echoes):.4f} (n={len(same_section_echoes)})")
    print(f"  Diff section pairs: mean={np.mean(diff_section_echoes):.4f} (n={len(diff_section_echoes)})")

    if same_section_echoes and diff_section_echoes:
        t_stat, p_val = stats.ttest_ind(same_section_echoes, diff_section_echoes)
        print(f"  t-test: t={t_stat:.3f}, p={p_val:.4f}")

    # Test 3: Compare to null model (shuffled positions)
    print("\n" + "=" * 80)
    print("TEST 3: NULL MODEL COMPARISON")
    print("=" * 80)

    # Observed: late->early overlap across folios
    observed_overlaps = []
    for i, f1 in enumerate(folios):
        for j, f2 in enumerate(folios):
            if i >= j:
                continue
            late1 = folio_terminal[f1]['late_words']
            early2 = folio_terminal[f2]['early_words']
            late2 = folio_terminal[f2]['late_words']
            early1 = folio_terminal[f1]['early_words']

            # Both directions
            if late1 and early2:
                observed_overlaps.append(len(late1 & early2))
            if late2 and early1:
                observed_overlaps.append(len(late2 & early1))

    observed_mean = np.mean(observed_overlaps)

    # Null model: shuffle early/late labels within each folio
    null_means = []
    for _ in range(1000):
        shuffled_overlaps = []
        for i, f1 in enumerate(folios):
            for j, f2 in enumerate(folios):
                if i >= j:
                    continue

                # Randomly swap early/late for each folio
                if random.random() < 0.5:
                    vocab1 = folio_terminal[f1]['late_words']
                else:
                    vocab1 = folio_terminal[f1]['early_words']

                if random.random() < 0.5:
                    vocab2 = folio_terminal[f2]['early_words']
                else:
                    vocab2 = folio_terminal[f2]['late_words']

                if vocab1 and vocab2:
                    shuffled_overlaps.append(len(vocab1 & vocab2))

        null_means.append(np.mean(shuffled_overlaps) if shuffled_overlaps else 0)

    null_mean = np.mean(null_means)
    null_std = np.std(null_means)
    z_score = (observed_mean - null_mean) / null_std if null_std > 0 else 0

    print(f"\nLate->Early overlap (word count):")
    print(f"  Observed mean: {observed_mean:.3f}")
    print(f"  Null mean: {null_mean:.3f} (sd={null_std:.3f})")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  p-value (one-tailed): {1 - stats.norm.cdf(z_score):.4f}")

    # Test 4: Specific MIDDLE tracking
    print("\n" + "=" * 80)
    print("TEST 4: SPECIFIC MIDDLE TRACKING")
    print("=" * 80)

    # Which MIDDLEs appear in both late and early positions?
    all_late_middles = set()
    all_early_middles = set()

    for folio, data in folio_terminal.items():
        all_late_middles |= data['late_middles']
        all_early_middles |= data['early_middles']

    shared_middles = all_late_middles & all_early_middles

    print(f"\nTERMINAL FL MIDDLE analysis:")
    print(f"  Unique MIDDLEs in LATE: {len(all_late_middles)}")
    print(f"  Unique MIDDLEs in EARLY: {len(all_early_middles)}")
    print(f"  MIDDLEs in BOTH: {len(shared_middles)} ({len(shared_middles)/len(all_late_middles)*100:.1f}% of late)")

    # Count how many folios each shared MIDDLE appears in
    middle_folio_counts = defaultdict(lambda: {'early': 0, 'late': 0})
    for folio, data in folio_terminal.items():
        for m in data['early_middles']:
            if m in shared_middles:
                middle_folio_counts[m]['early'] += 1
        for m in data['late_middles']:
            if m in shared_middles:
                middle_folio_counts[m]['late'] += 1

    print(f"\nTop shared MIDDLEs (by total folio appearances):")
    sorted_middles = sorted(middle_folio_counts.items(),
                           key=lambda x: x[1]['early'] + x[1]['late'], reverse=True)
    for m, counts in sorted_middles[:15]:
        print(f"  {m}: early={counts['early']} folios, late={counts['late']} folios")

    # Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)

    if z_score > 1.96:
        print(f"\n[SUPPORTED] Late->Early echo is STRONGER than chance (z={z_score:.2f})")
        print("  TERMINAL FL vocabulary flows from late positions to early positions")
        print("  Consistent with folio chaining hypothesis")
    elif z_score > 1.0:
        print(f"\n[WEAK] Late->Early echo is slightly above chance (z={z_score:.2f})")
        print("  Some evidence for vocabulary flow, but not conclusive")
    else:
        print(f"\n[NOT SUPPORTED] Late->Early echo is NOT stronger than chance (z={z_score:.2f})")
        print("  No evidence for systematic folio chaining via TERMINAL FL")

    if same_section_echoes and diff_section_echoes and np.mean(same_section_echoes) > np.mean(diff_section_echoes):
        print("\n[SECTION EFFECT] Same-section folio pairs show stronger echo")
        print("  Suggests chaining is section-internal")

    # Save results
    results = {
        'summary': {
            'folios_analyzed': len(folio_terminal),
            'echo_words': len(echo_words),
            'late_only_words': len(late_only_words),
            'early_only_words': len(early_only_words),
            'echo_rate': len(echo_words) / len(all_late_words) if all_late_words else 0,
            'observed_overlap_mean': float(observed_mean),
            'null_overlap_mean': float(null_mean),
            'z_score': float(z_score),
            'same_section_jaccard': float(np.mean(same_section_echoes)) if same_section_echoes else 0,
            'diff_section_jaccard': float(np.mean(diff_section_echoes)) if diff_section_echoes else 0,
        },
        'shared_middles': list(shared_middles),
        'top_shared_middles': [
            {'middle': m, 'early_folios': counts['early'], 'late_folios': counts['late']}
            for m, counts in sorted_middles[:20]
        ]
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/08_cross_folio_terminal_echo.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
