"""
T5: P-Text to Diagram Relationship

Question: What is the relationship between P-text (paragraph text above diagrams)
and the adjacent diagram text on the same AZC folio?

Background: P-text has been validated as linguistically Currier A, not AZC.
This test explores whether P-text on a given folio relates to the diagram text.

Method:
1. For AZC folios with both P-text and diagram text:
   - Compute vocabulary overlap (MIDDLEs)
   - Compare PREFIX profiles
   - Test: is P-text vocabulary PREDICTIVE of diagram vocabulary?
2. Compare P-text to Currier A sections to confirm A-like behavior
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Collect P-text vs diagram text by folio
print("Collecting P-text and diagram text by folio...")

ptext_by_folio = defaultdict(list)
diagram_by_folio = defaultdict(list)

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    placement = getattr(token, 'placement', '')

    if placement.startswith('P'):
        ptext_by_folio[token.folio].append(w)
    elif placement:
        diagram_by_folio[token.folio].append(w)

# Folios with both P-text and diagram text
both_folios = set(ptext_by_folio.keys()) & set(diagram_by_folio.keys())

print(f"Folios with P-text: {len(ptext_by_folio)}")
print(f"Folios with diagram text: {len(diagram_by_folio)}")
print(f"Folios with BOTH: {len(both_folios)}")

if len(both_folios) == 0:
    print("\nNo folios have both P-text and diagram text. Exiting.")
    results = {'verdict': 'NO_OVERLAP_FOLIOS', 'both_count': 0}
    out_path = Path(__file__).parent.parent / 'results' / 't5_ptext_relation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    sys.exit(0)

# Analyze each folio with both types
print("\n" + "="*60)
print("P-TEXT vs DIAGRAM VOCABULARY BY FOLIO")
print("="*60)

results = {
    'folio_stats': {},
    'summary': {},
}

jaccard_scores = []
ptext_total = 0
diagram_total = 0

for folio in sorted(both_folios):
    ptext_tokens = ptext_by_folio[folio]
    diagram_tokens = diagram_by_folio[folio]

    # Extract MIDDLEs
    ptext_middles = set()
    for w in ptext_tokens:
        m = morph.extract(w)
        if m.middle:
            ptext_middles.add(m.middle)

    diagram_middles = set()
    for w in diagram_tokens:
        m = morph.extract(w)
        if m.middle:
            diagram_middles.add(m.middle)

    # Overlap metrics
    intersection = ptext_middles & diagram_middles
    union = ptext_middles | diagram_middles
    jaccard = len(intersection) / len(union) if union else 0

    results['folio_stats'][folio] = {
        'ptext_tokens': len(ptext_tokens),
        'diagram_tokens': len(diagram_tokens),
        'ptext_middles': len(ptext_middles),
        'diagram_middles': len(diagram_middles),
        'overlap_middles': len(intersection),
        'jaccard': round(jaccard, 3),
    }

    jaccard_scores.append(jaccard)
    ptext_total += len(ptext_tokens)
    diagram_total += len(diagram_tokens)

    print(f"{folio}: P={len(ptext_tokens):3}, D={len(diagram_tokens):3} | "
          f"MID: P={len(ptext_middles):2}, D={len(diagram_middles):2}, "
          f"overlap={len(intersection):2} | Jaccard={jaccard:.3f}")

# Summary
print("\n" + "="*60)
print("P-TEXT vs DIAGRAM SUMMARY")
print("="*60)

print(f"Total P-text tokens: {ptext_total}")
print(f"Total diagram tokens: {diagram_total}")
print(f"Mean Jaccard overlap: {np.mean(jaccard_scores):.3f} (std={np.std(jaccard_scores):.3f})")

# Compare to A vs B vocabulary overlap for reference
print("\n" + "="*60)
print("COMPARISON TO A-B BASELINE")
print("="*60)

# Collect A and B vocabulary for baseline
a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_middles.add(m.middle)

b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            b_middles.add(m.middle)

# P-text vocabulary compared to A and B
all_ptext_middles = set()
for folio in ptext_by_folio:
    for w in ptext_by_folio[folio]:
        m = morph.extract(w)
        if m.middle:
            all_ptext_middles.add(m.middle)

ptext_a_overlap = len(all_ptext_middles & a_middles) / len(all_ptext_middles) if all_ptext_middles else 0
ptext_b_overlap = len(all_ptext_middles & b_middles) / len(all_ptext_middles) if all_ptext_middles else 0

print(f"P-text MIDDLEs found in Currier A: {100*ptext_a_overlap:.1f}%")
print(f"P-text MIDDLEs found in Currier B: {100*ptext_b_overlap:.1f}%")

# P-text PREFIX profile comparison
print("\n" + "="*60)
print("P-TEXT PREFIX PROFILE")
print("="*60)

PREFIXES = ['qo', 'ch', 'sh', 'ol', 'or', 'ok', 'ot', 'd', 's', 'o']

ptext_prefixes = Counter()
diagram_prefixes = Counter()
a_prefixes = Counter()

for folio in ptext_by_folio:
    for w in ptext_by_folio[folio]:
        m = morph.extract(w)
        if m.prefix:
            ptext_prefixes[m.prefix] += 1

for folio in diagram_by_folio:
    for w in diagram_by_folio[folio]:
        m = morph.extract(w)
        if m.prefix:
            diagram_prefixes[m.prefix] += 1

for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.prefix:
            a_prefixes[m.prefix] += 1

def profile_vec(counter, prefixes):
    total = sum(counter.values())
    return [100.0 * counter.get(p, 0) / total if total > 0 else 0 for p in prefixes]

ptext_profile = profile_vec(ptext_prefixes, PREFIXES)
diagram_profile = profile_vec(diagram_prefixes, PREFIXES)
a_profile = profile_vec(a_prefixes, PREFIXES)

print(f"\n{'PREFIX':<6} {'P-text':>10} {'Diagram':>10} {'Currier A':>10}")
print("-" * 40)
for i, p in enumerate(PREFIXES):
    print(f"{p:<6} {ptext_profile[i]:>9.1f}% {diagram_profile[i]:>9.1f}% {a_profile[i]:>9.1f}%")

# Cosine similarity
def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

ptext_a_sim = cosine_sim(ptext_profile, a_profile)
ptext_diagram_sim = cosine_sim(ptext_profile, diagram_profile)

print(f"\nP-text to Currier A similarity: {ptext_a_sim:.3f}")
print(f"P-text to AZC diagram similarity: {ptext_diagram_sim:.3f}")

# Save results
results['summary'] = {
    'folios_with_both': len(both_folios),
    'total_ptext_tokens': ptext_total,
    'total_diagram_tokens': diagram_total,
    'mean_jaccard': float(np.mean(jaccard_scores)),
    'std_jaccard': float(np.std(jaccard_scores)),
    'ptext_a_overlap': float(ptext_a_overlap),
    'ptext_b_overlap': float(ptext_b_overlap),
    'ptext_a_prefix_sim': float(ptext_a_sim),
    'ptext_diagram_prefix_sim': float(ptext_diagram_sim),
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if ptext_a_sim > ptext_diagram_sim + 0.05:
    verdict = "PTEXT_IS_CURRIER_A"
    print(f"P-text is more similar to Currier A ({ptext_a_sim:.3f}) than to diagram text ({ptext_diagram_sim:.3f})")
elif np.mean(jaccard_scores) > 0.3:
    verdict = "PTEXT_DIAGRAM_RELATED"
    print(f"P-text shows substantial overlap with diagram text (mean Jaccard={np.mean(jaccard_scores):.3f})")
else:
    verdict = "PTEXT_DIAGRAM_INDEPENDENT"
    print(f"P-text vocabulary is largely independent of diagram text")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't5_ptext_relation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")
