#!/usr/bin/env python3
"""
Test 15: Paragraph-by-Paragraph Material Tracking on Selected Folios

Question: Can we track material identity through a folio by reading its
paragraphs sequentially?

Method:
1. Select 6 B folios with 4+ paragraphs, one from each section if possible.
2. Decode each using BFolioDecoder in structural + interpretive modes.
3. Extract per-paragraph MIDDLE vocabulary.
4. Identify paragraph-specific vs folio-wide MIDDLEs.
5. Check for folio-persistent rare MIDDLEs (potential material markers).
6. Look for paragraph-initial MIDDLEs that don't recur (material introduction).
7. Produce per-folio narrative material reading.

Pass: 3+ folios show consistent material-tracking signals.
Fail: All vocabulary shifts are operational, not material.
"""

import sys
import json
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology, BFolioDecoder

# ============================================================
# CONSTANTS
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / 'paragraph_material_tracking.json'

# Target folios: one per section where possible, 4+ paragraphs
TARGET_FOLIOS = ['f78r', 'f103r', 'f39r', 'f86v3', 'f66r', 'f107r']

# ============================================================
# STEP 0: Build global MIDDLE frequency for rarity analysis
# ============================================================
print("Building global MIDDLE frequency table...")
tx = Transcript()
morph = Morphology()

# Compute: which folios does each MIDDLE appear in?
middle_folio_sets = defaultdict(set)
middle_global_count = Counter()

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m.middle:
        middle_folio_sets[m.middle].add(t.folio)
        middle_global_count[m.middle] += 1

total_b_folios = len(set(t.folio for t in tx.currier_b()))
print(f"Total B folios: {total_b_folios}")
print(f"Unique MIDDLEs: {len(middle_global_count)}")

# Rare = appears in <15 folios; Common = appears in 40+ folios
RARE_THRESHOLD = 15
COMMON_THRESHOLD = 40

rare_middles = {m for m, fs in middle_folio_sets.items() if len(fs) < RARE_THRESHOLD}
common_middles = {m for m, fs in middle_folio_sets.items() if len(fs) >= COMMON_THRESHOLD}
print(f"Rare MIDDLEs (<{RARE_THRESHOLD} folios): {len(rare_middles)}")
print(f"Common MIDDLEs (>={COMMON_THRESHOLD} folios): {len(common_middles)}")

# ============================================================
# STEP 1: Initialize decoder (expensive, do once)
# ============================================================
print("\nInitializing BFolioDecoder...")
decoder = BFolioDecoder()

# ============================================================
# STEP 2: Check available folios and select ones with 4+ paragraphs
# ============================================================
print("\nChecking target folios for paragraph count...")

# First check which target folios exist and have enough paragraphs
available_folios = []
folio_sections = {}
for t in tx.currier_b():
    if t.folio not in folio_sections:
        folio_sections[t.folio] = t.section

for folio in TARGET_FOLIOS:
    paras = decoder.analyze_folio_paragraphs(folio)
    section = folio_sections.get(folio, '?')
    print(f"  {folio} (section {section}): {len(paras)} paragraphs")
    if len(paras) >= 3:  # Relax to 3+ if needed
        available_folios.append(folio)

# If we don't have 6, find replacements
if len(available_folios) < 6:
    print(f"\nOnly {len(available_folios)} target folios have 3+ paragraphs. Searching for replacements...")
    sections_covered = {folio_sections.get(f, '?') for f in available_folios}

    # Check all B folios for those with 4+ paragraphs
    all_b_folios = sorted(set(t.folio for t in tx.currier_b()))
    for folio in all_b_folios:
        if folio in available_folios:
            continue
        section = folio_sections.get(folio, '?')
        paras = decoder.analyze_folio_paragraphs(folio)
        if len(paras) >= 4:
            if section not in sections_covered or len(available_folios) < 6:
                available_folios.append(folio)
                sections_covered.add(section)
                print(f"  Added {folio} (section {section}): {len(paras)} paragraphs")
                if len(available_folios) >= 6:
                    break

print(f"\nFinal folio set ({len(available_folios)}):")
for f in available_folios:
    print(f"  {f} (section {folio_sections.get(f, '?')})")

# ============================================================
# STEP 3: Full analysis per folio
# ============================================================
folio_results = {}

