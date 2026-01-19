"""
SID-04: Human-State Compatibility Analysis (SAMPLED VERSION)

Uses sampling to handle large corpus efficiently.
TIER 4: Speculative compatibility only
"""

import sys
import math
import random
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, r'C:\git\voynich')

# Grammar patterns
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

HAZARD_TOKENS = {'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey',
                 'l', 'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol',
                 'ol', 'shor', 'dar', 'qokaiin', 'qokedy'}


def load_data_fast():
    """Fast load with early termination."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    sections = []

    with open(filepath, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 4:
                # Filter to H (PRIMARY) transcriber track only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').lower()
                section = parts[3].strip('"')
                if word and not word.startswith('*'):
                    tokens.append(word)
                    sections.append(section)

    return tokens, sections


def is_grammar(t):
    for p in GRAMMAR_PREFIXES:
        if t.startswith(p): return True
    for s in GRAMMAR_SUFFIXES:
        if t.endswith(s): return True
    return False


def classify(tokens):
    residue = []
    res_pos = []
    for i, t in enumerate(tokens):
        if not is_grammar(t):
            residue.append(t)
            res_pos.append(i)
    return residue, res_pos


def main():
    print("=" * 60)
    print("SID-04: HUMAN-STATE COMPATIBILITY (SAMPLED)")
    print("=" * 60)
    print()

    random.seed(42)
    np.random.seed(42)

    # Load
    print("Loading data...")
    tokens, sections = load_data_fast()
    print(f"  Total tokens: {len(tokens)}")

    residue, res_pos = classify(tokens)
    res_sections = [sections[i] for i in res_pos]
    print(f"  Residue tokens: {len(residue)}")
    print(f"  Residue types: {len(set(residue))}")
    print()

    # Sample for faster tests
    SAMPLE_SIZE = 5000
    if len(residue) > SAMPLE_SIZE:
        indices = sorted(random.sample(range(len(residue)), SAMPLE_SIZE))
        sample_residue = [residue[i] for i in indices]
        sample_sections = [res_sections[i] for i in indices]
        sample_pos = [res_pos[i] for i in indices]
        print(f"  Using sample of {SAMPLE_SIZE} tokens for tests")
    else:
        sample_residue = residue
        sample_sections = res_sections
        sample_pos = res_pos
    print()

    results = []

    # TEST 1: Temporal Autocorrelation
    print("Test 1: TEMPORAL AUTOCORRELATION")
    self_rate = sum(1 for i in range(len(sample_residue)-1)
                    if sample_residue[i] == sample_residue[i+1]) / (len(sample_residue)-1)

    # Null: shuffle
    null_rates = []
    for _ in range(30):
        shuf = sample_residue.copy()
        random.shuffle(shuf)
        null_rates.append(sum(1 for i in range(len(shuf)-1) if shuf[i] == shuf[i+1]) / (len(shuf)-1))

    z = (self_rate - np.mean(null_rates)) / np.std(null_rates) if np.std(null_rates) > 0 else 0
    v1 = 'CONSISTENT' if z > 2 else ('WEAK' if z > 1 else 'INCONSISTENT')
    print(f"  Self-rate: {self_rate:.4f}, null: {np.mean(null_rates):.4f}, z={z:.2f}")
    print(f"  Verdict: {v1}")
    results.append(v1)
    print()

    # TEST 2: Section Exclusivity
    print("Test 2: SECTION EXCLUSIVITY")
    type_sects = defaultdict(set)
    for t, s in zip(sample_residue, sample_sections):
        type_sects[t].add(s)
    excl = sum(1 for sects in type_sects.values() if len(sects) == 1) / len(type_sects)

    # Null: shuffle sections
    null_excl = []
    for _ in range(30):
        shuf_s = sample_sections.copy()
        random.shuffle(shuf_s)
        ts = defaultdict(set)
        for t, s in zip(sample_residue, shuf_s):
            ts[t].add(s)
        null_excl.append(sum(1 for sects in ts.values() if len(sects) == 1) / len(ts))

    z2 = (excl - np.mean(null_excl)) / np.std(null_excl) if np.std(null_excl) > 0 else 0
    v2 = 'CONSISTENT' if z2 > 2 else ('WEAK' if z2 > 1 else 'INCONSISTENT')
    print(f"  Exclusivity: {excl:.3f}, null: {np.mean(null_excl):.3f}, z={z2:.2f}")
    print(f"  Verdict: {v2}")
    results.append(v2)
    print()

    # TEST 3: Hazard Proximity
    print("Test 3: HAZARD PROXIMITY")
    haz_pos = [i for i, t in enumerate(tokens) if t in HAZARD_TOKENS]

    if len(haz_pos) > 10:
        dists = [min(abs(p - h) for h in haz_pos) for p in sample_pos[:1000]]
        mean_dist = np.mean(dists)

        # Null: random positions
        null_dists = []
        for _ in range(30):
            rnd_pos = random.sample(range(len(tokens)), min(1000, len(sample_pos)))
            null_dists.append(np.mean([min(abs(p - h) for h in haz_pos) for p in rnd_pos]))

        z3 = (mean_dist - np.mean(null_dists)) / np.std(null_dists) if np.std(null_dists) > 0 else 0
        v3 = 'CONSISTENT' if z3 > 1.5 else 'INCONSISTENT'
        print(f"  Mean dist: {mean_dist:.2f}, null: {np.mean(null_dists):.2f}, z={z3:.2f}")
        print(f"  Verdict: {v3}")
    else:
        v3 = 'INSUFFICIENT_DATA'
        print(f"  Verdict: {v3}")
    results.append(v3)
    print()

    # TEST 4: Run Lengths
    print("Test 4: RUN LENGTHS")
    runs = []
    curr_t, curr_len = None, 0
    for t in sample_residue:
        if t == curr_t:
            curr_len += 1
        else:
            if curr_len > 0: runs.append(curr_len)
            curr_t, curr_len = t, 1
    if curr_len > 0: runs.append(curr_len)

    mean_run = np.mean(runs)
    cv = np.std(runs) / mean_run if mean_run > 0 else 0
    p_geom = 1 / mean_run if mean_run > 0 else 1
    exp_cv = math.sqrt(1-p_geom)/p_geom if p_geom < 1 else 1
    cv_ratio = cv / exp_cv if exp_cv > 0 else 0

    v4 = 'CONSISTENT' if 0.7 < cv_ratio < 1.3 else 'INCONSISTENT'
    print(f"  Mean run: {mean_run:.2f}, CV: {cv:.3f}, expected: {exp_cv:.3f}")
    print(f"  CV ratio: {cv_ratio:.3f}, Verdict: {v4}")
    results.append(v4)
    print()

    # TEST 5: Boundary Asymmetry
    print("Test 5: BOUNDARY ASYMMETRY")
    bounds = [i for i in range(1, len(sections)) if sections[i] != sections[i-1]]
    res_set = set(res_pos)

    if len(bounds) >= 5:
        entry = sum(1 for b in bounds for i in range(b, min(len(tokens), b+5)) if i in res_set)
        exit_ = sum(1 for b in bounds for i in range(max(0, b-5), b) if i in res_set)
        asym = (entry - exit_) / (entry + exit_) if (entry + exit_) > 0 else 0

        # Null
        null_asym = []
        for _ in range(30):
            null_set = set(random.sample(range(len(tokens)), len(res_pos)))
            ne = sum(1 for b in bounds for i in range(b, min(len(tokens), b+5)) if i in null_set)
            nx = sum(1 for b in bounds for i in range(max(0, b-5), b) if i in null_set)
            if ne + nx > 0:
                null_asym.append((ne - nx) / (ne + nx))

        z5 = (asym - np.mean(null_asym)) / np.std(null_asym) if np.std(null_asym) > 0 else 0
        v5 = 'CONSISTENT' if abs(z5) > 2 else 'INCONSISTENT'
        print(f"  Entry: {entry}, Exit: {exit_}, Asymmetry: {asym:.3f}, z={z5:.2f}")
        print(f"  Verdict: {v5}")
    else:
        v5 = 'INSUFFICIENT_DATA'
        print(f"  Verdict: {v5}")
    results.append(v5)
    print()

    # TEST 6: Synthetic Model
    print("Test 6: SYNTHETIC MODEL FIT")
    obs_autocorr = sum(1 for i in range(len(sample_residue)-1)
                       if sample_residue[i] == sample_residue[i+1]) / (len(sample_residue)-1)

    # Build section emissions
    sect_counts = defaultdict(Counter)
    for t, s in zip(sample_residue, sample_sections):
        sect_counts[s][t] += 1
    sect_probs = {}
    for s, c in sect_counts.items():
        tot = sum(c.values())
        sect_probs[s] = {t: n/tot for t, n in c.items()}

    # Generate
    matches = []
    for _ in range(20):
        synth = []
        state = random.random()
        for s in sample_sections:
            state = 0.7 * state + 0.3 * random.random()
            if s in sect_probs:
                toks = list(sect_probs[s].keys())
                probs = [sect_probs[s][t] for t in toks]
                synth.append(random.choices(toks, weights=probs)[0])
            else:
                synth.append(random.choice(sample_residue))

        syn_auto = sum(1 for i in range(len(synth)-1) if synth[i] == synth[i+1]) / (len(synth)-1)
        matches.append(abs(syn_auto / obs_autocorr - 1) if obs_autocorr > 0 else 0)

    avg_dev = np.mean(matches)
    v6 = 'CONSISTENT' if avg_dev < 0.3 else ('WEAK' if avg_dev < 0.5 else 'INCONSISTENT')
    print(f"  Avg deviation from observed: {avg_dev:.3f}")
    print(f"  Verdict: {v6}")
    results.append(v6)
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()

    consistent = sum(1 for v in results if 'CONSISTENT' in v and v != 'INCONSISTENT')
    print(f"Tests consistent: {consistent}/6")
    print()

    for i, (name, v) in enumerate(zip(
        ['AUTOCORRELATION', 'SECTION_EXCLUSIVITY', 'HAZARD_PROXIMITY',
         'RUN_LENGTHS', 'BOUNDARY_ASYMMETRY', 'SYNTHETIC_MODEL'], results)):
        print(f"  {name}: {v}")

    print()
    if consistent >= 4:
        print("OVERALL: COMPATIBLE with non-encoding human-state model")
    elif consistent >= 2:
        print("OVERALL: PARTIALLY COMPATIBLE")
    else:
        print("OVERALL: INCOMPATIBLE")

    print()
    print("LIMITS: Tokens do NOT encode states. Compatibility != explanation.")
    print()
    print("=" * 60)
    print("SID-04 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
