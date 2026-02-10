"""Test: No two distinct MIDDLEs produce identical gloss strings.

Expert-recommended invariant: every structurally different MIDDLE must produce
a visually distinct gloss. This prevents regression when new glosses are added.

Also checks suffix_gloss uniqueness within collision-prone groups.
"""
import json, sys
from pathlib import Path

PROJECT = Path(r'C:\git\voynich')
sys.path.insert(0, str(PROJECT))

# --- MIDDLE dictionary uniqueness ---
md = json.load(open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8'))
middles = md['middles']

# Build gloss -> list of MIDDLEs map
gloss_to_middles = {}
for mid, entry in middles.items():
    gloss = entry.get('gloss')
    if not gloss:
        continue
    gloss_to_middles.setdefault(gloss, []).append(mid)

# Find collisions
collisions = {g: ms for g, ms in gloss_to_middles.items() if len(ms) > 1}

print("=" * 70)
print("MIDDLE DICTIONARY UNIQUENESS TEST")
print("=" * 70)
print(f"Glossed MIDDLEs: {sum(1 for e in middles.values() if e.get('gloss'))}")
print(f"Distinct gloss strings: {len(gloss_to_middles)}")
print(f"Collision groups: {len(collisions)}")

if collisions:
    print(f"\nFAILED - {len(collisions)} collision(s):")
    for gloss, ms in sorted(collisions.items()):
        print(f"  '{gloss}' <- {ms}")
else:
    print("\nPASSED - Every MIDDLE has a unique gloss string")

# --- Suffix gloss uniqueness ---
dm = json.load(open(PROJECT / 'data' / 'decoder_maps.json', encoding='utf-8'))
suffix_gloss_section = dm.get('maps', {}).get('suffix_gloss', {})
suffix_entries = suffix_gloss_section.get('entries', {})

sg_to_suffixes = {}
for sfx, entry in suffix_entries.items():
    gloss = entry.get('value', '') if isinstance(entry, dict) else str(entry)
    sg_to_suffixes.setdefault(gloss, []).append(sfx)

suffix_collisions = {g: ss for g, ss in sg_to_suffixes.items() if len(ss) > 1}

print(f"\n{'=' * 70}")
print("SUFFIX GLOSS UNIQUENESS TEST")
print("=" * 70)
print(f"Suffix gloss entries: {len(suffix_entries)}")
print(f"Distinct gloss strings: {len(sg_to_suffixes)}")
print(f"Collision groups: {len(suffix_collisions)}")

if suffix_collisions:
    print(f"\nCollision groups (may be acceptable):")
    for gloss, ss in sorted(suffix_collisions.items()):
        print(f"  '{gloss}' <- {ss}")
else:
    print("\nPASSED - Every suffix has a unique gloss string")

# --- Token-level rendered gloss uniqueness ---
# Check that tokens with different (prefix, middle, suffix) don't get identical glosses
from scripts.voynich import Morphology, TokenDictionary

morph = Morphology()
td_obj = TokenDictionary()
td = json.load(open(PROJECT / 'data' / 'token_dictionary.json', encoding='utf-8'))

triple_to_glosses = {}  # (prefix, middle, suffix) -> set of glosses
gloss_to_triples = {}   # gloss -> set of (prefix, middle, suffix)

for tok, entry in td['tokens'].items():
    gloss = entry.get('gloss')
    if not gloss:
        continue
    m = morph.extract(tok)
    triple = (m.prefix, m.middle, m.suffix)
    triple_to_glosses.setdefault(triple, set()).add(gloss)
    gloss_to_triples.setdefault(gloss, set()).add(triple)

# Find cases where different triples produce same gloss
multi_triple_glosses = {g: ts for g, ts in gloss_to_triples.items() if len(ts) > 1}

print(f"\n{'=' * 70}")
print("TOKEN RENDERED GLOSS UNIQUENESS TEST")
print("=" * 70)
print(f"Glossed tokens: {sum(1 for e in td['tokens'].values() if e.get('gloss'))}")
print(f"Distinct (prefix, middle, suffix) triples: {len(triple_to_glosses)}")
print(f"Distinct rendered glosses: {len(gloss_to_triples)}")
print(f"Glosses shared by multiple triples: {len(multi_triple_glosses)}")

if multi_triple_glosses:
    # Show top collision groups
    sorted_collisions = sorted(multi_triple_glosses.items(), key=lambda x: -len(x[1]))
    print(f"\nTop collision groups (up to 15):")
    for gloss, triples in sorted_collisions[:15]:
        print(f"  '{gloss[:50]}' <- {len(triples)} triples")
        for t in sorted(triples, key=lambda x: tuple(s or '' for s in x))[:5]:
            print(f"    {t}")
        if len(triples) > 5:
            print(f"    ... and {len(triples) - 5} more")
else:
    print("\nPASSED - Every (prefix, middle, suffix) triple has a unique rendered gloss")

# --- Summary verdict ---
print(f"\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)

middle_ok = len(collisions) == 0
print(f"MIDDLE uniqueness:  {'PASS' if middle_ok else 'FAIL'}")
print(f"Suffix uniqueness:  {len(suffix_collisions)} shared groups (informational)")
print(f"Token triple check: {len(multi_triple_glosses)} shared glosses (informational)")

if middle_ok:
    print("\nVERDICT: PASS - Zero MIDDLE gloss collisions")
else:
    print(f"\nVERDICT: FAIL - {len(collisions)} MIDDLE collision(s) found")

# Write result
result = {
    "test": "middle_uniqueness",
    "verdict": "PASS" if middle_ok else "FAIL",
    "middle_collisions": len(collisions),
    "suffix_collision_groups": len(suffix_collisions),
    "token_triple_shared_glosses": len(multi_triple_glosses),
    "glossed_middles": sum(1 for e in middles.values() if e.get('gloss')),
    "distinct_middle_glosses": len(gloss_to_middles),
}

out_path = PROJECT / 'phases' / 'GLOSS_RESEARCH' / 'results' / '25_middle_uniqueness_test.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(f"\nSaved: {out_path}")
