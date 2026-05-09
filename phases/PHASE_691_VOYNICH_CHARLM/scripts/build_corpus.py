#!/usr/bin/env python3
"""
Build training corpus for Phase 691 char-LM from H-track.

Outputs:
  data/corpus_train.jsonl  — 80% of folios
  data/corpus_val.jsonl    — 10% of folios
  data/corpus_test.jsonl   — 10% of folios

Each line is a JSON record:
  {
    "folio": "f1r",
    "line": "1",
    "section": "A" | "B" | "AZC",
    "text": "fachys ykal ar ataiin shol shory cthres y kor sholdy",
    "tokens": ["fachys", "ykal", ...],
  }

Splits stratify by Currier section AND are folio-disjoint (no folio bleeds
across splits — required to prevent leakage of folio-level patterns).
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

PHASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PHASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Reproducible split seed
SPLIT_SEED = 691

# Section determination:
#   - language A => section A
#   - language B => section B
#   - language NA (AZC) => section AZC
def get_section(token):
    lang = token.language
    if lang == 'A':
        return 'A'
    if lang == 'B':
        return 'B'
    return 'AZC'


def main():
    tx = Transcript()
    # Group tokens by (folio, line)
    by_line = defaultdict(list)
    folio_section = {}  # folio -> primary section (mode of token sections)
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        sec = get_section(tok)
        by_line[(tok.folio, tok.line)].append((tok.word, sec))
        # Track folio's section (use first-seen)
        if tok.folio not in folio_section:
            folio_section[tok.folio] = sec

    print(f"Total folios: {len(folio_section)}")
    sec_counts = defaultdict(int)
    for s in folio_section.values():
        sec_counts[s] += 1
    print(f"Folio counts by section: {dict(sec_counts)}")

    # Build line records
    line_records = []
    for (folio, line), pairs in by_line.items():
        tokens = [w for w, _ in pairs]
        # Section = mode of token sections in this line (almost always uniform within a folio)
        secs = [s for _, s in pairs]
        sec = max(set(secs), key=secs.count)
        line_records.append({
            'folio': folio,
            'line': str(line),
            'section': sec,
            'tokens': tokens,
            'text': ' '.join(tokens),
        })
    print(f"Total lines: {len(line_records)}")

    # Sort lines by (folio, line) for determinism
    def line_key(r):
        try:
            return (r['folio'], int(r['line']))
        except ValueError:
            return (r['folio'], 999)
    line_records.sort(key=line_key)

    # Stratified folio-disjoint split: shuffle folios within each section, then assign
    rng = random.Random(SPLIT_SEED)
    folios_by_sec = defaultdict(list)
    for f, s in folio_section.items():
        folios_by_sec[s].append(f)

    split_assign = {}  # folio -> 'train' | 'val' | 'test'
    for sec, folios in folios_by_sec.items():
        folios = sorted(folios)
        rng.shuffle(folios)
        n = len(folios)
        n_val = max(1, n // 10)
        n_test = max(1, n // 10)
        n_train = n - n_val - n_test
        for f in folios[:n_train]:
            split_assign[f] = 'train'
        for f in folios[n_train:n_train + n_val]:
            split_assign[f] = 'val'
        for f in folios[n_train + n_val:]:
            split_assign[f] = 'test'

    # Write splits
    splits = defaultdict(list)
    for rec in line_records:
        splits[split_assign[rec['folio']]].append(rec)

    print()
    print(f"{'Split':<8} {'lines':>8} {'folios':>8} {'tokens':>10} {'A':>6} {'B':>6} {'AZC':>6}")
    for split in ['train', 'val', 'test']:
        recs = splits[split]
        n_lines = len(recs)
        folios = set(r['folio'] for r in recs)
        n_tokens = sum(len(r['tokens']) for r in recs)
        sec_n = defaultdict(int)
        for r in recs:
            sec_n[r['section']] += 1
        print(f"{split:<8} {n_lines:>8} {len(folios):>8} {n_tokens:>10} "
              f"{sec_n['A']:>6} {sec_n['B']:>6} {sec_n['AZC']:>6}")

        out_path = DATA_DIR / f'corpus_{split}.jsonl'
        with open(out_path, 'w', encoding='utf-8') as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # Write split assignment for reproducibility
    with open(DATA_DIR / 'split_assignment.json', 'w', encoding='utf-8') as f:
        json.dump({
            'seed': SPLIT_SEED,
            'folio_to_split': split_assign,
            'folio_to_section': folio_section,
        }, f, indent=2, ensure_ascii=False)

    # Vocab inventory
    chars = set()
    for r in line_records:
        for t in r['tokens']:
            chars.update(t)
    print(f"\nUnique characters in corpus: {len(chars)}")
    print(f"Characters: {sorted(chars)}")
    with open(DATA_DIR / 'char_inventory.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(chars), f)


if __name__ == '__main__':
    main()
