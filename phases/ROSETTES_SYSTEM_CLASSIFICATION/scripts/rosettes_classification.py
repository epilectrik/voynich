#!/usr/bin/env python3
"""
Phase 387: ROSETTES_SYSTEM_CLASSIFICATION

Determines whether the Rosettes foldout (f85-f86) operates under:
- B grammar (49-class sequential execution)
- AZC positional grammar (placement-coded, orthogonal vocabulary)
- Hybrid regime (mixed system properties)

10-test battery with decision gate. Expert-designed priority ordering.
"""

import sys
import json
import random
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer, BFolioDecoder

# ============================================================
# SETUP: Pre-compute all data structures
# ============================================================
print("=" * 65)
print("Phase 387: ROSETTES_SYSTEM_CLASSIFICATION")
print("=" * 65)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()

# Load 49-class token map
CTM_PATH = ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
with open(CTM_PATH, 'r', encoding='utf-8') as f:
    ctm_data = json.load(f)
token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}

# Forbidden transitions (C109): 17 pairs by MIDDLE
FORBIDDEN_MIDDLE_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('dy', 'chey'), ('chey', 'chedy'),
    ('chey', 'shedy'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('c', 'ee'), ('shedy', 'aiin'),
    ('l', 'chol'), ('ar', 'dal'), ('he', 't'), ('shedy', 'o'),
    ('or', 'dal'),
    ('he', 'or'),
]
FORBIDDEN_SET = set(FORBIDDEN_MIDDLE_PAIRS)

# Pre-build token lists by system
print("\nPre-computing token sets...")

# B corpus (non-Rosettes, H-track)
b_tokens_by_folio = defaultdict(list)
b_all_tokens = []
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        b_tokens_by_folio[tok.folio].append(tok)
        b_all_tokens.append(tok)

# AZC corpus (H-track)
azc_tokens_by_folio = defaultdict(list)
azc_all_tokens = []
for tok in tx.azc():
    azc_tokens_by_folio[tok.folio].append(tok)
    azc_all_tokens.append(tok)

# A corpus (H-track)
a_all_tokens = list(tx.currier_a())

# Rosettes tokens (best track per region)
ros_tokens_by_folio = {}
ros_all_tokens = []
for folio in ra.get_folios():
    toks = ra.get_tokens(folio)
    ros_tokens_by_folio[folio] = toks
    ros_all_tokens.extend(toks)

# Rosettes H-track only folios (for clean comparisons)
ROS_H_FOLIOS = ['f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']
ros_h_tokens = []
for f in ROS_H_FOLIOS:
    ros_h_tokens.extend(ros_tokens_by_folio.get(f, []))

print(f"  B corpus: {len(b_all_tokens)} tokens, {len(b_tokens_by_folio)} folios")
print(f"  AZC corpus: {len(azc_all_tokens)} tokens, {len(azc_tokens_by_folio)} folios")
print(f"  A corpus: {len(a_all_tokens)} tokens")
print(f"  Rosettes: {len(ros_all_tokens)} tokens ({len(ros_h_tokens)} H-track)")
print(f"  f85v2: {len(ros_tokens_by_folio.get('f85v2', []))} tokens (U/V track)")

results = {
    'phase': 387,
    'name': 'ROSETTES_SYSTEM_CLASSIFICATION',
    'test_count': 10,
    'verdicts': {},
}


# ============================================================
# T0: U/V TRACK VALIDATION (PREREQUISITE)
# ============================================================
print("\n" + "=" * 65)
print("T0: U/V TRACK VALIDATION")
print("=" * 65)

# Compare H vs U tracks on folios that have both
t0_results = {}
t0_folios = ['f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']

for folio in t0_folios:
    # Get H and U tokens, grouped by (placement, line)
    h_by_pos = defaultdict(list)
    u_by_pos = defaultdict(list)

    for tok in tx.all(h_only=False):
        if tok.folio != folio or not tok.word.strip() or '*' in tok.word:
            continue
        key = (tok.placement, tok.line)
        if tok.transcriber == 'H':
            h_by_pos[key].append(tok.word)
        elif tok.transcriber == 'U':
            u_by_pos[key].append(tok.word)

    # Compare where both exist
    shared_keys = set(h_by_pos.keys()) & set(u_by_pos.keys())
    exact_match = 0
    total_compared = 0
    morph_match = 0

    for key in shared_keys:
        h_words = h_by_pos[key]
        u_words = u_by_pos[key]
        # Align by position (zip shortest)
        for hw, uw in zip(h_words, u_words):
            total_compared += 1
            if hw == uw:
                exact_match += 1
            # Check morphological agreement
            hm = morph.extract(hw)
            um = morph.extract(uw)
            if (hm.prefix == um.prefix and hm.middle == um.middle
                    and hm.suffix == um.suffix):
                morph_match += 1

    # Vocabulary Jaccard
    h_vocab = set()
    u_vocab = set()
    for words in h_by_pos.values():
        h_vocab.update(words)
    for words in u_by_pos.values():
        u_vocab.update(words)
    vocab_jaccard = (len(h_vocab & u_vocab) / len(h_vocab | u_vocab)
                     if (h_vocab | u_vocab) else 0)

    identity_rate = exact_match / total_compared if total_compared else 0
    morph_rate = morph_match / total_compared if total_compared else 0

    t0_results[folio] = {
        'shared_positions': len(shared_keys),
        'tokens_compared': total_compared,
        'exact_match': exact_match,
        'identity_rate': round(identity_rate, 3),
        'morph_match': morph_match,
        'morph_rate': round(morph_rate, 3),
        'vocab_jaccard': round(vocab_jaccard, 3),
    }
    print(f"  {folio}: {total_compared} compared, "
          f"identity={identity_rate:.1%}, morph={morph_rate:.1%}, "
          f"vocab_J={vocab_jaccard:.3f}")

