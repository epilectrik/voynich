"""Test 2: Section-Conditional Suffix Variation on Same MIDDLE.

Question: Does the same MIDDLE take different SUFFIX distributions in
different sections?

Method:
  1. Extract MIDDLE and SUFFIX for each Currier B token.
  2. For each common MIDDLE (count >= 100), build suffix distribution per section.
  3. Chi-square test of independence (suffix x section) per MIDDLE.
  4. Cramer's V effect size per MIDDLE.
  5. Bonferroni correction across all tested MIDDLEs.
  6. Identify section-dependent MIDDLEs (p < 0.01 post-Bonferroni).
  7. Characterize enriched suffix-section pairs for significant MIDDLEs.
  8. Compare mean V against C495 baseline (V=0.159).
  9. Confound control: suffix x regime chi-square/V per MIDDLE.
 10. Within-section suffix x regime test.

Pass: mean Cramer's V > 0.20 (exceeding C495 V=0.159), >50% significant.
Fail: mean V < 0.159 (weaker than regime effect).
"""

import json
import sys
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()

SECTIONS = ['B', 'H', 'S', 'T', 'C']
MIDDLE_MIN_COUNT = 100
BONFERRONI_ALPHA = 0.01

# Load canonical regime mapping
regime_path = Path('C:/git/voynich/phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json')
with open(regime_path, encoding='utf-8') as f:
    regime_mapping = json.load(f)

folio_regime = {}
for regime, folios in regime_mapping.items():
    for fol in folios:
        folio_regime[fol] = regime

REGIMES = sorted(set(folio_regime.values()))

# ============================================================
# STEP 1: Collect per-token data (single pass)
# ============================================================
# Pre-collect: for each MIDDLE, count by (suffix, section) and (suffix, regime)
middle_section_suffix = defaultdict(lambda: defaultdict(Counter))  # middle -> section -> suffix counter
middle_regime_suffix = defaultdict(lambda: defaultdict(Counter))   # middle -> regime -> suffix counter
middle_total = Counter()  # total token count per MIDDLE
section_regime_suffix = defaultdict(lambda: defaultdict(Counter))  # (section) -> regime -> suffix counter

for token in tx.currier_b():
    word = token.word
    section = token.section
    if section not in SECTIONS:
        continue

    m = morph.extract(word)
    mid = m.middle
    if not mid or mid == '_EMPTY_':
        continue
    sfx = m.suffix if m.suffix else 'BARE'

    middle_total[mid] += 1
    middle_section_suffix[mid][section][sfx] += 1

    regime = folio_regime.get(token.folio)
    if regime:
        middle_regime_suffix[mid][regime][sfx] += 1
        section_regime_suffix[section][regime][sfx] += 1


# ============================================================
# STEP 2: Filter to common MIDDLEs (>= 100 tokens)
# ============================================================
common_middles = sorted([mid for mid, cnt in middle_total.items() if cnt >= MIDDLE_MIN_COUNT],
                        key=lambda x: -middle_total[x])

print(f"Common MIDDLEs (>= {MIDDLE_MIN_COUNT} tokens): {len(common_middles)}")
print(f"Total MIDDLEs: {len(middle_total)}")


# ============================================================
# HELPER: Build contingency table and compute chi2 + Cramer's V
# ============================================================
def cramers_v(chi2_stat, n, min_dim):
    """Compute Cramer's V from chi2, sample size, and min(rows,cols)-1."""
    if n == 0 or min_dim == 0:
        return 0.0
    return math.sqrt(chi2_stat / (n * min_dim))


