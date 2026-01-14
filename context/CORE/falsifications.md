# Consolidated Falsifications (Tier 1)

**Status:** CLOSED | **Tier:** 1

---

## Purpose

These hypotheses have been **explicitly tested and rejected**. Each has documented falsifying evidence. Do not retry these approaches.

---

## Major Falsifications

### Language Encoding
**Status:** FALSIFIED
**Evidence:** Phase X.5 found 0.19% reference rate
**Meaning:** Tokens do not behave like words. No referential structure exists.

### Cipher Encoding
**Status:** FALSIFIED
**Evidence:** Phase G showed cipher transforms DECREASE mutual information
**Meaning:** If this were cipher, decryption would increase structure. The opposite happens.

### Glyph-Level Semantics
**Status:** FALSIFIED
**Evidence:** Phase 19 found 0 identifier tokens
**Meaning:** Individual glyphs don't carry meaning. Tokens are the minimal unit.

### Illustration-Dependent Logic
**Status:** FALSIFIED
**Evidence:** Phase ILL showed swap invariance p=1.0; Phase ILL-TOP-1 tested 8 hypotheses (topology, order, quire, scaffolding, geometry) - all failed
**Meaning:** Swapping illustrations doesn't affect text analysis. Visual similarity does not predict constraint similarity at any level. Illustrations are epiphenomenal to grammar.

### Step-by-Step Recipe Format
**Status:** FALSIFIED
**Evidence:** Phase FSS showed families are emergent, not designed
**Meaning:** The text is not organized as discrete recipes with beginnings and endings.

---

## Specific Claim Falsifications

| Claim | Evidence | Phase |
|-------|----------|-------|
| Text encodes language | 0.19% reference rate | X.5 |
| Tokens have translatable meanings | 0 identifier tokens | 19 |
| Illustrations are instructional | Swap invariance p=1.0 | ILL |
| Illustrations organize constraints | 8/8 tests failed | ILL-TOP-1 |
| Plants indicate ingredients | Dual-use history (perfumery, medicine) | PCIP |
| Sections = apparatus configs | F-ratio 0.37 | PCS |
| Programs correlate with plant morphology | All p>>0.05 | PPC |
| 49-class grammar generalizes to full manuscript | 13.6% Currier A coverage | CAud |
| Hazard topology is universal | 5 violations in Currier A | CAud |
| "100% convergence to STATE-C" | Only 57.8% terminate in STATE-C | SEL-F |
| Procedural chaining (folios form macro-sequences) | Tests 1-6 falsified | SEL-F |
| STATE-C marks material-family boundaries | TEST 11 p=1.0 | SEL-F |
| Sharp material-family clustering | Silhouette=0.018 (highly overlapping) | SEL-F |
| Hazard "100% bidirectional" | 65% asymmetric | SEL-D |
| Hazard "KERNEL_ADJACENT clustering" | 59% distant from kernel | SEL-D |
| Human-track "7 coordinate functions" | Overfitting | SEL-E |
| HT 99.6% LINK-proximal | ρ=0.010, p=0.93 (decoupled) | HTD |
| Repetition encodes ratios/proportions | No cross-entry comparison, no reference frame | EXT-9B |

---

## Adversarial Audit Results

Eight attack vectors were tested against the model:

| Attack | Result |
|--------|--------|
| Kernel Collapse | SURVIVES |
| Cycle Illusion | WEAKENED (documented) |
| Grammar Minimality | WEAKENED (documented) |
| Random Baseline | SURVIVES |
| Folio Independence | SURVIVES |
| Grammar Collapse | SURVIVES |
| DSL Discriminator | SURVIVES |
| Family Syntax | SURVIVES |

**Overall:** 6/8 attacks failed to falsify the model. 2/8 weakened specific claims (now documented with caveats).

---

## Purpose Classes Eliminated

The following purpose classes were eliminated by structural incompatibility:

- Cipher/hoax
- Encoded language
- Recipe/pharmacology
- Herbarium/taxonomy
- Medical procedure
- Astronomical calculation
- Ritual/symbolic practice
- Educational text
- Discrete batch operations
- Fermentation
- Glassmaking/metallurgy
- Dyeing/mordanting

**Only surviving purpose class:** Continuous closed-loop process control

---

## Rule

**Do not retry falsified approaches.**

If you believe a falsification was incorrect, first review the phase documentation. The evidence is documented. If you still disagree, you are likely misunderstanding the scope or methodology.

---

## Navigation

← [model_boundary.md](model_boundary.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
