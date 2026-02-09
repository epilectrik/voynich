#!/usr/bin/env python3
"""
Demonstrate what we can decode from a B folio using current model.
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# Three-tier MIDDLE classification
PREP_MIDDLES = {'tch', 'pch', 'lch', 'ksh', 'sch', 'cth'}
THERMO_MIDDLES = {'k', 't', 'e', 'ch', 'sh'}
EXTENDED_MIDDLES = {'ke', 'kch', 'te', 'the'}

# Kernel roles
KERNEL_OPS = {
    'k': 'ENERGY (heat application)',
    'h': 'HAZARD (boundary monitoring)',
    'e': 'ESCAPE (equilibration/release)',
}

# Brunschwig semantic mappings (Tier 4)
BRUNSCHWIG_MAP = {
    'tch': 'POUND (mechanical breakdown)',
    'pch': 'CHOP (cutting/division)',
    'ke': 'SUSTAINED HEAT (equilibration cycle)',
    'kch': 'PRECISION BURST (controlled heat pulse)',
    'te': 'GENTLE SUSTAINED (low heat maintenance)',
}

def classify_middle(middle):
    """Classify MIDDLE into three-tier structure."""
    if middle in PREP_MIDDLES:
        return 'PREP'
    elif middle in EXTENDED_MIDDLES:
        return 'EXTENDED'
    elif middle in THERMO_MIDDLES:
        return 'THERMO'
    else:
        return 'OTHER'

def analyze_folio(folio_id):
    tx = Transcript()
    morph = Morphology()

    # Get folio tokens
    folio_tokens = [t for t in tx.currier_b() if t.folio == folio_id]

    if not folio_tokens:
        print(f"No tokens found for folio {folio_id}")
        return

    print(f"=" * 60)
    print(f"FOLIO {folio_id}: {len(folio_tokens)} tokens")
    print(f"=" * 60)

    # Group by line
    lines = defaultdict(list)
    for t in folio_tokens:
        lines[t.line].append(t)

    # Analyze each line
    total_lines = len(lines)
    tier_counts = defaultdict(int)
    kernel_counts = defaultdict(int)

    print(f"\n{'LINE':<5} {'POS':<5} {'TIER PROFILE':<20} {'TOKENS'}")
    print("-" * 60)

    for i, line_num in enumerate(sorted(lines.keys())):
        toks = lines[line_num]
        pos = i / max(total_lines - 1, 1)  # Normalized position

        # Classify tokens
        line_tiers = defaultdict(int)
        line_kernels = defaultdict(int)
        decoded = []

        for t in toks:
            m = morph.extract(t.word)
            if m.middle:
                tier = classify_middle(m.middle)
                line_tiers[tier] += 1
                tier_counts[tier] += 1

                # Check for kernel
                for k in ['k', 'h', 'e']:
                    if k in m.middle:
                        line_kernels[k] += 1
                        kernel_counts[k] += 1

                # Build decoded representation
                if m.middle in BRUNSCHWIG_MAP:
                    decoded.append(f"[{m.middle}={BRUNSCHWIG_MAP[m.middle][:10]}]")
                elif m.middle in KERNEL_OPS:
                    decoded.append(f"[{m.middle}={KERNEL_OPS[m.middle][:10]}]")
                else:
                    decoded.append(m.middle)

        # Format tier profile
        tier_str = ' '.join(f"{t}:{line_tiers[t]}" for t in ['PREP', 'THERMO', 'EXTENDED'] if line_tiers[t])
        if not tier_str:
            tier_str = "OTHER"

        print(f"{line_num:<5} {pos:.2f}  {tier_str:<20} {' '.join(decoded[:5])}")

    # Summary
    print(f"\n{'=' * 60}")
    print("FOLIO SUMMARY")
    print(f"{'=' * 60}")

    print(f"\nThree-Tier Distribution:")
    total = sum(tier_counts.values()) or 1
    for tier in ['PREP', 'THERMO', 'EXTENDED', 'OTHER']:
        pct = tier_counts[tier] / total * 100
        bar = '#' * int(pct / 2)
        print(f"  {tier:<10}: {tier_counts[tier]:3} ({pct:5.1f}%) {bar}")

    print(f"\nKernel Distribution:")
    k_total = sum(kernel_counts.values()) or 1
    for k, desc in KERNEL_OPS.items():
        pct = kernel_counts[k] / k_total * 100
        print(f"  {k} ({desc[:15]}): {kernel_counts[k]:3} ({pct:5.1f}%)")

    # Determine REGIME
    print(f"\nREGIME Assessment:")
    intensive = tier_counts['PREP']
    extended = tier_counts['EXTENDED']

    if tier_counts['PREP'] > tier_counts['THERMO'] * 0.5:
        print("  -> Elevated PREP suggests material processing focus")
    if kernel_counts['k'] > kernel_counts['h'] * 2:
        print("  -> k >> h suggests energy-dominant (not hazard-constrained)")
    if extended > total * 0.2:
        print("  -> High EXTENDED suggests sustained/precision operations")

    print(f"\n{'=' * 60}")
    print("WHAT WE CAN DECODE:")
    print("  [+] Operation types (prep/thermo/extended)")
    print("  [+] Kernel balance (energy vs hazard vs escape)")
    print("  [+] Positional phase (early=prep, mid=thermo, late=extended)")
    print("  [+] Procedure type (water vs oil vs precision)")
    print(f"\nWHAT WE CANNOT DECODE:")
    print("  [-] Specific material being processed")
    print("  [-] Exact temperatures or durations")
    print("  [-] Individual token meanings")
    print("  [-] The 'content' - only the 'structure'")

if __name__ == '__main__':
    # Default to a pharma folio
    folio = sys.argv[1] if len(sys.argv) > 1 else 'f88r'
    analyze_folio(folio)
