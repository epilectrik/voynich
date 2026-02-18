#!/usr/bin/env python3
"""Phase 390: Bridge Backbone Manuscript Survey (6 predictions).

Tests whether bridge density varies across the manuscript and whether
it mediates the Rosettes-Section T correlation (C1090).
"""
import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()

results = {
    'phase': 390,
    'name': 'BRIDGE_BACKBONE_MANUSCRIPT_SURVEY',
    'test_count': 6,
    'verdicts': {},
}

def round_floats(obj, decimals=4):
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return str(obj)
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, decimals) for v in obj]
    return obj

def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0

# ============================================================
# LOAD PRE-COMPUTED DATA
# ============================================================
print("Loading pre-computed data...")

# 1. Bridge MIDDLEs
bridge_path = ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

# 2. REGIME mapping
regime_path = ROOT / 'data/regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {}
for folio, info in regime_data.get('regime_assignments', {}).items():
    folio_regime[folio] = info.get('regime', 'UNKNOWN')
print(f"  REGIME mappings: {len(folio_regime)}")

# ============================================================
# PRE-COMPUTE: Per-folio MIDDLE sets, bridge density, sections
# ============================================================
print("Computing per-folio bridge density...")

# Build per-folio data (exclude Rosettes for manuscript survey, include for P5)
folio_middles = defaultdict(set)       # folio -> set of unique MIDDLEs
folio_sections = {}                     # folio -> section code
folio_languages = defaultdict(set)      # folio -> set of languages (A, B, NA)
folio_token_counts = Counter()

# Section-level MIDDLE sets (for Jaccard)
section_middles = defaultdict(set)

for tok in tx.all():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    m = morph.extract(tok.word)
    if m.middle:
        folio_middles[tok.folio].add(m.middle)
        folio_sections[tok.folio] = tok.section
        folio_languages[tok.folio].add(tok.language)
        folio_token_counts[tok.folio] += 1
        section_middles[tok.section].add(m.middle)

# Compute bridge density per folio
folio_bridge_density = {}
for folio, mids in folio_middles.items():
    bridge_count = len(mids & bridge_middles)
    folio_bridge_density[folio] = bridge_count / len(mids) if mids else 0

# Rosettes MIDDLE sets (all folios combined)
ros_all_middles = set()
for folio in ra.ROSETTES_FOLIOS:
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.middle:
            ros_all_middles.add(m.middle)

ros_bridge = ros_all_middles & bridge_middles
ros_nonbridge = ros_all_middles - bridge_middles

# Section MIDDLE subsets (bridge / non-bridge)
section_bridge = {s: mids & bridge_middles for s, mids in section_middles.items()}
section_nonbridge = {s: mids - bridge_middles for s, mids in section_middles.items()}

# Group folios by section
section_folios = defaultdict(list)
for folio, sec in folio_sections.items():
    section_folios[sec].append(folio)

print(f"  Folios: {len(folio_middles)}")
print(f"  Sections: {sorted(section_folios.keys())}")
print(f"  Rosettes MIDDLEs: {len(ros_all_middles)} ({len(ros_bridge)} bridge, {len(ros_nonbridge)} non-bridge)")

# ============================================================
# P1: BRIDGE DENSITY VARIES BY SECTION
# ============================================================
print("\n" + "=" * 70)
print("P1: BRIDGE DENSITY VARIES BY SECTION")
print("=" * 70)

p1_data = {'per_section': {}}

print(f"\n{'Section':<8} {'N':>4} {'Mean BD':>8} {'Median':>8} {'Min':>6} {'Max':>6}")
print("-" * 48)

