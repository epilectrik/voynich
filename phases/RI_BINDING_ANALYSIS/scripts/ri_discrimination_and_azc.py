"""
RI_BINDING_ANALYSIS - Phase 2: Discrimination & AZC Tests

T7: RI Contribution to Folio Orthogonality
    Remove all RI from A records. Does folio orthogonality (C437, Jaccard=0.056)
    degrade? Tests whether RI has a structural role in making folios
    distinguishable even though it doesn't bind to PP.

T8: RI-AZC Zone Interaction
    8.9% of RI MIDDLEs appear in AZC (C498.a). Do they cluster in specific
    AZC zones (C/P/R/S)? Are AZC-present RI structurally different from
    AZC-absent RI?

T9: RI Density as Folio Complexity Metric
    Does RI count/density per folio correlate with B-side properties
    (REGIME, section, folio size)?
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy import stats as scipy_stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("RI_BINDING_ANALYSIS - Phase 2: Discrimination & AZC Tests")
print("=" * 70)

# -- Load data --
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()
print(f"A folios: {len(folios)}")

# -- Load middle_classes.json --
mid_classes_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
with open(mid_classes_path, 'r') as f:
    mid_classes = json.load(f)

ri_middles_set = set(mid_classes['a_exclusive_middles'])
print(f"RI MIDDLE types: {len(ri_middles_set)}")

# -- Pre-compute all A records --
folio_records = {}
for fol in folios:
    folio_records[fol] = analyzer.analyze_folio(fol)

# -- Pre-compute per-folio: full MIDDLE set, PP-only MIDDLE set, RI-only MIDDLE set --
folio_all_middles = {}     # all MIDDLEs (PP + RI)
folio_pp_middles = {}      # PP only
folio_ri_middles = {}      # RI only

for fol in folios:
    all_mids = set()
    pp_mids = set()
    ri_mids = set()
    for rec in folio_records[fol]:
        for t in rec.tokens:
            if t.middle:
                all_mids.add(t.middle)
                if t.is_ri:
                    ri_mids.add(t.middle)
                if t.is_pp:
                    pp_mids.add(t.middle)
    folio_all_middles[fol] = all_mids
    folio_pp_middles[fol] = pp_mids
    folio_ri_middles[fol] = ri_mids

results = {
    'metadata': {
        'phase': 'RI_BINDING_ANALYSIS',
        'script': 'ri_discrimination_and_azc.py',
        'tests': 'T7-T9',
        'n_folios': len(folios),
    },
}

# ============================================================
# T7: RI Contribution to Folio Orthogonality
# ============================================================
print()
print("-" * 60)
print("T7: RI Contribution to Folio Orthogonality")
print("-" * 60)

# Compute pairwise Jaccard for: full vocabulary, PP-only, RI-only
# Pre-compute all pairs
folio_list = sorted(folios)
n_folios = len(folio_list)

# Pre-build arrays for O(n^2) pair computation
full_jaccards = []
pp_jaccards = []
ri_jaccards = []

for i in range(n_folios):
    fi = folio_list[i]
    for j in range(i + 1, n_folios):
        fj = folio_list[j]

        # Full vocabulary
        a_all = folio_all_middles[fi]
        b_all = folio_all_middles[fj]
        union_all = a_all | b_all
        if union_all:
            full_jaccards.append(len(a_all & b_all) / len(union_all))

        # PP-only
        a_pp = folio_pp_middles[fi]
        b_pp = folio_pp_middles[fj]
        union_pp = a_pp | b_pp
        if union_pp:
            pp_jaccards.append(len(a_pp & b_pp) / len(union_pp))

        # RI-only
        a_ri = folio_ri_middles[fi]
        b_ri = folio_ri_middles[fj]
        union_ri = a_ri | b_ri
        if union_ri:
            ri_jaccards.append(len(a_ri & b_ri) / len(union_ri))

full_mean = float(np.mean(full_jaccards))
pp_mean = float(np.mean(pp_jaccards))
ri_mean = float(np.mean(ri_jaccards))

print(f"  Pairwise Jaccard (all {len(full_jaccards)} pairs):")
print(f"    Full vocabulary (PP+RI): {full_mean:.4f}")
print(f"    PP-only:                 {pp_mean:.4f}")
print(f"    RI-only:                 {ri_mean:.4f}")
print(f"    C437 reference:          0.056")

# Does removing RI increase Jaccard (less orthogonal)?
diff = pp_mean - full_mean
pct_change = (pp_mean - full_mean) / full_mean * 100 if full_mean > 0 else 0

print(f"\n  Removing RI changes Jaccard by: {diff:+.4f} ({pct_change:+.1f}%)")

# How orthogonal is RI by itself?
print(f"  RI-only Jaccard: {ri_mean:.4f} (lower = more orthogonal)")

# Statistical test: is full < PP? (removing RI makes folios less distinct)
# Paired comparison
full_arr = np.array(full_jaccards)
pp_arr = np.array(pp_jaccards)
t7_stat, t7_p = scipy_stats.wilcoxon(full_arr - pp_arr, alternative='less')

print(f"  Wilcoxon (full < PP): p={t7_p:.4e}")

# Discrimination power: unique fingerprints
full_fingerprints = set()
pp_fingerprints = set()
for fol in folio_list:
    full_fingerprints.add(frozenset(folio_all_middles[fol]))
    pp_fingerprints.add(frozenset(folio_pp_middles[fol]))

full_unique = len(full_fingerprints) / n_folios
pp_unique = len(pp_fingerprints) / n_folios

print(f"\n  Unique fingerprints:")
print(f"    Full (PP+RI): {len(full_fingerprints)}/{n_folios} ({full_unique*100:.1f}%)")
print(f"    PP-only:      {len(pp_fingerprints)}/{n_folios} ({pp_unique*100:.1f}%)")

t7_pass = diff < -0.005 and t7_p < 0.001  # RI meaningfully increases orthogonality

print(f"\n  T7 {'PASS' if t7_pass else 'FAIL'}: {'RI contributes to folio orthogonality' if t7_pass else 'RI does NOT meaningfully increase folio orthogonality'}")

results['T7_folio_orthogonality'] = {
    'full_jaccard': round(full_mean, 4),
    'pp_only_jaccard': round(pp_mean, 4),
    'ri_only_jaccard': round(ri_mean, 4),
    'c437_reference': 0.056,
    'diff_removing_ri': round(diff, 4),
    'pct_change': round(pct_change, 1),
    'wilcoxon_p': float(t7_p),
    'full_unique_fingerprints': len(full_fingerprints),
    'pp_unique_fingerprints': len(pp_fingerprints),
    'n_folios': n_folios,
    'pass': t7_pass,
}

# ============================================================
# T8: RI-AZC Zone Interaction
# ============================================================
print()
print("-" * 60)
print("T8: RI-AZC Zone Interaction")
print("-" * 60)

# Get all AZC tokens (language=NA)
azc_tokens = list(tx.azc())
print(f"  AZC tokens: {len(azc_tokens)}")

# Extract AZC MIDDLEs and their positions
azc_middles = set()
azc_mid_positions = defaultdict(list)  # middle -> list of placement codes
azc_mid_folios = defaultdict(set)      # middle -> set of folios

for token in azc_tokens:
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)
        placement = token.placement if hasattr(token, 'placement') else ''
        azc_mid_positions[m.middle].append(placement)
        azc_mid_folios[m.middle].add(token.folio)

print(f"  AZC MIDDLE types: {len(azc_middles)}")

# Which RI MIDDLEs appear in AZC?
ri_in_azc = ri_middles_set & azc_middles
ri_not_azc = ri_middles_set - azc_middles

print(f"  RI MIDDLEs in AZC: {len(ri_in_azc)} ({100*len(ri_in_azc)/len(ri_middles_set):.1f}%)")
print(f"  RI MIDDLEs NOT in AZC: {len(ri_not_azc)}")

# Zone analysis: what placement codes do RI-in-AZC tokens have?
# Placement codes: C=cosmological, P=pharmaceutical, R=ring, S=star
ri_azc_placements = Counter()
all_azc_placements = Counter()

for token in azc_tokens:
    m = morph.extract(token.word)
    if not m.middle:
        continue
    placement = token.placement if hasattr(token, 'placement') else ''
    zone = placement[0] if placement else '?'
    all_azc_placements[zone] += 1
    if m.middle in ri_in_azc:
        ri_azc_placements[zone] += 1

print(f"\n  AZC zone distribution (all vs RI-only):")
print(f"  {'Zone':>6} {'All AZC':>10} {'RI-in-AZC':>10} {'RI %':>8}")
for zone in sorted(set(all_azc_placements.keys()) | set(ri_azc_placements.keys())):
    all_ct = all_azc_placements.get(zone, 0)
    ri_ct = ri_azc_placements.get(zone, 0)
    ri_pct = 100 * ri_ct / all_ct if all_ct > 0 else 0
    print(f"  {zone:>6} {all_ct:>10} {ri_ct:>10} {ri_pct:>7.1f}%")

# Is RI zone distribution different from overall AZC zone distribution?
# Chi-squared: observed RI zone counts vs expected from overall distribution
total_all = sum(all_azc_placements.values())
total_ri = sum(ri_azc_placements.values())

if total_ri >= 10:
    zones = sorted(all_azc_placements.keys())
    observed = np.array([ri_azc_placements.get(z, 0) for z in zones], dtype=float)
    expected = np.array([all_azc_placements.get(z, 0) for z in zones], dtype=float)
    expected = expected / expected.sum() * total_ri

    # Filter out zones with expected < 1
    mask = expected >= 1
    if mask.sum() >= 2:
        chi2 = float(np.sum((observed[mask] - expected[mask])**2 / expected[mask]))
        chi2_df = int(mask.sum()) - 1
        chi2_p = float(scipy_stats.chi2.sf(chi2, chi2_df))
    else:
        chi2, chi2_df, chi2_p = 0, 0, 1.0
else:
    chi2, chi2_df, chi2_p = 0, 0, 1.0

print(f"\n  Chi-squared (RI zone vs overall): chi2={chi2:.2f}, df={chi2_df}, p={chi2_p:.4e}")

# Morphological comparison: AZC-present RI vs AZC-absent RI
ri_azc_lengths = [len(m) for m in ri_in_azc]
ri_notazc_lengths = [len(m) for m in ri_not_azc]

if ri_azc_lengths and ri_notazc_lengths:
    azc_len_mean = float(np.mean(ri_azc_lengths))
    notazc_len_mean = float(np.mean(ri_notazc_lengths))
    len_u, len_p = scipy_stats.mannwhitneyu(ri_azc_lengths, ri_notazc_lengths, alternative='two-sided')
else:
    azc_len_mean = 0
    notazc_len_mean = 0
    len_p = 1.0

print(f"\n  RI MIDDLE length:")
print(f"    AZC-present: mean={azc_len_mean:.2f} (n={len(ri_in_azc)})")
print(f"    AZC-absent:  mean={notazc_len_mean:.2f} (n={len(ri_not_azc)})")
print(f"    Mann-Whitney p={len_p:.4e}")

# Folio spread: AZC-present RI vs AZC-absent RI
# How many A folios use each RI MIDDLE?
ri_folio_spread = {}
for fol in folios:
    for mid in folio_ri_middles[fol]:
        if mid not in ri_folio_spread:
            ri_folio_spread[mid] = 0
        ri_folio_spread[mid] += 1

azc_ri_spreads = [ri_folio_spread.get(m, 0) for m in ri_in_azc]
notazc_ri_spreads = [ri_folio_spread.get(m, 0) for m in ri_not_azc]

if azc_ri_spreads and notazc_ri_spreads:
    azc_spread_mean = float(np.mean(azc_ri_spreads))
    notazc_spread_mean = float(np.mean(notazc_ri_spreads))
    spread_u, spread_p = scipy_stats.mannwhitneyu(azc_ri_spreads, notazc_ri_spreads, alternative='two-sided')
else:
    azc_spread_mean = 0
    notazc_spread_mean = 0
    spread_p = 1.0

print(f"\n  RI folio spread (A folios using each MIDDLE):")
print(f"    AZC-present: mean={azc_spread_mean:.2f}")
print(f"    AZC-absent:  mean={notazc_spread_mean:.2f}")
print(f"    Mann-Whitney p={spread_p:.4e}")

# PREFIX bifurcation: are AZC-present RI differently split?
ri_prefix_status = {}  # mid -> 'required', 'forbidden', 'optional'
for fol in folios:
    for rec in folio_records[fol]:
        for t in rec.tokens:
            if t.is_ri and t.middle:
                m_obj = morph.extract(t.word)
                mid = t.middle
                has_prefix = m_obj.prefix is not None
                if mid not in ri_prefix_status:
                    ri_prefix_status[mid] = {'with': 0, 'without': 0}
                if has_prefix:
                    ri_prefix_status[mid]['with'] += 1
                else:
                    ri_prefix_status[mid]['without'] += 1

azc_prefix_req = sum(1 for m in ri_in_azc
                     if m in ri_prefix_status
                     and ri_prefix_status[m]['with'] > 0
                     and ri_prefix_status[m]['without'] == 0)
azc_prefix_forb = sum(1 for m in ri_in_azc
                      if m in ri_prefix_status
                      and ri_prefix_status[m]['without'] > 0
                      and ri_prefix_status[m]['with'] == 0)
notazc_prefix_req = sum(1 for m in ri_not_azc
                        if m in ri_prefix_status
                        and ri_prefix_status[m]['with'] > 0
                        and ri_prefix_status[m]['without'] == 0)
notazc_prefix_forb = sum(1 for m in ri_not_azc
                         if m in ri_prefix_status
                         and ri_prefix_status[m]['without'] > 0
                         and ri_prefix_status[m]['with'] == 0)

azc_req_frac = azc_prefix_req / len(ri_in_azc) if ri_in_azc else 0
notazc_req_frac = notazc_prefix_req / len(ri_not_azc) if ri_not_azc else 0

print(f"\n  PREFIX bifurcation (C528):")
print(f"    AZC-present:  REQ={azc_prefix_req} FORB={azc_prefix_forb} (REQ rate={azc_req_frac:.3f})")
print(f"    AZC-absent:   REQ={notazc_prefix_req} FORB={notazc_prefix_forb} (REQ rate={notazc_req_frac:.3f})")

# Fisher exact test on PREFIX REQ vs FORB for AZC-present vs absent
if azc_prefix_req + azc_prefix_forb > 0 and notazc_prefix_req + notazc_prefix_forb > 0:
    fisher_table = [[azc_prefix_req, azc_prefix_forb],
                    [notazc_prefix_req, notazc_prefix_forb]]
    fisher_or, fisher_p = scipy_stats.fisher_exact(fisher_table)
    print(f"    Fisher exact: OR={fisher_or:.3f}, p={fisher_p:.4e}")
else:
    fisher_or, fisher_p = 1.0, 1.0

t8_zone_pass = chi2_p < 0.01  # RI clusters in specific zones
t8_morph_pass = len_p < 0.01 or fisher_p < 0.01  # AZC-present RI is morphologically distinct
t8_pass = t8_zone_pass or t8_morph_pass

print(f"\n  T8 zone clustering: {'PASS' if t8_zone_pass else 'FAIL'}")
print(f"  T8 morphological distinction: {'PASS' if t8_morph_pass else 'FAIL'}")
print(f"  T8 overall {'PASS' if t8_pass else 'FAIL'}: {'RI-AZC interaction detected' if t8_pass else 'No RI-AZC interaction'}")

results['T8_ri_azc_interaction'] = {
    'ri_in_azc_count': len(ri_in_azc),
    'ri_in_azc_pct': round(100 * len(ri_in_azc) / len(ri_middles_set), 1),
    'zone_chi2': round(chi2, 2),
    'zone_chi2_df': chi2_df,
    'zone_chi2_p': float(chi2_p),
    'ri_azc_placements': dict(ri_azc_placements),
    'all_azc_placements': dict(all_azc_placements),
    'length_azc_present': round(azc_len_mean, 2),
    'length_azc_absent': round(notazc_len_mean, 2),
    'length_p': float(len_p),
    'spread_azc_present': round(azc_spread_mean, 2),
    'spread_azc_absent': round(notazc_spread_mean, 2),
    'spread_p': float(spread_p),
    'prefix_azc_req_rate': round(azc_req_frac, 3),
    'prefix_notazc_req_rate': round(notazc_req_frac, 3),
    'fisher_p': float(fisher_p),
    'zone_pass': t8_zone_pass,
    'morph_pass': t8_morph_pass,
    'pass': t8_pass,
}

# ============================================================
# T9: RI Density as Folio Complexity Metric
# ============================================================
print()
print("-" * 60)
print("T9: RI Density as Folio Complexity Metric")
print("-" * 60)

# Per folio: RI type count, RI token count, RI density (types/lines)
folio_ri_type_count = {}
folio_ri_token_count = {}
folio_line_count = {}
folio_ri_density = {}

for fol in folios:
    ri_types = folio_ri_middles[fol]
    ri_tokens = sum(1 for rec in folio_records[fol] for t in rec.tokens if t.is_ri)
    n_lines = len(folio_records[fol])
    folio_ri_type_count[fol] = len(ri_types)
    folio_ri_token_count[fol] = ri_tokens
    folio_line_count[fol] = n_lines
    folio_ri_density[fol] = len(ri_types) / n_lines if n_lines > 0 else 0

# Load REGIME mapping
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
regime_map = {}
if regime_path.exists():
    with open(regime_path, 'r') as f:
        regime_data = json.load(f)
    for regime, regime_folios in regime_data.items():
        for fol in regime_folios:
            regime_map[fol] = regime

# Get folio sections
folio_section = {}
for token in tx.currier_a():
    fol = token.folio
    if fol not in folio_section:
        folio_section[fol] = token.section if hasattr(token, 'section') else None

# If section not directly available
if all(v is None for v in folio_section.values()):
    df = tx._df
    df_h = df[df['transcriber'] == 'H']
    for fol in folios:
        fol_df = df_h[df_h['folio'] == fol]
        if len(fol_df) > 0 and 'section' in fol_df.columns:
            folio_section[fol] = fol_df.iloc[0]['section']

# Correlation: RI density vs folio size
ri_densities = np.array([folio_ri_density[f] for f in folio_list])
line_counts = np.array([folio_line_count[f] for f in folio_list])
ri_type_counts = np.array([folio_ri_type_count[f] for f in folio_list])

rho_size, p_size = scipy_stats.spearmanr(ri_densities, line_counts)
print(f"  RI density vs folio size: rho={rho_size:.4f}, p={p_size:.4e}")

rho_types_size, p_types_size = scipy_stats.spearmanr(ri_type_counts, line_counts)
print(f"  RI type count vs folio size: rho={rho_types_size:.4f}, p={p_types_size:.4e}")

# RI density by section
section_ri = defaultdict(list)
for fol in folio_list:
    s = folio_section.get(fol)
    if s:
        section_ri[s].append(folio_ri_density[fol])

print(f"\n  RI density by section:")
for s in sorted(section_ri.keys()):
    vals = section_ri[s]
    print(f"    {s}: mean={np.mean(vals):.4f}, n={len(vals)}")

if len(section_ri) >= 2:
    section_groups = [section_ri[s] for s in sorted(section_ri.keys()) if len(section_ri[s]) >= 3]
    if len(section_groups) >= 2:
        kw_stat, kw_p = scipy_stats.kruskal(*section_groups)
        print(f"    Kruskal-Wallis: H={kw_stat:.3f}, p={kw_p:.4e}")
    else:
        kw_stat, kw_p = 0, 1.0
else:
    kw_stat, kw_p = 0, 1.0

# RI density by REGIME
regime_ri = defaultdict(list)
for fol in folio_list:
    r = regime_map.get(fol)
    if r:
        regime_ri[r].append(folio_ri_density[fol])

if regime_ri:
    print(f"\n  RI density by REGIME:")
    for r in sorted(regime_ri.keys()):
        vals = regime_ri[r]
        print(f"    {r}: mean={np.mean(vals):.4f}, n={len(vals)}")

    regime_groups = [regime_ri[r] for r in sorted(regime_ri.keys()) if len(regime_ri[r]) >= 3]
    if len(regime_groups) >= 2:
        rg_stat, rg_p = scipy_stats.kruskal(*regime_groups)
        print(f"    Kruskal-Wallis: H={rg_stat:.3f}, p={rg_p:.4e}")
    else:
        rg_stat, rg_p = 0, 1.0
else:
    rg_stat, rg_p = 0, 1.0
    print(f"\n  REGIME mapping not available")

# PP density comparison
folio_pp_density = {}
for fol in folios:
    pp_types = folio_pp_middles[fol]
    n_lines = folio_line_count[fol]
    folio_pp_density[fol] = len(pp_types) / n_lines if n_lines > 0 else 0

pp_densities = np.array([folio_pp_density[f] for f in folio_list])
rho_ri_pp, p_ri_pp = scipy_stats.spearmanr(ri_densities, pp_densities)
print(f"\n  RI density vs PP density: rho={rho_ri_pp:.4f}, p={p_ri_pp:.4e}")

t9_pass = (abs(rho_size) > 0.3 and p_size < 0.01) or (kw_p < 0.01) or (rg_p < 0.01)

print(f"\n  T9 {'PASS' if t9_pass else 'FAIL'}: {'RI density carries structural information' if t9_pass else 'RI density is not structurally informative'}")

results['T9_ri_density'] = {
    'rho_size': round(float(rho_size), 4),
    'p_size': float(p_size),
    'rho_types_size': round(float(rho_types_size), 4),
    'p_types_size': float(p_types_size),
    'section_kruskal_p': float(kw_p),
    'regime_kruskal_p': float(rg_p),
    'rho_ri_pp_density': round(float(rho_ri_pp), 4),
    'p_ri_pp_density': float(p_ri_pp),
    'pass': t9_pass,
}

# ============================================================
# Summary
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

pass_count = sum([t7_pass, t8_pass, t9_pass])
print(f"\n  Tests passed: {pass_count}/3")
print()
print(f"  T7 [{'PASS' if t7_pass else 'FAIL'}] RI contribution to folio orthogonality")
print(f"      Full Jaccard={full_mean:.4f}, PP-only={pp_mean:.4f}, RI-only={ri_mean:.4f}")
print(f"      Removing RI: {pct_change:+.1f}% change. Fingerprints: {len(full_fingerprints)} vs {len(pp_fingerprints)}")
print()
print(f"  T8 [{'PASS' if t8_pass else 'FAIL'}] RI-AZC zone interaction")
print(f"      RI in AZC: {len(ri_in_azc)}/{len(ri_middles_set)} ({100*len(ri_in_azc)/len(ri_middles_set):.1f}%)")
print(f"      Zone clustering p={chi2_p:.4e}, Length diff p={len_p:.4e}")
print()
print(f"  T9 [{'PASS' if t9_pass else 'FAIL'}] RI density as complexity metric")
print(f"      Size rho={rho_size:.3f}, Section KW p={kw_p:.4e}, REGIME KW p={rg_p:.4e}")

results['summary'] = {
    'pass_count': pass_count,
    'total_tests': 3,
    'T7_pass': t7_pass,
    'T8_pass': t8_pass,
    'T9_pass': t9_pass,
}

# Save
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
output_path = RESULTS_DIR / 'ri_discrimination_and_azc.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
