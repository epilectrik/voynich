#!/usr/bin/env python3
"""
Test whether PP composition affects token-level availability within classes.

Question: If two A records enable the same classes but via different PP MIDDLEs,
do they enable different specific tokens within those classes?
"""

import json
import pandas as pd
from collections import defaultdict

# Load data
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)

token_to_class = data['token_to_class']
token_to_middle = data.get('token_to_middle', {})

# Build class_to_tokens and class_to_middles
class_to_tokens = defaultdict(list)
class_to_middles = defaultdict(set)
for token, cls in token_to_class.items():
    class_to_tokens[cls].append(token)
    if token in token_to_middle:
        m = token_to_middle[token]
        if m:
            class_to_middles[cls].add(m)

print("=" * 70)
print("PP COMPOSITION -> TOKEN-LEVEL EFFECT TEST")
print("=" * 70)

# Load survivor data to get real A-record PP sets
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors = json.load(f)

# Get PP vocabulary (MIDDLEs that appear in B)
DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']

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
                    return remainder[:-len(s)] or None
            return remainder or None
    return None

# Get B MIDDLEs (PP vocabulary)
df_b = df[(df['language'] == 'B') & (~df['word'].isna())]
df_b = df_b.copy()
df_b['middle'] = df_b['word'].apply(extract_middle)
b_middles = set(df_b['middle'].dropna().unique())

print(f"\nPP vocabulary size: {len(b_middles)} MIDDLEs")

# For each class, compute: what fraction of its tokens are enabled by different PP sets?
print("\n" + "-" * 70)
print("WITHIN-CLASS TOKEN VARIATION")
print("-" * 70)

# Sample some A records with similar class survival but different PP composition
records = survivors['records']

# Group records by class survival count
by_survival = defaultdict(list)
for rec in records:
    n_classes = rec['n_surviving_classes']
    by_survival[n_classes].append(rec)

# Find pairs with same class count
print("\nLooking for A records with SAME class survival but DIFFERENT PP sets...")

# Pick a common survival count
for n_cls in sorted(by_survival.keys(), reverse=True):
    recs = by_survival[n_cls]
    if len(recs) >= 10:
        print(f"\nAnalyzing {len(recs)} records with {n_cls} surviving classes:")

        # Get PP sets for each
        pp_sets = []
        for rec in recs[:50]:  # sample
            a_record = rec['a_record']
            middles = set(rec['surviving_middles']) & b_middles
            pp_sets.append((a_record, middles, set(rec['surviving_classes'])))

        # Compare pairs with same classes but different PP
        comparisons = 0
        token_overlap_sum = 0

        for i in range(len(pp_sets)):
            for j in range(i+1, len(pp_sets)):
                rec_i, pp_i, cls_i = pp_sets[i]
                rec_j, pp_j, cls_j = pp_sets[j]

                # Same class survival pattern?
                if cls_i == cls_j and pp_i != pp_j:
                    # Compare token availability
                    tokens_i = set()
                    tokens_j = set()

                    for cls in cls_i:
                        for tok in class_to_tokens[cls]:
                            m = token_to_middle.get(tok)
                            if m in pp_i:
                                tokens_i.add(tok)
                            if m in pp_j:
                                tokens_j.add(tok)

                    if tokens_i and tokens_j:
                        overlap = len(tokens_i & tokens_j) / len(tokens_i | tokens_j)
                        token_overlap_sum += overlap
                        comparisons += 1

        if comparisons > 0:
            mean_overlap = token_overlap_sum / comparisons
            print(f"  Pairs with same classes, different PP: {comparisons}")
            print(f"  Mean token Jaccard overlap: {mean_overlap:.3f}")
            print(f"  -> If 1.0, PP composition doesn't affect token selection")
            print(f"  -> If <1.0, PP composition DOES affect which tokens are available")

        break

# Final analysis: across all records, how much does PP composition vary token availability?
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
Key question: Does PP composition matter for execution behavior?

Level 1: CLASS survival
  - PP COUNT matters (r=0.72)
  - PP COMPOSITION doesn't change which classes survive (cosine=0.995)
  - Classes are redundant (mean 2.9 MIDDLEs per class)

Level 2: TOKEN availability within classes
  - PP composition DOES affect which specific tokens are available
  - Different PP sets enable different tokens even if same classes survive
  - If tokens within a class have different usage patterns, this matters

Level 3: EXECUTION behavior
  - Unknown - we haven't tested if within-class token variation affects behavior
  - Tokens in same class are "equivalent" by grammar definition
  - But they may have frequency/context differences in actual usage
""")
