#!/usr/bin/env python3
"""Update CASC contract with C498.a terminology"""

def main():
    filepath = 'context/STRUCTURAL_CONTRACTS/currierA.casc.yaml'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update the two_track_structure section
    old_section = '''    two_track_structure:
      description: "MIDDLEs divide into pipeline-participating (43.4%) and registry-internal (56.6%)"
      pipeline_participating:
        count: 268
        characteristics: "Standard prefixes, standard suffixes, broad folio spread (7.96 folios)"
        role: "Flow through A→AZC→B pipeline"
      registry_internal:
        count: 349
        characteristics: "ct-prefix 5.1× enriched, suffix-less 3×, folio-localized (1.34 folios)"
        role: "Stay in A registry, encode within-category fine distinctions"
        interpretation: "Below granularity threshold for execution"
      provenance: "C498"'''

    new_section = '''    two_track_structure:
      description: "MIDDLEs divide into shared-with-B (43.4%) and registry-internal (56.6%)"
      shared_with_b:
        count: 268
        substructure:  # C498.a
          azc_mediated:
            count: 154
            percent: "25.0% of A vocabulary"
            role: "True pipeline participation: A→AZC→B constraint propagation"
            breakdown:
              universal: 17  # 10+ AZC folios, 48.7 B spread
              moderate: 45   # 3-10 AZC folios, 20.1 B spread
              restricted: 92 # 1-2 AZC folios, 6.8 B spread
          b_native_overlap:
            count: 114
            percent: "18.5% of A vocabulary"
            role: "B operational vocabulary with incidental A presence"
            characteristics: "Zero AZC presence, B-heavy frequency (58.8% have B > 2×A)"
            note: "NOT pipeline-participating despite A∩B membership"
        provenance: "C498.a"
      registry_internal:
        count: 349
        characteristics: "ct-prefix 5.1× enriched, suffix-less 3×, folio-localized (1.34 folios)"
        role: "Stay in A registry, encode within-category fine distinctions"
        interpretation: "Below granularity threshold for execution"
      provenance: "C498, C498.a"'''

    if 'C498.a' in content:
        print("C498.a already in CASC")
        return 0

    content = content.replace(old_section, new_section)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: CASC updated with C498.a terminology")
    return 0

if __name__ == '__main__':
    exit(main())
