"""
SID-04 Quick Hygiene Check - Fast version without bootstrap
"""

import math
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}


def is_grammar_original(t):
    t = t.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_grammar_strict(t):
    t = t.lower().strip()
    if len(t) < 2 or not t.isalpha() or t in HAZARD_TOKENS:
        return True
    return is_grammar_original(t)


def load_data():
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()  # skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').strip()
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and not word.startswith('*') and word.isalpha():
                    data.append({'token': word, 'section': section})
    return data


def test_clustering(data, is_grammar):
    residue = [d['token'] for d in data if not is_grammar(d['token'])]
    if len(residue) < 100:
        return 0, 0
    repeats = sum(1 for i in range(1, len(residue)) if residue[i] == residue[i-1])
    obs = repeats / (len(residue) - 1)
    vocab = Counter(residue)
    exp = sum((c/len(residue))**2 for c in vocab.values())
    n = len(residue) - 1
    std = math.sqrt(exp * (1 - exp) / n) if exp < 1 else 0.001
    z = (obs - exp) / std if std > 0 else 0
    return round(z, 1), len(residue)


def test_exclusivity(data, is_grammar):
    by_section = defaultdict(set)
    for d in data:
        if not is_grammar(d['token']):
            by_section[d['section']].add(d['token'])
    all_tokens = set()
    for tokens in by_section.values():
        all_tokens.update(tokens)
    exclusive = sum(1 for t in all_tokens
                   if sum(1 for s, tokens in by_section.items() if t in tokens) == 1)
    rate = exclusive / len(all_tokens) if all_tokens else 0
    return round(rate, 3), len(all_tokens)


def test_hazard_distance(data, is_grammar):
    tokens = [d['token'] for d in data]
    hazard_pos = [i for i, t in enumerate(tokens) if t in HAZARD_TOKENS]
    residue_pos = [i for i, t in enumerate(tokens) if not is_grammar(t)]
    if not hazard_pos or not residue_pos:
        return 0, 0, 0
    dists = [min(abs(r - h) for h in hazard_pos) for r in residue_pos]
    mean_dist = np.mean(dists)
    # Simple expected: uniform distribution
    exp_dist = len(tokens) / (len(hazard_pos) + 1) / 2
    return round(mean_dist, 2), round(exp_dist, 2), len(residue_pos)


def test_run_cv(data, is_grammar):
    runs = []
    current = 0
    for d in data:
        if not is_grammar(d['token']):
            current += 1
        else:
            if current > 0:
                runs.append(current)
            current = 0
    if current > 0:
        runs.append(current)
    if len(runs) < 10:
        return 0, 0
    cv = np.std(runs) / np.mean(runs) if np.mean(runs) > 0 else 0
    return round(cv, 2), len(runs)


def main():
    print("SID-04 Quick Hygiene Check")
    print("=" * 60)

    data = load_data()
    print(f"Loaded {len(data)} tokens\n")

    # Original
    print("ORIGINAL classification:")
    z1_o, n1_o = test_clustering(data, is_grammar_original)
    ex_o, nt_o = test_exclusivity(data, is_grammar_original)
    hd_o, he_o, nh_o = test_hazard_distance(data, is_grammar_original)
    cv_o, nr_o = test_run_cv(data, is_grammar_original)

    print(f"  Residue count: {n1_o}")
    print(f"  Clustering z: {z1_o}")
    print(f"  Exclusivity: {ex_o}")
    print(f"  Hazard dist: {hd_o} (expected ~{he_o})")
    print(f"  Run CV: {cv_o}")

    # Strict
    print("\nSTRICT classification:")
    z1_s, n1_s = test_clustering(data, is_grammar_strict)
    ex_s, nt_s = test_exclusivity(data, is_grammar_strict)
    hd_s, he_s, nh_s = test_hazard_distance(data, is_grammar_strict)
    cv_s, nr_s = test_run_cv(data, is_grammar_strict)

    print(f"  Residue count: {n1_s}")
    print(f"  Clustering z: {z1_s}")
    print(f"  Exclusivity: {ex_s}")
    print(f"  Hazard dist: {hd_s} (expected ~{he_s})")
    print(f"  Run CV: {cv_s}")

    # Compare
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    def pct_change(old, new):
        if old == 0:
            return "N/A"
        return f"{(new - old) / abs(old) * 100:+.1f}%"

    print(f"""
| Metric        | Original | Strict   | Change    |
|---------------|----------|----------|-----------|
| Residue count | {n1_o:,}    | {n1_s:,}    | {pct_change(n1_o, n1_s)} |
| Clustering z  | {z1_o}     | {z1_s}     | {pct_change(z1_o, z1_s)} |
| Exclusivity   | {ex_o}    | {ex_s}    | {pct_change(ex_o, ex_s)} |
| Hazard dist   | {hd_o}     | {hd_s}     | {pct_change(hd_o, hd_s)} |
| Run CV        | {cv_o}      | {cv_s}      | {pct_change(cv_o, cv_s)} |
""")

    # Verdict
    changes = [
        abs((z1_s - z1_o) / z1_o * 100) if z1_o else 0,
        abs((ex_s - ex_o) / ex_o * 100) if ex_o else 0,
        abs((cv_s - cv_o) / cv_o * 100) if cv_o else 0,
    ]
    max_change = max(changes)

    print("=" * 60)
    if max_change < 20:
        print(f"** RESULTS STABLE ** (max change: {max_change:.1f}%)")
        print("Token filtering does NOT significantly affect SID-04 findings.")
    elif max_change < 50:
        print(f"** MINOR CHANGES ** (max change: {max_change:.1f}%)")
    else:
        print(f"** SIGNIFICANT CHANGES ** (max change: {max_change:.1f}%)")
        print("Full audit recommended.")


if __name__ == '__main__':
    main()
