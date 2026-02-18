#!/usr/bin/env python3
"""Quick profile of Rosettes folios."""
import sys, json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, BTokenAnalysis

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load regime
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Rosettes folios
ROSETTE_FOLIOS = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Build token data
folio_tokens = defaultdict(list)
folio_section = {}

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens[tok.folio].append(tok)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

print("=" * 70)
print("ROSETTES FOLIO PROFILES")
print("=" * 70)
print()

# Basic stats
for f in sorted(ROSETTE_FOLIOS):
    if f not in folio_tokens:
        print(f"  {f}: NO TOKENS (not in Currier B?)")
        continue
    toks = folio_tokens[f]
    sec = folio_section.get(f, '?')
    reg = folio_regime.get(f, '?')
    print(f"  {f}: {len(toks)} tokens, section={sec}, regime={reg}")

print()

# Detailed profiling
print("-" * 70)
print("KERNEL BALANCE PER ROSETTES FOLIO")
print("-" * 70)
print()
print(f"  {'Folio':<10} {'k%':>8} {'h%':>8} {'e%':>8} {'k/e':>8} {'Sec':>5} {'Regime':>10}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*5} {'-'*10}")

rosette_kernels = Counter()
for f in sorted(ROSETTE_FOLIOS):
    if f not in folio_tokens:
        continue
    kernels = Counter()
    for tok in folio_tokens[f]:
        m = morph.extract(tok.word)
        if m.middle:
            for c in m.middle:
                if c in ('k', 'h', 'e'):
                    kernels[c] += 1
    total = sum(kernels.values())
    if total == 0:
        continue
    k_pct = 100 * kernels['k'] / total
    h_pct = 100 * kernels['h'] / total
    e_pct = 100 * kernels['e'] / total
    ke = kernels['k'] / kernels['e'] if kernels['e'] > 0 else float('inf')
    print(f"  {f:<10} {k_pct:>7.1f}% {h_pct:>7.1f}% {e_pct:>7.1f}% {ke:>8.3f} {folio_section.get(f,'?'):>5} {folio_regime.get(f,'?'):>10}")
    rosette_kernels += kernels

# Rosettes aggregate
total = sum(rosette_kernels.values())
if total > 0:
    print(f"  {'ROSETTES':<10} {100*rosette_kernels['k']/total:>7.1f}% {100*rosette_kernels['h']/total:>7.1f}% {100*rosette_kernels['e']/total:>7.1f}% {rosette_kernels['k']/rosette_kernels['e']:>8.3f}")

# Corpus comparison
print()
all_kernels = Counter()
for f, toks in folio_tokens.items():
    for tok in toks:
        m = morph.extract(tok.word)
        if m.middle:
            for c in m.middle:
                if c in ('k', 'h', 'e'):
                    all_kernels[c] += 1
at = sum(all_kernels.values())
print(f"  {'CORPUS':<10} {100*all_kernels['k']/at:>7.1f}% {100*all_kernels['h']/at:>7.1f}% {100*all_kernels['e']/at:>7.1f}% {all_kernels['k']/all_kernels['e']:>8.3f}")

# LINK, hazard, lanes, CC triggers
print()
print("-" * 70)
print("OPERATIONAL PROFILE PER ROSETTES FOLIO")
print("-" * 70)
print()

HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey', 'ar', 'c', 'he', 'shedy'}

print(f"  {'Folio':<10} {'LINK%':>8} {'HazDen':>8} {'QO%':>8} {'CHSH%':>8} {'AXM_self':>10} {'Tokens':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*8}")

for f in sorted(ROSETTE_FOLIOS):
    if f not in folio_tokens:
        continue
    toks = folio_tokens[f]
    n = len(toks)

    n_link = 0
    n_haz = 0
    lanes = Counter()
    states = []

    for tok in toks:
        m = morph.extract(tok.word)
        if not m.middle:
            continue

        # LINK
        if m.prefix and m.prefix in ('lk', 'lo'):
            n_link += 1

        # Hazard
        if m.middle in HAZARD_SOURCES:
            n_haz += 1

        # Lane
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            if lane:
                lanes[lane] += 1

        # Macro state
        analysis = decoder.analyze_token(tok.word)
        if analysis.macro_state:
            states.append(analysis.macro_state)

    lane_total = sum(lanes.values())
    qo_pct = 100 * lanes.get('QO', 0) / lane_total if lane_total > 0 else 0
    chsh_pct = 100 * lanes.get('CHSH', 0) / lane_total if lane_total > 0 else 0

    # AXM self-transition
    axm_self = 0
    if len(states) > 1:
        same = sum(1 for i in range(len(states)-1) if states[i] == states[i+1])
        axm_self = same / (len(states) - 1)

    link_pct = 100 * n_link / n if n > 0 else 0
    haz_den = 100 * n_haz / n if n > 0 else 0

    print(f"  {f:<10} {link_pct:>7.2f}% {haz_den:>7.1f}% {qo_pct:>7.1f}% {chsh_pct:>7.1f}% {axm_self:>10.3f} {n:>8}")

