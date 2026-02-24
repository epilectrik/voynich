#!/usr/bin/env python3
"""
Phase 442: PARAGRAPH_TERMINATION_MECHANICS

Investigate what controls paragraph length and what triggers -am termination.

Gap 1: Distribution shape (geometric/memoryless?)
Gap 2: Section & REGIME effects on body length
Gap 3: -am trigger context
Gap 4: Short vs long paragraph structure
Gap 5: Header complexity -> body length

Output: phases/PARAGRAPH_TERMINATION_MECHANICS/results/termination_analysis.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'PARAGRAPH_TERMINATION_MECHANICS' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

TERMINAL_SUFFIXES = {'dy', 'edy', 'eey', 'ey', 'hy', 'ry', 'ly', 'am', 'om'}

# ============================================================
# DECODE ALL FOLIOS — collect paragraphs with metadata
# ============================================================
print("Decoding all B folios...")
b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Get section and REGIME for each folio
folio_section = {}
folio_regime = {}
for t in tx.currier_b():
    if t.folio not in folio_section:
        folio_section[t.folio] = t.section

for folio in b_folios:
    try:
        fa = decoder.analyze_folio(folio)
        if fa and fa.regime:
            folio_regime[folio] = fa.regime
    except:
        pass

all_paragraphs = []  # (folio, section, regime, BParagraphAnalysis)
for folio in b_folios:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
        section = folio_section.get(folio, '?')
        regime = folio_regime.get(folio, '?')
        for p in paras:
            all_paragraphs.append((folio, section, regime, p))
    except:
        continue

print(f"  {len(all_paragraphs)} paragraphs from {len(b_folios)} folios")

# ============================================================
# GAP 1: DISTRIBUTION SHAPE
# ============================================================
print("\n" + "="*70)
print("GAP 1: BODY LINE COUNT DISTRIBUTION")
print("="*70)

body_lengths = []
for folio, section, regime, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if len(body_lines) >= 1:
        body_lengths.append(len(body_lines))

n = len(body_lengths)
mean_len = sum(body_lengths) / n
var_len = sum((x - mean_len)**2 for x in body_lengths) / n
std_len = var_len ** 0.5

print(f"\n  Paragraphs with body lines: {n}")
print(f"  Mean body length: {mean_len:.2f}")
print(f"  Std: {std_len:.2f}")
print(f"  Variance/mean ratio: {var_len/mean_len:.2f} (geometric=1.0 would give ~1/p)")
print(f"  Min: {min(body_lengths)}, Max: {max(body_lengths)}")

# Distribution histogram
length_counts = Counter(body_lengths)
print(f"\n  Body length distribution:")
print(f"  {'Length':>6s} {'Count':>6s} {'Pct':>7s} {'CumPct':>7s}")
cum = 0
for length in sorted(length_counts.keys()):
    ct = length_counts[length]
    pct = ct / n * 100
    cum += pct
    bar = '#' * int(pct)
    print(f"  {length:6d} {ct:6d} {pct:6.1f}% {cum:6.1f}% {bar}")
    if length > 20:
        remaining = sum(length_counts[k] for k in length_counts if k > length)
        print(f"  ...{remaining} paragraphs with length > {length}")
        break

# Geometric fit test
# Geometric distribution: P(X=k) = (1-p)^(k-1) * p, where p = 1/mean
# For body lines, k starts at 1
p_geom = 1.0 / mean_len
print(f"\n  Geometric fit: p = {p_geom:.4f} (1/mean)")

# Chi-squared goodness of fit
print(f"\n  Chi-squared goodness of fit (geometric):")
chi2_geom = 0
bins_used = 0
expected_counts = []
observed_counts = []
for k in range(1, 21):
    expected = n * (1 - p_geom) ** (k - 1) * p_geom
    observed = length_counts.get(k, 0)
    if expected >= 5:  # Chi-squared requires expected >= 5
        chi2_geom += (observed - expected) ** 2 / expected
        bins_used += 1
        expected_counts.append(expected)
        observed_counts.append(observed)
        print(f"    k={k:2d}: obs={observed:4d} exp={expected:6.1f} (O-E)^2/E={((observed-expected)**2/expected):6.2f}")

# Overflow bin
exp_overflow = n * (1 - p_geom) ** 20
obs_overflow = sum(length_counts.get(k, 0) for k in length_counts if k > 20)
if exp_overflow >= 5:
    chi2_geom += (obs_overflow - exp_overflow) ** 2 / exp_overflow
    bins_used += 1
    print(f"    k>20: obs={obs_overflow:4d} exp={exp_overflow:6.1f}")

df_geom = bins_used - 2  # -1 for total, -1 for estimated p
print(f"\n  Chi-squared = {chi2_geom:.2f}, df = {df_geom}")

# Approximate p-value using chi-squared CDF (simplified)
# For large df, chi2 ~ normal(df, sqrt(2*df))
if df_geom > 0:
    z = (chi2_geom - df_geom) / (2 * df_geom) ** 0.5
    # Very rough: |z| > 2 means p < 0.05
    if z > 3:
        print(f"  z-score = {z:.2f} -> GEOMETRIC REJECTED (p << 0.05)")
    elif z > 2:
        print(f"  z-score = {z:.2f} -> GEOMETRIC REJECTED (p < 0.05)")
    elif z > 1.5:
        print(f"  z-score = {z:.2f} -> GEOMETRIC MARGINAL")
    else:
        print(f"  z-score = {z:.2f} -> GEOMETRIC NOT REJECTED")

# Variance test: geometric has variance = (1-p)/p^2
# If var >> geometric variance, it's overdispersed
geom_var = (1 - p_geom) / (p_geom ** 2)
dispersion = var_len / geom_var
print(f"\n  Geometric expected variance: {geom_var:.2f}")
print(f"  Observed variance: {var_len:.2f}")
print(f"  Dispersion ratio: {dispersion:.2f} (1.0 = geometric, >1 = overdispersed)")

# Stratify by section
print(f"\n  Body length by section:")
section_lengths = defaultdict(list)
for folio, section, regime, para in all_paragraphs:
    body = [l for l in para.lines if not l.is_header]
    if body:
        section_lengths[section].append(len(body))

print(f"  {'Section':>8s} {'N':>5s} {'Mean':>6s} {'Std':>6s} {'Var/Mean':>8s}")
for sec in sorted(section_lengths.keys()):
    vals = section_lengths[sec]
    sec_n = len(vals)
    sec_mean = sum(vals) / sec_n
    sec_var = sum((x - sec_mean)**2 for x in vals) / sec_n
    sec_std = sec_var ** 0.5
    vm = sec_var / sec_mean if sec_mean > 0 else 0
    print(f"  {sec:>8s} {sec_n:5d} {sec_mean:6.2f} {sec_std:6.2f} {vm:8.2f}")

# ============================================================
# GAP 2: SECTION & REGIME EFFECTS
# ============================================================
print("\n" + "="*70)
print("GAP 2: SECTION & REGIME EFFECTS ON BODY LENGTH")
print("="*70)

# ANOVA-like: between-group vs within-group variance
# Section effect
grand_mean = mean_len
ss_between_sec = 0
ss_within_sec = 0
for sec, vals in section_lengths.items():
    sec_mean = sum(vals) / len(vals)
    ss_between_sec += len(vals) * (sec_mean - grand_mean) ** 2
    ss_within_sec += sum((x - sec_mean) ** 2 for x in vals)

k_sec = len(section_lengths)
n_total = sum(len(v) for v in section_lengths.values())
if k_sec > 1 and n_total > k_sec:
    ms_between = ss_between_sec / (k_sec - 1)
    ms_within = ss_within_sec / (n_total - k_sec)
    f_sec = ms_between / ms_within if ms_within > 0 else 0
    eta2_sec = ss_between_sec / (ss_between_sec + ss_within_sec)
    print(f"\n  Section ANOVA: F = {f_sec:.2f}, eta-squared = {eta2_sec:.3f}")
    print(f"  Section explains {eta2_sec*100:.1f}% of body length variance")

# REGIME effect
regime_lengths = defaultdict(list)
for folio, section, regime, para in all_paragraphs:
    if regime != '?':
        body = [l for l in para.lines if not l.is_header]
        if body:
            regime_lengths[regime].append(len(body))

print(f"\n  Body length by REGIME:")
print(f"  {'REGIME':>10s} {'N':>5s} {'Mean':>6s} {'Std':>6s}")
for reg in sorted(regime_lengths.keys()):
    vals = regime_lengths[reg]
    r_mean = sum(vals) / len(vals)
    r_var = sum((x - r_mean)**2 for x in vals) / len(vals)
    print(f"  {reg:>10s} {len(vals):5d} {r_mean:6.2f} {r_var**0.5:6.2f}")

ss_between_reg = 0
ss_within_reg = 0
for reg, vals in regime_lengths.items():
    r_mean = sum(vals) / len(vals)
    ss_between_reg += len(vals) * (r_mean - grand_mean) ** 2
    ss_within_reg += sum((x - r_mean) ** 2 for x in vals)

k_reg = len(regime_lengths)
n_reg = sum(len(v) for v in regime_lengths.values())
if k_reg > 1 and n_reg > k_reg:
    ms_between_r = ss_between_reg / (k_reg - 1)
    ms_within_r = ss_within_reg / (n_reg - k_reg)
    f_reg = ms_between_r / ms_within_r if ms_within_r > 0 else 0
    eta2_reg = ss_between_reg / (ss_between_reg + ss_within_reg)
    print(f"\n  REGIME ANOVA: F = {f_reg:.2f}, eta-squared = {eta2_reg:.3f}")
    print(f"  REGIME explains {eta2_reg*100:.1f}% of body length variance")

# Folio-level variation within section
print(f"\n  Within-section folio variation:")
for sec in sorted(section_lengths.keys()):
    folio_means = defaultdict(list)
    for folio, section, regime, para in all_paragraphs:
        if section != sec:
            continue
        body = [l for l in para.lines if not l.is_header]
        if body:
            folio_means[folio].append(len(body))
    folio_avgs = [sum(v)/len(v) for v in folio_means.values() if len(v) >= 2]
    if len(folio_avgs) >= 3:
        fm_mean = sum(folio_avgs) / len(folio_avgs)
        fm_std = (sum((x - fm_mean)**2 for x in folio_avgs) / len(folio_avgs)) ** 0.5
        cv = fm_std / fm_mean if fm_mean > 0 else 0
        print(f"    {sec}: {len(folio_avgs)} folios, mean-of-means={fm_mean:.1f}, CV={cv:.2f}")

# ============================================================
# GAP 3: -am TRIGGER CONTEXT
# ============================================================
print("\n" + "="*70)
print("GAP 3: -am TRIGGER CONTEXT")
print("="*70)

# Find all paragraph-final -am tokens and their context
para_final_am_contexts = []  # (preceding_words, am_word, folio)
nonpara_final_am_contexts = []  # -am at line-final but NOT paragraph-final

for folio, section, regime, para in all_paragraphs:
    body_lines = [l for l in para.lines if not l.is_header]
    if not body_lines:
        continue

    for li, line_a in enumerate(body_lines):
        if not line_a.tokens:
            continue
        final_tok = line_a.tokens[-1]
        m = final_tok.morph
        is_am = m.suffix == 'am'
        is_last_line = (li == len(body_lines) - 1)

        if is_am:
            # Collect preceding tokens (up to 5)
            preceding = [t.word for t in line_a.tokens[max(0, len(line_a.tokens)-6):-1]]
            if is_last_line:
                para_final_am_contexts.append({
                    'word': final_tok.word,
                    'preceding': preceding,
                    'folio': folio,
                    'section': section,
                    'prefix': m.prefix or '',
                    'middle': m.middle or '',
                    'line_length': line_a.token_count,
                    'body_position': li / max(len(body_lines) - 1, 1),
                })
            else:
                nonpara_final_am_contexts.append({
                    'word': final_tok.word,
                    'preceding': preceding,
                    'prefix': m.prefix or '',
                    'middle': m.middle or '',
                    'line_length': line_a.token_count,
                    'body_position': li / max(len(body_lines) - 1, 1),
                })

print(f"\n  Paragraph-final -am tokens: {len(para_final_am_contexts)}")
print(f"  Non-para-final -am tokens: {len(nonpara_final_am_contexts)}")

# Words
pf_am_words = Counter(c['word'] for c in para_final_am_contexts)
npf_am_words = Counter(c['word'] for c in nonpara_final_am_contexts)
print(f"\n  Paragraph-final -am words:")
for word, ct in pf_am_words.most_common(10):
    npf_ct = npf_am_words.get(word, 0)
    print(f"    {word:>12s}: {ct:4d} para-final, {npf_ct:4d} non-final")

# PREFIX patterns
pf_am_prefixes = Counter(c['prefix'] for c in para_final_am_contexts)
npf_am_prefixes = Counter(c['prefix'] for c in nonpara_final_am_contexts)
pf_total = len(para_final_am_contexts) or 1
npf_total = len(nonpara_final_am_contexts) or 1

print(f"\n  PREFIX distribution of -am tokens:")
print(f"  {'PREFIX':>8s} {'ParaF%':>8s} {'NonF%':>8s} {'Enrich':>8s}")
all_prefixes = set(pf_am_prefixes.keys()) | set(npf_am_prefixes.keys())
for prefix in sorted(all_prefixes, key=lambda p: pf_am_prefixes.get(p, 0) + npf_am_prefixes.get(p, 0), reverse=True)[:10]:
    pf_pct = pf_am_prefixes.get(prefix, 0) / pf_total * 100
    npf_pct = npf_am_prefixes.get(prefix, 0) / npf_total * 100
    enr = pf_pct / npf_pct if npf_pct > 0 else 99.9
    pfx_label = prefix if prefix else 'NONE'
    print(f"  {pfx_label:>8s} {pf_pct:7.1f}% {npf_pct:7.1f}% {enr:7.2f}x")

# MIDDLE patterns
pf_am_middles = Counter(c['middle'] for c in para_final_am_contexts)
npf_am_middles = Counter(c['middle'] for c in nonpara_final_am_contexts)
print(f"\n  MIDDLE distribution of -am tokens:")
print(f"  {'MIDDLE':>8s} {'ParaF%':>8s} {'NonF%':>8s} {'Enrich':>8s}")
all_middles = set(pf_am_middles.keys()) | set(npf_am_middles.keys())
for mid in sorted(all_middles, key=lambda m: pf_am_middles.get(m, 0) + npf_am_middles.get(m, 0), reverse=True)[:10]:
    pf_pct = pf_am_middles.get(mid, 0) / pf_total * 100
    npf_pct = npf_am_middles.get(mid, 0) / npf_total * 100
    enr = pf_pct / npf_pct if npf_pct > 0 else 99.9
    print(f"  {mid:>8s} {pf_pct:7.1f}% {npf_pct:7.1f}% {enr:7.2f}x")

# Body position of -am
pf_pos = [c['body_position'] for c in para_final_am_contexts]
npf_pos = [c['body_position'] for c in nonpara_final_am_contexts]
print(f"\n  Mean body position of -am:")
print(f"    Paragraph-final: {sum(pf_pos)/len(pf_pos):.3f}" if pf_pos else "    (none)")
print(f"    Non-para-final:  {sum(npf_pos)/len(npf_pos):.3f}" if npf_pos else "    (none)")

# Line length containing -am
pf_linelen = [c['line_length'] for c in para_final_am_contexts]
npf_linelen = [c['line_length'] for c in nonpara_final_am_contexts]
print(f"\n  Mean line length containing -am:")
print(f"    Paragraph-final: {sum(pf_linelen)/len(pf_linelen):.1f}" if pf_linelen else "    (none)")
print(f"    Non-para-final:  {sum(npf_linelen)/len(npf_linelen):.1f}" if npf_linelen else "    (none)")

# Preceding token patterns (2-grams before -am)
pf_bigrams = Counter()
npf_bigrams = Counter()
for ctx in para_final_am_contexts:
    if len(ctx['preceding']) >= 1:
        pf_bigrams[ctx['preceding'][-1]] += 1
for ctx in nonpara_final_am_contexts:
    if len(ctx['preceding']) >= 1:
        npf_bigrams[ctx['preceding'][-1]] += 1

print(f"\n  Token immediately preceding paragraph-final -am:")
for word, ct in pf_bigrams.most_common(10):
    npf_ct = npf_bigrams.get(word, 0)
    print(f"    {word:>14s}: {ct:4d} para-final, {npf_ct:4d} non-final")

# ============================================================
# GAP 4: SHORT vs LONG PARAGRAPH STRUCTURE
# ============================================================
print("\n" + "="*70)
print("GAP 4: SHORT vs LONG PARAGRAPH STRUCTURE")
print("="*70)

# Classify paragraphs
short_paras = []   # 2-4 body lines
medium_paras = []  # 5-7 body lines
long_paras = []    # 8+ body lines

for folio, section, regime, para in all_paragraphs:
    body = [l for l in para.lines if not l.is_header]
    n_body = len(body)
    if n_body <= 1:
        continue
    entry = (folio, section, regime, para, body)
    if n_body <= 4:
        short_paras.append(entry)
    elif n_body <= 7:
        medium_paras.append(entry)
    else:
        long_paras.append(entry)

print(f"\n  Short (2-4): {len(short_paras)}")
print(f"  Medium (5-7): {len(medium_paras)}")
print(f"  Long (8+): {len(long_paras)}")

# Compare structure
for label, group in [('SHORT', short_paras), ('MEDIUM', medium_paras), ('LONG', long_paras)]:
    if not group:
        continue

    # Cycling behavior
    interleave_rates = [p.mode_interleave_rate for _, _, _, p, _ in group if p.mode_interleave_rate is not None]
    # Kernel balance
    k_counts = Counter()
    for _, _, _, para, body in group:
        for l in body:
            for t in l.tokens:
                for k in t.kernels:
                    k_counts[k] += 1
    k_total = sum(k_counts.values()) or 1

    # Mode distribution
    mode_counts = Counter()
    for _, _, _, para, body in group:
        for l in body:
            if l.suffix_mode:
                mode_counts[l.suffix_mode] += 1
    mode_total = sum(mode_counts.values()) or 1

    # Line-final patterns
    final_suffixes = Counter()
    for _, _, _, para, body in group:
        for l in body:
            if l.tokens:
                m = l.tokens[-1].morph
                final_suffixes[m.suffix or 'BARE'] += 1
    final_total = sum(final_suffixes.values()) or 1

    # Tail product signature
    tail_sigs = Counter(p.tail_product_signature for _, _, _, p, _ in group if p.tail_product_signature)

    mean_interleave = sum(interleave_rates) / len(interleave_rates) if interleave_rates else 0

    print(f"\n  {label} (n={len(group)}):")
    print(f"    Mode interleave rate: {mean_interleave:.3f}")
    print(f"    Kernel: k={k_counts.get('k',0)/k_total*100:.1f}%, e={k_counts.get('e',0)/k_total*100:.1f}%, h={k_counts.get('h',0)/k_total*100:.1f}%")
    print(f"    Mode A: {mode_counts.get('A',0)/mode_total*100:.1f}%, Mode B: {mode_counts.get('B',0)/mode_total*100:.1f}%")
    print(f"    Final -am: {final_suffixes.get('am',0)/final_total*100:.1f}%, -dy: {(final_suffixes.get('dy',0)+final_suffixes.get('edy',0))/final_total*100:.1f}%, BARE: {final_suffixes.get('BARE',0)/final_total*100:.1f}%")
    print(f"    Tail signatures: {dict(tail_sigs.most_common(3))}")

# Section distribution by length class
print(f"\n  Section composition by paragraph length:")
for label, group in [('SHORT', short_paras), ('MEDIUM', medium_paras), ('LONG', long_paras)]:
    sec_dist = Counter(section for _, section, _, _, _ in group)
    total_g = len(group) or 1
    sec_str = ', '.join(f"{s}:{c/total_g*100:.0f}%" for s, c in sec_dist.most_common())
    print(f"    {label}: {sec_str}")

# ============================================================
# GAP 5: HEADER COMPLEXITY -> BODY LENGTH
# ============================================================
print("\n" + "="*70)
print("GAP 5: HEADER COMPLEXITY -> BODY LENGTH")
print("="*70)

header_body_pairs = []  # (header_metrics, body_length)

for folio, section, regime, para in all_paragraphs:
    if not para.lines:
        continue
    header = para.lines[0] if para.lines[0].is_header else None
    body = [l for l in para.lines if not l.is_header]
    if not header or len(body) < 1:
        continue

    # Header metrics
    h_tokens = header.token_count
    h_unique_middles = len(set(t.morph.middle for t in header.tokens if t.morph.middle))
    h_ht_count = sum(1 for t in header.tokens if t.morph.middle and len(t.morph.middle) > 4)  # compound proxy
    h_kernels = Counter()
    for t in header.tokens:
        for k in t.kernels:
            h_kernels[k] += 1
    h_kernel_diversity = len(h_kernels)

    header_body_pairs.append({
        'h_tokens': h_tokens,
        'h_unique_middles': h_unique_middles,
        'h_ht_count': h_ht_count,
        'h_kernel_diversity': h_kernel_diversity,
        'body_length': len(body),
        'section': section,
    })

print(f"\n  Paragraphs with header + body: {len(header_body_pairs)}")

# Correlations
def pearson_r(xs, ys):
    n = len(xs)
    if n < 3:
        return 0
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den_x = sum((x - x_mean)**2 for x in xs) ** 0.5
    den_y = sum((y - y_mean)**2 for y in ys) ** 0.5
    return num / (den_x * den_y) if den_x > 0 and den_y > 0 else 0

body_lens = [p['body_length'] for p in header_body_pairs]

for metric in ['h_tokens', 'h_unique_middles', 'h_ht_count', 'h_kernel_diversity']:
    vals = [p[metric] for p in header_body_pairs]
    r = pearson_r(vals, body_lens)
    print(f"  {metric:>20s} vs body_length: r = {r:+.3f}")

# Quartile analysis: do complex headers predict longer bodies?
h_token_sorted = sorted(header_body_pairs, key=lambda p: p['h_tokens'])
q_size = len(h_token_sorted) // 4
if q_size > 10:
    q1 = h_token_sorted[:q_size]
    q4 = h_token_sorted[-q_size:]
    q1_mean = sum(p['body_length'] for p in q1) / len(q1)
    q4_mean = sum(p['body_length'] for p in q4) / len(q4)
    print(f"\n  Simplest headers (Q1, mean {sum(p['h_tokens'] for p in q1)/len(q1):.1f} tokens): body length = {q1_mean:.1f}")
    print(f"  Most complex headers (Q4, mean {sum(p['h_tokens'] for p in q4)/len(q4):.1f} tokens): body length = {q4_mean:.1f}")
    ratio = q4_mean / q1_mean if q1_mean > 0 else 0
    print(f"  Ratio: {ratio:.2f}x")

# Within-section correlation (controls for section confound)
print(f"\n  Within-section header-body correlations:")
for sec in sorted(set(p['section'] for p in header_body_pairs)):
    sec_pairs = [p for p in header_body_pairs if p['section'] == sec]
    if len(sec_pairs) < 10:
        continue
    vals = [p['h_tokens'] for p in sec_pairs]
    bls = [p['body_length'] for p in sec_pairs]
    r = pearson_r(vals, bls)
    print(f"    {sec}: n={len(sec_pairs)}, r(h_tokens, body_length) = {r:+.3f}")

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "="*70)
print("SYNTHESIS")
print("="*70)

# Compile results
results = {
    'gap1_distribution': {
        'n_paragraphs': n,
        'mean_body_length': round(mean_len, 2),
        'std': round(std_len, 2),
        'variance': round(var_len, 2),
        'dispersion_ratio': round(dispersion, 2),
        'geometric_p': round(p_geom, 4),
        'chi2_geometric': round(chi2_geom, 2),
        'df': df_geom,
        'length_distribution': {str(k): v for k, v in sorted(length_counts.items())},
        'section_means': {sec: round(sum(v)/len(v), 2) for sec, v in section_lengths.items()},
    },
    'gap2_effects': {
        'section_f': round(f_sec, 2) if k_sec > 1 else None,
        'section_eta2': round(eta2_sec, 3) if k_sec > 1 else None,
        'regime_f': round(f_reg, 2) if k_reg > 1 else None,
        'regime_eta2': round(eta2_reg, 3) if k_reg > 1 else None,
        'regime_means': {reg: round(sum(v)/len(v), 2) for reg, v in regime_lengths.items()},
    },
    'gap3_am_context': {
        'para_final_am_count': len(para_final_am_contexts),
        'nonpara_final_am_count': len(nonpara_final_am_contexts),
        'para_final_top_words': dict(pf_am_words.most_common(10)),
        'nonpara_final_top_words': dict(npf_am_words.most_common(10)),
        'para_final_mean_position': round(sum(pf_pos)/len(pf_pos), 3) if pf_pos else None,
        'nonpara_final_mean_position': round(sum(npf_pos)/len(npf_pos), 3) if npf_pos else None,
        'para_final_mean_linelen': round(sum(pf_linelen)/len(pf_linelen), 1) if pf_linelen else None,
        'nonpara_final_mean_linelen': round(sum(npf_linelen)/len(npf_linelen), 1) if npf_linelen else None,
    },
    'gap4_short_vs_long': {
        'short_count': len(short_paras),
        'medium_count': len(medium_paras),
        'long_count': len(long_paras),
    },
    'gap5_header_body': {
        'n_pairs': len(header_body_pairs),
        'correlations': {
            metric: round(pearson_r([p[metric] for p in header_body_pairs], body_lens), 3)
            for metric in ['h_tokens', 'h_unique_middles', 'h_ht_count', 'h_kernel_diversity']
        },
    },
}

output_path = OUTPUT_DIR / 'termination_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
