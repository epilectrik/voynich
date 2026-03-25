"""
Phase 627, Script 1: PL Channel Features at Per-Chapter Subtype Resolution.

Re-extracts pseudo-Lull Testamentum features at per-chapter subtype resolution.
Phase 602 JSON only has global aggregate counts per chapter. This script applies
the EXACT same regex patterns from Phase 602 within each chapter's
en_line_start..en_line_end range to produce per-chapter subtype distributions.

Input:
  - sources/pseudo_lull_testamentum/testamentum_complete_english.txt
  - phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json

Output:
  - phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/pl_channel_features.json
"""

import sys
import time
import json
import re
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared_627 import (
    PROJECT_ROOT, RESULTS_DIR, HEAT_MODES, HEAT_INTENSITY,
    round_floats, euclidean_dist, pairwise_upper_triangle,
    load_pl_structural_profile, load_pl_english_lines,
)

t0 = time.time()
print("=" * 60)
print("Phase 627, Script 1: PL Channel Features")
print("=" * 60)

# ============================================================
# Load data
# ============================================================

profile = load_pl_structural_profile()
chapters = profile['E1_chapters']
en_lines = load_pl_english_lines()

print(f"Loaded {len(chapters)} chapters, {len(en_lines)} English lines")

# ============================================================
# T1: Per-chapter heat mode distribution
# ============================================================

print("\n--- T1: Heat mode distribution ---")

HEAT_EN = re.compile(
    r'\b(fire|heat\w*|degree|gentle|strong|moderate|fierce|slow|'
    r'balneum|bath|bain-marie|water\s+bath|ashes?|ash\s+(?:fire|bed)|'
    r'sand|sand\s+bath|athanor|furnace|dung|horse\s+dung|quicklime|'
    r'cinericium|cupel|crucible|tripod|oven|charcoal|'
    r'digestion\s+[A-Z])\b',
    re.IGNORECASE
)

HEAT_TRANSITION = re.compile(
    r'\b(increase\s+(?:the\s+)?(?:fire|heat)|'
    r'reduce\s+(?:the\s+)?(?:fire|heat)|'
    r'decrease\s+(?:the\s+)?(?:fire|heat)|'
    r'change\s+(?:the\s+)?(?:fire|heat)|'
    r'gentle\s+fire|'
    r'strong(?:er)?\s+fire|'
    r'with\s+(?:a\s+)?(?:small|great|moderate|fierce)\s+fire|'
    r'first\s+degree|second\s+degree|third\s+degree|fourth\s+degree)\b',
    re.IGNORECASE
)

# Heat mode sub-classifiers
HEAT_MODE_PATTERNS = {
    'balneum_mariae': re.compile(r'\bbalneum|bath|bain-marie|water\s+bath\b', re.IGNORECASE),
    'ash_fire':       re.compile(r'\bash(?:es)?\s*(?:fire|bed)?\b', re.IGNORECASE),
    'sand_bath':      re.compile(r'\bsand\s*(?:bath)?\b', re.IGNORECASE),
    'athanor':        re.compile(r'\bathanor\b', re.IGNORECASE),
    'dung_fire':      re.compile(r'\bdung|horse\s+dung|quicklime\b', re.IGNORECASE),
    'gentle_fire':    re.compile(r'\bgentle\s+fire|small\s+fire|lento\b', re.IGNORECASE),
    'strong_fire':    re.compile(r'\bstrong\s+fire|great\s+fire|fierce\b', re.IGNORECASE),
    'moderate_fire':  re.compile(r'\bmoderate\s+fire\b', re.IGNORECASE),
    'open_fire':      re.compile(r'\bopen\s+fire|charcoal\b', re.IGNORECASE),
    'cupellation':    re.compile(r'\bcinericium|cupel\b', re.IGNORECASE),
    'crucible':       re.compile(r'\bcrucible\b', re.IGNORECASE),
    'tripod_of_secrets': re.compile(r'\btripod\b', re.IGNORECASE),
    'solar_heat':     (re.compile(r'\bsun\b', re.IGNORECASE),
                       re.compile(r'\bheat|warm|expose\b', re.IGNORECASE)),
}

