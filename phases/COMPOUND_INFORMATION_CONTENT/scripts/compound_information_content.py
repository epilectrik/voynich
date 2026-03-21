"""
Phase 622: COMPOUND_INFORMATION_CONTENT

Does compound MIDDLE category composition carry information about execution
context beyond what is explained by folio/section-level category pools,
line-position gradients, and PREFIX routing?

Four progressively tighter null models (N0-N3), each removing a known confound
layer, plus a synthetic non-compound control (C0).

Null model hierarchy (weakest -> tightest):
  N0 (global) < N1 (within-folio) < N2 (folio+position) < N3 (folio+PREFIX)
"""

import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import (Transcript, Morphology, MiddleAnalyzer,
                              CategoryClassifier)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}
CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']
RNG = random.Random(42)
N_PERM = 1000


# ============================================================
# Block 1: Build corpus
# ============================================================

def build_corpus():
    """Build per-(folio, line) token lists from Currier B."""
    tx = Transcript()
    morph = Morphology()
    ma = MiddleAnalyzer()
    ma.build_inventory('B')
    cc = CategoryClassifier()

    # line_data[(folio, line)] = list of token dicts
    line_data = defaultdict(list)
    # Per-folio atom pool: folio -> list of (atom, category) for sampling
    folio_atom_pool = defaultdict(list)

    n_total = 0
    n_compound = 0
    n_core = 0
    n_no_middle = 0

    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        if tok.is_label or tok.is_uncertain:
            continue
        if not tok.word.strip():
            continue

        n_total += 1
        m = morph.extract(tok.word)
        if not m.middle or ',' in m.middle or '?' in m.middle:
            n_no_middle += 1
            continue
        # Skip MIDDLEs with unusual characters
        if any(c in m.middle for c in 'jqz'):
            n_no_middle += 1
            continue

        cat = cc.classify(m.middle)
        is_comp = ma.is_compound(m.middle)

        entry = {
            'word': tok.word,
            'middle': m.middle,
            'category': cat,
            'is_compound': is_comp,
            'atoms': [],
            'atom_cats': Counter(),
            'prefix': m.prefix or '',
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
        }

        if is_comp:
            n_compound += 1
            atoms = ma.get_contained_atoms(m.middle)
            entry['atoms'] = atoms
            for atom in atoms:
                ac = cc.classify(atom)
                if ac:
                    entry['atom_cats'][ac] += 1
            # Add atoms to folio pool
            for atom in atoms:
                ac = cc.classify(atom)
                if ac:
                    folio_atom_pool[tok.folio].append((atom, ac))
        else:
            n_core += 1
            # Non-compound atoms also go into folio pool
            if cat:
                folio_atom_pool[tok.folio].append((m.middle, cat))

        line_data[(tok.folio, tok.line)].append(entry)

    # Assign position_in_line
    for key, tokens in line_data.items():
        n = len(tokens)
        for i, t in enumerate(tokens):
            t['position_in_line'] = i
            # Quintile: Q0..Q4
            t['position_quintile'] = min(4, int(5 * i / n)) if n > 0 else 0

    print(f'Corpus: {n_total} total tokens, {n_compound} compound, '
          f'{n_core} core, {n_no_middle} no-middle/filtered')
    print(f'  {len(line_data)} folio-line groups')
    print(f'  {len(folio_atom_pool)} folios with atom pools '
          f'(mean {sum(len(v) for v in folio_atom_pool.values()) / max(1, len(folio_atom_pool)):.0f} atoms/folio)')

    return line_data, folio_atom_pool, ma, cc


# ============================================================
# Block 2: Cosine similarity infrastructure
# ============================================================

def cosine_sim(a, b, keys=CATEGORIES):
    """Cosine similarity between two Counter/dict objects over given keys."""
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(a.get(k, 0)**2 for k in keys))
    mag_b = math.sqrt(sum(b.get(k, 0)**2 for k in keys))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def compute_mean_alignment(pairs):
    """Mean cosine of (atom_cats, context_cats) pairs."""
    if not pairs:
        return 0.0
    return sum(cosine_sim(p['atom_cats'], p['context_cats']) for p in pairs) / len(pairs)


