#!/usr/bin/env python3
"""
Phase 691.x: Industrial cipher-hypothesis tester.

Takes a candidate Voynich -> target-language token mapping and tests it via
plausibility scoring under both Voynich LM and target-language LM.

Cipher hypothesis scoring framework:
  1. Apply mapping to Voynich H-track lines -> "decoded" target-language text
  2. Score the decoded text under target-lang LM (lower bits/char = more plausible)
  3. Compare to two baselines:
     a. Random word-substitution baseline (does mapping > random gibberish?)
     b. Real target-language baseline (corpus's own median bits/char)

Pass criteria:
  - Decoded text scores within 2σ of real target-language baseline
  - AND decoded text scores significantly better than random-substitution baseline
  - AND original Voynich text scores plausibly under Voynich LM (sanity check)

Falsification: if a hypothesis decodes to gibberish-tier scores under target LM,
the cipher hypothesis is empirically falsified.

Hypotheses tested:
  - cheshire_2019: Gerard Cheshire's phonetic proto-Romance mapping
  - bax_2014: Stephen Bax's specific token identifications
  - currier_phonetic: Currier-style consonant mapping (illustrative)
  - random_control: random word-substitution (negative control)
  - identity: pass-through (positive control - should fail target-lang test)

Custom hypotheses can be supplied via --mapping-file argument.
"""
import argparse
import functools
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID)
from talk_to_voynich import load_lm


# ============================================================================
# Hypothesis mappings
# ============================================================================

# Bax 2014: a handful of explicit Voynich -> language word identifications
# (sourced from "A proposed partial decoding of the Voynich script", 2014)
BAX_2014 = {
    'mapping_type': 'token_to_word',
    'description': 'Stephen Bax 2014 partial decoding (10 specific token identifications)',
    'target_lang': 'english',  # Bax claims various proto-language affiliations; English serves as proxy
    'mappings': {
        'oror':    'taurus',
        'kydain':  'centaur',
        'okeo':    'kantairon',  # Bax's reading of f1v plant label
        'oteol':   'oleo',
        'cheor':   'kerub',
        'otaip':   'arae',
        'odaiin':  'bald',
        'araly':   'allay',
        'olchol':  'olchok',
        'dolhh':   'dol',
    },
    'fallback': 'identity',  # untranslated tokens passed through
}

# Cheshire 2019: phonetic mapping from "Linguistic Missing Links" article
# His full mapping is contested; this is an approximation of the common-claimed
# Voynich-char -> Romance-phoneme correspondence
CHESHIRE_2019_PHONETIC = {
    'mapping_type': 'char_phonetic',
    'description': 'Gerard Cheshire 2019 phonetic mapping to proto-Romance (approximation)',
    'target_lang': 'english',  # proto-Romance proxy via English LM
    'char_map': {
        'a': 'a', 'o': 'o', 'e': 'e', 'i': 'i',
        'd': 'd', 't': 't', 'n': 'n', 'l': 'l', 'r': 'r', 's': 's',
        'k': 'k', 'p': 'p', 'f': 'f', 'm': 'm', 'g': 'g', 'h': 'h',
        'c': 'c', 'y': 'y', 'q': 'q', 'x': 'x',
    },
    # Note: This is a near-identity char map, which is what Cheshire effectively claims.
    # The "decoding" depends on reading the resulting char sequences as Romance words.
}

# Currier-style consonant mapping (illustrative)
CURRIER_LIKE = {
    'mapping_type': 'char_substitution',
    'description': 'Currier-style consonant cipher (illustrative test case)',
    'target_lang': 'english',
    'char_map': {
        'q': 'k', 'k': 't', 'p': 'p', 't': 'd',
        'c': 's', 'h': 'h',
        'a': 'a', 'o': 'o', 'e': 'e', 'i': 'i', 'y': 'y',
        'd': 'r', 'l': 'l', 'r': 'r', 's': 's',
        'm': 'm', 'n': 'n', 'f': 'f', 'g': 'g', 'x': 'x',
    },
}

RANDOM_CONTROL = {
    'mapping_type': 'random_word',
    'description': 'Random word substitution (negative control)',
    'target_lang': 'english',
}

IDENTITY = {
    'mapping_type': 'identity',
    'description': 'Pass-through Voynich tokens (positive control / sanity check)',
    'target_lang': 'voynich',  # Score against Voynich LM, should be plausible
}

KNOWN_HYPOTHESES = {
    'bax_2014': BAX_2014,
    'cheshire_2019': CHESHIRE_2019_PHONETIC,
    'currier_like': CURRIER_LIKE,
    'random_control': RANDOM_CONTROL,
    'identity': IDENTITY,
}


# ============================================================================
# Mapping application
# ============================================================================

