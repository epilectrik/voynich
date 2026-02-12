"""Compare three folio->regime mappings to quantify disagreement."""
import json
from collections import Counter, defaultdict

# ── Source A (median-split) ──
source_a_raw = {
    "REGIME_3": ["f103r","f104v","f114v","f115r","f116r","f31r","f33r","f33v","f39r","f46r","f77r","f81r","f83v","f86v4","f95r1","f95r2"],
    "REGIME_1": ["f103v","f104r","f106r","f106v","f107v","f108r","f108v","f111r","f111v","f112r","f112v","f113r","f114r","f66r","f75r","f75v","f76r","f76v","f77v","f78r","f78v","f79r","f79v","f80r","f80v","f81v","f82r","f82v","f83r","f84r","f84v"],
    "REGIME_2": ["f105r","f105v","f107r","f113v","f115v","f26v","f48r","f48v","f85v2","f86v3","f86v5"],
    "REGIME_4": ["f26r","f31v","f34r","f34v","f39v","f40r","f40v","f41r","f41v","f43r","f43v","f46v","f50r","f50v","f55r","f55v","f57r","f66v","f85r1","f85r2","f86v6","f94r","f94v","f95v1","f95v2"]
}

# ── Source B (alternative approach) ──
source_b_raw = {
    "REGIME_1": ["f39r","f41r","f66r","f66v","f75r","f75v","f76r","f76v","f77r","f77v","f79r","f80r","f80v","f82r","f82v","f83r","f83v","f84r","f95v1","f106v","f111v","f115r","f115v"],
    "REGIME_2": ["f26v","f31v","f33v","f39v","f40r","f40v","f48v","f50v","f55r","f81r","f85r1","f85r2","f86v4","f86v5","f86v3","f95v2","f103v","f104v","f105r","f106r","f112v","f113r","f113v","f116r"],
    "REGIME_3": ["f26r","f34r","f78v","f81v","f84v","f94r","f95r2","f114r"],
    "REGIME_4": ["f31r","f33r","f34v","f41v","f43r","f43v","f46r","f46v","f48r","f50r","f55v","f57r","f78r","f79v","f86v6","f94v","f95r1","f103r","f104r","f105v","f107r","f107v","f108r","f108v","f111r","f112r","f114v"]
}

# ── Source C (GMM k=4, authoritative) ──
with open(r"C:\git\voynich\data\regime_folio_mapping.json") as f:
    source_c_json = json.load(f)

# Flatten all sources to {folio: regime}
def flatten(raw):
    out = {}
    for regime, folios in raw.items():
        for f in folios:
            out[f] = regime
    return out

A = flatten(source_a_raw)
B = flatten(source_b_raw)
C = {folio: info["regime"] for folio, info in source_c_json["regime_assignments"].items()}
C_prob = {folio: info["probability"] for folio, info in source_c_json["regime_assignments"].items()}

# ── Regime number extraction for distance ──
def regime_num(r):
    return int(r.split("_")[1])

# ============================================================
# 1. SIZE DISTRIBUTIONS
# ============================================================
print("=" * 70)
print("1. SIZE DISTRIBUTIONS (folios per regime)")
print("=" * 70)

for name, src in [("A (median-split)", A), ("B (alternative)", B), ("C (GMM k=4)", C)]:
    counts = Counter(src.values())
    total = sum(counts.values())
    print(f"\n  Source {name}  (total: {total})")
    for r in sorted(counts):
        print(f"    {r}: {counts[r]:3d}  ({counts[r]/total*100:5.1f}%)")

# ============================================================
# 2. A vs B AGREEMENT
# ============================================================
print("\n" + "=" * 70)
print("2. AGREEMENT: A vs B")
print("=" * 70)

common_ab = set(A) & set(B)
only_a = set(A) - set(B)
only_b = set(B) - set(A)
print(f"\n  Folios in A: {len(A)}, in B: {len(B)}, in both: {len(common_ab)}")
if only_a:
    print(f"  Only in A: {sorted(only_a)}")
