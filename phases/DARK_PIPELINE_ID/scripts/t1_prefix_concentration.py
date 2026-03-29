"""
T1: Dark MIDDLE PREFIX concentration vs frequency-matched bridge MIDDLEs.

Question: Do individual dark MIDDLEs lock to specific PREFIXes more than
bridge MIDDLEs of comparable frequency?

Method: PREFIX concentration ratio = fraction of tokens using the most
common PREFIX. Bounded [0,1] regardless of token count (avoids the
entropy ceiling problem at low frequencies).

Design fix per expert review: use concentration ratio instead of Shannon
entropy because dark MIDDLEs average 5.7 tokens (C1135) — entropy is
mechanically capped at low counts. Also use rarefaction as secondary check.

Pass: dark concentration significantly higher than frequency-matched bridge, p<0.01
"""

import sys, os, io, json, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load dark pipeline set
with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

# Load bridge middles
from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
# Bridge = PP middles that ARE in grammar (matched). Dark = PP middles NOT in grammar.
# We need the bridge set. Bridge MIDDLEs are the PP MIDDLEs minus dark pipeline.
bridge_set = pp_middles - dp_set

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
print(f"Currier B: {len(all_b)} tokens")
print(f"Dark MIDDLEs: {len(dp_set)}, Bridge MIDDLEs: {len(bridge_set)}")

# ═══ BUILD PER-MIDDLE PREFIX PROFILES ═══
mid_prefix = defaultdict(Counter)  # middle -> Counter of prefixes
mid_total = Counter()              # middle -> total token count

for t in all_b:
    m = morph.extract(t.word)
    mid = m.middle
    if mid:
        pre = m.prefix or 'BARE'
        mid_prefix[mid][pre] += 1
        mid_total[mid] += 1

# ═══ COMPUTE PREFIX CONCENTRATION RATIO ═══
# Concentration = max(prefix_count) / total_count for that MIDDLE
# 1.0 = all tokens use same PREFIX, 0.0 = perfectly spread

def concentration(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return max(counter.values()) / total

# Filter: need minimum token count to be meaningful
MIN_TOKENS = 5  # Lower than 10 to get more dark MIDDLEs

dark_conc = []  # (middle, concentration, token_count)
bridge_conc = []

for mid in dp_set:
    n = mid_total.get(mid, 0)
    if n >= MIN_TOKENS:
        c = concentration(mid_prefix[mid])
        dark_conc.append((mid, c, n))

for mid in bridge_set:
    n = mid_total.get(mid, 0)
    if n >= MIN_TOKENS:
        c = concentration(mid_prefix[mid])
        bridge_conc.append((mid, c, n))

print(f"\nQualifying MIDDLEs (>={MIN_TOKENS} tokens):")
print(f"  Dark: {len(dark_conc)}")
print(f"  Bridge: {len(bridge_conc)}")

# ═══ FREQUENCY-MATCHED COMPARISON ═══
# For each dark MIDDLE, find bridge MIDDLEs in frequency range [N*0.5, N*2.0]
dark_vals = [c for _, c, _ in dark_conc]
dark_freqs = [n for _, _, n in dark_conc]

matched_bridge_vals = []
for mid, c, n in dark_conc:
    lo = n * 0.5
    hi = n * 2.0
    matches = [bc for _, bc, bn in bridge_conc if lo <= bn <= hi]
    matched_bridge_vals.extend(matches)

# Also compute unmatched (all qualifying bridge)
all_bridge_vals = [c for _, c, _ in bridge_conc]

print(f"\n  Dark concentrations: n={len(dark_vals)}, mean={sum(dark_vals)/len(dark_vals):.3f}, median={sorted(dark_vals)[len(dark_vals)//2]:.3f}")
print(f"  Bridge (all): n={len(all_bridge_vals)}, mean={sum(all_bridge_vals)/len(all_bridge_vals):.3f}, median={sorted(all_bridge_vals)[len(all_bridge_vals)//2]:.3f}")
print(f"  Bridge (freq-matched): n={len(matched_bridge_vals)}, mean={sum(matched_bridge_vals)/len(matched_bridge_vals):.3f}" if matched_bridge_vals else "  Bridge (freq-matched): n=0")

# ═══ MANN-WHITNEY U TEST ═══
def mann_whitney(x, y):
    """Simple Mann-Whitney U test. Returns U, z, p (two-tailed)."""
    import math
    nx, ny = len(x), len(y)
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties by averaging)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average
        for k in range(i, j):
            ranks[id(combined[k])] = avg_rank  # Not quite right, need index-based

        i = j

    # Simpler: rank by sorting
    vals = [v for v, _ in combined]
    rank_list = []
    i = 0
    while i < len(vals):
        j = i
        while j < len(vals) and vals[j] == vals[i]:
            j += 1
        avg_r = sum(range(i+1, j+1)) / (j - i)
        for _ in range(i, j):
            rank_list.append(avg_r)
        i = j

    # Sum ranks for x
    rx = sum(rank_list[k] for k in range(len(combined)) if combined[k][1] == 'x')
    u = rx - nx * (nx + 1) / 2
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)
    z = (u - mu) / sigma if sigma > 0 else 0

    # Two-tailed p via normal approx
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return u, z, p

