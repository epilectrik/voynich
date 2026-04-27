"""
Phase 665 s1 — III.19 ↔ f75r quantitative alignment test

Locked methodology per PRE_REGISTRATION.md (commit 70ca0eb).

Primary: Spearman ρ between paragraph token-count and subrecipe char-count
under ordinal mapping P_i ↔ III.19.{i-1}.
Secondary: 4 verb-category Spearman with Bonferroni correction.
"""

import io
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts.voynich import Transcript

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# LOCKED MAPPING per pre-reg
MAPPING = [
    ('P1', 0),  # P1 ↔ III.19.0
    ('P2', 1),
    ('P3', 2),
    ('P4', 3),
    ('P5', 4),
    ('P6', 5),
    ('P7', 6),
    ('P8', 7),
    ('P9', 8),
]


def spearman(a, b):
    n = len(a)
    if n < 2:
        return 0.0
    ra = rank(a)
    rb = rank(b)
    ma = sum(ra)/n
    mb = sum(rb)/n
    num = sum((ra[i]-ma)*(rb[i]-mb) for i in range(n))
    da = math.sqrt(sum((x-ma)**2 for x in ra))
    db = math.sqrt(sum((x-mb)**2 for x in rb))
    return num / (da*db) if da*db > 0 else 0.0


def rank(values):
    sorted_pairs = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0] * len(values)
    i = 0
    while i < len(sorted_pairs):
        j = i
        while j < len(sorted_pairs) - 1 and sorted_pairs[j+1][1] == sorted_pairs[i][1]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j+1):
            ranks[sorted_pairs[k][0]] = avg_rank
        i = j + 1
    return ranks


