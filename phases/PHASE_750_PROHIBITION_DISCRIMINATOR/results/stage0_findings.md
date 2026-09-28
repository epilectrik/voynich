# Q3 Stage 0 — Cross-language invariance (PILOT)

**Verdict: PASS (does not abort) — qualitative prohibition-shape is language-invariant; F1-magnitude coder/language confound flagged for the crossed-coder fix.**

## Method
12 matched `_L`(Latin)/`_R`(Catalan) passage pairs from the SISMEL Spaggiari parallel edition
(facing-page, same passage in both languages). Each side extracted by a BLIND agent (neutral
file IDs, told nothing of the parallel pairing, the Voynich, or the hypothesis) — Latin sides by
two agents, Catalan sides by two different agents. 4 features per passage (F1 asymmetry,
F2 sequence-vs-compatibility, F3 unconstrained-op, F4 commitment-point), verbatim-evidenced.

## Result — same passage, Latin vs Catalan
| Feature | Cross-language agreement |
|---|---|
| F2 sequence-dominance | mean \|L−C\| = 0.14 — invariant |
| F3 unconstrained-op present | 10/12 agree |
| F4 commitment present | 10/12 agree (both 11/12 present) |
| F1 asymmetry magnitude | mean \|L−C\| = 0.23, **systematic Latin>Catalan (+0.225)** |

**Qualitative signature identical in both languages:** asymmetry-dominant 11/12, sequence-dominant
10–11/12, commitment-present 11/12. The procedure-shape is recoverable and language-stable — the
core premise that makes this method semantic (not surface-bound like the 8D matcher).

## The one flag (design issue, not a kill)
F1's systematic Latin>Catalan gap is **confounded with coder** (different agents per language) and
almost certainly **coder-variance on reciprocal alchemical constructs** — e.g.
*"when the spirit congeals the body dissolves; when the body dissolves the spirit congeals"*
(dissolution↔congelation cycles): Latin agents coded these as two directional rules, Catalan
agents as one symmetric pair. Same content (literal parallel translation), ambiguous coding rule —
not a true language effect.

**Fixes (folded into Stage 1):** (1) CROSSED CODERS — mixed-corpus/mixed-language batches so
coder-identity is not aligned with language or corpus; (2) tightened F1 rubric — code reciprocal
"when A→B, when B→A" as the count of DISTINCT directional implications stated; symmetric ONLY if
the text explicitly says the two states are interchangeable/order-free.

## Incidental
- **Risk A milder than feared:** only 2/24 passage-sides were low-density. The Testamentum's
  practical sections are denser with extractable procedure than its "intentionally vague"
  reputation implied — good for power.
- **No over-reading:** the aggregate Testamentum shape (asymmetric, sequence-dominant,
  commitment-bearing) resembles the Voynich signature, but that is meaningless until Stage 1 shows
  the features DISCRIMINATE distillation from metalwork. Stage 1 is the gate.
