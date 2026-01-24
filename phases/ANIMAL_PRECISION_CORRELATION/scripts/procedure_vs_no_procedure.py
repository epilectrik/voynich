#!/usr/bin/env python3
"""
Direct comparison: Materials WITH procedures vs WITHOUT procedures.

Test hypothesis:
- Materials with specific procedures → rich records → RI convergence works
- Materials without procedures → sparse records → RI convergence fails

Compare:
- ANIMAL (fire=4, has procedure) - WORKS
- HERB (fire=2, precision override) - WORKS (tested above)
- FLOWER (fire=1, NO procedure) - FAILS
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('C:/git/voynich')

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or '_EMPTY_'
            return remainder or '_EMPTY_'
    return None

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared = a_middles & b_middles
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

class_lookup = {}
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    if posterior:
        class_lookup[middle] = posterior

# Get high-prior tokens for each class
def get_top_tokens(class_name, min_prob=0.5):
    """Get tokens with high probability for a given class."""
    tokens = []
    for middle, priors in class_lookup.items():
        prob = priors.get(class_name, 0)
        if prob >= min_prob:
            tokens.append((middle, prob))
    return sorted(tokens, key=lambda x: -x[1])

print("=" * 70)
print("PROCEDURE vs NO-PROCEDURE COMPARISON")
print("=" * 70)
print()

# Get top tokens for each class
animal_tokens = get_top_tokens('animal', 0.3)
herb_tokens = get_top_tokens('herb', 0.3) + get_top_tokens('hot_dry_herb', 0.3) + get_top_tokens('moderate_herb', 0.3)
flower_tokens = get_top_tokens('cold_moist_flower', 0.3) + get_top_tokens('hot_flower', 0.3)

print(f"Animal tokens (P>=0.3): {len(animal_tokens)}")
print(f"Herb tokens (P>=0.3): {len(herb_tokens)}")
print(f"Flower tokens (P>=0.3): {len(flower_tokens)}")
print()

# Build record structure for each token
def analyze_token_records(token_list, class_name):
    """Analyze record structure for tokens of a given class."""
    results = []

    for token, prob in token_list[:20]:  # Top 20
        # Find all A records containing this token
        token_records = df_a[df_a['middle'] == token][['folio', 'line_number']].drop_duplicates()

        if len(token_records) == 0:
            continue

        record_stats = []
        for _, row in token_records.iterrows():
            folio, line = row['folio'], row['line_number']
            record = df_a[(df_a['folio'] == folio) & (df_a['line_number'] == line)]
            middles = set(record['middle'].dropna().unique()) - infrastructure

            pp_overlap = middles & shared
            ri = middles - b_middles

            record_stats.append({
                'folio': folio,
                'line': line,
                'n_middles': len(middles),
                'n_pp': len(pp_overlap),
                'n_ri': len(ri)
            })

        avg_pp = sum(r['n_pp'] for r in record_stats) / len(record_stats) if record_stats else 0
        avg_ri = sum(r['n_ri'] for r in record_stats) / len(record_stats) if record_stats else 0
        avg_middles = sum(r['n_middles'] for r in record_stats) / len(record_stats) if record_stats else 0

        results.append({
            'token': token,
            'prob': prob,
            'n_records': len(record_stats),
            'avg_middles': avg_middles,
            'avg_pp': avg_pp,
            'avg_ri': avg_ri
        })

    return results

print("-" * 70)
print("Analyzing record structure by material class...")
print("-" * 70)
print()

# Analyze each class
animal_stats = analyze_token_records(animal_tokens, 'animal')
herb_stats = analyze_token_records(herb_tokens, 'herb')
flower_stats = analyze_token_records(flower_tokens, 'flower')

# Summary stats
def summarize_class(stats, class_name):
    if not stats:
        return {'class': class_name, 'n_tokens': 0, 'avg_pp': 0, 'avg_ri': 0, 'avg_middles': 0}

    total_pp = sum(s['avg_pp'] * s['n_records'] for s in stats)
    total_ri = sum(s['avg_ri'] * s['n_records'] for s in stats)
    total_middles = sum(s['avg_middles'] * s['n_records'] for s in stats)
    total_records = sum(s['n_records'] for s in stats)

    return {
        'class': class_name,
        'n_tokens': len(stats),
        'avg_pp': total_pp / total_records if total_records else 0,
        'avg_ri': total_ri / total_records if total_records else 0,
        'avg_middles': total_middles / total_records if total_records else 0
    }

animal_summary = summarize_class(animal_stats, 'ANIMAL (procedure)')
herb_summary = summarize_class(herb_stats, 'HERB (procedure)')
flower_summary = summarize_class(flower_stats, 'FLOWER (no procedure)')

print("=" * 70)
print("SUMMARY: Record Structure by Material Class")
print("=" * 70)
print()
print(f"{'Class':<25} {'Tokens':<8} {'Avg MIDDLEs':<12} {'Avg PP':<10} {'Avg RI':<10}")
print("-" * 65)

for summary in [animal_summary, herb_summary, flower_summary]:
    print(f"{summary['class']:<25} {summary['n_tokens']:<8} {summary['avg_middles']:<12.1f} {summary['avg_pp']:<10.1f} {summary['avg_ri']:<10.1f}")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

# Determine if hypothesis is confirmed
if animal_summary['avg_pp'] > 2 and flower_summary['avg_pp'] < 1:
    print("HYPOTHESIS CONFIRMED:")
    print()
    print("  Materials WITH specific procedures (animal, some herbs):")
    print(f"    -> Rich records ({animal_summary['avg_middles']:.1f} MIDDLEs)")
    print(f"    -> High PP overlap ({animal_summary['avg_pp']:.1f} tokens)")
    print(f"    -> RI tokens available ({animal_summary['avg_ri']:.1f} per record)")
    print(f"    -> PP convergence WORKS")
    print()
    print("  Materials WITHOUT specific procedures (flowers):")
    print(f"    -> Sparse records ({flower_summary['avg_middles']:.1f} MIDDLEs)")
    print(f"    -> Low/no PP overlap ({flower_summary['avg_pp']:.1f} tokens)")
    print(f"    -> Few RI tokens ({flower_summary['avg_ri']:.1f} per record)")
    print(f"    -> PP convergence FAILS")
    print()
    print("CONCLUSION:")
    print("  Generic materials (flowers, common herbs) treated identically in Brunschwig")
    print("  -> No need for specific tokens, just class-level designation")
    print("  -> These appear in labels or sparse entries, not detailed records")
    print()
    print("  Specialized materials (animals, precision herbs) have unique procedures")
    print("  -> Each material needs specific identification")
    print("  -> These appear in rich records with PP context for triangulation")

# Show specific examples
print()
print("-" * 70)
print("TOP EXAMPLES BY CLASS")
print("-" * 70)
print()

for class_name, stats in [('ANIMAL', animal_stats), ('HERB', herb_stats), ('FLOWER', flower_stats)]:
    print(f"{class_name}:")
    for s in stats[:5]:
        print(f"  {s['token']} (P={s['prob']:.2f}): {s['n_records']} records, avg {s['avg_pp']:.1f} PP, {s['avg_ri']:.1f} RI")
    print()