def classify_heat_modes(line: str) -> list:
    """Classify heat modes present in a line. Returns list of mode names."""
    modes = []
    lower = line.lower()
    for mode_name, pattern in HEAT_MODE_PATTERNS.items():
        if mode_name == 'solar_heat':
            # Special case: requires both sun AND heat/warm/expose
            pat_sun, pat_heat = pattern
            if pat_sun.search(line) and pat_heat.search(line):
                modes.append(mode_name)
        elif mode_name == 'ash_fire':
            # Special case: must have 'ash' in line
            if 'ash' in lower and pattern.search(line):
                modes.append(mode_name)
        else:
            if pattern.search(line):
                modes.append(mode_name)
    return modes


t1_per_chapter = []
t1_global_heat = 0
t1_global_modes_found = set()

for ch_idx, ch in enumerate(chapters):
    start = ch['en_line_start']
    end = ch['en_line_end']
    mode_counts = defaultdict(int)
    transition_count = 0
    total_heat = 0

    for line_idx in range(start, end):
        if line_idx >= len(en_lines):
            break
        line = en_lines[line_idx]

        if HEAT_EN.search(line):
            total_heat += 1
            modes = classify_heat_modes(line)
            for m in modes:
                mode_counts[m] += 1

        if HEAT_TRANSITION.search(line):
            transition_count += 1

    # Determine dominant mode
    mode_counts_dict = dict(mode_counts)
    dominant_mode = max(mode_counts_dict, key=mode_counts_dict.get) if mode_counts_dict else None

    # Mean heat intensity (weighted by mode counts)
    intensity_sum = 0
    intensity_n = 0
    for m, c in mode_counts_dict.items():
        if m in HEAT_INTENSITY:
            intensity_sum += HEAT_INTENSITY[m] * c
            intensity_n += c
    mean_intensity = intensity_sum / intensity_n if intensity_n > 0 else 0.0

    t1_global_heat += total_heat
    t1_global_modes_found.update(mode_counts_dict.keys())

    t1_per_chapter.append({
        'chapter_idx': ch_idx,
        'chapter_number': ch['number'],
        'family': ch['primary_family'],
        'mode_counts': mode_counts_dict,
        'dominant_mode': dominant_mode,
        'mean_intensity': mean_intensity,
        'transition_count': transition_count,
        'total_heat': total_heat,
    })

print(f"  Total heat lines: {t1_global_heat}, distinct modes: {len(t1_global_modes_found)}")

# ============================================================
# T2: Per-chapter monitoring subtype distribution
# ============================================================

print("\n--- T2: Monitoring subtype distribution ---")

COLOR_EN = re.compile(
    r'\b(blackness|blackened|whiteness|whitened|redness|reddened|'
    r'nigredo|albedo|rubedo|citrin\w*|snow-white|charcoal|'
    r'scarlet)\b', re.IGNORECASE
)
COLOR_ADJ_EN = re.compile(
    r'\b(black|white|red|yellow|golden|pale|dark)\b(?=.*\b(?:color|appear|become|turn|sign|see))',
    re.IGNORECASE
)
CONSIST_EN = re.compile(
    r'\b(powder|powdery|pulverized|paste|wax-like|waxy|fusible|'
    r'fuse[ds]?|fusion|flow\w*|liquid|liquefied|crystallin\w*|'
    r'solid\w*|hardened|calx|earthy|oily|unctuous|'
    r'slimy|gummy|foliated)\b', re.IGNORECASE
)
VOLAT_EN = re.compile(
    r'\b(vapor\w*|fume[ds]?|smoke|smoking|volatile|volatilized|'
    r'sublimate[ds]?|flight|fleeing|ascending|rising|evaporate\w*)\b',
    re.IGNORECASE
)

t2_per_chapter = []
t2_global_monitoring = 0

