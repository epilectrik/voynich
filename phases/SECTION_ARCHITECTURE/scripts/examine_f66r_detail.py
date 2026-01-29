"""Examine f66r placement codes in detail."""
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()
all_tokens = list(tx.all(h_only=True))

# Get f66r tokens
f66r = [t for t in all_tokens if t.folio == 'f66r']

print('f66r placement breakdown:')
placement_counts = Counter(t.placement for t in f66r)
for p, c in placement_counts.most_common():
    print(f"  {p}: {c}")
print()

# Show tokens by placement type
print('=== R-placement tokens (first 30) ===')
r_tokens = [t for t in f66r if t.placement.startswith('R')]
for t in r_tokens[:30]:
    print(f"  line={t.line:>5}  placement={t.placement:>3}  word={t.word}")

print()
print('=== M-placement tokens (all) ===')
m_tokens = [t for t in f66r if t.placement == 'M']
for t in m_tokens:
    print(f"  line={t.line:>5}  placement={t.placement:>3}  word={t.word}")

print()
print('=== W-placement tokens (all) ===')
w_tokens = [t for t in f66r if t.placement == 'W']
for t in w_tokens:
    print(f"  line={t.line:>5}  placement={t.placement:>3}  word={t.word}")

# Check what other folios have R-placement
print()
print('=== Which folios have R-placement? (top 20) ===')
r_by_folio = defaultdict(int)
for t in all_tokens:
    if t.placement.startswith('R'):
        r_by_folio[t.folio] += 1

for folio, count in sorted(r_by_folio.items(), key=lambda x: -x[1])[:20]:
    print(f"  {folio}: {count}")

# Also check: what sections are these R-placement folios in?
print()
print('=== R-placement folios by section ===')
r_folios = set(r_by_folio.keys())
for folio in sorted(r_folios):
    section = next((t.section for t in all_tokens if t.folio == folio), '?')
    lang = next((t.language for t in all_tokens if t.folio == folio), '?')
    print(f"  {folio}: section={section}, language={lang}, R-tokens={r_by_folio[folio]}")