def chi2_test_from_counts(group_suffix_counts, group_labels):
    """
    Build contingency table from {group_label: Counter(suffix)} and run chi2.

    Returns (chi2, p, dof, V, n, table_info) or None if table is degenerate.
    """
    # Collect all suffixes across groups
    all_suffixes = set()
    for gc in group_suffix_counts.values():
        all_suffixes.update(gc.keys())
    all_suffixes = sorted(all_suffixes)

    # Only keep groups that actually have data
    active_groups = [g for g in group_labels if sum(group_suffix_counts.get(g, {}).values()) > 0]
    if len(active_groups) < 2 or len(all_suffixes) < 2:
        return None

    # Build matrix: rows = groups, cols = suffixes
    table = []
    for g in active_groups:
        row = [group_suffix_counts.get(g, Counter()).get(s, 0) for s in all_suffixes]
        table.append(row)

    table = np.array(table, dtype=float)

    # Remove zero-sum columns
    col_sums = table.sum(axis=0)
    keep_cols = col_sums > 0
    table = table[:, keep_cols]
    filtered_suffixes = [s for s, k in zip(all_suffixes, keep_cols) if k]

    if table.shape[0] < 2 or table.shape[1] < 2:
        return None

    n = table.sum()
    if n < 5:
        return None

    try:
        chi2_stat, p, dof, expected = chi2_contingency(table)
    except ValueError:
        return None

    min_dim = min(table.shape[0], table.shape[1]) - 1
    V = cramers_v(chi2_stat, n, min_dim)

    return {
        'chi2': float(chi2_stat),
        'p': float(p),
        'dof': int(dof),
        'V': float(V),
        'n': int(n),
        'groups': active_groups,
        'suffixes': filtered_suffixes,
        'table_shape': list(table.shape),
    }


# ============================================================
# STEP 3: Suffix x Section test per MIDDLE
# ============================================================
section_results = {}
section_vs = []

for mid in common_middles:
    result = chi2_test_from_counts(middle_section_suffix[mid], SECTIONS)
    if result is None:
        section_results[mid] = {'status': 'DEGENERATE', 'count': middle_total[mid]}
        continue

    section_results[mid] = result
    section_vs.append(result['V'])

print(f"\nSection test: {len(section_vs)} testable MIDDLEs out of {len(common_middles)}")


# ============================================================
# STEP 4: Bonferroni correction on section tests
# ============================================================
n_tests = len(section_vs)
bonferroni_threshold = BONFERRONI_ALPHA / max(1, n_tests)

significant_section = []
for mid in common_middles:
    r = section_results[mid]
    if isinstance(r, dict) and 'p' in r:
        r['bonferroni_threshold'] = bonferroni_threshold
        r['significant'] = r['p'] < bonferroni_threshold
        if r['significant']:
            significant_section.append(mid)

pct_significant = len(significant_section) / max(1, n_tests) * 100
mean_V_section = float(np.mean(section_vs)) if section_vs else 0.0
median_V_section = float(np.median(section_vs)) if section_vs else 0.0

print(f"Mean Cramer's V (suffix x section): {mean_V_section:.4f}")
print(f"Median Cramer's V: {median_V_section:.4f}")
print(f"Significant after Bonferroni: {len(significant_section)}/{n_tests} ({pct_significant:.1f}%)")


# ============================================================
# STEP 5: Characterize enriched suffix-section pairs
# ============================================================
enrichment_details = {}

for mid in significant_section:
    data = middle_section_suffix[mid]
    # Overall suffix distribution for this MIDDLE
    total_suffix = Counter()
    for sec in SECTIONS:
        total_suffix += data.get(sec, Counter())

    total_n = sum(total_suffix.values())
    if total_n == 0:
        continue

    # Expected proportion of each suffix
    expected_prop = {s: c / total_n for s, c in total_suffix.items()}

    # Per-section enrichment
    section_enrichments = {}
    for sec in SECTIONS:
        sec_counts = data.get(sec, Counter())
        sec_n = sum(sec_counts.values())
        if sec_n < 5:
            continue

        enriched = []
        depleted = []
        for sfx in total_suffix:
            obs_prop = sec_counts.get(sfx, 0) / sec_n
            exp_prop = expected_prop[sfx]
            if exp_prop > 0:
                ratio = obs_prop / exp_prop
                if ratio > 1.5 and sec_counts.get(sfx, 0) >= 3:
                    enriched.append({'suffix': sfx, 'ratio': round(ratio, 2),
                                     'obs_count': sec_counts.get(sfx, 0),
                                     'obs_pct': round(obs_prop * 100, 1),
                                     'exp_pct': round(exp_prop * 100, 1)})
                elif ratio < 0.5 and total_suffix[sfx] >= 5:
                    depleted.append({'suffix': sfx, 'ratio': round(ratio, 2),
                                     'obs_count': sec_counts.get(sfx, 0),
                                     'obs_pct': round(obs_prop * 100, 1),
                                     'exp_pct': round(exp_prop * 100, 1)})

        if enriched or depleted:
            section_enrichments[sec] = {
                'section_n': sec_n,
                'enriched': sorted(enriched, key=lambda x: -x['ratio']),
                'depleted': sorted(depleted, key=lambda x: x['ratio']),
            }

    if section_enrichments:
        enrichment_details[mid] = {
            'total_n': total_n,
            'V': section_results[mid]['V'],
            'sections': section_enrichments,
        }