if only_b:
    print(f"  Only in B: {sorted(only_b)}")

agree_ab = sum(1 for f in common_ab if A[f] == B[f])
disagree_ab = len(common_ab) - agree_ab
print(f"\n  Exact matches: {agree_ab}/{len(common_ab)} ({agree_ab/len(common_ab)*100:.1f}%)")
print(f"  Disagreements: {disagree_ab}/{len(common_ab)} ({disagree_ab/len(common_ab)*100:.1f}%)")

# Disagreement patterns
patterns_ab = Counter()
for f in common_ab:
    if A[f] != B[f]:
        patterns_ab[(A[f], B[f])] += 1

print(f"\n  Top disagreement patterns (A_regime -> B_regime):")
for (a_r, b_r), cnt in patterns_ab.most_common(15):
    print(f"    {a_r} -> {b_r}: {cnt} folios")

# ============================================================
# 3. A vs C, B vs C AGREEMENT
# ============================================================
for label_old, old_src, label_new in [("A", A, "C"), ("B", B, "C")]:
    print("\n" + "=" * 70)
    print(f"3. AGREEMENT: {label_old} vs {label_new}")
    print("=" * 70)

    common = set(old_src) & set(C)
    only_old = set(old_src) - set(C)
    only_new = set(C) - set(old_src)
    print(f"\n  Folios in {label_old}: {len(old_src)}, in {label_new}: {len(C)}, in both: {len(common)}")
    if only_old:
        print(f"  Only in {label_old}: {sorted(only_old)}")
    if only_new:
        print(f"  Only in {label_new}: {sorted(only_new)}")

    agree = sum(1 for f in common if old_src[f] == C[f])
    disagree = len(common) - agree
    print(f"\n  Exact matches: {agree}/{len(common)} ({agree/len(common)*100:.1f}%)")
    print(f"  Disagreements: {disagree}/{len(common)} ({disagree/len(common)*100:.1f}%)")

    patterns = Counter()
    for f in common:
        if old_src[f] != C[f]:
            patterns[(old_src[f], C[f])] += 1

    print(f"\n  Top disagreement patterns ({label_old}_regime -> {label_new}_regime):")
    for (o_r, n_r), cnt in patterns.most_common(15):
        print(f"    {o_r} -> {n_r}: {cnt} folios")

# ============================================================
# 4. CONFUSION MATRICES
# ============================================================
print("\n" + "=" * 70)
print("4. CONFUSION MATRICES")
print("=" * 70)

regimes = ["REGIME_1", "REGIME_2", "REGIME_3", "REGIME_4"]

def print_confusion(src1, src2, label1, label2):
    common = set(src1) & set(src2)
    matrix = defaultdict(lambda: defaultdict(int))
    for f in common:
        matrix[src1[f]][src2[f]] += 1

    # Header
    header = f"{'':>12s}" + "".join(f"{r:>12s}" for r in regimes) + f"{'TOTAL':>8s}"
    print(f"\n  {label1} (rows) vs {label2} (cols):")
    print(f"  {header}")
    print(f"  {'-'*len(header)}")
    for r1 in regimes:
        row_total = sum(matrix[r1][r2] for r2 in regimes)
        row = f"{r1:>12s}" + "".join(f"{matrix[r1][r2]:>12d}" for r2 in regimes) + f"{row_total:>8d}"
        print(f"  {row}")
    col_totals = f"{'TOTAL':>12s}" + "".join(f"{sum(matrix[r1][r2] for r1 in regimes):>12d}" for r2 in regimes)
    print(f"  {col_totals}")

    # Diagonal accuracy
    on_diag = sum(matrix[r][r] for r in regimes)
    total = sum(matrix[r1][r2] for r1 in regimes for r2 in regimes)
    print(f"\n  Diagonal (agreement): {on_diag}/{total} = {on_diag/total*100:.1f}%")

    # Most confused pairs
    off_diag = []
    for r1 in regimes:
        for r2 in regimes:
            if r1 != r2 and matrix[r1][r2] > 0:
                off_diag.append((matrix[r1][r2], r1, r2))
    off_diag.sort(reverse=True)
    if off_diag:
        print(f"  Most confused pairs:")
        for cnt, r1, r2 in off_diag[:8]:
            print(f"    {r1} mistaken for {r2}: {cnt}")

