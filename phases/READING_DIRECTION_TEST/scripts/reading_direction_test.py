#!/usr/bin/env python3
"""
Phase 399: READING_DIRECTION_TEST
==================================
Tests whether Currier B tokens read left-to-right (LTR), right-to-left (RTL),
or boundary-inward within lines. LTR has been assumed but never formally tested.

Motivation:
  - C391: H(X|past) = H(X|future) — symmetric conditional entropy
  - C608: Rejected LTR causation
  - C1034: Symmetric (bidirectional) forbidden pairs FIX the generative model
  - C886: Transition probabilities are directional (KL=89.2), but direction unknown
  - External: voynich-toolkit found character-level RTL (z=22.97)

7-Test Battery:
  T1: Forbidden pair landscape (LTR vs RTL) — DECISIVE
  T2: MI asymmetry direction (extends C1024) — DECISIVE
  T3: PREFIX positional coherence — DECISIVE
  T4: Transition matrix spectral properties — DIAGNOSTIC
  T5: Per-position entropy profile — DIAGNOSTIC (boundary-inward test)
  T6: CC positional role — SUPPORTING
  T7: Vocabulary gradient direction — SUPPORTING
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

ROLE_CLASSES = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}

CLASS_TO_ROLE = {}
for role, classes in ROLE_CLASSES.items():
    for c in classes:
        CLASS_TO_ROLE[c] = role

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_MACRO = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = state

# PREFIX morphological families (shared initial consonant)
PREFIX_FAMILIES = {
    'ch_family': {'ch'},
    'sh_family': {'sh'},
    'qo_family': {'qo'},
    'ok_family': {'ok', 'ol', 'ot', 'or'},
    'da_family': {'da', 'dch'},
    'sa_family': {'sa', 'so'},
    'l_family':  {'lk', 'lch', 'lsh'},
    'k_family':  {'ke', 'ka', 'ko'},
    'p_family':  {'po', 'pch'},
    't_family':  {'ta', 'tch', 'to'},
    'a_family':  {'al', 'ar'},
}

FORBIDDEN_THRESHOLD = 10  # Phase 15A: min degree for forbidden pair detection

N_CLASSES = 49


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens grouped by (folio, line), with class/prefix/middle/suffix."""
    print("Loading data...")

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    morph = Morphology()

    lines = defaultdict(list)
    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        if cls is None:
            continue
        m = morph.extract(token.word)
        prefix = m.prefix if m else None
        middle = m.middle if m else token.word
        suffix = m.suffix if m else None

        lines[(token.folio, token.line)].append({
            'word': token.word,
            'cls': cls,
            'role': CLASS_TO_ROLE.get(cls, 'UNK'),
            'macro': CLASS_TO_MACRO.get(cls, 'UNK'),
            'prefix': prefix or 'BARE',
            'middle': middle or token.word,
            'suffix': suffix or 'BARE',
            'folio': token.folio,
            'line': token.line,
        })

    # Sort line keys for deterministic ordering
    sorted_keys = sorted(lines.keys())

    n_tokens = sum(len(lines[k]) for k in sorted_keys)
    print(f"  {n_tokens} tokens in {len(sorted_keys)} lines")
    return dict(lines), sorted_keys, token_to_class, morph


# ── Utilities ────────────────────────────────────────────────────────

def jsd(p, q):
    """Jensen-Shannon divergence between two distributions (bits)."""
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    m_arr = 0.5 * (p + q)
    return float(0.5 * _kl(p, m_arr) + 0.5 * _kl(q, m_arr))


def _kl(p, q):
    """KL divergence (bits)."""
    return float(np.sum(p * np.log2(p / q)))


