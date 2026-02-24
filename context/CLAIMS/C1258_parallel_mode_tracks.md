# C1258: Parallel Mode Tracks

**Tier:** 2
**Scope:** B
**Phase:** SEQUENTIAL_CONTENT_PREDICTION (Phase 450)
**Date:** 2026-02-24

## Statement

Mode A and Mode B lines within paragraphs form coupled parallel sequential tracks. Mode B lines show within-track vocabulary continuity (Jaccard 0.197 vs null 0.179, 1.10x, p=0.000), kernel profile continuity (cosine 0.874 vs null 0.851, p=0.000), and FL stage continuity (cosine 0.572 vs null 0.541, p=0.001). Mode A lines show weaker or no within-track continuity (vocabulary p=0.692, kernel p=0.054, FL p=0.991). Cross-mode coupling is also significant: A lines predict the following B line's kernel profile and vice versa (A→B rho=0.189, p=0.000; B→A rho=0.208, p=0.000). Within-mode coupling is stronger than cross-mode coupling (Jaccard 0.188 vs 0.164, p=0.000). Result: 5/5 tests PASS.

## Architecture

- **Mode B = continuous track.** Maintains state across interleaved A-line interruptions. Sequential vocabulary, kernel, and FL continuity. The foundational thread of the paragraph.
- **Mode A = specification injections.** Interrupts the B track to inject new parameters. Each A-line is relatively independent of the previous A-line. The directed-change voice.
- **Coupled counterpoint.** A influences B's next state (specification takes effect), and B's current state influences A's next specification (feedback). Neither track is independent.

## Key Findings

| Test | Within-A | Within-B | Cross-mode | Verdict |
|------|----------|----------|------------|---------|
| Vocabulary (Jaccard) | 0.174 (p=0.692) | 0.197 (p=0.000) | 0.164 | B-track only |
| Kernel (cosine) | 0.869 (p=0.054) | 0.874 (p=0.000) | 0.856 | B-track + borderline A |
| FL stage (cosine) | 0.466 (p=0.991) | 0.572 (p=0.001) | 0.529 | B-track only |
| Cross-mode coupling | — | — | A→B=0.189, B→A=0.208 (both p=0.000) | Bidirectional |
| Within vs cross | 0.188 within | — | 0.164 cross (p=0.000) | Within > cross |

- 174 paragraphs with 4+ body lines (terminal lines excluded)
- 467 Mode A lines, 680 Mode B lines (non-terminal)
- 315 within-A pairs, 509 within-B pairs, 425 cross-mode pairs

## Resolves

- C670 (no adjacent-line vocabulary coupling) → C670 tested adjacent lines which are typically cross-mode; within-mode pairs (skipping interleaved lines) DO show coupling
- C1229 (alternating suffix modes, 80% non-contiguous) → the interleaving pattern is not random alternation but structured counterpoint between two coupled tracks

## Implications

The B-language paragraph is written in two voices: a continuous operational track (Mode B) and a punctuating specification track (Mode A). This counterpoint architecture explains why C670 found no adjacent-line coupling — it was measuring across voices rather than within them.

## Method

Within-mode pairs: for each line, find the next line of same mode within the paragraph (skipping interleaved opposite-mode lines). Cross-mode pairs: adjacent lines of different modes. Terminal lines (last body line) excluded per user specification. Permutation null: shuffle mode labels within each paragraph (1000 permutations). 5 tests, all significant at p < 0.005.

## Provenance

- Phase 450 parallel tracks follow-up: T1-T5 (all PASS)
- Builds on C1229 (mode alternation), C1231 (mode centroids), C959 (opener role), C670 (line independence)
