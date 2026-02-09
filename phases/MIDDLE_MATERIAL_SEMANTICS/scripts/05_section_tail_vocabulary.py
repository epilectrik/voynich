#!/usr/bin/env python3
"""
Test 5: Section-Specific Tail Vocabulary

Question: Does each section have its own tail vocabulary?

Method:
  1. Load Currier B tokens (H transcriber, labels/uncertain excluded)
  2. Extract MIDDLEs via canonical Morphology
  3. Define TAIL middles as those appearing in < 15 folios corpus-wide
  4. For every folio pair, compute Jaccard similarity of tail-middle sets
  5. Compare WITHIN-section vs BETWEEN-section Jaccard distributions
  6. Per-section: count section-exclusive tail middles
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.voynich import Transcript, Morphology

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

tx = Transcript()
morph = Morphology()

TAIL_THRESHOLD = 15  # Appear in fewer than this many folios

# ------------------------------------------------------------------
# Step 1: Collect per-folio MIDDLE sets (Currier B only)
# ------------------------------------------------------------------
folio_middles = defaultdict(set)        # folio -> set of MIDDLEs
folio_section = {}                       # folio -> section
middle_folio_set = defaultdict(set)      # MIDDLE -> set of folios it appears in

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_':
        folio_middles[token.folio].add(m.middle)
        middle_folio_set[m.middle].add(token.folio)
        folio_section[token.folio] = token.section

# ------------------------------------------------------------------
# Step 2: Identify TAIL middles (< TAIL_THRESHOLD folios)
# ------------------------------------------------------------------
tail_middles = {mid for mid, folios in middle_folio_set.items()
                if len(folios) < TAIL_THRESHOLD}

print(f"Total distinct MIDDLEs in Currier B: {len(middle_folio_set)}")
print(f"TAIL MIDDLEs (< {TAIL_THRESHOLD} folios): {len(tail_middles)}")

# ------------------------------------------------------------------
# Step 3: Per-folio TAIL-middle sets (pre-computed for O(1) lookup)
# ------------------------------------------------------------------
folio_tail = {folio: mids & tail_middles for folio, mids in folio_middles.items()}

# Filter to folios that actually have tail middles
folios_with_tail = [f for f, s in folio_tail.items() if len(s) > 0]
print(f"Folios with at least 1 tail MIDDLE: {len(folios_with_tail)}")

# ------------------------------------------------------------------
# Step 4: Pairwise Jaccard similarity
# ------------------------------------------------------------------
within_jaccards = []
between_jaccards = []

for f1, f2 in combinations(folios_with_tail, 2):
    s1 = folio_tail[f1]
    s2 = folio_tail[f2]
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    if union == 0:
        continue
    jacc = intersection / union

    if folio_section[f1] == folio_section[f2]:
        within_jaccards.append(jacc)
    else:
        between_jaccards.append(jacc)

print(f"\nPairwise comparisons:")
print(f"  WITHIN-section pairs:  {len(within_jaccards)}")
print(f"  BETWEEN-section pairs: {len(between_jaccards)}")

# ------------------------------------------------------------------
# Step 5: Statistical comparison
# ------------------------------------------------------------------
mean_within = sum(within_jaccards) / len(within_jaccards) if within_jaccards else 0
mean_between = sum(between_jaccards) / len(between_jaccards) if between_jaccards else 0
ratio = mean_within / mean_between if mean_between > 0 else float('inf')

print(f"\nMean Jaccard WITHIN sections:  {mean_within:.4f}")
print(f"Mean Jaccard BETWEEN sections: {mean_between:.4f}")
print(f"Ratio (within / between):      {ratio:.2f}")

# Mann-Whitney U test (scipy-free implementation)
def mann_whitney_u(x, y):
    """Compute Mann-Whitney U statistic and approximate p-value (normal approx)."""
    nx, ny = len(x), len(y)
    # Combine and rank
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties by averaging)
    ranks = []
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average rank
        for k in range(i, j):
            ranks.append((avg_rank, combined[k][1]))
        i = j

    # Sum ranks for x
    r_x = sum(r for r, g in ranks if g == 'x')
    u_x = r_x - nx * (nx + 1) / 2
    u_y = nx * ny - u_x
    u = min(u_x, u_y)

    # Normal approximation for p-value
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)
    if sigma == 0:
        return u, 1.0
    z = (u - mu) / sigma
    # Two-tailed p-value from z using error function approximation
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return u, p


def cohens_d(x, y):
    """Compute Cohen's d effect size."""
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 0.0
    mean_x = sum(x) / nx
    mean_y = sum(y) / ny
    var_x = sum((v - mean_x) ** 2 for v in x) / (nx - 1)
    var_y = sum((v - mean_y) ** 2 for v in y) / (ny - 1)
    pooled_sd = math.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2))
    if pooled_sd == 0:
        return 0.0
    return (mean_x - mean_y) / pooled_sd


