"""
11_integrated_verdict.py

Synthesize results from all 10 tests into an integrated verdict.

Verdict categories:
- ARTIFACT: Tests 1+6 explain bimodality via confounds; GMM prefers 1-component
- CONTEXT_MODULATED: Bimodality explained by context (Test 2) or hazard/safe (Test 9)
- DUAL_STATE: GMM prefers 2-component (Test 7); bimodality persists after controls
- MIXED: Some MIDDLEs dual-state, others context-modulated
"""
import sys
import json
from pathlib import Path

results_dir = Path(__file__).resolve().parent.parent / "results"

# ============================================================
# Load all results
# ============================================================
test_files = {
    '01_line_length': '01_line_length_artifact.json',
    '02_context_kurtosis': '02_context_stratified_kurtosis.json',
    '03_anchoring': '03_positional_anchoring_taxonomy.json',
    '04_section_t': '04_section_t_anomaly.json',
    '05_subsequences': '05_multi_fl_subsequences.json',
    '06_regression': '06_residual_regression.json',
    '07_gmm': '07_gaussian_mixture.json',
    '08_forward_bias': '08_forward_bias_decomposition.json',
    '09_hazard_safe': '09_hazard_safe_bimodality.json',
    '10_prefix': '10_prefix_fl_mode_interaction.json',
}

results = {}
missing = []
for key, filename in test_files.items():
    path = results_dir / filename
    if path.exists():
        with open(path) as f:
            results[key] = json.load(f)
        print(f"  Loaded {key}: verdict = {results[key].get('verdict', 'N/A')}")
    else:
        missing.append(key)
        print(f"  MISSING: {filename}")

if missing:
    print(f"\nWARNING: {len(missing)} test results missing: {missing}")

# ============================================================
# Score each dimension
# ============================================================
scores = {}

# 1. Line-length artifact
v = results.get('01_line_length', {}).get('verdict', '')
scores['artifact_line_length'] = 1 if v == 'ARTIFACT' else 0
print(f"\n[01] Line length artifact: {v} -> {'artifact' if scores['artifact_line_length'] else 'NOT artifact'}")

# 2. Context-driven bimodality
v = results.get('02_context_kurtosis', {}).get('verdict', '')
scores['context_driven'] = 1 if v == 'CONTEXT_DRIVEN' else 0
print(f"[02] Context kurtosis: {v} -> {'context-driven' if scores['context_driven'] else 'intrinsic'}")

# 3. Anchoring partition
v = results.get('03_anchoring', {}).get('verdict', '')
scores['clear_partition'] = 1 if v == 'CLEAR_PARTITION' else 0
print(f"[03] Anchoring: {v} -> {'partitioned' if scores['clear_partition'] else 'uniform'}")

# 4. Section T
v = results.get('04_section_t', {}).get('verdict', '')
scores['section_t_artifact'] = 1 if v == 'SAMPLE_SIZE_ARTIFACT' else 0
print(f"[04] Section T: {v} -> {'artifact' if scores['section_t_artifact'] else 'genuine anomaly'}")

# 5. Subsequences
v = results.get('05_subsequences', {}).get('verdict', '')
adj_data = results.get('05_subsequences', {}).get('adjacent_transitions', {})
fwd_ratio = adj_data.get('fwd_bwd_ratio', 0)
scores['strong_forward'] = 1 if fwd_ratio > 2.0 else 0
print(f"[05] Subsequences: {v} (fwd:bwd = {fwd_ratio}:1)")

# 6. Regression
v = results.get('06_regression', {}).get('verdict', '')
r2 = results.get('06_regression', {}).get('model_3_full', {}).get('r_squared', 0)
resid_bimodal = results.get('06_regression', {}).get('bimodal_after_regression', 0)
scores['confounds_explain'] = 1 if v == 'CONFOUNDS_EXPLAIN' else 0
scores['residual_bimodal'] = 1 if resid_bimodal > 5 else 0
print(f"[06] Regression: {v} (R²={r2}, {resid_bimodal} MIDDLEs bimodal after regression)")

# 7. GMM
v = results.get('07_gmm', {}).get('verdict', '')
pct_2comp = results.get('07_gmm', {}).get('pct_prefer_2', 0)
scores['gmm_dual'] = 1 if pct_2comp > 0.50 else 0
scores['gmm_single'] = 1 if pct_2comp < 0.30 else 0
print(f"[07] GMM: {v} ({pct_2comp:.0%} prefer 2-component)")

# 8. Forward bias decomposition
v = results.get('08_forward_bias', {}).get('verdict', '')
scores['bias_subtype_driven'] = 1 if v == 'SUBTYPE_DRIVEN' else 0
print(f"[08] Forward bias: {v}")

