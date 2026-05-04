"""
Phase 680 Script 4: same-folio baseline test (per crazy-expert).

The path-vs-node comparison showed da-prefix at 16% (paths) vs 1.7% (nodes).
But: are rosette nodes already da-enriched compared to f85-86 body text?
If the rosettes folio is dar-rich at the folio level, then path enrichment
might be 'paths sample from local dar-rich pool' rather than 'paths are
genuinely different.'

TEST: Compute dar/da-prefix rates in:
  1. Rosette path tokens (from rosettes_annotated.json) — already known: 16%
  2. Rosette node tokens (from rosettes_annotated.json) — already known: 1.7%
  3. f85 body tokens (from main transcript) — NEW
  4. f86 body tokens (from main transcript) — NEW
  5. Adjacent folios (f84r/v, f87r/v) — NEW (control)
  6. Corpus average — known: ~0.8%

If f85/f86 body has high da rate (similar to paths), path enrichment is
folio-pool artifact.
If f85/f86 body has low da rate (similar to nodes), the path-vs-node
difference is real and not folio-pool driven.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology


def main():
    rosettes_data = json.load(open(Path(__file__).resolve().parents[3] / "data" / "rosettes_annotated.json", encoding="utf-8"))
    tx = Transcript()
    morph = Morphology()

    # === Get f85 and f86 body tokens from main transcript ===
    # Use ALL tracks (not just H) since the main currier_b filter applies
    f85_f86_tokens = []
    for t in tx.currier_b():
        if "*" in t.word or not t.word.strip() or t.is_label:
            continue
        if t.folio in ("f85r1", "f85r2", "f85v1", "f85v2", "f85r", "f85v",
                       "f86r", "f86v1", "f86v2", "f86v3", "f86v4", "f86v5", "f86v6", "f86v"):
            f85_f86_tokens.append(t)

    # Adjacent folios for control
    adjacent_tokens = []
    for t in tx.currier_b():
        if "*" in t.word or not t.word.strip() or t.is_label:
            continue
        if t.folio in ("f84r", "f84v", "f87r", "f87v"):
            adjacent_tokens.append(t)

    print(f"f85/f86 body tokens (main transcript): {len(f85_f86_tokens)}")
    print(f"Adjacent (f84r/v, f87r/v) body tokens: {len(adjacent_tokens)}")

    # Show breakdown by folio for f85/f86
    print()
    by_folio = defaultdict(int)
    for t in f85_f86_tokens:
        by_folio[t.folio] += 1
    for f, c in sorted(by_folio.items()):
        print(f"  {f}: {c} tokens")

    def compute_prefix_rates(tokens):
        n = len(tokens)
        if n == 0:
            return None
        counts = Counter()
        dar_count = 0
        da_prefix_count = 0
        for t in tokens:
            word = t.word if hasattr(t, "word") else t
            a = morph.atomize(word)
            counts[a.prefix or "BARE"] += 1
            if word == "dar":
                dar_count += 1
            if a.prefix and a.prefix.startswith("da"):
                da_prefix_count += 1
        return {
            "n": n,
            "prefix_rates": {p: c / n for p, c in counts.items()},
            "dar_count": dar_count,
            "dar_rate": dar_count / n,
            "da_prefix_count": da_prefix_count,
            "da_prefix_rate": da_prefix_count / n,
        }

    f85_86_stats = compute_prefix_rates(f85_f86_tokens)
    adjacent_stats = compute_prefix_rates(adjacent_tokens)

    print(f"\n=== KEY COMPARISON ===\n")
    print(f"  {'Population':<35} {'N':>6} {'da-prefix':>10} {'dar exact':>10} {'ok-prefix':>10}")

    # Paths and nodes from rosettes data
    path_da = path_dar = path_ok = path_n = 0
    node_da = node_dar = node_ok = node_n = 0
    for ent_key, ent in rosettes_data["entities"].items():
        is_path = ent_key.startswith("PATH")
        is_node = ent_key in ("CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW")
        if not (is_path or is_node):
            continue
        for sub_name, sub in ent.get("sub_regions", {}).items():
            for locus in sub.get("loci", []):
                for w in locus.get("words", []):
                    word = w.get("word", "")
                    clean = word.replace(".", "").replace(",", "").replace("'", "").strip()
                    if not clean or "*" in clean:
                        continue
                    a = morph.atomize(clean)
                    if is_path:
                        path_n += 1
                        if a.prefix and a.prefix.startswith("da"):
                            path_da += 1
                        if clean == "dar":
                            path_dar += 1
                        if a.prefix == "ok":
                            path_ok += 1
                    elif is_node:
                        node_n += 1
                        if a.prefix and a.prefix.startswith("da"):
                            node_da += 1
                        if clean == "dar":
                            node_dar += 1
                        if a.prefix == "ok":
                            node_ok += 1

    def fmt(da, dar, ok, n):
        if n == 0:
            return f"{n:>6} {'-':>10} {'-':>10} {'-':>10}"
        return (f"{n:>6} {da}/{n} ({da/n*100:>4.1f}%)  "
                f"{dar}/{n} ({dar/n*100:>4.1f}%)  "
                f"{ok}/{n} ({ok/n*100:>4.1f}%)")

    print(f"  {'1. Rosette PATH tokens':<35} {fmt(path_da, path_dar, path_ok, path_n)}")
    print(f"  {'2. Rosette NODE tokens':<35} {fmt(node_da, node_dar, node_ok, node_n)}")

    if f85_86_stats:
        f85_86_da_n = sum(1 for t in f85_f86_tokens if morph.atomize(t.word).prefix and morph.atomize(t.word).prefix.startswith("da"))
        f85_86_dar_n = sum(1 for t in f85_f86_tokens if t.word == "dar")
        f85_86_ok_n = sum(1 for t in f85_f86_tokens if morph.atomize(t.word).prefix == "ok")
        print(f"  {'3. f85+f86 BODY tokens':<35} {fmt(f85_86_da_n, f85_86_dar_n, f85_86_ok_n, len(f85_f86_tokens))}")

    if adjacent_stats:
        adj_da_n = sum(1 for t in adjacent_tokens if morph.atomize(t.word).prefix and morph.atomize(t.word).prefix.startswith("da"))
        adj_dar_n = sum(1 for t in adjacent_tokens if t.word == "dar")
        adj_ok_n = sum(1 for t in adjacent_tokens if morph.atomize(t.word).prefix == "ok")
        print(f"  {'4. Adjacent folios body':<35} {fmt(adj_da_n, adj_dar_n, adj_ok_n, len(adjacent_tokens))}")

    # Corpus baseline
    all_b = list(tx.currier_b())
    all_b_clean = [t for t in all_b if "*" not in t.word and t.word.strip() and not t.is_label]
    corpus_da_n = sum(1 for t in all_b_clean if morph.atomize(t.word).prefix and morph.atomize(t.word).prefix.startswith("da"))
    corpus_dar_n = sum(1 for t in all_b_clean if t.word == "dar")
    corpus_ok_n = sum(1 for t in all_b_clean if morph.atomize(t.word).prefix == "ok")
    print(f"  {'5. Corpus baseline (all B body)':<35} {fmt(corpus_da_n, corpus_dar_n, corpus_ok_n, len(all_b_clean))}")

    # === VERDICT LOGIC ===
    print("\n=== VERDICT LOGIC ===")
    print("If f85/f86 body has da-rate similar to PATHS (~16%): path enrichment = folio-pool artifact")
    print("If f85/f86 body has da-rate similar to NODES (~1.7%): path-vs-node difference is real")
    print("If f85/f86 body is between: partial folio effect + partial path-specific effect\n")


if __name__ == "__main__":
    main()
