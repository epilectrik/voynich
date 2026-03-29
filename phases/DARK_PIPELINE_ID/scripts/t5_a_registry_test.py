"""
T5: A-Side Registry Test — Material Class vs Operational Sub-Type

Currier A is a NON_SEQUENTIAL_CATEGORICAL_REGISTRY (C240).
If dark MIDDLEs are material property classes, they should behave
like THINGS BEING CATALOGED in A. If operational sub-types, they
should behave like OPERATION MODIFIERS.

5 tests with pre-registered pass/fail thresholds:

T1: RI derivation rate
    Material class: dark RI derivation >= 0.5x bridge
    Operational sub-type: dark RI derivation < 0.2x bridge

T2: A-line positional profile
    Material class: same as bridge (cosine > 0.85)
    Operational sub-type: END-shifted (cosine < 0.70)

T3: RI co-occurrence on A lines containing dark MIDDLEs
    Material class: >= 1.2x RI density
    Operational sub-type: 0.9-1.1x (neutral)

T4: PREFIX independence in A
    Material class: V < 0.15 (independent)
    Operational sub-type: V > 0.25 (affiliated)

T5: Cross-record sharing pattern
    Material class: shared dark -> higher RI-extension similarity
    Operational sub-type: shared dark -> higher PREFIX similarity
"""

import sys, os, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
bridge_set = pp_middles - dp_set

# Load A tokens
all_a = [t for t in tx.currier_a() if t.word.strip() and not t.is_label]
all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
print(f"Currier A: {len(all_a)} tokens")
print(f"Currier B: {len(all_b)} tokens")
print(f"Dark MIDDLEs: {len(dp_set)}, Bridge MIDDLEs: {len(bridge_set)}, RI MIDDLEs: {len(ri_middles)}")

# ═══ PRECOMPUTE A-SIDE MIDDLE CLASSIFICATIONS ═══
a_mid_class = {}  # middle -> 'RI', 'DARK', 'BRIDGE', 'OTHER'
for t in all_a:
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    if mid in ri_middles:
        a_mid_class[mid] = 'RI'
    elif mid in dp_set:
        a_mid_class[mid] = 'DARK'
    elif mid in bridge_set:
        a_mid_class[mid] = 'BRIDGE'

# ═══ T1: RI DERIVATION RATE ═══
print("\n" + "=" * 100)
print("T1: RI DERIVATION RATE")
print("    Do dark MIDDLEs spawn RI extensions? (PP+extension = instance)")
print("    Material class: >= 0.5x bridge rate")
print("    Operational sub-type: < 0.2x bridge rate")
print("=" * 100)

# For each dark/bridge MIDDLE in A, check if any RI MIDDLE contains it as substring
dark_as_ri_base = 0
dark_tested = 0
bridge_as_ri_base = 0
bridge_tested = 0

# Dark MIDDLEs that appear in A
dark_in_a = set()
bridge_in_a = set()
for t in all_a:
    m = morph.extract(t.word)
    mid = m.middle
    if mid and mid in dp_set:
        dark_in_a.add(mid)
    elif mid and mid in bridge_set:
        bridge_in_a.add(mid)

for mid in dark_in_a:
    dark_tested += 1
    # Does any RI MIDDLE contain this dark MIDDLE as substring?
    for ri_mid in ri_middles:
        if mid in ri_mid and mid != ri_mid and len(ri_mid) > len(mid):
            dark_as_ri_base += 1
            break

for mid in bridge_in_a:
    bridge_tested += 1
    for ri_mid in ri_middles:
        if mid in ri_mid and mid != ri_mid and len(ri_mid) > len(mid):
            bridge_as_ri_base += 1
            break

dark_rate = dark_as_ri_base / dark_tested if dark_tested > 0 else 0
bridge_rate = bridge_as_ri_base / bridge_tested if bridge_tested > 0 else 0
ratio = dark_rate / bridge_rate if bridge_rate > 0 else 0

