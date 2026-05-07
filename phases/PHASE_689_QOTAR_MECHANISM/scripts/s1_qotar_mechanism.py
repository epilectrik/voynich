#!/usr/bin/env python3
"""
Phase 689 - qotar morphological clustering mechanism.

Pre-registered tests (Phase 689 INDEX.md):
  T1: same-stem fraction of qotar's adjacent tokens > 30%
  T2: Gini coefficient of qotar across folios > 0.7
  T3: section concentration in S/C with chi^2 p<0.01 and obs/exp ratio > 1.5
  T4: qokedy comparison — different mechanism profile across all three metrics

Methodology locked (M1-M7 in INDEX).
"""
import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology


def levenshtein(a, b):
    """Standard Levenshtein distance."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            cur.append(min(
                prev[j + 1] + 1,
                cur[-1] + 1,
                prev[j] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def get_qo_middle(token, morph_engine):
    """Return the post-qo-prefix portion of token if qo-prefixed, else None."""
    m = morph_engine.extract(token)
    if m.prefix == 'qo':
        return (m.middle or '') + (m.suffix or '')
    return None


def is_same_stem(target, neighbor, target_qo_middle, morph_engine):
    """Same-stem if Levenshtein <= 1 OR same post-qo middle."""
    if levenshtein(target, neighbor) <= 1:
        return True
    if target_qo_middle is not None:
        nb_qo = get_qo_middle(neighbor, morph_engine)
        if nb_qo is not None and nb_qo == target_qo_middle:
            return True
    return False


def gini_coefficient(values):
    """Gini coefficient on a list of non-negative values."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    cum = 0
    for i, v in enumerate(sorted_v, start=1):
        cum += i * v
    total = sum(sorted_v)
    if total == 0:
        return 0.0
    return (2 * cum) / (n * total) - (n + 1) / n


