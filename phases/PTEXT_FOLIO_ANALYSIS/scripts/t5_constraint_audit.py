#!/usr/bin/env python3
"""
Test 5: Constraint Reframing Audit

Questions:
- Which constraints mention "P-zone" or "P-placement" and need reframing?
- How should C492 (ct PREFIX exclusivity) be understood given P-text is A text?
- How should C486 (P-zone correlates with high-escape) be reframed?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
import re

# Search context directory for P-related mentions
context_dir = Path('C:/git/voynich/context')
claims_dir = context_dir / 'CLAIMS'

print("=" * 70)
print("TEST 5: CONSTRAINT REFRAMING AUDIT")
print("=" * 70)
print()

# 1. Find all P-zone/P-placement mentions
print("1. FILES MENTIONING 'P-zone', 'P-placement', 'P placement'")
print("-" * 50)

p_mentions = []

def search_files(directory, patterns):
    """Search files for patterns."""
    results = []
    for f in directory.rglob('*.md'):
        try:
            content = f.read_text(encoding='utf-8')
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results.append(f)
                    break
        except:
            pass
    return results

patterns = [r'P[- ]?zone', r'P[- ]?placement', r'P[- ]?position']
files_with_p = search_files(context_dir, patterns)

for f in sorted(set(files_with_p)):
    rel = f.relative_to(context_dir)
    print(f"  {rel}")
print()

# 2. Specific constraints to audit
print("2. SPECIFIC CONSTRAINTS TO AUDIT")
print("-" * 50)

constraints_to_check = {
    'C492': 'ct PREFIX exclusivity to P-placement',
    'C486': 'P-zone vocabulary correlates with high-escape B',
    'C758': 'P-text Currier A identity',
    'C443': 'AZC position types',
}

for cid, desc in constraints_to_check.items():
    # Search for constraint file
    matches = list(claims_dir.glob(f'*{cid}*.md'))
    if matches:
        print(f"{cid}: {desc}")
        print(f"  File: {matches[0].name}")
        # Read first few lines
        content = matches[0].read_text(encoding='utf-8')[:500]
        print(f"  Status: EXISTS")
    else:
        print(f"{cid}: {desc}")
        print(f"  Status: NOT FOUND (may need creation)")
    print()

# 3. Reframing recommendations
print("3. REFRAMING RECOMMENDATIONS")
print("-" * 50)
print("""
Based on phase findings, the following reframings are needed:

A. C492 (ct PREFIX exclusivity to P-placement):
   OLD: "ct PREFIX appears only in P-zone of AZC diagrams"
   ISSUE: P is not a diagram zone - it's paragraph text (Currier A)
   NEW: "ct PREFIX appears only in Currier A paragraph text on AZC folios"
   IMPLICATION: ct is a marker for A-type paragraph text, not a positional marker

B. C486 (P-zone vocabulary correlates with high-escape B):
   OLD: "Tokens in P-zone correlate with high-escape B behavior"
   ISSUE: P is Currier A text, not a diagram position
   NEW: "Currier A paragraph vocabulary (on AZC folios) correlates with high-escape B"
   IMPLICATION: This actually STRENGTHENS C486 - it's about vocabulary subset, not position

C. C443 (AZC position types):
   Already audited and fixed in previous session.
   Verified: P removed from diagram position list.

D. C758 (P-text Currier A identity):
   This constraint is CORRECT and documents the key finding.
   No reframing needed - this is the authoritative source.
""")

# 4. New constraint recommendations
print("4. NEW CONSTRAINT RECOMMENDATIONS")
print("-" * 50)
print("""
Based on phase findings, the following NEW constraints should be documented:

A. P-TEXT TRANSMISSION ADVANTAGE:
   "P-text MIDDLEs have 76.7% transmission rate to Currier B,
    vs 39.9% for general Currier A vocabulary."
   TIER: 2 (statistical fact)

B. P-TEXT SAME-FOLIO CORRELATION:
   "P-text has 0.195 mean Jaccard overlap with same-folio AZC diagram,
    vs 0.040 baseline with cross-folio diagrams."
   TIER: 2 (statistical fact)
   IMPLICATION: P-text content is related to accompanying diagram

C. P-TEXT FOLIO CLUSTERING:
   "P-text appears on 9 specific AZC folios (f65v-f70r2 range),
    all in A/C family, none in Zodiac section."
   TIER: 2 (observation)

D. f65v ANOMALY:
   "Folio f65v is 100% P-text with no diagram content,
    unique among AZC folios."
   TIER: 2 (observation)
""")

# 5. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Constraint Audit Results:

1. REFRAMING NEEDED:
   - C492: Reframe from "P-zone" to "A paragraph text on AZC folios"
   - C486: Reframe from "P-zone vocabulary" to "A paragraph vocabulary"

2. ALREADY CORRECT:
   - C758: Documents P-text as Currier A (authoritative)
   - C443: Already fixed in previous audit

3. NEW CONSTRAINTS TO ADD:
   - P-text transmission advantage (76.7% vs 39.9%)
   - P-text same-folio correlation (0.195 vs 0.040)
   - P-text folio clustering (9 folios, f65v-f70r2)
   - f65v anomaly (100% P-text, no diagram)

4. KEY INSIGHT:
   P-text is not a diagram position but a Currier A paragraph subset
   that appears on specific AZC folios and has privileged transmission
   to Currier B execution.
""")
