"""
Currier A Behavioral Classification

Maps Currier A entries to behavioral chemistry properties:
- Operational Domain (what type of operation the entry encodes)
- Material Behavior Class (what material behaviors the operation handles)
- Sister Mode (variant within equivalence class)
- Decision Archetype (what type of judgment call is required)

Tier 3 - Speculative (consistent with semantic ceiling)
Source: ECR-1 through ECR-4, CCM-1

Key principle: We classify OPERATIONS ON materials, not materials themselves.
The system encodes "how to handle materials with these behaviors" not
"which specific substances are involved."
"""

import os
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from enum import Enum, auto

# =============================================================================
# BEHAVIORAL CONSTANTS (from ECR and CCM analysis)
# =============================================================================

# Material Behavior Classes (ECR-1)
# These describe how materials BEHAVE, not what they ARE
class MaterialBehavior(Enum):
    """
    Material behavior classes from ECR-1.

    Classification axes:
    - Phase behavior: Mobile (can change phase/location) vs Stable
    - Composition behavior: Distinct (can be fractionated) vs Homogeneous
    """
    M_A = "PHASE_SENSITIVE_MOBILE"      # Mobile + Distinct: requires careful control
    M_B = "UNIFORM_MOBILE"              # Mobile + Homogeneous: routine handling
    M_C = "PHASE_STABLE_DISTINCT"       # Stable + Distinct: exclusion-prone
    M_D = "CONTROL_STABLE"              # Stable + Homogeneous: infrastructure
    CROSS_CLASS = "CROSS_CLASS"         # Class-independent operation


# Operational Domains (CCM-1)
class OperationalDomain(Enum):
    """
    Operational domain from prefix analysis (CCM-1).

    The prefix encodes WHAT KIND OF OPERATION, not what material.
    """
    ENERGY_OPERATOR = "ENERGY_OPERATOR"           # ch-, qo-: Energy control ops
    FREQUENT_OPERATOR = "FREQUENT_OPERATOR"       # ok-, ot-: Routine ops
    CORE_CONTROL = "CORE_CONTROL"                 # da-, ol: Structural anchors
    REGISTRY_REFERENCE = "REGISTRY_REFERENCE"     # ct-: Reference to stable items


# Decision Archetypes (ECR-3)
class DecisionArchetype(Enum):
    """
    Decision archetypes - what judgment call does this entry support?
    """
    D1_PHASE_POSITION = "Is material in correct phase/location?"
    D2_FRACTION_IDENTITY = "Is this the fraction I think it is?"
    D5_ENERGY_LEVEL = "Is energy input appropriate?"
    D6_WAIT_VS_ACT = "Should I intervene or wait?"
    D9_CASE_COMPARISON = "Is this case like that previous case?"
    D12_REGIME_RECOGNITION = "What operating regime am I in?"


# Sister Pairs (C408)
SISTER_PAIRS = {
    'ch': 'sh',
    'sh': 'ch',
    'ok': 'ot',
    'ot': 'ok',
}

# Prefix → Domain Mapping (CCM-1)
PREFIX_TO_DOMAIN = {
    'ch': OperationalDomain.ENERGY_OPERATOR,
    'sh': OperationalDomain.ENERGY_OPERATOR,
    'qo': OperationalDomain.ENERGY_OPERATOR,
    'ok': OperationalDomain.FREQUENT_OPERATOR,
    'ot': OperationalDomain.FREQUENT_OPERATOR,
    'da': OperationalDomain.CORE_CONTROL,
    'ol': OperationalDomain.CORE_CONTROL,
    'ct': OperationalDomain.REGISTRY_REFERENCE,
}

# Domain → Material Class Association (CCM-1)
# Note: Operations HANDLE materials with these behaviors
DOMAIN_TO_MATERIAL = {
    OperationalDomain.ENERGY_OPERATOR: MaterialBehavior.M_A,      # Handles mobile+distinct
    OperationalDomain.FREQUENT_OPERATOR: MaterialBehavior.M_B,    # Handles mobile+homogeneous
    OperationalDomain.CORE_CONTROL: MaterialBehavior.CROSS_CLASS, # Class-independent
    OperationalDomain.REGISTRY_REFERENCE: MaterialBehavior.M_C,   # References stable+distinct
}

# Domain → Primary Decision Archetypes
DOMAIN_TO_ARCHETYPE = {
    OperationalDomain.ENERGY_OPERATOR: [DecisionArchetype.D1_PHASE_POSITION,
                                         DecisionArchetype.D5_ENERGY_LEVEL],
    OperationalDomain.FREQUENT_OPERATOR: [DecisionArchetype.D6_WAIT_VS_ACT,
                                           DecisionArchetype.D12_REGIME_RECOGNITION],
    OperationalDomain.CORE_CONTROL: [DecisionArchetype.D6_WAIT_VS_ACT],
    OperationalDomain.REGISTRY_REFERENCE: [DecisionArchetype.D2_FRACTION_IDENTITY,
                                            DecisionArchetype.D9_CASE_COMPARISON],
}

