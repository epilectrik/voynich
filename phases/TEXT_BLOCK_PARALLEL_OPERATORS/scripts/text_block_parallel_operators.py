#!/usr/bin/env python3
"""
Phase 462: TEXT_BLOCK_PARALLEL_OPERATORS
========================================
Tests whether visual text blocks on Currier B folios group complementary
parallel operators — paragraphs that share the same thermal envelope but
specialize in different operational aspects.

Hypothesis: Within-block paragraphs converge on kernel/category context
(same fire regime) but diverge on PREFIX profiles (different jobs within
that context). Like different stations in the same distillation setup.

7-test battery:
  T1: Block census validation
  T2: Thermal envelope convergence (within-block kernel similarity)
  T3: PREFIX profile divergence (within-block specialization)
  T4: Category envelope convergence (shared operational domain)
  T5: Operational coverage (block completeness / division of labor)
  T6: Block-initial paragraph enrichment
  T7: Section-specific block architecture
"""

import csv
import json
import math
import random
import sys
from collections import defaultdict, OrderedDict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier, BFolioDecoder

SEED = 42
N_PERM = 1_000
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
TRANSCRIPT_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

GALLOWS = {'k', 't', 'p', 'f'}
CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

# ============================================================
# Statistical utilities (pure Python, no scipy)
# ============================================================

def cosine_sim(a, b):
    """Cosine similarity between two vectors (lists/tuples)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    eps = 1e-12
    m = [(pi + qi) / 2.0 + eps for pi, qi in zip(p, q)]
    kl_pm = sum((pi + eps) * math.log((pi + eps) / mi) for pi, mi in zip(p, m) if pi > 0)
    kl_qm = sum((qi + eps) * math.log((qi + eps) / mi) for qi, mi in zip(q, m) if qi > 0)
    return (kl_pm + kl_qm) / 2.0


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


def normalize_profile(counts, keys=None):
    """Normalize a count dict to a probability vector."""
    if keys is None:
        keys = sorted(counts.keys())
    total = sum(counts.get(k, 0) for k in keys)
    if total == 0:
        return [0.0] * len(keys)
    return [counts.get(k, 0) / total for k in keys]


def mann_whitney_u(x, y):
    """Mann-Whitney U test with normal approximation. Returns (U, z, p_two_tail)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0, 0.0, 1.0
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            if k not in ranks:
                ranks[k] = []
            ranks[k] = avg_rank
        i = j
    r_x = sum(ranks[i] for i in range(len(combined)) if combined[i][1] == 'x')
    U = r_x - nx * (nx + 1) / 2.0
    mu = nx * ny / 2.0
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return U, 0.0, 1.0
    z = (U - mu) / sigma
    p = 2.0 * normal_cdf(-abs(z))
    return U, z, p


def kruskal_wallis(groups):
    """Kruskal-Wallis H test. Returns (H, p)."""
    all_vals = []
    for i, g in enumerate(groups):
        for v in g:
            all_vals.append((v, i))
    all_vals.sort(key=lambda t: t[0])
    N = len(all_vals)
    if N < 2:
        return 0.0, 1.0
    rank_sums = defaultdict(float)
    group_ns = defaultdict(int)
    i = 0
    while i < N:
        j = i
        while j < N and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            gid = all_vals[k][1]
            rank_sums[gid] += avg_rank
            group_ns[gid] += 1
        i = j
    H = (12.0 / (N * (N + 1))) * sum(
        rank_sums[g] ** 2 / group_ns[g] for g in rank_sums
    ) - 3 * (N + 1)
    df = len(groups) - 1
    p = chi2_sf(H, df)
    return H, p


def chi2_sf(x, k):
    """Survival function for chi-squared distribution (Wilson-Hilferty approx)."""
    if k <= 0 or x <= 0:
        return 1.0
    z = ((x / k) ** (1.0 / 3.0) - (1 - 2.0 / (9.0 * k))) / math.sqrt(2.0 / (9.0 * k))
    return 1.0 - normal_cdf(z)


