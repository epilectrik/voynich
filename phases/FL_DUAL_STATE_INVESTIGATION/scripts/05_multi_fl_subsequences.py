"""
05_multi_fl_subsequences.py

Analyze FL subsequences in lines with 2+ FL tokens.

Q: In lines with 2+ FL tokens, do FL subsequences follow specific patterns?
- Extract all FL subsequences from multi-FL lines
- Classify each pair: forward, backward, same-stage
- Identify common FL bigrams and trigrams
- Test if specific FL bigrams predict section or line position
- Compare within-line forward bias to C786's 5:1 global ratio
"""
import sys
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}

tx = Transcript()
morph = Morphology()

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL per-line sequences
fl_sequences = {}  # line_key -> [(middle, idx, stage, expected_pos)]
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    fl_in_line = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            stage, expected = FL_STAGE_MAP[m.middle]
            fl_in_line.append((m.middle, idx, stage, expected, t.section))

    if len(fl_in_line) >= 2:
        fl_sequences[line_key] = fl_in_line

print(f"Lines with 2+ FL tokens: {len(fl_sequences)}")

# ============================================================
# Pairwise transition analysis
# ============================================================
forward = 0
backward = 0
same_stage = 0
bigram_counts = Counter()
transition_types = Counter()

for line_key, fl_seq in fl_sequences.items():
    for i in range(len(fl_seq) - 1):
        mid_a, _, stage_a, exp_a, _ = fl_seq[i]
        mid_b, _, stage_b, exp_b, _ = fl_seq[i + 1]

        bigram = f"{mid_a}->{mid_b}"
        bigram_counts[bigram] += 1

        ord_a = STAGE_ORDER[stage_a]
        ord_b = STAGE_ORDER[stage_b]

        if ord_b > ord_a:
            forward += 1
            transition_types['forward'] += 1
        elif ord_b < ord_a:
            backward += 1
            transition_types['backward'] += 1
        else:
            same_stage += 1
            transition_types['same_stage'] += 1

total_transitions = forward + backward + same_stage
fwd_rate = forward / total_transitions if total_transitions > 0 else 0
bwd_rate = backward / total_transitions if total_transitions > 0 else 0
same_rate = same_stage / total_transitions if total_transitions > 0 else 0
fwd_bwd_ratio = forward / backward if backward > 0 else float('inf')

print(f"\nTransition counts (adjacent FL pairs):")
print(f"  Forward:    {forward:>5} ({fwd_rate:.1%})")
print(f"  Same-stage: {same_stage:>5} ({same_rate:.1%})")
print(f"  Backward:   {backward:>5} ({bwd_rate:.1%})")
print(f"  Forward:Backward ratio = {fwd_bwd_ratio:.1f}:1")
print(f"  (C786 global = 5:1)")

# ============================================================
# Top bigrams
# ============================================================
print(f"\nTop 20 FL bigrams:")
for bigram, count in bigram_counts.most_common(20):
    parts = bigram.split('->')
    stage_a = FL_STAGE_MAP[parts[0]][0]
    stage_b = FL_STAGE_MAP[parts[1]][0]
    direction = "FWD" if STAGE_ORDER[stage_b] > STAGE_ORDER[stage_a] else \
                "BWD" if STAGE_ORDER[stage_b] < STAGE_ORDER[stage_a] else "SAME"
    print(f"  {bigram:>12}: {count:>4} [{direction}] ({stage_a}->{stage_b})")

# ============================================================
# Trigrams (lines with 3+ FL)
# ============================================================
trigram_counts = Counter()
for line_key, fl_seq in fl_sequences.items():
    if len(fl_seq) >= 3:
        for i in range(len(fl_seq) - 2):
            tri = f"{fl_seq[i][0]}->{fl_seq[i+1][0]}->{fl_seq[i+2][0]}"
            trigram_counts[tri] += 1

print(f"\nTop 15 FL trigrams:")
for tri, count in trigram_counts.most_common(15):
    print(f"  {tri:>20}: {count:>3}")

