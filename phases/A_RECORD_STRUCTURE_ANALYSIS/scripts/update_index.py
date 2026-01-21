#!/usr/bin/env python3
"""Update INDEX.md with C498.a entry"""

def main():
    filepath = 'context/CLAIMS/INDEX.md'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add C498.a to table
    old_table = '| **498** | **Registry-Internal Vocabulary Track** (56.6% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don\'t propagate to B) | 2 | A | ⊂ currier_a |\n| 499 |'

    new_table = '| **498** | **Registry-Internal Vocabulary Track** (56.6% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don\'t propagate to B) | 2 | A | ⊂ currier_a |\n| **498.a** | **A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed) | 2 | A | ⊂ currier_a |\n| 499 |'

    if '498.a' in content:
        print("C498.a already in INDEX.md")
        return 0

    content = content.replace(old_table, new_table)

    # Add characterization note
    old_char = '**C498-CHAR-A-SEGMENT (Tier 3):** RI closure operates hierarchically: 1.76× at line-final, 1.43× at segment-final. RI-RICH segments (>30% RI, 6.1%) are short, PREFIX-coherent, terminal-preferring. PREFIX does NOT predict segment RI profile (p=0.151) — RI concentration is positional, not PREFIX-bound. See currier_a.md.\n\n---'

    new_char = '''**C498-CHAR-A-SEGMENT (Tier 3):** RI closure operates hierarchically: 1.76× at line-final, 1.43× at segment-final. RI-RICH segments (>30% RI, 6.1%) are short, PREFIX-coherent, terminal-preferring. PREFIX does NOT predict segment RI profile (p=0.151) — RI concentration is positional, not PREFIX-bound. See currier_a.md.

**C498.a (Tier 2 Refinement):** A∩B shared vocabulary bifurcates into AZC-Mediated (154 MIDDLEs, true pipeline) and B-Native Overlap (114 MIDDLEs, B vocabulary with incidental A presence). Pipeline scope is narrower than "all A∩B shared" implies. See currier_a.md.

---'''

    content = content.replace(old_char, new_char)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: INDEX.md updated with C498.a")
    return 0

if __name__ == '__main__':
    exit(main())
