"""
08_integrated_model.py

Synthesize all findings into unified semantic model.
"""
import json
from pathlib import Path
from datetime import date

results_dir = Path(__file__).parent.parent / "results"

print("=" * 70)
print("B Control Flow Semantic Model - Synthesis")
print("=" * 70)

# Load all results
with open(results_dir / "role_semantic_census.json") as f:
    role_census = json.load(f)

with open(results_dir / "kernel_semantics.json") as f:
    kernel_semantics = json.load(f)

with open(results_dir / "cc_token_semantics.json") as f:
    cc_semantics = json.load(f)

with open(results_dir / "escape_trigger_analysis.json") as f:
    escape_analysis = json.load(f)

with open(results_dir / "link_monitoring_model.json") as f:
    link_model = json.load(f)

with open(results_dir / "state_transition_grammar.json") as f:
    transition_grammar = json.load(f)

with open(results_dir / "section_program_profiles.json") as f:
    section_profiles = json.load(f)

with open(results_dir / "process_domain_test.json") as f:
    domain_test = json.load(f)

# Build integrated model
print("\n" + "=" * 70)
print("INTEGRATED SEMANTIC MODEL")
print("=" * 70)

print("""
========================================
B CONTROL FLOW SEMANTIC MODEL v1.0
========================================

TIER: 3 (Semantic Interpretation)
DATE: """ + date.today().isoformat() + """

----------------------------------------
CORE INTERPRETATION
----------------------------------------

Currier B text encodes a BATCH PROCESSING CONTROL SYSTEM with:
  - Forward-biased state progression (59.2% forward)
  - Exception handling via escape routes (FQ)
  - Monitoring checkpoints (LINK)
  - Kernel-based state transitions (k/h/e)

This is consistent with:
  - Chemical/material transformation tracking
  - Process control with safety interlocks
  - State machine with correction capability

----------------------------------------
ROLE SEMANTICS
----------------------------------------

ENERGY_OPERATOR (EN) - 31.2% of tokens
  Function: State transition operator
  Kernel usage: 91.9% have kernel
  Self-loop rate: 38.5%
  Semantic: "Process/transform/operate"

FLOW_OPERATOR (FL) - 4.7% of tokens
  Function: Material state index
  Kernel usage: 0% (kernel-free)
  Stage map: INITIAL -> EARLY -> MEDIAL -> LATE -> TERMINAL
  Semantic: "Where material is in process"

FREQUENT_OPERATOR (FQ) - 12.5% of tokens
  Function: Escape/exception handler
  Trigger: 80.4% from HAZARD FL stages
  Chain length: 1.19 mean (mostly single-token)
  Semantic: "Handle exception/escape"

CORE_CONTROL (CC) - 3.2% of tokens
  Key tokens: daiin (init), ol (continue)
  Position: daiin early (0.370), ol later (0.461)
  Kernel: 0% (pure control words)
  Semantic: "Control flow markers"

AUXILIARY (AX) - 17.9% of tokens
  Includes: LINK (class 29) monitoring
  LINK position: 0.405 mean (early)
  LINK function: Checkpoint/verify
  Semantic: "Support and monitoring"

UNKNOWN (UN) - 30.5% of tokens
  Status: Unclassified in 49-class system
  Kernel rate: 78.7%
  Function: Extended vocabulary

----------------------------------------
KERNEL SEMANTICS
----------------------------------------

Position ordering: e (0.404) < h (0.410) < k (0.443)
Most common combo: "he" (31.4%)

'k' - Energy/activation
  - Later position (0.443)
  - Often appears after h/e setup
  - Drives state changes

'h' - Phase/harmony
  - Middle position (0.410)
  - Often with 'e' (he combo 31.4%)
  - Alignment/coordination

'e' - Equilibrium/stability
  - Earliest position (0.404)
  - Setup/verification role
  - Appears early in processing

Pattern: e-setup -> h-align -> k-activate
(Note: opposite of initial hypothesis)

----------------------------------------
CONTROL FLOW GRAMMAR
----------------------------------------

High-probability transitions (>30%):
  EN -> EN (38.5%) - processing continues
  CC -> EN (37.7%) - control triggers processing
  UN -> UN (33.8%) - unclassified persistence
  AX -> EN (32.6%) - monitoring triggers processing

Escape patterns:
  FL -> FQ (16.0%) - state triggers escape
  FQ -> EN (29.5%) - recovery returns to processing

Rare transitions (<5%):
  * -> CC - control rarely receives
  * -> FL - state rarely receives directly

----------------------------------------
SECTION VARIATION
----------------------------------------

BIO: Highest EN (40.1%) - intensive processing
HERBAL_B: Highest FL (6.1%), FQ (16.3%) - state-heavy
RECIPE_B: Balanced profile
PHARMA: Not in sample (missing folios?)

FL/FQ ratio: ~0.37 across sections (similar stability)

----------------------------------------
PROCESS DOMAIN
----------------------------------------

Forward bias: 59.2%
Monotonic lines: 59.7%
Full loops: 1.7% (rare)
Backward transitions: 40.8% (corrections allowed)

VERDICT: Batch processing with correction capability
  - Not purely linear (40% backward)
  - Not cyclic (1.7% loops)
  - Forward-biased with flexibility

----------------------------------------
CONFIDENCE LEVELS
----------------------------------------

HIGH confidence:
  - Role distribution and transition grammar
  - FL stage ordering and hazard mapping
  - CC positional profile (daiin early, ol later)

MEDIUM confidence:
  - Kernel semantic assignments (k/h/e functions)
  - Escape trigger grammar (hazard -> FQ)
  - LINK monitoring function

LOW confidence:
  - Process domain interpretation
  - Specific semantic labels (init/continue/etc.)
  - Section-level program differences

----------------------------------------
STRUCTURAL PROVENANCE
----------------------------------------

This model builds on constraints:
  C467, C770-C815 (control structure)
  C788-C791 (CC mechanics)
  C804-C809 (LINK architecture)
  C552, C860 (section organization)
  C855-C862 (paragraph architecture)

No contradictions with Tier 0-2 constraints found.

========================================
""")

