"""Test if AZC-matching tokens are more frequent than non-matching."""
from apps.azc_folio_animator.core.folio_loader import FolioLoader
from collections import Counter

loader = FolioLoader()
loader.load()

# Build AZC vocabulary
azc_ids = loader.get_azc_folio_ids()
azc_vocab = set()
for azc_id in azc_ids:
    azc_folio = loader.get_folio(azc_id.lstrip('f'))
    if azc_folio:
        azc_vocab.update(t.text for t in azc_folio.tokens)

print(f"AZC vocabulary size: {len(azc_vocab)}")

# Count token frequencies across several Currier A folios
test_folios = ['1r', '1v', '2r', '3r', '4r', '5r', '10r', '15r', '20r']
all_tokens = []

for fid in test_folios:
    folio = loader.get_folio(fid)
    if folio:
        all_tokens.extend(t.text for t in folio.tokens)

freq = Counter(all_tokens)
total_tokens = len(all_tokens)
total_types = len(freq)

# Split by AZC membership
azc_match_tokens = 0
azc_match_types = 0
non_match_tokens = 0
non_match_types = 0

for token, count in freq.items():
    if token in azc_vocab:
        azc_match_tokens += count
        azc_match_types += 1
    else:
        non_match_tokens += count
        non_match_types += 1

print(f"\nTotal tokens: {total_tokens}")
print(f"Total types: {total_types}")

print(f"\n=== By TYPE (unique tokens) ===")
print(f"AZC-matching types: {azc_match_types}/{total_types} ({100*azc_match_types/total_types:.1f}%)")
print(f"Non-matching types: {non_match_types}/{total_types} ({100*non_match_types/total_types:.1f}%)")

print(f"\n=== By TOKEN (occurrences) ===")
print(f"AZC-matching tokens: {azc_match_tokens}/{total_tokens} ({100*azc_match_tokens/total_tokens:.1f}%)")
print(f"Non-matching tokens: {non_match_tokens}/{total_tokens} ({100*non_match_tokens/total_tokens:.1f}%)")

# Show most frequent non-matching tokens
print(f"\n=== Most frequent NON-matching tokens ===")
non_match_freq = [(t, c) for t, c in freq.most_common() if t not in azc_vocab]
for t, c in non_match_freq[:15]:
    print(f"  {t}: {c}")

# Show most frequent matching tokens
print(f"\n=== Most frequent MATCHING tokens ===")
match_freq = [(t, c) for t, c in freq.most_common() if t in azc_vocab]
for t, c in match_freq[:15]:
    print(f"  {t}: {c}")
