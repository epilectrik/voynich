#!/usr/bin/env python3
"""
Phase 484: POSITION-CONDITIONED CATEGORY GRAMMAR
=================================================
Tests whether 8-category transition grammar varies by line position,
extending M2.1's class-level position-conditioning (C1362) to the
operational category layer.

Tests:
  T1: Category transition position-dependence (chi-squared homogeneity)
  T2: Category gradient profile (frequency by quintile)
  T3: Position-specific mandatory/depleted bigrams
  T4: Section-position interaction (C1047 extension)
  T5: Category self-transition rates by position

Pre-registered predictions:
  P1: MARKING front-depleted after Q1
  P2: THERMAL medially concentrated
  P3: FLOW peaks at line-final (Q5)
  P4: TRANSITION late-line enrichment
  P5: Category self-transition rates vary by position (>=3/8)
  P6: Section-position interaction absent or weak

Depends on: C1362, C1286, C1047, C1287, C556, C562, C1305
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, chi2_contingency
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)
N_QUINTILES = 5

# Section mapping
SECTION_LABELS = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS', 'C': 'COSMO'}


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def quintile_index(pos, line_len):
    """Compute quintile (0-4) for position within line."""
    if line_len <= 1:
        return 2  # midpoint
    frac = pos / (line_len - 1)
    q = int(frac * N_QUINTILES)
    return min(q, N_QUINTILES - 1)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with category assignments and positional info."""
    print("Loading data...")

    morph = Morphology()
    cc = CategoryClassifier()

    # Load section assignments
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        p479 = json.load(f)
    folio_section = {f: d.get('section', 'UNK') for f, d in p479['per_folio'].items()}

    # Collect per-line token sequences with categories
    # Structure: {(folio, line): [(position_in_line, category, section), ...]}
    line_tokens = defaultdict(list)

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        if not cat:
            continue

        section = folio_section.get(token.folio, 'UNK')
        key = (token.folio, token.line)
        line_tokens[key].append((cat, section))

    # Build quintile-assigned token pairs
    # For each line, compute quintile for each token position, then extract adjacent pairs
    global_cat_counts = np.zeros((N_QUINTILES, N_CATS), dtype=int)
    global_trans_counts = np.zeros((N_QUINTILES, N_CATS, N_CATS), dtype=int)
    section_trans_counts = defaultdict(lambda: np.zeros((N_QUINTILES, N_CATS, N_CATS), dtype=int))

    n_lines = 0
    n_tokens = 0
    n_transitions = 0

    for key, tokens in line_tokens.items():
        line_len = len(tokens)
        if line_len < 2:
            continue

        n_lines += 1
        for pos, (cat, section) in enumerate(tokens):
            q = quintile_index(pos, line_len)
            ci = CAT_IDX[cat]
            global_cat_counts[q, ci] += 1
            n_tokens += 1

            # Transition to next token
            if pos < line_len - 1:
                next_cat = tokens[pos + 1][0]
                nci = CAT_IDX[next_cat]
                global_trans_counts[q, ci, nci] += 1
                if section in SECTION_LABELS:
                    section_trans_counts[section][q, ci, nci] += 1
                n_transitions += 1

    print(f"  Lines: {n_lines}, Tokens: {n_tokens}, Transitions: {n_transitions}")
    print(f"  Tokens per quintile: {[int(global_cat_counts[q].sum()) for q in range(N_QUINTILES)]}")

    return {
        'global_cat_counts': global_cat_counts,
        'global_trans_counts': global_trans_counts,
        'section_trans_counts': dict(section_trans_counts),
        'n_lines': n_lines,
        'n_tokens': n_tokens,
        'n_transitions': n_transitions,
    }


# ── Test Functions ───────────────────────────────────────────────────

