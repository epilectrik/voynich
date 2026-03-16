"""Phase 594: Within-Line Atom Sequence Grammar

Tests whether the TERM→HEAD routing grammar (C1563) varies by line position
(quintile Q0-Q4), revealing position-modulated routing as the mechanism by
which individual tokens produce the specification→work→closure arc.

TERM = MIDDLE terminal atom from decompose_middle_hmt() (NOT suffix — C1564).
HEAD = MIDDLE head atom from decompose_middle_hmt().
"""

import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# ── Constants ──────────────────────────────────────────────────────────

TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']
N_TERMS = len(TERM_TYPES)
N_HEADS = len(HEAD_TYPES)
N_CELLS = N_TERMS * N_HEADS  # 42
N_QUINTILES = 5

TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}

# Major enriched rules from C1563
ENRICHED_RULES = [
    ('r', 'a', 2.23), ('h', 't', 1.89), ('y', 'k', 1.60),
    ('m', 'o', 1.55), ('n', 'a', 1.42), ('l', 'e', 1.25),
]

# Major depleted rules from C1563
DEPLETED_RULES = [
    ('r', 't', 0.25), ('r', 'k', 0.37), ('n', 't', 0.32), ('n', 'k', 0.53),
]

N_SHUFFLES = 1000
N_BOOTSTRAP = 1000
SEED = 42
MIN_COUNT = 20  # Minimum count filter for enrichment reporting

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# Section assignments (standard mapping)
SECTION_MAP = {
    'f1r': 'H', 'f1v': 'H', 'f2r': 'H', 'f2v': 'H', 'f3r': 'H', 'f3v': 'H',
    'f4r': 'H', 'f4v': 'H', 'f5r': 'H', 'f5v': 'H', 'f6r': 'H', 'f6v': 'H',
    'f7r': 'H', 'f7v': 'H', 'f8r': 'H', 'f8v': 'H', 'f9r': 'H', 'f9v': 'H',
    'f10r': 'H', 'f10v': 'H', 'f11r': 'H', 'f11v': 'H', 'f13r': 'H', 'f13v': 'H',
    'f14r': 'H', 'f14v': 'H', 'f15r': 'H', 'f15v': 'H', 'f16r': 'H', 'f16v': 'H',
    'f17r': 'H', 'f17v': 'H', 'f18r': 'H', 'f18v': 'H', 'f19r': 'H', 'f19v': 'H',
    'f20r': 'H', 'f20v': 'H', 'f22r': 'H', 'f22v': 'H', 'f23r': 'H', 'f23v': 'H',
    'f24r': 'H', 'f24v': 'H', 'f25r': 'H', 'f25v': 'H',
    'f27r': 'H', 'f27v': 'H', 'f29r': 'H', 'f29v': 'H',
    'f31r': 'H', 'f31v': 'H', 'f32r': 'H', 'f32v': 'H',
    'f33r': 'H', 'f33v': 'H', 'f34r': 'H', 'f34v': 'H',
    'f35r': 'H', 'f35v': 'H', 'f36r': 'H', 'f36v': 'H',
    'f38r': 'H', 'f38v': 'H', 'f39r': 'H', 'f39v': 'H',
    'f40r': 'H', 'f40v': 'H', 'f41r': 'H', 'f41v': 'H',
    'f47r': 'H', 'f47v': 'H', 'f48r': 'H', 'f48v': 'H',
    'f49r': 'H', 'f49v': 'H', 'f50r': 'H', 'f50v': 'H',
    'f65r': 'H', 'f65v': 'H', 'f66r': 'H', 'f66v': 'H',
    'f75r': 'B', 'f75v': 'B', 'f76r': 'B', 'f76v': 'B',
    'f77r': 'B', 'f77v': 'B', 'f78r': 'B', 'f78v': 'B',
    'f79r': 'B', 'f79v': 'B', 'f80r': 'B', 'f80v': 'B',
    'f81r': 'B', 'f81v': 'B', 'f82r': 'B', 'f82v': 'B',
    'f83r': 'B', 'f83v': 'B', 'f84r': 'B', 'f84v': 'B',
    'f86v3': 'S', 'f86v4': 'S',
    'f87r': 'B', 'f87v': 'B', 'f88r': 'B', 'f88v': 'B',
    'f89r1': 'B', 'f89r2': 'B', 'f89v1': 'B', 'f89v2': 'B',
    'f99r': 'S', 'f99v': 'S', 'f100r': 'S', 'f100v': 'S',
    'f101r1': 'S', 'f101v2': 'S', 'f102r1': 'S', 'f102r2': 'S',
    'f102v1': 'S', 'f102v2': 'S', 'f103r': 'C', 'f103v': 'C',
    'f104r': 'C', 'f104v': 'C', 'f105r': 'C', 'f105v': 'C',
    'f106r': 'C', 'f106v': 'C', 'f107r': 'C', 'f107v': 'C',
    'f108r': 'C', 'f108v': 'C', 'f111r': 'C', 'f111v': 'C',
    'f112r': 'C', 'f112v': 'C', 'f113r': 'C', 'f113v': 'C',
    'f114r': 'C', 'f114v': 'C', 'f115r': 'C', 'f116r': 'C',
}


