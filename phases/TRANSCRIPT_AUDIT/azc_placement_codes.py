"""
AZC PLACEMENT CODES ANALYSIS

What placement codes exist for AZC folios and what do they mean?
"""

import os
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Get all unique placements for AZC folios (H track only)
placements_by_folio = defaultdict(Counter)
all_placements = Counter()

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H' and row.get('language') == 'NA':
            folio = row.get('folio', '')
            p = row.get('placement', '')
            placements_by_folio[folio][p] += 1
            all_placements[p] += 1

print("=" * 70)
print("AZC PLACEMENT CODES BY FOLIO")
print("=" * 70)

# Show placement codes per folio
for folio in sorted(placements_by_folio.keys()):
    counts = placements_by_folio[folio]
    codes_str = ', '.join(f"{p}:{c}" for p, c in sorted(counts.items()))
    print(f"\n{folio}:")
    print(f"  {codes_str}")

print("\n" + "=" * 70)
print("ALL PLACEMENT CODES (sorted by frequency)")
print("=" * 70)

for p, c in all_placements.most_common():
    print(f"  {p:<10} {c:>5} tokens")

print("\n" + "=" * 70)
print("PLACEMENT CODE INTERPRETATION")
print("=" * 70)

# Group by prefix
r_codes = {p: c for p, c in all_placements.items() if p.startswith('R')}
s_codes = {p: c for p, c in all_placements.items() if p.startswith('S')}
c_codes = {p: c for p, c in all_placements.items() if p.startswith('C')}
other_codes = {p: c for p, c in all_placements.items()
               if not p.startswith('R') and not p.startswith('S') and not p.startswith('C')}

print(f"\nR-series (rings): {sum(r_codes.values())} tokens")
for p in sorted(r_codes.keys()):
    print(f"  {p}: {r_codes[p]}")

print(f"\nS-series (stars/spokes?): {sum(s_codes.values())} tokens")
for p in sorted(s_codes.keys()):
    print(f"  {p}: {s_codes[p]}")

print(f"\nC-series (circles?): {sum(c_codes.values())} tokens")
for p in sorted(c_codes.keys()):
    print(f"  {p}: {c_codes[p]}")

print(f"\nOther codes: {sum(other_codes.values())} tokens")
for p in sorted(other_codes.keys()):
    print(f"  {p}: {other_codes[p]}")
