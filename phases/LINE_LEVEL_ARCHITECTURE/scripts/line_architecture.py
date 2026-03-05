"""
Phase 519: Line-Level Architecture
====================================

Systematic profiling of the Currier B line as a structural unit.
What IS a line? How does it differ from a paragraph or a token sequence?

Tests:
  T1.  Line length distribution (overall, by section, by paragraph position)
  T2.  Line-initial token profile (PREFIX, HEAD, TERMINAL, suffix, articulator, category)
  T3.  Line-final token profile (same dimensions)
  T4.  Positional gradient within lines (all dimensions by token position)
  T5.  PREFIX positional grammar validation (C1218-C1219 direct test)
  T6.  Line-internal transition structure (macro-state, category)
  T7.  Line-to-line independence (MI between consecutive lines)
  T8.  Line as information unit (entropy distribution)
  T9.  Line type classification (clustering)
  T10. Line boundary markers (boundary vs within-line transitions)

Validates: C1218, C1219, C1417, C1423, C976, C556, C670, C964
"""

import sys
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Section name mapping
SECTION_MAP = {
    'S': 'STARS_RECIPE', 'B': 'BIO', 'H': 'HERBAL',
    'C': 'COSMO', 'T': 'ZODIAC'
}

# Atom classifications per C1209 / C1210 / C1393
HEAD_SET = {'a', 'o', 'e', 'k', 't'}  # atoms that can be HEAD (initial)
TERM_SET = {'l', 'r', 'h', 'y', 'm', 'n', 'k', 't'}  # atoms that can be TERMINAL

# Macro-state mapping is not easily available without the full classifier,
# so we will focus on operational categories which ARE available via CategoryClassifier.


# --- Utility Functions -------------------------------------------

def entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def normalized_counts(counts, top_n=None):
    """Return dict of {key: fraction} from Counter, optionally top N."""
    total = sum(counts.values())
    if total == 0:
        return {}
    items = counts.most_common(top_n) if top_n else counts.most_common()
    return {k: round(v / total, 4) for k, v in items}