# ── Helpers ────────────────────────────────────────────────────────────

def get_head_and_term(word, morph):
    """Extract MIDDLE HEAD and TERM atoms."""
    m = morph.extract(word)
    if not m.middle:
        return None, None
    head, mods, term, frame = decompose_middle_hmt(m.middle)
    head = head if head else 'headless'
    return head, term


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else np.ones_like(p) / len(p)
    q = q / q.sum() if q.sum() > 0 else np.ones_like(q) / len(q)
    return float(jensenshannon(p, q) ** 2)  # squared JSD


def mi_from_contingency(table):
    """Compute mutual information in bits from a 2D contingency table."""
    table = np.asarray(table, dtype=float)
    total = table.sum()
    if total == 0:
        return 0.0
    p_joint = table / total
    p_row = table.sum(axis=1) / total
    p_col = table.sum(axis=0) / total
    mi = 0.0
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            if p_joint[i, j] > 0 and p_row[i] > 0 and p_col[j] > 0:
                mi += p_joint[i, j] * np.log2(p_joint[i, j] / (p_row[i] * p_col[j]))
    return mi


# ── Data Assembly ──────────────────────────────────────────────────────

def assemble_data():
    """Load Currier B tokens, group by line, extract HEAD/TERM/quintile."""
    tx = Transcript()
    morph = Morphology()

    line_groups = defaultdict(list)  # (folio, line) -> [(head, term, quintile, section), ...]

    for token in tx.currier_b():
        if token.placement.startswith('L'):
            continue
        if '*' in token.word:
            continue
        w = token.word.strip()
        if not w:
            continue
        head, term = get_head_and_term(w, morph)
        if head is None:
            continue
        if term not in TERM_IDX or head not in HEAD_IDX:
            continue
        section = SECTION_MAP.get(token.folio, '?')
        line_groups[(token.folio, token.line)].append({
            'head': head, 'term': term, 'section': section, 'folio': token.folio
        })

    # Assign quintiles
    records = []  # Each record: (folio, line, head, term, quintile, section, idx, line_len)
    line_data = {}  # (folio, line) -> list of enriched token dicts
    for (folio, line), tokens in sorted(line_groups.items()):
        line_len = len(tokens)
        if line_len < 3:
            continue
        enriched = []
        for idx, tok in enumerate(tokens):
            frac_pos = idx / (line_len - 1) if line_len > 1 else 0.5
            quintile = min(int(frac_pos * 5), 4)
            tok['quintile'] = quintile
            tok['idx'] = idx
            tok['line_len'] = line_len
            enriched.append(tok)
        line_data[(folio, line)] = enriched

    return line_data


def build_pairs(line_data):
    """Build consecutive token pairs within lines.
    Returns list of (source_term, source_quintile, target_head, target_quintile, section, line_len)
    """
    pairs = []
    for (folio, line), tokens in sorted(line_data.items()):
        for i in range(len(tokens) - 1):
            src = tokens[i]
            tgt = tokens[i + 1]
            pairs.append((
                src['term'], src['quintile'],
                tgt['head'], tgt['quintile'],
                src['section'], src['line_len']
            ))
    return pairs


# ── T1: Position-Conditioned Routing Matrices ──────────────────────────

