"""
01_phase_exclusivity_corpus.py - Phase-Position Exclusivity (Corpus-Wide)

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 1: Does the f78r pattern (phase-exclusive rare vocabulary) hold across all B folios?

Method:
1. Load Currier B tokens (H transcriber, labels excluded, uncertain excluded)
2. Extract MIDDLEs via canonical Morphology
3. For each B folio, identify paragraph boundaries and assign zones:
   - SETUP (first paragraph), PROCESS (middle paragraphs), FINISH (final paragraph)
   - For folios with 1-2 paragraphs, use line-based 20/60/20 split
4. Classify each MIDDLE as zone-exclusive or SHARED
5. Compare zone-exclusive rates between RARE (<15 folios) and COMMON (>=15 folios) middles
6. Statistical test: Mann-Whitney U

Key filter: Exclude hapax middles (only 1 occurrence per folio) since they are
trivially zone-exclusive. Only count middles with 2+ occurrences per folio.
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology

# scipy for statistics
from scipy.stats import mannwhitneyu
import math


# ============================================================
# CONFIGURATION
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RARITY_THRESHOLD = 15  # folios: <15 = RARE, >=15 = COMMON
MIN_FOLIO_OCCURRENCES = 2  # exclude hapax (1 occurrence per folio)


# ============================================================
# DATA LOADING
# ============================================================
def load_b_tokens():
    """Load all Currier B tokens with line/paragraph metadata."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for tok in tx.currier_b():
        # Skip labels already handled by currier_b(), but placement-filter non-P
        # We want text tokens only (P-prefixed placements)
        if not tok.placement.startswith('P'):
            continue

        m = morph.extract(tok.word)
        if m.middle is None or m.middle == '_EMPTY_':
            continue

        tokens.append({
            'word': tok.word,
            'middle': m.middle,
            'folio': tok.folio,
            'line': tok.line,
            'par_initial': tok.par_initial,
            'line_initial': tok.line_initial,
        })

    return tokens


