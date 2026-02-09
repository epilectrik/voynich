"""Brunschwig compound MIDDLE differentiation test.

The aggregate REGIME test confirmed broad glosses (k=heat, e=cool, ch=check).
Now we ask: can Brunschwig's SPECIFIC operations differentiate COMPOUND middles?

Brunschwig heat application methods:
  - Balneum marie (water bath, indirect, sustained gentle)
  - Ash bath (per cinerem, indirect, moderate)
  - Sand bath (per arenam, indirect, moderate-intense)
  - Direct fire (per ignem, intense, direct)
  - No-fire methods: sunshine, ant hill, horse dung, baker's oven

Brunschwig cooling operations:
  - Remove from heat source
  - Let stand overnight (mandatory safety)
  - Gradual cooling (prevent glass cracking from thermal shock)
  - Cool BEFORE opening vessel (prevent vapor loss)

Brunschwig monitoring protocols:
  - Finger test (temperature check)
  - Drip rate timing (distillation speed)
  - Thumbnail viscosity test (quality)
  - Cloudiness check (contamination)
  - Color/smell check (degradation)
  - Taste test (potency)

Question: Do k-compound, e-compound, and ch-compound middles
distribute differently across REGIMEs in ways that match these
specific Brunschwig operations?
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))
regime_mapping = json.load(open('results/regime_folio_mapping.json', encoding='utf-8'))

# Build folio -> regime lookup
folio_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_regime[f] = regime

# --- Collect compound MIDDLE distributions by REGIME ---
# Focus on k-family, e-family, ch-family compounds
k_compounds = {}  # middle -> {regime -> count}
e_compounds = {}
h_compounds = {}
monitoring_compounds = {}  # ch/sh as middle

all_middles_by_regime = defaultdict(lambda: Counter())
regime_totals = Counter()

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if not regime:
        continue
    regime_totals[regime] += 1

    m = morph.extract(token.word)
    if not m.middle:
        continue

    mid = m.middle
    gloss = md['middles'].get(mid, {}).get('gloss') or ''
    all_middles_by_regime[mid][regime] += 1

    # Classify into families
    # K-family: middles containing k (heat operations)
    if 'k' in mid and ('heat' in gloss or 'lock' in gloss or 'precision' in gloss):
        if mid not in k_compounds:
            k_compounds[mid] = Counter()
        k_compounds[mid][regime] += 1

    # E-family: middles starting with e (cooling/settling operations)
    if mid.startswith('e') and ('cool' in gloss or 'discharge' in gloss or 'sustain' in gloss):
        if mid not in e_compounds:
            e_compounds[mid] = Counter()
        e_compounds[mid][regime] += 1

    # H-family: h-containing middles (hazard operations)
    if 'h' in mid and ('hazard' in gloss or 'heat-check' in gloss):
        if mid not in h_compounds:
            h_compounds[mid] = Counter()
        h_compounds[mid][regime] += 1

    # Monitoring: ch, sh as middles or in compounds
    if ('check' in gloss or 'verify' in gloss) and mid not in ('ck', 'eck'):
        if mid not in monitoring_compounds:
            monitoring_compounds[mid] = Counter()
        monitoring_compounds[mid][regime] += 1


def print_family(name, compounds, min_count=15):
    """Print REGIME distribution for a compound family."""
    print(f"\n{'='*80}")
    print(f"{name} COMPOUNDS - REGIME Distribution")
    print(f"{'='*80}")
    print(f"{'Middle':<14} {'Gloss':<25} {'Total':>5} {'R1%':>7} {'R2%':>7} {'R3%':>7} {'R4%':>7}  {'Peak REGIME'}")
    print(f"{'-'*14} {'-'*25} {'-'*5} {'-'*7} {'-'*7} {'-'*7} {'-'*7}  {'-'*15}")

    sorted_compounds = sorted(compounds.items(), key=lambda x: -sum(x[1].values()))
    for mid, regime_counts in sorted_compounds:
        total = sum(regime_counts.values())
        if total < min_count:
            continue
        gloss = md['middles'].get(mid, {}).get('gloss') or '?'
        # Normalize by regime size to get enrichment
        rates = {}
        for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            n = regime_totals[r]
            raw = regime_counts.get(r, 0)
            rates[r] = (raw / n * 100) if n > 0 else 0

        peak = max(rates, key=rates.get)
        peak_short = peak.replace('REGIME_', 'R')

        r1 = rates['REGIME_1']
        r2 = rates['REGIME_2']
        r3 = rates['REGIME_3']
        r4 = rates['REGIME_4']

        # Calculate enrichment ratio (peak vs mean)
        mean = sum(rates.values()) / 4
        enrich = rates[peak] / mean if mean > 0 else 0

        gloss_short = gloss[:24]
        marker = f'  ({enrich:.1f}x)' if enrich > 1.3 else ''
        print(f"  {mid:<14} {gloss_short:<25} {total:>5} {r1:>6.2f} {r2:>6.2f} {r3:>6.2f} {r4:>6.2f}  {peak_short}{marker}")

    return sorted_compounds


# --- Print all families ---
k_sorted = print_family("K-FAMILY (HEAT)", k_compounds, min_count=10)
e_sorted = print_family("E-FAMILY (COOLING)", e_compounds, min_count=10)
h_sorted = print_family("H-FAMILY (HAZARD)", h_compounds, min_count=5)
m_sorted = print_family("MONITORING (CHECK/VERIFY)", monitoring_compounds, min_count=10)


# --- Brunschwig operation mapping analysis ---
print(f"\n{'='*80}")
print(f"BRUNSCHWIG OPERATION MAPPING")
print(f"{'='*80}")
print(f"""
Brunschwig describes these specific heat methods:
  1. Balneum marie (water bath) -> Fire degree 1 -> REGIME_2
  2. Ash/sand bath (indirect)   -> Fire degree 2 -> REGIME_1
  3. Direct fire                -> Fire degree 3 -> REGIME_3
  4. Precision/animal           -> Fire degree 4 -> REGIME_4