def compute_t1(pairs):
    """Build per-quintile 7×6 count/enrichment matrices."""
    # Count matrices per quintile
    q_counts = {q: np.zeros((N_TERMS, N_HEADS)) for q in range(N_QUINTILES)}
    global_counts = np.zeros((N_TERMS, N_HEADS))

    for src_term, src_q, tgt_head, tgt_q, section, ll in pairs:
        ti = TERM_IDX[src_term]
        hi = HEAD_IDX[tgt_head]
        q_counts[src_q][ti, hi] += 1
        global_counts[ti, hi] += 1

    total_pairs = int(global_counts.sum())
    q_totals = {q: int(q_counts[q].sum()) for q in range(N_QUINTILES)}

    # Global marginals
    global_term_marginal = global_counts.sum(axis=1) / total_pairs  # P(TERM)
    global_head_marginal = global_counts.sum(axis=0) / total_pairs  # P(HEAD)

    # Per-quintile TERM marginals (for Version B)
    q_term_marginals = {}
    for q in range(N_QUINTILES):
        qt = q_counts[q].sum()
        if qt > 0:
            q_term_marginals[q] = q_counts[q].sum(axis=1) / qt
        else:
            q_term_marginals[q] = np.ones(N_TERMS) / N_TERMS

    # Version A: global-marginal enrichment
    enrich_A = {}
    for q in range(N_QUINTILES):
        expected = np.outer(global_term_marginal, global_head_marginal) * q_totals[q]
        with np.errstate(divide='ignore', invalid='ignore'):
            e = np.where(expected > 0, q_counts[q] / expected, 0.0)
        enrich_A[q] = e

    # Version B: local-marginal enrichment (isolates three-way interaction)
    enrich_B = {}
    for q in range(N_QUINTILES):
        expected = np.outer(q_term_marginals[q], global_head_marginal) * q_totals[q]
        with np.errstate(divide='ignore', invalid='ignore'):
            e = np.where(expected > 0, q_counts[q] / expected, 0.0)
        enrich_B[q] = e

    # JSD of each quintile's routing proportions vs global
    global_props = global_counts.flatten()
    global_props = global_props / global_props.sum()

    jsd_vs_global_A = {}
    jsd_vs_global_B = {}
    for q in range(N_QUINTILES):
        q_props = q_counts[q].flatten()
        q_props = q_props / q_props.sum() if q_props.sum() > 0 else np.ones(N_CELLS) / N_CELLS
        jsd_vs_global_A[q] = jsd(q_props, global_props)

    # For Version B JSD: compare local-marginal-adjusted proportions
    # This is the JSD between the quintile's actual routing distribution and
    # what the independent margins predict
    for q in range(N_QUINTILES):
        predicted = np.outer(q_term_marginals[q], global_head_marginal).flatten()
        predicted = predicted / predicted.sum() if predicted.sum() > 0 else np.ones(N_CELLS) / N_CELLS
        actual = q_counts[q].flatten()
        actual = actual / actual.sum() if actual.sum() > 0 else np.ones(N_CELLS) / N_CELLS
        jsd_vs_global_B[q] = jsd(actual, predicted)

    # Format output
    result = {
        'total_pairs': total_pairs,
        'per_quintile_pairs': q_totals,
        'global_counts': global_counts.tolist(),
        'per_quintile_counts': {str(q): q_counts[q].tolist() for q in range(N_QUINTILES)},
        'enrichment_version_A': {str(q): [[round(v, 3) for v in row] for row in enrich_A[q].tolist()] for q in range(N_QUINTILES)},
        'enrichment_version_B': {str(q): [[round(v, 3) for v in row] for row in enrich_B[q].tolist()] for q in range(N_QUINTILES)},
        'jsd_vs_global_A': {str(q): round(jsd_vs_global_A[q], 6) for q in range(N_QUINTILES)},
        'jsd_vs_global_B': {str(q): round(jsd_vs_global_B[q], 6) for q in range(N_QUINTILES)},
        'term_types': TERM_TYPES,
        'head_types': HEAD_TYPES,
    }
    return result, q_counts, global_counts


# ── T2: Three-Way Interaction Test ─────────────────────────────────────

