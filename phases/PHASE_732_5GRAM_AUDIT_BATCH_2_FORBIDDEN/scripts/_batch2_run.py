"""Phase 732 Batch 2 — 5-gram null mechanism characterization of C109's 17 forbidden transitions.

PRE-REGISTERED (locked, expert-audited 2026-05-28, see INDEX.md):

REFRAMED PER EXPERTS:
- C109 is Tier 0 STRUCTURAL EXISTENCE claim ("17 forbidden transitions exist with 0% real rate").
  That's a fact. This audit tests MECHANISM: are these prohibitions above the 5-gram floor,
  or reproducible from local character statistics?
- Verdict labels reflect this: ABOVE_MARKOV_SUPPRESSION (not "designed prohibition").

VERDICTS (locked, denominator-invariant expected-count thresholds):
- ABOVE_MARKOV_SUPPRESSION_STRONG: real==0, expected synth bigrams >= 3.0 AND p_emp < 0.05
- ABOVE_MARKOV_SUPPRESSION_WEAK: real==0, expected synth bigrams 0.3-3.0 AND p_emp < 0.05
- MARKOV_TRIVIAL: real==0, expected synth bigrams < 0.3 (or p >= 0.05)
- PHANTOM_CONSTRUCTION: src_count == 0 OR tgt_count == 0 (4 pairs)

N_SYNTH STRATIFIED:
- both src and tgt >= 200: N=500
- either src or tgt 30-200: N=1000
- either src or tgt < 30: N=2000

SECONDARY: C627 prediction — >=7/13 testable pairs ABOVE_MARKOV_SUPPRESSION matches
the circuit-topology mechanism (C627 says 9/12 explained by circuit topology).

NEGATIVE CONTROL: 17 random non-forbidden frequency-matched bigrams, audited the same way.
If most negative-control bigrams show synth ~ real (Markov reproduces what it should),
methodology is calibrated; if synth diverges from real systematically, methodology issue.
"""
from __future__ import annotations
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'PHASE_731_5GRAM_AUDIT_BATCH_1' / 'scripts'))
from _audit_framework import (
    load_real_currier_b_lines, train_5gram, bigram_rate, run_audit,
)

FORBIDDEN = [
    (1, 'PHASE_ORDERING', 'shey', 'aiin'),
    (2, 'PHASE_ORDERING', 'shey', 'al'),
    (3, 'PHASE_ORDERING', 'shey', 'c'),
    (4, 'PHASE_ORDERING', 'dy', 'aiin'),
    (5, 'PHASE_ORDERING', 'dy', 'chey'),
    (6, 'PHASE_ORDERING', 'chey', 'chedy'),
    (7, 'PHASE_ORDERING', 'chey', 'shedy'),
    (8, 'COMPOSITION_JUMP', 'chedy', 'ee'),
    (9, 'COMPOSITION_JUMP', 'c', 'ee'),
    (10, 'COMPOSITION_JUMP', 'shedy', 'aiin'),
    (11, 'COMPOSITION_JUMP', 'shedy', 'o'),
    (12, 'CONTAINMENT_TIMING', 'chol', 'r'),
    (13, 'CONTAINMENT_TIMING', 'l', 'chol'),
    (14, 'CONTAINMENT_TIMING', 'or', 'dal'),
    (15, 'CONTAINMENT_TIMING', 'he', 'or'),
    (16, 'RATE_MISMATCH', 'ar', 'dal'),
    (17, 'ENERGY_OVERSHOOT', 'he', 't'),
]
ORDER = 5


def n_synth_for_pair(src_n, tgt_n):
    if src_n == 0 or tgt_n == 0:
        return 0  # phantom; skip audit
    if min(src_n, tgt_n) >= 200:
        return 500
    if min(src_n, tgt_n) >= 30:
        return 1000
    return 2000


def classify(real, synth_mean, src_n, p_emp, phantom):
    """Apply expected-count-based classification."""
    if phantom:
        return f'PHANTOM_CONSTRUCTION_src_or_tgt_zero', 'phantom'
    expected_bigrams = synth_mean * src_n
    if real == 0:
        if expected_bigrams >= 3.0 and p_emp < 0.05:
            return f'ABOVE_MARKOV_SUPPRESSION_STRONG_exp{expected_bigrams:.2f}_p{p_emp:.3f}', 'survive_strong'
        if expected_bigrams >= 0.3 and p_emp < 0.05:
            return f'ABOVE_MARKOV_SUPPRESSION_WEAK_exp{expected_bigrams:.2f}_p{p_emp:.3f}', 'survive_weak'
        return f'MARKOV_TRIVIAL_exp{expected_bigrams:.4f}_p{p_emp:.3f}', 'demote'
    return f'UNEXPECTED_real_nonzero_real{real:.4f}_synth{synth_mean:.4f}', 'unexpected'


