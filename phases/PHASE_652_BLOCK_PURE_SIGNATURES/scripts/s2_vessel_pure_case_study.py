"""
Case study on the 13 vessel-pure block-pure paragraphs.

Hypothesis (crazy-expert): these 13 paragraphs are not statistical noise but
a distinct structural class - "vessel-state preamble" paragraphs that declare
apparatus configuration before the operational body of the folio.

Test: do they cluster at folio-opening positions (paragraph indices 0, 1, 2)?

If yes -> new structural class candidate
If no -> dead hypothesis, the 13 are sample noise
"""
import sys
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

# Re-derive the 13 vessel-pure paragraphs (same logic as earlier)
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

def block_of(p):
    if p in FIRE: return 'F'
    if p in VESSEL: return 'V'
    return None

# Folio paragraph counts (for relative position)
folio_max_par = defaultdict(int)
for (f, par_idx) in paragraphs:
    folio_max_par[f] = max(folio_max_par[f], par_idx)

# Identify vessel-pure paragraphs
vessel_pure = []
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue
    prefix_counts = Counter()
    block_counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            prefix_counts[p] += 1
            block_counts[block_of(p)] += 1
    target_total = sum(prefix_counts.values())
    if target_total < 4: continue
    fire_frac = block_counts.get('F', 0) / target_total
    vessel_frac = block_counts.get('V', 0) / target_total
    if vessel_frac > 0.70:
        # Find dominant channel
        dom_channel = max(VESSEL, key=lambda p: prefix_counts.get(p, 0))
        vessel_pure.append({
            'folio': folio, 'par_idx': par_idx, 'tokens': toks,
            'token_count': len(toks),
            'vessel_frac': vessel_frac,
            'dom_channel': dom_channel,
            'prefix_counts': dict(prefix_counts),
            'max_par_in_folio': folio_max_par[folio],
            'rel_position': par_idx / max(folio_max_par[folio], 1),
            'is_first_par': (par_idx == 0),
            'is_first_two': (par_idx <= 1),
        })

print(f"Vessel-pure paragraphs (>70% vessel-side): {len(vessel_pure)}")
print()

# Sort by folio + par_idx
vessel_pure.sort(key=lambda d: (d['folio'], d['par_idx']))

print("="*100)
print("CASE STUDY: 13 VESSEL-PURE PARAGRAPHS")
print("="*100)
print()
print(f"{'Folio':>7s}  {'Par':>3s}  {'/of':>4s}  {'rel':>5s}  {'Chan':>4s}  {'Tok':>4s}  Vessel%  Section  First sample tokens")
print("-"*120)

# Get section per folio
folio_section = {}
for t in tx.currier_b():
    if t.folio not in folio_section:
        folio_section[t.folio] = t.section

position_counts = Counter()
section_counts = Counter()
for d in vessel_pure:
    sec = folio_section.get(d['folio'], '?')
    section_counts[sec] += 1
    if d['is_first_par']:
        position_counts['first'] += 1
    elif d['is_first_two']:
        position_counts['first_two'] += 1
    elif d['rel_position'] >= 0.7:
        position_counts['late'] += 1
    else:
        position_counts['middle'] += 1

    sample_tokens = ' '.join(t.word for t in d['tokens'][:8])
    print(f"  {d['folio']:>5s}  {d['par_idx']:>3d}  {d['max_par_in_folio']:>4d}  "
          f"{d['rel_position']:>5.2f}  {d['dom_channel']:>4s}  {d['token_count']:>4d}  "
          f"{d['vessel_frac']*100:>6.1f}%  {sec:>5s}     {sample_tokens}")

print()
print("="*100)
print("POSITION ANALYSIS")
print("="*100)
print()
print(f"Total: {len(vessel_pure)} vessel-pure paragraphs")
print()
print(f"Position distribution:")
print(f"  Paragraph 0 (folio-opening): {position_counts['first']}")
print(f"  Paragraph 1 (just after open): {position_counts['first_two']}")
print(f"  Middle of folio: {position_counts['middle']}")
print(f"  Late in folio (rel >= 0.7): {position_counts['late']}")
print()

# Compare to baseline: how do all paragraphs distribute?
all_positions = []
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue
    rel = par_idx / max(folio_max_par[folio], 1)
    if par_idx == 0:
        all_positions.append('first')
    elif par_idx == 1:
        all_positions.append('first_two')
    elif rel >= 0.7:
        all_positions.append('late')
    else:
        all_positions.append('middle')
all_pos_counts = Counter(all_positions)
total_baseline = sum(all_pos_counts.values())

print(f"Baseline (all paragraphs):")
for pos in ('first', 'first_two', 'middle', 'late'):
    pct = all_pos_counts[pos] / total_baseline * 100
    print(f"  {pos}: {all_pos_counts[pos]} ({pct:.1f}%)")

print()
print(f"Section distribution:")
for sec in sorted(section_counts.keys()):
    print(f"  Section {sec}: {section_counts[sec]}")

# Statistical test: Fisher's exact / chi-square against null
# H0: vessel-pure paragraphs distribute like all paragraphs across positions
# If significantly more "first" or "first_two" than baseline -> preamble class
import math
def chi_square(observed, expected):
    if any(e == 0 for e in expected): return None
    return sum((o - e)**2 / e for o, e in zip(observed, expected))

# Test: vessel-pure first-or-first-two count vs baseline rate
n_vp = len(vessel_pure)
vp_early = position_counts['first'] + position_counts['first_two']
baseline_early_rate = (all_pos_counts['first'] + all_pos_counts['first_two']) / total_baseline
expected_early = n_vp * baseline_early_rate
print()
print("="*100)
print("SIGNIFICANCE TEST: vessel-pure early-position concentration")
print("="*100)
print(f"  Vessel-pure paragraphs at folio-opening (par 0 or 1): {vp_early}/{n_vp} = {vp_early/n_vp*100:.1f}%")
print(f"  Baseline rate of par 0 or 1 across all paragraphs: {baseline_early_rate*100:.1f}%")
print(f"  Expected count under null: {expected_early:.2f}")
print(f"  Observed count: {vp_early}")
if vp_early > expected_early * 1.3:
    print(f"  -> EARLY-ENRICHED (>30% above expected)")
elif vp_early < expected_early * 0.7:
    print(f"  -> EARLY-DEPLETED")
else:
    print(f"  -> consistent with baseline (no positional bias)")

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/vessel_pure_case_study.json', 'w') as f:
    json.dump({
        'count': len(vessel_pure),
        'paragraphs': [{k: v for k, v in d.items() if k != 'tokens'} for d in vessel_pure],
        'position_counts': dict(position_counts),
        'baseline_early_rate': baseline_early_rate,
        'expected_early': expected_early,
        'observed_early': vp_early,
    }, f, indent=2, default=str)
print()
print("Saved: scratch/vessel_pure_case_study.json")