def chi2_independence(observed_matrix):
    """Simple chi-squared test for independence on a 2D dict-of-dicts.
    Returns chi2, dof, and approximate p-value flag."""
    # Build row/col totals
    rows = list(observed_matrix.keys())
    cols = set()
    for r in rows:
        cols.update(observed_matrix[r].keys())
    cols = sorted(cols)

    row_totals = {r: sum(observed_matrix[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(observed_matrix[r].get(c, 0) for r in rows) for c in cols}
    grand_total = sum(row_totals.values())

    if grand_total == 0:
        return 0.0, 0, 'N/A'

    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = observed_matrix[r].get(c, 0)
            exp = (row_totals[r] * col_totals[c]) / grand_total if grand_total > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    dof = (len(rows) - 1) * (len(cols) - 1)
    # Rough p-value category
    if dof > 0:
        chi2_per_dof = chi2 / dof
        if chi2_per_dof > 10:
            p_flag = 'p<0.001'
        elif chi2_per_dof > 5:
            p_flag = 'p<0.01'
        elif chi2_per_dof > 3:
            p_flag = 'p<0.05'
        else:
            p_flag = 'p>=0.05'
    else:
        p_flag = 'N/A'

    return chi2, dof, p_flag


def mutual_information(joint_counts):
    """Compute MI(X;Y) from joint_counts dict-of-dicts {x: {y: count}}."""
    # Marginals
    x_counts = Counter()
    y_counts = Counter()
    total = 0
    for x, yd in joint_counts.items():
        for y, c in yd.items():
            x_counts[x] += c
            y_counts[y] += c
            total += c

    if total == 0:
        return 0.0

    mi = 0.0
    for x, yd in joint_counts.items():
        for y, c in yd.items():
            if c > 0:
                p_xy = c / total
                p_x = x_counts[x] / total
                p_y = y_counts[y] / total
                if p_x > 0 and p_y > 0:
                    mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


# --- Data Loading ------------------------------------------------

def load_data():
    """Load all Currier B text tokens, organized by line."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Build line-organized data
    lines = defaultdict(list)  # (folio, line_num) -> [token_info_dict, ...]
    all_tokens = []

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue

        m = morph.extract(tok.word)
        mid = m.middle or ''
        cat = cc.classify(mid) if mid else None

        # HEAD and TERMINAL atom extraction
        head_atom = None
        term_atom = None
        if mid:
            if mid[0] in HEAD_SET:
                head_atom = mid[0]
            if mid[-1] in TERM_SET:
                term_atom = mid[-1]

        info = {
            'word': tok.word,
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
            'placement': tok.placement,
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
            'prefix': m.prefix,
            'middle': mid,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'has_suffix': m.suffix is not None,
            'has_articulator': m.articulator is not None,
            'head_atom': head_atom,
            'term_atom': term_atom,
            'category': cat,
        }

        key = (tok.folio, tok.line)
        lines[key].append(info)
        all_tokens.append(info)

    # Sort tokens within each line by their order
    # (they come in order from transcript, so this is already sorted)

    print(f"Loaded {len(all_tokens)} tokens across {len(lines)} lines")
    return lines, all_tokens


# --- T1: Line Length Distribution --------------------------------

def test_line_length(lines, all_tokens):
    """T1: Line length distribution."""
    print("\n=== T1: Line Length Distribution ===")

    lengths = []
    lengths_by_section = defaultdict(list)
    lengths_header = []  # paragraph-initial lines
    lengths_body = []    # non-paragraph-initial lines

    for key, toks in lines.items():
        n = len(toks)
        lengths.append(n)
        section = toks[0]['section']
        lengths_by_section[section].append(n)

        if toks[0]['par_initial']:
            lengths_header.append(n)
        else:
            lengths_body.append(n)

    # Overall stats
    mean_len = sum(lengths) / len(lengths)
    sorted_lens = sorted(lengths)
    median_len = sorted_lens[len(sorted_lens) // 2]
    std_len = (sum((x - mean_len) ** 2 for x in lengths) / len(lengths)) ** 0.5
    cv = std_len / mean_len if mean_len > 0 else 0

    # Distribution histogram
    len_counts = Counter(lengths)

    # Section breakdown
    section_stats = {}
    for sec, lens in lengths_by_section.items():
        sec_mean = sum(lens) / len(lens) if lens else 0
        sec_std = (sum((x - sec_mean) ** 2 for x in lens) / len(lens)) ** 0.5 if lens else 0
        section_stats[SECTION_MAP.get(sec, sec)] = {
            'n_lines': len(lens),
            'mean': round(sec_mean, 2),
            'std': round(sec_std, 2),
            'min': min(lens) if lens else 0,
            'max': max(lens) if lens else 0,
            'median': sorted(lens)[len(lens) // 2] if lens else 0,
        }

    # Header vs body
    header_mean = sum(lengths_header) / len(lengths_header) if lengths_header else 0
    body_mean = sum(lengths_body) / len(lengths_body) if lengths_body else 0

    result = {
        'n_lines': len(lengths),
        'n_tokens': len(all_tokens),
        'mean': round(mean_len, 2),
        'median': median_len,
        'std': round(std_len, 2),
        'cv': round(cv, 3),
        'min': min(lengths),
        'max': max(lengths),
        'length_distribution': {str(k): v for k, v in sorted(len_counts.items())},
        'by_section': section_stats,
        'header_mean': round(header_mean, 2),
        'body_mean': round(body_mean, 2),
        'header_body_ratio': round(header_mean / body_mean, 3) if body_mean > 0 else None,
        'n_header_lines': len(lengths_header),
        'n_body_lines': len(lengths_body),
    }

    print(f"  Overall: mean={mean_len:.1f}, median={median_len}, std={std_len:.1f}, CV={cv:.3f}")
    print(f"  Range: {min(lengths)}-{max(lengths)}")
    print(f"  Header lines: mean={header_mean:.1f} (n={len(lengths_header)})")
    print(f"  Body lines: mean={body_mean:.1f} (n={len(lengths_body)})")
    for sec, stats in sorted(section_stats.items()):
        print(f"  {sec}: mean={stats['mean']}, median={stats['median']}, n={stats['n_lines']}")

    return result


# --- T2: Line-Initial Token Profile ------------------------------

def test_initial_profile(lines, all_tokens):
    """T2: Line-initial token profile."""
    print("\n=== T2: Line-Initial Token Profile ===")

    initial_tokens = [toks[0] for toks in lines.values() if toks]
    n_initial = len(initial_tokens)

    # Overall population for comparison
    all_prefixes = Counter(t['prefix'] for t in all_tokens if t['prefix'])
    all_heads = Counter(t['head_atom'] for t in all_tokens if t['head_atom'])
    all_terms = Counter(t['term_atom'] for t in all_tokens if t['term_atom'])
    all_suffix_rate = sum(1 for t in all_tokens if t['has_suffix']) / len(all_tokens)
    all_artic_rate = sum(1 for t in all_tokens if t['has_articulator']) / len(all_tokens)
    all_cats = Counter(t['category'] for t in all_tokens if t['category'])

    # Line-initial populations
    init_prefixes = Counter(t['prefix'] for t in initial_tokens if t['prefix'])
    init_heads = Counter(t['head_atom'] for t in initial_tokens if t['head_atom'])
    init_terms = Counter(t['term_atom'] for t in initial_tokens if t['term_atom'])
    init_suffix_rate = sum(1 for t in initial_tokens if t['has_suffix']) / n_initial
    init_artic_rate = sum(1 for t in initial_tokens if t['has_articulator']) / n_initial
    init_cats = Counter(t['category'] for t in initial_tokens if t['category'])

    # PREFIX enrichment
    prefix_enrichment = {}
    for pfx in set(list(all_prefixes.keys()) + list(init_prefixes.keys())):
        init_frac = init_prefixes.get(pfx, 0) / n_initial
        all_frac = all_prefixes.get(pfx, 0) / len(all_tokens) if all_prefixes.get(pfx, 0) > 0 else 0.001
        if all_frac > 0:
            prefix_enrichment[pfx] = round(init_frac / all_frac, 2)

    # Category enrichment
    cat_enrichment = {}
    for cat in set(list(all_cats.keys()) + list(init_cats.keys())):
        init_frac = init_cats.get(cat, 0) / n_initial
        all_frac = all_cats.get(cat, 0) / len(all_tokens) if all_cats.get(cat, 0) > 0 else 0.001
        if all_frac > 0:
            cat_enrichment[cat] = round(init_frac / all_frac, 2)

    result = {
        'n_initial': n_initial,
        'prefix_distribution': normalized_counts(init_prefixes, 15),
        'prefix_enrichment_vs_overall': dict(sorted(prefix_enrichment.items(), key=lambda x: -x[1])[:15]),
        'head_atom_distribution': normalized_counts(init_heads),
        'terminal_atom_distribution': normalized_counts(init_terms),
        'suffix_rate': round(init_suffix_rate, 4),
        'suffix_rate_overall': round(all_suffix_rate, 4),
        'suffix_enrichment': round(init_suffix_rate / all_suffix_rate, 3) if all_suffix_rate > 0 else None,
        'articulator_rate': round(init_artic_rate, 4),
        'articulator_rate_overall': round(all_artic_rate, 4),
        'articulator_enrichment': round(init_artic_rate / all_artic_rate, 3) if all_artic_rate > 0 else None,
        'category_distribution': normalized_counts(init_cats),
        'category_enrichment': dict(sorted(cat_enrichment.items(), key=lambda x: -x[1])),
        'top_initial_words': normalized_counts(Counter(t['word'] for t in initial_tokens), 20),
    }

    print(f"  n_initial={n_initial}")
    print(f"  Suffix rate: initial={init_suffix_rate:.3f} vs overall={all_suffix_rate:.3f} "
          f"(enrichment={init_suffix_rate/all_suffix_rate:.2f}x)")
    print(f"  Articulator rate: initial={init_artic_rate:.3f} vs overall={all_artic_rate:.3f} "
          f"(enrichment={init_artic_rate/all_artic_rate:.2f}x)")
    print(f"  Top PREFIX enrichments: {sorted(prefix_enrichment.items(), key=lambda x: -x[1])[:5]}")
    print(f"  Top category enrichments: {sorted(cat_enrichment.items(), key=lambda x: -x[1])[:5]}")

    return result


# --- T3: Line-Final Token Profile --------------------------------

def test_final_profile(lines, all_tokens):
    """T3: Line-final token profile."""
    print("\n=== T3: Line-Final Token Profile ===")

    final_tokens = [toks[-1] for toks in lines.values() if toks]
    parfinal_tokens = [toks[-1] for toks in lines.values() if toks and toks[-1]['par_final']]
    n_final = len(final_tokens)

    # Overall for comparison
    all_prefixes = Counter(t['prefix'] for t in all_tokens if t['prefix'])
    all_heads = Counter(t['head_atom'] for t in all_tokens if t['head_atom'])
    all_terms = Counter(t['term_atom'] for t in all_tokens if t['term_atom'])
    all_suffix_rate = sum(1 for t in all_tokens if t['has_suffix']) / len(all_tokens)
    all_artic_rate = sum(1 for t in all_tokens if t['has_articulator']) / len(all_tokens)
    all_cats = Counter(t['category'] for t in all_tokens if t['category'])

    # Line-final populations
    fin_prefixes = Counter(t['prefix'] for t in final_tokens if t['prefix'])
    fin_heads = Counter(t['head_atom'] for t in final_tokens if t['head_atom'])
    fin_terms = Counter(t['term_atom'] for t in final_tokens if t['term_atom'])
    fin_suffix_rate = sum(1 for t in final_tokens if t['has_suffix']) / n_final
    fin_artic_rate = sum(1 for t in final_tokens if t['has_articulator']) / n_final
    fin_cats = Counter(t['category'] for t in final_tokens if t['category'])

    # Enrichments
    prefix_enrichment = {}
    for pfx in set(list(all_prefixes.keys()) + list(fin_prefixes.keys())):
        fin_frac = fin_prefixes.get(pfx, 0) / n_final
        all_frac = all_prefixes.get(pfx, 0) / len(all_tokens) if all_prefixes.get(pfx, 0) > 0 else 0.001
        if all_frac > 0:
            prefix_enrichment[pfx] = round(fin_frac / all_frac, 2)

    cat_enrichment = {}
    for cat in set(list(all_cats.keys()) + list(fin_cats.keys())):
        fin_frac = fin_cats.get(cat, 0) / n_final
        all_frac = all_cats.get(cat, 0) / len(all_tokens) if all_cats.get(cat, 0) > 0 else 0.001
        if all_frac > 0:
            cat_enrichment[cat] = round(fin_frac / all_frac, 2)

    # Also compare line-final vs paragraph-final
    pf_cats = Counter(t['category'] for t in parfinal_tokens if t['category'])
    pf_suffix_rate = sum(1 for t in parfinal_tokens if t['has_suffix']) / len(parfinal_tokens) if parfinal_tokens else 0

    result = {
        'n_final': n_final,
        'n_paragraph_final': len(parfinal_tokens),
        'prefix_distribution': normalized_counts(fin_prefixes, 15),
        'prefix_enrichment_vs_overall': dict(sorted(prefix_enrichment.items(), key=lambda x: -x[1])[:15]),
        'head_atom_distribution': normalized_counts(fin_heads),
        'terminal_atom_distribution': normalized_counts(fin_terms),
        'suffix_rate': round(fin_suffix_rate, 4),
        'suffix_rate_overall': round(all_suffix_rate, 4),
        'suffix_enrichment': round(fin_suffix_rate / all_suffix_rate, 3) if all_suffix_rate > 0 else None,
        'articulator_rate': round(fin_artic_rate, 4),
        'articulator_rate_overall': round(all_artic_rate, 4),
        'articulator_enrichment': round(fin_artic_rate / all_artic_rate, 3) if all_artic_rate > 0 else None,
        'category_distribution': normalized_counts(fin_cats),
        'category_enrichment': dict(sorted(cat_enrichment.items(), key=lambda x: -x[1])),
        'paragraph_final_suffix_rate': round(pf_suffix_rate, 4),
        'paragraph_final_category_distribution': normalized_counts(pf_cats),
        'top_final_words': normalized_counts(Counter(t['word'] for t in final_tokens), 20),
    }

    print(f"  n_final={n_final}, n_par_final={len(parfinal_tokens)}")
    print(f"  Suffix rate: final={fin_suffix_rate:.3f} vs overall={all_suffix_rate:.3f} "
          f"(enrichment={fin_suffix_rate/all_suffix_rate:.2f}x)")
    print(f"  Articulator rate: final={fin_artic_rate:.3f} vs overall={all_artic_rate:.3f} "
          f"(enrichment={fin_artic_rate/all_artic_rate:.2f}x)")
    print(f"  Top PREFIX enrichments: {sorted(prefix_enrichment.items(), key=lambda x: -x[1])[:5]}")
    print(f"  Top category enrichments: {sorted(cat_enrichment.items(), key=lambda x: -x[1])[:5]}")

    return result


# --- T4: Positional Gradient Within Lines -------------------------

def test_positional_gradient(lines, all_tokens):
    """T4: Positional gradient within lines."""
    print("\n=== T4: Positional Gradient Within Lines ===")

    # Use normalized position (0-1) and also absolute position
    # For absolute, cap at position 15 (most lines <= 15 tokens)
    MAX_ABS_POS = 15

    # Collect by normalized quintile (5 bins: 0-0.2, 0.2-0.4, etc.)
    quintile_data = {q: [] for q in range(5)}

    # Collect by absolute position
    abs_pos_data = {p: [] for p in range(1, MAX_ABS_POS + 1)}

    for key, toks in lines.items():
        n = len(toks)
        if n < 2:
            continue
        for i, t in enumerate(toks):
            # Normalized position
            norm_pos = i / (n - 1) if n > 1 else 0.5
            q = min(int(norm_pos * 5), 4)
            quintile_data[q].append(t)

            # Absolute position (1-indexed)
            abs_p = i + 1
            if abs_p <= MAX_ABS_POS:
                abs_pos_data[abs_p].append(t)

    # Compute profiles per quintile
    quintile_profiles = {}
    for q in range(5):
        toks = quintile_data[q]
        if not toks:
            continue
        n = len(toks)
        profile = {
            'n_tokens': n,
            'prefix_distribution': normalized_counts(Counter(t['prefix'] for t in toks if t['prefix']), 10),
            'head_atom_distribution': normalized_counts(Counter(t['head_atom'] for t in toks if t['head_atom'])),
            'terminal_atom_distribution': normalized_counts(Counter(t['term_atom'] for t in toks if t['term_atom'])),
            'suffix_rate': round(sum(1 for t in toks if t['has_suffix']) / n, 4),
            'articulator_rate': round(sum(1 for t in toks if t['has_articulator']) / n, 4),
            'category_distribution': normalized_counts(Counter(t['category'] for t in toks if t['category'])),
            'bare_prefix_rate': round(sum(1 for t in toks if not t['prefix']) / n, 4),
        }
        quintile_profiles[f'Q{q}'] = profile

    # Compute key gradient metrics across quintiles
    gradient_metrics = {}
    for metric_name, extract_fn in [
        ('suffix_rate', lambda toks: sum(1 for t in toks if t['has_suffix']) / len(toks)),
        ('articulator_rate', lambda toks: sum(1 for t in toks if t['has_articulator']) / len(toks)),
        ('bare_prefix_rate', lambda toks: sum(1 for t in toks if not t['prefix']) / len(toks)),
        ('THERMAL_rate', lambda toks: sum(1 for t in toks if t['category'] == 'THERMAL') / max(1, sum(1 for t in toks if t['category']))),
        ('TRANSITION_rate', lambda toks: sum(1 for t in toks if t['category'] == 'TRANSITION') / max(1, sum(1 for t in toks if t['category']))),
        ('FLOW_rate', lambda toks: sum(1 for t in toks if t['category'] == 'FLOW') / max(1, sum(1 for t in toks if t['category']))),
        ('STAGING_rate', lambda toks: sum(1 for t in toks if t['category'] == 'STAGING') / max(1, sum(1 for t in toks if t['category']))),
        ('MARKING_rate', lambda toks: sum(1 for t in toks if t['category'] == 'MARKING') / max(1, sum(1 for t in toks if t['category']))),
        ('MONITORING_rate', lambda toks: sum(1 for t in toks if t['category'] == 'MONITORING') / max(1, sum(1 for t in toks if t['category']))),
    ]:
        values = []
        for q in range(5):
            if quintile_data[q]:
                values.append(round(extract_fn(quintile_data[q]), 4))
            else:
                values.append(None)
        gradient_metrics[metric_name] = values

    # Compute absolute position profiles for key metrics
    abs_profiles = {}
    for p in range(1, min(MAX_ABS_POS + 1, 13)):  # up to position 12
        toks = abs_pos_data.get(p, [])
        if len(toks) < 50:  # skip sparse positions
            continue
        n = len(toks)
        abs_profiles[str(p)] = {
            'n_tokens': n,
            'suffix_rate': round(sum(1 for t in toks if t['has_suffix']) / n, 4),
            'articulator_rate': round(sum(1 for t in toks if t['has_articulator']) / n, 4),
            'top_prefixes': normalized_counts(Counter(t['prefix'] for t in toks if t['prefix']), 5),
            'category_distribution': normalized_counts(Counter(t['category'] for t in toks if t['category'])),
        }

    result = {
        'quintile_profiles': quintile_profiles,
        'gradient_metrics': gradient_metrics,
        'absolute_position_profiles': abs_profiles,
    }

    print(f"  Quintile suffix rates: {gradient_metrics['suffix_rate']}")
    print(f"  Quintile articulator rates: {gradient_metrics['articulator_rate']}")
    print(f"  Quintile THERMAL rates: {gradient_metrics['THERMAL_rate']}")
    print(f"  Quintile TRANSITION rates: {gradient_metrics['TRANSITION_rate']}")
    print(f"  Quintile FLOW rates: {gradient_metrics['FLOW_rate']}")

    return result


# --- T5: PREFIX Positional Grammar Validation --------------------

def test_prefix_positional_grammar(lines, all_tokens):
    """T5: PREFIX positional grammar validation (C1218-C1219 direct test)."""
    print("\n=== T5: PREFIX Positional Grammar Validation ===")

    # For each PREFIX, compute the distribution of normalized positions
    prefix_positions = defaultdict(list)
    prefix_abs_positions = defaultdict(list)

    for key, toks in lines.items():
        n = len(toks)
        if n < 2:
            continue
        for i, t in enumerate(toks):
            pfx = t['prefix'] or 'BARE'
            norm_pos = i / (n - 1) if n > 1 else 0.5
            prefix_positions[pfx].append(norm_pos)
            prefix_abs_positions[pfx].append(i + 1)

    # Compute mean position and spread for each PREFIX
    prefix_stats = {}
    for pfx, positions in prefix_positions.items():
        if len(positions) < 20:
            continue
        mean_pos = sum(positions) / len(positions)
        std_pos = (sum((x - mean_pos) ** 2 for x in positions) / len(positions)) ** 0.5

        # Compute quintile distribution
        quintile_counts = Counter()
        for p in positions:
            q = min(int(p * 5), 4)
            quintile_counts[q] += 1
        quintile_dist = {f'Q{q}': round(quintile_counts.get(q, 0) / len(positions), 3) for q in range(5)}

        # Initial rate (Q0) and final rate (Q4) for classification
        init_rate = quintile_dist.get('Q0', 0)
        final_rate = quintile_dist.get('Q4', 0)

        prefix_stats[pfx] = {
            'n': len(positions),
            'mean_pos': round(mean_pos, 3),
            'std_pos': round(std_pos, 3),
            'quintile_distribution': quintile_dist,
            'initial_rate': round(init_rate, 3),
            'final_rate': round(final_rate, 3),
            'position_class': (
                'INITIAL_BIASED' if init_rate > 0.30 else
                'FINAL_BIASED' if final_rate > 0.30 else
                'CENTRAL' if mean_pos > 0.35 and mean_pos < 0.65 else
                'DISTRIBUTED'
            ),
        }

    # Count how many PREFIXes are position-restricted vs free
    position_classes = Counter(v['position_class'] for v in prefix_stats.values())

    # Test C1218 prediction: modifiers (q,d,f,p,y,s) at POS-0, bases (h,e) at POS-1+
    # Check: do PREFIXes starting with these characters show expected positions?
    modifier_chars = set('qdfpys')
    base_chars = set('he')
    modifier_pfx_positions = []
    base_pfx_positions = []
    for pfx, stats in prefix_stats.items():
        if pfx == 'BARE':
            continue
        if pfx[0] in modifier_chars:
            modifier_pfx_positions.append(stats['mean_pos'])
        elif pfx[0] in base_chars:
            base_pfx_positions.append(stats['mean_pos'])

    result = {
        'n_prefixes_tested': len(prefix_stats),
        'prefix_stats': dict(sorted(prefix_stats.items(), key=lambda x: x[1]['mean_pos'])),
        'position_class_counts': dict(position_classes),
        'modifier_char_mean_pos': round(sum(modifier_pfx_positions) / len(modifier_pfx_positions), 3) if modifier_pfx_positions else None,
        'base_char_mean_pos': round(sum(base_pfx_positions) / len(base_pfx_positions), 3) if base_pfx_positions else None,
    }

    print(f"  {len(prefix_stats)} PREFIXes tested")
    print(f"  Position classes: {dict(position_classes)}")
    most_initial = sorted(prefix_stats.items(), key=lambda x: x[1]['mean_pos'])[:5]
    most_final = sorted(prefix_stats.items(), key=lambda x: -x[1]['mean_pos'])[:5]
    print(f"  Most initial: {[(p, s['mean_pos']) for p, s in most_initial]}")
    print(f"  Most final: {[(p, s['mean_pos']) for p, s in most_final]}")

    return result


# --- T6: Line-Internal Transition Structure ----------------------

def test_internal_transitions(lines, all_tokens):
    """T6: Line-internal transition structure."""
    print("\n=== T6: Line-Internal Transition Structure ===")

    # Category-to-category transitions within lines
    cat_transitions = defaultdict(Counter)
    # PREFIX-to-PREFIX transitions within lines
    pfx_transitions = defaultdict(Counter)
    # HEAD atom to HEAD atom transitions
    head_transitions = defaultdict(Counter)

    n_transitions = 0

    for key, toks in lines.items():
        for i in range(len(toks) - 1):
            t1, t2 = toks[i], toks[i + 1]

            cat1 = t1['category'] or 'UNK'
            cat2 = t2['category'] or 'UNK'
            cat_transitions[cat1][cat2] += 1

            pfx1 = t1['prefix'] or 'BARE'
            pfx2 = t2['prefix'] or 'BARE'
            pfx_transitions[pfx1][pfx2] += 1

            h1 = t1['head_atom'] or 'none'
            h2 = t2['head_atom'] or 'none'
            head_transitions[h1][h2] += 1

            n_transitions += 1

    # Category transition entropy
    cat_entropy_values = []
    for src, targets in cat_transitions.items():
        e = entropy(targets)
        cat_entropy_values.append(e)
    mean_cat_entropy = sum(cat_entropy_values) / len(cat_entropy_values) if cat_entropy_values else 0

    # Self-transition rates (same category)
    total_cat_trans = sum(sum(v.values()) for v in cat_transitions.values())
    self_cat_trans = sum(cat_transitions[c].get(c, 0) for c in cat_transitions)
    self_cat_rate = self_cat_trans / total_cat_trans if total_cat_trans > 0 else 0

    # Category transition matrix (top 8 categories)
    top_cats = Counter()
    for src, targets in cat_transitions.items():
        for tgt, c in targets.items():
            top_cats[src] += c
    top_cat_names = [c for c, _ in top_cats.most_common(8)]

    cat_matrix = {}
    for src in top_cat_names:
        row = {}
        total = sum(cat_transitions[src].values())
        for tgt in top_cat_names:
            row[tgt] = round(cat_transitions[src].get(tgt, 0) / total, 3) if total > 0 else 0
        cat_matrix[src] = row

    # PREFIX self-transition rates
    pfx_self_rates = {}
    for pfx, targets in pfx_transitions.items():
        total = sum(targets.values())
        if total >= 20:
            self_count = targets.get(pfx, 0)
            pfx_self_rates[pfx] = round(self_count / total, 3)

    result = {
        'n_transitions': n_transitions,
        'category_transition_matrix': cat_matrix,
        'mean_category_transition_entropy': round(mean_cat_entropy, 3),
        'category_self_transition_rate': round(self_cat_rate, 3),
        'prefix_self_transition_rates': dict(sorted(pfx_self_rates.items(), key=lambda x: -x[1])[:15]),
    }

    print(f"  n_transitions={n_transitions}")
    print(f"  Category self-transition rate: {self_cat_rate:.3f}")
    print(f"  Mean category transition entropy: {mean_cat_entropy:.3f} bits")

    return result


# --- T7: Line-to-Line Independence -------------------------------

def test_line_independence(lines, all_tokens):
    """T7: Line-to-line independence (MI between consecutive lines)."""
    print("\n=== T7: Line-to-Line Independence ===")

    # Organize lines by folio, in order
    folio_lines = defaultdict(list)
    for (folio, line_num), toks in sorted(lines.items()):
        folio_lines[folio].append((line_num, toks))

    # Sort by line number within folio
    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

    # Compute consecutive line pairs
    consecutive_pairs = []
    for folio, line_list in folio_lines.items():
        for i in range(len(line_list) - 1):
            ln1, toks1 = line_list[i]
            ln2, toks2 = line_list[i + 1]
            consecutive_pairs.append((toks1, toks2))

    n_pairs = len(consecutive_pairs)

    # Test 1: Suffix mode (majority suffix type) of line N vs line N+1
    def get_line_suffix_mode(toks):
        suffix_types = Counter()
        for t in toks:
            if t['suffix']:
                # Classify suffix as terminal (-y, -dy, -hy, -ly, -ry, -edy, -eey, -ey) or other
                sfx = t['suffix']
                if sfx.endswith('y'):
                    suffix_types['terminal'] += 1
                elif sfx.endswith('in') or sfx.endswith('iin') or sfx.endswith('ain') or sfx.endswith('aiin'):
                    suffix_types['checkpoint'] += 1
                else:
                    suffix_types['other'] += 1
            else:
                suffix_types['bare'] += 1
        if not suffix_types:
            return 'bare'
        return suffix_types.most_common(1)[0][0]

    # Suffix mode MI
    suffix_joint = defaultdict(Counter)
    for toks1, toks2 in consecutive_pairs:
        m1 = get_line_suffix_mode(toks1)
        m2 = get_line_suffix_mode(toks2)
        suffix_joint[m1][m2] += 1

    suffix_mi = mutual_information(suffix_joint)

    # Test 2: Dominant category of line N vs line N+1
    def get_dominant_category(toks):
        cats = Counter(t['category'] for t in toks if t['category'])
        return cats.most_common(1)[0][0] if cats else 'UNK'

    cat_joint = defaultdict(Counter)
    for toks1, toks2 in consecutive_pairs:
        c1 = get_dominant_category(toks1)
        c2 = get_dominant_category(toks2)
        cat_joint[c1][c2] += 1

    cat_mi = mutual_information(cat_joint)

    # Test 3: Line-final token category vs next line-initial token category
    boundary_joint = defaultdict(Counter)
    for toks1, toks2 in consecutive_pairs:
        if toks1 and toks2:
            c1 = toks1[-1]['category'] or 'UNK'
            c2 = toks2[0]['category'] or 'UNK'
            boundary_joint[c1][c2] += 1

    boundary_mi = mutual_information(boundary_joint)

    # Test 4: Line length correlation
    len_pairs = [(len(toks1), len(toks2)) for toks1, toks2 in consecutive_pairs]
    mean_len1 = sum(l1 for l1, l2 in len_pairs) / len(len_pairs)
    mean_len2 = sum(l2 for l1, l2 in len_pairs) / len(len_pairs)
    cov = sum((l1 - mean_len1) * (l2 - mean_len2) for l1, l2 in len_pairs) / len(len_pairs)
    std1 = (sum((l1 - mean_len1) ** 2 for l1, l2 in len_pairs) / len(len_pairs)) ** 0.5
    std2 = (sum((l2 - mean_len2) ** 2 for l1, l2 in len_pairs) / len(len_pairs)) ** 0.5
    len_corr = cov / (std1 * std2) if std1 > 0 and std2 > 0 else 0

    # Test 5: MIDDLE vocabulary overlap between consecutive lines
    jaccard_values = []
    for toks1, toks2 in consecutive_pairs:
        mids1 = set(t['middle'] for t in toks1 if t['middle'])
        mids2 = set(t['middle'] for t in toks2 if t['middle'])
        if mids1 or mids2:
            intersection = len(mids1 & mids2)
            union = len(mids1 | mids2)
            jaccard_values.append(intersection / union if union > 0 else 0)

    mean_jaccard = sum(jaccard_values) / len(jaccard_values) if jaccard_values else 0

    result = {
        'n_consecutive_pairs': n_pairs,
        'suffix_mode_MI': round(suffix_mi, 4),
        'dominant_category_MI': round(cat_mi, 4),
        'boundary_category_MI': round(boundary_mi, 4),
        'line_length_correlation': round(len_corr, 4),
        'mean_vocabulary_jaccard': round(mean_jaccard, 4),
        'interpretation': (
            'INDEPENDENT' if cat_mi < 0.05 and boundary_mi < 0.05
            else 'WEAKLY_COUPLED' if cat_mi < 0.15
            else 'COUPLED'
        ),
    }

    print(f"  n_pairs={n_pairs}")
    print(f"  Suffix mode MI: {suffix_mi:.4f} bits")
    print(f"  Dominant category MI: {cat_mi:.4f} bits")
    print(f"  Boundary category MI: {boundary_mi:.4f} bits")
    print(f"  Line length correlation: {len_corr:.4f}")
    print(f"  Mean vocabulary Jaccard: {mean_jaccard:.4f}")
    print(f"  Verdict: {result['interpretation']}")

    return result


# --- T8: Line as Information Unit --------------------------------

def test_information_unit(lines, all_tokens):
    """T8: Line as information unit (entropy distribution)."""
    print("\n=== T8: Line as Information Unit ===")

    # Compute per-position information content
    # Use word-level entropy at each position
    all_word_counts = Counter(t['word'] for t in all_tokens)
    total_words = sum(all_word_counts.values())
    word_entropy_global = entropy(all_word_counts)

    # Information content = -log2(P(word)) for each token
    # Compute average information per position
    pos_info = defaultdict(list)
    for key, toks in lines.items():
        n = len(toks)
        if n < 3:
            continue
        for i, t in enumerate(toks):
            word_count = all_word_counts.get(t['word'], 1)
            info_content = -math.log2(word_count / total_words) if word_count > 0 else 0
            # Normalized position
            norm_pos = i / (n - 1) if n > 1 else 0.5
            q = min(int(norm_pos * 5), 4)
            pos_info[q].append(info_content)

    quintile_info = {}
    for q in range(5):
        vals = pos_info.get(q, [])
        if vals:
            quintile_info[f'Q{q}'] = {
                'mean_info_bits': round(sum(vals) / len(vals), 3),
                'n_tokens': len(vals),
            }

    # Per-line entropy distribution
    line_entropies = []
    for key, toks in lines.items():
        if len(toks) < 3:
            continue
        word_counts = Counter(t['word'] for t in toks)
        h = entropy(word_counts)
        line_entropies.append(h)

    mean_line_entropy = sum(line_entropies) / len(line_entropies) if line_entropies else 0
    max_possible = math.log2(10) if line_entropies else 0  # typical line ~10 tokens

    # How much does position 1 predict the rest?
    # MI(word_at_pos1; all_remaining_words_concatenated_category)
    # Simplified: MI(pos1_prefix; dominant_category_of_rest)
    pos1_rest_joint = defaultdict(Counter)
    for key, toks in lines.items():
        if len(toks) < 3:
            continue
        pos1_pfx = toks[0]['prefix'] or 'BARE'
        rest_cats = Counter(t['category'] for t in toks[1:] if t['category'])
        dom_cat = rest_cats.most_common(1)[0][0] if rest_cats else 'UNK'
        pos1_rest_joint[pos1_pfx][dom_cat] += 1

    pos1_rest_mi = mutual_information(pos1_rest_joint)

    result = {
        'word_entropy_global': round(word_entropy_global, 3),
        'quintile_info_content': quintile_info,
        'mean_line_entropy': round(mean_line_entropy, 3),
        'pos1_prefix_to_rest_category_MI': round(pos1_rest_mi, 4),
        'info_gradient': [quintile_info.get(f'Q{q}', {}).get('mean_info_bits', None) for q in range(5)],
    }

    print(f"  Global word entropy: {word_entropy_global:.3f} bits")
    print(f"  Mean line entropy: {mean_line_entropy:.3f} bits")
    print(f"  Info content by quintile: {[quintile_info.get(f'Q{q}', {}).get('mean_info_bits', None) for q in range(5)]}")
    print(f"  Pos1 PREFIX -> rest category MI: {pos1_rest_mi:.4f} bits")

    return result


# --- T9: Line Type Classification --------------------------------

def test_line_types(lines, all_tokens):
    """T9: Line type classification (simple profiling, not full clustering)."""
    print("\n=== T9: Line Type Classification ===")

    # Characterize each line by a feature vector
    line_profiles = []
    for key, toks in lines.items():
        if len(toks) < 2:
            continue

        n = len(toks)
        cats = Counter(t['category'] for t in toks if t['category'])
        total_cat = sum(cats.values())

        profile = {
            'key': f"{key[0]}_{key[1]}",
            'section': toks[0]['section'],
            'is_par_initial': toks[0]['par_initial'],
            'length': n,
            'suffix_rate': sum(1 for t in toks if t['has_suffix']) / n,
            'articulator_rate': sum(1 for t in toks if t['has_articulator']) / n,
            'bare_prefix_rate': sum(1 for t in toks if not t['prefix']) / n,
            'THERMAL_frac': cats.get('THERMAL', 0) / total_cat if total_cat > 0 else 0,
            'TRANSITION_frac': cats.get('TRANSITION', 0) / total_cat if total_cat > 0 else 0,
            'FLOW_frac': cats.get('FLOW', 0) / total_cat if total_cat > 0 else 0,
            'STAGING_frac': cats.get('STAGING', 0) / total_cat if total_cat > 0 else 0,
            'MARKING_frac': cats.get('MARKING', 0) / total_cat if total_cat > 0 else 0,
        }
        line_profiles.append(profile)

    # Classify lines by dominant category
    dom_cat_counts = Counter()
    for lp in line_profiles:
        cat_fracs = {k: lp[k] for k in ['THERMAL_frac', 'TRANSITION_frac', 'FLOW_frac', 'STAGING_frac', 'MARKING_frac']}
        dom = max(cat_fracs, key=cat_fracs.get).replace('_frac', '')
        dom_cat_counts[dom] += 1

    # Correlate with paragraph position
    header_dom = Counter()
    body_dom = Counter()
    for lp in line_profiles:
        cat_fracs = {k: lp[k] for k in ['THERMAL_frac', 'TRANSITION_frac', 'FLOW_frac', 'STAGING_frac', 'MARKING_frac']}
        dom = max(cat_fracs, key=cat_fracs.get).replace('_frac', '')
        if lp['is_par_initial']:
            header_dom[dom] += 1
        else:
            body_dom[dom] += 1

    # By section
    section_dom = defaultdict(Counter)
    for lp in line_profiles:
        cat_fracs = {k: lp[k] for k in ['THERMAL_frac', 'TRANSITION_frac', 'FLOW_frac', 'STAGING_frac', 'MARKING_frac']}
        dom = max(cat_fracs, key=cat_fracs.get).replace('_frac', '')
        section_dom[lp['section']][dom] += 1

    # Line length vs category profile
    short_lines = [lp for lp in line_profiles if lp['length'] <= 5]
    long_lines = [lp for lp in line_profiles if lp['length'] >= 10]

    short_suffix_rate = sum(lp['suffix_rate'] for lp in short_lines) / len(short_lines) if short_lines else 0
    long_suffix_rate = sum(lp['suffix_rate'] for lp in long_lines) / len(long_lines) if long_lines else 0

    result = {
        'n_lines_profiled': len(line_profiles),
        'dominant_category_distribution': normalized_counts(dom_cat_counts),
        'header_dominant_category': normalized_counts(header_dom),
        'body_dominant_category': normalized_counts(body_dom),
        'section_dominant_category': {SECTION_MAP.get(s, s): normalized_counts(v)
                                       for s, v in section_dom.items()},
        'short_line_suffix_rate': round(short_suffix_rate, 3),
        'long_line_suffix_rate': round(long_suffix_rate, 3),
        'n_short_lines': len(short_lines),
        'n_long_lines': len(long_lines),
    }

    print(f"  n_lines={len(line_profiles)}")
    print(f"  Dominant category: {normalized_counts(dom_cat_counts)}")
    print(f"  Header dominant: {normalized_counts(header_dom)}")
    print(f"  Body dominant: {normalized_counts(body_dom)}")

    return result


# --- T10: Line Boundary Markers ----------------------------------

def test_boundary_markers(lines, all_tokens):
    """T10: Line boundary markers - what distinguishes line boundaries?"""
    print("\n=== T10: Line Boundary Markers ===")

    # Organize lines by folio to get consecutive line pairs
    folio_lines = defaultdict(list)
    for (folio, line_num), toks in sorted(lines.items()):
        folio_lines[folio].append((line_num, toks))

    for folio in folio_lines:
        folio_lines[folio].sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

    # Compare: within-line transitions vs cross-line transitions
    within_cat_trans = defaultdict(Counter)
    cross_cat_trans = defaultdict(Counter)
    within_pfx_trans = defaultdict(Counter)
    cross_pfx_trans = defaultdict(Counter)

    for folio, line_list in folio_lines.items():
        for idx, (ln, toks) in enumerate(line_list):
            # Within-line transitions
            for i in range(len(toks) - 1):
                c1 = toks[i]['category'] or 'UNK'
                c2 = toks[i + 1]['category'] or 'UNK'
                within_cat_trans[c1][c2] += 1
                p1 = toks[i]['prefix'] or 'BARE'
                p2 = toks[i + 1]['prefix'] or 'BARE'
                within_pfx_trans[p1][p2] += 1

            # Cross-line transition (last token of this line -> first of next)
            if idx + 1 < len(line_list):
                next_toks = line_list[idx + 1][1]
                if toks and next_toks:
                    c1 = toks[-1]['category'] or 'UNK'
                    c2 = next_toks[0]['category'] or 'UNK'
                    cross_cat_trans[c1][c2] += 1
                    p1 = toks[-1]['prefix'] or 'BARE'
                    p2 = next_toks[0]['prefix'] or 'BARE'
                    cross_pfx_trans[p1][p2] += 1

    # Compare within vs cross entropy
    within_entropies = []
    for src, targets in within_cat_trans.items():
        if sum(targets.values()) >= 20:
            within_entropies.append(entropy(targets))
    cross_entropies = []
    for src, targets in cross_cat_trans.items():
        if sum(targets.values()) >= 20:
            cross_entropies.append(entropy(targets))

    mean_within = sum(within_entropies) / len(within_entropies) if within_entropies else 0
    mean_cross = sum(cross_entropies) / len(cross_entropies) if cross_entropies else 0

    # Also compare paragraph boundaries vs line boundaries
    par_cross_cat = defaultdict(Counter)
    nonpar_cross_cat = defaultdict(Counter)

    for folio, line_list in folio_lines.items():
        for idx in range(len(line_list) - 1):
            toks1 = line_list[idx][1]
            toks2 = line_list[idx + 1][1]
            if not toks1 or not toks2:
                continue
            c1 = toks1[-1]['category'] or 'UNK'
            c2 = toks2[0]['category'] or 'UNK'
            # Is the next line a paragraph start?
            if toks2[0]['par_initial']:
                par_cross_cat[c1][c2] += 1
            else:
                nonpar_cross_cat[c1][c2] += 1

    par_entropies = [entropy(v) for v in par_cross_cat.values() if sum(v.values()) >= 10]
    nonpar_entropies = [entropy(v) for v in nonpar_cross_cat.values() if sum(v.values()) >= 10]

    mean_par_cross = sum(par_entropies) / len(par_entropies) if par_entropies else 0
    mean_nonpar_cross = sum(nonpar_entropies) / len(nonpar_entropies) if nonpar_entropies else 0

    # Specific boundary patterns
    # What suffix/category ends lines most often?
    final_suffix_types = Counter()
    final_no_suffix = 0
    for key, toks in lines.items():
        if toks:
            sfx = toks[-1]['suffix']
            if sfx:
                final_suffix_types[sfx] += 1
            else:
                final_no_suffix += 1

    n_lines_total = len(lines)
    bare_final_rate = final_no_suffix / n_lines_total

    # Overall suffix type distribution for comparison
    all_suffix_types = Counter(t['suffix'] for t in all_tokens if t['suffix'])

    # Enrichment of suffix types at line-final
    suffix_enrichment = {}
    for sfx in final_suffix_types:
        fin_frac = final_suffix_types[sfx] / n_lines_total
        all_frac = all_suffix_types.get(sfx, 0) / len(all_tokens)
        if all_frac > 0:
            suffix_enrichment[sfx] = round(fin_frac / all_frac, 2)

    result = {
        'within_line_mean_entropy': round(mean_within, 3),
        'cross_line_mean_entropy': round(mean_cross, 3),
        'entropy_ratio_cross_vs_within': round(mean_cross / mean_within, 3) if mean_within > 0 else None,
        'paragraph_cross_mean_entropy': round(mean_par_cross, 3),
        'non_paragraph_cross_mean_entropy': round(mean_nonpar_cross, 3),
        'bare_suffix_final_rate': round(bare_final_rate, 3),
        'top_final_suffixes': normalized_counts(final_suffix_types, 10),
        'suffix_final_enrichment': dict(sorted(suffix_enrichment.items(), key=lambda x: -x[1])[:10]),
        'boundary_hierarchy': (
            'PARAGRAPH > LINE > WITHIN' if mean_par_cross > mean_cross > mean_within
            else 'LINE = PARAGRAPH' if abs(mean_par_cross - mean_cross) < 0.1
            else 'COMPLEX'
        ),
    }

    print(f"  Within-line transition entropy: {mean_within:.3f} bits")
    print(f"  Cross-line transition entropy: {mean_cross:.3f} bits")
    print(f"  Cross-paragraph transition entropy: {mean_par_cross:.3f} bits")
    print(f"  Non-paragraph cross-line entropy: {mean_nonpar_cross:.3f} bits")
    print(f"  Entropy ratio (cross/within): {mean_cross/mean_within:.3f}" if mean_within > 0 else "  N/A")
    print(f"  Bare suffix at line-final: {bare_final_rate:.3f}")
    print(f"  Verdict: {result['boundary_hierarchy']}")

    return result


# --- Main --------------------------------------------------------

def main():
    print("Phase 519: Line-Level Architecture")
    print("=" * 60)

    lines, all_tokens = load_data()

    results = {
        'phase': 'LINE_LEVEL_ARCHITECTURE',
        'phase_number': 519,
        'date': '2026-03-05',
        'n_tokens': len(all_tokens),
        'n_lines': len(lines),
    }

    results['T1_line_length'] = test_line_length(lines, all_tokens)
    results['T2_initial_profile'] = test_initial_profile(lines, all_tokens)
    results['T3_final_profile'] = test_final_profile(lines, all_tokens)
    results['T4_positional_gradient'] = test_positional_gradient(lines, all_tokens)
    results['T5_prefix_positional_grammar'] = test_prefix_positional_grammar(lines, all_tokens)
    results['T6_internal_transitions'] = test_internal_transitions(lines, all_tokens)
    results['T7_line_independence'] = test_line_independence(lines, all_tokens)
    results['T8_information_unit'] = test_information_unit(lines, all_tokens)
    results['T9_line_types'] = test_line_types(lines, all_tokens)
    results['T10_boundary_markers'] = test_boundary_markers(lines, all_tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total lines: {len(lines)}")
    print(f"Total tokens: {len(all_tokens)}")
    print(f"Mean line length: {results['T1_line_length']['mean']}")
    print(f"Line independence: {results['T7_line_independence']['interpretation']}")
    print(f"Boundary hierarchy: {results['T10_boundary_markers']['boundary_hierarchy']}")

    # Write results
    output_path = RESULTS_DIR / 'line_architecture.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to {output_path}")


if __name__ == '__main__':
    main()
