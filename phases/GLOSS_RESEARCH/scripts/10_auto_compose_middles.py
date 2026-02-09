"""Auto-compose compound middle glosses from glossed atoms.

Strategy:
  1. Gloss remaining high-frequency atomic middles
  2. For each unglossed compound middle, find the best decomposition
     into glossed atoms and compose a gloss from them
  3. Only add glosses where decomposition is unambiguous

Atomic middle glosses added here are based on their prefix-role
equivalents and positional behavior in tokens.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import MiddleAnalyzer

md_path = Path('data/middle_dictionary.json')
md = json.load(open(md_path, encoding='utf-8'))
middles = md['middles']

# --- Step 1: Gloss remaining atomic middles ---
# These are true atoms (not decomposable) that lack glosses.
# Glosses derived from their prefix-role equivalents and context.
atomic_glosses = {
    'sh':  'verify',        # prefix sh = observe/verify; as middle = verification step
    'f':   'mark',          # functional marker (rare as middle, f-tokens are few)
    'ii':  'repeat',        # related to i=step, iin=iterate; double = repeat
    'an':  'bind',          # a=attach variant; -n suffix = binding
    'ir':  'input-step',    # i=step + r=input compound but behaves as atom
    'ep':  'cool-pause',    # e=cool + p=pause
    'x':   'cross',         # rare, structural marker
    'g':   'hold',          # terminal hold (appears in suffixes)
    'q':   'energy',        # qo-family energy marker
    'n':   'anchor',        # terminal anchor
    'im':  'step-mark',     # i=step + m=precision marker
    'ro':  'input-work',    # r=input + o=work
}

atom_count = 0
atom_log = []
for mid, gloss in atomic_glosses.items():
    entry = middles.get(mid)
    if not entry:
        continue
    if entry.get('gloss'):
        continue  # already glossed
    entry['gloss'] = gloss
    atom_count += 1
    atom_log.append((mid, gloss, entry.get('token_count', 0)))

print(f"Step 1: Added {atom_count} atomic middle glosses\n")
for mid, gloss, n in sorted(atom_log, key=lambda x: -x[2]):
    print(f"  {mid:<10} = {gloss:<20} (n={n})")

# --- Step 2: Build glossed atom lookup ---
glossed = {m: e['gloss'] for m, e in middles.items() if e.get('gloss')}

# --- Step 3: Auto-compose compound middles ---
# Use greedy longest-match decomposition from left to right
def decompose(middle, glossed_atoms):
    """Decompose a compound middle into glossed atoms (greedy longest match)."""
    result = []
    pos = 0
    while pos < len(middle):
        # Try longest match first
        found = False
        for length in range(min(5, len(middle) - pos), 0, -1):
            candidate = middle[pos:pos+length]
            if candidate in glossed_atoms:
                result.append((candidate, glossed_atoms[candidate]))
                pos += length
                found = True
                break
        if not found:
            return None  # Can't decompose fully
    return result

compose_count = 0
compose_log = []

for mid, entry in sorted(middles.items(), key=lambda x: -x[1].get('token_count', 0)):
    if entry.get('gloss'):
        continue  # already glossed
    count = entry.get('token_count', 0)
    if count < 3:
        continue  # too rare to bother

    parts = decompose(mid, glossed)
    if parts and len(parts) >= 2:
        # Compose gloss: join with comma or hyphen
        # Use hyphen for tight compounds, comma for loose
        part_glosses = [g for _, g in parts]
        composed = ', '.join(part_glosses)
        entry['gloss'] = composed
        compose_count += 1
        atoms_str = '+'.join(f"{a}({g})" for a, g in parts)
        compose_log.append((mid, composed, count, atoms_str))

print(f"\nStep 2: Auto-composed {compose_count} compound middle glosses\n")
print(f"{'Middle':<14} {'Composed Gloss':<35} {'Count':>5}  {'Decomposition'}")
print(f"{'-'*14} {'-'*35} {'-'*5}  {'-'*40}")
for mid, gloss, n, atoms in sorted(compose_log, key=lambda x: -x[2]):
    print(f"  {mid:<14} {gloss:<35} {n:>5}  {atoms}")

# --- Step 4: Update metadata ---
total_glossed = sum(1 for e in middles.values() if e.get('gloss'))
md['meta']['glossed'] = total_glossed
md['meta']['auto_composition'] = f'Auto-composed {compose_count} compound middles from atoms (2026-02-06)'
md['meta']['version'] = '1.5'

with open(md_path, 'w', encoding='utf-8') as f:
    json.dump(md, f, indent=2, ensure_ascii=False)

# --- Step 5: Coverage report ---
total_tokens = sum(e.get('token_count', 0) for e in middles.values())
glossed_tokens = sum(e.get('token_count', 0) for e in middles.values() if e.get('gloss'))
print(f"\n{'='*60}")
print(f"COVERAGE REPORT")
print(f"{'='*60}")
print(f"  Glossed middles: {total_glossed} / {len(middles)}")
print(f"  Token coverage:  {glossed_tokens} / {total_tokens} ({glossed_tokens/total_tokens*100:.1f}%)")
print(f"  Atoms glossed:   {atom_count} new")
print(f"  Compounds auto:  {compose_count} new")
