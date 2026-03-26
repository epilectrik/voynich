"""f76r crib decode exploration: Ch18 (element separation, graduated distillation).

Ch18 recipe structure:
  1. Classify fractions (earth+fire = solid, water+air = liquid)
  2. Iterative distillation of water/air (7+ passes), dregs -> earth
  3. Silver-plate purity test (monitoring gate: blackens = impure)
  4. Wash earth with purified water -> aqua vitae / Mercury
  5. Air distillation -> tincture oil, combine with sulfur
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

# All B tokens on f76r
tokens = [t for t in tx.currier_b() if t.folio == 'f76r' and not t.is_label]
freq = Counter(t.word for t in tx.currier_b())

# ============================================================
# 1. Basic folio stats
# ============================================================
lines = sorted(set(t.line for t in tokens), key=lambda x: int(x) if x.isdigit() else 0)
print("=" * 70)
print("f76r BASIC STATS")
print("=" * 70)
print(f"Tokens: {len(tokens)}")
print(f"Lines: {len(lines)} ({lines[0]}-{lines[-1]})")
print(f"Unique types: {len(set(t.word for t in tokens))}")

# ============================================================
# 2. Paragraph detection (gallows-delimited)
# ============================================================
print("\n" + "=" * 70)
print("f76r PARAGRAPH STRUCTURE")
print("=" * 70)

# Group tokens by line
line_tokens = defaultdict(list)
for t in tokens:
    line_tokens[t.line].append(t)

# Detect paragraph boundaries via par_initial
para_starts = []
for t in tokens:
    if t.par_initial:
        para_starts.append((t.line, t.word))

print(f"\nParagraph starts (par_initial=True): {len(para_starts)}")
for line, word in para_starts:
    print(f"  Line {line}: starts with '{word}'")

# Build paragraph groups
paragraphs = []
current_para_lines = []
current_para_start = None

for line_num in lines:
    lt = line_tokens[line_num]
    is_start = any(t.par_initial for t in lt)
    if is_start and current_para_lines:
        paragraphs.append((current_para_start, current_para_lines))
        current_para_lines = []
    if is_start:
        current_para_start = line_num
    current_para_lines.append(line_num)

if current_para_lines:
    paragraphs.append((current_para_start, current_para_lines))

print(f"\nParagraphs: {len(paragraphs)}")
for i, (start, plines) in enumerate(paragraphs, 1):
    n_tokens = sum(len(line_tokens[l]) for l in plines)
    print(f"  P{i}: lines {plines[0]}-{plines[-1]} ({len(plines)} lines, {n_tokens} tokens)")

# ============================================================
# 3. Full token dump with morphology
# ============================================================
print("\n" + "=" * 70)
print("f76r FULL TOKEN DUMP (with morphology)")
print("=" * 70)

para_idx = 0
for line_num in lines:
    lt = line_tokens[line_num]

    # Check if this is a paragraph start
    is_para_start = any(t.par_initial for t in lt)
    if is_para_start:
        para_idx += 1
        print(f"\n--- PARAGRAPH {para_idx} ---")

    print(f"\n  Line {line_num}:")
    for t in lt:
        m = morph.extract(t.word)
        flag = ''
        if freq[t.word] == 1:
            flag = ' *** HAPAX'
        elif freq[t.word] <= 3:
            flag = ' * RARE'

        art_str = m.articulator or '-'
        pre_str = m.prefix or '-'
        mid_str = m.middle or '?'
        suf_str = m.suffix or '-'

        pos_flags = []
        if t.line_initial:
            pos_flags.append('LI')
        if t.line_final:
            pos_flags.append('LF')
        if t.par_initial:
            pos_flags.append('PI')
        if t.par_final:
            pos_flags.append('PF')
        pos_str = ','.join(pos_flags) if pos_flags else ''

        print(f"    {t.word:20s} art={art_str:3s} pre={pre_str:6s} "
              f"mid={mid_str:10s} suf={suf_str:6s} "
              f"freq={freq[t.word]:5d} {pos_str:6s}{flag}")

# ============================================================
# 4. Hapax legomena on f76r
# ============================================================
print("\n" + "=" * 70)
print("f76r HAPAX LEGOMENA (unique to this folio)")
print("=" * 70)

hapax = []
for t in tokens:
    if freq[t.word] == 1 and t.word not in [h[0] for h in hapax]:
        m = morph.extract(t.word)
        hapax.append((t.word, t.line, m))

print(f"\nTotal hapax: {len(hapax)}")
for word, line, m in hapax:
    parseable = bool(m.prefix)
    print(f"  L{line:>3s} {word:20s} pre={m.prefix or '-':6s} "
          f"mid={m.middle or '?':10s} suf={m.suffix or '-':6s} "
          f"parseable={parseable}")

# ============================================================
# 5. Prefix distribution
# ============================================================
print("\n" + "=" * 70)
print("f76r PREFIX DISTRIBUTION")
print("=" * 70)

prefix_counts = Counter()
for t in tokens:
    m = morph.extract(t.word)
    prefix_counts[m.prefix or '(none)'] += 1

for pre, cnt in prefix_counts.most_common(20):
    pct = 100 * cnt / len(tokens)
    print(f"  {pre:10s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 6. MIDDLE distribution
# ============================================================
print("\n" + "=" * 70)
print("f76r MIDDLE DISTRIBUTION")
print("=" * 70)

middle_counts = Counter()
for t in tokens:
    m = morph.extract(t.word)
    middle_counts[m.middle or '?'] += 1

for mid, cnt in middle_counts.most_common(20):
    pct = 100 * cnt / len(tokens)
    print(f"  {mid:12s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 7. Suffix distribution
# ============================================================
print("\n" + "=" * 70)
print("f76r SUFFIX DISTRIBUTION")
print("=" * 70)

suffix_counts = Counter()
for t in tokens:
    m = morph.extract(t.word)
    suffix_counts[m.suffix or '(none)'] += 1

for suf, cnt in suffix_counts.most_common(20):
    pct = 100 * cnt / len(tokens)
    print(f"  {suf:10s}: {cnt:4d} ({pct:5.1f}%)")

# ============================================================
# 8. Consecutive token repetition
# ============================================================
print("\n" + "=" * 70)
print("f76r CONSECUTIVE TOKEN RUNS")
print("=" * 70)

for line_num in lines:
    words = [t.word for t in line_tokens[line_num]]
    i = 0
    while i < len(words):
        run_len = 1
        while i + run_len < len(words) and words[i + run_len] == words[i]:
            run_len += 1
        if run_len >= 2:
            print(f"  L{line_num}: '{words[i]}' x{run_len}")
        i += run_len

# ============================================================
# 9. dar tokens on f76r
# ============================================================
print("\n" + "=" * 70)
print("f76r 'dar' TOKENS")
print("=" * 70)

for line_num in lines:
    words = [t.word for t in line_tokens[line_num]]
    for i, w in enumerate(words):
        if w == 'dar':
            start = max(0, i - 3)
            end = min(len(words), i + 4)
            context = words[start:end]
            marker_pos = i - start
            ctx_str = ' '.join(
                f'[{w}]' if j == marker_pos else w
                for j, w in enumerate(context)
            )
            print(f"  L{line_num} pos={i}: ...{ctx_str}...")

# ============================================================
# 10. Paragraph-level operational profile
# ============================================================
print("\n" + "=" * 70)
print("f76r PARAGRAPH OPERATIONAL PROFILES")
print("=" * 70)

# For each paragraph, show: prefix distribution, dominant MIDDLEs,
# suffix pattern, heat indicators (k-prefix rate), monitoring (h-prefix)

for i, (start, plines) in enumerate(paragraphs, 1):
    para_tokens = []
    for l in plines:
        para_tokens.extend(line_tokens[l])

    n = len(para_tokens)

    # Prefix categories
    k_count = 0  # thermal (k-prefix, ke-, ko-)
    h_count = 0  # monitoring (ch-, sh-)
    e_count = 0  # correction (da-, ok-, ot-)
    link_count = 0  # LINK (ol-)
    qo_count = 0  # qo-prefix

    for t in para_tokens:
        m = morph.extract(t.word)
        p = m.prefix or ''
        if p.startswith('k') or p in ['ke', 'ko', 'ka']:
            k_count += 1
        if p in ['ch', 'sh', 'pch', 'tch', 'kch', 'fch', 'sch']:
            h_count += 1
        if p in ['da', 'ok', 'ot', 'ol']:
            if p == 'ol':
                link_count += 1
            else:
                e_count += 1
        if p == 'qo':
            qo_count += 1

    # Suffix pattern
    dy_count = sum(1 for t in para_tokens if morph.extract(t.word).suffix == 'dy')
    y_count = sum(1 for t in para_tokens if morph.extract(t.word).suffix == 'y')
    ain_count = sum(1 for t in para_tokens
                    if (morph.extract(t.word).suffix or '').startswith('ain'))

    # Gallows (T-gallows as paragraph delimiters)
    gallows = sum(1 for t in para_tokens if t.word and t.word[0] in 'ptkf'
                  and len(t.word) > 2)

    print(f"\n  P{i} (L{start}-L{plines[-1]}, {len(plines)} lines, {n} tokens):")
    print(f"    Prefixes: qo={qo_count} ch/sh={h_count} da/ok/ot={e_count} "
          f"ol={link_count} k-thermal={k_count}")
    print(f"    Suffixes: -dy={dy_count} -y={y_count} -ain={ain_count}")
    print(f"    Gallows-initial: {gallows}")
    print(f"    k/(k+h): {k_count/(k_count+h_count):.2f}" if k_count+h_count > 0 else "    k/(k+h): N/A")

    # Show first and last few tokens
    first_3 = ' '.join(t.word for t in para_tokens[:4])
    last_3 = ' '.join(t.word for t in para_tokens[-4:])
    print(f"    Opens: {first_3}")
    print(f"    Closes: {last_3}")

# ============================================================
# 11. Comparison: f76r vs f75r operational signatures
# ============================================================
print("\n" + "=" * 70)
print("f76r vs f75r COMPARISON")
print("=" * 70)

f75r_tokens = [t for t in tx.currier_b() if t.folio == 'f75r' and not t.is_label]

for folio_name, ftokens in [('f75r', f75r_tokens), ('f76r', tokens)]:
    n = len(ftokens)

    k_count = sum(1 for t in ftokens
                  if (morph.extract(t.word).prefix or '').startswith('k'))
    qo_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix == 'qo')
    ch_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix in ['ch', 'pch', 'tch', 'kch', 'fch'])
    sh_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix in ['sh'])
    ol_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix == 'ol')
    da_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix == 'da')
    ok_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix == 'ok')
    ot_count = sum(1 for t in ftokens
                   if morph.extract(t.word).prefix == 'ot')

    dy_count = sum(1 for t in ftokens if morph.extract(t.word).suffix == 'dy')
    y_count = sum(1 for t in ftokens if morph.extract(t.word).suffix == 'y')

    hapax_count = sum(1 for t in ftokens if freq[t.word] == 1)

    print(f"\n  {folio_name} ({n} tokens):")
    print(f"    qo: {qo_count:3d} ({100*qo_count/n:.1f}%)  "
          f"ch: {ch_count:3d} ({100*ch_count/n:.1f}%)  "
          f"sh: {sh_count:3d} ({100*sh_count/n:.1f}%)")
    print(f"    k:  {k_count:3d} ({100*k_count/n:.1f}%)  "
          f"ol: {ol_count:3d} ({100*ol_count/n:.1f}%)  "
          f"da: {da_count:3d} ({100*da_count/n:.1f}%)")
    print(f"    ok: {ok_count:3d} ({100*ok_count/n:.1f}%)  "
          f"ot: {ot_count:3d} ({100*ot_count/n:.1f}%)")
    print(f"    -dy: {dy_count:3d} ({100*dy_count/n:.1f}%)  "
          f"-y:  {y_count:3d} ({100*y_count/n:.1f}%)")
    print(f"    Hapax: {hapax_count}")
