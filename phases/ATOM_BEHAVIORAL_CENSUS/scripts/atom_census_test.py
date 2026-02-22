"""
ATOM_BEHAVIORAL_CENSUS: Phase 428
==================================
Systematically characterizes ALL atoms in Currier B MIDDLEs across three
dimensions: folio-level co-occurrence (dimensionality), within-line state
carryover, and positional grammar within MIDDLEs.

Context:
  - C1190: Single characters are genuine behavioral atoms (additive)
  - C1197: Only e and i are extensible; 18 others binary
  - C1200: k/e carryover within lines (z=+7.90)
  - C1205: i anti-clusters (z=-6.14), orthogonal to k/e
  - C1060: Compound atom position grammar (V=0.333)
  - C1067: Terminal character determines compound position

Tests:
  T1:  Folio-level atom correlation matrix (dimensionality)
  T1b: Same, excluding daiin/aiin tokens
  T2:  Within-line carryover census for all atoms
  T2b: Same, excluding daiin/aiin tokens
  T3:  Positional grammar within MIDDLEs (per-character)
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_BEHAVIORAL_CENSUS/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000
MIN_ATOM_COUNT_CORR = 50      # min occurrences for T1 correlations
MIN_ATOM_COUNT_CARRY = 30     # min occurrences for T2 carryover
MIN_FOLIO_TOKENS = 20         # min tokens per folio for T1
FDR_ALPHA = 0.05


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all Currier B tokens with morphological decomposition."""
    tx = Transcript()
    morph = Morphology()
    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            tokens.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return tokens


def load_tokens_by_line():
    """Load Currier B tokens grouped by (folio, line), preserving order."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            line_groups[(t.folio, t.line)].append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return line_groups


def discover_atoms(tokens):
    """Find all unique characters in MIDDLE strings."""
    chars = set()
    for t in tokens:
        for ch in t['middle']:
            chars.add(ch)
    return sorted(chars)


def pearson_r(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return 0.0, 1.0  # r, p
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx2 = sum((x - mx)**2 for x in xs)
    dy2 = sum((y - my)**2 for y in ys)
    denom = (dx2 * dy2) ** 0.5
    if denom == 0:
        return 0.0, 1.0
    r = num / denom
    # t-test for significance
    if abs(r) >= 1.0:
        p = 0.0
    else:
        t_stat = r * ((n - 2) / (1 - r * r)) ** 0.5
        # Approximate two-tailed p from t-distribution using normal for large n
        p = 2 * (1 - _norm_cdf(abs(t_stat)))
    return r, p


def _norm_cdf(x):
    """Approximate standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def benjamini_hochberg(p_values, alpha=FDR_ALPHA):
    """Apply Benjamini-Hochberg FDR correction.
    Returns list of (index, p, adjusted_p, significant) tuples."""
    n = len(p_values)
    if n == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * n
    prev_adj = 0
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        adj_p = min(p * n / rank, 1.0)
        adj_p = max(adj_p, prev_adj)  # enforce monotonicity
        prev_adj = adj_p
        results[orig_idx] = (orig_idx, p, adj_p, adj_p < alpha)
    return results


# ============================================================
# T1: ATOM DIMENSIONALITY MAP
# ============================================================

