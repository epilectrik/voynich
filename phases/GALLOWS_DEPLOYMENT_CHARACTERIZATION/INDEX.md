# Phase 611: GALLOWS_DEPLOYMENT_CHARACTERIZATION

**Status:** COMPLETE
**Verdict:** CONTEXT_SENSITIVE_DEPLOYMENT
**Constraints:** C1772-C1777
**Scripts:** `scripts/gallows_deployment.py` (~3s)

## Motivation

During Phase 610 (Stars Folio Close Reading), observations about gallows markers prompted an extended investigation into their role as paragraph delimiters. Through one-shot scripts, we discovered that gallows encode context-sensitive deployment postures that are not reducible to simple positional or archetype effects. This phase formalizes those findings.

Gallows still have known structural positional behavior (C865 front bias, C1321 within-block ordering, C1323 cross-block restart). This phase does not refute positional structure -- it refutes the stronger idea that gallows are *nothing but* position/archetype labels.

## Method

Consolidated analysis across 572 gallows-initial paragraphs (k=35, t=230, p=287, f=20) spanning 82 Currier B folios and all 5 sections. Gallows-initial token excluded from all body counts. Tests organized into 5 blocks:

- **A.** Body atom ecology (self-enrichment, complementary bias, full O/E matrix)
- **B.** Body composition escalation (atom/bigram/MIDDLE resolution)
- **C.** Deployment context (ambient state, event triggers, rate-of-change)
- **D.** Archetype interaction (aggregate and within-section independence)
- **E.** Auxiliary (terminal suffix routing, folio ecology)

## Results Summary

### Block A: Body Atom Ecology
- **p-gallows self-enrichment:** O/E=1.417, p=0.0001, survives all 5 sections
- **k-gallows e-bias:** O/E=1.171, p<0.000001 (k enriches e, not k)
- **t self-enrichment:** NULL (O/E=1.085, p=0.156)
- **f self-enrichment:** NULL (O/E=1.308, p=0.461, low n)
- **Full contingency:** Cramer's V=0.039, p<0.000001

### Block B: Body Composition
- **Effect size escalation:** V=0.039 (atoms) -> V=0.065 (bigrams) -> V=0.087 (MIDDLEs)
- All three resolutions significant (p<0.000001)
- f-gallows notable: {d,i} 3.28x enriched, termination MIDDLEs depleted

### Block C: Deployment Context
- **Ambient context significant:** thermal p=0.0004, monitoring p=0.002
- **Event triggers ALL NULL:** alarms p=0.14-0.26, deltas p=0.37-0.78
- Deployment is context-conditioned, not event-dispatched

### Block D: Archetype Interaction
- **Aggregate:** p=0.0009, V=0.130 (significant)
- **Within Stars:** p=0.227 (null)
- **Within Bio:** p=0.683 (null)
- **Within Cosmo:** p=0.959 (null)
- **Within Herbal:** p=0.008 (but low expected cells, unreliable)
- Aggregate association is section-mediated

### Block E: Auxiliary
- Terminal suffix -> next gallows: NULL (V=0.161, p=0.252)
- Folio ecology: e_frac vs t-frac rho=-0.369 (p=0.002), e_frac vs p-frac rho=+0.356 (p=0.003)

## Findings

### F1: Gallows bias body composition at multiple resolutions
Gallows type predicts paragraph body atom composition with escalating effect size at higher compositional structure (V=0.039 atoms -> 0.065 bigrams -> 0.087 MIDDLEs). Gallows are not ornamental.

### F2: Atom substrate inheritance is partial and asymmetric
p shows direct body continuity (self-enrichment 1.417x across all sections). k shows complementary e-bias (1.171x, consistent with C866/C521). t and f show no significant self-enrichment.

### F3: Deployment is ambient-context sensitive
Local thermal and monitoring state predict which gallows deploys. Event-like triggers (threshold crossings, rate-of-change, trajectory shifts) are all null. Gallows respond to operational context, not alarms.

### F4: Gallows are not reducible to paragraph archetypes
The aggregate gallows-archetype association is entirely section-mediated. Within any section, gallows type and paragraph archetype are independent structural layers.

## Constraints

### C1772: Gallows-Body Composition Association
**Tier 2 | Scope: B_paragraph, gallows**

Gallows type predicts paragraph body composition at multiple compositional resolutions, with effect strength increasing at higher structure levels. Atom-level: Cramer's V=0.039 (p<0.000001, 4 gallows x 16 atoms, 46,982 body atom instances). Bigram-level: V=0.065 (top 30 ordered bigrams). MIDDLE-level: V=0.087 (top 30 MIDDLEs). All three significant. The escalation confirms compositional, not just individual-atom, gallows influence on paragraph body content.

