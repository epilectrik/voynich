"""5-gram null audit framework — reusable across batches.

Expert-audited 2026-05-28. Critical additions:
- Held-out folio split (80/20) — train on 80%, measure on 20% real + matched-structure synth
- Near-zero rail for prohibition claims
- Fractional thresholds in addition to absolute
- Surface-fact vs mechanism claim-type flagging
"""
from __future__ import annotations
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript


def load_real_currier_b_lines(exclude_labels: bool = True) -> tuple[list[list[str]], list[str]]:
    """Returns (lines, line_folios). Currier B, H-track, no labels/uncertain."""
    tx = Transcript()
    lines_dict = defaultdict(list)
    for t in tx.currier_b(exclude_labels=exclude_labels, exclude_uncertain=True):
        w = t.word.strip()
        if not w or '*' in w:
            continue
        lines_dict[(t.folio, t.line)].append(w)
    lines = []
    line_folios = []
    for key in sorted(lines_dict.keys()):
        lines.append(lines_dict[key])
        line_folios.append(key[0])
    return lines, line_folios


def holdout_split(lines: list[list[str]], line_folios: list[str], holdout_frac: float = 0.20, seed: int = 42):
    """Random 80/20 folio-level split. Returns (train_lines, holdout_lines, train_folios, holdout_folios)."""
    rng = random.Random(seed)
    folios = sorted(set(line_folios))
    rng.shuffle(folios)
    n_holdout = max(1, int(round(len(folios) * holdout_frac)))
    holdout_folios = set(folios[:n_holdout])
    train_folios = set(folios[n_holdout:])
    train_lines = [l for l, f in zip(lines, line_folios) if f in train_folios]
    holdout_lines = [l for l, f in zip(lines, line_folios) if f in holdout_folios]
    return train_lines, holdout_lines, train_folios, holdout_folios


def train_5gram(line_word_lists: list[list[str]], order: int = 5):
    counts = defaultdict(Counter)
    for words in line_word_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_line(counts, order: int, target_token_count: int, rng: random.Random) -> list[str]:
    out_tokens = []
    ctx = '\x01' * (order - 1)
    buf = []
    attempts = 0
    while len(out_tokens) < target_token_count and attempts < target_token_count * 60:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1)
            continue
        chars = list(cand.keys())
        weights = list(cand.values())
        ch = rng.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            if buf:
                out_tokens.append(''.join(buf))
                buf = []
            ctx = '\x01' * (order - 1)
            if len(out_tokens) >= target_token_count:
                break
            continue
        if ch == ' ':
            if buf:
                out_tokens.append(''.join(buf))
                buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
            continue
        buf.append(ch)
        ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    if buf and len(out_tokens) < target_token_count:
        out_tokens.append(''.join(buf))
    return out_tokens[:target_token_count]


def sample_corpus(counts, order: int, target_structure_lines: list[list[str]], rng: random.Random) -> list[list[str]]:
    """Sample synthetic corpus matching target_structure_lines' line/token-count structure."""
    return [sample_line(counts, order, len(line), rng) for line in target_structure_lines]


# ===== Measurement helpers =====

def line_initial_rate(corpus, target_token):
    total, initial = 0, 0
    for line in corpus:
        for i, tok in enumerate(line):
            if tok == target_token:
                total += 1
                if i == 0:
                    initial += 1
    return {'total': total, 'initial': initial, 'rate': initial / total if total else 0.0}


def line_final_rate(corpus, target_token):
    total, final = 0, 0
    for line in corpus:
        for i, tok in enumerate(line):
            if tok == target_token:
                total += 1
                if i == len(line) - 1:
                    final += 1
    return {'total': total, 'final': final, 'rate': final / total if total else 0.0}


def mean_normalized_position(corpus, target_token):
    positions = []
    for line in corpus:
        if len(line) < 2:
            continue
        for i, tok in enumerate(line):
            if tok == target_token:
                positions.append(i / (len(line) - 1))
    return {'n': len(positions),
            'mean_pos': float(np.mean(positions)) if positions else 0.0,
            'std_pos': float(np.std(positions)) if positions else 0.0,
            'rate': float(np.mean(positions)) if positions else 0.0}  # 'rate' alias for run_audit


def position_differential(corpus, token_a, token_b):
    """Mean position of token_b minus mean position of token_a (corpus-level aggregate)."""
    a_pos = mean_normalized_position(corpus, token_a)['mean_pos']
    b_pos = mean_normalized_position(corpus, token_b)['mean_pos']
    return {'a_mean_pos': a_pos, 'b_mean_pos': b_pos, 'differential': b_pos - a_pos,
            'rate': b_pos - a_pos}


def bigram_rate(corpus, current, target_next):
    """P(next in target_next set | current == current) within-line."""
    if isinstance(target_next, str):
        target_next = {target_next}
    else:
        target_next = set(target_next)
    total, match = 0, 0
    for line in corpus:
        for i in range(len(line) - 1):
            if line[i] == current:
                total += 1
                if line[i+1] in target_next:
                    match += 1
    return {'total': total, 'match': match, 'rate': match / total if total else 0.0}


def prefix_bigram_rate(corpus, current_prefix, target_prefixes):
    target_set = list(target_prefixes)
    total, match = 0, 0
    for line in corpus:
        for i in range(len(line) - 1):
            if line[i].startswith(current_prefix):
                total += 1
                if any(line[i+1].startswith(p) for p in target_set):
                    match += 1
    return {'total': total, 'match': match, 'rate': match / total if total else 0.0}