print_confusion(A, B, "A", "B")
print_confusion(A, C, "A", "C")
print_confusion(B, C, "B", "C")

# ============================================================
# 5. EGREGIOUS CASES
# ============================================================
print("\n" + "=" * 70)
print("5. EGREGIOUS CASES")
print("=" * 70)

# 5a: A vs B with regime distance >= 3
print("\n  5a. A vs B disagreement by 3+ regime steps:")
all_folios = sorted(set(A) | set(B) | set(C))
found_any = False
for f in sorted(set(A) & set(B)):
    if A[f] != B[f]:
        dist = abs(regime_num(A[f]) - regime_num(B[f]))
        if dist >= 3:
            c_val = C.get(f, "N/A")
            found_any = True
            print(f"    {f}: A={A[f]}, B={B[f]} (distance={dist}), C={c_val}")
if not found_any:
    print("    None found with distance >= 3")

# Also check A vs C and B vs C for distance >= 3
print("\n  5b. A vs C disagreement by 3+ regime steps:")
found_any = False
for f in sorted(set(A) & set(C)):
    if A[f] != C[f]:
        dist = abs(regime_num(A[f]) - regime_num(C[f]))
        if dist >= 3:
            b_val = B.get(f, "N/A")
            found_any = True
            print(f"    {f}: A={A[f]}, C={C[f]} (distance={dist}), B={b_val}")
if not found_any:
    print("    None found with distance >= 3")

print("\n  5c. B vs C disagreement by 3+ regime steps:")
found_any = False
for f in sorted(set(B) & set(C)):
    if B[f] != C[f]:
        dist = abs(regime_num(B[f]) - regime_num(C[f]))
        if dist >= 3:
            a_val = A.get(f, "N/A")
            found_any = True
            print(f"    {f}: B={B[f]}, C={C[f]} (distance={dist}), A={a_val}")
if not found_any:
    print("    None found with distance >= 3")

# 5d: All three disagree
print("\n  5d. Folios where ALL THREE sources disagree (three different regimes):")
common_abc = set(A) & set(B) & set(C)
triple_disagree = []
for f in sorted(common_abc):
    vals = {A[f], B[f], C[f]}
    if len(vals) == 3:
        triple_disagree.append(f)
        prob = C_prob.get(f, "?")
        print(f"    {f}: A={A[f]}, B={B[f]}, C={C[f]}  (C prob={prob})")
print(f"\n  Total triple-disagreements: {len(triple_disagree)}/{len(common_abc)} "
      f"({len(triple_disagree)/len(common_abc)*100:.1f}%)")

# Also: all three completely agree
triple_agree = sum(1 for f in common_abc if A[f] == B[f] == C[f])
print(f"  Total triple-agreements: {triple_agree}/{len(common_abc)} "
      f"({triple_agree/len(common_abc)*100:.1f}%)")

# ============================================================
# 6. OVERALL VERDICT
# ============================================================
print("\n" + "=" * 70)
print("6. OVERALL VERDICT")
print("=" * 70)

# Summary stats
common_ab = set(A) & set(B)
common_ac = set(A) & set(C)
common_bc = set(B) & set(C)
common_abc_set = set(A) & set(B) & set(C)

agree_ab = sum(1 for f in common_ab if A[f] == B[f])
agree_ac = sum(1 for f in common_ac if A[f] == C[f])
agree_bc = sum(1 for f in common_bc if B[f] == C[f])