for ch_idx, ch in enumerate(chapters):
    start = ch['en_line_start']
    end = ch['en_line_end']
    color_count = 0
    consistency_count = 0
    volatility_count = 0
    chain_count = 0

    for line_idx in range(start, end):
        if line_idx >= len(en_lines):
            break
        line = en_lines[line_idx]

        has_color = bool(COLOR_EN.search(line) or COLOR_ADJ_EN.search(line))
        has_consist = bool(CONSIST_EN.search(line))
        has_volat = bool(VOLAT_EN.search(line))

        types_present = sum([has_color, has_consist, has_volat])
        if has_color:
            color_count += 1
        if has_consist:
            consistency_count += 1
        if has_volat:
            volatility_count += 1
        if types_present >= 2:
            chain_count += 1

    total_monitoring = color_count + consistency_count + volatility_count
    t2_global_monitoring += total_monitoring

    t2_per_chapter.append({
        'chapter_idx': ch_idx,
        'chapter_number': ch['number'],
        'family': ch['primary_family'],
        'color_count': color_count,
        'consistency_count': consistency_count,
        'volatility_count': volatility_count,
        'total_monitoring': total_monitoring,
        'chain_count': chain_count,
    })

print(f"  Total monitoring: {t2_global_monitoring}")

# ============================================================
# T3: Per-chapter termination subtype distribution
# ============================================================

print("\n--- T3: Termination subtype distribution ---")

TERM_EN = re.compile(
    r'\b(until|repeat\w*|reiterat\w*|as many times|so often|'
    r'continue\s+(?:this|the)|iterate\w*)\b', re.IGNORECASE
)
COUNT_RE = re.compile(
    r'\b(one|two|three|four|five|six|seven|eight|nine|ten|'
    r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
    r'eighteen|nineteen|twenty|thirty|forty|fifty|hundred|'
    r'thousand|\d+)\s*(?:times|distillat|sublim|iter|repetit)',
    re.IGNORECASE
)
TIME_RE = re.compile(
    r'\b(?:for|per)\s+(?:one|two|three|four|five|six|seven|eight|'
    r'nine|ten|eleven|twelve|\d+)\s*(?:day|night|hour|month|year|week)',
    re.IGNORECASE
)
QUALITY_RE = re.compile(
    r'\b(?:until\s+it\s+(?:resists?|withstands?|flows?|passes?|endures?)|'
    r'until\s+it\s+(?:becomes?\s+(?:fusible|fixed|white|red|black))|'
    r'until\s+(?:the|it)\s+(?:volatile|mercury)\s+is\s+(?:fixed|entirely))',
    re.IGNORECASE
)
EXT_JUDGED_RE = re.compile(
    r'\b(you\s+(?:judge|wish|desire)|as\s+(?:seems?|suffic))\b',
    re.IGNORECASE
)

def classify_termination(line: str) -> str:
    """Classify a termination line into its subtype."""
    if COUNT_RE.search(line):
        return 'count_based'
    if TIME_RE.search(line):
        return 'time_dependent'
    if QUALITY_RE.search(line):
        return 'quality_gated'
    if EXT_JUDGED_RE.search(line):
        return 'externally_judged'
    return 'threshold_based'


t3_per_chapter = []
t3_global_termination = 0

for ch_idx, ch in enumerate(chapters):
    start = ch['en_line_start']
    end = ch['en_line_end']
    counts = defaultdict(int)
    total_termination = 0

    for line_idx in range(start, end):
        if line_idx >= len(en_lines):
            break
        line = en_lines[line_idx]

        if TERM_EN.search(line):
            total_termination += 1
            term_type = classify_termination(line)
            counts[term_type] += 1

    threshold_count = counts.get('threshold_based', 0)
    threshold_frac = threshold_count / total_termination if total_termination > 0 else 0.0

    t3_global_termination += total_termination

    t3_per_chapter.append({
        'chapter_idx': ch_idx,
        'chapter_number': ch['number'],
        'family': ch['primary_family'],
        'threshold_count': threshold_count,
        'count_based_count': counts.get('count_based', 0),
        'time_based_count': counts.get('time_dependent', 0),
        'quality_gated_count': counts.get('quality_gated', 0),
        'externally_judged_count': counts.get('externally_judged', 0),
        'total_termination': total_termination,
        'threshold_frac': threshold_frac,
    })

print(f"  Total termination: {t3_global_termination}")

# ============================================================
# T4: Per-chapter correction subtype distribution
# ============================================================

print("\n--- T4: Correction subtype distribution ---")