def test1_position_dependence(data):
    """T1: Category transition position-dependence."""
    print("\n=== T1: Category Transition Position-Dependence ===")

    trans = data['global_trans_counts']  # (5, 8, 8)

    # Global transition matrix (pooled across quintiles)
    global_matrix = trans.sum(axis=0)  # (8, 8)

    # Chi-squared homogeneity test: are quintile transition matrices the same?
    # Flatten each quintile's 8x8 into 64-vector, build 5x64 contingency table
    n_bigrams = N_CATS * N_CATS
    contingency = np.zeros((N_QUINTILES, n_bigrams), dtype=int)
    for q in range(N_QUINTILES):
        contingency[q] = trans[q].flatten()

    # Remove columns that are all-zero (rare bigrams)
    col_sums = contingency.sum(axis=0)
    valid_cols = col_sums > 0
    contingency_valid = contingency[:, valid_cols]

    if contingency_valid.shape[1] > 1:
        chi2, p_val, dof, expected = chi2_contingency(contingency_valid)
        cramers_v = np.sqrt(chi2 / (contingency_valid.sum() * (min(contingency_valid.shape) - 1)))
    else:
        chi2, p_val, dof, cramers_v = 0, 1, 0, 0

    print(f"  Chi-squared homogeneity: chi2={chi2:.1f}, dof={dof}, p={p_val:.6f}")
    print(f"  Cramer's V: {cramers_v:.4f}")

    # JS divergence of each quintile's transition distribution from global
    js_per_quintile = []
    for q in range(N_QUINTILES):
        p_q = trans[q].flatten().astype(float)
        p_g = global_matrix.flatten().astype(float)
        # Normalize
        p_q = p_q / max(p_q.sum(), 1)
        p_g = p_g / max(p_g.sum(), 1)
        # Add epsilon
        eps = 1e-10
        p_q = p_q + eps
        p_g = p_g + eps
        p_q = p_q / p_q.sum()
        p_g = p_g / p_g.sum()
        js = float(jensenshannon(p_q, p_g) ** 2)
        js_per_quintile.append(js)
        print(f"  Q{q+1} JS from global: {js:.6f}")

    position_dependent = p_val < 0.001  # Strong threshold
    print(f"  Position-dependent: {position_dependent}")

    return {
        'chi2': float(chi2),
        'p': float(p_val),
        'dof': int(dof),
        'cramers_v': float(cramers_v),
        'js_per_quintile': js_per_quintile,
        'position_dependent': position_dependent,
    }


