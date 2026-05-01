"""
Phase 674 Script 1: Pharmaceutical regime cluster operational profile.

Phase 642 identified a 26-folio cluster (PC1 separates 8-10sigma from
Testamentum-matched alchemical folios) with characterization "low-heat
observational" (cluster side: e-depth=0, a/o-HEAD, BARE prefix; matched
side: qo, e-depth=1, k/e-HEAD).

This phase characterizes what they're DOING operationally beyond the
PC1 axis. Side-by-side comparison vs the 11 Phase-668-validated
alchemical-matched folios.

Pre-registered axes (12 dimensions):
  1. PREFIX channel rates (qo, ch, sh, ok, ot, ol, lk, BARE)
  2. HEAD atom composition (a, e, o, k, t)
  3. Terminal atom rates (-y, -n, -r, -l, -m, -d, -s, -o)
  4. Kernel atom rates (k, e, h, p, c)
  5. e-depth distribution (mean, % at 0/1/2+)
  6. Token class rates (RI, PP, INFRA, UNKNOWN per voynich.py)
  7. Paragraph counts per folio (median, range)
  8. Tokens per paragraph
  9. Hapax token rate (1-occurrence tokens within folio)
  10. dar-prefix rate (material introduction marker C1925)
  11. Line-final -m rate (universal closure C1486)
  12. Inter-paragraph token overlap (high = parallel/reference-like,
      low = sequential/procedural)

Output: phases/PHASE_674_PHARMACEUTICAL_CLUSTER_PROFILE/results/
        cluster_vs_matched_profile.json
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median, stdev

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology, RecordAnalyzer


CLUSTER_FOLIOS = [
    "f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v",
    "f43r", "f50r", "f50v", "f55r", "f55v", "f85r1", "f85r2",
    "f86v4", "f86v5", "f86v6", "f94r", "f94v", "f95r1", "f95r2",
    "f95v1", "f95v2", "f105v", "f114r",
]

MATCHED_FOLIOS = [
    "f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v", "f112v",
    "f103r", "f116r", "f112r",
]

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "cluster_vs_matched_profile.json"


def gather_folio_tokens(folio_target, b_tokens):
    """Return (folio_tokens, lines_dict, paragraph_dict)."""
    folio_tokens = [t for t in b_tokens if t.folio == folio_target
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    lines = defaultdict(list)
    for t in folio_tokens:
        lines[t.line].append(t)
    # Group lines by paragraph (par_initial flag delimits)
    paragraphs = []
    current = []
    sorted_lines = sorted(lines.items(), key=lambda x: (
        int(x[0].split(".")[0]) if x[0].split(".")[0].isdigit() else 999, x[0]))
    for line_id, tokens in sorted_lines:
        if tokens and tokens[0].par_initial and current:
            paragraphs.append(current)
            current = []
        current.append((line_id, tokens))
    if current:
        paragraphs.append(current)
    return folio_tokens, lines, paragraphs


def profile_folio(folio, b_tokens, morph):
    folio_tokens, lines, paragraphs = gather_folio_tokens(folio, b_tokens)
    if not folio_tokens:
        return None

    # 1. PREFIX channels
    prefix_count = Counter()
    head_count = Counter()
    term_count = Counter()
    kernel_count = Counter()
    edepth_dist = Counter()
    edepth_values = []
    n_atomized = 0
    dar_count = 0
    bare_count = 0
    line_final_m = 0
    line_final_total = 0

    for t in folio_tokens:
        a = morph.atomize(t.word)
        prefix_count[a.prefix or "BARE"] += 1
        if not a.prefix:
            bare_count += 1
        if t.word == "dar":
            dar_count += 1
        if a.atoms:
            n_atomized += 1
            head_char, head_role, _ = a.atoms[0]
            if head_role == "HEAD":
                head_count[head_char] += 1
            term_char, term_role, _ = a.atoms[-1]
            if term_role == "TERM":
                term_count[term_char] += 1
            for ch, role, _ in a.atoms:
                if ch in "kehpc":
                    kernel_count[ch] += 1
            edepth_dist[a.e_depth] += 1
            edepth_values.append(a.e_depth)

    # Line-final -m
    for line_id, line_tokens in lines.items():
        if not line_tokens:
            continue
        last = line_tokens[-1]
        line_final_total += 1
        if last.word.endswith("m"):
            line_final_m += 1

    n_total = len(folio_tokens)

    # 7-8. Paragraph metrics
    paragraph_token_counts = [sum(len(t) for _, t in p) for p in paragraphs]
    n_paragraphs = len(paragraphs)
    median_tokens_per_para = median(paragraph_token_counts) if paragraph_token_counts else 0

    # 9. Hapax rate
    word_counts = Counter(t.word for t in folio_tokens)
    hapax = sum(1 for w, c in word_counts.items() if c == 1)
    hapax_rate = hapax / len(word_counts) if word_counts else 0
    vocab_size = len(word_counts)
    type_token_ratio = vocab_size / n_total if n_total > 0 else 0

    # 12. Inter-paragraph token overlap (Jaccard average between adjacent paragraphs)
    paragraph_words = [set(t.word for _, line_tokens in p for t in line_tokens) for p in paragraphs]
    jaccards = []
    for i in range(len(paragraph_words) - 1):
        a_set = paragraph_words[i]
        b_set = paragraph_words[i + 1]
        if a_set and b_set:
            j = len(a_set & b_set) / len(a_set | b_set)
            jaccards.append(j)
    mean_para_jaccard = mean(jaccards) if jaccards else 0

    return {
        "folio": folio,
        "n_tokens": n_total,
        "n_paragraphs": n_paragraphs,
        "median_tokens_per_para": median_tokens_per_para,
        "vocab_size": vocab_size,
        "type_token_ratio": type_token_ratio,
        "hapax_rate": hapax_rate,
        "prefix_rates": {p: c / n_total for p, c in prefix_count.items()},
        "head_rates": {h: c / n_atomized for h, c in head_count.items()} if n_atomized > 0 else {},
        "term_rates": {t: c / n_atomized for t, c in term_count.items()} if n_atomized > 0 else {},
        "kernel_rates": {k: c / n_atomized for k, c in kernel_count.items()} if n_atomized > 0 else {},
        "edepth_mean": mean(edepth_values) if edepth_values else 0,
        "edepth_dist": {str(d): c / n_atomized for d, c in edepth_dist.items()} if n_atomized > 0 else {},
        "bare_rate": bare_count / n_total,
        "dar_rate": dar_count / n_total,
        "line_final_m_rate": line_final_m / line_final_total if line_final_total > 0 else 0,
        "mean_para_jaccard": mean_para_jaccard,
    }


def aggregate_group(profiles):
    """Aggregate per-folio profiles into a group summary (mean, std)."""
    if not profiles:
        return {}
    keys = ["n_tokens", "n_paragraphs", "median_tokens_per_para", "vocab_size",
            "type_token_ratio", "hapax_rate", "edepth_mean", "bare_rate",
            "dar_rate", "line_final_m_rate", "mean_para_jaccard"]
    out = {}
    for k in keys:
        values = [p[k] for p in profiles]
        out[k] = {"mean": mean(values), "std": stdev(values) if len(values) > 1 else 0,
                  "min": min(values), "max": max(values), "n": len(values)}

    # Aggregate dict-valued fields (rates)
    dict_keys = ["prefix_rates", "head_rates", "term_rates", "kernel_rates", "edepth_dist"]
    for dk in dict_keys:
        all_keys = set()
        for p in profiles:
            all_keys.update(p[dk].keys())
        out[dk] = {}
        for sub_key in all_keys:
            values = [p[dk].get(sub_key, 0) for p in profiles]
            out[dk][sub_key] = {
                "mean": mean(values),
                "std": stdev(values) if len(values) > 1 else 0,
            }
    return out


def compare_groups(cluster_agg, matched_agg, key, sub_key=None):
    """Cohen's d effect size between cluster and matched group means."""
    if sub_key is None:
        c = cluster_agg.get(key, {})
        m = matched_agg.get(key, {})
        c_mean = c.get("mean", 0)
        m_mean = m.get("mean", 0)
        c_std = c.get("std", 0)
        m_std = m.get("std", 0)
    else:
        c = cluster_agg.get(key, {}).get(sub_key, {})
        m = matched_agg.get(key, {}).get(sub_key, {})
        c_mean = c.get("mean", 0)
        m_mean = m.get("mean", 0)
        c_std = c.get("std", 0)
        m_std = m.get("std", 0)
    pooled_std = ((c_std ** 2 + m_std ** 2) / 2) ** 0.5
    if pooled_std == 0:
        return c_mean, m_mean, 0
    d = (c_mean - m_mean) / pooled_std
    return c_mean, m_mean, d