CORRECT_EN = re.compile(
    r'\b(error|errors?|erring|correct\w*|defect\w*|trouble|'
    r'fail\w*|beware\s+lest|wrong|mistaken|sophisticat\w*|'
    r'deceiv\w*|ruin\w*|burn\w*|combust\w*|start\s+over|'
    r'begin\s+again|lost|irrecoverable)\b', re.IGNORECASE
)

FAIL_PATTERNS = {
    'process_drift':     re.compile(r'\bcolor|black|white|red|premature\b', re.IGNORECASE),
    'apparatus_failure': re.compile(r'\bvessel|seal|break|crack\b', re.IGNORECASE),
    'operator_error':    re.compile(r'\btoo\s+much\s+(?:fire|heat)|opened?\s+too\s+(?:early|soon)\b', re.IGNORECASE),
    'irrecoverable':     re.compile(r'\bstart\s+over|begin\s+again|irrecoverable|lost|cannot\b', re.IGNORECASE),
    'combustion':        re.compile(r'\bburn|combust\b', re.IGNORECASE),
}

def classify_failure_source(line: str) -> str:
    """Classify a correction line's failure source."""
    # Check in priority order
    for source in ['process_drift', 'apparatus_failure', 'operator_error',
                   'irrecoverable', 'combustion']:
        if FAIL_PATTERNS[source].search(line):
            return source
    return 'unspecified'


t4_per_chapter = []
t4_global_correction = 0

for ch_idx, ch in enumerate(chapters):
    start = ch['en_line_start']
    end = ch['en_line_end']
    counts = defaultdict(int)
    total_correction = 0

    for line_idx in range(start, end):
        if line_idx >= len(en_lines):
            break
        line = en_lines[line_idx]

        if CORRECT_EN.search(line):
            total_correction += 1
            source = classify_failure_source(line)
            counts[source] += 1

    recoverable = total_correction - counts.get('irrecoverable', 0)
    recoverable_frac = recoverable / total_correction if total_correction > 0 else 0.0

    t4_global_correction += total_correction

    t4_per_chapter.append({
        'chapter_idx': ch_idx,
        'chapter_number': ch['number'],
        'family': ch['primary_family'],
        'process_drift_count': counts.get('process_drift', 0),
        'combustion_count': counts.get('combustion', 0),
        'irrecoverable_count': counts.get('irrecoverable', 0),
        'apparatus_failure_count': counts.get('apparatus_failure', 0),
        'operator_error_count': counts.get('operator_error', 0),
        'unspecified_count': counts.get('unspecified', 0),
        'total_correction': total_correction,
        'recoverable_frac': recoverable_frac,
    })

print(f"  Total correction: {t4_global_correction}")

# ============================================================
# T5: Per-chapter channel signature vector
# ============================================================

print("\n--- T5: Channel signature vectors ---")

t5_per_chapter = []

for ch_idx, ch in enumerate(chapters):
    n_lines = ch['en_line_end'] - ch['en_line_start']
    if n_lines <= 0:
        n_lines = 1  # avoid division by zero

    t1 = t1_per_chapter[ch_idx]
    t2 = t2_per_chapter[ch_idx]
    t3 = t3_per_chapter[ch_idx]
    t4 = t4_per_chapter[ch_idx]

    # k-channel (heat/thermal)
    k_channel = {
        'heat_rate': t1['total_heat'] / n_lines,
        'mean_heat_intensity': t1['mean_intensity'],
        'heat_transition_rate': t1['transition_count'] / n_lines,
    }

    # e-channel (correction/error)
    e_channel = {
        'correction_rate': t4['total_correction'] / n_lines,
        'recoverable_frac': t4['recoverable_frac'],
        'process_drift_frac': t4['process_drift_count'] / max(t4['total_correction'], 1),
    }

    # h-channel (monitoring/observation)
    h_channel = {
        'monitoring_rate': t2['total_monitoring'] / n_lines,
        'color_frac': t2['color_count'] / max(t2['total_monitoring'], 1),
        'consistency_frac': t2['consistency_count'] / max(t2['total_monitoring'], 1),
        'volatility_frac': t2['volatility_count'] / max(t2['total_monitoring'], 1),
        'chain_rate': t2['chain_count'] / n_lines,
    }

    # t-channel (termination)
    t_channel = {
        'termination_rate': t3['total_termination'] / n_lines,
        'threshold_frac': t3['threshold_frac'],
    }

    t5_per_chapter.append({
        'chapter_idx': ch_idx,
        'chapter_number': ch['number'],
        'family': ch['primary_family'],
        'n_lines': n_lines,
        'k_channel': k_channel,
        'e_channel': e_channel,
        'h_channel': h_channel,
        't_channel': t_channel,
    })

