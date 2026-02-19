"""Phase 398: Section Incompatibility Test

Tests whether section-level B program profiles are INCOMPATIBLE with a
single-domain explanation after controlling for REGIME composition.

6 tests (A-F) within REGIME_1:
  A: Operator substitution (49-class)
  B: Vocabulary discontinuity (MIDDLE JSD)
  C: Kernel balance independence (k/h/e)
  D: Macro-state distribution independence (6-state)
  E: PREFIX profile independence (supporting)
  F: Affordance bin specialization (supporting)
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS_DIR = PROJECT / 'phases' / 'SECTION_INCOMPATIBILITY_TEST' / 'results'

random.seed(42)

# ── Helpers ──────────────────────────────────────────────────────────────

def jsd(p, q):
    """Jensen-Shannon divergence between two frequency dicts."""
    all_keys = set(p) | set(q)
    total_p = sum(p.values()) or 1
    total_q = sum(q.values()) or 1
    eps = 1e-12
    d = 0.0
    for k in all_keys:
        pk = p.get(k, 0) / total_p + eps
        qk = q.get(k, 0) / total_q + eps
        mk = (pk + qk) / 2
        d += 0.5 * pk * math.log(pk / mk) + 0.5 * qk * math.log(qk / mk)
    return d


def chi2_test(contingency):
    """Chi-squared test on a section x category contingency dict.
    contingency: {section: {category: count}}
    Returns chi2, p, dof, cramers_v."""
    sections = sorted(contingency)
    categories = sorted(set(c for s in sections for c in contingency[s]))
    n_rows = len(sections)
    n_cols = len(categories)
    if n_rows < 2 or n_cols < 2:
        return 0.0, 1.0, 0, 0.0

    # Build matrix
    matrix = []
    for s in sections:
        row = [contingency[s].get(c, 0) for c in categories]
        matrix.append(row)

    N = sum(sum(r) for r in matrix)
    if N == 0:
        return 0.0, 1.0, 0, 0.0

    row_sums = [sum(r) for r in matrix]
    col_sums = [sum(matrix[i][j] for i in range(n_rows)) for j in range(n_cols)]

    chi2 = 0.0
    for i in range(n_rows):
        for j in range(n_cols):
            expected = row_sums[i] * col_sums[j] / N
            if expected > 0:
                chi2 += (matrix[i][j] - expected) ** 2 / expected

    dof = (n_rows - 1) * (n_cols - 1)
    # p-value approximation using chi2 survival function
    p = chi2_survival(chi2, dof)
    cramers_v = math.sqrt(chi2 / (N * (min(n_rows, n_cols) - 1))) if N > 0 and min(n_rows, n_cols) > 1 else 0.0
    return chi2, p, dof, cramers_v


def chi2_survival(x, k):
    """Approximate chi-squared survival function P(X > x) for k dof.
    Uses regularized incomplete gamma function approximation."""
    if k <= 0 or x <= 0:
        return 1.0
    # Use series expansion for regularized lower incomplete gamma
    a = k / 2.0
    z = x / 2.0
    # For large z, use normal approximation
    if z > a + 20 * math.sqrt(a):
        return 0.0
    # Series: gamma_inc(a, z) = e^(-z) * z^a * sum(z^n / gamma(a+n+1))
    term = 1.0 / a
    total = term
    for n in range(1, 500):
        term *= z / (a + n)
        total += term
        if abs(term) < 1e-15 * abs(total):
            break
    p_lower = math.exp(-z + a * math.log(z) - math.lgamma(a)) * total
    p_lower = max(0.0, min(1.0, p_lower))
    return 1.0 - p_lower


def kruskal_wallis(groups):
    """Kruskal-Wallis H test. groups: list of lists of values.
    Returns H, p."""
    all_vals = []
    for i, g in enumerate(groups):
        for v in g:
            all_vals.append((v, i))
    all_vals.sort(key=lambda x: x[0])
    N = len(all_vals)
    if N < 3:
        return 0.0, 1.0
    # Assign ranks
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-indexed
        for k_idx in range(i, j):
            ranks[k_idx] = avg_rank
        i = j
    # Sum ranks per group
    group_rank_sums = defaultdict(float)
    group_sizes = defaultdict(int)
    for idx, (val, gid) in enumerate(all_vals):
        group_rank_sums[gid] += ranks[idx]
        group_sizes[gid] += 1
    k = len(groups)
    if k < 2:
        return 0.0, 1.0
    H = 0.0
    for gid in range(k):
        ni = group_sizes[gid]
        if ni == 0:
            continue
        Ri = group_rank_sums[gid]
        H += (Ri ** 2) / ni
    H = (12.0 / (N * (N + 1))) * H - 3 * (N + 1)
    p = chi2_survival(H, k - 1)
    return H, p


# ── Data Loading ─────────────────────────────────────────────────────────

def load_data():
    """Load all data sources and pre-compute per-token fields in one pass."""
    print("Loading data sources...")

    # 1. Regime mapping
    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_regime = {f: v['regime'] for f, v in regime_data['regime_assignments'].items()}

    # 2. Class mapping (word -> class_id)
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        class_data = json.load(f)
    token_to_class = class_data['token_to_class']

    # 3. Macro-state mapping (class_id -> 6-state)
    with open(PROJECT / 'data' / 'decoder_maps.json') as f:
        decoder_data = json.load(f)
    macro_state_map = {int(k): v['value'] for k, v in decoder_data['maps']['macro_state']['entries'].items()}

    # 4. Affordance bin mapping (middle -> label)
    with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
        aff_data = json.load(f)
    middle_to_aff = {}
    middles_section = aff_data.get('middles', aff_data)
    for mid, info in middles_section.items():
        if mid.startswith('_'):
            continue
        if isinstance(info, dict) and 'affordance_label' in info:
            middle_to_aff[mid] = info['affordance_label']

    # 5. Single-pass token extraction
    tx = Transcript()
    morph = Morphology()

    tokens = []
    folio_section_map = {}
    for tok in tx.currier_b():
        if not tok.word.strip() or '*' in tok.word:
            continue
        m = morph.extract(tok.word)
        cls = token_to_class.get(tok.word)
        macro = macro_state_map.get(cls) if cls is not None else None
        aff = middle_to_aff.get(m.middle) if m.middle else None

        # Kernel chars in middle
        kernel_chars = []
        if m.middle:
            for c in m.middle:
                if c in ('k', 'h', 'e'):
                    kernel_chars.append(c)

        tokens.append({
            'word': tok.word,
            'folio': tok.folio,
            'section': tok.section,
            'middle': m.middle,
            'prefix': m.prefix if m.prefix else 'BARE',
            'class_id': cls,
            'macro_state': macro,
            'affordance_bin': aff,
            'kernel_chars': kernel_chars,
        })
        folio_section_map[tok.folio] = tok.section

    # 6. Build regime-section cross-tab and filter to REGIME_1
    regime_section_cross = defaultdict(lambda: defaultdict(int))
    for folio, regime in folio_regime.items():
        sec = folio_section_map.get(folio)
        if sec:
            regime_section_cross[regime][sec] += 1

    r1_folios = {f for f, r in folio_regime.items() if r == 'REGIME_1'}
    r1_tokens = [t for t in tokens if t['folio'] in r1_folios]

    # Sections in REGIME_1 (exclude T)
    r1_sections = sorted(set(t['section'] for t in r1_tokens if t['section'] != 'T'))

    print(f"\nTotal B tokens: {len(tokens)}")
    print(f"REGIME_1 tokens: {len(r1_tokens)}")
    print(f"REGIME_1 sections: {r1_sections}")
    print(f"\nREGIME x Section cross-tab (folio counts):")
    for regime in sorted(regime_section_cross):
        parts = [f"{s}={regime_section_cross[regime][s]}" for s in sorted(regime_section_cross[regime])]
        print(f"  {regime}: {', '.join(parts)}")

    # Per-section token counts in R1
    r1_sec_counts = Counter(t['section'] for t in r1_tokens if t['section'] in r1_sections)
    print(f"\nREGIME_1 tokens per section:")
    for s in r1_sections:
        print(f"  {s}: {r1_sec_counts[s]}")

    return {
        'tokens': tokens,
        'r1_tokens': r1_tokens,
        'r1_sections': r1_sections,
        'folio_regime': folio_regime,
        'r1_folios': r1_folios,
        'folio_section': folio_section_map,
        'regime_section_cross': {r: dict(v) for r, v in regime_section_cross.items()},
    }


# ── Test A: Operator Substitution ────────────────────────────────────────

def test_A_operator_substitution(r1_tokens, sections):
    """Within REGIME_1: per-section 49-class frequencies. Flag substitution pairs."""
    print("\n" + "="*70)
    print("TEST A: Operator Substitution (extends C555)")
    print("="*70)

    # Per-section class counts
    sec_class = {s: Counter() for s in sections}
    total_class = Counter()
    for t in r1_tokens:
        if t['section'] in sections and t['class_id'] is not None:
            sec_class[t['section']][t['class_id']] += 1
            total_class[t['class_id']] += 1

    # All classes present
    all_classes = sorted(total_class.keys())
    total_n = sum(total_class.values())
    sec_totals = {s: sum(sec_class[s].values()) for s in sections}

    print(f"\nClassified tokens in R1: {total_n}")
    for s in sections:
        print(f"  {s}: {sec_totals[s]} classified tokens")

    # Minimum tokens for a section to count in substitution detection
    # With <500 classified tokens, many classes will be 0 by chance
    MIN_TOKENS_SUBSTITUTION = 500

    # Compute enrichment per class per section
    substitution_pairs = []
    substitution_pairs_robust = []  # Only sections with enough data
    class_enrichments = {}
    large_sections = [s for s in sections if sec_totals[s] >= MIN_TOKENS_SUBSTITUTION]
    small_sections = [s for s in sections if sec_totals[s] < MIN_TOKENS_SUBSTITUTION]

    if small_sections:
        print(f"\n  WARNING: {small_sections} have <{MIN_TOKENS_SUBSTITUTION} classified tokens.")
        print(f"  Substitution pairs involving these sections may be sample-size artifacts.")
        print(f"  Robust analysis uses only: {large_sections}")

    for cls in all_classes:
        regime_rate = total_class[cls] / total_n if total_n > 0 else 0
        if regime_rate == 0:
            continue
        enrichments = {}
        for s in sections:
            sec_rate = sec_class[s].get(cls, 0) / sec_totals[s] if sec_totals[s] > 0 else 0
            enrichments[s] = sec_rate / regime_rate if regime_rate > 0 else 0
        class_enrichments[cls] = enrichments

        # Check for substitution: one >1.5x, another <0.3x
        max_sec = max(enrichments, key=lambda s: enrichments[s])
        min_sec = min(enrichments, key=lambda s: enrichments[s])
        if enrichments[max_sec] > 1.5 and enrichments[min_sec] < 0.3:
            divergence = enrichments[max_sec] / max(enrichments[min_sec], 0.001)
            pair = {
                'class': cls,
                'enriched_section': max_sec,
                'enriched_ratio': round(enrichments[max_sec], 3),
                'depleted_section': min_sec,
                'depleted_ratio': round(enrichments[min_sec], 3),
                'divergence': round(divergence, 1),
            }
            substitution_pairs.append(pair)
            # Robust: only count if both sections are large
            if max_sec in large_sections and min_sec in large_sections:
                substitution_pairs_robust.append(pair)

    # Sort by divergence
    substitution_pairs.sort(key=lambda x: x['divergence'], reverse=True)
    substitution_pairs_robust.sort(key=lambda x: x['divergence'], reverse=True)

    # Chi-squared: full and B-vs-S pairwise
    contingency = {s: {cls: sec_class[s].get(cls, 0) for cls in all_classes} for s in sections}
    chi2, p, dof, cramers_v = chi2_test(contingency)

    # Pairwise chi-squared for large sections only
    pairwise_chi2 = {}
    for i, s1 in enumerate(large_sections):
        for s2 in large_sections[i+1:]:
            pair_cont = {s1: contingency[s1], s2: contingency[s2]}
            c2, pp, dd, cv = chi2_test(pair_cont)
            pairwise_chi2[f"{s1}-{s2}"] = {
                'chi2': round(c2, 1), 'p': pp, 'dof': dd, 'cramers_v': round(cv, 4)
            }

    # Verdict based on ROBUST substitution pairs (large sections only)
    n_subs = len(substitution_pairs)
    n_subs_robust = len(substitution_pairs_robust)

    if n_subs_robust >= 3:
        verdict = 'INCOMPATIBLE'
    elif n_subs_robust >= 1:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        # Fall back to chi-squared for large-section pairs
        any_pair_sig = any(v['p'] < 0.01 and v['cramers_v'] > 0.10 for v in pairwise_chi2.values())
        if any_pair_sig:
            verdict = 'WEAKLY_INCOMPATIBLE'
        else:
            verdict = 'COMPATIBLE'

    print(f"\nAll substitution pairs (>1.5x / <0.3x): {n_subs}")
    for sp in substitution_pairs[:10]:
        print(f"  Class {sp['class']}: {sp['enriched_section']} {sp['enriched_ratio']}x / "
              f"{sp['depleted_section']} {sp['depleted_ratio']}x (divergence {sp['divergence']}x)")
    print(f"\nRobust substitution pairs (large sections only): {n_subs_robust}")
    for sp in substitution_pairs_robust[:10]:
        print(f"  Class {sp['class']}: {sp['enriched_section']} {sp['enriched_ratio']}x / "
              f"{sp['depleted_section']} {sp['depleted_ratio']}x (divergence {sp['divergence']}x)")
    print(f"\nFull chi-squared: {chi2:.1f}, p={p:.2e}, dof={dof}, Cramer's V={cramers_v:.4f}")
    for pair, stats in pairwise_chi2.items():
        print(f"  Pairwise {pair}: chi2={stats['chi2']}, p={stats['p']:.2e}, V={stats['cramers_v']}")
    print(f"Verdict: {verdict}")

    return {
        'n_classes_tested': len(all_classes),
        'n_substitution_pairs_all': n_subs,
        'n_substitution_pairs_robust': n_subs_robust,
        'substitution_pairs_all': substitution_pairs[:20],
        'substitution_pairs_robust': substitution_pairs_robust[:20],
        'large_sections': large_sections,
        'small_sections': small_sections,
        'chi2': round(chi2, 2),
        'p': p,
        'dof': dof,
        'cramers_v': round(cramers_v, 4),
        'pairwise_chi2': pairwise_chi2,
        'per_section_totals': {s: sec_totals[s] for s in sections},
        'verdict': verdict,
    }


# ── Test B: Vocabulary Discontinuity ─────────────────────────────────────

def test_B_vocabulary_discontinuity(r1_tokens, sections, folio_section):
    """Within REGIME_1: MIDDLE JSD between sections vs within-section null."""
    print("\n" + "="*70)
    print("TEST B: Vocabulary Discontinuity (MIDDLE JSD)")
    print("="*70)

    # Per-section MIDDLE frequencies
    sec_mid = {s: Counter() for s in sections}
    # Also per-folio for split tests
    folio_mid = defaultdict(Counter)
    sec_folios = defaultdict(set)

    for t in r1_tokens:
        if t['section'] in sections and t['middle']:
            sec_mid[t['section']][t['middle']] += 1
            folio_mid[t['folio']][t['middle']] += 1
            sec_folios[t['section']].add(t['folio'])

    for s in sections:
        print(f"  {s}: {sum(sec_mid[s].values())} MIDDLEs from {len(sec_folios[s])} folios")

    # Pairwise between-section JSD
    between_jsd = {}
    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            d = jsd(sec_mid[s1], sec_mid[s2])
            between_jsd[f"{s1}-{s2}"] = round(d, 6)
            print(f"  JSD({s1},{s2}) = {d:.6f}")

    # Null: within-section random folio splits
    n_perms = 1000
    within_jsds = []
    for s in sections:
        folios = sorted(sec_folios[s])
        if len(folios) < 4:
            print(f"  Warning: {s} has only {len(folios)} folios — skipping split test")
            continue
        for _ in range(n_perms // len(sections)):
            random.shuffle(folios)
            half = len(folios) // 2
            split_a = Counter()
            split_b = Counter()
            for f in folios[:half]:
                split_a.update(folio_mid[f])
            for f in folios[half:]:
                split_b.update(folio_mid[f])
            if sum(split_a.values()) > 0 and sum(split_b.values()) > 0:
                within_jsds.append(jsd(split_a, split_b))

    if within_jsds:
        null_mean = sum(within_jsds) / len(within_jsds)
        null_sd = (sum((x - null_mean)**2 for x in within_jsds) / len(within_jsds)) ** 0.5
        print(f"\nWithin-section null: mean={null_mean:.6f}, SD={null_sd:.6f} (n={len(within_jsds)})")

        # How many between-section pairs exceed 2 SD?
        n_above_2sd = 0
        n_above_1sd = 0
        pair_sigmas = {}
        for pair, d in between_jsd.items():
            sigma = (d - null_mean) / null_sd if null_sd > 0 else 0
            pair_sigmas[pair] = round(sigma, 2)
            if sigma > 2:
                n_above_2sd += 1
            if sigma > 1:
                n_above_1sd += 1
            print(f"  {pair}: {sigma:.2f} SD above null")
    else:
        null_mean = 0
        null_sd = 0
        n_above_2sd = 0
        n_above_1sd = 0
        pair_sigmas = {}

    # Robust verdict: separate pairs involving small vs large sections
    # Sections with <4 folios couldn't participate in null, so their JSD is unreliable
    large_sec_folios = {s for s in sec_folios if len(sec_folios[s]) >= 4}
    n_robust_above_2sd = 0
    n_robust_above_1sd = 0
    n_small_above_2sd = 0
    for pair, sigma in pair_sigmas.items():
        s1, s2 = pair.split('-')
        if s1 in large_sec_folios and s2 in large_sec_folios:
            if sigma > 2:
                n_robust_above_2sd += 1
            if sigma > 1:
                n_robust_above_1sd += 1
        else:
            if sigma > 2:
                n_small_above_2sd += 1

    # Verdict based on robust pairs
    if n_robust_above_2sd >= 2:
        verdict = 'INCOMPATIBLE'
    elif n_robust_above_2sd >= 1 or n_robust_above_1sd >= 2:
        verdict = 'WEAKLY_INCOMPATIBLE'
    elif n_above_1sd >= 1:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        verdict = 'COMPATIBLE'

    print(f"\nAll pairs >2 SD: {n_above_2sd}, >1 SD: {n_above_1sd}")
    print(f"Robust pairs (large sections only) >2 SD: {n_robust_above_2sd}, >1 SD: {n_robust_above_1sd}")
    print(f"Small-section pairs >2 SD: {n_small_above_2sd} (unreliable)")
    print(f"Verdict: {verdict}")

    return {
        'between_section_jsd': between_jsd,
        'within_section_null_mean': round(null_mean, 6),
        'within_section_null_sd': round(null_sd, 6),
        'n_permutations': len(within_jsds),
        'pair_sigmas': pair_sigmas,
        'n_above_2sd': n_above_2sd,
        'n_above_1sd': n_above_1sd,
        'n_robust_above_2sd': n_robust_above_2sd,
        'n_robust_above_1sd': n_robust_above_1sd,
        'n_small_above_2sd': n_small_above_2sd,
        'verdict': verdict,
    }


# ── Test C: Kernel Balance Independence ──────────────────────────────────

def test_C_kernel_balance(r1_tokens, sections, r1_folios_set, folio_section):
    """Within REGIME_1: per-folio k/h/e grouped by section."""
    print("\n" + "="*70)
    print("TEST C: Kernel Balance Independence (extends C1085, C1106)")
    print("="*70)

    # Per-folio kernel counts
    folio_kernel = defaultdict(lambda: Counter())
    for t in r1_tokens:
        if t['section'] in sections:
            for kc in t['kernel_chars']:
                folio_kernel[t['folio']][kc] += 1

    # Per-folio percentages
    folio_khe = {}
    for f in folio_kernel:
        total = sum(folio_kernel[f].values())
        if total >= 10:  # minimum kernel chars
            folio_khe[f] = {
                'k': folio_kernel[f].get('k', 0) / total,
                'h': folio_kernel[f].get('h', 0) / total,
                'e': folio_kernel[f].get('e', 0) / total,
                'n': total,
            }

    # Group by section
    sec_groups = {s: [] for s in sections}
    for f, khe in folio_khe.items():
        sec = folio_section.get(f)
        if sec in sections:
            sec_groups[sec].append(khe)

    print(f"\nFolios with sufficient kernel data:")
    sec_centroids = {}
    for s in sections:
        vals = sec_groups[s]
        if vals:
            k_mean = sum(v['k'] for v in vals) / len(vals)
            h_mean = sum(v['h'] for v in vals) / len(vals)
            e_mean = sum(v['e'] for v in vals) / len(vals)
            sec_centroids[s] = {'k': round(k_mean, 4), 'h': round(h_mean, 4), 'e': round(e_mean, 4)}
            print(f"  {s}: n={len(vals)}, k={k_mean:.3f}, h={h_mean:.3f}, e={e_mean:.3f}")
        else:
            print(f"  {s}: no folios with sufficient kernel data")

    # Kruskal-Wallis per dimension
    kw_results = {}
    for dim in ('k', 'h', 'e'):
        groups = [
            [v[dim] for v in sec_groups[s]]
            for s in sections if sec_groups[s]
        ]
        groups = [g for g in groups if g]  # remove empty
        H, p = kruskal_wallis(groups)
        kw_results[dim] = {'H': round(H, 2), 'p': round(p, 6)}
        print(f"  Kruskal-Wallis {dim}: H={H:.2f}, p={p:.6f}")

    # PERMANOVA approximation: permutation test on between-group vs within-group distance
    n_perms = 5000
    # Compute observed F-statistic (ratio of between/within SS in k/h/e space)
    all_folio_data = []
    folio_labels = []
    for s in sections:
        for v in sec_groups[s]:
            all_folio_data.append((v['k'], v['h'], v['e']))
            folio_labels.append(s)

    def compute_f_stat(data, labels):
        if len(data) < 4:
            return 0.0
        groups_idx = defaultdict(list)
        for i, lab in enumerate(labels):
            groups_idx[lab].append(i)
        grand_mean = tuple(sum(d[dim] for d in data) / len(data) for dim in range(3))
        ss_between = 0.0
        ss_within = 0.0
        k_groups = len(groups_idx)
        for lab, indices in groups_idx.items():
            grp = [data[i] for i in indices]
            grp_mean = tuple(sum(g[dim] for g in grp) / len(grp) for dim in range(3))
            ss_between += len(grp) * sum((grp_mean[dim] - grand_mean[dim])**2 for dim in range(3))
            for g in grp:
                ss_within += sum((g[dim] - grp_mean[dim])**2 for dim in range(3))
        if ss_within == 0:
            return float('inf')
        N = len(data)
        return (ss_between / (k_groups - 1)) / (ss_within / (N - k_groups)) if N > k_groups else 0.0

    observed_f = compute_f_stat(all_folio_data, folio_labels)
    n_exceed = 0
    for _ in range(n_perms):
        perm_labels = folio_labels[:]
        random.shuffle(perm_labels)
        perm_f = compute_f_stat(all_folio_data, perm_labels)
        if perm_f >= observed_f:
            n_exceed += 1
    permanova_p = (n_exceed + 1) / (n_perms + 1)

    print(f"\n  PERMANOVA: F={observed_f:.3f}, p={permanova_p:.4f} ({n_perms} permutations)")

    # Count distinct sections (significant KW on any dimension)
    n_significant_dims = sum(1 for d in kw_results.values() if d['p'] < 0.01)

    # Verdict
    if permanova_p < 0.01 and n_significant_dims >= 2:
        verdict = 'INCOMPATIBLE'
    elif permanova_p < 0.05 or n_significant_dims >= 1:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        verdict = 'COMPATIBLE'

    print(f"  Significant KW dimensions (p<0.01): {n_significant_dims}/3")
    print(f"Verdict: {verdict}")

    return {
        'section_centroids': sec_centroids,
        'section_folio_counts': {s: len(sec_groups[s]) for s in sections},
        'kruskal_wallis': kw_results,
        'permanova_F': round(observed_f, 4),
        'permanova_p': round(permanova_p, 4),
        'n_permutations': n_perms,
        'n_significant_kw_dims': n_significant_dims,
        'verdict': verdict,
    }


# ── Test D: Macro-State Distribution ─────────────────────────────────────

def test_D_macro_state(r1_tokens, sections):
    """Within REGIME_1: per-section 6-state distribution."""
    print("\n" + "="*70)
    print("TEST D: Macro-State Distribution Independence")
    print("="*70)

    STATES = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
    sec_state = {s: Counter() for s in sections}

    for t in r1_tokens:
        if t['section'] in sections and t['macro_state']:
            sec_state[t['section']][t['macro_state']] += 1

    # Print distributions
    print(f"\n{'Section':>8}", end='')
    for st in STATES:
        print(f"  {st:>8}", end='')
    print(f"  {'Total':>8}")

    for s in sections:
        total = sum(sec_state[s].values())
        print(f"{s:>8}", end='')
        for st in STATES:
            pct = sec_state[s].get(st, 0) / total * 100 if total > 0 else 0
            print(f"  {pct:>7.1f}%", end='')
        print(f"  {total:>8}")

    # Chi-squared
    contingency = {s: {st: sec_state[s].get(st, 0) for st in STATES} for s in sections}
    chi2, p, dof, cramers_v = chi2_test(contingency)

    # Pairwise JSD
    pairwise = {}
    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            d = jsd(sec_state[s1], sec_state[s2])
            pairwise[f"{s1}-{s2}"] = round(d, 6)

    print(f"\nChi-squared: {chi2:.1f}, p={p:.2e}, dof={dof}, Cramer's V={cramers_v:.4f}")
    print("Pairwise JSD:")
    for pair, d in sorted(pairwise.items()):
        print(f"  {pair}: {d:.6f}")

    # Verdict
    if p < 0.01 and cramers_v > 0.10:
        verdict = 'INCOMPATIBLE'
    elif p < 0.01:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        verdict = 'COMPATIBLE'

    print(f"Verdict: {verdict}")

    return {
        'section_distributions': {
            s: {st: sec_state[s].get(st, 0) for st in STATES} for s in sections
        },
        'section_proportions': {
            s: {st: round(sec_state[s].get(st, 0) / max(sum(sec_state[s].values()), 1) * 100, 2)
                for st in STATES} for s in sections
        },
        'chi2': round(chi2, 2),
        'p': p,
        'dof': dof,
        'cramers_v': round(cramers_v, 4),
        'pairwise_jsd': pairwise,
        'verdict': verdict,
    }


# ── Test E: PREFIX Profile ───────────────────────────────────────────────

def test_E_prefix_profile(r1_tokens, sections):
    """Within REGIME_1: per-section PREFIX distribution."""
    print("\n" + "="*70)
    print("TEST E: PREFIX Profile Independence (supporting)")
    print("="*70)

    sec_pfx = {s: Counter() for s in sections}
    for t in r1_tokens:
        if t['section'] in sections and t['prefix']:
            sec_pfx[t['section']][t['prefix']] += 1

    # Top prefixes
    total_pfx = Counter()
    for s in sections:
        total_pfx.update(sec_pfx[s])
    top_prefixes = [p for p, _ in total_pfx.most_common(12)]

    # Print
    print(f"\n{'Section':>8}", end='')
    for pfx in top_prefixes[:8]:
        print(f"  {pfx:>6}", end='')
    print(f"  {'Total':>8}")

    for s in sections:
        total = sum(sec_pfx[s].values())
        print(f"{s:>8}", end='')
        for pfx in top_prefixes[:8]:
            pct = sec_pfx[s].get(pfx, 0) / total * 100 if total > 0 else 0
            print(f"  {pct:>5.1f}%", end='')
        print(f"  {total:>8}")

    # Chi-squared on top prefixes
    contingency = {s: {pfx: sec_pfx[s].get(pfx, 0) for pfx in top_prefixes} for s in sections}
    chi2, p, dof, cramers_v = chi2_test(contingency)

    print(f"\nChi-squared: {chi2:.1f}, p={p:.2e}, dof={dof}, Cramer's V={cramers_v:.4f}")

    # Verdict
    if p < 0.01 and cramers_v > 0.10:
        verdict = 'INCOMPATIBLE'
    elif p < 0.01:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        verdict = 'COMPATIBLE'

    print(f"Verdict: {verdict}")

    return {
        'section_distributions': {
            s: {pfx: sec_pfx[s].get(pfx, 0) for pfx in top_prefixes} for s in sections
        },
        'section_proportions': {
            s: {pfx: round(sec_pfx[s].get(pfx, 0) / max(sum(sec_pfx[s].values()), 1) * 100, 2)
                for pfx in top_prefixes[:8]} for s in sections
        },
        'chi2': round(chi2, 2),
        'p': p,
        'dof': dof,
        'cramers_v': round(cramers_v, 4),
        'verdict': verdict,
    }


# ── Test F: Affordance Bin Specialization ────────────────────────────────

def test_F_affordance_bins(r1_tokens, sections):
    """Within REGIME_1: per-section affordance bin distribution."""
    print("\n" + "="*70)
    print("TEST F: Affordance Bin Specialization (supporting)")
    print("="*70)

    sec_aff = {s: Counter() for s in sections}
    for t in r1_tokens:
        if t['section'] in sections and t['affordance_bin']:
            sec_aff[t['section']][t['affordance_bin']] += 1

    # All bins
    all_bins = sorted(set(b for s in sections for b in sec_aff[s]))

    # Print
    print(f"\n{'Section':>8}", end='')
    for b in all_bins:
        label = b[:12]
        print(f"  {label:>12}", end='')
    print(f"  {'Total':>8}")

    for s in sections:
        total = sum(sec_aff[s].values())
        print(f"{s:>8}", end='')
        for b in all_bins:
            pct = sec_aff[s].get(b, 0) / total * 100 if total > 0 else 0
            print(f"  {pct:>11.1f}%", end='')
        print(f"  {total:>8}")

    # Chi-squared
    contingency = {s: {b: sec_aff[s].get(b, 0) for b in all_bins} for s in sections}
    chi2, p, dof, cramers_v = chi2_test(contingency)

    # Enrichment per bin per section
    total_aff = Counter()
    for s in sections:
        total_aff.update(sec_aff[s])
    total_n = sum(total_aff.values())
    sec_totals = {s: sum(sec_aff[s].values()) for s in sections}

    enrichments = {}
    for b in all_bins:
        regime_rate = total_aff[b] / total_n if total_n > 0 else 0
        for s in sections:
            sec_rate = sec_aff[s].get(b, 0) / sec_totals[s] if sec_totals[s] > 0 else 0
            ratio = sec_rate / regime_rate if regime_rate > 0 else 0
            if ratio > 1.5 or ratio < 0.5:
                enrichments[f"{s}_{b}"] = round(ratio, 3)

    print(f"\nChi-squared: {chi2:.1f}, p={p:.2e}, dof={dof}, Cramer's V={cramers_v:.4f}")
    if enrichments:
        print("Notable enrichments/depletions (>1.5x or <0.5x):")
        for key, ratio in sorted(enrichments.items()):
            print(f"  {key}: {ratio}x")

    # Verdict
    if p < 0.01 and cramers_v > 0.10:
        verdict = 'INCOMPATIBLE'
    elif p < 0.01:
        verdict = 'WEAKLY_INCOMPATIBLE'
    else:
        verdict = 'COMPATIBLE'

    print(f"Verdict: {verdict}")

    return {
        'section_distributions': {
            s: {b: sec_aff[s].get(b, 0) for b in all_bins} for s in sections
        },
        'section_proportions': {
            s: {b: round(sec_aff[s].get(b, 0) / max(sec_totals.get(s, 1), 1) * 100, 2)
                for b in all_bins} for s in sections
        },
        'chi2': round(chi2, 2),
        'p': p,
        'dof': dof,
        'cramers_v': round(cramers_v, 4),
        'notable_enrichments': enrichments,
        'verdict': verdict,
    }


# ── Combined Verdict ─────────────────────────────────────────────────────

def combined_verdict(results):
    """Score tests and produce final verdict."""
    score_map = {'COMPATIBLE': 0, 'WEAKLY_INCOMPATIBLE': 1, 'INCOMPATIBLE': 2}

    primary_tests = ['test_A', 'test_B', 'test_C', 'test_D']
    support_tests = ['test_E', 'test_F']

    primary_score = sum(score_map.get(results[t]['verdict'], 0) for t in primary_tests)
    support_score = sum(score_map.get(results[t]['verdict'], 0) for t in support_tests)

    n_primary_incompatible = sum(
        1 for t in primary_tests if results[t]['verdict'] == 'INCOMPATIBLE'
    )

    # Expert-validated verdict framework (Phase 398 expert review):
    # Consistency of weak effects confirms C1029 section parameterization
    # but does NOT establish qualitative incompatibility.
    # Multi-domain upgrade requires INCOMPATIBLE on 2+ primary robust tests.
    if primary_score == 0:
        verdict = 'COMPATIBLE'
        implication = 'No section effects within REGIME. Single-domain trivially sufficient.'
    elif n_primary_incompatible >= 2:
        if support_score >= 2:
            verdict = 'STRONGLY_INCOMPATIBLE'
            implication = 'Multi-domain upgrades to Tier 2 with high confidence.'
        else:
            verdict = 'INCOMPATIBLE'
            implication = 'Multi-domain upgrades to Tier 2.'
    elif n_primary_incompatible >= 1:
        verdict = 'WEAKLY_INCOMPATIBLE'
        implication = ('One primary dimension shows qualitative section divergence. '
                       'Multi-domain stays Tier 3 with noted evidence.')
    elif primary_score >= 2:
        verdict = 'SECTION_DIFFERENTIATED'
        implication = ('Sections show consistent quantitative divergence within REGIME '
                       '(confirms C1029 section parameterization at within-REGIME granularity). '
                       'Multi-domain stays Tier 3. New constraint: within-REGIME section parameterization.')
    else:
        verdict = 'COMPATIBLE'
        implication = 'Minimal section effects within REGIME. Single-domain sufficient.'

    return {
        'primary_score': primary_score,
        'primary_max': 8,
        'support_score': support_score,
        'support_max': 4,
        'n_primary_incompatible': n_primary_incompatible,
        'per_test_verdicts': {t: results[t]['verdict'] for t in primary_tests + support_tests},
        'overall_verdict': verdict,
        'implication': implication,
    }


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    data = load_data()
    r1_tokens = data['r1_tokens']
    sections = data['r1_sections']

    results = {}
    results['test_A'] = test_A_operator_substitution(r1_tokens, sections)
    results['test_B'] = test_B_vocabulary_discontinuity(r1_tokens, sections, data['folio_section'])
    results['test_C'] = test_C_kernel_balance(r1_tokens, sections, data['r1_folios'], data['folio_section'])
    results['test_D'] = test_D_macro_state(r1_tokens, sections)
    results['test_E'] = test_E_prefix_profile(r1_tokens, sections)
    results['test_F'] = test_F_affordance_bins(r1_tokens, sections)

    verdict = combined_verdict(results)

    # Summary
    print("\n" + "="*70)
    print("COMBINED VERDICT")
    print("="*70)
    print(f"\nPer-test verdicts:")
    for t, v in verdict['per_test_verdicts'].items():
        label = {'test_A': 'A: Operator Substitution',
                 'test_B': 'B: Vocabulary Discontinuity',
                 'test_C': 'C: Kernel Balance',
                 'test_D': 'D: Macro-State Distribution',
                 'test_E': 'E: PREFIX Profile (support)',
                 'test_F': 'F: Affordance Bins (support)'}[t]
        print(f"  {label}: {v}")
    print(f"\nPrimary score: {verdict['primary_score']}/{verdict['primary_max']}")
    print(f"Support score: {verdict['support_score']}/{verdict['support_max']}")
    print(f"Primary INCOMPATIBLE count: {verdict['n_primary_incompatible']}")
    print(f"\n{'='*40}")
    print(f"OVERALL: {verdict['overall_verdict']}")
    print(f"{'='*40}")
    print(f"\n{verdict['implication']}")

    # Save
    output = {
        'phase': 398,
        'name': 'SECTION_INCOMPATIBILITY_TEST',
        'regime_focus': 'REGIME_1',
        'sections_tested': sections,
        'regime_section_cross_tab': data['regime_section_cross'],
        'test_A': results['test_A'],
        'test_B': results['test_B'],
        'test_C': results['test_C'],
        'test_D': results['test_D'],
        'test_E': results['test_E'],
        'test_F': results['test_F'],
        'combined': verdict,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'section_incompatibility_results.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