# 9. Hazard/safe bimodality
v = results.get('09_hazard_safe', {}).get('verdict', '')
scores['c773_explains'] = 1 if v == 'C773_EXPLAINS' else 0
scores['c773_independent'] = 1 if v == 'INDEPENDENT' else 0
print(f"[09] Hazard/safe: {v}")

# 10. PREFIX mode
v = results.get('10_prefix', {}).get('verdict', '')
scores['prefix_selects'] = 1 if v == 'PREFIX_SELECTS_MODE' else 0
print(f"[10] PREFIX mode: {v}")

# ============================================================
# Integrated verdict logic
# ============================================================
print(f"\n{'='*60}")
print("INTEGRATED SCORING")

# ARTIFACT evidence
artifact_score = (scores['artifact_line_length'] +
                  scores['confounds_explain'] +
                  scores['gmm_single'])
print(f"  ARTIFACT score: {artifact_score}/3 "
      f"(line_length={scores['artifact_line_length']}, "
      f"confounds={scores['confounds_explain']}, "
      f"gmm_single={scores['gmm_single']})")

# CONTEXT_MODULATED evidence
context_score = (scores['context_driven'] +
                 scores['c773_explains'] +
                 scores['section_t_artifact'])
print(f"  CONTEXT_MODULATED score: {context_score}/3 "
      f"(context={scores['context_driven']}, "
      f"c773={scores['c773_explains']}, "
      f"section_t={scores['section_t_artifact']})")

# DUAL_STATE evidence
dual_score = (scores['gmm_dual'] +
              scores['residual_bimodal'] +
              scores['c773_independent'] +
              scores['prefix_selects'] +
              scores['clear_partition'])
print(f"  DUAL_STATE score: {dual_score}/5 "
      f"(gmm={scores['gmm_dual']}, "
      f"resid_bimodal={scores['residual_bimodal']}, "
      f"c773_indep={scores['c773_independent']}, "
      f"prefix={scores['prefix_selects']}, "
      f"partition={scores['clear_partition']})")

# Decision
if artifact_score >= 2:
    verdict = "ARTIFACT"
    confidence = "HIGH" if artifact_score == 3 else "MODERATE"
elif dual_score >= 3:
    verdict = "DUAL_STATE"
    confidence = "HIGH" if dual_score >= 4 else "MODERATE"
elif context_score >= 2:
    verdict = "CONTEXT_MODULATED"
    confidence = "HIGH" if context_score == 3 else "MODERATE"
elif dual_score >= 2 and context_score >= 1:
    verdict = "MIXED"
    confidence = "MODERATE"
elif dual_score >= 1 and context_score >= 1:
    verdict = "MIXED"
    confidence = "LOW"
else:
    verdict = "INCONCLUSIVE"
    confidence = "LOW"

# Build explanation
explanation_parts = []
if scores['artifact_line_length']:
    explanation_parts.append("Line length is an artifact factor")
if scores['context_driven']:
    explanation_parts.append("Context mixing drives some bimodality")
if scores['c773_explains']:
    explanation_parts.append("Hazard/safe split (C773) explains bimodality for some MIDDLEs")
if scores['c773_independent']:
    explanation_parts.append("Bimodality persists within hazard/safe classes")
if scores['gmm_dual']:
    explanation_parts.append(f"GMM prefers 2-component for {pct_2comp:.0%} of MIDDLEs")
if scores['residual_bimodal']:
    explanation_parts.append(f"{resid_bimodal} MIDDLEs remain bimodal after regression")
if scores['prefix_selects']:
    explanation_parts.append("PREFIX choice shifts FL position significantly")
if scores['clear_partition']:
    explanation_parts.append("FL MIDDLEs partition into RIGID and FLEXIBLE types")

explanation = ". ".join(explanation_parts) + "." if explanation_parts else "Insufficient evidence for any conclusion."

print(f"\n{'='*60}")
print(f"INTEGRATED VERDICT: {verdict}")
print(f"CONFIDENCE: {confidence}")
print(f"EXPLANATION: {explanation}")

# ============================================================
# Per-test summary table
# ============================================================
test_summary = []
for key, filename in test_files.items():
    r = results.get(key, {})
    test_summary.append({
        'test': key,
        'verdict': r.get('verdict', 'MISSING'),
        'explanation': r.get('explanation', ''),
    })

result = {
    'tests_loaded': len(results),
    'tests_missing': missing,
    'scores': scores,
    'artifact_score': artifact_score,
    'context_score': context_score,
    'dual_score': dual_score,
    'integrated_verdict': verdict,
    'confidence': confidence,
    'explanation': explanation,
    'test_summary': test_summary,
}

out_path = results_dir / "11_integrated_verdict.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
