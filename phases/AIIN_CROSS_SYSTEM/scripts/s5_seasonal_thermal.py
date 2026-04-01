#!/usr/bin/env python3
"""
s5_seasonal_thermal.py — Seasonal aiin enrichment & thermal cluster daiin analysis.

Phase: AIIN_CROSS_SYSTEM
Purpose:
  Part A: Test whether C1908 zodiac i/d swap manifests specifically through
          aiin-family enrichment in AZC seasonal folios.
  Part B: Test whether daiin density in A records correlates with thermal
          complexity (mean e_depth of non-daiin tokens).
  Part C: Section fingerprint — aiin-family internal composition across sections.

PRE-REGISTERED COMPLEXITY METRIC (stated before analysis):
  For each line, compute mean e_depth of non-daiin tokens on that line.
  Hypothesis: daiin-dense lines have LOWER mean e_depth in non-daiin tokens
  (i.e., daiin is infrastructure that co-occurs with simpler content).

Uses: scripts/voynich.py canonical library
"""

import sys
import io
import os
import json
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats
import numpy as np

# Windows stdout encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RESULTS_DIR = REPO_ROOT / 'phases' / 'AIIN_CROSS_SYSTEM' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

# Seasonal assignments (C1681/C1684 corrected map)
SEASONS = {
    'Spring': ['f70v1', 'f70v2', 'f71r'],
    'Summer': ['f72r2', 'f72r3', 'f72v1'],
    'Autumn': ['f72v2', 'f72v3', 'f73r'],
    'Winter': ['f71v', 'f72r1', 'f73v'],
}
FOLIO_TO_SEASON = {}
for season, folios in SEASONS.items():
    for f in folios:
        FOLIO_TO_SEASON[f] = season

# A-side thermal clusters
CLUSTERS = {
    'Cluster 1 (Thermal/Pharma)': [
        'f87r', 'f87v', 'f88v', 'f89r1', 'f89r2', 'f89v1', 'f89v2',
        'f90r2', 'f90v1', 'f90v2', 'f93v', 'f96v', 'f99r', 'f99v',
        'f101r1', 'f101v2', 'f102r1', 'f102r2', 'f102v1', 'f102v2',
        'f27r', 'f51r', 'f51v', 'f52v', 'f53v', 'f58r', 'f58v',
    ],
    'Cluster 2 (Arrangement)': [
        'f100r', 'f100v', 'f17r', 'f1v', 'f24r', 'f24v', 'f3r', 'f3v',
        'f45v', 'f52r', 'f53r', 'f54r', 'f6v', 'f88r', 'f90r1', 'f93r', 'f96r',
    ],
    'Cluster 3 (Stripped-down)': [
        'f1r', 'f2r', 'f2v', 'f4r', 'f5v', 'f6r', 'f8r', 'f8v', 'f9r', 'f9v',
        'f10v', 'f11r', 'f13v', 'f15r', 'f15v', 'f17v', 'f18r', 'f20v', 'f22r',
        'f22v', 'f23r', 'f23v', 'f25r', 'f25v', 'f28v', 'f29v', 'f32r', 'f32v',
        'f35r', 'f35v', 'f36r', 'f36v', 'f37r', 'f37v', 'f38r', 'f38v', 'f42r',
        'f44v', 'f45r', 'f47r', 'f54v',
    ],
    'Cluster 4 (Closure-heavy)': [
        'f10r', 'f11v', 'f13r', 'f14r', 'f14v', 'f16r', 'f16v', 'f18v', 'f19r',
        'f19v', 'f20r', 'f21r', 'f21v', 'f27v', 'f28r', 'f29r', 'f30r', 'f30v',
        'f42v', 'f44r', 'f47v', 'f49r', 'f49v', 'f4v', 'f56r', 'f56v', 'f5r',
        'f7r', 'f7v',
    ],
}
FOLIO_TO_CLUSTER = {}
for cname, folios in CLUSTERS.items():
    for f in folios:
        FOLIO_TO_CLUSTER[f] = cname


# ============================================================
# HELPERS
# ============================================================

