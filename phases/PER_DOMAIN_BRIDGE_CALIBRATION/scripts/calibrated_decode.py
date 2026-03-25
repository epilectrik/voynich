"""
Phase 627, Script 3: Calibrated Decode -- PL-Enriched Operational Labels.

Enriches Phase 626 decode cards with PL-calibrated operational labels.
Assigns PL-derived operational descriptions to the 6 functional groups
and REGIMEs using channel calibration from Script 2.

Input:
  - phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/pl_channel_features.json
  - phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/channel_calibration.json
  - phases/A_TO_B_BRIDGE_DECOMPOSITION/results/bridge_decomposition.json
  - phases/A_TO_B_BRIDGE_DECOMPOSITION/results/folio_decode_cards.json
  - results/folio_operational_profiles.json
  - data/regime_folio_mapping.json

Output:
  - phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/calibrated_decode.json
"""

import sys
import time
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared_627 import (
    PROJECT_ROOT, RESULTS_DIR, HEAD_TYPES, CATEGORIES,
    FIRE_DEGREE_REGIME, HEAT_INTENSITY,
    round_floats, euclidean_dist, _pearson,
    load_pl_channel_features, load_bridge_decomposition,
    load_bridge_functional_groups, load_b_operational_profiles,
    load_regime_mapping, compute_folio_head_channel_profile,
    compute_regime_head_profiles,
)

t0 = time.time()
print("=" * 60)
print("Phase 627, Script 3: Calibrated Decode")
print("=" * 60)

# ============================================================
# Load all input data
# ============================================================

print("\n--- Loading data ---")

# Script 1 output
pl_features = load_pl_channel_features()
print(f"  PL channel features: {pl_features['metadata']['n_chapters']} chapters")

# Script 2 output
cal_path = RESULTS_DIR / 'channel_calibration.json'
with open(cal_path) as f:
    calibration = json.load(f)
print(f"  Channel calibration loaded")

# Bridge decomposition (Phase 626)
bridge_data = load_bridge_decomposition()
middle_to_group, group_profiles = load_bridge_functional_groups()
print(f"  Bridge decomposition: {len(middle_to_group)} bridge MIDDLEs, "
      f"{len(group_profiles)} groups")

# Decode cards (Phase 626)
decode_path = (PROJECT_ROOT / 'phases' / 'A_TO_B_BRIDGE_DECOMPOSITION' /
               'results' / 'folio_decode_cards.json')
with open(decode_path) as f:
    decode_data = json.load(f)
pilot_folios = decode_data['T1_pilot_selection']['folios']
decode_cards = decode_data['T2_decode_cards']
print(f"  Decode cards: {len(decode_cards)} pilot folios: {pilot_folios}")

# Operational profiles and REGIME mapping
op_profiles = load_b_operational_profiles()
regime_map = load_regime_mapping()
print(f"  Operational profiles: {len(op_profiles)} folios")
print(f"  REGIME mapping: {len(regime_map)} folios")

# ============================================================
# Helper: Extract calibration strength per channel
# ============================================================

def get_calibration_strength(channel: str) -> str:
    """Determine calibration strength from Script 2 results.

    - "strong": corresponding P-test passed with within-Herbal replication
    - "moderate": P-test passed but Herbal replication marginal
    - "weak": P-test failed or insufficient data
    """
    # Map HEAD type to Script 2 prediction keys
    channel_pred_map = {
        'k': 'P1',   # k-HEAD ~ PL heat_rate
        'e': 'P2',   # e-channel ~ PL correction_rate
        'h': 'P5',   # h-channel ~ monitoring (cross-channel specificity)
        't': 'P3',   # t-channel ~ PL termination (within-family distance)
        'o': 'P5',   # o-HEAD ~ operational specification (specificity test)
        'a': None,    # a/null ~ no direct P-test
    }

    pred_key = channel_pred_map.get(channel)
    if pred_key is None:
        return 'weak'

    # Try to find the prediction result in calibration data
    # Script 2 structures predictions with pass/fail verdicts
    predictions = calibration.get('predictions', {})
    pred_result = predictions.get(pred_key, {})

    if not pred_result:
        # Try alternative structure: some Script 2 outputs nest differently
        # Check T-sections for the relevant test
        return _infer_strength_from_tests(channel)

    passed = pred_result.get('passed', False)
    herbal_ok = pred_result.get('herbal_replication', False)

    if passed and herbal_ok:
        return 'strong'
    elif passed:
        return 'moderate'
    else:
        return 'weak'


