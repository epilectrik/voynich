# CCF Extraction - Identify Circular Control Folios
import re
from collections import defaultdict

# Read corpus
folios = defaultdict(list)
with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
            if transcriber != 'H':
                continue
            folio = parts[1]
            # Look for circular folios f67-f73 (known circular/astro section)
            if re.match(r'f(67|68|69|70|71|72|73)', folio):
                folios[folio].append(parts)

print("Circular Folios Found:")
for folio in sorted(folios.keys()):
    print(f"  {folio}: {len(folios[folio])} records")
print(f"\nTotal folios: {len(folios)}")
print(f"Total records: {sum(len(v) for v in folios.values())}")