def test_atom_dimensionality(tokens, exclude_aiin=False):
    """Compute folio-level correlation matrix for all atoms."""
    label = "T1" if not exclude_aiin else "T1b"
    suffix = " (excluding aiin)" if exclude_aiin else ""
    print(f"\n{'='*70}")
    print(f"{label}: ATOM DIMENSIONALITY MAP{suffix}")
    print("=" * 70)

    if exclude_aiin:
        tokens = [t for t in tokens if 'aiin' not in t['middle']]
        print(f"  After aiin exclusion: {len(tokens)} tokens")

    atoms = discover_atoms(tokens)
    print(f"  Atoms found: {', '.join(atoms)} ({len(atoms)} total)")

    # Pre-compute per-folio atom character counts
    folio_chars = defaultdict(lambda: defaultdict(int))  # folio -> atom -> count
    folio_total = defaultdict(int)  # folio -> total chars

    for t in tokens:
        mid = t['middle']
        f = t['folio']
        folio_total[f] += len(mid)
        for ch in mid:
            folio_chars[f][ch] += 1

    # Filter folios with enough tokens
    valid_folios = [f for f in folio_total if folio_total[f] >= MIN_FOLIO_TOKENS]
    valid_folios.sort()
    print(f"  Folios with {MIN_FOLIO_TOKENS}+ chars: {len(valid_folios)}")

    # Filter atoms with enough total occurrences
    atom_totals = Counter()
    for f in valid_folios:
        for a in atoms:
            atom_totals[a] += folio_chars[f].get(a, 0)

    valid_atoms = [a for a in atoms if atom_totals[a] >= MIN_ATOM_COUNT_CORR]
    print(f"  Atoms with {MIN_ATOM_COUNT_CORR}+ occurrences: {', '.join(valid_atoms)} ({len(valid_atoms)})")

    excluded_atoms = [a for a in atoms if a not in valid_atoms]
    if excluded_atoms:
        print(f"  Excluded (too rare): {', '.join(excluded_atoms)}")

    # Build folio-level fraction vectors
    folio_fracs = {}  # atom -> list of fractions (one per folio)
    for a in valid_atoms:
        folio_fracs[a] = [folio_chars[f].get(a, 0) / folio_total[f] for f in valid_folios]

    # Compute pairwise correlation matrix
    n_atoms = len(valid_atoms)
    corr_matrix = [[0.0] * n_atoms for _ in range(n_atoms)]
    p_matrix = [[1.0] * n_atoms for _ in range(n_atoms)]
    pairs = []

    for i in range(n_atoms):
        corr_matrix[i][i] = 1.0
        p_matrix[i][i] = 0.0
        for j in range(i + 1, n_atoms):
            r, p = pearson_r(folio_fracs[valid_atoms[i]], folio_fracs[valid_atoms[j]])
            corr_matrix[i][j] = r
            corr_matrix[j][i] = r
            p_matrix[i][j] = p
            p_matrix[j][i] = p
            pairs.append((valid_atoms[i], valid_atoms[j], r, p))

    # FDR correction on all pairwise p-values
    all_p = [p[3] for p in pairs]
    fdr_results = benjamini_hochberg(all_p)
    sig_pairs = []
    for idx, (_, raw_p, adj_p, sig) in enumerate(fdr_results):
        a1, a2, r, _ = pairs[idx]
        if sig:
            sig_pairs.append((a1, a2, round(r, 3), round(adj_p, 4)))

    sig_pairs.sort(key=lambda x: -abs(x[2]))

    # Print correlation matrix
    print(f"\n  Correlation matrix (top triangle, {len(valid_atoms)} atoms):")
    header = "  " + " " * 6 + "".join(f"{a:>6}" for a in valid_atoms)
    print(header)
    for i, a in enumerate(valid_atoms):
        row = f"  {a:>4}  "
        for j in range(n_atoms):
            if j < i:
                row += "      "
            else:
                r = corr_matrix[i][j]
                row += f"{r:+6.3f}"[0:6]
        print(row)

    # Print significant pairs
    print(f"\n  Significant pairs (FDR < {FDR_ALPHA}): {len(sig_pairs)} of {len(pairs)}")
    if sig_pairs:
        print(f"  {'Pair':<8} {'r':>8} {'adj-p':>8}")
        print(f"  {'-'*24}")
        for a1, a2, r, adj_p in sig_pairs[:30]:
            print(f"  {a1}-{a2:<5} {r:+8.3f} {adj_p:8.4f}")

    # Identify clusters: strong positive correlations (r > 0.3)
    pos_clusters = [(a1, a2, r) for a1, a2, r, _ in sig_pairs if r > 0.3]
    neg_clusters = [(a1, a2, r) for a1, a2, r, _ in sig_pairs if r < -0.3]

    if pos_clusters:
        print(f"\n  Positive clusters (r > 0.3):")
        for a1, a2, r in pos_clusters:
            print(f"    {a1}-{a2}: r={r:+.3f}")

    if neg_clusters:
        print(f"\n  Anti-correlations (r < -0.3):")
        for a1, a2, r in neg_clusters:
            print(f"    {a1}-{a2}: r={r:+.3f}")

    # Global atom frequency summary
    print(f"\n  Atom frequency summary (MIDDLE chars only):")
    total_chars = sum(folio_total[f] for f in valid_folios)
    print(f"  {'Atom':<6} {'Count':>8} {'Fraction':>10}")
    print(f"  {'-'*24}")
    for a in valid_atoms:
        ct = atom_totals[a]
        print(f"  {a:<6} {ct:>8} {ct/total_chars:>10.4f}")

    return {
        'atoms': valid_atoms,
        'matrix': [[round(corr_matrix[i][j], 4) for j in range(n_atoms)] for i in range(n_atoms)],
        'significant_pairs': sig_pairs,
        'n_folios': len(valid_folios),
        'n_pairs_tested': len(pairs),
        'n_significant': len(sig_pairs),
        'atom_counts': {a: atom_totals[a] for a in valid_atoms},
        'excluded_atoms': excluded_atoms,
    }


