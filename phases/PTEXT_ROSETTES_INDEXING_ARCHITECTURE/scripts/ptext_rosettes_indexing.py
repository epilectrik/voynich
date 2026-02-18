#!/usr/bin/env python3
"""
Phase 395: P-Text / Rosettes Indexing Architecture

Tests whether P-text (Currier A-like tokens on AZC folios) and Rosettes labels
share a unified bridge-vocabulary indexing system spanning A -> AZC -> B.

Stage 1 (P1-P5): P-Text Characterization — P1 is GATE
Stage 2 (I1-I5): Integration Tests — gated on P1 PASS

Synthesis verdicts:
  UNIFIED_INDEXING               P1 + I1 + (I2|I3) + I4
  COINCIDENTAL                   P1 + I1 + !I2 + !I3
  BRIDGE_MEDIATED_BUT_INDEPENDENT P1 + !I1 + P2
  ROSETTES_UNIQUE                P1 + !I1 + !P2
  P_TEXT_DISTINCT                !P1 (Stage 2 skipped)
"""
import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy.stats import mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    Transcript, Morphology, RosettesAnalyzer,
    BFolioDecoder, BTokenAnalysis
)

RESULTS = ROOT / 'phases' / 'PTEXT_ROSETTES_INDEXING_ARCHITECTURE' / 'results'
RESULTS.mkdir(parents=True, exist_ok=True)

# ── Constants ────────────────────────────────────────────────────────────────

ROSETTES_FOLIOS = ['f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']
TARGET_FOLIOS = ['f111r', 'f108r', 'f76r', 'f108v', 'f116r']  # Phase 393 cross-ref targets

# f85v2 region classification (C1093)
LABEL_REGIONS = {'B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1'}
DESC_REGIONS = {'C2', 'N1', 'N2', 'V1', 'V2'}

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]  # Exclude bin 4 (BULK_OPERATIONAL)
KERNEL_CHARS = {'k', 'h', 'e'}  # C647
LINK_PREFIXES = {'lk', 'lo'}  # From _get_prefix_lane

N_BOOT = 5000
RNG_SEED = 42

# ── Utilities ────────────────────────────────────────────────────────────────

def round_floats(obj, decimals=4):
    """Recursive float rounder handling numpy types."""
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


def jaccard(s1, s2):
    """Jaccard similarity between two sets."""
    if not s1 and not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def cosine_sim(v1, v2):
    """Cosine similarity between two vectors."""
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def bin_vector(middle_set, mid_to_bin, bins=None):
    """Convert a set of MIDDLEs to a bin frequency vector."""
    if bins is None:
        bins = FUNCTIONAL_BINS
    counts = Counter()
    for mid in middle_set:
        b = mid_to_bin.get(mid)
        if b is not None and b in bins:
            counts[b] += 1
    total = sum(counts.values())
    if total == 0:
        return [0.0] * len(bins)
    return [counts.get(b, 0) / total for b in bins]


# ── Data Initialization ─────────────────────────────────────────────────────

print('=' * 70)
print('PHASE 395: P-TEXT / ROSETTES INDEXING ARCHITECTURE')
print('=' * 70)
print()

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()
rng = np.random.RandomState(RNG_SEED)

# Morphology cache
_morph_cache = {}
def get_middle(word):
    """Extract MIDDLE from word, return None if empty/uncertain/special."""
    if not word or not word.strip() or '*' in word:
        return None
    if word not in _morph_cache:
        m = morph.extract(word)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
        _morph_cache[word] = mid
    return _morph_cache[word]


# ── Load bridge MIDDLEs ──────────────────────────────────────────────────────

bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f'Bridge MIDDLEs loaded: {len(bridge_middles)}')

# ── Load affordance table ────────────────────────────────────────────────────

aff_path = ROOT / 'data' / 'middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)
middle_to_bin = {}
for mid_key, mid_val in aff_data.get('middles', {}).items():
    if isinstance(mid_val, dict) and 'affordance_bin' in mid_val:
        middle_to_bin[mid_key] = mid_val['affordance_bin']
print(f'Affordance mappings loaded: {len(middle_to_bin)}')

# ── P-text tokens and MIDDLEs ────────────────────────────────────────────────