print("\n" + "=" * 90)
print("MANN-WHITNEY U TEST: Dark vs Bridge PREFIX Concentration")
print("=" * 90)

# Dark vs all bridge
u, z, p = mann_whitney(dark_vals, all_bridge_vals)
print(f"\n  Dark vs ALL bridge:")
print(f"    U={u:.0f}, Z={z:.2f}, p={p:.6f}")
print(f"    Dark mean={sum(dark_vals)/len(dark_vals):.3f}, Bridge mean={sum(all_bridge_vals)/len(all_bridge_vals):.3f}")
if z > 0:
    print(f"    Dark concentration HIGHER (more PREFIX-locked)")
else:
    print(f"    Dark concentration LOWER (less PREFIX-locked)")
if p < 0.001:
    print(f"    *** p < 0.001 HIGHLY SIGNIFICANT ***")
elif p < 0.01:
    print(f"    ** p < 0.01 SIGNIFICANT **")
elif p < 0.05:
    print(f"    * p < 0.05 SIGNIFICANT *")
else:
    print(f"    NOT SIGNIFICANT (p={p:.3f})")

# Dark vs freq-matched bridge
if matched_bridge_vals:
    u2, z2, p2 = mann_whitney(dark_vals, matched_bridge_vals)
    print(f"\n  Dark vs FREQUENCY-MATCHED bridge:")
    print(f"    U={u2:.0f}, Z={z2:.2f}, p={p2:.6f}")
    print(f"    Dark mean={sum(dark_vals)/len(dark_vals):.3f}, Matched bridge mean={sum(matched_bridge_vals)/len(matched_bridge_vals):.3f}")
    if z2 > 0:
        print(f"    Dark concentration HIGHER (more PREFIX-locked)")
    else:
        print(f"    Dark concentration LOWER (less PREFIX-locked)")
    if p2 < 0.001:
        print(f"    *** p < 0.001 HIGHLY SIGNIFICANT ***")
    elif p2 < 0.01:
        print(f"    ** p < 0.01 SIGNIFICANT **")
    elif p2 < 0.05:
        print(f"    * p < 0.05 SIGNIFICANT *")
    else:
        print(f"    NOT SIGNIFICANT (p={p2:.3f})")

# ═══ RAREFACTION CHECK ═══
# Subsample bridge MIDDLEs DOWN to dark-level token counts
print("\n" + "=" * 90)
print("RAREFACTION: Subsample bridge to dark-level token counts")
print("=" * 90)

random.seed(42)
N_RARE = 200  # iterations

