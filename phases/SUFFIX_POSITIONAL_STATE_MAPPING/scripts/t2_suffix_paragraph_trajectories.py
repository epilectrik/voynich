"""
T2: Per-Suffix Paragraph Quintile Trajectories
===============================================
Phase: SUFFIX_POSITIONAL_STATE_MAPPING

C932 showed category-level paragraph gradients (terminal r=-0.89, bare r=+0.90).
This tests whether individual suffixes have monotonic paragraph trajectories.

Pass: 10+ individual suffixes with |partial rho|>0.8, Bonferroni p<0.05
Fail: <5 monotonic trends

Output: t2_suffix_paragraph_trajectories.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

MIN_TOKENS = 50  # Minimum body-line tokens for a suffix


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Build paragraph structure ─────────────────────────
    print("Building paragraph structure...")

    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_morph = {}
    for w in unique_words:
        word_morph[w] = morph.extract(w)

    # Group tokens by folio and line
    folio_lines = defaultdict(lambda: defaultdict(list))
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        folio_lines[token.folio][token.line].append(token)

    # Identify paragraphs: consecutive line groups within a folio
    # A paragraph break occurs at a gap in line numbering
    para_records = []  # (folio, para_idx, line_in_para, n_lines_in_para, tokens)

    for folio in sorted(folio_lines.keys()):
        lines_sorted = sorted(folio_lines[folio].keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if not lines_sorted:
            continue

        # Simple paragraph detection: consecutive line numbers
        paragraphs = []
        current_para = [lines_sorted[0]]
        for i in range(1, len(lines_sorted)):
            try:
                curr_num = int(lines_sorted[i])
                prev_num = int(lines_sorted[i-1])
                if curr_num == prev_num + 1:
                    current_para.append(lines_sorted[i])
                else:
                    paragraphs.append(current_para)
                    current_para = [lines_sorted[i]]
            except ValueError:
                paragraphs.append(current_para)
                current_para = [lines_sorted[i]]
        paragraphs.append(current_para)

        for para_idx, para_lines in enumerate(paragraphs):
            n_lines = len(para_lines)
            if n_lines < 3:  # Need at least 3 lines for quintile assignment
                continue
            for line_pos, line_key in enumerate(para_lines):
                # Normalize line position within paragraph [0, 1]
                para_position = line_pos / (n_lines - 1) if n_lines > 1 else 0.5
                # Quintile assignment
                quintile = min(4, int(para_position * 5))
                tokens = folio_lines[folio][line_key]
                para_records.append((folio, para_idx, quintile, n_lines, tokens))

    print(f"  Paragraph lines: {len(para_records)}")

    # ── Extract per-suffix quintile frequencies ────────────
    print("Computing per-suffix paragraph trajectories...")

    # Count (suffix, quintile) occurrences, also track line lengths
    suffix_quintile_counts = defaultdict(lambda: Counter())
    quintile_totals = Counter()
    line_lengths = []

    for folio, para_idx, quintile, n_lines, tokens in para_records:
        line_len = 0
        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            suffix = m.suffix or 'NONE'
            suffix_quintile_counts[suffix][quintile] += 1
            quintile_totals[quintile] += 1
            line_len += 1
        line_lengths.append((quintile, line_len))

    # Compute per-suffix quintile frequencies (normalized by quintile total)
    testable_suffixes = [s for s, counts in suffix_quintile_counts.items()
                         if sum(counts.values()) >= MIN_TOKENS]
    n_testable = len(testable_suffixes)
    bonf_threshold = 0.05 / n_testable if n_testable > 0 else 0.05

    print(f"  Testable suffixes (N>={MIN_TOKENS}): {n_testable}")
    print(f"  Bonferroni threshold: p < {bonf_threshold:.4f}")

    # ══════════════════════════════════════════════════════
    # PER-SUFFIX TRAJECTORIES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"PER-SUFFIX PARAGRAPH QUINTILE TRAJECTORIES")
    print(f"{'='*70}")

    print(f"\n  {'SUFFIX':<10s} {'N':>6s} {'Q0%':>7s} {'Q1%':>7s} {'Q2%':>7s} "
          f"{'Q3%':>7s} {'Q4%':>7s} {'rho':>7s} {'p':>10s} {'Trend':>10s}")
    print(f"  {'-'*10} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} "
          f"{'-'*7} {'-'*10} {'-'*10}")

    suffix_trajectories = {}
    monotonic_count = 0

    for suffix in sorted(testable_suffixes,
                         key=lambda s: -sum(suffix_quintile_counts[s].values())):
        counts = suffix_quintile_counts[suffix]
        total = sum(counts.values())

        # Frequency per quintile (as % of that quintile's total)
        q_freqs = []
        for q in range(5):
            q_total = quintile_totals[q]
            q_count = counts.get(q, 0)
            freq = (q_count / q_total * 100) if q_total > 0 else 0.0
            q_freqs.append(freq)

        # Spearman rho of frequency vs quintile
        quintile_indices = np.array([0, 1, 2, 3, 4])
        freq_array = np.array(q_freqs)

        if np.std(freq_array) > 0:
            rho, p_val = stats.spearmanr(quintile_indices, freq_array)
        else:
            rho, p_val = 0.0, 1.0

        is_monotonic = abs(rho) > 0.8 and p_val < bonf_threshold
        if is_monotonic:
            monotonic_count += 1

        if rho > 0.5:
            trend = 'RISING'
        elif rho < -0.5:
            trend = 'FALLING'
        else:
            trend = 'FLAT'

        suffix_trajectories[suffix] = {
            'n': total,
            'quintile_freqs_pct': [float(f) for f in q_freqs],
            'spearman_rho': float(rho),
            'spearman_p': float(p_val),
            'trend': trend,
            'is_monotonic': bool(is_monotonic),
        }

        sig = '***' if is_monotonic else ('*' if p_val < 0.05 else '')
        print(f"  {suffix:<10s} {total:>6d} {q_freqs[0]:>6.2f}% {q_freqs[1]:>6.2f}% "
              f"{q_freqs[2]:>6.2f}% {q_freqs[3]:>6.2f}% {q_freqs[4]:>6.2f}% "
              f"{rho:>+7.3f} {p_val:>10.3e} {trend:>10s} {sig}")

    # ── Summary ───────────────────────────────────────────
    rising = [s for s, t in suffix_trajectories.items() if t['trend'] == 'RISING']
    falling = [s for s, t in suffix_trajectories.items() if t['trend'] == 'FALLING']
    monotonic_list = [s for s, t in suffix_trajectories.items() if t['is_monotonic']]

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Monotonic suffixes (|rho|>0.8, Bonf p<0.05): "
          f"{monotonic_count}/{n_testable}")
    print(f"  Rising trend (rho>0.5): {rising}")
    print(f"  Falling trend (rho<-0.5): {falling}")
    print(f"  Strictly monotonic: {monotonic_list}")

    # Verdict
    if monotonic_count >= 10:
        verdict = 'SUFFIX_PARAGRAPH_TRAJECTORIES_CONFIRMED'
        detail = (f'{monotonic_count}/{n_testable} suffixes show monotonic '
                  f'paragraph trajectories. Individual suffix identity carries '
                  f'paragraph-position information beyond category level (C932).')
    elif monotonic_count >= 5:
        verdict = 'SUFFIX_PARAGRAPH_TRAJECTORIES_PARTIAL'
        detail = (f'{monotonic_count}/{n_testable} suffixes show monotonic trends. '
                  f'Category gradients partially decompose to individuals.')
    else:
        verdict = 'NO_SUFFIX_PARAGRAPH_TRAJECTORIES'
        detail = (f'Only {monotonic_count}/{n_testable} suffixes are monotonic. '
                  f'C932 category gradients do NOT decompose to individual suffixes.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'SUFFIX_POSITIONAL_STATE_MAPPING',
            'test': 'T2_SUFFIX_PARAGRAPH_TRAJECTORIES',
            'min_tokens': MIN_TOKENS,
            'bonferroni_threshold': bonf_threshold,
        },
        'corpus': {
            'paragraph_lines': len(para_records),
            'testable_suffixes': n_testable,
            'quintile_totals': {str(k): v for k, v in quintile_totals.items()},
        },
        'suffix_trajectories': suffix_trajectories,
        'monotonic_count': monotonic_count,
        'monotonic_list': monotonic_list,
        'rising': rising,
        'falling': falling,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't2_suffix_paragraph_trajectories.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
