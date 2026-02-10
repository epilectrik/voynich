"""
07_fl_in_currier_a.py

Test whether FL MIDDLEs in Currier A records respect the FL positional gradient
established in Currier B (C777).

Core question: If A records document material transformations, do FL MIDDLEs
within A records show INITIAL→EARLY→MEDIAL→LATE→TERMINAL ordering?

This would mean A records literally map the material's journey through FL state space.
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# FL MIDDLE stage assignments from C777
FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299),
    'i':  ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r':  ('MEDIAL', 0.507),
    'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606),
    'l':  ('LATE', 0.618),
    'ol': ('LATE', 0.643),
    'o':  ('FINAL', 0.751),
    'ly': ('FINAL', 0.785),
    'am': ('FINAL', 0.802),
    'm':  ('TERMINAL', 0.861),
    'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913),
    'y':  ('TERMINAL', 0.942),
}

STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}

tx = Transcript()
morph = Morphology()

# ============================================================
# 1. Collect FL MIDDLEs in Currier A with position info
# ============================================================

# Group tokens by paragraph using par_initial flag
a_paragraphs = defaultdict(list)
current_folio = None
current_para_id = 0

for t in tx.currier_a():
    if t.folio != current_folio:
        current_folio = t.folio
        current_para_id = 0
    if t.par_initial:
        current_para_id += 1
    key = (t.folio, current_para_id)
    a_paragraphs[key].append(t)

print(f"Total A paragraphs: {len(a_paragraphs)}")

# For each paragraph, extract FL tokens with normalized position
fl_in_a = []
fl_by_paragraph = defaultdict(list)
paragraph_fl_sequences = []  # (paragraph_key, [(position, fl_middle, stage, b_position)])

for para_key, tokens in a_paragraphs.items():
    if len(tokens) < 2:
        continue

    # Assign normalized position within paragraph
    max_idx = len(tokens) - 1
    if max_idx == 0:
        continue

    fl_seq = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            norm_pos = idx / max_idx
            stage, b_pos = FL_STAGE_MAP[m.middle]
            fl_in_a.append({
                'word': t.word,
                'middle': m.middle,
                'stage': stage,
                'b_position': b_pos,  # Expected position from B
                'a_position': norm_pos,  # Actual position in A record
                'folio': t.folio,
                'paragraph': para_key[1],
                'line': t.line,
            })
            fl_seq.append((norm_pos, m.middle, stage, b_pos))
            fl_by_paragraph[para_key].append((norm_pos, m.middle, stage, b_pos))

    if len(fl_seq) >= 2:
        paragraph_fl_sequences.append((para_key, fl_seq))

print(f"FL tokens in A: {len(fl_in_a)}")
print(f"Paragraphs with 2+ FL tokens: {len(paragraph_fl_sequences)}")

# ============================================================
# 2. Global: FL MIDDLE mean position in A vs B
# ============================================================

print("\n" + "=" * 60)
print("FL MIDDLE Positions: A vs B")
print("=" * 60)

a_positions_by_middle = defaultdict(list)
for entry in fl_in_a:
    a_positions_by_middle[entry['middle']].append(entry['a_position'])

print(f"\n{'MIDDLE':>6} | {'A_pos':>6} | {'B_pos':>6} | {'N_A':>5} | {'Stage':>10} | {'Match':>5}")
print("-" * 60)

a_means = {}
position_pairs = []  # (b_pos, a_mean_pos) for correlation

for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    stage, b_pos = FL_STAGE_MAP[mid]
    a_positions = a_positions_by_middle.get(mid, [])
    if a_positions:
        a_mean = statistics.mean(a_positions)
        a_means[mid] = a_mean
        position_pairs.append((b_pos, a_mean))
        match = "YES" if abs(a_mean - b_pos) < 0.15 else "~" if abs(a_mean - b_pos) < 0.25 else "NO"
        print(f"{mid:>6} | {a_mean:.3f} | {b_pos:.3f} | {len(a_positions):>5} | {stage:>10} | {match:>5}")
    else:
        print(f"{mid:>6} |   N/A | {b_pos:.3f} |     0 | {stage:>10} |   N/A")

# Spearman correlation between A and B positions
if len(position_pairs) >= 5:
    from scipy import stats
    b_positions = [p[0] for p in position_pairs]
    a_mean_positions = [p[1] for p in position_pairs]
    rho, p_value = stats.spearmanr(b_positions, a_mean_positions)
    print(f"\nSpearman correlation (A position vs B position): rho={rho:.3f}, p={p_value:.4f}")

    # Also Pearson
    r_pearson, p_pearson = stats.pearsonr(b_positions, a_mean_positions)
    print(f"Pearson correlation: r={r_pearson:.3f}, p={p_pearson:.4f}")
else:
    rho, p_value = None, None
    r_pearson, p_pearson = None, None

# ============================================================
# 3. Within-paragraph FL ordering concordance
# ============================================================

print("\n" + "=" * 60)
print("Within-Paragraph FL Ordering")
print("=" * 60)

concordant = 0
discordant = 0
tied = 0
total_pairs = 0

for para_key, fl_seq in paragraph_fl_sequences:
    # Check all pairs: is the B-expected ordering respected in A position?
    for i in range(len(fl_seq)):
        for j in range(i+1, len(fl_seq)):
            a_pos_i, mid_i, stage_i, b_pos_i = fl_seq[i]
            a_pos_j, mid_j, stage_j, b_pos_j = fl_seq[j]

            # a_pos_i < a_pos_j by construction (sequential)
            # Question: does b_pos_i < b_pos_j? (concordant)
            total_pairs += 1
            if b_pos_i < b_pos_j:
                concordant += 1
            elif b_pos_i > b_pos_j:
                discordant += 1
            else:
                tied += 1

if total_pairs > 0:
    concordance_rate = concordant / total_pairs
    kendall_tau = (concordant - discordant) / total_pairs
    print(f"Total FL token pairs within paragraphs: {total_pairs}")
    print(f"Concordant (A order matches B expected): {concordant} ({concordant/total_pairs*100:.1f}%)")
    print(f"Discordant: {discordant} ({discordant/total_pairs*100:.1f}%)")
    print(f"Tied: {tied} ({tied/total_pairs*100:.1f}%)")
    print(f"Kendall's tau: {kendall_tau:.3f}")
    print(f"\nIf random, expect ~50% concordant. If A respects FL order, expect >>50%.")
else:
    concordance_rate = None
    kendall_tau = None
    print("Insufficient FL pairs for ordering test")

# ============================================================
# 4. FL stage distribution by paragraph position
# ============================================================

print("\n" + "=" * 60)
print("FL Stage by Position in A Record")
print("=" * 60)

# Bin positions into thirds
position_bins = {'FIRST_THIRD': [], 'MIDDLE_THIRD': [], 'LAST_THIRD': []}
for entry in fl_in_a:
    if entry['a_position'] < 0.333:
        position_bins['FIRST_THIRD'].append(entry)
    elif entry['a_position'] < 0.667:
        position_bins['MIDDLE_THIRD'].append(entry)
    else:
        position_bins['LAST_THIRD'].append(entry)

for bin_name in ['FIRST_THIRD', 'MIDDLE_THIRD', 'LAST_THIRD']:
    entries = position_bins[bin_name]
    stage_counts = Counter(e['stage'] for e in entries)
    total = len(entries)
    print(f"\n{bin_name} ({total} tokens):")
    for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
        count = stage_counts.get(stage, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = '#' * int(pct / 2)
        print(f"  {stage:>10}: {count:>4} ({pct:>5.1f}%) {bar}")

# Chi-square test: stage distribution vs position bin
from scipy.stats import chi2_contingency
stage_list = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']
contingency = []
for bin_name in ['FIRST_THIRD', 'MIDDLE_THIRD', 'LAST_THIRD']:
    entries = position_bins[bin_name]
    row = [sum(1 for e in entries if e['stage'] == s) for s in stage_list]
    contingency.append(row)

chi2, p_chi2, dof, expected = chi2_contingency(contingency)
print(f"\nChi-square test (stage × position): chi2={chi2:.2f}, p={p_chi2:.4f}, dof={dof}")

# ============================================================
# 5. Compare WITH-RI vs WITHOUT-RI paragraphs
# ============================================================

print("\n" + "=" * 60)
print("FL in WITH-RI vs WITHOUT-RI Paragraphs")
print("=" * 60)

# Detect RI presence: first-line tokens that are RI (A-only MIDDLEs)
b_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

with_ri_fl_stages = []
without_ri_fl_stages = []

for para_key, tokens in a_paragraphs.items():
    if len(tokens) < 2:
        continue

    # Check first line for RI
    first_line = tokens[0].line
    first_line_tokens = [t for t in tokens if t.line == first_line]
    has_ri = False
    for t in first_line_tokens:
        m = morph.extract(t.word)
        if m and m.middle and m.middle not in b_middles:
            has_ri = True
            break

    # Collect FL stages
    for t in tokens:
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            stage, b_pos = FL_STAGE_MAP[m.middle]
            if has_ri:
                with_ri_fl_stages.append(stage)
            else:
                without_ri_fl_stages.append(stage)

print(f"WITH-RI FL tokens: {len(with_ri_fl_stages)}")
print(f"WITHOUT-RI FL tokens: {len(without_ri_fl_stages)}")

for label, stages in [("WITH-RI", with_ri_fl_stages), ("WITHOUT-RI", without_ri_fl_stages)]:
    total = len(stages)
    if total == 0:
        continue
    print(f"\n{label}:")
    stage_counts = Counter(stages)
    for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
        count = stage_counts.get(stage, 0)
        pct = count / total * 100
        print(f"  {stage:>10}: {count:>4} ({pct:>5.1f}%)")

# ============================================================
# 6. FL MIDDLE frequency comparison: A vs B
# ============================================================

print("\n" + "=" * 60)
print("FL MIDDLE Frequency: A vs B")
print("=" * 60)

b_fl_counts = Counter()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle and m.middle in FL_STAGE_MAP:
        b_fl_counts[m.middle] += 1

a_fl_counts = Counter()
for entry in fl_in_a:
    a_fl_counts[entry['middle']] += 1

total_a_fl = sum(a_fl_counts.values())
total_b_fl = sum(b_fl_counts.values())

print(f"\n{'MIDDLE':>6} | {'A_count':>7} | {'A_pct':>6} | {'B_count':>7} | {'B_pct':>6} | {'A/B ratio':>9} | {'Stage':>10}")
print("-" * 80)

enrichment_data = []
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    stage, _ = FL_STAGE_MAP[mid]
    a_c = a_fl_counts.get(mid, 0)
    b_c = b_fl_counts.get(mid, 0)
    a_pct = a_c / total_a_fl * 100 if total_a_fl > 0 else 0
    b_pct = b_c / total_b_fl * 100 if total_b_fl > 0 else 0
    ratio = (a_pct / b_pct) if b_pct > 0 else 0
    enrichment_data.append({'middle': mid, 'stage': stage, 'a_count': a_c, 'b_count': b_c, 'a_pct': round(a_pct, 1), 'b_pct': round(b_pct, 1), 'ratio': round(ratio, 2)})
    print(f"{mid:>6} | {a_c:>7} | {a_pct:>5.1f}% | {b_c:>7} | {b_pct:>5.1f}% | {ratio:>8.2f}x | {stage:>10}")

# ============================================================
# Write results
# ============================================================

result = {
    "total_a_paragraphs": len(a_paragraphs),
    "fl_tokens_in_a": len(fl_in_a),
    "paragraphs_with_2plus_fl": len(paragraph_fl_sequences),
    "a_vs_b_position_correlation": {
        "spearman_rho": round(rho, 4) if rho is not None else None,
        "spearman_p": round(p_value, 6) if p_value is not None else None,
        "pearson_r": round(r_pearson, 4) if r_pearson is not None else None,
        "pearson_p": round(p_pearson, 6) if p_pearson is not None else None,
    },
    "within_paragraph_ordering": {
        "total_pairs": total_pairs,
        "concordant": concordant,
        "discordant": discordant,
        "tied": tied,
        "concordance_rate": round(concordance_rate, 4) if concordance_rate is not None else None,
        "kendall_tau": round(kendall_tau, 4) if kendall_tau is not None else None,
    },
    "stage_by_position_chi2": {
        "chi2": round(chi2, 2),
        "p_value": round(p_chi2, 6),
        "dof": dof,
    },
    "fl_middle_a_positions": {
        mid: {
            "a_mean_pos": round(statistics.mean(a_positions_by_middle[mid]), 3),
            "b_expected_pos": FL_STAGE_MAP[mid][1],
            "n": len(a_positions_by_middle[mid]),
            "stage": FL_STAGE_MAP[mid][0],
        }
        for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1])
        if mid in a_positions_by_middle
    },
    "with_ri_fl_stages": dict(Counter(with_ri_fl_stages)),
    "without_ri_fl_stages": dict(Counter(without_ri_fl_stages)),
    "fl_frequency_comparison": enrichment_data,
}

out_path = Path(__file__).resolve().parents[1] / "results" / "07_fl_in_currier_a.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
