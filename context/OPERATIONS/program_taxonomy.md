# Program Taxonomy

**Status:** CLOSED | **Tier:** 2

> **Status note (v7.25):** "program", "waiting", "restart", "aggressive/conservative" and "risk" below are the OPS-era control reading, now the Tier-3 working interpretation (closed-loop control demoted, C171; see SYSTEM/STATUS_BRIEF.md §3). The folio metrics themselves (C178–C198, C403) remain Tier 2 in the generated table. Current orientation: SYSTEM/STATUS_BRIEF.md.

---

## 83 Folios Enumerated

| Metric | Value |
|--------|-------|
| Total folios | 83 |
| Total instructions | 75,248 (legacy count, apparently pre-H-filter; H-track Currier B = 23,243 tokens) |
| Grammar coverage | 100% of the grammar's own 480 types = 69.5% of B tokens (C124 as corrected; HT/UN by exclusion, C566) |
| Translation-eligible | 0 (C119) |

---

## Stability Distribution

| Category | Count | % |
|----------|-------|---|
| MODERATE | 46 | 55% |
| CONSERVATIVE | 18 | 22% |
| AGGRESSIVE | 15 | 18% |
| ULTRA_CONSERVATIVE | 4 | 5% |

---

## Waiting Profiles

*[Historical labels: these profiles were computed in the OPS phases, when LINK was read as waiting. The 38% LINK figure of that era is not reproducible (true density 13.2%, C609) and LINK is a morphological artifact of "ol" (C1174); the "waiting" reading is withdrawn.]*

| Profile | Count | % |
|---------|-------|---|
| LINK_MODERATE | 39 | 47% |
| LINK_HEAVY | 24 | 29% |
| LINK_SPARSE | 14 | 17% |
| LINK_EXTREME | 6 | 7% |

---

## Special Folios

### RESTART_CAPABLE (3)
- f50v
- f57r (= RESTART_PROTOCOL, only folio with reset behavior)
- f82v

### Vocabulary Outliers (3)
- f113r
- f66v
- f105v

---

## 5 Program Archetypes (C403)

Programs form a continuum (silhouette 0.14-0.19):

| Archetype | Folios | Key Characteristics |
|-----------|--------|---------------------|
| Conservative Waiting | 10 | LINK 0.50, HIGH_IMPACT 21.7% |
| Aggressive Intervention | 10 | CORE_CONTROL 26.3% |
| Balanced Standard | 20 | Middle of manifold |
| FREQUENT_OPERATOR-Dominated | 16 | 26.7% |
| Energy-Intensive | 26 | ENERGY_OPERATOR 47.2% |

**Not discrete categories** - positions on multidimensional operational manifold.

---

## Section Distribution

*[STATE-C rate = terminal-state occupancy only (C074, Tier 2 measurement); "convergence to STATE-C" is withdrawn — no sequential convergence (C1401–C1403), and C079/C084 are demoted to Tier 3.]*

| Section | Folios | STATE-C Rate |
|---------|--------|--------------|
| H | ~40 | ~50% |
| S | ~20 | ~50% |
| B | ~15 | ~70% |
| C | ~8 | ~100% |

---

## Folio Ordering

| Property | Value |
|----------|-------|
| Risk gradient | rho=0.39 |
| CEI smoothing | d=1.89 |
| Aggressive buffering | 88% vs 49% null |

Manuscript ordering is designed, not random. [C161/C162 remain Tier 2 as ordering measurements; "risk" and "designed" are the OPS-era control reading (C171 demoted to Tier 3).]

---

## Navigation

← [ops_doctrine.md](ops_doctrine.md) | [control_engagement.md](control_engagement.md) →
