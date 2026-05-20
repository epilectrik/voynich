"""
PHASE_710: Monocategorical-operational vocabulary discrimination test.

Measure inventory size (N) and categorical homogeneity (H) for each system's
primitive vocabulary. Compare Voynich atom inventory against:
  - Procedural-DSL positive controls (Forth CORE, x86 base)
  - Floor control (mensural duration classes — small inventory, ENTITY-dominant)
  - NL morpheme/word baseline (Latin top-50 from Codicillus)

Pre-registered decision rules in PHASE_710 INDEX.md.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
PHASE_DIR = ROOT / 'phases' / 'PHASE_710_MONOCATEGORICAL_VOCABULARY'
REFS_PATH = PHASE_DIR / 'reference_data' / 'reference_inventories.json'
OUT_PATH = PHASE_DIR / 'results' / 'monocategorical_results.json'


def inventory_stats(items_dict, strict_category=None, dominant_only=True):
    """For an items dict {symbol: {category, ...}}, compute N, category counts,
    H_dominant, H_target (if strict_category given).

    Args:
        items_dict: {symbol: {"category": str, ...}}
        strict_category: if set, compute H against this specific category
        dominant_only: if True, treat AMBIGUOUS_OP_* as their dominant op-side
                       in the "inclusive" tally
    """
    n = len(items_dict)
    if n == 0:
        return {"N": 0, "categories": {}, "H_dominant": 0.0, "dominant_category": None}

    # Strict tally: keep ambiguous categories separate
    strict_cats = Counter(it["category"] for it in items_dict.values())

    # Inclusive tally: collapse AMBIGUOUS_OP_* into OPERATION (lenient reading)
    inclusive_cats = Counter()
    for it in items_dict.values():
        cat = it["category"]
        if cat.startswith("AMBIGUOUS_OP_"):
            inclusive_cats["OPERATION"] += 1
        else:
            inclusive_cats[cat] += 1

    # Dominant category and its share
    dominant_strict, dom_count_strict = strict_cats.most_common(1)[0]
    h_dominant_strict = dom_count_strict / n

    dominant_inclusive, dom_count_inclusive = inclusive_cats.most_common(1)[0]
    h_dominant_inclusive = dom_count_inclusive / n

    out = {
        "N": n,
        "strict_categories": dict(strict_cats),
        "inclusive_categories": dict(inclusive_cats),
        "dominant_category_strict": dominant_strict,
        "H_dominant_strict": h_dominant_strict,
        "dominant_category_inclusive": dominant_inclusive,
        "H_dominant_inclusive": h_dominant_inclusive,
    }
    if strict_category:
        h_target = strict_cats.get(strict_category, 0) / n
        h_target_inclusive = inclusive_cats.get(strict_category, 0) / n
        out["H_target_category_strict"] = h_target
        out["H_target_category_inclusive"] = h_target_inclusive
        out["target_category"] = strict_category
    return out


def voynich_ambiguity_audit(voynich_items):
    """Step 0: how many Voynich atoms are AMBIGUOUS_OP_*?"""
    op_pure = 0
    ambiguous = []
    other = []
    for sym, it in voynich_items.items():
        cat = it["category"]
        if cat == "OPERATION":
            op_pure += 1
        elif cat.startswith("AMBIGUOUS_OP_"):
            ambiguous.append((sym, it["gloss"], cat))
        else:
            other.append((sym, it["gloss"], cat))
    return {
        "n_atoms": len(voynich_items),
        "n_operation_pure": op_pure,
        "n_ambiguous_operation": len(ambiguous),
        "n_other": len(other),
        "ambiguous_atoms": ambiguous,
        "other_atoms": other,
        "h_operation_strict": op_pure / len(voynich_items),
        "h_operation_inclusive": (op_pure + len(ambiguous)) / len(voynich_items),
    }


def evaluate_verdict(voynich_stats, controls, audit):
    """Apply the pre-registered decision rules.

    Axis 1: H_dominant_inclusive ≥ 0.85 for Voynich on OPERATION
    Axis 2: matches ≥2 positive controls on (N small AND H high AND OP-dominant)
    Axis 3: differs from mensural (high H but ENTITY) and from NL Latin (low H or large N)
    """
    voy_h_inclusive = voynich_stats["H_target_category_inclusive"]
    voy_h_strict = voynich_stats["H_target_category_strict"]
    voy_n = voynich_stats["N"]

    # Axis 1
    axis1_pass = voy_h_inclusive >= 0.85
    axis1_pass_strict = voy_h_strict >= 0.85

    # Axis 2: positive controls
    pos_controls = ["forth_core_words", "x86_base_instructions"]
    pos_matches = 0
    pos_match_details = []
    for c in pos_controls:
        s = controls.get(c)
        if s is None:
            continue
        match = (
            s["N"] >= 30 and s["N"] <= 300 and  # comparable inventory size range
            s["H_dominant_inclusive"] >= 0.85 and
            s["dominant_category_inclusive"] == "OPERATION"
        )
        if match:
            pos_matches += 1
        pos_match_details.append({
            "corpus": c,
            "N": s["N"],
            "H_dominant_inclusive": s["H_dominant_inclusive"],
            "dominant": s["dominant_category_inclusive"],
            "matches": match,
        })
    axis2_pass = pos_matches >= 2

    # Axis 3: mensural and NL distinction
    mens = controls.get("mensural_durations", {})
    nl = controls.get("latin_top50_codicillus", {})

    # Voynich should NOT match mensural pattern (mensural is small-N, high-H, but ENTITY)
    mens_pattern_avoided = (
        mens.get("dominant_category_inclusive") != "OPERATION" or
        mens.get("dominant_category_inclusive") == voynich_stats["dominant_category_inclusive"]
    )
    # The cleaner check: mensural's H_dominant_inclusive for OPERATION should be near 0
    mens_op_h = mens.get("inclusive_categories", {}).get("OPERATION", 0) / max(mens.get("N", 1), 1)
    mens_distinct = mens_op_h < 0.30

    # Voynich should differ from NL: NL should have mixed categories (lower H_dominant
    # OR larger N AND non-OPERATION dominant)
    nl_h_op_inclusive = nl.get("inclusive_categories", {}).get("OPERATION", 0) / max(nl.get("N", 1), 1)
    nl_h_dominant = nl.get("H_dominant_inclusive", 1.0)
    nl_distinct = (nl_h_dominant < 0.50) or (nl.get("dominant_category_inclusive") != "OPERATION")

    axis3_pass = mens_distinct and nl_distinct

    # Verdict matrix
    if not axis1_pass:
        verdict = "MONOCATEGORICAL CLAIM FALSIFIED"
        rationale = (f"Voynich H_inclusive for OPERATION = {voy_h_inclusive:.2%} < 0.85. "
                     f"Strict (no ambiguous): {voy_h_strict:.2%}. Pre-registration threshold not met.")
    elif axis1_pass and axis2_pass and axis3_pass:
        verdict = "PROCEDURAL-DSL SIGNATURE CONFIRMED"
        rationale = (f"All three axes pass: Voynich H_OP_inclusive={voy_h_inclusive:.2%}, "
                     f"matches {pos_matches}/2 positive controls, "
                     f"distinguished from mensural (OP-H={mens_op_h:.2%}) and NL (dominant-H={nl_h_dominant:.2%}, "
                     f"dominant={nl.get('dominant_category_inclusive')}).")
    elif axis1_pass and not axis3_pass and mens_op_h >= 0.30:
        verdict = "FLOOR — small-N+high-H is generic for small-inventory-symbolic systems"
        rationale = (f"Voynich passes axes 1+2 but mensural ALSO shows OPERATION dominance (H={mens_op_h:.2%}). "
                     f"Small inventory size + categorical homogeneity is a floor signature, not procedural-DSL discriminator.")
    elif axis1_pass and not axis2_pass:
        verdict = "UNIQUE SIGNATURE — Voynich isn't on procedural-DSL spectrum but isn't NL either"
        rationale = (f"Voynich passes axis 1 (H={voy_h_inclusive:.2%}) and axis 3 (distinct from mensural+NL) "
                     f"but matches only {pos_matches}/2 procedural-DSL positive controls. Voynich is sui generis.")
    else:
        verdict = "MIXED — partial pattern match; document and design follow-up"
        rationale = (f"Axis 1 pass={axis1_pass}, Axis 2 pass={axis2_pass} ({pos_matches}/2 controls), "
                     f"Axis 3 pass={axis3_pass}.")

    return {
        "verdict": verdict,
        "rationale": rationale,
        "axis1_pass_inclusive": axis1_pass,
        "axis1_pass_strict": axis1_pass_strict,
        "axis2_pass": axis2_pass,
        "axis3_pass": axis3_pass,
        "axis2_details": pos_match_details,
        "voynich_h_op_inclusive": voy_h_inclusive,
        "voynich_h_op_strict": voy_h_strict,
        "mensural_op_h_inclusive": mens_op_h,
        "nl_dominant_h": nl_h_dominant,
        "nl_op_h_inclusive": nl_h_op_inclusive,
    }


def main():
    print("=" * 90)
    print("PHASE_710 MONOCATEGORICAL-OPERATIONAL VOCABULARY TEST")
    print("=" * 90)

    refs = json.loads(REFS_PATH.read_text(encoding='utf-8'))

    # ---- Step 0: Ambiguity audit ----
    print("\n--- Step 0: Voynich atom ambiguity audit ---")
    voy_items = refs["voynich_atoms"]["items"]
    audit = voynich_ambiguity_audit(voy_items)
    print(f"  Total atoms: {audit['n_atoms']}")
    print(f"  Operation-pure: {audit['n_operation_pure']}")
    print(f"  Ambiguous (operation-or-entity / operation-or-property): {audit['n_ambiguous_operation']}")
    if audit['ambiguous_atoms']:
        print("    Ambiguous list:")
        for sym, gl, cat in audit['ambiguous_atoms']:
            print(f"      {sym} ({gl}) -> {cat}")
    print(f"  Other category: {audit['n_other']}")
    if audit['other_atoms']:
        for sym, gl, cat in audit['other_atoms']:
            print(f"      {sym} ({gl}) -> {cat}")
    print(f"  H_OP strict (op-pure only): {audit['h_operation_strict']:.2%}")
    print(f"  H_OP inclusive (op-pure + ambiguous-as-op): {audit['h_operation_inclusive']:.2%}")

    # ---- Step 1: Compute stats per inventory ----
    print("\n--- Step 1: Inventory stats per system ---")
    # Load Latin morpheme inventory (granularity-fix per expert-advisor PHASE_710 scrutiny)
    morpheme_path = PHASE_DIR / 'reference_data' / 'latin_morpheme_inventory.json'
    if morpheme_path.exists():
        morphemes_data = json.loads(morpheme_path.read_text(encoding='utf-8'))
        morpheme_items = morphemes_data["items"]
    else:
        morpheme_items = {}

    inventories = {
        "voynich_atoms":               (refs["voynich_atoms"]["items"],          "OPERATION"),
        "forth_core_words":            (refs["forth_core_words"]["items"],       "OPERATION"),
        "x86_base_instructions":       (refs["x86_base_instructions"]["items"],  "OPERATION"),
        "mensural_durations":          (refs["mensural_durations"]["items"],     "OPERATION"),
        "latin_top50_codicillus":      (refs["latin_top50_codicillus"]["items"], "OPERATION"),
        "latin_morpheme_inventory":    (morpheme_items,                          "OPERATION"),
    }

    all_stats = {}
    for name, (items, target) in inventories.items():
        s = inventory_stats(items, strict_category=target)
        all_stats[name] = s
        print(f"\n  {name}:")
        print(f"    N = {s['N']}")
        print(f"    Categories (strict):    {s['strict_categories']}")
        print(f"    Categories (inclusive): {s['inclusive_categories']}")
        print(f"    Dominant strict:    {s['dominant_category_strict']} (H={s['H_dominant_strict']:.2%})")
        print(f"    Dominant inclusive: {s['dominant_category_inclusive']} (H={s['H_dominant_inclusive']:.2%})")
        print(f"    H_OPERATION strict:    {s['H_target_category_strict']:.2%}")
        print(f"    H_OPERATION inclusive: {s['H_target_category_inclusive']:.2%}")

    # ---- Step 2: Cross-corpus comparison table ----
    print("\n" + "=" * 90)
    print("CROSS-CORPUS COMPARISON")
    print("=" * 90)
    print(f"\n{'Corpus':<28}{'N':>6}{'H_OP_strict':>14}{'H_OP_incl':>12}{'Dom_incl':>20}")
    print("-" * 80)
    for name, s in all_stats.items():
        print(f"{name:<28}{s['N']:>6}{s['H_target_category_strict']:>14.2%}"
              f"{s['H_target_category_inclusive']:>12.2%}{s['dominant_category_inclusive']:>20}")

    # ---- Step 3: Verdict ----
    print("\n" + "=" * 90)
    print("VERDICT EVALUATION (pre-registered)")
    print("=" * 90)

    verdict_data = evaluate_verdict(all_stats["voynich_atoms"], all_stats, audit)
    print(f"\n  Axis 1 (Voynich H_OP_inclusive >= 0.85): "
          f"{'PASS' if verdict_data['axis1_pass_inclusive'] else 'FAIL'} "
          f"(H={verdict_data['voynich_h_op_inclusive']:.2%})")
    print(f"           strict variant: "
          f"{'PASS' if verdict_data['axis1_pass_strict'] else 'FAIL'} "
          f"(H={verdict_data['voynich_h_op_strict']:.2%})")
    print(f"  Axis 2 (matches >= 2 positive controls): "
          f"{'PASS' if verdict_data['axis2_pass'] else 'FAIL'}")
    for d in verdict_data['axis2_details']:
        print(f"           {d['corpus']}: N={d['N']}, H_incl={d['H_dominant_inclusive']:.2%}, "
              f"dom={d['dominant']} -> {'match' if d['matches'] else 'no match'}")
    print(f"  Axis 3 (distinguished from mensural + NL): "
          f"{'PASS' if verdict_data['axis3_pass'] else 'FAIL'}")
    print(f"           mensural OP-H={verdict_data['mensural_op_h_inclusive']:.2%} (should be <0.30)")
    print(f"           NL dominant-H={verdict_data['nl_dominant_h']:.2%} (should be <0.50 OR non-OPERATION dominant)")
    print(f"           NL OP-H_inclusive={verdict_data['nl_op_h_inclusive']:.2%}")

    print(f"\n  VERDICT: {verdict_data['verdict']}")
    print(f"  Rationale: {verdict_data['rationale']}")

    # ---- Save ----
    out = {
        "method": "PHASE_710 monocategorical-operational vocabulary discrimination",
        "ambiguity_audit": audit,
        "inventory_stats": all_stats,
        "verdict_evaluation": verdict_data,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