def test2_category_gradient(data):
    """T2: Category gradient profile (frequency by quintile)."""
    print("\n=== T2: Category Gradient Profile ===")

    counts = data['global_cat_counts']  # (5, 8)
    # Normalize per quintile
    row_sums = counts.sum(axis=1, keepdims=True)
    fracs = counts / np.maximum(row_sums, 1)

    results = {}
    print(f"  {'Category':15s} {'Q1':>6s} {'Q2':>6s} {'Q3':>6s} {'Q4':>6s} {'Q5':>6s} {'rho':>6s} {'p':>8s}")

    for ci, cat in enumerate(CATEGORIES):
        vals = fracs[:, ci]
        quintiles = np.arange(N_QUINTILES)
        rho, p = spearmanr(quintiles, vals)

        print(f"  {cat:15s} {vals[0]:6.3f} {vals[1]:6.3f} {vals[2]:6.3f} {vals[3]:6.3f} {vals[4]:6.3f} "
              f"{rho:6.3f} {p:8.4f}")

        results[cat] = {
            'quintile_fracs': [float(v) for v in vals],
            'spearman_rho': float(rho),
            'spearman_p': float(p),
            'peak_quintile': int(np.argmax(vals)),
            'trough_quintile': int(np.argmin(vals)),
        }

    # P1: MARKING front-depleted (Q1 vs Q5 ratio > 1.5)
    mk = fracs[:, CAT_IDX['MARKING']]
    p1_ratio = mk[0] / max(mk[4], 1e-10)
    p1 = bool(p1_ratio > 1.5)
    print(f"\n  P1 (MARKING Q1/Q5 > 1.5): {'CONFIRMED' if p1 else 'FALSIFIED'} (ratio={p1_ratio:.2f})")

    # P2: THERMAL medially concentrated (Q2-Q4 mean > Q1 and Q5)
    th = fracs[:, CAT_IDX['THERMAL']]
    th_medial = float(np.mean(th[1:4]))
    p2 = bool(th_medial > th[0] and th_medial > th[4])
    print(f"  P2 (THERMAL medial > edges): {'CONFIRMED' if p2 else 'FALSIFIED'} "
          f"(medial={th_medial:.3f}, Q1={th[0]:.3f}, Q5={th[4]:.3f})")

    # P3: FLOW peaks at Q5, >= 1.5x Q1
    fl = fracs[:, CAT_IDX['FLOW']]
    p3_peak = int(np.argmax(fl)) == 4
    p3_ratio = fl[4] / max(fl[0], 1e-10)
    p3 = bool(p3_peak and p3_ratio >= 1.5)
    print(f"  P3 (FLOW peaks Q5, >=1.5x Q1): {'CONFIRMED' if p3 else 'FALSIFIED'} "
          f"(peak=Q{np.argmax(fl)+1}, ratio={p3_ratio:.2f})")

    # P4: TRANSITION late-enriched (Q4-Q5 mean > Q1-Q2 mean)
    tr = fracs[:, CAT_IDX['TRANSITION']]
    tr_late = float(np.mean(tr[3:5]))
    tr_early = float(np.mean(tr[0:2]))
    p4 = bool(tr_late > tr_early)
    print(f"  P4 (TRANSITION late > early): {'CONFIRMED' if p4 else 'FALSIFIED'} "
          f"(late={tr_late:.3f}, early={tr_early:.3f})")

    results['P1_marking_front'] = p1
    results['P1_ratio'] = float(p1_ratio)
    results['P2_thermal_medial'] = p2
    results['P3_flow_final'] = p3
    results['P4_transition_late'] = p4

    return results


def test3_positional_bigrams(data):
    """T3: Position-specific mandatory/depleted category bigrams."""
    print("\n=== T3: Position-Specific Category Bigrams ===")

    trans = data['global_trans_counts']  # (5, 8, 8)
    global_matrix = trans.sum(axis=0)  # (8, 8)

    # Global bigram rates
    total_global = global_matrix.sum()
    global_rates = global_matrix / max(total_global, 1)

    # Per-quintile rates
    enrichments = {}
    significant_bigrams = []

    for q in range(N_QUINTILES):
        total_q = trans[q].sum()
        if total_q == 0:
            continue
        q_rates = trans[q] / total_q

        for ci, src in enumerate(CATEGORIES):
            for cj, tgt in enumerate(CATEGORIES):
                observed = trans[q, ci, cj]
                expected = global_rates[ci, cj] * total_q
                if expected < 5:
                    continue

                ratio = observed / max(expected, 1e-10)
                bigram_key = f"{src}→{tgt}"

                if bigram_key not in enrichments:
                    enrichments[bigram_key] = {}
                enrichments[bigram_key][f'Q{q+1}'] = {
                    'observed': int(observed),
                    'expected': float(expected),
                    'ratio': float(ratio),
                }

                # Flag highly enriched/depleted (>2x or <0.5x)
                if ratio > 2.0 or ratio < 0.5:
                    significant_bigrams.append((bigram_key, q + 1, ratio, observed))

    # Report top positionally-variant bigrams
    if significant_bigrams:
        significant_bigrams.sort(key=lambda x: abs(x[2] - 1.0), reverse=True)
        print(f"  {len(significant_bigrams)} position-variant bigrams (>2x or <0.5x):")
        for bg, q, ratio, obs in significant_bigrams[:10]:
            direction = 'ENRICHED' if ratio > 1 else 'DEPLETED'
            print(f"    {bg:25s} Q{q}: {direction} {ratio:.2f}x (n={obs})")
    else:
        print(f"  No strongly position-variant bigrams detected")

    return {
        'n_variant_bigrams': len(significant_bigrams),
        'top_variants': [(bg, q, float(ratio), int(obs)) for bg, q, ratio, obs in significant_bigrams[:20]],
    }


