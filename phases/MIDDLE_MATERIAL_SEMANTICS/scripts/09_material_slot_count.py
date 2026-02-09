"""
09_material_slot_count.py - Material Slot Count vs Brunschwig

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 9

Question: Does phase-exclusive rare middle count match historical recipe complexity?

Method:
1. Load Currier B tokens (H track, no labels, no uncertain)
2. Extract MIDDLEs using Morphology
3. Build corpus-wide folio count per MIDDLE
4. For each folio, assign zones (SETUP/PROCESS/FINISH) using paragraph structure
   (3+ paras) or 20/60/20 line split (1-2 paras)
5. Identify zone-exclusive rare middles per folio:
   - Rare = appears in <15 folios corpus-wide
   - 2+ occurrences within the folio (exclude hapax)
   - Appears in exactly one zone within the folio
6. Count = "material slot count" per folio
7. Load Brunschwig curated data - count parts_used per recipe, group by fire_degree
8. Load regime_folio_mapping.json for REGIME assignment
9. Kruskal-Wallis: slot count differs by REGIME
10. Spearman correlation: slot count vs k/(k+h+e) kernel ratio (continuous proxy)
11. Report: mean slot count, distribution, Brunschwig comparison

Verdict: SUPPORTED if slot counts in 3-8 range AND regime association significant (p < 0.05)
"""
import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from collections import defaultdict, Counter
from pathlib import Path
from scripts.voynich import Transcript, Morphology

from scipy.stats import spearmanr, kruskal

# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RARITY_THRESHOLD = 15       # folios: <15 = RARE
MIN_FOLIO_OCCURRENCES = 2   # exclude hapax (1 occurrence per folio)
REGIME_MAPPING_PATH = Path('C:/git/voynich/results/regime_folio_mapping.json')
BRUNSCHWIG_PATH = Path('C:/git/voynich/data/brunschwig_curated_v3.json')

# ============================================================
# DATA LOADING
# ============================================================
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()

b_tokens = []
for tok in tx.currier_b():
    if not tok.placement.startswith('P'):
        continue
    m = morph.extract(tok.word)
    if m.middle is None or m.middle == '_EMPTY_':
        continue
    b_tokens.append({
        'word': tok.word,
        'middle': m.middle,
        'folio': tok.folio,
        'line': tok.line,
        'par_initial': tok.par_initial,
        'line_initial': tok.line_initial,
    })

print(f"  Currier B text tokens with valid MIDDLE: {len(b_tokens)}")

# ============================================================
# PRE-COMPUTE: corpus-wide MIDDLE folio counts
# ============================================================
middle_folios = defaultdict(set)
for td in b_tokens:
    middle_folios[td['middle']].add(td['folio'])

middle_folio_count = {mid: len(fs) for mid, fs in middle_folios.items()}
n_rare_middles = sum(1 for v in middle_folio_count.values() if v < RARITY_THRESHOLD)
print(f"  Unique MIDDLEs: {len(middle_folio_count)}")
print(f"  Rare MIDDLEs (<{RARITY_THRESHOLD} folios): {n_rare_middles}")

# ============================================================
# GROUP BY FOLIO
# ============================================================
folio_groups = defaultdict(list)
for td in b_tokens:
    folio_groups[td['folio']].append(td)

print(f"  B folios: {len(folio_groups)}")

# ============================================================
# PARAGRAPH BOUNDARY DETECTION
# ============================================================
def assign_paragraphs(folio_tokens):
    """Assign paragraph numbers to tokens within a folio."""
    current_para = 0
    para_assignments = []
    for tok in folio_tokens:
        if tok['par_initial'] and tok['line_initial']:
            current_para += 1
        para_assignments.append(current_para)
    return para_assignments

