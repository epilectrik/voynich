"""
Can we identify fermentation in the Voynich text?

Fermentation (putrefaction in alchemical terms):
  - LONG duration (days to weeks)
  - LOW sustained heat (balneum mariae, ~40-80C)
  - PASSIVE monitoring (watch color, smell, bubbles)
  - NO active testing (don't disturb it)
  - SEALED vessel (lute and leave)
  - NO transfers during the process
  - NO material additions during the process

Structural predictions:
  - HIGH sh (passive monitor), LOW ch (active test) -> sh:ch ratio >> 1
  - LOW qo prefix (not actively managing heat)
  - HIGH e-HEAD (stabilizing/cooling domain)
  - LOW k-HEAD (not doing active heating)
  - FEW dar (no material additions)
  - FEW transfer-class tokens
  - Possibly: -dy suffix concentration (sealed/closed operations)

Compare against distillation (active heating+testing) and
material addition (dar-heavy) paragraphs.
"""

import sys, os, io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

def paragraph_signature(ptokens):
    """Compute operational signature for a set of tokens."""
    n = len(ptokens)
    if n == 0:
        return None
    pre = Counter()
    heads = Counter()
    suffs = Counter()
    words = [t.word for t in ptokens]

    for t in ptokens:
        m = morph.extract(t.word)
        if m.prefix: pre[m.prefix] += 1
        mid = m.middle or ''
        if mid:
            c0 = mid[0]
            if c0 in 'aeokt':
                heads[c0] += 1
        if m.suffix: suffs[m.suffix] += 1

    sh = pre.get('sh', 0)
    ch = pre.get('ch', 0) + pre.get('pch', 0) + pre.get('tch', 0) + pre.get('dch', 0) + pre.get('lch', 0)
    qo = pre.get('qo', 0) + pre.get('ko', 0) + pre.get('ke', 0) + pre.get('lk', 0)
    ok_ot = pre.get('ok', 0) + pre.get('ot', 0)
    da = pre.get('da', 0) + pre.get('sa', 0)

    k_head = heads.get('k', 0)
    e_head = heads.get('e', 0)
    t_head = heads.get('t', 0)

    dar_n = words.count('dar')
    dy_suf = suffs.get('dy', 0) + sum(1 for w in words if w == 'dy')

    sh_ch_ratio = sh / ch if ch > 0 else (99.0 if sh > 0 else 0.0)

    return {
        'n': n,
        'sh': sh, 'ch': ch, 'sh_ch_ratio': sh_ch_ratio,
        'sh_pct': 100*sh/n, 'ch_pct': 100*ch/n,
        'qo_pct': 100*qo/n,
        'ok_ot_pct': 100*ok_ot/n,
        'da_pct': 100*da/n,
        'k_pct': 100*k_head/n, 'e_pct': 100*e_head/n, 't_pct': 100*t_head/n,
        'dar': dar_n,
        'dy_pct': 100*dy_suf/n,
    }


# ═══ BUILD ALL PARAGRAPHS ACROSS ALL CURRIER B FOLIOS ═══
all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
folios = sorted(set(t.folio for t in all_b))

all_paragraphs = []

for folio in folios:
    ftokens = [t for t in all_b if t.folio == folio]
    flines = sorted(set(t.line for t in ftokens), key=lambda x: int(x) if x.isdigit() else 0)

    # Detect paragraph boundaries (gallows-initial lines)
    para_bounds = []
    for li in flines:
        lt = [t for t in ftokens if t.line == li]
        if lt and lt[0].word and lt[0].word[0] in 'tkpf' and len(lt[0].word) > 1:
            para_bounds.append(li)

    for i, start in enumerate(para_bounds):
        if i + 1 < len(para_bounds):
            end_idx = flines.index(para_bounds[i + 1])
            p_lines = flines[flines.index(start):end_idx]
        else:
            p_lines = flines[flines.index(start):]
        p_tokens = [t for t in ftokens if t.line in p_lines]
        if len(p_tokens) >= 5:  # skip tiny fragments
            all_paragraphs.append({
                'folio': folio, 'pidx': i+1,
                'lines': p_lines, 'tokens': p_tokens,
                'n': len(p_tokens),
            })