# State run analysis for Rosettes
print()
print("-" * 70)
print("STATE RUN LENGTHS (Rosettes vs Sections)")
print("-" * 70)
print()

def compute_runs(token_list):
    runs = []
    current = None
    length = 0
    for tok in token_list:
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        analysis = decoder.analyze_token(tok.word)
        state = analysis.macro_state
        if state is None:
            continue
        if state == current:
            length += 1
        else:
            if current is not None:
                runs.append(length)
            current = state
            length = 1
    if current is not None:
        runs.append(length)
    return runs

# Rosettes aggregate runs
all_rosette_runs = []
for f in ROSETTE_FOLIOS:
    if f in folio_tokens:
        all_rosette_runs.extend(compute_runs(folio_tokens[f]))

if all_rosette_runs:
    print(f"  Rosettes: mean_run={np.mean(all_rosette_runs):.2f}, "
          f"median={np.median(all_rosette_runs):.1f}, "
          f"max={max(all_rosette_runs)}, "
          f"pct_1={100*sum(1 for r in all_rosette_runs if r==1)/len(all_rosette_runs):.1f}%, "
          f"pct_5+={100*sum(1 for r in all_rosette_runs if r>=5)/len(all_rosette_runs):.1f}%")

# Compare with section medians from Phase 386
print()
print("  Section comparison (from Phase 386):")
print(f"  Bio:    mean_run=2.50, pct_10+=4.2%")
print(f"  Cosmo:  mean_run=1.85, pct_10+=0.4%")
print(f"  Herbal: mean_run=1.72, pct_10+=0.7%")
print(f"  Stars:  mean_run=2.12, pct_10+=1.8%")

# f85v2 special check (noted as anomalous k=0 in constraints)
print()
print("-" * 70)
print("f85v2 SPECIAL CHECK (C459 noted as anomalous, k=0)")
print("-" * 70)
f85v2_toks = folio_tokens.get('f85v2', [])
if f85v2_toks:
    print(f"  f85v2 tokens: {len(f85v2_toks)}")
    # Check if it's in H track
    print(f"  NOTE: f85v2 has ONLY U and V transcribers (no H track)")
    print(f"  -> This folio is EXCLUDED from all H-only analysis")
else:
    print(f"  f85v2: 0 tokens in Currier B (H-track)")
    print(f"  This folio has no H-transcriber data - it's a gap in our coverage")

# Check what the Rosettes look like compared to Cosmo section overall
print()
print("-" * 70)
print("ROSETTES vs REST OF COSMO")
print("-" * 70)
print()

cosmo_folios = [f for f, s in folio_section.items() if s == 'C']
rosette_in_cosmo = [f for f in cosmo_folios if f in ROSETTE_FOLIOS]
non_rosette_cosmo = [f for f in cosmo_folios if f not in ROSETTE_FOLIOS]
print(f"  Cosmo folios: {sorted(cosmo_folios)}")
print(f"  Rosettes in Cosmo: {sorted(rosette_in_cosmo)}")
print(f"  Non-Rosettes Cosmo: {sorted(non_rosette_cosmo)}")
print(f"  -> Rosettes ARE Cosmo (mostly). {len(rosette_in_cosmo)}/{len(cosmo_folios)} Cosmo folios are Rosettes.")

# Unique MIDDLEs in Rosettes
print()
print("-" * 70)
print("VOCABULARY OVERLAP")
print("-" * 70)
print()

rosette_middles = set()
for f in ROSETTE_FOLIOS:
    for tok in folio_tokens.get(f, []):
        m = morph.extract(tok.word)
        if m.middle:
            rosette_middles.add(m.middle)

all_middles = set()
non_rosette_middles = set()
for f, toks in folio_tokens.items():
    for tok in toks:
        m = morph.extract(tok.word)
        if m.middle:
            all_middles.add(m.middle)
            if f not in ROSETTE_FOLIOS:
                non_rosette_middles.add(m.middle)

rosette_unique = rosette_middles - non_rosette_middles
shared = rosette_middles & non_rosette_middles

print(f"  Rosettes MIDDLEs: {len(rosette_middles)}")
print(f"  Non-Rosettes MIDDLEs: {len(non_rosette_middles)}")
print(f"  Shared: {len(shared)}")
print(f"  Rosette-unique: {len(rosette_unique)}")
if rosette_unique:
    print(f"  Unique MIDDLEs: {sorted(rosette_unique)}")
print(f"  Vocabulary overlap: {100*len(shared)/len(rosette_middles):.1f}% of Rosettes vocabulary appears elsewhere")

print()
print("=" * 70)
print("DONE")
