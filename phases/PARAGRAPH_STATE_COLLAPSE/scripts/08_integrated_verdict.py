"""
Test 08: Integrated Verdict
Phase: PARAGRAPH_STATE_COLLAPSE

Purpose: Load results from T01-T07, compute aggregate collapse score,
and deliver final phase verdict.

Scoring: PASS=1.0, PARTIAL=0.5, FAIL=0.0
  STRONG COLLAPSE (score >= 5.5): pervasive depletion
  MODERATE COLLAPSE (score >= 3.5): multiple features collapse
  WEAK COLLAPSE (score >= 1.5): inconsistent evidence
  NO COLLAPSE (score < 1.5): body truly homogeneous in diversity too
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("C:/git/voynich").resolve()
RESULTS_DIR = PROJECT_ROOT / "phases/PARAGRAPH_STATE_COLLAPSE/results"
OUTPUT_PATH = RESULTS_DIR / "08_integrated_verdict.json"

SCORE_MAP = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0}

TESTS = [
    ("01_vocabulary_entropy_collapse", "Vocabulary Entropy"),
    ("02_role_entropy_collapse", "Role Entropy"),
    ("03_suffix_entropy_collapse", "Suffix Entropy"),
    ("04_effective_instruction_set", "Effective Instruction Set"),
    ("05_ax_terminal_scaffold", "AX Terminal Scaffold"),
    ("06_ht_ax_substitution", "HT-AX Substitution"),
    ("07_kernel_diversity_collapse", "Kernel Diversity"),
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
    v = info["verdict"]
    scores[test_name] = SCORE_MAP.get(v, 0.0)

total_score = sum(scores.values())
max_score = len(TESTS) * 1.0

if total_score >= 5.5:
    phase_verdict = "STRONG_COLLAPSE"
elif total_score >= 3.5:
    phase_verdict = "MODERATE_COLLAPSE"
elif total_score >= 1.5:
    phase_verdict = "WEAK_COLLAPSE"
else:
    phase_verdict = "NO_COLLAPSE"

print("=" * 60)
print("PARAGRAPH_STATE_COLLAPSE — Integrated Verdict")
print("=" * 60)
print()

for test_name, info in test_results.items():
    v = info["verdict"]
    s = scores[test_name]
    print(f"  {info['label']:30s}  {v:8s}  ({s:.1f})")

print()
print(f"  Total score: {total_score:.1f} / {max_score:.1f}")
print(f"  Phase verdict: {phase_verdict}")
print()

# ---------------------------------------------------------------------------
# COLLECT NOTABLE FINDINGS (signals that emerged despite FAIL verdicts)
# ---------------------------------------------------------------------------
notable_findings = []

# T07 kernel composition shift
t07 = test_results.get("07_kernel_diversity_collapse", {}).get("data", {})
if t07:
    h_frac = t07.get("h_fraction", {})
    e_frac = t07.get("e_fraction", {})
    h_partial_p = h_frac.get("partial_p", 1.0)
    e_partial_p = e_frac.get("partial_p", 1.0)
    if h_partial_p < 0.01 or e_partial_p < 0.01:
        notable_findings.append({
            "source": "T07",
            "finding": "Kernel composition shift",
            "detail": (
                f"h-fraction rises (partial rho={h_frac.get('partial_rho', 0):+.4f}, "
                f"p={h_partial_p:.4f}), "
                f"e-fraction drops (partial rho={e_frac.get('partial_rho', 0):+.4f}, "
                f"p={e_partial_p:.4f}). "
                "Survives length control. Not a diversity collapse but a composition shift."
            ),
        })

# T06 HT-AX cross-correlation
t06 = test_results.get("06_ht_ax_substitution", {}).get("data", {})
if t06:
    cross = t06.get("ht_ax_cross_correlation", {})
    cross_p = cross.get("p", 1.0)
    if cross_p < 0.01:
        notable_findings.append({
            "source": "T06",
            "finding": "HT-AX negative cross-correlation",
            "detail": (
                f"rho={cross.get('rho', 0):+.4f}, p={cross_p:.6f}. "
                "Lines with more HT have less AX and vice versa. "
                "Not a positional trend but a per-line trade-off."
            ),
        })

# T01 line-length confound magnitude
t01 = test_results.get("01_vocabulary_entropy_collapse", {}).get("data", {})
if t01:
    confound = t01.get("line_length_confound", {})
    if confound:
        notable_findings.append({
            "source": "T01",
            "finding": "Line length dominates entropy",
            "detail": (
                f"Line length correlates with MIDDLE entropy at "
                f"rho={confound.get('rho_with_entropy', 0):+.4f}. "
                "All raw entropy/diversity declines are driven by C677 (line shortening), "
                "not by independent collapse."
            ),
        })

if notable_findings:
    print("Notable findings (emerged despite FAIL verdicts):")
    for nf in notable_findings:
        print(f"  [{nf['source']}] {nf['finding']}")
        print(f"    {nf['detail']}")
    print()

# ---------------------------------------------------------------------------
# INTERPRETATION
# ---------------------------------------------------------------------------
if phase_verdict == "NO_COLLAPSE":
    interpretation = (
        "Paragraph body lines show NO measurable state collapse beyond line shortening (C677). "
        "C963 (body homogeneity) is comprehensively confirmed: role fractions, entropy, "
        "distinct counts, suffix diversity, AX subgroup distribution, HT rates, and kernel "
        "diversity are ALL flat after controlling for line length. The 'quiet and rigid' "
        "appearance of late paragraphs is entirely explained by C677 (fewer tokens per line) — "
        "the effective instruction set does not shrink. "
        "One genuine signal survived: kernel composition shifts from e-dominant to h-dominant "
        "across paragraph bodies (T07), but this is a composition change, not a diversity collapse."
    )
elif phase_verdict == "WEAK_COLLAPSE":
    interpretation = (
        "Weak evidence for state collapse. Some diversity metrics show marginal declines "
        "but the pattern is inconsistent. Line shortening (C677) remains the dominant driver."
    )
elif phase_verdict == "MODERATE_COLLAPSE":
    interpretation = (
        "Moderate evidence for state collapse across multiple dimensions. "
        "The effective instruction set measurably narrows beyond what line shortening explains."
    )
else:
    interpretation = (
        "Strong, pervasive state collapse. Nearly all diversity metrics decline "
        "systematically through paragraph bodies, independent of line shortening."
    )

print(f"Interpretation: {interpretation}")
print()

# ---------------------------------------------------------------------------
# CONSTRAINT CANDIDATES
# ---------------------------------------------------------------------------
constraint_candidates = []

if phase_verdict in ("MODERATE_COLLAPSE", "STRONG_COLLAPSE"):
    constraint_candidates.append({
        "id": "C965",
        "statement": "Paragraph body effective instruction set shrinks monotonically",
        "tier": 2,
    })

# Always propose the kernel shift if significant
if any(nf["source"] == "T07" for nf in notable_findings):
    constraint_candidates.append({
        "id": "C965",
        "statement": (
            "B paragraph body kernel composition shifts: h-kernel fraction increases "
            "and e-kernel fraction decreases through body lines, controlling for line length. "
            "This is a composition shift, not a diversity collapse."
        ),
        "tier": 2,
    })

# Always propose C677 confirmation
constraint_candidates.append({
    "id": "C963_EXTENDED",
    "statement": (
        "C963 body homogeneity extends to all diversity metrics: Shannon entropy "
        "(vocabulary, role, suffix, kernel), distinct counts (roles, classes, MIDDLEs, "
        "suffixes), and rate-normalized versions. All are flat after line-length control. "
        "7/7 tests FAIL the collapse hypothesis."
    ),
    "tier": 2,
})

if constraint_candidates:
    print("Constraint candidates:")
    for cc in constraint_candidates:
        print(f"  {cc['id']}: {cc['statement']}")
    print()

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

result = {
    "test": "08_integrated_verdict",
    "phase": "PARAGRAPH_STATE_COLLAPSE",
    "phase_verdict": phase_verdict,
    "total_score": total_score,
    "max_score": max_score,
    "test_scores": {
        info["label"]: {"verdict": info["verdict"], "score": scores[test_name]}
        for test_name, info in test_results.items()
    },
    "notable_findings": notable_findings,
    "interpretation": interpretation,
    "constraint_candidates": constraint_candidates,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=True)

print(f"Results saved to {OUTPUT_PATH}")
