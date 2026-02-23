"""
Phase 437: KE_THERMAL_CYCLING_VALIDATION
=========================================
Tests whether ke-family tokens encode thermal cycling (heat-equilibrate)
and whether e-depth is a parametric axis encoding equilibration duration.

Centerpiece: T3 tests PREFIX-controlled CHSH lane routing after ke-family tokens.

Uses paragraph-level analysis (C855/C862: paragraphs are programs).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

REGIME_PATH = ROOT / 'data' / 'regime_folio_mapping.json'
FORBIDDEN_PATH = ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
RESULTS_PATH = ROOT / 'phases' / 'KE_THERMAL_CYCLING_VALIDATION' / 'results' / 'ke_thermal_results.json'

# Lane classification by PREFIX (C574, C576, C649)
QO_PREFIXES = {'qo', 'ok', 'ot', 'o', 'ko', 'to', 'po'}
CHSH_PREFIXES = {'ch', 'sh', 'lsh'}

# ke-family: MIDDLEs containing only k and e atoms
KE_ATOMS = {'k', 'e'}

# kch-family for comparison: MIDDLEs starting with k and containing ch
# (from F-BRU-013: ke vs kch differentiation)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def is_ke_family(middle):
    """Check if MIDDLE consists only of k and e atoms."""
    if not middle:
        return False
    return all(ch in KE_ATOMS for ch in middle) and 'k' in middle and 'e' in middle


def is_kch_family(middle):
    """Check if MIDDLE is kch-family (contains k, c, h but NOT just k+e)."""
    if not middle:
        return False
    return 'k' in middle and 'c' in middle and 'h' in middle


def has_e_atom(middle):
    """Check if MIDDLE contains at least one e."""
    return middle and 'e' in middle


def e_depth(middle):
    """Count e atoms in a MIDDLE."""
    if not middle:
        return 0
    return sum(1 for ch in middle if ch == 'e')


def e_depth_group(middle):
    """Binary: single-e vs multi-e."""
    d = e_depth(middle)
    if d <= 1:
        return 'single-e'
    return 'multi-e'


def get_lane(prefix):
    """Classify prefix into lane."""
    if prefix in QO_PREFIXES:
        return 'QO'
    elif prefix in CHSH_PREFIXES:
        return 'CHSH'
    else:
        return 'OTHER'


def kernel_profile(middle):
    """Compute kernel atom fractions for a MIDDLE."""
    if not middle:
        return {'k': 0, 'h': 0, 'e': 0}
    k = sum(1 for ch in middle if ch == 'k')
    h = sum(1 for ch in middle if ch == 'h')
    e = sum(1 for ch in middle if ch == 'e')
    total = len(middle) if len(middle) > 0 else 1
    return {'k': k/total, 'h': h/total, 'e': e/total}


# =====================================================================
# LOAD DATA
# =====================================================================
print("KE THERMAL CYCLING VALIDATION")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Load regime assignments
with open(REGIME_PATH) as f:
    regime_raw = json.load(f)
regime_data = regime_raw.get('regime_assignments', regime_raw)

# Load forbidden transitions
with open(FORBIDDEN_PATH) as f:
    forbidden_raw = json.load(f)
forbidden_pairs = set()
forbidden_words = set()
for t in forbidden_raw['transitions']:
    forbidden_pairs.add((t['source'], t['target']))
    forbidden_words.add(t['source'])
    forbidden_words.add(t['target'])

# Build line-grouped tokens with morphology
print("\nBuilding line-grouped token data...")
line_groups = defaultdict(list)
all_tokens = []

for t in tx.currier_b():
    m = morph.extract(t.word)
    regime = regime_data.get(t.folio, {}).get('regime', 'UNK') if isinstance(regime_data, dict) else 'UNK'
    tok = {
        'word': t.word,
        'middle': m.middle if m.middle else '',
        'prefix': m.prefix if m.prefix else '',
        'suffix': m.suffix if m.suffix else '',
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'regime': regime,
        'line_initial': t.line_initial,
        'line_final': t.line_final,
        'is_ke_family': is_ke_family(m.middle) if m.middle else False,
        'is_kch_family': is_kch_family(m.middle) if m.middle else False,
        'has_e': has_e_atom(m.middle) if m.middle else False,
        'e_depth': e_depth(m.middle) if m.middle else 0,
        'e_group': e_depth_group(m.middle) if m.middle and is_ke_family(m.middle) else None,
        'lane': get_lane(m.prefix if m.prefix else ''),
    }
    key = (t.folio, t.line)
    line_groups[key].append(tok)
    all_tokens.append(tok)

# Summary
ke_tokens = [t for t in all_tokens if t['is_ke_family']]
kch_tokens = [t for t in all_tokens if t['is_kch_family']]
e_containing = [t for t in all_tokens if t['has_e'] and not t['is_ke_family'] and t['middle']]

print(f"  Total B tokens: {len(all_tokens)}")
print(f"  ke-family: {len(ke_tokens)} ({len(ke_tokens)/len(all_tokens):.1%})")
print(f"  kch-family: {len(kch_tokens)} ({len(kch_tokens)/len(all_tokens):.1%})")
print(f"  e-containing (non-ke): {len(e_containing)}")

# ke-family breakdown
ke_middles = Counter(t['middle'] for t in ke_tokens)
print(f"\n  ke-family MIDDLEs:")
for mid, cnt in ke_middles.most_common():
    grp = e_depth_group(mid)
    print(f"    {mid:>6s}: {cnt:>4d} ({grp}, e-depth={e_depth(mid)})")

single_e = [t for t in ke_tokens if t['e_group'] == 'single-e']
multi_e = [t for t in ke_tokens if t['e_group'] == 'multi-e']
print(f"\n  single-e: {len(single_e)}, multi-e: {len(multi_e)}")

results = {}

# =====================================================================
# T1: E-DEPTH x REGIME
# =====================================================================
print(f"\n{'=' * 70}")
print("T1: E-DEPTH x REGIME (binary collapse)")
print("=" * 70)

regime_edepth = defaultdict(Counter)
for t in ke_tokens:
    if t['regime'] != 'UNK':
        regime_edepth[t['regime']][t['e_group']] += 1

regimes = sorted(regime_edepth.keys())
print(f"\n  {'Regime':<12} {'single-e':>10} {'multi-e':>10} {'multi-e%':>10} {'N':>6}")
print(f"  {'------':<12} {'--------':>10} {'-------':>10} {'--------':>10} {'--':>6}")

table_t1 = []
for reg in regimes:
    s = regime_edepth[reg]['single-e']
    m = regime_edepth[reg]['multi-e']
    total = s + m
    pct = m / total if total > 0 else 0
    table_t1.append([s, m])
    print(f"  {reg:<12} {s:>10d} {m:>10d} {pct:>9.1%} {total:>6d}")

# Chi-squared test
table_arr = np.array(table_t1)
if table_arr.shape[0] >= 2 and table_arr.min() >= 0:
    chi2, p_t1, dof, expected = stats.chi2_contingency(table_arr)
    sig = '***' if p_t1 < 0.001 else '**' if p_t1 < 0.01 else '*' if p_t1 < 0.05 else 'NS'
    print(f"\n  Chi-squared: {chi2:.2f}, df={dof}, p={p_t1:.4f} {sig}")
    # Check min expected
    print(f"  Min expected count: {expected.min():.1f}")
else:
    p_t1 = 1.0
    print("\n  Insufficient data for chi-squared")

results['T1_edepth_regime'] = {
    'regime_counts': {r: dict(regime_edepth[r]) for r in regimes},
    'p_value': round(float(p_t1), 6),
}

# =====================================================================
# T2: E-DEPTH x SECTION (exploratory)
# =====================================================================
print(f"\n{'=' * 70}")
print("T2: E-DEPTH x SECTION (confirmatory/exploratory)")
print("=" * 70)

section_edepth = defaultdict(Counter)
for t in ke_tokens:
    section_edepth[t['section']][t['e_group']] += 1

sections = sorted(section_edepth.keys())
print(f"\n  {'Section':<12} {'single-e':>10} {'multi-e':>10} {'multi-e%':>10} {'N':>6}")
print(f"  {'-------':<12} {'--------':>10} {'-------':>10} {'--------':>10} {'--':>6}")

table_t2 = []
for sec in sections:
    s = section_edepth[sec]['single-e']
    m = section_edepth[sec]['multi-e']
    total = s + m
    pct = m / total if total > 0 else 0
    table_t2.append([s, m])
    print(f"  {sec:<12} {s:>10d} {m:>10d} {pct:>9.1%} {total:>6d}")

table_arr2 = np.array(table_t2)
if table_arr2.shape[0] >= 2 and table_arr2.min() >= 0:
    chi2_t2, p_t2, dof_t2, exp_t2 = stats.chi2_contingency(table_arr2)
    sig = '***' if p_t2 < 0.001 else '**' if p_t2 < 0.01 else '*' if p_t2 < 0.05 else 'NS'
    print(f"\n  Chi-squared: {chi2_t2:.2f}, df={dof_t2}, p={p_t2:.4f} {sig}")
    print(f"  Min expected count: {exp_t2.min():.1f}")
else:
    p_t2 = 1.0

results['T2_edepth_section'] = {
    'section_counts': {s: dict(section_edepth[s]) for s in sections},
    'p_value': round(float(p_t2), 6),
}

# =====================================================================
# T3: KE-FAMILY -> CHSH LANE ROUTING (KEY TEST)
# =====================================================================
print(f"\n{'=' * 70}")
print("T3: KE-FAMILY -> CHSH LANE ROUTING (PREFIX-controlled)")
print("=" * 70)

# For each non-line-final token, record (source_prefix, source_is_ke, next_lane)
successor_data = []
for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(len(tokens) - 1):
        src = tokens[i]
        nxt = tokens[i + 1]
        nxt_lane = nxt['lane']
        if nxt_lane == 'OTHER':
            continue  # Only count QO/CHSH successors
        src_prefix = src['prefix']
        if not src_prefix:
            continue
        successor_data.append({
            'src_prefix': src_prefix,
            'src_middle': src['middle'],
            'src_is_ke': src['is_ke_family'],
            'src_is_kch': src['is_kch_family'],
            'src_has_e': src['has_e'] and not src['is_ke_family'],
            'nxt_lane': nxt_lane,
        })

print(f"\n  Successor pairs with QO/CHSH next-lane: {len(successor_data)}")

# Overall ke-family vs non-ke routing (unstratified)
ke_succ = [s for s in successor_data if s['src_is_ke']]
nonke_succ = [s for s in successor_data if not s['src_is_ke']]
kch_succ = [s for s in successor_data if s['src_is_kch']]

ke_chsh_rate = sum(1 for s in ke_succ if s['nxt_lane'] == 'CHSH') / len(ke_succ) if ke_succ else 0
nonke_chsh_rate = sum(1 for s in nonke_succ if s['nxt_lane'] == 'CHSH') / len(nonke_succ) if nonke_succ else 0
kch_chsh_rate = sum(1 for s in kch_succ if s['nxt_lane'] == 'CHSH') / len(kch_succ) if kch_succ else 0

print(f"\n  Unstratified CHSH routing rates:")
print(f"    ke-family:    {ke_chsh_rate:.1%} ({len(ke_succ)} tokens)")
print(f"    kch-family:   {kch_chsh_rate:.1%} ({len(kch_succ)} tokens)")
print(f"    non-ke/kch:   {nonke_chsh_rate:.1%} ({len(nonke_succ)} tokens)")

# PREFIX-stratified analysis
print(f"\n  PREFIX-stratified CHSH routing (ke-family vs baseline):")
prefix_counts = Counter(s['src_prefix'] for s in successor_data)
strata_results = {}

print(f"  {'PREFIX':<8} {'ke->CHSH':>10} {'ke_N':>6} {'base->CHSH':>12} {'base_N':>8} {'Delta':>8} {'Fisher_p':>10}")
print(f"  {'------':<8} {'--------':>10} {'----':>6} {'----------':>12} {'------':>8} {'-----':>8} {'---------':>10}")

for prefix in sorted(prefix_counts.keys()):
    if prefix_counts[prefix] < 20:
        continue  # Skip very rare prefixes
    ke_in_prefix = [s for s in successor_data if s['src_prefix'] == prefix and s['src_is_ke']]
    base_in_prefix = [s for s in successor_data if s['src_prefix'] == prefix and not s['src_is_ke']]

    if len(ke_in_prefix) < 5 or len(base_in_prefix) < 5:
        continue

    ke_chsh = sum(1 for s in ke_in_prefix if s['nxt_lane'] == 'CHSH')
    ke_qo = len(ke_in_prefix) - ke_chsh
    base_chsh = sum(1 for s in base_in_prefix if s['nxt_lane'] == 'CHSH')
    base_qo = len(base_in_prefix) - base_chsh

    ke_rate = ke_chsh / len(ke_in_prefix) if ke_in_prefix else 0
    base_rate = base_chsh / len(base_in_prefix) if base_in_prefix else 0
    delta = ke_rate - base_rate

    # Fisher exact test
    table = [[ke_chsh, ke_qo], [base_chsh, base_qo]]
    odds, fisher_p = stats.fisher_exact(table)

    sig = '***' if fisher_p < 0.001 else '**' if fisher_p < 0.01 else '*' if fisher_p < 0.05 else ''
    print(f"  {prefix:<8} {ke_rate:>9.1%} {len(ke_in_prefix):>6d} {base_rate:>11.1%} {len(base_in_prefix):>8d} {delta:>+7.1%} {fisher_p:>9.4f} {sig}")

    strata_results[prefix] = {
        'ke_chsh_rate': round(ke_rate, 4),
        'base_chsh_rate': round(base_rate, 4),
        'ke_n': len(ke_in_prefix),
        'base_n': len(base_in_prefix),
        'fisher_p': round(float(fisher_p), 6),
    }

# Permutation test (PREFIX-stratified)
print(f"\n  Running PREFIX-stratified permutation test (10000 iterations)...")
observed_ke_chsh_total = sum(1 for s in ke_succ if s['nxt_lane'] == 'CHSH')
observed_ke_chsh_rate = observed_ke_chsh_total / len(ke_succ) if ke_succ else 0

# For each PREFIX stratum, compute the weighted expected CHSH rate under null
# (shuffle ke/non-ke labels within each PREFIX)
n_perms = 10000
null_rates = []
rng = np.random.default_rng(42)

# Group successor data by prefix for efficient shuffling
prefix_groups = defaultdict(list)
for s in successor_data:
    prefix_groups[s['src_prefix']].append(s)

for _ in range(n_perms):
    perm_ke_chsh = 0
    perm_ke_total = 0
    for prefix, group in prefix_groups.items():
        n_ke_in_group = sum(1 for s in group if s['src_is_ke'])
        if n_ke_in_group == 0 or n_ke_in_group == len(group):
            # No variation possible in this stratum
            for s in group:
                if s['src_is_ke'] and s['nxt_lane'] == 'CHSH':
                    perm_ke_chsh += 1
                if s['src_is_ke']:
                    perm_ke_total += 1
            continue
        # Shuffle the ke labels within this prefix
        lanes = [s['nxt_lane'] for s in group]
        shuffled_idx = rng.permutation(len(group))
        # First n_ke_in_group get "ke" label
        for j in range(n_ke_in_group):
            if lanes[shuffled_idx[j]] == 'CHSH':
                perm_ke_chsh += 1
        perm_ke_total += n_ke_in_group

    null_rates.append(perm_ke_chsh / perm_ke_total if perm_ke_total > 0 else 0)

null_mean = np.mean(null_rates)
null_std = np.std(null_rates)
p_perm = np.mean([nr >= observed_ke_chsh_rate for nr in null_rates])

print(f"    Observed ke -> CHSH rate: {observed_ke_chsh_rate:.4f}")
print(f"    Null mean: {null_mean:.4f} +/- {null_std:.4f}")
print(f"    Permutation p-value: {p_perm:.4f}")
sig = '***' if p_perm < 0.001 else '**' if p_perm < 0.01 else '*' if p_perm < 0.05 else 'NS'
print(f"    --> {sig}")

results['T3_lane_routing'] = {
    'ke_chsh_rate': round(ke_chsh_rate, 4),
    'kch_chsh_rate': round(kch_chsh_rate, 4),
    'nonke_chsh_rate': round(nonke_chsh_rate, 4),
    'ke_n': len(ke_succ),
    'kch_n': len(kch_succ),
    'strata': strata_results,
    'permutation_p': round(float(p_perm), 6),
    'null_mean': round(null_mean, 4),
    'null_std': round(null_std, 4),
}

# =====================================================================
# T4: MORPHOLOGICAL SPILLOVER NULL
# =====================================================================
print(f"\n{'=' * 70}")
print("T4: MORPHOLOGICAL SPILLOVER NULL (ke-specific vs general e-containing)")
print("=" * 70)

# Compare ke-family CHSH routing against all e-containing non-ke MIDDLEs
e_succ = [s for s in successor_data if s['src_has_e']]
e_chsh_rate = sum(1 for s in e_succ if s['nxt_lane'] == 'CHSH') / len(e_succ) if e_succ else 0

print(f"\n  CHSH routing rates:")
print(f"    ke-family:           {ke_chsh_rate:.1%} ({len(ke_succ)} tokens)")
print(f"    e-containing non-ke: {e_chsh_rate:.1%} ({len(e_succ)} tokens)")
print(f"    all non-ke:          {nonke_chsh_rate:.1%} ({len(nonke_succ)} tokens)")

# Fisher exact: ke-family vs e-containing non-ke
ke_chsh_n = sum(1 for s in ke_succ if s['nxt_lane'] == 'CHSH')
ke_qo_n = len(ke_succ) - ke_chsh_n
e_chsh_n = sum(1 for s in e_succ if s['nxt_lane'] == 'CHSH')
e_qo_n = len(e_succ) - e_chsh_n

if ke_chsh_n + ke_qo_n > 0 and e_chsh_n + e_qo_n > 0:
    table_t4 = [[ke_chsh_n, ke_qo_n], [e_chsh_n, e_qo_n]]
    odds_t4, p_t4 = stats.fisher_exact(table_t4)
    sig = '***' if p_t4 < 0.001 else '**' if p_t4 < 0.01 else '*' if p_t4 < 0.05 else 'NS'
    print(f"\n  ke-family vs e-containing: Fisher p={p_t4:.4f} {sig}, OR={odds_t4:.2f}")

    if p_t4 < 0.05:
        print(f"  --> ke-family has DISTINCT routing from general e-pool (ke-specific effect)")
    else:
        print(f"  --> ke-family routing is INDISTINGUISHABLE from general e-pool (compositional effect)")
else:
    p_t4 = 1.0

results['T4_spillover_null'] = {
    'ke_chsh_rate': round(ke_chsh_rate, 4),
    'e_containing_chsh_rate': round(e_chsh_rate, 4),
    'fisher_p': round(float(p_t4), 6),
}

# =====================================================================
# T5: SEQUENTIAL CONTEXT (what precedes ke vs kch)
# =====================================================================
print(f"\n{'=' * 70}")
print("T5: SEQUENTIAL CONTEXT (what precedes ke-family vs kch-family)")
print("=" * 70)

# For non-line-initial tokens, record predecessor's kernel profile
ke_predecessors = []
kch_predecessors = []
other_predecessors = []

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(1, len(tokens)):
        curr = tokens[i]
        prev = tokens[i - 1]
        prev_kp = kernel_profile(prev['middle'])

        if curr['is_ke_family']:
            ke_predecessors.append(prev_kp)
        elif curr['is_kch_family']:
            kch_predecessors.append(prev_kp)
        else:
            other_predecessors.append(prev_kp)

print(f"\n  Predecessor kernel profiles:")
print(f"  {'Context':<20} {'N':>6} {'mean_k':>8} {'mean_h':>8} {'mean_e':>8}")
print(f"  {'-------':<20} {'--':>6} {'------':>8} {'------':>8} {'------':>8}")

for label, preds in [('before ke-family', ke_predecessors),
                      ('before kch-family', kch_predecessors),
                      ('before other', other_predecessors)]:
    if not preds:
        continue
    mk = np.mean([p['k'] for p in preds])
    mh = np.mean([p['h'] for p in preds])
    me = np.mean([p['e'] for p in preds])
    print(f"  {label:<20} {len(preds):>6d} {mk:>7.1%} {mh:>7.1%} {me:>7.1%}")

# KW test: do predecessors of ke differ from predecessors of kch on each kernel?
print(f"\n  Kruskal-Wallis: ke predecessors vs kch predecessors vs other")
for kernel_name in ['k', 'h', 'e']:
    ke_vals = [p[kernel_name] for p in ke_predecessors]
    kch_vals = [p[kernel_name] for p in kch_predecessors]
    other_vals = [p[kernel_name] for p in other_predecessors]

    if len(ke_vals) >= 5 and len(kch_vals) >= 5:
        H_stat, p_kw = stats.kruskal(ke_vals, kch_vals, other_vals)
        sig = '***' if p_kw < 0.001 else '**' if p_kw < 0.01 else '*' if p_kw < 0.05 else 'NS'
        print(f"    {kernel_name}-kernel: H={H_stat:.2f}, p={p_kw:.4f} {sig}")

        # Pairwise: ke vs kch specifically
        u_stat, p_mw = stats.mannwhitneyu(ke_vals, kch_vals, alternative='two-sided')
        sig2 = '***' if p_mw < 0.001 else '**' if p_mw < 0.01 else '*' if p_mw < 0.05 else 'NS'
        print(f"      ke vs kch: U={u_stat:.0f}, p={p_mw:.4f} {sig2}")

# Also: does ke follow h-containing MIDDLEs more than kch does?
ke_after_h = sum(1 for p in ke_predecessors if p['h'] > 0)
kch_after_h = sum(1 for p in kch_predecessors if p['h'] > 0)
ke_after_h_rate = ke_after_h / len(ke_predecessors) if ke_predecessors else 0
kch_after_h_rate = kch_after_h / len(kch_predecessors) if kch_predecessors else 0

print(f"\n  Preceded by h-containing MIDDLE:")
print(f"    ke-family:  {ke_after_h_rate:.1%} ({ke_after_h}/{len(ke_predecessors)})")
print(f"    kch-family: {kch_after_h_rate:.1%} ({kch_after_h}/{len(kch_predecessors)})")

results['T5_sequential_context'] = {
    'ke_pred_mean_k': round(float(np.mean([p['k'] for p in ke_predecessors])), 4) if ke_predecessors else None,
    'ke_pred_mean_h': round(float(np.mean([p['h'] for p in ke_predecessors])), 4) if ke_predecessors else None,
    'ke_pred_mean_e': round(float(np.mean([p['e'] for p in ke_predecessors])), 4) if ke_predecessors else None,
    'kch_pred_mean_k': round(float(np.mean([p['k'] for p in kch_predecessors])), 4) if kch_predecessors else None,
    'kch_pred_mean_h': round(float(np.mean([p['h'] for p in kch_predecessors])), 4) if kch_predecessors else None,
    'kch_pred_mean_e': round(float(np.mean([p['e'] for p in kch_predecessors])), 4) if kch_predecessors else None,
    'ke_after_h_rate': round(ke_after_h_rate, 4),
    'kch_after_h_rate': round(kch_after_h_rate, 4),
}

# =====================================================================
# T6: KE vs KCH HAZARD PROXIMITY
# =====================================================================
print(f"\n{'=' * 70}")
print("T6: KE vs KCH HAZARD PROXIMITY")
print("=" * 70)

# For each ke/kch token in a line, compute min distance to forbidden pair member
ke_hazard_dists = []
kch_hazard_dists = []
other_hazard_dists = []

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    words = [t['word'] for t in tokens]

    # Find positions of forbidden-pair-participating words
    forbidden_positions = set()
    for i in range(len(words) - 1):
        if (words[i], words[i+1]) in forbidden_pairs:
            forbidden_positions.add(i)
            forbidden_positions.add(i+1)

    # Also check individual words that are sources or targets
    for i, w in enumerate(words):
        if w in forbidden_words:
            forbidden_positions.add(i)

    if not forbidden_positions:
        continue  # No hazard reference points in this line

    for i, tok in enumerate(tokens):
        min_dist = min(abs(i - fp) for fp in forbidden_positions)
        if tok['is_ke_family']:
            ke_hazard_dists.append(min_dist)
        elif tok['is_kch_family']:
            kch_hazard_dists.append(min_dist)
        else:
            other_hazard_dists.append(min_dist)

print(f"\n  Tokens in lines with forbidden pair members:")
print(f"    ke-family: {len(ke_hazard_dists)}")
print(f"    kch-family: {len(kch_hazard_dists)}")
print(f"    other: {len(other_hazard_dists)}")

if ke_hazard_dists and kch_hazard_dists:
    print(f"\n  Mean distance to nearest forbidden word:")
    print(f"    ke-family:  {np.mean(ke_hazard_dists):.2f} (median {np.median(ke_hazard_dists):.0f})")
    print(f"    kch-family: {np.mean(kch_hazard_dists):.2f} (median {np.median(kch_hazard_dists):.0f})")
    print(f"    other:      {np.mean(other_hazard_dists):.2f} (median {np.median(other_hazard_dists):.0f})")

    u_stat, p_t6 = stats.mannwhitneyu(ke_hazard_dists, kch_hazard_dists, alternative='greater')
    sig = '***' if p_t6 < 0.001 else '**' if p_t6 < 0.01 else '*' if p_t6 < 0.05 else 'NS'
    print(f"\n  ke farther than kch? U={u_stat:.0f}, p={p_t6:.4f} {sig}")
else:
    p_t6 = 1.0
    print("\n  Insufficient data for hazard proximity comparison")

results['T6_hazard_proximity'] = {
    'ke_mean_dist': round(float(np.mean(ke_hazard_dists)), 4) if ke_hazard_dists else None,
    'kch_mean_dist': round(float(np.mean(kch_hazard_dists)), 4) if kch_hazard_dists else None,
    'p_value': round(float(p_t6), 6),
}

# =====================================================================
# T7: E-DEPTH x SUFFIX
# =====================================================================
print(f"\n{'=' * 70}")
print("T7: E-DEPTH x SUFFIX DISTRIBUTION")
print("=" * 70)

suffix_by_group = defaultdict(Counter)
for t in ke_tokens:
    if t['suffix']:
        suffix_by_group[t['e_group']][t['suffix']] += 1

for grp in ['single-e', 'multi-e']:
    total = sum(suffix_by_group[grp].values())
    print(f"\n  {grp} suffixes (N={total}):")
    for suf, cnt in suffix_by_group[grp].most_common(8):
        print(f"    {suf:>6s}: {cnt:>4d} ({cnt/total:.1%})")

# Build contingency table for top suffixes
all_suffixes = set()
for grp in suffix_by_group:
    all_suffixes.update(suffix_by_group[grp].keys())
top_suffixes = sorted(all_suffixes, key=lambda s: sum(suffix_by_group[g][s] for g in suffix_by_group), reverse=True)[:6]

table_t7 = []
for grp in ['single-e', 'multi-e']:
    row = [suffix_by_group[grp].get(s, 0) for s in top_suffixes]
    # Add "other" column
    other = sum(v for s, v in suffix_by_group[grp].items() if s not in top_suffixes)
    row.append(other)
    table_t7.append(row)

table_t7_arr = np.array(table_t7)
if table_t7_arr.shape[0] >= 2 and table_t7_arr.sum() > 0:
    chi2_t7, p_t7, dof_t7, exp_t7 = stats.chi2_contingency(table_t7_arr)
    sig = '***' if p_t7 < 0.001 else '**' if p_t7 < 0.01 else '*' if p_t7 < 0.05 else 'NS'
    print(f"\n  Chi-squared (top {len(top_suffixes)} + other): {chi2_t7:.2f}, df={dof_t7}, p={p_t7:.4f} {sig}")
    print(f"  Min expected: {exp_t7.min():.1f}")
else:
    p_t7 = 1.0

results['T7_suffix'] = {
    'single_e_suffixes': dict(suffix_by_group['single-e'].most_common(10)),
    'multi_e_suffixes': dict(suffix_by_group['multi-e'].most_common(10)),
    'p_value': round(float(p_t7), 6),
}

# =====================================================================
# T8: E-DEPTH x LINE POSITION (PREFIX-controlled)
# =====================================================================
print(f"\n{'=' * 70}")
print("T8: E-DEPTH x LINE POSITION (PREFIX-controlled)")
print("=" * 70)

# Compute normalized line position for each ke-family token
ke_positions = {'single-e': [], 'multi-e': []}
ke_positions_by_prefix = defaultdict(lambda: {'single-e': [], 'multi-e': []})

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    n = len(tokens)
    if n < 3:
        continue
    for i, tok in enumerate(tokens):
        if tok['is_ke_family']:
            pos = i / (n - 1)  # 0.0 to 1.0
            grp = tok['e_group']
            ke_positions[grp].append(pos)
            ke_positions_by_prefix[tok['prefix']][grp].append(pos)

print(f"\n  Overall line position:")
for grp in ['single-e', 'multi-e']:
    vals = ke_positions[grp]
    if vals:
        print(f"    {grp}: mean={np.mean(vals):.3f}, median={np.median(vals):.3f}, N={len(vals)}")

if ke_positions['single-e'] and ke_positions['multi-e']:
    u_stat, p_t8 = stats.mannwhitneyu(ke_positions['single-e'], ke_positions['multi-e'], alternative='two-sided')
    sig = '***' if p_t8 < 0.001 else '**' if p_t8 < 0.01 else '*' if p_t8 < 0.05 else 'NS'
    print(f"\n  Mann-Whitney U: {u_stat:.0f}, p={p_t8:.4f} {sig}")
else:
    p_t8 = 1.0

# PREFIX-controlled: within major prefixes
print(f"\n  PREFIX-controlled line position:")
for prefix in sorted(ke_positions_by_prefix.keys()):
    s = ke_positions_by_prefix[prefix]['single-e']
    m = ke_positions_by_prefix[prefix]['multi-e']
    if len(s) >= 5 and len(m) >= 3:
        print(f"    {prefix:<6s}: single-e mean={np.mean(s):.3f} (N={len(s)}), multi-e mean={np.mean(m):.3f} (N={len(m)})")

results['T8_line_position'] = {
    'single_e_mean_pos': round(float(np.mean(ke_positions['single-e'])), 4) if ke_positions['single-e'] else None,
    'multi_e_mean_pos': round(float(np.mean(ke_positions['multi-e'])), 4) if ke_positions['multi-e'] else None,
    'p_value': round(float(p_t8), 6),
}

# =====================================================================
# VERDICT
# =====================================================================
print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

bonferroni = 0.05 / 8
print(f"\n  Bonferroni-corrected alpha: {bonferroni:.4f}")
print(f"\n  {'Test':<40} {'p-value':>10} {'Pass?':>8}")
print(f"  {'----':<40} {'-------':>10} {'-----':>8}")

tests = [
    ('T1: E-depth x REGIME', p_t1),
    ('T2: E-depth x Section', p_t2),
    ('T3: ke->CHSH routing (permutation)', p_perm),
    ('T4: Spillover null (ke vs e-pool)', p_t4),
    ('T5: Sequential context', None),  # Multiple tests
    ('T6: Hazard proximity', p_t6),
    ('T7: Suffix x e-depth', p_t7),
    ('T8: Line position x e-depth', p_t8),
]

n_pass = 0
for name, p in tests:
    if p is None:
        print(f"  {name:<40} {'(multi)':>10} {'--':>8}")
    else:
        passed = p < bonferroni
        if passed:
            n_pass += 1
        sig_str = 'PASS' if passed else 'fail'
        print(f"  {name:<40} {p:>10.4f} {sig_str:>8}")

print(f"\n  Tests passing Bonferroni: {n_pass}/7")

# =====================================================================
# SAVE
# =====================================================================
with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_PATH}")
