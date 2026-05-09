#!/usr/bin/env python3
"""Test the trained glosser on novel synthetic tokens.

Real test: did it learn the atomization RULE, or just memorize the corpus
mapping? Generate synthetic tokens, glossed by the actual atomize() function,
and see if the model produces matching glosses.
"""
import json
import sys
from pathlib import Path

import torch

PHASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PHASE_DIR.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Morphology
from train_glosser import GlosserGPT, gloss_token, encode_input


def main():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    ckpt = torch.load(PHASE_DIR / 'results' / 'training_glosser' / 'glosser.pt',
                      map_location=device, weights_only=False)
    vocab = ckpt['vocab']
    char_to_id = {c: i for i, c in enumerate(vocab)}
    id_to_char = {i: c for c, i in char_to_id.items()}
    model = GlosserGPT(vocab_size=len(vocab)).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    print(f"Loaded glosser. Vocab size: {len(vocab)}")

    # Test 1: Token in training set (corpus)
    print(f"\n[1] Tokens from training corpus:")
    morph = Morphology()
    corpus_tokens = ['qokeedy', 'chedy', 'daiin', 'shedy', 'okeey', 'cthedy']
    correct = 0
    for tok in corpus_tokens:
        truth = morph.atomize(tok).gloss
        pred = gloss_token(model, tok, char_to_id, id_to_char, device)
        match = pred == truth
        correct += match
        print(f"  {tok:>10s}  pred={pred:<30s}  truth={truth:<30s}  {'✓' if match else '✗'}")
    print(f"  {correct}/{len(corpus_tokens)} correct")

    # Test 2: Held-out / unseen / made-up tokens that COULD be Voynichese
    # These follow Voynichese morphology but are not necessarily in the corpus
    print(f"\n[2] Made-up Voynichese-shaped tokens (test rule learning):")
    unseen_tokens = [
        'qokeeeody',     # qo + multi-e + deeper
        'chokar',        # ch + ok + ar
        'tcheoldy',      # tch + e + ol + dy
        'qoteeey',       # qo + t + multi-e + y
        'shokchey',      # sh + ok + ch + ey
        'pcheo',         # pch + eo
        'okchodam',      # ok + ch + odam
        'qotaiin',       # qo + taiin
    ]
    rule_correct = 0
    for tok in unseen_tokens:
        try:
            truth = morph.atomize(tok).gloss
        except Exception:
            truth = '(atomize failed)'
        pred = gloss_token(model, tok, char_to_id, id_to_char, device)
        match = pred == truth
        rule_correct += match
        print(f"  {tok:>12s}  pred={pred:<30s}  truth={truth:<30s}  {'✓' if match else '✗'}")
    print(f"  {rule_correct}/{len(unseen_tokens)} correct on novel tokens")

    # Test 3: Made-up tokens that violate Voynichese morphology
    print(f"\n[3] Non-Voynichese tokens (off-distribution):")
    odd_tokens = ['xxqq', 'aaaa', 'kkkkk', 'mnoiu', 'qqqq']
    for tok in odd_tokens:
        try:
            truth = morph.atomize(tok).gloss
        except Exception:
            truth = '(atomize failed)'
        pred = gloss_token(model, tok, char_to_id, id_to_char, device)
        print(f"  {tok:>12s}  pred={pred:<30s}  truth={truth}")

    # Test 4: Bulk eval on val set
    print(f"\n[4] Held-out val set evaluation (sequence-level exact match):")
    pairs = []
    with open(PHASE_DIR / 'data' / 'gloss_pairs.jsonl', encoding='utf-8') as f:
        for line in f:
            pairs.append(json.loads(line))
    import random
    rng = random.Random(691)
    rng.shuffle(pairs)
    n_val = max(50, len(pairs) // 10)
    val_pairs = pairs[:n_val]
    n_correct = 0
    for p in val_pairs:
        pred = gloss_token(model, p['token'], char_to_id, id_to_char, device)
        if pred == p['gloss']:
            n_correct += 1
    print(f"  Val exact-match accuracy: {n_correct}/{len(val_pairs)} = {100*n_correct/len(val_pairs):.1f}%")


if __name__ == '__main__':
    main()
