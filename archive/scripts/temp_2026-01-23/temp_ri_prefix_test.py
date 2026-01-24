#!/usr/bin/env python3
"""
Quick exploration: Do RI token prefixes correlate with B token survival?

User hypothesis: RI tokens have specific prefix subsets. Do these prefixes
predict which B class members survive?
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

# Load data
DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)
token_to_class = data['token_to_class']

print("=" * 70)
print("RI PREFIX ANALYSIS")
print("=" * 70)

# Extract MIDDLE and PREFIX from token
def get_middle(token):
    if pd.isna(token) or len(str(token)) < 2:
        return None
    token = str(token)
    return token[1:-1] if len(token) > 2 else (token[1] if len(token) == 2 else None)

def get_prefix(token):
    """Extract prefix (first character(s) that form a known prefix)"""
    if pd.isna(token) or len(str(token)) < 1:
        return None
    token = str(token)
    # Known prefixes from the system
    prefixes = ['ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct', 'o', 'q', 'd', 'c', 's', 'k', 't']
    for p in sorted(prefixes, key=len, reverse=True):  # Try longest first
        if token.startswith(p):
            return p
    return token[0] if token else None

# =============================================================================
# 1. What MIDDLEs are A-exclusive (RI) vs shared (PP)?
# =============================================================================
print("\n" + "=" * 70)
print("1. MIDDLE CLASSIFICATION: RI vs PP")
print("=" * 70)

a_middles = set()
for tok in df_a['word'].dropna():
    mid = get_middle(tok)
    if mid:
        a_middles.add(mid)

b_middles = set()
for tok in df_b['word'].dropna():
    mid = get_middle(tok)
    if mid:
        b_middles.add(mid)

ri_middles = a_middles - b_middles  # A-exclusive
pp_middles = a_middles & b_middles  # Shared (pipeline-participating)

print(f"\nA MIDDLEs: {len(a_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"RI (A-exclusive): {len(ri_middles)}")
print(f"PP (shared): {len(pp_middles)}")

# =============================================================================
# 2. What prefixes do RI tokens have vs PP tokens?
# =============================================================================
print("\n" + "=" * 70)
print("2. PREFIX DISTRIBUTION: RI vs PP TOKENS")
print("=" * 70)

# Get prefix distribution for A tokens with RI MIDDLEs vs PP MIDDLEs
ri_prefixes = Counter()
pp_prefixes = Counter()

for tok in df_a['word'].dropna():
    mid = get_middle(tok)
    prefix = get_prefix(tok)
    if mid and prefix:
        if mid in ri_middles:
            ri_prefixes[prefix] += 1
        elif mid in pp_middles:
            pp_prefixes[prefix] += 1

print("\nRI token prefixes (A-exclusive MIDDLEs):")
for prefix, count in ri_prefixes.most_common():
    pct = 100 * count / sum(ri_prefixes.values())
    print(f"  {prefix}: {count} ({pct:.1f}%)")

print("\nPP token prefixes (shared MIDDLEs):")
for prefix, count in pp_prefixes.most_common():
    pct = 100 * count / sum(pp_prefixes.values())
    print(f"  {prefix}: {count} ({pct:.1f}%)")

# =============================================================================
# 3. Prefix families (grouping sister pairs)
# =============================================================================
print("\n" + "=" * 70)
print("3. PREFIX FAMILIES")
print("=" * 70)

def get_prefix_family(prefix):
    """Group prefixes into families"""
    families = {
        'CH': ['ch', 'c'],
        'SH': ['sh', 's'],
        'OK': ['ok', 'o'],
        'OT': ['ot'],
        'DA': ['da', 'd'],
        'QO': ['qo', 'q'],
        'OL': ['ol'],
        'CT': ['ct', 't'],
        'K': ['k'],
    }
    for family, members in families.items():
        if prefix in members:
            return family
    return 'OTHER'

ri_families = Counter()
pp_families = Counter()

for prefix, count in ri_prefixes.items():
    ri_families[get_prefix_family(prefix)] += count

for prefix, count in pp_prefixes.items():
    pp_families[get_prefix_family(prefix)] += count

print("\nRI token prefix families:")
for family, count in ri_families.most_common():
    pct = 100 * count / sum(ri_families.values())
    print(f"  {family}: {count} ({pct:.1f}%)")

print("\nPP token prefix families:")
for family, count in pp_families.most_common():
    pct = 100 * count / sum(pp_families.values())
    print(f"  {family}: {count} ({pct:.1f}%)")

# =============================================================================
# 4. Does RI prefix family predict B survival?
# =============================================================================
print("\n" + "=" * 70)
print("4. RI PREFIX FAMILY vs B TOKEN SURVIVAL")
print("=" * 70)

# Load survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivor_data = json.load(f)

# For each A record, categorize by dominant RI prefix family
# Then check if B survival differs

# First, build A record -> token mapping
a_record_tokens = defaultdict(list)
for _, row in df_a.iterrows():
    folio = row['folio']
    line = row['line_number']
    word = row['word']
    if pd.notna(word):
        record_id = f"{folio}_{line}"
        a_record_tokens[record_id].append(word)

# For each A record, get RI prefix composition and PP MIDDLE count
record_profiles = {}
for record_id, tokens in a_record_tokens.items():
    ri_prefix_counts = Counter()
    pp_middle_count = 0

    for tok in tokens:
        mid = get_middle(tok)
        prefix = get_prefix(tok)
        if mid:
            if mid in ri_middles:
                family = get_prefix_family(prefix)
                ri_prefix_counts[family] += 1
            elif mid in pp_middles:
                pp_middle_count += 1

    if ri_prefix_counts or pp_middle_count > 0:
        dominant_ri_family = ri_prefix_counts.most_common(1)[0][0] if ri_prefix_counts else None
        record_profiles[record_id] = {
            'ri_families': dict(ri_prefix_counts),
            'dominant_ri': dominant_ri_family,
            'pp_count': pp_middle_count,
            'total_ri': sum(ri_prefix_counts.values())
        }

print(f"\nA records with profile data: {len(record_profiles)}")

# Match with survivor data
# Survivor data uses different record IDs, need to match by content
# For now, let's look at correlation between RI composition and B class diversity

# Group A records by dominant RI family
family_to_profiles = defaultdict(list)
for record_id, profile in record_profiles.items():
    dom = profile['dominant_ri']
    if dom:
        family_to_profiles[dom].append(profile)

print("\nA records by dominant RI prefix family:")
for family in sorted(family_to_profiles.keys()):
    profiles = family_to_profiles[family]
    mean_pp = np.mean([p['pp_count'] for p in profiles])
    mean_ri = np.mean([p['total_ri'] for p in profiles])
    print(f"  {family}: {len(profiles)} records, mean PP={mean_pp:.1f}, mean RI={mean_ri:.1f}")

# =============================================================================
# 5. Specific test: CT prefix (registry reference)
# =============================================================================
print("\n" + "=" * 70)
print("5. CT PREFIX ANALYSIS (Registry Reference)")
print("=" * 70)

ct_records = [r for r, p in record_profiles.items() if 'CT' in p['ri_families']]
non_ct_records = [r for r, p in record_profiles.items() if 'CT' not in p['ri_families'] and p['total_ri'] > 0]

print(f"\nRecords with CT-prefix RI tokens: {len(ct_records)}")
print(f"Records with RI tokens but no CT: {len(non_ct_records)}")

if ct_records and non_ct_records:
    ct_pp = [record_profiles[r]['pp_count'] for r in ct_records]
    non_ct_pp = [record_profiles[r]['pp_count'] for r in non_ct_records]

    from scipy import stats
    stat, p = stats.mannwhitneyu(ct_pp, non_ct_pp, alternative='two-sided')

    print(f"\nPP count comparison:")
    print(f"  CT records: mean PP = {np.mean(ct_pp):.2f}")
    print(f"  Non-CT records: mean PP = {np.mean(non_ct_pp):.2f}")
    print(f"  Mann-Whitney p = {p:.4f}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
RI vs PP MIDDLE split:
- RI (A-exclusive): {len(ri_middles)} MIDDLEs
- PP (shared): {len(pp_middles)} MIDDLEs

RI prefix distribution:
{dict(ri_families.most_common(5))}

PP prefix distribution:
{dict(pp_families.most_common(5))}

Key question: Does RI prefix predict B behavior?
This would suggest RI encodes "type" information that affects execution.
""")