# ============================================================
# Block 3: Build compound-context pairs
# ============================================================

def build_compound_context_pairs(line_data):
    """Build pairs of (compound atom_cats, line context_cats)."""
    pairs = []
    for (folio, line), tokens in line_data.items():
        compounds_on_line = [t for t in tokens if t['is_compound'] and t['atom_cats']]
        non_compounds = [t for t in tokens if not t['is_compound'] and t['category']]

        if not compounds_on_line or not non_compounds:
            continue

        # Context: category distribution of non-compound tokens
        context_cats = Counter()
        for t in non_compounds:
            context_cats[t['category']] += 1

        for t in compounds_on_line:
            pairs.append({
                'atom_cats': dict(t['atom_cats']),
                'context_cats': dict(context_cats),
                'folio': folio,
                'line': line,
                'section': t['section'],
                'position_quintile': t['position_quintile'],
                'prefix': t['prefix'],
                'n_atoms': len(t['atoms']),
                'middle': t['middle'],
            })

    # Stats
    n_atoms_dist = Counter(p['n_atoms'] for p in pairs)
    print(f'\nCompound-context pairs: {len(pairs)}')
    print(f'  n_atoms distribution: {dict(sorted(n_atoms_dist.items()))}')
    print(f'  Folios represented: {len(set(p["folio"] for p in pairs))}')

    return pairs


# ============================================================
# Block 4: N0 -- Global Shuffle Baseline
# ============================================================

def run_permutation_test(pairs, group_key=None, n_perm=N_PERM):
    """
    Run permutation test on compound-context pairs.

    If group_key is None: global shuffle (N0).
    If group_key is a function: shuffle within groups defined by group_key(pair).

    Returns dict with observed, null_mean, null_std, effect_size, p_value.
    """
    observed = compute_mean_alignment(pairs)

    if group_key is None:
        # Global shuffle: permute atom_cats across all pairs
        indices = list(range(len(pairs)))
        null_means = []
        for _ in range(n_perm):
            RNG.shuffle(indices)
            null_val = sum(
                cosine_sim(pairs[indices[i]]['atom_cats'], pairs[i]['context_cats'])
                for i in range(len(pairs))
            ) / len(pairs)
            null_means.append(null_val)
    else:
        # Grouped shuffle: permute atom_cats within groups
        groups = defaultdict(list)
        for i, p in enumerate(pairs):
            groups[group_key(p)].append(i)

        # Count effective groups (size > 1)
        effective_groups = sum(1 for g in groups.values() if len(g) > 1)
        mean_group_size = sum(len(g) for g in groups.values()) / max(1, len(groups))

        null_means = []
        for _ in range(n_perm):
            # Build shuffled index mapping
            shuffled = list(range(len(pairs)))
            for group_indices in groups.values():
                if len(group_indices) > 1:
                    # Shuffle within this group
                    vals = [group_indices[j] for j in range(len(group_indices))]
                    RNG.shuffle(vals)
                    for j, idx in enumerate(group_indices):
                        shuffled[idx] = vals[j]

            null_val = sum(
                cosine_sim(pairs[shuffled[i]]['atom_cats'], pairs[i]['context_cats'])
                for i in range(len(pairs))
            ) / len(pairs)
            null_means.append(null_val)

    null_mean = sum(null_means) / len(null_means)
    null_std = math.sqrt(sum((v - null_mean)**2 for v in null_means) / len(null_means))
    effect_size = (observed - null_mean) / null_std if null_std > 0 else 0
    p_value = sum(1 for v in null_means if v >= observed) / len(null_means)

    result = {
        'observed': round(observed, 6),
        'null_mean': round(null_mean, 6),
        'null_std': round(null_std, 6),
        'effect_size': round(effect_size, 4),
        'p_value': round(p_value, 4),
    }

    if group_key is not None:
        result['n_groups'] = len(groups)
        result['effective_groups'] = effective_groups
        result['mean_group_size'] = round(mean_group_size, 1)

    return result