# ============================================================
# Sequence length distribution
# ============================================================
seq_lengths = Counter(len(v) for v in fl_sequences.values())
print(f"\nFL sequence length distribution:")
for length in sorted(seq_lengths.keys()):
    print(f"  {length} FL tokens: {seq_lengths[length]} lines")

# ============================================================
# Section-specific bigram patterns
# ============================================================
section_bigrams = defaultdict(Counter)
for line_key, fl_seq in fl_sequences.items():
    section = fl_seq[0][4]
    for i in range(len(fl_seq) - 1):
        bigram = f"{fl_seq[i][0]}->{fl_seq[i+1][0]}"
        section_bigrams[section][bigram] += 1

print(f"\nTop bigram by section:")
for section in sorted(section_bigrams.keys()):
    top = section_bigrams[section].most_common(3)
    top_str = ", ".join(f"{b}({c})" for b, c in top)
    print(f"  {section}: {top_str}")

# ============================================================
# Forward bias: within-line vs global
# ============================================================
# All pairwise (not just adjacent) — matches C786 methodology
all_pair_fwd = 0
all_pair_bwd = 0
all_pair_same = 0

for line_key, fl_seq in fl_sequences.items():
    for i in range(len(fl_seq)):
        for j in range(i + 1, len(fl_seq)):
            ord_a = STAGE_ORDER[fl_seq[i][2]]
            ord_b = STAGE_ORDER[fl_seq[j][2]]
            if ord_b > ord_a:
                all_pair_fwd += 1
            elif ord_b < ord_a:
                all_pair_bwd += 1
            else:
                all_pair_same += 1

all_pair_total = all_pair_fwd + all_pair_bwd + all_pair_same
all_pair_ratio = all_pair_fwd / all_pair_bwd if all_pair_bwd > 0 else float('inf')

print(f"\nAll-pairs forward bias (within multi-FL lines):")
print(f"  Forward: {all_pair_fwd} ({all_pair_fwd/all_pair_total:.1%})")
print(f"  Same:    {all_pair_same} ({all_pair_same/all_pair_total:.1%})")
print(f"  Backward:{all_pair_bwd} ({all_pair_bwd/all_pair_total:.1%})")
print(f"  Ratio:   {all_pair_ratio:.1f}:1")

# ============================================================
# Verdict
# ============================================================
if fwd_bwd_ratio > 3.0:
    bias_verdict = "STRONG_FORWARD"
elif fwd_bwd_ratio > 1.5:
    bias_verdict = "MODERATE_FORWARD"
else:
    bias_verdict = "WEAK_OR_NO_BIAS"

if len(trigram_counts) > 0 and trigram_counts.most_common(1)[0][1] > 10:
    pattern_verdict = "RECURRENT_PATTERNS"
else:
    pattern_verdict = "NO_DOMINANT_PATTERNS"

verdict = f"{bias_verdict}_{pattern_verdict}"
explanation = (f"Within-line forward:backward ratio = {fwd_bwd_ratio:.1f}:1 "
               f"(C786 global = 5:1). "
               f"Top bigram: {bigram_counts.most_common(1)[0][0]} "
               f"({bigram_counts.most_common(1)[0][1]}x)")

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'n_multi_fl_lines': len(fl_sequences),
    'adjacent_transitions': {
        'forward': forward,
        'backward': backward,
        'same_stage': same_stage,
        'total': total_transitions,
        'fwd_rate': round(fwd_rate, 4),
        'bwd_rate': round(bwd_rate, 4),
        'same_rate': round(same_rate, 4),
        'fwd_bwd_ratio': round(fwd_bwd_ratio, 2),
    },
    'all_pairs': {
        'forward': all_pair_fwd,
        'backward': all_pair_bwd,
        'same': all_pair_same,
        'ratio': round(all_pair_ratio, 2),
    },
    'top_bigrams': bigram_counts.most_common(30),
    'top_trigrams': trigram_counts.most_common(20),
    'sequence_lengths': dict(seq_lengths),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "05_multi_fl_subsequences.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
