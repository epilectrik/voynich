#!/usr/bin/env python3
"""Exploratory: Three structural checks on hazardous vs safe flow.

Tests whether the physical interpretation (hazardous flow = intervention
during active distillation, safe flow = terminal collection) produces
testable structural predictions.

Test 1: Successor monitoring rate — do ch/sh (test/monitor) prefixes
        follow hazardous flow tokens more than safe flow tokens?
Test 2: Energy co-occurrence — do lines with hazardous flow contain
        more energy MIDDLEs (k, ke, kch) than lines with safe flow?
Test 3: Seal proximity — does dy (seal) appear near hazardous flow
        tokens more than near safe flow tokens?
"""

import sys
import functools
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Token class membership ───────────────────────────────────────

HAZARDOUS_FLOW_TOKENS = {
    # Class 7
    'ar', 'al',
    # Class 30
    'dar', 'dal', 'dain', 'dair', 'dam',
}

SAFE_FLOW_TOKENS = {
    # Class 38
    'aral', 'aldy', 'arody', 'aram', 'arol', 'daim',
    # Class 40
    'daly', 'aly', 'ary', 'dary', 'daiir', 'dan',
}

ENERGY_MIDDLES = {'k', 'ke', 'kch'}
SEAL_MIDDLE = 'dy'
MONITORING_PREFIXES = {'ch', 'sh'}

# ── Load data ────────────────────────────────────────────────────

print("Loading B corpus...")
tx = Transcript()
morph = Morphology()

# Build line-level token lists
lines = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    mid = m.middle if m and m.middle else w
    pfx = m.prefix if m and m.prefix else None
    lines[(token.folio, token.line)].append({
        'word': w,
        'middle': mid,
        'prefix': pfx,
    })

print(f"  {len(lines)} lines loaded")

# Count hazardous and safe flow token occurrences
hz_count = sum(1 for line in lines.values() for t in line if t['word'] in HAZARDOUS_FLOW_TOKENS)
sf_count = sum(1 for line in lines.values() for t in line if t['word'] in SAFE_FLOW_TOKENS)
print(f"  Hazardous flow tokens: {hz_count}")
print(f"  Safe flow tokens: {sf_count}")

# ══════════════════════════════════════════════════════════════════
# TEST 1: Successor monitoring rate
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 1: Successor Monitoring Rate")
print("=" * 60)
print("Prediction: ch/sh (test/monitor) follows hazardous flow")
print("            MORE than safe flow\n")

hz_successors = Counter()
hz_succ_monitoring = 0
hz_succ_total = 0

sf_successors = Counter()
sf_succ_monitoring = 0
sf_succ_total = 0

for (folio, line_id), tokens in lines.items():
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        succ = tokens[i + 1]

        if curr['word'] in HAZARDOUS_FLOW_TOKENS:
            hz_succ_total += 1
            succ_pfx = succ['prefix']
            hz_successors[succ_pfx] += 1
            if succ_pfx in MONITORING_PREFIXES:
                hz_succ_monitoring += 1

        elif curr['word'] in SAFE_FLOW_TOKENS:
            sf_succ_total += 1
            succ_pfx = succ['prefix']
            sf_successors[succ_pfx] += 1
            if succ_pfx in MONITORING_PREFIXES:
                sf_succ_monitoring += 1

hz_rate = hz_succ_monitoring / max(hz_succ_total, 1)
sf_rate = sf_succ_monitoring / max(sf_succ_total, 1)

print(f"Hazardous flow → monitoring successor: {hz_succ_monitoring}/{hz_succ_total} = {hz_rate:.3f}")
print(f"Safe flow → monitoring successor:      {sf_succ_monitoring}/{sf_succ_total} = {sf_rate:.3f}")
print(f"Ratio: {hz_rate / max(sf_rate, 0.001):.2f}x")

# Fisher's exact test
table = [[hz_succ_monitoring, hz_succ_total - hz_succ_monitoring],
         [sf_succ_monitoring, sf_succ_total - sf_succ_monitoring]]
odds_ratio, p_fisher = fisher_exact(table, alternative='greater')
print(f"Fisher exact (one-sided): OR={odds_ratio:.2f}, p={p_fisher:.4f}")

# Show top successor prefixes for each
print(f"\nHazardous flow successor prefixes (top 10):")
for pfx, n in hz_successors.most_common(10):
    pct = n / max(hz_succ_total, 1) * 100
    print(f"  {pfx or '(none)':>8}: {n:4d} ({pct:.1f}%)")

print(f"\nSafe flow successor prefixes (top 10):")
for pfx, n in sf_successors.most_common(10):
    pct = n / max(sf_succ_total, 1) * 100
    print(f"  {pfx or '(none)':>8}: {n:4d} ({pct:.1f}%)")


# ══════════════════════════════════════════════════════════════════
# TEST 2: Energy co-occurrence on same line
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 2: Energy Co-occurrence on Same Line")
print("=" * 60)
print("Prediction: lines with hazardous flow contain MORE energy")
print("            MIDDLEs (k/ke/kch) than lines with safe flow\n")

hz_lines_energy = []  # (has_energy, energy_count) per hazardous-flow line
sf_lines_energy = []

for (folio, line_id), tokens in lines.items():
    has_hazardous = any(t['word'] in HAZARDOUS_FLOW_TOKENS for t in tokens)
    has_safe = any(t['word'] in SAFE_FLOW_TOKENS for t in tokens)
    energy_count = sum(1 for t in tokens if t['middle'] in ENERGY_MIDDLES)
    line_len = len(tokens)

    if has_hazardous:
        hz_lines_energy.append((energy_count, line_len))
    if has_safe:
        sf_lines_energy.append((energy_count, line_len))

