"""Check eoschso location and paragraph structure."""
import json
import sys
sys.path.insert(0, 'scripts')
from voynich import Morphology, Transcript

morph = Morphology()
tx = Transcript()

# Build B middles
b_middles = set()
for token in tx.currier_b():
    if '*' not in token.word and token.word.strip():
        try:
            m = morph.extract(token.word)
            if m.middle:
                b_middles.add(m.middle)
        except:
            pass

print(f"B MIDDLE vocabulary: {len(b_middles)}")

# Load paragraphs
para_tokens = json.load(open('phases/PARAGRAPH_INTERNAL_PROFILING/results/a_paragraph_tokens.json'))

# Find all paragraphs containing eoschso
print("\n" + "="*70)
print("PARAGRAPHS CONTAINING eoschso")
print("="*70)

for para_id, tokens in para_tokens.items():
    for i, t in enumerate(tokens):
        try:
            m = morph.extract(t['word'])
            if m.middle == 'eoschso':
                # Analyze this paragraph
                print(f"\n{para_id}: found at position {i}/{len(tokens)}")
                print(f"  Word: {t['word']}")
                print(f"  Folio: {t['folio']}:{t['line']}")

                # Get initial RI
                initial_ri = []
                for tok in tokens:
                    try:
                        mm = morph.extract(tok['word'])
                        mid = mm.middle if mm.middle else tok['word']
                    except:
                        mid = tok['word']
                    if mid not in b_middles:
                        initial_ri.append((tok['word'], mid))
                    else:
                        break
                print(f"  Initial RI (ID): {initial_ri[:3]}")

                # Check if eoschso could be ID
                is_initial = i < len(initial_ri) if initial_ri else False
                print(f"  eoschso is initial RI: {is_initial}")

                # Context
                context = [(tokens[j]['word'], 'RI' if morph.extract(tokens[j]['word']).middle not in b_middles else 'PP')
                          for j in range(max(0, i-3), min(len(tokens), i+4))]
                print(f"  Context: {context}")

        except Exception as e:
            pass

# Also check: are there any paragraphs where eoschso IS the initial RI?
print("\n" + "="*70)
print("CHECKING IF eoschso EVER APPEARS AS INITIAL RI")
print("="*70)

for para_id, tokens in para_tokens.items():
    # Get first token's MIDDLE
    if tokens:
        try:
            m = morph.extract(tokens[0]['word'])
            if m.middle == 'eoschso':
                print(f"\n{para_id}: eoschso is INITIAL token!")
                print(f"  Word: {tokens[0]['word']}")
        except:
            pass
