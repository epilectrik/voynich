#!/usr/bin/env python3
"""
Full folio decoder using all constraint knowledge.

Uses:
- C371-374: PREFIX functional grammar
- C375-378: SUFFIX functional grammar
- C372: Kernel-heavy vs kernel-light prefixes
- C376: Kernel-heavy vs kernel-light suffixes
- C884: Animal suffix markers
- F-BRU-011: Three-tier MIDDLE structure
- F-BRU-018: Root processing markers (tch/pch)
- F-BRU-020: Output category markers
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# === PREFIX CLASSIFICATION (C371-374) ===
PREFIX_ROLES = {
    # KERNEL-HEAVY (C372): 100% kernel contact
    'ch': 'EN_KERNEL',    # Energy, kernel-heavy
    'sh': 'EN_KERNEL',    # Energy, kernel-heavy
    'ok': 'EN_KERNEL',    # Energy, kernel-heavy
    'lk': 'EN_KERNEL',    # Energy, kernel-heavy
    'lch': 'EN_KERNEL',   # Energy, kernel-heavy
    'yk': 'EN_KERNEL',    # Energy, kernel-heavy
    'ke': 'EN_KERNEL',    # Extended energy

    # QO-FAMILY (C387): Phase-transition hub
    'qo': 'EN_QO',        # Energy, LINK-avoiding
    'o': 'EN_QO',         # Energy variant

    # KERNEL-LIGHT / AUXILIARY (C372)
    'da': 'AX_SCAFFOLD',  # Auxiliary, 4.9% kernel
    'sa': 'AX_SCAFFOLD',  # Auxiliary, 3.4% kernel

    # LINK-ATTRACTED (C373)
    'al': 'AX_LINK',      # Auxiliary, LINK-attracted 2.48x
    'ol': 'AX_LINK',      # Auxiliary, LINK-attracted 1.82x

    # LINE-INITIAL (C371)
    'so': 'CC_INIT',      # Core control, line-initial 6.3x
    'ych': 'CC_INIT',     # Core control, line-initial 7.0x
    'pch': 'PREP',        # Preparation, line-initial 5.2x
    'tch': 'PREP',        # Preparation (POUND)
    'kch': 'PREP',        # Precision burst

    # LINE-FINAL (C371)
    'lo': 'FL_FINAL',     # Flow, line-final 3.7x
}

# === SUFFIX CLASSIFICATION (C375-378, C884) ===
SUFFIX_ROLES = {
    # KERNEL-HEAVY (C376)
    'edy': 'KERN_HEAVY',  # 91% kernel
    'ey': 'KERN_HEAVY',   # 95% kernel (also ANIMAL marker C884)
    'dy': 'KERN_HEAVY',   # 83% kernel
    'eey': 'KERN_HEAVY',  # Extended

    # KERNEL-LIGHT / LINK-ATTRACTED (C377)
    'l': 'LINK_ATTR',     # 2.78x near LINK
    'in': 'LINK_ATTR',    # 2.30x near LINK
    'r': 'LINK_ATTR',     # 2.16x near LINK
    'aiin': 'LINK_ATTR',  # Common variant
    'ain': 'LINK_ATTR',   # Common variant

    # LINE-FINAL (C375)
    'am': 'LINE_FINAL',   # 7.7x line-final
    'om': 'LINE_FINAL',   # 8.7x line-final
    'oly': 'LINE_FINAL',  # 4.6x line-final

    # ANIMAL MARKERS (C884)
    'ol': 'ANIMAL',       # Animal material marker
    'or': 'ANIMAL',       # Animal material marker

    # WATER markers (F-BRU-020)
    'ly': 'WATER',        # 0.32x in OIL
    'al': 'WATER',        # 0.48x in OIL
}

# === MIDDLE CLASSIFICATION (F-BRU-011, F-BRU-018) ===
MIDDLE_TIERS = {
    # PREPARATION (early, F-BRU-011)
    'tch': ('PREP', 'POUND - mechanical breakdown'),
    'pch': ('PREP', 'CHOP - cutting/division'),
    'lch': ('PREP', 'preparation operation'),
    'ksh': ('PREP', 'preparation operation'),
    'sch': ('PREP', 'preparation operation'),
    'cth': ('PREP', 'preparation operation'),

    # THERMODYNAMIC (mid, F-BRU-011)
    'k': ('THERMO', 'ENERGY - heat application'),
    't': ('THERMO', 'energy transfer'),
    'e': ('THERMO', 'ESCAPE - equilibration'),
    'ch': ('THERMO', 'precision monitoring'),
    'sh': ('THERMO', 'monitoring'),
    'h': ('THERMO', 'HAZARD - boundary check'),

    # EXTENDED (late, F-BRU-011)
    'ke': ('EXTENDED', 'SUSTAINED - equilibration cycle'),
    'kch': ('EXTENDED', 'PRECISION BURST - controlled pulse'),
    'te': ('EXTENDED', 'gentle sustained'),
    'the': ('EXTENDED', 'extended thermal'),

    # OIL markers (F-BRU-020)
    'kc': ('OIL_MARKER', 'oil procedure completion'),
    'okch': ('OIL_MARKER', 'oil procedure completion'),
}

# === KERNEL SEMANTICS ===
KERNEL_MEANING = {
    'k': 'ENERGY (heat input)',
    'h': 'HAZARD (boundary monitoring)',
    'e': 'ESCAPE (equilibration/release)',
}

def classify_token(word, morph):
    """Full classification of a token."""
    m = morph.extract(word)

    result = {
        'word': word,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'prefix_role': None,
        'suffix_role': None,
        'middle_tier': None,
        'middle_meaning': None,
        'kernels': [],
        'material_markers': [],
    }

    # Prefix role
    if m.prefix and m.prefix in PREFIX_ROLES:
        result['prefix_role'] = PREFIX_ROLES[m.prefix]

    # Suffix role
    if m.suffix and m.suffix in SUFFIX_ROLES:
        result['suffix_role'] = SUFFIX_ROLES[m.suffix]

    # Animal/material markers from suffix
    if m.suffix in ['ey', 'ol', 'eey', 'or']:
        result['material_markers'].append('ANIMAL')
    if m.suffix in ['ly', 'al']:
        result['material_markers'].append('WATER')

    # Middle tier and meaning
    if m.middle:
        if m.middle in MIDDLE_TIERS:
            result['middle_tier'], result['middle_meaning'] = MIDDLE_TIERS[m.middle]
        else:
            # Check for contained patterns
            for mid, (tier, meaning) in MIDDLE_TIERS.items():
                if mid in m.middle and len(mid) >= 2:
                    result['middle_tier'] = tier
                    result['middle_meaning'] = f"contains {mid}"
                    break

        # Extract kernels
        for k in ['k', 'h', 'e']:
            if k in m.middle:
                result['kernels'].append(k)

    return result

def analyze_folio(folio_id):
    tx = Transcript()
    morph = Morphology()

    # Get folio tokens
    folio_tokens = [t for t in tx.currier_b() if t.folio == folio_id]

    if not folio_tokens:
        print(f"No tokens found for folio {folio_id}")
        return

    print(f"{'=' * 70}")
    print(f"FOLIO {folio_id}: {len(folio_tokens)} tokens - FULL DECODE")
    print(f"{'=' * 70}")

    # Classify all tokens
    classifications = []
    for t in folio_tokens:
        c = classify_token(t.word, morph)
        c['line'] = t.line
        classifications.append(c)

    # === STATISTICS ===
    prefix_roles = defaultdict(int)
    suffix_roles = defaultdict(int)
    middle_tiers = defaultdict(int)
    kernels = defaultdict(int)
    material_markers = defaultdict(int)
    classified_count = 0

    for c in classifications:
        if c['prefix_role']:
            prefix_roles[c['prefix_role']] += 1
            classified_count += 1
        if c['suffix_role']:
            suffix_roles[c['suffix_role']] += 1
        if c['middle_tier']:
            middle_tiers[c['middle_tier']] += 1
        for k in c['kernels']:
            kernels[k] += 1
        for m in c['material_markers']:
            material_markers[m] += 1

    total = len(classifications)

    # === PREFIX ROLE DISTRIBUTION ===
    print(f"\n1. PREFIX ROLES (from C371-374):")
    print(f"   Classified: {sum(prefix_roles.values())}/{total} ({100*sum(prefix_roles.values())/total:.1f}%)")
    for role in ['EN_KERNEL', 'EN_QO', 'AX_SCAFFOLD', 'AX_LINK', 'CC_INIT', 'PREP', 'FL_FINAL']:
        if prefix_roles[role]:
            pct = 100 * prefix_roles[role] / total
            print(f"   {role:12}: {prefix_roles[role]:4} ({pct:5.1f}%)")

    # === SUFFIX ROLE DISTRIBUTION ===
    print(f"\n2. SUFFIX ROLES (from C375-378):")
    print(f"   Classified: {sum(suffix_roles.values())}/{total} ({100*sum(suffix_roles.values())/total:.1f}%)")
    for role in ['KERN_HEAVY', 'LINK_ATTR', 'LINE_FINAL', 'ANIMAL', 'WATER']:
        if suffix_roles[role]:
            pct = 100 * suffix_roles[role] / total
            print(f"   {role:12}: {suffix_roles[role]:4} ({pct:5.1f}%)")

    # === MIDDLE TIER DISTRIBUTION ===
    print(f"\n3. MIDDLE TIERS (from F-BRU-011):")
    print(f"   Classified: {sum(middle_tiers.values())}/{total} ({100*sum(middle_tiers.values())/total:.1f}%)")
    for tier in ['PREP', 'THERMO', 'EXTENDED', 'OIL_MARKER']:
        if middle_tiers[tier]:
            pct = 100 * middle_tiers[tier] / total
            print(f"   {tier:12}: {middle_tiers[tier]:4} ({pct:5.1f}%)")

    # === KERNEL DISTRIBUTION ===
    print(f"\n4. KERNEL OPERATIONS:")
    kernel_total = sum(kernels.values())
    for k in ['k', 'h', 'e']:
        if kernel_total > 0:
            pct = 100 * kernels[k] / kernel_total
            print(f"   {k} ({KERNEL_MEANING[k]:20}): {kernels[k]:4} ({pct:5.1f}%)")

    # === MATERIAL MARKERS ===
    print(f"\n5. MATERIAL CATEGORY MARKERS (from C884, F-BRU-020):")
    for marker in ['ANIMAL', 'WATER']:
        if material_markers[marker]:
            pct = 100 * material_markers[marker] / total
            print(f"   {marker:12}: {material_markers[marker]:4} ({pct:5.1f}%)")

    if not material_markers:
        print("   No material markers -> likely DELICATE PLANT (unmarked default)")

    # === SAMPLE DECODED LINES ===
    print(f"\n6. SAMPLE DECODED LINES:")
    lines = defaultdict(list)
    for c in classifications:
        lines[c['line']].append(c)

    for line_num in sorted(lines.keys())[:5]:
        toks = lines[line_num]
        print(f"\n   Line {line_num}:")
        for c in toks[:4]:
            parts = []
            if c['prefix_role']:
                parts.append(c['prefix_role'])
            if c['middle_tier']:
                parts.append(c['middle_tier'])
            if c['suffix_role']:
                parts.append(c['suffix_role'])
            if c['kernels']:
                parts.append(f"kern:{','.join(c['kernels'])}")

            decode = ' + '.join(parts) if parts else '(unclassified)'
            print(f"      {c['word']:12} -> {decode}")

    # === FOLIO INTERPRETATION ===
    print(f"\n{'=' * 70}")
    print("FOLIO INTERPRETATION:")
    print(f"{'=' * 70}")

    # Energy balance
    if kernel_total > 0:
        k_pct = kernels['k'] / kernel_total
        h_pct = kernels['h'] / kernel_total
        e_pct = kernels['e'] / kernel_total

        if e_pct > 0.4:
            print(f"   [+] ESCAPE-DOMINANT ({e_pct*100:.0f}%): Focus on equilibration/release")
        elif k_pct > 0.5:
            print(f"   [+] ENERGY-DOMINANT ({k_pct*100:.0f}%): Active heating focus")
        elif h_pct > 0.3:
            print(f"   [+] HAZARD-HEAVY ({h_pct*100:.0f}%): Careful boundary monitoring")

    # Processing type
    prep_pct = middle_tiers['PREP'] / total if total > 0 else 0
    ext_pct = middle_tiers['EXTENDED'] / total if total > 0 else 0

    if prep_pct > 0.05:
        print(f"   [+] PREPARATION PHASE PRESENT ({prep_pct*100:.1f}%): Material processing (tch=pound, pch=chop)")
    else:
        print(f"   [-] LOW PREPARATION ({prep_pct*100:.1f}%): Likely pre-processed material")

    if ext_pct > 0.03:
        print(f"   [+] EXTENDED OPERATIONS ({ext_pct*100:.1f}%): Sustained/precision processing")

    # Material category
    if material_markers['ANIMAL'] > 5:
        print(f"   [+] ANIMAL MATERIAL MARKERS: Precision timing required (REGIME_4)")
    elif prep_pct > 0.05:
        print(f"   [+] ROOT/DENSE MATERIAL: Mechanical processing required")
    else:
        print(f"   [+] DELICATE PLANT MATERIAL (default): Gentle processing assumed")

    # Output type
    if middle_tiers['OIL_MARKER'] > 0:
        print(f"   [+] OIL/RESIN OUTPUT: Intensive completion operations")
    else:
        print(f"   [+] WATER OUTPUT (default): Standard distillation")

    print(f"\n   Overall classification rate: ~{100*(sum(prefix_roles.values())+sum(middle_tiers.values()))/(2*total):.0f}%")

if __name__ == '__main__':
    folio = sys.argv[1] if len(sys.argv) > 1 else 'f107r'
    analyze_folio(folio)
