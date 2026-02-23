"""
PREFIX_ATOM_ROLES: Phase 434
============================
Tests whether PREFIX characters function as compositional atoms with
position-specific roles (base, modifier, phase), analogous to MIDDLE
atom grammar but encoding a different "part of speech."

Tests:
  T1: PREFIX internal positional grammar (do characters have consistent positions?)
  T2: Base character behavioral profiles (does last char predict MIDDLE content?)
  T3: Modifier character behavioral profiles (does modifier shift atom profile consistently?)
  T4: Per-PREFIX MIDDLE content profiles (formalized, with cosine similarity + shuffle)
  T5: Folio-level PREFIX correlation matrix
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/PREFIX_ATOM_ROLES/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000
MIN_PREFIX_TOKENS = 30
MIN_FOLIO_TOKENS = 5
MIN_FOLIOS_PREFIX = 10
FDR_ALPHA = 0.05

AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
    'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER', 'q': 'OTHER',
}
AXIS_NAMES = ['ITERATION', 'ENERGY', 'STABILITY', 'MONITORING', 'CLOSURE', 'STRUCTURAL', 'FREE', 'OTHER']


# ============================================================
# STAT UTILITIES (from atom_census_test.py)
# ============================================================

def pearson_r(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0, 1.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx2 = sum((x - mx)**2 for x in xs)
    dy2 = sum((y - my)**2 for y in ys)
    denom = (dx2 * dy2) ** 0.5
    if denom == 0:
        return 0.0, 1.0
    r = num / denom
    if abs(r) >= 1.0:
        p = 0.0
    else:
        t_stat = r * ((n - 2) / (1 - r * r)) ** 0.5
        p = 2 * (1 - _norm_cdf(abs(t_stat)))
    return r, p


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def benjamini_hochberg(p_values, alpha=FDR_ALPHA):
    n = len(p_values)
    if n == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * n
    prev_adj = 0
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        adj_p = min(p * n / rank, 1.0)
        adj_p = max(adj_p, prev_adj)
        prev_adj = adj_p
        results[orig_idx] = (orig_idx, p, adj_p, adj_p < alpha)
    return results


def cosine_sim(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sum(a * a for a in v1) ** 0.5
    n2 = sum(b * b for b in v2) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    tx = Transcript()
    morph = Morphology()
    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            tokens.append({
                'word': t.word,
                'prefix': m.prefix or 'BARE',
                'middle': m.middle,
                'suffix': m.suffix or 'NONE',
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return tokens


def get_axis_vector(atom_counter, total):
    """Convert atom counter to axis fraction vector."""
    vec = []
    for axis in AXIS_NAMES:
        axis_atoms = [a for a, ax in AXIS.items() if ax == axis]
        count = sum(atom_counter.get(a, 0) for a in axis_atoms)
        vec.append(count / total if total > 0 else 0)
    return vec


def get_atom_vector(atom_counter, total, all_atoms):
    """Convert atom counter to full atom fraction vector."""
    return [atom_counter.get(a, 0) / total if total > 0 else 0 for a in all_atoms]


# ============================================================
# T1: PREFIX INTERNAL POSITIONAL GRAMMAR
# ============================================================

def test_positional_grammar(tokens, prefix_counts):
    print(f"\n{'='*70}")
    print("T1: PREFIX INTERNAL POSITIONAL GRAMMAR")
    print("=" * 70)

    # Count character occurrences at each position within PREFIXes
    char_positions = defaultdict(lambda: Counter())  # char -> {pos: count}
    prefix_lengths = Counter()

    for pre, count in prefix_counts.items():
        if pre == 'BARE' or count < MIN_PREFIX_TOKENS:
            continue
        for pos, ch in enumerate(pre):
            # Normalize position: for 2-char prefix, pos 0=modifier, pos 1=base
            # For 3-char prefix, pos 0=phase, pos 1=modifier, pos 2=base
            char_positions[ch][pos] += count
        prefix_lengths[len(pre)] += count

    print(f"  PREFIX length distribution: {dict(prefix_lengths)}")

    # For each character, compute positional preference
    all_chars = sorted(char_positions.keys())
    results = {}

    print(f"\n  {'Char':>4}  {'Pos0':>6}  {'Pos1':>6}  {'Pos2':>6}  {'Total':>6}  {'Primary':>7}  {'Conc':>5}")
    print(f"  {'----':>4}  {'----':>6}  {'----':>6}  {'----':>6}  {'-----':>6}  {'-------':>7}  {'----':>5}")

    for ch in all_chars:
        counts = char_positions[ch]
        total = sum(counts.values())
        if total < 50:
            continue
        p0 = counts.get(0, 0)
        p1 = counts.get(1, 0)
        p2 = counts.get(2, 0)
        fracs = {0: p0/total, 1: p1/total, 2: p2/total}
        primary_pos = max(fracs, key=fracs.get)
        conc = fracs[primary_pos]

        # Chi-squared vs uniform
        expected = total / max(len(counts), 1)
        chi2 = sum((counts.get(p, 0) - expected)**2 / expected for p in counts if expected > 0)

        pos_labels = {0: 'POS-0', 1: 'POS-1', 2: 'POS-2'}
        print(f"  {ch:>4}  {p0:>6}  {p1:>6}  {p2:>6}  {total:>6}  {pos_labels[primary_pos]:>7}  {conc:>4.0%}")

        results[ch] = {
            'pos0': p0, 'pos1': p1, 'pos2': p2, 'total': total,
            'primary_pos': primary_pos, 'concentration': round(conc, 3),
            'chi2': round(chi2, 2),
        }

    # Classify: which chars are BASES (position-final) vs MODIFIERS (position-0)?
    bases = [ch for ch, r in results.items() if r['primary_pos'] == max(len(p) - 1 for p in prefix_counts if ch in p and prefix_counts[p] >= MIN_PREFIX_TOKENS and p != 'BARE')]
    print(f"\n  Base candidates (position-final): {[ch for ch, r in results.items() if r['pos1'] > r['pos0'] and r['pos1'] > r.get('pos2', 0)]}")
    print(f"  Modifier candidates (position-0): {[ch for ch, r in results.items() if r['pos0'] > r['pos1']]}")

    return results


# ============================================================
# T2: BASE CHARACTER BEHAVIORAL PROFILES
# ============================================================

def test_base_profiles(tokens, prefix_counts):
    print(f"\n{'='*70}")
    print("T2: BASE CHARACTER BEHAVIORAL PROFILES")
    print("=" * 70)

    valid = {p for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS and p != 'BARE'}

    # Group prefixes by last character (base)
    base_groups = defaultdict(list)
    for pre in valid:
        base = pre[-1]
        base_groups[base].append(pre)

    print(f"  Base groups:")
    for base in sorted(base_groups.keys()):
        members = sorted(base_groups[base])
        total = sum(prefix_counts[p] for p in members)
        print(f"    {base}: {members} ({total} tokens)")

    # Pre-compute per-prefix token groups
    prefix_tokens = defaultdict(list)
    for t in tokens:
        if t['prefix'] in valid:
            prefix_tokens[t['prefix']].append(t)

    # Compute axis profiles per base group
    all_atoms = sorted(set(AXIS.keys()))
    base_results = {}

    print(f"\n  {'Base':>4}  {'N':>5}  {'ITER':>5}  {'ENRG':>5}  {'STAB':>5}  {'MON':>5}  {'CLOS':>5}  {'STRC':>5}  {'FREE':>5}")
    print(f"  {'----':>4}  {'---':>5}  {'----':>5}  {'----':>5}  {'----':>5}  {'---':>5}  {'----':>5}  {'----':>5}  {'----':>5}")

    for base in sorted(base_groups.keys()):
        members = base_groups[base]
        atom_counts = Counter()
        total_chars = 0
        for pre in members:
            for t in prefix_tokens[pre]:
                for ch in t['middle']:
                    atom_counts[ch] += 1
                    total_chars += 1

        axis_vec = get_axis_vector(atom_counts, total_chars)
        n_tokens = sum(prefix_counts[p] for p in members)

        print(f"  {base:>4}  {n_tokens:>5}  " + "  ".join(f"{v:>4.0%}" for v in axis_vec))

        base_results[base] = {
            'members': members,
            'n_tokens': n_tokens,
            'n_middle_chars': total_chars,
            'axis_fractions': {ax: round(v, 4) for ax, v in zip(AXIS_NAMES, axis_vec)},
            'atom_fractions': {a: round(atom_counts.get(a, 0) / total_chars, 4) if total_chars > 0 else 0 for a in all_atoms},
        }

    # Test: does base predict axis profile? Compare between-base vs within-base variance
    # Compute per-prefix axis vectors, then compare
    prefix_vectors = {}
    for pre in valid:
        atom_counts = Counter()
        total_chars = 0
        for t in prefix_tokens[pre]:
            for ch in t['middle']:
                atom_counts[ch] += 1
                total_chars += 1
        if total_chars > 0:
            prefix_vectors[pre] = get_axis_vector(atom_counts, total_chars)

    # Within-base mean cosine similarity
    within_sims = []
    for base, members in base_groups.items():
        vecs = [prefix_vectors[m] for m in members if m in prefix_vectors]
        if len(vecs) < 2:
            continue
        for i in range(len(vecs)):
            for j in range(i+1, len(vecs)):
                within_sims.append(cosine_sim(vecs[i], vecs[j]))

    # Between-base mean cosine similarity
    between_sims = []
    all_bases = sorted(base_groups.keys())
    for bi in range(len(all_bases)):
        for bj in range(bi+1, len(all_bases)):
            vecs_i = [prefix_vectors[m] for m in base_groups[all_bases[bi]] if m in prefix_vectors]
            vecs_j = [prefix_vectors[m] for m in base_groups[all_bases[bj]] if m in prefix_vectors]
            for vi in vecs_i:
                for vj in vecs_j:
                    between_sims.append(cosine_sim(vi, vj))

    within_mean = sum(within_sims) / len(within_sims) if within_sims else 0
    between_mean = sum(between_sims) / len(between_sims) if between_sims else 0

    print(f"\n  Within-base mean cosine: {within_mean:.3f} ({len(within_sims)} pairs)")
    print(f"  Between-base mean cosine: {between_mean:.3f} ({len(between_sims)} pairs)")
    print(f"  Ratio (within/between): {within_mean/between_mean:.2f}" if between_mean > 0 else "")

    base_results['_summary'] = {
        'within_base_cosine': round(within_mean, 4),
        'between_base_cosine': round(between_mean, 4),
        'ratio': round(within_mean / between_mean, 3) if between_mean > 0 else None,
    }

    return base_results


# ============================================================
# T3: MODIFIER CHARACTER BEHAVIORAL PROFILES
# ============================================================

def test_modifier_profiles(tokens, prefix_counts):
    print(f"\n{'='*70}")
    print("T3: MODIFIER CHARACTER BEHAVIORAL PROFILES")
    print("=" * 70)

    valid = {p for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS and p != 'BARE'}

    # Pre-compute per-prefix MIDDLE atom profiles
    prefix_atom_profiles = {}
    for pre in valid:
        atom_counts = Counter()
        total = 0
        for t in tokens:
            if t['prefix'] == pre:
                for ch in t['middle']:
                    atom_counts[ch] += 1
                    total += 1
        if total > 0:
            prefix_atom_profiles[pre] = {
                'atoms': dict(atom_counts),
                'total': total,
                'axis_vec': get_axis_vector(atom_counts, total),
            }

    # Group by base, then compare modifiers within each base group
    base_groups = defaultdict(list)
    for pre in valid:
        base = pre[-1]
        base_groups[base].append(pre)

    results = {}

    for base in sorted(base_groups.keys()):
        members = sorted(base_groups[base])
        if len(members) < 2:
            continue

        print(f"\n  Base '{base}' group: {members}")
        print(f"  {'PREFIX':>8}  {'Modifier':>8}  {'ITER':>5}  {'ENRG':>5}  {'STAB':>5}  {'MON':>5}  {'CLOS':>5}  {'STRC':>5}  {'FREE':>5}  {'N':>5}")

        group_data = {}
        for pre in members:
            if pre not in prefix_atom_profiles:
                continue
            prof = prefix_atom_profiles[pre]
            modifier = pre[:-1] if len(pre) > 1 else '-'
            vec = prof['axis_vec']
            n = prefix_counts[pre]
            print(f"  {pre:>8}  {modifier:>8}  " + "  ".join(f"{v:>4.0%}" for v in vec) + f"  {n:>5}")
            group_data[pre] = {'modifier': modifier, 'axis_vec': vec, 'n': n}

        results[base] = group_data

    # Cross-base modifier consistency: does the same modifier do the same thing across bases?
    print(f"\n  CROSS-BASE MODIFIER CONSISTENCY:")
    modifier_across_bases = defaultdict(list)  # modifier -> [(base, prefix, axis_vec)]
    for pre in valid:
        if len(pre) < 2:
            continue
        modifier = pre[0]
        base = pre[-1]
        if pre in prefix_atom_profiles:
            modifier_across_bases[modifier].append((base, pre, prefix_atom_profiles[pre]['axis_vec']))

    cross_results = {}
    for mod in sorted(modifier_across_bases.keys()):
        entries = modifier_across_bases[mod]
        if len(entries) < 2:
            continue
        # Compute mean pairwise cosine similarity
        sims = []
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                s = cosine_sim(entries[i][2], entries[j][2])
                sims.append(s)
        mean_sim = sum(sims) / len(sims) if sims else 0
        prefixes = [e[1] for e in entries]
        print(f"    Modifier '{mod}' appears in: {prefixes}, mean cosine={mean_sim:.3f}")
        cross_results[mod] = {
            'prefixes': prefixes,
            'mean_cosine': round(mean_sim, 3),
            'n_pairs': len(sims),
        }

    results['_cross_base'] = cross_results
    return results


# ============================================================
# T4: PER-PREFIX MIDDLE CONTENT PROFILES
# ============================================================

def test_prefix_content_profiles(tokens, prefix_counts):
    print(f"\n{'='*70}")
    print("T4: PER-PREFIX MIDDLE CONTENT PROFILES")
    print("=" * 70)

    valid = sorted(p for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS and p != 'BARE')

    # Compute per-prefix atom profiles
    all_atoms = sorted(set(AXIS.keys()))
    prefix_data = {}

    for pre in valid:
        atom_counts = Counter()
        total = 0
        for t in tokens:
            if t['prefix'] == pre:
                for ch in t['middle']:
                    atom_counts[ch] += 1
                    total += 1
        axis_vec = get_axis_vector(atom_counts, total)
        atom_vec = get_atom_vector(atom_counts, total, all_atoms)
        prefix_data[pre] = {
            'n_tokens': prefix_counts[pre],
            'n_chars': total,
            'axis_vec': axis_vec,
            'atom_vec': atom_vec,
            'axis_fracs': {ax: round(v, 4) for ax, v in zip(AXIS_NAMES, axis_vec)},
        }

    # Print axis table
    print(f"\n  {'PRE':>8}  {'N':>5}  {'ITER':>5}  {'ENRG':>5}  {'STAB':>5}  {'MON':>5}  {'CLOS':>5}  {'STRC':>5}  {'FREE':>5}  {'OTHR':>5}")
    print(f"  {'---':>8}  {'---':>5}  {'----':>5}  {'----':>5}  {'----':>5}  {'---':>5}  {'----':>5}  {'----':>5}  {'----':>5}  {'----':>5}")
    for pre in valid:
        d = prefix_data[pre]
        print(f"  {pre:>8}  {d['n_tokens']:>5}  " + "  ".join(f"{v:>4.0%}" for v in d['axis_vec']))

    # Cosine similarity matrix
    n = len(valid)
    sim_matrix = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim_matrix[i][j] = cosine_sim(prefix_data[valid[i]]['atom_vec'],
                                          prefix_data[valid[j]]['atom_vec'])

    # Prep group similarity
    prep_prefixes = [p for p in ['pch', 'tch', 'dch', 'te', 'lch'] if p in valid]
    prep_sims = []
    for i in range(len(prep_prefixes)):
        for j in range(i+1, len(prep_prefixes)):
            idx_i = valid.index(prep_prefixes[i])
            idx_j = valid.index(prep_prefixes[j])
            prep_sims.append(sim_matrix[idx_i][idx_j])
    prep_mean = sum(prep_sims) / len(prep_sims) if prep_sims else 0

    print(f"\n  Prep PREFIX group ({prep_prefixes}):")
    print(f"    Mean pairwise cosine: {prep_mean:.3f}")

    # Shuffle test: permute PREFIX labels within folios
    print(f"\n  Shuffle test ({N_PERMUTATIONS} iterations)...")
    random.seed(42)
    folio_tokens = defaultdict(list)
    for t in tokens:
        if t['prefix'] in valid:
            folio_tokens[t['folio']].append(t)

    exceed_count = 0
    for iteration in range(N_PERMUTATIONS):
        # Shuffle prefix labels within each folio
        shuf_atoms = defaultdict(Counter)
        shuf_totals = defaultdict(int)
        for folio, ftoks in folio_tokens.items():
            prefixes = [t['prefix'] for t in ftoks]
            random.shuffle(prefixes)
            for i, t in enumerate(ftoks):
                shuf_pre = prefixes[i]
                for ch in t['middle']:
                    shuf_atoms[shuf_pre][ch] += 1
                    shuf_totals[shuf_pre] += 1

        # Compute prep group similarity under shuffle
        shuf_vecs = {}
        for pre in prep_prefixes:
            if shuf_totals[pre] > 0:
                shuf_vecs[pre] = get_atom_vector(shuf_atoms[pre], shuf_totals[pre], all_atoms)

        shuf_sims = []
        for i in range(len(prep_prefixes)):
            for j in range(i+1, len(prep_prefixes)):
                if prep_prefixes[i] in shuf_vecs and prep_prefixes[j] in shuf_vecs:
                    shuf_sims.append(cosine_sim(shuf_vecs[prep_prefixes[i]],
                                                shuf_vecs[prep_prefixes[j]]))
        shuf_mean = sum(shuf_sims) / len(shuf_sims) if shuf_sims else 0
        if shuf_mean >= prep_mean:
            exceed_count += 1

    p_val = exceed_count / N_PERMUTATIONS
    print(f"    Observed prep mean cosine: {prep_mean:.3f}")
    print(f"    Exceeded in {exceed_count}/{N_PERMUTATIONS} shuffles (p={p_val:.4f})")

    results = {
        'prefixes': valid,
        'per_prefix': {pre: prefix_data[pre]['axis_fracs'] for pre in valid},
        'per_prefix_n': {pre: prefix_data[pre]['n_tokens'] for pre in valid},
        'cosine_matrix': {valid[i]: {valid[j]: round(sim_matrix[i][j], 3) for j in range(n)} for i in range(n)},
        'prep_group': {
            'prefixes': prep_prefixes,
            'mean_cosine': round(prep_mean, 3),
            'shuffle_p': p_val,
            'n_shuffles': N_PERMUTATIONS,
        },
    }
    return results


# ============================================================
# T5: FOLIO-LEVEL PREFIX CORRELATION MATRIX
# ============================================================

def test_folio_correlation(tokens, prefix_counts):
    print(f"\n{'='*70}")
    print("T5: FOLIO-LEVEL PREFIX CORRELATION MATRIX")
    print("=" * 70)

    valid = sorted(p for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS)

    # Compute prefix fractions per folio
    folio_counts = defaultdict(Counter)  # folio -> {prefix: count}
    folio_totals = Counter()
    for t in tokens:
        folio_counts[t['folio']][t['prefix']] += 1
        folio_totals[t['folio']] += 1

    # Filter to folios with enough tokens
    folios = sorted(f for f in folio_totals if folio_totals[f] >= 20)
    print(f"  {len(folios)} folios with 20+ tokens")

    # Filter prefixes to those appearing in enough folios
    prefix_folio_count = defaultdict(int)
    for f in folios:
        for pre in valid:
            if folio_counts[f][pre] >= MIN_FOLIO_TOKENS:
                prefix_folio_count[pre] += 1

    valid_corr = sorted(p for p in valid if prefix_folio_count[p] >= MIN_FOLIOS_PREFIX)
    print(f"  {len(valid_corr)} prefixes qualify (>={MIN_FOLIOS_PREFIX} folios with >={MIN_FOLIO_TOKENS} tokens)")

    # Build fraction matrix
    n_pre = len(valid_corr)
    prefix_fracs = {pre: [] for pre in valid_corr}
    for f in folios:
        total = folio_totals[f]
        for pre in valid_corr:
            prefix_fracs[pre].append(folio_counts[f][pre] / total)

    # Pairwise correlations
    pairs = []
    p_values = []
    for i in range(n_pre):
        for j in range(i+1, n_pre):
            r, p = pearson_r(prefix_fracs[valid_corr[i]], prefix_fracs[valid_corr[j]])
            pairs.append((valid_corr[i], valid_corr[j], r, p))
            p_values.append(p)

    # FDR correction
    fdr_results = benjamini_hochberg(p_values)
    significant = []
    for k, (p1, p2, r, raw_p) in enumerate(pairs):
        _, _, adj_p, sig = fdr_results[k]
        if sig:
            significant.append((p1, p2, round(r, 3), round(adj_p, 4)))

    # Print significant correlations
    significant.sort(key=lambda x: -abs(x[2]))
    print(f"\n  {len(significant)} FDR-significant pairs (of {len(pairs)} tested):")
    print(f"  {'Pre1':>8}  {'Pre2':>8}  {'r':>6}  {'p_adj':>8}")
    for p1, p2, r, adj_p in significant[:20]:
        print(f"  {p1:>8}  {p2:>8}  {r:>+5.3f}  {adj_p:>8.4f}")
    if len(significant) > 20:
        print(f"  ... ({len(significant) - 20} more)")

    # Check if same-base prefixes correlate more
    base_pairs_r = []
    diff_pairs_r = []
    for p1, p2, r, adj_p in significant:
        if p1[-1] == p2[-1]:
            base_pairs_r.append(r)
        else:
            diff_pairs_r.append(r)

    if base_pairs_r:
        print(f"\n  Same-base significant pairs: mean r = {sum(base_pairs_r)/len(base_pairs_r):+.3f} ({len(base_pairs_r)} pairs)")
    if diff_pairs_r:
        print(f"  Diff-base significant pairs: mean r = {sum(diff_pairs_r)/len(diff_pairs_r):+.3f} ({len(diff_pairs_r)} pairs)")

    results = {
        'n_folios': len(folios),
        'n_prefixes_tested': n_pre,
        'prefixes': valid_corr,
        'n_pairs': len(pairs),
        'n_significant': len(significant),
        'significant_pairs': significant,
    }
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("PREFIX_ATOM_ROLES -- Phase 434")
    print("=" * 70)

    tokens = load_data()
    print(f"Loaded {len(tokens)} Currier B tokens with non-empty MIDDLEs")

    prefix_counts = Counter(t['prefix'] for t in tokens)
    valid = sorted(p for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS)
    print(f"Total unique prefixes: {len(prefix_counts)}")
    print(f"Prefixes with {MIN_PREFIX_TOKENS}+ tokens: {len(valid)}")

    results = {}
    results['metadata'] = {
        'n_tokens': len(tokens),
        'n_prefixes_total': len(prefix_counts),
        'n_prefixes_tested': len(valid),
        'valid_prefixes': valid,
    }

    results['T1_positional_grammar'] = test_positional_grammar(tokens, prefix_counts)
    results['T2_base_profiles'] = test_base_profiles(tokens, prefix_counts)
    results['T3_modifier_profiles'] = test_modifier_profiles(tokens, prefix_counts)
    results['T4_content_profiles'] = test_prefix_content_profiles(tokens, prefix_counts)
    results['T5_folio_correlation'] = test_folio_correlation(tokens, prefix_counts)

    output_path = RESULTS_DIR / "prefix_atom_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
