"""
COMPOUND_SLOT_GRAMMAR: Phase 432
==================================
Tests how compound MIDDLEs interact with the atom-level slot grammar
established in C1209-C1211.

Context:
  - C1209: MIDDLE positional grammar (INITIAL/MEDIAL/TERMINAL/FREE)
  - C1210: Forbidden combinations (a->y, e->n, k->n)
  - C1211: Pairwise sufficiency within MIDDLEs
  - C1212: Cross-token chaining at token boundary (z=20.3)
  - C1177: Dark pipeline ordering consistent with C1065

Tests:
  T1:  Compound vs atomic C1210 compliance (whole INITIAL->TERMINAL)
  T2:  Internal junction grammar (where embedded atoms meet)
  T3:  Junction grammar vs C1212 cross-token grammar correlation
"""
import json
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

RESULTS_DIR = Path("phases/COMPOUND_SLOT_GRAMMAR/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# C1210 forbidden combinations (near-categorical)
FORBIDDEN_PAIRS = [('a', 'y'), ('e', 'n'), ('k', 'n')]


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all Currier B tokens with morphology and compound analysis."""
    tx = Transcript()
    morph = Morphology()
    analyzer = MiddleAnalyzer()
    analyzer.build_inventory('B')

    core_middles = analyzer.get_core_middles()

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if not m.middle or m.middle == '_EMPTY_' or len(m.middle) < 2:
            continue
        is_comp = analyzer.is_compound(m.middle)
        contained = analyzer.get_contained_atoms(m.middle) if is_comp else []
        maximal = analyzer.get_maximal_atoms(m.middle) if is_comp else []
        tokens.append({
            'word': t.word,
            'middle': m.middle,
            'folio': t.folio,
            'section': t.section,
            'initial': m.middle[0],
            'terminal': m.middle[-1],
            'is_compound': is_comp,
            'contained_atoms': contained,
            'maximal_atoms': maximal,
        })

    return tokens, core_middles, analyzer


def greedy_tile(middle, core_set, min_len=2):
    """Greedy left-to-right tiling of a MIDDLE using core atoms.

    Returns a list of tiles. Each tile is either a core atom or a
    single-character residue.
    """
    tiles = []
    i = 0
    while i < len(middle):
        best = None
        # Try longest matches first
        for length in range(min(len(middle) - i, 8), min_len - 1, -1):
            candidate = middle[i:i + length]
            if candidate in core_set and candidate != middle:
                best = candidate
                break
        if best:
            tiles.append(best)
            i += len(best)
        else:
            tiles.append(middle[i])
            i += 1
    return tiles


# ============================================================
# HELPERS
# ============================================================

def cramers_v(contingency):
    """Compute chi2 and Cramer's V from contingency Counter."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    if n == 0:
        return 0.0, 0.0, 0

    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    k = min(len(rows), len(cols))
    v = (chi2 / (n * (k - 1))) ** 0.5 if k > 1 and n > 0 else 0
    return chi2, v, n


def mutual_info(contingency):
    """Compute MI in bits."""
    n = sum(contingency.values())
    if n == 0:
        return 0.0
    rows = set(r for r, c in contingency)
    cols = set(c for r, c in contingency)
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    mi = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            if obs == 0:
                continue
            p_rc = obs / n
            p_r = row_totals[r] / n
            p_c = col_totals[c] / n
            if p_r > 0 and p_c > 0:
                mi += p_rc * math.log2(p_rc / (p_r * p_c))
    return mi


def enrichment_ratios(contingency, min_expected=5):
    """Compute obs/expected ratios."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    ratios = {}
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp >= min_expected:
                ratios[(r, c)] = {'obs': obs, 'exp': round(exp, 1),
                                  'ratio': round(obs / exp, 2) if exp > 0 else 0}
    return ratios


# ============================================================
# T1: COMPOUND vs ATOMIC C1210 COMPLIANCE
# ============================================================

def test_compliance(tokens):
    """Compare forbidden-pair rates between atomic and compound MIDDLEs."""
    print(f"\n{'='*70}")
    print("T1: COMPOUND vs ATOMIC C1210 FORBIDDEN PAIR COMPLIANCE")
    print("=" * 70)

    atomic = [t for t in tokens if not t['is_compound']]
    compound = [t for t in tokens if t['is_compound']]

    print(f"  Atomic MIDDLEs: {len(atomic)}")
    print(f"  Compound MIDDLEs: {len(compound)}")

    # Build INITIAL->TERMINAL contingency for each group
    atomic_cont = Counter()
    compound_cont = Counter()
    for t in atomic:
        atomic_cont[(t['initial'], t['terminal'])] += 1
    for t in compound:
        compound_cont[(t['initial'], t['terminal'])] += 1

    chi2_a, v_a, _ = cramers_v(atomic_cont)
    chi2_c, v_c, _ = cramers_v(compound_cont)
    mi_a = mutual_info(atomic_cont)
    mi_c = mutual_info(compound_cont)

    print(f"\n  Atomic INITIAL->TERMINAL:   V={v_a:.4f}, MI={mi_a:.4f} bits")
    print(f"  Compound INITIAL->TERMINAL: V={v_c:.4f}, MI={mi_c:.4f} bits")

    # Check forbidden pairs specifically
    print(f"\n  C1210 Forbidden pair counts:")
    print(f"    {'Pair':>8}  {'Atomic obs':>12}  {'Atomic total':>12}  "
          f"{'Compound obs':>14}  {'Compound total':>14}")
    results_forbidden = {}
    for init, term in FORBIDDEN_PAIRS:
        a_obs = atomic_cont.get((init, term), 0)
        c_obs = compound_cont.get((init, term), 0)
        # Total tokens starting with init
        a_total = sum(v for (i, t), v in atomic_cont.items() if i == init)
        c_total = sum(v for (i, t), v in compound_cont.items() if i == init)
        a_rate = a_obs / a_total if a_total > 0 else 0
        c_rate = c_obs / c_total if c_total > 0 else 0
        print(f"    {init}->{term}:    {a_obs:>10}/{a_total:<8} ({a_rate:.3%})    "
              f"{c_obs:>10}/{c_total:<8} ({c_rate:.3%})")
        results_forbidden[f"{init}->{term}"] = {
            'atomic_obs': a_obs, 'atomic_total': a_total, 'atomic_rate': round(a_rate, 5),
            'compound_obs': c_obs, 'compound_total': c_total, 'compound_rate': round(c_rate, 5),
        }

    # Overall enrichment comparison (top enriched/depleted)
    ratios_a = enrichment_ratios(atomic_cont)
    ratios_c = enrichment_ratios(compound_cont, min_expected=3)

    top_a = sorted([(k, v) for k, v in ratios_a.items() if v['ratio'] >= 2.0],
                   key=lambda x: -x[1]['ratio'])[:10]
    top_c = sorted([(k, v) for k, v in ratios_c.items() if v['ratio'] >= 2.0],
                   key=lambda x: -x[1]['ratio'])[:10]

    print(f"\n  Top enriched INITIAL->TERMINAL (>= 2.0x):")
    print(f"    Atomic:")
    for (i, t), info in top_a[:8]:
        print(f"      {i}->{t}: {info['ratio']}x ({info['obs']}/{info['exp']})")
    print(f"    Compound:")
    for (i, t), info in top_c[:8]:
        print(f"      {i}->{t}: {info['ratio']}x ({info['obs']}/{info['exp']})")

    return {
        'n_atomic': len(atomic),
        'n_compound': len(compound),
        'atomic_v': round(v_a, 4),
        'atomic_mi': round(mi_a, 4),
        'compound_v': round(v_c, 4),
        'compound_mi': round(mi_c, 4),
        'forbidden_pairs': results_forbidden,
    }


# ============================================================
# T2: INTERNAL JUNCTION GRAMMAR
# ============================================================

def test_junction_grammar(tokens, core_middles):
    """Analyze transitions at junctions within compound MIDDLEs."""
    print(f"\n{'='*70}")
    print("T2: INTERNAL JUNCTION GRAMMAR (where embedded atoms meet)")
    print("=" * 70)

    compounds = [t for t in tokens if t['is_compound']]

    # Greedy tile each compound
    junction_cont = Counter()  # (terminal_of_tile_i, initial_of_tile_j) -> count
    within_cont = Counter()    # (char_a, char_b) within a tile
    n_junctions = 0
    n_within = 0
    n_tiled = 0
    n_multi_tile = 0
    tile_length_dist = Counter()

    for t in compounds:
        tiles = greedy_tile(t['middle'], core_middles)
        tile_length_dist[len(tiles)] += 1

        if len(tiles) < 2:
            continue
        n_multi_tile += 1

        # Junction transitions
        for j in range(len(tiles) - 1):
            term = tiles[j][-1]
            init = tiles[j + 1][0]
            junction_cont[(term, init)] += 1
            n_junctions += 1

        # Within-tile transitions (for comparison)
        for tile in tiles:
            for k in range(len(tile) - 1):
                within_cont[(tile[k], tile[k + 1])] += 1
                n_within += 1

        n_tiled += 1

    print(f"  Compound MIDDLEs tiled: {n_tiled}")
    print(f"  Multi-tile compounds: {n_multi_tile}")
    print(f"  Junction transitions: {n_junctions}")
    print(f"  Within-tile transitions: {n_within}")

    print(f"\n  Tile count distribution:")
    for n_tiles in sorted(tile_length_dist.keys()):
        print(f"    {n_tiles} tiles: {tile_length_dist[n_tiles]}")

    if n_junctions < 50:
        print("  Too few junctions for analysis")
        return {'n_junctions': n_junctions, 'insufficient': True}

    chi2_j, v_j, _ = cramers_v(junction_cont)
    chi2_w, v_w, _ = cramers_v(within_cont)
    mi_j = mutual_info(junction_cont)
    mi_w = mutual_info(within_cont)

    print(f"\n  Junction transitions: V={v_j:.4f}, MI={mi_j:.4f} bits (n={n_junctions})")
    print(f"  Within-tile transitions: V={v_w:.4f}, MI={mi_w:.4f} bits (n={n_within})")

    # Enrichment at junctions
    ratios_j = enrichment_ratios(junction_cont, min_expected=3)
    enriched = sorted([(k, v) for k, v in ratios_j.items() if v['ratio'] >= 1.5 and v['obs'] >= 5],
                      key=lambda x: -x[1]['ratio'])
    depleted = sorted([(k, v) for k, v in ratios_j.items() if v['ratio'] <= 0.5 and v['exp'] >= 5],
                      key=lambda x: x[1]['ratio'])

    print(f"\n  Junction enriched pairs (>= 1.5x, obs >= 5):")
    for (a, b), info in enriched[:15]:
        print(f"    {a}->{b}: {info['obs']}/{info['exp']} = {info['ratio']}x")

    if depleted:
        print(f"\n  Junction depleted pairs (<= 0.5x, exp >= 5):")
        for (a, b), info in depleted[:15]:
            print(f"    {a}->{b}: {info['obs']}/{info['exp']} = {info['ratio']}x")

    # Check C1210 forbidden pairs at junctions
    print(f"\n  C1210 forbidden pairs at junctions:")
    for init, term in FORBIDDEN_PAIRS:
        obs = junction_cont.get((init, term), 0)  # note: reversed -- term of tile i, init of tile j
        # Actually: junction is (terminal_of_prev, initial_of_next)
        # C1210 forbidden: (INITIAL, TERMINAL) -- here we have (TERMINAL, INITIAL)
        # So we need to check if any junction has the pattern where
        # the terminal atom would be forbidden as INITIAL->TERMINAL
        pass

    # C1210 is about INITIAL->TERMINAL within a MIDDLE
    # Junctions are TERMINAL(tile_i)->INITIAL(tile_j)
    # These are DIFFERENT from C1210 -- they're analogous to C1212
    # Let's check both directions
    print(f"\n  Forbidden-pair atoms at junctions (TERMINAL->INITIAL):")
    for term_atom, init_atom in FORBIDDEN_PAIRS:
        # Check if term_atom->init_atom appears at junctions
        obs = junction_cont.get((term_atom, init_atom), 0)
        total = sum(v for (t, i), v in junction_cont.items() if t == term_atom)
        rate = obs / total if total > 0 else 0
        print(f"    {term_atom}->{init_atom}: {obs}/{total} ({rate:.3%})")
        # And the reverse
        obs_r = junction_cont.get((init_atom, term_atom), 0)
        total_r = sum(v for (t, i), v in junction_cont.items() if t == init_atom)
        rate_r = obs_r / total_r if total_r > 0 else 0
        print(f"    {init_atom}->{term_atom}: {obs_r}/{total_r} ({rate_r:.3%})")

    return {
        'n_compound_tiled': n_tiled,
        'n_multi_tile': n_multi_tile,
        'n_junctions': n_junctions,
        'n_within': n_within,
        'junction_v': round(v_j, 4),
        'junction_mi': round(mi_j, 4),
        'within_v': round(v_w, 4),
        'within_mi': round(mi_w, 4),
        'enriched': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'],
                      'ratio': v['ratio']} for k, v in enriched[:15]],
        'depleted': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'],
                      'ratio': v['ratio']} for k, v in depleted[:15]],
        'tile_distribution': dict(tile_length_dist),
    }


# ============================================================
# T3: JUNCTION vs C1212 CROSS-TOKEN CORRELATION
# ============================================================

def test_junction_vs_cross_token(tokens, core_middles):
    """Compare junction enrichment patterns to C1212 cross-token patterns."""
    print(f"\n{'='*70}")
    print("T3: JUNCTION GRAMMAR vs C1212 CROSS-TOKEN GRAMMAR")
    print("=" * 70)

    # Build junction contingency (same as T2 but we need cross-token too)
    compounds = [t for t in tokens if t['is_compound']]

    junction_cont = Counter()
    for t in compounds:
        tiles = greedy_tile(t['middle'], core_middles)
        if len(tiles) < 2:
            continue
        for j in range(len(tiles) - 1):
            term = tiles[j][-1]
            init = tiles[j + 1][0]
            junction_cont[(term, init)] += 1

    # Build cross-token contingency (TERMINAL(N)->INITIAL(N+1))
    # Need line-grouped data for this
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_' and len(m.middle) >= 2:
            line_groups[(t.folio, t.line)].append({
                'initial': m.middle[0],
                'terminal': m.middle[-1],
            })

    cross_token_cont = Counter()
    for key in sorted(line_groups.keys()):
        toks = line_groups[key]
        for j in range(len(toks) - 1):
            cross_token_cont[(toks[j]['terminal'], toks[j + 1]['initial'])] += 1

    # Compute enrichment ratios for both
    ratios_j = enrichment_ratios(junction_cont, min_expected=3)
    ratios_ct = enrichment_ratios(cross_token_cont, min_expected=5)

    # Find common pairs and compute correlation
    common_pairs = set(ratios_j.keys()) & set(ratios_ct.keys())
    if len(common_pairs) < 5:
        print(f"  Only {len(common_pairs)} common pairs -- insufficient for correlation")
        return {'n_common': len(common_pairs)}

    j_ratios = [ratios_j[p]['ratio'] for p in sorted(common_pairs)]
    ct_ratios = [ratios_ct[p]['ratio'] for p in sorted(common_pairs)]

    # Pearson r
    n = len(j_ratios)
    mean_j = sum(j_ratios) / n
    mean_ct = sum(ct_ratios) / n
    cov = sum((j - mean_j) * (c - mean_ct) for j, c in zip(j_ratios, ct_ratios)) / n
    std_j = (sum((j - mean_j)**2 for j in j_ratios) / n) ** 0.5
    std_ct = (sum((c - mean_ct)**2 for c in ct_ratios) / n) ** 0.5
    r = cov / (std_j * std_ct) if std_j > 0 and std_ct > 0 else 0

    print(f"  Common pairs with enrichment data: {n}")
    print(f"  Correlation of enrichment ratios: r={r:.3f}")
    if r > 0.5:
        print(f"  -> SAME grammar operating at both scales")
    elif r > 0.2:
        print(f"  -> RELATED but distinct grammars")
    else:
        print(f"  -> DIFFERENT grammars at junction vs cross-token level")

    # Show pairs with biggest divergence
    pair_data = []
    for p in sorted(common_pairs):
        j_r = ratios_j[p]['ratio']
        ct_r = ratios_ct[p]['ratio']
        pair_data.append((p, j_r, ct_r, j_r - ct_r))

    pair_data.sort(key=lambda x: -abs(x[3]))
    print(f"\n  Biggest divergences (junction ratio vs cross-token ratio):")
    for (a, b), j_r, ct_r, diff in pair_data[:10]:
        print(f"    {a}->{b}: junction={j_r:.2f}x, cross-token={ct_r:.2f}x, diff={diff:+.2f}")

    # Also show pairs where both are enriched
    both_enriched = [(p, ratios_j[p]['ratio'], ratios_ct[p]['ratio'])
                     for p in common_pairs
                     if ratios_j[p]['ratio'] >= 1.3 and ratios_ct[p]['ratio'] >= 1.3]
    both_enriched.sort(key=lambda x: -(x[1] + x[2]))
    if both_enriched:
        print(f"\n  Pairs enriched at BOTH levels (>= 1.3x):")
        for (a, b), j_r, ct_r in both_enriched[:10]:
            print(f"    {a}->{b}: junction={j_r:.2f}x, cross-token={ct_r:.2f}x")

    both_depleted = [(p, ratios_j[p]['ratio'], ratios_ct[p]['ratio'])
                     for p in common_pairs
                     if ratios_j[p]['ratio'] <= 0.7 and ratios_ct[p]['ratio'] <= 0.7]
    if both_depleted:
        print(f"\n  Pairs depleted at BOTH levels (<= 0.7x):")
        for (a, b), j_r, ct_r in both_depleted[:10]:
            print(f"    {a}->{b}: junction={j_r:.2f}x, cross-token={ct_r:.2f}x")

    return {
        'n_common_pairs': n,
        'correlation_r': round(r, 4),
        'junction_mean_ratio': round(mean_j, 3),
        'cross_token_mean_ratio': round(mean_ct, 3),
        'both_enriched': len(both_enriched),
        'both_depleted': len(both_depleted),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("COMPOUND_SLOT_GRAMMAR -- Phase 432")
    print("=" * 70)

    print("\nLoading data...")
    tokens, core_middles, analyzer = load_data()
    summary = analyzer.summary()
    n_compound = sum(1 for t in tokens if t['is_compound'])
    n_atomic = sum(1 for t in tokens if not t['is_compound'])
    print(f"Loaded {len(tokens)} tokens ({n_atomic} atomic, {n_compound} compound)")
    print(f"Core MIDDLEs in inventory: {summary['core_count']}")

    results = {}

    # T1: Compliance
    results['T1_compliance'] = test_compliance(tokens)

    # T2: Junction grammar
    results['T2_junction_grammar'] = test_junction_grammar(tokens, core_middles)

    # T3: Junction vs cross-token correlation
    results['T3_junction_vs_cross_token'] = test_junction_vs_cross_token(tokens, core_middles)

    # Save
    output_path = RESULTS_DIR / "compound_slot_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
