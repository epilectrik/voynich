"""
02_cross_folio_position.py - Cross-folio paragraph position comparison

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Test B: Are paragraph-1s across different folios more similar to each other than to other paragraphs?

Question: Do same-ordinal paragraphs cluster structurally across folios?

Method:
1. Extract structural features per paragraph (role distribution, FL types, HT rate, length)
2. Compute similarity matrix across all paragraphs from all folios
3. Test whether same-ordinal paragraphs cluster together

Null model: Shuffle paragraph ordinals within folios, measure whether real ordinals
produce tighter within-ordinal similarity

Expected: Weak ordinal clustering (from C857: P1 is NOT structurally special)
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.spatial.distance import cosine, euclidean

GALLOWS = {'k', 't', 'p', 'f'}

# FL categories from C777
FL_INITIAL = {'ar', 'r'}
FL_LATE = {'al', 'l', 'ol'}
FL_TERMINAL = {'aly', 'am', 'y'}

def has_gallows_initial(word):
    if not word or not word.strip():
        return False
    return word[0] in GALLOWS

def load_raw_data():
    data_path = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['transcriber'] == 'H' and row['language'] == 'B':
                folio = row['folio']
                line = row['line_number']
                word = row['word']
                section = row['section']
                if '*' in word:
                    continue
                folio_lines[folio][line].append({
                    'word': word,
                    'section': section
                })

    return folio_lines

def detect_paragraphs(folio_data):
    """Detect paragraphs using gallows-initial heuristic."""
    paragraphs = defaultdict(list)
    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]['word']
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].extend(tokens)

    return paragraphs

def get_fl_category(suffix):
    """Categorize FL type."""
    if not suffix:
        return None
    if suffix in FL_INITIAL:
        return 'INITIAL'
    if suffix in FL_LATE:
        return 'LATE'
    if suffix in FL_TERMINAL:
        return 'TERMINAL'
    return None

def extract_features(tokens, morph):
    """
    Extract structural features from paragraph tokens.

    Features:
    - token_count: number of tokens
    - mean_token_length: average token length
    - gallows_rate: fraction of tokens starting with gallows
    - fl_initial_rate, fl_late_rate, fl_terminal_rate: FL type distribution
    - unique_middle_rate: unique MIDDLEs / total tokens
    """
    if not tokens:
        return None

    words = [t['word'] for t in tokens]
    n = len(words)

    # Basic stats
    token_count = n
    mean_length = np.mean([len(w) for w in words])

    # Gallows rate
    gallows_count = sum(1 for w in words if has_gallows_initial(w))
    gallows_rate = gallows_count / n

    # Morphological analysis
    middles = []
    fl_counts = Counter()

    for word in words:
        m = morph.extract(word)
        if m:
            if m.middle:
                middles.append(m.middle)
            fl_cat = get_fl_category(m.suffix)
            if fl_cat:
                fl_counts[fl_cat] += 1

    unique_middle_rate = len(set(middles)) / n if n > 0 else 0

    # FL rates
    fl_total = sum(fl_counts.values())
    fl_initial_rate = fl_counts['INITIAL'] / n
    fl_late_rate = fl_counts['LATE'] / n
    fl_terminal_rate = fl_counts['TERMINAL'] / n

    return {
        'token_count': token_count,
        'mean_token_length': mean_length,
        'gallows_rate': gallows_rate,
        'fl_initial_rate': fl_initial_rate,
        'fl_late_rate': fl_late_rate,
        'fl_terminal_rate': fl_terminal_rate,
        'unique_middle_rate': unique_middle_rate
    }

def feature_vector(features):
    """Convert feature dict to numpy array for similarity computation."""
    return np.array([
        features['token_count'] / 100,  # normalize
        features['mean_token_length'] / 10,
        features['gallows_rate'],
        features['fl_initial_rate'],
        features['fl_late_rate'],
        features['fl_terminal_rate'],
        features['unique_middle_rate']
    ])

def cosine_similarity(v1, v2):
    """Compute cosine similarity (1 - cosine distance)."""
    if np.allclose(v1, 0) or np.allclose(v2, 0):
        return 0.0
    return 1 - cosine(v1, v2)

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    # Extract all paragraphs with features
    all_paragraphs = []

    for folio in sorted(folio_data.keys()):
        paragraphs = detect_paragraphs(folio_data[folio])

        # Normalize ordinal to relative position (1=first, 2=second, etc.)
        # Also compute relative position (early/middle/late)
        n_paras = len(paragraphs)
        if n_paras < 2:
            continue

        for ordinal in sorted(paragraphs.keys()):
            tokens = paragraphs[ordinal]
            features = extract_features(tokens, morph)
            if features is None:
                continue

            # Relative position: 0=first, 0.5=middle, 1=last
            rel_pos = (ordinal - 1) / (n_paras - 1) if n_paras > 1 else 0

            all_paragraphs.append({
                'folio': folio,
                'ordinal': ordinal,
                'n_paras_in_folio': n_paras,
                'relative_position': rel_pos,
                'position_bin': 'early' if rel_pos < 0.33 else ('late' if rel_pos > 0.67 else 'middle'),
                'features': features,
                'vector': feature_vector(features)
            })

    print("=" * 70)
    print("TEST B: CROSS-FOLIO PARAGRAPH POSITION COMPARISON")
    print("=" * 70)
    print(f"\nTotal paragraphs analyzed: {len(all_paragraphs)}")
    print(f"From {len(set(p['folio'] for p in all_paragraphs))} folios")

    # Bin paragraphs by position
    position_bins = defaultdict(list)
    for p in all_paragraphs:
        position_bins[p['position_bin']].append(p)

    print(f"\nPosition bins:")
    for bin_name in ['early', 'middle', 'late']:
        print(f"  {bin_name}: {len(position_bins[bin_name])} paragraphs")

    # Compute within-bin vs between-bin similarity
    within_sims = []
    between_sims = []

    # Sample pairs for efficiency
    np.random.seed(42)

    for bin_name, paras in position_bins.items():
        n = len(paras)
        if n < 2:
            continue

        # Within-bin pairs (sample if too many)
        n_pairs = min(500, n * (n-1) // 2)
        for _ in range(n_pairs):
            i, j = np.random.choice(n, 2, replace=False)
            sim = cosine_similarity(paras[i]['vector'], paras[j]['vector'])
            within_sims.append(sim)

    # Between-bin pairs
    bins = list(position_bins.keys())
    for i, bin1 in enumerate(bins):
        for bin2 in bins[i+1:]:
            paras1 = position_bins[bin1]
            paras2 = position_bins[bin2]

            n_pairs = min(300, len(paras1) * len(paras2))
            for _ in range(n_pairs):
                p1 = paras1[np.random.randint(len(paras1))]
                p2 = paras2[np.random.randint(len(paras2))]
                sim = cosine_similarity(p1['vector'], p2['vector'])
                between_sims.append(sim)

    print(f"\n--- Similarity Analysis ---")
    print(f"Within-bin similarity:  {np.mean(within_sims):.3f} (sd={np.std(within_sims):.3f})")
    print(f"Between-bin similarity: {np.mean(between_sims):.3f} (sd={np.std(between_sims):.3f})")

    # Statistical test
    t_stat, p_val = stats.ttest_ind(within_sims, between_sims)
    print(f"\nWithin vs Between t-test:")
    print(f"  t = {t_stat:.3f}, p = {p_val:.4f}")

    effect_size = (np.mean(within_sims) - np.mean(between_sims)) / np.sqrt(
        (np.std(within_sims)**2 + np.std(between_sims)**2) / 2
    )
    print(f"  Cohen's d = {effect_size:.3f}")

    # Analyze feature means by position
    print(f"\n--- Feature Means by Position ---")
    feature_names = ['token_count', 'gallows_rate', 'fl_initial_rate', 'fl_late_rate', 'fl_terminal_rate']

    for fname in feature_names:
        print(f"\n{fname}:")
        for bin_name in ['early', 'middle', 'late']:
            vals = [p['features'][fname] for p in position_bins[bin_name]]
            print(f"  {bin_name}: {np.mean(vals):.3f} (sd={np.std(vals):.3f})")

    # ANOVA for each feature
    print(f"\n--- ANOVA by Position ---")
    for fname in feature_names:
        groups = [
            [p['features'][fname] for p in position_bins['early']],
            [p['features'][fname] for p in position_bins['middle']],
            [p['features'][fname] for p in position_bins['late']]
        ]
        f_stat, p_val = stats.f_oneway(*groups)
        sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else ""))
        print(f"  {fname}: F={f_stat:.2f}, p={p_val:.4f} {sig}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if effect_size > 0.2:
        print(f"\nMODERATE POSITIONAL CLUSTERING (d={effect_size:.2f}):")
        print("  Same-position paragraphs are more similar across folios.")
        print("  Suggests paragraph ordinal carries structural meaning.")
    elif effect_size > 0.05:
        print(f"\nWEAK POSITIONAL CLUSTERING (d={effect_size:.2f}):")
        print("  Slight tendency for same-position similarity.")
        print("  Consistent with C857 (P1 not strongly special).")
    else:
        print(f"\nNO POSITIONAL CLUSTERING (d={effect_size:.2f}):")
        print("  Paragraph structure independent of ordinal position.")
        print("  Strong support for C855 (PARALLEL_PROGRAMS).")

    # Save results
    def clean_for_json(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(i) for i in obj]
        return obj

    results = {
        'summary': {
            'total_paragraphs': len(all_paragraphs),
            'folios': len(set(p['folio'] for p in all_paragraphs)),
            'within_bin_similarity': float(np.mean(within_sims)),
            'between_bin_similarity': float(np.mean(between_sims)),
            'cohens_d': float(effect_size),
            't_statistic': float(t_stat),
            'p_value': float(p_val)
        },
        'position_counts': {k: len(v) for k, v in position_bins.items()},
        'feature_means': {
            bin_name: {
                fname: float(np.mean([p['features'][fname] for p in position_bins[bin_name]]))
                for fname in feature_names
            }
            for bin_name in ['early', 'middle', 'late']
        }
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/02_cross_folio_position.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
