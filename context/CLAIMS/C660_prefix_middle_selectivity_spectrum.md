# C660: PREFIX x MIDDLE Selectivity Spectrum

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

PP MIDDLEs are overwhelmingly PREFIX-promiscuous in B text. Of 128 testable MIDDLEs (>=10 B tokens), only 5 (3.9%) are locked to a single PREFIX (concentration >=0.95). The majority are promiscuous: 59 (46.1%) have max PREFIX fraction <0.50, meaning no single PREFIX dominates. Mean concentration = 0.562, median = 0.563. The contingency table (404 MIDDLEs x 36 PREFIXes) is 89.3% sparse: MIDDLEs use a limited but non-exclusive subset of PREFIXes.

One dramatic exception: QO-predicting MIDDLEs (k/t/p-initial) are 100% EN-PREFIX dominant (all 23 testable MIDDLEs have qo as dominant PREFIX). CHSH-predicting MIDDLEs are 52.9% EN-family dominant. Neutral MIDDLEs are 20.4% EN-family dominant. Lane x selectivity chi2=50.65, p<0.0001, Cramer's V=0.445.

B text uses more PREFIX combinations than A records show (B wider for 68 MIDDLEs vs A wider for 34, Jaccard mean=0.484).

## Evidence

- 404 MIDDLEs x 36 PREFIXes, 89.3% sparse, 21,642 B-side PP tokens
- Type-level exclusivity: 156/404 (38.6%) appear with only 1 PREFIX
- Token-level categories (128 testable, >=10 tokens):
  - Locked (>=0.95): 5 (3.9%)
  - Dominant (0.70-0.95): 35 (27.3%)
  - Bimodal (2 PREFIXes >=0.25): 29 (22.7%)
  - Promiscuous (<0.50): 59 (46.1%)
- Concentration: mean=0.562, median=0.563, min=0.179, max=1.000
- QO lane: 100% qo-PREFIX dominant (23/23)
- CHSH lane: 52.9% EN-family dominant (27/51)
- Lane x category: chi2=50.65, p<0.0001, V=0.445
- A vs B: Jaccard mean=0.484, B wider (68 vs 34)

## Interpretation

The B grammar freely recombines PREFIXes with MIDDLEs. Most PP MIDDLEs are not "owned" by a single PREFIX — they participate across multiple PREFIX contexts. The 38.6% type-level exclusivity is driven by low-frequency MIDDLEs (1-9 tokens) that simply haven't been observed with other PREFIXes. At sufficient sample size (>=10 tokens), only 3.9% are truly locked.

The QO lane is the exception: all QO-predicting MIDDLEs are locked to qo PREFIX, consistent with C649's deterministic partition. This means qo is not just a PREFIX but a dedicated channel for k/t/p-initial MIDDLEs.

C276 (28 exclusive) and C423 (80% exclusive) were measured on the full vocabulary at type level. At B-side token level for PP MIDDLEs specifically, exclusivity is 38.6% at type level and 3.9% at token-weighted level — substantially lower, because PP MIDDLEs are high-frequency items that get recombined.

## Cross-References

- C276: 28 MIDDLEs exclusive to single PREFIX (V=0.674) — measured on full vocab, not PP-specific
- C423: 80% PREFIX-exclusive MIDDLEs — type-level, full vocab
- C649: EN-exclusive MIDDLEs deterministic by initial character — confirmed by QO 100% lock
- C576: EN MIDDLE bifurcation (Jaccard=0.133) — C660 extends to all 404 PP
- C652: PP vocabulary CHSH-biased — consistent with CHSH dominance in neutral MIDDLEs

## Provenance

PREFIX_MIDDLE_SELECTIVITY, Script 1 (prefix_middle_inventory.py), Tests 1-4
