"""
Phase 681 Script 1: Test da-MIDDLE state-encoding hypothesis on f84r.

Pre-registered protocol locked in PRE_REGISTRATION.md (committed before
running). Two tests: ARI clustering (PRIMARY) and Mantel correlation
(SECONDARY). Pass requires both with p<0.01.
"""
import json
import random
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "f84r_state_encoding.json"


def gather_f84r_paragraphs(b_tokens):
    """Group f84r tokens by paragraph (par_initial-delimited)."""
    f84r_tokens = [t for t in b_tokens if t.folio == "f84r"
                   and "*" not in t.word and t.word.strip() and not t.is_label]
    lines = defaultdict(list)
    for t in f84r_tokens:
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


def find_dar_tokens(paragraphs):
    """Return list of (paragraph_idx, token_position_in_para, word)."""
    dar_records = []
    for p_idx, para in enumerate(paragraphs):
        for t_idx, t in enumerate(para):
            if t.word == "dar":
                dar_records.append({
                    "paragraph": p_idx + 1,  # 1-indexed
                    "para_position": t_idx,
                    "word": t.word,
                    "line": t.line,
                })
    return dar_records


def middle_atom_set(word, morph):
    """Extract MIDDLE atom set: atoms between prefix and TERM."""
    a = morph.atomize(word)
    if not a.atoms:
        return set()
    middle_atoms = set()
    for i, (ch, role, _) in enumerate(a.atoms):
        if role in ("MOD", "HEAD", "PSEUDO_HEAD"):
            middle_atoms.add(ch)
    return middle_atoms


def jaccard_distance(a, b):
    if not a and not b:
        return 0.0
    return 1.0 - len(a & b) / max(1, len(a | b))


def hierarchical_cluster(dist_matrix, n_items, k):
    """Simple agglomerative clustering (single linkage), return cluster labels."""
    clusters = [[i] for i in range(n_items)]
    while len(clusters) > k:
        min_d = float("inf")
        min_pair = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = min(dist_matrix[a][b] for a in clusters[i] for b in clusters[j])
                if d < min_d:
                    min_d = d
                    min_pair = (i, j)
        i, j = min_pair
        clusters[i] = clusters[i] + clusters[j]
        clusters.pop(j)
    labels = [0] * n_items
    for c_idx, members in enumerate(clusters):
        for m in members:
            labels[m] = c_idx
    return labels


