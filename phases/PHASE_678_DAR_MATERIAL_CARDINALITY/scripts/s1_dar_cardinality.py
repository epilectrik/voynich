"""
Phase 678: dar (material introduction) cardinality test on matched folios.

ORTHOGONAL CHANNEL TEST (vs Phase 677 qok-class iteration):
  C1925: dar = material introduction (5 distribution patterns)
  Hypothesis: if recipe has explicit material counts (N materials introduced),
  matched folio should have N dar tokens in the corresponding section.

PRE-REGISTERED PREDICTIONS (locked from source text BEFORE folio inspection):

  f76r (II.16 element separation):
    Source: "three elements, which pertain to the white, signified by..."
    Source: "for the red there are all four elements signified by o, p, q, r"
    Predict: f76r paragraph dar counts include {3, 4} (white-section: 3 dar,
    red-section: 4 dar). Total expected ~7 dar in the element-separation
    paragraphs.

  f112v (III.1 lunaria -> quicksilver):
    Source: "divide it into two parts, and one part you shall keep..."
    Source: "from the second part you shall draw the elements"
    Predict: f112v early paragraph (where division happens) has 2 dar.

PASS CRITERION:
  f76r: paragraph dar counts match {3, 4} within ±1 (i.e., include both
        a 3-or-2-or-4 paragraph AND a 4-or-3-or-5 paragraph)
  f112v: at least one paragraph has 2 dar tokens (within ±1 of predicted 2)

NULL: If dar-counts don't match predictions, material-cardinality is not
      a structural encoding channel (or is f103r-specific to qok).
"""
import json
from collections import defaultdict, Counter
from pathlib import Path
import sys
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "dar_cardinality.json"