print('=' * 75)
print('Phase 732 Batch 2 -- 5-gram null mechanism characterization of C109')
print('=' * 75)

print('\nLoading Currier B...')
lines, _ = load_real_currier_b_lines()
print(f'  {len(lines)} lines, {sum(len(l) for l in lines)} tokens')

tc = Counter()
for line in lines:
    for w in line:
        tc[w] += 1

print(f'\nTraining {ORDER}-gram on full Currier B...')
counts = train_5gram(lines, order=ORDER)
print(f'  {len(counts)} contexts learned.')

# =============== AUDIT MAIN: 17 FORBIDDEN PAIRS ===============
print('\n' + '=' * 75)
print('=== AUDIT: 17 forbidden transitions ===')
print('=' * 75)
print(f'{"#":>3} {"src":>10} {"->":>3} {"tgt":>10} {"src_n":>6} {"tgt_n":>6} {"N":>5} '
      f'{"real":>6} {"synth_m":>9} {"exp":>6} {"p":>6}')
print('-' * 90)

dispositions = {}
verdict_counts = Counter()

for n, cls, src, tgt in FORBIDDEN:
    src_n = tc[src]; tgt_n = tc[tgt]
    phantom = (src_n == 0 or tgt_n == 0)
    N = n_synth_for_pair(src_n, tgt_n)
    if N == 0:
        # phantom
        verdict, bucket = classify(0, 0, src_n, 1.0, phantom=True)
        print(f'{n:>3} {src:>10} {"->":>3} {tgt:>10} {src_n:>6} {tgt_n:>6} {"---":>5} '
              f'{"---":>6} {"---":>9} {"---":>6} {"---":>6}  PHANTOM')
        dispositions[f'pair_{n:02d}_{src}_to_{tgt}'] = {
            'pair_number': n, 'class': cls, 'src': src, 'tgt': tgt,
            'src_count': src_n, 'tgt_count': tgt_n, 'phantom': True,
            'verdict': verdict, 'bucket': bucket,
        }
        verdict_counts[bucket] += 1
        continue
    summary = run_audit(lines, counts, ORDER, N,
                        lambda c: bigram_rate(c, src, tgt))
    p_emp = min(summary['p_emp_above'], summary['p_emp_below'])
    expected_bigrams = summary['synth_mean'] * src_n
    verdict, bucket = classify(summary['real_value'], summary['synth_mean'], src_n, p_emp, phantom=False)
    verdict_counts[bucket] += 1
    print(f'{n:>3} {src:>10} {"->":>3} {tgt:>10} {src_n:>6} {tgt_n:>6} {N:>5} '
          f'{summary["real_value"]:>6.3f} {summary["synth_mean"]:>9.5f} {expected_bigrams:>6.2f} {p_emp:>6.3f}  {bucket}')
    dispositions[f'pair_{n:02d}_{src}_to_{tgt}'] = {
        'pair_number': n, 'class': cls, 'src': src, 'tgt': tgt,
        'src_count': src_n, 'tgt_count': tgt_n, 'phantom': False,
        'N_synth': N,
        'real_bigram_rate': summary['real_value'],
        'synth_mean': summary['synth_mean'], 'synth_std': summary['synth_std'],
        'synth_min': summary['synth_min'], 'synth_max': summary['synth_max'],
        'expected_bigrams_per_synth': expected_bigrams,
        'p_emp_above': summary['p_emp_above'], 'p_emp_below': summary['p_emp_below'],
        'verdict': verdict, 'bucket': bucket,
    }

# =============== NEGATIVE CONTROL ===============
print('\n' + '=' * 75)
print('=== NEGATIVE CONTROL: 17 random non-forbidden bigrams (frequency-matched) ===')
print('=' * 75)

# Build frequency profile of the 17 forbidden pairs
forbidden_src_freqs = [tc[src] for _, _, src, _ in FORBIDDEN if tc[src] > 0]
forbidden_tgt_freqs = [tc[tgt] for _, _, _, tgt in FORBIDDEN if tc[tgt] > 0]
mean_src_freq = np.mean(forbidden_src_freqs)
mean_tgt_freq = np.mean(forbidden_tgt_freqs)
print(f'Forbidden-pair frequency profile: src mean={mean_src_freq:.0f}, tgt mean={mean_tgt_freq:.0f}')

