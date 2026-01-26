"""
ANIMAL SIGNATURE SCORING (Phase 1)

Goal: Score each A record for P(animal) using C505 + C527 markers.

Markers (from validated constraints):
- C505: Animal PP MIDDLEs enriched: 'te' 16.1×, 'ho' 8.6×, 'ke' 5.1×
- C527: Animal suffixes: 78% -ey/-ol, 0% -y/-dy (herb: 41% -y/-dy)

Output: animal_signatures.json with scored A records
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PHASE 1: ANIMAL SIGNATURE SCORING")
print("=" * 70)

# C505 animal PP markers with enrichment factors
ANIMAL_PP_MARKERS = {
    'te': 16.1,  # Highest enrichment
    'ho': 8.6,
    'ke': 5.1,
}

# C527 suffix patterns
ANIMAL_SUFFIXES = {'ey', 'ol'}  # 78% in animal
HERB_SUFFIXES = {'y', 'dy'}     # 0% in animal, 41% in herb

# Build A record data
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

# Score each record
print("\nScoring records for animal probability...")

def score_animal(record_data):
    """
    Score a record for animal probability using C505 + C527 markers.

    Returns dict with component scores and total score.
    """
    middles = record_data['middles']
    suffixes = record_data['suffixes']

    # C505: PP marker score (weighted by enrichment)
    pp_score = 0
    pp_hits = []
    for middle in middles:
        for marker, weight in ANIMAL_PP_MARKERS.items():
            if marker in middle or middle == marker:
                pp_score += weight
                pp_hits.append(marker)

    # Normalize by token count to avoid bias toward longer records
    n_tokens = len(record_data['tokens']) or 1
    pp_score_norm = pp_score / n_tokens

    # C527: Suffix score
    animal_suffix_count = sum(1 for s in suffixes if s in ANIMAL_SUFFIXES)
    herb_suffix_count = sum(1 for s in suffixes if s in HERB_SUFFIXES)

    # Suffix ratio: +1 for each animal suffix, -1 for each herb suffix
    suffix_score = animal_suffix_count - herb_suffix_count
    suffix_score_norm = suffix_score / n_tokens if n_tokens > 0 else 0

    # Combined score (weighted)
    # PP markers are stronger indicators (higher enrichment factors)
    total_score = pp_score_norm * 0.7 + suffix_score_norm * 0.3

    return {
        'pp_score': pp_score,
        'pp_score_norm': pp_score_norm,
        'pp_hits': pp_hits,
        'animal_suffix_count': animal_suffix_count,
        'herb_suffix_count': herb_suffix_count,
        'suffix_score_norm': suffix_score_norm,
        'total_score': total_score,
        'n_tokens': n_tokens,
    }

# Score all records
scored_records = []
for record_id, data in a_records.items():
    score = score_animal(data)
    scored_records.append({
        'record_id': record_id,
        'folio': data['folio'],
        'line': data['line'],
        'n_tokens': score['n_tokens'],
        'pp_score': score['pp_score'],
        'pp_score_norm': score['pp_score_norm'],
        'pp_hits': score['pp_hits'],
        'animal_suffix_count': score['animal_suffix_count'],
        'herb_suffix_count': score['herb_suffix_count'],
        'suffix_score_norm': score['suffix_score_norm'],
        'total_score': score['total_score'],
        'middles': data['middles'],
        'suffixes': data['suffixes'],
    })

# Sort by total score
scored_records.sort(key=lambda x: -x['total_score'])

# Statistics
scores = [r['total_score'] for r in scored_records]
print(f"\nScore distribution:")
print(f"  Min: {min(scores):.3f}")
print(f"  Max: {max(scores):.3f}")
print(f"  Mean: {np.mean(scores):.3f}")
print(f"  Std: {np.std(scores):.3f}")
print(f"  Median: {np.median(scores):.3f}")

# Find threshold for "high confidence animal"
# Use mean + 1.5 std as threshold
threshold = np.mean(scores) + 1.5 * np.std(scores)
high_confidence = [r for r in scored_records if r['total_score'] >= threshold]

print(f"\nThreshold (mean + 1.5*std): {threshold:.3f}")
print(f"High-confidence animal records: {len(high_confidence)}")

# Also check top percentiles
p90 = np.percentile(scores, 90)
p95 = np.percentile(scores, 95)
p99 = np.percentile(scores, 99)

print(f"\nPercentile thresholds:")
print(f"  90th percentile: {p90:.3f} ({sum(1 for s in scores if s >= p90)} records)")
print(f"  95th percentile: {p95:.3f} ({sum(1 for s in scores if s >= p95)} records)")
print(f"  99th percentile: {p99:.3f} ({sum(1 for s in scores if s >= p99)} records)")

# Show top 20 animal records
print("\n" + "=" * 70)
print("TOP 20 ANIMAL-SIGNATURE RECORDS")
print("=" * 70)

print(f"\n{'Record':<15} {'Score':<8} {'PP Hits':<20} {'A-Suf':<6} {'H-Suf':<6}")
print("-" * 60)
for r in scored_records[:20]:
    pp_hits = ','.join(r['pp_hits'][:3]) if r['pp_hits'] else '-'
    print(f"{r['record_id']:<15} {r['total_score']:.3f}    {pp_hits:<20} {r['animal_suffix_count']:<6} {r['herb_suffix_count']:<6}")

# Show distribution of PP marker hits
print("\n" + "=" * 70)
print("PP MARKER DISTRIBUTION IN HIGH-CONFIDENCE RECORDS")
print("=" * 70)

marker_counts = Counter()
for r in high_confidence:
    for hit in r['pp_hits']:
        marker_counts[hit] += 1

print(f"\nMarker frequency in {len(high_confidence)} high-confidence records:")
for marker, count in marker_counts.most_common():
    pct = 100 * count / len(high_confidence)
    print(f"  '{marker}': {count} ({pct:.1f}%)")

# Save results
results = {
    'metadata': {
        'phase': 1,
        'description': 'Animal signature scoring',
        'total_records': len(scored_records),
        'threshold': threshold,
        'threshold_method': 'mean + 1.5*std',
        'high_confidence_count': len(high_confidence),
        'markers_used': {
            'pp_markers': ANIMAL_PP_MARKERS,
            'animal_suffixes': list(ANIMAL_SUFFIXES),
            'herb_suffixes': list(HERB_SUFFIXES),
        },
    },
    'statistics': {
        'score_min': min(scores),
        'score_max': max(scores),
        'score_mean': np.mean(scores),
        'score_std': np.std(scores),
        'score_median': np.median(scores),
        'p90': p90,
        'p95': p95,
        'p99': p99,
    },
    'high_confidence_records': [
        {
            'record_id': r['record_id'],
            'folio': r['folio'],
            'line': r['line'],
            'total_score': r['total_score'],
            'pp_hits': r['pp_hits'],
            'animal_suffix_count': r['animal_suffix_count'],
            'herb_suffix_count': r['herb_suffix_count'],
            'middles': r['middles'],
        }
        for r in high_confidence
    ],
    'all_records_summary': [
        {
            'record_id': r['record_id'],
            'total_score': r['total_score'],
            'pp_hits': r['pp_hits'],
        }
        for r in scored_records
    ],
}

output_path = 'phases/ANIMAL_RECIPE_TRACE/results/animal_signatures.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Summary for checkpoint
print("\n" + "=" * 70)
print("PHASE 1 COMPLETE - SUMMARY FOR CHECKPOINT")
print("=" * 70)

print(f"""
Key Results:
- Total A records scored: {len(scored_records)}
- Threshold (mean + 1.5*std): {threshold:.3f}
- High-confidence animal records: {len(high_confidence)}
- Top marker in high-confidence: '{marker_counts.most_common(1)[0][0]}' ({marker_counts.most_common(1)[0][1]} hits)

Next Step: Phase 2 - Trace these {len(high_confidence)} records through AZC
           to find which B vocabulary is legal for animal materials.
""")