### C1773: p-Gallows Direct Body Continuity
**Tier 2 | Scope: B_paragraph, p-gallows**

p-gallows paragraphs show robust p-atom enrichment in body tokens (excluding header token): O/E=1.417, chi2=14.98, p=0.0001 (n=287 paragraphs, 25,870 body atoms). Survives section stratification: Bio O/E=2.058 (p=0.008), Herbal O/E=1.666 (p=0.032), Stars O/E=1.283 (p=0.026), T O/E=5.812 (p=0.0003). p is the only gallows type showing significant self-atom enrichment. This is direct body continuity: the atom that names the gallows is overrepresented in the paragraph's body.

### C1774: k-Gallows Complementary e-Bias
**Tier 2 | Scope: B_paragraph, k-gallows, C866, C521**

k-gallows paragraphs enrich e-atoms rather than k-atoms in body tokens: e O/E=1.171 (p<0.000001), k O/E=0.905 (p=0.088, null). k-paragraphs do not implement "more heat" -- they implement "cooling response." This complementary rather than self-identity continuity is consistent with C866 (k uniquely uses e-POST at 29.8%) and C521 (e = cooling/regulation). The k-gallows header declares the condition; the body implements the complementary response.

### C1775: Gallows Ambient-Context Deployment
**Tier 2 | Scope: B_paragraph, deployment, context**

Gallows selection correlates with local ambient operational context: 3-line run-up window thermal_frac KW p=0.0004, monitoring_frac KW p=0.0019. Event-like triggers are all null: above-median alarm conditions (k_high p=0.22, h_high p=0.14, e_high p=0.26), rate-of-change deltas (dk p=0.37, dh p=0.78, de p=0.59). Terminal suffix routing is also null (V=0.161, p=0.252). Gallows deployment is context-conditioned, not event-dispatched and not sequentially routed.

### C1776: Gallows-Archetype Non-Reducibility
**Tier 2 | Scope: B_paragraph, archetype, section**

Aggregate gallows-archetype association is significant (chi2, p=0.0009, V=0.130) but section-mediated. Within-section tests attenuate or collapse: Stars p=0.227 V=0.132 (n=294), Bio p=0.683 V=0.162 (n=122), Cosmo p=0.959 V=0.201 (n=47). Herbal shows p=0.008 but with low expected cells (unreliable). Gallows type and paragraph archetype are distinct structural layers; gallows do not select archetypes once section is controlled.

### C1777: Gallows Atom-Substrate Asymmetry
**Tier 2 | Scope: B_paragraph, gallows, atom_substrate**

Gallows body inheritance from the shared atom substrate is partial and asymmetric: direct in p (self-enrichment O/E=1.417, p=0.0001, all sections), complementary in k (e-bias O/E=1.171, p<0.000001; self null), and weaker/rarer in t (O/E=1.085, p=0.156) and f (O/E=1.308, p=0.461). The four gallows types have qualitatively different relationships to their body ecology. This is not a uniform "gallows = atom label" pattern but an asymmetric, type-specific substrate inheritance.

## Tier 3 Synthesis

Gallows function as context-sensitive paragraph deployment headers. They encode invocation posture under ambient operational conditions and bias body implementation at atom/composition level. Their inheritance from the shared atom substrate is partial and asymmetric: direct in p, complementary in k, weaker or rarer in t and f. They are not broad category labels, not event-dispatch states, and not proven worker-role markers. Gallows are structurally independent from, but interact with, paragraph archetype and block-position systems.

## Observations Preserved (Not Registered as Tier 2)

- **f-gallows anti-termination profile:** {d,i} co-occurrence enriched 3.28x, termination MIDDLEs (ey, in) depleted 0.34x. Suggestive of sustained intervention posture but too interpretive with low n (f=20 paragraphs) for Tier 2.
- **Folio gallows ecology:** e_frac vs t-frac rho=-0.369 (p=0.002), e_frac vs p-frac rho=+0.356 (p=0.003). Derivative of section composition, too thin as standalone constraint.
- **Section gallows menus:** Herbal 62% t, Cosmo 70% p, Stars balanced. Descriptive; absorbed by C1776 section-mediation finding.

## Output Files

| File | Description |
|------|-------------|
| `results/gallows_deployment_results.json` | Full test statistics, constraint evidence, O/E matrices |
| `scripts/gallows_deployment.py` | Consolidated analysis (5 test blocks A-E) |

## Related Constraints

C855 (paragraph independence), C865 (gallows front bias), C866 (gallows morphological patterns), C867 (p-t transition dynamics), C869 (gallows functional model), C1195 (atom glosses), C1321 (gallows within-block ordering), C1322 (gallows content-label independence), C1323 (cross-block restart), C521 (e-atom cooling).
