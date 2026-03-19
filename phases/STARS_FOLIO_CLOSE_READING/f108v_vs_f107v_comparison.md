# Extreme Pair Comparison: f108v (lowest h) vs f107v (highest h)

## Folio Profiles

| Metric | f108v (low-h) | f107v (high-h) |
|--------|---------------|-----------------|
| h_ratio | 0.055 | 0.124 |
| h_resid | -0.1012 (rank 1/23) | +0.0747 (rank 23/23) |
| k_ratio | 0.282 | 0.477 |
| Kernel | k=28.4% h=4.0% e=67.6% | k=48.3% h=9.9% e=41.8% |
| Balance | ESCAPE_DOMINANT | BALANCED |
| Tokens | 570 | 455 |
| Paragraphs | 9 | 20 |
| THERMAL % | 40.1% | 29.0% |
| Sister ratio | 0.571 | 0.769 |
| Bridge rate | 88.1% | 88.6% |

## Key Finding: The Monitoring Axis Is an Operational Philosophy

The two folios represent **different operational philosophies**, not the same program with a monitoring knob turned up or down.

### f108v: The Confidence Program
- 9 paragraphs, one massive (P9 = 21 lines, 230 tokens = 40% of folio)
- e-dominated (67.6%) — sustained cooling/stabilization
- When h appears, it's buried medially in compounds (not terminal)
- Near-balanced sister ratio (0.571) — passive monitoring when it monitors at all
- P9 is structurally anti-monitoring: long repetitive sequences with no natural pause points
- Philosophy: "Trust the process to run. Minimize interruptions."

### f107v: The Vigilance Program
- 20 paragraphs (8 single-line), none exceeding 18% of tokens
- Balanced kernel (k=48.3%, e=41.8%) — active heating + active cooling
- h appears in TERMINAL position of compounds (architecturally significant endpoint)
- Strong ch-bias (0.769) — active checkpoint testing (C929)
- Dedicated monitoring paragraphs: P2 (h=50%), P19 (h=33%), P10 (h=25%, zero e!)
- Philosophy: "Watch constantly. Never let the operator go long without assessing."

## Five Dimensions of Divergence

The monitoring difference manifests simultaneously across:

1. **Paragraph architecture** — concentrated (9 large) vs distributed (20 small)
2. **Kernel balance** — e-dominated vs balanced (k and e roughly equal)
3. **Monitoring mode** — passive/absent vs active/checkpoint
4. **Token morphology** — h buried medially vs h in terminal position
5. **Sister pair selection** — balanced ch/sh vs ch-dominant (active testing)

## Surprises

### 1. k/h Positive Correlation
The monitoring-rich folio is ALSO the k-rich folio. More heating → more need for monitoring. e-dominant cooling is inherently self-stabilizing and can afford less monitoring. This connects to C1740 (safety substitution).

### 2. P10's Zero-e Profile (f107v)
A paragraph with k=75%, h=25%, e=0%: "heat and watch" with NO programmed stabilization. The vigilant program occasionally trusts the operator with pure thermal work, delegating entirely to judgment. Selective trust, not blanket caution.

### 3. Bridge Rate Parity
Identical vocabulary sourcing (88.1% vs 88.6%) despite radically different programs. The monitoring difference is in deployment, not vocabulary.

### 4. f108v P9 as Active Anti-Monitoring
P9 isn't just low-monitoring — it's structurally designed to suppress monitoring interruptions. Long repetitive sequences with no pause points. The program says: "for this phase, keep going and do not look."

### 5. Sister Ratio Coherence
f107v's ch-dominance (active checkpoints) aligns with its high monitoring. f108v's balanced ch/sh means even its monitoring moments are more passive. The monitoring philosophy is self-consistent across amount AND character.

## Synthesis

The monitoring axis in Stars encodes **trust in the process**:
- f108v trusts the process to run autonomously
- f107v insists on watching

This is not a trivial h-counting effect. It is a complete operational strategy difference that manifests in paragraph granularity, kernel ecology, token morphology, PREFIX selection, and safety architecture simultaneously.

Validates: C1154 (h program-specific in Stars), C1755 (paragraph shape tracks monitoring, rho=+0.739)
