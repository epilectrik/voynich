"""
Two killer tests for f66r findings:

1. Cross-folio atom-gloss test: do other folios pass the 4-mapping test by chance?
2. Max-folio short-start null: where does f66r=88% sit in null distribution?
"""
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

PREDICTIONS = [
    ("d", "da"),
    ("t", "ot"),
    ("sh", "sh"),
    ("l", "ol"),
]


def main():
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    clean = [t for t in b_tokens if "*" not in t.word and t.word.strip() and not t.is_label]

    by_line = defaultdict(list)
    for t in clean:
        by_line[(t.folio, t.line)].append(t)

    # Group lines by folio
    folio_lines = defaultdict(list)
    for (folio, line), tokens in by_line.items():
        words = [t.word for t in tokens]
        if words:
            folio_lines[folio].append(words)

    # Corpus prefix baselines (for ALL folios)
    all_prefix = Counter()
    all_total = 0
    for t in clean:
        a = morph.atomize(t.word)
        all_prefix[a.prefix or "BARE"] += 1
        all_total += 1
    baselines = {p: c / all_total for p, c in all_prefix.items()}

    # ===== KILLER TEST 1: max-folio short-start null =====
    print("=" * 70)
    print("KILLER TEST 1: Max-folio short-start rate null distribution")
    print("=" * 70)

    folio_short_rates = {}
    for folio, lines in folio_lines.items():
        if len(lines) < 5:
            continue
        n_short = sum(1 for line in lines if line and len(line[0]) <= 2)
        rate = n_short / len(lines)
        folio_short_rates[folio] = (n_short, len(lines), rate)

    print(f"  N folios with >=5 lines: {len(folio_short_rates)}")

    # Sorted by rate
    sorted_rates = sorted(folio_short_rates.items(), key=lambda x: -x[1][2])
    print(f"  Top 5 folios by short-start rate:")
    for folio, (sh, tot, rate) in sorted_rates[:5]:
        print(f"    {folio:<8} {sh}/{tot} = {rate*100:.1f}%")
    print(f"  Median: {sorted_rates[len(sorted_rates)//2][1][2]*100:.1f}%")
    print(f"  Mean: {mean(r[2] for _, r in folio_short_rates.items())*100:.1f}%")
    print(f"  Std: {stdev(r[2] for _, r in folio_short_rates.items())*100:.1f}%")

    # Null: shuffle line-first-tokens across all body B, recompute per-folio
    n_perm = 1000
    null_max_rates = []
    all_lines_all_folios = []
    for folio, lines in folio_lines.items():
        for line in lines:
            if line:
                all_lines_all_folios.append((folio, line[0]))  # (folio, first-token)

    # Build folio→list of slots structure
    folio_slot_count = {f: sum(1 for line in lines if line) for f, lines in folio_lines.items()
                        if len(lines) >= 5}

    all_first_tokens = [first for _, first in all_lines_all_folios]
    print(f"\n  Running {n_perm} permutations...")
    for _ in range(n_perm):
        # Shuffle which first-token goes to which folio slot
        shuffled = all_first_tokens[:]
        random.shuffle(shuffled)
        # Assign to folio slots in order
        idx = 0
        max_rate = 0
        for folio, n_slots in folio_slot_count.items():
            slots = shuffled[idx:idx+n_slots]
            idx += n_slots
            n_short = sum(1 for first in slots if len(first) <= 2)
            rate = n_short / n_slots if n_slots > 0 else 0
            if rate > max_rate:
                max_rate = rate
        null_max_rates.append(max_rate)

    null_max_mean = mean(null_max_rates)
    null_max_std = stdev(null_max_rates)
    null_max_p95 = sorted(null_max_rates)[int(0.95 * n_perm)]
    actual_max = sorted_rates[0][1][2]

    print(f"\n  ACTUAL max short-start rate: {actual_max*100:.1f}% (f66r)")
    print(f"  NULL max distribution:")
    print(f"    Mean: {null_max_mean*100:.1f}%")
    print(f"    Std: {null_max_std*100:.1f}%")
    print(f"    95th percentile: {null_max_p95*100:.1f}%")
    z = (actual_max - null_max_mean) / null_max_std if null_max_std > 0 else float("inf")
    p = sum(1 for v in null_max_rates if v >= actual_max) / n_perm
    print(f"    Z-score: {z:.2f}")
    print(f"    p(null >= 88%): {p:.4f}")

    # ===== KILLER TEST 2: cross-folio atom-gloss test =====
    print()
    print("=" * 70)
    print("KILLER TEST 2: Cross-folio atom-gloss mapping test")
    print("=" * 70)

    # Filter folios with >=30 lines for adequate testing
    test_folios = [f for f, lines in folio_lines.items() if len(lines) >= 30]
    print(f"  N folios with >=30 lines: {len(test_folios)}")
    print(f"  Folios: {sorted(test_folios)[:10]}{'...' if len(test_folios) > 10 else ''}")

    def run_atom_test(folio, lines, baselines):
        """Run the 4-mapping test on a folio."""
        passing = 0
        details = {}
        for header_char, predicted_prefix in PREDICTIONS:
            # Pool content from lines whose first token is the header
            content = []
            for line in lines:
                if line and line[0] == header_char:
                    content.extend(line[1:])
            if len(content) < 5:
                details[(header_char, predicted_prefix)] = (0, 0, 0, 1.0)
                continue
            n_match = sum(1 for w in content if morph.atomize(w).prefix == predicted_prefix)
            rate = n_match / len(content)
            baseline = baselines.get(predicted_prefix, 0)
            enrichment = rate / baseline if baseline > 0 else 0

            # Permutation: shuffle which lines have this header within the folio
            n_perm_inner = 500
            n_extreme = 0
            line_first_tokens = [line[0] if line else "" for line in lines]
            line_contents = [line[1:] if line else [] for line in lines]
            for _ in range(n_perm_inner):
                shuffled_idx = list(range(len(lines)))
                random.shuffle(shuffled_idx)
                # The lines whose shuffled position has header == header_char
                shuf_content = []
                for i, idx in enumerate(shuffled_idx):
                    if line_first_tokens[i] == header_char:
                        shuf_content.extend(line_contents[idx])
                if not shuf_content:
                    continue
                shuf_match = sum(1 for w in shuf_content if morph.atomize(w).prefix == predicted_prefix)
                shuf_rate = shuf_match / len(shuf_content)
                shuf_enrich = shuf_rate / baseline if baseline > 0 else 0
                if shuf_enrich >= enrichment:
                    n_extreme += 1
            p_val = n_extreme / n_perm_inner

            details[(header_char, predicted_prefix)] = (len(content), n_match, enrichment, p_val)
            if enrichment >= 2.0 and p_val < 0.05:
                passing += 1
        return passing, details

    print(f"\n  Running atom-gloss test on each folio (this may take a moment)...")
    folio_results = {}
    for folio in test_folios:
        lines = folio_lines[folio]
        passing, details = run_atom_test(folio, lines, baselines)
        folio_results[folio] = {"passing": passing, "details": details, "n_lines": len(lines)}

    # Summarize: how many folios pass 2+ mappings?
    pass_2 = sum(1 for r in folio_results.values() if r["passing"] >= 2)
    pass_3 = sum(1 for r in folio_results.values() if r["passing"] >= 3)
    pass_4 = sum(1 for r in folio_results.values() if r["passing"] >= 4)
    n_total = len(folio_results)

    print(f"\n  Results:")
    print(f"    Folios passing >=4 mappings: {pass_4}/{n_total} ({pass_4/n_total*100:.0f}%)")
    print(f"    Folios passing >=3 mappings: {pass_3}/{n_total} ({pass_3/n_total*100:.0f}%)")
    print(f"    Folios passing >=2 mappings: {pass_2}/{n_total} ({pass_2/n_total*100:.0f}%)")

    f66r_passing = folio_results.get("f66r", {}).get("passing", "n/a")
    print(f"\n    f66r passing: {f66r_passing}/4")

    # List which folios pass 2+
    print(f"\n  Folios passing 2+ mappings:")
    for folio, r in sorted(folio_results.items(), key=lambda x: -x[1]["passing"])[:15]:
        if r["passing"] >= 1:
            print(f"    {folio:<8} {r['passing']}/4 (n_lines={r['n_lines']})")

    # === VERDICT ===
    print()
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print(f"  KILLER 1 (short-start anomaly): f66r at 88% vs null max {null_max_mean*100:.0f}% mean (z={z:.1f}, p={p:.4f})")
    if p < 0.001:
        print(f"    -> f66r is GENUINE structural outlier; Tier 2 candidate for short-start anomaly")
    elif p < 0.05:
        print(f"    -> f66r is significant but not extreme; Tier 3 candidate")
    else:
        print(f"    -> f66r is within null distribution; structural anomaly NOT exceptional")

    print()
    if pass_2 / n_total > 0.20:
        print(f"  KILLER 2 (atom-gloss): {pass_2}/{n_total} folios pass 2+ mappings ({pass_2/n_total*100:.0f}%)")
        print(f"    -> atom-gloss correspondence is NOT specific to f66r; REJECT Finding 2")
    else:
        print(f"  KILLER 2 (atom-gloss): only {pass_2}/{n_total} folios pass 2+ mappings ({pass_2/n_total*100:.0f}%)")
        print(f"    -> f66r is unusual on atom-gloss test; possibly registerable")


if __name__ == "__main__":
    main()
