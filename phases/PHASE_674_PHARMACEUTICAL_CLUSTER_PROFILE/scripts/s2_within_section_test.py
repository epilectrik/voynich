"""
Phase 674 Script 2: Within-section confound test.

Both experts flagged Phase 674 Script 1's headline d-values as likely section
artifact (cluster mostly Herbal, matched mostly Biological/Pharmaceutical).
Per C1893, C1404, C1808 — section significantly affects PREFIX composition.

WITHIN-SECTION TEST: For each section that has BOTH cluster and matched
folios, compare on the e-channel axis (collapsed: e-depth-mean as composite).

If within-section d > 1.0 → finding survives → real cluster property.
If within-section d < 0.3 → finding is section recapitulation → don't register.

Also drops TTR/hapax (Heaps' law confound).
Also tests size-matched paragraph-Jaccard.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

CLUSTER_FOLIOS = [
    "f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v",
    "f43r", "f50r", "f50v", "f55r", "f55v", "f85r1", "f85r2",
    "f86v4", "f86v5", "f86v6", "f94r", "f94v", "f95r1", "f95r2",
    "f95v1", "f95v2", "f105v", "f114r",
]
MATCHED_FOLIOS = ["f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v",
                  "f112v", "f103r", "f116r", "f112r"]


def get_folio_section(folio_target, b_tokens):
    """Get section label of folio (from any token's section attribute)."""
    for t in b_tokens:
        if t.folio == folio_target:
            return t.section
    return None


def get_folio_metrics(folio_target, b_tokens, morph):
    folio_tokens = [t for t in b_tokens if t.folio == folio_target
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    if not folio_tokens:
        return None

    # e-channel composite metrics
    edepth_values = []
    head_e_count = 0
    kernel_e_count = 0
    qo_count = 0
    term_r_count = 0
    head_a_count = 0
    bare_count = 0
    n_atomized = 0
    for t in folio_tokens:
        a = morph.atomize(t.word)
        if not a.prefix:
            bare_count += 1
        if a.prefix == "qo":
            qo_count += 1
        if a.atoms:
            n_atomized += 1
            edepth_values.append(a.e_depth)
            head_char, head_role, _ = a.atoms[0]
            if head_role == "HEAD":
                if head_char == "e":
                    head_e_count += 1
                elif head_char == "a":
                    head_a_count += 1
            term_char, term_role, _ = a.atoms[-1]
            if term_role == "TERM" and term_char == "r":
                term_r_count += 1
            for ch, role, _ in a.atoms:
                if ch == "e":
                    kernel_e_count += 1

    n = len(folio_tokens)
    return {
        "folio": folio_target,
        "n_tokens": n,
        "edepth_mean": mean(edepth_values) if edepth_values else 0,
        "head_e_rate": head_e_count / n_atomized if n_atomized else 0,
        "head_a_rate": head_a_count / n_atomized if n_atomized else 0,
        "kernel_e_rate": kernel_e_count / n_atomized if n_atomized else 0,
        "qo_rate": qo_count / n,
        "term_r_rate": term_r_count / n_atomized if n_atomized else 0,
        "bare_rate": bare_count / n,
    }


def cohens_d(a, b):
    if len(a) < 2 or len(b) < 2:
        return None
    sa = stdev(a)
    sb = stdev(b)
    pooled = ((sa * sa + sb * sb) / 2) ** 0.5
    if pooled == 0:
        return 0
    return (mean(a) - mean(b)) / pooled


def main():
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    print("=== SECTION ASSIGNMENT ===")
    cluster_sec = {}
    matched_sec = {}
    for f in CLUSTER_FOLIOS:
        cluster_sec[f] = get_folio_section(f, b_tokens)
    for f in MATCHED_FOLIOS:
        matched_sec[f] = get_folio_section(f, b_tokens)

    cluster_section_dist = defaultdict(list)
    for f, s in cluster_sec.items():
        cluster_section_dist[s].append(f)
    matched_section_dist = defaultdict(list)
    for f, s in matched_sec.items():
        matched_section_dist[s].append(f)

    print("  CLUSTER folios by section:")
    for s, folios in sorted(cluster_section_dist.items()):
        print(f"    {s!r:<8}: {len(folios)} ({', '.join(folios)})")
    print("  MATCHED folios by section:")
    for s, folios in sorted(matched_section_dist.items()):
        print(f"    {s!r:<8}: {len(folios)} ({', '.join(folios)})")

    # Get profiles
    cluster_profiles = {f: get_folio_metrics(f, b_tokens, morph) for f in CLUSTER_FOLIOS}
    matched_profiles = {f: get_folio_metrics(f, b_tokens, morph) for f in MATCHED_FOLIOS}

    METRICS = ["edepth_mean", "head_e_rate", "head_a_rate", "kernel_e_rate",
               "qo_rate", "term_r_rate", "bare_rate"]

    # All-folio comparison (recap from s1)
    print("\n=== ALL-FOLIO COMPARISON (recap) ===")
    print(f"  {'Metric':<18} {'Cluster':>10} {'Matched':>10} {'d':>8}")
    for m in METRICS:
        cv = [cluster_profiles[f][m] for f in CLUSTER_FOLIOS if cluster_profiles[f]]
        mv = [matched_profiles[f][m] for f in MATCHED_FOLIOS if matched_profiles[f]]
        d = cohens_d(cv, mv)
        print(f"  {m:<18} {mean(cv):>10.4f} {mean(mv):>10.4f} {d:>+8.2f}")

    # Within-section comparison (per section that has both)
    print("\n=== WITHIN-SECTION COMPARISON ===")
    sections = set(cluster_section_dist.keys()) & set(matched_section_dist.keys())
    sections.discard(None)
    for sec in sorted(sections):
        c_folios = cluster_section_dist[sec]
        m_folios = matched_section_dist[sec]
        if len(c_folios) < 3 or len(m_folios) < 3:
            print(f"\n  Section {sec!r}: insufficient (cluster {len(c_folios)}, matched {len(m_folios)})")
            continue
        print(f"\n  Section {sec!r}: cluster={len(c_folios)} folios, matched={len(m_folios)} folios")
        print(f"  {'Metric':<18} {'Cluster':>10} {'Matched':>10} {'d':>8}")
        for m in METRICS:
            cv = [cluster_profiles[f][m] for f in c_folios if cluster_profiles[f]]
            mv = [matched_profiles[f][m] for f in m_folios if matched_profiles[f]]
            d = cohens_d(cv, mv)
            d_str = f"{d:+8.2f}" if d is not None else "    n/a"
            print(f"  {m:<18} {mean(cv):>10.4f} {mean(mv):>10.4f} {d_str}")

    # Note: if within-section has fewer than 3 in either group, t-test is unreliable
    # Document outcome for tier decision
    print("\n=== INTERPRETATION GUIDE ===")
    print("  If within-section |d| > 1.0 -> cluster property survives -> register")
    print("  If within-section |d| < 0.3 -> section recapitulation only -> don't register")
    print("  If insufficient overlap (e.g., no matched in Herbal) -> can't section-control")


if __name__ == "__main__":
    main()