# Prefixes and Suffixes
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy', 'eeol',
            'r', 'l', 's', 'd', 'n', 'm', 'hy']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


# =============================================================================
# DATA CLASS
# =============================================================================

@dataclass
class ClassifiedEntry:
    """A Currier A entry with behavioral classification."""
    token: str
    folio: str
    section: str
    line_num: str
    line_position: str  # 'initial', 'final', or 'middle'

    # Morphological decomposition
    prefix: Optional[str]
    middle: Optional[str]
    suffix: Optional[str]

    # Behavioral classification
    operational_domain: Optional[str]
    material_behavior: Optional[str]
    sister_mode: Optional[str]           # 'primary' (ch, ok) or 'alternate' (sh, ot)
    sister_pair: Optional[str]           # the other member of the pair
    decision_archetypes: List[str]

    # Chemistry interpretation (Tier 3 prose only)
    chemistry_note: str

    # Validity
    is_valid: bool
    parse_status: str


# =============================================================================
# LOADING AND PARSING
# =============================================================================

def load_currier_a():
    """Load all Currier A tokens with metadata."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip()
                    line_init = parts[13].strip('"').strip() if len(parts) > 13 else '0'
                    line_final = parts[14].strip('"').strip() if len(parts) > 14 else '0'

                    if token:
                        pos = 'initial' if line_init == '1' else ('final' if line_final == '1' else 'middle')
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section,
                            'line_num': line_num,
                            'line_position': pos
                        })

    return tokens


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """
    Decompose token into PREFIX + MIDDLE + SUFFIX.

    Returns: (prefix, middle, suffix, status)
    """
    prefix = None
    remainder = token

    # Find prefix (longest match)
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None, "NO_PREFIX"

    # Find suffix (longest match from end)
    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s):
            if len(remainder) > len(s):
                suffix = s
                middle = remainder[:-len(s)]
                break
            elif remainder == s:
                suffix = s
                middle = ''
                break

    if not suffix and len(remainder) > 0:
        # Try last 1-2 chars as suffix
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        else:
            suffix = remainder
            middle = ''

    if middle == '':
        middle = None

    status = "VALID_ENTRY" if middle else "MINIMAL_FORM"
    return prefix, middle, suffix, status


def get_sister_mode(prefix: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Determine sister-pair membership.

    Returns: (mode, sister_pair)
    - mode: 'primary' (ch, ok) or 'alternate' (sh, ot)
    - sister_pair: the other member
    """
    if prefix in ['ch', 'ok']:
        return 'primary', SISTER_PAIRS.get(prefix)
    elif prefix in ['sh', 'ot']:
        return 'alternate', SISTER_PAIRS.get(prefix)
    else:
        return None, None


def generate_chemistry_note(domain: OperationalDomain, prefix: str,
                            material: MaterialBehavior, middle: Optional[str]) -> str:
    """
    Generate Tier-3 chemistry interpretation note.

    This is COMMENTARY, not formal structure. Uses concrete terms
    only as illustration of the behavioral pattern.
    """
    notes = {
        OperationalDomain.ENERGY_OPERATOR: (
            "Energy-control operation. In thermal-chemical context: "
            "handles volatile/aromatic materials requiring careful temperature regulation. "
            f"Prefix '{prefix}' indicates energy-intensive handling."
        ),
        OperationalDomain.FREQUENT_OPERATOR: (
            "Routine handling operation. In thermal-chemical context: "
            "handles uniform mobile materials (solvents, carriers) with lower hazard profile. "
            f"Prefix '{prefix}' indicates standard manipulation."
        ),
        OperationalDomain.CORE_CONTROL: (
            "Structural control operation. Class-independent; provides process articulation. "
            f"Prefix '{prefix}' anchors sequence regardless of material type."
        ),
        OperationalDomain.REGISTRY_REFERENCE: (
            "Registry reference entry. In thermal-chemical context: "
            "references stable materials (apparatus, containers, stable products). "
            f"Prefix '{prefix}' indicates lookup/comparison rather than active control."
        ),
    }

    base = notes.get(domain, "Unknown domain")

    if middle:
        base += f" MIDDLE='{middle}' differentiates this specific referent."

    return base


# =============================================================================
# MAIN CLASSIFICATION
# =============================================================================

