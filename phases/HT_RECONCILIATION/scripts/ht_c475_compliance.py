"""
HT_RECONCILIATION - Script 2: HT C475 Compliance
T2: HT MIDDLE graph participation rate
T3: HT within-line C475 violation rate

Requires T1 PASS.
"""
import json, sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
rng = np.random.RandomState(42)

# --- Load classified set ---
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# --- Load C475 incompatibility data ---
incompat_path = PROJECT_ROOT / 'results' / 'middle_incompatibility.json'
with open(incompat_path, 'r', encoding='utf-8') as f:
    incompat = json.load(f)

# Build illegal pairs set and graph MIDDLEs
illegal_pairs = set()
graph_middles = set()
for pair_data in incompat['illegal_pairs']:
    a, b = pair_data[0]
    illegal_pairs.add(frozenset([a, b]))
    graph_middles.add(a)
    graph_middles.add(b)

print(f"C475 graph: {len(graph_middles)} MIDDLEs, {len(illegal_pairs)} illegal pairs")

# --- Collect B tokens per line with metadata ---
line_tokens = defaultdict(list)  # (folio, line) -> list of token dicts

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    is_ht = w not in classified_tokens
    m = morph.extract(w)
    line_tokens[(token.folio, token.line)].append({
        'word': w,
        'is_ht': is_ht,
        'middle': m.middle,
    })

# --- Collect all HT MIDDLEs and classified MIDDLEs ---
ht_middle_types = set()
classified_middle_types = set()
ht_middle_counts = Counter()
classified_middle_counts = Counter()

for tokens in line_tokens.values():
    for t in tokens:
        mid = t['middle']
        if not mid:
            continue
        if t['is_ht']:
            ht_middle_types.add(mid)
            ht_middle_counts[mid] += 1
        else:
            classified_middle_types.add(mid)
            classified_middle_counts[mid] += 1

# ===================================================================
# T2: HT MIDDLE Incompatibility Graph Participation
# ===================================================================
print()
print("=== T2: HT MIDDLE Graph Participation ===")

ht_in_graph = ht_middle_types & graph_middles
ht_not_in_graph = ht_middle_types - graph_middles
cl_in_graph = classified_middle_types & graph_middles

print(f"HT MIDDLE types: {len(ht_middle_types)}")
print(f"  In C475 graph: {len(ht_in_graph)} ({len(ht_in_graph)/len(ht_middle_types)*100:.1f}%)")
print(f"  Not in graph: {len(ht_not_in_graph)} ({len(ht_not_in_graph)/len(ht_middle_types)*100:.1f}%)")
print()
print(f"Classified MIDDLE types: {len(classified_middle_types)}")
print(f"  In C475 graph: {len(cl_in_graph)} ({len(cl_in_graph)/len(classified_middle_types)*100:.1f}%)")

# Occurrence-weighted participation
ht_in_graph_occ = sum(ht_middle_counts[m] for m in ht_in_graph)
ht_total_occ = sum(ht_middle_counts.values())
print()
print(f"HT occurrence coverage by graph MIDDLEs: {ht_in_graph_occ}/{ht_total_occ} ({ht_in_graph_occ/ht_total_occ*100:.1f}%)")

# Degree analysis for HT MIDDLEs in graph
ht_graph_degree = {}
for mid in ht_in_graph:
    degree = sum(1 for pair in illegal_pairs if mid in pair)
    ht_graph_degree[mid] = degree

if ht_graph_degree:
    degrees = list(ht_graph_degree.values())
    print(f"HT MIDDLEs in graph - degree stats:")
    print(f"  Mean: {np.mean(degrees):.1f}")
    print(f"  Median: {np.median(degrees):.1f}")
    print(f"  Max: {max(degrees)}")
    top5 = sorted(ht_graph_degree.items(), key=lambda x: -x[1])[:5]
    for mid, deg in top5:
        print(f"    {mid}: degree={deg}, occ={ht_middle_counts[mid]}")

# T2 verdict
t2_participation = len(ht_in_graph) / len(ht_middle_types) * 100
if t2_participation > 50:
    t2_verdict = "EXTENSIVE"
    t2_detail = f"{t2_participation:.1f}% of HT MIDDLEs participate in C475 graph"
