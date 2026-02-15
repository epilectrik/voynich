# C1049: Shared Vocabulary is Section-Universal Substrate

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** A<>B
**Phase:** A_B_SECTION_CORRESPONDENCE (Phase 367)
**Extends:** C946 (no material-domain routing), C506 (PP composition uniform)
**Relates to:** C752 (no section routing), C753 (constraint propagation pipeline)

---

## Statement

MIDDLEs shared between Currier A (as PP) and Currier B are significantly LESS section-concentrated in B than B-only MIDDLEs:

| Category | n | Mean Herfindahl | Median | % Uniform (<0.40) | % Concentrated (>0.80) |
|----------|---|----------------|--------|-------------------|----------------------|
| Shared (A PP ∩ B) | 329 | **0.701** | 0.594 | 11.2% | 40.1% |
| B-only (not in A PP) | 862 | **0.933** | 1.000 | 1.4% | 86.2% |

Mann-Whitney U=74060, p < 10^-6. The difference is massive: 86% of B-only MIDDLEs are section-concentrated vs only 40% of shared MIDDLEs. Shared MIDDLEs are the section-universal substrate; section-specific vocabulary is B-internal.

---

## Evidence

- Herfindahl index = sum of squared section fractions across B, H, S (range 1/3 to 1.0)
- 329 shared MIDDLEs (PP MIDDLEs from 111 A folios that also appear in B)
- 862 B-only MIDDLEs (present in B but not in any A folio's PP pool)
- Both distributions compared on all 3 viable B sections (B=20, H=32, S=23 folios)

---

## Interpretation

This explains the mechanistic basis of C946 (reach cosine 0.997) and C752 (no section routing). A folios cover all B sections uniformly because the shared vocabulary IS the section-universal layer of B. The section-specific vocabulary (86% concentrated in one section) is NOT accessible from A. A→B constraint propagation operates exclusively through the universal substrate, making section routing impossible at the vocabulary level.

The 329 shared MIDDLEs serve as a section-agnostic pipeline, while B's 862 section-specific MIDDLEs are generated internally. This is a structural partition: A provides universal operational capacity, B generates section-specific specialization.

---

## Method

- PP MIDDLE pools extracted per A folio via RecordAnalyzer
- B MIDDLE section distributions computed from Transcript token counts (H-track, labels excluded)
- Herfindahl computed per MIDDLE across 3 sections (B, H, S)
- C and T sections excluded (too few folios)

**Script:** `phases/A_B_SECTION_CORRESPONDENCE/scripts/ab_section_correspondence.py`
**Results:** `phases/A_B_SECTION_CORRESPONDENCE/results/ab_section_correspondence.json`
