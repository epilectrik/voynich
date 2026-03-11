"""T4: Section-Conditioned Gradients for Phase 581.

Per-section HEAD/TERM quintile profiles, Q3->Q4 step magnitude,
gradient preservation test, section-specific atom signatures.
"""
import json, os, math
from collections import Counter, defaultdict

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

HEADS = ['a', 'e', 'k', 'o', 't', 'headless']
TERMINALS = ['bare', 'h', 'l', 'm', 'n', 'r', 'y']
QUINTILES = [0, 1, 2, 3, 4]
MIN_SECTION_TOKENS = 500


def jsd(dist_p, dist_q, labels):
    """JSD between two distributions given as count dicts."""
    total_p = sum(dist_p.get(k, 0) for k in labels) or 1
    total_q = sum(dist_q.get(k, 0) for k in labels) or 1
    div = 0.0
    for k in labels:
        pk = dist_p.get(k, 0) / total_p
        qk = dist_q.get(k, 0) / total_q
        mk = 0.5 * (pk + qk)
        if pk > 0 and mk > 0:
            div += 0.5 * pk * math.log2(pk / mk)
        if qk > 0 and mk > 0:
            div += 0.5 * qk * math.log2(qk / mk)
    return div


def pearson_r(x, y):
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = sum((x[i] - mx) ** 2 for i in range(n))
    dy = sum((y[i] - my) ** 2 for i in range(n))
    den = math.sqrt(dx * dy)
    if den < 1e-12:
        return 0.0
    return num / den


