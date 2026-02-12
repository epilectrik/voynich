#!/usr/bin/env python3
"""BIN_HAZARD_NECESSITY: Ablation study for affordance bins.

For each of 9 functional bins, remove all tokens whose MIDDLE belongs
to that bin. Recompute structural metrics on the reduced corpus.
Compare against full-corpus baseline.

Question: Which bins are structurally load-bearing for the
hazard/lane/recovery architecture?

Key test: If removing STABILITY_CRITICAL collapses CHSH absorption,
hazard distribution, or forbidden-pair topology, that bin is not
narrative convenience -- it's structural necessity.
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Load data ──────────────────────────────────────────────────────

with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
middle_to_qo = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
    sig = data.get('behavioral_signature', {})
    middle_to_qo[mid] = sig.get('qo_affinity', 0.5)
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# Lane thresholds (same as T2)
QO_THRESH = 0.6
CHSH_THRESH = 0.4

def classify_lane(qo_aff):
    if qo_aff > QO_THRESH:
        return 'QO'
    elif qo_aff < CHSH_THRESH:
        return 'CHSH'
    return 'NEUTRAL'

# Forbidden transitions
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json') as f:
    inv = json.load(f)

forbidden_pairs = set()
forbidden_sources = set()
forbidden_targets = set()
for t in inv['transitions']:
    forbidden_pairs.add((t['source'], t['target']))
    forbidden_sources.add(t['source'])
    forbidden_targets.add(t['target'])

morph_tmp = Morphology()
hazard_middles = set()
for s in forbidden_sources | forbidden_targets:
    m = morph_tmp.extract(s)
    if m.middle:
        hazard_middles.add(m.middle)

# ICC class map
with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)
token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

# FQ classes
with open(PROJECT / 'phases' / 'HAZARD_CLASS_VULNERABILITY' / 'results' / 'hazard_exposure_anatomy.json') as f:
    haz_anatomy = json.load(f)
class_to_role = {}
for cls_str, info in haz_anatomy['section1_class_routing']['per_class'].items():
    class_to_role[int(cls_str)] = info['role']
FQ_CLASSES = {c for c, r in class_to_role.items() if r == 'FREQUENT_OPERATOR'}

# ── Build corpus ───────────────────────────────────────────────────

tx = Transcript()
morph = Morphology()

# Store all tokens with full metadata, grouped by line
corpus_lines = []  # list of lists of token dicts
current_key = None
current_line = []

for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)
    qo = middle_to_qo.get(mid, 0.5)
    cls = token_to_class.get(word, -1)

    key = (token.folio, token.line)
    if key != current_key:
        if current_line:
            corpus_lines.append(current_line)
        current_line = []
        current_key = key

    current_line.append({
        'word': word,
        'middle': mid,
        'bin': b,
        'lane': classify_lane(qo),
        'cls': cls,
    })

if current_line:
    corpus_lines.append(current_line)

print("=" * 70)
print("BIN HAZARD NECESSITY: ABLATION STUDY")
print("=" * 70)
print(f"\nCorpus: {len(corpus_lines)} lines, {sum(len(l) for l in corpus_lines)} tokens")

# ── Metrics computation ────────────────────────────────────────────

def compute_metrics(lines, label=""):
    """Compute structural fingerprint from a set of lines (list of token lists)."""
    total = 0
    lane_counts = Counter()
    hazard_cls_count = 0
    hazard_adj_count = 0
    forbidden_mid_count = 0
    same_lane = 0
    switch_lane = 0
    line_positions = []
    initial_count = 0
    final_count = 0
    fq_distances = []
    induced_forbidden = 0

    for line in lines:
        n = len(line)
        if n == 0:
            continue

        # Hazard positions and FQ positions
        hazard_pos = set()
        fq_pos = set()
        for i, tok in enumerate(line):
            if tok['cls'] in HAZARD_CLASSES:
                hazard_pos.add(i)
            if tok['cls'] in FQ_CLASSES:
                fq_pos.add(i)

        for i, tok in enumerate(line):
            total += 1
            lane_counts[tok['lane']] += 1

            # Hazard class membership
            if tok['cls'] in HAZARD_CLASSES:
                hazard_cls_count += 1

            # Hazard adjacency
            if tok['cls'] not in HAZARD_CLASSES and hazard_pos:
                if (i > 0 and (i - 1) in hazard_pos) or (i < n - 1 and (i + 1) in hazard_pos):
                    hazard_adj_count += 1

            # Forbidden-MIDDLE
            if tok['middle'] in hazard_middles:
                forbidden_mid_count += 1

            # Line position
            rel_pos = i / max(n - 1, 1)
            line_positions.append(rel_pos)
            if i == 0:
                initial_count += 1
            if i == n - 1:
                final_count += 1

            # FQ distance
            if tok['cls'] not in FQ_CLASSES and fq_pos:
                dist = min(abs(i - fp) for fp in fq_pos)
                fq_distances.append(dist)

        # Lane inertia
        for i in range(n - 1):
            a_lane = line[i]['lane']
            b_lane = line[i + 1]['lane']
            if a_lane in ('QO', 'CHSH') and b_lane in ('QO', 'CHSH'):
                if a_lane == b_lane:
                    same_lane += 1
                else:
                    switch_lane += 1

        # Induced forbidden pairs (check adjacent token words)
        for i in range(n - 1):
            pair = (line[i]['word'], line[i + 1]['word'])
            if pair in forbidden_pairs:
                induced_forbidden += 1

    if total == 0:
        return None

    lane_trans = same_lane + switch_lane
    return {
        'total_tokens': total,
        'qo_fraction': lane_counts['QO'] / total,
        'chsh_fraction': lane_counts['CHSH'] / total,
        'neutral_fraction': lane_counts['NEUTRAL'] / total,
        'hazard_class_rate': hazard_cls_count / total,
        'hazard_adj_rate': hazard_adj_count / max(total - hazard_cls_count, 1),
        'forbidden_mid_rate': forbidden_mid_count / total,
        'lane_inertia': same_lane / lane_trans if lane_trans > 0 else 0,
        'mean_line_position': float(np.mean(line_positions)),
        'initial_rate': initial_count / total,
        'final_rate': final_count / total,
        'mean_fq_distance': float(np.mean(fq_distances)) if fq_distances else 0,
        'induced_forbidden_pairs': induced_forbidden,
    }


def ablate_bin(lines, remove_bin):
    """Remove all tokens whose bin == remove_bin, return new lines."""
    new_lines = []
    for line in lines:
        new_line = [tok for tok in line if tok['bin'] != remove_bin]
        if new_line:
            new_lines.append(new_line)
    return new_lines


# ── Baseline ───────────────────────────────────────────────────────

baseline = compute_metrics(corpus_lines, "FULL")

print(f"\nBASELINE (full corpus):")
for k, v in baseline.items():
    if isinstance(v, float):
        print(f"  {k:>25}: {v:.4f}")
    else:
        print(f"  {k:>25}: {v}")

# ── Ablation loop ──────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("ABLATION RESULTS")
print("=" * 70)

METRIC_KEYS = [
    'qo_fraction', 'chsh_fraction', 'neutral_fraction',
    'hazard_class_rate', 'hazard_adj_rate', 'forbidden_mid_rate',
    'lane_inertia', 'mean_line_position', 'initial_rate', 'final_rate',
    'mean_fq_distance',
]

ablation_results = {}

for remove_bin in FUNCTIONAL_BINS:
    label = bin_labels.get(remove_bin, '?')
    ablated_lines = ablate_bin(corpus_lines, remove_bin)
    metrics = compute_metrics(ablated_lines)

    # Compute changes from baseline
    changes = {}
    for k in METRIC_KEYS:
        base_val = baseline[k]
        abl_val = metrics[k]
        if base_val != 0:
            pct_change = 100 * (abl_val - base_val) / abs(base_val)
        else:
            pct_change = 0
        changes[k] = {
            'baseline': base_val,
            'ablated': abl_val,
            'abs_change': abl_val - base_val,
            'pct_change': pct_change,
        }

    # L2 degradation score (on percentage changes)
    pct_changes = [changes[k]['pct_change'] for k in METRIC_KEYS]
    degradation = np.sqrt(np.sum(np.array(pct_changes) ** 2))

    ablation_results[remove_bin] = {
        'label': label,
        'tokens_removed': baseline['total_tokens'] - metrics['total_tokens'],
        'pct_removed': 100 * (1 - metrics['total_tokens'] / baseline['total_tokens']),
        'metrics': metrics,
        'changes': changes,
        'degradation_score': degradation,
        'induced_forbidden': metrics['induced_forbidden_pairs'],
    }

# Print summary table
print(f"\n  {'Bin':>4} {'Label':>25} {'Removed':>8} {'Rem%':>6} {'Degrad':>8} {'Forbid':>7}")
print(f"  {'-' * 62}")
for b in sorted(FUNCTIONAL_BINS, key=lambda x: -ablation_results[x]['degradation_score']):
    r = ablation_results[b]
    print(f"  {b:>4} {r['label']:>25} {r['tokens_removed']:>8} {r['pct_removed']:>5.1f}% {r['degradation_score']:>8.2f} {r['induced_forbidden']:>7}")

# ── Per-bin detail ─────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("PER-BIN ABLATION DETAIL")
print("=" * 70)

for b in sorted(FUNCTIONAL_BINS, key=lambda x: -ablation_results[x]['degradation_score']):
    r = ablation_results[b]
    print(f"\n  --- Bin {b}: {r['label']} (removed {r['tokens_removed']} tokens, {r['pct_removed']:.1f}%) ---")
    print(f"  {'Metric':>25} {'Baseline':>10} {'Ablated':>10} {'Change':>10} {'%Change':>9}")
    print(f"  {'-' * 66}")
    for k in METRIC_KEYS:
        c = r['changes'][k]
        print(f"  {k:>25} {c['baseline']:>10.4f} {c['ablated']:>10.4f} {c['abs_change']:>+10.4f} {c['pct_change']:>+8.1f}%")
    if r['induced_forbidden'] > 0:
        print(f"  {'INDUCED FORBIDDEN PAIRS':>25}: {r['induced_forbidden']}")

# ── STABILITY_CRITICAL deep dive ──────────────────────────────────

print(f"\n{'=' * 70}")
print("STABILITY_CRITICAL (BIN 8) DEEP DIVE")
print("=" * 70)

b8 = ablation_results[8]
print(f"\n  Tokens removed: {b8['tokens_removed']} ({b8['pct_removed']:.1f}% of corpus)")
print(f"  Degradation score: {b8['degradation_score']:.2f}")

# Key metrics
print(f"\n  CHSH fraction: {baseline['chsh_fraction']:.4f} -> {b8['metrics']['chsh_fraction']:.4f} ({b8['changes']['chsh_fraction']['pct_change']:+.1f}%)")
print(f"  Hazard class rate: {baseline['hazard_class_rate']:.4f} -> {b8['metrics']['hazard_class_rate']:.4f} ({b8['changes']['hazard_class_rate']['pct_change']:+.1f}%)")
print(f"  Forbidden-MIDDLE rate: {baseline['forbidden_mid_rate']:.4f} -> {b8['metrics']['forbidden_mid_rate']:.4f} ({b8['changes']['forbidden_mid_rate']['pct_change']:+.1f}%)")
print(f"  Lane inertia: {baseline['lane_inertia']:.4f} -> {b8['metrics']['lane_inertia']:.4f} ({b8['changes']['lane_inertia']['pct_change']:+.1f}%)")
print(f"  Induced forbidden pairs: {b8['induced_forbidden']}")

# What % of hazard-class tokens were in bin 8?
b8_hazard_in_bin = sum(
    1 for line in corpus_lines for tok in line
    if tok['bin'] == 8 and tok['cls'] in HAZARD_CLASSES
)
total_hazard = sum(
    1 for line in corpus_lines for tok in line
    if tok['cls'] in HAZARD_CLASSES
)
print(f"\n  Bin 8 hazard-class tokens: {b8_hazard_in_bin} / {total_hazard} ({100*b8_hazard_in_bin/total_hazard:.1f}%)")

# What % of CHSH tokens were in bin 8?
b8_chsh = sum(
    1 for line in corpus_lines for tok in line
    if tok['bin'] == 8 and tok['lane'] == 'CHSH'
)
total_chsh = sum(
    1 for line in corpus_lines for tok in line
    if tok['lane'] == 'CHSH'
)
print(f"  Bin 8 CHSH tokens: {b8_chsh} / {total_chsh} ({100*b8_chsh/total_chsh:.1f}%)")

# ── HUB_UNIVERSAL deep dive ───────────────────────────────────────

print(f"\n{'=' * 70}")
print("HUB_UNIVERSAL (BIN 6) DEEP DIVE")
print("=" * 70)

b6 = ablation_results[6]
print(f"\n  Tokens removed: {b6['tokens_removed']} ({b6['pct_removed']:.1f}% of corpus)")
print(f"  Degradation score: {b6['degradation_score']:.2f}")

print(f"\n  CHSH fraction: {baseline['chsh_fraction']:.4f} -> {b6['metrics']['chsh_fraction']:.4f} ({b6['changes']['chsh_fraction']['pct_change']:+.1f}%)")
print(f"  Hazard class rate: {baseline['hazard_class_rate']:.4f} -> {b6['metrics']['hazard_class_rate']:.4f} ({b6['changes']['hazard_class_rate']['pct_change']:+.1f}%)")
print(f"  Forbidden-MIDDLE rate: {baseline['forbidden_mid_rate']:.4f} -> {b6['metrics']['forbidden_mid_rate']:.4f} ({b6['changes']['forbidden_mid_rate']['pct_change']:+.1f}%)")
print(f"  Lane inertia: {baseline['lane_inertia']:.4f} -> {b6['metrics']['lane_inertia']:.4f} ({b6['changes']['lane_inertia']['pct_change']:+.1f}%)")
print(f"  Induced forbidden pairs: {b6['induced_forbidden']}")

# ── Normalized degradation (per-token) ─────────────────────────────

print(f"\n{'=' * 70}")
print("NORMALIZED DEGRADATION (per 1% corpus removed)")
print("=" * 70)

print(f"\n  {'Bin':>4} {'Label':>25} {'Rem%':>6} {'RawDeg':>8} {'NormDeg':>9}")
print(f"  {'-' * 56}")
for b in sorted(FUNCTIONAL_BINS, key=lambda x: -ablation_results[x]['degradation_score'] / max(ablation_results[x]['pct_removed'], 0.01)):
    r = ablation_results[b]
    norm = r['degradation_score'] / max(r['pct_removed'], 0.01)
    print(f"  {b:>4} {r['label']:>25} {r['pct_removed']:>5.1f}% {r['degradation_score']:>8.2f} {norm:>9.2f}")

# ── Verdict ────────────────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

# Rank by normalized degradation
ranked = sorted(FUNCTIONAL_BINS, key=lambda x: -ablation_results[x]['degradation_score'] / max(ablation_results[x]['pct_removed'], 0.01))

print(f"\n  STRUCTURAL NECESSITY RANKING (by degradation per % removed):")
for i, b in enumerate(ranked):
    r = ablation_results[b]
    norm = r['degradation_score'] / max(r['pct_removed'], 0.01)
    tier = "LOAD-BEARING" if norm > 5 else "SIGNIFICANT" if norm > 2 else "MODERATE" if norm > 1 else "DISPENSABLE"
    print(f"    {i+1}. Bin {b:>2} ({r['label']:>25}): norm_deg={norm:.2f} [{tier}]")

# STABILITY_CRITICAL verdict
b8_verdict = "LOAD-BEARING" if b8['degradation_score'] / max(b8['pct_removed'], 0.01) > 5 else "SIGNIFICANT"
print(f"\n  STABILITY_CRITICAL (Bin 8): {b8_verdict}")
if b8['induced_forbidden'] > 0:
    print(f"    CRITICAL: Removing Bin 8 INDUCES {b8['induced_forbidden']} forbidden pairs!")
    print(f"    The grammar's safety guarantee is violated without this bin.")

# ── Save results ───────────────────────────────────────────────────

results = {
    'metadata': {
        'phase': 'BIN_HAZARD_NECESSITY',
        'test': 'BIN_ABLATION',
        'n_functional_bins': len(FUNCTIONAL_BINS),
        'corpus_lines': len(corpus_lines),
        'corpus_tokens': baseline['total_tokens'],
    },
    'baseline': baseline,
    'ablations': {},
    'ranking': [],
}

for b in ranked:
    r = ablation_results[b]
    norm = r['degradation_score'] / max(r['pct_removed'], 0.01)
    results['ablations'][str(b)] = {
        'label': r['label'],
        'tokens_removed': r['tokens_removed'],
        'pct_removed': round(r['pct_removed'], 2),
        'degradation_score': round(r['degradation_score'], 3),
        'normalized_degradation': round(norm, 3),
        'induced_forbidden_pairs': r['induced_forbidden'],
        'metrics': {k: round(v, 5) if isinstance(v, float) else v for k, v in r['metrics'].items()},
        'changes': {
            k: {
                'abs_change': round(v['abs_change'], 5),
                'pct_change': round(v['pct_change'], 2),
            }
            for k, v in r['changes'].items()
        },
    }
    results['ranking'].append({
        'rank': len(results['ranking']) + 1,
        'bin': b,
        'label': r['label'],
        'normalized_degradation': round(norm, 3),
    })

out_path = PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' / 'bin_ablation.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")
