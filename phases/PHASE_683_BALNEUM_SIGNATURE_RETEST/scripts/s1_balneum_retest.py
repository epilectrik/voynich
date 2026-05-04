"""
Phase 683b Script 1: Balneum signature retest with corrected methodology.

Pre-registered protocol locked in PRE_REGISTRATION.md.

Tests:
  T1 PRIMARY: ke/(ke+ek) proportion, matched vs corpus, Mann-Whitney one-tailed
  T2 SECONDARY: e_depth>=2 token fraction
  T3 SECONDARY: kernel-e fraction

Stopping rule: only run T2/T3 if T1 passes.
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "balneum_retest.json"

MATCHED = ["f75r", "f76r", "f76v", "f79r", "f81v", "f82r", "f84r",
           "f103r", "f112r", "f112v", "f116r"]
CLUSTER_FOLIOS = [
    "f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v",
    "f43r", "f50r", "f50v", "f55r", "f55v", "f85r1", "f85r2",
    "f86v4", "f86v5", "f86v6", "f94r", "f94v", "f95r1", "f95r2",
    "f95v1", "f95v2", "f105v", "f114r",
]


def gather_paragraphs(folio, b_tokens):
    folio_tokens = [t for t in b_tokens if t.folio == folio
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


def compute_metrics(para_tokens, morph):
    """For one paragraph, compute ke count, ek count, e-depth>=2 count, total atoms."""
    ke_count = 0  # k followed by e in MIDDLE
    ek_count = 0  # e followed by k in MIDDLE
    edepth_ge2_tokens = 0
    kernel_e_count = 0
    kernel_total = 0
    total_kernel_eligible = 0
    for t in para_tokens:
        word = t.word
        a = morph.atomize(word)
        if not a.atoms:
            continue
        # Look at MIDDLE chars (between prefix and any single TERM)
        atom_chars = [c for c, _, _ in a.atoms]
        # Count ke and ek bigrams in atom sequence
        for i in range(len(atom_chars) - 1):
            if atom_chars[i] == "k" and atom_chars[i + 1] == "e":
                ke_count += 1
            if atom_chars[i] == "e" and atom_chars[i + 1] == "k":
                ek_count += 1
        # e-depth >= 2
        if a.e_depth >= 2:
            edepth_ge2_tokens += 1
        # Kernel atom count
        for c in atom_chars:
            if c in "khe":
                kernel_total += 1
                if c == "e":
                    kernel_e_count += 1
        total_kernel_eligible += 1
    return {
        "n_tokens": len(para_tokens),
        "ke_count": ke_count,
        "ek_count": ek_count,
        "ke_ratio": ke_count / max(1, ek_count),
        "ke_proportion": ke_count / max(1, ke_count + ek_count),
        "edepth_ge2_frac": edepth_ge2_tokens / max(1, len(para_tokens)),
        "kernel_e_frac": kernel_e_count / max(1, kernel_total),
    }


def mann_whitney_u(group1, group2):
    """Compute U statistic and approximate one-tailed p-value (group1 > group2)."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return None, None
    combined = [(v, 1) for v in group1] + [(v, 2) for v in group2]
    combined.sort(key=lambda x: x[0])
    # Compute ranks (handle ties with average rank)
    ranks = [0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    R1 = sum(r for r, (_, g) in zip(ranks, combined) if g == 1)
    U1 = R1 - n1 * (n1 + 1) / 2
    # Normal approximation
    mu_U = n1 * n2 / 2
    sigma_U = (n1 * n2 * (n1 + n2 + 1) / 12) ** 0.5
    if sigma_U == 0:
        return U1, 1.0
    z = (U1 - mu_U) / sigma_U
    # one-tailed p (group1 > group2)
    from math import erf, sqrt
    p_one = 0.5 * (1 - erf(z / sqrt(2)))
    return U1, p_one


def cohens_d(g1, g2):
    if len(g1) < 2 or len(g2) < 2:
        return 0
    s1 = stdev(g1)
    s2 = stdev(g2)
    pooled = ((s1 * s1 + s2 * s2) / 2) ** 0.5
    if pooled == 0:
        return 0
    return (mean(g1) - mean(g2)) / pooled


def main():
    print("Loading...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Per-paragraph metrics for matched folios + corpus + cluster (for control)
    matched_paras = []
    cluster_paras = []
    corpus_paras = []

    all_folios = sorted(set(t.folio for t in b_tokens))
    for folio in all_folios:
        paras = gather_paragraphs(folio, b_tokens)
        for p in paras:
            if len(p) < 5:
                continue
            metrics = compute_metrics(p, morph)
            metrics["folio"] = folio
            if folio in MATCHED:
                matched_paras.append(metrics)
            elif folio in CLUSTER_FOLIOS:
                cluster_paras.append(metrics)
            else:
                corpus_paras.append(metrics)

    print(f"Matched paragraphs: {len(matched_paras)}")
    print(f"Cluster paragraphs: {len(cluster_paras)}")
    print(f"Corpus paragraphs: {len(corpus_paras)}")

    # Filter: only keep paragraphs with non-zero ke+ek (otherwise proportion undefined)
    matched_with_kek = [p for p in matched_paras if (p["ke_count"] + p["ek_count"]) > 0]
    corpus_with_kek = [p for p in corpus_paras if (p["ke_count"] + p["ek_count"]) > 0]
    cluster_with_kek = [p for p in cluster_paras if (p["ke_count"] + p["ek_count"]) > 0]
    print(f"\nWith non-zero ke+ek:")
    print(f"  Matched: {len(matched_with_kek)}")
    print(f"  Corpus: {len(corpus_with_kek)}")
    print(f"  Cluster: {len(cluster_with_kek)}")

    # === T1 PRIMARY ===
    print("\n=== T1 PRIMARY: ke/(ke+ek) proportion, Matched vs Corpus ===")
    m_props = [p["ke_proportion"] for p in matched_with_kek]
    c_props = [p["ke_proportion"] for p in corpus_with_kek]
    cluster_props = [p["ke_proportion"] for p in cluster_with_kek]

    d = cohens_d(m_props, c_props)
    U, p = mann_whitney_u(m_props, c_props)
    print(f"  Matched mean: {mean(m_props):.4f} (n={len(m_props)})")
    print(f"  Corpus mean: {mean(c_props):.4f} (n={len(c_props)})")
    print(f"  Cluster mean: {mean(cluster_props):.4f} (n={len(cluster_props)})")
    print(f"  Cohen's d (matched vs corpus): {d:+.4f}")
    print(f"  Mann-Whitney U: {U:.0f}, one-tailed p: {p:.4f}")

    # === LOO ===
    print("\n=== T1 LOO SAFEGUARD ===")
    loo_d_min = float("inf")
    for f in MATCHED:
        loo_matched = [p for p in matched_with_kek if p["folio"] != f]
        if len(loo_matched) < 2:
            continue
        loo_d = cohens_d([p["ke_proportion"] for p in loo_matched], c_props)
        print(f"  Drop {f}: d={loo_d:+.4f}")
        if loo_d < loo_d_min:
            loo_d_min = loo_d
    print(f"  LOO minimum d: {loo_d_min:+.4f}")

    # === N1 PERMUTATION NULL ===
    print("\n=== N1 PERMUTATION NULL (10k shuffles) ===")
    all_paras = matched_with_kek + corpus_with_kek
    all_props = [p["ke_proportion"] for p in all_paras]
    n_match = len(matched_with_kek)
    null_ds = []
    for _ in range(10000):
        shuffled = all_props[:]
        random.shuffle(shuffled)
        g1 = shuffled[:n_match]
        g2 = shuffled[n_match:]
        null_ds.append(cohens_d(g1, g2))
    p_perm = sum(1 for v in null_ds if v >= d) / 10000
    print(f"  Null mean d: {mean(null_ds):.4f}")
    print(f"  p(null >= actual): {p_perm:.4f}")

    # === N2 CLUSTER POSITIVE-CONTROL ===
    print("\n=== N2 CLUSTER POSITIVE CONTROL ===")
    d_cluster_corpus = cohens_d(cluster_props, c_props)
    d_matched_cluster = cohens_d(m_props, cluster_props)
    print(f"  Cluster vs corpus d: {d_cluster_corpus:+.4f}")
    print(f"  Matched vs cluster d: {d_matched_cluster:+.4f}")
    print("  If section-driven: cluster vs corpus large; matched vs cluster ~0")
    print("  If match-driven: matched vs cluster large; cluster vs corpus small")

    # === VERDICT ===
    print("\n=== T1 VERDICT ===")
    pass_d = d >= 0.35
    pass_p = p < 0.05
    pass_loo = loo_d_min >= 0.20
    pass_perm = p_perm < 0.05
    print(f"  d >= 0.35: {'PASS' if pass_d else 'FAIL'} ({d:+.4f})")
    print(f"  p < 0.05: {'PASS' if pass_p else 'FAIL'} ({p:.4f})")
    print(f"  LOO min d >= 0.20: {'PASS' if pass_loo else 'FAIL'} ({loo_d_min:+.4f})")
    print(f"  Perm p < 0.05: {'PASS' if pass_perm else 'FAIL'} ({p_perm:.4f})")

    t1_pass = pass_d and pass_p and pass_loo and pass_perm

    if not t1_pass:
        print("\n=== T1 FAILED — STOPPING RULE: T2/T3 NOT RUN ===")
        verdict = "T1 FAIL: workshop interpretation stays Tier 4"
    else:
        print("\n=== T2 SECONDARY: e_depth>=2 fraction ===")
        m2 = [p["edepth_ge2_frac"] for p in matched_paras]
        c2 = [p["edepth_ge2_frac"] for p in corpus_paras]
        d2 = cohens_d(m2, c2)
        U2, p2 = mann_whitney_u(m2, c2)
        print(f"  Matched mean: {mean(m2):.4f}, Corpus mean: {mean(c2):.4f}")
        print(f"  d: {d2:+.4f}, p (one-tailed): {p2:.4f}")
        pass_t2 = d2 >= 0.35 and p2 < 0.0167

        print("\n=== T3 SECONDARY: kernel-e fraction ===")
        m3 = [p["kernel_e_frac"] for p in matched_paras]
        c3 = [p["kernel_e_frac"] for p in corpus_paras]
        d3 = cohens_d(m3, c3)
        U3, p3 = mann_whitney_u(m3, c3)
        print(f"  Matched mean: {mean(m3):.4f}, Corpus mean: {mean(c3):.4f}")
        print(f"  d: {d3:+.4f}, p (one-tailed): {p3:.4f}")
        pass_t3 = d3 >= 0.35 and p3 < 0.0167

        if t1_pass and pass_t2 and pass_t3:
            verdict = "STRONG: register Tier 3 with all 3 metrics"
        elif t1_pass:
            verdict = "Primary only: register Tier 3 narrow"

    print(f"\nVERDICT: {verdict}")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "matched_n": len(matched_with_kek),
        "corpus_n": len(corpus_with_kek),
        "matched_mean": mean(m_props),
        "corpus_mean": mean(c_props),
        "cluster_mean": mean(cluster_props),
        "cohens_d_matched_corpus": d,
        "p_one_tailed": p,
        "loo_min_d": loo_d_min,
        "permutation_p": p_perm,
        "cluster_vs_corpus_d": d_cluster_corpus,
        "matched_vs_cluster_d": d_matched_cluster,
        "t1_pass": t1_pass,
        "verdict": verdict,
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
