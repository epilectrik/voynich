"""
07_glossary_hypothesis_test.py - Test if A is a glossary/index to B

HYPOTHESIS: A is a glossary/index where:
- RI tokens are entry headwords (labels)
- PP tokens reference B vocabulary being indexed
- Linkers are "see also" cross-references
- Paragraph structure is: RI header -> PP body -> optional linker

PREDICTIONS:
1. RI should be LINE-INITIAL (headword position)
2. PP vocabulary in A paragraphs should predict specific B folios
3. Linker source/destination should share more PP than random pairs
4. Entry structure should be consistent (RI first, then PP)
5. RI might have distinct morphological profile (labels vs content)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import numpy as np
import json

tx = Transcript()
morph = Morphology()

# Build B vocabulary
print("Building vocabulary sets...")
b_tokens = list(tx.currier_b())
b_middles = set()
b_folio_middles = defaultdict(set)

for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)
        b_folio_middles[t.folio].add(m.middle)

print(f"  B vocabulary: {len(b_middles)} MIDDLEs across {len(b_folio_middles)} folios")

# Get A tokens
a_tokens = list(tx.currier_a())
print(f"  A tokens: {len(a_tokens)}")

# ============================================================
# TEST 1: RI LINE-INITIAL CONCENTRATION
# ============================================================
print("\n" + "="*70)
print("TEST 1: RI LINE-INITIAL CONCENTRATION")
print("="*70)
print("Prediction: If RI are headwords, they should be LINE-INITIAL")
print()

ri_initial = 0
ri_non_initial = 0
pp_initial = 0
pp_non_initial = 0

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        is_ri = m.middle not in b_middles
        is_initial = t.line_initial

        if is_ri:
            if is_initial:
                ri_initial += 1
            else:
                ri_non_initial += 1
        else:
            if is_initial:
                pp_initial += 1
            else:
                pp_non_initial += 1

ri_initial_rate = ri_initial / (ri_initial + ri_non_initial) if (ri_initial + ri_non_initial) > 0 else 0
pp_initial_rate = pp_initial / (pp_initial + pp_non_initial) if (pp_initial + pp_non_initial) > 0 else 0

print(f"RI tokens:")
print(f"  Line-initial: {ri_initial} ({100*ri_initial_rate:.1f}%)")
print(f"  Non-initial:  {ri_non_initial} ({100*(1-ri_initial_rate):.1f}%)")

print(f"\nPP tokens:")
print(f"  Line-initial: {pp_initial} ({100*pp_initial_rate:.1f}%)")
print(f"  Non-initial:  {pp_non_initial} ({100*(1-pp_initial_rate):.1f}%)")

# Chi-square test
contingency = [[ri_initial, ri_non_initial], [pp_initial, pp_non_initial]]
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-square test:")
print(f"  chi2 = {chi2:.2f}, p = {p_value:.4f}")

enrichment = ri_initial_rate / pp_initial_rate if pp_initial_rate > 0 else float('inf')
print(f"  RI line-initial enrichment: {enrichment:.2f}x vs PP")

if p_value < 0.05 and enrichment > 1.2:
    test1_result = "SUPPORTS"
    print("  -> RI is significantly enriched in line-initial position")
    print("  -> SUPPORTS glossary hypothesis (RI as headwords)")
elif p_value < 0.05 and enrichment < 0.8:
    test1_result = "CONTRADICTS"
    print("  -> RI is depleted in line-initial position")
else:
    test1_result = "NEUTRAL"
    print("  -> No significant difference")

# ============================================================
# TEST 2: PP-TO-B FOLIO MAPPING
# ============================================================
print("\n" + "="*70)
print("TEST 2: PP-TO-B FOLIO MAPPING")
print("="*70)
print("Prediction: If A indexes B, PP in A paragraphs should predict B folios")
print()

# Build A folio PP profiles
a_folio_pp = defaultdict(set)
for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle and m.middle in b_middles:
        a_folio_pp[t.folio].add(m.middle)

# For each A folio, find best-matching B folio
best_matches = []
random_matches = []

b_folios = list(b_folio_middles.keys())

for a_folio, a_pp in a_folio_pp.items():
    if len(a_pp) < 5:
        continue

    # Find B folio with highest Jaccard overlap
    best_jaccard = 0
    best_b_folio = None

    jaccards = []
    for b_folio in b_folios:
        b_vocab = b_folio_middles[b_folio]
        if a_pp and b_vocab:
            jaccard = len(a_pp & b_vocab) / len(a_pp | b_vocab)
            jaccards.append(jaccard)
            if jaccard > best_jaccard:
                best_jaccard = jaccard
                best_b_folio = b_folio

    if jaccards:
        best_matches.append(best_jaccard)
        # Random baseline: mean Jaccard
        random_matches.append(np.mean(jaccards))

print(f"A folios analyzed: {len(best_matches)}")
print(f"\nBest B-folio match (Jaccard):")
print(f"  Mean best match:   {np.mean(best_matches):.3f}")
print(f"  Mean random match: {np.mean(random_matches):.3f}")

if best_matches and random_matches:
    t_stat, p_val = stats.ttest_rel(best_matches, random_matches)
    print(f"\nPaired t-test: t={t_stat:.2f}, p={p_val:.4f}")

    ratio = np.mean(best_matches) / np.mean(random_matches)
    print(f"  Best/random ratio: {ratio:.2f}x")

    if p_val < 0.05 and ratio > 1.5:
        test2_result = "SUPPORTS"
        print("  -> A PP strongly predicts specific B folios")
        print("  -> SUPPORTS glossary hypothesis (A indexes B content)")
    elif p_val < 0.05 and ratio > 1.2:
        test2_result = "WEAK_SUPPORT"
        print("  -> A PP moderately predicts B folios")
    else:
        test2_result = "NEUTRAL"
        print("  -> A PP doesn't strongly predict specific B folios")
else:
    test2_result = "INSUFFICIENT_DATA"

# ============================================================
# TEST 3: LINKER SEMANTIC COHERENCE
# ============================================================
print("\n" + "="*70)
print("TEST 3: LINKER SEMANTIC COHERENCE")
print("="*70)
print("Prediction: If linkers are 'see also', source/dest should share PP")
print()

LINKERS = ['cthody', 'ctho', 'ctheody', 'qokoiiin']
LINKER_DESTINATIONS = ['f93v', 'f32r']  # From C835

# Get PP sets for linker source folios
linker_source_folios = set()
for t in a_tokens:
    if t.word in LINKERS:
        linker_source_folios.add(t.folio)

# Compute Jaccard between source and destination PP
source_dest_jaccards = []
for src in linker_source_folios:
    if src in a_folio_pp:
        for dest in LINKER_DESTINATIONS:
            if dest in a_folio_pp:
                src_pp = a_folio_pp[src]
                dest_pp = a_folio_pp[dest]
                if src_pp and dest_pp:
                    jaccard = len(src_pp & dest_pp) / len(src_pp | dest_pp)
                    source_dest_jaccards.append(jaccard)

# Random baseline: random A folio pairs
a_folios_list = [f for f in a_folio_pp if len(a_folio_pp[f]) >= 5]
random_jaccards = []
np.random.seed(42)
for _ in range(100):
    f1, f2 = np.random.choice(a_folios_list, 2, replace=False)
    pp1 = a_folio_pp[f1]
    pp2 = a_folio_pp[f2]
    if pp1 and pp2:
        jaccard = len(pp1 & pp2) / len(pp1 | pp2)
        random_jaccards.append(jaccard)

print(f"Linker source folios: {len(linker_source_folios)}")
print(f"Source-destination pairs: {len(source_dest_jaccards)}")

if source_dest_jaccards:
    print(f"\nPP Jaccard similarity:")
    print(f"  Linker source-dest: {np.mean(source_dest_jaccards):.3f}")
    print(f"  Random folio pairs: {np.mean(random_jaccards):.3f}")

    # Mann-Whitney U test
    u_stat, p_val = stats.mannwhitneyu(source_dest_jaccards, random_jaccards, alternative='greater')
    print(f"\nMann-Whitney U: p={p_val:.4f}")

    ratio = np.mean(source_dest_jaccards) / np.mean(random_jaccards) if np.mean(random_jaccards) > 0 else float('inf')
    print(f"  Ratio: {ratio:.2f}x")

    if p_val < 0.05 and ratio > 1.3:
        test3_result = "SUPPORTS"
        print("  -> Linker pairs share more PP than random")
        print("  -> SUPPORTS glossary hypothesis (linkers as 'see also')")
    else:
        test3_result = "NEUTRAL"
        print("  -> No significant difference from random")
else:
    test3_result = "INSUFFICIENT_DATA"
    print("  -> Insufficient linker data")

# ============================================================
# TEST 4: ENTRY STRUCTURE CONSISTENCY
# ============================================================
print("\n" + "="*70)
print("TEST 4: ENTRY STRUCTURE CONSISTENCY")
print("="*70)
print("Prediction: If glossary, entries should be: RI first, then PP")
print()

# For each line, check if RI precedes PP
ri_before_pp = 0
pp_before_ri = 0
mixed_lines = 0

# Group tokens by (folio, line)
line_tokens = defaultdict(list)
for t in a_tokens:
    line_tokens[(t.folio, t.line)].append(t)

for key, tokens in line_tokens.items():
    # Classify each token
    classifications = []
    for t in tokens:
        m = morph.extract(t.word)
        if m and m.middle:
            is_ri = m.middle not in b_middles
            classifications.append('RI' if is_ri else 'PP')

    if not classifications:
        continue

    # Check order: does RI come before PP?
    ri_indices = [i for i, c in enumerate(classifications) if c == 'RI']
    pp_indices = [i for i, c in enumerate(classifications) if c == 'PP']

    if ri_indices and pp_indices:
        # Mixed line - check if RI comes first
        if min(ri_indices) < min(pp_indices):
            ri_before_pp += 1
        else:
            pp_before_ri += 1
        mixed_lines += 1

print(f"Lines with both RI and PP: {mixed_lines}")
print(f"  RI before PP: {ri_before_pp} ({100*ri_before_pp/mixed_lines:.1f}%)" if mixed_lines else "")
print(f"  PP before RI: {pp_before_ri} ({100*pp_before_ri/mixed_lines:.1f}%)" if mixed_lines else "")

if mixed_lines > 0:
    # Binomial test: is RI-first significantly more common than 50%?
    binom_result = stats.binomtest(ri_before_pp, mixed_lines, 0.5, alternative='greater')
    p_binom = binom_result.pvalue
    print(f"\nBinomial test (RI-first > 50%): p={p_binom:.4f}")

    if p_binom < 0.05 and ri_before_pp / mixed_lines > 0.6:
        test4_result = "SUPPORTS"
        print("  -> RI significantly precedes PP")
        print("  -> SUPPORTS glossary hypothesis (headword-first structure)")
    else:
        test4_result = "NEUTRAL"
        print("  -> No consistent RI-first pattern")
else:
    test4_result = "INSUFFICIENT_DATA"

# ============================================================
# TEST 5: RI MORPHOLOGICAL DISTINCTIVENESS
# ============================================================
print("\n" + "="*70)
print("TEST 5: RI MORPHOLOGICAL DISTINCTIVENESS")
print("="*70)
print("Prediction: If RI are labels, they might look different than PP")
print()

ri_prefixes = Counter()
pp_prefixes = Counter()
ri_suffixes = Counter()
pp_suffixes = Counter()
ri_lengths = []
pp_lengths = []

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        is_ri = m.middle not in b_middles

        if is_ri:
            if m.prefix:
                ri_prefixes[m.prefix] += 1
            if m.suffix:
                ri_suffixes[m.suffix] += 1
            ri_lengths.append(len(m.middle))
        else:
            if m.prefix:
                pp_prefixes[m.prefix] += 1
            if m.suffix:
                pp_suffixes[m.suffix] += 1
            pp_lengths.append(len(m.middle))

print("PREFIX distribution:")
print(f"{'PREFIX':<10} {'RI%':<10} {'PP%':<10} {'Diff':<10}")
print("-" * 40)

ri_total = sum(ri_prefixes.values())
pp_total = sum(pp_prefixes.values())

key_prefixes = ['qo', 'ch', 'sh', 'da', 'ok', 'ol', 'ct', 'o', 'd', 's']
for prefix in key_prefixes:
    ri_pct = 100 * ri_prefixes.get(prefix, 0) / ri_total if ri_total else 0
    pp_pct = 100 * pp_prefixes.get(prefix, 0) / pp_total if pp_total else 0
    diff = ri_pct - pp_pct
    print(f"{prefix:<10} {ri_pct:>6.1f}%    {pp_pct:>6.1f}%    {diff:>+5.1f}%")

print(f"\nMIDDLE length:")
print(f"  RI mean: {np.mean(ri_lengths):.2f} chars")
print(f"  PP mean: {np.mean(pp_lengths):.2f} chars")

t_len, p_len = stats.ttest_ind(ri_lengths, pp_lengths)
print(f"  t-test: p={p_len:.4f}")

if p_len < 0.05:
    if np.mean(ri_lengths) > np.mean(pp_lengths):
        test5_result = "SUPPORTS"
        print("  -> RI MIDDLEs are significantly longer")
        print("  -> SUPPORTS glossary hypothesis (labels more complex)")
    else:
        test5_result = "PARTIAL"
        print("  -> RI MIDDLEs are significantly shorter")
else:
    test5_result = "NEUTRAL"
    print("  -> No significant length difference")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("GLOSSARY HYPOTHESIS TEST SUMMARY")
print("="*70)

results = {
    'test1_ri_line_initial': test1_result,
    'test2_pp_b_mapping': test2_result,
    'test3_linker_coherence': test3_result,
    'test4_entry_structure': test4_result,
    'test5_morphology': test5_result
}

print(f"""
Test 1 (RI line-initial):     {test1_result}
Test 2 (PP predicts B folio): {test2_result}
Test 3 (Linker coherence):    {test3_result}
Test 4 (RI-first structure):  {test4_result}
Test 5 (RI morphology):       {test5_result}
""")

supports = sum(1 for r in results.values() if r == "SUPPORTS")
contradicts = sum(1 for r in results.values() if r == "CONTRADICTS")
neutral = sum(1 for r in results.values() if r in ["NEUTRAL", "WEAK_SUPPORT", "PARTIAL", "INSUFFICIENT_DATA"])

print(f"Overall: {supports}/5 support, {contradicts}/5 contradict, {neutral}/5 neutral")

if supports >= 3:
    verdict = "SUPPORTED"
    print("\n-> GLOSSARY HYPOTHESIS IS SUPPORTED")
elif supports >= 2 and contradicts == 0:
    verdict = "PARTIALLY_SUPPORTED"
    print("\n-> GLOSSARY HYPOTHESIS IS PARTIALLY SUPPORTED")
elif contradicts >= 2:
    verdict = "CONTRADICTED"
    print("\n-> GLOSSARY HYPOTHESIS IS CONTRADICTED")
else:
    verdict = "INCONCLUSIVE"
    print("\n-> GLOSSARY HYPOTHESIS IS INCONCLUSIVE")

# Save results
output = {
    'hypothesis': 'A is a glossary/index to B',
    'tests': {
        'test1_ri_line_initial': {
            'result': test1_result,
            'ri_initial_rate': ri_initial_rate,
            'pp_initial_rate': pp_initial_rate,
            'enrichment': enrichment
        },
        'test2_pp_b_mapping': {
            'result': test2_result,
            'best_match_mean': float(np.mean(best_matches)) if best_matches else None,
            'random_match_mean': float(np.mean(random_matches)) if random_matches else None
        },
        'test3_linker_coherence': {
            'result': test3_result,
            'source_dest_jaccard': float(np.mean(source_dest_jaccards)) if source_dest_jaccards else None,
            'random_jaccard': float(np.mean(random_jaccards)) if random_jaccards else None
        },
        'test4_entry_structure': {
            'result': test4_result,
            'ri_before_pp': ri_before_pp,
            'pp_before_ri': pp_before_ri
        },
        'test5_morphology': {
            'result': test5_result,
            'ri_mean_length': float(np.mean(ri_lengths)),
            'pp_mean_length': float(np.mean(pp_lengths))
        }
    },
    'summary': {
        'supports': supports,
        'contradicts': contradicts,
        'neutral': neutral,
        'verdict': verdict
    }
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/glossary_hypothesis_test.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to glossary_hypothesis_test.json")
