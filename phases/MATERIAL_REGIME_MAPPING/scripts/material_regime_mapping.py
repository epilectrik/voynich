"""
MATERIAL-CLASS REGIME MAPPING

Goal: Complete the Material -> PP Profile -> REGIME mapping for all material classes.
Tests whether PP profiles encode material-appropriate execution contexts.

From C505/C527:
- Animal: te/ho/ke enriched, 0% -y/-dy, 78% -ey/-ol -> REGIME_4 (confirmed)
- Herb: 41% -y/-dy, 27% -ey/-ol (opposite suffix pattern)
- Water/Gentle: te 19.2x enriched

This script:
1. Identifies material-class signatures using PP/suffix markers
2. Traces each class through AZC filtering
3. Maps to REGIME distribution
4. Compares routing patterns across material classes
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("MATERIAL-CLASS REGIME MAPPING")
print("=" * 70)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# =============================================================================
# STEP 1: BUILD A RECORD PROFILES
# =============================================================================
print("\nBuilding A record profiles...")

a_records = defaultdict(lambda: {
    'tokens': [],
    'middles': [],
    'prefixes': [],
    'suffixes': [],
    'folio': None,
    'line': None,
})

for token in tx.currier_a():
    record_id = f"{token.folio}:{token.line}"
    a_records[record_id]['folio'] = token.folio
    a_records[record_id]['line'] = token.line

    if token.word:
        m = morph.extract(token.word)
        a_records[record_id]['tokens'].append(token.word)
        if m.middle:
            a_records[record_id]['middles'].append(m.middle)
        if m.prefix:
            a_records[record_id]['prefixes'].append(m.prefix)
        if m.suffix:
            a_records[record_id]['suffixes'].append(m.suffix)

print(f"Total A records: {len(a_records)}")

# =============================================================================
# STEP 2: DEFINE MATERIAL CLASS MARKERS
# =============================================================================

# From C505 and C527
MATERIAL_MARKERS = {
    'animal': {
        'pp_markers': {'te': 16.1, 'ho': 8.6, 'ke': 5.1},  # Enrichment factors
        'positive_suffixes': {'ey', 'ol'},  # 78% in animal
        'negative_suffixes': {'y', 'dy'},   # 0% in animal
        'description': 'Heat-sensitive proteins/fats (C505, C527)',
    },
    'herb': {
        'pp_markers': {},  # Will identify from inverse of animal
        'positive_suffixes': {'y', 'dy'},   # 41% in herb
        'negative_suffixes': {'ey', 'ol'},  # Only 27% in herb
        'description': 'Plant materials - opposite suffix pattern',
    },
}

# =============================================================================
# STEP 3: SCORE RECORDS FOR EACH MATERIAL CLASS
# =============================================================================
print("\nScoring records for material classes...")

def score_material_class(record_data, markers):
    """Score a record for material class probability."""
    middles = record_data['middles']
    suffixes = record_data['suffixes']
    n_tokens = len(record_data['tokens']) or 1

    # PP marker score
    pp_score = 0
    pp_hits = []
    for middle in middles:
        for marker, weight in markers.get('pp_markers', {}).items():
            if marker in middle or middle == marker:
                pp_score += weight
                pp_hits.append(marker)
    pp_score_norm = pp_score / n_tokens

    # Suffix score
    pos_count = sum(1 for s in suffixes if s in markers.get('positive_suffixes', set()))
    neg_count = sum(1 for s in suffixes if s in markers.get('negative_suffixes', set()))
    suffix_score = pos_count - neg_count
    suffix_score_norm = suffix_score / n_tokens

    # Combined score
    total_score = pp_score_norm * 0.7 + suffix_score_norm * 0.3

    return {
        'pp_score_norm': pp_score_norm,
        'pp_hits': pp_hits,
        'suffix_score_norm': suffix_score_norm,
        'total_score': total_score,
        'pos_suffix_count': pos_count,
        'neg_suffix_count': neg_count,
    }

# Score all records for animal class
animal_scores = {}
for record_id, data in a_records.items():
    score = score_material_class(data, MATERIAL_MARKERS['animal'])
    animal_scores[record_id] = score

# Score all records for herb class (opposite suffix pattern)
herb_scores = {}
for record_id, data in a_records.items():
    score = score_material_class(data, MATERIAL_MARKERS['herb'])
    herb_scores[record_id] = score

# =============================================================================
# STEP 4: IDENTIFY HIGH-CONFIDENCE RECORDS FOR EACH CLASS
# =============================================================================
print("\nIdentifying high-confidence records...")

def get_high_confidence(scores, threshold_multiplier=1.5):
    """Get records above mean + multiplier*std threshold."""
    all_scores = [s['total_score'] for s in scores.values()]
    threshold = np.mean(all_scores) + threshold_multiplier * np.std(all_scores)
    high_conf = {rid: s for rid, s in scores.items() if s['total_score'] >= threshold}
    return high_conf, threshold

# Animal high-confidence (using positive animal markers)
animal_high, animal_thresh = get_high_confidence(animal_scores)
print(f"Animal high-confidence: {len(animal_high)} records (threshold: {animal_thresh:.3f})")

# Herb high-confidence (using positive herb markers = negative animal markers)
herb_high, herb_thresh = get_high_confidence(herb_scores)
print(f"Herb high-confidence: {len(herb_high)} records (threshold: {herb_thresh:.3f})")

# Also identify "neutral" records (low scores on both)
neutral_records = {}
for record_id in a_records:
    animal_score = animal_scores[record_id]['total_score']
    herb_score = herb_scores[record_id]['total_score']
    if animal_score < animal_thresh and herb_score < herb_thresh:
        neutral_records[record_id] = {
            'animal_score': animal_score,
            'herb_score': herb_score,
        }

print(f"Neutral records: {len(neutral_records)}")

# =============================================================================
# STEP 5: BUILD B FOLIO PROFILES FOR RECEPTION ANALYSIS
# =============================================================================
print("\nBuilding B folio profiles...")

# Build A record morphological profiles for AZC filtering
a_record_profiles = {}
for record_id, data in a_records.items():
    a_record_profiles[record_id] = {
        'middles': set(data['middles']),
        'prefixes': set(data['prefixes']) | {''},  # Include empty for bare tokens
        'suffixes': set(data['suffixes']) | {''},  # Include empty for unsuffixed
    }

# Build B token data
b_tokens = []
b_token_set = set()
for token in tx.currier_b():
    if token.word and token.word not in b_token_set:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
            'folio': token.folio,
        })
        b_token_set.add(token.word)

print(f"Total unique B tokens: {len(b_tokens)}")

# Build B folio -> MIDDLE mapping
b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

# =============================================================================
# STEP 6: COMPUTE COMPATIBLE VOCABULARY FOR EACH MATERIAL CLASS
# =============================================================================
print("\nComputing compatible B vocabulary per material class...")

def get_compatible_b_tokens(a_profile, b_tokens):
    """Apply C502.a filtering."""
    compatible = []
    for bt in b_tokens:
        middle_ok = bt['middle'] in a_profile['middles']
        prefix_ok = bt['prefix'] in a_profile['prefixes']
        suffix_ok = bt['suffix'] in a_profile['suffixes']
        if middle_ok and prefix_ok and suffix_ok:
            compatible.append(bt)
    return compatible

def get_class_compatible_middles(high_conf_records, a_record_profiles, b_tokens):
    """Get all compatible B MIDDLEs for a material class."""
    all_compatible_middles = Counter()
    for record_id in high_conf_records:
        if record_id in a_record_profiles:
            profile = a_record_profiles[record_id]
            compatible = get_compatible_b_tokens(profile, b_tokens)
            for t in compatible:
                if t['middle']:
                    all_compatible_middles[t['middle']] += 1
    return all_compatible_middles

animal_middles = get_class_compatible_middles(animal_high, a_record_profiles, b_tokens)
herb_middles = get_class_compatible_middles(herb_high, a_record_profiles, b_tokens)

print(f"Animal-compatible MIDDLEs: {len(animal_middles)}")
print(f"Herb-compatible MIDDLEs: {len(herb_middles)}")

# =============================================================================
# STEP 7: COMPUTE FOLIO RECEPTION FOR EACH MATERIAL CLASS
# =============================================================================
print("\nComputing folio reception rates...")

def compute_folio_reception(compatible_middles, b_folio_middles):
    """Compute reception rate for each B folio."""
    compatible_set = set(compatible_middles.keys())
    reception = {}
    for folio, middles in b_folio_middles.items():
        overlap = middles & compatible_set
        rate = len(overlap) / len(middles) if middles else 0
        reception[folio] = {
            'total_middles': len(middles),
            'compatible': len(overlap),
            'reception_rate': rate,
        }
    return reception

animal_reception = compute_folio_reception(animal_middles, b_folio_middles)
herb_reception = compute_folio_reception(herb_middles, b_folio_middles)

# =============================================================================
# STEP 8: COMPUTE REGIME DISTRIBUTION FOR EACH MATERIAL CLASS
# =============================================================================
print("\n" + "=" * 70)
print("REGIME DISTRIBUTION BY MATERIAL CLASS")
print("=" * 70)

def get_regime_distribution(reception, folio_to_regime, threshold_percentile=75):
    """Get REGIME distribution for high-reception folios."""
    # Get high-reception folios
    rates = [r['reception_rate'] for r in reception.values()]
    threshold = np.percentile(rates, threshold_percentile)

    high_reception = [f for f, r in reception.items() if r['reception_rate'] >= threshold]

    # Count REGIMEs
    regime_counts = Counter()
    for folio in high_reception:
        if folio in folio_to_regime:
            regime_counts[folio_to_regime[folio]] += 1

    return regime_counts, threshold, len(high_reception)

# Get baseline REGIME distribution
all_folios_with_regime = [f for f in b_folio_middles.keys() if f in folio_to_regime]
baseline_counts = Counter([folio_to_regime[f] for f in all_folios_with_regime])

print(f"\nBaseline REGIME distribution ({len(all_folios_with_regime)} folios):")
for regime in sorted(baseline_counts.keys()):
    pct = 100 * baseline_counts[regime] / len(all_folios_with_regime)
    print(f"  {regime}: {baseline_counts[regime]} ({pct:.1f}%)")

# Animal REGIME distribution
animal_regimes, animal_thresh_r, animal_n = get_regime_distribution(
    animal_reception, folio_to_regime, 75)

print(f"\nANIMAL high-reception folios (n={animal_n}, threshold={animal_thresh_r:.3f}):")
for regime in sorted(animal_regimes.keys()):
    pct = 100 * animal_regimes[regime] / animal_n if animal_n else 0
    expected = baseline_counts[regime] / len(all_folios_with_regime) * animal_n
    enrichment = animal_regimes[regime] / expected if expected > 0 else 0
    print(f"  {regime}: {animal_regimes[regime]} ({pct:.1f}%) - {enrichment:.2f}x enrichment")

# Herb REGIME distribution
herb_regimes, herb_thresh_r, herb_n = get_regime_distribution(
    herb_reception, folio_to_regime, 75)

print(f"\nHERB high-reception folios (n={herb_n}, threshold={herb_thresh_r:.3f}):")
for regime in sorted(herb_regimes.keys()):
    pct = 100 * herb_regimes[regime] / herb_n if herb_n else 0
    expected = baseline_counts[regime] / len(all_folios_with_regime) * herb_n
    enrichment = herb_regimes[regime] / expected if expected > 0 else 0
    print(f"  {regime}: {herb_regimes[regime]} ({pct:.1f}%) - {enrichment:.2f}x enrichment")

# =============================================================================
# STEP 9: STATISTICAL TESTS
# =============================================================================
print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

def chi_square_test(observed_counts, baseline_counts, n_observed):
    """Chi-square test for REGIME distribution."""
    regimes = sorted(set(observed_counts.keys()) | set(baseline_counts.keys()))
    observed = [observed_counts.get(r, 0) for r in regimes]
    total_baseline = sum(baseline_counts.values())
    expected = [baseline_counts.get(r, 0) / total_baseline * n_observed for r in regimes]

    # Filter out zeros
    filtered = [(o, e) for o, e in zip(observed, expected) if e > 0]
    if len(filtered) < 2:
        return None, None

    obs_f = [x[0] for x in filtered]
    exp_f = [x[1] for x in filtered]

    chi2, p = stats.chisquare(obs_f, exp_f)
    return chi2, p

animal_chi2, animal_p = chi_square_test(animal_regimes, baseline_counts, animal_n)
herb_chi2, herb_p = chi_square_test(herb_regimes, baseline_counts, herb_n)

print(f"\nAnimal REGIME distribution:")
print(f"  Chi-square: {animal_chi2:.3f}, p = {animal_p:.6f}" if animal_chi2 else "  Insufficient data")

print(f"\nHerb REGIME distribution:")
print(f"  Chi-square: {herb_chi2:.3f}, p = {herb_p:.6f}" if herb_chi2 else "  Insufficient data")

# =============================================================================
# STEP 10: COMPARE ANIMAL vs HERB REGIME PROFILES
# =============================================================================
print("\n" + "=" * 70)
print("MATERIAL CLASS COMPARISON")
print("=" * 70)

print("\nREGIME enrichment comparison:")
print(f"{'REGIME':<12} {'Animal':<15} {'Herb':<15} {'Difference':<15}")
print("-" * 55)

for regime in sorted(baseline_counts.keys()):
    base_pct = baseline_counts[regime] / len(all_folios_with_regime)

    animal_pct = animal_regimes.get(regime, 0) / animal_n if animal_n else 0
    animal_enrich = animal_pct / base_pct if base_pct > 0 else 0

    herb_pct = herb_regimes.get(regime, 0) / herb_n if herb_n else 0
    herb_enrich = herb_pct / base_pct if base_pct > 0 else 0

    diff = animal_enrich - herb_enrich

    print(f"{regime:<12} {animal_enrich:.2f}x          {herb_enrich:.2f}x          {diff:+.2f}")

# Mean reception rates by REGIME
print("\n" + "=" * 70)
print("MEAN RECEPTION RATE BY REGIME")
print("=" * 70)

def mean_reception_by_regime(reception, folio_to_regime, regime_mapping):
    """Compute mean reception rate per REGIME."""
    regime_rates = {}
    for regime, folios in regime_mapping.items():
        rates = [reception[f]['reception_rate'] for f in folios if f in reception]
        if rates:
            regime_rates[regime] = {
                'mean': np.mean(rates),
                'std': np.std(rates),
                'n': len(rates),
            }
    return regime_rates

animal_regime_rates = mean_reception_by_regime(animal_reception, folio_to_regime, regime_mapping)
herb_regime_rates = mean_reception_by_regime(herb_reception, folio_to_regime, regime_mapping)

print(f"\n{'REGIME':<12} {'Animal Mean':<15} {'Herb Mean':<15} {'Difference':<15}")
print("-" * 55)
for regime in sorted(regime_mapping.keys()):
    a_mean = animal_regime_rates.get(regime, {}).get('mean', 0)
    h_mean = herb_regime_rates.get(regime, {}).get('mean', 0)
    diff = a_mean - h_mean
    print(f"{regime:<12} {a_mean:.3f}           {h_mean:.3f}           {diff:+.3f}")

# ANOVA for each material class
print("\nANOVA tests (reception rate across REGIMEs):")

def anova_by_regime(reception, regime_mapping):
    """ANOVA test for reception rate differences across REGIMEs."""
    groups = []
    for regime, folios in regime_mapping.items():
        rates = [reception[f]['reception_rate'] for f in folios if f in reception]
        if rates:
            groups.append(rates)
    if len(groups) >= 2:
        f_stat, p = stats.f_oneway(*groups)
        return f_stat, p
    return None, None

animal_f, animal_anova_p = anova_by_regime(animal_reception, regime_mapping)
herb_f, herb_anova_p = anova_by_regime(herb_reception, regime_mapping)

print(f"  Animal: F={animal_f:.3f}, p={animal_anova_p:.6f}" if animal_f else "  Animal: insufficient data")
print(f"  Herb: F={herb_f:.3f}, p={herb_anova_p:.6f}" if herb_f else "  Herb: insufficient data")

# =============================================================================
# STEP 11: SAVE RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

results = {
    'metadata': {
        'description': 'Material-class REGIME mapping',
        'date': '2026-01-25',
    },
    'material_classes': {
        'animal': {
            'high_confidence_records': len(animal_high),
            'threshold': animal_thresh,
            'compatible_middles': len(animal_middles),
            'regime_distribution': dict(animal_regimes),
            'chi_square': animal_chi2,
            'chi_square_p': animal_p,
            'anova_f': animal_f,
            'anova_p': animal_anova_p,
            'regime_mean_reception': {
                r: animal_regime_rates.get(r, {}).get('mean', 0)
                for r in regime_mapping.keys()
            },
        },
        'herb': {
            'high_confidence_records': len(herb_high),
            'threshold': herb_thresh,
            'compatible_middles': len(herb_middles),
            'regime_distribution': dict(herb_regimes),
            'chi_square': herb_chi2,
            'chi_square_p': herb_p,
            'anova_f': herb_f,
            'anova_p': herb_anova_p,
            'regime_mean_reception': {
                r: herb_regime_rates.get(r, {}).get('mean', 0)
                for r in regime_mapping.keys()
            },
        },
    },
    'baseline': {
        'total_folios': len(all_folios_with_regime),
        'regime_distribution': dict(baseline_counts),
    },
}

output_path = 'phases/MATERIAL_REGIME_MAPPING/results/material_regime_mapping.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_path}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: MATERIAL -> REGIME MAPPING")
print("=" * 70)

# Find dominant REGIME for each class
def find_dominant_regime(regime_counts, baseline_counts, n_total):
    """Find most enriched REGIME."""
    best_regime = None
    best_enrichment = 0
    for regime, count in regime_counts.items():
        base_pct = baseline_counts.get(regime, 1) / sum(baseline_counts.values())
        enrichment = (count / n_total) / base_pct if base_pct > 0 else 0
        if enrichment > best_enrichment:
            best_enrichment = enrichment
            best_regime = regime
    return best_regime, best_enrichment

animal_dominant, animal_enrich = find_dominant_regime(animal_regimes, baseline_counts, animal_n)
herb_dominant, herb_enrich = find_dominant_regime(herb_regimes, baseline_counts, herb_n)

print(f"""
MATERIAL CLASS ROUTING SUMMARY:

