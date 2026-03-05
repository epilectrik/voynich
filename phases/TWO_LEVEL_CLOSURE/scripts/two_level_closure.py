"""
Phase 522: Two-Level Closure Architecture
==========================================

C1439 showed that m-terminal (MIDDLE-level) and -am suffix (suffix-level) are
orthogonal closure systems. This phase investigates whether this is a GENERAL
design principle: do MIDDLE TERMINAL atoms and suffix atoms systematically
partition closure/routing functions between the two layers?

Tests:
  T1.  Terminal-suffix orthogonality matrix (6 TERMINAL x 16 suffix atoms)
  T2.  Suffix suppression gradient by TERMINAL
  T3.  Same-atom orthogonality test (self-co-occurrence across layers)
  T4.  Functional partitioning test (category complementarity)
  T5.  Two-level closure generalization (line-final concentration)
  T6.  Mutual exclusivity patterns (O/E < 0.1 and O/E > 3)
  T7.  Information complementarity (I(cat; TERMINAL) vs I(cat; suffix))
  T8.  Layer specialization by line position
  T9.  Paragraph-level layer balance
  T10. Design principle test: exclusion vs independence

Output: phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json
"""

import sys
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, spearmanr, mannwhitneyu

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# ATOM AND SLOT DEFINITIONS (from C1393, C1394, C1408)
# ============================================================
HEAD_SET = {'a', 'o', 'e', 'k', 't'}
TERM_SET = {'l', 'r', 'h', 'y', 'm', 'n', 'k', 't'}
EXTENSIBLE = {'e', 'i'}

# The 6 core TERMINAL atoms (C1209: n 99.4% terminal, y, l, r, h, m)
CORE_TERMINALS = ['y', 'l', 'r', 'h', 'm', 'n']

# Suffix atoms (from C1408 scheme)
SUFFIX_ATOMS = set('aeoktpficdsylrhmn')


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def atomize_middle(middle):
    """Split MIDDLE into atoms, respecting e/i extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def get_terminal_atom(middle):
    """Get the terminal atom of a MIDDLE (last character, grouped for extensibility)."""
    atoms = atomize_middle(middle)
    if not atoms:
        return None
    last = atoms[-1]
    base = last[0]
    if base in TERM_SET:
        return base
    return None


def get_head_atom(middle):
    """Get the HEAD atom (first atom if it can be HEAD)."""
    atoms = atomize_middle(middle)
    if not atoms:
        return None
    first = atoms[0]
    base = first[0]
    if base in HEAD_SET:
        return base
    return None


def decompose_suffix(sfx):
    """Parse suffix into atoms."""
    if not sfx:
        return []
    atoms = []
    i = 0
    while i < len(sfx):
        if i + 1 < len(sfx) and sfx[i:i+2] in ('ii', 'ee', 'oo'):
            atoms.append(sfx[i:i+2])
            i += 2
        elif sfx[i] in SUFFIX_ATOMS:
            atoms.append(sfx[i])
            i += 1
        else:
            atoms.append(sfx[i])
            i += 1
    return atoms


def get_suffix_head(sfx):
    """Get the first atom of a suffix."""
    atoms = decompose_suffix(sfx)
    if not atoms:
        return None
    return atoms[0][0]  # Base character


def get_suffix_term(sfx):
    """Get the last atom of a suffix."""
    atoms = decompose_suffix(sfx)
    if not atoms:
        return None
    return atoms[-1][0]  # Base character


def safe_ratio(a, b):
    """Compute a/b handling zero."""
    if b == 0:
        return float('inf') if a > 0 else 0.0
    return a / b


def mutual_info(contingency):
    """Compute mutual information from contingency table (bits)."""
    arr = np.array(contingency, dtype=float)
    n = arr.sum()
    if n == 0:
        return 0.0
    p = arr / n
    row_sums = p.sum(axis=1)
    col_sums = p.sum(axis=0)
    mi = 0.0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if p[i, j] > 0 and row_sums[i] > 0 and col_sums[j] > 0:
                mi += p[i, j] * np.log2(p[i, j] / (row_sums[i] * col_sums[j]))
    return mi


def entropy(dist):
    """Shannon entropy in bits from a distribution dict."""
    total = sum(dist.values())
    if total == 0:
        return 0.0
    h = 0.0
    for v in dist.values():
        if v > 0:
            p = v / total
            h -= p * np.log2(p)
    return h


def cramers_v(contingency_table):
    """Compute Cramer's V from contingency table."""
    try:
        arr = np.array(contingency_table, dtype=float)
        chi2, p, dof, expected = chi2_contingency(arr)
        n = arr.sum()
        min_dim = min(arr.shape) - 1
        if min_dim == 0 or n == 0:
            return 0.0, chi2, p
        v = math.sqrt(chi2 / (n * min_dim))
        return v, chi2, p
    except Exception:
        return 0.0, 0.0, 1.0


# ============================================================
# DATA LOADING
# ============================================================

print("=" * 70)
print("Phase 522: Two-Level Closure Architecture")
print("=" * 70)

print("\nLoading data...")
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

# Collect all Currier B tokens with full annotations
all_tokens = []
folio_lines = defaultdict(list)

for tok in tx.currier_b():
    if '*' in tok.word or not tok.word.strip():
        continue
    m = morph.extract(tok.word)
    mid = m.middle
    terminal = get_terminal_atom(mid) if mid else None
    head = get_head_atom(mid) if mid else None
    cat = cc.classify(mid) if mid else None
    sfx = m.suffix
    sfx_head = get_suffix_head(sfx) if sfx else None
    sfx_term = get_suffix_term(sfx) if sfx else None
    sfx_atoms = decompose_suffix(sfx) if sfx else []

    # Compute line position quintile (will be populated later)
    entry = {
        'word': tok.word,
        'folio': tok.folio,
        'line': tok.line,
        'section': tok.section,
        'prefix': m.prefix,
        'middle': mid,
        'suffix': sfx,
        'articulator': m.articulator,
        'terminal': terminal,
        'head_atom': head,
        'category': cat,
        'sfx_head': sfx_head,
        'sfx_term': sfx_term,
        'sfx_atoms': sfx_atoms,
        'line_initial': tok.line_initial,
        'line_final': tok.line_final,
        'par_initial': tok.par_initial,
        'par_final': tok.par_final,
    }
    all_tokens.append(entry)
    folio_lines[(tok.folio, tok.line)].append(entry)

