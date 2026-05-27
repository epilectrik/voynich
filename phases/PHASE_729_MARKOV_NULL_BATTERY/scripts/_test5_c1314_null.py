"""Test 5: Does 5-gram-generated text reproduce C1314 qo-k -> ok-e cycling?

C1314 baseline (real Voynich Currier B):
  qo-k -> ok-e: 103 obs vs 72.0 null (43% above chance, p=0)
  ok-e -> qo-k: 112 obs vs 72.1 null (55% above chance, p=0)
  Negative control da -> sa: at chance

Test: train 5-gram on Currier B with matched line structure, generate synthetic,
recompute bigram counts + within-line shuffle null on synthetic.

If synthetic shows 40%+ enrichment, C1314 is Markov-trivial (the bigram
preference is captured by local character statistics).

If synthetic shows ~0% enrichment, C1314 survives — the thermal cycling
is a real structural property beyond Markov.
"""
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
random.seed(42)

from scripts.voynich import Transcript, Morphology

morph = Morphology()
tx = Transcript()

# ----------- Token classification -----------
def classify_token(w):
    """Return ('qo_k', 'ok_e', 'da', 'sa', None)."""
    try:
        m = morph.extract(w)
    except Exception:
        return None
    if not m.middle:
        return None
    prefix = m.prefix or ''
    has_k = 'k' in m.middle
    has_e = 'e' in m.middle
    if prefix == 'qo' and has_k:
        return 'qo_k'
    if prefix == 'ok' and has_e:
        return 'ok_e'
    if prefix == 'da':
        return 'da'
    if prefix == 'sa':
        return 'sa'
    return None


def count_bigrams(lines):
    """Count qo_k -> ok_e and ok_e -> qo_k bigrams within each line."""
    fwd = 0
    rev = 0
    da_to_sa = 0
    total = 0
    for words in lines:
        classes = [classify_token(w) for w in words]
        for i in range(len(classes) - 1):
            total += 1
            if classes[i] == 'qo_k' and classes[i+1] == 'ok_e':
                fwd += 1
            if classes[i] == 'ok_e' and classes[i+1] == 'qo_k':
                rev += 1
            if classes[i] == 'da' and classes[i+1] == 'sa':
                da_to_sa += 1
    return fwd, rev, da_to_sa, total


def shuffle_null(lines, n_shuffles=200, seed=42):
    """Within-line shuffle null."""
    rng = random.Random(seed)
    nfwd, nrev, nctrl = [], [], []
    for trial in range(n_shuffles):
        fwd, rev, ctrl = 0, 0, 0
        for words in lines:
            shuffled = list(words)
            rng.shuffle(shuffled)
            classes = [classify_token(w) for w in shuffled]
            for i in range(len(classes) - 1):
                if classes[i] == 'qo_k' and classes[i+1] == 'ok_e':
                    fwd += 1
                if classes[i] == 'ok_e' and classes[i+1] == 'qo_k':
                    rev += 1
                if classes[i] == 'da' and classes[i+1] == 'sa':
                    ctrl += 1
        nfwd.append(fwd); nrev.append(rev); nctrl.append(ctrl)
    return nfwd, nrev, nctrl


# ----------- 1. Real Currier B baseline -----------
lines_dict = defaultdict(list)
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    lines_dict[(t.folio, t.line)].append(w)
real_lines = list(lines_dict.values())
print(f'Real Currier B: {len(real_lines)} lines')

