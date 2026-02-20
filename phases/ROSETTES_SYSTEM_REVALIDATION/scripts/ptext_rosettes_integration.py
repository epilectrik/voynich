"""Phase 403: P-Text / Rosettes Integration Revalidation — 7-test battery.

Revalidates the unified indexing hypothesis (Phase 395, C1112/C1113) using
corrected ZL transcription data for Rosettes.

5 revalidation tests (R1, R3-R5 revalidate Phase 395's P1, I1, I3, I4)
2 new diagnostic tests (R2, R6, R7) leveraging Phase 402 entity-type data.

Synthesis: UNIFIED_INDEXING_v2 = R1 + R3 + R4 + R5
  (I2_original from Phase 395 was FAIL, so R4 carries that slot)

Data sources:
  - P-text: Transcript.azc() filtered by P placement (main transcript, unchanged)
  - Rosettes: data/rosettes_annotated.json (corrected ZL, via RosettesAnalyzer)
  - Bridge MIDDLEs: bridge_selection.json (85 MIDDLEs)
  - Affordance bins: middle_affordance_table.json
  - B paragraphs: BFolioDecoder.analyze_folio_paragraphs()
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import defaultdict, Counter

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer, BFolioDecoder)

# ============================================================
# CONSTANTS
# ============================================================

N_BOOT = 5000
RNG_SEED = 42
FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]  # exclude bin 4 (BULK_OPERATIONAL)

ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}


# ============================================================
# UTILITY
# ============================================================

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    return obj


def jaccard(a, b):
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def cosine_sim_counters(vec_a, vec_b):
    """Cosine similarity between two Counter-like dicts."""
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def cosine_sim_vectors(a, b):
    """Cosine similarity between two numeric lists."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x ** 2 for x in a))
    mag_b = math.sqrt(sum(x ** 2 for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _rank(values):
    """Assign fractional ranks (for Spearman correlation)."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman_rho(x, y):
    """Manual Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0
    x_ranks = _rank(x)
    y_ranks = _rank(y)
    d_sq = sum((x_ranks[i] - y_ranks[i]) ** 2 for i in range(n))
    rho = 1 - (6 * d_sq) / (n * (n ** 2 - 1))
    return rho


def spearman_p_approx(rho, n):
    """Approximate p-value for Spearman rho using t-distribution (valid for n>30)."""
    if abs(rho) >= 1.0:
        return 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    # For n > 100, t ~ normal, so use conservative p estimate
    abs_t = abs(t_stat)
    if abs_t > 10:
        return 0.0  # p << 0.001
    elif abs_t > 3.29:
        return 0.001
    elif abs_t > 2.576:
        return 0.01
    elif abs_t > 1.96:
        return 0.05
    else:
        return 0.10  # conservative upper bound


def bin_vector(middle_set, mid_to_bin):
    """Convert a set of MIDDLEs to a 9-element affordance bin frequency vector."""
    counts = Counter()
    for mid in middle_set:
        b = mid_to_bin.get(mid)
        if b is not None and b in FUNCTIONAL_BINS:
            counts[b] += 1
    total = sum(counts.values())
    if total == 0:
        return [0.0] * len(FUNCTIONAL_BINS)
    return [counts.get(b, 0) / total for b in FUNCTIONAL_BINS]


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Pre-compute all reference data for tests R1-R7."""
    print("Loading data...")
    morph = Morphology()
    tx = Transcript()
    ra = RosettesAnalyzer()

    # ---- P-text tokens ----
    ptext_all_mids = set()
    ptext_folio_mids = defaultdict(set)
    ptext_prefix_counts = Counter()
    ptext_token_count = 0
    ptext_folios = set()

    for tok in tx.azc():
        if not tok.placement.startswith('P'):
            continue
        if not tok.word.strip() or '*' in tok.word:
            continue
        m = morph.extract(tok.word)
        ptext_token_count += 1
        ptext_folios.add(tok.folio)
        if m.middle:
            ptext_all_mids.add(m.middle)
            ptext_folio_mids[tok.folio].add(m.middle)
        if m.prefix:
            ptext_prefix_counts[m.prefix] += 1

    print(f"  P-text: {ptext_token_count} tokens, {len(ptext_all_mids)} unique MIDDLEs, "
          f"{len(ptext_folios)} folios")

    # ---- Rosettes data (entity-type decomposition) ----
    ros_all_mids = ra.all_middles()
    ros_bridge_mids = ra.all_bridge_middles()
    ros_prefix_counts = Counter()

    # Group by sub-region type (entity type)
    ros_entity_type_mids = defaultdict(set)
    for entity_name in ra.get_entities():
        for sr in ra.get_sub_regions(entity_name):
            tokens = ra.get_entity_tokens(entity_name, sub_region=sr)
            for t in tokens:
                if t.get('middle'):
                    ros_entity_type_mids[sr].add(t['middle'])
                if t.get('prefix'):
                    ros_prefix_counts[t['prefix']] += 1

    print(f"  Rosettes: {len(ros_all_mids)} unique MIDDLEs, "
          f"{len(ros_bridge_mids)} bridge MIDDLEs")
    print(f"  Rosettes entity types: {dict({k: len(v) for k, v in ros_entity_type_mids.items()})}")

    # ---- Currier A corpus ----
    a_all_mids = set()
    a_prefix_counts = Counter()
    for tok in tx.currier_a():
        m = morph.extract(tok.word)
        if m.middle:
            a_all_mids.add(m.middle)
        if m.prefix:
            a_prefix_counts[m.prefix] += 1

    print(f"  Currier A: {len(a_all_mids)} unique MIDDLEs")

    # ---- AZC diagram tokens (non-P-text) for R2 ----
    azc_diag_prefix_counts = Counter()
    for tok in tx.azc():
        if tok.placement.startswith('P'):
            continue  # skip P-text
        m = morph.extract(tok.word)
        if m.prefix:
            azc_diag_prefix_counts[m.prefix] += 1

    # ---- Currier B corpus (excluding Rosettes folios) ----
    b_all_mids = set()
    b_folio_mids = defaultdict(set)
    section_middles = defaultdict(set)
    b_folios = set()

    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        m = morph.extract(tok.word)
        if m.middle:
            b_all_mids.add(m.middle)
            b_folio_mids[tok.folio].add(m.middle)
            section_middles[tok.section].add(m.middle)
        b_folios.add(tok.folio)

    print(f"  Currier B: {len(b_all_mids)} unique MIDDLEs, {len(b_folios)} folios")

    # ---- Bridge MIDDLEs ----
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bd = json.load(f)
    bridge_middles = set(bd['t5_structural_profile']['bridge_middles'])
    print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

    # ---- Affordance table ----
    aff_path = PROJECT / 'data' / 'middle_affordance_table.json'
    with open(aff_path, 'r', encoding='utf-8') as f:
        aff_data = json.load(f)
    mid_to_bin = {}
    for mid_key, mid_val in aff_data.get('middles', {}).items():
        if isinstance(mid_val, dict) and 'affordance_bin' in mid_val:
            mid_to_bin[mid_key] = mid_val['affordance_bin']
    print(f"  Affordance table: {len(mid_to_bin)} MIDDLEs mapped")

    # ---- B paragraph header/body MIDDLEs ----
    decoder = BFolioDecoder()
    para_records = []  # (folio, para_id, header_mids_set, body_mids_set, all_mids_set)
    all_header_mids = set()

    for folio in sorted(b_folios):
        try:
            paras = decoder.analyze_folio_paragraphs(folio)
        except Exception:
            continue
        for p in paras:
            header_mids = set()
            body_mids = set()
            all_para_mids = set()
            for line in p.lines:
                for tok in line.tokens:
                    m = morph.extract(tok.word)
                    if m.middle:
                        all_para_mids.add(m.middle)
                        if line.paragraph_zone == 'HEADER':
                            header_mids.add(m.middle)
                        else:
                            body_mids.add(m.middle)
            if all_para_mids:
                para_records.append((folio, p.paragraph_id, header_mids, body_mids, all_para_mids))
                all_header_mids.update(header_mids)

    print(f"  B paragraphs: {len(para_records)} with MIDDLEs, "
          f"{len(all_header_mids)} unique header MIDDLEs")

    # ---- Per-rosette MIDDLEs (for R7) ----
    per_rosette_mids = ra.per_rosette_middles()

    return {
        'morph': morph,
        'ptext_all_mids': ptext_all_mids,
        'ptext_folio_mids': dict(ptext_folio_mids),
        'ptext_prefix_counts': ptext_prefix_counts,
        'ptext_token_count': ptext_token_count,
        'ptext_folios': sorted(ptext_folios),
        'ros_all_mids': ros_all_mids,
        'ros_bridge_mids': ros_bridge_mids,
        'ros_entity_type_mids': dict(ros_entity_type_mids),
        'ros_prefix_counts': ros_prefix_counts,
        'per_rosette_mids': per_rosette_mids,
        'a_all_mids': a_all_mids,
        'a_prefix_counts': a_prefix_counts,
        'azc_diag_prefix_counts': azc_diag_prefix_counts,
        'b_all_mids': b_all_mids,
        'b_folio_mids': dict(b_folio_mids),
        'b_folios': sorted(b_folios),
        'section_middles': dict(section_middles),
        'bridge_middles': bridge_middles,
        'mid_to_bin': mid_to_bin,
        'para_records': para_records,
        'all_header_mids': all_header_mids,
    }


# ============================================================
# R1: Bridge Density Comparison (entity-decomposed)
# ============================================================

def r1_bridge_density(data):
    """R1: Revalidation of Phase 395 P1.

    P-text bridge fraction vs A bootstrap + Rosettes entity-type comparison.
    PASS: P-text bridge frac > A bootstrap p95 AND >= 50% of Rosettes bridge frac.
    """
    print("\n=== R1: Bridge Density Comparison ===")

    ptext_mids = data['ptext_all_mids']
    bridge = data['bridge_middles']
    a_mids = data['a_all_mids']
    ros_all = data['ros_all_mids']
    ros_bridge = data['ros_bridge_mids']
    ros_types = data['ros_entity_type_mids']

    # P-text bridge fraction
    pt_bridge = ptext_mids & bridge
    pt_frac = len(pt_bridge) / len(ptext_mids) if ptext_mids else 0

    # Rosettes overall bridge fraction
    ros_frac = len(ros_bridge) / len(ros_all) if ros_all else 0

    # Per entity type bridge fractions
    type_fracs = {}
    for sr_type, mids in sorted(ros_types.items()):
        br = mids & bridge
        type_fracs[sr_type] = {
            'bridge_count': len(br),
            'total_mids': len(mids),
            'fraction': len(br) / len(mids) if mids else 0,
        }

    # Bootstrap: sample from A vocabulary
    random.seed(RNG_SEED)
    a_mids_list = sorted(a_mids)
    sample_size = min(len(ptext_mids), len(a_mids_list))
    boot_fracs = []
    for _ in range(N_BOOT):
        sample = set(random.sample(a_mids_list, sample_size))
        boot_fracs.append(len(sample & bridge) / len(sample))

    boot_fracs_sorted = sorted(boot_fracs)
    p95 = boot_fracs_sorted[int(0.95 * N_BOOT)]
    percentile = sum(1 for x in boot_fracs if x <= pt_frac) / N_BOOT * 100
    boot_mean = sum(boot_fracs) / N_BOOT

    above_p95 = pt_frac > p95
    within_50pct_ros = pt_frac >= 0.5 * ros_frac
    verdict = 'PASS' if (above_p95 and within_50pct_ros) else 'FAIL'

    print(f"  P-text bridge fraction: {pt_frac:.4f} ({len(pt_bridge)}/{len(ptext_mids)})")
    print(f"  Rosettes bridge fraction: {ros_frac:.4f} ({len(ros_bridge)}/{len(ros_all)})")
    print(f"  A bootstrap p95: {p95:.4f}, P-text percentile: {percentile:.1f}%")
    print(f"  above_a_p95: {above_p95}, within_50pct_ros: {within_50pct_ros}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'R1',
        'name': 'Bridge Density Comparison (entity-decomposed)',
        'verdict': verdict,
        'ptext_bridge_fraction': pt_frac,
        'ptext_bridge_count': len(pt_bridge),
        'ptext_total_mids': len(ptext_mids),
        'rosettes_bridge_fraction': ros_frac,
        'rosettes_bridge_count': len(ros_bridge),
        'rosettes_total_mids': len(ros_all),
        'per_entity_type': type_fracs,
        'bootstrap_n': N_BOOT,
        'bootstrap_p95': p95,
        'bootstrap_mean': boot_mean,
        'ptext_percentile': percentile,
        'above_a_p95': above_p95,
        'within_50pct_ros': within_50pct_ros,
    }


# ============================================================
# R2: Grammar Profile Divergence (diagnostic)
# ============================================================

def r2_grammar_divergence(data):
    """R2: New diagnostic — PREFIX cosine similarities.

    P-text should be A-like (C758 cosine 0.97), Rosettes should be AZC-like (C1127).
    Reports cosine matrix, no PASS/FAIL.
    """
    print("\n=== R2: Grammar Profile Divergence (diagnostic) ===")

    profiles = {
        'ptext': data['ptext_prefix_counts'],
        'currier_a': data['a_prefix_counts'],
        'rosettes': data['ros_prefix_counts'],
        'azc_diagram': data['azc_diag_prefix_counts'],
    }

    # Compute all pairwise cosines
    names = ['ptext', 'currier_a', 'rosettes', 'azc_diagram']
    cosine_matrix = {}
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            cos = cosine_sim_counters(profiles[n1], profiles[n2])
            key = f"{n1}_vs_{n2}"
            cosine_matrix[key] = cos
            print(f"  {n1} vs {n2}: {cos:.4f}")

    # Key comparisons
    pt_a = cosine_matrix.get('ptext_vs_currier_a', 0)
    pt_ros = cosine_matrix.get('ptext_vs_rosettes', 0)
    ros_azc = cosine_matrix.get('rosettes_vs_azc_diagram', 0)

    print(f"  Key: P-text~A={pt_a:.4f}, P-text~Rosettes={pt_ros:.4f}, "
          f"Rosettes~AZC={ros_azc:.4f}")

    return {
        'test': 'R2',
        'name': 'Grammar Profile Divergence (diagnostic)',
        'verdict': 'DIAGNOSTIC',
        'cosine_matrix': cosine_matrix,
        'key_findings': {
            'ptext_to_A': pt_a,
            'ptext_to_rosettes': pt_ros,
            'rosettes_to_AZC': ros_azc,
            'ptext_is_A_like': pt_a > 0.90,
            'rosettes_is_AZC_like': ros_azc > 0.70,
            'grammar_divergence': pt_a > pt_ros,
        },
        'profile_sizes': {name: sum(profiles[name].values()) for name in names},
    }


# ============================================================
# R3: Vocabulary Overlap (entity-decomposed)
# ============================================================

def r3_vocabulary_overlap(data):
    """R3: Revalidation of Phase 395 I1.

    Jaccard of P-text vs Rosettes MIDDLEs + entity-type decomposition.
    PASS: Jaccard(P-text, Rosettes_all) > A bootstrap p95.
    """
    print("\n=== R3: Vocabulary Overlap (entity-decomposed) ===")

    ptext_mids = data['ptext_all_mids']
    ros_all = data['ros_all_mids']
    a_mids = data['a_all_mids']
    ros_types = data['ros_entity_type_mids']

    # Overall Jaccard
    j_overall = jaccard(ptext_mids, ros_all)
    intersection = ptext_mids & ros_all
    print(f"  P-text vs Rosettes (all): Jaccard={j_overall:.4f}, "
          f"|intersection|={len(intersection)}")

    # Per entity type Jaccard
    type_jaccards = {}
    for sr_type, mids in sorted(ros_types.items()):
        j = jaccard(ptext_mids, mids)
        inter = ptext_mids & mids
        type_jaccards[sr_type] = {
            'jaccard': j,
            'intersection_size': len(inter),
            'rosettes_type_mids': len(mids),
        }
        print(f"  P-text vs {sr_type}: Jaccard={j:.4f} (|inter|={len(inter)})")

    # Bootstrap: sample from A, compute Jaccard vs Rosettes
    random.seed(RNG_SEED)
    a_mids_list = sorted(a_mids)
    sample_size = min(len(ptext_mids), len(a_mids_list))
    boot_jaccards = []
    for _ in range(N_BOOT):
        sample = set(random.sample(a_mids_list, sample_size))
        boot_jaccards.append(jaccard(sample, ros_all))

    boot_sorted = sorted(boot_jaccards)
    p95 = boot_sorted[int(0.95 * N_BOOT)]
    percentile = sum(1 for x in boot_jaccards if x <= j_overall) / N_BOOT * 100
    boot_mean = sum(boot_jaccards) / N_BOOT

    verdict = 'PASS' if j_overall > p95 else 'FAIL'

    print(f"  Bootstrap p95: {p95:.4f}, P-text percentile: {percentile:.1f}%")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'R3',
        'name': 'Vocabulary Overlap (entity-decomposed)',
        'verdict': verdict,
        'jaccard_overall': j_overall,
        'intersection_size': len(intersection),
        'intersection_middles': sorted(intersection),
        'ptext_mids_count': len(ptext_mids),
        'rosettes_mids_count': len(ros_all),
        'per_entity_type': type_jaccards,
        'bootstrap_n': N_BOOT,
        'bootstrap_p95': p95,
        'bootstrap_mean': boot_mean,
        'ptext_percentile': percentile,
    }


# ============================================================
# R4: Paragraph Co-Tracking
# ============================================================

def r4_paragraph_cotracking(data):
    """R4: Revalidation of Phase 395 I3.

    Spearman correlation of P-text/Rosettes overlap with B paragraphs.
    PASS: rho > 0.30 AND p < 0.05.
    """
    print("\n=== R4: Paragraph Co-Tracking ===")

    ptext_mids = data['ptext_all_mids']
    ros_all = data['ros_all_mids']
    para_records = data['para_records']

    pt_overlaps = []
    ros_overlaps = []

    for folio, para_id, header_mids, body_mids, all_para_mids in para_records:
        if not all_para_mids:
            continue
        pt_ov = len(ptext_mids & all_para_mids) / len(all_para_mids)
        ros_ov = len(ros_all & all_para_mids) / len(all_para_mids)
        pt_overlaps.append(pt_ov)
        ros_overlaps.append(ros_ov)

    n = len(pt_overlaps)
    rho = spearman_rho(pt_overlaps, ros_overlaps)
    p_val = spearman_p_approx(rho, n)

    pt_mean = sum(pt_overlaps) / n if n else 0
    ros_mean = sum(ros_overlaps) / n if n else 0

    verdict = 'PASS' if (rho > 0.30 and p_val < 0.05) else 'FAIL'

    print(f"  Paragraphs analyzed: {n}")
    print(f"  P-text overlap mean: {pt_mean:.4f}")
    print(f"  Rosettes overlap mean: {ros_mean:.4f}")
    print(f"  Spearman rho: {rho:.4f}, p ~ {p_val}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'R4',
        'name': 'Paragraph Co-Tracking',
        'verdict': verdict,
        'n_paragraphs': n,
        'spearman_rho': rho,
        'p_value_approx': p_val,
        'ptext_overlap_mean': pt_mean,
        'rosettes_overlap_mean': ros_mean,
    }


# ============================================================
# R5: Union Bridge Paragraph Prediction
# ============================================================

def r5_union_bridge_prediction(data):
    """R5: Revalidation of Phase 395 I4.

    Cosine of affordance bin vectors: unified index (P-text + Rosettes) vs B headers.
    PASS: cosine > 0.70.
    """
    print("\n=== R5: Union Bridge Paragraph Prediction ===")

    ptext_mids = data['ptext_all_mids']
    ros_all = data['ros_all_mids']
    all_header_mids = data['all_header_mids']
    mid_to_bin = data['mid_to_bin']

    # Unified index
    unified = ptext_mids | ros_all
    print(f"  Unified index: {len(unified)} MIDDLEs "
          f"({len(ptext_mids)} P-text + {len(ros_all)} Rosettes, "
          f"{len(ptext_mids & ros_all)} overlap)")

    # Bin vectors
    unified_vec = bin_vector(unified, mid_to_bin)
    header_vec = bin_vector(all_header_mids, mid_to_bin)

    # Also compute individual components for comparison
    ptext_vec = bin_vector(ptext_mids, mid_to_bin)
    ros_vec = bin_vector(ros_all, mid_to_bin)

    cos_unified = cosine_sim_vectors(unified_vec, header_vec)
    cos_ptext_only = cosine_sim_vectors(ptext_vec, header_vec)
    cos_ros_only = cosine_sim_vectors(ros_vec, header_vec)

    verdict = 'PASS' if cos_unified > 0.70 else 'FAIL'

    print(f"  Unified vs Headers: cosine={cos_unified:.4f}")
    print(f"  P-text alone vs Headers: cosine={cos_ptext_only:.4f}")
    print(f"  Rosettes alone vs Headers: cosine={cos_ros_only:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'R5',
        'name': 'Union Bridge Paragraph Prediction',
        'verdict': verdict,
        'unified_mids_count': len(unified),
        'header_mids_count': len(all_header_mids),
        'cosine_unified_vs_headers': cos_unified,
        'cosine_ptext_only_vs_headers': cos_ptext_only,
        'cosine_rosettes_only_vs_headers': cos_ros_only,
        'unified_better_than_individual': cos_unified >= max(cos_ptext_only, cos_ros_only),
        'bin_vectors': {
            'unified': unified_vec,
            'headers': header_vec,
            'ptext': ptext_vec,
            'rosettes': ros_vec,
        },
    }


# ============================================================
# R6: Section T Mediation (diagnostic)
# ============================================================

def r6_section_t_mediation(data):
    """R6: New diagnostic — is P-text/Rosettes overlap Section T mediated?

    Reports per-section fraction of shared vocabulary. No PASS/FAIL.
    """
    print("\n=== R6: Section T Mediation (diagnostic) ===")

    ptext_mids = data['ptext_all_mids']
    ros_all = data['ros_all_mids']
    section_middles = data['section_middles']

    # P-text/Rosettes shared vocabulary
    shared = ptext_mids & ros_all
    print(f"  P-text/Rosettes shared MIDDLEs: {len(shared)}")

    # Per-section: how many shared MIDDLEs appear in each section?
    section_hits = {}
    for section, sec_mids in sorted(section_middles.items()):
        section_shared = shared & sec_mids
        section_hits[section] = {
            'shared_in_section': len(section_shared),
            'fraction_of_shared': len(section_shared) / len(shared) if shared else 0,
            'section_total_mids': len(sec_mids),
        }
        print(f"  Section {section}: {len(section_shared)}/{len(shared)} shared MIDDLEs "
              f"({len(section_shared)/len(shared)*100:.1f}%)")

    # Also compute per-section Jaccard restricted to section vocabulary
    section_jaccards = {}
    for section, sec_mids in sorted(section_middles.items()):
        pt_in_sec = ptext_mids & sec_mids
        ros_in_sec = ros_all & sec_mids
        j = jaccard(pt_in_sec, ros_in_sec)
        section_jaccards[section] = {
            'jaccard': j,
            'ptext_in_section': len(pt_in_sec),
            'rosettes_in_section': len(ros_in_sec),
        }

    # Determine mediation pattern
    t_fraction = section_hits.get('T', {}).get('fraction_of_shared', 0)
    best_section = max(section_hits.items(),
                       key=lambda x: x[1]['shared_in_section'])[0] if section_hits else 'NONE'

    print(f"  Section T fraction: {t_fraction:.4f}")
    print(f"  Best section: {best_section}")

    return {
        'test': 'R6',
        'name': 'Section T Mediation (diagnostic)',
        'verdict': 'DIAGNOSTIC',
        'shared_vocabulary_size': len(shared),
        'per_section_coverage': section_hits,
        'per_section_jaccards': section_jaccards,
        'section_t_fraction': t_fraction,
        'best_section': best_section,
        'is_t_dominated': t_fraction > 0.60,
    }


# ============================================================
# R7: Indexing Specificity Comparison (diagnostic)
# ============================================================

def r7_indexing_specificity(data):
    """R7: New diagnostic — how specific is P-text vs Rosettes targeting?

    For each P-text folio and each rosette, find top-5 B folios by Jaccard.
    Compare overlap of top-5 sets. No PASS/FAIL.
    """
    print("\n=== R7: Indexing Specificity Comparison (diagnostic) ===")

    ptext_folio_mids = data['ptext_folio_mids']
    per_rosette_mids = data['per_rosette_mids']
    b_folio_mids = data['b_folio_mids']

    def top_5_targets(source_mids, b_folio_mids_dict):
        """Return top-5 B folios by Jaccard with source."""
        scores = []
        for folio, f_mids in b_folio_mids_dict.items():
            j = jaccard(source_mids, f_mids)
            scores.append((folio, j))
        scores.sort(key=lambda x: -x[1])
        return [f for f, _ in scores[:5]]

    # P-text: per-folio top-5 B targets
    pt_targets = {}
    for folio, mids in sorted(ptext_folio_mids.items()):
        if len(mids) < 3:  # skip folios with too few MIDDLEs
            continue
        pt_targets[folio] = top_5_targets(mids, b_folio_mids)

    # Rosettes: per-rosette top-5 B targets
    ros_targets = {}
    for rosette, mids in sorted(per_rosette_mids.items()):
        if len(mids) < 3:
            continue
        ros_targets[rosette] = top_5_targets(mids, b_folio_mids)

    # Mean intra-group overlap Jaccard of top-5 sets
    def mean_overlap(targets_dict):
        keys = sorted(targets_dict.keys())
        if len(keys) < 2:
            return 0.0
        overlaps = []
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                s1 = set(targets_dict[keys[i]])
                s2 = set(targets_dict[keys[j]])
                overlaps.append(jaccard(s1, s2))
        return sum(overlaps) / len(overlaps) if overlaps else 0.0

    pt_mean_overlap = mean_overlap(pt_targets)
    ros_mean_overlap = mean_overlap(ros_targets)

    # Cross-group overlap: P-text targets vs Rosettes targets
    cross_overlaps = []
    for pt_folio, pt_top5 in pt_targets.items():
        for ros_name, ros_top5 in ros_targets.items():
            cross_overlaps.append(jaccard(set(pt_top5), set(ros_top5)))
    cross_mean = sum(cross_overlaps) / len(cross_overlaps) if cross_overlaps else 0.0

    print(f"  P-text sources: {len(pt_targets)} folios")
    print(f"  Rosettes sources: {len(ros_targets)} rosettes")
    print(f"  P-text intra-group overlap: {pt_mean_overlap:.4f}")
    print(f"  Rosettes intra-group overlap: {ros_mean_overlap:.4f}")
    print(f"  Cross-group overlap: {cross_mean:.4f}")

    # Determine specificity
    if pt_mean_overlap < ros_mean_overlap:
        comparison = 'PTEXT_MORE_SPECIFIC'
    elif pt_mean_overlap > ros_mean_overlap:
        comparison = 'ROSETTES_MORE_SPECIFIC'
    else:
        comparison = 'SIMILAR_SPECIFICITY'

    print(f"  Comparison: {comparison}")

    return {
        'test': 'R7',
        'name': 'Indexing Specificity Comparison (diagnostic)',
        'verdict': 'DIAGNOSTIC',
        'ptext_sources': len(pt_targets),
        'rosettes_sources': len(ros_targets),
        'ptext_intra_overlap': pt_mean_overlap,
        'rosettes_intra_overlap': ros_mean_overlap,
        'cross_group_overlap': cross_mean,
        'specificity_comparison': comparison,
        'ptext_targets': {f: t for f, t in sorted(pt_targets.items())},
        'rosettes_targets': {r: t for r, t in sorted(ros_targets.items())},
    }


# ============================================================
# SYNTHESIS
# ============================================================

def synthesis(results):
    """Combine R1-R7 into integration verdict.

    Formula: R1 + R3 + R4 + R5 (I2_original from Phase 395 was FAIL)
    """
    r1 = results['R1']['verdict']
    r3 = results['R3']['verdict']
    r4 = results['R4']['verdict']
    r5 = results['R5']['verdict']

    components = {'R1': r1, 'R3': r3, 'R4': r4, 'R5': r5}
    pass_count = sum(1 for v in components.values() if v == 'PASS')

    if pass_count == 4:
        verdict = 'UNIFIED_CONFIRMED'
    elif pass_count == 3:
        verdict = 'UNIFIED_SUPPORTED'
    elif pass_count == 2:
        verdict = 'PARTIAL_OVERLAP'
    else:
        verdict = 'UNIFIED_REJECTED'

    return {
        'formula': 'R1 + R3 + (I2_original | R4) + R5',
        'i2_original_note': 'FAIL in Phase 395 (not re-tested, R4 carries this slot)',
        'components': components,
        'pass_count': f"{pass_count}/4",
        'verdict': verdict,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    data = load_data()

    results = {}
    results['R1'] = r1_bridge_density(data)
    results['R2'] = r2_grammar_divergence(data)
    results['R3'] = r3_vocabulary_overlap(data)
    results['R4'] = r4_paragraph_cotracking(data)
    results['R5'] = r5_union_bridge_prediction(data)
    results['R6'] = r6_section_t_mediation(data)
    results['R7'] = r7_indexing_specificity(data)

    synth = synthesis(results)
    results['synthesis'] = synth

    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    print(f"  Formula: {synth['formula']}")
    print(f"  Components: {synth['components']}")
    print(f"  Pass count: {synth['pass_count']}")
    print(f"  VERDICT: {synth['verdict']}")

    # Build output
    output = {
        'phase': 403,
        'name': 'PTEXT_ROSETTES_INTEGRATION_REVALIDATION',
        'supersedes': 'Phase 395 (PTEXT_ROSETTES_INDEXING_ARCHITECTURE) partial — 5 Rosettes-dependent tests',
        'data_sources': {
            'ptext': 'Transcript.azc() filtered by P placement (main transcript)',
            'rosettes': 'data/rosettes_annotated.json (corrected ZL transcription)',
            'bridge': 'bridge_selection.json (85 MIDDLEs)',
            'affordance': 'middle_affordance_table.json',
            'b_paragraphs': 'BFolioDecoder.analyze_folio_paragraphs()',
        },
        'test_count': 7,
        'counts': {
            'ptext_tokens': data['ptext_token_count'],
            'ptext_unique_mids': len(data['ptext_all_mids']),
            'ptext_folios': len(data['ptext_folios']),
            'rosettes_unique_mids': len(data['ros_all_mids']),
            'a_unique_mids': len(data['a_all_mids']),
            'b_unique_mids': len(data['b_all_mids']),
            'b_folios': len(data['b_folio_mids']),
            'b_paragraphs': len(data['para_records']),
            'bridge_middles': len(data['bridge_middles']),
        },
    }

    # Add test results
    for key in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'synthesis']:
        output[key] = results[key]

    output = round_floats(output)

    # Save
    out_path = PROJECT / 'phases' / 'ROSETTES_SYSTEM_REVALIDATION' / 'results' / 'ptext_rosettes_integration.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
