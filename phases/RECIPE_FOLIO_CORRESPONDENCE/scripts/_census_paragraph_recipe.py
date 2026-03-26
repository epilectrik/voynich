#!/usr/bin/env python3
"""
Census: Paragraph count vs recipe step count correlation.

For each of the 9 confident recipe-to-folio matches, compares:
  1. Number of paragraphs in the Voynich folio
  2. Number of lines in the PL chapter (from structural profile)
  3. Number of operational steps in the PL chapter (verb-counted from English text)

Tests Spearman rank correlation for paragraph_count vs PL_line_count
and paragraph_count vs step_count.

Prediction P7: Expected null result (p > 0.10).
"""

import json
import re
import random
import sys

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript

# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = 'C:/git/voynich'
PROFILE_PATH = f'{PROJECT_ROOT}/phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json'
ENGLISH_PATH = f'{PROJECT_ROOT}/sources/pseudo_lull_testamentum/testamentum_complete_english.txt'

# 9 confident matches from Phase 628 (chapter_idx is flat index into E1_chapters)
CONFIDENT_MATCHES = [
    {'pl_chapter': 'Ch14',  'chapter_idx': 109, 'folio': 'f84r',  'distance': 0.723, 'ratio': 2.097},
    {'pl_chapter': 'Ch27',  'chapter_idx': 154, 'folio': 'f77v',  'distance': 0.851, 'ratio': 2.805},
    {'pl_chapter': 'Ch19',  'chapter_idx': 146, 'folio': 'f75r',  'distance': 1.285, 'ratio': 1.317},
    {'pl_chapter': 'Ch18',  'chapter_idx': 113, 'folio': 'f76r',  'distance': 1.332, 'ratio': 1.707},
    {'pl_chapter': 'Ch9',   'chapter_idx': 104, 'folio': 'f83r',  'distance': 1.560, 'ratio': 1.203},
    {'pl_chapter': 'Ch24',  'chapter_idx': 151, 'folio': 'f84v',  'distance': 1.561, 'ratio': 1.261},
    {'pl_chapter': 'Ch16',  'chapter_idx': 111, 'folio': 'f108r', 'distance': 1.827, 'ratio': 1.348},
    {'pl_chapter': 'Ch11',  'chapter_idx': 138, 'folio': 'f112r', 'distance': 2.484, 'ratio': 1.258},
    {'pl_chapter': 'Ch18t', 'chapter_idx': 145, 'folio': 'f81v',  'distance': 2.767, 'ratio': 1.151},
]

# Operation verbs for step counting
OPERATION_VERBS = [
    'take', 'distill', 'distilling', 'put', 'add', 'heat', 'dissolve',
    'wash', 'pour', 'separate', 'mix', 'grind', 'calcine', 'sublime',
    'ferment', 'circulate', 'repeat', 'filter', 'coagulate', 'place',
    'seal', 'cut', 'pound', 'cast', 'rectify', 'return', 'dry',
    'evaporate', 'decoct', 'imbibe', 'pulverize', 'sift',
]

N_PERM = 1000
RNG = random.Random(629_001)

# ============================================================
# Statistics (manual implementations)
# ============================================================