def compute_g_squared(contingency_3d):
    """Compute G² for TERM×HEAD×Quintile three-way interaction.

    contingency_3d: shape (N_QUINTILES, N_TERMS, N_HEADS)
    Tests: full model vs model with all two-way interactions but no three-way.
    G² = 2 * Σ O * ln(O / E) where E is the expected count under the null.
    """
    table = contingency_3d.copy()
    total = table.sum()
    if total == 0:
        return 0.0

    # Compute expected counts under H0 (all two-way, no three-way)
    # E_{qth} = N * P(q,t) * P(q,h) * P(t,h) / (P(q)^2 * P(t) * P(h))
    # Using iterative proportional fitting (IPF) for the log-linear model
    expected = np.ones_like(table, dtype=float)

    # Marginals
    m_qt = table.sum(axis=2)  # (Q, T)
    m_qh = table.sum(axis=1)  # (Q, H)
    m_th = table.sum(axis=0)  # (T, H)

    # IPF: fit to all three two-way marginals
    for iteration in range(200):
        # Fit Q×T margin
        cur_qt = expected.sum(axis=2)
        for q in range(N_QUINTILES):
            for t in range(N_TERMS):
                if cur_qt[q, t] > 0:
                    expected[q, t, :] *= m_qt[q, t] / cur_qt[q, t]

        # Fit Q×H margin
        cur_qh = expected.sum(axis=1)
        for q in range(N_QUINTILES):
            for h in range(N_HEADS):
                if cur_qh[q, h] > 0:
                    expected[q, :, h] *= m_qh[q, h] / cur_qh[q, h]

        # Fit T×H margin
        cur_th = expected.sum(axis=0)
        for t in range(N_TERMS):
            for h in range(N_HEADS):
                if cur_th[t, h] > 0:
                    expected[:, t, h] *= m_th[t, h] / cur_th[t, h]

        # Check convergence
        if iteration > 10:
            err_qt = np.abs(expected.sum(axis=2) - m_qt).max()
            err_qh = np.abs(expected.sum(axis=1) - m_qh).max()
            err_th = np.abs(expected.sum(axis=0) - m_th).max()
            if max(err_qt, err_qh, err_th) < 1e-8:
                break

    # G² = 2 * Σ O * ln(O/E) for O > 0
    g2 = 0.0
    for q in range(N_QUINTILES):
        for t in range(N_TERMS):
            for h in range(N_HEADS):
                obs = table[q, t, h]
                exp = expected[q, t, h]
                if obs > 0 and exp > 0:
                    g2 += obs * np.log(obs / exp)
    g2 *= 2.0

    return g2


def compute_t2(pairs, line_data, rng):
    """Three-way interaction test with shuffle null."""
    # Build 3D contingency table
    contingency = np.zeros((N_QUINTILES, N_TERMS, N_HEADS))
    for src_term, src_q, tgt_head, tgt_q, section, ll in pairs:
        contingency[src_q, TERM_IDX[src_term], HEAD_IDX[tgt_head]] += 1

    g2_obs = compute_g_squared(contingency)
    total_n = int(contingency.sum())

    # Degrees of freedom for three-way interaction
    df = (N_QUINTILES - 1) * (N_TERMS - 1) * (N_HEADS - 1)

    # Cramér's V
    cramers_v = np.sqrt(g2_obs / (total_n * min(df, 1))) if total_n > 0 and df > 0 else 0.0

    # Shuffle null: permute quintile labels within each line
    g2_null = []
    for perm_i in range(N_SHUFFLES):
        shuffled_contingency = np.zeros((N_QUINTILES, N_TERMS, N_HEADS))
        for (folio, line), tokens in line_data.items():
            n_tok = len(tokens)
            if n_tok < 3:
                continue
            # Permute quintile assignments
            quintiles = [t['quintile'] for t in tokens]
            shuffled_q = list(quintiles)
            rng.shuffle(shuffled_q)

            for i in range(n_tok - 1):
                src = tokens[i]
                tgt = tokens[i + 1]
                sq = shuffled_q[i]
                ti = TERM_IDX.get(src['term'])
                hi = HEAD_IDX.get(tgt['head'])
                if ti is not None and hi is not None:
                    shuffled_contingency[sq, ti, hi] += 1

        g2_null.append(compute_g_squared(shuffled_contingency))

    g2_null = np.array(g2_null)
    p_value = float(np.mean(g2_null >= g2_obs))
    g2_p99 = float(np.percentile(g2_null, 99))
    snr = g2_obs / g2_p99 if g2_p99 > 0 else float('inf')

    return {
        'g_squared': round(g2_obs, 2),
        'df': df,
        'n_pairs': total_n,
        'cramers_v': round(cramers_v, 4),
        'shuffle_p': round(p_value, 4),
        'shuffle_null_mean': round(float(g2_null.mean()), 2),
        'shuffle_null_p99': round(g2_p99, 2),
        'signal_to_noise_ratio': round(snr, 2),
        'n_shuffles': N_SHUFFLES,
        'significant': p_value < 0.01,
    }


# ── T3: Zone-Transition Routing Shift ──────────────────────────────────