N = len(all_tokens)
print(f"Total B tokens (clean): {N}")

# Compute line positions for quintile analysis
for key, tokens in folio_lines.items():
    line_len = len(tokens)
    for i, tok in enumerate(tokens):
        tok['line_pos'] = i / max(line_len - 1, 1)  # 0 to 1
        tok['line_quintile'] = min(int(tok['line_pos'] * 5), 4)  # 0 to 4
        tok['line_len'] = line_len

# Pre-compute paragraph boundaries
par_final_lines = set()
par_initial_lines = set()
for key, tokens in folio_lines.items():
    if tokens[-1]['par_final']:
        par_final_lines.add(key)
    if tokens[0]['par_initial']:
        par_initial_lines.add(key)

# Pre-compute paragraph info
# Assign paragraph IDs
par_id_map = {}
current_par = 0
prev_folio = None
for tok in all_tokens:
    key = (tok['folio'], tok['line'])
    if tok['folio'] != prev_folio:
        current_par += 1
        prev_folio = tok['folio']
    elif tok['par_initial'] and tok['line_initial']:
        current_par += 1
    par_id_map[id(tok)] = current_par
    tok['par_id'] = current_par

# Identify header lines vs body lines
header_lines = set()
body_lines = set()
par_line_sets = defaultdict(list)
for key, tokens in folio_lines.items():
    pid = tokens[0]['par_id']
    par_line_sets[pid].append(key)

for pid, lines in par_line_sets.items():
    if lines:
        header_lines.add(lines[0])
        for line in lines[1:]:
            body_lines.add(line)

# Mark header vs body
for tok in all_tokens:
    key = (tok['folio'], tok['line'])
    tok['is_header'] = key in header_lines
    tok['is_body'] = key in body_lines

# Section → REGIME mapping (approximate from data)
# Load REGIME data if available
regime_path = PROJECT_ROOT / 'data' / 'folio_regimes.json'
folio_regime = {}
if regime_path.exists():
    with open(regime_path) as f:
        folio_regime = json.load(f)
for tok in all_tokens:
    tok['regime'] = folio_regime.get(tok['folio'], 'UNKNOWN')

# Overall suffix rate
overall_suffix_rate = sum(1 for t in all_tokens if t['suffix']) / N
print(f"Overall suffix rate: {overall_suffix_rate:.3f}")

results = {}

# ============================================================
# T1: Terminal-suffix orthogonality matrix
# ============================================================
print("\n=== T1: Terminal-suffix orthogonality matrix ===")

# For each TERMINAL atom, compute suffix rate and suffix-initial distribution
# Build 6 (TERMINAL) x N (suffix_head_atom) matrix of O/E ratios

# Get all suffix head atoms
sfx_head_counts = Counter()
for t in all_tokens:
    if t['sfx_head']:
        sfx_head_counts[t['sfx_head']] += 1

# Sort by frequency
sfx_head_atoms = sorted(sfx_head_counts.keys(), key=lambda x: -sfx_head_counts[x])
print(f"  Suffix head atoms found: {len(sfx_head_atoms)}: {sfx_head_atoms}")

# Build matrix: for each TERMINAL, what suffix head atoms appear?
matrix = {}
terminal_counts = Counter()
terminal_suffixed = Counter()

for t in all_tokens:
    term = t['terminal']
    if term and term in CORE_TERMINALS:
        terminal_counts[term] += 1
        if t['suffix']:
            terminal_suffixed[term] += 1

# Overall rates for expected computation
total_suffixed = sum(1 for t in all_tokens if t['suffix'])
# Rate of each suffix head atom among ALL suffixed tokens
sfx_head_rate = {a: sfx_head_counts[a] / total_suffixed for a in sfx_head_atoms}

for term_atom in CORE_TERMINALS:
    # Get all tokens with this terminal
    term_tokens = [t for t in all_tokens if t['terminal'] == term_atom]
    n_term = len(term_tokens)
    if n_term == 0:
        continue

    # Suffix rate for this terminal
    n_suffixed = sum(1 for t in term_tokens if t['suffix'])
    sfx_rate = n_suffixed / n_term

    # Distribution of suffix head atoms among suffixed tokens with this terminal
    sfx_dist = Counter()
    for t in term_tokens:
        if t['sfx_head']:
            sfx_dist[t['sfx_head']] += 1

    # Compute O/E ratios
    oe_ratios = {}
    for sa in sfx_head_atoms:
        observed = sfx_dist.get(sa, 0)
        # Expected: P(suffix_head=sa) * n_suffixed
        expected = sfx_head_rate.get(sa, 0) * n_suffixed
        oe = safe_ratio(observed, expected) if expected > 0 else (float('inf') if observed > 0 else 0.0)
        oe_ratios[sa] = {
            'observed': observed,
            'expected': round(expected, 1),
            'oe_ratio': round(oe, 3),
        }

    matrix[term_atom] = {
        'n_tokens': n_term,
        'n_suffixed': n_suffixed,
        'suffix_rate': round(sfx_rate, 4),
        'suffix_head_oe': oe_ratios,
    }

    # Print summary
    top_sfx = sorted(sfx_dist.items(), key=lambda x: -x[1])[:5]
    top_str = ', '.join(f"{a}:{c}" for a, c in top_sfx)
    print(f"  {term_atom}-terminal: n={n_term}, suffix_rate={sfx_rate:.3f}, top_sfx_heads: {top_str}")

