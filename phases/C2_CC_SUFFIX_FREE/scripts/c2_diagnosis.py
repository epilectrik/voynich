"""
C2 CC Suffix-Free Diagnosis

Investigate the C2 test failure:
- C588/C590 say CC is 100% suffix-free
- C1025 reports real C2 = 0.834
- C1030 reports CC = 100% suffix-free (735 tokens)
- But generative_sufficiency.py uses CC={10,11,12,17}

Questions:
1. Does class 17 really have suffixed tokens per morph.extract()?
2. Is the C2 metric computed correctly?
3. Is the CC definition correct?
4. Is C2 misspecified (like B4 was)?
"""

import sys, json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

# ── Definitions ───────────────────────────────────────────────
ROLE_CLASSES_5 = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}

MACRO_CC = {10, 11, 12}  # C1030's definition

# ── Data Loading ──────────────────────────────────────────────
morph = Morphology()
tx = Transcript()

# Load class map
with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
          encoding='utf-8') as f:
    cmap = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

# ── T1: Class 17 Token Inventory ─────────────────────────────
print("=" * 70)
print("T1: CLASS 17 TOKEN INVENTORY")
print("=" * 70)

class17_tokens = []
for token in tx.currier_b():
    if token.placement.startswith('L'):
        continue
    if not token.word or not token.word.strip() or '*' in token.word:
        continue
    cls = token_to_class.get(token.word)
    if cls == 17:
        m = morph.extract(token.word)
        class17_tokens.append({
            'word': token.word,
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else None,
            'suffix': m.suffix if m else None,
        })

# Count by word
word_counts = Counter(t['word'] for t in class17_tokens)
print(f"\nClass 17 total tokens: {len(class17_tokens)}")
print(f"Class 17 unique types: {len(word_counts)}")
print(f"\nTop 20 class 17 tokens:")
for word, count in word_counts.most_common(20):
    m = morph.extract(word)
    sfx = m.suffix if m else None
    pfx = m.prefix if m else None
    mid = m.middle if m else None
    print(f"  {word:20s} n={count:4d}  pfx={str(pfx):6s} mid={str(mid):8s} sfx={str(sfx):6s}")

# Count suffixed
suffixed = sum(1 for t in class17_tokens if t['suffix'])
print(f"\nClass 17 suffixed: {suffixed}/{len(class17_tokens)} = {suffixed/max(len(class17_tokens),1):.3f}")
print(f"Class 17 suffix-free: {len(class17_tokens)-suffixed}/{len(class17_tokens)} = {(len(class17_tokens)-suffixed)/max(len(class17_tokens),1):.3f}")

# ── T2: CC Suffix-Free by Definition ─────────────────────────
print("\n" + "=" * 70)
print("T2: CC SUFFIX-FREE BY DEFINITION")
print("=" * 70)

all_tokens = []
for token in tx.currier_b():
    if token.placement.startswith('L'):
        continue
    if not token.word or not token.word.strip() or '*' in token.word:
        continue
    cls = token_to_class.get(token.word)
    if cls is None:
        continue
    m = morph.extract(token.word)
    all_tokens.append({
        'word': token.word,
        'cls': cls,
        'suffix': m.suffix if m else None,
    })

for label, cc_set in [("MACRO CC={10,11,12}", MACRO_CC),
                        ("ROLE CC={10,11,12,17}", ROLE_CLASSES_5['CC'])]:
    cc_tokens = [t for t in all_tokens if t['cls'] in cc_set]
    cc_suffixed = sum(1 for t in cc_tokens if t['suffix'])
    cc_sfree = 1.0 - (cc_suffixed / max(len(cc_tokens), 1))
    print(f"\n{label}:")
    print(f"  Total CC tokens: {len(cc_tokens)}")
    print(f"  Suffixed: {cc_suffixed}")
    print(f"  Suffix-free rate: {cc_sfree:.4f}")

# ── T3: Per-Class Breakdown ──────────────────────────────────
print("\n" + "=" * 70)
print("T3: PER-CLASS SUFFIX BREAKDOWN FOR CC CLASSES")
print("=" * 70)

for cls_id in sorted(ROLE_CLASSES_5['CC']):
    cls_tokens = [t for t in all_tokens if t['cls'] == cls_id]
    if not cls_tokens:
        print(f"\n  Class {cls_id}: 0 tokens (ghost)")
        continue
    suffixed = sum(1 for t in cls_tokens if t['suffix'])
    sfree = 1.0 - (suffixed / len(cls_tokens))
    print(f"\n  Class {cls_id}: {len(cls_tokens)} tokens, {suffixed} suffixed ({sfree:.3f} suffix-free)")
    if suffixed > 0:
        suffix_examples = [(t['word'], t['suffix']) for t in cls_tokens if t['suffix']]
        suffix_counter = Counter(s for _, s in suffix_examples)
        print(f"    Suffix types: {dict(suffix_counter)}")
        # Show some examples
        word_sfx = Counter((t['word'], t['suffix']) for t in cls_tokens if t['suffix'])
        for (w, s), n in word_sfx.most_common(10):
            m = morph.extract(w)
            print(f"    {w:20s} sfx={s:6s} (n={n:3d})  [pfx={m.prefix}, mid={m.middle}]")

