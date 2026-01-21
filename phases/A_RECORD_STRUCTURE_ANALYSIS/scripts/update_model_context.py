#!/usr/bin/env python3
"""Update MODEL_CONTEXT.md with C498.a hierarchy"""

def main():
    filepath = 'context/MODEL_CONTEXT.md'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_section = '''### Two-Track Vocabulary Structure (C498)

Currier A MIDDLEs divide into two vocabulary tracks:

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating** | 268 (43.4%) | Standard prefixes/suffixes, 7.96 folio spread | Flow through A→AZC→B |
| **Registry-internal** | 349 (56.6%) | ct-prefix 5.1×, suffix-less 3×, 1.34 folio spread | Stay in A registry |

Registry-internal MIDDLEs encode **within-category fine distinctions** for A-registry navigation that don't propagate to B execution. The morphological signature (ct-prefix, suffix-less, folio-localized) reflects their A-internal scope.

**Note:** 8.9% of A-exclusive MIDDLEs also appear in AZC - this is interface noise from systems sharing the same alphabet, not a distinct vocabulary stratum. Verification testing rejected the "AZC-terminal bifurcation" hypothesis.'''

    new_section = '''### Two-Track Vocabulary Structure (C498, C498.a)

Currier A MIDDLEs divide into two vocabulary tracks, with the shared track further bifurcated:

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

**Key insight (C498.a):** Only 154 MIDDLEs (25% of A vocabulary) genuinely participate in the A→AZC→B pipeline. The 114 B-Native Overlap MIDDLEs appear in both A and B but never in AZC - they are B operational vocabulary with incidental A presence, not pipeline participants.

Registry-internal MIDDLEs encode **within-category fine distinctions** for A-registry navigation that don't propagate to B execution. The morphological signature (ct-prefix, suffix-less, folio-localized) reflects their A-internal scope.

**Note:** 8.9% of A-exclusive MIDDLEs also appear in AZC - this is interface noise from systems sharing the same alphabet, not a distinct vocabulary stratum. Verification testing rejected the "AZC-terminal bifurcation" hypothesis.'''

    if 'C498.a' in content and 'B-Native Overlap' in content:
        print("C498.a hierarchy already in MODEL_CONTEXT.md")
        return 0

    content = content.replace(old_section, new_section)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: MODEL_CONTEXT.md updated with C498.a hierarchy")
    return 0

if __name__ == '__main__':
    exit(main())
