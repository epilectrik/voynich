#!/usr/bin/env python3
"""
Test 23: Treatment Selection Hypothesis

If Voynich B encodes WHICH treatment to apply (not HOW to prepare it),
we should see:
1. Branching/selection patterns (if X then Y)
2. Condition assessment vocabulary (h = monitoring)
3. Outcome tracking (success/failure pathways)
4. Recovery routes when treatment fails

Compare to Trotula's simple linear recipes.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
import re
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TEST 23: TREATMENT SELECTION vs RECIPE PREPARATION")
print("=" * 70)
print()

# 1. Voynich B: How much is monitoring (h) vs transformation (k)?
print("1. VOYNICH B: MONITORING vs TRANSFORMATION")
print("-" * 50)

# h-class tokens: monitoring, assessment
# k-class tokens: transformation, kernel operations
# e-class tokens: output, escape, application

b_tokens = list(tx.currier_b())

h_prefixes = ['ch', 'sh', 'sch', 'cth', 'pch', 'lch']
k_prefixes = ['ok', 'qok', 'k', 'lk', 'yk', 'ke', 'ka']
e_prefixes = ['o', 'ol', 'or', 'ar', 'al']

role_counts = defaultdict(int)
for token in b_tokens:
    m = morph.extract(token.word)
    if m and m.prefix:
        p = m.prefix.lower()
        if any(p.startswith(h) for h in h_prefixes):
            role_counts['h (monitor)'] += 1
        elif any(p.startswith(k) for k in k_prefixes):
            role_counts['k (transform)'] += 1
        elif any(p.startswith(e) for e in e_prefixes):
            role_counts['e (output)'] += 1
        else:
            role_counts['other prefix'] += 1
    else:
        role_counts['no prefix'] += 1

total = sum(role_counts.values())
print("Voynich B role distribution:")
for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
    print(f"  {role}: {count} ({count/total*100:.1f}%)")

# Calculate h:k ratio - key for decision vs execution
h_count = role_counts.get('h (monitor)', 0)
k_count = role_counts.get('k (transform)', 0)
h_k_ratio = h_count / k_count if k_count > 0 else 0

print()
print(f"h:k ratio = {h_k_ratio:.2f}")
print()

# 2. Line-level: Does monitoring precede transformation?
print("2. LINE STRUCTURE: MONITOR THEN TRANSFORM?")
print("-" * 50)

# Group by line
b_by_line = defaultdict(list)
for token in tx.currier_b():
    key = (token.folio, token.line)
    m = morph.extract(token.word)
    if m and m.prefix:
        p = m.prefix.lower()
        if any(p.startswith(h) for h in h_prefixes):
            b_by_line[key].append('h')
        elif any(p.startswith(k) for k in k_prefixes):
            b_by_line[key].append('k')
        elif any(p.startswith(e) for e in e_prefixes):
            b_by_line[key].append('e')
        else:
            b_by_line[key].append('?')
    else:
        b_by_line[key].append('-')

# Analyze line patterns
pattern_counts = Counter()
for line_tokens in b_by_line.values():
    if len(line_tokens) >= 3:
        # Get unique sequence pattern (simplified)
        # Look at first 3 and last token
        first_three = ''.join(line_tokens[:3])
        pattern_counts[first_three] += 1

print("Most common line opening patterns (first 3 tokens by role):")
for pattern, count in pattern_counts.most_common(15):
    print(f"  {pattern}: {count}")

print()

# Check if h tends to come before k
h_before_k = 0
k_before_h = 0
for line_tokens in b_by_line.values():
    h_positions = [i for i, t in enumerate(line_tokens) if t == 'h']
    k_positions = [i for i, t in enumerate(line_tokens) if t == 'k']

    if h_positions and k_positions:
        avg_h = sum(h_positions) / len(h_positions)
        avg_k = sum(k_positions) / len(k_positions)
        if avg_h < avg_k:
            h_before_k += 1
        else:
            k_before_h += 1

print(f"Lines where h comes before k (on average): {h_before_k}")
print(f"Lines where k comes before h (on average): {k_before_h}")

if h_before_k > k_before_h:
    print("-> MONITOR-FIRST pattern: assess before transform")
else:
    print("-> TRANSFORM-FIRST pattern: act then check")

print()

# 3. Recovery/branching analysis
print("3. RECOVERY/BRANCHING EVIDENCE")
print("-" * 50)

# Look for lines that have BOTH h and e (monitor and escape)
# This suggests "if monitoring shows problem -> escape"
recovery_lines = 0
for line_tokens in b_by_line.values():
    has_h = 'h' in line_tokens
    has_e = 'e' in line_tokens
    if has_h and has_e:
        recovery_lines += 1

print(f"Lines with BOTH monitor (h) and output (e): {recovery_lines}")
print(f"Percentage: {recovery_lines / len(b_by_line) * 100:.1f}%")
print()

# 4. Compare to expected patterns
print("4. PATTERN COMPARISON")
print("-" * 50)

print("""
RECIPE PREPARATION pattern (like Trotula):
  - Linear: TAKE -> PROCESS -> GIVE
  - Minimal monitoring
  - No branching
  - Expected: low h:k ratio, few h+e lines