# Aggregate
total_comp = sum(r['tokens_compared'] for r in t0_results.values())
total_exact = sum(r['exact_match'] for r in t0_results.values())
total_morph = sum(r['morph_match'] for r in t0_results.values())
agg_identity = total_exact / total_comp if total_comp else 0
agg_morph = total_morph / total_comp if total_comp else 0

if agg_identity > 0.85:
    t0_verdict = 'PASS_RELIABLE'
elif agg_identity > 0.70:
    t0_verdict = 'PASS_MARGINAL'
else:
    t0_verdict = 'FAIL_UNRELIABLE'

print(f"\n  Aggregate: identity={agg_identity:.1%}, morph={agg_morph:.1%}")
print(f"  VERDICT: {t0_verdict}")

results['verdicts']['T0_uv_validation'] = t0_verdict
results['T0_data'] = {
    'per_folio': t0_results,
    'aggregate_identity': round(agg_identity, 3),
    'aggregate_morph': round(agg_morph, 3),
}


# ============================================================
# R1.1: 49-CLASS GRAMMAR COVERAGE
# ============================================================
print("\n" + "=" * 65)
print("R1.1: 49-CLASS GRAMMAR COVERAGE")
print("=" * 65)

def grammar_coverage(tokens):
    """Fraction of tokens that map to 49-class system."""
    if not tokens:
        return 0, 0, 0
    mapped = sum(1 for t in tokens if t.word in token_to_class)
    return mapped, len(tokens), mapped / len(tokens) if tokens else 0

# Reference: B corpus
b_mapped, b_total, b_cov = grammar_coverage(b_all_tokens)
print(f"  B corpus:    {b_mapped}/{b_total} = {b_cov:.1%}")

# Reference: AZC corpus
azc_mapped, azc_total, azc_cov = grammar_coverage(azc_all_tokens)
print(f"  AZC corpus:  {azc_mapped}/{azc_total} = {azc_cov:.1%}")

# Reference: A corpus
a_mapped, a_total, a_cov = grammar_coverage(a_all_tokens)
print(f"  A corpus:    {a_mapped}/{a_total} = {a_cov:.1%}")

# Rosettes overall
ros_mapped, ros_total, ros_cov = grammar_coverage(ros_all_tokens)
print(f"  Rosettes:    {ros_mapped}/{ros_total} = {ros_cov:.1%}")

# Rosettes H-track only
rh_mapped, rh_total, rh_cov = grammar_coverage(ros_h_tokens)
print(f"  Ros H-only:  {rh_mapped}/{rh_total} = {rh_cov:.1%}")

# f85v2 separately
v2_toks = ros_tokens_by_folio.get('f85v2', [])
v2_mapped, v2_total, v2_cov = grammar_coverage(v2_toks)
print(f"  f85v2 (U/V): {v2_mapped}/{v2_total} = {v2_cov:.1%}")

# Per Rosettes folio
r11_per_folio = {}
for f in ra.get_folios():
    ftoks = ros_tokens_by_folio.get(f, [])
    m, t, c = grammar_coverage(ftoks)
    r11_per_folio[f] = {'mapped': m, 'total': t, 'coverage': round(c, 3)}
    print(f"    {f}: {m}/{t} = {c:.1%}")

# Classify
if ros_cov > 0.70:
    r11_verdict = 'B_LIKE'
elif ros_cov < 0.30:
    r11_verdict = 'AZC_LIKE'
else:
    r11_verdict = 'INTERMEDIATE'

print(f"\n  VERDICT: {r11_verdict} (Rosettes coverage={ros_cov:.1%})")
results['verdicts']['R1_1_grammar_coverage'] = r11_verdict
results['R1_1_data'] = {
    'b_coverage': round(b_cov, 3),
    'azc_coverage': round(azc_cov, 3),
    'a_coverage': round(a_cov, 3),
    'ros_coverage': round(ros_cov, 3),
    'ros_h_coverage': round(rh_cov, 3),
    'f85v2_coverage': round(v2_cov, 3),
    'per_folio': r11_per_folio,
}