print(f"\nMIDDLEs with characterized enrichments: {len(enrichment_details)}")


# ============================================================
# STEP 6: Confound control -- suffix x regime per MIDDLE
# ============================================================
regime_results = {}
regime_vs = []

for mid in common_middles:
    result = chi2_test_from_counts(middle_regime_suffix[mid], REGIMES)
    if result is None:
        regime_results[mid] = {'status': 'DEGENERATE', 'count': middle_total[mid]}
        continue

    regime_results[mid] = result
    regime_vs.append(result['V'])

# Bonferroni on regime tests too
n_regime_tests = len(regime_vs)
bonferroni_regime = BONFERRONI_ALPHA / max(1, n_regime_tests)
significant_regime = []
for mid in common_middles:
    r = regime_results[mid]
    if isinstance(r, dict) and 'p' in r:
        r['bonferroni_threshold'] = bonferroni_regime
        r['significant'] = r['p'] < bonferroni_regime
        if r['significant']:
            significant_regime.append(mid)

mean_V_regime = float(np.mean(regime_vs)) if regime_vs else 0.0
median_V_regime = float(np.median(regime_vs)) if regime_vs else 0.0

print(f"\nConfound control (suffix x regime):")
print(f"  Mean Cramer's V: {mean_V_regime:.4f}")
print(f"  Median V: {median_V_regime:.4f}")
print(f"  Significant: {len(significant_regime)}/{n_regime_tests} ({len(significant_regime)/max(1,n_regime_tests)*100:.1f}%)")


# ============================================================
# STEP 7: Compare section vs regime effect sizes per MIDDLE
# ============================================================
comparison = []
section_stronger_count = 0
regime_stronger_count = 0

for mid in common_middles:
    sr = section_results.get(mid, {})
    rr = regime_results.get(mid, {})
    if 'V' in sr and 'V' in rr:
        sv = sr['V']
        rv = rr['V']
        diff = sv - rv
        comparison.append({
            'middle': mid,
            'V_section': round(sv, 4),
            'V_regime': round(rv, 4),
            'V_diff': round(diff, 4),
            'section_stronger': diff > 0,
        })
        if diff > 0:
            section_stronger_count += 1
        else:
            regime_stronger_count += 1

pct_section_stronger = section_stronger_count / max(1, len(comparison)) * 100

print(f"\nSection vs Regime comparison:")
print(f"  Section stronger: {section_stronger_count}/{len(comparison)} ({pct_section_stronger:.1f}%)")
print(f"  Regime stronger: {regime_stronger_count}/{len(comparison)}")


# ============================================================
# STEP 8: Within-section suffix x regime test
# ============================================================
within_section_results = {}

for sec in SECTIONS:
    data = section_regime_suffix.get(sec, {})
    result = chi2_test_from_counts(data, REGIMES)
    if result is not None:
        within_section_results[sec] = result
        print(f"  Within {sec}: chi2={result['chi2']:.1f}, V={result['V']:.4f}, p={result['p']:.2e}, n={result['n']}")
    else:
        within_section_results[sec] = {'status': 'DEGENERATE'}
        print(f"  Within {sec}: DEGENERATE (insufficient data)")


# ============================================================
# VERDICT
# ============================================================
c495_baseline = 0.159

if mean_V_section > 0.20 and pct_significant > 50:
    verdict = 'PASS'
    verdict_reason = (f"Mean V={mean_V_section:.3f} > 0.20, "
                      f"{pct_significant:.1f}% significant > 50%")
