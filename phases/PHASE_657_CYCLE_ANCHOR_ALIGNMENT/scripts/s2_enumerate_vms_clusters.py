"""
Phase 657 s2 — VMS Cycle-Cluster Enumerator

Per locked PRE_REGISTRATION.md section 2:
  A homogeneous cluster of size N is a maximal consecutive run of N tokens
  within a single line OR spanning at most one line break, where every
  token shares the same prefix-class.

Locked prefix-class set: qo, ot, ok, ol, or, ch, sh, da, qok, qot
(qok and qot are compound classes, counted in addition to bare qo/qot).

Inclusion: N >= 3.

Output: results/VMS_CYCLE_CLUSTERS.json
"""

import io
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Locked prefix-class set
PREFIX_CLASSES = ['qok', 'qot', 'qo', 'ot', 'ok', 'ol', 'or', 'ch', 'sh', 'da']

# Cluster definitions:
# - "bare" classes (qo, ot, ok, ol, or, ch, sh, da): a token is in class C if
#   its word starts with C AND the next character (if any) is NOT one of
#   the compound extenders. We use simple longest-prefix-match: the token
#   is assigned to the LONGEST matching prefix-class in PREFIX_CLASSES.
# - "compound" classes (qok, qot): a token is in class qok iff word starts
#   with 'qok'; similarly qot iff starts with 'qot'.
#
# Per pre-reg: "qok counted both as qo and as a separate qok class for matching"
# So we enumerate clusters TWICE per token: once at bare-prefix resolution
# (longest match excluding compounds) and once at compound resolution.
# Implementation: build TWO classifications per token.

BARE_PREFIXES = ['qo', 'ot', 'ok', 'ol', 'or', 'ch', 'sh', 'da']
COMPOUND_PREFIXES = ['qok', 'qot']

MIN_CLUSTER_SIZE = 3