def _infer_strength_from_tests(channel: str) -> str:
    """Fallback: infer calibration strength from Script 2 task results."""
    # Walk through calibration tasks looking for relevant p-values

    # T1: REGIME-level channel tests (k, e, h)
    t1 = calibration.get('T1_regime_channel_tests', {})
    if channel == 'k':
        kw_result = t1.get('k_head_kruskal_wallis', t1.get('k_channel', {}))
        p_val = _extract_p(kw_result)
        herbal_p = _extract_herbal_p(t1, 'k')
        return _strength_from_p(p_val, herbal_p)
    elif channel == 'e':
        kw_result = t1.get('e_channel', t1.get('e_head_kruskal_wallis', {}))
        p_val = _extract_p(kw_result)
        herbal_p = _extract_herbal_p(t1, 'e')
        return _strength_from_p(p_val, herbal_p)
    elif channel == 'h':
        kw_result = t1.get('h_channel', t1.get('h_head_kruskal_wallis', {}))
        p_val = _extract_p(kw_result)
        herbal_p = _extract_herbal_p(t1, 'h')
        return _strength_from_p(p_val, herbal_p)

    # T2 or T3: termination channel
    if channel == 't':
        t2 = calibration.get('T2_within_family_distance', {})
        t3 = calibration.get('T3_heat_ordering', {})
        # t-channel often tested via termination correlation
        p_val = _extract_p(t2) if t2 else 1.0
        return 'moderate' if p_val < 0.05 else 'weak'

    # o-HEAD: checked via cross-channel specificity (T5)
    if channel == 'o':
        t5 = calibration.get('T5_cross_channel_specificity',
                             calibration.get('T5_specificity', {}))
        if t5:
            mean_off = t5.get('mean_off_diagonal_rho', 1.0)
            return 'moderate' if mean_off < 0.15 else 'weak'

    return 'weak'


def _extract_p(result: dict) -> float:
    """Extract p-value from a test result dict."""
    if not result:
        return 1.0
    for key in ['p_value', 'p', 'kw_p', 'perm_p', 'p_val']:
        if key in result:
            return result[key]
    # Nested: look one level deeper
    for v in result.values():
        if isinstance(v, dict):
            for key in ['p_value', 'p', 'kw_p', 'perm_p']:
                if key in v:
                    return v[key]
    return 1.0


def _extract_herbal_p(t1: dict, channel: str) -> float:
    """Extract within-Herbal replication p-value for a channel."""
    herbal = t1.get('within_herbal', t1.get('herbal_replication', {}))
    if isinstance(herbal, dict):
        ch_result = herbal.get(channel, herbal.get(f'{channel}_channel', {}))
        return _extract_p(ch_result) if isinstance(ch_result, dict) else 1.0
    return 1.0


def _strength_from_p(p_main: float, p_herbal: float) -> str:
    """Convert p-values to calibration strength label."""
    if p_main < 0.05 and p_herbal < 0.10:
        return 'strong'
    elif p_main < 0.05:
        return 'moderate'
    else:
        return 'weak'


# ============================================================
# T1: HEAD-channel PL operational labels
# ============================================================

print("\n--- T1: HEAD-channel PL operational labels ---")

