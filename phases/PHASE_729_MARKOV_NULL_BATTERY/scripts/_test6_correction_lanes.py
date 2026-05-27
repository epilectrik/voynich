"""Test 6: Multiple 'correction-after-heat' lanes against 5-gram null.

After a qo-k token (heat add), what follows above chance?
- ok-anything (vessel-temp correction) — C1314 generalized
- ok-e (vessel cool — C1314 narrow)
- ch-anything (active monitor)
- sh-anything (passive monitor)
- ot-anything (transfer)

For each candidate "correction lane," compute:
- Real Currier B enrichment vs within-line shuffle
- Synthetic 5-gram enrichment vs within-line shuffle on synthetic
- Differential = real residual after subtracting Markov-reproducible portion
"""
import random
import sys
from collections import defaultdict, Counter

sys.path.insert(0, 'C:/git/voynich')
random.seed(42)

from scripts.voynich import Transcript, Morphology

morph = Morphology()
tx = Transcript()


def get_prefix_middle(w):
    try:
        m = morph.extract(w)
        return (m.prefix or ''), (m.middle or '')
    except Exception:
        return '', ''


def is_qo_k(w):
    p, mid = get_prefix_middle(w)
    return p == 'qo' and 'k' in mid


def is_ok_e(w):
    p, mid = get_prefix_middle(w)
    return p == 'ok' and 'e' in mid


def is_ok(w):
    p, _ = get_prefix_middle(w)
    return p == 'ok'


def is_ch(w):
    p, _ = get_prefix_middle(w)
    return p == 'ch'


def is_sh(w):
    p, _ = get_prefix_middle(w)
    return p == 'sh'


def is_ot(w):
    p, _ = get_prefix_middle(w)
    return p == 'ot'


def is_qo(w):
    p, _ = get_prefix_middle(w)
    return p == 'qo'


CANDIDATE_LANES = [
    ('qo-k -> ok',    is_qo_k, is_ok,   'ok-anything (broad vessel correction)'),
    ('qo-k -> ok-e',  is_qo_k, is_ok_e, 'ok-e (narrow C1314)'),
    ('qo-k -> ch',    is_qo_k, is_ch,   'active monitor after heat'),
    ('qo-k -> sh',    is_qo_k, is_sh,   'passive monitor after heat'),
    ('qo-k -> ot',    is_qo_k, is_ot,   'transfer after heat'),
    ('qo -> ch',      is_qo,   is_ch,   'broad: any qo -> ch'),
    ('qo -> sh',      is_qo,   is_sh,   'broad: any qo -> sh'),
]


def count_bigrams(lines, predicate_a, predicate_b):
    n = 0
    for words in lines:
        for i in range(len(words) - 1):
            if predicate_a(words[i]) and predicate_b(words[i+1]):
                n += 1
    return n


def shuffle_null_bigrams(lines, predicate_a, predicate_b, n_shuffles=100, seed=42):
    rng = random.Random(seed)
    nulls = []
    for _ in range(n_shuffles):
        n = 0
        for words in lines:
            shuffled = list(words)
            rng.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                if predicate_a(shuffled[i]) and predicate_b(shuffled[i+1]):
                    n += 1
        nulls.append(n)
    return sum(nulls) / len(nulls)


# Load real Currier B
lines_dict = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    lines_dict[(t.folio, t.line)].append(w)
real_lines = list(lines_dict.values())


# Train 5-gram, generate synthetic
def train_ngram(line_lists, order):
    counts = defaultdict(Counter)
    for words in line_lists:
        s = ' '.join(words)
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            counts[ctx][padded[i]] += 1
    return counts


def sample_line(counts, order, target_n):
    out = []; ctx = '\x01' * (order - 1); buf = []; attempts = 0
    while len(out) < target_n and attempts < target_n * 30:
        attempts += 1
        cand = counts.get(ctx)
        if not cand:
            ctx = '\x01' * (order - 1); continue
        chars = list(cand.keys()); weights = list(cand.values())
        ch = random.choices(chars, weights=weights, k=1)[0]
        if ch == '\x02':
            if buf:
                out.append(''.join(buf)); buf = []
            break
        if ch == ' ':
            if buf:
                out.append(''.join(buf)); buf = []
            ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
            continue
        buf.append(ch); ctx = (ctx + ch)[-(order - 1):] if order > 1 else ''
    if buf and len(out) < target_n:
        out.append(''.join(buf))
    return out[:target_n]


print(f'Training 5-gram on {len(real_lines)} Currier B lines...')
ngram = train_ngram(real_lines, 5)
synth_lines = [sample_line(ngram, 5, len(w)) for w in real_lines]
print(f'Generated {len(synth_lines)} synthetic lines')

print(f'\n{"Lane":<25} {"Real obs":>9} {"Real null":>10} {"Real %":>8}   {"Syn obs":>9} {"Syn null":>10} {"Syn %":>8}   {"Residual":>10}')
print('-' * 130)

results = []
for name, pa, pb, descr in CANDIDATE_LANES:
    r_obs = count_bigrams(real_lines, pa, pb)
    r_null = shuffle_null_bigrams(real_lines, pa, pb, n_shuffles=100)
    r_pct = (r_obs - r_null) / r_null * 100 if r_null > 0 else 0
    s_obs = count_bigrams(synth_lines, pa, pb)
    s_null = shuffle_null_bigrams(synth_lines, pa, pb, n_shuffles=100, seed=123)
    s_pct = (s_obs - s_null) / s_null * 100 if s_null > 0 else 0
    residual = r_pct - s_pct
    print(f'{name:<25} {r_obs:>9} {r_null:>10.1f} {r_pct:>+7.1f}%   {s_obs:>9} {s_null:>10.1f} {s_pct:>+7.1f}%   {residual:>+9.1f}pp   {descr}')
    results.append((name, r_pct, s_pct, residual))

print('\n=== INTERPRETATION ===')
print('Real % - Syn % = "residual signal beyond Markov." Positive = real structure 5-gram can\'t produce.')
print('Magnitudes >10pp are meaningful; <5pp is in noise floor.\n')
results.sort(key=lambda x: -x[3])
for name, r, s, res in results:
    if abs(res) > 15:
        verdict = 'STRONG residual signal'
    elif abs(res) > 7:
        verdict = 'Moderate residual'
    elif abs(res) > 2:
        verdict = 'Weak residual'
    else:
        verdict = 'Markov-trivial'
    print(f'  {name:<22} real {r:+5.1f}%, syn {s:+5.1f}%, residual {res:+5.1f}pp -- {verdict}')
