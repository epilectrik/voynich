"""
Phase 445b: APPARATUS PROFILE SCORING
========================================
Bottom-up approach: define apparatus-specific vocabulary profiles from
Brunschwig, score each folio against them, and see what the data says.

Instead of unsupervised clustering on all PM pairs, we:
  1. Define apparatus marker vocabularies from domain knowledge
  2. Compute co-occurrence of marker sets at the folio level
  3. Score each folio against each apparatus profile
  4. See whether REGIME aligns with apparatus, or if there's a second axis
  5. Look at folio-level vocabulary fingerprints for the strongest markers

The goal is to FIND THE ANSWER, not test a hypothesis.
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "APPARATUS_VOCABULARY_CLASSIFICATION" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
REGIME_PATH = ROOT / "data" / "regime_folio_mapping.json"


# ============================================================
# APPARATUS PROFILES (from Brunschwig / GLOSS_RESEARCH)
# ============================================================
#
# Each profile defines MIDDLEs and PREFIXes expected for that apparatus.
# Scores are computed as: (count of profile tokens) / (total tokens).
#
# These are NOT mutually exclusive — a folio could score high on multiple
# profiles if it uses multiple apparatus stages.

APPARATUS_PROFILES = {
    'DISTILLATION': {
        'description': 'Open distillation via alembic — drive off volatiles, collect condensate',
        'marker_middles': {'t', 'od', 'te', 'eol'},     # drive, collect, rapid-gather, sustain-output
        'marker_prefixes': {'qo'},                        # energy domain
        'anti_markers': set(),                            # nothing specifically excluded
    },
    'SEALED_VESSEL': {
        'description': 'Sealed/circulatory apparatus — seal vessel, extended processing, unseal',
        'marker_middles': {'aii', 'ok', 'ee', 'eey', 'eeol'},  # unseal, seal, extended-cool, overnight
        'marker_prefixes': {'ok'},                         # vessel domain
        'anti_markers': set(),
    },
    'DIRECT_FIRE': {
        'description': 'Direct fire / per ignem — intense heat, direct operations',
        'marker_middles': {'ck', 'kc', 'te'},             # direct-heat, intense-heat-seal, rapid-gather
        'marker_prefixes': set(),
        'anti_markers': set(),
    },
    'PRECISION': {
        'description': 'Precision / controlled — tight tolerance, sequential steps',
        'marker_middles': {'ek', 's', 'm', 'ep'},         # precision, sequence, precision-marker, precision-cool
        'marker_prefixes': {'kch', 'ct'},                  # precision-heat, control
        'anti_markers': set(),
    },
    'SUSTAINED_HEAT': {
        'description': 'Sustained heat / balneum marie style — gentle prolonged heating',
        'marker_middles': {'ke', 'eeo', 'eeol', 'ee'},    # sustained-heat, monitored-cool, overnight, extended-cool
        'marker_prefixes': {'da'},                          # setup/infrastructure
        'anti_markers': set(),
    },
}

# Co-occurrence pairs: marker combinations that indicate specific apparatus
CO_OCCURRENCE_PAIRS = [
    # (name, middle_A, middle_B, interpretation)
    ('seal_unseal', 'ok', 'aii', 'Sealed vessel cycle: seal then unseal'),
    ('drive_collect', 't', 'od', 'Distillation cycle: drive off then collect'),
    ('drive_sustain', 't', 'eol', 'Active distillation: drive off with sustained output'),
    ('heat_overnight', 'ke', 'eeol', 'Sustained heat then overnight standing'),
    ('direct_collect', 'ck', 'od', 'Direct fire collection'),
    ('seal_cool', 'ok', 'ee', 'Seal then extended cool (circulatory)'),
    ('heat_measure', 'k', 'edy', 'Generic heat-measure cycle (baseline)'),
    ('precision_sequence', 'ek', 's', 'Precision sequential steps'),
]


def load_regime_map():
    with open(REGIME_PATH, encoding='utf-8') as f:
        raw = json.load(f)
    assignments = raw.get('regime_assignments', raw)
    return {k: v.get('regime', 'UNK') if isinstance(v, dict) else v
            for k, v in assignments.items()}


def extract_folio_vocabulary():
    """Extract per-folio vocabulary: middles, prefixes, words, and token counts."""
    tx = Transcript()
    morph = Morphology()

    folio_middles = defaultdict(Counter)       # folio -> Counter of middles
    folio_prefixes = defaultdict(Counter)      # folio -> Counter of prefixes
    folio_words = defaultdict(Counter)         # folio -> Counter of full words
    folio_token_counts = Counter()
    folio_sections = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        folio = token.folio
        folio_token_counts[folio] += 1
        folio_sections[folio] = token.section

        m = morph.extract(w)
        mid = m.middle or '_EMPTY_'
        pfx = m.prefix or 'NONE'

        folio_middles[folio][mid] += 1
        folio_prefixes[folio][pfx] += 1
        folio_words[folio][w] += 1

    return (dict(folio_middles), dict(folio_prefixes), dict(folio_words),
            dict(folio_token_counts), folio_sections)


def score_apparatus_profile(profile, folio_middles, folio_prefixes, total):
    """Score a folio against an apparatus profile.

    Returns:
        score: fraction of tokens matching profile markers
        middle_hits: Counter of which marker middles were found
        prefix_hits: Counter of which marker prefixes were found
    """
    middle_hits = Counter()
    prefix_hits = Counter()

    for mid in profile['marker_middles']:
        c = folio_middles.get(mid, 0)
        if c > 0:
            middle_hits[mid] = c

    for pfx in profile['marker_prefixes']:
        c = folio_prefixes.get(pfx, 0)
        if c > 0:
            prefix_hits[pfx] = c

    hit_count = sum(middle_hits.values()) + sum(prefix_hits.values())
    score = hit_count / total if total > 0 else 0
    return score, middle_hits, prefix_hits


def compute_co_occurrence(folio_middles):
    """Check if a folio has both members of a co-occurrence pair."""
    results = {}
    for name, mid_a, mid_b, interp in CO_OCCURRENCE_PAIRS:
        count_a = folio_middles.get(mid_a, 0)
        count_b = folio_middles.get(mid_b, 0)
        both = count_a > 0 and count_b > 0
        results[name] = {
            'a': mid_a, 'b': mid_b,
            'count_a': count_a, 'count_b': count_b,
            'both_present': both,
            'min_count': min(count_a, count_b),
        }
    return results


def main():
    start = time.time()
    print("Phase 445b: APPARATUS PROFILE SCORING")
    print("=" * 70)

    regime_map = load_regime_map()
    folio_middles, folio_prefixes, folio_words, folio_counts, folio_sections = extract_folio_vocabulary()

    folios = sorted(f for f in folio_counts if folio_counts[f] >= 50)
    print(f"Folios: {len(folios)} (>= 50 tokens)")

    # ============================================================
    # PART 1: Score each folio against each apparatus profile
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 1: APPARATUS PROFILE SCORES PER FOLIO")
    print("=" * 70)

    folio_scores = {}
    profile_names = sorted(APPARATUS_PROFILES.keys())

    for f in folios:
        folio_scores[f] = {}
        for pname in profile_names:
            profile = APPARATUS_PROFILES[pname]
            score, mid_hits, pfx_hits = score_apparatus_profile(
                profile, folio_middles[f], folio_prefixes[f], folio_counts[f])
            folio_scores[f][pname] = {
                'score': score,
                'middle_hits': dict(mid_hits),
                'prefix_hits': dict(pfx_hits),
            }

    # Summary: mean score per profile per REGIME
    print(f"\n{'Profile':<20} {'Overall':<10} {'R1':<10} {'R2':<10} {'R3':<10} {'R4':<10}")
    print("-" * 70)

    regime_profile_means = {}
    for pname in profile_names:
        all_scores = [folio_scores[f][pname]['score'] for f in folios]
        regime_scores = defaultdict(list)
        for f in folios:
            r = regime_map.get(f, '?')
            regime_scores[r].append(folio_scores[f][pname]['score'])

        overall = np.mean(all_scores)
        r_means = {}
        row = f"{pname:<20} {overall:<10.4f}"
        for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            m = np.mean(regime_scores[r]) if regime_scores[r] else 0
            r_means[r] = m
            row += f" {m:<10.4f}"
        print(row)
        regime_profile_means[pname] = r_means

    # Dominant profile per folio
    print(f"\n{'Folio':<10} {'REGIME':<12} {'Sec':<4} {'Dominant Profile':<22} {'Score':<8} {'2nd Profile':<22} {'Score':<8}")
    print("-" * 90)

    folio_dominant = {}
    for f in folios:
        ranked = sorted(profile_names, key=lambda p: folio_scores[f][p]['score'], reverse=True)
        dom = ranked[0]
        sec = ranked[1]
        folio_dominant[f] = {
            'dominant': dom,
            'dominant_score': folio_scores[f][dom]['score'],
            'second': sec,
            'second_score': folio_scores[f][sec]['score'],
        }
        r = regime_map.get(f, '?')
        s = folio_sections.get(f, '?')
        print(f"{f:<10} {r:<12} {s:<4} {dom:<22} {folio_scores[f][dom]['score']:<8.4f} "
              f"{sec:<22} {folio_scores[f][sec]['score']:<8.4f}")

    # ============================================================
    # PART 2: Co-occurrence analysis
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 2: CO-OCCURRENCE PAIRS")
    print("=" * 70)

    co_occ_summary = {}
    for name, mid_a, mid_b, interp in CO_OCCURRENCE_PAIRS:
        n_both = 0
        n_a_only = 0
        n_b_only = 0
        n_neither = 0
        regime_both = Counter()

        for f in folios:
            has_a = folio_middles[f].get(mid_a, 0) > 0
            has_b = folio_middles[f].get(mid_b, 0) > 0
            r = regime_map.get(f, '?')
            if has_a and has_b:
                n_both += 1
                regime_both[r] += 1
            elif has_a:
                n_a_only += 1
            elif has_b:
                n_b_only += 1
            else:
                n_neither += 1

        # Fisher exact: is co-occurrence more than expected?
        table = [[n_both, n_a_only], [n_b_only, n_neither]]
        if min(n_both, n_a_only, n_b_only, n_neither) >= 0:
            odds, p = sp_stats.fisher_exact(table, alternative='greater')
        else:
            odds, p = 0, 1

        co_occ_summary[name] = {
            'pair': f"{mid_a}+{mid_b}",
            'interpretation': interp,
            'n_both': n_both,
            'n_a_only': n_a_only,
            'n_b_only': n_b_only,
            'n_neither': n_neither,
            'fisher_odds': round(odds, 3) if odds != float('inf') else 'inf',
            'fisher_p': round(p, 6),
            'regime_both': dict(regime_both),
        }

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {name:<25} {mid_a:>5}+{mid_b:<5}  both={n_both:>3}  "
              f"a_only={n_a_only:>3}  b_only={n_b_only:>3}  neither={n_neither:>3}  "
              f"OR={odds:>6.2f}  p={p:.4f} {sig}")

    # ============================================================
    # PART 3: Regime as apparatus — how well does REGIME predict
    #         the dominant apparatus profile?
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 3: REGIME → APPARATUS ALIGNMENT")
    print("=" * 70)

    # Cross-tabulate REGIME x dominant profile
    regime_profile_ct = defaultdict(Counter)
    for f in folios:
        r = regime_map.get(f, '?')
        dom = folio_dominant[f]['dominant']
        regime_profile_ct[r][dom] += 1

    print(f"\n{'REGIME':<12}", end="")
    for p in profile_names:
        print(f" {p[:12]:<14}", end="")
    print(f" {'Total':<6}")
    print("-" * 90)

    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        print(f"{r:<12}", end="")
        total_r = sum(regime_profile_ct[r].values())
        for p in profile_names:
            c = regime_profile_ct[r].get(p, 0)
            pct = c / total_r * 100 if total_r > 0 else 0
            print(f" {c:>3} ({pct:4.0f}%){'':<4}", end="")
        print(f" {total_r:<6}")

    # ============================================================
    # PART 4: Within-REGIME profile variation
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 4: WITHIN-REGIME PROFILE VARIATION")
    print("=" * 70)
    print("(Do folios within the same REGIME vary in apparatus profile?)")

    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        r_folios = [f for f in folios if regime_map.get(f) == r]
        if len(r_folios) < 3:
            continue

        print(f"\n  {r} ({len(r_folios)} folios):")

        # Compute std of each profile score within this REGIME
        for pname in profile_names:
            scores = [folio_scores[f][pname]['score'] for f in r_folios]
            mean_s = np.mean(scores)
            std_s = np.std(scores)
            min_s = min(scores)
            max_s = max(scores)
            cv = std_s / mean_s if mean_s > 0 else 0
            print(f"    {pname:<20} mean={mean_s:.4f}  std={std_s:.4f}  "
                  f"range=[{min_s:.4f}, {max_s:.4f}]  CV={cv:.2f}")

        # Find folios that deviate most from REGIME mean
        # Use combined profile vector distance
        regime_mean_vec = np.array([np.mean([folio_scores[f][p]['score'] for f in r_folios])
                                    for p in profile_names])
        deviations = []
        for f in r_folios:
            vec = np.array([folio_scores[f][p]['score'] for p in profile_names])
            dist = np.linalg.norm(vec - regime_mean_vec)
            deviations.append((f, dist, folio_dominant[f]['dominant']))
        deviations.sort(key=lambda x: x[1], reverse=True)
        if deviations:
            print(f"    Most atypical: {deviations[0][0]} (dist={deviations[0][1]:.4f}, "
                  f"dom={deviations[0][2]})")

    # ============================================================
    # PART 5: Specific marker MIDDLE distribution
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 5: KEY MARKER MIDDLES — FOLIO PRESENCE/ABSENCE")
    print("=" * 70)

    key_middles = ['t', 'od', 'te', 'eol', 'ok', 'aii', 'ck', 'kc',
                   'ek', 's', 'ke', 'eeol', 'ee', 'eey']

    print(f"\n{'Middle':<8} {'Total':<8} {'Folios':<8} {'%Folios':<10} "
          f"{'R1':<10} {'R2':<10} {'R3':<10} {'R4':<10}")
    print("-" * 80)

    middle_folio_presence = {}
    for mid in key_middles:
        total = sum(folio_middles[f].get(mid, 0) for f in folios)
        present = sum(1 for f in folios if folio_middles[f].get(mid, 0) > 0)
        pct = present / len(folios) * 100

        regime_presence = {}
        for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            r_folios = [f for f in folios if regime_map.get(f) == r]
            r_present = sum(1 for f in r_folios if folio_middles[f].get(mid, 0) > 0)
            r_pct = r_present / len(r_folios) * 100 if r_folios else 0
            regime_presence[r] = f"{r_present}/{len(r_folios)}"

        print(f"{mid:<8} {total:<8} {present:<8} {pct:<10.1f} "
              f"{regime_presence['REGIME_1']:<10} {regime_presence['REGIME_2']:<10} "
              f"{regime_presence['REGIME_3']:<10} {regime_presence['REGIME_4']:<10}")

        middle_folio_presence[mid] = {
            'total_count': total,
            'folios_present': present,
            'pct_folios': round(pct, 1),
            'by_regime': regime_presence,
        }

    # ============================================================
    # PART 6: Profile score correlations
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 6: INTER-PROFILE CORRELATIONS")
    print("=" * 70)
    print("(Do profiles co-vary? Positive = same apparatus uses both; Negative = different apparatus)")

    score_matrix = np.zeros((len(folios), len(profile_names)))
    for i, f in enumerate(folios):
        for j, p in enumerate(profile_names):
            score_matrix[i, j] = folio_scores[f][p]['score']

    profile_correlations = {}
    print(f"\n{'Pair':<40} {'rho':>8} {'p':>10}")
    print("-" * 60)
    for i in range(len(profile_names)):
        for j in range(i + 1, len(profile_names)):
            rho, p = sp_stats.spearmanr(score_matrix[:, i], score_matrix[:, j])
            pair_name = f"{profile_names[i]} vs {profile_names[j]}"
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {pair_name:<38} {rho:>8.3f} {p:>10.4f} {sig}")
            profile_correlations[pair_name] = {'rho': round(rho, 4), 'p': round(p, 6)}

    # ============================================================
    # PART 7: Section effect — do sections specialize?
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 7: SECTION → APPARATUS PROFILE")
    print("=" * 70)

    section_profile_means = defaultdict(dict)
    sections = sorted(set(folio_sections.get(f, '?') for f in folios))

    print(f"\n{'Section':<10}", end="")
    for p in profile_names:
        print(f" {p[:14]:<16}", end="")
    print()
    print("-" * 100)

    for sec in sections:
        s_folios = [f for f in folios if folio_sections.get(f) == sec]
        if not s_folios:
            continue
        print(f"{sec:<10}", end="")
        for pname in profile_names:
            scores = [folio_scores[f][pname]['score'] for f in s_folios]
            m = np.mean(scores)
            section_profile_means[sec][pname] = round(m, 4)
            print(f" {m:<16.4f}", end="")
        print(f"  (n={len(s_folios)})")

    # ============================================================
    # PART 8: Strongest apparatus signal — which folios are MOST
    #         distinctly one apparatus type?
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 8: STRONGEST APPARATUS SIGNATURES")
    print("=" * 70)
    print("(Folios where one profile dominates most clearly)")

    folio_clarity = []
    for f in folios:
        scores_sorted = sorted(
            [(p, folio_scores[f][p]['score']) for p in profile_names],
            key=lambda x: x[1], reverse=True)
        top_score = scores_sorted[0][1]
        second_score = scores_sorted[1][1]
        gap = top_score - second_score
        folio_clarity.append((f, scores_sorted[0][0], top_score, gap,
                              regime_map.get(f, '?'), folio_sections.get(f, '?')))

    folio_clarity.sort(key=lambda x: x[3], reverse=True)
    print(f"\n{'Folio':<10} {'Dominant':<22} {'Score':<8} {'Gap':<8} {'REGIME':<12} {'Sec':<4}")
    print("-" * 70)
    for f, dom, score, gap, r, s in folio_clarity[:20]:
        print(f"{f:<10} {dom:<22} {score:<8.4f} {gap:<8.4f} {r:<12} {s:<4}")

    print(f"\n  Weakest signatures (hardest to classify):")
    for f, dom, score, gap, r, s in folio_clarity[-10:]:
        print(f"  {f:<10} {dom:<22} {score:<8.4f} {gap:<8.4f} {r:<12} {s:<4}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    results = {
        '_metadata': {
            'phase': 'APPARATUS_VOCABULARY_CLASSIFICATION',
            'phase_number': '445b',
            'approach': 'bottom-up profile scoring',
            'n_folios': len(folios),
            'profiles_defined': list(APPARATUS_PROFILES.keys()),
        },
        'regime_profile_means': regime_profile_means,
        'section_profile_means': dict(section_profile_means),
        'co_occurrence': co_occ_summary,
        'profile_correlations': profile_correlations,
        'middle_folio_presence': middle_folio_presence,
        'folio_scores': {f: {p: round(folio_scores[f][p]['score'], 6)
                             for p in profile_names} for f in folios},
        'folio_dominant': folio_dominant,
        'folio_clarity_ranking': [
            {'folio': f, 'dominant': dom, 'score': round(score, 4),
             'gap': round(gap, 4), 'regime': r, 'section': s}
            for f, dom, score, gap, r, s in folio_clarity
        ],
    }

    output_path = RESULTS_DIR / 'apparatus_profiles.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - start
    print(f"\nResults saved to {output_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
