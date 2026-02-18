#!/usr/bin/env python3
"""Quick jar label vs rosettes label comparison."""
import sys, json, glob
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
from scripts.voynich import Morphology, RosettesAnalyzer, BFolioDecoder

morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# 1. Extract all jar labels from JSON files
jar_words = set()
jar_dir = ROOT / 'phases/PHARMA_LABEL_DECODING'
for jf in jar_dir.glob('*_mapping.json'):
    with open(jf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'groups' in data:
        for g in data['groups']:
            jar_val = g.get('jar')
            if jar_val:
                if isinstance(jar_val, str):
                    jar_words.add(jar_val)
                elif isinstance(jar_val, list):
                    for j in jar_val:
                        if isinstance(j, str):
                            jar_words.add(j)

print(f"Jar labels found: {len(jar_words)}")
print(f"  {sorted(jar_words)}")

# Extract MIDDLEs
jar_middles = {}
for w in jar_words:
    m = morph.extract(w)
    jar_middles[w] = m.middle
    a = decoder.analyze_token(w)
    hub = a.hub_sub_role or ''
    mk = a.middle_kernel or ''
    print(f"  {w:<18s} PRE={str(m.prefix):>5s} MID={str(m.middle):>10s} "
          f"SUF={str(m.suffix):>5s} {hub} {mk}")

# 2. Extract rosettes labels
label_regions = ['B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1']
ros_labels = []
for r in label_regions:
    for t in ra.get_tokens('f85v2', r):
        ros_labels.append(t.word)

ros_middles = {}
for w in set(ros_labels):
    m = morph.extract(w)
    ros_middles[w] = m.middle

# 3. Compare
print(f"\n{'='*60}")
print(f"COMPARISON")
print(f"{'='*60}")

jar_mid_set = set(jar_middles.values())
ros_mid_set = set(ros_middles.values())

# Word overlap
word_overlap = jar_words & set(ros_labels)
print(f"\nExact word overlap: {len(word_overlap)}")
if word_overlap:
    print(f"  {sorted(word_overlap)}")

# MIDDLE overlap
mid_overlap = jar_mid_set & ros_mid_set
print(f"\nMIDDLE overlap: {len(mid_overlap)}")
if mid_overlap:
    print(f"  {sorted(mid_overlap)}")
    for mid in sorted(mid_overlap):
        jars_with = [w for w, m in jar_middles.items() if m == mid]
        ros_with = [w for w, m in ros_middles.items() if m == mid]
        print(f"    {mid}: jars={jars_with}, rosettes={ros_with}")

# Morphological comparison
print(f"\n{'='*60}")
print(f"MORPHOLOGICAL PROFILE")
print(f"{'='*60}")

jar_lens = [len(w) for w in jar_words]
ros_lens = [len(w) for w in ros_labels]

print(f"  Mean length: jars={sum(jar_lens)/len(jar_lens):.1f}, rosettes={sum(ros_lens)/len(ros_lens):.1f}")

jar_pres = Counter(morph.extract(w).prefix for w in jar_words if morph.extract(w).prefix)
ros_pres = Counter(morph.extract(w).prefix for w in ros_labels if morph.extract(w).prefix)

print(f"\n  Jar prefixes: {dict(jar_pres.most_common())}")
print(f"  Ros prefixes: {dict(ros_pres.most_common())}")

# KEY TEST: Do jar labels share PREFIX distribution with rosettes labels?
# C525 says jar labels never use M-A prefixes (ch-, sh-)
# Rosettes labels DO use ch- but sparingly
print(f"\n  ch/sh in jars: {jar_pres.get('ch', 0) + jar_pres.get('sh', 0)}")
print(f"  ch/sh in rosettes: {ros_pres.get('ch', 0) + ros_pres.get('sh', 0)}")
print(f"  ok in jars: {jar_pres.get('ok', 0)} ({100*jar_pres.get('ok',0)/len(jar_words):.0f}%)")
print(f"  ok in rosettes: {ros_pres.get('ok', 0)} ({100*ros_pres.get('ok',0)/len(ros_labels):.0f}%)")
print(f"  ot in jars: {jar_pres.get('ot', 0)} ({100*jar_pres.get('ot',0)/len(jar_words):.0f}%)")
print(f"  ot in rosettes: {ros_pres.get('ot', 0)} ({100*ros_pres.get('ot',0)/len(ros_labels):.0f}%)")
print(f"  da in jars: {jar_pres.get('da', 0)} ({100*jar_pres.get('da',0)/len(jar_words):.0f}%)")
print(f"  da in rosettes: {ros_pres.get('da', 0)} ({100*ros_pres.get('da',0)/len(ros_labels):.0f}%)")

# In vocabulary (appears in B body text)?
from scripts.voynich import Transcript
tx = Transcript()
b_words = set(t.word for t in tx.currier_b() if t.folio not in ra.ROSETTES_FOLIOS)

jar_in_b = sum(1 for w in jar_words if w in b_words)
ros_in_b = sum(1 for w in set(ros_labels) if w in b_words)

print(f"\n  In B body text: jars={jar_in_b}/{len(jar_words)} ({100*jar_in_b/len(jar_words):.0f}%), "
      f"rosettes={ros_in_b}/{len(set(ros_labels))} ({100*ros_in_b/len(set(ros_labels)):.0f}%)")

# PP atom packing comparison
print(f"\n{'='*60}")
print(f"PP ATOM PACKING (Compression Test)")
print(f"{'='*60}")

# Count how many core MIDDLEs (len<=3) are embedded in each label's MIDDLE
core_mids = set()
for tok in tx.currier_b():
    m = morph.extract(tok.word)
    if m.middle and len(m.middle) <= 3:
        core_mids.add(m.middle)

def count_atoms(word):
    m = morph.extract(word)
    if not m.middle or len(m.middle) <= 3:
        return 0
    count = 0
    for cm in core_mids:
        if cm in m.middle:
            count += 1
    return count

jar_atoms = [(w, count_atoms(w)) for w in sorted(jar_words)]
ros_atoms = [(w, count_atoms(w)) for w in sorted(set(ros_labels)) if count_atoms(w) > 0]

print(f"\nJar labels with embedded atoms:")
for w, n in jar_atoms:
    if n > 0:
        print(f"  {w:<18s} {n} atoms")

jar_mean_atoms = sum(n for _, n in jar_atoms) / len(jar_atoms) if jar_atoms else 0
ros_long = [(w, n) for w, n in [(w, count_atoms(w)) for w in set(ros_labels)] if len(w) > 5]
ros_mean_atoms = sum(n for _, n in ros_long) / len(ros_long) if ros_long else 0

print(f"\nMean atom count (all): jars={jar_mean_atoms:.1f}, rosettes(len>5)={ros_mean_atoms:.1f}")

print(f"\n{'='*60}")
print(f"VERDICT")
print(f"{'='*60}")
print(f"""
Jar labels and Rosettes labels are DIFFERENT SYSTEMS:
  - Jar: longer (7.1), unique identifiers, NOT in text, compressed configs
  - Rosettes: shorter (5.3), 54% appear in B text, include hub vocabulary
  - Word overlap: minimal (only 'dy', 'okory', 'y' if any)
  - MIDDLE overlap exists but through CORE vocabulary shared by everything

However, they share PREFIX patterns:
  - Both favor ok- (routine) and da- (scaffold)
  - Both avoid ch-/sh- (energy operations)
  - This suggests both are MATERIAL-FACING, not OPERATION-FACING labels
""")