def chi_square_section(observed, expected_proportions):
    """Chi-square test against expected proportions.
    observed: dict section -> count
    expected_proportions: dict section -> proportion (sum to 1)
    Returns chi2_stat, df, approx_p (Wilson-Hilferty)
    """
    n = sum(observed.values())
    if n == 0:
        return 0.0, 0, 1.0
    sections = sorted(set(observed.keys()) | set(expected_proportions.keys()))
    chi2 = 0.0
    df = 0
    for s in sections:
        o = observed.get(s, 0)
        e = expected_proportions.get(s, 0) * n
        if e > 0:
            chi2 += (o - e) ** 2 / e
            df += 1
    df = max(df - 1, 1)
    # Wilson-Hilferty approx
    if df > 0:
        z_wh = ((chi2 / df) ** (1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        p = 0.5 * (1 - math.erf(z_wh / math.sqrt(2)))
    else:
        p = 1.0
    return chi2, df, p


def analyze_token(target, all_tokens_with_metadata, morph_engine, section_proportions):
    """
    For target token, compute:
      - n_instances
      - same-stem fraction of adjacent tokens
      - per-folio counts and Gini
      - per-section counts and chi^2
      - example contexts (first few)
    """
    target_qo_middle = get_qo_middle(target, morph_engine)

    # Find instances
    instances = []
    for i, (tok, folio, section, line, par_initial, par_final) in enumerate(
            all_tokens_with_metadata):
        if tok == target:
            instances.append((i, folio, section, line, par_initial, par_final))

    n = len(instances)
    if n == 0:
        return None

    # Adjacent tokens with same-stem analysis (skip paragraph boundaries)
    adjacent = []
    same_stem_count = 0
    total_adjacent = 0
    for i, folio, section, line, par_init, par_fin in instances:
        # prev (skip if par_initial)
        if not par_init and i > 0:
            prev_tok = all_tokens_with_metadata[i - 1][0]
            adjacent.append(('prev', prev_tok))
            if is_same_stem(target, prev_tok, target_qo_middle, morph_engine):
                same_stem_count += 1
            total_adjacent += 1
        # next (skip if par_final)
        if not par_fin and i < len(all_tokens_with_metadata) - 1:
            next_tok = all_tokens_with_metadata[i + 1][0]
            adjacent.append(('next', next_tok))
            if is_same_stem(target, next_tok, target_qo_middle, morph_engine):
                same_stem_count += 1
            total_adjacent += 1

    same_stem_frac = same_stem_count / total_adjacent if total_adjacent > 0 else 0.0

    # Folio counts and Gini
    by_folio = Counter(folio for _, folio, _, _, _, _ in instances)
    # Include zero-count folios? For Gini, include only folios that contain ANY token from corpus
    all_folios = set(t[1] for t in all_tokens_with_metadata)
    folio_counts_inclusive = [by_folio.get(f, 0) for f in all_folios]
    gini = gini_coefficient(folio_counts_inclusive)

    # Section distribution
    by_section = Counter(section for _, _, section, _, _, _ in instances)
    chi2, df, p = chi_square_section(by_section, section_proportions)

    sc_observed = by_section.get('S', 0) + by_section.get('C', 0)
    sc_expected = (section_proportions.get('S', 0) + section_proportions.get('C', 0)) * n
    sc_ratio = sc_observed / sc_expected if sc_expected > 0 else 0.0

    # Top adjacent tokens
    adj_counter = Counter(t for _, t in adjacent)
    top_adj = adj_counter.most_common(15)

    return {
        'target': target,
        'n_instances': n,
        'n_adjacent': total_adjacent,
        'same_stem_count': same_stem_count,
        'same_stem_frac': same_stem_frac,
        'n_folios_with': len([c for c in folio_counts_inclusive if c > 0]),
        'n_folios_total': len(all_folios),
        'gini_folio': gini,
        'top_folios': by_folio.most_common(8),
        'section_dist': dict(by_section),
        'section_chi2': chi2,
        'section_df': df,
        'section_p': p,
        'sc_observed': sc_observed,
        'sc_expected': sc_expected,
        'sc_ratio': sc_ratio,
        'top_adjacent': top_adj,
    }


def main():
    print("Loading Currier B tokens with metadata...")
    tx = Transcript()
    rows = []
    for tok in tx.currier_b():
        if not tok.word:
            continue
        rows.append((
            tok.word, tok.folio, tok.section, tok.line,
            tok.par_initial, tok.par_final,
        ))
    print(f"  Total Currier B tokens: {len(rows)}")

    # Compute section proportions for null
    by_section_total = Counter(r[2] for r in rows)
    total = len(rows)
    section_proportions = {s: c / total for s, c in by_section_total.items()}
    print(f"  Section breakdown of Currier B tokens:")
    for s, c in sorted(by_section_total.items()):
        print(f"    {s}: n={c} ({100*c/total:.1f}%)")

    morph = Morphology()

    print("\nAnalyzing qotar...")
    qotar_result = analyze_token('qotar', rows, morph, section_proportions)

    print("\nAnalyzing qokedy (comparison)...")
    qokedy_result = analyze_token('qokedy', rows, morph, section_proportions)

    # ==== Pre-registered adjudication ====
    def report(r):
        print(f"\n  {r['target']}: n_instances={r['n_instances']}, "
              f"n_adjacent={r['n_adjacent']}")
        print(f"    Same-stem fraction: {r['same_stem_frac']:.3f} "
              f"({r['same_stem_count']}/{r['n_adjacent']})")
        print(f"    Folios touched: {r['n_folios_with']}/{r['n_folios_total']}, "
              f"Gini={r['gini_folio']:.3f}")
        print(f"    Top folios: {r['top_folios']}")
        print(f"    Section distribution: {r['section_dist']}")
        print(f"    chi^2={r['section_chi2']:.2f}, df={r['section_df']}, p={r['section_p']:.4f}")
        print(f"    S+C observed={r['sc_observed']}, expected={r['sc_expected']:.2f}, "
              f"ratio={r['sc_ratio']:.2f}")
        print(f"    Top adjacent tokens: {r['top_adjacent'][:10]}")

    print("\n" + "=" * 72)
    print("RESULTS")
    print("=" * 72)
    report(qotar_result)
    report(qokedy_result)

    # T1
    t1 = 'PASS' if qotar_result['same_stem_frac'] > 0.30 else 'FAIL'
    # T2
    t2 = 'PASS' if qotar_result['gini_folio'] > 0.70 else 'FAIL'
    # T3
    t3 = ('PASS' if qotar_result['section_p'] < 0.01
          and qotar_result['sc_ratio'] > 1.5 else 'FAIL')

    # T4: qokedy different on all three
    t4_lower_stem = qokedy_result['same_stem_frac'] < qotar_result['same_stem_frac']
    t4_lower_gini = qokedy_result['gini_folio'] < qotar_result['gini_folio']
    t4_no_sc_concentration = qokedy_result['sc_ratio'] <= 1.5
    t4_components = sum([t4_lower_stem, t4_lower_gini, t4_no_sc_concentration])
    if t4_components == 3:
        t4 = 'PASS'
    elif t4_components >= 1:
        t4 = 'PARTIAL'
    else:
        t4 = 'FAIL'

    print("\n" + "=" * 72)
    print("PRE-REGISTERED VERDICTS")
    print("=" * 72)
    print(f"  T1 (qotar same-stem > 30%): "
          f"{qotar_result['same_stem_frac']:.1%} -> {t1}")
    print(f"  T2 (qotar Gini > 0.70): "
          f"{qotar_result['gini_folio']:.3f} -> {t2}")
    print(f"  T3 (S/C section concentration): "
          f"p={qotar_result['section_p']:.4f}, ratio={qotar_result['sc_ratio']:.2f} -> {t3}")
    print(f"  T4 (qokedy different on all three): "
          f"stem_lower={t4_lower_stem}, gini_lower={t4_lower_gini}, "
          f"no_sc={t4_no_sc_concentration} -> {t4}")

    # T1+T2+T3 combined verdict
    pass_count = sum(1 for v in [t1, t2, t3] if v == 'PASS')
    if pass_count == 3:
        c2002_verdict = 'ALL_THREE_PASS'
    elif pass_count == 2:
        c2002_verdict = 'TWO_OF_THREE'
    elif pass_count == 1:
        c2002_verdict = 'ONE_OF_THREE'
    else:
        c2002_verdict = 'NONE_PASS'

    print(f"\n  C2002 verdict: T1+T2+T3 = {c2002_verdict} ({pass_count}/3)")
    print(f"  C2003 conditional: {'will register' if t4 == 'PASS' else 'NOT registered (T4 not PASS)'}")

    # Save
    out = {
        'phase': 689,
        'qotar': qotar_result,
        'qokedy': qokedy_result,
        'verdicts': {
            'T1': t1,
            'T2': t2,
            'T3': t3,
            'T4': t4,
        },
        'c2002_verdict': c2002_verdict,
        'pass_count_T1_T2_T3': pass_count,
        'thresholds': {
            'same_stem_threshold': 0.30,
            'gini_threshold': 0.70,
            'chi2_p_threshold': 0.01,
            'sc_ratio_threshold': 1.5,
        },
    }
    out_path = Path(__file__).resolve().parent.parent / 'results' / 't1_qotar_mechanism.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=lambda x: list(x) if isinstance(x, tuple) else x)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