print('\nBuilding P-text inventory...')
ptext_tokens = [t for t in tx.azc() if t.placement.startswith('P')
                and t.word.strip() and '*' not in t.word]

ptext_folio_mids = defaultdict(set)
ptext_all_mids = set()

for tok in ptext_tokens:
    mid = get_middle(tok.word)
    if mid:
        ptext_folio_mids[tok.folio].add(mid)
        ptext_all_mids.add(mid)

ptext_folios_found = sorted(ptext_folio_mids.keys())
print(f'  P-text tokens: {len(ptext_tokens)}')
print(f'  Unique MIDDLEs: {len(ptext_all_mids)}')
print(f'  Folios: {ptext_folios_found}')

# ── Rosettes tokens and MIDDLEs ──────────────────────────────────────────────

print('\nBuilding Rosettes inventory...')
ros_all_mids = set()
ros_label_mids = set()
ros_folio_mids = defaultdict(set)

for folio in ROSETTES_FOLIOS:
    toks = ra.get_tokens(folio)
    for tok in toks:
        mid = get_middle(tok.word)
        if mid:
            ros_all_mids.add(mid)
            ros_folio_mids[folio].add(mid)

# f85v2 label regions
for region in LABEL_REGIONS:
    toks = ra.get_tokens('f85v2', region)
    for tok in toks:
        mid = get_middle(tok.word)
        if mid:
            ros_label_mids.add(mid)

# Non-f85v2 Rosettes folios are structurally label-like (C1093)
for folio in ROSETTES_FOLIOS:
    if folio != 'f85v2':
        ros_label_mids.update(ros_folio_mids[folio])

print(f'  Rosettes all MIDDLEs: {len(ros_all_mids)}')
print(f'  Rosettes label MIDDLEs: {len(ros_label_mids)}')

# ── Currier A tokens and MIDDLEs ─────────────────────────────────────────────

print('\nBuilding Currier A inventory...')
a_folio_mids = defaultdict(set)
a_all_unique = set()

for tok in tx.currier_a():
    mid = get_middle(tok.word)
    if mid:
        a_folio_mids[tok.folio].add(mid)
        a_all_unique.add(mid)

a_all_unique_list = sorted(a_all_unique)
print(f'  A unique MIDDLEs: {len(a_all_unique)}, folios: {len(a_folio_mids)}')

# ── Currier B tokens and MIDDLEs ─────────────────────────────────────────────

print('\nBuilding Currier B inventory...')
b_folio_mids = defaultdict(set)
b_all_mids = set()

for tok in tx.currier_b():
    mid = get_middle(tok.word)
    if mid:
        b_folio_mids[tok.folio].add(mid)
        b_all_mids.add(mid)

b_all_folios = sorted(b_folio_mids.keys())
print(f'  B unique MIDDLEs: {len(b_all_mids)}, folios: {len(b_all_folios)}')

# ── B paragraph header/body MIDDLE sets ──────────────────────────────────────

print('\nComputing B paragraph header/body MIDDLE sets...')
para_records = []  # (folio, para_id, header_mids, body_mids)

for folio in b_all_folios:
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except Exception:
        continue
    for para in paragraphs:
        if not para.lines:
            continue
        header_mids = set()
        body_mids = set()
        for la in para.lines:
            line_mids = set()
            for btok in la.tokens:
                mid = get_middle(btok.word)
                if mid:
                    line_mids.add(mid)
            if la.paragraph_zone == 'HEADER':
                header_mids.update(line_mids)
            else:
                body_mids.update(line_mids)
        para_records.append((folio, para.paragraph_id, header_mids, body_mids))

print(f'  B paragraphs analyzed: {len(para_records)}')


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: P-TEXT CHARACTERIZATION
# ═══════════════════════════════════════════════════════════════════════════

print()
print('=' * 70)
print('STAGE 1: P-TEXT CHARACTERIZATION')
print('=' * 70)

# ── P1: P-Text Bridge Density [GATE] ────────────────────────────────────────

print('\nP1: P-Text Bridge Density [GATE]')

n_pt = len(ptext_all_mids)
pt_bridge = ptext_all_mids & bridge_middles
pt_bridge_frac = len(pt_bridge) / n_pt if n_pt > 0 else 0.0

ros_bridge_frac = len(ros_all_mids & bridge_middles) / len(ros_all_mids) if ros_all_mids else 0.0

