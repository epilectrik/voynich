"""Dump full MIDDLE inventory for compound decomposition analysis."""
import json

with open("data/middle_dictionary.json") as f:
    d = json.load(f)

middles = d["middles"]
entries = []
for name, info in middles.items():
    tc = info.get("token_count", 0)
    gloss = info.get("gloss", None)
    kernel = info.get("kernel", None)
    entries.append((tc, name, gloss, kernel))

entries.sort(reverse=True)
print(f"Total MIDDLEs: {len(entries)}")
print()
print(f"{'MIDDLE':14s} {'tokens':>6s} {'kernel':>6s} gloss")
print("-" * 55)
for tc, name, gloss, kernel in entries:
    print(f"{name:14s} {tc:6d} {str(kernel):>6s} {gloss}")