results['T1_terminal_suffix_matrix'] = matrix

# ============================================================
# T2: Suffix suppression gradient by TERMINAL
# ============================================================
print("\n=== T2: Suffix suppression gradient ===")

suppression = {}
for term_atom in CORE_TERMINALS:
    if term_atom in matrix:
        sfx_rate = matrix[term_atom]['suffix_rate']
        norm_rate = sfx_rate / overall_suffix_rate if overall_suffix_rate > 0 else 0
        suppression[term_atom] = {
            'suffix_rate': round(sfx_rate, 4),
            'overall_rate': round(overall_suffix_rate, 4),
            'normalized_rate': round(norm_rate, 4),
            'suppression_ratio': round(1 / norm_rate, 2) if norm_rate > 0 else float('inf'),
            'n_tokens': matrix[term_atom]['n_tokens'],
        }

# Sort by suffix rate (most suppressing first)
ranked = sorted(suppression.items(), key=lambda x: x[1]['suffix_rate'])
print("  Ranked by suffix suppression (most suppressing first):")
for term, info in ranked:
    print(f"    {term}: rate={info['suffix_rate']:.3f}, norm={info['normalized_rate']:.3f}, "
          f"suppression={info['suppression_ratio']}x, n={info['n_tokens']}")

# Category determination strength (from C1412 — V values)
# Compute V(terminal; category) for each terminal
term_cat_data = {}
for term_atom in CORE_TERMINALS:
    term_tokens = [t for t in all_tokens if t['terminal'] == term_atom and t['category']]
    non_term_tokens = [t for t in all_tokens if t['terminal'] != term_atom and t['category']]
    if len(term_tokens) < 10:
        continue

    # Get category distributions
    cat_dist_term = Counter(t['category'] for t in term_tokens)
    cat_dist_other = Counter(t['category'] for t in non_term_tokens)

    # Top category
    top_cat = cat_dist_term.most_common(1)[0] if cat_dist_term else ('', 0)
    concentration = top_cat[1] / len(term_tokens) if len(term_tokens) > 0 else 0

    term_cat_data[term_atom] = {
        'top_category': top_cat[0],
        'concentration': round(concentration, 3),
        'n': len(term_tokens),
    }

# Correlation between suffix suppression and category concentration
if len(suppression) >= 4 and len(term_cat_data) >= 4:
    common = set(suppression.keys()) & set(term_cat_data.keys())
    supp_vals = [suppression[t]['normalized_rate'] for t in common]
    conc_vals = [term_cat_data[t]['concentration'] for t in common]
    if len(common) >= 4:
        rho, p_rho = spearmanr(supp_vals, conc_vals)
    else:
        rho, p_rho = 0.0, 1.0
else:
    rho, p_rho = 0.0, 1.0

suppression_result = {
    'ranked': {t: s for t, s in ranked},
    'category_concentration': term_cat_data,
    'suffix_rate_vs_concentration': {
        'spearman_rho': round(rho, 3),
        'p_value': round(p_rho, 4),
    }
}
results['T2_suppression_gradient'] = suppression_result

# ============================================================
# T3: Same-atom orthogonality test
# ============================================================
print("\n=== T3: Same-atom orthogonality ===")

# For each atom that appears in BOTH MIDDLE-terminal AND suffix:
# When atom X is the MIDDLE TERMINAL, how often does X appear in the suffix?
same_atom_results = {}

for atom in CORE_TERMINALS:
    # Tokens where this atom is the MIDDLE TERMINAL
    term_tokens = [t for t in all_tokens if t['terminal'] == atom]
    n_term = len(term_tokens)
    if n_term == 0:
        continue

    # Among those, how many have this atom in the suffix?
    has_atom_in_suffix = 0
    for t in term_tokens:
        sfx_chars = set()
        for sa in t['sfx_atoms']:
            sfx_chars.update(sa)  # Individual characters
        if atom in sfx_chars:
            has_atom_in_suffix += 1

    obs_rate = has_atom_in_suffix / n_term

    # Expected rate: P(atom in suffix) across ALL tokens
    all_with_atom_in_sfx = 0
    for t in all_tokens:
        sfx_chars = set()
        for sa in t['sfx_atoms']:
            sfx_chars.update(sa)
        if atom in sfx_chars:
            all_with_atom_in_sfx += 1
    exp_rate = all_with_atom_in_sfx / N

    oe = safe_ratio(obs_rate, exp_rate)

    # Fisher exact test: 2x2 contingency
    # [term_with_sfx_atom, term_without_sfx_atom]
    # [nonterm_with_sfx_atom, nonterm_without_sfx_atom]
    a = has_atom_in_suffix
    b = n_term - has_atom_in_suffix
    c = all_with_atom_in_sfx - has_atom_in_suffix
    d = (N - n_term) - c
    if c < 0:
        c = 0
        d = N - n_term
    try:
        odds, p_fisher = fisher_exact([[a, b], [c, d]])
    except:
        odds, p_fisher = 1.0, 1.0

    same_atom_results[atom] = {
        'n_term_tokens': n_term,
        'n_with_self_in_suffix': has_atom_in_suffix,
        'obs_rate': round(obs_rate, 4),
        'exp_rate': round(exp_rate, 4),
        'oe_ratio': round(oe, 3),
        'fisher_odds': round(odds, 3),
        'fisher_p': round(p_fisher, 6),
        'direction': 'SELF_REPEL' if oe < 0.5 else ('SELF_ATTRACT' if oe > 1.5 else 'NEUTRAL'),
    }
    print(f"  {atom}: obs={obs_rate:.4f}, exp={exp_rate:.4f}, O/E={oe:.3f}, "
          f"p={p_fisher:.6f} {'***' if p_fisher < 0.001 else '**' if p_fisher < 0.01 else '*' if p_fisher < 0.05 else 'ns'}")

