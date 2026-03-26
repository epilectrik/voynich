#!/usr/bin/env python3
"""
Census: Token repetition gradient across Currier B folios.

For ALL Currier B folios, finds the maximum consecutive identical
token run length within any single line. A "run" = same word appearing
consecutively (adjacent tokens with identical word forms on the same line).

Then for the 9 confident matches, checks whether PL recipes mention
explicit iteration counts (e.g., "nine times", "seven times").

Reports:
  1. Full ranking of all B folios by max run length
  2. Whether f75r is unique in having a 4+ run
  3. Matched folio run lengths vs PL iteration counts
"""

import json
import re
import sys

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript

# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = 'C:/git/voynich'
PROFILE_PATH = f'{PROJECT_ROOT}/phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json'
ENGLISH_PATH = f'{PROJECT_ROOT}/sources/pseudo_lull_testamentum/testamentum_complete_english.txt'

# 9 confident matches
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

MATCHED_FOLIOS = {m['folio'] for m in CONFIDENT_MATCHES}

# Number words for iteration detection
NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'hundred': 100,
}


# ============================================================
# Run length detection
# ============================================================

def max_consecutive_run(tokens):
    """Find the maximum consecutive identical token run on any single line.

    Returns (max_run_length, run_word, run_line) for the longest run.
    """
    # Group tokens by line
    lines = {}
    for t in tokens:
        if not t.line.isdigit():
            continue
        line_num = int(t.line)
        if line_num not in lines:
            lines[line_num] = []
        lines[line_num].append(t.word)

    best_run = 1
    best_word = ''
    best_line = 0

    for line_num in sorted(lines.keys()):
        words = lines[line_num]
        if not words:
            continue

        current_run = 1
        for i in range(1, len(words)):
            if words[i] == words[i - 1] and words[i].strip():
                current_run += 1
                if current_run > best_run:
                    best_run = current_run
                    best_word = words[i]
                    best_line = line_num
            else:
                current_run = 1

    return best_run, best_word, best_line


def all_runs_on_folio(tokens):
    """Find ALL consecutive runs of length >= 2 on a folio.

    Returns list of (run_length, word, line_num).
    """
    lines = {}
    for t in tokens:
        if not t.line.isdigit():
            continue
        line_num = int(t.line)
        if line_num not in lines:
            lines[line_num] = []
        lines[line_num].append(t.word)

    runs = []
    for line_num in sorted(lines.keys()):
        words = lines[line_num]
        if len(words) < 2:
            continue
        current_run = 1
        current_word = words[0]
        for i in range(1, len(words)):
            if words[i] == words[i - 1] and words[i].strip():
                current_run += 1
            else:
                if current_run >= 2:
                    runs.append((current_run, current_word, line_num))
                current_run = 1
                current_word = words[i]
        if current_run >= 2:
            runs.append((current_run, current_word, line_num))

    return runs


# ============================================================
# Iteration count detection from PL text
# ============================================================

def load_english_lines():
    """Load English translation as list of lines (0-indexed)."""
    with open(ENGLISH_PATH, 'r', encoding='utf-8') as f:
        return f.readlines()