# ============================================================
# R1.2: FORBIDDEN TRANSITION COMPLIANCE
# ============================================================
print("\n" + "=" * 65)
print("R1.2: FORBIDDEN TRANSITION COMPLIANCE")
print("=" * 65)

def middle_bigrams(tokens):
    """Extract MIDDLE bigrams within lines."""
    lines = defaultdict(list)
    for tok in tokens:
        m = morph.extract(tok.word)
        if m.middle:
            lines[(tok.folio, tok.line)].append(m.middle)
    bigrams = []
    for key, middles in lines.items():
        for i in range(len(middles) - 1):
            bigrams.append((middles[i], middles[i+1]))
    return bigrams

def forbidden_rate(bigrams):
    """Fraction of bigrams that are forbidden transitions."""
    if not bigrams:
        return 0, 0, 0
    violations = sum(1 for b in bigrams if b in FORBIDDEN_SET)
    return violations, len(bigrams), violations / len(bigrams) if bigrams else 0

# B corpus reference
b_bigrams = middle_bigrams(b_all_tokens)
b_viol, b_big_total, b_viol_rate = forbidden_rate(b_bigrams)
print(f"  B corpus:    {b_viol}/{b_big_total} violations = {b_viol_rate:.4%}")

# Random baseline (shuffle B middles)
random.seed(42)
b_middles_flat = [morph.extract(t.word).middle for t in b_all_tokens
                  if morph.extract(t.word).middle]
shuffled = b_middles_flat.copy()
random.shuffle(shuffled)
shuffled_bigrams = [(shuffled[i], shuffled[i+1]) for i in range(len(shuffled)-1)]
rand_viol, rand_total, rand_rate = forbidden_rate(shuffled_bigrams)
print(f"  Random:      {rand_viol}/{rand_total} violations = {rand_rate:.4%}")

# Rosettes
ros_bigrams = middle_bigrams(ros_all_tokens)
ros_viol, ros_big_total, ros_viol_rate = forbidden_rate(ros_bigrams)
print(f"  Rosettes:    {ros_viol}/{ros_big_total} violations = {ros_viol_rate:.4%}")

# Rosettes H-track only
rh_bigrams = middle_bigrams(ros_h_tokens)
rh_viol, rh_big_total, rh_viol_rate = forbidden_rate(rh_bigrams)
print(f"  Ros H-only:  {rh_viol}/{rh_big_total} violations = {rh_viol_rate:.4%}")

# f85v2
v2_bigrams = middle_bigrams(v2_toks)
v2_viol, v2_big_total, v2_viol_rate = forbidden_rate(v2_bigrams)
print(f"  f85v2 (U/V): {v2_viol}/{v2_big_total} violations = {v2_viol_rate:.4%}")

# AZC reference
azc_bigrams = middle_bigrams(azc_all_tokens)
azc_viol, azc_big_total, azc_viol_rate = forbidden_rate(azc_bigrams)
print(f"  AZC:         {azc_viol}/{azc_big_total} violations = {azc_viol_rate:.4%}")

if ros_viol_rate < 0.005:
    r12_verdict = 'B_LIKE_COMPLIANT'
elif ros_viol_rate > rand_rate * 0.5:
    r12_verdict = 'NON_B_RANDOM_LIKE'
else:
    r12_verdict = 'INTERMEDIATE'

print(f"\n  VERDICT: {r12_verdict}")
results['verdicts']['R1_2_forbidden_transitions'] = r12_verdict
results['R1_2_data'] = {
    'b_violation_rate': round(b_viol_rate, 6),
    'random_violation_rate': round(rand_rate, 6),
    'ros_violation_rate': round(ros_viol_rate, 6),
    'ros_h_violation_rate': round(rh_viol_rate, 6),
    'f85v2_violation_rate': round(v2_viol_rate, 6),
    'azc_violation_rate': round(azc_viol_rate, 6),
    'ros_violations': ros_viol,
    'ros_bigrams': ros_big_total,
}


# ============================================================
# R1.3: LINK DENSITY
# ============================================================
print("\n" + "=" * 65)
print("R1.3: LINK DENSITY")
print("=" * 65)

LINK_PREFIXES = {'lk', 'lo'}

def link_density(tokens):
    """Fraction of tokens with LINK prefix."""
    if not tokens:
        return 0, 0, 0
    links = sum(1 for t in tokens
                if morph.extract(t.word).prefix in LINK_PREFIXES)
    return links, len(tokens), links / len(tokens) if tokens else 0

b_links, b_lt, b_ld = link_density(b_all_tokens)
print(f"  B corpus:    {b_links}/{b_lt} = {b_ld:.2%}")

azc_links, azc_lt, azc_ld = link_density(azc_all_tokens)
print(f"  AZC corpus:  {azc_links}/{azc_lt} = {azc_ld:.2%}")

