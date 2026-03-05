"""
Phase 521: The m-Terminal Anomaly
==================================

C1427 found that the MIDDLE TERMINAL atom m is 196x enriched at line-final
position — the largest positional effect ever observed. This phase investigates:

  T1.  m-terminal inventory (types, HEAD atoms, vocabulary diversity)
  T2.  m-terminal positional profile (gradient shape)
  T3.  m-terminal vs paragraph-final vs line-final
  T4.  m-terminal and PREFIX
  T5.  m-terminal and suffix
  T6.  m-terminal and operational category
  T7.  m-terminal and macro-state transitions
  T8.  m-terminal and hazard topology
  T9.  m-terminal vs other rare terminals
  T10. m-terminal as closure signal — functional test

Output: phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json
"""

import sys
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu, spearmanr, fisher_exact

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
# ATOM AND SLOT DEFINITIONS (from C1393, C1394)
# ============================================================
HEAD_SET = {'a', 'o', 'e', 'k', 't'}
TERM_SET = {'l', 'r', 'h', 'y', 'm', 'n', 'k', 't'}
EXTENSIBLE = {'e', 'i'}

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
        return base  # Return the base char for grouping
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


def decompose_middle(middle):
    """Full decomposition into head, mods, term."""
    atoms = atomize_middle(middle)
    if not atoms:
        return None, [], None
    if len(atoms) == 1:
        atom = atoms[0]
        base = atom[0]
        # Single atom: could be HEAD or TERM or both
        if base in HEAD_SET and base in TERM_SET:
            return atom, [], None  # Ambiguous, treat as HEAD
        elif base in HEAD_SET:
            return atom, [], None
        elif base in TERM_SET:
            return None, [], atom
        return atom, [], None

    head = None
    head_base = atoms[0][0]
    if head_base in HEAD_SET:
        head = atoms[0]
        remainder = atoms[1:]
    else:
        head = None
        remainder = atoms

    if not remainder:
        return head, [], None

    term = None
    term_base = remainder[-1][0]
    if term_base in TERM_SET:
        term = remainder[-1]
        mods = remainder[:-1]
    else:
        term = None
        mods = remainder

    return head, mods, term


def cramers_v(contingency_table):
    """Compute Cramer's V from contingency table."""
    try:
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        n = contingency_table.sum()
        min_dim = min(contingency_table.shape) - 1
        if min_dim == 0 or n == 0:
            return 0.0, p
        v = math.sqrt(chi2 / (n * min_dim))
        return v, p
    except Exception:
        return 0.0, 1.0


def safe_ratio(a, b):
    """Compute ratio a/b, handling zero."""
    if b == 0:
        return float('inf') if a > 0 else 0.0
    return a / b


# ============================================================
# DATA LOADING
# ============================================================

print("Loading data...")
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

# Collect all Currier B tokens with full annotations
all_tokens = []
folio_lines = defaultdict(list)  # (folio, line) -> list of tokens in order

for tok in tx.currier_b():
    if '*' in tok.word or not tok.word.strip():
        continue
    m = morph.extract(tok.word)
    mid = m.middle
    terminal = get_terminal_atom(mid) if mid else None
    head = get_head_atom(mid) if mid else None
    cat = cc.classify(mid) if mid else None
    _, mods, _ = decompose_middle(mid) if mid else (None, [], None)
    mod_str = ''.join([a for a in mods]) if mods else ''

    entry = {
        'word': tok.word,
        'folio': tok.folio,
        'line': tok.line,
        'section': tok.section,
        'prefix': m.prefix,
        'middle': mid,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'terminal': terminal,
        'head_atom': head,
        'mod_stack': mod_str,
        'category': cat,
        'line_initial': tok.line_initial,
        'line_final': tok.line_final,
        'par_initial': tok.par_initial,
        'par_final': tok.par_final,
    }
    all_tokens.append(entry)
    folio_lines[(tok.folio, tok.line)].append(entry)

N = len(all_tokens)
print(f"Total B tokens (clean): {N}")

# Pre-compute per-line data
lines_data = {}
for key, tokens in folio_lines.items():
    lines_data[key] = {
        'length': len(tokens),
        'tokens': tokens,
        'folio': tokens[0]['folio'],
        'section': tokens[0]['section'],
    }

# Identify paragraph-final lines (par_final on last token)
par_final_lines = set()
for key, tokens in folio_lines.items():
    if tokens[-1]['par_final']:
        par_final_lines.add(key)

# Identify folio-final lines (last line in each folio)
folio_last_lines = {}
for key in folio_lines:
    folio, line = key
    line_num = int(line) if line.isdigit() else 0
    if folio not in folio_last_lines or line_num > folio_last_lines[folio][1]:
        folio_last_lines[folio] = (key, line_num)
folio_final_line_set = {v[0] for v in folio_last_lines.values()}

results = {}

# ============================================================
# T1: m-terminal inventory
# ============================================================
print("\n=== T1: m-terminal inventory ===")

# All m-terminal MIDDLEs
m_term_tokens = [t for t in all_tokens if t['terminal'] == 'm']
m_term_middles = Counter([t['middle'] for t in m_term_tokens])
n_m = len(m_term_tokens)

# HEAD atoms preceding m in m-terminal MIDDLEs
m_heads = Counter([t['head_atom'] for t in m_term_tokens])
m_mods = Counter([t['mod_stack'] for t in m_term_tokens if t['mod_stack']])

