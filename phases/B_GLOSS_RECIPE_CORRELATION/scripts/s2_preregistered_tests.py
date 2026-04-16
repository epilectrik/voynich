"""
Phase 641, Script 2: Pre-registered hypothesis tests.

Runs all 22 blocks-A-G hypotheses from PLAN.md in a single pass. Writes results
as a scorecard JSON. All regex patterns and predictions are LOCKED — no peeking
at feature data before running.

Block summary:
  A1-A6: PREFIX glosses (qo, ch, sh, ok, ot, da)
  B1-B4: Suffix function (-aiin/-ain, -dy, -y, -am)
  C1-C6: SOLID atoms (d, t, l, o, c, p)
  D1-D2: LOCKED atom drift (a, n)
  E1-E3: PLAUSIBLE atoms (r, f, s) — expect INCONCLUSIVE
  G1:    m-terminal (C1434-1439 TRANSITION category)
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from s1_shared_validation import (
    MATCHED_PAIRS, folio_profile, recipe_feature_profile,
    run_test, bh_fdr,
)

OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'preregistered_tests.json')

# ============================================================
# BUILD FOLIO x RECIPE DATA MATRIX
# ============================================================
print("Building folio and recipe profiles...")
pairs_data = []
for folio, part, num, tier, desc in MATCHED_PAIRS:
    fp = folio_profile(folio)
    rp = recipe_feature_profile(part, num)
    if fp is None or rp is None:
        print(f"  SKIP {folio}: missing profile")
        continue
    pairs_data.append({
        'folio': folio, 'part': part, 'num': num, 'tier': tier, 'desc': desc,
        'folio_profile': fp, 'recipe_profile': rp,
    })
print(f"  {len(pairs_data)} complete pairs")

# Helper: extract a column of values across pairs
def folio_values(key_path, data=pairs_data):
    """e.g., key_path=('prefix_rate','qo') or ('head_atom_rate','k')."""
    out = []
    for p in data:
        node = p['folio_profile']
        val = node
        for k in key_path:
            if isinstance(val, dict):
                val = val.get(k, 0)
            else:
                val = 0
        out.append(val if isinstance(val, (int, float)) else 0)
    return out

def recipe_values(feature_name, rate=False, data=pairs_data):
    """e.g., feature_name='heat_mode_count' (or with rate=True -> heat_mode_count__rate)."""
    key = feature_name + ('__rate' if rate else '')
    out = []
    for p in data:
        feats = p['recipe_profile']['features']
        out.append(feats.get(key, feats.get(feature_name, 0)))
    return out

def labels(data=pairs_data):
    return [p['folio'] for p in data]

# ============================================================
# PRE-REGISTERED TESTS (LOCKED)
# ============================================================
tests_config = []

# ---- Block A: PREFIX glosses ----
tests_config.extend([
    ('A1_qo_heat', ('prefix_rate', 'qo'), 'heat_mode_count', '+', True),
    ('A2_ch_check', ('prefix_rate', 'ch'),
     None, '+', True),  # custom: ch vs (monitoring + heat_transition)
    ('A3_sh_monitor', ('prefix_rate', 'sh'), 'monitoring_count', '+', True),
    ('A4_ok_vessel', ('prefix_rate', 'ok'), 'vessel_count', '+', True),
    ('A5_ot_transfer', ('prefix_rate', 'ot'), 'transfer_count', '+', True),
    ('A6_da_material', ('prefix_rate', 'da'), 'material_addition_count', '+', True),
])

# ---- Block B: Suffix function ----
tests_config.extend([
    ('B1_aiin_sealing', ('suffix_rate', 'iin'), 'sealing_count', '+', True),  # -ain/-aiin
    ('B1b_aiin_vessel', ('suffix_rate', 'iin'), 'vessel_count', '+', True),
    ('B2_dy_iteration', ('suffix_rate', 'dy'), 'iteration_count', '+', True),
    ('B3a_dy_termination', ('compound_term_rate', 'dy'), 'termination_count', '+', True),
    ('B3b_ey_termination', ('compound_term_rate', 'ey'), 'termination_count', '+', True),
    ('B3c_hy_termination', ('compound_term_rate', 'hy'), 'termination_count', '+', True),
    ('B4_am_transition', ('suffix_rate', 'am'), 'transition_count', '+', True),
])

# ---- Block C: SOLID atoms ----
tests_config.extend([
    ('C1_d_execute', ('atom_rate', 'd'), 'material_addition_count', '+', True),
    ('C2_t_transfer', ('atom_rate', 't'), 'transfer_count', '+', True),
    ('C3_l_state_inverse', ('atom_rate', 'l'), 'heat_transition_count', '-', True),
    ('C4_o_arrange', ('atom_rate', 'o'), 'vessel_count', '+', True),
    ('C5_c_adjust', ('atom_rate', 'c'), 'heat_transition_count', '+', True),
    ('C6_p_pause', ('atom_rate', 'p'), 'termination_count', '+', True),
])

# ---- Block D: LOCKED atom drift check (no demotion) ----
tests_config.extend([
    ('D1_a_yield_inverse', ('atom_rate', 'a'), 'termination_count', '-', True),
    ('D2_n_halt_inverse', ('atom_rate', 'n'), 'iteration_count', '-', True),
])

# ---- Block E: PLAUSIBLE atoms (expect INCONCLUSIVE) ----
tests_config.extend([
    ('E1_r_respond', ('atom_rate', 'r'), 'monitoring_count', '+', True),
    ('E2_f_flag', ('atom_rate', 'f'), 'termination_count', '+', True),
    ('E3_s_sequence', ('atom_rate', 's'), 'iteration_count', '+', True),
])

# ---- Block G: m-terminal ----
tests_config.extend([
    ('G1_m_terminal_transition', ('term_atom_rate', 'm'), 'transition_count', '+', True),
])

# Custom tests with composite features
CUSTOM_TESTS = {
    'A2_ch_check': {
        'folio_key': ('prefix_rate', 'ch'),
        'recipe_fn': lambda p: p['recipe_profile']['features'].get('monitoring_count', 0) +
                               p['recipe_profile']['features'].get('heat_transition_count', 0),
        'predicted_sign': '+',
    },
    'A1b_qo_composite_heat': {  # extra test with rate normalization
        'folio_key': ('prefix_rate', 'qo'),
        'recipe_fn': lambda p: p['recipe_profile']['features'].get('heat_mode_count__rate', 0),
        'predicted_sign': '+',
    },
}

# ============================================================
# RUN
# ============================================================
print(f"\nRunning {len(tests_config)} pre-registered + {len(CUSTOM_TESTS)} custom tests...")

results = []
for label, folio_key, recipe_feature, predicted_sign, use_rate in tests_config:
    # Handle custom tests
    if label in CUSTOM_TESTS:
        cfg = CUSTOM_TESTS[label]
        fv = folio_values(cfg['folio_key'])
        rv = [cfg['recipe_fn'](p) for p in pairs_data]
        predicted = cfg['predicted_sign']
    else:
        fv = folio_values(folio_key)
        rv = recipe_values(recipe_feature, rate=use_rate)
        predicted = predicted_sign

    # Skip if all zeros on either side
    if sum(fv) == 0 or sum(rv) == 0:
        results.append({
            'label': label,
            'verdict': 'SKIPPED_ZERO',
            'folio_sum': sum(fv),
            'recipe_sum': sum(rv),
        })
        continue

    result = run_test(label, fv, rv, labels(), predicted, n_perm=10000, n_boot=1000)
    result['folio_values'] = fv
    result['recipe_values'] = rv
    results.append(result)

# Also run the extra A1b custom
for label, cfg in CUSTOM_TESTS.items():
    if label == 'A2_ch_check': continue  # already inside main loop
    fv = folio_values(cfg['folio_key'])
    rv = [cfg['recipe_fn'](p) for p in pairs_data]
    if sum(fv) == 0 or sum(rv) == 0:
        results.append({'label': label, 'verdict': 'SKIPPED_ZERO'})
        continue
    result = run_test(label, fv, rv, labels(), cfg['predicted_sign'], n_perm=10000, n_boot=1000)
    result['folio_values'] = fv
    result['recipe_values'] = rv
    results.append(result)

# ============================================================
# BH-FDR CORRECTION
# ============================================================
valid = [r for r in results if 'verdict' in r and r['verdict'] != 'SKIPPED_ZERO' and 'p' in r]
pvals = [r['p'] for r in valid]
fdr_accept = bh_fdr(pvals, q=0.10)
for r, accept in zip(valid, fdr_accept):
    r['fdr_accept'] = accept

# ============================================================
# PRINT SUMMARY
# ============================================================
print(f"\n{'='*95}")
print(f"RESULTS  (n_pairs={len(pairs_data)}, BH-FDR q=0.10)")
print(f"{'='*95}")
print(f"{'Label':<30} {'ρ':>7} {'p':>8} {'Verdict':<14} {'CI':>18} {'LOO':>6} {'FDR':>5}")
print('-' * 95)
for r in results:
    if r.get('verdict') == 'SKIPPED_ZERO':
        print(f"{r['label']:<30} {'—':>7} {'—':>8} {'SKIPPED_ZERO':<14}")
        continue
    rho = r.get('rho', 0)
    p = r.get('p', 1)
    verdict = r.get('verdict', '?')
    ci = r.get('bootstrap_ci', [0, 0])
    loo = 'Y' if r.get('loo_stable') else 'N'
    fdr = 'Y' if r.get('fdr_accept') else 'N'
    ci_str = f"[{ci[0]:+.2f},{ci[1]:+.2f}]"
    print(f"{r['label']:<30} {rho:>+.3f} {p:>.4f}  {verdict:<14} {ci_str:>18} {loo:>6} {fdr:>5}")

# Count verdicts
from collections import Counter
verdict_counts = Counter(r.get('verdict', '?') for r in results)
print(f"\nVerdict tally: {dict(verdict_counts)}")
print(f"FDR-accepted (q=0.10): {sum(1 for r in valid if r.get('fdr_accept'))}/{len(valid)}")
print(f"CI excludes zero: {sum(1 for r in valid if r.get('ci_excludes_zero'))}/{len(valid)}")
print(f"LOO-stable: {sum(1 for r in valid if r.get('loo_stable'))}/{len(valid)}")

# ============================================================
# Save JSON
# ============================================================
out = {
    'metadata': {
        'phase': 641,
        'script': 's2_preregistered_tests',
        'n_pairs': len(pairs_data),
        'n_tests': len(results),
        'fdr_q': 0.10,
        'p_threshold_directional': 0.05,
        'pair_labels': labels(),
    },
    'results': results,
    'verdict_counts': dict(verdict_counts),
}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nWrote {OUT_PATH}")
