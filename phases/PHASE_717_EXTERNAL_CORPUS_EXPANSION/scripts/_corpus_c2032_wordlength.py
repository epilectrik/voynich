"""PHASE_717 v2: C2032 with word-length-class as target feature.

The most-common-word target (v1) had lag1-instability issues across Latin corpora
(same problem as PHASE_711). Switch to word-length-class: count of characters per
word, grouped into classes (3, 4, 5, 6, 7, 8+). This is robust, well-distributed,
and is the natural analog to Voynich's e-depth-class methodology used in C2032.

Apply uniformly to Voynich Currier B + all reference corpora + new corpora for
apples-to-apples comparison.
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / 'phases' / 'PHASE_717_EXTERNAL_CORPUS_EXPANSION' / 'results' / 'c2032_wordlength.json'

random.seed(42)
N_PERM = 200


def word_length_class(word, min_len=3, max_len=10):
    """Bin word into length class. Returns string label."""
    n = len(word)
    if n < min_len:
        return f'<{min_len}'
    if n >= max_len:
        return f'>={max_len}'
    return str(n)


# ---- Corpus loading ----

def load_latin_text(path, skip_lines=0):
    """Load text, return word list (lowercase alphabetic, len >=3, no extreme repetition)."""
    if not Path(path).exists():
        return None
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    if skip_lines > 0:
        lines = lines[skip_lines:]
    text = '\n'.join(lines).lower()
    words = re.findall(r'[a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]+', text)
    words = [w for w in words if 3 <= len(w) <= 30 and not re.search(r'(.)\1{4,}', w)]
    return words


def load_theophilus_latin_body():
    """Theophilus: take body Latin range per README guide.

    Per README:
    - Front matter: lines 1-1700 (skip)
    - Book I Latin: 2242-?, English: 2278-4283
    - Book I notes: 4315-7212 (skip)
    - Book II Latin: 7213-?, English: 7520-9147
    - Book II notes: 9178-10536 (skip)
    - Book III Latin: 10537-?, English: 11337-20528

    Take Latin-rich line ranges (chapters with both Latin and English mixed are
    accepted; notes excluded).
    """
    path = ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt'
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')

    # Latin-rich ranges per README (excluding notes)
    body_lines = []
    body_lines.extend(lines[2242:4283])   # Book I (Latin + English mix)
    body_lines.extend(lines[7213:9147])   # Book II
    body_lines.extend(lines[10537:11337]) # Book III Latin section (before English chapters)

    body_text = '\n'.join(body_lines).lower()
    words = re.findall(r'[a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]+', body_text)
    words = [w for w in words if 3 <= len(w) <= 30 and not re.search(r'(.)\1{4,}', w)]
    return words


def load_voynich_currier_b():
    """Voynich Currier B P-placement tokens."""
    from scripts.voynich import Transcript
    tx = Transcript()
    folio_words = defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != 'B':
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        folio_words[t.folio].append(t.word.lower())
    return folio_words


# ---- C2032 with word-length class ----

def class_chain_excess(seqs, target_class, lags=(1, 2, 3), n_perm=N_PERM):
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


def chunk_words(words, chunk_size=2000):
    seqs = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if len(chunk) >= 100:
            seqs.append(chunk)
    return seqs


def words_to_length_class_seqs(seqs_of_words):
    """Convert sequences-of-words to sequences-of-length-classes."""
    return [[word_length_class(w) for w in seq] for seq in seqs_of_words]


def compute_c2032_wordlength(words_or_folio_dict, label):
    """Compute C2032 r21 using word-length-class as target.

    words_or_folio_dict: if dict, treat values as per-folio sequences.
                        if list, chunk into seqs of 2000.
    """
    if isinstance(words_or_folio_dict, dict):
        seqs_of_words = [v for v in words_or_folio_dict.values() if len(v) >= 20]
        n_chunks = len(seqs_of_words)
        chunk_label = 'per-folio'
    else:
        seqs_of_words = chunk_words(words_or_folio_dict, chunk_size=2000)
        n_chunks = len(seqs_of_words)
        chunk_label = '2000-word chunks'

    total_words = sum(len(s) for s in seqs_of_words)
    if total_words < 500:
        return {'label': label, 'error': f'too few words: {total_words}'}

    # Convert to length-class sequences
    length_seqs = words_to_length_class_seqs(seqs_of_words)

    # Distribution of length classes
    all_classes = [c for seq in length_seqs for c in seq]
    class_counts = Counter(all_classes)
    total = sum(class_counts.values())

    # Most common length class
    target, target_count = class_counts.most_common(1)[0]
    target_freq = target_count / total

    # Compute chain excess
    chain = class_chain_excess(length_seqs, target, lags=(1, 2, 3), n_perm=N_PERM)
    lag1 = chain[1]['excess']
    lag2 = chain[2]['excess']
    lag3 = chain[3]['excess']
    r21 = lag2 / lag1 if abs(lag1) > 1e-9 else float('nan')

    return {
        'label': label,
        'chunk_method': chunk_label,
        'n_chunks': n_chunks,
        'n_words': total_words,
        'class_distribution': dict(class_counts.most_common()),
        'target_class': target,
        'target_freq': target_freq,
        'lag1_excess': lag1,
        'lag2_excess': lag2,
        'lag3_excess': lag3,
        'r21': r21,
        'chain_results': chain,
    }


def main():
    print("=" * 80)
    print("PHASE_717 v2: C2032 WITH WORD-LENGTH CLASS")
    print("=" * 80)

    results = {}

    # Voynich Currier B (per-folio sequences)
    print("\n[Voynich Currier B]")
    voy_folio_words = load_voynich_currier_b()
    print(f"  N folios: {len(voy_folio_words)}, total tokens: {sum(len(v) for v in voy_folio_words.values())}")
    r = compute_c2032_wordlength(voy_folio_words, 'Voynich Currier B')
    results['Voynich_B'] = r

    # Reference Latin corpora
    print("\n[Codicillus]")
    cod = load_latin_text(ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt')
    if cod:
        r = compute_c2032_wordlength(cod, 'Codicillus')
        results['Codicillus'] = r

    print("\n[Mesue Grabadin]")
    mes = load_latin_text(ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt')
    if mes:
        r = compute_c2032_wordlength(mes, 'Mesue Grabadin')
        results['Mesue'] = r

    print("\n[Brunschwig 1512]")
    brun = load_latin_text(ROOT / 'sources' / 'brunschwig_1512' / 'brunschwig_1512_assembled.txt')
    if brun:
        r = compute_c2032_wordlength(brun, 'Brunschwig 1512')
        results['Brunschwig'] = r

    # New corpora
    print("\n[Theophilus (body, Latin-rich ranges)]")
    theo = load_theophilus_latin_body()
    if theo:
        r = compute_c2032_wordlength(theo, 'Theophilus')
        results['Theophilus'] = r

    print("\n[Rupescissa]")
    rup = load_latin_text(ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt', skip_lines=200)
    if rup:
        r = compute_c2032_wordlength(rup, 'Rupescissa')
        results['Rupescissa'] = r

    print("\n[Pseudo-Lull Testamentum]")
    pl = load_latin_text(ROOT / 'sources' / 'pseudo_lull_testamentum' / 'testamentum_complete_latin.txt')
    if pl:
        r = compute_c2032_wordlength(pl, 'Pseudo-Lull Testamentum')
        results['Pseudo-Lull'] = r

    # ---- Cross-corpus summary ----
    print("\n" + "=" * 80)
    print("CROSS-CORPUS SUMMARY (word-length-class C2032)")
    print("=" * 80)
    print(f"\n{'Corpus':<28}{'n_words':>10}{'n_chunks':>10}{'target':>10}{'freq':>10}{'lag1':>10}{'lag2':>10}{'r21':>10}")
    print("-" * 108)
    for name, r in results.items():
        if 'error' in r:
            print(f"{name:<28}  ERROR")
            continue
        print(f"{r['label']:<28}{r['n_words']:>10}{r['n_chunks']:>10}{r['target_class']:>10}"
              f"{r['target_freq']:>10.1%}{r['lag1_excess']:>+10.4f}{r['lag2_excess']:>+10.4f}"
              f"{r['r21']:>+10.3f}")

    # Comparison
    print("\n" + "=" * 80)
    print("ALIGNMENT ANALYSIS")
    print("=" * 80)

    voy_r21 = results.get('Voynich_B', {}).get('r21', float('nan'))
    print(f"\n  Voynich Currier B r21 (this metric): {voy_r21:+.3f}")
    print(f"\n  Pre-registered alignment criteria:")
    print(f"    Voynich-aligned: |r21 - {voy_r21:+.3f}| < 0.10")
    print(f"    NL-aligned: |r21| < 0.20")
    print(f"    Other: in between")

    print("\n  Per-corpus verdict:")
    for name, r in results.items():
        if 'error' in r or name == 'Voynich_B':
            continue
        r21 = r['r21']
        if abs(r21 - voy_r21) < 0.10:
            verdict = "VOYNICH-ALIGNED (major finding)"
        elif abs(r21) < 0.20:
            verdict = "NL-aligned"
        else:
            verdict = "OTHER"
        delta_voy = r21 - voy_r21
        print(f"    {name}: r21={r21:+.3f}  (Δ vs Voynich = {delta_voy:+.3f})  →  {verdict}")

    # Save
    out = {
        'method': 'PHASE_717 v2 C2032 word-length-class',
        'n_permutations': N_PERM,
        'voynich_r21': voy_r21,
        'results': results,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