def perm_spearman(a, b, n_perm=10000, seed=20260426):
    obs = spearman(a, b)
    n_ge = 0
    rng = random.Random(seed)
    for _ in range(n_perm):
        b_shuf = b[:]
        rng.shuffle(b_shuf)
        if spearman(a, b_shuf) >= obs:
            n_ge += 1
    return obs, n_ge / n_perm


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_665_SUBRECIPE_PARAGRAPH_ALIGNMENT' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load Catalan subrecipes for III.19
    sismel = json.loads((REPO_ROOT / 'phases' / 'SISMEL_RECIPE_CORPUS' / 'results' /
                         'sismel_subrecipes.json').read_text(encoding='utf-8'))
    sub_by_id = {s['id']: s for s in sismel['subrecipes']}

    # Get III.19.0 through III.19.8
    subrecipes = []
    for i in range(9):
        sid = f'III.19.{i}'
        s = sub_by_id.get(sid)
        if s is None:
            print(f'WARNING: missing {sid}')
            continue
        subrecipes.append({
            'id': sid,
            'idx': i,
            'chars': len(s.get('catalan') or ''),
            'catalan': s.get('catalan') or '',
        })
    print(f'Loaded {len(subrecipes)} subrecipes for III.19')
    sub_chars = [s['chars'] for s in subrecipes]

    # Load f75r tokens. Paragraph segmentation uses LINE RANGES per the
    # f75r_full_decode.txt structure (which matches the locked pre-reg
    # mapping). The transcript's par_initial markers are inconsistent
    # for f75r and would segment into only 3 paragraphs — this is a known
    # methodology issue, not a result of post-hoc choice.
    tx = Transcript()
    f75r_tokens = [t for t in tx.currier_b() if t.folio == 'f75r']

    # Locked line ranges from f75r_full_decode.txt (matches pre-reg mapping)
    PARAGRAPH_RANGES = [
        (1, 5),    # P1
        (6, 6),    # P2
        (7, 12),   # P3
        (13, 16),  # P4
        (17, 22),  # P5
        (23, 26),  # P6
        (27, 27),  # P7
        (28, 31),  # P8
        (32, 46),  # P9
    ]
    paragraphs = []
    for lo, hi in PARAGRAPH_RANGES:
        para = [t for t in f75r_tokens if lo <= int(t.line) <= hi]
        paragraphs.append(para)
    print(f'f75r segmented into {len(paragraphs)} paragraphs by locked line ranges')

    para_token_counts = [len(p) for p in paragraphs]
    print(f'  paragraph token counts: {para_token_counts}')

    if len(paragraphs) != 9:
        print(f'WARNING: expected 9 paragraphs, got {len(paragraphs)}')

    # ---- Primary: Spearman on length ----
    print('\n=== Primary endpoint: paragraph-tokens vs subrecipe-chars ===')
    for (pn, sidx) in MAPPING:
        pi = int(pn[1:]) - 1
        if pi < len(para_token_counts) and sidx < len(sub_chars):
            print(f'  {pn} ({para_token_counts[pi]} tok) <-> III.19.{sidx} ({sub_chars[sidx]} chars)')

    obs_rho, p_value = perm_spearman(para_token_counts, sub_chars)
    print(f'\n  Spearman ρ = {obs_rho:+.4f}')
    print(f'  Permutation p (one-sided, ρ >= obs) = {p_value:.4f}')

    # Pearson sanity
    n = min(len(para_token_counts), len(sub_chars))
    a = para_token_counts[:n]
    b = sub_chars[:n]
    ma = sum(a)/n; mb = sum(b)/n
    num = sum((a[i]-ma)*(b[i]-mb) for i in range(n))
    da = math.sqrt(sum((x-ma)**2 for x in a))
    db = math.sqrt(sum((x-mb)**2 for x in b))
    pearson = num/(da*db) if da*db > 0 else 0
    print(f'  Pearson r (sanity) = {pearson:+.4f}')

    # ---- Secondary: 4 verb-category densities ----
    print('\n=== Secondary: verb-category density correlations ===')
    # f75r-side proxies
    def qok_density(para_tokens):
        qok = sum(1 for t in para_tokens if t.word.startswith('qok'))
        return qok / max(1, len(para_tokens))
    def take_density(para_tokens):
        # pen-/pol-/pch- openers (from H6 expert hypothesis)
        n = sum(1 for t in para_tokens if t.word.startswith(('pch', 'pen', 'pol')))
        return n / max(1, len(para_tokens))
    def place_density(para_tokens):
        # dar/dal/daly (per C1925)
        n = sum(1 for t in para_tokens if t.word in ('dar', 'dal', 'daly') or t.word.startswith('dar') or t.word.startswith('dal'))
        return n / max(1, len(para_tokens))
    def observe_density(para_tokens):
        # aiin / ain substring (per C1234)
        n = sum(1 for t in para_tokens if 'aiin' in t.word or 'ain' in t.word)
        return n / max(1, len(para_tokens))

    para_qok = [qok_density(p) for p in paragraphs]
    para_take = [take_density(p) for p in paragraphs]
    para_place = [place_density(p) for p in paragraphs]
    para_obs = [observe_density(p) for p in paragraphs]

    # Catalan-side from Phase 660 corpus
    verb_corpus = json.loads((REPO_ROOT / 'phases' / 'PHASE_660_OPERATOR_VERB_INVENTORY' /
                              'results' / 'VERB_CORPUS.json').read_text(encoding='utf-8'))
    verbs_by_subrecipe = defaultdict(lambda: defaultdict(int))
    for r in verb_corpus['instances']:
        verbs_by_subrecipe[r['subrecipe_id']][r['category']] += 1

    def sub_density(cat):
        return [verbs_by_subrecipe[s['id']].get(cat, 0) / max(1, s['chars'] / 1000)
                for s in subrecipes]

    sub_dist = sub_density('DISTILLATION')
    sub_take = sub_density('MATERIAL_TAKE')
    sub_place = sub_density('MATERIAL_PLACE')
    sub_obs = sub_density('OBSERVATION')

    secondary_results = {}
    for label, vms_vals, cat_vals in [
        ('DISTILLATION (qok-density vs Catalan dist)', para_qok, sub_dist),
        ('MATERIAL_TAKE (pen/pol/pch vs Pren)',        para_take, sub_take),
        ('MATERIAL_PLACE (dar/dal vs met)',            para_place, sub_place),
        ('OBSERVATION (aiin/ain vs guarda/veure)',     para_obs, sub_obs),
    ]:
        rho, p = perm_spearman(vms_vals, cat_vals)
        secondary_results[label] = {'rho': rho, 'p': p, 'vms': vms_vals, 'cat': cat_vals}
        print(f'  {label}')
        print(f'    ρ = {rho:+.4f}, p = {p:.4f}')

    # Verdict per pre-reg
    n_secondary_strict = sum(
        1 for r in secondary_results.values()
        if r['rho'] >= 0.4 and r['p'] <= 0.0125
    )
    n_secondary_lax = sum(
        1 for r in secondary_results.values()
        if r['rho'] >= 0.4 and r['p'] <= 0.10
    )

    print(f'\n=== VERDICT ===')
    print(f'  Primary: ρ={obs_rho:+.4f}, p={p_value:.4f}')
    print(f'  Secondary: {n_secondary_strict}/4 at strict (ρ≥0.4, p≤0.0125), '
          f'{n_secondary_lax}/4 at lax (ρ≥0.4, p≤0.10)')

    if obs_rho < 0.2 or obs_rho < 0:
        verdict = 'FALSIFIED'
    elif obs_rho >= 0.6 and p_value <= 0.05 and n_secondary_strict >= 2:
        verdict = 'SUPPORTED'
    elif (obs_rho >= 0.4 and p_value <= 0.10) or n_secondary_lax >= 2:
        verdict = 'DIRECTIONAL'
    else:
        verdict = 'INCONCLUSIVE'

    print(f'  Final: {verdict}')

    # LOO sensitivity (NOT load-bearing for verdict; per pre-reg requires it for registration)
    print(f'\n=== LOO sensitivity check (drop each pair, recompute primary) ===')
    loo_results = []
    for drop in range(len(MAPPING)):
        a = [para_token_counts[i] for i in range(9) if i != drop]
        b = [sub_chars[i] for i in range(9) if i != drop]
        rho, p = perm_spearman(a, b, n_perm=2000)
        loo_results.append({'drop_p': f'P{drop+1}', 'drop_s': f'III.19.{drop}',
                            'rho': rho, 'p': p})
        print(f'  drop ({MAPPING[drop][0]}, III.19.{MAPPING[drop][1]}): ρ={rho:+.3f}, p={p:.4f}')

    out = {
        'phase': 665,
        'pre_registration_commit': '70ca0eb',
        'mapping': MAPPING,
        'paragraph_token_counts': para_token_counts,
        'subrecipe_char_counts': sub_chars,
        'primary': {
            'spearman_rho': obs_rho,
            'permutation_p': p_value,
            'pearson_r': pearson,
        },
        'secondary': secondary_results,
        'verdict': verdict,
        'loo': loo_results,
    }
    (out_dir / 'ALIGNMENT_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
