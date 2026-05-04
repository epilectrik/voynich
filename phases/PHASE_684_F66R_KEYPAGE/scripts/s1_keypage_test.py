"""
Test whether f66r is a character-key page: header chars predict content prefix.

PRE-REGISTERED PREDICTIONS (locked before running):
  Specific header-to-prefix mappings derived from atom gloss + observed patterns:

    d-header (gloss "do")           -> da-prefix content (material introduction)
    t-header (gloss "transfer")     -> ot-prefix content (iteration/transfer)
    sh-header (gloss "passive monitor") -> sh-prefix content (matching prefix)
    l-header (gloss "state/release")    -> ol-prefix content (l in second position)

  For each predicted mapping, compute:
    - Actual content prefix rate on f66r line
    - Corpus baseline (rate of that prefix in non-f66r body B)
    - Enrichment ratio
    - Permutation null: shuffle f66r line headers across content

  PASS: 3 of 4 specific predicted mappings show >2x enrichment with permutation p<0.05
"""
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)


def main():
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    clean = [t for t in b_tokens if "*" not in t.word and t.word.strip() and not t.is_label]

    by_line = defaultdict(list)
    for t in clean:
        by_line[(t.folio, t.line)].append(t)

    # f66r lines and corpus baseline
    f66r_lines_data = []
    corpus_prefix_count = Counter()
    corpus_total = 0
    for (folio, line), tokens in by_line.items():
        if folio == "f66r":
            words = [t.word for t in tokens]
            if not words:
                continue
            header = words[0]
            content = words[1:]
            f66r_lines_data.append({"line": line, "header": header, "content": content})
        else:
            for t in tokens:
                a = morph.atomize(t.word)
                corpus_prefix_count[a.prefix or "BARE"] += 1
                corpus_total += 1

    # Corpus baseline rates
    corpus_baselines = {p: c / corpus_total for p, c in corpus_prefix_count.items()}
    print(f"Corpus baselines (selected):")
    for p in ["da", "ot", "sh", "ol", "qo", "ch", "ok"]:
        print(f"  {p}: {corpus_baselines.get(p, 0)*100:.2f}%")
    print()

    # Pre-registered mappings
    PREDICTIONS = [
        ("d", "da"),
        ("t", "ot"),
        ("sh", "sh"),
        ("l", "ol"),
    ]

    # For each prediction, compute f66r line content prefix rate
    print("=" * 70)
    print("PRE-REGISTERED HEADER-TO-PREFIX MAPPING TEST")
    print("=" * 70)
    print(f"  {'Header':<8} {'Predicted':<12} {'Content tokens':<15} {'%matched':<10} {'Corpus baseline':<15} {'Enrichment':<10}")

    results = []
    for header_char, predicted_prefix in PREDICTIONS:
        # Pool all content from lines with this header
        all_content = []
        for line_data in f66r_lines_data:
            if line_data["header"] == header_char:
                all_content.extend(line_data["content"])
        if len(all_content) < 5:
            print(f"  {header_char:<8} {predicted_prefix:<12} (insufficient content, n={len(all_content)})")
            continue
        # Compute prefix rate
        n_total = len(all_content)
        n_match = sum(1 for w in all_content if morph.atomize(w).prefix == predicted_prefix)
        rate = n_match / n_total
        baseline = corpus_baselines.get(predicted_prefix, 0)
        enrichment = rate / baseline if baseline > 0 else float("inf")
        results.append({
            "header": header_char,
            "predicted_prefix": predicted_prefix,
            "n_content": n_total,
            "n_match": n_match,
            "rate": rate,
            "baseline": baseline,
            "enrichment": enrichment,
        })
        print(f"  {header_char:<8} {predicted_prefix:<12} {n_total:>10} {rate*100:>9.1f}%  {baseline*100:>14.2f}%  {enrichment:>8.1f}x")

    # Permutation null: shuffle headers across lines, recompute enrichment
    print("\n=== PERMUTATION NULL ===")
    n_perm = 10000
    headers = [ld["header"] for ld in f66r_lines_data]
    # Build flat content per line
    line_contents = [ld["content"] for ld in f66r_lines_data]

    def compute_enrichment(headers_assigned):
        out = {}
        for header_char, predicted_prefix in PREDICTIONS:
            content = []
            for i, h in enumerate(headers_assigned):
                if h == header_char:
                    content.extend(line_contents[i])
            if not content:
                out[(header_char, predicted_prefix)] = 0
                continue
            n_match = sum(1 for w in content if morph.atomize(w).prefix == predicted_prefix)
            rate = n_match / len(content)
            baseline = corpus_baselines.get(predicted_prefix, 0)
            out[(header_char, predicted_prefix)] = rate / baseline if baseline > 0 else 0
        return out

    actual_enrichments = compute_enrichment(headers)
    null_extreme = {k: 0 for k in actual_enrichments}
    null_means = {k: [] for k in actual_enrichments}
    for _ in range(n_perm):
        shuffled = headers[:]
        random.shuffle(shuffled)
        null = compute_enrichment(shuffled)
        for k, v in null.items():
            null_means[k].append(v)
            if v >= actual_enrichments[k]:
                null_extreme[k] += 1

    print(f"  {'Header':<8} {'Predicted':<12} {'Actual enrich':<15} {'Null mean':<12} {'p-value':<10}")
    for header_char, predicted_prefix in PREDICTIONS:
        key = (header_char, predicted_prefix)
        actual = actual_enrichments[key]
        null_m = sum(null_means[key]) / len(null_means[key]) if null_means[key] else 0
        p = null_extreme[key] / n_perm
        print(f"  {header_char:<8} {predicted_prefix:<12} {actual:>10.2f}x  {null_m:>10.2f}x  {p:>10.4f}")

    # === VERDICT ===
    print("\n=== VERDICT ===")
    n_pass = 0
    for r in results:
        h, p = r["header"], r["predicted_prefix"]
        actual = r["enrichment"]
        p_val = null_extreme[(h, p)] / n_perm
        passed = actual >= 2.0 and p_val < 0.05
        if passed:
            n_pass += 1
        flag = "PASS" if passed else "fail"
        print(f"  {h}-header → {p}-prefix: enrichment={actual:.2f}x, p={p_val:.4f} [{flag}]")
    print(f"\n  Total passing: {n_pass}/{len(PREDICTIONS)}")
    if n_pass >= 3:
        verdict = "STRONG: f66r is a character-key page"
    elif n_pass >= 2:
        verdict = "PARTIAL: some predictions hold"
    else:
        verdict = "Key-page hypothesis NOT supported"
    print(f"  VERDICT: {verdict}")


if __name__ == "__main__":
    main()