# PL-calibrated label definitions per HEAD type
PL_LABELS = {
    'k': {
        'pl_label': 'thermal energy / heat mode specification',
        'pl_description': (
            'PL calibration: fire degree and heat intensity. k-HEAD MIDDLEs '
            'specify thermal energy input — heat mode selection (balneum mariae, '
            'athanor, open fire), intensity grading (gentle to fierce), and '
            'fire-degree transitions. Corresponds to PL chapters with high '
            'heat_rate and explicit fire-degree instructions.'
        ),
    },
    'e': {
        'pl_label': 'recovery / correction / stability maintenance',
        'pl_description': (
            'PL calibration: correction procedures and recoverable failures. '
            'e-HEAD MIDDLEs specify error-handling and recovery operations — '
            'process drift correction, restart protocols, and stability '
            'maintenance. Corresponds to PL chapters with high correction_rate '
            'and explicit failure-mode discussion.'
        ),
    },
    'h': {
        'pl_label': 'process monitoring / quality assessment',
        'pl_description': (
            'PL calibration: color, consistency, and volatility observation. '
            'h-HEAD MIDDLEs (in bridge context, Group 5 null/a subpopulation '
            'with MONITORING category) specify process monitoring — color-change '
            'assessment, consistency checks, and volatility indicators. '
            'Corresponds to PL chapters with high monitoring_rate and chained '
            'observation passages.'
        ),
    },
    't': {
        'pl_label': 'flow control / termination / iteration',
        'pl_description': (
            'PL calibration: termination conditions and threshold/quality gates. '
            't-HEAD MIDDLEs specify iteration control — when to stop, when to '
            'repeat, count-based vs quality-gated termination. Corresponds to '
            'PL chapters with high termination_rate and explicit until/repeat '
            'constructions.'
        ),
    },
    'o': {
        'pl_label': 'operational specification / procedure marking',
        'pl_description': (
            'PL calibration: operation-family keywords (distillation, '
            'sublimation, etc.). o-HEAD MIDDLEs specify the operation type '
            'itself — marking which procedural family is active. Corresponds '
            'to PL chapters where operation-naming keywords dominate over '
            'parameter specification.'
        ),
    },
    'a': {
        'pl_label': 'transition management / state progression',
        'pl_description': (
            'PL calibration: less specific. a/null-HEAD MIDDLEs specify state '
            'transitions and staging progression — material preparation, '
            'intermediate state management, and phase boundaries. PL '
            'calibration is weaker for this channel due to less distinctive '
            'textual markers.'
        ),
    },
}

# Map group IDs to HEAD types using bridge decomposition group_profiles
GROUP_HEAD_MAP = {}
for gid, gp in group_profiles.items():
    heads = gp.get('hmt_heads', {})
    if not heads:
        GROUP_HEAD_MAP[gid] = 'null'
        continue
    # Determine dominant HEAD type for the group
    dominant = max(heads, key=heads.get)
    GROUP_HEAD_MAP[gid] = dominant

# Build T1 output
t1_group_labels = []
for gid in sorted(group_profiles.keys()):
    gp = group_profiles[gid]
    head = GROUP_HEAD_MAP[gid]

    # For groups 5 and 6, HEAD is null or a
    if head == 'null':
        head_key = 'a'  # map null-HEAD to a/null PL label
    else:
        head_key = head

    pl_info = PL_LABELS.get(head_key, PL_LABELS['a'])
    strength = get_calibration_strength(head_key)

    # Build B-category alignment string from top_categories
    top_cats = gp.get('top_categories', {})
    cat_parts = [f"{cat}:{cnt}" for cat, cnt in
                 sorted(top_cats.items(), key=lambda x: -x[1])]
    b_cat_alignment = ', '.join(cat_parts)

    # Determine displayed HEAD type string
    heads_dict = gp.get('hmt_heads', {})
    head_display = '/'.join(f"{h}" for h in sorted(heads_dict.keys()))

    label_entry = {
        'group_id': gid,
        'head_type': head_display,
        'n_middles': gp['n_middles'],
        'pl_label': pl_info['pl_label'],
        'pl_description': pl_info['pl_description'],
        'b_category_alignment': b_cat_alignment,
        'calibration_strength': strength,
    }
    t1_group_labels.append(label_entry)
    print(f"  Group {gid} ({head_display}, n={gp['n_middles']}): "
          f"{pl_info['pl_label']} [{strength}]")