for folio in available_folios:
    print(f"\n{'='*70}")
    print(f"FOLIO: {folio} (section {folio_sections.get(folio, '?')})")
    print(f"{'='*70}")

    # --- Decode in both modes ---
    para_structural = decoder.decode_folio_paragraphs(folio, mode='structural')
    para_interpretive = decoder.decode_folio_paragraphs(folio, mode='interpretive')
    lines_structural = decoder.decode_folio_lines(folio, mode='structural')
    lines_interpretive = decoder.decode_folio_lines(folio, mode='interpretive')

    print("\n--- STRUCTURAL (paragraphs) ---")
    print(para_structural)
    print("\n--- INTERPRETIVE (paragraphs) ---")
    print(para_interpretive)
    print("\n--- STRUCTURAL (lines, first 20) ---")
    for line in lines_structural.split('\n')[:40]:
        print(line)
    print("\n--- INTERPRETIVE (lines, first 20) ---")
    for line in lines_interpretive.split('\n')[:40]:
        print(line)

    # --- Extract per-paragraph MIDDLE vocabulary ---
    para_analyses = decoder.analyze_folio_paragraphs(folio)

    paragraph_middles = {}   # para_id -> set of MIDDLEs
    paragraph_tokens = {}    # para_id -> list of (word, middle)
    paragraph_initial_middles = {}  # para_id -> MIDDLEs from first 3 tokens

    for pa in para_analyses:
        mid_set = set()
        token_list = []
        init_middles = set()

        token_count = 0
        for la in pa.lines:
            for bt in la.tokens:
                mid = bt.morph.middle
                if mid:
                    mid_set.add(mid)
                    token_list.append((bt.word, mid))
                    if token_count < 3:
                        init_middles.add(mid)
                    token_count += 1

        paragraph_middles[pa.paragraph_id] = mid_set
        paragraph_tokens[pa.paragraph_id] = token_list
        paragraph_initial_middles[pa.paragraph_id] = init_middles

    # --- Compute folio-wide vs paragraph-specific MIDDLEs ---
    all_para_ids = list(paragraph_middles.keys())
    folio_wide_middles = set()
    if len(all_para_ids) >= 2:
        # MIDDLEs that appear in ALL paragraphs
        folio_wide_middles = set.intersection(*paragraph_middles.values()) if paragraph_middles.values() else set()

    para_specific_middles = {}
    for pid, mids in paragraph_middles.items():
        other_mids = set()
        for other_pid, other_mset in paragraph_middles.items():
            if other_pid != pid:
                other_mids |= other_mset
        para_specific_middles[pid] = mids - other_mids

    # --- Identify folio-persistent rare MIDDLEs (potential material markers) ---
    folio_persistent_rare = set()
    for mid in folio_wide_middles:
        if mid in rare_middles:
            folio_persistent_rare.add(mid)

    # Also check: MIDDLEs in majority (>60%) of paragraphs that are rare
    majority_persistent_rare = set()
    n_paras = len(all_para_ids)
    for mid in set().union(*paragraph_middles.values()):
        para_count = sum(1 for pid in all_para_ids if mid in paragraph_middles[pid])
        if para_count >= n_paras * 0.6 and mid in rare_middles:
            majority_persistent_rare.add(mid)

    # --- Paragraph-initial MIDDLEs that don't recur later ---
    intro_only_middles = {}
    for pid in all_para_ids:
        init_mids = paragraph_initial_middles[pid]
        later_mids = set()
        token_idx = 0
        for la in [la for pa in para_analyses if pa.paragraph_id == pid for la in pa.lines]:
            for bt in la.tokens:
                if bt.morph.middle and token_idx >= 3:
                    later_mids.add(bt.morph.middle)
                token_idx += 1
        intro_only = init_mids - later_mids
        intro_only_middles[pid] = intro_only

    # --- Pairwise Jaccard similarity between paragraphs ---
    jaccard_pairs = {}
    for i, pid1 in enumerate(all_para_ids):
        for pid2 in all_para_ids[i+1:]:
            s1, s2 = paragraph_middles[pid1], paragraph_middles[pid2]
            if s1 | s2:
                jacc = len(s1 & s2) / len(s1 | s2)
            else:
                jacc = 0.0
            jaccard_pairs[f"{pid1}-{pid2}"] = round(jacc, 3)

    # --- Material markers per paragraph ---
    para_material_markers = {}
    for pa in para_analyses:
        markers = Counter()
        for la in pa.lines:
            for bt in la.tokens:
                for mm in bt.material_markers:
                    markers[mm] += 1
                for om in bt.output_markers:
                    markers[om] += 1
        para_material_markers[pa.paragraph_id] = dict(markers)

    # --- Kernel balance per paragraph ---
    para_kernels = {}
    for pa in para_analyses:
        para_kernels[pa.paragraph_id] = {
            'kernel_balance': pa.kernel_balance,
            'kernel_dist': pa.kernel_dist,
            'fl_trend': pa.fl_trend,
        }

    # --- Print detailed vocabulary analysis ---
    print(f"\n--- MIDDLE VOCABULARY ANALYSIS ---")
    print(f"Folio-wide MIDDLEs (in ALL {n_paras} paragraphs): {sorted(folio_wide_middles)}")
    print(f"  of which RARE (potential material): {sorted(folio_persistent_rare)}")
    print(f"Majority-persistent rare MIDDLEs (>60%): {sorted(majority_persistent_rare)}")

    for pid in all_para_ids:
        print(f"\n  {pid}:")
        print(f"    Total MIDDLEs: {len(paragraph_middles[pid])}")
        print(f"    Specific to this paragraph: {sorted(para_specific_middles[pid])}")
        print(f"    Initial (first 3 tokens): {sorted(paragraph_initial_middles[pid])}")
        intro = intro_only_middles[pid]
        print(f"    Intro-only (appear in first 3, not later): {sorted(intro)}")
        print(f"    Material markers: {para_material_markers.get(pid, {})}")
        print(f"    Kernel: {para_kernels.get(pid, {})}")

    print(f"\n  Pairwise Jaccard (MIDDLE overlap):")
    for pair, jacc in jaccard_pairs.items():
        print(f"    {pair}: {jacc}")

    # --- Store results ---
    folio_results[folio] = {
        'section': folio_sections.get(folio, '?'),
        'n_paragraphs': n_paras,
        'folio_wide_middles': sorted(folio_wide_middles),
        'folio_wide_count': len(folio_wide_middles),
        'folio_persistent_rare': sorted(folio_persistent_rare),
        'majority_persistent_rare': sorted(majority_persistent_rare),
        'paragraph_vocabulary': {
            pid: {
                'total_middles': len(paragraph_middles[pid]),
                'middles': sorted(paragraph_middles[pid]),
                'specific_middles': sorted(para_specific_middles[pid]),
                'initial_middles': sorted(paragraph_initial_middles[pid]),
                'intro_only_middles': sorted(intro_only_middles[pid]),
                'material_markers': para_material_markers.get(pid, {}),
                'kernel_info': para_kernels.get(pid, {}),
            }
            for pid in all_para_ids
        },
        'pairwise_jaccard': jaccard_pairs,
        'structural_decode': para_structural,
        'interpretive_decode': para_interpretive,
    }