# ============================================================
# Block 8: C0 -- Synthetic Non-Compound Control
# ============================================================

def run_synthetic_control(pairs, folio_atom_pool, n_resamplings=100):
    """
    For each compound, construct a synthetic control by randomly sampling
    n_atoms atoms from the same folio's atom pool.
    """
    real_mean = compute_mean_alignment(pairs)

    synthetic_means = []
    for _ in range(n_resamplings):
        synthetic_total = 0.0
        n_valid = 0
        for p in pairs:
            pool = folio_atom_pool.get(p['folio'], [])
            if not pool or p['n_atoms'] == 0:
                continue

            # Sample n_atoms atoms from folio pool
            sampled = RNG.choices(pool, k=p['n_atoms'])
            synth_cats = Counter()
            for atom, cat in sampled:
                synth_cats[cat] += 1

            sim = cosine_sim(dict(synth_cats), p['context_cats'])
            synthetic_total += sim
            n_valid += 1

        if n_valid > 0:
            synthetic_means.append(synthetic_total / n_valid)

    synth_mean = sum(synthetic_means) / len(synthetic_means) if synthetic_means else 0
    synth_std = math.sqrt(
        sum((v - synth_mean)**2 for v in synthetic_means) / len(synthetic_means)
    ) if synthetic_means else 0

    difference = real_mean - synth_mean
    effect_size = difference / synth_std if synth_std > 0 else 0

    return {
        'real_mean': round(real_mean, 6),
        'synthetic_mean': round(synth_mean, 6),
        'synthetic_std': round(synth_std, 6),
        'difference': round(difference, 6),
        'effect_size': round(effect_size, 4),
        'n_resamplings': n_resamplings,
        'pass': difference > 2 * synth_std,
    }


# ============================================================
# Block 9: Diagnostics
# ============================================================

def diagnostic_cross_line(pairs, line_data):
    """D1: Compare same-line alignment vs next-line alignment."""
    same_line_sims = []
    next_line_sims = []

    # Build line ordering per folio
    folio_lines = defaultdict(list)
    for (folio, line) in line_data:
        folio_lines[folio].append(line)
    for folio in folio_lines:
        folio_lines[folio] = sorted(set(folio_lines[folio]))

    # Build next-line context
    next_line_context = {}
    for folio, lines in folio_lines.items():
        for i in range(len(lines) - 1):
            curr_line = lines[i]
            next_line = lines[i + 1]
            next_tokens = line_data.get((folio, next_line), [])
            non_comp_next = [t for t in next_tokens if not t['is_compound'] and t['category']]
            if non_comp_next:
                ctx = Counter()
                for t in non_comp_next:
                    ctx[t['category']] += 1
                next_line_context[(folio, curr_line)] = dict(ctx)

    for p in pairs:
        same_sim = cosine_sim(p['atom_cats'], p['context_cats'])
        same_line_sims.append(same_sim)

        nctx = next_line_context.get((p['folio'], p['line']))
        if nctx:
            next_sim = cosine_sim(p['atom_cats'], nctx)
            next_line_sims.append(next_sim)

    same_mean = sum(same_line_sims) / len(same_line_sims) if same_line_sims else 0
    next_mean = sum(next_line_sims) / len(next_line_sims) if next_line_sims else 0
    ratio = next_mean / same_mean if same_mean > 0 else 0

    return {
        'same_line_mean': round(same_mean, 6),
        'next_line_mean': round(next_mean, 6),
        'same_line_n': len(same_line_sims),
        'next_line_n': len(next_line_sims),
        'ratio': round(ratio, 4),
        'interpretation': (
            'folio-mediated (next-line similar to same-line)' if ratio > 0.85
            else 'line-specific (same-line >> next-line)' if ratio < 0.5
            else 'intermediate'
        ),
    }


