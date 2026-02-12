#!/usr/bin/env python3
"""
T4: Alternative Domain Compatibility Matrix
PROCESS_PHENOMENOLOGY_EXCLUSION phase (Tier 4)

Scores 7 alternative process domains against the 20-feature Voynich
structural fingerprint. Extends process_isomorphism.md (which tested
only calcination as negative control) to 7 complete domains.
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


# ============================================================
# DOMAIN DEFINITIONS
# ============================================================

DOMAINS = {
    'DISTILLATION': {
        'description': 'Circulatory reflux distillation (pelican/alembic)',
        'period': '15th century',
        'characteristics': 'Closed-loop thermal, phase-sensitive, multi-fraction, sensory-driven',
    },
    'FERMENTATION': {
        'description': 'Wine, beer, mead, or vinegar fermentation',
        'period': '15th century',
        'characteristics': 'Biological process, long timescale (days-weeks), limited intervention, open vessel',
    },
    'METALLURGY': {
        'description': 'Smelting, cupellation, assaying, metal annealing',
        'period': '15th century',
        'characteristics': 'Extreme temperatures, mineral/inorganic, solid-liquid-gas phases, furnace-based',
    },
    'GLASS_WORKING': {
        'description': 'Glass blowing, fusing, lamp-working, annealing',
        'period': '15th century',
        'characteristics': 'Extreme temperature, viscous material, continuous heating, visual-dominated',
    },
    'PHARMACOLOGICAL': {
        'description': 'Drug compounding, electuary preparation, tincture making',
        'period': '15th century',
        'characteristics': 'Sequential recipe, material identity critical, grinding/mixing, room temperature',
    },
    'RITUAL_CALENDAR': {
        'description': 'Astrological timing, liturgical scheduling, ritual sequences',
        'period': '15th century',
        'characteristics': 'No physical feedback loop, no continuous process, discrete calendar events',
    },
    'TEXTILE_DYEING': {
        'description': 'Vat dyeing, mordanting, color fixation',
        'period': '15th century',
        'characteristics': 'Temperature control matters, immersion process, no distillation, batch sequential',
    },
    'AGRICULTURAL': {
        'description': 'Irrigation scheduling, crop rotation, soil management',
        'period': '15th century',
        'characteristics': 'Long timescale (seasons), weather-dependent, no apparatus, no thermal control',
    },
}


# ============================================================
# COMPATIBILITY SCORING: 20 features x 8 domains
# Each entry: (score, reason)
# Score: 1.0 = fully compatible, 0.5 = partially compatible, 0.0 = incompatible
# ============================================================

COMPATIBILITY = {
    'F01_1token_response_time': {
        'description': 'System responds to hazard in exactly 1 token (immediate categorical gate)',
        'evidence': 'Hazard gate KL baseline at offset+2, C967',
        'scores': {
            'DISTILLATION':   (1.0, 'Thermal hazards require immediate response: reduce fire, open vent, redirect flow'),
            'FERMENTATION':   (0.0, 'Fermentation operates on hour/day timescale; no immediate hazard response needed'),
            'METALLURGY':     (0.5, 'Furnace has fast hazards (crack, spill) but response is physical, not categorical'),
            'GLASS_WORKING':  (0.5, 'Glass cracking/burning requires fast response but less categorical decision space'),
            'PHARMACOLOGICAL':(0.0, 'No continuous hazard; compounding is step-by-step at room temperature'),
            'RITUAL_CALENDAR':(0.0, 'No physical process requiring immediate response'),
            'TEXTILE_DYEING': (0.0, 'Dyeing hazards are slow (color wrong, mordant failure); no immediate gate needed'),
            'AGRICULTURAL':   (0.0, 'Seasonal timescale; no sub-minute hazard response'),
        },
    },
    'F02_first_order_markov_sufficient': {
        'description': 'Current state fully predicts next action; no hidden accumulator or memory required',
        'evidence': 'BIC selects 12-param markov_haz over 18-param full model, C966',
        'scores': {
            'DISTILLATION':   (1.0, 'Thermal state visible now; no need to remember previous temperatures'),
            'FERMENTATION':   (0.0, 'Fermentation progress depends on cumulative biological history'),
            'METALLURGY':     (0.5, 'Current metal state is somewhat visible but thermal history matters for annealing'),
            'GLASS_WORKING':  (0.5, 'Current viscosity visible but thermal history affects stress accumulation'),
            'PHARMACOLOGICAL':(0.0, 'Recipe progress requires tracking what has been added (cumulative state)'),
            'RITUAL_CALENDAR':(0.0, 'Calendar position requires knowing date (cumulative time)'),
            'TEXTILE_DYEING': (0.5, 'Current dye state partially visible but mordant history matters'),
            'AGRICULTURAL':   (0.0, 'Crop state depends on season history; not first-order'),
        },
    },
    'F03_categorical_not_numeric': {
        'description': 'System uses categorical distinctions (type/kind) not numeric values (quantity/amount)',
        'evidence': 'No ratio encoding C287-C290, no magnitude encoding, discrete MIDDLE variants, C469',
        'scores': {
            'DISTILLATION':   (1.0, 'Pre-instrument distillation uses sensory categories: hot/warm/cool, clear/cloudy'),
            'FERMENTATION':   (0.5, 'Some categorical (taste, color) but also quantitative (time, volume)'),
            'METALLURGY':     (0.0, 'Requires numeric: weight of ore, assay results, temperature estimation'),
            'GLASS_WORKING':  (0.0, 'Requires numeric: temperature estimation, thickness, timing'),
            'PHARMACOLOGICAL':(0.0, 'Requires precise quantities: weights, measures, proportions are central'),
            'RITUAL_CALENDAR':(0.5, 'Calendar uses categorical (which day/planet) but also counts (which hour)'),
            'TEXTILE_DYEING': (0.5, 'Some categorical (color matching) but also quantitative (dye amounts, timing)'),
            'AGRICULTURAL':   (0.0, 'Requires numeric: planting dates, water amounts, field dimensions'),
        },
    },
    'F04_high_dimensional_incompatibility': {
        'description': '100D discrimination space with 972 entities; 97.8% pairwise incompatible',
        'evidence': 'Effective rank 344, dimensionality ~101, compatibility only 2.2%, C987',
        'scores': {
            'DISTILLATION':   (1.0, 'Hundreds of aromatic compounds with complex cross-reactivity and co-occurrence rules'),
            'FERMENTATION':   (0.0, 'Simple: few ingredients (grain, water, yeast), low-dimensional parameter space'),
            'METALLURGY':     (0.5, 'Moderate: many alloy compositions but compatibility is lower-dimensional'),
            'GLASS_WORKING':  (0.0, 'Low-dimensional: few components (silica, soda, lime), simple compatibility'),
            'PHARMACOLOGICAL':(0.5, 'Moderate: drug interactions exist but typical formulary has <100 ingredients'),
            'RITUAL_CALENDAR':(0.0, 'No material incompatibility concept applies'),
            'TEXTILE_DYEING': (0.0, 'Low-dimensional: limited dye/mordant combinations, mostly independent'),
            'AGRICULTURAL':   (0.0, 'Low-dimensional: crop rotation rules are simple (3-4 categories)'),
        },
    },
    'F05_strong_transitivity': {
        'description': 'Compatibility is strongly transitive (clustering 0.873, z=+136.9)',
        'evidence': 'If A compat B and B compat C then very likely A compat C, C983',
        'scores': {
            'DISTILLATION':   (1.0, 'Compatible materials share physical properties (volatility, polarity) that propagate'),
            'FERMENTATION':   (0.0, 'Fermentation compatibility is not transitive (yeast A+sugar does not predict yeast B+sugar)'),
            'METALLURGY':     (0.5, 'Alloy compatibility is partially transitive (similar melting points cluster)'),
            'GLASS_WORKING':  (0.0, 'Glass compatibility is not strongly transitive'),
            'PHARMACOLOGICAL':(0.0, 'Drug interactions are famously non-transitive (A+B safe, B+C safe, A+C toxic)'),
            'RITUAL_CALENDAR':(0.0, 'No transitivity concept applies to calendar/ritual'),
            'TEXTILE_DYEING': (0.0, 'Dye compatibility is not transitive (mordant-dependent)'),
            'AGRICULTURAL':   (0.0, 'Crop rotation compatibility is not strongly transitive'),
        },
    },
    'F06_hazard_asymmetry': {
        'description': '65% of forbidden transitions are asymmetric (A->B forbidden but B->A allowed)',
        'evidence': 'Directional hazards, not symmetric incompatibilities, C111, C789',
        'scores': {
            'DISTILLATION':   (1.0, 'Phase transitions are asymmetric: heating past boil is dangerous, cooling past boil is safe'),
            'FERMENTATION':   (0.0, 'Fermentation hazards (contamination) are mostly symmetric'),
            'METALLURGY':     (0.5, 'Some asymmetry (heating iron is different from cooling) but less pronounced'),
            'GLASS_WORKING':  (0.5, 'Some asymmetry in heating/cooling glass but thermal shock is more symmetric'),
            'PHARMACOLOGICAL':(0.0, 'Compounding order sometimes matters but this is recipe, not hazard'),
            'RITUAL_CALENDAR':(0.0, 'No directional hazard concept'),
            'TEXTILE_DYEING': (0.0, 'Dyeing order matters (mordant before dye) but not in a hazard sense'),
            'AGRICULTURAL':   (0.0, 'No directional hazard concept in farming'),
        },
    },
    'F07_absorbing_stabilization_state': {
        'description': 'One kernel operator (e) absorbs 54.7% of recovery paths — system has an attractor state',
        'evidence': 'e = STABILITY_ANCHOR, one-way valve k,h->e elevated, e->h,k suppressed, C105, C521',
        'scores': {
            'DISTILLATION':   (1.0, 'Cooling/condensation IS the natural attractor — system returns to equilibrium via cooling'),
            'FERMENTATION':   (0.5, 'Fermentation has completion (all sugar consumed) as attractor but this is terminal, not recovery'),
            'METALLURGY':     (0.5, 'Cooling is important in metallurgy but not a dominant recovery mechanism in the same way'),
            'GLASS_WORKING':  (0.0, 'Glass has no absorbing state — you keep heating or it cools and freezes (different logic)'),
            'PHARMACOLOGICAL':(0.0, 'No absorbing state in compounding; each step is discrete'),
            'RITUAL_CALENDAR':(0.0, 'No physical absorbing state'),
            'TEXTILE_DYEING': (0.5, 'Rinse/cool is a recovery step but not a dominant attractor (17% not 55%)'),
            'AGRICULTURAL':   (0.0, 'No absorbing state in seasonal agriculture'),
        },
    },
    'F08_lane_oscillation': {
        'description': 'Two-lane alternation (QO/CHSH) at 55.4% with post-hazard CHSH spike to 75.2%',
        'evidence': 'Lane oscillation control law, C643, C645, C966',
        'scores': {
            'DISTILLATION':   (1.0, 'Natural heating/monitoring oscillation: apply heat (QO), check result (CHSH), adjust'),
            'FERMENTATION':   (0.0, 'No rapid oscillation in fermentation; it is passive waiting'),
            'METALLURGY':     (0.0, 'Metallurgy has heating but no systematic oscillation with monitoring'),
            'GLASS_WORKING':  (0.0, 'Glass working is continuous heating, not oscillatory'),
            'PHARMACOLOGICAL':(0.0, 'No oscillation in sequential recipe execution'),
            'RITUAL_CALENDAR':(0.0, 'No physical oscillation'),
            'TEXTILE_DYEING': (0.0, 'No rapid heating/monitoring oscillation in dyeing'),
            'AGRICULTURAL':   (0.0, 'No short-timescale oscillation'),
        },
    },
    'F09_energy_medial_concentration': {
        'description': 'ENERGY operators concentrated at line center, avoided at boundaries (0.45x initial, 0.50x final)',
        'evidence': 'Energy comes after setup, ends before closure, C556',
        'scores': {
            'DISTILLATION':   (1.0, 'Setup (prepare apparatus) -> Heat (distill) -> Close (collect/seal) matches medial energy'),
            'FERMENTATION':   (0.0, 'Energy is not a major concept in fermentation (it is biological, not thermal)'),
            'METALLURGY':     (1.0, 'Metallurgy also has: prepare furnace -> heat -> remove product. Similar medial pattern'),
            'GLASS_WORKING':  (1.0, 'Glass: prepare tools -> heat glass -> shape/finish. Similar medial pattern'),
            'PHARMACOLOGICAL':(0.0, 'No thermal energy phase in compounding'),
            'RITUAL_CALENDAR':(0.0, 'No energy concept'),
            'TEXTILE_DYEING': (0.5, 'Heat bath in middle of dye process, but not as pronounced as distillation'),
            'AGRICULTURAL':   (0.0, 'No concentrated energy phase'),
        },
    },
    'F10_recovery_unconditionally_free': {
        'description': '10/12 recovery features are REGIME-independent; escape strategy is per-folio design choice',
        'evidence': 'Recovery free, hazard clamped, C636, C635',
        'scores': {
            'DISTILLATION':   (1.0, 'Recovery from a near-boilover or contamination has many valid strategies depending on setup'),
            'FERMENTATION':   (0.0, 'Fermentation recovery is limited (contaminated batch is usually lost)'),
            'METALLURGY':     (0.5, 'Some recovery flexibility in metallurgy but options are more constrained by material'),
            'GLASS_WORKING':  (0.0, 'Glass recovery is very limited — once cracked or mis-shaped, material is lost'),
            'PHARMACOLOGICAL':(0.0, 'Wrong proportion in pharmacy is typically not recoverable'),
            'RITUAL_CALENDAR':(0.0, 'No physical recovery concept'),
            'TEXTILE_DYEING': (0.5, 'Some recovery options in dyeing (re-dye, re-mordant) but limited'),
            'AGRICULTURAL':   (0.0, 'Crop failure recovery is seasonal; not a within-process concept'),
        },
    },
    'F11_universal_grammar': {
        'description': '49 instruction classes with 100% coverage across 83 folios, zero exceptions',
        'evidence': '8.2x compression, holdout-invariant, C124',
        'scores': {
            'DISTILLATION':   (1.0, 'Same control vocabulary applies to all materials/runs (same apparatus, same operations)'),
            'FERMENTATION':   (0.0, 'Different ferments require very different procedures (wine vs beer vs vinegar)'),
            'METALLURGY':     (0.5, 'Partially universal (furnace operations shared) but metals require specialized operations'),
            'GLASS_WORKING':  (0.0, 'Different glass types require different techniques (blowing vs fusing vs annealing)'),
            'PHARMACOLOGICAL':(0.0, 'Each recipe is unique; no universal grammar of compounding'),
            'RITUAL_CALENDAR':(0.5, 'Calendar has universal structure (months, hours) but content varies by tradition'),
            'TEXTILE_DYEING': (0.0, 'Different dyes require different procedures (mordant type, temperature, timing)'),
            'AGRICULTURAL':   (0.0, 'Crops are highly variable; no universal agricultural grammar'),
        },
    },
    'F12_phase_ordering_dominant_hazard': {
        'description': 'PHASE_ORDERING is 41% of hazard transitions (7/17), largest class',
        'evidence': 'Phase failures dominate, C109, C110',
        'scores': {
            'DISTILLATION':   (1.0, 'Phase ordering is THE central challenge: liquid/vapor boundary management'),
            'FERMENTATION':   (0.0, 'Fermentation has no phase ordering (single liquid phase throughout)'),
            'METALLURGY':     (0.5, 'Phase matters (solid/liquid/gas) but not as dominant as in distillation'),
            'GLASS_WORKING':  (0.5, 'Viscous-liquid transition matters but it is gradual, not a sharp ordering problem'),
            'PHARMACOLOGICAL':(0.0, 'No phase ordering in compounding'),
            'RITUAL_CALENDAR':(0.0, 'No physical phases'),
            'TEXTILE_DYEING': (0.0, 'No significant phase ordering hazard in dyeing'),
            'AGRICULTURAL':   (0.0, 'No phase ordering concept'),
        },
    },
    'F13_convergent_monostate': {
        'description': '57.8% of programs terminate in STATE-C (a single dominant attractor)',
        'evidence': 'Convergent program structure, C079, C323',
        'scores': {
            'DISTILLATION':   (1.0, 'Distillation naturally converges to steady-state reflux as the operational target'),
            'FERMENTATION':   (1.0, 'Fermentation also converges to completion (all sugar consumed)'),
            'METALLURGY':     (0.5, 'Metal working has target states but they vary (different alloys, different products)'),
            'GLASS_WORKING':  (0.5, 'Annealing converges to cooled state, but working has many target shapes'),
            'PHARMACOLOGICAL':(0.0, 'Each recipe has its own endpoint; no universal convergent state'),
            'RITUAL_CALENDAR':(0.0, 'No physical convergent state'),
            'TEXTILE_DYEING': (0.5, 'Dyeing converges to "done" (color achieved) but this is binary, not a state'),
            'AGRICULTURAL':   (0.5, 'Harvest is a convergent endpoint but it is annual, not per-run'),
        },
    },
    'F14_exactly_5_hazard_classes': {
        'description': 'Exactly 5 failure classes covering 17 forbidden transitions across 6 instruction classes',
        'evidence': 'Rich hazard taxonomy matching phase-sensitive thermal process, C109, C541',
        'scores': {
            'DISTILLATION':   (1.0, 'Phase, composition, containment, rate, energy = 5 natural failure families in distillation'),
            'FERMENTATION':   (0.0, 'Fermentation has ~2 failure modes (contamination, stuck fermentation), not 5'),
            'METALLURGY':     (0.5, 'Metallurgy has several failure modes but different classes (crack, wrong alloy, oxidation)'),
            'GLASS_WORKING':  (0.0, 'Glass has ~2-3 failure modes (thermal shock, wrong shape, crystallization)'),
            'PHARMACOLOGICAL':(0.0, 'Pharmacy has ~2 failure modes (wrong amount, wrong ingredient)'),
            'RITUAL_CALENDAR':(0.0, 'No physical failure modes'),
            'TEXTILE_DYEING': (0.0, 'Dyeing has ~2 failure modes (wrong color, poor fixation)'),
            'AGRICULTURAL':   (0.0, 'Agriculture has failures but they are not within-process hazards'),
        },
    },
    'F15_closed_loop_not_batch': {
        'description': 'System is circulatory (closed-loop), not linear batch processing',
        'evidence': 'Pelican reflux circulates; line resets but within a continuous process, C670, C966',
        'scores': {
            'DISTILLATION':   (1.0, 'Pelican reflux IS a closed-loop circulatory system by definition'),
            'FERMENTATION':   (0.0, 'Fermentation is batch (start to finish, no circulation)'),
            'METALLURGY':     (0.0, 'Metallurgy is batch processing (heat, transform, cool, done)'),
            'GLASS_WORKING':  (0.5, 'Glass annealing involves controlled cooling but not a circulatory loop'),
            'PHARMACOLOGICAL':(0.0, 'Compounding is linear sequential, not circulatory'),
            'RITUAL_CALENDAR':(0.0, 'No physical loop'),
            'TEXTILE_DYEING': (0.5, 'Vat dyeing involves immersion/removal cycles but not a true closed loop'),
            'AGRICULTURAL':   (0.0, 'Agriculture is seasonal linear, not circulatory'),
        },
    },
    'F16_line_boundary_memory_reset': {
        'description': 'Hard memory reset at control block boundaries; cross-line MI = 0.52 bits (below null 0.72)',
        'evidence': 'C670, FINGERPRINT_UNIQUENESS F10',
        'scores': {
            'DISTILLATION':   (1.0, 'Each fraction/operation starts fresh from current apparatus state, not from history'),
            'FERMENTATION':   (0.0, 'Fermentation is continuous; no memory resets between stages'),
            'METALLURGY':     (0.5, 'Each heating cycle somewhat independent but thermal history affects metal'),
            'GLASS_WORKING':  (0.0, 'Glass state carries forward continuously; no clean resets'),
            'PHARMACOLOGICAL':(0.0, 'Each step depends on what was added before; no resets'),
            'RITUAL_CALENDAR':(0.0, 'Calendar is continuous; no memory resets'),
            'TEXTILE_DYEING': (0.5, 'Rinse between dye baths provides partial reset'),
            'AGRICULTURAL':   (0.0, 'Soil state carries between seasons'),
        },
    },
    'F17_link_monitoring_phase': {
        'description': 'LINK operator (13.2% density) encodes monitoring/observation phases, mean position 0.476',
        'evidence': 'Monitoring before action, C609, C813',
        'scores': {
            'DISTILLATION':   (1.0, 'Constant monitoring between interventions: watch the still, check the drip, smell the output'),
            'FERMENTATION':   (0.5, 'Some monitoring (check gravity, taste, smell) but infrequent (daily not continuous)'),
            'METALLURGY':     (0.0, 'Metallurgy has less monitoring between actions (fire-and-wait pattern)'),
            'GLASS_WORKING':  (0.0, 'Glass working is continuous action, not monitor-then-act'),
            'PHARMACOLOGICAL':(0.0, 'No continuous monitoring in compounding'),
            'RITUAL_CALENDAR':(0.0, 'No physical monitoring'),
            'TEXTILE_DYEING': (0.5, 'Some monitoring (check color) but less frequent than distillation'),
            'AGRICULTURAL':   (0.0, 'Monitoring is seasonal/weekly, not within-process'),
        },
    },
    'F18_e_recovery_dominance': {
        'description': '54.7% of recovery paths through e (STABILITY_ANCHOR); cooling is primary recovery',
        'evidence': 'C105, C634',
        'scores': {
            'DISTILLATION':   (1.0, 'Cooling IS the primary recovery in distillation: reduce heat, let system equilibrate'),
            'FERMENTATION':   (0.0, 'No cooling-as-recovery in fermentation'),
            'METALLURGY':     (0.0, 'Metallurgy recovery is not cooling-dominated; re-heating is equally common'),
            'GLASS_WORKING':  (0.0, 'Glass recovery is not cooling-dominated (re-heating broken piece is standard)'),
            'PHARMACOLOGICAL':(0.0, 'No thermal recovery in pharmacy'),
            'RITUAL_CALENDAR':(0.0, 'No physical recovery'),
            'TEXTILE_DYEING': (0.0, 'Recovery in dyeing is not cooling-dominated'),
            'AGRICULTURAL':   (0.0, 'No thermal recovery in agriculture'),
        },
    },
    'F19_folio_vocabulary_uniqueness': {
        'description': 'Each folio/program has unique MIDDLE vocabulary; different runs use different material profiles',
        'evidence': 'C178, C531',
        'scores': {
            'DISTILLATION':   (1.0, 'Different distillation runs process different materials with distinct properties'),
            'FERMENTATION':   (0.5, 'Different ferments use different ingredients but vocabulary is much smaller'),
            'METALLURGY':     (0.5, 'Different ores have different properties but the vocabulary is smaller'),
            'GLASS_WORKING':  (0.0, 'Glass recipes are relatively uniform; limited vocabulary variation'),
            'PHARMACOLOGICAL':(0.5, 'Different medicines use different ingredients; moderate vocabulary'),
            'RITUAL_CALENDAR':(0.0, 'No material vocabulary per entry'),
            'TEXTILE_DYEING': (0.5, 'Different dyes have different properties but limited vocabulary'),
            'AGRICULTURAL':   (0.0, 'Limited crop vocabulary; not per-field unique'),
        },
    },
    'F20_design_asymmetry': {
        'description': 'Hazard topology is clamped (same everywhere) but recovery is free (varies per folio)',
        'evidence': 'C458, C636',
        'scores': {
            'DISTILLATION':   (1.0, 'Physics of failure is universal (same for all materials) but recovery depends on what you are distilling'),
            'FERMENTATION':   (0.0, 'Fermentation failure and recovery are both material-dependent, not asymmetric'),
            'METALLURGY':     (0.0, 'Both hazards and recovery vary by metal type; not clearly asymmetric'),
            'GLASS_WORKING':  (0.0, 'Both failure modes and recovery are glass-type dependent'),
            'PHARMACOLOGICAL':(0.0, 'Both errors and corrections are recipe-specific'),
            'RITUAL_CALENDAR':(0.0, 'No physical design asymmetry'),
            'TEXTILE_DYEING': (0.0, 'Failure and recovery both dye-dependent'),
            'AGRICULTURAL':   (0.0, 'Both failure and recovery are crop/season dependent'),
        },
    },
}


def main():
    print("=" * 70)
    print("T4: ALTERNATIVE DOMAIN COMPATIBILITY MATRIX")
    print("=" * 70)

    n_features = len(COMPATIBILITY)
    n_domains = len(DOMAINS)
    print(f"\nFeatures: {n_features}")
    print(f"Domains: {n_domains}")

    # ---- Compute per-domain scores ----
    domain_scores = {}
    domain_details = {}

    for domain_name in DOMAINS:
        total = 0.0
        feature_details = {}
        for feat_name, feat_data in COMPATIBILITY.items():
            score, reason = feat_data['scores'][domain_name]
            total += score
            feature_details[feat_name] = {
                'score': score,
                'reason': reason,
            }
        normalized = total / n_features
        domain_scores[domain_name] = {
            'total_score': round(total, 1),
            'normalized': round(normalized, 4),
        }
        domain_details[domain_name] = feature_details

    # ---- Rankings ----
    rankings = sorted(
        [(name, scores['total_score'], scores['normalized'])
         for name, scores in domain_scores.items()],
        key=lambda x: -x[1]
    )

    print("\n--- Domain Rankings ---")
    for rank, (name, total, norm) in enumerate(rankings, 1):
        marker = " <-- TARGET" if name == 'DISTILLATION' else ""
        print(f"  {rank}. {name}: {total}/{n_features} ({norm:.1%}){marker}")

    # ---- Exclusion gap ----
    distillation_score = domain_scores['DISTILLATION']['normalized']
    alternatives = [(name, scores['normalized'])
                    for name, scores in domain_scores.items()
                    if name != 'DISTILLATION']
    best_alt_name, best_alt_score = max(alternatives, key=lambda x: x[1])
    exclusion_gap = round(distillation_score - best_alt_score, 4)

    print(f"\n--- Exclusion Analysis ---")
    print(f"  Distillation: {distillation_score:.1%}")
    print(f"  Best alternative: {best_alt_name} at {best_alt_score:.1%}")
    print(f"  Exclusion gap: {exclusion_gap:.1%}")

    # ---- Killer features ----
    killer_features = []
    for feat_name, feat_data in COMPATIBILITY.items():
        dist_score = feat_data['scores']['DISTILLATION'][0]
        if dist_score < 1.0:
            continue
        all_alt_low = all(
            feat_data['scores'][d][0] <= 0.5
            for d in DOMAINS if d != 'DISTILLATION'
        )
        if all_alt_low:
            killer_features.append(feat_name)

    print(f"\n--- Killer Features (distillation=1, all alts<=0.5) ---")
    for kf in killer_features:
        print(f"  {kf}")
    print(f"  Total: {len(killer_features)}/{n_features}")

    # ---- Feature discrimination ----
    feature_discrimination = {}
    for feat_name, feat_data in COMPATIBILITY.items():
        n_compat = 0
        n_partial = 0
        n_excluded = 0
        for d in DOMAINS:
            if d == 'DISTILLATION':
                continue
            score = feat_data['scores'][d][0]
            if score >= 1.0:
                n_compat += 1
            elif score >= 0.5:
                n_partial += 1
            else:
                n_excluded += 1
        feature_discrimination[feat_name] = {
            'n_compatible': n_compat,
            'n_partial': n_partial,
            'n_excluded': n_excluded,
        }

    # ---- Closest features for best alternative ----
    closest_features = []
    for feat_name, feat_data in COMPATIBILITY.items():
        alt_score = feat_data['scores'][best_alt_name][0]
        if alt_score >= 0.5:
            closest_features.append({
                'feature': feat_name,
                'score': alt_score,
                'reason': feat_data['scores'][best_alt_name][1],
            })

    # ---- Verdict ----
    all_below_50 = all(s < 0.50 for _, s in alternatives)
    all_below_65 = all(s < 0.65 for _, s in alternatives)

    if all_below_50 and exclusion_gap >= 0.30:
        verdict = 'EXCLUDED'
    elif all_below_65 and exclusion_gap >= 0.15:
        verdict = 'WEAKLY_EXCLUDED'
    else:
        verdict = 'NOT_EXCLUDED'

    explanation = (
        f"Distillation scores {distillation_score:.1%}. "
        f"Best alternative ({best_alt_name}) scores {best_alt_score:.1%}. "
        f"Exclusion gap: {exclusion_gap:.1%}. "
        f"Killer features: {len(killer_features)}/{n_features}. "
    )
    if verdict == 'EXCLUDED':
        explanation += "All alternatives below 50% with gap >= 30%. The structural fingerprint is uniquely compatible with thermal circulatory distillation."
    elif verdict == 'WEAKLY_EXCLUDED':
        explanation += "All alternatives below 65% with gap >= 15%. Distillation is structurally favored but not uniquely compatible."
    else:
        explanation += f"Domain {best_alt_name} scores >= 65%. The fingerprint is not uniquely thermal."

    # ---- Compile results ----
    results = {
        'test': 'T4_domain_compatibility_matrix',
        'n_features': n_features,
        'n_domains': n_domains,
        'domain_scores': domain_scores,
        'domain_details': domain_details,
        'rankings': [
            {'rank': i + 1, 'domain': name, 'total_score': total, 'normalized': norm}
            for i, (name, total, norm) in enumerate(rankings)
        ],
        'exclusion_gap': exclusion_gap,
        'best_alternative': {
            'domain': best_alt_name,
            'score': best_alt_score,
            'closest_features': closest_features,
        },
        'killer_features': killer_features,
        'n_killer_features': len(killer_features),
        'feature_discrimination': feature_discrimination,
        'verdict': verdict,
        'explanation': explanation,
    }

    # ---- Save ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't4_domain_compatibility.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"VERDICT: {verdict}")
    print(f"  Distillation: {distillation_score:.1%}")
    print(f"  Best alternative: {best_alt_name} at {best_alt_score:.1%}")
    print(f"  Exclusion gap: {exclusion_gap:.1%}")
    print(f"  Killer features: {len(killer_features)}/{n_features}")
    print(f"  {explanation}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
