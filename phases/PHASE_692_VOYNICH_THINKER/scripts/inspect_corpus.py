#!/usr/bin/env python3
"""Spot-check the training corpus."""
import json
from pathlib import Path
from collections import Counter

PHASE_DIR = Path(__file__).resolve().parents[1]
path = PHASE_DIR / 'data' / 'training_corpus.jsonl'

types = Counter()
tiers = Counter()
total_chars = 0
total = 0
samples_per_type = {}
size_by_type = {}

with open(path, encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        t = r['type']
        types[t] += 1
        tiers[r['tier']] += 1
        size = len(r['content'])
        total_chars += size
        total += 1
        size_by_type[t] = size_by_type.get(t, 0) + size
        if t not in samples_per_type:
            samples_per_type[t] = r

print(f"Total entries: {total}")
print(f"Total chars: {total_chars:,}")
print(f"Avg chars/entry: {total_chars/total:.0f}")

print(f"\nBy type:")
for t, n in types.most_common():
    avg = size_by_type[t] / n
    print(f"  {t:>20s}: {n:>5d} entries, {size_by_type[t]:>10,d} chars total, {avg:>7.0f} avg")

print(f"\nBy tier:")
for tier in sorted(tiers.keys()):
    print(f"  Tier {tier}: {tiers[tier]} entries")

print(f"\n=== Samples ===\n")
for t, sample in samples_per_type.items():
    print(f"\n--- TYPE: {t} ---")
    print(f"Source: {sample['source']}")
    print(f"Tier: {sample['tier']}")
    print(f"Metadata: {sample.get('metadata')}")
    content = sample['content'][:400]
    print(f"Content (first 400 chars):\n{content}\n")
