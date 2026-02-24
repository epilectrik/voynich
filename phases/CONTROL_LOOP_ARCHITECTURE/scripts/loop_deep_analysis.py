#!/usr/bin/env python3
"""
Control Loop Deep Analysis — 5 tests to determine the ACTUAL loop structure.

Test 1: What predicts STOP vs CONTINUE at line-final?
Test 2: Does STOP rate increase with paragraph position?
Test 3: Within-line kernel ordering (e→h→k safety interlock, C873)
Test 4: Token bigram motifs (stereotyped sequences)
Test 5: Mode sequence entropy (structured or random?)

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/loop_deep_analysis.json
"""

import sys
import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

TERMINAL_SUFFIXES = {'dy', 'edy', 'eey', 'ey', 'hy', 'ry', 'ly', 'am', 'om'}
CHECKPOINT_SUFFIXES = {'ain', 'aiin', 'iin', 'oiin'}

def classify_final(tok):
    """Classify a token as STOP, CONTINUE, or NEUTRAL."""
    m = tok.morph
    has_m = m.middle and 'm' in m.middle
    has_i = m.middle and 'i' in m.middle
    cat = None
    if m.suffix in TERMINAL_SUFFIXES:
        cat = 'TERMINAL'
    elif m.suffix in CHECKPOINT_SUFFIXES:
        cat = 'CHECKPOINT'

    if cat == 'TERMINAL' or has_m:
        return 'STOP'
    elif cat == 'CHECKPOINT' or (has_i and not has_m):
        return 'CONTINUE'
    return 'NEUTRAL'

# ============================================================
# DECODE ALL FOLIOS
# ============================================================
print("Decoding all B folios...")
b_folios = sorted(set(t.folio for t in tx.currier_b()))

all_paragraphs = []  # (folio, BParagraphAnalysis)
for folio in b_folios:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
        for p in paras:
            all_paragraphs.append((folio, p))
    except:
        continue

print(f"  {len(all_paragraphs)} paragraphs from {len(b_folios)} folios")

# ============================================================
# TEST 1: LINE-FINAL DECISION PREDICTORS
# ============================================================
print("\n" + "="*70)
print("TEST 1: LINE-FINAL DECISION PREDICTORS")
print("="*70)

line_records = []
for folio, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    n_body = len(body_lines)
    if n_body < 3:
        continue

    for li, line_a in enumerate(body_lines):
        if line_a.token_count < 3:
            continue

        # Position in paragraph (0=first body, 1=last body)
        para_pos = li / max(n_body - 1, 1)

        # Kernel balance
        kernels = Counter()
        for tok in line_a.tokens:
            for k in tok.kernels:
                kernels[k] += 1
        k_total = sum(kernels.values()) or 1
        k_pct = kernels.get('k', 0) / k_total
        e_pct = kernels.get('e', 0) / k_total
        h_pct = kernels.get('h', 0) / k_total

        # FL last stage
        non_none_fl = [f for f in line_a.fl_stages if f]
        fl_last = non_none_fl[-1] if non_none_fl else 'NONE'

        # Mode
        mode = line_a.suffix_mode or '?'

        # Final token decision
        final_tok = line_a.tokens[-1]
        decision = classify_final(final_tok)

        line_records.append({
            'para_pos': para_pos,
            'k_pct': k_pct,
            'e_pct': e_pct,
            'h_pct': h_pct,
            'fl_last': fl_last,
            'mode': mode,
            'token_count': line_a.token_count,
            'decision': decision,
        })

print(f"  Lines analyzed: {len(line_records)}")

# Feature correlation with STOP decision
stop_lines = [r for r in line_records if r['decision'] == 'STOP']
cont_lines = [r for r in line_records if r['decision'] == 'CONTINUE']
neut_lines = [r for r in line_records if r['decision'] == 'NEUTRAL']

print(f"  STOP: {len(stop_lines)} ({len(stop_lines)/len(line_records)*100:.1f}%)")
print(f"  CONTINUE: {len(cont_lines)} ({len(cont_lines)/len(line_records)*100:.1f}%)")
print(f"  NEUTRAL: {len(neut_lines)} ({len(neut_lines)/len(line_records)*100:.1f}%)")

