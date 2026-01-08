"""
Test: Is Currier A documenting error states or hazard conditions?

If A documents errors, the B-operational tokens (chedy, shedy, etc.)
that appear rarely in A might mark hazard-relevant entries.
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# B-operational tokens that appear in forbidden transitions
# and are rare in A (potential "hazard markers")
HAZARD_TOKENS = ['chedy', 'shedy', 'he', 'ee', 'c', 't']

# Tokens involved in forbidden transitions that DO appear in A
FORBIDDEN_RELEVANT = ['aiin', 'al', 'ar', 'chedy', 'chey', 'chol', 'dal',
                      'dy', 'l', 'o', 'or', 'r', 'shedy', 'shey', 't']

# Load data grouped by entry (folio + line)
entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                line_num = parts[11].strip('"').strip()

                if word:
                    key = f"{folio}_{line_num}"
                    entries[key]['tokens'].append(word)
                    entries[key]['section'] = section
                    entries[key]['folio'] = folio

print("=" * 70)
print("ERROR STATE HYPOTHESIS TEST")
print("=" * 70)

# Find entries containing hazard tokens
print(f"\n### ENTRIES CONTAINING B-OPERATIONAL TOKENS (rare in A)")
print("-" * 70)

hazard_entries = []
for entry_id, data in entries.items():
    hazard_in_entry = [t for t in data['tokens'] if t in HAZARD_TOKENS]
    if hazard_in_entry:
        hazard_entries.append({
            'id': entry_id,
            'tokens': data['tokens'],
            'section': data['section'],
            'folio': data['folio'],
            'hazard_tokens': hazard_in_entry
        })

print(f"\nEntries with hazard tokens: {len(hazard_entries)} / {len(entries)} ({100*len(hazard_entries)/len(entries):.1f}%)")

# Show them
print("\nHazard-containing entries:")
for e in hazard_entries[:20]:
    print(f"  {e['folio']} ({e['section']}): {' '.join(e['tokens'])}")
    print(f"    Hazard tokens: {e['hazard_tokens']}")

# Section distribution of hazard entries
print(f"\n### SECTION DISTRIBUTION OF HAZARD ENTRIES")
print("-" * 70)

hazard_by_section = Counter(e['section'] for e in hazard_entries)
all_by_section = Counter(data['section'] for data in entries.values())

print(f"\n{'Section':<10} {'Hazard':>10} {'Total':>10} {'Rate':>10}")
print("-" * 45)
for section in ['H', 'P', 'T']:
    hz = hazard_by_section.get(section, 0)
    total = all_by_section.get(section, 0)
    rate = 100 * hz / total if total else 0
    print(f"{section:<10} {hz:>10} {total:>10} {rate:>9.1f}%")

# Compare structure: are hazard entries different from normal entries?
print(f"\n### STRUCTURAL COMPARISON: HAZARD vs NORMAL ENTRIES")
print("-" * 70)

hazard_lens = [len(e['tokens']) for e in hazard_entries]
normal_lens = [len(data['tokens']) for data in entries.values()
               if not any(t in HAZARD_TOKENS for t in data['tokens'])]

avg_hazard = sum(hazard_lens) / len(hazard_lens) if hazard_lens else 0
avg_normal = sum(normal_lens) / len(normal_lens) if normal_lens else 0

print(f"\nAverage entry length:")
print(f"  Hazard entries: {avg_hazard:.1f} tokens")
print(f"  Normal entries: {avg_normal:.1f} tokens")

# Check for repetition in hazard entries
def has_repetition(tokens):
    n = len(tokens)
    if n < 4:
        return False
    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                if all(tokens[i*block_size:(i+1)*block_size] == block for i in range(1, count)):
                    return True
    return False

hazard_rep = sum(1 for e in hazard_entries if has_repetition(e['tokens']))
normal_entries_list = [data for data in entries.values()
                       if not any(t in HAZARD_TOKENS for t in data['tokens'])]
normal_rep = sum(1 for data in normal_entries_list if has_repetition(data['tokens']))

print(f"\nRepetition rate:")
print(f"  Hazard entries: {100*hazard_rep/len(hazard_entries) if hazard_entries else 0:.1f}%")
print(f"  Normal entries: {100*normal_rep/len(normal_entries_list) if normal_entries_list else 0:.1f}%")

# Check if hazard entries are clustered in specific folios
print(f"\n### FOLIO DISTRIBUTION OF HAZARD ENTRIES")
print("-" * 70)

hazard_by_folio = Counter(e['folio'] for e in hazard_entries)
print(f"\nFolios with hazard entries: {len(hazard_by_folio)}")
print(f"\nMost hazard-dense folios:")
for folio, count in hazard_by_folio.most_common(10):
    total_in_folio = sum(1 for data in entries.values() if data['folio'] == folio)
    print(f"  {folio}: {count}/{total_in_folio} entries ({100*count/total_in_folio:.0f}%)")

# Now check the broader question: do forbidden-relevant tokens mark special entries?
print(f"\n\n### BROADER TEST: FORBIDDEN-RELEVANT TOKEN ENTRIES")
print("-" * 70)

forbidden_entries = []
for entry_id, data in entries.items():
    forbidden_in_entry = [t for t in data['tokens'] if t in FORBIDDEN_RELEVANT]
    if forbidden_in_entry:
        forbidden_entries.append({
            'id': entry_id,
            'tokens': data['tokens'],
            'section': data['section'],
            'folio': data['folio'],
            'forbidden_tokens': forbidden_in_entry
        })

print(f"\nEntries with ANY forbidden-relevant token: {len(forbidden_entries)} / {len(entries)} ({100*len(forbidden_entries)/len(entries):.1f}%)")

# These are common tokens like 'aiin', 'chol', 'dy' - so many entries have them
# The question is: do entries with MULTIPLE forbidden-relevant tokens show patterns?

multi_forbidden = [e for e in forbidden_entries if len(set(e['forbidden_tokens'])) >= 2]
print(f"Entries with 2+ DIFFERENT forbidden-relevant tokens: {len(multi_forbidden)}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if len(hazard_entries) < 20:
    print(f"""
FINDING: Only {len(hazard_entries)} entries contain B-operational tokens.

These are too FEW to be systematic error documentation.
If A documented errors, we'd expect many more entries with these tokens.

The rare B-operational tokens in A appear to be:
- Incidental vocabulary overlap
- Not structurally special
- Not clustered meaningfully

VERDICT: Error documentation hypothesis NOT SUPPORTED.
""")
else:
    print(f"""
FINDING: {len(hazard_entries)} entries contain B-operational tokens.

This warrants further investigation:
- Check if these entries have special structural properties
- Check if they cluster in specific manuscript regions
- Compare their section distribution to baseline
""")