def classify_bare(word):
    """Return the longest matching bare prefix or None."""
    for p in sorted(BARE_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            return p
    return None


def classify_compound(word):
    """Return the matching compound prefix or None."""
    for p in COMPOUND_PREFIXES:
        if word.startswith(p):
            return p
    return None


def find_clusters_in_sequence(tokens_with_meta, prefix_class):
    """
    tokens_with_meta: list of (token_index, word, line_number, classification)
    prefix_class: which class to scan for ('qok', 'qo', etc.)

    Returns list of clusters. A cluster is a max consecutive run of tokens
    where classification == prefix_class, with the constraint that the
    cluster spans at most 1 line break.
    """
    clusters = []
    i = 0
    n = len(tokens_with_meta)
    while i < n:
        if tokens_with_meta[i][3] != prefix_class:
            i += 1
            continue
        # Start of a potential cluster
        start = i
        line_breaks_within = 0
        prev_line = tokens_with_meta[i][2]
        j = i + 1
        while j < n:
            cls = tokens_with_meta[j][3]
            cur_line = tokens_with_meta[j][2]
            line_changed = (cur_line != prev_line)
            if line_changed:
                line_breaks_within += 1
                if line_breaks_within > 1:
                    break  # cluster cannot span more than 1 line break
            if cls != prefix_class:
                break
            prev_line = cur_line
            j += 1
        size = j - start
        if size >= MIN_CLUSTER_SIZE:
            cluster_tokens = tokens_with_meta[start:j]
            clusters.append({
                'size': size,
                'line_start': cluster_tokens[0][2],
                'line_end': cluster_tokens[-1][2],
                'tokens': [t[1] for t in cluster_tokens],
                'token_indices': [t[0] for t in cluster_tokens],
            })
        i = j
    return clusters


def enumerate_folio_clusters(folio_tokens):
    """
    folio_tokens: list of Token objects (Currier B, H-only, no labels)
    Returns dict: {prefix_class: [cluster_dict, ...]}
    """
    if not folio_tokens:
        return {}

    # Build (idx, word, line_number, bare_class, compound_class)
    seq = []
    for idx, t in enumerate(folio_tokens):
        word = t.word
        if not word:
            continue
        bare = classify_bare(word)
        comp = classify_compound(word)
        # Convert line number to int if possible
        try:
            line_num = int(t.line)
        except (ValueError, TypeError):
            line_num = t.line  # fallback to string
        seq.append((idx, word, line_num, bare, comp))

    out = defaultdict(list)

    # Bare classes
    for cls in BARE_PREFIXES:
        # Use bare classification (slot 3)
        subseq = [(i, w, ln, b) for (i, w, ln, b, c) in seq]
        clusters = find_clusters_in_sequence(subseq, cls)
        if clusters:
            out[cls] = clusters

    # Compound classes (use slot 4 = compound class)
    for cls in COMPOUND_PREFIXES:
        subseq = [(i, w, ln, c) for (i, w, ln, b, c) in seq]
        clusters = find_clusters_in_sequence(subseq, cls)
        if clusters:
            out[cls] = clusters

    return dict(out)


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_657_CYCLE_ANCHOR_ALIGNMENT' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('loading Currier B tokens...')
    tx = Transcript()
    # Currier B, H-only, no labels, no uncertain
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        by_folio[tok.folio].append(tok)
    print(f'  folios with Currier B tokens: {len(by_folio)}')
    total = sum(len(v) for v in by_folio.values())
    print(f'  total tokens: {total}')

    folio_clusters = {}
    for folio, toks in sorted(by_folio.items()):
        folio_clusters[folio] = enumerate_folio_clusters(toks)

    # Summary stats
    n_folios_with_any = sum(1 for c in folio_clusters.values() if c)
    print(f'  folios with >=1 cluster (any class, N>=3): {n_folios_with_any}')

    # Cluster size distribution per class
    print()
    print('Cluster-size distribution per prefix class:')
    print(f'{"class":>6}  {"N3":>5} {"N4":>5} {"N5":>5} {"N6":>5} {"N7":>5} {"N8":>5} {"N9":>5} {"N10+":>5}')
    for cls in PREFIX_CLASSES:
        bins = [0, 0, 0, 0, 0, 0, 0, 0]  # 3,4,5,6,7,8,9,10+
        for f, classes in folio_clusters.items():
            for cluster in classes.get(cls, []):
                s = cluster['size']
                if s == 3: bins[0] += 1
                elif s == 4: bins[1] += 1
                elif s == 5: bins[2] += 1
                elif s == 6: bins[3] += 1
                elif s == 7: bins[4] += 1
                elif s == 8: bins[5] += 1
                elif s == 9: bins[6] += 1
                else: bins[7] += 1
        print(f'{cls:>6}  ' + ' '.join(f'{b:>5}' for b in bins))

    # Highlight pre-registered key folios
    print()
    print('Pre-registered key folios:')
    for folio in ['f75r', 'f112r', 'f82v']:
        clusters = folio_clusters.get(folio, {})
        if not clusters:
            print(f'  {folio}: NO clusters >= 3')
            continue
        for cls, cs in clusters.items():
            for c in cs:
                print(f'  {folio}  {cls}-cluster size={c["size"]}  '
                      f'L{c["line_start"]}-L{c["line_end"]}: '
                      f'{c["tokens"][:6]}{"..." if len(c["tokens"]) > 6 else ""}')

    out_path = out_dir / 'VMS_CYCLE_CLUSTERS.json'
    out_path.write_text(json.dumps({
        'phase': 657,
        'stage': 'B',
        'script': 's2',
        'pre_registration_commit': '7227532',
        'min_cluster_size': MIN_CLUSTER_SIZE,
        'prefix_classes': PREFIX_CLASSES,
        'bare_prefixes': BARE_PREFIXES,
        'compound_prefixes': COMPOUND_PREFIXES,
        'folio_count': len(folio_clusters),
        'folios': folio_clusters,
    }, indent=2), encoding='utf-8')
    print(f'\nwrote {out_path}')


if __name__ == '__main__':
    main()