results['T3_same_atom_orthogonality'] = same_atom_results

# ============================================================
# T4: Functional partitioning test
# ============================================================
print("\n=== T4: Functional partitioning ===")

# For each TERMINAL atom, compute category distribution
# For each suffix-head atom, compute category distribution
# Test: complementarity between them

categories = list(cc.CATEGORIES)
cat_idx = {c: i for i, c in enumerate(categories)}

# Terminal → category distributions
term_cat_dists = {}
for term_atom in CORE_TERMINALS:
    dist = Counter()
    for t in all_tokens:
        if t['terminal'] == term_atom and t['category']:
            dist[t['category']] += 1
    if sum(dist.values()) > 0:
        term_cat_dists[term_atom] = dist

# Suffix head → category distributions
sfx_cat_dists = {}
for sfx_a in sfx_head_atoms:
    dist = Counter()
    for t in all_tokens:
        if t['sfx_head'] == sfx_a and t['category']:
            dist[t['category']] += 1
    if sum(dist.values()) > 0:
        sfx_cat_dists[sfx_a] = dist

# Compute JSD between each TERMINAL's category profile and each suffix head's profile
func_partition = {}
for term_atom in CORE_TERMINALS:
    if term_atom not in term_cat_dists:
        continue
    td = term_cat_dists[term_atom]
    total_t = sum(td.values())
    t_vec = np.array([td.get(c, 0) / total_t for c in categories])

    for sfx_a in sfx_head_atoms:
        if sfx_a not in sfx_cat_dists:
            continue
        sd = sfx_cat_dists[sfx_a]
        total_s = sum(sd.values())
        s_vec = np.array([sd.get(c, 0) / total_s for c in categories])

        # JSD
        m_vec = 0.5 * (t_vec + s_vec)
        kl_t = sum(t_vec[i] * np.log2(t_vec[i] / m_vec[i]) for i in range(len(categories))
                    if t_vec[i] > 0 and m_vec[i] > 0)
        kl_s = sum(s_vec[i] * np.log2(s_vec[i] / m_vec[i]) for i in range(len(categories))
                    if s_vec[i] > 0 and m_vec[i] > 0)
        jsd_val = 0.5 * kl_t + 0.5 * kl_s

        pair_key = f"{term_atom}_term_vs_{sfx_a}_sfx"
        func_partition[pair_key] = {
            'jsd': round(jsd_val, 4),
            'term_top': td.most_common(1)[0][0],
            'sfx_top': sd.most_common(1)[0][0],
            'complementary': td.most_common(1)[0][0] != sd.most_common(1)[0][0],
        }

# Self-pairs (same atom in terminal vs suffix head)
self_pairs = {}
for atom in CORE_TERMINALS:
    if atom in term_cat_dists and atom in sfx_cat_dists:
        pair_key = f"{atom}_term_vs_{atom}_sfx"
        if pair_key in func_partition:
            self_pairs[atom] = func_partition[pair_key]

# Count complementary pairs
n_comp = sum(1 for v in func_partition.values() if v['complementary'])
n_total_pairs = len(func_partition)

print(f"  Total TERMINAL x suffix_head pairs tested: {n_total_pairs}")
print(f"  Complementary (different top category): {n_comp} ({100*n_comp/n_total_pairs:.1f}%)")
print(f"  Self-pairs:")
for atom, info in self_pairs.items():
    print(f"    {atom}: JSD={info['jsd']:.4f}, term_top={info['term_top']}, sfx_top={info['sfx_top']}, "
          f"complementary={info['complementary']}")

results['T4_functional_partitioning'] = {
    'n_pairs': n_total_pairs,
    'n_complementary': n_comp,
    'frac_complementary': round(n_comp / n_total_pairs, 3) if n_total_pairs > 0 else 0,
    'self_pairs': self_pairs,
    'terminal_category_profiles': {
        t: {c: d.get(c, 0) for c in categories}
        for t, d in term_cat_dists.items()
    },
    'suffix_head_category_profiles': {
        s: {c: d.get(c, 0) for c in categories}
        for s, d in sfx_cat_dists.items() if sum(d.values()) >= 20
    },
}

# ============================================================
# T5: Two-level closure generalization
# ============================================================
print("\n=== T5: Two-level closure generalization ===")

# Compare line-final concentration of TERMINAL atoms vs suffix atoms
# Which ones serve as closure signals?

# TERMINAL atoms: line-final rate
term_final_rates = {}
for term_atom in CORE_TERMINALS:
    term_tokens = [t for t in all_tokens if t['terminal'] == term_atom]
    if not term_tokens:
        continue
    n_final = sum(1 for t in term_tokens if t['line_final'])
    n_total = len(term_tokens)
    overall_final_rate = sum(1 for t in all_tokens if t['line_final']) / N
    norm = (n_final / n_total) / overall_final_rate if overall_final_rate > 0 else 0

    term_final_rates[term_atom] = {
        'n': n_total,
        'n_final': n_final,
        'final_rate': round(n_final / n_total, 4),
        'normalized': round(norm, 3),
    }

# Suffix atoms: line-final rate (by suffix-head atom)
sfx_final_rates = {}
for sfx_a in sfx_head_atoms:
    sfx_tokens = [t for t in all_tokens if t['sfx_head'] == sfx_a]
    if not sfx_tokens:
        continue
    n_final = sum(1 for t in sfx_tokens if t['line_final'])
    n_total = len(sfx_tokens)
    overall_final_rate_sfx = sum(1 for t in all_tokens if t['line_final']) / N
    norm = (n_final / n_total) / overall_final_rate_sfx if overall_final_rate_sfx > 0 else 0

    sfx_final_rates[sfx_a] = {
        'n': n_total,
        'n_final': n_final,
        'final_rate': round(n_final / n_total, 4),
        'normalized': round(norm, 3),
    }

