"""f76r crib decode v2: deeper analysis of paragraph-level patterns.

Ch18 recipe phases:
  Phase 1: Classify fractions (earth+fire solid, water+air liquid)
  Phase 2: Iterative distillation 7+ passes, dregs -> earth
  Phase 3: Silver-plate purity test (monitoring gate)
  Phase 4: Wash earth with purified water -> aqua vitae / Mercury
  Phase 5: Air distillation -> tincture, combine with sulfur

f76r structure:
  P1: L1-L29 (29 lines, 357 tokens) -- DOMINANT paragraph
  P2: L30-L34 (5 lines, 58 tokens)
  P3: L35-L41 (7 lines, 74 tokens)
  P4: L42-L47 (6 lines, 57 tokens)

Questions:
  1. Does P1 contain the iterative distillation loop (7+ passes)?
  2. Is there a monitoring-dense region matching the silver-plate test?
  3. Do P2-P4 correspond to post-test operations?
  4. What are the operational transitions within P1?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

tokens = [t for t in tx.currier_b() if t.folio == 'f76r' and not t.is_label]
freq = Counter(t.word for t in tx.currier_b())

line_tokens = defaultdict(list)
for t in tokens:
    line_tokens[t.line].append(t)

lines = sorted(line_tokens.keys(), key=lambda x: int(x) if x.isdigit() else 0)

# ============================================================
# 1. Per-line operational fingerprint
# ============================================================
print("=" * 80)
print("f76r PER-LINE OPERATIONAL FINGERPRINT")
print("=" * 80)
print(f"{'Line':>4s} {'Tok':>3s} {'qo':>3s} {'ch':>3s} {'sh':>3s} "
      f"{'ok':>3s} {'ot':>3s} {'da':>3s} {'ol':>3s} {'k-':>3s} "
      f"{'sa':>3s} {'-dy':>3s} {'hpx':>3s}  dominant_prefixes  unique_tokens")
print("-" * 110)

para_num = 0
for line_num in lines:
    lt = line_tokens[line_num]
    is_para = any(t.par_initial for t in lt)
    if is_para:
        para_num += 1
        print(f"  --- P{para_num} ---")

    n = len(lt)
    counts = Counter()
    for t in lt:
        m = morph.extract(t.word)
        p = m.prefix or '(none)'
        counts[p] += 1

    qo = counts.get('qo', 0)
    ch_total = sum(counts.get(p, 0) for p in ['ch', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch'])
    sh_total = sum(counts.get(p, 0) for p in ['sh', 'lsh'])
    ok = counts.get('ok', 0)
    ot = counts.get('ot', 0)
    da = counts.get('da', 0)
    ol = counts.get('ol', 0)
    k_thermal = sum(counts.get(p, 0) for p in ['ke', 'ko', 'ka'])
    sa = counts.get('sa', 0)

    dy_count = sum(1 for t in lt if (morph.extract(t.word).suffix or '') == 'dy')
    hapax_count = sum(1 for t in lt if freq[t.word] == 1)

    # Dominant prefix (top 2)
    top_pre = counts.most_common(3)
    dom_str = ', '.join(f'{p}={c}' for p, c in top_pre)

    # Unique tokens
    uniq = [t.word for t in lt if freq[t.word] == 1]
    uniq_str = ' '.join(uniq[:3])
    if len(uniq) > 3:
        uniq_str += '...'

    print(f"  {line_num:>3s} {n:3d} {qo:3d} {ch_total:3d} {sh_total:3d} "
          f"{ok:3d} {ot:3d} {da:3d} {ol:3d} {k_thermal:3d} "
          f"{sa:3d} {dy_count:3d} {hapax_count:3d}  {dom_str:30s} {uniq_str}")

# ============================================================
# 2. Monitoring concentration analysis
# ============================================================
print("\n" + "=" * 80)
print("MONITORING CONCENTRATION (ch+sh rate per line)")
print("=" * 80)

print(f"\n{'Line':>4s} {'ch+sh':>5s} {'total':>5s} {'rate':>6s}  visual")
print("-" * 50)

para_num = 0
for line_num in lines:
    lt = line_tokens[line_num]
    is_para = any(t.par_initial for t in lt)
    if is_para:
        para_num += 1
        print(f"  --- P{para_num} ---")

    n = len(lt)
    mon = 0
    for t in lt:
        m = morph.extract(t.word)
        p = m.prefix or ''
        if p in ['ch', 'sh', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch', 'lsh']:
            mon += 1

    rate = mon / n if n > 0 else 0
    bar = '#' * int(rate * 40)
    print(f"  {line_num:>3s} {mon:5d} {n:5d} {rate:6.2f}  {bar}")

# ============================================================
# 3. Heat/thermal concentration (k-prefix + qo-prefix)
# ============================================================
print("\n" + "=" * 80)
print("THERMAL CONCENTRATION (qo + k-prefix rate per line)")
print("=" * 80)

print(f"\n{'Line':>4s} {'qo+k':>5s} {'total':>5s} {'rate':>6s}  visual")
print("-" * 50)

para_num = 0
for line_num in lines:
    lt = line_tokens[line_num]
    is_para = any(t.par_initial for t in lt)
    if is_para:
        para_num += 1
        print(f"  --- P{para_num} ---")

    n = len(lt)
    therm = 0
    for t in lt:
        m = morph.extract(t.word)
        p = m.prefix or ''
        if p == 'qo' or p.startswith('k'):
            therm += 1

    rate = therm / n if n > 0 else 0
    bar = '#' * int(rate * 40)
    print(f"  {line_num:>3s} {therm:5d} {n:5d} {rate:6.2f}  {bar}")

# ============================================================
# 4. Correction concentration (da + ok + ot rate per line)
# ============================================================
print("\n" + "=" * 80)
print("CORRECTION CONCENTRATION (da+ok+ot rate per line)")
print("=" * 80)

print(f"\n{'Line':>4s} {'corr':>5s} {'total':>5s} {'rate':>6s}  visual")
print("-" * 50)

para_num = 0
for line_num in lines:
    lt = line_tokens[line_num]
    is_para = any(t.par_initial for t in lt)
    if is_para:
        para_num += 1
        print(f"  --- P{para_num} ---")

    n = len(lt)
    corr = 0
    for t in lt:
        m = morph.extract(t.word)
        p = m.prefix or ''
        if p in ['da', 'ok', 'ot']:
            corr += 1

    rate = corr / n if n > 0 else 0
    bar = '#' * int(rate * 40)
    print(f"  {line_num:>3s} {corr:5d} {n:5d} {rate:6.2f}  {bar}")

# ============================================================
# 5. LINK (ol-prefix) concentration
# ============================================================
print("\n" + "=" * 80)
print("LINK CONCENTRATION (ol-prefix rate per line)")
print("=" * 80)

print(f"\n{'Line':>4s} {'ol':>5s} {'total':>5s} {'rate':>6s}  visual")
print("-" * 50)

para_num = 0
for line_num in lines:
    lt = line_tokens[line_num]
    is_para = any(t.par_initial for t in lt)
    if is_para:
        para_num += 1
        print(f"  --- P{para_num} ---")

    n = len(lt)
    link = 0
    for t in lt:
        m = morph.extract(t.word)
        p = m.prefix or ''
        if p == 'ol':
            link += 1

    rate = link / n if n > 0 else 0
    bar = '#' * int(rate * 40)
    print(f"  {line_num:>3s} {link:5d} {n:5d} {rate:6.2f}  {bar}")

# ============================================================
# 6. P1 internal structure: is there a section break?
# ============================================================
print("\n" + "=" * 80)
print("P1 INTERNAL STRUCTURE (lines 1-29)")
print("Looking for operational transitions within the big paragraph")
print("=" * 80)

# Compute a rolling 3-line window of monitoring vs thermal dominance
for start_line in range(1, 28):
    window_lines = [str(l) for l in range(start_line, min(start_line+3, 30))]
    window_tokens = []
    for wl in window_lines:
        if wl in line_tokens:
            window_tokens.extend(line_tokens[wl])

    if not window_tokens:
        continue

    n = len(window_tokens)
    mon = sum(1 for t in window_tokens
              if (morph.extract(t.word).prefix or '') in
              ['ch', 'sh', 'pch', 'tch', 'kch', 'fch', 'sch', 'rch', 'dch', 'lch', 'lsh'])
    therm = sum(1 for t in window_tokens
                if (morph.extract(t.word).prefix or '') in ['qo'] or
                (morph.extract(t.word).prefix or '').startswith('k'))
    corr = sum(1 for t in window_tokens
               if (morph.extract(t.word).prefix or '') in ['da', 'ok', 'ot'])

    mon_r = mon / n
    therm_r = therm / n
    corr_r = corr / n

    dom = 'MON' if mon_r > therm_r and mon_r > corr_r else (
          'THERM' if therm_r > mon_r and therm_r > corr_r else 'CORR')

    m_bar = 'M' * int(mon_r * 20)
    t_bar = 'T' * int(therm_r * 20)
    c_bar = 'C' * int(corr_r * 20)

    print(f"  L{start_line:>2d}-{min(start_line+2,29):>2d}: "
          f"mon={mon_r:.2f} therm={therm_r:.2f} corr={corr_r:.2f}  "
          f"{dom:5s}  {m_bar}{t_bar}{c_bar}")

# ============================================================
# 7. Token repetition patterns on f76r
# ============================================================
print("\n" + "=" * 80)
print("NOTABLE TOKEN PATTERNS")
print("=" * 80)

# shedy frequency per line (the dominant monitoring token)
print("\n'shedy' distribution across lines:")
for line_num in lines:
    lt = line_tokens[line_num]
    shedy_count = sum(1 for t in lt if t.word == 'shedy')
    if shedy_count >= 2:
        print(f"  L{line_num}: shedy x{shedy_count}")

# qokedy frequency per line (the dominant thermal token)
print("\n'qokedy' distribution:")
for line_num in lines:
    lt = line_tokens[line_num]
    qokedy_count = sum(1 for t in lt if t.word == 'qokedy')
    if qokedy_count >= 2:
        print(f"  L{line_num}: qokedy x{qokedy_count}")

# qokeey frequency (another common thermal token)
print("\n'qokeey' distribution:")
for line_num in lines:
    lt = line_tokens[line_num]
    count = sum(1 for t in lt if t.word == 'qokeey')
    if count >= 2:
        print(f"  L{line_num}: qokeey x{count}")
