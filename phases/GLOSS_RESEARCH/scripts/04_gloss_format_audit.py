"""Audit: Do token glosses use *middle references or hardcoded text?"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Morphology

morph = Morphology()
td = json.load(open('data/token_dictionary.json', encoding='utf-8'))

uses_star = 0
hardcoded = 0
no_gloss = 0
star_examples = []
hardcoded_examples = []

for tok, entry in td['tokens'].items():
    gloss = entry.get('gloss')
    if not gloss:
        no_gloss += 1
        continue

    if '*' in gloss:
        uses_star += 1
        if len(star_examples) < 10:
            star_examples.append((tok, gloss))
    else:
        hardcoded += 1
        if len(hardcoded_examples) < 30:
            m = morph.extract(tok)
            hardcoded_examples.append((tok, gloss, m.prefix, m.middle, m.suffix))

print(f"Total tokens: {len(td['tokens'])}")
print(f"No gloss: {no_gloss}")
print(f"Uses *middle ref: {uses_star}")
print(f"Hardcoded text: {hardcoded}")
print(f"Pct using *ref: {uses_star/(uses_star+hardcoded)*100:.1f}%")

print(f"\n{'='*60}")
print(f"EXAMPLES WITH *middle REFERENCES:")
print(f"{'='*60}")
for tok, gloss in star_examples:
    print(f"  {tok:<20} {gloss}")

print(f"\n{'='*60}")
print(f"EXAMPLES WITH HARDCODED TEXT:")
print(f"{'='*60}")
for tok, gloss, prefix, middle, suffix in hardcoded_examples:
    print(f"  {tok:<20} p={prefix or '-':<4} m={middle or '-':<8} s={suffix or '-':<5}  gloss={gloss}")