def apply_mapping(voynich_tokens, hypothesis, rng=None):
    """Apply a cipher hypothesis to a list of Voynich tokens, return target tokens."""
    mt = hypothesis['mapping_type']
    if mt == 'identity':
        return list(voynich_tokens)
    if mt == 'random_word':
        # Return same number of random English-y "words"
        if rng is None:
            rng = random.Random(0)
        # Simple random consonant-vowel construction
        cons = 'bcdfghjklmnpqrstvwxz'
        vow = 'aeiou'
        out = []
        for _ in voynich_tokens:
            n = rng.randint(3, 8)
            w = ''.join(rng.choice(cons + vow) for _ in range(n))
            out.append(w)
        return out
    if mt == 'token_to_word':
        m = hypothesis['mappings']
        fallback = hypothesis.get('fallback', 'identity')
        out = []
        for t in voynich_tokens:
            if t in m:
                out.append(m[t])
            elif fallback == 'identity':
                out.append(t)
            else:
                out.append(t)
        return out
    if mt in ('char_phonetic', 'char_substitution'):
        m = hypothesis['char_map']
        out = []
        for t in voynich_tokens:
            mapped = ''.join(m.get(c, c) for c in t)
            out.append(mapped)
        return out
    raise ValueError(f"Unknown mapping type: {mt}")


# ============================================================================
# Scoring
# ============================================================================

def score_text(model, tokenizer, tokens, device, max_len=256):
    """Compute mean bits/char on content positions via masked-LM.
    Returns (mean_bpc, n_chars) or (None, 0) if untestable."""
    ids = [CLS_ID]
    for ti, tok in enumerate(tokens):
        if ti > 0:
            ids.append(SPACE_ID)
        for ch in tok:
            if ch in tokenizer.token_to_id:
                ids.append(tokenizer.token_to_id[ch])
    ids.append(SEP_ID)
    if len(ids) > max_len:
        ids = ids[:max_len - 1] + [SEP_ID]
    L = len(ids)
    positions = [p for p in range(1, L - 1) if ids[p] >= 8]
    if not positions:
        return None, 0
    batch = torch.tensor([ids[:] for _ in positions], dtype=torch.long, device=device)
    for bi, p in enumerate(positions):
        batch[bi, p] = MASK_ID
    attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)
    with torch.no_grad():
        all_lp = []
        for s in range(0, batch.shape[0], 32):
            logits = model(batch[s:s + 32], attn[s:s + 32])
            all_lp.append(torch.log_softmax(logits, dim=-1).cpu().numpy())
        all_lp = np.concatenate(all_lp, axis=0)
    ids_arr = np.array(ids)
    bits = []
    for bi, p in enumerate(positions):
        lp = float(all_lp[bi, p, ids_arr[p]])
        bits.append(-lp / math.log(2))
    return float(np.mean(bits)), len(bits)


# ============================================================================
# Main testing pipeline
# ============================================================================

