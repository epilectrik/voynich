#!/usr/bin/env python3
"""
Phase CURRIER_A_ATOMS / Script 3: Currier A Record Internal Structure at Atom Level

Analyzes the internal token sequence within Currier A records (lines),
focusing on HEAD, PREFIX, and TERM positional grammar.

Key questions:
  - What is the record length distribution?
  - Do HEAD atoms follow positional grammar within records?
  - What HEAD-to-HEAD transitions occur?
  - What are the most common record type patterns?
  - How does e_depth evolve within records?

Uses scripts/voynich.py canonical library.
"""

import sys
import os
import json
from collections import Counter, defaultdict
from pathlib import Path

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Run from repo root
os.chdir(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ============================================================
# LOAD DATA
# ============================================================
tx = Transcript()
morph = Morphology()

# Collect Currier A text tokens grouped by (folio, line)
records = defaultdict(list)  # (folio, line) -> [Token, ...]

for token in tx.currier_a(h_only=True, exclude_labels=True, exclude_uncertain=True):
    records[(token.folio, token.line)].append(token)

print(f"Total Currier A records (lines): {len(records)}")
print(f"Total Currier A tokens: {sum(len(v) for v in records.values())}")

# ============================================================
# ATOMIZE ALL TOKENS (pre-compute)
# ============================================================
# For each record, atomize every token
record_atoms = {}  # (folio, line) -> [AtomAnalysis, ...]
for key, tokens in records.items():
    record_atoms[key] = [morph.atomize(t.word) for t in tokens]

# ============================================================
# 1. RECORD LENGTH DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("1. RECORD LENGTH DISTRIBUTION")
print("=" * 70)

lengths = [len(v) for v in records.values()]
length_counts = Counter(lengths)

for length in sorted(length_counts):
    pct = 100.0 * length_counts[length] / len(records)
    print(f"  Length {length:2d}: {length_counts[length]:4d} records ({pct:5.1f}%)")

import statistics
print(f"\n  Mean:   {statistics.mean(lengths):.2f}")
print(f"  Median: {statistics.median(lengths):.1f}")
print(f"  StdDev: {statistics.stdev(lengths):.2f}")

# ============================================================
# 2. POSITIONAL HEAD GRAMMAR
# ============================================================
print("\n" + "=" * 70)
print("2. POSITIONAL HEAD GRAMMAR")
print("=" * 70)

def head_label(aa):
    """Return HEAD atom or 'HEADLESS' or 'SOLE:<atom>'."""
    if not aa.atoms:
        return 'EMPTY'
    head = aa.head
    if head is not None:
        return head
    # Check SOLE
    if aa.atoms[0][1] == 'SOLE':
        c = aa.atoms[0][0]
        if c in {'a', 'e', 'o', 'k', 't'}:
            return c
        return f'HL'  # headless sole
    if aa.is_headless:
        return 'HL'
    return 'HL'

def prefix_label(aa):
    return aa.prefix if aa.prefix else 'NONE'

def term_label(aa):
    t = aa.term
    if t:
        return t
    if aa.atoms:
        last_role = aa.atoms[-1][1]
        if last_role == 'SOLE':
            return aa.atoms[-1][0]
    return 'NONE'

# Length-3 records
for target_len in [2, 3, 4]:
    recs = [(k, v) for k, v in record_atoms.items() if len(v) == target_len]
    print(f"\n  --- Length-{target_len} records ({len(recs)} records) ---")

    for pos in range(target_len):
        pos_label = f"Position {pos+1}"
        head_counter = Counter()
        for k, atoms_list in recs:
            head_counter[head_label(atoms_list[pos])] += 1

        print(f"\n  {pos_label} HEAD distribution:")
        for h, cnt in head_counter.most_common(10):
            pct = 100.0 * cnt / len(recs)
            print(f"    {h:10s}: {cnt:4d} ({pct:5.1f}%)")

# Length 5+ grouped FIRST/MIDDLE/LAST
recs_long = [(k, v) for k, v in record_atoms.items() if len(v) >= 5]
if recs_long:
    print(f"\n  --- Length 5+ records ({len(recs_long)} records) ---")
    first_heads = Counter()
    middle_heads = Counter()
    last_heads = Counter()
    for k, atoms_list in recs_long:
        first_heads[head_label(atoms_list[0])] += 1
        last_heads[head_label(atoms_list[-1])] += 1
        for aa in atoms_list[1:-1]:
            middle_heads[head_label(aa)] += 1

    for label, ctr in [("FIRST", first_heads), ("MIDDLE", middle_heads), ("LAST", last_heads)]:
        print(f"\n  {label} HEAD distribution:")
        total = sum(ctr.values())
        for h, cnt in ctr.most_common(10):
            pct = 100.0 * cnt / total
            print(f"    {h:10s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 3. POSITIONAL PREFIX GRAMMAR
# ============================================================
print("\n" + "=" * 70)
print("3. POSITIONAL PREFIX GRAMMAR")
print("=" * 70)

for target_len in [2, 3, 4]:
    recs = [(k, v) for k, v in record_atoms.items() if len(v) == target_len]
    print(f"\n  --- Length-{target_len} records ({len(recs)} records) ---")

    for pos in range(target_len):
        pos_label = f"Position {pos+1}"
        pfx_counter = Counter()
        for k, atoms_list in recs:
            pfx_counter[prefix_label(atoms_list[pos])] += 1

        print(f"\n  {pos_label} PREFIX distribution:")
        for p, cnt in pfx_counter.most_common(10):
            pct = 100.0 * cnt / len(recs)
            print(f"    {p:10s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 4. HEAD-TO-HEAD TRANSITIONS
# ============================================================
print("\n" + "=" * 70)
print("4. HEAD-TO-HEAD TRANSITIONS (consecutive tokens within records)")
print("=" * 70)

transition_matrix = Counter()
for k, atoms_list in record_atoms.items():
    for i in range(len(atoms_list) - 1):
        h1 = head_label(atoms_list[i])
        h2 = head_label(atoms_list[i + 1])
        transition_matrix[(h1, h2)] += 1

# Show top 25 transitions
total_transitions = sum(transition_matrix.values())
print(f"\n  Total transitions: {total_transitions}")
print(f"\n  Top 25 HEAD->HEAD transitions:")
for (h1, h2), cnt in transition_matrix.most_common(25):
    pct = 100.0 * cnt / total_transitions
    print(f"    {h1:6s} -> {h2:6s}: {cnt:4d} ({pct:5.1f}%)")

# Build matrix view for the top heads
all_heads_seen = set()
for (h1, h2) in transition_matrix:
    all_heads_seen.add(h1)
    all_heads_seen.add(h2)

# Sort: o, e, a, k, t, HL, EMPTY
head_order = ['o', 'e', 'a', 'k', 't', 'HL', 'EMPTY']
head_order = [h for h in head_order if h in all_heads_seen]

print(f"\n  Transition matrix (rows=FROM, cols=TO):")
header = "        " + "".join(f"{h:>7s}" for h in head_order)
print(header)
for h1 in head_order:
    row_total = sum(transition_matrix.get((h1, h2), 0) for h2 in head_order)
    cells = []
    for h2 in head_order:
        cnt = transition_matrix.get((h1, h2), 0)
        if row_total > 0:
            pct = 100.0 * cnt / row_total
            cells.append(f"{pct:6.1f}%")
        else:
            cells.append(f"{'---':>7s}")
    print(f"  {h1:>6s}" + "".join(cells))

# ============================================================
# 5. RECORD TYPE TAXONOMY (HEAD sequence patterns)
# ============================================================
print("\n" + "=" * 70)
print("5. RECORD TYPE TAXONOMY (top 20 HEAD sequence patterns)")
print("=" * 70)

head_patterns = Counter()
for k, atoms_list in record_atoms.items():
    pattern = " -> ".join(head_label(aa) for aa in atoms_list)
    head_patterns[pattern] += 1

total_recs = len(records)
cumulative = 0
for pattern, cnt in head_patterns.most_common(20):
    pct = 100.0 * cnt / total_recs
    cumulative += pct
    print(f"  {pattern:40s}: {cnt:4d} ({pct:5.1f}%)  [cum: {cumulative:5.1f}%]")

# ============================================================
# 6. PREFIX SEQUENCE PATTERNS
# ============================================================
print("\n" + "=" * 70)
print("6. PREFIX SEQUENCE PATTERNS (top 20)")
print("=" * 70)

prefix_patterns = Counter()
for k, atoms_list in record_atoms.items():
    pattern = " -> ".join(prefix_label(aa) for aa in atoms_list)
    prefix_patterns[pattern] += 1

cumulative = 0
for pattern, cnt in prefix_patterns.most_common(20):
    pct = 100.0 * cnt / total_recs
    cumulative += pct
    print(f"  {pattern:50s}: {cnt:4d} ({pct:5.1f}%)  [cum: {cumulative:5.1f}%]")

# ============================================================
# 7. TYPICAL 3-TOKEN RECORD ANATOMY
# ============================================================
print("\n" + "=" * 70)
print("7. TYPICAL 3-TOKEN RECORD ANATOMY")
print("=" * 70)

# Find most common 3-token HEAD pattern
three_token_head_patterns = Counter()
three_token_records = {}  # pattern -> [(folio, line, words), ...]

for k, atoms_list in record_atoms.items():
    if len(atoms_list) != 3:
        continue
    pattern = " -> ".join(head_label(aa) for aa in atoms_list)
    three_token_head_patterns[pattern] += 1
    words = [records[k][i].word for i in range(3)]
    if pattern not in three_token_records:
        three_token_records[pattern] = []
    three_token_records[pattern].append((k[0], k[1], words))

top_pattern = three_token_head_patterns.most_common(1)[0][0]
print(f"\n  Most common 3-token HEAD pattern: {top_pattern}")
print(f"  Occurrences: {three_token_head_patterns[top_pattern]}")

# Show top 5 patterns with examples
for pattern, cnt in three_token_head_patterns.most_common(5):
    print(f"\n  Pattern: {pattern} ({cnt} records)")

    # Count actual word sequences
    word_seqs = Counter()
    for folio, line, words in three_token_records[pattern]:
        word_seqs[tuple(words)] += 1

    print(f"  Top 10 word sequences:")
    for words, wcnt in word_seqs.most_common(10):
        print(f"    {' | '.join(words):40s} x{wcnt}")

# ============================================================
# 8. e_depth TRAJECTORY WITHIN RECORDS
# ============================================================
print("\n" + "=" * 70)
print("8. e_depth TRAJECTORY WITHIN RECORDS (length 3+)")
print("=" * 70)

trajectory_types = Counter()  # 'INCREASING', 'DECREASING', 'FLAT', 'MIXED'

for k, atoms_list in record_atoms.items():
    if len(atoms_list) < 3:
        continue
    depths = [aa.e_depth for aa in atoms_list]

    diffs = [depths[i+1] - depths[i] for i in range(len(depths)-1)]

    if all(d > 0 for d in diffs):
        trajectory_types['INCREASING'] += 1
    elif all(d < 0 for d in diffs):
        trajectory_types['DECREASING'] += 1
    elif all(d == 0 for d in diffs):
        trajectory_types['FLAT'] += 1
    elif sum(diffs) > 0:
        trajectory_types['NET_INCREASE'] += 1
    elif sum(diffs) < 0:
        trajectory_types['NET_DECREASE'] += 1
    else:
        trajectory_types['NET_ZERO'] += 1

total_3plus = sum(trajectory_types.values())
print(f"\n  Records of length 3+: {total_3plus}")
for traj, cnt in trajectory_types.most_common():
    pct = 100.0 * cnt / total_3plus
    print(f"    {traj:15s}: {cnt:4d} ({pct:5.1f}%)")

# Average e_depth by position (for length-3 records)
len3_recs = [(k, v) for k, v in record_atoms.items() if len(v) == 3]
print(f"\n  Average e_depth by position (length-3 records, n={len(len3_recs)}):")
for pos in range(3):
    depths = [atoms_list[pos].e_depth for _, atoms_list in len3_recs]
    avg = sum(depths) / len(depths) if depths else 0
    print(f"    Position {pos+1}: {avg:.3f}")

# ============================================================
# 9. TERMINAL TOKEN ANALYSIS (LAST token in record)
# ============================================================
print("\n" + "=" * 70)
print("9. TERMINAL TOKEN ANALYSIS (last token in each record)")
print("=" * 70)

last_heads = Counter()
last_prefixes = Counter()
last_terms = Counter()
last_opacity = Counter()

for k, atoms_list in record_atoms.items():
    last = atoms_list[-1]
    last_heads[head_label(last)] += 1
    last_prefixes[prefix_label(last)] += 1
    last_terms[term_label(last)] += 1
    last_opacity[last.terminal_opacity] += 1

print(f"\n  HEAD distribution (last token):")
for h, cnt in last_heads.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {h:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  PREFIX distribution (last token):")
for p, cnt in last_prefixes.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {p:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  TERM distribution (last token):")
for t, cnt in last_terms.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {t:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  Terminal opacity (last token):")
for op, cnt in last_opacity.most_common():
    pct = 100.0 * cnt / total_recs
    print(f"    {op:20s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 10. FIRST TOKEN ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("10. FIRST TOKEN ANALYSIS (first token in each record)")
print("=" * 70)

first_heads = Counter()
first_prefixes = Counter()
first_terms = Counter()
first_opacity = Counter()

for k, atoms_list in record_atoms.items():
    first = atoms_list[0]
    first_heads[head_label(first)] += 1
    first_prefixes[prefix_label(first)] += 1
    first_terms[term_label(first)] += 1
    first_opacity[first.terminal_opacity] += 1

print(f"\n  HEAD distribution (first token):")
for h, cnt in first_heads.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {h:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  PREFIX distribution (first token):")
for p, cnt in first_prefixes.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {p:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  TERM distribution (first token):")
for t, cnt in first_terms.most_common(10):
    pct = 100.0 * cnt / total_recs
    print(f"    {t:10s}: {cnt:4d} ({pct:5.1f}%)")

print(f"\n  Terminal opacity (first token):")
for op, cnt in first_opacity.most_common():
    pct = 100.0 * cnt / total_recs
    print(f"    {op:20s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    "metadata": {
        "script": "s3_a_record_structure.py",
        "total_records": len(records),
        "total_tokens": sum(len(v) for v in records.values()),
    },
    "record_length_distribution": {str(k): v for k, v in sorted(length_counts.items())},
    "record_length_stats": {
        "mean": round(statistics.mean(lengths), 2),
        "median": statistics.median(lengths),
        "stdev": round(statistics.stdev(lengths), 2),
    },
    "positional_head_grammar": {},
    "positional_prefix_grammar": {},
    "head_transitions": {
        "total": total_transitions,
        "top_25": [
            {"from": h1, "to": h2, "count": cnt, "pct": round(100.0 * cnt / total_transitions, 2)}
            for (h1, h2), cnt in transition_matrix.most_common(25)
        ],
        "matrix": {
            h1: {h2: transition_matrix.get((h1, h2), 0) for h2 in head_order}
            for h1 in head_order
        },
    },
    "head_sequence_patterns_top20": [
        {"pattern": p, "count": c, "pct": round(100.0 * c / total_recs, 2)}
        for p, c in head_patterns.most_common(20)
    ],
    "prefix_sequence_patterns_top20": [
        {"pattern": p, "count": c, "pct": round(100.0 * c / total_recs, 2)}
        for p, c in prefix_patterns.most_common(20)
    ],
    "e_depth_trajectory": {
        "total_records_3plus": total_3plus,
        "trajectories": {t: c for t, c in trajectory_types.most_common()},
    },
    "terminal_token": {
        "head": {h: c for h, c in last_heads.most_common(10)},
        "prefix": {p: c for p, c in last_prefixes.most_common(10)},
        "term": {t: c for t, c in last_terms.most_common(10)},
        "opacity": {o: c for o, c in last_opacity.most_common()},
    },
    "first_token": {
        "head": {h: c for h, c in first_heads.most_common(10)},
        "prefix": {p: c for p, c in first_prefixes.most_common(10)},
        "term": {t: c for t, c in first_terms.most_common(10)},
        "opacity": {o: c for o, c in first_opacity.most_common()},
    },
}

# Add positional grammar for lengths 2-4
for target_len in [2, 3, 4]:
    recs = [(k, v) for k, v in record_atoms.items() if len(v) == target_len]
    head_by_pos = {}
    pfx_by_pos = {}
    for pos in range(target_len):
        hc = Counter()
        pc = Counter()
        for k, atoms_list in recs:
            hc[head_label(atoms_list[pos])] += 1
            pc[prefix_label(atoms_list[pos])] += 1
        head_by_pos[f"pos_{pos+1}"] = {h: c for h, c in hc.most_common(10)}
        pfx_by_pos[f"pos_{pos+1}"] = {p: c for p, c in pc.most_common(10)}
    results["positional_head_grammar"][f"length_{target_len}"] = {
        "n_records": len(recs),
        "positions": head_by_pos,
    }
    results["positional_prefix_grammar"][f"length_{target_len}"] = {
        "n_records": len(recs),
        "positions": pfx_by_pos,
    }

out_path = Path("phases/CURRIER_A_ATOMS/results/s3_a_record_structure.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n\nResults saved to {out_path}")
print("Done.")