def compute_t3(q_counts, pairs, rng):
    """Compare per-quintile routing matrices across zone boundaries."""
    # Pairwise JSD between consecutive quintile routing matrices
    transitions = {}
    labels = ['Q0_vs_Q1', 'Q1_vs_Q2', 'Q2_vs_Q3', 'Q3_vs_Q4']
    for i, label in enumerate(labels):
        p1 = q_counts[i].flatten()
        p2 = q_counts[i + 1].flatten()
        transitions[label] = round(jsd(p1, p2), 6)

    # Total consecutive JSD sum
    total_jsd = sum(transitions.values())
    q3_q4_frac = transitions['Q3_vs_Q4'] / total_jsd if total_jsd > 0 else 0.0

    # Bootstrap CI on Q3-vs-Q4 JSD (Q4 has reduced counts)
    # Resample Q4 pairs with replacement
    q4_pairs = [(src_t, tgt_h) for src_t, src_q, tgt_h, tgt_q, sec, ll in pairs if src_q == 4]
    q3_counts_flat = q_counts[3].flatten()

    bootstrap_jsds = []
    for _ in range(N_BOOTSTRAP):
        # Resample Q4 pairs
        if len(q4_pairs) > 0:
            boot_idx = rng.integers(0, len(q4_pairs), size=len(q4_pairs))
            boot_counts = np.zeros((N_TERMS, N_HEADS))
            for bi in boot_idx:
                st, th = q4_pairs[bi]
                if st in TERM_IDX and th in HEAD_IDX:
                    boot_counts[TERM_IDX[st], HEAD_IDX[th]] += 1
            bootstrap_jsds.append(jsd(q3_counts_flat, boot_counts.flatten()))
        else:
            bootstrap_jsds.append(0.0)

    bootstrap_jsds = np.array(bootstrap_jsds)
    ci_lo = float(np.percentile(bootstrap_jsds, 2.5))
    ci_hi = float(np.percentile(bootstrap_jsds, 97.5))

    # Work-zone baseline
    work_jsds = [transitions['Q1_vs_Q2'], transitions['Q2_vs_Q3']]
    work_mean = np.mean(work_jsds)

    # Closure dominance check
    closure_dominated = (q3_q4_frac > 0.70 and
                         transitions['Q0_vs_Q1'] <= max(work_jsds) * 1.5)

    # Zone-transition gated check
    zone_gated = (transitions['Q3_vs_Q4'] > max(work_jsds) * 3 and
                  transitions['Q0_vs_Q1'] > max(work_jsds) * 2)

    return {
        'pairwise_jsd': transitions,
        'total_jsd_sum': round(total_jsd, 6),
        'q3_q4_fraction_of_total': round(q3_q4_frac, 4),
        'work_zone_mean_jsd': round(work_mean, 6),
        'q3_q4_bootstrap_ci': [round(ci_lo, 6), round(ci_hi, 6)],
        'q4_pair_count': len(q4_pairs),
        'closure_dominated': closure_dominated,
        'zone_transition_gated': zone_gated,
    }


# ── T4: Mutual Information Decomposition ───────────────────────────────

def compute_t4(pairs):
    """MI decomposition: total, conditional, interaction, co-information."""
    # Total MI: MI(TERM_n; HEAD_{n+1}) across all pairs
    total_table = np.zeros((N_TERMS, N_HEADS))
    for src_term, src_q, tgt_head, tgt_q, sec, ll in pairs:
        total_table[TERM_IDX[src_term], HEAD_IDX[tgt_head]] += 1

    mi_total = mi_from_contingency(total_table)

    # Position-conditional MI: Σ_q P(q) × MI(TERM; HEAD | Q=q)
    q_tables = {q: np.zeros((N_TERMS, N_HEADS)) for q in range(N_QUINTILES)}
    q_counts = Counter()
    for src_term, src_q, tgt_head, tgt_q, sec, ll in pairs:
        q_tables[src_q][TERM_IDX[src_term], HEAD_IDX[tgt_head]] += 1
        q_counts[src_q] += 1

    total_n = sum(q_counts.values())
    mi_conditional = 0.0
    per_q_mi = {}
    for q in range(N_QUINTILES):
        p_q = q_counts[q] / total_n if total_n > 0 else 0.0
        mi_q = mi_from_contingency(q_tables[q])
        per_q_mi[q] = mi_q
        mi_conditional += p_q * mi_q

    # Interaction MI = Total - Conditional
    mi_interaction = mi_total - mi_conditional

    # Co-information: I(TERM; HEAD; Q) = I(TERM; HEAD) - I(TERM; HEAD | Q)
    # Same as mi_interaction by definition
    # Positive = redundancy, Negative = synergy
    co_info = mi_interaction

    return {
        'mi_total_bits': round(mi_total, 6),
        'mi_conditional_bits': round(mi_conditional, 6),
        'mi_interaction_bits': round(mi_interaction, 6),
        'interaction_fraction': round(mi_interaction / mi_total, 4) if mi_total > 0 else 0.0,
        'co_information_bits': round(co_info, 6),
        'interpretation': 'REDUNDANCY' if co_info > 0 else ('SYNERGY' if co_info < -1e-6 else 'INDEPENDENT'),
        'per_quintile_mi': {str(q): round(per_q_mi[q], 6) for q in range(N_QUINTILES)},
    }