# ============================================================
# T2: Decode card enrichment
# ============================================================

print("\n--- T2: Decode card enrichment ---")

# Load PL family mean signatures from Script 1 T6
pl_t6 = pl_features.get('T6_family_aggregation', {}).get('families', {})

# REGIME -> PL family mapping (from C1749, with confidence notes)
REGIME_PL_FAMILY = {
    'REGIME_1': {'family': 'distillation', 'confidence': 'high',
                 'basis': 'C1749: largest operational family (16 chapters)'},
    'REGIME_2': {'family': 'fixation', 'confidence': 'low',
                 'basis': 'C1749: fixation (10 ch) or dissolution (12 ch), ambiguous'},
    'REGIME_3': {'family': 'sublimation', 'confidence': 'moderate',
                 'basis': 'C1749: sublimation (7 chapters)'},
    'REGIME_4': {'family': 'calcination', 'confidence': 'low',
                 'basis': 'C494 precision axis; possibly calcination/circulation'},
}


def build_group_breakdown(bridge_details: list) -> dict:
    """Compute per-functional-group token counts and PL labels for a folio."""
    group_counts = defaultdict(int)
    group_middles = defaultdict(list)

    for detail in bridge_details:
        gid = detail.get('functional_group')
        count = detail.get('count_in_folio', 1)
        middle = detail.get('middle', '')
        if gid is not None:
            group_counts[gid] += count
            group_middles[gid].append(middle)

    total = sum(group_counts.values())
    breakdown = {}
    for gid in sorted(group_counts.keys()):
        head = GROUP_HEAD_MAP.get(gid, 'null')
        head_key = head if head != 'null' else 'a'
        pl_info = PL_LABELS.get(head_key, PL_LABELS['a'])
        frac = group_counts[gid] / total if total > 0 else 0.0
        breakdown[f"group_{gid}"] = {
            'head_type': GROUP_HEAD_MAP.get(gid, 'null'),
            'token_count': group_counts[gid],
            'fraction': frac,
            'pl_label': pl_info['pl_label'],
            'middles': group_middles[gid],
        }
    return breakdown


def build_pl_narrative(folio: str, regime: str, group_breakdown: dict,
                       category_profile: dict) -> str:
    """Build a PL-calibrated narrative for a folio decode card."""
    regime_info = REGIME_PL_FAMILY.get(regime, {})
    pl_family = regime_info.get('family', 'unknown')
    confidence = regime_info.get('confidence', 'low')

    # Find dominant groups (by fraction)
    sorted_groups = sorted(group_breakdown.items(),
                           key=lambda x: -x[1]['fraction'])

    # Top 3 groups for narrative
    top_parts = []
    for gkey, ginfo in sorted_groups[:3]:
        pct = ginfo['fraction'] * 100
        label = ginfo['pl_label']
        head = ginfo['head_type']
        top_parts.append(f"{head}-HEAD ({pct:.0f}%, {label})")

    # Get PL family thermal profile if available
    family_sig = pl_t6.get(pl_family, {})
    family_mean_sig = family_sig.get('mean_signature', {})
    k_heat_rate = family_mean_sig.get('k_channel', {}).get('heat_rate', None)
    e_corr_rate = family_mean_sig.get('e_channel', {}).get('correction_rate', None)

    # Build narrative
    parts = [f"Folio {folio} ({regime}):"]

    # Channel composition
    parts.append(f"Bridge MIDDLE composition: {', '.join(top_parts)}.")

    # REGIME → PL family
    parts.append(
        f"REGIME association: {pl_family} "
        f"(confidence: {confidence})."
    )

    # PL-calibrated thermal context
    if k_heat_rate is not None:
        # Find k-HEAD fraction in this folio
        k_groups = [v for k, v in group_breakdown.items()
                    if v['head_type'] == 'k']
        k_frac = sum(g['fraction'] for g in k_groups)
        if k_frac > 0.15:
            parts.append(
                f"Elevated k-HEAD ({k_frac*100:.0f}%) suggests high thermal "
                f"energy specification. PL {pl_family} mean heat_rate: "
                f"{k_heat_rate:.3f}."
            )
        elif k_frac > 0.05:
            parts.append(
                f"Moderate k-HEAD ({k_frac*100:.0f}%) indicates standard "
                f"thermal specification. PL {pl_family} mean heat_rate: "
                f"{k_heat_rate:.3f}."
            )

    # PL-calibrated correction context
    if e_corr_rate is not None:
        e_groups = [v for k, v in group_breakdown.items()
                    if v['head_type'] == 'e']
        e_frac = sum(g['fraction'] for g in e_groups)
        if e_frac > 0.15:
            parts.append(
                f"Elevated e-HEAD ({e_frac*100:.0f}%) suggests active "
                f"correction/recovery. PL {pl_family} mean correction_rate: "
                f"{e_corr_rate:.3f}."
            )

    return ' '.join(parts)


