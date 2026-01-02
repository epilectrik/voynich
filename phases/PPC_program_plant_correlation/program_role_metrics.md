# Program Role Metrics (INDEPENDENT)

> **PURPOSE**: Extract control program metrics for botanical folios.
> **METHOD**: Derived from locked control_signatures.json without reference to plant morphology.

---

## Metric Definitions

| Metric | Derivation | Classes |
|--------|------------|---------|
| **Aggressiveness** | hazard_density + intervention_freq/20 - link_density | AGGRESSIVE (>0.6), MODERATE (0.4-0.6), CONSERVATIVE (<0.4) |
| **LINK Class** | link_density | HEAVY (>0.45), MODERATE (0.30-0.45), SPARSE (<0.30) |
| **Hazard Proximity** | hazard_density | HIGH (>0.65), MEDIUM (0.50-0.65), LOW (<0.50) |
| **Duration** | total_length | EXTENDED (>500), REGULAR (<=500) |
| **Recovery** | recovery_ops_count | HIGH (>10), MODERATE (3-10), LOW (<3) |

---

## Folio-by-Folio Program Metrics

| Folio | Aggressiveness | LINK Class | Hazard Proximity | Duration | Recovery |
|-------|----------------|------------|------------------|----------|----------|
| **f26r** | MODERATE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f26v** | CONSERVATIVE | HEAVY | LOW | REGULAR | LOW |
| **f31r** | AGGRESSIVE | SPARSE | HIGH | REGULAR | MODERATE |
| **f31v** | CONSERVATIVE | HEAVY | MEDIUM | REGULAR | LOW |
| **f33r** | AGGRESSIVE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f33v** | AGGRESSIVE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f34r** | MODERATE | MODERATE | MEDIUM | REGULAR | HIGH |
| **f34v** | MODERATE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f39r** | AGGRESSIVE | MODERATE | MEDIUM | EXTENDED | HIGH |
| **f39v** | MODERATE | MODERATE | MEDIUM | EXTENDED | MODERATE |
| **f40r** | MODERATE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f40v** | CONSERVATIVE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f41r** | MODERATE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f41v** | CONSERVATIVE | HEAVY | LOW | REGULAR | MODERATE |
| **f43r** | MODERATE | MODERATE | MEDIUM | EXTENDED | MODERATE |
| **f43v** | CONSERVATIVE | MODERATE | MEDIUM | EXTENDED | LOW |
| **f46r** | AGGRESSIVE | MODERATE | MEDIUM | EXTENDED | HIGH |
| **f46v** | MODERATE | MODERATE | MEDIUM | EXTENDED | MODERATE |
| **f48r** | CONSERVATIVE | HEAVY | LOW | REGULAR | LOW |
| **f48v** | CONSERVATIVE | HEAVY | LOW | REGULAR | LOW |
| **f50r** | CONSERVATIVE | HEAVY | MEDIUM | REGULAR | MODERATE |
| **f50v** | CONSERVATIVE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f55r** | AGGRESSIVE | MODERATE | MEDIUM | REGULAR | MODERATE |
| **f55v** | MODERATE | MODERATE | LOW | REGULAR | HIGH |

---

## Distribution Summary

### Aggressiveness Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| AGGRESSIVE | 6 | 25.0% |
| MODERATE | 10 | 41.7% |
| CONSERVATIVE | 8 | 33.3% |

### LINK Class Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| SPARSE | 1 | 4.2% |
| MODERATE | 17 | 70.8% |
| HEAVY | 6 | 25.0% |

### Hazard Proximity Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| HIGH | 1 | 4.2% |
| MEDIUM | 18 | 75.0% |
| LOW | 5 | 20.8% |

### Duration Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| EXTENDED | 6 | 25.0% |
| REGULAR | 18 | 75.0% |

### Recovery Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| HIGH | 4 | 16.7% |
| MODERATE | 15 | 62.5% |
| LOW | 5 | 20.8% |

---

## Raw Numeric Values

| Folio | link_density | hazard_density | kernel_contact | intervention_freq | total_length |
|-------|--------------|----------------|----------------|-------------------|--------------|
| f26r | 0.396 | 0.554 | 0.604 | 7.48 | 260 |
| f26v | 0.504 | 0.496 | 0.496 | 4.19 | 355 |
| f31r | 0.295 | 0.664 | 0.705 | 5.38 | 298 |
| f31v | 0.469 | 0.515 | 0.531 | 4.76 | 305 |
| f33r | 0.319 | 0.639 | 0.681 | 9.19 | 216 |
| f33v | 0.340 | 0.630 | 0.660 | 11.36 | 430 |
| f34r | 0.381 | 0.581 | 0.619 | 5.91 | 430 |
| f34v | 0.413 | 0.560 | 0.587 | 5.89 | 441 |
| f39r | 0.327 | 0.635 | 0.673 | 8.30 | 617 |
| f39v | 0.399 | 0.591 | 0.601 | 6.50 | 562 |
| f40r | 0.392 | 0.567 | 0.608 | 6.85 | 293 |
| f40v | 0.419 | 0.522 | 0.581 | 3.80 | 301 |
| f41r | 0.404 | 0.585 | 0.596 | 4.51 | 371 |
| f41v | 0.452 | 0.484 | 0.548 | 6.38 | 279 |
| f43r | 0.416 | 0.586 | 0.616 | 5.14 | 762 |
| f43v | 0.421 | 0.540 | 0.565 | 3.69 | 515 |
| f46r | 0.344 | 0.623 | 0.653 | 9.48 | 516 |
| f46v | 0.408 | 0.573 | 0.591 | 6.44 | 524 |
| f48r | 0.478 | 0.476 | 0.521 | 5.06 | 252 |
| f48v | 0.459 | 0.493 | 0.541 | 4.83 | 269 |
| f50r | 0.453 | 0.522 | 0.547 | 5.41 | 296 |
| f50v | 0.423 | 0.532 | 0.577 | 5.71 | 328 |
| f55r | 0.336 | 0.590 | 0.644 | 9.25 | 347 |
| f55v | 0.412 | 0.489 | 0.564 | 7.60 | 283 |

---

*Metrics extracted from locked control_signatures.json without reference to plant morphology.*