rarefied_bridge_concs = []
for mid, bc, bn in bridge_conc:
    if bn < MIN_TOKENS:
        continue
    # For each dark MIDDLE, find the median dark token count
    median_dark_n = sorted(dark_freqs)[len(dark_freqs)//2]
    # Subsample this bridge MIDDLE down to median_dark_n tokens
    if bn <= median_dark_n:
        rarefied_bridge_concs.append(bc)
        continue
    # Subsample N_RARE times, take mean concentration
    tokens_for_mid = []
    for t in all_b:
        m = morph.extract(t.word)
        if m.middle == mid:
            tokens_for_mid.append(m.prefix or 'BARE')
    concs = []
    for _ in range(N_RARE):
        sample = random.sample(tokens_for_mid, min(median_dark_n, len(tokens_for_mid)))
        c_sample = Counter(sample)
        concs.append(max(c_sample.values()) / len(sample))
    rarefied_bridge_concs.append(sum(concs) / len(concs))

if rarefied_bridge_concs:
    u3, z3, p3 = mann_whitney(dark_vals, rarefied_bridge_concs)
    print(f"\n  Dark vs RAREFIED bridge (subsampled to median dark N={sorted(dark_freqs)[len(dark_freqs)//2]}):")
    print(f"    n_dark={len(dark_vals)}, n_bridge_rarefied={len(rarefied_bridge_concs)}")
    print(f"    Dark mean={sum(dark_vals)/len(dark_vals):.3f}, Rarefied bridge mean={sum(rarefied_bridge_concs)/len(rarefied_bridge_concs):.3f}")
    print(f"    U={u3:.0f}, Z={z3:.2f}, p={p3:.6f}")
    if z3 > 0 and p3 < 0.01:
        print(f"    *** Dark MORE PREFIX-locked even after rarefaction ***")
    elif z3 <= 0:
        print(f"    Dark LESS concentrated after frequency control — PREFIX lock is a FREQUENCY ARTIFACT")
    else:
        print(f"    Not significant after rarefaction (p={p3:.3f})")

# ═══ TOP DARK MIDDLEs BY CONCENTRATION ═══
print("\n" + "=" * 90)
print("TOP 15 MOST PREFIX-LOCKED DARK MIDDLEs")
print("=" * 90)

dark_conc.sort(key=lambda x: -x[1])
print(f"\n  {'MIDDLE':>8s} {'N':>5s} {'Conc':>6s} {'Top PREFIX':>12s} {'Top%':>6s} {'2nd PREFIX':>12s} {'2nd%':>6s}")
print(f"  {'-'*60}")
for mid, c, n in dark_conc[:15]:
    top = mid_prefix[mid].most_common(2)
    t1_pre, t1_ct = top[0]
    t1_pct = 100 * t1_ct / n
    t2_pre, t2_ct = top[1] if len(top) > 1 else ('', 0)
    t2_pct = 100 * t2_ct / n
    print(f"  {mid:>8s} {n:5d} {c:6.3f} {t1_pre:>12s} {t1_pct:5.0f}% {t2_pre:>12s} {t2_pct:5.0f}%")

# ═══ DISTRIBUTION COMPARISON ═══
print("\n" + "=" * 90)
print("CONCENTRATION DISTRIBUTION")
print("=" * 90)

def histogram(vals, bins=10, label=""):
    mn, mx = min(vals), max(vals)
    width = (mx - mn) / bins if mx > mn else 1
    counts = [0] * bins
    for v in vals:
        b = min(int((v - mn) / width), bins - 1)
        counts[b] += 1
    print(f"\n  {label} (n={len(vals)}):")
    for i, ct in enumerate(counts):
        lo = mn + i * width
        hi = lo + width
        bar = '#' * (ct * 2)
        print(f"    {lo:.2f}-{hi:.2f}: {ct:3d} {bar}")

histogram(dark_vals, 10, "Dark MIDDLEs")
histogram(all_bridge_vals, 10, "Bridge MIDDLEs (all)")

# ═══ VERDICT ═══
print("\n" + "=" * 90)
print("VERDICT")
print("=" * 90)

# Use the rarefied result as the authoritative test
if rarefied_bridge_concs:
    if z3 > 0 and p3 < 0.01:
        print(f"\n  PASS: Dark MIDDLEs are significantly more PREFIX-locked than bridge")
        print(f"  even after controlling for frequency via rarefaction.")
        print(f"  This is a REAL structural property of the dark pipeline, not a frequency artifact.")
    elif z3 > 0 and p3 < 0.05:
        print(f"\n  MARGINAL: Dark MIDDLEs trend more PREFIX-locked (p={p3:.3f})")
        print(f"  but does not pass the p<0.01 threshold.")
    else:
        print(f"\n  FAIL: Dark PREFIX concentration is NOT significantly higher")
        print(f"  than frequency-matched bridge after rarefaction.")
        print(f"  The PREFIX lock observed on f75r may be a frequency artifact.")
else:
    print(f"\n  INCONCLUSIVE: insufficient data for rarefaction")

print("\n" + "=" * 90)
print("DONE")
print("=" * 90)
