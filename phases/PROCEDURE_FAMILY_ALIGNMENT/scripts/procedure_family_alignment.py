#!/usr/bin/env python3
"""
Phase 604: Procedure-Family Alignment

Tests whether pseudo-Lull's operation families (distillation, fixation,
sublimation, dissolution) predict specific properties of Voynich operational
units when represented as control-signature bundles.

Two complementary approaches:
  A: Folio-level z-scored cosine matching (3D primary, 5D sensitivity)
  B: Paragraph zone distribution matching (derived profiles via mapping matrix)

Pre-registration: PREDICTIONS.md (SHA-256 verified before execution)
"""

import sys, os, json, math, hashlib, statistics
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt
from scipy import stats
import numpy as np

# ===========================================================================
# 0. Pre-registration hash verification
# ===========================================================================

PHASE_DIR = PROJECT_ROOT / 'phases' / 'PROCEDURE_FAMILY_ALIGNMENT'
PREDICTIONS_PATH = PHASE_DIR / 'PREDICTIONS.md'
EXPECTED_HASH = '2775f9751f2336ed16af27f6f5aa6bac59ba577e63578398efdd2bdbde80cfa8'

pred_hash = hashlib.sha256(PREDICTIONS_PATH.read_bytes()).hexdigest()
if pred_hash != EXPECTED_HASH:
    print(f'FATAL: PREDICTIONS.md hash mismatch')
    print(f'  Expected: {EXPECTED_HASH}')
    print(f'  Got:      {pred_hash}')
    sys.exit(1)
print(f'Pre-registration hash verified: {pred_hash[:16]}...')

# ===========================================================================
# 1. Load data
# ===========================================================================

# Phase 602 profile
PROFILE_PATH = PROJECT_ROOT / 'phases' / 'PSEUDO_LULL_CHARACTERIZATION' / 'results' / 'pseudo_lull_structural_profile.json'
with open(PROFILE_PATH) as f:
    profile = json.load(f)