hz_energy_counts = [e for e, _ in hz_lines_energy]
sf_energy_counts = [e for e, _ in sf_lines_energy]

hz_energy_rates = [e / l for e, l in hz_lines_energy if l > 0]
sf_energy_rates = [e / l for e, l in sf_lines_energy if l > 0]

hz_mean_count = np.mean(hz_energy_counts) if hz_energy_counts else 0
sf_mean_count = np.mean(sf_energy_counts) if sf_energy_counts else 0
hz_mean_rate = np.mean(hz_energy_rates) if hz_energy_rates else 0
sf_mean_rate = np.mean(sf_energy_rates) if sf_energy_rates else 0

print(f"Lines containing hazardous flow: {len(hz_lines_energy)}")
print(f"Lines containing safe flow:      {len(sf_lines_energy)}")
print(f"\nMean energy tokens per line:")
print(f"  Hazardous flow lines: {hz_mean_count:.2f} (rate: {hz_mean_rate:.3f})")
print(f"  Safe flow lines:      {sf_mean_count:.2f} (rate: {sf_mean_rate:.3f})")
print(f"  Ratio: {hz_mean_rate / max(sf_mean_rate, 0.001):.2f}x")

if len(hz_energy_rates) >= 5 and len(sf_energy_rates) >= 5:
    stat, p_mw = mannwhitneyu(hz_energy_rates, sf_energy_rates, alternative='greater')
    print(f"  Mann-Whitney U (one-sided): U={stat:.0f}, p={p_mw:.4f}")


# ══════════════════════════════════════════════════════════════════
# TEST 3: Seal (dy) proximity
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 3: Seal (dy) Proximity")
print("=" * 60)
print("Prediction: dy (seal) appears near hazardous flow tokens")
print("            MORE than near safe flow tokens\n")

WINDOW = 2  # ±2 tokens

hz_seal_near = 0
hz_seal_total = 0
sf_seal_near = 0
sf_seal_total = 0

# Also check same-line co-occurrence
hz_lines_with_seal = 0
hz_lines_total = 0
sf_lines_with_seal = 0
sf_lines_total = 0

for (folio, line_id), tokens in lines.items():
    has_hazardous = any(t['word'] in HAZARDOUS_FLOW_TOKENS for t in tokens)
    has_safe = any(t['word'] in SAFE_FLOW_TOKENS for t in tokens)
    has_seal = any(t['middle'] == SEAL_MIDDLE for t in tokens)

    if has_hazardous:
        hz_lines_total += 1
        if has_seal:
            hz_lines_with_seal += 1

    if has_safe:
        sf_lines_total += 1
        if has_seal:
            sf_lines_with_seal += 1

    # Window-based proximity
    for i, t in enumerate(tokens):
        window_middles = set()
        for j in range(max(0, i - WINDOW), min(len(tokens), i + WINDOW + 1)):
            if j != i:
                window_middles.add(tokens[j]['middle'])

        if t['word'] in HAZARDOUS_FLOW_TOKENS:
            hz_seal_total += 1
            if SEAL_MIDDLE in window_middles:
                hz_seal_near += 1

        elif t['word'] in SAFE_FLOW_TOKENS:
            sf_seal_total += 1
            if SEAL_MIDDLE in window_middles:
                sf_seal_near += 1

hz_prox_rate = hz_seal_near / max(hz_seal_total, 1)
sf_prox_rate = sf_seal_near / max(sf_seal_total, 1)
hz_line_rate = hz_lines_with_seal / max(hz_lines_total, 1)
sf_line_rate = sf_lines_with_seal / max(sf_lines_total, 1)

print(f"Window proximity (±{WINDOW} tokens):")
print(f"  Hazardous flow near dy: {hz_seal_near}/{hz_seal_total} = {hz_prox_rate:.3f}")
print(f"  Safe flow near dy:      {sf_seal_near}/{sf_seal_total} = {sf_prox_rate:.3f}")
if sf_prox_rate > 0:
    print(f"  Ratio: {hz_prox_rate / sf_prox_rate:.2f}x")

table3 = [[hz_seal_near, hz_seal_total - hz_seal_near],
          [sf_seal_near, sf_seal_total - sf_seal_near]]
if min(hz_seal_total, sf_seal_total) > 0:
    or3, p3 = fisher_exact(table3, alternative='greater')
    print(f"  Fisher exact (one-sided): OR={or3:.2f}, p={p3:.4f}")

print(f"\nSame-line co-occurrence:")
print(f"  Hazardous flow lines with dy: {hz_lines_with_seal}/{hz_lines_total} = {hz_line_rate:.3f}")
print(f"  Safe flow lines with dy:      {sf_lines_with_seal}/{sf_lines_total} = {sf_line_rate:.3f}")

# ══════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Test 1 (successor monitoring): hz={hz_rate:.3f} vs sf={sf_rate:.3f}, p={p_fisher:.4f}")
print(f"Test 2 (energy co-occurrence):  hz={hz_mean_rate:.3f} vs sf={sf_mean_rate:.3f}", end="")
if len(hz_energy_rates) >= 5 and len(sf_energy_rates) >= 5:
    print(f", p={p_mw:.4f}")
else:
    print(" (insufficient data)")
print(f"Test 3 (seal proximity ±{WINDOW}):   hz={hz_prox_rate:.3f} vs sf={sf_prox_rate:.3f}", end="")
if min(hz_seal_total, sf_seal_total) > 0:
    print(f", p={p3:.4f}")
else:
    print(" (insufficient data)")
