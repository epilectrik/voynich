"""T1: Atom Positional Gradients for Phase 581.

HEAD/TERM/MOD x quintile profiles, chi-squared tests, 6 predictions,
gradient heterogeneity, headless internal split, carryover cross-reference.
"""
import json, os, math
from collections import Counter, defaultdict

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

HEADS = ['a', 'e', 'k', 'o', 't', 'headless']
TERMINALS = ['bare', 'h', 'l', 'm', 'n', 'r', 'y']
MODIFIERS = ['c', 'd', 'f', 'i', 'p', 's']
QUINTILES = [0, 1, 2, 3, 4]

# C1208 carryover classes
CARRYOVER = {
    'a': 'POS', 'e': 'NEG', 'k': 'POS', 'o': 'NEU', 't': 'POS',
    'm': 'POS', 'r': 'POS', 'h': 'POS', 'l': 'NEU', 'n': 'NEG',
    'y': 'NEG', 'bare': 'NEU',
    'c': 'POS', 'd': 'NEU', 'f': 'NEU', 'i': 'NEG', 'p': 'POS', 's': 'POS',
}


def chi_squared(table):
    """Chi-squared test on a dict-of-dict contingency table.
    Returns (chi2, df, p_approx).
    """
    rows = sorted(table.keys())
    cols = sorted({c for r in table.values() for c in r})
    n_rows = len(rows)
    n_cols = len(cols)
    if n_rows < 2 or n_cols < 2:
        return (0.0, 0, 1.0)

    # Build matrix
    obs = {}
    row_totals = {}
    col_totals = {c: 0 for c in cols}
    grand_total = 0
    for r in rows:
        row_totals[r] = 0
        for c in cols:
            v = table[r].get(c, 0)
            obs[(r, c)] = v
            row_totals[r] += v
            col_totals[c] += v
            grand_total += v

    if grand_total == 0:
        return (0.0, 0, 1.0)

    chi2 = 0.0
    for r in rows:
        for c in cols:
            expected = row_totals[r] * col_totals[c] / grand_total
            if expected > 0:
                chi2 += (obs[(r, c)] - expected) ** 2 / expected

    df = (n_rows - 1) * (n_cols - 1)

    # p-value approximation using Wilson-Hilferty
    if df == 0:
        p = 1.0
    elif chi2 <= 0:
        p = 1.0
    else:
        z = ((chi2 / df) ** (1 / 3) - 1 + 2 / (9 * df)) / math.sqrt(2 / (9 * df))
        p = 0.5 * math.erfc(z / math.sqrt(2))

    return (round(chi2, 2), df, round(p, 8))