# ============================================================
# STEP 4: Cross-folio analysis and narrative assessment
# ============================================================
print(f"\n{'='*70}")
print("CROSS-FOLIO ANALYSIS")
print(f"{'='*70}")

# Count folios with material-tracking signals
material_signal_folios = 0
narratives = {}

for folio, data in folio_results.items():
    signals = []

    # Signal 1: Folio-persistent rare MIDDLEs exist
    if len(data['folio_persistent_rare']) > 0:
        signals.append(f"Has {len(data['folio_persistent_rare'])} folio-persistent rare MIDDLEs: {data['folio_persistent_rare']}")

    # Signal 2: Majority-persistent rare MIDDLEs
    if len(data['majority_persistent_rare']) > 0:
        signals.append(f"Has {len(data['majority_persistent_rare'])} majority-persistent rare MIDDLEs: {data['majority_persistent_rare']}")

    # Signal 3: Low paragraph-specific vocabulary (material stays constant)
    avg_specific = sum(len(data['paragraph_vocabulary'][p]['specific_middles'])
                       for p in data['paragraph_vocabulary']) / max(len(data['paragraph_vocabulary']), 1)
    avg_total = sum(data['paragraph_vocabulary'][p]['total_middles']
                    for p in data['paragraph_vocabulary']) / max(len(data['paragraph_vocabulary']), 1)
    specificity_rate = avg_specific / max(avg_total, 1)

    if specificity_rate < 0.3:
        signals.append(f"Low specificity rate ({specificity_rate:.1%}): vocabulary shared across paragraphs")

    # Signal 4: Consistent material markers across paragraphs
    all_markers = [data['paragraph_vocabulary'][p]['material_markers'] for p in data['paragraph_vocabulary']]
    marker_types = set()
    for m in all_markers:
        marker_types.update(m.keys())

    consistent_markers = []
    for mt in marker_types:
        present_in = sum(1 for m in all_markers if mt in m)
        if present_in >= len(all_markers) * 0.6:
            consistent_markers.append(mt)

    if consistent_markers:
        signals.append(f"Consistent markers across paragraphs: {consistent_markers}")

    # Signal 5: Kernel balance varies (operational) but vocabulary overlaps (material constant)
    kernel_balances = [data['paragraph_vocabulary'][p]['kernel_info'].get('kernel_balance', '')
                       for p in data['paragraph_vocabulary']]
    jaccards = list(data['pairwise_jaccard'].values())
    avg_jaccard = sum(jaccards) / max(len(jaccards), 1) if jaccards else 0

    kernel_variation = len(set(kernel_balances)) > 1
    if kernel_variation and avg_jaccard > 0.15:
        signals.append(f"Kernel varies ({set(kernel_balances)}) but vocabulary overlaps (avg Jaccard {avg_jaccard:.2f})")

    # Signal 6: Intro-only middles in first paragraph
    first_para = list(data['paragraph_vocabulary'].keys())[0] if data['paragraph_vocabulary'] else None
    if first_para:
        intro_only = data['paragraph_vocabulary'][first_para]['intro_only_middles']
        if len(intro_only) > 0:
            signals.append(f"P1 has intro-only MIDDLEs: {intro_only}")

    has_signal = len(signals) >= 2  # At least 2 signals
    if has_signal:
        material_signal_folios += 1

    # Build narrative
    narrative = {
        'section': data['section'],
        'n_paragraphs': data['n_paragraphs'],
        'signal_count': len(signals),
        'signals': signals,
        'has_material_signal': has_signal,
        'avg_jaccard': round(avg_jaccard, 3),
        'specificity_rate': round(specificity_rate, 3),
        'kernel_balances': kernel_balances,
        'folio_persistent_rare': data['folio_persistent_rare'],
        'majority_persistent_rare': data['majority_persistent_rare'],
    }

    # Material reading
    if data['folio_persistent_rare']:
        reading = (f"POSSIBLE SINGLE-MATERIAL: Rare MIDDLEs {data['folio_persistent_rare']} persist "
                   f"across all paragraphs, suggesting a material context that spans operational units. "
                   f"Kernel variation ({set(kernel_balances)}) indicates different processing phases of the "
                   f"same material.")
    elif data['majority_persistent_rare']:
        reading = (f"POSSIBLE MATERIAL WITH VARIATION: MIDDLEs {data['majority_persistent_rare']} "
                   f"persist in most paragraphs. Some paragraphs may introduce secondary materials.")
    elif avg_jaccard > 0.2:
        reading = (f"SHARED VOCABULARY (avg Jaccard {avg_jaccard:.2f}): High overlap suggests "
                   f"material continuity, though no single rare MIDDLE dominates. Material identity "
                   f"may be distributed across common vocabulary rather than marked by rare tokens.")
    else:
        reading = (f"INDEPENDENT PROGRAMS: Low vocabulary overlap (avg Jaccard {avg_jaccard:.2f}) "
                   f"and no persistent rare MIDDLEs. Each paragraph appears to operate on "
                   f"different material or the same material with different vocabulary focus.")

    narrative['material_reading'] = reading
    narratives[folio] = narrative

    print(f"\n{folio} ({data['section']}): {'MATERIAL SIGNAL' if has_signal else 'NO CLEAR SIGNAL'}")
    print(f"  Signals: {len(signals)}")
    for s in signals:
        print(f"    - {s}")
    print(f"  Reading: {reading}")

