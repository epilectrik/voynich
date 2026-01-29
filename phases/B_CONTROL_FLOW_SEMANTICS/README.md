# B_CONTROL_FLOW_SEMANTICS Phase

**Status:** PLANNED
**Tier:** 3 (Semantic Interpretation)
**Scope:** B

---

## Objective

Synthesize structural constraints into a unified semantic model of what Currier B text is doing. Build on the 738 validated constraints to produce an integrated interpretation of the control flow system.

---

## Background

### What We Know (Tier 2 Structural Facts)

| Component | Key Constraints | Structural Facts |
|-----------|-----------------|------------------|
| FL (Flow) | C770-C777 | Kernel-free state index, INITIAL→TERMINAL stages, hazard=early/safe=late |
| EN (Energy) | C778-C780 | Kernel-containing operators, k-injection before transitions, e-verification after |
| CC (Control) | C788-C791 | Singleton tokens (daiin, ol, k), positional gradient, routes to EN |
| FQ (Frequent) | C781, C785 | Escape pathway, medial targeting, phase bypass |
| LINK | C804-C809 | Monitoring boundary, 13.2% of tokens, positional bias, kernel separation |
| Control Loop | C810-C815 | LINK→KERNEL→FL ordering, kernel-escape inverse (rho=-0.528) |
| Hazard | C467, C789 | 17 forbidden pairs, ~65% compliance (soft constraints) |

### Semantic Work Done

| Phase | Key Finding |
|-------|-------------|
| FL_SEMANTIC_INTERPRETATION | FL indexes material position: INPUT(i)→MEDIAL(r,l)→YIELD(y) |
| CC_MECHANICS_DEEP_DIVE | CC "classes" are specific tokens, not broad categories |
| CONTROL_LOOP_SYNTHESIS | Canonical ordering LINK→KERNEL→FL, flexible timing |

### Central Question

**What is Currier B text actually doing?**

Candidate interpretations:
- Process control (chemical/biological transformation)
- State machine (finite automaton with escape routes)
- Batch processing (input→process→output with monitoring)
- Recipe encoding (procedural instructions with conditionals)

---

## Phase Structure

```
phases/B_CONTROL_FLOW_SEMANTICS/
├── README.md
├── FINDINGS.md
├── scripts/
│   ├── 00_role_semantic_census.py      # GATE: Build role profiles with semantic annotations
│   ├── 01_kernel_semantics.py          # What do k, h, e actually encode?
│   ├── 02_cc_token_semantics.py        # Why daiin, ol, k are special
│   ├── 03_escape_trigger_analysis.py   # What states trigger FQ escape?
│   ├── 04_link_monitoring_model.py     # What is LINK monitoring?
│   ├── 05_state_transition_grammar.py  # Formal transition rules
│   ├── 06_section_program_profiles.py  # Do sections run different programs?
│   ├── 07_process_domain_test.py       # Test candidate domain interpretations
│   └── 08_integrated_model.py          # Synthesize unified semantic model
└── results/
    └── [output files]
```

---

## Script Specifications

### Script 00: Role Semantic Census (GATE)

**Purpose:** Build comprehensive role profiles with all known semantic annotations.

**Output per role:**
```json
{
  "role": "FL",
  "token_count": 1078,
  "type_count": 89,
  "kernel_rate": 0.0,
  "hazard_rate": 0.887,
  "mean_position": 0.576,
  "semantic_annotations": {
    "stage_map": {"INITIAL": ["i", "ii"], "MEDIAL": ["r", "l"], ...},
    "function": "state_index",
    "domain_hint": "material_position"
  }
}
```

**Verification:** All 49 classes mapped to 7 roles with semantic annotations.

---

### Script 01: Kernel Semantics

**Question:** What do k, h, e actually encode?

**Background:**
- k appears before state transitions (C779)
- e appears after transitions (verification)
- h is minimal (phase alignment?)

**Tests:**
1. k-context analysis: What states precede/follow k?
2. e-context analysis: What states precede/follow e?
3. h-context analysis: When does h appear?
4. Kernel combinations: What do kh, ke, he mean?
5. Kernel absence: What happens without kernel?

**Semantic candidates:**
- k = energy/activation (kinetic)
- h = phase/harmony (alignment)
- e = equilibrium/stability (verification)

