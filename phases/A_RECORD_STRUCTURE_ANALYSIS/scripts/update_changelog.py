#!/usr/bin/env python3
"""Add phase summary to CHANGELOG.md"""

new_entry = '''## Version 2.72 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: PP Vocabulary Bifurcation (C498.a)

### Summary

Investigated the internal structure of "Pipeline-Participating" (PP) MIDDLEs from C498. Discovered that the 268 A∩B shared MIDDLEs comprise two structurally distinct subclasses, not a uniform pipeline-participating population.

### Key Findings

| Finding | Evidence |
|---------|----------|
| 114 bypass MIDDLEs | Appear in A and B but **never** in AZC |
| B-heavy frequency | 58.8% have B count > 2× A count |
| B-native vocabulary | e.g., `eck` A=2, B=85; `ect` A=2, B=46 |
| Pipeline narrower | Only 154 (25%) genuinely participate in A→AZC→B |

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

### Terminology Correction

The original "Pipeline-Participating" label is misleading:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

### External Validation

Reviewed by domain expert. Verdict: "This is a solid, architecture-strengthening refinement. It sharpens C498, clarifies pipeline scope, and removes an implicit overgeneralization — without reopening any closed tier."

### Constraint Changes

1. **C498.a added (Tier 2 Refinement):** A∩B shared vocabulary bifurcates into AZC-Mediated (154) and B-Native Overlap (114). Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass.

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498.a refinement
- `context/CLAIMS/INDEX.md` - Added C498.a entry and characterization note
- `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` - Updated two_track_structure with substructure
- `context/MODEL_CONTEXT.md` - Updated Two-Track section with full hierarchy

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS (PP vocabulary analysis)
- Scripts: pp_middle_frequency.py, pp_singleton_analysis.py, pp_singleton_b_frequency.py, pp_middle_propagation.py, pp_bypass_azc.py
- Results: pp_middle_propagation.json

---

'''

def main():
    filepath = 'context/SYSTEM/CHANGELOG.md'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Version 2.72' in content or 'C498.a' in content:
        print("Version 2.72 / C498.a already in CHANGELOG")
        return 0

    # Find the position after the header
    header_end = content.find('---\n\n## Version')
    if header_end == -1:
        print("ERROR: Could not find insertion point")
        return 1

    # Insert new entry after the header separator
    new_content = content[:header_end + 5] + new_entry + content[header_end + 5:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: CHANGELOG.md updated with v2.72")
    return 0

if __name__ == '__main__':
    exit(main())
