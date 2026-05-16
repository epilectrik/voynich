# Paper Notes

Stable reference set for the Voynich 2026 Conference paper.

This file consolidates paper-drafting decisions, target-venue details, prior-work citation handling, methodology framing, research chronology audit, public-documentation overclaim audit, and language discipline patterns.

Separated from `PENDING_TESTS.md` (which stays focused on research hypothesis predictions and their outcomes).

---

## Strategy

### PUB-001: Methodological-novelty paper framing — the "Category 3 gap" in Voynich scholarship
- **Context:** Strategic thinking about how to eventually publish this work given (a) anti-AI sentiment in Voynich field, (b) history of failed decipherment claims (Newbold, Bax, Gibbs, Cheshire), (c) user has already emailed repo to top researchers establishing priority, (d) need to position work defensibly without overclaiming.
- **Key insight (from conversation 2026-04-18):** Voynich scholarship has a methodological gap that our work fills:
  - **Category 1 (accepted, content-neutral):** Structural analyses tying folios together by scribal hand, statistical properties, codicological features. Examples: Currier (A/B hands), Landini (Zipf/word-length), Zandbergen (structural+codicological).
  - **Category 2 (mostly wrong, narrow scope):** Content-level decipherment claims. Newbold (whole manuscript, fabricated), Bax (10 words, cherry-picked), Gibbs (few abbreviations, wrong), Cheshire (broad but unrigorous).
  - **Category 3 (the gap — previously unoccupied):** Systematic content-level claims spanning multiple folios with statistical validation and external source-text anchoring.
- **Our work fills Category 3 via the combination of:**
  1. Systematic matching methodology (not anecdotal)
  2. 15-16 folio-recipe pairs (population-size, not single-case)
  3. Pre-computed token glosses (independent derivation before matching; C1195, C1394)
  4. External source text (Testamentum — specific, historically grounded)
  5. Permutation-validated correspondence (10,000-shuffle significance tests)
  6. Cross-operation-class generalization (distillation, maceration, vessel spec, cohobation)
  7. Falsifiable predictions (pre-registered)
  8. Documented self-correction (PT-027 → PT-028 → PT-029 arc)
- **Recommended paper framing (NOT a decipherment claim):**
  - **Title (approximate):** "Structural Correspondence Between Currier B Folios and Pseudo-Lull Testamentum Recipes: A 10,000-Permutation Test"
  - **Main claim (narrow + statistically-anchored):** 15-16 folio-recipe pairings show structural correspondence exceeding random pairing at p<0.001 across 10,000 permutation trials. Individual-folio interpretations are tentative; set-level correspondence is robust.
  - **Evidence structure:** permutation test as primary evidence, individual cases (f75r/Ch19M most developed) as illustrative supporting examples, NOT as load-bearing claims.
  - **Positioning:** extends Currier/Landini/Zandbergen methodological tradition by adding content-level dimension while maintaining statistical rigor. Explicitly distinguish from Bax/Gibbs/Cheshire cherry-picking by reference to pre-computed glosses + permutation test + leave-one-out robustness.
  - **Limitations section must include:** PT-028 calibration issues, single-interpretation uncertainties, workshop-adaptation complexity, alternative source texts not definitively ruled out.
- **Key rhetorical move:** Don't claim decipherment. Claim "first systematic content-level analysis with statistical validation in the manuscript's research history." Methodological firsts get cited even when specific claims get revised (cf. Currier's A/B work). Decipherment claims get debunked (cf. Cheshire).
- **What to DE-emphasize in paper writing:**
  - "AI-assisted" anything (describe as "computational corpus analysis")
  - Broad decipherment language ("solved," "decoded," "translated")
  - Strong claims about specific material identities (respect C171 semantic ceiling)
  - Single-folio anecdotes without set-level context
- **Target venues (ranked):**
  1. **Ambix** — Society for History of Alchemy and Chemistry. Specializes in alchemical manuscript studies. Reviewers would understand operational recipe analysis. Best fit.
  2. **Cryptologia** — publishes Voynich statistical work historically. Permutation-test papers align with their tradition.
  3. **Early Science and Medicine** (Brill) — history of science including alchemy.
  4. **Digital Humanities Quarterly** — open-access, methods-friendly.
  5. **PLOS ONE** — accepts methodology papers, low scope-expectation.
- **Preprint first:** arXiv (cs.CL or stat.AP) or Zenodo with DOI. Establishes dated priority without peer-review gatekeeping. User's existing emails to top researchers already establish priority; preprint formalizes it.
- **Credentials/affiliation:** "Independent Researcher" is a valid affiliation. ORCID ID (free) adds legitimacy. No credential gatekeeping at most journals; desk-rejection rate elevated ~20-30% for uncredentialed but not categorical. Historical precedents: Einstein (patent clerk), Perelman (unaffiliated), Mendel (provincial monk).
- **Workshop-adaptation hypothesis** (discussed 2026-04-18 conversation): The paper should acknowledge that Voynich encoding is workshop-specific adaptation of Testamentum recipes, not literal text transcription. This explains count-encoding inconsistencies (operator-specific counting), aspectual vs. enumerative distinction, and why no single folio maps 1:1 to a recipe. This is a more defensible and more sophisticated thesis than direct encoding.
- **Evidence that Testamentum IS specifically the source (not just a tradition):**
  - Preserved ordering between Testamentum chapters and matched folios
  - Ch18M→Ch19M presupposition encoding (f81v→f75r recipe-DAG)
  - Multi-chapter folios (f80r = Ch21-25M) preserving Testamentum chapter-sequence
  - Testamentum uniquely integrates Theorica+Practica+recipes in the way the manuscript appears to
  - Specific vocabulary matches (lunaria as starting material, mercury preparations, vessel specification)