def is_aiin_family(word):
    """Check if token contains ii+n atom subsequence."""
    try:
        a = morph.atomize(word)
        chars = [c for c, _, _ in a.atoms]
        for idx in range(len(chars) - 2):
            if chars[idx] == 'i' and chars[idx+1] == 'i' and chars[idx+2] == 'n':
                return True
    except Exception:
        pass
    return False


def is_ody_family(word):
    """Check if token contains od+y atom sequence."""
    try:
        a = morph.atomize(word)
        chars = [c for c, _, _ in a.atoms]
        for idx in range(len(chars) - 2):
            if chars[idx] == 'o' and chars[idx+1] == 'd' and chars[idx+2] == 'y':
                return True
    except Exception:
        pass
    return False


def has_i_atom(word):
    """Check if token contains at least one 'i' atom."""
    try:
        a = morph.atomize(word)
        return any(c == 'i' for c, _, _ in a.atoms)
    except Exception:
        return False


def get_e_depth(word):
    """Get e_depth from atomization."""
    try:
        a = morph.atomize(word)
        return a.e_depth
    except Exception:
        return 0


def map_section(section_raw):
    """Map section column to broad category."""
    if not section_raw:
        return 'Unknown'
    s = section_raw.upper()
    if s.startswith('HA') or s.startswith('HB') or s == 'H' or s.startswith('H'):
        return 'Herbal'
    if s.startswith('P'):
        return 'Pharma'
    if s.startswith('T'):
        return 'Text'
    if s.startswith('S'):
        return 'Stars'
    if s.startswith('C'):
        return 'Cosmo'
    if s.startswith('Z'):
        return 'Zodiac'
    if s.startswith('B'):
        return 'Bio'
    return 'Other'


def is_daiin(word):
    """Check if token is literally 'daiin'."""
    return word == 'daiin'


# ============================================================
# COLLECT DATA
# ============================================================

print("=" * 70)
print("s5_seasonal_thermal.py — Seasonal aiin enrichment & thermal analysis")
print("=" * 70)
print()

# Collect AZC tokens (for Part A)
azc_tokens = []
for tok in tx.azc():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    if tok.placement and tok.placement.startswith('L'):
        continue
    azc_tokens.append(tok)

# Collect Currier A tokens (for Parts B, C)
a_tokens = []
for tok in tx.currier_a():
    a_tokens.append(tok)

# Collect Currier B tokens (for Part C)
b_tokens = []
for tok in tx.currier_b():
    b_tokens.append(tok)

print(f"AZC tokens (zodiac folios): {len(azc_tokens)}")
print(f"Currier A tokens: {len(a_tokens)}")
print(f"Currier B tokens: {len(b_tokens)}")
print()

results = {}

# ============================================================
# PART A — AZC Seasonal Analysis
# ============================================================
print("=" * 70)
print("PART A: AZC Seasonal aiin-family enrichment")
print("=" * 70)
print()

# A.1: Per-folio aiin-family rate
zodiac_folios = set(FOLIO_TO_SEASON.keys())
azc_zodiac = [t for t in azc_tokens if t.folio in zodiac_folios]

print(f"AZC tokens in zodiac folios: {len(azc_zodiac)}")
print()

# Pre-compute per folio
folio_counts = defaultdict(lambda: {'total': 0, 'aiin': 0, 'ody': 0, 'i_bearing': 0})
for tok in azc_zodiac:
    fc = folio_counts[tok.folio]
    fc['total'] += 1
    if is_aiin_family(tok.word):
        fc['aiin'] += 1
    if is_ody_family(tok.word):
        fc['ody'] += 1
    if has_i_atom(tok.word):
        fc['i_bearing'] += 1

print("A.1: Per-folio aiin-family counts")
print(f"{'Folio':<10} {'Season':<10} {'Total':>6} {'aiin-fam':>9} {'Rate':>7} {'ody-fam':>8} {'Rate':>7}")
print("-" * 65)
folio_results = {}
for folio in sorted(zodiac_folios):
    fc = folio_counts[folio]
    rate = fc['aiin'] / fc['total'] if fc['total'] > 0 else 0
    ody_rate = fc['ody'] / fc['total'] if fc['total'] > 0 else 0
    season = FOLIO_TO_SEASON[folio]
    print(f"{folio:<10} {season:<10} {fc['total']:>6} {fc['aiin']:>9} {rate:>7.3f} {fc['ody']:>8} {ody_rate:>7.3f}")
    folio_results[folio] = {
        'season': season, 'total': fc['total'],
        'aiin_family': fc['aiin'], 'aiin_rate': round(rate, 4),
        'ody_family': fc['ody'], 'ody_rate': round(ody_rate, 4),
        'i_bearing': fc['i_bearing'],
    }

