"""Brunschwig Balneum Marie -> REGIME_2 Gloss Validation Test.

Decompose Brunschwig's balneum marie (water bath) procedure into
structural operations, then check if REGIME_2 folio paragraphs
show matching token sequences with current glosses.

Brunschwig balneum marie procedure (Fire Degree 1):
  1. GATHER/SELECT material (delicate flowers, animal parts)
  2. SETUP apparatus (glass vessel in water bath)
  3. APPLY GENTLE HEAT (degree 1 = lukewarm, finger-test level)
  4. MONITOR continuously (finger test, drip observation)
  5. SUSTAIN temperature (maintain gentle warmth)
  6. CHECK quality (taste, smell, thumbnail viscosity)
  7. COOL overnight (mandatory thermal safety)
  8. COLLECT distillate
  9. CLOSE/STORE

Expected Voynich predictions for REGIME_2:
  - ke (gentle heat) enriched vs k (direct heat)
  - sh/ch (observe/check) elevated — continuous monitoring
  - e tokens (cool) elevated — overnight cooling emphasis
  - od (collect) present — distillate collection
  - pch/tch (chop/pound) LOWER than other regimes — delicate materials
  - LINK density HIGH — Brunschwig says continuous monitoring for degree 1
  - -ey suffix (set) — condition established before proceeding
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology, BFolioDecoder, MiddleDictionary

# --- Setup ---
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))

# REGIME_2 folios (from regime_folio_mapping.json)
regime_2_folios = ['f105r', 'f105v', 'f107r', 'f113v', 'f115v',
                   'f26v', 'f48r', 'f48v', 'f85v2', 'f86v3', 'f86v5']

# All B folios for comparison
regime_mapping = json.load(open('results/regime_folio_mapping.json', encoding='utf-8'))
all_regimes = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        all_regimes[f] = regime

# --- Helper: extract operation profile from tokens ---
def get_operation_profile(tokens):
    """Extract Brunschwig-relevant operation counts from a list of tokens."""
    profile = Counter()
    for token in tokens:
        if not token.word.strip() or '*' in token.word:
            continue
        m = morph.extract(token.word)

        # Prefix operations
        if m.prefix == 'ch':
            profile['CHECK'] += 1
        elif m.prefix == 'sh':
            profile['OBSERVE'] += 1
        elif m.prefix == 'qo':
            profile['ENERGY'] += 1
        elif m.prefix == 'ol':
            profile['CONTINUE'] += 1
        elif m.prefix == 'da':
            profile['SETUP'] += 1
        elif m.prefix == 'ok':
            profile['LOCK'] += 1
        elif m.prefix in ('pch', 'tch', 'kch', 'fch'):
            profile['PREP_MECHANICAL'] += 1
        elif m.prefix in ('ke', 'te', 'se', 'de', 'pe'):
            profile['SUSTAINED'] += 1
        elif m.prefix in ('lk', 'lch', 'lsh'):
            profile['L_COMPOUND'] += 1

        # Middle operations
        if m.middle:
            mid_gloss = md['middles'].get(m.middle, {}).get('gloss') or ''
            if 'gentle heat' in mid_gloss or m.middle == 'ke':
                profile['GENTLE_HEAT'] += 1
            elif 'heat' in mid_gloss and 'gentle' not in mid_gloss:
                profile['DIRECT_HEAT'] += 1
            elif 'cool' in mid_gloss:
                profile['COOLING'] += 1
            elif 'check' in mid_gloss or 'verify' in mid_gloss:
                profile['VERIFICATION'] += 1
            elif 'collect' in mid_gloss:
                profile['COLLECTION'] += 1
            elif 'hazard' in mid_gloss:
                profile['HAZARD'] += 1
            elif 'precision' in mid_gloss:
                profile['PRECISION'] += 1
            elif 'frame' in mid_gloss:
                profile['FRAME'] += 1
            elif 'transfer' in mid_gloss:
                profile['TRANSFER'] += 1
            elif 'work' in mid_gloss:
                profile['WORK'] += 1
            elif 'close' in mid_gloss:
                profile['CLOSE'] += 1
            elif 'sustain' in mid_gloss:
                profile['SUSTAIN'] += 1

        # Suffix markers
        if m.suffix == 'ey':
            profile['SET_CONDITION'] += 1
        elif m.suffix == 'am':
            profile['FINALIZE'] += 1
        elif m.suffix in ('aiin', 'ain'):
            profile['CHECK_SUFFIX'] += 1
        elif m.suffix in ('dy', 'ar'):
            profile['CLOSE_SUFFIX'] += 1

    return profile


# --- Analysis 1: REGIME_2 vs other REGIMEs operation profiles ---
print("=" * 70)
print("TEST: Balneum Marie Operation Predictions vs REGIME_2")
print("=" * 70)

regime_profiles = defaultdict(lambda: Counter())
regime_token_counts = Counter()

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = all_regimes.get(token.folio)
    if not regime:
        continue
    m = morph.extract(token.word)
    regime_token_counts[regime] += 1

    # Count key operations
    if m.middle:
        mid_gloss = md['middles'].get(m.middle, {}).get('gloss') or ''
        if 'gentle heat' in mid_gloss or m.middle == 'ke':
            regime_profiles[regime]['gentle_heat'] += 1
        elif 'heat' in mid_gloss and 'gentle' not in mid_gloss:
            regime_profiles[regime]['direct_heat'] += 1
        if 'cool' in mid_gloss:
            regime_profiles[regime]['cooling'] += 1
        if 'check' in mid_gloss or 'verify' in mid_gloss:
            regime_profiles[regime]['checking'] += 1
        if 'collect' in mid_gloss:
            regime_profiles[regime]['collecting'] += 1
        if 'precision' in mid_gloss:
            regime_profiles[regime]['precision'] += 1
        if 'hazard' in mid_gloss:
            regime_profiles[regime]['hazard'] += 1

    if m.prefix in ('pch', 'tch', 'kch', 'fch'):
        regime_profiles[regime]['prep_mechanical'] += 1
    if m.prefix in ('sh', 'ch'):
        regime_profiles[regime]['monitoring'] += 1
    if m.prefix == 'ol':
        regime_profiles[regime]['continuation'] += 1

print(f"\nOperation rates by REGIME (per 100 tokens):")
print(f"{'Operation':<20} {'R1':>8} {'R2':>8} {'R3':>8} {'R4':>8}  {'Prediction'}")
print(f"{'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  {'-'*30}")

ops = ['gentle_heat', 'direct_heat', 'cooling', 'checking', 'monitoring',
       'collecting', 'precision', 'hazard', 'prep_mechanical', 'continuation']
predictions = {
    'gentle_heat': 'R2 HIGH (balneum marie = gentle)',
    'direct_heat': 'R2 LOW (not direct fire)',
    'cooling': 'R2 HIGH (overnight cooling emphasis)',
    'checking': 'R2 HIGH (continuous monitoring)',
    'monitoring': 'R2 HIGH (finger test, drip obs)',
    'collecting': 'R2 similar (all collect distillate)',
    'precision': 'R4 HIGH (tight tolerances)',
    'hazard': 'R3 HIGH (intense = more hazardous)',
    'prep_mechanical': 'R2 LOW (delicate materials)',
    'continuation': 'R2 HIGH (sustained operations)',
}

results = {}
for op in ops:
    rates = {}
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_token_counts[regime]
        if n > 0:
            rate = regime_profiles[regime][op] / n * 100
        else:
            rate = 0.0
        rates[regime] = rate
    results[op] = rates

    r1 = rates.get('REGIME_1', 0)
    r2 = rates.get('REGIME_2', 0)
    r3 = rates.get('REGIME_3', 0)
    r4 = rates.get('REGIME_4', 0)

    # Check if R2 is highest/lowest as predicted
    all_rates = [r1, r2, r3, r4]
    if 'HIGH' in predictions[op] and 'R2' in predictions[op]:
        match = 'PASS' if r2 == max(all_rates) else ('PARTIAL' if r2 > (sum(all_rates)/4) else 'FAIL')
    elif 'LOW' in predictions[op] and 'R2' in predictions[op]:
        match = 'PASS' if r2 == min(all_rates) else ('PARTIAL' if r2 < (sum(all_rates)/4) else 'FAIL')
    elif 'R4' in predictions[op]:
        match = 'PASS' if r4 == max(all_rates) else 'PARTIAL'
    elif 'R3' in predictions[op]:
        match = 'PASS' if r3 == max(all_rates) else 'PARTIAL'
    else:
        match = '-'

    pred = predictions[op]
    print(f"  {op:<20} {r1:>7.2f} {r2:>7.2f} {r3:>7.2f} {r4:>7.2f}  {match:<8} {pred}")


# --- Analysis 2: Gentle/Direct heat ratio by REGIME ---
print(f"\n{'='*70}")
print(f"GENTLE vs DIRECT HEAT RATIO")
print(f"{'='*70}")
print(f"Balneum marie prediction: R2 has highest gentle/direct ratio\n")

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    g = regime_profiles[regime]['gentle_heat']
    d = regime_profiles[regime]['direct_heat']
    ratio = g / d if d > 0 else float('inf')
    n = regime_token_counts[regime]
    print(f"  {regime}: gentle={g}, direct={d}, ratio={ratio:.3f}  (n={n})")


# --- Analysis 3: Sample REGIME_2 paragraphs with glosses ---
print(f"\n{'='*70}")
print(f"REGIME_2 SAMPLE PARAGRAPHS (glossed)")
print(f"{'='*70}")
print(f"Checking if operation sequences match balneum marie procedure\n")

# Show first 3 REGIME_2 folios, first 2 paragraphs each
for folio in regime_2_folios[:4]:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
    except Exception as exc:
        print(f"  {folio}: skipped - {exc}")
        continue

    print(f"\n  FOLIO: {folio}")
    for para in paras[:2]:
        print(f"    {para.paragraph_id} ({para.line_count} lines, {para.token_count} tokens)")
        print(f"    Kernel balance: {para.kernel_balance}")

        # Show operation sequence for each line
        for line in para.lines:
            glosses = []
            for tok in line.tokens:
                g = tok.interpretive()
                if g:
                    # Truncate long glosses
                    g = g[:40]
                glosses.append(g)
            gloss_str = ' | '.join(glosses)
            print(f"      L{line.line_id}: {gloss_str[:120]}")
        print()


# --- Analysis 4: Operation sequence within REGIME_2 paragraphs ---
print(f"\n{'='*70}")
print(f"OPERATION SEQUENCE ANALYSIS")
print(f"{'='*70}")
print(f"Do REGIME_2 paragraphs follow SETUP->HEAT->MONITOR->COOL->COLLECT order?\n")

# For each R2 paragraph, extract the sequence of operation types
sequence_matches = 0
total_paras = 0

# Define Brunschwig operation phases
def classify_operation(token, morph_obj, middle_dict):
    """Classify a token into Brunschwig operational phase."""
    m = morph_obj.extract(token.word)
    if not m.middle:
        return None
    mid_gloss = middle_dict['middles'].get(m.middle, {}).get('gloss') or ''

    # Phase classification (ordered)
    if m.prefix in ('da', 'sa') or m.suffix == 'am':
        return 'SETUP'
    if m.prefix in ('pch', 'tch', 'kch', 'fch'):
        return 'PREP'
    if 'gentle heat' in mid_gloss or m.middle == 'ke':
        return 'GENTLE_HEAT'
    if 'heat' in mid_gloss and 'cool' not in mid_gloss and 'check' not in mid_gloss:
        return 'HEAT'
    if m.prefix in ('sh', 'ch') or 'check' in mid_gloss or 'verify' in mid_gloss:
        return 'MONITOR'
    if 'cool' in mid_gloss:
        return 'COOL'
    if 'collect' in mid_gloss:
        return 'COLLECT'
    if 'close' in mid_gloss or m.suffix in ('dy', 'ar'):
        return 'CLOSE'
    if 'transfer' in mid_gloss:
        return 'TRANSFER'
    return 'OTHER'

phase_order = {'SETUP': 0, 'PREP': 1, 'GENTLE_HEAT': 2, 'HEAT': 2,
               'MONITOR': 3, 'COOL': 4, 'COLLECT': 5, 'CLOSE': 6,
               'TRANSFER': 3, 'OTHER': 3}

phase_sequences = []

for folio in regime_2_folios:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
    except Exception:
        continue

    for para in paras:
        total_paras += 1
        # Get operation sequence
        ops_seq = []
        for line in para.lines:
            for tok in line.tokens:
                if not tok.word.strip() or '*' in tok.word:
                    continue
                phase = classify_operation(tok, morph, md)
                if phase and phase != 'OTHER':
                    ops_seq.append(phase)

        if len(ops_seq) >= 3:
            phase_sequences.append((folio, para.paragraph_id, ops_seq))

            # Check if sequence is roughly ordered
            positions = [phase_order.get(p, 3) for p in ops_seq]
            # Compute sequence monotonicity (how well ordered is it?)
            increases = sum(1 for i in range(len(positions)-1) if positions[i+1] >= positions[i])
            monotonicity = increases / (len(positions) - 1) if len(positions) > 1 else 0
            if monotonicity > 0.6:
                sequence_matches += 1

print(f"  Total REGIME_2 paragraphs: {total_paras}")
print(f"  With 3+ classified operations: {len(phase_sequences)}")
print(f"  Roughly ordered (>60% monotonic): {sequence_matches} ({sequence_matches/len(phase_sequences)*100:.1f}%)")

# Show top 5 most ordered paragraphs
print(f"\n  BEST-ORDERED PARAGRAPHS:")
scored = []
for folio, para_id, ops in phase_sequences:
    positions = [phase_order.get(p, 3) for p in ops]
    increases = sum(1 for i in range(len(positions)-1) if positions[i+1] >= positions[i])
    mono = increases / (len(positions) - 1) if len(positions) > 1 else 0
    scored.append((folio, para_id, ops, mono))

scored.sort(key=lambda x: -x[3])
for folio, para_id, ops, mono in scored[:8]:
    seq_str = '->'.join(ops[:15])
    if len(ops) > 15:
        seq_str += f'... ({len(ops)} total)'
    print(f"    {folio} {para_id}: mono={mono:.2f}  {seq_str}")

# Show WORST ordered too (counterexamples)
print(f"\n  LEAST-ORDERED PARAGRAPHS:")
for folio, para_id, ops, mono in scored[-5:]:
    seq_str = '->'.join(ops[:15])
    if len(ops) > 15:
        seq_str += f'... ({len(ops)} total)'
    print(f"    {folio} {para_id}: mono={mono:.2f}  {seq_str}")


# --- Analysis 5: Phase distribution in REGIME_2 vs others ---
print(f"\n{'='*70}")
print(f"PHASE DISTRIBUTION BY REGIME")
print(f"{'='*70}")
print(f"What fraction of each regime is spent on each operation phase?\n")

regime_phases = defaultdict(lambda: Counter())
regime_phase_totals = Counter()

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = all_regimes.get(token.folio)
    if not regime:
        continue
    phase = classify_operation(token, morph, md)
    if phase:
        regime_phases[regime][phase] += 1
        regime_phase_totals[regime] += 1

phases_list = ['SETUP', 'PREP', 'GENTLE_HEAT', 'HEAT', 'MONITOR', 'COOL', 'COLLECT', 'CLOSE', 'TRANSFER']
print(f"{'Phase':<15} {'R1':>7} {'R2':>7} {'R3':>7} {'R4':>7}")
print(f"{'-'*15} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
for phase in phases_list:
    vals = []
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_phase_totals[regime]
        if n > 0:
            pct = regime_phases[regime][phase] / n * 100
        else:
            pct = 0
        vals.append(pct)
    # Highlight R2 if it's the highest
    marker = '  <<<' if vals[1] == max(vals) and vals[1] > 0 else ''
    print(f"  {phase:<15} {vals[0]:>6.1f}% {vals[1]:>6.1f}% {vals[2]:>6.1f}% {vals[3]:>6.1f}%{marker}")


# --- Analysis 6: Gloss quality check on R2 paragraphs ---
print(f"\n{'='*70}")
print(f"GLOSS QUALITY: REGIME_2 FOLIO SAMPLE")
print(f"{'='*70}")
print(f"Full paragraph decode for one R2 folio\n")

# Pick a representative R2 folio
for folio in ['f48r']:
    try:
        paras = decoder.analyze_folio_paragraphs(folio)
    except Exception as exc:
        print(f"  {folio}: {exc}")
        continue

    print(f"  FOLIO: {folio} ({len(paras)} paragraphs)")
    for para in paras[:3]:
        print(f"\n    {para.paragraph_id} ({para.line_count}L, {para.token_count}T, balance={para.kernel_balance})")
        for line in para.lines:
            tokens_str = ' '.join(t.word for t in line.tokens)
            glosses = []
            for tok in line.tokens:
                g = tok.interpretive()
                if g:
                    glosses.append(g)
                else:
                    glosses.append('___')
            gloss_line = ' '.join(glosses)
            print(f"      L{line.line_id}: {gloss_line[:130]}")
            if len(gloss_line) > 130:
                print(f"             {gloss_line[130:260]}")


# --- Summary ---
print(f"\n{'='*70}")
print(f"SUMMARY: Brunschwig Balneum Marie Gloss Validation")
print(f"{'='*70}")

# Count predictions
pass_count = 0
partial_count = 0
fail_count = 0
for op in ops:
    rates = results[op]
    r1, r2, r3, r4 = rates['REGIME_1'], rates['REGIME_2'], rates['REGIME_3'], rates['REGIME_4']
    all_r = [r1, r2, r3, r4]
    pred = predictions[op]
    if 'HIGH' in pred and 'R2' in pred:
        if r2 == max(all_r): pass_count += 1
        elif r2 > sum(all_r)/4: partial_count += 1
        else: fail_count += 1
    elif 'LOW' in pred and 'R2' in pred:
        if r2 == min(all_r): pass_count += 1
        elif r2 < sum(all_r)/4: partial_count += 1
        else: fail_count += 1
    elif 'R4' in pred:
        if r4 == max(all_r): pass_count += 1
        else: partial_count += 1
    elif 'R3' in pred:
        if r3 == max(all_r): pass_count += 1
        else: partial_count += 1

print(f"\n  Prediction results: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL")
print(f"  Sequence ordering: {sequence_matches}/{len(phase_sequences)} paragraphs ({sequence_matches/max(1,len(phase_sequences))*100:.0f}%) roughly monotonic")
print(f"\n  Key findings for gloss refinement:")
print(f"    - Gentle/Direct heat ratio distinguishes regimes: check above")
print(f"    - Monitoring enrichment in R2: check above")
print(f"    - Cooling emphasis in R2: check above")
print(f"    - Low mechanical prep in R2: check above (delicate materials)")
