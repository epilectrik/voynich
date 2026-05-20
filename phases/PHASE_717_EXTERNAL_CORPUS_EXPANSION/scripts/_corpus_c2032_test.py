"""PHASE_717: Apply C2032 lag2/lag1 chain-rate-excess to new external corpora.

Test whether the substrate-quintet "non-NL" framing holds across additional
medieval procedural Latin corpora not yet tested at this level.

Corpora:
  - Theophilus De Diversis Artibus (~1120, metalwork/glass/pigments)
  - Rupescissa Quintae Essentiae (~1351, distillation/alchemy)
  - Pseudo-Lull Testamentum (full corpus, not just Codicillus)

Methodology matches existing phases (MENSURAL_NOTATION_HYPOTHESIS triad measurement,
PHASE_709 atom-scale test): build per-document sequences, pick most-common word as
target class, compute chain-rate-excess at lag 1/2/3 with within-document shuffle null.
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / 'phases' / 'PHASE_717_EXTERNAL_CORPUS_EXPANSION' / 'results' / 'c2032_external_corpus.json'

random.seed(42)
N_PERM = 200


# ---- Corpus loading ----

def load_text_filtered(path, skip_lines=0, max_words=None):
    """Load text from file, filter to lowercase alphabetic words ≥3 chars."""
    if not Path(path).exists():
        return None
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    if skip_lines > 0:
        lines = lines[skip_lines:]
    text = '\n'.join(lines).lower()
    # Latin: just alphabetic chars including æ/œ/à/é/etc.
    words = re.findall(r'[a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]+', text)
    # Filter: length ≥3, no extreme repetition (>10 same chars)
    words = [w for w in words if 3 <= len(w) <= 30 and not re.search(r'(.)\1{4,}', w)]
    if max_words and len(words) > max_words:
        words = words[:max_words]
    return words


def load_theophilus_latin_only():
    """Extract Latin Theophilus content (skip front matter + English notes per README)."""
    path = ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt'
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    # Per README: Latin chunks at L2242-?, L7213-?, L10537-?
    # Skip front matter (1-1700), keep Books I+II+III Latin sections
    # We can't easily separate Latin from English in the same file, so just skip front matter
    # and accept some English contamination. Many words will be Latin.
    body_lines = lines[1700:20528]  # Excludes end matter
    body_text = '\n'.join(body_lines).lower()
    words = re.findall(r'[a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]+', body_text)
    words = [w for w in words if 3 <= len(w) <= 30 and not re.search(r'(.)\1{4,}', w)]
    return words


def load_rupescissa():
    """Rupescissa Latin 1561 — skip title page front matter."""
    path = ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt'
    return load_text_filtered(path, skip_lines=200)


def load_pseudo_lull_testamentum():
    """Pseudo-Lull Testamentum — full Latin (includes Codicillus + other parts)."""
    path = ROOT / 'sources' / 'pseudo_lull_testamentum' / 'testamentum_complete_latin.txt'
    return load_text_filtered(path)


def load_codicillus_for_reference():
    """Existing baseline for reference."""
    path = ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'
    return load_text_filtered(path)


def load_mesue_for_reference():
    path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'
    return load_text_filtered(path)


# ---- C2032 methodology (matches MENSURAL_NOTATION_HYPOTHESIS/_triad_measurement.py) ----

def class_chain_excess(seqs, target_class, lags=(1, 2, 3), n_perm=N_PERM):
    """Chain rate of target_class at given lags, with within-seq shuffle null."""
    out = {}
    for lag in lags:
        obs_hits = 0
        obs_pairs = 0
        for seq in seqs:
            for i in range(len(seq) - lag):
                if seq[i] == target_class:
                    obs_pairs += 1
                    if seq[i + lag] == target_class:
                        obs_hits += 1
        obs_rate = obs_hits / obs_pairs if obs_pairs else 0.0
        null_rates = []
        for _ in range(n_perm):
            null_hits = 0
            null_pairs = 0
            for seq in seqs:
                perm = seq.copy()
                random.shuffle(perm)
                for i in range(len(perm) - lag):
                    if perm[i] == target_class:
                        null_pairs += 1
                        if perm[i + lag] == target_class:
                            null_hits += 1
            null_rates.append(null_hits / null_pairs if null_pairs else 0.0)
        null_rate = sum(null_rates) / len(null_rates)
        out[lag] = {
            "n_pairs": obs_pairs,
            "obs_rate": obs_rate,
            "null_rate": null_rate,
            "excess": obs_rate - null_rate,
        }
    return out


def chunk_into_sequences(words, chunk_size=1000):
    """Chunk word list into sequences of ~chunk_size words each."""
    seqs = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if len(chunk) >= 50:
            seqs.append(chunk)
    return seqs


def compute_c2032(words, label, chunk_size=1000):
    """Compute C2032 lag2/lag1 r21 metric for a word list."""
    if not words or len(words) < 500:
        return {'label': label, 'error': f'too few words: {len(words) if words else 0}'}

    # Build per-chunk sequences
    seqs = chunk_into_sequences(words, chunk_size=chunk_size)
    n_chunks = len(seqs)
    total_words = sum(len(s) for s in seqs)

    # Get most-common word as target class
    counter = Counter(words)
    target, target_count = counter.most_common(1)[0]
    target_freq = target_count / len(words)

    # Vocab size and entropy
    vocab_size = len(counter)
    import math
    total = sum(counter.values())
    entropy = -sum((c / total) * math.log2(c / total) for c in counter.values() if c > 0)

    # Compute chain excess
    chain = class_chain_excess(seqs, target, lags=(1, 2, 3), n_perm=N_PERM)
    lag1 = chain[1]['excess']
    lag2 = chain[2]['excess']
    lag3 = chain[3]['excess']
    r21 = lag2 / lag1 if abs(lag1) > 1e-9 else float('nan')
    r31 = lag3 / lag1 if abs(lag1) > 1e-9 else float('nan')

    return {
        'label': label,
        'n_words': total_words,
        'n_chunks': n_chunks,
        'chunk_size': chunk_size,
        'vocab_size': vocab_size,
        'entropy_bpc': entropy,
        'target_class': target,
        'target_count': target_count,
        'target_freq': target_freq,
        'lag1_excess': lag1,
        'lag2_excess': lag2,
        'lag3_excess': lag3,
        'r21': r21,
        'r31': r31,
        'chain_results': chain,
    }


def main():
    print("=" * 80)
    print("PHASE_717 EXTERNAL CORPUS C2032 EXPANSION")
    print("=" * 80)

    # Load corpora
    corpora = {}
    print("\nLoading corpora...")

    print("  Theophilus...")
    theo = load_theophilus_latin_only()
    if theo:
        corpora['Theophilus'] = theo
        print(f"    {len(theo)} alphabetic words (filtered)")

    print("  Rupescissa...")
    rup = load_rupescissa()
    if rup:
        corpora['Rupescissa'] = rup
        print(f"    {len(rup)} alphabetic words (filtered)")

    print("  Pseudo-Lull Testamentum...")
    pl = load_pseudo_lull_testamentum()
    if pl:
        corpora['Pseudo-Lull Testamentum'] = pl
        print(f"    {len(pl)} alphabetic words (filtered)")

    print("  Codicillus (reference)...")
    cod = load_codicillus_for_reference()
    if cod:
        corpora['Codicillus (ref)'] = cod
        print(f"    {len(cod)} alphabetic words (filtered)")

    print("  Mesue (reference)...")
    mes = load_mesue_for_reference()
    if mes:
        corpora['Mesue (ref)'] = mes
        print(f"    {len(mes)} alphabetic words (filtered)")

    # Run C2032 on each
    print("\n" + "=" * 80)
    print("C2032 RESULTS (chunk_size=1000)")
    print("=" * 80)
    print(f"\n{'Corpus':<28}{'n_words':>10}{'vocab':>10}{'H_bpc':>9}{'target':<14}{'lag1':>9}{'lag2':>9}{'r21':>9}")
    print("-" * 100)

    results = {}
    for name, words in corpora.items():
        r = compute_c2032(words, name)
        results[name] = r
        if 'error' in r:
            print(f"{name:<28}  ERROR: {r['error']}")
            continue
        target_display = f'{r["target_class"][:10]}({r["target_freq"]:.1%})'
        print(f"{name:<28}{r['n_words']:>10}{r['vocab_size']:>10}{r['entropy_bpc']:>9.2f}"
              f"{target_display:<14}{r['lag1_excess']:>+9.4f}{r['lag2_excess']:>+9.4f}{r['r21']:>+9.3f}")

    # ---- Comparison with known references ----
    print("\n" + "=" * 80)
    print("COMPARISON WITH ESTABLISHED REFERENCES")
    print("=" * 80)
    print(f"\n  Voynich Section B (known): r21 = -0.66 (period-2 signature)")
    print(f"  Mensural notation (known): r21 = +0.18 (NL-like)")
    print(f"  Codicillus (known): r21 ≈ -0.22")
    print(f"  Mesue (known): r21 ≈ -0.17")
    print(f"\n  Pre-registered alignment criterion:")
    print(f"    Voynich-aligned: |r21 - (-0.66)| < 0.10")
    print(f"    NL-aligned: |r21| < 0.30")
    print(f"    Mensural-aligned: r21 > +0.10")

    # Identify alignments
    print("\n  New corpus alignments:")
    for name, r in results.items():
        if 'error' in r:
            continue
        if name in ('Codicillus (ref)', 'Mesue (ref)'):
            continue  # skip references
        r21 = r['r21']
        if abs(r21 + 0.66) < 0.10:
            verdict = "VOYNICH-ALIGNED (major finding)"
        elif abs(r21) < 0.30:
            verdict = "NL-aligned (adds to non-NL evidence for Voynich)"
        elif r21 > 0.10:
            verdict = "Mensural-aligned"
        else:
            verdict = f"OTHER (r21={r21:+.3f})"
        print(f"    {name}: r21={r21:+.3f}  →  {verdict}")

    # ---- Save ----
    out = {
        'method': 'PHASE_717 external corpus C2032 expansion',
        'n_permutations': N_PERM,
        'chunk_size': 1000,
        'results': results,
        'reference_values': {
            'voynich_section_b': -0.66,
            'mensural': 0.18,
            'codicillus_known': -0.22,
            'mesue_known': -0.17,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