def normal_cdf(z):
    """Standard normal CDF (Abramowitz-Stegun approximation)."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p_const = 0.3275911
    sign = 1 if z >= 0 else -1
    z_abs = abs(z)
    t = 1.0 / (1.0 + p_const * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def permutation_p(observed, null_dist, alternative='greater'):
    """Permutation p-value."""
    n = len(null_dist)
    if n == 0:
        return 1.0
    if alternative == 'greater':
        return sum(1 for x in null_dist if x >= observed) / n
    else:
        return sum(1 for x in null_dist if x <= observed) / n


# ============================================================
# Block detection (from _tmp_block_census.py)
# ============================================================

def strip_quotes(s):
    return s.strip().strip('"')


def is_gallows_initial(word):
    if not word:
        return False
    w = word.lower()
    if w.startswith('y') and len(w) > 1:
        return w[1] in GALLOWS
    return w[0] in GALLOWS


def load_raw_tokens():
    """Load raw transcript tokens with par_initial integer values."""
    tokens = []
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if strip_quotes(row.get('transcriber', '')) != 'H':
                continue
            if strip_quotes(row.get('language', '')) != 'B':
                continue
            placement = strip_quotes(row.get('placement', ''))
            if placement.startswith('L'):
                continue
            word = strip_quotes(row.get('word', ''))
            if '*' in word or not word.strip():
                continue
            pi_raw = strip_quotes(row.get('par_initial', ''))
            tokens.append({
                'word': word,
                'folio': strip_quotes(row.get('folio', '')),
                'line': strip_quotes(row.get('line_number', '')),
                'section': strip_quotes(row.get('section', '')),
                'line_initial': strip_quotes(row.get('line_initial', '')) == '1',
                'par_initial_raw': pi_raw,
            })
    return tokens


def detect_blocks(folio_tokens):
    """Detect visual text block boundaries by par_initial counter resets.
    Returns list of block dicts with first_line, last_line, line_numbers."""
    lines = OrderedDict()
    for tok in folio_tokens:
        lk = tok['line']
        if lk not in lines:
            lines[lk] = {'tokens': [], 'first_pi': None}
        lines[lk]['tokens'].append(tok)
        if tok['line_initial'] and tok['par_initial_raw'] not in ('NA', ''):
            try:
                lines[lk]['first_pi'] = int(tok['par_initial_raw'])
            except ValueError:
                pass

    line_list = list(lines.items())
    blocks = []
    current = []
    prev_pi = None
    for line_num, ld in line_list:
        pi = ld['first_pi']
        if prev_pi is not None and pi is not None and pi < prev_pi:
            if current:
                blocks.append(current)
            current = []
        current.append(line_num)
        if pi is not None:
            prev_pi = pi
    if current:
        blocks.append(current)

    return [{'line_numbers': b, 'first_line': b[0], 'last_line': b[-1]}
            for b in blocks]


# ============================================================
# Data loading and assembly
# ============================================================

def load_data():
    """Load all data: raw tokens for block detection + BFolioDecoder for paragraph analysis."""
    print("Loading raw transcript for block detection...")
    raw = load_raw_tokens()
    n_b = len(raw)
    print(f"  {n_b} B text tokens loaded")
    assert 22500 < n_b < 24000, f"Unexpected B token count: {n_b}"

    # Group raw tokens by folio
    folio_raw = OrderedDict()
    folio_sections = {}
    for tok in raw:
        f = tok['folio']
        if f not in folio_raw:
            folio_raw[f] = []
            folio_sections[f] = tok['section']
        folio_raw[f].append(tok)

    # Detect blocks per folio
    print("Detecting visual text blocks...")
    folio_blocks = {}
    for folio, toks in folio_raw.items():
        folio_blocks[folio] = detect_blocks(toks)

    # Build paragraph analyses using BFolioDecoder
    print("Analyzing paragraphs with BFolioDecoder...")
    decoder = BFolioDecoder()
    morph = Morphology()

    folio_data = {}
    for folio in folio_raw:
        try:
            paras = decoder.analyze_folio_paragraphs(folio)
        except Exception as e:
            print(f"  Warning: {folio} skipped ({e})")
            continue

        blocks = folio_blocks[folio]

        # Map paragraphs to blocks by line number overlap
        block_para_map = []
        for blk in blocks:
            block_line_set = set(str(ln) for ln in blk['line_numbers'])
            matching_paras = []
            for p in paras:
                para_lines = set(str(la.line_id) for la in p.lines)
                if para_lines & block_line_set:
                    matching_paras.append(p)
            block_para_map.append(matching_paras)

        folio_data[folio] = {
            'folio': folio,
            'section': folio_sections[folio],
            'blocks': blocks,
            'block_paras': block_para_map,
            'all_paras': paras,
        }

    print(f"  {len(folio_data)} folios analyzed")
    return folio_data


# ============================================================
# Per-paragraph metric extraction
# ============================================================

def para_kernel_vec(para):
    """Extract normalized [k, h, e] kernel vector from paragraph."""
    kd = para.kernel_dist if para.kernel_dist else {}
    total = sum(kd.values())
    if total == 0:
        return [0.0, 0.0, 0.0]
    return [kd.get('k', 0) / total, kd.get('h', 0) / total, kd.get('e', 0) / total]


def para_prefix_vec(para, prefix_keys, morph):
    """Extract normalized PREFIX frequency vector from paragraph."""
    prefix_counts = Counter()
    for la in para.lines:
        for tok in la.tokens:
            m = morph.extract(tok.word)
            if m.prefix:
                prefix_counts[m.prefix] += 1
    return normalize_profile(prefix_counts, prefix_keys)


def para_category_set(para, threshold=0.05):
    """Get set of categories with >= threshold fraction."""
    cp = para.category_profile if para.category_profile else {}
    total = sum(cp.values())
    if total == 0:
        return set()
    return {cat for cat in CATEGORIES if cp.get(cat, 0) / total >= threshold}


def para_ht_density(para):
    """Fraction of tokens that are HT."""
    total = 0
    ht = 0
    for la in para.lines:
        for tok in la.tokens:
            total += 1
            if tok.is_ht:
                ht += 1
    return ht / total if total > 0 else 0.0


def para_marking_rate(para):
    """MARKING category fraction."""
    cp = para.category_profile if para.category_profile else {}
    total = sum(cp.values())
    if total == 0:
        return 0.0
    return cp.get('MARKING', 0) / total


# ============================================================
# Pre-computation for permutation tests
# ============================================================

def precompute_pairwise(folio_data):
    """Pre-compute per-paragraph metrics and NxN pairwise matrices for all folios.

    This is the key optimization: metrics are computed ONCE, then permutation
    tests only shuffle indices and do O(1) matrix lookups instead of recomputing
    cosine/JSD/Jaccard on every iteration.
    """
    print("Pre-computing pairwise matrices...")
    morph = Morphology()

    # Collect all prefixes for shared key set
    all_prefixes = set()
    for fd in folio_data.values():
        for p in fd['all_paras']:
            for la in p.lines:
                for tok in la.tokens:
                    m = morph.extract(tok.word)
                    if m.prefix:
                        all_prefixes.add(m.prefix)
    prefix_keys = sorted(all_prefixes)

    for folio, fd in folio_data.items():
        paras = fd['all_paras']
        n = len(paras)

        # Per-paragraph metrics (computed once)
        kern_vecs = [para_kernel_vec(p) for p in paras]
        pfx_vecs = [para_prefix_vec(p, prefix_keys, morph) for p in paras]
        cat_sets_list = [para_category_set(p) for p in paras]

        # Validity flags
        kern_valid = [sum(v) > 0 for v in kern_vecs]
        pfx_valid = [sum(v) > 0 for v in pfx_vecs]

        # NxN pairwise matrices (symmetric)
        kern_mat = [[None] * n for _ in range(n)]
        pfx_mat = [[None] * n for _ in range(n)]
        cat_mat = [[None] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                if kern_valid[i] and kern_valid[j]:
                    v = cosine_sim(kern_vecs[i], kern_vecs[j])
                    kern_mat[i][j] = v
                    kern_mat[j][i] = v
                if pfx_valid[i] and pfx_valid[j]:
                    v = jsd(pfx_vecs[i], pfx_vecs[j])
                    pfx_mat[i][j] = v
                    pfx_mat[j][i] = v
                if cat_sets_list[i] or cat_sets_list[j]:
                    v = jaccard(cat_sets_list[i], cat_sets_list[j])
                    cat_mat[i][j] = v
                    cat_mat[j][i] = v

        # Block indices (map paragraph objects to indices in paras list)
        pid_to_idx = {p.paragraph_id: i for i, p in enumerate(paras)}
        block_indices = []
        for bp_list in fd['block_paras']:
            idxs = [pid_to_idx[p.paragraph_id] for p in bp_list
                    if p.paragraph_id in pid_to_idx]
            block_indices.append(idxs)

        # Store pre-computed data
        fd['_n'] = n
        fd['_kern_mat'] = kern_mat
        fd['_pfx_mat'] = pfx_mat
        fd['_cat_mat'] = cat_mat
        fd['_cat_sets'] = cat_sets_list
        fd['_block_indices'] = block_indices
        fd['_block_sizes'] = [len(bi) for bi in block_indices]

    print(f"  Done. {len(folio_data)} folios, {len(prefix_keys)} prefix keys")
    return prefix_keys


def _collect_within_between(block_indices, matrix):
    """Collect within-block and between-block values from a pairwise matrix."""
    within = []
    between = []
    for blk in block_indices:
        for a in range(len(blk)):
            for b in range(a + 1, len(blk)):
                v = matrix[blk[a]][blk[b]]
                if v is not None:
                    within.append(v)
    for bi in range(len(block_indices)):
        for bj in range(bi + 1, len(block_indices)):
            for a in block_indices[bi]:
                for b in block_indices[bj]:
                    v = matrix[a][b]
                    if v is not None:
                        between.append(v)
    return within, between


def _perm_within_between_diff(n, matrix, block_sizes, rng):
    """One permutation: shuffle paragraphs into fake blocks, return mean(within) - mean(between)."""
    indices = list(range(n))
    rng.shuffle(indices)
    fake_blocks = []
    idx = 0
    for sz in block_sizes:
        fake_blocks.append(indices[idx:idx + sz])
        idx += sz
    w, b = _collect_within_between(fake_blocks, matrix)
    if w and b:
        return sum(w) / len(w) - sum(b) / len(b)
    return None


# ============================================================
# Test functions
# ============================================================

def test_t1(folio_data):
    """T1: Block Census Validation."""
    print("\n=== T1: Block Census Validation ===")

    total_folios = len(folio_data)
    multi_block = sum(1 for fd in folio_data.values() if len(fd['blocks']) > 1)
    total_blocks = sum(len(fd['blocks']) for fd in folio_data.values())

    section_stats = defaultdict(lambda: {'folios': 0, 'multi': 0, 'blocks': []})
    for fd in folio_data.values():
        s = fd['section']
        nb = len(fd['blocks'])
        section_stats[s]['folios'] += 1
        section_stats[s]['blocks'].append(nb)
        if nb > 1:
            section_stats[s]['multi'] += 1

    section_summary = {}
    for sec, st in sorted(section_stats.items()):
        section_summary[sec] = {
            'folios': st['folios'],
            'multi_block': st['multi'],
            'pct_multi': round(100 * st['multi'] / st['folios'], 1) if st['folios'] > 0 else 0,
            'avg_blocks': round(sum(st['blocks']) / len(st['blocks']), 2),
            'min_blocks': min(st['blocks']),
            'max_blocks': max(st['blocks']),
        }
        print(f"  {sec}: {st['folios']} folios, {st['multi']} multi-block "
              f"({section_summary[sec]['pct_multi']}%), avg {section_summary[sec]['avg_blocks']} blocks")

    multi_pct = 100 * multi_block / total_folios
    passed = multi_pct >= 80.0
    print(f"  Total: {total_folios} folios, {multi_block} multi-block ({multi_pct:.1f}%)")
    print(f"  Total blocks: {total_blocks}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T1: Block Census Validation',
        'tier': 'T2 (structural)',
        'passed': passed,
        'total_folios': total_folios,
        'multi_block_folios': multi_block,
        'multi_block_pct': round(multi_pct, 1),
        'total_blocks': total_blocks,
        'section_summary': section_summary,
    }


def test_t2(folio_data, rng):
    """T2: Thermal Envelope Convergence — within-block kernel similarity > between-block."""
    print("\n=== T2: Thermal Envelope Convergence ===")

    within_sims = []
    between_sims = []
    perm_folios = []

    for fd in folio_data.values():
        n = fd['_n']
        bi = fd['_block_indices']
        if n < 3 or len(bi) < 2:
            continue
        mat = fd['_kern_mat']
        w, b = _collect_within_between(bi, mat)
        within_sims.extend(w)
        between_sims.extend(b)
        perm_folios.append((n, mat, fd['_block_sizes']))

    if not within_sims or not between_sims:
        print("  Insufficient data")
        return {'test': 'T2: Thermal Envelope Convergence', 'passed': False,
                'reason': 'insufficient data'}

    within_mean = sum(within_sims) / len(within_sims)
    between_mean = sum(between_sims) / len(between_sims)
    observed_diff = within_mean - between_mean

    U, z, p_mw = mann_whitney_u(within_sims, between_sims)

    # Permutation control: shuffle paragraph-to-block assignments
    null_diffs = []
    for _ in range(N_PERM):
        w_all, b_all = [], []
        for n, mat, sizes in perm_folios:
            indices = list(range(n))
            rng.shuffle(indices)
            fake_blocks = []
            idx = 0
            for sz in sizes:
                fake_blocks.append(indices[idx:idx + sz])
                idx += sz
            w, b = _collect_within_between(fake_blocks, mat)
            w_all.extend(w)
            b_all.extend(b)
        if w_all and b_all:
            null_diffs.append(sum(w_all) / len(w_all) - sum(b_all) / len(b_all))

    perm_p = permutation_p(observed_diff, null_diffs, 'greater')

    passed = within_mean > between_mean and perm_p < 0.01
    print(f"  Within-block kernel cosine: {within_mean:.4f} (n={len(within_sims)})")
    print(f"  Between-block kernel cosine: {between_mean:.4f} (n={len(between_sims)})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.4f}")
    print(f"  Permutation p: {perm_p:.4f}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T2: Thermal Envelope Convergence',
        'tier': 'T2 (structural)',
        'passed': passed,
        'within_mean': round(within_mean, 4),
        'between_mean': round(between_mean, 4),
        'diff': round(observed_diff, 4),
        'n_within': len(within_sims),
        'n_between': len(between_sims),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
    }


def test_t3(folio_data, rng):
    """T3: PREFIX Profile Divergence — within-block PREFIX JSD > between-block."""
    print("\n=== T3: PREFIX Profile Divergence (Complementarity) ===")

    within_jsds = []
    between_jsds = []
    perm_folios = []

    for fd in folio_data.values():
        n = fd['_n']
        bi = fd['_block_indices']
        if n < 3 or len(bi) < 2:
            continue
        mat = fd['_pfx_mat']
        w, b = _collect_within_between(bi, mat)
        within_jsds.extend(w)
        between_jsds.extend(b)
        perm_folios.append((n, mat, fd['_block_sizes']))

    if not within_jsds or not between_jsds:
        print("  Insufficient data")
        return {'test': 'T3: PREFIX Profile Divergence', 'passed': False,
                'reason': 'insufficient data'}

    within_mean = sum(within_jsds) / len(within_jsds)
    between_mean = sum(between_jsds) / len(between_jsds)
    observed_diff = within_mean - between_mean

    U, z, p_mw = mann_whitney_u(within_jsds, between_jsds)

    # Permutation control
    null_diffs = []
    for _ in range(N_PERM):
        w_all, b_all = [], []
        for n, mat, sizes in perm_folios:
            indices = list(range(n))
            rng.shuffle(indices)
            fake_blocks = []
            idx = 0
            for sz in sizes:
                fake_blocks.append(indices[idx:idx + sz])
                idx += sz
            w, b = _collect_within_between(fake_blocks, mat)
            w_all.extend(w)
            b_all.extend(b)
        if w_all and b_all:
            null_diffs.append(sum(w_all) / len(w_all) - sum(b_all) / len(b_all))

    perm_p = permutation_p(observed_diff, null_diffs, 'greater')

    passed = within_mean > between_mean and perm_p < 0.01
    print(f"  Within-block PREFIX JSD: {within_mean:.4f} (n={len(within_jsds)})")
    print(f"  Between-block PREFIX JSD: {between_mean:.4f} (n={len(between_jsds)})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.4f}")
    print(f"  Permutation p: {perm_p:.4f}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T3: PREFIX Profile Divergence',
        'tier': 'T2 (structural)',
        'passed': passed,
        'within_mean': round(within_mean, 4),
        'between_mean': round(between_mean, 4),
        'diff': round(observed_diff, 4),
        'n_within': len(within_jsds),
        'n_between': len(between_jsds),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
    }


def test_t4(folio_data, rng):
    """T4: Category Envelope Convergence — within-block category key overlap > between-block."""
    print("\n=== T4: Category Envelope Convergence ===")

    within_overlaps = []
    between_overlaps = []
    perm_folios = []

    for fd in folio_data.values():
        n = fd['_n']
        bi = fd['_block_indices']
        if n < 3 or len(bi) < 2:
            continue
        mat = fd['_cat_mat']
        w, b = _collect_within_between(bi, mat)
        within_overlaps.extend(w)
        between_overlaps.extend(b)
        perm_folios.append((n, mat, fd['_block_sizes']))

    if not within_overlaps or not between_overlaps:
        print("  Insufficient data")
        return {'test': 'T4: Category Envelope Convergence', 'passed': False,
                'reason': 'insufficient data'}

    within_mean = sum(within_overlaps) / len(within_overlaps)
    between_mean = sum(between_overlaps) / len(between_overlaps)
    observed_diff = within_mean - between_mean

    U, z, p_mw = mann_whitney_u(within_overlaps, between_overlaps)

    # Permutation control
    null_diffs = []
    for _ in range(N_PERM):
        w_all, b_all = [], []
        for n, mat, sizes in perm_folios:
            indices = list(range(n))
            rng.shuffle(indices)
            fake_blocks = []
            idx = 0
            for sz in sizes:
                fake_blocks.append(indices[idx:idx + sz])
                idx += sz
            w, b = _collect_within_between(fake_blocks, mat)
            w_all.extend(w)
            b_all.extend(b)
        if w_all and b_all:
            null_diffs.append(sum(w_all) / len(w_all) - sum(b_all) / len(b_all))

    perm_p = permutation_p(observed_diff, null_diffs, 'greater')

    passed = within_mean > between_mean and perm_p < 0.01
    print(f"  Within-block category overlap: {within_mean:.4f} (n={len(within_overlaps)})")
    print(f"  Between-block category overlap: {between_mean:.4f} (n={len(between_overlaps)})")
    print(f"  Diff: {observed_diff:.4f}, MW z={z:.2f} p={p_mw:.4f}")
    print(f"  Permutation p: {perm_p:.4f}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T4: Category Envelope Convergence',
        'tier': 'T2 (structural)',
        'passed': passed,
        'within_mean': round(within_mean, 4),
        'between_mean': round(between_mean, 4),
        'diff': round(observed_diff, 4),
        'n_within': len(within_overlaps),
        'n_between': len(between_overlaps),
        'mw_z': round(z, 3),
        'mw_p': round(p_mw, 6),
        'perm_p': round(perm_p, 4),
    }


def test_t5(folio_data, rng):
    """T5: Operational Coverage — blocks cover more categories than individual paragraphs."""
    print("\n=== T5: Operational Coverage (Division of Labor) ===")

    # Pre-compute category sets per folio (already in fd['_cat_sets'])
    observed_ratios = []
    perm_folios = []  # (cat_sets_list, block_sizes_with_multis)

    for fd in folio_data.values():
        cat_sets = fd['_cat_sets']
        bi = fd['_block_indices']
        multi_block_sizes = []

        for blk_idxs in bi:
            if len(blk_idxs) < 2:
                continue
            para_coverages = []
            union_cats = set()
            for idx in blk_idxs:
                cs = cat_sets[idx]
                para_coverages.append(len(cs))
                union_cats |= cs
            block_cov = len(union_cats)
            mean_para_cov = sum(para_coverages) / len(para_coverages)
            if mean_para_cov > 0:
                observed_ratios.append(block_cov / mean_para_cov)
            multi_block_sizes.append(len(blk_idxs))

        if multi_block_sizes and len(fd['all_paras']) >= 3:
            perm_folios.append((cat_sets, fd['_n'], multi_block_sizes))

    if not observed_ratios:
        print("  Insufficient data")
        return {'test': 'T5: Operational Coverage', 'passed': False,
                'reason': 'insufficient data'}

    observed_mean = sum(observed_ratios) / len(observed_ratios)

    # Null control: random paragraph groupings of same sizes
    null_means = []
    for _ in range(N_PERM):
        null_ratios = []
        for cat_sets, n, multi_sizes in perm_folios:
            indices = list(range(n))
            rng.shuffle(indices)
            idx = 0
            for sz in multi_sizes:
                group = indices[idx:idx + sz]
                idx += sz
                pcs = []
                uc = set()
                for gi in group:
                    cs = cat_sets[gi]
                    pcs.append(len(cs))
                    uc |= cs
                mpc = sum(pcs) / len(pcs)
                if mpc > 0:
                    null_ratios.append(len(uc) / mpc)
        if null_ratios:
            null_means.append(sum(null_ratios) / len(null_ratios))

    perm_p = permutation_p(observed_mean, null_means, 'greater')

    passed = perm_p < 0.01
    print(f"  Observed coverage ratio: {observed_mean:.4f} (n={len(observed_ratios)} blocks)")
    print(f"  Null mean: {sum(null_means) / len(null_means):.4f}" if null_means else "  No null data")
    print(f"  Permutation p: {perm_p:.4f}")
    print(f"  PASS: {passed}")

    return {
        'test': 'T5: Operational Coverage',
        'tier': 'T2 (structural)',
        'passed': passed,
        'observed_mean_ratio': round(observed_mean, 4),
        'null_mean_ratio': round(sum(null_means) / len(null_means), 4) if null_means else None,
        'n_blocks': len(observed_ratios),
        'perm_p': round(perm_p, 4),
    }


def test_t6(folio_data):
    """T6: Block-Initial Paragraph Enrichment."""
    print("\n=== T6: Block-Initial Paragraph Enrichment ===")

    initial_ht = []
    internal_ht = []
    initial_marking = []
    internal_marking = []

    for fd in folio_data.values():
        for bp_list in fd['block_paras']:
            if not bp_list:
                continue
            for idx, p in enumerate(bp_list):
                if p.token_count < 3:
                    continue
                ht = para_ht_density(p)
                mk = para_marking_rate(p)
                if idx == 0:
                    initial_ht.append(ht)
                    initial_marking.append(mk)
                else:
                    internal_ht.append(ht)
                    internal_marking.append(mk)

    results = {}

    # HT density test
    if initial_ht and internal_ht:
        init_mean = sum(initial_ht) / len(initial_ht)
        int_mean = sum(internal_ht) / len(internal_ht)
        U, z, p = mann_whitney_u(initial_ht, internal_ht)
        results['ht_initial_mean'] = round(init_mean, 4)
        results['ht_internal_mean'] = round(int_mean, 4)
        results['ht_mw_z'] = round(z, 3)
        results['ht_mw_p'] = round(p, 6)
        print(f"  HT density: initial={init_mean:.4f} vs internal={int_mean:.4f}, z={z:.2f} p={p:.4f}")

    # MARKING rate test
    if initial_marking and internal_marking:
        init_mean = sum(initial_marking) / len(initial_marking)
        int_mean = sum(internal_marking) / len(internal_marking)
        U, z, p = mann_whitney_u(initial_marking, internal_marking)
        results['marking_initial_mean'] = round(init_mean, 4)
        results['marking_internal_mean'] = round(int_mean, 4)
        results['marking_mw_z'] = round(z, 3)
        results['marking_mw_p'] = round(p, 6)
        print(f"  MARKING rate: initial={init_mean:.4f} vs internal={int_mean:.4f}, z={z:.2f} p={p:.4f}")

    # Pass if at least one metric significant
    ht_sig = results.get('ht_mw_p', 1.0) < 0.01
    mk_sig = results.get('marking_mw_p', 1.0) < 0.01
    passed = ht_sig or mk_sig

    results.update({
        'test': 'T6: Block-Initial Paragraph Enrichment',
        'tier': 'T2 (structural)',
        'passed': passed,
        'n_initial': len(initial_ht),
        'n_internal': len(internal_ht),
    })
    print(f"  PASS: {passed}")
    return results


def test_t7(folio_data):
    """T7: Section-Specific Block Architecture."""
    print("\n=== T7: Section-Specific Block Architecture ===")

    section_block_counts = defaultdict(list)
    section_block_sizes = defaultdict(list)
    section_paras_per_block = defaultdict(list)

    for fd in folio_data.values():
        sec = fd['section']
        nb = len(fd['blocks'])
        section_block_counts[sec].append(nb)
        for bp_list in fd['block_paras']:
            section_block_sizes[sec].append(sum(p.token_count for p in bp_list))
            section_paras_per_block[sec].append(len(bp_list))

    groups_counts = [section_block_counts[s] for s in sorted(section_block_counts)
                     if len(section_block_counts[s]) >= 3]
    groups_sizes = [section_block_sizes[s] for s in sorted(section_block_sizes)
                    if len(section_block_sizes[s]) >= 3]

    results = {'test': 'T7: Section-Specific Block Architecture', 'tier': 'T2 (structural)'}

    if len(groups_counts) >= 2:
        H_c, p_c = kruskal_wallis(groups_counts)
        results['block_count_H'] = round(H_c, 3)
        results['block_count_p'] = round(p_c, 6)
        print(f"  Block count by section: H={H_c:.2f}, p={p_c:.6f}")

    if len(groups_sizes) >= 2:
        H_s, p_s = kruskal_wallis(groups_sizes)
        results['block_size_H'] = round(H_s, 3)
        results['block_size_p'] = round(p_s, 6)
        print(f"  Block size by section: H={H_s:.2f}, p={p_s:.6f}")

    section_summary = {}
    for sec in sorted(section_block_counts):
        counts = section_block_counts[sec]
        sizes = section_block_sizes.get(sec, [])
        ppb = section_paras_per_block.get(sec, [])
        section_summary[sec] = {
            'n_folios': len(counts),
            'mean_blocks': round(sum(counts) / len(counts), 2),
            'mean_block_tokens': round(sum(sizes) / len(sizes), 1) if sizes else 0,
            'mean_paras_per_block': round(sum(ppb) / len(ppb), 2) if ppb else 0,
        }

    results['section_summary'] = section_summary
    passed = results.get('block_count_p', 1.0) < 0.01 or results.get('block_size_p', 1.0) < 0.01
    results['passed'] = passed
    print(f"  PASS: {passed}")
    return results


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("Phase 462: TEXT_BLOCK_PARALLEL_OPERATORS")
    print("=" * 80)

    rng = random.Random(SEED)
    folio_data = load_data()
    precompute_pairwise(folio_data)

    results = {}
    results['T1'] = test_t1(folio_data)
    results['T2'] = test_t2(folio_data, rng)
    results['T3'] = test_t3(folio_data, rng)
    results['T4'] = test_t4(folio_data, rng)
    results['T5'] = test_t5(folio_data, rng)
    results['T6'] = test_t6(folio_data)
    results['T7'] = test_t7(folio_data)

    # Summary
    passed = sum(1 for r in results.values() if r.get('passed'))
    total = len(results)

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    for k, r in results.items():
        status = "PASS" if r.get('passed') else "FAIL"
        print(f"  {k}: {status} — {r.get('test', k)}")
    print(f"{'=' * 80}")

    output = {
        'phase': 'TEXT_BLOCK_PARALLEL_OPERATORS',
        'phase_number': 462,
        'tier': '2-3 (structural with interpretive implications)',
        'seed': SEED,
        'n_permutations': N_PERM,
        'tests': results,
        'summary': {
            'tests_passed': passed,
            'tests_total': total,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'text_block_parallel_operators.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
