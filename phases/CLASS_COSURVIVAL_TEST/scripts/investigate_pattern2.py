"""Investigate the 19 A records that reduce to only 6 classes."""
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Load survivor data
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'a_record_survivors.json', 'r') as f:
    data = json.load(f)

# Find Pattern 2 records (only 6 classes survive)
pattern2_records = [r for r in data['records'] if r['surviving_class_count'] == 6]

print("=" * 70)
print(f"PATTERN 2: {len(pattern2_records)} A RECORDS WITH ONLY 6 CLASSES")
print("=" * 70)

print("\n--- BASIC INFO ---")
for r in pattern2_records:
    print(f"{r['a_record']:15} | MIDDLEs: {r['a_middles']} | AZC folios: {len(r['matching_azc_folios'])} | Legal MIDDLEs: {r['legal_middle_count']}")

# Check what AZC folios they match
print("\n--- AZC FOLIO MATCHING ---")
azc_folio_counts = {}
for r in pattern2_records:
    for f in r['matching_azc_folios']:
        azc_folio_counts[f] = azc_folio_counts.get(f, 0) + 1

print(f"AZC folios matched by these records:")
for folio, count in sorted(azc_folio_counts.items(), key=lambda x: -x[1]):
    print(f"  {folio}: {count} records")

# Check what MIDDLEs they have
print("\n--- MIDDLE ANALYSIS ---")
all_middles = set()
for r in pattern2_records:
    all_middles.update(r['a_middles'])
print(f"Unique MIDDLEs across all 19 records: {len(all_middles)}")
print(f"MIDDLEs: {sorted(all_middles)}")

# Load transcript to see actual tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A']

print("\n--- ACTUAL A RECORD CONTENT ---")
for r in pattern2_records[:5]:  # First 5
    folio, line = r['a_record'].split(':')
    tokens = df_a[(df_a['folio'] == folio) & (df_a['line_number'].astype(str) == line)]['word'].tolist()
    print(f"\n{r['a_record']}:")
    print(f"  Tokens: {tokens}")
    print(f"  MIDDLEs: {r['a_middles']}")
    print(f"  AZC matches: {r['matching_azc_folios']}")

# Check folio distribution
print("\n--- FOLIO DISTRIBUTION ---")
folios = [r['a_record'].split(':')[0] for r in pattern2_records]
from collections import Counter
folio_counts = Counter(folios)
print(f"By folio:")
for folio, count in folio_counts.most_common():
    print(f"  {folio}: {count} records")

# Compare to normal Pattern 1 records
print("\n--- COMPARISON TO PATTERN 1 (normal) ---")
pattern1_records = [r for r in data['records'] if r['surviving_class_count'] == 49]

p1_avg_middles = sum(len(r['a_middles']) for r in pattern1_records) / len(pattern1_records)
p2_avg_middles = sum(len(r['a_middles']) for r in pattern2_records) / len(pattern2_records)

p1_avg_azc = sum(len(r['matching_azc_folios']) for r in pattern1_records) / len(pattern1_records)
p2_avg_azc = sum(len(r['matching_azc_folios']) for r in pattern2_records) / len(pattern2_records)

p1_avg_legal = sum(r['legal_middle_count'] for r in pattern1_records) / len(pattern1_records)
p2_avg_legal = sum(r['legal_middle_count'] for r in pattern2_records) / len(pattern2_records)

print(f"{'Metric':<25} {'Pattern 1 (49 cls)':<20} {'Pattern 2 (6 cls)':<20}")
print("-" * 65)
print(f"{'Avg MIDDLEs in A record':<25} {p1_avg_middles:<20.1f} {p2_avg_middles:<20.1f}")
print(f"{'Avg AZC folios matched':<25} {p1_avg_azc:<20.1f} {p2_avg_azc:<20.1f}")
print(f"{'Avg legal MIDDLEs':<25} {p1_avg_legal:<20.1f} {p2_avg_legal:<20.1f}")

# What's special - do they match NO AZC folios?
print("\n--- KEY FINDING ---")
zero_azc = [r for r in pattern2_records if len(r['matching_azc_folios']) == 0]
print(f"Records matching ZERO AZC folios: {len(zero_azc)}")
if zero_azc:
    print("These A records have MIDDLEs not found in ANY AZC folio!")
    for r in zero_azc[:5]:
        print(f"  {r['a_record']}: MIDDLEs = {r['a_middles']}")
