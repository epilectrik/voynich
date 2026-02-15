#!/usr/bin/env python3
"""Phase 365: Section-Parameterized Line Grammar

Tests whether section identity modulates the Currier B line grammar —
interior transitions (H1-H5) and boundary constraints (H6-H10).

Depends on:
  C1029 (section-parameterized grammar), C956-C964 (line grammar),
  C821 (REGIME-invariant line syntax), C789 (forbidden compliance),
  C957 (mandatory bigrams), C958 (line length), C552 (role taxonomy)

Outputs:
  phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = PROJECT / 'phases' / 'SECTION_PARAMETERIZED_LINE_GRAMMAR' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SECTION_NAMES = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS_RECIPE', 'C': 'COSMO'}
VALID_SECTIONS = set(SECTION_NAMES.keys())
RNG = np.random.RandomState(42)
N_PERMS = 1000

# ════════════════════════════════════════════════════════════════
# S1: Load B corpus, assign classes/roles, build per-line structures
# ════════════════════════════════════════════════════════════════

def load_data():
    """Load B corpus with class assignments and per-line structure."""
    print("S1: Loading data...")

    # Class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in cmap['class_to_role'].items()}

    # Forbidden MIDDLE pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    # Mandatory bigrams
    with open(PROJECT / 'phases' / 'LINE_CONTROL_BLOCK_GRAMMAR' / 'results' / '02_mandatory_forbidden_bigrams.json',
              encoding='utf-8') as f:
        bigram_data = json.load(f)
    mandatory_bigrams = bigram_data['mandatory']['bigrams']

    # Exclusive tokens
    with open(PROJECT / 'phases' / 'LINE_CONTROL_BLOCK_GRAMMAR' / 'results' / '01_positional_token_exclusivity.json',
              encoding='utf-8') as f:
        excl_data = json.load(f)
    exclusive_tokens = excl_data['raw_pass']['top_exclusive']

    morph = Morphology()
    tx = Transcript()

    # Build per-line structures
    lines = []          # list of lists of token dicts
    line_meta = []      # metadata per line
    current_line = []
    prev_key = None
    current_folio = None
    current_section = None
    current_line_id = None

    for token in tx.currier_b():
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        if cls is None:
            continue

        key = (token.folio, token.line)
        if key != prev_key:
            if current_line:
                lines.append(current_line)
                line_meta.append({
                    'folio': current_folio,
                    'line': current_line_id,
                    'section': current_section,
                })
            current_line = []
            current_folio = token.folio
            current_section = token.section
            current_line_id = token.line
            prev_key = key

        m = morph.extract(token.word)
        role = class_to_role.get(cls, 'UNKNOWN')
        current_line.append({
            'word': token.word,
            'cls': cls,
            'role': role,
            'middle': m.middle if m.middle else '',
        })

    # Don't forget last line
    if current_line:
        lines.append(current_line)
        line_meta.append({
            'folio': current_folio,
            'line': current_line_id,
            'section': current_section,
        })

    # Expand forbidden MIDDLE pairs to class-level pairs
    middle_to_classes = defaultdict(set)
    for line in lines:
        for t in line:
            middle_to_classes[t['middle']].add(t['cls'])
    forbidden_class_pairs = set()
    for src_mid, tgt_mid in forbidden_middle_pairs:
        for sc in middle_to_classes.get(src_mid, set()):
            for tc in middle_to_classes.get(tgt_mid, set()):
                forbidden_class_pairs.add((sc, tc))

    # Filter to valid sections
    valid_lines = []
    valid_meta = []
    for line, meta in zip(lines, line_meta):
        if meta['section'] in VALID_SECTIONS:
            valid_lines.append(line)
            valid_meta.append(meta)

    # Section token counts
    sec_counts = Counter(m['section'] for m in valid_meta for _ in range(1))  # line count
    sec_tok_counts = Counter()
    for line, meta in zip(valid_lines, valid_meta):
        sec_tok_counts[meta['section']] += len(line)

    print(f"  {sum(len(l) for l in valid_lines)} tokens in {len(valid_lines)} lines")
    print(f"  Section line counts: {dict(Counter(m['section'] for m in valid_meta))}")
    print(f"  Section token counts: {dict(sec_tok_counts)}")
    print(f"  {len(forbidden_middle_pairs)} forbidden MIDDLE pairs -> {len(forbidden_class_pairs)} class pairs")

    return (valid_lines, valid_meta, token_to_class, class_to_role,
            forbidden_class_pairs, mandatory_bigrams, exclusive_tokens, morph)


# ════════════════════════════════════════════════════════════════
# S2: Interior transitions (H1) + self-loop rates (H2)
# ════════════════════════════════════════════════════════════════

def compute_jsd(p, q, epsilon=1e-10):
    """Jensen-Shannon divergence between two distributions."""
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def test_interior_transitions(lines, meta, class_to_role):
    """H1: Interior transitions section-dependent (permutation test on JSD).
       H2: Within-line self-loop rates section-dependent."""
    print("\nS2: Interior transitions + self-loop rates...")

    n_classes = 50  # classes are 1-indexed (1..49), use 50 for safe indexing

    # Build per-section WORK-zone transition matrices (positions 2 to N-2)
    section_transitions = defaultdict(lambda: np.zeros((n_classes, n_classes)))
    section_selfloops = defaultdict(lambda: Counter())  # role -> {self, other}

    for line, m in zip(lines, meta):
        sec = m['section']
        n = len(line)
        if n < 5:  # Need at least 5 tokens for meaningful WORK zone
            continue
        work_zone = line[2:n-2]  # positions 2 to N-3

        for i in range(len(work_zone) - 1):
            c1 = work_zone[i]['cls']
            c2 = work_zone[i+1]['cls']
            section_transitions[sec][c1, c2] += 1

        # Self-loop tracking by role
        for i in range(len(work_zone) - 1):
            role = work_zone[i]['role']
            if work_zone[i]['cls'] == work_zone[i+1]['cls']:
                section_selfloops[sec][('self', role)] += 1
            else:
                section_selfloops[sec][('other', role)] += 1

    # Active sections
    active_secs = sorted(s for s in section_transitions if section_transitions[s].sum() > 50)
    print(f"  Active sections for interior test: {active_secs}")

    if len(active_secs) < 2:
        return {'h1_pass': False, 'h2_pass': False, 'reason': 'insufficient_sections'}

    # H1: Pairwise JSD between section transition matrices
    real_jsds = []
    for i in range(len(active_secs)):
        for j in range(i+1, len(active_secs)):
            s1, s2 = active_secs[i], active_secs[j]
            p = section_transitions[s1].flatten()
            q = section_transitions[s2].flatten()
            real_jsds.append(compute_jsd(p, q))
    real_mean_jsd = np.mean(real_jsds)

    # Permutation test: shuffle section labels across lines
    all_line_indices = [(i, meta[i]['section']) for i in range(len(lines))
                        if meta[i]['section'] in active_secs and len(lines[i]) >= 5]
    perm_jsds = []
    for _ in range(N_PERMS):
        shuffled_secs = [s for _, s in all_line_indices]
        RNG.shuffle(shuffled_secs)
        perm_trans = defaultdict(lambda: np.zeros((50, 50)))
        for (idx, _), new_sec in zip(all_line_indices, shuffled_secs):
            line = lines[idx]
            n = len(line)
            work = line[2:n-2]
            for k in range(len(work) - 1):
                perm_trans[new_sec][work[k]['cls'], work[k+1]['cls']] += 1
        perm_jsd_vals = []
        for i in range(len(active_secs)):
            for j in range(i+1, len(active_secs)):
                s1, s2 = active_secs[i], active_secs[j]
                p = perm_trans[s1].flatten()
                q = perm_trans[s2].flatten()
                perm_jsd_vals.append(compute_jsd(p, q))
        perm_jsds.append(np.mean(perm_jsd_vals))

    perm_jsds = np.array(perm_jsds)
    h1_p = float(np.mean(perm_jsds >= real_mean_jsd))
    h1_pass = h1_p < 0.05

    print(f"  H1: mean JSD = {real_mean_jsd:.6f}, perm p = {h1_p:.4f} -> {'PASS' if h1_pass else 'FAIL'}")

    # H2: Self-loop rates by section and role (chi-squared)
    roles = ['AUXILIARY', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR']
    selfloop_table = np.zeros((len(active_secs), len(roles)))
    total_table = np.zeros((len(active_secs), len(roles)))
    for si, sec in enumerate(active_secs):
        for ri, role in enumerate(roles):
            selfloop_table[si, ri] = section_selfloops[sec].get(('self', role), 0)
            total_table[si, ri] = (section_selfloops[sec].get(('self', role), 0) +
                                   section_selfloops[sec].get(('other', role), 0))

    h2_pass = False
    h2_enrichment = {}
    h2_chi2 = np.nan
    h2_p = np.nan
    rates = np.zeros_like(selfloop_table)

    if total_table.sum() > 0:
        rates = np.divide(selfloop_table, total_table, where=total_table > 0,
                          out=np.zeros_like(selfloop_table))

        # Chi-squared on selfloop count table (sections x roles)
        # Only include roles with at least some occurrences
        col_mask = total_table.sum(axis=0) > 0
        if col_mask.sum() >= 2:
            sl_filtered = selfloop_table[:, col_mask].astype(int)
            nonsl_filtered = (total_table[:, col_mask] - selfloop_table[:, col_mask]).astype(int)
            # Stack: rows = [sec0_self, sec0_nonself, sec1_self, ...], cols = roles
            stacked = np.zeros((len(active_secs) * 2, int(col_mask.sum())), dtype=int)
            for si in range(len(active_secs)):
                stacked[si * 2] = sl_filtered[si]
                stacked[si * 2 + 1] = nonsl_filtered[si]
            # Remove any remaining zero-sum rows/cols
            row_ok = stacked.sum(axis=1) > 0
            col_ok = stacked.sum(axis=0) > 0
            if row_ok.sum() >= 4 and col_ok.sum() >= 2:
                try:
                    h2_chi2, h2_p, _, _ = stats.chi2_contingency(stacked[np.ix_(row_ok, col_ok)])
                except ValueError:
                    pass

        # Enrichment: >= 2 roles with max/min self-loop rate > 1.5
        enriched_roles = 0
        for ri, role in enumerate(roles):
            sec_rates = [float(rates[si, ri]) for si in range(len(active_secs))
                         if total_table[si, ri] >= 5]
            if len(sec_rates) >= 2 and min(sec_rates) > 0:
                ratio = max(sec_rates) / min(sec_rates)
                h2_enrichment[role] = float(ratio)
                if ratio >= 1.5:
                    enriched_roles += 1

        h2_pass = bool(not np.isnan(h2_p) and h2_p < 0.01 and enriched_roles >= 2)

    print(f"  H2: chi2={h2_chi2:.2f}, p={h2_p:.4f}, enriched roles={len([v for v in h2_enrichment.values() if v >= 1.5])}")
    print(f"      -> {'PASS' if h2_pass else 'FAIL'}")

    return {
        'h1': {
            'mean_jsd': float(real_mean_jsd),
            'perm_mean': float(perm_jsds.mean()),
            'perm_std': float(perm_jsds.std()),
            'p': float(h1_p),
            'n_lines': len(all_line_indices),
            'active_sections': active_secs,
        },
        'h1_pass': bool(h1_pass),
        'h2': {
            'chi2': float(h2_chi2) if not np.isnan(h2_chi2) else None,
            'p': float(h2_p) if not np.isnan(h2_p) else None,
            'enrichment_by_role': h2_enrichment,
            'selfloop_rates': {
                sec: {role: float(rates[si, ri]) if total_table[si, ri] > 0 else None
                      for ri, role in enumerate(roles)}
                for si, sec in enumerate(active_secs)
            } if total_table.sum() > 0 else {},
        },
        'h2_pass': bool(h2_pass),
    }


# ════════════════════════════════════════════════════════════════
# S3: Phase interleaving by section (H3)
# ════════════════════════════════════════════════════════════════

def test_phase_interleaving(lines, meta, class_to_role):
    """H3: KERNEL/LINK/FL alternation rate and sequential compliance per section."""
    print("\nS3: Phase interleaving by section...")

    # Map roles to phase groups for interleaving analysis
    # KERNEL = {AUXILIARY, ENERGY_OPERATOR}, LINK = {CORE_CONTROL, FREQUENT_OPERATOR}, FL = {FLOW_OPERATOR}
    def role_to_phase(role):
        if role in ('AUXILIARY', 'ENERGY_OPERATOR'):
            return 'KERNEL'
        elif role in ('CORE_CONTROL', 'FREQUENT_OPERATOR'):
            return 'LINK'
        elif role == 'FLOW_OPERATOR':
            return 'FL'
        return None

    section_alternations = defaultdict(list)
    section_compliance = defaultdict(lambda: {'compliant': 0, 'total': 0})

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        if len(line) < 4:
            continue

        # Get phase sequence (skip None)
        phases = []
        for t in line:
            ph = role_to_phase(t['role'])
            if ph:
                phases.append(ph)

        if len(phases) < 3:
            continue

        # Alternation rate: fraction of consecutive pairs that differ
        alternations = sum(1 for i in range(len(phases)-1) if phases[i] != phases[i+1])
        alt_rate = alternations / (len(phases) - 1)
        section_alternations[sec].append(alt_rate)

        # Sequential compliance: KERNEL before LINK in each half
        mid = len(phases) // 2
        first_half = phases[:mid]
        second_half = phases[mid:]
        for half in [first_half, second_half]:
            if len(half) < 2:
                continue
            first_kernel = next((i for i, p in enumerate(half) if p == 'KERNEL'), None)
            first_link = next((i for i, p in enumerate(half) if p == 'LINK'), None)
            section_compliance[sec]['total'] += 1
            if first_kernel is not None and first_link is not None and first_kernel < first_link:
                section_compliance[sec]['compliant'] += 1

    active_secs = sorted(s for s in section_alternations if len(section_alternations[s]) >= 20)

    if len(active_secs) < 2:
        return {'h3_pass': False, 'reason': 'insufficient_sections'}

    # Kruskal-Wallis on alternation rates
    groups = [section_alternations[s] for s in active_secs]
    kw_stat, kw_p = stats.kruskal(*groups)

    # Chi-squared on compliance
    comp_table = np.zeros((len(active_secs), 2))  # compliant, non-compliant
    for si, sec in enumerate(active_secs):
        comp_table[si, 0] = section_compliance[sec]['compliant']
        comp_table[si, 1] = section_compliance[sec]['total'] - section_compliance[sec]['compliant']

    chi2_comp, chi2_p = np.nan, np.nan
    if comp_table.sum() > 0 and comp_table.min(axis=0).sum() > 0:
        try:
            chi2_comp, chi2_p, _, _ = stats.chi2_contingency(comp_table)
        except ValueError:
            pass

    h3_pass = bool(kw_p < 0.01 or (not np.isnan(chi2_p) and chi2_p < 0.01))

    print(f"  H3: KW stat={kw_stat:.2f}, p={kw_p:.4f}; compliance chi2={chi2_comp:.2f}, p={chi2_p:.4f}")
    print(f"      -> {'PASS' if h3_pass else 'FAIL'}")

    return {
        'h3': {
            'alternation_kw_stat': float(kw_stat),
            'alternation_kw_p': float(kw_p),
            'compliance_chi2': float(chi2_comp) if not np.isnan(chi2_comp) else None,
            'compliance_p': float(chi2_p) if not np.isnan(chi2_p) else None,
            'section_mean_alternation': {s: float(np.mean(section_alternations[s]))
                                         for s in active_secs},
            'section_compliance_rate': {s: float(section_compliance[s]['compliant'] /
                                                  section_compliance[s]['total'])
                                         if section_compliance[s]['total'] > 0 else None
                                         for s in active_secs},
            'section_n_lines': {s: len(section_alternations[s]) for s in active_secs},
        },
        'h3_pass': bool(h3_pass),
    }


# ════════════════════════════════════════════════════════════════
# S4: Forbidden transition compliance by section (H4)
# ════════════════════════════════════════════════════════════════

def test_forbidden_compliance(lines, meta, forbidden_class_pairs):
    """H4: Forbidden transition violation rate section-dependent."""
    print("\nS4: Forbidden transition compliance...")

    section_eligible = Counter()
    section_violations = Counter()

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        for i in range(len(line) - 1):
            pair = (line[i]['cls'], line[i+1]['cls'])
            if pair in forbidden_class_pairs:
                section_eligible[sec] += 1
                section_violations[sec] += 1
            # Check if source class participates in ANY forbidden pair
            # "eligible" = source class has forbidden targets
            src = line[i]['cls']
            if any(s == src for s, _ in forbidden_class_pairs):
                section_eligible[sec] += 1
                if pair in forbidden_class_pairs:
                    pass  # already counted above

    # Recompute properly: eligible = transition where source has forbidden targets
    forbidden_sources = set(s for s, _ in forbidden_class_pairs)
    forbidden_by_source = defaultdict(set)
    for s, t in forbidden_class_pairs:
        forbidden_by_source[s].add(t)

    section_eligible = Counter()
    section_violations = Counter()
    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        for i in range(len(line) - 1):
            src = line[i]['cls']
            tgt = line[i+1]['cls']
            if src in forbidden_sources:
                section_eligible[sec] += 1
                if tgt in forbidden_by_source[src]:
                    section_violations[sec] += 1

    active_secs = sorted(s for s in section_eligible if section_eligible[s] >= 20)

    if len(active_secs) < 2:
        return {'h4_pass': False, 'reason': 'insufficient_data'}

    # Chi-squared: violated vs compliant per section
    table = np.zeros((len(active_secs), 2))
    rates = {}
    for si, sec in enumerate(active_secs):
        v = section_violations[sec]
        e = section_eligible[sec]
        table[si, 0] = v
        table[si, 1] = e - v
        rates[sec] = float(v / e) if e > 0 else 0.0

    chi2, p_val = np.nan, np.nan
    try:
        chi2, p_val, _, _ = stats.chi2_contingency(table)
    except ValueError:
        pass

    # Max/min ratio
    rate_vals = [rates[s] for s in active_secs if rates[s] > 0]
    max_min_ratio = max(rate_vals) / min(rate_vals) if len(rate_vals) >= 2 and min(rate_vals) > 0 else 0.0

    h4_pass = bool(not np.isnan(p_val) and p_val < 0.01 and max_min_ratio >= 1.5)

    print(f"  H4: chi2={chi2:.2f}, p={p_val:.4f}, max/min ratio={max_min_ratio:.2f}")
    print(f"      Rates: {rates}")
    print(f"      -> {'PASS' if h4_pass else 'FAIL'}")

    return {
        'h4': {
            'chi2': float(chi2) if not np.isnan(chi2) else None,
            'p': float(p_val) if not np.isnan(p_val) else None,
            'max_min_ratio': float(max_min_ratio),
            'section_rates': rates,
            'section_eligible': {s: int(section_eligible[s]) for s in active_secs},
            'section_violations': {s: int(section_violations[s]) for s in active_secs},
            'n_forbidden_class_pairs': len(forbidden_class_pairs),
        },
        'h4_pass': bool(h4_pass),
    }


# ════════════════════════════════════════════════════════════════
# S5: Within-zone ordering by section (H5)
# ════════════════════════════════════════════════════════════════

def test_zone_ordering(lines, meta):
    """H5: WORK zone EN token ordering emerges per section.
    Kendall's tau for EN class indices within WORK zone."""
    print("\nS5: Within-zone ordering...")

    section_taus = defaultdict(list)

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        n = len(line)
        if n < 6:  # Need enough for WORK zone
            continue

        # WORK zone: positions 2 to N-2
        work = line[2:n-2]
        en_positions = [(i, t['cls']) for i, t in enumerate(work) if t['role'] == 'ENERGY_OPERATOR']

        if len(en_positions) < 3:
            continue

        positions = [p for p, _ in en_positions]
        classes = [c for _, c in en_positions]
        tau, p = stats.kendalltau(positions, classes)
        if not np.isnan(tau):
            section_taus[sec].append(tau)

    active_secs = sorted(s for s in section_taus if len(section_taus[s]) >= 20)

    if len(active_secs) < 1:
        return {'h5_pass': False, 'reason': 'insufficient_data'}

    # Per-section one-sample t-test against 0, Bonferroni correction
    alpha_bonf = 0.05 / len(active_secs)
    section_results = {}
    h5_pass = False

    for sec in active_secs:
        taus = section_taus[sec]
        mean_tau = np.mean(taus)
        t_stat, p_val = stats.ttest_1samp(taus, 0)
        significant = bool(abs(mean_tau) > 0.05 and p_val < alpha_bonf)
        section_results[sec] = {
            'n': len(taus),
            'mean_tau': float(mean_tau),
            't_stat': float(t_stat),
            'p': float(p_val),
            'significant': significant,
        }
        if significant:
            h5_pass = True

    for sec, r in section_results.items():
        print(f"  H5 {sec}: tau={r['mean_tau']:.4f}, p={r['p']:.4f}, sig={r['significant']}")
    print(f"      -> {'PASS' if h5_pass else 'FAIL'}")

    return {
        'h5': {
            'section_results': section_results,
            'alpha_bonferroni': float(alpha_bonf),
        },
        'h5_pass': bool(h5_pass),
    }