print(f"\n  Dark MIDDLEs in A: {dark_tested}")
print(f"  Dark serving as RI base: {dark_as_ri_base} ({100*dark_rate:.1f}%)")
print(f"  Bridge MIDDLEs in A: {bridge_tested}")
print(f"  Bridge serving as RI base: {bridge_as_ri_base} ({100*bridge_rate:.1f}%)")
print(f"  Ratio (dark/bridge): {ratio:.2f}x")

if ratio >= 0.5:
    print(f"  >> MATERIAL CLASS (ratio >= 0.5x)")
    t1_verdict = 'MATERIAL'
elif ratio < 0.2:
    print(f"  >> OPERATIONAL SUB-TYPE (ratio < 0.2x)")
    t1_verdict = 'OPERATIONAL'
else:
    print(f"  >> INCONCLUSIVE (0.2-0.5x)")
    t1_verdict = 'INCONCLUSIVE'


# ═══ T2: A-LINE POSITIONAL PROFILE ═══
print("\n" + "=" * 100)
print("T2: A-LINE POSITIONAL PROFILE")
print("    Where in A lines do dark vs bridge MIDDLEs appear?")
print("    Material class: same as bridge (cosine > 0.85)")
print("    Operational sub-type: END-shifted (cosine < 0.70)")
print("=" * 100)

# For each A token, compute its relative position in the line
folio_line_a = defaultdict(list)
for t in all_a:
    folio_line_a[(t.folio, t.line)].append(t)

dark_positions = []  # relative position [0, 1]
bridge_positions = []

for (folio, line), line_toks in folio_line_a.items():
    n = len(line_toks)
    if n < 2:
        continue
    for idx, t in enumerate(line_toks):
        m = morph.extract(t.word)
        mid = m.middle
        rel_pos = idx / (n - 1)
        if mid and mid in dp_set:
            dark_positions.append(rel_pos)
        elif mid and mid in bridge_set:
            bridge_positions.append(rel_pos)

# Bin into deciles for cosine comparison
def bin_positions(positions, n_bins=10):
    counts = [0] * n_bins
    for p in positions:
        b = min(int(p * n_bins), n_bins - 1)
        counts[b] += 1
    total = sum(counts)
    return [c / total if total > 0 else 0 for c in counts]

dark_bins = bin_positions(dark_positions)
bridge_bins = bin_positions(bridge_positions)

# Cosine similarity
dot = sum(d * b for d, b in zip(dark_bins, bridge_bins))
n_d = sum(d**2 for d in dark_bins) ** 0.5
n_b = sum(b**2 for b in bridge_bins) ** 0.5
cos = dot / (n_d * n_b) if n_d > 0 and n_b > 0 else 0

print(f"\n  Dark positions: n={len(dark_positions)}, mean={sum(dark_positions)/len(dark_positions):.3f}")
print(f"  Bridge positions: n={len(bridge_positions)}, mean={sum(bridge_positions)/len(bridge_positions):.3f}")
print(f"\n  Positional bins (deciles):")
print(f"    {'Bin':>6s} {'Dark%':>7s} {'Bridge%':>8s}")
for i in range(10):
    print(f"    {i*10:>3d}-{(i+1)*10:<3d} {100*dark_bins[i]:7.1f} {100*bridge_bins[i]:8.1f}")
print(f"\n  Cosine similarity: {cos:.3f}")

if cos > 0.85:
    print(f"  >> MATERIAL CLASS (cosine > 0.85 = same positional profile)")
    t2_verdict = 'MATERIAL'
elif cos < 0.70:
    print(f"  >> OPERATIONAL SUB-TYPE (cosine < 0.70 = different profile)")
    t2_verdict = 'OPERATIONAL'
else:
    print(f"  >> INCONCLUSIVE (0.70-0.85)")
    t2_verdict = 'INCONCLUSIVE'


