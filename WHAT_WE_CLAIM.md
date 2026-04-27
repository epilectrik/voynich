# What We Claim / What We Do Not Claim

This document states the project's claims explicitly, with the evidence tier and constraint basis for each. It exists because the Voynich Manuscript attracts extraordinary claims, and readers deserve to know exactly where our confidence is high and where it is not.

For the full constraint system, see `context/CLAIMS/INDEX.md` (1,969 validated constraints).

---

## What We Claim

### Structural findings (Tier 0-2: proven from the data)

These claims are grounded in statistical evidence from the transcript. They do not depend on interpretation, domain identification, or historical comparison.

- **The manuscript's main text (Currier B) forms a closed executable grammar.** 479 token types collapse to 49 instruction classes with 100% coverage. No token falls outside the grammar. (C121, C124)

- **The grammar is governed by a single shared set of rules across all 83 folios.** There is no folio that uses a different grammar. The instruction classes, disfavored transitions, and macro-state dynamics apply universally. (C124, C531)

- **17 state transitions are structurally disfavored, organized into 5 hazard classes.** These transitions occur at ~65% compliance — strongly suppressed but not absolute. The disfavored transitions partition into classes with near-orthogonal atom territories. (C109, C789, C1528-C1533)

- **The manuscript has a three-level safety architecture.** Level 1: vocabulary exclusion (certain constructions cannot be built). Level 2: hazard source typing (headed tokens have 0% hazard source rate). Level 3: transition suppression (the 17 disfavored transitions, ~65% compliance). These are independent, redundant safety layers. (C1446, C1546, C1553-C1555)

- **Each line is a self-contained safety envelope.** Lines carry no state from previous lines. Within a line, operations follow a fixed positional grammar: specification opens, thermal work fills the middle, closure ends. (C1463-C1471)

- **The manuscript uses four structurally distinct registers (A, B, AZC, HT) sharing a common compositional substrate.** All four registers build tokens from the same 18 atoms but deploy them in different proportions. Pairwise Jaccard similarity of atom inventories is 0.895 or higher. (C1499, C1500-C1509)

- **The notation is not a natural language and not an ordinary cipher.** Language encoding tests: CLOSED (C132). Micro-cipher tests: 0/18 passed (C207). Reference rate to any known language: 0.19% (C130). The notation has no linguistic source text.

- **A simple Markov model using the discovered grammar reproduces 87% of measurable structure.** The M2.1 generative model passes 21/21 closure metrics. This means the grammar is sufficient to regenerate the data's statistical properties. (C1365)

- **Every token decomposes into operational atoms with 100% coverage.** The HEAD+MOD*+TERM architecture (C1394) with 18 atoms at four confidence tiers (C1195) produces readable operational descriptions for all 23,096 Currier B tokens. (C1897)

- **Specific tokens encode identifiable operational functions across multiple independently-matched folios.** `dar` (da+r) = material introduction — present on all folios matched to recipes introducing new materials, absent on all folios matched to cohobation/separation-only recipes (6/6 partition, C1925). `chekar` (ch+ek+ar) = post-thermal quality check — appears in structurally identical context across 7/83 folios (C1926).

- **The manuscript encodes only procedural content.** Full-spectrum scan of all 209 *Testamentum* chapters: 96 theoretical chapters and 30 furnace-specification chapters produce zero atom-validated matches. Only procedural Practica and Mercuriorum chapters match. (C1932)

### Historical source tradition (Tier 2-3: framework established, specific assignments interpretive)

These claims combine structural evidence (Tier 2) with interpretive identification (Tier 3). The structural matching is validated; the specific recipe assignments could be revised by new evidence.

- **The best-fit historical source tradition is Pseudo-Lullian alchemy.** Statistical matching using 8 locked feature dimensions identifies the *Testamentum*'s Practica and Liber Mercuriorum as the source, calibrated independently against Brunschwig's distillation manual (1500). 10-dimension permutation test: 0/10,000 shuffles, p<0.0001 (C1956). Cross-family replication confirmed (C1885). Wrong-regime negative control collapses (C1886). (Tier 2 for the matching framework; Tier 3 for the specific PL identification)

- **51 procedural chapters from the *Testamentum* match to 41 folios, covering 96% of expanded procedural content (53 chapters).** 3 confirmed by independent structural evidence (f75r/Ch19, f76r/Ch18P, f84r/Ch14P); 5 via reverse-blind prediction (C1935); 4 via fch (mercury marker) hard-filter matching (C1943-C1945, C1952); 1 via cs (gold marker) hard-filter (C1947); 4 via recto/verso systematic scan (C1948, C1953-C1955); the remainder at supported or speculative confidence. Multi-chapter folios combine related short procedures (C1937); sequential operations appear on recto/verso pairs (C1936). Individual assignments are Tier 3. The matching framework was trained on distillation chapters; cross-family generalization adds +7% distance penalty (C1933). Phase 638 reclassified 6 higher Mercuriorum chapters from "theoretical" to "procedural" based on Latin verb counting (C1946).

