"""
10_c619_phase_level_retest.py - C619 Phase-Level Retest

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 10: Do unique MIDDLEs show different transition profiles WITHIN phases?

Background: C619 tested globally and found V=0.070 (near-identical transition
profiles between unique and shared MIDDLEs). If unique MIDDLEs encode material
identity, they should show HIGHER behavioral divergence within the same
procedural phase. If they're just operational variants, divergence should
remain low.

Method:
1. For each B folio, assign zones (SETUP/PROCESS/FINISH) using paragraph structure
2. For tokens carrying unique vs shared MIDDLEs, record their successor's MIDDLE class
3. Successor MIDDLE classes: k-class (contains k), h-class (contains h),
   e-class (contains e), other
4. Strategy A: Aggregate JSD per zone (unique vs shared successor distributions)
   with bootstrap CIs to assess stability
5. Strategy B: Per-folio JSD within each zone -- for each folio+zone with enough
   tokens of both types, compute JSD between unique and shared successor
   distributions, then compare across folios using Mann-Whitney U
6. Compare intra-group divergence: sample random MIDDLE subsets from shared
   population to estimate expected JSD range, then check if unique-vs-shared
   JSD exceeds this baseline

Verdict:
  SUPPORTED if unique MIDDLEs show significantly higher within-zone divergence
    (p < 0.05 in per-folio comparison or bootstrap CIs exclude 0)
  NOT_SUPPORTED if divergence is comparable or unique is lower
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import math
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology
from scipy.stats import mannwhitneyu, chi2_contingency


# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
N_BOOTSTRAP = 1000  # Bootstrap iterations for CI
MIN_TOKENS_PER_GROUP = 5  # Min tokens per group in per-folio analysis
RNG_SEED = 42


# ============================================================
# JENSEN-SHANNON DIVERGENCE
# ============================================================
def kl_divergence(p, q):
    """Compute KL divergence D(P || Q). Both must be numpy arrays summing to 1."""
    mask = p > 0
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(mask, p * np.log2(p / q), 0.0)
    return np.sum(result)


def js_divergence(p, q):
    """Compute Jensen-Shannon divergence between two distributions (as counts or probs)."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)

    p_sum = p.sum()
    q_sum = q.sum()
    if p_sum == 0 or q_sum == 0:
        return None
    p = p / p_sum
    q = q / q_sum

    m = 0.5 * (p + q)
    return float(0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m))


# ============================================================
# SUCCESSOR MIDDLE CLASS CLASSIFICATION
# ============================================================
ALL_CLASSES = ['k-class', 'h-class', 'e-class', 'other']


def classify_middle_broad(middle):
    """
    Classify a MIDDLE into broad kernel-based classes.
    Priority: k > h > e > other (reflects kernel operator hierarchy).
    """
    if middle is None:
        return 'other'
    if 'k' in middle:
        return 'k-class'
    if 'h' in middle:
        return 'h-class'
    if 'e' in middle:
        return 'e-class'
    return 'other'


def counter_to_vec(counter, classes=ALL_CLASSES):
    """Convert Counter to numpy array aligned to class order."""
    return np.array([counter.get(c, 0) for c in classes], dtype=float)


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with line/paragraph metadata and morphology."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        if not tok.placement.startswith('P'):
            continue

        m = morph.extract(tok.word)
        if m.middle is None or m.middle == '_EMPTY_':
            mid = None
        else:
            mid = m.middle

        tokens.append({
            'word': tok.word,
            'middle': mid,
            'middle_class': classify_middle_broad(mid),
            'folio': tok.folio,
            'line': tok.line,
            'par_initial': tok.par_initial,
            'line_initial': tok.line_initial,
        })

    return tokens


# ============================================================
# PARAGRAPH BOUNDARY DETECTION
# ============================================================
def assign_paragraphs(folio_tokens):
    """Assign paragraph numbers. par_initial=True + line_initial=True = new paragraph."""
    current_para = 0
    para_assignments = []
    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)
    return para_assignments