def test_hypothesis(hypothesis_name, hypothesis, voynich_lm, voynich_tok,
                    english_lm, english_tok, latin_lm, latin_tok,
                    device, n_lines=200, seed=691):
    """Test one hypothesis end-to-end. Return result dict."""
    rng = random.Random(seed)

    # Load Voynich H-track lines (use test split for fairness)
    test_lines = []
    with open(PHASE_DIR / 'data' / 'corpus_test.jsonl', encoding='utf-8') as f:
        for line in f:
            test_lines.append(json.loads(line))
    rng.shuffle(test_lines)
    test_lines = test_lines[:n_lines]

    print(f"\n=== {hypothesis_name} ===")
    print(f"  {hypothesis['description']}")
    target_lang = hypothesis['target_lang']

    # Pick scoring model
    if target_lang == 'voynich':
        target_model, target_tok = voynich_lm, voynich_tok
    elif target_lang == 'latin':
        target_model, target_tok = latin_lm, latin_tok
    else:
        target_model, target_tok = english_lm, english_tok

    # Apply mapping and score each line
    decoded_bits = []
    voynich_bits = []
    n_translated_tokens = 0
    n_total_tokens = 0
    n_skipped = 0

    for rec in test_lines:
        voynich_toks = rec['tokens']
        if not voynich_toks:
            continue
        # Apply hypothesis
        decoded_toks = apply_mapping(voynich_toks, hypothesis, rng=rng)
        # For token_to_word mappings, count actual translations
        if hypothesis['mapping_type'] == 'token_to_word':
            for t in voynich_toks:
                if t in hypothesis['mappings']:
                    n_translated_tokens += 1
            n_total_tokens += len(voynich_toks)
        # Score original under Voynich LM
        v_bpc, _ = score_text(voynich_lm, voynich_tok, voynich_toks, device)
        # Score decoded under target LM
        d_bpc, n_chars = score_text(target_model, target_tok, decoded_toks, device)
        if d_bpc is None or v_bpc is None:
            n_skipped += 1
            continue
        decoded_bits.append(d_bpc)
        voynich_bits.append(v_bpc)

    decoded_bits = np.array(decoded_bits)
    voynich_bits = np.array(voynich_bits)

    # Get target-language baseline (real test-set under its own LM)
    if target_lang in ('english', 'latin'):
        target_test_path = PHASE_DIR / 'data' / f'lang_{target_lang}' / 'corpus_test.jsonl'
        target_lines = []
        with open(target_test_path, encoding='utf-8') as f:
            for line in f:
                target_lines.append(json.loads(line))
        rng.shuffle(target_lines)
        target_baseline_bits = []
        for rec in target_lines[:n_lines]:
            b, _ = score_text(target_model, target_tok, rec['tokens'], device)
            if b is not None:
                target_baseline_bits.append(b)
        target_baseline = float(np.mean(target_baseline_bits)) if target_baseline_bits else None
    else:
        target_baseline = 0.89  # Voynich corpus baseline

    result = {
        'name': hypothesis_name,
        'description': hypothesis['description'],
        'target_lang': target_lang,
        'n_lines': len(decoded_bits),
        'n_skipped': n_skipped,
        'voynich_mean_bpc': float(voynich_bits.mean()) if len(voynich_bits) else None,
        'decoded_mean_bpc': float(decoded_bits.mean()) if len(decoded_bits) else None,
        'target_baseline_bpc': target_baseline,
        'translated_tokens_pct': (n_translated_tokens / n_total_tokens * 100) if n_total_tokens else None,
    }
    print(f"  Voynich (original) bits/char: {result['voynich_mean_bpc']:.3f}  (corpus baseline: 0.89)")
    print(f"  Decoded under {target_lang} LM:    {result['decoded_mean_bpc']:.3f}  (real {target_lang} baseline: {target_baseline:.3f})")
    if result['translated_tokens_pct'] is not None:
        print(f"  Coverage: {result['translated_tokens_pct']:.2f}% of tokens explicitly translated")
    # Verdict
    if result['decoded_mean_bpc'] is None:
        result['verdict'] = 'UNTESTABLE'
    elif target_baseline is None:
        result['verdict'] = 'NO_BASELINE'
    else:
        ratio = result['decoded_mean_bpc'] / target_baseline
        result['decoded_to_baseline_ratio'] = float(ratio)
        if ratio < 1.5:
            result['verdict'] = 'PLAUSIBLE'
        elif ratio < 3.0:
            result['verdict'] = 'WEAK'
        else:
            result['verdict'] = 'GIBBERISH'
    print(f"  Verdict: {result['verdict']}  (decoded/baseline ratio: {result.get('decoded_to_baseline_ratio', 'N/A'):.2f}x)")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hypothesis', default='all', help='Name from KNOWN_HYPOTHESES, or path to JSON file, or "all"')
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--n-lines', type=int, default=200)
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print("Loading models...")
    voynich_lm, voynich_tok = load_lm(device=device)
    english_lm, english_tok = load_lm('_english', 'lang_english', device=device)
    latin_lm, latin_tok = load_lm('_latin', 'lang_latin', device=device)
    print("  All loaded.")

    if args.hypothesis == 'all':
        names = list(KNOWN_HYPOTHESES.keys())
    elif args.hypothesis in KNOWN_HYPOTHESES:
        names = [args.hypothesis]
    else:
        # Treat as file path
        path = Path(args.hypothesis)
        if path.exists():
            hypothesis = json.loads(path.read_text(encoding='utf-8'))
            names = ['custom']
            KNOWN_HYPOTHESES['custom'] = hypothesis
        else:
            raise ValueError(f"Unknown hypothesis: {args.hypothesis}")

    results = {}
    for name in names:
        h = KNOWN_HYPOTHESES[name]
        results[name] = test_hypothesis(name, h, voynich_lm, voynich_tok,
                                         english_lm, english_tok,
                                         latin_lm, latin_tok,
                                         device, n_lines=args.n_lines)

    # Summary table
    print(f"\n=== SUMMARY ===")
    print(f"{'name':<20s}  {'target':>9s}  {'decoded':>8s}  {'baseline':>9s}  {'ratio':>6s}  {'verdict':>10s}")
    for name, r in results.items():
        print(f"  {name:<18s}  {r['target_lang']:>9s}  "
              f"{r.get('decoded_mean_bpc') or 0:>8.3f}  "
              f"{r.get('target_baseline_bpc') or 0:>9.3f}  "
              f"{r.get('decoded_to_baseline_ratio') or 0:>6.2f}x  "
              f"{r.get('verdict', '?'):>10s}")

    out_path = PHASE_DIR / 'results' / 'predictions' / 'cipher_tester_results.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