print(f"  Computed channel signatures for {len(t5_per_chapter)} chapters")

# ============================================================
# T6: Per-family aggregation
# ============================================================

print("\n--- T6: Per-family aggregation ---")

# Identify operational chapters (non-theoretical families)
OPERATIONAL_FAMILIES = set()
for ch_idx, ch in enumerate(chapters):
    fam = ch['primary_family']
    if fam and fam != 'theoretical':
        OPERATIONAL_FAMILIES.add(fam)

print(f"  Operational families: {sorted(OPERATIONAL_FAMILIES)}")

# Group operational chapters by family
family_chapters = defaultdict(list)
for ch_idx, ch in enumerate(chapters):
    fam = ch['primary_family']
    if fam in OPERATIONAL_FAMILIES:
        family_chapters[fam].append(ch_idx)


def get_6d_vector(ch_idx: int) -> list:
    """Extract 6D feature vector for distance computation."""
    sig = t5_per_chapter[ch_idx]
    return [
        sig['k_channel']['heat_rate'],
        sig['h_channel']['monitoring_rate'],
        sig['e_channel']['correction_rate'],
        sig['t_channel']['termination_rate'],
        sig['h_channel']['chain_rate'],
        sig['k_channel']['mean_heat_intensity'],
    ]


def mean_signature(ch_indices: list) -> dict:
    """Compute mean channel signature across chapters."""
    k_keys = ['heat_rate', 'mean_heat_intensity', 'heat_transition_rate']
    e_keys = ['correction_rate', 'recoverable_frac', 'process_drift_frac']
    h_keys = ['monitoring_rate', 'color_frac', 'consistency_frac', 'volatility_frac', 'chain_rate']
    t_keys = ['termination_rate', 'threshold_frac']

    n = len(ch_indices)
    if n == 0:
        return {}

    result = {'k_channel': {}, 'e_channel': {}, 'h_channel': {}, 't_channel': {}}

    for key in k_keys:
        vals = [t5_per_chapter[i]['k_channel'][key] for i in ch_indices]
        result['k_channel'][key] = sum(vals) / n

    for key in e_keys:
        vals = [t5_per_chapter[i]['e_channel'][key] for i in ch_indices]
        result['e_channel'][key] = sum(vals) / n

    for key in h_keys:
        vals = [t5_per_chapter[i]['h_channel'][key] for i in ch_indices]
        result['h_channel'][key] = sum(vals) / n

    for key in t_keys:
        vals = [t5_per_chapter[i]['t_channel'][key] for i in ch_indices]
        result['t_channel'][key] = sum(vals) / n

    return result


t6_families = {}
for fam, ch_indices in sorted(family_chapters.items()):
    # Mean signature
    mean_sig = mean_signature(ch_indices)

    # Within-family pairwise Euclidean distances (upper triangle)
    vectors = [get_6d_vector(i) for i in ch_indices]
    within_distances = pairwise_upper_triangle(vectors, euclidean_dist)

    t6_families[fam] = {
        'n_chapters': len(ch_indices),
        'mean_signature': mean_sig,
        'chapter_indices': ch_indices,
        'within_family_distances': within_distances,
    }
    print(f"  {fam}: {len(ch_indices)} chapters, "
          f"{len(within_distances)} pairwise distances")

# ============================================================
# T7: Validation against Phase 602 global totals
# ============================================================

print("\n--- T7: Validation against Phase 602 ---")

# Phase 602 global totals (from E3-E6 sections)
p602_heat_total = profile['E5_heat_regimes']['total_passages']
p602_monitoring_total = profile['E3_monitoring']['total_passages']
p602_termination_total = profile['E4_termination']['total_conditions']
p602_correction_total = profile['E6_corrections']['total_passages']