print(f"Total paragraphs (5+ tokens): {len(all_paragraphs)} across {len(folios)} folios")

# ═══ COMPUTE SIGNATURES ═══
sigs = []
for p in all_paragraphs:
    sig = paragraph_signature(p['tokens'])
    if sig:
        sig['folio'] = p['folio']
        sig['pidx'] = p['pidx']
        sig['lines'] = f"{p['lines'][0]}-{p['lines'][-1]}"
        sigs.append(sig)

# ═══ FERMENTATION FILTER ═══
# Fermentation signature: high sh, low ch, low qo, high e, low k
# Define thresholds
print("\n" + "=" * 100)
print("FERMENTATION CANDIDATES")
print("Criteria: sh > 20%, ch < 10%, qo < 15%, e-HEAD > 25%, k-HEAD < 15%, 10+ tokens")
print("=" * 100)

ferm_candidates = []
for sig in sigs:
    if (sig['n'] >= 10 and
        sig['sh_pct'] > 20 and
        sig['ch_pct'] < 10 and
        sig['qo_pct'] < 15 and
        sig['e_pct'] > 25 and
        sig['k_pct'] < 15):
        ferm_candidates.append(sig)

ferm_candidates.sort(key=lambda s: s['sh_ch_ratio'], reverse=True)

print(f"\nFound {len(ferm_candidates)} candidates out of {len(sigs)} paragraphs")
print(f"\n{'Folio':>8s} P# {'Tok':>4s} {'sh%':>5s} {'ch%':>5s} {'sh:ch':>6s} {'qo%':>5s} {'k%':>5s} {'e%':>5s} {'dar':>4s} Lines")
print("-" * 80)
for s in ferm_candidates:
    ratio_str = f"{s['sh_ch_ratio']:.1f}" if s['sh_ch_ratio'] < 50 else "INF"
    print(f"{s['folio']:>8s} P{s['pidx']:<2d} {s['n']:4d} {s['sh_pct']:5.1f} {s['ch_pct']:5.1f} {ratio_str:>6s} {s['qo_pct']:5.1f} {s['k_pct']:5.1f} {s['e_pct']:5.1f} {s['dar']:4d} L{s['lines']}")

# ═══ WHAT FOLIOS HAVE FERMENTATION-LIKE PARAGRAPHS? ═══
ferm_folios = sorted(set(s['folio'] for s in ferm_candidates))
print(f"\nFolios with fermentation-like paragraphs: {len(ferm_folios)}")
print(f"  {', '.join(ferm_folios)}")

# ═══ COMPARE: f75r P5 vs CORPUS ═══
print("\n" + "=" * 100)
print("f75r P5 IN CONTEXT (our predicted fermentation paragraph)")
print("=" * 100)

f75r_p5 = [s for s in sigs if s['folio'] == 'f75r' and s['pidx'] == 5]
if f75r_p5:
    s = f75r_p5[0]
    print(f"  sh={s['sh_pct']:.1f}%  ch={s['ch_pct']:.1f}%  sh:ch={s['sh_ch_ratio']:.1f}  qo={s['qo_pct']:.1f}%  k={s['k_pct']:.1f}%  e={s['e_pct']:.1f}%  dar={s['dar']}")

    # Rank among all paragraphs on sh:ch ratio
    all_ratios = sorted([s2['sh_ch_ratio'] for s2 in sigs if s2['n'] >= 10], reverse=True)
    rank = all_ratios.index(s['sh_ch_ratio']) + 1
    print(f"  sh:ch ratio rank: {rank}/{len(all_ratios)} (top {100*rank/len(all_ratios):.1f}%)")

# ═══ RELAXED SEARCH: Just sh-dominant paragraphs ═══
print("\n" + "=" * 100)
print("SH-DOMINANT PARAGRAPHS (sh > 2*ch, 10+ tokens)")
print("These are PASSIVE MONITORING zones - fermentation, slow reactions, waiting")
print("=" * 100)

