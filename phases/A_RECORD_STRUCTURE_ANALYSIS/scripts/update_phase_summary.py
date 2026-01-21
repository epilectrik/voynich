#!/usr/bin/env python3
"""Add Part 4 (PP Bifurcation) to PHASE_SUMMARY.md"""

part4_content = '''---

## Part 4: PP Vocabulary Bifurcation (C498.a)

Following the RI closure characterizations (Parts 1-3), we investigated the internal structure of the "Pipeline-Participating" (PP) vocabulary track.

### Question

Do all 268 A∩B shared MIDDLEs actually participate in the A→AZC→B pipeline?

### Investigation Path

#### Step 1: PP MIDDLE Frequency Distribution

| Category | Count | % of PP | Token Coverage |
|----------|-------|---------|----------------|
| Singletons (freq=1) | 98 | 36.6% | 1.1% |
| Low (2-5) | 72 | 26.9% | 3.0% |
| Mid (6-50) | 68 | 25.4% | 16.6% |
| High (>50) | 30 | 11.2% | 79.3% |

**Finding:** Top 10 MIDDLEs cover 80.1% of PP usage. `_EMPTY_` alone = 58.5%.

#### Step 2: AZC Propagation Trace

Traced all 268 PP MIDDLEs through A → AZC → B:

| AZC Category | Count | % of PP | Mean B Folio Spread |
|--------------|-------|---------|---------------------|
| No AZC presence | **114** | **42.5%** | 4.0 folios |
| Restricted (1-2 AZC folios) | 92 | 34.3% | 6.8 folios |
| Moderate (3-10 AZC folios) | 45 | 16.8% | 20.1 folios |
| Universal (10+ AZC folios) | 17 | 6.3% | 48.7 folios |

**Critical Finding:** 114 PP MIDDLEs (42.5%) appear in A and B but NEVER in any AZC folio.

#### Step 3: Bypass MIDDLE Characteristics

The 114 "bypass" MIDDLEs show B-heavy frequency ratios:

| MIDDLE | A count | B count | Ratio |
|--------|---------|---------|-------|
| `eck` | 2 | 85 | 42× more in B |
| `ect` | 2 | 46 | 23× more in B |
| `keed` | 1 | 29 | 29× more in B |
| `pch` | 2 | 25 | 12× more in B |

**A vs B balance:**
- B-heavy (B > 2×A): 67 MIDDLEs (58.8%)
- A-heavy (A > 2×B): 12 MIDDLEs (10.5%)
- Balanced: 35 MIDDLEs (30.7%)

### Key Insight

The B-heavy ratios indicate these are NOT A vocabulary that "selects" B destinations. They are **B-native operational vocabulary** with incidental A presence. Causality runs B→A (shared operational domain), not A→B (pipeline transmission).

### Complete A MIDDLE Hierarchy

```
A MIDDLEs (617 total)
├── RI: Registry-Internal (349, 56.6%)
│     A-exclusive, instance discrimination, folio-localized
│
└── Shared with B (268, 43.4%)
    ├── AZC-Mediated (154, 25.0% of A vocabulary)
    │     A→AZC→B constraint propagation
    │     ├── Universal (17) - 10+ AZC folios
    │     ├── Moderate (45) - 3-10 AZC folios
    │     └── Restricted (92) - 1-2 AZC folios
    │
    └── B-Native Overlap (114, 18.5% of A vocabulary)
          Zero AZC presence, B-dominant frequency
          Execution-layer vocabulary with incidental A appearance
```

### Architectural Implications

1. **Pipeline scope narrower than assumed:** Only 154 (25% of A vocabulary) genuinely participate in A→AZC→B constraint propagation
2. **C468-C470 preserved but scoped:** Constraint inheritance applies only to AZC-Mediated subclass
3. **Reinforces C384:** No entry-level A-B coupling — B-Native Overlap demonstrates statistical, not referential, sharing

### Terminology Correction

The original "Pipeline-Participating" label is misleading:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

### External Expert Validation

The finding was reviewed by a domain expert:

> "This is a solid, architecture-strengthening refinement. It sharpens C498, clarifies pipeline scope, and removes an implicit overgeneralization — without reopening any closed tier."

**Verdict:** C498.a added as Tier 2 refinement (not independent constraint).

### Constraint Added

> **C498.a (Tier 2 Refinement):**
> The A∩B shared MIDDLE vocabulary comprises two structurally distinct subclasses: (i) AZC-mediated pipeline MIDDLEs (154), which propagate A-origin discrimination constraints through AZC into B; and (ii) B-native overlap MIDDLEs (114), which appear in both A and B but do not participate in AZC mediation and function as execution-layer vocabulary with incidental A presence. Constraint inheritance (C468-C470) applies only to the former subclass.

---

## Final Files Produced

```
phases/A_RECORD_STRUCTURE_ANALYSIS/
├── scripts/
│   ├── ri_pp_structure_v2.py
│   ├── ri_signal_investigation.py
│   ├── ri_position_analysis.py
│   ├── analyze_multi_ri.py
│   ├── check_ri_adjacency.py
│   ├── noncloser_ri_investigation.py
│   ├── closer_frequency.py
│   ├── closer_folio_analysis.py
│   ├── prefix_ri_pp_crosstab.py
│   ├── da_segment_ri_pp_composition.py
│   ├── da_segment_ri_position.py
│   ├── da_segment_clustering.py
│   ├── pp_middle_frequency.py          # Part 4
│   ├── pp_singleton_analysis.py        # Part 4
│   ├── pp_singleton_b_frequency.py     # Part 4
│   ├── pp_middle_propagation.py        # Part 4
│   └── pp_bypass_azc.py                # Part 4
├── results/
│   ├── ri_pp_structure_v2.json
│   ├── ri_signal_investigation.json
│   ├── noncloser_ri_investigation.json
│   ├── prefix_ri_pp_crosstab.json
│   ├── da_segment_ri_pp_composition.json
│   ├── da_segment_ri_position.json
│   ├── da_segment_clustering.json
│   └── pp_middle_propagation.json      # Part 4
└── PHASE_SUMMARY.md
```

---

## Phase Status: COMPLETE

All four parts of A_RECORD_STRUCTURE_ANALYSIS have been completed:

| Part | Topic | Outcome |
|------|-------|---------|
| 1 | RI Positional Signal | C498-CHAR-A-CLOSURE (Tier 3) |
| 2 | Non-Closer RI | Opener/middle characterization |
| 3 | DA Segmentation | C498-CHAR-A-SEGMENT (Tier 3) |
| 4 | PP Bifurcation | **C498.a (Tier 2 Refinement)** |

The phase discovered both a distributional regularity (RI closure behavior) and an architectural refinement (PP/BN bifurcation) that sharpens the pipeline model.
'''

def main():
    filepath = 'phases/A_RECORD_STRUCTURE_ANALYSIS/PHASE_SUMMARY.md'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Part 4: PP Vocabulary Bifurcation' in content:
        print("Part 4 already in PHASE_SUMMARY.md")
        return 0

    # Find the "Open Questions" section and insert Part 4 before it
    open_questions_marker = '## Open Questions for Future Phases'
    if open_questions_marker in content:
        content = content.replace(open_questions_marker, part4_content + '\n' + open_questions_marker)
    else:
        # Append at end
        content = content + part4_content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Part 4 added to PHASE_SUMMARY.md")
    return 0

if __name__ == '__main__':
    exit(main())