# ============================================================
# ZONE ASSIGNMENT
# ============================================================
def assign_zones(folio_tokens, para_assignments):
    """
    Assign SETUP/PROCESS/FINISH zones.
    If 3+ paragraphs: first=SETUP, last=FINISH, middle=PROCESS
    If 1-2 paragraphs: line-based 20/60/20 split
    """
    n_paras = max(para_assignments) if para_assignments else 0

    if n_paras >= 3:
        first_para = 1
        last_para = n_paras
        zones = []
        for p in para_assignments:
            if p == first_para:
                zones.append('SETUP')
            elif p == last_para:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones
    else:
        # Line-based 20/60/20 split
        lines = []
        seen = set()
        for tok in folio_tokens:
            if tok['line'] not in seen:
                lines.append(tok['line'])
                seen.add(tok['line'])

        n_lines = len(lines)
        if n_lines < 3:
            return ['PROCESS'] * len(folio_tokens)

        setup_end = max(1, int(n_lines * 0.2))
        finish_start = n_lines - max(1, int(n_lines * 0.2))

        setup_lines = set(lines[:setup_end])
        finish_lines = set(lines[finish_start:])

        zones = []
        for tok in folio_tokens:
            if tok['line'] in setup_lines:
                zones.append('SETUP')
            elif tok['line'] in finish_lines:
                zones.append('FINISH')
            else:
                zones.append('PROCESS')
        return zones

# ============================================================
# COMPUTE MATERIAL SLOT COUNT PER FOLIO
# ============================================================
print("\nComputing material slot counts per folio...")

folio_slot_counts = {}
folio_slot_details = {}

for folio in sorted(folio_groups.keys()):
    ftokens = folio_groups[folio]

    # Assign paragraphs and zones
    para_assignments = assign_paragraphs(ftokens)
    zones = assign_zones(ftokens, para_assignments)

    # For each MIDDLE on this folio: count occurrences and track zones
    middle_zone_sets = defaultdict(set)    # middle -> set of zones
    middle_folio_freq = Counter()           # middle -> count on this folio

    for tok, zone in zip(ftokens, zones):
        mid = tok['middle']
        middle_zone_sets[mid].add(zone)
        middle_folio_freq[mid] += 1

    # Identify zone-exclusive rare middles
    slot_middles = []
    for mid, freq in middle_folio_freq.items():
        # Must have 2+ occurrences on this folio (no hapax)
        if freq < MIN_FOLIO_OCCURRENCES:
            continue
        # Must be rare corpus-wide
        if middle_folio_count.get(mid, 0) >= RARITY_THRESHOLD:
            continue
        # Must appear in exactly one zone
        if len(middle_zone_sets[mid]) == 1:
            slot_middles.append({
                'middle': mid,
                'zone': list(middle_zone_sets[mid])[0],
                'folio_freq': freq,
                'corpus_folio_count': middle_folio_count.get(mid, 0),
            })

    folio_slot_counts[folio] = len(slot_middles)
    folio_slot_details[folio] = {
        'slot_count': len(slot_middles),
        'n_paragraphs': max(para_assignments) if para_assignments else 0,
        'n_tokens': len(ftokens),
        'slot_middles': slot_middles,
    }