| Material | Dominant REGIME | Enrichment | p-value |
|----------|-----------------|------------|---------|
| Animal   | {animal_dominant or 'N/A':<15} | {animal_enrich:.2f}x       | {animal_p:.6f if animal_p else 'N/A'} |
| Herb     | {herb_dominant or 'N/A':<15} | {herb_enrich:.2f}x       | {herb_p:.6f if herb_p else 'N/A'} |

REGIME CHARACTERISTICS (from C494 and prior):
- REGIME_1: Moderate, forgiving (escape 0.143)
- REGIME_2: Low intensity, introductory (escape 0.128)
- REGIME_3: High intensity, aggressive (escape 0.156)
- REGIME_4: Precision, tight control (escape 0.107)

INTERPRETATION:
""")

if animal_dominant == 'REGIME_4':
    print("- Animal -> REGIME_4: Heat-sensitive materials need precision (CONFIRMED)")
if herb_dominant:
    if herb_dominant == 'REGIME_1':
        print("- Herb -> REGIME_1: Standard materials accept moderate, forgiving execution")
    elif herb_dominant == 'REGIME_2':
        print("- Herb -> REGIME_2: Gentle materials prefer low-intensity execution")
    elif herb_dominant == 'REGIME_3':
        print("- Herb -> REGIME_3: Robust materials tolerate aggressive execution")
    elif herb_dominant == 'REGIME_4':
        print("- Herb -> REGIME_4: Also needs precision (surprising if true)")

print("""
TIER 4 MODEL (if confirmed):
PP profiles encode material-appropriate execution contexts.
Different material classes route to different REGIMEs based on
their operational requirements (heat sensitivity, robustness, etc.)
""")