a_links, a_lt, a_ld = link_density(a_all_tokens)
print(f"  A corpus:    {a_links}/{a_lt} = {a_ld:.2%}")

ros_links, ros_lt, ros_ld = link_density(ros_all_tokens)
print(f"  Rosettes:    {ros_links}/{ros_lt} = {ros_ld:.2%}")

# Per folio
r13_per_folio = {}
for f in ra.get_folios():
    ftoks = ros_tokens_by_folio.get(f, [])
    fl, ft, fd = link_density(ftoks)
    r13_per_folio[f] = {'links': fl, 'total': ft, 'density': round(fd, 4)}
    print(f"    {f}: {fl}/{ft} = {fd:.2%}")

if ros_ld >= 0.04:
    r13_verdict = 'B_LIKE'
elif ros_ld < 0.01:
    r13_verdict = 'AZC_LIKE'
else:
    r13_verdict = 'INTERMEDIATE'

print(f"\n  VERDICT: {r13_verdict}")
results['verdicts']['R1_3_link_density'] = r13_verdict
results['R1_3_data'] = {
    'b_density': round(b_ld, 4),
    'azc_density': round(azc_ld, 4),
    'a_density': round(a_ld, 4),
    'ros_density': round(ros_ld, 4),
    'per_folio': r13_per_folio,
}


# ============================================================
# R1.4: KERNEL CHARACTER DENSITY
# ============================================================
print("\n" + "=" * 65)
print("R1.4: KERNEL CHARACTER DENSITY")
print("=" * 65)

KERNEL_CHARS = set('khe')

def kernel_density(tokens):
    """Fraction of MIDDLEs containing at least one kernel character."""
    middles_with_kernel = 0
    total_middles = 0
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle:
            total_middles += 1
            if any(c in KERNEL_CHARS for c in m.middle):
                middles_with_kernel += 1
    rate = middles_with_kernel / total_middles if total_middles else 0
    return middles_with_kernel, total_middles, rate

b_kd_n, b_kd_t, b_kd_r = kernel_density(b_all_tokens)
print(f"  B corpus:    {b_kd_n}/{b_kd_t} = {b_kd_r:.1%}")

azc_kd_n, azc_kd_t, azc_kd_r = kernel_density(azc_all_tokens)
print(f"  AZC corpus:  {azc_kd_n}/{azc_kd_t} = {azc_kd_r:.1%}")

a_kd_n, a_kd_t, a_kd_r = kernel_density(a_all_tokens)
print(f"  A corpus:    {a_kd_n}/{a_kd_t} = {a_kd_r:.1%}")

ros_kd_n, ros_kd_t, ros_kd_r = kernel_density(ros_all_tokens)
print(f"  Rosettes:    {ros_kd_n}/{ros_kd_t} = {ros_kd_r:.1%}")

r14_verdict = 'B_LIKE' if ros_kd_r > 0.60 else ('AZC_LIKE' if ros_kd_r < 0.40 else 'INTERMEDIATE')
print(f"\n  VERDICT: {r14_verdict}")
results['verdicts']['R1_4_kernel_density'] = r14_verdict
results['R1_4_data'] = {
    'b_rate': round(b_kd_r, 3),
    'azc_rate': round(azc_kd_r, 3),
    'a_rate': round(a_kd_r, 3),
    'ros_rate': round(ros_kd_r, 3),
}


# ============================================================
# R1.5: PLACEMENT-POSITION VOCABULARY DEPENDENCY (CRITICAL)
# ============================================================
print("\n" + "=" * 65)
print("R1.5: PLACEMENT-POSITION VOCABULARY DEPENDENCY")
print("=" * 65)

def region_jaccard_matrix(folio):
    """Compute pairwise MIDDLE Jaccard between regions on a folio."""
    regions = ra.get_regions(folio)
    region_vocabs = {}
    for r in regions:
        toks = ra.get_tokens(folio, r)
        middles = set()
        for t in toks:
            m = morph.extract(t.word)
            if m.middle:
                middles.add(m.middle)
        if middles:
            region_vocabs[r] = middles

    jaccards = []
    pairs = list(combinations(region_vocabs.keys(), 2))
    for r1, r2 in pairs:
        intersection = len(region_vocabs[r1] & region_vocabs[r2])
        union = len(region_vocabs[r1] | region_vocabs[r2])
        j = intersection / union if union else 0
        jaccards.append(j)

    return {
        'regions': list(region_vocabs.keys()),
        'n_regions': len(region_vocabs),
        'n_pairs': len(pairs),
        'mean_jaccard': sum(jaccards) / len(jaccards) if jaccards else 0,
        'min_jaccard': min(jaccards) if jaccards else 0,
        'max_jaccard': max(jaccards) if jaccards else 0,
    }