# ============================================================
# STEP 5: Overall verdict
# ============================================================
verdict = "PASS" if material_signal_folios >= 3 else "FAIL"
print(f"\n{'='*70}")
print(f"OVERALL VERDICT: {verdict}")
print(f"  {material_signal_folios}/{len(available_folios)} folios show material-tracking signals")
print(f"{'='*70}")

# ============================================================
# STEP 6: Save results
# ============================================================
output = {
    'test': 'Test 15: Paragraph-by-Paragraph Material Tracking',
    'question': 'Can we track material identity through a folio by reading its paragraphs sequentially?',
    'folios_analyzed': available_folios,
    'folio_sections': {f: folio_sections.get(f, '?') for f in available_folios},
    'global_stats': {
        'total_b_folios': total_b_folios,
        'unique_middles': len(middle_global_count),
        'rare_middles_count': len(rare_middles),
        'common_middles_count': len(common_middles),
    },
    'per_folio_narratives': narratives,
    'per_folio_vocabulary': {
        folio: {
            'folio_wide_middles': data['folio_wide_middles'],
            'folio_persistent_rare': data['folio_persistent_rare'],
            'majority_persistent_rare': data['majority_persistent_rare'],
            'paragraph_vocabulary': data['paragraph_vocabulary'],
            'pairwise_jaccard': data['pairwise_jaccard'],
        }
        for folio, data in folio_results.items()
    },
    'verdict': verdict,
    'material_signal_count': material_signal_folios,
    'total_folios_tested': len(available_folios),
    'pass_threshold': '3+ folios with consistent material-tracking signals',
    'methodology_notes': [
        'Paragraphs are INDEPENDENT operational units (C855), not sequential stages',
        'Material persistence is detected by MIDDLEs appearing across operationally independent paragraphs',
        'Folio-persistent rare MIDDLEs are the strongest material signal',
        'Jaccard similarity measures vocabulary overlap between paragraphs',
        'Specificity rate measures what fraction of each paragraphs vocabulary is unique to it',
    ],
}

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to {OUTPUT_PATH}")