def classify_entry(entry_data: dict) -> ClassifiedEntry:
    """Classify a single Currier A entry with behavioral properties."""
    token = entry_data['token']

    # Decompose
    prefix, middle, suffix, status = decompose_token(token)

    # Get behavioral classification
    if prefix:
        domain = PREFIX_TO_DOMAIN.get(prefix)
        material = DOMAIN_TO_MATERIAL.get(domain) if domain else None
        archetypes = DOMAIN_TO_ARCHETYPE.get(domain, [])
        sister_mode, sister_pair = get_sister_mode(prefix)

        chemistry_note = generate_chemistry_note(domain, prefix, material, middle) if domain else ""

        return ClassifiedEntry(
            token=token,
            folio=entry_data['folio'],
            section=entry_data['section'],
            line_num=entry_data['line_num'],
            line_position=entry_data['line_position'],
            prefix=prefix,
            middle=middle,
            suffix=suffix,
            operational_domain=domain.value if domain else None,
            material_behavior=material.value if material else None,
            sister_mode=sister_mode,
            sister_pair=sister_pair,
            decision_archetypes=[a.value for a in archetypes],
            chemistry_note=chemistry_note,
            is_valid=True,
            parse_status=status
        )
    else:
        return ClassifiedEntry(
            token=token,
            folio=entry_data['folio'],
            section=entry_data['section'],
            line_num=entry_data['line_num'],
            line_position=entry_data['line_position'],
            prefix=None,
            middle=None,
            suffix=None,
            operational_domain=None,
            material_behavior=None,
            sister_mode=None,
            sister_pair=None,
            decision_archetypes=[],
            chemistry_note="No valid prefix - cannot classify behavioral domain",
            is_valid=False,
            parse_status=status
        )


def classify_all_entries() -> List[ClassifiedEntry]:
    """Classify all Currier A entries."""
    raw_entries = load_currier_a()
    print(f"Loaded {len(raw_entries)} Currier A tokens")

    classified = []
    for entry in raw_entries:
        classified.append(classify_entry(entry))

    return classified


# =============================================================================
# ANALYSIS AND STATISTICS
# =============================================================================

def compute_distribution_stats(classified: List[ClassifiedEntry]) -> dict:
    """Compute distribution statistics for classified entries."""
    stats = {
        'total_entries': len(classified),
        'valid_entries': sum(1 for e in classified if e.is_valid),
        'coverage_rate': 0,

        'by_domain': Counter(),
        'by_material': Counter(),
        'by_sister_mode': Counter(),
        'by_prefix': Counter(),
        'by_section': defaultdict(Counter),

        'unique_middles': set(),
        'middle_by_domain': defaultdict(set),
        'domain_by_section': defaultdict(Counter),

        'archetype_distribution': Counter(),
    }

    for entry in classified:
        if not entry.is_valid:
            continue

        stats['by_domain'][entry.operational_domain] += 1
        stats['by_material'][entry.material_behavior] += 1
        stats['by_prefix'][entry.prefix] += 1

        if entry.sister_mode:
            stats['by_sister_mode'][entry.sister_mode] += 1

        if entry.section:
            stats['by_section'][entry.section][entry.operational_domain] += 1
            stats['domain_by_section'][entry.section][entry.operational_domain] += 1

        if entry.middle:
            stats['unique_middles'].add(entry.middle)
            stats['middle_by_domain'][entry.operational_domain].add(entry.middle)

        for archetype in entry.decision_archetypes:
            stats['archetype_distribution'][archetype] += 1

    stats['coverage_rate'] = stats['valid_entries'] / stats['total_entries'] if stats['total_entries'] > 0 else 0
    stats['unique_middle_count'] = len(stats['unique_middles'])

    # Convert sets to counts for JSON serialization
    stats['unique_middles'] = len(stats['unique_middles'])
    stats['middle_by_domain'] = {k: len(v) for k, v in stats['middle_by_domain'].items()}
    stats['domain_by_section'] = {k: dict(v) for k, v in stats['domain_by_section'].items()}
    stats['by_section'] = {k: dict(v) for k, v in stats['by_section'].items()}

    return stats


