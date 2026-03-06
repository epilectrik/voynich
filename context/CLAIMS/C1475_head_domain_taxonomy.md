# C1475: HEAD Atom Domain Taxonomy

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, category, domain, taxonomy
**Phase:** HEAD_DOMAIN_DIFFERENTIATION (Phase 533)
**Date:** 2026-03-05

## Statement

The 5 HEAD atoms {a, e, o, k, t} define categorically distinct operational domains with extreme specialization. k=THERMAL (90.3%, 3.80x enrichment), t=FLOW (87.0%, 4.47x), a=FLOW+TRANSITION (54.2%+41.4%), e=THERMAL+OPERATION (34.7%+32.2%), o=STAGING+OPERATION (32.4%+25.6%). Headless MIDDLEs form a sixth domain: CONTAINMENT+MARKING+STAGING (2.70x/2.51x/2.38x). Category JSD from baseline ranges 0.111 (e, most balanced) to 0.412 (t, most specialized). The 5 HEADs + headless partition the 8-category operational space into non-overlapping primary domains.

## Evidence

- **N:** 23,096 tokens; 16,819 headed (72.8%), 6,277 headless (27.2%)
- **Population:** e=7,002 (30.3%), k=3,100 (13.4%), a=3,079 (13.3%), o=2,717 (11.8%), t=921 (4.0%), headless=6,277 (27.2%)
- **k domain:** THERMAL 90.3% (3.80x baseline), all other categories <3%
- **t domain:** FLOW 87.0% (4.47x baseline), OPERATION 7.4% (0.51x), all others <3.2%
- **a domain:** FLOW 54.2% (2.79x), TRANSITION 41.4% (2.76x), dual-category
- **e domain:** THERMAL 34.7% (1.46x), OPERATION 32.2% (2.24x), TRANSITION 19.1% (1.27x), multi-category
- **o domain:** STAGING 32.4% (2.49x), OPERATION 25.6% (1.78x), FLOW 20.1% (1.03x), multi-category
- **headless domain:** STAGING 30.9% (2.38x), MARKING 19.5% (2.51x), CONTAINMENT 13.0% (2.70x), FLOW 15.1%
- **Pairwise JSD (category):** k vs a = 0.829, k vs t = 0.784, a vs e = 0.502, o vs headless = 0.124 (most similar)

## Relationship to Prior Constraints

- Extends C1393/C1394 (HEAD+MOD*+TERM encoding) with full category characterization per HEAD
- Confirms C1446 (k-HEAD) as pure THERMAL operator
- Refines C1388 (o-atom arrangement domain marker) — o as STAGING-primary HEAD
- Connects to C1305 (MIDDLE determines category) — HEAD is the primary categorical selector within MIDDLE
- Validates C1397 (headless compound functional grammar) — headless domain categorically distinct from all HEADs

## Falsifiable Prediction

If HEAD atoms were not domain-specific, random reassignment of HEAD labels should preserve the category profile structure. The observed extreme enrichments (k THERMAL 3.80x, t FLOW 4.47x) would not survive permutation.