# ═══ T3: RI CO-OCCURRENCE ON A LINES WITH DARK MIDDLEs ═══
print("\n" + "=" * 100)
print("T3: RI CO-OCCURRENCE ON A LINES WITH DARK MIDDLEs")
print("    Material class: >= 1.2x RI density")
print("    Operational sub-type: 0.9-1.1x (neutral)")
print("=" * 100)

lines_with_dark = set()
lines_without_dark = set()
line_ri_count = {}

for (folio, line), line_toks in folio_line_a.items():
    has_dark = False
    ri_count = 0
    for t in line_toks:
        m = morph.extract(t.word)
        mid = m.middle
        if mid and mid in dp_set:
            has_dark = True
        if mid and mid in ri_middles:
            ri_count += 1

    key = (folio, line)
    line_ri_count[key] = ri_count / len(line_toks) if line_toks else 0
    if has_dark:
        lines_with_dark.add(key)
    else:
        lines_without_dark.add(key)

dark_line_ri = [line_ri_count[k] for k in lines_with_dark if k in line_ri_count]
nondark_line_ri = [line_ri_count[k] for k in lines_without_dark if k in line_ri_count]

dark_ri_mean = sum(dark_line_ri) / len(dark_line_ri) if dark_line_ri else 0
nondark_ri_mean = sum(nondark_line_ri) / len(nondark_line_ri) if nondark_line_ri else 0
ri_ratio = dark_ri_mean / nondark_ri_mean if nondark_ri_mean > 0 else 0

print(f"\n  Lines with dark MIDDLEs: {len(lines_with_dark)}")
print(f"  Lines without: {len(lines_without_dark)}")
print(f"  RI density (dark lines): {dark_ri_mean:.3f}")
print(f"  RI density (non-dark lines): {nondark_ri_mean:.3f}")
print(f"  Ratio: {ri_ratio:.2f}x")

if ri_ratio >= 1.2:
    print(f"  >> MATERIAL CLASS (RI enriched on dark lines)")
    t3_verdict = 'MATERIAL'
elif 0.9 <= ri_ratio <= 1.1:
    print(f"  >> OPERATIONAL SUB-TYPE (RI neutral)")
    t3_verdict = 'OPERATIONAL'
else:
    print(f"  >> INCONCLUSIVE (ratio={ri_ratio:.2f})")
    t3_verdict = 'INCONCLUSIVE'


# ═══ T4: PREFIX INDEPENDENCE IN A ═══
print("\n" + "=" * 100)
print("T4: PREFIX INDEPENDENCE IN A")
print("    Material class: V < 0.15 (PREFIX-independent)")
print("    Operational sub-type: V > 0.25 (PREFIX-affiliated)")
print("=" * 100)

# Cramers V between dark MIDDLE identity and PREFIX in A
dark_mid_pre = defaultdict(Counter)
for t in all_a:
    m = morph.extract(t.word)
    mid = m.middle
    if mid and mid in dp_set:
        pre = m.prefix or 'BARE'
        dark_mid_pre[mid][pre] += 1

# Only use dark MIDDLEs with 5+ A tokens
qualifying = {mid: ct for mid, ct in dark_mid_pre.items() if sum(ct.values()) >= 5}