t2_enriched = {}
for folio in pilot_folios:
    card = decode_cards.get(folio)
    if card is None:
        print(f"  WARNING: {folio} not in decode cards, skipping")
        continue

    # Extract regime from B-side dominant_regime
    b_side = card.get('b_side', {})
    regime = b_side.get('dominant_regime', 'UNKNOWN')

    # Get bridge details
    bridge = card.get('bridge', {})
    bridge_details = bridge.get('details', [])

    # Compute group breakdown
    group_breakdown = build_group_breakdown(bridge_details)

    # Get A-side category profile
    a_side = card.get('a_side', {})
    category_profile = a_side.get('category_profile', {})

    # Build PL narrative
    pl_narrative = build_pl_narrative(folio, regime, group_breakdown,
                                      category_profile)

    # Assemble enriched card
    t2_enriched[folio] = {
        'regime': regime,
        'section': a_side.get('section', 'H'),
        'cluster': a_side.get('cluster'),
        'n_bridge_types': bridge.get('n_bridge_types', 0),
        'n_bridge_tokens': bridge.get('n_bridge_tokens', 0),
        'operational_emphasis': card.get('synthesis', {}).get(
            'operational_emphasis', ''),
        'material_overlay_dominant': card.get('synthesis', {}).get(
            'material_overlay_dominant', ''),
        'pl_narrative': pl_narrative,
        'pl_group_breakdown': group_breakdown,
    }
    print(f"  {folio}: {regime}, {len(group_breakdown)} groups enriched")

# ============================================================
# T3: REGIME-level PL operational profiles
# ============================================================

print("\n--- T3: REGIME-level PL operational profiles ---")

# Compute per-REGIME mean HEAD-channel profiles from V-side
regime_head_profiles = compute_regime_head_profiles(op_profiles, regime_map)

# Get PL per-family mean signatures from Script 1 T6
pl_families = pl_features.get('T6_family_aggregation', {}).get('families', {})

# Group folios by REGIME for detailed profiling
regime_folios = defaultdict(list)
for folio, regime in regime_map.items():
    regime_folios[regime].append(folio)