def test4_section_position_interaction(data):
    """T4: Section-position interaction test (C1047 extension)."""
    print("\n=== T4: Section-Position Interaction ===")

    # For each section, compute per-quintile transition distribution
    # Test: is section x position interaction significant?
    section_trans = data['section_trans_counts']

    # Compare per-section JS divergence profiles
    section_js_profiles = {}
    for section in sorted(section_trans.keys()):
        if section not in SECTION_LABELS:
            continue
        s_trans = section_trans[section]  # (5, 8, 8)
        s_global = s_trans.sum(axis=0)  # (8, 8)

        js_vals = []
        for q in range(N_QUINTILES):
            p_q = s_trans[q].flatten().astype(float)
            p_g = s_global.flatten().astype(float)
            if p_q.sum() < 10:
                js_vals.append(0.0)
                continue
            eps = 1e-10
            p_q = (p_q + eps) / (p_q + eps).sum()
            p_g = (p_g + eps) / (p_g + eps).sum()
            js = float(jensenshannon(p_q, p_g) ** 2)
            js_vals.append(js)

        section_js_profiles[section] = js_vals
        label = SECTION_LABELS[section]
        print(f"  {label}: JS from section global = "
              f"{', '.join(f'Q{q+1}={js:.5f}' for q, js in enumerate(js_vals))}")

    # Compare JS profiles across sections
    # If interaction exists, sections should have DIFFERENT positional profiles
    # Compute between-section JS profile similarity
    sections_list = sorted(section_js_profiles.keys())
    if len(sections_list) >= 2:
        profile_corrs = []
        for i in range(len(sections_list)):
            for j in range(i + 1, len(sections_list)):
                js_i = np.array(section_js_profiles[sections_list[i]])
                js_j = np.array(section_js_profiles[sections_list[j]])
                if np.std(js_i) > 1e-10 and np.std(js_j) > 1e-10:
                    r, _ = spearmanr(js_i, js_j)
                    profile_corrs.append(r)

        mean_profile_corr = float(np.mean(profile_corrs)) if profile_corrs else 0
        print(f"\n  Mean JS profile correlation between sections: {mean_profile_corr:.3f}")
        # High correlation = sections show SAME positional pattern = additive (no interaction)
        # Low correlation = sections show DIFFERENT positional patterns = interaction
        p6 = bool(mean_profile_corr > 0.3)  # Additive if correlated
        print(f"  P6 (no interaction / additive): {'CONFIRMED' if p6 else 'FALSIFIED'} "
              f"(mean corr={mean_profile_corr:.3f})")
    else:
        mean_profile_corr = None
        p6 = None

    return {
        'section_js_profiles': {s: [float(v) for v in vals]
                                 for s, vals in section_js_profiles.items()},
        'mean_profile_correlation': mean_profile_corr,
        'P6_additive': p6,
    }


