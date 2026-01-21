#!/usr/bin/env python3
"""Add C498.a refinement to currier_a.md"""

c498a_content = '''### C498.a - A∩B Shared Vocabulary Bifurcation (Tier 2 Refinement)
**Tier:** 2 | **Status:** CLOSED

The A∩B shared MIDDLE vocabulary (originally labeled "Pipeline-Participating") comprises two structurally distinct subclasses:

| Subclass | Count | % of Shared | Mechanism |
|----------|-------|-------------|-----------|
| **AZC-Mediated** | 154 | 57.5% | A→AZC→B constraint propagation |
| **B-Native Overlap (BN)** | 114 | 42.5% | B operational vocabulary with incidental A presence |

**Evidence:**
- Traced all 268 A∩B MIDDLEs through Currier A, AZC folios, and Currier B
- 114 MIDDLEs appear in A and B but **never** in any AZC folio
- Zero-AZC MIDDLEs show B-heavy frequency ratios (e.g., `eck` A=2, B=85; `ect` A=2, B=46)
- Pattern consistent with B-native origin, not A→B transmission

**AZC-Mediated substructure:**

| AZC Presence | Count | Mean B Folio Spread |
|--------------|-------|---------------------|
| Universal (10+ AZC folios) | 17 | 48.7 folios |
| Moderate (3-10 AZC folios) | 45 | 20.1 folios |
| Restricted (1-2 AZC folios) | 92 | 6.8 folios |

**B-Native Overlap characteristics:**
- Mean B folio spread: 4.0 folios (flat, AZC-independent)
- B-heavy (B > 2×A): 67 MIDDLEs (58.8%)
- A-heavy (A > 2×B): 12 MIDDLEs (10.5%)
- Execution-infrastructure vocabulary: boundary discriminators, stabilizers, orthographic variants

**Architectural implications:**
- Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass
- Pipeline scope is narrower than "all A∩B shared" implies
- A's outbound vocabulary to pipeline is 154 MIDDLEs (25% of A vocabulary), not 268 (43.4%)

**Relationship to existing constraints:**
- Consistent with C384 (No Entry-Level A-B Coupling): BN MIDDLEs demonstrate statistical, not referential, sharing
- Consistent with C383 (Global Type System): Shared morphology ≠ shared function
- Refines C468-C470: Pipeline model preserved but now precisely scoped

**Terminology correction:**
The original "Pipeline-Participating" label is misleading. Recommended terminology:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

**Complete A MIDDLE hierarchy:**
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

**Source:** A_RECORD_STRUCTURE_ANALYSIS phase (2026-01-20)
**External validation:** Reviewed by domain expert; confirmed as architecture-strengthening refinement that sharpens pipeline scope without contradiction.

---

'''

def main():
    filepath = 'context/CLAIMS/currier_a.md'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '### C498-CHAR-A-CLOSURE - RI Closure Tokens (Tier 3 Characterization)'

    if marker not in content:
        print(f"ERROR: Marker not found in {filepath}")
        return 1

    if '### C498.a' in content:
        print("C498.a already exists, skipping")
        return 0

    new_content = content.replace(marker, c498a_content + marker)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: C498.a added to currier_a.md")
    return 0

if __name__ == '__main__':
    exit(main())