# ── T5: Per-Rule Positional Activation Profile ─────────────────────────

def compute_t5(pairs, q_counts, global_counts):
    """Per-rule positional activation curves using Version A enrichment."""
    total_pairs = sum(p[1] == q for p in pairs for q in range(N_QUINTILES))  # approximate
    # More precise: use q_counts totals
    q_totals = {q: q_counts[q].sum() for q in range(N_QUINTILES)}
    grand_total = global_counts.sum()

    global_term_marginal = global_counts.sum(axis=1) / grand_total
    global_head_marginal = global_counts.sum(axis=0) / grand_total

    results = {}

    all_rules = ENRICHED_RULES + DEPLETED_RULES
    for term, head, global_enrich in all_rules:
        ti = TERM_IDX[term]
        hi = HEAD_IDX[head]

        enrichments = []
        counts = []
        for q in range(N_QUINTILES):
            obs = q_counts[q][ti, hi]
            expected = global_term_marginal[ti] * global_head_marginal[hi] * q_totals[q]
            enrich = obs / expected if expected > 0 else 0.0
            enrichments.append(round(enrich, 3))
            counts.append(int(obs))

        # Spearman trend test
        if len(enrichments) >= 3:
            rho, p_val = spearmanr(range(N_QUINTILES), enrichments)
        else:
            rho, p_val = 0.0, 1.0

        key = f"{term}_to_{head}"
        results[key] = {
            'global_enrichment': global_enrich,
            'per_quintile_enrichment': enrichments,
            'per_quintile_counts': counts,
            'spearman_rho': round(rho, 4) if not np.isnan(rho) else 0.0,
            'spearman_p': round(p_val, 4) if not np.isnan(p_val) else 1.0,
            'position_modulated': p_val < 0.05,
            'min_count_met': all(c >= MIN_COUNT for c in counts),
        }

    return results


# ── T6: Depleted-Rule Position Localization ────────────────────────────

def compute_t6(q_counts, global_counts):
    """Check if globally depleted rules are enriched at specific quintiles."""
    q_totals = {q: q_counts[q].sum() for q in range(N_QUINTILES)}
    grand_total = global_counts.sum()
    global_term_marginal = global_counts.sum(axis=1) / grand_total
    global_head_marginal = global_counts.sum(axis=0) / grand_total

    results = {}
    for term, head, global_depl in DEPLETED_RULES:
        ti = TERM_IDX[term]
        hi = HEAD_IDX[head]

        enrichments = []
        counts = []
        for q in range(N_QUINTILES):
            obs = q_counts[q][ti, hi]
            expected = global_term_marginal[ti] * global_head_marginal[hi] * q_totals[q]
            enrich = obs / expected if expected > 0 else 0.0
            enrichments.append(round(enrich, 3))
            counts.append(int(obs))

        # Find position-specific exceptions (globally depleted but locally enriched)
        exceptions = []
        for q in range(N_QUINTILES):
            if enrichments[q] > 1.0 and counts[q] >= MIN_COUNT:
                exceptions.append({'quintile': q, 'enrichment': enrichments[q], 'count': counts[q]})

        key = f"{term}_to_{head}"
        results[key] = {
            'global_depletion': global_depl,
            'per_quintile_enrichment': enrichments,
            'per_quintile_counts': counts,
            'position_exceptions': exceptions,
            'has_exceptions': len(exceptions) > 0,
        }

    return results


# ── Controls ───────────────────────────────────────────────────────────

def section_stratification(pairs):
    """Test whether position-routing interaction is universal or section-specific."""
    section_pairs = defaultdict(list)
    for src_term, src_q, tgt_head, tgt_q, section, ll in pairs:
        section_pairs[section].append((src_term, src_q, tgt_head))

    results = {}
    for section, sp in sorted(section_pairs.items()):
        if len(sp) < 500:  # Need enough data
            continue
        contingency = np.zeros((N_QUINTILES, N_TERMS, N_HEADS))
        for src_term, src_q, tgt_head in sp:
            contingency[src_q, TERM_IDX[src_term], HEAD_IDX[tgt_head]] += 1

        g2 = compute_g_squared(contingency)
        n = int(contingency.sum())
        results[section] = {
            'g_squared': round(g2, 2),
            'n_pairs': n,
            'g2_per_pair': round(g2 / n, 6) if n > 0 else 0.0,
        }

    return results