# Compare features across decisions
print(f"\n  {'Feature':20s} {'STOP':>8s} {'CONTINUE':>10s} {'NEUTRAL':>10s}")
print(f"  {'-'*50}")
for feat in ['para_pos', 'k_pct', 'e_pct', 'h_pct', 'token_count']:
    stop_mean = sum(r[feat] for r in stop_lines) / len(stop_lines) if stop_lines else 0
    cont_mean = sum(r[feat] for r in cont_lines) / len(cont_lines) if cont_lines else 0
    neut_mean = sum(r[feat] for r in neut_lines) / len(neut_lines) if neut_lines else 0
    print(f"  {feat:20s} {stop_mean:8.3f} {cont_mean:10.3f} {neut_mean:10.3f}")

# FL distribution per decision
print(f"\n  FL distribution at line-final:")
for dec_label, dec_lines in [('STOP', stop_lines), ('CONTINUE', cont_lines), ('NEUTRAL', neut_lines)]:
    fl_counts = Counter(r['fl_last'] for r in dec_lines)
    total = len(dec_lines) or 1
    fl_str = ' '.join(f"{fl}:{fl_counts[fl]/total*100:.0f}%" for fl in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL'] if fl_counts[fl] > 0)
    print(f"    {dec_label:10s}: {fl_str}")

# Mode distribution per decision
print(f"\n  Mode distribution:")
for dec_label, dec_lines in [('STOP', stop_lines), ('CONTINUE', cont_lines), ('NEUTRAL', neut_lines)]:
    mode_counts = Counter(r['mode'] for r in dec_lines)
    total = len(dec_lines) or 1
    a_pct = mode_counts.get('A', 0) / total * 100
    b_pct = mode_counts.get('B', 0) / total * 100
    print(f"    {dec_label:10s}: A={a_pct:.1f}% B={b_pct:.1f}%")

# ============================================================
# TEST 2: STOP RATE vs PARAGRAPH POSITION
# ============================================================
print("\n" + "="*70)
print("TEST 2: STOP RATE vs PARAGRAPH POSITION")
print("="*70)

# Bin by quintile
quintile_data = defaultdict(lambda: {'stop': 0, 'continue': 0, 'neutral': 0, 'total': 0})
for r in line_records:
    q = min(int(r['para_pos'] * 5), 4)  # 0-4 quintiles
    quintile_data[q][r['decision'].lower()] += 1
    quintile_data[q]['total'] += 1

print(f"\n  {'Quintile':>10s} {'Lines':>6s} {'STOP%':>8s} {'CONT%':>8s} {'NEUT%':>8s}")
print(f"  {'-'*45}")
stop_rates = []
for q in range(5):
    d = quintile_data[q]
    n = d['total'] or 1
    stop_r = d['stop'] / n * 100
    cont_r = d['continue'] / n * 100
    neut_r = d['neutral'] / n * 100
    stop_rates.append(stop_r)
    label = f"Q{q} ({q*20}-{(q+1)*20}%)"
    print(f"  {label:>10s} {d['total']:6d} {stop_r:7.1f}% {cont_r:7.1f}% {neut_r:7.1f}%")

# Trend: is stop rate increasing?
if len(stop_rates) >= 3:
    # Simple linear regression
    n = len(stop_rates)
    x_mean = (n - 1) / 2
    y_mean = sum(stop_rates) / n
    num = sum((i - x_mean) * (stop_rates[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den > 0 else 0
    print(f"\n  STOP rate trend: slope = {slope:+.2f} percentage points per quintile")
    if slope > 2:
        print(f"  -> INCREASING: loop converges toward termination")
    elif slope < -2:
        print(f"  -> DECREASING: loop converges toward continuation")
    else:
        print(f"  -> FLAT: loop is steady-state (no convergence)")

# ============================================================
# TEST 3: WITHIN-LINE KERNEL ORDERING
# ============================================================
print("\n" + "="*70)
print("TEST 3: WITHIN-LINE KERNEL ORDERING (e->h->k safety interlock)")
print("="*70)

# For each line, find kernel atom positions
e_before_k = 0
k_before_e = 0
e_before_h = 0
h_before_e = 0
h_before_k = 0
k_before_h = 0
lines_with_ek = 0
lines_with_eh = 0
lines_with_hk = 0

for folio, para in all_paragraphs:
    for line_a in para.lines:
        if line_a.token_count < 4:
            continue

        # Find first position of each kernel in the line
        first_e = first_h = first_k = None
        for i, tok in enumerate(line_a.tokens):
            if 'e' in tok.kernels and first_e is None:
                first_e = i
            if 'h' in tok.kernels and first_h is None:
                first_h = i
            if 'k' in tok.kernels and first_k is None:
                first_k = i

        if first_e is not None and first_k is not None:
            lines_with_ek += 1
            if first_e < first_k:
                e_before_k += 1
            else:
                k_before_e += 1

        if first_e is not None and first_h is not None:
            lines_with_eh += 1
            if first_e < first_h:
                e_before_h += 1
            else:
                h_before_e += 1

        if first_h is not None and first_k is not None:
            lines_with_hk += 1
            if first_h < first_k:
                h_before_k += 1
            else:
                k_before_h += 1

print(f"\n  Kernel pair ordering (first occurrence in line):")
if lines_with_ek > 0:
    print(f"    e before k: {e_before_k}/{lines_with_ek} ({e_before_k/lines_with_ek*100:.1f}%)  {'CONFIRMED' if e_before_k/lines_with_ek > 0.55 else 'WEAK'}")
if lines_with_eh > 0:
    print(f"    e before h: {e_before_h}/{lines_with_eh} ({e_before_h/lines_with_eh*100:.1f}%)  {'CONFIRMED' if e_before_h/lines_with_eh > 0.55 else 'WEAK'}")
if lines_with_hk > 0:
    print(f"    h before k: {h_before_k}/{lines_with_hk} ({h_before_k/lines_with_hk*100:.1f}%)  {'CONFIRMED' if h_before_k/lines_with_hk > 0.55 else 'WEAK'}")

# Shuffle test: how often does random ordering produce e<h<k?
random.seed(42)
n_shuffles = 10000
shuffle_e_before_k = 0
for _ in range(n_shuffles):
    positions = list(range(10))
    random.shuffle(positions)
    if positions[0] < positions[1]:
        shuffle_e_before_k += 1
expected_rate = shuffle_e_before_k / n_shuffles
print(f"\n  Random baseline (any pair): {expected_rate*100:.1f}% (should be ~50%)")
if lines_with_ek > 0:
    observed = e_before_k / lines_with_ek
    effect = observed - 0.5
    print(f"  e-before-k effect size: {effect:+.3f} ({effect*100:+.1f} percentage points above chance)")

# ============================================================
# TEST 4: TOKEN BIGRAM MOTIFS
# ============================================================
print("\n" + "="*70)
print("TEST 4: TOKEN BIGRAM MOTIFS")
print("="*70)

# Build bigram counts (within lines)
bigrams_within = Counter()
word_counts = Counter()

for folio, para in all_paragraphs:
    for line_a in para.lines:
        for i, tok in enumerate(line_a.tokens):
            word_counts[tok.word] += 1
            if i > 0:
                prev_word = line_a.tokens[i-1].word
                bigrams_within[(prev_word, tok.word)] += 1

# Build bigrams across line boundaries
bigrams_across = Counter()
for folio, para in all_paragraphs:
    for li in range(1, len(para.lines)):
        prev_line = para.lines[li-1]
        curr_line = para.lines[li]
        if prev_line.tokens and curr_line.tokens:
            last_word = prev_line.tokens[-1].word
            first_word = curr_line.tokens[0].word
            bigrams_across[(last_word, first_word)] += 1

total_words = sum(word_counts.values())

# PMI for within-line bigrams
print(f"\n  Top within-line bigrams by PMI (min count 20):")
print(f"  {'Word1':>14s} -> {'Word2':>14s}  {'Count':>5s}  {'PMI':>6s}")
pmi_list = []
for (w1, w2), count in bigrams_within.items():
    if count < 20:
        continue
    p_w1 = word_counts[w1] / total_words
    p_w2 = word_counts[w2] / total_words
    p_bigram = count / sum(bigrams_within.values())
    if p_w1 > 0 and p_w2 > 0:
        pmi = math.log2(p_bigram / (p_w1 * p_w2))
        pmi_list.append((w1, w2, count, pmi))

pmi_list.sort(key=lambda x: x[3], reverse=True)
for w1, w2, count, pmi in pmi_list[:20]:
    print(f"  {w1:>14s} -> {w2:>14s}  {count:5d}  {pmi:6.2f}")

# Cross-line bigrams
print(f"\n  Top cross-line boundary bigrams (last word -> first word, min 5):")
for (w1, w2), count in bigrams_across.most_common(20):
    if count < 5:
        break
    print(f"  {w1:>14s} -> {w2:>14s}  {count:5d}")

# ============================================================
# TEST 5: MODE SEQUENCE ENTROPY
# ============================================================
print("\n" + "="*70)
print("TEST 5: MODE SEQUENCE ENTROPY")
print("="*70)

# Collect mode sequences from all paragraphs
mode_sequences = []
for folio, para in all_paragraphs:
    body_modes = [l.suffix_mode for l in para.lines if not l.is_header and l.suffix_mode]
    if len(body_modes) >= 4:
        mode_sequences.append(body_modes)

print(f"  Paragraphs with 4+ mode-classified body lines: {len(mode_sequences)}")

# Transition matrix
mode_trans = Counter()
for seq in mode_sequences:
    for i in range(1, len(seq)):
        mode_trans[(seq[i-1], seq[i])] += 1

total_trans = sum(mode_trans.values())
print(f"\n  Mode transition matrix:")
print(f"  {'FROM':>6s} -> {'A':>6s} {'B':>6s}")
for fr in ['A', 'B']:
    row_total = mode_trans[(fr, 'A')] + mode_trans[(fr, 'B')]
    if row_total == 0:
        continue
    a_pct = mode_trans[(fr, 'A')] / row_total * 100
    b_pct = mode_trans[(fr, 'B')] / row_total * 100
    print(f"  {fr:>6s} -> {a_pct:5.1f}% {b_pct:5.1f}%")

# Entropy of transitions
trans_entropy = 0
for fr in ['A', 'B']:
    row_total = mode_trans[(fr, 'A')] + mode_trans[(fr, 'B')]
    if row_total == 0:
        continue
    p_row = row_total / total_trans
    for to in ['A', 'B']:
        p = mode_trans[(fr, to)] / row_total
        if p > 0:
            trans_entropy -= p_row * p * math.log2(p)

max_entropy = 1.0  # binary choice
print(f"\n  Transition entropy: {trans_entropy:.4f} bits (max = {max_entropy:.4f})")
print(f"  Entropy ratio: {trans_entropy/max_entropy*100:.1f}% of maximum")
if trans_entropy / max_entropy > 0.95:
    print(f"  -> MODE TRANSITIONS ARE NEAR-RANDOM")
elif trans_entropy / max_entropy > 0.80:
    print(f"  -> MODE TRANSITIONS ARE WEAKLY STRUCTURED")
else:
    print(f"  -> MODE TRANSITIONS ARE STRONGLY STRUCTURED")

# Run-length analysis
print(f"\n  Run-length analysis:")
run_lengths = {'A': [], 'B': []}
for seq in mode_sequences:
    current = seq[0]
    length = 1
    for i in range(1, len(seq)):
        if seq[i] == current:
            length += 1
        else:
            run_lengths[current].append(length)
            current = seq[i]
            length = 1
    run_lengths[current].append(length)

for mode in ['A', 'B']:
    runs = run_lengths[mode]
    if runs:
        mean_run = sum(runs) / len(runs)
        max_run = max(runs)
        run_dist = Counter(runs)
        print(f"  Mode {mode}: mean run length = {mean_run:.2f}, max = {max_run}, n_runs = {len(runs)}")
        print(f"    Distribution: {dict(sorted(run_dist.items())[:8])}")

# Expected run length under independence
p_a = sum(1 for s in mode_sequences for m in s if m == 'A') / sum(len(s) for s in mode_sequences)
p_b = 1 - p_a
exp_run_a = 1 / (1 - p_a) if p_a < 1 else float('inf')
exp_run_b = 1 / (1 - p_b) if p_b < 1 else float('inf')
print(f"\n  P(A) = {p_a:.3f}, P(B) = {p_b:.3f}")
print(f"  Expected run length if random: A={exp_run_a:.2f}, B={exp_run_b:.2f}")
print(f"  Observed run length: A={sum(run_lengths['A'])/len(run_lengths['A']):.2f}, B={sum(run_lengths['B'])/len(run_lengths['B']):.2f}")

obs_a = sum(run_lengths['A']) / len(run_lengths['A'])
obs_b = sum(run_lengths['B']) / len(run_lengths['B'])
if abs(obs_a - exp_run_a) < 0.3 and abs(obs_b - exp_run_b) < 0.3:
    print(f"  -> Run lengths MATCH random expectation. Mode sequence is NOT structured.")
elif obs_a < exp_run_a * 0.8 and obs_b < exp_run_b * 0.8:
    print(f"  -> Runs SHORTER than random = excess alternation (real cycling)")
elif obs_a > exp_run_a * 1.2 and obs_b > exp_run_b * 1.2:
    print(f"  -> Runs LONGER than random = clustering (not cycling)")
else:
    print(f"  -> Mixed signal")

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "="*70)
print("SYNTHESIS")
print("="*70)

# Compile key numbers for synthesis
results = {
    'test1_decision_predictors': {
        'n_lines': len(line_records),
        'stop_pct': round(len(stop_lines)/len(line_records)*100, 1),
        'continue_pct': round(len(cont_lines)/len(line_records)*100, 1),
        'neutral_pct': round(len(neut_lines)/len(line_records)*100, 1),
        'para_pos_stop_mean': round(sum(r['para_pos'] for r in stop_lines)/len(stop_lines), 3) if stop_lines else 0,
        'para_pos_cont_mean': round(sum(r['para_pos'] for r in cont_lines)/len(cont_lines), 3) if cont_lines else 0,
        'para_pos_neut_mean': round(sum(r['para_pos'] for r in neut_lines)/len(neut_lines), 3) if neut_lines else 0,
    },
    'test2_stop_by_position': {
        'quintile_stop_rates': [round(r, 1) for r in stop_rates],
        'slope': round(slope, 2),
        'verdict': 'INCREASING' if slope > 2 else ('DECREASING' if slope < -2 else 'FLAT'),
    },
    'test3_kernel_ordering': {
        'e_before_k_pct': round(e_before_k/lines_with_ek*100, 1) if lines_with_ek > 0 else 0,
        'e_before_h_pct': round(e_before_h/lines_with_eh*100, 1) if lines_with_eh > 0 else 0,
        'h_before_k_pct': round(h_before_k/lines_with_hk*100, 1) if lines_with_hk > 0 else 0,
        'e_before_k_effect': round(e_before_k/lines_with_ek - 0.5, 3) if lines_with_ek > 0 else 0,
    },
    'test4_top_bigrams': [(w1, w2, count, round(pmi, 2)) for w1, w2, count, pmi in pmi_list[:15]],
    'test5_mode_entropy': {
        'transition_entropy': round(trans_entropy, 4),
        'max_entropy': max_entropy,
        'entropy_ratio': round(trans_entropy/max_entropy*100, 1),
        'p_a': round(p_a, 3),
        'p_b': round(p_b, 3),
        'mean_run_a': round(obs_a, 2),
        'mean_run_b': round(obs_b, 2),
        'expected_run_a': round(exp_run_a, 2),
        'expected_run_b': round(exp_run_b, 2),
    },
}

output_path = OUTPUT_DIR / 'loop_deep_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