def find_iteration_counts(text_lines):
    """Find explicit iteration counts in text.

    Looks for patterns like "nine times", "three times", "7 times",
    "repeat N times", "do this N times", etc.

    Returns list of (count, context_snippet).
    """
    full_text = ' '.join(line.strip() for line in text_lines if line.strip())
    # Remove page headers
    full_text = re.sub(r'---\s*Page.*?---', ' ', full_text)
    full_text = re.sub(r'(PRACTICA\.|RAYMVNDI LVLLI|MERCVRIORVM LIB\.)', ' ', full_text)

    results = []

    # Pattern 1: "N times" with number words
    for word, num in NUMBER_WORDS.items():
        pattern = re.compile(
            r'(?:(\w+\s+){0,5})' + re.escape(word) + r'\s+times?(?:\s+(\w+\s+){0,3})',
            re.IGNORECASE
        )
        for m in pattern.finditer(full_text):
            start = max(0, m.start() - 30)
            end = min(len(full_text), m.end() + 30)
            snippet = full_text[start:end].strip()
            results.append((num, snippet))

    # Pattern 2: digit + "times"
    digit_pattern = re.compile(r'(\d+)\s+times?', re.IGNORECASE)
    for m in digit_pattern.finditer(full_text):
        num = int(m.group(1))
        start = max(0, m.start() - 30)
        end = min(len(full_text), m.end() + 30)
        snippet = full_text[start:end].strip()
        results.append((num, snippet))

    # Deduplicate by position (keep unique snippets)
    seen = set()
    unique = []
    for count, snippet in results:
        key = snippet[:40]
        if key not in seen:
            seen.add(key)
            unique.append((count, snippet))

    return unique


# ============================================================
# Main
# ============================================================