# ── T4: Reproduce C2 Metric Exactly ─────────────────────────
print("\n" + "=" * 70)
print("T4: REPRODUCE C2 METRIC (as in generative_sufficiency.py)")
print("=" * 70)

cc_total = 0
cc_violations = 0
for t in all_tokens:
    role = None
    for rname, rclasses in ROLE_CLASSES_5.items():
        if t['cls'] in rclasses:
            role = rname
            break
    if role == 'CC':
        cc_total += 1
        if t['suffix']:
            cc_violations += 1

c2 = 1.0 - (cc_violations / max(cc_total, 1))
print(f"\nCC total: {cc_total}")
print(f"CC violations: {cc_violations}")
print(f"C2 metric: {c2:.4f}")
print(f"C1025 reported: 0.834")
print(f"Match: {abs(c2 - 0.834) < 0.01}")

# ── T5: What If CC = {10,11,12} Only? ────────────────────────
print("\n" + "=" * 70)
print("T5: C2 WITH CORRECTED CC DEFINITION")
print("=" * 70)

cc_total_corrected = 0
cc_violations_corrected = 0
for t in all_tokens:
    if t['cls'] in MACRO_CC:
        cc_total_corrected += 1
        if t['suffix']:
            cc_violations_corrected += 1

c2_corrected = 1.0 - (cc_violations_corrected / max(cc_total_corrected, 1))
print(f"\nCC={'{10,11,12}'} total: {cc_total_corrected}")
print(f"CC={'{10,11,12}'} violations: {cc_violations_corrected}")
print(f"C2 corrected: {c2_corrected:.4f}")

# ── T6: Check C590 Claim ─────────────────────────────────────
print("\n" + "=" * 70)
print("T6: C590 CLAIM VERIFICATION")
print("=" * 70)
print("C590 says class 17 suffix = NONE")
print(f"Our finding: class 17 has {suffixed} suffixed tokens out of {len(class17_tokens)}")
if suffixed > 0:
    print("=> C590 is WRONG about class 17 suffix = NONE")
    print("   OR the morphological parser has changed since C590")
else:
    print("=> C590 is CONFIRMED. Class 17 is suffix-free.")
    print("   The C2 failure must come from a different source.")

# ── T7: Diagnosis ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("T7: DIAGNOSIS")
print("=" * 70)

if c2_corrected >= 0.99:
    print("\nCC={10,11,12} is >= 99% suffix-free.")
    if c2 < 0.99:
        print(f"CC={'{10,11,12,17}'} is {c2:.3f} suffix-free (< 99%).")
        print("\n=> C2 IS MISSPECIFIED.")
        print("   The test uses ROLE CC={10,11,12,17} but")
        print("   C588/C590 defined CC suffix-free using CC={10,11,12}.")
        print("   Class 17 has suffixed tokens, dragging the metric below 99%.")
        print("\n   Fix options:")
        print("   A) Change CC definition in test to {10,11,12} (match C588/C590)")
        print("   B) Change threshold to match real value")
        print("   C) Use relative test: |gen_C2 - real_C2| < tolerance")
        verdict = "C2_MISSPECIFIED"
    else:
        print("Both definitions pass. C2 is fine.")
        verdict = "C2_OK"
else:
    print(f"Even CC={'{10,11,12}'} fails at {c2_corrected:.3f}.")
    verdict = "C2_GENUINE_FAILURE"

print(f"\nVerdict: {verdict}")

# ── Save ──────────────────────────────────────────────────────
results = {
    'class17_total': len(class17_tokens),
    'class17_suffixed': suffixed,
    'class17_suffix_free_rate': (len(class17_tokens)-suffixed)/max(len(class17_tokens),1),
    'c2_role_cc': c2,
    'c2_macro_cc': c2_corrected,
    'c2_role_cc_total': cc_total,
    'c2_role_cc_violations': cc_violations,
    'c2_macro_cc_total': cc_total_corrected,
    'c2_macro_cc_violations': cc_violations_corrected,
    'c1025_reported': 0.834,
    'verdict': verdict,
}

out_dir = PROJECT / 'phases' / 'C2_CC_SUFFIX_FREE' / 'results'
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / 'c2_diagnosis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_dir / 'c2_diagnosis.json'}")
