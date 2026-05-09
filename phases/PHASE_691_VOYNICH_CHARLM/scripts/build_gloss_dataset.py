#!/usr/bin/env python3
"""
Build training dataset for the Voynich-to-gloss translator.

For every unique H-track token, compute its atomize() output (per C1394).
Save as (input_chars, output_gloss_string) pairs.

The model will learn: given Voynich character sequence, produce its
structural decomposition with semantic tags (heat, cool, do, end, etc).
"""
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

PHASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PHASE_DIR / 'data'


def main():
    tx = Transcript()
    morph = Morphology()

    # Collect all unique tokens with frequency
    token_freq = Counter()
    for tok in tx.all(h_only=True):
        if tok.word and not tok.is_uncertain:
            token_freq[tok.word] += 1

    # Compute gloss for each
    pairs = []
    gloss_atoms = set()
    failed = 0
    for word, freq in token_freq.items():
        try:
            a = morph.atomize(word)
        except Exception:
            failed += 1
            continue
        if not a or not a.atoms:
            failed += 1
            continue
        # Build the gloss string: prefix:atom1.atom2.atom3 (semantic glosses)
        atom_glosses = [g for _, _, g in a.atoms]
        gloss_atoms.update(atom_glosses)
        if a.prefix:
            gloss_str = f"{a.prefix}:" + ".".join(atom_glosses)
        else:
            gloss_str = ".".join(atom_glosses)
        pairs.append({
            'token': word,
            'frequency': freq,
            'gloss': gloss_str,
            'prefix': a.prefix,
            'atoms': [(c, r, g) for c, r, g in a.atoms],
            'is_headless': a.is_headless,
            'e_depth': a.e_depth,
            'i_depth': a.i_depth,
        })
    print(f"Total unique H-track tokens: {len(token_freq)}")
    print(f"Successfully atomized:        {len(pairs)}")
    print(f"Failed:                       {failed}")

    print(f"\nUnique semantic atoms in glosses: {len(gloss_atoms)}")
    print(f"  {sorted(gloss_atoms)}")

    # Build prefix vocabulary
    prefixes = Counter(p['prefix'] for p in pairs if p['prefix'])
    print(f"\nUnique prefixes: {len(prefixes)}")
    print(f"  Top: {prefixes.most_common(15)}")

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / 'gloss_pairs.jsonl'
    with open(out_path, 'w', encoding='utf-8') as f:
        for p in sorted(pairs, key=lambda x: -x['frequency']):
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print(f"\nSaved: {out_path}")

    # Vocab
    vocab_path = DATA_DIR / 'gloss_vocab.json'
    vocab = {
        'semantic_atoms': sorted(gloss_atoms),
        'prefixes': sorted(prefixes.keys()),
        'roles': ['HEAD', 'MOD', 'TERM', 'SOLE', 'PSEUDO_HEAD'],
    }
    vocab_path.write_text(json.dumps(vocab, indent=2, ensure_ascii=False))
    print(f"Saved: {vocab_path}")

    # Show 10 random samples
    import random
    rng = random.Random(691)
    rng.shuffle(pairs)
    print(f"\n=== Sample (token, gloss) pairs ===")
    for p in pairs[:15]:
        print(f"  {p['token']:>15s} (×{p['frequency']:>4d})  →  {p['gloss']}")


if __name__ == '__main__':
    main()