def line_length_stratification(pairs):
    """Test interaction for short/medium/long lines."""
    strata = {'short': [], 'medium': [], 'long': []}
    for src_term, src_q, tgt_head, tgt_q, section, ll in pairs:
        if ll <= 7:
            strata['short'].append((src_term, src_q, tgt_head))
        elif ll <= 11:
            strata['medium'].append((src_term, src_q, tgt_head))
        else:
            strata['long'].append((src_term, src_q, tgt_head))

    results = {}
    for name, sp in strata.items():
        if len(sp) < 500:
            continue
        contingency = np.zeros((N_QUINTILES, N_TERMS, N_HEADS))
        for src_term, src_q, tgt_head in sp:
            contingency[src_q, TERM_IDX[src_term], HEAD_IDX[tgt_head]] += 1

        g2 = compute_g_squared(contingency)
        n = int(contingency.sum())
        results[name] = {
            'g_squared': round(g2, 2),
            'n_pairs': n,
            'g2_per_pair': round(g2 / n, 6) if n > 0 else 0.0,
        }

    return results


# ── Verdict ────────────────────────────────────────────────────────────

def compute_verdict(t2_result, t3_result, t1_result):
    """Determine final verdict based on T2 + T3 + T1.

    Decision tree from plan:
    - G2 not significant:
      - Version A JSDs all small -> ROUTING_UNIFORM
      - JSDs elevated (esp Q4) -> MARGINAL_PRODUCT
    - G2 significant:
      - T3 closure dominated -> CLOSURE_DOMINATED
      - T3 zone-transition gated -> ZONE_TRANSITION_GATED
      - T3 continuous gradient -> CONTINUOUS_GRADIENT
      - Otherwise -> POSITION_MODULATED
    """
    if not t2_result['significant']:
        # Check if routing visibly varies by position (Version A JSD)
        jsds_A = t1_result['jsd_vs_global_A']
        max_jsd = max(float(v) for v in jsds_A.values())
        interior_jsds = [float(jsds_A[str(q)]) for q in [1, 2, 3]]
        max_interior = max(interior_jsds)

        # If Q4 JSD >> interior, routing varies but it's marginal-driven
        if max_jsd > 0.005 and max_jsd > max_interior * 3:
            return 'MARGINAL_PRODUCT'
        else:
            return 'ROUTING_UNIFORM'

    # T2 significant -> check T3
    t3 = t3_result
    if t3['closure_dominated']:
        return 'CLOSURE_DOMINATED'
    elif t3['zone_transition_gated']:
        return 'ZONE_TRANSITION_GATED'
    else:
        jsds = t3['pairwise_jsd']
        vals = [jsds['Q0_vs_Q1'], jsds['Q1_vs_Q2'], jsds['Q2_vs_Q3'], jsds['Q3_vs_Q4']]
        rho, p = spearmanr(range(4), vals)
        if rho > 0.8 and p < 0.1:
            return 'CONTINUOUS_GRADIENT'
        else:
            return 'POSITION_MODULATED'


