#!/usr/bin/env python3
"""
Phase 603: Pseudo-Lull Midprocess Control Alignment

Tests whether pseudo-Lull's operational control architecture predicts
specific, validated properties of the Voynich structural grammar.

Pre-registration: PREDICTIONS.md (SHA-256 verified before execution)
Source data: Phase 602 structural profile + Voynich transcript + Brunschwig
"""

import sys, os, json, re, math, hashlib, statistics
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt
from scipy import stats
import numpy as np

# ---------------------------------------------------------------------------
# 0. Pre-registration hash verification
# ---------------------------------------------------------------------------

PHASE_DIR = PROJECT_ROOT / 'phases' / 'PSEUDO_LULL_MIDPROCESS_ALIGNMENT'
PREDICTIONS_PATH = PHASE_DIR / 'PREDICTIONS.md'
EXPECTED_HASH = '6d8b1579c00469e311be23920e1d3688c6b992613356f5b072799de7e009852f'

pred_hash = hashlib.sha256(PREDICTIONS_PATH.read_bytes()).hexdigest()
if pred_hash != EXPECTED_HASH:
    print(f'FATAL: PREDICTIONS.md hash mismatch')
    print(f'  Expected: {EXPECTED_HASH}')
    print(f'  Got:      {pred_hash}')
    sys.exit(1)
print(f'Pre-registration hash verified: {pred_hash[:16]}...')

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------

# Phase 602 profile
PROFILE_PATH = PROJECT_ROOT / 'phases' / 'PSEUDO_LULL_CHARACTERIZATION' / 'results' / 'pseudo_lull_structural_profile.json'
with open(PROFILE_PATH) as f:
    profile = json.load(f)

# Regime mapping
with open(PROJECT_ROOT / 'data' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_map = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

# B macro scaffold (for C458 hazard/recovery CVs)
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json') as f:
    scaffold_data = json.load(f)
scaffold_features = scaffold_data['features']

# AXM decomposition (for axm_self per folio)
AXM_PATH = PROJECT_ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
with open(AXM_PATH) as f:
    axm_data = json.load(f)
axm_folio_data = axm_data.get('folio_data', {})

# Token-to-class map (for N1)
CLASS_MAP_PATH = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(CLASS_MAP_PATH) as f:
    class_map_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_map_data['token_to_class'].items()}

# Brunschwig corrected text (for P3)
BRUNSCHWIG_PATH = PROJECT_ROOT / 'sources' / 'brunschwig_1512' / 'brunschwig_1512_corrected.txt'
with open(BRUNSCHWIG_PATH, encoding='utf-8') as f:
    brunschwig_text = f.read()

print(f'Phase 602 profile: {len(profile["E1_chapters"])} chapters')
print(f'Regime map: {len(regime_map)} folios')
print(f'Scaffold: {len(scaffold_features)} folios')
print(f'AXM data: {len(axm_folio_data)} folios')
print(f'Brunschwig text: {len(brunschwig_text):,} chars')

# ---------------------------------------------------------------------------
# 2. Compute Voynich per-folio metrics
# ---------------------------------------------------------------------------

tx = Transcript()
morph = Morphology()

def max_consecutive_i(middle):
    max_run = current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

folio_token_counts = Counter()
folio_ey_counts = Counter()
folio_ii_counts = Counter()
folio_section = {}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if token.placement.startswith('L'):
        continue
    folio = token.folio
    folio_section[folio] = token.section
    m = morph.extract(w)
    if m.middle and m.middle != '_EMPTY_':
        head, mods, term, frame = decompose_middle_hmt(m.middle)
    else:
        head, term = None, None
    folio_token_counts[folio] += 1
    if head == 'e' and term == 'y':
        folio_ey_counts[folio] += 1
    if m.middle and max_consecutive_i(m.middle) >= 2:
        folio_ii_counts[folio] += 1