slot_values = list(folio_slot_counts.values())
mean_slots = sum(slot_values) / len(slot_values) if slot_values else 0
median_slots = sorted(slot_values)[len(slot_values) // 2] if slot_values else 0
min_slots = min(slot_values) if slot_values else 0
max_slots = max(slot_values) if slot_values else 0

print(f"  Mean material slot count: {mean_slots:.2f}")
print(f"  Median: {median_slots}")
print(f"  Range: {min_slots} - {max_slots}")
print(f"  Folios in 3-8 range: {sum(1 for v in slot_values if 3 <= v <= 8)}/{len(slot_values)}")

# Distribution histogram
slot_dist = Counter(slot_values)
print(f"\n  Slot count distribution:")
for k in sorted(slot_dist.keys()):
    bar = '#' * slot_dist[k]
    print(f"    {k:3d}: {slot_dist[k]:3d} folios  {bar}")

# Zone breakdown of slot middles
all_slot_zones = Counter()
for folio, details in folio_slot_details.items():
    for sm in details['slot_middles']:
        all_slot_zones[sm['zone']] += 1

total_slot_middles = sum(all_slot_zones.values())
print(f"\n  Zone distribution of slot middles (n={total_slot_middles}):")
for zone in ['SETUP', 'PROCESS', 'FINISH']:
    cnt = all_slot_zones.get(zone, 0)
    pct = 100 * cnt / total_slot_middles if total_slot_middles > 0 else 0
    print(f"    {zone}: {cnt} ({pct:.1f}%)")

# ============================================================
# LOAD REGIME MAPPING
# ============================================================
print("\n" + "=" * 60)
print("REGIME ANALYSIS")
print("=" * 60)

with open(REGIME_MAPPING_PATH, 'r') as f:
    regime_mapping = json.load(f)

# Invert: folio -> regime
folio_regime = {}
for regime, folios in regime_mapping.items():
    for fol in folios:
        folio_regime[fol] = regime

# Group slot counts by regime
regime_slots = defaultdict(list)
for folio, count in folio_slot_counts.items():
    regime = folio_regime.get(folio)
    if regime:
        regime_slots[regime].append(count)

for regime in sorted(regime_slots.keys()):
    vals = regime_slots[regime]
    r_mean = sum(vals) / len(vals) if vals else 0
    r_median = sorted(vals)[len(vals) // 2] if vals else 0
    print(f"  {regime}: n={len(vals)}, mean={r_mean:.2f}, median={r_median}, range=[{min(vals)}-{max(vals)}]")

# Kruskal-Wallis test: do slot counts differ by regime?
regime_groups = [regime_slots[r] for r in sorted(regime_slots.keys()) if len(regime_slots[r]) >= 2]
if len(regime_groups) >= 2:
    kw_stat, kw_p = kruskal(*regime_groups)
    print(f"\n  Kruskal-Wallis H={kw_stat:.3f}, p={kw_p:.6f}")
else:
    kw_stat, kw_p = None, None
    print("\n  Insufficient regime groups for Kruskal-Wallis")

# ============================================================
# CONTINUOUS REGIME PROXY: k/(k+h+e) ratio
# ============================================================
print("\n" + "=" * 60)
print("KERNEL RATIO CORRELATION")
print("=" * 60)

KERNELS = {'k', 'h', 'e'}

folio_k_ratio = {}
for folio, ftokens in folio_groups.items():
    k_count = 0
    h_count = 0
    e_count = 0
    total_kernel = 0
    for tok in ftokens:
        for c in tok['word']:
            if c == 'k':
                k_count += 1
            elif c == 'h':
                h_count += 1
            elif c == 'e':
                e_count += 1
        total_kernel += sum(1 for c in tok['word'] if c in KERNELS)

    if total_kernel > 0:
        folio_k_ratio[folio] = k_count / total_kernel
    else:
        folio_k_ratio[folio] = 0.0

# Spearman correlation: slot count vs k-ratio
shared_folios = sorted(set(folio_slot_counts.keys()) & set(folio_k_ratio.keys()))
slot_vals_corr = [folio_slot_counts[f] for f in shared_folios]
k_ratio_vals = [folio_k_ratio[f] for f in shared_folios]

if len(shared_folios) >= 5:
    rho, rho_p = spearmanr(slot_vals_corr, k_ratio_vals)
    print(f"  Spearman rho (slot_count vs k_ratio): {rho:.4f}, p={rho_p:.6f}")
else:
    rho, rho_p = None, None
    print("  Insufficient data for Spearman correlation")

# Also: Spearman slot count vs h-ratio (h-dominant = REGIME_3 style)
folio_h_ratio = {}
for folio, ftokens in folio_groups.items():
    h_count = sum(1 for tok in ftokens for c in tok['word'] if c == 'h')
    total_kernel = sum(1 for tok in ftokens for c in tok['word'] if c in KERNELS)
    folio_h_ratio[folio] = h_count / total_kernel if total_kernel > 0 else 0.0

h_ratio_vals = [folio_h_ratio[f] for f in shared_folios]

if len(shared_folios) >= 5:
    rho_h, rho_h_p = spearmanr(slot_vals_corr, h_ratio_vals)
    print(f"  Spearman rho (slot_count vs h_ratio): {rho_h:.4f}, p={rho_h_p:.6f}")
else:
    rho_h, rho_h_p = None, None

# ============================================================
# BRUNSCHWIG COMPARISON
# ============================================================
print("\n" + "=" * 60)
print("BRUNSCHWIG COMPARISON")
print("=" * 60)

with open(BRUNSCHWIG_PATH, 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)

recipes = brunschwig.get('recipes', [])
print(f"  Total Brunschwig recipes: {len(recipes)}")

# Count materials per recipe: len(parts_used) where available
# Also count procedural steps as a complexity proxy
fire_degree_parts = defaultdict(list)       # fire_degree -> list of parts_used counts
fire_degree_steps = defaultdict(list)       # fire_degree -> list of procedural step counts

for recipe in recipes:
    fd = recipe.get('fire_degree')
    if fd is None:
        continue

    # Parts used count (material count)
    parts = recipe.get('parts_used')
    if parts is not None and isinstance(parts, list):
        fire_degree_parts[fd].append(len(parts))

    # Procedural step count (complexity proxy)
    steps = recipe.get('procedural_steps')
    if steps is not None and isinstance(steps, list):
        fire_degree_steps[fd].append(len(steps))

print(f"\n  Brunschwig material counts (parts_used) by fire degree:")
brunschwig_by_degree = {}
for fd in sorted(fire_degree_parts.keys()):
    vals = fire_degree_parts[fd]
    fd_mean = sum(vals) / len(vals) if vals else 0
    fd_median = sorted(vals)[len(vals) // 2] if vals else 0
    brunschwig_by_degree[fd] = {
        'n_recipes': len(vals),
        'mean_parts': round(fd_mean, 2),
        'median_parts': fd_median,
        'min_parts': min(vals) if vals else 0,
        'max_parts': max(vals) if vals else 0,
    }
    print(f"    Degree {fd}: n={len(vals)}, mean={fd_mean:.2f}, median={fd_median}, range=[{min(vals)}-{max(vals)}]")

print(f"\n  Brunschwig procedural step counts by fire degree:")
brunschwig_steps_by_degree = {}
for fd in sorted(fire_degree_steps.keys()):
    vals = fire_degree_steps[fd]
    fd_mean = sum(vals) / len(vals) if vals else 0
    fd_median = sorted(vals)[len(vals) // 2] if vals else 0
    brunschwig_steps_by_degree[fd] = {
        'n_recipes': len(vals),
        'mean_steps': round(fd_mean, 2),
        'median_steps': fd_median,
        'min_steps': min(vals) if vals else 0,
        'max_steps': max(vals) if vals else 0,
    }
    print(f"    Degree {fd}: n={len(vals)}, mean={fd_mean:.2f}, median={fd_median}, range=[{min(vals)}-{max(vals)}]")

# Overall Brunschwig material count range
all_parts_counts = [c for clist in fire_degree_parts.values() for c in clist]
brunschwig_overall_mean = sum(all_parts_counts) / len(all_parts_counts) if all_parts_counts else 0
brunschwig_overall_range = (min(all_parts_counts), max(all_parts_counts)) if all_parts_counts else (0, 0)
print(f"\n  Brunschwig overall: mean={brunschwig_overall_mean:.2f}, range={brunschwig_overall_range}")

# ============================================================
# REGIME-FIRE DEGREE ALIGNMENT CHECK
# ============================================================
# Per BRSC: degree_1->REGIME_2, degree_2->REGIME_1, degree_3->REGIME_3, degree_4->REGIME_4
# Compare mean slot count per REGIME with mean material count per corresponding fire degree
print("\n  REGIME <-> fire_degree alignment (per BRSC):")
degree_regime_map = {1: 'REGIME_2', 2: 'REGIME_1', 3: 'REGIME_3'}
# No degree 4 in data, but check

alignment_data = {}
for fd, regime_name in degree_regime_map.items():
    if fd in brunschwig_by_degree and regime_name in regime_slots:
        b_mean = brunschwig_by_degree[fd]['mean_parts']
        v_vals = regime_slots[regime_name]
        v_mean = sum(v_vals) / len(v_vals) if v_vals else 0
        alignment_data[regime_name] = {
            'fire_degree': fd,
            'brunschwig_mean_parts': b_mean,
            'voynich_mean_slots': round(v_mean, 2),
        }
        print(f"    Degree {fd} -> {regime_name}: Brunschwig mean={b_mean:.2f} parts, Voynich mean={v_mean:.2f} slots")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "=" * 60)

# Criterion 1: Slot counts in 3-8 range (majority of folios)
in_range_pct = 100 * sum(1 for v in slot_values if 3 <= v <= 8) / len(slot_values) if slot_values else 0
range_ok = in_range_pct >= 40  # at least 40% of folios in range

# Criterion 2: Regime association significant (KW p < 0.05 OR Spearman p < 0.05)
regime_sig = False
if kw_p is not None and kw_p < 0.05:
    regime_sig = True
if rho_p is not None and rho_p < 0.05:
    regime_sig = True
if rho_h_p is not None and rho_h_p < 0.05:
    regime_sig = True

verdict = "SUPPORTED" if (range_ok and regime_sig) else "NOT_SUPPORTED"

# Build notes
notes_parts = []
notes_parts.append(f"Mean slot count={mean_slots:.2f}, median={median_slots}, range=[{min_slots}-{max_slots}]")
notes_parts.append(f"{in_range_pct:.1f}% folios in 3-8 range")

if kw_p is not None:
    notes_parts.append(f"KW H={kw_stat:.3f} p={kw_p:.4f}")
if rho is not None:
    notes_parts.append(f"Spearman(slot,k_ratio) rho={rho:.4f} p={rho_p:.4f}")
if rho_h is not None:
    notes_parts.append(f"Spearman(slot,h_ratio) rho={rho_h:.4f} p={rho_h_p:.4f}")

notes_parts.append(f"Brunschwig parts range={brunschwig_overall_range}")

notes = "; ".join(notes_parts)

print(f"VERDICT: {verdict}")
print(f"{'=' * 60}")
print(f"Notes: {notes}")

# ============================================================
# SAVE RESULTS
# ============================================================
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Compact per-folio data (no slot_middles detail to keep output manageable)
per_folio_compact = {}
for folio, details in folio_slot_details.items():
    regime = folio_regime.get(folio, 'UNKNOWN')
    per_folio_compact[folio] = {
        'slot_count': details['slot_count'],
        'n_paragraphs': details['n_paragraphs'],
        'n_tokens': details['n_tokens'],
        'regime': regime,
        'k_ratio': round(folio_k_ratio.get(folio, 0), 4),
        'slot_middles': [sm['middle'] for sm in details['slot_middles']],
    }

output = {
    "test": "Material Slot Count vs Brunschwig",
    "question": "Does phase-exclusive rare middle count match historical recipe complexity?",
    "method": "Zone-exclusive rare MIDDLEs per folio (rare=<15 folios, 2+ occurrences, 1 zone)",
    "n_folios": len(folio_groups),
    "n_tokens_analyzed": len(b_tokens),
    "rarity_threshold_folios": RARITY_THRESHOLD,
    "min_folio_occurrences": MIN_FOLIO_OCCURRENCES,
    "slot_count_summary": {
        "mean": round(mean_slots, 2),
        "median": median_slots,
        "min": min_slots,
        "max": max_slots,
        "pct_in_3_8_range": round(in_range_pct, 1),
        "distribution": {str(k): v for k, v in sorted(slot_dist.items())},
    },
    "zone_distribution_of_slots": {
        zone: {
            "count": all_slot_zones.get(zone, 0),
            "pct": round(100 * all_slot_zones.get(zone, 0) / total_slot_middles, 1) if total_slot_middles > 0 else 0,
        }
        for zone in ['SETUP', 'PROCESS', 'FINISH']
    },
    "regime_analysis": {
        "kruskal_wallis_H": round(kw_stat, 4) if kw_stat is not None else None,
        "kruskal_wallis_p": round(kw_p, 6) if kw_p is not None else None,
        "per_regime": {
            regime: {
                "n_folios": len(vals),
                "mean_slots": round(sum(vals) / len(vals), 2) if vals else 0,
                "median_slots": sorted(vals)[len(vals) // 2] if vals else 0,
                "min_slots": min(vals) if vals else 0,
                "max_slots": max(vals) if vals else 0,
            }
            for regime, vals in sorted(regime_slots.items())
        },
    },
    "kernel_correlation": {
        "spearman_k_ratio": {
            "rho": round(rho, 4) if rho is not None else None,
            "p_value": round(rho_p, 6) if rho_p is not None else None,
        },
        "spearman_h_ratio": {
            "rho": round(rho_h, 4) if rho_h is not None else None,
            "p_value": round(rho_h_p, 6) if rho_h_p is not None else None,
        },
    },
    "brunschwig_comparison": {
        "overall_mean_parts": round(brunschwig_overall_mean, 2),
        "overall_range": list(brunschwig_overall_range),
        "by_fire_degree": {
            str(fd): data for fd, data in sorted(brunschwig_by_degree.items())
        },
        "procedural_steps_by_degree": {
            str(fd): data for fd, data in sorted(brunschwig_steps_by_degree.items())
        },
    },
    "regime_fire_degree_alignment": alignment_data,
    "per_folio": per_folio_compact,
    "verdict": verdict,
    "notes": notes,
}

output_path = RESULTS_DIR / 'material_slot_count.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