# f85v2 (16 regions)
v2_jac = region_jaccard_matrix('f85v2')
print(f"  f85v2: {v2_jac['n_regions']} regions, {v2_jac['n_pairs']} pairs")
print(f"    Mean Jaccard: {v2_jac['mean_jaccard']:.3f}")
print(f"    Range: [{v2_jac['min_jaccard']:.3f}, {v2_jac['max_jaccard']:.3f}]")

# f86v3 (5 regions)
v3_jac = region_jaccard_matrix('f86v3')
print(f"  f86v3: {v3_jac['n_regions']} regions, {v3_jac['n_pairs']} pairs")
print(f"    Mean Jaccard: {v3_jac['mean_jaccard']:.3f}")
print(f"    Range: [{v3_jac['min_jaccard']:.3f}, {v3_jac['max_jaccard']:.3f}]")

# f86v4 (3 regions)
v4_jac = region_jaccard_matrix('f86v4')
print(f"  f86v4: {v4_jac['n_regions']} regions, {v4_jac['n_pairs']} pairs")
print(f"    Mean Jaccard: {v4_jac['mean_jaccard']:.3f}")

# Reference: AZC inter-folio Jaccard (C437 = 0.056)
azc_folio_vocabs = {}
for f, toks in azc_tokens_by_folio.items():
    middles = set()
    for t in toks:
        m = morph.extract(t.word)
        if m.middle:
            middles.add(m.middle)
    if middles:
        azc_folio_vocabs[f] = middles

azc_jaccards = []
for f1, f2 in combinations(azc_folio_vocabs.keys(), 2):
    inter = len(azc_folio_vocabs[f1] & azc_folio_vocabs[f2])
    union = len(azc_folio_vocabs[f1] | azc_folio_vocabs[f2])
    if union:
        azc_jaccards.append(inter / union)

azc_mean_j = sum(azc_jaccards) / len(azc_jaccards) if azc_jaccards else 0
print(f"\n  AZC inter-folio Jaccard (ref): {azc_mean_j:.3f} (C437 expects ~0.056)")

# Reference: B inter-line Jaccard (same folio, sample)
b_sample_folio = 'f107r'
b_line_vocabs = defaultdict(set)
for tok in b_tokens_by_folio.get(b_sample_folio, []):
    m = morph.extract(tok.word)
    if m.middle:
        b_line_vocabs[tok.line].add(m.middle)
b_line_jaccards = []
for l1, l2 in combinations(b_line_vocabs.keys(), 2):
    inter = len(b_line_vocabs[l1] & b_line_vocabs[l2])
    union = len(b_line_vocabs[l1] | b_line_vocabs[l2])
    if union:
        b_line_jaccards.append(inter / union)
b_line_mean_j = sum(b_line_jaccards) / len(b_line_jaccards) if b_line_jaccards else 0
print(f"  B inter-line Jaccard ({b_sample_folio} ref): {b_line_mean_j:.3f}")

# Verdict: AZC-like if close to AZC inter-folio orthogonality
if v2_jac['mean_jaccard'] < 0.10:
    r15_verdict = 'AZC_LIKE_ORTHOGONAL'
elif v2_jac['mean_jaccard'] < 0.20:
    r15_verdict = 'LOW_OVERLAP'
else:
    r15_verdict = 'B_LIKE_SHARED'

print(f"\n  VERDICT: {r15_verdict}")
results['verdicts']['R1_5_position_vocabulary'] = r15_verdict
results['R1_5_data'] = {
    'f85v2': v2_jac,
    'f86v3': v3_jac,
    'f86v4': {k: round(v, 3) if isinstance(v, float) else v for k, v in v4_jac.items()},
    'azc_interfolio_jaccard': round(azc_mean_j, 3),
    'b_interline_jaccard': round(b_line_mean_j, 3),
}


# ============================================================
# R1.6: BIGRAM REUSE RATE
# ============================================================
print("\n" + "=" * 65)
print("R1.6: BIGRAM REUSE RATE")
print("=" * 65)

def bigram_reuse(tokens):
    """Fraction of distinct bigrams appearing 2+ times."""
    lines = defaultdict(list)
    for tok in tokens:
        lines[(tok.folio, tok.line)].append(tok.word)
    bigrams = Counter()
    for words in lines.values():
        for i in range(len(words) - 1):
            bigrams[(words[i], words[i+1])] += 1
    total_unique = len(bigrams)
    reused = sum(1 for c in bigrams.values() if c >= 2)
    return reused, total_unique, reused / total_unique if total_unique else 0

b_br_n, b_br_t, b_br_r = bigram_reuse(b_all_tokens)
print(f"  B corpus:    {b_br_n}/{b_br_t} = {b_br_r:.1%} reused")

azc_br_n, azc_br_t, azc_br_r = bigram_reuse(azc_all_tokens)
print(f"  AZC corpus:  {azc_br_n}/{azc_br_t} = {azc_br_r:.1%} reused")