def test5_self_transition_by_position(data):
    """T5: Category self-transition rates by position."""
    print("\n=== T5: Self-Transition Rates by Position ===")

    trans = data['global_trans_counts']  # (5, 8, 8)

    results = {}
    sig_count = 0

    print(f"  {'Category':15s} {'Q1':>6s} {'Q2':>6s} {'Q3':>6s} {'Q4':>6s} {'Q5':>6s} {'rho':>6s} {'sig':>4s}")

    for ci, cat in enumerate(CATEGORIES):
        self_rates = []
        for q in range(N_QUINTILES):
            total_from = trans[q, ci, :].sum()
            self_count = trans[q, ci, ci]
            rate = self_count / max(total_from, 1)
            self_rates.append(float(rate))

        rho, p = spearmanr(np.arange(N_QUINTILES), self_rates)
        sig = p < 0.05

        # Also test Q1 vs Q5 difference
        q1_total = trans[0, ci, :].sum()
        q5_total = trans[4, ci, :].sum()
        q1_self = trans[0, ci, ci]
        q5_self = trans[4, ci, ci]

        if q1_total > 10 and q5_total > 10:
            q1_rate = q1_self / q1_total
            q5_rate = q5_self / q5_total
            # Simple z-test for proportions
            pooled = (q1_self + q5_self) / (q1_total + q5_total)
            if pooled > 0 and pooled < 1:
                se = np.sqrt(pooled * (1 - pooled) * (1 / q1_total + 1 / q5_total))
                z = (q1_rate - q5_rate) / max(se, 1e-10)
                from scipy.stats import norm
                p_z = 2 * (1 - norm.cdf(abs(z)))
                sig_prop = p_z < 0.05
            else:
                sig_prop = False
        else:
            sig_prop = False

        if sig or sig_prop:
            sig_count += 1

        marker = '*' if sig else ''
        print(f"  {cat:15s} {self_rates[0]:6.3f} {self_rates[1]:6.3f} {self_rates[2]:6.3f} "
              f"{self_rates[3]:6.3f} {self_rates[4]:6.3f} {rho:6.3f} {marker:>4s}")

        results[cat] = {
            'self_rates': self_rates,
            'spearman_rho': float(rho),
            'spearman_p': float(p),
            'significant': bool(sig or sig_prop),
        }

    # P5: >=3/8 categories have significantly different self-transition rates
    p5 = sig_count >= 3
    print(f"\n  P5 (>=3/8 significant): {'CONFIRMED' if p5 else 'FALSIFIED'} ({sig_count}/8)")

    results['P5_self_rate_variation'] = bool(p5)
    results['significant_count'] = sig_count
    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()

    t1 = test1_position_dependence(data)
    t2 = test2_category_gradient(data)
    t3 = test3_positional_bigrams(data)
    t4 = test4_section_position_interaction(data)
    t5 = test5_self_transition_by_position(data)

    # ── Verdict ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRE-REGISTERED PREDICTION RESULTS:")

    predictions = {
        'P1_marking_front': t2.get('P1_marking_front'),
        'P2_thermal_medial': t2.get('P2_thermal_medial'),
        'P3_flow_final': t2.get('P3_flow_final'),
        'P4_transition_late': t2.get('P4_transition_late'),
        'P5_self_rate_variation': t5.get('P5_self_rate_variation'),
        'P6_additive': t4.get('P6_additive'),
    }

    for pid, result in predictions.items():
        status = 'CONFIRMED' if result is True else 'FALSIFIED' if result is False else 'INCONCLUSIVE'
        print(f"  {pid}: {status}")

    confirmed = sum(1 for v in predictions.values() if v is True)
    falsified = sum(1 for v in predictions.values() if v is False)
    print(f"\n  Score: {confirmed}/6 confirmed, {falsified}/6 falsified")

    # Overall
    pos_dep = t1.get('position_dependent', False)
    cramers = t1.get('cramers_v', 0)
    n_variant = t3.get('n_variant_bigrams', 0)

    verdict = (f"Category transitions ARE position-conditioned (chi2 p={t1['p']:.2e}, V={cramers:.4f}). "
               if pos_dep else
               f"Category transitions are NOT position-conditioned (p={t1['p']:.4f}). ")
    verdict += (f"{n_variant} position-variant bigrams. "
                f"{confirmed}/6 predictions confirmed.")

    print(f"\nVERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save
    results = {
        'metadata': {
            'phase': 484,
            'name': 'POSITION_CONDITIONED_CATEGORY_GRAMMAR',
            'n_tokens': data['n_tokens'],
            'n_transitions': data['n_transitions'],
            'n_lines': data['n_lines'],
            'elapsed_seconds': elapsed,
        },
        'T1_position_dependence': t1,
        'T2_category_gradient': t2,
        'T3_positional_bigrams': t3,
        'T4_section_interaction': t4,
        'T5_self_transitions': t5,
        'predictions': predictions,
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'position_conditioned_category_grammar.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
