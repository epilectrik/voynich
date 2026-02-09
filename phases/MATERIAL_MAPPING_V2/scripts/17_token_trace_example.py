"""
17_token_trace_example.py

Trace a specific PRECISION token through A -> AZC -> B pipeline.
Shows concrete example of how position affects legality.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("PRECISION TOKEN TRACE EXAMPLE")
print("="*70)

# Load paragraph A_194 (opolch - strong PRECISION candidate)
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Get tokens from A_194
a194_tokens = para_tokens.get("A_194", [])
print(f"\nParagraph A_194 (folio f58v)")
print(f"Initial RI: opolch")
print(f"Total tokens: {len(a194_tokens)}")

# Extract PP tokens with qo- prefix (ESCAPE role)
escape_tokens = []
aux_tokens = []
other_pp = []

for t in a194_tokens:
    word = t.get('word', '')
    if not word or '*' in word:
        continue
    try:
        m = morph.extract(word)
        if m.middle and m.middle in pp_middles:
            if m.prefix == 'qo':
                escape_tokens.append(word)
            elif m.prefix in ['ok', 'ot']:
                aux_tokens.append(word)
            else:
                other_pp.append(word)
    except:
        pass

print(f"\nPP tokens by PREFIX role:")
print(f"  ESCAPE (qo-): {len(escape_tokens)}")
print(f"  AUX (ok/ot-): {len(aux_tokens)}")
print(f"  Other PP: {len(other_pp)}")

# Pick a specific ESCAPE token to trace
if escape_tokens:
    example_token = escape_tokens[0]
else:
    example_token = aux_tokens[0] if aux_tokens else other_pp[0]

print(f"\n" + "="*70)
print(f"TRACING TOKEN: {example_token}")
print("="*70)

m = morph.extract(example_token)
print(f"\nMorphology:")
print(f"  PREFIX: {m.prefix}")
print(f"  MIDDLE: {m.middle}")
print(f"  SUFFIX: {m.suffix}")

# Load transcript
tx = Transcript()

# Find in A
print(f"\n--- IN CURRIER A ---")
a_locations = []
for t in tx.currier_a():
    if t.word == example_token:
        a_locations.append(t)

print(f"Occurrences: {len(a_locations)}")
for loc in a_locations[:5]:
    print(f"  {loc.folio}:{loc.line}")

# Find in AZC (language=NA tokens)
print(f"\n--- IN AZC ---")
azc_locations = []
for t in tx.azc():
    if t.word == example_token:
        azc_locations.append(t)

print(f"Occurrences: {len(azc_locations)}")
if azc_locations:
    # Show placement types
    placements = defaultdict(list)
    for loc in azc_locations:
        placements[loc.placement[0] if loc.placement else '?'].append(loc)

    print(f"By placement type:")
    for ptype, locs in sorted(placements.items()):
        print(f"  {ptype}: {len(locs)} tokens")
        for loc in locs[:3]:
            print(f"    {loc.folio}:{loc.placement}")
else:
    print("  (not found in AZC)")

# Find in B
print(f"\n--- IN CURRIER B ---")
b_locations = []
for t in tx.currier_b():
    if t.word == example_token:
        b_locations.append(t)

print(f"Occurrences: {len(b_locations)}")
b_folios = set(t.folio for t in b_locations)
print(f"B folios: {len(b_folios)}")

if b_locations:
    # Show sample locations
    print(f"Sample locations:")
    for loc in b_locations[:5]:
        print(f"  {loc.folio}:{loc.line}")

# Summary
print(f"\n" + "="*70)
print("PIPELINE SUMMARY")
print("="*70)
print(f"""
Token: {example_token}
  PREFIX: {m.prefix} (ESCAPE role in B grammar)
  MIDDLE: {m.middle} (PP class)

Flow:
  A (paragraph A_194, f58v)
    |
    | Selected as part of PRECISION handling procedure
    | PREFIX=qo indicates ESCAPE instruction class
    |
    v
  AZC ({len(azc_locations)} positions)
    |
    | Position determines:
    |   - Legality (is this token permitted here?)
    |   - Escape permission (can this token trigger intervention?)
    |
    v
  B ({len(b_locations)} occurrences across {len(b_folios)} folios)
    |
    | Executes as ESCAPE instruction
    | Kernel: k or e (not h) - matches PRECISION signature
""")

# Show a few more ESCAPE tokens for comparison
print("="*70)
print("OTHER ESCAPE TOKENS FROM A_194")
print("="*70)

for token in escape_tokens[:5]:
    m = morph.extract(token)

    # Count in each system
    a_count = sum(1 for t in tx.currier_a() if t.word == token)
    azc_count = sum(1 for t in tx.azc() if t.word == token)
    b_count = sum(1 for t in tx.currier_b() if t.word == token)

    print(f"\n{token} ({m.prefix}-{m.middle}-{m.suffix or 'ø'}):")
    print(f"  A: {a_count}  |  AZC: {azc_count}  |  B: {b_count}")