# ===== Run-audit =====

def run_audit(
    holdout_lines: list[list[str]],
    train_counts,
    order: int,
    n_synth: int,
    measurement_fn: Callable[[list[list[str]]], dict],
    seed: int = 42,
) -> dict:
    """Run measurement on real held-out + N synth corpora (synth structure matches holdout)."""
    rng = random.Random(seed)
    real_result = measurement_fn(holdout_lines)
    synth_results = []
    for _ in range(n_synth):
        synth_corpus = sample_corpus(train_counts, order, holdout_lines, rng)
        synth_results.append(measurement_fn(synth_corpus))
    real_val = real_result.get('rate', real_result.get('mean_pos', 0.0))
    synth_vals = [r.get('rate', r.get('mean_pos', 0.0)) for r in synth_results]
    synth_arr = np.array(synth_vals)
    z_diff = ((real_val - synth_arr.mean()) / synth_arr.std()) if synth_arr.std() > 0 else float('inf')
    p_emp = float((synth_arr >= real_val).mean())
    return {
        'real_value': real_val,
        'synth_mean': float(synth_arr.mean()),
        'synth_std': float(synth_arr.std()),
        'synth_min': float(synth_arr.min()),
        'synth_max': float(synth_arr.max()),
        'residual': real_val - float(synth_arr.mean()),
        'z_diff': float(z_diff) if z_diff != float('inf') else 999.0,
        'p_emp_above': p_emp,
        'p_emp_below': 1 - p_emp,
        'real_full': real_result,
        'n_synth': n_synth,
    }


def classify_disposition(summary: dict, original_effect_magnitude: float, claim_type: str,
                          near_zero_claim: bool = False) -> str:
    """Apply pre-registered classification (Option A: p_emp-only, metric-agnostic).

    Revised 2026-05-28 after second calibration cycle: PHASE_729 used enrichment-over-
    shuffle-null metric; my framework uses raw-rate metric; the magnitudes don't translate.
    Switched to p_emp-only verdicts. Effect-magnitude ratio kept as descriptive info in
    summary (note appended to verdict) for mechanism-strength assessment.

    Verdicts:
      p_emp < 0.01                                   -> SURVIVES STRONG (clearly above Markov)
      p_emp < 0.05                                   -> SURVIVES Tier 2 (above Markov)
      p_emp >= 0.05                                  -> DEMOTE Tier 2 -> Tier 3 (Markov-trivial)
      Sign flip AND p_emp < 0.05                     -> SURVIVES STRONG sign-flip
      Near-zero AND real<0.01 AND synth>0.01 AND p<0.05 -> SURVIVES STRONG prohibition
      Near-zero AND real<0.01 AND synth<0.01         -> DEMOTE (zero reproducible by Markov)

    For mechanism-class claims with small effect ratio, the verdict string appends a
    mechanism-strength flag for disposition note; the verdict itself is p_emp-only.
    """
    real = summary['real_value']
    synth = summary['synth_mean']
    p_above = summary['p_emp_above']
    p_below = summary['p_emp_below']
    p_emp = min(p_above, p_below)
    residual = abs(summary['residual'])
    sign_flip = (real * synth < 0) and (abs(real) > 0.01)
    ratio = residual / abs(original_effect_magnitude) if original_effect_magnitude else 0.0

    # Near-zero rail
    if near_zero_claim:
        if real < 0.01 and synth > 0.01 and p_emp < 0.05:
            return f'SURVIVES_STRONG_near_zero_prohibition_p{p_emp:.4f}_synth{synth:.4f}'
        if real < 0.01 and synth < 0.01:
            return f'DEMOTE_Tier2_to_Tier3_zero_reproducible_by_markov_p{p_emp:.4f}'

    if sign_flip and p_emp < 0.05:
        return f'SURVIVES_STRONG_sign_flip_p{p_emp:.4f}'

    # Mechanism-strength flag (descriptive, doesn't change verdict)
    strength_flag = ''
    if claim_type == 'mechanism' and ratio < 0.30 and ratio > 0:
        strength_flag = f'_mechanism_weak_ratio{ratio:.2f}'

    if p_emp < 0.01:
        return f'SURVIVES_STRONG_p{p_emp:.4f}{strength_flag}'
    if p_emp < 0.05:
        return f'SURVIVES_Tier2_above_markov_p{p_emp:.4f}{strength_flag}'
    return f'DEMOTE_Tier2_to_Tier3_markov_trivial_p{p_emp:.4f}_residual{residual:.4f}'


if __name__ == '__main__':
    print('Audit framework loaded.')
    lines, line_folios = load_real_currier_b_lines()
    print(f'Total: {len(lines)} lines from {len(set(line_folios))} folios, {sum(len(l) for l in lines)} tokens')
    train, hold, train_f, hold_f = holdout_split(lines, line_folios)
    print(f'Train: {len(train)} lines from {len(train_f)} folios ({sum(len(l) for l in train)} tokens)')
    print(f'Held-out: {len(hold)} lines from {len(hold_f)} folios ({sum(len(l) for l in hold)} tokens)')
    print(f'Held-out folios: {sorted(hold_f)}')