- **The manuscript's sections map to *Testamentum* book divisions.** Section B folios f75-f84 correspond to Liber Mercuriorum preparation chapters (Ch1-28). Section S folios f103-f116 correspond to transmutation/multiplication chapters (Ch40+). The ordering follows product chains, not book order. (C1927, C1930 — Tier 2 for the clustering, Tier 3 for the specific mapping)

- **A product chain links folios across the manuscript.** f75r (Ch19 aqua vitae / quintessence) produces the input for f84r (Ch14 gold dissolution, which requires "vegetable G" = quintessence per the *Testamentum*'s cipher key). Parallel mineral and animal production chains converge at medical administration. (C1928 — Tier 3)

### Structural domain alignment (Tier 3: consistent with evidence, not proven by it)

- **The grammar's structural properties align with thermal process control.** 28 tests across 4 test suites comparing VMS structure to Brunschwig's *Liber de arte distillandi* (1500). Forbidden transitions map onto physical failure modes. Recovery architecture matches Brunschwig's bounded retry rule. Fire degrees correlate with stability proxy. (F-BRU-001 through F-BRU-034)

- **The manuscript is best modeled as a multi-register technical control notation.** The four-register architecture functions as a coordinated document stack for expert practitioners. (C1499, Phase 551)

- **No existing medieval document genre matches the VMS structural profile.** Eight genres compared across 7 dimensions; best match scores 2.5/7. We propose the classification OPERATIONAL CONTROL CODEX as an analytical category. (Phase 552)

---

## What We Do Not Claim

- **We do not claim plaintext translation.** No token has a proven English (or any language) equivalent. The atom glosses describe operational functions within the control grammar, not natural-language content. (C171: semantic ceiling)

- **We do not claim exact substance identification from tokens alone.** `dar` identifies a material-introduction EVENT but not WHICH material. `chekar` identifies a quality-check EVENT but not what is being checked. The notation discriminates materials from each other but does not name them — material identity was externalized to the practitioner's knowledge. (C120: PURE_OPERATIONAL)

- **We do not claim exact product identification from tokens alone.** The product chain (quintessence → gold tincture) is established through the *Testamentum*'s cipher key, not through reading Voynich tokens as product names. Without the external text, the tokens would reveal only that one folio's output feeds another folio's input.

- **We do not claim text equivalence with the *Testamentum*.** The VMS is not a cipher for the *Testamentum* text. It encodes the same operational CONTENT in a completely different notation system, reorganized for workshop use. The relationship is content correspondence, not textual derivation.

- **We do not claim that operational glosses are proven translations.** When we label an atom "heat" or a category "CONTAINMENT," these are interpretive labels for structurally validated clusters. They are consistent with the domain identification but are not recovered plaintext. (C171)

- **We do not claim authorship or provenance proof.** The radiocarbon date (1404-1438) and structural properties are consistent with Central European guild workshop culture, but this is historical interpretation (Tier 3-4), not proof.

- **We do not claim that all folios are Pseudo-Lullian.** 51 procedural chapters map to 41 folios (50% of 82 Currier B folios). The remaining 41 unmatched folios (mostly Section H herbal pages) use the same grammar and operational vocabulary but have not been matched to specific source chapters. They may correspond to other Pseudo-Lullian texts, herbal distillation traditions, or workshop-specific procedures.

- **We do not claim that illustrations carry semantic content.** Illustration-text coupling tests show swap invariance (C138) — the illustrations are orientation aids, not information carriers.

---

## What Would Change Our Mind

The structural findings (Tier 0-2) are falsifiable. Here is what would overturn them:

- **A valid natural language decipherment** that produces coherent text in a known language and explains the grammatical regularities. (Would overturn C132)
- **A demonstration that the statistical patterns arise from a known cipher mechanism** applied to natural language. (Would overturn C207)
- **Evidence that the 49 instruction classes do not have 100% coverage** — tokens that fall outside all classes. (Would overturn C121)
- **A folio that uses a different grammar** from the other 82. (Would overturn C124)

The historical identification (Tier 2-3) is more easily revised:

- **A better-fitting source tradition** whose operational features match the 8D feature space more closely than the *Testamentum*. We would adopt it.
- **Evidence that the *Testamentum* postdates the manuscript's radiocarbon window** (currently compatible: PL tradition active 1330s-1500s, manuscript 1404-1438).
- **Evidence that the 8D matching features are artifacts of an uncontrolled confound** rather than genuine operational correspondence.
- **A demonstration that the section-to-book mapping (f75-f84 = Mercuriorum) is coincidental** — e.g., that any 11 contiguous folios would match a single PL book at 8/11 by chance.

---

*For the full constraint system, see `context/CLAIMS/INDEX.md`. For the conceptual walkthrough, see [GUIDE.md](GUIDE.md).*
