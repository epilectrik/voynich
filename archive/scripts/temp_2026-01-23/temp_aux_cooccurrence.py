#!/usr/bin/env python3
"""
Analyze AUXILIARY class co-occurrence patterns in Currier B.

Questions:
1. Which AUXILIARY classes co-occur on the same lines?
2. Which pairs NEVER co-occur?
3. What are the survival/filtering patterns?
"""

import json
import pandas as pd
from collections import defaultdict
from itertools import combinations

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']  # H track only
df = df.rename(columns={'line_number': 'line'})  # Standardize column name

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

# Identify AUXILIARY classes
aux_classes = [int(c) for c, role in class_to_role.items() if role == 'AUXILIARY']
aux_classes.sort()
print(f"AUXILIARY classes ({len(aux_classes)}): {aux_classes}")

# Filter to Currier B only
df_b = df[df['language'] == 'B'].copy()
print(f"\nCurrier B tokens: {len(df_b)}")

# Map tokens to classes
df_b['class'] = df_b['word'].map(token_to_class)
df_b = df_b.dropna(subset=['class'])
df_b['class'] = df_b['class'].astype(int)
print(f"Tokens with class mapping: {len(df_b)}")

# Filter to AUXILIARY tokens only
df_aux = df_b[df_b['class'].isin(aux_classes)]
print(f"AUXILIARY tokens in B: {len(df_aux)}")
print(f"AUXILIARY % of B: {100*len(df_aux)/len(df_b):.1f}%")

# ============================================================
# ANALYSIS 1: Line-level co-occurrence
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 1: LINE-LEVEL CO-OCCURRENCE")
print("="*60)

# Group by folio+line to get classes per line
line_groups = df_b.groupby(['folio', 'line'])['class'].apply(set).reset_index()
line_groups.columns = ['folio', 'line', 'classes']

# Count co-occurrences
cooccur_matrix = defaultdict(lambda: defaultdict(int))
aux_line_counts = defaultdict(int)

for _, row in line_groups.iterrows():
    line_classes = row['classes']
    aux_in_line = [c for c in line_classes if c in aux_classes]

    for c in aux_in_line:
        aux_line_counts[c] += 1

    for c1, c2 in combinations(aux_in_line, 2):
        if c1 > c2:
            c1, c2 = c2, c1
        cooccur_matrix[c1][c2] += 1

# Find pairs that NEVER co-occur
never_cooccur = []
for c1, c2 in combinations(aux_classes, 2):
    if c1 > c2:
        c1, c2 = c2, c1
    if cooccur_matrix[c1][c2] == 0:
        never_cooccur.append((c1, c2))

print(f"\nTotal AUXILIARY pairs: {len(list(combinations(aux_classes, 2)))}")
print(f"Pairs that NEVER co-occur: {len(never_cooccur)}")

if never_cooccur:
    print("\nNever co-occurring pairs (first 20):")
    for c1, c2 in never_cooccur[:20]:
        count1 = aux_line_counts[c1]
        count2 = aux_line_counts[c2]
        print(f"  Class {c1} ({count1} lines) + Class {c2} ({count2} lines)")

# Find most frequently co-occurring pairs
cooccur_list = []
for c1 in cooccur_matrix:
    for c2 in cooccur_matrix[c1]:
        cooccur_list.append((c1, c2, cooccur_matrix[c1][c2]))

cooccur_list.sort(key=lambda x: -x[2])

print(f"\nMost frequently co-occurring AUXILIARY pairs:")
for c1, c2, count in cooccur_list[:15]:
    print(f"  Class {c1} + Class {c2}: {count} lines")

# ============================================================
# ANALYSIS 2: Class frequency in B
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 2: AUXILIARY CLASS FREQUENCY IN B")
print("="*60)

class_counts = df_aux['class'].value_counts().sort_index()
print("\nAUXILIARY class token counts:")
for cls in aux_classes:
    count = class_counts.get(cls, 0)
    pct = 100 * count / len(df_aux)
    print(f"  Class {cls:2d}: {count:5d} tokens ({pct:5.1f}%)")

# ============================================================
# ANALYSIS 3: Survival patterns from cosurvival data
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 3: AUXILIARY SURVIVAL UNDER AZC FILTERING")
print("="*60)

with open('phases/CLASS_COSURVIVAL_TEST/results/cosurvival_analysis.json') as f:
    cosurvival = json.load(f)

always_survive = set(cosurvival['always_survive'])
aux_always = [c for c in aux_classes if c in always_survive]
aux_sometimes = [c for c in aux_classes if c not in always_survive]

print(f"\nAUXILIARY classes that ALWAYS survive: {aux_always}")
print(f"AUXILIARY classes sometimes filtered: {len(aux_sometimes)}")

# Get survival rates for AUXILIARY classes
print("\nLoading per-class survival rates...")

# Read A record survivors to compute survival rates
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

# Get pre-computed survival rates
class_survival_rates = survivors_data['class_survival_rates']
survivors = survivors_data['records']

# Get survival rate for each AUXILIARY class
aux_survival = {}
for cls in aux_classes:
    aux_survival[cls] = class_survival_rates.get(str(cls), 0)

