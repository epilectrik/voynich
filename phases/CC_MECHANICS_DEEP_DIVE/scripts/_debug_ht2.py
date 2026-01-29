import json
import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

tx = Transcript()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

print(f"Classified token types: {len(classified_tokens)}")

# Check what type token.line is
for i, token in enumerate(tx.currier_b()):
    if i < 5:
        print(f"token.line = {token.line!r}, type = {type(token.line)}")

# Check line 1 tokens with string comparison
print("\nLine '1' tokens classification (first 30):")
count = 0
ht_on_line1 = 0
total_line1 = 0
for token in tx.currier_b():
    if str(token.line) == '1':  # String comparison
        total_line1 += 1
        w = token.word.strip()
        if not w:
            continue
        is_ht = w not in classified_tokens
        if is_ht:
            ht_on_line1 += 1
        if count < 30:
            status = "HT" if is_ht else "CLASSIFIED"
            print(f"  '{w}': {status}")
            count += 1

print(f"\nTotal line-1 tokens: {total_line1}")
if total_line1 > 0:
    print(f"HT on line 1: {ht_on_line1} ({100*ht_on_line1/total_line1:.1f}%)")
