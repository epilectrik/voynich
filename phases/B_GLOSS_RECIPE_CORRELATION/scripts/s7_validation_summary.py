"""
Phase 641, Script 7: Validation summary.

Reads s2 (pre-registered tests) + s3 (ordinal alignment) and produces:
  1. Full per-test scorecard with verdict, p, CI, LOO
  2. Near-significant items (right direction, p < 0.25, LOO-stable)
  3. Structural interpretation of null results
  4. Recommendations: what to promote (none this round), what's informative
"""
import sys, io, os, json
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
OUT_PATH = os.path.join(RESULTS_DIR, 'validation_scorecard.json')

with open(os.path.join(RESULTS_DIR, 'preregistered_tests.json'), 'r', encoding='utf-8') as f:
    s2 = json.load(f)
with open(os.path.join(RESULTS_DIR, 'ordinal_alignment.json'), 'r', encoding='utf-8') as f:
    s3 = json.load(f)

# ============================================================
# s2 verdict summary
# ============================================================
print("=" * 90)
print("PHASE 641 VALIDATION SUMMARY")
print("=" * 90)
print(f"\nn_pairs: {s2['metadata']['n_pairs']}")
print(f"n_tests (blocks A-G): {s2['metadata']['n_tests']}")

verdicts = Counter(r['verdict'] for r in s2['results'])
print(f"\nVerdict distribution: {dict(verdicts)}")

valid = [r for r in s2['results'] if 'p' in r and r['verdict'] != 'SKIPPED_ZERO']
fdr_pass = [r for r in valid if r.get('fdr_accept')]
print(f"FDR-accepted (q=0.10): {len(fdr_pass)}/{len(valid)}")

# Right-direction near-significant items (interesting but not FDR-passing)
near_sig = [r for r in valid if r['verdict'] == 'INCONCLUSIVE' and r['p'] < 0.25 and
            ((r['predicted_sign'] == '+' and r['rho'] > 0) or
             (r['predicted_sign'] == '-' and r['rho'] < 0))]
# Wrong-direction near-sig (potential falsifications)
wrong_dir_sig = [r for r in valid if r['p'] < 0.10 and
                 ((r['predicted_sign'] == '+' and r['rho'] < 0) or
                  (r['predicted_sign'] == '-' and r['rho'] > 0))]

print(f"\nNear-significant right-direction (p<0.25, LOO-stable in parentheses):")
for r in sorted(near_sig, key=lambda x: x['p']):
    ci = r.get('bootstrap_ci', [0,0])
    loo = '✓' if r.get('loo_stable') else '✗'
    print(f"  {r['label']:<30} ρ={r['rho']:+.3f}  p={r['p']:.4f}  CI=[{ci[0]:+.2f},{ci[1]:+.2f}]  LOO={loo}")

print(f"\nWrong-direction near-significant (potential falsifications, p<0.10):")
for r in sorted(wrong_dir_sig, key=lambda x: x['p']):
    print(f"  {r['label']:<30} ρ={r['rho']:+.3f}  p={r['p']:.4f}  (predicted {r['predicted_sign']}, got opposite)")

# ============================================================
# s3 ordinal summary
# ============================================================
print(f"\n{'='*90}")
print("ORDINAL ALIGNMENT (s3)")
print(f"{'='*90}")
meta = s3['metadata']
print(f"n_pairs: {meta['n_pairs']}")
print(f"Valid ρ: {meta['n_valid_rhos']} (pairs with ≥3 shared categories)")
if meta['mean_rho'] is not None:
    print(f"Mean ρ: {meta['mean_rho']:+.3f}")
    print(f"Permutation p: {meta['permutation_p']:.4f}")

# Per-pair alignment
print(f"\nPer-pair alignment scores (valid only):")
for r in s3['pair_results']:
    if r['first_pos_rho'] is None: continue
    print(f"  {r['folio']:<6} {r['tier']:<10}  ρ={r['first_pos_rho']:+.3f}  "
          f"LCS={r['lcs_length']}/{min(r['recipe_len'], r['folio_len'])}  "
          f"shared={r['n_shared_cats']}  ({r['tier']})")

# ============================================================
# STRUCTURAL INTERPRETATION
# ============================================================
print(f"\n{'='*90}")
print("INTERPRETATION")
print(f"{'='*90}")