# ════════════════════════════════════════════════════════════════
# S6: Boundary role distributions (H6, H7)
# ════════════════════════════════════════════════════════════════

def test_boundary_roles(lines, meta, class_to_role):
    """H6: Opener role distribution section-dependent.
       H7: Closer role distribution section-dependent."""
    print("\nS6: Boundary role distributions...")

    roles = ['AUXILIARY', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR']
    role_idx = {r: i for i, r in enumerate(roles)}

    section_opener_roles = defaultdict(Counter)
    section_closer_roles = defaultdict(Counter)

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        if len(line) < 2:
            continue

        opener_role = line[0]['role']
        closer_role = line[-1]['role']

        if opener_role in role_idx:
            section_opener_roles[sec][opener_role] += 1
        if closer_role in role_idx:
            section_closer_roles[sec][closer_role] += 1

    active_secs = sorted(s for s in section_opener_roles if sum(section_opener_roles[s].values()) >= 20)

    if len(active_secs) < 2:
        return {'h6_pass': False, 'h7_pass': False, 'reason': 'insufficient_sections'}

    def do_chi2_cramers(section_counts, label):
        table = np.zeros((len(active_secs), len(roles)))
        for si, sec in enumerate(active_secs):
            for ri, role in enumerate(roles):
                table[si, ri] = section_counts[sec].get(role, 0)

        # Remove zero columns
        col_mask = table.sum(axis=0) > 0
        table = table[:, col_mask]
        used_roles = [r for r, m in zip(roles, col_mask) if m]

        if table.shape[1] < 2:
            return None, None, None, {}, used_roles

        try:
            chi2, p_val, dof, expected = stats.chi2_contingency(table)
        except ValueError:
            return None, None, None, {}, used_roles

        n = table.sum()
        k = min(table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * k)) if n > 0 and k > 0 else 0.0

        dist = {}
        for si, sec in enumerate(active_secs):
            row_total = table[si].sum()
            dist[sec] = {r: float(table[si, ri] / row_total) if row_total > 0 else 0.0
                         for ri, r in enumerate(used_roles)}

        return float(chi2), float(p_val), float(cramers_v), dist, used_roles

    # H6: Opener roles
    h6_chi2, h6_p, h6_v, h6_dist, h6_roles = do_chi2_cramers(section_opener_roles, "opener")
    h6_pass = bool(h6_p is not None and h6_p < 0.001 and h6_v >= 0.05)

    # H7: Closer roles
    h7_chi2, h7_p, h7_v, h7_dist, h7_roles = do_chi2_cramers(section_closer_roles, "closer")
    h7_pass = bool(h7_p is not None and h7_p < 0.001 and h7_v >= 0.05)

    print(f"  H6 (opener): chi2={h6_chi2}, p={h6_p}, V={h6_v} -> {'PASS' if h6_pass else 'FAIL'}")
    print(f"  H7 (closer): chi2={h7_chi2}, p={h7_p}, V={h7_v} -> {'PASS' if h7_pass else 'FAIL'}")

    return {
        'h6': {
            'chi2': h6_chi2, 'p': h6_p, 'cramers_v': h6_v,
            'distributions': h6_dist, 'roles_used': h6_roles,
        },
        'h6_pass': bool(h6_pass),
        'h7': {
            'chi2': h7_chi2, 'p': h7_p, 'cramers_v': h7_v,
            'distributions': h7_dist, 'roles_used': h7_roles,
        },
        'h7_pass': bool(h7_pass),
    }


