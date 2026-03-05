"""
Phase 517: ARTICULATOR Deep Dive
=================================

Comprehensive analysis of the ARTICULATOR slot in token structure:
  [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]

Tests T1-T10 examining inventory, selectivity, interactions, position,
paragraph structure, combinatorial constraints, and q-articulator identity.

All effect sizes compared against the known PREFIX->MIDDLE->SUFFIX chain
(C1411 V=0.414, C1412 V=0.503, C1413 V=0.276).
"""

import sys
import os
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ---
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Section label mapping (from voynich.py)
SECTION_LABELS = {
    'S': 'STARS', 'H': 'HERBAL', 'B': 'BIO', 'P': 'PHARMA',
    'C': 'COSMO', 'T': 'TEXT',
}

# Atom classifications per C1209/C1210/C1393
HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERM_SET = {'l', 'r', 'h', 'y', 'm', 'n', 'k', 't'}

# Known reference effect sizes from C1411-C1413
REF_PREFIX_MIDDLE_V = 0.414   # PREFIX -> MIDDLE HEAD (C1411)
REF_MIDDLE_SUFFIX_V = 0.503   # MIDDLE TERM -> SUFFIX HEAD (C1412)
REF_PREFIX_SUFFIX_V = 0.276   # PREFIX -> SUFFIX HEAD (C1413)