print("\nAUXILIARY class survival rates (sorted):")
for cls, rate in sorted(aux_survival.items(), key=lambda x: -x[1]):
    status = "ALWAYS" if cls in always_survive else ""
    print(f"  Class {cls:2d}: {rate*100:5.1f}% {status}")

# ============================================================
# ANALYSIS 4: Co-survival patterns
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 4: CO-SURVIVAL PATTERNS")
print("="*60)

# For each A record, which AUXILIARY classes survive together?
cosurvive_matrix = defaultdict(lambda: defaultdict(int))
n_records = len(survivors)

for rec in survivors:
    surviving = set(rec['surviving_classes'])
    aux_surviving = [c for c in surviving if c in aux_classes]

    for c1, c2 in combinations(aux_surviving, 2):
        if c1 > c2:
            c1, c2 = c2, c1
        cosurvive_matrix[c1][c2] += 1

# Find pairs that NEVER co-survive
never_cosurvive = []
for c1, c2 in combinations(aux_classes, 2):
    if c1 > c2:
        c1, c2 = c2, c1
    if cosurvive_matrix[c1][c2] == 0:
        never_cosurvive.append((c1, c2))

print(f"\nAUXILIARY pairs that NEVER co-survive (under any A record): {len(never_cosurvive)}")

if never_cosurvive:
    print("\nNever co-surviving pairs:")
    for c1, c2 in never_cosurvive[:20]:
        rate1 = aux_survival[c1]
        rate2 = aux_survival[c2]
        print(f"  Class {c1} ({rate1*100:.1f}%) + Class {c2} ({rate2*100:.1f}%)")

# Find most frequently co-surviving pairs
cosurvive_list = []
for c1 in cosurvive_matrix:
    for c2 in cosurvive_matrix[c1]:
        cosurvive_list.append((c1, c2, cosurvive_matrix[c1][c2]))

cosurvive_list.sort(key=lambda x: -x[2])

print(f"\nMost frequently co-surviving AUXILIARY pairs:")
for c1, c2, count in cosurvive_list[:15]:
    pct = 100 * count / n_records
    print(f"  Class {c1} + Class {c2}: {count} records ({pct:.1f}%)")

# ============================================================
# ANALYSIS 5: Conditional co-survival
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 5: CONDITIONAL CO-SURVIVAL")
print("="*60)

# For each AUXILIARY class, what % of the time does another class also survive?
print("\nGiven class X survives, probability class Y also survives:")

# Focus on the always-survive AUXILIARY classes (21, 22)
# vs the sometimes-filtered ones
for anchor in [21, 22]:
    print(f"\n  Given class {anchor} survives (100%):")
    conditional = {}
    for target in aux_classes:
        if target == anchor:
            continue
        # Count records where both survive
        both = sum(1 for rec in survivors
                   if anchor in rec['surviving_classes'] and target in rec['surviving_classes'])
        # anchor always survives, so P(target|anchor) = both/total
        conditional[target] = both / n_records

    for target, prob in sorted(conditional.items(), key=lambda x: -x[1])[:10]:
        print(f"    P(class {target:2d}) = {prob*100:5.1f}%")

# ============================================================
# ANALYSIS 6: Cluster analysis - which AUX classes form groups?
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 6: AUXILIARY CLASS CLUSTERS")
print("="*60)

# Use Jaccard similarity of survival patterns
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import numpy as np

# Build survival pattern matrix (records x classes)
n_records = len(survivors)
n_aux = len(aux_classes)
survival_matrix = np.zeros((n_records, n_aux))

for i, rec in enumerate(survivors):
    for j, cls in enumerate(aux_classes):
        if cls in rec['surviving_classes']:
            survival_matrix[i, j] = 1

# Compute Jaccard distance between classes (column-wise)
# Jaccard = 1 - (intersection / union)
def jaccard_distance(u, v):
    both = np.sum((u == 1) & (v == 1))
    either = np.sum((u == 1) | (v == 1))
    if either == 0:
        return 0
    return 1 - both / either

distances = pdist(survival_matrix.T, metric=jaccard_distance)
dist_matrix = squareform(distances)

# Hierarchical clustering
Z = linkage(distances, method='average')

# Cut at different thresholds
for threshold in [0.3, 0.5, 0.7]:
    clusters = fcluster(Z, threshold, criterion='distance')
    n_clusters = len(set(clusters))
    print(f"\nAt Jaccard distance threshold {threshold}: {n_clusters} clusters")

    cluster_members = defaultdict(list)
    for cls, cluster_id in zip(aux_classes, clusters):
        cluster_members[cluster_id].append(cls)

    for cluster_id, members in sorted(cluster_members.items()):
        if len(members) > 1:
            print(f"  Cluster {cluster_id}: {members}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total AUXILIARY classes: {len(aux_classes)}")
print(f"Always-survive (unfilterable): {aux_always}")
print(f"Sometimes-filtered: {len(aux_sometimes)}")
print(f"AUXILIARY % of B tokens: {100*len(df_aux)/len(df_b):.1f}%")
print(f"Never co-occur on same line: {len(never_cooccur)} pairs")
print(f"Never co-survive under any A record: {len(never_cosurvive)} pairs")
