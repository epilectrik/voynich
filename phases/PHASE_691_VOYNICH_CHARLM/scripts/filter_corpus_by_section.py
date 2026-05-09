#!/usr/bin/env python3
"""
Phase 691.5b prep: split corpus_{train,val,test}.jsonl into section-restricted
sub-corpora.

Outputs:
  data/section_A/corpus_train.jsonl  (only A lines)
  data/section_A/corpus_val.jsonl
  data/section_A/corpus_test.jsonl
  data/section_B/...
  data/section_AZC/...

Each section's split sizes are smaller. Re-uses the same folio-disjoint
assignments from the global split (no leakage).
"""
import json
from collections import defaultdict
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parents[1]
DATA = PHASE_DIR / 'data'

for sec in ['A', 'B', 'AZC']:
    out_dir = DATA / f'section_{sec}'
    out_dir.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for split in ['train', 'val', 'test']:
        in_path = DATA / f'corpus_{split}.jsonl'
        out_path = out_dir / f'corpus_{split}.jsonl'
        n = 0
        with open(in_path, encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as g:
            for line in f:
                r = json.loads(line)
                if r['section'] == sec:
                    g.write(line)
                    n += 1
        sizes[split] = n
    print(f"section_{sec}: train={sizes['train']:>5d}  val={sizes['val']:>5d}  test={sizes['test']:>5d}")
