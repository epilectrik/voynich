#!/usr/bin/env python3
"""
Phase 558 -- T3: Coherence Scoring
==================================
Scores 5 coherence criteria (C1-C5) using T1 decomposition and T2 execution data.

C1: Execution coherence (viability, NaN, contradictions)
C2: Safety coherence (CLOSE weight vs position correlation + closure latch rate)
C3: Paragraph differentiation (pairwise JSD of paragraph profiles + permutation test)
C4: Token-level functional fit (6 directional tests on weight profiles)
C5: Null comparison (full vs null on C1-C4 metrics)

Overall verdict: PASS requires C1 + C5a + C5c + at least 2 of {C2, C3, C4}
"""

import json, sys, os, itertools
import numpy as np
from scipy import stats
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PHASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PHASE_DIR / "results"
T1_PATH = RESULTS_DIR / "t1_folio_decomposition.json"
T2_PATH = RESULTS_DIR / "t2_plant_execution.json"
OUT_PATH = RESULTS_DIR / "t3_coherence_scoring.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def jsd(p, q):
    """Jensen-Shannon Divergence between two probability vectors."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    # Normalize to probability distributions
    p_sum = p.sum()
    q_sum = q.sum()
    if p_sum == 0 or q_sum == 0:
        return 1.0  # maximally different
    p = p / p_sum
    q = q / q_sum
    m = 0.5 * (p + q)
    # Use base-2 log, handle zeros
    def kl(a, b):
        mask = a > 0
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def extract_close_weight(token):
    """Extract the CLOSE permission weight from a T1 token."""
    # permission field: index 3 = CLOSE (from T1 script: PERMISSIONS = ['ALLOW','DENY','HOLD','CLOSE'])
    perm = token["weights"]["permission"]
    return perm[3]  # CLOSE index


def extract_commit_close_route(token):
    """Extract COMMIT_CLOSE routing weight from a T1 token."""
    # routing field: index 1 = COMMIT_CLOSE (from T1: ROUTINGS = ['CONTINUE','COMMIT_CLOSE','RECYCLE','ESCALATE'])
    routing = token["weights"]["routing"]
    return routing[1]


DOMAIN_ORDER = ['THERMAL', 'FLOW', 'STABILIZE', 'TRANSITION', 'ARRANGE', 'CONTAIN']
PERMISSION_ORDER = ['ALLOW', 'DENY', 'HOLD', 'CLOSE']


def paragraph_domain_vector(para_profile):
    """Get the mean domain weight vector from a paragraph profile."""
    mdw = para_profile["mean_domain_weights"]
    if isinstance(mdw, dict):
        return np.array([mdw.get(k, 0.0) for k in DOMAIN_ORDER])
    return np.array(mdw)


def paragraph_permission_vector(para_profile):
    """Get the mean permission weight vector from a paragraph profile."""
    mpw = para_profile["mean_permission_weights"]
    if isinstance(mpw, dict):
        return np.array([mpw.get(k, 0.0) for k in PERMISSION_ORDER])
    return np.array(mpw)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading T1 data (may take a moment -- 39MB)...")
with open(T1_PATH, "r") as f:
    t1 = json.load(f)
print(f"  T1 loaded: {len(t1['paragraphs'])} paragraphs")

print("Loading T2 data...")
with open(T2_PATH, "r") as f:
    t2 = json.load(f)
print(f"  T2 loaded: {len(t2.get('full_runs', {}))} full runs, {len(t2.get('null_runs', {}))} null run types")

# ---------------------------------------------------------------------------
# C1: Execution Coherence
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("C1: EXECUTION COHERENCE")
print("="*70)

c1_results = {}

# Check all full runs
for run_key, run_data in t2.get("full_runs", {}).items():
    viability = run_data.get("viability", 0)
    total_nan = run_data.get("total_nan", -1)
    total_contradiction = run_data.get("total_contradiction", -1)

    c1_results[run_key] = {
        "viability": viability,
        "total_nan": total_nan,
        "total_contradiction": total_contradiction,
        "pass": viability == 1.0 and total_nan == 0 and total_contradiction == 0
    }
    print(f"  {run_key}: viability={viability:.3f}, NaN={total_nan}, contradictions={total_contradiction}")

# C1 passes if ALL full runs pass
c1_pass = all(r["pass"] for r in c1_results.values()) if c1_results else False
print(f"\n  C1 verdict: {'PASS' if c1_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# C2: Safety Coherence
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("C2: SAFETY COHERENCE")
print("="*70)

# C2a: Spearman correlation of CLOSE weight with normalized line position (from T1)
all_tokens_flat = []
for para in t1["paragraphs"]:
    for line in para["lines"]:
        for tok in line["tokens"]:
            all_tokens_flat.append(tok)

total_tokens = len(all_tokens_flat)
print(f"  Total tokens from T1: {total_tokens}")

# Compute normalized position for each token (0 to 1 across entire folio)
close_weights = []
positions = []
for i, tok in enumerate(all_tokens_flat):
    close_weights.append(extract_close_weight(tok))
    positions.append(i / max(total_tokens - 1, 1))

rho_close, p_close = stats.spearmanr(positions, close_weights)
print(f"  Spearman(position, CLOSE_weight): rho={rho_close:.4f}, p={p_close:.4e}")

# C2b: Closure latch activation rate from T2
closure_rates = {}
for run_key, run_data in t2.get("full_runs", {}).items():
    line_metrics = run_data.get("line_metrics", [])
    if line_metrics:
        n_close = sum(1 for lm in line_metrics if lm.get("sup_closing_activated", False))
        rate = n_close / len(line_metrics)
        closure_rates[run_key] = rate
        print(f"  {run_key} closure activation rate: {rate:.3f} ({n_close}/{len(line_metrics)} lines)")

# C2 pass criteria: rho > 0.15 AND p < 0.05 AND closure_rate > 0.0
c2_rho_pass = rho_close > 0.15 and p_close < 0.05
c2_closure_pass = any(r > 0.0 for r in closure_rates.values()) if closure_rates else False
c2_pass = c2_rho_pass and c2_closure_pass
print(f"\n  C2a (rho>0.15 & p<0.05): {'PASS' if c2_rho_pass else 'FAIL'}")
print(f"  C2b (closure_rate>0): {'PASS' if c2_closure_pass else 'FAIL'}")
print(f"  C2 verdict: {'PASS' if c2_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# C3: Paragraph Differentiation
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("C3: PARAGRAPH DIFFERENTIATION")
print("="*70)

para_profiles = t1.get("paragraph_profiles", [])
n_para = len(para_profiles)
print(f"  Number of paragraphs: {n_para}")

# Compute pairwise JSD on domain vectors
if n_para >= 2:
    domain_vecs = [paragraph_domain_vector(pp) for pp in para_profiles]

    pairwise_jsds = []
    for i, j in itertools.combinations(range(n_para), 2):
        d = jsd(domain_vecs[i], domain_vecs[j])
        pairwise_jsds.append(d)

    mean_jsd = np.mean(pairwise_jsds)
    print(f"  Mean pairwise JSD (domain): {mean_jsd:.4f}")
    print(f"  Range: [{min(pairwise_jsds):.4f}, {max(pairwise_jsds):.4f}]")

    # Permutation test: shuffle tokens across paragraphs, recompute profiles, compare JSD
    # Use 1000 permutations
    N_PERM = 1000
    rng = np.random.default_rng(42)

    # Collect all tokens with their paragraph membership
    para_sizes = []
    all_domain_weights = []
    for pi, para in enumerate(t1["paragraphs"]):
        count = 0
        for line in para["lines"]:
            for tok in line["tokens"]:
                all_domain_weights.append(np.array(tok["weights"]["domain"]))
                count += 1
        para_sizes.append(count)

    all_domain_weights = np.array(all_domain_weights)  # (N_tokens, 6)

    null_jsds = []
    for perm_i in range(N_PERM):
        # Shuffle token assignment to paragraphs
        shuffled_idx = rng.permutation(len(all_domain_weights))
        shuffled_weights = all_domain_weights[shuffled_idx]

        # Reconstruct paragraph profiles
        offset = 0
        perm_vecs = []
        for size in para_sizes:
            chunk = shuffled_weights[offset:offset+size]
            offset += size
            perm_vecs.append(chunk.mean(axis=0))

        # Pairwise JSD
        perm_jsds = []
        for i, j in itertools.combinations(range(n_para), 2):
            d = jsd(perm_vecs[i], perm_vecs[j])
            perm_jsds.append(d)
        null_jsds.append(np.mean(perm_jsds))

    null_jsds = np.array(null_jsds)
    p_perm = np.mean(null_jsds >= mean_jsd)
    print(f"  Permutation test (1000 perms): p={p_perm:.4f}")
    print(f"  Null mean JSD: {null_jsds.mean():.4f} +/- {null_jsds.std():.4f}")

    # C3 pass: mean_jsd > 0.05 AND p_perm < 0.05
    c3_pass = mean_jsd > 0.05 and p_perm < 0.05
else:
    mean_jsd = 0.0
    p_perm = 1.0
    null_jsds = np.array([0.0])
    pairwise_jsds = []
    c3_pass = False
    print("  Fewer than 2 paragraphs -- C3 trivially fails")

print(f"\n  C3 verdict: {'PASS' if c3_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# C4: Token-Level Functional Fit (6 directional tests)
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("C4: TOKEN-LEVEL FUNCTIONAL FIT (6 directional tests)")
print("="*70)

# Organize tokens by paragraph zone and quintile for directional tests
# Tests use T1 weight vectors

# Build per-paragraph token lists
para_token_lists = []
for para in t1["paragraphs"]:
    tokens = []
    for line in para["lines"]:
        for tok in line["tokens"]:
            tokens.append(tok)
    para_token_lists.append(tokens)

# D1: THERMAL domain weight should be higher in Q1-Q2 than Q3-Q4 (C1428: THERMAL peaks early then declines)
# domain index 0 = THERMAL
early_thermal = []
late_thermal = []
for tok in all_tokens_flat:
    q = tok.get("quintile", "Q2")
    thermal = tok["weights"]["domain"][0]
    if q in ("Q0", "Q1"):
        early_thermal.append(thermal)
    elif q in ("Q3", "Q4"):
        late_thermal.append(thermal)

if early_thermal and late_thermal:
    d1_stat, d1_p = stats.mannwhitneyu(early_thermal, late_thermal, alternative='greater')
    d1_effect = np.mean(early_thermal) - np.mean(late_thermal)
    d1_pass = d1_p < 0.05 and d1_effect > 0
    print(f"  D1 (THERMAL early>late): mean_early={np.mean(early_thermal):.4f}, mean_late={np.mean(late_thermal):.4f}, delta={d1_effect:.4f}, p={d1_p:.4e} -> {'PASS' if d1_pass else 'FAIL'}")
else:
    d1_pass = False
    d1_effect = 0.0
    d1_p = 1.0
    print(f"  D1: insufficient data -> FAIL")

# D2: CLOSE permission should increase toward line-final (C1427: line-final transition/closure profile)
# Compute per-line: compare first-half vs second-half of each line
d2_early_close = []
d2_late_close = []
for para in t1["paragraphs"]:
    for line in para["lines"]:
        toks = line["tokens"]
        n = len(toks)
        if n < 2:
            continue
        mid = n // 2
        for tok in toks[:mid]:
            d2_early_close.append(extract_close_weight(tok))
        for tok in toks[mid:]:
            d2_late_close.append(extract_close_weight(tok))

if d2_early_close and d2_late_close:
    d2_stat, d2_p = stats.mannwhitneyu(d2_late_close, d2_early_close, alternative='greater')
    d2_effect = np.mean(d2_late_close) - np.mean(d2_early_close)
    d2_pass = d2_p < 0.05 and d2_effect > 0
    print(f"  D2 (CLOSE late>early within lines): mean_late={np.mean(d2_late_close):.4f}, mean_early={np.mean(d2_early_close):.4f}, delta={d2_effect:.4f}, p={d2_p:.4e} -> {'PASS' if d2_pass else 'FAIL'}")
else:
    d2_pass = False
    d2_effect = 0.0
    d2_p = 1.0
    print(f"  D2: insufficient data -> FAIL")

# D3: DENY permission should be higher for tokens with hazardous frames (a-HEAD, r-terminal)
# C1446-C1451: k-HEAD immune, a-HEAD hazardous, r-terminal hazard vector
# permission index 1 = DENY
hazard_deny = []
safe_deny = []
for tok in all_tokens_flat:
    meta = tok.get("meta", {})
    head = meta.get("head", "")
    terminal = meta.get("terminal", "")
    deny = tok["weights"]["permission"][1]
    if head == "a" or terminal == "r":
        hazard_deny.append(deny)
    elif head == "k" or head == "e":
        safe_deny.append(deny)

if hazard_deny and safe_deny:
    d3_stat, d3_p = stats.mannwhitneyu(hazard_deny, safe_deny, alternative='greater')
    d3_effect = np.mean(hazard_deny) - np.mean(safe_deny)
    d3_pass = d3_p < 0.05 and d3_effect > 0
    print(f"  D3 (DENY hazard>safe frames): mean_haz={np.mean(hazard_deny):.4f}, mean_safe={np.mean(safe_deny):.4f}, delta={d3_effect:.4f}, p={d3_p:.4e} -> {'PASS' if d3_pass else 'FAIL'}")
else:
    d3_pass = False
    d3_effect = 0.0
    d3_p = 1.0
    print(f"  D3: insufficient data -> FAIL")

# D4: Guard BLOCK weight should be higher for headless tokens (C1488-C1493: headless = 6th domain)
# guard index: need to check field_names
# GUARDS from T1 script: ['PASS_THROUGH', 'ATTENUATE', 'BLOCK', 'AMPLIFY']
# guard index 2 = BLOCK
headless_block = []
headed_block = []
for tok in all_tokens_flat:
    meta = tok.get("meta", {})
    head = meta.get("head", "")
    block_w = tok["weights"]["guard"][2]
    if head == "" or head is None:
        headless_block.append(block_w)
    else:
        headed_block.append(block_w)

if headless_block and headed_block:
    d4_stat, d4_p = stats.mannwhitneyu(headless_block, headed_block, alternative='greater')
    d4_effect = np.mean(headless_block) - np.mean(headed_block)
    d4_pass = d4_p < 0.05 and d4_effect > 0
    print(f"  D4 (BLOCK headless>headed): mean_headless={np.mean(headless_block):.4f}, mean_headed={np.mean(headed_block):.4f}, delta={d4_effect:.4f}, p={d4_p:.4e} -> {'PASS' if d4_pass else 'FAIL'}")
else:
    d4_pass = False
    d4_effect = 0.0
    d4_p = 1.0
    print(f"  D4: insufficient data -> FAIL")

# D5: COMMIT_CLOSE routing should increase toward paragraph final lines
# routing index 1 = COMMIT_CLOSE
# Compare first-half vs second-half of each paragraph
d5_early_cc = []
d5_late_cc = []
for para in t1["paragraphs"]:
    lines = para["lines"]
    n_lines = len(lines)
    if n_lines < 2:
        continue
    mid_line = n_lines // 2
    for line in lines[:mid_line]:
        for tok in line["tokens"]:
            d5_early_cc.append(extract_commit_close_route(tok))
    for line in lines[mid_line:]:
        for tok in line["tokens"]:
            d5_late_cc.append(extract_commit_close_route(tok))

if d5_early_cc and d5_late_cc:
    d5_stat, d5_p = stats.mannwhitneyu(d5_late_cc, d5_early_cc, alternative='greater')
    d5_effect = np.mean(d5_late_cc) - np.mean(d5_early_cc)
    d5_pass = d5_p < 0.05 and d5_effect > 0
    print(f"  D5 (COMMIT_CLOSE late>early in para): mean_late={np.mean(d5_late_cc):.4f}, mean_early={np.mean(d5_early_cc):.4f}, delta={d5_effect:.4f}, p={d5_p:.4e} -> {'PASS' if d5_pass else 'FAIL'}")
else:
    d5_pass = False
    d5_effect = 0.0
    d5_p = 1.0
    print(f"  D5: insufficient data -> FAIL")

# D6: Paragraph-initial tokens should have higher ALLOW permission (C1426: specification zone)
# permission index 0 = ALLOW
para_init_allow = []
para_body_allow = []
for para in t1["paragraphs"]:
    lines = para["lines"]
    if not lines:
        continue
    # First line = paragraph initial
    for tok in lines[0]["tokens"]:
        para_init_allow.append(tok["weights"]["permission"][0])
    # Remaining lines = body
    for line in lines[1:]:
        for tok in line["tokens"]:
            para_body_allow.append(tok["weights"]["permission"][0])

if para_init_allow and para_body_allow:
    d6_stat, d6_p = stats.mannwhitneyu(para_init_allow, para_body_allow, alternative='greater')
    d6_effect = np.mean(para_init_allow) - np.mean(para_body_allow)
    d6_pass = d6_p < 0.05 and d6_effect > 0
    print(f"  D6 (ALLOW para_init>body): mean_init={np.mean(para_init_allow):.4f}, mean_body={np.mean(para_body_allow):.4f}, delta={d6_effect:.4f}, p={d6_p:.4e} -> {'PASS' if d6_pass else 'FAIL'}")
else:
    d6_pass = False
    d6_effect = 0.0
    d6_p = 1.0
    print(f"  D6: insufficient data -> FAIL")

d_tests = [d1_pass, d2_pass, d3_pass, d4_pass, d5_pass, d6_pass]
d_pass_count = sum(d_tests)
# C4 pass: at least 4 of 6 directional tests pass
c4_pass = d_pass_count >= 4
print(f"\n  Directional tests passed: {d_pass_count}/6")
print(f"  C4 verdict (need >=4): {'PASS' if c4_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# C5: Null Comparison
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("C5: NULL COMPARISON")
print("="*70)

# C5a (hard): full viability > mean null viability for at least one null type
# C5b (soft): full mean_abs_error < mean null mean_abs_error
# C5c (hard): full closure_rate > mean null closure_rate
# C5d (soft): at least one C4 directional test shows full > null separation

# Collect full run metrics (use first available full run as reference)
ref_run_key = list(t2.get("full_runs", {}).keys())[0] if t2.get("full_runs") else None
if ref_run_key:
    ref_run = t2["full_runs"][ref_run_key]
    full_viability = ref_run.get("viability", 0)
    full_line_metrics = ref_run.get("line_metrics", [])
    full_mean_error = np.mean([lm.get("mean_abs_error", 0) for lm in full_line_metrics]) if full_line_metrics else 0
    full_closure_rate = np.mean([1.0 if lm.get("sup_closing_activated", False) else 0.0 for lm in full_line_metrics]) if full_line_metrics else 0

    print(f"  Reference full run: {ref_run_key}")
    print(f"    viability={full_viability:.3f}, mean_error={full_mean_error:.4f}, closure_rate={full_closure_rate:.4f}")
else:
    full_viability = 0
    full_mean_error = 999
    full_closure_rate = 0

# Process null runs
null_summaries = {}
c5a_any_pass = False
c5b_any_pass = False
c5c_any_pass = False

for null_key, null_seeds in t2.get("null_runs", {}).items():
    if not isinstance(null_seeds, list):
        continue

    null_viabilities = [s.get("viability", 0) for s in null_seeds if isinstance(s, dict)]
    null_errors = [s.get("mean_abs_error", 0) for s in null_seeds if isinstance(s, dict)]
    null_closures = [s.get("closing_rate", 0) for s in null_seeds if isinstance(s, dict)]

    if not null_viabilities:
        continue

    mean_null_viab = np.mean(null_viabilities)
    mean_null_error = np.mean(null_errors) if null_errors else 999
    mean_null_closure = np.mean(null_closures) if null_closures else 0

    viab_better = full_viability > mean_null_viab
    error_better = full_mean_error < mean_null_error
    closure_better = full_closure_rate > mean_null_closure

    if viab_better:
        c5a_any_pass = True
    if error_better:
        c5b_any_pass = True
    if closure_better:
        c5c_any_pass = True

    null_summaries[null_key] = {
        "n_seeds": len(null_viabilities),
        "mean_viability": float(mean_null_viab),
        "std_viability": float(np.std(null_viabilities)),
        "mean_error": float(mean_null_error),
        "mean_closure": float(mean_null_closure),
        "full_viab_better": viab_better,
        "full_error_better": error_better,
        "full_closure_better": closure_better
    }

    print(f"  {null_key} ({len(null_viabilities)} seeds):")
    print(f"    viab: {mean_null_viab:.4f} (full {'>' if viab_better else '<='} null)")
    print(f"    error: {mean_null_error:.4f} (full {'<' if error_better else '>='} null)")
    print(f"    closure: {mean_null_closure:.4f} (full {'>' if closure_better else '<='} null)")

# C5d: Run C4 directional tests on null variants from T1
# Use token_shuffle null from T1
print("\n  C5d: Null directional test comparison")
null_variants = t1.get("null_variants", {})
c5d_pass = False
null_d_results = {}

for null_type, null_seeds_data in null_variants.items():
    if not isinstance(null_seeds_data, list) or len(null_seeds_data) == 0:
        continue

    # Run D1 (THERMAL early>late) on each null seed, get distribution of effects
    null_d1_effects = []
    for seed_data in null_seeds_data[:50]:  # cap at 50 seeds
        null_early_t = []
        null_late_t = []
        if isinstance(seed_data, dict) and "paragraphs" in seed_data:
            for para in seed_data["paragraphs"]:
                for line in para.get("lines", []):
                    for tok in line.get("tokens", []):
                        q = tok.get("quintile", "Q2")
                        thermal = tok["weights"]["domain"][0]
                        if q in ("Q0", "Q1"):
                            null_early_t.append(thermal)
                        elif q in ("Q3", "Q4"):
                            null_late_t.append(thermal)
        if null_early_t and null_late_t:
            null_d1_effects.append(np.mean(null_early_t) - np.mean(null_late_t))

    if null_d1_effects:
        mean_null_d1 = np.mean(null_d1_effects)
        # Real D1 effect exceeds null distribution?
        pval = np.mean(np.array(null_d1_effects) >= d1_effect)
        exceeds = d1_effect > mean_null_d1
        if exceeds and pval < 0.05:
            c5d_pass = True
        null_d_results[null_type] = {
            "D1_real_effect": float(d1_effect),
            "D1_null_mean": float(mean_null_d1),
            "D1_null_std": float(np.std(null_d1_effects)),
            "D1_exceeds": exceeds,
            "D1_pval": float(pval)
        }
        print(f"    {null_type} D1: real={d1_effect:.4f}, null_mean={mean_null_d1:.4f}, exceeds={exceeds}, p={pval:.4f}")

c5a_pass = c5a_any_pass  # hard requirement
c5c_pass = c5c_any_pass  # hard requirement

print(f"\n  C5a (viab full>null, hard): {'PASS' if c5a_pass else 'FAIL'}")
print(f"  C5b (error full<null, soft): {'PASS' if c5b_any_pass else 'FAIL'}")
print(f"  C5c (closure full>null, hard): {'PASS' if c5c_pass else 'FAIL'}")
print(f"  C5d (directional separation, soft): {'PASS' if c5d_pass else 'FAIL'}")

c5_pass = c5a_pass and c5c_pass  # both hard requirements must pass

print(f"  C5 verdict (C5a AND C5c): {'PASS' if c5_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# Overall Verdict
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("OVERALL VERDICT")
print("="*70)

# PASS requires: C1 + C5a + C5c + at least 2 of {C2, C3, C4}
optional_passes = sum([c2_pass, c3_pass, c4_pass])
overall_pass = c1_pass and c5a_pass and c5c_pass and optional_passes >= 2

print(f"  C1 (execution coherence):     {'PASS' if c1_pass else 'FAIL'}  [required]")
print(f"  C2 (safety coherence):        {'PASS' if c2_pass else 'FAIL'}  [optional, {1 if c2_pass else 0}/1]")
print(f"  C3 (paragraph differentiation):{'PASS' if c3_pass else 'FAIL'}  [optional, {1 if c3_pass else 0}/1]")
print(f"  C4 (functional fit):          {'PASS' if c4_pass else 'FAIL'}  [optional, {1 if c4_pass else 0}/1]")
print(f"  C5a (viab > null):            {'PASS' if c5a_pass else 'FAIL'}  [required]")
print(f"  C5c (closure > null):         {'PASS' if c5c_pass else 'FAIL'}  [required]")
print(f"  Optional criteria met: {optional_passes}/3 (need >= 2)")
print(f"\n  *** OVERALL: {'PASS' if overall_pass else 'FAIL'} ***")

# ---------------------------------------------------------------------------
# Honest assessment
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("HONEST ASSESSMENT")
print("="*70)

# Check if nulls are basically the same as full
if null_summaries:
    viab_diffs = [full_viability - ns["mean_viability"] for ns in null_summaries.values()]
    mean_viab_diff = np.mean(viab_diffs) if viab_diffs else 0
    print(f"  Mean viability advantage over nulls: {mean_viab_diff:.4f}")
    if abs(mean_viab_diff) < 0.02:
        print("  WARNING: Nulls are essentially indistinguishable from full runs on viability.")
        print("  The token decomposition may not contribute meaningful execution differentiation.")

    error_diffs = [full_mean_error - ns["mean_error"] for ns in null_summaries.values()]
    mean_error_diff = np.mean(error_diffs) if error_diffs else 0
    print(f"  Mean error advantage over nulls: {mean_error_diff:.4f}")
    if abs(mean_error_diff) < 0.01:
        print("  WARNING: Error rates are essentially identical between full and null runs.")

# Check if plant dynamics are too constrained for token effects to matter
if ref_run_key:
    max_Ts = [lm.get("max_T", 0) for lm in full_line_metrics]
    overall_max_T = max(max_Ts) if max_Ts else 0
    print(f"  Max temperature achieved in full run: {overall_max_T:.4f}")
    if overall_max_T < 0.8:
        print("  WARNING: Plant never approaches target temperature (1.05).")
        print("  The ODE dynamics may be too heavily damped for supervisory signals to matter.")

# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------
output = {
    "metadata": {
        "phase": "558",
        "task": "T3_coherence_scoring",
        "folio": "f43v",
        "t1_path": str(T1_PATH),
        "t2_path": str(T2_PATH)
    },
    "C1": {
        "verdict": "PASS" if c1_pass else "FAIL",
        "runs": c1_results
    },
    "C2": {
        "verdict": "PASS" if c2_pass else "FAIL",
        "spearman_rho": float(rho_close),
        "spearman_p": float(p_close),
        "closure_rates": {k: float(v) for k, v in closure_rates.items()},
        "c2a_pass": c2_rho_pass,
        "c2b_pass": c2_closure_pass
    },
    "C3": {
        "verdict": "PASS" if c3_pass else "FAIL",
        "mean_pairwise_jsd": float(mean_jsd),
        "pairwise_jsds": [float(x) for x in pairwise_jsds],
        "permutation_p": float(p_perm),
        "null_jsd_mean": float(null_jsds.mean()),
        "null_jsd_std": float(null_jsds.std()),
        "n_paragraphs": n_para
    },
    "C4": {
        "verdict": "PASS" if c4_pass else "FAIL",
        "tests_passed": d_pass_count,
        "tests_total": 6,
        "D1_thermal_gradient": {"pass": d1_pass, "effect": float(d1_effect), "p": float(d1_p)},
        "D2_close_within_line": {"pass": d2_pass, "effect": float(d2_effect), "p": float(d2_p)},
        "D3_deny_hazard_frame": {"pass": d3_pass, "effect": float(d3_effect), "p": float(d3_p)},
        "D4_block_headless": {"pass": d4_pass, "effect": float(d4_effect), "p": float(d4_p)},
        "D5_commit_close_para": {"pass": d5_pass, "effect": float(d5_effect), "p": float(d5_p)},
        "D6_allow_para_init": {"pass": d6_pass, "effect": float(d6_effect), "p": float(d6_p)}
    },
    "C5": {
        "verdict": "PASS" if c5_pass else "FAIL",
        "c5a_viab_pass": c5a_pass,
        "c5b_error_pass": c5b_any_pass,
        "c5c_closure_pass": c5c_pass,
        "c5d_directional_pass": c5d_pass,
        "null_summaries": null_summaries,
        "null_directional": null_d_results
    },
    "overall": {
        "verdict": "PASS" if overall_pass else "FAIL",
        "required_met": c1_pass and c5a_pass and c5c_pass,
        "optional_met": optional_passes,
        "optional_needed": 2,
        "formula": "C1 AND C5a AND C5c AND (>=2 of {C2,C3,C4})"
    },
    "honest_assessment": {
        "null_viab_diff": float(mean_viab_diff) if null_summaries else None,
        "null_error_diff": float(mean_error_diff) if null_summaries else None,
        "max_temperature": float(overall_max_T) if ref_run_key else None,
        "plant_too_constrained": bool(overall_max_T < 0.8) if ref_run_key else None,
        "nulls_indistinguishable": bool(abs(mean_viab_diff) < 0.02) if null_summaries else None
    }
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to: {OUT_PATH}")
print("Done.")