- **Self-correction as strength, not weakness:** The PT-027→PT-029 arc documenting overclaim-then-walk-back is CREDIBILITY-BUILDING, not reputation-damaging. Distinguishes our methodology from Cheshire (never retracted), Gibbs (never retracted), Bax (never retracted). Explicitly frame this in the paper.
- **Status:** Strategic framing for eventual paper submission. Not currently being drafted. To execute: after SISMEL arrives and initial Catalan validation work done, draft a 8-15 page methods-forward paper with set-level claim + individual case studies + explicit limitations + falsifiable predictions. Submit to Ambix or Cryptologia. Total effort estimate: 40-80 hours.
- **Session:** 2026-04-18 (strategic discussion after PT-029 direct-reading verification)

---

## Target venue

### PUB-002: Voynich 2026 International Conference — primary submission target
- **Conference:** 2026 International Conference on the Voynich Manuscript (DEDICATED EXCLUSIVELY TO VOYNICH — not a general conference)
- **Date:** Wednesday, December 9, 2026 (online)
- **Host:** University of Malta (Valletta Campus)
- **Chair:** Dr. Colin Layfield (Senior Lecturer, University of Malta)
- **Co-Chair:** Prof. John Abela (Associate Professor, University of Malta)
- **Program Committee:** international — Yale, Utrecht University, University of Iceland, University of Texas at Austin, European Space Agency, and independent researchers specializing in linguistics/cryptography/manuscript analysis (independent researchers EXPLICITLY on the committee — accepts non-credentialed submissions)
- **Website:** https://www.um.edu.mt/events/voynich2026/
- **Contact:** voynich2026@um.edu.mt
- **Submission platform:** EasyChair — https://easychair.org/conferences/?conf=voy2026
- **Stated objective:** "Provide researchers with the opportunity to present their research and work on the Voynich manuscript." Researchers can present findings, learn about current scholarship, and network with the investigation community focused on this historical document.
- **Key timeline:**
  - Abstract/summary deadline: **June 30, 2026 (11:59 CEST)** — ~10 weeks from session date (2026-04-18)
  - Acceptance notification: July 24, 2026
  - Full paper deadline: August 31, 2026
  - Final acceptance: October 1, 2026
  - Video presentation deadline: November 9, 2026
- **Submission requirements:**
  - Abstract: max 750 words
  - Full paper: 5-9 pages using CEUR-ART templates (LaTeX or LibreOffice)
  - 20-minute pre-recorded video presentation + live Q&A
  - Must be unpublished work
  - At least one author must register and present
- **Accepted research areas:** historical approaches and ciphers, NLP techniques, AI/ML applications, image processing, hoax vs. natural language discussions, digital humanities methods
- **CRITICAL policies:**
  - **Decipherment claims EXPLICITLY REJECTED** — "Proposed manuscript 'solutions' are rejected." This aligns perfectly with our methods-forward framing (PUB-001). Must avoid decipherment language.
  - **Generative AI text generation PROHIBITED.** Grammar/translation tools exempt. AI-assisted content requires disclosure. Paper prose must be human-written; AI can be research assistant but not author.
  - Open about AI tool USE (for analysis) is fine with disclosure