elif t2_participation > 10:
    t2_verdict = "PARTIAL"
    t2_detail = f"{t2_participation:.1f}% of HT MIDDLEs participate in C475 graph"
else:
    t2_verdict = "MINIMAL"
    t2_detail = f"Only {t2_participation:.1f}% of HT MIDDLEs in C475 graph"

print()
print(f"T2 VERDICT: {t2_verdict} - {t2_detail}")

# ===================================================================
# T3: HT Within-Line C475 Violation Rate
# ===================================================================
print()
print("=== T3: HT Within-Line C475 Violation Rate ===")

# For each line with both HT and classified tokens:
# Check cross-category MIDDLE pairs against illegal_pairs
cross_pairs_checked = 0
cross_violations = 0
# Also compute classified-classified baseline
cc_pairs_checked = 0
cc_violations = 0
# And HT-HT pairs
hh_pairs_checked = 0
hh_violations = 0

mixed_lines = 0
total_lines = len(line_tokens)

# Pre-sort tokens by category per line
for (folio, line), tokens in line_tokens.items():
    ht_mids = [t['middle'] for t in tokens if t['is_ht'] and t['middle']]
    cl_mids = [t['middle'] for t in tokens if not t['is_ht'] and t['middle']]

    if ht_mids and cl_mids:
        mixed_lines += 1

    # Cross-category pairs (HT x Classified)
    for hm in ht_mids:
        for cm in cl_mids:
            pair = frozenset([hm, cm])
            cross_pairs_checked += 1
            if pair in illegal_pairs:
                cross_violations += 1

    # Classified-classified pairs (baseline)
    for i in range(len(cl_mids)):
        for j in range(i + 1, len(cl_mids)):
            pair = frozenset([cl_mids[i], cl_mids[j]])
            cc_pairs_checked += 1
            if pair in illegal_pairs:
                cc_violations += 1

    # HT-HT pairs
    for i in range(len(ht_mids)):
        for j in range(i + 1, len(ht_mids)):
            pair = frozenset([ht_mids[i], ht_mids[j]])
            hh_pairs_checked += 1
            if pair in illegal_pairs:
                hh_violations += 1

cross_rate = cross_violations / cross_pairs_checked * 100 if cross_pairs_checked else 0
cc_rate = cc_violations / cc_pairs_checked * 100 if cc_pairs_checked else 0
hh_rate = hh_violations / hh_pairs_checked * 100 if hh_pairs_checked else 0

print(f"Lines with both HT and classified: {mixed_lines}/{total_lines}")
print()
print(f"Classified-Classified (baseline):")
print(f"  Pairs checked: {cc_pairs_checked}")
print(f"  Violations: {cc_violations}")
print(f"  Rate: {cc_rate:.4f}%")
print()
print(f"HT-Classified (cross-category):")
print(f"  Pairs checked: {cross_pairs_checked}")
print(f"  Violations: {cross_violations}")
print(f"  Rate: {cross_rate:.4f}%")
print()
print(f"HT-HT:")
print(f"  Pairs checked: {hh_pairs_checked}")
print(f"  Violations: {hh_violations}")
print(f"  Rate: {hh_rate:.4f}%")

# --- Permutation test: shuffle HT tokens across lines within folio ---
print()
print("=== T3 Permutation Test (1000 shuffles) ===")

# Group lines by folio
folio_lines = defaultdict(list)
for (folio, line), tokens in line_tokens.items():
    folio_lines[folio].append((line, tokens))

null_cross_violations = []

for p in range(1000):
    perm_violations = 0
    perm_pairs = 0

    for folio, lines_data in folio_lines.items():
        # Collect all HT middles in this folio
        all_ht_mids = []
        ht_positions = []  # (line_idx, token_idx_in_line)

        for line_idx, (line, tokens) in enumerate(lines_data):
            for tok_idx, t in enumerate(tokens):
                if t['is_ht'] and t['middle']:
                    all_ht_mids.append(t['middle'])
                    ht_positions.append((line_idx, tok_idx))

        if not all_ht_mids:
            continue

        # Shuffle HT middles across positions within folio
        shuffled = list(all_ht_mids)
        rng.shuffle(shuffled)

        # Rebuild line assignments
        shuffled_by_line = defaultdict(list)
        for i, (line_idx, _) in enumerate(ht_positions):
            shuffled_by_line[line_idx].append(shuffled[i])

        # Count violations with classified tokens
        for line_idx, (line, tokens) in enumerate(lines_data):
            cl_mids = [t['middle'] for t in tokens if not t['is_ht'] and t['middle']]
            sh_ht_mids = shuffled_by_line.get(line_idx, [])

            for hm in sh_ht_mids:
                for cm in cl_mids:
                    pair = frozenset([hm, cm])
                    perm_pairs += 1
                    if pair in illegal_pairs:
                        perm_violations += 1

    null_cross_violations.append(perm_violations)