If k-compound middles encode heat METHOD (not just intensity),
then each compound should peak in the REGIME matching its method.
""")

# Map k-compounds to Brunschwig methods based on REGIME peaks
print(f"K-COMPOUND REGIME PEAKS -> Brunschwig Method Hypothesis:")
print(f"{'-'*70}")
brunschwig_method = {
    'REGIME_1': 'Ash/sand bath (moderate, indirect)',
    'REGIME_2': 'Balneum marie (water bath, gentle)',
    'REGIME_3': 'Direct fire (intense)',
    'REGIME_4': 'Precision (animal, tight tolerance)',
}

for mid, regime_counts in sorted(k_compounds.items(), key=lambda x: -sum(x[1].values())):
    total = sum(regime_counts.values())
    if total < 10:
        continue
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    rates = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_totals[r]
        rates[r] = (regime_counts.get(r, 0) / n * 100) if n > 0 else 0
    peak = max(rates, key=rates.get)
    method = brunschwig_method.get(peak, '?')
    peak_short = peak.replace('REGIME_', 'R')
    print(f"  {mid:<14} '{gloss}'  -> peaks in {peak_short} -> {method}")


# --- E-compound differentiation ---
print(f"\n\nE-COMPOUND REGIME PEAKS -> Brunschwig Cooling Hypothesis:")
print(f"{'-'*70}")
print(f"""
Brunschwig cooling operations:
  - Quick remove from heat (active, during process)
  - Gradual cooling (prevent thermal shock)
  - Overnight standing (passive, extended)
  - Cool before opening (safety)