if qualifying:
    # Build contingency table
    all_pres = set()
    for ct in qualifying.values():
        all_pres.update(ct.keys())
    all_pres = sorted(all_pres)
    all_mids = sorted(qualifying.keys())

    # Chi-squared
    n_total = sum(sum(ct.values()) for ct in qualifying.values())
    row_totals = {mid: sum(qualifying[mid].values()) for mid in all_mids}
    col_totals = {pre: sum(qualifying[mid].get(pre, 0) for mid in all_mids) for pre in all_pres}

    chi2 = 0
    for mid in all_mids:
        for pre in all_pres:
            observed = qualifying[mid].get(pre, 0)
            expected = row_totals[mid] * col_totals[pre] / n_total if n_total > 0 else 0
            if expected > 0:
                chi2 += (observed - expected)**2 / expected

    k = min(len(all_mids), len(all_pres))
    v = (chi2 / (n_total * (k - 1))) ** 0.5 if n_total > 0 and k > 1 else 0

    print(f"\n  Qualifying dark MIDDLEs in A (5+ tokens): {len(qualifying)}")
    print(f"  Total tokens: {n_total}")
    print(f"  Unique PREFIXes: {len(all_pres)}")
    print(f"  Chi-squared: {chi2:.1f}")
    print(f"  Cramers V: {v:.3f}")

    if v < 0.15:
        print(f"  >> MATERIAL CLASS (PREFIX-independent, V < 0.15)")
        t4_verdict = 'MATERIAL'
    elif v > 0.25:
        print(f"  >> OPERATIONAL SUB-TYPE (PREFIX-affiliated, V > 0.25)")
        t4_verdict = 'OPERATIONAL'
    else:
        print(f"  >> INCONCLUSIVE (V between 0.15-0.25)")
        t4_verdict = 'INCONCLUSIVE'
else:
    print(f"\n  No qualifying dark MIDDLEs in A with 5+ tokens")
    t4_verdict = 'NO_DATA'


# ═══ T5: CROSS-RECORD SHARING ═══
print("\n" + "=" * 100)
print("T5: CROSS-RECORD SHARING PATTERN")
print("    A records sharing dark MIDDLEs: do they share RI extensions")
print("    (material class) or PREFIX profiles (operational sub-type)?")
print("=" * 100)

# Build per-folio profiles in A
folio_dark_a = defaultdict(set)
folio_bridge_a = defaultdict(set)
folio_ri_a = defaultdict(set)
folio_pre_a = defaultdict(Counter)

for t in all_a:
    m = morph.extract(t.word)
    mid = m.middle
    pre = m.prefix or 'BARE'
    if mid:
        if mid in dp_set:
            folio_dark_a[t.folio].add(mid)
        elif mid in bridge_set:
            folio_bridge_a[t.folio].add(mid)
        elif mid in ri_middles:
            folio_ri_a[t.folio].add(mid)
    folio_pre_a[t.folio][pre] += 1

a_folios = sorted(set(t.folio for t in all_a))

def jaccard(s1, s2):
    if not s1 and not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0

def cosine_counters(c1, c2):
    keys = set(c1.keys()) | set(c2.keys())
    dot = sum(c1.get(k, 0) * c2.get(k, 0) for k in keys)
    n1 = sum(v**2 for v in c1.values()) ** 0.5
    n2 = sum(v**2 for v in c2.values()) ** 0.5
    return dot / (n1 * n2) if n1 > 0 and n2 > 0 else 0.0

# For folio pairs that share dark MIDDLEs vs pairs that don't
import random
random.seed(42)

sharing_pairs_ri = []
sharing_pairs_pre = []
nonsharing_pairs_ri = []
nonsharing_pairs_pre = []

pairs_tested = 0
for i in range(len(a_folios)):
    for j in range(i+1, len(a_folios)):
        f1, f2 = a_folios[i], a_folios[j]
        if not folio_dark_a[f1] or not folio_dark_a[f2]:
            continue
        if not folio_ri_a[f1] or not folio_ri_a[f2]:
            continue

        dark_shared = len(folio_dark_a[f1] & folio_dark_a[f2]) > 0
        ri_jac = jaccard(folio_ri_a[f1], folio_ri_a[f2])
        pre_cos = cosine_counters(folio_pre_a[f1], folio_pre_a[f2])

        if dark_shared:
            sharing_pairs_ri.append(ri_jac)
            sharing_pairs_pre.append(pre_cos)
        else:
            nonsharing_pairs_ri.append(ri_jac)
            nonsharing_pairs_pre.append(pre_cos)
        pairs_tested += 1

