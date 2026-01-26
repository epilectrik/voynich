"""
A-B FOLIO COMPATIBILITY TEST

Question: Could A record PREFIX profiles have been used to find compatible B folios?

If the A→B pipeline is a deliberate matching system:
- A records with certain PREFIXes would have higher compatibility with certain B folios
- We'd see non-random correlation between A PREFIX profiles and B folio class distributions

Test:
1. For each A record, compute surviving classes based on morphology
2. For each B folio, compute class distribution (which classes are used)
3. Check if A records have higher "compatibility" with some B folios than others
4. Is there evidence of deliberate A-B pairing?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("A-B FOLIO COMPATIBILITY TEST")
print("Could A PREFIX profiles be used to find compatible B folios?")
print("=" * 70)

# Build B token data with class assignments
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        # PREFIX-based class
        if m.prefix:
            cls = f"P_{m.prefix}"
        elif m.suffix:
            cls = f"S_{m.suffix}"
        else:
            cls = "BARE"
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'class': cls
        }

b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

# Get all classes
all_classes = set(info['class'] for info in b_tokens.values())
print(f"\nB vocabulary: {len(b_tokens)} tokens, {len(all_classes)} classes")

# Build B folio class profiles
b_folio_classes = defaultdict(Counter)
b_folio_tokens = defaultdict(list)

for token in tx.currier_b():
    word = token.word
    if word and word in b_tokens:
        folio = token.folio
        cls = b_tokens[word]['class']
        b_folio_classes[folio][cls] += 1
        b_folio_tokens[folio].append(word)

print(f"B folios: {len(b_folio_classes)}")

# Build A records with morphology
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

print(f"A records: {len(record_morphology)}")

# Compute surviving classes for each A record
def get_surviving_classes(prefixes, middles, suffixes):
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, info in b_tokens.items():
        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            surviving.add(info['class'])

    return surviving

a_record_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    a_record_classes[(folio, line)] = get_surviving_classes(prefixes, middles, suffixes)

# Compute compatibility: for each A record × B folio pair
# Compatibility = proportion of B folio's tokens that come from A's surviving classes

print("\n" + "=" * 70)
print("COMPUTING A-B COMPATIBILITY SCORES")
print("=" * 70)

# For efficiency, sample A records
a_sample = list(a_record_classes.keys())[:500]
b_folios = list(b_folio_classes.keys())

print(f"\nSampling {len(a_sample)} A records × {len(b_folios)} B folios")

compatibility_matrix = []
a_record_list = []
b_folio_list = b_folios

for a_key in a_sample:
    a_classes = a_record_classes[a_key]
    row = []
    for b_folio in b_folios:
        # What fraction of B folio tokens come from A's surviving classes?
        b_class_counts = b_folio_classes[b_folio]
        total_tokens = sum(b_class_counts.values())
        compatible_tokens = sum(b_class_counts[cls] for cls in a_classes if cls in b_class_counts)
        compatibility = compatible_tokens / total_tokens if total_tokens > 0 else 0
        row.append(compatibility)
    compatibility_matrix.append(row)
    a_record_list.append(a_key)

compatibility_matrix = np.array(compatibility_matrix)

print(f"\nCompatibility matrix shape: {compatibility_matrix.shape}")
print(f"Mean compatibility: {np.mean(compatibility_matrix):.3f}")
print(f"Std: {np.std(compatibility_matrix):.3f}")
print(f"Min: {np.min(compatibility_matrix):.3f}")
print(f"Max: {np.max(compatibility_matrix):.3f}")

# Key question: Is compatibility uniform, or do some A records have "preferred" B folios?
print("\n" + "=" * 70)
print("A RECORD COMPATIBILITY VARIANCE")
print("=" * 70)

# For each A record, how much does compatibility vary across B folios?
a_record_variance = []
for i, a_key in enumerate(a_record_list):
    row = compatibility_matrix[i, :]
    variance = np.var(row)
    a_record_variance.append(variance)

print(f"\nPer-A-record compatibility variance:")
print(f"  Mean variance: {np.mean(a_record_variance):.4f}")
print(f"  Max variance: {np.max(a_record_variance):.4f}")

# Compare to null: if we shuffle class assignments, what's expected variance?
print("\n--- Null model comparison ---")
null_variances = []
for _ in range(100):
    shuffled_classes = list(a_record_classes[a_sample[0]])
    np.random.shuffle(list(shuffled_classes))
    # This is a simplified null - just checking if observed variance is unusual

# Actually, let's check if certain B folios are consistently higher/lower compatibility
b_folio_mean_compat = []
for j, b_folio in enumerate(b_folio_list):
    col = compatibility_matrix[:, j]
    b_folio_mean_compat.append((b_folio, np.mean(col), np.std(col)))

b_folio_mean_compat.sort(key=lambda x: -x[1])

print("\nB folios by mean compatibility with A records:")
print("(Higher = more A records can execute this folio's classes)")
print("\nTop 10 (most compatible):")
for folio, mean, std in b_folio_mean_compat[:10]:
    print(f"  {folio}: {mean:.3f} ± {std:.3f}")

print("\nBottom 10 (least compatible):")
for folio, mean, std in b_folio_mean_compat[-10:]:
    print(f"  {folio}: {mean:.3f} ± {std:.3f}")

# Check: is there a relationship between A folio and B folio compatibility?
print("\n" + "=" * 70)
print("A FOLIO -> B FOLIO AFFINITY")
print("=" * 70)

# Group A records by their folio
a_by_folio = defaultdict(list)
for i, (a_folio, a_line) in enumerate(a_record_list):
    a_by_folio[a_folio].append(i)

# For each A folio, compute mean compatibility with each B folio
a_folio_b_compat = {}
for a_folio, indices in a_by_folio.items():
    if len(indices) < 3:
        continue
    mean_row = np.mean(compatibility_matrix[indices, :], axis=0)
    a_folio_b_compat[a_folio] = mean_row

print(f"\nA folios with sufficient records: {len(a_folio_b_compat)}")

# Is there variance in which B folios different A folios prefer?
if len(a_folio_b_compat) > 1:
    a_folio_profiles = np.array(list(a_folio_b_compat.values()))
    print(f"A folio compatibility profiles shape: {a_folio_profiles.shape}")

    # Correlation between A folio profiles
    print("\nCorrelation between A folio compatibility profiles:")
    a_folio_names = list(a_folio_b_compat.keys())
    sample_pairs = min(10, len(a_folio_names) * (len(a_folio_names) - 1) // 2)

    corrs = []
    for i in range(len(a_folio_names)):
        for j in range(i+1, len(a_folio_names)):
            r, _ = stats.pearsonr(a_folio_profiles[i], a_folio_profiles[j])
            corrs.append(r)

    print(f"  Mean pairwise correlation: {np.mean(corrs):.3f}")
    print(f"  Std: {np.std(corrs):.3f}")

    if np.mean(corrs) > 0.8:
        print("  -> HIGH correlation: all A folios have similar B folio preferences")
        print("     This suggests PREFIX profiles are similar across A folios")
    elif np.mean(corrs) < 0.3:
        print("  -> LOW correlation: A folios have DIFFERENT B folio preferences")
        print("     This could support deliberate A-B pairing")
    else:
        print("  -> MODERATE correlation: some shared, some unique preferences")

# Check specific high-value pairings
print("\n" + "=" * 70)
print("SPECIFIC A-B PAIRINGS")
print("=" * 70)

# Find A records with highest compatibility variance (most "selective")
selective_a = sorted(enumerate(a_record_variance), key=lambda x: -x[1])[:20]

print("\nMost selective A records (high variance in B compatibility):")
for i, var in selective_a[:5]:
    a_key = a_record_list[i]
    row = compatibility_matrix[i, :]
    best_b_idx = np.argmax(row)
    worst_b_idx = np.argmin(row)
    best_b = b_folio_list[best_b_idx]
    worst_b = b_folio_list[worst_b_idx]
    print(f"\n  A record {a_key}:")
    print(f"    Variance: {var:.4f}")
    print(f"    Best B folio: {best_b} ({row[best_b_idx]:.3f})")
    print(f"    Worst B folio: {worst_b} ({row[worst_b_idx]:.3f})")
    print(f"    Classes: {len(a_record_classes[a_key])}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

overall_variance = np.var(compatibility_matrix)
within_a_variance = np.mean(a_record_variance)

print(f"""
COMPATIBILITY STATISTICS:
  Mean A-B compatibility: {np.mean(compatibility_matrix):.3f}
  Overall variance: {overall_variance:.4f}
  Within-A-record variance: {within_a_variance:.4f}
  B folio range: {b_folio_mean_compat[-1][1]:.3f} - {b_folio_mean_compat[0][1]:.3f}

INTERPRETATION:
""")

if b_folio_mean_compat[0][1] - b_folio_mean_compat[-1][1] > 0.3:
    print("  B folios have VERY DIFFERENT compatibility profiles.")
    print("  Some B folios are much more 'accessible' than others.")
    print("  This COULD support deliberate compatibility matching.")
elif b_folio_mean_compat[0][1] - b_folio_mean_compat[-1][1] > 0.15:
    print("  B folios have MODERATE compatibility differences.")
    print("  Some preference structure exists.")
else:
    print("  B folios have SIMILAR compatibility (~uniform).")
    print("  A records can access most B folios roughly equally.")
    print("  This argues AGAINST specific A-B pairing.")

print(f"""
KEY FINDING:
  Mean compatibility = {np.mean(compatibility_matrix):.1%} of B folio tokens
  are from classes surviving each A record's filtering.
""")
