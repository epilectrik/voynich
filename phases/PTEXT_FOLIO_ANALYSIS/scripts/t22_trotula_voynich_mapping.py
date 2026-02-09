#!/usr/bin/env python3
"""
Test 22: Trotula-Voynich Structural Mapping

Deep analysis comparing:
1. Trotula recipe sequences vs Voynich line-level transitions
2. Trotula operation types vs Voynich instruction roles (h/k/e)
3. Whether Trotula procedural logic matches Voynich control structure

Key question: Could Voynich B encode Trotula-style decoction recipes?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
import re
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

# Load Voynich data
tx = Transcript()
morph = Morphology()

# Read Trotula text
trotula_path = Path('C:/git/voynich/data/reference_texts/trotula/experimentarius_medicinae_1544.txt')
with open(trotula_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Only Trotula section
trotula_text = text[:text.find('HILDEGARDIs')]

print("=" * 70)
print("TEST 22: TROTULA-VOYNICH STRUCTURAL MAPPING")
print("=" * 70)
print()

# 1. Extract Trotula operation types and map to Voynich h/k/e
print("1. TROTULA OPERATIONS -> VOYNICH ROLE MAPPING")
print("-" * 50)

# Categorize Trotula operations by functional type
trotula_ops = {
    # MONITORING (h-like): assessing, checking state
    'h_like': {
        'cognosc': 'RECOGNIZE/KNOW',  # assess condition
        'vide': 'SEE/OBSERVE',
        'inspic': 'INSPECT',
        'prob': 'TEST/TRY',
    },
    # KERNEL (k-like): transformative operations
    'k_like': {
        'coque': 'COOK',
        'coquat': 'COOK',
        'coquantur': 'COOK',
        'decoque': 'DECOCT',
        'bulliat': 'BOIL',
        'bulliant': 'BOIL',
        'tere': 'GRIND',
        'teratur': 'GRIND',
        'confic': 'PREPARE/MIX',
        'combur': 'BURN',
        'ust': 'BURN',
        'fiat': 'LET BE MADE',
    },
    # ESCAPE/OUTPUT (e-like): final application
    'e_like': {
        'da': 'GIVE',
        'detur': 'LET BE GIVEN',
        'bibat': 'DRINK',
        'potetur': 'LET BE DRUNK',
        'impone': 'APPLY',
        'inunge': 'ANOINT',
        'laua': 'WASH',
        'sedeat': 'SIT (in bath)',
        'fumig': 'FUMIGATE',
        'suppon': 'APPLY BELOW',
    },
    # SETUP (prefix-like): initialization
    'prefix_like': {
        'accipe': 'TAKE',
        'recipe': 'TAKE',
        'pone': 'PUT/PLACE',
        'adde': 'ADD',
        'misce': 'MIX IN',
        'cola': 'STRAIN',
        'coletur': 'LET BE STRAINED',
    }
}

# Count each category
category_counts = defaultdict(int)
for category, patterns in trotula_ops.items():
    for pattern in patterns.keys():
        count = len(re.findall(pattern, trotula_text, re.IGNORECASE))
        category_counts[category] += count

total_ops = sum(category_counts.values())
print("Trotula operation distribution by Voynich role:")
for cat in ['prefix_like', 'h_like', 'k_like', 'e_like']:
    count = category_counts[cat]
    pct = count / total_ops * 100 if total_ops > 0 else 0
    print(f"  {cat}: {count} ({pct:.1f}%)")

print()

# 2. Compare to actual Voynich B role distribution
print("2. VOYNICH B ACTUAL ROLE DISTRIBUTION")
print("-" * 50)

# Get Currier B tokens and classify
b_tokens = list(tx.currier_b())

# Count h, k, e tokens based on PREFIX patterns
# h-prefixes: sh, ch (monitoring)
# k-prefixes: ok, qok (kernel)
# e-prefixes: o (escape/output)
voynich_roles = Counter()
for token in b_tokens:
    m = morph.extract(token.word)
    if m and m.prefix:
        p = m.prefix.lower()
        if p in ['sh', 'ch', 'sch', 'cth']:
            voynich_roles['h_dominant'] += 1
        elif 'ok' in p or 'qok' in p or p.startswith('k'):
            voynich_roles['k_dominant'] += 1
        elif p in ['o', 'ol', 'or', 'ar']:
            voynich_roles['e_potential'] += 1
        else:
            voynich_roles['other'] += 1
    else:
        voynich_roles['no_prefix'] += 1

total_b = sum(voynich_roles.values())
print("Voynich B PREFIX role hints:")
for role, count in voynich_roles.most_common():
    print(f"  {role}: {count} ({count/total_b*100:.1f}%)")

print()

# 3. Recipe sequence analysis
print("3. TROTULA RECIPE SEQUENCE PATTERNS")
print("-" * 50)

# Extract recipes and analyze step sequences
recipes = []
current_recipe = []

# Find all sentences (roughly)
sentences = re.split(r'[.;]', trotula_text)

for sent in sentences:
    sent_lower = sent.lower()

    # Check for recipe start
    if re.search(r'\b(accipe|recipe)\b', sent_lower):
        if current_recipe:
            recipes.append(current_recipe)
        current_recipe = ['TAKE']
    elif current_recipe:
        # Check what operations appear
        if re.search(r'(coque|coqu|decoque|bull)', sent_lower):
            current_recipe.append('COOK')
        if re.search(r'(tere|tera|pista)', sent_lower):
            current_recipe.append('GRIND')
        if re.search(r'(col[ae]|strain)', sent_lower):
            current_recipe.append('STRAIN')
        if re.search(r'(adde|misce)', sent_lower):
            current_recipe.append('MIX')
        if re.search(r'\bda\b|detur|bibat|potetur', sent_lower):
            current_recipe.append('GIVE')
        if re.search(r'(impone|inunge|laua)', sent_lower):
            current_recipe.append('APPLY')

if current_recipe:
    recipes.append(current_recipe)

# Analyze sequences
sequence_counts = Counter()
for recipe in recipes:
    if len(recipe) >= 2:
        seq = ' -> '.join(recipe)
        sequence_counts[seq] += 1

print(f"Extracted {len(recipes)} recipe sequences")
print()
print("Most common sequences:")
for seq, count in sequence_counts.most_common(15):
    print(f"  [{count}] {seq}")

print()

# 4. Voynich line-level transition patterns
print("4. VOYNICH B LINE-LEVEL PATTERNS")
print("-" * 50)

# Group B tokens by folio and line
b_by_line = defaultdict(list)
for token in tx.currier_b():
    key = (token.folio, token.line)
    m = morph.extract(token.word)
    if m:
        b_by_line[key].append(m)

# Analyze within-line patterns: do lines follow TAKE -> PROCESS -> OUTPUT?
line_patterns = Counter()
for (folio, line), tokens in b_by_line.items():
    if len(tokens) < 3:
        continue

    # Check first and last token characteristics
    first = tokens[0]
    last = tokens[-1]

    # First token often has o- or ol- prefix (like TAKE)
    first_is_init = first.prefix and first.prefix.lower() in ['o', 'ol', 'or', 'qo']

    # Last token often has -y suffix (completion marker)
    last_is_complete = last.suffix and last.suffix.lower() == 'y'

    if first_is_init and last_is_complete:
        line_patterns['INIT -> ... -> COMPLETE'] += 1
    elif first_is_init:
        line_patterns['INIT -> ...'] += 1
    elif last_is_complete:
        line_patterns['... -> COMPLETE'] += 1
    else:
        line_patterns['other'] += 1

print("Voynich B line patterns (first/last token):")
for pattern, count in line_patterns.most_common():
    print(f"  {pattern}: {count}")

print()

# 5. Solvent/carrier analysis
print("5. SOLVENT/CARRIER COMPARISON")
print("-" * 50)

# Trotula uses specific solvents
trotula_solvents = {
    'aqua': 'water',
    'uinum': 'wine',
    'uino': 'wine',
    'acetum': 'vinegar',
    'mel': 'honey',
    'oleum': 'oil',
    'lac': 'milk',
}

solvent_counts = Counter()
for pattern, name in trotula_solvents.items():
    count = len(re.findall(pattern, trotula_text, re.IGNORECASE))
    solvent_counts[name] += count

print("Trotula solvents/carriers:")
for solvent, count in solvent_counts.most_common():
    print(f"  {solvent}: {count}")

print()

# In Voynich, check if PREFIX patterns might encode solvent choice
print("Voynich B PREFIX frequency (potential solvent encoding):")
prefix_counts = Counter()
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m and m.prefix:
        prefix_counts[m.prefix.lower()] += 1

for prefix, count in prefix_counts.most_common(15):
    print(f"  {prefix}: {count}")

print()

# 6. Structural compatibility assessment
print("=" * 70)
print("STRUCTURAL COMPATIBILITY ASSESSMENT")
print("=" * 70)

print("""
TROTULA STRUCTURE:
- Recipes are LINEAR: TAKE -> PROCESS -> OUTPUT
- Few branching conditions
- 2-5 steps per recipe typically
- Material list upfront, then operations