if sharing_pairs_ri and nonsharing_pairs_ri:
    share_ri_mean = sum(sharing_pairs_ri) / len(sharing_pairs_ri)
    nonshare_ri_mean = sum(nonsharing_pairs_ri) / len(nonsharing_pairs_ri)
    share_pre_mean = sum(sharing_pairs_pre) / len(sharing_pairs_pre)
    nonshare_pre_mean = sum(nonsharing_pairs_pre) / len(nonsharing_pairs_pre)

    ri_lift = share_ri_mean / nonshare_ri_mean if nonshare_ri_mean > 0 else 0
    pre_lift = share_pre_mean / nonshare_pre_mean if nonshare_pre_mean > 0 else 0

    print(f"\n  Pairs tested: {pairs_tested}")
    print(f"  Dark-sharing pairs: {len(sharing_pairs_ri)}")
    print(f"  Non-sharing pairs: {len(nonsharing_pairs_ri)}")
    print(f"\n  RI Jaccard:")
    print(f"    Dark-sharing: {share_ri_mean:.4f}")
    print(f"    Non-sharing:  {nonshare_ri_mean:.4f}")
    print(f"    Lift: {ri_lift:.2f}x")
    print(f"\n  PREFIX cosine:")
    print(f"    Dark-sharing: {share_pre_mean:.4f}")
    print(f"    Non-sharing:  {nonshare_pre_mean:.4f}")
    print(f"    Lift: {pre_lift:.2f}x")

    if ri_lift > pre_lift and ri_lift > 1.1:
        print(f"\n  >> MATERIAL CLASS (dark sharing predicts RI similarity more)")
        t5_verdict = 'MATERIAL'
    elif pre_lift > ri_lift and pre_lift > 1.1:
        print(f"\n  >> OPERATIONAL SUB-TYPE (dark sharing predicts PREFIX similarity more)")
        t5_verdict = 'OPERATIONAL'
    else:
        print(f"\n  >> INCONCLUSIVE")
        t5_verdict = 'INCONCLUSIVE'
else:
    print(f"\n  Insufficient data for cross-record test")
    t5_verdict = 'NO_DATA'


# ═══ SCORECARD ═══
print("\n\n" + "=" * 100)
print("SCORECARD")
print("=" * 100)

verdicts = {
    'T1 (RI derivation)': t1_verdict,
    'T2 (A-line position)': t2_verdict,
    'T3 (RI co-occurrence)': t3_verdict,
    'T4 (PREFIX independence)': t4_verdict,
    'T5 (cross-record sharing)': t5_verdict,
}

mat_count = sum(1 for v in verdicts.values() if v == 'MATERIAL')
ops_count = sum(1 for v in verdicts.values() if v == 'OPERATIONAL')
inc_count = sum(1 for v in verdicts.values() if v in ('INCONCLUSIVE', 'NO_DATA'))

print(f"\n  {'Test':>30s} {'Verdict':>15s}")
print(f"  {'-'*50}")
for test, verdict in verdicts.items():
    print(f"  {test:>30s} {verdict:>15s}")

print(f"\n  MATERIAL CLASS:      {mat_count}/5")
print(f"  OPERATIONAL SUB-TYPE: {ops_count}/5")
print(f"  INCONCLUSIVE:        {inc_count}/5")

if mat_count >= 4:
    print(f"\n  OVERALL: MATERIAL CLASS SUPPORTED")
elif ops_count >= 4:
    print(f"\n  OVERALL: OPERATIONAL SUB-TYPE SUPPORTED")
elif mat_count >= 3:
    print(f"\n  OVERALL: MATERIAL CLASS LEANING (not decisive)")
elif ops_count >= 3:
    print(f"\n  OVERALL: OPERATIONAL SUB-TYPE LEANING (not decisive)")
else:
    print(f"\n  OVERALL: INCONCLUSIVE — interpretations may not be separable at this resolution")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