# ============================================================
# T2: CARRYOVER CENSUS
# ============================================================

def test_carryover_census(line_groups, exclude_aiin=False):
    """Run carryover test for ALL atoms simultaneously."""
    label = "T2" if not exclude_aiin else "T2b"
    suffix = " (excluding aiin)" if exclude_aiin else ""
    print(f"\n{'='*70}")
    print(f"{label}: CARRYOVER CENSUS{suffix}")
    print("=" * 70)

    # Discover atoms from line_groups
    all_atoms = set()
    for key in line_groups:
        for t in line_groups[key]:
            for ch in t['middle']:
                all_atoms.add(ch)
    all_atoms = sorted(all_atoms)

    # Count total occurrences to filter rare atoms
    atom_total = Counter()
    for key in line_groups:
        tokens = line_groups[key]
        if exclude_aiin:
            tokens = [t for t in tokens if 'aiin' not in t['middle']]
        for t in tokens:
            for ch in set(t['middle']):  # count tokens containing atom, not chars
                atom_total[ch] += 1

    valid_atoms = [a for a in all_atoms if atom_total[a] >= MIN_ATOM_COUNT_CARRY]
    print(f"  Atoms with {MIN_ATOM_COUNT_CARRY}+ tokens: {', '.join(valid_atoms)} ({len(valid_atoms)})")

    # Pre-filter lines for aiin exclusion (avoid re-filtering in hot loop)
    if exclude_aiin:
        filtered_groups = {}
        for key in line_groups:
            filtered = [t for t in line_groups[key] if 'aiin' not in t['middle']]
            if len(filtered) >= 2:
                filtered_groups[key] = filtered
    else:
        filtered_groups = {k: v for k, v in line_groups.items() if len(v) >= 2}

    # OBSERVED: compute carryover for each atom
    def compute_carryover(groups):
        """Compute carryover deltas for all atoms from grouped tokens."""
        # For each atom: count (given, given_hit) and (not_given, not_given_hit)
        given = {a: 0 for a in valid_atoms}
        given_hit = {a: 0 for a in valid_atoms}
        not_given = {a: 0 for a in valid_atoms}
        not_given_hit = {a: 0 for a in valid_atoms}

        for key in groups:
            tokens = groups[key]
            for j in range(len(tokens) - 1):
                mid_a = tokens[j]['middle']
                mid_b = tokens[j + 1]['middle']
                a_atoms = set(mid_a)
                b_atoms = set(mid_b)
                for atom in valid_atoms:
                    if atom in a_atoms:
                        given[atom] += 1
                        if atom in b_atoms:
                            given_hit[atom] += 1
                    else:
                        not_given[atom] += 1
                        if atom in b_atoms:
                            not_given_hit[atom] += 1

        deltas = {}
        for atom in valid_atoms:
            p_g = given_hit[atom] / given[atom] if given[atom] > 0 else 0
            p_ng = not_given_hit[atom] / not_given[atom] if not_given[atom] > 0 else 0
            deltas[atom] = p_g - p_ng
        return deltas, given, given_hit, not_given, not_given_hit

    observed_deltas, obs_given, obs_given_hit, obs_not_given, obs_not_given_hit = compute_carryover(filtered_groups)

    # SHUFFLE TEST: permute MIDDLEs within each line
    print(f"  Running {N_PERMUTATIONS} shuffle permutations for {len(valid_atoms)} atoms...")
    random.seed(42)
    perm_deltas_all = {a: [] for a in valid_atoms}

    for perm_i in range(N_PERMUTATIONS):
        # Build shuffled version: shuffle MIDDLEs within each line
        shuffled_groups = {}
        for key in filtered_groups:
            tokens = filtered_groups[key]
            middles = [t['middle'] for t in tokens]
            random.shuffle(middles)
            # Create pseudo-tokens with shuffled middles
            shuffled_groups[key] = [{'middle': m} for m in middles]

        perm_d, _, _, _, _ = compute_carryover(shuffled_groups)
        for atom in valid_atoms:
            perm_deltas_all[atom].append(perm_d[atom])

        if (perm_i + 1) % 200 == 0:
            print(f"    ... {perm_i + 1}/{N_PERMUTATIONS}")

    # Compute z-scores and classify
    results = {}
    print(f"\n  {'Atom':<6} {'P(B|A)':<10} {'P(B|~A)':<10} {'Delta':<10} {'z-score':<10} {'Class':<15}")
    print(f"  {'-'*61}")

    for atom in valid_atoms:
        p_g = obs_given_hit[atom] / obs_given[atom] if obs_given[atom] > 0 else 0
        p_ng = obs_not_given_hit[atom] / obs_not_given[atom] if obs_not_given[atom] > 0 else 0
        delta = observed_deltas[atom]

        perm_list = perm_deltas_all[atom]
        perm_mean = sum(perm_list) / len(perm_list)
        perm_std = (sum((d - perm_mean)**2 for d in perm_list) / len(perm_list)) ** 0.5
        z = (delta - perm_mean) / perm_std if perm_std > 0 else 0

        if z > 2:
            cls = "POSITIVE"
        elif z < -2:
            cls = "NEGATIVE"
        else:
            cls = "NEUTRAL"

        print(f"  {atom:<6} {p_g:<10.4f} {p_ng:<10.4f} {delta:<+10.4f} {z:<+10.2f} {cls:<15}")

        results[atom] = {
            'p_given': round(p_g, 4),
            'p_given_not': round(p_ng, 4),
            'delta': round(delta, 4),
            'z_score': round(z, 2),
            'class': cls,
            'n_given': obs_given[atom],
            'n_not_given': obs_not_given[atom],
        }

    # Cross-line carryover (brief)
    print(f"\n  Cross-line carryover (last token line N -> first token line N+1):")
    sorted_keys = sorted(filtered_groups.keys())
    cross_given = {a: 0 for a in valid_atoms}
    cross_given_hit = {a: 0 for a in valid_atoms}
    cross_not_given = {a: 0 for a in valid_atoms}
    cross_not_given_hit = {a: 0 for a in valid_atoms}

    for idx in range(len(sorted_keys) - 1):
        key_a = sorted_keys[idx]
        key_b = sorted_keys[idx + 1]
        if key_a[0] != key_b[0]:  # different folio
            continue
        tokens_a = filtered_groups[key_a]
        tokens_b = filtered_groups[key_b]
        mid_a = tokens_a[-1]['middle']
        mid_b = tokens_b[0]['middle']
        a_atoms = set(mid_a)
        b_atoms = set(mid_b)
        for atom in valid_atoms:
            if atom in a_atoms:
                cross_given[atom] += 1
                if atom in b_atoms:
                    cross_given_hit[atom] += 1
            else:
                cross_not_given[atom] += 1
                if atom in b_atoms:
                    cross_not_given_hit[atom] += 1

    print(f"  {'Atom':<6} {'Within-delta':<14} {'Cross-delta':<14} {'Ratio':<10}")
    print(f"  {'-'*44}")
    for atom in valid_atoms:
        p_cg = cross_given_hit[atom] / cross_given[atom] if cross_given[atom] > 0 else 0
        p_cng = cross_not_given_hit[atom] / cross_not_given[atom] if cross_not_given[atom] > 0 else 0
        cross_delta = p_cg - p_cng
        within_delta = observed_deltas[atom]
        ratio = within_delta / cross_delta if abs(cross_delta) > 0.001 else float('inf')
        print(f"  {atom:<6} {within_delta:<+14.4f} {cross_delta:<+14.4f} {ratio:<10.1f}")
        results[atom]['cross_delta'] = round(cross_delta, 4)

    # Summary
    pos_atoms = [a for a in valid_atoms if results[a]['class'] == 'POSITIVE']
    neg_atoms = [a for a in valid_atoms if results[a]['class'] == 'NEGATIVE']
    neu_atoms = [a for a in valid_atoms if results[a]['class'] == 'NEUTRAL']
    print(f"\n  Summary:")
    print(f"    POSITIVE carryover: {', '.join(pos_atoms)} ({len(pos_atoms)})")
    print(f"    NEGATIVE (anti-cluster): {', '.join(neg_atoms)} ({len(neg_atoms)})")
    print(f"    NEUTRAL: {', '.join(neu_atoms)} ({len(neu_atoms)})")

    return results


