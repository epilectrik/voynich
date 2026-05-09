#!/usr/bin/env python3
"""
Extract Liber Mercuriorum (SISMEL Testamentum Part III) Latin chapter texts.

SISMEL structure:
  - Spreads paginate as L (left, Latin) / R (right, Catalan)
  - Chapter number markers: a line containing only a number (centered)
  - "TESTAMENTUM · III" page headers
  - Footnotes and figure captions interspersed

Strategy: walk the file from "Liber faciendi mercuria" start, only keep L-spread
content, parse chapter boundaries via standalone numeric lines, accumulate text
between markers as that chapter's body.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]


def main():
    text = (PROJECT_ROOT / 'sources/sismel_testamentum/sismel_testamentum_assembled.txt').read_text(
        encoding='utf-8', errors='ignore')
    lines = text.split('\n')

    # Find Liber Mercuriorum start
    start_idx = None
    for i, ln in enumerate(lines):
        if 'Liber faciendi mercuria' in ln:
            start_idx = i
            break
    if start_idx is None:
        print("ERROR: couldn't find Liber Mercuriorum start")
        return
    print(f"Liber Mercuriorum starts at line {start_idx}")

    # Walk forward
    chapters = defaultdict(list)
    current_ch = 1  # the first text after "Liber faciendi mercuria" is chapter 1
    in_l_spread = True  # we start mid-spread but assume L
    chapter_num_re = re.compile(r'^\s+(\d+)\s*$')
    spread_l_re = re.compile(r'SPREAD\s+\d+\s+\xe2\x80\x94\s+L'.encode().decode('latin-1', errors='replace'))
    # Use plain ASCII detection
    def is_spread_marker(ln):
        return ln.startswith('SPREAD ')
    # Simpler detection: look for "_L" or "_R" in the file ref part
    def is_left_spread(ln):
        return '_L.txt' in ln
    def is_right_spread(ln):
        return '_R.txt' in ln

    for i in range(start_idx + 1, len(lines)):
        ln = lines[i]
        # Spread header
        if is_spread_marker(ln):
            if is_left_spread(ln):
                in_l_spread = True
            elif is_right_spread(ln):
                in_l_spread = False
            continue
        if not in_l_spread:
            continue
        # End of Liber Mercuriorum?
        if 'EXPLICIT' in ln or 'Explicit' in ln:
            if 'Liber' in ln or 'Mercuri' in ln:
                print(f"  Liber Mercuriorum ends at line {i}: {ln.strip()}")
                break
        # Chapter number marker patterns (Latin L spread):
        #   "                              5"           (just number, centered)
        #   "f. 60ra                              5"   (folio ref + number, all one line)
        m = re.match(r'^\s{30,}(\d+)\s*$', ln)
        if not m:
            m = re.match(r'^\s*f\.\s*\d+\w*\s{10,}(\d+)\s*$', ln)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 50 and n > current_ch and n <= current_ch + 3:
                current_ch = n
            # Always skip the marker line
            continue
        # Skip page headers / page numbers
        stripped = ln.strip()
        if not stripped:
            continue
        if 'TESTAMENTUM' in stripped and 'III' in stripped:
            continue
        if re.match(r'^[0-9]+$', stripped) and len(stripped) <= 4:
            # Page number
            continue
        if stripped.startswith('==='):
            continue
        if stripped.startswith('───'):
            continue
        # Footnote indicator (start with number followed by period)
        if re.match(r'^\d+\. ', stripped):
            continue
        # FIGURA caption
        if stripped.startswith('FIGURA') or stripped.startswith('Figura'):
            continue
        # Folio reference like "f. 59ra"
        if re.match(r'^f\.\s*\d+', stripped):
            continue
        # Otherwise content
        chapters[current_ch].append(stripped)

    print(f"\nExtracted {len(chapters)} chapters from Liber Mercuriorum")
    out = {}
    for ch in sorted(chapters.keys()):
        body = '\n'.join(chapters[ch])
        n_chars = len(body)
        n_words = len(body.split())
        out[str(ch)] = body
        if n_words > 5:
            print(f"  III.{ch}: {n_words} words, {n_chars} chars")

    # Save
    out_path = PHASE_DIR / 'data' / 'sismel_liber_mercuriorum_latin.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_path}")

    # Show a sample
    if out.get('19'):
        sample = out['19'][:600]
        print(f"\n=== Sample III.19 (matches f75r) ===")
        print(sample)


if __name__ == '__main__':
    main()
