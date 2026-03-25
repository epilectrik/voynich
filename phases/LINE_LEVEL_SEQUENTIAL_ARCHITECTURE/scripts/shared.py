"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Shared utilities.

Provides corpus building, MI estimation, transfer entropy, and constants
for all phase scripts.
"""

import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any

import sys
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))
from scripts.voynich import (Transcript, Morphology, MiddleAnalyzer,
                              CategoryClassifier, decompose_middle_hmt)

# ============================================================
# Constants
# ============================================================

PROJECT_ROOT = _PROJECT_ROOT
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'LINE_LEVEL_SEQUENTIAL_ARCHITECTURE' / 'results'

ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

RNG = random.Random(42)
N_PERM = 500

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERM_SET = {'y', 'l', 'r', 'h', 'm', 'n'}

# Terminal opacity tiers (C1440)
LOCKED_TERMS = {'y', 'm', 'n'}      # Opacity = 1.0
CHANNELED_TERMS = {'l', 'h', 'r'}   # Opacity = 0.5
DIFFUSE_TERMS = {'k', 't'}          # Opacity = 0.0

# Atom correlation clusters (C1207)
ITERATION_ATOMS = {'a', 'i', 'n', 'r'}
MONITORING_ATOMS = {'c', 'h'}

# Suffix mode classification (C1229/C1341)
MODE_A_SUFFIXES = {'aiin', 'oiin', 'ey', 'eey'}  # Specification/energy
MODE_B_SUFFIXES = {'y', 'dy', 'l', 'r', 'm', 'n', 's', 'g'}  # Continuation/bare

# Quire mapping -- approximate from standard Voynich codicology
# (folio number prefix -> quire)
def _folio_to_quire(folio: str) -> int:
    """Approximate quire assignment from folio number."""
    import re
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 0
    num = int(m.group(1))
    # Standard quire boundaries (approximate, based on Voynich codicology)
    if num <= 8: return 1
    elif num <= 16: return 2
    elif num <= 24: return 3
    elif num <= 32: return 4
    elif num <= 40: return 5
    elif num <= 48: return 6
    elif num <= 56: return 7
    elif num <= 66: return 8
    elif num <= 73: return 9
    elif num <= 84: return 10
    elif num <= 86: return 11  # Rosettes
    elif num <= 90: return 12
    elif num <= 96: return 13
    elif num <= 102: return 14
    elif num <= 108: return 15
    elif num <= 116: return 16
    return 17


# ============================================================
# Data loading
# ============================================================

def _load_bridge_set() -> set:
    """Load the 85 bridge MIDDLEs from C1013."""
    path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path) as f:
        data = json.load(f)
    return set(data.get('bridge_middles', []))


def _load_dark_set() -> set:
    """Load the 300 dark-pipeline MIDDLEs from C1137/C1140."""
    path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(path) as f:
        data = json.load(f)
    return set(data.get('middles', []))


def _load_regime_map() -> Dict[str, str]:
    """Load folio -> REGIME mapping from authoritative source."""
    path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    with open(path) as f:
        data = json.load(f)
    assignments = data.get('regime_assignments', {})
    return {folio: info['regime'] for folio, info in assignments.items()}


# ============================================================
# Suffix mode / CTS helpers
# ============================================================

def suffix_mode(suffix: Optional[str]) -> str:
    """Classify suffix as Mode A or Mode B (C1229/C1341)."""
    if not suffix:
        return 'B'  # bare = Mode B
    if suffix in MODE_A_SUFFIXES:
        return 'A'
    return 'B'


def terminal_opacity(term_char: str) -> float:
    """Terminal opacity score: LOCKED=1.0, CHANNELED=0.5, DIFFUSE=0.0 (C1440)."""
    if term_char in LOCKED_TERMS:
        return 1.0
    elif term_char in CHANNELED_TERMS:
        return 0.5
    elif term_char in DIFFUSE_TERMS:
        return 0.0
    return 0.0  # bare or unknown


def terminal_opacity_tier(term_char: str) -> str:
    """Terminal opacity tier name."""
    if term_char in LOCKED_TERMS:
        return 'LOCKED'
    elif term_char in CHANNELED_TERMS:
        return 'CHANNELED'
    elif term_char in DIFFUSE_TERMS:
        return 'DIFFUSE'
    return 'BARE'


def cts_score(tokens: list) -> float:
    """Opacity-weighted CTS for a line's tokens (C1440 three-tier)."""
    if not tokens:
        return 0.0
    opacities = []
    for t in tokens:
        term = t.get('term', 'bare')
        if term and term != 'bare':
            opacities.append(terminal_opacity(term))
        else:
            opacities.append(0.0)
    return sum(opacities) / len(opacities) if opacities else 0.0


