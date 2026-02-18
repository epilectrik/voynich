#!/usr/bin/env python3
"""Test: Do Rosettes labels connect to pharma jar labels?"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer, BFolioDecoder

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# ============================================================
# 1. EXTRACT KNOWN JAR LABELS FROM PHARMA FOLIOS
# ============================================================
print("=" * 70)
print("JAR LABEL vs ROSETTES LABEL CONNECTION TEST")
print("=" * 70)

# Pharma folios with jar labels (from PHARMA_LABEL_DECODING)
PHARMA_FOLIOS = ['f88v', 'f89r1', 'f89r2', 'f89v2',
                 'f99r', 'f99v',
                 'f100r', 'f100v',
                 'f101v2', 'f102r1', 'f102r2', 'f102v1', 'f102v2']

# Get all label tokens from pharma folios (L-placement = labels)
pharma_labels = []
pharma_jar_labels = []
pharma_content_labels = []

for tok in tx.all():
    if tok.folio in PHARMA_FOLIOS and tok.placement.startswith('L'):
        pharma_labels.append(tok)

# Jar labels are the FIRST token in each label group (per PHARMA_LABEL_DECODING)
# They're unique, never repeat, and share zero tokens with content labels
# Let's get all pharma label tokens and their MIDDLEs
pharma_label_words = set(t.word for t in pharma_labels)
pharma_label_middles = set()
for t in pharma_labels:
    m = morph.extract(t.word)
    if m.middle:
        pharma_label_middles.add(m.middle)

print(f"\nPharma label tokens: {len(pharma_labels)}")
print(f"Unique pharma label words: {len(pharma_label_words)}")
print(f"Unique pharma label MIDDLEs: {len(pharma_label_middles)}")

# ============================================================
# 2. EXTRACT ROSETTES LABELS (from f85v2 label regions)
# ============================================================
label_regions = ['B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1']
ros_labels = []
for r in label_regions:
    toks = ra.get_tokens('f85v2', r)
    for t in toks:
        ros_labels.append(t)

ros_label_words = set(t.word for t in ros_labels)
ros_label_middles = set()
for t in ros_labels:
    m = morph.extract(t.word)
    if m.middle:
        ros_label_middles.add(m.middle)

print(f"\nRosettes label tokens: {len(ros_labels)}")
print(f"Unique rosettes label words: {len(ros_label_words)}")
print(f"Unique rosettes label MIDDLEs: {len(ros_label_middles)}")

# ============================================================
# 3. DIRECT OVERLAP
# ============================================================
print("\n" + "=" * 70)
print("DIRECT VOCABULARY OVERLAP")
print("=" * 70)

word_overlap = ros_label_words & pharma_label_words
mid_overlap = ros_label_middles & pharma_label_middles

# Jaccard
word_union = ros_label_words | pharma_label_words
mid_union = ros_label_middles | pharma_label_middles

word_jaccard = len(word_overlap) / len(word_union) if word_union else 0
mid_jaccard = len(mid_overlap) / len(mid_union) if mid_union else 0

print(f"\nWord-level overlap: {len(word_overlap)}/{len(word_union)} (Jaccard={word_jaccard:.3f})")
if word_overlap:
    print(f"  Shared words: {sorted(word_overlap)}")

print(f"\nMIDDLE-level overlap: {len(mid_overlap)}/{len(mid_union)} (Jaccard={mid_jaccard:.3f})")
if mid_overlap:
    print(f"  Shared MIDDLEs: {sorted(mid_overlap)}")

# ============================================================
# 4. MORPHOLOGICAL COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("MORPHOLOGICAL COMPARISON")
print("=" * 70)

# Prefix distribution comparison
pharma_prefixes = Counter()
ros_prefixes = Counter()

for t in pharma_labels:
    m = morph.extract(t.word)
    if m.prefix:
        pharma_prefixes[m.prefix] += 1

for t in ros_labels:
    m = morph.extract(t.word)
    if m.prefix:
        ros_prefixes[m.prefix] += 1

print(f"\nPrefix distributions:")
all_pres = sorted(set(list(pharma_prefixes.keys()) + list(ros_prefixes.keys())),
                  key=lambda p: pharma_prefixes.get(p, 0) + ros_prefixes.get(p, 0),
                  reverse=True)

pharma_total = sum(pharma_prefixes.values())
ros_total = sum(ros_prefixes.values())

print(f"{'Prefix':<8} {'Pharma':>8} {'Pharma%':>8} {'Rosettes':>10} {'Ros%':>8}")
print("-" * 50)
for p in all_pres[:15]:
    pc = pharma_prefixes.get(p, 0)
    rc = ros_prefixes.get(p, 0)
    pp = 100 * pc / pharma_total if pharma_total else 0
    rp = 100 * rc / ros_total if ros_total else 0
    print(f"{p:<8} {pc:>8} {pp:>7.1f}% {rc:>10} {rp:>7.1f}%")

# Mean length comparison
pharma_lens = [len(t.word) for t in pharma_labels]
ros_lens = [len(t.word) for t in ros_labels]

print(f"\nMean word length:")
print(f"  Pharma labels: {sum(pharma_lens)/len(pharma_lens):.1f} chars")
print(f"  Rosettes labels: {sum(ros_lens)/len(ros_lens):.1f} chars")

# ============================================================
# 5. JAR-SPECIFIC ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("JAR-SPECIFIC VOCABULARY TEST")
print("=" * 70)

# Load jar labels specifically from the JSON files
jar_words = set()
jar_middles = set()

for pharma_folio in PHARMA_FOLIOS:
    jar_path = ROOT / f'phases/PHARMA_LABEL_DECODING/{pharma_folio}_jar_root_mapping.json'
    if jar_path.exists():
        with open(jar_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'jar_label' in data:
            jar_words.add(data['jar_label'])
            m = morph.extract(data['jar_label'])
            if m.middle:
                jar_middles.add(m.middle)
        if 'jar_labels' in data:
            for jl in data['jar_labels']:
                jar_words.add(jl)
                m = morph.extract(jl)
                if m.middle:
                    jar_middles.add(m.middle)

    # Also try leaf mapping files
    jar_path2 = ROOT / f'phases/PHARMA_LABEL_DECODING/{pharma_folio}_jar_leaf_mapping.json'
    if jar_path2.exists():
        with open(jar_path2, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'jar_label' in data:
            jar_words.add(data['jar_label'])
            m = morph.extract(data['jar_label'])
            if m.middle:
                jar_middles.add(m.middle)

print(f"Known jar labels: {len(jar_words)}")
print(f"Jar label words: {sorted(jar_words)}")
print(f"Jar label MIDDLEs: {sorted(jar_middles)}")

# Cross with rosettes
jar_ros_word_overlap = jar_words & ros_label_words
jar_ros_mid_overlap = jar_middles & ros_label_middles

print(f"\nJar-Rosettes word overlap: {len(jar_ros_word_overlap)}")
if jar_ros_word_overlap:
    print(f"  Shared: {sorted(jar_ros_word_overlap)}")

print(f"Jar-Rosettes MIDDLE overlap: {len(jar_ros_mid_overlap)}")
if jar_ros_mid_overlap:
    print(f"  Shared MIDDLEs: {sorted(jar_ros_mid_overlap)}")
    for mid in sorted(jar_ros_mid_overlap):
        # Show the jar labels and rosettes labels using this MIDDLE
        jar_with = [w for w in jar_words if morph.extract(w).middle == mid]
        ros_with = [t.word for t in ros_labels if morph.extract(t.word).middle == mid]
        print(f"    {mid}: jars={jar_with}, rosettes={ros_with}")

# ============================================================
# 6. PP BASE COMPARISON (the key link per C928)
# ============================================================
print("\n" + "=" * 70)
print("PP BASE COMPARISON (C928 Pipeline Test)")
print("=" * 70)

# Per C524, jar labels are compressed configurations with 5-8 PP atoms
# Per C928, jar PP bases appear in B at 2.1x in AX_FINAL positions
# Question: Do rosettes labels share the same PP base vocabulary?

# Extract PP atoms from both sets
# PP bases are sub-components of MIDDLEs
# For simplicity, check if the same MIDDLEs appear as substrings

# Get all core MIDDLEs (short, high-frequency)
core_middles = set()
for tok in tx.currier_b():
    m = morph.extract(tok.word)
    if m.middle and len(m.middle) <= 3:
        core_middles.add(m.middle)

# Count how many core MIDDLEs are embedded in jar labels vs rosettes labels
jar_embedded = Counter()
for w in jar_words:
    m = morph.extract(w)
    if m.middle:
        for cm in core_middles:
            if cm in m.middle and cm != m.middle:
                jar_embedded[cm] += 1

ros_embedded = Counter()
for t in ros_labels:
    m = morph.extract(t.word)
    if m.middle:
        for cm in core_middles:
            if cm in m.middle and cm != m.middle:
                ros_embedded[cm] += 1

# Shared embedded atoms
shared_atoms = set(jar_embedded.keys()) & set(ros_embedded.keys())
print(f"\nCore MIDDLEs embedded in jar labels: {len(jar_embedded)}")
print(f"Core MIDDLEs embedded in rosettes labels: {len(ros_embedded)}")
print(f"Shared embedded atoms: {len(shared_atoms)}")
if shared_atoms:
    print(f"  {sorted(shared_atoms)}")

# ============================================================
# 7. STRUCTURAL ROLE COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("STRUCTURAL ROLE COMPARISON")
print("=" * 70)

# Jar labels per C524: compressed configuration signatures, NOT parseable
# Rosettes labels: A-like single-token entries
# Question: Are they the same TYPE of label or different?

print("\nJar label properties (per C523-C524):")
print("  - Mean length: 7.1 chars (longer than A baseline)")
print("  - PP atoms per MIDDLE: 5-8 (densely packed)")
print("  - In vocabulary: 12.5% (mostly NOT in text)")
print("  - Repeat rate: 0% (each unique to one folio)")
print("  - Function: Physical container identifiers")

ros_in_text = 0
ros_total_check = 0
for t in ros_labels:
    ros_total_check += 1
    # Check if appears in B body text
    found = False
    for bt in tx.currier_b():
        if bt.folio not in ra.ROSETTES_FOLIOS and bt.word == t.word:
            found = True
            break
    if found:
        ros_in_text += 1

ros_mean_len = sum(len(t.word) for t in ros_labels) / len(ros_labels)
ros_unique_rate = len(ros_label_words) / len(ros_labels)

print(f"\nRosettes label properties:")
print(f"  - Mean length: {ros_mean_len:.1f} chars")
print(f"  - Unique words: {len(ros_label_words)}/{len(ros_labels)} ({100*ros_unique_rate:.0f}%)")
print(f"  - In B body text: {ros_in_text}/{ros_total_check} ({100*ros_in_text/ros_total_check:.0f}%)")

# Repeat rate for rosettes labels
from collections import Counter as C2
ros_word_counts = C2(t.word for t in ros_labels)
repeats = sum(1 for w, c in ros_word_counts.items() if c > 1)
print(f"  - Repeated words: {repeats}/{len(ros_label_words)} ({100*repeats/len(ros_label_words):.0f}%)")
if repeats:
    for w, c in ros_word_counts.most_common():
        if c > 1:
            print(f"      {w}: {c}x")

# ============================================================
# 8. SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS: Are Rosettes labels related to jar labels?")
print("=" * 70)

# Compare the two label systems
print(f"""
Comparison Matrix:
                        JAR LABELS          ROSETTES LABELS
  Count:                16                  87 (49 unique MIDDLEs)
  Mean length:          7.1 chars           {ros_mean_len:.1f} chars
  In B text:            12.5%               {100*ros_in_text/ros_total_check:.0f}%
  Cross-folio repeat:   0% (each unique)    {100*repeats/len(ros_label_words):.0f}%
  Prefix pattern:       ok- and da- dominant ok- and ot- dominant
  Vocabulary overlap:   (see above)
  Function (C523/524):  Container IDs       (to be determined)
  Compression:          High (5-8 atoms)    (to be determined)
""")