a_br_n, a_br_t, a_br_r = bigram_reuse(a_all_tokens)
print(f"  A corpus:    {a_br_n}/{a_br_t} = {a_br_r:.1%} reused")

ros_br_n, ros_br_t, ros_br_r = bigram_reuse(ros_all_tokens)
print(f"  Rosettes:    {ros_br_n}/{ros_br_t} = {ros_br_r:.1%} reused")

r16_verdict = 'HIGH_REUSE' if ros_br_r > a_br_r else ('B_LIKE' if ros_br_r > azc_br_r else 'LOW_REUSE')
print(f"\n  VERDICT: {r16_verdict}")
results['verdicts']['R1_6_bigram_reuse'] = r16_verdict
results['R1_6_data'] = {
    'b_reuse_rate': round(b_br_r, 3),
    'azc_reuse_rate': round(azc_br_r, 3),
    'a_reuse_rate': round(a_br_r, 3),
    'ros_reuse_rate': round(ros_br_r, 3),
}


# ============================================================
# R1.7: SEQUENTIAL COHERENCE (AXM SELF-TRANSITION)
# ============================================================
print("\n" + "=" * 65)
print("R1.7: SEQUENTIAL COHERENCE (AXM)")
print("=" * 65)

def axm_self_transition(tokens):
    """Fraction of consecutive pairs sharing the same MIDDLE."""
    lines = defaultdict(list)
    for tok in tokens:
        m = morph.extract(tok.word)
        if m.middle:
            lines[(tok.folio, tok.line)].append(m.middle)
    same = 0
    total = 0
    for middles in lines.values():
        for i in range(len(middles) - 1):
            total += 1
            if middles[i] == middles[i+1]:
                same += 1
    return same, total, same / total if total else 0

b_ax_n, b_ax_t, b_ax_r = axm_self_transition(b_all_tokens)
print(f"  B corpus:    {b_ax_n}/{b_ax_t} = {b_ax_r:.3f}")

azc_ax_n, azc_ax_t, azc_ax_r = axm_self_transition(azc_all_tokens)
print(f"  AZC corpus:  {azc_ax_n}/{azc_ax_t} = {azc_ax_r:.3f}")

a_ax_n, a_ax_t, a_ax_r = axm_self_transition(a_all_tokens)
print(f"  A corpus:    {a_ax_n}/{a_ax_t} = {a_ax_r:.3f}")

ros_ax_n, ros_ax_t, ros_ax_r = axm_self_transition(ros_all_tokens)
print(f"  Rosettes:    {ros_ax_n}/{ros_ax_t} = {ros_ax_r:.3f}")

# Per folio
for f in ra.get_folios():
    ftoks = ros_tokens_by_folio.get(f, [])
    fn, ft, fr = axm_self_transition(ftoks)
    print(f"    {f}: {fr:.3f}")

r17_verdict = 'B_LIKE' if ros_ax_r > 0.05 else ('AZC_LIKE' if ros_ax_r < 0.02 else 'INTERMEDIATE')
print(f"\n  VERDICT: {r17_verdict}")
results['verdicts']['R1_7_sequential_coherence'] = r17_verdict
results['R1_7_data'] = {
    'b_self_transition': round(b_ax_r, 4),
    'azc_self_transition': round(azc_ax_r, 4),
    'a_self_transition': round(a_ax_r, 4),
    'ros_self_transition': round(ros_ax_r, 4),
}


# ============================================================
# R1.8: LINE ATOMICITY TEST
# ============================================================
print("\n" + "=" * 65)
print("R1.8: LINE ATOMICITY TEST")
print("=" * 65)

def interline_overlap(tokens_by_folio, folios_to_test):
    """Mean pairwise MIDDLE Jaccard between lines within folios."""
    all_jaccards = []
    for f in folios_to_test:
        toks = tokens_by_folio.get(f, [])
        if not toks:
            continue
        line_vocabs = defaultdict(set)
        for t in toks:
            m = morph.extract(t.word)
            if m.middle:
                line_vocabs[t.line].add(m.middle)
        # Only lines with 3+ MIDDLEs
        valid_lines = {l: v for l, v in line_vocabs.items() if len(v) >= 3}
        for l1, l2 in combinations(valid_lines.keys(), 2):
            inter = len(valid_lines[l1] & valid_lines[l2])
            union = len(valid_lines[l1] | valid_lines[l2])
            if union:
                all_jaccards.append(inter / union)
    return sum(all_jaccards) / len(all_jaccards) if all_jaccards else 0

# B reference (sample of folios)
b_sample_folios = list(b_tokens_by_folio.keys())[:10]
b_interline = interline_overlap(b_tokens_by_folio, b_sample_folios)
print(f"  B corpus (10 folios): mean inter-line J = {b_interline:.3f}")

# A reference
a_by_folio = defaultdict(list)
for t in a_all_tokens:
    a_by_folio[t.folio].append(t)
