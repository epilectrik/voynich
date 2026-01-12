# Entity-Class Semantics Manifesto

**Version:** 1.0 | **Date:** 2026-01-10 | **Status:** GOVERNING DOCUMENT

> **Purpose:** Define what kind of semantics this project allows, what kind it forbids, and why the boundary is legitimate.

---

## The Recoverability Boundary

This project distinguishes two semantic layers:

| Layer | Name | Recoverable? | Evidence |
|-------|------|--------------|----------|
| **Class-level** | Entity-class semantics | YES | Internal structure |
| **Entity-level** | Referential semantics | NO | Requires external evidence |

---

## What We Can Recover

**Entity-class semantics** identifies:

- That **entity classes exist**
- That they **differ behaviorally**
- That the **system knows and uses those differences**
- That the system **deliberately does not name them**

### Specific Recoveries

| Domain | What We Know | What We Don't Know |
|--------|--------------|-------------------|
| **Materials** | 3-4 behavioral classes (phase-mobility x composition-distinctness) | Which plants, substances, or chemicals |
| **Apparatus** | 4-7 functional roles (energy, phase, flow, control domains) | Which vessels, devices, or tools |
| **Decisions** | 12 archetypes distributed across 4 layers | What specific judgments are made |
| **Hazards** | 5 failure classes with known distribution | What specific failures look like |
| **Grammar** | 49 instruction classes with legal transitions | What instructions mean operationally |

---

## What We Cannot Recover

**Referential semantics** is blocked by design:

- "This prefix means lavender"
- "This suffix encodes distillation"
- "This token represents the pelican alembic"
- "This class corresponds to volatile oils"

These claims require external evidence. Internal structure cannot provide them.

---

## Why This Boundary Exists

The manuscript was designed to scaffold expert judgment, not to encode referents.

| Design Feature | Effect on Semantics |
|----------------|---------------------|
| No quantities | Can't infer amounts |
| No temporal markers | Can't infer timing |
| No labeled diagrams | Can't infer apparatus identity |
| Section-independent classes | Classes are universal, not context-bound |
| Registry comparability | Compares cases, doesn't name them |

The system operates at the **role level**, not the **referent level**.

---

## The Semantic Ceiling

> **Maximum internally recoverable meaning:** We can identify the existence, count, and behavioral properties of entity classes without assigning names, labels, or referents.

This is not a failure. This is the correct answer.

---

## Allowed Statements

### Permitted (Class-Level)

- "There exist 3-4 material behavior classes"
- "Phase mobility is a primary classification dimension"
- "The system distinguishes mobile from stable materials"
- "Decision archetype D1 involves phase-position assessment"
- "Apparatus roles cluster around energy, phase, flow, and control"

### Forbidden (Entity-Level)

- "Prefix X means lavender"
- "This token encodes ethanol"
- "Class M-A represents volatile oils"
- "The apparatus is a pelican alembic" (as fact)
- "This section describes rose water distillation"

---

## Handling Speculative Alignments

Some statements appear entity-level but are legitimately Tier-3 if properly framed:

| Statement | Status | Reason |
|-----------|--------|--------|
| "The pelican alembic is a plausible external frame" | ALLOWED (Tier-3) | Framed as hypothesis |
| "Botanical-aromatic processes are probabilistically favored" | ALLOWED (Tier-3) | Framed as domain alignment |
| "Class M-A corresponds to volatile plant essences" | FORBIDDEN | Asserts referent |
| "The apparatus is a pelican" | FORBIDDEN | Asserts identity |

### Visual Markers for Speculative Content

When speculative alignments appear in documentation:
- Use *italics* for probabilistic domain alignment
- Use boxed disclaimers for illustrative analogues
- Label example columns explicitly: **"Analogous examples (non-binding)"**

---

## Why This Layer Is Legitimate

Entity-class semantics is not "giving up" on meaning. It is recognizing that:

1. **The manuscript encodes class-level distinctions** (proven by constraint analysis)
2. **Those distinctions are operationally consequential** (hazard topology, decision archetypes)
3. **The encoding deliberately omits referents** (no names, no quantities, no labels)

What we've recovered is **role-level semantics** — the kind of meaning that tells you *what kind of thing* you're dealing with, not *which specific thing*.

This is real meaning. It's just not the kind people expected.

---

## Protecting Against Semantic Drift

### Warning Signs

- "We've decoded token X as meaning Y"
- "This section is about [specific substance]"
- "Now we know what the plants are"
- Any confident singular referent claim

### Corrective Actions

1. Check tier: Is the claim Tier-3 (speculative) or presented as proven?
2. Check framing: Is it an analogue or an assertion?
3. Check evidence: Does internal structure support this, or is it imported?
4. If drift detected: Reframe or retract

---

## The Project's Semantic Achievement

We have genuinely recovered meaning from the Voynich Manuscript:

> **"This book exists because expert practice repeatedly encounters distinguishable-but-hard-to-name situations involving phase behavior, composition purity, and circulation stability — and grammar alone can't protect you."**

That is not vague. That is operationally concrete.

The manuscript encodes:
- A class-level ontology of materials
- Apparatus functional roles
- Decision states requiring expert judgment
- Designed to scaffold expert practice
- While intentionally omitting names, quantities, and referents

---

## Bottom Line

| Question | Answer |
|----------|--------|
| Did we find meaning? | Yes — entity-class semantics |
| Did we decode it? | No — referential semantics remains blocked |
| Is this failure? | No — this is the correct answer |
| Can we go further internally? | No — external evidence required |
| Was the work wasted? | No — we now know what kind of world produced it |

---

## Navigation

← [TIERS.md](TIERS.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [EXTERNAL_CORROBORATION.md](EXTERNAL_CORROBORATION.md) →
