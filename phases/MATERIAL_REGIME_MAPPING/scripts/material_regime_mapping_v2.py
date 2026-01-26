"""
MATERIAL-CLASS REGIME MAPPING v2

Uses both PP markers AND suffix patterns for classification.

Animal markers (from enrichment analysis):
- PP: pch (43x), opch (18x), octh (9x), cph (3.7x), kch (3.7x), ch (2.9x), ckh (2.9x), h (2.5x)
- Suffix: ey, ol enriched; y, dy depleted

Herb markers:
- PP: keo (66x), eok (52x), ko (33x), cho (33x), to (33x), eo (3.3x)
- Suffix: y, dy enriched; ey, ol depleted
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
print("MATERIAL-CLASS REGIME MAPPING v2")
print("(Using PP markers + suffix patterns)")
print("=" * 70)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Material class markers (empirically derived)
MATERIAL_MARKERS = {
    'animal': {
        'pp_markers': {
            'pch': 43.0, 'opch': 18.0, 'octh': 9.0, 'cph': 3.7,
            'kch': 3.7, 'ch': 2.9, 'ckh': 2.9, 'h': 2.5, 'tch': 2.1
        },
        'positive_suffixes': {'ey', 'ol'},
        'negative_suffixes': {'y', 'dy'},
    },
    'herb': {
        'pp_markers': {
            'keo': 66.0, 'eok': 52.0, 'ko': 33.0, 'cho': 33.0,
            'to': 33.0, 'ry': 28.0, 'eo': 3.3, 'eeo': 3.0, 'eod': 3.0
        },
        'positive_suffixes': {'y', 'dy'},
        'negative_suffixes': {'ey', 'ol'},
    },
}

# Build A record profiles
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

# Score records for each material class
def score_material_class(record_data, markers):
    """Score using both PP and suffix markers."""
    middles = record_data['middles']
    suffixes = record_data['suffixes']
    n_tokens = len(record_data['tokens']) or 1

    # PP marker score (weighted by enrichment)
    pp_score = 0
    pp_hits = []
    for middle in middles:
        for marker, weight in markers.get('pp_markers', {}).items():
            if marker == middle or marker in middle:
                pp_score += weight
                pp_hits.append(marker)

    pp_score_norm = pp_score / n_tokens

    # Suffix score
    pos_count = sum(1 for s in suffixes if s in markers.get('positive_suffixes', set()))
    neg_count = sum(1 for s in suffixes if s in markers.get('negative_suffixes', set()))
    suffix_score = pos_count - neg_count
    suffix_score_norm = suffix_score / n_tokens

    # Combined score (PP weighted higher due to stronger enrichment)
    total_score = pp_score_norm * 0.6 + suffix_score_norm * 0.4

    return {
        'pp_score_norm': pp_score_norm,
        'pp_hits': pp_hits,
        'suffix_score_norm': suffix_score_norm,
        'total_score': total_score,
    }

# Score all records
animal_scores = {rid: score_material_class(data, MATERIAL_MARKERS['animal'])
                 for rid, data in a_records.items()}
herb_scores = {rid: score_material_class(data, MATERIAL_MARKERS['herb'])
               for rid, data in a_records.items()}

# Classify records
def classify_records(animal_scores, herb_scores, threshold_mult=1.5):
    """Classify records as animal, herb, or neutral."""
    animal_vals = [s['total_score'] for s in animal_scores.values()]
    herb_vals = [s['total_score'] for s in herb_scores.values()]

    animal_thresh = np.mean(animal_vals) + threshold_mult * np.std(animal_vals)
    herb_thresh = np.mean(herb_vals) + threshold_mult * np.std(herb_vals)

    animal_high = {rid for rid, s in animal_scores.items() if s['total_score'] >= animal_thresh}
    herb_high = {rid for rid, s in herb_scores.items() if s['total_score'] >= herb_thresh}

    # Remove overlaps - assign to higher score
    overlap = animal_high & herb_high
    for rid in overlap:
        if animal_scores[rid]['total_score'] > herb_scores[rid]['total_score']:
            herb_high.discard(rid)
        else:
            animal_high.discard(rid)

    return animal_high, herb_high, animal_thresh, herb_thresh

animal_high, herb_high, animal_thresh, herb_thresh = classify_records(animal_scores, herb_scores)

print(f"\nClassification (mean + 1.5*std threshold):")
print(f"  Animal high-confidence: {len(animal_high)} records")
print(f"  Herb high-confidence: {len(herb_high)} records")
print(f"  Overlap removed: {len(animal_high & herb_high)}")

# Build B data
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
        })
        b_token_set.add(token.word)

b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

# Build A record profiles for AZC filtering
a_profiles = {}
for record_id, data in a_records.items():
    a_profiles[record_id] = {
        'middles': set(data['middles']),
        'prefixes': set(data['prefixes']) | {''},
        'suffixes': set(data['suffixes']) | {''},
    }

# Get compatible B tokens
def get_compatible_b_tokens(a_profile, b_tokens):
    compatible = []
    for bt in b_tokens:
        if (bt['middle'] in a_profile['middles'] and
            bt['prefix'] in a_profile['prefixes'] and
            bt['suffix'] in a_profile['suffixes']):
            compatible.append(bt)
    return compatible

def get_class_compatible_middles(high_conf_records, a_profiles, b_tokens):
    all_compatible = Counter()
    for rid in high_conf_records:
        if rid in a_profiles:
            compatible = get_compatible_b_tokens(a_profiles[rid], b_tokens)
            for t in compatible:
                if t['middle']:
                    all_compatible[t['middle']] += 1
    return all_compatible

animal_middles = get_class_compatible_middles(animal_high, a_profiles, b_tokens)
herb_middles = get_class_compatible_middles(herb_high, a_profiles, b_tokens)

print(f"\nCompatible B MIDDLEs:")
print(f"  Animal: {len(animal_middles)}")
print(f"  Herb: {len(herb_middles)}")

# Compute folio reception
def compute_reception(compatible_middles, b_folio_middles):
    compatible_set = set(compatible_middles.keys())
    reception = {}
    for folio, middles in b_folio_middles.items():
        overlap = middles & compatible_set
        rate = len(overlap) / len(middles) if middles else 0
        reception[folio] = {'reception_rate': rate, 'compatible': len(overlap), 'total': len(middles)}
    return reception

animal_reception = compute_reception(animal_middles, b_folio_middles)
herb_reception = compute_reception(herb_middles, b_folio_middles)

# Get REGIME distribution for high-reception folios
def get_regime_dist(reception, folio_to_regime, pct=75):
    rates = [r['reception_rate'] for r in reception.values()]
    thresh = np.percentile(rates, pct)
    high_folios = [f for f, r in reception.items() if r['reception_rate'] >= thresh]
    regimes = Counter([folio_to_regime[f] for f in high_folios if f in folio_to_regime])
    return regimes, thresh, len(high_folios)

# Baseline
all_folios = [f for f in b_folio_middles.keys() if f in folio_to_regime]
baseline = Counter([folio_to_regime[f] for f in all_folios])

animal_regimes, animal_thresh_r, animal_n = get_regime_dist(animal_reception, folio_to_regime)
herb_regimes, herb_thresh_r, herb_n = get_regime_dist(herb_reception, folio_to_regime)

print("\n" + "=" * 70)
print("REGIME DISTRIBUTION BY MATERIAL CLASS")
print("=" * 70)

print(f"\nBaseline ({len(all_folios)} folios):")
for r in sorted(baseline.keys()):
    print(f"  {r}: {baseline[r]} ({100*baseline[r]/len(all_folios):.1f}%)")

print(f"\nANIMAL (n={animal_n}, reception threshold={animal_thresh_r:.3f}):")
for r in sorted(baseline.keys()):
    count = animal_regimes.get(r, 0)
    pct = 100 * count / animal_n if animal_n else 0
    exp = baseline[r] / len(all_folios) * animal_n
    enrich = count / exp if exp > 0 else 0
    print(f"  {r}: {count} ({pct:.1f}%) - {enrich:.2f}x")

print(f"\nHERB (n={herb_n}, reception threshold={herb_thresh_r:.3f}):")
for r in sorted(baseline.keys()):
    count = herb_regimes.get(r, 0)
    pct = 100 * count / herb_n if herb_n else 0
    exp = baseline[r] / len(all_folios) * herb_n
    enrich = count / exp if exp > 0 else 0
    print(f"  {r}: {count} ({pct:.1f}%) - {enrich:.2f}x")

# Chi-square tests
def chi_square(observed, baseline, n):
    regimes = sorted(baseline.keys())
    obs = [observed.get(r, 0) for r in regimes]
    exp = [baseline[r] / sum(baseline.values()) * n for r in regimes]
    return stats.chisquare(obs, exp)

animal_chi2, animal_p = chi_square(animal_regimes, baseline, animal_n)
herb_chi2, herb_p = chi_square(herb_regimes, baseline, herb_n)

print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)
print(f"\nAnimal: chi2={animal_chi2:.3f}, p={animal_p:.6f}")
print(f"Herb: chi2={herb_chi2:.3f}, p={herb_p:.6f}")

# Mean reception by REGIME
print("\n" + "=" * 70)
print("MEAN RECEPTION RATE BY REGIME")
print("=" * 70)

def mean_by_regime(reception, regime_mapping):
    result = {}
    for regime, folios in regime_mapping.items():
        rates = [reception[f]['reception_rate'] for f in folios if f in reception]
        if rates:
            result[regime] = np.mean(rates)
    return result

animal_means = mean_by_regime(animal_reception, regime_mapping)
herb_means = mean_by_regime(herb_reception, regime_mapping)

print(f"\n{'REGIME':<12} {'Animal':<12} {'Herb':<12} {'Diff':<12}")
print("-" * 48)
for r in sorted(regime_mapping.keys()):
    a = animal_means.get(r, 0)
    h = herb_means.get(r, 0)
    print(f"{r:<12} {a:.3f}        {h:.3f}        {a-h:+.3f}")

# Find dominant REGIME for each class
def find_dominant(regime_counts, baseline, n):
    best = None
    best_enrich = 0
    for r, count in regime_counts.items():
        exp = baseline[r] / sum(baseline.values())
        enrich = (count / n) / exp if exp > 0 else 0
        if enrich > best_enrich:
            best_enrich = enrich
            best = r
    return best, best_enrich

animal_dom, animal_enrich = find_dominant(animal_regimes, baseline, animal_n)
herb_dom, herb_enrich = find_dominant(herb_regimes, baseline, herb_n)

# Are they different?
print("\n" + "=" * 70)
print("SUMMARY: MATERIAL -> REGIME MAPPING")
print("=" * 70)

print(f"""
CLASSIFICATION SUMMARY:
- Animal high-confidence records: {len(animal_high)}
- Herb high-confidence records: {len(herb_high)}