def main():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    print(f"  B tokens: {len(b_tokens)}")
    print()

    cluster_profiles = []
    matched_profiles = []

    print("=== PROFILING CLUSTER FOLIOS ===")
    for folio in CLUSTER_FOLIOS:
        p = profile_folio(folio, b_tokens, morph)
        if p:
            cluster_profiles.append(p)
            print(f"  {folio:<8} tokens={p['n_tokens']:>4} paras={p['n_paragraphs']:>2} "
                  f"vocab={p['vocab_size']:>4} edepth_mean={p['edepth_mean']:.2f} "
                  f"bare_rate={p['bare_rate']:.3f}")
        else:
            print(f"  {folio:<8} NO TOKENS")

    print(f"\n  Cluster profiles built: {len(cluster_profiles)}/{len(CLUSTER_FOLIOS)}")

    print("\n=== PROFILING MATCHED ALCHEMICAL FOLIOS ===")
    for folio in MATCHED_FOLIOS:
        p = profile_folio(folio, b_tokens, morph)
        if p:
            matched_profiles.append(p)
            print(f"  {folio:<8} tokens={p['n_tokens']:>4} paras={p['n_paragraphs']:>2} "
                  f"vocab={p['vocab_size']:>4} edepth_mean={p['edepth_mean']:.2f} "
                  f"bare_rate={p['bare_rate']:.3f}")

    cluster_agg = aggregate_group(cluster_profiles)
    matched_agg = aggregate_group(matched_profiles)

    # === SIDE-BY-SIDE COMPARISON ===
    print("\n" + "=" * 80)
    print("CLUSTER (n=26) vs MATCHED ALCHEMICAL (n=11) — Cohen's d effect sizes")
    print("=" * 80)

    print("\n--- SCALAR DIMENSIONS ---")
    print(f"  {'Metric':<28} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for key in ["n_tokens", "n_paragraphs", "median_tokens_per_para", "vocab_size",
                "type_token_ratio", "hapax_rate", "edepth_mean", "bare_rate",
                "dar_rate", "line_final_m_rate", "mean_para_jaccard"]:
        cm, mm, d = compare_groups(cluster_agg, matched_agg, key)
        print(f"  {key:<28} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {d:>+10.2f}")

    print("\n--- PREFIX RATES (top 10 by cluster mean) ---")
    pr_keys = sorted(set(cluster_agg["prefix_rates"].keys()) | set(matched_agg["prefix_rates"].keys()),
                     key=lambda k: -cluster_agg["prefix_rates"].get(k, {}).get("mean", 0))[:12]
    print(f"  {'Prefix':<14} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for pf in pr_keys:
        cm, mm, d = compare_groups(cluster_agg, matched_agg, "prefix_rates", pf)
        if cm > 0.005 or mm > 0.005:
            print(f"  {pf:<14} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {d:>+10.2f}")

    print("\n--- HEAD ATOM RATES ---")
    print(f"  {'HEAD':<6} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for h in "aeokt":
        cm, mm, d = compare_groups(cluster_agg, matched_agg, "head_rates", h)
        print(f"  {h:<6} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {d:>+10.2f}")

    print("\n--- TERMINAL ATOM RATES ---")
    print(f"  {'TERM':<6} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for t in "ynlrmsod":
        cm, mm, d = compare_groups(cluster_agg, matched_agg, "term_rates", t)
        if cm > 0.001 or mm > 0.001:
            print(f"  {t:<6} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {d:>+10.2f}")

    print("\n--- KERNEL ATOM RATES ---")
    print(f"  {'Kernel':<8} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for k in "kehpc":
        cm, mm, d = compare_groups(cluster_agg, matched_agg, "kernel_rates", k)
        if cm > 0.005 or mm > 0.005:
            print(f"  {k:<8} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {d:>+10.2f}")

    print("\n--- e-DEPTH DISTRIBUTION ---")
    print(f"  {'e-depth':<8} {'Cluster':>10} {'Matched':>10} {'Diff':>10} {'Cohen-d':>10}")
    for d_str in ["0", "1", "2", "3", "4"]:
        cm, mm, dd = compare_groups(cluster_agg, matched_agg, "edepth_dist", d_str)
        if cm > 0.01 or mm > 0.01:
            print(f"  {d_str:<8} {cm:>10.4f} {mm:>10.4f} {cm-mm:>+10.4f} {dd:>+10.2f}")

    # Save full output
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "cluster_folios": [p["folio"] for p in cluster_profiles],
        "matched_folios": [p["folio"] for p in matched_profiles],
        "cluster_per_folio": cluster_profiles,
        "matched_per_folio": matched_profiles,
        "cluster_agg": cluster_agg,
        "matched_agg": matched_agg,
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