elif mean_V_section < c495_baseline:
    verdict = 'FAIL'
    verdict_reason = (f"Mean V={mean_V_section:.3f} < C495 baseline {c495_baseline}")
else:
    verdict = 'PARTIAL'
    verdict_reason = (f"Mean V={mean_V_section:.3f} exceeds C495 baseline {c495_baseline} "
                      f"but below 0.20 threshold or {pct_significant:.1f}% < 50% significant")

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {verdict_reason}")
print(f"{'='*60}")


# ============================================================
# TOP significant MIDDLEs
# ============================================================
top_sig = sorted(
    [(mid, section_results[mid]['V'], section_results[mid]['chi2'],
      section_results[mid]['p'], section_results[mid]['n'])
     for mid in significant_section if 'V' in section_results[mid]],
    key=lambda x: -x[1]
)

print(f"\nTop significant MIDDLEs (by V):")
for mid, v, chi2, p, n in top_sig[:15]:
    print(f"  {mid:15s}  V={v:.3f}  chi2={chi2:.1f}  p={p:.2e}  n={n}")


# ============================================================
# OUTPUT
# ============================================================
output = {
    'test': 'suffix_section_interaction',
    'description': 'Does the same MIDDLE take different suffix distributions in different sections?',
    'timestamp': datetime.now().isoformat(),
    'parameters': {
        'middle_min_count': MIDDLE_MIN_COUNT,
        'bonferroni_alpha': BONFERRONI_ALPHA,
        'sections': SECTIONS,
        'regimes': REGIMES,
    },
    'counts': {
        'total_middles': len(middle_total),
        'common_middles_tested': len(common_middles),
        'testable_section': len(section_vs),
        'testable_regime': len(regime_vs),
    },
    'section_test': {
        'mean_cramers_v': round(mean_V_section, 4),
        'median_cramers_v': round(median_V_section, 4),
        'significant_count': len(significant_section),
        'pct_significant': round(pct_significant, 1),
        'bonferroni_threshold': bonferroni_threshold,
        'c495_baseline_v': c495_baseline,
    },
    'regime_confound': {
        'mean_cramers_v': round(mean_V_regime, 4),
        'median_cramers_v': round(median_V_regime, 4),
        'significant_count': len(significant_regime),
        'pct_significant': round(len(significant_regime) / max(1, n_regime_tests) * 100, 1),
    },
    'comparison': {
        'section_stronger_count': section_stronger_count,
        'regime_stronger_count': regime_stronger_count,
        'pct_section_stronger': round(pct_section_stronger, 1),
        'mean_V_diff': round(float(np.mean([c['V_diff'] for c in comparison])), 4) if comparison else 0.0,
    },
    'within_section_regime': {
        sec: {
            'V': round(r['V'], 4) if 'V' in r else None,
            'chi2': round(r['chi2'], 1) if 'chi2' in r else None,
            'p': r.get('p'),
            'n': r.get('n'),
        }
        for sec, r in within_section_results.items()
    },
    'verdict': verdict,
    'verdict_reason': verdict_reason,
    'per_middle_results': {
        mid: {
            'count': middle_total[mid],
            'section_V': round(section_results[mid]['V'], 4) if 'V' in section_results.get(mid, {}) else None,
            'section_p': section_results[mid].get('p'),
            'section_significant': section_results[mid].get('significant', False),
            'regime_V': round(regime_results[mid]['V'], 4) if 'V' in regime_results.get(mid, {}) else None,
            'regime_p': regime_results[mid].get('p'),
            'regime_significant': regime_results[mid].get('significant', False),
        }
        for mid in common_middles
    },
    'enrichment_details': enrichment_details,
    'top_significant': [
        {'middle': mid, 'V': round(v, 4), 'chi2': round(chi2, 1), 'p': p, 'n': n}
        for mid, v, chi2, p, n in top_sig[:20]
    ],
    'comparison_per_middle': comparison[:30],
}

out_path = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results/suffix_section_interaction.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nOutput written to: {out_path}")
print("Done.")
