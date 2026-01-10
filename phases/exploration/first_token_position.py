#!/usr/bin/env python
"""
Phase 3: Folio Organization Analysis

Research question Q2: Do "inverted prefix" patterns correlate with folio structure?
Research question Q3: Is first-token position syntactically special in A?

Tests:
- Section distribution of prefix types
- Quire alignment
- Adjacent folio patterns
- Compare first-token vocabulary to general A vocabulary

Decision threshold: chi-square p < 0.05 indicates section-conditioning
"""
import sys
import json
from collections import Counter, defaultdict
from typing import List, Dict
import re
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader


# =============================================================================
# FOLIO METADATA
# =============================================================================

# Voynich manuscript section boundaries (Currier's divisions)
# Based on standard folio ranges
SECTION_MAP = {
    # Herbal A (1-66)
    **{f'{i}{s}': 'H' for i in range(1, 26) for s in ['r', 'v']},
    # Note: This is simplified - full section mapping would come from codicology
}

# Quire boundaries (standard Voynich quire structure)
QUIRE_MAP = {
    # Quire 1: f1-f8
    **{f'{i}{s}': 'Q1' for i in range(1, 9) for s in ['r', 'v']},
    # Quire 2: f9-f16
    **{f'{i}{s}': 'Q2' for i in range(9, 17) for s in ['r', 'v']},
    # Quire 3: f17-f24
    **{f'{i}{s}': 'Q3' for i in range(17, 25) for s in ['r', 'v']},
    # Quire 4: f25+
    **{f'{i}{s}': 'Q4' for i in range(25, 30) for s in ['r', 'v']},
}


def get_folio_section(folio_id: str) -> str:
    """Get section for folio."""
    return SECTION_MAP.get(folio_id, 'UNKNOWN')


def get_folio_quire(folio_id: str) -> str:
    """Get quire for folio."""
    return QUIRE_MAP.get(folio_id, 'UNKNOWN')


# =============================================================================
# VOCABULARY ANALYSIS
# =============================================================================

def get_general_a_vocabulary() -> Dict[str, int]:
    """
    Get full vocabulary from A folios (all tokens, all positions).
    Returns frequency dict.
    """
    loader = TranscriptionLoader()
    loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]
    vocab = Counter()

    for folio_id in a_folios:
        folio = loader.get_folio(folio_id)
        if not folio or not folio.lines:
            continue

        for line in folio.lines:
            tokens = re.split(r'[\.\s]+', line.text)
            tokens = [t.lower() for t in tokens if t]
            vocab.update(tokens)

    return dict(vocab)