# Also cross-check per-chapter sums from Phase 602
p602_heat_sum = sum(ch.get('heat_count', 0) for ch in chapters)
p602_monitoring_sum = sum(ch.get('monitoring_count', 0) for ch in chapters)
p602_termination_sum = sum(ch.get('termination_count', 0) for ch in chapters)
p602_correction_sum = sum(ch.get('correction_count', 0) for ch in chapters)

discrepancies = []

def check_match(name: str, our_total: int, p602_global: int, p602_sum: int) -> bool:
    """Check if our total matches Phase 602 within 5% tolerance."""
    # Report against both the global summary and the per-chapter sum
    threshold_global = max(1, int(p602_global * 0.05))
    threshold_sum = max(1, int(p602_sum * 0.05)) if p602_sum > 0 else 1

    match_global = abs(our_total - p602_global) <= threshold_global
    match_sum = abs(our_total - p602_sum) <= threshold_sum

    print(f"  {name}: ours={our_total}, P602_global={p602_global}, "
          f"P602_chapter_sum={p602_sum}")

    if not match_global:
        diff_pct = abs(our_total - p602_global) / max(p602_global, 1) * 100
        discrepancies.append({
            'channel': name,
            'our_total': our_total,
            'p602_global': p602_global,
            'p602_chapter_sum': p602_sum,
            'diff_pct_vs_global': round(diff_pct, 1),
            'note': ('Expected: same regex on same lines may differ from '
                     'P602 which may have used slightly different line ranges '
                     'or additional logic'),
        })
        print(f"    DISCREPANCY vs global: {diff_pct:.1f}%")
    else:
        print(f"    OK vs global (within 5%)")

    if not match_sum:
        diff_pct_sum = abs(our_total - p602_sum) / max(p602_sum, 1) * 100
        print(f"    DISCREPANCY vs chapter_sum: {diff_pct_sum:.1f}%")

    return match_global


heat_match = check_match('heat', t1_global_heat, p602_heat_total, p602_heat_sum)
monitoring_match = check_match('monitoring', t2_global_monitoring,
                               p602_monitoring_total, p602_monitoring_sum)
termination_match = check_match('termination', t3_global_termination,
                                p602_termination_total, p602_termination_sum)
correction_match = check_match('correction', t4_global_correction,
                               p602_correction_total, p602_correction_sum)

# ============================================================
# Assemble output
# ============================================================

elapsed = time.time() - t0

result = {
    'metadata': {
        'phase': 627,
        'script': 1,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'n_chapters': len(chapters),
        'elapsed_s': elapsed,
    },
    'T1_heat_modes': {
        'per_chapter': t1_per_chapter,
        'global_summary': {
            'total_heat': t1_global_heat,
            'modes_found': len(t1_global_modes_found),
        },
    },
    'T2_monitoring': {
        'per_chapter': t2_per_chapter,
        'global_summary': {
            'total_monitoring': t2_global_monitoring,
        },
    },
    'T3_termination': {
        'per_chapter': t3_per_chapter,
        'global_summary': {
            'total_termination': t3_global_termination,
        },
    },
    'T4_correction': {
        'per_chapter': t4_per_chapter,
        'global_summary': {
            'total_correction': t4_global_correction,
        },
    },
    'T5_channel_signatures': {
        'per_chapter': t5_per_chapter,
    },
    'T6_family_aggregation': {
        'families': t6_families,
    },
    'T7_validation': {
        'heat_match': heat_match,
        'monitoring_match': monitoring_match,
        'termination_match': termination_match,
        'correction_match': correction_match,
        'discrepancies': discrepancies,
    },
}

# Round all floats and write
result = round_floats(result)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
out_path = RESULTS_DIR / 'pl_channel_features.json'
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n{'=' * 60}")
print(f"Output: {out_path}")
print(f"Elapsed: {elapsed:.2f}s")
print(f"Chapters: {len(chapters)}")
print(f"Operational families: {len(t6_families)}")
print(f"Discrepancies: {len(discrepancies)}")
print(f"{'=' * 60}")
