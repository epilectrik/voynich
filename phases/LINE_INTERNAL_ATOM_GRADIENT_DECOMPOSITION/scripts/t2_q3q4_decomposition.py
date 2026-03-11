"""T2: Q3->Q4 Decomposition for Phase 581.

Per-atom JSD contribution to closure step. All four transitions.
Concentration metric and rate change tables.
"""
import json, os, math
from collections import Counter

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

HEADS = ['a', 'e', 'k', 'o', 't', 'headless']
TERMINALS = ['bare', 'h', 'l', 'm', 'n', 'r', 'y']
TRANSITIONS = [(0, 1), (1, 2), (2, 3), (3, 4)]
TRANSITION_NAMES = ['Q0->Q1', 'Q1->Q2', 'Q2->Q3', 'Q3->Q4']


def jsd_decomposed(dist_p, dist_q, labels):
    """Compute JSD and per-atom contributions.

    dist_p, dist_q: dicts {label: count}
    Returns: (total_jsd, {label: contribution})
    """
    total_p = sum(dist_p.get(k, 0) for k in labels) or 1
    total_q = sum(dist_q.get(k, 0) for k in labels) or 1

    contributions = {}
    total_jsd = 0.0
    for k in labels:
        pk = dist_p.get(k, 0) / total_p
        qk = dist_q.get(k, 0) / total_q
        mk = 0.5 * (pk + qk)

        c = 0.0
        if pk > 0 and mk > 0:
            c += 0.5 * pk * math.log2(pk / mk)
        if qk > 0 and mk > 0:
            c += 0.5 * qk * math.log2(qk / mk)
        contributions[k] = c
        total_jsd += c

    return total_jsd, contributions


def gini_coefficient(values):
    """Compute Gini coefficient for a list of non-negative values."""
    n = len(values)
    if n == 0:
        return 0.0
    s = sorted(values)
    total = sum(s)
    if total < 1e-12:
        return 0.0
    cumulative = 0.0
    gini_sum = 0.0
    for i, v in enumerate(s):
        cumulative += v
        gini_sum += cumulative
    return round(1 - 2 * gini_sum / (n * total) + 1 / n, 4)


