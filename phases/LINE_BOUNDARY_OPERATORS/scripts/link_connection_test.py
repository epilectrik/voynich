"""
LINK CONNECTION TEST

From BCSC:
- LINK marks boundary between monitoring and intervention
- LINK is followed by ENERGY_OPERATOR (1.15x enrichment)
- LINK is spatially uniform (no positional clustering)

Question: Are L-compound tokens the post-LINK energy operations?

Test:
1. Identify LINK tokens
2. Check if L-compound appears after LINK
3. Check position relationship
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("LINK CONNECTION TEST")
print("=" * 70)

# =============================================================================
# STEP 1: Load class mappings
# =============================================================================
print("\n[Step 1] Loading class mappings...")

try:
    with open('data/class_token_map.json', 'r') as f:
        class_token_map = json.load(f)
    print(f"  Loaded class_token_map.json: {len(class_token_map)} classes")

    # Find LINK class
    link_tokens = set()
    for cls, tokens in class_token_map.items():
        if 'LINK' in cls.upper():
            link_tokens.update(tokens)
            print(f"  Found LINK class '{cls}': {len(tokens)} tokens")

    if not link_tokens:
        print("  No explicit LINK class found in class_token_map")
        print("  Checking all classes...")
        for cls in sorted(class_token_map.keys()):
            print(f"    {cls}: {len(class_token_map[cls])} tokens")

except Exception as e:
    print(f"  Could not load class_token_map: {e}")
    class_token_map = None

# =============================================================================
# STEP 2: Try canonical_grammar.json
# =============================================================================
print("\n[Step 2] Checking canonical_grammar.json...")

try:
    with open('data/canonical_grammar.json', 'r') as f:
        canonical = json.load(f)

    # Find LINK tokens
    link_tokens = set()
    for token, info in canonical.items():
        role = info.get('role', '')
        if 'LINK' in role.upper():
            link_tokens.add(token)

    print(f"  LINK tokens found: {len(link_tokens)}")
    if link_tokens:
        print(f"  Examples: {list(link_tokens)[:10]}")

except Exception as e:
    print(f"  Could not load canonical_grammar: {e}")

# =============================================================================
# STEP 3: Alternative - use ol/daiin as potential LINK markers
# =============================================================================
print("\n[Step 3] Checking ol/daiin as potential LINK markers...")

# From C366: LINK is preceded by AUXILIARY/FLOW_OPERATOR, followed by HIGH_IMPACT/ENERGY
# ol and daiin are common CORE_CONTROL tokens that might mark boundaries

b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })

# Check what follows ol and daiin
def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    return middle[0] == 'l' and middle[1] not in 'aeioy'

# Build line sequences
folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    folio_line_tokens[(tok['folio'], tok['line'])].append(tok)

# Check what follows potential LINK tokens (ol, daiin)
potential_link_words = {'ol', 'daiin', 'dain', 'saiin', 'sain'}
followers_of_link = Counter()
followers_general = Counter()

for key, tokens in folio_line_tokens.items():
    for i, tok in enumerate(tokens):
        # Track what follows potential LINK
        if tok['word'] in potential_link_words and i < len(tokens) - 1:
            next_tok = tokens[i + 1]
            if is_l_compound(next_tok['middle']):
                followers_of_link['L-compound'] += 1
            elif next_tok['prefix'] in {'ch', 'sh', 'qo'}:
                followers_of_link['ENERGY-prefix'] += 1
            else:
                followers_of_link['other'] += 1

        # Track general followers
        if i < len(tokens) - 1:
            next_tok = tokens[i + 1]
            if is_l_compound(next_tok['middle']):
                followers_general['L-compound'] += 1
            elif next_tok['prefix'] in {'ch', 'sh', 'qo'}:
                followers_general['ENERGY-prefix'] += 1
            else:
                followers_general['other'] += 1

print(f"\n  What follows potential LINK tokens (ol, daiin, etc.):")
total_link = sum(followers_of_link.values())
for cat, count in followers_of_link.most_common():
    pct = count / total_link * 100 if total_link else 0
    print(f"    {cat}: {count} ({pct:.1f}%)")

print(f"\n  General followers (baseline):")
total_gen = sum(followers_general.values())
for cat, count in followers_general.most_common():
    pct = count / total_gen * 100 if total_gen else 0
    print(f"    {cat}: {count} ({pct:.1f}%)")

# Enrichment
if total_link and total_gen:
    l_after_link = followers_of_link.get('L-compound', 0) / total_link
    l_baseline = followers_general.get('L-compound', 0) / total_gen
    if l_baseline > 0:
        enrichment = l_after_link / l_baseline
        print(f"\n  L-compound enrichment after LINK: {enrichment:.2f}x")

# =============================================================================
# STEP 4: Direct test - position of L-compound relative to ol/daiin
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Position of L-compound relative to ol/daiin in lines")
print("=" * 70)

# In lines with both, which comes first?
l_before_link = 0
link_before_l = 0
lines_with_both = 0

for key, tokens in folio_line_tokens.items():
    has_l = False
    has_link = False
    l_pos = None
    link_pos = None

    for i, tok in enumerate(tokens):
        if is_l_compound(tok['middle']):
            has_l = True
            if l_pos is None:
                l_pos = i
        if tok['word'] in potential_link_words:
            has_link = True
            if link_pos is None:
                link_pos = i

    if has_l and has_link:
        lines_with_both += 1
        if l_pos < link_pos:
            l_before_link += 1
        else:
            link_before_l += 1

print(f"\n  Lines with both L-compound and potential LINK: {lines_with_both}")
if lines_with_both:
    print(f"  L-compound BEFORE link: {l_before_link} ({l_before_link/lines_with_both*100:.1f}%)")
    print(f"  Link BEFORE L-compound: {link_before_l} ({link_before_l/lines_with_both*100:.1f}%)")

# =============================================================================
# STEP 5: Alternative hypothesis - 'l' as LINK marker itself
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Alternative - Is 'l' itself the LINK marker?")
print("=" * 70)

# Hypothesis: the 'l' in L-compound is LINK
# So lch = LINK + ch (linked energy operation)
# This would mean L-compound IS the post-LINK energy

print("""
Hypothesis: 'l' = LINK marker

