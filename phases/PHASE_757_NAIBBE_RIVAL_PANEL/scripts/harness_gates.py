#!/usr/bin/env python3
"""PHASE_757 harness gates G1 (decipherability) and G2 (reproduces the published generator). No discriminator.

See ../PRE_REGISTRATION.md (locked, commit a5506cb).
"""
from __future__ import annotations

import difflib
import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import naibbe_harness as H  # noqa: E402

OUT = H.ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/results'
OUT.mkdir(parents=True, exist_ok=True)


def load_decrypter():
    spec = importlib.util.spec_from_file_location('naibbe_decrypt', H.NAIBBE_DIR / 'decrypt_naibbe.py')
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    maps = d.build_reverse_mappings(pd.read_csv(H.NAIBBE_DIR / 'references/naibbe_tables.csv'))
    return d, maps


def decrypted_letters(d, maps, tokens):
    out = []
    for tok in tokens:
        r = d.decrypt_naibbe_token(tok, *maps, basic=True)
        if r.startswith('('):
            r = r[1:-1].split('|')[0]
        out.append(r.replace('*', '').replace(' ', '').replace('[?]', ''))
    return ''.join(out)


def g1():
    d, maps = load_decrypter()
    res = {}
    for v in ('GV1', 'GV2'):
        m = H.load_version(v)
        for pid in H.RAW:
            lines = H.plaintext(pid, m)[0]
            fr = []
            for member in range(5):
                random.seed(757_100 + member)
                i0 = random.randrange(len(lines))
                matched = total = 0
                for i in range(i0, i0 + 150):
                    text = lines[i % len(lines)]
                    ct, _ = H.encrypt_line(m, text)
                    rec = decrypted_letters(d, maps, ct)
                    sm = difflib.SequenceMatcher(None, text, rec, autojunk=False)
                    matched += sum(b.size for b in sm.get_matching_blocks())
                    total += len(text)
                fr.append(matched / total)
            res[f'{v}/{pid}'] = {'min_letter_recovery': round(min(fr), 5), 'mean': round(sum(fr) / len(fr), 5),
                                 'pass': min(fr) >= 0.99}
            print(f'G1 {v} {pid}: min recovery {min(fr):.4f}', flush=True)
    return res


def stats(tokens):
    c = Counter(tokens)
    return {'tokens': len(tokens), 'types': len(c), 'ttr': len(c) / len(tokens),
            'hapax_type_fraction': sum(1 for v in c.values() if v == 1) / len(c),
            'mean_token_length': sum(map(len, tokens)) / len(tokens)}


def g2(n_b):
    res = {}
    m2 = H.load_version('GV2')
    pt = H.plaintext('P-NH', m2)
    for sr in (False, True):
        toks, _ = H.gen_stream(m2, pt, 757_200 + sr, n_b, sr)
        st = stats(toks)
        st['pass'] = 0.40 <= st['hapax_type_fraction'] <= 0.60
        res[f'a_GV2_P-NH_SR{3 if sr else 0}'] = st
        print(f"G2a GV2 SR{3 if sr else 0}: {st}", flush=True)
    m1 = H.load_version('GV1')
    theirs = open(H.NAIBBE_DIR / 'encrypted/nathist_output_ciphertext.txt', encoding='utf-8').read().split()
    random.seed(757_300)
    ours = []
    for line in open(H.NAIBBE_DIR / 'input/examples/nathist_book16.txt', encoding='utf-8'):
        cl = m1.clean_line(line)
        if cl:
            ours.extend(H.encrypt_line(m1, cl)[0])
    n = min(len(ours), len(theirs))
    so, st = stats(ours[:n]), stats(theirs[:n])
    rel = {k: abs(so[k] - st[k]) / st[k] for k in ('ttr', 'hapax_type_fraction', 'mean_token_length')}
    res['b_GV1_vs_committed'] = {'ours': so, 'committed': st, 'relative_diff': rel,
                                 'pass': all(x <= 0.10 for x in rel.values())}
    print(f"G2b GV1 vs committed: ours {so} | committed {st} | rel {rel}", flush=True)
    return res


def main():
    skel = H.load_skeleton()
    out = {'G1': g1(), 'G2': g2(skel['n_certain'])}
    out['G1_pass'] = all(r['pass'] for r in out['G1'].values())
    out['G2_pass'] = all(r['pass'] for r in out['G2'].values())
    noise = H.noise_model()
    out['noise_model'] = {k: v for k, v in noise.items() if k != 'edits'}
    json.dump(out, open(OUT / 'harness_gates.json', 'w', encoding='utf-8'), indent=1)
    print(f"G1 pass={out['G1_pass']}  G2 pass={out['G2_pass']}  noise rho={noise['rho']:.4f} "
          f"(disagreement {noise['disagreement_rate']:.4f}, n_edit1={noise['n_edit1']}, types {noise['edit_type_counts']})")


if __name__ == '__main__':
    main()