---

### Script 02: CC Token Semantics

**Question:** Why are daiin, ol, and k the control tokens?

**Background (C788-C791):**
- Class 10: "daiin" only (314 occurrences)
- Class 11: "ol" only (421 occurrences)
- Class 12: "k" only (0 occurrences - ghost)
- Class 17: "ol-" compounds (olkeedy, olkeey, etc.)

**Tests:**
1. daiin context: What precedes/follows daiin?
2. ol context: What precedes/follows ol?
3. daiin vs ol comparison: Do they serve different functions?
4. Morphological analysis: What are daiin and ol structurally?
5. Position comparison: daiin is early (0.455), ol-compounds later

**Semantic candidates:**
- daiin = "begin/initiate" (early position, no kernel)
- ol = "continue/proceed" (medial, can take kernel suffixes)

---

### Script 03: Escape Trigger Analysis

**Question:** What states trigger FQ escape?

**Background:**
- FQ = escape pathway (C781)
- Hazard FL has 16.7% FQ rate, Safe FL has 5.6% (C775)
- FQ targets medial positions (C785)

**Tests:**
1. Pre-FQ state census: What states immediately precede FQ?
2. Hazard-FQ correlation: Which hazard types trigger escape?
3. Kernel-FQ relationship: Does kernel presence affect escape?
4. Recovery after FQ: What states follow FQ tokens?
5. FQ chains: Do escapes chain or resolve quickly?

**Expected findings:** Identify the "escape trigger grammar" - what conditions make escape necessary.

---

### Script 04: LINK Monitoring Model

**Question:** What is LINK monitoring?

**Background (C804-C809):**
- LINK = 13.2% of tokens
- Positional bias (earlier in lines)
- Kernel-separated (LINK-kernel transitions rare)
- Not adjacent to FL (C810)

**Tests:**
1. LINK successor states: What follows LINK?
2. LINK predecessor states: What precedes LINK?
3. LINK-hazard relationship: Does LINK detect hazard?
4. LINK density by line position: Where is monitoring concentrated?
5. LINK-to-intervention: When does monitoring trigger action?

**Semantic candidates:**
- LINK = "check/verify" (monitoring phase)
- LINK = "measure/sense" (input to control decision)
- LINK = "wait/hold" (synchronization point)

---

### Script 05: State Transition Grammar

**Question:** What are the formal transition rules?

**Approach:** Build explicit state machine from observed transitions.

**States:**
- FL stages (INITIAL, EARLY, MEDIAL, LATE, TERMINAL)
- Kernel states (k-active, h-active, e-active, neutral)
- Control states (LINK, CC, normal)

**Transitions to characterize:**
1. Legal transitions (observed frequently)
2. Forbidden transitions (hazard pairs)
3. Escape transitions (FQ routes)
4. Recovery transitions (post-escape)

**Output:** Formal grammar of allowed/forbidden state transitions.

---

### Script 06: Section Program Profiles

**Question:** Do different sections run different programs?

**Background (C552, C860):**
- BIO: 7.5 paragraphs/folio, role profile X
- HERBAL_B: 2.2 paragraphs/folio, role profile Y
- PHARMA: 14.0 paragraphs/folio, role profile Z
- RECIPE_B: 10.2 paragraphs/folio, role profile W

**Tests:**
1. Role distribution by section: EN/FL/FQ/CC ratios
2. Kernel usage by section: k/h/e preferences
3. Escape rate by section: Which sections need more escape?
4. State progression by section: Different process types?
5. CC token usage by section: daiin/ol preferences

**Expected findings:** Sections may encode different process types (e.g., PHARMA = more complex, HERBAL = simpler).

---

### Script 07: Process Domain Test

**Question:** Which domain interpretation best fits the data?

**Candidate domains:**

| Domain | Prediction | Test |
|--------|------------|------|
| Chemical | FL stages = reaction progress | Stage ordering should be irreversible |
| Biological | FL = organism state | Should see growth/decay patterns |
| Alchemical | FL = purification level | Terminal should be "noble" |
| Procedural | FL = instruction pointer | Should see loops/conditionals |

**Tests:**
1. Irreversibility test: How often does TERMINAL→INITIAL occur?
2. Monotonicity test: Does state generally progress forward?
3. Branching test: Are there conditional paths?
4. Loop test: Are there repeating cycles?
5. Section-domain correlation: Do sections suggest different domains?

