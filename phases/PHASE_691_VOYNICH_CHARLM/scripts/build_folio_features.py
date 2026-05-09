#!/usr/bin/env python3
"""
Phase 691.x: Build hand-crafted structural feature vectors per Voynich folio.

Per expert-advisor: hand-crafted features + classical retrieval is the cheap
diagnostic. If hand-features hit >=4/9 LOO recovery, the signal is real; if
<2/9, bilingual training won't help.

Per-folio features (selected for cross-corpus alignment value):
  - mean_e_depth (C1206 thermal signature)         HIGH-VALUE
  - mean_i_depth (iteration signature)              HIGH-VALUE
  - atom HEAD distribution (5-dim: a/e/o/k/t)       HIGH-VALUE
  - atom TERM distribution (8-dim: y/n/m/h/l/r/k/t) MED-VALUE
  - mean_token_length                                BASELINE
  - paragraph_count
  - qok_token_rate (qo-heat-prefix tokens, alchemy signature)  HIGH
  - cardinality_anchors: 1 if any same-token x4+ run         HIGH
  - n_tokens
  - section_A/B/AZC dummies
  - dam_rate, ar_rate, or_rate (apparatus tokens)
  - h_rate (avoid as feature - C922 single-char ring exclusion)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

HEAD_CHARS = list('aeokt')
TERM_CHARS = list('ynmhlrkt')


def main():
    tx = Transcript()
    morph = Morphology()
    by_folio = defaultdict(list)
    folio_paragraphs = defaultdict(set)
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        by_folio[tok.folio].append(tok)
        # Track paragraph IDs (line + folio is a proxy)
        # Actual paragraph delineation is per project's paragraph constraint
        # For now: count distinct lines as approx
    folios = sorted(by_folio.keys())
    print(f"Building features for {len(folios)} folios")

    rows = []
    for folio in folios:
        toks = by_folio[folio]
        words = [t.word for t in toks]
        n = len(words)
        if n < 3:
            continue

        # Basic stats
        word_lens = [len(w) for w in words]
        avg_len = sum(word_lens) / n
        unique_pct = len(set(words)) / n

        # Sections
        secs = Counter(t.language for t in toks)
        total = sum(secs.values())
        sec_a = secs.get('A', 0) / max(1, total)
        sec_b = secs.get('B', 0) / max(1, total)
        sec_na = secs.get('NA', 0) / max(1, total)  # AZC

        # Atom-derived features
        head_counts = Counter()
        term_counts = Counter()
        e_depths = []
        i_depths = []
        n_with_atoms = 0
        n_qok = 0
        n_qot = 0
        for t in toks:
            try:
                a = morph.atomize(t.word)
            except Exception:
                continue
            if not a or not a.atoms:
                continue
            n_with_atoms += 1
            if a.head:
                head_counts[a.head] += 1
            if a.term:
                term_counts[a.term] += 1
            e_depths.append(a.e_depth)
            i_depths.append(a.i_depth)
            if a.prefix == 'qo' and a.head == 'k':
                n_qok += 1
            if a.prefix == 'qo' and a.head == 't':
                n_qot += 1

        head_dist = [head_counts.get(c, 0) / max(1, n_with_atoms) for c in HEAD_CHARS]
        term_dist = [term_counts.get(c, 0) / max(1, n_with_atoms) for c in TERM_CHARS]
        mean_e = np.mean(e_depths) if e_depths else 0
        mean_i = np.mean(i_depths) if i_depths else 0
        max_e = max(e_depths) if e_depths else 0

        # Cardinality anchors: same-token run >= 3
        cardinality_anchor = 0
        runs = 0
        prev = None
        run_len = 0
        max_run = 0
        for w in words:
            if w == prev:
                run_len += 1
            else:
                if run_len >= 3:
                    runs += 1
                    max_run = max(max_run, run_len)
                run_len = 1
                prev = w
        if run_len >= 3:
            runs += 1
            max_run = max(max_run, run_len)
        if runs > 0:
            cardinality_anchor = max_run

        # Apparatus-related token rates
        dam_rate = sum(1 for w in words if w == 'dam') / n
        ar_rate = sum(1 for w in words if w == 'ar') / n
        or_rate = sum(1 for w in words if w == 'or') / n
        daiin_rate = sum(1 for w in words if w == 'daiin') / n
        chedy_rate = sum(1 for w in words if w == 'chedy') / n
        shedy_rate = sum(1 for w in words if w == 'shedy') / n
        ol_rate = sum(1 for w in words if w == 'ol') / n

        qok_rate = n_qok / max(1, n_with_atoms)
        qot_rate = n_qot / max(1, n_with_atoms)

        # Line count proxy (paragraph count)
        n_lines = len(set(t.line for t in toks))

        row = {
            'folio': folio,
            'n_tokens': n,
            'n_lines': n_lines,
            'avg_token_len': avg_len,
            'unique_pct': unique_pct,
            'sec_a': sec_a,
            'sec_b': sec_b,
            'sec_na': sec_na,
            'mean_e_depth': mean_e,
            'mean_i_depth': mean_i,
            'max_e_depth': max_e,
            'cardinality_max_run': cardinality_anchor,
            'dam_rate': dam_rate,
            'ar_rate': ar_rate,
            'or_rate': or_rate,
            'daiin_rate': daiin_rate,
            'chedy_rate': chedy_rate,
            'shedy_rate': shedy_rate,
            'ol_rate': ol_rate,
            'qok_rate': qok_rate,
            'qot_rate': qot_rate,
        }
        for c, v in zip(HEAD_CHARS, head_dist):
            row[f'head_{c}'] = v
        for c, v in zip(TERM_CHARS, term_dist):
            row[f'term_{c}'] = v
        rows.append(row)

    print(f"Computed features for {len(rows)} folios")

    # Save
    out_path = PHASE_DIR / 'data' / 'folio_features.jsonl'
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Saved: {out_path}")

    # Show f75r (confirmed match)
    for r in rows:
        if r['folio'] == 'f75r':
            print(f"\nExample: f75r features (matches Ch 19):")
            for k, v in r.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.4f}")
                else:
                    print(f"  {k}: {v}")
            break


if __name__ == '__main__':
    main()
