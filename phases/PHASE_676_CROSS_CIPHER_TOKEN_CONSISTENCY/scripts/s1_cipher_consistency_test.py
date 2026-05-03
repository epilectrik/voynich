"""
Phase 676 Script 1: Cross-cipher token consistency test.

The "must-be-true" question:
  The Pseudo-Lull source uses 4 cipher systems (Part II A-H, Part III B-G,
  Tavola 2 mirror-script, Practica). Same letter symbols mean different
  substances across parts ("B" = mercury in Part II, "B" = simple water in
  Part III). Our matched folios split:

    Part II:  f76r, f84r (n=2)
    Part III: f75r, f79r, f82r, f76v, f81v, f112v, f103r, f116r, f112r (n=9)

  The Voynich uses ONE cipher system (C1976). The matching catalog implicitly
  assumes Voynich tokens carry CIPHER-INVARIANT operational meaning: 'qo' is
  thermal injection regardless of whether the source-passage was Part II
  (mercury) or Part III (water). C171, C1394, C1976 all predict this.

  HAS NEVER BEEN DIRECTLY TESTED.

PRE-REGISTERED HYPOTHESIS:
  Frequent Voynich tokens have similar operational profiles on Part-II-matched
  folios and on REGIME/Section-matched Part-III-matched folios.

  Expert-advisor flagged the trap: f76r/f84r are both REGIME_1/Section B.
  A naive Part-II vs Part-III comparison would confound cipher with REGIME.
  Required control: stratify Part-III into Section-B subset (REGIME-matched
  to f76r/f84r) and compare specifically against that subset.

PRIMARY TEST:
  For each Voynich token X with frequency >= 5 in BOTH Part II folios pooled
  AND Part III Section-B folios pooled:
    - Compute per-token operational profile: (mean line position, mean e-depth,
      terminal-y rate, kernel-e rate)
    - Distance = |Part II profile - Part III Section-B profile|
  Aggregate mean distance across tokens.
  Compare to within-Part-III random-split null (10k splits).

FALSIFICATION:
  Between-part mean distance > within-Part-III random-split distance at
  p < 0.05 -> tokens have substance-coupled meaning -> matching catalog
  downgrade.

  Between-part distance ~= within-Part-III distance -> cipher-invariant
  assumption holds -> foundation confirmed (Tier 2 candidate).

OUTPUT: phases/PHASE_676_CROSS_CIPHER_TOKEN_CONSISTENCY/results/
        cipher_consistency.json
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "cipher_consistency.json"

# Phase 668 + memory-derived assignment
PART_II_FOLIOS = ["f76r", "f84r"]  # Both Section B (Biological), both REGIME_1
PART_III_ALL = ["f75r", "f79r", "f82r", "f76v", "f81v", "f112v", "f103r", "f116r", "f112r"]
# Section B subset (REGIME-matched to f76r/f84r): f75r, f79r, f82r, f76v, f81v
PART_III_B_SECTION = ["f75r", "f79r", "f82r", "f76v", "f81v"]
PART_III_S_SECTION = ["f112v", "f103r", "f116r", "f112r"]


def gather_token_instances(folios, b_tokens, morph):
    """For each folio, collect token instances with operational features.

    Returns dict: folio -> list of {word, position, e_depth, term, head, prefix}
    """
    by_folio = defaultdict(list)
    by_folio_lines = defaultdict(lambda: defaultdict(list))

    # First, group by folio and line
    for t in b_tokens:
        if t.folio not in folios:
            continue
        if "*" in t.word or not t.word.strip() or t.is_label:
            continue
        by_folio_lines[t.folio][t.line].append(t)

    for folio, lines in by_folio_lines.items():
        for line_id, tokens_in_line in lines.items():
            n = len(tokens_in_line)
            if n < 4:
                continue
            # Body-only: skip first line of paragraph
            if tokens_in_line[0].par_initial:
                continue
            for i, t in enumerate(tokens_in_line):
                pos = i / (n - 1) if n > 1 else 0.5
                a = morph.atomize(t.word)
                head_char = None
                term_char = None
                if a.atoms:
                    h, hr, _ = a.atoms[0]
                    if hr == "HEAD":
                        head_char = h
                    tc, tr, _ = a.atoms[-1]
                    if tr == "TERM":
                        term_char = tc
                by_folio[folio].append({
                    "word": t.word, "position": pos, "e_depth": a.e_depth,
                    "term": term_char, "head": head_char, "prefix": a.prefix or "BARE",
                })
    return by_folio


def token_profile(instances):
    """Compute operational profile vector for a list of token instances."""
    if not instances:
        return None
    n = len(instances)
    return {
        "n": n,
        "mean_position": mean(i["position"] for i in instances),
        "mean_edepth": mean(i["e_depth"] for i in instances),
        "term_y_rate": sum(1 for i in instances if i["term"] == "y") / n,
        "term_n_rate": sum(1 for i in instances if i["term"] == "n") / n,
        "term_r_rate": sum(1 for i in instances if i["term"] == "r") / n,
        "head_e_rate": sum(1 for i in instances if i["head"] == "e") / n,
        "head_a_rate": sum(1 for i in instances if i["head"] == "a") / n,
    }


def profile_distance(p1, p2):
    """Sum of absolute differences across profile features."""
    if p1 is None or p2 is None:
        return None
    keys = ["mean_position", "mean_edepth", "term_y_rate", "term_n_rate",
            "term_r_rate", "head_e_rate", "head_a_rate"]
    return sum(abs(p1[k] - p2[k]) for k in keys)


def pooled_token_instances(folios_instances):
    """Pool token instances across multiple folios.

    Returns: word -> list of instance dicts
    """
    by_word = defaultdict(list)
    for folio, instances in folios_instances.items():
        for inst in instances:
            by_word[inst["word"]].append(inst)
    return by_word


def main():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    all_target = PART_II_FOLIOS + PART_III_ALL
    folio_instances = gather_token_instances(all_target, b_tokens, morph)
    for f in all_target:
        print(f"  {f:<8}: {len(folio_instances.get(f, []))} body tokens")

    # Pool by group
    p2_pool = pooled_token_instances({f: folio_instances[f] for f in PART_II_FOLIOS if f in folio_instances})
    p3b_pool = pooled_token_instances({f: folio_instances[f] for f in PART_III_B_SECTION if f in folio_instances})
    p3s_pool = pooled_token_instances({f: folio_instances[f] for f in PART_III_S_SECTION if f in folio_instances})
    p3_all_pool = pooled_token_instances({f: folio_instances[f] for f in PART_III_ALL if f in folio_instances})

    # Find tokens with >=5 instances in BOTH Part II and Part III B-section
    common_tokens_B = set()
    for word in p2_pool:
        if len(p2_pool[word]) >= 5 and word in p3b_pool and len(p3b_pool[word]) >= 5:
            common_tokens_B.add(word)
    print(f"\nTokens with n>=5 in BOTH Part II and Part III B-section: {len(common_tokens_B)}")

    # Same for Part III S-section
    common_tokens_S = set()
    for word in p2_pool:
        if len(p2_pool[word]) >= 5 and word in p3s_pool and len(p3s_pool[word]) >= 5:
            common_tokens_S.add(word)
    print(f"Tokens with n>=5 in BOTH Part II and Part III S-section: {len(common_tokens_S)}")

    # Compute per-token Part II vs Part III-B distances
    print("\n=== TOKEN PROFILES: Part II vs Part III B-section (REGIME-matched) ===")
    print(f"  {'Token':<14} {'n_p2':>5} {'n_p3b':>6} {'d_pos':>7} {'d_edep':>7} {'d_total':>8}")
    rows = []
    for word in sorted(common_tokens_B, key=lambda w: -len(p2_pool[w])):
        p2_prof = token_profile(p2_pool[word])
        p3b_prof = token_profile(p3b_pool[word])
        d = profile_distance(p2_prof, p3b_prof)
        d_pos = abs(p2_prof["mean_position"] - p3b_prof["mean_position"])
        d_edep = abs(p2_prof["mean_edepth"] - p3b_prof["mean_edepth"])
        rows.append({
            "word": word, "n_p2": p2_prof["n"], "n_p3b": p3b_prof["n"],
            "d_pos": d_pos, "d_edep": d_edep, "d_total": d,
            "p2_pos": p2_prof["mean_position"], "p3b_pos": p3b_prof["mean_position"],
            "p2_edep": p2_prof["mean_edepth"], "p3b_edep": p3b_prof["mean_edepth"],
        })
    for r in rows[:30]:
        print(f"  {r['word']:<14} {r['n_p2']:>5} {r['n_p3b']:>6} {r['d_pos']:>7.3f} {r['d_edep']:>7.3f} {r['d_total']:>8.3f}")
    if len(rows) > 30:
        print(f"  ... and {len(rows)-30} more")

    if not rows:
        print("\nNo common tokens with sufficient frequency. Cannot run test.")
        return

    actual_mean_distance_B = mean(r["d_total"] for r in rows)
    actual_mean_dpos_B = mean(r["d_pos"] for r in rows)
    actual_mean_dedep_B = mean(r["d_edep"] for r in rows)
    print(f"\n  Mean total profile distance (Part II vs Part III B-sec): {actual_mean_distance_B:.4f}")
    print(f"  Mean position diff: {actual_mean_dpos_B:.4f}")
    print(f"  Mean e-depth diff: {actual_mean_dedep_B:.4f}")

    # === PERMUTATION NULL: within-Part III random splits ===
    print("\n=== PERMUTATION NULL: within-Part III B-section random splits ===")
    p3b_folios_present = [f for f in PART_III_B_SECTION if f in folio_instances]
    if len(p3b_folios_present) < 4:
        print(f"  Need at least 4 Part-III B-section folios for split test, got {len(p3b_folios_present)}")
    else:
        n_perm = 10000
        # Pre-aggregate per-folio token instances
        p3b_per_folio = {f: defaultdict(list) for f in p3b_folios_present}
        for f in p3b_folios_present:
            for inst in folio_instances[f]:
                p3b_per_folio[f][inst["word"]].append(inst)

        random_distances = []
        for _ in range(n_perm):
            # Random split of B-section folios into 2 halves
            shuffled = p3b_folios_present[:]
            random.shuffle(shuffled)
            half = len(shuffled) // 2
            group_a = shuffled[:half]
            group_b = shuffled[half:half * 2]
            # Pool tokens per group
            a_pool = defaultdict(list)
            b_pool = defaultdict(list)
            for f in group_a:
                for w, insts in p3b_per_folio[f].items():
                    a_pool[w].extend(insts)
            for f in group_b:
                for w, insts in p3b_per_folio[f].items():
                    b_pool[w].extend(insts)
            # Distances on common tokens (n>=5 in both)
            ds = []
            for w in a_pool:
                if len(a_pool[w]) >= 5 and w in b_pool and len(b_pool[w]) >= 5:
                    da = profile_distance(token_profile(a_pool[w]), token_profile(b_pool[w]))
                    ds.append(da)
            if ds:
                random_distances.append(mean(ds))

        if random_distances:
            null_mean = mean(random_distances)
            null_extreme = sum(1 for d in random_distances if d >= actual_mean_distance_B) / len(random_distances)
            print(f"  Random within-P3B split mean distance: {null_mean:.4f}")
            print(f"  p(actual >= within-P3B random): {null_extreme:.4f}")
        else:
            null_mean = None

    # === SECONDARY: Part II vs Part III S-section (REGIME-mismatched control) ===
    print("\n=== Part II vs Part III S-section (REGIME-MISMATCHED — section confound check) ===")
    rows_s = []
    for word in common_tokens_S:
        p2_prof = token_profile(p2_pool[word])
        p3s_prof = token_profile(p3s_pool[word])
        d = profile_distance(p2_prof, p3s_prof)
        rows_s.append({"word": word, "d_total": d,
                       "n_p2": p2_prof["n"], "n_p3s": p3s_prof["n"]})
    if rows_s:
        actual_mean_distance_S = mean(r["d_total"] for r in rows_s)
        print(f"  Mean total profile distance (Part II vs Part III S-sec): {actual_mean_distance_S:.4f}")
        print(f"  N common tokens: {len(rows_s)}")
        print(f"  Compare to Part II vs Part III B-sec: {actual_mean_distance_B:.4f}")
        print(f"  If section-confound dominates: P3S distance >> P3B distance")
    else:
        actual_mean_distance_S = None

    # === VERDICT ===
    print("\n=== VERDICT ===")
    if null_mean is not None:
        if null_extreme > 0.05:
            verdict = "CIPHER-INVARIANT (foundation confirmed)"
            print(f"  Part II vs Part III B-sec distance ({actual_mean_distance_B:.4f}) is NOT")
            print(f"  significantly larger than within-P3B random split ({null_mean:.4f})")
            print(f"  -> Voynich tokens are operationally invariant to source cipher context.")
            print(f"  -> Foundation of matching program confirmed.")
        else:
            verdict = "SUBSTANCE-COUPLED (matching catalog downgrade)"
            print(f"  Part II vs Part III B-sec distance ({actual_mean_distance_B:.4f}) is")
            print(f"  significantly larger than within-P3B random split ({null_mean:.4f}, p={null_extreme:.4f})")
            print(f"  -> Voynich tokens have substance-coupled meaning across cipher contexts.")
            print(f"  -> Matching catalog needs Part II vs Part III stratification.")
    else:
        verdict = "INSUFFICIENT DATA"
        print(f"  Cannot adjudicate — insufficient data for permutation null.")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "preregistered_hypothesis": "Voynich tokens are cipher-invariant (Part II profile == Part III B-sec profile)",
        "n_common_tokens_B": len(rows),
        "n_common_tokens_S": len(rows_s),
        "actual_mean_distance_part_II_vs_III_B": actual_mean_distance_B,
        "actual_mean_distance_part_II_vs_III_S": actual_mean_distance_S,
        "null_mean_within_p3b": null_mean if null_mean is not None else None,
        "p_value": null_extreme if null_mean is not None else None,
        "verdict": verdict,
        "per_token_distances_B": rows,
        "per_token_distances_S": rows_s,
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
