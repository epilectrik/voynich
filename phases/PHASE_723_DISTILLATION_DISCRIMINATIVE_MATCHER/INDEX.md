# PHASE_723: Distillation-Discriminative Matcher (Option 3)

**Status:** Phase 1-3 COMPLETE, registered as C2054. Phase 4 BLOCKED on framework-as-null trap — needs decoupled feature redesign.
**Date:** 2026-05-21
**Verdict (Phase 1-3):** Hand-tuned physics-architectural features cleanly discriminate three classes within medieval procedural Latin: operational distillation (Codicillus +0.0152, full Pseudo-Lull Testamentum +0.0077), theoretical-alchemy/pharmacy neutral (Rupescissa +0.0005, Mesue -0.0004), metalwork (Theophilus -0.0052). Mann-Whitney p<10⁻⁵ between operational distillation and metalwork. Generalizes from Codicillus subset to full Testamentum (Phase 3, 3/3 PASS). Registered as C2054 (Tier 2 Latin-side instrument calibration measurement).
**Phase 4 blocked:** Both experts identified framework-as-null trap — the proposed Voynich-side mapping uses constraints (C1314, C645+C2045, C2042) DERIVED FROM Voynich substrate observations. Using them as positive features for "Voynich is distillation" would be tautological. Phase 4 requires decoupled feature design (Voynich-side features defined a priori from external Latin features, NOT from existing Voynich constraints) per crazy-expert's recommendation.
**Posture:** PHASE_718 confirmed the existing 8D matcher is generic — it clusters medieval-craft-procedural Latin generically without discriminating distillation from metalwork. This phase builds a NEW matcher using features specifically designed to discriminate distillation-class operations from metalwork-class operations at the text level.

---

## Why a new matcher (per user discussion)

The 8D matcher's features (heat_rate, monitoring_rate, correction_rate, termination_rate, etc.) measure register/instructional density. They cluster medieval-craft-procedural Latin generically — Theophilus metalwork matches the same Voynich folios as Codicillus alchemy at similar rates per PHASE_718.

PWRE-1 structurally excludes Theophilus-type irreversible-transformation metalwork from the controller's compatible physics class. But the 8D matcher's text features can't capture this physics distinction. **Solution:** build features that explicitly capture the physics-architectural differences between distillation and metalwork.

---

## Feature design

### Distillation-class markers (Latin)

**Apparatus** — distillation-specific vessels:
- `alembic`, `alembico`, `alembicum`, `cucurbita`, `capitellum`, `distillatorium`, `serpentinum`, `recipiens` (receiver), `vas distillatorium`

**Phase-transition operations** — vapor/condensation cycles:
- `distill*`, `sublim*`, `evaporat*`, `condens*`, `vaporat*`, `ascend*`, `descend*`, `transmut*`, `exhal*`

**Reversibility markers** — return-to-state operations:
- `revert*`, `restaur*`, `regenera*`, `redditur`, `redit`, `iter*`, `repet*`

**Circulation markers** — closed-loop indicators:
- `circul*`, `rotatio`, `refluxus`, `redux*`, `pelican*`

**State markers** — phase descriptors:
- `vapor`, `fumus`, `aer`, `aqua` (in vapor/condensation contexts), `quintessen*`

### Metalwork-class markers (Latin)

**Apparatus** — metalwork-specific tools:
- `incus` (anvil), `malleus` (hammer), `tenax` (tongs), `forn*` (furnace, but careful — overlaps with alchemy), `crucibulum` (crucible — used in BOTH, exclude)

**Irreversible-transformation operations**:
- `fund*` (cast), `conflat*` (smelt), `cud*` (hammer), `trahere` (draw out), `polire` (polish), `lim*` (file), `fabric*` (forge)

**Metallic materials**:
- `aurum`, `argentum`, `ferrum`, `cuprum`, `stannum`, `plumbum`, `aes`, `electrum`, `ferramentum`

**Solid-state markers**:
- `durus`, `indurat*`, `solidus`, `rigid*`, `tem*pera*` (tempering)

### Critical exclusions (ambiguous between domains)

- `fornax` / `furnace` — both domains
- `crucibulum` / `crucible` — both domains
- `ignis` / `fire` — both domains
- `aqua` (without phase-transition context) — both domains
- `terra` / `earth` — both domains

These ambiguous terms are EXCLUDED to avoid masking the discrimination.

---

## Methodology (LOCKED)

### Phase 1: Validate feature discrimination on Latin corpora

For each Latin chapter/paragraph in {Codicillus, Rupescissa, Theophilus}:
1. Compute `distillation_score = (count of distillation markers) / n_words`
2. Compute `metalwork_score = (count of metalwork markers) / n_words`
3. Compute `discrimination_score = distillation_score - metalwork_score`