folio_ey_rate = {f: folio_ey_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_ii_rate = {f: folio_ii_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_safety_bal = {f: folio_ey_rate[f] - folio_ii_rate[f] for f in folio_ey_rate}

print(f'\nVoynich B folios computed: {len(folio_token_counts)}')
print(f'Mean ey_rate: {statistics.mean(folio_ey_rate.values()):.4f}')
print(f'Mean ii_rate: {statistics.mean(folio_ii_rate.values()):.4f}')

# ---------------------------------------------------------------------------
# Helper: compute CV
# ---------------------------------------------------------------------------

def compute_cv(values):
    if len(values) < 2:
        return 0.0
    m = statistics.mean(values)
    if m == 0:
        return 0.0
    return statistics.stdev(values) / m

# ---------------------------------------------------------------------------
# Helper: Jensen-Shannon divergence
# ---------------------------------------------------------------------------

def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    # Avoid log(0)
    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# ===========================================================================
# S1: CALIBRATION ANCHOR
# ===========================================================================

print('\n' + '=' * 70)
print('S1: CALIBRATION ANCHOR (Stars ey_rate R1 vs R3)')
print('=' * 70)

common_folios = set(folio_ey_rate) & set(regime_map) & set(folio_section)
stars_r1_ey = [folio_ey_rate[f] for f in common_folios
               if folio_section[f] == 'S' and regime_map.get(f) == 'REGIME_1']
stars_r3_ey = [folio_ey_rate[f] for f in common_folios
               if folio_section[f] == 'S' and regime_map.get(f) == 'REGIME_3']

print(f'Stars R1 folios: {len(stars_r1_ey)}, mean ey_rate: {statistics.mean(stars_r1_ey):.4f}')
print(f'Stars R3 folios: {len(stars_r3_ey)}, mean ey_rate: {statistics.mean(stars_r3_ey):.4f}')

s1_stat, s1_p = stats.mannwhitneyu(stars_r1_ey, stars_r3_ey, alternative='greater')
s1_pass = s1_p < 0.05
print(f'Mann-Whitney U={s1_stat:.1f}, p={s1_p:.6f}')
print(f'S1 RESULT: {"PASS" if s1_pass else "FAIL"}')

if not s1_pass:
    print('\nCALIBRATION_FAILURE -- stopping all tests.')
    results = {
        'verdict': 'CALIBRATION_FAILURE',
        'S1': {'pass': False, 'U': float(s1_stat), 'p': float(s1_p)},
        'reason': 'S1 calibration anchor failed'
    }
    with open(PHASE_DIR / 'results' / 'pseudo_lull_alignment_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    sys.exit(0)

# ===========================================================================
# P1: MONITOR->ACTION CHAIN OUTCOME DISTRIBUTION
# ===========================================================================

print('\n' + '=' * 70)
print('P1: MONITOR->ACTION CHAIN OUTCOME DISTRIBUTION')
print('=' * 70)

# From E8 judgment cues by_consequence
e8 = profile['E8_judgment_cues']
consequences = e8['by_consequence']
print(f'E8 consequences: {consequences}')

cont = consequences.get('continue', 0)
proc = consequences.get('proceed', 0)
stop = consequences.get('stop', 0)
correct = consequences.get('correct', 0)
adjust = consequences.get('adjust', 0)
abort_count = consequences.get('abort', 0)
total_outcomes = cont + proc + stop + correct + adjust + abort_count

# P1a: Stabilization ratio
stabilize = cont + stop + correct
escalate = proc + adjust
p1a_ratio = stabilize / escalate if escalate > 0 else float('inf')
p1a_pass = p1a_ratio >= 2.0
print(f'\nP1a: Stabilization ratio = ({cont}+{stop}+{correct}) / ({proc}+{adjust}) = {stabilize}/{escalate} = {p1a_ratio:.2f}')
print(f'  Prediction: >= 2.0, Result: {"PASS" if p1a_pass else "FAIL"}')

# P1b: Abort fraction
p1b_frac = abort_count / total_outcomes if total_outcomes > 0 else 0
p1b_pass = p1b_frac < 0.05
print(f'\nP1b: Abort fraction = {abort_count}/{total_outcomes} = {p1b_frac:.4f}')
print(f'  Prediction: < 0.05, Result: {"PASS" if p1b_pass else "FAIL"}')

# P1c: Part-conditioned asymmetry (diagnostic)
# Need per-part judgment cue consequences -- extract from E8 sample
e8_sample = e8.get('sample', [])
part_consequences = defaultdict(lambda: Counter())
for cue in e8_sample:
    part = cue.get('part', 'Unknown')
    cons = cue.get('consequence', 'unknown')
    part_consequences[part][cons] += 1

print(f'\nP1c (diagnostic): Per-part judgment cue consequences:')
for part in ['Theorica', 'Practica', 'Mercuriorum', 'Furnis', 'Compendium']:
    pc = part_consequences.get(part, Counter())
    if sum(pc.values()) > 0:
        stab = pc.get('continue', 0) + pc.get('stop', 0) + pc.get('correct', 0)
        esc = pc.get('proceed', 0) + pc.get('adjust', 0)
        ratio = stab / esc if esc > 0 else float('inf')
        print(f'  {part}: stabilize={stab}, escalate={esc}, ratio={ratio:.2f} (n={sum(pc.values())})')

p1_pass = p1a_pass and p1b_pass
print(f'\nP1 RESULT: {"PASS" if p1_pass else "FAIL"}')

# ===========================================================================
# P2: RECOVERY DOCTRINE <-> SAFETY-STYLE SPLIT
# ===========================================================================

print('\n' + '=' * 70)
print('P2: RECOVERY DOCTRINE <-> SAFETY-STYLE SPLIT')
print('=' * 70)

# Pseudo-Lull recovery ratio
e6 = profile['E6_corrections']
recoverable = e6['recoverable']
irrecoverable = e6['irrecoverable']
pl_recovery_ratio = recoverable / irrecoverable if irrecoverable > 0 else float('inf')
print(f'Pseudo-Lull: recoverable={recoverable}, irrecoverable={irrecoverable}, ratio={pl_recovery_ratio:.2f}')

# Voynich ey/ii ratio (global mean)
mean_ey = statistics.mean(folio_ey_rate.values())
mean_ii = statistics.mean(folio_ii_rate.values())
v_ey_ii_ratio = mean_ey / mean_ii if mean_ii > 0 else float('inf')
print(f'Voynich: mean ey_rate={mean_ey:.4f}, mean ii_rate={mean_ii:.4f}, ratio={v_ey_ii_ratio:.2f}')

# P2a: Both ratios > 1.0 and same direction
p2a_pass = pl_recovery_ratio > 1.0 and v_ey_ii_ratio > 1.0
print(f'\nP2a: PL ratio > 1.0 ({pl_recovery_ratio:.2f} > 1.0: {pl_recovery_ratio > 1.0})')
print(f'     Voynich ey/ii > 1.0 ({v_ey_ii_ratio:.2f} > 1.0: {v_ey_ii_ratio > 1.0})')
print(f'  Result: {"PASS" if p2a_pass else "FAIL"}')

# P2b (diagnostic): Part with highest correction density -> section with highest safety_balance
corrections_by_part = e6['by_part']
chapters_by_part = Counter()
for ch in profile['E1_chapters']:
    chapters_by_part[ch['part']] += 1

print(f'\nP2b (diagnostic): Correction density by part:')
part_corr_density = {}
for part in ['Theorica', 'Practica', 'Mercuriorum', 'Furnis']:
    n_corr = corrections_by_part.get(part, 0)
    n_ch = chapters_by_part.get(part, 1)
    density = n_corr / n_ch
    part_corr_density[part] = density
    print(f'  {part}: {n_corr} corrections / {n_ch} chapters = {density:.2f}')

highest_corr_part = max(part_corr_density, key=part_corr_density.get)
print(f'  Highest: {highest_corr_part} ({part_corr_density[highest_corr_part]:.2f})')

# Section safety balance
section_safety = defaultdict(list)
for f in folio_safety_bal:
    sec = folio_section.get(f)
    if sec:
        section_safety[sec].append(folio_safety_bal[f])

print(f'  Voynich safety_balance by section:')
for sec in sorted(section_safety):
    vals = section_safety[sec]
    if vals:
        print(f'    {sec}: mean={statistics.mean(vals):.4f} (n={len(vals)})')

p2_pass = p2a_pass
print(f'\nP2 RESULT: {"PASS" if p2_pass else "FAIL"}')

# ===========================================================================
# P3: THRESHOLDED TERMINATION <-> CLOSURE AUTHENTICITY
# ===========================================================================

print('\n' + '=' * 70)
print('P3: THRESHOLDED TERMINATION <-> CLOSURE AUTHENTICITY')
print('=' * 70)

# Pseudo-Lull termination types
e4 = profile['E4_termination']
pl_threshold = e4['by_type'].get('threshold_based', 0)
pl_count = e4['by_type'].get('count_based', 0)
pl_ratio = pl_threshold / pl_count if pl_count > 0 else float('inf')
print(f'Pseudo-Lull: threshold={pl_threshold}, count={pl_count}, ratio={pl_ratio:.1f}')

# Extract Brunschwig termination patterns
# Use same lexicon from EXTRACTION_PROTOCOL.md
TERM_TRIGGERS_EN = [
    r'\buntil\b', r'\brepeat\b', r'\breiterate\b', r'\breiteration\b',
    r'\bas many times as\b', r'\bso often\b', r'\bcontinue\b.*\buntil\b',
    r'\biterate\b'
]
# ENHG/German termination patterns
TERM_TRIGGERS_DE = [
    r'\bbiss?\b', r'\bbiß\b',           # bis/biss (until)
    r'\bso lang\b', r'\bso lange?\b',   # so lang(e) (as long as)
    r'\bmal\b',                         # mal (times)
    r'\bofft?\b',                       # oft (often)
    r'\bwider\b.*\bmal\b',             # wider...mal (again...times)
    r'\bso offt\b',                     # so oft
]

# Count-based patterns (numbers + "mal/times")
COUNT_PATTERNS = [
    r'\b(?:ein|zwo|zwey|drey|vier|funff|sechs|sieben|acht|neun|zehen)\s*mal\b',
    r'\b\d+\s*mal\b',
    r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+times?\b',
    r'\b\d+\s+times?\b',
]

# Threshold-based patterns (state/quality terms + "until/bis")
THRESHOLD_PATTERNS = [
    # German: color/state + bis/biss
    r'\bbiss?\b.*\b(?:weiss|schwartz|rot|gelb|braun|klar|lauter|dick|dunn|trucken)\b',
    r'\b(?:weiss|schwartz|rot|gelb|braun|klar|lauter|dick|dunn|trucken)\b.*\bbiss?\b',
    r'\bbiß\b.*\b(?:weiss|schwartz|rot|gelb|braun|klar|lauter|dick|dunn|trucken)\b',
    # German: "bis es" (until it)
    r'\bbiss?\s+(?:es|das|die|der)\b',
    r'\bbiß\s+(?:es|das|die|der)\b',
    # "so lang bis" (as long as until)
    r'\bso\s+lang\w*\s+biss?\b',
]

# Scan Brunschwig text
brun_lines = brunschwig_text.split('\n')
brun_threshold_count = 0
brun_count_count = 0
brun_total_termination = 0

for line in brun_lines:
    if line.strip().startswith('---'):
        continue  # skip page headers
    line_lower = line.lower()

    is_termination = False
    for pat in TERM_TRIGGERS_DE:
        if re.search(pat, line_lower):
            is_termination = True
            break

    if not is_termination:
        continue

    brun_total_termination += 1

    # Classify: count-based or threshold-based
    is_count = False
    for pat in COUNT_PATTERNS:
        if re.search(pat, line_lower):
            is_count = True
            break

    is_threshold = False
    for pat in THRESHOLD_PATTERNS:
        if re.search(pat, line_lower):
            is_threshold = True
            break

    if is_count:
        brun_count_count += 1
    if is_threshold:
        brun_threshold_count += 1

# Remaining lines that matched termination triggers but not count/threshold
brun_other = brun_total_termination - brun_count_count - brun_threshold_count
# Lines matching both count and threshold are double-counted; adjust
print(f'Brunschwig termination lines: {brun_total_termination}')
print(f'  Threshold-pattern: {brun_threshold_count}')
print(f'  Count-pattern: {brun_count_count}')
print(f'  Other: {brun_other}')

brun_ratio = brun_threshold_count / brun_count_count if brun_count_count > 0 else float('inf')
print(f'  Brunschwig threshold/count ratio: {brun_ratio:.2f}')
print(f'  Pseudo-Lull threshold/count ratio: {pl_ratio:.1f}')

if brun_ratio > 0 and brun_ratio != float('inf'):
    gap = pl_ratio / brun_ratio
    p3a_pass = gap >= 3.0
    print(f'  Gap: {pl_ratio:.1f} / {brun_ratio:.2f} = {gap:.2f}x')
else:
    # If Brunschwig has 0 count-based, ratio is inf; PL can't be >= 3x inf
    # If Brunschwig has 0 threshold, ratio is 0; PL/0 = inf >= 3.0
    if brun_count_count == 0 and brun_threshold_count == 0:
        p3a_pass = True  # Brunschwig has no termination patterns at all
        gap = float('inf')
        print(f'  Brunschwig has no classifiable termination patterns')
    elif brun_count_count == 0:
        p3a_pass = False  # Can't compute ratio
        gap = float('nan')
        print(f'  Brunschwig has 0 count-based (ratio=inf, cannot compare)')
    else:
        p3a_pass = True
        gap = float('inf')
        print(f'  Brunschwig ratio=0 (all count-based), PL dominates')

print(f'  Prediction: PL ratio >= 3x Brunschwig ratio')
print(f'  Result: {"PASS" if p3a_pass else "FAIL"}')

# P3b (diagnostic): MONOSTATE -- AXM fraction > 50% in all sections
print(f'\nP3b (diagnostic): AXM fraction by section')
section_axm = defaultdict(list)
for f, fdata in axm_folio_data.items():
    sec = fdata.get('section', folio_section.get(f))
    axm_self = fdata.get('axm_self')
    if sec and axm_self is not None:
        section_axm[sec].append(axm_self)

p3b_all_above_50 = True
for sec in sorted(section_axm):
    vals = section_axm[sec]
    if vals:
        m = statistics.mean(vals)
        above = m > 0.50
        if not above:
            p3b_all_above_50 = False
        print(f'  {sec}: mean AXM self-transition = {m:.4f} (n={len(vals)}) {"OK" if above else "BELOW 50%"}')

print(f'  All sections > 50%: {p3b_all_above_50}')

p3_pass = p3a_pass
print(f'\nP3 RESULT: {"PASS" if p3_pass else "FAIL"}')

# ===========================================================================
# P4: RECOVERY ASYMMETRY (CLAMPED HAZARD / FREE RECOVERY)
# ===========================================================================

print('\n' + '=' * 70)
print('P4: RECOVERY ASYMMETRY (C458)')
print('=' * 70)

# P4a: Pseudo-Lull convergent recovery
e6_design = e6['design_pattern']
n_failure_modes = e6_design['n_failure_modes']
n_correction_strategies = e6_design['n_correction_strategies']
p4a_ratio = n_failure_modes / n_correction_strategies if n_correction_strategies > 0 else float('inf')
p4a_pass = p4a_ratio > 2.0
print(f'P4a: failure_modes={n_failure_modes}, correction_strategies={n_correction_strategies}, ratio={p4a_ratio:.2f}')
print(f'  Prediction: > 2.0, Result: {"PASS" if p4a_pass else "FAIL"}')

# P4b: Voynich hazard CV < 0.15, recovery CV > 0.50
all_hazard = [feat['hazard_density'] for feat in scaffold_features.values()]
all_recovery = [feat['recovery_ops_count'] for feat in scaffold_features.values()]

hazard_cv = compute_cv(all_hazard)
recovery_cv = compute_cv(all_recovery)

p4b_pass = hazard_cv < 0.15 and recovery_cv > 0.50
print(f'\nP4b: Voynich hazard_density CV = {hazard_cv:.4f} (predict < 0.15: {hazard_cv < 0.15})')
print(f'     Voynich recovery_ops CV = {recovery_cv:.4f} (predict > 0.50: {recovery_cv > 0.50})')
print(f'  Result: {"PASS" if p4b_pass else "FAIL"}')

# P4c (diagnostic): Per-part correction density CV
print(f'\nP4c (diagnostic): Per-part correction density CV')
part_densities = list(part_corr_density.values())
p4c_cv = compute_cv(part_densities)
print(f'  Part correction densities: {[f"{k}={v:.2f}" for k,v in part_corr_density.items()]}')
print(f'  CV = {p4c_cv:.4f} (predict > 0.30: {p4c_cv > 0.30})')

p4_pass = p4a_pass and p4b_pass
print(f'\nP4 RESULT: {"PASS" if p4_pass else "FAIL"}')

# ===========================================================================
# P5: REGISTER ARCHITECTURE (SAME INVENTORY, DIFFERENT WEIGHTING)
# ===========================================================================

print('\n' + '=' * 70)
print('P5: REGISTER ARCHITECTURE')
print('=' * 70)

# Build operation-family frequency vectors per pseudo-Lull part
all_families = set()
part_family_counts = defaultdict(Counter)
for ch in profile['E1_chapters']:
    part = ch['part']
    fam = ch.get('primary_family')
    if fam:
        part_family_counts[part][fam] += 1
        all_families.add(fam)
    sec_fam = ch.get('secondary_family')
    if sec_fam:
        # Don't double-count for primary, but note presence
        all_families.add(sec_fam)

all_families = sorted(all_families)
parts = ['Theorica', 'Practica', 'Mercuriorum', 'Furnis']

print(f'All families ({len(all_families)}): {all_families}')

# Build frequency vectors
part_vectors = {}
for part in parts:
    vec = [part_family_counts[part].get(fam, 0) for fam in all_families]
    part_vectors[part] = vec
    present = sum(1 for v in vec if v > 0)
    print(f'  {part}: {present}/{len(all_families)} families present, total={sum(vec)}')

# P5a: Pairwise JSD > 0.05 AND shared families >= 60%
print(f'\nPairwise JSD and family overlap:')
pair_jsds = []
pair_overlaps = []
p5a_all_jsd_above = True
p5a_all_overlap_above = True

for i in range(len(parts)):
    for j in range(i + 1, len(parts)):
        v1 = np.array(part_vectors[parts[i]], dtype=float)
        v2 = np.array(part_vectors[parts[j]], dtype=float)
        d = jsd(v1, v2)
        pair_jsds.append(d)

        # Shared families: both have count > 0
        shared = sum(1 for a, b in zip(v1, v2) if a > 0 and b > 0)
        total_present = sum(1 for a, b in zip(v1, v2) if a > 0 or b > 0)
        overlap = shared / total_present if total_present > 0 else 0
        pair_overlaps.append(overlap)

        jsd_ok = d > 0.05
        overlap_ok = overlap >= 0.60
        if not jsd_ok:
            p5a_all_jsd_above = False
        if not overlap_ok:
            p5a_all_overlap_above = False

        print(f'  {parts[i]} vs {parts[j]}: JSD={d:.4f} {"OK" if jsd_ok else "LOW"}, overlap={overlap:.2f} ({shared}/{total_present}) {"OK" if overlap_ok else "LOW"}')

p5a_pass = p5a_all_jsd_above and p5a_all_overlap_above
print(f'\nP5a: All JSD > 0.05: {p5a_all_jsd_above}')
print(f'     All overlap >= 60%: {p5a_all_overlap_above}')
print(f'  Result: {"PASS" if p5a_pass else "FAIL"}')

# P5b (diagnostic): Mean JSD in [0.05, 0.50]
mean_jsd = statistics.mean(pair_jsds)
p5b_in_range = 0.05 <= mean_jsd <= 0.50
print(f'\nP5b (diagnostic): Mean pairwise JSD = {mean_jsd:.4f} (in [0.05, 0.50]: {p5b_in_range})')
print(f'  Voynich C1134 reference: inter-section JS = 0.124')

p5_pass = p5a_pass
print(f'\nP5 RESULT: {"PASS" if p5_pass else "FAIL"}')

# ===========================================================================
# N1: NEGATIVE CONTROL -- NO CROSS-SECTION RANK PREDICTION
# ===========================================================================

print('\n' + '=' * 70)
print('N1: NEGATIVE CONTROL (Cross-System Structural Distance)')
print('=' * 70)

# Strategy: Compare inter-part structural distance patterns (pseudo-Lull)
# with inter-section structural distance patterns (Voynich).
# If pseudo-Lull parts map to Voynich sections, their distance matrices
# should correlate. Per C1739, they should NOT correlate.
#
# Pseudo-Lull: 4 parts -> 6 pairwise distances (operation-family JSD)
# Voynich: 4 largest sections (S,H,B,P) -> 6 pairwise distances (class JSD)
# Mantel-like test: Spearman between the two 6-element distance vectors.
# Test all 24 possible part-to-section pairings; report minimum p-value.

# Pseudo-Lull: already have part_vectors from P5 (operation-family frequency per part)
# pl_parts = ['Theorica', 'Practica', 'Mercuriorum', 'Furnis']
# part_vectors[part] = frequency vector over all_families

# Voynich: compute section-level instruction class frequency vectors
section_class_counts = defaultdict(Counter)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or token.placement.startswith('L'):
        continue
    cls = token_to_class.get(w)
    if cls is not None:
        section_class_counts[token.section][cls] += 1

# Use 4 largest sections
v_sections = ['S', 'H', 'B', 'P']
all_classes = sorted(set(c for sec in v_sections for c in section_class_counts[sec]))
section_vectors = {}
for sec in v_sections:
    vec = [section_class_counts[sec].get(c, 0) for c in all_classes]
    section_vectors[sec] = vec

# Compute pseudo-Lull 6 pairwise JSDs (already computed in P5 for parts)
# Re-extract from part_vectors
pl_parts_ordered = ['Theorica', 'Practica', 'Mercuriorum', 'Furnis']
pl_pair_jsds = []
for i in range(4):
    for j in range(i + 1, 4):
        v1 = np.array(part_vectors[pl_parts_ordered[i]], dtype=float)
        v2 = np.array(part_vectors[pl_parts_ordered[j]], dtype=float)
        pl_pair_jsds.append(jsd(v1, v2))

# Compute Voynich 6 pairwise JSDs
v_pair_jsds = []
for i in range(4):
    for j in range(i + 1, 4):
        v1 = np.array(section_vectors[v_sections[i]], dtype=float)
        v2 = np.array(section_vectors[v_sections[j]], dtype=float)
        v_pair_jsds.append(jsd(v1, v2))

print(f'PL inter-part JSDs: {[f"{d:.4f}" for d in pl_pair_jsds]}')
print(f'V inter-section JSDs: {[f"{d:.4f}" for d in v_pair_jsds]}')

# Test all 24 permutations of part-to-section pairing
from itertools import permutations

best_rho = -2
best_p = 1.0
best_perm = None

for perm in permutations(range(4)):
    # Reorder Voynich JSDs to match this pairing
    # perm[i] = which section corresponds to pl_parts_ordered[i]
    # Reconstruct pair indices
    reordered_v_jsds = []
    for i in range(4):
        for j in range(i + 1, 4):
            # Find the JSD between sections perm[i] and perm[j]
            si, sj = perm[i], perm[j]
            if si > sj:
                si, sj = sj, si
            # Index in the flattened upper triangle
            idx = 0
            for a in range(4):
                for b in range(a + 1, 4):
                    if a == si and b == sj:
                        break
                    idx += 1
                else:
                    continue
                break
            reordered_v_jsds.append(v_pair_jsds[idx])

    rho, p = stats.spearmanr(pl_pair_jsds, reordered_v_jsds)
    if p < best_p:
        best_p = p
        best_rho = rho
        best_perm = perm

perm_labels = [v_sections[p] for p in best_perm]
print(f'\nBest pairing: {list(zip(pl_parts_ordered, perm_labels))}')
print(f'Best Spearman rho={best_rho:.4f}, p={best_p:.4f}')
print(f'(Testing all 24 permutations; reporting minimum p-value)')

# Apply Bonferroni correction for 24 tests
n1_p_corrected = min(best_p * 24, 1.0)
n1_rho = best_rho
n1_p = n1_p_corrected
n1_pass = n1_p > 0.10
n1_k = 6  # 6 pairwise distances

print(f'Bonferroni-corrected p = {n1_p_corrected:.4f}')
print(f'N1 RESULT: {"PASS" if n1_pass else "FAIL"} (prediction: p > 0.10)')

# ===========================================================================
# D1: DIAGNOSTIC -- FORMALIZATION BOUNDARY
# ===========================================================================

print('\n' + '=' * 70)
print('D1: DIAGNOSTIC -- FORMALIZATION BOUNDARY')
print('=' * 70)

pl_formalized = e8.get('formalized_count', 61)
pl_discretionary = e8['total_cues'] - pl_formalized
pl_form_ratio = pl_formalized / pl_discretionary if pl_discretionary > 0 else float('inf')

v_encodable = 49  # 49 instruction classes (BCSC)
v_non_encodable = 13  # 13 non-encodable types (C197)
v_form_ratio = v_encodable / v_non_encodable

print(f'Pseudo-Lull: formalized={pl_formalized}, discretionary={pl_discretionary}, ratio={pl_form_ratio:.2f}')
print(f'Voynich: encodable={v_encodable}, non-encodable={v_non_encodable}, ratio={v_form_ratio:.2f}')
print(f'Gap: Voynich ratio ({v_form_ratio:.2f}) is {v_form_ratio/pl_form_ratio:.2f}x pseudo-Lull ({pl_form_ratio:.2f})')
print(f'Interpretation: Voynich encodes proportionally more of its operational space')
print(f'  (This is consistent with a coded system being more formal than a natural-language text)')

# ===========================================================================
# VERDICT
# ===========================================================================

print('\n' + '=' * 70)
print('VERDICT')
print('=' * 70)

p_results = {
    'P1': p1_pass, 'P2': p2_pass, 'P3': p3_pass,
    'P4': p4_pass, 'P5': p5_pass
}
n_pass = sum(1 for v in p_results.values() if v)

for name, passed in p_results.items():
    print(f'  {name}: {"PASS" if passed else "FAIL"}')
print(f'  N1: {"PASS" if n1_pass else "FAIL"}')
print(f'\nPassing tests: {n_pass}/5')

# Determine verdict
if not n1_pass and n1_p < 0.05:
    verdict = 'LEVEL_CONFUSION'
elif n1_p > 0.10:
    if n_pass >= 4:
        verdict = 'MIDPROCESS_CONTROL_ALIGNMENT_CONFIRMED'
    elif n_pass == 3:
        verdict = 'PARTIAL_MIDPROCESS_ALIGNMENT'
    else:
        verdict = 'MIDPROCESS_ALIGNMENT_NOT_CONFIRMED'
else:
    # N1 ambiguous (0.05 < p < 0.10)
    if n_pass >= 4:
        verdict = 'MIDPROCESS_CONTROL_ALIGNMENT_CONFIRMED (N1 ambiguous)'
    elif n_pass == 3:
        verdict = 'PARTIAL_MIDPROCESS_ALIGNMENT (N1 ambiguous)'
    else:
        verdict = 'MIDPROCESS_ALIGNMENT_NOT_CONFIRMED (N1 ambiguous)'

print(f'\nVERDICT: {verdict}')

# ===========================================================================
# Write results JSON
# ===========================================================================

results = {
    'phase': 603,
    'predictions_hash': pred_hash,
    'verdict': verdict,
    'S1': {
        'pass': bool(s1_pass),
        'stars_r1_n': len(stars_r1_ey),
        'stars_r3_n': len(stars_r3_ey),
        'stars_r1_mean_ey': float(statistics.mean(stars_r1_ey)),
        'stars_r3_mean_ey': float(statistics.mean(stars_r3_ey)),
        'U': float(s1_stat),
        'p': float(s1_p)
    },
    'P1': {
        'pass': bool(p1_pass),
        'consequences': consequences,
        'stabilization_ratio': float(p1a_ratio),
        'abort_fraction': float(p1b_frac),
        'P1a_pass': bool(p1a_pass),
        'P1b_pass': bool(p1b_pass)
    },
    'P2': {
        'pass': bool(p2_pass),
        'pl_recovery_ratio': float(pl_recovery_ratio),
        'voynich_ey_ii_ratio': float(v_ey_ii_ratio),
        'mean_ey_rate': float(mean_ey),
        'mean_ii_rate': float(mean_ii),
        'part_correction_density': {k: float(v) for k, v in part_corr_density.items()},
        'section_safety_balance': {
            sec: float(statistics.mean(vals))
            for sec, vals in section_safety.items() if vals
        }
    },
    'P3': {
        'pass': bool(p3_pass),
        'pl_threshold': pl_threshold,
        'pl_count': pl_count,
        'pl_ratio': float(pl_ratio) if pl_ratio != float('inf') else 'inf',
        'brunschwig_threshold': brun_threshold_count,
        'brunschwig_count': brun_count_count,
        'brunschwig_total_termination': brun_total_termination,
        'brunschwig_ratio': float(brun_ratio) if brun_ratio != float('inf') else 'inf',
        'gap_multiplier': float(gap) if gap != float('inf') and not math.isnan(gap) else str(gap),
        'monostate_diagnostic': {
            sec: float(statistics.mean(vals))
            for sec, vals in section_axm.items() if vals
        }
    },
    'P4': {
        'pass': bool(p4_pass),
        'pl_failure_modes': n_failure_modes,
        'pl_correction_strategies': n_correction_strategies,
        'pl_convergence_ratio': float(p4a_ratio),
        'voynich_hazard_cv': float(hazard_cv),
        'voynich_recovery_cv': float(recovery_cv),
        'P4a_pass': bool(p4a_pass),
        'P4b_pass': bool(p4b_pass),
        'part_correction_density_cv': float(p4c_cv)
    },
    'P5': {
        'pass': bool(p5_pass),
        'n_families': len(all_families),
        'families': all_families,
        'part_family_presence': {
            part: sum(1 for v in vec if v > 0)
            for part, vec in part_vectors.items()
        },
        'pairwise_jsd': [
            {
                'pair': f'{parts[i]} vs {parts[j]}',
                'jsd': float(pair_jsds[idx]),
                'overlap': float(pair_overlaps[idx])
            }
            for idx, (i, j) in enumerate(
                (i, j) for i in range(len(parts)) for j in range(i + 1, len(parts))
            )
        ],
        'mean_jsd': float(mean_jsd),
        'P5a_pass': bool(p5a_pass)
    },
    'N1': {
        'pass': bool(n1_pass),
        'rho': float(n1_rho),
        'p_corrected': float(n1_p),
        'p_raw': float(best_p),
        'n_permutations_tested': 24,
        'best_pairing': list(zip(pl_parts_ordered, perm_labels)),
        'k_distances': n1_k,
        'pl_pair_jsds': [float(d) for d in pl_pair_jsds],
        'v_pair_jsds': [float(d) for d in v_pair_jsds]
    },
    'D1': {
        'pl_formalized': pl_formalized,
        'pl_discretionary': pl_discretionary,
        'pl_ratio': float(pl_form_ratio),
        'voynich_encodable': v_encodable,
        'voynich_non_encodable': v_non_encodable,
        'voynich_ratio': float(v_form_ratio)
    },
    'summary': {
        'n_passing': n_pass,
        'tests': {name: 'PASS' if passed else 'FAIL' for name, passed in p_results.items()},
        'n1': 'PASS' if n1_pass else 'FAIL'
    }
}

# Custom encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

output_path = PHASE_DIR / 'results' / 'pseudo_lull_alignment_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f'\nResults written to: {output_path}')
print(f'JSON size: {output_path.stat().st_size:,} bytes')
