#!/usr/bin/env python3
"""Analyze what's actually different between H and U tracks."""
import sys
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

tx = Transcript()

# Look at f86v3 which had best agreement (78.2%)
print("=" * 65)
print("H vs U DISAGREEMENT ANALYSIS")
print("=" * 65)

for folio in ['f86v3', 'f85r2', 'f86v4']:
    h_by_pos = defaultdict(list)
    u_by_pos = defaultdict(list)

    for tok in tx.all(h_only=False):
        if tok.folio != folio or not tok.word.strip() or '*' in tok.word:
            continue
        key = (tok.placement, tok.line)
        if tok.transcriber == 'H':
            h_by_pos[key].append(tok.word)
        elif tok.transcriber == 'U':
            u_by_pos[key].append(tok.word)

    print(f"\n{folio}:")
    print(f"  H positions: {len(h_by_pos)}, U positions: {len(u_by_pos)}")
    print(f"  Shared positions: {len(set(h_by_pos) & set(u_by_pos))}")

    # Show actual disagreements
    disagreements = []
    agreements = 0
    total = 0
    shared_keys = set(h_by_pos) & set(u_by_pos)

    for key in sorted(shared_keys):
        h_words = h_by_pos[key]
        u_words = u_by_pos[key]
        for i, (hw, uw) in enumerate(zip(h_words, u_words)):
            total += 1
            if hw == uw:
                agreements += 1
            else:
                disagreements.append((key, hw, uw))

    print(f"  Total compared: {total}, agreed: {agreements} ({100*agreements/total:.1f}%)")
    print(f"  Disagreements: {len(disagreements)}")

    # Show sample disagreements
    print(f"\n  Sample disagreements (placement, line) H vs U:")
    for (place, line), hw, uw in disagreements[:15]:
        # Compute edit distance approximation
        common = sum(1 for a, b in zip(hw, uw) if a == b)
        max_len = max(len(hw), len(uw))
        sim = common / max_len if max_len else 1
        print(f"    {place}:{line}  H={hw:20s} U={uw:20s} (char_sim={sim:.0%})")

# Check if H and U have different NUMBER of tokens per line
print("\n" + "=" * 65)
print("TOKEN COUNT MISMATCH ANALYSIS")
print("=" * 65)

for folio in ['f86v3', 'f86v4']:
    h_by_pos = defaultdict(list)
    u_by_pos = defaultdict(list)

    for tok in tx.all(h_only=False):
        if tok.folio != folio or not tok.word.strip():
            continue
        key = (tok.placement, tok.line)
        if tok.transcriber == 'H':
            h_by_pos[key].append(tok.word)
        elif tok.transcriber == 'U':
            u_by_pos[key].append(tok.word)

    print(f"\n{folio}:")
    shared = set(h_by_pos) & set(u_by_pos)
    same_count = 0
    diff_count = 0
    for key in shared:
        if len(h_by_pos[key]) == len(u_by_pos[key]):
            same_count += 1
        else:
            diff_count += 1
            print(f"  {key}: H has {len(h_by_pos[key])} tokens, U has {len(u_by_pos[key])}")
    print(f"  Same token count: {same_count}/{len(shared)}")
    print(f"  Different count: {diff_count}/{len(shared)}")