# Also check: line-final tokens that are bare (no suffix) — pure TERMINAL closure
bare_final = [t for t in all_tokens if t['line_final'] and not t['suffix'] and t['terminal']]
suffixed_final = [t for t in all_tokens if t['line_final'] and t['suffix']]
all_final = [t for t in all_tokens if t['line_final']]

print("  TERMINAL atom line-final enrichment:")
for term, info in sorted(term_final_rates.items(), key=lambda x: -x[1]['normalized']):
    print(f"    {term}: final_rate={info['final_rate']:.4f}, enrichment={info['normalized']:.2f}x, n={info['n']}")

print("  Suffix-head atom line-final enrichment:")
for sfx_a, info in sorted(sfx_final_rates.items(), key=lambda x: -x[1]['normalized']):
    if info['n'] >= 20:
        print(f"    {sfx_a}: final_rate={info['final_rate']:.4f}, enrichment={info['normalized']:.2f}x, n={info['n']}")

print(f"\n  Line-final composition: bare={len(bare_final)}, suffixed={len(suffixed_final)}, "
      f"total_final={len(all_final)}")
print(f"  Bare fraction of finals: {len(bare_final)/len(all_final):.3f}")

# Terminal distribution among bare finals
bare_final_terms = Counter(t['terminal'] for t in bare_final)
print(f"  Bare-final terminal distribution: {dict(bare_final_terms.most_common())}")

results['T5_closure_generalization'] = {
    'terminal_final_enrichment': term_final_rates,
    'suffix_head_final_enrichment': {k: v for k, v in sfx_final_rates.items() if v['n'] >= 10},
    'line_final_composition': {
        'bare_final': len(bare_final),
        'suffixed_final': len(suffixed_final),
        'total_final': len(all_final),
        'bare_fraction': round(len(bare_final) / len(all_final), 3),
    },
    'bare_final_terminal_dist': dict(bare_final_terms),
}

# ============================================================
# T6: Mutual exclusivity patterns
# ============================================================
print("\n=== T6: Mutual exclusivity patterns ===")

# For all TERMINAL x suffix-head pairs, find O/E < 0.1 and O/E > 3
near_exclusive = []  # O/E < 0.1
strong_cooccur = []  # O/E > 3

for term_atom in CORE_TERMINALS:
    if term_atom not in matrix:
        continue
    for sa in sfx_head_atoms:
        info = matrix[term_atom]['suffix_head_oe'].get(sa, {})
        oe = info.get('oe_ratio', None)
        obs = info.get('observed', 0)
        exp = info.get('expected', 0)
        if oe is not None:
            entry = {
                'terminal': term_atom,
                'suffix_head': sa,
                'oe_ratio': oe,
                'observed': obs,
                'expected': exp,
            }
            if oe < 0.1 and exp >= 2:  # Only count if expected >= 2
                near_exclusive.append(entry)
            elif oe > 3 and obs >= 3:  # Only count if observed >= 3
                strong_cooccur.append(entry)

print(f"  Near-exclusive pairs (O/E < 0.1, expected >= 2): {len(near_exclusive)}")
for p in near_exclusive:
    print(f"    {p['terminal']}-TERM + {p['suffix_head']}-SFX: O/E={p['oe_ratio']:.3f}, "
          f"obs={p['observed']}, exp={p['expected']}")

print(f"\n  Strong co-occurrence pairs (O/E > 3, obs >= 3): {len(strong_cooccur)}")
for p in strong_cooccur:
    print(f"    {p['terminal']}-TERM + {p['suffix_head']}-SFX: O/E={p['oe_ratio']:.3f}, "
          f"obs={p['observed']}, exp={p['expected']}")

results['T6_mutual_exclusivity'] = {
    'near_exclusive': near_exclusive,
    'strong_cooccurrence': strong_cooccur,
    'n_near_exclusive': len(near_exclusive),
    'n_strong_cooccurrence': len(strong_cooccur),
}

# ============================================================
# T7: Information complementarity
# ============================================================
print("\n=== T7: Information complementarity ===")

# Build contingency tables: category x TERMINAL, category x suffix_head
# Then compute joint: category x (TERMINAL, suffix_head)

# Filter to tokens with both terminal and category
cat_tokens = [t for t in all_tokens if t['terminal'] and t['category']]
n_cat = len(cat_tokens)

# I(category; TERMINAL)
term_cat_table = defaultdict(lambda: defaultdict(int))
for t in cat_tokens:
    term_cat_table[t['terminal']][t['category']] += 1

# Build numpy array
terms_list = sorted(term_cat_table.keys())
cats_list = sorted(categories)
arr_tc = np.zeros((len(terms_list), len(cats_list)))
for i, term in enumerate(terms_list):
    for j, cat in enumerate(cats_list):
        arr_tc[i, j] = term_cat_table[term].get(cat, 0)
mi_term_cat = mutual_info(arr_tc)

# I(category; suffix_head) — only among suffixed tokens
sfx_cat_tokens = [t for t in all_tokens if t['sfx_head'] and t['category']]
n_sfx_cat = len(sfx_cat_tokens)

sfx_cat_table = defaultdict(lambda: defaultdict(int))
for t in sfx_cat_tokens:
    sfx_cat_table[t['sfx_head']][t['category']] += 1

sfx_heads_list = sorted(sfx_cat_table.keys())
arr_sc = np.zeros((len(sfx_heads_list), len(cats_list)))
for i, sfx in enumerate(sfx_heads_list):
    for j, cat in enumerate(cats_list):
        arr_sc[i, j] = sfx_cat_table[sfx].get(cat, 0)
mi_sfx_cat = mutual_info(arr_sc)

# Joint I(category; TERMINAL, suffix_head) — only among tokens with both
joint_tokens = [t for t in all_tokens if t['terminal'] and t['sfx_head'] and t['category']]
n_joint = len(joint_tokens)

