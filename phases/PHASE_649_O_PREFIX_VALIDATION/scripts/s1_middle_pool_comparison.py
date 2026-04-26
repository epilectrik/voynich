"""
Phase 649 Step 1: MIDDLE-pool comparison across o-prefixes.

Disambiguation test for C1962:
- If ok/ot/ol/or carry DISTINCT operational content (4-channel reading),
  their MIDDLE distributions should be statistically distinct.
- If they're ALLOMORPHS of the same channel (decoration variants),
  their MIDDLE distributions should be similar.

Method:
- For each o-prefix, extract the MIDDLE of every token starting with that prefix
- Compute pairwise Jaccard similarity on top-K MIDDLEs
- Compute pairwise Jensen-Shannon divergence on full distributions
- Run within-position-bin (early/mid/late) to address crazy-expert's specific
  formulation: "different MIDDLE distributions when they appear at the same
  paragraph position."

Falsification:
- High Jaccard (>0.7) on top-20 MIDDLEs across all pairs → allomorph reading wins
- Low cross-pair JS divergence (<0.05) → same channel
- High Jaccard but distinct mass distribution → channels with shared vocabulary
"""
import sys
import json
import math
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

# Group tokens into paragraphs (matching s6/s7 setup)
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

def position_bin(i, n):
    p = i / max(n - 1, 1)
    if p < 0.33: return 'early'
    if p < 0.67: return 'mid'
    return 'late'

# Collect MIDDLEs per prefix, overall and per position bin
prefixes = ['ok','ot','ol','or']
middles_by_prefix = {p: Counter() for p in prefixes}
middles_by_prefix_pos = {p: {'early': Counter(), 'mid': Counter(), 'late': Counter()}
                         for p in prefixes}
all_token_count = {p: 0 for p in prefixes}

for (f, par_idx), toks in paragraphs.items():
    n = len(toks)
    if n < 4: continue
    for i, t in enumerate(toks):
        w = t.word
        if len(w) < 2 or w[0] != 'o' or w[1] not in ('k','t','l','r'):
            continue
        pref = 'o' + w[1]
        all_token_count[pref] += 1
        # Extract middle: skip first 2 chars (prefix), then use morphology
        m = morph.extract(w)
        # The morphology extracts prefix=ok/ot/ol/or, middle is what's after
        mid = m.middle if m.middle else ''
        # For tokens like "okedy" middle might be empty if 'edy' is treated as suffix
        # We actually want the part between prefix and suffix
        # Use the post-prefix substring as a fallback if morphology gives empty middle
        if not mid:
            # Take everything after the 2-char prefix; classify suffix off the end
            rest = w[2:]
            mid = rest  # crude — will include suffix too, but consistent across prefixes
        middles_by_prefix[pref][mid] += 1
        bin_name = position_bin(i, n)
        middles_by_prefix_pos[pref][bin_name][mid] += 1

print("="*72)
print("TEST: MIDDLE-pool comparison across o-prefixes")
print("="*72)
print()
print("Token counts per o-prefix (in paragraphs >= 4 tokens):")
for p in prefixes:
    print(f"  {p}: {all_token_count[p]:5d} tokens, {len(middles_by_prefix[p])} distinct MIDDLEs")
print()

# Top-K MIDDLEs per prefix
print("Top 10 MIDDLEs per prefix (showing token-rate within prefix):")
for p in prefixes:
    print(f"\n  {p}:")
    total = sum(middles_by_prefix[p].values())
    for mid, c in middles_by_prefix[p].most_common(10):
        repr_mid = repr(mid)
        print(f"    {repr_mid:>12s}: {c:5d} ({c/total*100:5.1f}%)")

# Pairwise Jaccard on top-K
def jaccard(set_a, set_b):
    if not set_a and not set_b: return 0.0
    return len(set_a & set_b) / len(set_a | set_b)

print()
print("="*72)
print("PAIRWISE JACCARD on top-20 MIDDLEs (set overlap):")
print("="*72)
print("Higher = more shared vocabulary (allomorph signature)")
print("Lower = more distinct vocabulary (channel signature)")
print()
for K in (10, 20, 50):
    print(f"\nTop-{K}:")
    print("        " + "  ".join(f"{p:>5s}" for p in prefixes))
    for p1 in prefixes:
        row = [f"{p1:>5s}"]
        s1 = set(m for m, _ in middles_by_prefix[p1].most_common(K))
        for p2 in prefixes:
            if p1 == p2:
                row.append(f"{1.00:>5.2f}")
            else:
                s2 = set(m for m, _ in middles_by_prefix[p2].most_common(K))
                row.append(f"{jaccard(s1, s2):>5.2f}")
        print("  ".join(row))

