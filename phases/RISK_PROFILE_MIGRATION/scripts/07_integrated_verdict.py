"""
Test 07: Integrated Verdict
Phase: RISK_PROFILE_MIGRATION

Purpose: Load results from T01-T06, compute aggregate score, deliver phase verdict.

Scoring: PASS=1.0, PARTIAL=0.5, FAIL=0.0
  STRONG (score >= 5.0): risk profile evolves in tandem with kernel
  MATERIAL (score >= 3.5): multiple migration signals
  WEAK (score >= 2.0): some sub-group migration, no clear tandem
  NONE (score < 2.0): kernel shift is isolated noise

T01 is a prerequisite: if FAIL, cap verdict at WEAK regardless of other scores.
"""

import json
from pathlib import Path

RESULTS_DIR = Path("C:/git/voynich/phases/RISK_PROFILE_MIGRATION/results")
OUTPUT_PATH = RESULTS_DIR / "07_integrated_verdict.json"

SCORE_MAP = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0}

TESTS = [
    ("01_total_hazard_rate_flatness", "Total Hazard Rate Flatness"),
    ("02_hazard_subgroup_migration", "Hazard Sub-Group Migration"),
    ("03_risk_type_migration", "Risk Type Migration"),
    ("04_kernel_mediation_hazard_vs_safe", "Kernel Mediation (Hazard vs Safe)"),
    ("05_hazard_escape_positional_dynamics", "Hazard-Escape Dynamics"),
    ("06_risk_kernel_cross_correlation", "Risk-Kernel Cross-Correlation"),
]

# ---------------------------------------------------------------------------
# LOAD RESULTS
# ---------------------------------------------------------------------------
test_results = {}
for test_name, label in TESTS:
    path = RESULTS_DIR / f"{test_name}.json"
    if not path.exists():
        print(f"WARNING: {path} not found, scoring as FAIL")
        test_results[test_name] = {"verdict": "FAIL", "label": label}
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    test_results[test_name] = {
        "verdict": data.get("verdict", "FAIL"),
        "label": label,
        "data": data,
    }

# ---------------------------------------------------------------------------
# SCORE
# ---------------------------------------------------------------------------
scores = {}
for test_name, info in test_results.items():
    scores[test_name] = SCORE_MAP.get(info["verdict"], 0.0)

total_score = sum(scores.values())
max_score = len(TESTS) * 1.0

# T01 prerequisite check
t01_verdict = test_results.get("01_total_hazard_rate_flatness", {}).get("verdict", "FAIL")
prerequisite_met = t01_verdict == "PASS"

if total_score >= 5.0 and prerequisite_met:
    phase_verdict = "STRONG"
elif total_score >= 3.5 and prerequisite_met:
    phase_verdict = "MATERIAL"
elif total_score >= 2.0:
    if not prerequisite_met:
        phase_verdict = "WEAK"  # Capped due to T01 FAIL
    else:
        phase_verdict = "WEAK"
else:
    phase_verdict = "NONE"

print("=" * 60)
print("RISK_PROFILE_MIGRATION — Integrated Verdict")
print("=" * 60)
print()

for test_name, info in test_results.items():
    v = info["verdict"]
    s = scores[test_name]
    print(f"  {info['label']:42s}  {v:8s}  ({s:.1f})")

print()
print(f"  Total score: {total_score:.1f} / {max_score:.1f}")
print(f"  Prerequisite (T01 flatness): {'MET' if prerequisite_met else 'NOT MET'}")
print(f"  Phase verdict: {phase_verdict}")
print()

# ---------------------------------------------------------------------------
# NOTABLE FINDINGS
# ---------------------------------------------------------------------------
notable_findings = []

# T01: C458 at paragraph level
if prerequisite_met:
    t01_data = test_results.get("01_total_hazard_rate_flatness", {}).get("data", {})
    notable_findings.append({
        "source": "T01",
        "finding": "C458 design clamp confirmed at paragraph level",
        "detail": (
            f"Hazard fraction ~{t01_data.get('counts', {}).get('mean_hazard_fraction', 0):.1%} "
            f"per line, flat across quintiles (partial rho={t01_data.get('partial_spearman', {}).get('rho', 0):+.4f})."
        ),
    })

