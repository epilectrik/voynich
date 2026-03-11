"""T0: Data Assembly for Phase 581.

Load all Currier B tokens with line position, atom decomposition,
hazard class, category, section, pseudo-HEAD, and carryover class.
"""
import json, os, sys
from collections import defaultdict, Counter

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))
sys.path.insert(0, ROOT)

from scripts.voynich import (Transcript, Morphology, CategoryClassifier,
                              decompose_middle_hmt)

DECODER_PATH = os.path.join(ROOT, 'data', 'decoder_maps.json')

# Pseudo-HEAD domains for headless tokens (C1488-C1493)
PSEUDO_HEAD_DOMAIN = {
    'd': 'CONTAIN', 'i': 'STAGE', 'p': 'MARK',
    'f': 'MARK', 'r': 'FLOW', 'c': 'OPER', 'l': 'STAGE',
    's': 'STAGE', 'g': 'TRANS',
}

# Carryover classes from C1208
CARRYOVER_CLASS = {
    # POSITIVE (z > 2)
    'm': 'POSITIVE', 'a': 'POSITIVE', 'p': 'POSITIVE', 't': 'POSITIVE',
    'h': 'POSITIVE', 'k': 'POSITIVE', 'c': 'POSITIVE', 'r': 'POSITIVE',
    's': 'POSITIVE',
    # NEGATIVE (z < -2)
    'i': 'NEGATIVE', 'y': 'NEGATIVE', 'e': 'NEGATIVE', 'n': 'NEGATIVE',
    # NEUTRAL
    'f': 'NEUTRAL', 'o': 'NEUTRAL', 'd': 'NEUTRAL', 'l': 'NEUTRAL',
    'q': 'NEUTRAL',
}


def load_frame_hazard_map():
    """Load frame hazard map from decoder_maps.json."""
    with open(DECODER_PATH) as f:
        dm = json.load(f)
    fh = dm['maps']['frame_hazard']['entries']
    return {k: v['value'] for k, v in fh.items()}


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    frame_map = load_frame_hazard_map()

    # Group tokens by (folio, line)
    line_groups = defaultdict(list)
    skipped_labels = 0
    skipped_uncertain = 0
    skipped_empty = 0

    for token in tx.currier_b():
        if token.placement.startswith('L'):
            skipped_labels += 1
            continue
        if '*' in token.word:
            skipped_uncertain += 1
            continue
        w = token.word.strip()
        if not w:
            skipped_empty += 1
            continue
        line_key = (token.folio, token.line)
        line_groups[line_key].append(token)

    # Process each line
    all_tokens = []
    skipped_short_lines = 0
    skipped_no_middle = 0

    for line_key, tokens in sorted(line_groups.items()):
        line_len = len(tokens)
        if line_len < 3:
            skipped_short_lines += 1
            continue

        for idx, tok in enumerate(tokens):
            frac_pos = idx / (line_len - 1)
            quintile = min(int(frac_pos * 5), 4)

            w = tok.word.strip()
            m = morph.extract(w)
            if not m.middle:
                skipped_no_middle += 1
                continue

            head, mods, term, frame_str = decompose_middle_hmt(m.middle)

            # Hazard class
            if head == 'k':
                hazard_class = 'IMMUNE'
            elif frame_str:
                hazard_class = frame_map.get(frame_str, 'LOW')
            else:
                hazard_class = 'LOW'

            # Category
            cat = cc.classify(m.middle)

            # Pseudo-HEAD for headless tokens
            pseudo_head = None
            pseudo_head_dom = None
            if head is None and m.middle:
                pseudo_head = m.middle[0]
                pseudo_head_dom = PSEUDO_HEAD_DOMAIN.get(pseudo_head)

            # Carryover class for HEAD atom (or pseudo-head if headless)
            head_carryover = CARRYOVER_CLASS.get(head) if head else None
            term_carryover = CARRYOVER_CLASS.get(term) if term != 'bare' else CARRYOVER_CLASS.get('bare', 'NEUTRAL')

            all_tokens.append({
                'word': w,
                'folio': tok.folio,
                'line_key': f"{tok.folio}_{tok.line}",
                'position_in_line': idx,
                'line_length': line_len,
                'frac_pos': round(frac_pos, 4),
                'quintile': quintile,
                'middle': m.middle,
                'prefix': m.prefix,
                'head': head,
                'mods': mods,
                'term': term,
                'frame_str': frame_str,
                'hazard_class': hazard_class,
                'category': cat,
                'section': tok.section,
                'pseudo_head': pseudo_head,
                'pseudo_head_domain': pseudo_head_dom,
                'head_carryover': head_carryover,
                'term_carryover': term_carryover,
            })

    n = len(all_tokens)

    # Summary statistics
    quintile_counts = Counter(t['quintile'] for t in all_tokens)
    head_counts = Counter(t['head'] if t['head'] else 'headless' for t in all_tokens)
    term_counts = Counter(t['term'] for t in all_tokens)
    section_counts = Counter(t['section'] for t in all_tokens)
    hazard_counts = Counter(t['hazard_class'] for t in all_tokens)
    pseudo_head_counts = Counter(t['pseudo_head'] for t in all_tokens if t['pseudo_head'])

    output = {
        'metadata': {
            'phase': '581',
            'script': 't0_data_assembly.py',
            'n_tokens': n,
            'n_lines': len([k for k, v in line_groups.items() if len(v) >= 3]),
        },
        'tokens': all_tokens,
        'summary': {
            'quintile_counts': dict(sorted(quintile_counts.items())),
            'head_counts': dict(sorted(head_counts.items(), key=lambda x: -x[1])),
            'term_counts': dict(sorted(term_counts.items(), key=lambda x: -x[1])),
            'section_counts': dict(sorted(section_counts.items(), key=lambda x: -x[1])),
            'hazard_counts': dict(sorted(hazard_counts.items(), key=lambda x: -x[1])),
            'pseudo_head_counts': dict(sorted(pseudo_head_counts.items(), key=lambda x: -x[1])),
        },
        'quality': {
            'skipped_labels': skipped_labels,
            'skipped_uncertain': skipped_uncertain,
            'skipped_empty': skipped_empty,
            'skipped_short_lines': skipped_short_lines,
            'skipped_no_middle': skipped_no_middle,
        },
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, 't0_data_assembly.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T0: Data assembly complete")
    print(f"  Total tokens: {n}")
    print(f"  Lines: {output['metadata']['n_lines']}")
    print(f"  Quintile counts: {dict(sorted(quintile_counts.items()))}")
    print(f"  HEAD counts: {dict(sorted(head_counts.items(), key=lambda x: -x[1]))}")
    print(f"  TERMINAL counts: {dict(sorted(term_counts.items(), key=lambda x: -x[1]))}")
    print(f"  Section counts: {dict(sorted(section_counts.items(), key=lambda x: -x[1]))}")
    print(f"  Hazard counts: {dict(sorted(hazard_counts.items(), key=lambda x: -x[1]))}")
    print(f"  Pseudo-HEAD counts: {dict(sorted(pseudo_head_counts.items(), key=lambda x: -x[1]))}")
    print(f"  Quality: {output['quality']}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
