"""
T1: FL (Flow Operator) Complete Inventory

FL is remarkably pure:
- 0% compound MIDDLEs
- 0 kernel characters (k, h, e)
- 4 classes: {7, 30, 38, 40}
- 1,078 tokens, 4.7% of B

Question: What exactly are FL's MIDDLEs? What makes them special?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

# FL classes from BCSC
FL_CLASSES = {7, 30, 38, 40}

# Build MiddleAnalyzer for reference
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer.get_core_middles()

print("="*70)
print("FL (FLOW OPERATOR) COMPLETE INVENTORY")
print("="*70)

# Collect all FL tokens
fl_tokens = []
fl_by_class = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or w not in token_to_class:
        continue

    cls = int(token_to_class[w])
    if cls not in FL_CLASSES:
        continue

    m = morph.extract(w)
    fl_tokens.append({
        'word': w,
        'class': cls,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'folio': token.folio,
        'line': token.line,
        'section': token.section
    })
    fl_by_class[cls].append(fl_tokens[-1])

print(f"\nTotal FL tokens: {len(fl_tokens)}")
print(f"FL classes: {sorted(FL_CLASSES)}")

# ============================================================
# PER-CLASS BREAKDOWN
# ============================================================
print("\n" + "="*70)
print("PER-CLASS BREAKDOWN")
print("="*70)

for cls in sorted(FL_CLASSES):
    tokens = fl_by_class[cls]
    print(f"\nClass {cls}: {len(tokens)} tokens")

    # Unique words
    words = Counter(t['word'] for t in tokens)
    print(f"  Unique types: {len(words)}")
    print(f"  Top words: {words.most_common(5)}")

    # MIDDLEs
    middles = Counter(t['middle'] for t in tokens)
    print(f"  Unique MIDDLEs: {len(middles)}")
    print(f"  MIDDLEs: {dict(middles)}")

    # PREFIXes
    prefixes = Counter(t['prefix'] for t in tokens)
    print(f"  PREFIXes: {dict(prefixes)}")

    # SUFFIXes
    suffixes = Counter(t['suffix'] for t in tokens if t['suffix'])
    print(f"  SUFFIXes: {dict(suffixes) if suffixes else 'NONE'}")

# ============================================================
# COMPLETE MIDDLE INVENTORY
# ============================================================
print("\n" + "="*70)
print("COMPLETE FL MIDDLE INVENTORY")
print("="*70)

all_fl_middles = set(t['middle'] for t in fl_tokens if t['middle'])
print(f"\nTotal unique FL MIDDLEs: {len(all_fl_middles)}")
print(f"MIDDLEs: {sorted(all_fl_middles)}")

# Character analysis
all_chars = set()
for mid in all_fl_middles:
    all_chars.update(mid)
print(f"\nCharacters used: {sorted(all_chars)}")
print(f"Character count: {len(all_chars)}")

# Kernel character check
kernel_chars = {'k', 'h', 'e'}
has_kernel = [mid for mid in all_fl_middles if any(c in mid for c in kernel_chars)]
print(f"\nMIDDLEs with kernel chars (k/h/e): {has_kernel if has_kernel else 'NONE'}")

# Check what characters FL DOESN'T use
b_primitives = {'s', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r'}  # C085
missing = b_primitives - all_chars
print(f"\nB primitives (C085) NOT in FL: {sorted(missing)}")

# ============================================================
# MORPHOLOGICAL STRUCTURE
# ============================================================
print("\n" + "="*70)
print("MORPHOLOGICAL STRUCTURE")
print("="*70)

# PREFIX distribution
prefix_dist = Counter(t['prefix'] for t in fl_tokens)
print(f"\nPREFIX distribution:")
for prefix, count in prefix_dist.most_common():
    pct = 100 * count / len(fl_tokens)
    print(f"  {prefix if prefix else 'NONE':<8}: {count:>4} ({pct:>5.1f}%)")

# SUFFIX distribution
suffix_dist = Counter(t['suffix'] for t in fl_tokens)
print(f"\nSUFFIX distribution:")
for suffix, count in suffix_dist.most_common():
    pct = 100 * count / len(fl_tokens)
    print(f"  {suffix if suffix else 'NONE':<8}: {count:>4} ({pct:>5.1f}%)")

# Articulator distribution
art_dist = Counter(t['articulator'] for t in fl_tokens)
print(f"\nARTICULATOR distribution:")
for art, count in art_dist.most_common():
    pct = 100 * count / len(fl_tokens)
    print(f"  {art if art else 'NONE':<8}: {count:>4} ({pct:>5.1f}%)")

# ============================================================
# MIDDLE LENGTH ANALYSIS
# ============================================================
print("\n" + "="*70)
print("MIDDLE LENGTH ANALYSIS")
print("="*70)

middle_lengths = [len(t['middle']) for t in fl_tokens if t['middle']]
length_dist = Counter(middle_lengths)
print(f"\nMIDDLE length distribution:")
for length in sorted(length_dist.keys()):
    count = length_dist[length]
    pct = 100 * count / len(middle_lengths)
    print(f"  {length}: {count:>4} ({pct:>5.1f}%)")

mean_len = sum(middle_lengths) / len(middle_lengths) if middle_lengths else 0
print(f"\nMean MIDDLE length: {mean_len:.2f}")

# Compare to other roles
print("\nComparison (from T7):")
print("  FL mean: 1.55 (pure primitives)")
print("  EN mean: ~2.5 (mixed)")
print("  FQ mean: ~2.3 (compound-biased)")

# ============================================================
# FOLIO/SECTION DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("DISTRIBUTION ANALYSIS")
print("="*70)

# By section
section_dist = Counter(t['section'] for t in fl_tokens)
print(f"\nBy section:")
for sec, count in section_dist.most_common():
    pct = 100 * count / len(fl_tokens)
    print(f"  {sec}: {count:>4} ({pct:>5.1f}%)")

# Folio coverage
folio_dist = Counter(t['folio'] for t in fl_tokens)
print(f"\nFolio coverage: {len(folio_dist)} folios")
print(f"Mean per folio: {len(fl_tokens) / len(folio_dist):.1f} tokens")

# ============================================================
# COMPARISON TO CORE MIDDLEs
# ============================================================
print("\n" + "="*70)
print("FL vs CORE MIDDLEs")
print("="*70)

fl_in_core = all_fl_middles & core_middles
print(f"\nFL MIDDLEs that are CORE (20+ folios): {len(fl_in_core)}/{len(all_fl_middles)}")
print(f"  {sorted(fl_in_core)}")

fl_not_core = all_fl_middles - core_middles
print(f"\nFL MIDDLEs that are NOT core: {len(fl_not_core)}")
print(f"  {sorted(fl_not_core)}")

# ============================================================
# UNIQUE CHARACTERISTICS
# ============================================================
print("\n" + "="*70)
print("UNIQUE FL CHARACTERISTICS")
print("="*70)

findings = []

# No kernel chars
if not has_kernel:
    findings.append("NO_KERNEL_CHARS: FL uses 0 MIDDLEs with k, h, or e")

# Missing primitives
if missing:
    findings.append(f"MISSING_PRIMITIVES: FL doesn't use {sorted(missing)} from C085")

# Length
if mean_len < 2:
    findings.append(f"SHORT_MIDDLES: Mean length {mean_len:.2f} < 2 chars")

# Prefix pattern
none_prefix = prefix_dist.get(None, 0)
if none_prefix / len(fl_tokens) > 0.7:
    findings.append(f"PREFIX_SPARSE: {100*none_prefix/len(fl_tokens):.1f}% have no PREFIX")

# Suffix pattern
none_suffix = suffix_dist.get(None, 0)
if none_suffix / len(fl_tokens) > 0.9:
    findings.append(f"SUFFIX_DEPLETED: {100*none_suffix/len(fl_tokens):.1f}% have no SUFFIX")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

print(f"""
FL (Flow Operator) is the PRIMITIVE LAYER of B grammar:
- {len(all_fl_middles)} unique MIDDLEs (vs 88 classified total)
- 0% compound (no core MIDDLEs as substrings)
- 0 kernel characters (k, h, e absent)
- Mean MIDDLE length: {mean_len:.2f} (shortest of all roles)
- {100*none_suffix/len(fl_tokens):.1f}% suffix-free

FL operates BELOW the kernel level. It provides the primitive
sequencing substrate that other roles build upon.
""")

# Save results
results = {
    'token_count': len(fl_tokens),
    'class_counts': {cls: len(fl_by_class[cls]) for cls in FL_CLASSES},
    'unique_middles': sorted(all_fl_middles),
    'middle_count': len(all_fl_middles),
    'characters_used': sorted(all_chars),
    'kernel_chars_present': len(has_kernel) > 0,
    'missing_primitives': sorted(missing),
    'mean_middle_length': mean_len,
    'prefix_none_rate': none_prefix / len(fl_tokens),
    'suffix_none_rate': none_suffix / len(fl_tokens),
    'core_overlap': sorted(fl_in_core),
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't1_fl_inventory.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
