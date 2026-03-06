# C1529: PHASE_ORDERING Is Headless-y to a-HEAD Transition Failure

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, TERM, hazard, PHASE_ORDERING, headless, y-terminal, a-HEAD, forbidden, violation, C109, C110, C1477, C1484, C1488, C1489
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

PHASE_ORDERING (7/17 forbidden pairs, 41% of all hazard — C110) decomposes as headless y-terminal sources (shey, dy, chey) routing illegally into a-HEAD iteration targets (aiin, al, chedy, shedy). All source MIDDLEs are y-terminal (100%); target MIDDLEs are predominantly a-HEAD (42.9%). This class accounts for 10/11 (90.9%) of all actual corpus forbidden violations, all being dy->aiin transitions. PHASE_ORDERING is the grammar's dominant failure mode: operations that complete (y = "end") but then illegally restart iteration cycles (a = "into", n = "bind").

## Evidence

### Source and target atom analysis

- Source HEADs: s, d, c (all headless pseudo-HEADs)
- Source TERMs: y (100%)
- Target HEADs: a (42.9%), c, s (headless)
- Target TERMs: n, l, y, c

### Corpus violations

- 10/11 total corpus forbidden violations are PHASE_ORDERING (90.9%)
- All 10 are dy->aiin transitions
- Source MIDDLE 'dy' appears 558 times; 10 violations = 98.21% avoidance rate
- CHSH-prefixed contexts carry 7/11 violations (see C1533)

### Phantom sources

- 3 of 4 PHASE_ORDERING source MIDDLEs (shey, chey, chol) have ZERO corpus occurrences
- Only 'dy' actually appears, accounting for all violations
- See C1531 for phantom MIDDLE analysis

## Interpretation

PHASE_ORDERING is a sequencing failure at the atom level: y-terminal completion signals (dy = "seal-end", shey = "monitor-end") followed by a-HEAD iteration (aiin = "into-cycle-cycle-bind"). The grammar forbids restarting an iteration cycle after a process has been marked as complete. This is consistent with the distillation interpretation: once you have finished and sealed, you cannot legally re-enter the iteration loop.

## Falsification Criteria

1. If PHASE_ORDERING source y-terminal rate drops below 80%
2. If PHASE_ORDERING violations drop below 70% of total corpus violations
3. If non-dy source MIDDLEs begin appearing in corpus with violations

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