If e-compounds encode cooling TYPE:
""")

for mid, regime_counts in sorted(e_compounds.items(), key=lambda x: -sum(x[1].values())):
    total = sum(regime_counts.values())
    if total < 10:
        continue
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    rates = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_totals[r]
        rates[r] = (regime_counts.get(r, 0) / n * 100) if n > 0 else 0
    peak = max(rates, key=rates.get)
    peak_short = peak.replace('REGIME_', 'R')

    # What cooling type would make sense for this regime?
    if peak == 'REGIME_2':
        interp = 'Overnight/extended cooling (gentle process, long cool)'
    elif peak == 'REGIME_1':
        interp = 'Standard cooling (moderate process)'
    elif peak == 'REGIME_3':
        interp = 'Rapid cool-down (intense process, thermal shock risk)'
    elif peak == 'REGIME_4':
        interp = 'Precision cooling (tight tolerance, careful)'
    else:
        interp = '?'

    print(f"  {mid:<14} '{gloss}'  -> peaks in {peak_short} -> {interp}")


# --- Positional analysis: do k-compounds appear at different line positions? ---
print(f"\n\n{'='*80}")
print(f"POSITIONAL ANALYSIS: K-compounds within lines")
print(f"{'='*80}")
print(f"If compounds encode different heat STAGES, they should appear at different positions.\n")

# Pre-compute token positions within lines
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    line_tokens[(token.folio, token.line)].append(token)

token_positions = {}  # (folio, line, word_index) -> normalized position
for key, tokens in line_tokens.items():
    n = len(tokens)
    for i, tok in enumerate(tokens):
        pos = i / max(1, n - 1) if n > 1 else 0.5
        token_positions[(tok.folio, tok.line, i)] = pos

k_positions = defaultdict(list)
idx_tracker = defaultdict(int)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    key = (token.folio, token.line)
    idx = idx_tracker[key]
    idx_tracker[key] += 1
    m = morph.extract(token.word)
    if not m.middle:
        continue
    mid = m.middle
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None and mid in k_compounds and sum(k_compounds[mid].values()) >= 20:
        k_positions[mid].append(pos)

print(f"{'Middle':<14} {'Gloss':<25} {'Mean Pos':>8} {'N':>5}  {'Interpretation'}")
print(f"{'-'*14} {'-'*25} {'-'*8} {'-'*5}  {'-'*30}")

for mid in sorted(k_positions.keys(), key=lambda m: sum(k_compounds[m].values()), reverse=True):
    positions = k_positions[mid]
    if len(positions) < 20:
        continue
    mean_pos = sum(positions) / len(positions)
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    gloss_short = gloss[:24]

    if mean_pos < 0.4:
        interp = 'EARLY (setup/ignition?)'
    elif mean_pos < 0.5:
        interp = 'EARLY-MID (active heating?)'
    elif mean_pos < 0.6:
        interp = 'MID (main process?)'
    else:
        interp = 'LATE (sustained/finishing?)'

    print(f"  {mid:<14} {gloss_short:<25} {mean_pos:>7.3f} {len(positions):>5}  {interp}")


# --- Same for e-compounds ---
print(f"\n{'='*80}")
print(f"POSITIONAL ANALYSIS: E-compounds within lines")
print(f"{'='*80}\n")

e_positions = defaultdict(list)
idx_tracker2 = defaultdict(int)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    key = (token.folio, token.line)
    idx = idx_tracker2[key]
    idx_tracker2[key] += 1
    m = morph.extract(token.word)
    if not m.middle:
        continue
    mid = m.middle
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None and mid in e_compounds and sum(e_compounds[mid].values()) >= 15:
        e_positions[mid].append(pos)

print(f"{'Middle':<14} {'Gloss':<25} {'Mean Pos':>8} {'N':>5}  {'Interpretation'}")
print(f"{'-'*14} {'-'*25} {'-'*8} {'-'*5}  {'-'*30}")

for mid in sorted(e_positions.keys(), key=lambda m: sum(e_compounds[m].values()), reverse=True):
    positions = e_positions[mid]
    if len(positions) < 15:
        continue
    mean_pos = sum(positions) / len(positions)
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    gloss_short = gloss[:24]

    if mean_pos < 0.4:
        interp = 'EARLY (pre-cool? remove from heat?)'
    elif mean_pos < 0.5:
        interp = 'EARLY-MID (active cooling?)'
    elif mean_pos < 0.6:
        interp = 'MID (gradual cooling?)'
    else:
        interp = 'LATE (final cool/overnight?)'

    print(f"  {mid:<14} {gloss_short:<25} {mean_pos:>7.3f} {len(positions):>5}  {interp}")


# --- Bigram analysis: what follows k-compounds? ---
print(f"\n{'='*80}")
print(f"BIGRAM ANALYSIS: What follows each K-compound?")
print(f"{'='*80}")
print(f"Brunschwig: after heating comes monitoring, then cooling.\n")

# Build bigrams
bigrams = defaultdict(lambda: Counter())
prev_mid = None
prev_tok = None
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        prev_mid = None
        continue
    m = morph.extract(token.word)
    if not m.middle:
        prev_mid = None
        continue

    if prev_mid and prev_mid in k_compounds and sum(k_compounds[prev_mid].values()) >= 20:
        # What operation follows this k-compound?
        next_gloss = md['middles'].get(m.middle, {}).get('gloss') or m.middle
        bigrams[prev_mid][next_gloss] += 1

    prev_mid = m.middle

print(f"{'K-compound':<14} {'Top 5 following operations'}")
print(f"{'-'*14} {'-'*60}")
for mid in sorted(bigrams.keys(), key=lambda m: sum(k_compounds[m].values()), reverse=True):
    total = sum(bigrams[mid].values())
    if total < 15:
        continue
    top5 = bigrams[mid].most_common(5)
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    following = ', '.join(f"{g}({c})" for g, c in top5)
    print(f"  {mid:<14} {following[:70]}")


# --- Summary: proposed gloss refinements ---
print(f"\n\n{'='*80}")
print(f"PROPOSED GLOSS REFINEMENTS (from Brunschwig mapping)")
print(f"{'='*80}")
print(f"""
Based on REGIME distribution, positional data, and bigram context:

K-FAMILY (heat application methods):
  Check which compounds peak in which REGIME above.
  - Compounds peaking in R1 (degree 2) = standard/indirect heating
  - Compounds peaking in R2 (degree 1) = gentle/water bath heating
  - Compounds peaking in R3 (degree 3) = intense/direct heating
  - Compounds peaking in R4 (degree 4) = precision heating

E-FAMILY (cooling operations):
  Check positional data above.
  - EARLY e-compounds = active removal from heat
  - MID e-compounds = gradual cooling (thermal shock prevention)
  - LATE e-compounds = extended cooling (overnight standing)

Bigram data shows what operation FOLLOWS each heat type,
which constrains interpretation (heating followed by monitoring
vs heating followed by more heating tells you different things).
""")
