"""Demonstrate glossing folio-unique MIDDLEs using compound decomposition.

Shows that 88% of folio-unique MIDDLEs (ext_len <= 3) can be auto-glossed
by composing atom gloss + extension character meanings.
"""
import json
import sys
from collections import Counter

sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, BFolioDecoder

# --- Setup ---
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer._core_middles

with open('data/middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)['middles']

# --- Single-char extension glosses ---
ext_glosses = {}
for name, entry in mid_dict.items():
    if len(name) == 1 and entry.get('gloss'):
        ext_glosses[name] = entry['gloss']

print("Extension character glosses:")
for ch, gl in sorted(ext_glosses.items()):
    print(f"  '{ch}' = {gl}")

# --- Decompose all folio-unique MIDDLEs ---
folio_middles = {}
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        if m.middle not in folio_middles:
            folio_middles[m.middle] = set()
        folio_middles[m.middle].add(t.folio)

unique_middles = {mid: list(folios)[0]
                  for mid, folios in folio_middles.items()
                  if len(folios) == 1}

# Decompose with different ext_len limits
def decompose(middle, max_ext=3):
    """Try to decompose into core atom + extensions."""
    if middle in core_middles:
        return ('CORE', middle, '', '')
    best = None
    for atom in sorted(core_middles, key=len, reverse=True):
        idx = middle.find(atom)
        if idx >= 0:
            pre = middle[:idx]
            post = middle[idx + len(atom):]
            ext_len = len(pre) + len(post)
            if ext_len <= max_ext and (best is None or ext_len < best[4]):
                best = (atom, pre, post, ext_len, ext_len)
    if best:
        return ('COMPOUND', best[0], best[1], best[2])
    return ('NOVEL', None, '', '')


def compose_gloss(middle, max_ext=3):
    """Compose a gloss from atom + extension chars."""
    result = decompose(middle, max_ext)
    if result[0] == 'CORE':
        atom_entry = mid_dict.get(middle, {})
        return atom_entry.get('gloss', f'[{middle}]')
    if result[0] == 'NOVEL':
        return None

    atom, pre, suf = result[1], result[2], result[3]
    atom_entry = mid_dict.get(atom, {})
    atom_gloss = atom_entry.get('gloss')
    if not atom_gloss:
        return None

    ext_parts = []
    for ch in pre + suf:
        gl = ext_glosses.get(ch)
        if gl:
            ext_parts.append(gl)
        else:
            ext_parts.append(f'?{ch}')

    if ext_parts:
        return f"{atom_gloss} (+{', '.join(ext_parts)})"
    return atom_gloss


# --- Coverage by ext_len limit ---
print(f"\n{'='*70}")
print("COVERAGE BY EXTENSION LENGTH LIMIT")
print(f"{'='*70}")

for limit in [3, 4, 5, 6]:
    glossable = 0
    decomposable = 0
    for mid in unique_middles:
        result = decompose(mid, limit)
        if result[0] == 'COMPOUND':
            decomposable += 1
            gloss = compose_gloss(mid, limit)
            if gloss:
                glossable += 1

    print(f"  ext_len <= {limit}: {decomposable}/{len(unique_middles)} decomposable "
          f"({100*decomposable/len(unique_middles):.1f}%), "
          f"{glossable} glossable ({100*glossable/len(unique_middles):.1f}%)")

# --- Show glossed examples for the most distinctive folios ---
distinctive_folios = ['f114r', 'f105v', 'f105r', 'f115r', 'f86v6']

print(f"\n{'='*70}")
print("GLOSSED FOLIO-UNIQUE MIDDLEs (MOST DISTINCTIVE FOLIOS)")
print(f"{'='*70}")

for folio in distinctive_folios:
    folio_uniques = [mid for mid, f in unique_middles.items() if f == folio]
    if not folio_uniques:
        continue

    print(f"\n  {folio} ({len(folio_uniques)} unique MIDDLEs):")

    glossed = 0
    unglossed = 0
    for mid in sorted(folio_uniques, key=len):
        gloss = compose_gloss(mid, max_ext=3)
        result = decompose(mid, max_ext=3)

        if result[0] == 'COMPOUND':
            atom, pre, suf = result[1], result[2], result[3]
            decomp_str = f"{pre}[{atom}]{suf}"
        elif result[0] == 'CORE':
            decomp_str = f"[{mid}]"
        else:
            decomp_str = "NOVEL"

        if gloss:
            glossed += 1
            print(f"    '{mid}' -> {decomp_str:20s} => {gloss}")
        else:
            unglossed += 1
            # Try with higher limit
            gloss6 = compose_gloss(mid, max_ext=6)
            if gloss6:
                result6 = decompose(mid, max_ext=6)
                decomp6 = f"{result6[2]}[{result6[1]}]{result6[3]}"
                print(f"    '{mid}' -> {decomp6:20s} => {gloss6}  (needs ext<=6)")
            else:
                print(f"    '{mid}' -> {decomp_str:20s} => ???")

    print(f"    --- Glossed: {glossed}/{len(folio_uniques)} "
          f"({100*glossed/len(folio_uniques):.0f}%) with ext<=3 ---")

# --- Full rendering with BFolioDecoder for one folio ---
print(f"\n{'='*70}")
print("FULL RENDERED TOKENS FOR f114r (using BFolioDecoder)")
print(f"{'='*70}")

analysis = decoder.analyze_folio('f114r')
unique_set = set(mid for mid, f in unique_middles.items() if f == 'f114r')

for ta in analysis.tokens[:50]:
    m = morph.extract(ta.word)
    if m and m.middle and m.middle in unique_set:
        interp = ta.interpretive()
        print(f"  {ta.word:15s} middle={m.middle:15s} -> {interp}")

# --- Summary statistics ---
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

total_unique = len(unique_middles)
glossable_3 = sum(1 for mid in unique_middles if compose_gloss(mid, 3))
glossable_6 = sum(1 for mid in unique_middles if compose_gloss(mid, 6))

print(f"""
Total folio-unique MIDDLEs: {total_unique}
  Glossable with ext<=3:    {glossable_3} ({100*glossable_3/total_unique:.1f}%)
  Glossable with ext<=6:    {glossable_6} ({100*glossable_6/total_unique:.1f}%)
  Unglosable:               {total_unique - glossable_6} ({100*(total_unique-glossable_6)/total_unique:.1f}%)

The compound MIDDLE renderer already covers {100*glossable_3/total_unique:.0f}% of
folio-unique tokens. Each gets a composed gloss like:
  atom_meaning (+extension1, extension2, ...)

Example: 'edalo' = [al]o -> 'settle (+cool, work)'
  - atom 'al' = settle
  - extension 'e' = cool
  - extension 'o' = work

These glosses are compositional: they read as the core operation
modified by operational qualifiers (heat, cool, mark, step, etc.)
""")