# ============================================================
# Statistical helpers
# ============================================================
def cramers_v(contingency):
    """Compute Cramer's V from a contingency dict-of-dicts."""
    # Build matrix
    rows = sorted(contingency.keys())
    cols = sorted(set(c for r in contingency.values() for c in r))
    if len(rows) < 2 or len(cols) < 2:
        return 0.0, 1.0, 0

    n_total = sum(contingency[r].get(c, 0) for r in rows for c in cols)
    if n_total == 0:
        return 0.0, 1.0, 0

    # Expected frequencies and chi-square
    row_totals = {r: sum(contingency[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency[r].get(c, 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            observed = contingency[r].get(c, 0)
            expected = row_totals[r] * col_totals[c] / n_total
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    k = min(len(rows), len(cols))
    if k <= 1 or n_total <= 1:
        return 0.0, 1.0, n_total

    v = math.sqrt(chi2 / (n_total * (k - 1)))

    # Approximate p-value using chi-square distribution
    df = (len(rows) - 1) * (len(cols) - 1)
    p = chi2_pvalue(chi2, df)

    return v, p, n_total


def chi2_pvalue(chi2, df):
    """Approximate chi-square p-value using Wilson-Hilferty approximation."""
    if df <= 0 or chi2 <= 0:
        return 1.0
    z = ((chi2 / df) ** (1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    # Standard normal CDF approximation
    p = 0.5 * math.erfc(z / math.sqrt(2))
    return max(p, 1e-300)


def mutual_info(joint_counts, margin_x_counts, margin_y_counts, n_total):
    """Compute mutual information I(X;Y) in bits."""
    if n_total == 0:
        return 0.0
    mi = 0.0
    for (x, y), count in joint_counts.items():
        if count == 0:
            continue
        px = margin_x_counts[x] / n_total
        py = margin_y_counts[y] / n_total
        pxy = count / n_total
        if px > 0 and py > 0 and pxy > 0:
            mi += pxy * math.log2(pxy / (px * py))
    return mi


def conditional_mi(xyz_counts, xz_counts, yz_counts, z_counts, n_total):
    """Compute conditional MI: I(X;Y|Z) = sum_z P(z) * I(X;Y|Z=z).

    xyz_counts: {(x,y,z): count}
    xz_counts: {(x,z): count}
    yz_counts: {(y,z): count}
    z_counts: {z: count}
    """
    if n_total == 0:
        return 0.0

    cmi = 0.0
    for z, nz in z_counts.items():
        if nz == 0:
            continue
        pz = nz / n_total
        # Compute I(X;Y|Z=z)
        mi_z = 0.0
        for (x, y, zz), count in xyz_counts.items():
            if zz != z or count == 0:
                continue
            pxy_z = count / nz
            px_z = xz_counts.get((x, z), 0) / nz
            py_z = yz_counts.get((y, z), 0) / nz
            if px_z > 0 and py_z > 0 and pxy_z > 0:
                mi_z += pxy_z * math.log2(pxy_z / (px_z * py_z))
        cmi += pz * mi_z
    return cmi


def enrichment_ratio(observed, expected):
    """Compute enrichment ratio, handling zero expected."""
    if expected == 0:
        return float('inf') if observed > 0 else 1.0
    return observed / expected


# ============================================================
# Data loading
# ============================================================
def load_data():
    """Load and pre-process all Currier B tokens."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        mid = m.middle or ''

        # MIDDLE HEAD and TERMINAL atoms
        head = mid[0] if mid and mid[0] in HEAD_SET else None
        term = mid[-1] if mid and mid[-1] in TERM_SET and len(mid) > 1 else None
        if mid and len(mid) == 1:
            # Single-char MIDDLE: it's the head, no terminal
            head = mid[0] if mid[0] in HEAD_SET else None
            term = None

        # Category
        cat = cc.classify(mid) if mid else None

        # Line position (normalized)
        try:
            line_num = int(t.line) if t.line else 0
        except ValueError:
            line_num = 0

        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'line_num': line_num,
            'section': t.section,
            'section_label': SECTION_LABELS.get(t.section, t.section),
            'line_initial': t.line_initial,
            'line_final': t.line_final,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'articulator': m.articulator,
            'prefix': m.prefix,
            'middle': mid,
            'suffix': m.suffix,
            'head': head,
            'term': term,
            'category': cat,
        })

    return tokens


# ============================================================
# T1: Inventory and frequency
# ============================================================
def test_t1(tokens):
    """T1: ARTICULATOR inventory and frequency."""
    print("=" * 70)
    print("T1: ARTICULATOR Inventory and Frequency")
    print("=" * 70)

    total = len(tokens)
    art_counter = Counter()
    for t in tokens:
        art_counter[t['articulator'] or 'NONE'] += 1

    articulated = total - art_counter.get('NONE', 0)
    art_rate = articulated / total if total > 0 else 0

    print(f"\nTotal B tokens: {total}")
    print(f"Articulated: {articulated} ({art_rate:.1%})")
    print(f"Non-articulated: {art_counter.get('NONE', 0)} ({1 - art_rate:.1%})")
    print(f"\nPer articulator:")
    for art, count in art_counter.most_common():
        print(f"  {art:6s}: {count:6d} ({count/total:.3%})")

    # Per-section breakdown
    section_art = defaultdict(Counter)
    section_total = Counter()
    for t in tokens:
        sec = t['section_label']
        section_total[sec] += 1
        section_art[sec][t['articulator'] or 'NONE'] += 1

    print(f"\nPer-section articulator rates:")
    for sec in sorted(section_total.keys()):
        n = section_total[sec]
        n_art = n - section_art[sec].get('NONE', 0)
        rate = n_art / n if n > 0 else 0
        print(f"  {sec:8s}: {n_art:5d}/{n:5d} = {rate:.3%}")
        for art in sorted(section_art[sec].keys()):
            if art != 'NONE':
                c = section_art[sec][art]
                print(f"    {art}: {c:4d} ({c/n:.3%})")

    # Per-line-position breakdown
    pos_art = defaultdict(Counter)
    pos_total = Counter()
    for t in tokens:
        pos = 'initial' if t['line_initial'] else ('final' if t['line_final'] else 'medial')
        pos_total[pos] += 1
        pos_art[pos][t['articulator'] or 'NONE'] += 1

    print(f"\nPer-line-position articulator rates:")
    for pos in ['initial', 'medial', 'final']:
        n = pos_total[pos]
        n_art = n - pos_art[pos].get('NONE', 0)
        rate = n_art / n if n > 0 else 0
        print(f"  {pos:8s}: {n_art:5d}/{n:5d} = {rate:.3%}")

    return {
        'total_tokens': total,
        'articulated_count': articulated,
        'articulated_rate': round(art_rate, 4),
        'per_articulator': {k: v for k, v in art_counter.most_common()},
        'per_section': {
            sec: {
                'total': section_total[sec],
                'articulated': section_total[sec] - section_art[sec].get('NONE', 0),
                'rate': round((section_total[sec] - section_art[sec].get('NONE', 0)) / section_total[sec], 4)
                    if section_total[sec] > 0 else 0,
            }
            for sec in sorted(section_total.keys())
        },
        'per_position': {
            pos: {
                'total': pos_total[pos],
                'articulated': pos_total[pos] - pos_art[pos].get('NONE', 0),
                'rate': round((pos_total[pos] - pos_art[pos].get('NONE', 0)) / pos_total[pos], 4)
                    if pos_total[pos] > 0 else 0,
            }
            for pos in ['initial', 'medial', 'final']
        },
    }


# ============================================================
# T2: ARTICULATOR -> PREFIX selectivity
# ============================================================
def test_t2(tokens):
    """T2: ARTICULATOR -> PREFIX selectivity."""
    print("\n" + "=" * 70)
    print("T2: ARTICULATOR -> PREFIX Selectivity")
    print("=" * 70)

    contingency = defaultdict(Counter)
    for t in tokens:
        art = t['articulator'] or 'NONE'
        pfx = t['prefix'] or 'BARE'
        contingency[art][pfx] += 1

    v, p, n = cramers_v(contingency)
    print(f"\nCramer's V(ARTICULATOR, PREFIX) = {v:.4f}, p = {p:.2e}, N = {n}")
    print(f"  Reference: PREFIX->MIDDLE V = {REF_PREFIX_MIDDLE_V}")

    # Per-articulator top PREFIXes
    for art in ['NONE', 'y', 'k', 'd', 's', 'l', 'p', 'f', 'r', 't']:
        if art not in contingency:
            continue
        total_art = sum(contingency[art].values())
        if total_art < 10:
            continue
        top = contingency[art].most_common(5)
        top_str = ', '.join(f"{pfx}:{c}" for pfx, c in top)
        print(f"  {art:6s} (N={total_art:5d}): {top_str}")

    # Articulated vs non-articulated PREFIX distributions
    art_pfx = Counter()
    noart_pfx = Counter()
    for t in tokens:
        pfx = t['prefix'] or 'BARE'
        if t['articulator']:
            art_pfx[pfx] += 1
        else:
            noart_pfx[pfx] += 1

    n_art = sum(art_pfx.values())
    n_noart = sum(noart_pfx.values())
    print(f"\nArticulated vs Non-articulated PREFIX distribution:")
    all_pfxes = sorted(set(list(art_pfx.keys()) + list(noart_pfx.keys())),
                       key=lambda x: -(art_pfx.get(x, 0) + noart_pfx.get(x, 0)))
    for pfx in all_pfxes[:15]:
        art_frac = art_pfx.get(pfx, 0) / n_art if n_art > 0 else 0
        noart_frac = noart_pfx.get(pfx, 0) / n_noart if n_noart > 0 else 0
        ratio = enrichment_ratio(art_frac, noart_frac)
        print(f"  {pfx:6s}: art={art_frac:.3f} noart={noart_frac:.3f} ratio={ratio:.2f}")

    return {
        'cramers_v': round(v, 4),
        'p_value': p,
        'n': n,
        'per_articulator_top_prefixes': {
            art: dict(contingency[art].most_common(5))
            for art in contingency
            if sum(contingency[art].values()) >= 10
        },
    }


# ============================================================
# T3: ARTICULATOR -> MIDDLE selectivity
# ============================================================
def test_t3(tokens):
    """T3: ARTICULATOR -> MIDDLE HEAD and TERM selectivity."""
    print("\n" + "=" * 70)
    print("T3: ARTICULATOR -> MIDDLE Selectivity")
    print("=" * 70)

    # ARTICULATOR -> MIDDLE HEAD
    contingency_head = defaultdict(Counter)
    for t in tokens:
        if t['head'] is None:
            continue
        art = t['articulator'] or 'NONE'
        contingency_head[art][t['head']] += 1

    v_head, p_head, n_head = cramers_v(contingency_head)
    print(f"\nCramer's V(ARTICULATOR, MIDDLE HEAD) = {v_head:.4f}, p = {p_head:.2e}, N = {n_head}")
    print(f"  Reference: PREFIX->MIDDLE HEAD V = {REF_PREFIX_MIDDLE_V}")

    # ARTICULATOR -> MIDDLE TERMINAL
    contingency_term = defaultdict(Counter)
    for t in tokens:
        if t['term'] is None:
            continue
        art = t['articulator'] or 'NONE'
        contingency_term[art][t['term']] += 1

    v_term, p_term, n_term = cramers_v(contingency_term)
    print(f"Cramer's V(ARTICULATOR, MIDDLE TERM) = {v_term:.4f}, p = {p_term:.2e}, N = {n_term}")
    print(f"  Reference: MIDDLE TERM->SUFFIX V = {REF_MIDDLE_SUFFIX_V}")

    # Per-articulator HEAD distributions
    print(f"\nPer-articulator MIDDLE HEAD distributions:")
    for art in sorted(contingency_head.keys()):
        total_art = sum(contingency_head[art].values())
        if total_art < 10:
            continue
        top = contingency_head[art].most_common(5)
        top_str = ', '.join(f"{h}:{c/total_art:.2f}" for h, c in top)
        print(f"  {art:6s} (N={total_art:5d}): {top_str}")

    # Per-articulator TERM distributions
    print(f"\nPer-articulator MIDDLE TERM distributions:")
    for art in sorted(contingency_term.keys()):
        total_art = sum(contingency_term[art].values())
        if total_art < 10:
            continue
        top = contingency_term[art].most_common(5)
        top_str = ', '.join(f"{h}:{c/total_art:.2f}" for h, c in top)
        print(f"  {art:6s} (N={total_art:5d}): {top_str}")

    # ARTICULATOR -> MIDDLE controlling for PREFIX
    # Compute I(ARTICULATOR; MIDDLE HEAD | PREFIX)
    xyz_counts = Counter()  # (art, head, pfx)
    xz_counts = Counter()   # (art, pfx)
    yz_counts = Counter()   # (head, pfx)
    z_counts = Counter()    # pfx
    n_cmi = 0
    for t in tokens:
        if t['head'] is None:
            continue
        art = t['articulator'] or 'NONE'
        pfx = t['prefix'] or 'BARE'
        head = t['head']
        xyz_counts[(art, head, pfx)] += 1
        xz_counts[(art, pfx)] += 1
        yz_counts[(head, pfx)] += 1
        z_counts[pfx] += 1
        n_cmi += 1

    cmi = conditional_mi(xyz_counts, xz_counts, yz_counts, z_counts, n_cmi)
    # Also compute unconditional I(ART; HEAD)
    joint = Counter()
    art_margin = Counter()
    head_margin = Counter()
    for t in tokens:
        if t['head'] is None:
            continue
        art = t['articulator'] or 'NONE'
        head = t['head']
        joint[(art, head)] += 1
        art_margin[art] += 1
        head_margin[head] += 1
    mi_raw = mutual_info(joint, art_margin, head_margin, sum(art_margin.values()))

    print(f"\nInformation theory:")
    print(f"  I(ART; MIDDLE HEAD) = {mi_raw:.4f} bits")
    print(f"  I(ART; MIDDLE HEAD | PREFIX) = {cmi:.4f} bits")
    print(f"  Reduction by PREFIX control: {(1 - cmi/mi_raw)*100:.1f}%" if mi_raw > 0 else "  N/A")

    return {
        'middle_head': {
            'cramers_v': round(v_head, 4),
            'p_value': p_head,
            'n': n_head,
        },
        'middle_term': {
            'cramers_v': round(v_term, 4),
            'p_value': p_term,
            'n': n_term,
        },
        'mi_art_head': round(mi_raw, 4),
        'cmi_art_head_given_prefix': round(cmi, 4),
        'prefix_mediation_pct': round((1 - cmi/mi_raw)*100, 1) if mi_raw > 0 else None,
    }


# ============================================================
# T4: ARTICULATOR -> SUFFIX selectivity
# ============================================================
def test_t4(tokens):
    """T4: ARTICULATOR -> SUFFIX selectivity."""
    print("\n" + "=" * 70)
    print("T4: ARTICULATOR -> SUFFIX Selectivity")
    print("=" * 70)

    # Suffix presence/absence
    art_suffix = defaultdict(Counter)  # art -> {HAS_SUFFIX, NO_SUFFIX}
    for t in tokens:
        art = t['articulator'] or 'NONE'
        has_sfx = 'HAS_SUFFIX' if t['suffix'] else 'NO_SUFFIX'
        art_suffix[art][has_sfx] += 1

    print(f"\nSuffix presence rate by articulator:")
    for art in sorted(art_suffix.keys()):
        n = sum(art_suffix[art].values())
        if n < 10:
            continue
        sfx_rate = art_suffix[art].get('HAS_SUFFIX', 0) / n
        print(f"  {art:6s}: {sfx_rate:.3f} ({art_suffix[art].get('HAS_SUFFIX',0)}/{n})")

    # ARTICULATOR -> SUFFIX identity
    contingency = defaultdict(Counter)
    for t in tokens:
        if not t['suffix']:
            continue
        art = t['articulator'] or 'NONE'
        contingency[art][t['suffix']] += 1

    v, p, n = cramers_v(contingency)
    print(f"\nCramer's V(ARTICULATOR, SUFFIX) = {v:.4f}, p = {p:.2e}, N = {n}")
    print(f"  Reference: MIDDLE TERM->SUFFIX V = {REF_MIDDLE_SUFFIX_V}")

    # Suffix mode (Mode A = terminal suffixes like -edy, -ey; Mode B = bare/checkpoint)
    # Approximate: -edy, -eey, -ey, -dy, -hy, -ly, -ry, -y are terminal-heavy (Mode A leaning)
    # -aiin, -ain, -oiin, -oin, -iin, -in, -ol, -al, -ar, -or are checkpoint/continuation
    MODE_A_SUFFIXES = {'edy', 'eey', 'ey', 'dy', 'hy', 'ly', 'ry', 'y'}
    MODE_B_SUFFIXES = {'aiin', 'ain', 'oiin', 'oin', 'iin', 'in', 'ol', 'al', 'ar', 'or', 'am', 'om'}

    art_mode = defaultdict(Counter)
    for t in tokens:
        if not t['suffix']:
            continue
        art = t['articulator'] or 'NONE'
        if t['suffix'] in MODE_A_SUFFIXES:
            art_mode[art]['MODE_A'] += 1
        elif t['suffix'] in MODE_B_SUFFIXES:
            art_mode[art]['MODE_B'] += 1
        else:
            art_mode[art]['OTHER'] += 1

    print(f"\nSuffix mode by articulator (among suffixed tokens):")
    for art in sorted(art_mode.keys()):
        n = sum(art_mode[art].values())
        if n < 10:
            continue
        a_rate = art_mode[art].get('MODE_A', 0) / n
        b_rate = art_mode[art].get('MODE_B', 0) / n
        print(f"  {art:6s}: Mode A={a_rate:.3f} Mode B={b_rate:.3f} (N={n})")

    return {
        'suffix_presence': {
            art: {
                'rate': round(art_suffix[art].get('HAS_SUFFIX', 0) / max(sum(art_suffix[art].values()), 1), 4),
                'n': sum(art_suffix[art].values()),
            }
            for art in art_suffix
            if sum(art_suffix[art].values()) >= 10
        },
        'suffix_identity': {
            'cramers_v': round(v, 4),
            'p_value': p,
            'n': n,
        },
    }


# ============================================================
# T5: ARTICULATOR -> operational category
# ============================================================
def test_t5(tokens):
    """T5: ARTICULATOR -> operational category selectivity."""
    print("\n" + "=" * 70)
    print("T5: ARTICULATOR -> Operational Category")
    print("=" * 70)

    contingency = defaultdict(Counter)
    for t in tokens:
        if not t['category']:
            continue
        art = t['articulator'] or 'NONE'
        contingency[art][t['category']] += 1

    v, p, n = cramers_v(contingency)
    print(f"\nCramer's V(ARTICULATOR, CATEGORY) = {v:.4f}, p = {p:.2e}, N = {n}")

    # Per-articulator category distributions
    print(f"\nPer-articulator category distributions:")
    for art in sorted(contingency.keys()):
        total_art = sum(contingency[art].values())
        if total_art < 10:
            continue
        top = contingency[art].most_common(4)
        top_str = ', '.join(f"{cat}:{c/total_art:.2f}" for cat, c in top)
        print(f"  {art:6s} (N={total_art:5d}): {top_str}")

    # Conditional: I(ART; CATEGORY | PREFIX)
    xyz = Counter()
    xz = Counter()
    yz = Counter()
    zc = Counter()
    nc = 0
    for t in tokens:
        if not t['category']:
            continue
        art = t['articulator'] or 'NONE'
        pfx = t['prefix'] or 'BARE'
        cat = t['category']
        xyz[(art, cat, pfx)] += 1
        xz[(art, pfx)] += 1
        yz[(cat, pfx)] += 1
        zc[pfx] += 1
        nc += 1

    cmi_pfx = conditional_mi(xyz, xz, yz, zc, nc)

    # Also condition on MIDDLE
    xyz2 = Counter()
    xz2 = Counter()
    yz2 = Counter()
    zc2 = Counter()
    nc2 = 0
    for t in tokens:
        if not t['category'] or not t['middle']:
            continue
        art = t['articulator'] or 'NONE'
        mid = t['middle']
        cat = t['category']
        xyz2[(art, cat, mid)] += 1
        xz2[(art, mid)] += 1
        yz2[(cat, mid)] += 1
        zc2[mid] += 1
        nc2 += 1

    cmi_mid = conditional_mi(xyz2, xz2, yz2, zc2, nc2)

    # Raw MI
    joint = Counter()
    art_margin = Counter()
    cat_margin = Counter()
    for t in tokens:
        if not t['category']:
            continue
        art = t['articulator'] or 'NONE'
        cat = t['category']
        joint[(art, cat)] += 1
        art_margin[art] += 1
        cat_margin[cat] += 1
    mi_raw = mutual_info(joint, art_margin, cat_margin, sum(art_margin.values()))

    print(f"\nInformation theory (ARTICULATOR -> CATEGORY):")
    print(f"  I(ART; CAT) = {mi_raw:.4f} bits")
    print(f"  I(ART; CAT | PREFIX) = {cmi_pfx:.4f} bits")
    print(f"  I(ART; CAT | MIDDLE) = {cmi_mid:.4f} bits")
    print(f"  PREFIX mediation: {(1-cmi_pfx/mi_raw)*100:.1f}%" if mi_raw > 0 else "")
    print(f"  MIDDLE mediation: {(1-cmi_mid/mi_raw)*100:.1f}%" if mi_raw > 0 else "")

    return {
        'cramers_v': round(v, 4),
        'p_value': p,
        'n': n,
        'mi_raw': round(mi_raw, 4),
        'cmi_given_prefix': round(cmi_pfx, 4),
        'cmi_given_middle': round(cmi_mid, 4),
        'prefix_mediation_pct': round((1-cmi_pfx/mi_raw)*100, 1) if mi_raw > 0 else None,
        'middle_mediation_pct': round((1-cmi_mid/mi_raw)*100, 1) if mi_raw > 0 else None,
    }


# ============================================================
# T6: ARTICULATOR in the information chain
# ============================================================
def test_t6(tokens):
    """T6: ARTICULATOR interaction with PREFIX->MIDDLE->SUFFIX chain."""
    print("\n" + "=" * 70)
    print("T6: ARTICULATOR in the Information Chain")
    print("=" * 70)

    # Pairwise MI: ART<->PREFIX, ART<->MIDDLE, ART<->SUFFIX
    pairs = [
        ('ART', 'PREFIX', lambda t: (t['articulator'] or 'NONE', t['prefix'] or 'BARE')),
        ('ART', 'MIDDLE', lambda t: (t['articulator'] or 'NONE', t['middle'] or '_EMPTY_')),
        ('ART', 'SUFFIX', lambda t: (t['articulator'] or 'NONE', t['suffix'] or '_NONE_')),
        ('PREFIX', 'MIDDLE', lambda t: (t['prefix'] or 'BARE', t['middle'] or '_EMPTY_')),
        ('PREFIX', 'SUFFIX', lambda t: (t['prefix'] or 'BARE', t['suffix'] or '_NONE_')),
        ('MIDDLE', 'SUFFIX', lambda t: (t['middle'] or '_EMPTY_', t['suffix'] or '_NONE_')),
    ]

    mi_results = {}
    for name_x, name_y, extract_fn in pairs:
        joint = Counter()
        margin_x = Counter()
        margin_y = Counter()
        n = 0
        for t in tokens:
            x, y = extract_fn(t)
            joint[(x, y)] += 1
            margin_x[x] += 1
            margin_y[y] += 1
            n += 1
        mi = mutual_info(joint, margin_x, margin_y, n)
        mi_results[f"I({name_x};{name_y})"] = round(mi, 4)

    print(f"\nPairwise mutual information (bits):")
    for key, val in mi_results.items():
        print(f"  {key:25s} = {val:.4f}")

    # Three-way: I(MIDDLE; ART, PREFIX) vs I(MIDDLE; PREFIX)
    # Does ART add to MIDDLE beyond PREFIX?
    # I(MIDDLE; ART | PREFIX) = I(MIDDLE; ART, PREFIX) - I(MIDDLE; PREFIX)

    # I(MIDDLE; ART | PREFIX) via conditional MI
    xyz_counts = Counter()
    xz_counts = Counter()
    yz_counts = Counter()
    z_counts = Counter()
    n_3way = 0
    for t in tokens:
        mid = t['middle'] or '_EMPTY_'
        art = t['articulator'] or 'NONE'
        pfx = t['prefix'] or 'BARE'
        xyz_counts[(mid, art, pfx)] += 1
        xz_counts[(mid, pfx)] += 1
        yz_counts[(art, pfx)] += 1
        z_counts[pfx] += 1
        n_3way += 1

    cmi_mid_art_pfx = conditional_mi(xyz_counts, xz_counts, yz_counts, z_counts, n_3way)

    # I(SUFFIX; ART | MIDDLE)
    xyz2 = Counter()
    xz2 = Counter()
    yz2 = Counter()
    z2 = Counter()
    n2 = 0
    for t in tokens:
        sfx = t['suffix'] or '_NONE_'
        art = t['articulator'] or 'NONE'
        mid = t['middle'] or '_EMPTY_'
        xyz2[(sfx, art, mid)] += 1
        xz2[(sfx, mid)] += 1
        yz2[(art, mid)] += 1
        z2[mid] += 1
        n2 += 1

    cmi_sfx_art_mid = conditional_mi(xyz2, xz2, yz2, z2, n2)

    print(f"\nConditional MI (ARTICULATOR contribution beyond chain):")
    print(f"  I(MIDDLE; ART | PREFIX) = {cmi_mid_art_pfx:.4f} bits (ART adds to MIDDLE beyond PREFIX)")
    print(f"  I(SUFFIX; ART | MIDDLE) = {cmi_sfx_art_mid:.4f} bits (ART adds to SUFFIX beyond MIDDLE)")

    return {
        'pairwise_mi': mi_results,
        'cmi_middle_art_given_prefix': round(cmi_mid_art_pfx, 4),
        'cmi_suffix_art_given_middle': round(cmi_sfx_art_mid, 4),
    }


# ============================================================
# T7: ARTICULATOR and line position
# ============================================================
def test_t7(tokens):
    """T7: ARTICULATOR and line position."""
    print("\n" + "=" * 70)
    print("T7: ARTICULATOR and Line Position")
    print("=" * 70)

    # Group tokens by line to compute normalized position
    folio_line_tokens = defaultdict(list)
    for i, t in enumerate(tokens):
        folio_line_tokens[(t['folio'], t['line'])].append(i)

    # Compute normalized position for each token
    positions = [0.0] * len(tokens)
    for (fol, line), indices in folio_line_tokens.items():
        n = len(indices)
        for j, idx in enumerate(indices):
            positions[idx] = j / max(n - 1, 1)

    # Bin into quintiles
    quintile_art = defaultdict(Counter)
    quintile_total = Counter()
    for i, t in enumerate(tokens):
        q = min(int(positions[i] * 5), 4)  # 0-4
        quintile_total[q] += 1
        art = t['articulator'] or 'NONE'
        quintile_art[q][art] += 1

    print(f"\nArticulator rate by line position quintile:")
    for q in range(5):
        n = quintile_total[q]
        n_art = n - quintile_art[q].get('NONE', 0)
        rate = n_art / n if n > 0 else 0
        label = ['Q0(initial)', 'Q1', 'Q2', 'Q3', 'Q4(final)'][q]
        print(f"  {label:15s}: {rate:.4f} ({n_art}/{n})")

    # Per-articulator positional profiles
    print(f"\nPer-articulator positional profiles (quintile rates):")
    all_arts = sorted(set(t['articulator'] for t in tokens if t['articulator']))
    for art in all_arts:
        total_this = sum(1 for t in tokens if t['articulator'] == art)
        if total_this < 20:
            continue
        qs = []
        for q in range(5):
            c = quintile_art[q].get(art, 0)
            expected = total_this / 5
            ratio = c / expected if expected > 0 else 0
            qs.append(f"{ratio:.2f}")
        print(f"  {art}: [{', '.join(qs)}] (N={total_this})")

    # Chi-square: position quintile x articulator
    contingency = defaultdict(Counter)
    for i, t in enumerate(tokens):
        q = min(int(positions[i] * 5), 4)
        art = t['articulator'] or 'NONE'
        contingency[str(q)][art] += 1

    v, p, n = cramers_v(contingency)
    print(f"\nCramer's V(position quintile, ARTICULATOR) = {v:.4f}, p = {p:.2e}, N = {n}")

    return {
        'cramers_v_position': round(v, 4),
        'p_value': p,
        'quintile_rates': {
            q: {
                'total': quintile_total[q],
                'articulated': quintile_total[q] - quintile_art[q].get('NONE', 0),
                'rate': round((quintile_total[q] - quintile_art[q].get('NONE', 0)) / max(quintile_total[q], 1), 4),
            }
            for q in range(5)
        },
    }


# ============================================================
# T8: ARTICULATOR and paragraph structure
# ============================================================
def test_t8(tokens):
    """T8: ARTICULATOR and paragraph structure."""
    print("\n" + "=" * 70)
    print("T8: ARTICULATOR and Paragraph Structure")
    print("=" * 70)

    # Header (par_initial) vs body
    header_counts = Counter()
    body_counts = Counter()
    for t in tokens:
        art = t['articulator'] or 'NONE'
        if t['par_initial']:
            header_counts[art] += 1
        else:
            body_counts[art] += 1

    n_header = sum(header_counts.values())
    n_body = sum(body_counts.values())
    header_art_rate = (n_header - header_counts.get('NONE', 0)) / n_header if n_header > 0 else 0
    body_art_rate = (n_body - body_counts.get('NONE', 0)) / n_body if n_body > 0 else 0

    print(f"\nArticulator rate:")
    print(f"  Header lines: {header_art_rate:.4f} (N={n_header})")
    print(f"  Body lines:   {body_art_rate:.4f} (N={n_body})")
    print(f"  Ratio: {header_art_rate/body_art_rate:.3f}x" if body_art_rate > 0 else "")

    # Par-final tokens
    parfinal_art = Counter()
    notparfinal_art = Counter()
    for t in tokens:
        art = t['articulator'] or 'NONE'
        if t['par_final']:
            parfinal_art[art] += 1
        else:
            notparfinal_art[art] += 1

    n_pf = sum(parfinal_art.values())
    n_npf = sum(notparfinal_art.values())
    pf_rate = (n_pf - parfinal_art.get('NONE', 0)) / n_pf if n_pf > 0 else 0
    npf_rate = (n_npf - notparfinal_art.get('NONE', 0)) / n_npf if n_npf > 0 else 0

    print(f"  Par-final tokens: {pf_rate:.4f} (N={n_pf})")
    print(f"  Non-par-final:    {npf_rate:.4f} (N={n_npf})")

    return {
        'header_art_rate': round(header_art_rate, 4),
        'body_art_rate': round(body_art_rate, 4),
        'header_body_ratio': round(header_art_rate / body_art_rate, 3) if body_art_rate > 0 else None,
        'par_final_rate': round(pf_rate, 4),
        'non_par_final_rate': round(npf_rate, 4),
        'n_header': n_header,
        'n_body': n_body,
    }


# ============================================================
# T9: ARTICULATOR combinatorial constraints
# ============================================================
def test_t9(tokens):
    """T9: ARTICULATOR combinations and constraints."""
    print("\n" + "=" * 70)
    print("T9: ARTICULATOR Combinatorial Constraints")
    print("=" * 70)

    # ART x PREFIX observed/expected
    art_pfx = defaultdict(Counter)
    art_totals = Counter()
    pfx_totals = Counter()
    n_total = 0
    for t in tokens:
        art = t['articulator'] or 'NONE'
        pfx = t['prefix'] or 'BARE'
        art_pfx[art][pfx] += 1
        art_totals[art] += 1
        pfx_totals[pfx] += 1
        n_total += 1

    # Find forbidden (observed=0 where expected>=5)
    forbidden_art_pfx = []
    enriched_art_pfx = []
    for art in sorted(art_totals.keys()):
        if art == 'NONE':
            continue
        for pfx in sorted(pfx_totals.keys()):
            expected = art_totals[art] * pfx_totals[pfx] / n_total
            observed = art_pfx[art].get(pfx, 0)
            if expected >= 5 and observed == 0:
                forbidden_art_pfx.append((art, pfx, expected))
            elif expected >= 5 and observed > 0:
                ratio = observed / expected
                if ratio >= 3.0 or ratio <= 0.33:
                    enriched_art_pfx.append((art, pfx, observed, expected, ratio))

    print(f"\nForbidden ART x PREFIX pairs (observed=0, expected>=5):")
    if forbidden_art_pfx:
        for art, pfx, exp in forbidden_art_pfx:
            print(f"  {art} x {pfx} (expected={exp:.1f})")
    else:
        print(f"  None found")

    print(f"\nExtreme enrichment/depletion (>=3x or <=0.33x, expected>=5):")
    enriched_art_pfx.sort(key=lambda x: -abs(x[4] - 1))
    for art, pfx, obs, exp, ratio in enriched_art_pfx[:20]:
        print(f"  {art} x {pfx}: obs={obs} exp={exp:.1f} ratio={ratio:.2f}")

    # ART x MIDDLE HEAD
    art_head = defaultdict(Counter)
    for t in tokens:
        if not t['head']:
            continue
        art = t['articulator'] or 'NONE'
        art_head[art][t['head']] += 1

    head_totals = Counter()
    for t in tokens:
        if t['head']:
            head_totals[t['head']] += 1

    forbidden_art_head = []
    for art in sorted(art_totals.keys()):
        if art == 'NONE':
            continue
        n_art_with_head = sum(art_head[art].values())
        if n_art_with_head < 10:
            continue
        n_with_head = sum(head_totals.values())
        for head in sorted(head_totals.keys()):
            expected = n_art_with_head * head_totals[head] / n_with_head if n_with_head > 0 else 0
            observed = art_head[art].get(head, 0)
            if expected >= 3 and observed == 0:
                forbidden_art_head.append((art, head, expected))

    print(f"\nForbidden ART x MIDDLE HEAD pairs (observed=0, expected>=3):")
    if forbidden_art_head:
        for art, head, exp in forbidden_art_head:
            print(f"  {art} x HEAD={head} (expected={exp:.1f})")
    else:
        print(f"  None found")

    return {
        'forbidden_art_prefix': [(a, p, round(e, 1)) for a, p, e in forbidden_art_pfx],
        'n_forbidden_art_prefix': len(forbidden_art_pfx),
        'n_extreme_enrichment': len(enriched_art_pfx),
        'forbidden_art_head': [(a, h, round(e, 1)) for a, h, e in forbidden_art_head],
        'n_forbidden_art_head': len(forbidden_art_head),
    }


# ============================================================
# T10: q-articulator deep dive
# ============================================================
def test_t10(tokens):
    """T10: q-articulator identity analysis."""
    print("\n" + "=" * 70)
    print("T10: q-Articulator Deep Dive")
    print("=" * 70)

    # The question: is 'q' in 'qo', 'qok', 'qot' an ARTICULATOR or part of PREFIX?
    # Under current morphology: qo is parsed as PREFIX=qo (not ART=q + PFX=o)
    # So q-as-articulator would be tokens where q appears BEFORE a recognized prefix
    # that is NOT already a qo-compound

    # Count tokens where morphology finds q as articulator
    q_art_tokens = [t for t in tokens if t['articulator'] == 'q']
    print(f"\nTokens with q as articulator: {len(q_art_tokens)}")

    # Actually, the ARTICULATORS list in voynich.py does NOT include 'q'!
    # Let me check: C291 says articulators are y, k, l, p, d, f, r, s, t
    # q is NOT in the articulator list - it's part of the qo prefix!
    print(f"  (Note: q is NOT in the canonical ARTICULATOR list per C291)")
    print(f"  q appears only as part of prefixes qo, qok, qot etc.")

    # Instead, compare qo-prefixed vs o-prefixed tokens
    qo_tokens = [t for t in tokens if t['prefix'] and t['prefix'].startswith('qo')]
    o_only_tokens = [t for t in tokens if t['prefix'] and t['prefix'] in ('ok', 'ot', 'ol', 'or') and not t['prefix'].startswith('qo')]

    print(f"\n  qo-prefixed tokens: {len(qo_tokens)}")
    print(f"  o-base (ok/ot/ol/or) tokens: {len(o_only_tokens)}")

    # Compare categories
    qo_cats = Counter(t['category'] for t in qo_tokens if t['category'])
    o_cats = Counter(t['category'] for t in o_only_tokens if t['category'])

    n_qo = sum(qo_cats.values())
    n_o = sum(o_cats.values())

    print(f"\nCategory comparison (qo-prefix vs o-base):")
    all_cats = sorted(set(list(qo_cats.keys()) + list(o_cats.keys())))
    for cat in all_cats:
        qo_frac = qo_cats.get(cat, 0) / n_qo if n_qo > 0 else 0
        o_frac = o_cats.get(cat, 0) / n_o if n_o > 0 else 0
        ratio = enrichment_ratio(qo_frac, o_frac)
        print(f"  {cat:15s}: qo={qo_frac:.3f} o={o_frac:.3f} ratio={ratio:.2f}")

    # Compare MIDDLE distributions
    qo_mids = Counter(t['middle'] for t in qo_tokens if t['middle'])
    o_mids = Counter(t['middle'] for t in o_only_tokens if t['middle'])

    shared_mids = set(qo_mids.keys()) & set(o_mids.keys())
    qo_only = set(qo_mids.keys()) - set(o_mids.keys())
    o_only = set(o_mids.keys()) - set(qo_mids.keys())

    print(f"\nMIDDLE vocabulary overlap:")
    print(f"  Shared: {len(shared_mids)}")
    print(f"  qo-only: {len(qo_only)}")
    print(f"  o-only: {len(o_only)}")
    print(f"  Jaccard: {len(shared_mids) / len(shared_mids | qo_only | o_only):.3f}"
          if (shared_mids | qo_only | o_only) else "  Jaccard: N/A")

    # Now the real articulators: y, k, d, s are the ones we should focus on
    # (l, p, f, r, t also in list but may be rare)
    print(f"\n\n--- Actual articulators (y, k, d, s, l, p, f, r, t) ---")
    real_arts = ['y', 'k', 'd', 's', 'l', 'p', 'f', 'r', 't']
    art_tokens = defaultdict(list)
    for t in tokens:
        if t['articulator'] in real_arts:
            art_tokens[t['articulator']].append(t)

    for art in real_arts:
        n = len(art_tokens[art])
        if n < 5:
            continue
        # Compare with non-articulated tokens having same prefix
        pfx_dist = Counter(t['prefix'] or 'BARE' for t in art_tokens[art])
        top_pfx = pfx_dist.most_common(3)
        cat_dist = Counter(t['category'] for t in art_tokens[art] if t['category'])
        top_cat = cat_dist.most_common(3)

        print(f"\n  {art}-articulator (N={n}):")
        print(f"    Top PREFIXes: {', '.join(f'{p}:{c}' for p,c in top_pfx)}")
        print(f"    Top categories: {', '.join(f'{c}:{n}' for c,n in top_cat)}")

        # Sample tokens
        sample = sorted(set(t['word'] for t in art_tokens[art]))[:10]
        print(f"    Samples: {', '.join(sample)}")

    return {
        'q_not_canonical_articulator': True,
        'qo_token_count': len(qo_tokens),
        'o_base_token_count': len(o_only_tokens),
        'articulator_counts': {art: len(art_tokens[art]) for art in real_arts},
    }


# ============================================================
# Main
# ============================================================
def main():
    print("Phase 517: ARTICULATOR Deep Dive")
    print("=" * 70)
    print("Loading data...")

    tokens = load_data()
    print(f"Loaded {len(tokens)} Currier B tokens")

    results = {}

    # Run all tests
    results['T1_inventory'] = test_t1(tokens)
    results['T2_prefix_selectivity'] = test_t2(tokens)
    results['T3_middle_selectivity'] = test_t3(tokens)
    results['T4_suffix_selectivity'] = test_t4(tokens)
    results['T5_category_selectivity'] = test_t5(tokens)
    results['T6_information_chain'] = test_t6(tokens)
    results['T7_line_position'] = test_t7(tokens)
    results['T8_paragraph_structure'] = test_t8(tokens)
    results['T9_combinatorial_constraints'] = test_t9(tokens)
    results['T10_q_deep_dive'] = test_t10(tokens)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nArticulator rate: {results['T1_inventory']['articulated_rate']:.1%} of B tokens")
    print(f"\nEffect sizes (Cramer's V):")
    print(f"  ART -> PREFIX:      {results['T2_prefix_selectivity']['cramers_v']:.4f}")
    print(f"  ART -> MIDDLE HEAD: {results['T3_middle_selectivity']['middle_head']['cramers_v']:.4f}")
    print(f"  ART -> MIDDLE TERM: {results['T3_middle_selectivity']['middle_term']['cramers_v']:.4f}")
    print(f"  ART -> SUFFIX:      {results['T4_suffix_selectivity']['suffix_identity']['cramers_v']:.4f}")
    print(f"  ART -> CATEGORY:    {results['T5_category_selectivity']['cramers_v']:.4f}")
    print(f"  ART -> POSITION:    {results['T7_line_position']['cramers_v_position']:.4f}")
    print(f"\nReference chain effect sizes:")
    print(f"  PREFIX -> MIDDLE:   {REF_PREFIX_MIDDLE_V:.4f}")
    print(f"  MIDDLE -> SUFFIX:   {REF_MIDDLE_SUFFIX_V:.4f}")
    print(f"  PREFIX -> SUFFIX:   {REF_PREFIX_SUFFIX_V:.4f}")
    print(f"\nInformation chain contributions:")
    print(f"  I(MIDDLE; ART | PREFIX): {results['T6_information_chain']['cmi_middle_art_given_prefix']:.4f} bits")
    print(f"  I(SUFFIX; ART | MIDDLE): {results['T6_information_chain']['cmi_suffix_art_given_middle']:.4f} bits")
    print(f"\nCombinatorial constraints:")
    print(f"  Forbidden ART x PREFIX: {results['T9_combinatorial_constraints']['n_forbidden_art_prefix']}")
    print(f"  Forbidden ART x HEAD:   {results['T9_combinatorial_constraints']['n_forbidden_art_head']}")

    # Save results
    output_path = RESULTS_DIR / 'articulator_deep_dive.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
