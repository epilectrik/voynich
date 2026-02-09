#!/usr/bin/env python3
"""
Deep analysis of s-prefix tokens as apparatus candidates.

From apparatus_candidate_analysis.py:
- sor, sol, sain, saiin, sar all score high
- All AUXILIARY role
- All 0 kernel content
- All highly line-initial

Question: Are these apparatus terms?
- Do they co-occur with specific operations?
- Do they appear in specific positions within procedures?
- Do they cluster with fire operations or phase operations?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

# S-prefix tokens of interest
S_TOKENS = {'sor', 'sol', 'sain', 'saiin', 'sar', 'sair', 's'}

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

print("="*70)
print("S-PREFIX APPARATUS ANALYSIS")
print("="*70)

# Count s-prefix tokens
s_counts = Counter()
for folio in folio_lines:
    for line in folio_lines[folio]:
        for word in folio_lines[folio][line]:
            if word.startswith('s') and not word.startswith('sh'):
                s_counts[word] += 1

print(f"\nS-prefix tokens (not sh-) by count:")
for word, count in s_counts.most_common(20):
    role = token_to_role.get(word, '?')
    print(f"  {word:<15} {count:<8} {role}")

# ============================================================
# CO-OCCURRENCE ANALYSIS
# ============================================================
print(f"\n{'='*70}")
print("CO-OCCURRENCE: What appears on same line as s-prefix?")
print("="*70)

# What tokens appear on the same line as s-prefix tokens?
s_cooccur = Counter()
non_s_cooccur = Counter()

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        has_s = any(w in S_TOKENS for w in words)

        for word in words:
            if word in S_TOKENS:
                continue
            if has_s:
                s_cooccur[word] += 1
            else:
                non_s_cooccur[word] += 1

# Calculate enrichment
print(f"\nTokens enriched on lines WITH s-prefix tokens:")
print(f"{'Token':<15} {'With S':<10} {'Without S':<12} {'Enrichment':<12} {'Role':<20}")
print("-"*75)

enrichments = []
for word in set(s_cooccur.keys()) | set(non_s_cooccur.keys()):
    s_count = s_cooccur.get(word, 0)
    non_s_count = non_s_cooccur.get(word, 0)

    # Normalize by total lines
    total_s_lines = sum(1 for f in folio_lines for l in folio_lines[f]
                        if any(w in S_TOKENS for w in folio_lines[f][l]))
    total_non_s_lines = sum(1 for f in folio_lines for l in folio_lines[f]
                            if not any(w in S_TOKENS for w in folio_lines[f][l]))

    if s_count >= 5 and non_s_count >= 5:
        s_rate = s_count / total_s_lines
        non_s_rate = non_s_count / total_non_s_lines
        if non_s_rate > 0:
            enrichment = s_rate / non_s_rate
            enrichments.append((word, enrichment, s_count, non_s_count))

enrichments.sort(key=lambda x: -x[1])
for word, enrich, s_c, non_s_c in enrichments[:15]:
    role = token_to_role.get(word, '?')
    print(f"{word:<15} {s_c:<10} {non_s_c:<12} {enrich:<12.2f} {role:<20}")

print(f"\nTokens DEPLETED on lines with s-prefix tokens:")
enrichments.sort(key=lambda x: x[1])
for word, enrich, s_c, non_s_c in enrichments[:10]:
    role = token_to_role.get(word, '?')
    print(f"{word:<15} {s_c:<10} {non_s_c:<12} {enrich:<12.2f} {role:<20}")

# ============================================================
# POSITION ANALYSIS: Where does s-prefix appear in line?
# ============================================================
print(f"\n{'='*70}")
print("POSITION ANALYSIS: Line position of s-prefix tokens")
print("="*70)

s_positions = defaultdict(list)

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        n = len(words)
        if n == 0:
            continue

        for i, word in enumerate(words):
            if word in S_TOKENS:
                norm_pos = i / (n - 1) if n > 1 else 0.5
                s_positions[word].append(norm_pos)

print(f"\n{'Token':<15} {'Count':<10} {'Mean Pos':<12} {'Std':<10} {'% at pos 0':<12}")
print("-"*60)

for word in sorted(S_TOKENS):
    if word in s_positions and len(s_positions[word]) >= 5:
        positions = s_positions[word]
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)
        at_zero = sum(1 for p in positions if p == 0) / len(positions)
        print(f"{word:<15} {len(positions):<10} {mean_pos:<12.3f} {std_pos:<10.3f} {100*at_zero:<12.1f}")

# ============================================================
# ROLE DISTRIBUTION: On lines with s-prefix
# ============================================================
print(f"\n{'='*70}")
print("ROLE DISTRIBUTION: On lines with vs without s-prefix")
print("="*70)

s_line_roles = Counter()
non_s_line_roles = Counter()

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        has_s = any(w in S_TOKENS for w in words)

        for word in words:
            role = token_to_role.get(word, 'UNKNOWN')
            if has_s:
                s_line_roles[role] += 1
            else:
                non_s_line_roles[role] += 1

total_s_tokens = sum(s_line_roles.values())
total_non_s_tokens = sum(non_s_line_roles.values())

print(f"\n{'Role':<25} {'With S %':<12} {'Without S %':<12} {'Difference':<12}")
print("-"*60)

for role in set(s_line_roles.keys()) | set(non_s_line_roles.keys()):
    s_pct = 100 * s_line_roles.get(role, 0) / total_s_tokens if total_s_tokens > 0 else 0
    non_s_pct = 100 * non_s_line_roles.get(role, 0) / total_non_s_tokens if total_non_s_tokens > 0 else 0
    diff = s_pct - non_s_pct
    if abs(diff) > 1:
        print(f"{role:<25} {s_pct:<12.1f} {non_s_pct:<12.1f} {diff:+.1f}")

# ============================================================
# SECTION DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("SECTION DISTRIBUTION: Where do s-prefix tokens appear?")
print("="*70)

s_by_section = Counter()
total_by_section = Counter()

for folio in folio_lines:
    section = folio_section.get(folio, 'UNKNOWN')
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        total_by_section[section] += len(words)
        for word in words:
            if word in S_TOKENS:
                s_by_section[section] += 1

print(f"\n{'Section':<15} {'S-tokens':<12} {'Total':<12} {'Rate %':<12}")
print("-"*50)

for section in sorted(total_by_section.keys()):
    s_count = s_by_section.get(section, 0)
    total = total_by_section[section]
    rate = 100 * s_count / total if total > 0 else 0
    print(f"{section:<15} {s_count:<12} {total:<12} {rate:<12.2f}")

# ============================================================
# BRUNSCHWIG HYPOTHESIS
# ============================================================
print(f"\n{'='*70}")
print("BRUNSCHWIG APPARATUS HYPOTHESIS")
print("="*70)

print("""
If s-prefix tokens encode apparatus:

BRUNSCHWIG APPARATUS:
- Alembic (distillation head)
- Cucurbit (vessel body)
- Receiver (collection vessel)
- Furnace types
- Water bath (balneum marie)

S-PREFIX CANDIDATES:
- sor: Very line-initial (78%), could be "vessel" marker
- sol: Also line-initial (54%)
- sain/saiin: Intermediate
- sar: 45% line-initial

EXPECTED BEHAVIOR (if apparatus):
1. Should appear at procedure START (setup)
2. Should NOT encode process state (no kernel)
3. Should be stable across procedures (same equipment)
4. Should co-occur with specific operations

OBSERVED BEHAVIOR:
1. Very line-initial - CONSISTENT with setup
2. Zero kernel content - CONSISTENT
3. Good folio coverage - PARTIALLY CONSISTENT
4. Co-occurrence pattern - NEEDS ANALYSIS

NOTE: This is speculative. S-prefix could also be:
- Flow markers (start of operation)
- Conditional markers (if-then)
- Reference markers (to previous step)
""")

# ============================================================
# D-PREFIX COMPARISON
# ============================================================
print(f"\n{'='*70}")
print("D-PREFIX COMPARISON (Alternative apparatus candidates)")
print("="*70)

D_TOKENS = {'daiin', 'dar', 'dain', 'dair', 'dal', 'dol', 'dor'}

d_counts = Counter()
for folio in folio_lines:
    for line in folio_lines[folio]:
        for word in folio_lines[folio][line]:
            if word in D_TOKENS:
                d_counts[word] += 1

print(f"\nD-prefix token counts:")
for word, count in d_counts.most_common():
    role = token_to_role.get(word, '?')
    print(f"  {word:<15} {count:<8} {role}")

# D-prefix positions
d_positions = defaultdict(list)

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        n = len(words)
        if n == 0:
            continue

        for i, word in enumerate(words):
            if word in D_TOKENS:
                norm_pos = i / (n - 1) if n > 1 else 0.5
                d_positions[word].append(norm_pos)

print(f"\nD-prefix positions:")
print(f"{'Token':<15} {'Count':<10} {'Mean Pos':<12} {'% at pos 0':<12}")
print("-"*50)

for word in sorted(D_TOKENS):
    if word in d_positions and len(d_positions[word]) >= 5:
        positions = d_positions[word]
        mean_pos = np.mean(positions)
        at_zero = sum(1 for p in positions if p == 0) / len(positions)
        print(f"{word:<15} {len(positions):<10} {mean_pos:<12.3f} {100*at_zero:<12.1f}")

print("""
COMPARISON:
- daiin has highest coverage (92%) but later position (0.41)
- dar/dair are mid-line
- D-prefix seems more like FLOW/CONTROL than APPARATUS

S-prefix is more apparatus-like (early position, no kernel).
D-prefix is more control-flow-like (mid-position, structural).
""")