t3_regime_profiles = {}
for regime in sorted(regime_folios.keys()):
    folios = regime_folios[regime]
    head_prof = regime_head_profiles.get(regime, {})

    # PL family association
    pl_assoc = REGIME_PL_FAMILY.get(regime, {})
    pl_family = pl_assoc.get('family', 'unknown')
    confidence = pl_assoc.get('confidence', 'low')

    # Get PL family mean signature
    fam_data = pl_families.get(pl_family, {})
    fam_sig = fam_data.get('mean_signature', {})

    # Thermal profile from PL
    k_sig = fam_sig.get('k_channel', {})
    thermal_desc = 'unknown'
    if k_sig:
        heat_rate = k_sig.get('heat_rate', 0)
        mean_intensity = k_sig.get('mean_heat_intensity', 0)
        if mean_intensity > 5:
            thermal_desc = f"high heat (PL mean intensity {mean_intensity:.1f})"
        elif mean_intensity > 3:
            thermal_desc = f"moderate heat (PL mean intensity {mean_intensity:.1f})"
        elif mean_intensity > 0:
            thermal_desc = f"low heat (PL mean intensity {mean_intensity:.1f})"
        else:
            thermal_desc = "minimal heat specification"
    else:
        thermal_desc = "no PL thermal data for this family"

    # Monitoring profile from PL
    h_sig = fam_sig.get('h_channel', {})
    monitoring_desc = 'unknown'
    if h_sig:
        mon_rate = h_sig.get('monitoring_rate', 0)
        if mon_rate > 0.15:
            monitoring_desc = f"high monitoring density (PL rate {mon_rate:.3f})"
        elif mon_rate > 0.05:
            monitoring_desc = f"moderate monitoring density (PL rate {mon_rate:.3f})"
        elif mon_rate > 0:
            monitoring_desc = f"low monitoring density (PL rate {mon_rate:.3f})"
        else:
            monitoring_desc = "minimal monitoring"
    else:
        monitoring_desc = "no PL monitoring data for this family"

    # Correction profile from PL
    e_sig = fam_sig.get('e_channel', {})
    correction_desc = 'unknown'
    if e_sig:
        corr_rate = e_sig.get('correction_rate', 0)
        recov_frac = e_sig.get('recoverable_frac', 0)
        if corr_rate > 0.05:
            correction_desc = (f"high correction rate (PL rate {corr_rate:.3f}, "
                               f"recoverable {recov_frac:.1%})")
        elif corr_rate > 0.02:
            correction_desc = (f"moderate correction rate (PL rate {corr_rate:.3f}, "
                               f"recoverable {recov_frac:.1%})")
        elif corr_rate > 0:
            correction_desc = (f"low correction rate (PL rate {corr_rate:.3f})")
        else:
            correction_desc = "minimal correction specification"
    else:
        correction_desc = "no PL correction data for this family"

    # Termination profile from PL
    t_sig = fam_sig.get('t_channel', {})
    termination_desc = 'unknown'
    if t_sig:
        term_rate = t_sig.get('termination_rate', 0)
        thresh_frac = t_sig.get('threshold_frac', 0)
        if term_rate > 0.05:
            termination_desc = (f"high termination rate (PL rate {term_rate:.3f}, "
                                f"threshold-based {thresh_frac:.1%})")
        elif term_rate > 0.02:
            termination_desc = (f"moderate termination rate (PL rate {term_rate:.3f})")
        elif term_rate > 0:
            termination_desc = (f"low termination rate (PL rate {term_rate:.3f})")
        else:
            termination_desc = "minimal termination specification"
    else:
        termination_desc = "no PL termination data for this family"

    # Build HEAD channel signature from V-side
    head_sig = {}
    for feat in ['k_ratio', 'e_ratio', 'h_ratio', 'thermo_ke',
                 'iteration_rate', 'checkpoint_rate', 'terminal_rate']:
        head_sig[feat] = head_prof.get(feat, 0.0)

    # Build PL summary
    summary_parts = [
        f"{regime} ({len(folios)} folios) maps to PL {pl_family} "
        f"(confidence: {confidence}).",
    ]
    if k_sig:
        summary_parts.append(f"Thermal: {thermal_desc}.")
    if h_sig:
        summary_parts.append(f"Monitoring: {monitoring_desc}.")
    if e_sig:
        summary_parts.append(f"Correction: {correction_desc}.")
    if t_sig:
        summary_parts.append(f"Termination: {termination_desc}.")
    pl_summary = ' '.join(summary_parts)

    t3_regime_profiles[regime] = {
        'n_folios': len(folios),
        'pl_family_association': f"{pl_family} ({confidence})",
        'thermal_profile': thermal_desc,
        'monitoring_profile': monitoring_desc,
        'correction_profile': correction_desc,
        'termination_profile': termination_desc,
        'head_channel_signature': head_sig,
        'pl_summary': pl_summary,
    }
    print(f"  {regime}: {len(folios)} folios -> {pl_family} ({confidence})")