print(f"""
  Pairwise agreement rates:
    A vs B: {agree_ab}/{len(common_ab)} = {agree_ab/len(common_ab)*100:.1f}%
    A vs C: {agree_ac}/{len(common_ac)} = {agree_ac/len(common_ac)*100:.1f}%
    B vs C: {agree_bc}/{len(common_bc)} = {agree_bc/len(common_bc)*100:.1f}%

  Triple agreement (A=B=C): {triple_agree}/{len(common_abc_set)} = {triple_agree/len(common_abc_set)*100:.1f}%
  Triple disagreement (all different): {len(triple_disagree)}/{len(common_abc_set)} = {len(triple_disagree)/len(common_abc_set)*100:.1f}%
""")

# Mean absolute regime distance
def mean_distance(s1, s2):
    common = set(s1) & set(s2)
    dists = [abs(regime_num(s1[f]) - regime_num(s2[f])) for f in common]
    return sum(dists) / len(dists) if dists else 0

print(f"  Mean absolute regime distance:")
print(f"    A vs B: {mean_distance(A, B):.2f}")
print(f"    A vs C: {mean_distance(A, C):.2f}")
print(f"    B vs C: {mean_distance(B, C):.2f}")

# Cohen's Kappa (simple version)
def cohens_kappa(s1, s2):
    common = sorted(set(s1) & set(s2))
    n = len(common)
    if n == 0:
        return 0
    # Observed agreement
    po = sum(1 for f in common if s1[f] == s2[f]) / n
    # Expected agreement by chance
    c1 = Counter(s1[f] for f in common)
    c2 = Counter(s2[f] for f in common)
    pe = sum((c1[r] / n) * (c2[r] / n) for r in regimes)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)

print(f"\n  Cohen's Kappa (chance-corrected agreement):")
print(f"    A vs B: {cohens_kappa(A, B):.3f}")
print(f"    A vs C: {cohens_kappa(A, C):.3f}")
print(f"    B vs C: {cohens_kappa(B, C):.3f}")
print(f"\n  Kappa interpretation: <0 = worse than chance, 0 = chance,")
print(f"    0.01-0.20 = slight, 0.21-0.40 = fair, 0.41-0.60 = moderate,")
print(f"    0.61-0.80 = substantial, 0.81-1.0 = near-perfect")

# Per-regime breakdown: which regime does C most agree with from A/B?
print(f"\n  Per-regime agreement rate (A vs C):")
for r in regimes:
    folios_in_r_A = [f for f in common_ac if A[f] == r]
    if folios_in_r_A:
        agree = sum(1 for f in folios_in_r_A if C[f] == r)
        print(f"    {r}: {agree}/{len(folios_in_r_A)} = {agree/len(folios_in_r_A)*100:.1f}%")

print(f"\n  Per-regime agreement rate (B vs C):")
for r in regimes:
    folios_in_r_B = [f for f in common_bc if B[f] == r]
    if folios_in_r_B:
        agree = sum(1 for f in folios_in_r_B if C[f] == r)
        print(f"    {r}: {agree}/{len(folios_in_r_B)} = {agree/len(folios_in_r_B)*100:.1f}%")

# Note about C's f85v2 absence
print(f"\n  NOTE: Source A contains f85v2, which is absent from C.")
print(f"  Source C has 82 folios total.")

# Final judgment
print(f"""
  ------------------------------------------------------
  VERDICT:

  The two old mappings (A and B) agree on only {agree_ab/len(common_ab)*100:.1f}% of folios.
  That means they DISAGREE on {disagree_ab} out of {len(common_ab)} common folios.

  Against the new data-driven mapping (C):
    - A agrees {agree_ac/len(common_ac)*100:.1f}% of the time
    - B agrees {agree_bc/len(common_bc)*100:.1f}% of the time

  All three agree on only {triple_agree/len(common_abc_set)*100:.1f}% of folios.
  All three disagree on {len(triple_disagree)/len(common_abc_set)*100:.1f}% of folios.

  Cohen's Kappa for A vs B ({cohens_kappa(A, B):.3f}) indicates
  {"worse than chance" if cohens_kappa(A, B) < 0 else "slight" if cohens_kappa(A, B) < 0.21 else "fair" if cohens_kappa(A, B) < 0.41 else "moderate"} agreement.
  ------------------------------------------------------
""")