---

### Script 08: Integrated Model

**Purpose:** Synthesize all findings into unified semantic model.

**Output:**
```json
{
  "model_name": "B Control Flow Semantic Model",
  "tier": 3,
  "core_interpretation": "...",
  "role_semantics": {
    "FL": "material state index (INPUT→YIELD)",
    "EN": "state transition operator (k=activate, e=verify)",
    "CC": "control words (daiin=begin, ol=continue)",
    "FQ": "escape handler (unstable→recovery)",
    "LINK": "monitoring checkpoint",
    "AX": "...",
    "UN": "..."
  },
  "control_loop": {
    "phases": ["MONITOR", "PROCESS", "VERIFY", "ESCAPE_IF_NEEDED"],
    "canonical_order": "LINK → KERNEL → FL",
    "escape_trigger": "hazard state + kernel failure"
  },
  "process_domain": "batch transformation with safety interlocks",
  "confidence": "MEDIUM",
  "structural_provenance": ["C770-C815", "C788-C791", ...]
}
```

---

## Expected Constraints

| # | Name | Hypothesis |
|---|------|------------|
| C873 | Kernel Semantic Assignment | k=activation, h=alignment, e=verification |
| C874 | CC Token Functions | daiin=initiate, ol=continue |
| C875 | Escape Trigger Grammar | Hazard + kernel-absence triggers FQ |
| C876 | LINK Monitoring Function | LINK = state verification checkpoint |
| C877 | State Transition Formalism | Explicit legal/forbidden transition rules |
| C878 | Section Program Differentiation | Sections encode different process complexities |
| C879 | Process Domain Verdict | Best-fit domain interpretation |
| C880 | Integrated Control Model | Unified semantic model of B control flow |

---

## Tier Assignment

All constraints from this phase will be **Tier 3** (semantic interpretation) because they assign meaning to structural patterns. The structural patterns themselves (C770-C815, etc.) remain Tier 2.

**Tier 3 criteria:**
- Builds on established structure (Tier 2)
- Assigns semantic labels to patterns
- Cannot be falsified by internal structure alone
- Would require external validation (decipherment) to confirm

---

## Data Dependencies

| Script | Depends On |
|--------|------------|
| 00 | class_token_map.json, FL semantic model |
| 01-04 | role_semantic_census.json (from 00) |
| 05 | All transition data from 01-04 |
| 06 | Section definitions (C552) |
| 07 | All findings from 01-06 |
| 08 | All results from 00-07 |

---

## Verification

### Cross-Reference Validation

| New Finding | Must Check Against |
|-------------|-------------------|
| Kernel semantics | C778-C780 (EN kernel profile) |
| CC functions | C788-C791 (CC mechanics) |
| Escape triggers | C775, C781, C785 (FQ architecture) |
| LINK function | C804-C809 (LINK operator) |
| Section profiles | C552, C860 (section organization) |

### Semantic Validation Standards

Since this is Tier 3 work:
- All interpretations must be consistent with Tier 2 structure
- Multiple interpretations may be valid; document alternatives
- Confidence levels: HIGH (single interpretation), MEDIUM (preferred among alternatives), LOW (speculative)
- No interpretation can contradict established constraints

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Over-interpretation | Document confidence levels, alternatives |
| Confirmation bias | Test multiple domain hypotheses |
| Semantic drift | Anchor all claims to constraint numbers |
| Tier confusion | Explicitly mark all outputs as Tier 3 |

---

## Success Criteria

Phase succeeds if:
1. All scripts execute without structural contradictions
2. Unified model is internally consistent
3. Model explains observed patterns (hazard, escape, kernel, etc.)
4. Clear confidence levels assigned to all interpretations
5. Alternative interpretations documented where applicable

Phase fails if:
1. Semantic assignments contradict structural constraints
2. No coherent model emerges from synthesis
3. Interpretations require special pleading or exceptions

---

## Estimated Scope

| Component | Count |
|-----------|-------|
| Scripts | 9 |
| Expected constraints | 8 (all Tier 3) |
| Structural constraints used | ~50 (C467, C552, C770-C815, etc.) |
| Tokens analyzed | 23,096 (all B) |