# ============================================================
# T3: POSITIONAL GRAMMAR WITHIN MIDDLEs
# ============================================================

def test_positional_grammar(tokens):
    """Map where each atom prefers to sit within MIDDLE strings."""
    print(f"\n{'='*70}")
    print("T3: POSITIONAL GRAMMAR WITHIN MIDDLEs")
    print("=" * 70)

    # Only use MIDDLEs with length >= 2 (single-char trivially at all positions)
    multi_char = [t for t in tokens if len(t['middle']) >= 2]
    print(f"  Tokens with MIDDLE len >= 2: {len(multi_char)} of {len(tokens)}")

    # For each character occurrence, record its normalized position
    atom_positions = defaultdict(list)  # atom -> list of normalized positions
    atom_pos_counts = defaultdict(lambda: {'initial': 0, 'terminal': 0, 'medial': 0, 'total': 0})

    for t in multi_char:
        mid = t['middle']
        n = len(mid)
        for pos, ch in enumerate(mid):
            norm_pos = pos / (n - 1)  # 0.0 = first, 1.0 = last
            atom_positions[ch].append(norm_pos)
            atom_pos_counts[ch]['total'] += 1
            if pos == 0:
                atom_pos_counts[ch]['initial'] += 1
            elif pos == n - 1:
                atom_pos_counts[ch]['terminal'] += 1
            else:
                atom_pos_counts[ch]['medial'] += 1

    # Also count single-char MIDDLEs separately
    single_char = [t for t in tokens if len(t['middle']) == 1]
    single_counts = Counter(t['middle'] for t in single_char)
    print(f"  Single-char MIDDLEs: {len(single_char)}")

    valid_atoms = sorted([a for a in atom_positions if atom_pos_counts[a]['total'] >= 30])
    print(f"  Atoms with 30+ positional observations: {', '.join(valid_atoms)} ({len(valid_atoms)})")

    # Compute statistics per atom
    results = {}
    print(f"\n  {'Atom':<6} {'N':>6} {'MeanPos':>8} {'Initial%':>9} {'Terminal%':>10} {'Medial%':>8} {'Chi2':>8} {'p':>10} {'Bias':<10}")
    print(f"  {'-'*75}")

    all_p_values = []
    atom_order = []

    for atom in valid_atoms:
        positions = atom_positions[atom]
        counts = atom_pos_counts[atom]
        n = counts['total']
        mean_pos = sum(positions) / n

        init_frac = counts['initial'] / n
        term_frac = counts['terminal'] / n
        med_frac = counts['medial'] / n

        # Chi-squared: observed vs uniform expectation
        # For a MIDDLE of length L, expected fractions depend on L distribution
        # Simpler: compare to overall average across all atoms
        # Use global proportions as expected
        total_all = sum(atom_pos_counts[a]['total'] for a in valid_atoms)
        global_init = sum(atom_pos_counts[a]['initial'] for a in valid_atoms) / total_all
        global_term = sum(atom_pos_counts[a]['terminal'] for a in valid_atoms) / total_all
        global_med = sum(atom_pos_counts[a]['medial'] for a in valid_atoms) / total_all

        exp_init = n * global_init
        exp_term = n * global_term
        exp_med = n * global_med

        chi2 = 0
        for obs, exp in [(counts['initial'], exp_init),
                         (counts['terminal'], exp_term),
                         (counts['medial'], exp_med)]:
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

        # Approximate p-value for chi2 with df=2
        p_val = math.exp(-chi2 / 2) if chi2 < 50 else 0.0

        # Determine bias
        if init_frac > global_init * 1.5 and init_frac > term_frac:
            bias = "INITIAL"
        elif term_frac > global_term * 1.5 and term_frac > init_frac:
            bias = "TERMINAL"
        elif med_frac > global_med * 1.5:
            bias = "MEDIAL"
        else:
            bias = "NEUTRAL"

        all_p_values.append(p_val)
        atom_order.append(atom)

        print(f"  {atom:<6} {n:>6} {mean_pos:>8.3f} {init_frac:>8.1%} {term_frac:>9.1%} {med_frac:>8.1%} {chi2:>8.1f} {p_val:>10.4f} {bias:<10}")

        results[atom] = {
            'n': n,
            'mean_pos': round(mean_pos, 4),
            'initial_frac': round(init_frac, 4),
            'terminal_frac': round(term_frac, 4),
            'medial_frac': round(med_frac, 4),
            'chi2': round(chi2, 1),
            'p': round(p_val, 6),
            'bias': bias,
            'single_char_count': single_counts.get(atom, 0),
        }

    # FDR correction
    fdr = benjamini_hochberg(all_p_values)
    sig_count = 0
    for idx, (_, raw_p, adj_p, sig) in enumerate(fdr):
        atom = atom_order[idx]
        results[atom]['p_adj'] = round(adj_p, 6)
        results[atom]['significant'] = sig
        if sig:
            sig_count += 1

    print(f"\n  FDR-significant atoms: {sig_count} of {len(valid_atoms)}")

    # Global position distribution (for reference)
    total_all = sum(atom_pos_counts[a]['total'] for a in valid_atoms)
    print(f"\n  Global position fractions:")
    print(f"    INITIAL: {global_init:.3f}")
    print(f"    TERMINAL: {global_term:.3f}")
    print(f"    MEDIAL: {global_med:.3f}")

    # Summary by bias class
    for bias_class in ['INITIAL', 'TERMINAL', 'MEDIAL', 'NEUTRAL']:
        atoms_in_class = [a for a in valid_atoms if results[a]['bias'] == bias_class]
        if atoms_in_class:
            print(f"\n  {bias_class} atoms: {', '.join(atoms_in_class)}")
            for a in atoms_in_class:
                print(f"    {a}: mean_pos={results[a]['mean_pos']:.3f}, init={results[a]['initial_frac']:.3f}, term={results[a]['terminal_frac']:.3f}")

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("ATOM BEHAVIORAL CENSUS -- Phase 428")
    print("=" * 70)

    print("\nLoading data...")
    tokens = load_data()
    line_groups = load_tokens_by_line()
    n_tokens = len(tokens)
    n_lines = len(line_groups)
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    atoms = discover_atoms(tokens)
    print(f"Atom inventory: {', '.join(atoms)} ({len(atoms)} atoms)")

    results = {}

    # T1: Atom dimensionality map
    results['T1_correlation_matrix'] = test_atom_dimensionality(tokens, exclude_aiin=False)

    # T1b: Same without aiin
    results['T1b_correlation_no_aiin'] = test_atom_dimensionality(tokens, exclude_aiin=True)

    # T2: Carryover census
    results['T2_carryover_census'] = test_carryover_census(line_groups, exclude_aiin=False)

    # T2b: Same without aiin
    results['T2b_carryover_no_aiin'] = test_carryover_census(line_groups, exclude_aiin=True)

    # T3: Positional grammar
    results['T3_positional_grammar'] = test_positional_grammar(tokens)

    # Save
    output_path = RESULTS_DIR / "atom_census_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