# A.2: Aggregate by season
print()
print("A.2: Season-level aggregation")
season_data = {}
for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
    s_folios = SEASONS[season]
    total = sum(folio_counts[f]['total'] for f in s_folios)
    aiin = sum(folio_counts[f]['aiin'] for f in s_folios)
    ody = sum(folio_counts[f]['ody'] for f in s_folios)
    i_bearing = sum(folio_counts[f]['i_bearing'] for f in s_folios)
    rate = aiin / total if total > 0 else 0
    ody_rate = ody / total if total > 0 else 0
    season_data[season] = {
        'total': total, 'aiin': aiin, 'aiin_rate': round(rate, 4),
        'ody': ody, 'ody_rate': round(ody_rate, 4),
        'i_bearing': i_bearing,
    }
    print(f"  {season:<10} total={total:>4}  aiin-fam={aiin:>3} ({rate:.3f})  "
          f"ody-fam={ody:>3} ({ody_rate:.3f})  i-bearing={i_bearing:>3}")

# Chi-squared test: Summer+Winter vs Spring+Autumn aiin rates
hot_cold = season_data['Summer']['aiin'] + season_data['Winter']['aiin']
hot_cold_total = season_data['Summer']['total'] + season_data['Winter']['total']
mild = season_data['Spring']['aiin'] + season_data['Autumn']['aiin']
mild_total = season_data['Spring']['total'] + season_data['Autumn']['total']

# 2x2 contingency table: [[aiin, non-aiin], [aiin, non-aiin]]
table = np.array([
    [hot_cold, hot_cold_total - hot_cold],
    [mild, mild_total - mild],
])
print()
print(f"  Chi-squared test (Summer+Winter vs Spring+Autumn aiin rates):")
print(f"    Hot/Cold: {hot_cold}/{hot_cold_total} = {hot_cold/hot_cold_total:.4f}")
print(f"    Mild:     {mild}/{mild_total} = {mild/mild_total:.4f}")

if table.min() >= 0 and hot_cold_total > 0 and mild_total > 0:
    # Use Fisher exact for small counts
    if table.min() < 5:
        odds_ratio, fisher_p = stats.fisher_exact(table)
        print(f"    Fisher exact: OR={odds_ratio:.3f}, p={fisher_p:.4f}")
        seasonal_test = {'test': 'fisher_exact', 'odds_ratio': round(odds_ratio, 4),
                         'p_value': round(fisher_p, 6)}
    else:
        chi2, chi_p, dof, expected = stats.chi2_contingency(table)
        print(f"    Chi-squared: chi2={chi2:.3f}, p={chi_p:.4f}, dof={dof}")
        seasonal_test = {'test': 'chi_squared', 'chi2': round(chi2, 4),
                         'p_value': round(chi_p, 6), 'dof': dof}
else:
    print("    Insufficient data for test")
    seasonal_test = {'test': 'insufficient_data'}

# A.3: What fraction of i-tokens are aiin-family?
print()
print("A.3: Fraction of seasonal i-tokens that are aiin-family")
for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
    sd = season_data[season]
    frac = sd['aiin'] / sd['i_bearing'] if sd['i_bearing'] > 0 else 0
    print(f"  {season:<10} i-bearing={sd['i_bearing']:>3}  of which aiin-fam={sd['aiin']:>3}  "
          f"fraction={frac:.3f}")
    season_data[season]['aiin_fraction_of_i'] = round(frac, 4)

# A.4: ody-family rate comparison (already computed above)
print()
print("A.4: ody-family rate by season (comparison metric)")
for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
    sd = season_data[season]
    print(f"  {season:<10} ody-fam={sd['ody']:>3}/{sd['total']:>4} = {sd['ody_rate']:.4f}")

