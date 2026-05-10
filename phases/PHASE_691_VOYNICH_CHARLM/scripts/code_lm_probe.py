#!/usr/bin/env python3
"""
Phase 691.x: Code-strong LM perplexity probe of Voynich.

Hypothesis: if Voynich is procedural/control-grammar notation (per C1430,
C1025, C1394), a model with strong code priors should give it lower perplexity
than a model would give random gibberish, AND its perplexity profile should
be closer to code than to natural language.

Comparison corpora (all ~50 lines each, normalized to similar length):
  1. Voynich H-track (target)
  2. Random-shuffled Voynich (control: same tokens, no structure)
  3. Char-permuted Voynich within tokens (control: same chars, no token structure)
  4. Real Python code (positive control: known code-like)
  5. Real Latin prose (negative control: known natural language)
  6. Real English prose (negative control)

Pre-registered prediction:
  Voynich perplexity < random-shuffled perplexity (>20% lower) → has structure
  Voynich perplexity / Latin perplexity < 1.5 → looks "language-like"
  Voynich perplexity / Python perplexity < 1.5 → looks "code-like"

Diagnostic interpretation:
  If Voynich-vs-code ratio < Voynich-vs-Latin ratio: model sees Voynich as
  more code-like than language-like. (External corroboration of procedural
  notation framing.)
"""
import argparse
import functools
import json
import math
import random
import sys
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PHASE_DIR.parents[1]