# Bootstrap: sample same-size unique MIDDLE sets from A vocabulary
boot_fracs = []
a_pool = np.array(a_all_unique_list)
for _ in range(N_BOOT):
    sample = set(rng.choice(a_pool, size=min(n_pt, len(a_pool)), replace=False))
    boot_fracs.append(len(sample & bridge_middles) / len(sample) if sample else 0.0)

a_p95 = float(np.percentile(boot_fracs, 95))
percentile = float(np.mean(np.array(boot_fracs) <= pt_bridge_frac) * 100)
above_a = pt_bridge_frac > a_p95
within_50pct_ros = ros_bridge_frac > 0 and pt_bridge_frac >= 0.5 * ros_bridge_frac

p1_verdict = 'PASS' if above_a and within_50pct_ros else 'FAIL'

p1 = {
    'pt_bridge_count': len(pt_bridge),
    'pt_total_mids': n_pt,
    'pt_bridge_frac': pt_bridge_frac,
    'pt_bridge_list': sorted(pt_bridge),
    'ros_bridge_frac': ros_bridge_frac,
    'a_bootstrap_p95': a_p95,
    'a_bootstrap_mean': float(np.mean(boot_fracs)),
    'pt_percentile_in_a': percentile,
    'above_a_p95': above_a,
    'within_50pct_rosettes': within_50pct_ros,
    'verdict': p1_verdict,
}

print(f'  P-text bridge frac: {pt_bridge_frac:.4f} ({len(pt_bridge)}/{n_pt})')
print(f'  Rosettes bridge frac: {ros_bridge_frac:.4f}')
print(f'  A bootstrap p95: {a_p95:.4f}, mean: {float(np.mean(boot_fracs)):.4f}')
print(f'  P-text at {percentile:.1f}th percentile of A')
print(f'  Above A p95: {above_a}')
print(f'  Within 50% of Rosettes: {within_50pct_ros}')
print(f'  P1 VERDICT: {p1_verdict}')

# ── P2: P-Text Affordance Bin Profile ────────────────────────────────────────

print('\nP2: P-Text Affordance Bin Profile')

pt_vec = bin_vector(ptext_all_mids, middle_to_bin)
ros_vec = bin_vector(ros_all_mids, middle_to_bin)
p2_cosine = cosine_sim(pt_vec, ros_vec)
p2_verdict = 'PASS' if p2_cosine > 0.85 else 'FAIL'

bin_labels = {0: 'FLOW_TERM', 1: 'ROUTINE', 2: 'PRECISION', 3: 'COMPOUND',
              5: 'SETTLING', 6: 'HUB', 7: 'ENERGY', 8: 'STABILITY', 9: 'PHASE'}

p2 = {
    'cosine_similarity': p2_cosine,
    'threshold': 0.85,
    'pt_bin_vector': {bin_labels.get(b, str(b)): v for b, v in zip(FUNCTIONAL_BINS, pt_vec)},
    'ros_bin_vector': {bin_labels.get(b, str(b)): v for b, v in zip(FUNCTIONAL_BINS, ros_vec)},
    'verdict': p2_verdict,
}

print(f'  Cosine similarity (P-text vs Rosettes): {p2_cosine:.4f}')
print(f'  P-text bins: {", ".join(f"{bin_labels[b]}={v:.3f}" for b, v in zip(FUNCTIONAL_BINS, pt_vec))}')
print(f'  Rosettes bins: {", ".join(f"{bin_labels[b]}={v:.3f}" for b, v in zip(FUNCTIONAL_BINS, ros_vec))}')
print(f'  P2 VERDICT: {p2_verdict}')

# ── P3: C486 Bridge Mediation ────────────────────────────────────────────────

print('\nP3: C486 Bridge Mediation')

pt_bridges_set = ptext_all_mids & bridge_middles
pt_nonbridges_set = ptext_all_mids - bridge_middles

bridge_in_b = len(pt_bridges_set & b_all_mids)
bridge_b_rate = bridge_in_b / len(pt_bridges_set) if pt_bridges_set else 0.0

nonbridge_in_b = len(pt_nonbridges_set & b_all_mids)
nonbridge_b_rate = nonbridge_in_b / len(pt_nonbridges_set) if pt_nonbridges_set else 0.0

