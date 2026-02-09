"""
13_cross_folio_material_consistency.py - Cross-Folio Material Consistency

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 13: Do folios with similar material profiles share more phase-exclusive tail middles?

Question: If tail middles encode materials, then folios performing similar procedures
(similar PP token profiles) should share more phase-exclusive tail vocabulary.

Method:
1. Load Currier B tokens (H track, labels excluded, uncertain excluded)
2. Extract MIDDLEs using canonical Morphology
3. Classify MIDDLEs as TAIL (rare: <15 folios) or COMMON (>=15 folios)
4. For each folio: assign zones (SETUP/PROCESS/FINISH) and identify zone-exclusive tail middles
5. Compute PP Jaccard between all folio pairs (PP = shared A+B middles via middle_classes.json)
6. Compute zone-exclusive tail middle Jaccard between all folio pairs
7. Spearman correlation between PP Jaccard and tail-middle Jaccard
8. Also test: same-section vs cross-section pairs

Verdict:
  SUPPORTED if Spearman r > 0.2 AND p < 0.05
  NOT_SUPPORTED if r <= 0.2 or p >= 0.05
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import math
from collections import defaultdict, Counter
from pathlib import Path
from itertools import combinations
from voynich import Transcript, Morphology

# scipy for correlation
from scipy.stats import spearmanr

# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RARITY_THRESHOLD = 15  # folios: <15 = TAIL/RARE, >=15 = COMMON
MIN_FOLIO_OCCURRENCES = 2  # exclude hapax per folio for zone-exclusivity


# ============================================================
# LOAD PP MIDDLE SET
# ============================================================
def load_pp_middles():
    """Load PP (shared A+B) middle set from classification data."""
    path = Path('C:/git/voynich/phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json')
    with open(path) as f:
        data = json.load(f)
    return set(data['a_shared_middles'])


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B text tokens with metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        # Text tokens only (P-prefixed placements)
        if not tok.placement.startswith('P'):
            continue

        m = morph.extract(tok.word)
        if m.middle is None or m.middle == '_EMPTY_':
            continue

        tokens.append({
            'word': tok.word,
            'middle': m.middle,
            'folio': tok.folio,
            'section': tok.section,
            'line': tok.line,
            'par_initial': tok.par_initial,
            'line_initial': tok.line_initial,
        })

    return tokens


# ============================================================
# PARAGRAPH BOUNDARY DETECTION (from Test 1)
# ============================================================
def assign_paragraphs(folio_tokens):
    """Assign paragraph numbers to tokens within a folio."""
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)

    return para_assignments


# ============================================================
# ZONE ASSIGNMENT (from Test 1)
# ============================================================
def assign_zones(folio_tokens, para_assignments):
    """
    Assign SETUP/PROCESS/FINISH zones.

    If 3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
    If 1-2 paragraphs: line-based 20/60/20 split
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
        # Line-based 20/60/20 split
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
# JACCARD HELPER
# ============================================================
def jaccard(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if len(union) == 0:
        return 0.0
    return len(set_a & set_b) / len(union)


# ============================================================
# MAIN ANALYSIS
# ============================================================
def main():
    print("=" * 70)
    print("TEST 13: CROSS-FOLIO MATERIAL CONSISTENCY")
    print("=" * 70)

    # Load PP middle set
    pp_middles = load_pp_middles()
    print(f"PP middles loaded: {len(pp_middles)}")

    # Load tokens
    print("\nLoading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    folio_section = {}
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)
        folio_section[tok['folio']] = tok['section']

    folios = sorted(folio_groups.keys())
    print(f"  B folios: {len(folios)}")

    # ---- Corpus-wide MIDDLE folio counts ----
    middle_folios = defaultdict(set)
    for tok in all_tokens:
        middle_folios[tok['middle']].add(tok['folio'])

    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    # Identify TAIL middles (rare: < RARITY_THRESHOLD folios)
    tail_middles = {m for m, c in middle_folio_count.items() if c < RARITY_THRESHOLD}
    common_middles = {m for m, c in middle_folio_count.items() if c >= RARITY_THRESHOLD}

    print(f"\n  TAIL middles (<{RARITY_THRESHOLD} folios): {len(tail_middles)}")
    print(f"  COMMON middles (>={RARITY_THRESHOLD} folios): {len(common_middles)}")

    # ---- Per-folio: zone-exclusive tail middles + PP token sets ----
    folio_zone_exclusive_tails = {}  # folio -> set of zone-exclusive tail middles
    folio_pp_tokens = {}             # folio -> set of PP token words (by PP middle membership)

    for folio in folios:
        ftokens = folio_groups[folio]

        # Assign paragraphs and zones
        para_assignments = assign_paragraphs(ftokens)
        zones = assign_zones(ftokens, para_assignments)

        # Track MIDDLE zone presence and frequency for this folio
        middle_zone_sets = defaultdict(set)  # middle -> set of zones
        middle_folio_freq = Counter()        # middle -> count on this folio

        for tok, zone in zip(ftokens, zones):
            mid = tok['middle']
            middle_zone_sets[mid].add(zone)
            middle_folio_freq[mid] += 1

        # Identify zone-exclusive tail middles
        # (tail middles with 2+ occurrences appearing in exactly 1 zone)
        exclusive_tails = set()
        for mid, freq in middle_folio_freq.items():
            if freq < MIN_FOLIO_OCCURRENCES:
                continue
            if mid not in tail_middles:
                continue
            if len(middle_zone_sets[mid]) == 1:
                exclusive_tails.add(mid)

        folio_zone_exclusive_tails[folio] = exclusive_tails

        # Collect PP tokens for this folio
        # A token is PP if its MIDDLE is in the PP (shared A+B) set
        pp_set = set()
        for tok in ftokens:
            if tok['middle'] in pp_middles:
                pp_set.add(tok['word'])

        folio_pp_tokens[folio] = pp_set

    # Report coverage
    folios_with_exclusive_tails = [f for f in folios if len(folio_zone_exclusive_tails[f]) > 0]
    folios_with_pp = [f for f in folios if len(folio_pp_tokens[f]) > 0]
    print(f"\n  Folios with zone-exclusive tail middles: {len(folios_with_exclusive_tails)}")
    print(f"  Folios with PP tokens: {len(folios_with_pp)}")

    # ---- Pairwise comparisons ----
    # Only use folios that have BOTH zone-exclusive tails AND PP tokens
    usable_folios = sorted(set(folios_with_exclusive_tails) & set(folios_with_pp))
    print(f"  Usable folios (have both): {len(usable_folios)}")

    pp_jaccards = []
    tail_jaccards = []
    pair_labels = []

    for f1, f2 in combinations(usable_folios, 2):
        pp_j = jaccard(folio_pp_tokens[f1], folio_pp_tokens[f2])
        tail_j = jaccard(folio_zone_exclusive_tails[f1], folio_zone_exclusive_tails[f2])

        pp_jaccards.append(pp_j)
        tail_jaccards.append(tail_j)
        pair_labels.append((f1, f2))

    n_pairs = len(pp_jaccards)
    print(f"\n  Total folio pairs: {n_pairs}")

    # ---- Spearman correlation ----
    if n_pairs >= 10:
        rho, p_value = spearmanr(pp_jaccards, tail_jaccards)
    else:
        rho, p_value = 0.0, 1.0
        print("  WARNING: Too few pairs for reliable correlation")

    print(f"\n=== PRIMARY RESULT ===")
    print(f"  Spearman rho (PP Jaccard vs tail-middle Jaccard): {rho:.4f}")
    print(f"  p-value: {p_value:.2e}")
    print(f"  N pairs: {n_pairs}")

    # ---- Descriptive statistics ----
    mean_pp_j = sum(pp_jaccards) / len(pp_jaccards) if pp_jaccards else 0
    mean_tail_j = sum(tail_jaccards) / len(tail_jaccards) if tail_jaccards else 0

    # Count non-zero entries
    nonzero_pp = sum(1 for j in pp_jaccards if j > 0)
    nonzero_tail = sum(1 for j in tail_jaccards if j > 0)

    print(f"\n  Mean PP Jaccard: {mean_pp_j:.4f}")
    print(f"  Mean tail-middle Jaccard: {mean_tail_j:.4f}")
    print(f"  Non-zero PP pairs: {nonzero_pp}/{n_pairs} ({100*nonzero_pp/n_pairs:.1f}%)")
    print(f"  Non-zero tail pairs: {nonzero_tail}/{n_pairs} ({100*nonzero_tail/n_pairs:.1f}%)")

    # ---- Same-section vs cross-section breakdown ----
    print(f"\n=== SECTION BREAKDOWN ===")
    within_pp = []
    within_tail = []
    between_pp = []
    between_tail = []

    for (f1, f2), pp_j, tail_j in zip(pair_labels, pp_jaccards, tail_jaccards):
        if folio_section[f1] == folio_section[f2]:
            within_pp.append(pp_j)
            within_tail.append(tail_j)
        else:
            between_pp.append(pp_j)
            between_tail.append(tail_j)

    mean_within_pp = sum(within_pp) / len(within_pp) if within_pp else 0
    mean_within_tail = sum(within_tail) / len(within_tail) if within_tail else 0
    mean_between_pp = sum(between_pp) / len(between_pp) if between_pp else 0
    mean_between_tail = sum(between_tail) / len(between_tail) if between_tail else 0

    print(f"  WITHIN-section pairs: {len(within_pp)}")
    print(f"    Mean PP Jaccard: {mean_within_pp:.4f}")
    print(f"    Mean tail Jaccard: {mean_within_tail:.4f}")
    print(f"  BETWEEN-section pairs: {len(between_pp)}")
    print(f"    Mean PP Jaccard: {mean_between_pp:.4f}")
    print(f"    Mean tail Jaccard: {mean_between_tail:.4f}")

    # Within-section correlation
    if len(within_pp) >= 10:
        rho_within, p_within = spearmanr(within_pp, within_tail)
    else:
        rho_within, p_within = 0.0, 1.0

    # Between-section correlation
    if len(between_pp) >= 10:
        rho_between, p_between = spearmanr(between_pp, between_tail)
    else:
        rho_between, p_between = 0.0, 1.0

    print(f"\n  Within-section Spearman rho: {rho_within:.4f} (p={p_within:.2e}, n={len(within_pp)})")
    print(f"  Between-section Spearman rho: {rho_between:.4f} (p={p_between:.2e}, n={len(between_pp)})")

    # ---- Also compute using MIDDLE-vocabulary Jaccard as alternate PP proxy ----
    print(f"\n=== ALTERNATE: Full MIDDLE Vocabulary Jaccard as Profile Proxy ===")

    folio_all_middles = {}
    for folio in usable_folios:
        folio_all_middles[folio] = {tok['middle'] for tok in folio_groups[folio]}

    vocab_jaccards = []
    for f1, f2 in combinations(usable_folios, 2):
        vocab_jaccards.append(jaccard(folio_all_middles[f1], folio_all_middles[f2]))

    if n_pairs >= 10:
        rho_vocab, p_vocab = spearmanr(vocab_jaccards, tail_jaccards)
    else:
        rho_vocab, p_vocab = 0.0, 1.0

    print(f"  Spearman rho (vocab Jaccard vs tail-middle Jaccard): {rho_vocab:.4f}")
    print(f"  p-value: {p_vocab:.2e}")

    # ---- Top sharing pairs (for interpretability) ----
    print(f"\n=== TOP 10 FOLIO PAIRS BY TAIL-MIDDLE SHARING ===")
    paired = list(zip(pair_labels, tail_jaccards, pp_jaccards))
    paired.sort(key=lambda x: x[1], reverse=True)
    top_pairs = []
    for (f1, f2), tj, pj in paired[:10]:
        shared = folio_zone_exclusive_tails[f1] & folio_zone_exclusive_tails[f2]
        same_sec = folio_section[f1] == folio_section[f2]
        top_pairs.append({
            'folio_1': f1,
            'folio_2': f2,
            'tail_jaccard': round(tj, 4),
            'pp_jaccard': round(pj, 4),
            'same_section': same_sec,
            'shared_tail_middles': sorted(shared),
            'n_shared': len(shared),
        })
        sec_marker = "SAME" if same_sec else "DIFF"
        print(f"  {f1} - {f2}: tail_J={tj:.4f}, pp_J={pj:.4f}, "
              f"shared={len(shared)}, sec={sec_marker}")

    # ---- Verdict ----
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")

    if p_value < 0.05 and rho > 0.2:
        verdict = "SUPPORTED"
        interpretation = (
            f"Positive correlation (rho={rho:.4f}, p={p_value:.2e}) between PP similarity "
            f"and zone-exclusive tail sharing. Folios with similar procedural profiles "
            f"share more phase-exclusive tail vocabulary, consistent with material identity encoding."
        )
    elif p_value < 0.05 and rho > 0:
        verdict = "WEAK"
        interpretation = (
            f"Statistically significant but weak correlation (rho={rho:.4f}, p={p_value:.2e}). "
            f"Some association between procedural similarity and tail sharing, but below "
            f"the r>0.2 threshold for material-encoding support."
        )
    else:
        verdict = "NOT_SUPPORTED"
        interpretation = (
            f"No significant positive correlation (rho={rho:.4f}, p={p_value:.2e}). "
            f"Tail vocabulary sharing is not driven by procedural profile similarity. "
            f"Consistent with operational phase-specificity rather than material identity."
        )

    print(f"  Verdict: {verdict}")
    print(f"  {interpretation}")

    # ---- Assemble notes ----
    notes = (
        f"PP tokens defined as B tokens whose MIDDLE is in the A+B shared set "
        f"(n={len(pp_middles)} PP middles). "
        f"Zone-exclusive tail middles: TAIL middles (<{RARITY_THRESHOLD} folios) appearing "
        f"in exactly 1 zone per folio with 2+ occurrences. "
        f"Zones: SETUP (1st paragraph), PROCESS (middle), FINISH (last paragraph). "
        f"Alternate full-vocabulary proxy: rho={rho_vocab:.4f} (p={p_vocab:.2e})."
    )

    # ---- Save results ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "test": "Cross-Folio Material Consistency",
        "test_number": 13,
        "question": "Do folios with similar material profiles share more phase-exclusive tail middles?",
        "n_folios_total": len(folios),
        "n_usable_folios": len(usable_folios),
        "n_pairs": n_pairs,
        "n_tail_middles": len(tail_middles),
        "n_pp_middles_loaded": len(pp_middles),
        "rarity_threshold": RARITY_THRESHOLD,
        "primary_result": {
            "spearman_rho": round(rho, 4),
            "p_value": float(f'{p_value:.2e}'),
            "p_value_str": f'{p_value:.2e}',
        },
        "descriptive": {
            "mean_pp_jaccard": round(mean_pp_j, 6),
            "mean_tail_jaccard": round(mean_tail_j, 6),
            "nonzero_pp_pairs": nonzero_pp,
            "nonzero_tail_pairs": nonzero_tail,
            "pct_nonzero_pp": round(100 * nonzero_pp / n_pairs, 1) if n_pairs > 0 else 0,
            "pct_nonzero_tail": round(100 * nonzero_tail / n_pairs, 1) if n_pairs > 0 else 0,
        },
        "section_breakdown": {
            "within_section_pairs": len(within_pp),
            "between_section_pairs": len(between_pp),
            "within_mean_pp_jaccard": round(mean_within_pp, 6),
            "within_mean_tail_jaccard": round(mean_within_tail, 6),
            "between_mean_pp_jaccard": round(mean_between_pp, 6),
            "between_mean_tail_jaccard": round(mean_between_tail, 6),
            "within_spearman_rho": round(rho_within, 4),
            "within_p_value": float(f'{p_within:.2e}'),
            "between_spearman_rho": round(rho_between, 4),
            "between_p_value": float(f'{p_between:.2e}'),
        },
        "alternate_vocab_proxy": {
            "spearman_rho": round(rho_vocab, 4),
            "p_value": float(f'{p_vocab:.2e}'),
            "p_value_str": f'{p_vocab:.2e}',
        },
        "top_sharing_pairs": top_pairs,
        "verdict": verdict,
        "interpretation": interpretation,
        "notes": notes,
    }

    output_path = RESULTS_DIR / 'cross_folio_material_consistency.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