# Regime mapping
with open(PROJECT_ROOT / 'data' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_map = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

# Folio operational profiles (k_ratio, h_ratio, e_ratio)
with open(PROJECT_ROOT / 'results' / 'folio_operational_profiles.json') as f:
    op_profiles = json.load(f)
folio_profiles = {p['folio']: p for p in op_profiles['profiles']}

# B macro scaffold (hazard_density, recovery_ops_count, kernel_contact_ratio)
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json') as f:
    scaffold_data = json.load(f)
scaffold_features = scaffold_data['features']

# Closure data (strong_close_fraction, profile/apparatus family)
CLOSURE_PATH = PROJECT_ROOT / 'phases' / 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES' / 'results' / 't0_opportunity_normalization.json'
with open(CLOSURE_PATH) as f:
    closure_data = json.load(f)
closure_covariates = closure_data['covariates']

# AXM decomposition
AXM_PATH = PROJECT_ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
with open(AXM_PATH) as f:
    axm_data = json.load(f)
axm_folio_data = axm_data.get('folio_data', {})

# Apparatus atlas (family A1/A2/A3)
ATLAS_PATH = PROJECT_ROOT / 'phases' / 'APPARATUS_ATLAS_BRIDGE_DESIGN' / 'results' / 't0_data_assembly.json'
with open(ATLAS_PATH) as f:
    atlas_data = json.load(f)
# Build per-folio apparatus family (data is under 'per_folio' key)
apparatus_family = {}
per_folio_data = atlas_data.get('per_folio', {})
for folio, fdata in per_folio_data.items():
    apparatus_family[folio] = fdata.get('family', 'UNKNOWN')
# Fallback: also extract from closure data profile field
for folio, cov in closure_covariates.items():
    if folio not in apparatus_family:
        prof = cov.get('profile', '')
        if prof.startswith('A1'):
            apparatus_family[folio] = 'A1'
        elif prof.startswith('A2'):
            apparatus_family[folio] = 'A2'
        elif prof.startswith('A3'):
            apparatus_family[folio] = 'A3'

# Paragraph zone assignments (C1398)
PARA_PATH = PROJECT_ROOT / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json'
with open(PARA_PATH) as f:
    para_data = json.load(f)
paragraph_labels = para_data['paragraph_labels']

print(f'Phase 602 profile: {len(profile["E1_chapters"])} chapters')
print(f'Regime map: {len(regime_map)} folios')
print(f'Folio profiles: {len(folio_profiles)} folios')
print(f'Scaffold: {len(scaffold_features)} folios')
print(f'Closure: {len(closure_covariates)} folios')
print(f'Apparatus family: {len(apparatus_family)} folios')
print(f'Paragraph labels: {len(paragraph_labels)} paragraphs')

# ===========================================================================
# 2. Compute Voynich per-folio safety metrics
# ===========================================================================

tx = Transcript()
morph = Morphology()

def max_consecutive_i(middle):
    max_run = current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

folio_token_counts = Counter()
folio_ey_counts = Counter()
folio_ii_counts = Counter()
folio_section = {}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if token.placement.startswith('L'):
        continue
    folio = token.folio
    folio_section[folio] = token.section
    m = morph.extract(w)
    if m.middle and m.middle != '_EMPTY_':
        head, mods, term, frame = decompose_middle_hmt(m.middle)
    else:
        head, term = None, None
    folio_token_counts[folio] += 1
    if head == 'e' and term == 'y':
        folio_ey_counts[folio] += 1
    if m.middle and max_consecutive_i(m.middle) >= 2:
        folio_ii_counts[folio] += 1

folio_ey_rate = {f: folio_ey_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_ii_rate = {f: folio_ii_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_safety_bal = {f: folio_ey_rate[f] - folio_ii_rate[f] for f in folio_ey_rate}

print(f'\nVoynich B folios computed: {len(folio_token_counts)}')
print(f'Mean ey_rate: {statistics.mean(folio_ey_rate.values()):.4f}')
print(f'Mean ii_rate: {statistics.mean(folio_ii_rate.values()):.4f}')

# ===========================================================================
# Helpers
# ===========================================================================

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

def compute_cv(values):
    if len(values) < 2:
        return 0.0
    m = statistics.mean(values)
    if m == 0:
        return 0.0
    return statistics.stdev(values) / m

def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))

def emd_1d(p, q):
    """Earth mover's distance between two 1D probability distributions."""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    if p.sum() > 0:
        p = p / p.sum()
    if q.sum() > 0:
        q = q / q.sum()
    return float(np.sum(np.abs(np.cumsum(p) - np.cumsum(q))))

def softmax(x):
    """Softmax normalization."""
    x = np.array(x, dtype=float)
    e = np.exp(x - np.max(x))
    return e / e.sum()

def rank_biserial(group1, group2):
    """Rank-biserial correlation (effect size for Mann-Whitney)."""
    if len(group1) == 0 or len(group2) == 0:
        return 0.0
    U, _ = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    n1, n2 = len(group1), len(group2)
    return float(1 - 2 * U / (n1 * n2))

# ===========================================================================
# S1: Calibration Anchor
# ===========================================================================

print('\n' + '='*60)
print('S1: Calibration Anchor (Stars R1 > R3 ey_rate)')
print('='*60)

stars_folios = [f for f in folio_section if folio_section[f] == 'S']
r1_ey = [folio_ey_rate[f] for f in stars_folios
         if f in folio_ey_rate and regime_map.get(f) == 'REGIME_1']
r3_ey = [folio_ey_rate[f] for f in stars_folios
         if f in folio_ey_rate and regime_map.get(f) == 'REGIME_3']

s1_U, s1_p = stats.mannwhitneyu(r1_ey, r3_ey, alternative='greater')
s1_pass = bool(s1_p < 0.05)

print(f'  R1 n={len(r1_ey)}, mean ey={statistics.mean(r1_ey):.4f}')
print(f'  R3 n={len(r3_ey)}, mean ey={statistics.mean(r3_ey):.4f}')
print(f'  U={s1_U}, p={s1_p:.6f} -> {"PASS" if s1_pass else "FAIL"}')

if not s1_pass:
    print('CALIBRATION_FAILURE: S1 did not pass. Stopping.')
    results = {'phase': 604, 'verdict': 'CALIBRATION_FAILURE',
               'S1': {'pass': False, 'U': float(s1_U), 'p': float(s1_p)}}
    out_path = PHASE_DIR / 'results' / 'procedure_family_alignment_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    sys.exit(0)

# ===========================================================================
# Stage 1a-b: Register filter + signature extraction
# ===========================================================================

print('\n' + '='*60)
print('Stage 1: PL Family Profile Extraction + Discrimination Gate')
print('='*60)

SELECTED_FAMILIES = ['distillation', 'fixation', 'sublimation', 'dissolution']
OPERATIONAL_PARTS = ['Practica', 'Mercuriorum', 'Furnis']

chapters = profile['E1_chapters']

# Build per-chapter 7D signatures for operational families
# Register filter: exclude theory_practice == "theoretical" from operational families
family_chapters = defaultdict(list)  # family -> list of 7D vectors
family_chapter_info = defaultdict(list)  # for debugging

for ch in chapters:
    fam = ch['primary_family']
    part = ch['part']

    # Only operational parts for all families
    if part not in OPERATIONAL_PARTS:
        continue

    chapter_lines = max(ch['en_line_end'] - ch['en_line_start'], 1)

    sig = {
        'monitoring_density': ch.get('monitoring_density', 0.0),
        'correction_rate': ch.get('correction_count', 0) / chapter_lines * 100,
        'heat_rate': ch.get('heat_count', 0) / chapter_lines * 100,
        'judgment_rate': ch.get('judgment_count', 0) / chapter_lines * 100,
        'termination_rate': ch.get('termination_count', 0) / chapter_lines * 100,
        'chain_rate': ch.get('chain_count', 0) / chapter_lines * 100,
        'operational_density': ch.get('operational_density', 0.0),
    }

    if fam in SELECTED_FAMILIES:
        # Register filter: exclude purely theoretical chapters from operational families
        if ch.get('theory_practice') == 'theoretical':
            continue
        family_chapters[fam].append(sig)
        family_chapter_info[fam].append({
            'part': part, 'number': ch['number'],
            'theory_practice': ch.get('theory_practice', '?')
        })

    # Theoretical negative control: chapters tagged theoretical/mixed from operational parts
    if fam == 'theoretical' or ch.get('theory_practice') == 'theoretical':
        family_chapters['theoretical_neg'].append(sig)

DIM_NAMES = ['monitoring_density', 'correction_rate', 'heat_rate',
             'judgment_rate', 'termination_rate', 'chain_rate', 'operational_density']

print('\nFamily chapter counts (after register filter):')
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    print(f'  {fam}: {len(family_chapters[fam])} chapters')

# ===========================================================================
# Stage 1c: Two-part discrimination gate
# ===========================================================================

# Gate A: Univariate Kruskal-Wallis + pairwise
print('\n--- Gate A (Univariate) ---')

gate_a_results = {}
bonferroni_alpha = 0.05 / len(DIM_NAMES)
n_bonferroni_pass = 0
n_nominal_pass = 0

for dim in DIM_NAMES:
    groups = [np.array([ch[dim] for ch in family_chapters[fam]])
              for fam in SELECTED_FAMILIES]
    H, p = stats.kruskal(*groups)
    gate_a_results[dim] = {'H': float(H), 'p': float(p),
                           'bonferroni_pass': bool(p < bonferroni_alpha),
                           'nominal_pass': bool(p < 0.05)}
    if p < bonferroni_alpha:
        n_bonferroni_pass += 1
    if p < 0.05:
        n_nominal_pass += 1
    print(f'  {dim}: H={H:.3f}, p={p:.4f} '
          f'{"***BONF" if p < bonferroni_alpha else ("*NOM" if p < 0.05 else "")}')

# Pairwise Mann-Whitney for key contrasts
pairwise_results = {}
key_pairs = [('distillation', 'fixation'), ('distillation', 'sublimation'),
             ('fixation', 'sublimation')]
for f1, f2 in key_pairs:
    pair_key = f'{f1}_vs_{f2}'
    pairwise_results[pair_key] = {}
    for dim in DIM_NAMES:
        v1 = [ch[dim] for ch in family_chapters[f1]]
        v2 = [ch[dim] for ch in family_chapters[f2]]
        if len(v1) >= 2 and len(v2) >= 2:
            U, p = stats.mannwhitneyu(v1, v2, alternative='two-sided')
            rb = rank_biserial(v1, v2)
            pairwise_results[pair_key][dim] = {
                'U': float(U), 'p': float(p), 'rank_biserial': rb
            }

gate_a_pass = bool(n_bonferroni_pass >= 1 or n_nominal_pass >= 2)
print(f'\nGate A: {n_bonferroni_pass} Bonferroni, {n_nominal_pass} nominal -> {"PASS" if gate_a_pass else "FAIL"}')

# Gate B: Multivariate LOO classifier
print('\n--- Gate B (Multivariate LOO) ---')

# Build matrix of all operational chapters with family labels
all_vecs = []
all_labels = []
for fam in SELECTED_FAMILIES:
    for ch in family_chapters[fam]:
        all_vecs.append([ch[d] for d in DIM_NAMES])
        all_labels.append(fam)

all_vecs = np.array(all_vecs)
all_labels = np.array(all_labels)

# LOO nearest-centroid classifier
correct = 0
for i in range(len(all_vecs)):
    test_vec = all_vecs[i]
    test_label = all_labels[i]
    # Compute centroids excluding this point
    centroids = {}
    for fam in SELECTED_FAMILIES:
        mask = (all_labels == fam)
        mask[i] = False
        if mask.sum() > 0:
            centroids[fam] = all_vecs[mask].mean(axis=0)
    # Find nearest centroid
    best_fam = min(centroids.keys(),
                   key=lambda f: np.linalg.norm(test_vec - centroids[f]))
    if best_fam == test_label:
        correct += 1

loo_accuracy = correct / len(all_vecs)
chance_level = max(Counter(all_labels).values()) / len(all_labels)
gate_b_pass = bool(loo_accuracy > chance_level)
print(f'  LOO accuracy: {correct}/{len(all_vecs)} = {loo_accuracy:.3f}')
print(f'  Chance level: {chance_level:.3f}')
print(f'  Gate B: {"PASS" if gate_b_pass else "FAIL"}')

stage1_pass = bool(gate_a_pass or gate_b_pass)
print(f'\n*** Stage 1 GATE: {"PASS" if stage1_pass else "FAIL"} ***')

if not stage1_pass:
    print('FAMILIES_NOT_SEPARABLE: Stage 1 gate did not pass. Stopping.')
    results = {
        'phase': 604, 'verdict': 'FAMILIES_NOT_SEPARABLE',
        'predictions_hash': pred_hash,
        'S1': {'pass': True, 'U': float(s1_U), 'p': float(s1_p)},
        'stage1': {
            'gate_a_pass': gate_a_pass,
            'gate_b_pass': gate_b_pass,
            'loo_accuracy': loo_accuracy,
            'chance_level': chance_level,
            'kruskal_wallis': gate_a_results,
        }
    }
    out_path = PHASE_DIR / 'results' / 'procedure_family_alignment_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    sys.exit(0)

# ===========================================================================
# Stage 1d: Family prototypes
# ===========================================================================

family_prototypes = {}
family_stds = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    if not family_chapters[fam]:
        continue
    vecs = np.array([[ch[d] for d in DIM_NAMES] for ch in family_chapters[fam]])
    family_prototypes[fam] = vecs.mean(axis=0)
    family_stds[fam] = vecs.std(axis=0)

print('\nFamily prototypes (7D):')
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    if fam in family_prototypes:
        proto = family_prototypes[fam]
        print(f'  {fam}: [{", ".join(f"{v:.3f}" for v in proto)}]')

# ===========================================================================
# Stage 2 Approach A: Folio-level control signature matching
# ===========================================================================

print('\n' + '='*60)
print('Stage 2 Approach A: Folio-Level Control Signature Matching')
print('='*60)

# Build Voynich folio signatures
# PRIMARY 3D: h_ratio, safety_balance, k_ratio
# SECONDARY +2D: strong_close_fraction, kernel_contact_ratio

b_folios = sorted(folio_token_counts.keys())

v_sigs_3d = {}
v_sigs_5d = {}
for f in b_folios:
    h_ratio = folio_profiles[f]['h_ratio'] if f in folio_profiles else None
    k_ratio = folio_profiles[f]['k_ratio'] if f in folio_profiles else None
    safety = folio_safety_bal.get(f, None)
    scf = closure_covariates[f]['strong_close_fraction'] if f in closure_covariates else None
    kcr = scaffold_features[f]['kernel_contact_ratio'] if f in scaffold_features else None

    if h_ratio is not None and safety is not None and k_ratio is not None:
        v_sigs_3d[f] = np.array([h_ratio, safety, k_ratio])
    if all(v is not None for v in [h_ratio, safety, k_ratio, scf, kcr]):
        v_sigs_5d[f] = np.array([h_ratio, safety, k_ratio, scf, kcr])

print(f'Folios with 3D signatures: {len(v_sigs_3d)}')
print(f'Folios with 5D signatures: {len(v_sigs_5d)}')

# Z-score PL prototypes and V signatures
# PL: z-score the 4 operational family prototypes across families
pl_proto_3d = {}
for fam in SELECTED_FAMILIES:
    proto = family_prototypes[fam]
    # Map: monitoring_density(0) -> h, correction_rate(1) -> safety, heat_rate(2) -> k
    pl_proto_3d[fam] = np.array([proto[0], proto[1], proto[2]])

# Include theoretical_neg
theo_proto = family_prototypes.get('theoretical_neg', np.zeros(len(DIM_NAMES)))
pl_proto_3d['theoretical_neg'] = np.array([theo_proto[0], theo_proto[1], theo_proto[2]])

# Z-score PL prototypes
all_pl_3d = np.array([pl_proto_3d[f] for f in SELECTED_FAMILIES])
pl_mean_3d = all_pl_3d.mean(axis=0)
pl_std_3d = all_pl_3d.std(axis=0)
pl_std_3d[pl_std_3d == 0] = 1.0

pl_z_3d = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    pl_z_3d[fam] = (pl_proto_3d[fam] - pl_mean_3d) / pl_std_3d

# Z-score V signatures
v_vals_3d = np.array(list(v_sigs_3d.values()))
v_mean_3d = v_vals_3d.mean(axis=0)
v_std_3d = v_vals_3d.std(axis=0)
v_std_3d[v_std_3d == 0] = 1.0

v_z_3d = {f: (v_sigs_3d[f] - v_mean_3d) / v_std_3d for f in v_sigs_3d}

# Assign folios to nearest OPERATIONAL family only (theoretical_neg is NOT assignable)
# Theoretical_neg is only used as a comparison metric in N1
assignments_a = {}
folio_cosines_a = {}
for f in v_z_3d:
    sims = {}
    for fam in SELECTED_FAMILIES + ['theoretical_neg']:
        sims[fam] = cosine_sim(v_z_3d[f], pl_z_3d[fam])
    # Assign only among operational families
    best = max(SELECTED_FAMILIES, key=lambda fam: sims[fam])
    assignments_a[f] = best
    folio_cosines_a[f] = sims

# Count assignments
a_counts = Counter(assignments_a.values())
print('\nApproach A assignments (3D, operational families only):')
for fam in SELECTED_FAMILIES:
    print(f'  {fam}: {a_counts.get(fam, 0)} folios')

# 5D sensitivity analysis
pl_proto_5d = {}
for fam in SELECTED_FAMILIES:
    proto = family_prototypes[fam]
    # monitoring(0)->h, correction(1)->safety, heat(2)->k, judgment(3)->scf, chain(5)->kcr
    pl_proto_5d[fam] = np.array([proto[0], proto[1], proto[2], proto[3], proto[5]])
pl_proto_5d['theoretical_neg'] = np.array([
    theo_proto[0], theo_proto[1], theo_proto[2], theo_proto[3], theo_proto[5]])

all_pl_5d = np.array([pl_proto_5d[f] for f in SELECTED_FAMILIES])
pl_mean_5d = all_pl_5d.mean(axis=0)
pl_std_5d = all_pl_5d.std(axis=0)
pl_std_5d[pl_std_5d == 0] = 1.0
pl_z_5d = {fam: (pl_proto_5d[fam] - pl_mean_5d) / pl_std_5d
           for fam in SELECTED_FAMILIES + ['theoretical_neg']}

v_vals_5d = np.array(list(v_sigs_5d.values()))
v_mean_5d = v_vals_5d.mean(axis=0)
v_std_5d = v_vals_5d.std(axis=0)
v_std_5d[v_std_5d == 0] = 1.0
v_z_5d = {f: (v_sigs_5d[f] - v_mean_5d) / v_std_5d for f in v_sigs_5d}

assignments_5d = {}
for f in v_z_5d:
    sims = {fam: cosine_sim(v_z_5d[f], pl_z_5d[fam])
            for fam in SELECTED_FAMILIES + ['theoretical_neg']}
    assignments_5d[f] = max(SELECTED_FAMILIES, key=lambda fam: sims[fam])

# D4: 3D vs 5D stability
common_folios = set(assignments_a) & set(assignments_5d)
d4_changed = sum(1 for f in common_folios if assignments_a[f] != assignments_5d[f])
d4_total = len(common_folios)
print(f'\nD4: 5D vs 3D changes: {d4_changed}/{d4_total} ({d4_changed/d4_total*100:.1f}%)')

# ===========================================================================
# Stage 2 Approach B: Paragraph zone distribution matching
# ===========================================================================

print('\n' + '='*60)
print('Stage 2 Approach B: Paragraph Zone Distribution Matching')
print('='*60)

# Derive zone profiles from PL signatures via mapping matrix
# First z-score the family prototypes across the 4 operational families
proto_matrix = np.array([family_prototypes[fam] for fam in SELECTED_FAMILIES])
proto_mean = proto_matrix.mean(axis=0)
proto_std = proto_matrix.std(axis=0)
proto_std[proto_std == 0] = 1.0

family_z = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    family_z[fam] = (family_prototypes[fam] - proto_mean) / proto_std

# Mapping matrix: PL 7D -> 4 zone weights
# DIM_NAMES: monitoring_density(0), correction_rate(1), heat_rate(2),
#            judgment_rate(3), termination_rate(4), chain_rate(5), operational_density(6)

def derive_zone_profile(z_vec):
    """Derive C1398 zone weights from z-scored 7D PL prototype."""
    zone0 = 0.5 * z_vec[2] + 0.3 * z_vec[6] + 0.2 * z_vec[4]  # THERMAL
    zone1 = 0.4 * z_vec[1] + 0.3 * z_vec[4] + 0.3 * z_vec[3]  # CONTAINMENT
    zone2 = 0.4 * z_vec[5] + 0.3 * z_vec[6] + 0.3 * z_vec[2]  # ITERATION
    zone3 = 0.5 * z_vec[0] + 0.3 * z_vec[3] + 0.2 * z_vec[1]  # MONITORING
    raw = np.array([zone0, zone1, zone2, zone3])
    return softmax(raw)

family_zone_profiles = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    family_zone_profiles[fam] = derive_zone_profile(family_z[fam])

print('Derived zone profiles (softmax-normalized):')
zone_names = ['THERMAL', 'CONTAIN', 'ITERATE', 'MONITOR']
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    zp = family_zone_profiles[fam]
    print(f'  {fam}: [{", ".join(f"{v:.3f}" for v in zp)}]')

# Compute per-folio zone distributions
folio_zone_dist = defaultdict(lambda: np.zeros(4))
folio_para_count = Counter()

for p in paragraph_labels:
    f = p['folio']
    z = p['cluster']
    folio_zone_dist[f][z] += 1
    folio_para_count[f] += 1

# Filter: >= 3 qualifying paragraphs
eligible_folios_b = {f for f in folio_zone_dist if folio_para_count[f] >= 3}

# Normalize to probability vectors
folio_zone_prob = {}
for f in eligible_folios_b:
    total = folio_zone_dist[f].sum()
    folio_zone_prob[f] = folio_zone_dist[f] / total if total > 0 else folio_zone_dist[f]

print(f'\nEligible folios (>= 3 paragraphs): {len(eligible_folios_b)}')

# Assign folios to nearest OPERATIONAL family by EMD (theoretical_neg not assignable)
assignments_b = {}
folio_emds_b = {}
for f in eligible_folios_b:
    emds = {}
    for fam in SELECTED_FAMILIES + ['theoretical_neg']:
        emds[fam] = emd_1d(folio_zone_prob[f], family_zone_profiles[fam])
    best = min(SELECTED_FAMILIES, key=lambda fam: emds[fam])
    assignments_b[f] = best
    folio_emds_b[f] = emds

b_counts = Counter(assignments_b.values())
print('\nApproach B assignments (operational families only):')
for fam in SELECTED_FAMILIES:
    print(f'  {fam}: {b_counts.get(fam, 0)} folios')

# ===========================================================================
# P3: Safety Discriminant (LOAD-BEARING)
# ===========================================================================

print('\n' + '='*60)
print('P3: Safety Discriminant (fixation < distillation on safety_balance)')
print('='*60)

dist_folios = [f for f, a in assignments_a.items() if a == 'distillation']
fix_folios = [f for f, a in assignments_a.items() if a == 'fixation']

dist_safety = [folio_safety_bal[f] for f in dist_folios if f in folio_safety_bal]
fix_safety = [folio_safety_bal[f] for f in fix_folios if f in folio_safety_bal]

if len(dist_safety) >= 2 and len(fix_safety) >= 2:
    p3_U, p3_p = stats.mannwhitneyu(dist_safety, fix_safety, alternative='greater')
    p3_rb = rank_biserial(dist_safety, fix_safety)
    p3_pass = bool(p3_p < 0.05)
else:
    p3_U, p3_p, p3_rb = 0, 1.0, 0.0
    p3_pass = False

print(f'  Distillation: n={len(dist_safety)}, mean safety_bal={statistics.mean(dist_safety) if dist_safety else 0:.4f}')
print(f'  Fixation: n={len(fix_safety)}, mean safety_bal={statistics.mean(fix_safety) if fix_safety else 0:.4f}')
print(f'  U={p3_U}, p={p3_p:.6f}, rank_biserial={p3_rb:.3f} -> {"PASS" if p3_pass else "FAIL"}')

# ===========================================================================
# P4: Monitoring Contrast (LOAD-BEARING)
# ===========================================================================

print('\n' + '='*60)
print('P4: Monitoring Contrast (sublimation > distillation on h_ratio)')
print('='*60)

sub_folios = [f for f, a in assignments_a.items() if a == 'sublimation']

dist_h = [folio_profiles[f]['h_ratio'] for f in dist_folios if f in folio_profiles]
sub_h = [folio_profiles[f]['h_ratio'] for f in sub_folios if f in folio_profiles]

if len(sub_h) >= 2 and len(dist_h) >= 2:
    p4_U, p4_p = stats.mannwhitneyu(sub_h, dist_h, alternative='greater')
    p4_rb = rank_biserial(sub_h, dist_h)
    p4_pass = bool(p4_p < 0.10)
else:
    p4_U, p4_p, p4_rb = 0, 1.0, 0.0
    p4_pass = False

print(f'  Sublimation: n={len(sub_h)}, mean h_ratio={statistics.mean(sub_h) if sub_h else 0:.4f}')
print(f'  Distillation: n={len(dist_h)}, mean h_ratio={statistics.mean(dist_h) if dist_h else 0:.4f}')
print(f'  U={p4_U}, p={p4_p:.6f}, rank_biserial={p4_rb:.3f} -> {"PASS" if p4_pass else "FAIL"}')

# ===========================================================================
# P1: Conservative Anchor (Distillation -> Stars / A3)
# ===========================================================================

print('\n' + '='*60)
print('P1: Conservative Anchor (Distillation -> Stars / A3)')
print('='*60)

# Fisher exact: distillation-assigned vs other for Stars membership
dist_set = set(dist_folios)
all_assigned = set(assignments_a.keys())

# Stars enrichment
n_dist_stars = sum(1 for f in dist_set if folio_section.get(f) == 'S')
n_dist_other_sec = len(dist_set) - n_dist_stars
n_nondist_stars = sum(1 for f in (all_assigned - dist_set) if folio_section.get(f) == 'S')
n_nondist_other_sec = len(all_assigned - dist_set) - n_nondist_stars

if n_dist_stars + n_nondist_stars > 0:
    p1_stars_or, p1_stars_p = stats.fisher_exact(
        [[n_dist_stars, n_dist_other_sec],
         [n_nondist_stars, n_nondist_other_sec]], alternative='greater')
else:
    p1_stars_or, p1_stars_p = 1.0, 1.0

# A3 enrichment
n_dist_a3 = sum(1 for f in dist_set if apparatus_family.get(f) == 'A3')
n_dist_other_app = sum(1 for f in dist_set if f in apparatus_family) - n_dist_a3
nondist_in_app = {f for f in (all_assigned - dist_set) if f in apparatus_family}
n_nondist_a3 = sum(1 for f in nondist_in_app if apparatus_family[f] == 'A3')
n_nondist_other_app = len(nondist_in_app) - n_nondist_a3

if n_dist_a3 + n_nondist_a3 > 0:
    p1_a3_or, p1_a3_p = stats.fisher_exact(
        [[n_dist_a3, n_dist_other_app],
         [n_nondist_a3, n_nondist_other_app]], alternative='greater')
else:
    p1_a3_or, p1_a3_p = 1.0, 1.0

# Within-stratum: among A3 folios, distillation-assigned have higher k_ratio
a3_folios_all = [f for f in all_assigned if apparatus_family.get(f) == 'A3']
a3_dist_k = [folio_profiles[f]['k_ratio'] for f in a3_folios_all
             if f in dist_set and f in folio_profiles]
a3_nondist_k = [folio_profiles[f]['k_ratio'] for f in a3_folios_all
                if f not in dist_set and f in folio_profiles]

if len(a3_dist_k) >= 2 and len(a3_nondist_k) >= 2:
    p1_ws_U, p1_ws_p = stats.mannwhitneyu(a3_dist_k, a3_nondist_k, alternative='greater')
else:
    p1_ws_U, p1_ws_p = 0, 1.0

p1_pass = bool(p1_stars_p < 0.10 or p1_a3_p < 0.10 or p1_ws_p < 0.10)

print(f'  Stars enrichment: OR={p1_stars_or:.3f}, p={p1_stars_p:.4f}')
print(f'  A3 enrichment: OR={p1_a3_or:.3f}, p={p1_a3_p:.4f}')
print(f'  Within-A3 k_ratio: dist={statistics.mean(a3_dist_k) if a3_dist_k else 0:.4f} vs non={statistics.mean(a3_nondist_k) if a3_nondist_k else 0:.4f}, p={p1_ws_p:.4f}')
print(f'  -> {"PASS" if p1_pass else "FAIL"}')

# ===========================================================================
# P2: Bold Target (Fixation -> A2 / Herbal)
# ===========================================================================

print('\n' + '='*60)
print('P2: Bold Target (Fixation -> A2 / Herbal)')
print('='*60)

fix_set = set(fix_folios)

# Herbal enrichment
n_fix_herbal = sum(1 for f in fix_set if folio_section.get(f) == 'H')
n_fix_other_sec = len(fix_set) - n_fix_herbal
n_nonfix_herbal = sum(1 for f in (all_assigned - fix_set) if folio_section.get(f) == 'H')
n_nonfix_other_sec = len(all_assigned - fix_set) - n_nonfix_herbal

if n_fix_herbal + n_nonfix_herbal > 0:
    p2_herbal_or, p2_herbal_p = stats.fisher_exact(
        [[n_fix_herbal, n_fix_other_sec],
         [n_nonfix_herbal, n_nonfix_other_sec]], alternative='greater')
else:
    p2_herbal_or, p2_herbal_p = 1.0, 1.0

# A2 enrichment
n_fix_a2 = sum(1 for f in fix_set if apparatus_family.get(f) == 'A2')
n_fix_other_app = sum(1 for f in fix_set if f in apparatus_family) - n_fix_a2
nonfix_in_app = {f for f in (all_assigned - fix_set) if f in apparatus_family}
n_nonfix_a2 = sum(1 for f in nonfix_in_app if apparatus_family[f] == 'A2')
n_nonfix_other_app = len(nonfix_in_app) - n_nonfix_a2

if n_fix_a2 + n_nonfix_a2 > 0:
    p2_a2_or, p2_a2_p = stats.fisher_exact(
        [[n_fix_a2, n_fix_other_app],
         [n_nonfix_a2, n_nonfix_other_app]], alternative='greater')
else:
    p2_a2_or, p2_a2_p = 1.0, 1.0

# Within-stratum: among Herbal, fixation-assigned have lower safety_balance
herbal_folios_all = [f for f in all_assigned if folio_section.get(f) == 'H']
herb_fix_safety = [folio_safety_bal[f] for f in herbal_folios_all
                   if f in fix_set and f in folio_safety_bal]
herb_nonfix_safety = [folio_safety_bal[f] for f in herbal_folios_all
                      if f not in fix_set and f in folio_safety_bal]

if len(herb_fix_safety) >= 2 and len(herb_nonfix_safety) >= 2:
    p2_ws_U, p2_ws_p = stats.mannwhitneyu(herb_nonfix_safety, herb_fix_safety, alternative='greater')
else:
    p2_ws_U, p2_ws_p = 0, 1.0

p2_pass = bool(p2_herbal_p < 0.10 or p2_a2_p < 0.10 or p2_ws_p < 0.10)

print(f'  Herbal enrichment: OR={p2_herbal_or:.3f}, p={p2_herbal_p:.4f}')
print(f'  A2 enrichment: OR={p2_a2_or:.3f}, p={p2_a2_p:.4f}')
print(f'  Within-Herbal safety_bal: fix={statistics.mean(herb_fix_safety) if herb_fix_safety else 0:.4f} vs non={statistics.mean(herb_nonfix_safety) if herb_nonfix_safety else 0:.4f}, p={p2_ws_p:.4f}')
print(f'  -> {"PASS" if p2_pass else "FAIL"}')

# ===========================================================================
# P5: Cross-Approach Concordance (Diagnostic)
# ===========================================================================

print('\n' + '='*60)
print('P5: Cross-Approach Concordance')
print('='*60)

common_ab = set(assignments_a) & set(assignments_b)
if common_ab:
    # Cohen's kappa
    labels_a = [assignments_a[f] for f in sorted(common_ab)]
    labels_b = [assignments_b[f] for f in sorted(common_ab)]

    # Compute kappa manually
    all_cats = sorted(set(labels_a) | set(labels_b))
    n = len(labels_a)
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agree / n

    # Expected agreement
    pe = 0
    for cat in all_cats:
        na = sum(1 for x in labels_a if x == cat)
        nb = sum(1 for x in labels_b if x == cat)
        pe += (na / n) * (nb / n)

    kappa = (po - pe) / (1 - pe) if pe < 1 else 0.0
    p5_pass = bool(kappa > 0.10)
    print(f'  Common folios: {len(common_ab)}')
    print(f'  Agreement: {agree}/{n} = {po:.3f}')
    print(f'  Kappa: {kappa:.3f} -> {"PASS" if p5_pass else "FAIL"}')
else:
    kappa = 0.0
    p5_pass = False
    po = 0.0
    print('  No common folios between approaches')

# ===========================================================================
# N1: Theoretical Negative Control
# ===========================================================================

print('\n' + '='*60)
print('N1: Theoretical Negative Control')
print('='*60)

# Approach A: mean cosine similarity of each family prototype to all folios
mean_cosines_a = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    sims = [folio_cosines_a[f][fam] for f in folio_cosines_a]
    mean_cosines_a[fam] = statistics.mean(sims)

# Approach B: mean EMD of each family profile to all eligible folios
mean_emds_b = {}
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    emds = [folio_emds_b[f][fam] for f in folio_emds_b]
    mean_emds_b[fam] = statistics.mean(emds)

# Theoretical should be worst (lowest cosine in A, highest EMD in B)
worst_cosine = min(mean_cosines_a, key=mean_cosines_a.get)
worst_emd = max(mean_emds_b, key=mean_emds_b.get)

n1_a_pass = (worst_cosine == 'theoretical_neg')
n1_b_pass = (worst_emd == 'theoretical_neg')
n1_pass = bool(n1_a_pass and n1_b_pass)

print('  Approach A mean cosines:')
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    print(f'    {fam}: {mean_cosines_a[fam]:.4f} {"<-- WORST" if fam == worst_cosine else ""}')
print('  Approach B mean EMDs:')
for fam in SELECTED_FAMILIES + ['theoretical_neg']:
    print(f'    {fam}: {mean_emds_b[fam]:.4f} {"<-- WORST" if fam == worst_emd else ""}')
print(f'  N1: {"PASS" if n1_pass else "FAIL"} (A: {n1_a_pass}, B: {n1_b_pass})')

# ===========================================================================
# N2: Permutation Control
# ===========================================================================

print('\n' + '='*60)
print('N2: Permutation Control')
print('='*60)

# Permutation test: shuffle PL family labels on prototypes, re-assign folios,
# re-compute P3+P4 combined test statistic. Real labeling should produce
# stronger directional effects than shuffled labeling.

def compute_directional_score(assignments, folio_safety, folio_h, family_names):
    """Compute combined directional score:
    (distillation safety - fixation safety) + (sublimation h - distillation h)
    Higher = more aligned with predictions."""
    dist_f = [f for f, a in assignments.items() if a == family_names[0]]  # "distillation" role
    fix_f = [f for f, a in assignments.items() if a == family_names[1]]   # "fixation" role
    sub_f = [f for f, a in assignments.items() if a == family_names[2]]   # "sublimation" role

    # P3 direction: distillation safety > fixation safety
    dist_s = [folio_safety[f] for f in dist_f if f in folio_safety]
    fix_s = [folio_safety[f] for f in fix_f if f in folio_safety]
    p3_effect = (statistics.mean(dist_s) - statistics.mean(fix_s)) if (dist_s and fix_s) else 0.0

    # P4 direction: sublimation h > distillation h
    sub_hr = [folio_h[f] for f in sub_f if f in folio_h]
    dist_hr = [folio_h[f] for f in dist_f if f in folio_h]
    p4_effect = (statistics.mean(sub_hr) - statistics.mean(dist_hr)) if (sub_hr and dist_hr) else 0.0

    return p3_effect + p4_effect

# Build folio h_ratio dict for convenience
folio_h_ratio = {p['folio']: p['h_ratio'] for p in op_profiles['profiles']}

# Real score
real_score = compute_directional_score(
    assignments_a, folio_safety_bal, folio_h_ratio,
    ['distillation', 'fixation', 'sublimation'])

# Permutation test
n_perms = 1000
perm_scores = []
rng = np.random.RandomState(42)

for _ in range(n_perms):
    shuffled_fams = list(SELECTED_FAMILIES)
    rng.shuffle(shuffled_fams)
    # Build shuffled prototypes (swap which PL prototype gets which family label)
    shuffled_z = {}
    for i, orig_fam in enumerate(SELECTED_FAMILIES):
        shuffled_z[shuffled_fams[i]] = pl_z_3d[orig_fam]

    # Re-assign folios using shuffled prototypes
    perm_assignments = {}
    for f in v_z_3d:
        sims = {fam: cosine_sim(v_z_3d[f], shuffled_z[fam])
                for fam in SELECTED_FAMILIES}
        perm_assignments[f] = max(SELECTED_FAMILIES, key=lambda fam: sims[fam])

    # Compute directional score with the shuffled labels
    score = compute_directional_score(
        perm_assignments, folio_safety_bal, folio_h_ratio,
        ['distillation', 'fixation', 'sublimation'])
    perm_scores.append(score)

n2_percentile = sum(1 for ps in perm_scores if ps >= real_score) / n_perms
n2_pass = bool(n2_percentile < 0.05)

print(f'  Real directional score: {real_score:.6f}')
print(f'  Permutation 95th percentile: {sorted(perm_scores)[int(0.95 * n_perms)]:.6f}')
print(f'  Fraction >= real: {n2_percentile:.4f}')
print(f'  N2: {"PASS" if n2_pass else "FAIL"}')

# ===========================================================================
# D1-D5: Diagnostics
# ===========================================================================

print('\n' + '='*60)
print('Diagnostics')
print('='*60)

# D1: Fixation vs distillation effect size on safety_balance
print(f'\nD1: Fixation vs distillation safety_balance rank-biserial = {p3_rb:.3f}')

# D2: Fixation vs sublimation effect size on safety_balance
sub_safety = [folio_safety_bal[f] for f in sub_folios if f in folio_safety_bal]
if len(fix_safety) >= 2 and len(sub_safety) >= 2:
    d2_rb = rank_biserial(sub_safety, fix_safety)
    print(f'D2: Fixation vs sublimation safety_balance rank-biserial = {d2_rb:.3f}')
    print(f'    Sublimation mean: {statistics.mean(sub_safety):.4f}, Fixation mean: {statistics.mean(fix_safety):.4f}')
else:
    d2_rb = 0.0
    print(f'D2: Insufficient data (sub n={len(sub_safety)}, fix n={len(fix_safety)})')

# D3: Dissolution assignment profile
diss_folios = [f for f, a in assignments_a.items() if a == 'dissolution']
diss_sections = Counter(folio_section.get(f, '?') for f in diss_folios)
diss_regimes = Counter(regime_map.get(f, '?') for f in diss_folios)
diss_apparatus = Counter(apparatus_family.get(f, '?') for f in diss_folios)
print(f'\nD3: Dissolution-assigned folios (n={len(diss_folios)}):')
print(f'    Sections: {dict(diss_sections)}')
print(f'    REGIMEs: {dict(diss_regimes)}')
print(f'    Apparatus: {dict(diss_apparatus)}')

# D4 already computed above
print(f'\nD4: 5D vs 3D assignment changes: {d4_changed}/{d4_total}')

# D5: Per-family supplementary validation
print('\nD5: Per-family supplementary metrics:')
for fam in SELECTED_FAMILIES:
    fam_folios = [f for f, a in assignments_a.items() if a == fam]
    axm_vals = [axm_folio_data[f]['axm_self'] for f in fam_folios if f in axm_folio_data]
    scf_vals = [closure_covariates[f]['strong_close_fraction'] for f in fam_folios if f in closure_covariates]
    app_dist = Counter(apparatus_family.get(f, '?') for f in fam_folios)
    sec_dist = Counter(folio_section.get(f, '?') for f in fam_folios)
    reg_dist = Counter(regime_map.get(f, '?') for f in fam_folios)

    print(f'  {fam} (n={len(fam_folios)}):')
    print(f'    mean axm_self: {statistics.mean(axm_vals):.4f}' if axm_vals else '    axm_self: N/A')
    print(f'    mean strong_close_frac: {statistics.mean(scf_vals):.4f}' if scf_vals else '    strong_close_frac: N/A')
    print(f'    apparatus: {dict(app_dist)}')
    print(f'    sections: {dict(sec_dist)}')
    print(f'    regimes: {dict(reg_dist)}')

# ===========================================================================
# Verdict
# ===========================================================================

print('\n' + '='*60)
print('VERDICT')
print('='*60)

p_tests = {'P1': p1_pass, 'P2': p2_pass, 'P3': p3_pass, 'P4': p4_pass}
n_tests = {'N1': n1_pass, 'N2': n2_pass}
n_p_pass = sum(p_tests.values())

doctrinal_pass = p3_pass or p4_pass
localization_pass = p1_pass or p2_pass

if not (n1_pass and n2_pass):
    if not n1_pass:
        verdict = 'SPECIFICITY_FAILURE'
    else:
        verdict = 'ALIGNMENT_NOT_SIGNIFICANT'
elif doctrinal_pass and localization_pass:
    verdict = 'PROCEDURE_FAMILY_ALIGNMENT_CONFIRMED'
elif doctrinal_pass and not localization_pass:
    verdict = 'DOCTRINAL_ALIGNMENT_WITHOUT_LOCALIZATION'
elif localization_pass and not doctrinal_pass:
    verdict = 'LOCALIZATION_WITHOUT_DOCTRINE'
else:
    verdict = 'PROCEDURE_FAMILY_ALIGNMENT_NOT_CONFIRMED'

print(f'\nTests: P1={p1_pass}, P2={p2_pass}, P3={p3_pass}, P4={p4_pass}')
print(f'       N1={n1_pass}, N2={n2_pass}, P5={p5_pass}')
print(f'Verdict: {verdict}')

# ===========================================================================
# Output JSON
# ===========================================================================

results = {
    'phase': 604,
    'predictions_hash': pred_hash,
    'verdict': verdict,
    'S1': {
        'pass': True,
        'stars_r1_n': len(r1_ey),
        'stars_r3_n': len(r3_ey),
        'stars_r1_mean_ey': float(statistics.mean(r1_ey)),
        'stars_r3_mean_ey': float(statistics.mean(r3_ey)),
        'U': float(s1_U),
        'p': float(s1_p),
    },
    'stage1': {
        'family_chapter_counts': {fam: len(family_chapters[fam]) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
        'gate_a': {
            'pass': bool(gate_a_pass),
            'n_bonferroni': n_bonferroni_pass,
            'n_nominal': n_nominal_pass,
            'kruskal_wallis': gate_a_results,
        },
        'gate_b': {
            'pass': bool(gate_b_pass),
            'loo_accuracy': float(loo_accuracy),
            'chance_level': float(chance_level),
            'n_chapters': len(all_vecs),
        },
        'pairwise': pairwise_results,
        'prototypes': {fam: family_prototypes[fam].tolist() for fam in SELECTED_FAMILIES + ['theoretical_neg']
                       if fam in family_prototypes},
        'prototype_dims': DIM_NAMES,
    },
    'approach_a': {
        'n_folios': len(v_sigs_3d),
        'assignments': {fam: a_counts.get(fam, 0) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
        'mean_cosines': {fam: float(mean_cosines_a[fam]) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
    },
    'approach_b': {
        'n_eligible_folios': len(eligible_folios_b),
        'assignments': {fam: b_counts.get(fam, 0) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
        'derived_zone_profiles': {fam: family_zone_profiles[fam].tolist()
                                   for fam in SELECTED_FAMILIES + ['theoretical_neg']},
        'mean_emds': {fam: float(mean_emds_b[fam]) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
    },
    'P3': {
        'pass': bool(p3_pass),
        'distillation_n': len(dist_safety),
        'fixation_n': len(fix_safety),
        'distillation_mean_safety': float(statistics.mean(dist_safety)) if dist_safety else None,
        'fixation_mean_safety': float(statistics.mean(fix_safety)) if fix_safety else None,
        'U': float(p3_U),
        'p': float(p3_p),
        'rank_biserial': float(p3_rb),
    },
    'P4': {
        'pass': bool(p4_pass),
        'sublimation_n': len(sub_h),
        'distillation_n': len(dist_h),
        'sublimation_mean_h': float(statistics.mean(sub_h)) if sub_h else None,
        'distillation_mean_h': float(statistics.mean(dist_h)) if dist_h else None,
        'U': float(p4_U),
        'p': float(p4_p),
        'rank_biserial': float(p4_rb),
    },
    'P1': {
        'pass': bool(p1_pass),
        'stars_enrichment_p': float(p1_stars_p),
        'stars_enrichment_or': float(p1_stars_or),
        'a3_enrichment_p': float(p1_a3_p),
        'a3_enrichment_or': float(p1_a3_or),
        'within_a3_p': float(p1_ws_p),
        'within_a3_dist_k_n': len(a3_dist_k),
        'within_a3_nondist_k_n': len(a3_nondist_k),
    },
    'P2': {
        'pass': bool(p2_pass),
        'herbal_enrichment_p': float(p2_herbal_p),
        'herbal_enrichment_or': float(p2_herbal_or),
        'a2_enrichment_p': float(p2_a2_p),
        'a2_enrichment_or': float(p2_a2_or),
        'within_herbal_p': float(p2_ws_p),
        'within_herbal_fix_n': len(herb_fix_safety),
        'within_herbal_nonfix_n': len(herb_nonfix_safety),
    },
    'P5': {
        'pass': bool(p5_pass),
        'n_common_folios': len(common_ab),
        'agreement': float(po),
        'kappa': float(kappa),
    },
    'N1': {
        'pass': bool(n1_pass),
        'approach_a_worst': worst_cosine,
        'approach_b_worst': worst_emd,
        'mean_cosines': {fam: float(mean_cosines_a[fam]) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
        'mean_emds': {fam: float(mean_emds_b[fam]) for fam in SELECTED_FAMILIES + ['theoretical_neg']},
    },
    'N2': {
        'pass': bool(n2_pass),
        'real_directional_score': float(real_score),
        'perm_95th': float(sorted(perm_scores)[int(0.95 * n_perms)]),
        'fraction_exceeding': float(n2_percentile),
        'n_permutations': n_perms,
    },
    'diagnostics': {
        'D1_fix_vs_dist_safety_rb': float(p3_rb),
        'D2_fix_vs_sub_safety_rb': float(d2_rb),
        'D3_dissolution_sections': dict(diss_sections),
        'D3_dissolution_regimes': dict(diss_regimes),
        'D3_dissolution_apparatus': dict(diss_apparatus),
        'D4_5d_vs_3d_changed': d4_changed,
        'D4_5d_vs_3d_total': d4_total,
    },
    'summary': {
        'n_passing_p': n_p_pass,
        'tests': {k: 'PASS' if v else 'FAIL' for k, v in p_tests.items()},
        'controls': {k: 'PASS' if v else 'FAIL' for k, v in n_tests.items()},
        'diagnostic_p5': 'PASS' if p5_pass else 'FAIL',
    },
}

out_path = PHASE_DIR / 'results' / 'procedure_family_alignment_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f'\nResults written to {out_path}')
print(f'VERDICT: {verdict}')