def shannon_entropy(counts):
    """Shannon entropy from a Counter or dict of counts (bits)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def build_class_transitions(lines, keys, reverse=False):
    """Build 49x49 class transition matrix from within-line consecutive pairs.
    If reverse=True, read each line right-to-left."""
    trans = np.zeros((N_CLASSES, N_CLASSES))
    for key in keys:
        seq = [t['cls'] for t in lines[key]]
        if reverse:
            seq = list(reversed(seq))
        for i in range(len(seq) - 1):
            trans[seq[i] - 1, seq[i + 1] - 1] += 1
    return trans


def build_middle_transitions(lines, keys, morph, reverse=False):
    """Build MIDDLE-to-MIDDLE transition counts.
    Returns: counts dict {(src, tgt): count}, out_degree, in_degree."""
    counts = Counter()
    for key in keys:
        toks = lines[key]
        middles = [t['middle'] for t in toks]
        if reverse:
            middles = list(reversed(middles))
        for i in range(len(middles) - 1):
            counts[(middles[i], middles[i + 1])] += 1

    out_degree = Counter()
    in_degree = Counter()
    for (src, tgt), c in counts.items():
        out_degree[src] += c
        in_degree[tgt] += c

    return counts, out_degree, in_degree


def detect_forbidden_pairs(counts, out_degree, in_degree, threshold=FORBIDDEN_THRESHOLD):
    """Phase 15A criteria: pair is forbidden if count(A->B)=0
    AND out_degree(A) > threshold AND in_degree(B) > threshold."""
    active_middles = set()
    for mid in set(out_degree.keys()) | set(in_degree.keys()):
        if out_degree.get(mid, 0) > threshold and in_degree.get(mid, 0) > threshold:
            active_middles.add(mid)

    forbidden = []
    for src in active_middles:
        for tgt in active_middles:
            if src != tgt and counts.get((src, tgt), 0) == 0:
                forbidden.append((src, tgt))
    return forbidden, active_middles


def compute_mi(pairs):
    """Compute mutual information I(X; Y) from list of (x, y) pairs (bits)."""
    xy_counts = Counter(pairs)
    x_counts = Counter(p[0] for p in pairs)
    y_counts = Counter(p[1] for p in pairs)
    n = len(pairs)
    if n == 0:
        return 0.0

    mi = 0.0
    for (x, y), count in xy_counts.items():
        p_xy = count / n
        p_x = x_counts[x] / n
        p_y = y_counts[y] / n
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


# ── T1: Forbidden Pair Landscape ─────────────────────────────────────

def run_t1(lines, keys, morph):
    """Compare forbidden pair landscapes under LTR vs RTL."""
    print("\n" + "=" * 60)
    print("T1: Forbidden Pair Landscape Reversal")
    print("=" * 60)

    # LTR forbidden pairs
    ltr_counts, ltr_out, ltr_in = build_middle_transitions(lines, keys, morph, reverse=False)
    ltr_forbidden, ltr_active = detect_forbidden_pairs(ltr_counts, ltr_out, ltr_in)

    # RTL forbidden pairs
    rtl_counts, rtl_out, rtl_in = build_middle_transitions(lines, keys, morph, reverse=True)
    rtl_forbidden, rtl_active = detect_forbidden_pairs(rtl_counts, rtl_out, rtl_in)

    ltr_set = set(ltr_forbidden)
    rtl_set = set(rtl_forbidden)

    # Direct overlap: same (A, B) appears in both
    direct_overlap = ltr_set & rtl_set

    # Reverse overlap: LTR has (A, B), RTL has (B, A)
    ltr_reversed = {(b, a) for (a, b) in ltr_set}
    reverse_overlap = ltr_reversed & rtl_set

    # Symmetric pairs in each set
    ltr_symmetric = {(a, b) for (a, b) in ltr_set if (b, a) in ltr_set}
    rtl_symmetric = {(a, b) for (a, b) in rtl_set if (b, a) in rtl_set}

    # Jaccard similarity
    union = ltr_set | rtl_set
    jaccard = len(direct_overlap) / len(union) if union else 0

    # Load known 17 forbidden pairs for validation
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        known = json.load(f)
    known_pairs_raw = set((t['source'], t['target']) for t in known['transitions'])

    # Phase 15A used full token stems (e.g., "shey") not Morphology-extracted MIDDLEs
    # (e.g., "ey"). Check at both levels.
    known_recovered = known_pairs_raw & ltr_set
    known_in_rtl = known_pairs_raw & rtl_set
    known_reversed_in_rtl = {(b, a) for (a, b) in known_pairs_raw} & rtl_set

    # Also check at class level using C783's 17 class-level forbidden pairs
    CLASS_FORBIDDEN_PAIRS = [
        (12, 23), (12, 9), (17, 23), (17, 9),
        (10, 12), (10, 17), (11, 12), (11, 17),
        (10, 23), (10, 9), (11, 23), (11, 9),
        (32, 12), (32, 17), (31, 12), (31, 17),
        (23, 9)
    ]

    # Build class-level transition counts
    ltr_class_counts = Counter()
    rtl_class_counts = Counter()
    for key in keys:
        seq = [t['cls'] for t in lines[key]]
        for i in range(len(seq) - 1):
            ltr_class_counts[(seq[i], seq[i + 1])] += 1
        rev_seq = list(reversed(seq))
        for i in range(len(rev_seq) - 1):
            rtl_class_counts[(rev_seq[i], rev_seq[i + 1])] += 1

    # Check C783 forbidden pairs in both directions
    class_ltr_zero = sum(1 for p in CLASS_FORBIDDEN_PAIRS if ltr_class_counts.get(p, 0) == 0)
    class_rtl_zero = sum(1 for p in CLASS_FORBIDDEN_PAIRS if rtl_class_counts.get(p, 0) == 0)
    class_reversed_rtl_zero = sum(1 for (a, b) in CLASS_FORBIDDEN_PAIRS
                                  if rtl_class_counts.get((b, a), 0) == 0)

    # Count violations of C783 pairs in each direction
    class_ltr_violations = sum(ltr_class_counts.get(p, 0) for p in CLASS_FORBIDDEN_PAIRS)
    class_rtl_violations = sum(rtl_class_counts.get(p, 0) for p in CLASS_FORBIDDEN_PAIRS)
    class_reversed_violations = sum(rtl_class_counts.get((b, a), 0)
                                    for (a, b) in CLASS_FORBIDDEN_PAIRS)

    # Macro-state categorization of forbidden pairs
    def categorize_pair(src, tgt, trans_counts, out_deg, in_deg):
        """Determine macro-state category of a forbidden pair by checking
        what classes the MIDDLEs belong to in the token data."""
        return f"{src} -> {tgt}"

    print(f"  LTR: {len(ltr_forbidden)} forbidden pairs ({len(ltr_active)} active MIDDLEs)")
    print(f"  RTL: {len(rtl_forbidden)} forbidden pairs ({len(rtl_active)} active MIDDLEs)")
    print(f"  Direct overlap: {len(direct_overlap)}")
    print(f"  Reverse overlap (LTR A->B matches RTL B->A): {len(reverse_overlap)}")
    print(f"  LTR symmetric pairs: {len(ltr_symmetric)}")
    print(f"  RTL symmetric pairs: {len(rtl_symmetric)}")
    print(f"  Jaccard similarity: {jaccard:.4f}")
    print(f"  Known 17 (MIDDLE-level) recovered in LTR: {len(known_recovered)}/17")
    print(f"    (Note: Phase 15A used token stems, not Morphology MIDDLEs — mismatch expected)")
    print(f"\n  CLASS-LEVEL forbidden pair check (C783):")
    print(f"    C783 pairs with 0 count under LTR: {class_ltr_zero}/17")
    print(f"    C783 pairs with 0 count under RTL: {class_rtl_zero}/17")
    print(f"    C783 reversed pairs with 0 count under RTL: {class_reversed_rtl_zero}/17")
    print(f"    C783 pair violations under LTR: {class_ltr_violations}")
    print(f"    C783 pair violations under RTL: {class_rtl_violations}")
    print(f"    C783 reversed pair violations under RTL: {class_reversed_violations}")
    print(f"\n  MATHEMATICAL NOTE: Forbidden pair landscapes under LTR and RTL are")
    print(f"  exact mirror images by construction. This test cannot distinguish")
    print(f"  directions. The key finding is the SYMMETRY FRACTION: {len(ltr_symmetric)}/{len(ltr_forbidden)}")
    print(f"  = {len(ltr_symmetric)/len(ltr_forbidden)*100:.1f}% of forbidden pairs are adjacency constraints")
    print(f"  (forbidden in BOTH directions), explaining why C1034's symmetric model works.")

    # LTR-only and RTL-only forbidden pairs
    ltr_only = ltr_set - rtl_set
    rtl_only = rtl_set - ltr_set

    # Verdict
    if len(ltr_forbidden) > len(rtl_forbidden) * 1.3:
        verdict = "LTR_MORE_CONSTRAINED"
    elif len(rtl_forbidden) > len(ltr_forbidden) * 1.3:
        verdict = "RTL_MORE_CONSTRAINED"
    elif jaccard > 0.6:
        verdict = "NEUTRAL_HIGH_OVERLAP"
    elif len(reverse_overlap) > len(direct_overlap):
        verdict = "REVERSE_CORRESPONDENCE"
    else:
        verdict = "NEUTRAL_DIVERGENT"

    print(f"  Verdict: {verdict}")

    return {
        'n_ltr_forbidden': len(ltr_forbidden),
        'n_rtl_forbidden': len(rtl_forbidden),
        'n_ltr_active': len(ltr_active),
        'n_rtl_active': len(rtl_active),
        'n_direct_overlap': len(direct_overlap),
        'n_reverse_overlap': len(reverse_overlap),
        'n_ltr_symmetric': len(ltr_symmetric),
        'n_rtl_symmetric': len(rtl_symmetric),
        'symmetry_fraction': round(len(ltr_symmetric) / len(ltr_forbidden), 4) if ltr_forbidden else 0,
        'jaccard': round(jaccard, 4),
        'known_17_middle_recovered_ltr': len(known_recovered),
        'class_level': {
            'c783_zero_ltr': class_ltr_zero,
            'c783_zero_rtl': class_rtl_zero,
            'c783_reversed_zero_rtl': class_reversed_rtl_zero,
            'c783_violations_ltr': class_ltr_violations,
            'c783_violations_rtl': class_rtl_violations,
            'c783_reversed_violations_rtl': class_reversed_violations,
        },
        'ltr_only_count': len(ltr_only),
        'rtl_only_count': len(rtl_only),
        'mathematical_note': 'Forbidden landscapes under LTR/RTL are exact mirror images by construction. '
                             'This test cannot distinguish directions. Key finding: symmetry_fraction shows '
                             'what proportion are adjacency constraints (forbidden in both directions).',
        'verdict': verdict,
    }


# ── T2: MI Asymmetry Direction ──────────────────────────────────────

def run_t2(lines, keys):
    """Re-compute C1024 T2 MI decomposition and analyze direction."""
    print("\n" + "=" * 60)
    print("T2: MI Asymmetry Direction (extends C1024)")
    print("=" * 60)

    # Collect forward and backward pairs for each component
    results = {}
    for component in ['prefix', 'middle', 'suffix']:
        forward_pairs = []
        backward_pairs = []

        for key in keys:
            toks = lines[key]
            for i in range(len(toks)):
                comp_val = toks[i][component]
                if i < len(toks) - 1:
                    forward_pairs.append((comp_val, toks[i + 1]['cls']))
                if i > 0:
                    backward_pairs.append((comp_val, toks[i - 1]['cls']))

        mi_fwd = compute_mi(forward_pairs)
        mi_bwd = compute_mi(backward_pairs)
        asymmetry = mi_fwd - mi_bwd

        results[component] = {
            'mi_forward': round(mi_fwd, 6),
            'mi_backward': round(mi_bwd, 6),
            'asymmetry': round(asymmetry, 6),
            'n_pairs': len(forward_pairs),
        }

        print(f"  {component:8s}: MI_fwd={mi_fwd:.4f} MI_bwd={mi_bwd:.4f} "
              f"asym={asymmetry:+.4f}")

    # Under RTL, forward/backward swap:
    # RTL_asymmetry = MI_bwd - MI_fwd = -LTR_asymmetry (by construction)
    for comp in ['prefix', 'middle', 'suffix']:
        results[comp]['rtl_asymmetry'] = round(-results[comp]['asymmetry'], 6)

    # Null control: shuffle within-line token order, re-compute MI
    print("\n  Running null control (100 shuffles)...")
    null_asym = {'prefix': [], 'middle': [], 'suffix': []}
    rng = np.random.RandomState(42)
    for trial in range(100):
        shuffled_lines = {}
        for key in keys:
            toks = list(lines[key])
            rng.shuffle(toks)
            shuffled_lines[key] = toks

        for component in ['prefix', 'middle', 'suffix']:
            fwd_pairs = []
            bwd_pairs = []
            for key in keys:
                toks = shuffled_lines[key]
                for i in range(len(toks)):
                    comp_val = toks[i][component]
                    if i < len(toks) - 1:
                        fwd_pairs.append((comp_val, toks[i + 1]['cls']))
                    if i > 0:
                        bwd_pairs.append((comp_val, toks[i - 1]['cls']))
            null_asym[component].append(compute_mi(fwd_pairs) - compute_mi(bwd_pairs))

    for comp in ['prefix', 'middle', 'suffix']:
        null_mean = np.mean(null_asym[comp])
        null_sd = np.std(null_asym[comp])
        real_asym = results[comp]['asymmetry']
        z = (real_asym - null_mean) / null_sd if null_sd > 0 else 0
        results[comp]['null_mean'] = round(float(null_mean), 6)
        results[comp]['null_sd'] = round(float(null_sd), 6)
        results[comp]['z_score'] = round(float(z), 2)
        genuine_pct = ((abs(real_asym) - abs(null_mean)) / abs(real_asym) * 100
                       if abs(real_asym) > 0 else 0)
        results[comp]['genuine_pct'] = round(genuine_pct, 1)

        print(f"  {comp:8s}: null_mean={null_mean:+.4f} z={z:+.1f} "
              f"genuine={genuine_pct:.0f}%")

    # MIDDLE is the primary directional carrier (4x PREFIX)
    mid_asym = results['middle']['asymmetry']
    mid_z = results['middle']['z_score']

    if mid_asym > 0 and mid_z > 2:
        verdict = "LTR_FORWARD_BIASED"
        direction_vote = "LTR"
    elif mid_asym < 0 and mid_z < -2:
        verdict = "RTL_FORWARD_BIASED"
        direction_vote = "RTL"
    else:
        verdict = "WEAK_ASYMMETRY"
        direction_vote = "NEUTRAL"

    results['verdict'] = verdict
    results['direction_vote'] = direction_vote
    print(f"  Verdict: {verdict} (vote: {direction_vote})")

    return results


# ── T3: PREFIX Positional Coherence ──────────────────────────────────

def run_t3(lines, keys):
    """PREFIX positional analysis under LTR vs RTL."""
    print("\n" + "=" * 60)
    print("T3: PREFIX Positional Coherence")
    print("=" * 60)

    # Compute mean position for each PREFIX under LTR
    prefix_positions = defaultdict(list)
    for key in keys:
        toks = lines[key]
        n = len(toks)
        if n < 2:
            continue
        for i, t in enumerate(toks):
            pos = i / (n - 1)  # [0, 1]
            prefix_positions[t['prefix']].append(pos)

    # Filter to PREFIXes with enough observations
    MIN_OBS = 50
    valid_prefixes = {p: positions for p, positions in prefix_positions.items()
                      if len(positions) >= MIN_OBS}

    # LTR statistics
    ltr_stats = {}
    for pfx, positions in valid_prefixes.items():
        ltr_stats[pfx] = {
            'mean_pos': round(np.mean(positions), 4),
            'std_pos': round(np.std(positions), 4),
            'n': len(positions),
        }

    # RTL statistics (position = 1 - ltr_position)
    rtl_stats = {}
    for pfx, positions in valid_prefixes.items():
        rtl_positions = [1 - p for p in positions]
        rtl_stats[pfx] = {
            'mean_pos': round(np.mean(rtl_positions), 4),
            'std_pos': round(np.std(rtl_positions), 4),
            'n': len(rtl_positions),
        }

    # Zone classification (C1001 method)
    def classify_zone(mean_pos):
        if mean_pos < 0.45:
            return 'INITIAL'
        elif mean_pos > 0.55:
            return 'FINAL'
        else:
            return 'CENTRAL'

    for pfx in valid_prefixes:
        ltr_stats[pfx]['zone'] = classify_zone(ltr_stats[pfx]['mean_pos'])
        rtl_stats[pfx]['zone'] = classify_zone(rtl_stats[pfx]['mean_pos'])

    # Functional coherence: do morphological PREFIX families cluster in same zone?
    def compute_family_coherence(stats):
        """For each PREFIX family, compute zone uniformity."""
        scores = []
        for family_name, members in PREFIX_FAMILIES.items():
            family_zones = [stats[pfx]['zone'] for pfx in members if pfx in stats]
            if len(family_zones) >= 2:
                # Uniformity = fraction of majority zone
                zone_counts = Counter(family_zones)
                uniformity = zone_counts.most_common(1)[0][1] / len(family_zones)
                scores.append(uniformity)
        return np.mean(scores) if scores else 0

    ltr_coherence = compute_family_coherence(ltr_stats)
    rtl_coherence = compute_family_coherence(rtl_stats)

    # Within-zone position variance (lower = tighter clustering)
    def compute_zone_variance(stats, positions_dict):
        """Mean within-zone position variance."""
        zone_variances = defaultdict(list)
        for pfx, s in stats.items():
            zone_variances[s['zone']].append(np.var(positions_dict[pfx]))
        return {z: round(np.mean(v), 6) for z, v in zone_variances.items()}

    ltr_zone_var = compute_zone_variance(ltr_stats, valid_prefixes)
    rtl_positions_dict = {pfx: [1 - p for p in positions]
                          for pfx, positions in valid_prefixes.items()}
    rtl_zone_var = compute_zone_variance(rtl_stats, rtl_positions_dict)

    # R-squared: PREFIX -> position
    all_positions = []
    all_prefix_means = []
    for pfx, positions in valid_prefixes.items():
        mean = np.mean(positions)
        for p in positions:
            all_positions.append(p)
            all_prefix_means.append(mean)
    all_positions = np.array(all_positions)
    all_prefix_means = np.array(all_prefix_means)
    ss_res = np.sum((all_positions - all_prefix_means) ** 2)
    ss_tot = np.sum((all_positions - np.mean(all_positions)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Print zone assignments
    print(f"\n  LTR zones:")
    for zone in ['INITIAL', 'CENTRAL', 'FINAL']:
        members = [p for p, s in ltr_stats.items() if s['zone'] == zone]
        members.sort(key=lambda p: ltr_stats[p]['mean_pos'])
        parts = [f"{p}({ltr_stats[p]['mean_pos']:.2f})" for p in members]
        print(f"    {zone}: {', '.join(parts)}")

    print(f"\n  RTL zones:")
    for zone in ['INITIAL', 'CENTRAL', 'FINAL']:
        members = [p for p, s in rtl_stats.items() if s['zone'] == zone]
        members.sort(key=lambda p: rtl_stats[p]['mean_pos'])
        parts = [f"{p}({rtl_stats[p]['mean_pos']:.2f})" for p in members]
        print(f"    {zone}: {', '.join(parts)}")

    print(f"\n  Family coherence: LTR={ltr_coherence:.3f}, RTL={rtl_coherence:.3f}")
    print(f"  R-squared (PREFIX -> position): {r_squared:.4f} (invariant under reversal)")
    print(f"  Zone variances LTR: {ltr_zone_var}")
    print(f"  Zone variances RTL: {rtl_zone_var}")

    # LTR interpretation check: are preparation PREFIXes (po, pch, tch, so) initial?
    prep_prefixes = {'po', 'pch', 'tch', 'so', 'dch'}
    closure_prefixes = {'ar', 'al', 'or', 'ol', 'ot'}

    ltr_prep_initial = sum(1 for p in prep_prefixes
                           if p in ltr_stats and ltr_stats[p]['zone'] == 'INITIAL')
    ltr_closure_final = sum(1 for p in closure_prefixes
                            if p in ltr_stats and ltr_stats[p]['zone'] == 'FINAL')
    rtl_prep_initial = sum(1 for p in prep_prefixes
                           if p in rtl_stats and rtl_stats[p]['zone'] == 'INITIAL')
    rtl_closure_final = sum(1 for p in closure_prefixes
                            if p in rtl_stats and rtl_stats[p]['zone'] == 'FINAL')

    ltr_interpretive_score = ltr_prep_initial + ltr_closure_final
    rtl_interpretive_score = rtl_prep_initial + rtl_closure_final

    print(f"\n  LTR: prep-initial={ltr_prep_initial}/{len(prep_prefixes)}, "
          f"closure-final={ltr_closure_final}/{len(closure_prefixes)}, "
          f"score={ltr_interpretive_score}")
    print(f"  RTL: prep-initial={rtl_prep_initial}/{len(prep_prefixes)}, "
          f"closure-final={rtl_closure_final}/{len(closure_prefixes)}, "
          f"score={rtl_interpretive_score}")

    if ltr_interpretive_score > rtl_interpretive_score + 2:
        verdict = "LTR_MORE_COHERENT"
    elif rtl_interpretive_score > ltr_interpretive_score + 2:
        verdict = "RTL_MORE_COHERENT"
    else:
        verdict = "NEUTRAL"

    print(f"  Verdict: {verdict}")

    return {
        'n_valid_prefixes': len(valid_prefixes),
        'r_squared': round(r_squared, 4),
        'ltr_family_coherence': round(ltr_coherence, 4),
        'rtl_family_coherence': round(rtl_coherence, 4),
        'ltr_zone_variance': ltr_zone_var,
        'rtl_zone_variance': rtl_zone_var,
        'ltr_zones': {pfx: s['zone'] for pfx, s in ltr_stats.items()},
        'rtl_zones': {pfx: s['zone'] for pfx, s in rtl_stats.items()},
        'ltr_positions': {pfx: s['mean_pos'] for pfx, s in ltr_stats.items()},
        'rtl_positions': {pfx: s['mean_pos'] for pfx, s in rtl_stats.items()},
        'ltr_interpretive_score': ltr_interpretive_score,
        'rtl_interpretive_score': rtl_interpretive_score,
        'verdict': verdict,
    }


# ── T4: Transition Matrix Spectral Properties ───────────────────────

def run_t4(lines, keys, token_to_class):
    """Compare 49x49 transition matrix eigenvalues under LTR vs RTL."""
    print("\n" + "=" * 60)
    print("T4: Transition Matrix Spectral Properties")
    print("=" * 60)

    ltr_trans = build_class_transitions(lines, keys, reverse=False)
    rtl_trans = build_class_transitions(lines, keys, reverse=True)

    def analyze_matrix(trans, label):
        """Compute spectral properties of a transition matrix."""
        row_sums = trans.sum(axis=1)
        prob = np.zeros_like(trans)
        for i in range(N_CLASSES):
            if row_sums[i] > 0:
                prob[i] = trans[i] / row_sums[i]

        # Eigenvalues
        eigenvalues = np.linalg.eigvals(prob)
        eigenvalues_abs = np.sort(np.abs(eigenvalues))[::-1]

        spectral_gap = 1 - eigenvalues_abs[1] if len(eigenvalues_abs) > 1 else 0

        # Stationary distribution (left eigenvector of eigenvalue 1)
        stationary = row_sums / row_sums.sum()

        # 6-state aggregation
        state_trans_6 = np.zeros((6, 6))
        state_names = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
        state_indices = {}
        for si, sname in enumerate(state_names):
            state_indices[sname] = si

        for i in range(N_CLASSES):
            ci = i + 1
            si = CLASS_TO_MACRO.get(ci)
            if si is None:
                continue
            si_idx = state_indices[si]
            for j in range(N_CLASSES):
                cj = j + 1
                sj = CLASS_TO_MACRO.get(cj)
                if sj is None:
                    continue
                sj_idx = state_indices[sj]
                state_trans_6[si_idx, sj_idx] += trans[i, j]

        # Normalize 6x6
        row_sums_6 = state_trans_6.sum(axis=1, keepdims=True)
        prob_6 = np.where(row_sums_6 > 0, state_trans_6 / row_sums_6, 0)

        eig_6 = np.sort(np.abs(np.linalg.eigvals(prob_6)))[::-1]
        gap_6 = 1 - eig_6[1] if len(eig_6) > 1 else 0

        stat_6 = state_trans_6.sum(axis=1) / state_trans_6.sum()

        print(f"\n  {label}:")
        print(f"    49x49 spectral gap: {spectral_gap:.4f}")
        print(f"    6x6 spectral gap: {gap_6:.4f}")
        print(f"    Stationary (6-state): {dict(zip(state_names, [round(s, 4) for s in stat_6]))}")

        return {
            'spectral_gap_49': round(float(spectral_gap), 4),
            'spectral_gap_6': round(float(gap_6), 4),
            'top_5_eigenvalues': [round(float(e), 4) for e in eigenvalues_abs[:5]],
            'stationary_6': {sn: round(float(s), 4) for sn, s in zip(state_names, stat_6)},
            'transition_matrix_6': {
                sn: {sn2: round(float(prob_6[i, j]), 4)
                     for j, sn2 in enumerate(state_names)}
                for i, sn in enumerate(state_names)
            },
        }

    ltr_result = analyze_matrix(ltr_trans, "LTR")
    rtl_result = analyze_matrix(rtl_trans, "RTL")

    # Compare
    gap_diff = abs(ltr_result['spectral_gap_6'] - rtl_result['spectral_gap_6'])
    stat_diff = sum(abs(ltr_result['stationary_6'][s] - rtl_result['stationary_6'][s])
                    for s in ltr_result['stationary_6'])

    print(f"\n  Spectral gap difference (6x6): {gap_diff:.4f}")
    print(f"  Stationary distribution L1 difference: {stat_diff:.6f}")

    if gap_diff < 0.05 and stat_diff < 0.01:
        verdict = "DIRECTION_INVARIANT"
    elif gap_diff > 0.1:
        verdict = "DIRECTION_SENSITIVE"
    else:
        verdict = "WEAKLY_SENSITIVE"

    print(f"  Verdict: {verdict}")

    return {
        'ltr': ltr_result,
        'rtl': rtl_result,
        'spectral_gap_diff_6': round(gap_diff, 4),
        'stationary_l1_diff': round(stat_diff, 6),
        'verdict': verdict,
    }


# ── T5: Per-Position Entropy Profile ─────────────────────────────────

def run_t5(lines, keys):
    """Compute class entropy by position quintile. Test for shape."""
    print("\n" + "=" * 60)
    print("T5: Per-Position Entropy Profile (Boundary-Inward Test)")
    print("=" * 60)

    # Bin tokens by position quintile
    quintile_classes = defaultdict(list)  # quintile_idx -> [class_ids]
    quintile_cond_fwd = defaultdict(list)  # quintile -> [(prev_class, this_class)]
    quintile_cond_bwd = defaultdict(list)  # quintile -> [(next_class, this_class)]

    for key in keys:
        toks = lines[key]
        n = len(toks)
        if n < 3:  # Need at least 3 tokens for meaningful position
            continue
        for i, t in enumerate(toks):
            pos = i / (n - 1)  # [0, 1]
            q = min(int(pos * 5), 4)  # Quintile 0-4
            quintile_classes[q].append(t['cls'])

            if i > 0:
                quintile_cond_fwd[q].append((toks[i - 1]['cls'], t['cls']))
            if i < n - 1:
                quintile_cond_bwd[q].append((toks[i + 1]['cls'], t['cls']))

    # Shannon entropy per quintile
    quintile_entropy = {}
    for q in range(5):
        counts = Counter(quintile_classes[q])
        h = shannon_entropy(counts)
        quintile_entropy[q] = round(h, 4)
        print(f"  Q{q} (pos {q*20}-{(q+1)*20}%): H={h:.4f} bits, "
              f"n={len(quintile_classes[q])}")

    # Conditional entropy H(class | prev_class) per quintile (forward conditioning)
    def cond_entropy(pairs):
        """H(Y|X) from list of (x, y) pairs."""
        joint = Counter(pairs)
        x_counts = Counter(p[0] for p in pairs)
        n = len(pairs)
        if n == 0:
            return 0.0
        h_xy = -sum(c / n * math.log2(c / n) for c in joint.values() if c > 0)
        h_x = -sum(c / n * math.log2(c / n) for c in x_counts.values() if c > 0)
        return h_xy - h_x

    cond_fwd_entropy = {}
    cond_bwd_entropy = {}
    for q in range(5):
        cf = cond_entropy(quintile_cond_fwd[q]) if quintile_cond_fwd[q] else 0
        cb = cond_entropy(quintile_cond_bwd[q]) if quintile_cond_bwd[q] else 0
        cond_fwd_entropy[q] = round(cf, 4)
        cond_bwd_entropy[q] = round(cb, 4)

    print(f"\n  Conditional entropy H(class | prev):")
    for q in range(5):
        print(f"    Q{q}: H_fwd={cond_fwd_entropy[q]:.4f}, H_bwd={cond_bwd_entropy[q]:.4f}")

    # Shape detection
    entropies = [quintile_entropy[q] for q in range(5)]

    # Monotonic decrease (LTR convergence)?
    mono_decrease = all(entropies[i] >= entropies[i + 1] for i in range(4))
    # Monotonic increase (RTL convergence)?
    mono_increase = all(entropies[i] <= entropies[i + 1] for i in range(4))

    # U-shaped (boundary-inward)?
    # Minimum should be at edges (Q0 or Q4), maximum in middle (Q2)
    min_q = entropies.index(min(entropies))
    max_q = entropies.index(max(entropies))
    u_shaped = (min_q in [0, 4]) and (max_q in [1, 2, 3])

    # Inverted U (low boundaries, high middle)?
    inv_u = (max_q in [1, 2, 3]) and (entropies[0] < entropies[2]) and (entropies[4] < entropies[2])

    # Gradient: Spearman-like correlation of entropy with position
    from scipy.stats import spearmanr
    positions = list(range(5))
    rho, p_val = spearmanr(positions, entropies)

    print(f"\n  Entropy gradient: rho={rho:.3f} (p={p_val:.3f})")
    print(f"  Monotonic decrease: {mono_decrease}")
    print(f"  Monotonic increase: {mono_increase}")
    print(f"  U-shaped: {u_shaped}")
    print(f"  Inverted-U: {inv_u}")
    print(f"  Min at Q{min_q}, Max at Q{max_q}")

    if mono_decrease or (rho < -0.5 and p_val < 0.1):
        verdict = "LTR_CONVERGENCE"
    elif mono_increase or (rho > 0.5 and p_val < 0.1):
        verdict = "RTL_CONVERGENCE"
    elif inv_u:
        verdict = "BOUNDARY_INWARD"
    elif u_shaped:
        verdict = "BOUNDARY_OUTWARD"
    else:
        verdict = "NO_CLEAR_PATTERN"

    print(f"  Verdict: {verdict}")

    return {
        'quintile_entropy': quintile_entropy,
        'cond_fwd_entropy': cond_fwd_entropy,
        'cond_bwd_entropy': cond_bwd_entropy,
        'spearman_rho': round(float(rho), 4),
        'spearman_p': round(float(p_val), 4),
        'monotonic_decrease': mono_decrease,
        'monotonic_increase': mono_increase,
        'u_shaped': u_shaped,
        'inverted_u': inv_u,
        'verdict': verdict,
    }


# ── T6: CC Positional Role ──────────────────────────────────────────

def run_t6(lines, keys):
    """Analyze CC class positional role under LTR vs RTL."""
    print("\n" + "=" * 60)
    print("T6: CC Positional Role (Initiator vs Terminator)")
    print("=" * 60)

    CC_CLASSES = {10, 11, 12}
    AXM_CLASSES = MACRO_STATE_PARTITION['AXM']

    # CC position statistics
    cc_positions = defaultdict(list)
    for key in keys:
        toks = lines[key]
        n = len(toks)
        if n < 2:
            continue
        for i, t in enumerate(toks):
            if t['cls'] in CC_CLASSES:
                pos = i / (n - 1)
                cc_positions[t['cls']].append(pos)

    print("  CC class positions (LTR):")
    for cls in sorted(CC_CLASSES):
        if cls in cc_positions:
            positions = cc_positions[cls]
            mean_pos = np.mean(positions)
            print(f"    Class {cls}: mean_pos={mean_pos:.3f} (n={len(positions)}), "
                  f"RTL_pos={1-mean_pos:.3f}")

    # CC transition analysis: what follows CC vs what precedes CC
    cc_to_next = Counter()  # What class follows CC?
    prev_to_cc = Counter()  # What class precedes CC?

    for key in keys:
        toks = lines[key]
        for i, t in enumerate(toks):
            if t['cls'] in CC_CLASSES:
                if i < len(toks) - 1:
                    next_macro = CLASS_TO_MACRO.get(toks[i + 1]['cls'], 'UNK')
                    cc_to_next[next_macro] += 1
                if i > 0:
                    prev_macro = CLASS_TO_MACRO.get(toks[i - 1]['cls'], 'UNK')
                    prev_to_cc[prev_macro] += 1

    total_next = sum(cc_to_next.values())
    total_prev = sum(prev_to_cc.values())

    print(f"\n  CC -> next (LTR, n={total_next}):")
    for state, count in cc_to_next.most_common():
        print(f"    {state}: {count} ({count/total_next*100:.1f}%)")

    print(f"\n  prev -> CC (LTR, n={total_prev}):")
    for state, count in prev_to_cc.most_common():
        print(f"    {state}: {count} ({count/total_prev*100:.1f}%)")

    # Under RTL, "CC -> next" becomes "prev -> CC" and vice versa
    # So RTL CC->next = LTR prev->CC
    cc_to_axm_ltr = cc_to_next.get('AXM', 0) / total_next if total_next > 0 else 0
    cc_to_axm_rtl = prev_to_cc.get('AXM', 0) / total_prev if total_prev > 0 else 0

    # CC at line boundary?
    cc_initial = 0
    cc_final = 0
    cc_total = 0
    for key in keys:
        toks = lines[key]
        for i, t in enumerate(toks):
            if t['cls'] in CC_CLASSES:
                cc_total += 1
                if i == 0:
                    cc_initial += 1
                if i == len(toks) - 1:
                    cc_final += 1

    print(f"\n  CC at boundaries: initial={cc_initial} ({cc_initial/cc_total*100:.1f}%), "
          f"final={cc_final} ({cc_final/cc_total*100:.1f}%), total={cc_total}")
    print(f"  CC->AXM: LTR={cc_to_axm_ltr:.3f}, RTL={cc_to_axm_rtl:.3f}")

    if cc_to_axm_ltr > cc_to_axm_rtl and cc_initial > cc_final:
        verdict = "CC_INITIATOR_LTR"
    elif cc_to_axm_rtl > cc_to_axm_ltr and cc_final > cc_initial:
        verdict = "CC_INITIATOR_RTL"
    elif cc_initial > cc_final:
        verdict = "CC_BOUNDARY_LEFT"
    elif cc_final > cc_initial:
        verdict = "CC_BOUNDARY_RIGHT"
    else:
        verdict = "CC_NEUTRAL"

    print(f"  Verdict: {verdict}")

    return {
        'cc_mean_positions': {str(c): round(float(np.mean(cc_positions[c])), 4)
                              for c in sorted(CC_CLASSES) if c in cc_positions},
        'cc_to_next_ltr': {s: c for s, c in cc_to_next.most_common()},
        'prev_to_cc_ltr': {s: c for s, c in prev_to_cc.most_common()},
        'cc_to_axm_ltr': round(cc_to_axm_ltr, 4),
        'cc_to_axm_rtl': round(cc_to_axm_rtl, 4),
        'cc_initial': cc_initial,
        'cc_final': cc_final,
        'cc_total': cc_total,
        'verdict': verdict,
    }


# ── T7: Vocabulary Gradient Direction ────────────────────────────────

def run_t7(lines, keys, morph):
    """Test vocabulary gradient direction within paragraph bodies."""
    print("\n" + "=" * 60)
    print("T7: Vocabulary Gradient Direction")
    print("=" * 60)

    # Build a global MIDDLE frequency table
    global_middle_freq = Counter()
    for key in keys:
        for t in lines[key]:
            global_middle_freq[t['middle']] += 1

    total_tokens = sum(global_middle_freq.values())
    n_unique_middles = len(global_middle_freq)

    # Classify MIDDLEs as universal (top 20 by frequency) or rare (bottom 50% by frequency)
    sorted_middles = global_middle_freq.most_common()
    universal_set = set(m for m, _ in sorted_middles[:20])
    cumulative = 0
    rare_set = set()
    for m, c in reversed(sorted_middles):
        cumulative += c
        rare_set.add(m)
        if cumulative > total_tokens * 0.05:  # Bottom 5% of token mass
            break

    # Group lines by paragraph (folio, paragraph_number inferred from line structure)
    # Paragraphs are delimited by gallows — approximate using line_number sequences
    # For simplicity, group all lines of a folio and use line position
    folio_lines = defaultdict(list)
    for key in keys:
        folio, line_num = key
        folio_lines[folio].append((line_num, key))

    # Compute per-quintile vocabulary statistics
    # Use line position within folio as proxy for position within paragraph body
    quintile_universal = defaultdict(int)
    quintile_rare = defaultdict(int)
    quintile_total = defaultdict(int)

    for folio, line_items in folio_lines.items():
        line_items.sort(key=lambda x: (int(x[0]) if x[0].isdigit() else 999, x[0]))
        n_lines = len(line_items)
        if n_lines < 3:
            continue

        # Skip first line (header) per C932 methodology
        body_lines = line_items[1:]
        n_body = len(body_lines)

        for idx, (line_num, key) in enumerate(body_lines):
            q = min(int(idx / n_body * 5), 4)
            for t in lines[key]:
                quintile_total[q] += 1
                if t['middle'] in universal_set:
                    quintile_universal[q] += 1
                if t['middle'] in rare_set:
                    quintile_rare[q] += 1

    # Compute percentages
    universal_pct = {}
    rare_pct = {}
    for q in range(5):
        total = quintile_total.get(q, 1)
        universal_pct[q] = round(quintile_universal.get(q, 0) / total * 100, 2)
        rare_pct[q] = round(quintile_rare.get(q, 0) / total * 100, 2)
        print(f"  Q{q}: universal={universal_pct[q]:.1f}%, rare={rare_pct[q]:.1f}%, "
              f"n={total}")

    # Gradient direction
    uni_values = [universal_pct[q] for q in range(5)]
    rare_values = [rare_pct[q] for q in range(5)]
    positions = list(range(5))

    from scipy.stats import spearmanr
    rho_uni, p_uni = spearmanr(positions, uni_values)
    rho_rare, p_rare = spearmanr(positions, rare_values)

    print(f"\n  Universal gradient: rho={rho_uni:.3f} (p={p_uni:.3f})")
    print(f"  Rare gradient: rho={rho_rare:.3f} (p={p_rare:.3f})")

    # C932 baseline: universal increases (r=+0.92), rare decreases (r=-0.80) under LTR
    if rho_uni > 0.5 and rho_rare < -0.3:
        verdict = "LTR_SPEC_TO_EXEC"
    elif rho_uni < -0.5 and rho_rare > 0.3:
        verdict = "RTL_SPEC_TO_EXEC"
    elif abs(rho_uni) < 0.3 and abs(rho_rare) < 0.3:
        verdict = "NO_GRADIENT"
    else:
        verdict = "MIXED_GRADIENT"

    print(f"  Verdict: {verdict}")

    return {
        'universal_pct': universal_pct,
        'rare_pct': rare_pct,
        'quintile_totals': dict(quintile_total),
        'rho_universal': round(float(rho_uni), 4),
        'p_universal': round(float(p_uni), 4),
        'rho_rare': round(float(rho_rare), 4),
        'p_rare': round(float(p_rare), 4),
        'n_universal_middles': len(universal_set),
        'n_rare_middles': len(rare_set),
        'verdict': verdict,
    }


# ── Combined Verdict ─────────────────────────────────────────────────

def combined_verdict(results):
    """Synthesize all 7 tests into overall direction verdict."""
    votes = {'LTR': 0, 'RTL': 0, 'NEUTRAL': 0, 'BOUNDARY_INWARD': 0}

    # T1: Forbidden landscape (direction-neutral by construction — cannot vote)
    # Key finding: symmetry fraction explains C1034
    votes['NEUTRAL'] += 1

    # T2: MI asymmetry
    if results['t2']['direction_vote'] == 'LTR':
        votes['LTR'] += 2
    elif results['t2']['direction_vote'] == 'RTL':
        votes['RTL'] += 2
    else:
        votes['NEUTRAL'] += 1

    # T3: PREFIX coherence
    if 'LTR' in results['t3']['verdict']:
        votes['LTR'] += 2
    elif 'RTL' in results['t3']['verdict']:
        votes['RTL'] += 2
    else:
        votes['NEUTRAL'] += 1

    # T4: Spectral (diagnostic)
    if results['t4']['verdict'] == 'DIRECTION_INVARIANT':
        votes['NEUTRAL'] += 1
    elif results['t4']['verdict'] == 'DIRECTION_SENSITIVE':
        pass  # Doesn't vote for direction, just notes sensitivity

    # T5: Entropy profile (special — can detect boundary-inward)
    if 'LTR' in results['t5']['verdict']:
        votes['LTR'] += 1
    elif 'RTL' in results['t5']['verdict']:
        votes['RTL'] += 1
    elif 'BOUNDARY_INWARD' in results['t5']['verdict']:
        votes['BOUNDARY_INWARD'] += 2
    else:
        votes['NEUTRAL'] += 1

    # T6: CC role (supporting)
    if 'LTR' in results['t6']['verdict']:
        votes['LTR'] += 1
    elif 'RTL' in results['t6']['verdict']:
        votes['RTL'] += 1

    # T7: Vocabulary gradient (supporting)
    if 'LTR' in results['t7']['verdict']:
        votes['LTR'] += 1
    elif 'RTL' in results['t7']['verdict']:
        votes['RTL'] += 1

    # Determine overall verdict
    max_votes = max(votes.values())
    winners = [k for k, v in votes.items() if v == max_votes]

    if len(winners) == 1:
        winner = winners[0]
    else:
        # Tie-breaking: Tier 1 tests (T1-T3) have priority
        winner = 'DIRECTION_AMBIGUOUS'

    if winner == 'LTR':
        overall = 'DIRECTION_CONFIRMED_LTR'
    elif winner == 'RTL':
        overall = 'DIRECTION_CONFIRMED_RTL'
    elif winner == 'BOUNDARY_INWARD':
        overall = 'BOUNDARY_INWARD_SUPPORTED'
    elif winner == 'NEUTRAL':
        overall = 'DIRECTION_INDETERMINATE'
    else:
        overall = 'DIRECTION_AMBIGUOUS'

    return {
        'votes': votes,
        'overall_verdict': overall,
        'per_test_verdicts': {
            'T1_forbidden': results['t1']['verdict'],
            'T2_mi_asymmetry': results['t2']['verdict'],
            'T3_prefix_coherence': results['t3']['verdict'],
            'T4_spectral': results['t4']['verdict'],
            'T5_entropy_profile': results['t5']['verdict'],
            'T6_cc_role': results['t6']['verdict'],
            'T7_vocabulary_gradient': results['t7']['verdict'],
        },
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 399: Reading Direction Test (LTR vs RTL)")
    print("=" * 60)

    lines, keys, token_to_class, morph = load_data()

    results = {
        'phase': 399,
        'name': 'READING_DIRECTION_TEST',
        'n_tokens': sum(len(lines[k]) for k in keys),
        'n_lines': len(keys),
    }

    results['t1'] = run_t1(lines, keys, morph)
    results['t2'] = run_t2(lines, keys)
    results['t3'] = run_t3(lines, keys)
    results['t4'] = run_t4(lines, keys, token_to_class)
    results['t5'] = run_t5(lines, keys)
    results['t6'] = run_t6(lines, keys)
    results['t7'] = run_t7(lines, keys, morph)

    results['combined'] = combined_verdict(results)

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'reading_direction_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("COMBINED VERDICT")
    print("=" * 60)
    print(f"  Votes: {results['combined']['votes']}")
    print(f"  Overall: {results['combined']['overall_verdict']}")
    print(f"\n  Per-test verdicts:")
    for test, verdict in results['combined']['per_test_verdicts'].items():
        print(f"    {test}: {verdict}")
    print(f"\n  Results saved to: {out_path}")


if __name__ == '__main__':
    main()
