#!/usr/bin/env python3
"""
Are RI-D and RI-B functionally different, or just different complexity levels?

Hypothesis: RI-B (short repeaters) repeat because fewer combinations exist
at that length, not because they serve a different function.

Test:
1. Segment count distribution for RI-D vs RI-B
2. Is repeat frequency predicted by MIDDLE length?
3. Is there a smooth complexity → frequency relationship?
"""

import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None

# Load data
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

# Get RI MIDDLEs
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
ri_counts = ri_tokens['middle'].value_counts()

# Classify all RI by frequency
ri_middles = list(ri_counts.index)
ri_freq = {m: c for m, c in ri_counts.items()}

print("="*70)
print("RI COMPLEXITY vs FREQUENCY ANALYSIS")
print("="*70)

# 1. Length vs Frequency
print(f"\n--- LENGTH vs FREQUENCY ---")

length_freq_data = [(len(m), ri_freq[m]) for m in ri_middles]
lengths = [x[0] for x in length_freq_data]
freqs = [x[1] for x in length_freq_data]

# Correlation
corr, p_val = stats.spearmanr(lengths, freqs)
print(f"\nSpearman correlation (length vs frequency): rho={corr:.3f}, p={p_val:.2e}")

# Mean frequency by length
print(f"\nMean frequency by MIDDLE length:")
length_to_freq = defaultdict(list)
for m in ri_middles:
    length_to_freq[len(m)].append(ri_freq[m])

for l in sorted(length_to_freq.keys()):
    freqs_at_l = length_to_freq[l]
    mean_f = np.mean(freqs_at_l)
    n_types = len(freqs_at_l)
    n_singletons = sum(1 for f in freqs_at_l if f == 1)
    pct_singleton = 100 * n_singletons / n_types
    print(f"  {l} chars: {n_types} types, mean freq={mean_f:.2f}, {pct_singleton:.0f}% singleton")

# 2. What makes something repeat?
print(f"\n" + "="*70)
print("WHAT MAKES AN RI MIDDLE REPEAT?")
print("="*70)

singletons = [m for m in ri_middles if ri_freq[m] == 1]
repeaters = [m for m in ri_middles if ri_freq[m] > 1]

print(f"\nSingletons: {len(singletons)}")
print(f"Repeaters: {len(repeaters)}")

# Length comparison
sing_lengths = [len(m) for m in singletons]
rep_lengths = [len(m) for m in repeaters]

print(f"\nLength distribution:")
print(f"  Singletons: mean={np.mean(sing_lengths):.2f}, median={np.median(sing_lengths):.0f}")
print(f"  Repeaters:  mean={np.mean(rep_lengths):.2f}, median={np.median(rep_lengths):.0f}")

t_stat, t_p = stats.ttest_ind(sing_lengths, rep_lengths)
print(f"  t-test: t={t_stat:.2f}, p={t_p:.2e}")

# 3. Is the singleton/repeater split just a length threshold?
print(f"\n" + "="*70)
print("IS SINGLETON vs REPEATER JUST A LENGTH THRESHOLD?")
print("="*70)

print(f"\nSingleton rate by length:")
for l in sorted(length_to_freq.keys()):
    freqs_at_l = length_to_freq[l]
    n_types = len(freqs_at_l)
    n_sing = sum(1 for f in freqs_at_l if f == 1)
    if n_types >= 5:  # Only show if enough data
        print(f"  {l} chars: {n_sing}/{n_types} singleton ({100*n_sing/n_types:.0f}%)")

# 4. Position analysis - do repeaters and singletons differ in WHERE they appear?
print(f"\n" + "="*70)
print("POSITIONAL DIFFERENCES")
print("="*70)

# Line-initial rate
df_a['is_line_first'] = df_a.groupby(['folio', 'line_number']).cumcount() == 0

singleton_set = set(singletons)
repeater_set = set(repeaters)

sing_tokens = df_a[df_a['middle'].isin(singleton_set)]
rep_tokens = df_a[df_a['middle'].isin(repeater_set)]

sing_line_first = sing_tokens['is_line_first'].mean()
rep_line_first = rep_tokens['is_line_first'].mean()

print(f"\nLine-initial rate:")
print(f"  Singletons: {100*sing_line_first:.1f}%")
print(f"  Repeaters:  {100*rep_line_first:.1f}%")

# 5. Do short singletons exist? If so, the distinction might be functional
print(f"\n" + "="*70)
print("SHORT SINGLETONS vs SHORT REPEATERS")
print("="*70)

short_singletons = [m for m in singletons if len(m) <= 3]
short_repeaters = [m for m in repeaters if len(m) <= 3]

print(f"\nMIDDLEs with length <= 3:")
print(f"  Singletons: {len(short_singletons)}")
print(f"  Repeaters: {len(short_repeaters)}")

if short_singletons:
    print(f"\nExamples of SHORT singletons (unique despite being short):")
    for m in short_singletons[:20]:
        print(f"  '{m}'")

# 6. Frequency distribution for short MIDDLEs
print(f"\n" + "="*70)
print("FREQUENCY DISTRIBUTION FOR SHORT MIDDLES (len <= 3)")
print("="*70)

short_middles = [m for m in ri_middles if len(m) <= 3]
short_freqs = [ri_freq[m] for m in short_middles]

print(f"\nShort MIDDLEs: {len(short_middles)}")
freq_dist = Counter(short_freqs)
print(f"Frequency distribution:")
for f in sorted(freq_dist.keys())[:15]:
    print(f"  freq={f}: {freq_dist[f]} MIDDLEs")

# 7. Are there "RI-B style" patterns among longer MIDDLEs?
print(f"\n" + "="*70)
print("HIGH-FREQUENCY MIDDLES BY LENGTH")
print("="*70)

print(f"\nMIDDLEs that repeat 5+ times, by length:")
high_freq = [(m, ri_freq[m]) for m in ri_middles if ri_freq[m] >= 5]
high_freq.sort(key=lambda x: -x[1])

for m, f in high_freq[:25]:
    print(f"  '{m}' (len={len(m)}): {f} times")

# Summary
print(f"\n" + "="*70)
print("SUMMARY")
print("="*70)

if corr < -0.3 and t_p < 0.001:
    print(f"""
LENGTH STRONGLY PREDICTS FREQUENCY.

Correlation: rho={corr:.3f}
Mean length: Singletons={np.mean(sing_lengths):.1f}, Repeaters={np.mean(rep_lengths):.1f}

The "RI-D vs RI-B" distinction may just be a LENGTH/COMPLEXITY effect:
- Short MIDDLEs (1-2 sub-components) → few combinations → repeats
- Long MIDDLEs (2-4 sub-components) → many combinations → unique

This would mean ONE RI population with a complexity gradient,
not TWO functionally distinct populations.
""")
elif len(short_singletons) > 50:
    print(f"""
SHORT SINGLETONS EXIST - suggesting functional distinction.

{len(short_singletons)} MIDDLEs are both SHORT (<=3 chars) and UNIQUE.
If uniqueness were purely combinatorial, short MIDDLEs should repeat.

This suggests RI-D vs RI-B may have functional differences beyond length.
""")
else:
    print(f"""
MIXED EVIDENCE.

Correlation (length vs freq): rho={corr:.3f}
Short singletons: {len(short_singletons)}
Short repeaters: {len(short_repeaters)}

Need more analysis to determine if RI-D/RI-B are functionally distinct
or just complexity variants.
""")