a_sample = list(a_by_folio.keys())[:10]
a_interline = interline_overlap(a_by_folio, a_sample)
print(f"  A corpus (10 folios): mean inter-line J = {a_interline:.3f}")

# Rosettes
ros_interline = interline_overlap(ros_tokens_by_folio, ra.get_folios())
print(f"  Rosettes:             mean inter-line J = {ros_interline:.3f}")

# Per folio
for f in ra.get_folios():
    fj = interline_overlap(ros_tokens_by_folio, [f])
    print(f"    {f}: {fj:.3f}")

if ros_interline < a_interline * 1.2:
    r18_verdict = 'A_LIKE_ATOMIC'
elif ros_interline > b_interline * 0.8:
    r18_verdict = 'B_LIKE_SEQUENCED'
else:
    r18_verdict = 'INTERMEDIATE'

print(f"\n  VERDICT: {r18_verdict}")
results['verdicts']['R1_8_line_atomicity'] = r18_verdict
results['R1_8_data'] = {
    'b_interline_jaccard': round(b_interline, 3),
    'a_interline_jaccard': round(a_interline, 3),
    'ros_interline_jaccard': round(ros_interline, 3),
}


# ============================================================
# R1.9: PREFIX RATIO CLASSIFICATION
# ============================================================
print("\n" + "=" * 65)
print("R1.9: PREFIX RATIO (ok+ot)/(qo+ch)")
print("=" * 65)

def prefix_ratio(tokens):
    """Compute (ok+ot) / (qo+ch) ratio."""
    counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            counts[m.prefix] += 1
    ok_ot = counts.get('ok', 0) + counts.get('ot', 0)
    qo_ch = counts.get('qo', 0) + counts.get('ch', 0)
    ratio = ok_ot / qo_ch if qo_ch else float('inf')
    return ok_ot, qo_ch, ratio

b_ok, b_qo, b_ratio = prefix_ratio(b_all_tokens)
print(f"  B corpus:    ok+ot={b_ok}, qo+ch={b_qo}, ratio={b_ratio:.3f}")

azc_ok, azc_qo, azc_ratio = prefix_ratio(azc_all_tokens)
print(f"  AZC corpus:  ok+ot={azc_ok}, qo+ch={azc_qo}, ratio={azc_ratio:.3f}")

a_ok, a_qo, a_ratio = prefix_ratio(a_all_tokens)
print(f"  A corpus:    ok+ot={a_ok}, qo+ch={a_qo}, ratio={a_ratio:.3f}")

ros_ok, ros_qo, ros_ratio = prefix_ratio(ros_all_tokens)
print(f"  Rosettes:    ok+ot={ros_ok}, qo+ch={ros_qo}, ratio={ros_ratio:.3f}")

# Per folio
for f in ra.get_folios():
    ftoks = ros_tokens_by_folio.get(f, [])
    fok, fqo, fr = prefix_ratio(ftoks)
    print(f"    {f}: ok+ot={fok}, qo+ch={fqo}, ratio={fr:.3f}")

if ros_ratio > 1.0:
    r19_verdict = 'AZC_LIKE'
elif ros_ratio < 0.5:
    r19_verdict = 'B_LIKE'
else:
    r19_verdict = 'INTERMEDIATE'

print(f"\n  VERDICT: {r19_verdict}")
results['verdicts']['R1_9_prefix_ratio'] = r19_verdict
results['R1_9_data'] = {
    'b_ratio': round(b_ratio, 3),
    'azc_ratio': round(azc_ratio, 3),
    'a_ratio': round(a_ratio, 3),
    'ros_ratio': round(ros_ratio, 3),
}


# ============================================================
# R1.10: RI VOCABULARY TEST
# ============================================================
print("\n" + "=" * 65)
print("R1.10: RI VOCABULARY TEST (18 A-not-B MIDDLEs)")
print("=" * 65)

# Pre-compute A and B MIDDLE sets
a_middles = set()
for t in a_all_tokens:
    m = morph.extract(t.word)
    if m.middle:
        a_middles.add(m.middle)

b_middles = set()
for t in b_all_tokens:
    m = morph.extract(t.word)
    if m.middle:
        b_middles.add(m.middle)

ros_middles = set()
for t in ros_all_tokens:
    m = morph.extract(t.word)
    if m.middle:
        ros_middles.add(m.middle)

a_not_b = sorted(ros_middles & a_middles - b_middles)
print(f"  A-not-B MIDDLEs in Rosettes: {len(a_not_b)}")
print(f"    {a_not_b}")