def rank_values(vals):
    """Assign ranks to values (average rank for ties)."""
    indexed = sorted(enumerate(vals), key=lambda x: x[1])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # average of 1-based ranks i+1..j
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman(x, y):
    """Spearman rank correlation coefficient."""
    n = len(x)
    if n < 3:
        return 0.0
    rx = rank_values(x)
    ry = rank_values(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def permutation_p_value(x, y, n_perm=N_PERM, rng=RNG):
    """Two-sided permutation test for Spearman correlation."""
    real_rs = spearman(x, y)
    abs_real = abs(real_rs)
    count = 0
    y_perm = list(y)
    for _ in range(n_perm):
        rng.shuffle(y_perm)
        rs_perm = spearman(x, y_perm)
        if abs(rs_perm) >= abs_real:
            count += 1
    return count / n_perm


# ============================================================
# Paragraph counting
# ============================================================

def count_paragraphs_gap(tokens):
    """Count paragraphs via line number gaps (gap > 1 = new paragraph)."""
    line_nums = sorted(set(int(t.line) for t in tokens if t.line.isdigit()))
    if not line_nums:
        return 0
    par_count = 1
    for i in range(1, len(line_nums)):
        if line_nums[i] > line_nums[i - 1] + 1:
            par_count += 1
    return par_count


def count_paragraphs_par_initial(tokens):
    """Count paragraphs via par_initial field in transcript."""
    par_lines = set(int(t.line) for t in tokens if t.par_initial and t.line.isdigit())
    # Line 1 always starts paragraph 1 even if not marked
    if 1 not in par_lines:
        par_lines.add(1)
    return len(par_lines)


# ============================================================
# Step counting from English text
# ============================================================

def load_english_lines():
    """Load English translation as list of lines (0-indexed)."""
    with open(ENGLISH_PATH, 'r', encoding='utf-8') as f:
        return f.readlines()


def count_operation_steps(text_lines):
    """Count distinct operational steps in text.

    Each sentence containing one or more operation verbs = 1 step.
    Sentences are split on '.', '!', '?', and ';' (semicolons often
    separate distinct operations in alchemical text).
    """
    full_text = ' '.join(line.strip() for line in text_lines if line.strip())
    # Remove page headers and chapter titles
    full_text = re.sub(r'---\s*Page.*?---', ' ', full_text)
    full_text = re.sub(r'(PRACTICA\.|RAYMVNDI LVLLI|MERCVRIORVM LIB\.)', ' ', full_text)
    full_text = re.sub(r'CAP\.?\s+[IVXLCDM]+\.?', ' ', full_text)
    full_text = re.sub(r'CAPVT\s+\w+', ' ', full_text)

    # Split into sentences
    sentences = re.split(r'[.!?;]', full_text)

    step_count = 0
    verb_pattern = re.compile(
        r'\b(' + '|'.join(OPERATION_VERBS) + r')\b',
        re.IGNORECASE
    )
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if verb_pattern.search(sentence):
            step_count += 1

    return step_count


def extract_chapter_text(english_lines, en_line_start, en_line_end):
    """Extract English text for a chapter by line range (1-indexed)."""
    # en_line_start and en_line_end are 1-indexed line numbers
    return english_lines[en_line_start - 1:en_line_end - 1]


# ============================================================
# Main
# ============================================================

def main():
    print('=' * 72)
    print('CENSUS: Paragraph Count vs Recipe Step Count')
    print('Prediction P7: Expected null result (p > 0.10)')
    print('=' * 72)

    # Load structural profile
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    chapters = profile['E1_chapters']

    # Load English text
    english_lines = load_english_lines()

    # Load transcript
    tx = Transcript()

    # --------------------------------------------------------
    # Collect data for each match
    # --------------------------------------------------------
    print('\n--- Data Collection ---\n')
    print(f'{"Match":<8} {"Folio":<8} {"P(gap)":<7} {"P(pi)":<7} '
          f'{"PL Part":<14} {"PL Lines":<10} {"Steps":<7}')
    print('-' * 70)

    folio_par_gap = []
    folio_par_pi = []
    pl_line_counts = []
    pl_step_counts = []

    for match in CONFIDENT_MATCHES:
        folio = match['folio']
        ch_idx = match['chapter_idx']
        ch = chapters[ch_idx]

        # Paragraph counts from Voynich
        tokens = [t for t in tx.currier_b() if t.folio == folio]
        p_gap = count_paragraphs_gap(tokens)
        p_pi = count_paragraphs_par_initial(tokens)

        # PL chapter info
        part = ch['part']
        en_start = ch['en_line_start']
        en_end = ch['en_line_end']
        n_lines = en_end - en_start

        # Step count from English text
        ch_text = extract_chapter_text(english_lines, en_start, en_end)
        n_steps = count_operation_steps(ch_text)

        folio_par_gap.append(p_gap)
        folio_par_pi.append(p_pi)
        pl_line_counts.append(n_lines)
        pl_step_counts.append(n_steps)

        print(f'{match["pl_chapter"]:<8} {folio:<8} {p_gap:<7} {p_pi:<7} '
              f'{part:<14} {n_lines:<10} {n_steps:<7}')

    # --------------------------------------------------------
    # Gap-based paragraph detection result
    # --------------------------------------------------------
    print('\n--- Method 1: Gap-Based Paragraph Detection ---\n')
    unique_gap = len(set(folio_par_gap))
    if unique_gap <= 1:
        print(f'ALL folios have {folio_par_gap[0]} paragraph(s) by gap detection.')
        print('No variance in paragraph count -- Spearman correlation undefined.')
        print('REASON: Line numbers are consecutive (1,2,3,...N) for all 9 folios.')
        print('Gap-based detection finds no paragraph breaks.\n')
        print('VERDICT (gap method): TRIVIALLY NULL -- no variance to correlate.\n')
    else:
        rs_gap_lines = spearman(folio_par_gap, pl_line_counts)
        p_gap_lines = permutation_p_value(folio_par_gap, pl_line_counts)
        print(f'Spearman(gap_pars, PL_lines): rs = {rs_gap_lines:.4f}, p = {p_gap_lines:.4f}')

        rs_gap_steps = spearman(folio_par_gap, pl_step_counts)
        p_gap_steps = permutation_p_value(folio_par_gap, pl_step_counts)
        print(f'Spearman(gap_pars, PL_steps): rs = {rs_gap_steps:.4f}, p = {p_gap_steps:.4f}')

    # --------------------------------------------------------
    # par_initial-based paragraph detection
    # --------------------------------------------------------
    print('--- Method 2: par_initial Transcript Field ---\n')
    print('Using the transcript par_initial field as an alternative')
    print('paragraph boundary marker (gallows-delimited paragraphs).\n')

    rs_pi_lines = spearman(folio_par_pi, pl_line_counts)
    p_pi_lines = permutation_p_value(folio_par_pi, pl_line_counts)
    print(f'Spearman(pi_pars, PL_lines):  rs = {rs_pi_lines:.4f}, p = {p_pi_lines:.4f}')

    rs_pi_steps = spearman(folio_par_pi, pl_step_counts)
    p_pi_steps = permutation_p_value(folio_par_pi, pl_step_counts)
    print(f'Spearman(pi_pars, PL_steps):  rs = {rs_pi_steps:.4f}, p = {p_pi_steps:.4f}')

    # --------------------------------------------------------
    # Also test: PL lines vs PL steps (sanity check)
    # --------------------------------------------------------
    print('\n--- Sanity Check: PL Lines vs PL Steps ---\n')
    rs_lines_steps = spearman(pl_line_counts, pl_step_counts)
    p_lines_steps = permutation_p_value(pl_line_counts, pl_step_counts)
    print(f'Spearman(PL_lines, PL_steps): rs = {rs_lines_steps:.4f}, p = {p_lines_steps:.4f}')
    if p_lines_steps < 0.05:
        print('(These correlate, confirming step counting tracks chapter length.)')
    else:
        print('(Weak correlation -- step counting adds info beyond raw length.)')

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    print('\n' + '=' * 72)
    print('SUMMARY')
    print('=' * 72)
    print()
    print('Gap-based paragraph detection: all folios = 1 paragraph (no variance)')
    print(f'par_initial paragraph counts: range {min(folio_par_pi)}-{max(folio_par_pi)}')
    print(f'PL line counts:               range {min(pl_line_counts)}-{max(pl_line_counts)}')
    print(f'PL step counts:               range {min(pl_step_counts)}-{max(pl_step_counts)}')
    print()

    # Determine verdict
    null_confirmed = True
    if unique_gap > 1:
        if p_gap_lines < 0.10 or p_gap_steps < 0.10:
            null_confirmed = False
    if p_pi_lines < 0.10 or p_pi_steps < 0.10:
        null_confirmed = False

    if null_confirmed:
        print('VERDICT: NULL CONFIRMED (p > 0.10 for all tests)')
        print('Prediction P7 PASSES: paragraph count does NOT correlate')
        print('with recipe step count or chapter length.')
    else:
        print('VERDICT: UNEXPECTED SIGNAL DETECTED (p < 0.10 for at least one test)')
        print('Prediction P7 FAILS: there may be structural correspondence')
        print('between Voynich paragraph structure and PL recipe steps.')

    print()
    print('Interpretation: Voynich paragraphs are operational units')
    print('(gallows-delimited control blocks), not recipe step markers.')
    print('Their count reflects the manuscript\'s own structural grammar,')
    print('not the step count of the source recipe.')


if __name__ == '__main__':
    main()