joint_cat_table = defaultdict(lambda: defaultdict(int))
for t in joint_tokens:
    joint_key = f"{t['terminal']}_{t['sfx_head']}"
    joint_cat_table[joint_key][t['category']] += 1

joint_keys_list = sorted(joint_cat_table.keys())
arr_jc = np.zeros((len(joint_keys_list), len(cats_list)))
for i, jk in enumerate(joint_keys_list):
    for j, cat in enumerate(cats_list):
        arr_jc[i, j] = joint_cat_table[jk].get(cat, 0)
mi_joint_cat = mutual_info(arr_jc)

# Also compute I(category; TERMINAL) AMONG suffixed tokens only (for fair comparison)
term_cat_suffixed = defaultdict(lambda: defaultdict(int))
for t in joint_tokens:
    term_cat_suffixed[t['terminal']][t['category']] += 1
terms_sfx_list = sorted(term_cat_suffixed.keys())
arr_tcs = np.zeros((len(terms_sfx_list), len(cats_list)))
for i, term in enumerate(terms_sfx_list):
    for j, cat in enumerate(cats_list):
        arr_tcs[i, j] = term_cat_suffixed[term].get(cat, 0)
mi_term_cat_suffixed = mutual_info(arr_tcs)

# Redundancy and synergy
# If additive: mi_joint ≈ mi_term + mi_sfx (among suffixed)
# If redundant: mi_joint < mi_term + mi_sfx
sum_individual = mi_term_cat_suffixed + mi_sfx_cat
redundancy = sum_individual - mi_joint_cat

# H(category) for normalization
cat_dist_all = Counter(t['category'] for t in all_tokens if t['category'])
h_cat = entropy(cat_dist_all)

print(f"  I(category; TERMINAL) = {mi_term_cat:.4f} bits (all tokens, n={n_cat})")
print(f"  I(category; suffix_head) = {mi_sfx_cat:.4f} bits (suffixed tokens, n={n_sfx_cat})")
print(f"  I(category; TERMINAL) [suffixed only] = {mi_term_cat_suffixed:.4f} bits (n={n_joint})")
print(f"  I(category; TERMINAL+suffix_head) = {mi_joint_cat:.4f} bits (joint, n={n_joint})")
print(f"  H(category) = {h_cat:.4f} bits")
print(f"  Sum individual = {sum_individual:.4f}")
print(f"  Redundancy (sum - joint) = {redundancy:.4f} bits")
print(f"  Redundancy fraction = {redundancy/sum_individual:.3f}" if sum_individual > 0 else "  N/A")

results['T7_information_complementarity'] = {
    'mi_terminal_category': round(mi_term_cat, 4),
    'mi_suffix_head_category': round(mi_sfx_cat, 4),
    'mi_terminal_category_suffixed': round(mi_term_cat_suffixed, 4),
    'mi_joint_category': round(mi_joint_cat, 4),
    'h_category': round(h_cat, 4),
    'sum_individual': round(sum_individual, 4),
    'redundancy': round(redundancy, 4),
    'redundancy_fraction': round(redundancy / sum_individual, 3) if sum_individual > 0 else 0,
    'n_all': n_cat,
    'n_suffixed': n_sfx_cat,
    'n_joint': n_joint,
    'complementarity_verdict': 'COMPLEMENTARY' if redundancy < 0.1 * sum_individual else (
        'PARTIALLY_REDUNDANT' if redundancy < 0.5 * sum_individual else 'REDUNDANT'),
}

# ============================================================
# T8: Layer specialization by line position
# ============================================================
print("\n=== T8: Layer specialization by line position ===")

# At each quintile, compute I(category; TERMINAL) and I(category; suffix_head)
quintile_results = {}
for q in range(5):
    q_tokens = [t for t in all_tokens if t.get('line_quintile') == q]
    if not q_tokens:
        continue

    # I(cat; terminal) at this quintile
    q_term_cat = defaultdict(lambda: defaultdict(int))
    for t in q_tokens:
        if t['terminal'] and t['category']:
            q_term_cat[t['terminal']][t['category']] += 1
    q_terms = sorted(q_term_cat.keys())
    if len(q_terms) > 1:
        arr = np.zeros((len(q_terms), len(cats_list)))
        for i, term in enumerate(q_terms):
            for j, cat in enumerate(cats_list):
                arr[i, j] = q_term_cat[term].get(cat, 0)
        mi_t = mutual_info(arr)
    else:
        mi_t = 0.0

    # I(cat; suffix_head) at this quintile
    q_sfx_cat = defaultdict(lambda: defaultdict(int))
    for t in q_tokens:
        if t['sfx_head'] and t['category']:
            q_sfx_cat[t['sfx_head']][t['category']] += 1
    q_sfxs = sorted(q_sfx_cat.keys())
    if len(q_sfxs) > 1:
        arr = np.zeros((len(q_sfxs), len(cats_list)))
        for i, sfx in enumerate(q_sfxs):
            for j, cat in enumerate(cats_list):
                arr[i, j] = q_sfx_cat[sfx].get(cat, 0)
        mi_s = mutual_info(arr)
    else:
        mi_s = 0.0

    # Suffix rate at this quintile
    sfx_rate_q = sum(1 for t in q_tokens if t['suffix']) / len(q_tokens) if q_tokens else 0

    quintile_results[f"Q{q}"] = {
        'n_tokens': len(q_tokens),
        'mi_terminal_category': round(mi_t, 4),
        'mi_suffix_category': round(mi_s, 4),
        'layer_ratio': round(mi_t / mi_s, 3) if mi_s > 0 else float('inf'),
        'suffix_rate': round(sfx_rate_q, 4),
    }
    print(f"  Q{q}: MI(term,cat)={mi_t:.4f}, MI(sfx,cat)={mi_s:.4f}, "
          f"ratio={mi_t/mi_s:.2f}x, sfx_rate={sfx_rate_q:.3f}, n={len(q_tokens)}")

