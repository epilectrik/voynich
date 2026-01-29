"""
T1: CC Token Inventory

What are the actual tokens in CC classes 10, 11, 12, 17?
What are their morphological characteristics?
Why does class 12 show 0 tokens?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']
class_to_tokens = ctm['class_to_tokens']

CC_CLASSES = [10, 11, 12, 17]

print("="*70)
print("CC TOKEN INVENTORY")
print("="*70)

# ============================================================
# CLASS MEMBERSHIP
# ============================================================
print("\n" + "="*70)
print("CLASS MEMBERSHIP (from class_token_map)")
print("="*70)

cc_tokens_by_class = {}
for cls in CC_CLASSES:
    tokens = class_to_tokens.get(str(cls), [])
    cc_tokens_by_class[cls] = tokens
    print(f"\nClass {cls}: {len(tokens)} types")
    if tokens:
        print(f"  Sample: {tokens[:10]}")

# ============================================================
# OCCURRENCE COUNTS IN B TEXT
# ============================================================
print("\n" + "="*70)
print("OCCURRENCE COUNTS IN B TEXT")
print("="*70)

cc_occ_counts = {cls: Counter() for cls in CC_CLASSES}
cc_total_occ = {cls: 0 for cls in CC_CLASSES}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if w in token_to_class:
        cls = int(token_to_class[w])
        if cls in CC_CLASSES:
            cc_occ_counts[cls][w] += 1
            cc_total_occ[cls] += 1

for cls in CC_CLASSES:
    print(f"\nClass {cls}: {cc_total_occ[cls]} occurrences, {len(cc_occ_counts[cls])} types")
    if cc_occ_counts[cls]:
        print(f"  Top 5: {cc_occ_counts[cls].most_common(5)}")

# ============================================================
# MORPHOLOGICAL ANALYSIS
# ============================================================
print("\n" + "="*70)
print("MORPHOLOGICAL ANALYSIS")
print("="*70)

cc_middles = {cls: Counter() for cls in CC_CLASSES}
cc_prefixes = {cls: Counter() for cls in CC_CLASSES}
cc_suffixes = {cls: Counter() for cls in CC_CLASSES}
cc_kernel_chars = {cls: Counter() for cls in CC_CLASSES}

KERNEL_CHARS = {'k', 'h', 'e'}

for cls in CC_CLASSES:
    for tok in cc_tokens_by_class[cls]:
        m = morph.extract(tok)
        if m.middle:
            cc_middles[cls][m.middle] += 1
            # Check kernel chars in middle
            for c in m.middle:
                if c in KERNEL_CHARS:
                    cc_kernel_chars[cls][c] += 1
        if m.prefix:
            cc_prefixes[cls][m.prefix] += 1
        if m.suffix:
            cc_suffixes[cls][m.suffix] += 1

for cls in CC_CLASSES:
    print(f"\nClass {cls}:")
    print(f"  MIDDLEs: {len(cc_middles[cls])} unique")
    if cc_middles[cls]:
        print(f"    Top 5: {cc_middles[cls].most_common(5)}")
    print(f"  PREFIXes: {cc_prefixes[cls].most_common(5) if cc_prefixes[cls] else 'None'}")
    print(f"  SUFFIXes: {cc_suffixes[cls].most_common(5) if cc_suffixes[cls] else 'None'}")
    print(f"  Kernel chars in MIDDLEs: {dict(cc_kernel_chars[cls])}")

# ============================================================
# KERNEL RATE BY CLASS (TYPE-LEVEL)
# ============================================================
print("\n" + "="*70)
print("KERNEL RATE BY CLASS (TYPE-LEVEL)")
print("="*70)

for cls in CC_CLASSES:
    tokens = cc_tokens_by_class[cls]
    if not tokens:
        print(f"Class {cls}: No tokens")
        continue

    kernel_count = 0
    for tok in tokens:
        m = morph.extract(tok)
        if m.middle and any(c in KERNEL_CHARS for c in m.middle):
            kernel_count += 1

    rate = 100 * kernel_count / len(tokens) if tokens else 0
    print(f"Class {cls}: {kernel_count}/{len(tokens)} = {rate:.1f}% kernel")

# ============================================================
# KERNEL CHAR BREAKDOWN
# ============================================================
print("\n" + "="*70)
print("KERNEL CHAR BREAKDOWN (which k/h/e)")
print("="*70)

for cls in CC_CLASSES:
    tokens = cc_tokens_by_class[cls]
    if not tokens:
        continue

    has_k = sum(1 for t in tokens if 'k' in (morph.extract(t).middle or ''))
    has_h = sum(1 for t in tokens if 'h' in (morph.extract(t).middle or ''))
    has_e = sum(1 for t in tokens if 'e' in (morph.extract(t).middle or ''))

    n = len(tokens)
    print(f"Class {cls} (n={n}):")
    print(f"  k: {has_k} ({100*has_k/n:.1f}%)")
    print(f"  h: {has_h} ({100*has_h/n:.1f}%)")
    print(f"  e: {has_e} ({100*has_e/n:.1f}%)")

# ============================================================
# CLASS 12 INVESTIGATION
# ============================================================
print("\n" + "="*70)
print("CLASS 12 INVESTIGATION")
print("="*70)

class_12_tokens = class_to_tokens.get('12', [])
print(f"Class 12 has {len(class_12_tokens)} types in class_token_map")

if class_12_tokens:
    print(f"Tokens: {class_12_tokens}")
    # Check if they appear in B text
    b_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w:
            b_words.add(w)

    in_b = [t for t in class_12_tokens if t in b_words]
    print(f"Of these, {len(in_b)} appear in B text: {in_b}")
else:
    print("Class 12 is empty in class_token_map")

# ============================================================
# FORBIDDEN PAIR PARTICIPATION DETAIL
# ============================================================
print("\n" + "="*70)
print("FORBIDDEN PAIR PARTICIPATION BY CC CLASS")
print("="*70)

# From t2_forbidden_pair_pattern results
cc_forbidden = {
    'as_source': {10: 4, 11: 4, 12: 2, 17: 2},
    'as_target': {12: 4, 17: 4}
}

for cls in CC_CLASSES:
    src = cc_forbidden['as_source'].get(cls, 0)
    tgt = cc_forbidden['as_target'].get(cls, 0)
    print(f"Class {cls}: SOURCE in {src} pairs, TARGET in {tgt} pairs")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Class 12 status
if not class_12_tokens:
    findings.append("CLASS_12_EMPTY: Class 12 has no tokens in grammar")
elif cc_total_occ[12] == 0:
    findings.append(f"CLASS_12_ABSENT: Class 12 has {len(class_12_tokens)} types but 0 B occurrences")

# Kernel bifurcation
k10 = sum(1 for t in cc_tokens_by_class[10] if any(c in KERNEL_CHARS for c in (morph.extract(t).middle or '')))
k11 = sum(1 for t in cc_tokens_by_class[11] if any(c in KERNEL_CHARS for c in (morph.extract(t).middle or '')))
k17 = sum(1 for t in cc_tokens_by_class[17] if any(c in KERNEL_CHARS for c in (morph.extract(t).middle or '')))

n10, n11, n17 = len(cc_tokens_by_class[10]), len(cc_tokens_by_class[11]), len(cc_tokens_by_class[17])

if n10 > 0 and n11 > 0 and n17 > 0:
    r10 = 100 * k10 / n10
    r11 = 100 * k11 / n11
    r17 = 100 * k17 / n17

    if r10 < 10 and r11 < 10 and r17 > 80:
        findings.append(f"KERNEL_BIFURCATION_CONFIRMED: 10={r10:.0f}%, 11={r11:.0f}%, 17={r17:.0f}%")

# Source vs target pattern
if cc_forbidden['as_target'].get(10, 0) == 0 and cc_forbidden['as_target'].get(11, 0) == 0:
    findings.append("CC_GROUP_A_SOURCE_ONLY: Classes 10,11 are never forbidden targets")

if cc_forbidden['as_source'].get(12, 0) > 0 or cc_forbidden['as_source'].get(17, 0) > 0:
    if cc_forbidden['as_target'].get(12, 0) > 0 or cc_forbidden['as_target'].get(17, 0) > 0:
        findings.append("CC_GROUP_B_BIDIRECTIONAL: Classes 12,17 are both source and target")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Save results
results = {
    'cc_types': {cls: len(cc_tokens_by_class[cls]) for cls in CC_CLASSES},
    'cc_occurrences': cc_total_occ,
    'cc_middles': {cls: dict(cc_middles[cls].most_common(10)) for cls in CC_CLASSES},
    'cc_kernel_rates': {
        cls: round(100 * sum(1 for t in cc_tokens_by_class[cls]
                            if any(c in KERNEL_CHARS for c in (morph.extract(t).middle or '')))
                   / len(cc_tokens_by_class[cls]), 1) if cc_tokens_by_class[cls] else 0
        for cls in CC_CLASSES
    },
    'cc_kernel_chars': {cls: dict(cc_kernel_chars[cls]) for cls in CC_CLASSES},
    'class_12_types': class_12_tokens,
    'class_12_in_b': len([t for t in class_12_tokens if t in b_words]) if class_12_tokens else 0,
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'CC_MECHANICS_DEEP_DIVE' / 'results' / 't1_cc_token_inventory.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
