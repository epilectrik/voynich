"""
Phase 672 Script 1: PREFIX-class differential positional bias on fixed e->y frame.

Investigation chain (post Phase 671):
  - okar outlier (Phase 671): only a-HEAD r-TERM token without bimodal class profile
  - Initial broad scan: prefix classes appeared to encode positional roles
  - Both experts flagged confounds (paragraph leakage C1287/C1819, section
    confound C1808, articulator C1417, LATE-class C539, line-zone C1426)
  - Crazy-expert's discriminating test: hold HEAD+TERM frame fixed (e->y, the
    highest-power frame per C1457), exclude articulators, vary only PREFIX.
    If sh-e->y vs ch-e->y differ -> prefix carries info. If identical -> passive.

Pre-registered controls:
  - Body-only (paragraph-initial line excluded)
  - Paragraph-line >= 3 (skip lines 1+2 to bypass header register C1819)
  - Section stratification (H, B, S separately and pooled)
  - HEAD=e, TERM=y, no articulator (frame held fixed)
  - Lines >= 4 tokens (avoid degenerate normalization)

Pre-registered formal test:
  - Permutation of prefix labels within each line containing both ch and sh
    e->y tokens. Test null: sh-mean == ch-mean. 10,000 permutations.

Output: phases/PHASE_672_PREFIX_POSITIONAL_ROLE/results/prefix_position_ey.json
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "prefix_position_ey.json"


def gather_lines_with_para_pos(tokens):
    by_line = defaultdict(list)
    for t in tokens:
        if "*" in t.word or not t.word.strip() or t.is_label:
            continue
        by_line[(t.folio, t.line)].append(t)
    by_folio = defaultdict(list)
    for (folio, line_id), tokens_in_line in by_line.items():
        by_folio[folio].append((line_id, tokens_in_line))
    para_pos = {}
    for folio, line_list in by_folio.items():
        def line_key(item):
            ln = item[0]
            try:
                return (int(ln.split(".")[0]), ln)
            except Exception:
                return (999, ln)
        line_list.sort(key=line_key)
        current_para_idx = 0
        for line_id, tokens_in_line in line_list:
            if tokens_in_line and tokens_in_line[0].par_initial:
                current_para_idx = 0
            para_pos[(folio, line_id)] = current_para_idx
            current_para_idx += 1
    return by_line, para_pos


def position_stats(positions):
    n = len(positions)
    if n == 0:
        return None
    mean = sum(positions) / n
    bins = [0] * 10
    for p in positions:
        bins[min(9, int(p * 10))] += 1
    deciles = [b / n * 100 for b in bins]
    var = sum((p - mean) ** 2 for p in positions) / n
    std = var ** 0.5
    if std > 0:
        skew = sum(((p - mean) / std) ** 3 for p in positions) / n
        kurt = sum(((p - mean) / std) ** 4 for p in positions) / n
    else:
        skew, kurt = 0, 0
    bc = (skew * skew + 1) / kurt if kurt > 0 else 0
    return {"n": n, "mean": mean, "deciles": deciles, "bc": bc, "skew": skew}


def is_ey_no_articulator(word, morph):
    if "*" in word or not word.endswith("y"):
        return False, None
    a = morph.atomize(word)
    if a.is_headless or not a.atoms or a.articulator:
        return False, None
    head_char, head_role, _ = a.atoms[0]
    if head_role != "HEAD" or head_char != "e":
        return False, None
    term_char, term_role, _ = a.atoms[-1]
    if term_role != "TERM" or term_char != "y":
        return False, None
    return True, (a.prefix if a.prefix else "(no_prefix)")


def collect_by_prefix(by_line, para_pos, morph, min_para_pos=1, section_filter=None):
    by_prefix = defaultdict(list)
    for (folio, line_id), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        pp = para_pos.get((folio, line_id), 0)
        if pp < min_para_pos:
            continue
        if section_filter is not None:
            sec = tokens_in_line[0].section if tokens_in_line else None
            if sec != section_filter:
                continue
        for i, t in enumerate(tokens_in_line):
            ok_, prefix = is_ey_no_articulator(t.word, morph)
            if not ok_:
                continue
            by_prefix[prefix].append(i / (n - 1))
    return by_prefix


def permutation_test_sh_vs_ch(by_line, para_pos, morph, n_perm=10000, min_para_pos=1):
    """Permutation test: shuffle prefix labels among sh+ch e->y tokens within each line.

    For lines containing >=1 sh-e->y or ch-e->y token, pool all sh and ch
    e->y token positions in that line, randomly relabel them as sh or ch
    preserving counts, and compute the difference in mean position. The null
    distribution is the difference under random labeling within lines.
    """
    line_items = []  # per-line list of (positions, prefix_labels)
    for (folio, line_id), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        pp = para_pos.get((folio, line_id), 0)
        if pp < min_para_pos:
            continue
        positions, prefixes = [], []
        for i, t in enumerate(tokens_in_line):
            ok_, prefix = is_ey_no_articulator(t.word, morph)
            if not ok_:
                continue
            if prefix in ("sh", "ch"):
                positions.append(i / (n - 1))
                prefixes.append(prefix)
        if positions:
            line_items.append((positions, prefixes))

    def diff(line_items_, prefix_overrides=None):
        sh_positions, ch_positions = [], []
        for li_idx, (positions, prefixes) in enumerate(line_items_):
            current_prefixes = prefix_overrides[li_idx] if prefix_overrides else prefixes
            for p, pf in zip(positions, current_prefixes):
                if pf == "sh":
                    sh_positions.append(p)
                else:
                    ch_positions.append(p)
        sh_mean = sum(sh_positions) / len(sh_positions) if sh_positions else 0
        ch_mean = sum(ch_positions) / len(ch_positions) if ch_positions else 0
        return sh_mean - ch_mean, sh_mean, ch_mean, len(sh_positions), len(ch_positions)

    actual_diff, actual_sh_mean, actual_ch_mean, n_sh, n_ch = diff(line_items)

    # Permutation
    extreme = 0
    for _ in range(n_perm):
        overrides = []
        for positions, prefixes in line_items:
            shuffled = prefixes[:]
            random.shuffle(shuffled)
            overrides.append(shuffled)
        rd, _, _, _, _ = diff(line_items, overrides)
        if abs(rd) >= abs(actual_diff):
            extreme += 1

    return {
        "n_sh": n_sh, "n_ch": n_ch,
        "sh_mean": actual_sh_mean, "ch_mean": actual_ch_mean,
        "diff": actual_diff, "p_value": extreme / n_perm,
        "n_lines_pooled": len(line_items),
        "min_para_pos": min_para_pos,
    }


def main():
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    by_line, para_pos = gather_lines_with_para_pos(b_tokens)

    results = {}

    # === Per-prefix descriptives ===
    print("=== e -> y FRAME, BODY-ONLY (par-line >= 1), CURRIER B ===")
    by_prefix_body = collect_by_prefix(by_line, para_pos, morph, min_para_pos=1)
    body_stats = {}
    for prefix in ["ch", "sh", "ok", "ot", "lch", "lk", "yk", "ke", "lsh", "qo"]:
        positions = by_prefix_body.get(prefix, [])
        if len(positions) < 30:
            continue
        s = position_stats(positions)
        body_stats[prefix] = s
        print(f"  {prefix:<8} n={s['n']:>5} mean={s['mean']:.3f}  BC={s['bc']:.3f}  skew={s['skew']:+.3f}")
    results["body_only"] = body_stats

    # === Para-line >= 3 (header-leakage control) ===
    print("\n=== e -> y FRAME, PARA-LINE >= 3 ===")
    by_prefix_p3 = collect_by_prefix(by_line, para_pos, morph, min_para_pos=3)
    p3_stats = {}
    for prefix in ["ch", "sh", "ok", "ot"]:
        positions = by_prefix_p3.get(prefix, [])
        if len(positions) < 30:
            continue
        s = position_stats(positions)
        p3_stats[prefix] = s
        print(f"  {prefix:<8} n={s['n']:>5} mean={s['mean']:.3f}  BC={s['bc']:.3f}  skew={s['skew']:+.3f}")
    results["para_line_ge_3"] = p3_stats

    # === Section stratification ===
    print("\n=== SECTION-STRATIFIED (body-only) ===")
    section_stats = defaultdict(dict)
    for section in ["H", "B", "S", "C", "T"]:
        for prefix in ["ch", "sh", "ok", "ot"]:
            by_prefix = collect_by_prefix(by_line, para_pos, morph, min_para_pos=1, section_filter=section)
            positions = by_prefix.get(prefix, [])
            if len(positions) < 30:
                continue
            s = position_stats(positions)
            section_stats[section][prefix] = s
            print(f"  {section:<3} {prefix:<6} n={s['n']:>4} mean={s['mean']:.3f}  BC={s['bc']:.3f}  skew={s['skew']:+.3f}")
    results["section_stratified"] = {sec: dict(d) for sec, d in section_stats.items()}

    # === Permutation tests ===
    print("\n=== PERMUTATION TEST: sh vs ch on e->y frame (within-line shuffles) ===")
    perm_body = permutation_test_sh_vs_ch(by_line, para_pos, morph, n_perm=10000, min_para_pos=1)
    print(f"  Body-only: sh_mean={perm_body['sh_mean']:.3f} ch_mean={perm_body['ch_mean']:.3f} "
          f"diff={perm_body['diff']:+.3f} p={perm_body['p_value']:.4f}")
    print(f"             (n_sh={perm_body['n_sh']}, n_ch={perm_body['n_ch']}, "
          f"lines pooled={perm_body['n_lines_pooled']})")
    results["permutation_body_only"] = perm_body

    perm_p3 = permutation_test_sh_vs_ch(by_line, para_pos, morph, n_perm=10000, min_para_pos=3)
    print(f"  Para-line>=3: sh_mean={perm_p3['sh_mean']:.3f} ch_mean={perm_p3['ch_mean']:.3f} "
          f"diff={perm_p3['diff']:+.3f} p={perm_p3['p_value']:.4f}")
    print(f"                (n_sh={perm_p3['n_sh']}, n_ch={perm_p3['n_ch']}, "
          f"lines pooled={perm_p3['n_lines_pooled']})")
    results["permutation_para_line_ge_3"] = perm_p3

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