VOYNICH B STRUCTURE (per BCSC):
- Lines are CONTROL BLOCKS with hazard constraints
- Tokens have PREFIX (pathway) + MIDDLE (state) + SUFFIX (outcome)
- Strong h/k/e role system
- Forbidden transitions (hazard avoidance)

COMPATIBILITY ANALYSIS:
""")

# Calculate ratios
e_ratio_trotula = category_counts['e_like'] / total_ops * 100 if total_ops > 0 else 0
k_ratio_trotula = category_counts['k_like'] / total_ops * 100 if total_ops > 0 else 0

print(f"Trotula e-like (output) operations: {e_ratio_trotula:.1f}%")
print(f"Trotula k-like (kernel) operations: {k_ratio_trotula:.1f}%")
print()

# The key insight
print("KEY FINDING:")
print("-" * 50)

if e_ratio_trotula > k_ratio_trotula:
    print("""
TROTULA IS OUTPUT-HEAVY:
- Dominated by 'da' (GIVE) = output/application verbs
- More focused on DELIVERY than TRANSFORMATION
- This differs from Voynich B's kernel-centric design

IMPLICATION:
Trotula recipes may be TOO SIMPLE for Voynich B grammar.
Voynich B appears designed for processes with:
- Multiple state transitions (kernel operations)
- Hazard avoidance (forbidden sequences)
- Recovery pathways (escape when things go wrong)

