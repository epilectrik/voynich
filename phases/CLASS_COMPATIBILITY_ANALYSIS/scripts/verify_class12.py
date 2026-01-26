"""Verify what Class 12 actually contains and whether it's real."""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter
import json

tx = Transcript()
morph = Morphology()

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    data = json.load(f)
    token_to_class = data['token_to_class']
    class_to_tokens = data['class_to_tokens']

print("=== Class 12 in mapping file ===")
class12_tokens = class_to_tokens.get('12', [])
print(f"Tokens in Class 12: {class12_tokens}")

print("\n=== Checking actual B transcript ===")
b_words = Counter()
for t in tx.currier_b():
    b_words[t.word] += 1

print(f"Total unique B words: {len(b_words)}")

for tok in class12_tokens:
    count = b_words.get(tok, 0)
    print(f"  '{tok}': {count} occurrences in B")

print("\n=== What about CORE_CONTROL classes 10 and 11? ===")
for cls in ['10', '11']:
    tokens = class_to_tokens.get(cls, [])
    print(f"\nClass {cls}: {tokens}")
    for tok in tokens:
        count = b_words.get(tok, 0)
        print(f"  '{tok}': {count} occurrences in B")

print("\n=== Checking morphology of daiin and ol ===")
for word in ['daiin', 'ol', 'k']:
    m = morph.extract(word)
    count = b_words.get(word, 0)
    print(f"'{word}': B count={count}, prefix={m.prefix}, middle={m.middle}, suffix={m.suffix}")
