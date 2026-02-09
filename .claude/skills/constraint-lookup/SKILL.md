---
name: constraint-lookup
description: Looks up constraints by number, keyword, or topic. Use when user asks about a specific constraint, wants to find related constraints, or needs to verify constraint details.
allowed-tools: Read, Grep, Glob
---

# Constraint Lookup Skill

When looking up constraints in the Voynich project:

## By Number (C###)

1. Read `context/CLAIMS/INDEX.md` to find the constraint
2. Check the legend:
   - `→` = Individual file exists
   - `⊂` = In grouped registry
3. Read the appropriate file:
   - Individual: `context/CLAIMS/C###_name.md`
   - Grouped: `context/CLAIMS/[category].md`

## By Keyword

1. Grep `context/CLAIMS/` for the keyword
2. Return matching constraint numbers with brief descriptions
3. Offer to read full details if needed

## Individual Claim Files Available

- C074 - Dominant convergence
- C109 - 5 hazard failure classes
- C121 - 49 instruction classes
- C124 - 100% grammar coverage
- C171 - Closed-loop control only
- C229 - Currier A is DISJOINT
- C240 - A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
- C267 - Tokens are COMPOSITIONAL
- C301 - AZC is HYBRID
- C357 - Lines are DELIBERATELY CHUNKED
- C382 - Morphology encodes control phase
- C383 - GLOBAL TYPE SYSTEM
- C384 - NO entry-level A-B coupling
- C404 - HT terminal independence (non-operational)
- C408 - Sister pair equivalence classes
- C411 - Deliberate over-specification

## Grouped Registries

| File | Constraints |
|------|-------------|
| tier0_core.md | Tier 0 frozen facts |
| grammar_system.md | C085-C144 (kernel, hazard, families) |
| currier_a.md | C224-C299 (A schema, morphology) |
| human_track.md | C166-C172, C341-C348, C404-C406 |
| azc_system.md | C300-C322 |
| operations.md | C178-C223 (OPS, EXT) |
| organization.md | C153-C165, C323-C403 |
| morphology.md | C349-C411 |

## Output Format

When returning constraint info, always include:

```
**C###: [Short Name]**
- Tier: [0/1/2/3/4]
- Status: [FROZEN/CLOSED/OPEN]
- Source: Phase [NAME]
- Statement: [One sentence]
- Evidence: [Key evidence]
- Related: C###, C###
```

## Quick Reference

| Tier | Meaning |
|------|---------|
| 0 | FROZEN FACT - proven, do not reopen |
| 1 | FALSIFICATION - rejected, do not retry |
| 2 | STRUCTURAL - high-confidence bounded |
| 3 | SPECULATIVE - interpretive layer |
| 4 | EXPLORATORY - idea generation only |
