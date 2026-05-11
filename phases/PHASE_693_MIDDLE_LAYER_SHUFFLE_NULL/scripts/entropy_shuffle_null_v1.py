"""Off-books triple conditional entropy test for SUFFIX/coda.

Discriminator proposed by an independent cold-read of the H-track transcript:
  H(coda | stem) vs H(coda | previous coda) vs H(coda | line-position)

  - If H(coda | stem) is smallest -> coda is lexically bound to stem
    (natural-language-like signature; suffixes are part of word lexicon).
  - If H(coda | previous coda) is smallest -> coda is determined by the
    previous coda (state-machine / control-grammar signature).
  - If H(coda | position) is smallest -> coda is determined by line position
    (formulary/template register signature).

Computes the three conditional entropies and their mutual-information
reductions vs marginal H(coda). Reports for full H-track, Currier B only,
and Currier A only. NOT registered as a constraint -- exploratory only.
"""
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

POSITION_BINS = 10
MIN_STEM_COUNT = 20  # filter unreliable conditional entropies


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c == 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


def cond_entropy(joint_counts, marginal_counts):
    """H(Y|X) = sum_x p(x) H(Y|X=x)."""
    total = sum(marginal_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for x, n_x in marginal_counts.items():
        p_x = n_x / total
        ys = joint_counts.get(x, {})
        h_y_given_x = entropy(ys)
        h += p_x * h_y_given_x
    return h


def collect_tokens(tx, morph, currier=None):
    """Yield (folio, line_label, line_idx, n_in_line, position, prefix, middle, suffix)
    for filtered tokens."""
    # Group tokens by (folio, line) so we can compute within-line position.
    by_line = defaultdict(list)
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        if currier == 'A' and tok.language != 'A':
            continue
        if currier == 'B' and tok.language != 'B':
            continue
        # Skip labels (LABEL_PREFIX 'L') and ring/star/circle placements; keep P*.
        if not (tok.placement and tok.placement.startswith('P')):
            continue
        by_line[(tok.folio, tok.line)].append(tok)

    out = []
    for (folio, line), toks in by_line.items():
        n = len(toks)
        if n == 0:
            continue
        for i, tok in enumerate(toks):
            m = morph.extract(tok.word)
            if m.middle is None or m.suffix is None:
                continue
            pos_bin = min(POSITION_BINS - 1, int(POSITION_BINS * i / max(1, n)))
            out.append({
                'folio': folio,
                'line': line,
                'pos_idx': i,
                'pos_bin': pos_bin,
                'prefix': m.prefix or '_',
                'middle': m.middle,  # this is our "stem"
                'suffix': m.suffix,  # this is our "coda"
                'line_idx': len(out),
            })
    return out


def analyze(rows, label):
    if not rows:
        print(f"\n=== {label}: NO ROWS ===")
        return
    n = len(rows)
    suffixes = [r['suffix'] for r in rows]
    middles = [r['middle'] for r in rows]
    pos_bins = [r['pos_bin'] for r in rows]

    # Marginal H(coda)
    suffix_counts = Counter(suffixes)
    h_coda = entropy(suffix_counts)

    # H(coda | stem) -- filter stems with at least MIN_STEM_COUNT occurrences
    stem_counts_full = Counter(middles)
    keep_stems = {s for s, c in stem_counts_full.items() if c >= MIN_STEM_COUNT}
    stem_joint = defaultdict(Counter)
    stem_marg = Counter()
    n_kept_stem = 0
    for r in rows:
        if r['middle'] in keep_stems:
            stem_joint[r['middle']][r['suffix']] += 1
            stem_marg[r['middle']] += 1
            n_kept_stem += 1
    h_coda_given_stem = cond_entropy(stem_joint, stem_marg)

    # H(coda | previous coda) -- sequential within line
    prev_joint = defaultdict(Counter)
    prev_marg = Counter()
    # Group sequential pairs by (folio, line) again
    rows_by_line = defaultdict(list)
    for r in rows:
        rows_by_line[(r['folio'], r['line'])].append(r)
    for key, lst in rows_by_line.items():
        lst.sort(key=lambda r: r['pos_idx'])
        for a, b in zip(lst, lst[1:]):
            prev_joint[a['suffix']][b['suffix']] += 1
            prev_marg[a['suffix']] += 1
    h_coda_given_prev = cond_entropy(prev_joint, prev_marg)
    n_pairs = sum(prev_marg.values())

    # H(coda | position bin)
    pos_joint = defaultdict(Counter)
    pos_marg = Counter()
    for r in rows:
        pos_joint[r['pos_bin']][r['suffix']] += 1
        pos_marg[r['pos_bin']] += 1
    h_coda_given_pos = cond_entropy(pos_joint, pos_marg)

    # Mutual information = H(Y) - H(Y|X)
    mi_stem = h_coda - h_coda_given_stem
    mi_prev = h_coda - h_coda_given_prev
    mi_pos = h_coda - h_coda_given_pos

    print(f"\n=== {label} (n={n} tokens, {len(rows_by_line)} lines) ===")
    print(f"  Marginal H(coda)         = {h_coda:.4f} bits")
    print(f"  H(coda | stem)           = {h_coda_given_stem:.4f}  [I={mi_stem:+.4f}, "
          f"n_used={n_kept_stem}, n_stems_kept={len(keep_stems)}/{len(stem_counts_full)}]")
    print(f"  H(coda | prev_coda)      = {h_coda_given_prev:.4f}  [I={mi_prev:+.4f}, "
          f"n_pairs={n_pairs}]")
    print(f"  H(coda | line_pos_bin)   = {h_coda_given_pos:.4f}  [I={mi_pos:+.4f}, "
          f"n_bins={len(pos_marg)}]")

    # Rank
    ranking = sorted(
        [('stem', mi_stem), ('prev_coda', mi_prev), ('line_pos', mi_pos)],
        key=lambda kv: -kv[1],
    )
    print(f"  RANKED (most informative -> least):")
    for k, v in ranking:
        print(f"    {k:>10s}: I = {v:.4f} bits  ({100*v/max(0.001,h_coda):.1f}% of H(coda))")

    # Sanity: top suffixes
    top = suffix_counts.most_common(10)
    print(f"  Top 10 suffixes: {top}")
    print(f"  Unique suffixes: {len(suffix_counts)}")
    return {
        'label': label,
        'n': n,
        'h_coda': h_coda,
        'h_coda_given_stem': h_coda_given_stem,
        'h_coda_given_prev': h_coda_given_prev,
        'h_coda_given_pos': h_coda_given_pos,
        'mi_stem': mi_stem,
        'mi_prev': mi_prev,
        'mi_pos': mi_pos,
    }


def _shuffle_within_line_prev_middle_MI(rows, n_shuffles=20, seed=0):
    """Null distribution for I(middle; prev_middle) under within-line shuffle.
    Repetition (chol chol chol) survives shuffling within a line — so any
    signal above this null is genuine sequential dependency beyond bag-of-line
    composition."""
    import random
    rng = random.Random(seed)

    rows_by_line = defaultdict(list)
    for r in rows:
        rows_by_line[(r['folio'], r['line'])].append(r)

    h_marginal = entropy(Counter(r['middle'] for r in rows))

    mis = []
    for shuf_i in range(n_shuffles):
        joint = defaultdict(Counter)
        marg = Counter()
        for key, lst in rows_by_line.items():
            shuffled = [r['middle'] for r in lst]
            rng.shuffle(shuffled)
            for a, b in zip(shuffled, shuffled[1:]):
                joint[a][b] += 1
                marg[a] += 1
        h_cond = cond_entropy(joint, marg)
        mis.append(h_marginal - h_cond)
    mean = sum(mis) / len(mis)
    sd = (sum((x - mean) ** 2 for x in mis) / len(mis)) ** 0.5
    return mean, sd, mis


def analyze_middle_layer(rows, label):
    """Same triple-entropy test, but targets MIDDLE/stem (the layer where
    the project's state-machine actually lives, per C109/C997 forbidden
    MIDDLE bigrams). Predictors: prefix, previous middle, line position."""
    if not rows:
        print(f"\n=== {label} (MIDDLE layer): NO ROWS ===")
        return None
    n = len(rows)
    middles = [r['middle'] for r in rows]
    middle_counts = Counter(middles)
    h_mid = entropy(middle_counts)

    # I(middle; prefix) — only keep prefixes with >= MIN_STEM_COUNT
    prefix_counts_full = Counter(r['prefix'] for r in rows)
    keep_prefixes = {p for p, c in prefix_counts_full.items() if c >= MIN_STEM_COUNT}
    pre_joint = defaultdict(Counter)
    pre_marg = Counter()
    n_kept_pre = 0
    for r in rows:
        if r['prefix'] in keep_prefixes:
            pre_joint[r['prefix']][r['middle']] += 1
            pre_marg[r['prefix']] += 1
            n_kept_pre += 1
    h_mid_given_pre = cond_entropy(pre_joint, pre_marg)

    # I(middle; prev_middle) — sequential within line
    prev_joint = defaultdict(Counter)
    prev_marg = Counter()
    rows_by_line = defaultdict(list)
    for r in rows:
        rows_by_line[(r['folio'], r['line'])].append(r)
    for key, lst in rows_by_line.items():
        lst.sort(key=lambda r: r['pos_idx'])
        for a, b in zip(lst, lst[1:]):
            prev_joint[a['middle']][b['middle']] += 1
            prev_marg[a['middle']] += 1
    h_mid_given_prev = cond_entropy(prev_joint, prev_marg)
    n_pairs = sum(prev_marg.values())

    # I(middle; position)
    pos_joint = defaultdict(Counter)
    pos_marg = Counter()
    for r in rows:
        pos_joint[r['pos_bin']][r['middle']] += 1
        pos_marg[r['pos_bin']] += 1
    h_mid_given_pos = cond_entropy(pos_joint, pos_marg)

    mi_pre = h_mid - h_mid_given_pre
    mi_prev = h_mid - h_mid_given_prev
    mi_pos = h_mid - h_mid_given_pos

    print(f"\n--- {label} MIDDLE layer (n={n} tokens) ---")
    print(f"  Marginal H(middle)        = {h_mid:.4f} bits  (n_unique={len(middle_counts)})")
    print(f"  H(middle | prefix)        = {h_mid_given_pre:.4f}  [I={mi_pre:+.4f}, n_kept_prefixes={len(keep_prefixes)}/{len(prefix_counts_full)}]")
    print(f"  H(middle | prev_middle)   = {h_mid_given_prev:.4f}  [I={mi_prev:+.4f}, n_pairs={n_pairs}]")
    print(f"  H(middle | line_pos_bin)  = {h_mid_given_pos:.4f}  [I={mi_pos:+.4f}, n_bins={len(pos_marg)}]")
    ranking = sorted([('prefix', mi_pre), ('prev_middle', mi_prev), ('line_pos', mi_pos)],
                     key=lambda kv: -kv[1])
    print(f"  RANKED:")
    for k, v in ranking:
        print(f"    {k:>12s}: I = {v:.4f} bits  ({100*v/max(0.001,h_mid):.1f}% of H(middle))")

    # Within-line shuffle null for I(middle; prev_middle)
    null_mean, null_sd, _ = _shuffle_within_line_prev_middle_MI(rows, n_shuffles=20)
    z = (mi_prev - null_mean) / max(null_sd, 1e-9)
    excess = mi_prev - null_mean
    print(f"  WITHIN-LINE-SHUFFLE NULL for I(middle; prev_middle):")
    print(f"    null I mean = {null_mean:.4f} +/- {null_sd:.4f}  (20 shuffles)")
    print(f"    real I      = {mi_prev:.4f}")
    print(f"    excess      = {excess:+.4f} bits  (z = {z:.2f})")
    return {
        'label': label + ' (middle)',
        'n': n,
        'h_middle': h_mid,
        'mi_prefix': mi_pre,
        'mi_prev_middle': mi_prev,
        'mi_pos_middle': mi_pos,
    }


def main():
    print("Loading transcript + morphology...")
    tx = Transcript()
    morph = Morphology()

    print("Collecting tokens (H-track, paragraph only, decomposable morphology)...")
    rows_all = collect_tokens(tx, morph, currier=None)
    rows_a = collect_tokens(tx, morph, currier='A')
    rows_b = collect_tokens(tx, morph, currier='B')

    # Layer 1: SUFFIX (coda) — what the cold agent specified
    print("\n###########################################################")
    print("# LAYER 1: SUFFIX/coda — cold agent's stated discriminator #")
    print("###########################################################")
    results = []
    results.append(analyze(rows_all, "H-track FULL"))
    results.append(analyze(rows_b, "Currier B only"))
    results.append(analyze(rows_a, "Currier A only"))

    print("\n=== SUFFIX-LAYER SUMMARY (Mutual Info I(coda; X) in bits) ===")
    print(f"{'subset':<20s}  {'H(coda)':>8s}  {'I(stem)':>8s}  {'I(prev_coda)':>13s}  {'I(line_pos)':>12s}  {'winner':<12s}")
    for r in results:
        if r is None:
            continue
        ranks = {'stem': r['mi_stem'], 'prev_coda': r['mi_prev'], 'line_pos': r['mi_pos']}
        winner = max(ranks, key=ranks.get)
        print(f"  {r['label']:<18s}  {r['h_coda']:>8.4f}  {r['mi_stem']:>8.4f}  "
              f"{r['mi_prev']:>13.4f}  {r['mi_pos']:>12.4f}  {winner}")

    # Layer 2: MIDDLE/stem — where C109/C997 forbidden bigrams actually live
    print("\n###############################################################")
    print("# LAYER 2: MIDDLE/stem — where project's state machine lives  #")
    print("###############################################################")
    mid_results = []
    mid_results.append(analyze_middle_layer(rows_all, "H-track FULL"))
    mid_results.append(analyze_middle_layer(rows_b, "Currier B only"))
    mid_results.append(analyze_middle_layer(rows_a, "Currier A only"))

    print("\n=== MIDDLE-LAYER SUMMARY (Mutual Info I(middle; X) in bits) ===")
    print(f"{'subset':<25s}  {'H(mid)':>8s}  {'I(prefix)':>10s}  {'I(prev_middle)':>15s}  {'I(line_pos)':>12s}  {'winner':<14s}")
    for r in mid_results:
        if r is None:
            continue
        ranks = {'prefix': r['mi_prefix'], 'prev_middle': r['mi_prev_middle'], 'line_pos': r['mi_pos_middle']}
        winner = max(ranks, key=ranks.get)
        print(f"  {r['label']:<23s}  {r['h_middle']:>8.4f}  {r['mi_prefix']:>10.4f}  "
              f"{r['mi_prev_middle']:>15.4f}  {r['mi_pos_middle']:>12.4f}  {winner}")


if __name__ == '__main__':
    main()