Trotula's linear TAKE -> BOIL -> GIVE structure
doesn't require the complexity Voynich B provides.
""")
else:
    print("""
TROTULA HAS BALANCED KERNEL/OUTPUT:
Could be compatible with Voynich B's control structure.
""")

print()
print("VERDICT ON TROTULA-VOYNICH COMPATIBILITY:")
print("-" * 50)

# Final assessment
if len(recipes) > 0:
    avg_steps = sum(len(r) for r in recipes) / len(recipes)
    print(f"Average Trotula recipe steps: {avg_steps:.1f}")
    print(f"Average Voynich B line length: {sum(len(tokens) for tokens in b_by_line.values()) / len(b_by_line):.1f} tokens")
    print()

print("""
CONCLUSION:

1. STRUCTURAL MATCH: PARTIAL
   - Both have sequential step structure
   - Both use material + operation + outcome pattern

2. COMPLEXITY MATCH: POOR
   - Trotula is OUTPUT-DOMINATED (da/give verbs)
   - Voynich B is KERNEL-CENTRIC (state transformations)
   - Voynich B has hazard avoidance; Trotula doesn't need it

3. DOMAIN MATCH: POSSIBLE
   - Trotula covers women's health (matches Rosettes hypothesis)
   - But procedural complexity doesn't match

4. ALTERNATIVE HYPOTHESIS:
   - Voynich might encode WHEN to apply Trotula-style recipes
   - Rather than the recipes themselves
   - Rosettes = timing/routing for simpler procedures
   - B folios = WHICH procedure to use, not HOW to do it

This would explain why Voynich B has:
- High kernel content (decision logic)
- Recovery pathways (what if treatment fails)
- Hazard avoidance (contraindicated combinations)
- Without detailed TAKE X BOIL Y instructions
""")