def get_second_token_distribution() -> List[Dict]:
    """
    Get distribution of SECOND tokens (position 2 in line 1).
    Compare to first tokens to test position-specificity.
    """
    loader = TranscriptionLoader()
    loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]
    second_tokens = []

    for folio_id in a_folios:
        folio = loader.get_folio(folio_id)
        if not folio or not folio.lines:
            continue

        first_line = folio.lines[0]
        tokens = re.split(r'[\.\s]+', first_line.text)
        tokens = [t for t in tokens if t]

        if len(tokens) >= 2:
            token = tokens[1]
            prefix_2char = token[:2].lower() if len(token) >= 2 else token.lower()
            second_tokens.append({
                'folio_id': folio_id,
                'token': token,
                'prefix_2char': prefix_2char,
            })

    return second_tokens


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_position_analysis():
    """Run full Phase 3 analysis."""

    print("=" * 70)
    print("PHASE 3: Folio Organization Analysis")
    print("=" * 70)

    # Load Phase 1 data
    with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
        phase1_data = json.load(f)

    records = phase1_data['records']

    print(f"\n### Section Distribution ###")

    # Categorize by pass/fail and section
    pass_by_section = defaultdict(list)
    fail_by_section = defaultdict(list)
    prefix_by_section = defaultdict(lambda: defaultdict(int))

    for r in records:
        section = get_folio_section(r['folio_id'])
        quire = get_folio_quire(r['folio_id'])

        if r['is_pass']:
            pass_by_section[section].append(r)
        else:
            fail_by_section[section].append(r)

        prefix_by_section[section][r['prefix_2char']] += 1

    # Section summary
    for section in sorted(set(SECTION_MAP.values())):
        pass_count = len(pass_by_section[section])
        fail_count = len(fail_by_section[section])
        total = pass_count + fail_count
        if total > 0:
            print(f"\nSection {section}:")
            print(f"  Total: {total}, Pass: {pass_count}, Fail: {fail_count}")
            print(f"  Fail rate: {100*fail_count/total:.1f}%")
            print(f"  Top prefixes: ", end="")
            top = sorted(prefix_by_section[section].items(), key=lambda x: -x[1])[:5]
            print(", ".join(f"{p}:{c}" for p, c in top))

    print(f"\n### Quire Distribution ###")

    # Categorize by quire
    pass_by_quire = defaultdict(list)
    fail_by_quire = defaultdict(list)
    prefix_by_quire = defaultdict(lambda: defaultdict(int))

    for r in records:
        quire = get_folio_quire(r['folio_id'])

        if r['is_pass']:
            pass_by_quire[quire].append(r)
        else:
            fail_by_quire[quire].append(r)

        prefix_by_quire[quire][r['prefix_2char']] += 1

    for quire in ['Q1', 'Q2', 'Q3', 'Q4']:
        pass_count = len(pass_by_quire[quire])
        fail_count = len(fail_by_quire[quire])
        total = pass_count + fail_count
        if total > 0:
            print(f"\n{quire}:")
            print(f"  Total: {total}, Pass: {pass_count}, Fail: {fail_count}")
            print(f"  Fail rate: {100*fail_count/total:.1f}%")
            print(f"  Top prefixes: ", end="")
            top = sorted(prefix_by_quire[quire].items(), key=lambda x: -x[1])[:5]
            print(", ".join(f"{p}:{c}" for p, c in top))

    # Chi-square test for quire independence
    print(f"\n### Statistical Tests ###")

    # Build contingency table: quires x pass/fail
    quires = ['Q1', 'Q2', 'Q3', 'Q4']
    observed = []
    for quire in quires:
        pass_count = len(pass_by_quire[quire])
        fail_count = len(fail_by_quire[quire])
        if pass_count + fail_count > 0:
            observed.append([pass_count, fail_count])

    if len(observed) >= 2:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square (quire x pass/fail):")
        print(f"  chi2 = {chi2:.3f}, p = {p_value:.4f}, dof = {dof}")
        if p_value < 0.05:
            print(f"  --> SIGNIFICANT: First-token pass/fail is quire-conditioned")
        else:
            print(f"  --> NOT SIGNIFICANT: First-token pass/fail is quire-independent")

    print(f"\n### Position Comparison: First vs Second Token ###")

    # Compare first-token prefixes to second-token prefixes
    second_tokens = get_second_token_distribution()

    first_prefixes = Counter(r['prefix_2char'] for r in records)
    second_prefixes = Counter(t['prefix_2char'] for t in second_tokens)

    print(f"\nFirst-token prefixes (top 5):")
    for prefix, count in first_prefixes.most_common(5):
        pct = 100 * count / len(records)
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    print(f"\nSecond-token prefixes (top 5):")
    for prefix, count in second_prefixes.most_common(5):
        pct = 100 * count / len(second_tokens)
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    # Jaccard of prefix vocabularies
    first_prefix_set = set(first_prefixes.keys())
    second_prefix_set = set(second_prefixes.keys())
    position_jaccard = len(first_prefix_set & second_prefix_set) / len(first_prefix_set | second_prefix_set)

    print(f"\nPrefix vocabulary Jaccard (1st vs 2nd): {position_jaccard:.3f}")
    print(f"First-only prefixes: {sorted(first_prefix_set - second_prefix_set)}")
    print(f"Second-only prefixes (sample): {sorted(list(second_prefix_set - first_prefix_set)[:10])}")

    # Calculate C+vowel proportion for each position
    c_vowel_prefixes = {'ko', 'po', 'to', 'fo', 'ka', 'ta', 'pa', 'fa'}

    first_c_vowel = sum(first_prefixes.get(p, 0) for p in c_vowel_prefixes)
    first_c_vowel_pct = 100 * first_c_vowel / len(records)

    second_c_vowel = sum(second_prefixes.get(p, 0) for p in c_vowel_prefixes)
    second_c_vowel_pct = 100 * second_c_vowel / len(second_tokens) if second_tokens else 0

    print(f"\nC+vowel prefix proportion:")
    print(f"  First position:  {first_c_vowel}/{len(records)} ({first_c_vowel_pct:.1f}%)")
    print(f"  Second position: {second_c_vowel}/{len(second_tokens)} ({second_c_vowel_pct:.1f}%)")

    # Fisher exact test for position x C+vowel
    # Contingency: [[first_cvowel, first_other], [second_cvowel, second_other]]
    first_other = len(records) - first_c_vowel
    second_other = len(second_tokens) - second_c_vowel

    contingency = [[first_c_vowel, first_other], [second_c_vowel, second_other]]
    odds_ratio, fisher_p = stats.fisher_exact(contingency)

    print(f"\nFisher exact (position x C+vowel):")
    print(f"  odds_ratio = {odds_ratio:.2f}, p = {fisher_p:.4f}")
    if fisher_p < 0.05:
        print(f"  --> SIGNIFICANT: C+vowel prefixes are position-specific")
    else:
        print(f"  --> NOT SIGNIFICANT: C+vowel prefixes are position-independent")

    print(f"\n### Adjacent Folio Patterns ###")

    # Check if adjacent folios share prefix patterns
    folio_to_prefix = {r['folio_id']: r['prefix_2char'] for r in records}

    adjacent_match = 0
    adjacent_total = 0

    for i in range(1, 25):  # 1-24
        for s1, s2 in [('r', 'v'), ('v', 'r')]:
            f1 = f'{i}{s1}'
            if s2 == 'r':
                f2 = f'{i+1}r' if s1 == 'v' else f'{i}v'
            else:
                f2 = f'{i}v'

            if f1 in folio_to_prefix and f2 in folio_to_prefix:
                adjacent_total += 1
                if folio_to_prefix[f1] == folio_to_prefix[f2]:
                    adjacent_match += 1

    if adjacent_total > 0:
        print(f"Adjacent folio prefix matches: {adjacent_match}/{adjacent_total} ({100*adjacent_match/adjacent_total:.1f}%)")
        # Random expectation: 1/n where n = number of unique prefixes
        n_prefixes = len(set(folio_to_prefix.values()))
        expected = 100 / n_prefixes
        print(f"Random expectation: {expected:.1f}%")

    # Summary
    print(f"\n{'=' * 70}")
    print("PHASE 3 SUMMARY")
    print(f"{'=' * 70}")

    # Determine findings
    findings = []

    if len(observed) >= 2 and p_value >= 0.05:
        findings.append("Quire-independent: Pass/fail not conditioned on quire")

    if fisher_p < 0.05:
        findings.append(f"Position-specific: C+vowel prefixes enriched {odds_ratio:.1f}x in first position")
    else:
        findings.append("Position-independent: C+vowel distribution similar across positions")

    for f in findings:
        print(f"- {f}")

    # Decision
    if fisher_p < 0.05:
        decision = "POSITION_SPECIFIC"
        print(f"\nDECISION: {decision}")
        print("First-token position in Currier A shows distinct prefix vocabulary.")
        print("C+vowel prefixes (ko-, po-, to-) are concentrated at folio-initial.")
        print("This may represent a 'header' or 'register marker' convention.")
    else:
        decision = "POSITION_FREE"
        print(f"\nDECISION: {decision}")
        print("First-token position does not show special syntax.")
        print("C234 (POSITION_FREE) remains valid without exception.")

    # Save results
    results = {
        'phase': 'first_token_position',
        'quire_chi2_p': p_value if len(observed) >= 2 else None,
        'fisher_p': fisher_p,
        'odds_ratio': odds_ratio,
        'first_c_vowel_pct': first_c_vowel_pct,
        'second_c_vowel_pct': second_c_vowel_pct,
        'position_jaccard': position_jaccard,
        'decision': decision,
        'findings': findings,
    }

    with open('C:/git/voynich/phases/exploration/first_token_position_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: phases/exploration/first_token_position_results.json")

    return results


if __name__ == '__main__':
    run_position_analysis()