def gather_folio_paragraphs(folio_target, b_tokens):
    """Return list of paragraphs (each a list of Token objects)."""
    folio_tokens = [t for t in b_tokens if t.folio == folio_target
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    if not folio_tokens:
        return []
    lines = defaultdict(list)
    for t in folio_tokens:
        lines[t.line].append(t)
    sorted_lines = sorted(lines.items(), key=lambda x: (
        int(x[0].split(".")[0]) if x[0].split(".")[0].isdigit() else 999, x[0]))
    paragraphs = []
    current = []
    for line_id, tokens in sorted_lines:
        if tokens and tokens[0].par_initial and current:
            paragraphs.append(current)
            current = []
        current.extend(tokens)
    if current:
        paragraphs.append(current)
    return paragraphs


def dar_count_per_para(folio, b_tokens):
    paras = gather_folio_paragraphs(folio, b_tokens)
    return [{
        "n_tokens": len(p),
        "dar_count": sum(1 for t in p if t.word == "dar"),
        "dar_words": [t.word for t in p if t.word == "dar"],
        "first_line": p[0].line if p else None,
        "last_line": p[-1].line if p else None,
    } for p in paras]


def folio_relative_rarity_counts(target_count, all_b_folios, b_tokens):
    """How many folios have AT LEAST ONE paragraph with exactly target_count dar?"""
    n_match = 0
    for folio in all_b_folios:
        paras = gather_folio_paragraphs(folio, b_tokens)
        if any(sum(1 for t in p if t.word == "dar") == target_count for p in paras):
            n_match += 1
    return n_match, len(all_b_folios)


def folio_relative_rarity_within_pm1(target_count, all_b_folios, b_tokens):
    """Folios with at least one paragraph at target±1."""
    n_match = 0
    for folio in all_b_folios:
        paras = gather_folio_paragraphs(folio, b_tokens)
        if any(abs(sum(1 for t in p if t.word == "dar") - target_count) <= 1 for p in paras):
            n_match += 1
    return n_match, len(all_b_folios)


def joint_rarity_3_and_4(all_b_folios, b_tokens):
    """How many folios have BOTH a paragraph with ~3 dar AND a paragraph with ~4 dar?"""
    n_strict = 0
    n_pm1 = 0
    for folio in all_b_folios:
        paras = gather_folio_paragraphs(folio, b_tokens)
        counts = [sum(1 for t in p if t.word == "dar") for p in paras]
        if 3 in counts and 4 in counts:
            n_strict += 1
        # Within ±1
        has_3ish = any(abs(c - 3) <= 1 for c in counts)
        has_4ish = any(abs(c - 4) <= 1 for c in counts)
        if has_3ish and has_4ish and not (3 in counts and 4 in counts and counts.count(3) == 1 == counts.count(4)):
            # Must be different paragraphs
            indices_3ish = [i for i, c in enumerate(counts) if abs(c - 3) <= 1]
            indices_4ish = [i for i, c in enumerate(counts) if abs(c - 4) <= 1]
            # Need at least one paragraph in each set, possibly overlapping but with at least 2 paragraphs total
            if len(set(indices_3ish) | set(indices_4ish)) >= 2:
                n_pm1 += 1
    return n_strict, n_pm1, len(all_b_folios)


def main():
    tx = Transcript()
    b_tokens = list(tx.currier_b())
    all_b_folios = sorted(set(t.folio for t in b_tokens))

    print("=" * 70)
    print("PRE-REGISTERED TEST 1: f76r dar paragraph cardinality")
    print("=" * 70)
    print("  Source: II.16 element separation — '3 white elements' + '4 red elements'")
    print("  Predict: paragraph counts include {3, 4} (within ±1)\n")

    f76r_paras = dar_count_per_para("f76r", b_tokens)
    print(f"  f76r paragraphs: {len(f76r_paras)}")
    for i, p in enumerate(f76r_paras):
        print(f"    P{i+1}: {p['n_tokens']:>3} tokens, {p['dar_count']} dar (L{p['first_line']}-L{p['last_line']})")
    print()
    f76r_counts = [p["dar_count"] for p in f76r_paras]
    has_3 = 3 in f76r_counts
    has_4 = 4 in f76r_counts
    has_3pm1 = any(abs(c - 3) <= 1 for c in f76r_counts)
    has_4pm1 = any(abs(c - 4) <= 1 for c in f76r_counts)
    print(f"  Counts: {f76r_counts}")
    print(f"  Has exactly 3: {has_3}")
    print(f"  Has exactly 4: {has_4}")
    print(f"  Has 3±1: {has_3pm1}")
    print(f"  Has 4±1: {has_4pm1}")
    print(f"  STRICT verdict: {'PASS' if (has_3 and has_4) else 'FAIL'}")
    print(f"  ±1 verdict:    {'PASS' if (has_3pm1 and has_4pm1) else 'FAIL'}")

    print()
    print("=" * 70)
    print("PRE-REGISTERED TEST 2: f112v dar paragraph cardinality")
    print("=" * 70)
    print("  Source: III.1 lunaria — 'divide it into two parts...one part...second part'")
    print("  Predict: early paragraph has 2 dar tokens\n")

    f112v_paras = dar_count_per_para("f112v", b_tokens)
    print(f"  f112v paragraphs: {len(f112v_paras)}")
    for i, p in enumerate(f112v_paras):
        print(f"    P{i+1}: {p['n_tokens']:>3} tokens, {p['dar_count']} dar (L{p['first_line']}-L{p['last_line']})")
    print()
    f112v_counts = [p["dar_count"] for p in f112v_paras]
    early_paras = f112v_counts[:max(1, len(f112v_counts) // 3)]  # first third
    print(f"  Counts: {f112v_counts}")
    print(f"  Early section (first third): {early_paras}")
    print(f"  Has 2 in early section: {2 in early_paras}")
    print(f"  Has 2±1 in early section: {any(abs(c - 2) <= 1 for c in early_paras)}")
    print(f"  STRICT verdict: {'PASS' if 2 in early_paras else 'FAIL'}")
    print(f"  ±1 verdict:    {'PASS' if any(abs(c - 2) <= 1 for c in early_paras) else 'FAIL'}")

    # === FOLIO-RELATIVE RARITY ===
    print()
    print("=" * 70)
    print("FOLIO-RELATIVE RARITY")
    print("=" * 70)
    n_with_3, n_total = folio_relative_rarity_counts(3, all_b_folios, b_tokens)
    n_with_4, _ = folio_relative_rarity_counts(4, all_b_folios, b_tokens)
    n_with_2, _ = folio_relative_rarity_counts(2, all_b_folios, b_tokens)
    n_with_3pm1, _ = folio_relative_rarity_within_pm1(3, all_b_folios, b_tokens)
    n_with_4pm1, _ = folio_relative_rarity_within_pm1(4, all_b_folios, b_tokens)
    n_with_2pm1, _ = folio_relative_rarity_within_pm1(2, all_b_folios, b_tokens)
    print(f"  Folios with at least one paragraph having exactly 3 dar: {n_with_3}/{n_total} ({n_with_3/n_total*100:.0f}%)")
    print(f"  Folios with at least one paragraph having exactly 4 dar: {n_with_4}/{n_total} ({n_with_4/n_total*100:.0f}%)")
    print(f"  Folios with at least one paragraph having exactly 2 dar: {n_with_2}/{n_total} ({n_with_2/n_total*100:.0f}%)")
    print(f"  Folios with paragraph at 3±1: {n_with_3pm1}/{n_total} ({n_with_3pm1/n_total*100:.0f}%)")
    print(f"  Folios with paragraph at 4±1: {n_with_4pm1}/{n_total} ({n_with_4pm1/n_total*100:.0f}%)")
    print(f"  Folios with paragraph at 2±1: {n_with_2pm1}/{n_total} ({n_with_2pm1/n_total*100:.0f}%)")

    # Joint test
    n_strict, n_pm1, _ = joint_rarity_3_and_4(all_b_folios, b_tokens)
    print(f"  Folios with paragraph having 3 AND another with 4 (strict): {n_strict}/{n_total} ({n_strict/n_total*100:.0f}%)")

    # === SUMMARY ===
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    out = {
        "f76r": {
            "paragraphs": f76r_paras,
            "counts": f76r_counts,
            "has_3_strict": has_3,
            "has_4_strict": has_4,
            "has_3_pm1": has_3pm1,
            "has_4_pm1": has_4pm1,
            "joint_strict_pass": has_3 and has_4,
            "joint_pm1_pass": has_3pm1 and has_4pm1,
        },
        "f112v": {
            "paragraphs": f112v_paras,
            "counts": f112v_counts,
            "early_section": early_paras,
            "has_2_strict_early": 2 in early_paras,
            "has_2_pm1_early": any(abs(c - 2) <= 1 for c in early_paras),
        },
        "rarity": {
            "n_total_folios": n_total,
            "exactly_3": n_with_3, "exactly_4": n_with_4, "exactly_2": n_with_2,
            "at_3_pm1": n_with_3pm1, "at_4_pm1": n_with_4pm1, "at_2_pm1": n_with_2pm1,
            "joint_3_and_4_strict": n_strict,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