results['T8_position_specialization'] = quintile_results

# ============================================================
# T9: Paragraph-level layer balance
# ============================================================
print("\n=== T9: Paragraph-level layer balance ===")

# For each paragraph, compute:
# - Fraction using TERMINAL-level closure (m or n terminal)
# - Fraction using suffix-level closure (has suffix)
# - Fraction using both
# - Fraction using neither

# Group tokens by paragraph
par_tokens = defaultdict(list)
for t in all_tokens:
    par_tokens[t['par_id']].append(t)

par_balance = []
for pid, tokens in par_tokens.items():
    if len(tokens) < 5:
        continue

    n = len(tokens)
    # TERMINAL closure signals: m-terminal primarily (strongest closure)
    n_m_term = sum(1 for t in tokens if t['terminal'] == 'm')
    # Also count n-terminal (halt signal)
    n_n_term = sum(1 for t in tokens if t['terminal'] == 'n')
    # Suffix closure signals: any suffix present
    n_suffixed = sum(1 for t in tokens if t['suffix'])
    # Both: m-terminal AND suffixed (should be rare per C1438)
    n_both = sum(1 for t in tokens if t['terminal'] == 'm' and t['suffix'])
    # Neither: not m/n terminal AND no suffix
    n_neither = sum(1 for t in tokens if t['terminal'] not in ('m', 'n') and not t['suffix'])

    section = tokens[0]['section']
    regime = tokens[0]['regime']

    par_balance.append({
        'par_id': pid,
        'n_tokens': n,
        'm_term_frac': n_m_term / n,
        'n_term_frac': n_n_term / n,
        'suffix_frac': n_suffixed / n,
        'both_frac': n_both / n,
        'neither_frac': n_neither / n,
        'section': section,
        'regime': regime,
    })

# Summary statistics
m_fracs = [p['m_term_frac'] for p in par_balance]
sfx_fracs = [p['suffix_frac'] for p in par_balance]
both_fracs = [p['both_frac'] for p in par_balance]
neither_fracs = [p['neither_frac'] for p in par_balance]

print(f"  Paragraphs analyzed: {len(par_balance)}")
print(f"  m-terminal fraction: mean={np.mean(m_fracs):.4f}, std={np.std(m_fracs):.4f}")
print(f"  suffix fraction:     mean={np.mean(sfx_fracs):.4f}, std={np.std(sfx_fracs):.4f}")
print(f"  both fraction:       mean={np.mean(both_fracs):.4f}, std={np.std(both_fracs):.4f}")
print(f"  neither fraction:    mean={np.mean(neither_fracs):.4f}, std={np.std(neither_fracs):.4f}")

# By section
section_balance = defaultdict(lambda: {'m': [], 'sfx': [], 'both': [], 'neither': []})
for p in par_balance:
    section_balance[p['section']]['m'].append(p['m_term_frac'])
    section_balance[p['section']]['sfx'].append(p['suffix_frac'])
    section_balance[p['section']]['both'].append(p['both_frac'])
    section_balance[p['section']]['neither'].append(p['neither_frac'])

section_summary = {}
for sec, data in section_balance.items():
    section_summary[sec] = {
        'n': len(data['m']),
        'm_term_mean': round(np.mean(data['m']), 4),
        'suffix_mean': round(np.mean(data['sfx']), 4),
        'both_mean': round(np.mean(data['both']), 4),
        'neither_mean': round(np.mean(data['neither']), 4),
    }
    print(f"  Section {sec}: m_term={np.mean(data['m']):.4f}, suffix={np.mean(data['sfx']):.4f}, "
          f"both={np.mean(data['both']):.4f}, neither={np.mean(data['neither']):.4f}, n={len(data['m'])}")

# Correlation between m-terminal and suffix fractions
rho_ms, p_ms = spearmanr(m_fracs, sfx_fracs)
print(f"\n  Correlation m_frac vs suffix_frac: rho={rho_ms:.3f}, p={p_ms:.6f}")

results['T9_paragraph_balance'] = {
    'n_paragraphs': len(par_balance),
    'means': {
        'm_term_frac': round(np.mean(m_fracs), 4),
        'suffix_frac': round(np.mean(sfx_fracs), 4),
        'both_frac': round(np.mean(both_fracs), 4),
        'neither_frac': round(np.mean(neither_fracs), 4),
    },
    'section_balance': section_summary,
    'm_suffix_correlation': {
        'spearman_rho': round(rho_ms, 3),
        'p_value': round(p_ms, 6),
    },
}

# ============================================================
# T10: Design principle test: exclusion vs independence
# ============================================================
print("\n=== T10: Exclusion vs Independence ===")

# Focus on m-terminal and -am suffix as the primary test case
# Condition on tokens where BOTH could plausibly appear:
# - Body lines (m-terminal scope per C1435)
# - Line-final position (where m concentrates)
# - Not par-final (to avoid -am's par-final bias confound)

# Also test: do m-terminal tokens appear in the -am suffix population?

# Population where m-terminal could appear: body-line-final, not par-final
body_final_nonpar = [t for t in all_tokens
                     if t['is_body'] and t['line_final'] and not t['par_final']]
n_bf = len(body_final_nonpar)
print(f"  Body-line-final, non-par-final tokens: {n_bf}")

# Among these: m-terminal rate
m_in_bf = sum(1 for t in body_final_nonpar if t['terminal'] == 'm')
am_in_bf = sum(1 for t in body_final_nonpar if t['suffix'] and 'am' in t['suffix'])
both_in_bf = sum(1 for t in body_final_nonpar if t['terminal'] == 'm' and t['suffix'] and 'am' in t['suffix'])

print(f"  m-terminal: {m_in_bf} ({100*m_in_bf/n_bf:.1f}%)")
print(f"  -am suffix: {am_in_bf} ({100*am_in_bf/n_bf:.1f}%)")
print(f"  Both:       {both_in_bf} ({100*both_in_bf/n_bf:.1f}%)")