- **Why this venue is ideal:**
  - Methods-forward framing explicitly welcomed (NLP/AI/ML/DH)
  - Decipherment-rejection policy PROTECTS our framing (we're not trying to "solve" anyway)
  - Medieval Academy institutional backing adds credibility
  - Online format reduces travel cost
  - International audience
  - December 2026 timeline allows full SISMEL validation work before submission
- **Strategic plan:**
  - Phase 1 (late April-May 2026): Complete SISMEL Catalan validation work when book arrives
  - Phase 2 (May-June 2026): Draft 750-word abstract for June 30 deadline
  - Phase 3 (July-August 2026): If accepted, write 5-9 page paper
  - Phase 4 (September-November 2026): Prepare video presentation
  - Phase 5 (December 9 2026): Present
- **Abstract content draft (tentative):**
  - Title: "Computational Corpus Analysis of Currier B Folios: Structural Regime Separation and Testamentum-Tradition Correspondence"
  - Lead findings: PT-019 regime cluster + PT-020 three-part vocabulary + f75r/Ch19M multi-channel alignment
  - Framing: methods extension of Currier/Landini/Zandbergen tradition, explicitly complementary to Pereira (2002)
  - Emphasize: pre-registered predictions, self-correction documentation, permutation testing, workshop-adaptation hypothesis
  - De-emphasize: "decipherment," "solve," broad claims, AI generative tooling
- **Paper constraints (5-9 pages) force tight scope:**
  - Cannot cover full matched set in depth
  - One flagship case (f75r/Ch19M) + set-level statistics
  - Supporting examples as tables/figures not full discussion
  - Most PT-series findings compressed to methodology + results sections
- **Author affiliation:** "Independent Researcher, [location]" — conference accepts independent submissions per their CFP
- **AI disclosure plan (when submitting):** state clearly that AI models (specifically Claude Opus 4.6/4.7) were used as research assistants for structural analysis, corpus extraction, and statistical validation. State that prose is human-authored. This meets the disclosure requirement without violating the generative-text prohibition.
- **Risk factors:**
  - High rejection rate expected (most conference submissions rejected)
  - "Decipherment-rejection" policy could catch us if reviewers interpret our work as decipherment-adjacent
  - AI-disclosure requirement could trigger skeptical reviewing even for legitimate methods
  - 5-9 page constraint is tight for the evidence we have
- **Backup venues if rejected:** Cryptologia (Voynich statistical work has long history there), Ambix (alchemical manuscript studies), arXiv preprint as priority-preserving fallback
- **Status:** Primary near-term publication target. Concrete deadlines. Realistic timeline given SISMEL arrival this week.
- **Session:** 2026-04-18

---

## Citations and methodology framing

### PUB-003: Paper prior-work citations and methodology-framing decisions
- **Purpose:** Lock in citation handling and methodology-framing decisions for the Voynich 2026 Conference paper so the paper draft has stable references. Covers: (a) how to cite parallel/prior Voynich work, (b) how to frame atom-gloss-based matching without triggering the conference's "no decipherment" policy.

**Part A: Prior-work citations**

- **Earnhart, D. (2026)** — "The Voynich Manuscript Isn't a Language. It's a Paper Computer." Medium, January 4, 2026. https://medium.com/@derekearnhart711/the-voynich-manuscript-isnt-a-language-it-s-a-paper-computer-9a0c72822b5a
  - **Citation approach:** Cite as **parallel framing work**, no ordering claim. Recommended wording: "A similar high-level framing — the manuscript as a system encoding procedures for trained operators — has been proposed by Earnhart (2026). The present work develops this class of interpretation through a distinct methodology..."
  - **Rationale:** Conceptual overlap is real (paper computer / trained operators / procedures vs. our control grammar / trained operators / operations). Earnhart published in January 2026; our repo went public in February 2026. Git commits predate his publication internally but the repo was private when he published — so formal public priority goes to him. Practical reality: nobody was watching either way, so priority is functionally unresolvable. Decision: don't litigate; cite as parallel independent work.
  - **Flip the framing:** Two researchers with different methods arriving at similar interpretations = modest evidence that the framing tracks something real in the manuscript, not a Rorschach artifact. This is rhetorically stronger than priority.
  - **Do NOT cite his Harmonic Constraint Solver (HCS)** as methodology. HCS is a single scalar metric (Φ = U_rigidity − S_Shannon/τ) with no empirical validation in the article. Branding oversells substance. Not methodologically comparable to our work.

- **O'Donovan, D. — "Pharma" series (Voynich Revisionist, 2021)** — https://voynichrevisionist.com/2021/08/09/pharma-pt-2-i-the-legend/
  - **Citation approach:** Read before paper draft. Cite if specific observations overlap with yours. O'Donovan has been at Voynich research for years, is respected as an independent researcher, and specifically focuses on the pharmaceutical section.
  - **Rationale:** Being caught unaware of her work by a reviewer would be a bad look. Being prepared to engage with it demonstrates scholarly due diligence.

- **Hartlieb / "Encipherment of Women's Secrets" paper** — *Social History of Medicine*, Oxford Academic. https://academic.oup.com/shm/article-abstract/37/3/559/7633883
  - **Citation approach:** Brief citation in prior work section as example of peer-reviewed academic engagement with Voynich-as-medical-text interpretations. Different specific framing (gynecological) from yours but same genre-space (pharmaceutical/medical).
  - **Rationale:** Adds academic respectability to the genre-framing by showing peer-reviewed venues accept this interpretive direction.

- **Cheshire / Gibbs / Bax / d'Imperio / Pelling / Davis** — standard Voynich-solution-attempt lineage
  - **Citation approach:** Brief mention in prior-work section establishing (a) prior "solution" attempts have not held up under scrutiny, (b) your work is methodologically different — measurement via reproducible pipeline, not translation. Don't dismiss uncharitably — acknowledge that failed attempts have informed paleography/dating.

- **Timm & Schinner** — statistical characterization work (2020, published in CEUR-WS Vol-3313 from 2022 Malta conference)
  - **Citation approach:** Cite as precedent for statistical-structural Voynich analysis in the same conference venue. Demonstrates that your paper's genre is welcomed by this specific conference.

- **Stolfi (1997-2000)** — word-grammar decomposition (prefix/midfix/suffix → core/mantle/crust)
  - **Citation approach:** Cite as precursor to HEAD+MOD+TERM atom system. Stolfi's soft/hard letter partition is a proto-version of the HEAD/TERM distinction. Generous citation expected by the Voynich community.

- **Griffonage-Dot-Com (Rabin, 2021)** — "Transitional Probabilities in the Voynich Manuscript"
  - **Citation approach:** Cite for documented prior work on transition-level constraints. Our specific 17-transition taxonomy + 5-class clustering is a refinement of the genre-level phenomenon he documented.

- **Montemurro & Zanette (PLOS ONE 2013)** — keywords and co-occurrence, information-theoretic analysis
  - **Citation approach:** Cite as precedent for information-theoretic analyses of Voynich structure.

- **Amancio et al. (arXiv 1611.09122, 2016)** — statistical properties of European languages and Voynich
  - **Citation approach:** Cite as prior statistical characterization work.

- **Uncontested priority territory** (no competing publications found):
  - Brunschwig *Liber de arte distillandi* as structural-alignment target
  - Pseudo-Lull *Testamentum* as source corpus with statistical recipe matching
  - 8D feature matching pipeline for recipe-folio correspondence
  - Constraint-system methodology with tier discipline
  - The specific 5-class hazard taxonomy and its integration with atom-compositional structure (the transition phenomenon itself has precedent — Stolfi, Rabin, Zandbergen — but the specific taxonomy and interpretive framing is ours)

**Part B: Methodology framing (threading the "no decipherment" policy)**

The conference policy explicitly rejects "proposed manuscript solutions" / decipherment claims. Our 8D pipeline makes operational-semantic hypotheses at atom-class granularity (e.g., pairing k_ratio with heat_rate) — these are interpretive assignments, not pure structural counts. The framing must distinguish this from traditional token-level decipherment.

- **Core distinction:** Atom-class → operational-domain assignment is *structural-functional hypothesis testing* (legitimate NLP/corpus-linguistics methodology), NOT *token-level decipherment* (what the policy rejects). Topic models, word embeddings, and feature-labeled classifiers all make similar operational-semantic assignments.

- **What the paper claims:** Empirical correspondence between structural token features and operational recipe features, at permutation-validated statistical significance.

- **What the paper does NOT claim:**
  - Token-level translation (no token = natural-language word)
  - Plaintext recovery (no readable text produced)
  - Material identification (no plants/minerals/substances named)
  - Solution in the Cheshire/Gibbs/Bax sense

- **Three things that make the framing defensible:**
  1. **Constrained assignment, not invention** — atom-class-to-operation pairings are forced by compositional analysis (atom classes cluster distinctly in the grammar with specific structural properties), not arbitrary labeling
  2. **Cross-folio consistency as blind validator** — same atom-class pairings work across 41 independently-matched folios; if arbitrary, they wouldn't produce consistent correspondence
  3. **Permutation test as formal defense** — 0/10,000 shuffles achieve comparable match quality; arbitrary labeling would shuffle-equivalent

- **Key language discipline (ban these words in paper's own voice):**
  - "decode," "decipher," "solve," "crack"
  - "translate," "translation," "reading" (in interpretive sense)
  - "the Voynich says..." / "means..." / "is" (for interpretive claims)
  - "breakthrough," "finally," "key to"
  - Any claim about authorship, intent, or identity

- **Replacement vocabulary:**
  - "match," "correspond," "align," "correlate"
  - "structural correspondence" / "statistical association"
  - "consistent with" / "analogous to"
  - "evidence for" (bounded) / "measurement"

- **Paper structural moves:**
  1. **Lead with empirical result** (permutation-validated matching) before detailing the pipeline — anchors reviewer on "measurement" framing before interpretive layer
  2. **Describe atom features structurally in methods, not semantically** — e.g., "we measure the rate of tokens whose HEAD atom is from the k-class (characterized by 0% hazard source rate, y/d-terminal preferences, thermal-regime enrichment)" — note operational label only after structural definition
  3. **Handle interpretive layer in discussion**, not methods — "The atom-class assignments function as operational feature labels; they are hypotheses constrained by compositional structure and validated by external correspondence, not token-level translations."
  4. **Include explicit non-claim paragraph**: "We do not claim token-level translation, material identification, plaintext recovery, or linguistic decipherment. We claim that an operational-feature correspondence exists between Voynich folios and candidate recipe chapters at permutation-validated statistical significance, via a pipeline that assigns structural token classes to operational feature categories based on compositional structure and cross-folio consistency."
  5. **Include explicit falsifier paragraph**: "What would overturn these findings: independent re-implementation producing materially different results; SISMEL Catalan edition diverging substantially from Latin baseline; permutation tests on shuffled source corpora producing comparable match rates; blind re-encoding tests showing gloss-atom assignments are artifacts of our choices."

- **Defense language if challenged on decode-policy:**
  > "So does every topic model. The atom-class-to-operation assignment is constrained by compositional structure, falsifiable via permutation, and empirically validated. It is not a solution claim; it is hypothesis testing at atom-class granularity. The analysis identifies operational function, not material content (semantic ceiling: C171). No token is mapped to a natural-language word."

- **Scope decision — Currier B only:**
  - Paper focuses on Currier B (where all 41 matches live and all permutation tests run)
  - Currier A and AZC acknowledged as architecturally distinct subsystems with their own properties (catalogue/index and transit/activation layers, respectively)
  - NO recipe-level claims for A or AZC folios in paper
  - Rationale: methodology doesn't trivially transfer across subsystem architectures; defensible core = B

- **Status:** Decisions locked for paper draft. Will apply when paper drafting starts (May-June 2026, after SISMEL validation work).
- **Session:** 2026-04-19

---

## Language discipline patterns

### LANG-001: Interpretive vocabulary as definitional language (pattern across multiple docs)
- **Purpose:** Identify a recurring pattern across the project's public docs where interpretive labels (originally intended as cluster descriptors) get treated as empirical findings and propagated as definitional language. This pattern must be corrected uniformly when drafting the paper.
- **Three instances of the pattern:**

  **1. Atom glosses treated as meanings**
  - k=heat, e=cool, etc. are originally cluster labels for atoms with distinct structural properties (0% hazard for k-HEAD, etc.)
  - Synthesis docs propagate these as if they were translations
  - Paper must frame as operational feature labels, not meanings
  - See PUB-003 Part B for framing guidance

  **2. "Safety architecture" / "executable" / "program" used as definitional vocabulary**
  - Tier 2-3 interpretive framings get used throughout README, GUIDE, ARCHITECTURE, WHAT_WE_CLAIM without hedging
  - Paper must use these as hypothesized interpretations, not definitional claims
  - See DOC-001 (below) for specific line-level overclaim hits

  **3. Hazard class names embedding physical-process interpretation**
  - Cluster labels like "PHASE_ORDERING hazard," "CONTAINMENT_TIMING hazard," "ENERGY_OVERSHOOT hazard" assign specific physical-process failure modes to empirically-identified transition clusters
  - This is a multi-layer interpretive leap: (a) forbidden transitions exist (empirical), (b) they cluster (empirical), (c) clusters correspond to physical hazards (interpretive — assumes distillation domain), (d) each cluster specifically identifies WHICH hazard type (interpretive — specific identification)
  - Names reads as decipherment-adjacent to a skeptical reviewer ("they're claiming these transitions are being actively suppressed to prevent phase-ordering errors")
  - Parallel to Stolfi's discipline: he named letter clusters "soft" and "hard" rather than "vowels" and "consonants" — neutral labels for empirical clusters

- **Uniform fix pattern for paper:**
  1. **Keep the empirical finding** (clustering, distributional data, correspondence statistics)
  2. **Neutralize the label** — use Class 1-5 or letter codes, or atom-pattern descriptors ("terminal-r cluster," "k-HEAD target cluster"), or letter codes A-E
  3. **Move the physical-process interpretation to discussion section** as a hypothesis, not a fact
  4. **Don't use "safety," "hazard," "failure mode," "executable," "program" as definitional language in main claims** — these are Tier 2-3 interpretive framings

- **Example contrast for hazard classes:**

  **Wrong (current docs):**
  > "The grammar has 5 hazard classes. PHASE_ORDERING accounts for 41%, CONTAINMENT_TIMING for 24%..."

  **Right (measurement-first):**
  > "Disfavored transitions cluster into approximately 5 groups based on source-atom and target-atom patterns (Class 1: terminal-r-sourced, 41% of depleted volume; Class 2: terminal-n/r-sourced to q-prefix, 24%; Class 3: terminal-r/n-sourced to l-head, 24%; Class 4: bare-terminal sourced, 6%; Class 5: transparent-h-terminal sourced, 6%). Physical-process interpretations are possible (e.g., Class 1 is consistent with phase-ordering constraints if the manuscript encodes distillation procedures, as suggested by cross-corpus matching to medieval alchemical recipes) but are interpretive hypotheses, not established identities for the clusters."

- **Why this matters:**
  - The conference policy rejects decipherment; interpretive naming schemes read as decipherment-adjacent
  - The pattern is the same across atom glosses, architecture vocabulary, and hazard class names
  - Uniform fix approach: structural description first, operational-interpretive label as hypothesis after

- **Status:** Framing guidance for paper drafting. Applies alongside PUB-003's methodology framing section.
- **Session:** 2026-04-19

---

## Research chronology reference

### CHRON-001: Project research chronology — stable reference for paper methodology narrative
- **Purpose:** Two retrospective audits conducted to establish an accurate methodology trajectory for the paper. First audit reconstructed the overall research chronology vs. user's recollection. Second audit examined the so-called "physics battery" for methodological coherence. This entry captures both as a stable reference for paper drafting.

**Part A: Research trajectory (chronological inflection points)**

| # | Inflection | Date / Version | Status |
|---|---|---|---|
| 1 | Natural-language hypothesis exhausted (DSL, semantic slots, compositional morphology all rejected) | Phase 23, v1.8 FROZEN, 2026-01-08 | STILL HOLDS (C130, C132 Tier 1) |
| 2 | Data-file/source-code framing adopted | v2.0, 2026-01-09 | STILL HOLDS (C115, C120 Tier 0) |
| 3 | k/h/e kernel structure identified | v2.0, 2026-01-10 | STILL HOLDS (C085, C089 Tier 0) |
| 4 | Purpose-class elimination → semantic ceiling (C171 established) | PCI phase, 2026-01-04 (NOT the later physics battery) | STILL HOLDS (Tier 2) |
| 5 | Physics plausibility testing | PPA + PHYS + FM-PHY-1 + MAT-PHY-1, 2026-01-01 to 2026-01-16 | MIXED — see Part B |
| 6 | Domain alignment (Brunschwig selected based on token-complexity match) | v2.36, 2026-01-14 | STILL HOLDS (selection rationale) but full-transfer claim FALSIFIED (F-BRU-022, F-BRU-025) |
| 7 | Statistical bombardment + PREFIX/MIDDLE/SUFFIX morphology | v2.50-v2.89, 2026-01-16 to 2026-01-29 | STILL HOLDS |
| 8 | Glosses solidify as compositional operations (NOT word meanings) | ~2026-01-20 | STILL HOLDS (this is the moment C171-compliant framing locks in) |
| 9 | Internal validation → external recipe matching begins (Testamentum) | Phase 629, 2026-02-08 | STILL HOLDS |
| 10 | HEAD+MOD+TERM atom compositional formalism locked | Phase 630, v6.02, 2026-03-27 (LATE — not early as commonly remembered) | STILL HOLDS (C1394, C1897-C1900) |
| 11 | Full-spectrum Testamentum matching, 51/53 coverage | Phase 635-638, Feb-Mar 2026 | STILL HOLDS (C1930-C1947) |
| 12 | Null/neutral result phases confirm C171 predictions | Phase 641 (null), Phase 642 (neutral), Apr 2026 | STILL HOLDS as credibility-building |

**Constraint-count inflection:** v1.8 (~150) → v2.36 (~500) → v3.0 (~850) → v6.22 (1,958). The Jan 14-20 window added ~350 constraints in one week — this is the methodology crystallization moment.

**Key corrections from original recollection:**
- HEAD+MOD+TERM atom formalism was formalized in **March 2026 (Phase 630)**, not during earlier statistical bombardment. The paper's methodology ordering should reflect that Testamentum matching was partially done via morphology-level features; the atom compositional formalism was developed after to explain why the matches worked.
- Testamentum matching started **February 2026**, not earlier.
- "Tokens carry meaning beyond atoms" should be reframed as **"tokens carry context-dependent execution-state identity"** — not semantic content. C171 (semantic ceiling) explicitly rules out the "meaning" framing.

**Part B: Physics battery coherence**

The "physics battery" is a post-hoc narrative name, not a single phase. It comprises FOUR separate phases (2026-01-01 to 2026-01-16) with mixed tier status:

| Phase | Purpose | Tier | Outputs | Paper-ready? |
|---|---|---|---|---|
| PPA (Physics Plausibility Audit) | 7-track thermodynamic validation (irreversibility, energy, latency, noise, control dimensionality, stability, failure modes) | 2 | Track-level validation | YES |
| PHYS (Physics Stress Test) | 5 tests on kernel operators (recovery, stabilization, LINK buffering, oscillation, abort cost) | 2 | C339 (E-class dominance, 36%), C340 (LINK-escalation complementarity) | YES, but note post-hoc reframing |
| FM-PHY-1 (Failure Mode Alignment) | 3 tests comparing hazard distribution to engineering taxonomy | 3 | Topology match finding | NO — authors refused Tier 2 promotion ("topology match ≠ identification") |
| MAT-PHY-1 (Material Topology) | 5 tests on Currier A incompatibility vs. botanical chemistry | 3 | Topology match finding | NO — authors explicitly refused Tier 2 ("match ≠ necessity") |

**Coherence verdict: PARTIAL (structurally coherent, purpose-incoherent)**

Strengths:
- All four phases were pre-registered with measurable criteria
- Individual phases have internal test logic
- PPA's 7-track design is genuinely coherent

Weaknesses:
- Four separate hypotheses tested in parallel, not one unified hypothesis
- No single falsification pathway across the battery (no kill condition)
- Every test passed — zero failures across battery is a p-hacking concern
- PHYS had post-hoc reinterpretation: expected inertia-based recovery, found rapid recovery, reframed findings as "also plausible" and derived new constraints from the unexpected pattern (hypothesis-generated-after-results)
- 50% of battery phases (FM-PHY-1, MAT-PHY-1) are Tier 3 exploratory and explicitly non-binding per their own authors

**Part C: Critical attribution correction for paper**

**C171 (semantic ceiling / closed-loop-control-only) was NOT a result of the physics battery.**

- C171 was produced by **phase PCI (Purpose Class Inference) on 2026-01-04** via an 8-constraint elimination test across candidate purpose classes
- The physics battery (2026-01-01 to 2026-01-16) was conducted AFTER PCI concluded — designed to test whether closed-loop control's physics are plausible given the already-established purpose inference
- The battery **validated** C171; it did not **establish** it

**Paper framing implications:**
- Wrong: "The physics battery established that the manuscript encodes closed-loop control (C171)"
- Right: "Purpose-class elimination (PCI) established closed-loop control as the only viable purpose class (C171); subsequent physics plausibility testing validated that the grammar's structure is consistent with closed-loop control physics"

This is a distinction without a textual difference at the claim level but a significant difference in causal logic. Review this before any paper passage discussing the physics-validation narrative.

**Part D: Paper-ready subset (what to cite, what to skip)**

**CITE confidently:**
- PCI purpose-class elimination → C171 (Tier 2)
- PPA 7-track plausibility validation (Tier 2)
- PHYS: C339 (stability dominance), C340 (LINK-escalation complementarity) — both Tier 2
- Kernel structure (C085, C089) — Tier 0
- Language/cipher rejection (C130, C132) — Tier 1
- Testamentum matching pipeline + 8D residual matching (Phases 629-638)
- Atom compositional formalism (C1394, C1897-C1900, Phase 630)

**CITE carefully (with honest reframing):**
- PHYS post-hoc reframing — either describe the original hypothesis and its revision honestly, or omit the specific finding; reviewers who read the phase INDEX will see the reinterpretation
- Brunschwig alignment — cite as **structural mirror** (confirms Voynich is procedural), not as semantic source; explicitly note F-BRU-022 and F-BRU-025 negatives

**DO NOT cite as supporting evidence:**
- FM-PHY-1 hazard-distribution-matches-distillation (Tier 3, authors said not necessity)
- MAT-PHY-1 Currier-A-matches-botany (Tier 3, authors explicitly refused Tier 2)
- "The physics battery" as a monolithic unified validation (it's four separate phases with mixed status)

**EXPLICITLY INCLUDE as credibility-building negatives:**
- Phase 641 null result (gloss-recipe correlation) — frame as C171 prediction confirmed
- Phase 642 neutral result (Brunschwig feature-matching insufficient)
- F-BRU-022, F-BRU-025 (Brunschwig semantic transfer falsified)
- Reviewers need to see that tests have actually failed in this project; the record supports this

**Part E: Key language discipline for methodology section**

- Don't call it "the physics battery" — say "structural plausibility analysis (PPA) and kernel stress testing (PHYS)" with separate citations
- Don't claim "the physics battery proved X" — the battery validated conclusions from separate elimination testing
- Don't cite Tier 3 exploratory findings as if they were Tier 2 supporting evidence
- Do own the post-hoc reframing in PHYS if citing those specific findings — honesty disarms critique
- Do prominently feature the failed tests (641, 642, F-BRU series) — they establish that the methodology can reject as well as accept

- **Status:** Both audits complete. Stable reference for paper drafting. Any future paper passage discussing methodology trajectory or physics validation should cross-check against this entry before citing.
- **Session:** 2026-04-19

---

## Public documentation overclaim audit

### DOC-001: Public documentation overclaim audit (pre-submission)
- **Purpose:** The public repo will be cited in any conference paper as the reproducibility backing. A reviewer's first impression is the README. If the README voice (confident, declarative, interpretation-forward) mismatches the paper voice (measurement-focused, explicit scope limits, hedged interpretations), the mismatch is lethal — a reviewer could conclude the paper is hedging for show while the real project is a decipherment claim. This entry documents the audit of 9 public-facing docs; no edits applied yet.
- **Docs audited:**
  1. `README.md` — top-level entry point
  2. `WHAT_WE_CLAIM.md` — most carefully-written, explicit tier markings
  3. `GUIDE.md` — conceptual walkthrough
  4. `RECIPE_MATCHING.md` — methodology-forward, relatively clean
  5. `METHODS_AND_TOOLS.md` — methodology documentation, mostly fine
  6. `phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md` — Phase 550 formal synthesis
  7. `phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md` — Phase 551, explicitly Tier 3
  8. `phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md` — Phase 491 historical context
  9. `phases/HISTORICAL_NETWORK/HISTORICAL_ESSAY.md` — narrative synthesis
- **Overclaim patterns identified:**
  1. **Interpretive vocabulary used as definitional:** "executable," "program," "safety architecture," "control grammar" — used throughout without hedging; these are Tier 2-3 framings, not Tier 0 facts
  2. **Declarative assertions of Tier 2-3 interpretations:** "is" instead of "appears to be," "encodes" instead of "contains features consistent with"
  3. **Rhetorical flourishes:** "The structure *IS* the semantics," "we recovered the formal operating logic," "we proved" — present in README and GUIDE
  4. **Strong negative universals:** "The manuscript encodes only procedural content" — universal claim for a set still being analyzed
  5. **Semantic identifications stated as fact:** "A product chain links folios," "vegetable G = quintessence" — Tier 3 interpretations asserted declaratively
  6. **"Proved" language for Tier 2 findings:** Appears in GUIDE ("We proved that its internal structure... fits the domain...")
- **Structural clarity issues (density + category-mixing):** Separate from per-line overclaim language, the README opening paragraphs have a density problem that compounds the overclaim issue. Empirical facts, Tier 2 structural findings, Tier 3 interpretations, and Tier 1 falsifications are packed into single paragraphs without visual or grammatical signal that they're different kinds of claims. A reader can't tell which part is measurement and which part is opinion.

  **Example — README L3 contains 7 interleaved claims of mixed kind:**
  1. Corpus stats: 23,243 tokens, 83 folios (empirical)
  2. Tier 3 framing: "closed-loop control programs in a purpose-built operational notation"
  3. Tier 3 framing: "Each folio is a self-contained program"
  4. Tier 2 structural facts: 49 instruction types, 18-atom architecture
  5. Tier 1 falsification: not a language
  6. Tier 1 falsification: not a cipher
  7. Tier 3 negative: not a translation

  **README L5** similarly mashes Tier 3 interpretation (source tradition), empirical match numbers (51/41/96%), structural observations (multi-chapter, recto/verso), universal Tier 3 negative ("encodes only procedural content"), and empirical validation (permutation p<0.0001) into a single paragraph.

  **README L7** jumps from analogy (sheet music) to assertion ("we recovered the formal operating logic"), drafting on the analogy's persuasive force without earning it with evidence.

  **Fix target — separate-by-kind structure:**
  1. Para 1 — what the corpus is (empirical, Tier 0-2)
  2. Para 2 — what we've measured (empirical results)
  3. Para 3 — what we've inferred (clearly marked as interpretation)
  4. Para 4 — what we do not claim (scope limits)

  This structure lets readers calibrate claim strength by paragraph position and stops the rhetorical leakage from interpretation into assertion. Addressing this is the same editing pass as the overclaim fixes but with clearer structural targets — it's not additional work, it's the same work done correctly.
- **Per-doc highest-impact overclaim hits:**

  **README.md** (most paper-critical):
  - L3: "encodes closed-loop control programs in a purpose-built operational notation" — declarative
  - L3: "Each folio is a self-contained program" — declarative interpretation
  - L7: "The structure *is* the semantics" (italicized) — bold rhetorical flourish
  - L7: "we recovered the formal operating logic" — "recovered" implies actual answer
  - L16: "closed executable grammar" — "executable" interpretive
  - L18: "three-level safety architecture" — "safety" interpretive
  - L23: "The manuscript encodes only procedural content" — strong negative universal
  - L26: "The best-fit historical source tradition is Pseudo-Lullian alchemy" — "is" not "appears to be"
  - L29: "A product chain links folios: f75r (quintessence) feeds f84r (gold tincture)" — semantic claim as fact
  - L164: "what the manuscript encodes (a control grammar for Pseudo-Lullian alchemical procedures)" — definitive content claim

  **WHAT_WE_CLAIM.md** (has good structure but still overclaim hits):
  - L15: "Currier B forms a closed executable grammar" — "executable" interpretive
  - L21: "The manuscript has a three-level safety architecture" — "safety" interpretive
  - L23: "Each line is a self-contained safety envelope" — "safety envelope" interpretive
  - L35: "The manuscript encodes only procedural content" — strong universal
  - L41: "The best-fit historical source tradition is Pseudo-Lullian alchemy" — "is"
  - L47: "A product chain links folios across the manuscript" — declarative
  - **Strength:** explicit "What We Do Not Claim" section (L59-76), "What Would Change Our Mind" with falsifiers (L79-93)

  **GUIDE.md:**
  - L22: "The Voynich Manuscript is not a language. It is not a cipher. It is a **control grammar**" — declarative triple
  - L38: "The structure *is* the semantics" — same rhetorical flourish as README
  - L40: "**This is exactly what we are doing with the Voynich Manuscript.**" — overconfident emphasis
  - L40: "We proved that its internal structure... fits the domain of thermodynamic process control and no other domain tested" — "proved" language
  - L74-78: Currier B defined as containing "control procedures" / "closed-loop control process" as definitional

  **RECIPE_MATCHING.md:**
  - L20: "The manuscript encodes only procedural content" — universal
  - L3: "51 procedural chapters map to 41 folios, covering 96% of the *Testamentum*'s procedural content" — strong number but defensible
  - **Strength:** has explicit "Feature Provenance and Tuning Timeline" section (L45-65) with honest post-match refinement accounting; strong Limitations section (L323-346)

  **METHODS_AND_TOOLS.md:** Mostly fine. One flag: L9 "no result depends on AI intuition or pattern-matching alone" — strong defensive claim.

  **ARCHITECTURE.md (Phase 550):**
  - L4: "DEFINITIVE SYNTHESIS" — "definitive" strong
  - L19: "Every Currier B token is a single executable instruction" — declarative interpretive
  - L193+: "The Safety Architecture" entire section — interpretive vocabulary throughout
  - L297: "Each of the 83 Currier B folios is a complete executable program" — declarative
  - L341: "Currier B is the execution layer" — declarative
  - **Strength:** Appendix A marked "fully discardable" for interpretive content

  **OPERATOR_MODEL.md (Phase 551):**
  - Status header already marks this Tier 3 explicitly
  - L19: "The manuscript was designed for experts, not novices" — declarative
  - L203-206: "the Voynich Manuscript is to medieval distillation what an IEC 61131-3 program is to an industrial process" — strong analogy claim
  - **Strength:** explicit scope disclaimer L9-14

  **HISTORICAL_NETWORK.md:**
  - L288+: Milan/Visconti identification detailed as "strongest candidate" — Tier 3-4 speculation
  - **Strengths:** explicit disclaimers L11-12, dedicated "What This Phase Does NOT Claim" section L324-331

  **HISTORICAL_ESSAY.md:**
  - L43-44: "encodes closed-loop control programs" — declarative
  - **Strength:** explicit "What This Does Not Claim" L336-342
- **Paper-README tension risk:** Paper will say "we report measurable structural correspondences... we do not claim decipherment." README + GUIDE currently say "each folio is a self-contained program... the structure IS the semantics... the manuscript encodes only procedural content." These voices don't match. Reviewer who reads paper first then checks repo will feel whiplash.
- **Recommended action (not yet executed, per user decision to defer):**

  **Approach: hybrid — surgical edits + companion note (NOT full rewrite)**

  Pure softening of all docs risks looking like pre-submission scrubbing — the exact thing the ethics guidance says not to do. Leaving everything as-is leaves loud overclaims a skeptical reviewer will screenshot. Hybrid:

  1. **Create `PAPER_COMPANION.md`** — new top-level document that:
     - Maps every paper claim to specific repo artifacts (script + commit hash + constraint #)
     - Enumerates paper scope explicitly (what IS claimed in paper, what IS NOT)
     - Notes: "The main project documentation (README, GUIDE, architecture docs) represents the project's accumulated interpretive framework. The associated conference paper takes a deliberately narrower, measurement-focused framing. Where the two differ, the paper's scope is authoritative for evaluation of the paper's claims."

  2. **Surgical edits to README.md only** (5-6 specific lines) — the highest-impact overclaims that a reviewer would screenshot:
     - "The structure IS the semantics" → remove italics, soften to "The structure carries the operational semantics" or remove entirely
     - "we recovered the formal operating logic" → "we characterized the structural grammar"
     - "three-level safety architecture" → keep but add qualifier ("interpreted as a three-level defense pattern")
     - "Each folio is a self-contained program" → "Each folio appears to function as a structural unit"
     - "The manuscript encodes only procedural content" → "Validated matches are restricted to procedural content"

  3. **Add scope-note headers to GUIDE.md, WHAT_WE_CLAIM.md, ARCHITECTURE.md** — one-paragraph note at the top stating that the document represents the project's Tier 2-3 interpretive synthesis; conference-paper claims are narrower.

  4. **Leave OPERATOR_MODEL.md, HISTORICAL_NETWORK.md, HISTORICAL_ESSAY.md as-is** — these are explicitly Tier 3-4 and already marked as such; they should NOT be cited in the paper. Add a note in PAPER_COMPANION.md that these documents are supporting context but not paper-relevant.

  5. **Leave RECIPE_MATCHING.md and METHODS_AND_TOOLS.md essentially as-is** — they're methodology docs, honest about limitations, appropriately hedged.
- **What NOT to do:**
  - No force-pushing or git history rewriting
  - No deleting constraints or downgrading tier markings to match paper
  - No removing negative results or failed-hypothesis records
  - No silent edits that erase earlier framings (every change visible in git log)
- **Estimated scope:**
  - PAPER_COMPANION.md: new doc, 200-300 lines
  - README surgical edits: 5-6 lines
  - Scope notes on 3 other docs: ~10 lines each
  - Total: manageable 1-2 hour pass
- **Decision status:** DEFERRED — user noted audit before editing. Execution pending user go-ahead, likely alongside paper draft work in May/June 2026.
- **Session:** 2026-04-18