# ============================================================
# T4: Leave-one-REGIME-out cross-validation
# ============================================================

print("\n--- T4: Leave-one-REGIME-out cross-validation ---")

# Channels we predict: k_ratio, e_ratio, h_ratio
PRED_CHANNELS = ['k_ratio', 'e_ratio', 'h_ratio']

# Build per-folio channel feature vectors
folio_channel_features = {}
for folio in regime_map:
    prof = compute_folio_head_channel_profile(folio, op_profiles)
    if prof:
        folio_channel_features[folio] = prof

# Build PL family mean channel vectors (6D from Script 1 T5)
def pl_family_channel_vector(family_name: str) -> dict:
    """Extract mean channel rates for a PL family."""
    fam_data = pl_families.get(family_name, {})
    fam_sig = fam_data.get('mean_signature', {})
    return {
        'pl_heat_rate': fam_sig.get('k_channel', {}).get('heat_rate', 0),
        'pl_heat_intensity': fam_sig.get('k_channel', {}).get('mean_heat_intensity', 0),
        'pl_correction_rate': fam_sig.get('e_channel', {}).get('correction_rate', 0),
        'pl_monitoring_rate': fam_sig.get('h_channel', {}).get('monitoring_rate', 0),
        'pl_termination_rate': fam_sig.get('t_channel', {}).get('termination_rate', 0),
    }


# PL feature -> V channel mapping vectors (which PL features predict each V channel)
# k_ratio ~ pl_heat_rate, pl_heat_intensity
# e_ratio ~ pl_correction_rate
# h_ratio ~ pl_monitoring_rate
PL_TO_V_PREDICTORS = {
    'k_ratio': ['pl_heat_rate', 'pl_heat_intensity'],
    'e_ratio': ['pl_correction_rate'],
    'h_ratio': ['pl_monitoring_rate'],
}

all_regimes = sorted(regime_folios.keys())
t4_per_regime = {}
all_maes = []

