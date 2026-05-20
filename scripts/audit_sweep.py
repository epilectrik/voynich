"""
Audit-sweep triage tool — applies three diagnostic patterns from session
2026-05-19 audit findings (C131, C475, C1068) to flag suspicious constraints
for manual audit.

Pattern definitions (from session methodology memories):

  1. INVENTED-THRESHOLD (C131 pattern):
     - Constraint cites a specific numerical threshold for falsification
     - Threshold is not cited from external source (NL baseline, validated
       reference)
     - Pre-v2.42 era (transcriber-filter bug fix at 2026-01-16, roughly
       C-number < 500)
     Memory: feedback_made_up_threshold_audit.md

  2. SPARSITY-DENOMINATOR (C475 pattern):
     - Constraint cites "X% of [possible/total] pairs/triples forbidden"
     - On a sparse graph (vocabulary V > 100, attested pairs << V*(V-1)/2)
     - Headline % uses N_possible denominator, not N_attested
     Memory: feedback_denominator_choice_sparse_cooccurrence.md

  3. CHI²-VS-PERMNULL (C1068 pattern):
     - Cross-layer/coupling claim with chi² statistic
     - perm_null_p reported with p > 0.05 (constraint registered despite
       failing proper null)
     - OR chi² without perm_null companion (audit-pending)
     Memory: feedback_chi2_vs_permutation_null_mismatch.md

Usage:
  python scripts/audit_sweep.py
  python scripts/audit_sweep.py --pattern sparsity  # filter to one pattern
  python scripts/audit_sweep.py --min-score 2       # show only multi-signal

Output: ranked triage report. NOT an auto-audit — flags candidates for
manual review.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
CONSTRAINT_TABLE = ROOT / 'context' / 'CONSTRAINT_TABLE.txt'
INDEX_MD = ROOT / 'context' / 'CLAIMS' / 'INDEX.md'

# Roughly the C-number range when pre-v2.42 transcriber filter bug was active.
# v2.42 was committed 2026-01-16. By that point the constraint count was
# around C500. So C-numbers < 500 are higher suspicion for filter-bug-era.
PRE_V242_CUTOFF = 500

# Crazy-expert's targeted high-suspicion list from C475+C1068 audits
TARGETED_LIST = {153, 268, 476, 481, 517, 518, 982, 983, 996}
# Plus pre-PHASE_700 cross-layer / coupling space (C660-C1100)
TARGETED_RANGE = range(660, 1101)


# ===================================================================
# PARSE CONSTRAINT TABLE
# ===================================================================

def load_constraints():
    """Returns list of dicts: {num, text_table, tier, scope, location}."""
    constraints = []
    with open(CONSTRAINT_TABLE, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or not line.startswith('C'):
                continue
            parts = line.split('\t')
            if len(parts) < 5:
                continue
            num_str = parts[0]
            m = re.match(r'C(\d+)', num_str)
            if not m:
                continue
            num = int(m.group(1))
            constraints.append({
                'num': num,
                'id': num_str,
                'text_table': parts[1],
                'tier': parts[2],
                'scope': parts[3],
                'location': parts[4],
            })
    return constraints


def load_index_descriptions():
    """Returns dict {C_num: full_index_text} for constraints with rows in INDEX.md."""
    index_text = INDEX_MD.read_text(encoding='utf-8')
    desc = {}
    # Match lines like "| 475 | ... | tier | scope | ... |" or "| **475** | ... |"
    # Allow the number to be bold or not, with or without ~~retraction markers~~
    pattern = re.compile(r'^\|\s*(?:~~)?(?:\*\*)?(\d+)(?:\*\*)?(?:~~)?\s*\|', re.MULTILINE)
    for line in index_text.split('\n'):
        m = pattern.match(line)
        if m:
            num = int(m.group(1))
            desc[num] = line
    return desc


# ===================================================================
# DIAGNOSTIC PATTERNS
# ===================================================================

# Patterns are tuples of (signal_name, regex, description)

# Pattern 1: invented threshold
THRESHOLD_PATTERNS = [
    ('explicit_threshold', re.compile(r'threshold\s*[><=]\s*[0-9]', re.I),
     'explicit numerical threshold cited'),
    ('threshold_above', re.compile(r'(above|below|more than|less than)\s*[0-9]+\s*%', re.I),
     'absolute % threshold for falsification'),
    ('contradicts_threshold', re.compile(r'\bLOW\b.*[0-9]+\s*%|<\s*[0-9]+\s*%.*threshold', re.I),
     'claims "LOW/HIGH" against a numeric threshold'),
]

# Pattern 2: sparsity denominator
SPARSITY_PATTERNS = [
    ('pct_of_possible', re.compile(r'[0-9]+\.?[0-9]*\s*%\s*(?:of|are)\s*(?:possible|total)\s*(pairs|combinations|triples)', re.I),
     'cites % of "possible" or "total" pairs/triples'),
    ('illegal_forbidden_pct', re.compile(r'([0-9]+\.?[0-9]*)\s*%\s*(?:are\s*)?(?:statistically\s*)?(?:illegal|forbidden|incompatible)', re.I),
     'cites X% illegal/forbidden/incompatible'),
    ('pair_counts_huge', re.compile(r'[0-9]{3,}\s*pairs?', re.I),
     'cites pair counts in hundreds/thousands (potential sparsity)'),
]

# Pattern 3: chi² vs perm-null
CHI2_PATTERNS = [
    ('chi2_huge', re.compile(r'(?:chi[²2]|χ²|x²)\s*=\s*[0-9]+|p\s*=?\s*[0-9.]*e-[0-9]{2,}', re.I),
     'cites chi² with extreme p-value'),
    ('perm_null_marginal', re.compile(r'perm[_\s]?(?:null[_\s])?p\s*=\s*0\.(?:1[3-9]|[2-9])', re.I),
     'perm_null_p > 0.13 (registered despite marginal perm null)'),
    ('nmi_cited', re.compile(r'\bNMI\s*=\s*0\.[0-9]', re.I),
     'cites NMI (cross-layer coupling)'),
]


def score_constraint(c, full_text):
    """Score a constraint against the three patterns. Returns dict of signals fired."""
    text = (c['text_table'] + ' ' + full_text).lower()
    text_orig = c['text_table'] + ' ' + full_text  # preserve case for some regexes

    signals = {
        'pattern_1_threshold': [],
        'pattern_2_sparsity': [],
        'pattern_3_chi2': [],
    }

    # Pattern 1
    for name, regex, desc in THRESHOLD_PATTERNS:
        m = regex.search(text_orig)
        if m:
            signals['pattern_1_threshold'].append((name, m.group(0)))

    # Pattern 2
    for name, regex, desc in SPARSITY_PATTERNS:
        m = regex.search(text_orig)
        if m:
            signals['pattern_2_sparsity'].append((name, m.group(0)))

    # Pattern 3
    for name, regex, desc in CHI2_PATTERNS:
        m = regex.search(text_orig)
        if m:
            signals['pattern_3_chi2'].append((name, m.group(0)))

    # Special: chi² cited but no perm null - audit pending
    if signals['pattern_3_chi2']:
        has_chi2 = any(n == 'chi2_huge' for n, _ in signals['pattern_3_chi2'])
        has_perm = bool(re.search(r'perm', text_orig, re.I))
        if has_chi2 and not has_perm:
            signals['pattern_3_chi2'].append(('chi2_without_perm_companion',
                                              'chi² cited but no permutation null mentioned'))

    # Already-acted constraints get a "skip" signal
    is_retracted_or_demoted = bool(re.search(r'RETRACTED|DEMOTED', text_orig, re.I))
    signals['already_acted'] = is_retracted_or_demoted

    # Already-audit-pending constraints get the flag
    is_audit_pending = bool(re.search(r'AUDIT[_\s]PENDING', text_orig, re.I))
    signals['audit_pending'] = is_audit_pending

    return signals


def suspicion_score(c, signals):
    """Composite suspicion score (0-3) for ranking. Higher = more suspicious."""
    if signals['already_acted']:
        return -1  # Skip
    score = 0
    if signals['pattern_1_threshold']:
        score += 1
    if signals['pattern_2_sparsity']:
        score += 1
    if signals['pattern_3_chi2']:
        score += 1
    # Bonus for being in targeted list
    if c['num'] in TARGETED_LIST:
        score += 1
    return score


# ===================================================================
# MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description='Audit-sweep triage tool')
    parser.add_argument('--pattern', choices=['threshold', 'sparsity', 'chi2', 'all'],
                       default='all', help='Filter to specific pattern')
    parser.add_argument('--min-score', type=int, default=1,
                       help='Minimum suspicion score (default 1)')
    parser.add_argument('--top', type=int, default=50,
                       help='Show top N candidates (default 50)')
    parser.add_argument('--targeted-only', action='store_true',
                       help='Show only crazy-expert targeted list (C153, C268, ...)')
    args = parser.parse_args()

    print("=" * 80)
    print("AUDIT-SWEEP TRIAGE")
    print("=" * 80)
    print(f"\nDiagnostic patterns (from 2026-05-19 audit findings):")
    print(f"  1. INVENTED-THRESHOLD (C131): explicit numerical threshold for falsification")
    print(f"  2. SPARSITY-DENOMINATOR (C475): X% of possible pairs forbidden")
    print(f"  3. CHI²-VS-PERMNULL (C1068): chi² cited, perm-null marginal or absent")

    constraints = load_constraints()
    descriptions = load_index_descriptions()
    print(f"\nLoaded {len(constraints)} constraints from CONSTRAINT_TABLE.txt")
    print(f"Loaded {len(descriptions)} INDEX.md row descriptions for cross-reference")

    # Score all constraints
    candidates = []
    skipped = 0
    for c in constraints:
        full_text = descriptions.get(c['num'], '')
        signals = score_constraint(c, full_text)
        score = suspicion_score(c, signals)
        if score < 0:
            skipped += 1
            continue
        if score < args.min_score:
            continue
        # Pattern filter
        if args.pattern == 'threshold' and not signals['pattern_1_threshold']:
            continue
        if args.pattern == 'sparsity' and not signals['pattern_2_sparsity']:
            continue
        if args.pattern == 'chi2' and not signals['pattern_3_chi2']:
            continue
        # Targeted filter
        if args.targeted_only and c['num'] not in TARGETED_LIST:
            continue
        candidates.append({
            'constraint': c,
            'signals': signals,
            'score': score,
            'in_targeted_list': c['num'] in TARGETED_LIST,
            'pre_v242': c['num'] < PRE_V242_CUTOFF,
        })

    # Rank by score, then by C-number for stable ordering
    candidates.sort(key=lambda x: (-x['score'], x['constraint']['num']))

    print(f"\nSkipped {skipped} already-retracted/demoted constraints")
    print(f"Found {len(candidates)} candidates matching filters")
    print()

    # Display
    if not candidates:
        print("No candidates match the filters.")
        return

    print("=" * 80)
    print(f"TOP {min(args.top, len(candidates))} TRIAGE CANDIDATES")
    print("=" * 80)

    for i, cand in enumerate(candidates[:args.top]):
        c = cand['constraint']
        s = cand['signals']
        print(f"\n[{i+1}] {c['id']} (Tier {c['tier']}, Scope {c['scope']}) — score {cand['score']}")
        marker = ''
        if cand['in_targeted_list']:
            marker += ' [TARGETED-LIST]'
        if cand['pre_v242']:
            marker += ' [pre-v2.42 era]'
        if s['audit_pending']:
            marker += ' [AUDIT-PENDING]'
        if marker:
            print(f"    Flags:{marker}")
        text = c['text_table']
        if len(text) > 200:
            text = text[:200] + '...'
        print(f"    Text: {text}")
        if s['pattern_1_threshold']:
            print(f"    P1 INVENTED-THRESHOLD signals:")
            for name, match in s['pattern_1_threshold']:
                print(f"      - {name}: {match[:100]!r}")
        if s['pattern_2_sparsity']:
            print(f"    P2 SPARSITY-DENOMINATOR signals:")
            for name, match in s['pattern_2_sparsity']:
                print(f"      - {name}: {match[:100]!r}")
        if s['pattern_3_chi2']:
            print(f"    P3 CHI²-VS-PERMNULL signals:")
            for name, match in s['pattern_3_chi2']:
                print(f"      - {name}: {match[:100]!r}")

    # Summary by pattern
    print("\n" + "=" * 80)
    print("PATTERN BREAKDOWN (across all candidates)")
    print("=" * 80)
    n_p1 = sum(1 for c in candidates if c['signals']['pattern_1_threshold'])
    n_p2 = sum(1 for c in candidates if c['signals']['pattern_2_sparsity'])
    n_p3 = sum(1 for c in candidates if c['signals']['pattern_3_chi2'])
    n_targeted = sum(1 for c in candidates if c['in_targeted_list'])
    n_pre_v242 = sum(1 for c in candidates if c['pre_v242'])
    print(f"  Pattern 1 (invented-threshold) flagged: {n_p1}")
    print(f"  Pattern 2 (sparsity-denominator) flagged: {n_p2}")
    print(f"  Pattern 3 (chi²-vs-perm-null) flagged: {n_p3}")
    print(f"  In targeted list: {n_targeted}")
    print(f"  Pre-v2.42 era (C# < 500): {n_pre_v242}")
    print(f"  Total candidates: {len(candidates)}")

    # Suggest top-3 for next manual audit
    print("\n" + "=" * 80)
    print("RECOMMENDED NEXT MANUAL AUDIT TARGETS")
    print("=" * 80)
    print(f"\nTop 3 candidates by composite score (excluding already-acted):")
    for i, cand in enumerate(candidates[:3]):
        c = cand['constraint']
        print(f"  {i+1}. {c['id']} (score {cand['score']}) — {c['text_table'][:120]}")

    print("\nUsage notes:")
    print("  - This script TRIAGES; it does not auto-audit")
    print("  - High-suspicion = candidate for manual run, not automatic action")
    print("  - Re-run after each audit; constraint table updates with retractions/demotions")
    print("  - To filter to specific patterns: --pattern {threshold,sparsity,chi2}")
    print("  - To see crazy-expert's targeted list: --targeted-only")


if __name__ == '__main__':
    main()
