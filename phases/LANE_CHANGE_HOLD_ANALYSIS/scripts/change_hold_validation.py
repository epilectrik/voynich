#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANE_CHANGE_HOLD_ANALYSIS - Script 2: Change/Hold Validation

Tests 5 predictions of the Change/Hold interpretation:
1. Kernel primitive co-occurrence (QO->e, CHSH->k/h)
2. Transition stability (QO more stable contexts)
3. Recovery/escape routing (QO dominates)
4. Hazard proximity (CHSH closer to hazard tokens)
5. Hysteresis oscillation (alternation > chance, short runs)

All tests use B-side token data.
"""

import json
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from math import log2

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("SECTION 1: Load & Prepare")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

# Apply class 17 correction: AX -> CC per BCSC v1.4 (C560/C581)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # Correction
token_to_role = {}
for t, c in token_to_class.items():
    token_to_role[t] = class_to_role.get(c, 'UNKNOWN')

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

# CC classes for kernel detection (10, 11, 12, 17)
CC_CLASSES = {10, 11, 12, 17}
# Hazard classes (FL_HAZ)
HAZ_CLASSES = {7, 30}

# Load transcript
tx = Transcript()
morph = Morphology()

# Build line-organized B token data
print("Building line-organized B token data...")
lines = defaultdict(list)  # (folio, line) -> [token_info, ...]

for token in tx.currier_b():
    cls = token_to_class.get(token.word)
    role = token_to_role.get(token.word, 'UNKNOWN')
    m = morph.extract(token.word)

    # Classify EN subfamily by prefix
    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'
        # Minor class (41) or ambiguous — skip

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    is_en = cls in all_en_classes if cls is not None else False

    lines[(token.folio, token.line)].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'prefix': m.prefix,
        'middle': m.middle,
        'en_subfamily': en_subfamily,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'is_en': is_en,
        'section': token.section,
        'line_final': token.line_final,
    })

n_lines = len(lines)
n_en_tokens = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] is not None)
n_qo = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] == 'QO')
n_chsh = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] == 'CHSH')

print(f"B lines: {n_lines}")
print(f"EN tokens with subfamily: {n_en_tokens} (QO: {n_qo}, CHSH: {n_chsh})")

# Identify kernel type for CC tokens
# CC classes: 10=k-kernel, 11=h-kernel, 12=e-kernel, 17=mixed
# Note: class 12 may be rare/absent. Kernel primitives k,h,e also appear
# as CHARACTER-LEVEL features within token MIDDLEs (C521).
KERNEL_MAP = {10: 'k', 11: 'h', 12: 'e', 17: 'k'}  # class 17 is k-dominant per BCSC

# ============================================================
# SECTION 2: Kernel Primitive Co-occurrence
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Kernel Primitive Co-occurrence")
print("=" * 60)

# TEST A: Nearest CC token kernel type
kernel_co = {'QO': Counter(), 'CHSH': Counter()}
kernel_distances = {'QO': [], 'CHSH': []}

for (folio, line_num), toks in lines.items():
    en_positions = [(i, t['en_subfamily']) for i, t in enumerate(toks)
                     if t['en_subfamily'] is not None]
    cc_positions = [(i, KERNEL_MAP.get(t['class'], '?')) for i, t in enumerate(toks)
                     if t['is_cc']]

    if not en_positions or not cc_positions:
        continue

    for en_pos, subfamily in en_positions:
        min_dist = float('inf')
        nearest_kernel = None
        for cc_pos, kernel_type in cc_positions:
            dist = abs(en_pos - cc_pos)
            if dist < min_dist:
                min_dist = dist
                nearest_kernel = kernel_type

        if nearest_kernel is not None and nearest_kernel != '?':
            kernel_co[subfamily][nearest_kernel] += 1
            kernel_distances[subfamily].append(min_dist)

print("Test A - Nearest CC token kernel type:")
for sf in ['QO', 'CHSH']:
    total = sum(kernel_co[sf].values())
    print(f"  {sf}: ", end="")
    for k_type in ['k', 'h', 'e']:
        count = kernel_co[sf][k_type]
        pct = count / total * 100 if total > 0 else 0
        print(f"{k_type}={count} ({pct:.1f}%) ", end="")
    print(f"  total={total}")

# Chi-squared on non-zero columns only
kernel_types_present = [k for k in ['k', 'h', 'e']
                        if kernel_co['QO'][k] + kernel_co['CHSH'][k] > 0]
if len(kernel_types_present) >= 2:
    contingency_kernel = np.array([
        [kernel_co['QO'][k] for k in kernel_types_present],
        [kernel_co['CHSH'][k] for k in kernel_types_present],
    ])
    try:
        chi2_kernel, p_kernel, dof_kernel, _ = stats.chi2_contingency(contingency_kernel)
        total_kernel = contingency_kernel.sum()
        v_kernel = float(np.sqrt(chi2_kernel / (total_kernel * (min(contingency_kernel.shape) - 1))))
        print(f"Chi2 ({'/'.join(kernel_types_present)})={chi2_kernel:.3f}, p={p_kernel:.6f}, V={v_kernel:.4f}")
    except ValueError as e:
        chi2_kernel, p_kernel, v_kernel = float('nan'), float('nan'), float('nan')
        print(f"Chi2 test failed: {e}")
else:
    chi2_kernel, p_kernel, v_kernel = float('nan'), float('nan'), float('nan')
    print("Fewer than 2 kernel types present in CC tokens")

for sf in ['QO', 'CHSH']:
    dists = kernel_distances[sf]
    if dists:
        print(f"  {sf} mean CC distance: {np.mean(dists):.2f} (median: {np.median(dists):.1f})")

# TEST B: Kernel character content WITHIN EN token MIDDLEs (C521)
# Kernel primitives k, h, e appear as characters within MIDDLEs
print("\nTest B - Kernel characters within EN token MIDDLEs:")
en_kernel_content = {'QO': Counter(), 'CHSH': Counter()}

for (folio, line_num), toks in lines.items():
    for t in toks:
        if t['en_subfamily'] is None or t['middle'] is None:
            continue
        mid = t['middle']
        has_k = 'k' in mid
        has_h = 'h' in mid
        has_e = 'e' in mid
        sf = t['en_subfamily']
        if has_k:
            en_kernel_content[sf]['k'] += 1
        if has_h:
            en_kernel_content[sf]['h'] += 1
        if has_e:
            en_kernel_content[sf]['e'] += 1

for sf in ['QO', 'CHSH']:
    total_sf = n_qo if sf == 'QO' else n_chsh
    print(f"  {sf} (n={total_sf}): ", end="")
    for k_type in ['k', 'h', 'e']:
        count = en_kernel_content[sf][k_type]
        pct = count / total_sf * 100 if total_sf > 0 else 0
        print(f"{k_type}={count} ({pct:.1f}%) ", end="")
    print()

# Chi-squared on MIDDLE kernel content
content_types = ['k', 'h', 'e']
contingency_content = np.array([
    [en_kernel_content['QO'][k] for k in content_types],
    [en_kernel_content['CHSH'][k] for k in content_types],
])
try:
    chi2_content, p_content, _, _ = stats.chi2_contingency(contingency_content)
    total_content = contingency_content.sum()
    v_content = float(np.sqrt(chi2_content / (total_content * (min(contingency_content.shape) - 1))))
    print(f"Chi2 (MIDDLE content)={chi2_content:.3f}, p={p_content:.6f}, V={v_content:.4f}")
except ValueError as e:
    chi2_content, p_content, v_content = float('nan'), float('nan'), float('nan')
    print(f"Chi2 test failed: {e}")

# Prediction check (revised): QO MIDDLEs should have more 'e' character content
qo_e_pct = en_kernel_content['QO']['e'] / max(n_qo, 1)
chsh_e_pct = en_kernel_content['CHSH']['e'] / max(n_chsh, 1)
qo_k_pct = en_kernel_content['QO']['k'] / max(n_qo, 1)
chsh_k_pct = en_kernel_content['CHSH']['k'] / max(n_chsh, 1)

# Original prediction: QO->more e. But also check k distribution
kernel_prediction = "CONFIRMED" if qo_e_pct > chsh_e_pct else "REJECTED"
print(f"\nPrediction (QO -> more e): QO e%={qo_e_pct:.3f}, CHSH e%={chsh_e_pct:.3f} -> {kernel_prediction}")
print(f"  Additional: QO k%={qo_k_pct:.3f}, CHSH k%={chsh_k_pct:.3f}")

# ============================================================
# SECTION 3: Transition Stability
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Transition Stability")
print("=" * 60)

# For each EN token, check if surrounding context changes class
stability_scores = {'QO': [], 'CHSH': []}
prev_role_next_role = {'QO': [], 'CHSH': []}

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue

        # Get prev and next roles
        prev_role = toks[i - 1]['role'] if i > 0 else None
        next_role = toks[i + 1]['role'] if i < len(toks) - 1 else None

        if prev_role and next_role:
            # Context stability: 1 if prev_role == next_role (stable), 0 if different
            stable = 1 if prev_role == next_role else 0
            stability_scores[t['en_subfamily']].append(stable)
            prev_role_next_role[t['en_subfamily']].append((prev_role, next_role))

# Compare stability
for sf in ['QO', 'CHSH']:
    scores = stability_scores[sf]
    if scores:
        print(f"  {sf}: mean stability={np.mean(scores):.4f}, n={len(scores)}")

if stability_scores['QO'] and stability_scores['CHSH']:
    u_stab, p_stab = stats.mannwhitneyu(
        stability_scores['QO'], stability_scores['CHSH'], alternative='two-sided'
    )
    n1, n2 = len(stability_scores['QO']), len(stability_scores['CHSH'])
    r_rb_stab = 1 - (2 * u_stab) / (n1 * n2) if n1 > 0 and n2 > 0 else 0

    stab_prediction = "CONFIRMED" if np.mean(stability_scores['QO']) > np.mean(stability_scores['CHSH']) else "REJECTED"
    print(f"Mann-Whitney U: p={p_stab:.6f}, rank-biserial r={r_rb_stab:.4f}")
    print(f"Prediction (QO more stable): {stab_prediction}")
else:
    p_stab, r_rb_stab = float('nan'), float('nan')
    stab_prediction = "INSUFFICIENT_DATA"

# Transition entropy per subfamily
def compute_entropy(pairs):
    """Compute entropy of (prev_role, next_role) distribution."""
    counts = Counter(pairs)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * log2(p)
    return entropy

qo_entropy = compute_entropy(prev_role_next_role['QO'])
chsh_entropy = compute_entropy(prev_role_next_role['CHSH'])
print(f"\nTransition entropy: QO={qo_entropy:.3f}, CHSH={chsh_entropy:.3f}")
entropy_prediction = "CONFIRMED" if qo_entropy < chsh_entropy else "REJECTED"
print(f"Prediction (QO lower entropy): {entropy_prediction}")

# ============================================================
# SECTION 4: Recovery/Escape Routing
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Recovery/Escape Routing")
print("=" * 60)

# For each hazard-class token, find the next EN token
post_hazard_en = {'QO': 0, 'CHSH': 0}
total_post_hazard = 0

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if not t['is_haz']:
            continue
        # Find next EN token
        for j in range(i + 1, len(toks)):
            if toks[j]['en_subfamily'] is not None:
                post_hazard_en[toks[j]['en_subfamily']] += 1
                total_post_hazard += 1
                break

total_ph = post_hazard_en['QO'] + post_hazard_en['CHSH']
if total_ph > 0:
    qo_escape_rate = post_hazard_en['QO'] / total_ph
    print(f"Post-hazard EN routing: QO={post_hazard_en['QO']} ({qo_escape_rate:.3f}), "
          f"CHSH={post_hazard_en['CHSH']} ({1-qo_escape_rate:.3f})")

    # Compare to base rate
    base_qo_rate = n_qo / (n_qo + n_chsh) if (n_qo + n_chsh) > 0 else 0
    print(f"Base QO rate: {base_qo_rate:.3f}")
    enrichment = qo_escape_rate / base_qo_rate if base_qo_rate > 0 else float('inf')
    print(f"QO escape enrichment: {enrichment:.2f}x")

    # Binomial test: is QO escape rate > base rate?
    binom_p = stats.binomtest(post_hazard_en['QO'], total_ph, base_qo_rate, alternative='greater').pvalue
    print(f"Binomial test (QO > base): p={binom_p:.6f}")
    escape_prediction = "CONFIRMED" if qo_escape_rate > base_qo_rate and binom_p < 0.05 else "REJECTED"
else:
    qo_escape_rate = float('nan')
    binom_p = float('nan')
    enrichment = float('nan')
    escape_prediction = "INSUFFICIENT_DATA"
    print("No post-hazard EN tokens found")

print(f"Prediction (QO dominates escape): {escape_prediction}")

# Convergent lines: QO proportion
# Check last token class — STATE-C is terminal convergence
# STATE-C corresponds to specific convergent classes; use role = terminal
# For simplicity: check lines where last token is in a convergent pattern
convergent_en = {'QO': 0, 'CHSH': 0}
non_convergent_en = {'QO': 0, 'CHSH': 0}

for (folio, line_num), toks in lines.items():
    if not toks:
        continue
    # Check if line-final token has specific convergent role
    last_tok = toks[-1]
    is_convergent = last_tok['line_final'] and last_tok['role'] in ('AUXILIARY', 'FREQUENT_OPERATOR')

    for t in toks:
        if t['en_subfamily'] is not None:
            if is_convergent:
                convergent_en[t['en_subfamily']] += 1
            else:
                non_convergent_en[t['en_subfamily']] += 1

total_conv = convergent_en['QO'] + convergent_en['CHSH']
total_nonconv = non_convergent_en['QO'] + non_convergent_en['CHSH']
if total_conv > 0 and total_nonconv > 0:
    qo_conv_rate = convergent_en['QO'] / total_conv
    qo_nonconv_rate = non_convergent_en['QO'] / total_nonconv
    print(f"\nConvergent lines: QO rate={qo_conv_rate:.3f} (n={total_conv})")
    print(f"Non-convergent lines: QO rate={qo_nonconv_rate:.3f} (n={total_nonconv})")

    # Fisher's exact
    table_conv = [
        [convergent_en['QO'], convergent_en['CHSH']],
        [non_convergent_en['QO'], non_convergent_en['CHSH']]
    ]
    _, fisher_p_conv = stats.fisher_exact(table_conv)
    print(f"Fisher's exact p={fisher_p_conv:.6f}")

# ============================================================
# SECTION 5: Hazard Proximity
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Hazard Proximity")
print("=" * 60)

# For each EN token, compute minimum distance to hazard token in same line
proximity = {'QO': [], 'CHSH': []}

for (folio, line_num), toks in lines.items():
    haz_positions = [i for i, t in enumerate(toks) if t['is_haz']]
    if not haz_positions:
        continue  # Only include lines WITH hazard tokens

    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue
        min_dist = min(abs(i - hp) for hp in haz_positions)
        proximity[t['en_subfamily']].append(min_dist)

for sf in ['QO', 'CHSH']:
    if proximity[sf]:
        print(f"  {sf}: mean proximity={np.mean(proximity[sf]):.2f}, "
              f"median={np.median(proximity[sf]):.1f}, n={len(proximity[sf])}")

if proximity['QO'] and proximity['CHSH']:
    u_prox, p_prox = stats.mannwhitneyu(
        proximity['CHSH'], proximity['QO'], alternative='less'
    )
    n1, n2 = len(proximity['CHSH']), len(proximity['QO'])
    r_rb_prox = 1 - (2 * u_prox) / (n1 * n2) if n1 > 0 and n2 > 0 else 0

    prox_prediction = "CONFIRMED" if np.mean(proximity['CHSH']) < np.mean(proximity['QO']) else "REJECTED"
    print(f"Mann-Whitney (CHSH closer): p={p_prox:.6f}, r={r_rb_prox:.4f}")
    print(f"Prediction (CHSH closer to hazard): {prox_prediction}")

    # Fraction within distance <= 2
    qo_near = sum(1 for d in proximity['QO'] if d <= 2) / len(proximity['QO']) if proximity['QO'] else 0
    chsh_near = sum(1 for d in proximity['CHSH'] if d <= 2) / len(proximity['CHSH']) if proximity['CHSH'] else 0
    print(f"Within 2 tokens: QO={qo_near:.3f}, CHSH={chsh_near:.3f}")
else:
    p_prox, r_rb_prox = float('nan'), float('nan')
    prox_prediction = "INSUFFICIENT_DATA"

# ============================================================
# SECTION 6: Hysteresis Oscillation Test
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Hysteresis Oscillation Test")
print("=" * 60)

MIN_EN_PER_LINE = 4
N_PERMS = 10000

# Collect EN sequences per line
en_sequences = []
line_sections = []

for (folio, line_num), toks in lines.items():
    seq = [t['en_subfamily'] for t in toks if t['en_subfamily'] is not None]
    if len(seq) >= MIN_EN_PER_LINE:
        en_sequences.append(seq)
        line_sections.append(toks[0]['section'])

print(f"Lines with >= {MIN_EN_PER_LINE} EN tokens: {len(en_sequences)}")

# Compute observed alternation rate
def compute_alternation(sequences):
    """Fraction of adjacent EN pairs that switch lanes."""
    total_pairs = 0
    alternations = 0
    for seq in sequences:
        for i in range(len(seq) - 1):
            total_pairs += 1
            if seq[i] != seq[i + 1]:
                alternations += 1
    return alternations / total_pairs if total_pairs > 0 else 0, total_pairs

obs_alt_rate, obs_pairs = compute_alternation(en_sequences)
print(f"Observed alternation rate: {obs_alt_rate:.4f} ({obs_pairs} pairs)")

# Run length distribution
run_lengths = {'QO': [], 'CHSH': []}
for seq in en_sequences:
    current = seq[0]
    run_len = 1
    for i in range(1, len(seq)):
        if seq[i] == current:
            run_len += 1
        else:
            run_lengths[current].append(run_len)
            current = seq[i]
            run_len = 1
    run_lengths[current].append(run_len)

for sf in ['QO', 'CHSH']:
    if run_lengths[sf]:
        print(f"  {sf} run lengths: mean={np.mean(run_lengths[sf]):.2f}, "
              f"median={np.median(run_lengths[sf]):.1f}, max={max(run_lengths[sf])}")

# Transition matrix
trans = {'QO->QO': 0, 'QO->CHSH': 0, 'CHSH->QO': 0, 'CHSH->CHSH': 0}
for seq in en_sequences:
    for i in range(len(seq) - 1):
        key = f"{seq[i]}->{seq[i+1]}"
        trans[key] += 1

total_from_qo = trans['QO->QO'] + trans['QO->CHSH']
total_from_chsh = trans['CHSH->QO'] + trans['CHSH->CHSH']
if total_from_qo > 0:
    print(f"\nTransitions from QO:  ->QO={trans['QO->QO']} ({trans['QO->QO']/total_from_qo:.3f}), "
          f"->CHSH={trans['QO->CHSH']} ({trans['QO->CHSH']/total_from_qo:.3f})")
if total_from_chsh > 0:
    print(f"Transitions from CHSH: ->QO={trans['CHSH->QO']} ({trans['CHSH->QO']/total_from_chsh:.3f}), "
          f"->CHSH={trans['CHSH->CHSH']} ({trans['CHSH->CHSH']/total_from_chsh:.3f})")

# Permutation test: shuffle labels within each line, recompute alternation
print(f"\nRunning {N_PERMS} permutations...")
rng = np.random.default_rng(42)
perm_alt_rates = []

for perm_i in range(N_PERMS):
    shuffled_seqs = [list(rng.permutation(seq)) for seq in en_sequences]
    perm_rate, _ = compute_alternation(shuffled_seqs)
    perm_alt_rates.append(perm_rate)
    if (perm_i + 1) % 2000 == 0:
        print(f"  Permutation {perm_i + 1}/{N_PERMS}...")

perm_array = np.array(perm_alt_rates)
# Two-sided: is observed different from null?
perm_p_alt = float(np.mean(np.abs(perm_array - perm_array.mean()) >= abs(obs_alt_rate - perm_array.mean())))

print(f"\nPermutation results:")
print(f"  Observed alternation: {obs_alt_rate:.4f}")
print(f"  Null mean: {perm_array.mean():.4f} (std: {perm_array.std():.4f})")
print(f"  Empirical p (two-sided): {perm_p_alt:.4f}")

# Direction check
if obs_alt_rate > perm_array.mean():
    alt_direction = "ELEVATED (more alternation than chance = hysteresis)"
    hysteresis_prediction = "CONFIRMED"
elif obs_alt_rate < perm_array.mean():
    alt_direction = "DEPLETED (less alternation than chance = lane runs)"
    hysteresis_prediction = "REJECTED"
else:
    alt_direction = "AT_CHANCE"
    hysteresis_prediction = "REJECTED"

print(f"  Direction: {alt_direction}")
print(f"  Prediction (alternation > chance): {hysteresis_prediction}")

# Section stratification
section_alt = defaultdict(lambda: {'pairs': 0, 'alternations': 0})
for seq, sec in zip(en_sequences, line_sections):
    for i in range(len(seq) - 1):
        section_alt[sec]['pairs'] += 1
        if seq[i] != seq[i + 1]:
            section_alt[sec]['alternations'] += 1

print(f"\nAlternation by section:")
for sec in sorted(section_alt.keys()):
    d = section_alt[sec]
    rate = d['alternations'] / d['pairs'] if d['pairs'] > 0 else 0
    print(f"  {sec}: {rate:.4f} ({d['pairs']} pairs)")

# ============================================================
# SECTION 7: Summary & Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Summary & Verdict")
print("=" * 60)

scorecard = [
    {
        'test': 'Kernel co-occurrence',
        'prediction': 'QO->more e, CHSH->more k/h',
        'result': kernel_prediction,
        'detail': f"QO e%={qo_e_pct:.3f}, CHSH e%={chsh_e_pct:.3f}, chi2 p={p_kernel:.6f}",
    },
    {
        'test': 'Transition stability',
        'prediction': 'QO more stable contexts',
        'result': stab_prediction,
        'detail': f"QO mean={np.mean(stability_scores['QO']):.4f}, "
                  f"CHSH mean={np.mean(stability_scores['CHSH']):.4f}, p={p_stab:.6f}"
                  if stability_scores['QO'] and stability_scores['CHSH'] else "insufficient data",
    },
    {
        'test': 'Recovery/escape routing',
        'prediction': 'QO dominates post-hazard',
        'result': escape_prediction,
        'detail': f"QO escape rate={qo_escape_rate:.3f}, base={base_qo_rate:.3f}, "
                  f"enrichment={enrichment:.2f}x" if total_ph > 0 else "insufficient data",
    },
    {
        'test': 'Hazard proximity',
        'prediction': 'CHSH closer to hazard tokens',
        'result': prox_prediction,
        'detail': f"CHSH mean={np.mean(proximity['CHSH']):.2f}, "
                  f"QO mean={np.mean(proximity['QO']):.2f}, p={p_prox:.6f}"
                  if proximity['QO'] and proximity['CHSH'] else "insufficient data",
    },
    {
        'test': 'Hysteresis oscillation',
        'prediction': 'Alternation > chance, short runs',
        'result': hysteresis_prediction,
        'detail': f"observed={obs_alt_rate:.4f}, null={perm_array.mean():.4f}, "
                  f"p={perm_p_alt:.4f}, direction={alt_direction}",
    },
]

confirmed = sum(1 for s in scorecard if s['result'] == 'CONFIRMED')
total_tests = len(scorecard)

print(f"\nSCORECARD: {confirmed}/{total_tests} predictions confirmed")
print(f"{'Test':<30} {'Prediction':<35} {'Result':<12}")
print("-" * 77)
for s in scorecard:
    print(f"{s['test']:<30} {s['prediction']:<35} {s['result']:<12}")
    print(f"  -> {s['detail']}")

if confirmed >= 5:
    verdict = "STRONG"
elif confirmed >= 3:
    verdict = "MODERATE"
else:
    verdict = "WEAK"

print(f"\nOVERALL VERDICT: {verdict}")
print(f"Change/Hold interpretation is {'well-supported' if verdict == 'STRONG' else 'plausible with caveats' if verdict == 'MODERATE' else 'needs revision'}.")

# Save results
results = {
    'preparation': {
        'n_lines': n_lines,
        'n_en_tokens': n_en_tokens,
        'n_qo': n_qo,
        'n_chsh': n_chsh,
    },
    'kernel_cooccurrence': {
        'counts': {sf: dict(kernel_co[sf]) for sf in ['QO', 'CHSH']},
        'chi2': float(chi2_kernel) if not np.isnan(chi2_kernel) else None,
        'p': float(p_kernel) if not np.isnan(p_kernel) else None,
        'cramers_v': float(v_kernel) if not np.isnan(v_kernel) else None,
        'qo_e_pct': float(qo_e_pct),
        'chsh_e_pct': float(chsh_e_pct),
        'prediction': kernel_prediction,
    },
    'transition_stability': {
        'qo_mean': float(np.mean(stability_scores['QO'])) if stability_scores['QO'] else None,
        'chsh_mean': float(np.mean(stability_scores['CHSH'])) if stability_scores['CHSH'] else None,
        'qo_n': len(stability_scores['QO']),
        'chsh_n': len(stability_scores['CHSH']),
        'p': float(p_stab) if not np.isnan(p_stab) else None,
        'r_rb': float(r_rb_stab) if not np.isnan(r_rb_stab) else None,
        'qo_entropy': float(qo_entropy),
        'chsh_entropy': float(chsh_entropy),
        'prediction': stab_prediction,
    },
    'recovery_routing': {
        'post_hazard_qo': post_hazard_en['QO'],
        'post_hazard_chsh': post_hazard_en['CHSH'],
        'qo_escape_rate': float(qo_escape_rate) if not np.isnan(qo_escape_rate) else None,
        'base_qo_rate': float(base_qo_rate) if total_ph > 0 else None,
        'enrichment': float(enrichment) if not np.isnan(enrichment) else None,
        'binom_p': float(binom_p) if not np.isnan(binom_p) else None,
        'prediction': escape_prediction,
    },
    'hazard_proximity': {
        'qo_mean': float(np.mean(proximity['QO'])) if proximity['QO'] else None,
        'chsh_mean': float(np.mean(proximity['CHSH'])) if proximity['CHSH'] else None,
        'qo_n': len(proximity['QO']),
        'chsh_n': len(proximity['CHSH']),
        'p': float(p_prox) if not np.isnan(p_prox) else None,
        'r_rb': float(r_rb_prox) if not np.isnan(r_rb_prox) else None,
        'prediction': prox_prediction,
    },
    'hysteresis': {
        'n_lines_tested': len(en_sequences),
        'observed_alternation': float(obs_alt_rate),
        'null_mean': float(perm_array.mean()),
        'null_std': float(perm_array.std()),
        'perm_p': float(perm_p_alt),
        'direction': alt_direction,
        'transition_matrix': trans,
        'run_lengths': {
            sf: {
                'mean': float(np.mean(run_lengths[sf])) if run_lengths[sf] else None,
                'median': float(np.median(run_lengths[sf])) if run_lengths[sf] else None,
                'max': int(max(run_lengths[sf])) if run_lengths[sf] else None,
            } for sf in ['QO', 'CHSH']
        },
        'section_alternation': {
            sec: {
                'rate': d['alternations'] / d['pairs'] if d['pairs'] > 0 else 0,
                'n_pairs': d['pairs'],
            } for sec, d in section_alt.items()
        },
        'prediction': hysteresis_prediction,
    },
    'scorecard': scorecard,
    'verdict': verdict,
    'confirmed_count': confirmed,
    'total_tests': total_tests,
}

output_path = RESULTS_DIR / 'change_hold_validation.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
print("DONE.")