# Jensen-Shannon divergence on full distributions
def js_divergence(p_dist, q_dist):
    """Jensen-Shannon divergence between two discrete distributions
    (Counters), normalized. Returns nats; 0 = identical, log(2) ≈ 0.693 = max."""
    keys = set(p_dist.keys()) | set(q_dist.keys())
    p_total = sum(p_dist.values()) or 1
    q_total = sum(q_dist.values()) or 1
    p_arr = [p_dist.get(k, 0) / p_total for k in keys]
    q_arr = [q_dist.get(k, 0) / q_total for k in keys]
    m_arr = [(pv + qv) / 2 for pv, qv in zip(p_arr, q_arr)]
    def kl(a, b):
        return sum(av * math.log(av / bv) for av, bv in zip(a, b)
                   if av > 0 and bv > 0)
    return 0.5 * kl(p_arr, m_arr) + 0.5 * kl(q_arr, m_arr)

print()
print("="*72)
print("PAIRWISE JENSEN-SHANNON DIVERGENCE on full MIDDLE distributions:")
print("="*72)
print("Range: 0 (identical) to ln(2) ~0.693 (max divergence)")
print("Reference: a JS of 0.05-0.1 = subtle but real distinction")
print("           a JS of 0.2+ = clearly distinct distributions")
print()
print("        " + "  ".join(f"{p:>5s}" for p in prefixes))
for p1 in prefixes:
    row = [f"{p1:>5s}"]
    for p2 in prefixes:
        if p1 == p2:
            row.append(f"{0.0:>5.2f}")
        else:
            jsd = js_divergence(middles_by_prefix[p1], middles_by_prefix[p2])
            row.append(f"{jsd:>5.3f}")
    print("  ".join(row))

# Within-position-bin comparison
print()
print("="*72)
print("WITHIN-POSITION-BIN JS DIVERGENCE (per crazy-expert's specific test)")
print("="*72)
print("Compares MIDDLE distributions of o-prefixes WITHIN the same paragraph-")
print("position bin. If channels are distinct, divergence should remain high.")
print("If allomorphs, divergence should drop when controlling for position.")
print()
for bin_name in ('early','mid','late'):
    print(f"\n[{bin_name.upper()} bin]")
    print("        " + "  ".join(f"{p:>5s}" for p in prefixes))
    for p1 in prefixes:
        row = [f"{p1:>5s}"]
        for p2 in prefixes:
            if p1 == p2:
                row.append(f"{0.0:>5.2f}")
            else:
                d1 = middles_by_prefix_pos[p1][bin_name]
                d2 = middles_by_prefix_pos[p2][bin_name]
                if sum(d1.values()) < 5 or sum(d2.values()) < 5:
                    row.append(f"{'  --':>5s}")
                else:
                    jsd = js_divergence(d1, d2)
                    row.append(f"{jsd:>5.3f}")
        print("  ".join(row))

# Save
out = {
    'token_counts': all_token_count,
    'top_middles': {p: middles_by_prefix[p].most_common(20) for p in prefixes},
    'js_divergence_overall': {f'{p1}_vs_{p2}':
                              js_divergence(middles_by_prefix[p1], middles_by_prefix[p2])
                              for p1 in prefixes for p2 in prefixes if p1 != p2},
    'jaccard_top20': {f'{p1}_vs_{p2}':
                      jaccard(set(m for m,_ in middles_by_prefix[p1].most_common(20)),
                              set(m for m,_ in middles_by_prefix[p2].most_common(20)))
                      for p1 in prefixes for p2 in prefixes if p1 != p2},
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/middle_pool_comparison.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)

# Verdict
print()
print("="*72)
print("VERDICT")
print("="*72)
js_pairs = [v for k, v in out['js_divergence_overall'].items()]
mean_js = sum(js_pairs) / len(js_pairs)
jac_pairs = [v for k, v in out['jaccard_top20'].items()]
mean_jac = sum(jac_pairs) / len(jac_pairs)
print(f"Mean pairwise JS divergence: {mean_js:.3f}")
print(f"Mean pairwise Jaccard (top-20): {mean_jac:.3f}")
print()
if mean_js > 0.15 and mean_jac < 0.5:
    print("→ Channels carry DISTINCT MIDDLE content. Allomorph hypothesis falsified.")
    print("  C1962 4-axis claim survives this test.")
elif mean_js < 0.05 and mean_jac > 0.7:
    print("→ Channels share MIDDLE content. Allomorph hypothesis SUPPORTED.")
    print("  C1962 should be revised — the 4 prefixes are decoration variants.")
else:
    print(f"→ Mixed signal. JS={mean_js:.3f}, Jaccard={mean_jac:.3f}.")
    print("  Channels share *some* vocabulary but deploy it differently.")
    print("  C1962 4-axis claim is qualified-supported.")
