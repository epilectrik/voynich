"""
Create a blind version of f104r_dump.txt that strips:
- Folio-level aggregate stats (kernel %, category profile, regime, etc.)
- Per-paragraph kernel distributions
- Paragraph summary table

Keeps:
- Folio ID and basic size info
- Raw token-by-token data with morphology, atom glosses, categories
- Paragraph boundaries (which gallows, how many lines/tokens)
"""

import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'

with open(DATA_DIR / 'f104r_dump.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

blind_lines = []
skip_until_dump = False
in_para_summary = False
skip_kernel_line = False

for line in lines:
    stripped = line.strip()

    # Keep the first line (folio ID + token count)
    if stripped.startswith('FOLIO f104r'):
        blind_lines.append(f"{'=' * 80}\n")
        blind_lines.append(f"FOLIO f104r — 438 tokens, 45 lines, 11 paragraphs\n")
        blind_lines.append(f"Section: Stars\n")
        blind_lines.append(f"{'=' * 80}\n")
        blind_lines.append(f"\n")
        skip_until_dump = True
        continue

    # Skip everything between the header and the token dump
    if skip_until_dump:
        if stripped.startswith('LINE-BY-LINE TOKEN DUMP'):
            skip_until_dump = False
            blind_lines.append(line)
        continue

    # In the token dump section, strip per-paragraph kernel distributions
    if stripped.startswith('Kernel: k='):
        continue
    if stripped.startswith('Dominant category:'):
        continue

    blind_lines.append(line)

outpath = DATA_DIR / 'f104r_blind.txt'
with open(outpath, 'w', encoding='utf-8') as f:
    f.writelines(blind_lines)

print(f"Blind version written to {outpath}")
print(f"  {len(blind_lines)} lines (vs {len(lines)} original)")