def cosine_sim(a, b):
    """Cosine similarity between two lists."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x ** 2 for x in a))
    norm_b = math.sqrt(sum(x ** 2 for x in b))
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0
    return dot / (norm_a * norm_b)


def build_profiles(tokens, atom_key, atom_labels):
    """Build quintile profiles and enrichment for a given atom dimension.

    Returns:
        contingency: {atom: {quintile: count}}
        rates: {atom: {quintile: rate}}
        enrichment: {atom: {quintile: enrichment}}
        marginal: {atom: marginal_rate}
        quintile_totals: {quintile: total}
    """
    contingency = {a: {q: 0 for q in QUINTILES} for a in atom_labels}
    quintile_totals = {q: 0 for q in QUINTILES}

    for t in tokens:
        q = t['quintile']
        val = t.get(atom_key)
        if val is None:
            val = 'headless'
        if val not in contingency:
            continue
        contingency[val][q] += 1
        quintile_totals[q] += 1

    total = sum(quintile_totals.values())
    marginal = {}
    for a in atom_labels:
        marginal[a] = sum(contingency[a].values()) / total if total > 0 else 0

    rates = {a: {} for a in atom_labels}
    enrichment = {a: {} for a in atom_labels}
    for a in atom_labels:
        for q in QUINTILES:
            qt = quintile_totals[q]
            rate = contingency[a][q] / qt if qt > 0 else 0
            rates[a][q] = round(rate, 6)
            enrichment[a][q] = round(rate / marginal[a], 4) if marginal[a] > 1e-8 else 0
    return contingency, rates, enrichment, marginal, quintile_totals


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    tokens = t0['tokens']
    n = len(tokens)

    # ---- 1a: HEAD quintile profiles ----
    head_cont, head_rates, head_enrich, head_marg, q_totals = \
        build_profiles(tokens, 'head', HEADS)
    head_chi2, head_df, head_p = chi_squared(head_cont)

    # Headless internal split (pseudo-HEAD x quintile)
    headless_tokens = [t for t in tokens if t['head'] is None]
    pseudo_heads_present = sorted(set(t['pseudo_head'] for t in headless_tokens
                                       if t['pseudo_head']))
    pseudo_cont, pseudo_rates, pseudo_enrich, pseudo_marg, pseudo_q_totals = \
        build_profiles(headless_tokens, 'pseudo_head', pseudo_heads_present)
    pseudo_chi2, pseudo_df, pseudo_p = chi_squared(pseudo_cont)

    # ---- 1b: TERMINAL quintile profiles ----
    term_cont, term_rates, term_enrich, term_marg, _ = \
        build_profiles(tokens, 'term', TERMINALS)
    term_chi2, term_df, term_p = chi_squared(term_cont)

    # ---- 1c: MODIFIER quintile profiles ----
    mod_tokens = []
    for t in tokens:
        mods_str = t.get('mods', '')
        for ch in mods_str:
            if ch in set(MODIFIERS):
                mod_tokens.append({'quintile': t['quintile'], 'mod': ch})
    mod_cont, mod_rates, mod_enrich, mod_marg, _ = \
        build_profiles(mod_tokens, 'mod', MODIFIERS)
    mod_chi2, mod_df, mod_p = chi_squared(mod_cont)

    # ---- 1d: Gradient heterogeneity ----
    # HEAD range (max - min rate across quintiles)
    head_ranges = {}
    for a in HEADS:
        vals = [head_rates[a][q] for q in QUINTILES]
        head_ranges[a] = round(max(vals) - min(vals), 6)

    # TERMINAL range
    term_ranges = {}
    for a in TERMINALS:
        vals = [term_rates[a][q] for q in QUINTILES]
        term_ranges[a] = round(max(vals) - min(vals), 6)

    # Pairwise cosine similarity of HEAD quintile profiles
    head_cosines = {}
    min_cosine = 1.0
    for i, a1 in enumerate(HEADS):
        for a2 in HEADS[i + 1:]:
            v1 = [head_rates[a1][q] for q in QUINTILES]
            v2 = [head_rates[a2][q] for q in QUINTILES]
            cs = cosine_sim(v1, v2)
            head_cosines[f'{a1}_vs_{a2}'] = round(cs, 4)
            if cs < min_cosine:
                min_cosine = cs

    # ---- 1e: Six predictions ----
    predictions = {}

    # P1: k-HEAD peaks at Q1
    k_q1_enrich = head_enrich.get('k', {}).get(1, 0)
    k_peak_q = max(QUINTILES, key=lambda q: head_rates.get('k', {}).get(q, 0))
    predictions['P1_k_peaks_Q1'] = {
        'test': 'k enrichment Q1 > 1.15',
        'k_Q1_enrichment': k_q1_enrich,
        'k_peak_quintile': k_peak_q,
        'pass': k_q1_enrich > 1.15
    }

    # P2: e-HEAD peaks at Q0
    e_q0_enrich = head_enrich.get('e', {}).get(0, 0)
    e_peak_q = max(QUINTILES, key=lambda q: head_rates.get('e', {}).get(q, 0))
    predictions['P2_e_peaks_Q0'] = {
        'test': 'e enrichment Q0 > 1.15',
        'e_Q0_enrichment': e_q0_enrich,
        'e_peak_quintile': e_peak_q,
        'pass': e_q0_enrich > 1.15
    }

    # P3: m-terminal concentrated at Q4
    m_q4_enrich = term_enrich.get('m', {}).get(4, 0)
    predictions['P3_m_concentrated_Q4'] = {
        'test': 'm enrichment Q4 > 3.0',
        'm_Q4_enrichment': m_q4_enrich,
        'pass': m_q4_enrich > 3.0
    }

    # P4: headless closure/infrastructural concentration (softened)
    hl_q4_enrich = head_enrich.get('headless', {}).get(4, 0)
    # Check if any pseudo-HEAD subgroup concentrates at Q4
    pseudo_q4_max = 0
    pseudo_q4_atom = None
    for ph in pseudo_heads_present:
        ph_q4 = pseudo_enrich.get(ph, {}).get(4, 0)
        if ph_q4 > pseudo_q4_max:
            pseudo_q4_max = ph_q4
            pseudo_q4_atom = ph
    predictions['P4_headless_closure'] = {
        'test': 'headless enrichment Q4 > 1.15 OR pseudo-HEAD subgroup concentrates',
        'headless_Q4_enrichment': hl_q4_enrich,
        'top_pseudo_head_Q4': pseudo_q4_atom,
        'top_pseudo_head_Q4_enrichment': round(pseudo_q4_max, 4),
        'pass': hl_q4_enrich > 1.15 or pseudo_q4_max > 1.5
    }

    # P5: r-terminal depleted at Q0
    r_q0_enrich = term_enrich.get('r', {}).get(0, 0)
    predictions['P5_r_depleted_Q0'] = {
        'test': 'r enrichment Q0 < 0.85',
        'r_Q0_enrichment': r_q0_enrich,
        'pass': r_q0_enrich < 0.85
    }

    # P6: y-terminal more work-distributed than m/r (softened)
    y_q3q4_change = abs(term_rates.get('y', {}).get(4, 0) - term_rates.get('y', {}).get(3, 0))
    m_q3q4_change = abs(term_rates.get('m', {}).get(4, 0) - term_rates.get('m', {}).get(3, 0))
    predictions['P6_y_work_distributed'] = {
        'test': 'y Q3->Q4 |change| < m Q3->Q4 |change|',
        'y_Q3Q4_abs_change': round(y_q3q4_change, 6),
        'm_Q3Q4_abs_change': round(m_q3q4_change, 6),
        'pass': y_q3q4_change < m_q3q4_change
    }

    predictions_passed = sum(1 for v in predictions.values() if v['pass'])

    # ---- 1f: Gradient magnitude ranking ----
    head_gradient_mag = {a: round(sum(abs(head_rates[a][q] - head_marg[a])
                                       for q in QUINTILES), 6) for a in HEADS}
    term_gradient_mag = {a: round(sum(abs(term_rates[a][q] - term_marg[a])
                                       for q in QUINTILES), 6) for a in TERMINALS}
    mod_gradient_mag = {a: round(sum(abs(mod_rates[a][q] - mod_marg[a])
                                      for q in QUINTILES), 6) for a in MODIFIERS}

    head_ranked = sorted(head_gradient_mag.items(), key=lambda x: -x[1])
    term_ranked = sorted(term_gradient_mag.items(), key=lambda x: -x[1])
    mod_ranked = sorted(mod_gradient_mag.items(), key=lambda x: -x[1])

    # ---- 1g: Carryover cross-reference ----
    top3_head = [a for a, _ in head_ranked[:3]]
    top3_term = [a for a, _ in term_ranked[:3]]
    carryover_xref = {
        'top3_positional_heads': {a: CARRYOVER.get(a, 'N/A') for a in top3_head},
        'top3_positional_terms': {a: CARRYOVER.get(a, 'N/A') for a in top3_term},
    }
    # Check if position-sensitive atoms cluster by carryover class
    all_top = [CARRYOVER.get(a, 'N/A') for a in top3_head + top3_term]
    carryover_dist = Counter(all_top)
    carryover_xref['carryover_distribution'] = dict(carryover_dist)
    dominant_class = carryover_dist.most_common(1)[0] if carryover_dist else ('N/A', 0)
    carryover_xref['dominant_carryover'] = dominant_class[0]
    carryover_xref['dominant_fraction'] = round(dominant_class[1] / len(all_top), 3) if all_top else 0

    # ---- C1671 decision ----
    if head_p < 0.001 and term_p < 0.001 and min_cosine < 0.90:
        verdict = 'GRADIENT_HETEROGENEOUS'
    elif (head_p < 0.001 or term_p < 0.001) and min_cosine >= 0.95:
        verdict = 'GRADIENT_UNIFORM'
    elif head_p >= 0.01 and term_p >= 0.01:
        verdict = 'GRADIENT_ABSENT'
    else:
        verdict = 'GRADIENT_HETEROGENEOUS'  # significant + moderate cosine spread

    output = {
        'metadata': {
            'phase': '581',
            'script': 't1_atom_positional_gradients.py',
            'n_tokens': n,
        },
        'head_profiles': {
            'contingency': {a: {str(q): v for q, v in head_cont[a].items()} for a in HEADS},
            'rates': {a: {str(q): v for q, v in head_rates[a].items()} for a in HEADS},
            'enrichment': {a: {str(q): v for q, v in head_enrich[a].items()} for a in HEADS},
            'marginal': head_marg,
            'chi_squared': head_chi2,
            'df': head_df,
            'p_value': head_p,
            'ranges': head_ranges,
            'gradient_magnitude': dict(head_ranked),
        },
        'headless_internal': {
            'n_headless': len(headless_tokens),
            'pseudo_heads': pseudo_heads_present,
            'rates': {a: {str(q): v for q, v in pseudo_rates[a].items()} for a in pseudo_heads_present},
            'enrichment': {a: {str(q): v for q, v in pseudo_enrich[a].items()} for a in pseudo_heads_present},
            'chi_squared': pseudo_chi2,
            'df': pseudo_df,
            'p_value': pseudo_p,
        },
        'terminal_profiles': {
            'contingency': {a: {str(q): v for q, v in term_cont[a].items()} for a in TERMINALS},
            'rates': {a: {str(q): v for q, v in term_rates[a].items()} for a in TERMINALS},
            'enrichment': {a: {str(q): v for q, v in term_enrich[a].items()} for a in TERMINALS},
            'marginal': term_marg,
            'chi_squared': term_chi2,
            'df': term_df,
            'p_value': term_p,
            'ranges': term_ranges,
            'gradient_magnitude': dict(term_ranked),
        },
        'modifier_profiles': {
            'n_modifier_tokens': len(mod_tokens),
            'rates': {a: {str(q): v for q, v in mod_rates[a].items()} for a in MODIFIERS},
            'enrichment': {a: {str(q): v for q, v in mod_enrich[a].items()} for a in MODIFIERS},
            'marginal': mod_marg,
            'chi_squared': mod_chi2,
            'df': mod_df,
            'p_value': mod_p,
            'gradient_magnitude': dict(mod_ranked),
        },
        'gradient_heterogeneity': {
            'head_pairwise_cosines': head_cosines,
            'min_head_cosine': round(min_cosine, 4),
            'head_range_ratio': round(max(head_ranges.values()) / max(min(head_ranges.values()), 1e-8), 2),
        },
        'predictions': predictions,
        'predictions_passed': predictions_passed,
        'predictions_total': 6,
        'carryover_cross_reference': carryover_xref,
        'C1671': {
            'verdict': verdict,
            'head_chi2': head_chi2,
            'head_p': head_p,
            'term_chi2': term_chi2,
            'term_p': term_p,
            'min_head_cosine': round(min_cosine, 4),
            'rationale': (f"HEAD chi2={head_chi2} p={head_p}, "
                          f"TERM chi2={term_chi2} p={term_p}, "
                          f"min cosine={min_cosine:.4f}")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't1_atom_positional_gradients.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T1: Atom positional gradients complete")
    print(f"  HEAD chi2={head_chi2}, df={head_df}, p={head_p}")
    print(f"  TERM chi2={term_chi2}, df={term_df}, p={term_p}")
    print(f"  MOD  chi2={mod_chi2}, df={mod_df}, p={mod_p}")
    print(f"  Min HEAD pairwise cosine: {min_cosine:.4f}")
    print(f"  HEAD gradient ranking: {head_ranked}")
    print(f"  TERM gradient ranking: {term_ranked}")
    print(f"  Predictions: {predictions_passed}/6 passed")
    for k, v in predictions.items():
        status = 'PASS' if v['pass'] else 'FAIL'
        print(f"    {k}: {status}")
    print(f"  Carryover: dominant={carryover_xref['dominant_carryover']} "
          f"({carryover_xref['dominant_fraction']:.0%})")
    print(f"  C1671: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