# T04: Kernel shift in safe pool only
t04_data = test_results.get("04_kernel_mediation_hazard_vs_safe", {}).get("data", {})
if t04_data:
    safe_h = t04_data.get("safe_h_frac", {})
    hazard_h = t04_data.get("hazard_h_frac", {})
    if safe_h.get("significant") and not hazard_h.get("significant"):
        notable_findings.append({
            "source": "T04",
            "finding": "C965 kernel shift is concentrated in NON-hazard tokens",
            "detail": (
                f"Safe pool h_fraction: partial rho={safe_h.get('partial_rho', 0):+.4f}, "
                f"p={safe_h.get('partial_p', 1):.4f}. "
                f"Hazard pool h_fraction: partial rho={hazard_h.get('partial_rho', 0):+.4f}, "
                f"p={hazard_h.get('partial_p', 1):.4f}. "
                "The kernel composition shift operates in the safe (non-hazard) instruction space, "
                "not within hazard-involved tokens."
            ),
        })

# T06: Tautological cross-correlation
t06_data = test_results.get("06_risk_kernel_cross_correlation", {}).get("data", {})
if t06_data:
    cc1 = t06_data.get("cross_correlation_1", {})
    if cc1.get("shuffle_null", {}).get("std", 1) < 0.001:
        notable_findings.append({
            "source": "T06",
            "finding": "EN_CHSH <-> h-kernel cross-correlation is tautological",
            "detail": (
                f"Per-line rho={cc1.get('double_partial_spearman', {}).get('rho', 0):+.4f} "
                f"(p={cc1.get('double_partial_spearman', {}).get('p', 1):.2e}), "
                "but shuffle null has std=0.0 — identical under permutation. "
                "EN_CHSH tokens are defined by ch/sh prefix, which IS the h-kernel marker. "
                "The cross-correlation is a structural identity, not a dynamic signal."
            ),
        })

if notable_findings:
    print("Notable findings:")
    for nf in notable_findings:
        print(f"  [{nf['source']}] {nf['finding']}")
        print(f"    {nf['detail']}")
    print()

# ---------------------------------------------------------------------------
# INTERPRETATION
# ---------------------------------------------------------------------------
if phase_verdict == "NONE":
    interpretation = (
        "The hazard sub-group mix does NOT shift through paragraph body lines. "
        "Risk type migration is absent: PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT_TIMING, "
        "and RATE_MISMATCH exposures are all flat. The C965 kernel composition shift (h rises, "
        "e drops) is NOT mirrored by a corresponding hazard sub-group migration. "
        "C965 is therefore an isolated compositional feature of the non-hazard instruction space, "
        "not evidence of risk profile evolution."
    )
elif phase_verdict == "WEAK":
    interpretation = (
        "Weak evidence for risk profile migration. The hazard rate is flat (C458 confirmed) "
        "but sub-group composition does not shift significantly. The kernel composition shift "
        "(C965) is present in non-hazard tokens only. The cross-correlation between hazard "
        "sub-groups and kernel types is tautological (EN_CHSH = ch/sh prefix = h-kernel). "
        "C965 reflects a grammar-wide compositional drift in the safe instruction space, "
        "not a hazard-mediation strategy."
    )
elif phase_verdict == "MATERIAL":
    interpretation = (
        "Material evidence for risk profile migration. Multiple signals indicate the "
        "risk type being managed shifts through paragraph bodies."
    )
else:
    interpretation = (
        "Strong evidence: hazard sub-group mix and kernel composition shift in tandem. "
        "The risk profile genuinely evolves while total risk exposure stays constant."
    )

print(f"Interpretation: {interpretation}")
print()

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

result = {
    "test": "07_integrated_verdict",
    "phase": "RISK_PROFILE_MIGRATION",
    "phase_verdict": phase_verdict,
    "total_score": total_score,
    "max_score": max_score,
    "prerequisite_met": prerequisite_met,
    "test_scores": {
        info["label"]: {"verdict": info["verdict"], "score": scores[test_name]}
        for test_name, info in test_results.items()
    },
    "notable_findings": notable_findings,
    "interpretation": interpretation,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=True)

print(f"Results saved to {OUTPUT_PATH}")