section_densities = {}
for sec in sorted(section_folios.keys()):
    folios = section_folios[sec]
    densities = [folio_bridge_density[f] for f in folios if f in folio_bridge_density]
    if not densities:
        continue
    section_densities[sec] = densities
    mean_d = sum(densities) / len(densities)
    sorted_d = sorted(densities)
    median_d = sorted_d[len(sorted_d) // 2]
    print(f"{sec:<8} {len(densities):>4} {mean_d:>7.3f} {median_d:>7.3f} "
          f"{min(densities):>5.3f} {max(densities):>5.3f}")
    p1_data['per_section'][sec] = {
        'n_folios': len(densities),
        'mean': mean_d,
        'median': median_d,
        'min': min(densities),
        'max': max(densities),
    }

# Kruskal-Wallis test
try:
    from scipy.stats import kruskal
    groups = [d for d in section_densities.values() if len(d) >= 2]
    if len(groups) >= 2:
        stat, p_val = kruskal(*groups)
        p1_data['kruskal_wallis_H'] = stat
        p1_data['kruskal_wallis_p'] = p_val
        print(f"\nKruskal-Wallis: H={stat:.2f}, p={p_val:.4e}")
    else:
        p1_data['kruskal_wallis_p'] = None
        print("\n  Not enough groups for Kruskal-Wallis")
except ImportError:
    p1_data['kruskal_wallis_p'] = None
    print("\n  (scipy not available)")

p1_verdict = 'SIGNIFICANT' if p1_data.get('kruskal_wallis_p', 1) and p1_data.get('kruskal_wallis_p', 1) < 0.05 else 'NOT_SIGNIFICANT'
p1_data['verdict'] = p1_verdict
results['verdicts']['P1_section_variation'] = p1_verdict
results['P1_data'] = p1_data
print(f"\nP1 VERDICT: {p1_verdict}")

# ============================================================
# P2: SECTION T HAS HIGHEST BRIDGE CONCENTRATION
# ============================================================
print("\n" + "=" * 70)
print("P2: SECTION T HAS HIGHEST BRIDGE CONCENTRATION")
print("=" * 70)

p2_data = {}

# Rank sections by mean bridge density
section_means = {sec: sum(d) / len(d) for sec, d in section_densities.items() if d}
ranked = sorted(section_means.items(), key=lambda x: x[1], reverse=True)

print(f"\nSection ranking by mean bridge density:")
for rank, (sec, mean_bd) in enumerate(ranked, 1):
    marker = " <-- Section T" if sec == 'T' else ""
    print(f"  {rank}. {sec}: {mean_bd:.3f} (n={len(section_densities[sec])}){marker}")

t_rank = next((i + 1 for i, (s, _) in enumerate(ranked) if s == 'T'), None)
p2_data['section_ranking'] = [(s, m) for s, m in ranked]
p2_data['t_rank'] = t_rank
p2_data['t_mean_bridge_density'] = section_means.get('T', 0)

# Section T bridge composition
if 'T' in section_middles:
    t_mids = section_middles['T']
    t_bridge_count = len(t_mids & bridge_middles)
    t_bridge_frac = t_bridge_count / len(t_mids) if t_mids else 0
    p2_data['t_unique_middles'] = len(t_mids)
    p2_data['t_bridge_middles'] = t_bridge_count
    p2_data['t_bridge_fraction'] = t_bridge_frac
    print(f"\nSection T vocabulary: {t_bridge_count}/{len(t_mids)} unique MIDDLEs are bridges ({100*t_bridge_frac:.1f}%)")

# Mann-Whitney T vs non-T
try:
    from scipy.stats import mannwhitneyu
    t_dens = section_densities.get('T', [])
    non_t_dens = [d for sec, dlist in section_densities.items() if sec != 'T' for d in dlist]
    if len(t_dens) >= 2 and len(non_t_dens) >= 2:
        u_stat, u_p = mannwhitneyu(t_dens, non_t_dens, alternative='greater')
        p2_data['mann_whitney_U'] = u_stat
        p2_data['mann_whitney_p'] = u_p
        print(f"Mann-Whitney (T > non-T): U={u_stat:.1f}, p={u_p:.4f}")
    else:
        print(f"  Section T has only {len(t_dens)} folios - Mann-Whitney underpowered")
        p2_data['mann_whitney_p'] = None
except ImportError:
    p2_data['mann_whitney_p'] = None

p2_verdict = 'T_HIGHEST' if t_rank == 1 else f'T_RANK_{t_rank}'
p2_data['verdict'] = p2_verdict
results['verdicts']['P2_section_t_highest'] = p2_verdict
results['P2_data'] = p2_data
print(f"\nP2 VERDICT: {p2_verdict}")

# ============================================================
# P3: BRIDGE DENSITY CORRELATES WITH AXM DYNAMICS
# ============================================================
print("\n" + "=" * 70)
print("P3: BRIDGE DENSITY CORRELATES WITH AXM DYNAMICS")
print("=" * 70)

p3_data = {}

# Compute AXM self-transition rate per folio from token sequences
# AXM is the dominant macro-state. We need to compute per-folio transition matrices.
# Macro-state assignment requires the 6-state model from C1010/C1015.
# Since we don't have the per-folio raw data, we compute a proxy:
# bridge density vs folio vocabulary richness (which correlates with AXM behavior)

# Actually, let's compute per-folio macro-state sequences using the class_token_map
class_map_path = ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
macro_state_path = ROOT / 'data/macro_state_mapping.json'

# Check if macro-state mapping exists
axm_data_available = False
folio_axm_self = {}

if macro_state_path.exists():
    with open(macro_state_path, 'r', encoding='utf-8') as f:
        macro_map = json.load(f)
    axm_data_available = True
    print("  Loaded macro-state mapping")
else:
    # Try to compute from class_token_map
    if class_map_path.exists():
        with open(class_map_path, 'r', encoding='utf-8') as f:
            class_map = json.load(f)
        # Build token -> class -> role mapping
        token_to_role = class_map.get('token_to_role', {})
        # Compute per-folio role sequences for B corpus
        folio_role_sequences = defaultdict(list)
        for tok in tx.currier_b():
            if tok.folio in ra.ROSETTES_FOLIOS:
                continue
            role = token_to_role.get(tok.word, 'UNKNOWN')
            folio_role_sequences[tok.folio].append(role)

        # AXM proxy: fraction of tokens that are AUXILIARY (the dominant role)
        # This is a rough proxy for AXM occupancy, not the exact self-transition
        # But for correlation purposes it should track
        for folio, roles in folio_role_sequences.items():
            if len(roles) < 10:
                continue
            # Count self-transitions in the role sequence
            axm_count = sum(1 for r in roles if r in ('AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL'))
            total = len(roles)
            # AXM self-transition proxy: fraction of consecutive pairs where both are AXM-like
            self_trans = 0
            trans_total = 0
            for i in range(len(roles) - 1):
                r1 = roles[i] in ('AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL')
                r2 = roles[i+1] in ('AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL')
                if r1:
                    trans_total += 1
                    if r2:
                        self_trans += 1
            if trans_total > 0:
                folio_axm_self[folio] = self_trans / trans_total
        axm_data_available = len(folio_axm_self) > 10
        print(f"  Computed AXM self-transition proxy for {len(folio_axm_self)} folios")

if axm_data_available and folio_axm_self:
    # Compute Spearman correlation
    common_folios = [f for f in folio_axm_self if f in folio_bridge_density]
    bd_vals = [folio_bridge_density[f] for f in common_folios]
    axm_vals = [folio_axm_self[f] for f in common_folios]

    try:
        from scipy.stats import spearmanr
        rho, p_val = spearmanr(bd_vals, axm_vals)
        p3_data['n_folios'] = len(common_folios)
        p3_data['spearman_rho'] = rho
        p3_data['spearman_p'] = p_val
        p3_data['expected_rho'] = -0.308
        print(f"\nSpearman(bridge_density, AXM_self_proxy):")
        print(f"  rho = {rho:.4f} (expected: -0.308)")
        print(f"  p = {p_val:.4e}")
        print(f"  n = {len(common_folios)} folios")
    except ImportError:
        p3_data['spearman_rho'] = None
        print("  (scipy not available)")
else:
    p3_data['spearman_rho'] = None
    print("  AXM data not available - skipping P3")

p3_verdict = 'REPLICATED' if p3_data.get('spearman_rho') and p3_data['spearman_rho'] < -0.15 and p3_data.get('spearman_p', 1) < 0.05 else 'NOT_REPLICATED'
p3_data['verdict'] = p3_verdict
results['verdicts']['P3_axm_correlation'] = p3_verdict
results['P3_data'] = p3_data
print(f"\nP3 VERDICT: {p3_verdict}")

# ============================================================
# P4: MISSING ROSETTES BRIDGES ARE NON-RANDOM
# ============================================================
print("\n" + "=" * 70)
print("P4: MISSING ROSETTES BRIDGES ARE NON-RANDOM")
print("=" * 70)

p4_data = {}

missing_bridges = bridge_middles - ros_all_middles
present_bridges = bridge_middles & ros_all_middles
p4_data['n_missing'] = len(missing_bridges)
p4_data['n_present'] = len(present_bridges)
p4_data['missing_list'] = sorted(missing_bridges)

print(f"\nMissing bridges ({len(missing_bridges)}): {sorted(missing_bridges)}")
print(f"Present bridges ({len(present_bridges)})")

# For each missing bridge: which sections use it?
print(f"\n{'Bridge':<10} {'Sections':>40}")
print("-" * 55)
missing_section_counts = Counter()
for mid in sorted(missing_bridges):
    secs = []
    for sec, mids in section_middles.items():
        if mid in mids:
            secs.append(sec)
            missing_section_counts[sec] += 1
    print(f"{mid:<10} {', '.join(sorted(secs)):>40}")

p4_data['missing_section_distribution'] = dict(missing_section_counts)

# Compare: present bridges section distribution
present_section_counts = Counter()
for mid in present_bridges:
    for sec, mids in section_middles.items():
        if mid in mids:
            present_section_counts[sec] += 1

p4_data['present_section_distribution'] = dict(present_section_counts)

print(f"\nSection distribution of missing vs present bridges:")
all_secs = sorted(set(list(missing_section_counts.keys()) + list(present_section_counts.keys())))
print(f"{'Section':<8} {'Missing':>8} {'Present':>8} {'Miss%':>7} {'Pres%':>7}")
print("-" * 45)
for sec in all_secs:
    mc = missing_section_counts.get(sec, 0)
    pc = present_section_counts.get(sec, 0)
    mp = 100 * mc / max(len(missing_bridges), 1)
    pp = 100 * pc / max(len(present_bridges), 1)
    print(f"{sec:<8} {mc:>8} {pc:>8} {mp:>6.1f}% {pp:>6.1f}%")

# Fisher exact for non-random: do missing bridges concentrate in specific sections?
try:
    from scipy.stats import chi2_contingency
    # Build contingency table: section x (missing vs present)
    table = []
    for sec in all_secs:
        table.append([missing_section_counts.get(sec, 0), present_section_counts.get(sec, 0)])
    if len(table) >= 2:
        chi2, p_val, dof, expected = chi2_contingency(table)
        p4_data['chi2'] = chi2
        p4_data['chi2_p'] = p_val
        print(f"\nChi-squared test: chi2={chi2:.2f}, p={p_val:.4f}, dof={dof}")
except ImportError:
    p4_data['chi2_p'] = None
    print("  (scipy not available)")

p4_verdict = 'NON_RANDOM' if p4_data.get('chi2_p', 1) and p4_data.get('chi2_p', 1) < 0.05 else 'RANDOM'
p4_data['verdict'] = p4_verdict
results['verdicts']['P4_missing_bridges'] = p4_verdict
results['P4_data'] = p4_data
print(f"\nP4 VERDICT: {p4_verdict}")

# ============================================================
# P5: BRIDGE DENSITY MEDIATES ROSETTES-T CORRELATION (KEY TEST)
# ============================================================
print("\n" + "=" * 70)
print("P5: BRIDGE DENSITY MEDIATES ROSETTES-T CORRELATION")
print("=" * 70)

p5_data = {}

# Three Jaccard comparisons
print(f"\nRosettes vocabulary: {len(ros_all_middles)} total, "
      f"{len(ros_bridge)} bridge, {len(ros_nonbridge)} non-bridge")

sections_for_jaccard = sorted(section_middles.keys())

# A. ALL MIDDLEs (reproduces C1090)
print(f"\n--- A. ALL MIDDLEs Jaccard (reproduce C1090) ---")
print(f"{'Section':<8} {'J(all)':>8} {'|inter|':>8} {'|union|':>8}")
print("-" * 38)

all_jaccards = {}
for sec in sections_for_jaccard:
    j = jaccard(ros_all_middles, section_middles[sec])
    inter = len(ros_all_middles & section_middles[sec])
    union = len(ros_all_middles | section_middles[sec])
    all_jaccards[sec] = j
    print(f"{sec:<8} {j:>7.4f} {inter:>8} {union:>8}")

all_ranked = sorted(all_jaccards.items(), key=lambda x: x[1], reverse=True)
all_winner = all_ranked[0][0]
print(f"Winner (ALL): {all_winner} ({all_ranked[0][1]:.4f})")

# B. BRIDGE-only Jaccard
print(f"\n--- B. BRIDGE-only Jaccard ---")
print(f"{'Section':<8} {'J(bridge)':>10} {'|inter|':>8} {'|union|':>8}")
print("-" * 40)

bridge_jaccards = {}
for sec in sections_for_jaccard:
    j = jaccard(ros_bridge, section_bridge[sec])
    inter = len(ros_bridge & section_bridge[sec])
    union = len(ros_bridge | section_bridge[sec])
    bridge_jaccards[sec] = j
    print(f"{sec:<8} {j:>9.4f} {inter:>8} {union:>8}")

bridge_ranked = sorted(bridge_jaccards.items(), key=lambda x: x[1], reverse=True)
bridge_winner = bridge_ranked[0][0]
print(f"Winner (BRIDGE): {bridge_winner} ({bridge_ranked[0][1]:.4f})")

# C. NON-BRIDGE Jaccard (THE KEY TEST)
print(f"\n--- C. NON-BRIDGE Jaccard (KEY TEST) ---")
print(f"{'Section':<8} {'J(non-br)':>10} {'|inter|':>8} {'|union|':>8}")
print("-" * 40)

nonbridge_jaccards = {}
for sec in sections_for_jaccard:
    j = jaccard(ros_nonbridge, section_nonbridge[sec])
    inter = len(ros_nonbridge & section_nonbridge[sec])
    union = len(ros_nonbridge | section_nonbridge[sec])
    nonbridge_jaccards[sec] = j
    print(f"{sec:<8} {j:>9.4f} {inter:>8} {union:>8}")

nonbridge_ranked = sorted(nonbridge_jaccards.items(), key=lambda x: x[1], reverse=True)
nonbridge_winner = nonbridge_ranked[0][0]
print(f"Winner (NON-BRIDGE): {nonbridge_winner} ({nonbridge_ranked[0][1]:.4f})")

p5_data['all_jaccards'] = dict(all_jaccards)
p5_data['bridge_jaccards'] = dict(bridge_jaccards)
p5_data['nonbridge_jaccards'] = dict(nonbridge_jaccards)
p5_data['all_winner'] = all_winner
p5_data['bridge_winner'] = bridge_winner
p5_data['nonbridge_winner'] = nonbridge_winner
p5_data['all_ranking'] = [(s, j) for s, j in all_ranked]
p5_data['nonbridge_ranking'] = [(s, j) for s, j in nonbridge_ranked]

# Mediation check
t_wins_all = (all_winner == 'T')
t_loses_nonbridge = (nonbridge_winner != 'T')
full_mediation = t_wins_all and t_loses_nonbridge

# How much does T drop?
t_all_rank = next(i + 1 for i, (s, _) in enumerate(all_ranked) if s == 'T')
t_nonbridge_rank = next(i + 1 for i, (s, _) in enumerate(nonbridge_ranked) if s == 'T')
p5_data['t_all_rank'] = t_all_rank
p5_data['t_nonbridge_rank'] = t_nonbridge_rank

print(f"\n--- Mediation Summary ---")
print(f"T rank in ALL: {t_all_rank}")
print(f"T rank in NON-BRIDGE: {t_nonbridge_rank}")
print(f"T wins ALL: {t_wins_all}")
print(f"T loses NON-BRIDGE: {t_loses_nonbridge}")
print(f"Full mediation: {full_mediation}")
print(f"Non-bridge winner: {nonbridge_winner} (replaces T in content-level similarity)")

if full_mediation:
    p5_verdict = 'FULL_MEDIATION'
elif t_nonbridge_rank > t_all_rank:
    p5_verdict = 'PARTIAL_MEDIATION'
else:
    p5_verdict = 'NO_MEDIATION'

p5_data['verdict'] = p5_verdict
results['verdicts']['P5_mediation'] = p5_verdict
results['P5_data'] = p5_data
print(f"\nP5 VERDICT: {p5_verdict}")

# ============================================================
# P6: BRIDGE DENSITY IS REGIME-INDEPENDENT
# ============================================================
print("\n" + "=" * 70)
print("P6: BRIDGE DENSITY IS REGIME-INDEPENDENT")
print("=" * 70)

p6_data = {}

# Group folios by REGIME
regime_densities = defaultdict(list)
for folio, bd in folio_bridge_density.items():
    regime = folio_regime.get(folio, 'UNKNOWN')
    if regime != 'UNKNOWN':
        regime_densities[regime].append(bd)

print(f"\n{'REGIME':<12} {'N':>4} {'Mean BD':>8} {'StDev':>8}")
print("-" * 38)
for regime in sorted(regime_densities.keys()):
    densities = regime_densities[regime]
    mean_d = sum(densities) / len(densities)
    std_d = (sum((d - mean_d)**2 for d in densities) / len(densities))**0.5 if len(densities) > 1 else 0
    print(f"{regime:<12} {len(densities):>4} {mean_d:>7.3f} {std_d:>7.3f}")
    p6_data[regime] = {'n': len(densities), 'mean': mean_d, 'std': std_d}

# One-way ANOVA
try:
    from scipy.stats import f_oneway
    groups = [d for d in regime_densities.values() if len(d) >= 2]
    if len(groups) >= 2:
        f_stat, p_val = f_oneway(*groups)
        p6_data['anova_F'] = f_stat
        p6_data['anova_p'] = p_val
        print(f"\nOne-way ANOVA: F={f_stat:.3f}, p={p_val:.4f}")
except ImportError:
    p6_data['anova_p'] = None
    print("  (scipy not available)")

p6_verdict = 'REGIME_INDEPENDENT' if p6_data.get('anova_p', 0) and p6_data.get('anova_p', 0) > 0.05 else 'REGIME_DEPENDENT'
p6_data['verdict'] = p6_verdict
results['verdicts']['P6_regime_independence'] = p6_verdict
results['P6_data'] = p6_data
print(f"\nP6 VERDICT: {p6_verdict}")

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

p2_pass = results['verdicts']['P2_section_t_highest'] == 'T_HIGHEST'
p5_pass = results['verdicts']['P5_mediation'] == 'FULL_MEDIATION'

if p2_pass and p5_pass:
    overall = 'BRIDGE_MEDIATED'
    explanation = ("The Rosettes-T correlation (C1090) is fully mediated by bridge density. "
                   "Both Rosettes and Section T are bridge-heavy because neither specializes. "
                   f"Non-bridge vocabulary points to Section {p5_data['nonbridge_winner']} instead.")
elif p2_pass and not p5_pass:
    overall = 'PARTIAL_MEDIATION'
    explanation = ("Section T has highest bridge density, but removing bridges doesn't fully "
                   "eliminate the T-correlation. Additional shared vocabulary contributes.")
elif not p2_pass and p5_pass:
    overall = 'MEDIATION_WITHOUT_T_PRIMACY'
    explanation = ("Bridge vocabulary mediates the T-correlation, but T doesn't have the "
                   "highest bridge density. The mechanism is more complex than simple bridge concentration.")
else:
    overall = 'BRIDGE_DENSITY_UNIFORM'
    explanation = "Bridge density doesn't explain the Rosettes-T correlation. Different mechanism needed."

results['overall'] = overall
results['explanation'] = explanation

# Summary table
print(f"\n{'Test':<5} {'Verdict':<25} {'Key Number'}")
print("-" * 60)
for key, verdict in results['verdicts'].items():
    print(f"{key:<5} {verdict:<25}")

print(f"\nOVERALL: {overall}")
print(f"Explanation: {explanation}")

if overall == 'BRIDGE_MEDIATED':
    print(f"\nNote (C384): Index function operates through vocabulary-mediated")
    print(f"correlation (C384.a), not direct A-to-B addressing.")

# ============================================================
# SAVE
# ============================================================
output_path = ROOT / 'phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/results/bridge_backbone_survey.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2)

print(f"\nResults saved to: {output_path}")
