"""
Script 5: Internal Structure Tests for CC, FL, FQ

Within-role differentiation tests. For each role:
- Kruskal-Wallis H-test across feature dimensions
- Pairwise J-S divergence between classes
- Role-specific hypotheses (Class 17/12, hazard vs safe, Class 9 anomaly)
- Verdict: GENUINE_STRUCTURE / PARTIAL_STRUCTURE / COLLAPSED
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
CENSUS = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_census.json'
FEATURES = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_features.json'
RESULTS = BASE / 'phases/SMALL_ROLE_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

with open(CENSUS) as f:
    census = json.load(f)
with open(FEATURES) as f:
    feat_data = json.load(f)

# Role definitions
CC_FINAL = set(census['resolved_roles']['CC']['classes'])
FL_FINAL = set(census['resolved_roles']['FL']['classes'])
FQ_FINAL = set(census['resolved_roles']['FQ']['classes'])

def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except Exception:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    else:
        return 'RECIPE'

# Build per-token data for statistical tests
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'folio': token.folio,
    })

# Per-class position samples (for Kruskal-Wallis)
class_positions = defaultdict(list)
class_regimes = defaultdict(list)
class_sections = defaultdict(list)

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n == 0:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls is None:
            continue
        pos = i / (n - 1) if n > 1 else 0.5
        class_positions[cls].append(pos)
        class_regimes[cls].append(folio_regime.get(folio, 'UNKNOWN'))
        class_sections[cls].append(get_section(folio))

print("=" * 70)
print("INTERNAL STRUCTURE TESTS: CC, FL, FQ")
print("=" * 70)

# ============================================================
# KRUSKAL-WALLIS TESTS
# ============================================================

def kruskal_wallis_test(feature_name, groups, group_labels):
    """Run Kruskal-Wallis test. Returns H, p, effect_size (eta-squared)."""
    # Filter out empty groups
    valid = [(g, l) for g, l in zip(groups, group_labels) if len(g) >= 5]
    if len(valid) < 2:
        return None, None, None, 'insufficient_groups'

    valid_groups = [g for g, l in valid]
    valid_labels = [l for g, l in valid]

    # Check for constant values
    all_vals = np.concatenate(valid_groups)
    if np.std(all_vals) < 1e-10:
        return None, None, None, 'constant'

    H, p = stats.kruskal(*valid_groups)
    # Eta-squared effect size
    N = len(all_vals)
    k = len(valid_groups)
    eta2 = (H - k + 1) / (N - k) if N > k else 0

    return H, p, eta2, 'ok'

def js_divergence(dist1, dist2, categories):
    """Jensen-Shannon divergence between two distributions."""
    p = np.array([dist1.get(c, 0) for c in categories], dtype=float)
    q = np.array([dist2.get(c, 0) for c in categories], dtype=float)
    p_sum = p.sum()
    q_sum = q.sum()
    if p_sum == 0 or q_sum == 0:
        return None
    p = p / p_sum
    q = q / q_sum
    return float(jensenshannon(p, q) ** 2)  # squared for proper divergence

results = {}

for role_name, role_classes in [('CC', CC_FINAL), ('FL', FL_FINAL), ('FQ', FQ_FINAL)]:
    print(f"\n{'='*70}")
    print(f"{role_name} INTERNAL STRUCTURE")
    print(f"{'='*70}")

    active_classes = [cls for cls in sorted(role_classes) if len(class_positions.get(cls, [])) >= 5]
    all_classes_list = sorted(role_classes)

    print(f"\nClasses: {all_classes_list}")
    print(f"Active classes (>=5 tokens): {active_classes}")

    if len(active_classes) < 2:
        print(f"  INSUFFICIENT ACTIVE CLASSES for differentiation tests")
        results[role_name] = {
            'classes': all_classes_list,
            'active_classes': active_classes,
            'verdict': 'INSUFFICIENT_DATA',
            'note': f'Only {len(active_classes)} active class(es)'
        }
        continue

    # ---- KRUSKAL-WALLIS TESTS ----
    print(f"\n--- KRUSKAL-WALLIS TESTS ---")
    kw_results = {}
    sig_count = 0
    total_tests = 0

    # Position
    pos_groups = [np.array(class_positions[cls]) for cls in active_classes]
    H, p, eta2, status = kruskal_wallis_test('position', pos_groups, active_classes)
    if status == 'ok':
        sig = p < 0.05
        if sig: sig_count += 1
        total_tests += 1
        print(f"  Position: H={H:.1f}, p={p:.2e}, eta2={eta2:.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        kw_results['position'] = {'H': round(H, 2), 'p': float(p), 'eta2': round(eta2, 4), 'significant': sig}
    else:
        print(f"  Position: {status}")

    # Initial rate (binary per-token: is this token line-initial?)
    init_groups = []
    for cls in active_classes:
        cls_init = []
        for (folio, line_id), line_toks in lines.items():
            if not line_toks:
                continue
            for i, tok in enumerate(line_toks):
                if tok['class'] == cls:
                    cls_init.append(1.0 if i == 0 else 0.0)
        init_groups.append(np.array(cls_init))

    H, p, eta2, status = kruskal_wallis_test('initial_rate', init_groups, active_classes)
    if status == 'ok':
        sig = p < 0.05
        if sig: sig_count += 1
        total_tests += 1
        print(f"  Initial rate: H={H:.1f}, p={p:.2e}, eta2={eta2:.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        kw_results['initial_rate'] = {'H': round(H, 2), 'p': float(p), 'eta2': round(eta2, 4), 'significant': sig}
    else:
        print(f"  Initial rate: {status}")

    # Final rate
    final_groups = []
    for cls in active_classes:
        cls_final = []
        for (folio, line_id), line_toks in lines.items():
            n = len(line_toks)
            if n == 0:
                continue
            for i, tok in enumerate(line_toks):
                if tok['class'] == cls:
                    cls_final.append(1.0 if i == n - 1 else 0.0)
        final_groups.append(np.array(cls_final))

    H, p, eta2, status = kruskal_wallis_test('final_rate', final_groups, active_classes)
    if status == 'ok':
        sig = p < 0.05
        if sig: sig_count += 1
        total_tests += 1
        print(f"  Final rate: H={H:.1f}, p={p:.2e}, eta2={eta2:.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        kw_results['final_rate'] = {'H': round(H, 2), 'p': float(p), 'eta2': round(eta2, 4), 'significant': sig}
    else:
        print(f"  Final rate: {status}")

    # Token length (per occurrence, from types)
    class_to_tokens_list = defaultdict(list)
    for tok, cls in token_to_class.items():
        class_to_tokens_list[cls].append(tok)

    len_groups = []
    for cls in active_classes:
        cls_lens = []
        for (folio, line_id), line_toks in lines.items():
            for tok in line_toks:
                if tok['class'] == cls:
                    cls_lens.append(len(tok['word']))
        len_groups.append(np.array(cls_lens) if cls_lens else np.array([0]))

    H, p, eta2, status = kruskal_wallis_test('token_length', len_groups, active_classes)
    if status == 'ok':
        sig = p < 0.05
        if sig: sig_count += 1
        total_tests += 1
        print(f"  Token length: H={H:.1f}, p={p:.2e}, eta2={eta2:.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        kw_results['token_length'] = {'H': round(H, 2), 'p': float(p), 'eta2': round(eta2, 4), 'significant': sig}
    else:
        print(f"  Token length: {status}")

    # ---- PAIRWISE J-S DIVERGENCE ----
    print(f"\n--- PAIRWISE J-S DIVERGENCE ---")
    REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    SECTIONS = ['HERBAL', 'PHARMA', 'BIO', 'RECIPE']

    # Build per-class distributions
    class_regime_dist = {}
    class_section_dist = {}
    for cls in active_classes:
        class_regime_dist[cls] = Counter(class_regimes[cls])
        class_section_dist[cls] = Counter(class_sections[cls])

    js_results = {}
    for i, c1 in enumerate(active_classes):
        for j, c2 in enumerate(active_classes):
            if j <= i:
                continue
            js_regime = js_divergence(class_regime_dist[c1], class_regime_dist[c2], REGIMES)
            js_section = js_divergence(class_section_dist[c1], class_section_dist[c2], SECTIONS)
            pair_key = f"{c1}-{c2}"
            js_results[pair_key] = {
                'regime': round(js_regime, 4) if js_regime is not None else None,
                'section': round(js_section, 4) if js_section is not None else None
            }
            js_r_str = f"{js_regime:.4f}" if js_regime is not None else 'N/A'
            js_s_str = f"{js_section:.4f}" if js_section is not None else 'N/A'
            print(f"  {c1} vs {c2}: JS_regime={js_r_str}, JS_section={js_s_str}")

    # ---- ROLE-SPECIFIC HYPOTHESES ----
    print(f"\n--- ROLE-SPECIFIC HYPOTHESES ---")

    role_specific = {}

    if role_name == 'CC':
        # Class 12 is never instantiated, so it's really a 2-class role
        print(f"  H1: Is Class 12 (k) a ghost class? (zero corpus tokens)")
        n12 = len(class_positions.get(12, []))
        print(f"    Class 12 tokens: {n12}")
        print(f"    VERDICT: Class 12 is GHOST (defined but not instantiated, C540)")

        # Are 10 and 11 genuinely different?
        if 10 in active_classes and 11 in active_classes:
            pos_10 = np.array(class_positions[10])
            pos_11 = np.array(class_positions[11])
            U, p_mann = stats.mannwhitneyu(pos_10, pos_11, alternative='two-sided')
            print(f"\n  H2: Are Class 10 (daiin) and Class 11 (ol) positionally different?")
            print(f"    Class 10 mean pos: {pos_10.mean():.3f} (n={len(pos_10)})")
            print(f"    Class 11 mean pos: {pos_11.mean():.3f} (n={len(pos_11)})")
            print(f"    Mann-Whitney U={U:.0f}, p={p_mann:.2e}")
            print(f"    VERDICT: {'DIFFERENT' if p_mann < 0.01 else 'NOT DIFFERENT'}")
            role_specific['class_10_vs_11_position'] = {
                'U': float(U), 'p': float(p_mann),
                'mean_10': round(pos_10.mean(), 4),
                'mean_11': round(pos_11.mean(), 4),
                'different': p_mann < 0.01
            }

        role_specific['class_12_ghost'] = True

    elif role_name == 'FL':
        # Do hazard classes (7, 30) form a subgroup vs non-hazard (38, 40)?
        haz_cls = sorted(FL_FINAL & {7, 30})
        safe_cls = sorted(FL_FINAL & {38, 40})

        print(f"  H1: Do hazard classes {haz_cls} differ from safe classes {safe_cls}?")

        # Position comparison
        haz_pos = np.concatenate([np.array(class_positions[c]) for c in haz_cls if class_positions[c]])
        safe_pos = np.concatenate([np.array(class_positions[c]) for c in safe_cls if class_positions[c]])

        if len(haz_pos) >= 5 and len(safe_pos) >= 5:
            U, p_mann = stats.mannwhitneyu(haz_pos, safe_pos, alternative='two-sided')
            print(f"    Hazard mean pos: {haz_pos.mean():.3f} (n={len(haz_pos)})")
            print(f"    Safe mean pos: {safe_pos.mean():.3f} (n={len(safe_pos)})")
            print(f"    Mann-Whitney U={U:.0f}, p={p_mann:.2e}")
            print(f"    VERDICT: {'DIFFERENT' if p_mann < 0.01 else 'NOT DIFFERENT'}")
            role_specific['hazard_vs_safe_position'] = {
                'U': float(U), 'p': float(p_mann),
                'mean_hazard': round(float(haz_pos.mean()), 4),
                'mean_safe': round(float(safe_pos.mean()), 4),
                'different': p_mann < 0.01
            }

        # Final rate comparison
        haz_final = np.concatenate([np.array(final_groups[active_classes.index(c)]) for c in haz_cls if c in active_classes])
        safe_final = np.concatenate([np.array(final_groups[active_classes.index(c)]) for c in safe_cls if c in active_classes])
        if len(haz_final) >= 5 and len(safe_final) >= 5:
            U2, p2 = stats.mannwhitneyu(haz_final, safe_final, alternative='two-sided')
            print(f"    Hazard final rate: {haz_final.mean()*100:.1f}% (n={len(haz_final)})")
            print(f"    Safe final rate: {safe_final.mean()*100:.1f}% (n={len(safe_final)})")
            print(f"    Mann-Whitney U={U2:.0f}, p={p2:.2e}")
            role_specific['hazard_vs_safe_final'] = {
                'U': float(U2), 'p': float(p2),
                'hazard_final_rate': round(float(haz_final.mean()), 4),
                'safe_final_rate': round(float(safe_final.mean()), 4),
                'different': p2 < 0.01
            }

    elif role_name == 'FQ':
        # Does Class 9 (aiin, o, or) differ from {13, 14, 23}?
        cls9_pos = np.array(class_positions.get(9, []))
        other_cls = sorted(FQ_FINAL - {9})
        other_pos = np.concatenate([np.array(class_positions[c]) for c in other_cls if class_positions[c]])

        print(f"  H1: Does Class 9 differ from {other_cls}?")
        if len(cls9_pos) >= 5 and len(other_pos) >= 5:
            U, p_mann = stats.mannwhitneyu(cls9_pos, other_pos, alternative='two-sided')
            print(f"    Class 9 mean pos: {cls9_pos.mean():.3f} (n={len(cls9_pos)})")
            print(f"    Other mean pos: {other_pos.mean():.3f} (n={len(other_pos)})")
            print(f"    Mann-Whitney U={U:.0f}, p={p_mann:.2e}")
            print(f"    VERDICT: {'DIFFERENT' if p_mann < 0.01 else 'NOT DIFFERENT'}")
            role_specific['class9_vs_others_position'] = {
                'U': float(U), 'p': float(p_mann),
                'mean_9': round(float(cls9_pos.mean()), 4),
                'mean_others': round(float(other_pos.mean()), 4),
                'different': p_mann < 0.01
            }

        # Are Classes 13, 14 (ok/ot-prefixed) similar to each other?
        if 13 in active_classes and 14 in active_classes:
            pos_13 = np.array(class_positions[13])
            pos_14 = np.array(class_positions[14])
            U3, p3 = stats.mannwhitneyu(pos_13, pos_14, alternative='two-sided')
            print(f"\n  H2: Are Classes 13 (ok-) and 14 (ot-) positionally similar?")
            print(f"    Class 13 mean pos: {pos_13.mean():.3f} (n={len(pos_13)})")
            print(f"    Class 14 mean pos: {pos_14.mean():.3f} (n={len(pos_14)})")
            print(f"    Mann-Whitney U={U3:.0f}, p={p3:.2e}")
            role_specific['class13_vs_14'] = {
                'U': float(U3), 'p': float(p3),
                'mean_13': round(float(pos_13.mean()), 4),
                'mean_14': round(float(pos_14.mean()), 4),
                'different': p3 < 0.01
            }

    # ---- VERDICT ----
    print(f"\n--- VERDICT ---")
    distinct_fraction = sig_count / total_tests if total_tests > 0 else 0
    print(f"  Significant KW tests: {sig_count}/{total_tests} = {distinct_fraction*100:.0f}%")

    # Check J-S divergences
    js_values = [v['regime'] for v in js_results.values() if v['regime'] is not None]
    js_values += [v['section'] for v in js_results.values() if v['section'] is not None]
    mean_js = np.mean(js_values) if js_values else 0
    print(f"  Mean J-S divergence: {mean_js:.4f}")

    if distinct_fraction >= 0.75 and mean_js > 0.01:
        verdict = 'GENUINE_STRUCTURE'
    elif distinct_fraction >= 0.50 or mean_js > 0.005:
        verdict = 'PARTIAL_STRUCTURE'
    else:
        verdict = 'COLLAPSED'

    # Override for CC with ghost class
    if role_name == 'CC' and role_specific.get('class_12_ghost'):
        if len(active_classes) == 2 and role_specific.get('class_10_vs_11_position', {}).get('different'):
            verdict = 'GENUINE_STRUCTURE (2 active classes + 1 ghost)'
        elif len(active_classes) == 2:
            verdict = 'PARTIAL_STRUCTURE (2 active + 1 ghost, weak separation)'

    print(f"  VERDICT: {verdict}")

    results[role_name] = {
        'classes': all_classes_list,
        'active_classes': active_classes,
        'kruskal_wallis': kw_results,
        'js_divergence': js_results,
        'role_specific': role_specific,
        'distinct_fraction': round(distinct_fraction, 4),
        'mean_js_divergence': round(mean_js, 4),
        'verdict': verdict,
    }

# ============================================================
# CROSS-ROLE SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("CROSS-ROLE SUMMARY")
print(f"{'='*70}")

print(f"\n{'Role':>4} {'Classes':>8} {'Active':>7} {'KW sig%':>8} {'Mean JS':>8} {'Verdict'}")
for role_name in ['CC', 'FL', 'FQ']:
    r = results[role_name]
    print(f"{role_name:>4} {len(r['classes']):>8} {len(r['active_classes']):>7} "
          f"{r.get('distinct_fraction', 0)*100:>7.0f}% {r.get('mean_js_divergence', 0):>8.4f} {r['verdict']}")

# Save
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_internal_structure.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sr_internal_structure.json'}")