# ════════════════════════════════════════════════════════════════
# S7: Line length + mandatory bigram rates (H8, H9)
# ════════════════════════════════════════════════════════════════

def test_line_length_and_bigrams(lines, meta, mandatory_bigrams):
    """H8: Section modulates line length beyond folio.
       H9: Mandatory bigram rates section-dependent."""
    print("\nS7: Line length + bigram rates...")

    # H8: Line length by section
    section_lengths = defaultdict(list)
    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        section_lengths[sec].append(len(line))

    active_secs = sorted(s for s in section_lengths if len(section_lengths[s]) >= 20)

    if len(active_secs) < 2:
        return {'h8_pass': False, 'h9_pass': False, 'reason': 'insufficient_sections'}

    # Kruskal-Wallis on line length
    groups = [section_lengths[s] for s in active_secs]
    kw_stat, kw_p = stats.kruskal(*groups)

    # Eta-squared (R²) for section effect
    all_lengths = np.concatenate(groups)
    grand_mean = all_lengths.mean()
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = np.sum((all_lengths - grand_mean)**2)
    eta2 = float(ss_between / ss_total) if ss_total > 0 else 0.0

    h8_pass = bool(kw_p < 0.001 and eta2 >= 0.03)

    print(f"  H8: KW stat={kw_stat:.2f}, p={kw_p:.6f}, eta2={eta2:.4f}")
    print(f"      Means: { {s: f'{np.mean(section_lengths[s]):.1f}' for s in active_secs} }")
    print(f"      -> {'PASS' if h8_pass else 'FAIL'}")

    # H9: Mandatory bigram rates by section
    # Select top bigrams with >= 20 global occurrences
    # Select bigrams with sufficient global count; mandatory bigrams are rare by nature
    top_bigrams = sorted([b for b in mandatory_bigrams if b['observed'] >= 5],
                         key=lambda x: -x['observed'])[:10]

    if len(top_bigrams) < 3:
        print(f"  H9: only {len(top_bigrams)} bigrams with >=5 occurrences, need >=3")
        return {
            'h8': {'kw_stat': float(kw_stat), 'kw_p': float(kw_p), 'eta2': eta2,
                   'section_means': {s: float(np.mean(section_lengths[s])) for s in active_secs}},
            'h8_pass': bool(h8_pass),
            'h9_pass': False, 'h9': {'reason': 'insufficient_bigrams'},
        }

    # Count each bigram per section
    section_bigram_counts = {s: Counter() for s in active_secs}
    section_total_bigrams = Counter()

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in active_secs:
            continue
        for i in range(len(line) - 1):
            section_total_bigrams[sec] += 1
            for bi, bg in enumerate(top_bigrams):
                if line[i]['word'] == bg['token_a'] and line[i+1]['word'] == bg['token_b']:
                    section_bigram_counts[sec][bi] += 1

    # Chi-squared per bigram, Bonferroni correction
    alpha_bonf = 0.05 / len(top_bigrams)
    significant_bigrams = 0
    bigram_results = []

    for bi, bg in enumerate(top_bigrams):
        # Build 2xN table: present/absent per section
        table = np.zeros((len(active_secs), 2))
        for si, sec in enumerate(active_secs):
            present = section_bigram_counts[sec].get(bi, 0)
            absent = section_total_bigrams[sec] - present
            table[si, 0] = present
            table[si, 1] = absent

        try:
            chi2, p_val, _, _ = stats.chi2_contingency(table)
        except ValueError:
            chi2, p_val = 0.0, 1.0

        sig = bool(p_val < alpha_bonf)
        if sig:
            significant_bigrams += 1

        bigram_results.append({
            'token_a': bg['token_a'],
            'token_b': bg['token_b'],
            'global_observed': bg['observed'],
            'chi2': float(chi2),
            'p': float(p_val),
            'significant': sig,
            'section_rates': {s: float(section_bigram_counts[s].get(bi, 0) / section_total_bigrams[s])
                              if section_total_bigrams[s] > 0 else 0.0
                              for s in active_secs},
        })

    h9_pass = bool(significant_bigrams >= 3)

    print(f"  H9: {significant_bigrams}/{len(top_bigrams)} bigrams significant at alpha={alpha_bonf:.4f}")
    print(f"      -> {'PASS' if h9_pass else 'FAIL'}")

    return {
        'h8': {
            'kw_stat': float(kw_stat),
            'kw_p': float(kw_p),
            'eta2': eta2,
            'section_means': {s: float(np.mean(section_lengths[s])) for s in active_secs},
            'section_n': {s: len(section_lengths[s]) for s in active_secs},
        },
        'h8_pass': bool(h8_pass),
        'h9': {
            'n_tested': len(top_bigrams),
            'n_significant': significant_bigrams,
            'alpha_bonferroni': float(alpha_bonf),
            'bigram_results': bigram_results,
        },
        'h9_pass': bool(h9_pass),
    }