print('\n--- Real Currier B baseline ---')
fwd_real, rev_real, ctrl_real, total_real = count_bigrams(real_lines)
print(f'  Observed: qo-k->ok-e = {fwd_real}, ok-e->qo-k = {rev_real}, da->sa (neg ctrl) = {ctrl_real}')
print(f'  Total within-line bigrams: {total_real}')
print('  Computing within-line shuffle null (200 perms)...')
nfwd, nrev, nctrl = shuffle_null(real_lines, n_shuffles=200)
print(f'  Null mean: qo-k->ok-e = {sum(nfwd)/len(nfwd):.1f}, ok-e->qo-k = {sum(nrev)/len(nrev):.1f}, da->sa = {sum(nctrl)/len(nctrl):.1f}')
fwd_excess = (fwd_real - sum(nfwd)/len(nfwd)) / (sum(nfwd)/len(nfwd)) * 100
rev_excess = (rev_real - sum(nrev)/len(nrev)) / (sum(nrev)/len(nrev)) * 100
ctrl_excess = (ctrl_real - sum(nctrl)/len(nctrl)) / (sum(nctrl)/len(nctrl)) * 100 if sum(nctrl) > 0 else 0
print(f'  Enrichment: qo-k->ok-e {fwd_excess:+.1f}%, ok-e->qo-k {rev_excess:+.1f}%, da->sa {ctrl_excess:+.1f}%')

# ----------- 2. Train 5-gram, generate synthetic with matched line structure -----------
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


print('\nTraining 5-gram on Currier B...')
ngram = train_ngram(real_lines, 5)
print('Generating synthetic Currier B with matched line lengths...')
synth_lines = []
for words in real_lines:
    synth_lines.append(sample_line(ngram, 5, len(words)))
print(f'Generated {len(synth_lines)} synthetic lines')

print('\n--- Synthetic 5-gram ---')
fwd_syn, rev_syn, ctrl_syn, total_syn = count_bigrams(synth_lines)
print(f'  Observed: qo-k->ok-e = {fwd_syn}, ok-e->qo-k = {rev_syn}, da->sa (neg ctrl) = {ctrl_syn}')
print(f'  Total within-line bigrams: {total_syn}')
print('  Computing within-line shuffle null on synthetic...')
snfwd, snrev, snctrl = shuffle_null(synth_lines, n_shuffles=200, seed=123)
snull_fwd_mean = sum(snfwd)/len(snfwd)
snull_rev_mean = sum(snrev)/len(snrev)
snull_ctrl_mean = sum(snctrl)/len(snctrl) if snctrl else 0
print(f'  Null mean: qo-k->ok-e = {snull_fwd_mean:.1f}, ok-e->qo-k = {snull_rev_mean:.1f}, da->sa = {snull_ctrl_mean:.1f}')
syn_fwd_excess = (fwd_syn - snull_fwd_mean) / snull_fwd_mean * 100 if snull_fwd_mean > 0 else 0
syn_rev_excess = (rev_syn - snull_rev_mean) / snull_rev_mean * 100 if snull_rev_mean > 0 else 0
syn_ctrl_excess = (ctrl_syn - snull_ctrl_mean) / snull_ctrl_mean * 100 if snull_ctrl_mean > 0 else 0
print(f'  Enrichment: qo-k->ok-e {syn_fwd_excess:+.1f}%, ok-e->qo-k {syn_rev_excess:+.1f}%, da->sa {syn_ctrl_excess:+.1f}%')

print('\n=== VERDICT ===')
print(f'Real qo-k->ok-e enrichment: {fwd_excess:+.1f}%')
print(f'Synth qo-k->ok-e enrichment: {syn_fwd_excess:+.1f}%')
print(f'Real ok-e->qo-k enrichment: {rev_excess:+.1f}%')
print(f'Synth ok-e->qo-k enrichment: {syn_rev_excess:+.1f}%')

if abs(syn_fwd_excess) < 10 and abs(syn_rev_excess) < 10:
    print('  --> 5-gram does NOT reproduce C1314 cycling. The thermal cycling SURVIVES Markov null.')
elif syn_fwd_excess > 30 and syn_rev_excess > 30:
    print('  --> 5-gram REPRODUCES C1314 cycling. The thermal cycling is a Markov artifact.')
else:
    print(f'  --> PARTIAL reproduction. Real {fwd_excess:.0f}%/{rev_excess:.0f}% vs synth {syn_fwd_excess:.0f}%/{syn_rev_excess:.0f}%')