REGIME ROUTING:
| Material | Dominant REGIME | Enrichment | Chi2 p-value |
|----------|-----------------|------------|--------------|
| Animal   | {animal_dom}    | {animal_enrich:.2f}x       | {animal_p:.6f} |
| Herb     | {herb_dom}      | {herb_enrich:.2f}x       | {herb_p:.6f} |

DIFFERENTIATION:
""")

if animal_dom == herb_dom:
    # Same dominant REGIME - check secondary preferences
    print(f"Both classes route primarily to {animal_dom}.")
    print("\nSecondary preferences:")

    for r in sorted(baseline.keys()):
        if r != animal_dom:
            a_enrich = (animal_regimes.get(r, 0) / animal_n) / (baseline[r] / len(all_folios)) if animal_n else 0
            h_enrich = (herb_regimes.get(r, 0) / herb_n) / (baseline[r] / len(all_folios)) if herb_n else 0
            diff = a_enrich - h_enrich
            if abs(diff) > 0.3:
                print(f"  {r}: Animal {a_enrich:.2f}x vs Herb {h_enrich:.2f}x (diff={diff:+.2f})")

    print("\nCheck if they route to DIFFERENT secondary REGIMEs:")
    # REGIME where animal > herb
    animal_preferred = None
    herb_preferred = None
    for r in sorted(baseline.keys()):
        a_enrich = (animal_regimes.get(r, 0) / animal_n) / (baseline[r] / len(all_folios)) if animal_n else 0
        h_enrich = (herb_regimes.get(r, 0) / herb_n) / (baseline[r] / len(all_folios)) if herb_n else 0
        if a_enrich > h_enrich and a_enrich > 0.5:
            if animal_preferred is None or a_enrich > animal_preferred[1]:
                animal_preferred = (r, a_enrich)
        if h_enrich > a_enrich and h_enrich > 0.5:
            if herb_preferred is None or h_enrich > herb_preferred[1]:
                herb_preferred = (r, h_enrich)

    if animal_preferred and herb_preferred and animal_preferred[0] != herb_preferred[0]:
        print(f"\n  Animal prefers {animal_preferred[0]} ({animal_preferred[1]:.2f}x)")
        print(f"  Herb prefers {herb_preferred[0]} ({herb_preferred[1]:.2f}x)")
    else:
        print("\n  No clear secondary differentiation found.")
else:
    print(f"Material classes route to DIFFERENT REGIMEs!")
    print(f"  Animal -> {animal_dom}")
    print(f"  Herb -> {herb_dom}")

# Save results
results = {
    'animal': {
        'n_records': len(animal_high),
        'dominant_regime': animal_dom,
        'enrichment': animal_enrich,
        'chi2_p': animal_p,
        'regime_distribution': dict(animal_regimes),
        'mean_reception': animal_means,
    },
    'herb': {
        'n_records': len(herb_high),
        'dominant_regime': herb_dom,
        'enrichment': herb_enrich,
        'chi2_p': herb_p,
        'regime_distribution': dict(herb_regimes),
        'mean_reception': herb_means,
    },
    'baseline': dict(baseline),
}

with open('phases/MATERIAL_REGIME_MAPPING/results/material_regime_mapping_v2.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved.")
