# What We Claim / What We Do Not Claim

This document states the project's claims explicitly, with the evidence tier and constraint basis for each. It exists because the Voynich Manuscript attracts extraordinary claims, and readers deserve to know exactly where our confidence is high and where it is not.

For the full constraint system, see `context/CLAIMS/INDEX.md` (1,711 validated constraints).

---

## What We Claim

### Structural findings (Tier 0-2: proven from the data)

These claims are grounded in statistical evidence from the transcript. They do not depend on interpretation, domain identification, or historical comparison.

- **The manuscript's main text (Currier B) forms a closed executable grammar.** 479 token types collapse to 49 instruction classes with 100% coverage. No token falls outside the grammar. (C121, C124)

- **The grammar is governed by a single shared set of rules across all 83 folios.** There is no folio that uses a different grammar. The instruction classes, forbidden transitions, and macro-state dynamics apply universally. (C124, C531)

- **17 state transitions are structurally forbidden, organized into 5 hazard classes.** These are not rare — they are absent. The forbidden transitions partition into classes with near-orthogonal atom territories. (C109, C110, C1528-C1533)

- **The manuscript has a three-level safety architecture.** Level 1: vocabulary exclusion (certain constructions cannot be built). Level 2: hazard source typing (headed tokens have 0% hazard source rate). Level 3: transition prohibition (the 17 forbidden transitions). These are independent, redundant safety layers. (C1446, C1546, C1553-C1555)

- **Each line is a self-contained safety envelope.** Lines carry no state from previous lines. Within a line, operations follow a fixed positional grammar: specification opens, thermal work fills the middle, closure ends. (C1463-C1471)

- **The manuscript uses four structurally distinct registers (A, B, AZC, HT) sharing a common compositional substrate.** All four registers build tokens from the same 18 atoms but deploy them in different proportions. Pairwise Jaccard similarity of atom inventories is 0.895 or higher. (C1499, C1500-C1509)

- **The notation is not a natural language and not an ordinary cipher.** Language encoding tests: CLOSED (C132). Micro-cipher tests: 0/18 passed (C207). Reference rate to any known language: 0.19% (C130). The notation has no linguistic source text.

- **A simple Markov model using the discovered grammar reproduces 87% of measurable structure.** The M2.1 generative model passes 21/21 closure metrics. This means the grammar is sufficient to regenerate the data's statistical properties. (C1365)

### Domain identification (Tier 3: consistent with evidence, not proven by it)

These claims go beyond the structural data. They are the best current interpretation but could be wrong.

- **The grammar's structural properties align with thermal process control — most likely reflux distillation.** 28 tests across 4 test suites comparing the VMS structure to Hieronymus Brunschwig's *Liber de arte distillandi* (1500), the first printed distillation manual. The forbidden transitions map onto physical failure modes. The convergence behavior matches distillation physics. (F-BRU-001 through F-BRU-034)

- **The manuscript is best modeled as a multi-register technical control notation.** The four-register architecture (specification catalog, legality bridge, execution grammar, orientation layer) functions as a coordinated document stack for expert practitioners. (C1499, Phase 551)

- **No existing medieval document genre matches the VMS structural profile.** Eight genres compared across 7 dimensions; best match scores 2.5/7. Three VMS properties have zero historical precedent: structural safety architecture, multi-register architecture, formal operational grammar. We propose the classification OPERATIONAL CONTROL CODEX as an analytical category. (Phase 552)

---

## What We Do Not Claim

- **We do not claim plaintext translation.** No token has a proven English (or any language) equivalent. The structural reconstruction recovers formal operating logic, not natural-language content.

- **We do not claim exact substance identification.** The manuscript externalized material identity — the notation discriminates materials from each other but does not name them. The "semantic ceiling" (C171) means substance names are irrecoverable from the notation alone.

- **We do not claim exact product identification.** We cannot determine what the processes produce. The grammar specifies operations, not outcomes.

- **We do not claim exact apparatus schematics.** The structural evidence is consistent with circulatory thermal equipment (pelican alembics, reflux apparatus), but the manuscript describes how to *operate* apparatus, not how to *build* it.

- **We do not claim one-to-one Brunschwig equivalence.** The Brunschwig comparison is a structural parallel demonstrating domain alignment. It is not a claim that the VMS is a cipher for Brunschwig's text, nor that the two manuscripts describe the same specific processes.

- **We do not claim authorship or provenance proof.** The radiocarbon date (1404-1438) and structural properties are consistent with Central European guild workshop culture, but this is historical interpretation (Tier 3-4), not proof.

- **We do not claim that operational labels are proven translations.** When we label an atom "thermal" or a category "CONTAINMENT," these are interpretive labels for structurally validated clusters. They are consistent with the domain identification but are not recovered plaintext.

- **We do not claim that illustrations carry semantic content.** Illustration-text coupling tests show swap invariance (C138) — the illustrations are orientation aids, not information carriers.

- **We do not claim historical genre discovery.** OPERATIONAL CONTROL CODEX is a proposed analytical classification based on structural properties, not a recovered medieval native genre term. No medieval source describes such a genre.

---

## What Would Change Our Mind

The structural findings (Tier 0-2) are falsifiable. Here is what would overturn them:

- **A valid natural language decipherment** that produces coherent text in a known language and explains the grammatical regularities. (Would overturn C132)
- **A demonstration that the statistical patterns arise from a known cipher mechanism** applied to natural language. (Would overturn C207)
- **Evidence that the 49 instruction classes do not have 100% coverage** — tokens that fall outside all classes. (Would overturn C121)
- **A folio that uses a different grammar** from the other 82. (Would overturn C124)

The domain identification (Tier 3) is more easily revised:

- **A better-fitting domain** whose physics match the forbidden transitions, convergence behavior, and recovery architecture more closely than distillation. We would adopt it.
- **Evidence that the Brunschwig structural alignment is coincidental** — a non-distillation domain that matches equally well on the same test battery.

---

*Phase 553 | Part of the public documentation editorial pass*
*Based on 1,711 validated constraints across 589 research phases*
