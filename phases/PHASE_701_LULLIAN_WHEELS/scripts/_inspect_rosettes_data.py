"""Inspect what placement codes / data we have for the rosettes foldout (f85v + f86r)."""
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "C:/git/voynich")
from scripts.voynich import Transcript

tx = Transcript()

# The rosettes foldout is f85v + f86r (folio numbering varies — also referenced as f86v3 in some splits)
target_folios = ["f85v", "f86r", "f86v3", "f85v1", "f85v2", "f86r1", "f86r2"]

print("Inspecting rosettes foldout folios...")
for folio in target_folios:
    placements = Counter()
    sample_tokens = []
    for t in tx.all(h_only=True):
        if t.folio != folio:
            continue
        if not t.word or t.is_uncertain:
            continue
        placements[t.placement] += 1
        if len(sample_tokens) < 5:
            sample_tokens.append((t.word, t.placement))
    if placements:
        print(f"\n{folio}:")
        print(f"  Total tokens: {sum(placements.values())}")
        print(f"  Placements: {dict(placements)}")
        print(f"  Sample: {sample_tokens}")

# Show ALL folios containing f85 or f86 in name
print("\n\nAll matching folios with 'f85' or 'f86':")
all_folios = set()
for t in tx.all(h_only=True):
    if "f85" in t.folio or "f86" in t.folio:
        all_folios.add(t.folio)
for f in sorted(all_folios):
    print(f"  {f}")