overall_in_b = len(ptext_all_mids & b_all_mids)
overall_b_rate = overall_in_b / len(ptext_all_mids) if ptext_all_mids else 0.0

p3_verdict = 'PASS' if nonbridge_b_rate < 0.50 else 'FAIL'

p3 = {
    'bridge_middles_count': len(pt_bridges_set),
    'bridge_in_b': bridge_in_b,
    'bridge_b_rate': bridge_b_rate,
    'nonbridge_middles_count': len(pt_nonbridges_set),
    'nonbridge_in_b': nonbridge_in_b,
    'nonbridge_b_rate': nonbridge_b_rate,
    'overall_in_b': overall_in_b,
    'overall_b_rate': overall_b_rate,
    'expected_c486': 0.767,
    'verdict': p3_verdict,
}

print(f'  Bridge MIDDLEs: {len(pt_bridges_set)}, in B: {bridge_in_b} ({bridge_b_rate:.4f})')
print(f'  Non-bridge MIDDLEs: {len(pt_nonbridges_set)}, in B: {nonbridge_in_b} ({nonbridge_b_rate:.4f})')
print(f'  Overall B-transmission: {overall_b_rate:.4f} (expected ~0.767)')
print(f'  P3 VERDICT: {p3_verdict}')

# ── P4: P-Text Folio Specificity vs Universality ────────────────────────────

print('\nP4: P-Text Folio Specificity')

pt_folios_with_data = [f for f in sorted(ptext_folio_mids.keys()) if ptext_folio_mids[f]]

pt_jaccards = []
for f1, f2 in combinations(pt_folios_with_data, 2):
    pt_jaccards.append(jaccard(ptext_folio_mids[f1], ptext_folio_mids[f2]))

# Currier A baseline (cap at 30 folios for speed)
a_folios_with_data = [f for f in sorted(a_folio_mids.keys()) if a_folio_mids[f]][:30]
a_jaccards = []
for f1, f2 in combinations(a_folios_with_data, 2):
    a_jaccards.append(jaccard(a_folio_mids[f1], a_folio_mids[f2]))

mean_pt_j = float(np.mean(pt_jaccards)) if pt_jaccards else 0.0
mean_a_j = float(np.mean(a_jaccards)) if a_jaccards else 0.0

if mean_pt_j > 0.30:
    p4_class = 'UNIVERSAL'
elif mean_pt_j < 0.15:
    p4_class = 'SPECIFIC'
else:
    p4_class = 'MODERATE'

p4 = {
    'pt_mean_jaccard': mean_pt_j,
    'pt_std_jaccard': float(np.std(pt_jaccards)) if pt_jaccards else 0.0,
    'pt_pairs_count': len(pt_jaccards),
    'pt_folios': pt_folios_with_data,
    'pt_folio_mid_counts': {f: len(ptext_folio_mids[f]) for f in pt_folios_with_data},
    'a_mean_jaccard': mean_a_j,
    'a_pairs_count': len(a_jaccards),
    'classification': p4_class,
    'verdict': p4_class,
}

print(f'  P-text mean Jaccard: {mean_pt_j:.4f} (std={p4["pt_std_jaccard"]:.4f}, {len(pt_jaccards)} pairs)')
print(f'  A mean Jaccard: {mean_a_j:.4f} ({len(a_jaccards)} pairs)')
print(f'  Per-folio MIDDLE counts: {dict(p4["pt_folio_mid_counts"])}')
print(f'  Classification: {p4_class}')

# ── P5: P-Text Kernel and LINK Absence ───────────────────────────────────────

print('\nP5: P-Text Kernel and LINK Absence')

n_tok = len(ptext_tokens)
kernel_count = 0
link_count = 0

for tok in ptext_tokens:
    m = morph.extract(tok.word)
    if m.middle and m.middle != '_EMPTY_' and any(c in m.middle for c in KERNEL_CHARS):
        kernel_count += 1
    if m.prefix and m.prefix in LINK_PREFIXES:
        link_count += 1

kernel_frac = kernel_count / n_tok if n_tok > 0 else 0.0
link_frac = link_count / n_tok if n_tok > 0 else 0.0

p5_verdict = 'PASS' if kernel_frac < 0.05 and link_frac < 0.05 else 'FAIL'