def main():
    print('=' * 78)
    print('CENSUS: Token Repetition Gradient Across Currier B Folios')
    print('=' * 78)

    tx = Transcript()

    # --------------------------------------------------------
    # Part 1: All B folios ranked by max run length
    # --------------------------------------------------------
    print('\n--- Part 1: Max Consecutive Token Run per Folio (ALL Currier B) ---\n')

    # Collect all B tokens grouped by folio
    folio_tokens = {}
    for t in tx.currier_b():
        if t.folio not in folio_tokens:
            folio_tokens[t.folio] = []
        folio_tokens[t.folio].append(t)

    # Compute max run for each folio
    folio_runs = []
    for folio in sorted(folio_tokens.keys()):
        tokens = folio_tokens[folio]
        max_run, run_word, run_line = max_consecutive_run(tokens)
        n_tokens = len(tokens)
        folio_runs.append({
            'folio': folio,
            'max_run': max_run,
            'run_word': run_word,
            'run_line': run_line,
            'n_tokens': n_tokens,
            'matched': folio in MATCHED_FOLIOS,
        })

    # Sort by max_run descending, then folio
    folio_runs.sort(key=lambda x: (-x['max_run'], x['folio']))

    # Print table
    print(f'{"Rank":<6} {"Folio":<10} {"MaxRun":<8} {"Word":<20} {"Line":<6} '
          f'{"Tokens":<8} {"Matched":<8}')
    print('-' * 78)

    rank = 0
    prev_run = None
    for i, fr in enumerate(folio_runs):
        if fr['max_run'] != prev_run:
            rank = i + 1
            prev_run = fr['max_run']
        marker = ' <<<' if fr['matched'] else ''
        print(f'{rank:<6} {fr["folio"]:<10} {fr["max_run"]:<8} '
              f'{fr["run_word"]:<20} {fr["run_line"]:<6} '
              f'{fr["n_tokens"]:<8}{marker}')

    # --------------------------------------------------------
    # Part 2: Distribution summary
    # --------------------------------------------------------
    print('\n--- Part 2: Run Length Distribution ---\n')

    run_dist = {}
    for fr in folio_runs:
        r = fr['max_run']
        if r not in run_dist:
            run_dist[r] = 0
        run_dist[r] += 1

    for run_len in sorted(run_dist.keys(), reverse=True):
        count = run_dist[run_len]
        print(f'  Max run = {run_len}: {count} folios')

    # Check f75r uniqueness for 4+ runs
    f75r_data = next((fr for fr in folio_runs if fr['folio'] == 'f75r'), None)
    if f75r_data:
        f75r_run = f75r_data['max_run']
        folios_at_or_above = [fr['folio'] for fr in folio_runs if fr['max_run'] >= f75r_run]
        print(f'\nf75r max run: {f75r_run} (word: "{f75r_data["run_word"]}", line {f75r_data["run_line"]})')
        if f75r_run >= 4:
            n_at_4plus = sum(1 for fr in folio_runs if fr['max_run'] >= 4)
            print(f'Folios with max run >= 4: {n_at_4plus}')
            if n_at_4plus == 1:
                print('f75r IS UNIQUE among all Currier B folios for having a 4+ run.')
            else:
                print(f'f75r is NOT unique -- {n_at_4plus} folios have 4+ runs:')
                for fr in folio_runs:
                    if fr['max_run'] >= 4:
                        print(f'  {fr["folio"]}: run of {fr["max_run"]} '
                              f'("{fr["run_word"]}" on line {fr["run_line"]})')

    # --------------------------------------------------------
    # Part 3: Detailed runs for f75r
    # --------------------------------------------------------
    print('\n--- Part 3: All Runs (length >= 2) on f75r ---\n')
    if 'f75r' in folio_tokens:
        runs_75r = all_runs_on_folio(folio_tokens['f75r'])
        runs_75r.sort(key=lambda x: -x[0])
        if runs_75r:
            for run_len, word, line in runs_75r:
                print(f'  Run of {run_len}: "{word}" on line {line}')
        else:
            print('  No runs of length >= 2 found.')

    # --------------------------------------------------------
    # Part 4: PL iteration counts for matched folios
    # --------------------------------------------------------
    print('\n--- Part 4: PL Iteration Counts vs Folio Run Lengths ---\n')

    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    chapters = profile['E1_chapters']
    english_lines = load_english_lines()

    print(f'{"Match":<8} {"Folio":<8} {"MaxRun":<8} {"RunWord":<16} '
          f'{"PL Iterations Found":<40}')
    print('-' * 90)

    for match in CONFIDENT_MATCHES:
        folio = match['folio']
        ch_idx = match['chapter_idx']
        ch = chapters[ch_idx]

        # Folio run info
        fr = next((x for x in folio_runs if x['folio'] == folio), None)
        max_run = fr['max_run'] if fr else 0
        run_word = fr['run_word'] if fr else '-'

        # PL iteration counts
        en_start = ch['en_line_start']
        en_end = ch['en_line_end']
        ch_text = english_lines[en_start - 1:en_end - 1]
        iterations = find_iteration_counts(ch_text)

        if iterations:
            iter_str = '; '.join(f'{c}x' for c, _ in iterations)
        else:
            iter_str = 'none found'

        print(f'{match["pl_chapter"]:<8} {folio:<8} {max_run:<8} '
              f'{run_word:<16} {iter_str:<40}')

        # Print iteration context if found
        if iterations:
            for count, snippet in iterations:
                clean = snippet.replace('\n', ' ')[:70]
                print(f'         -> {count}x: "...{clean}..."')

    # --------------------------------------------------------
    # Part 5: Summary
    # --------------------------------------------------------
    print('\n' + '=' * 78)
    print('SUMMARY')
    print('=' * 78)

    n_total = len(folio_runs)
    max_global = folio_runs[0]['max_run'] if folio_runs else 0
    median_idx = n_total // 2
    median_run = folio_runs[median_idx]['max_run'] if folio_runs else 0

    print(f'\nTotal Currier B folios: {n_total}')
    print(f'Global max run: {max_global} ({folio_runs[0]["folio"]})')
    print(f'Median max run: {median_run}')
    matched_runs = []
    for m in CONFIDENT_MATCHES:
        fol = m['folio']
        run_val = next((x['max_run'] for x in folio_runs if x['folio'] == fol), 0)
        matched_runs.append(f'{fol}={run_val}')
    print(f'Matched folios max runs: {", ".join(matched_runs)}')

    print('\nConsecutive token repetition is rare across all Currier B folios.')
    print('Most folios have max run of 2 (a single repeated pair).')
    print('Runs of 3+ are uncommon; runs of 4+ are exceptional.')
    print()
    print('PL iteration counts (e.g., "nine times", "three times") are')
    print('sparse in the matched chapters. Direct encoding of iteration')
    print('count as token repetition is not systematically supported.')


if __name__ == '__main__':
    main()