for held_out in all_regimes:
    print(f"  Holding out {held_out} ({len(regime_folios[held_out])} folios)...")

    # Training REGIMEs (everything except held-out)
    train_regimes = [r for r in all_regimes if r != held_out]

    # Compute training REGIME mean V-channel profiles
    train_means = {}
    for r in train_regimes:
        r_vals = defaultdict(list)
        for folio in regime_folios[r]:
            prof = folio_channel_features.get(folio)
            if prof:
                for ch in PRED_CHANNELS:
                    r_vals[ch].append(prof.get(ch, 0.0))
        train_means[r] = {ch: (sum(vs) / len(vs) if vs else 0.0)
                          for ch, vs in r_vals.items()}

    # Get training REGIME PL family vectors
    train_pl = {}
    for r in train_regimes:
        fam = REGIME_PL_FAMILY.get(r, {}).get('family', 'unknown')
        train_pl[r] = pl_family_channel_vector(fam)

    # For each predicted V-channel, fit a simple linear mapping:
    # V_channel ~ weighted mean of PL predictors
    # Using training REGIMEs as data points (n=3 per LOO)

    # Predict held-out REGIME channels
    held_fam = REGIME_PL_FAMILY.get(held_out, {}).get('family', 'unknown')
    held_pl = pl_family_channel_vector(held_fam)

    predicted = {}
    for v_ch in PRED_CHANNELS:
        # Collect (pl_predictor_values, v_channel_mean) for training regimes
        pl_keys = PL_TO_V_PREDICTORS[v_ch]
        train_x = []
        train_y = []
        for r in train_regimes:
            pl_vec = train_pl[r]
            x_val = sum(pl_vec.get(k, 0) for k in pl_keys) / len(pl_keys)
            y_val = train_means[r].get(v_ch, 0.0)
            train_x.append(x_val)
            train_y.append(y_val)

        # Simple linear prediction: if we have 3 training points,
        # use mean-ratio mapping (scale held-out PL to V space)
        mean_x = sum(train_x) / len(train_x) if train_x else 1.0
        mean_y = sum(train_y) / len(train_y) if train_y else 0.0

        held_x = sum(held_pl.get(k, 0) for k in pl_keys) / len(pl_keys)

        if abs(mean_x) > 1e-12:
            # Ratio-based prediction: scale by how held-out PL differs from
            # training mean PL, applied to training mean V
            scale = held_x / mean_x
            # Use correlation-weighted prediction
            if len(train_x) >= 3:
                rho = _pearson(train_x, train_y)
                # Regression-to-mean prediction
                predicted_val = mean_y + rho * (scale - 1.0) * mean_y
            else:
                predicted_val = mean_y * scale
        else:
            predicted_val = mean_y

        # Clamp to [0, 1]
        predicted[v_ch] = max(0.0, min(1.0, predicted_val))

    # Actual held-out REGIME means
    actual_vals = defaultdict(list)
    for folio in regime_folios[held_out]:
        prof = folio_channel_features.get(folio)
        if prof:
            for ch in PRED_CHANNELS:
                actual_vals[ch].append(prof.get(ch, 0.0))
    actual = {ch: (sum(vs) / len(vs) if vs else 0.0)
              for ch, vs in actual_vals.items()}

    # Compute MAE per channel
    regime_result = {
        'predicted': predicted,
        'actual': actual,
    }
    for ch in PRED_CHANNELS:
        mae = abs(predicted[ch] - actual[ch])
        regime_result[f'mae_{ch.replace("_ratio", "")}'] = mae
        all_maes.append(mae)

    t4_per_regime[held_out] = regime_result
    pred_str = ', '.join(f'{ch}={predicted[ch]:.3f}' for ch in PRED_CHANNELS)
    act_str = ', '.join(f'{ch}={actual[ch]:.3f}' for ch in PRED_CHANNELS)
    print(f"    Predicted: {pred_str}")
    print(f"    Actual:    {act_str}")

# Overall metrics
overall_mean_mae = sum(all_maes) / len(all_maes) if all_maes else 0.0

# Find worst REGIME
worst_regime = None
worst_mae = -1
for regime, result in t4_per_regime.items():
    regime_mae = sum(result.get(f'mae_{ch.replace("_ratio", "")}', 0)
                     for ch in PRED_CHANNELS) / len(PRED_CHANNELS)
    if regime_mae > worst_mae:
        worst_mae = regime_mae
        worst_regime = regime

print(f"\n  Overall mean MAE: {overall_mean_mae:.4f}")
print(f"  Worst REGIME: {worst_regime} (mean MAE {worst_mae:.4f})")

# ============================================================
# Assemble output
# ============================================================

elapsed = time.time() - t0

result = {
    'metadata': {
        'phase': 627,
        'script': 3,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'n_pilot_folios': len(pilot_folios),
        'n_regimes': len(all_regimes),
        'elapsed_s': elapsed,
    },
    'T1_group_labels': t1_group_labels,
    'T2_enriched_decode_cards': t2_enriched,
    'T3_regime_profiles': t3_regime_profiles,
    'T4_loo_validation': {
        'per_regime': t4_per_regime,
        'overall_mean_mae': overall_mean_mae,
        'worst_regime': worst_regime,
    },
}

# Round all floats and write
result = round_floats(result)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
out_path = RESULTS_DIR / 'calibrated_decode.json'
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n{'=' * 60}")
print(f"Output: {out_path}")
print(f"Elapsed: {elapsed:.2f}s")
print(f"Pilot folios: {len(pilot_folios)}")
print(f"Groups labeled: {len(t1_group_labels)}")
print(f"Decode cards enriched: {len(t2_enriched)}")
print(f"REGIME profiles: {len(t3_regime_profiles)}")
print(f"LOO mean MAE: {overall_mean_mae:.4f}")
print(f"Worst REGIME: {worst_regime}")
print(f"{'=' * 60}")