# ════════════════════════════════════════════════════════════════
# S8: Positional exclusivity retention (H10)
# ════════════════════════════════════════════════════════════════

def test_exclusivity_retention(lines, meta, exclusive_tokens):
    """H10 (null): positional exclusivity is section-invariant.
    Check that >= 80% of 192 globally exclusive tokens retain exclusivity per section."""
    print("\nS8: Exclusivity retention...")

    # Build exclusive token set with their exclusive zone
    excl_map = {}
    for et in exclusive_tokens:
        token = et['token']
        # Determine exclusive zone: zero_zones tells which zones have 0 count
        # The token is exclusive to the zone(s) where it appears
        zones = ['INITIAL', 'MEDIAL', 'FINAL']
        zone_counts = [et.get('INITIAL', 0), et.get('MEDIAL', 0), et.get('FINAL', 0)]
        nonzero = [z for z, c in zip(zones, zone_counts) if c > 0]
        if len(nonzero) == 1:
            excl_map[token] = nonzero[0]

    if not excl_map:
        return {'h10_pass': False, 'reason': 'no_exclusive_tokens_found'}

    # Per-section zone counts for exclusive tokens
    section_zone_counts = defaultdict(lambda: defaultdict(Counter))
    # section -> token -> Counter(zone -> count)

    for line, m in zip(lines, meta):
        sec = m['section']
        if sec not in VALID_SECTIONS:
            continue
        n = len(line)
        for pos, t in enumerate(line):
            if t['word'] not in excl_map:
                continue
            if n == 1:
                zone = 'INITIAL'
            elif pos == 0:
                zone = 'INITIAL'
            elif pos == n - 1:
                zone = 'FINAL'
            else:
                zone = 'MEDIAL'
            section_zone_counts[sec][t['word']][zone] += 1

    active_secs = sorted(s for s in section_zone_counts if len(section_zone_counts[s]) >= 5)

    if len(active_secs) < 2:
        return {'h10_pass': False, 'reason': 'insufficient_sections'}

    # For each section, count how many exclusive tokens retain exclusivity
    section_retention = {}
    for sec in active_secs:
        retained = 0
        tested = 0
        for token, expected_zone in excl_map.items():
            if token not in section_zone_counts[sec]:
                continue
            counts = section_zone_counts[sec][token]
            total = sum(counts.values())
            if total < 2:  # Need at least 2 occurrences
                continue
            tested += 1
            nonzero_zones = [z for z, c in counts.items() if c > 0]
            if len(nonzero_zones) == 1 and nonzero_zones[0] == expected_zone:
                retained += 1
        retention_rate = retained / tested if tested > 0 else 1.0
        section_retention[sec] = {
            'tested': tested,
            'retained': retained,
            'rate': float(retention_rate),
        }

    # H10 PASS (null confirmed) if >= 80% retention in all sections
    all_above_80 = all(section_retention[s]['rate'] >= 0.80 for s in active_secs
                       if section_retention[s]['tested'] >= 5)
    h10_pass = bool(all_above_80)

    for sec, r in section_retention.items():
        print(f"  H10 {sec}: {r['rate']:.1%} ({r['retained']}/{r['tested']})")
    print(f"       -> {'PASS (null confirmed)' if h10_pass else 'FAIL (exclusivity breaks)'}")

    return {
        'h10': {
            'n_global_exclusive': len(excl_map),
            'section_retention': section_retention,
        },
        'h10_pass': bool(h10_pass),
    }