# Compare vocabulary diversity across terminals
all_terminals = Counter([t['terminal'] for t in all_tokens if t['terminal']])
term_diversity = {}
for term_char in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    term_tokens = [t for t in all_tokens if t['terminal'] == term_char]
    term_mids = Counter([t['middle'] for t in term_tokens])
    term_diversity[term_char] = {
        'count': len(term_tokens),
        'unique_middles': len(term_mids),
        'top_5': term_mids.most_common(5),
        'frac_of_all': len(term_tokens) / N,
    }

t1 = {
    'n_m_terminal': n_m,
    'frac_of_all': n_m / N,
    'unique_m_middles': len(m_term_middles),
    'm_middle_inventory': dict(m_term_middles.most_common()),
    'head_atoms': dict(m_heads.most_common()),
    'mod_stacks': dict(m_mods.most_common()),
    'terminal_diversity': {k: {'count': v['count'], 'unique': v['unique_middles'],
                               'frac': round(v['frac_of_all'], 5),
                               'top5': [(m, c) for m, c in v['top_5']]}
                          for k, v in term_diversity.items()},
}
results['T1_inventory'] = t1

print(f"m-terminal tokens: {n_m} ({n_m/N:.3%} of all)")
print(f"Unique m-terminal MIDDLEs: {len(m_term_middles)}")
print(f"Types: {dict(m_term_middles.most_common())}")
print(f"HEAD atoms: {dict(m_heads.most_common())}")
print(f"\nTerminal diversity comparison:")
for t_char in ['y', 'l', 'r', 'h', 'm', 'n']:
    d = term_diversity[t_char]
    print(f"  {t_char}: {d['count']} tokens, {d['unique_middles']} types, {d['frac_of_all']:.4%}")

# ============================================================
# T2: m-terminal positional profile
# ============================================================
print("\n=== T2: m-terminal positional profile ===")

# Compute rate at each position index within line
# Group tokens by their position index
max_pos = 20  # We'll report up to position 20
pos_m_counts = Counter()
pos_total_counts = Counter()

for key, tokens in folio_lines.items():
    ll = len(tokens)
    for i, tok in enumerate(tokens):
        # Compute quintile (0-4) and absolute position
        abs_pos = i + 1  # 1-based
        is_final = (i == ll - 1)

        if abs_pos <= max_pos:
            pos_total_counts[abs_pos] += 1
            if tok['terminal'] == 'm':
                pos_m_counts[abs_pos] += 1

        # Quintile (Q0-Q4)
        if ll >= 5:
            q = min(int(i * 5 / ll), 4)
        else:
            q = min(i, 4)
        pos_total_counts[f'Q{q}'] += 1
        if tok['terminal'] == 'm':
            pos_m_counts[f'Q{q}'] += 1

        # Final token marker
        if is_final:
            pos_total_counts['FINAL'] += 1
            if tok['terminal'] == 'm':
                pos_m_counts['FINAL'] += 1

# Compute rates by position
pos_rates = {}
for k in sorted(pos_total_counts.keys(), key=lambda x: (isinstance(x, str), str(x))):
    if pos_total_counts[k] >= 50:  # minimum sample
        rate = pos_m_counts[k] / pos_total_counts[k]
        pos_rates[str(k)] = {
            'rate': round(rate, 5),
            'count': pos_m_counts[k],
            'total': pos_total_counts[k],
        }

