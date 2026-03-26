"""Gradient rarity test: how rare is f76r P1's monotonic monitoring gradient?

For every B paragraph with 15+ body lines, compute Spearman correlation
of monitoring PREFIX fraction (ch+sh) vs line position. Rank f76r P1.

Also decompose: is the gradient ch-dominant (active test) or sh-dominant
(passive monitor)?
"""

import sys, math
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict

tx = Transcript()
morph = Morphology()

MONITORING_PREFIXES = {'ch', 'sh', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch', 'lsh'}
CH_ACTIVE = {'ch', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch'}
SH_PASSIVE = {'sh', 'lsh'}


def spearman_rho(x, y):
    """Compute Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0

    def rank_vals(vals):
        indexed = sorted(enumerate(vals), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rx = rank_vals(x)
    ry = rank_vals(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


# ============================================================
# Build paragraph data for ALL Currier B folios
# ============================================================
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for t in tx.currier_b():
    folio_line_tokens[t.folio][t.line].append(t)

# Detect paragraphs via par_initial
paragraphs = []  # (folio, para_idx, line_list, token_list)

for folio in sorted(folio_line_tokens):
    lines_sorted = sorted(folio_line_tokens[folio].keys(),
                          key=lambda x: int(x) if x.isdigit() else 0)
    current_lines = []
    current_tokens = []
    para_idx = 0

    for line_num in lines_sorted:
        lt = folio_line_tokens[folio][line_num]
        is_start = any(t.par_initial for t in lt)

        if is_start and current_lines:
            paragraphs.append((folio, para_idx, current_lines, current_tokens))
            para_idx += 1
            current_lines = []
            current_tokens = []

        current_lines.append(line_num)
        current_tokens.extend(lt)

    if current_lines:
        paragraphs.append((folio, para_idx, current_lines, current_tokens))

# ============================================================
# For each paragraph with 15+ lines: compute monitoring gradient
# ============================================================
MIN_LINES = 15
results = []

for folio, pidx, plines, ptokens in paragraphs:
    if len(plines) < MIN_LINES:
        continue

    # Per-line monitoring rate
    line_positions = []
    mon_rates = []
    ch_rates = []
    sh_rates = []

    for i, line_num in enumerate(plines):
        lt = folio_line_tokens[folio][line_num]
        n = len(lt)
        if n == 0:
            continue

        mon = 0
        ch_count = 0
        sh_count = 0
        for t in lt:
            m = morph.extract(t.word)
            p = m.prefix or ''
            if p in MONITORING_PREFIXES:
                mon += 1
            if p in CH_ACTIVE:
                ch_count += 1
            if p in SH_PASSIVE:
                sh_count += 1

        line_positions.append(i)
        mon_rates.append(mon / n)
        ch_rates.append(ch_count / n)
        sh_rates.append(sh_count / n)

    if len(line_positions) < MIN_LINES:
        continue

    rho_mon = spearman_rho(line_positions, mon_rates)
    rho_ch = spearman_rho(line_positions, ch_rates)
    rho_sh = spearman_rho(line_positions, sh_rates)

    # Gradient magnitude: difference between first-third and last-third means
    n = len(mon_rates)
    third = n // 3
    first_third_mean = sum(mon_rates[:third]) / third if third > 0 else 0
    last_third_mean = sum(mon_rates[-third:]) / third if third > 0 else 0
    gradient_mag = last_third_mean - first_third_mean

    results.append({
        'folio': folio,
        'para_idx': pidx,
        'n_lines': len(plines),
        'n_tokens': len(ptokens),
        'rho_mon': rho_mon,
        'rho_ch': rho_ch,
        'rho_sh': rho_sh,
        'gradient_mag': gradient_mag,
        'first_third': first_third_mean,
        'last_third': last_third_mean,
    })

# ============================================================
# Results
# ============================================================
print("=" * 80)
print(f"MONITORING GRADIENT RARITY TEST")
print(f"Paragraphs with {MIN_LINES}+ lines: {len(results)}")
print("=" * 80)

# Sort by rho_mon descending (strongest positive gradients first)
results.sort(key=lambda x: -x['rho_mon'])

print(f"\n{'Rank':>4s} {'Folio':>8s} {'P#':>3s} {'Lines':>5s} {'Toks':>5s} "
      f"{'rho_mon':>8s} {'rho_ch':>8s} {'rho_sh':>8s} "
      f"{'grad_mag':>8s} {'1st/3':>6s} {'3rd/3':>6s}")
print("-" * 90)

f76r_rank = None
for rank, r in enumerate(results, 1):
    marker = ' <<<' if r['folio'] == 'f76r' and r['para_idx'] == 0 else ''
    if r['folio'] == 'f76r' and r['para_idx'] == 0:
        f76r_rank = rank
    print(f"  {rank:3d} {r['folio']:>8s} P{r['para_idx']:<2d} {r['n_lines']:5d} {r['n_tokens']:5d} "
          f"{r['rho_mon']:8.3f} {r['rho_ch']:8.3f} {r['rho_sh']:8.3f} "
          f"{r['gradient_mag']:8.3f} {r['first_third']:6.3f} {r['last_third']:6.3f}{marker}")

print(f"\n--- f76r P1 rank: {f76r_rank}/{len(results)} ---")
percentile = 100 * (1 - (f76r_rank - 1) / len(results)) if f76r_rank else 0
print(f"    Percentile: {percentile:.1f}th")

# Distribution summary
rhos = [r['rho_mon'] for r in results]
mean_rho = sum(rhos) / len(rhos)
pos_count = sum(1 for r in rhos if r > 0)
strong_pos = sum(1 for r in rhos if r > 0.5)
print(f"\n--- Distribution of monitoring gradient (Spearman rho) ---")
print(f"    Mean rho: {mean_rho:.3f}")
print(f"    Positive gradients: {pos_count}/{len(results)} ({100*pos_count/len(results):.0f}%)")
print(f"    Strong positive (rho>0.5): {strong_pos}/{len(results)} ({100*strong_pos/len(results):.0f}%)")

# ============================================================
# f76r P1 detailed: ch vs sh decomposition
# ============================================================
print("\n" + "=" * 80)
print("f76r P1: ch vs sh DECOMPOSITION")
print("=" * 80)

f76r_result = [r for r in results if r['folio'] == 'f76r' and r['para_idx'] == 0]
if f76r_result:
    r = f76r_result[0]
    print(f"\n  Monitoring gradient (ch+sh): rho = {r['rho_mon']:.3f}")
    print(f"  Active test (ch) gradient:   rho = {r['rho_ch']:.3f}")
    print(f"  Passive monitor (sh) gradient: rho = {r['rho_sh']:.3f}")

    if r['rho_ch'] > r['rho_sh']:
        print(f"\n  ACTIVE TEST (ch) dominates the gradient")
        print(f"  Consistent with Ch18's silver-plate active testing procedure")
    else:
        print(f"\n  PASSIVE MONITOR (sh) dominates the gradient")
        print(f"  Not specifically consistent with active testing")

# ============================================================
# Control: do high-monitoring folios generically show gradients?
# ============================================================
print("\n" + "=" * 80)
print("CONTROL: HIGH-MONITORING FOLIOS")
print("Do folios with high aggregate monitoring also show gradients?")
print("=" * 80)

# Compute folio-level monitoring rate
folio_mon_rate = {}
for folio in folio_line_tokens:
    all_tokens = []
    for line in folio_line_tokens[folio]:
        all_tokens.extend(folio_line_tokens[folio][line])
    n = len(all_tokens)
    if n == 0:
        continue
    mon = sum(1 for t in all_tokens
              if (morph.extract(t.word).prefix or '') in MONITORING_PREFIXES)
    folio_mon_rate[folio] = mon / n

# Top 10 monitoring folios
top_mon = sorted(folio_mon_rate.items(), key=lambda x: -x[1])[:10]
print(f"\nTop 10 monitoring folios:")
for folio, rate in top_mon:
    # Find their gradient result
    para_results = [r for r in results if r['folio'] == folio]
    if para_results:
        best = max(para_results, key=lambda x: x['rho_mon'])
        print(f"  {folio:8s}: mon_rate={rate:.3f}  best_gradient_rho={best['rho_mon']:.3f} "
              f"(P{best['para_idx']}, {best['n_lines']} lines)")
    else:
        print(f"  {folio:8s}: mon_rate={rate:.3f}  (no paragraph with {MIN_LINES}+ lines)")
