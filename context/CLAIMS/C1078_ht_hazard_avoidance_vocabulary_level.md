### C1078 — HT Hazard Avoidance Is Vocabulary-Level, Not Positional

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (HT token × forbidden transition proximity)
- **Phase:** HT_INTERACTION_ARCHITECTURE (2026-02-15)

**Finding:** Only 5 of 7,042 HT tokens in Currier B participate in forbidden transition vocabulary (C109). HT tokens are categorically excluded from hazard pairs by vocabulary selection, not by positional avoidance. The HTSC cross-guarantee prediction (C217 × C803) yields no testable signal because HT's hazard avoidance operates entirely at the role/vocabulary level (C622): the HT vocabulary simply does not include words that appear in forbidden transitions.

**Interpretation:** The boundary enrichment of HT (C803: first=45.8%, last=42.9%, middle=25.7%) is structurally independent of hazard avoidance (C217). These two HT properties do not interact because they operate at different levels: boundary enrichment is positional, hazard avoidance is lexical. The cross-guarantee prediction is trivially satisfied — there is no position-dependent hazard modulation to detect because HT never encounters hazards regardless of position.

**Extends:** C217 (hazard avoidance), C803 (boundary enrichment)
**Confirms:** C622 (hazard avoidance is role-mediated: 43 safe classes, 23 role-excluded)

**Quantitative:**
- HT tokens in B: 7,042
- HT tokens in forbidden vocabulary: 5 (0.07%)
- Boundary vs interior hazard distance: MW p=1.00, Cohen's d=0.17
- Conclusion: No positional modulation detectable (insufficient forbidden-vocabulary HT tokens)