def diagnostic_compound_rate_entropy(line_data):
    """D2: Per-folio compound rate vs category entropy correlation."""
    folio_stats = defaultdict(lambda: {'compound': 0, 'total': 0, 'cats': Counter()})
    for (folio, line), tokens in line_data.items():
        for t in tokens:
            if t['category']:
                folio_stats[folio]['total'] += 1
                folio_stats[folio]['cats'][t['category']] += 1
                if t['is_compound']:
                    folio_stats[folio]['compound'] += 1

    rates = []
    entropies = []
    for folio, stats in folio_stats.items():
        if stats['total'] < 10:
            continue
        rate = stats['compound'] / stats['total']
        total_cats = sum(stats['cats'].values())
        probs = [v / total_cats for v in stats['cats'].values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        rates.append(rate)
        entropies.append(entropy)

    # Spearman rank correlation
    if len(rates) < 5:
        return {'rho': 0, 'n_folios': len(rates), 'interpretation': 'insufficient data'}

    n = len(rates)
    rank_r = sorted(range(n), key=lambda i: rates[i])
    rank_e = sorted(range(n), key=lambda i: entropies[i])
    rank_r_val = [0] * n
    rank_e_val = [0] * n
    for i, idx in enumerate(rank_r):
        rank_r_val[idx] = i
    for i, idx in enumerate(rank_e):
        rank_e_val[idx] = i

    d_sq = sum((rank_r_val[i] - rank_e_val[i])**2 for i in range(n))
    rho = 1 - 6 * d_sq / (n * (n**2 - 1))

    return {
        'rho': round(rho, 4),
        'n_folios': n,
        'interpretation': (
            f'negative correlation (rho={rho:.3f})' if rho < -0.3
            else f'positive correlation (rho={rho:.3f})' if rho > 0.3
            else f'no correlation (rho={rho:.3f})'
        ),
    }


# ============================================================
# Block 10: Synthesis and Verdict
# ============================================================

def compute_verdict(n0, n1, n2, n3, c0):
    """Determine verdict from test results."""
    p1 = n0['effect_size'] > 2.0
    p2 = n1['effect_size'] > 2.0
    p3 = n3['effect_size'] > 2.0  # N3 = PREFIX-matched (tightest null)
    p4 = c0['pass']  # Real > synthetic by 2*std

    predictions = {
        'P1_global': {'pass': p1, 'effect_size': n0['effect_size'], 'test': 'N0'},
        'P2_within_folio': {'pass': p2, 'effect_size': n1['effect_size'], 'test': 'N1'},
        'P3_prefix_matched': {'pass': p3, 'effect_size': n3['effect_size'], 'test': 'N3'},
        'P4_synthetic_control': {'pass': p4, 'effect_size': c0['effect_size'], 'test': 'C0'},
    }

    if not p1:
        verdict = 'NO_ALIGNMENT'
    elif not p2:
        verdict = 'COMPOSITION_ARTIFACT'
    elif not p3 and not p4:
        verdict = 'POSITION_PREFIX_ARTIFACT'
    elif p2 and (not p3 or not p4):
        verdict = 'COMPOUND_RESIDUAL_SIGNAL'
    else:
        verdict = 'COMPOUND_INFORMATION_SURPLUS'

    return verdict, predictions


# ============================================================
# Main
# ============================================================

def main():
    print('=' * 70)
    print('Phase 622: COMPOUND_INFORMATION_CONTENT')
    print('=' * 70)

    # Build corpus
    print('\n--- Building corpus ---')
    line_data, folio_atom_pool, ma, cc = build_corpus()

    # Build compound-context pairs
    print('\n--- Building compound-context pairs ---')
    pairs = build_compound_context_pairs(line_data)

    if not pairs:
        print('ERROR: No compound-context pairs found')
        return

    # N0: Global shuffle
    print('\n--- N0: Global Shuffle Baseline ---')
    n0 = run_permutation_test(pairs, group_key=None)
    print(f'  Observed: {n0["observed"]:.6f}')
    print(f'  Null: {n0["null_mean"]:.6f} +/- {n0["null_std"]:.6f}')
    print(f'  Effect size: {n0["effect_size"]:.4f}')
    print(f'  p-value: {n0["p_value"]:.4f}')

    # N1: Within-folio shuffle
    print('\n--- N1: Within-Folio Shuffle ---')
    n1 = run_permutation_test(pairs, group_key=lambda p: p['folio'])
    print(f'  Observed: {n1["observed"]:.6f}')
    print(f'  Null: {n1["null_mean"]:.6f} +/- {n1["null_std"]:.6f}')
    print(f'  Effect size: {n1["effect_size"]:.4f}')
    print(f'  p-value: {n1["p_value"]:.4f}')
    print(f'  Groups: {n1["n_groups"]}, effective: {n1["effective_groups"]}, '
          f'mean size: {n1["mean_group_size"]}')
    pct_retained_n1 = (n1['effect_size'] / n0['effect_size'] * 100) if n0['effect_size'] != 0 else 0
    print(f'  Effect retained vs N0: {pct_retained_n1:.1f}%')

    # N2: Position-matched within-folio shuffle
    print('\n--- N2: Position-Matched Within-Folio Shuffle ---')
    n2 = run_permutation_test(pairs, group_key=lambda p: (p['folio'], p['position_quintile']))
    print(f'  Observed: {n2["observed"]:.6f}')
    print(f'  Null: {n2["null_mean"]:.6f} +/- {n2["null_std"]:.6f}')
    print(f'  Effect size: {n2["effect_size"]:.4f}')
    print(f'  p-value: {n2["p_value"]:.4f}')
    print(f'  Groups: {n2["n_groups"]}, effective: {n2["effective_groups"]}, '
          f'mean size: {n2["mean_group_size"]}')
    pct_retained_n2 = (n2['effect_size'] / n0['effect_size'] * 100) if n0['effect_size'] != 0 else 0
    print(f'  Effect retained vs N0: {pct_retained_n2:.1f}%')

    # N3: PREFIX-matched within-folio shuffle
    print('\n--- N3: PREFIX-Matched Within-Folio Shuffle ---')
    n3 = run_permutation_test(pairs, group_key=lambda p: (p['folio'], p['prefix']))
    print(f'  Observed: {n3["observed"]:.6f}')
    print(f'  Null: {n3["null_mean"]:.6f} +/- {n3["null_std"]:.6f}')
    print(f'  Effect size: {n3["effect_size"]:.4f}')
    print(f'  p-value: {n3["p_value"]:.4f}')
    print(f'  Groups: {n3["n_groups"]}, effective: {n3["effective_groups"]}, '
          f'mean size: {n3["mean_group_size"]}')
    pct_retained_n3 = (n3['effect_size'] / n0['effect_size'] * 100) if n0['effect_size'] != 0 else 0
    print(f'  Effect retained vs N0: {pct_retained_n3:.1f}%')

    # C0: Synthetic non-compound control
    print('\n--- C0: Synthetic Non-Compound Control ---')
    c0 = run_synthetic_control(pairs, folio_atom_pool)
    print(f'  Real mean: {c0["real_mean"]:.6f}')
    print(f'  Synthetic mean: {c0["synthetic_mean"]:.6f} +/- {c0["synthetic_std"]:.6f}')
    print(f'  Difference: {c0["difference"]:.6f}')
    print(f'  Effect size: {c0["effect_size"]:.4f}')
    print(f'  PASS (real > synthetic + 2*std): {c0["pass"]}')

    # Diagnostics
    print('\n--- D1: Cross-Line Prediction ---')
    d1 = diagnostic_cross_line(pairs, line_data)
    print(f'  Same-line mean: {d1["same_line_mean"]:.6f} (N={d1["same_line_n"]})')
    print(f'  Next-line mean: {d1["next_line_mean"]:.6f} (N={d1["next_line_n"]})')
    print(f'  Ratio: {d1["ratio"]:.4f}')
    print(f'  Interpretation: {d1["interpretation"]}')

    print('\n--- D2: Compound Rate vs Category Entropy ---')
    d2 = diagnostic_compound_rate_entropy(line_data)
    print(f'  Spearman rho: {d2["rho"]:.4f} (N={d2["n_folios"]} folios)')
    print(f'  Interpretation: {d2["interpretation"]}')

    # Effect cascade
    print('\n--- D3: Effect Cascade Summary ---')
    print(f'  N0 (global):         effect={n0["effect_size"]:7.4f}  p={n0["p_value"]:.4f}  (100.0% retained)')
    print(f'  N1 (within-folio):   effect={n1["effect_size"]:7.4f}  p={n1["p_value"]:.4f}  ({pct_retained_n1:.1f}% retained)')
    print(f'  N2 (folio+position): effect={n2["effect_size"]:7.4f}  p={n2["p_value"]:.4f}  ({pct_retained_n2:.1f}% retained)')
    print(f'  N3 (folio+PREFIX):   effect={n3["effect_size"]:7.4f}  p={n3["p_value"]:.4f}  ({pct_retained_n3:.1f}% retained)')

    # Verdict
    print('\n' + '=' * 70)
    verdict, predictions = compute_verdict(n0, n1, n2, n3, c0)
    print(f'VERDICT: {verdict}')
    print()
    for pname, pdata in predictions.items():
        status = 'PASS' if pdata['pass'] else 'FAIL'
        print(f'  {pname}: {status} (effect={pdata["effect_size"]:.4f}, test={pdata["test"]})')

    # Save results
    results = {
        'phase': 'COMPOUND_INFORMATION_CONTENT',
        'phase_number': 622,
        'question': 'Does compound MIDDLE category composition carry information '
                    'about execution context beyond folio/section pools?',
        'n_pairs': len(pairs),
        'n_folios': len(set(p['folio'] for p in pairs)),
        'n_atoms_distribution': dict(Counter(p['n_atoms'] for p in pairs)),
        'tests': {
            'N0_global_shuffle': n0,
            'N1_within_folio': n1,
            'N2_position_matched': n2,
            'N3_prefix_matched': n3,
            'C0_synthetic_control': c0,
        },
        'diagnostics': {
            'D1_cross_line': d1,
            'D2_compound_rate_entropy': d2,
            'D3_effect_cascade': {
                'N0_pct': 100.0,
                'N1_pct': round(pct_retained_n1, 1),
                'N2_pct': round(pct_retained_n2, 1),
                'N3_pct': round(pct_retained_n3, 1),
            },
        },
        'predictions': predictions,
        'verdict': verdict,
        'verdict_thresholds': {
            'COMPOUND_INFORMATION_SURPLUS': 'P1+P2+P3+P4 all PASS',
            'COMPOUND_RESIDUAL_SIGNAL': 'P1+P2 PASS, P3 or P4 FAIL',
            'POSITION_PREFIX_ARTIFACT': 'P1 PASS + P2 PASS + P3 FAIL + P4 FAIL',
            'COMPOSITION_ARTIFACT': 'P1 PASS + P2 FAIL',
            'NO_ALIGNMENT': 'P1 FAIL',
        },
        'confounds_controlled': {
            'N0': 'none (global shuffle)',
            'N1': 'folio-level category pool (C1176)',
            'N2': 'folio pool + line-position gradient (C1428)',
            'N3': 'folio pool + PREFIX->category routing (C1297/C1300/C1411)',
            'C0': 'compound-specificity via synthetic multi-atom sampling',
        },
        'key_constraints_referenced': [
            'C935', 'C1053', 'C1176', 'C1190', 'C1214',
            'C1297', 'C1300', 'C1411', 'C1428',
        ],
    }

    out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_INFORMATION_CONTENT' / 'results' / 'compound_information_content.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nResults saved to {out_path}')


if __name__ == '__main__':
    main()