# Pick 17 random non-forbidden bigrams with both tokens in similar frequency range
all_freq_tokens = [t for t, n in tc.items() if 30 <= n <= 600]
forbidden_set = {(src, tgt) for _, _, src, tgt in FORBIDDEN}
rng = random.Random(2026)
neg_controls = []
attempts = 0
while len(neg_controls) < 17 and attempts < 1000:
    attempts += 1
    src = rng.choice(all_freq_tokens)
    tgt = rng.choice(all_freq_tokens)
    if src == tgt: continue
    if (src, tgt) in forbidden_set: continue
    # Skip if already in negative controls
    if any(s == src and t == tgt for _, s, t in neg_controls): continue
    # Skip if real bigram is 0 (we want CONTROLS that exist; we expect synth to also produce them)
    real_count = sum(1 for line in lines for i in range(len(line)-1) if line[i]==src and line[i+1]==tgt)
    if real_count == 0: continue
    neg_controls.append((len(neg_controls)+1, src, tgt))

print(f'Selected {len(neg_controls)} non-forbidden bigrams with real_count > 0\n')
print(f'{"#":>3} {"src":>10} {"->":>3} {"tgt":>10} {"src_n":>6} {"tgt_n":>6} {"real":>7} {"synth":>9} {"ratio":>6}')
print('-' * 75)

neg_results = []
for n, src, tgt in neg_controls:
    src_n = tc[src]; tgt_n = tc[tgt]
    N = n_synth_for_pair(src_n, tgt_n)
    summary = run_audit(lines, counts, ORDER, N,
                        lambda c: bigram_rate(c, src, tgt))
    ratio = summary['real_value'] / summary['synth_mean'] if summary['synth_mean'] > 0 else float('inf')
    print(f'{n:>3} {src:>10} {"->":>3} {tgt:>10} {src_n:>6} {tgt_n:>6} '
          f'{summary["real_value"]:>7.4f} {summary["synth_mean"]:>9.5f} {ratio:>6.2f}')
    neg_results.append({
        'index': n, 'src': src, 'tgt': tgt, 'src_count': src_n, 'tgt_count': tgt_n,
        'real_rate': summary['real_value'], 'synth_mean': summary['synth_mean'],
        'real_to_synth_ratio': ratio,
        'p_emp_above': summary['p_emp_above'], 'p_emp_below': summary['p_emp_below'],
    })

# Negative control summary
ratios = [r['real_to_synth_ratio'] for r in neg_results if r['synth_mean'] > 0 and r['real_to_synth_ratio'] != float('inf')]
if ratios:
    print(f'\nNegative-control real/synth ratios: median={np.median(ratios):.2f}, mean={np.mean(ratios):.2f}')
    print(f'  (Calibration check: 5-gram should produce non-forbidden bigrams at rates comparable to real.')
    print(f'   Median ratio near 1.0 = good calibration; ratio >> 1 = synth under-produces; ratio << 1 = synth over-produces.)')


# =============== AGGREGATE & VERDICTS ===============
print('\n' + '=' * 75)
print('=== AGGREGATE ===')
print('=' * 75)
for b, n in verdict_counts.most_common():
    print(f'  {b}: {n}')

n_strong = verdict_counts['survive_strong']
n_weak = verdict_counts['survive_weak']
n_demote = verdict_counts['demote']
n_phantom = verdict_counts['phantom']
n_testable = 17 - n_phantom

print(f'\n  Testable pairs (non-phantom): {n_testable}')
print(f'  ABOVE_MARKOV_SUPPRESSION_STRONG: {n_strong}')
print(f'  ABOVE_MARKOV_SUPPRESSION_WEAK: {n_weak}')
print(f'  MARKOV_TRIVIAL: {n_demote}')
print(f'  PHANTOM_CONSTRUCTION: {n_phantom}')

n_survive = n_strong + n_weak
print(f'\n  Total surviving: {n_survive}/{n_testable} testable')

print(f'\n  Pre-registered C627 baseline (>=7/13 testable ABOVE_MARKOV_SUPPRESSION):')
if n_survive >= 7 and n_testable >= 13:
    print(f'    MET: {n_survive} >= 7 of {n_testable}. C109 mechanism is above-5-gram structure for majority of testable pairs.')
elif n_survive >= n_testable * 0.4:
    print(f'    PARTIAL: {n_survive}/{n_testable} ({n_survive/n_testable*100:.0f}%). Mixed: some above-Markov, some Markov-trivial.')
else:
    print(f'    NOT MET: {n_survive}/{n_testable} ({n_survive/n_testable*100:.0f}%). Majority of forbidden pairs are Markov-trivial.')

# Write outputs
out_dispositions = Path(__file__).parent.parent / 'results' / 'batch2_dispositions.json'
out_dispositions.parent.mkdir(parents=True, exist_ok=True)
out_dispositions.write_text(json.dumps(dispositions, indent=2))
print(f'\nDispositions written to {out_dispositions}')

out_neg = Path(__file__).parent.parent / 'results' / 'batch2_negative_control.json'
out_neg.write_text(json.dumps(neg_results, indent=2))
print(f'Negative control written to {out_neg}')
