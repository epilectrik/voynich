"""Phase 629 supplement: Null baseline for blind prediction scoring.

For each of the 7 matched chapters, formalizes the blind predictions
as quantitative binary tests (using corpus tertile thresholds), then
scores ALL Currier B folios against each prediction battery.

Compares the matched folio's score to the null distribution to determine
whether predictions are specific enough to discriminate the matched folio.

Key question: Does the matched folio score better than random folios?
"""

import sys, json, math
from collections import Counter, defaultdict
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
freq = Counter(t.word for t in tx.currier_b())

MON_PREFIXES = {'ch', 'sh', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch', 'lsh'}
CH_ACTIVE = {'ch', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch'}
SH_PASSIVE = {'sh', 'lsh'}


def spearman_rho(x, y):
    n = len(x)
    if n < 3:
        return 0.0
    def rank_vals(vals):
        indexed = sorted(enumerate(vals), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j+1][1] == indexed[j][1]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j+1):
                ranks[indexed[k][0]] = avg
            i = j + 1
        return ranks
    rx = rank_vals(x)
    ry = rank_vals(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


# ============================================================
# Build structural profiles for ALL Currier B folios
# ============================================================
print("Building structural profiles for all Currier B folios...")

folio_line_tokens = defaultdict(lambda: defaultdict(list))
for t in tx.currier_b():
    if not t.is_label:
        folio_line_tokens[t.folio][t.line].append(t)

# Build paragraphs
folio_paragraphs = defaultdict(list)
for folio in sorted(folio_line_tokens):
    lines_sorted = sorted(folio_line_tokens[folio].keys(),
                          key=lambda x: int(x) if x.isdigit() else 0)
    current_lines = []
    para_idx = 0
    for line_num in lines_sorted:
        lt = folio_line_tokens[folio][line_num]
        is_start = any(t.par_initial for t in lt)
        if is_start and current_lines:
            folio_paragraphs[folio].append((para_idx, current_lines))
            para_idx += 1
            current_lines = []
        current_lines.append(line_num)
    if current_lines:
        folio_paragraphs[folio].append((para_idx, current_lines))

# Compute features for all folios
profiles = {}
for folio in sorted(folio_line_tokens):
    tokens = [t for t in tx.currier_b() if t.folio == folio and not t.is_label]
    if len(tokens) < 10:
        continue

    n = len(tokens)
    prefix_counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        prefix_counts[m.prefix or '(none)'] += 1

    qo_rate = prefix_counts.get('qo', 0) / n
    ch_rate = sum(prefix_counts.get(p, 0) for p in CH_ACTIVE) / n
    sh_rate = sum(prefix_counts.get(p, 0) for p in SH_PASSIVE) / n
    ok_rate = prefix_counts.get('ok', 0) / n
    ot_rate = prefix_counts.get('ot', 0) / n
    da_rate = prefix_counts.get('da', 0) / n
    mon_rate = (ch_rate + sh_rate)

    hapax_count = sum(1 for t in tokens if freq[t.word] == 1)
    hapax_rate = hapax_count / n

    paras = folio_paragraphs.get(folio, [])
    n_paras = len(paras)

    # Max paragraph fraction
    para_tokens_list = []
    for pidx, plines in paras:
        pt = sum(len(folio_line_tokens[folio].get(l, [])) for l in plines)
        para_tokens_list.append(pt)
    max_para_frac = max(para_tokens_list) / n if para_tokens_list else 0

    # Monitoring gradient for longest paragraph
    longest_para = max(paras, key=lambda p: len(p[1])) if paras else (0, [])
    lp_lines = longest_para[1]
    mon_gradient = 0.0
    if len(lp_lines) >= 5:
        positions = []
        mon_r = []
        for i, ln in enumerate(lp_lines):
            lt = folio_line_tokens[folio].get(ln, [])
            nl = len(lt)
            if nl == 0:
                continue
            mon = sum(1 for t in lt if (morph.extract(t.word).prefix or '') in MON_PREFIXES)
            positions.append(i)
            mon_r.append(mon / nl)
        if len(positions) >= 5:
            mon_gradient = spearman_rho(positions, mon_r)

    profiles[folio] = {
        'n_tokens': n,
        'hapax_rate': hapax_rate,
        'n_paras': n_paras,
        'qo_rate': qo_rate,
        'ch_rate': ch_rate,
        'sh_rate': sh_rate,
        'mon_rate': mon_rate,
        'ok_rate': ok_rate,
        'ot_rate': ot_rate,
        'da_rate': da_rate,
        'max_para_frac': max_para_frac,
        'mon_gradient': mon_gradient,
        'longest_para_lines': len(lp_lines),
        'corr_rate': ok_rate + ot_rate,
    }

print(f"  {len(profiles)} folios profiled")

# ============================================================
# Compute corpus tertiles for thresholding
# ============================================================
def tertiles(values):
    s = sorted(values)
    n = len(s)
    return s[n // 3], s[2 * n // 3]

def quartiles(values):
    s = sorted(values)
    n = len(s)
    return s[n // 4], s[n // 2], s[3 * n // 4]

all_folios = sorted(profiles.keys())
corpus_stats = {}
for feat in ['hapax_rate', 'n_paras', 'qo_rate', 'ch_rate', 'sh_rate',
             'mon_rate', 'ok_rate', 'ot_rate', 'da_rate', 'max_para_frac',
             'mon_gradient', 'corr_rate']:
    vals = [profiles[f][feat] for f in all_folios]
    t1, t2 = tertiles(vals)
    q1, q2, q3 = quartiles(vals)
    corpus_stats[feat] = {
        'T1': t1, 'T2': t2,
        'Q1': q1, 'median': q2, 'Q3': q3,
        'min': min(vals), 'max': max(vals),
    }

print("\nCorpus tertile thresholds:")
for feat, s in corpus_stats.items():
    print(f"  {feat:>18s}: T1={s['T1']:.4f}  T2={s['T2']:.4f}  "
          f"(range {s['min']:.4f}-{s['max']:.4f})")


# ============================================================
# Define prediction batteries as quantitative binary tests
# ============================================================
# Each prediction: (description, lambda profile -> bool)
# Using tertile boundaries: LOW = below T1, HIGH = above T2, MODERATE = between

def in_low(feat):
    """Feature is in bottom tertile."""
    t1 = corpus_stats[feat]['T1']
    return lambda p: p[feat] <= t1

def in_high(feat):
    """Feature is in top tertile."""
    t2 = corpus_stats[feat]['T2']
    return lambda p: p[feat] >= t2

def in_mod(feat):
    """Feature is in middle tertile."""
    t1, t2 = corpus_stats[feat]['T1'], corpus_stats[feat]['T2']
    return lambda p: t1 < p[feat] < t2

def below_median(feat):
    med = corpus_stats[feat]['median']
    return lambda p: p[feat] <= med

def above_median(feat):
    med = corpus_stats[feat]['median']
    return lambda p: p[feat] > med

def below_threshold(feat, threshold):
    return lambda p: p[feat] <= threshold

def above_threshold(feat, threshold):
    return lambda p: p[feat] > threshold

def in_top_quartile(feat):
    q3 = corpus_stats[feat]['Q3']
    return lambda p: p[feat] >= q3

def in_bottom_quartile(feat):
    q1 = corpus_stats[feat]['Q1']
    return lambda p: p[feat] <= q1


# Prediction batteries formalized from _blind_predictions.md
BATTERIES = {
    'Ch14': {
        'matched_folio': 'f84r',
        'predictions': [
            ('LOW hapax rate', in_low('hapax_rate')),
            ('LOW monitoring gradient', below_threshold('mon_gradient', 0.3)),
            ('LOW-MODERATE paragraph count', below_median('n_paras')),
            ('LOW-MODERATE ch/sh rate', below_median('mon_rate')),
            ('da-prefix above median', above_median('da_rate')),
        ],
    },
    'Ch27': {
        'matched_folio': 'f77v',
        'predictions': [
            ('UNUSUAL para structure (dominant para)', above_median('max_para_frac')),
            ('LOW thermal gradient', below_median('qo_rate')),
            ('ok/ot enriched', above_median('corr_rate')),
            ('HIGH hapax rate', in_high('hapax_rate')),
            ('LOW monitoring gradient', below_threshold('mon_gradient', 0.2)),
        ],
    },
    'Ch9': {
        'matched_folio': 'f83r',
        'predictions': [
            ('HIGH hapax rate', in_high('hapax_rate')),
            ('HIGH paragraph count', in_high('n_paras')),
            ('Monitoring gradient present', above_threshold('mon_gradient', 0.3)),
            ('qo moderate-high', above_median('qo_rate')),
        ],
    },
    'Ch24': {
        'matched_folio': 'f84v',
        'predictions': [
            ('LOW paragraph count', in_low('n_paras')),
            ('LOW monitoring rate', in_low('mon_rate')),
            ('LOW hapax rate', in_low('hapax_rate')),
            # P5 from predictions.md actually PREDICTS the gradient anomaly
            # as a likely failure point, so include it as a negative test
            ('HIGH monitoring gradient (anomaly noted in predictions)',
             above_threshold('mon_gradient', 0.5)),
        ],
    },
    'Ch16': {
        'matched_folio': 'f108r',
        'predictions': [
            ('MODERATE monitoring', in_mod('mon_rate')),
            ('MODERATE hapax rate', in_mod('hapax_rate')),
            ('HIGH paragraph count', in_high('n_paras')),
            ('ok/ot enriched', above_median('corr_rate')),
        ],
    },
    'Ch11': {
        'matched_folio': 'f112r',
        'predictions': [
            ('MODERATE-HIGH monitoring', above_median('mon_rate')),
            ('MODERATE hapax rate', in_mod('hapax_rate')),
            ('MULTIPLE paragraphs', above_median('n_paras')),
            ('ok/ot correction enriched', above_median('corr_rate')),
            ('da-prefix for cohobation', above_median('da_rate')),
        ],
    },
    'Ch18t': {
        'matched_folio': 'f81v',
        'predictions': [
            ('HIGH monitoring density', in_high('mon_rate')),
            ('ch specifically enriched', in_high('ch_rate')),
            ('LOW thermal variation', below_median('qo_rate')),
            ('Dominant paragraph', above_median('max_para_frac')),
        ],
    },
}


# ============================================================
# Score all folios against each prediction battery
# ============================================================
print("\n" + "=" * 80)
print("NULL BASELINE: SCORING ALL FOLIOS AGAINST EACH PREDICTION BATTERY")
print("=" * 80)

results = {
    'method': 'Corpus tertile thresholding of blind predictions',
    'n_folios_scored': len(profiles),
    'per_chapter': {},
}

for ch_name, battery in BATTERIES.items():
    matched = battery['matched_folio']
    preds = battery['predictions']
    n_preds = len(preds)

    # Score all folios
    folio_scores = {}
    for folio in all_folios:
        p = profiles[folio]
        score = sum(1 for _, test in preds if test(p))
        folio_scores[folio] = score

    # Rank matched folio
    matched_score = folio_scores[matched]
    scores_list = sorted(folio_scores.values(), reverse=True)
    rank = scores_list.index(matched_score) + 1
    n_at_or_above = sum(1 for s in folio_scores.values() if s >= matched_score)
    p_value = n_at_or_above / len(folio_scores)

    # Score distribution
    score_dist = Counter(folio_scores.values())

    # Mean and std of null scores (excluding matched folio)
    null_scores = [s for f, s in folio_scores.items() if f != matched]
    null_mean = sum(null_scores) / len(null_scores)
    null_var = sum((s - null_mean)**2 for s in null_scores) / len(null_scores)
    null_std = null_var ** 0.5

    # Which predictions pass for the matched folio?
    matched_detail = []
    for desc, test in preds:
        passed = test(profiles[matched])
        matched_detail.append({'prediction': desc, 'pass': passed})

    print(f"\n  {ch_name} -> {matched}:")
    print(f"    Predictions: {n_preds}")
    print(f"    Matched folio score: {matched_score}/{n_preds}")
    print(f"    Null mean: {null_mean:.2f} (std={null_std:.2f})")
    print(f"    Rank: {rank}/{len(folio_scores)} "
          f"(p={p_value:.3f}, folios at or above: {n_at_or_above})")
    print(f"    Score distribution: ", end='')
    for s in range(n_preds + 1):
        c = score_dist.get(s, 0)
        if c > 0:
            print(f"{s}:{c}", end='  ')
    print()

    # Show prediction detail
    for d in matched_detail:
        status = 'PASS' if d['pass'] else 'FAIL'
        print(f"      [{status}] {d['prediction']}")

    # Top-scoring folios
    top_folios = sorted(folio_scores.items(), key=lambda x: -x[1])[:5]
    print(f"    Top 5 folios: ", end='')
    for f, s in top_folios:
        marker = ' <<<' if f == matched else ''
        print(f"{f}={s}{marker}", end='  ')
    print()

    results['per_chapter'][ch_name] = {
        'matched_folio': matched,
        'n_predictions': n_preds,
        'matched_score': matched_score,
        'null_mean': round(null_mean, 3),
        'null_std': round(null_std, 3),
        'rank': rank,
        'n_folios': len(folio_scores),
        'p_value': round(p_value, 4),
        'n_at_or_above': n_at_or_above,
        'score_distribution': {str(k): v for k, v in sorted(score_dist.items())},
        'matched_detail': matched_detail,
        'top5': [{'folio': f, 'score': s} for f, s in top_folios],
    }


# ============================================================
# Aggregate summary
# ============================================================
print("\n" + "=" * 80)
print("AGGREGATE SUMMARY")
print("=" * 80)

total_matched_score = 0
total_preds = 0
total_null_scores = 0.0  # sum of null_mean (not weighted)
n_chapters = len(BATTERIES)
sig_count = 0

for ch_name, r in results['per_chapter'].items():
    total_matched_score += r['matched_score']
    total_preds += r['n_predictions']
    total_null_scores += r['null_mean']
    if r['p_value'] <= 0.20:
        sig_count += 1

# Aggregate null rate: sum of null_means / sum of n_predictions
weighted_null_rate = total_null_scores / total_preds if total_preds else 0
matched_rate = total_matched_score / total_preds if total_preds else 0

print(f"\n  Matched folios aggregate: {total_matched_score}/{total_preds} "
      f"({matched_rate:.1%})")
print(f"  Null (random folio) rate: {weighted_null_rate:.1%}")
print(f"  Lift over null: {matched_rate / weighted_null_rate:.2f}x" if weighted_null_rate > 0 else "")
print(f"  Chapters with p <= 0.20: {sig_count}/{n_chapters}")

# Per-chapter summary table
print(f"\n  {'Chapter':>8s}  {'Folio':>6s}  {'Score':>6s}  {'Null':>6s}  {'Rank':>8s}  {'p':>6s}")
print(f"  {'-'*48}")
for ch_name in BATTERIES:
    r = results['per_chapter'][ch_name]
    print(f"  {ch_name:>8s}  {r['matched_folio']:>6s}  "
          f"{r['matched_score']}/{r['n_predictions']}     "
          f"{r['null_mean']:.1f}     "
          f"{r['rank']:>3d}/{r['n_folios']}   "
          f"{r['p_value']:.3f}")

results['aggregate'] = {
    'total_matched_score': total_matched_score,
    'total_predictions': total_preds,
    'matched_rate': round(matched_rate, 4),
    'null_rate': round(weighted_null_rate, 4),
    'lift': round(matched_rate / weighted_null_rate, 3) if weighted_null_rate > 0 else None,
    'chapters_p_le_020': sig_count,
    'note': 'null_rate = sum(null_mean per chapter) / sum(n_predictions per chapter)',
}

# Write results
output_path = 'C:/git/voynich/phases/CRIB_DECODE_VALIDATION/results/null_baseline.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results written to: {output_path}")