results['part_a'] = {
    'folio_results': folio_results,
    'season_data': season_data,
    'seasonal_test': seasonal_test,
}


# ============================================================
# PART B — A-side Thermal Clusters
# ============================================================
print()
print("=" * 70)
print("PART B: A-side thermal cluster analysis")
print("=" * 70)
print()

# B.5: daiin rate and aiin rate per cluster
print("B.5: daiin and aiin rates per cluster")
cluster_data = {}
for cname in CLUSTERS:
    c_folios = set(CLUSTERS[cname.split(' ')[0]] if False else CLUSTERS[cname])
    c_toks = [t for t in a_tokens if t.folio in c_folios]
    total = len(c_toks)
    daiin_count = sum(1 for t in c_toks if is_daiin(t.word))
    aiin_count = sum(1 for t in c_toks if is_aiin_family(t.word))
    daiin_rate = daiin_count / total if total > 0 else 0
    aiin_rate = aiin_count / total if total > 0 else 0
    cluster_data[cname] = {
        'total': total, 'daiin_count': daiin_count, 'aiin_count': aiin_count,
        'daiin_rate': round(daiin_rate, 4), 'aiin_rate': round(aiin_rate, 4),
    }
    print(f"  {cname}")
    print(f"    Tokens: {total}  daiin: {daiin_count} ({daiin_rate:.4f})  "
          f"aiin-fam: {aiin_count} ({aiin_rate:.4f})")

# B.6: Daiin density vs complexity (pre-registered)
print()
print("B.6: Daiin density vs e_depth correlation (PRE-REGISTERED)")
print("  Metric: mean e_depth of non-daiin tokens on same line")
print("  Hypothesis: daiin-dense lines have LOWER non-daiin e_depth")
print()

# Group A tokens by (folio, line)
a_by_line = defaultdict(list)
for tok in a_tokens:
    a_by_line[(tok.folio, tok.line)].append(tok)

# Build per-line metrics
line_metrics = []
for (folio, line), toks in a_by_line.items():
    n_daiin = sum(1 for t in toks if is_daiin(t.word))
    non_daiin = [t for t in toks if not is_daiin(t.word)]
    if len(non_daiin) == 0:
        continue
    e_depths = [get_e_depth(t.word) for t in non_daiin]
    mean_e = np.mean(e_depths)
    section = map_section(toks[0].section)
    line_metrics.append({
        'folio': folio, 'line': line, 'section': section,
        'n_tokens': len(toks), 'n_daiin': n_daiin,
        'mean_e_depth_non_daiin': mean_e,
    })

# Overall Spearman
daiins = np.array([m['n_daiin'] for m in line_metrics])
e_depths_arr = np.array([m['mean_e_depth_non_daiin'] for m in line_metrics])

if len(daiins) > 10:
    rho, pval = stats.spearmanr(daiins, e_depths_arr)
    print(f"  Overall: n_lines={len(daiins)}, Spearman rho={rho:.4f}, p={pval:.4f}")
    overall_corr = {'n_lines': len(daiins), 'rho': round(rho, 4), 'p_value': round(pval, 6)}
else:
    print("  Insufficient lines for overall correlation")
    overall_corr = {'n_lines': len(daiins), 'note': 'insufficient'}

# Per section
section_corrs = {}
for sec in sorted(set(m['section'] for m in line_metrics)):
    sec_lines = [m for m in line_metrics if m['section'] == sec]
    if len(sec_lines) < 10:
        print(f"  Section {sec}: n={len(sec_lines)} — too few lines")
        section_corrs[sec] = {'n_lines': len(sec_lines), 'note': 'insufficient'}
        continue
    d = np.array([m['n_daiin'] for m in sec_lines])
    e = np.array([m['mean_e_depth_non_daiin'] for m in sec_lines])
    # Check variance
    if np.std(d) == 0 or np.std(e) == 0:
        print(f"  Section {sec}: n={len(sec_lines)} — no variance in one metric")
        section_corrs[sec] = {'n_lines': len(sec_lines), 'note': 'no_variance'}
        continue
    rho_s, pval_s = stats.spearmanr(d, e)
    print(f"  Section {sec}: n={len(sec_lines)}, Spearman rho={rho_s:.4f}, p={pval_s:.4f}")
    section_corrs[sec] = {'n_lines': len(sec_lines), 'rho': round(rho_s, 4),
                          'p_value': round(pval_s, 6)}

