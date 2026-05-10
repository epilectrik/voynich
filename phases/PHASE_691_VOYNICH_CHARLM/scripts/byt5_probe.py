#!/usr/bin/env python3
"""
Phase 691.x: ByT5 char-level perplexity probe.

ByT5 operates on bytes (no BPE), so it directly tests whether the TinyLlama
result was a tokenization artifact. Same corpora, same comparison, but
char-level so structure should be visible if it's there.

Pre-registered prediction (per crazy-expert):
  If ByT5 distinguishes Voynich from shuffled at >60%: BPE-mismatch story
    confirmed; the original probe is reframed cleanly.
  If ByT5 ALSO fails to distinguish: stronger Tier 2 candidate about Voynich's
    structure being below even char-level pretrained-model resolution.

Reports bits-per-CHARACTER (not per-token) for proper cross-corpus comparison.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_lm_probe import (
    voynich_lines, shuffled_voynich, char_permuted_voynich,
    python_code_lines, latin_lines, english_lines, random_chars,
)


def compute_byt5_bpc(model, tokenizer, text, device, max_length=512):
    """Compute mean bits per CHARACTER using ByT5 conditional perplexity.

    ByT5 is encoder-decoder; we use it as masked language model:
    encode source as text + decode target as text, score the decoder's
    cross-entropy. For "raw text perplexity" we feed the same text as
    both source and target with a span-mask transformation.

    Simpler approach: use the LM (T5) score-mode. Tokenize the text byte
    by byte, then for each position compute teacher-forced next-byte
    probability via the encoder-decoder.

    For comparison with TinyLlama we use a simpler proxy: encode the text
    as decoder-only via the cross-entropy of generating the text itself
    given a fixed prefix.
    """
    # Use ByT5's encoder-only approach for entropy estimation:
    # Mask each character position, predict it, sum the log-probs.
    # This is masked-LM perplexity, comparable across corpora.
    enc = tokenizer(text, return_tensors='pt', truncation=True, max_length=max_length)
    input_ids = enc['input_ids'].to(device)
    n_chars = input_ids.shape[1] - 1  # subtract EOS
    if n_chars < 5:
        return None, 0
    # ByT5 uses sentinel tokens for masking. Mask one position at a time, predict.
    # For efficiency, use a single forward pass with chunked masking.
    # Simpler: use the CausalLM-like forward pass via score_text utility.
    # T5 has labels= for cross-entropy training. Use that.
    with torch.no_grad():
        # Source = text with no masks; target = text shifted
        # But T5 doesn't naturally compute autoregressive LL.
        # Use teacher-forcing: source is empty/prefix, target is the text.
        # The decoder cross-entropy will then approximate per-byte LL.
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
        source_ids = torch.tensor([[pad_id]], device=device)
        target_ids = input_ids
        outputs = model(input_ids=source_ids, labels=target_ids)
        loss = outputs.loss.item()
    bits_per_byte = loss / math.log(2)
    return bits_per_byte, n_chars


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='google/byt5-small')
    parser.add_argument('--n-samples', type=int, default=50)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--max-length', type=int, default=512)
    args = parser.parse_args()

    from transformers import AutoTokenizer, T5ForConditionalGeneration
    device = args.device if torch.cuda.is_available() else 'cpu'
    print(f"Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = T5ForConditionalGeneration.from_pretrained(
        args.model, torch_dtype=torch.float16,
    ).to(device)
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  Params: {n_params:,}")

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

    print(f"\n=== Computing per-character bits ===")
    results = {}
    individual = {}
    for name, samples in corpora.items():
        bpcs = []
        for text in samples:
            bpc, n = compute_byt5_bpc(model, tokenizer, text, device, args.max_length)
            if bpc is None:
                continue
            bpcs.append(bpc)
        results[name] = {
            'mean_bpc': float(np.mean(bpcs)),
            'std_bpc': float(np.std(bpcs)),
            'median_bpc': float(np.median(bpcs)),
            'n_samples': len(bpcs),
        }
        individual[name] = bpcs
        print(f"  {name:20s}  bpc={np.mean(bpcs):>6.3f}  std={np.std(bpcs):>5.3f}  median={np.median(bpcs):>6.3f}  n={len(bpcs)}")

    # Statistical test: can ByT5 distinguish Voynich from shuffled?
    print(f"\n=== Statistical tests ===")
    from scipy import stats
    real_bpc = np.array(individual['voynich'])
    shuf_bpc = np.array(individual['voynich_shuffled'])
    char_bpc = np.array(individual['voynich_charperm'])
    rand_bpc = np.array(individual['random_chars'])

    if len(real_bpc) and len(shuf_bpc):
        u_stat, p = stats.mannwhitneyu(real_bpc, shuf_bpc, alternative='two-sided')
        print(f"  Voynich vs shuffled: Mann-Whitney p = {p:.4f}")
        # Classifier accuracy: optimal threshold
        all_bpc = np.concatenate([real_bpc, shuf_bpc])
        labels = np.array([0]*len(real_bpc) + [1]*len(shuf_bpc))
        sorted_bpc = np.sort(all_bpc)
        best_acc = 0.5
        for t in sorted_bpc:
            preds = (all_bpc >= t).astype(int)
            acc = max((preds == labels).mean(), (preds == 1 - labels).mean())
            if acc > best_acc:
                best_acc = acc
        print(f"  Voynich vs shuffled: classifier accuracy {best_acc:.3f}")
    else:
        p, best_acc = None, None

    if len(real_bpc) and len(char_bpc):
        u_stat2, p2 = stats.mannwhitneyu(real_bpc, char_bpc, alternative='two-sided')
        print(f"  Voynich vs char-permuted: Mann-Whitney p = {p2:.4f}")
    if len(real_bpc) and len(rand_bpc):
        u_stat3, p3 = stats.mannwhitneyu(real_bpc, rand_bpc, alternative='two-sided')
        print(f"  Voynich vs random chars:  Mann-Whitney p = {p3:.4f}")

    # Verdict
    print(f"\n=== Verdict (per pre-registered criterion) ===")
    if p is not None:
        if best_acc >= 0.60:
            verdict = 'CHAR_LEVEL_DISTINGUISHES'
            print(f"  ByT5 distinguishes Voynich from shuffled at acc={best_acc:.2f}")
            print(f"  → BPE-mismatch story confirmed: TinyLlama failure was tokenization")
            print(f"  → ByT5 char-level resolution can see Voynich's structure")
        elif best_acc >= 0.55:
            verdict = 'WEAK_DISTINCTION'
            print(f"  ByT5 weakly distinguishes (acc={best_acc:.2f})")
            print(f"  → Some signal recoverable at char level, but pretrained priors")
            print(f"     are still mismatched")
        else:
            verdict = 'CHAR_LEVEL_BLIND'
            print(f"  ByT5 ALSO cannot distinguish Voynich from shuffled (acc={best_acc:.2f})")
            print(f"  → Voynich's structure is below pretrained char-LM resolution")
            print(f"  → Stronger Tier 2 candidate")

    out = {
        'model': args.model,
        'n_params': n_params,
        'n_samples_per_corpus': args.n_samples,
        'results': results,
        'voynich_vs_shuffled_p': float(p) if p else None,
        'voynich_vs_shuffled_classifier_acc': float(best_acc) if best_acc else None,
        'verdict': verdict if p is not None else None,
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'byt5_probe.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