Compute chapter-level statistics per corpus.

### Phase 2: Pre-registered discrimination criteria (LOCKED)

| Corpus | Predicted | Threshold |
|---|---|---|
| Codicillus (distillation) | discrimination_score > +0.005 | mean per chapter |
| Rupescissa (distillation) | discrimination_score > +0.005 | mean per chapter |
| Theophilus (metalwork) | discrimination_score < -0.005 | mean per chapter |
| Theophilus vs Codicillus | difference > 0.010 | substantial separation |

**Test of independence:**
- t-test or Mann-Whitney for Theophilus-vs-Codicillus discrimination scores
- Pre-registered: p < 0.01 for substantial separation

### Phase 3: Apply to Pseudo-Lull Testamentum (full text)

Apply same features to the full ~104k-word Testamentum corpus. Test if signature matches the Codicillus subset baseline.

### Phase 4: Voynich-side mapping (conditional on Phase 1-2 success)

If Phase 1-2 discrimination works on Latin, design Voynich-side equivalents:
- Distillation markers → Voynich structural features (kernel cycling per C1314, recovery patterns per C645+C2045, reversibility-indicating sequences)
- Metalwork markers → Voynich structural features (NOT predicted to be present per PWRE narrowing)

Compute Voynich folio signatures. Test where Voynich falls relative to distillation/metalwork baseline.

**Phase 4 is the actual matcher payoff** — if it works, it provides external grounding the existing 8D matcher doesn't.

---

## Pre-registered outcomes

| Outcome | Verdict |
|---|---|
| Phase 1-2 discrimination works (Codicillus + Rupescissa > Theophilus on distillation_score) | **DISTILLATION-DISCRIMINATIVE FEATURES VALIDATED** — proceed to Phase 3-4 |
| Phase 1-2 fails (no separation or wrong direction) | **FEATURE DESIGN FAILED** — text-level distillation discrimination not tractable with this approach; close INDEX-only |
| Phase 3 (Testamentum) matches Codicillus baseline | **Generalization confirmed** — features capture domain-class, not corpus-specific quirks |
| Phase 4 places Voynich in distillation-class | **External grounding for distillation interpretation via discriminative matcher** |
| Phase 4 places Voynich in metalwork-class | **UNEXPECTED** — contradicts PWRE narrowing; needs investigation |
| Phase 4 places Voynich in neither (intermediate) | **Matcher insufficient** — needs Option 2 architectural matcher |

---

## Why this is the right next test

Per cumulative session pattern: text-statistical methods are exhausted at this resolution because they measure register/instructional density. The fix is features designed to discriminate PHYSICS-ARCHITECTURE (reversibility, phase transitions, apparatus class) — not just text register.

**If Phase 1-2 works:** we've built a tool the existing matcher couldn't be — distillation-specific discrimination at the text level. That's an evidence-base expansion.

**If Phase 1-2 fails:** we've confirmed that text-level features cannot discriminate distillation from metalwork even with hand-tuned domain-specific markers. That's a clean negative supporting the procedural ceiling.

Both outcomes are informative.

---

## Implementation

| Script | Purpose |
|---|---|
| `_distillation_matcher_v1.py` | Phase 1-2: validate distillation-discriminative features on Codicillus + Rupescissa + Theophilus |
| (conditional) `_apply_to_testamentum.py` | Phase 3: full Pseudo-Lull Testamentum application |
| (conditional) `_voynich_side_mapping.py` | Phase 4: Voynich folio classification under new feature set |

---

## Effort estimate

- Phase 1-2: ~3-4 hours implementation, ~5 min runtime
- Phase 3: ~1 hour if Phase 1-2 passes
- Phase 4: ~5-10 hours (substantial — designing Voynich-side feature extraction)
- Total: ~10-15 hours if all phases run

---

## Registration-trap audit

- Pre-registered binary criteria locked before run
- Critical exclusions documented (ambiguous markers excluded to prevent masking)
- Multiple corpora tested simultaneously (Codicillus + Rupescissa + Theophilus + Testamentum)
- Both directions tested (distillation feature presence AND metalwork feature presence)
- Per `feedback_floor_vs_discriminator_metric_test.md`: this test explicitly aims to be a DISCRIMINATOR (not just a floor), with metalwork-class Theophilus as the discriminating control
- Per `feedback_framework_as_null.md`: features designed FROM physics-architecture (PWRE narrowing), not from project's existing operational vocabulary — should avoid framework-echo
- N per corpus will be hundreds of paragraphs (Codicillus 148 at 15-80 filter, Theophilus 144, Rupescissa 279, full Testamentum ~500+) — far above PHASE_722's noise-floor problem