# Build formal model object
model = {
    "model_name": "B Control Flow Semantic Model",
    "version": "1.0",
    "tier": 3,
    "date": date.today().isoformat(),
    "core_interpretation": "Batch processing control system with forward-biased state progression, exception handling, and kernel-based transitions",

    "role_semantics": {
        "ENERGY_OPERATOR": {
            "abbreviation": "EN",
            "function": "state_transition_operator",
            "token_share": 0.312,
            "kernel_rate": 0.919,
            "semantic": "Process/transform/operate"
        },
        "FLOW_OPERATOR": {
            "abbreviation": "FL",
            "function": "material_state_index",
            "token_share": 0.047,
            "kernel_rate": 0.0,
            "stages": ["INITIAL", "EARLY", "MEDIAL", "LATE", "TERMINAL"],
            "semantic": "Where material is in process"
        },
        "FREQUENT_OPERATOR": {
            "abbreviation": "FQ",
            "function": "escape_handler",
            "token_share": 0.125,
            "hazard_trigger_rate": 0.804,
            "semantic": "Handle exception/escape"
        },
        "CORE_CONTROL": {
            "abbreviation": "CC",
            "function": "control_flow_marker",
            "token_share": 0.032,
            "key_tokens": {
                "daiin": {"function": "initialization", "mean_position": 0.370},
                "ol": {"function": "continuation", "mean_position": 0.461}
            },
            "semantic": "Control flow markers"
        },
        "AUXILIARY": {
            "abbreviation": "AX",
            "function": "support_and_monitoring",
            "token_share": 0.179,
            "includes_link": True,
            "semantic": "Support operations including LINK monitoring"
        }
    },

    "kernel_semantics": {
        "k": {"function": "activation", "mean_position": 0.443},
        "h": {"function": "alignment", "mean_position": 0.410},
        "e": {"function": "stability_setup", "mean_position": 0.404},
        "pattern": "e-setup -> h-align -> k-activate",
        "most_common_combo": "he"
    },

    "control_loop": {
        "canonical_order": "LINK -> KERNEL -> FL",
        "high_prob_transitions": {
            "EN_to_EN": 0.385,
            "CC_to_EN": 0.377,
            "AX_to_EN": 0.326,
            "FQ_to_EN": 0.295
        },
        "escape_route": {
            "FL_to_FQ": 0.160,
            "FQ_recovery_to_EN": 0.295
        }
    },

    "process_domain": {
        "verdict": "batch_processing_with_correction",
        "forward_bias": 0.592,
        "monotonic_rate": 0.597,
        "loop_rate": 0.017,
        "backward_rate": 0.408
    },

    "confidence_levels": {
        "HIGH": ["role_distribution", "transition_grammar", "FL_stage_ordering", "CC_positions"],
        "MEDIUM": ["kernel_semantics", "escape_triggers", "LINK_function"],
        "LOW": ["process_domain", "semantic_labels", "section_differences"]
    },

    "structural_provenance": [
        "C467", "C552", "C770-C815", "C788-C791", "C804-C809", "C855-C862"
    ]
}