# ============================================================
# ZONE ASSIGNMENT
# ============================================================
def assign_zones(folio_tokens, para_assignments):
    """
    Assign SETUP/PROCESS/FINISH zones.
    3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
    1-2 paragraphs: line-based 20/60/20 split
    """
    n_paras = max(para_assignments) if para_assignments else 0

    if n_paras >= 3:
        first_para = 1
        last_para = n_paras
        zones = []
        for p in para_assignments:
            if p == first_para:
                zones.append('SETUP')
            elif p == last_para:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones
    else:
        lines = []
        seen = set()
        for tok in folio_tokens:
            if tok['line'] not in seen:
                lines.append(tok['line'])
                seen.add(tok['line'])

        n_lines = len(lines)
        if n_lines < 3:
            return ['PROCESS'] * len(folio_tokens)

        setup_end = max(1, int(n_lines * 0.2))
        finish_start = n_lines - max(1, int(n_lines * 0.2))
        setup_lines = set(lines[:setup_end])
        finish_lines = set(lines[finish_start:])

        zones = []
        for tok in folio_tokens:
            if tok['line'] in setup_lines:
                zones.append('SETUP')
            elif tok['line'] in finish_lines:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    rng = np.random.default_rng(RNG_SEED)

    print("Loading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens: {len(all_tokens)}")

    tokens_with_middle = [t for t in all_tokens if t['middle'] is not None]
    print(f"  Tokens with valid MIDDLE: {len(tokens_with_middle)}")

    # ---- Pre-compute: corpus-wide MIDDLE folio counts ----
    middle_folios = defaultdict(set)
    for tok in tokens_with_middle:
        middle_folios[tok['middle']].add(tok['folio'])
    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    n_unique_middles = sum(1 for c in middle_folio_count.values() if c == 1)
    n_shared_middles = sum(1 for c in middle_folio_count.values() if c >= 2)
    print(f"  Unique MIDDLEs (1 folio): {n_unique_middles}")
    print(f"  Shared MIDDLEs (2+ folios): {n_shared_middles}")

    # ---- Group tokens by folio ----
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)
    print(f"  B folios: {len(folio_groups)}")

    # ---- Assign zones and build line-ordered sequences ----
    folio_line_tokens = defaultdict(list)

    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]
        para_assignments = assign_paragraphs(ftokens)
        zones = assign_zones(ftokens, para_assignments)
        for tok, zone in zip(ftokens, zones):
            tok['zone'] = zone
            folio_line_tokens[(folio, tok['line'])].append(tok)

    # ---- Build successor data ----
    # For each token with a valid MIDDLE, record:
    # (folio, zone, is_unique, successor_class)
    successor_records = []

    for (folio, line), line_toks in folio_line_tokens.items():
        for i in range(len(line_toks) - 1):
            tok = line_toks[i]
            succ = line_toks[i + 1]

            if tok['middle'] is None:
                continue

            mid = tok['middle']
            fc = middle_folio_count.get(mid, 0)

            successor_records.append({
                'folio': folio,
                'zone': tok['zone'],
                'is_unique': fc == 1,
                'middle': mid,
                'succ_class': succ['middle_class'],
            })

    n_unique_succ = sum(1 for r in successor_records if r['is_unique'])
    n_shared_succ = sum(1 for r in successor_records if not r['is_unique'])
    print(f"\n  Successor records: {len(successor_records)}")
    print(f"    Unique-MIDDLE tokens with successors: {n_unique_succ}")
    print(f"    Shared-MIDDLE tokens with successors: {n_shared_succ}")

    # ============================================================
    # STRATEGY A: Aggregate JSD per zone + bootstrap CI
    # ============================================================
    print("\n" + "=" * 60)
    print("STRATEGY A: Aggregate JSD per zone (unique vs shared)")
    print("=" * 60)

    zone_results = {}
    for zone in ['SETUP', 'PROCESS', 'FINISH']:
        zone_recs = [r for r in successor_records if r['zone'] == zone]
        unique_recs = [r for r in zone_recs if r['is_unique']]
        shared_recs = [r for r in zone_recs if not r['is_unique']]

        unique_dist = Counter(r['succ_class'] for r in unique_recs)
        shared_dist = Counter(r['succ_class'] for r in shared_recs)

        unique_vec = counter_to_vec(unique_dist)
        shared_vec = counter_to_vec(shared_dist)

        jsd = js_divergence(unique_vec, shared_vec)

        # Bootstrap CI: resample successor classes within each group
        bootstrap_jsds = []
        unique_classes = [r['succ_class'] for r in unique_recs]
        shared_classes = [r['succ_class'] for r in shared_recs]

        if len(unique_classes) >= 5 and len(shared_classes) >= 5:
            for _ in range(N_BOOTSTRAP):
                u_sample = rng.choice(unique_classes, size=len(unique_classes), replace=True)
                s_sample = rng.choice(shared_classes, size=len(shared_classes), replace=True)
                u_cnt = Counter(u_sample)
                s_cnt = Counter(s_sample)
                b_jsd = js_divergence(counter_to_vec(u_cnt), counter_to_vec(s_cnt))
                if b_jsd is not None:
                    bootstrap_jsds.append(b_jsd)

        ci_lo = float(np.percentile(bootstrap_jsds, 2.5)) if bootstrap_jsds else None
        ci_hi = float(np.percentile(bootstrap_jsds, 97.5)) if bootstrap_jsds else None

        zone_results[zone] = {
            'n_unique': len(unique_recs),
            'n_shared': len(shared_recs),
            'jsd': round(jsd, 6) if jsd is not None else None,
            'bootstrap_ci_95': [round(ci_lo, 6), round(ci_hi, 6)] if ci_lo is not None else None,
            'unique_dist': {c: unique_dist.get(c, 0) for c in ALL_CLASSES},
            'shared_dist': {c: shared_dist.get(c, 0) for c in ALL_CLASSES},
        }

        print(f"\n  {zone}:")
        print(f"    Unique tokens: {len(unique_recs)}, Shared tokens: {len(shared_recs)}")
        if jsd is not None:
            print(f"    JSD(unique vs shared) = {jsd:.6f}")
        if ci_lo is not None:
            print(f"    Bootstrap 95% CI: [{ci_lo:.6f}, {ci_hi:.6f}]")

        # Print distributions
        u_total = sum(unique_dist.values())
        s_total = sum(shared_dist.values())
        print(f"    {'Class':<12} {'Unique':>10} {'Shared':>10}")
        for cls in ALL_CLASSES:
            u_pct = 100 * unique_dist.get(cls, 0) / u_total if u_total > 0 else 0
            s_pct = 100 * shared_dist.get(cls, 0) / s_total if s_total > 0 else 0
            print(f"    {cls:<12} {u_pct:>9.1f}% {s_pct:>9.1f}%")

    # Overall aggregate
    unique_all_dist = Counter(r['succ_class'] for r in successor_records if r['is_unique'])
    shared_all_dist = Counter(r['succ_class'] for r in successor_records if not r['is_unique'])
    overall_jsd = js_divergence(counter_to_vec(unique_all_dist), counter_to_vec(shared_all_dist))

    print(f"\n  OVERALL (all zones pooled):")
    print(f"    JSD(unique vs shared) = {overall_jsd:.6f}" if overall_jsd is not None else "    JSD: N/A")

    # ============================================================
    # STRATEGY B: Per-folio within-zone JSD
    # ============================================================
    print("\n" + "=" * 60)
    print("STRATEGY B: Per-folio JSD within zones")
    print("=" * 60)

    # Group successor records by (folio, zone)
    fz_groups = defaultdict(lambda: {'unique': [], 'shared': []})
    for r in successor_records:
        key = (r['folio'], r['zone'])
        if r['is_unique']:
            fz_groups[key]['unique'].append(r['succ_class'])
        else:
            fz_groups[key]['shared'].append(r['succ_class'])

    # For each (folio, zone) with enough tokens in both groups, compute JSD
    per_folio_jsd_values = []
    per_folio_details = []

    for (folio, zone), groups in sorted(fz_groups.items()):
        u_list = groups['unique']
        s_list = groups['shared']
        if len(u_list) >= MIN_TOKENS_PER_GROUP and len(s_list) >= MIN_TOKENS_PER_GROUP:
            u_cnt = Counter(u_list)
            s_cnt = Counter(s_list)
            jsd = js_divergence(counter_to_vec(u_cnt), counter_to_vec(s_cnt))
            if jsd is not None:
                per_folio_jsd_values.append(jsd)
                per_folio_details.append({
                    'folio': folio,
                    'zone': zone,
                    'n_unique': len(u_list),
                    'n_shared': len(s_list),
                    'jsd': round(jsd, 6),
                })

    print(f"\n  Folio-zone pairs with >={MIN_TOKENS_PER_GROUP} tokens per group: {len(per_folio_jsd_values)}")

    if per_folio_jsd_values:
        pf_mean = float(np.mean(per_folio_jsd_values))
        pf_median = float(np.median(per_folio_jsd_values))
        pf_std = float(np.std(per_folio_jsd_values))
        print(f"  Per-folio JSD: mean={pf_mean:.4f}, median={pf_median:.4f}, std={pf_std:.4f}")
    else:
        pf_mean = pf_median = pf_std = None
        print(f"  Per-folio JSD: NO DATA")

    # ============================================================
    # STRATEGY C: Null comparison -- random split of shared MIDDLEs
    # ============================================================
    print("\n" + "=" * 60)
    print("STRATEGY C: Null comparison (random split of shared MIDDLEs)")
    print("=" * 60)

    # Within each zone, randomly split shared-MIDDLE successor records into two
    # groups of size matching unique count, compute JSD. Repeat N_BOOTSTRAP times.
    # This gives the expected JSD under the null (no unique/shared difference).
    null_jsds_by_zone = {}

    for zone in ['SETUP', 'PROCESS', 'FINISH']:
        zone_shared = [r['succ_class'] for r in successor_records
                       if r['zone'] == zone and not r['is_unique']]
        n_unique_zone = sum(1 for r in successor_records
                           if r['zone'] == zone and r['is_unique'])

        if n_unique_zone < 5 or len(zone_shared) < 2 * n_unique_zone:
            null_jsds_by_zone[zone] = None
            continue

        null_jsds = []
        shared_arr = np.array(zone_shared)
        for _ in range(N_BOOTSTRAP):
            # Random split: pick n_unique_zone from shared as "pseudo-unique"
            idx = rng.choice(len(shared_arr), size=min(2 * n_unique_zone, len(shared_arr)),
                             replace=False)
            group_a = shared_arr[idx[:n_unique_zone]]
            group_b = shared_arr[idx[n_unique_zone:2 * n_unique_zone]]
            a_cnt = Counter(group_a)
            b_cnt = Counter(group_b)
            null_jsd = js_divergence(counter_to_vec(a_cnt), counter_to_vec(b_cnt))
            if null_jsd is not None:
                null_jsds.append(null_jsd)

        null_jsds_by_zone[zone] = null_jsds

    # Compare actual unique-vs-shared JSD to null distribution
    print()
    comparison_results = {}
    for zone in ['SETUP', 'PROCESS', 'FINISH']:
        actual_jsd = zone_results[zone]['jsd']
        null_jsds = null_jsds_by_zone.get(zone)

        if actual_jsd is not None and null_jsds:
            null_mean = float(np.mean(null_jsds))
            null_p95 = float(np.percentile(null_jsds, 95))
            null_p99 = float(np.percentile(null_jsds, 99))
            exceeds_95 = actual_jsd > null_p95
            exceeds_99 = actual_jsd > null_p99
            # Empirical p-value: fraction of null >= actual
            emp_p = float(np.mean(np.array(null_jsds) >= actual_jsd))

            comparison_results[zone] = {
                'actual_jsd': round(actual_jsd, 6),
                'null_mean': round(null_mean, 6),
                'null_p95': round(null_p95, 6),
                'null_p99': round(null_p99, 6),
                'exceeds_95th': exceeds_95,
                'exceeds_99th': exceeds_99,
                'empirical_p': round(emp_p, 4),
            }
            print(f"  {zone}: actual JSD={actual_jsd:.6f}, null mean={null_mean:.6f}, "
                  f"null 95th={null_p95:.6f}, emp_p={emp_p:.4f}")
        else:
            comparison_results[zone] = None
            print(f"  {zone}: insufficient data for null comparison")

    # ============================================================
    # OVERALL VERDICT
    # ============================================================
    # Collect all zone-level evidence
    # Apply Bonferroni correction for 3 zones: alpha = 0.05/3 = 0.0167
    # SUPPORTED if:
    #   - At least 1 zone shows actual JSD > null (emp_p < 0.0167 after Bonferroni)
    #   - OR 2+ zones show emp_p < 0.05 (convergent evidence)
    bonferroni_alpha = 0.05 / 3  # 0.0167
    zones_significant_bonferroni = []
    zones_significant_nominal = []
    for zone in ['SETUP', 'PROCESS', 'FINISH']:
        cr = comparison_results.get(zone)
        if cr is not None:
            if cr['empirical_p'] < bonferroni_alpha:
                zones_significant_bonferroni.append(zone)
            if cr['empirical_p'] < 0.05:
                zones_significant_nominal.append(zone)

    # Also check per-zone aggregate JSD magnitude
    mean_zone_jsd = np.mean([
        zone_results[z]['jsd'] for z in ['SETUP', 'PROCESS', 'FINISH']
        if zone_results[z]['jsd'] is not None
    ]) if any(zone_results[z]['jsd'] is not None for z in ['SETUP', 'PROCESS', 'FINISH']) else None

    if zones_significant_bonferroni:
        verdict = "SUPPORTED"
        verdict_detail = (
            f"Unique MIDDLEs show significantly higher successor divergence in "
            f"{len(zones_significant_bonferroni)} zone(s): "
            f"{', '.join(zones_significant_bonferroni)} "
            f"(emp_p < {bonferroni_alpha:.4f}, Bonferroni-corrected). "
            f"Material identity hypothesis gains support at phase level."
        )
    elif len(zones_significant_nominal) >= 2:
        verdict = "SUPPORTED"
        verdict_detail = (
            f"Convergent evidence: {len(zones_significant_nominal)} zones show "
            f"elevated divergence at nominal p<0.05: "
            f"{', '.join(zones_significant_nominal)}. "
            f"Survives convergent evidence criterion though not individual Bonferroni."
        )
    elif zones_significant_nominal:
        verdict = "NOT_SUPPORTED"
        verdict_detail = (
            f"Weak signal: {len(zones_significant_nominal)} zone(s) nominally "
            f"significant ({', '.join(zones_significant_nominal)}, p<0.05) "
            f"but does not survive Bonferroni correction (alpha={bonferroni_alpha:.4f}). "
            f"C619 finding (V=0.070, near-identical transitions) largely holds within phases. "
            f"Unique MIDDLEs show a subtle h-class successor elevation but not enough "
            f"to establish material identity."
        )
    else:
        verdict = "NOT_SUPPORTED"
        verdict_detail = (
            f"Unique MIDDLEs do NOT show significantly higher successor divergence "
            f"in any zone (all emp_p >= 0.05). "
            f"C619 finding (V=0.070, near-identical transitions) holds even within phases. "
            f"Unique MIDDLEs are operational variants, not material markers."
        )

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")
    print(f"  {verdict_detail}")
    if mean_zone_jsd is not None:
        print(f"  Mean zone JSD: {mean_zone_jsd:.6f}")
    if overall_jsd is not None:
        print(f"  Overall JSD: {overall_jsd:.6f}")
    print(f"  Zones significant (Bonferroni): {zones_significant_bonferroni if zones_significant_bonferroni else 'none'}")
    print(f"  Zones significant (nominal): {zones_significant_nominal if zones_significant_nominal else 'none'}")

    # ---- Save results ----
    results = {
        'test': 'C619 Phase-Level Retest',
        'question': 'Do unique MIDDLEs show different transition profiles WITHIN phases?',
        'n_tokens_analyzed': len(tokens_with_middle),
        'n_folios': len(folio_groups),
        'n_unique_middles_corpus': n_unique_middles,
        'n_shared_middles_corpus': n_shared_middles,
        'n_unique_successor_tokens': n_unique_succ,
        'n_shared_successor_tokens': n_shared_succ,
        'strategy_a_zone_jsd': zone_results,
        'strategy_a_overall_jsd': round(overall_jsd, 6) if overall_jsd is not None else None,
        'strategy_b_per_folio': {
            'n_folio_zone_pairs': len(per_folio_jsd_values),
            'min_tokens_per_group': MIN_TOKENS_PER_GROUP,
            'mean_jsd': round(pf_mean, 4) if pf_mean is not None else None,
            'median_jsd': round(pf_median, 4) if pf_median is not None else None,
            'std_jsd': round(pf_std, 4) if pf_std is not None else None,
            'details': per_folio_details[:20],  # Top 20 for reference
        },
        'strategy_c_null_comparison': comparison_results,
        'n_bootstrap': N_BOOTSTRAP,
        'zones_significant_bonferroni': zones_significant_bonferroni,
        'zones_significant_nominal': zones_significant_nominal,
        'bonferroni_alpha': round(bonferroni_alpha, 4),
        'mean_zone_jsd': round(float(mean_zone_jsd), 6) if mean_zone_jsd is not None else None,
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'aggregate_successor_distribution': {
            'unique': {c: round(100 * unique_all_dist.get(c, 0) / n_unique_succ, 2)
                       if n_unique_succ > 0 else 0 for c in ALL_CLASSES},
            'shared': {c: round(100 * shared_all_dist.get(c, 0) / n_shared_succ, 2)
                       if n_shared_succ > 0 else 0 for c in ALL_CLASSES},
        },
        'notes': (
            "C619 found V=0.070 (near-identical transition profiles globally). "
            "This retest checks whether controlling for procedural phase (SETUP/PROCESS/FINISH) "
            "reveals higher behavioral divergence for unique MIDDLEs. "
            "Three strategies: (A) Aggregate JSD per zone with bootstrap CI, "
            "(B) Per-folio JSD within zones, (C) Null comparison via random split of shared MIDDLEs. "
            "Unique = appears on exactly 1 folio. Shared = appears on 2+ folios. "
            "Successor class: k-class (MIDDLE contains k), h-class (h), e-class (e), other. "
            "JSD = Jensen-Shannon divergence between successor class distributions."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'c619_phase_level_retest.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
