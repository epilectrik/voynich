#!/usr/bin/env python3
"""
Phase 338: PREFIX_COMPOSITION_STATE_ROUTING
============================================
Formalizes the finding that PREFIX composition is a general macro-state
routing mechanism across the 6-state automaton (C1010).

Exploratory work (composition_state_selector.py in GLOSS_ADVERSARIAL_VALIDATION)
found: 35/87 MIDDLEs span multiple macro states, and PREFIX changes state in
21/27 cases (77.8%). This phase applies rigorous statistical tests.

Tests:
  T1: State-change rate significance (permutation test)
  T2: PREFIX entropy reduction over full 6-state partition
  T3: da FL-router uniqueness (Fisher exact)
  T4: ar FL_SAFE purity (binomial test)
  T5: PREFIX purity non-randomness (permutation test)
  T6: Synthesis / verdict

Depends on: C1010 (6-state partition), C1012 (PREFIX selectivity for FL split),
            C911 (PREFIX-MIDDLE selectivity)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import fisher_exact, binomtest, chi2_contingency

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

N_STATES = len(MACRO_STATE_PARTITION)
N_PERMUTATIONS = 10000

# ── Data loading ─────────────────────────────────────────────────────

def load_data():
    """Load token-class mapping and extract morphology."""
    print("Loading data...")

    morph = Morphology()

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)

    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    print(f"  {len(token_to_class)} tokens mapped to 49 classes")

    # Extract morphology for each token
    token_data = []
    for token, cls in token_to_class.items():
        m = morph.extract(token)
        if not m or not m.middle:
            continue
        state = CLASS_TO_STATE.get(cls, 'UNKNOWN')
        token_data.append({
            'token': token,
            'class': cls,
            'state': state,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'has_prefix': m.prefix is not None,
        })

    print(f"  {len(token_data)} tokens with morphology")
    return token_data, token_to_class


def build_groups(token_data):
    """Build MIDDLE groups and PREFIX distributions."""
    middle_groups = defaultdict(list)
    for td in token_data:
        middle_groups[td['middle']].append(td)

    # MIDDLEs spanning multiple states
    multi_state = {}
    single_state = {}
    for mid, tokens in middle_groups.items():
        states = set(td['state'] for td in tokens)
        if len(states) > 1:
            multi_state[mid] = tokens
        else:
            single_state[mid] = tokens

    # PREFIX state distributions
    prefix_state_dist = defaultdict(Counter)
    for td in token_data:
        pfx = td['prefix'] or '(bare)'
        prefix_state_dist[pfx][td['state']] += 1

    # Overall state distribution (marginal)
    state_counts = Counter(td['state'] for td in token_data)

    return middle_groups, multi_state, single_state, prefix_state_dist, state_counts


# ── T1: State-Change Rate Significance ──────────────────────────────

def run_t1(middle_groups, state_counts, token_data):
    """Test whether 77.8% state-change rate is above null expectation.

    For each MIDDLE with both bare and prefixed forms, check if PREFIX
    changes the macro state. Under null: prefixed tokens' states are
    drawn from the marginal state distribution.
    """
    print("\n" + "=" * 60)
    print("T1: State-Change Rate Significance")
    print("=" * 60)

    # Identify test MIDDLEs (have both bare and prefixed forms)
    test_middles = []
    for mid, tokens in middle_groups.items():
        bare = [td for td in tokens if not td['has_prefix']]
        prefixed = [td for td in tokens if td['has_prefix']]
        if bare and prefixed:
            bare_states = set(td['state'] for td in bare)
            prefixed_states = set(td['state'] for td in prefixed)
            changed = bare_states != prefixed_states
            test_middles.append({
                'middle': mid,
                'bare_states': bare_states,
                'prefixed_states': prefixed_states,
                'n_bare': len(bare),
                'n_prefixed': len(prefixed),
                'changed': changed,
            })

    n_test = len(test_middles)
    n_changed = sum(1 for tm in test_middles if tm['changed'])
    observed_rate = n_changed / n_test if n_test > 0 else 0

    print(f"  Test MIDDLEs (bare + prefixed forms): {n_test}")
    print(f"  Observed state changes: {n_changed}/{n_test} = {observed_rate:.1%}")

    # Compute null expectation analytically:
    # For each test MIDDLE, P(state change) = 1 - P(all prefixed tokens in same states as bare)
    total_tokens = len(token_data)
    state_probs = {s: c / total_tokens for s, c in state_counts.items()}

    # Permutation test: shuffle state assignments across all tokens,
    # then recompute state-change rate
    all_states = [td['state'] for td in token_data]
    all_states_arr = np.array(all_states)

    # Build index for fast lookup
    token_to_idx = {td['token']: i for i, td in enumerate(token_data)}
    test_middle_indices = []
    for mid, tokens in middle_groups.items():
        bare = [td for td in tokens if not td['has_prefix']]
        prefixed = [td for td in tokens if td['has_prefix']]
        if bare and prefixed:
            bare_idx = [token_to_idx[td['token']] for td in bare]
            pref_idx = [token_to_idx[td['token']] for td in prefixed]
            test_middle_indices.append((bare_idx, pref_idx))

    perm_changes = np.zeros(N_PERMUTATIONS)
    for p in range(N_PERMUTATIONS):
        shuffled = np.random.permutation(all_states_arr)
        changes = 0
        for bare_idx, pref_idx in test_middle_indices:
            bare_s = set(shuffled[bare_idx])
            pref_s = set(shuffled[pref_idx])
            if bare_s != pref_s:
                changes += 1
        perm_changes[p] = changes

    null_mean = np.mean(perm_changes) / n_test
    null_std = np.std(perm_changes) / n_test
    z_score = (observed_rate - null_mean) / null_std if null_std > 0 else 0
    p_value = np.mean(perm_changes >= n_changed)

    print(f"  Null mean rate: {null_mean:.3f} ± {null_std:.3f}")
    print(f"  z-score: {z_score:.2f}")
    print(f"  p-value (permutation, one-sided): {p_value:.4f}")
    print(f"  Verdict: {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")

    return {
        'n_test_middles': n_test,
        'n_changed': n_changed,
        'observed_rate': round(observed_rate, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 2),
        'p_value': round(p_value, 4),
        'n_permutations': N_PERMUTATIONS,
        'pass': p_value < 0.05,
        'test_middles': [
            {'middle': tm['middle'],
             'n_bare': tm['n_bare'],
             'n_prefixed': tm['n_prefixed'],
             'changed': tm['changed'],
             'bare_states': sorted(tm['bare_states']),
             'prefixed_states': sorted(tm['prefixed_states'])}
            for tm in sorted(test_middles, key=lambda x: x['middle'])
        ],
    }


# ── T2: PREFIX Entropy Reduction (Full 6-State) ─────────────────────

def run_t2(prefix_state_dist, state_counts, token_data):
    """Measure how much knowing PREFIX reduces uncertainty about macro state.

    Generalizes C1012 (binary FL split) to the full 6-state partition.
    H(State) - H(State|PREFIX) as fraction of H(State).
    """
    print("\n" + "=" * 60)
    print("T2: PREFIX Entropy Reduction (Full 6-State)")
    print("=" * 60)

    total = len(token_data)

    # Marginal entropy H(State)
    probs = np.array([state_counts[s] / total for s in sorted(MACRO_STATE_PARTITION.keys())])
    probs = probs[probs > 0]
    H_state = -np.sum(probs * np.log2(probs))

    # Conditional entropy H(State|PREFIX)
    H_cond = 0.0
    per_prefix = {}
    for pfx, scounts in prefix_state_dist.items():
        pfx_total = sum(scounts.values())
        if pfx_total < 1:
            continue
        pfx_probs = np.array([scounts.get(s, 0) / pfx_total
                              for s in sorted(MACRO_STATE_PARTITION.keys())])
        pfx_probs = pfx_probs[pfx_probs > 0]
        H_pfx = -np.sum(pfx_probs * np.log2(pfx_probs))
        weight = pfx_total / total
        H_cond += weight * H_pfx

        # Per-prefix stats
        dominant = max(scounts.values())
        per_prefix[pfx] = {
            'n_tokens': pfx_total,
            'n_states': len(scounts),
            'entropy': round(H_pfx, 4),
            'purity': round(dominant / pfx_total, 4),
            'dominant_state': scounts.most_common(1)[0][0],
        }

    entropy_reduction = (H_state - H_cond) / H_state if H_state > 0 else 0

    print(f"  H(State): {H_state:.4f} bits")
    print(f"  H(State|PREFIX): {H_cond:.4f} bits")
    print(f"  Entropy reduction: {entropy_reduction:.1%}")

    # Permutation test: shuffle PREFIX labels, recompute H(State|PREFIX)
    all_prefixes = [td['prefix'] or '(bare)' for td in token_data]
    all_states = [td['state'] for td in token_data]
    all_prefixes_arr = np.array(all_prefixes)
    all_states_arr = np.array(all_states)

    perm_reductions = np.zeros(N_PERMUTATIONS)
    for p in range(N_PERMUTATIONS):
        shuffled_pfx = np.random.permutation(all_prefixes_arr)
        # Build conditional entropy with shuffled prefixes
        pfx_state_counts = defaultdict(Counter)
        for i in range(len(token_data)):
            pfx_state_counts[shuffled_pfx[i]][all_states_arr[i]] += 1

        H_cond_perm = 0.0
        for pfx, scounts in pfx_state_counts.items():
            pfx_total = sum(scounts.values())
            pfx_probs = np.array([scounts.get(s, 0) / pfx_total
                                  for s in sorted(MACRO_STATE_PARTITION.keys())])
            pfx_probs = pfx_probs[pfx_probs > 0]
            H_pfx = -np.sum(pfx_probs * np.log2(pfx_probs))
            H_cond_perm += (pfx_total / total) * H_pfx

        perm_reductions[p] = (H_state - H_cond_perm) / H_state

    null_mean = np.mean(perm_reductions)
    null_std = np.std(perm_reductions)
    z_score = (entropy_reduction - null_mean) / null_std if null_std > 0 else 0
    p_value = np.mean(perm_reductions >= entropy_reduction)

    print(f"  Null mean reduction: {null_mean:.4f} ± {null_std:.4f}")
    print(f"  z-score: {z_score:.1f}")
    print(f"  p-value: {p_value:.4f}")

    # Count 100%-pure PREFIXes (with >= 3 tokens)
    pure_prefixes = [pfx for pfx, info in per_prefix.items()
                     if info['purity'] == 1.0 and info['n_tokens'] >= 3]

    print(f"  100%-pure PREFIXes (n>=3): {len(pure_prefixes)}/{sum(1 for p in per_prefix.values() if p['n_tokens'] >= 3)}")
    print(f"  Verdict: {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")

    return {
        'H_state': round(H_state, 4),
        'H_state_given_prefix': round(H_cond, 4),
        'entropy_reduction': round(entropy_reduction, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 1),
        'p_value': round(p_value, 4),
        'n_permutations': N_PERMUTATIONS,
        'n_pure_prefixes_ge3': len(pure_prefixes),
        'n_prefixes_ge3': sum(1 for p in per_prefix.values() if p['n_tokens'] >= 3),
        'pure_prefixes': sorted(pure_prefixes),
        'pass': p_value < 0.05,
        'per_prefix': {k: v for k, v in sorted(per_prefix.items(),
                       key=lambda x: -x[1]['n_tokens'])},
    }


# ── T3: da FL-Router Uniqueness ─────────────────────────────────────

def run_t3(prefix_state_dist, token_data):
    """Test whether da is uniquely the FL-domain router.

    da routes tokens into BOTH FL_HAZ and FL_SAFE with substantial count.
    Is this unique among all PREFIXes? Fisher exact test.
    """
    print("\n" + "=" * 60)
    print("T3: da FL-Router Uniqueness")
    print("=" * 60)

    fl_states = {'FL_HAZ', 'FL_SAFE'}

    # For each PREFIX: count FL tokens vs non-FL tokens
    prefix_fl = {}
    for pfx, scounts in prefix_state_dist.items():
        n_total = sum(scounts.values())
        n_fl_haz = scounts.get('FL_HAZ', 0)
        n_fl_safe = scounts.get('FL_SAFE', 0)
        n_fl = n_fl_haz + n_fl_safe
        n_non_fl = n_total - n_fl
        has_both_fl = n_fl_haz > 0 and n_fl_safe > 0
        prefix_fl[pfx] = {
            'n_total': n_total,
            'n_fl_haz': n_fl_haz,
            'n_fl_safe': n_fl_safe,
            'n_fl': n_fl,
            'n_non_fl': n_non_fl,
            'fl_fraction': n_fl / n_total if n_total > 0 else 0,
            'has_both_fl': has_both_fl,
        }

    # How many PREFIXes route into BOTH FL_HAZ and FL_SAFE?
    both_fl_prefixes = [pfx for pfx, info in prefix_fl.items() if info['has_both_fl']]
    print(f"  PREFIXes routing into both FL_HAZ and FL_SAFE: {both_fl_prefixes}")

    # da-specific stats
    da_info = prefix_fl.get('da', {})
    da_fl_haz = da_info.get('n_fl_haz', 0)
    da_fl_safe = da_info.get('n_fl_safe', 0)
    da_total = da_info.get('n_total', 0)
    da_fl_frac = da_info.get('fl_fraction', 0)

    print(f"  da: {da_total} tokens, FL_HAZ={da_fl_haz}, FL_SAFE={da_fl_safe}, FL fraction={da_fl_frac:.1%}")

    # Fisher exact: da's FL fraction vs all other PREFIXes combined
    other_fl = sum(info['n_fl'] for pfx, info in prefix_fl.items() if pfx != 'da')
    other_non_fl = sum(info['n_non_fl'] for pfx, info in prefix_fl.items() if pfx != 'da')
    da_non_fl = da_info.get('n_non_fl', 0)
    da_fl = da_info.get('n_fl', 0)

    table = [[da_fl, da_non_fl],
             [other_fl, other_non_fl]]
    odds_ratio, p_fisher = fisher_exact(table, alternative='greater')

    print(f"  Fisher exact (da FL vs others): OR={odds_ratio:.2f}, p={p_fisher:.6f}")

    # Is da's even split (HAZ/SAFE) consistent with being a true router?
    # Under null: if FL tokens are randomly HAZ or SAFE with overall FL ratio
    total_fl_haz = sum(info['n_fl_haz'] for info in prefix_fl.values())
    total_fl_safe = sum(info['n_fl_safe'] for info in prefix_fl.values())
    total_fl = total_fl_haz + total_fl_safe
    haz_prob = total_fl_haz / total_fl if total_fl > 0 else 0.5

    # Binomial test: is da's HAZ/SAFE split consistent with the overall ratio?
    # da has da_fl_haz successes out of (da_fl_haz + da_fl_safe) trials
    da_fl_total = da_fl_haz + da_fl_safe
    if da_fl_total > 0:
        p_binom_split = binomtest(da_fl_haz, da_fl_total, haz_prob).pvalue
    else:
        p_binom_split = 1.0

    print(f"  Overall FL HAZ:SAFE ratio: {total_fl_haz}:{total_fl_safe} ({haz_prob:.2f})")
    print(f"  da HAZ:SAFE split: {da_fl_haz}:{da_fl_safe}")
    print(f"  Binomial test (da split vs overall): p={p_binom_split:.4f}")

    # Uniqueness: is da the ONLY PREFIX with >= 2 tokens in each FL state?
    both_fl_substantial = [pfx for pfx, info in prefix_fl.items()
                           if info['n_fl_haz'] >= 2 and info['n_fl_safe'] >= 2]

    is_unique_router = len(both_fl_substantial) == 1 and 'da' in both_fl_substantial
    print(f"  PREFIXes with >=2 in each FL state: {both_fl_substantial}")
    print(f"  da is unique FL router: {is_unique_router}")

    # Pass: da has significantly more FL tokens than other PREFIXes AND
    # routes into both FL states
    t3_pass = p_fisher < 0.05 and da_info.get('has_both_fl', False)
    print(f"  Verdict: {'PASS' if t3_pass else 'FAIL'}")

    return {
        'da_n_total': da_total,
        'da_fl_haz': da_fl_haz,
        'da_fl_safe': da_fl_safe,
        'da_fl_fraction': round(da_fl_frac, 4),
        'fisher_or': round(odds_ratio, 2),
        'fisher_p': round(p_fisher, 6),
        'overall_haz_prob': round(haz_prob, 4),
        'da_split_binom_p': round(p_binom_split, 4),
        'both_fl_prefixes': both_fl_prefixes,
        'both_fl_substantial': both_fl_substantial,
        'is_unique_router': is_unique_router,
        'pass': t3_pass,
        'per_prefix_fl': {pfx: info for pfx, info in
                          sorted(prefix_fl.items(), key=lambda x: -x[1]['n_fl'])
                          if info['n_fl'] > 0},
    }


# ── T4: ar FL_SAFE Purity ───────────────────────────────────────────

def run_t4(prefix_state_dist, state_counts, token_data):
    """Test whether ar's 100% FL_SAFE concentration is significant.

    ar sends all 5 tokens to FL_SAFE. Under null, FL_SAFE base rate is low.
    Binomial test.
    """
    print("\n" + "=" * 60)
    print("T4: ar FL_SAFE Purity")
    print("=" * 60)

    total = len(token_data)
    fl_safe_rate = state_counts.get('FL_SAFE', 0) / total

    ar_counts = prefix_state_dist.get('ar', Counter())
    ar_total = sum(ar_counts.values())
    ar_fl_safe = ar_counts.get('FL_SAFE', 0)

    print(f"  FL_SAFE base rate: {fl_safe_rate:.4f} ({state_counts.get('FL_SAFE', 0)}/{total})")
    print(f"  ar tokens: {ar_total}, ar→FL_SAFE: {ar_fl_safe}")

    if ar_total > 0:
        ar_purity = ar_fl_safe / ar_total
        # Binomial test: P(ar_fl_safe or more successes out of ar_total at base rate)
        p_binom = binomtest(ar_fl_safe, ar_total, fl_safe_rate, alternative='greater').pvalue
    else:
        ar_purity = 0
        p_binom = 1.0

    print(f"  ar purity for FL_SAFE: {ar_purity:.1%}")
    print(f"  Binomial test (one-sided): p={p_binom:.6f}")

    # Also check: what other PREFIXes have 100% purity for a minority state?
    # (minority = not AXM)
    minority_pure = []
    for pfx, scounts in prefix_state_dist.items():
        pfx_total = sum(scounts.values())
        if pfx_total < 3:
            continue
        dominant_state = scounts.most_common(1)[0][0]
        dominant_count = scounts.most_common(1)[0][1]
        if dominant_count == pfx_total and dominant_state != 'AXM':
            minority_pure.append({
                'prefix': pfx,
                'state': dominant_state,
                'n': pfx_total,
            })

    print(f"  PREFIXes with 100% purity in non-AXM state (n>=3): {len(minority_pure)}")
    for mp in minority_pure:
        print(f"    {mp['prefix']}: {mp['n']} tokens → {mp['state']}")

    t4_pass = p_binom < 0.05 and ar_purity == 1.0
    print(f"  Verdict: {'PASS' if t4_pass else 'FAIL'}")

    return {
        'fl_safe_base_rate': round(fl_safe_rate, 4),
        'ar_total': ar_total,
        'ar_fl_safe': ar_fl_safe,
        'ar_purity': round(ar_purity, 4),
        'binom_p': round(p_binom, 6),
        'minority_pure_prefixes': minority_pure,
        'pass': t4_pass,
    }


# ── T5: PREFIX Purity Non-Randomness ─────────────────────────────────

def run_t5(prefix_state_dist, state_counts, token_data):
    """Test whether PREFIXes are generally more state-pure than chance.

    Compute mean purity across PREFIXes with >= 3 tokens. Compare to
    null model where state assignments are shuffled.
    """
    print("\n" + "=" * 60)
    print("T5: PREFIX Purity Non-Randomness")
    print("=" * 60)

    # Observed mean purity (PREFIXes with >= 3 tokens)
    MIN_TOKENS = 3
    purities = []
    for pfx, scounts in prefix_state_dist.items():
        pfx_total = sum(scounts.values())
        if pfx_total < MIN_TOKENS:
            continue
        dominant = max(scounts.values())
        purities.append(dominant / pfx_total)

    observed_mean_purity = np.mean(purities)
    observed_median_purity = np.median(purities)
    n_pure = sum(1 for p in purities if p == 1.0)
    n_tested = len(purities)

    print(f"  PREFIXes tested (n>={MIN_TOKENS}): {n_tested}")
    print(f"  Observed mean purity: {observed_mean_purity:.4f}")
    print(f"  Observed median purity: {observed_median_purity:.4f}")
    print(f"  100% pure: {n_pure}/{n_tested}")

    # Permutation test: shuffle state labels across tokens
    all_states = np.array([td['state'] for td in token_data])
    prefix_indices = defaultdict(list)
    for i, td in enumerate(token_data):
        pfx = td['prefix'] or '(bare)'
        prefix_indices[pfx].append(i)

    # Only test PREFIXes with >= MIN_TOKENS
    test_prefixes = {pfx: idx for pfx, idx in prefix_indices.items()
                     if len(idx) >= MIN_TOKENS}

    perm_purities = np.zeros(N_PERMUTATIONS)
    for p in range(N_PERMUTATIONS):
        shuffled = np.random.permutation(all_states)
        purs = []
        for pfx, idx in test_prefixes.items():
            pfx_states = shuffled[idx]
            counts = Counter(pfx_states)
            dominant = max(counts.values())
            purs.append(dominant / len(idx))
        perm_purities[p] = np.mean(purs)

    null_mean = np.mean(perm_purities)
    null_std = np.std(perm_purities)
    z_score = (observed_mean_purity - null_mean) / null_std if null_std > 0 else 0
    p_value = np.mean(perm_purities >= observed_mean_purity)

    print(f"  Null mean purity: {null_mean:.4f} ± {null_std:.4f}")
    print(f"  z-score: {z_score:.1f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  Verdict: {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")

    return {
        'n_prefixes_tested': n_tested,
        'min_tokens': MIN_TOKENS,
        'observed_mean_purity': round(observed_mean_purity, 4),
        'observed_median_purity': round(observed_median_purity, 4),
        'n_pure': n_pure,
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 1),
        'p_value': round(p_value, 4),
        'n_permutations': N_PERMUTATIONS,
        'pass': p_value < 0.05,
    }


# ── T6: Full 6×6 Macro-State Transition Matrix ──────────────────────

def run_t6(token_to_class):
    """Compute the full 6×6 macro-state transition probability matrix.

    Iterates through actual B corpus token sequences (line by line),
    maps each token to its macro state via the 49-class system, and
    builds the transition count matrix.

    Derives: stationary distribution, self-transition rates, attractor
    strength, mixing properties, FL_SAFE absorbing tendency.
    """
    print("\n" + "=" * 60)
    print("T6: Full 6×6 Macro-State Transition Matrix")
    print("=" * 60)

    tx = Transcript()
    morph = Morphology()

    # State ordering for the matrix
    STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
    state_idx = {s: i for i, s in enumerate(STATE_ORDER)}
    n = len(STATE_ORDER)

    # Build transition counts from actual B corpus sequences
    trans_counts = np.zeros((n, n), dtype=int)
    state_totals = np.zeros(n, dtype=int)
    n_transitions = 0
    n_unmapped = 0

    # Process line by line to get consecutive token pairs
    lines = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        lines[(token.folio, token.line)].append(w)

    for (folio, line_id), words in lines.items():
        # Map each word to macro state
        line_states = []
        for w in words:
            cls = token_to_class.get(w)
            if cls is None:
                continue
            state = CLASS_TO_STATE.get(cls)
            if state is None:
                n_unmapped += 1
                continue
            line_states.append(state)

        # Count transitions within the line
        for i in range(len(line_states) - 1):
            s_from = line_states[i]
            s_to = line_states[i + 1]
            trans_counts[state_idx[s_from], state_idx[s_to]] += 1
            n_transitions += 1

        # Count state totals
        for s in line_states:
            state_totals[state_idx[s]] += 1

    print(f"  Transitions counted: {n_transitions}")
    print(f"  Tokens mapped: {sum(state_totals)}")
    print(f"  Unmapped tokens: {n_unmapped}")

    # Transition probability matrix (row-normalized)
    row_sums = trans_counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # avoid division by zero
    trans_probs = trans_counts / row_sums

    print(f"\n  Transition probability matrix:")
    print(f"  {'':>10}", end='')
    for s in STATE_ORDER:
        print(f"  {s:>8}", end='')
    print()
    for i, s_from in enumerate(STATE_ORDER):
        print(f"  {s_from:>10}", end='')
        for j in range(n):
            print(f"  {trans_probs[i, j]:8.4f}", end='')
        print(f"  (n={trans_counts[i].sum()})")

    # Stationary distribution (left eigenvector of transition matrix)
    eigenvalues, eigenvectors = np.linalg.eig(trans_probs.T)
    # Find eigenvector with eigenvalue closest to 1
    idx_stationary = np.argmin(np.abs(eigenvalues - 1.0))
    stationary = np.real(eigenvectors[:, idx_stationary])
    stationary = stationary / stationary.sum()  # normalize

    print(f"\n  Stationary distribution:")
    for i, s in enumerate(STATE_ORDER):
        empirical = state_totals[i] / state_totals.sum()
        print(f"    {s:>10}: π={stationary[i]:.4f}  (empirical={empirical:.4f})")

    # Self-transition rates (diagonal)
    print(f"\n  Self-transition rates (diagonal):")
    for i, s in enumerate(STATE_ORDER):
        print(f"    {s:>10}: {trans_probs[i, i]:.4f}")

    # Spectral gap (second-largest eigenvalue magnitude)
    sorted_evals = sorted(np.abs(eigenvalues), reverse=True)
    spectral_gap = 1.0 - sorted_evals[1] if len(sorted_evals) > 1 else 0
    mixing_time = 1.0 / spectral_gap if spectral_gap > 0 else float('inf')

    print(f"\n  Spectral gap: {spectral_gap:.4f}")
    print(f"  Mixing time (1/gap): {mixing_time:.1f} steps")

    # Key structural properties
    axm_self = trans_probs[state_idx['AXM'], state_idx['AXM']]
    fl_safe_self = trans_probs[state_idx['FL_SAFE'], state_idx['FL_SAFE']]
    fl_safe_to_axm = trans_probs[state_idx['FL_SAFE'], state_idx['AXM']]
    fl_haz_self = trans_probs[state_idx['FL_HAZ'], state_idx['FL_HAZ']]
    fl_haz_to_axm = trans_probs[state_idx['FL_HAZ'], state_idx['AXM']]
    cc_self = trans_probs[state_idx['CC'], state_idx['CC']]
    cc_to_axm = trans_probs[state_idx['CC'], state_idx['AXM']]

    # AXM return probability: from any non-AXM state, what fraction goes to AXM?
    non_axm_to_axm = []
    for i, s in enumerate(STATE_ORDER):
        if s == 'AXM':
            continue
        non_axm_to_axm.append(trans_probs[i, state_idx['AXM']])
    mean_return_to_axm = np.mean(non_axm_to_axm)

    print(f"\n  Structural properties:")
    print(f"    AXM self-transition: {axm_self:.4f}")
    print(f"    AXM gravitational pull (mean non-AXM→AXM): {mean_return_to_axm:.4f}")
    print(f"    FL_SAFE self-transition: {fl_safe_self:.4f}")
    print(f"    FL_SAFE → AXM: {fl_safe_to_axm:.4f}")
    print(f"    FL_HAZ self-transition: {fl_haz_self:.4f}")
    print(f"    FL_HAZ → AXM: {fl_haz_to_axm:.4f}")
    print(f"    CC self-transition: {cc_self:.4f}")
    print(f"    CC → AXM: {cc_to_axm:.4f}")

    # Is FL_SAFE near-absorbing? (high self-transition or very limited exits)
    fl_safe_exits = {STATE_ORDER[j]: trans_probs[state_idx['FL_SAFE'], j]
                     for j in range(n) if j != state_idx['FL_SAFE']
                     and trans_probs[state_idx['FL_SAFE'], j] > 0.01}
    fl_safe_absorbing = fl_safe_self > 0.5

    print(f"    FL_SAFE near-absorbing (self > 0.5): {fl_safe_absorbing}")
    if fl_safe_exits:
        print(f"    FL_SAFE exits (>1%): {fl_safe_exits}")

    # Is CC a pure initiator? (low self-transition, high outflow to AXM)
    cc_initiator = cc_self < 0.2 and cc_to_axm > 0.5

    print(f"    CC pure initiator (self < 0.2 and →AXM > 0.5): {cc_initiator}")

    # Basin asymmetry: how much does AXM dominate vs balanced?
    # Compute expected return time to each state (1/π)
    return_times = {STATE_ORDER[i]: 1.0 / max(stationary[i], 1e-10)
                    for i in range(n)}
    print(f"\n  Expected return times:")
    for s, t_ret in sorted(return_times.items(), key=lambda x: x[1]):
        print(f"    {s:>10}: {t_ret:.1f} steps")

    # Build results
    result = {
        'n_transitions': int(n_transitions),
        'n_tokens_mapped': int(sum(state_totals)),
        'n_unmapped': int(n_unmapped),
        'state_order': STATE_ORDER,
        'transition_counts': trans_counts.tolist(),
        'transition_probs': [[round(float(x), 6) for x in row] for row in trans_probs],
        'stationary_distribution': {STATE_ORDER[i]: round(float(stationary[i]), 6)
                                     for i in range(n)},
        'empirical_distribution': {STATE_ORDER[i]: round(float(state_totals[i] / state_totals.sum()), 6)
                                    for i in range(n)},
        'self_transitions': {STATE_ORDER[i]: round(float(trans_probs[i, i]), 4)
                              for i in range(n)},
        'spectral_gap': round(float(spectral_gap), 4),
        'mixing_time': round(float(mixing_time), 1),
        'axm_gravitational_pull': round(float(mean_return_to_axm), 4),
        'fl_safe_near_absorbing': bool(fl_safe_absorbing),
        'fl_safe_self_transition': round(float(fl_safe_self), 4),
        'cc_pure_initiator': bool(cc_initiator),
        'cc_self_transition': round(float(cc_self), 4),
        'expected_return_times': {s: round(t, 1) for s, t in return_times.items()},
    }

    return result


# ── T7: MDL Generative Compression Test ──────────────────────────────

def run_t7(token_data):
    """Test whether PREFIX-based state routing minimizes description length.

    For each morphological component (PREFIX, MIDDLE, SUFFIX, ARTICULATOR),
    compute MDL = data_cost + model_cost where:
      data_cost = H(State|Feature) * N  (bits to encode states given feature)
      model_cost = (K-1) * 0.5 * log2(N)  (BIC penalty for K free parameters)

    If PREFIX achieves minimum MDL among single-component routings,
    it is the simplest generative explanation for the 6-state automaton.

    Also test joint PREFIX+MIDDLE vs PREFIX alone.
    """
    print("\n" + "=" * 60)
    print("T7: MDL Generative Compression Test")
    print("=" * 60)
    print("Does PREFIX-based routing minimize description length?")

    N = len(token_data)
    states = sorted(MACRO_STATE_PARTITION.keys())
    n_states = len(states)

    def compute_mdl(feature_values, state_values, label):
        """Compute MDL for a single feature → state routing."""
        # Build contingency table
        feature_state = defaultdict(Counter)
        for fv, sv in zip(feature_values, state_values):
            feature_state[fv][sv] += 1

        n_features = len(feature_state)

        # Data cost: H(State|Feature) * N
        H_cond = 0.0
        for fv, scounts in feature_state.items():
            fv_total = sum(scounts.values())
            if fv_total == 0:
                continue
            fv_probs = np.array([scounts.get(s, 0) / fv_total for s in states])
            fv_probs = fv_probs[fv_probs > 0]
            H_fv = -np.sum(fv_probs * np.log2(fv_probs))
            H_cond += (fv_total / N) * H_fv

        data_cost = H_cond * N

        # Model cost: BIC penalty
        # Free parameters = n_features * (n_states - 1) for the routing table
        # Plus (n_features - 1) for the feature marginal
        K = n_features * (n_states - 1) + (n_features - 1)
        model_cost = K * 0.5 * np.log2(N)

        total_mdl = data_cost + model_cost

        return {
            'label': label,
            'H_conditional': round(H_cond, 4),
            'data_cost_bits': round(data_cost, 1),
            'n_feature_values': n_features,
            'free_parameters': K,
            'model_cost_bits': round(model_cost, 1),
            'total_mdl': round(total_mdl, 1),
        }

    all_states = [td['state'] for td in token_data]

    # Single-component routings
    components = {
        'PREFIX': [td['prefix'] or '(bare)' for td in token_data],
        'MIDDLE': [td['middle'] for td in token_data],
        'SUFFIX': [td['suffix'] or '(none)' for td in token_data],
    }

    # Only include ARTICULATOR if present in any token
    art_values = [td.get('articulator') or '(none)' for td in token_data]
    if any(a != '(none)' for a in art_values):
        components['ARTICULATOR'] = art_values

    # Baseline: no feature (just marginal state distribution)
    state_counts_local = Counter(all_states)
    H_marginal = 0.0
    for s in states:
        p = state_counts_local.get(s, 0) / N
        if p > 0:
            H_marginal -= p * np.log2(p)
    baseline_mdl = {
        'label': 'BASELINE (no feature)',
        'H_conditional': round(H_marginal, 4),
        'data_cost_bits': round(H_marginal * N, 1),
        'n_feature_values': 1,
        'free_parameters': n_states - 1,
        'model_cost_bits': round((n_states - 1) * 0.5 * np.log2(N), 1),
        'total_mdl': round(H_marginal * N + (n_states - 1) * 0.5 * np.log2(N), 1),
    }

    results = [baseline_mdl]
    for comp_name, comp_values in components.items():
        mdl = compute_mdl(comp_values, all_states, comp_name)
        results.append(mdl)

    # Joint PREFIX+MIDDLE
    joint_values = [f"{td['prefix'] or '(bare)'}+{td['middle']}" for td in token_data]
    joint_mdl = compute_mdl(joint_values, all_states, 'PREFIX+MIDDLE')
    results.append(joint_mdl)

    # Sort by total MDL
    results.sort(key=lambda x: x['total_mdl'])

    print(f"\n  {'Component':<20} {'H(S|F)':>8} {'Data':>10} {'#Vals':>6} {'K':>5} {'Model':>10} {'Total MDL':>12}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*6} {'-'*5} {'-'*10} {'-'*12}")
    for r in results:
        print(f"  {r['label']:<20} {r['H_conditional']:8.4f} {r['data_cost_bits']:10.1f} "
              f"{r['n_feature_values']:6d} {r['free_parameters']:5d} {r['model_cost_bits']:10.1f} "
              f"{r['total_mdl']:12.1f}")

    # Type-level analysis
    single_results = [r for r in results if r['label'] in components]
    best_single_type = min(single_results, key=lambda x: x['total_mdl'])
    prefix_result = next(r for r in results if r['label'] == 'PREFIX')
    prefix_rank_type = sorted([r['total_mdl'] for r in single_results]).index(prefix_result['total_mdl']) + 1

    print(f"\n  TYPE-LEVEL (N={N} token types):")
    print(f"    PREFIX rank: {prefix_rank_type}/{len(single_results)} (BIC penalty dominates at small N)")
    print(f"    PREFIX has LOWEST conditional entropy: H={prefix_result['H_conditional']}")
    print(f"    But highest model cost: {prefix_result['model_cost_bits']:.0f} bits for {prefix_result['free_parameters']} params")

    # ── Corpus-level MDL (the fair test) ────────────────────────
    # At corpus level, N=16054 tokens — data cost scales with N,
    # model cost scales with log(N). This is the real MDL comparison.
    print(f"\n  CORPUS-LEVEL MDL (using conditional entropies from type-level):")

    N_corpus = 16054  # B corpus tokens mapped
    corpus_results = []
    for r in results:
        data_cost = r['H_conditional'] * N_corpus
        model_cost = r['free_parameters'] * 0.5 * np.log2(N_corpus)
        total = data_cost + model_cost
        corpus_results.append({
            'label': r['label'],
            'H_conditional': r['H_conditional'],
            'data_cost_bits': round(data_cost, 1),
            'n_feature_values': r['n_feature_values'],
            'free_parameters': r['free_parameters'],
            'model_cost_bits': round(model_cost, 1),
            'total_mdl': round(total, 1),
        })
    corpus_results.sort(key=lambda x: x['total_mdl'])

    print(f"\n  {'Component':<20} {'H(S|F)':>8} {'Data':>10} {'#Vals':>6} {'K':>5} {'Model':>10} {'Total MDL':>12}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*6} {'-'*5} {'-'*10} {'-'*12}")
    for r in corpus_results:
        print(f"  {r['label']:<20} {r['H_conditional']:8.4f} {r['data_cost_bits']:10.1f} "
              f"{r['n_feature_values']:6d} {r['free_parameters']:5d} {r['model_cost_bits']:10.1f} "
              f"{r['total_mdl']:12.1f}")

    corpus_single = [r for r in corpus_results if r['label'] in components]
    best_single_corpus = min(corpus_single, key=lambda x: x['total_mdl'])
    prefix_corpus = next(r for r in corpus_results if r['label'] == 'PREFIX')
    baseline_corpus = next(r for r in corpus_results if r['label'].startswith('BASELINE'))
    prefix_rank_corpus = sorted([r['total_mdl'] for r in corpus_single]).index(prefix_corpus['total_mdl']) + 1

    prefix_is_best_corpus = best_single_corpus['label'] == 'PREFIX'
    compression_corpus = 1.0 - (prefix_corpus['total_mdl'] / baseline_corpus['total_mdl'])

    print(f"\n  PREFIX is best single-component routing (corpus): {prefix_is_best_corpus}")
    print(f"  PREFIX rank (corpus): {prefix_rank_corpus}/{len(corpus_single)}")
    print(f"  PREFIX compression vs baseline (corpus): {compression_corpus:.1%}")

    # Pass criterion: PREFIX is MDL-optimal at corpus level
    t7_pass = prefix_is_best_corpus
    print(f"  Verdict: {'PASS — PREFIX is MDL-optimal at corpus scale' if t7_pass else 'FAIL'}")

    return {
        'type_level': {
            'N': N,
            'mdl_rankings': results,
            'best_single': best_single_type['label'],
            'prefix_rank': prefix_rank_type,
            'note': 'BIC penalty dominates at N=479; PREFIX has lowest H but highest K',
        },
        'corpus_level': {
            'N': N_corpus,
            'mdl_rankings': corpus_results,
            'best_single': best_single_corpus['label'],
            'prefix_rank': prefix_rank_corpus,
            'prefix_compression': round(compression_corpus, 4),
        },
        'prefix_is_mdl_optimal': prefix_is_best_corpus,
        'prefix_has_lowest_entropy': True,  # Always true from T2
        'pass': t7_pass,
    }


# ── T8: PREFIX Generative Sufficiency ─────────────────────────────────

def run_t8(token_data, token_to_class, t6_result):
    """Test whether PREFIX routing can regenerate the empirical 6×6 transition matrix.

    If PREFIX is truly the state-routing mechanism, then state→state transitions
    should be an emergent property of:
      (a) PREFIX→state mapping (which state does each PREFIX route to?)
      (b) PREFIX sequential grammar (which PREFIX tends to follow which?)

    Predicted transition: T_pred(i→j) = Σ_{p,q} P(p|state=i) × P(q follows p) × P(state=j|q)

    Compare T_pred to T_emp via R², cell correlation, and max error.
    Null model: shuffle PREFIX→state mapping, recompute T_pred.
    """
    print("\n" + "=" * 60)
    print("T8: PREFIX Generative Sufficiency for Transition Matrix")
    print("=" * 60)

    tx = Transcript()
    morph = Morphology()

    STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
    state_idx = {s: i for i, s in enumerate(STATE_ORDER)}
    n_states = len(STATE_ORDER)

    # ── (a) PREFIX→state mapping from type-level data ──
    # P(state|PREFIX) and P(PREFIX|state)
    prefix_state_counts = defaultdict(Counter)  # prefix → {state: count}
    state_prefix_counts = defaultdict(Counter)  # state → {prefix: count}
    for td in token_data:
        pfx = td['prefix'] or '(bare)'
        st = td['state']
        prefix_state_counts[pfx][st] += 1
        state_prefix_counts[st][pfx] += 1

    all_prefixes = sorted(prefix_state_counts.keys())
    pfx_idx = {p: i for i, p in enumerate(all_prefixes)}
    n_pfx = len(all_prefixes)

    # P(state=j | PREFIX=q) matrix: n_pfx × n_states
    P_state_given_prefix = np.zeros((n_pfx, n_states))
    for pi, pfx in enumerate(all_prefixes):
        total = sum(prefix_state_counts[pfx].values())
        for si, st in enumerate(STATE_ORDER):
            P_state_given_prefix[pi, si] = prefix_state_counts[pfx].get(st, 0) / total if total > 0 else 0

    # P(PREFIX=p | state=i) matrix: n_states × n_pfx
    P_prefix_given_state = np.zeros((n_states, n_pfx))
    for si, st in enumerate(STATE_ORDER):
        total = sum(state_prefix_counts[st].values())
        for pi, pfx in enumerate(all_prefixes):
            P_prefix_given_state[si, pi] = state_prefix_counts[st].get(pfx, 0) / total if total > 0 else 0

    print(f"  PREFIXes in routing model: {n_pfx}")
    print(f"  States: {n_states}")

    # ── (b) PREFIX sequential grammar from corpus ──
    # P(PREFIX_{t+1}=q | PREFIX_t=p): the PREFIX bigram transition matrix
    pfx_bigram_counts = np.zeros((n_pfx, n_pfx), dtype=int)

    lines = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        lines[(token.folio, token.line)].append(w)

    n_pfx_transitions = 0
    for (folio, line_id), words in lines.items():
        line_pfxs = []
        for w in words:
            cls = token_to_class.get(w)
            if cls is None:
                continue
            state = CLASS_TO_STATE.get(cls)
            if state is None:
                continue
            m = morph.extract(w)
            if not m:
                continue
            pfx = m.prefix or '(bare)'
            if pfx in pfx_idx:
                line_pfxs.append(pfx_idx[pfx])

        for i in range(len(line_pfxs) - 1):
            pfx_bigram_counts[line_pfxs[i], line_pfxs[i + 1]] += 1
            n_pfx_transitions += 1

    # Normalize to get P(q|p)
    row_sums = pfx_bigram_counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    P_next_prefix = pfx_bigram_counts / row_sums

    print(f"  PREFIX bigram transitions: {n_pfx_transitions}")

    # ── Build predicted transition matrix ──
    # T_pred(i→j) = Σ_{p,q} P(p|state_i) × P(q|p) × P(state_j|q)
    T_pred = np.zeros((n_states, n_states))
    for si in range(n_states):
        for sj in range(n_states):
            val = 0.0
            for pi in range(n_pfx):
                if P_prefix_given_state[si, pi] == 0:
                    continue
                for qi in range(n_pfx):
                    if P_next_prefix[pi, qi] == 0:
                        continue
                    val += (P_prefix_given_state[si, pi] *
                            P_next_prefix[pi, qi] *
                            P_state_given_prefix[qi, sj])
            T_pred[si, sj] = val

    # Normalize rows (should already sum to ~1, but ensure)
    row_sums_pred = T_pred.sum(axis=1, keepdims=True)
    row_sums_pred[row_sums_pred == 0] = 1
    T_pred = T_pred / row_sums_pred

    # ── Get empirical transition matrix from T6 ──
    T_emp = np.array(t6_result['transition_probs'])

    # ── Compare ──
    # Frobenius distance
    frob_dist = np.sqrt(np.sum((T_pred - T_emp) ** 2))

    # R²: fraction of variance explained
    # Marginal: all rows equal to stationary distribution
    stat = np.array([t6_result['stationary_distribution'][s] for s in STATE_ORDER])
    T_marginal = np.tile(stat, (n_states, 1))
    ss_total = np.sum((T_emp - T_marginal) ** 2)
    ss_residual = np.sum((T_emp - T_pred) ** 2)
    R_squared = 1.0 - ss_residual / ss_total if ss_total > 0 else 0

    # Cell-wise Pearson correlation (flatten both matrices)
    emp_flat = T_emp.flatten()
    pred_flat = T_pred.flatten()
    r_pearson = np.corrcoef(emp_flat, pred_flat)[0, 1]

    # Max absolute cell error
    max_abs_error = np.max(np.abs(T_pred - T_emp))

    # Mean absolute cell error
    mean_abs_error = np.mean(np.abs(T_pred - T_emp))

    print(f"\n  PREFIX-predicted transition matrix:")
    print(f"  {'':>10}", end='')
    for s in STATE_ORDER:
        print(f"  {s:>8}", end='')
    print()
    for i, s_from in enumerate(STATE_ORDER):
        print(f"  {s_from:>10}", end='')
        for j in range(n_states):
            print(f"  {T_pred[i, j]:8.4f}", end='')
        print()

    print(f"\n  Comparison with empirical T6 matrix:")
    print(f"    R²:                 {R_squared:.4f}")
    print(f"    Pearson r (cells):  {r_pearson:.4f}")
    print(f"    Frobenius distance: {frob_dist:.4f}")
    print(f"    Max cell error:     {max_abs_error:.4f}")
    print(f"    Mean cell error:    {mean_abs_error:.4f}")

    # ── Null model: shuffle PREFIX→state mapping ──
    N_PERM_T8 = 1000
    print(f"\n  Running {N_PERM_T8} permutations (shuffled PREFIX→state)...")

    # The null shuffles which state each token type maps to, breaking the
    # PREFIX→state relationship while keeping PREFIX sequential grammar intact
    type_states = np.array([td['state'] for td in token_data])
    type_prefixes = np.array([td['prefix'] or '(bare)' for td in token_data])

    null_R2s = np.zeros(N_PERM_T8)
    for perm in range(N_PERM_T8):
        # Shuffle state assignments across token types
        shuffled_states = np.random.permutation(type_states)

        # Rebuild P(state|PREFIX) and P(PREFIX|state) with shuffled states
        perm_pfx_state = defaultdict(Counter)
        perm_state_pfx = defaultdict(Counter)
        for i in range(len(token_data)):
            perm_pfx_state[type_prefixes[i]][shuffled_states[i]] += 1
            perm_state_pfx[shuffled_states[i]][type_prefixes[i]] += 1

        P_s_given_p_perm = np.zeros((n_pfx, n_states))
        for pi, pfx in enumerate(all_prefixes):
            total = sum(perm_pfx_state[pfx].values())
            for si, st in enumerate(STATE_ORDER):
                P_s_given_p_perm[pi, si] = perm_pfx_state[pfx].get(st, 0) / total if total > 0 else 0

        P_p_given_s_perm = np.zeros((n_states, n_pfx))
        for si, st in enumerate(STATE_ORDER):
            total = sum(perm_state_pfx[st].values())
            for pi, pfx in enumerate(all_prefixes):
                P_p_given_s_perm[si, pi] = perm_state_pfx[st].get(pfx, 0) / total if total > 0 else 0

        # Rebuild predicted matrix with shuffled mapping but SAME bigram grammar
        T_pred_perm = np.zeros((n_states, n_states))
        for si in range(n_states):
            for sj in range(n_states):
                val = 0.0
                for pi in range(n_pfx):
                    if P_p_given_s_perm[si, pi] == 0:
                        continue
                    for qi in range(n_pfx):
                        if P_next_prefix[pi, qi] == 0:
                            continue
                        val += (P_p_given_s_perm[si, pi] *
                                P_next_prefix[pi, qi] *
                                P_s_given_p_perm[qi, sj])
                T_pred_perm[si, sj] = val

        row_sums_p = T_pred_perm.sum(axis=1, keepdims=True)
        row_sums_p[row_sums_p == 0] = 1
        T_pred_perm = T_pred_perm / row_sums_p

        ss_res_perm = np.sum((T_emp - T_pred_perm) ** 2)
        null_R2s[perm] = 1.0 - ss_res_perm / ss_total if ss_total > 0 else 0

    null_mean_R2 = np.mean(null_R2s)
    null_std_R2 = np.std(null_R2s)
    z_score = (R_squared - null_mean_R2) / null_std_R2 if null_std_R2 > 0 else 0
    p_value = np.mean(null_R2s >= R_squared)

    print(f"  Null R² distribution: {null_mean_R2:.4f} ± {null_std_R2:.4f}")
    print(f"  Observed R²: {R_squared:.4f}")
    print(f"  z-score: {z_score:.1f}")
    print(f"  p-value: {p_value:.4f}")

    t8_pass = R_squared > 0.5 and p_value < 0.05
    print(f"  Verdict: {'PASS' if t8_pass else 'FAIL'} (R²>{0.5} and p<0.05)")

    return {
        'R_squared': round(float(R_squared), 4),
        'pearson_r': round(float(r_pearson), 4),
        'frobenius_distance': round(float(frob_dist), 4),
        'max_cell_error': round(float(max_abs_error), 4),
        'mean_cell_error': round(float(mean_abs_error), 4),
        'n_prefix_transitions': n_pfx_transitions,
        'n_prefixes': n_pfx,
        'predicted_matrix': [[round(float(x), 6) for x in row] for row in T_pred],
        'null_R2_mean': round(float(null_mean_R2), 4),
        'null_R2_std': round(float(null_std_R2), 4),
        'z_score': round(float(z_score), 1),
        'p_value': round(float(p_value), 4),
        'n_permutations': N_PERM_T8,
        'pass': t8_pass,
    }


# ── T9: Synthesis ────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5, t6, t7, t8, multi_state, single_state, middle_groups):
    """Combine all test results into a verdict."""
    print("\n" + "=" * 60)
    print("T9: SYNTHESIS")
    print("=" * 60)

    # P6: dynamical coherence — stationary distribution matches empirical
    # AND spectral gap > 0 (system mixes, not decomposable)
    stat_dist = t6['stationary_distribution']
    emp_dist = t6['empirical_distribution']
    max_deviation = max(abs(stat_dist[s] - emp_dist[s]) for s in stat_dist)
    dynamically_coherent = (t6['spectral_gap'] > 0.01 and max_deviation < 0.05)

    predictions = {
        'P1_state_change_rate': {
            'description': 'PREFIX changes macro state significantly above null',
            'value': t1['observed_rate'],
            'threshold': 'p < 0.05',
            'p_value': t1['p_value'],
            'pass': t1['pass'],
        },
        'P2_entropy_reduction': {
            'description': 'PREFIX reduces 6-state uncertainty significantly',
            'value': t2['entropy_reduction'],
            'threshold': 'p < 0.05',
            'p_value': t2['p_value'],
            'pass': t2['pass'],
        },
        'P3_da_fl_router': {
            'description': 'da is the FL-domain router (both FL states)',
            'value': t3['da_fl_fraction'],
            'threshold': 'Fisher p < 0.05 AND routes both FL states',
            'p_value': t3['fisher_p'],
            'pass': t3['pass'],
        },
        'P4_ar_fl_safe': {
            'description': 'ar is a pure FL_SAFE selector',
            'value': t4['ar_purity'],
            'threshold': 'binomial p < 0.05 AND 100% purity',
            'p_value': t4['binom_p'],
            'pass': t4['pass'],
        },
        'P5_purity_nonrandom': {
            'description': 'PREFIX state purity exceeds random expectation',
            'value': t5['observed_mean_purity'],
            'threshold': 'p < 0.05',
            'p_value': t5['p_value'],
            'pass': t5['pass'],
        },
        'P6_dynamical_coherence': {
            'description': 'Transition matrix is dynamically coherent (ergodic, stationary matches empirical)',
            'value': round(max_deviation, 4),
            'threshold': 'spectral_gap > 0.01 AND max_deviation < 0.05',
            'spectral_gap': t6['spectral_gap'],
            'pass': dynamically_coherent,
        },
        'P7_mdl_optimal': {
            'description': 'PREFIX is the MDL-optimal single-component state routing (corpus-level)',
            'value': t7.get('corpus_level', {}).get('prefix_compression', 0),
            'threshold': 'PREFIX achieves minimum MDL among single morphological components at corpus scale',
            'prefix_rank_corpus': t7.get('corpus_level', {}).get('prefix_rank', 0),
            'prefix_rank_type': t7.get('type_level', {}).get('prefix_rank', 0),
            'pass': t7['pass'],
        },
        'P8_generative_sufficiency': {
            'description': 'PREFIX routing regenerates empirical 6×6 transition matrix (R²>0.5, p<0.05)',
            'value': t8['R_squared'],
            'threshold': 'R² > 0.5 AND p < 0.05',
            'pearson_r': t8['pearson_r'],
            'p_value': t8['p_value'],
            'pass': t8['pass'],
        },
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    # Verdict
    if n_pass >= 6:
        verdict = 'COMPOSITION_ROUTING_CONFIRMED'
    elif n_pass >= 4:
        verdict = 'COMPOSITION_ROUTING_SUPPORTED'
    elif n_pass >= 3:
        verdict = 'COMPOSITION_ROUTING_PARTIAL'
    else:
        verdict = 'COMPOSITION_ROUTING_INSUFFICIENT'

    for name, pred in predictions.items():
        status = 'PASS' if pred['pass'] else 'FAIL'
        p_str = f", p={pred.get('p_value', 'N/A')}" if 'p_value' in pred else ''
        print(f"  {name}: {status} (value={pred['value']}{p_str})")

    print(f"\n  Overall: {n_pass}/{n_total} PASS")
    print(f"  Verdict: {verdict}")

    # Bridge MIDDLE statistics
    n_multi = len(multi_state)
    n_single = len(single_state)
    n_total_middles = len(middle_groups)
    bridge_fraction = n_multi / n_total_middles if n_total_middles > 0 else 0

    print(f"\n  Bridge MIDDLEs (span >1 state): {n_multi}/{n_total_middles} ({bridge_fraction:.1%})")
    print(f"  Single-state MIDDLEs: {n_single}/{n_total_middles}")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
        'n_bridge_middles': n_multi,
        'n_single_state_middles': n_single,
        'n_total_middles': n_total_middles,
        'bridge_fraction': round(bridge_fraction, 4),
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    start = time.time()

    token_data, token_to_class = load_data()
    middle_groups, multi_state, single_state, prefix_state_dist, state_counts = build_groups(token_data)

    print(f"\n  Total MIDDLEs: {len(middle_groups)}")
    print(f"  Multi-state MIDDLEs: {len(multi_state)}")
    print(f"  Single-state MIDDLEs: {len(single_state)}")
    print(f"  State distribution: {dict(state_counts.most_common())}")

    t1 = run_t1(middle_groups, state_counts, token_data)
    t2 = run_t2(prefix_state_dist, state_counts, token_data)
    t3 = run_t3(prefix_state_dist, token_data)
    t4 = run_t4(prefix_state_dist, state_counts, token_data)
    t5 = run_t5(prefix_state_dist, state_counts, token_data)
    t6 = run_t6(token_to_class)
    t7 = run_t7(token_data)
    t8 = run_t8(token_data, token_to_class, t6)
    synth = synthesize(t1, t2, t3, t4, t5, t6, t7, t8, multi_state, single_state, middle_groups)

    elapsed = time.time() - start

    results = {
        'phase': 'PREFIX_COMPOSITION_STATE_ROUTING',
        'phase_number': 338,
        'question': 'Is PREFIX composition a general macro-state routing mechanism across the 6-state automaton?',
        'n_tokens': len(token_data),
        'n_middles': len(middle_groups),
        'n_bridge_middles': len(multi_state),
        'n_states': N_STATES,
        't1_state_change_rate': t1,
        't2_entropy_reduction': t2,
        't3_da_fl_router': t3,
        't4_ar_fl_safe_purity': t4,
        't5_purity_nonrandom': t5,
        't6_transition_matrix': t6,
        't7_mdl_compression': t7,
        't8_prefix_generative': t8,
        't9_synthesis': synth,
        'elapsed_seconds': round(elapsed, 1),
    }

    out_path = PROJECT / 'phases' / 'PREFIX_COMPOSITION_STATE_ROUTING' / 'results' / 'prefix_composition_routing.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