# Also compute per-terminal positional profiles for comparison
terminal_pos_rates = {}
for term_char in ['y', 'l', 'r', 'h', 'm', 'n']:
    this_rates = {}
    for key, tokens in folio_lines.items():
        ll = len(tokens)
        for i, tok in enumerate(tokens):
            is_final = (i == ll - 1)
            if is_final:
                k = 'FINAL'
            elif i == 0:
                k = 'POS1'
            else:
                if ll >= 5:
                    q = min(int(i * 5 / ll), 4)
                else:
                    q = min(i, 4)
                k = f'Q{q}'
            if k not in this_rates:
                this_rates[k] = [0, 0]
            this_rates[k][1] += 1
            if tok['terminal'] == term_char:
                this_rates[k][0] += 1

    terminal_pos_rates[term_char] = {}
    for k in ['POS1', 'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'FINAL']:
        if k in this_rates and this_rates[k][1] >= 50:
            terminal_pos_rates[term_char][k] = round(this_rates[k][0] / this_rates[k][1], 5)

# Positional concentration index: final_rate / overall_rate
concentration_indices = {}
for term_char in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    overall_rate = term_diversity[term_char]['frac_of_all']
    if 'FINAL' in terminal_pos_rates.get(term_char, {}):
        final_rate = terminal_pos_rates[term_char]['FINAL']
        ci = safe_ratio(final_rate, overall_rate) if overall_rate > 0 else 0
        concentration_indices[term_char] = round(ci, 2)

t2 = {
    'positional_rates_m': pos_rates,
    'terminal_positional_profiles': terminal_pos_rates,
    'concentration_indices': concentration_indices,
}
results['T2_positional'] = t2

print("m-terminal rate by position:")
for k, v in sorted(pos_rates.items(), key=lambda x: x[1]['rate']):
    print(f"  {k}: {v['rate']:.5f} ({v['count']}/{v['total']})")
print("\nConcentration indices (final_rate / overall_rate):")
for tc, ci in sorted(concentration_indices.items(), key=lambda x: -x[1]):
    print(f"  {tc}: {ci:.1f}x")

# ============================================================
# T3: m-terminal vs paragraph-final vs line-final
# ============================================================
print("\n=== T3: paragraph-final vs line-final vs folio-final ===")

# Categorize all line-final tokens
line_final_tokens = [t for t in all_tokens if t['line_final']]
par_final_tokens = [t for t in all_tokens if t['par_final']]
# Body-line final = line-final but NOT paragraph-final
body_line_final = [t for t in line_final_tokens if not t['par_final']]
# Header-line final = first line of paragraph, line-final (always true)
# Need to find first-line-of-paragraph line-final tokens
header_line_final = [t for t in line_final_tokens if t['par_initial']]
non_header_line_final = [t for t in line_final_tokens if not t['par_initial']]

m_in_line_final = sum(1 for t in line_final_tokens if t['terminal'] == 'm')
m_in_par_final = sum(1 for t in par_final_tokens if t['terminal'] == 'm')
m_in_body_final = sum(1 for t in body_line_final if t['terminal'] == 'm')
m_in_header_final = sum(1 for t in header_line_final if t['terminal'] == 'm')
m_in_non_header_final = sum(1 for t in non_header_line_final if t['terminal'] == 'm')

# Folio-final
folio_final_tokens = [t for t in all_tokens if t['line_final'] and
                      (t['folio'], t['line']) in folio_final_line_set]
m_in_folio_final = sum(1 for t in folio_final_tokens if t['terminal'] == 'm')

# Non-final m rate
non_final_tokens = [t for t in all_tokens if not t['line_final']]
m_in_non_final = sum(1 for t in non_final_tokens if t['terminal'] == 'm')

t3 = {
    'line_final': {
        'n': len(line_final_tokens),
        'm_count': m_in_line_final,
        'm_rate': round(m_in_line_final / len(line_final_tokens), 5),
    },
    'par_final': {
        'n': len(par_final_tokens),
        'm_count': m_in_par_final,
        'm_rate': round(m_in_par_final / len(par_final_tokens), 5),
    },
    'body_line_final_not_par_final': {
        'n': len(body_line_final),
        'm_count': m_in_body_final,
        'm_rate': round(m_in_body_final / max(len(body_line_final), 1), 5),
    },
    'header_line_final': {
        'n': len(header_line_final),
        'm_count': m_in_header_final,
        'm_rate': round(m_in_header_final / max(len(header_line_final), 1), 5),
    },
    'non_header_line_final': {
        'n': len(non_header_line_final),
        'm_count': m_in_non_header_final,
        'm_rate': round(m_in_non_header_final / max(len(non_header_line_final), 1), 5),
    },
    'folio_final': {
        'n': len(folio_final_tokens),
        'm_count': m_in_folio_final,
        'm_rate': round(m_in_folio_final / max(len(folio_final_tokens), 1), 5),
    },
    'non_final': {
        'n': len(non_final_tokens),
        'm_count': m_in_non_final,
        'm_rate': round(m_in_non_final / max(len(non_final_tokens), 1), 5),
    },
}
results['T3_scope'] = t3

print(f"m-terminal rate at line-final: {t3['line_final']['m_rate']:.4%} ({m_in_line_final}/{len(line_final_tokens)})")
print(f"m-terminal rate at par-final:  {t3['par_final']['m_rate']:.4%} ({m_in_par_final}/{len(par_final_tokens)})")
print(f"m-terminal rate at body-line-final (not par): {t3['body_line_final_not_par_final']['m_rate']:.4%}")
print(f"m-terminal rate at header-line-final: {t3['header_line_final']['m_rate']:.4%}")
print(f"m-terminal rate at non-header-line-final: {t3['non_header_line_final']['m_rate']:.4%}")
print(f"m-terminal rate at folio-final: {t3['folio_final']['m_rate']:.4%} ({m_in_folio_final}/{len(folio_final_tokens)})")
print(f"m-terminal rate NOT line-final: {t3['non_final']['m_rate']:.4%} ({m_in_non_final}/{len(non_final_tokens)})")

# Fisher's exact for par-final vs body-line-final
table_3 = np.array([
    [m_in_par_final, len(par_final_tokens) - m_in_par_final],
    [m_in_body_final, len(body_line_final) - m_in_body_final]
])
if table_3.min() >= 0 and table_3.sum() > 0:
    try:
        _, p_par_body = fisher_exact(table_3)
    except Exception:
        p_par_body = 1.0
else:
    p_par_body = 1.0

t3['par_vs_body_fisher_p'] = round(p_par_body, 6)
print(f"Fisher par-final vs body-line-final p={p_par_body:.6f}")

# ============================================================
# T4: m-terminal and PREFIX
# ============================================================
print("\n=== T4: m-terminal and PREFIX ===")

m_pfx = Counter([t['prefix'] or 'BARE' for t in m_term_tokens])
all_pfx = Counter([t['prefix'] or 'BARE' for t in all_tokens])
final_pfx = Counter([t['prefix'] or 'BARE' for t in line_final_tokens])

# m-terminal PREFIX distribution
m_pfx_dist = {}
for pfx, cnt in m_pfx.most_common(20):
    overall_frac = all_pfx[pfx] / N
    m_pfx_dist[pfx] = {
        'count': cnt,
        'frac_of_m': round(cnt / n_m, 4),
        'overall_frac': round(overall_frac, 4),
        'enrichment': round(safe_ratio(cnt / n_m, overall_frac), 2),
    }

# Chi-squared: PREFIX distribution for m-terminal vs all
top_pfx = [p for p, c in all_pfx.most_common(15)]
m_pfx_vec = [m_pfx.get(p, 0) for p in top_pfx]
all_pfx_vec = [all_pfx[p] - m_pfx.get(p, 0) for p in top_pfx]
if sum(m_pfx_vec) > 0 and sum(all_pfx_vec) > 0:
    ct = np.array([m_pfx_vec, all_pfx_vec])
    chi2_pfx, p_pfx, dof_pfx, _ = chi2_contingency(ct)
    v_pfx = math.sqrt(chi2_pfx / (ct.sum() * (min(ct.shape) - 1)))
else:
    chi2_pfx, p_pfx, v_pfx = 0, 1, 0

t4 = {
    'prefix_distribution': m_pfx_dist,
    'chi2': round(chi2_pfx, 1),
    'p': p_pfx,
    'cramers_v': round(v_pfx, 4),
}
results['T4_prefix'] = t4

print("PREFIX distribution for m-terminal:")
for pfx, info in sorted(m_pfx_dist.items(), key=lambda x: -x[1]['count']):
    print(f"  {pfx}: {info['count']} ({info['frac_of_m']:.1%}), enrichment {info['enrichment']:.2f}x")
print(f"Chi2={chi2_pfx:.1f}, p={p_pfx:.2e}, V={v_pfx:.4f}")

# ============================================================
# T5: m-terminal and suffix
# ============================================================
print("\n=== T5: m-terminal and suffix ===")

m_sfx = Counter([t['suffix'] or 'BARE' for t in m_term_tokens])
all_sfx = Counter([t['suffix'] or 'BARE' for t in all_tokens])

# Suffix rate
m_sfx_rate = sum(1 for t in m_term_tokens if t['suffix']) / max(n_m, 1)
all_sfx_rate = sum(1 for t in all_tokens if t['suffix']) / N

# Suffix mode assignment: Mode A = {d,e,ee,h,y}, Mode B = {a,i,ii,l,m,n,o,r,s}
MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

def suffix_mode(sfx):
    """Classify suffix into Mode A or Mode B based on first atom."""
    if not sfx:
        return None
    # Atomize suffix
    atoms = []
    i = 0
    while i < len(sfx):
        ch = sfx[i]
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(sfx) and sfx[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    if not atoms:
        return None
    first = atoms[0]
    if first in MODE_A_ATOMS:
        return 'A'
    elif first in MODE_B_ATOMS:
        return 'B'
    return None

m_modes = Counter([suffix_mode(t['suffix']) for t in m_term_tokens if t['suffix']])
all_modes = Counter([suffix_mode(t['suffix']) for t in all_tokens if t['suffix']])

# What specific suffixes appear on m-terminal tokens?
m_sfx_dist = {}
for sfx, cnt in m_sfx.most_common(15):
    overall_frac = all_sfx[sfx] / N
    m_sfx_dist[sfx] = {
        'count': cnt,
        'frac_of_m': round(cnt / n_m, 4),
        'overall_frac': round(overall_frac, 4),
    }

t5 = {
    'suffix_rate_m': round(m_sfx_rate, 4),
    'suffix_rate_all': round(all_sfx_rate, 4),
    'suffix_distribution': m_sfx_dist,
    'mode_dist_m': dict(m_modes),
    'mode_dist_all': dict(all_modes),
    'mode_a_frac_m': round(m_modes.get('A', 0) / max(sum(m_modes.values()), 1), 4),
    'mode_a_frac_all': round(all_modes.get('A', 0) / max(sum(all_modes.values()), 1), 4),
}
results['T5_suffix'] = t5

print(f"Suffix rate on m-terminal: {m_sfx_rate:.1%} (vs {all_sfx_rate:.1%} overall)")
print(f"Mode A frac (m-terminal): {t5['mode_a_frac_m']:.1%} (vs {t5['mode_a_frac_all']:.1%} overall)")
print("Suffix distribution on m-terminal:")
for sfx, info in sorted(m_sfx_dist.items(), key=lambda x: -x[1]['count']):
    print(f"  '{sfx}': {info['count']} ({info['frac_of_m']:.1%})")

# ============================================================
# T6: m-terminal and operational category
# ============================================================
print("\n=== T6: m-terminal and category ===")

m_cats = Counter([t['category'] for t in m_term_tokens if t['category']])
all_cats = Counter([t['category'] for t in all_tokens if t['category']])
n_classified = sum(all_cats.values())
m_classified = sum(m_cats.values())

cat_profile = {}
for cat in sorted(all_cats.keys()):
    m_frac = m_cats.get(cat, 0) / max(m_classified, 1)
    all_frac = all_cats[cat] / max(n_classified, 1)
    cat_profile[cat] = {
        'm_count': m_cats.get(cat, 0),
        'm_frac': round(m_frac, 4),
        'all_frac': round(all_frac, 4),
        'enrichment': round(safe_ratio(m_frac, all_frac), 2),
    }

# Per m-terminal MIDDLE: what category?
m_mid_cats = {}
for mid, cnt in m_term_middles.most_common():
    cat = cc.classify(mid)
    m_mid_cats[mid] = {'count': cnt, 'category': cat}

# Non-m-terminal TRANSITION tokens
non_m_transition = [t for t in all_tokens if t['category'] == 'TRANSITION' and t['terminal'] != 'm']
m_transition = [t for t in m_term_tokens if t['category'] == 'TRANSITION']

t6 = {
    'category_profile': cat_profile,
    'per_middle_category': m_mid_cats,
    'transition_m_count': len(m_transition),
    'transition_non_m_count': len(non_m_transition),
    'transition_total': len(m_transition) + len(non_m_transition),
    'm_frac_of_transition': round(len(m_transition) / max(len(m_transition) + len(non_m_transition), 1), 4),
}
results['T6_category'] = t6

print("Category profile for m-terminal MIDDLEs:")
for cat, info in sorted(cat_profile.items(), key=lambda x: -x[1]['enrichment']):
    print(f"  {cat}: {info['m_count']} ({info['m_frac']:.1%}), enrichment {info['enrichment']:.2f}x")
print(f"\nPer-MIDDLE categories:")
for mid, info in m_mid_cats.items():
    print(f"  '{mid}': {info['count']}x, category={info['category']}")
print(f"\nm-terminal as fraction of all TRANSITION: {t6['m_frac_of_transition']:.1%}")

# ============================================================
# T7: m-terminal and macro-state transitions (successor analysis)
# ============================================================
print("\n=== T7: m-terminal successor analysis ===")

# What category follows m-terminal tokens?
m_successor_cats = Counter()
non_m_final_successor_cats = Counter()
other_successor_cats = Counter()

# Build token sequences by line
for key, tokens in folio_lines.items():
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_tok = tokens[i + 1]
        next_cat = next_tok['category'] or 'UNK'
        if curr['terminal'] == 'm':
            m_successor_cats[next_cat] += 1
        elif curr['line_final']:
            # This shouldn't happen within a line, but as safety
            pass
        else:
            other_successor_cats[next_cat] += 1

# Cross-line successors: last token of line N -> first token of line N+1
sorted_keys = sorted(folio_lines.keys(), key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else 0))
folio_key_sequences = defaultdict(list)
for key in sorted_keys:
    folio_key_sequences[key[0]].append(key)

m_cross_line_succ = Counter()
non_m_cross_line_succ = Counter()

for folio, keys in folio_key_sequences.items():
    for i in range(len(keys) - 1):
        last_tok = folio_lines[keys[i]][-1]
        first_tok = folio_lines[keys[i + 1]][0]
        next_cat = first_tok['category'] or 'UNK'
        if last_tok['terminal'] == 'm':
            m_cross_line_succ[next_cat] += 1
        else:
            non_m_cross_line_succ[next_cat] += 1

# Category change rate after m vs after non-m
m_within_succ_total = sum(m_successor_cats.values())
m_cross_succ_total = sum(m_cross_line_succ.values())
nonm_cross_succ_total = sum(non_m_cross_line_succ.values())

t7 = {
    'within_line_successor_cats': dict(m_successor_cats.most_common()),
    'cross_line_successor_cats_after_m': dict(m_cross_line_succ.most_common()),
    'cross_line_successor_cats_after_nonm': dict(non_m_cross_line_succ.most_common()),
    'n_within_line_successors': m_within_succ_total,
    'n_cross_line_after_m': m_cross_succ_total,
    'n_cross_line_after_nonm': nonm_cross_succ_total,
}
results['T7_successors'] = t7

print("Within-line successors after m-terminal:")
for cat, cnt in m_successor_cats.most_common():
    print(f"  {cat}: {cnt} ({cnt/max(m_within_succ_total,1):.1%})")
print(f"\nCross-line successors (next line's first token):")
print(f"After m-terminal ({m_cross_succ_total} transitions):")
for cat, cnt in m_cross_line_succ.most_common():
    print(f"  {cat}: {cnt} ({cnt/max(m_cross_succ_total,1):.1%})")
print(f"After non-m-terminal ({nonm_cross_succ_total} transitions):")
for cat, cnt in non_m_cross_line_succ.most_common(5):
    print(f"  {cat}: {cnt} ({cnt/max(nonm_cross_succ_total,1):.1%})")

# ============================================================
# T8: m-terminal and hazard topology
# ============================================================
print("\n=== T8: m-terminal and hazard topology ===")

# Check forbidden pair involvement
# The 17 forbidden transitions are at class level. We don't have a class mapper,
# but we can check if m-terminal MIDDLEs appear in known hazardous categories.
# C1280: Hazard concentrates in FLOW/CONTAINMENT
# C820: CC is safe, C784: FL/AX hazard-immune
# Check: what fraction of m-terminal tokens are in hazard-associated categories?
hazard_cats = {'FLOW', 'CONTAINMENT'}
safe_cats = {'THERMAL', 'MONITORING', 'STAGING', 'MARKING', 'OPERATION'}

m_hazard = sum(1 for t in m_term_tokens if t['category'] in hazard_cats)
m_safe = sum(1 for t in m_term_tokens if t['category'] in safe_cats)
all_hazard = sum(1 for t in all_tokens if t['category'] in hazard_cats)
all_safe = sum(1 for t in all_tokens if t['category'] in safe_cats)

# Preceding and following hazard-associated tokens
m_preceded_by_hazard = 0
m_followed_by_hazard = 0
total_m_with_context = 0

for key, tokens in folio_lines.items():
    for i, tok in enumerate(tokens):
        if tok['terminal'] == 'm':
            total_m_with_context += 1
            if i > 0 and tokens[i-1]['category'] in hazard_cats:
                m_preceded_by_hazard += 1
            if i < len(tokens) - 1 and tokens[i+1]['category'] in hazard_cats:
                m_followed_by_hazard += 1

t8 = {
    'm_in_hazard_cats': m_hazard,
    'm_in_safe_cats': m_safe,
    'm_hazard_rate': round(m_hazard / max(n_m, 1), 4),
    'all_hazard_rate': round(all_hazard / max(N, 1), 4),
    'm_preceded_by_hazard': m_preceded_by_hazard,
    'm_followed_by_hazard': m_followed_by_hazard,
    'total_m_with_context': total_m_with_context,
}
results['T8_hazard'] = t8

print(f"m-terminal in hazard categories: {m_hazard} ({m_hazard/max(n_m,1):.1%})")
print(f"All tokens in hazard categories: {all_hazard} ({all_hazard/N:.1%})")
print(f"m preceded by hazard-cat: {m_preceded_by_hazard}/{total_m_with_context}")
print(f"m followed by hazard-cat: {m_followed_by_hazard}/{total_m_with_context}")

# ============================================================
# T9: m-terminal vs other rare terminals
# ============================================================
print("\n=== T9: Terminal comparison ===")

# Overall frequency of each terminal
term_freqs = {}
for term_char in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    cnt = sum(1 for t in all_tokens if t['terminal'] == term_char)
    term_freqs[term_char] = {
        'count': cnt,
        'frac': round(cnt / N, 5),
    }

# Line-final rate for each terminal
for term_char in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    final_cnt = sum(1 for t in line_final_tokens if t['terminal'] == term_char)
    overall_cnt = term_freqs[term_char]['count']
    term_freqs[term_char]['final_count'] = final_cnt
    term_freqs[term_char]['final_rate'] = round(final_cnt / max(len(line_final_tokens), 1), 5)
    term_freqs[term_char]['concentration_idx'] = round(
        safe_ratio(
            final_cnt / max(len(line_final_tokens), 1),
            overall_cnt / N
        ), 2
    )

# Line-initial rate
for term_char in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    initial_tokens = [t for t in all_tokens if t['line_initial']]
    initial_cnt = sum(1 for t in initial_tokens if t['terminal'] == term_char)
    term_freqs[term_char]['initial_count'] = initial_cnt
    term_freqs[term_char]['initial_rate'] = round(initial_cnt / max(len(initial_tokens), 1), 5)

t9 = {
    'terminal_comparison': term_freqs,
}
results['T9_comparison'] = t9

print("Terminal atom comparison:")
print(f"{'Term':>5} {'Count':>7} {'%All':>7} {'#Final':>7} {'%Final':>7} {'ConcIdx':>8} {'#Init':>7} {'%Init':>7}")
for tc in ['y', 'l', 'r', 'h', 'm', 'n', 'k', 't']:
    d = term_freqs[tc]
    print(f"  {tc:>3} {d['count']:>7} {d['frac']:>7.4f} {d['final_count']:>7} "
          f"{d['final_rate']:>7.4f} {d['concentration_idx']:>8.1f}x "
          f"{d['initial_count']:>7} {d['initial_rate']:>7.4f}")

# ============================================================
# T10: m-terminal as closure signal — functional test
# ============================================================
print("\n=== T10: m-terminal as closure signal ===")

# T10a: Line length of m-closed lines vs non-m-closed lines
m_closed_lengths = [lines_data[key]['length'] for key in lines_data
                    if folio_lines[key][-1]['terminal'] == 'm']
non_m_closed_lengths = [lines_data[key]['length'] for key in lines_data
                        if folio_lines[key][-1]['terminal'] != 'm']

m_len_mean = np.mean(m_closed_lengths) if m_closed_lengths else 0
non_m_len_mean = np.mean(non_m_closed_lengths) if non_m_closed_lengths else 0

if m_closed_lengths and non_m_closed_lengths:
    u_stat, u_p = mannwhitneyu(m_closed_lengths, non_m_closed_lengths, alternative='two-sided')
else:
    u_stat, u_p = 0, 1

# T10b: Category composition of m-closed lines vs non-m-closed
m_closed_cat_counts = Counter()
non_m_closed_cat_counts = Counter()
for key, tokens in folio_lines.items():
    for tok in tokens:
        cat = tok['category'] or 'UNK'
        if folio_lines[key][-1]['terminal'] == 'm':
            m_closed_cat_counts[cat] += 1
        else:
            non_m_closed_cat_counts[cat] += 1

m_closed_total = sum(m_closed_cat_counts.values())
non_m_closed_total = sum(non_m_closed_cat_counts.values())
cat_comparison = {}
for cat in set(list(m_closed_cat_counts.keys()) + list(non_m_closed_cat_counts.keys())):
    if cat == 'UNK':
        continue
    m_frac = m_closed_cat_counts[cat] / max(m_closed_total, 1)
    nm_frac = non_m_closed_cat_counts[cat] / max(non_m_closed_total, 1)
    cat_comparison[cat] = {
        'm_frac': round(m_frac, 4),
        'non_m_frac': round(nm_frac, 4),
        'ratio': round(safe_ratio(m_frac, nm_frac), 3),
    }

# T10c: Paragraph position of m-closed lines
# Are m-closed lines concentrated at specific paragraph positions?
m_closed_par_positions = []
non_m_closed_par_positions = []

# Group lines by paragraph (folio + paragraph index)
for key, tokens in folio_lines.items():
    is_m = tokens[-1]['terminal'] == 'm'
    is_par_init = tokens[0]['par_initial']
    is_par_final = tokens[-1]['par_final']
    # Encode as categorical position
    pos = 'body'
    if is_par_init and is_par_final:
        pos = 'single'
    elif is_par_init:
        pos = 'header'
    elif is_par_final:
        pos = 'last'
    if is_m:
        m_closed_par_positions.append(pos)
    else:
        non_m_closed_par_positions.append(pos)

m_par_pos_counts = Counter(m_closed_par_positions)
non_m_par_pos_counts = Counter(non_m_closed_par_positions)

# T10d: What follows m-closed lines (first token of next line)?
# Category of first token after m-closed line
m_next_line_init_cat = Counter()
nonm_next_line_init_cat = Counter()
m_next_line_init_pfx = Counter()
nonm_next_line_init_pfx = Counter()

for folio, keys in folio_key_sequences.items():
    for i in range(len(keys) - 1):
        last_tok = folio_lines[keys[i]][-1]
        first_tok = folio_lines[keys[i + 1]][0]
        next_cat = first_tok['category'] or 'UNK'
        next_pfx = first_tok['prefix'] or 'BARE'
        if last_tok['terminal'] == 'm':
            m_next_line_init_cat[next_cat] += 1
            m_next_line_init_pfx[next_pfx] += 1
        else:
            nonm_next_line_init_cat[next_cat] += 1
            nonm_next_line_init_pfx[next_pfx] += 1

# T10e: Section distribution of m-terminal
m_sections = Counter([t['section'] for t in m_term_tokens])
all_sections = Counter([t['section'] for t in all_tokens])
section_enrichment = {}
for sec in all_sections:
    m_frac = m_sections.get(sec, 0) / max(n_m, 1)
    all_frac = all_sections[sec] / N
    section_enrichment[sec] = {
        'm_count': m_sections.get(sec, 0),
        'm_frac': round(m_frac, 4),
        'all_frac': round(all_frac, 4),
        'enrichment': round(safe_ratio(m_frac, all_frac), 2),
    }

# T10f: -am suffix (recognized by morphology) vs m-terminal MIDDLE
am_suffix_tokens = [t for t in all_tokens if t['suffix'] and t['suffix'].endswith('am')]
n_am_sfx = len(am_suffix_tokens)
am_sfx_line_final_count = sum(1 for t in am_suffix_tokens if t['line_final'])
am_sfx_line_final_rate = am_sfx_line_final_count / max(n_am_sfx, 1)
# How many are also m-terminal in their MIDDLE?
am_sfx_m_term = sum(1 for t in am_suffix_tokens if t['terminal'] == 'm')

# m-terminal (MIDDLE ends in m) that do NOT have -am suffix
m_term_no_am = sum(1 for t in m_term_tokens if not (t['suffix'] and t['suffix'].endswith('am')))

t10 = {
    'line_length': {
        'm_closed_mean': round(m_len_mean, 2),
        'non_m_mean': round(non_m_len_mean, 2),
        'n_m_lines': len(m_closed_lengths),
        'n_nonm_lines': len(non_m_closed_lengths),
        'mann_whitney_U': float(u_stat),
        'p': round(u_p, 6),
    },
    'category_composition': cat_comparison,
    'paragraph_position': {
        'm_closed': dict(m_par_pos_counts),
        'non_m_closed': dict(non_m_par_pos_counts),
    },
    'next_line_initial_cat_after_m': dict(m_next_line_init_cat.most_common()),
    'next_line_initial_cat_after_nonm': dict(nonm_next_line_init_cat.most_common(8)),
    'next_line_initial_pfx_after_m': dict(m_next_line_init_pfx.most_common(10)),
    'section_enrichment': section_enrichment,
    'am_suffix_analysis': {
        'n_am_suffix': n_am_sfx,
        'am_suffix_line_final_rate': round(am_sfx_line_final_rate, 4),
        'am_suffix_also_m_terminal_middle': am_sfx_m_term,
        'm_terminal_without_am_suffix': m_term_no_am,
    },
}
results['T10_closure'] = t10

print(f"Line length: m-closed {m_len_mean:.1f} vs non-m {non_m_len_mean:.1f} (U-test p={u_p:.6f})")
print(f"N m-closed lines: {len(m_closed_lengths)}, N non-m: {len(non_m_closed_lengths)}")
print(f"\nCategory composition of m-closed vs non-m-closed lines:")
for cat, info in sorted(cat_comparison.items(), key=lambda x: -abs(x[1]['ratio'] - 1)):
    print(f"  {cat}: m={info['m_frac']:.1%} vs non-m={info['non_m_frac']:.1%} (ratio {info['ratio']:.3f})")
print(f"\nParagraph position of m-closed lines: {dict(m_par_pos_counts)}")
print(f"Paragraph position of non-m lines: {dict(non_m_par_pos_counts)}")
print(f"\nNext line initial category after m-closed:")
for cat, cnt in m_next_line_init_cat.most_common():
    print(f"  {cat}: {cnt} ({cnt/max(sum(m_next_line_init_cat.values()),1):.1%})")
print(f"\nSection enrichment:")
for sec, info in sorted(section_enrichment.items(), key=lambda x: -x[1]['enrichment']):
    print(f"  {sec}: {info['m_count']}x ({info['enrichment']:.2f}x enrichment)")
print(f"\n-am suffix analysis:")
print(f"  Tokens with -am suffix: {n_am_sfx}")
print(f"  -am suffix at line-final: {am_sfx_line_final_rate:.1%}")
print(f"  -am suffix also m-terminal MIDDLE: {am_sfx_m_term}")
print(f"  m-terminal MIDDLE without -am suffix: {m_term_no_am}/{n_m}")

# ============================================================
# ADDITIONAL DEEP-DIVES
# ============================================================

# A1: m-terminal tokens — full inventory with all annotations
print("\n=== A1: Full m-terminal token inventory ===")
m_token_types = Counter([t['word'] for t in m_term_tokens])
m_full_inventory = []
for word, cnt in m_token_types.most_common():
    sample = [t for t in m_term_tokens if t['word'] == word][0]
    m_full_inventory.append({
        'word': word,
        'count': cnt,
        'prefix': sample['prefix'],
        'middle': sample['middle'],
        'suffix': sample['suffix'],
        'category': sample['category'],
        'terminal': sample['terminal'],
        'head': sample['head_atom'],
    })
print(f"{'Word':>15} {'Count':>5} {'Pfx':>6} {'Mid':>6} {'Sfx':>6} {'Cat':>12} {'Head':>5}")
for item in m_full_inventory[:30]:
    print(f"  {item['word']:>13} {item['count']:>5} {str(item['prefix']):>6} "
          f"{item['middle']:>6} {str(item['suffix']):>6} {str(item['category']):>12} "
          f"{str(item['head']):>5}")

results['A1_full_inventory'] = m_full_inventory

# A2: Broader m context — any token containing m in MIDDLE, not just terminal
print("\n=== A2: All MIDDLEs containing m (any position) ===")
m_anywhere = Counter([t['middle'] for t in all_tokens if t['middle'] and 'm' in t['middle']])
print(f"MIDDLEs containing 'm' anywhere: {len(m_anywhere)} types, {sum(m_anywhere.values())} tokens")
# Is m always terminal or does it appear elsewhere?
m_non_terminal = {mid: cnt for mid, cnt in m_anywhere.items() if mid[-1] != 'm'}
print(f"MIDDLEs with m NOT at terminal: {len(m_non_terminal)} types, {sum(m_non_terminal.values())} tokens")
for mid, cnt in sorted(m_non_terminal.items(), key=lambda x: -x[1])[:15]:
    print(f"  '{mid}': {cnt}")

results['A2_m_anywhere'] = {
    'total_types': len(m_anywhere),
    'total_tokens': sum(m_anywhere.values()),
    'non_terminal_types': len(m_non_terminal),
    'non_terminal_tokens': sum(m_non_terminal.values()),
    'non_terminal_examples': [(mid, cnt) for mid, cnt in sorted(m_non_terminal.items(), key=lambda x: -x[1])[:15]],
}

# A3: -am suffix deep dive (C1237: -am paragraph terminator)
print("\n=== A3: -am suffix interaction with m-terminal ===")
# Tokens with suffix ending in 'am' — separate from m-terminal MIDDLE
am_sfx_cats = Counter([t['category'] for t in am_suffix_tokens if t['category']])
am_sfx_pfx = Counter([t['prefix'] or 'BARE' for t in am_suffix_tokens])
am_sfx_mid_term = Counter([t['terminal'] for t in am_suffix_tokens if t['terminal']])

# Double-m: suffix -am AND middle ends in m
double_m = [t for t in am_suffix_tokens if t['terminal'] == 'm']
print(f"-am suffix tokens: {n_am_sfx}")
print(f"-am suffix categories: {dict(am_sfx_cats.most_common())}")
print(f"-am suffix terminal atoms: {dict(am_sfx_mid_term.most_common())}")
print(f"Double-m (suffix -am + MIDDLE ends in m): {len(double_m)}")
for t in double_m[:10]:
    print(f"  {t['word']}: mid={t['middle']} sfx={t['suffix']} cat={t['category']}")

results['A3_am_suffix'] = {
    'n_am_suffix': n_am_sfx,
    'categories': dict(am_sfx_cats.most_common()),
    'prefixes': dict(am_sfx_pfx.most_common(10)),
    'middle_terminals': dict(am_sfx_mid_term.most_common()),
    'double_m_count': len(double_m),
    'double_m_examples': [{'word': t['word'], 'mid': t['middle'], 'sfx': t['suffix']}
                          for t in double_m[:10]],
}

# A4: Token preceding m-terminal: what's the penultimate token?
print("\n=== A4: Token preceding m-terminal (penultimate) ===")
pre_m_cats = Counter()
pre_m_terms = Counter()
pre_m_pfx = Counter()

for key, tokens in folio_lines.items():
    for i, tok in enumerate(tokens):
        if tok['terminal'] == 'm' and i > 0:
            prev = tokens[i - 1]
            pre_m_cats[prev['category'] or 'UNK'] += 1
            pre_m_terms[prev['terminal'] or 'UNK'] += 1
            pre_m_pfx[prev['prefix'] or 'BARE'] += 1

print(f"Category of token BEFORE m-terminal:")
for cat, cnt in pre_m_cats.most_common():
    print(f"  {cat}: {cnt} ({cnt/max(sum(pre_m_cats.values()),1):.1%})")
print(f"Terminal atom of token BEFORE m-terminal:")
for t, cnt in pre_m_terms.most_common():
    print(f"  {t}: {cnt}")

results['A4_preceding'] = {
    'preceding_categories': dict(pre_m_cats.most_common()),
    'preceding_terminals': dict(pre_m_terms.most_common()),
    'preceding_prefixes': dict(pre_m_pfx.most_common(10)),
}

# A5: Per-section m-terminal rate at line-final
print("\n=== A5: Per-section m-terminal at line-final ===")
section_m_final = {}
for sec in ['B', 'H', 'S', 'C', 'T']:
    sec_final = [t for t in line_final_tokens if t['section'] == sec]
    sec_m_final_cnt = sum(1 for t in sec_final if t['terminal'] == 'm')
    section_m_final[sec] = {
        'n_final': len(sec_final),
        'm_final': sec_m_final_cnt,
        'rate': round(sec_m_final_cnt / max(len(sec_final), 1), 4),
    }
    if sec_final:
        print(f"  {sec}: {sec_m_final_cnt}/{len(sec_final)} ({section_m_final[sec]['rate']:.1%})")

results['A5_section_final'] = section_m_final

# ============================================================
# SAVE RESULTS
# ============================================================
output_path = RESULTS_DIR / 'm_terminal_analysis.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

print(f"\n=== Results saved to {output_path} ===")
print(f"Total m-terminal tokens: {n_m} ({n_m/N:.3%})")
print(f"m-terminal at line-final: {t3['line_final']['m_rate']:.4%}")
print(f"m-terminal NOT at line-final: {t3['non_final']['m_rate']:.4%}")
print(f"Concentration index: {concentration_indices.get('m', 0):.1f}x")
