# FOLIO_PARAGRAPH_ARCHITECTURE Phase

**Question:** How do paragraphs organize within folios? What do gallows tokens at paragraph starts encode?

**Answer:**
1. Sequential phases of a single procedure, linguistically independent but physically sequential
2. Gallows tokens are procedure-type markers with distinct roles (openers vs modes)

---

## Key Discoveries

### 1. Paragraph-Ordinal EN Gradient (C863)
- Early paragraphs: qo-prefixed EN enriched (setup/venting)
- Late paragraphs: ch/sh-prefixed EN enriched (precision/finishing)

### 2. Gallows Paragraph Markers (C864-C869)
- 81.5% of B paragraphs start with gallows token
- Distribution: p (55%), t (29%), k (12%), f (4%)

### 3. Gallows Folio Position
| Gallows | Position | Role |
|---------|----------|------|
| f | 0.30 (front) | Folio opener (HT-rich, PHARMA-specific) |
| k | 0.35 (front) | E-pathway opener |
| p | 0.52 (distributed) | Primary processing mode |
| t | 0.49 (distributed) | Transitional mode (returns to p) |

### 4. P-T Dynamics
- p->p: 54% (self-continuing, stable)
- t->p: 50% (returns to primary mode)
- p is the "steady state", t is the "perturbation"

---

## Model

```
FOLIO = Single procedure for one material

[f/k opener] -> [p continuation] -> [t excursion] -> [p return]
   Setup          Main process       Adjustment       Resume

Gallows = procedure type marker
QO/CHSH = operational mode (independent axis)
```

---

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| 00 | Census | 82 folios, 585 paragraphs, 7.1 mean |
| 01 | Cohesion | Role is primary (0.831), not vocab (0.061) |
| 02 | Vocab distribution | Distributed (Gini 0.279), Par 1 = 27.4% |
| 03 | First paragraph | NOT distinct, predicts 11.8% of later |
| 04 | Complexity | Count reflects complexity (rho 0.836) |
| 05 | Convergence | Vocab converges (14%->39%), roles diverge |
| 06 | Sections | HERBAL_B 2.2 vs PHARMA 14.0 pars/folio |
| 07 | LINK/hazard | Even distribution (CV < 0.21) |
| 08 | Template test | Template score 0.623 (role, not vocab) |
| 09 | Character probe | qo-early/ch-late gradient (C863) |
| 10 | Gallows initial | 81.5% gallows-initial, p dominant |
| 11 | Gallows structure | Token morphology patterns |
| 12 | Gallows QO/CH | Independent axes (0.3% variance) |
| 13 | Gallows meaning | Position in folio (k/f front-biased) |
| 14 | Gallows morphology | k uses e, f often bare |
| 15 | P vs T | Transition dynamics (p stable, t returns) |

---

## Constraints

**C855-C862:** Folio-paragraph architecture (role template, vocab distribution)
**C863:** Paragraph-ordinal EN subfamily gradient (Tier 3)
**C864-C868:** Gallows structural findings (Tier 2)
**C869:** Gallows functional model (Tier 3)

---

## Expert Validation

Model validated against full constraint system:
- No conflicts with existing constraints
- Consistent with C574, C577, C608 (EN subfamily patterns)
- Consistent with C540 (k bound morpheme)
- Consistent with C671 (front-loaded novelty)

---

## Data Dependencies

- `PARAGRAPH_INTERNAL_PROFILING/results/b_paragraph_inventory.json`
- `PARAGRAPH_INTERNAL_PROFILING/results/b_paragraph_tokens.json`
- `CLASS_COSURVIVAL_TEST/results/class_token_map.json`