def cosine_sim(a, b):
    """Cosine similarity between two lists."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x ** 2 for x in a))
    nb = math.sqrt(sum(x ** 2 for x in b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return dot / (na * nb)


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    tokens = t0['tokens']
    n = len(tokens)

    # Group by section
    section_tokens = defaultdict(list)
    for t in tokens:
        section_tokens[t['section']].append(t)

    qualifying_sections = {s: toks for s, toks in section_tokens.items()
                           if len(toks) >= MIN_SECTION_TOKENS}

    # Corpus-wide HEAD/TERM rates per quintile (for comparison)
    corpus_head_by_q = {q: Counter() for q in QUINTILES}
    corpus_term_by_q = {q: Counter() for q in QUINTILES}
    for t in tokens:
        q = t['quintile']
        h = t['head'] if t['head'] else 'headless'
        corpus_head_by_q[q][h] += 1
        corpus_term_by_q[q][t['term']] += 1

    corpus_head_rates = {}
    corpus_term_rates = {}
    for q in QUINTILES:
        qt = sum(corpus_head_by_q[q].values())
        corpus_head_rates[q] = {h: corpus_head_by_q[q][h] / qt if qt > 0 else 0 for h in HEADS}
        qt2 = sum(corpus_term_by_q[q].values())
        corpus_term_rates[q] = {t: corpus_term_by_q[q][t] / qt2 if qt2 > 0 else 0 for t in TERMINALS}

    # Corpus-wide marginals
    corpus_head_marg = {}
    corpus_term_marg = {}
    for h in HEADS:
        corpus_head_marg[h] = sum(corpus_head_by_q[q][h] for q in QUINTILES) / n
    for t_atom in TERMINALS:
        corpus_term_marg[t_atom] = sum(corpus_term_by_q[q][t_atom] for q in QUINTILES) / n

    # ---- Per-section analysis ----
    section_results = {}
    for sec, toks in sorted(qualifying_sections.items()):
        n_sec = len(toks)

        # HEAD x quintile
        head_by_q = {q: Counter() for q in QUINTILES}
        term_by_q = {q: Counter() for q in QUINTILES}
        for t in toks:
            q = t['quintile']
            h = t['head'] if t['head'] else 'headless'
            head_by_q[q][h] += 1
            term_by_q[q][t['term']] += 1

        # Section HEAD rates per quintile
        sec_head_rates = {}
        for q in QUINTILES:
            qt = sum(head_by_q[q].values())
            sec_head_rates[q] = {h: head_by_q[q][h] / qt if qt > 0 else 0 for h in HEADS}

        # Section TERM rates per quintile
        sec_term_rates = {}
        for q in QUINTILES:
            qt = sum(term_by_q[q].values())
            sec_term_rates[q] = {t: term_by_q[q][t] / qt if qt > 0 else 0 for t in TERMINALS}

        # ---- 4a: Enrichment (section rate / corpus rate) ----
        head_enrichment = {}
        for h in HEADS:
            head_enrichment[h] = {}
            for q in QUINTILES:
                corp_rate = corpus_head_rates[q][h]
                sec_rate = sec_head_rates[q][h]
                head_enrichment[h][str(q)] = round(sec_rate / corp_rate, 4) if corp_rate > 1e-8 else 0

        term_enrichment = {}
        for t_atom in TERMINALS:
            term_enrichment[t_atom] = {}
            for q in QUINTILES:
                corp_rate = corpus_term_rates[q][t_atom]
                sec_rate = sec_term_rates[q][t_atom]
                term_enrichment[t_atom][str(q)] = round(sec_rate / corp_rate, 4) if corp_rate > 1e-8 else 0

        # ---- 4b: Q3->Q4 step magnitude ----
        head_jsd_q3q4 = jsd(head_by_q[3], head_by_q[4], HEADS)
        term_jsd_q3q4 = jsd(term_by_q[3], term_by_q[4], TERMINALS)

        # ---- 4c: m-terminal Q4 surge ----
        q4_total = sum(term_by_q[4].values())
        q3_total = sum(term_by_q[3].values())
        m_q4_rate = term_by_q[4].get('m', 0) / q4_total if q4_total > 0 else 0
        m_q3_rate = term_by_q[3].get('m', 0) / q3_total if q3_total > 0 else 0
        m_surge = m_q4_rate - m_q3_rate

        # ---- 4d: Gradient preservation (correlation with corpus) ----
        # Flatten: section HEAD rates across all quintiles vs corpus HEAD rates
        sec_head_flat = []
        corp_head_flat = []
        for q in QUINTILES:
            for h in HEADS:
                sec_head_flat.append(sec_head_rates[q][h])
                corp_head_flat.append(corpus_head_rates[q][h])
        head_corr = round(pearson_r(sec_head_flat, corp_head_flat), 4)

        sec_term_flat = []
        corp_term_flat = []
        for q in QUINTILES:
            for t_atom in TERMINALS:
                sec_term_flat.append(sec_term_rates[q][t_atom])
                corp_term_flat.append(corpus_term_rates[q][t_atom])
        term_corr = round(pearson_r(sec_term_flat, corp_term_flat), 4)

        # ---- 4e: Section-specific atom signatures ----
        # Section marginal rates vs corpus marginal rates
        sec_head_marg = {}
        for h in HEADS:
            sec_head_marg[h] = sum(head_by_q[q][h] for q in QUINTILES) / n_sec

        head_deviations = {}
        for h in HEADS:
            dev = sec_head_marg[h] - corpus_head_marg[h]
            head_deviations[h] = round(dev, 6)

        sec_term_marg = {}
        for t_atom in TERMINALS:
            sec_term_marg[t_atom] = sum(term_by_q[q][t_atom] for q in QUINTILES) / n_sec

        term_deviations = {}
        for t_atom in TERMINALS:
            dev = sec_term_marg[t_atom] - corpus_term_marg[t_atom]
            term_deviations[t_atom] = round(dev, 6)

        top3_enriched_head = sorted(head_deviations.items(), key=lambda x: -x[1])[:3]
        top3_depleted_head = sorted(head_deviations.items(), key=lambda x: x[1])[:3]
        top3_enriched_term = sorted(term_deviations.items(), key=lambda x: -x[1])[:3]
        top3_depleted_term = sorted(term_deviations.items(), key=lambda x: x[1])[:3]

        # Cosine similarity of gradient vectors with corpus
        # Gradient vector = [rate(atom, q) - marginal(atom)] for all atom, q
        sec_grad = []
        corp_grad = []
        for q in QUINTILES:
            for h in HEADS:
                sec_grad.append(sec_head_rates[q][h] - sec_head_marg[h])
                corp_grad.append(corpus_head_rates[q][h] - corpus_head_marg[h])
        gradient_cosine = round(cosine_sim(sec_grad, corp_grad), 4)

        section_results[sec] = {
            'n_tokens': n_sec,
            'head_rates': {str(q): {h: round(v, 6) for h, v in sec_head_rates[q].items()}
                           for q in QUINTILES},
            'term_rates': {str(q): {t: round(v, 6) for t, v in sec_term_rates[q].items()}
                           for q in QUINTILES},
            'head_enrichment_vs_corpus': head_enrichment,
            'term_enrichment_vs_corpus': term_enrichment,
            'q3q4_step': {
                'head_jsd': round(head_jsd_q3q4, 6),
                'term_jsd': round(term_jsd_q3q4, 6),
            },
            'm_terminal_surge': {
                'm_Q3_rate': round(m_q3_rate, 6),
                'm_Q4_rate': round(m_q4_rate, 6),
                'm_surge': round(m_surge, 6),
            },
            'gradient_preservation': {
                'head_correlation': head_corr,
                'term_correlation': term_corr,
                'gradient_cosine': gradient_cosine,
            },
            'atom_signatures': {
                'head_deviations': head_deviations,
                'term_deviations': term_deviations,
                'top3_enriched_head': top3_enriched_head,
                'top3_depleted_head': top3_depleted_head,
                'top3_enriched_term': top3_enriched_term,
                'top3_depleted_term': top3_depleted_term,
            }
        }

    # ---- Aggregate: C1674 decision ----
    head_corrs = [section_results[s]['gradient_preservation']['head_correlation']
                  for s in section_results]
    term_corrs = [section_results[s]['gradient_preservation']['term_correlation']
                  for s in section_results]
    min_head_corr = min(head_corrs) if head_corrs else 1.0
    min_term_corr = min(term_corrs) if term_corrs else 1.0

    q3q4_head_jsds = [section_results[s]['q3q4_step']['head_jsd']
                       for s in section_results]
    q3q4_ratio = max(q3q4_head_jsds) / min(q3q4_head_jsds) if min(q3q4_head_jsds) > 1e-8 else 999

    # Check for major sections (n > 1000) with low correlation
    major_low_corr = any(
        section_results[s]['n_tokens'] > 1000 and
        (section_results[s]['gradient_preservation']['head_correlation'] < 0.80 or
         section_results[s]['gradient_preservation']['term_correlation'] < 0.80)
        for s in section_results
    )

    if major_low_corr or q3q4_ratio > 2.0:
        verdict = 'SECTION_MODULATES_GRADIENT'
    elif min_head_corr > 0.90 and min_term_corr > 0.90 and q3q4_ratio < 2.0:
        verdict = 'SECTION_PRESERVES_GRADIENT'
    else:
        verdict = 'SECTION_MODULATES_GRADIENT'  # borderline → modulates

    output = {
        'metadata': {
            'phase': '581',
            'script': 't4_section_conditioned_gradients.py',
            'n_tokens': n,
            'qualifying_sections': list(qualifying_sections.keys()),
            'min_section_tokens': MIN_SECTION_TOKENS,
        },
        'section_results': section_results,
        'corpus_head_marginals': {h: round(v, 6) for h, v in corpus_head_marg.items()},
        'corpus_term_marginals': {t: round(v, 6) for t, v in corpus_term_marg.items()},
        'aggregate': {
            'head_correlations': {s: section_results[s]['gradient_preservation']['head_correlation']
                                  for s in section_results},
            'term_correlations': {s: section_results[s]['gradient_preservation']['term_correlation']
                                  for s in section_results},
            'min_head_corr': round(min_head_corr, 4),
            'min_term_corr': round(min_term_corr, 4),
            'q3q4_head_jsds': {s: section_results[s]['q3q4_step']['head_jsd']
                                for s in section_results},
            'q3q4_jsd_ratio': round(q3q4_ratio, 3),
        },
        'C1674': {
            'verdict': verdict,
            'min_head_corr': round(min_head_corr, 4),
            'min_term_corr': round(min_term_corr, 4),
            'q3q4_jsd_ratio': round(q3q4_ratio, 3),
            'major_low_corr': major_low_corr,
            'rationale': (f"Min HEAD corr={min_head_corr:.4f}, "
                          f"min TERM corr={min_term_corr:.4f}, "
                          f"Q3Q4 JSD ratio={q3q4_ratio:.3f}")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't4_section_conditioned_gradients.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T4: Section-conditioned gradients complete")
    print(f"  Qualifying sections: {list(qualifying_sections.keys())} "
          f"(min {MIN_SECTION_TOKENS} tokens)")
    for sec in sorted(section_results.keys()):
        sr = section_results[sec]
        print(f"  {sec} (n={sr['n_tokens']}): "
              f"HEAD corr={sr['gradient_preservation']['head_correlation']:.4f}, "
              f"TERM corr={sr['gradient_preservation']['term_correlation']:.4f}, "
              f"Q3Q4 HEAD JSD={sr['q3q4_step']['head_jsd']:.6f}, "
              f"m surge={sr['m_terminal_surge']['m_surge']:.4f}")
    print(f"  Q3Q4 JSD ratio (max/min): {q3q4_ratio:.3f}")
    print(f"  C1674: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
