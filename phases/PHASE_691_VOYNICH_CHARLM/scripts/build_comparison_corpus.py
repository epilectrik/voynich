#!/usr/bin/env python3
"""
Phase 691.6: Build comparison corpora for three-LM analysis.

Process raw natural-language text into Voynich-comparable form:
  - Lowercase
  - Keep only [a-z] (drop punctuation, digits, accents)
  - Split into lines on sentence boundaries / line breaks
  - Filter out very short / very long lines
  - Whitespace-tokenize
  - Build train/val/test split (folio-disjoint analog: line-level random)

Outputs to data/lang_<name>/ matching Voynich corpus layout.
"""
import argparse
import json
import random
import re
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parents[1]
DATA = PHASE_DIR / 'data'

# Lowercase letters only — match Voynich vocab style (~20 chars but English/Latin will be ~26)
KEEP = re.compile(r'[a-z]+')
SENT_SPLIT = re.compile(r'[.!?;]+|\n')
SKIP_RE = re.compile(r'^(spread|page|chapter|isbn|©|sismel|edizioni|figure|sommario|^\d+$|introduzione)', re.I)


def normalize_text(text):
    text = text.lower()
    return text


def lines_from_text(text, min_tokens=3, max_tokens=30):
    """Yield 'lines' as token lists — comparable to Voynich line structure."""
    text = normalize_text(text)
    for chunk in SENT_SPLIT.split(text):
        chunk = chunk.strip()
        if not chunk:
            continue
        if SKIP_RE.match(chunk):
            continue
        tokens = KEEP.findall(chunk)
        if min_tokens <= len(tokens) <= max_tokens:
            yield tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, help='lang_latin, lang_english, etc.')
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--target-lines', type=int, default=4435,
                        help='Match Voynich line count (4435)')
    parser.add_argument('--seed', type=int, default=691)
    args = parser.parse_args()

    text = args.source.read_text(encoding='utf-8', errors='ignore')
    print(f"Source: {args.source} ({len(text):,} chars)")

    all_lines = list(lines_from_text(text))
    print(f"  Extracted {len(all_lines)} usable lines (filtered)")

    rng = random.Random(args.seed)
    rng.shuffle(all_lines)
    if len(all_lines) > args.target_lines:
        all_lines = all_lines[:args.target_lines]
    print(f"  Sampled to {len(all_lines)} lines (target {args.target_lines})")

    # Stats
    tokens = [t for line in all_lines for t in line]
    chars = set(c for t in tokens for c in t)
    print(f"  Total tokens: {len(tokens):,}")
    print(f"  Unique chars: {len(chars)} -> {sorted(chars)}")
    print(f"  Mean tokens/line: {len(tokens)/len(all_lines):.1f}")

    # Split 80/10/10
    n = len(all_lines)
    n_test = max(1, n // 10)
    n_val = max(1, n // 10)
    splits = {
        'train': all_lines[:n - n_val - n_test],
        'val': all_lines[n - n_val - n_test:n - n_test],
        'test': all_lines[n - n_test:],
    }

    out_dir = DATA / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    for split, lines in splits.items():
        path = out_dir / f'corpus_{split}.jsonl'
        with open(path, 'w', encoding='utf-8') as f:
            for i, toks in enumerate(lines):
                f.write(json.dumps({
                    'folio': f'{args.name}_{split}',
                    'line': str(i),
                    'section': 'A',  # placeholder for compat
                    'tokens': toks,
                    'text': ' '.join(toks),
                }, ensure_ascii=False) + '\n')
        print(f"  {split}: {len(lines):>5d} lines -> {path}")

    # Char inventory + tokenizer
    inv_path = out_dir / 'char_inventory.json'
    inv_path.write_text(json.dumps(sorted(chars)))

    # Build tokenizer matching this char set (use same special tokens as Voynich)
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tokenizer import CharTokenizer
    tok = CharTokenizer(sorted(chars))
    tok.save(out_dir / 'tokenizer.json')
    print(f"  Tokenizer vocab: {tok.vocab_size}")


if __name__ == '__main__':
    main()
