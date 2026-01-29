"""
Investigate single-character sequences across all three systems:
- f57v (AZC) - R2 single character sequence
- f49v (Currier A) - margin single characters
- f76r (Currier B) - single characters
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

tx = Transcript()

# Collect all tokens from all systems
print("Loading all tokens...")
all_token_list = []
for token in tx.currier_a():
    all_token_list.append(token)
for token in tx.currier_b():
    all_token_list.append(token)
for token in tx.azc():
    all_token_list.append(token)
print(f"Loaded {len(all_token_list)} tokens")

# Extract tokens for these folios
for target in ['f49v', 'f76r', 'f57v']:
    print(f'\n{"="*70}')
    print(f'FOLIO: {target}')
    print(f'{"="*70}')

    tokens_by_line = {}
    for token in all_token_list:
        if token.folio != target:
            continue
        w = token.word.strip()
        if not w:
            continue

        key = (token.line, getattr(token, 'placement', ''))
        if key not in tokens_by_line:
            tokens_by_line[key] = []
        tokens_by_line[key].append(w)

    for (line, placement), tokens in sorted(tokens_by_line.items()):
        # Highlight lines with many single-char tokens
        singles = sum(1 for t in tokens if len(t) <= 2)
        marker = ' *** SINGLE CHARS' if singles > 3 else ''
        print(f'  L{line:02} [{placement:4}]: {" ".join(tokens)}{marker}')

# Also search for any other lines with high single-char density
print(f'\n{"="*70}')
print('SEARCHING ALL FOLIOS FOR SINGLE-CHAR SEQUENCES')
print(f'{"="*70}')

all_tokens_by_folio_line = {}
for token in all_token_list:
    w = token.word.strip()
    if not w:
        continue

    key = (token.folio, token.line, getattr(token, 'placement', ''))
    if key not in all_tokens_by_folio_line:
        all_tokens_by_folio_line[key] = []
    all_tokens_by_folio_line[key].append(w)

# Find lines with high single-char ratio
single_char_lines = []
for (folio, line, placement), tokens in all_tokens_by_folio_line.items():
    if len(tokens) < 4:
        continue
    singles = sum(1 for t in tokens if len(t) <= 2)
    ratio = singles / len(tokens)
    if ratio > 0.5:  # More than half are single chars
        single_char_lines.append((folio, line, placement, tokens, ratio))

single_char_lines.sort(key=lambda x: x[4], reverse=True)

print(f'\nFound {len(single_char_lines)} lines with >50% single-character tokens:\n')
for folio, line, placement, tokens, ratio in single_char_lines[:20]:
    print(f'{folio:8} L{line:02} [{placement:4}] ({ratio:.0%}): {" ".join(tokens)}')