# B.7: Folio-level daiin_rate vs mean e_depth
print()
print("B.7: Folio-level daiin_rate vs mean e_depth")

a_by_folio = defaultdict(list)
for tok in a_tokens:
    a_by_folio[tok.folio].append(tok)

folio_metrics = []
for folio, toks in sorted(a_by_folio.items()):
    total = len(toks)
    daiin_ct = sum(1 for t in toks if is_daiin(t.word))
    aiin_ct = sum(1 for t in toks if is_aiin_family(t.word))
    e_depths_folio = [get_e_depth(t.word) for t in toks]
    mean_e = np.mean(e_depths_folio) if e_depths_folio else 0
    folio_metrics.append({
        'folio': folio, 'total': total,
        'daiin_rate': daiin_ct / total if total > 0 else 0,
        'aiin_rate': aiin_ct / total if total > 0 else 0,
        'mean_e_depth': round(float(mean_e), 4),
    })

if len(folio_metrics) > 10:
    dr = np.array([m['daiin_rate'] for m in folio_metrics])
    me = np.array([m['mean_e_depth'] for m in folio_metrics])
    rho_f, pval_f = stats.spearmanr(dr, me)
    print(f"  Folio-level: n={len(folio_metrics)}, Spearman rho={rho_f:.4f}, p={pval_f:.4f}")
    folio_corr = {'n_folios': len(folio_metrics), 'rho': round(rho_f, 4),
                  'p_value': round(pval_f, 6)}
else:
    print("  Insufficient folios")
    folio_corr = {'note': 'insufficient'}

# Print top/bottom folios
folio_metrics_sorted = sorted(folio_metrics, key=lambda x: x['daiin_rate'], reverse=True)
print()
print("  Top 10 folios by daiin rate:")
print(f"  {'Folio':<10} {'daiin_rate':>10} {'aiin_rate':>10} {'mean_e':>8} {'tokens':>7}")
for fm in folio_metrics_sorted[:10]:
    print(f"  {fm['folio']:<10} {fm['daiin_rate']:>10.4f} {fm['aiin_rate']:>10.4f} "
          f"{fm['mean_e_depth']:>8.4f} {fm['total']:>7}")

results['part_b'] = {
    'cluster_data': cluster_data,
    'daiin_edepth_correlation': {
        'pre_registered_metric': 'mean e_depth of non-daiin tokens on same line',
        'hypothesis': 'daiin-dense lines have lower non-daiin e_depth',
        'overall': overall_corr,
        'by_section': section_corrs,
    },
    'folio_level_correlation': folio_corr,
    'folio_metrics': {fm['folio']: fm for fm in folio_metrics},
}


# ============================================================
# PART C — Section Fingerprint
# ============================================================
print()
print("=" * 70)
print("PART C: Section fingerprint — aiin-family internal composition")
print("=" * 70)
print()