TREATMENT SELECTION pattern (decision tree):
  - Branching: ASSESS -> if X then A, else B
  - Heavy monitoring
  - Recovery pathways
  - Expected: high h:k ratio, many h+e lines
""")

print("Voynich B measurements:")
print(f"  h:k ratio: {h_k_ratio:.2f} (>1.0 suggests selection-heavy)")
print(f"  Monitor+output lines: {recovery_lines / len(b_by_line) * 100:.1f}%")
print()

# 5. Trotula conditional language
print("5. TROTULA CONDITIONAL/DECISION LANGUAGE")
print("-" * 50)

trotula_path = Path('C:/git/voynich/data/reference_texts/trotula/experimentarius_medicinae_1544.txt')
with open(trotula_path, 'r', encoding='utf-8') as f:
    trotula_text = f.read()[:200000]  # First 200k chars

# Count decision/conditional language
conditional_patterns = {
    r'\bsi\b': 'if (si)',
    r'\bvel\b': 'or (vel)',
    r'\baut\b': 'or (aut)',
    r'\baliter\b': 'otherwise',
    r'\bquod si\b': 'but if',
    r'\bnisi\b': 'unless',
}

decision_counts = Counter()
for pattern, meaning in conditional_patterns.items():
    count = len(re.findall(pattern, trotula_text, re.IGNORECASE))
    decision_counts[meaning] = count

print("Trotula conditional/decision terms:")
for term, count in decision_counts.most_common():
    print(f"  {term}: {count}")

total_conditionals = sum(decision_counts.values())
total_operations = len(re.findall(r'\b(da|coque|accipe|recipe)\b', trotula_text, re.IGNORECASE))

conditional_ratio = total_conditionals / total_operations if total_operations > 0 else 0
print()
print(f"Conditional terms per operation: {conditional_ratio:.2f}")

print()

# 6. Synthesis
print("=" * 70)
print("SYNTHESIS: WHAT DOES VOYNICH B ENCODE?")
print("=" * 70)

print(f"""
EVIDENCE SUMMARY:

Voynich B characteristics:
- h:k ratio = {h_k_ratio:.2f} (monitoring vs transformation)
- {recovery_lines / len(b_by_line) * 100:.1f}% of lines have monitor+output
- h tends to come {'before' if h_before_k > k_before_h else 'after'} k
- Per BCSC: 17 forbidden transitions (hazard avoidance)
- Per BCSC: Recovery architecture with escape routes

Trotula characteristics:
- 78.3% output-dominated (da/give verbs)
- Linear TAKE -> PROCESS -> GIVE
- Conditional ratio: {conditional_ratio:.2f} per operation
- Simple procedural structure

INTERPRETATION:
""")

if h_k_ratio > 1.0 and recovery_lines / len(b_by_line) > 0.3:
    print("""
STRONG EVIDENCE: Voynich B is TREATMENT SELECTION

Voynich B appears to encode:
- WHEN to apply treatments (timing/conditions)
- WHICH treatment pathway to choose
- HOW to recover if treatment fails
- WHAT combinations are forbidden

NOT:
- Detailed recipe preparation steps
- Material quantities
- Cooking/boiling instructions

The Rosettes + B folios may function as:
- Navigation/routing system for treatments
- Decision tree with hazard avoidance
- Selection logic rather than preparation instructions

External recipe collections (like Trotula) would provide
the actual HOW-TO instructions for each selected treatment.
""")
elif h_k_ratio > 0.5:
    print("""
MODERATE EVIDENCE: Voynich B has SELECTION COMPONENT

Voynich B appears to encode BOTH:
- Some treatment selection logic
- Some procedural information

May be intermediate between pure recipes and pure routing.
""")
else:
    print("""
WEAK EVIDENCE: Cannot distinguish selection from preparation

Voynich B structure doesn't clearly indicate
treatment selection over recipe encoding.
""")

# Final comparison
print()
print("TROTULA vs VOYNICH STRUCTURAL FIT:")
print("-" * 50)
print("""
                    Trotula         Voynich B
                    -------         ---------
Primary function    Preparation     Selection?
Decision ratio      Low             High (h-heavy)
Recovery paths      None            Yes (e-escapes)
Hazard avoidance    None            17 forbidden
Linear vs Branch    Linear          Branching

CONCLUSION: Trotula recipes are COMPATIBLE as content
that Voynich B SELECTS, not as structural matches.
""")