p5 = {
    'n_tokens': n_tok,
    'kernel_count': kernel_count,
    'kernel_frac': kernel_frac,
    'link_count': link_count,
    'link_frac': link_frac,
    'threshold': 0.05,
    'verdict': p5_verdict,
}

print(f'  Tokens: {n_tok}')
print(f'  Kernel hits: {kernel_count} ({kernel_frac:.4f})')
print(f'  LINK hits: {link_count} ({link_frac:.4f})')
print(f'  P5 VERDICT: {p5_verdict}')


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print()
print('-' * 70)
s1_verdicts = {'P1': p1_verdict, 'P2': p2_verdict, 'P3': p3_verdict,
               'P4': p4_class, 'P5': p5_verdict}
for k, v in s1_verdicts.items():
    print(f'  {k}: {v}')
print(f'  Gate P1: {"OPEN (Stage 2 enabled)" if p1_verdict == "PASS" else "CLOSED (Stage 2 skipped)"}')
print('-' * 70)


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: INTEGRATION TESTS (gated on P1 PASS)
# ═══════════════════════════════════════════════════════════════════════════

results = {
    'phase': 395,
    'name': 'PTEXT_ROSETTES_INDEXING_ARCHITECTURE',
    'counts': {
        'ptext_tokens': len(ptext_tokens),
        'ptext_unique_mids': len(ptext_all_mids),
        'ptext_folios': len(ptext_folios_found),
        'rosettes_all_mids': len(ros_all_mids),
        'rosettes_label_mids': len(ros_label_mids),
        'a_unique_mids': len(a_all_unique),
        'b_unique_mids': len(b_all_mids),
        'b_folios': len(b_all_folios),
        'b_paragraphs': len(para_records),
        'bridge_middles': len(bridge_middles),
    },
    'stage1': {
        'P1_bridge_density': p1,
        'P2_bin_profile': p2,
        'P3_c486_mediation': p3,
        'P4_folio_specificity': p4,
        'P5_kernel_link_absence': p5,
    },
    'stage2': {},
    'stage2_enabled': p1_verdict == 'PASS',
    'synthesis': None,
}

