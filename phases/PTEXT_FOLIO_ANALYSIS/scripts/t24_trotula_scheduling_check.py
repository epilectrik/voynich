#!/usr/bin/env python3
"""
Test 24: Does Trotula Have Treatment Scheduling?

Check if Trotula actually contains:
1. Timing instructions (when to apply)
2. Conditional selection (if X then Y)
3. Contraindication warnings (don't combine)

If NOT, then we're speculating about treatment selection.
"""

from pathlib import Path
import re

trotula_path = Path('C:/git/voynich/data/reference_texts/trotula/experimentarius_medicinae_1544.txt')
trotula = trotula_path.read_text(encoding='utf-8')
trotula = trotula[:trotula.find('HILDEGARDIs')]

print("=" * 70)
print("TEST 24: DOES TROTULA HAVE TREATMENT SCHEDULING?")
print("=" * 70)
print()

# 1. Timing/scheduling language
print("1. TIMING/SCHEDULING LANGUAGE")
print("-" * 50)

timing_patterns = {
    'mane': 'morning',
    'vespere': 'evening',
    'nocte': 'at night',
    r'\bhora\b': 'hour',
    r'\bdie\b': 'day',
    'diebus': 'days',
    'dies': 'days',
    'luna': 'moon',
    'mense': 'month',
    'mensibus': 'months',
    'tempore': 'time/season',
    'ante cibum': 'before food',
    'post cibum': 'after food',
    'ieiuni': 'fasting',
    'quando': 'when',
    'donec': 'until',
    'quousque': 'until',
    'per': 'for (duration)',
}

timing_total = 0
for pattern, meaning in timing_patterns.items():
    count = len(re.findall(pattern, trotula, re.IGNORECASE))
    if count > 0:
        print(f"  {pattern} ({meaning}): {count}")
        timing_total += count

print(f"\nTotal timing terms: {timing_total}")
print()

# 2. Conditional/selection language
print("2. CONDITIONAL/SELECTION LANGUAGE")
print("-" * 50)

selection_patterns = {
    r'\bsi\b': 'if',
    r'si non': 'if not',
    r'si autem': 'but if',
    r'quod si': 'but if',
    r'vel si': 'or if',
    r'nisi': 'unless',
    r'secundum': 'according to',
    r'pro\b': 'for/depending on',
    r'iuxta': 'according to',
    r'aliter': 'otherwise',
}

selection_total = 0
for pattern, meaning in selection_patterns.items():
    count = len(re.findall(pattern, trotula, re.IGNORECASE))
    if count > 0:
        print(f"  {pattern} ({meaning}): {count}")
        selection_total += count

print(f"\nTotal selection terms: {selection_total}")
print()

# 3. Contraindication/warning language
print("3. CONTRAINDICATION/WARNING LANGUAGE")
print("-" * 50)

contra_patterns = {
    r'cave\b': 'beware',
    r'caveat': 'let him beware',
    r'cavendum': 'must beware',
    r'nocet': 'harms',
    r'noceat': 'may harm',
    r'periculosum': 'dangerous',
    r'periculum': 'danger',
    r'contrari': 'contrary',
    r'non debet': 'must not',
    r'prohib': 'forbid',
    r'vitand': 'avoid',
}

contra_total = 0
for pattern, meaning in contra_patterns.items():
    count = len(re.findall(pattern, trotula, re.IGNORECASE))
    if count > 0:
        print(f"  {pattern} ({meaning}): {count}")
        contra_total += count

print(f"\nTotal contraindication terms: {contra_total}")
print()

# 4. Extract sample scheduling instructions
print("4. SAMPLE SCHEDULING INSTRUCTIONS")
print("-" * 50)

# Find sentences with timing terms
sentences = re.split(r'[.;]', trotula)
timing_sentences = []
for sent in sentences:
    if re.search(r'(mane|vespere|nocte|diebus|dies\b|ante cibum|post cibum)', sent, re.IGNORECASE):
        timing_sentences.append(sent.strip()[:200])

print(f"Found {len(timing_sentences)} sentences with timing instructions")
print("\nExamples:")
for i, sent in enumerate(timing_sentences[:5]):
    print(f"  {i+1}. {sent}...")
print()

# 5. Extract conditional treatment selections
print("5. SAMPLE CONDITIONAL SELECTIONS")
print("-" * 50)

conditional_sentences = []
for sent in sentences:
    if re.search(r'\bsi\b.*\b(da|accipe|recipe|coque)\b', sent, re.IGNORECASE):
        conditional_sentences.append(sent.strip()[:200])

print(f"Found {len(conditional_sentences)} if...then treatment selections")
print("\nExamples:")
for i, sent in enumerate(conditional_sentences[:5]):
    print(f"  {i+1}. {sent}...")
print()

# 6. Summary assessment
print("=" * 70)
print("ASSESSMENT: DOES TROTULA HAVE TREATMENT SCHEDULING?")
print("=" * 70)

total_ops = len(re.findall(r'\b(da|coque|accipe|recipe)\b', trotula, re.IGNORECASE))
print(f"\nTotal procedural operations: {total_ops}")
print(f"Timing instructions: {timing_total} ({timing_total/total_ops*100:.1f}% of operations)")
print(f"Conditional selections: {selection_total} ({selection_total/total_ops*100:.1f}% of operations)")
print(f"Contraindications: {contra_total} ({contra_total/total_ops*100:.1f}% of operations)")

print()
scheduling_ratio = (timing_total + selection_total + contra_total) / total_ops

if scheduling_ratio > 0.5:
    print("VERDICT: YES - Trotula has substantial scheduling/selection content")
    print(f"Scheduling ratio: {scheduling_ratio:.2f} per operation")
elif scheduling_ratio > 0.2:
    print("VERDICT: PARTIAL - Trotula has some scheduling, but mostly recipes")
    print(f"Scheduling ratio: {scheduling_ratio:.2f} per operation")
else:
    print("VERDICT: NO - Trotula is primarily recipe preparation, not scheduling")
    print(f"Scheduling ratio: {scheduling_ratio:.2f} per operation")
    print()
    print("IMPLICATION: We are SPECULATING about treatment selection.")
    print("Trotula does not provide evidence that medieval medical texts")
    print("contained the kind of scheduling/selection logic we hypothesized.")