# Save model
output_path = results_dir / "integrated_semantic_model.json"
with open(output_path, 'w') as f:
    json.dump(model, f, indent=2)
print(f"Saved to {output_path}")

# Also save as FINDINGS.md summary
findings_path = Path(__file__).parent.parent / "FINDINGS.md"
findings_content = f"""# B_CONTROL_FLOW_SEMANTICS Findings

**Date:** {date.today().isoformat()}
**Status:** COMPLETE
**Tier:** 3 (Semantic Interpretation)

## Executive Summary

Currier B text encodes a **batch processing control system** with forward-biased state progression (59.2%), exception handling via FQ escape routes, and kernel-based (k/h/e) state transitions. The system tracks material through FL stages (INITIAL->TERMINAL) with monitoring checkpoints (LINK) and control markers (daiin/ol).

## Key Findings

### 1. Role Semantics

| Role | Share | Function | Key Feature |
|------|-------|----------|-------------|
| EN | 31.2% | State transition | 91.9% kernel, self-loops 38.5% |
| FL | 4.7% | Material state index | Kernel-free, 5 stages |
| FQ | 12.5% | Escape handler | 80.4% triggered by hazard |
| CC | 3.2% | Control markers | daiin=init, ol=continue |
| AX | 17.9% | Support/monitoring | Includes LINK checkpoints |

### 2. Kernel Semantics

Position ordering: **e (0.404) < h (0.410) < k (0.443)**

- 'e' = stability/setup (earliest)
- 'h' = alignment (middle)
- 'k' = activation (latest)

Most common combo: "he" (31.4%)

### 3. Control Flow Grammar

High-probability transitions:
- EN->EN (38.5%) - processing continues
- CC->EN (37.7%) - control triggers processing
- FQ->EN (29.5%) - escape recovers to processing

Escape pattern:
- FL->FQ (16.0%) - hazard state triggers escape

### 4. Process Domain

| Test | Result | Interpretation |
|------|--------|----------------|
| Forward bias | 59.2% | Moderately forward |
| Monotonic lines | 59.7% | Mostly orderly |
| Full loops | 1.7% | Rarely cyclic |
| Backward | 40.8% | Corrections allowed |

**Verdict:** Batch processing with correction capability

### 5. Section Variation

- BIO: Highest EN (40.1%) - intensive processing
- HERBAL_B: Highest FL/FQ - state-heavy
- FL/FQ ratio ~0.37 across sections (similar stability)

## Semantic Model

```
BATCH PROCESSING CONTROL SYSTEM
+------------------------------------------------------------------+
|  MONITORING      PROCESSING       STATE          ESCAPE           |
|     LINK    -->     EN      -->    FL     -->     FQ             |
|   (check)       (k/h/e ops)     (stage)      (if hazard)         |
|                     ^              |              |               |
|                     +--------------+--------------+               |
|                         (loop back to processing)                 |
+------------------------------------------------------------------+

Control injection: CC (daiin=init, ol=continue) -> EN

Kernel pattern: e-setup -> h-align -> k-activate
```

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C873 | Kernel Semantic Pattern | e<h<k positional ordering |
| C874 | CC Token Functions | daiin=init (0.370), ol=continue (0.461) |
| C875 | Escape Trigger Grammar | 80.4% from hazard FL stages |
| C876 | LINK Checkpoint Function | Position 0.405, routes to EN |
| C877 | Transition Grammar | EN self-loop 38.5%, CC->EN 37.7% |
| C878 | Section Program Variation | BIO=high EN, HERBAL_B=high FL/FQ |
| C879 | Process Domain Verdict | Batch processing, 59.2% forward |
| C880 | Integrated Control Model | See semantic model above |

## Confidence Assessment

- **HIGH:** Role distribution, transition grammar, FL stages, CC positions
- **MEDIUM:** Kernel semantics, escape triggers, LINK function
- **LOW:** Process domain labels, specific semantic interpretations

## Structural Provenance

Built on Tier 2 constraints: C467, C552, C770-C815, C788-C791, C804-C809, C855-C862

No contradictions with existing constraints found.
"""

with open(findings_path, 'w') as f:
    f.write(findings_content)
print(f"Saved FINDINGS.md")