def load_model(model_name, device):
    """Load HuggingFace causal LM + tokenizer."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"  Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16,
        device_map=device, trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def compute_perplexity(model, tokenizer, text, device, max_length=512):
    """Compute mean per-token negative log-likelihood (cross-entropy in nats)."""
    enc = tokenizer(text, return_tensors='pt', truncation=True, max_length=max_length)
    input_ids = enc['input_ids'].to(device)
    if input_ids.shape[1] < 2:
        return None, 0
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        loss = outputs.loss.item()
    return loss, input_ids.shape[1] - 1


def voynich_lines(n=50, seed=691):
    """Sample N Voynich H-track lines from the test split."""
    path = PHASE_DIR / 'data' / 'corpus_test.jsonl'
    lines = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r['tokens'] and len(r['tokens']) >= 5:
                lines.append(' '.join(r['tokens']))
    rng = random.Random(seed)
    rng.shuffle(lines)
    return lines[:n]


def shuffled_voynich(n=50, seed=691):
    """Same line-token counts but randomly assembled tokens from corpus."""
    rng = random.Random(seed)
    all_tokens = []
    for split in ('train', 'val', 'test'):
        path = PHASE_DIR / 'data' / f'corpus_{split}.jsonl'
        with open(path, encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                all_tokens.extend(r['tokens'])
    out = []
    for _ in range(n):
        line_len = rng.randint(8, 15)
        line = ' '.join(rng.sample(all_tokens, line_len))
        out.append(line)
    return out


def char_permuted_voynich(n=50, seed=691):
    """Real Voynich tokens but chars shuffled within each token."""
    base = voynich_lines(n, seed)
    rng = random.Random(seed + 1)
    out = []
    for line in base:
        scrambled = []
        for tok in line.split():
            chars = list(tok)
            rng.shuffle(chars)
            scrambled.append(''.join(chars))
        out.append(' '.join(scrambled))
    return out


def python_code_lines(n=50, seed=691):
    """Sample real Python code lines (use this script's directory)."""
    rng = random.Random(seed)
    code_lines = []
    for p in (PHASE_DIR / 'scripts').glob('*.py'):
        if p.name.startswith('_'):
            continue
        with open(p, encoding='utf-8') as f:
            for line in f:
                stripped = line.rstrip()
                if 30 <= len(stripped) <= 200:
                    code_lines.append(stripped)
    rng.shuffle(code_lines)
    # Group into chunks of ~5 lines for fair comparison with Voynich line lengths
    chunks = []
    for i in range(0, min(len(code_lines), n * 5), 5):
        chunks.append('\n'.join(code_lines[i:i + 5]))
    return chunks[:n]


def latin_lines(n=50, seed=691):
    """Sample real Latin prose lines from SISMEL Liber Mercuriorum."""
    chap_path = PHASE_DIR / 'data' / 'sismel_liber_mercuriorum_latin.json'
    chapters = json.loads(chap_path.read_text(encoding='utf-8'))
    rng = random.Random(seed)
    chunks = []
    for ch_text in chapters.values():
        words = ch_text.split()
        # 12-25 word chunks comparable to Voynich line lengths
        if len(words) < 30:
            continue
        for i in range(0, len(words) - 15, 18):
            chunk = ' '.join(words[i:i + 18])
            chunks.append(chunk)
    rng.shuffle(chunks)
    return chunks[:n]


def english_lines(n=50, seed=691):
    """Sample English prose from Brunschwig 1512 translation."""
    path = PROJECT_ROOT / 'sources/brunschwig_1512/brunschwig_1512_english.txt'
    # Fall back to the lang_english corpus we already built for Phase 691.6
    if not path.exists():
        path2 = PHASE_DIR / 'data' / 'lang_english' / 'corpus_test.jsonl'
        if path2.exists():
            sentences = []
            with open(path2, encoding='utf-8') as f:
                for line in f:
                    r = json.loads(line)
                    text = r.get('text', '')
                    words = text.split()
                    if 12 <= len(words) <= 25:
                        sentences.append(text)
            rng = random.Random(seed)
            rng.shuffle(sentences)
            return sentences[:n]
        return []
    text = path.read_text(encoding='utf-8', errors='ignore')
    sentences = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if 12 <= len(words) <= 25:
            sentences.append(line)
    rng = random.Random(seed)
    rng.shuffle(sentences)
    return sentences[:n]


def random_chars(n=50, seed=691):
    """Truly random char strings (negative-negative control - should be highest perplexity)."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        chunk_len = rng.randint(60, 150)
        chunk = ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz ') for _ in range(chunk_len))
        out.append(chunk)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='microsoft/Phi-3.5-mini-instruct')
    parser.add_argument('--n-samples', type=int, default=50)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--max-length', type=int, default=256)
    args = parser.parse_args()

    device = args.device if torch.cuda.is_available() else 'cpu'
    print(f"Loading model: {args.model}")
    model, tokenizer = load_model(args.model, device)
    print(f"  Vocab size: {len(tokenizer)}")

    # Build all corpora
    print(f"\nBuilding test corpora ({args.n_samples} samples each)...")
    corpora = {
        'voynich':         voynich_lines(args.n_samples),
        'voynich_shuffled': shuffled_voynich(args.n_samples),
        'voynich_charperm': char_permuted_voynich(args.n_samples),
        'python_code':      python_code_lines(args.n_samples),
        'latin_prose':      latin_lines(args.n_samples),
        'english_prose':    english_lines(args.n_samples),
        'random_chars':     random_chars(args.n_samples),
    }
    for name, samples in corpora.items():
        print(f"  {name:20s}: {len(samples)} samples, sample: {repr(samples[0][:60])[:80]}")

    # Compute perplexity for each
    print(f"\n=== Computing perplexity ===")
    results = {}
    for name, samples in corpora.items():
        losses = []
        n_total_tokens = 0
        for text in samples:
            loss, n_tok = compute_perplexity(model, tokenizer, text, device,
                                              max_length=args.max_length)
            if loss is None:
                continue
            losses.append(loss)
            n_total_tokens += n_tok
        mean_loss_nats = float(np.mean(losses))
        mean_bits_per_token = mean_loss_nats / math.log(2)
        ppl = math.exp(min(20, mean_loss_nats))
        results[name] = {
            'mean_loss_nats': mean_loss_nats,
            'mean_bits_per_token': mean_bits_per_token,
            'perplexity': ppl,
            'std_loss': float(np.std(losses)),
            'n_samples': len(losses),
            'n_total_tokens': n_total_tokens,
        }
        print(f"  {name:20s}  bpt={mean_bits_per_token:>6.2f}  ppl={ppl:>8.1f}  std={np.std(losses):.3f}")

    # Comparisons
    print(f"\n=== Pre-registered comparisons ===")
    voy = results['voynich']['mean_bits_per_token']
    shuf = results['voynich_shuffled']['mean_bits_per_token']
    charperm = results['voynich_charperm']['mean_bits_per_token']
    code = results['python_code']['mean_bits_per_token']
    latin = results['latin_prose']['mean_bits_per_token']
    english = results['english_prose']['mean_bits_per_token']
    rand = results['random_chars']['mean_bits_per_token']

    print(f"\n  [Test 1] Does Voynich have structure? (vs random/shuffled)")
    print(f"    Voynich:           {voy:.3f} bpt")
    print(f"    Voynich shuffled:  {shuf:.3f} bpt  ({100*(shuf-voy)/voy:+.1f}% vs Voynich)")
    print(f"    Voynich charperm:  {charperm:.3f} bpt  ({100*(charperm-voy)/voy:+.1f}% vs Voynich)")
    print(f"    Random chars:      {rand:.3f} bpt  ({100*(rand-voy)/voy:+.1f}% vs Voynich)")
    has_structure = voy < shuf * 0.95
    print(f"    PASS Test 1 (Voynich < shuffled by >5%): {has_structure}")

    print(f"\n  [Test 2] Is Voynich more code-like or language-like?")
    print(f"    Voynich:           {voy:.3f} bpt")
    print(f"    Python code:       {code:.3f} bpt  (Voynich/code ratio: {voy/code:.2f}x)")
    print(f"    Latin prose:       {latin:.3f} bpt  (Voynich/latin ratio: {voy/latin:.2f}x)")
    print(f"    English prose:     {english:.3f} bpt  (Voynich/english ratio: {voy/english:.2f}x)")

    code_ratio = voy / code
    lang_ratio = voy / ((latin + english) / 2)
    print(f"\n    Voynich-to-code ratio:     {code_ratio:.2f}x")
    print(f"    Voynich-to-language ratio: {lang_ratio:.2f}x")
    if code_ratio < lang_ratio * 0.85:
        verdict = 'CODE_LIKE'
    elif lang_ratio < code_ratio * 0.85:
        verdict = 'LANGUAGE_LIKE'
    else:
        verdict = 'NEITHER_OR_BOTH'
    print(f"    Verdict: {verdict}")

    # Save
    out = {
        'model': args.model,
        'n_samples_per_corpus': args.n_samples,
        'results': results,
        'has_structure': bool(has_structure),
        'code_ratio': float(code_ratio),
        'lang_ratio': float(lang_ratio),
        'verdict': verdict,
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'code_lm_probe.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