# ============================================================
# PARAGRAPH BOUNDARY DETECTION
# ============================================================
def assign_paragraphs(folio_tokens):
    """
    Assign paragraph numbers to tokens within a folio.

    Uses par_initial field: when par_initial is True (==1 in raw data,
    converted to bool by Token loader) AND line_initial is True, a new
    paragraph starts.

    Note: The Token dataclass loads par_initial as bool:
      row['par_initial'].strip() == '1'
    This means par_initial=True only when the raw value is '1',
    i.e., the first token of a paragraph.
    """
    # Group tokens by line to identify line-initial tokens
    # par_initial==True on a line-initial token signals paragraph start
    current_para = 0
    para_assignments = []

    for tok in folio_tokens:
        # New paragraph if this is the first token of a paragraph
        # par_initial is True when raw value == '1' (first position)
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
        # Paragraph-based zones
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
        # Get unique sorted lines
        lines = []
        seen = set()
        for tok in folio_tokens:
            if tok['line'] not in seen:
                lines.append(tok['line'])
                seen.add(tok['line'])

        n_lines = len(lines)
        if n_lines < 3:
            # Too few lines - all PROCESS
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
# MAIN ANALYSIS
# ============================================================
def main():
    print("Loading Currier B tokens...")
    all_tokens = load_b_tokens()
    print(f"  Total B text tokens with valid MIDDLE: {len(all_tokens)}")

    # Group by folio
    folio_groups = defaultdict(list)
    for tok in all_tokens:
        folio_groups[tok['folio']].append(tok)

    print(f"  B folios: {len(folio_groups)}")

    # ---- Pre-compute: corpus-wide MIDDLE folio counts ----
    middle_folios = defaultdict(set)
    for tok in all_tokens:
        middle_folios[tok['middle']].add(tok['folio'])

    middle_folio_count = {m: len(fs) for m, fs in middle_folios.items()}

    # ---- Per-folio analysis ----
    # For each folio, for each MIDDLE with 2+ occurrences:
    #   classify as zone-exclusive or SHARED
    per_folio_summary = {}

    # Collect per-middle zone-exclusivity across folios
    # Key: (middle, folio) -> is_zone_exclusive (bool)
    middle_exclusivity = []

    for folio in sorted(folio_groups.keys()):
        ftokens = folio_groups[folio]

        # Assign paragraphs
        para_assignments = assign_paragraphs(ftokens)

        # Assign zones
        zones = assign_zones(ftokens, para_assignments)

        # Count MIDDLEs per zone, and total per folio
        middle_zone_sets = defaultdict(set)  # middle -> set of zones
        middle_folio_freq = Counter()  # middle -> count on this folio

        for tok, zone in zip(ftokens, zones):
            mid = tok['middle']
            middle_zone_sets[mid].add(zone)
            middle_folio_freq[mid] += 1

        # Classify middles (2+ occurrences only)
        n_exclusive = 0
        n_shared = 0
        n_hapax_skipped = 0
        rare_exclusive = 0
        rare_total = 0
        common_exclusive = 0
        common_total = 0

        for mid, freq in middle_folio_freq.items():
            if freq < MIN_FOLIO_OCCURRENCES:
                n_hapax_skipped += 1
                continue

            zones_present = middle_zone_sets[mid]
            is_exclusive = len(zones_present) == 1
            folio_count = middle_folio_count.get(mid, 0)

            if is_exclusive:
                n_exclusive += 1
            else:
                n_shared += 1

            # Classify as rare or common
            if folio_count < RARITY_THRESHOLD:
                rare_total += 1
                if is_exclusive:
                    rare_exclusive += 1
            else:
                common_total += 1
                if is_exclusive:
                    common_exclusive += 1

            # Record for statistical test
            middle_exclusivity.append({
                'middle': mid,
                'folio': folio,
                'is_exclusive': is_exclusive,
                'n_zones': len(zones_present),
                'zones': sorted(zones_present),
                'folio_freq': freq,
                'corpus_folio_count': folio_count,
                'is_rare': folio_count < RARITY_THRESHOLD,
            })

        total_classified = n_exclusive + n_shared
        per_folio_summary[folio] = {
            'n_paragraphs': max(para_assignments) if para_assignments else 0,
            'n_lines': len(set(t['line'] for t in ftokens)),
            'n_tokens': len(ftokens),
            'n_unique_middles': len(middle_folio_freq),
            'n_hapax_skipped': n_hapax_skipped,
            'n_classified': total_classified,
            'n_zone_exclusive': n_exclusive,
            'n_shared': n_shared,
            'zone_exclusive_rate': n_exclusive / total_classified if total_classified > 0 else None,
            'rare_exclusive': rare_exclusive,
            'rare_total': rare_total,
            'common_exclusive': common_exclusive,
            'common_total': common_total,
        }

    # ---- Aggregate statistics ----
    # Per-middle exclusivity rates by rarity class
    rare_records = [r for r in middle_exclusivity if r['is_rare']]
    common_records = [r for r in middle_exclusivity if not r['is_rare']]

    rare_exclusive_count = sum(1 for r in rare_records if r['is_exclusive'])
    common_exclusive_count = sum(1 for r in common_records if r['is_exclusive'])

    rare_exclusive_rate = rare_exclusive_count / len(rare_records) if rare_records else 0
    common_exclusive_rate = common_exclusive_count / len(common_records) if common_records else 0

    print(f"\n=== Zone Exclusivity Results ===")
    print(f"  Rare middles (<{RARITY_THRESHOLD} folios): {rare_exclusive_count}/{len(rare_records)} zone-exclusive = {rare_exclusive_rate:.3f}")
    print(f"  Common middles (>={RARITY_THRESHOLD} folios): {common_exclusive_count}/{len(common_records)} zone-exclusive = {common_exclusive_rate:.3f}")

    # ---- Mann-Whitney U test ----
    # Compare zone-exclusive rates per folio between rare and common
    # Build per-folio rates for each rarity class
    rare_folio_rates = []
    common_folio_rates = []

    for folio, summary in per_folio_summary.items():
        if summary['rare_total'] > 0:
            rare_folio_rates.append(summary['rare_exclusive'] / summary['rare_total'])
        if summary['common_total'] > 0:
            common_folio_rates.append(summary['common_exclusive'] / summary['common_total'])

    print(f"\n  Per-folio rare rates: n={len(rare_folio_rates)}, mean={sum(rare_folio_rates)/len(rare_folio_rates):.3f}" if rare_folio_rates else "  No rare per-folio data")
    print(f"  Per-folio common rates: n={len(common_folio_rates)}, mean={sum(common_folio_rates)/len(common_folio_rates):.3f}" if common_folio_rates else "  No common per-folio data")

    # Mann-Whitney U on individual (middle, folio) exclusivity values
    # Use binary: 1 if exclusive, 0 if shared
    rare_values = [1 if r['is_exclusive'] else 0 for r in rare_records]
    common_values = [1 if r['is_exclusive'] else 0 for r in common_records]

    if len(rare_values) >= 5 and len(common_values) >= 5:
        u_stat, p_value = mannwhitneyu(rare_values, common_values, alternative='greater')
        print(f"\n  Mann-Whitney U = {u_stat:.1f}, p = {p_value:.6f}")
    else:
        u_stat = None
        p_value = None
        print("\n  Insufficient data for Mann-Whitney U test")

    # ---- Effect size (Cohen's d) ----
    if rare_values and common_values:
        mean_rare = sum(rare_values) / len(rare_values)
        mean_common = sum(common_values) / len(common_values)

        var_rare = sum((x - mean_rare) ** 2 for x in rare_values) / max(1, len(rare_values) - 1)
        var_common = sum((x - mean_common) ** 2 for x in common_values) / max(1, len(common_values) - 1)

        pooled_std = math.sqrt(
            ((len(rare_values) - 1) * var_rare + (len(common_values) - 1) * var_common)
            / (len(rare_values) + len(common_values) - 2)
        )
        effect_size_d = (mean_rare - mean_common) / pooled_std if pooled_std > 0 else 0
        print(f"  Cohen's d = {effect_size_d:.3f}")
    else:
        effect_size_d = None

    # ---- Verdict ----
    # SUPPORTED if rare middles are significantly more zone-exclusive than common
    if p_value is not None and p_value < 0.05 and rare_exclusive_rate > common_exclusive_rate:
        verdict = "SUPPORTED"
    else:
        verdict = "NOT_SUPPORTED"

    print(f"\n  Verdict: {verdict}")

    # ---- Zone breakdown ----
    # Which zone do exclusive middles prefer?
    zone_preference = Counter()
    for r in middle_exclusivity:
        if r['is_exclusive']:
            zone_preference[r['zones'][0]] += 1

    rare_zone_pref = Counter()
    for r in rare_records:
        if r['is_exclusive']:
            rare_zone_pref[r['zones'][0]] += 1

    common_zone_pref = Counter()
    for r in common_records:
        if r['is_exclusive']:
            common_zone_pref[r['zones'][0]] += 1

    print(f"\n  Zone preference (all exclusive middles): {dict(zone_preference)}")
    print(f"  Zone preference (rare exclusive): {dict(rare_zone_pref)}")
    print(f"  Zone preference (common exclusive): {dict(common_zone_pref)}")

    # ---- Save results ----
    results = {
        'test': 'Phase-Position Exclusivity',
        'n_folios': len(folio_groups),
        'n_tokens_analyzed': len(all_tokens),
        'n_middle_folio_pairs': len(middle_exclusivity),
        'rarity_threshold_folios': RARITY_THRESHOLD,
        'min_folio_occurrences': MIN_FOLIO_OCCURRENCES,
        'rare_zone_exclusive_rate': round(rare_exclusive_rate, 4),
        'common_zone_exclusive_rate': round(common_exclusive_rate, 4),
        'rare_count': len(rare_records),
        'common_count': len(common_records),
        'rare_exclusive_count': rare_exclusive_count,
        'common_exclusive_count': common_exclusive_count,
        'mann_whitney_u': round(u_stat, 2) if u_stat is not None else None,
        'p_value': float(f'{p_value:.2e}') if p_value is not None else None,
        'p_value_str': f'{p_value:.2e}' if p_value is not None else None,
        'effect_size_d': round(effect_size_d, 4) if effect_size_d is not None else None,
        'verdict': verdict,
        'zone_preference_all': dict(zone_preference),
        'zone_preference_rare': dict(rare_zone_pref),
        'zone_preference_common': dict(common_zone_pref),
        'per_folio_summary': per_folio_summary,
        'notes': (
            f"Zone-exclusive = MIDDLE appears in exactly 1 of 3 zones (SETUP/PROCESS/FINISH). "
            f"Hapax middles (1 occurrence per folio) excluded to avoid trivial exclusivity. "
            f"Zones assigned by paragraph (3+ paras) or line-based 20/60/20 split (1-2 paras). "
            f"RARE = appears in <{RARITY_THRESHOLD} folios across corpus. "
            f"Mann-Whitney U tests whether rare middles have higher zone-exclusivity than common."
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'phase_exclusivity_corpus.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