If true, then:
- lch = LINK + ch = "linked/monitored ch operation"
- lk = LINK + k = "linked/monitored k operation"
- L-compound = energy operation with LINK semantics

This would explain:
- Why L-compound is early (LINK precedes intervention)
- Why L-compound is B-exclusive (LINK is B grammar)
- Why L-compound contains energy roots (LINK followed by ENERGY)
""")

# Test: Do L-compound tokens have LINK-like properties?
# Property 1: Spatially uniform (no positional clustering)

l_positions_by_folio = defaultdict(list)
for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    folio = key[0]
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)
        if is_l_compound(tok['middle']):
            l_positions_by_folio[folio].append(rel_pos)

# Check variance across folios
folio_means = []
for folio, positions in l_positions_by_folio.items():
    if len(positions) >= 5:
        folio_means.append(np.mean(positions))

if folio_means:
    print(f"\n  L-compound position variance across folios:")
    print(f"    Mean of folio means: {np.mean(folio_means):.3f}")
    print(f"    Std of folio means: {np.std(folio_means):.3f}")
    print(f"    (Low std = spatially uniform)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
LINK CONNECTION FINDINGS:

1. EXPLICIT LINK CLASS:
   - Need to verify what tokens are classified as LINK
   - May not be in class_token_map directly

2. POTENTIAL LINK TOKENS (ol, daiin):
   - Check enrichment of L-compound after these tokens
   - If enriched, supports LINK->L-compound sequence

3. POSITION RELATIONSHIP:
   - If LINK comes before L-compound in lines, supports connection
   - If L-compound comes before, weakens connection

4. ALTERNATIVE: 'l' = LINK
   - L-compound could BE the LINK-marked energy operation
   - 'l' as grammatical LINK marker on energy roots
   - Would explain all observed properties

INTERPRETATION:

If 'l' IS the LINK marker, then:
- L-compound is not "followed by LINK"
- L-compound IS "LINK + energy operation"
- This makes L-compound the MONITORING phase of energy work
- While non-l energy (ch, sh, k) is the INTERVENTION phase

This would give us:
- l+ch (lch) = monitored/linked ch operation
- ch = direct ch operation (intervention)
- LATE = output marking after intervention
""")