u_stat, p_value = mann_whitney_u(within_jaccards, between_jaccards)
d = cohens_d(within_jaccards, between_jaccards)

print(f"\nMann-Whitney U: {u_stat:.1f}")
print(f"p-value:        {p_value:.2e}")
print(f"Cohen's d:      {d:.3f}")

# ------------------------------------------------------------------
# Step 6: Per-section statistics
# ------------------------------------------------------------------
sections = sorted(set(folio_section.values()))
print(f"\nSections found: {sections}")

per_section = {}
for sec in sections:
    sec_folios = [f for f in folios_with_tail if folio_section[f] == sec]
    # Union of tail middles across all folios in this section
    sec_tail = set()
    for f in sec_folios:
        sec_tail |= folio_tail[f]

    # Section-exclusive: tail middles that appear ONLY in folios of this section
    exclusive = set()
    for mid in sec_tail:
        mid_sections = {folio_section[f] for f in middle_folio_set[mid] if f in folio_section}
        if mid_sections == {sec}:
            exclusive.add(mid)

    pct_exclusive = (len(exclusive) / len(sec_tail) * 100) if sec_tail else 0

    per_section[sec] = {
        "n_folios": len(sec_folios),
        "n_tail_middles": len(sec_tail),
        "n_section_exclusive": len(exclusive),
        "pct_exclusive": round(pct_exclusive, 1)
    }

    print(f"  {sec}: {len(sec_folios)} folios, {len(sec_tail)} tail MIDDLEs, "
          f"{len(exclusive)} exclusive ({pct_exclusive:.1f}%)")

# ------------------------------------------------------------------
# Step 7: Verdict
# ------------------------------------------------------------------
# SUPPORTED if:
#   - within > between with p < 0.05
#   - ratio > 1.5 or Cohen's d > 0.3 (small-medium effect)
#   - at least some sections have notable exclusive vocabulary
avg_pct_exclusive = (sum(s["pct_exclusive"] for s in per_section.values())
                     / len(per_section)) if per_section else 0

supported = (p_value < 0.05
             and mean_within > mean_between
             and (ratio > 1.5 or d > 0.3))

verdict = "SUPPORTED" if supported else "NOT_SUPPORTED"

notes_parts = []
if p_value < 0.05:
    notes_parts.append(f"significant at p={p_value:.2e}")
else:
    notes_parts.append(f"not significant (p={p_value:.2e})")
notes_parts.append(f"within/between ratio={ratio:.2f}")
notes_parts.append(f"Cohen's d={d:.3f}")
notes_parts.append(f"avg section-exclusive={avg_pct_exclusive:.1f}%")

notes = "; ".join(notes_parts)

print(f"\nVerdict: {verdict}")
print(f"Notes: {notes}")

# ------------------------------------------------------------------
# Step 8: Save results
# ------------------------------------------------------------------
output = {
    "test": "Section-Specific Tail Vocabulary",
    "n_tail_middles": len(tail_middles),
    "n_sections": len(sections),
    "mean_within_jaccard": round(mean_within, 6),
    "mean_between_jaccard": round(mean_between, 6),
    "within_over_between_ratio": round(ratio, 4),
    "mann_whitney_u": round(u_stat, 1),
    "p_value": p_value,
    "effect_size_d": round(d, 4),
    "per_section": per_section,
    "verdict": verdict,
    "notes": notes
}

out_path = results_dir / "section_tail_vocabulary.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to {out_path}")