def generate_behavioral_summary(stats: dict) -> dict:
    """Generate behavioral chemistry summary."""
    total_valid = stats['valid_entries']

    domain_dist = stats['by_domain']

    summary = {
        'headline': "Currier A Behavioral Classification Summary",
        'tier': 3,
        'status': 'SPECULATIVE',

        'coverage': {
            'total_tokens': stats['total_entries'],
            'classified': stats['valid_entries'],
            'rate': round(stats['coverage_rate'] * 100, 1),
        },

        'behavioral_profile': {
            'energy_operations': {
                'count': domain_dist.get('ENERGY_OPERATOR', 0),
                'percent': round(100 * domain_dist.get('ENERGY_OPERATOR', 0) / total_valid, 1) if total_valid > 0 else 0,
                'interpretation': "Operations on phase-sensitive, mobile materials (M-A)",
                'prefixes': ['ch', 'sh', 'qo'],
                'chemistry_note': "In distillation: volatile aromatics, fractionation targets"
            },
            'frequent_operations': {
                'count': domain_dist.get('FREQUENT_OPERATOR', 0),
                'percent': round(100 * domain_dist.get('FREQUENT_OPERATOR', 0) / total_valid, 1) if total_valid > 0 else 0,
                'interpretation': "Operations on uniform mobile materials (M-B)",
                'prefixes': ['ok', 'ot'],
                'chemistry_note': "In distillation: solvents, carriers, wash liquids"
            },
            'control_operations': {
                'count': domain_dist.get('CORE_CONTROL', 0),
                'percent': round(100 * domain_dist.get('CORE_CONTROL', 0) / total_valid, 1) if total_valid > 0 else 0,
                'interpretation': "Class-independent structural anchors",
                'prefixes': ['da', 'ol'],
                'chemistry_note': "Process articulation regardless of material"
            },
            'registry_references': {
                'count': domain_dist.get('REGISTRY_REFERENCE', 0),
                'percent': round(100 * domain_dist.get('REGISTRY_REFERENCE', 0) / total_valid, 1) if total_valid > 0 else 0,
                'interpretation': "References to stable materials (M-C/M-D)",
                'prefixes': ['ct'],
                'chemistry_note': "In distillation: apparatus, containers, stable products"
            },
        },

        'sister_pair_usage': {
            'primary_mode': stats['by_sister_mode'].get('primary', 0),
            'alternate_mode': stats['by_sister_mode'].get('alternate', 0),
            'interpretation': "Sister pairs encode variant selection within same operation type"
        },

        'discrimination_capacity': {
            'unique_middles': stats['unique_middle_count'],
            'middles_by_domain': stats['middle_by_domain'],
            'interpretation': "MIDDLE component differentiates specific referents within operational domain"
        },

        'decision_support': {
            'archetype_coverage': dict(stats['archetype_distribution']),
            'interpretation': "Entry supports these decision judgment calls"
        }
    }

    return summary


# =============================================================================
# OUTPUT
# =============================================================================

def save_results(classified: List[ClassifiedEntry], stats: dict, summary: dict):
    """Save all results."""
    os.makedirs('results', exist_ok=True)

    # Full classified registry
    registry_path = 'results/currier_a_behavioral_registry.json'
    registry_data = [asdict(e) for e in classified]
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2)
    print(f"Saved: {registry_path}")

    # Statistics
    stats_path = 'results/currier_a_behavioral_stats.json'
    # Convert Counter objects for JSON
    json_stats = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in stats.items()}
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(json_stats, f, indent=2)
    print(f"Saved: {stats_path}")

    # Summary
    summary_path = 'results/currier_a_behavioral_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved: {summary_path}")


def main():
    """Main execution."""
    print("=" * 60)
    print("Currier A Behavioral Classification")
    print("=" * 60)

    # Classify all entries
    classified = classify_all_entries()

    # Compute statistics
    stats = compute_distribution_stats(classified)

    # Generate summary
    summary = generate_behavioral_summary(stats)

    # Print quick overview
    print("\n" + "-" * 60)
    print("BEHAVIORAL PROFILE")
    print("-" * 60)

    profile = summary['behavioral_profile']
    for domain_name, domain_data in profile.items():
        print(f"\n{domain_name.upper()}:")
        print(f"  Count: {domain_data['count']} ({domain_data['percent']}%)")
        print(f"  Prefixes: {domain_data['prefixes']}")
        print(f"  Interpretation: {domain_data['interpretation']}")
        print(f"  Chemistry: {domain_data['chemistry_note']}")

    print("\n" + "-" * 60)
    print("DISCRIMINATION CAPACITY")
    print("-" * 60)
    print(f"Unique MIDDLEs: {stats['unique_middle_count']}")
    print(f"MIDDLEs by domain: {stats['middle_by_domain']}")

    print("\n" + "-" * 60)
    print("SISTER PAIR USAGE")
    print("-" * 60)
    print(f"Primary mode (ch, ok): {stats['by_sister_mode'].get('primary', 0)}")
    print(f"Alternate mode (sh, ot): {stats['by_sister_mode'].get('alternate', 0)}")

    # Save
    save_results(classified, stats, summary)

    print("\n" + "=" * 60)
    print("Classification complete!")
    print("=" * 60)

    return summary


if __name__ == '__main__':
    main()