# C498 RI characterization: length, suffix rate, ct-prefix enrichment
if a_not_b:
    lengths = [len(m) for m in a_not_b]
    mean_len = sum(lengths) / len(lengths)
    print(f"\n  Mean MIDDLE length: {mean_len:.2f} (C498 RI prediction: ~4.82)")

    # Check suffix status for tokens containing these MIDDLEs
    suffix_less = 0
    total_checked = 0
    ct_prefix = 0
    for t in ros_all_tokens:
        m = morph.extract(t.word)
        if m.middle in a_not_b:
            total_checked += 1
            if not m.suffix:
                suffix_less += 1
            if m.prefix == 'ct':
                ct_prefix += 1

    suffix_less_rate = suffix_less / total_checked if total_checked else 0
    ct_rate = ct_prefix / total_checked if total_checked else 0
    print(f"  Suffix-less rate: {suffix_less_rate:.1%} (C498: RI has 3x enrichment)")
    print(f"  ct-prefix rate: {ct_rate:.1%} (C498: RI has 5.1x enrichment)")

    # Also check: are these MIDDLEs long and compound-like?
    compound_count = 0
    for mid in a_not_b:
        # Simple compound check: contains known core MIDDLEs
        core_shorts = {'od', 'al', 'ar', 'aiin', 'or', 'dy', 'ol', 'ey',
                       'y', 'r', 'l', 'e', 'd', 'k', 'h'}
        contained = [c for c in core_shorts if c in mid and c != mid]
        if len(contained) >= 2:
            compound_count += 1
    compound_rate = compound_count / len(a_not_b) if a_not_b else 0
    print(f"  Compound rate: {compound_rate:.1%}")

    r110_verdict = 'RI_CONFIRMED' if mean_len > 3.5 and suffix_less_rate > 0.3 else 'RI_INCONCLUSIVE'
else:
    r110_verdict = 'NO_A_NOT_B'
    mean_len = 0
    suffix_less_rate = 0
    ct_rate = 0

print(f"\n  VERDICT: {r110_verdict}")
results['verdicts']['R1_10_ri_vocabulary'] = r110_verdict
results['R1_10_data'] = {
    'a_not_b_middles': a_not_b,
    'count': len(a_not_b),
    'mean_length': round(mean_len, 2) if a_not_b else None,
    'suffix_less_rate': round(suffix_less_rate, 3) if a_not_b else None,
    'ct_prefix_rate': round(ct_rate, 3) if a_not_b else None,
}


# ============================================================
# OVERALL CLASSIFICATION
# ============================================================
print("\n" + "=" * 65)
print("OVERALL CLASSIFICATION")
print("=" * 65)

verdicts = results['verdicts']

# Count B-like vs AZC-like signals
b_signals = sum(1 for v in verdicts.values()
                if 'B_LIKE' in v or 'B_LIKE' in str(v))
azc_signals = sum(1 for v in verdicts.values()
                  if 'AZC_LIKE' in v or 'AZC_LIKE' in str(v))
intermediate_signals = sum(1 for v in verdicts.values()
                           if 'INTERMEDIATE' in v)

print(f"\n  Signal summary:")
print(f"    B-like signals:     {b_signals}")
print(f"    AZC-like signals:   {azc_signals}")
print(f"    Intermediate:       {intermediate_signals}")

# Decision gate
grammar_ok = 'B_LIKE' in verdicts.get('R1_1_grammar_coverage', '')
forbidden_ok = 'COMPLIANT' in verdicts.get('R1_2_forbidden_transitions', '')
position_azc = 'AZC' in verdicts.get('R1_5_position_vocabulary', '') or 'LOW' in verdicts.get('R1_5_position_vocabulary', '')
link_azc = 'AZC' in verdicts.get('R1_3_link_density', '')
prefix_azc = 'AZC' in verdicts.get('R1_9_prefix_ratio', '')

if grammar_ok and forbidden_ok:
    overall = 'B_FAMILY'
elif position_azc and link_azc and prefix_azc:
    overall = 'AZC_FAMILY'
elif b_signals > azc_signals + intermediate_signals:
    overall = 'B_FAMILY_PROBABLE'
elif azc_signals > b_signals + intermediate_signals:
    overall = 'AZC_FAMILY_PROBABLE'
else:
    overall = 'HYBRID'

print(f"\n  OVERALL CLASSIFICATION: {overall}")
print(f"\n  Decision gate:")
if overall.startswith('B'):
    print("    => Phase 388B: B grammar deep validation")
elif overall.startswith('AZC'):
    print("    => Phase 388A: AZC characterization")
else:
    print("    => Phase 388H: Hybrid per-region system mapping")

results['overall'] = overall
results['signal_summary'] = {
    'b_signals': b_signals,
    'azc_signals': azc_signals,
    'intermediate_signals': intermediate_signals,
}

# Print all verdicts
print("\n  All verdicts:")
for test, verdict in sorted(verdicts.items()):
    print(f"    {test}: {verdict}")


# ============================================================
# SAVE RESULTS
# ============================================================
output_path = ROOT / 'phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_classification_results.json'

# Round floats in nested dicts for JSON
def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    return obj

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2)

print(f"\nResults saved to {output_path}")
