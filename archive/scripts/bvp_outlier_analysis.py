"""
BVP Outlier Analysis

Investigate the 3 vocabulary outliers detected in BVP-4:
- f113r: Large vocabulary
- f66v: High uniqueness
- f105v: High uniqueness
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
REGIME_FILE = BASE / "phases" / "OPS2_control_strategy_clustering" / "ops2_folio_cluster_assignments.json"
CONTROL_SIGS = BASE / "results" / "control_signatures.json"
OPS3_FILE = BASE / "phases" / "OPS3_risk_time_stability_tradeoffs" / "ops3_tradeoff_models.json"

def load_all_data():
    # Transcription
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)

    # Regimes
    with open(REGIME_FILE, 'r') as f:
        regimes = json.load(f)['assignments']

    # Control signatures
    with open(CONTROL_SIGS, 'r') as f:
        control_sigs = json.load(f)['signatures']

    # Stability data
    with open(OPS3_FILE, 'r') as f:
        stability = json.load(f)['folio_normalized_axes']

    return data, regimes, control_sigs, stability

def get_b_folio_data(data):
    """Get Currier B data grouped by folio."""
    folio_tokens = defaultdict(list)
    for row in data:
        if row.get('language') == 'B' and row.get('transcriber') == 'H':
            folio_tokens[row['folio']].append(row)
    return dict(folio_tokens)

def analyze_outlier(folio, folio_tokens, all_b_tokens, regimes, control_sigs, stability):
    """Detailed analysis of a single outlier folio."""
    tokens = folio_tokens.get(folio, [])
    vocab = set(t['word'] for t in tokens if t['word'])

    # Build global token frequency
    global_token_freq = Counter()
    global_token_folios = defaultdict(set)
    for f, toks in folio_tokens.items():
        for t in toks:
            if t['word']:
                global_token_freq[t['word']] += 1
                global_token_folios[t['word']].add(f)

    n_folios = len(folio_tokens)

    # Compute metrics
    vocab_size = len(vocab)
    token_count = len(tokens)

    # Unique tokens (only in this folio)
    unique_tokens = [t for t in vocab if len(global_token_folios[t]) == 1]
    unique_pct = len(unique_tokens) / vocab_size if vocab_size > 0 else 0

    # Core tokens (in >=50% of folios)
    core_tokens = [t for t in vocab if len(global_token_folios[t]) >= n_folios * 0.5]
    core_pct = len(core_tokens) / vocab_size if vocab_size > 0 else 0

    # Rare tokens (in <=5 folios)
    rare_tokens = [t for t in vocab if len(global_token_folios[t]) <= 5]
    rare_pct = len(rare_tokens) / vocab_size if vocab_size > 0 else 0

    # Get operational properties
    regime = regimes.get(folio, {}).get('cluster_id', 'UNKNOWN')

    sig = control_sigs.get(folio, {})
    link_density = sig.get('link_density', 0)
    terminal_state = sig.get('terminal_state', 'UNKNOWN')
    reset_present = sig.get('reset_present', False)
    hazard_density = sig.get('hazard_density', 0)

    stab = stability.get(folio, {})
    stability_score = stab.get('stability', 0)
    risk_score = stab.get('risk', 0)

    # Line structure
    lines = defaultdict(list)
    for t in tokens:
        lines[t.get('line_number', '1')].append(t['word'])
    n_lines = len(lines)
    avg_line_len = np.mean([len(l) for l in lines.values()]) if lines else 0

    # Section
    sections = set(t.get('section', '') for t in tokens)
    section = list(sections)[0] if len(sections) == 1 else str(sections)

    # Get most distinctive tokens (appear in fewest other folios)
    token_distinctiveness = [(t, len(global_token_folios[t])) for t in vocab]
    token_distinctiveness.sort(key=lambda x: x[1])
    most_distinctive = token_distinctiveness[:10]

    # Get most common tokens in this folio
    folio_token_freq = Counter(t['word'] for t in tokens if t['word'])
    most_common = folio_token_freq.most_common(10)

    return {
        'folio': folio,
        'vocab_size': vocab_size,
        'token_count': token_count,
        'n_lines': n_lines,
        'avg_line_len': avg_line_len,
        'section': section,
        'regime': regime,
        'link_density': link_density,
        'terminal_state': terminal_state,
        'reset_present': reset_present,
        'hazard_density': hazard_density,
        'stability': stability_score,
        'risk': risk_score,
        'unique_tokens': len(unique_tokens),
        'unique_pct': unique_pct,
        'core_tokens': len(core_tokens),
        'core_pct': core_pct,
        'rare_tokens': len(rare_tokens),
        'rare_pct': rare_pct,
        'most_distinctive': most_distinctive,
        'most_common': most_common,
        'sample_unique': unique_tokens[:20]
    }

def compute_percentiles(folio_tokens, all_results):
    """Compute where outliers rank among all folios."""
    all_vocab_sizes = []
    all_unique_pcts = []

    global_token_folios = defaultdict(set)
    for f, toks in folio_tokens.items():
        for t in toks:
            if t['word']:
                global_token_folios[t['word']].add(f)

    n_folios = len(folio_tokens)

    for f, toks in folio_tokens.items():
        vocab = set(t['word'] for t in toks if t['word'])
        vocab_size = len(vocab)
        unique = [t for t in vocab if len(global_token_folios[t]) == 1]
        unique_pct = len(unique) / vocab_size if vocab_size > 0 else 0
        all_vocab_sizes.append((f, vocab_size))
        all_unique_pcts.append((f, unique_pct))

    all_vocab_sizes.sort(key=lambda x: x[1], reverse=True)
    all_unique_pcts.sort(key=lambda x: x[1], reverse=True)

    return {
        'vocab_size_ranking': all_vocab_sizes[:10],
        'unique_pct_ranking': all_unique_pcts[:10]
    }

def main():
    print("="*70)
    print("BVP OUTLIER ANALYSIS")
    print("="*70)

    data, regimes, control_sigs, stability = load_all_data()
    folio_tokens = get_b_folio_data(data)

    outliers = ['f113r', 'f66v', 'f105v']

    # Get percentile rankings
    rankings = compute_percentiles(folio_tokens, None)

    print("\n" + "="*70)
    print("GLOBAL RANKINGS")
    print("="*70)

    print("\nTop 10 by vocabulary size:")
    for i, (f, size) in enumerate(rankings['vocab_size_ranking'], 1):
        marker = " <-- OUTLIER" if f in outliers else ""
        print(f"  {i:2}. {f}: {size} tokens{marker}")

    print("\nTop 10 by uniqueness %:")
    for i, (f, pct) in enumerate(rankings['unique_pct_ranking'], 1):
        marker = " <-- OUTLIER" if f in outliers else ""
        print(f"  {i:2}. {f}: {pct*100:.1f}%{marker}")

    # Analyze each outlier
    for folio in outliers:
        print("\n" + "="*70)
        print(f"OUTLIER: {folio}")
        print("="*70)

        result = analyze_outlier(folio, folio_tokens, data, regimes, control_sigs, stability)

        print(f"\n--- Basic Properties ---")
        print(f"Section: {result['section']}")
        print(f"Regime: {result['regime']}")
        print(f"Token count: {result['token_count']}")
        print(f"Vocabulary size: {result['vocab_size']}")
        print(f"Lines: {result['n_lines']}")
        print(f"Avg tokens/line: {result['avg_line_len']:.1f}")

        print(f"\n--- Operational Profile ---")
        print(f"LINK density: {result['link_density']:.3f}")
        print(f"Terminal state: {result['terminal_state']}")
        print(f"Reset present: {result['reset_present']}")
        print(f"Hazard density: {result['hazard_density']:.3f}")
        print(f"Stability: {result['stability']:.3f}")
        print(f"Risk: {result['risk']:.3f}")

        print(f"\n--- Vocabulary Profile ---")
        print(f"Unique tokens (only in this folio): {result['unique_tokens']} ({result['unique_pct']*100:.1f}%)")
        print(f"Core tokens (in >=50% of folios): {result['core_tokens']} ({result['core_pct']*100:.1f}%)")
        print(f"Rare tokens (in <=5 folios): {result['rare_tokens']} ({result['rare_pct']*100:.1f}%)")

        print(f"\n--- Most Distinctive Tokens ---")
        print("(tokens that appear in fewest other folios)")
        for token, n_folios in result['most_distinctive']:
            print(f"  '{token}' - appears in {n_folios} folio(s)")

        print(f"\n--- Most Common Tokens (in this folio) ---")
        for token, count in result['most_common']:
            print(f"  '{token}' - {count} occurrences")

        print(f"\n--- Sample Unique Tokens ---")
        print(f"  {result['sample_unique']}")

    # Compare outliers to typical folios
    print("\n" + "="*70)
    print("COMPARISON TO TYPICAL FOLIOS")
    print("="*70)

    all_metrics = []
    global_token_folios = defaultdict(set)
    for f, toks in folio_tokens.items():
        for t in toks:
            if t['word']:
                global_token_folios[t['word']].add(f)

    n_folios = len(folio_tokens)

    for f, toks in folio_tokens.items():
        vocab = set(t['word'] for t in toks if t['word'])
        vocab_size = len(vocab)
        unique = [t for t in vocab if len(global_token_folios[t]) == 1]
        unique_pct = len(unique) / vocab_size if vocab_size > 0 else 0
        all_metrics.append({
            'folio': f,
            'vocab_size': vocab_size,
            'unique_pct': unique_pct,
            'token_count': len(toks)
        })

    vocab_sizes = [m['vocab_size'] for m in all_metrics]
    unique_pcts = [m['unique_pct'] for m in all_metrics]
    token_counts = [m['token_count'] for m in all_metrics]

    print(f"\nTypical folio (median):")
    print(f"  Vocabulary size: {np.median(vocab_sizes):.0f}")
    print(f"  Token count: {np.median(token_counts):.0f}")
    print(f"  Unique %: {np.median(unique_pcts)*100:.1f}%")

    for folio in outliers:
        m = next(x for x in all_metrics if x['folio'] == folio)
        vocab_z = (m['vocab_size'] - np.mean(vocab_sizes)) / np.std(vocab_sizes)
        unique_z = (m['unique_pct'] - np.mean(unique_pcts)) / np.std(unique_pcts)
        print(f"\n{folio}:")
        print(f"  Vocabulary size: {m['vocab_size']} (z={vocab_z:+.2f})")
        print(f"  Token count: {m['token_count']}")
        print(f"  Unique %: {m['unique_pct']*100:.1f}% (z={unique_z:+.2f})")

    # Interpretation
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    print("""
f113r - LARGE VOCABULARY OUTLIER:
  This folio has an unusually large vocabulary. Key questions:
  - Is it simply a longer folio? (token count vs vocab size ratio)
  - Does it have lower repetition? (using more unique tokens)
  - Is it a specialized procedure using distinct terminology?

f66v, f105v - HIGH UNIQUENESS OUTLIERS:
  These folios have unusually high proportions of tokens that appear
  ONLY in these folios. Key questions:
  - Are these highly specialized procedures?
  - Do they contain transcription artifacts or unusual glyphs?
  - Are they from unusual sections or positions?
""")

if __name__ == '__main__':
    main()
