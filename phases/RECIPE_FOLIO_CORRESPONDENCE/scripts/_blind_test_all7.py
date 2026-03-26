"""Blind test: compute structural profiles for 7 matched folios.
Predictions were written BEFORE running this script."""

import sys, math
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()
freq = Counter(t.word for t in tx.currier_b())

MATCHES = [
    ('Ch14', 109, 'f84r', 0.723, 2.097),
    ('Ch27', 154, 'f77v', 0.851, 2.805),
    ('Ch9',  104, 'f83r', 1.560, 1.203),
    ('Ch24', 151, 'f84v', 1.561, 1.261),
    ('Ch16', 111, 'f108r', 1.827, 1.348),
    ('Ch11', 138, 'f112r', 2.484, 1.258),
    ('Ch18t', 145, 'f81v', 2.767, 1.151),
]

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
    d2 = sum((a-b)**2 for a, b in zip(rx, ry))
    return 1.0 - 6.0 * d2 / (n * (n*n - 1))


# ============================================================
# Build data for all folios
# ============================================================
folio_data = {}

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    tokens = [t for t in tx.currier_b() if t.folio == folio and not t.is_label]
    if not tokens:
        print(f"WARNING: no tokens for {folio}")
        continue

    line_tokens = defaultdict(list)
    for t in tokens:
        line_tokens[t.line].append(t)
    lines = sorted(line_tokens.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    # Paragraph detection
    paragraphs = []
    current_lines = []
    for line_num in lines:
        lt = line_tokens[line_num]
        is_start = any(t.par_initial for t in lt)
        if is_start and current_lines:
            paragraphs.append(current_lines)
            current_lines = []
        current_lines.append(line_num)
    if current_lines:
        paragraphs.append(current_lines)

    n_tokens = len(tokens)

    # PREFIX counts
    prefix_counts = Counter()
    for t in tokens:
        m = morph.extract(t.word)
        prefix_counts[m.prefix or '(none)'] += 1

    qo = prefix_counts.get('qo', 0)
    ch_total = sum(prefix_counts.get(p, 0) for p in CH_ACTIVE)
    sh_total = sum(prefix_counts.get(p, 0) for p in SH_PASSIVE)
    ok = prefix_counts.get('ok', 0)
    ot = prefix_counts.get('ot', 0)
    da = prefix_counts.get('da', 0)
    ol = prefix_counts.get('ol', 0)
    k_thermal = sum(prefix_counts.get(p, 0) for p in ['ke', 'ko', 'ka'])

    # Hapax
    hapax_count = sum(1 for t in tokens if freq[t.word] == 1)
    hapax_rate = hapax_count / n_tokens

    # Max consecutive token run
    max_run = 1
    max_run_word = ''
    max_run_line = ''
    for line_num in lines:
        words = [t.word for t in line_tokens[line_num]]
        i = 0
        while i < len(words):
            run_len = 1
            while i + run_len < len(words) and words[i + run_len] == words[i]:
                run_len += 1
            if run_len > max_run:
                max_run = run_len
                max_run_word = words[i]
                max_run_line = line_num
            i += run_len

    # Monitoring gradient for longest paragraph
    longest_para = max(paragraphs, key=len)
    if len(longest_para) >= 5:
        positions = []
        mon_rates = []
        ch_rates = []
        sh_rates = []
        for i, line_num in enumerate(longest_para):
            lt = line_tokens[line_num]
            n = len(lt)
            if n == 0:
                continue
            mon = sum(1 for t in lt if (morph.extract(t.word).prefix or '') in MON_PREFIXES)
            ch_c = sum(1 for t in lt if (morph.extract(t.word).prefix or '') in CH_ACTIVE)
            sh_c = sum(1 for t in lt if (morph.extract(t.word).prefix or '') in SH_PASSIVE)
            positions.append(i)
            mon_rates.append(mon / n)
            ch_rates.append(ch_c / n)
            sh_rates.append(sh_c / n)
        mon_gradient_rho = spearman_rho(positions, mon_rates)
        ch_gradient_rho = spearman_rho(positions, ch_rates)
        sh_gradient_rho = spearman_rho(positions, sh_rates)
    else:
        mon_gradient_rho = 0.0
        ch_gradient_rho = 0.0
        sh_gradient_rho = 0.0

    # Thermal gradient for longest paragraph
    if len(longest_para) >= 5:
        therm_rates = []
        for line_num in longest_para:
            lt = line_tokens[line_num]
            n = len(lt)
            if n == 0:
                continue
            therm = sum(1 for t in lt
                       if (morph.extract(t.word).prefix or '') == 'qo' or
                       (morph.extract(t.word).prefix or '').startswith('k'))
            therm_rates.append(therm / n)
        therm_gradient_rho = spearman_rho(list(range(len(therm_rates))), therm_rates)
    else:
        therm_gradient_rho = 0.0

    # Paragraph size distribution
    para_sizes = [len(p) for p in paragraphs]
    para_tokens = []
    for p in paragraphs:
        n = sum(len(line_tokens[l]) for l in p)
        para_tokens.append(n)
    max_para_frac = max(para_tokens) / n_tokens if n_tokens > 0 else 0

    # Per-paragraph monitoring rate
    para_mon_rates = []
    for p in paragraphs:
        p_tokens = []
        for l in p:
            p_tokens.extend(line_tokens[l])
        n = len(p_tokens)
        if n == 0:
            para_mon_rates.append(0.0)
            continue
        mon = sum(1 for t in p_tokens if (morph.extract(t.word).prefix or '') in MON_PREFIXES)
        para_mon_rates.append(mon / n)

    # Per-paragraph correction rate (ok+ot)
    para_corr_rates = []
    for p in paragraphs:
        p_tokens = []
        for l in p:
            p_tokens.extend(line_tokens[l])
        n = len(p_tokens)
        if n == 0:
            para_corr_rates.append(0.0)
            continue
        corr = sum(1 for t in p_tokens
                   if (morph.extract(t.word).prefix or '') in ['ok', 'ot', 'da'])
        para_corr_rates.append(corr / n)

    # dar count
    dar_count = sum(1 for t in tokens if t.word == 'dar')

    folio_data[folio] = {
        'ch_name': ch_name, 'ch_idx': ch_idx,
        'dist': dist, 'ratio': ratio,
        'n_tokens': n_tokens, 'n_lines': len(lines),
        'n_paras': len(paragraphs), 'para_sizes': para_sizes,
        'para_tokens': para_tokens, 'max_para_frac': max_para_frac,
        'qo_rate': qo / n_tokens, 'ch_rate': ch_total / n_tokens,
        'sh_rate': sh_total / n_tokens, 'ok_rate': ok / n_tokens,
        'ot_rate': ot / n_tokens, 'da_rate': da / n_tokens,
        'ol_rate': ol / n_tokens, 'k_therm_rate': k_thermal / n_tokens,
        'hapax_count': hapax_count, 'hapax_rate': hapax_rate,
        'max_run': max_run, 'max_run_word': max_run_word,
        'mon_gradient_rho': mon_gradient_rho,
        'ch_gradient_rho': ch_gradient_rho,
        'sh_gradient_rho': sh_gradient_rho,
        'therm_gradient_rho': therm_gradient_rho,
        'longest_para_lines': len(longest_para),
        'para_mon_rates': para_mon_rates,
        'para_corr_rates': para_corr_rates,
        'dar_count': dar_count,
    }

# ============================================================
# Print results
# ============================================================
print("=" * 100)
print("BLIND TEST: STRUCTURAL PROFILES FOR 7 MATCHED FOLIOS")
print("=" * 100)

print(f"\n{'Match':>6s} {'Folio':>6s} {'Dist':>6s} {'Ratio':>6s} "
      f"{'Toks':>5s} {'Lines':>5s} {'Paras':>5s} {'MaxP%':>5s} "
      f"{'Hapax':>6s} {'H%':>5s} {'MaxRun':>6s}")
print("-" * 85)

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    d = folio_data[folio]
    print(f"  {ch_name:>5s} {folio:>6s} {dist:6.3f} {ratio:6.3f} "
          f"{d['n_tokens']:5d} {d['n_lines']:5d} {d['n_paras']:5d} {d['max_para_frac']:5.0%} "
          f"{d['hapax_count']:6d} {d['hapax_rate']:5.1%} "
          f"{d['max_run']:3d}x {d['max_run_word']}")

print(f"\n\n{'Match':>6s} {'Folio':>6s} "
      f"{'qo%':>5s} {'ch%':>5s} {'sh%':>5s} {'ok%':>5s} {'ot%':>5s} {'da%':>5s} {'ol%':>5s} {'k%':>5s} "
      f"{'dar':>4s}")
print("-" * 75)

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    d = folio_data[folio]
    print(f"  {ch_name:>5s} {folio:>6s} "
          f"{d['qo_rate']:5.1%} {d['ch_rate']:5.1%} {d['sh_rate']:5.1%} "
          f"{d['ok_rate']:5.1%} {d['ot_rate']:5.1%} {d['da_rate']:5.1%} "
          f"{d['ol_rate']:5.1%} {d['k_therm_rate']:5.1%} "
          f"{d['dar_count']:4d}")

print(f"\n\n{'Match':>6s} {'Folio':>6s} "
      f"{'MonGrad':>8s} {'chGrad':>8s} {'shGrad':>8s} {'ThGrad':>8s} {'LPLines':>7s}")
print("-" * 60)

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    d = folio_data[folio]
    print(f"  {ch_name:>5s} {folio:>6s} "
          f"{d['mon_gradient_rho']:8.3f} {d['ch_gradient_rho']:8.3f} "
          f"{d['sh_gradient_rho']:8.3f} {d['therm_gradient_rho']:8.3f} "
          f"{d['longest_para_lines']:7d}")

# ============================================================
# Paragraph details
# ============================================================
print("\n\n" + "=" * 100)
print("PARAGRAPH STRUCTURE DETAILS")
print("=" * 100)

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    d = folio_data[folio]
    print(f"\n  {ch_name} -> {folio} ({d['n_paras']} paragraphs):")
    for i, (sz, tok, mr, cr) in enumerate(zip(d['para_sizes'], d['para_tokens'],
                                               d['para_mon_rates'], d['para_corr_rates'])):
        pct = tok / d['n_tokens']
        print(f"    P{i+1}: {sz:2d} lines, {tok:3d} tokens ({pct:4.0%})  "
              f"mon={mr:.2f}  corr={cr:.2f}")

# ============================================================
# Prediction scoring
# ============================================================
print("\n\n" + "=" * 100)
print("PREDICTION SCORING")
print("=" * 100)

# Get corpus-wide stats for context
all_folios_hapax = {}
all_folios_mon = {}
for folio_name in set(t.folio for t in tx.currier_b()):
    ftokens = [t for t in tx.currier_b() if t.folio == folio_name and not t.is_label]
    if not ftokens:
        continue
    n = len(ftokens)
    h = sum(1 for t in ftokens if freq[t.word] == 1)
    all_folios_hapax[folio_name] = h / n
    mon = sum(1 for t in ftokens if (morph.extract(t.word).prefix or '') in MON_PREFIXES)
    all_folios_mon[folio_name] = mon / n

hapax_rates = sorted(all_folios_hapax.values())
mon_rates_all = sorted(all_folios_mon.values())
median_hapax = hapax_rates[len(hapax_rates)//2]
median_mon = mon_rates_all[len(mon_rates_all)//2]

print(f"\nCorpus-wide medians: hapax_rate={median_hapax:.3f}, mon_rate={median_mon:.3f}")

for ch_name, ch_idx, folio, dist, ratio in MATCHES:
    d = folio_data[folio]
    hapax_pct = sum(1 for r in hapax_rates if r <= d['hapax_rate']) / len(hapax_rates)
    mon_pct = sum(1 for r in mon_rates_all if r <= (d['ch_rate'] + d['sh_rate'])) / len(mon_rates_all)
    print(f"\n  {ch_name} -> {folio}:")
    print(f"    Hapax rate: {d['hapax_rate']:.3f} ({hapax_pct:.0%} percentile)")
    print(f"    Monitoring rate: {d['ch_rate']+d['sh_rate']:.3f} ({mon_pct:.0%} percentile)")
    print(f"    Mon gradient (longest para): {d['mon_gradient_rho']:.3f}")
    print(f"    Therm gradient (longest para): {d['therm_gradient_rho']:.3f}")
    print(f"    Paragraph asymmetry (max para %): {d['max_para_frac']:.0%}")