def cosine_sim(a, b):
    """Cosine similarity between two dicts sharing keys."""
    keys = set(list(a.keys()) + list(b.keys()))
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(a.get(k, 0) ** 2 for k in keys))
    nb = math.sqrt(sum(b.get(k, 0) ** 2 for k in keys))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return round(dot / (na * nb), 4)


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    tokens = t0['tokens']

    # Build quintile-specific distributions
    head_by_q = {q: Counter() for q in range(5)}
    term_by_q = {q: Counter() for q in range(5)}

    for t in tokens:
        q = t['quintile']
        h = t['head'] if t['head'] else 'headless'
        head_by_q[q][h] += 1
        term_by_q[q][t['term']] += 1

    # ---- 2a/2c: Per-atom JSD decomposition for ALL four transitions ----
    all_transitions = {}
    for (q_from, q_to), name in zip(TRANSITIONS, TRANSITION_NAMES):
        head_jsd, head_contribs = jsd_decomposed(head_by_q[q_from], head_by_q[q_to], HEADS)
        term_jsd, term_contribs = jsd_decomposed(term_by_q[q_from], term_by_q[q_to], TERMINALS)

        head_ranked = sorted(head_contribs.items(), key=lambda x: -x[1])
        term_ranked = sorted(term_contribs.items(), key=lambda x: -x[1])

        # Top-1 and top-2 share
        head_vals = sorted(head_contribs.values(), reverse=True)
        term_vals = sorted(term_contribs.values(), reverse=True)
        head_top1_share = head_vals[0] / head_jsd if head_jsd > 1e-12 else 0
        head_top2_share = sum(head_vals[:2]) / head_jsd if head_jsd > 1e-12 else 0
        term_top1_share = term_vals[0] / term_jsd if term_jsd > 1e-12 else 0
        term_top2_share = sum(term_vals[:2]) / term_jsd if term_jsd > 1e-12 else 0

        all_transitions[name] = {
            'head_total_jsd': round(head_jsd, 6),
            'head_contributions': {k: round(v, 6) for k, v in head_ranked},
            'head_top1_share': round(head_top1_share, 4),
            'head_top2_share': round(head_top2_share, 4),
            'head_gini': gini_coefficient(list(head_contribs.values())),
            'term_total_jsd': round(term_jsd, 6),
            'term_contributions': {k: round(v, 6) for k, v in term_ranked},
            'term_top1_share': round(term_top1_share, 4),
            'term_top2_share': round(term_top2_share, 4),
            'term_gini': gini_coefficient(list(term_contribs.values())),
        }

    # ---- 2c extended: Cosine similarity of contribution vectors across transitions ----
    cross_cosines = {}
    q3q4_head = all_transitions['Q3->Q4']['head_contributions']
    q3q4_term = all_transitions['Q3->Q4']['term_contributions']
    for name in TRANSITION_NAMES:
        if name == 'Q3->Q4':
            continue
        other_head = all_transitions[name]['head_contributions']
        other_term = all_transitions[name]['term_contributions']
        cross_cosines[f'Q3Q4_vs_{name}_HEAD'] = cosine_sim(q3q4_head, other_head)
        cross_cosines[f'Q3Q4_vs_{name}_TERM'] = cosine_sim(q3q4_term, other_term)

    # ---- 2d: Rate change tables ----
    head_rate_changes = []
    for h in HEADS:
        total_q3 = sum(head_by_q[3].values())
        total_q4 = sum(head_by_q[4].values())
        rate_q3 = head_by_q[3][h] / total_q3 if total_q3 > 0 else 0
        rate_q4 = head_by_q[4][h] / total_q4 if total_q4 > 0 else 0
        abs_change = rate_q4 - rate_q3
        rel_change = abs_change / rate_q3 if rate_q3 > 1e-8 else 0
        head_rate_changes.append({
            'atom': h,
            'rate_Q3': round(rate_q3, 6),
            'rate_Q4': round(rate_q4, 6),
            'abs_change': round(abs_change, 6),
            'rel_change': round(rel_change, 4),
        })
    head_rate_changes.sort(key=lambda x: -abs(x['abs_change']))

    term_rate_changes = []
    for t_atom in TERMINALS:
        total_q3 = sum(term_by_q[3].values())
        total_q4 = sum(term_by_q[4].values())
        rate_q3 = term_by_q[3][t_atom] / total_q3 if total_q3 > 0 else 0
        rate_q4 = term_by_q[4][t_atom] / total_q4 if total_q4 > 0 else 0
        abs_change = rate_q4 - rate_q3
        rel_change = abs_change / rate_q3 if rate_q3 > 1e-8 else 0
        term_rate_changes.append({
            'atom': t_atom,
            'rate_Q3': round(rate_q3, 6),
            'rate_Q4': round(rate_q4, 6),
            'abs_change': round(abs_change, 6),
            'rel_change': round(rel_change, 4),
        })
    term_rate_changes.sort(key=lambda x: -abs(x['abs_change']))

    # ---- C1672 decision ----
    q3q4 = all_transitions['Q3->Q4']
    head_top2 = q3q4['head_top2_share']
    term_top2 = q3q4['term_top2_share']

    if head_top2 > 0.60 and term_top2 > 0.60:
        verdict = 'CLOSURE_CONCENTRATED'
    elif head_top2 < 0.30 and term_top2 < 0.30:
        verdict = 'CLOSURE_UNIFORM'
    else:
        verdict = 'CLOSURE_DISTRIBUTED'

    output = {
        'metadata': {
            'phase': '581',
            'script': 't2_q3q4_decomposition.py',
            'n_tokens': len(tokens),
        },
        'all_transitions': all_transitions,
        'cross_transition_cosines': cross_cosines,
        'rate_changes': {
            'head_Q3_to_Q4': head_rate_changes,
            'term_Q3_to_Q4': term_rate_changes,
        },
        'C1672': {
            'verdict': verdict,
            'head_top2_share': head_top2,
            'term_top2_share': term_top2,
            'head_gini': q3q4['head_gini'],
            'term_gini': q3q4['term_gini'],
            'q3q4_head_jsd': q3q4['head_total_jsd'],
            'q3q4_term_jsd': q3q4['term_total_jsd'],
            'q3q4_vs_q0q1_head_cosine': cross_cosines.get('Q3Q4_vs_Q0->Q1_HEAD', 0),
            'q3q4_vs_q2q3_head_cosine': cross_cosines.get('Q3Q4_vs_Q2->Q3_HEAD', 0),
            'rationale': (f"HEAD top2={head_top2:.3f}, TERM top2={term_top2:.3f}, "
                          f"HEAD JSD={q3q4['head_total_jsd']:.6f}, "
                          f"TERM JSD={q3q4['term_total_jsd']:.6f}")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't2_q3q4_decomposition.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T2: Q3->Q4 decomposition complete")
    for name in TRANSITION_NAMES:
        tr = all_transitions[name]
        print(f"  {name}: HEAD JSD={tr['head_total_jsd']:.6f}, "
              f"TERM JSD={tr['term_total_jsd']:.6f}")
    print(f"  Q3->Q4 HEAD top contributors: "
          f"{list(all_transitions['Q3->Q4']['head_contributions'].items())[:3]}")
    print(f"  Q3->Q4 TERM top contributors: "
          f"{list(all_transitions['Q3->Q4']['term_contributions'].items())[:3]}")
    print(f"  Cross-transition cosines: {cross_cosines}")
    print(f"  HEAD rate changes (Q3->Q4):")
    for rc in head_rate_changes[:3]:
        print(f"    {rc['atom']}: {rc['rate_Q3']:.4f} -> {rc['rate_Q4']:.4f} "
              f"({rc['abs_change']:+.4f})")
    print(f"  TERM rate changes (Q3->Q4):")
    for rc in term_rate_changes[:3]:
        print(f"    {rc['atom']}: {rc['rate_Q3']:.4f} -> {rc['rate_Q4']:.4f} "
              f"({rc['abs_change']:+.4f})")
    print(f"  C1672: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