sh_dom = [s for s in sigs if s['n'] >= 10 and s['sh_pct'] > 2 * s['ch_pct'] and s['sh_pct'] > 15]
sh_dom.sort(key=lambda s: s['sh_ch_ratio'], reverse=True)

print(f"\nFound {len(sh_dom)} sh-dominant paragraphs")
print(f"\n{'Folio':>8s} P# {'Tok':>4s} {'sh%':>5s} {'ch%':>5s} {'sh:ch':>6s} {'qo%':>5s} {'k%':>5s} {'e%':>5s} {'dar':>4s} Lines")
print("-" * 80)
for s in sh_dom[:30]:
    ratio_str = f"{s['sh_ch_ratio']:.1f}" if s['sh_ch_ratio'] < 50 else "INF"
    print(f"{s['folio']:>8s} P{s['pidx']:<2d} {s['n']:4d} {s['sh_pct']:5.1f} {s['ch_pct']:5.1f} {ratio_str:>6s} {s['qo_pct']:5.1f} {s['k_pct']:5.1f} {s['e_pct']:5.1f} {s['dar']:4d} L{s['lines']}")

# ═══ CHECK: Do fermentation candidates cluster on balneum folios? ═══
print("\n" + "=" * 100)
print("BALNEUM CROSS-CHECK")
print("Do fermentation candidates overlap with chekar-bearing folios?")
print("=" * 100)

# Folios with chekar
chekar_folios = set()
for t in all_b:
    if t.word == 'chekar':
        chekar_folios.add(t.folio)
print(f"\nFolios with chekar: {sorted(chekar_folios)}")
print(f"Fermentation candidate folios: {sorted(ferm_folios)}")
overlap = chekar_folios & set(ferm_folios)
print(f"Overlap: {sorted(overlap) if overlap else 'NONE'}")

# ═══ SPECIFIC FERMENTATION MARKERS ═══
print("\n" + "=" * 100)
print("CANDIDATE FERMENTATION MARKERS")
print("Tokens that appear disproportionately in fermentation-like paragraphs")
print("=" * 100)

# Count token types in fermentation vs non-fermentation paragraphs
ferm_words = Counter()
nonferm_words = Counter()
ferm_total = 0
nonferm_total = 0

ferm_ids = set((s['folio'], s['pidx']) for s in ferm_candidates)
for p in all_paragraphs:
    words = [t.word for t in p['tokens']]
    if (p['folio'], p['pidx']) in ferm_ids:
        ferm_words.update(words)
        ferm_total += len(words)
    else:
        nonferm_words.update(words)
        nonferm_total += len(words)

print(f"\nFermentation tokens: {ferm_total}, Non-fermentation: {nonferm_total}")

# Find enriched tokens
enriched = []
for word, ferm_ct in ferm_words.items():
    nf_ct = nonferm_words.get(word, 0)
    ferm_rate = ferm_ct / ferm_total
    nf_rate = nf_ct / nonferm_total if nonferm_total > 0 else 0
    if nf_rate > 0 and ferm_ct >= 3:
        enrichment = ferm_rate / nf_rate
        if enrichment > 2.0:
            enriched.append((word, ferm_ct, nf_ct, enrichment))

enriched.sort(key=lambda x: x[3], reverse=True)

print(f"\nTokens enriched >2x in fermentation paragraphs (min 3 occurrences):")
print(f"  {'Token':<16s} {'Ferm':>5s} {'Other':>6s} {'Enrich':>7s}  Morphology")
print("-" * 70)
for word, fc, nc, enr in enriched[:25]:
    m = morph.extract(word)
    pre = m.prefix or 'BARE'
    mid = m.middle or '?'
    suf = m.suffix or ''
    print(f"  {word:<16s} {fc:5d} {nc:6d} {enr:7.1f}x  {pre}+{mid}+{suf}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
