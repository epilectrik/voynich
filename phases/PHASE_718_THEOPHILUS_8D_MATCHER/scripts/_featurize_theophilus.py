"""PHASE_718: Featurize Theophilus De Diversis Artibus chapters.

Segments Theophilus body English text by CHAPTER markers, applies the same
keyword-based feature extraction as Codicillus, outputs JSON in compatible format
for use with the 8D matcher.

Reuses keyword dictionaries from sources/codicillus/_featurize_codicillus.py.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_718_THEOPHILUS_8D_MATCHER' / 'results' / 'theophilus_chapter_features.json'

# Import keyword dictionaries from Codicillus featurizer
sys.path.insert(0, str(ROOT / 'sources' / 'codicillus'))
from _featurize_codicillus import (
    HEAT_WORDS, HEAT_INTENSITY, HEAT_TRANSITION_WORDS,
    MONITORING_WORDS, COLOR_WORDS, CONSISTENCY_WORDS, VOLATILITY_WORDS,
    TERMINATION_WORDS, THRESHOLD_WORDS, TIME_WORDS,
    CORRECTION_WORDS, RECOVERABLE_WORDS, FATAL_WORDS, DRIFT_WORDS,
    count_keyword_hits, count_words,
    compute_k_channel, compute_h_channel, compute_t_channel, compute_e_channel,
)


# Body English chapter line ranges per Theophilus README
BOOK_RANGES = {
    'Book I':   (2278, 4283),
    'Book II':  (7520, 9147),
    'Book III': (11337, 20528),
}


def extract_chapters(filepath):
    """Parse Theophilus, return list of (book, chapter_num, text) tuples.
    Uses CHAPTER markers in English body sections.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    chapters = []
    for book_name, (lo, hi) in BOOK_RANGES.items():
        body_lines = lines[lo:hi]
        # Find CHAPTER markers (regex tolerates extra whitespace)
        chapter_marker_re = re.compile(r'^CHAPTER\s+([IVXLC]+)\.', re.IGNORECASE)
        chapter_boundaries = []
        for i, line in enumerate(body_lines):
            m = chapter_marker_re.match(line.strip())
            if m:
                chapter_boundaries.append((i, m.group(1)))
        chapter_boundaries.append((len(body_lines), 'END'))

        # Extract each chapter text
        for j in range(len(chapter_boundaries) - 1):
            start_i, roman = chapter_boundaries[j]
            end_i, _ = chapter_boundaries[j + 1]
            ch_lines = body_lines[start_i:end_i]
            ch_text = ' '.join(ln.strip() for ln in ch_lines)
            if ch_lines and roman != 'END':
                chapters.append({
                    'book': book_name,
                    'chapter_roman': roman,
                    'text': ch_text,
                    'line_start_in_book': start_i,
                    'line_end_in_book': end_i,
                    'n_lines': end_i - start_i,
                })
    return chapters


def featurize_chapter(ch_text):
    """Apply Codicillus featurization to a chapter's English text."""
    text_lower = ch_text.lower()
    total_words = count_words(ch_text)
    if total_words < 20:
        return None
    k = compute_k_channel(ch_text, total_words)
    h = compute_h_channel(ch_text, total_words)
    t = compute_t_channel(ch_text, total_words)
    e = compute_e_channel(ch_text, total_words)
    return {
        'n_words': total_words,
        'k_channel': k,
        'h_channel': h,
        't_channel': t,
        'e_channel': e,
    }


def main():
    print("=" * 70)
    print("PHASE_718 THEOPHILUS FEATURIZATION")
    print("=" * 70)

    fpath = ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt'
    chapters = extract_chapters(fpath)
    print(f"\nExtracted {len(chapters)} chapters across books")
    book_counts = {}
    for ch in chapters:
        book_counts[ch['book']] = book_counts.get(ch['book'], 0) + 1
    for book, count in book_counts.items():
        print(f"  {book}: {count} chapters")

    # Featurize each chapter
    featurized = []
    skipped = 0
    for idx, ch in enumerate(chapters):
        feats = featurize_chapter(ch['text'])
        if feats is None:
            skipped += 1
            continue
        family = 'theophilus_workshop'  # placeholder family label (NOT alchemy)
        record = {
            'segment_idx': idx,
            'book': ch['book'],
            'chapter_roman': ch['chapter_roman'],
            'summary': f"{ch['book']} Chapter {ch['chapter_roman']}",
            'family': family,
            'n_lines': ch['n_lines'],
            **feats,
        }
        featurized.append(record)
    print(f"\nFeaturized {len(featurized)} chapters (skipped {skipped} with <20 words)")

    # Stats summary
    heat_rates = [c['k_channel']['heat_rate'] for c in featurized]
    mon_rates = [c['h_channel']['monitoring_rate'] for c in featurized]
    term_rates = [c['t_channel']['termination_rate'] for c in featurized]
    corr_rates = [c['e_channel']['correction_rate'] for c in featurized]
    import statistics
    print(f"\nChannel rate statistics across {len(featurized)} chapters:")
    print(f"  heat_rate:        mean={statistics.mean(heat_rates):.4f}, median={statistics.median(heat_rates):.4f}, max={max(heat_rates):.4f}")
    print(f"  monitoring_rate:  mean={statistics.mean(mon_rates):.4f}, median={statistics.median(mon_rates):.4f}, max={max(mon_rates):.4f}")
    print(f"  termination_rate: mean={statistics.mean(term_rates):.4f}, median={statistics.median(term_rates):.4f}, max={max(term_rates):.4f}")
    print(f"  correction_rate:  mean={statistics.mean(corr_rates):.4f}, median={statistics.median(corr_rates):.4f}, max={max(corr_rates):.4f}")

    # Save
    output = {
        'metadata': {
            'source': 'theophilus_de_diversis_artibus',
            'edition': 'Hendrie 1847 Latin-English parallel',
            'date': '2026-05-20',
            'n_chapters_total_extracted': len(chapters),
            'n_chapters_featurized': len(featurized),
            'segmentation': 'English CHAPTER markers in body ranges per README',
            'keywords': 'reused from codicillus _featurize_codicillus.py',
        },
        'chapters': featurized,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