null_mean = np.mean(null_cross_violations)
null_std = np.std(null_cross_violations)
z_score = (cross_violations - null_mean) / null_std if null_std > 0 else 0
p_fewer = np.mean([nv >= cross_violations for nv in null_cross_violations])
p_more = np.mean([nv <= cross_violations for nv in null_cross_violations])

print(f"Observed cross violations: {cross_violations}")
print(f"Null mean: {null_mean:.1f}")
print(f"Null std: {null_std:.2f}")
print(f"Z-score: {z_score:.2f}")
print(f"P(fewer violations than observed): {p_fewer:.4f}")
print(f"P(more violations than observed): {p_more:.4f}")

# T3 verdict
if cross_rate < 2.0:
    t3_verdict = "COMPLIANT"
    t3_detail = f"HT-classified violation rate {cross_rate:.4f}% < 2%"
elif cross_rate < 10.0:
    t3_verdict = "PARTIAL"
    t3_detail = f"HT-classified violation rate {cross_rate:.4f}% between 2-10%"
else:
    t3_verdict = "NON_COMPLIANT"
    t3_detail = f"HT-classified violation rate {cross_rate:.4f}% > 10%"

# Refine with permutation
if p_fewer < 0.01:
    t3_detail += " | Significantly fewer violations than random (HT avoids illegal pairs)"
elif p_more < 0.01:
    t3_detail += " | Significantly more violations than random (HT attracted to illegal pairs)"

print()
print(f"T3 VERDICT: {t3_verdict} - {t3_detail}")

# --- Save results ---
results = {
    "metadata": {
        "phase": "HT_RECONCILIATION",
        "script": "ht_c475_compliance.py",
        "tests": ["T2", "T3"],
        "n_illegal_pairs": len(illegal_pairs),
        "n_graph_middles": len(graph_middles)
    },
    "T2_incompatibility_coverage": {
        "ht_middle_types": len(ht_middle_types),
        "ht_in_graph": len(ht_in_graph),
        "ht_not_in_graph": len(ht_not_in_graph),
        "ht_participation_pct": round(t2_participation, 2),
        "ht_in_graph_occ": ht_in_graph_occ,
        "ht_total_occ": ht_total_occ,
        "ht_occ_coverage_pct": round(ht_in_graph_occ / ht_total_occ * 100, 2),
        "classified_middle_types": len(classified_middle_types),
        "classified_in_graph": len(cl_in_graph),
        "classified_participation_pct": round(len(cl_in_graph) / len(classified_middle_types) * 100, 2),
        "verdict": t2_verdict,
        "detail": t2_detail
    },
    "T3_violation_rate": {
        "mixed_lines": mixed_lines,
        "total_lines": total_lines,
        "cross_pairs_checked": cross_pairs_checked,
        "cross_violations": cross_violations,
        "cross_rate_pct": round(cross_rate, 6),
        "cc_pairs_checked": cc_pairs_checked,
        "cc_violations": cc_violations,
        "cc_rate_pct": round(cc_rate, 6),
        "hh_pairs_checked": hh_pairs_checked,
        "hh_violations": hh_violations,
        "hh_rate_pct": round(hh_rate, 6),
        "permutation": {
            "n_permutations": 1000,
            "observed": cross_violations,
            "null_mean": round(float(null_mean), 2),
            "null_std": round(float(null_std), 4),
            "z_score": round(float(z_score), 4),
            "p_fewer": round(float(p_fewer), 6),
            "p_more": round(float(p_more), 6)
        },
        "verdict": t3_verdict,
        "detail": t3_detail
    }
}

out_path = PROJECT_ROOT / 'phases' / 'HT_RECONCILIATION' / 'results' / 'ht_c475_compliance.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print()
print(f"Results saved to {out_path}")