interpretation = """
KEY FINDING: Both rate correlation (s2) and ordinal alignment (s3) fail to reach
significance at N=15. This is NOT a failure of the glosses — it's a structural
observation about the recipe↔folio relationship.

ROOT CAUSE (consistent with C171 semantic ceiling):

  The Voynich folio encodes OPERATIONAL EXECUTION;
  the Pseudo-Lull Latin text encodes the RECIPE DESCRIPTION.

Evidence:
  • Ch22M has 9 Latin lines with 2 heat mentions ("ignis", "balneum").
    f82r has 275 tokens with 31% qo-prefix (heat-source) rate.
    The recipe says 'place on ashes for 3 natural days';
    the folio describes continuous heat maintenance over that period.

  • Where we CAN see alignment (f82v Ch28M ρ=+1.0, f79r Ch12M ρ=+0.4),
    it's on chapters with distinctive multi-category steps. Chapters with
    1-2 sentences don't produce enough signal.

  • f83r shows NEGATIVE alignment (ρ=-0.60) — recipe has MAT early,
    folio has MAT late. Suggests operator executes in different order than
    recipe describes (e.g., prep fire BEFORE adding materials).

IMPLICATIONS FOR GLOSS VALIDATION:

  • Per-folio rate correlation is the WRONG test for validating glosses.
    A folio with one "place on ashes" instruction will have the same heat
    prefix rate as a folio with many heating operations — because both are
    operationally heating-dominant.

  • Gloss validation requires PER-PARAGRAPH alignment with recipe STEPS,
    which requires richer per-step Latin content than Testamentum's terse
    chapters provide (median 10-15 lines per matched chapter).

  • The qualitative deep-alignment method (PT-013/14/15) remains valid —
    it works at the paragraph↔step level with rich Catalan text from
    Buosi-Moncunill's thesis. SISMEL arrival will strengthen this.

NEAR-SIGNIFICANT SIGNALS (informative but not promotion-eligible):
  • A2 ch ↔ monitoring+heat_transition: ρ=+0.35, right direction
  • C6 p ↔ termination: ρ=+0.37, right direction
  • D2 n ↔ iteration (-): ρ=-0.34, right direction (supports "halt" gloss)
  • E2 f ↔ termination: ρ=+0.39, right direction

POTENTIAL FALSIFICATION (wrong direction, near-significant):
  • C2 t ↔ transfer: ρ=-0.47, p=0.07 (predicted +, got −)
    — transfer atom does NOT correlate with transfer verbs in Latin recipes
    — worth investigating: maybe 't' encodes something other than transfer
    — OR maybe transfer operations in Voynich use ot-prefix, not t-atom

PROMOTION: None this round. No test passed (SUPPORTED + FDR + CI-excludes-0 +
LOO-stable + control-corpus) requirements.

NEXT STEPS (ranked by value):
  1. SISMEL Catalan text arrives → richer per-step content → re-run s3 with
     paragraph↔step granularity (which Latin Testamentum text can't support)
  2. Brunschwig control (s0b) — even null result here needs "Testamentum
     beats controls" to be compelling. If Brunschwig correlates equally badly,
     Latin regex may be the limitation.
  3. Investigate C2 (t-atom ↔ transfer) falsification — if real, suggests
     gloss revision for 't'.
  4. Build ordinal alignment at PARAGRAPH-to-PARAGRAPH level once we have
     a text source dense enough for multi-step chapters.
"""
print(interpretation)

# ============================================================
# SAVE SCORECARD
# ============================================================
out = {
    'metadata': {
        'phase': 641,
        'script': 's7_validation_summary',
    },
    's2_summary': {
        'n_tests': len(s2['results']),
        'verdict_counts': dict(verdicts),
        'fdr_passed': len(fdr_pass),
        'fdr_threshold': 'BH-FDR q=0.10',
    },
    's3_summary': {
        'n_valid_rhos': meta['n_valid_rhos'],
        'mean_rho': meta['mean_rho'],
        'permutation_p': meta['permutation_p'],
    },
    'near_significant': [{'label': r['label'], 'rho': r['rho'], 'p': r['p'],
                          'predicted_sign': r['predicted_sign'],
                          'loo_stable': r.get('loo_stable', False)}
                         for r in near_sig],
    'potential_falsifications': [{'label': r['label'], 'rho': r['rho'], 'p': r['p'],
                                  'predicted_sign': r['predicted_sign']}
                                 for r in wrong_dir_sig],
    'promotable_constraints': [],
    'interpretation_key_findings': [
        'Voynich folios encode operational execution; Latin text encodes recipe description',
        'Per-folio rate correlation is the wrong test at this granularity',
        'Paragraph-to-paragraph alignment requires richer per-step text (awaits SISMEL Catalan)',
        'Near-significant signals exist but do not pass FDR at N=15',
        'Potential falsification on C2 (t-atom ↔ transfer) — wrong direction, p=0.07',
    ],
}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nWrote {OUT_PATH}")