def analyze_aiin_composition(tokens, system_name):
    """Analyze aiin-family internal composition by section."""
    # Group by section
    by_section = defaultdict(list)
    for tok in tokens:
        sec = map_section(tok.section)
        by_section[sec].append(tok)

    section_profiles = {}
    print(f"  {system_name} aiin-family composition:")
    print(f"  {'Section':<12} {'Total':>6} {'aiin-fam':>9} {'Rate':>7} "
          f"{'Headed':>7} {'Headless':>9} {'H/HL ratio':>11} {'Top prefixes'}")
    print("  " + "-" * 90)

    for sec in sorted(by_section.keys()):
        toks = by_section[sec]
        total = len(toks)
        aiin_members = []
        for t in toks:
            if is_aiin_family(t.word):
                aiin_members.append(t)

        n_aiin = len(aiin_members)
        rate = n_aiin / total if total > 0 else 0

        # Headed vs headless
        headed = 0
        headless = 0
        prefix_counter = Counter()
        for t in aiin_members:
            a = morph.atomize(t.word)
            if a.is_headless:
                headless += 1
            else:
                headed += 1
            if a.prefix:
                prefix_counter[a.prefix] += 1
            else:
                prefix_counter['(none)'] += 1

        ratio_str = f"{headed}/{headless}" if headless > 0 else f"{headed}/0"
        top_pfx = ', '.join(f"{p}:{c}" for p, c in prefix_counter.most_common(3))

        print(f"  {sec:<12} {total:>6} {n_aiin:>9} {rate:>7.4f} "
              f"{headed:>7} {headless:>9} {ratio_str:>11} {top_pfx}")

        section_profiles[sec] = {
            'total_tokens': total, 'aiin_family': n_aiin,
            'aiin_rate': round(rate, 4),
            'headed': headed, 'headless': headless,
            'prefix_distribution': dict(prefix_counter),
        }

    # Chi-squared on headed/headless ratio across sections (need >=2 sections with data)
    sections_with_data = {s: p for s, p in section_profiles.items()
                          if p['aiin_family'] >= 5}
    chi_result = None
    if len(sections_with_data) >= 2:
        # Build contingency table: rows=sections, cols=[headed, headless]
        table_data = []
        sec_names = sorted(sections_with_data.keys())
        for s in sec_names:
            p = sections_with_data[s]
            table_data.append([p['headed'], p['headless']])
        table_arr = np.array(table_data)

        # Only run if we have enough counts
        if table_arr.sum() >= 10 and table_arr.shape[0] >= 2:
            # Check if any column is all zeros
            if table_arr[:, 0].sum() > 0 and table_arr[:, 1].sum() > 0:
                chi2, chi_p, dof, expected = stats.chi2_contingency(table_arr)
                print(f"\n  Chi-squared (headed/headless across sections): "
                      f"chi2={chi2:.3f}, p={chi_p:.4f}, dof={dof}")
                chi_result = {'test': 'chi_squared', 'chi2': round(chi2, 4),
                              'p_value': round(chi_p, 6), 'dof': dof,
                              'sections': sec_names}
            else:
                print(f"\n  Chi-squared: skipped (zero column)")
                chi_result = {'test': 'skipped', 'reason': 'zero_column'}
        else:
            print(f"\n  Chi-squared: skipped (insufficient counts)")
            chi_result = {'test': 'skipped', 'reason': 'insufficient_counts'}
    else:
        print(f"\n  Chi-squared: skipped (<2 sections with >=5 aiin-family tokens)")
        chi_result = {'test': 'skipped', 'reason': 'insufficient_sections'}

    return section_profiles, chi_result


# C.8: Currier A sections
print("C.8: Currier A aiin-family composition by section")
a_profiles, a_chi = analyze_aiin_composition(a_tokens, "Currier A")

# C.9: Currier B sections
print()
print("C.9: Currier B aiin-family composition by section")
b_profiles, b_chi = analyze_aiin_composition(b_tokens, "Currier B")

results['part_c'] = {
    'currier_a': {
        'section_profiles': a_profiles,
        'chi_squared_test': a_chi,
    },
    'currier_b': {
        'section_profiles': b_profiles,
        'chi_squared_test': b_chi,
    },
}


# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

# Part A summary
print("Part A — AZC Seasonal:")
for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
    sd = season_data[season]
    print(f"  {season:<10} aiin rate={sd['aiin_rate']:.4f}  ody rate={sd['ody_rate']:.4f}")
print(f"  Seasonal test: {seasonal_test}")
print()

# Part B summary
print("Part B — Thermal Clusters:")
for cname in CLUSTERS:
    cd = cluster_data[cname]
    print(f"  {cname}: daiin={cd['daiin_rate']:.4f}  aiin={cd['aiin_rate']:.4f}")
print(f"  Daiin-edepth correlation (overall): {overall_corr}")
print(f"  Folio-level correlation: {folio_corr}")
print()

# Part C summary
print("Part C — Section Fingerprint:")
print("  Currier A chi-squared:", a_chi)
print("  Currier B chi-squared:", b_chi)

# ============================================================
# SAVE
# ============================================================
output_path = RESULTS_DIR / 's5_seasonal_thermal.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print()
print(f"Results saved to {output_path}")
print("Done.")