# ── Main ───────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)

    print("Phase 594: Within-Line Atom Sequence Grammar")
    print("=" * 60)

    # Data assembly
    print("\nAssembling data...")
    line_data = assemble_data()
    pairs = build_pairs(line_data)
    n_lines = len(line_data)
    n_pairs = len(pairs)
    print(f"  Lines: {n_lines}, Pairs: {n_pairs}")

    # Quintile pair counts
    q_pair_counts = Counter(src_q for _, src_q, _, _, _, _ in pairs)
    print(f"  Pair counts by source quintile: {dict(sorted(q_pair_counts.items()))}")

    # T1: Position-Conditioned Routing Matrices
    print("\nT1: Position-conditioned routing matrices...")
    t1_result, q_counts, global_counts = compute_t1(pairs)
    print(f"  Total pairs: {t1_result['total_pairs']}")
    print(f"  Per-quintile pairs: {t1_result['per_quintile_pairs']}")
    print(f"  JSD vs global (Version A): {t1_result['jsd_vs_global_A']}")
    print(f"  JSD vs global (Version B): {t1_result['jsd_vs_global_B']}")

    # T2: Three-Way Interaction Test
    print(f"\nT2: Three-way interaction test ({N_SHUFFLES} shuffles)...")
    t2_result = compute_t2(pairs, line_data, rng)
    print(f"  G² = {t2_result['g_squared']}, df = {t2_result['df']}")
    print(f"  Cramér's V = {t2_result['cramers_v']}")
    print(f"  Shuffle p = {t2_result['shuffle_p']}")
    print(f"  Null mean = {t2_result['shuffle_null_mean']}, p99 = {t2_result['shuffle_null_p99']}")
    print(f"  Signal/noise = {t2_result['signal_to_noise_ratio']}")
    print(f"  Significant: {t2_result['significant']}")

    # T3: Zone-Transition Routing Shift
    print("\nT3: Zone-transition routing shift...")
    t3_result = compute_t3(q_counts, pairs, rng)
    print(f"  Pairwise JSD: {t3_result['pairwise_jsd']}")
    print(f"  Q3->Q4 fraction: {t3_result['q3_q4_fraction_of_total']}")
    print(f"  Work-zone mean: {t3_result['work_zone_mean_jsd']}")
    print(f"  Q4 bootstrap CI: {t3_result['q3_q4_bootstrap_ci']}")
    print(f"  Q4 pairs: {t3_result['q4_pair_count']}")
    print(f"  Closure dominated: {t3_result['closure_dominated']}")
    print(f"  Zone-transition gated: {t3_result['zone_transition_gated']}")

    # T4: MI Decomposition
    print("\nT4: MI decomposition...")
    t4_result = compute_t4(pairs)
    print(f"  Total MI: {t4_result['mi_total_bits']} bits")
    print(f"  Conditional MI: {t4_result['mi_conditional_bits']} bits")
    print(f"  Interaction MI: {t4_result['mi_interaction_bits']} bits ({t4_result['interaction_fraction']} of total)")
    print(f"  Co-information: {t4_result['co_information_bits']} bits -> {t4_result['interpretation']}")
    print(f"  Per-quintile MI: {t4_result['per_quintile_mi']}")

    # T5: Per-Rule Activation Profiles
    print("\nT5: Per-rule positional activation profiles...")
    t5_result = compute_t5(pairs, q_counts, global_counts)
    n_modulated = sum(1 for v in t5_result.values() if v['position_modulated'])
    print(f"  Position-modulated rules: {n_modulated}/{len(t5_result)}")
    for key, val in sorted(t5_result.items()):
        marker = " *" if val['position_modulated'] else ""
        print(f"    {key}: {val['per_quintile_enrichment']} rho={val['spearman_rho']} p={val['spearman_p']}{marker}")

    # T6: Depleted-Rule Localization
    print("\nT6: Depleted-rule position localization...")
    t6_result = compute_t6(q_counts, global_counts)
    for key, val in sorted(t6_result.items()):
        exc = f" EXCEPTIONS: {val['position_exceptions']}" if val['has_exceptions'] else ""
        print(f"    {key}: {val['per_quintile_enrichment']}{exc}")

    # Controls
    print("\nControls...")
    section_strat = section_stratification(pairs)
    print(f"  Section stratification:")
    for sec, val in sorted(section_strat.items()):
        print(f"    {sec}: G²={val['g_squared']}, n={val['n_pairs']}, G²/n={val['g2_per_pair']}")

    length_strat = line_length_stratification(pairs)
    print(f"  Line-length stratification:")
    for name, val in sorted(length_strat.items()):
        print(f"    {name}: G²={val['g_squared']}, n={val['n_pairs']}, G²/n={val['g2_per_pair']}")

    # Verdict
    verdict = compute_verdict(t2_result, t3_result, t1_result)
    print(f"\n{'=' * 60}")
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 60}")

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': 594,
            'script': 'within_line_atom_grammar.py',
            'runtime_seconds': round(elapsed, 1),
            'n_lines': n_lines,
            'n_pairs': n_pairs,
            'seed': SEED,
        },
        'T1_position_conditioned_routing': t1_result,
        'T2_three_way_interaction': t2_result,
        'T3_zone_transition': t3_result,
        'T4_mi_decomposition': t4_result,
        'T5_per_rule_activation': t5_result,
        'T6_depleted_rule_localization': t6_result,
        'controls': {
            'section_stratification': section_strat,
            'line_length_stratification': length_strat,
        },
        'verdict': verdict,
    }

    out_path = os.path.join(RESULTS_DIR, 'within_line_atom_grammar_results.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
