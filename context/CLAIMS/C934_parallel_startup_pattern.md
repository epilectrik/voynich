# C934: Parallel Startup Pattern (Heat Before Prep)

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_EXECUTION_SEQUENCE

## Constraint

Within B paragraphs, heat operations (k MIDDLEs) appear before prep verbs (pch/lch/tch/te) in 65% of paragraphs. First heat appears at average position 0.079; first prep at 0.212. Lines containing BOTH heat and prep co-occur preferentially in early lines (Q0: 9.9%, Q4: 3.4%, r=-0.94). This is consistent with a "light the coals first, then prep materials" startup sequence.

## Evidence

Analysis of 80 B paragraphs with 8+ lines, 62 containing both heat and prep:

**First occurrence position:**

| Operation | Avg Position | N |
|-----------|-------------|---|
| First HEAT | 0.079 | 80 paragraphs |
| First PREP | 0.212 | 62 paragraphs |
| Difference | +0.133 | |

**Per-paragraph ordering:**

| Order | Count | Percent |
|-------|-------|---------|
| Heat first | 40 | 65% |
| Prep first | 17 | 27% |
| Same line | 5 | 8% |

**Lines with BOTH heat and prep by quintile:**

| Quintile | BOTH % |
|----------|--------|
| Q0 | 9.9% |
| Q1 | 7.5% |
| Q2 | 8.1% |
| Q3 | 5.9% |
| Q4 | 3.4% |
| Trend | r=-0.94 |

**Top co-occurring MIDDLEs on prep lines:**

| MIDDLE | Count | Category |
|--------|-------|----------|
| edy (batch) | 233 (9.8%) | MATERIAL |
| k (heat) | 210 (8.8%) | HEAT |
| ol (control) | 71 (3.0%) | CONTROL |
| aiin (control) | 58 (2.4%) | CONTROL |
| ke (sustained) | 47 (2.0%) | HEAT |

## Interpretation

The parallel startup pattern matches Brunschwig distillation practice:

1. **Light the coals** (heat operations appear first, position 0.079)
2. **While coals stabilize, prepare materials** (prep verbs appear at position 0.212)
3. **Both co-occur on early lines** (9.9% in Q0, declining to 3.4% in Q4)

This is not sequential (prep then heat) but parallel: the energy source is started first because it takes time to stabilize, and material preparation happens during that stabilization window.

The 65% heat-first rate is well above chance (50% if independent) but not universal, which is expected — some preparations might need to be completed before any heating begins.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C932 | VALIDATES - Part of the specification→execution gradient mechanism |
| C933 | EXTENDS - Prep verbs are early, but heat is even earlier |
| C893 | COMPATIBLE - HIGH_K paragraphs (recovery) vs HIGH_H (processing) is a different axis |
| C863 | COMPATIBLE - C863 is inter-paragraph (qo→ch/sh); this is intra-paragraph |

## Provenance

- Script: `scratchpad/parallel_startup_test.py`
- Phase: PARAGRAPH_EXECUTION_SEQUENCE

## Status

CONFIRMED - 65% heat-first ordering, co-occurrence r=-0.94 declining trend.