# ============================================================
# Corpus builder
# ============================================================

def build_corpus() -> Dict[str, Any]:
    """
    Build structured corpus of B paragraphs with full token decomposition.

    Returns dict: folio -> {section, regime, quire, paragraphs: [{id, header_lines, body_lines}]}
    Each line_dict has: folio, line, tokens (list of token dicts), length, cts.
    """
    tx = Transcript()
    morph = Morphology()
    ma = MiddleAnalyzer()
    ma.build_inventory('B')
    cc = CategoryClassifier()
    bridge_set = _load_bridge_set()
    dark_set = _load_dark_set()
    regime_map = _load_regime_map()

    # Group tokens by (folio, line) preserving order
    folio_line_tokens = defaultdict(lambda: defaultdict(list))
    folio_sections = {}

    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        if tok.is_label or tok.is_uncertain:
            continue
        if not tok.word.strip():
            continue

        m = morph.extract(tok.word)
        if not m.middle or ',' in m.middle or '?' in m.middle:
            continue
        if any(c in m.middle for c in 'jqz'):
            continue

        head, mods, term, frame = decompose_middle_hmt(m.middle)
        cat = cc.classify(m.middle)
        is_comp = ma.is_compound(m.middle)
        comp_depth = 0
        if is_comp:
            atoms = ma.get_maximal_atoms(m.middle)
            comp_depth = len(atoms) if atoms else 0

        # Kernel chars in MIDDLE
        kernels = [c for c in m.middle if c in ('k', 'h', 'e')]

        # Determine if HT (compound identification/specification tokens)
        # HT tokens use compound MIDDLEs that are folio-unique or have specific signatures
        # Simplified: tokens with is_compound and folio_unique classification
        is_ht = False
        try:
            mid_class = ma.classify_middle(m.middle)
            if mid_class == 'FOLIO_UNIQUE' and is_comp:
                is_ht = True
        except Exception:
            pass

        token_dict = {
            'word': tok.word,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': m.prefix or '',
            'middle': m.middle,
            'suffix': m.suffix or '',
            'articulator': m.articulator or '',
            'head': head or '',
            'mods': mods or '',
            'term': term or 'bare',
            'frame': frame or '',
            'category': cat or 'UNKNOWN',
            'kernels': kernels,
            'is_headless': head is None,
            'is_bridge': m.middle in bridge_set,
            'is_dark': m.middle in dark_set,
            'is_ht': is_ht,
            'is_compound': is_comp,
            'compound_depth': comp_depth,
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
            'suffix_mode': suffix_mode(m.suffix),
            'terminal_opacity': terminal_opacity_tier(term or 'bare'),
        }

        folio_line_tokens[tok.folio][tok.line].append(token_dict)
        folio_sections[tok.folio] = tok.section

    # Build paragraph structure
    corpus = {}
    for folio in sorted(folio_line_tokens.keys()):
        lines_dict = folio_line_tokens[folio]
        section = folio_sections.get(folio, '?')
        regime = regime_map.get(folio, 'UNKNOWN')
        quire = _folio_to_quire(folio)

        # Sort lines by numeric key
        sorted_lines = []
        for line_str in sorted(lines_dict.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            tokens = lines_dict[line_str]
            line_dict = {
                'folio': folio,
                'line': line_str,
                'tokens': tokens,
                'length': len(tokens),
                'cts': cts_score(tokens),
            }
            sorted_lines.append(line_dict)

        # Split into paragraphs using par_initial flag
        paragraphs = []
        current_para_lines = []
        para_count = 0

        for line_dict in sorted_lines:
            # Check if any token in this line is par_initial
            is_para_start = any(t['par_initial'] for t in line_dict['tokens'])
            if is_para_start and current_para_lines:
                # Finish previous paragraph
                para_count += 1
                header = [current_para_lines[0]] if current_para_lines else []
                body = current_para_lines[1:] if len(current_para_lines) > 1 else []
                paragraphs.append({
                    'id': f'P{para_count}',
                    'header_lines': header,
                    'body_lines': body,
                })
                current_para_lines = [line_dict]
            else:
                current_para_lines.append(line_dict)

        # Final paragraph
        if current_para_lines:
            para_count += 1
            header = [current_para_lines[0]] if current_para_lines else []
            body = current_para_lines[1:] if len(current_para_lines) > 1 else []
            paragraphs.append({
                'id': f'P{para_count}',
                'header_lines': header,
                'body_lines': body,
            })

        corpus[folio] = {
            'section': section,
            'regime': regime,
            'quire': quire,
            'paragraphs': paragraphs,
        }

    return corpus


# ============================================================
# MI / Transfer Entropy utilities
# ============================================================

def _discretize(values: List[float], n_bins: int = 5) -> List[int]:
    """Discretize continuous values into n_bins equal-frequency bins."""
    if not values:
        return []
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    boundaries = []
    for i in range(1, n_bins):
        idx = int(i * n / n_bins)
        boundaries.append(sorted_vals[min(idx, n - 1)])

    result = []
    for v in values:
        b = 0
        for boundary in boundaries:
            if v > boundary:
                b += 1
        result.append(min(b, n_bins - 1))
    return result


def compute_mi(x: List[float], y: List[float], n_bins: int = 5) -> float:
    """
    Compute mutual information I(X;Y) with Miller-Madow bias correction.

    Uses equal-frequency histogram binning.
    Returns MI in bits.
    """
    if len(x) != len(y) or len(x) < 10:
        return 0.0

    n = len(x)
    xd = _discretize(x, n_bins)
    yd = _discretize(y, n_bins)

    # Joint and marginal counts
    joint = Counter()
    mx = Counter()
    my = Counter()
    for xi, yi in zip(xd, yd):
        joint[(xi, yi)] += 1
        mx[xi] += 1
        my[yi] += 1

    # MI
    mi = 0.0
    for (xi, yi), nxy in joint.items():
        if nxy > 0:
            pxy = nxy / n
            px = mx[xi] / n
            py = my[yi] / n
            if px > 0 and py > 0:
                mi += pxy * math.log2(pxy / (px * py))

    # Miller-Madow bias correction
    k_joint = len([v for v in joint.values() if v > 0])
    correction = (k_joint - 1) / (2 * n * math.log(2))
    mi_corrected = max(0.0, mi - correction)

    return mi_corrected


def compute_binned_conditional_mi(x: List[float], y: List[float],
                                   condition: List[float],
                                   n_bins: int = 5,
                                   cond_bins: int = 4) -> float:
    """
    Compute MI(X;Y | C) by binning condition into cond_bins quartiles,
    computing MI within each bin, and taking weighted average.
    """
    if len(x) != len(y) or len(x) != len(condition) or len(x) < 20:
        return 0.0

    n = len(x)
    cd = _discretize(condition, cond_bins)

    # Group by condition bin
    groups = defaultdict(lambda: ([], []))
    for i in range(n):
        groups[cd[i]][0].append(x[i])
        groups[cd[i]][1].append(y[i])

    # Weighted average MI
    total_mi = 0.0
    for bin_id, (xg, yg) in groups.items():
        w = len(xg) / n
        mi = compute_mi(xg, yg, n_bins)
        total_mi += w * mi

    return total_mi


def compute_transfer_entropy(source: List[float], target: List[float],
                              n_bins: int = 5) -> float:
    """
    Compute transfer entropy TE(source -> target).

    TE(X->Y) = I(Y_{t+1}; X_t | Y_t)
             = H(Y_{t+1} | Y_t) - H(Y_{t+1} | Y_t, X_t)

    Approximated via discretization.
    Returns TE in bits.
    """
    if len(source) != len(target) or len(source) < 15:
        return 0.0

    n = len(source) - 1  # pairs
    sd = _discretize(source[:n], n_bins)
    td = _discretize(target[:n], n_bins)
    td1 = _discretize(target[1:n + 1], n_bins)

    # H(Y_{t+1} | Y_t) - need joint P(Y_{t+1}, Y_t) and P(Y_t)
    joint_yt_yt1 = Counter()
    count_yt = Counter()
    for i in range(n):
        joint_yt_yt1[(td[i], td1[i])] += 1
        count_yt[td[i]] += 1

    h_yt1_given_yt = 0.0
    for (yt, yt1), cnt in joint_yt_yt1.items():
        p_joint = cnt / n
        p_yt = count_yt[yt] / n
        if p_yt > 0 and p_joint > 0:
            h_yt1_given_yt -= p_joint * math.log2(p_joint / p_yt)

    # H(Y_{t+1} | Y_t, X_t)
    joint_triple = Counter()
    count_yt_xt = Counter()
    for i in range(n):
        joint_triple[(td[i], sd[i], td1[i])] += 1
        count_yt_xt[(td[i], sd[i])] += 1

    h_yt1_given_yt_xt = 0.0
    for (yt, xt, yt1), cnt in joint_triple.items():
        p_triple = cnt / n
        p_pair = count_yt_xt[(yt, xt)] / n
        if p_pair > 0 and p_triple > 0:
            h_yt1_given_yt_xt -= p_triple * math.log2(p_triple / p_pair)

    te = max(0.0, h_yt1_given_yt - h_yt1_given_yt_xt)
    return te


def permutation_test_mi(x: List[float], y: List[float],
                         n_perm: int = N_PERM, n_bins: int = 5,
                         rng: random.Random = None) -> Dict[str, float]:
    """
    Permutation test for MI significance.

    Shuffles y within groups (if provided) n_perm times.
    Returns observed MI, null mean/std, z-score, p-value.
    """
    if rng is None:
        rng = RNG

    observed = compute_mi(x, y, n_bins)

    null_values = []
    y_copy = list(y)
    for _ in range(n_perm):
        rng.shuffle(y_copy)
        null_mi = compute_mi(x, y_copy, n_bins)
        null_values.append(null_mi)

    null_mean = sum(null_values) / len(null_values)
    null_std = (sum((v - null_mean) ** 2 for v in null_values) / len(null_values)) ** 0.5

    z_score = (observed - null_mean) / null_std if null_std > 0 else 0.0
    p_value = sum(1 for v in null_values if v >= observed) / len(null_values)

    return {
        'observed': round(observed, 6),
        'null_mean': round(null_mean, 6),
        'null_std': round(null_std, 6),
        'z_score': round(z_score, 3),
        'p_value': round(p_value, 6),
    }


# ============================================================
# Line feature extraction
# ============================================================

def extract_line_features(line_dict: dict, folio_prefix_dist: Optional[Dict[str, float]] = None) -> dict:
    """
    Extract the 18 channel features from a line_dict.

    Returns dict with channel names -> scalar values.
    """
    tokens = line_dict['tokens']
    n = len(tokens)
    if n == 0:
        return {}

    # Channel 1: Line length
    length = n

    # Count atoms across all tokens
    all_atoms = []
    for t in tokens:
        for c in t['middle']:
            all_atoms.append(c)

    atom_counts = Counter(all_atoms)
    total_atoms = sum(atom_counts.values()) or 1

    # Kernel fractions
    k_count = sum(1 for t in tokens for c in t['kernels'] if c == 'k')
    h_count = sum(1 for t in tokens for c in t['kernels'] if c == 'h')
    e_count = sum(1 for t in tokens for c in t['kernels'] if c == 'e')
    khe_total = k_count + h_count + e_count
    k_frac = k_count / khe_total if khe_total > 0 else 0.0
    h_frac = h_count / khe_total if khe_total > 0 else 0.0
    e_frac = e_count / khe_total if khe_total > 0 else 0.0

    # Suffix mode proportion (fraction Mode A)
    mode_a_count = sum(1 for t in tokens if t['suffix_mode'] == 'A')
    suffix_mode_prop = mode_a_count / n

    # PREFIX JSD from folio mean
    prefix_jsd = 0.0
    if folio_prefix_dist:
        line_prefix_counts = Counter(t['prefix'] for t in tokens if t['prefix'])
        line_total = sum(line_prefix_counts.values()) or 1
        line_dist = {p: c / line_total for p, c in line_prefix_counts.items()}
        all_pfx = set(list(folio_prefix_dist.keys()) + list(line_dist.keys()))
        for pfx in all_pfx:
            p = line_dist.get(pfx, 0.0)
            q = folio_prefix_dist.get(pfx, 0.0)
            m_val = (p + q) / 2
            if p > 0 and m_val > 0:
                prefix_jsd += 0.5 * p * math.log2(p / m_val)
            if q > 0 and m_val > 0:
                prefix_jsd += 0.5 * q * math.log2(q / m_val)

    # Headless rate
    headless_count = sum(1 for t in tokens if t['is_headless'])
    headless_rate = headless_count / n

    # Modifier density
    mod_density = sum(len(t['mods']) for t in tokens) / n

    # m-terminal rate
    m_term_count = sum(1 for t in tokens if t['term'] == 'm')
    m_term_rate = m_term_count / n

    # Dark pipeline fraction
    dark_count = sum(1 for t in tokens if t['is_dark'])
    dark_frac = dark_count / n

    # HT density
    ht_count = sum(1 for t in tokens if t['is_ht'])
    ht_density = ht_count / n

    # Category entropy
    cat_counts = Counter(t['category'] for t in tokens)
    cat_total = sum(cat_counts.values()) or 1
    cat_entropy = 0.0
    for c in cat_counts.values():
        p = c / cat_total
        if p > 0:
            cat_entropy -= p * math.log2(p)

    # ITERATION cluster fraction ({a,i,n,r} / total atoms)
    iter_count = sum(atom_counts.get(a, 0) for a in ITERATION_ATOMS)
    iter_frac = iter_count / total_atoms

    # MONITORING cluster fraction ({c,h} / total atoms)
    mon_count = sum(atom_counts.get(a, 0) for a in MONITORING_ATOMS)
    mon_frac = mon_count / total_atoms

    # Bridge token fraction
    bridge_count = sum(1 for t in tokens if t['is_bridge'])
    bridge_frac = bridge_count / n

    # ARTICULATOR rate
    artic_count = sum(1 for t in tokens if t['articulator'])
    artic_rate = artic_count / n

    # ey-fraction (preventive safety: tokens with e-HEAD and y-TERM)
    ey_count = sum(1 for t in tokens if t['head'] == 'e' and t['term'] == 'y')
    ey_frac = ey_count / n

    # ii-fraction (transformative safety: tokens with 2+ 'i' in mods)
    ii_count = sum(1 for t in tokens if t['mods'].count('i') >= 2)
    ii_frac = ii_count / n

    return {
        'length': length,
        'suffix_mode_prop': suffix_mode_prop,
        'prefix_jsd': prefix_jsd,
        'k_frac': k_frac,
        'h_frac': h_frac,
        'e_frac': e_frac,
        'headless_rate': headless_rate,
        'mod_density': mod_density,
        'm_term_rate': m_term_rate,
        'dark_frac': dark_frac,
        'ht_density': ht_density,
        'cat_entropy': cat_entropy,
        'iter_frac': iter_frac,
        'mon_frac': mon_frac,
        'bridge_frac': bridge_frac,
        'artic_rate': artic_rate,
        'ey_frac': ey_frac,
        'ii_frac': ii_frac,
    }


CHANNEL_NAMES = [
    'length', 'suffix_mode_prop', 'prefix_jsd',
    'k_frac', 'h_frac', 'e_frac',
    'headless_rate', 'mod_density', 'm_term_rate',
    'dark_frac', 'ht_density', 'cat_entropy',
    'iter_frac', 'mon_frac', 'bridge_frac',
    'artic_rate', 'ey_frac', 'ii_frac',
]


# ============================================================
# Folio-level PREFIX distribution (for JSD computation)
# ============================================================

def compute_folio_prefix_dists(corpus: dict) -> Dict[str, Dict[str, float]]:
    """Compute per-folio PREFIX frequency distributions."""
    folio_dists = {}
    for folio, fdata in corpus.items():
        pfx_counts = Counter()
        total = 0
        for para in fdata['paragraphs']:
            for line in para['header_lines'] + para['body_lines']:
                for t in line['tokens']:
                    if t['prefix']:
                        pfx_counts[t['prefix']] += 1
                        total += 1
        if total > 0:
            folio_dists[folio] = {p: c / total for p, c in pfx_counts.items()}
        else:
            folio_dists[folio] = {}
    return folio_dists


# ============================================================
# Utility: round floats in nested structure for JSON
# ============================================================

def round_floats(obj, digits=6):
    """Recursively round floats in a nested dict/list structure."""
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [round_floats(v, digits) for v in obj]
    return obj