if p1_verdict == 'PASS':
    print()
    print('=' * 70)
    print('STAGE 2: INTEGRATION TESTS (P1 PASSED)')
    print('=' * 70)

    # ── I1: P-Text / Rosettes Label Vocabulary Overlap ───────────────────────

    print('\nI1: P-Text / Rosettes Label Vocabulary Overlap [KEY TEST]')

    i1_observed_j = jaccard(ptext_all_mids, ros_label_mids)
    i1_intersection = ptext_all_mids & ros_label_mids

    # Bootstrap: random A MIDDLE sets of same size vs Rosettes labels
    boot_jaccards = []
    for _ in range(N_BOOT):
        sample = set(rng.choice(a_pool, size=min(n_pt, len(a_pool)), replace=False))
        boot_jaccards.append(jaccard(sample, ros_label_mids))

    i1_p95 = float(np.percentile(boot_jaccards, 95))
    i1_p_val = float(np.mean(np.array(boot_jaccards) >= i1_observed_j))

    i1_verdict = 'PASS' if i1_observed_j > i1_p95 else 'FAIL'

    i1 = {
        'observed_jaccard': i1_observed_j,
        'ptext_unique_mids': len(ptext_all_mids),
        'rosettes_label_unique_mids': len(ros_label_mids),
        'intersection_size': len(i1_intersection),
        'intersection': sorted(i1_intersection),
        'bootstrap_p95': i1_p95,
        'bootstrap_mean': float(np.mean(boot_jaccards)),
        'p_val': i1_p_val,
        'verdict': i1_verdict,
    }

    print(f'  Observed Jaccard: {i1_observed_j:.4f}')
    print(f'  Intersection: {len(i1_intersection)} MIDDLEs')
    print(f'  Bootstrap p95: {i1_p95:.4f}, mean: {i1["bootstrap_mean"]:.4f}')
    print(f'  p-value: {i1_p_val:.4f}')
    print(f'  I1 VERDICT: {i1_verdict}')

    # ── I2: Cross-Reference Target Convergence ───────────────────────────────

    print('\nI2: Cross-Reference Target Convergence')

    target_set = set(TARGET_FOLIOS)
    target_fracs = []
    nontarget_fracs = []

    for folio in b_all_folios:
        mids = b_folio_mids.get(folio, set())
        if not mids:
            continue
        frac = len(ptext_all_mids & mids) / len(mids)
        if folio in target_set:
            target_fracs.append(frac)
        else:
            nontarget_fracs.append(frac)

    if target_fracs and nontarget_fracs:
        i2_stat, i2_p = mannwhitneyu(target_fracs, nontarget_fracs, alternative='greater')
        target_mean = float(np.mean(target_fracs))
        nontarget_mean = float(np.mean(nontarget_fracs))
        i2_verdict = 'PASS' if i2_p < 0.05 else 'FAIL'

        i2 = {
            'target_folios': TARGET_FOLIOS,
            'target_fracs': target_fracs,
            'target_mean': target_mean,
            'nontarget_mean': nontarget_mean,
            'nontarget_count': len(nontarget_fracs),
            'mannwhitney_stat': float(i2_stat),
            'p_val': float(i2_p),
            'note': 'underpowered (5 target vs ~77 non-target)',
            'verdict': i2_verdict,
        }
    else:
        i2 = {'verdict': 'INSUFFICIENT_DATA'}
        i2_verdict = 'INSUFFICIENT_DATA'

    print(f'  Target folios: {TARGET_FOLIOS}')
    print(f'  Target mean frac: {i2.get("target_mean", "N/A")}')
    print(f'  Non-target mean frac: {i2.get("nontarget_mean", "N/A")}')
    print(f'  p-value: {i2.get("p_val", "N/A")}')
    print(f'  I2 VERDICT: {i2_verdict}')

    # ── I3: Paragraph-Level Cross-Reference Resolution ───────────────────────

    print('\nI3: Paragraph-Level Cross-Reference Resolution')

    pt_overlaps = []
    ros_overlaps = []

    for folio, para_id, header_mids, body_mids in para_records:
        all_para_mids = header_mids | body_mids
        if not all_para_mids:
            continue
        pt_ovlp = len(ptext_all_mids & all_para_mids) / len(all_para_mids)
        ros_ovlp = len(ros_all_mids & all_para_mids) / len(all_para_mids)
        pt_overlaps.append(pt_ovlp)
        ros_overlaps.append(ros_ovlp)

    if len(pt_overlaps) >= 20:
        i3_rho, i3_p = spearmanr(pt_overlaps, ros_overlaps)
        i3_verdict = 'PASS' if i3_rho > 0.30 and i3_p < 0.05 else 'FAIL'
        i3 = {
            'n_paragraphs': len(pt_overlaps),
            'spearman_rho': float(i3_rho),
            'p_val': float(i3_p),
            'pt_overlap_mean': float(np.mean(pt_overlaps)),
            'ros_overlap_mean': float(np.mean(ros_overlaps)),
            'verdict': i3_verdict,
        }
    else:
        i3 = {'verdict': 'INSUFFICIENT_DATA', 'n_paragraphs': len(pt_overlaps)}
        i3_verdict = 'INSUFFICIENT_DATA'

    print(f'  Paragraphs: {i3.get("n_paragraphs", 0)}')
    print(f'  Spearman rho: {i3.get("spearman_rho", "N/A")}')
    print(f'  p-value: {i3.get("p_val", "N/A")}')
    print(f'  I3 VERDICT: {i3_verdict}')

    # ── I4: Unified Affordance Signature ─────────────────────────────────────

    print('\nI4: Unified Affordance Signature')

    unified_index = ptext_all_mids | ros_label_mids
    unified_vec = bin_vector(unified_index, middle_to_bin)

    header_mids_all = set()
    for _, _, h_mids, _ in para_records:
        header_mids_all.update(h_mids)
    header_vec = bin_vector(header_mids_all, middle_to_bin)

    i4_cosine = cosine_sim(unified_vec, header_vec)
    i4_verdict = 'PASS' if i4_cosine > 0.70 else 'FAIL'

    i4 = {
        'unified_index_size': len(unified_index),
        'header_mids_size': len(header_mids_all),
        'cosine_similarity': i4_cosine,
        'threshold': 0.70,
        'unified_vec': {bin_labels.get(b, str(b)): v for b, v in zip(FUNCTIONAL_BINS, unified_vec)},
        'header_vec': {bin_labels.get(b, str(b)): v for b, v in zip(FUNCTIONAL_BINS, header_vec)},
        'verdict': i4_verdict,
    }

    print(f'  Unified index size: {len(unified_index)} MIDDLEs')
    print(f'  Header MIDDLEs: {len(header_mids_all)}')
    print(f'  Cosine similarity: {i4_cosine:.4f}')
    print(f'  I4 VERDICT: {i4_verdict}')

    # ── I5: B-Paragraph Bridge Anatomy ───────────────────────────────────────

    print('\nI5: B-Paragraph Bridge Anatomy')

    header_bridge_fracs = []
    body_bridge_fracs = []

    for folio, para_id, header_mids, body_mids in para_records:
        if header_mids:
            h_frac = len(header_mids & bridge_middles) / len(header_mids)
            header_bridge_fracs.append(h_frac)
        if body_mids:
            b_frac = len(body_mids & bridge_middles) / len(body_mids)
            body_bridge_fracs.append(b_frac)

    if header_bridge_fracs and body_bridge_fracs:
        i5_stat, i5_p = mannwhitneyu(header_bridge_fracs, body_bridge_fracs, alternative='greater')
        i5_verdict = 'PASS' if i5_p < 0.05 else 'FAIL'
        i5 = {
            'n_header_paragraphs': len(header_bridge_fracs),
            'n_body_paragraphs': len(body_bridge_fracs),
            'header_mean_bridge_frac': float(np.mean(header_bridge_fracs)),
            'body_mean_bridge_frac': float(np.mean(body_bridge_fracs)),
            'mannwhitney_stat': float(i5_stat),
            'p_val': float(i5_p),
            'verdict': i5_verdict,
        }
    else:
        i5 = {'verdict': 'INSUFFICIENT_DATA'}
        i5_verdict = 'INSUFFICIENT_DATA'

    print(f'  Header mean bridge frac: {i5.get("header_mean_bridge_frac", "N/A")}')
    print(f'  Body mean bridge frac: {i5.get("body_mean_bridge_frac", "N/A")}')
    print(f'  p-value: {i5.get("p_val", "N/A")}')
    print(f'  I5 VERDICT: {i5_verdict}')

    # ── Stage 2 results ──────────────────────────────────────────────────────

    results['stage2'] = {
        'I1_vocab_overlap': i1,
        'I2_target_convergence': i2,
        'I3_paragraph_resolution': i3,
        'I4_unified_signature': i4,
        'I5_bridge_anatomy': i5,
    }

    # ── Synthesis ─────────────────────────────────────────────────────────────

    i1_pass = i1_verdict == 'PASS'
    i2_pass = i2_verdict == 'PASS'
    i3_pass = i3_verdict == 'PASS'
    i4_pass = i4_verdict == 'PASS'
    p2_pass = p2_verdict == 'PASS'

    if i1_pass and (i2_pass or i3_pass) and i4_pass:
        synthesis = 'UNIFIED_INDEXING'
    elif i1_pass and not i2_pass and not i3_pass:
        synthesis = 'COINCIDENTAL'
    elif not i1_pass and p2_pass:
        synthesis = 'BRIDGE_MEDIATED_BUT_INDEPENDENT'
    elif not i1_pass and not p2_pass:
        synthesis = 'ROSETTES_UNIQUE'
    else:
        synthesis = 'AMBIGUOUS'

    results['synthesis'] = synthesis

    print()
    print('=' * 70)
    print(f'SYNTHESIS VERDICT: {synthesis}')
    print('=' * 70)

    # Stage 2 summary
    print()
    print('-' * 70)
    s2_verdicts = {'I1': i1_verdict, 'I2': i2_verdict, 'I3': i3_verdict,
                   'I4': i4_verdict, 'I5': i5_verdict}
    for k, v in s2_verdicts.items():
        print(f'  {k}: {v}')
    print('-' * 70)

else:
    results['synthesis'] = 'P_TEXT_DISTINCT'
    print()
    print('=' * 70)
    print('STAGE 2 SKIPPED (P1 FAILED)')
    print('SYNTHESIS VERDICT: P_TEXT_DISTINCT')
    print('=' * 70)


# ── Save results ─────────────────────────────────────────────────────────────

out_path = RESULTS / 'ptext_rosettes_indexing.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2)
print(f'\nResults saved to: {out_path}')