# Expected co-occurrence if independent
exp_both_bf = (m_in_bf / n_bf) * (am_in_bf / n_bf) * n_bf if n_bf > 0 else 0
oe_bf = safe_ratio(both_in_bf, exp_both_bf)
print(f"  Expected both (if independent): {exp_both_bf:.2f}")
print(f"  O/E: {oe_bf:.3f}")

# Fisher exact test
try:
    # [[both, m_only], [am_only, neither]]
    m_only_bf = m_in_bf - both_in_bf
    am_only_bf = am_in_bf - both_in_bf
    neither_bf = n_bf - m_in_bf - am_only_bf
    odds_bf, p_bf = fisher_exact([[both_in_bf, m_only_bf], [am_only_bf, neither_bf]])
except:
    odds_bf, p_bf = 1.0, 1.0

print(f"  Fisher exact: odds={odds_bf:.3f}, p={p_bf:.6f}")

# Now test ALL TERMINAL-suffix pairs for exclusion vs independence in this population
# Which pairs show active exclusion (O/E << 1 in the matched population)?
exclusion_tests = {}
for term_atom in CORE_TERMINALS:
    # All body-final non-par-final tokens with this terminal
    t_in_bf = sum(1 for t in body_final_nonpar if t['terminal'] == term_atom)
    if t_in_bf < 5:
        continue

    # All such tokens that are also suffixed
    t_suffixed = sum(1 for t in body_final_nonpar if t['terminal'] == term_atom and t['suffix'])
    sfx_rate_bf = t_suffixed / t_in_bf

    # Overall suffix rate in body-final non-par-final
    overall_sfx_bf = sum(1 for t in body_final_nonpar if t['suffix']) / n_bf

    exclusion_tests[term_atom] = {
        'n_in_population': t_in_bf,
        'n_suffixed': t_suffixed,
        'suffix_rate': round(sfx_rate_bf, 4),
        'population_suffix_rate': round(overall_sfx_bf, 4),
        'oe_ratio': round(sfx_rate_bf / overall_sfx_bf, 3) if overall_sfx_bf > 0 else 0,
    }
    verdict = 'ACTIVE_EXCLUSION' if sfx_rate_bf / overall_sfx_bf < 0.2 else (
        'WEAK_SUPPRESSION' if sfx_rate_bf / overall_sfx_bf < 0.5 else 'NEUTRAL')
    exclusion_tests[term_atom]['verdict'] = verdict
    print(f"  {term_atom}-terminal suffix rate in pop: {sfx_rate_bf:.3f} vs {overall_sfx_bf:.3f}, "
          f"O/E={sfx_rate_bf/overall_sfx_bf:.3f}, verdict={verdict}")

results['T10_exclusion_vs_independence'] = {
    'm_am_test': {
        'population': 'body_line_final_non_par_final',
        'n_population': n_bf,
        'n_m_terminal': m_in_bf,
        'n_am_suffix': am_in_bf,
        'n_both': both_in_bf,
        'expected_both': round(exp_both_bf, 2),
        'oe_ratio': round(oe_bf, 3),
        'fisher_odds': round(odds_bf, 3),
        'fisher_p': round(p_bf, 6),
        'verdict': 'ACTIVE_EXCLUSION' if oe_bf < 0.2 else 'INDEPENDENT',
    },
    'terminal_exclusion_tests': exclusion_tests,
}

# ============================================================
# SUPPLEMENTARY: Full cross-tabulation summary
# ============================================================
print("\n=== SUPPLEMENTARY: Cross-tabulation summary ===")

# Build the definitive TERMINAL x has_suffix contingency
term_sfx_ct = defaultdict(lambda: {'bare': 0, 'suffixed': 0})
for t in all_tokens:
    if t['terminal'] and t['terminal'] in CORE_TERMINALS:
        if t['suffix']:
            term_sfx_ct[t['terminal']]['suffixed'] += 1
        else:
            term_sfx_ct[t['terminal']]['bare'] += 1

# Compute chi-square for TERMINAL x suffix presence
terms_for_chi = sorted(term_sfx_ct.keys())
chi_arr = np.array([[term_sfx_ct[t]['bare'], term_sfx_ct[t]['suffixed']] for t in terms_for_chi])
v_ts, chi2_ts, p_ts = cramers_v(chi_arr)
print(f"  TERMINAL x suffix_presence: V={v_ts:.3f}, chi2={chi2_ts:.1f}, p={p_ts:.2e}")

# Terminal transparency ranking (from C1412 framework)
transparency_ranking = {}
for t in terms_for_chi:
    total = term_sfx_ct[t]['bare'] + term_sfx_ct[t]['suffixed']
    sfx_r = term_sfx_ct[t]['suffixed'] / total if total > 0 else 0
    transparency_ranking[t] = {
        'suffix_rate': round(sfx_r, 4),
        'bare_rate': round(1 - sfx_r, 4),
        'n': total,
        'label': 'OPAQUE' if sfx_r < 0.2 else ('SEMI_TRANSPARENT' if sfx_r < 0.4 else 'TRANSPARENT'),
    }

print("\n  Terminal transparency ranking:")
for t, info in sorted(transparency_ranking.items(), key=lambda x: x[1]['suffix_rate']):
    print(f"    {t}: suffix_rate={info['suffix_rate']:.3f} ({info['label']}), n={info['n']}")

results['supplementary'] = {
    'terminal_x_suffix_contingency': {
        'V': round(v_ts, 3),
        'chi2': round(chi2_ts, 1),
        'p': p_ts,
    },
    'transparency_ranking': transparency_ranking,
}

# ============================================================
# SAVE RESULTS
# ============================================================
out_path = RESULTS_DIR / 'two_level_closure.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n{'='*70}")
print(f"Results saved to {out_path}")
print(f"{'='*70}")
