"""T1/T2/T3 follow-up tests after expert review of _entropy_triple_test.py.

T1: Stratify MIDDLE-layer shuffle null by section.
    Prediction (per C1048): BIO section has strongest residual sequential
    structure in B; if all sections are flat, original finding holds for
    the whole of B.

T2: Forward vs backward direction on the 17 forbidden MIDDLE pairs.
    For each pair (A, B), count adjacent occurrences in real order:
       fwd = count(M_t=A AND M_{t+1}=B)
       bwd = count(M_t=B AND M_{t+1}=A)
    Compare both to within-line shuffle null. If fwd >> bwd, transitional.
    If fwd ~~ bwd (both small or both near-null), co-occurrence-forbidden.

T3 (KILLER): Repeat shuffle null at the 49-class layer instead of the
    MIDDLE-string layer. Each token mapped to its class id via
    class_token_map.json. Predicted: if class-layer survives null while
    MIDDLE-layer doesn't, clean separation: macro-state automaton is
    genuinely sequential, MIDDLE pairs are co-occurrence. If class-layer
    ALSO fails the null, bigger reframing story.

Off-books exploratory. Not registered until results discussed.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

POSITION_BINS = 10
N_SHUFFLES = 30


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
    total = sum(marginal_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for x, n_x in marginal_counts.items():
        p_x = n_x / total
        ys = joint_counts.get(x, {})
        h += p_x * entropy(ys)
    return h


def collect_tokens(tx, morph, currier=None, section=None):
    by_line = defaultdict(list)
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        if currier and tok.language != currier:
            continue
        if section and tok.section != section:
            continue
        if not (tok.placement and tok.placement.startswith('P')):
            continue
        by_line[(tok.folio, tok.line)].append(tok)
    out = []
    for (folio, line), toks in by_line.items():
        n = len(toks)
        for i, tok in enumerate(toks):
            m = morph.extract(tok.word)
            if m.middle is None or m.suffix is None:
                continue
            pos_bin = min(POSITION_BINS - 1, int(POSITION_BINS * i / max(1, n)))
            out.append({
                'folio': folio, 'line': line, 'pos_idx': i, 'pos_bin': pos_bin,
                'prefix': m.prefix or '_', 'middle': m.middle, 'suffix': m.suffix,
                'word': tok.word,
            })
    return out


def attach_class_ids(rows, token_to_class):
    """Add a 'class_id' field to each row using the token-level lookup."""
    n_hit = 0
    for r in rows:
        cid = token_to_class.get(r['word'])
        r['class_id'] = cid  # None if not classified
        if cid is not None:
            n_hit += 1
    return n_hit


def shuffle_null_MI(rows, key='middle', n_shuffles=N_SHUFFLES, seed=0):
    """Within-line shuffle null for I(key; prev_key)."""
    rng = random.Random(seed)
    rows_by_line = defaultdict(list)
    for r in rows:
        if r.get(key) is None:
            continue
        rows_by_line[(r['folio'], r['line'])].append(r)
    h_marg = entropy(Counter(r[key] for r in rows if r.get(key) is not None))
    mis = []
    for _ in range(n_shuffles):
        joint = defaultdict(Counter)
        marg = Counter()
        for key_id, lst in rows_by_line.items():
            shuffled = [r[key] for r in lst]
            rng.shuffle(shuffled)
            for a, b in zip(shuffled, shuffled[1:]):
                joint[a][b] += 1
                marg[a] += 1
        h_cond = cond_entropy(joint, marg)
        mis.append(h_marg - h_cond)
    mean = sum(mis) / len(mis)
    sd = (sum((x - mean) ** 2 for x in mis) / len(mis)) ** 0.5 if len(mis) > 1 else 0.0
    return mean, sd


def real_prev_MI(rows, key='middle'):
    """Real I(key; prev_key) within line."""
    rows_by_line = defaultdict(list)
    for r in rows:
        if r.get(key) is None:
            continue
        rows_by_line[(r['folio'], r['line'])].append(r)
    h_marg = entropy(Counter(r[key] for r in rows if r.get(key) is not None))
    joint = defaultdict(Counter)
    marg = Counter()
    for key_id, lst in rows_by_line.items():
        lst.sort(key=lambda r: r['pos_idx'])
        for a, b in zip(lst, lst[1:]):
            joint[a[key]][b[key]] += 1
            marg[a[key]] += 1
    h_cond = cond_entropy(joint, marg)
    return h_marg, h_marg - h_cond, sum(marg.values())


# ======================================================================
# T1: Per-section shuffle null
# ======================================================================
def t1_per_section(tx, morph):
    print("\n" + "=" * 70)
    print("T1: MIDDLE-layer shuffle null stratified by section")
    print("=" * 70)
    # Currier B is distributed across sections; stratify by section using only B-language tokens.
    sections = ['B', 'C', 'H', 'S', 'T']  # B-language present in these sections
    print(f"\n{'section':>10s}  {'n_tok':>6s}  {'H(mid)':>7s}  {'real_I':>7s}  {'null_I':>7s}  {'excess':>8s}  {'z':>7s}")
    for sec in sections:
        rows = [r for r in collect_tokens(tx, morph, currier='B', section=sec)]
        if len(rows) < 100:
            print(f"  {sec:>8s}  {len(rows):>6d}  -- too few tokens --")
            continue
        h_marg, real_mi, n_pairs = real_prev_MI(rows, key='middle')
        null_mean, null_sd = shuffle_null_MI(rows, key='middle', n_shuffles=N_SHUFFLES)
        excess = real_mi - null_mean
        z = excess / max(null_sd, 1e-9)
        print(f"  {sec:>8s}  {len(rows):>6d}  {h_marg:>7.4f}  {real_mi:>7.4f}  "
              f"{null_mean:>7.4f}  {excess:>+8.4f}  {z:>+7.2f}")


# ======================================================================
# T2: Forward vs backward count on 17 forbidden pairs
# ======================================================================
def t2_directional_forbidden(rows, forbidden_pairs):
    """Count adjacent occurrences forward and backward for each forbidden pair.
    Compare both to within-line shuffle null distribution."""
    print("\n" + "=" * 70)
    print("T2: Forward vs backward count for 17 forbidden MIDDLE pairs")
    print("=" * 70)
    print("(real fwd = count(A then B); real bwd = count(B then A); both line-internal)")
    rows_by_line = defaultdict(list)
    for r in rows:
        rows_by_line[(r['folio'], r['line'])].append(r)

    # Real counts
    fwd_real = Counter()
    bwd_real = Counter()
    same_line = Counter()  # how many lines contain both A and B (in either order)
    pair_set = set(forbidden_pairs)
    rev_set = {(b, a) for (a, b) in forbidden_pairs}
    for key_id, lst in rows_by_line.items():
        lst.sort(key=lambda r: r['pos_idx'])
        middles = [r['middle'] for r in lst]
        # adjacent
        for x, y in zip(middles, middles[1:]):
            if (x, y) in pair_set:
                fwd_real[(x, y)] += 1
            if (x, y) in rev_set:
                bwd_real[(y, x)] += 1
        # bag membership for forbidden pairs
        mid_set = set(middles)
        for (a, b) in forbidden_pairs:
            if a in mid_set and b in mid_set:
                same_line[(a, b)] += 1

    # Null: within-line shuffle, average count of fwd and bwd
    rng = random.Random(42)
    fwd_null_sum = Counter()
    bwd_null_sum = Counter()
    for _ in range(N_SHUFFLES):
        for key_id, lst in rows_by_line.items():
            middles = [r['middle'] for r in lst]
            shuf = list(middles)
            rng.shuffle(shuf)
            for x, y in zip(shuf, shuf[1:]):
                if (x, y) in pair_set:
                    fwd_null_sum[(x, y)] += 1
                if (x, y) in rev_set:
                    bwd_null_sum[(y, x)] += 1
    # Average across shuffles
    fwd_null = {k: v / N_SHUFFLES for k, v in fwd_null_sum.items()}
    bwd_null = {k: v / N_SHUFFLES for k, v in bwd_null_sum.items()}

    print(f"\n{'pair (A->B)':<22s}  {'real_fwd':>8s}  {'null_fwd':>8s}  "
          f"{'real_bwd':>8s}  {'null_bwd':>8s}  {'same_line':>9s}  {'verdict':<24s}")
    total_real_fwd = 0
    total_null_fwd = 0.0
    total_real_bwd = 0
    total_null_bwd = 0.0
    total_same_line = 0
    for (a, b) in forbidden_pairs:
        rf = fwd_real.get((a, b), 0)
        rb = bwd_real.get((a, b), 0)
        nf = fwd_null.get((a, b), 0.0)
        nb = bwd_null.get((a, b), 0.0)
        sl = same_line.get((a, b), 0)
        # Verdict per pair
        if nf < 0.5 and nb < 0.5:
            verdict = "no-cooccur (phantom?)"
        elif rf < 0.5 * nf and rb < 0.5 * nb:
            verdict = "BOTH-SUPPRESSED (cooccur)"
        elif rf < 0.5 * nf:
            verdict = "FWD-only suppressed"
        elif rb < 0.5 * nb:
            verdict = "BWD-only suppressed"
        else:
            verdict = "no suppression"
        print(f"  {a+' -> '+b:<22s}  {rf:>8d}  {nf:>8.2f}  {rb:>8d}  {nb:>8.2f}  "
              f"{sl:>9d}  {verdict}")
        total_real_fwd += rf
        total_null_fwd += nf
        total_real_bwd += rb
        total_null_bwd += nb
        total_same_line += sl
    print(f"\n{'TOTAL':<22s}  {total_real_fwd:>8d}  {total_null_fwd:>8.2f}  "
          f"{total_real_bwd:>8d}  {total_null_bwd:>8.2f}  {total_same_line:>9d}")
    print(f"\n  Forward suppression: real {total_real_fwd} vs null {total_null_fwd:.2f}  "
          f"(ratio={total_real_fwd/max(0.01,total_null_fwd):.3f})")
    print(f"  Backward suppression: real {total_real_bwd} vs null {total_null_bwd:.2f}  "
          f"(ratio={total_real_bwd/max(0.01,total_null_bwd):.3f})")
    if total_null_fwd > 0 and total_null_bwd > 0:
        print(f"  Asymmetry (fwd_ratio vs bwd_ratio): "
              f"{(total_real_fwd/total_null_fwd) / max(0.01, total_real_bwd/total_null_bwd):.3f}")
    print(f"  Co-occurrence (both in same line): {total_same_line} pairs/lines (compare to total real adjacencies {total_real_fwd + total_real_bwd})")


# ======================================================================
# T3 (KILLER): Class-layer shuffle null
# ======================================================================
def t3_class_layer(rows, label):
    print(f"\n  --- {label} ---")
    # filter to tokens with class_id
    classed = [r for r in rows if r.get('class_id') is not None]
    n_classed = len(classed)
    n_total = len(rows)
    coverage = n_classed / max(1, n_total)
    print(f"  Class coverage: {n_classed}/{n_total} = {100*coverage:.1f}%")
    if n_classed < 500:
        print("  Too few classed tokens, skip.")
        return None
    h_marg, real_mi, n_pairs = real_prev_MI(classed, key='class_id')
    null_mean, null_sd = shuffle_null_MI(classed, key='class_id', n_shuffles=N_SHUFFLES)
    excess = real_mi - null_mean
    z = excess / max(null_sd, 1e-9)
    print(f"  H(class)             = {h_marg:.4f} bits  (n_unique={len(set(r['class_id'] for r in classed))})")
    print(f"  Real I(class; prev)  = {real_mi:.4f}  (n_pairs={n_pairs})")
    print(f"  Null mean +/- sd     = {null_mean:.4f} +/- {null_sd:.4f}  (N={N_SHUFFLES} shuffles)")
    print(f"  Excess (real - null) = {excess:+.4f} bits  (z = {z:+.2f})")
    if z > 3:
        print(f"  -> Class-layer survives shuffle null. Macro-state automaton is genuinely sequential.")
    elif z < -3:
        print(f"  -> Class-layer FAILS shuffle null. Even class-layer transitions are co-occurrence-driven.")
    else:
        print(f"  -> Class-layer is at-null. Marginal effect.")
    return {'real': real_mi, 'null_mean': null_mean, 'null_sd': null_sd, 'z': z, 'h': h_marg}


def main():
    print("Loading transcript + morphology + class lookup...")
    tx = Transcript()
    morph = Morphology()
    ctm_path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    ctm = json.loads(ctm_path.read_text())
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    print(f"  Loaded {len(token_to_class)} token->class mappings.")

    # T1: per-section stratification within Currier B
    t1_per_section(tx, morph)

    # T2: directional forbidden-pair analysis on B
    forbidden_path = PROJECT_ROOT / 'phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json'
    forbidden = json.loads(forbidden_path.read_text())
    forbidden_pairs = [(t['source'], t['target']) for t in forbidden['transitions']]
    print(f"\nLoaded {len(forbidden_pairs)} forbidden pairs.")
    rows_b = collect_tokens(tx, morph, currier='B')
    attach_class_ids(rows_b, token_to_class)
    t2_directional_forbidden(rows_b, forbidden_pairs)

    # T3 (KILLER): class-layer shuffle null
    print("\n" + "=" * 70)
    print("T3 (KILLER): Class-layer shuffle null")
    print("=" * 70)
    rows_all = collect_tokens(tx, morph)
    attach_class_ids(rows_all, token_to_class)
    rows_a = collect_tokens(tx, morph, currier='A')
    attach_class_ids(rows_a, token_to_class)

    t3_class_layer(rows_all, "H-track FULL")
    t3_class_layer(rows_b, "Currier B only")
    t3_class_layer(rows_a, "Currier A only")


if __name__ == '__main__':
    main()
