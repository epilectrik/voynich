# C1064: PREFIX-SUFFIX Joint Role Encoding

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE (Phase 380)
**Extends:** C1059 (suffix-role independence from PREFIX), C588 (role-suffix distributions), C662 (PREFIX role reclassification 75%)
**Relates to:** C1003 (no three-way synergy)

---

## Statement

Joint PREFIX+SUFFIX features predict role with **+5.9pp accuracy gain** over PREFIX alone (88.5% vs 82.6%, 5-fold CV). The gain is concentrated in QO-family PREFIXes where suffix provides strong sub-role discrimination.

| Feature set | CV accuracy |
|-------------|-------------|
| PREFIX-only | 82.6% |
| SUFFIX-only | 45.9% |
| Joint PREFIX+SUFFIX | **88.5%** |
| Gain over best single | **+5.9pp** |

Per-PREFIX within-group suffix V (how much suffix helps within each PREFIX):

| PREFIX | V | n | Interpretation |
|--------|---|---|----------------|
| ol | 0.663 | 475 | Suffix near-perfectly discriminates role |
| ok | 0.655 | 1185 | Very strong |
| da | 0.611 | 900 | Strong |
| ot | 0.532 | 1137 | Strong |
| BARE | 0.436 | 2715 | Moderate |
| ch | 0.129 | 2510 | Weak |
| sh | 0.120 | 1595 | Weak |

QO-family mean V = 0.615 vs sister-pair mean V = 0.124 (5.0x ratio).

---

## Interpretation

C1059 established that suffix carries independent role information (anti-mediation). This constraint quantifies the practical consequence: adding suffix to PREFIX classification yields a substantial 5.9pp gain.

The gain is structurally interpretable: QO-family PREFIXes (ok, ot, ol, da) contain multiple roles (EN, AX, FQ) distinguished almost entirely by suffix choice (V = 0.53-0.66). Sister-pair PREFIXes (ch, sh) route primarily to EN, leaving little room for suffix to add information (V = 0.12).

This confirms a three-layer encoding architecture: PREFIX provides primary role selection (82.6%), suffix provides independent secondary discrimination (+5.9pp), and their combination approaches the practical ceiling for morphological role prediction. The remaining ~11.5% error is either MIDDLE-dependent or reflects genuine ambiguity.

The +5.9pp gain is consistent with C662 (PREFIX captures 75% class reduction) and C1003 (no three-way synergy): the gain is additive, not synergistic.

---

## Method

- 16,054 classified Currier B tokens (49-class taxonomy)
- 5-fold stratified CV: frequency-based classifier (most-common role per feature value)
- Per-PREFIX decomposition: Cramér's V of role x suffix within each PREFIX group (n >= 50)
- QO-family: ok, ot, ol, da. Sister-pair: ch, sh.

**Script:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py`
**Results:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t2_prefix_suffix_role_gain.json`