# ════════════════════════════════════════════════════════════════
# S9: Integrated verdict
# ════════════════════════════════════════════════════════════════

def compute_verdict(results):
    """Compute verdict from H1-H10 results."""
    part_a = sum(1 for h in ['h1', 'h2', 'h3', 'h4', 'h5']
                 if results.get(f'{h}_pass', False))
    part_b = sum(1 for h in ['h6', 'h7', 'h8', 'h9', 'h10']
                 if results.get(f'{h}_pass', False))

    if part_a <= 1 and part_b <= 1:
        verdict = 'SECTION_UNIVERSAL'
    elif part_a <= 1 and part_b >= 3:
        verdict = 'BOUNDARY_ONLY'
    elif part_a >= 3 and part_b <= 1:
        verdict = 'INTERIOR_ONLY'
    elif part_a >= 3 and part_b >= 3:
        verdict = 'DEEP_PARAMETERIZATION'
    else:
        verdict = 'MIXED'

    return {
        'verdict': verdict,
        'part_a_pass': part_a,
        'part_b_pass': part_b,
        'total_pass': part_a + part_b,
        'hypotheses': {
            f'H{i+1}': bool(results.get(f'h{i+1}_pass', False))
            for i in range(10)
        },
    }


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Phase 365: Section-Parameterized Line Grammar")
    print("=" * 60)

    (lines, meta, token_to_class, class_to_role,
     forbidden_class_pairs, mandatory_bigrams, exclusive_tokens, morph) = load_data()

    results = {}

    # Part A: Interior parameterization
    r = test_interior_transitions(lines, meta, class_to_role)
    results.update(r)

    r = test_phase_interleaving(lines, meta, class_to_role)
    results.update(r)

    r = test_forbidden_compliance(lines, meta, forbidden_class_pairs)
    results.update(r)

    r = test_zone_ordering(lines, meta)
    results.update(r)

    # Part B: Boundary parameterization
    r = test_boundary_roles(lines, meta, class_to_role)
    results.update(r)

    r = test_line_length_and_bigrams(lines, meta, mandatory_bigrams)
    results.update(r)

    r = test_exclusivity_retention(lines, meta, exclusive_tokens)
    results.update(r)

    # Verdict
    verdict = compute_verdict(results)
    results['verdict'] = verdict

    print("\n" + "=" * 60)
    print(f"VERDICT: {verdict['verdict']}")
    print(f"Part A (interior): {verdict['part_a_pass']}/5")
    print(f"Part B (boundary): {verdict['part_b_pass']}/5")
    for h, p in verdict['hypotheses'].items():
        print(f"  {h}: {'PASS' if p else 'FAIL'}")
    print("=" * 60)

    # Save
    out_path = RESULTS_DIR / 'section_line_grammar.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