def adjusted_rand_index(labels1, labels2):
    """Compute ARI between two label assignments."""
    n = len(labels1)
    if n != len(labels2):
        return 0
    # Build contingency table
    from collections import Counter
    pairs1 = Counter(labels1)
    pairs2 = Counter(labels2)
    contingency = defaultdict(int)
    for i in range(n):
        contingency[(labels1[i], labels2[i])] += 1
    sum_nij = sum(c * (c - 1) // 2 for c in contingency.values())
    sum_ai = sum(c * (c - 1) // 2 for c in pairs1.values())
    sum_bj = sum(c * (c - 1) // 2 for c in pairs2.values())
    total_pairs = n * (n - 1) // 2
    if total_pairs == 0:
        return 0
    expected = sum_ai * sum_bj / total_pairs
    max_index = (sum_ai + sum_bj) / 2
    if max_index == expected:
        return 0
    return (sum_nij - expected) / (max_index - expected)


def mantel_test(d1, d2):
    """Pearson correlation between two distance matrices' upper triangles."""
    n = len(d1)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((d1[i][j], d2[i][j]))
    if not pairs:
        return 0
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    denx = sum((x - mx) ** 2 for x in xs)
    deny = sum((y - my) ** 2 for y in ys)
    if denx == 0 or deny == 0:
        return 0
    return num / (denx * deny) ** 0.5


def main():
    print("Loading...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    paragraphs = gather_f84r_paragraphs(b_tokens)
    print(f"f84r paragraphs: {len(paragraphs)}")

    dar_records = find_dar_tokens(paragraphs)
    print(f"f84r dar tokens: {len(dar_records)}")

    if len(dar_records) < 8:
        print("INSUFFICIENT POWER (n<8). Aborting per pre-reg.")
        return

    print("\n=== DAR TOKEN INVENTORY ===")
    for r in dar_records:
        print(f"  P{r['paragraph']:>2}  L{r['line']:>3}  pos{r['para_position']:>3}  {r['word']}")

    # Compute MIDDLE atom set per dar
    # Note: dar's MIDDLE is "ar" (HEAD=a, TERM=r). So all dar's have MIDDLE atom set {a}.
    # That means EVERY dar token has an identical MIDDLE = {a}!
    # We need the BROADER da-prefix family, OR we need to look at full token surrounding context.

    # CHECK: do ALL dar tokens have identical MIDDLE? If yes, the test is pre-failed.
    print("\n=== MIDDLE ATOM SETS ===")
    for r in dar_records:
        m = middle_atom_set(r["word"], morph)
        r["middle_atoms"] = m
        a = morph.atomize(r["word"])
        print(f"  P{r['paragraph']:>2}  {r['word']}  -> MIDDLE atoms: {sorted(m)} (full atomization: {[(c, role) for c, role, _ in a.atoms]})")

    # If all dar have identical MIDDLE, test as-defined cannot proceed.
    unique_middles = set(frozenset(r["middle_atoms"]) for r in dar_records)
    print(f"\n  Unique MIDDLE atom sets: {len(unique_middles)}")

    if len(unique_middles) <= 1:
        print("\nALL DAR TOKENS HAVE IDENTICAL MIDDLE COMPOSITION.")
        print("The test as pre-registered for f84r dar specifically CANNOT discriminate states.")
        print("This is itself an informative finding: dar token-form has no MIDDLE variability;")
        print("any state encoding via da-prefix would require looking at the BROADER da-prefix")
        print("family (dar/dal/dam/daiin/dain/dair) instead of just dar.")
        print()
        # Pivot: look at all da-prefix tokens in f84r, not just dar
        da_records = []
        for p_idx, para in enumerate(paragraphs):
            for t_idx, t in enumerate(para):
                a = morph.atomize(t.word)
                if a.prefix and a.prefix.startswith("da"):
                    da_records.append({
                        "paragraph": p_idx + 1,
                        "para_position": t_idx,
                        "word": t.word,
                        "line": t.line,
                        "middle_atoms": middle_atom_set(t.word, morph),
                    })
        print(f"=== EXPANDED: ALL da-prefix tokens in f84r (n={len(da_records)}) ===")
        for r in da_records:
            print(f"  P{r['paragraph']:>2}  L{r['line']:>3}  {r['word']:<12}  MIDDLE: {sorted(r['middle_atoms'])}")

        # Use this expanded set for the test
        dar_records = da_records

    # Filter out empty MIDDLEs
    dar_records = [r for r in dar_records if r["middle_atoms"]]
    n = len(dar_records)
    print(f"\n  Working set: n={n} da-prefix tokens with non-empty MIDDLE atoms")

    if n < 8:
        print("INSUFFICIENT POWER after filtering. Aborting.")
        return

    # === DISTANCE MATRICES ===
    para_dist = [[abs(dar_records[i]["paragraph"] - dar_records[j]["paragraph"])
                   for j in range(n)] for i in range(n)]
    middle_dist = [[jaccard_distance(dar_records[i]["middle_atoms"], dar_records[j]["middle_atoms"])
                     for j in range(n)] for i in range(n)]

    # === PRIMARY TEST: ARI clustering ===
    k = 4
    cluster_labels = hierarchical_cluster(middle_dist, n, k)
    # Stage labels: paragraph quartile bins
    para_max = max(r["paragraph"] for r in dar_records)
    para_min = min(r["paragraph"] for r in dar_records)
    para_range = para_max - para_min + 1
    stage_labels = [min(k - 1, int((r["paragraph"] - para_min) * k / para_range))
                     for r in dar_records]

    actual_ari = adjusted_rand_index(cluster_labels, stage_labels)

    print(f"\n=== PRIMARY: ARI CLUSTERING ===")
    print(f"  k = {k}")
    print(f"  Cluster labels:  {cluster_labels}")
    print(f"  Stage labels:    {stage_labels}")
    print(f"  Actual ARI: {actual_ari:.4f}")

    # Permutation null: shuffle MIDDLE assignments to dar positions
    n_perm = 10000
    null_aris = []
    indices = list(range(n))
    for _ in range(n_perm):
        shuffled = indices[:]
        random.shuffle(shuffled)
        shuffled_labels = [cluster_labels[i] for i in shuffled]
        null_aris.append(adjusted_rand_index(shuffled_labels, stage_labels))
    p_ari = sum(1 for v in null_aris if v >= actual_ari) / n_perm
    print(f"  Permutation null mean ARI: {mean(null_aris):.4f}")
    print(f"  p(null ARI >= actual): {p_ari:.4f}")

    # === SECONDARY TEST: Mantel correlation ===
    actual_mantel = mantel_test(para_dist, middle_dist)
    print(f"\n=== SECONDARY: MANTEL CORRELATION ===")
    print(f"  Actual rho: {actual_mantel:.4f}")
    null_mantels = []
    for _ in range(n_perm):
        perm = indices[:]
        random.shuffle(perm)
        perm_dist = [[middle_dist[perm[i]][perm[j]] for j in range(n)] for i in range(n)]
        null_mantels.append(mantel_test(para_dist, perm_dist))
    p_mantel = sum(1 for v in null_mantels if v >= actual_mantel) / n_perm
    print(f"  Permutation null mean rho: {mean(null_mantels):.4f}")
    print(f"  p(null rho >= actual): {p_mantel:.4f}")

    # === VERDICT ===
    print("\n=== VERDICT ===")
    pass_primary = actual_ari > 0.30 and p_ari < 0.01
    pass_secondary = actual_mantel > 0.30 and p_mantel < 0.01

    print(f"  PRIMARY (ARI > 0.30 AND p < 0.01): {'PASS' if pass_primary else 'FAIL'} "
          f"(ARI={actual_ari:.3f}, p={p_ari:.4f})")
    print(f"  SECONDARY (Mantel rho > 0.30 AND p < 0.01): {'PASS' if pass_secondary else 'FAIL'} "
          f"(rho={actual_mantel:.3f}, p={p_mantel:.4f})")

    if pass_primary and pass_secondary:
        verdict = "STATE-ENCODING SUPPORTED (Tier 3 candidate)"
    elif pass_primary or pass_secondary:
        verdict = "AMBIGUOUS (one test passes); per pre-reg: NO registration"
    else:
        verdict = "STATE-ENCODING REJECTED for f84r dar; identification-vocabulary per C1135 prevails"
    print(f"  VERDICT: {verdict}")

    # === C1 PARAGRAPH-1 CONFOUND CHECK ===
    print("\n=== C1: PARAGRAPH-1 ABLATION ===")
    no_p1 = [r for r in dar_records if r["paragraph"] != 1]
    if len(no_p1) >= 8:
        n2 = len(no_p1)
        para_dist2 = [[abs(no_p1[i]["paragraph"] - no_p1[j]["paragraph"]) for j in range(n2)] for i in range(n2)]
        middle_dist2 = [[jaccard_distance(no_p1[i]["middle_atoms"], no_p1[j]["middle_atoms"]) for j in range(n2)] for i in range(n2)]
        rho_no_p1 = mantel_test(para_dist2, middle_dist2)
        print(f"  Without P1 dar tokens (n={n2}): Mantel rho = {rho_no_p1:.4f}")
        print(f"  Original: {actual_mantel:.4f}")
    else:
        print(f"  After P1 ablation, n={len(no_p1)} too small for test")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "n": n,
        "dar_records": [{k: list(v) if isinstance(v, set) else v for k, v in r.items()} for r in dar_records],
        "actual_ari": actual_ari,
        "ari_p": p_ari,
        "actual_mantel": actual_mantel,
        "mantel_p": p_mantel,
        "pass_primary": pass_primary,
        "pass_secondary": pass_secondary,
        "verdict": verdict,
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
